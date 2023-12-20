#!/usr/bin/env python3

from neosca import IMG_DIR
from PIL import Image, ImageDraw, ImageFont

w = 1024
h = 1024
image_size = (w, h)
background_color = "#606060"

font_size = 730
font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Bold.ttf", font_size)
text = "NS"
text_color = "#ffffff"
text_args = {"xy": (0, 0), "text": text, "font": font, "align": "center", "spacing": 4}

image = Image.new("RGB", image_size, background_color)
draw = ImageDraw.Draw(image)
left, top, right, bottom = draw.textbbox(**text_args)
text_w = right + left
text_h = bottom + top
text_args["xy"] = ((w - text_w) // 2, (h - text_h) // 2)
draw.text(**text_args, fill=text_color)
image.save("ns_icon.png")  # {{{
image.save(
    IMG_DIR / "ns_icon.ico",
    sizes=[
        (16, 16),
        (20, 20),
        (24, 24),
        (30, 30),
        (32, 32),
        (36, 36),
        (40, 40),
        (48, 48),
        (60, 60),
        (64, 64),
        (72, 72),
        (80, 80),
        (96, 96),
        (256, 256),
    ],
)
image.save(
    IMG_DIR / "ns_icon.icns", sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]
)  # }}}
