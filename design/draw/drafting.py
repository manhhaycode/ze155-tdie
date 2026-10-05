"""Shared 2D construction helpers for section views (hatching with holes, screw profiles, bolt circles)."""
import math

import numpy as np
from matplotlib.patches import PathPatch, Circle, Polygon
from matplotlib.path import Path

from sheet import PT, DASH


def circle_pts(cx, cy, r, n=72, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cy + r * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def region(ax, outer, holes=(), hatch="////", fc="white", ec="k", lw=0.35, z=10, hatch_color="k"):
    """Filled, hatched region with holes (lists of points, sheet mm)."""
    verts, codes = [], []

    def add(pts, rev=False):
        pts = list(pts)
        a = sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))
        if (a < 0) != rev:
            pts = pts[::-1]
        verts.extend(pts + [pts[0]])
        codes.extend([Path.MOVETO] + [Path.LINETO] * (len(pts) - 1) + [Path.CLOSEPOLY])
    add(outer)
    for h in holes:
        add(h, rev=True)
    pp = PathPatch(Path(verts, codes), fc=fc, ec=ec, lw=lw * PT, hatch=hatch, zorder=z)
    ax.add_patch(pp)
    return pp


def fig8(cx, cy, a, r, k=1.0, n=90):
    """Figure-8 bore outline: two circles radius r with centres at cx +- a/2 (sheet units scaled by 1/k)."""
    c1, c2 = cx - a / 2 / k, cx + a / 2 / k
    rr = r / k
    h = math.sqrt(max(rr ** 2 - (a / 2 / k) ** 2, 0))
    t = math.atan2(h, a / 2 / k)
    pts = []
    for ang in np.linspace(t, 2 * math.pi - t, n):  # right circle, skipping the inner cusp side
        pts.append((c2 + rr * math.cos(ang - math.pi + 0) * -1, cy + rr * math.sin(ang)))
    pts = []
    for ang in np.linspace(-(math.pi - t), math.pi - t, n):
        pts.append((c2 + rr * math.cos(ang), cy + rr * math.sin(ang)))
    for ang in np.linspace(t, 2 * math.pi - t, n):
        pts.append((c1 + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts


def erdmenger(cx, cy, Ro, a, rot=0.0, k=1.0, n=360):
    """Self-wiping 2-flight co-rotating screw profile (Erdmenger), sheet coordinates (scale 1:k)."""
    psi = math.acos(a / (2 * Ro))
    kap = math.pi / 2 - 2 * psi  # tip angle
    Ri = a - Ro

    def r_of(th):
        th = th % math.pi
        if th > math.pi / 2:
            th = math.pi - th
        if th <= kap / 2:
            return Ro
        if th >= math.pi / 2 - kap / 2:
            return Ri
        beta0 = (math.pi / 2 - kap / 2) - math.pi
        Q = (Ro * math.cos(beta0), Ro * math.sin(beta0))
        e = (math.cos(th), math.sin(th))
        eq = e[0] * Q[0] + e[1] * Q[1]
        return eq + math.sqrt(max(eq ** 2 - Ro ** 2 + a ** 2, 0))
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        r = r_of(th)
        pts.append((cx + r / k * math.cos(th + rot), cy + r / k * math.sin(th + rot)))
    return pts


def hexagon(cx, cy, s_af, rot=0.0):
    r = s_af / math.sqrt(3)
    return [(cx + r * math.cos(rot + math.pi / 6 + i * math.pi / 3), cy + r * math.sin(rot + math.pi / 6 + i * math.pi / 3)) for i in range(6)]


def poly(ax, pts, fc="white", ec="k", lw=0.35, ls="solid", z=12, hatch=None, closed=True):
    p = Polygon(pts, closed=closed, fc=fc if closed else "none", ec=ec, lw=lw * PT, ls=DASH.get(ls, ls), zorder=z, hatch=hatch)
    ax.add_patch(p)
    return p


def circ(ax, c, r, fc="none", ec="k", lw=0.35, ls="solid", z=12, hatch=None):
    p = Circle(c, r, fc=fc, ec=ec, lw=lw * PT, ls=DASH.get(ls, ls), zorder=z, hatch=hatch)
    ax.add_patch(p)
    return p


def section_marker(sh, p1, p2, letter, look, size=4.0):
    """Cutting-plane line p1-p2 (sheet mm) with thick ends and arrows pointing along `look` (unit 2D)."""
    sh.line([p1, p2], lw=0.18, ls="cut", z=45)
    for p, q in ((p1, p2), (p2, p1)):
        d = (q[0] - p[0], q[1] - p[1])
        L = math.hypot(*d) or 1
        e = (p[0] + d[0] / L * 5, p[1] + d[1] / L * 5)
        sh.line([p, e], lw=0.7, z=46)
        tip = (p[0] + look[0] * 6, p[1] + look[1] * 6)
        sh.line([p, tip], lw=0.25, z=46)
        sh.arrow(tip, p, size=2.8)
        sh.text(tip[0] + look[0] * 2.5, tip[1] + look[1] * 2.5, letter, 9, ha="center", va="center", weight="bold", zorder=47)


def break_line(sh, a, b, amp=2.2, lw=0.25, z=46):
    """Freehand-style break line (ISO 128 zig-zag) from sheet point a to b, one Z in the middle; marks a clipped view edge."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    m = (a[0] + dx / 2, a[1] + dy / 2)
    p = lambda t, n: (m[0] + ux * t + nx * n, m[1] + uy * t + ny * n)
    sh.line([(a[0] - ux * 2, a[1] - uy * 2), p(-amp * 1.4, 0), p(-amp * 0.5, amp), p(amp * 0.5, -amp), p(amp * 1.4, 0),
             (b[0] + ux * 2, b[1] + uy * 2)], lw=lw, z=z)


def detail_marker(sh, c, r, letter):
    circ(sh.ax, c, r, ec="k", lw=0.25, z=45)
    sh.text(c[0] + r * 0.75, c[1] + r * 0.75 + 2, letter, 9, ha="left", va="bottom", weight="bold", zorder=47)


# ------------------------------------------------------------------ ISO 10628 / ISA 5.1 style symbols
def sym_valve(sh, c, size=6.0, orient="h", kind="gate", fc="white", z=50):
    """Two-triangle valve body; kind: gate, ball, solenoid, throttle, check, butterfly, needle, relief."""
    ax = sh.ax
    x, y = c
    s = size / 2
    if orient == "h":
        tri1 = [(x - s, y - s * 0.7), (x - s, y + s * 0.7), (x, y)]
        tri2 = [(x + s, y - s * 0.7), (x + s, y + s * 0.7), (x, y)]
    else:
        tri1 = [(x - s * 0.7, y - s), (x + s * 0.7, y - s), (x, y)]
        tri2 = [(x - s * 0.7, y + s), (x + s * 0.7, y + s), (x, y)]
    if kind == "check":
        poly(ax, tri1, fc=fc, lw=0.3, z=z)
        sh.line([(x + s * 0.3, y - s * 0.7), (x + s * 0.3, y + s * 0.7)] if orient == "h" else [(x - s * 0.7, y + s * 0.3), (x + s * 0.7, y + s * 0.3)], lw=0.3, z=z + 1)
        return
    poly(ax, tri1, fc=fc, lw=0.3, z=z)
    poly(ax, tri2, fc=fc, lw=0.3, z=z)
    if kind == "ball":
        circ(ax, (x, y), s * 0.32, fc="k", lw=0.2, z=z + 1)
    elif kind == "butterfly":
        sh.line([(x - s * 0.45, y - s * 0.6), (x + s * 0.45, y + s * 0.6)], lw=0.35, z=z + 1)
    elif kind in ("solenoid", "pneumatic", "motor"):
        top = (x, y + s * 1.5) if orient == "h" else (x + s * 1.5, y)
        sh.line([(x, y), top], lw=0.25, z=z + 1)
        bx, by = top
        poly(ax, [(bx - s * 0.6, by), (bx + s * 0.6, by), (bx + s * 0.6, by + s * 1.0), (bx - s * 0.6, by + s * 1.0)], fc="white", lw=0.3, z=z + 1)
        sh.text(bx, by + s * 0.5, {"solenoid": "S", "pneumatic": "P", "motor": "M"}[kind], 7, ha="center", va="center", zorder=z + 2)
    elif kind in ("throttle", "needle"):
        sh.line([(x - s * 0.9, y - s * 0.9), (x + s * 0.9, y + s * 0.9)], lw=0.25, z=z + 1)
        sh.arrow((x + s * 0.9, y + s * 0.9), (x, y), size=1.6)
    elif kind == "relief":
        sh.line([(x, y), (x, y + s * 1.4)], lw=0.25, z=z + 1)
        sh.line([(x - s * 0.4, y + s * 1.0), (x + s * 0.4, y + s * 1.2), (x - s * 0.4, y + s * 1.4)], lw=0.25, z=z + 1)
    elif kind == "manual":
        top = (x, y + s * 1.3) if orient == "h" else (x + s * 1.3, y)
        sh.line([(x, y), top], lw=0.25, z=z + 1)
        sh.line([(top[0] - s * 0.6, top[1]), (top[0] + s * 0.6, top[1])] if orient == "h" else [(top[0], top[1] - s * 0.6), (top[0], top[1] + s * 0.6)], lw=0.35, z=z + 1)


def sym_strainer(sh, c, size=6.0, z=50):
    x, y = c
    s = size / 2
    poly(sh.ax, [(x - s, y), (x + s, y), (x + s * 0.2, y - s * 1.2)], fc="white", lw=0.3, z=z)
    sh.line([(x - s * 0.4, y - s * 0.3), (x + s * 0.3, y - s * 0.8)], lw=0.2, ls="hidden", z=z + 1)


def sym_pump(sh, c, r=5.0, kind="centrifugal", z=50, label=None):
    x, y = c
    circ(sh.ax, (x, y), r, fc="white", lw=0.35, z=z)
    if kind == "gear":
        circ(sh.ax, (x - r * 0.3, y), r * 0.35, lw=0.2, z=z + 1)
        circ(sh.ax, (x + r * 0.3, y), r * 0.35, lw=0.2, z=z + 1)
    elif kind == "vacuum":
        poly(sh.ax, [(x - r * 0.6, y - r * 0.5), (x + r * 0.6, y), (x - r * 0.6, y + r * 0.5)], fc="none", lw=0.25, z=z + 1)
    else:
        sh.line([(x, y + r), (x + r, y)], lw=0.25, z=z + 1)
        sh.line([(x, y - r), (x + r, y)], lw=0.25, z=z + 1)
    if label:
        sh.text(x, y - r - 1.2, label, ha="center", va="top", zorder=z + 2)


def sym_instrument(sh, c, func, tag, r=6.8, panel=False, z=60):
    """ISA 5.1 bubble: function letters above, loop number below; a horizontal bar = panel mounted."""
    x, y = c
    circ(sh.ax, (x, y), r, fc="white", lw=0.35, z=z)
    if panel:
        sh.line([(x - r, y), (x + r, y)], lw=0.3, z=z + 1)
    sh.text(x, y + r * 0.38, func, 8.2 if len(func) < 4 else 7.0, ha="center", va="center", zorder=z + 2, weight="bold")
    sh.text(x, y - r * 0.42, tag, 7.6, ha="center", va="center", zorder=z + 2)


def sym_box(sh, c, w, h, text, fs=None, fc="white", z=40, ls="solid"):
    x, y = c
    poly(sh.ax, [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], fc=fc, lw=0.35, z=z, ls=ls)
    sh.text(x, y, text, fs or 9.8, ha="center", va="center", zorder=z + 1)
