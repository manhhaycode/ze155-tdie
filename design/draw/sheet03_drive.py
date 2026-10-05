#!/usr/bin/env python3
"""Sheet 03 – drive train: motor, couplings, gearbox, lantern + spline connection, lube-oil unit, motor base."""
import math

from geom import P, ORDER, scene
from sheet import Sheet, VP, fmt, PT, DASH, sheet_parts_list, MIN_FS
import drafting as dft

DRIVE = [q for q in ORDER if P[q]["group"] == "drive"]
IDS = DRIVE + [q for q in ("base_frame_drive", "base_frame_process", "base_feet", "ctrl_machine_cabinet", "ctrl_signal_tower", "barrel_b1",
                           "barrel_joint_1", "barrel_b2", "screws", "util_cw_supply_riser", "util_cw_return_riser", "util_cw_lube_hoses",
                           "barrel_cw_supply", "barrel_cw_return", "barrel_cable_tray", "ctrl_cable_mv", "ctrl_cable_drop", "feed_throat",
                           "barrel_cw_valves", "util_cw_motor_hoses") if q in P]
HID = ["drive_flex_coupling", "drive_safety_coupling"]


def hidden_outline(vp, ids):
    for it in scene(vp.v, ids):
        if it["sil"]:
            vp._patch(it, "none", "k", 0.18 * PT, DASH["hidden"], 60, None)


