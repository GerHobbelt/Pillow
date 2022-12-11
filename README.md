# Pillow quick hack to support R16G16B16 mode

Use with pillow-avif-plugin to write HDR10PQ AVIF image file https://github.com/manoreken2/pillow-avif-plugin

## Usage

```
from PIL import Image
import cv2

imCV = cv2.imread("a.png", cv2.IMREAD_UNCHANGED)
imCV = cv2.cvtColor(imCV, cv2.COLOR_BGR2RGB)
im = Image.fromarray(imCV, mode="R16G16B16")
```



