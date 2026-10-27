import io

from PIL import BdfFontFile, FontFile, Image

from .helper import PillowTestCase

filename = "Tests/images/courB08.bdf"


class TestFontBdf(PillowTestCase):
    def test_sanity(self):

        with open(filename, "rb") as test_file:
            font = BdfFontFile.BdfFontFile(test_file)

        self.assertIsInstance(font, FontFile.FontFile)
        self.assertEqual(len([_f for _f in font.glyph if _f]), 190)

    def test_decompression_bomb(self):
        with open(filename, "rb") as fp:
            data = fp.read()
        b = io.BytesIO(data.replace(b"BBX 1 1", b"BBX 13378 13378"))
        self.assertRaises(Image.DecompressionBombError, BdfFontFile.BdfFontFile, b)

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, BdfFontFile.BdfFontFile, fp)
