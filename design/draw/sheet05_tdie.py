#!/usr/bin/env python3
"""Sheet 05 – T-die: front view, top view with body bolts, section A-A (1:2), coat-hanger section B-B, side view with
roll stack, die lip to nip detail."""
import math

import numpy as np
from matplotlib.patches import Circle

from geom import P, ORDER, View
from sheet import Sheet, VP, fmt, PT, sheet_parts_list, MIN_FS
import drafting as dft

DIE = [q for q in ORDER if P[q]["group"] == "die"]
IDS = DIE + [q for q in ("melt_die_adapter", "melt_sensor_die", "melt_static_mixer", "melt_heater_bands", "util_air_drop", "util_frl",
                         "util_air_hose_die", "ctrl_trench_die_branch", "ctrl_floor_trench", "ctrl_estop_die") if q in P]
CTX = [q for q in ("ctx_roll_bottom", "ctx_roll_middle", "ctx_roll_top", "ctx_roll_stand", "ctx_roll_rails", "ctx_sheet", "ctx_roll_drives") if q in P]


XB = P["die_body_upper"]["bbox_mm"][0]   # die back face (X); was 9 126, DECISIONS 20 moves it to about 9 060
XF = P["die_body_upper"]["bbox_mm"][1]   # lip face
AD = P["melt_die_adapter"]["bbox_mm"]    # adapter flange ends at the die back face
MAN_R = 36                               # manifold Ø72 at the centre (G, design_issues #4)


def manifold_x():
    """Manifold centre X at Y = 0: from the die details if the designer states it, else 9 200 (drafter assumption G)."""
    import re
    for pid in ("die_body_upper", "die_body_lower"):
        for d in P[pid].get("details", []):
            m = re.search(r"ống phân phối[^.;]*?tâm (?:ở )?X\s*([0-9][0-9 ]{2,6})", d)
            if m:
                return float(m.group(1).replace(" ", ""))
    return 9200.0


MAN_X = manifold_x()


def bolt_rows():
    """Body-bolt rows (x, 'top'|'bottom') from die_body_bolts.positions_mm."""
    rows = sorted({(round(p[0]), "top" if p[2] > 1200 else "bottom") for p in P["die_body_bolts"]["positions_mm"]})
    return rows


def manifold_band(y):
    """Coat-hanger manifold centre line and half width at Y (G): centre MAN_X at Y = 0, swept 150 downstream at the ends."""
    return MAN_X + 150 * (abs(y) / 1250) ** 1.15, MAN_R - 22 * abs(y) / 1250


def lower_outline_z(x):
    return 1110 + (x - 9446) * 82 / 130


