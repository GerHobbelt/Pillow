from PIL import FontFile, Image

from .helper import PillowTestCase


class TestFontFile(PillowTestCase):
    def test_decompression_bomb(self):
        font = FontFile.FontFile()
        font.glyph[0] = (
            (0, 0),
            (0, 0, 0, 0),
            (0, 0, 10000, 10000),
            Image.new("L", (0, 0)),
        )
        self.assertRaises(Image.DecompressionBombError, font.compile)
