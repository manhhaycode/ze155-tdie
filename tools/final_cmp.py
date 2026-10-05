# Ảnh so sánh cuối: [ảnh gốc | mô hình (nền trắng) | chồng: ảnh gốc + đường viền mô hình]
# kèm dải tiêu đề. usage: python final_cmp.py ref.png render.png out.png title
import sys
from PIL import Image, ImageDraw, ImageFilter

ref_p, ren_p, out_p, title = sys.argv[1:5]
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
ov = ref_w.copy()
r2 = ren.copy()
r2.putalpha(a.point(lambda v: int(v * 0.45)))
ov = Image.alpha_composite(ov, r2)
ov.paste(Image.new('RGBA', ref.size, (0, 150, 255, 255)), (0, 0), edge)

bar = 34
gap = 8
out = Image.new('RGB', (W * 3 + gap * 2, H + bar), (34, 34, 34))
d = ImageDraw.Draw(out)
labels = ['ảnh gốc ' + title, 'mô hình Blender', 'chồng (viền xanh = mô hình)']
for i, p in enumerate([ref_w, ren_w, ov]):
    out.paste(p.convert('RGB'), (i * (W + gap), bar))
    d.text((i * (W + gap) + 10, 10), labels[i], fill=(235, 235, 235))
out.save(out_p)
print(out_p, out.size)