def main():
    sh = Sheet(5, "tdie", "Khuôn chữ T (T-die)", size="A0", scale="1:10; 1:2; 1:20; 1:5",
               subtitle="Khuôn móc áo môi mềm 2 400, vít thân, rãnh bản lề hở, bulông nhiệt, thanh chắn, deckle, xe khuôn, khe trục cán")
    ax = sh.ax
    up = P["die_body_upper"]["outline_mm"]["pts"]
    lo = P["die_body_lower"]["outline_mm"]["pts"]
    # ---------------------------------------------------------------- A: front view 1:10 (from +X)
    k = 10
    A = VP(sh, "die_end", k, 40 + 330 / 2, 612, 0, 0, clip=(-1650, 1650, -50, 1700))
    A.draw(IDS)
    ab = A.box()
    sh.heading((ab[0] + ab[1]) / 2, ab[3] + 30, "A. Mặt trước khuôn – nhìn từ phía cụm cán (−X)", "1:10")
    A.cline((0, 0, -50), (0, 0, 1700))
    A.cline((0, -1650, 1200), (0, 1650, 1200))
    zp = 2600 / 9
    for i in range(10):
        y = -1300 + i * zp
        sh.line([A.P((9576, y, 955)), A.P((9576, y, 1185))], lw=0.13, ls="center")
    for i in range(9):
        x, z1 = A.P((9576, -1300 + (i + 0.5) * zp, 1060))
        sh.text(x, z1, f"{10 + i}", ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.2), zorder=70)
    A.dimw((0, -1200, 1200), (0, 1200, 1200), 1780, "h", text="khe môi 2 400")
    A.dimw((0, -1375, 950), (0, 1375, 950), 880, "h", text="2 750 kể tấm đầu")
    A.dimw((0, -1525, 1200), (0, 1525, 1200), -170, "h", text="deckle 3 050")
    A.dimw((0, -1650, 0), (0, -1650, 1200), -1760, "v", text="1 200")
    dft.section_marker(sh, A.P((9576, 0, 1640)), A.P((9576, 0, 860)), "A", (-1, 0))
    A.balloons(["die_body_upper", "die_body_lower", "die_flex_lip", "die_end_plate_op", "die_end_plate_rear", "die_deckles",
                "die_bolt_actuator_rail", "die_lifting_lugs", "die_cart", "die_cart_rails", "die_drip_pan", "die_thermal_bolts",
                "die_choker_bolts", "ctrl_estop_die"], sides=("right",), offset=10)
    # ---------------------------------------------------------------- top view of the die 1:10 (look -Z, up = -X: lip at the bottom)
    tv = View("dietop", "+Y", "-X", "-Z")
    T = VP(sh, tv, k, A.ox, 548, 0, -9330, clip=(-1650, 1650, -9600, -9040))
    T.draw([q for q in DIE if q not in ("die_cart", "die_cart_rails", "die_drip_pan", "die_junction_box", "die_cable_harness", "die_heater_conduit")]
           + ["melt_die_adapter"], floor=False)
    tb = T.box()
    sh.heading((tb[0] + tb[1]) / 2, tb[3] + 4, "Hình chiếu bằng khuôn (top view) – môi khuôn ở dưới", "1:10")
    T.balloons(["die_body_bolts", "die_heater_boxes", "melt_die_adapter"], sides=("left",), offset=10)
    top_rows = [x for x, sd in bolt_rows() if sd == "top"]
    sh.text(tb[1] + 3, T.P((top_rows[0], 0, 1450))[1], "vít thân M30: hàng X " + " + ".join(fmt(x) for x in top_rows) + " (mặt đỉnh)",
            ha="left", va="center")
    cbx_ = P["die_choker_bolts"]["positions_mm"][0][0]
    sh.text(tb[1] + 3, T.P((cbx_, 0, 1450))[1] - 6, f"bulông thanh chắn X {fmt(cbx_)}", ha="left", va="center")
    # ---------------------------------------------------------------- B-B: coat-hanger on the parting plane 1:10 (aligned in Y)
    def E(x, y):
        return A.ox + y / k, 470 - (x - (XB - 26)) / k
    sh.heading(A.ox, 485, "Mặt cắt B–B – ống phân phối móc áo, mặt phân khuôn Z 1 200", "1:10", sub="nhìn xuống; môi khuôn ở dưới")
    body = [E(XB, -1375), E(XB, 1375), E(9560, 1375), E(9560, 1300), E(9576, 1300), E(9576, -1300), E(9560, -1300), E(9560, -1375)]
    ys = np.linspace(-1250, 1250, 101)
    xc = lambda y: manifold_band(y)[0]
    wd = lambda y: manifold_band(y)[1]
    man = [E(xc(y) + wd(y), y) for y in ys] + [E(xc(y) - wd(y), y) for y in ys[::-1]]
    inlet = [E(XB, -50), E(XB, 50), E(MAN_X - 10, 50), E(MAN_X - 10, -50)]
    holes = []
    pb = P["die_body_bolts"]
    for (x, y, z), it in zip(pb["positions_mm"], [pb["item_mm"]] * len(pb["positions_mm"])):
        holes.append(dft.circle_pts(*E(x, y), 15 / k, 16))
    dft.region(ax, body, [man, inlet], hatch="////", lw=0.5, z=10)
    for h in holes:
        dft.poly(ax, h, fc="#7f7f7f", lw=0.15, z=12)
    dft.poly(ax, [E(xc(y) + wd(y), y) for y in ys] + [E(9420, 1250), E(9420, -1250)], fc="#ededed", lw=0.2, z=11)
    dft.poly(ax, [E(9420, -1200), E(9420, 1200), E(9576, 1200), E(9576, -1200)], fc="#dcdcdc", lw=0.3, z=11)
    for s_ in (1, -1):
        dft.poly(ax, [E(9380, s_ * 1200), E(9380, s_ * 1525), E(9520, s_ * 1525), E(9520, s_ * 1200)], fc="white", lw=0.3, z=12)
    rows_ = bolt_rows()
    sh.labels_column([(E((XB + MAN_X - MAN_R) / 2, 0), "cửa vào Ø100 hở từ bích chuyển (C1)", "melt_die_adapter"),
                      (E(9230, -500), "ống phân phối móc áo Ø72 → Ø28 (G)"), (E(9330, 300), "vùng tiền môi (preland), khe 3–6"),
                      (E(9500, 700), "môi (land) dài 156, khe 0,5–2"), (E(rows_[0][0], -1100), f"vít thân cắt qua mặt phân khuôn ({len(P['die_body_bolts']['positions_mm'])})", "die_body_bolts")],
                     ab[1] + 12, 470, step=7)
    # orchestrator: design frozen; the body-bolt layout is a known simplification (design_issues #9), drawn as data, no clash flag
    sh.text(A.ox, E(XF + 14, 0)[1] - 2, "bố trí bu-lông thân khuôn đơn giản hóa (G)", ha="center", va="top")
    # ---------------------------------------------------------------- A-A: section through the die at Y = 0, 1:2
    k2 = 2
    ox, oy = 440, 640

    def S(x, z):
        return ox + (9600 - x) / k2, oy + (z - 1200) / k2
    sh.heading(ox + 140, 812, "Mặt cắt A–A (section A–A)", "1:2", sub="qua tâm khuôn Y = 0, nhìn từ +Y (môi bên trái)")
    ins = [(9446, 1140), (9446, 1199), (9576, 1199), (9576, 1192), (9493.6, 1140)]
    man_c = (MAN_X, 1200)
    man_up = [S(man_c[0] + 36 * math.cos(t), man_c[1] + 36 * math.sin(t)) for t in np.linspace(0, math.pi, 40)]
    man_lo = [S(man_c[0] + 36 * math.cos(t), man_c[1] + 36 * math.sin(t)) for t in np.linspace(math.pi, 2 * math.pi, 40)]
    pre_u = [S(9236, 1200), S(9446, 1200), S(9446, 1202), S(9236, 1202)]
    choker = [(9240, 1202), (9270, 1202), (9270, 1330), (9240, 1330)]
    heat_u = [dft.circle_pts(*S(9300, 1400), 10 / k2, 24)]
    heat_l = [dft.circle_pts(*S(x, 1010), 10 / k2, 24) for x in (MAN_X, 9330)]
    up_holes = [man_up, [S(XB, 1200), S(MAN_X - 10, 1200), S(MAN_X - 10, 1250), S(XB, 1250)],
                pre_u, [S(x, z) for x, z in choker]] + heat_u
    lo_holes = [man_lo, [S(XB, 1150), S(MAN_X - 10, 1150), S(MAN_X - 10, 1200), S(XB, 1200)], [S(x, z) for x, z in ins]] + heat_l
    dft.region(ax, [S(x, z) for x, z in up], up_holes, hatch="////", lw=0.5, z=10)
    dft.region(ax, [S(x, z) for x, z in lo], lo_holes, hatch="\\\\\\\\", lw=0.5, z=10)
    dft.poly(ax, [S(x, z) for x, z in ins], hatch="xxxx", lw=0.45, z=11)
    dft.poly(ax, [S(x, z) for x, z in [(9240, 1205), (9270, 1205), (9270, 1330), (9240, 1330)]], fc="#d0d0d0", lw=0.4, z=12)
    # adapter flange with open Ø100 bore (C1)
    xa0 = AD[1] - 76  # flange plate of the adapter (76 thick, G); the neck continues upstream
    dft.poly(ax, [S(xa0, 1250), S(AD[1], 1250), S(AD[1], AD[5]), S(xa0, AD[5])], hatch="xx", lw=0.45, z=10)
    dft.poly(ax, [S(xa0, AD[4]), S(AD[1], AD[4]), S(AD[1], 1150), S(xa0, 1150)], hatch="xx", lw=0.45, z=10)
    sh.line([S(xa0 - 10, 1250), S(xa0, 1250)], lw=0.3)
    sh.line([S(xa0 - 10, 1150), S(xa0, 1150)], lw=0.3)
    # heater boxes, rail, choker bolt, thermal bolt
    dft.poly(ax, [S(xa0, 1390), S(AD[1], 1390), S(AD[1], 1440), S(xa0, 1440)],
             fc="white", lw=0.35, z=13)
    rb = P["die_bolt_actuator_rail"]["bbox_mm"]
    dft.poly(ax, [S(rb[0], rb[4]), S(rb[1], rb[4]), S(rb[1], rb[5]), S(rb[0], rb[5])], fc="white", lw=0.4, z=10)
    cbx = P["die_choker_bolts"]["positions_mm"][0][0]
    cit = P["die_choker_bolts"]["item_mm"]
    dft.poly(ax, [S(cbx - 8, 1330), S(cbx + 8, 1330), S(cbx + 8, 1450), S(cbx - 8, 1450)], fc="#e6e6e6", lw=0.35, z=13)
    dft.poly(ax, [S(cbx - cit[0] / 2, 1450), S(cbx + cit[0] / 2, 1450), S(cbx + cit[0] / 2, 1450 + cit[2]), S(cbx - cit[0] / 2, 1450 + cit[2])],
             fc="#9a9a9a", lw=0.35, z=13)
    a_, b_ = np.array([9440, 1295.0]), np.array([9342, 1434.0])
    d_ = (b_ - a_) / np.linalg.norm(b_ - a_)
    n_ = np.array([-d_[1], d_[0]])
    dft.poly(ax, [S(*(a_ + n_ * 8)), S(*(b_ + n_ * 8)), S(*(b_ - n_ * 8)), S(*(a_ - n_ * 8))], fc="#9a9a9a", lw=0.35, z=14)
    dft.poly(ax, [S(*(a_ + n_ * 15 + d_ * 70)), S(*(b_ + n_ * 15)), S(*(b_ - n_ * 15)), S(*(a_ - n_ * 15 + d_ * 70))], fc="none", lw=0.3, z=14)
    # body bolts (out of the cutting plane: hidden), counterbores
    for x, side in bolt_rows():
        zt, zb = (1450, 1190) if side == "top" else (950, 1210)
        sg = -1 if zt > 1200 else 1
        sh.line([S(x - 15, zt + sg * 32), S(x - 15, zb), S(x + 15, zb), S(x + 15, zt + sg * 32)], lw=0.3, ls="hidden")
        sh.line([S(x - 24, zt), S(x - 24, zt + sg * 32), S(x + 24, zt + sg * 32), S(x + 24, zt)], lw=0.3, ls="hidden")
    # lower-lip screw
    sh.line([S(9505, 1118), S(9520, 1165)], lw=0.3, ls="hidden")
    sh.line([S(9640, 1200), S(9030, 1200)], lw=0.18, ls="center")
    sh.dim(S(XF, 950), S(XB, 950), S(0, 925)[1], "h", text=fmt(XF - XB))
    sh.dim(S(XB, 950), S(XB, 1450), S(XB - 111, 0)[0], "v", text="500")
    sh.dim(S(9404, 1450), S(9392, 1450), S(0, 1475)[1], "h", text="12")
    sh.dim(S(9392, 1200), S(9392, 1212), S(9370, 0)[0] - 0, "v", text="gân 12", tpos=(S(9370, 0)[0] - 1, S(0, 1170)[1]))
    sh.text(*S(9600, 1206), "↕ 0,5–2", ha="left", va="center")
    left = [(S(9398, 1300), "rãnh bản lề hở X 9 392–9 404 (I5)", "die_flex_lip"), (S(9440, 1296), "bulông nhiệt tì môi cách gân 36", "die_thermal_bolts"),
            (S(9576, 1200), "khe môi 0,5–2 tại Z 1 200"), (S(9520, 1170), "môi dưới: thanh chèn + vít M12", "die_body_lower")]
    right = [(S(9315, 1500), "thanh cơ cấu bulông nhiệt + ống gió", "die_bolt_actuator_rail"), (S(cbx, 1490), "bulông thanh chắn", "die_choker_bolts"),
             (S(9255, 1290), "thanh chắn (choker bar)"), (S(9300, 1400), "thanh nhiệt cắm (cartridge heater)"),
             (S(MAN_X, 1200 + MAN_R * 0.7), "ống phân phối Ø72 (G)"), (S((XB + MAN_X - MAN_R) / 2, 1200), "cửa vào Ø100 hở (C1)"),
             (S(AD[1] - 38, 1300), "bích chuyển, lòng Ø100", "melt_die_adapter"),
             (S(bolt_rows()[0][0], 1300), "vít thân M30 (nét khuất)", "die_body_bolts")]
    sh.labels_column(left + right, 735, 800, step=7.2)
    # ---------------------------------------------------------------- C: side view 1:20 with the roll stack
    k3 = 20
    C = VP(sh, "front", k3, 787 + 2650 / k3 / 2, 168, -(8650 + 11300) / 2, 0, clip=(-11300, -8650, -50, 3200))
    C.draw(IDS + CTX + ["melt_pipe"])
    cb = C.box()
    sh.heading((cb[0] + cb[1]) / 2, cb[3] + 20, "C. Khuôn + cụm cán (phantom)", "1:20")
    C.cline((8650, 0, 1200), (11300, 0, 1200))
    C.dimw((9576, 0, 1200), (9776, 0, 1200), 260, "h", text="200")
    C.dimw((9776, 0, 0), (9776, 0, 1200), -11450, "v", text="nip 1 200")
    C.balloons(["ctx_roll_middle", "ctx_roll_stand", "ctx_sheet", "die_junction_box"], sides=("top",), offset=6)
    # ---------------------------------------------------------------- D: die lip to nip 1:5 (single nose profile, clipped)
    kd = 5
    dx0, dy0 = 470, 300

    def Dp(x, z):
        return dx0 - (x - 9776) / kd, dy0 + (z - 1200) / kd
    sh.heading(dx0 + 31, 428, "D. Môi khuôn – khe trục cán", "1:5", sub="khe gió 200; khe hở mặt vát → trục giữa")
    clip = Circle((dx0 + 31, dy0 + 24), 92, transform=ax.transData)
    dft.circ(ax, (dx0 + 31, dy0 + 24), 92, lw=0.25, z=5)
    for pts in (up, lo):
        pg = dft.poly(ax, [Dp(x, z) for x, z in pts], fc="white", lw=0.5, z=10)
        pg.set_clip_path(clip)
    for zc in (799, 1601):
        th = np.linspace(0, 2 * math.pi, 360)
        pg = dft.poly(ax, [Dp(9776 + 400 * math.cos(t), zc + 400 * math.sin(t)) for t in th], fc="none", ec="#555555", lw=0.3, ls="phantom", z=11)
        pg.set_clip_path(clip)
    sh.line([Dp(9576, 1200), Dp(9776, 1200)], lw=0.8, c="#555555")
    a2 = np.array([9440, 1295.0])
    pg = dft.poly(ax, [Dp(*(a2 + n_ * 15)), Dp(*(b_ + n_ * 15)), Dp(*(b_ - n_ * 15)), Dp(*(a2 - n_ * 15))], fc="#9a9a9a", lw=0.35, z=12)
    pg.set_clip_path(clip)
    sh.dim(Dp(9576, 1200), Dp(9776, 1200), dy0 - 22, "h", text="khe gió 200")
    best = None
    for x, z in zip(np.linspace(9446, 9330, 60), np.linspace(1290, 1450, 60)):
        dd = math.hypot(x - 9776, z - 1601) - 400
        if best is None or dd < best[0]:
            best = (dd, x, z)
    dd, x, z = best
    ux, uz = (9776 - x) / (dd + 400), (1601 - z) / (dd + 400)
    sh.line([Dp(x, z), Dp(x + ux * dd, z + uz * dd)], lw=0.3)
    sh.labels_column([(Dp(x + ux * dd / 2, z + uz * dd / 2), f"khe hở mặt vát → trục giữa ≈ {dd:.0f} (trừ đầu bulông nhô ≤ 30)"),
                      (Dp(9776, 1200), "khe trục giữa – dưới X 9 776, Z 1 200"), (Dp(9650, 1200), "màn nhựa rộng 2 100", "ctx_sheet")],
                     dx0 + 135, dy0 + 100, step=8)
    # ---------------------------------------------------------------- tables, notes, parts list
    rows = [["1…9", "nửa trên, bước ≈ 289", "9 × 2,6 kW"], ["10…18", "nửa dưới, bước ≈ 289", "9 × 2,6 kW"],
            ["19, 20", "tấm đầu −Y / +Y", "2 × 1,5 kW"], ["BN 1…94", "bulông nhiệt bước 25,4", "94 × 80 W"]]
    sh.table(40, 250, [("Vùng", 22, "c"), ("Vị trí", 62, "l"), ("Công suất (G)", 40, "l")], rows, title="Vùng gia nhiệt khuôn")
    sh.notes(40, 205, "Ghi chú (notes)", [
        "1. Khuôn móc áo môi mềm, môi 2 400; tấm 2 100 sau cắt biên. Chỉnh thô bằng 33 bulông thanh chắn, tinh bằng 94 bulông nhiệt.",
        "2. Rãnh bản lề hở suốt bề rộng, gân 12 trên mặt chảy; bulông nhiệt bắc qua rãnh, tì môi cách gân 36.",
        "3. 94 vít thân M30 10.9 (4 hàng, bước 110, lệch 55) kẹp hai nửa ≈ 31 MN; đầu chìm trong lỗ khoét Ø48 × 32.",
        "4. Lòng Ø100 của bích chuyển nối thẳng vào cửa ống phân phối, đối xứng qua Z 1 200 (một nửa ở mỗi thân).",
        "5. Kích thước trong (ống phân phối, preland, thanh chắn, thanh nhiệt) là giả định (G).",
        "6. Xe khuôn chạy trên 2 ray theo Y; phải lùi cụm cán trước khi kéo khuôn. Cụm cán vẽ phantom.",
    ], width=330)
    sheet_parts_list(sh, 925, 470, rowh=5.2, extra=["die_heater_conduit", "die_cable_harness", "util_air_hose_die", "util_frl", "util_air_drop"])
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
