#
# The Python Imaging Library.
# $Id$
#
# XBM File handling
#
# History:
# 1995-09-08 fl   Created
# 1996-11-01 fl   Added save support
# 1997-07-07 fl   Made header parser more tolerant
# 1997-07-22 fl   Fixed yet another parser bug
# 2001-02-17 fl   Use 're' instead of 'regex' (Python 2.1) (0.4)
# 2001-05-13 fl   Added hotspot handling (based on code from Bernhard Herzog)
# 2004-02-24 fl   Allow some whitespace before first #define
#
# Copyright (c) 1997-2004 by Secret Labs AB
# Copyright (c) 1996-1997 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import re

from . import Image, ImageFile

# __version__ is deprecated and will be removed in a future version. Use
# PIL.__version__ instead.
__version__ = "0.6"

# XBM header
xbm_head = re.compile(
    br"\s*#define[ \t]+.*_width[ \t]+(?P<width>[0-9]+)[\r\n]+"
    b"#define[ \t]+.*_height[ \t]+(?P<height>[0-9]+)[\r\n]+"
    b"(?P<hotspot>"
    b"#define[ \t]+[^_]*_x_hot[ \t]+(?P<xhot>[0-9]+)[\r\n]+"
    b"#define[ \t]+[^_]*_y_hot[ \t]+(?P<yhot>[0-9]+)[\r\n]+"
    b")?"
    b"[\\000-\\377]*_bits\\[\\]"
)


def _accept(prefix):
    return prefix.startswith((b"#define", b"\n#define", b"/*"))


##
# Image plugin for X11 bitmaps.


class XbmImageFile(ImageFile.ImageFile):

    format = "XBM"
    format_description = "X11 Bitmap"

    def _open(self):

        width = None
        height = None
        x_hot = None
        offset = None
        starting = True
        in_block_comment = False
        while True:
            line = self.fp.readline(75)
            if not line:
                break
            line = line.rstrip()
            if in_block_comment:
                if line.endswith(b"*/"):
                    in_block_comment = False
                continue
            if line.startswith(b"/*"):
                in_block_comment = not line.endswith(b"*/")
                continue
            if starting and not line:
                starting = False
                continue
            if not line.startswith(b"#define "):
                if line.endswith(b"_bits[] = {"):
                    offset = self.fp.tell()
                break
            value = int(line.split().pop())
            if b"width " in line:
                width = value
            elif b"height " in line:
                height = value
            elif b"_x_hot " in line:
                x_hot = value
            elif b"_y_hot " in line:
                if x_hot is not None:
                    self.info["hotspot"] = x_hot, value
        if width is None or height is None or offset is None:
            raise SyntaxError("not a XBM file")

        self.mode = "1"
        self._size = width, height

        self.tile = [("xbm", (0, 0) + self.size, offset, None)]


def _save(im, fp, filename):

    if im.mode != "1":
        raise IOError("cannot write mode %s as XBM" % im.mode)

    fp.write(("#define im_width %d\n" % im.size[0]).encode("ascii"))
    fp.write(("#define im_height %d\n" % im.size[1]).encode("ascii"))

    hotspot = im.encoderinfo.get("hotspot")
    if hotspot:
        fp.write(("#define im_x_hot %d\n" % hotspot[0]).encode("ascii"))
        fp.write(("#define im_y_hot %d\n" % hotspot[1]).encode("ascii"))

    fp.write(b"static char im_bits[] = {\n")

    ImageFile._save(im, fp, [("xbm", (0, 0) + im.size, 0, None)])

    fp.write(b"};\n")


Image.register_open(XbmImageFile.format, XbmImageFile, _accept)
Image.register_save(XbmImageFile.format, _save)

Image.register_extension(XbmImageFile.format, ".xbm")

Image.register_mime(XbmImageFile.format, "image/xbm")
