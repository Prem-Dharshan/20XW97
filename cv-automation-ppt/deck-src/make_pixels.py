"""Frame with highlighted patch + zoomed grid of real pixel values (slide 5)."""
import sys
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")             # 1280x720 (2x upscaled 640x360)
NAVY, AMBER, INK = (11, 31, 51), (245, 163, 0), (16, 24, 40)
F = "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"
N, step = 8, 4                                   # 8x8 samples, every 4th px of the 1280 frame
px, py = int(sys.argv[3]), int(sys.argv[4])      # top-left of patch in frame coords
FW, FH = 1000, 562
canvas = Image.new("RGB", (FW + 60 + N * 64, FH), "white")
canvas.paste(im.resize((FW, FH)), (0, 0))
d = ImageDraw.Draw(canvas)
s = FW / im.width
bx0, by0, bx1, by1 = px * s, py * s, (px + N * step) * s, (py + N * step) * s
d.rectangle([bx0 - 2, by0 - 2, bx1 + 2, by1 + 2], outline=AMBER, width=5)
gx, gy, C = FW + 60, (FH - N * 64) // 2, 64
d.line([bx1 + 3, by0, gx, gy], fill=AMBER, width=3)
d.line([bx1 + 3, by1, gx, gy + N * C], fill=AMBER, width=3)
font = ImageFont.truetype(F % "Bold", 19)
for i in range(N):
    for j in range(N):
        r, g, b = im.getpixel((px + j * step, py + i * step))
        v = round(0.299 * r + 0.587 * g + 0.114 * b)
        x, y = gx + j * C, gy + i * C
        d.rectangle([x, y, x + C, y + C], fill=(r, g, b), outline=(255, 255, 255))
        d.text((x + C / 2, y + C / 2), str(v), font=font, anchor="mm", fill=INK if v > 120 else (255, 255, 255))
canvas.save(out)
print(canvas.size)
