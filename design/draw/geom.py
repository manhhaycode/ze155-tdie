"""3D primitives for every part in design/parts.json and their orthographic projection.

Shared by views.py (Blender background images) and the sheet scripts (engineering drawings), so the
drawings and the data cannot drift apart.  All coordinates in world mm (X flow, Y operator, Z up).

A part is turned into a list of Prim objects.  The silhouette comes from the parts.json geometry
(bbox, outline_mm, profile_mm, path_mm, positions_mm); the extra prims add the visible features listed
in `details` (doors, handles, bolts, flanges) and always stay inside the part's bbox unless a design
issue is logged in drawings/design_issues.md.
"""
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "design" / "parts.json").read_text())
PARTS = DATA["parts"]
P = {p["id"]: p for p in PARTS}
ORDER = [p["id"] for p in PARTS]
NUM = {pid: i + 1 for i, pid in enumerate(ORDER)}  # global item number used by every sheet
CONN = DATA["connections"]
AXI = {"X": 0, "Y": 1, "Z": 2}


def axvec(s):
    v = np.zeros(3)
    v[AXI[s[-1]]] = -1.0 if s[0] == "-" else 1.0
    return v


class View:
    def __init__(self, name, right, up, look):
        self.name, self.rs, self.us, self.ls = name, right, up, look
        self.R, self.U, self.L = axvec(right), axvec(up), axvec(look)

    def uv(self, p):
        p = np.asarray(p, float)
        return float(p @ self.R), float(p @ self.U)

    def depth(self, p):
        return float(np.asarray(p, float) @ self.L)


VIEWS = {
    "front": View("front", "-X", "+Z", "-Y"),
    "rear": View("rear", "+X", "+Z", "+Y"),
    "top": View("top", "-X", "-Y", "-Z"),
    "die_end": View("die_end", "+Y", "+Z", "-X"),
    "drive_end": View("drive_end", "-Y", "+Z", "+X"),
}


# ----------------------------------------------------------------------------------------- prims
class Prim:
    def __init__(self, kind, data, fill=True, lw="thick", ls=None, sil=True, shade=None, nofill=(),
                 hidden=False):
        self.kind, self.data = kind, data
        self.fill, self.lw, self.ls, self.sil, self.shade = fill, lw, ls, sil, shade
        self.nofill = set(nofill)  # look-strings of views in which this prim is drawn unfilled
        self.hidden = hidden       # internal item: dashed on sheets when requested
        self.part = None


def B(x0, x1, y0, y1, z0, z1, **k):
    return Prim("box", (x0, x1, y0, y1, z0, z1), **k)


def C(ax, c, r, t0, t1, **k):
    return Prim("cyl", (AXI[ax], list(map(float, c)), float(r), float(t0), float(t1)), **k)


def R(ax, c, prof, t0, **k):
    return Prim("rev", (AXI[ax], list(map(float, c)), [tuple(map(float, q)) for q in prof], float(t0)), **k)


def PR(plane, pts, d0, d1, sharp=25.0, **k):
    return Prim("prism", (plane, [tuple(map(float, q)) for q in pts], float(d0), float(d1), sharp), **k)


def H(pts, **k):
    return Prim("hull", [tuple(map(float, q)) for q in pts], **k)


def PI(path, r, **k):
    return Prim("pipe", ([tuple(map(float, q)) for q in path], float(r)), **k)


def L3(pts, **k):
    k.setdefault("fill", False)
    k.setdefault("sil", False)
    k.setdefault("lw", "thin")
    return Prim("lines", [tuple(map(float, q)) for q in pts], **k)


def Q3(pts, **k):
    return Prim("poly3", [tuple(map(float, q)) for q in pts], **k)


def D(face, w, shapes, **k):
    """Decal on an axis-aligned face. face '+Y' etc; shapes in the two other world axes (in X<Y<Z order)."""
    k.setdefault("sil", False)
    k.setdefault("lw", "thin")
    return Prim("decal", (AXI[face[1]], 1 if face[0] == "+" else -1, float(w), shapes), **k)


# decal shapes
def rect(p0, p1, q0, q1, fill=None):
    return ("poly", [(p0, q0), (p1, q0), (p1, q1), (p0, q1)], fill)


def circ(p, q, r, fill=None):
    return ("circle", (p, q, r), fill)


def poly(pts, fill=None):
    return ("poly", pts, fill)


def line(pts):
    return ("line", pts, None)


# ------------------------------------------------------------------------------- part geometry
def _bb(p):
    return p["bbox_mm"]


def g_frame_seg(p):
    o = p["outline_mm"]
    x0, x1 = o["d0"], o["d1"]
    pr = [PR("YZ", o["pts"], x0, x1)]
    holes = {"base_frame_drive": [-541, -3858], "base_frame_process": [1185, 5170]}[p["id"]]
    for s in (1, -1):
        sh = []
        x = x0 + 120
        while x + 520 <= x1 - 80:
            if all(abs(x + 260 - h) > 360 for h in holes):
                sh += [rect(x, x + 520, 95, 420), rect(x + 445, x + 495, 220, 300, "dark")]
            x += 860
        for h in holes:
            sh += [circ(h, 255, 70), circ(h, 255, 48, "mid")]
        pr.append(D(("+Y" if s > 0 else "-Y"), s * 950, sh))
        welds = [line([(xx, 458), (xx, 642)]) for xx in np.arange(x0 + 1050, x1 - 100, 1050)]
        pr.append(D(("+Y" if s > 0 else "-Y"), s * 1000, welds))
    return pr


def g_feet(p):
    out = []
    for x, y, z in p["positions_mm"]:
        out += [C("Z", [x, y, 0], 100, 0, 25, shade="dark"), C("Z", [x, y, 0], 30, 25, 60)]
    return out


def g_support(p):
    o = p["outline_mm"]
    pr = [PR("YZ", o["pts"], o["d0"], o["d1"])]
    pr.append(D("+X", o["d1"], [circ(0, 800, 60)]))
    pr.append(D("-X", o["d0"], [circ(0, 800, 60)]))
    return pr


def g_legframe(x0, x1, y0, y1, ztop, tp=30, leg=120, nx=2, rails=True):
    out = [B(x0, x1, y0, y1, ztop - tp, ztop)]
    xs = np.linspace(x0 + 20, x1 - 20 - leg, nx)
    for xa in xs:
        for ya in (y0 + 20, y1 - 20 - leg):
            out.append(B(xa, xa + leg, ya, ya + leg, 0, ztop - tp))
            out.append(B(xa - 20, xa + leg + 20, ya - 20, ya + leg + 20, 0, 15, shade="dark"))
    if rails:
        for ya in (y0 + 20, y1 - 20 - leg):
            out.append(B(x0 + 20, x1 - 20, ya + 20, ya + leg - 20, 150, 230))
        for s, ya in ((1, y1 - 20), (-1, y0 + 20)):
            for i in range(nx - 1):
                xa, xb = xs[i] + leg, xs[i + 1]
                out.append(D("+Y" if s > 0 else "-Y", ya, [line([(xa, 230), (xb, ztop - tp)]), line([(xa, ztop - tp), (xb, 230)])]))
    return out


