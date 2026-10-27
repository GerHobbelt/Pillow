from io import BytesIO

from PIL import GdImageFile, Image, _binary

from .helper import PillowTestCase

TEST_GD_FILE = "Tests/images/hopper.gd"


class TestFileGd(PillowTestCase):
    def test_sanity(self):
        im = GdImageFile.open(TEST_GD_FILE)
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "GD")

    def test_bad_mode(self):
        self.assertRaises(ValueError, GdImageFile.open, TEST_GD_FILE, "bad mode")

    def test_decompression_bomb(self):
        header = _binary.o16be(65535) + _binary.o16be(50000) + _binary.o16be(50000)
        b = BytesIO(header + b"\0" * 1031)
        self.assertRaises(Image.DecompressionBombError, GdImageFile.open, b)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(IOError, GdImageFile.open, invalid_file)