def main():
    sh = Sheet(3, "drive", "Truyền động (drive train)", size="A0", scale="1:20; 1:5",
               subtitle="Động cơ 1 500 kW, khớp đàn hồi + khớp an toàn, hộp số, lantern và nối then hoa, cụm dầu bôi trơn, đế động cơ")
    ax = sh.ax
    k = 20
    fx = 215 + 6100 / k / 2
    el = VP(sh, "front", k, fx, 600, 2750, 0, clip=(-300, 5800, -100, 2800))
    el.draw(IDS)
    el.breaks("left")  # barrel continues downstream (review M4)
    hidden_outline(el, HID)
    eb = el.box()
    pl = VP(sh, "top", k, fx, 445, 2750, 0, clip=(-300, 5800, -1150, 1150))
    pl.draw(IDS)
    pl.breaks("left")
    hidden_outline(pl, HID)
    pb = pl.box()
    de = VP(sh, "drive_end", k, eb[0] - 45 - 115 / 2, 600, 0, 0, clip=(-1150, 1150, -100, 2800))
    de.draw(IDS)
    db = de.box()
    sh.heading((eb[0] + eb[1]) / 2, eb[3] + 44, "Hình chiếu đứng (front elevation)", "1:20")
    sh.heading((pb[0] + pb[1]) / 2, pb[3] + 28, "Mặt bằng (plan view)", "1:20")
    sh.heading((db[0] + db[1]) / 2, db[3] + 44, "Nhìn từ đầu dẫn động (−X)", "1:20", fs=12)
    el.cline((-5150, 0, 1200), (300, 0, 1200))
    pl.cline((-5150, 0, 0), (300, 0, 0))
    for y in (71, -71):
        sh.line([pl.P((-750, y, 0)), pl.P((0, y, 0))], lw=0.18, ls="hidden")
    de.cline((0, 0, -100), (0, 0, 2800))
    de.cline((0, -1150, 1200), (0, 1150, 1200))
    dft.detail_marker(sh, el.P((-2640, 0, 1200)), 480 / k, "D")
    dft.section_marker(sh, el.P((-1000, 0, 1200)), el.P((150, 0, 1200)), "E", (0, -1))
    el.balloons(["drive_motor", "drive_encoder", "drive_coupling_guard", "gearbox", "lantern", "lube_pump_motor", "lube_filter_duplex",
                 "lube_oil_cooler", "lube_pipe_pressure", "ctrl_signal_tower", "ctrl_machine_cabinet", "barrel_b1", "drive_motor_base",
                 "lube_unit_frame", "util_cw_motor_hoses"], sides=("top",), offset=16, rows=2)
    el.balloons(["base_frame_drive", "base_feet", "lube_pipe_return", "util_cw_lube_hoses", "util_cw_supply_riser"], sides=("bottom",), offset=6)
    pl.balloons(["drive_motor_terminal_box", "ctrl_cable_mv", "barrel_cable_tray", "drive_safety_coupling", "drive_flex_coupling",
                 "util_cw_return_riser", "barrel_cw_supply"], sides=("bottom",), offset=6)
    yd = eb[3] + 5
    for a, b in ((-4975, -2950), (-2980, -2300), (-2300, -750), (-750, 0)):
        sh.dim(el.P((a, 0, 2610)), el.P((b, 0, 2610)), yd, "h", value=b - a)
    for z, lab in ((650, "650"), (750, "750"), (1200, "1 200 tâm trục"), (1720, "1 720"), (2610, "2 610 (đèn tháp 2 650)")):
        x, y = el.P((-5800, 0, z))
        sh.line([(x + 1, y), (x + 4, y)], lw=0.18)
        sh.text(x + 4.5, y, lab, ha="left", va="center")
    sh.dim(el.P((-3150, 0, 750)), el.P((-3150, 0, 1200)), el.P((-2560, 0, 0))[0], "v", text="H 450")
    pl.dimw((-4900, -575, 0), (-4900, 575, 0), 5100, "v")
    pl.dimw((-1500, -700, 0), (-1500, 700, 0), 1950, "v")
    pl.dimw((-5150, 1000, 0), (-5150, -1000, 0), 5780, "v", text="khung 2 000")
    de.dimw((0, -1000, 650), (0, 1000, 650), -60, "h", text="2 000")
    de.dimw((0, -575, 2610), (0, 575, 2610), 2700, "h", text="1 150")
    # ---------------------------------------------------------------- D: coupling train full section 1:5
    kc = 5
    cx0, cy0 = 560, 690  # sheet point of X -3150, Z 1200

    def C(x, r):
        return cx0 + (x + 3150) / kc, cy0 + r / kc
    sh.heading(C(-2700, 0)[0], 812, "Chi tiết D – khớp nối, mặt cắt dọc", "1:5", sub="trục động cơ Ø140 trong moay-ơ → đĩa lò xo → khớp an toàn → trục vào Ø160")

    def sec(x0, x1, r0, r1, h="////", fc="white", both=True):
        for s_ in ((1, -1) if both else (1,)):
            dft.poly(ax, [C(x0, s_ * r0), C(x1, s_ * r0), C(x1, s_ * r1), C(x0, s_ * r1)], hatch=h, fc=fc, lw=0.45)
    sec(-3150, -2830, 0, 70, None, "#ececec", both=False)
    sec(-3150, -2830, -70, 0, None, "#ececec", both=False)
    sec(-2950, -2910, 70, 150)                 # hub A boss on motor shaft
    sec(-2910, -2870, 70, 280)                 # hub A flange
    for i in range(6):
        sec(-2868 + i * 6, -2865 + i * 6, 150, 270, None, "#bdbdbd")
    sec(-2830, -2790, 85, 280, "\\\\\\\\")    # hub B flange
    sec(-2790, -2700, 85, 150, "\\\\\\\\")     # hub B / spacer
    sec(-2700, -2400, 200, 320, "xx")          # safety coupling outer ring
    sec(-2700, -2400, 80, 200, "////")         # safety coupling inner (friction) part
    sec(-2400, -2300, 80, 200, "////")         # taper hub
    sec(-2700, -2250, -80, 80, None, "#ececec", both=False)  # gearbox input shaft Ø160
    sec(-2950, -2830, 70, 78, None, "#7f7f7f")  # key
    for xb in (-2905, -2795):
        for s_ in (1, -1):
            dft.poly(ax, [C(xb - 6, s_ * 215), C(xb + 6, s_ * 215), C(xb + 6, s_ * 245), C(xb - 6, s_ * 245)], fc="white", lw=0.3)
    for s_ in (1, -1):
        dft.poly(ax, [C(-2712, s_ * 245), C(-2688, s_ * 245), C(-2688, s_ * 265), C(-2712, s_ * 265)], fc="white", lw=0.3)
    dft.poly(ax, [C(-2980, -450), C(-2980, 450), C(-2300, 450), C(-2300, -450)], fc="none", ec="#555555", lw=0.25, ls="phantom")
    dft.poly(ax, [C(-2300, -250), C(-2250, -250), C(-2250, 250), C(-2300, 250)], fc="white", lw=0.35)
    dft.poly(ax, [C(-3150, -575), C(-3150, 575)], fc="none", lw=0.5, closed=False)
    sh.line([C(-3170, 0), C(-2230, 0)], lw=0.18, ls="center")
    sh.dim(C(-3150, 70), C(-2830, 70), C(-3150, 520)[1], "h", text="đầu trục 320 (lắp 120 trong moay-ơ)")
    sh.dim(C(-2950, 280), C(-2700, 280), C(-3150, 490)[1], "h", text="250")
    sh.dim(C(-2700, 320), C(-2300, 320), C(-3150, 490)[1], "h", text="400")
    sh.dim(C(-2290, -320), C(-2290, 320), C(-2200, 0)[0], "v", text="Ø640")
    sh.dim(C(-2960, -280), C(-2960, 280), C(-3060, 0)[0] - 4, "v", text="Ø560")
    sh.labels_column([(C(-2990, 40), "trục động cơ Ø140, then + ép nóng", "drive_motor"),
                      (C(-2867, 220), "bộ đĩa lò xo – khớp đàn hồi Ø560", "drive_flex_coupling"),
                      (C(-2795, 230), "12 bulông nối hai moay-ơ"),
                      (C(-2550, 260), "khớp an toàn Ø640, công tắc nhả (s_16)", "drive_safety_coupling"),
                      (C(-2350, 140), "moay-ơ côn trên trục vào Ø160", "gearbox"),
                      (C(-2640, 450), "vỏ che (phantom), liên động s_15", "drive_coupling_guard")],
                     C(-2200, 0)[0] + 18, cy0 + 70, step=7.5)
    # ---------------------------------------------------------------- E: lantern / spline connection, plan section at Z 1200, 1:5
    kl = 5
    lx0, ly0 = 560, 455  # sheet point of X -1000, Y 0

    def L(x, y):
        return lx0 + (x + 1000) / kl, ly0 - y / kl
    sh.heading(L(-430, 0)[0], 560, "Mặt cắt E–E – lantern, nối then hoa trục ra – trục vít", "1:5", sub="mặt cắt ngang qua tâm hai trục Z 1 200, nhìn từ trên")
    hp = lambda pts, h="////", fc="white", lw=0.45: dft.poly(ax, [L(x, y) for x, y in pts], hatch=h, fc=fc, lw=lw)
    for s_ in (1, -1):
        hp([(-1000, s_ * 165), (-760, s_ * 165), (-760, s_ * 520), (-1000, s_ * 520)])               # gearbox wall at output
        hp([(-750, s_ * 410), (0, s_ * 410), (0, s_ * 450), (-750, s_ * 450)] if s_ < 0 else
           [(-750, 410), (-565, 410), (-565, 450), (-750, 450)], "\\\\\\\\")
        hp([(-750, s_ * 165), (-700, s_ * 165), (-700, s_ * 450), (-750, s_ * 450)], "\\\\\\\\")      # lantern rear flange
        hp([(-60, s_ * 160), (0, s_ * 160), (0, s_ * 450), (-60, s_ * 450)], "\\\\\\\\")             # lantern front flange
        hp([(0, s_ * 156), (50, s_ * 156), (50, s_ * 320), (0, s_ * 320)], "xx")                      # B1 flange
        hp([(50, s_ * 156), (150, s_ * 156), (150, s_ * 250), (50, s_ * 250)], "xx")
    hp([(-185, 410), (0, 410), (0, 450), (-185, 450)], "\\\\\\\\")
    dft.poly(ax, [L(-565, 450), L(-185, 450), L(-185, 462), L(-565, 462)], fc="white", lw=0.3, ls="hidden")
    for y in (71, -71):
        hp([(-1000, y - 60), (-330, y - 60), (-330, y + 60), (-1000, y + 60)], None, "#ececec", 0.4)    # output shaft
        hp([(-470, y - 68), (-170, y - 68), (-170, y + 68), (-470, y + 68)], "....", "white", 0.4)     # spline sleeve
        hp([(-300, y - 60), (0, y - 60), (0, y + 60), (-300, y + 60)], None, "#d8d8d8", 0.4)          # screw spline shank
        hp([(0, y - 83.75), (150, y - 83.75), (150, y + 83.75), (0, y + 83.75)], None, "#d8d8d8", 0.4)  # screw
        sh.line([L(-1000, y), L(150, y)], lw=0.13, ls="center")
        for xb in ((-985, -905) if y > 0 else (-905, -825)):
            pass
    for y, xa in ((71, -985), (-71, -905)):
        dft.poly(ax, [L(xa, y - 95), L(xa + 70, y - 95), L(xa + 70, y + 95), L(xa, y + 95)], fc="white", ec="#555555", lw=0.25, ls="phantom")
        sh.line([L(xa, y - 95), L(xa + 70, y + 95)], lw=0.18, c="#555555")
        sh.line([L(xa, y + 95), L(xa + 70, y - 95)], lw=0.18, c="#555555")
    for y in (280, -280):
        dft.poly(ax, [L(-80, y - 12), L(82, y - 12), L(82, y + 12), L(-80, y + 12)], fc="white", lw=0.35)
    sh.dim(L(-750, -450), L(0, -450), L(0, -560)[1], "h", text="lantern 750")
    sh.dim(L(160, 71), L(160, -71), L(190, 0)[0], "v", text="a = 142")
    sh.labels_column([(L(-900, 71), "ổ chặn (thrust bearing) xếp lệch, trong hộp số (phantom)"),
                      (L(-600, -71), "trục ra hộp số Ø120"),
                      (L(-320, 71), "ống then hoa 24 răng (spline sleeve)"),
                      (L(-100, -71), "đuôi trục vít then hoa Ø120", "screws"),
                      (L(-375, 456), "cửa thăm 380 × 250 phía +Y", "lantern"),
                      (L(25, 280), "20 bulông cấy M24, bích B1 Ø640", "barrel_b1")],
                     L(150, 0)[0] + 40, ly0 + 48, step=7.5)
    # ---------------------------------------------------------------- lube oil schematic (with relief valve, strainer, PS, TT)
    lx, ly = 70, 255
    sh.text(lx - 20, ly + 40, "Sơ đồ dầu bôi trơn hộp số (lube-oil circuit)", 11, va="bottom", weight="bold")
    oil, wcol = "#b06a00", "#1f5fbf"
    dft.sym_box(sh, (lx, ly), 44, 16, "carter hộp số")
    dft.sym_strainer(sh, (lx + 34, ly), 8)
    dft.sym_pump(sh, (lx + 56, ly), 7, kind="gear")
    sh.text(lx + 60, ly - 16, "bơm 60 L/ph, 4 kW", ha="center", va="top")
    dft.sym_box(sh, (lx + 98, ly), 40, 16, "lọc kép 25 µm")
    dft.sym_box(sh, (lx + 152, ly), 46, 16, "làm mát tấm 30 kW")
    dft.sym_box(sh, (lx + 152, ly - 40), 46, 16, "vòi phun + ổ trục")
    for a, b in (((lx + 22, ly), (lx + 30, ly)), ((lx + 38, ly), (lx + 49, ly)), ((lx + 63, ly), (lx + 78, ly)), ((lx + 118, ly), (lx + 129, ly))):
        sh.line([a, b], lw=0.6, c=oil)
        sh.arrow(b, a, size=2.6, c=oil)
    sh.line([(lx + 152, ly - 8), (lx + 152, ly - 32)], lw=0.6, c=oil)
    sh.arrow((lx + 152, ly - 32), (lx + 152, ly - 20), size=2.6, c=oil)
    sh.line([(lx + 129, ly - 40), (lx, ly - 40), (lx, ly - 8)], lw=0.6, c=oil)
    sh.arrow((lx, ly - 8), (lx, ly - 20), size=2.6, c=oil)
    sh.line([(lx + 56, ly + 7), (lx + 56, ly + 14), (lx + 12, ly + 14), (lx + 12, ly + 8)], lw=0.4, c=oil, ls="hidden")
    dft.sym_valve(sh, (lx + 34, ly + 14), 8, kind="relief")
    sh.text(lx + 34, ly + 24, "van an toàn", ha="center", va="bottom")
    sh.text(lx + 34, ly - 9, "lọc hút", ha="center", va="top")
    dft.sym_instrument(sh, (lx + 196, ly - 22), "PSL", "s_14")
    dft.sym_instrument(sh, (lx + 196, ly - 52), "TT", "s_14")
    sh.line([(lx + 152 + 23, ly - 24), (lx + 189.2, ly - 22)], lw=0.25, ls="hidden")
    sh.line([(lx + 152 + 23, ly - 40), (lx + 189.2, ly - 52)], lw=0.25, ls="hidden")
    sh.line([(lx + 175, ly + 4), (lx + 212, ly + 4)], lw=0.5, c=wcol)
    sh.line([(lx + 175, ly - 4), (lx + 212, ly - 4)], lw=0.5, c=wcol, ls="hidden")
    dft.sym_valve(sh, (lx + 200, ly + 4), 7, kind="ball")
    sh.text(lx + 214, ly, "nước DN25\ncấp / hồi", ha="left", va="center", color=wcol)
    sh.text(lx + 60, ly - 52, "PSL + TT → tủ đầu máy → PLC (s_14, s_17): cấm khởi động khi áp dầu thấp", ha="center", va="top")
    # ---------------------------------------------------------------- tables, notes, parts list
    rows = [["Trục động cơ Ø140", "1 200", "H 450 trên mặt đế Z 750"], ["Khớp đàn hồi / an toàn", "1 200", "đồng trục động cơ"],
            ["Trục vào hộp số Ø160", "1 200", "giả định (G)"], ["2 trục ra then hoa", "1 200", "Y = ±71, a = 142"],
            ["Hai trục vít", "1 200", "c006"], ["Mặt khung / đế động cơ", "650 / 750", "đế dày 100"]]
    sh.table(400, 300, [("Trục (shaft)", 54, "l"), ("Z", 22, "c"), ("Ghi chú", 56, "l")], rows, title="Cao độ trục (shaft heights)")
    sh.notes(400, 255, "Ghi chú (notes)", [
        "1. Động cơ 1 500 kW, 3 kV, khung AMI 450L4 (L 2 025, H 450, A 850, B 1 400) – G.",
        "2. Tỷ số hộp số ≈ 3,73 (1 490 → 400 v/ph); hộp số 2 × 35 kNm.",
        "3. Khớp nối trong vỏ che (nét đứt ở hình chiếu); chi tiết D và E vẽ mặt cắt.",
        "4. Liên động: vỏ che (s_15), nhả khớp (s_16), áp dầu + nhiệt dầu (s_14) → tủ đầu máy → PLC → STO.",
        "5. Đầu trục động cơ phải dài ≈ 320 để lắp 120 trong moay-ơ (xem design_issues).",
    ], width=260)
    sheet_parts_list(sh, 925, 460, rowh=5.2)
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
