#!/usr/bin/env python3
"""Sheet 02 – processing section: barrel layout, zones, screw configuration, cooling water, section A-A, details, covers."""
import math

import numpy as np

from geom import P, NUM, ORDER
from sheet import Sheet, VP, fmt, PT, wrap, sheet_parts_list, MIN_FS
import drafting as dft

BARRELS = [("B1", 0, 676, "4D", "cấp liệu (feed)", "miệng nạp 360×300", "áo nước"),
           ("B2", 676, 1690, "6D", "nóng chảy + cấp phụ", "cửa bên +Y 340×260", "2 băng nhiệt + nước"),
           ("B3", 1690, 2704, "6D", "chân không vùng 1", "lỗ đỉnh 320×280", "2 băng nhiệt + nước"),
           ("B4", 2704, 3718, "6D", "trộn, nút nhựa", "kín", "2 băng nhiệt + nước"),
           ("B5", 3718, 4732, "6D", "chân không vùng 2", "lỗ đỉnh 520×280", "2 băng nhiệt + nước"),
           ("B6", 4732, 5746, "6D", "tăng áp (metering)", "kín; cổng dự phòng", "2 băng nhiệt + nước")]
# screw element table from parts.json screws.details (designer, after review M8)
SCREW = [(0, 1100, "conv", "vận chuyển 1,5D"), (1100, 1560, "conv", "1,5D dưới cửa bên"), (1560, 1880, "kb45", "KB 45°/5"),
         (1880, 1950, "kb90", "KB 90°"), (1950, 2420, "conv2", "1,5D bước rộng – vùng 1"), (2420, 2900, "conv1", "1D"),
         (2900, 3260, "kb45", "KB 45°/5"), (3260, 3380, "kb90", "KB 90°"), (3380, 3620, "conv1", "1D"), (3620, 3720, "lh", "LH"),
         (3720, 4450, "conv2", "1,5D bước rộng – vùng 2"), (4450, 5100, "conv1", "1D"), (5100, 5746, "conv075", "0,75D")]
IDS_ELEV = [q for q in ["base_frame_drive", "base_frame_process", "base_drip_tray", "barrel_support_1", "barrel_support_2",
                        "barrel_support_3", "lantern", "barrel_b1", "barrel_b2", "barrel_b3", "barrel_b4", "barrel_b5", "barrel_b6",
                        "barrel_joint_1", "barrel_joint_2", "barrel_joint_3", "barrel_joint_4", "barrel_joint_5", "barrel_heater_shells",
                        "screws", "barrel_vent_dome_2", "barrel_vent_dome", "vac_valve", "vac_gauge_dome", "vac_valve_2",
                        "vac_gauge_dome_2", "vac_bellows", "barrel_thermocouples", "feed_throat", "feed_hopper", "sidefeed_adapter",
                        "barrel_heater_jboxes", "barrel_cable_tray", "melt_head_adapter", "melt_rupture_disc", "melt_sensor_head",
                        "barrel_cover_c1", "barrel_cover_c2", "barrel_cover_c3", "barrel_cover_c4", "barrel_cover_c5",
                        "barrel_cover_c6"] if q in P]
COVERS = ["barrel_cover_c%d" % i for i in range(1, 7)]
CW = [q for q in ["base_frame_drive", "base_frame_process", "barrel_support_1", "barrel_support_2", "barrel_support_3", "barrel_b1",
                  "barrel_b2", "barrel_b3", "barrel_b4", "barrel_b5", "barrel_b6", "barrel_joint_1", "barrel_joint_2", "barrel_joint_3",
                  "barrel_joint_4", "barrel_joint_5", "barrel_heater_shells", "barrel_cw_supply", "barrel_cw_return", "barrel_cw_valves",
                  "barrel_cw_hoses", "util_cw_supply_riser", "util_cw_return_riser", "util_cw_throat_hoses", "util_cw_sidefeed_hoses",
                  "feed_throat", "sidefeed_adapter", "lantern", "melt_head_adapter", "ctrl_estops"] if q in P]


