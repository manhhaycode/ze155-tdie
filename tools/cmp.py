# Ghép ảnh so sánh: [ảnh gốc | chồng (ảnh gốc + mô hình bán trong suốt + viền) | render]
# usage: python cmp.py ref.png render.png out.png [mode] [alpha]
#   mode: overlay (mặc định) | side (chỉ đặt cạnh) | edge (chỉ viền mô hình đè lên ảnh)
import sys
from PIL import Image, ImageChops, ImageFilter, ImageOps

ref_p, ren_p, out_p = sys.argv[1:4]
mode = sys.argv[4] if len(sys.argv) > 4 else 'overlay'
alpha = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
ref = Image.open(ref_p).convert('RGBA')
ren = Image.open(ren_p).convert('RGBA')
if ren.size != ref.size:
    ren = ren.resize(ref.size, Image.LANCZOS)
W, H = ref.size
white = Image.new('RGBA', ref.size, (255, 255, 255, 255))
ref_w = Image.alpha_composite(white, ref)
ren_w = Image.alpha_composite(white, ren)

a = ren.split()[3]
mask = a.point(lambda v: 255 if v > 128 else 0)
edge = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))

if mode in ('overlay', 'edge'):
    base = ref_w.copy()
    if mode == 'overlay':
        r2 = ren.copy()
        r2.putalpha(a.point(lambda v: int(v * alpha)))
        base = Image.alpha_composite(base, r2)
    col = Image.new('RGBA', ref.size, (0, 170, 255, 255))
    base.paste(col, (0, 0), edge)
    mid = base
    panels = [ref_w, mid, ren_w]
else:
    panels = [ref_w, ren_w]

gap = 8
out = Image.new('RGB', (W * len(panels) + gap * (len(panels) - 1), H), (40, 40, 40))
for i, p in enumerate(panels):
    out.paste(p.convert('RGB'), (i * (W + gap), 0))
out.save(out_p)
print(out_p, out.size)
