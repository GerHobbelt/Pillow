import struct
from io import BytesIO

from PIL import Image, ImageFont

from .helper import PillowTestCase


class TestImageFontPil(PillowTestCase):
    def test_width_overflow(self):
        for dx, expected in ((32767, "Width too large"), (-32767, "Width too small")):
            glyph = struct.pack(">10h", dx, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            fp = BytesIO(b"PILfont\n\nDATA\n" + glyph * 256)

            font = ImageFont.ImageFont()
            font._load_pilfont_data(fp, Image.new("L", (1, 1)))
            text = "A" * 100000
            self.assertRaisesRegex(OverflowError, expected, font.getsize, text)
            self.assertRaisesRegex(OverflowError, expected, font.getmask, text)
