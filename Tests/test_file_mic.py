from io import BytesIO

from PIL import Image, ImagePalette, features

from .helper import PillowTestCase, hopper, unittest

try:
    from PIL import MicImagePlugin
except ImportError:
    olefile_installed = False
else:
    olefile_installed = True

TEST_FILE = "Tests/images/hopper.mic"


@unittest.skipUnless(olefile_installed, "olefile package not installed")
@unittest.skipUnless(features.check("libtiff"), "libtiff not installed")
class TestFileMic(PillowTestCase):
    def test_sanity(self):
        im = Image.open(TEST_FILE)
        im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "MIC")

        # Adjust for the gamma of 2.2 encoded into the file
        lut = ImagePalette.make_gamma_lut(1 / 2.2)
        im = Image.merge("RGBA", [chan.point(lut) for chan in im.split()])

        im2 = hopper("RGBA")
        self.assert_image_similar(im, im2, 10)

    def test_n_frames(self):
        im = Image.open(TEST_FILE)

        self.assertEqual(im.n_frames, 1)

    def test_is_animated(self):
        im = Image.open(TEST_FILE)

        self.assertFalse(im.is_animated)

    def test_tell(self):
        im = Image.open(TEST_FILE)

        self.assertEqual(im.tell(), 0)

    def test_seek(self):
        im = Image.open(TEST_FILE)

        im.seek(0)
        self.assertEqual(im.tell(), 0)

        self.assertRaises(EOFError, im.seek, 99)
        self.assertEqual(im.tell(), 0)

    def test_seek_decompression_bomb(self):
        import olefile

        im = Image.open(TEST_FILE)
        im.images = [im.images[0], im.images[0]]

        fp = im.ole.openstream(im.images[0])
        tiff_data = fp.read()
        fp.close()
        tiff_data = tiff_data[:35132] + b"\xff\xff\xff\xff" + tiff_data[35136:]
        tiff_data = tiff_data[:35144] + b"\xff\xff\xff\xff" + tiff_data[35148:]
        with open(TEST_FILE, "rb") as fp:
            b = BytesIO(fp.read())
        im.ole = olefile.OleFileIO(b, write_mode=True)
        im.ole.write_stream(im.images[0], tiff_data)

        self.assertRaises(Image.DecompressionBombError, im.seek, 1)

    def test_invalid_file(self):
        # Test an invalid OLE file
        invalid_file = "Tests/images/flower.jpg"
        self.assertRaises(SyntaxError, MicImagePlugin.MicImageFile, invalid_file)

        # Test a valid OLE file, but not a MIC file
        ole_file = "Tests/images/test-ole-file.doc"
        self.assertRaises(SyntaxError, MicImagePlugin.MicImageFile, ole_file)
