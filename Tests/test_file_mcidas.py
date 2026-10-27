import struct

from PIL import Image, McIdasImagePlugin

from .helper import PillowTestCase


class TestFileMcIdas(PillowTestCase):
    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, McIdasImagePlugin.McIdasImageFile, invalid_file)

    def test_undersized_stride(self):
        # A crafted area descriptor declares a row stride far smaller than a full
        # row of pixels. Memory mapping must not lay out row pointers at that
        # stride, which would read past the mapped buffer; the image is rejected
        # instead of leaking memory or crashing.
        words = [0] * 65
        words[2] = 4  # magic: 00 00 00 00 00 00 00 04
        words[9] = 1  # ysize
        words[10] = 200000  # xsize -> a full row is 200000 bytes (mode "L")
        words[11] = 1  # mode "L"
        words[14] = 0  # zeroes the xsize term of the stride
        words[15] = 1  # stride = 1  (much smaller than a row)
        data = struct.pack("!64i", *words[1:65])

        path = self.tempfile("temp.area")
        with open(path, "wb") as f:
            f.write(data)

        im = Image.open(path)
        with self.assertRaises(ValueError) as e:
            im.load()
        self.assertIn("buffer is not large enough", str(e.exception))

    def test_valid_file(self):
        # Arrange
        # https://ghrc.nsstc.nasa.gov/hydro/details/cmx3g8
        # https://ghrc.nsstc.nasa.gov/pub/fieldCampaigns/camex3/cmx3g8/browse/
        test_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.ara"
        saved_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.png"

        # Act
        im = Image.open(test_file)
        im.load()

        # Assert
        self.assertEqual(im.format, "MCIDAS")
        self.assertEqual(im.mode, "I")
        self.assertEqual(im.size, (1800, 400))
        im2 = Image.open(saved_file)
        self.assert_image_equal(im, im2)
