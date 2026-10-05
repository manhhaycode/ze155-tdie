"""Shared helpers for the ZE 155 post-production pipeline (overlay, timing check, test inputs).

Pure Python + Pillow + numpy. Never imports bpy; nothing here talks to Blender.
"""
import json
import math
import os
from functools import lru_cache

import numpy as np
from PIL import ImageFont

POST = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.dirname(POST)
ROOT = os.path.dirname(ANIM)
SHOTS_JSON = os.path.join(ANIM, 'shots.json')
PARTS_JSON = os.path.join(ANIM, 'interior_parts.json')
RENDER = os.path.join(ANIM, 'render')

W, H = 1920, 1080          # reference frame: anchors and all drawing use this space
FPS = 25
FADE = 8                   # label fade in/out, frames (0.32 s); same as shots.json label_rule
MIN_FRAMES = 75            # 3 s
FRAMES_PER_WORD = 10       # 0.4 s per word

# ------------------------------------------------------------------ fonts
FONT_CANDIDATES = {
    False: ['/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf',
            '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
    True: ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf',
           '/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
}


def font_path(bold=False):
    env = os.environ.get('ZE_FONT_BOLD' if bold else 'ZE_FONT')
    for p in ([env] if env else []) + FONT_CANDIDATES[bold]:
        if p and os.path.exists(p):
            return p
    raise FileNotFoundError('No TTF font with Vietnamese glyphs found; set ZE_FONT / ZE_FONT_BOLD')


@lru_cache(maxsize=None)
def font(size, bold=False):
    return ImageFont.truetype(font_path(bold), size)


def missing_glyphs(text, bold=False):
    """Characters of `text` the font renders as .notdef (empty box)."""
    from PIL import Image, ImageDraw
    f = font(40, bold)

    def raster(c):
        im = Image.new('L', (80, 80))
        ImageDraw.Draw(im).text((10, 10), c, font=f, fill=255)
        return im.tobytes()
    notdef = {raster(chr(0xE000)), raster(chr(0x0378))}
    return sorted({c for c in text if not c.isspace() and ord(c) > 127 and raster(c) in notdef})


NBSP = '\u00a0'
UNITS = {'mm', 'm', 'kW', 'kNm', 'bar', 'mbar', '°C', 'kg/h', 'v/ph', '%', '%)', 'm/min', 'µm', 'cm²', 'cm³/vòng', 'D',
         't/h', 'dl/g', 'ppm', 'ppm)', 's', 'kWh/kg', 'mm)', 'bar)', 'kNm)', 'mm*', 'x', '×'}


def glue(text):
    """Join tokens that must not be split across lines with a no-break space: thousands groups ('1 500'),
    number + unit ('50 mbar*'), '≈ 50', and a '·' separator stays at the end of the line before it."""
    toks = text.split(' ')
    out = []
    for t in toks:
        if out:
            prev = out[-1]
            pd = prev.replace(NBSP, ' ').split(' ')[-1]
            core = t.rstrip('*,:;)').rstrip('*')
            join = (pd.isdigit() and len(t) >= 3 and t[:3].isdigit()) \
                or (any(c.isdigit() for c in pd) and (core in UNITS or t.rstrip(',:;') in UNITS)) \
                or (pd in ('≈', '~', '<', '>', '≥', '≤', '±', 'Ø') and t[:1].isdigit()) \
                or t == '·'
            if join:
                out[-1] = prev + NBSP + t
                continue
        out.append(t)
    return ' '.join(out)


def wrap(text, fnt, maxw):
    """Greedy word wrap with glue(); returns list of lines (no-break spaces turned back into spaces)."""
    lines, cur = [], ''
    for word in glue(text).split(' '):
        t = (cur + ' ' + word).strip()
        if cur and fnt.getlength(t) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = t
    if cur:
        lines.append(cur)
    return [l.replace(NBSP, ' ') for l in lines]


# ------------------------------------------------------------------ data
@lru_cache(maxsize=None)
def _load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def load_shots(path=SHOTS_JSON):
    return _load(path)


def screw_rows(path=PARTS_JSON):
    return _load(path)['screw_elements']['rows']


def screw_check(path=PARTS_JSON):
    return _load(path)['screw_elements']['check']


def shot_of_frame(shots, f):
    for s in shots:
        if s['frames'][0] <= f <= s['frames'][1]:
            return s
    return None


def words(text):
    return len(text.split())


def label_min_frames(text):
    return max(MIN_FRAMES, FRAMES_PER_WORD * words(text))


def ramp_alpha(f, f_in, f_out, fade=FADE):
    """Visible on f_in..f_out inclusive (= f_out - f_in + 1 frames, the convention shots.json was scheduled with).
    Linear fade over `fade` frames at both ends."""
    if f < f_in or f > f_out:
        return 0.0
    return max(0.0, min(1.0, (f - f_in + 1) / fade, (f_out - f + 1) / fade))


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def parse_ranges(spec):
    """'901-1000,3400-3410,5000' -> sorted list of frames."""
    out = set()
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-')
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return sorted(out)


# ------------------------------------------------------------------ camera simulation (fallback + test)
def _pchip_slopes(xs, ys):
    """Fritsch-Carlson monotone cubic slopes, zero at both ends (close to Blender auto-clamped Bezier)."""
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [0.0] * n
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1 = 2 * (xs[i + 1] - xs[i]) + (xs[i] - xs[i - 1])
            w2 = (xs[i + 1] - xs[i]) + 2 * (xs[i] - xs[i - 1])
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    return m


def interp_keys(keys, f, field):
    """Interpolate a key field (scalar or vector) at frame f with monotone cubic Hermite per component."""
    xs = [k['frame'] for k in keys]
    vals = [k[field] for k in keys]
    vec = isinstance(vals[0], (list, tuple))
    comps = list(zip(*vals)) if vec else [vals]
    out = []
    for ys in comps:
        if len(xs) == 1 or f <= xs[0]:
            out.append(ys[0])
            continue
        if f >= xs[-1]:
            out.append(ys[-1])
            continue
        m = _pchip_slopes(xs, list(ys))
        i = max(j for j in range(len(xs) - 1) if xs[j] <= f)
        h = xs[i + 1] - xs[i]
        t = (f - xs[i]) / h
        h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
        h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
        out.append(h00 * ys[i] + h10 * h * m[i] + h01 * ys[i + 1] + h11 * h * m[i + 1])
    return out if vec else out[0]


def look_at_matrix(loc, target, up=(0.0, 0.0, 1.0)):
    """Camera-to-world 4x4 like a Blender Track-To (track -Z, up Y)."""
    loc, target, up = np.array(loc, float), np.array(target, float), np.array(up, float)
    z = loc - target
    z /= np.linalg.norm(z)
    x = np.cross(up, z)
    if np.linalg.norm(x) < 1e-9:
        x = np.array([1.0, 0, 0])
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, loc
    return m


def simulated_camera(shot, f):
    """Camera state at frame f from shots.json keys (approximation of the Blender fcurves)."""
    cams = shot['cameras']
    cam = cams[0]
    for c in cams:
        if 'frames' in c and c['frames'][0] <= f <= c['frames'][1]:
            cam = c
    keys = cam['keys']
    loc = interp_keys(keys, f, 'loc')
    tgt = interp_keys(keys, f, 'target')
    lens = interp_keys(keys, f, 'lens_mm')
    return {'name': cam['name'], 'type': cam.get('type', 'PERSP'), 'matrix_world': look_at_matrix(loc, tgt),
            'lens_mm': lens, 'sensor_width_mm': 36.0, 'sensor_fit': 'AUTO',
            'ortho_scale': cam.get('ortho_scale_m', 1.0), 'shift': (0.0, 0.0), 'target_m': tgt}


def project(cam, point, w=W, h=H):
    """World point -> (x_px, y_px, in_front) in a w x h frame, same maths as world_to_camera_view.
    `cam` needs matrix_world (4x4 camera-to-world), lens_mm, sensor_width_mm, sensor_fit, type, ortho_scale, shift."""
    m = np.asarray(cam['matrix_world'], float).reshape(4, 4)
    p = np.linalg.inv(m) @ np.array([point[0], point[1], point[2], 1.0])
    aspect = w / h
    fit = cam.get('sensor_fit', 'AUTO')
    horiz = fit == 'HORIZONTAL' or (fit == 'AUTO' and w >= h)
    sx, sy = cam.get('shift', (0.0, 0.0))
    if cam.get('type', 'PERSP') == 'ORTHO':
        sc = cam['ortho_scale']
        half_w, half_h = (sc / 2, sc / 2 / aspect) if horiz else (sc / 2 * aspect, sc / 2)
        xn = 0.5 + p[0] / (2 * half_w)
        yn = 0.5 + p[1] / (2 * half_h)
        front = True
    else:
        depth = -p[2]
        front = depth > 1e-4
        depth = depth if abs(depth) > 1e-6 else 1e-6
        sw = cam.get('sensor_width_mm', 36.0)
        if horiz:
            fx = cam['lens_mm'] / sw
            fy = fx * aspect
        else:
            fy = cam['lens_mm'] / sw
            fx = fy / aspect
        xn = 0.5 + fx * p[0] / depth
        yn = 0.5 + fy * p[1] / depth
    big = max(w, h)          # lens shift moves the frame, so the point moves the other way
    xn -= sx * big / w
    yn -= sy * big / h
    return xn * w, (1 - yn) * h, bool(front)
