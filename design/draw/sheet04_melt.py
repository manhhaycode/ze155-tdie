#!/usr/bin/env python3
"""Sheet 04 – melt line: head adapter, diverter valve, screen changer + HPU, gear pump + drive, melt pipe, mixer, die adapter.
Flange data is read from design/design.md §6.3 (single source shared with parts.json connection types)."""
import math
import re

from geom import P, ORDER, ROOT
from sheet import Sheet, VP, fmt, PT, sheet_parts_list, MIN_FS
import drafting as dft
from sheet05_tdie import MAN_X

MELT = [q for q in ORDER if P[q]["group"] == "melt"]
IDS = MELT + [q for q in ("melt_stand_sc", "melt_stand_pump", "melt_pipe_saddles", "pump_drive_pedestal", "melt_valve_support",
                          "barrel_b6", "barrel_joint_5", "barrel_cover_c1", "base_frame_process", "barrel_support_3", "die_body_upper",
                          "die_body_lower", "die_flex_lip", "die_heater_boxes", "die_end_plate_op", "die_end_plate_rear", "die_cart",
                          "die_cart_rails", "ctrl_floor_trench", "ctrl_trench_die_branch", "barrel_heater_jboxes", "barrel_cable_tray",
                          "ctrl_estop_melt", "die_body_bolts", "die_choker_bolts", "die_bolt_actuator_rail") if q in P]
BORE = [(5600, 5746, 84.5), (5746, 5996, None), (5996, 6446, 60), (6446, 7301, 60), (7301, 7476, 55), (7476, 7926, 50), (7926, 8926, 50),
        (8926, 9164, 50)]


def flange_table():
    txt = (ROOT / "design" / "design.md").read_text()
    a = txt.index("### 6.3")
    b = txt.index("\n## 7", a)
    rows = []
    for ln in txt[a:b].splitlines():
        if ln.startswith("|") and not ln.startswith("|---") and "Mối nối" not in ln:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) >= 4:
                rows.append(cells[:4])
    out = []
    for joint, od, bolts, bore in rows:
        m_od = re.search(r"Ø\s?(\d+)", od)
        m_rect = re.search(r"(\d+)\s*×\s*(\d+)", od)
        m_n = re.search(r"(\d+)\s*(?:bulông cấy|vít|×)\s*M(\d+)", bolts)
        m_pcd = re.search(r"PCD\s*(\d+)", bolts)
        out.append(dict(joint=joint, od_text=od, bolts=bolts, bore=bore, od=int(m_od.group(1)) if m_od else None,
                        rect=(int(m_rect.group(1)), int(m_rect.group(2))) if (m_rect and not m_od) else None,
                        n=int(m_n.group(1)) if m_n else 8, m=int(m_n.group(2)) if m_n else 24, pcd=int(m_pcd.group(1)) if m_pcd else None))
    return out


