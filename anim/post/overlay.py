"""Draw every label and HUD element of the ZE 155 animation onto the rendered frames (Pillow, no Blender).

    uv run -q --with pillow --with numpy python anim/post/overlay.py [options]

Inputs  anim/shots.json, anim/interior_parts.json (read only)
        anim/render/anchors/<SHOT>.json      per-frame 2D anchors exported by the A3 builder (see ANCHORS.md)
        anim/render/frames/####.png          Blender frames, only for --mode final
Outputs --mode overlay (default): anim/render/overlay/####.png  RGBA 1920x1080, transparent where nothing is drawn;
                                  assemble.py composites them over the frames inside ffmpeg
        --mode final:             anim/render/final/####.png    frame + overlay, same size as the input frame
        anim/render/overlay_report.md  anchor sources, off-screen anchors, layout conflicts

Resumable: existing output files are skipped (use --force to redraw). Frames are drawn in parallel processes.
The label layout is computed per shot, sequentially from the shot's first frame, so it is identical whatever
frame subset is drawn and however the work is split.
"""
import argparse
import math
import os
import re
import sys
import time
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (FADE, NBSP, H, RENDER, W, font, glue, load_shots, missing_glyphs, parse_ranges,  # noqa: E402
                    project, ramp_alpha, screw_check, screw_rows, simulated_camera, smoothstep, wrap)

# ------------------------------------------------------------------ look
BG = (14, 16, 20)
AMBER = (255, 184, 28)
WHITE = (244, 245, 247)
GREY = (168, 174, 184)
DIM = (110, 116, 126)
MELT = (232, 144, 30)
BLUE = (96, 172, 255)
PURPLE = (150, 112, 232)
LABEL_BG = (250, 250, 247)
LABEL_TXT = (18, 18, 20)

TITLE_H = 60
MARGIN = 24
FOOT_H = 32
FOOT_Y = H - 12 - FOOT_H                 # 1036
HUD_BOTTOM = FOOT_Y - 8                  # panels above the footer end here (1028)
SAFE = (14, TITLE_H + 8, W - 14, H - 10)

LABEL_SIZE, LABEL_LINE, LABEL_MAXW = 26, 33, 560
LABEL_PADX, LABEL_PADY, LABEL_ACCENT = 14, 9, 6

STRIP_RECT = (MARGIN, HUD_BOTTOM - 210, W - MARGIN, HUD_BOTTOM)
S15_RECT = (1300, TITLE_H + 12, W - MARGIN, HUD_BOTTOM)
S11_RECT = (W - MARGIN - 600, TITLE_H + 12, W - MARGIN, TITLE_H + 12 + 360)
S12_RECT = (W - MARGIN - 440, HUD_BOTTOM - 196, W - MARGIN, HUD_BOTTOM)
S16_RECT = (240, 96, W - 240, 440)

# ------------------------------------------------------------------ fixed HUD text (Vietnamese UI strings)
FLAG = {   # shots whose speed badge does not already say "minh họa" but show schematic flows
    'S01': 'Trục quy trình: minh họa', 'S04': 'Nhựa: minh họa', 'S06': 'Nhựa: minh họa', 'S08': 'Nhựa: minh họa',
    'S10': 'Túi nhựa: minh họa', 'S12': 'Dòng chảy: minh họa', 'S14': 'Dòng chảy: minh họa', 'S15': 'Dòng chảy: minh họa',
}
S12_BADGE_BEFORE_X10 = 'Tốc độ thực'          # rolls; the ×10 badge from shots.json appears with gap_x10
ZONES = [(0, 1521, 'Nhận hạt'), (1521, 1859, 'Nóng chảy'), (1859, 1985.75, 'Nút 1'), (1985.75, 2492.75, 'Thoát khí 1'),
         (2492.75, 2830.75, 'Vận chuyển'), (2830.75, 3337.75, 'Trộn'), (3337.75, 3718, 'Nút 2'),
         (3718, 4478.5, 'Thoát khí 2'), (4478.5, 5746, 'Tăng áp')]
BARRELS = [(0, 676, 'B1'), (676, 1690, 'B2'), (1690, 2704, 'B3'), (2704, 3718, 'B4'), (3718, 4732, 'B5'), (4732, 5746, 'B6')]
PRESSURE = [(0, 0), (1521, 0), (1859, 8), (1985.75, 0), (2830.75, 0), (3337.75, 6), (3633.5, 12), (3718, 0),
            (4478.5, 0), (5154.5, 40), (5746, 100)]   # bar, schematic (storyboard S06); P1 ≈ 100 bar* at the tip
STRIP_TXT = {'title': 'Cấu hình vít · độ điền · áp suất (sơ đồ)', 'fill': 'độ điền', 'p': 'áp suất',
             'vent': 'cửa sổ chân không', 'view': 'trong khung hình', 'flow': 'dòng chảy', 'p1': 'P1 ≈ 100 bar*',
             'vent1': 'chân không 1', 'vent2': 'chân không 2'}
LEGEND_VI = {'melt': 'Nhựa chảy', 'material': 'Hạt / vật liệu', 'water supply / return': 'Nước cấp / hồi',
             'vacuum': 'Chân không', 'oil': 'Dầu', 'hydraulic': 'Thủy lực', 'air': 'Khí nén', 'power': 'Điện',
             'signal': 'Tín hiệu'}
LEGEND_TITLE = 'Chú giải lớp phủ'
S15_TXT = {'title': 'Sơ đồ khối điều khiển', 'sub': 'nét đứt = tín hiệu · tô sáng = vòng đang nói',
           'loops': 'Vòng điều khiển', 'note': 'Q6a: bơm đặt lưu lượng; P3 chỉnh cân + vít'}
S15_LOOPS = {1: 'Bơm: tốc độ đặt → lưu lượng cố định', 2: 'PIC-P3 → cân LIW + tốc độ vít',
             3: 'Chiều dày TB → tốc độ trục cán', 4: 'Profin ngang → 94 bu-lông nhiệt',
             5: 'PDI P2/P3 → nhịp quay đĩa lọc', 6: 'TIC × 20 → băng nhiệt / van nước', 7: 'Liên động P1/P4 → STO'}
S11_TXT = {'title': 'Móc áo: phóng đại, không theo tỉ lệ', 'sub': 'Khuôn 3D trong phim: gần chữ T (tiền môi 32 → 11 mm)',
           'inlet': 'cửa vào', 'manifold': 'ống phân phối', 'long': 'tiền môi dài', 'short': 'ngắn',
           'lip': 'môi 2 400 mm · vận tốc ra đều'}
S12_TXT = {'title': 'Khe môi thật', 'nominal': 'danh định', 'note': 'Bu-lông nhiệt ±0,15 mm · hình 3D vẽ ×10',
           'hot': 'bu-lông nóng'}


def all_fixed_strings():
    out = list(FLAG.values()) + [S12_BADGE_BEFORE_X10] + [z[2] for z in ZONES] + [b[2] for b in BARRELS]
    for d in (STRIP_TXT, LEGEND_VI, S15_TXT, S15_LOOPS, S11_TXT, S12_TXT):
        out += list(d.values())
    return out + [LEGEND_TITLE, '0,85', '1,00', '1,15', 'mm', '−0,15', 'X 0', 'X 5 746', '←', '→']


# ------------------------------------------------------------------ small geometry
def overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def expand(r, m):
    return (r[0] - m, r[1] - m, r[2] + m, r[3] + m)


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def nearest_on_rect(p, r):
    return (min(max(p[0], r[0]), r[2]), min(max(p[1], r[1]), r[3]))


def _ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])


def seg_cross(p1, p2, q1, q2):
    d1, d2, d3, d4 = _ccw(q1, q2, p1), _ccw(q1, q2, p2), _ccw(p1, p2, q1), _ccw(p1, p2, q2)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def seg_hits_rect(p1, p2, r):
    if inside(p1, r) or inside(p2, r):
        return True
    c = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    return any(seg_cross(p1, p2, c[i], c[(i + 1) % 4]) for i in range(4))


# ------------------------------------------------------------------ panels (drawn supersampled on an opaque RGB
# canvas so every translucent shape blends correctly, then reduced and given a rounded alpha mask)
_MASKS = {}


def rounded_mask(w, h, r, ss=3):
    key = (w, h, r)
    if key not in _MASKS:
        m = Image.new('L', (w * ss, h * ss), 0)
        if r > 0:
            ImageDraw.Draw(m).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], r * ss, fill=255)
        else:
            m.paste(255, (0, 0, w * ss, h * ss))
        _MASKS[key] = m.reduce(ss)
    return _MASKS[key]


