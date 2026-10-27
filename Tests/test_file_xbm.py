import signal
from io import BytesIO

from PIL import Image, XbmImagePlugin

from .helper import PillowTestCase, hopper, unittest

PIL151 = b"""
#define basic_width 32
#define basic_height 32
static char basic_bits[] = {
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00,
0x80, 0xff, 0xff, 0x01, 0x40, 0x00, 0x00, 0x02,
0x20, 0x00, 0x00, 0x04, 0x20, 0x00, 0x00, 0x04, 0x10, 0x00, 0x00, 0x08,
0x10, 0x00, 0x00, 0x08,
0x10, 0x00, 0x00, 0x08, 0x10, 0x00, 0x00, 0x08,
0x10, 0x00, 0x00, 0x08, 0x10, 0x00, 0x00, 0x08, 0x10, 0x00, 0x00, 0x08,
0x20, 0x00, 0x00, 0x04,
0x20, 0x00, 0x00, 0x04, 0x40, 0x00, 0x00, 0x02,
0x80, 0xff, 0xff, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00,
};
"""


class TestFileXbm(PillowTestCase):
    def test_pil151(self):
        from io import BytesIO

        im = Image.open(BytesIO(PIL151))

        im.load()
        self.assertEqual(im.mode, "1")
        self.assertEqual(im.size, (32, 32))

    def test_open(self):
        # Arrange
        # Created with `convert hopper.png hopper.xbm`
        filename = "Tests/images/hopper.xbm"

        # Act
        im = Image.open(filename)

        # Assert
        self.assertEqual(im.mode, "1")
        self.assertEqual(im.size, (128, 128))

    def test_leading_comment(self):
        for comment in (
            b"/* comment */\n",
            b"/*\nThis is an example file\n*/\n",
            b"/* " + b"A" * 200 + b" */\n",
            b"/* one */\n/* two */\n",
        ):
            im = Image.open(BytesIO(comment + PIL151))
            self.assertEqual(im.format, "XBM")
            self.assertEqual(im.size, (32, 32))
            self.assert_image_equal(im, Image.open(BytesIO(PIL151)))

    def test_comments_between_header_lines(self):
        b = BytesIO(
            b"""
#define basic_width 32
/*single line comment*/
#define basic_height 32
/*multi line
comment*/
"""
            + PIL151.split(b"static")[1]
        )
        im = Image.open(b)
        self.assert_image_equal(im, Image.open(BytesIO(PIL151)))

    def test_unterminated_comment(self):
        b = BytesIO(b"/* unterminated\n" + PIL151)
        self.assertRaises(IOError, Image.open, b)

    def test_hotspot(self):
        im = hopper("1")
        out = self.tempfile("temp.xbm")

        hotspot = (0, 7)
        im.save(out, hotspot=hotspot)

        reloaded = Image.open(out)
        self.assertEqual(reloaded.info["hotspot"], hotspot)

    def test_open_filename_with_underscore(self):
        # Arrange
        # Created with `convert hopper.png hopper_underscore.xbm`
        filename = "Tests/images/hopper_underscore.xbm"

        # Act
        im = Image.open(filename)

        # Assert
        self.assertEqual(im.mode, "1")
        self.assertEqual(im.size, (128, 128))

    @unittest.skipUnless(hasattr(signal, "SIGALRM"), "needs SIGALRM")
    def test_redos(self):
        redos = b""
        for prop in (b"width", b"height", b"x_hot", b"y_hot"):
            redos += b"#define" + b" " * 60 + b"_" + prop + b" 1\r"
        redos += b"\r" * 60 + b"_bits" + b"A" * 512

        def timeout(signum, frame):
            raise AssertionError("timed out")

        old_handler = signal.signal(signal.SIGALRM, timeout)
        signal.alarm(2)
        try:
            self.assertRaises(SyntaxError, XbmImagePlugin.XbmImageFile, BytesIO(redos))
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