def main():
    sh = Sheet(4, "melt-line", "Đường chảy nhựa (melt line)", size="A0", scale="1:10; 1:20; 1:2",
               subtitle="Đầu xi lanh, van khởi động, bộ lọc lưới + HPU, bơm bánh răng + truyền động, ống gia nhiệt, bộ trộn tĩnh, bích khuôn")
    ax = sh.ax
    # ---------------------------------------------------------------- A: in-line elevation 1:10 with melt channel to the manifold
    k = 10
    A = VP(sh, "front", k, 40 + 3750 / k / 2, 722, -(5600 + 9350) / 2, 1200, clip=(-9350, -5600, 860, 1780))
    A.draw(IDS, thick=0.45, thin=0.2, floor=False)
    ab = A.box()
    sh.heading((ab[0] + ab[1]) / 2, 814, "A. Đường chảy – hình chiếu đứng; nét đứt: lòng chảy tới ống phân phối khuôn", "1:10")
    A.cline((5600, 0, 1200), (9350, 0, 1200), lw=0.25)
    for x0, x1, r in BORE:
        if r is None:
            sh.line([A.P((x0, 0, 1284.5)), A.P((x1, 0, 1260))], lw=0.3, ls="hidden")
            sh.line([A.P((x0, 0, 1115.5)), A.P((x1, 0, 1140))], lw=0.3, ls="hidden")
        else:
            for sg in (1, -1):
                sh.line([A.P((x0, 0, 1200 + sg * r)), A.P((x1, 0, 1200 + sg * r))], lw=0.3, ls="hidden")
    dft.circ(ax, A.P((MAN_X, 0, 1200)), 36 / k, ls="hidden", lw=0.3, z=60)
    sh.line([A.P((MAN_X + 36, 0, 1200)), A.P((9345, 0, 1200))], lw=0.3, ls="hidden")
    dft.circ(ax, A.P((6221, 0, 1200)), 80 / k, ls="hidden", lw=0.3, z=60)
    for sg in (-1, 1):
        sh.line([A.P((6221 + sg * 40, 0, 1140)), A.P((6221 + sg * 40, 0, 940))], lw=0.3, ls="hidden")
    sh.line([A.P((6950, 0, 900)), A.P((6950, 0, 1740))], lw=0.3, ls="hidden")
    for dz in (65, -65):
        dft.circ(ax, A.P((7701, 0, 1200 + dz)), 70 / k, ls="hidden", lw=0.3, z=60)
    for xm in range(8476, 8900, 70):
        sh.line([A.P((xm, 0, 1150)), A.P((xm + 50, 0, 1250))], lw=0.2, ls="hidden")
    for xb in (5600, 9350):  # break lines at the view ends
        x, _ = A.P((xb, 0, 0))
        y0, y1 = ab[2], ab[3]
        pts = [(x, y0), (x, (y0 + y1) / 2 - 3), (x + 2, (y0 + y1) / 2 - 1), (x - 2, (y0 + y1) / 2 + 1), (x, (y0 + y1) / 2 + 3), (x, y1)]
        sh.line(pts, lw=0.25)
    labs = [((5876, 1700), "P1 + T1"), ((6521, 1650), "P2"), ((7388, 1620), "P3 → PIC → tốc độ bơm (s_20)"), ((8001, 1590), "P4 HH 330 bar"),
            ((9026, 1620), "P5 + T5"), ((6950, 1760), "lưới 60 µm quay"), ((7701, 1265), "2 bánh răng 764 cm³/v"),
            ((6221, 1280), "chốt xoay"), ((MAN_X, 1236), "ống phân phối Ø72 (sheet 05)")]
    labs.sort(key=lambda q: -q[0][0])
    for i, ((x, z), t) in enumerate(labs):
        a = A.P((x, 0, z))
        sh.label(a, (a[0] + 2, ab[3] + 3 + (i % 3) * 6), t, ha="left")
    xad, xdb = P["melt_die_adapter"]["bbox_mm"][0], P["die_body_upper"]["bbox_mm"][0]
    xs = [5746, 5996, 6446, 6596, 7301, 7476, 7926, 8076, 8426, xad, xdb]
    yd = ab[2] - 6
    for a, b in zip(xs, xs[1:]):
        sh.dim(A.P((a, 0, 1000)), A.P((b, 0, 1000)), yd, "h", value=b - a, ext=False)
    sh.dim(A.P((5746, 0, 1000)), A.P((xdb, 0, 1000)), yd - 11, "h", text=f"đường chảy {fmt(xdb - 5746)} (X 5 746 → {fmt(xdb)}), tâm Z 1 200",
           ext=False)
    sh.text(ab[1] + 3, ab[2] + 2, "đĩa nổ 1 và 2\nphía −Y (X 5 896, 8 001)", ha="left", va="bottom")
    # ---------------------------------------------------------------- B: elevation 1:20, C: plan 1:20
    k2 = 20
    uc = -(5550 + 9450) / 2
    B = VP(sh, "front", k2, 40 + 3900 / k2 / 2, 470, uc, 0, clip=(-9450, -5550, -100, 2400))
    B.draw(IDS)
    B.breaks("left", "right")  # die and barrel continue beyond the window (review M4)
    bb = B.box()
    sh.heading((bb[0] + bb[1]) / 2, bb[3] + 36, "B. Hình chiếu đứng", "1:20")
    B.cline((5550, 0, 1200), (9450, 0, 1200))
    Cp = VP(sh, "top", k2, 40 + 3900 / k2 / 2, 380 - 2950 / k2, uc, 0, clip=(-9450, -5550, -1050, 2950))
    Cp.draw(IDS)
    Cp.breaks("left", "right")
    cb = Cp.box()
    sh.heading((cb[0] + cb[1]) / 2, cb[3] + 8, "C. Mặt bằng", "1:20")
    Cp.cline((5550, 0, 0), (9450, 0, 0))
    B.balloons(["melt_head_adapter", "melt_startup_valve", "melt_sc_adapter_in", "melt_screen_changer", "melt_pump_adapter_in",
                "melt_gear_pump", "melt_pump_motor", "melt_pump_adapter_out", "melt_pipe", "melt_static_mixer", "melt_die_adapter",
                "melt_sensor_head", "melt_sensor_p2", "melt_sensor_p3", "melt_sensor_p4", "melt_sensor_die", "ctrl_estop_melt"],
               sides=("top",), offset=6, rows=2, r=4.8)
    B.balloons(["melt_drain_chute", "melt_purge_cart", "melt_stand_sc", "melt_stand_pump", "melt_pipe_saddles", "melt_valve_support",
                "melt_heater_bands"], sides=("bottom",), offset=5, r=4.8)
    Cp.balloons(["melt_hpu", "melt_hyd_hoses_sc", "melt_hyd_hoses_suv", "melt_sc_drive", "melt_startup_cyl", "melt_pump_cardan",
                 "melt_pump_gearbox", "pump_drive_pedestal", "melt_rupture_disc", "melt_rupture_disc_2", "melt_heater_jbox",
                 "melt_heater_conduits", "melt_sc_backflush"], sides=("right",), offset=8, r=4.8)
    for z, t in ((650, "650"), (970, "970"), (1200, "1 200"), (2079, "2 079 bộ lọc"), (2300, "2 300 động cơ bơm")):
        x, y = B.P((5550, 0, z))
        sh.line([(x + 1, y), (x + 4, y)], lw=0.18)
        sh.text(x + 4.5, y, t, ha="left", va="center")
    # ---------------------------------------------------------------- D: flange connections 1:10 from design.md §6.3
    fl = flange_table()
    sh.text(300, 600, "D. Mối nối mặt bích (flange connections), theo design.md §6.3", 11, va="bottom", weight="bold")
    kf = 10
    for i, f in enumerate(fl):
        cx = 335 + (i % 5) * 112
        cy = 548 - (i // 5) * 122
        if f["rect"]:
            w, h = f["rect"][0] / kf, f["rect"][1] / kf
            dft.poly(ax, [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], fc="white", lw=0.5)
            for bx, by in ((-210, -145), (-70, -145), (70, -145), (210, -145), (-210, 145), (-70, 145), (70, 145), (210, 145)):
                dft.circ(ax, (cx + bx / kf, cy + by / kf), f["m"] / 2 / kf * 1.1, fc="white", lw=0.3)
            dft.circ(ax, (cx, cy), 5, lw=0.35)
            sh.dim((cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), cy - h / 2 - 7, "h", text=f"{f['rect'][0]}")
            sh.dim((cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), cx + w / 2 + 7, "v", text=f"{f['rect'][1]}")
        else:
            R = f["od"] / 2 / kf
            dft.circ(ax, (cx, cy), R, fc="white", lw=0.5)
            if f["pcd"]:
                dft.circ(ax, (cx, cy), f["pcd"] / 2 / kf, lw=0.13, ls="center")
                off = math.pi / f["n"]
                for j in range(f["n"]):
                    a = off + 2 * math.pi * j / f["n"]
                    dft.circ(ax, (cx + f["pcd"] / 2 / kf * math.cos(a), cy + f["pcd"] / 2 / kf * math.sin(a)), f["m"] / 2 / kf * 1.1,
                             fc="white", lw=0.3)
            if "số 8" in f["bore"]:
                dft.poly(ax, dft.fig8(cx, cy, 142, 84.5, kf), fc="white", lw=0.35)
            else:
                m = re.findall(r"Ø(\d+)", f["bore"])
                dft.circ(ax, (cx, cy), (int(m[0]) / 2 if m else 50) / kf, lw=0.35)
            sh.dim((cx - R, cy), (cx + R, cy), cy - R - 6, "h", text=f"Ø{f['od']}")
            if f["pcd"]:
                sh.text(cx + R * 0.75, cy + R * 0.75, f"PCD {f['pcd']}", ha="left", va="bottom")
        sh.line([(cx - 36, cy), (cx + 36, cy)], lw=0.13, ls="center")
        sh.line([(cx, cy - 36), (cx, cy + 36)], lw=0.13, ls="center")
        mx = re.search(r"X\s?([\d ]+\d)", f["joint"])
        jt = re.sub(r"\s*\(.*?\)", "", f["joint"]).replace("đầu xi lanh", "đầu XL").replace("bích vào bộ lọc", "bích P2")
        jt = jt.replace("Bích ra → ống, ống → bộ trộn, bộ trộn → bích khuôn", "P4 → ống → trộn → khuôn")
        sh.text(cx, cy + 44, f"{i + 1}. {jt[:30]}", ha="center", va="bottom", weight="bold")
        if mx:
            sh.text(cx, cy + 39, f"X {mx.group(1)}", ha="center", va="bottom")
        sh.text(cx, cy - 46, f"{f['n']} × M{f['m']}" + (f", lòng {f['bore'][:14]}" if f["bore"] else ""), ha="center", va="top")
    # ---------------------------------------------------------------- E: typical melt flange, half section 1:2 (pump -> P4 adapter)
    k1 = 2
    ex0, ey0 = 300, 195  # sheet point of X 7880, axis

    def E(x, r):
        return ex0 + (x - 7880) / k1, ey0 + r / k1
    sh.heading(E(7960, 0)[0], 330, "E. Bích điển hình bơm → bích ra P4, nửa mặt cắt", "1:2", sub="gờ định tâm, vòng kín, bulông cấy, băng nhiệt, lỗ cảm biến")
    hp = lambda pts, h, fc="white", lw=0.5: dft.poly(ax, [E(x, r) for x, r in pts], hatch=h, fc=fc, lw=lw)
    hp([(7880, 50), (7911, 50), (7911, 180), (7926, 180), (7926, 118), (7921, 118), (7921, 100), (7926, 100), (7926, 50), (7880, 50)][:0] or
       [(7880, 50), (7926, 50), (7926, 100), (7921, 100), (7921, 118), (7926, 118), (7926, 180), (7911, 180), (7911, 230), (7880, 230)], "////")
    hp([(7926, 50), (8076, 50), (8076, 150), (8046, 150), (8046, 120), (7956, 120), (7956, 150), (7926, 150), (7926, 112),
        (7931, 112), (7931, 106), (7926, 106)], "\\\\\\\\")
    hp([(7921, 100), (7926, 100), (7926, 106), (7921, 106)], None, "#7f7f7f", 0.3)
    hp([(7888, 113), (7990, 113), (7990, 137), (7888, 137)], None, "white", 0.45)
    hp([(7956, 107), (7980, 107), (7980, 143), (7956, 143)], None, "#d0d0d0", 0.45)
    hp([(7966, 120), (8036, 120), (8036, 132), (7966, 132)], "xx", "white", 0.35)
    hp([(7995, 50), (8007, 50), (8007, 120), (7995, 120)], None, "white", 0.3)
    hp([(7989, 132), (8013, 132), (8013, 200), (7989, 200)], None, "#e6e6e6", 0.35)
    sh.line([E(7870, 0), E(8090, 0)], lw=0.18, ls="center")
    sh.line([E(7870, 125), E(8000, 125)], lw=0.13, ls="center")
    sh.dim(E(8076, 0), E(8076, 150), E(8100, 0)[0], "v", text="Ø300")
    sh.dim(E(7880, 0), E(7880, 125), E(7860, 0)[0], "v", text="PCD 250")
    sh.dim(E(7926, 150), E(7956, 150), E(7926, 215)[1], "h", text="30")
    sh.dim(E(7926, 150), E(8076, 150), E(7926, 235)[1], "h", text="150")
    sh.labels_column([(E(8001, 190), "cảm biến P4, lỗ ren 1/2\"-20UNF", "melt_sensor_p4"),
                      (E(7968, 140), "đai ốc M24 + vòng đệm"), (E(8020, 126), "băng nhiệt Ø260", "melt_heater_bands"),
                      (E(7940, 125), "bulông cấy M24 chịu nhiệt (8 cái)"), (E(7923, 103), "vòng kín kim loại trong rãnh"),
                      (E(7929, 109), "gờ định tâm Ø224 × 5"), (E(7900, 160), "thân bơm + đĩa bích Ø360", "melt_gear_pump"),
                      (E(8040, 80), "bích ra P4, lòng Ø100", "melt_pump_adapter_out")], E(8090, 0)[0] + 22, ey0 + 118, step=7.5)
    # ---------------------------------------------------------------- tables, notes, parts list
    rows = [[f"{i + 1}", f["joint"][:42], f["od_text"][:16], f["bolts"][:44], f["bore"][:18]] for i, f in enumerate(fl)]
    sh.table(925, 815, [("#", 8, "c"), ("Mối nối", 70, "l"), ("Ø ngoài", 30, "l"), ("Bulông", 96, "l"), ("Lòng chảy", 44, "l")], rows,
             title="Bảng bích đường chảy (design.md §6.3)")
    rows = [["P1 / T1", "X 5 876 / 5 916", "HH 350 bar → ngắt cứng (s_11)"], ["đĩa nổ 1", "X 5 896, −Y", "đứt → ngắt (s_12)"],
            ["P2", "X 6 521", "chênh áp lưới"], ["P3", "X 7 388", "PIC → tốc độ bơm (s_20)"], ["P4", "X 8 001", "HH 330 bar → dừng bơm + vít"],
            ["đĩa nổ 2", "X 8 001, −Y", "đứt → dừng (s_08, s_13)"], ["P5 / T5", "X 9 006 / 9 046", "áp + nhiệt vào khuôn"]]
    sh.table(560, 300, [("Cảm biến", 22, "c"), ("Vị trí", 38, "l"), ("Chức năng / liên động", 86, "l")], rows,
             title="Cảm biến và an toàn (transducers)")
    sh.notes(560, 248, "Ghi chú (notes)", [
        "1. Lưu lượng do cân quyết định; P3 giữ áp hút bơm ≈ 50 bar bằng tốc độ bơm bánh răng (s_20).",
        "2. Mọi bích kín kim loại có gờ định tâm, đồng trục Z 1 200; bích và ống có băng nhiệt hoặc vỏ inox.",
        "3. Van khởi động: chốt xoay 2 vị trí, xi lanh thuỷ lực theo Y; vị trí khởi động xả xuống máng và xe hứng.",
        "4. HPU phía −Y: 2 cặp ống mềm (h_01 bộ lọc, h_02 van khởi động).",
        "5. Bơm Maag GU 100/125: động cơ đứng 45 kW → hộp góc i ≈ 14 → các-đăng → trục bơm (−Y).",
    ], width=200)
    sheet_parts_list(sh, 925, 738, rowh=5.0)
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
