"""Animated GIF: a 3x3 vertical-edge kernel sliding over a 6x6 image, filling a 4x4 feature map."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
NAVY, INK, AMBER, MUTED, GRID, WHITE = (11, 31, 51), (16, 24, 40), (245, 163, 0), (102, 112, 133), (208, 213, 221), (255, 255, 255)
F = "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"
font = ImageFont.truetype(F % "Bold", 22)
small = ImageFont.truetype(F % "Regular", 22)
label = ImageFont.truetype(F % "Bold", 24)

img = np.array([[10, 10, 10, 200, 200, 200]] * 6)  # dark left, bright right: a vertical edge
img[0, :] = [10, 10, 10, 10, 200, 200]
img[5, :] = [10, 10, 200, 200, 200, 200]
k = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
out = np.zeros((4, 4), int)
for i in range(4):
    for j in range(4):
        out[i, j] = int((img[i:i + 3, j:j + 3] * k).sum())
vmax = np.abs(out).max()

W, H, C = 1100, 490, 64
X0, Y0 = 40, 90           # input grid
KX = 40 + 6 * C + 70      # kernel
OX = KX + 3 * C + 120     # output grid


def gray(v):
    g = int(v)
    return (g, g, g)


def frame(step):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    d.text((X0, 40), "Input pixels (6×6)", font=label, fill=INK)
    d.text((KX, 40), "Kernel (Sobel-x)", font=label, fill=INK)
    d.text((OX, 40), "Feature map (4×4)", font=label, fill=INK)
    for i in range(6):
        for j in range(6):
            x, y = X0 + j * C, Y0 + i * C
            v = img[i, j]
            d.rectangle([x, y, x + C, y + C], fill=gray(v), outline=GRID)
            d.text((x + C / 2, y + C / 2), str(v), font=small, anchor="mm", fill=WHITE if v < 128 else INK)
    for i in range(3):
        for j in range(3):
            x, y = KX + j * C, Y0 + 64 + i * C
            d.rectangle([x, y, x + C, y + C], fill=(255, 244, 214), outline=AMBER, width=2)
            d.text((x + C / 2, y + C / 2), str(k[i, j]), font=font, anchor="mm", fill=INK)
    d.text((KX + 1.5 * C, Y0 + 64 + 3 * C + 30), "multiply & sum", font=small, anchor="mm", fill=MUTED)
    for n in range(16):
        i, j = divmod(n, 4)
        x, y = OX + j * C, Y0 + 64 + i * C
        if n <= step:
            v = out[i, j]
            t = abs(v) / vmax
            fill = tuple(int(WHITE[c] + (AMBER[c] - WHITE[c]) * t) for c in range(3))
            d.rectangle([x, y, x + C, y + C], fill=fill, outline=GRID)
            d.text((x + C / 2, y + C / 2), str(v), font=ImageFont.truetype(F % "Bold", 17), anchor="mm", fill=INK)
        else:
            d.rectangle([x, y, x + C, y + C], fill=(248, 249, 251), outline=GRID)
    if 0 <= step < 16:
        i, j = divmod(step, 4)
        x, y = X0 + j * C, Y0 + i * C
        d.rectangle([x, y, x + 3 * C, y + 3 * C], outline=AMBER, width=6)
        ox, oy = OX + j * C, Y0 + 64 + i * C
        d.rectangle([ox, oy, ox + C, oy + C], outline=NAVY, width=5)
        d.line([x + 3 * C + 6, y + 1.5 * C, KX - 8, Y0 + 64 + 1.5 * C], fill=AMBER, width=3)
        d.line([KX + 3 * C + 8, Y0 + 64 + 1.5 * C, ox - 8, oy + C / 2], fill=NAVY, width=3)
    return im


frames = [frame(s) for s in range(16)] + [frame(16)]
durs = [550] * 16 + [2200]
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
frames[-1].save(OUT.replace(".gif", "_final.png"))
print("ok", out.tolist())
