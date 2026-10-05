#!/usr/bin/env python3
"""Sheet 01 – general arrangement (A0, 1:50)."""
from matplotlib.patches import Circle

from geom import ORDER, P, NUM
from sheet import Sheet, VP, fmt, PT, bom_rows, MIN_FS

FS_GA = 11.0  # GA tables and notes: cap height 2.8 mm


def envelope(ctx=False):
    bs = [p["bbox_mm"] for p in P.values() if (ctx or p["group"] != "context") and p["id"] != "ctx_floor"]
    return [min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs), max(b[3] for b in bs), min(b[4] for b in bs),
            max(b[5] for b in bs)]


FRONT_B = ["ctrl_signal_tower", "drive_motor", "drive_coupling_guard", "gearbox", "lantern", "lube_pump_motor",
           "feed_hopper", "feed_downpipe", "feed_main_feeder", "feed_main_hopper", "feed_vacuum_loader",
           "feed_conveying_line", "feed_additive_feeder", "feed_platform_railing", "feed_platform_columns_front",
           "barrel_b1", "barrel_b2", "barrel_vent_dome_2", "barrel_vent_dome", "barrel_cover_c6", "barrel_cover_c1",
           "melt_head_adapter", "melt_startup_valve", "melt_screen_changer", "melt_gear_pump", "melt_pump_motor",
           "melt_static_mixer", "die_end_plate_op", "die_cart", "ctx_roll_middle", "base_frame_drive", "base_frame_process",
           "barrel_cw_supply", "ctrl_estops", "melt_purge_cart", "melt_stand_sc", "melt_stand_pump", "sidefeed_motor",
           "sidefeed_feeder", "ctrl_machine_cabinet", "util_air_drop", "barrel_joint_1", "ctrl_estop_melt", "ctrl_estop_die",
           "ctrl_estop_platform", "ctrl_hmi"]
PLAN_B = ["ctrl_drive_cabinet", "ctrl_heater_cabinet", "feed_stair", "feed_platform_deck", "feed_control_cabinet",
          "vac_pipe", "vac_separator", "vac_pump_unit", "vac_exhaust", "melt_hpu", "melt_sc_drive", "melt_pump_gearbox",
          "sidefeed_cart", "lube_oil_cooler", "drive_motor_terminal_box", "barrel_cable_tray", "ctrl_floor_trench",
          "die_cart_rails", "ctx_roll_stand", "ctx_roll_drives", "melt_sc_backflush", "die_thermal_bolts",
          "feed_platform_columns_rear", "vac_pipe_3", "ctrl_die_bolt_cabinet", "melt_heater_jbox", "vac_reg_valve_2",
          "die_junction_box", "ctrl_infeed_mv", "ctrl_infeed_lv"]
DIE_B = ["die_deckles", "die_drip_pan", "ctx_sheet", "die_lifting_lugs"]
DRIVE_B = ["drive_encoder", "base_feet", "drive_motor_base", "ctrl_cable_drop"]
ESTOPS = [("ES1–3", "ctrl_estops", None), ("ES4", "ctrl_estop_melt", None), ("ES5", "ctrl_estop_die", None),
          ("ES6", "ctrl_estop_platform", None), ("ES7", "ctrl_hmi", "trên vỏ HMI"), ("ES8", "ctrl_machine_cabinet", "mặt +Y tủ đầu máy"),
          ("ES9", "die_junction_box", "cửa hộp đấu dây khuôn")]