class Panel:
    def __init__(self, w, h, bg=BG, alpha=212, radius=10, ss=2, border=None):
        self.w, self.h, self.alpha, self.radius, self.ss, self.border = int(w), int(h), alpha, radius, ss, border
        self.im = Image.new('RGB', (self.w * ss, self.h * ss), bg)
        self.d = ImageDraw.Draw(self.im, 'RGBA')

    def clone(self):
        p = Panel.__new__(Panel)
        p.__dict__.update(self.__dict__)
        p.im = self.im.copy()
        p.d = ImageDraw.Draw(p.im, 'RGBA')
        return p

    def _p(self, pts):
        s = self.ss
        return [(x * s, y * s) for x, y in pts]

    def rect(self, box, fill=None, outline=None, width=1, radius=0):
        b = [v * self.ss for v in box]
        if radius:
            self.d.rounded_rectangle(b, radius * self.ss, fill=fill, outline=outline, width=max(1, int(width * self.ss)))
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=max(1, int(width * self.ss)))

    def line(self, pts, fill, width=1.0):
        self.d.line(self._p(pts), fill=fill, width=max(1, int(round(width * self.ss))), joint='curve')

    def poly(self, pts, fill=None, outline=None):
        self.d.polygon(self._p(pts), fill=fill, outline=outline)

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse([v * self.ss for v in box], fill=fill, outline=outline, width=max(1, int(width * self.ss)))

    def text(self, xy, s, size, bold=False, fill=WHITE, anchor='la'):
        self.d.text((xy[0] * self.ss, xy[1] * self.ss), s, font=font(size * self.ss, bold), fill=fill, anchor=anchor)

    @staticmethod
    def tlen(s, size, bold=False):
        return font(size * 4, bold).getlength(s) / 4

    def finish(self, alpha_mul=1.0):
        im = self.im.reduce(self.ss) if self.ss > 1 else self.im
        out = im.convert('RGBA')
        a = self.alpha * alpha_mul / 255.0
        m = rounded_mask(self.w, self.h, self.radius)
        out.putalpha(m.point(lambda v: int(v * a)) if a < 0.999 else m)
        if self.border:
            ImageDraw.Draw(out).rounded_rectangle([0, 0, self.w - 1, self.h - 1], self.radius, outline=self.border, width=1)
        return out


def fade(img, a):
    if a >= 0.999:
        return img
    lut = [int(v * a) for v in range(256)]
    img = img.copy()
    img.putalpha(img.getchannel('A').point(lut))
    return img


def dashed(p, pts, fill, width, dash=10, gap=7, offset=0.0):
    """Dashed polyline on a Panel (1x coordinates); offset shifts the pattern along the line (animated pulses)."""
    period = dash + gap
    s0 = -(offset % period)
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if L < 1e-6:
            continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        t = s0
        while t < L:
            t0, t1 = max(t, 0), min(t + dash, L)
            if t1 > t0:
                p.line([(a[0] + ux * t0, a[1] + uy * t0), (a[0] + ux * t1, a[1] + uy * t1)], fill, width)
            t += period
        s0 = t - L - period


def arrowhead(p, a, b, fill, size=11):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    p1 = (b[0] - size * math.cos(ang - 0.45), b[1] - size * math.sin(ang - 0.45))
    p2 = (b[0] - size * math.cos(ang + 0.45), b[1] - size * math.sin(ang + 0.45))
    p.poly([b, p1, p2], fill=fill)


# ------------------------------------------------------------------ shot helpers
def anim_window(shot, *keywords, default=None):
    """Parse '+a…+b' from the shots.json 'animated' entry whose object/property mentions all keywords."""
    for e in shot.get('animated', []):
        blob = f"{e.get('object', '')} {e.get('property', '')}"
        if all(k in blob for k in keywords):
            m = re.search(r'\+(\d+)\s*…\s*\+(\d+)', e.get('rate', ''))
            if m:
                return shot['frames'][0] + int(m.group(1)), shot['frames'][0] + int(m.group(2))
    return (shot['frames'][0] + default[0], shot['frames'][0] + default[1]) if default else None


def strip_shots(shots):
    """Shots with the screw strip: hud.strip in shots.json, plus S08 (the brief lists S04/S06/S08)."""
    return {s['id'] for s in shots if s.get('hud', {}).get('strip')} | {'S08'}


def loop_number(text):
    m = re.match(r'\s*\((\d)\)', text)
    return int(m.group(1)) if m else None


def wrap_balanced(text, fnt, maxw):
    """Fewest lines at maxw without orphan words. Two lines: try every break, prefer the narrowest box,
    with a bonus for breaking after ':' '·' ',' or before '→' '(' (keeps phrases together)."""
    lines = wrap(text, fnt, maxw)
    if len(lines) <= 1:
        return lines
    toks = glue(text).split(' ')
    if len(lines) == 2:
        best = None
        for k in range(1, len(toks)):
            l1, l2 = ' '.join(toks[:k]).replace(NBSP, ' '), ' '.join(toks[k:]).replace(NBSP, ' ')
            w1, w2 = fnt.getlength(l1), fnt.getlength(l2)
            if max(w1, w2) > maxw:
                continue
            bonus = 70 if l1[-1:] in (':', '·', ',') else 50 if l2[:1] in ('→', '(') else 0
            cost = max(w1, w2) - bonus
            if best is None or cost < best[0]:
                best = (cost, [l1, l2])
        if best:
            return best[1]
    lo, hi = max(fnt.getlength(w.replace(NBSP, ' ')) for w in toks), float(maxw)
    while hi - lo > 2:
        mid = (lo + hi) / 2
        if len(wrap(text, fnt, mid)) <= len(lines):
            hi = mid
        else:
            lo = mid
    return wrap(text, fnt, hi)


def label_box_size(text):
    f = font(LABEL_SIZE)
    lines = [l[:-2] if l.endswith(' ·') else l for l in wrap_balanced(text, f, LABEL_MAXW)]
    tw = max(Panel.tlen(l, LABEL_SIZE) for l in lines)       # measured like the supersampled drawing
    return lines, int(math.ceil(tw + 2 * LABEL_PADX + LABEL_ACCENT)), int(len(lines) * LABEL_LINE + 2 * LABEL_PADY - 4)


def hud_obstacles(shot, f, sid_strip, values_rect, s11_win, s12_on):
    sid = shot['id']
    obs = [(0, 0, W, TITLE_H + 4), footer_rect(shot)]
    if values_rect:
        obs.append(values_rect)
    if sid in sid_strip:
        obs.append(STRIP_RECT)
    if sid == 'S15':
        obs.append(S15_RECT)
    if sid == 'S14':
        obs.append(legend_rect(shot))
    if sid == 'S11' and s11_win and s11_win[0] <= f <= s11_win[1]:
        obs.append(S11_RECT)
    if sid == 'S12' and s12_on:
        obs.append(S12_RECT)
    if sid == 'S16':
        obs.append(S16_RECT)
    return [o for o in obs if o]


def footer_rect(shot):
    t = shot.get('hud', {}).get('footer')
    if not t:
        return None
    return (MARGIN, FOOT_Y, MARGIN + int(Panel.tlen(t, 20)) + 28, FOOT_Y + FOOT_H)


def values_lines(shot):
    if shot['id'] in ('S16', 'S15', 'S14'):
        return []
    return list(shot.get('hud', {}).get('values', []))


def values_rect(shot):
    lines = values_lines(shot)
    if not lines:
        return None
    w = int(max(Panel.tlen(l, 22) for l in lines)) + 2 * 14 + 6
    return (MARGIN, TITLE_H + 14, MARGIN + w, TITLE_H + 14 + len(lines) * 30 + 16)


def legend_items(shot):
    leg = shot.get('hud', {}).get('legend') or {}
    items = []
    for k, v in leg.items():
        m = re.search(r'#([0-9A-Fa-f]{6})', v)
        col = tuple(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)) if m else GREY
        style = 'dashdot' if 'dash-dot' in v else 'dotted' if 'dotted' in v else \
            'solid/dashed' if 'solid / dashed' in v else 'dashed' if 'dashed' in v else 'solid'
        items.append((LEGEND_VI.get(k, k), col, style))
    return items


def legend_rect(shot):
    items = legend_items(shot)
    if not items:
        return None
    rows = math.ceil(len(items) / 2)
    h = 44 + rows * 30 + 6
    return (MARGIN, HUD_BOTTOM - h, MARGIN + 560, HUD_BOTTOM)


