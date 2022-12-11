# Pillow quick hack to support R16G16B16 mode

Use with pillow-avif-plugin to write HDR10PQ AVIF image file https://github.com/manoreken2/pillow-avif-plugin

## Usage

```
from PIL import Image
im = Image.fromarray(imCV, mode="R16G16B16")
```