def screw_strip(sh, vp, y0, h):
    ax = sh.ax
    k = vp.k
    for x0, x1, kind, lab in SCREW:
        a, _ = vp.P((x0, 0, 0))
        b, _ = vp.P((x1, 0, 0))
        lo, hi = min(a, b), max(a, b)
        dft.poly(ax, [(lo, y0), (hi, y0), (hi, y0 + h), (lo, y0 + h)], fc="white", lw=0.3)
        if kind.startswith("conv") or kind == "lh":
            pitch = {"conv": 254, "conv1": 169, "conv2": 254, "conv075": 127, "lh": 169}[kind] / k
            sgn = -1 if kind == "lh" else 1
            x = lo + pitch / 2
            while x < hi:
                xl, xr = x - sgn * pitch * 0.35, x + sgn * pitch * 0.35
                sh.line([(max(lo, min(hi, xl)), y0 + 0.3), (max(lo, min(hi, xr)), y0 + h - 0.3)], lw=0.3)
                x += pitch / 2
            if kind == "lh":
                dft.poly(ax, [(lo, y0), (hi, y0), (hi, y0 + h), (lo, y0 + h)], fc="none", lw=0.25, hatch="xxx")
        elif kind.startswith("kb"):
            w = 34 / k
            n = int((hi - lo) / w)
            for i in range(n):
                off = (i % 3) * h * 0.18 if kind == "kb45" else (i % 2) * h * 0.3
                dft.poly(ax, [(lo + i * w, y0 + off * 0.5), (lo + (i + 1) * w, y0 + off * 0.5),
                              (lo + (i + 1) * w, y0 + h - (h * 0.36 - off * 0.5)), (lo + i * w, y0 + h - (h * 0.36 - off * 0.5))],
                         fc="#d9d9d9", lw=0.2)


def barrel_section(sh, cx, cy, kk, notch=False, fitting=False, heater=True, nuts=True):
    """Transverse section through a 6D barrel at a heater shell (scale 1:kk). Returns sheet points for labels."""
    ax = sh.ax
    body = dft.circle_pts(cx, cy, 260 / kk, 120)
    bore = dft.fig8(cx, cy, 142, 84.5, kk)
    cool = [dft.circle_pts(cx + 215 / kk * math.cos(math.radians(22.5 + 45 * i)), cy + 215 / kk * math.sin(math.radians(22.5 + 45 * i)),
                           9 / kk, 24) for i in range(8)]
    if nuts:
        dft.circ(ax, (cx, cy), 320 / kk, lw=0.3, z=8)  # Ø640 flange beyond the cut
        dft.circ(ax, (cx, cy), 280 / kk, lw=0.13, ls="center", z=8)
        for i in range(20):
            a = math.radians(9 + 18 * i)
            dft.poly(ax, dft.hexagon(cx + 280 / kk * math.cos(a), cy + 280 / kk * math.sin(a), 36 / kk / 1.15, a), fc="white", lw=0.25, z=9)
    if heater:
        ring = dft.circle_pts(cx, cy, 290 / kk, 160)
        if notch:  # 50 mm notch at 45 deg lower +Y (sheet: right = +Y, up = +Z)
            a0, a1 = math.radians(-45 - 6), math.radians(-45 + 6)
            ring = [(cx + 290 / kk * math.cos(t), cy + 290 / kk * math.sin(t)) for t in np.linspace(a1, a0 + 2 * math.pi, 150)]
            ring += [(cx + 260 / kk * math.cos(t), cy + 260 / kk * math.sin(t)) for t in np.linspace(a0 + 2 * math.pi, a1, 150)]
            dft.poly(ax, ring, hatch="xx", lw=0.3, z=10)
        else:
            dft.region(ax, ring, [body], hatch="xx", lw=0.3, z=10)
    dft.region(ax, body, [bore] + cool, hatch="////", lw=0.5, z=11)
    for sgn, rot in ((-1, 0.0), (1, math.pi / 2)):
        prof = dft.erdmenger(cx + sgn * 71 / kk, cy, 83.75, 142, rot=rot, k=kk, n=240)
        dft.region(ax, prof, [dft.circle_pts(cx + sgn * 71 / kk, cy, 36 / kk, 40)], hatch="\\\\\\\\", lw=0.35, z=12)
        dft.circ(ax, (cx + sgn * 71 / kk, cy), 36 / kk, lw=0.3, z=13, hatch="||||", fc="white")
    if fitting:
        a = math.radians(-45)
        p0 = (cx + 215 / kk * math.cos(a), cy + 215 / kk * math.sin(a))
        p1 = (cx + 262 / kk * math.cos(a), cy + 262 / kk * math.sin(a))
        p2 = (cx + 330 / kk * math.cos(a), cy + 330 / kk * math.sin(a))
        sh.line([p0, p1], lw=0.6, ls="hidden")
        d = (math.cos(a), math.sin(a))
        n = (-d[1], d[0])
        w = 11 / kk
        dft.poly(ax, [(p1[0] + n[0] * w, p1[1] + n[1] * w), (p2[0] + n[0] * w, p2[1] + n[1] * w), (p2[0] - n[0] * w, p2[1] - n[1] * w),
                      (p1[0] - n[0] * w, p1[1] - n[1] * w)], fc="#bfbfbf", lw=0.35, z=14)
        p3 = (p2[0] + 60 / kk, p2[1] - 40 / kk)
        sh.line([p2, p3, (p3[0] + 60 / kk, p3[1])], lw=1.2, c="#1f5fbf", z=14)
        return p1, p2
    return None