# ------------------------------------------------------------------ anchors
class AnchorSource:
    """Per-frame 2D anchors for one shot: from anim/render/anchors/<SHOT>.json, else simulated from shots.json."""

    def __init__(self, shot, anchors_dir, allow_sim=True):
        import json
        self.shot = shot
        self.warn = []
        self.cam_frames = None
        path = os.path.join(anchors_dir, f"{shot['id']}.json") if anchors_dir else None
        self.source = 'file'
        if path and os.path.exists(path):
            with open(path, encoding='utf-8') as fh:
                d = json.load(fh)
            if d.get('format') != 'ze155-anchors/1':
                self.warn.append(f"{path}: format {d.get('format')!r}, expected 'ze155-anchors/1'")
            self.ref = d.get('ref_resolution', [W, H])
            self.frames = np.array(d['frames'], float)
            self.xy = {k: np.array(v['xy'], float) for k, v in d.get('anchors', {}).items()}
            self.anchor_m = {k: v.get('anchor_m') for k, v in d.get('anchors', {}).items()}
            self.tracks = {k: np.array(v, float) for k, v in d.get('tracks', {}).items()}
            cam = d.get('camera')
            if cam and cam.get('matrix_world'):
                self.cam = cam
                self.cam_frames = self.frames
            else:
                self.cam = None
            a, b = shot['frames']
            if self.frames[0] > a or self.frames[-1] < b:
                self.warn.append(f"{shot['id']}: anchors cover {int(self.frames[0])}–{int(self.frames[-1])}, shot is {a}–{b} (ends held)")
            # compare with shots.json
            for i, l in enumerate(shot['labels']):
                k = f'L{i}'
                if k not in self.xy:
                    self.warn.append(f"{shot['id']} {k}: missing in anchor file" + ('; reprojected from camera' if self.cam else '; drawn without leader'))
                elif self.anchor_m.get(k) and max(abs(p - q) for p, q in zip(self.anchor_m[k], l['anchor_m'])) > 0.001:
                    if self.cam:
                        self.warn.append(f"{shot['id']} {k}: anchor_m changed in shots.json; reprojected from the exported camera (occlusion unknown)")
                        del self.xy[k]
                    else:
                        self.warn.append(f"{shot['id']} {k}: anchor_m in the file {self.anchor_m[k]} != shots.json {l['anchor_m']}; re-export anchors")
        elif allow_sim:
            self.source = 'simulated'
            self.warn.append(f"{shot['id']}: no anchor file, anchors SIMULATED from shots.json camera keys (approximate)")
            self.frames, self.xy, self.tracks, self.cam = None, {}, {}, None
        else:
            raise FileNotFoundError(path)

    # -- camera
    def camera(self, f):
        if self.cam is not None:
            i = int(np.clip(np.searchsorted(self.cam_frames, f), 0, len(self.cam_frames) - 1))
            if i > 0 and abs(self.cam_frames[i - 1] - f) < abs(self.cam_frames[i] - f):
                i -= 1
            c, n = self.cam, len(self.cam_frames)

            def pick(k, dflt):
                v = c.get(k)
                if v is None:
                    return dflt
                if isinstance(v, list) and len(v) == n and (k != 'shift' or isinstance(v[0], (list, tuple))):
                    return v[i]
                return v
            return {'matrix_world': np.array(pick('matrix_world', None), float).reshape(4, 4), 'lens_mm': pick('lens_mm', 50.0),
                    'sensor_width_mm': pick('sensor_width_mm', 36.0), 'sensor_fit': pick('sensor_fit', 'AUTO'),
                    'type': pick('type', 'PERSP'), 'ortho_scale': pick('ortho_scale', 1.0), 'shift': pick('shift', (0.0, 0.0))}
        if self.source == 'simulated':
            return simulated_camera(self.shot, f)
        return None

    def _interp(self, arr, f):
        fr = self.frames
        if f <= fr[0]:
            return arr[0]
        if f >= fr[-1]:
            return arr[-1]
        i = int(np.searchsorted(fr, f))
        if fr[i] == f:
            return arr[i]
        t = (f - fr[i - 1]) / (fr[i] - fr[i - 1])
        out = arr[i - 1] + (arr[i] - arr[i - 1]) * t
        if arr.ndim > 1 and arr.shape[1] >= 4:      # flags: visible only if both samples agree; occluded if either
            out[2] = min(arr[i - 1][2], arr[i][2])
            out[3] = max(arr[i - 1][3], arr[i][3])
        return out

    def anchor(self, i, f):
        """(x, y, in_front, occluded) in 1920x1080 px, or None."""
        k = f'L{i}'
        if self.frames is not None and k in self.xy:
            v = self._interp(self.xy[k], f)
            sx, sy = W / self.ref[0], H / self.ref[1]
            return (v[0] * sx, v[1] * sy, bool(v[2] > 0.5), bool(v[3] > 0.5) if len(v) > 3 else False)
        cam = self.camera(f)
        if cam is None:
            return None
        x, y, front = project(cam, self.shot['labels'][i]['anchor_m'])
        return (x, y, front, False)

    def track(self, name, f):
        if self.frames is not None and name in self.tracks:
            return self._interp(self.tracks[name], f)
        return None

    def target_x_mm(self, f):
        t = self.track('cam_target_m', f)
        if t is not None:
            return float(np.atleast_1d(t)[0]) * 1000.0
        if self.source == 'simulated':
            return simulated_camera(self.shot, f)['target_m'][0] * 1000.0
        return None

    def axis_span_mm(self, f):
        """X range (mm) of the screw axis (Y 0, Z 1.2 m) inside the frame, if a camera is known."""
        cam = self.camera(f)
        if cam is None:
            return None
        xs = np.arange(-50, 5800, 25.0)
        ok = []
        for X in xs:
            x, y, front = project(cam, (X / 1000.0, 0.0, 1.2))
            if front and 0 <= x <= W and TITLE_H <= y <= H:
                ok.append(X)
        return (max(0.0, min(ok)), min(5746.0, max(ok))) if ok else None

    def strip_reversed(self, f):
        cam = self.camera(f)
        if cam is None:
            return True     # camera on the operator side (+Y): +X runs to screen left
        x0 = project(cam, (0.0, 0.0, 1.2))[0]
        x1 = project(cam, (5.746, 0.0, 1.2))[0]
        return x1 < x0


# ------------------------------------------------------------------ layout
DIRS = [(0, -1), (0.707, -0.707), (-0.707, -0.707), (1, 0), (-1, 0), (0.707, 0.707), (-0.707, 0.707), (0, 1)]
DISTS = (46, 100, 170, 250)
KEEP_BONUS = 700.0
GRID = [(SAFE[0] + (SAFE[2] - SAFE[0]) * (k + 0.5) / 7, SAFE[1] + (SAFE[3] - SAFE[1]) * (j + 0.5) / 6)
        for k in range(7) for j in range(6)]
SMOOTH = 0.2


def _clamp_center(cx, cy, w, h):
    x0, y0, x1, y1 = SAFE
    nx = min(max(cx, x0 + w / 2), x1 - w / 2)
    ny = min(max(cy, y0 + h / 2), y1 - h / 2)
    return nx, ny, abs(nx - cx) + abs(ny - cy)


def _score(rect, A, on, ctx):
    s = 0.0
    if on:
        q = nearest_on_rect(A, rect)
        d = math.dist(q, A)
        s += d
        if d < 12:
            s += 1e5                      # box covers its own anchor
        seg = (q, A)
        for L in ctx['leaders']:
            if L and seg_cross(seg[0], seg[1], L[0], L[1]):
                s += 2500
        for r in ctx['boxes']:
            if seg_hits_rect(seg[0], seg[1], r):
                s += 3000
        for r in ctx['obstacles']:
            if seg_hits_rect(seg[0], seg[1], expand(r, -2)):
                s += 900
    er = expand(rect, 12)
    for r in ctx['boxes']:
        ov = overlap(er, r)
        if ov > 0:
            s += 2500 + ov * 1.5
    for r in ctx['obstacles']:
        s += overlap(expand(rect, 6), r) * 1.0
    for p in ctx['anchors']:
        if inside(p, expand(rect, 16)):
            s += 6000
    for L in ctx['leaders']:
        if L and seg_hits_rect(L[0], L[1], rect):
            s += 3000
    return s


