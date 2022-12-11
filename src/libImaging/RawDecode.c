/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for raw (uncompressed) image data
 *
 * history:
 * 96-03-07 fl rewritten
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#include "Raw.h"

int
ImagingRawDecode(Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    enum { LINE = 1, SKIP };
    RAWSTATE *rawstate = state->context;

    UINT8 *ptr;

    printf("%s:%d ImagingRawDecode bytes=%d\n", __FILE__, __LINE__, (int)bytes);

    if (state->state == 0) {
        printf("%s:%d\n", __FILE__, __LINE__);
        /* Initialize context variables */

        /* get size of image data and padding */
        state->bytes = (state->xsize * state->bits + 7) / 8;
        if (rawstate->stride) {
            printf("%s:%d\n", __FILE__, __LINE__);
            rawstate->skip = rawstate->stride - state->bytes;
            if (rawstate->skip < 0) {
                state->errcode = IMAGING_CODEC_CONFIG;
                return -1;
            }
        } else {
            printf("%s:%d\n", __FILE__, __LINE__);
            rawstate->skip = 0;
        }

        /* check image orientation */
        if (state->ystep < 0) {
            printf("%s:%d\n", __FILE__, __LINE__);
            state->y = state->ysize - 1;
            state->ystep = -1;
        } else {
            printf("%s:%d\n", __FILE__, __LINE__);
            state->ystep = 1;
        }

        printf("%s:%d\n", __FILE__, __LINE__);
        state->state = LINE;
    }

    ptr = buf;

    for (;;) {
        printf("%s:%d\n", __FILE__, __LINE__);
        if (state->state == SKIP) {
            /* Skip padding between lines */

            if (bytes < rawstate->skip) {
                printf("%s:%d\n", __FILE__, __LINE__);
                return ptr - buf;
            }

            ptr += rawstate->skip;
            bytes -= rawstate->skip;

            state->state = LINE;
        }

        printf("%s:%d bytes=%d state->bytes=%d\n", __FILE__, __LINE__, (int)bytes, state->bytes);

        if (bytes < state->bytes) {
            printf("%s:%d\n", __FILE__, __LINE__);
            return ptr - buf;
        }

        printf("%s:%d im->pixelsize=%d, state->bytes=%d state->x=%d state->y=%d state->xoff=%d state->yoff=%d state->xsize=%d state->ysize=%d\n",
            __FILE__,
            __LINE__,
            im->pixelsize,
            state->bytes,
            state->x,
            state->y,
            state->xoff,
            state->yoff,
            state->xsize,
            state->ysize);

        /* Unpack data */
        state->shuffle(
            (UINT8 *)im->image[state->y + state->yoff] + state->xoff * im->pixelsize,
            ptr,
            state->xsize);

        ptr += state->bytes;
        bytes -= state->bytes;

        state->y += state->ystep;

        if (state->y < 0 || state->y >= state->ysize) {
            printf("%s:%d\n", __FILE__, __LINE__);
            /* End of file (errcode = 0) */
            return -1;
        }

        printf("%s:%d\n", __FILE__, __LINE__);
        state->state = SKIP;
    }
    printf("%s:%d\n", __FILE__, __LINE__);
}
