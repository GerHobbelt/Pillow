# Pillow quick hack to support R16G16B16A16 mode

## Usage

from PIL import Image

im = Image.fromarray(imCV, mode="R16G16B16")