def layout_shot(shot, src, obstacles_fn, f_last=None):
    """Sequential, deterministic label placement for one shot. Returns {frame: [placement, ...]}.
    placement = (label index, alpha, rect, anchor xy or None (no leader), occluded)."""
    labels = shot['labels']
    a, b = shot['frames']
    b = min(b, f_last) if f_last else b
    order = sorted(range(len(labels)), key=lambda i: (labels[i]['frame_in'], i))
    sizes = {i: label_box_size(labels[i]['text'])[1:] for i in order}
    state, out, stats = {}, {}, {i: {'frames': 0, 'off': 0, 'hud': 0, 'occ': 0, 'overlap': 0} for i in order}
    for f in range(a, b + 1):
        vis = [i for i in order if ramp_alpha(f, labels[i]['frame_in'], labels[i]['frame_out']) > 0]
        for i in list(state):
            if i not in vis:
                del state[i]
        anc = {i: src.anchor(i, f) for i in vis}
        obstacles = obstacles_fn(f)
        onscr, under = {}, {}
        for i in vis:
            A = anc[i]
            onscr[i] = bool(A and A[2] and 0 <= A[0] <= W and 0 <= A[1] <= H)
            under[i] = onscr[i] and any(inside((A[0], A[1]), r) for r in obstacles)
            onscr[i] = onscr[i] and not under[i]      # an anchor hidden by a HUD panel gets no leader
        ctx = {'boxes': [], 'leaders': [], 'obstacles': obstacles,
               'anchors': [(anc[i][0], anc[i][1]) for i in vis if onscr[i]]}
        placed = []
        for i in vis:
            w, h = sizes[i]
            A = anc[i]
            on = onscr[i]
            st = state.get(i)
            if on:
                ax, ay = A[0], A[1]
            elif st:
                ax, ay = st['ax'], st['ay']
            elif A and A[2]:
                ax, ay = min(max(A[0], SAFE[0]), SAFE[2]), min(max(A[1], SAFE[1]), SAFE[3])
            else:
                ax, ay = W / 2, H / 2
            ctx_self = dict(ctx, anchors=[p for p in ctx['anchors'] if not (on and p == (ax, ay))])
            cands = []
            if st:
                kx, ky = st['cx'] + (ax - st['ax']), st['cy'] + (ay - st['ay'])
                kx, ky, sh = _clamp_center(kx, ky, w, h)
                cands.append((kx, ky, sh, True))
            for dx, dy in DIRS:
                for dist in DISTS:
                    cx = ax + dx * dist + (np.sign(dx) * w / 2 if abs(dx) > 0.01 else 0)
                    cy = ay + dy * dist + (np.sign(dy) * h / 2 if abs(dy) > 0.01 else 0)
                    cx, cy, sh = _clamp_center(cx, cy, w, h)
                    cands.append((cx, cy, sh, False))
            for gx, gy in GRID:                       # fallback when the neighbourhood is crowded
                cx, cy, _ = _clamp_center(gx, gy, w, h)
                cands.append((cx, cy, 0.0, False))
            best, best_s = None, None
            for cx, cy, sh, keep in cands:
                rect = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                s = _score(rect, (ax, ay), on, ctx_self) + sh * 4 - (KEEP_BONUS if keep else 0)
                if not on:
                    s += 0.5 * math.dist(nearest_on_rect((ax, ay), rect), (ax, ay))
                if best_s is None or s < best_s:
                    best, best_s = (cx, cy, keep), s
            cx, cy, keep = best
            if st and not keep:
                # glide toward the new spot, but never through a bad one (over its own anchor or another box)
                kx, ky = cands[0][0], cands[0][1]
                tx, ty = cx, cy
                for step in (SMOOTH, 0.5, 1.0):
                    cx, cy, _ = _clamp_center(kx + (tx - kx) * step, ky + (ty - ky) * step, w, h)
                    r2 = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                    bad = (on and math.dist(nearest_on_rect((ax, ay), r2), (ax, ay)) < 12) or \
                        any(overlap(expand(r2, 4), r) > 0 for r in ctx['boxes'])
                    if not bad:
                        break
            rect = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            leader = None
            if on and not inside((ax, ay), rect):
                leader = (nearest_on_rect((ax, ay), rect), (ax, ay))
            occ = bool(on and A[3])
            stt = stats[i]
            stt['frames'] += 1
            stt['off'] += 0 if on else 1
            stt['hud'] += 1 if under[i] else 0
            stt['occ'] += 1 if occ else 0
            if any(overlap(rect, r) > 0 for r in ctx['boxes']):
                stt['overlap'] += 1
            ctx['boxes'].append(rect)
            ctx['leaders'].append(leader)
            state[i] = {'cx': cx, 'cy': cy, 'ax': ax, 'ay': ay}
            alpha = ramp_alpha(f, labels[i]['frame_in'], labels[i]['frame_out'])
            placed.append((i, alpha, rect, (ax, ay) if leader else None, occ))
        out[f] = placed
    return out, stats


# ------------------------------------------------------------------ plan (per-frame parameters, built in the main process)
def s12_values(shot, src, f):
    gw = anim_window(shot, 'gap_x10', default=(140, 170))
    lw = anim_window(shot, 'lip_push', default=(180, 300))
    g = src.track('gap_x10', f)
    lp = src.track('lip_push', f)
    if g is None:
        g = smoothstep((f - gw[0]) / max(1, gw[1] - gw[0]))
    if lp is None:
        mid = (lw[0] + lw[1]) / 2
        lp = smoothstep((f - lw[0]) / max(1, mid - lw[0])) if f <= mid else 1 - smoothstep((f - mid) / max(1, lw[1] - mid))
    return float(np.clip(g, 0, 1)), float(np.clip(lp, 0, 1))


