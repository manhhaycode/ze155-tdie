"""Annotated storyboard frames for the ZE 155 animation (one per shot) + contact sheet.

Run from the workspace root:
    uv run -q --with pillow python anim/storyboard/make_storyboard.py

Base images are existing renders, drawing sheets and brochure pages. All overlay
coordinates are fractions (0..1) of the cropped image region, so they survive resizing.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'anim', 'storyboard')
W, H = 1600, 900
TOP, BOT = 54, 70                     # title bar / caption heights
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
FONTB = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def f(sz, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, sz)

SHOTS = {s['id']: s for s in json.load(open(os.path.join(ROOT, 'anim', 'shots.json')))['shots']}
ROWS = json.load(open(os.path.join(ROOT, 'anim', 'interior_parts.json')))['screw_elements']['rows']

C_CAM = (255, 196, 0)       # camera path
C_FLOW = (232, 92, 30)      # material / melt flow
C_SEC = (220, 20, 60)       # section plane
C_BOX = (255, 255, 255)
C_TXT = (25, 25, 25)

# ------------------------------------------------------------------ helpers
class Frame:
    def __init__(self, src, crop=None, region=(0, TOP, W, H - BOT), bg=(38, 41, 46)):
        self.im = Image.new('RGB', (W, H), bg)
        base = Image.open(os.path.join(ROOT, src)).convert('RGB')
        if crop: base = base.crop(crop)
        rx0, ry0, rx1, ry1 = region
        rw, rh = rx1 - rx0, ry1 - ry0
        s = min(rw / base.width, rh / base.height)
        nw, nh = int(base.width * s), int(base.height * s)
        base = base.resize((nw, nh), Image.LANCZOS)
        self.ox, self.oy = rx0 + (rw - nw) // 2, ry0 + (rh - nh) // 2
        self.iw, self.ih = nw, nh
        self.im.paste(base, (self.ox, self.oy))
        self.d = ImageDraw.Draw(self.im, 'RGBA')

    def p(self, fx, fy):  # fraction of image region -> canvas px
        return (self.ox + fx * self.iw, self.oy + fy * self.ih)

    def poly(self, pts, col, width=6, dash=None, arrow=True, canvas=False):
        P = [pt if canvas else self.p(*pt) for pt in pts]
        if dash:
            segs = []
            for a, b in zip(P, P[1:]):
                L = math.dist(a, b); n = max(1, int(L // dash))
                for i in range(0, n, 2):
                    t0, t1 = i / n, min(1, (i + 1) / n)
                    segs.append(((a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)))
            for s in segs: self.d.line(s, fill=col, width=width)
        else:
            self.d.line(P, fill=col, width=width, joint='curve')
        if arrow: self.head(P[-2], P[-1], col, width)

    def head(self, a, b, col, width):
        ang = math.atan2(b[1] - a[1], b[0] - a[0]); L = 10 + width * 2.6
        p1 = (b[0] - L * math.cos(ang - 0.45), b[1] - L * math.sin(ang - 0.45))
        p2 = (b[0] - L * math.cos(ang + 0.45), b[1] - L * math.sin(ang + 0.45))
        self.d.polygon([b, p1, p2], fill=col)

    def arc_arrow(self, c, r, a0, a1, col, width=5):  # degrees, image fraction centre, r in px
        cx, cy = self.p(*c)
        self.d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=col, width=width)
        t = math.radians(a1); t2 = math.radians(a1 - 8 * (1 if a1 > a0 else -1))
        self.head((cx + r * math.cos(t2), cy + r * math.sin(t2)), (cx + r * math.cos(t), cy + r * math.sin(t)), col, width)

    def text_box(self, xy, text, size=21, col=C_TXT, bg=(255, 255, 255, 230), bold=False, pad=7, canvas=False, maxw=430):
        x, y = xy if canvas else self.p(*xy)
        fnt = f(size, bold)
        lines = []
        for para in text.split('\n'):
            cur = ''
            for w_ in para.split(' '):
                t = (cur + ' ' + w_).strip()
                if self.d.textlength(t, font=fnt) > maxw and cur:
                    lines.append(cur); cur = w_
                else:
                    cur = t
            lines.append(cur)
        tw = max(self.d.textlength(l, font=fnt) for l in lines); th = len(lines) * (size + 5)
        x = min(max(4, x), W - tw - 2 * pad - 4)
        self.d.rounded_rectangle([x, y, x + tw + 2 * pad, y + th + 2 * pad - 4], 6, fill=bg, outline=(0, 0, 0, 120))
        for i, l in enumerate(lines):
            self.d.text((x + pad, y + pad + i * (size + 5)), l, font=fnt, fill=col)
        return (x, y, x + tw + 2 * pad, y + th + 2 * pad - 4)

    def callout(self, anchor, box, text, size=20):
        bx = self.text_box(box, text, size)
        ax, ay = self.p(*anchor)
        cx = min(max(ax, bx[0]), bx[2]); cy = bx[3] if ay > bx[3] else (bx[1] if ay < bx[1] else (bx[1] + bx[3]) / 2)
        if bx[0] <= ax <= bx[2] and bx[1] <= ay <= bx[3]:
            return
        self.d.line([(cx, cy), (ax, ay)], fill=(255, 255, 255, 235), width=6)
        self.d.line([(cx, cy), (ax, ay)], fill=(30, 30, 30, 255), width=2)
        self.d.ellipse([ax - 6, ay - 6, ax + 6, ay + 6], fill=(255, 255, 255), outline=(0, 0, 0))

    def cam_icon(self, fxy, n):
        x, y = self.p(*fxy)
        self.d.rounded_rectangle([x - 16, y - 11, x + 12, y + 11], 3, fill=C_CAM, outline=(0, 0, 0))
        self.d.polygon([(x + 12, y - 6), (x + 24, y - 12), (x + 24, y + 12), (x + 12, y + 6)], fill=C_CAM, outline=(0, 0, 0))
        self.d.text((x - 10, y - 10), str(n), font=f(16, True), fill=(0, 0, 0))

    def chrome(self, sid, src_note):
        s = SHOTS[sid]
        self.d.rectangle([0, 0, W, TOP], fill=(20, 22, 26, 255))
        self.d.text((16, 11), f"{sid}", font=f(28, True), fill=C_CAM)
        self.d.text((86, 13), s['title_vi'], font=f(25, True), fill=(255, 255, 255))
        dur = f"{s['duration_s']:.0f} s · khung {s['frames'][0]}–{s['frames'][1]}"
        tw = self.d.textlength(dur, font=f(20))
        self.d.text((W - tw - 16, 16), dur, font=f(20), fill=(220, 220, 220))
        self.d.rectangle([0, H - BOT, W, H], fill=(20, 22, 26, 255))
        self.d.text((16, H - BOT + 8), "Dạy gì: " + s['purpose_vi'], font=f(18), fill=(235, 235, 235))
        badge = s.get('speed_badge_vi', '')
        self.d.text((16, H - BOT + 38), f"Tốc độ: {badge}   ·   Ảnh nền: {src_note}   ·   * = giả định", font=f(16), fill=(170, 175, 180))
        # legend
        lx = W - 560; ly = H - BOT + 40
        for col, name, dash in ((C_CAM, 'đường camera', None), (C_FLOW, 'dòng vật liệu', None), (C_SEC, 'mặt cắt', 14)):
            self.poly([(lx, ly + 8), (lx + 46, ly + 8)], col, 5, dash=dash, arrow=dash is None, canvas=True)
            self.d.text((lx + 54, ly - 2), name, font=f(16), fill=(220, 220, 220)); lx += 185

    def save(self, sid):
        p = os.path.join(OUT, f'{sid}.png'); self.im.save(p); return p


def panel(fr, x0, y0, x1, y1, title=None):
    fr.d.rounded_rectangle([x0, y0, x1, y1], 10, fill=(250, 250, 250, 238), outline=(0, 0, 0, 150))
    if title: fr.d.text((x0 + 14, y0 + 10), title, font=f(21, True), fill=C_TXT)


def gear(d, cx, cy, r, teeth, phase, col):
    pts = []
    for i in range(teeth * 4):
        a = phase + 2 * math.pi * i / (teeth * 4)
        rr = r + (9 if (i % 4) in (1, 2) else -9)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col, outline=(40, 40, 40))
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(60, 60, 60))

# ------------------------------------------------------------------ shots
made = []

# S01 overview -------------------------------------------------------
fr = Frame('out/renders/ze155-hero.png')
axis = [(.675, .11), (.672, .24), (.667, .33), (.648, .43), (.632, .50), (.615, .535), (.5, .548), (.42, .552), (.37, .556), (.32, .57), (.272, .615), (.24, .595), (.196, .52), (.15, .415), (.104, .52), (.08, .69)]
fr.poly(axis, C_FLOW, 7)
fr.poly([(.95, .16), (.75, .07), (.5, .06), (.25, .09), (.1, .17)], C_CAM, 6)
for i, pt in enumerate([(.95, .16), (.5, .06), (.1, .17)], 1): fr.cam_icon(pt, i)
fr.callout((.672, .26), (.75, .2), 'Cân & cấp liệu: hạt PET không sấy')
fr.callout((.77, .45), (.80, .55), 'Động cơ 1 500 kW* → hộp số chia công suất')
fr.callout((.5, .55), (.47, .72), 'Máy đùn ZE 155 A UT · 34D · 2 vùng chân không')
fr.callout((.33, .57), (.22, .80), 'Lọc lưới → bơm bánh răng → khuôn chữ T 2 400 mm')
fr.callout((.15, .42), (.02, .25), 'Cụm cán 3 trục Ø800 → tấm PET')
fr.text_box((.01, .02), 'Trục quy trình (vạch cam): hạt → máy đùn → nhựa chảy → khuôn → tấm', 19)
fr.chrome('S01', 'out/renders/ze155-hero.png'); made.append(fr.save('S01'))

# S02 drive ------------------------------------------------------------
fr = Frame('out/renders/ze155-drive.png')
fr.poly([(.30, .37), (.435, .37), (.435, .62), (.30, .62), (.30, .37)], (120, 200, 255), 4, dash=12, arrow=False)
fr.poly([(.62, .50), (.475, .50), (.37, .50), (.26, .46), (.205, .41)], C_FLOW, 9)
fr.poly([(.78, .22), (.55, .17), (.30, .22)], C_CAM, 6)
fr.cam_icon((.78, .22), 1); fr.cam_icon((.30, .22), 2)
fr.callout((.62, .46), (.66, .10), 'Động cơ 1 500 kW* · 1 119 v/ph khi vít 300 v/ph*')
fr.callout((.475, .50), (.42, .80), 'Khớp đàn hồi + khớp an toàn giới hạn mô-men (quay, chậm 20×)')
fr.callout((.37, .44), (.02, .14), 'Vỏ hộp số trong suốt (ghost) + sơ đồ bánh răng chia công suất i ≈ 3,73*')
fr.callout((.215, .42), (.02, .62), '2 trục then hoa quay cùng chiều → 2 vít')
fr.text_box((.66, .62), 'Mô-men ≈ 12,7 kNm* mỗi trục (36 % của 35 kNm)', 19)
fr.chrome('S02', 'out/renders/ze155-drive.png'); made.append(fr.save('S02'))

# S03 feeding ----------------------------------------------------------
fr = Frame('out/renders/ze155-feeding.png')
fr.poly([(.51, .12), (.515, .27), (.53, .43)], C_FLOW, 8, arrow=False)
fr.poly([(.53, .43), (.47, .60), (.39, .68), (.345, .71)], C_FLOW, 8, dash=16)
fr.poly([(.42, .58), (.33, .77)], C_SEC, 5, dash=14, arrow=False)
fr.text_box((.20, .87), 'Mặt cắt Y = 0 qua ống rơi, phễu, họng nạp (giữ nửa −Y)', 18, col=(140, 0, 30))
fr.poly([(.86, .10), (.76, .20)], C_CAM, 6); fr.cam_icon((.86, .10), 'a')
fr.poly([(.97, .62), (.62, .80)], C_CAM, 6); fr.cam_icon((.97, .62), 'b')
fr.text_box((.66, .86), 'Cắt cảnh: camera a trên sàn → camera b dưới sàn (không xuyên mép sàn)', 16, maxw=420)
fr.callout((.51, .12), (.58, .03), 'Máy hút liệu chân không')
fr.callout((.53, .43), (.60, .33), 'Cân chính (LIW) ≈ 3 300 kg/h*')
fr.callout((.29, .34), (.02, .17), 'Phụ gia ≈ 40 kg/h* → nhánh Y của ống rơi')
fr.callout((.44, .63), (.06, .45), 'Hạt rơi qua ống mềm cách cân, ống rơi (đi dưới sàn)')
fr.callout((.345, .71), (.02, .70), 'Họng nạp B1 (áo nước): cấp đói, vít chỉ đầy một phần')
fr.callout((.29, .82), (.40, .80), 'Biên tấm nghiền ≈ 160 kg/h* → side feeder (B2, +Y)')
fr.chrome('S03', 'out/renders/ze155-feeding.png'); made.append(fr.save('S03'))

# S04 barrel B1-B3 -----------------------------------------------------
fr = Frame('out/look/screws-cutaway-r1.png')
ins = Image.open(os.path.join(ROOT, 'research/pages/p13.png')).convert('RGB').crop((94, 460, 1170, 822))
ins = ins.resize((520, int(520 * ins.height / ins.width)))
fr.im.paste(ins, (int(fr.ox + 8), int(fr.oy + 8)))
fr.d.rectangle([fr.ox + 8, fr.oy + 8, fr.ox + 8 + ins.width, fr.oy + 8 + ins.height], outline=(255, 255, 255), width=3)
fr.text_box((fr.ox + 12, fr.oy + 14 + ins.height), 'Catalogue KM tr. 13: phần tử vận chuyển, khối nhào, trộn', 16, canvas=True)
fr.poly([(.02, .70), (.30, .60), (.50, .53), (.75, .44)], C_SEC, 4, dash=14, arrow=False)
fr.poly([(.74, .37), (.50, .46), (.30, .53), (.08, .62)], C_FLOW, 8)
fr.poly([(.92, .22), (.70, .20), (.45, .27)], C_CAM, 6)
fr.cam_icon((.92, .22), 1); fr.cam_icon((.45, .27), 4)
fr.callout((.82, .45), (.70, .58), 'B1: họng nạp, áo nước ≈ 50 °C*')
fr.callout((.62, .48), (.52, .68), 'Vận chuyển bước 1,5D: hạt rắn, điền ≈ 30 %')
fr.callout((.42, .54), (.20, .76), 'Khối nhào KB 45°/5: hạt → nhựa chảy (màu trắng → hổ phách)')
fr.callout((.30, .59), (.56, .82), 'KB 90° + ren trái: nút nhựa đầy 100 % trước chân không 1')
fr.text_box((.40, .03), 'Mặt cắt Z = 1 200: nửa trên xi lanh và vỏ che tách ra, nhấc lên (peel). Sàn thao tác ẩn trong shot này. Vít hiện có (ảnh) sẽ dựng lại theo bảng phần tử.', 17, maxw=560)
fr.d.rectangle([fr.p(.18, .50)[0], fr.p(.18, .50)[1] - 34, fr.p(.27, .50)[0], fr.p(.18, .50)[1] + 4], fill=(123, 79, 201, 90), outline=(123, 79, 201), width=3)
fr.text_box((.14, .36), 'Vòm 1 vẽ mờ + dải tím = cửa sổ lỗ chân không 1, ngay sau nút nhựa', 16, maxw=330)
fr.chrome('S04', 'out/look/screws-cutaway-r1.png + catalogue p13'); made.append(fr.save('S04'))

# S05 cross-section ----------------------------------------------------
fr = Frame('drawings/sheet-02-barrel.png', crop=(4980, 230, 6120, 1400), region=(0, TOP, 900, H - BOT), bg=(250, 250, 250))
for c in ((.375, .60), (.54, .60)):
    fr.arc_arrow(c, 105, 200, 330, C_FLOW, 6)
fr.callout((.457, .60), (.03, .02), 'Đỉnh ren vét sườn ren trục kia: tự làm sạch')
fr.callout((.69, .48), (.62, .02), '8 lỗ nước Ø18')
fr.callout((.13, .56), (.01, .86), 'Băng nhiệt gốm Ø580')
panel(fr, 920, TOP + 20, W - 20, H - BOT - 20, 'Mặt cắt ngang X = 2 450 (B3)')
y = TOP + 64
for t in ['Camera đứng phía +X nhìn về −X, đẩy vào chậm.', 'Hai biên dạng 2 đầu ren (Erdmenger) quay CÙNG chiều, chậm 20×.', 'Lỗ hình số 8: 2 × Ø169, a = 142, rộng 311.', 'Vít Ø167,5 / lõi 116,5 (mô hình) · khe đỉnh ≈ 0,7 mm*.', 'Phần vít sau mặt cắt bị ẩn; phần tử 12 cắt sẵn tại X 2 450, nắp = tấm biên dạng 2 mm quay theo trục.', 'Nắp thép xi lanh tô màu gạch, gạch chéo như bản vẽ.', 'Nhựa điền thấp (≈ 30 %) màu hổ phách ở đáy rãnh.', 'Ảnh nền: tờ 02, mặt cắt A-A (bản vẽ cắt ở X 2 984 qua B4).']:
    fr.text_box((936, y), '• ' + t, 19, canvas=True, bg=(0, 0, 0, 0), maxw=610); y += 74
fr.chrome('S05', 'drawings/sheet-02, mặt cắt A-A'); made.append(fr.save('S05'))

# S06 mixing + LH seal: drawing strip + fill/pressure graph ------------
fr = Frame('drawings/sheet-02-barrel.png', crop=(540, 1700, 4400, 2380), region=(0, TOP + 6, W, TOP + 300), bg=(250, 250, 250))
def gx(X):  # drawing strip: X 5746 at left, 0 at right
    return fr.ox + fr.iw * (0.0034 + 0.9926 * (5746 - X) / 5746)
gy0, gy1 = TOP + 330, H - BOT - 60
fr.d.rectangle([0, gy0 - 20, W, H - BOT], fill=(250, 250, 250))
pts = []
for r in ROWS:
    for X in (r['x_start_mm'], r['x_end_mm']):
        pts.append((gx(X), gy1 - (gy1 - gy0 - 30) * r['fill_degree_schematic']))
fr.d.line([(gx(5746), gy1), (gx(0), gy1)], fill=(80, 80, 80), width=2)
fr.d.polygon([(gx(5746), gy1)] + pts[::-1] + [(gx(0), gy1)], fill=(232, 144, 30, 150))
fr.d.line(pts, fill=(180, 80, 10), width=3)
prs = [(5746, 100), (5155, 40), (4479, 0), (3718, 0), (3634, 12), (3338, 6), (2831, 0), (1986, 0), (1859, 8), (1521, 0), (0, 0)]
fr.d.line([(gx(X), gy1 - (gy1 - gy0 - 30) * p / 110) for X, p in prs], fill=(30, 90, 200), width=4)
fr.text_box((16, gy0 + 20), 'Độ điền (cam, sơ đồ) · áp suất (xanh) tới P1 ≈ 100 bar', 17, canvas=True, maxw=300)
for x0, x1, col, t in ((2831, 3338, (46, 158, 79, 70), 'KB trộn B4'), (3634, 3718, (220, 20, 60, 90), 'LH'), (3860, 4380, (123, 79, 201, 60), 'lỗ chân không 2'), (1990, 2310, (123, 79, 201, 60), 'lỗ chân không 1')):
    fr.d.rectangle([gx(x1), TOP + 6, gx(x0), gy1], fill=col)
    fr.d.text((gx(x1) + 4, gy1 + 6), t, font=f(16, True), fill=(40, 40, 40))
for X, t in ((5746, 'X 5 746 (đầu xi lanh)'), (0, 'X 0')):
    fr.d.text((gx(X) - (0 if X else 50), gy1 + 30), t, font=f(15), fill=(90, 90, 90))
fr.poly([(gx(600), gy0 - 6), (gx(5200), gy0 - 6)], C_FLOW, 5, canvas=True)
fr.d.text((gx(2300), gy0 - 30), '← dòng chảy (tờ 02: đầu khuôn bên trái, X giảm sang phải)', font=f(16), fill=C_FLOW)
fr.text_box((gx(3300) - 60, TOP + 250), 'Ren trái cuối B4 đẩy ngược → nút nhựa 100 %, vùng chân không sâu kín khí', 18, canvas=True, maxw=380)
fr.text_box((gx(3100) - 420, gy0 + 40), 'Khối nhào KB 45° × 2 + KB 90°: trộn, đồng nhất nhiệt', 18, canvas=True, maxw=330)
fr.chrome('S06', 'drawings/sheet-02 cấu hình vít + đồ thị từ interior_parts.json'); made.append(fr.save('S06'))

# S07 vent 2 -----------------------------------------------------------
fr = Frame('drawings/sheet-02-barrel.png', crop=(1100, 300, 2300, 1600), region=(0, TOP, 960, H - BOT), bg=(250, 250, 250))
fr.poly([(.455, .02), (.455, .98)], C_SEC, 5, dash=14, arrow=False)
fr.text_box((.47, .90), 'SEC_X4120', 18, col=(140, 0, 30))
for x in (.39, .45, .51):
    fr.poly([(x, .46), (x + .01, .30), (x - .005, .17)], (123, 79, 201), 5)
fr.poly([(.455, .12), (.455, .0)], (123, 79, 201), 6)
fr.poly([(.06, .36), (.30, .36)], C_CAM, 6); fr.cam_icon((.06, .36), 1)
fr.text_box((.02, .40), 'camera ở +X nhìn về −X', 17)
panel(fr, 980, TOP + 20, W - 20, H - BOT - 20, 'Vòm chân không 2 (B5), cắt ngang')
y = TOP + 64
for t in ['Mặt cắt qua tâm vòm X = 4 120: thấy lỗ số 8, hai vít, lỗ thoát khí 520 × 280, khoang vòm, ống DN150.', 'Bọt hơi nước + acetaldehyde nổi lên, vào vòm, lên van DN150 → bình tách ngưng → Roots + bơm khô.', '5–20 mbar* (vùng 1 ở B3 ≈ 50 mbar*, bọt dày hơn).', 'Ẩm 2 000–4 000 ppm* → < 50 ppm*; IV 0,80 → ≥ 0,77 dl/g*.', 'Vít sau mặt cắt bị ẩn; phần tử 22 cắt sẵn tại X 4 120.', 'Không khử ẩm: thủy phân ở ≈ 280 °C, IV tụt mạnh → vì vậy không cần máy sấy.']:
    fr.text_box((996, y), '• ' + t, 19, canvas=True, bg=(0, 0, 0, 0), maxw=560); y += 96
fr.chrome('S07', 'drawings/sheet-02, hình chiếu đứng vùng B5'); made.append(fr.save('S07'))

# S08 B6 + head + start-up valve ---------------------------------------
fr = Frame('out/renders/ze155-melt-line.png', crop=(1250, 420, 2400, 1067))
fr.poly([(.98, .47), (.05, .45)], C_SEC, 4, dash=14, arrow=False)
fr.poly([(.95, .52), (.60, .50), (.34, .47), (.16, .45)], C_FLOW, 8)
fr.poly([(.228, .52), (.215, .70), (.19, .86)], C_FLOW, 6, dash=14)
fr.poly([(.90, .12), (.55, .10), (.25, .16)], C_CAM, 6)
fr.cam_icon((.90, .12), 1); fr.cam_icon((.25, .16), 3)
fr.callout((.75, .55), (.62, .70), 'B6: bước 1D → 0,75D, đầy 100 % → P1 ≈ 100 bar*')
fr.callout((.333, .46), (.36, .20), 'Đầu xi lanh: số 8 → tròn Ø120 · P1/T1 · đĩa nổ')
fr.callout((.228, .39), (.02, .03), 'Van khởi động: chốt trượt XẢ → CHẠY')
fr.callout((.19, .86), (.30, .84), 'Khởi động: nhựa xả xuống máng → xe hứng')
fr.chrome('S08', 'out/renders/ze155-melt-line.png (cắt vùng)'); made.append(fr.save('S08'))

# S09 screen changer ---------------------------------------------------
fr = Frame('out/renders/ze155-melt-line.png', crop=(840, 380, 1800, 920))
fr.poly([(.49 - .17, .37), (.49 + .17, .37)], C_SEC, 1, arrow=False)
cx, cy = fr.p(.49, .40); r = 150
fr.d.ellipse([cx - r * .8, cy - r, cx + r * .8, cy + r], outline=(255, 255, 255), width=4)
fr.poly([(.95, .55), (.62, .60), (.40, .62)], C_FLOW, 7)
fr.callout((.49, .40), (.02, .05), 'Vỏ bộ lọc trong suốt (ghost); đĩa lưới quay bên trong')
panel(fr, 1080, TOP + 20, W - 20, TOP + 470, 'Sơ đồ đĩa lưới (nhìn theo +X)')
dcx, dcy, R = 1335, TOP + 270, 160
fr.d.ellipse([dcx - R - 30, dcy - R - 30, dcx + R + 30, dcy + R + 30], fill=(200, 205, 210), outline=(60, 60, 60), width=2)
for i in range(12):
    a = math.radians(-150 + 30 * i)   # angle from +Y toward +Z (image: +Y right, +Z up)
    x, y_ = dcx + R * math.cos(a), dcy - R * math.sin(a)
    act = -150 <= (-150 + 30 * i) <= -30
    bf = (-150 + 30 * i) == 0
    fr.d.ellipse([x - 26, y_ - 26, x + 26, y_ + 26], fill=(232, 144, 30) if act else ((90, 60, 40) if bf else (235, 235, 235)), outline=(40, 40, 40), width=2)
fr.arc_arrow((0, 0), 1, 0, 1, (0, 0, 0, 0), 1)
fr.d.arc([dcx - R - 50, dcy - R - 50, dcx + R + 50, dcy + R + 50], 200, 250, fill=C_FLOW, width=5)
fr.head((dcx + (R + 50) * math.cos(math.radians(242)), dcy + (R + 50) * math.sin(math.radians(242))), (dcx + (R + 50) * math.cos(math.radians(250)), dcy + (R + 50) * math.sin(math.radians(250))), C_FLOW, 5)
fr.d.text((1100, TOP + 60), 'cam = 5 lưới trong dòng nhựa · nâu = xả ngược', font=f(17), fill=C_TXT)
fr.d.text((1100, TOP + 440), 'bước +30° mỗi 3 s (tua nhanh)', font=f(17), fill=C_TXT)
fr.text_box((1080, TOP + 490), 'Lưới 60 µm* · 970 cm² · P2 ≈ 95 bar* → Δp ≈ 45 bar* → P3 = 50 bar*. Δp tăng → tăng nhịp quay. Trục đĩa song song dòng chảy (anim sửa theo nguyên lý).', 18, canvas=True, maxw=470)
fr.chrome('S09', 'out/renders/ze155-melt-line.png (cắt vùng) + sơ đồ vẽ tay'); made.append(fr.save('S09'))

# S10 gear pump --------------------------------------------------------
fr = Frame('out/renders/ze155-melt-line.png', crop=(840, 520, 1320, 790), region=(0, TOP, 960, H - BOT))
fr.poly([(.02, .50), (.98, .50)], C_SEC, 4, dash=12, arrow=False)
fr.text_box((.02, .03), 'Mặt cắt Y = 0 qua giữa bề rộng bánh răng (giữ nửa −Y)', 18, col=(140, 0, 30))
panel(fr, 980, TOP + 20, W - 20, H - BOT - 20, 'Sơ đồ mặt cắt (nhìn từ +Y)')
gcx, gtop, gbot = 1290, TOP + 250, TOP + 390
fr.d.rounded_rectangle([1130, TOP + 150, 1450, TOP + 490], 20, fill=(205, 210, 215), outline=(60, 60, 60), width=2)
fr.d.rectangle([1000, TOP + 300, 1130, TOP + 340], fill=(232, 144, 30)); fr.d.rectangle([1450, TOP + 300, 1580, TOP + 340], fill=(232, 144, 30))
gear(fr.d, gcx, gtop, 70, 16, 0.0, (150, 155, 160)); gear(fr.d, gcx, gbot, 70, 16, math.pi / 16, (150, 155, 160))
fr.d.arc([gcx - 105, gtop - 105, gcx + 105, gtop + 105], 200, 340, fill=C_FLOW, width=6)
fr.head((gcx + 105 * math.cos(math.radians(330)), gtop + 105 * math.sin(math.radians(330))), (gcx + 105 * math.cos(math.radians(340)), gtop + 105 * math.sin(math.radians(340))), C_FLOW, 6)
fr.d.arc([gcx - 105, gbot - 105, gcx + 105, gbot + 105], 20, 160, fill=C_FLOW, width=6)
fr.head((gcx + 105 * math.cos(math.radians(30)), gbot + 105 * math.sin(math.radians(30))), (gcx + 105 * math.cos(math.radians(20)), gbot + 105 * math.sin(math.radians(20))), C_FLOW, 6)
fr.d.text((1000, TOP + 350), 'P3 = 50 bar*', font=f(19, True), fill=C_TXT); fr.d.text((1462, TOP + 350), 'P4 ≈ 250 bar*', font=f(19, True), fill=C_TXT)
fr.d.text((gcx + 80, gtop - 30), 'quay +', font=f(17), fill=C_TXT); fr.d.text((gcx + 80, gbot + 10), 'quay −', font=f(17), fill=C_TXT)
fr.text_box((1000, TOP + 520), 'Tốc độ bơm là giá trị ĐẶT (chủ): 764 cm³/vòng × ≈ 69 v/ph* → lưu lượng ra khuôn cố định. P3 giữ 50 bar* bằng cách chỉnh cân + vít theo tỉ lệ (Q6a). Nhựa đi vòng ngoài trong rãnh răng; vùng ăn khớp làm kín. Hiển thị chậm 4×.', 18, canvas=True, maxw=560)
fr.chrome('S10', 'out/renders/ze155-melt-line.png (cắt vùng) + sơ đồ vẽ tay'); made.append(fr.save('S10'))

# S11 die plan ---------------------------------------------------------
fr = Frame('drawings/sheet-05-tdie.png', crop=(400, 2350, 2450, 2900), region=(0, TOP + 10, W, TOP + 440), bg=(250, 250, 250))
for side in (-1, 1):
    fr.poly([(.47, .28), (.47 + side * .2, .36), (.47 + side * .4, .46)], C_FLOW, 6)
for x in (.15, .3, .47, .64, .8):
    fr.poly([(x, .52), (x, .80)], C_FLOW, 5)
fr.callout((.47, .27), (.52, .02), 'Cửa vào Ø100 ở giữa')
fr.callout((.25, .38), (.02, .02), 'Ống phân phối móc áo Ø72 → Ø28')
fr.callout((.62, .60), (.70, .60), 'Ra môi: vận tốc đều trên 2 400 mm')
fr.d.rectangle([0, TOP + 450, W, H - BOT], fill=(250, 250, 250))
# exploded sketch
bx0, bx1 = 300, 1300
fr.d.rectangle([bx0, TOP + 650, bx1, TOP + 730], fill=(200, 205, 210), outline=(60, 60, 60), width=2)
fr.d.line([(bx0 + 40, TOP + 655), ((bx0 + bx1) / 2, TOP + 652), (bx1 - 40, TOP + 660)], fill=(232, 144, 30), width=8)
fr.d.rectangle([bx0, TOP + 490, bx1, TOP + 570], fill=(225, 228, 232, 160), outline=(60, 60, 60), width=2)
fr.poly([((bx0 + bx1) / 2, TOP + 640), ((bx0 + bx1) / 2, TOP + 580)], C_CAM, 6, canvas=True)
fr.d.text((bx1 + 20, TOP + 500), 'nửa trên nhấc lên 0,9 m, mờ dần (peel)', font=f(18), fill=C_TXT)
fr.d.text((bx1 + 20, TOP + 670), 'nửa dưới: rãnh móc áo trên mặt Z = 1 200', font=f(18), fill=C_TXT)
fr.d.text((20, TOP + 470), 'Ảnh nền: tờ 05 mặt cắt B-B. Anim: móc áo dẹt (tâm X 9 172 → mép 9 215, tiền môi 32 → 11 mm) để nằm trước thanh chặn X 9 255; hình chèn 2D phóng đại – Q2', font=f(16), fill=(120, 30, 30))
fr.chrome('S11', 'drawings/sheet-05, mặt cắt B-B'); made.append(fr.save('S11'))

# S12 die section A-A --------------------------------------------------
fr = Frame('drawings/sheet-05-tdie.png', crop=(2700, 120, 4950, 2300), region=(0, TOP, 930, H - BOT), bg=(250, 250, 250))
fr.poly([(.13, .557), (.0, .557)], C_FLOW, 6)
fr.poly([(.85, .557), (.72, .557)], C_FLOW, 6)
fr.callout((.69, .557), (.70, .72), 'Ống phân phối Ø72')
fr.callout((.608, .47), (.75, .30), 'Thanh chặn: chỉnh thô')
fr.callout((.398, .48), (.18, .70), 'Rãnh bản lề, gân 12 mm')
fr.callout((.41, .30), (.02, .12), 'Bu-lông nhiệt: nóng → giãn → ép môi')
fr.callout((.14, .557), (.02, .40), 'Khe môi 1,0 mm* (vẽ ×10 trong shot)')
panel(fr, 950, TOP + 20, W - 20, H - BOT - 20, 'Mặt cắt Y = 0 (A-A), nhìn từ +Y')
y = TOP + 64
for t in ['Camera đẩy dần từ thân khuôn tới môi và khe gió (lens 45 → 80 mm).', 'Nhựa: cửa vào → ống phân phối → tiền môi → khe dưới thanh chặn → vùng bản lề → môi.', 'Khe môi và hành trình cùng vẽ phóng đại ×10: khe vẽ 10 mm, môi hạ 1,5 mm (thật 1,0 mm và ±0,15 mm) → không bao giờ đóng khe. Đồng hồ số hiện giá trị thật.', 'Khe gió 200 mm tới khe trục giữa–dưới; trục cán cắt đôi, quay tốc độ thực.', 'Ảnh nền: tờ 05 mặt cắt A-A.']:
    fr.text_box((966, y), '• ' + t, 19, canvas=True, bg=(0, 0, 0, 0), maxw=600); y += 96
fr.chrome('S12', 'drawings/sheet-05, mặt cắt A-A'); made.append(fr.save('S12'))

# S13 curtain -> rolls -> sheet ---------------------------------------
fr = Frame('out/renders/ze155-die-rolls.png')
fr.poly([(.45, .60), (.45, .44)], C_FLOW, 7)
fr.poly([(.38, .40), (.40, .25), (.52, .10), (.70, .04)], C_FLOW, 7)
for c, a0, a1 in (((.24, .10), 140, 20), ((.24, .31), 20, 140), ((.24, .54), 140, 20)):
    fr.arc_arrow(c, 40, a0, a1, (255, 255, 255), 5)
fr.poly([(.55, .95), (.75, .55), (.98, .08)], C_CAM, 6)
fr.cam_icon((.55, .95), 1); fr.cam_icon((.98, .08), 3)
fr.callout((.45, .44), (.50, .40), 'Màn nhựa ≈ 275 °C* vào khe trục giữa–dưới, còn màu hổ phách tới khe trục')
fr.callout((.24, .54), (.03, .62), 'Trục dưới ≈ 60 °C*')
fr.callout((.24, .31), (.03, .36), 'Trục giữa ≈ 55 °C*: tấm trong dần từ khe trục')
fr.callout((.24, .10), (.03, .16), 'Trục trên ≈ 45 °C*')
fr.text_box((.55, .18), 'Tấm 0,8 × 2 100 mm* · ≈ 25 m/min → băng tải + đầu đo chiều dày (ngoài khung, camera lùi ra ở cuối)', 18, maxw=520)
fr.chrome('S13', 'out/renders/ze155-die-rolls.png'); made.append(fr.save('S13'))

# S14 system interaction ----------------------------------------------
fr = Frame('out/renders/ze155-hero.png')
fr.d.rectangle([fr.ox, fr.oy, fr.ox + fr.iw, fr.oy + fr.ih], fill=(0, 0, 0, 90))
RED, BLU, PUR, BRN, MEL, GRY = (224, 64, 43), (47, 127, 216), (123, 79, 201), (139, 90, 43), (208, 52, 44), (230, 230, 230)
fr.poly([(.725, .40), (.75, .43), (.765, .45)], RED, 5, dash=10)
fr.poly([(.575, .42), (.55, .50), (.50, .535)], RED, 5, dash=10)
fr.poly([(.44, .615), (.615, .613)], BLU, 6, arrow=False)
fr.poly([(.4925, .476), (.46, .44), (.43, .42), (.40, .50)], PUR, 6)
fr.poly([(.57, .467), (.50, .43), (.43, .42)], PUR, 6, arrow=False)
fr.poly([(.675, .093), (.672, .25), (.645, .45), (.632, .50)], BRN, 6)
fr.poly([(.62, .53), (.4175, .551), (.37, .54), (.32, .578), (.2725, .627), (.24, .60)], MEL, 7)
def loop(a, b, c, col=GRY, h=.18):
    pts = [a, ((a[0] + b[0]) / 2, min(a[1], b[1]) - h), b, ((b[0] + c[0]) / 2, min(b[1], c[1]) - h), c]
    fr.poly(pts, col, 4, dash=10)
panel(fr, 20, H - BOT - 216, 520, H - BOT - 14, 'Chú giải (bật lần lượt, mỗi lớp ≈ 5 s)')
yy = H - BOT - 178
for col, t, dash in ((RED, '1. Năng lượng: trung thế → biến tần → động cơ; nhiệt', 10), (BLU, '2. Nước làm mát: xi lanh, dầu, động cơ', None), (BRN, '3. Hạt / phụ gia', None), (MEL, '3. Nhựa chảy', None), (PUR, '3. Chân không → bình tách → bơm', None)):
    fr.poly([(36, yy + 10), (90, yy + 10)], col, 5, dash=dash, arrow=False, canvas=True)
    fr.d.text((100, yy), t, font=f(17), fill=C_TXT); yy += 34
fr.text_box((.62, .74), 'Các vòng điều khiển để sang S15 (mỗi vòng ≈ 3 s, có sơ đồ khối).', 18, maxw=520)
fr.chrome('S14', 'out/renders/ze155-hero.png + đường vẽ tay'); made.append(fr.save('S14'))

# S15 control loops ------------------------------------------------------
fr = Frame('out/renders/ze155-hero.png', region=(0, TOP, 1010, H - BOT))
fr.d.rectangle([fr.ox, fr.oy, fr.ox + fr.iw, fr.oy + fr.ih], fill=(0, 0, 0, 110))
GRY, WHT = (210, 210, 210), (255, 255, 255)
def arc(a, b, h, col=WHT, w=4):
    m = ((a[0] + b[0]) / 2, min(a[1], b[1]) - h)
    fr.poly([a, m, b], col, w, dash=10)
arc((.42, .55), (.672, .26), .10)                 # P3 -> feeder
arc((.42, .55), (.77, .45), .12)                  # P3 -> screw motor
arc((.16, .62), (.24, .60), .06, GRY)             # scanner -> rolls
fr.callout((.42, .55), (.02, .05), '(2) P3 → cân + vít')
fr.callout((.33, .58), (.02, .80), '(1) tốc độ bơm đặt (chủ)')
fr.callout((.77, .45), (.62, .80), 'động cơ vít')
fr.poly([(.95, .20), (.95, .05)], C_CAM, 5); fr.text_box((.70, .04), 'camera: 3 vùng (cấp liệu–bơm, khuôn–trục–đầu đo, đường chảy–xi lanh)', 15, maxw=290)
panel(fr, 1025, TOP + 10, W - 12, H - BOT - 10, 'Sơ đồ khối (HUD, tô sáng vòng đang nói)')
BR, RD, SG = (139, 90, 43), (208, 52, 44), (40, 40, 40)
def ln(pts, col, dash=None, lab=None, lp=None):
    fr.poly(pts, col, 3, dash=dash, canvas=True)
    if lab: fr.d.text(lp, lab, font=f(16, True), fill=col)
ln([(1170, 132), (1195, 132), (1195, 280), (1150, 280), (1150, 290)], BR)
ln([(1105, 234), (1105, 290)], BR)
ln([(1170, 312), (1215, 312)], RD)
ln([(1305, 322), (1340, 322)], RD)
ln([(1440, 344), (1440, 400)], RD)
ln([(1440, 444), (1440, 500)], RD)
ln([(1340, 522), (1262, 522)], RD)
ln([(1260, 300), (1260, 216)], SG, 8, '(2)', (1266, 246))
ln([(1215, 182), (1172, 140)], SG, 8)
ln([(1215, 204), (1172, 214)], SG, 8)
ln([(1185, 500), (1185, 478), (1318, 478), (1318, 512), (1338, 512)], (90, 90, 90), 8, '(3)', (1230, 482))
ln([(1160, 500), (1160, 424), (1338, 424)], (90, 90, 90), 8, '(4)', (1230, 400))
B = [((1040, 110, 130), 'Cân LIW', True), ((1040, 190, 130), 'Động cơ vít', True), ((1040, 290, 130), 'Máy đùn', False),
     ((1215, 290, 90), 'P3', True), ((1340, 290, 200), 'Bơm (biến tần) (1)', True), ((1340, 400, 200), 'Khuôn + bu-lông nhiệt', False),
     ((1340, 500, 200), 'Trục cán', False), ((1110, 500, 150), 'Đầu đo', False), ((1215, 170, 120), 'PLC', True)]
for (x, y, w), t, hl in B:
    fr.d.rounded_rectangle([x, y, x + w, y + 44], 8, fill=(255, 220, 160) if hl else (235, 236, 238), outline=(40, 40, 40), width=2)
    fr.d.text((x + 8, y + 11), t, font=f(16, hl), fill=C_TXT)
fr.d.text((1040, 600), '(1) Bơm: tốc độ đặt → lưu lượng ra khuôn cố định', font=f(16, True), fill=C_TXT)
fr.d.text((1040, 626), '(2) P3 50 bar* → PLC chỉnh cân + vít theo tỉ lệ', font=f(16), fill=C_TXT)
fr.d.text((1040, 652), '(3) Chiều dày TB → tốc độ trục cán', font=f(16), fill=C_TXT)
fr.d.text((1040, 678), '(4) Profin ngang → 94 bu-lông nhiệt', font=f(16), fill=C_TXT)
fr.d.text((1040, 704), '(5) PDI lọc · (6) TIC 20 vùng · (7) liên động → STO', font=f(16), fill=C_TXT)
fr.d.text((1040, 740), 'Q6b (design s_20): P3 → tốc độ bơm, cân đặt lưu lượng', font=f(15), fill=(120, 30, 30))
fr.chrome('S15', 'out/renders/ze155-hero.png + sơ đồ khối vẽ tay'); made.append(fr.save('S15'))

# S16 closing ----------------------------------------------------------
fr = Frame('out/renders/ze155-front.png')
panel(fr, 60, TOP + 30, 1120, TOP + 300, 'PET không sấy → tấm vô định hình 0,8 mm* · 3,5 t/h*')
yy = TOP + 80
for t in ['1. Khử ẩm bằng 2 vùng chân không sau các nút nhựa', '2. Bơm bánh răng đặt lưu lượng ra khuôn; áp hút P3 chỉnh cân + vít', '3. Khuôn móc áo + 94 bu-lông nhiệt giữ chiều dày đều trên 2,1 m']:
    fr.d.text((84, yy), t, font=f(22), fill=C_TXT); yy += 56
fr.d.text((84, yy - 6), 'Giữ 10 s (≈ 35 chữ). Nếu chọn Q6b, dòng 2: "Cân đặt lưu lượng; bơm giữ áp hút P3".', font=f(16), fill=(120, 30, 30))
fr.chrome('S16', 'out/renders/ze155-front.png'); made.append(fr.save('S16'))

# ------------------------------------------------------------------ contact sheet
cols, tw = 3, 620
th = int(tw * H / W)
pad, head = 16, 70
rows = math.ceil(len(made) / cols)
sheet = Image.new('RGB', (cols * tw + (cols + 1) * pad, head + rows * (th + 40 + pad) + pad), (30, 32, 36))
d = ImageDraw.Draw(sheet)
total = sum(SHOTS[s]['duration_s'] for s in SHOTS)
d.text((pad, 18), f'ZE 155 – storyboard animation · {len(SHOTS)} shot · {total:.0f} s ({total // 60:.0f}:{total % 60:02.0f}) · 25 fps · 1920×1080', font=f(30, True), fill=(255, 255, 255))
for i, p in enumerate(made):
    sid = os.path.basename(p)[:-4]
    im = Image.open(p).resize((tw, th), Image.LANCZOS)
    x = pad + (i % cols) * (tw + pad); y = head + (i // cols) * (th + 40 + pad)
    sheet.paste(im, (x, y))
    s = SHOTS[sid]
    t_ = f"{sid} · {s['duration_s']:.0f} s · {s['title_vi']}"
    while d.textlength(t_, font=f(19)) > tw and len(t_) > 10: t_ = t_[:-2]
    d.text((x, y + th + 6), t_ if t_.endswith(s['title_vi']) else t_ + '…', font=f(19), fill=(230, 230, 230))
sheet.save(os.path.join(OUT, 'contact.png'))
print('frames:', len(made), '→', OUT)