def main():
    env = envelope()
    W_ = env[3] - env[2]
    sh = Sheet(1, "ga", "Bố trí chung (general arrangement)", size="A0", scale="1:50",
               subtitle="Hình chiếu đứng, mặt bằng, nhìn từ đầu khuôn và đầu dẫn động; vị trí nút dừng khẩn")
    k = 50
    fx = 245 + 18400 / k / 2
    front = VP(sh, "front", k, fx, 600, -3400, 0, clip=(-12600, 5800, -100, 6400))
    front.draw(ORDER)
    fb = front.box()
    plan = VP(sh, "top", k, fx, 470 - 5000 / k, -3400, 0, clip=(-12600, 5800, -2900, 5000))
    plan.draw(ORDER)
    pb = plan.box()
    drv = VP(sh, "drive_end", k, fb[0] - 47 - 158 / 2, 600, 1050, 0, clip=(-2900, 5000, -100, 6400))
    drv.draw(ORDER)
    db = drv.box()
    die = VP(sh, "die_end", k, fb[1] + 55 + 158 / 2, 600, -1050, 0, clip=(-5000, 2900, -100, 6400))
    die.draw(ORDER)
    eb = die.box()
    sh.heading((fb[0] + fb[1]) / 2, fb[3] + 40, "Hình chiếu đứng (front elevation), nhìn từ +Y", "1:50")
    sh.heading((pb[0] + pb[1]) / 2, pb[3] + 30, "Mặt bằng (plan view), nhìn từ +Z", "1:50")
    sh.heading((db[0] + db[1]) / 2, db[3] + 40, "Nhìn từ đầu dẫn động (−X)", "1:50", fs=12)
    sh.heading((eb[0] + eb[1]) / 2, eb[3] + 40, "Nhìn từ đầu khuôn (+X)", "1:50", fs=12)
    front.cline((-5800, 0, 1200), (10300, 0, 1200))
    plan.cline((-5800, 0, 0), (10300, 0, 0))
    for vp in (die, drv):
        vp.cline((0, 0, -100), (0, 0, 6400))
        vp.cline((0, -2600, 1200), (0, 2600, 1200))
    FB = [q for q in FRONT_B if q in P]
    front.balloons([q for q in FB if front.v.uv(P[q]["center_mm"])[1] > 1300], sides=("top",), offset=8, rows=2)
    front.balloons([q for q in FB if front.v.uv(P[q]["center_mm"])[1] <= 1300], sides=("bottom",), offset=6, rows=1)
    plan.balloons([q for q in PLAN_B if q in P], sides=("top",), offset=6, rows=2)
    die.balloons(DIE_B, sides=("right",), offset=34)
    drv.balloons(DRIVE_B, sides=("left",), offset=10)
    for tag, pid, _ in ESTOPS:
        p = P[pid]
        pts = [q for q in p.get("positions_mm", [])] or [p["center_mm"]]
        for i, q in enumerate(pts):
            x, y = plan.P(q)
            sh.ax.add_patch(Circle((x, y), 2.0, fc="#c8102e", ec="k", lw=0.3 * PT, zorder=45))
            t = tag if len(pts) == 1 else f"ES{i + 1}"
            sh.text(x + 2.5, y - 2.5, t, ha="left", va="top", color="#c8102e", weight="bold", zorder=46,
                    bbox=dict(fc="white", ec="none", pad=0.1))
    yb = pb[2] - 4
    xad, xdb = P["melt_die_adapter"]["bbox_mm"][0], P["die_body_upper"]["bbox_mm"][0]
    stations = [-5650, -4975, -2950, -2300, -750, 0, 676, 1690, 2704, 3718, 4732, 5746, 6596, 7301, 7926, xad, xdb, 9576, 9776]
    for x in stations:
        xs, _ = plan.P((x, 0, 0))
        sh.line([(xs, pb[2] - 1), (xs, yb - 2)], lw=0.18)
        sh.text(xs, yb - 3, fmt(x), ha="center", va="top", rotation=90)
    x0s, _ = plan.P((0, 0, 0))
    sh.ax.add_patch(Circle((x0s, yb - 2), 1.1, fc="white", ec="k", lw=0.3 * PT, zorder=40))
    sh.text(plan.P((-5800, 0, 0))[0] + 3, yb - 3, "X (mm), gốc X = 0 tại mặt xi lanh B1 phía hộp số", ha="left", va="top")
    y1 = yb - 26
    sh.dim(plan.P((env[0], 0, 0)), plan.P((env[1], 0, 0)), y1, "h", value=env[1] - env[0])
    sh.text(plan.P((2100, 0, 0))[0], y1 - 1.0, "máy, không kể cụm cán láng", ha="center", va="top")
    e2 = envelope(True)
    sh.dim(plan.P((env[0], 0, 0)), plan.P((e2[1], 0, 0)), y1 - 13, "h", value=e2[1] - env[0])
    sh.text(plan.P((3400, 0, 0))[0], y1 - 14.0, "cả dây chuyền tới cuối ray cụm cán", ha="center", va="top")
    plan.dimw((-5700, env[2], 0), (-5700, env[3], 0), plan.v.uv((-5700 - 9 * k, 0, 0))[0], "v", value=W_)
    plan.dimw((-5700, env[2], 0), (-5700, 0, 0), plan.v.uv((-5700 - 18 * k, 0, 0))[0], "v")
    d = P["feed_platform_deck"]["bbox_mm"]
    plan.dimw((d[0], d[3], 0), (d[1], d[3], 0), -(d[3] + 1300), "h")
    xo = fb[1] + 3
    for z, lab in ((0, "±0 sàn"), (650, "650 khung"), (1200, "1 200 tâm trục"), (1650, "1 650 vỏ che"),
                   (2610, "2 610 động cơ"), (3000, "3 000 sàn thao tác"), (4100, "4 100 tay vịn"), (6300, "6 300 ống hút liệu")):
        xs, ys = front.P((-5800, 0, z))
        sh.line([(xs + 1, ys), (xs + 5, ys)], lw=0.18)
        sh.text(xo + 3, ys, lab, ha="left", va="center")
    die.dimw((0, env[2], 0), (0, env[3], 0), -1100, "h", value=W_)
    die.dimw((0, 2800, 0), (0, 2800, 1200), 3250, "v")
    die.dimw((0, 2800, 0), (0, 2800, 3000), 3700, "v")
    die.dimw((0, 2800, 0), (0, 2800, env[5]), 4150, "v", value=env[5])
    drv.dimw((0, -1000, 650), (0, 1000, 650), 360, "h", text="khung 2 000")
    drv.dimw((0, 1000, 0), (0, 1000, 2610), -1400, "v")
    front.dimw((9576, 0, 1200), (9776, 0, 1200), 330, "h", text="200")
    sh.text(*front.P((9680, 0, 240)), "khe gió", ha="center", va="top")
    # the full BOM is on sheet 09, so the GA list drops the material column and uses 11 pt (cap height 2.8 mm)
    ga_ids = sorted(set(sh.ballooned) | set(sh.mentioned), key=lambda q: NUM[q])
    ga_rows = [[r[0], r[1], r[2], r[3], r[5]] for r in bom_rows(ga_ids)]
    sh.table(925, 815, [("Số", 12, "c"), ("Mã (id)", 70, "l"), ("Tên chi tiết", 146, "l"), ("SL", 13, "c"), ("G", 9, "c")], ga_rows,
             rowh=6.4, fs=FS_GA, hfs=FS_GA, zebra=True, title="Chi tiết có số bóng trên tờ này (danh mục đủ: tờ 09)")
    rows = []
    for tag, pid, note in ESTOPS:
        p = P[pid]
        pts = p.get("positions_mm") or [p["center_mm"]]
        for i, q in enumerate(pts):
            t = tag if len(pts) == 1 else f"ES{i + 1}"
            rows.append([t, NUM[pid], fmt(q[0]), fmt(q[1]), fmt(q[2]), note or p["name_vi"]])
            sh.mentioned.add(pid)
    sh.table(30, 236, [("Nút", 16, "c"), ("Số", 11, "c"), ("X", 20, "c"), ("Y", 20, "c"), ("Z", 18, "c"), ("Vị trí", 95, "l")], rows,
             title="Nút dừng khẩn (e-stops) – vị trí tâm, mm", fs=FS_GA, hfs=FS_GA, rowh=5.6)
    sh.notes(30, 158, "Ghi chú chung (general notes)", [
        "1. Kích thước bằng mm. Z tính từ mặt sàn. X = 0 tại mặt xi lanh B1 phía hộp số, +X theo chiều chảy, +Y phía người vận hành.",
        "2. Phép chiếu góc thứ nhất (ISO E): nhìn từ đầu dẫn động đặt bên trái, từ đầu khuôn đặt bên phải, mặt bằng đặt dưới.",
        "3. Nét liền đậm: cạnh thấy; nét đứt: cạnh khuất; nét chấm gạch: đường tâm; nét gạch hai chấm: bối cảnh (cụm cán, tấm).",
        "4. G = kích thước hoặc vị trí giả định (design/design.md). Số bóng = số trong danh mục, dùng chung cho mọi tờ.",
        "5. Sàn thao tác là sàn lưới: trong mặt bằng chỉ vẽ viền lưới, dầm thép vẫn che máy bên dưới.",
        "6. Sơ đồ P&ID và liên động: tờ 07. Tuyến tiện ích: tờ 08. Danh mục đủ: tờ 09. Vấn đề thiết kế: drawings/design_issues.md.",
    ], width=420, fs=FS_GA, lh=1.4)
    cols = [("Thông số chính (main data)", 76, "l"), ("Giá trị", 72, "l")]
    data = [["Kiểu máy", "ZE 155 A UT, đồng hướng"], ["Vít D / tâm a", "169 / 142 mm"], ["Chiều dài gia công", "34D = 5 746"],
            ["Tốc độ / mômen", "400 v/ph, 2 × 35 kNm"], ["Động cơ chính", "1 500 kW, AMI 450L4 (G)"], ["Cao tâm trục", "1 200"],
            ["Năng suất", "3 500 kg/h PET"], ["Môi khuôn / tấm", "2 400 / 2 100"], ["Khe trục cán", "X 9 776, Z 1 200"],
            ["Bao máy", f"{fmt(env[1] - env[0])} × {fmt(W_)} × {fmt(env[5])}"]]
    sh.table(236, 236, cols, data, fs=FS_GA, hfs=FS_GA, rowh=5.6)
    lx, ly = 410, 236
    sh.text(lx, ly + 1.5, "Kiểu nét (line types)", 11, va="bottom", weight="bold")
    for i, (ls, lw, lab) in enumerate((("solid", 0.35, "cạnh thấy (visible)"), ("hidden", 0.18, "cạnh khuất (hidden)"),
                                       ("center", 0.18, "đường tâm (centre line)"), ("phantom", 0.18, "bối cảnh (phantom)"))):
        y = ly - 6 - i * 7
        sh.line([(lx, y), (lx + 28, y)], lw=lw, ls=ls, c="#555555" if ls == "phantom" else "k")
        sh.text(lx + 32, y, lab, va="center")
    sh.balloon((lx + 5, ly - 37), (lx + 5, ly - 37), 12, dot=False)
    sh.text(lx + 13, ly - 37, "số bóng = số trong danh mục", va="center")
    sh.ax.add_patch(Circle((lx + 5, ly - 49), 2.0, fc="#c8102e", ec="k", lw=0.3 * PT, zorder=45))
    sh.text(lx + 13, ly - 49, "nút dừng khẩn ES (mặt bằng)", va="center")
    st = [["Tủ đầu máy", "−5 650", "−5 150"], ["Động cơ 1 500 kW", "−4 975", "−2 950"], ["Khớp nối + vỏ che", "−2 980", "−2 300"],
          ["Hộp số", "−2 300", "−750"], ["Lantern", "−750", "0"], ["Xi lanh B1…B6", "0", "5 746"], ["Đầu xi lanh", "5 746", "5 996"],
          ["Van khởi động", "5 996", "6 446"], ["Bộ lọc lưới", "6 596", "7 301"], ["Bơm bánh răng", "7 476", "7 926"],
          ["Ống + bộ trộn tĩnh", "8 076", fmt(xad)], ["Khuôn chữ T", fmt(xdb), "9 576"], ["Cụm cán láng (bối cảnh)", "9 376", "11 200"]]
    sh.table(600, 236, [("Trạm (station)", 64, "l"), ("X từ", 26, "c"), ("X tới", 26, "c")], st, fs=FS_GA, hfs=FS_GA, rowh=5.6)
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