def main():
    sh = Sheet(2, "barrel", "Đoạn gia công (processing section)", size="A0", scale="1:10; 1:5; 1:20; 1:50",
               subtitle="Xi lanh 1×4D + 5×6D, cấu hình trục vít, vùng chức năng, nước làm mát, mặt cắt lỗ số 8, mối nối bích Ø640, gối đỡ, vỏ che")
    ax = sh.ax
    k = 10
    uc = (-6050 + 400) / 2
    el = VP(sh, "front", k, 55 + 6450 / k / 2, 675, uc, 1200, clip=(-6050, 400, 600, 2250))
    el.draw(IDS_ELEV, phantom=COVERS, thick=0.45, thin=0.2, floor=False)
    eb = el.box()
    el.cline((-400, 0, 1200), (6050, 0, 1200))
    sh.heading((eb[0] + eb[1]) / 2, eb[3] + 36, "A. Bố trí xi lanh – hình chiếu đứng, vỏ che C1…C6 nét phantom", "1:10")
    el.balloons(["barrel_b1", "barrel_b2", "barrel_b3", "barrel_b4", "barrel_b5", "barrel_b6", "barrel_joint_1", "barrel_joint_2",
                 "barrel_joint_3", "barrel_joint_4", "barrel_joint_5", "barrel_heater_shells", "barrel_vent_dome_2", "barrel_vent_dome",
                 "barrel_thermocouples", "feed_throat", "feed_hopper", "melt_head_adapter", "lantern", "vac_valve", "vac_valve_2",
                 "sidefeed_adapter", "vac_gauge_dome", "vac_gauge_dome_2"], sides=("top",), offset=6, rows=2)
    el.balloons(["barrel_support_1", "barrel_support_2", "barrel_support_3", "barrel_heater_jboxes", "barrel_cable_tray",
                 "base_drip_tray", "screws"] + COVERS, sides=("bottom",), offset=4, rows=1)
    dft.section_marker(sh, el.P((2984, 0, 1560)), el.P((2984, 0, 840)), "A", (1, 0))
    dft.detail_marker(sh, el.P((2704, 0, 1350)), 250 / k, "B")
    dft.detail_marker(sh, el.P((3211, 0, 860)), 250 / k, "C")
    for (a, b, t) in ((160, 520, "nạp 360"), (1990, 2310, "lỗ 320"), (3860, 4380, "lỗ 520")):
        sh.dim(el.P((a, 0, 1520)), el.P((b, 0, 1520)), el.P((0, 0, 2215))[1], "h", text=t)
    for z, t in ((940, "940"), (1200, "1 200"), (1520, "1 520 bích Ø640"), (1650, "1 650 vỏ che"), (2150, "2 150 vòm 2")):
        x, y = el.P((-400, 0, z))
        sh.line([(x, y), (x + 3, y)], lw=0.18)
        sh.text(x + 4, y, t, ha="left", va="center")
    # ---------------------------------------------------------------- screw strip + zone table aligned in X
    ys = 562
    screw_strip(sh, el, ys, 12)
    sh.text(eb[0], ys + 20, "Cấu hình trục vít (screw configuration) theo parts.json – cùng tỷ lệ X với hình A", 11, ha="left",
            va="bottom", weight="bold")
    for i, (x0, x1, kind, lab) in enumerate(SCREW):
        xm = el.P(((x0 + x1) / 2, 0, 0))[0]
        if x1 - x0 < 300:
            sh.text(xm, ys - 1.0, lab, ha="center", va="top")
        else:
            sh.text(xm, ys + 13, lab, ha="center", va="bottom")
    yt = 540
    rh = 7.0
    labels = ["Đoạn", "Dài", "Chức năng", "Lỗ / cửa", "Nhiệt"]
    for i, r in enumerate(labels):
        sh.text(eb[1] + 2, yt - rh * (i + 0.5), r, ha="left", va="center", weight="bold")
    for name, x0, x1, ln, fn, op, ht in BARRELS:
        a = el.P((x0, 0, 0))[0]
        b = el.P((x1, 0, 0))[0]
        lo, hi = min(a, b), max(a, b)
        dft.poly(ax, [(lo, yt - rh * 5), (hi, yt - rh * 5), (hi, yt), (lo, yt)], fc="none", lw=0.3)
        for i in range(1, 5):
            sh.line([(lo, yt - rh * i), (hi, yt - rh * i)], lw=0.13)
        for i, v in enumerate([name, f"{ln} = {x1 - x0}", fn, op, ht]):
            lines = wrap(v, hi - lo - 2, MIN_FS)
            sh.text((lo + hi) / 2, yt - rh * (i + 0.5), lines[0] if len(lines) == 1 else v[: int((hi - lo) / 2)], 11 if i == 0 else MIN_FS,
                    ha="center", va="center", weight="bold" if i == 0 else "normal")
    xs = [0, 676, 1690, 2704, 3718, 4732, 5746]
    yd = yt - rh * 5 - 8
    for a, b in zip(xs, xs[1:]):
        sh.dim(el.P((a, 0, 0)), el.P((b, 0, 0)), yd, "h", value=b - a, ext=False)
    sh.dim(el.P((0, 0, 0)), el.P((5746, 0, 0)), yd - 10, "h", text="34D = 5 746 (L/D 34, D = 169)", ext=False)
    # ---------------------------------------------------------------- I1: cooling-water strip (no covers)
    cw = VP(sh, "front", k, el.ox, 400 - 600 / k + 600 / k, uc, 600 + 0, clip=(-6050, 400, 560, 1120))
    cw.oy = 395
    cw.draw(CW, thick=0.4, thin=0.2, floor=False)
    cb = cw.box()
    sh.heading((cb[0] + cb[1]) / 2, cb[3] + 18, "D. Nước làm mát xi lanh (barrel cooling water) – hình chiếu đứng không vỏ che", "1:10")
    cw.balloons(["barrel_cw_supply", "barrel_cw_return", "barrel_cw_valves", "barrel_cw_hoses", "util_cw_supply_riser",
                 "util_cw_return_riser", "util_cw_throat_hoses", "util_cw_sidefeed_hoses"], sides=("bottom",), offset=5, rows=1)
    for x in (200, 476, 876, 1490):
        a = cw.P((x, 184, 1016))
        sh.ax.add_patch(__import__("matplotlib").patches.Circle(a, 1.1, fc="#1f5fbf", ec="k", lw=0.2, zorder=50))
    sh.text(*cw.P((4500, 0, 1110)), "đầu nối 45° dưới +Y tại X = đầu đoạn + 200 / cuối đoạn − 200, qua rãnh băng nhiệt", ha="center",
            va="bottom", bbox=dict(fc="white", ec="none", pad=0.2))
    dft.section_marker(sh, cw.P((2904, 0, 1100)), cw.P((2904, 0, 700)), "E", (1, 0))
    # ---------------------------------------------------------------- right column: section A-A 1:5
    kk = 5
    cx, cy = 828, 712
    sh.heading(cx + 40, 812, "Mặt cắt A–A (section A–A)", "1:5", sub="qua B4 tại X 2 984 (băng nhiệt), nhìn theo −X")
    barrel_section(sh, cx, cy, kk)
    sh.line([(cx - 75, cy), (cx + 75, cy)], lw=0.18, ls="center")
    sh.line([(cx, cy - 72), (cx, cy + 72)], lw=0.18, ls="center")
    sh.dim((cx - 71 / kk, cy), (cx + 71 / kk, cy), cy - 24, "h", text="a = 142")
    sh.dim((cx - 155.5 / kk, cy), (cx + 155.5 / kk, cy), cy - 34, "h", text="311")
    sh.dim((cx - 320 / kk, cy), (cx + 320 / kk, cy), cy - 77, "h", text="Ø640 bích (phía sau)")
    sh.dim((cx + 71 / kk, cy - 84.5 / kk), (cx + 71 / kk, cy + 84.5 / kk), cx + 70, "v", text="Ø169")
    sh.dim((cx, cy - 290 / kk), (cx, cy + 290 / kk), cx + 80, "v", text="Ø580")
    a20 = math.radians(9 + 18 * 2)
    sh.labels_column([((cx + 290 / kk * math.cos(math.radians(60)), cy + 290 / kk * math.sin(math.radians(60))), "băng nhiệt gốm Ø580"),
                      ((cx + 280 / kk * math.cos(a20), cy + 280 / kk * math.sin(a20)), "20 đai ốc M24 trên PCD 560 (phía sau)", "barrel_joint_3"),
                      ((cx + 215 / kk * math.cos(math.radians(22.5)), cy + 215 / kk * math.sin(math.radians(22.5))), "8 lỗ khoan nước Ø18 trên Ø430 (G)"),
                      ((cx + 71 / kk + 8, cy + 3), "trục vít 2 đầu ren, tự làm sạch", "screws"),
                      ((cx + 71 / kk, cy), "trục then hoa Ø72 (gạch ba hướng)")],
                     cx + 92, cy + 58, step=7)
    # ---------------------------------------------------------------- detail B 1:5 (flange joint, half section)
    k5 = 5
    bx0, by0 = 770, 500

    def Bp(x, r):
        return bx0 + (x - 2560) / k5, by0 + r / k5
    sh.heading(Bp(2705, 0)[0] + 10, 615, "Chi tiết B (detail B)", "1:5", sub="mối nối bích Ø640, nửa mặt cắt qua bulông cấy")
    sec = lambda pts, h: dft.poly(ax, [Bp(x, r) for x, r in pts], hatch=h, lw=0.5)
    sec([(2560, 84.5), (2654, 84.5), (2704, 84.5), (2704, 320), (2654, 320), (2654, 250), (2614, 250), (2614, 260), (2560, 260)], "////")
    sec([(2704, 84.5), (2850, 84.5), (2850, 260), (2794, 260), (2794, 250), (2754, 250), (2754, 320), (2704, 320)], "\\\\\\\\")
    dft.poly(ax, [Bp(2704, 84.5), Bp(2709, 84.5), Bp(2709, 200), Bp(2704, 200)], fc="white", lw=0.3)
    dft.poly(ax, [Bp(2560, 260), Bp(2614, 260), Bp(2614, 290), Bp(2560, 290)], hatch="xx", lw=0.35)
    dft.poly(ax, [Bp(2794, 260), Bp(2850, 260), Bp(2850, 290), Bp(2794, 290)], hatch="xx", lw=0.35)
    dft.poly(ax, [Bp(2654, 267), Bp(2754, 267), Bp(2754, 293), Bp(2654, 293)], fc="white", lw=0.25)
    dft.poly(ax, [Bp(2622, 268), Bp(2786, 268), Bp(2786, 292), Bp(2622, 292)], fc="white", lw=0.4)
    dft.poly(ax, [Bp(2630, 262), Bp(2654, 262), Bp(2654, 298), Bp(2630, 298)], fc="#d0d0d0", lw=0.4)
    dft.poly(ax, [Bp(2754, 262), Bp(2778, 262), Bp(2778, 298), Bp(2754, 298)], fc="#d0d0d0", lw=0.4)
    dft.poly(ax, [Bp(2584, 257), Bp(2654, 257), Bp(2654, 303), Bp(2584, 303)], fc="none", ec="#555555", lw=0.25, ls="phantom")
    sh.line([Bp(2540, 0), Bp(2870, 0)], lw=0.18, ls="center")
    sh.line([Bp(2540, 280), Bp(2870, 280)], lw=0.13, ls="center")
    sh.dim(Bp(2654, 320), Bp(2704, 320), Bp(0 + 2560, 345)[1], "h", text="50")
    sh.dim(Bp(2704, 320), Bp(2754, 320), Bp(2560, 345)[1], "h", text="50")
    sh.dim(Bp(2622, 320), Bp(2786, 320), Bp(2560, 375)[1], "h", text="164")
    sh.dim(Bp(2850, 0), Bp(2850, 320), Bp(2890, 0)[0], "v", text="R320")
    sh.dim(Bp(2560, 0), Bp(2560, 250), Bp(2530, 0)[0], "v", text="R250 thắt")
    sh.labels_column([(Bp(2710, 280), "bulông cấy M24 10.9 × 164, 20 cái", "barrel_joint_3"),
                      (Bp(2642, 296), "đai ốc 12 cạnh + vòng đệm"),
                      (Bp(2620, 300), "vùng khẩu vặn (phantom), khe 12"),
                      (Bp(2634, 250), "thân thắt Ø500 × 40"),
                      (Bp(2706, 150), "gờ định tâm Ø400 + mặt kín")],
                     bx0 + 78, by0 + 52, step=7)
    # flange face 1:10
    k10 = 10
    fx, fy = 1080, 545
    sh.heading(fx, 615, "Mặt bích nhìn dọc trục", "1:10", sub="20 lỗ Ø26 trên PCD 560")
    dft.circ(ax, (fx, fy), 320 / k10, fc="white", lw=0.5)
    dft.circ(ax, (fx, fy), 250 / k10, lw=0.2, ls="hidden")
    dft.circ(ax, (fx, fy), 200 / k10, lw=0.2, ls="hidden")
    dft.circ(ax, (fx, fy), 280 / k10, lw=0.13, ls="center")
    dft.poly(ax, dft.fig8(fx, fy, 142, 84.5, k10), fc="white", lw=0.4)
    for i in range(20):
        a = math.radians(9 + 18 * i)
        dft.circ(ax, (fx + 28 * math.cos(a), fy + 28 * math.sin(a)), 1.3, fc="white", lw=0.3)
    sh.line([(fx - 38, fy), (fx + 38, fy)], lw=0.13, ls="center")
    sh.line([(fx, fy - 38), (fx, fy + 38)], lw=0.13, ls="center")
    sh.dim((fx - 32, fy), (fx + 32, fy), fy - 42, "h", text="Ø640")
    sh.dim((fx - 28, fy), (fx + 28, fy), fy - 52, "h", text="PCD 560")
    sh.text(fx, fy - 58, "mép lỗ – mép bích 27; nét đứt: thắt Ø500, gờ Ø400", ha="center", va="top")
    # ---------------------------------------------------------------- E: section through a cooling fitting 1:5 + schematic
    ex, ey = 760, 360
    sh.heading(ex, 448, "Mặt cắt E–E (đầu nối nước)", "1:5", sub="X 2 904, rãnh 50 ở băng nhiệt, 45° dưới +Y")
    p1, p2 = barrel_section(sh, ex, ey, kk, notch=True, fitting=True, nuts=False)
    sh.label(p2, (ex + 75, ey - 30), "khớp nối nhanh + ống mềm inox DN15", ha="left", pid="barrel_cw_hoses")
    sh.label(p1, (ex + 75, ey - 37), "lỗ khoan nước dọc thân", ha="left")
    # one-zone schematic
    sx0, sy0 = 712, 222
    sh.text(sx0 - 8, sy0 + 50, "Sơ đồ một vùng nhiệt (one zone)", 11, va="bottom", weight="bold")
    blue = "#1f5fbf"
    xsup = [sx0, sx0 + 12, sx0 + 26, sx0 + 42, sx0 + 62, sx0 + 84]
    yline = sy0 + 12
    sh.line([(sx0 - 6, yline), (sx0 + 100, yline)], lw=0.6, c=blue)
    dft.sym_valve(sh, (xsup[1], yline), 7, kind="ball")
    dft.sym_strainer(sh, (xsup[2], yline), 7)
    dft.sym_valve(sh, (xsup[3], yline), 7, kind="solenoid")
    dft.sym_box(sh, (xsup[4] + 8, yline), 18, 9, "xi lanh")
    sh.line([(sx0 + 79, yline - 14), (sx0 + 79, yline)], lw=0.6, c=blue)
    sh.line([(sx0 - 6, yline - 14), (sx0 + 100, yline - 14)], lw=0.6, c=blue, ls="hidden")
    dft.sym_valve(sh, (xsup[5] + 6, yline), 7, kind="throttle")
    sh.text(sx0 - 7, yline, "cấp", ha="right", va="center", color=blue)
    sh.text(sx0 - 7, yline - 14, "hồi", ha="right", va="center", color=blue)
    dft.sym_instrument(sh, (sx0 + 100, yline + 12), "FI", "z", r=6)
    dft.sym_instrument(sh, (xsup[4] + 8, yline + 24), "TE", "z", r=6)
    dft.sym_instrument(sh, (xsup[3], yline + 32), "TIC", "z", r=6.5, panel=True)
    sh.line([(xsup[4] + 8, yline + 18), (xsup[4] + 8, yline + 4.5)], lw=0.25, ls="hidden")
    sh.line([(xsup[3] + 6.5, yline + 32), (xsup[4] + 2, yline + 24)], lw=0.25, ls="hidden")
    sh.line([(xsup[3], yline + 25.5), (xsup[3], yline + 10)], lw=0.25, ls="hidden")
    sh.text(sx0 - 6, sy0 - 14, "van bi → lọc Y → van điện từ (TIC) → lỗ khoan → tiết lưu → FI → hồi", ha="left", va="center")
    # ---------------------------------------------------------------- bottom-left: support C, cover, water plan, notes
    sup = P["barrel_support_2"]["outline_mm"]["pts"]
    sx, syy = 95, 250
    kc = 10

    def S(y, z):
        return sx + y / kc, syy + (z - 650) / kc
    sh.heading(sx, 330, "Chi tiết C – gối đỡ", "1:10", sub="gối 2 tại X 3 211")
    dft.poly(ax, [S(y, z) for y, z in sup], fc="white", lw=0.5)
    dft.circ(ax, S(0, 800), 6, fc="white", lw=0.4)
    th = np.linspace(math.radians(205), math.radians(335), 40)
    dft.poly(ax, [S(260 * math.cos(t), 1200 + 260 * math.sin(t)) for t in th] + [S(260 * math.cos(t) * 0.97, 1200 + 268 * math.sin(t)) for t in th[::-1]],
             fc="#c8c8c8", lw=0.25)
    arc = np.linspace(0, 2 * math.pi, 120)
    dft.poly(ax, [S(260 * math.cos(t), 1200 + 260 * math.sin(t)) for t in arc], fc="none", ec="#555555", lw=0.2, ls="phantom")
    for y in (-300, 300):
        dft.poly(ax, [S(y - 15, 650), S(y + 15, 650), S(y + 15, 690), S(y - 15, 690)], fc="#8c8c8c", lw=0.2)
    sh.dim(S(-350, 650), S(350, 650), S(0, 570)[1], "h", text="700")
    sh.dim(S(-350, 650), S(-350, 1034), S(-450, 0)[0], "v", text="384")
    sh.labels_column([(S(120, 958), "tấm trượt đồng/PTFE: giữ Y, tự do X"), (S(0, 800), "lỗ Ø120 tại Z 800"),
                      (S(300, 670), "4 bulông M30, lỗ ô van")], sx + 42, syy + 34, step=7)
    cxp, cyp = 300, 250
    kc2 = 20
    cov = P["barrel_cover_c4"]["outline_mm"]["pts"]

    def Cv(y, z):
        return cxp + y / kc2, cyp + (z - 650) / kc2
    sh.heading(cxp + 10, 330, "Vỏ che C1…C6", "1:20", sub="mặt cắt ngang vỏ")
    dft.poly(ax, [Cv(y, z) for y, z in cov], fc="white", lw=0.5)
    sh.line([Cv(-480, 1150), Cv(480, 1150)], lw=0.3)
    dft.circ(ax, Cv(0, 1200), 330 / kc2, lw=0.2, ls="phantom", ec="#555555")
    sh.dim(Cv(-480, 650), Cv(480, 650), Cv(0, 520)[1], "h", text="960")
    sh.dim(Cv(-330, 1650), Cv(330, 1650), Cv(0, 1800)[1], "h", text="660")
    sh.dim(Cv(-480, 650), Cv(-480, 1650), Cv(-680, 0)[0], "v", text="1 000")
    sh.labels_column([(Cv(-345, 1640), "bản lề nắp phía −Y"), (Cv(200, 1150), "mép chia Z 1 150"),
                      (Cv(330, 1200), "lỗ tấm đầu Ø660 (bích Ø640)")], cxp + 34, cyp + 30, step=7)
    rows = [["C6", "1 690–2 366", "lỗ 420×380 ôm vòm vùng 1; tấm đầu lỗ Ø660"], ["C5", "2 366–3 042", "–"], ["C4", "3 042–3 718", "–"],
            ["C3", "3 718–4 450", "lỗ 620×420 ôm vòm vùng 2"], ["C2", "4 450–5 100", "–"],
            ["C1", "5 100–5 760", "tấm tròn Ø420 10 bulông; tấm đầu lỗ Ø660"]]
    sh.table(30, 195, [("Vỏ", 12, "c"), ("X (mm)", 30, "c"), ("Đặc điểm", 110, "l")], rows, title="Vỏ che (cover boxes)")
    # water routing plan 1:50
    wp = VP(sh, "top", 50, 560, 260, -(-4000 + 6400) / 2 * -1 * -1, 1050, clip=(-6400, 4000, -1300, 3300))
    wp.uc = -(6400 - 4000) / 2 * -1 + 0
    wp.uc = (-6400 + 4000) / 2
    wids = CW + [q for q in ("util_cw_lube_hoses", "util_cw_motor_hoses", "util_cw_vac_hoses", "lube_oil_cooler", "drive_motor",
                             "vac_separator", "vac_pump_unit", "gearbox", "lantern", "sidefeed_barrel") if q in P]
    wp.draw(wids, thick=0.3, thin=0.15, floor=False)
    wb = wp.box()
    sh.heading((wb[0] + wb[1]) / 2, wb[3] + 22, "F. Bố trí nước làm mát – mặt bằng", "1:50")
    wp.balloons(["util_cw_motor_hoses", "util_cw_vac_hoses", "util_cw_lube_hoses"], sides=("top",), offset=5)
    sh.notes(200, 195, "Ghi chú (notes)", [
        "1. Xi lanh cố định tại lantern (X = 0); gối đỡ 1–3 cho trượt theo X, giãn nở ≈ 17 mm ở ΔT 250 K.",
        "2. Bích Ø640 × 50, 20 × M24 trên PCD 560; thân thắt Ø500 × 40 sau mỗi bích cho khẩu vặn (khe 12).",
        "3. Lỗ số 8: hai lỗ Ø169 tâm Y = ±71 (a = 142), rộng 311 × cao 169; trục vít Ø167,5, lõi 114,6.",
        "4. Mỗi vùng: van bi, lọc Y, van điện từ do TIC điều khiển, lỗ khoan, tiết lưu, chỉ báo dòng.",
        "5. Lỗ khoan nước, profin rãnh then hoa là giả định (G).",
    ], width=230)
    sheet_parts_list(sh, 925, 455, rowh=5.0)
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