def build_plans(shots, frames, anchors_dir, allow_sim=True):
    by_id = {s['id']: s for s in shots}
    want = {}
    for f in frames:
        for s in shots:
            if s['frames'][0] <= f <= s['frames'][1]:
                want.setdefault(s['id'], []).append(f)
    sids_strip = strip_shots(shots)
    plans, report = [], {'shots': {}, 'warn': []}
    for sid, fl in want.items():
        shot = by_id[sid]
        src = AnchorSource(shot, anchors_dir, allow_sim)
        report['warn'] += src.warn
        vrect = values_rect(shot)
        s11w = anim_window(shot, 'HUD inset', default=(190, 349)) if sid == 'S11' else None
        if s11w:
            s11w = (s11w[0], min(s11w[1], shot['frames'][1]))
        s12 = {f: s12_values(shot, src, f) for f in range(shot['frames'][0], max(fl) + 1)} if sid == 'S12' else {}

        def obstacles(f, shot=shot, vrect=vrect, s11w=s11w, s12=s12):
            return hud_obstacles(shot, f, sids_strip, vrect, s11w, bool(s12.get(f, (0, 0))[0] > 0.001))
        lay, stats = layout_shot(shot, src, obstacles, f_last=max(fl))
        report['shots'][sid] = {'source': src.source, 'stats': stats, 'labels': shot['labels']}
        rev = src.strip_reversed((shot['frames'][0] + shot['frames'][1]) // 2) if sid in sids_strip else None
        for f in fl:
            p = {'f': f, 'shot': sid, 'labels': lay.get(f, [])}
            if sid in sids_strip:
                p['strip'] = {'x': src.target_x_mm(f), 'span': src.axis_span_mm(f), 'rev': rev}
            if sid == 'S12':
                p['gap'], p['lip'] = s12[f]
            if sid == 'S11':
                p['s11'] = s11w
            if sid == 'S15':
                vis = [(shot['labels'][i]['frame_in'], loop_number(shot['labels'][i]['text'])) for i, al, *_ in p['labels']]
                vis = sorted(v for v in vis if v[1])
                p['loops'] = [n for _, n in vis[::-1]]          # newest first
            plans.append(p)
    plans.sort(key=lambda p: p['f'])
    return plans, report


# ------------------------------------------------------------------ drawing
class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.shots = {s['id']: s for s in load_shots(cfg['shots_path'])['shots']}
        self.rows = screw_rows()
        self.check = screw_check()
        self.sids_strip = strip_shots(list(self.shots.values()))
        self._static, self._strip, self._s15, self._labels = {}, {}, {}, {}

    # -- static layer: title bar, footer, values, S14 legend
    def badge(self, shot, plan):
        b = shot.get('speed_badge_vi', '')
        if shot['id'] == 'S12' and plan.get('gap', 1) <= 0.001:
            return S12_BADGE_BEFORE_X10
        return '' if b.strip() in ('', '—', '-') else b

    def static_layer(self, shot, badge):
        key = (shot['id'], badge)
        if key in self._static:
            return self._static[key]
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ov.alpha_composite(self.title_bar(shot, badge), (0, 0))
        fr = footer_rect(shot)
        if fr:
            p = Panel(fr[2] - fr[0], FOOT_H, alpha=185, radius=8)
            p.text((14, FOOT_H / 2), shot['hud']['footer'], 20, fill=(222, 225, 230), anchor='lm')
            ov.alpha_composite(p.finish(), (fr[0], fr[1]))
        vr = values_rect(shot)
        if vr:
            p = Panel(vr[2] - vr[0], vr[3] - vr[1], alpha=200, radius=8)
            p.rect((0, 0, 5, p.h), fill=AMBER)
            for k, line in enumerate(values_lines(shot)):
                p.text((20, 8 + k * 30 + 15), line, 22, fill=WHITE, anchor='lm')
            ov.alpha_composite(p.finish(), (vr[0], vr[1]))
        lr = legend_rect(shot) if shot['id'] == 'S14' else None
        if lr:
            ov.alpha_composite(self.legend_panel(shot, lr), (lr[0], lr[1]))
        self._static[key] = ov
        return ov

    def title_bar(self, shot, badge):
        p = Panel(W, TITLE_H, alpha=218, radius=0)
        p.rect((0, TITLE_H - 3, W, TITLE_H), fill=AMBER + (200,))
        p.text((MARGIN, TITLE_H / 2), shot['id'], 30, True, AMBER, 'lm')
        x_right = W - MARGIN
        if badge:
            bw = Panel.tlen(badge, 22, True) + 30
            p.rect((x_right - bw, 12, x_right, TITLE_H - 14), fill=AMBER, radius=17)
            p.text((x_right - bw / 2, TITLE_H / 2 - 1), badge, 22, True, (20, 18, 10), 'mm')
            x_right -= bw + 12
        flag = FLAG.get(shot['id']) if 'minh họa' not in (shot.get('speed_badge_vi') or '') else None
        if flag:
            fw = Panel.tlen(flag, 21) + 28
            p.rect((x_right - fw, 12, x_right, TITLE_H - 14), fill=(38, 42, 52), outline=(200, 205, 215), width=1.5, radius=17)
            p.text((x_right - fw / 2, TITLE_H / 2 - 1), flag, 21, False, (235, 238, 242), 'mm')
            x_right -= fw + 12
        tx = MARGIN + 74
        avail = x_right - tx - 16
        title, size = shot['title_vi'], 30
        while size > 22 and Panel.tlen(title, size, True) > avail:
            size -= 1
        while Panel.tlen(title, size, True) > avail and len(title) > 4:
            title = title[:-2].rstrip() + '…'
        p.text((tx, TITLE_H / 2), title, size, True, WHITE, 'lm')
        return p.finish()

    def legend_panel(self, shot, lr):
        items = legend_items(shot)
        p = Panel(lr[2] - lr[0], lr[3] - lr[1], alpha=205, radius=8)
        p.text((16, 12), LEGEND_TITLE, 19, True, WHITE)
        for k, (name, col, style) in enumerate(items):
            cx, cy = 16 + (k % 2) * 272, 50 + (k // 2) * 30
            seg = [(cx, cy + 9), (cx + 50, cy + 9)]
            if style == 'solid':
                p.line(seg, col, 5)
            elif style == 'dashed':
                dashed(p, seg, col, 4, 9, 6)
            elif style == 'dotted':
                dashed(p, seg, col, 4, 3, 5)
            elif style == 'dashdot':
                dashed(p, seg, col, 4, 12, 5)
                p.ellipse((cx + 30, cy + 7, cx + 34, cy + 11), fill=col)
            else:  # solid / dashed
                p.line([(cx, cy + 5), (cx + 50, cy + 5)], col, 4)
                dashed(p, [(cx, cy + 14), (cx + 50, cy + 14)], col, 4, 8, 5)
            p.text((cx + 62, cy + 9), name, 19, fill=WHITE, anchor='lm')
        return p.finish()

    # -- labels
    def label_image(self, sid, i, text):
        key = (sid, i, text)
        if key not in self._labels:
            lines, w, h = label_box_size(text)
            p = Panel(w, h, bg=LABEL_BG, alpha=242, radius=7, border=(0, 0, 0, 70))
            p.rect((0, 0, LABEL_ACCENT, h), fill=AMBER)
            for k, line in enumerate(lines):
                p.text((LABEL_ACCENT + LABEL_PADX, LABEL_PADY - 1 + k * LABEL_LINE), line, LABEL_SIZE, fill=LABEL_TXT)
            self._labels[key] = p.finish()
        return self._labels[key]

    def leader_tile(self, rect, anchor, occluded, ss=3):
        q = nearest_on_rect(anchor, rect)
        x0 = int(min(q[0], anchor[0]) - 12)
        y0 = int(min(q[1], anchor[1]) - 12)
        x1 = int(max(q[0], anchor[0]) + 13)
        y1 = int(max(q[1], anchor[1]) + 13)
        t = Image.new('RGBA', ((x1 - x0) * ss, (y1 - y0) * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(t)
        a = ((anchor[0] - x0) * ss, (anchor[1] - y0) * ss)
        b = ((q[0] - x0) * ss, (q[1] - y0) * ss)
        d.line([b, a], fill=(255, 255, 255, 235), width=6 * ss)
        if occluded:
            L = math.dist(a, b)
            n = max(1, int(L // (12 * ss)))
            for k in range(n):
                t0, t1 = k / n, (k + 0.55) / n
                d.line([(b[0] + (a[0] - b[0]) * t0, b[1] + (a[1] - b[1]) * t0),
                        (b[0] + (a[0] - b[0]) * t1, b[1] + (a[1] - b[1]) * t1)], fill=(25, 25, 28, 255), width=2 * ss)
        else:
            d.line([b, a], fill=(25, 25, 28, 255), width=2 * ss)
        r = 7 * ss
        d.ellipse([a[0] - r - 2 * ss, a[1] - r - 2 * ss, a[0] + r + 2 * ss, a[1] + r + 2 * ss], fill=(25, 25, 28, 200))
        if occluded:
            d.ellipse([a[0] - r, a[1] - r, a[0] + r, a[1] + r], fill=(25, 25, 28, 255), outline=(255, 255, 255, 255), width=2 * ss)
        else:
            d.ellipse([a[0] - r, a[1] - r, a[0] + r, a[1] + r], fill=(255, 255, 255, 255))
            d.ellipse([a[0] - 2.5 * ss, a[1] - 2.5 * ss, a[0] + 2.5 * ss, a[1] + 2.5 * ss], fill=AMBER + (255,))
        return t.reduce(ss), (x0, y0)

    # -- screw strip
    def strip_base(self, sid, rev):
        key = (sid, rev)
        if key in self._strip:
            return self._strip[key]
        x0, y0, x1, y1 = STRIP_RECT
        p = Panel(x1 - x0, y1 - y0, alpha=238, radius=10)
        px0, px1 = 16, p.w - 16
        L = 5746.0

        def X(mm):
            t = mm / L
            return px1 - t * (px1 - px0) if rev else px0 + t * (px1 - px0)
        ybar, hbar = 58, 34
        yg0, yg1 = 98, 172
        # title row + legend
        p.text((16, 18), STRIP_TXT['title'], 18, True, WHITE, 'lm')
        lx = p.w - 16
        items = [('view', None), ('vent', PURPLE), ('p', BLUE), ('fill', MELT)]
        for key_, col in items:
            t = STRIP_TXT[key_]
            tw = Panel.tlen(t, 16)
            lx -= tw
            p.text((lx, 18), t, 16, fill=GREY, anchor='lm')
            lx -= 30
            if key_ == 'p':
                p.line([(lx, 18), (lx + 24, 18)], BLUE, 3)
            elif key_ == 'view':
                p.rect((lx, 10, lx + 24, 26), outline=(255, 255, 255), width=2)
            else:
                p.rect((lx, 11, lx + 24, 25), fill=col + (200,))
            lx -= 22
        # flow arrow in the title row
        fx = Panel.tlen(STRIP_TXT['title'], 18, True) + 44
        a_, b_ = (fx + 110, 18), (fx, 18)
        if not rev:
            a_, b_ = b_, a_
        p.line([a_, b_], MELT, 3)
        arrowhead(p, a_, b_, MELT, 12)
        p.text((fx + 122, 18), STRIP_TXT['flow'], 16, True, MELT, 'lm')
        # zones
        for za, zb, name in ZONES:
            cx = (X(za) + X(zb)) / 2
            p.text((cx, 46), name, 16, True, (215, 220, 228), 'mm')
            p.line([(X(za), 38), (X(za), 54)], (90, 96, 106), 1)
        # vent windows (behind the bar and graph)
        for (va, vb), key_ in ((self.check['vent1_mm'], 'vent1'), (self.check['vent2_mm'], 'vent2')):
            xa, xb = sorted((X(va), X(vb)))
            p.rect((xa, ybar - 4, xb, yg1), fill=PURPLE + (110,))
            p.text(((xa + xb) / 2, yg0 + 9), STRIP_TXT[key_], 15, True, (236, 228, 255), 'mm')
        # elements
        for r in self.rows:
            xa, xb = sorted((X(r['x_start_mm']), X(r['x_end_mm'])))
            typ = r['type']
            col = {'SE': (92, 104, 122), 'KB': (58, 138, 88), 'LH': (204, 58, 58), 'TIP': (128, 136, 148)}[typ]
            if typ == 'KB' and 'neutral' in (r.get('hand') or ''):
                col = (34, 104, 64)
            p.rect((xa, ybar, xb, ybar + hbar), fill=col)
            if typ in ('SE', 'LH'):
                pitch = (r.get('pitch_mm') or 169) * (px1 - px0) / L / 2
                step = max(6.0, pitch)
                slant = 10 if (typ == 'SE') ^ rev else -10
                xx = xa - 12
                while xx < xb + 12:
                    seg = [(xx, ybar + hbar), (xx + slant, ybar)]
                    if xa <= min(seg[0][0], seg[1][0]) and max(seg[0][0], seg[1][0]) <= xb:
                        p.line(seg, (190, 198, 212) if typ == 'SE' else (255, 210, 210), 1.5)
                    xx += step
            elif typ == 'KB':
                n = r.get('kb_discs') or 5
                for k in range(n):
                    xd = xa + (k + 0.5) * (xb - xa) / n
                    off = 5 if k % 2 else -5
                    p.rect((xd - 2, ybar + 4 + off, xd + 2, ybar + hbar - 4 + off), fill=(200, 236, 210))
            p.line([(xa, ybar), (xa, ybar + hbar)], (16, 18, 22), 1)
        p.rect((px0, ybar, px1, ybar + hbar), outline=(16, 18, 22), width=1)
        # graph: fill + pressure
        gh = yg1 - yg0
        p.line([(px0, yg1), (px1, yg1)], (90, 96, 106), 1)
        p.line([(px0, yg0), (px1, yg0)], (60, 64, 72), 1)
        pts = []
        for r in self.rows:
            for mm in (r['x_start_mm'], r['x_end_mm']):
                pts.append((X(mm), yg1 - gh * r['fill_degree_schematic']))
        p.poly([(X(0), yg1)] + pts + [(X(L), yg1)], fill=MELT + (165,))
        p.line(pts, (255, 170, 60), 2)
        pp = [(X(mm), yg1 - gh * bar / 110.0) for mm, bar in PRESSURE]
        p.line(pp, (10, 14, 24), 7)
        p.line(pp, BLUE, 3.5)
        tipx = X(L)
        tw = Panel.tlen(STRIP_TXT['p1'], 15, True)
        bx = tipx + 10 if rev else tipx - 10 - tw - 12
        p.rect((bx, yg0 + 3, bx + tw + 12, yg0 + 23), fill=(10, 14, 24, 235), radius=4)
        p.text((bx + 6, yg0 + 13), STRIP_TXT['p1'], 15, True, (150, 205, 255), 'lm')
        p.text((X(0) + (-6 if rev else 6), yg0 + 10), '100 %', 13, fill=GREY, anchor='rm' if rev else 'lm')
        # barrels
        for ba, bb, name in BARRELS:
            xa, xb = sorted((X(ba), X(bb)))
            p.rect((xa, yg1 + 6, xb, yg1 + 26), outline=(110, 116, 126), width=1)
            p.text(((xa + xb) / 2, yg1 + 16), name, 15, True, (200, 204, 212), 'mm')
        p.text((X(0) + (-4 if rev else 4), yg1 + 16), 'X 0', 13, fill=GREY, anchor='rm' if rev else 'lm')
        p.text((X(L) + (4 if rev else -4), yg1 + 16), 'X 5 746', 13, fill=GREY, anchor='lm' if rev else 'rm')
        self._strip[key] = (p, X, (ybar, hbar, yg0, yg1))
        return self._strip[key]

    def strip_panel(self, sid, sp):
        base, X, (ybar, hbar, yg0, yg1) = self.strip_base(sid, sp['rev'])
        p = base.clone()
        if sp.get('span'):
            xa, xb = sorted((X(sp['span'][0]), X(sp['span'][1])))
            for ra, rb in ((16, xa), (xb, p.w - 16)):
                if rb > ra:
                    p.rect((ra, ybar - 4, rb, yg1), fill=(8, 10, 14, 120))
            p.rect((xa, ybar - 5, xb, yg1 + 1), outline=(255, 255, 255, 220), width=2)
        if sp.get('x') is not None:
            x = X(min(max(sp['x'], 0), 5746))
            p.line([(x, ybar), (x, yg1)], (10, 12, 16), 6)
            p.line([(x, ybar), (x, yg1)], AMBER, 3)
            p.poly([(x - 10, ybar - 1), (x + 10, ybar - 1), (x, ybar + 13)], fill=AMBER, outline=(10, 12, 16))
        return p.finish()

    # -- S15 block diagram
    S15_BLOCKS = {'liw': 'Cân LIW', 'motor': 'Động cơ vít', 'filter': 'Lọc (PDI)', 'p3': 'P3', 'pump': 'Bơm (biến tần)',
                  'bolts': 'Bu-lông nhiệt', 'rolls': 'Trục cán', 'gauge': 'Đầu đo', 'plc': 'PLC', 'tic': 'Nhiệt (TIC)', 'sto': 'STO'}
    S15_CHAIN = ['liw', 'motor', 'filter', 'p3', 'pump', 'bolts', 'rolls', 'gauge']
    S15_EDGES = {1: [('plc', 'pump'), ('pump', 'bolts', 'proc')],
                 2: [('p3', 'plc'), ('plc', 'liw'), ('plc', 'motor')],
                 3: [('gauge', 'plc'), ('plc', 'rolls')],
                 4: [('gauge', 'plc'), ('plc', 'bolts')],
                 5: [('filter', 'plc'), ('plc', 'filter')],
                 6: [('tic', 'plc'), ('plc', 'tic'), ('tic', 'motor')],
                 7: [('motor', 'sto'), ('pump', 'sto'), ('sto', 'motor'), ('sto', 'pump'), ('sto', 'liw')]}

    def s15_geom(self, shot):
        names = list(shot.get('hud', {}).get('block_diagram', []))
        disp = dict(self.S15_BLOCKS)
        for k, v in self.S15_BLOCKS.items():         # take display names from shots.json when they match
            for n in names:
                if n.split(' ')[0].lower() == v.split(' ')[0].lower() and (n[:3] == v[:3]):
                    disp[k] = n
        g = {}
        for k, key in enumerate(self.S15_CHAIN):
            y = 96 + k * 64
            g[key] = (18, y, 238, y + 44)
        g['tic'] = (352, 96, 578, 140)
        g['plc'] = (352, 224, 578, 460)
        g['sto'] = (352, 544, 578, 588)
        return g, disp

    def s15_edge_pts(self, g, a, b, kind=None, both=False):
        """Polyline from block a to block b (panel coordinates)."""
        def right(k):
            r = g[k]
            return (r[2], (r[1] + r[3]) / 2)

        def left(k):
            r = g[k]
            return (r[0], (r[1] + r[3]) / 2)
        if kind == 'proc':
            return [(40, g[a][3]), (40, g[b][1])]
        plc = g['plc']
        if {a, b} == {'tic', 'plc'}:
            x = (g['tic'][0] + g['tic'][2]) / 2
            ends = {'tic': (x, g['tic'][3]), 'plc': (x, plc[1])}
        elif 'plc' in (a, b):
            blk = b if a == 'plc' else a
            k = self.S15_CHAIN.index(blk)
            ends = {blk: right(blk), 'plc': (plc[0], plc[1] + 16 + k * (plc[3] - plc[1] - 32) / 7)}
        else:                                           # tic / sto <-> process block
            ctl = a if a in ('tic', 'sto') else b
            other = b if ctl == a else a
            ends = {other: right(other), ctl: left(ctl)}
        pts = [ends[a], ends[b]]
        if both:                                        # two directions: offset each to its own side
            (x0, y0), (x1, y1) = pts
            L = math.hypot(x1 - x0, y1 - y0) or 1.0
            nx, ny = -(y1 - y0) / L * 4, (x1 - x0) / L * 4
            pts = [(x + nx, y + ny) for x, y in pts]
        return pts

    @staticmethod
    def _center(r):
        return ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)

    def s15_block(self, p, r, name, state):
        if state == 'on':
            fill, outl, tc, bold = (255, 208, 120), AMBER, (20, 18, 10), True
        elif state == 'second':
            fill, outl, tc, bold = (86, 72, 40), AMBER, WHITE, False
        else:
            fill, outl, tc, bold = (50, 54, 62), (104, 110, 120), (205, 209, 215), False
        p.rect(r, fill=fill, outline=outl, width=2 if state != 'off' else 1, radius=7)
        p.text(((r[0] + r[2]) / 2, (r[1] + r[3]) / 2), name, 24 if name == 'PLC' else 19, bold or name == 'PLC', tc, 'mm')

    def s15_base(self, shot):
        if shot['id'] in self._s15:
            return self._s15[shot['id']]
        x0, y0, x1, y1 = S15_RECT
        p = Panel(x1 - x0, y1 - y0, alpha=215, radius=10)
        g, disp = self.s15_geom(shot)
        p.text((18, 16), S15_TXT['title'], 22, True, WHITE)
        p.text((18, 50), S15_TXT['sub'], 16, fill=GREY)
        for k in range(len(self.S15_CHAIN) - 1):          # process chain
            a, b = self.S15_CHAIN[k], self.S15_CHAIN[k + 1]
            col = (139, 90, 43) if k == 0 else (208, 52, 44)
            pts = self.s15_edge_pts(g, a, b, 'proc')
            p.line(pts, col, 3)
            arrowhead(p, pts[0], pts[1], col, 10)
        for key in self.S15_CHAIN:                        # dim spokes
            dashed(p, self.s15_edge_pts(g, key, 'plc'), (96, 102, 112), 2, 7, 6)
        dashed(p, self.s15_edge_pts(g, 'tic', 'plc'), (96, 102, 112), 2, 7, 6)
        for key, r in g.items():
            self.s15_block(p, r, disp[key], 'off')
        p.text((18, 624), S15_TXT['loops'], 19, True, WHITE)
        p.text((18, p.h - 26), S15_TXT['note'], 16, fill=GREY, anchor='lm')
        self._s15[shot['id']] = (p, g, disp)
        return self._s15[shot['id']]

    def s15_panel(self, shot, loops, f):
        base, g, disp = self.s15_base(shot)
        p = base.clone()
        active = loops[:2]
        for rank, n in reversed(list(enumerate(active))):
            col = AMBER if rank == 0 else (200, 150, 40)
            width = 4 if rank == 0 else 3
            edges = self.S15_EDGES.get(n, [])
            pairs = {(e[0], e[1]) for e in edges}
            for e in edges:
                a, b = e[0], e[1]
                kind = e[2] if len(e) > 2 else None
                both = (b, a) in pairs
                pts = self.s15_edge_pts(g, a, b, kind, both)
                if kind == 'proc':
                    p.line(pts, col, width + 1)
                else:
                    dashed(p, pts, col, width, 12, 7, offset=-f * 2.4)
                arrowhead(p, pts[-2], pts[-1], col, 13)
        on = set()
        for rank, n in enumerate(active):
            for e in self.S15_EDGES.get(n, []):
                for k in e[:2]:
                    if rank == 0:
                        on.add(k)
        second = set()
        if len(active) > 1:
            for e in self.S15_EDGES.get(active[1], []):
                second.update(e[:2])
        for key, r in g.items():
            st = 'on' if key in on else 'second' if key in second else None
            if st:
                self.s15_block(p, r, disp[key], st)
        for n in range(1, 8):
            y = 664 + (n - 1) * 34
            txt = f'({n}) ' + S15_LOOPS[n]
            if active and n == active[0]:
                p.rect((10, y - 15, p.w - 10, y + 15), fill=(255, 208, 120), radius=6)
                p.text((20, y), txt, 19, True, (20, 18, 10), 'lm')
            elif n in active:
                p.text((20, y), txt, 19, False, AMBER, 'lm')
            else:
                p.text((20, y), txt, 19, False, (150, 156, 166), 'lm')
        return p.finish()

    # -- S11 coat-hanger inset
    def s11_panel(self, f, win):
        x0, y0, x1, y1 = S11_RECT
        p = Panel(x1 - x0, y1 - y0, alpha=222, radius=10)
        p.text((18, 14), S11_TXT['title'], 21, True, WHITE)
        p.text((18, 44), S11_TXT['sub'], 16, fill=(214, 200, 150))
        t = (f - win[0]) / 25.0
        cx, top, lip, el, er = 300, 104, 290, 52, 548
        arm_y = 210
        p.rect((40, 86, 560, 300), outline=(120, 126, 136), width=2, radius=4)
        prog_arm = smoothstep((t - 0.2) / 1.2)
        prog_pre = smoothstep((t - 1.1) / 1.4)
        steel = (70, 76, 86)
        # empty channels
        for side in (-1, 1):
            p.poly([(cx, top + 4), (cx + side * 248, arm_y - 4), (cx + side * 248, arm_y + 6), (cx, top + 22)], fill=steel)
        p.poly([(cx, top + 22), (er, arm_y + 6), (er, lip), (el, lip), (el, arm_y + 6)], fill=(56, 60, 68))
        # preland fill (front parallel to the lip moving down)
        if prog_pre > 0:
            yf = top + 22 + (lip - top - 22) * prog_pre
            poly = [(cx, top + 22), (er, arm_y + 6), (er, lip), (el, lip), (el, arm_y + 6)]
            clipped = clip_poly_y(poly, yf)
            if len(clipped) >= 3:
                p.poly(clipped, fill=(150, 84, 30))
        # manifold fill from the inlet outward
        if prog_arm > 0:
            for side in (-1, 1):
                ex = cx + side * 248 * prog_arm
                ey = top + (arm_y - top) * prog_arm
                wtop, wbot = 18 - 10 * prog_arm, 10 - 4 * prog_arm
                p.poly([(cx, top + 4), (ex, ey - 4), (ex, ey + wbot), (cx, top + 4 + 18)], fill=(255, 172, 64),
                       outline=(255, 224, 170))
        p.ellipse((cx - 14, top - 14, cx + 14, top + 14), fill=MELT, outline=(255, 210, 150), width=2)
        p.rect((el, lip, er, lip + 8), fill=(255, 196, 90) if prog_pre >= 1 else (120, 100, 70))
        # uniform exit arrows, pulsing once the front reached the lip
        if prog_pre >= 0.999:
            ph = ((f - win[0]) % 25) / 25.0
            for k in range(9):
                x = el + 20 + k * (er - el - 40) / 8
                ya, yb = lip + 14, lip + 40 + 6 * math.sin(2 * math.pi * ph)
                p.line([(x, ya), (x, yb)], (255, 200, 110), 3)
                arrowhead(p, (x, ya), (x, yb), (255, 200, 110), 9)
        # dimensions: long preland at the centre, short at the edge
        for (xa, ya, yb, txt, anc) in ((cx + 22, top + 26, lip - 4, S11_TXT['long'], 'lm'),
                                        (er - 18, arm_y + 10, lip - 4, S11_TXT['short'], 'rm')):
            p.line([(xa, ya), (xa, yb)], (230, 232, 236), 1.5)
            arrowhead(p, (xa, yb), (xa, ya), (230, 232, 236), 8)
            arrowhead(p, (xa, ya), (xa, yb), (230, 232, 236), 8)
            p.text((xa + (8 if anc == 'lm' else -8), (ya + yb) / 2), txt, 15, True, WHITE, anc)
        p.text((cx + 22, top - 2), S11_TXT['inlet'], 15, fill=WHITE, anchor='lm')
        p.text((62, 132), S11_TXT['manifold'], 15, True, (255, 214, 150), 'lm')
        p.text((cx, p.h - 12), S11_TXT['lip'], 15, True, (255, 214, 150), 'mb')
        return p.finish(ramp_alpha(f, win[0], win[1]))

    # -- S12 true-value gauge
    def s12_panel(self, gap, lip):
        x0, y0, x1, y1 = S12_RECT
        p = Panel(x1 - x0, y1 - y0, alpha=226, radius=10, border=(255, 184, 28, 160))
        v = 1.0 - 0.15 * lip
        p.text((18, 22), S12_TXT['title'], 22, True, WHITE, 'lm')
        heat = (int(90 + 165 * lip), int(96 - 50 * lip), int(106 - 70 * lip))
        p.ellipse((p.w - 34, 12, p.w - 14, 32), fill=heat, outline=(220, 220, 220), width=1)
        if lip > 0.05:
            p.text((p.w - 42, 22), S12_TXT['hot'], 15, fill=(255, 150, 120), anchor='rm')
        val = f'{v:.2f}'.replace('.', ',')
        p.text((18, 76), val, 60, True, WHITE, 'lm')
        vw = Panel.tlen(val, 60, True)
        p.text((26 + vw, 90), 'mm', 26, False, GREY, 'lm')
        dv = v - 1.0
        if abs(dv) >= 0.005:
            p.text((p.w - 18, 82), f'{dv:+.2f}'.replace('.', ',').replace('-', '−'), 30, True, AMBER, 'rm')
        else:
            p.text((p.w - 18, 82), S12_TXT['nominal'], 20, False, GREY, 'rm')
        sx0, sx1, sy = 30, p.w - 30, 132
        p.line([(sx0, sy), (sx1, sy)], (150, 156, 166), 3)
        for val_, lab in ((0.85, '0,85'), (1.0, '1,00'), (1.15, '1,15')):
            x = sx0 + (val_ - 0.85) / 0.30 * (sx1 - sx0)
            p.line([(x, sy - 8), (x, sy + 8)], (200, 204, 212), 2)
            p.text((x, sy + 12), lab, 15, False, GREY, 'mt')
        x = sx0 + (v - 0.85) / 0.30 * (sx1 - sx0)
        p.poly([(x - 9, sy - 20), (x + 9, sy - 20), (x, sy - 3)], fill=AMBER)
        p.text((18, p.h - 14), S12_TXT['note'], 15, False, (200, 204, 212), 'lm')
        return p.finish(min(1.0, gap / 0.25))

    # -- S16 summary card
    def s16_panel(self, shot, f):
        x0, y0, x1, y1 = S16_RECT
        p = Panel(x1 - x0, y1 - y0, alpha=222, radius=14)
        a = shot['frames'][0]
        title = shot['hud'].get('title', '')
        vals = shot['hud'].get('values', [])
        p.rect((0, 0, p.w, 6), fill=AMBER)
        p.text((p.w / 2, 58), title, 38, True, WHITE, 'mm')
        for k, line in enumerate(vals):
            al = smoothstep((f - (a + 10 + 12 * k)) / 10.0)
            if al <= 0:
                continue
            y = 140 + k * 72
            num, _, rest = line.partition('. ')
            col = tuple(int(c * al + 30 * (1 - al)) for c in AMBER)
            tc = tuple(int(c * al + 30 * (1 - al)) for c in WHITE)
            p.ellipse((56, y - 24, 104, y + 24), fill=col)
            p.text((80, y), num, 28, True, (20, 18, 10), 'mm')
            p.text((128, y), rest if rest else line, 32, False, tc, 'lm')
        return p.finish(ramp_alpha(f, a, shot['frames'][1] + 1000, FADE))

    # -- one frame
    def overlay(self, plan):
        shot = self.shots[plan['shot']]
        sid, f = shot['id'], plan['f']
        ov = self.static_layer(shot, self.badge(shot, plan)).copy()
        if 'strip' in plan:
            ov.alpha_composite(self.strip_panel(sid, plan['strip']), STRIP_RECT[:2])
        if sid == 'S15':
            ov.alpha_composite(self.s15_panel(shot, plan.get('loops', []), f), S15_RECT[:2])
        if sid == 'S11' and plan.get('s11') and plan['s11'][0] <= f <= plan['s11'][1]:
            ov.alpha_composite(self.s11_panel(f, plan['s11']), S11_RECT[:2])
        if sid == 'S12' and plan.get('gap', 0) > 0.001:
            ov.alpha_composite(self.s12_panel(plan['gap'], plan['lip']), S12_RECT[:2])
        if sid == 'S16':
            ov.alpha_composite(self.s16_panel(shot, f), S16_RECT[:2])
        labs = plan['labels']
        for i, al, rect, anchor, occ in labs:        # leaders under every box
            if anchor:
                tile, pos = self.leader_tile(rect, anchor, occ)
                ov.alpha_composite(fade(tile, al), (max(0, pos[0]), max(0, pos[1])),
                                   (max(0, -pos[0]), max(0, -pos[1])))
        for i, al, rect, anchor, occ in labs:
            img = self.label_image(sid, i, shot['labels'][i]['text'])
            ov.alpha_composite(fade(img, al), (int(round(rect[0])), int(round(rect[1]))))
        return ov


def clip_poly_y(poly, ymax):
    """Keep the part of a polygon with y <= ymax (Sutherland-Hodgman, one edge)."""
    out = []
    for k in range(len(poly)):
        a, b = poly[k], poly[(k + 1) % len(poly)]
        ina, inb = a[1] <= ymax, b[1] <= ymax
        if ina:
            out.append(a)
        if ina != inb:
            t = (ymax - a[1]) / (b[1] - a[1])
            out.append((a[0] + (b[0] - a[0]) * t, ymax))
    return out


# ------------------------------------------------------------------ workers
_R = None


def _init(cfg):
    global _R
    _R = Renderer(cfg)


def _work(plan):
    cfg = _R.cfg
    f = plan['f']
    out = os.path.join(cfg['out_dir'], f'{f:04d}.png')
    ov = _R.overlay(plan)
    tmp = out + '.tmp.png'
    if cfg['mode'] == 'overlay':
        ov.save(tmp, compress_level=cfg['png_level'])
    else:
        src = os.path.join(cfg['frames_dir'], f'{f:04d}.png')
        if not os.path.exists(src):
            if cfg['missing'] == 'skip':
                return f, 'missing'
            base = Image.new('RGB', (W, H), (60, 62, 66))
        else:
            base = Image.open(src).convert('RGB')
        if base.size != (W, H):
            ov = ov.resize(base.size, Image.LANCZOS)
        base.paste(ov, (0, 0), ov)
        base.save(tmp, compress_level=cfg['png_level'])
    os.replace(tmp, out)
    return f, 'ok'


def write_report(path, report, results, args, t_layout, t_draw):
    lines = ['# Overlay report (generated by overlay.py)', '',
             f'- mode: {args.mode}; out: `{os.path.relpath(args.out, os.getcwd())}`; frames requested: {results["requested"]}; '
             f'drawn: {results["ok"]}; skipped (existing): {results["skipped"]}; missing input: {len(results["missing"])}',
             f'- layout {t_layout:.1f} s, drawing {t_draw:.1f} s with {args.jobs} processes', '']
    if results['missing']:
        m = results['missing']
        lines += [f'- missing input frames: {m[0]}…{m[-1]} ({len(m)})', '']
    lines += ['## Warnings', ''] + ([f'- {w}' for w in report['warn']] or ['- none']) + ['']
    flagged = [(sid, i, st, d) for sid, d in report['shots'].items() for i, st in d['stats'].items()
               if st['frames'] and st['off'] / st['frames'] > 0.25]
    lines += ['## Labels without a leader for more than 25 % of their time', '',
              'The text still shows, but nothing points at the part. Fix the camera (or the anchor point) in Blender.', '']
    lines += [f"- {sid} L{i}: {st['off']}/{st['frames']} frames ({100 * st['off'] / st['frames']:.0f} %), "
              f"{st['hud']} under a HUD panel – {d['labels'][i]['text']}" for sid, i, st, d in flagged] or ['- none']
    lines += ['']
    lines += ['## Labels (frames of the shot drawn so far)', '',
              '| shot | anchors | label | frames on screen | no leader (anchor off-screen or under HUD) | of which under HUD | anchor occluded | box overlap | text |', '|---|---|---|---|---|---|---|---|---|']
    for sid, d in report['shots'].items():
        for i, st in d['stats'].items():
            if st['frames'] == 0:
                continue
            lines.append(f"| {sid} | {d['source']} | L{i} | {st['frames']} | {st['off']} | {st['hud']} | {st['occ']} | {st['overlap']} | {d['labels'][i]['text']} |")
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--shots', default=None, help='shots.json (default anim/shots.json)')
    ap.add_argument('--anchors', default=os.path.join(RENDER, 'anchors'))
    ap.add_argument('--frames', default=os.path.join(RENDER, 'frames'), help='Blender frames (####.png), --mode final')
    ap.add_argument('--out', default=None, help='default anim/render/overlay or anim/render/final')
    ap.add_argument('--mode', choices=('overlay', 'final'), default='overlay')
    ap.add_argument('--range', default=None, help="frames, e.g. '901-1350,3400-3500' (default: all)")
    ap.add_argument('--shot', default=None, help='comma list of shot ids, e.g. S04,S12')
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument('--force', action='store_true', help='redraw existing outputs')
    ap.add_argument('--png-level', type=int, default=None, help='PNG compress level (default 3 overlay, 1 final)')
    ap.add_argument('--missing', choices=('skip', 'grey'), default='skip', help='final mode: missing input frame')
    ap.add_argument('--no-sim', action='store_true', help='fail instead of simulating anchors when a file is missing')
    ap.add_argument('--report', default=os.path.join(RENDER, 'overlay_report.md'))
    ap.add_argument('--layout-only', action='store_true', help='compute layout + report, draw nothing')
    args = ap.parse_args()
    data = load_shots(args.shots) if args.shots else load_shots()
    shots = data['shots']
    args.out = args.out or os.path.join(RENDER, 'overlay' if args.mode == 'overlay' else 'final')
    png_level = args.png_level if args.png_level is not None else (3 if args.mode == 'overlay' else 1)
    frames = parse_ranges(args.range) if args.range else list(range(data['meta']['frame_start'], data['meta']['frame_end'] + 1))
    if args.shot:
        keep = set(args.shot.split(','))
        frames = [f for f in frames if any(s['id'] in keep and s['frames'][0] <= f <= s['frames'][1] for s in shots)]
    # font check before anything else
    texts = ' '.join([s['title_vi'] + ' ' + s.get('speed_badge_vi', '') + ' ' + ' '.join(l['text'] for l in s['labels'])
                      + ' ' + ' '.join(s.get('hud', {}).get('values', [])) + ' ' + s.get('hud', {}).get('title', '')
                      + ' ' + ' '.join(s.get('hud', {}).get('block_diagram', [])) for s in shots] + all_fixed_strings())
    for bold in (False, True):
        miss = missing_glyphs(texts, bold)
        if miss:
            sys.exit(f"font lacks glyphs ({'bold' if bold else 'regular'}): {''.join(miss)} – set ZE_FONT/ZE_FONT_BOLD")
    if not args.layout_only:
        os.makedirs(args.out, exist_ok=True)
    t0 = time.time()
    plans, report = build_plans(shots, frames, args.anchors, allow_sim=not args.no_sim)
    t_layout = time.time() - t0
    todo = [p for p in plans if args.force or not os.path.exists(os.path.join(args.out, f"{p['f']:04d}.png"))]
    if args.layout_only:
        todo = []
    results = {'requested': len(plans), 'skipped': len(plans) - len(todo), 'ok': 0, 'missing': []}
    print(f'{len(plans)} frames, {len(todo)} to draw, layout {t_layout:.1f} s; anchors: '
          + ', '.join(f"{k}={v['source']}" for k, v in report['shots'].items()))
    for w in report['warn']:
        print('  warn', w)
    cfg = {'shots_path': args.shots, 'out_dir': args.out, 'frames_dir': args.frames, 'mode': args.mode,
           'png_level': png_level, 'missing': args.missing}
    if cfg['shots_path'] is None:
        from common import SHOTS_JSON
        cfg['shots_path'] = SHOTS_JSON
    t1 = time.time()
    if todo:
        if args.jobs > 1 and len(todo) > 8:
            with Pool(args.jobs, initializer=_init, initargs=(cfg,)) as pool:
                for n, (f, st) in enumerate(pool.imap_unordered(_work, todo, chunksize=4), 1):
                    if st == 'ok':
                        results['ok'] += 1
                    else:
                        results['missing'].append(f)
                    if n % 200 == 0:
                        print(f'  {n}/{len(todo)}  {n / (time.time() - t1):.1f} fps')
        else:
            _init(cfg)
            for p in todo:
                f, st = _work(p)
                if st == 'ok':
                    results['ok'] += 1
                else:
                    results['missing'].append(f)
    results['missing'].sort()
    t_draw = time.time() - t1
    write_report(args.report, report, results, args, t_layout, t_draw)
    print(f"drawn {results['ok']}, skipped {results['skipped']}, missing input {len(results['missing'])}, "
          f"{t_draw:.1f} s ({results['ok'] / max(t_draw, 1e-6):.1f} fps) -> {args.out}; report {args.report}")


if __name__ == '__main__':
    main()
