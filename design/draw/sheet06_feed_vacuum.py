#!/usr/bin/env python3
"""Sheet 06 – feeding (mezzanine, stair, feeders, chute, side feeder) and vacuum system (layout + schematic)."""
from geom import P, ORDER
from sheet import Sheet, VP, fmt, PT, sheet_parts_list, MIN_FS
import drafting as dft

FEED = [q for q in ORDER if P[q]["group"] == "feed"]
VAC = [q for q in ORDER if P[q]["group"] == "vacuum"]
NOCTX = [q for q in ORDER if P[q]["group"] != "context"]


def main():
    sh = Sheet(6, "feed-vacuum", "Cấp liệu và chân không (feeding and vacuum)", size="A0", scale="1:50; 1:20",
               subtitle="Sàn thao tác, cầu thang, cân cấp liệu, ống nạp, side feeder; hệ chân không hai vùng: bố trí và sơ đồ")
    ax = sh.ax
    k = 50
    A = VP(sh, "front", k, 40 + 7800 / k / 2, 640, (-2000 + 5800) / 2, 0, clip=(-2000, 5800, -100, 6400))
    A.draw(NOCTX)
    ab = A.box()
    sh.heading((ab[0] + ab[1]) / 2, ab[3] + 32, "A. Cấp liệu – hình chiếu đứng", "1:50")
    A.balloons(["feed_vacuum_loader", "feed_main_hopper", "feed_main_feeder", "feed_additive_feeder", "feed_control_cabinet",
                "feed_platform_railing", "feed_stair", "feed_platform_deck", "feed_platform_columns_front", "feed_downpipe",
                "sidefeed_feeder", "sidefeed_feeder_hopper", "feed_conveying_line", "ctrl_estop_platform"], sides=("top",), offset=5, rows=2, r=4.8)
    for z, t in ((3000, "3 000 sàn"), (4100, "4 100 tay vịn"), (5800, "5 800"), (6300, "6 300")):
        x, y = A.P((-5800, 0, z))
        sh.line([(x + 1, y), (x + 4, y)], lw=0.18)
        sh.text(x + 4.5, y, t, ha="left", va="center")
    A.dimw((-5700, 0, 0), (-2700, 0, 0), -700, "h", text="cầu thang 45°, 15 bậc")
    B = VP(sh, "top", k, A.ox, 470, A.uc, 0 - 250, clip=(-2000, 5800, -2400, 2900))
    B.draw(NOCTX)
    bb = B.box()
    sh.heading((bb[0] + bb[1]) / 2, bb[3] + 8, "B. Sàn thao tác – mặt bằng (lưới không tô)", "1:50")
    d = P["feed_platform_deck"]["bbox_mm"]
    B.dimw((d[0], d[3], 0), (d[1], d[3], 0), -(d[3] + 700), "h")
    B.dimw((d[0], d[2], 0), (d[0], d[3], 0), -(d[0] - 600), "v")
    B.balloons(["feed_platform_columns_rear", "feed_control_cabinet", "sidefeed_cart"], sides=("bottom",), offset=10, r=4.8)
    # C: feed chute 1:20
    k2 = 20
    Cv = VP(sh, "front", k2, 262 + 1800 / k2 / 2, 640, (-700 + 1100) / 2, 1400, clip=(-700, 1100, 1400, 3800))
    ids_c = FEED + [q for q in ("barrel_b1", "barrel_b2", "barrel_joint_1", "lantern", "gearbox", "barrel_thermocouples", "util_cw_throat_hoses") if q in P]
    Cv.draw([q for q in ids_c if not q.startswith("feed_platform_columns")], floor=False)
    Cv.breaks("left", "right", "bottom")  # clipped view (review M4)
    cb = Cv.box()
    sh.heading((cb[0] + cb[1]) / 2, cb[3] + 32, "C. Ống nạp liệu", "1:20")
    Cv.balloons(["feed_main_feeder", "feed_feeder_sleeves", "feed_downpipe", "feed_additive_tube", "feed_flex_sleeve", "feed_hopper",
                 "feed_throat", "barrel_b1"], sides=("top", "right"), offset=6, r=4.8)
    Cv.dimw((90, 0, 1900), (590, 0, 1900), 1960, "h", text="500")
    # D: side feeder from +X 1:20
    D_ = VP(sh, "die_end", k2, 420 + 2600 / k2 / 2, 700, 900, 800, clip=(-400, 2200, 800, 1800))
    ids_d = [q for q in FEED if q.startswith("sidefeed")] + [q for q in ("barrel_b2", "barrel_support_1", "base_frame_process", "util_cw_sidefeed_hoses") if q in P]
    D_.draw(ids_d, floor=False)
    D_.breaks("bottom")
    db = D_.box()
    sh.heading((db[0] + db[1]) / 2, db[3] + 32, "D. Side feeder vào cửa bên B2 (nhìn từ +X)", "1:20")
    D_.balloons(["sidefeed_adapter", "sidefeed_barrel", "sidefeed_hopper", "sidefeed_gearbox", "sidefeed_motor", "sidefeed_cart",
                 "sidefeed_downpipe", "barrel_b2", "util_cw_sidefeed_hoses"], sides=("top",), offset=5, rows=2, r=4.8)
    D_.dimw((0, 260, 1200), (0, 1100, 1200), 860, "h", text="thân 770")
    # E: vacuum plan 1:50
    E = VP(sh, "top", k, 660 + 4800 / k / 2, 612, -(1600 + 6400) / 2, 0 + 1350, clip=(-6400, -1600, -800, 3500))
    E.draw(NOCTX)
    E.breaks("left", "right", "bottom")
    eb = E.box()
    sh.heading((eb[0] + eb[1]) / 2, eb[3] + 8, "E. Chân không – mặt bằng", "1:50")
    E.balloons(["vac_separator", "vac_pump_unit", "vac_exhaust", "vac_pipe_3", "vac_control_box", "util_cw_vac_hoses"], sides=("right",), offset=8, r=4.8)
    # F: vacuum elevation from +X 1:20
    F = VP(sh, "die_end", k2, 250 + 4000 / k2 / 2, 300, -1450, 0, clip=(-3450, 550, -50, 2500))
    ids_f = VAC + [q for q in ("barrel_b3", "barrel_b5", "barrel_cover_c3", "barrel_cover_c6", "base_frame_process", "util_cw_vac_hoses",
                               "util_air_tube_vac", "barrel_cable_tray", "barrel_heater_jboxes", "barrel_support_2") if q in P]
    F.draw(ids_f)
    fb = F.box()
    sh.heading((fb[0] + fb[1]) / 2, fb[3] + 34, "F. Chân không – nhìn từ +X", "1:20", sub="vùng 2 (B5) DN150 qua nắp vòm; vùng 1 (B3) DN100 qua van tiết lưu")
    F.balloons(["barrel_vent_dome", "vac_valve", "vac_bellows", "vac_pipe", "vac_pipe_support", "vac_separator", "vac_drain", "vac_pipe_2",
                "vac_pump_unit", "vac_control_box", "vac_exhaust", "vac_bleed_valve", "vac_pipe_3", "vac_reg_valve_2", "barrel_vent_dome_2",
                "vac_valve_2", "vac_bellows_2", "vac_gauge_dome", "vac_gauge_dome_2"], sides=("top", "left"), offset=6, rows=2, r=4.8)
    # G: vacuum schematic
    gx, gy = 480, 420
    sh.text(gx + 60, gy + 26, "G. Sơ đồ chân không (vacuum schematic)", 11, va="bottom", weight="bold")
    vc = "#6a3d9a"
    nodes = {"dome2": (gx + 30, gy - 10, "vòm vùng 1\nB3 ≈ 50 mbar"), "dome1": (gx + 30, gy - 62, "vòm vùng 2\nB5 5–20 mbar"),
             "v2": (gx + 105, gy - 10, "van bi DN100\n+ ống xếp"), "v1": (gx + 105, gy - 62, "van bướm DN150\n+ ống xếp"),
             "reg": (gx + 180, gy - 10, "van tiết lưu\nvùng 1"), "sep": (gx + 255, gy - 36, "bình tách ngưng\nØ600, ống xoắn"),
             "drain": (gx + 255, gy - 96, "nồi xả ngưng"), "roots": (gx + 330, gy - 36, "bơm Roots\n2 000 m³/h"),
             "screw": (gx + 405, gy - 36, "bơm trục vít khô\n400 m³/h")}
    for key, (x, y, t) in nodes.items():
        dft.sym_box(sh, (x, y), 58, 16, t)

    def fl(a, b, lab=None, via=None):
        pa, pb = nodes[a][:2], nodes[b][:2]
        pts = [(pa[0] + 29, pa[1])] + (via or []) + [(pb[0] - 29, pb[1])]
        sh.line(pts, lw=0.6, c=vc)
        sh.arrow(pts[-1], pts[-2], size=3, c=vc)
        if lab:
            sh.text((pts[0][0] + pts[1][0]) / 2, pts[0][1] + 1.2, lab, ha="center", va="bottom", color=vc)
    fl("dome2", "v2", "DN100")
    fl("v2", "reg")
    fl("reg", "sep", None, via=[(gx + 215, gy - 10), (gx + 215, gy - 30)])
    fl("dome1", "v1", "DN150")
    fl("v1", "sep", None, via=[(gx + 215, gy - 62), (gx + 215, gy - 42)])
    fl("sep", "roots", "DN150")
    fl("roots", "screw")
    sh.line([(gx + 434, gy - 36), (gx + 450, gy - 36), (gx + 450, gy - 10)], lw=0.6, c=vc)
    sh.arrow((gx + 450, gy - 10), (gx + 450, gy - 20), size=3, c=vc)
    sh.text(gx + 450, gy - 8, "xả lên mái", ha="center", va="bottom")
    sh.line([(gx + 255, gy - 44), (gx + 255, gy - 88)], lw=0.5, c="#1f5fbf")
    sh.arrow((gx + 255, gy - 88), (gx + 255, gy - 70), size=3, c="#1f5fbf")
    for (x, y, f, t) in ((gx + 30, gy + 12, "PI", "V1"), (gx + 30, gy - 40, "PIT", "V2"), (gx + 180, gy + 12, "PI", "V3"), (gx + 255, gy - 14, "LG", "V4")):
        dft.sym_instrument(sh, (x, y), f, t, r=6.5)
    sh.notes(40, 250, "Ghi chú (notes)", [
        "1. Sàn thao tác Z 3 000: lưới mạ kẽm trên dầm HEA180 + dầm phụ IPE160 (beams_mm), cột HEB200; lan can vàng 1 100; cầu thang 45° phía −Y.",
        "2. Dầm chính X −450 ngắt tại Y ±260 quanh lỗ ống rơi chính, hai dầm viền tựa trên dầm phụ X −760 và −140.",
        "3. Hạt PET: silo → máy hút liệu → phễu cân → cân BSP-150 → ống mềm → ống rơi Ø250 → ống mềm → phễu 45° → miệng nạp B1.",
        "4. Side feeder trục vít đôi phía +Y trên xe có bánh, kéo ra theo +Y khi bảo trì.",
        "5. Hai vùng chân không chung bình tách và cụm bơm; vùng 1 ≈ 50 mbar nhờ van tiết lưu, vùng 2 5–20 mbar; ống sau bình tách DN150.",
    ], width=420)
    sheet_parts_list(sh, 925, 815, rowh=4.9)
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
