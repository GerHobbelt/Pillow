# Pillow quick hack to support R16G16B16A16 mode

use it with pillow-avif-plugin to write it as HDR10PQ image https://github.com/manoreken2/pillow-avif-plugin

## Usage

```
from PIL import Image
im = Image.fromarray(imCV, mode="R16G16B16")
```