def g_stand_sc(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return g_legframe(x0, x1, y0, y1, z1, nx=2)


def g_stand_pump(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return g_legframe(x0, x1, y0, y1, z1, nx=3)


def g_saddles(p):
    # details: 2 V-saddles at X 8250 and 8676 (bbox X 8100-8750 -> widths 300 and 150, see design_issues)
    out = []
    for xa, xb in ((8100, 8400), (8602, 8750)):
        out.append(B(xa, xb, -120, 120, 970, 1000))
        out.append(PR("YZ", [(-120, 1000), (120, 1000), (120, 1050), (90, 1050), (0, 1000 + 0), (-90, 1050), (-120, 1050)], xa, xb))
    return out


def g_pedestal(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    out = [B(x0, x1, y0, y1, z1 - 30, z1)]
    for xa in (x0, x1 - 100):
        for ya in (y0, y1 - 100):
            out.append(B(xa, xa + 100, ya, ya + 100, 0, z1 - 30))
    for s, ya in ((1, y1), (-1, y0)):
        out.append(D("+Y" if s > 0 else "-Y", ya, [line([(x0 + 100, 60), (x1 - 100, z1 - 60)]), line([(x0 + 100, z1 - 60), (x1 - 100, 60)])]))
    out.append(B(x0, x1, y0, y1, 0, 20, shade="dark"))
    return out


def g_lantern(p):
    o = p["outline_mm"]
    out = [PR("XZ", o["pts"], -450, 450)]
    out.append(R("X", [0, 0, 1200], [(0, 0), (350, 0), (350, 60), (0, 60)], -60))
    sh = [rect(-565, -185, 1075, 1325), rect(-545, -205, 1095, 1305)]
    for xx in (-545, -375, -205):
        for zz in (1085, 1315):
            sh.append(circ(xx, zz, 8, "dark"))
    sh += [circ(-565, 1200, 8, "dark"), circ(-185, 1200, 8, "dark"), rect(-420, -330, 1185, 1215, "dark")]
    out.append(D("+Y", 450, sh))
    out.append(D("-Y", -450, [rect(-565, -185, 1075, 1325)]))
    return out


def g_gearbox(p):
    pts = [(-2250, 650), (-750, 650), (-750, 1720), (-1250, 1720), (-1320, 1650), (-2250, 1650)]
    out = [PR("XZ", pts, -700, 700), C("X", [0, 0, 1200], 250, -2300, -2250)]
    for x in (-2150, -1450):
        for y in (-620, 620):
            out.append(C("Y", [x, 0, 1680], 28, y - 10, y + 10, shade="dark"))
    out.append(C("Z", [-1700, 450, 0], 25, 1650, 1700))
    out.append(D("+Z", 1650, [rect(-2050, -1500, -380, 380)]))
    for s in (1, -1):
        sh = [line([(x, 680), (x, 1620)]) for x in (-2150, -1850, -1550)]
        sh += [rect(-1150, -850, 1300, 1450), line([(-2250, 1450), (-1320, 1450)])]
        if s > 0:
            sh += [circ(-1500, 900, 45), circ(-1500, 900, 30, "mid"), rect(-2100, -1900, 1150, 1260), circ(-2000, 1500, 28, "dark"), circ(-1500, 760, 30, "dark")]
        out.append(D("+Y" if s > 0 else "-Y", s * 700, sh))
    return out


def g_rev(p):
    ax = p.get("axis", "X")
    b = _bb(p)
    i = AXI[ax]
    prof = p.get("profile_mm")
    if not prof:
        r = p.get("radius_mm") or (b[3] - b[2]) / 2
        L = b[2 * i + 1] - b[2 * i]
        prof = [(0, 0), (r, 0), (r, L), (0, L)]
    c = p["center_mm"]
    return [R(ax, c, prof, b[2 * i])]


def g_guard(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    out = [B(x0, x1, y0, y1, z0, z1)]
    sh = [rect(-2850, -2430, 950, 1450)]
    for k in range(1, 9):
        sh.append(line([(-2850 + 46.7 * k, 950), (-2850 + 46.7 * k, 1450)]))
    for k in range(1, 10):
        sh.append(line([(-2850, 950 + 50 * k), (-2430, 950 + 50 * k)]))
    sh += [rect(-2960, -2930, 1300, 1380, "dark"), line([(x0 + 10, 680), (x1 - 10, 680)])]
    out.append(D("+Y", y1, sh))
    out.append(D("-Y", y0, [rect(-2850, -2430, 950, 1450), line([(x0 + 10, 680), (x1 - 10, 680)])]))
    out.append(D("+Z", z1, [rect(-2680, -2600, -60, 60, "dark")]))
    return out


def g_motor(p):
    out = [B(-4900, -3150, -575, 575, 750, 1680), B(-4800, -3300, -560, 560, 1680, 2610),
           C("X", [0, 0, 1200], 70, -3150, -2950), C("X", [0, 0, 1200], 200, -4975, -4900)]
    for s in (1, -1):
        sh = [line([(-4860, z), (-3190, z)]) for z in range(830, 1660, 70)]
        sh2 = []
        for xa in (-4700, -4000):
            sh2.append(rect(xa, xa + 600, 1820, 2470))
            sh2 += [line([(xa + 15, z), (xa + 585, z)]) for z in range(1860, 2460, 45)]
        if s > 0:
            sh.append(rect(-4200, -3950, 1450, 1580, "light"))
        out.append(D("+Y" if s > 0 else "-Y", s * 575, sh))
        out.append(D("+Y" if s > 0 else "-Y", s * 560, sh2))
    for f, xw in (("+X", -3300), ("-X", -4800)):
        sh = [rect(-420, 420, 1800, 2480)] + [line([(-400, z), (400, z)]) for z in range(1840, 2470, 45)]
        out.append(D(f, xw, sh))
    out.append(D("+Z", 2610, [rect(-4700, -3400, -460, 460), rect(-4650, -3450, -410, 410)]))
    return out


def g_tbox(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(x0, x1, y0, y1, z0, z1), D("-Y", y0, [rect(x0 + 30, x1 - 30, z0 + 30, z1 - 30)] +
            [circ(x, z, 8, "dark") for x in (x0 + 50, x1 - 50) for z in (z0 + 50, z1 - 50)]),
            D("-Z", z0, [circ(-4100, -750, 35), circ(-4000, -750, 35), circ(-3900, -750, 35)])]


def g_motor_base(p):
    out = [B(-5000, -3000, -600, -300, 650, 750), B(-5000, -3000, 300, 600, 650, 750),
           B(-5000, -4900, -300, 300, 650, 720), B(-3100, -3000, -300, 300, 650, 720)]
    for s in (1, -1):
        out.append(D("+Y" if s > 0 else "-Y", s * 600, [circ(x, 700, 18, "dark") for x in (-4700, -4000, -3300)]))
    return out


def g_cyl_axis(p):
    b = _bb(p)
    ax = p.get("axis", "Z")
    i = AXI[ax]
    r = p.get("radius_mm") or min(b[2 * j + 1] - b[2 * j] for j in range(3) if j != i) / 2
    return [C(ax, p["center_mm"], r, b[2 * i], b[2 * i + 1])]


def g_box(p):
    return [B(*_bb(p))]


def g_lube_pump(p):
    x, y = -3350, 800
    return [B(-3470, -3230, 690, 910, 700, 800), C("Z", [x, y, 0], 90, 800, 880), C("Z", [x, y, 0], 110, 880, 960),
            C("Z", [x, y, 0], 130, 960, 1370), C("Z", [x, y, 0], 120, 1370, 1450), C("Y", [x, 0, 760], 25, 910, 950),
            C("X", [0, 750, 1050], 25, -3500, -3480, shade="mid"), C("X", [0, 850, 1050], 25, -3500, -3480, shade="mid")]


def g_lube_filter(p):
    return [B(-3200, -2950, 680, 900, 700, 740), C("Z", [-3140, 815, 0], 55, 740, 1230), C("Z", [-3010, 815, 0], 55, 740, 1230),
            B(-3200, -2950, 740, 890, 1230, 1330), C("Z", [-3075, 815, 0], 10, 1330, 1400, shade="dark"),
            C("Y", [-3075, 0, 1290], 20, 890, 950, shade="mid")]


def g_lube_cooler(p):
    out = [B(-2950, -2600, 650, 870, 700, 1050), C("Y", [-2775, 0, 850], 20, 870, 900), C("Y", [-2690, 0, 950], 20, 870, 900),
           C("Z", [-2775, 775, 0], 21, 1050, 1051)]
    out.append(D("+Y", 870, [line([(x, 715), (x, 1035)]) for x in np.arange(-2930, -2615, 25)]))
    out.append(D("-Y", 650, [line([(x, 715), (x, 1035)]) for x in np.arange(-2930, -2615, 25)]))
    return out


def g_pipe(p):
    out = [PI(p["path_mm"], p["radius_mm"])]
    return out


def g_barrel(p):
    b = _bb(p)
    out = [R("X", [0, 0, 1200], p["profile_mm"], b[0])]
    if p["id"] == "barrel_b6":
        out.append(C("Y", [5400, 0, 1200], 80, 250, 300))
    return out


def g_joint(p):
    out = []
    for x, y, z in p["positions_mm"]:
        x0, x1 = x - 82, x + 82
        out += [C("X", [0, y, z], 12, x0, x1, shade="mid"), C("X", [0, y, z], 18, x0 + 8, x0 + 32, shade="dark"),
                C("X", [0, y, z], 18, x1 - 32, x1 - 8, shade="dark")]
    return out


def g_heaters(p):
    prof = [(0, 0), (284, 0), (284, 14), (290, 14), (290, 366), (284, 366), (284, 380), (0, 380)]
    return [R("X", [0, 0, 1200], prof, x - 190) for x, y, z in p["positions_mm"]]


def g_screws(p):
    out = []
    for y in (71, -71):
        out += [C("X", [0, y, 1200], 83.75, 0, 5746, hidden=True), C("X", [0, y, 1200], 60, -400, 0, hidden=True)]
    return out


def g_vent_atm(p):
    return [B(2050, 2350, -150, 150, 1455, 1490), C("Z", [2200, 0, 0], 120, 1490, 1860), C("Z", [2200, 0, 0], 150, 1860, 1880),
            C("Z", [2200, 0, 0], 140, 1880, 1900)]


def g_dome(p):
    o = p["outline_mm"]
    out = [B(3820, 4420, -200, 200, 1455, 1460, shade="mid"), PR("XZ", o["pts"], o["d0"], o["d1"]),
           C("Y", [4120, 0, 1980], 142.5, -320, -295), C("Y", [4120, 0, 1980], 84, -295, -200)]
    for x in (3970, 4270):
        out += [C("Y", [x, 0, 1880], 80, 200, 215), C("Y", [x, 0, 1880], 60, 215, 230, shade="light")]
    out.append(D("+Z", 2150, [circ(x, y, 15, "dark") for x in (3840, 4400) for y in (-170, 170)] + [rect(3950, 4050, -20, 20, "dark")]))
    return out


def g_cover(p):
    o = p["outline_mm"]
    x0, x1 = o["d0"], o["d1"]
    xm = (x0 + x1) / 2
    out = [PR("YZ", o["pts"], x0, x1)]
    sh = [line([(x0 + 5, 1150), (x1 - 5, 1150)]), rect(xm - 110, xm + 110, 1360, 1400, "dark"),
          rect(xm - 110, xm + 110, 880, 920, "dark"), poly([(xm - 55, 1085), (xm + 55, 1085), (xm, 1180)], "mid")]
    if p["id"] == "barrel_cover_c1":
        sh = [line([(x0 + 5, 1150), (x1 - 5, 1150)]), rect(5600, 5700, 1360, 1400, "dark"), rect(5600, 5700, 880, 920, "dark"),
              circ(5400, 1200, 210), poly([(5600, 1085), (5700, 1085), (5650, 1180)], "mid"), rect(5350, 5450, 900, 1000)]
        sh += [circ(5400 + 185 * math.cos(a), 1200 + 185 * math.sin(a), 11, "dark") for a in np.linspace(0, 2 * math.pi, 11)[:-1]]
    out.append(D("+Y", 480, sh))
    out.append(D("-Y", -480, [line([(x0 + 5, 1150), (x1 - 5, 1150)])] + [rect(xa, xa + 60, 1440, 1470, "dark") for xa in (x0 + 80, x1 - 140)]))
    out.append(D("+Z", 1650, [rect(xm - 110, xm + 110, -20, 20, "dark")]))
    if p["id"] == "barrel_cover_c1":
        out.append(D("+X", x1, [circ(0, 1200, 330)]))
    if p["id"] == "barrel_cover_c6":
        out.append(D("-X", x0, [circ(0, 1200, 330)]))
    return out


def g_tcs(p):
    out = []
    for x in (338, 1450, 2450, 3211, 4600, 5239):
        out += [C("Z", [x, 0, 0], 12, 1455, 1520), C("Z", [x, 0, 0], 20, 1520, 1545, shade="mid")]
    return out


def g_cw_valves(p):
    out = []
    for x, y, z in p["positions_mm"]:
        out += [B(x - 100, x + 100, 820, 1000, 650, 670), B(x - 50, x + 50, 830, 990, 740, 950),
                C("Z", [x - 20, 910, 0], 30, 950, 1000, shade="dark"), B(x + 50, x + 100, 960, 1000, 860, 880, shade="dark"),
                C("Y", [x + 20, 0, 780], 22, 990, 1000, shade="light")]
    return out


ZONES = [338, 1183, 2197, 3211, 4225, 5239]


def g_cw_hoses(p):
    out = []
    for x in ZONES:
        for dx in (-80, 80):
            out.append(PI([(x + dx, 900, 985), (x + dx, 500, 985), (x + dx, 150, 955), (x + dx, 0, 950)], 12))
    return out


def g_jboxes(p):
    out = []
    for x, y, z in p["positions_mm"]:
        out += [B(x - 90, x + 90, -700, -520, 700, 960), D("-Y", -700, [rect(x - 70, x + 70, 720, 940), rect(x - 30, x + 30, 900, 930, "mid")])]
    return out


def g_tray(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(x0, x1, y0, y1, z0, z1), D("-Y", y0, [line([(x0, z0 + 50), (x1, z0 + 50)])]),
            D("+Z", z1, [line([(x, y0 + 10), (x, y1 - 10)]) for x in np.arange(x0 + 500, x1, 1000)])]


def g_throat(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(x0, x1, y0, y1, z0, z1), D("+Y", y1, [circ(150, 1550, 18, "dark"), circ(530, 1550, 18, "dark")]),
            D("-Y", y0, [circ(150, 1550, 18, "dark"), circ(530, 1550, 18, "dark")])]


def g_hopper(p):
    return [H([(160, -150, 1640), (520, -150, 1640), (520, 150, 1640), (160, 150, 1640),
               (90, -250, 1900), (590, -250, 1900), (590, 250, 1900), (90, 250, 1900)]),
            C("Z", [470, 150, 0], 15, 1900, 1901), D("+Z", 1900, [circ(470, 150, 20, "dark"), circ(470, -150, 30)])]


def g_sleeve(p):
    a, b = np.array(p["path_mm"][0], float), np.array(p["path_mm"][1], float)
    d = (b - a) / np.linalg.norm(b - a)
    r = p["radius_mm"]
    return [PI([a, b], r), PI([a, a + 18 * d], r, shade="mid"), PI([b - 18 * d, b], r, shade="mid")]


def g_main_feeder(p):
    return [B(-1000, 100, -450, 450, 3000, 3080), C("Y", [-450, 0, 3380], 280, -250, 250), C("Z", [-450, 0, 0], 150, 3600, 3700),
            B(-650, -250, -450, -250, 3200, 3520), B(-150, 100, 250, 450, 3150, 3500),
            D("+Y", 450, [rect(-100, 50, 3200, 3450)]), D("-Y", -450, [circ(-450, 3360, 120)])]


def g_add_feeder(p):
    return [B(-1000, -300, 600, 1100, 3000, 3600), C("Z", [-650, 850, 0], 250, 3600, 4200),
            D("+Y", 1100, [rect(-950, -350, 3050, 3550)])]


SECTION_MM = {"HEA180": (180, 171), "HEB200": (200, 200), "HEA200": (200, 190), "IPE160": (82, 160), "IPE200": (100, 200)}


def g_deck(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    if p.get("beams_mm"):
        zg = z1 - 40
        out = [B(x0, x1, y0, y1, zg, z1, nofill={"-Z"}, lw="thick")]
        for bm in p["beams_mm"]:
            w, h = SECTION_MM.get(bm.get("section", "HEA180"), (180, 171))
            a, b = np.array(bm["from"], float), np.array(bm["to"], float)
            zc = a[2]
            za, zb = max(z0, zc - h / 2), min(zg, zc + h / 2)
            lo = np.minimum(a, b)
            hi = np.maximum(a, b)
            if abs(a[0] - b[0]) > abs(a[1] - b[1]):
                bx = (max(x0, lo[0]), min(x1, hi[0]), max(y0, lo[1] - w / 2), min(y1, hi[1] + w / 2))
            else:
                bx = (max(x0, lo[0] - w / 2), min(x1, hi[0] + w / 2), max(y0, lo[1]), min(y1, hi[1]))
            out.append(B(bx[0], bx[1], bx[2], bx[3], z0, zg))
        holes = [(-450, 0, 150), (-650, 850, 60), (1350, 950, 100)]
        out.append(D("+Z", z1, [circ(x, y, r) for x, y, r in holes]))
        return out
    out = [B(x0, x1, y0, y1, 2960, 3000, nofill={"-Z"}, lw="thick")]
    out += [B(x0, x1, y0, y0 + 180, 2780, 2960), B(x0, x1, y1 - 180, y1, 2780, 2960),
            B(x0, x0 + 180, y0 + 180, y1 - 180, 2780, 2960), B(x1 - 180, x1, y0 + 180, y1 - 180, 2780, 2960)]
    # primary beams on the inner column line X = -450, trimmed around the down-pipe opening (design_issues)
    out += [B(-540, -360, y0 + 180, -260, 2780, 2960), B(-540, -360, 260, y1 - 180, 2780, 2960),
            B(-760, -140, -260, -170, 2780, 2960), B(-760, -140, 170, 260, 2780, 2960)]
    out.append(D("+Z", 3000, [circ(-450, 0, 150), circ(-650, 850, 60), circ(1350, 950, 100)]))
    return out


def g_columns(p):
    out = []
    for x, y, z in p["positions_mm"]:
        out.append(B(x - 100, x + 100, y - 100, y + 100, 0, 2780))
        for f, w in (("+X", x + 100), ("-X", x - 100)):
            out.append(D(f, w, [line([(y - 85, 0), (y - 85, 2780)]), line([(y + 85, 0), (y + 85, 2780)])]))
    return out


def g_railing(p):
    pts = p["outline_mm"]["pts"]
    x0, x1, y0, y1 = -2700 + 21, 1850 - 21, -2300 + 21, 1400 - 21
    cl = [(min(max(x, x0), x1), min(max(y, y0), y1)) for x, y in pts]
    out = []
    for z, r in ((4079, 21), (3550, 17)):
        out.append(PI([(x, y, z) for x, y in cl], r, shade="mid"))
    posts = []
    for (xa, ya), (xb, yb) in zip(cl, cl[1:]):
        n = max(1, math.ceil(math.hypot(xb - xa, yb - ya) / 1500))
        for k in range(n):
            posts.append((xa + (xb - xa) * k / n, ya + (yb - ya) * k / n))
    posts.append(cl[-1])
    for x, y in posts:
        out.append(PI([(x, y, 3000), (x, y, 4079)], 21, shade="mid"))
    for (xa, ya), (xb, yb) in zip(cl, cl[1:]):
        if xa == xb:
            out.append(B(xa - 5, xa + 5, min(ya, yb), max(ya, yb), 3000, 3150, shade="mid"))
        else:
            out.append(B(min(xa, xb), max(xa, xb), ya - 5, ya + 5, 3000, 3150, shade="mid"))
    return out


def g_stair(p):
    out = []
    band = [(-5700, 0), (-5400, 0), (-2700, 2700), (-2700, 3000)]
    out += [PR("XZ", band, -2150, -2140, shade="mid"), PR("XZ", band, -1460, -1450, shade="mid")]
    for k in range(1, 15):
        z = 200 * k
        xa, xb = z - 5650, min(z - 5400, -2700)
        out.append(B(xa, xb, -2140, -1460, z - 30, z))
    for y in (-2129, -1471):
        out.append(PI([(-5679, y, 1015), (-2721, y, 3985)], 21, shade="mid"))
        for x in (-5679, -4700, -3700, -2721):
            out.append(PI([(x, y, x + 5700), (x, y, x + 6700 - 21)], 18, shade="mid"))
    return out


def g_feed_cab(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(x0, x1, y0, y1, z0, z1), D("-Y", y0, [rect(x0 + 30, x1 - 30, z0 + 60, z1 - 30), rect(x0 + 150, x1 - 150, z1 - 400, z1 - 150, "mid")])]


def g_sf_barrel(p):
    o = p.get("outline_mm")
    if o:
        out = [PR(o["plane"], o["pts"], o["d0"], o["d1"])]
        for y in (340, 590, 840, 1090):
            out.append(D("+Z", p["bbox_mm"][5], [line([(p["bbox_mm"][0] + 5, y), (p["bbox_mm"][1] - 5, y)])]))
        return out
    pts = []
    for a in np.linspace(90, -90, 13):
        pts.append((1385 + 130 * math.cos(math.radians(a)), 1200 + 130 * math.sin(math.radians(a))))
    for a in np.linspace(-90, -270, 13):
        pts.append((1315 + 130 * math.cos(math.radians(a)), 1200 + 130 * math.sin(math.radians(a))))
    out = [PR("XZ", pts, 330, 1100)]
    for y in (340, 590, 840, 1090):
        out.append(D("+Z", 1330, [line([(1190, y), (1510, y)])]))
    return out


def g_sf_hopper(p):
    return [H([(1250, 860, 1330), (1450, 860, 1330), (1450, 1040, 1330), (1250, 1040, 1330),
               (1200, 820, 1600), (1500, 820, 1600), (1500, 1080, 1600), (1200, 1080, 1600)])]


def g_sf_motor(p):
    return [C("Y", [1350, 0, 1200], 180, 1450, 1980), C("Y", [1350, 0, 1200], 165, 1980, 2050, shade="mid"),
            B(1230, 1470, 1500, 1900, 1000, 1040)]


def g_sf_cart(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    out = [B(x0, x1, y0, y1, 970, 1000), B(x0 + 10, x1 - 10, y0 + 10, y1 - 10, 100, 140)]
    for xa in (x0 + 10, x1 - 70):
        for ya in (y0 + 10, y1 - 70):
            out.append(B(xa, xa + 60, ya, ya + 60, 140, 970))
    for xa in (x0 + 35, x1 - 35):
        for ya in (y0 + 35, y1 - 35):
            out.append(C("X", [0, ya, 50], 50, xa - 20, xa + 20, shade="dark"))
    out.append(D("+Y", y1, [poly([(1310, 600), (1390, 600), (1350, 670)], "mid")]))
    return out


def g_sf_down(p):
    return [PI(p["path_mm"], 75), PI([(1350, 950, 1600), (1350, 950, 1760)], 75, shade="mid")]


def g_sf_feeder(p):
    return [B(1000, 1700, 650, 1250, 3000, 3060), B(1100, 1600, 750, 1150, 3060, 3400), C("X", [0, 950, 3250], 100, 1000, 1100),
            C("Z", [1350, 950, 0], 150, 3400, 3550)]


def g_vac_valve(p):
    return [C("Y", [4120, 0, 1980], 100, -420, -320), B(4060, 4180, -410, -330, 2080, 2250)]


def g_bellows(p):
    prof = [(0, 0), (110, 0), (110, 12)]
    h = 12
    while h < 180:
        prof += [(95, h), (95, h + 8), (108, h + 8), (108, h + 16)]
        h += 16
    prof += [(110, 188), (110, 200), (0, 200)]
    return [R("Y", [4120, 0, 1980], prof, -620)]


def g_vac_support(p):
    return [C("Z", [4120, -1500, 0], 50, 15, 1846), B(4070, 4170, -1550, -1450, 0, 15, shade="dark"), B(4070, 4170, -1550, -1450, 1846, 1896)]


def g_bleed(p):
    return [C("Z", [4120, -1500, 0], 25, 2060, 2150), B(4080, 4160, -1520, -1480, 2150, 2200, shade="dark")]


def g_gauge_dome(p):
    return [C("Z", [4310, 0, 0], 10, 2150, 2240), C("Y", [4310, 0, 2270], 30, -30, 30, shade="dark")]


def g_separator(p):
    out = [R("Z", [4120, -2000, 0], p["profile_mm"], 0)]
    for a in (90, 210, 330):
        x, y = 4120 + 240 * math.cos(math.radians(a)), -2000 + 240 * math.sin(math.radians(a))
        out.append(B(x - 25, x + 25, y - 25, y + 25, 0, 390))
    return out


def g_vac_drain(p):
    return [C("Z", [4120, -2000, 0], 100, 0, 300), B(4180, 4220, -2010, -1990, 200, 290, shade="dark")]


def g_vac_pump(p):
    return [B(4500, 6300, -2600, -1500, 0, 150, shade="mid"), B(4600, 5500, -2450, -1650, 150, 1000),
            C("X", [0, -2050, 600], 200, 5500, 5950), B(4650, 5100, -2250, -1750, 1000, 1450),
            C("Z", [4860, -2000, 0], 80, 1450, 1500), C("X", [0, -2000, 1225], 150, 5100, 5550),
            C("Z", [6150, -2400, 0], 120, 150, 1500), B(5950, 6300, -2000, -1550, 150, 900),
            D("+Y", -1650, [rect(4650, 5450, 250, 900)]), D("+Y", -1550, [rect(6000, 6250, 300, 800)] + [line([(6010, z), (6240, z)]) for z in range(350, 800, 50)])]


def g_vac_ctrl(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(x0, x1, y0, y1, z0, z1), D("+Y", y1, [rect(x0 + 30, x1 - 30, z0 + 30, z1 - 30), circ(6100, 1300, 45, "dark"), circ(6000, 1100, 15, "mid"), circ(6200, 1100, 15, "mid")])]


def g_sensor(x, z0, z1):
    return [C("Z", [x, 0, 0], 12.5, z0, z1 - 60), C("Z", [x, 0, 0], 20, z1 - 60, z1, shade="mid")]


def g_sensor_head(p):
    return g_sensor(5876, 1415, 1700) + g_sensor(5916, 1415, 1700)


def g_sensor_one(p):
    b = _bb(p)
    return g_sensor((b[0] + b[1]) / 2, b[4], b[5])


def g_sensor_die(p):
    return g_sensor(9006, 1375, 1620) + g_sensor(9046, 1375, 1620)


def g_startup(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    out = [B(x0, x1, y0, y1, z0, z1)]
    for f, w in (("+Y", y1), ("-Y", y0)):
        out.append(D(f, w, [circ(6221, 1200, 80), circ(6221, 1200, 50), line([(x0 + 40, z0 + 20), (x0 + 40, z1 - 20)]), line([(x1 - 40, z0 + 20), (x1 - 40, z1 - 20)])]))
    out.append(D("+Z", z1, [circ(x, y, 14, "dark") for x in (6060, 6382) for y in (-180, 0, 180)]))
    return out


def g_startup_cyl(p):
    return [C("Y", [6221, 0, 1200], 80, -860, -480), C("Y", [6221, 0, 1200], 80, -860, -825, shade="mid"),
            C("Y", [6221, 0, 1200], 80, -515, -480, shade="mid"), C("Y", [6221, 0, 1200], 28, -480, -300),
            B(6191, 6251, -300, -260, 1165, 1235), B(6141, 6181, -700, -620, 1280 - 40, 1280, shade="dark")]


def g_chute(p):
    return [H([(6096, -125, 940), (6346, -125, 940), (6346, 125, 940), (6096, 125, 940),
               (6146, -100, 520), (6296, -100, 520), (6296, 100, 520), (6146, 100, 520)])]


def g_purge(p):
    out = [H([(5980, -400, 520), (6500, -400, 520), (6500, 400, 520), (5980, 400, 520),
              (6010, -370, 90), (6470, -370, 90), (6470, 370, 90), (6010, 370, 90)])]
    for x in (6060, 6420):
        for y in (-330, 330):
            out.append(C("X", [0, y, 45], 45, x - 20, x + 20, shade="dark"))
    return out


def g_screen_changer(p):
    o = p["outline_mm"]
    out = [PR("YZ", o["pts"], o["d0"], o["d1"])]
    for f, w in (("-X", 6596), ("+X", 7301)):
        sh = [circ(0, 1200, 150), circ(0, 1200, 60)]
        sh += [circ(175 * math.cos(a), 1200 + 175 * math.sin(a), 14, "dark") for a in np.linspace(0, 2 * math.pi, 9)[:-1] + math.pi / 8]
        sh += [line([(-500, z), (380, z)]) for z in range(1830, 1880, 12)] if f == "-X" else []
        out.append(D(f, w, sh))
    out.append(D("+Y", 520, [rect(6680, 7220, 700, 1000), rect(6720, 7180, 1690, 1830, "mid"), line([(6600, 1600), (7297, 1600)])]))
    out.append(D("-Y", -520, [rect(6680, 7220, 700, 950), line([(6600, 1600), (7297, 1600)])]))
    return out


def g_sc_drive(p):
    return [B(6750, 7150, -640, -520, 1050, 1300), B(6900, 7000, -760, -640, 1000, 1350), C("Y", [6950, 0, 1175], 50, -1085, -760),
            C("Y", [6950, 0, 1175], 50, -1085, -1050, shade="mid")]


def g_backflush(p):
    return [H([(6700, 520, 1050), (7200, 520, 1050), (7200, 520, 1450), (6700, 520, 1450),
               (6850, 870, 1150), (7050, 870, 1150), (7050, 870, 1350), (6850, 870, 1350)]),
            D("+Y", 870, [rect(6880, 7020, 1180, 1320), circ(6950, 1250, 20, "dark")])]


def g_hpu(p):
    return [B(6400, 7250, -2100, -1400, 0, 700), C("Z", [6650, -1800, 0], 130, 700, 1200), B(6850, 7150, -1550, -1400, 700, 1180),
            B(6420, 6580, -1500, -1400, 850, 1130), C("Z", [7100, -1900, 0], 80, 700, 1150, shade="mid"),
            D("+Y", -1400, [rect(6450, 7200, 60, 640), rect(6500, 6560, 300, 600, "mid"), circ(7000, 1050, 30, "light")])]


def g_pump(p):
    out = [B(7491, 7911, -230, 230, 970, 1430), C("X", [0, 0, 1200], 180, 7476, 7491), C("X", [0, 0, 1200], 180, 7911, 7926),
           C("Y", [7701, 0, 1250], 40, -300, -230)]
    for f, w in (("+Y", 230), ("-Y", -230)):
        sh = [circ(7701, 1200, 195)] + [circ(7701 + 170 * math.cos(a), 1200 + 170 * math.sin(a), 12, "dark") for a in np.linspace(0, 2 * math.pi, 13)[:-1]]
        out.append(D(f, w, sh))
    out.append(D("+Z", 1430, [circ(x, y, 15, "dark") for x in (7560, 7842) for y in (-150, 150)]))
    return out


def g_cardan(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    out = [B(x0, x1, y0, y1, z0, z1)]
    mesh = [rect(-1200, -400, 1150, 1350)] + [line([(y, 1150), (y, 1350)]) for y in range(-1150, -400, 50)]
    out += [D("+X", x1, mesh), D("-X", x0, mesh)]
    out.append(D("+Z", z1, [rect(7580, 7820, -1200, -400)] + [line([(7580, y), (7820, y)]) for y in range(-1150, -400, 50)]))
    return out


def g_pump_gbx(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(x0, x1, y0, y1, z0, z1), D("+X", x1, [rect(-1700, -1350, 1000, 1400)]), D("-X", x0, [rect(-1700, -1350, 1000, 1400)])]


def g_pump_motor(p):
    c = [7701, -1525, 0]
    return [C("Z", c, 220, 1450, 1520), C("Z", c, 200, 1520, 2180), C("Z", c, 190, 2180, 2300, shade="mid")]


def g_melt_pipe(p):
    return [R("X", [0, 0, 1200], [(0, 0), (150, 0), (150, 117), (0, 117)], 8076),
            R("X", [0, 0, 1200], [(0, 0), (150, 0), (150, 117), (0, 117)], 8193),
            R("X", [0, 0, 1200], [(0, 0), (150, 0), (150, 116), (0, 116)], 8310)]


def g_mixer(p):
    return [R("X", [0, 0, 1200], [(0, 0), (150, 0), (150, 40), (140, 40), (140, 460), (150, 460), (150, 500), (0, 500)], 8426)]


def g_die_adapter(p):
    ring = [(8976, 150 * math.cos(a), 1200 + 150 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 25)[:-1]]
    rectp = [(9076, y, z) for y in (-250, 250) for z in (1020, 1380)]
    return [C("X", [0, 0, 1200], 150, 8926, 8976), H(ring + rectp), B(9076, 9126, -250, 250, 1020, 1380)]


HEATER_BANDS = [  # (x0, x1, r_in_profile_fn) -- 13 bands, see g_melt_bands
    ("cone", 5821, 5881), ("cone", 5886, 5946), ("cyl", 6486, 6556, 192), ("cyl", 7346, 7431, 162),
    ("cyl", 7966, 8036, 132), ("cyl", 8100, 8170, 140), ("cyl", 8216, 8286, 140), ("cyl", 8332, 8402, 140),
    ("cyl", 8480, 8550, 130), ("cyl", 8590, 8660, 130), ("cyl", 8700, 8770, 130), ("cyl", 8810, 8880, 130),
    ("cyl", 8931, 8971, 162)]


def _cone_r(x):
    h = x - 5746
    return 260 - (h - 60) * 60 / 140


def g_melt_bands(p):
    out = []
    for b in HEATER_BANDS:
        if b[0] == "cone":
            x0, x1 = b[1], b[2]
            r0, r1 = _cone_r(x0) + 10, _cone_r(x1) + 10
            out.append(R("X", [0, 0, 1200], [(0, 0), (r0, 0), (r1, x1 - x0), (0, x1 - x0)], x0, shade="light"))
        else:
            hid = b[1] >= 8076 and b[2] <= 8926
            out.append(C("X", [0, 0, 1200], b[3], b[1], b[2], shade="light", hidden=hid))
    return out


def g_die_half(p):
    o = p["outline_mm"]
    out = [PR("XZ", o["pts"], o["d0"], o["d1"])]
    return out


def g_end_plate(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    s = 1 if y0 > 0 else -1
    w = y1 if s > 0 else y0
    sh = [rect(9180, 9330, 1250, 1420), rect(9200, 9310, 1270, 1400, "mid"), line([(x0 + 5, 1200), (x1 - 5, 1200)])]
    sh += [circ(x, z, 10, "dark") for x in (9160, 9420, 9520) for z in (990, 1410)]
    return [B(x0, x1, y0, y1, z0, z1), D("+Y" if s > 0 else "-Y", w, sh)]


def g_deckles(p):
    out = []
    for s in (1, -1):
        a, b = (1375, 1525) if s > 0 else (-1525, -1375)
        out += [B(9380, 9560, a if s > 0 else b - 10, a + 10 if s > 0 else b, 1185, 1215, shade="mid"),
                C("Y", [9480, 0, 1200], 15, a, b), C("Y", [9480, 0, 1200], 20, (b - 30) if s > 0 else a, b if s > 0 else a + 30, shade="dark")]
    return out


def thermal_bolt_ys():
    return [-1181.1 + 25.4 * i for i in range(94)]


def g_thermal_bolts(p):
    out = []
    for y in thermal_bolt_ys():
        out.append(PI([(9448, y, 1296), (9348, y, 1440)], 12, shade="dark"))
    return out


def g_choker(p):
    out = []
    for i in range(33):
        y = -1200 + 75 * i
        out += [C("Z", [9185, y, 0], 12, 1450, 1490), C("Z", [9185, y, 0], 20, 1460, 1478, shade="mid"), C("Z", [9185, y, 0], 25, 1490, 1530, shade="dark")]
    return out


def g_die_heaters(p):
    out = []
    for z0, z1 in ((1330, 1440), (960, 1070)):
        for y0, y1 in ((-1250, -260), (260, 1250)):
            out.append(B(9050, 9126, y0, y1, z0, z1))
            out.append(D("-X", 9050, [rect(y0 + 20, y1 - 20, z0 + 15, z1 - 15)] + [circ(y, (z0 + z1) / 2, 12, "dark") for y in np.linspace(y0 + 80, y1 - 80, 4)]))
    return out


def g_lugs(p):
    # count 4 in parts.json but bbox only allows one X position per end plate: drawn 2 (design_issues)
    out = []
    for y in (1337, -1337):
        out += [C("Z", [9190, y, 0], 18, 1450, 1490), C("X", [0, y, 1530], 40, 9175, 9205)]
    return out


def g_die_cart(p):
    out = [B(9126, 9350, -1200, 1200, 180, 280)]
    for x in (9160, 9320):
        for y in (-1000, 1000):
            out.append(C("X", [0, y, 120], 60, x - 20, x + 20, shade="dark"))
    for s in (1, -1):
        ya, yb = (640, 760) if s > 0 else (-760, -640)
        out += [B(9180, 9300, ya, yb, 280, 880), B(9200, 9280, ya + 20, yb - 20, 880, 930, shade="mid"),
                B(9190, 9290, ya + 10 - 0, yb - 10, 930, 950)]
    out.append(B(9126, 9350, -1200, 1200, 880, 905))
    out.append(C("Y", [9240, 0, 820], 15, 760, 900, shade="dark"))
    out.append(D("+Y", 1200, [rect(9150, 9330, 200, 260)]))
    return out


def g_rails(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(9140, 9180, y0, y1, 0, 60, shade="mid"), B(9300, 9340, y0, y1, 0, 60, shade="mid")]


def g_die_jbox(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(x0, x1, y0, y1, z0, z1), D("-Y", y0, [rect(x0 + 15, x1 - 15, z0 + 15, z1 - 15), circ(9240, 820, 30, "dark"), rect(9190, 9290, 500, 560, "mid")])]


def g_cabinet(n, face="+Y", stripe=False):
    def f(p):
        x0, x1, y0, y1, z0, z1 = _bb(p)
        w = y1 if face == "+Y" else y0
        sh = [line([(x0, 100), (x1, 100)])]
        dw = (x1 - x0) / n
        for k in range(n):
            xa = x0 + k * dw
            sh += [rect(xa + 15, xa + dw - 15, 120, z1 - 20), rect(xa + dw - 70, xa + dw - 50, 1000, 1200, "dark"),
                   rect(xa + 120, xa + dw - 120, 250, 550)]
        if stripe:
            sh.append(rect(x0 + 15, x0 + 120, 120, z1 - 20, "mid"))
        return [B(x0, x1, y0, y1, z0, z1), D(face, w, sh)]
    return f


def g_machine_cab(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [B(x0, x1, y0, y1, z0, z1), D("+Y", y1, [rect(-5600, -5450, 200, 1900, "mid"), circ(-5300, 1400, 35, "dark")]),
            D("-X", x0, [rect(-350, -150, 200, 1900, "mid")]), D("-Y", y0, [rect(-5600, -5200, 100, 1900)])]


def g_tower(p):
    out = [C("Z", [-5400, 0, 0], 40, 2000, 2030), C("Z", [-5400, 0, 0], 18, 2030, 2400)]
    for k in range(4):
        out.append(C("Z", [-5400, 0, 0], 35, 2400 + 52 * k, 2452 + 52 * k, shade="light" if k % 2 else "mid"))
    out.append(C("Z", [-5400, 0, 0], 30, 2608, 2650, shade="dark"))
    return out


def g_hmi(p):
    c = math.cos(math.radians(15))
    s = math.sin(math.radians(15))
    pts = []
    for x in (-1700, -900):
        fb = (x, 1650, 1357)
        ft = (x, 1650 - 510 * s, 1357 + 510 * c)
        pts += [fb, ft, (x, fb[1] - 120 * c, fb[2] - 120 * s), (x, ft[1] - 120 * c, ft[2] - 120 * s)]
    return [B(-1450, -1150, 1400, 1650, 0, 20, shade="dark"), C("Z", [-1300, 1525, 0], 60, 20, 1290),
            C("Z", [-1300, 1525, 0], 80, 1290, 1340, shade="dark"), H(pts)]


def g_estops(p):
    out = []
    for x, y, z in p["positions_mm"]:
        out += [B(x - 50, x + 50, 1000, 1080, z - 70, z + 70), D("+Y", 1080, [circ(x, z, 30, "dark")])]
    return out


def g_floor(p):
    return []


def g_roll(p):
    c = p["center_mm"]
    return [R("Y", c, p["profile_mm"], -1600)]


def g_roll_stand(p):
    out = []
    o = p.get("outline_mm")
    pts = o["pts"] if o else [(9540, 60), (11200, 60), (11200, 3100), (10000, 3100), (9540, 2700), (9540, 1365), (9800, 1365), (9800, 1035), (9540, 1035)]
    a0, a1 = (o["d0"], o["d1"]) if o else (1400, 1750)
    for a, b in ((a0, a1), (-a1, -a0)):
        out.append(PR("XZ", pts, a, b))
    out += [B(10900, 11200, -1400, 1400, 60, 400), B(10900, 11200, -1400, 1400, 2700, 3100)]
    out.append(D("+Y", 1750, [rect(10200, 11100, 2800, 2950)]))
    out.append(D("-Y", -1750, [rect(10200, 11100, 2800, 2950)]))
    return out


def g_roll_drives(p):
    out = []
    for zc in (799, 1601, 2403):
        out += [B(9600, 9950, -2000, -1750, zc - 250, zc + 250), C("Y", [9776, 0, zc], 200, -2350, -2000)]
    return out


def g_roll_rails(p):
    return [B(9550, 12500, 1500, 1600, 0, 60), B(9550, 12500, -1600, -1500, 0, 60)]


def sheet_path():
    pts = [(9576, 1200), (9776, 1200)]
    for a in np.linspace(-90, 90, 19)[1:]:
        pts.append((9776 + 401 * math.cos(math.radians(a)), 1601 + 401 * math.sin(math.radians(a))))
    for a in np.linspace(270, 90, 19):
        pts.append((9776 + 401 * math.cos(math.radians(a)), 2403 + 401 * math.sin(math.radians(a))))
    pts.append((10200, 2804))
    return pts


def g_sheet(p):
    pts = sheet_path()
    out = []
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        out.append(Q3([(xa, -1050, za), (xb, -1050, zb), (xb, 1050, zb), (xa, 1050, za)], fill=False))
    return out


def g_frl(p):
    return [B(9000, 9150, -1240, -1220, 650, 900), C("Z", [9040, -1280, 0], 30, 680, 860), C("Z", [9110, -1280, 0], 30, 700, 860),
            C("Y", [9110, 0, 870], 25, -1330, -1305, shade="light")]


def g_flat_box(p):
    return [B(*_bb(p))]


SPECIAL = {
    "base_frame_drive": g_frame_seg, "base_frame_process": g_frame_seg, "base_feet": g_feet,
    "barrel_support_1": g_support, "barrel_support_2": g_support, "barrel_support_3": g_support,
    "melt_stand_sc": g_stand_sc, "melt_stand_pump": g_stand_pump, "melt_pipe_saddles": g_saddles,
    "pump_drive_pedestal": g_pedestal, "lantern": g_lantern, "gearbox": g_gearbox,
    "drive_coupling_guard": g_guard, "drive_motor": g_motor, "drive_motor_terminal_box": g_tbox,
    "drive_motor_base": g_motor_base, "lube_pump_motor": g_lube_pump, "lube_filter_duplex": g_lube_filter,
    "lube_oil_cooler": g_lube_cooler, "screws": g_screws, "barrel_heater_shells": g_heaters,
    "barrel_vent_atm": g_vent_atm, "barrel_vent_dome": g_dome, "barrel_thermocouples": g_tcs,
    "barrel_cw_valves": g_cw_valves, "barrel_cw_hoses": g_cw_hoses, "barrel_heater_jboxes": g_jboxes,
    "barrel_cable_tray": g_tray, "feed_throat": g_throat, "feed_hopper": g_hopper, "feed_flex_sleeve": g_sleeve,
    "feed_main_feeder": g_main_feeder, "feed_additive_feeder": g_add_feeder, "feed_platform_deck": g_deck,
    "feed_platform_columns_rear": g_columns, "feed_platform_columns_front": g_columns,
    "feed_platform_railing": g_railing, "feed_stair": g_stair, "feed_control_cabinet": g_feed_cab,
    "sidefeed_barrel": g_sf_barrel, "sidefeed_hopper": g_sf_hopper, "sidefeed_motor": g_sf_motor,
    "sidefeed_cart": g_sf_cart, "sidefeed_downpipe": g_sf_down, "sidefeed_feeder": g_sf_feeder,
    "vac_valve": g_vac_valve, "vac_bellows": g_bellows, "vac_pipe_support": g_vac_support,
    "vac_bleed_valve": g_bleed, "vac_gauge_dome": g_gauge_dome, "vac_separator": g_separator,
    "vac_drain": g_vac_drain, "vac_pump_unit": g_vac_pump, "vac_control_box": g_vac_ctrl,
    "melt_sensor_head": g_sensor_head, "melt_sensor_p2": g_sensor_one, "melt_sensor_p3": g_sensor_one,
    "melt_sensor_p4": g_sensor_one, "melt_sensor_die": g_sensor_die, "melt_startup_valve": g_startup,
    "melt_startup_cyl": g_startup_cyl, "melt_drain_chute": g_chute, "melt_purge_cart": g_purge,
    "melt_screen_changer": g_screen_changer, "melt_sc_drive": g_sc_drive, "melt_sc_backflush": g_backflush,
    "melt_hpu": g_hpu, "melt_gear_pump": g_pump, "melt_pump_cardan": g_cardan, "melt_pump_gearbox": g_pump_gbx,
    "melt_pump_motor": g_pump_motor, "melt_pipe": g_melt_pipe, "melt_static_mixer": g_mixer,
    "melt_die_adapter": g_die_adapter, "melt_heater_bands": g_melt_bands,
    "die_body_upper": g_die_half, "die_body_lower": g_die_half, "die_flex_lip": g_die_half,
    "die_end_plate_op": g_end_plate, "die_end_plate_rear": g_end_plate, "die_deckles": g_deckles,
    "die_thermal_bolts": g_thermal_bolts, "die_choker_bolts": g_choker, "die_heater_boxes": g_die_heaters,
    "die_lifting_lugs": g_lugs, "die_cart": g_die_cart, "die_cart_rails": g_rails, "die_junction_box": g_die_jbox,
    "ctrl_drive_cabinet": g_cabinet(6), "ctrl_heater_cabinet": g_cabinet(4, stripe=True),
    "ctrl_machine_cabinet": g_machine_cab, "ctrl_signal_tower": g_tower, "ctrl_hmi": g_hmi, "ctrl_estops": g_estops,
    "ctx_floor": g_floor, "ctx_roll_bottom": g_roll, "ctx_roll_middle": g_roll, "ctx_roll_top": g_roll,
    "ctx_roll_stand": g_roll_stand, "ctx_roll_drives": g_roll_drives, "ctx_roll_rails": g_roll_rails, "ctx_sheet": g_sheet,
    "util_frl": g_frl, "feed_control_cabinet": g_feed_cab,
}



# ------------------------------------------------------------------ data-driven geometry (parts.json rev. 2)
import re as _re


def _items(p):
    return list(zip(p.get("positions_mm", []), [p.get("item_mm")] * len(p.get("positions_mm", []))))


def _dia_list(p):
    return [float(v.replace(" ", "")) for v in _re.findall(r"Ø\s?(\d[\d ]*)", " ".join(p["details"]))]


def g_repeat(p):
    if item_axes(p) is not None:
        return g_tilted(p)
    out = []
    ax = p.get("axis", "Z")
    for (x, y, z), it in _items(p):
        if p["shape"] in ("cyl", "revolve"):
            i = AXI[ax]
            L = it[i]
            r = min(it[j] for j in range(3) if j != i) / 2
            c = [x, y, z]
            out.append(C(ax, c, r, c[i] - L / 2, c[i] + L / 2))
        else:
            out.append(B(x - it[0] / 2, x + it[0] / 2, y - it[1] / 2, y + it[1] / 2, z - it[2] / 2, z + it[2] / 2))
    return out


def g_paths(p):
    return [PI(path, p["radius_mm"]) for path in p["paths_mm"]]


def g_saddles2(p):
    out = []
    for (x, y, z), it in _items(p):
        x0, x1 = x - it[0] / 2, x + it[0] / 2
        hw = it[1] / 2
        z0, z1 = z - it[2] / 2, z + it[2] / 2
        out.append(B(x0, x1, y - hw, y + hw, z0, z0 + 30))
        out.append(PR("YZ", [(-hw, z0 + 30), (hw, z0 + 30), (hw, z1), (hw - 30, z1), (0, z0 + 40), (-hw + 30, z1), (-hw, z1)], x0, x1))
    return out


def g_valve_support(p):
    o = p["outline_mm"]
    return [PR("XZ", o["pts"], -260, -150), PR("XZ", o["pts"], 150, 260),
            B(5996, 6090, -260, -150, 925, 940, shade="mid"), B(5996, 6090, 150, 260, 925, 940, shade="mid")]


def g_stair2(p):
    b = _bb(p)
    y0, y1 = b[2], b[3]
    out = []
    band = [(-5700, 0), (-5400, 0), (-2700, 2700), (-2700, 3000)]
    out += [PR("XZ", band, y0, y0 + 10, shade="mid"), PR("XZ", band, y1 - 10, y1, shade="mid")]
    for k in range(1, 15):
        z = 200 * k
        out.append(B(z - 5650, min(z - 5400, -2700), y0 + 10, y1 - 10, z - 30, z))
    for y in (y0 + 21, y1 - 21):
        out.append(PI([(-5679, y, 1015), (-2721, y, 3985)], 21, shade="mid"))
        for x in (-5679, -4700, -3700, -2721):
            out.append(PI([(x, y, x + 5700), (x, y, x + 6700 - 21)], 18, shade="mid"))
    return out


def g_railing2(p):
    pts = p["outline_mm"]["pts"]
    b = _bb(p)
    x0, x1, y0, y1 = b[0] + 21, b[1] - 21, b[2] + 21, b[3] - 21
    cl = [(min(max(x, x0), x1), min(max(y, y0), y1)) for x, y in pts]
    out = []
    for z, r in ((b[5] - 21, 21), (3550, 17)):
        out.append(PI([(x, y, z) for x, y in cl], r, shade="mid"))
    posts = []
    for (xa, ya), (xb, yb) in zip(cl, cl[1:]):
        n = max(1, math.ceil(math.hypot(xb - xa, yb - ya) / 1500))
        for k in range(n):
            posts.append((xa + (xb - xa) * k / n, ya + (yb - ya) * k / n))
    posts.append(cl[-1])
    for x, y in posts:
        out.append(PI([(x, y, b[4]), (x, y, b[5] - 21)], 21, shade="mid"))
    for (xa, ya), (xb, yb) in zip(cl, cl[1:]):
        if abs(xa - xb) < 1:
            out.append(B(xa - 5, xa + 5, min(ya, yb), max(ya, yb), b[4], b[4] + 150, shade="mid"))
        else:
            out.append(B(min(xa, xb), max(xa, xb), ya - 5, ya + 5, b[4], b[4] + 150, shade="mid"))
    return out


def g_dome1(p):
    o = p["outline_mm"]
    out = [B(3820, 4420, -200, 200, 1455, 1460, shade="mid"), PR("XZ", o["pts"], o["d0"], o["d1"])]
    for x in (3970, 4270):
        out += [C("Y", [x, 0, 1880], 80, 200, 215), C("Y", [x, 0, 1880], 60, 215, 230, shade="light")]
    out.append(D("+Z", 2150, [circ(x, y, 15, "dark") for x in (3840, 4400) for y in (-170, 170)] + [circ(4120, 0, 95)]))
    for f, w in (("+Y", 230), ("-Y", -200)):
        out.append(D(f, w, [line([(3800, 2100), (4440, 2100)])]))
    return out


def g_dome2(p):
    o = p["outline_mm"]
    b = _bb(p)
    out = [B(1990, 2310, -140, 140, 1455, 1460, shade="mid"), PR("XZ", o["pts"], o["d0"], o["d1"]),
           C("Y", [2150, 0, 1800], 110, b[2], b[2] + 25), C("Y", [2150, 0, 1800], 57, b[2] + 25, o["d0"]),
           C("Y", [2150, 0, 1750], 60, o["d1"], o["d1"] + 15), C("Y", [2150, 0, 1750], 45, o["d1"] + 15, b[3], shade="light")]
    for f, w in (("+Y", o["d1"]), ("-Y", o["d0"])):
        out.append(D(f, w, [line([(1950, 1920), (2350, 1920)])]))
    out.append(D("+Z", 1960, [circ(x, y, 12, "dark") for x in (1975, 2325) for y in (-150, 150)]))
    return out


def g_vac_valve2(p):
    b = _bb(p)
    xc = (b[0] + b[1]) / 2
    return [C("Z", [xc, 0, 0], 100, 2150, 2260), B(xc - 60, xc + 60, b[2], -110, 2170, 2240)]


def _ripple(r, L, fl=12):
    prof = [(0, 0), (r, 0), (r, fl)]
    h = fl
    while h < L - fl - 16:
        prof += [(r * 0.86, h), (r * 0.86, h + 8), (r * 0.98, h + 8), (r * 0.98, h + 16)]
        h += 16
    prof += [(r, L - fl), (r, L), (0, L)]
    return prof


def g_bellows2(p):
    b = _bb(p)
    xc = (b[0] + b[1]) / 2
    zc = 2300
    return [C("Z", [xc, 0, 0], 110, 2260, 2275), PI([(xc, 0, 2275), (xc, 0, zc), (xc, -120, zc)], 84),
            R("Y", [xc, 0, zc], _ripple(110, 200), -320), C("Y", [xc, 0, zc], 110, b[2], -320)]


def g_vac_valve_b(p):  # zone-1 ball valve DN100 on the dome-2 outlet
    b = _bb(p)
    xc, zc = (b[0] + b[1]) / 2, (b[4] + b[5]) / 2
    return [C("Y", [xc, 0, zc], (b[5] - b[4]) / 2, b[2], b[3]), B(b[0], b[1], b[2] + 20, b[2] + 40, b[5] - 15, b[5], shade="dark")]


def g_bellows_b(p):
    b = _bb(p)
    xc, zc = (b[0] + b[1]) / 2, (b[4] + b[5]) / 2
    return [R("Y", [xc, 0, zc], _ripple(p["radius_mm"], b[3] - b[2], 10), b[2])]


def g_reg_valve(p):
    b = _bb(p)
    xc, yc = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2
    return [C("Z", [xc, yc, 0], 70, b[4] + 10, b[5] - 10), C("Y", [xc, 0, (b[4] + b[5]) / 2], 60, b[3] - 20, b[3], shade="dark")]


def g_gauge(p):
    b = _bb(p)
    xc, yc = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2
    r = (b[1] - b[0]) / 2
    return [C("Z", [xc, yc, 0], 10, b[4], b[5] - 2 * r), C("Y", [xc, 0, b[5] - r], r, b[2], b[3], shade="dark")]


def g_small_valve(p):
    b = _bb(p)
    xc, yc = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2
    return [C("Z", [xc, yc, 0], 25, b[4], b[5] - 50), B(b[0], b[1], yc - 20, yc + 20, b[5] - 50, b[5], shade="dark")]


def g_pipe_support2(p):
    b = _bb(p)
    xc, yc = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2
    return [C("Z", [xc, yc, 0], 50, 15, b[5] - 50), B(b[0], b[1], b[2], b[3], 0, 15, shade="dark"), B(b[0], b[1], b[2], b[3], b[5] - 50, b[5])]


def g_separator2(p):
    c = p["center_mm"]
    out = [R("Z", [c[0], c[1], 0], p["profile_mm"], 0)]
    h0 = p["profile_mm"][0][1]
    for a in (90, 210, 330):
        x, y = c[0] + 240 * math.cos(math.radians(a)), c[1] + 240 * math.sin(math.radians(a))
        out.append(B(x - 25, x + 25, y - 25, y + 25, 0, h0 + 60))
    return out


def g_drain2(p):
    b = _bb(p)
    xc, yc = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2
    r = (b[1] - b[0]) / 2
    return [C("Z", [xc, yc, 0], r, 50, 400), C("Z", [xc, yc, 0], 30, 400, b[5]), B(xc + 30, xc + 90, yc - 8, yc + 8, 415, 435, shade="dark"),
            B(xc - 10, xc + 10, yc - r, yc - r + 10, 0, 50)]


def g_vac_pump2(p):
    b = _bb(p)
    dy = b[3] - (-1500)
    o = []
    for q in g_vac_pump(p):
        if q.kind == "box":
            x0, x1, y0, y1, z0, z1 = q.data
            q.data = (x0, x1, y0 + dy, y1 + dy, z0, z1)
        elif q.kind == "cyl":
            a, c, r, t0, t1 = q.data
            c = list(c)
            c[1] += dy
            q.data = (a, c, r, t0, t1)
        elif q.kind == "decal":
            a, s_, w, sh = q.data
            q.data = (a, s_, w + dy, sh)
        o.append(q)
    return o


def g_hpu2(p):
    b = _bb(p)
    dy = b[3] - (-1400)
    o = []
    for q in g_hpu(p):
        if q.kind == "box":
            x0, x1, y0, y1, z0, z1 = q.data
            q.data = (x0, x1, y0 + dy, y1 + dy, z0, z1)
        elif q.kind == "cyl":
            a, c, r, t0, t1 = q.data
            c = list(c)
            c[1] += dy
            q.data = (a, c, r, t0, t1)
        elif q.kind == "decal":
            a, s_, w, sh = q.data
            q.data = (a, s_, w + dy, sh)
        o.append(q)
    return o


def g_sensors2(p):
    out = []
    for (x, y, z), it in _items(p):
        out += g_sensor(x, z - it[2] / 2, z + it[2] / 2)
    return out


def g_bands2(p):
    ds = _dia_list(p)[:len(p["positions_mm"])]
    out = []
    for i, ((x, y, z), it) in enumerate(_items(p)):
        r = (ds[i] / 2) if i < len(ds) else it[1] / 2
        out.append(C("X", [x, y, z], r, x - it[0] / 2, x + it[0] / 2, shade="light"))
    return out


def g_deckles2(p):
    out = []
    b = _bb(p)
    for (x, y, z), it in _items(p):
        a, c = y - it[1] / 2, y + it[1] / 2
        s_ = 1 if y > 0 else -1
        out += [C("Y", [x, 0, z], 15, a, c), C("Y", [x, 0, z], it[0] / 2, (c - 30) if s_ > 0 else a, c if s_ > 0 else a + 30, shade="dark"),
                B(b[0], b[1], (a - 0) if s_ > 0 else c - 10, a + 10 if s_ > 0 else c, z - 15, z + 15, shade="mid")]
    return out


def item_axes(p):
    """Per-item unit axis or None. With item_axis/item_axes, item_mm = [diameter, diameter, length along the axis]."""
    n = len(p.get("positions_mm", []))
    if p.get("item_axes"):
        ax_ = [np.array(a, float) for a in p["item_axes"]]
    elif p.get("item_axis"):
        ax_ = [np.array(p["item_axis"], float)] * n
    else:
        return None
    return [a / np.linalg.norm(a) for a in ax_]


def g_tilted(p, shade=None):
    axes = item_axes(p)
    out = []
    for ((x, y, z), it), a in zip(_items(p), axes):
        c = np.array([x, y, z], float)
        L, r = it[2], it[0] / 2
        if abs(abs(a[2]) - 1) < 1e-6:
            out.append(C("Z", [x, y, z], r, z - L / 2, z + L / 2, shade=shade))
        else:
            out.append(PI([c - a * L / 2, c + a * L / 2], r, shade=shade))
    return out


def g_tbolts2(p):
    if item_axes(p) is None:  # legacy data
        p = dict(p, item_axis=[-0.5765, 0, 0.8176], item_mm=[30, 30, p.get("item_length_mm", 170)])
    return g_tilted(p, shade="dark")


def g_choker2(p):
    out = []
    for (x, y, z), it in _items(p):
        z0, z1 = z - it[2] / 2, z + it[2] / 2
        r = it[0] / 2
        out += [C("Z", [x, y, 0], r * 0.55, z0, z0 + 40), C("Z", [x, y, 0], r * 0.85, z0 + 10, z0 + 28, shade="mid"),
                C("Z", [x, y, 0], r, z0 + 40, z1, shade="dark")]
    return out


def g_lugs2(p):
    out = []
    for (x, y, z), it in _items(p):
        z0, z1 = z - it[2] / 2, z + it[2] / 2
        out += [C("Z", [x, y, 0], 18, z0, z0 + 40), C("X", [0, y, z1 - 40], 40, x - 15, x + 15)]
    return out


def g_die_cart2(p):
    o = p["outline_mm"]
    b = _bb(p)
    out = [B(b[0], b[1], -1200, 1200, 180, 300)]
    for x in (8760, 9320):
        for y in (-1000, 1000):
            out.append(C("X", [0, y, 120], 60, x - 20, x + 20, shade="dark"))
    for s_ in (1, -1):
        ya, yb = (640, 760) if s_ > 0 else (-760, -640)
        out += [B(9180, 9320, ya, yb, 300, 880), B(9150, 9350, ya + 10, yb - 10, 930, 950)]
    out.append(B(9150, 9350, -1200, 1200, 880, 925))
    out.append(B(9165, 9335, -1150, 1150, 925, 930, shade="mid"))
    out.append(C("Y", [9250, 0, 820], 15, 760, 900, shade="dark"))
    out.append(D("+Y", 1200, [rect(b[0] + 30, b[1] - 30, 200, 280), line([(9150, 300), (9150, 880)])]))
    return out


def g_die_jbox2(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    xm = (x0 + x1) / 2
    return [B(x0, x1, y0, y1, z0, z1), D("+Y", y1, [rect(x0 + 20, x1 - 20, z0 + 60, z1 - 20), circ(xm, z1 - 150, 30, "dark"),
                                                   rect(x1 - 70, x1 - 50, 450, 600, "dark")]),
            D("+Z", z1, [circ(xm - 120, (y0 + y1) / 2, 40, "mid"), circ(xm, (y0 + y1) / 2, 40, "mid"), circ(xm + 120, (y0 + y1) / 2, 40, "mid")])]


def g_estops2(p):
    out = []
    for (x, y, z), it in _items(p):
        out += [B(x - it[0] / 2, x + it[0] / 2, y - it[1] / 2, y + it[1] / 2, z - it[2] / 2, z + it[2] / 2),
                D("+Y", y + it[1] / 2, [circ(x, z, 30, "dark")])]
        if y > 800:
            out.append(B(x - 30, x + 30, y + it[1] / 2 - 60 + 20, y + it[1] / 2 + 20, 650, z - it[2] / 2))
    return out


def g_frl2(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    w = x1 - x0
    return [B(x0, x1, y1 - 20, y1, z0, z1), C("Z", [x0 + w * 0.27, (y0 + y1 - 20) / 2, 0], min(30, w * 0.2), z0 + 30, z1 - 40),
            C("Z", [x0 + w * 0.73, (y0 + y1 - 20) / 2, 0], min(30, w * 0.2), z0 + 50, z1 - 40),
            C("Y", [x0 + w * 0.73, 0, z1 - 25], 22, y0, y0 + 25, shade="light")]


def g_roll_drives2(p):
    out = []
    for (x, y, z), it in _items(p):
        out += [B(x - 175, x + 175, y + 50, y + it[1] / 2, z - it[2] / 2, z + it[2] / 2), C("Y", [x, 0, z], 200, y - it[1] / 2, y + 50)]
    return out


def g_sheet2(p):
    w = p.get("width_mm", 2100) / 2
    pts = p["path_mm"]
    out = []
    for a, b2 in zip(pts, pts[1:]):
        out.append(Q3([(a[0], -w, a[2]), (b2[0], -w, b2[2]), (b2[0], w, b2[2]), (a[0], w, a[2])], fill=False))
    return out


def g_sleeves(p):
    ds = _dia_list(p)
    out = []
    for i, ((x, y, z), it) in enumerate(_items(p)):
        r = ds[i] / 2 if i < len(ds) else it[0] / 2
        out += [C("Z", [x, y, 0], r, z - it[2] / 2, z + it[2] / 2), C("Z", [x, y, 0], r, z - it[2] / 2 + 20, z - it[2] / 2 + 35, shade="mid"),
                C("Z", [x, y, 0], r, z + it[2] / 2 - 35, z + it[2] / 2 - 20, shade="mid")]
    return out


def g_box_door(face="+Y"):
    def f(p):
        x0, x1, y0, y1, z0, z1 = _bb(p)
        if face in ("+Y", "-Y"):
            w = y1 if face == "+Y" else y0
            return [B(x0, x1, y0, y1, z0, z1), D(face, w, [rect(x0 + 20, x1 - 20, z0 + 30, z1 - 20), rect(x1 - 60, x1 - 45, (z0 + z1) / 2 - 60, (z0 + z1) / 2 + 60, "dark")])]
        return [B(x0, x1, y0, y1, z0, z1)]
    return f


def g_tc2(p):
    if item_axes(p) is not None:
        out = []
        for q in g_tilted(p):
            out.append(q)
        # bayonet caps at the outer end of each couple
        for ((x, y, z), it), a in zip(_items(p), item_axes(p)):
            c = np.array([x, y, z], float) + a * (it[2] / 2 - 12)
            out.append(PI([c - a * 12, c + a * 12], it[0] / 2, shade="mid"))
        return out
    out = []
    for (x, y, z), it in _items(p):
        if abs(y) > 50:  # B1 couple inserted at 40 deg in the upper -Y quadrant
            d = np.array([0, math.sin(math.radians(-40)), math.cos(math.radians(40))])
            c = np.array([x, y, z], float)
            out.append(PI([c - d * it[2] / 2, c + d * it[2] / 2], it[0] / 2))
        else:
            out += [C("Z", [x, y, 0], it[0] / 2 * 0.8, z - it[2] / 2, z + it[2] / 2 - 25), C("Z", [x, y, 0], it[0] / 2, z + it[2] / 2 - 25, z + it[2] / 2, shade="mid")]
    return out


def g_body_bolts(p):
    out = []
    for (x, y, z), it in _items(p):
        r, h = it[0] / 2, it[2]
        if z > 1200:
            out.append(C("Z", [x, y, 0], r, z - h / 2, z + h / 2 + 0.5, shade="dark"))
        else:
            out.append(C("Z", [x, y, 0], r, z - h / 2 - 0.5, z + h / 2, shade="dark"))
    return out


def g_estop_post(p):
    x0, x1, y0, y1, z0, z1 = _bb(p)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    return [B(xm - 30, xm + 30, ym - 30, ym + 30, z0, z1 - 140), B(x0, x1, y0, y1, z1 - 140, z1, shade="mid"),
            D("+Y", y1, [circ(xm, z1 - 70, 30, "dark")])]


def g_estop_die(p):
    o = p["outline_mm"]
    x0, x1, y0, y1, z0, z1 = _bb(p)
    return [PR(o["plane"], o["pts"], o["d0"], o["d1"]), D("+Y", y1, [circ((x0 + x1) / 2, z1 - 70, 30, "dark")])]


SPECIAL.update({
    "die_body_bolts": g_body_bolts, "ctrl_estop_melt": g_estop_post, "ctrl_estop_die": g_estop_die,
    "melt_pipe_saddles": g_saddles2, "melt_valve_support": g_valve_support, "feed_stair": g_stair2,
    "feed_platform_railing": g_railing2, "barrel_vent_dome": g_dome1, "barrel_vent_dome_2": g_dome2,
    "vac_valve": g_vac_valve2, "vac_bellows": g_bellows2, "vac_valve_2": g_vac_valve_b, "vac_bellows_2": g_bellows_b,
    "vac_reg_valve_2": g_reg_valve, "vac_gauge_dome": g_gauge, "vac_gauge_dome_2": g_gauge, "vac_bleed_valve": g_small_valve,
    "vac_pipe_support": g_pipe_support2, "vac_separator": g_separator2, "vac_drain": g_drain2, "vac_pump_unit": g_vac_pump2,
    "melt_hpu": g_hpu2, "melt_sensor_head": g_sensors2, "melt_sensor_die": g_sensors2, "melt_heater_bands": g_bands2,
    "die_deckles": g_deckles2, "die_thermal_bolts": g_tbolts2, "die_choker_bolts": g_choker2, "die_lifting_lugs": g_lugs2,
    "die_cart": g_die_cart2, "die_junction_box": g_die_jbox2, "ctrl_estops": g_estops2, "util_frl": g_frl2, "util_frl_2": g_frl2,
    "ctx_roll_drives": g_roll_drives2, "ctx_sheet": g_sheet2, "feed_feeder_sleeves": g_sleeves,
    "ctrl_die_bolt_cabinet": g_cabinet(1), "melt_heater_jbox": g_box_door("+Y"), "barrel_thermocouples": g_tc2,
})
for _k in ("barrel_cw_hoses", "die_cart_rails", "ctx_roll_rails"):
    SPECIAL.pop(_k, None)


def part_prims(pid):
    p = P[pid]
    if pid in SPECIAL:
        prims = SPECIAL[pid](p)
    elif p.get("paths_mm"):
        prims = g_paths(p)
    elif p.get("positions_mm") and p.get("item_mm") and not p["id"].startswith("barrel_joint"):
        prims = g_repeat(p)
    elif p["id"].startswith("barrel_b"):
        prims = g_barrel(p)
    elif p["id"].startswith("barrel_joint"):
        prims = g_joint(p)
    elif p["id"].startswith("barrel_cover"):
        prims = g_cover(p)
    elif p.get("path_mm"):
        prims = g_pipe(p)
    elif p["shape"] == "revolve":
        prims = g_rev(p)
    elif p["shape"] == "cyl":
        prims = g_cyl_axis(p)
    elif p.get("outline_mm"):
        o = p["outline_mm"]
        prims = [PR(o["plane"], o["pts"], o["d0"], o["d1"])]
    else:
        prims = g_box(p)
    for q in prims:
        q.part = pid
    return prims


_CACHE = {}


def all_prims(ids=None):
    ids = ids or ORDER
    out = []
    for pid in ids:
        if pid not in _CACHE:
            _CACHE[pid] = part_prims(pid)
        out += _CACHE[pid]
    return out


# ---------------------------------------------------------------------------------- projection
def _hull2(pts):
    pts = sorted(set((round(a, 4), round(b, 4)) for a, b in pts))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _item(kind, geo, depth, prim, fill=None, lw=None):
    return {"type": kind, "geo": geo, "depth": depth, "part": prim.part, "fill": prim.fill if fill is None else fill,
            "lw": lw or prim.lw, "shade": prim.shade, "sil": prim.sil, "hidden": prim.hidden, "ls": prim.ls}


def project(prim, v):
    k = prim.kind
    d = prim.data
    out = []
    fill_ok = prim.fill and v.ls not in prim.nofill
    if k == "box":
        x0, x1, y0, y1, z0, z1 = d
        cs = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
        uvs = [v.uv(c) for c in cs]
        u0, u1 = min(a for a, b in uvs), max(a for a, b in uvs)
        w0, w1 = min(b for a, b in uvs), max(b for a, b in uvs)
        dep = min(v.depth(c) for c in cs)
        out.append(_item("poly", [(u0, w0), (u1, w0), (u1, w1), (u0, w1)], dep, prim, fill_ok))
    elif k == "cyl":
        a, c, r, t0, t1 = d
        if abs(v.L[a]) > 0.5:
            dep = min(v.L[a] * t0, v.L[a] * t1)
            out.append(_item("circle", (v.uv(c), r), dep, prim, fill_ok))
        else:
            p0, p1 = list(c), list(c)
            p0[a], p1[a] = t0, t1
            (ua, va), (ub, vb) = v.uv(p0), v.uv(p1)
            if abs(v.R[a]) > 0.5:
                poly_ = [(min(ua, ub), va - r), (max(ua, ub), va - r), (max(ua, ub), va + r), (min(ua, ub), va + r)]
            else:
                poly_ = [(ua - r, min(va, vb)), (ua + r, min(va, vb)), (ua + r, max(va, vb)), (ua - r, max(va, vb))]
            out.append(_item("poly", poly_, v.depth(c) - r, prim, fill_ok))
    elif k == "rev":
        a, c, prof, t0 = d
        rmax = max(q[0] for q in prof)
        if abs(v.L[a]) > 0.5:
            srt = sorted(prof, key=lambda q: v.L[a] * (t0 + q[1]))
            dep = v.L[a] * (t0 + srt[0][1])
            out.append(_item("circle", (v.uv(c), rmax), dep, prim, fill_ok))
            best = -1
            for r_, h in srt:
                if r_ > best + 0.5:
                    if 0 < r_ < rmax - 0.5:
                        out.append(_item("circle", (v.uv(c), r_), dep - 0.01, prim, False, "thin"))
                    best = r_
        else:
            W = v.U if abs(v.R[a]) > 0.5 else v.R
            base = np.array(c, float)
            plus, minus = [], []
            for r_, h in prof:
                q = base.copy()
                q[a] = t0 + h
                plus.append(v.uv(q + r_ * W))
                minus.append(v.uv(q - r_ * W))
            pts = plus + minus[::-1]
            ded = [pts[0]]
            for q in pts[1:]:
                if abs(q[0] - ded[-1][0]) > 1e-6 or abs(q[1] - ded[-1][1]) > 1e-6:
                    ded.append(q)
            out.append(_item("poly", ded, v.depth(c) - rmax, prim, fill_ok))
            hs = sorted(set(q[1] for q in prof))
            for h in hs[1:-1]:
                rr = max(q[0] for q in prof if abs(q[1] - h) < 1e-6)
                if rr <= 0:
                    continue
                q = base.copy()
                q[a] = t0 + h
                out.append(_item("line", [v.uv(q - rr * W), v.uv(q + rr * W)], v.depth(c) - rmax - 0.01, prim, False, "thin"))
    elif k == "prism":
        plane, pts, d0, d1, sharp = d
        pa, pb = {"XZ": (0, 2), "YZ": (1, 2), "XY": (0, 1)}[plane]
        e = 3 - pa - pb

        def w3(pq, de):
            q = [0.0, 0.0, 0.0]
            q[pa], q[pb], q[e] = pq[0], pq[1], de
            return q
        if abs(v.L[e]) > 0.5:
            dep = min(v.L[e] * d0, v.L[e] * d1)
            out.append(_item("poly", [v.uv(w3(q, d0)) for q in pts], dep, prim, fill_ok))
        else:
            di, vi = (0, 1) if abs(v.L[pa]) > 0.5 else (1, 0)  # index in pq of depth axis / visible axis
            dax = (pa, pb)[di]
            sL = v.L[dax]
            vis = [q[vi] for q in pts]
            dep_pts = [sL * q[di] for q in pts]
            lo, hi = min(vis), max(vis)
            corners = []
            for val in (lo, hi):
                for de in (d0, d1):
                    q = [0.0, 0.0]
                    q[vi] = val
                    q[di] = pts[0][di]
                    corners.append(v.uv(w3(q, de)))
            hull = _hull2(corners)
            dep = min(dep_pts)
            n = len(pts)

            def env_at(val):
                ds = []
                for j in range(n):
                    q0, q1 = pts[j], pts[(j + 1) % n]
                    if min(q0[vi], q1[vi]) - 1e-6 <= val <= max(q0[vi], q1[vi]) + 1e-6:
                        if abs(q1[vi] - q0[vi]) < 1e-9:
                            ds += [sL * q0[di], sL * q1[di]]
                        else:
                            t = (val - q0[vi]) / (q1[vi] - q0[vi])
                            ds.append(sL * (q0[di] + t * (q1[di] - q0[di])))
                return min(ds) if ds else dep
            cuts = sorted(set(round(q, 3) for q in vis))
            if len(cuts) > 2 and len(cuts) < 40:
                # depth strips: each band between vertex coordinates gets its own front depth (fill only),
                # the silhouette outline is a separate unfilled item
                for a_, b_ in zip(cuts, cuts[1:]):
                    sd = min(env_at(a_ + 1e-4), env_at(b_ - 1e-4), env_at((a_ + b_) / 2))
                    cs = []
                    for val in (a_, b_):
                        for de in (d0, d1):
                            q = [0.0, 0.0]
                            q[vi] = val
                            q[di] = pts[0][di]
                            cs.append(v.uv(w3(q, de)))
                    it = _item("poly", _hull2(cs), sd, prim, fill_ok)
                    it["noline"] = True
                    it["sil"] = prim.sil
                    out.append(it)
                ol = _item("poly", hull, dep - 0.02, prim, False)
                ol["sil"] = False
                out.append(ol)
            else:
                out.append(_item("poly", hull, dep, prim, fill_ok))
            done = set()
            for i in range(n):
                val = vis[i]
                if abs(val - lo) < 0.5 or abs(val - hi) < 0.5:
                    continue
                a0, a1, a2 = pts[i - 1], pts[i], pts[(i + 1) % n]
                v1 = (a1[0] - a0[0], a1[1] - a0[1])
                v2 = (a2[0] - a1[0], a2[1] - a1[1])
                ang = math.degrees(abs(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])))
                if ang < sharp:
                    continue
                # front envelope at this visible coordinate
                ds = []
                for j in range(n):
                    q0, q1 = pts[j], pts[(j + 1) % n]
                    if min(q0[vi], q1[vi]) - 1e-6 <= val <= max(q0[vi], q1[vi]) + 1e-6:
                        if abs(q1[vi] - q0[vi]) < 1e-9:
                            ds += [sL * q0[di], sL * q1[di]]
                        else:
                            t = (val - q0[vi]) / (q1[vi] - q0[vi])
                            ds.append(sL * (q0[di] + t * (q1[di] - q0[di])))
                if dep_pts[i] > min(ds) + 0.5:
                    continue
                key = round(val, 1)
                if key in done:
                    continue
                done.add(key)
                q = [0.0, 0.0]
                q[vi] = val
                q[di] = pts[i][di]
                out.append(_item("line", [v.uv(w3(q, d0)), v.uv(w3(q, d1))], dep_pts[i] - 0.01, prim, False, "thin"))
    elif k == "hull":
        uvs = [v.uv(q) for q in d]
        out.append(_item("poly", _hull2(uvs), min(v.depth(q) for q in d), prim, fill_ok))
    elif k == "pipe":
        path, r = d
        path = [np.array(q, float) for q in path]
        n = len(path)
        for i in range(n - 1):
            a, b = path[i], path[i + 1]
            dv = b - a
            L = np.linalg.norm(dv)
            if L < 1e-6:
                continue
            dn = dv / L
            if abs(dn @ v.L) > 0.999:
                out.append(_item("circle", (v.uv(a), r), min(v.depth(a), v.depth(b)), prim, fill_ok))
                continue
            ec = r * abs(float(dn @ v.L))  # end discs seen obliquely: extend by their projected half-size
            a2 = a - dn * r if i > 0 else a - dn * ec
            b2 = b + dn * r if i < n - 2 else b + dn * ec
            (ua, va), (ub, vb) = v.uv(a2), v.uv(b2)
            du, dw = ub - ua, vb - va
            l2 = math.hypot(du, dw)
            if l2 < 1e-9:
                continue
            nu, nw = -dw / l2 * r, du / l2 * r
            out.append(_item("poly", [(ua + nu, va + nw), (ub + nu, vb + nw), (ub - nu, vb - nw), (ua - nu, va - nw)],
                             min(v.depth(a), v.depth(b)) - r, prim, fill_ok))
    elif k == "lines":
        out.append(_item("line", [v.uv(q) for q in d], min(v.depth(q) for q in d) - 1, prim, False))
    elif k == "poly3":
        uvs = [v.uv(q) for q in d]
        area = 0.0
        for i in range(len(uvs)):
            (x0_, y0_), (x1_, y1_) = uvs[i - 1], uvs[i]
            area += x0_ * y1_ - x1_ * y0_
        dep = min(v.depth(q) for q in d)
        if abs(area) < 1e-3:
            hull = _hull2(uvs)
            far = max(((p_, q_) for p_ in hull for q_ in hull), key=lambda t: math.dist(t[0], t[1])) if len(hull) > 1 else (uvs[0], uvs[0])
            out.append(_item("line", list(far), dep, prim, False))
        else:
            out.append(_item("poly", uvs, dep, prim, fill_ok))
    elif k == "decal":
        a, s, w, shapes = d
        if s * v.L[a] >= 0:
            return out
        dep = v.L[a] * w - 0.5
        oth = [i for i in range(3) if i != a]
        for typ, geo, f in shapes:
            def to3(pq):
                q = [0.0, 0.0, 0.0]
                q[a], q[oth[0]], q[oth[1]] = w, pq[0], pq[1]
                return q
            if typ == "circle":
                pc, qc, r_ = geo
                it = _item("circle", (v.uv(to3((pc, qc))), r_), dep, prim, f is not None)
            elif typ == "poly":
                it = _item("poly", [v.uv(to3(q)) for q in geo], dep, prim, f is not None)
            else:
                it = _item("line", [v.uv(to3(q)) for q in geo], dep, prim, False)
            it["shade"] = f if f else prim.shade
            out.append(it)
    return out


def scene(view, ids=None, exclude=()):
    """All projected items for parts `ids`, painter-sorted (far first)."""
    v = VIEWS[view] if isinstance(view, str) else view
    items = []
    seq = 0
    for prim in all_prims(ids):
        if prim.part in exclude:
            continue
        for it in project(prim, v):
            it["seq"] = seq
            seq += 1
            items.append(it)
    items.sort(key=lambda it: (-it["depth"], it["seq"]))
    return items


def item_bounds(it):
    if it["type"] == "circle":
        (u, w), r = it["geo"]
        return u - r, u + r, w - r, w + r
    xs = [q[0] for q in it["geo"]]
    ys = [q[1] for q in it["geo"]]
    return min(xs), max(xs), min(ys), max(ys)


def bbox_uv(pid, v):
    """Projected bbox rectangle of a part (u0, u1, v0, v1) in world-mm screen coordinates."""
    b = P[pid]["bbox_mm"]
    cs = [(x, y, z) for x in b[0:2] for y in b[2:4] for z in b[4:6]]
    uvs = [v.uv(c) for c in cs]
    return min(a for a, _ in uvs), max(a for a, _ in uvs), min(c for _, c in uvs), max(c for _, c in uvs)
