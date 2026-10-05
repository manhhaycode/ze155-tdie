#!/usr/bin/env python3
"""Sheet 07 – P&ID (ISO 10628 / ISA 5.1 style): process, vacuum, cooling water, lube oil, hydraulics, air,
power one-line and the safety / interlock chain; cause-and-effect table read from design.md §7."""
import re

from geom import P, NUM, CONN, ROOT
from sheet import Sheet, fmt, PT, wrap, MIN_FS
import drafting as dft

C = {"melt": "#c0392b", "material": "#8b5a2b", "water": "#1f5fbf", "vacuum": "#6a3d9a", "oil": "#b06a00", "hydraulic": "#1e7b34",
     "air": "#0099b8", "power": "#d62728", "signal": "#222222", "mechanical": "#7f7f7f"}
LW = {"melt": 0.9, "material": 0.6, "water": 0.5, "vacuum": 0.6, "oil": 0.5, "hydraulic": 0.5, "air": 0.45, "power": 0.45, "signal": 0.3,
      "mechanical": 1.0}
LS = {"hydraulic": (0, (7, 2.5)), "air": (0, (2.5, 2)), "power": (0, (11, 2.5, 2.5, 2.5)), "signal": (0, (4.5, 2.5))}
CID = {c["id"]: c for c in CONN}


def ln(sh, pts, med, cid=None, arrow=True, lab_at=None, ret=False):
    ls = LS.get(med, "solid")
    if ret:
        ls = (0, (6, 2.5))
    sh.line(pts, lw=LW[med], ls=ls, c=C[med], z=20)
    if arrow:
        sh.arrow(pts[-1], pts[-2], size=3.0, c=C[med], z=21)
    if cid:
        i = lab_at if lab_at is not None else max(range(len(pts) - 1), key=lambda j: abs(pts[j][0] - pts[j + 1][0]) + abs(pts[j][1] - pts[j + 1][1]))
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        horiz = abs(x1 - x0) >= abs(y1 - y0)
        sh.text((x0 + x1) / 2 + (0 if horiz else 1.5), (y0 + y1) / 2 + (1.2 if horiz else 0), cid, ha="center" if horiz else "left",
                va="bottom" if horiz else "center", color=C[med], zorder=23, bbox=dict(fc="white", ec="none", pad=0.1))


def box(sh, c, w, h, t, pid=None, fc="white", ls="solid"):
    dft.sym_box(sh, c, w, h, t, fc=fc, ls=ls)
    if pid:
        # part number as a tag just outside the top-left corner (inside, it collides with the box text at 2.5 mm)
        sh.text(c[0] - w / 2, c[1] + h / 2 + 0.5, str(NUM[pid]), ha="left", va="bottom", zorder=45, color="#555555")
        sh.mentioned.add(pid)


def inst(sh, c, f, tag, panel=False, to=None, med="signal"):
    dft.sym_instrument(sh, c, f, tag, panel=panel)
    if to:
        sh.line([(c[0], c[1] - 6.8), to], lw=0.3, ls=LS["signal"], c=C["signal"], z=19)


def cause_effect():
    txt = (ROOT / "design" / "design.md").read_text()
    a = txt.index("| Nguyên nhân | Tác động |")
    rows = []
    for l in txt[a:].splitlines()[2:]:
        l = l.strip()
        if not l.startswith("|"):
            break
        c = [x.strip() for x in l.strip("|").split("|")]
        rows.append(c[:2])
    return rows


def main():
    sh = Sheet(7, "process-utilities", "Sơ đồ P&ID và liên động (P&ID, interlocks)", size="A0", scale="không tỷ lệ (NTS)",
               subtitle="Quá trình, chân không, nước làm mát, dầu, thuỷ lực, khí nén, cấp điện, chuỗi dừng khẩn và liên động; số đường = id mối nối")
    ax = sh.ax
    yp = 690
    # ================================================================ process: feed, extruder, melt line
    sh.text(40, 812, "1. Quá trình (process): vật liệu → máy đùn → đường chảy → khuôn", 11, va="bottom", weight="bold")
    box(sh, (60, yp), 26, 16, "M\n1 500 kW", "drive_motor")
    box(sh, (100, yp), 34, 22, "hộp số\ni ≈ 3,73", "gearbox")
    ln(sh, [(73, yp), (83, yp)], "mechanical", "m_01", arrow=False)
    xb = [125, 165, 212, 259, 306, 353, 400]
    for i in range(6):
        box(sh, ((xb[i] + xb[i + 1]) / 2, yp), xb[i + 1] - xb[i], 20, f"B{i + 1}", f"barrel_b{i + 1}")
    ln(sh, [(117, yp), (125, yp)], "mechanical", arrow=False)
    sh.text(262, yp - 14, "máy đùn ZE 155 A UT 34D – 2 trục vít (screws)", ha="center", va="top")
    sh.mentioned.add("screws")
    box(sh, (150, 790), 34, 14, "máy hút liệu", "feed_vacuum_loader")
    box(sh, (150, 765), 34, 14, "phễu cân", "feed_main_hopper")
    box(sh, (150, 738), 34, 14, "cân LIW", "feed_main_feeder")
    inst(sh, (178, 738), "WIC", "01", panel=True)
    ln(sh, [(100, 805), (100, 790), (133, 790)], "material", "mat_01")
    sh.text(100, 806, "từ silo", ha="center", va="bottom")
    ln(sh, [(150, 783), (150, 772)], "material", "mat_02")
    ln(sh, [(150, 758), (150, 745)], "material")
    ln(sh, [(150, 731), (150, 700)], "material", "mat_03")
    box(sh, (215, 760), 30, 14, "cân phụ gia", "feed_additive_feeder")
    inst(sh, (240, 760), "WIC", "02", panel=True)
    ln(sh, [(215, 753), (215, 718), (153, 718)], "material", "mat_04")
    box(sh, (190, 648), 34, 14, "side feeder", "sidefeed_barrel")
    box(sh, (240, 648), 30, 14, "cân side", "sidefeed_feeder")
    inst(sh, (240, 630), "WIC", "03", panel=True)
    ln(sh, [(225, 648), (207, 648)], "material")
    ln(sh, [(190, 655), (190, 680)], "material", "mat_05")
    box(sh, (165, 625), 18, 10, "M 22 kW", "sidefeed_motor")
    ln(sh, [(174, 628), (180, 641)], "mechanical", "m_03", arrow=False)
    # melt line
    box(sh, (415, yp), 16, 20, "đầu\nXL", "melt_head_adapter")
    ln(sh, [(400, yp), (407, yp)], "melt")
    sh.text(403.5, yp - 11, "melt_01", ha="center", va="top", color=C["melt"], zorder=23)  # the 7 mm stub cannot hold its id
    inst(sh, (415, 722), "PT TT", "P1 T1", to=(415, 700))
    inst(sh, (415, 745), "PAHH", "350", panel=True, to=(415, 728.8))
    sh.ax.add_patch(__import__("matplotlib").patches.Polygon([(411, 666), (419, 666), (415, 672)], closed=True, fc="white", ec="k", lw=0.3 * PT, zorder=50))
    sh.text(415, 664, "RD1", ha="center", va="top")
    sh.line([(415, 672), (415, 680)], lw=0.3)
    sh.mentioned.add("melt_rupture_disc")
    dft.sym_valve(sh, (445, yp), 9, kind="gate")
    sh.text(445, yp + 7, "van khởi động", ha="center", va="bottom")
    sh.mentioned.add("melt_startup_valve")
    ln(sh, [(423, yp), (440.5, yp)], "melt", "melt_02", lab_at=0)
    ln(sh, [(445, yp - 4.5), (445, 655)], "melt", "melt_04")
    box(sh, (445, 645), 26, 12, "xe hứng", "melt_purge_cart")
    box(sh, (485, yp), 24, 22, "bộ lọc\nlưới", "melt_screen_changer")
    ln(sh, [(449.5, yp), (473, yp)], "melt", "melt_03", lab_at=0)
    inst(sh, (472, 720), "PT", "P2", to=(472, 700))
    inst(sh, (498, 760), "PDI", "P2/P3", panel=True)
    sh.line([(476, 726), (492, 755)], lw=0.3, ls=LS["signal"], c=C["signal"])
    ln(sh, [(485, yp + 11), (485, yp + 20), (508, 702)][:0] or [(497, 696), (505, 714)], "melt", "melt_09", arrow=True)
    sh.text(502, 715, "xả ngược", ha="right", va="bottom")
    dft.sym_pump(sh, (535, yp), 7, kind="gear")
    sh.text(535, yp - 9, "bơm bánh răng", ha="center", va="top")
    sh.mentioned.add("melt_gear_pump")
    ln(sh, [(497, yp), (528, yp)], "melt", "melt_05", lab_at=0)
    inst(sh, (518, 720), "PT", "P3", to=(518, 700))
    inst(sh, (518, 745), "PIC", "P3", panel=True, to=(518, 728.8))
    box(sh, (558, 660), 22, 12, "M 45 kW", "melt_pump_motor")
    ln(sh, [(547, 660), (535, 660), (535, 683)], "mechanical", "m_02", arrow=False)
    sh.line([(524.8, 745), (566, 745), (566, 666)], lw=0.3, ls=LS["signal"], c=C["signal"])
    sh.text(568, 742, "SC (s_20)", ha="left", va="top")
    inst(sh, (555, 720), "PT", "P4", to=(555, 700))
    sh.ax.add_patch(__import__("matplotlib").patches.Polygon([(551, 674), (559, 674), (555, 680)], closed=True, fc="white", ec="k", lw=0.3 * PT, zorder=50))
    sh.text(551, 676, "RD2 ", ha="right", va="center")
    sh.mentioned.update({"melt_rupture_disc_2", "melt_sensor_p4", "melt_sensor_p3", "melt_sensor_p2", "melt_sensor_head", "melt_sensor_die"})
    box(sh, (590, yp), 30, 14, "ống + bộ trộn", "melt_static_mixer")
    ln(sh, [(542, yp), (575, yp)], "melt", "melt_06", lab_at=0)
    inst(sh, (620, 722), "PT TT", "P5 T5", to=(620, 700))
    box(sh, (650, yp), 24, 24, "khuôn\nchữ T", "die_body_upper")
    ln(sh, [(605, yp), (638, yp)], "melt", "melt_07", lab_at=0)
    inst(sh, (650, 728), "TIC", "×20", panel=True, to=(650, 702))
    box(sh, (700, yp), 26, 24, "cụm cán\n(bối cảnh)", "ctx_sheet", ls="phantom")
    ln(sh, [(662, yp), (687, yp)], "melt", "melt_08", lab_at=0)
    box(sh, (680, 740), 34, 12, "tủ bulông nhiệt", "ctrl_die_bolt_cabinet")
    sh.line([(663, 740), (656, 740), (656, 702)], lw=0.3, ls=LS["signal"], c=C["signal"])
    sh.text(640, 760, "94 bulông nhiệt (s_07)", ha="center", va="bottom")
    # ================================================================ vacuum
    sh.text(250, 812, "2. Chân không (vacuum)", 11, va="bottom", weight="bold")
    ln(sh, [(235, 700), (235, 712)], "vacuum", "v_03", arrow=False)
    box(sh, (235, 717), 18, 10, "vòm 1", "barrel_vent_dome_2")
    inst(sh, (258, 725), "PI", "V1")
    dft.sym_valve(sh, (235, 735), 8, orient="v", kind="ball")
    sh.mentioned.update({"vac_valve_2", "vac_bellows_2", "vac_reg_valve_2", "vac_gauge_dome_2"})
    dft.sym_valve(sh, (235, 758), 8, orient="v", kind="throttle")
    ln(sh, [(235, 722), (235, 731)], "vacuum", arrow=False)
    ln(sh, [(235, 739), (235, 754)], "vacuum", arrow=False)
    ln(sh, [(235, 762), (235, 780), (455, 780)], "vacuum", "v_05")
    ln(sh, [(330, 700), (330, 712)], "vacuum", arrow=False)
    box(sh, (330, 717), 18, 10, "vòm 2", "barrel_vent_dome")
    inst(sh, (352, 725), "PIT", "V2")
    dft.sym_valve(sh, (330, 738), 8, orient="v", kind="pneumatic")
    sh.mentioned.update({"vac_valve", "vac_bellows", "vac_gauge_dome", "vac_pipe", "vac_pipe_3"})
    ln(sh, [(330, 722), (330, 734)], "vacuum", arrow=False)
    ln(sh, [(330, 742), (330, 798), (470, 798), (470, 791)], "vacuum", "v_01", lab_at=1)
    box(sh, (470, 780), 22, 22, "bình tách\nngưng", "vac_separator")
    ln(sh, [(470, 769), (470, 758)], "water", "v_04")
    box(sh, (470, 752), 22, 10, "nồi xả", "vac_drain")
    dft.sym_pump(sh, (510, 780), 6.5, kind="vacuum", label="Roots")
    dft.sym_pump(sh, (545, 780), 6.5, kind="vacuum", label="trục vít")
    box(sh, (578, 780), 18, 10, "giảm thanh", None)
    sh.mentioned.update({"vac_pump_unit", "vac_exhaust", "vac_pipe_2", "vac_control_box", "vac_bleed_valve"})
    ln(sh, [(481, 780), (503.5, 780)], "vacuum", "DN150")
    ln(sh, [(516.5, 780), (538.5, 780)], "vacuum")
    ln(sh, [(551.5, 780), (569, 780)], "vacuum")
    ln(sh, [(587, 780), (600, 780), (600, 805)], "vacuum", "v_02")
    sh.text(600, 806, "ra mái", ha="center", va="bottom")
    # ================================================================ lube oil
    yl = 590
    sh.text(40, 625, "3. Dầu bôi trơn hộp số (lube oil)", 11, va="bottom", weight="bold")
    box(sh, (60, yl), 30, 14, "carter", "gearbox")
    dft.sym_strainer(sh, (85, yl), 7)
    dft.sym_pump(sh, (105, yl), 6, kind="gear")
    box(sh, (105, yl - 18), 16, 8, "M 4 kW", "lube_pump_motor")
    dft.sym_valve(sh, (105, yl + 15), 7, kind="relief")
    box(sh, (140, yl), 24, 14, "lọc kép", "lube_filter_duplex")
    inst(sh, (140, yl + 18), "PDI", "L1")
    box(sh, (180, yl), 26, 14, "làm mát", "lube_oil_cooler")
    inst(sh, (215, yl + 16), "PSL", "s_14")
    inst(sh, (215, yl - 16), "TT", "s_14")
    ln(sh, [(75, yl), (81.5, yl)], "oil", "o_01")
    ln(sh, [(88.5, yl), (99, yl)], "oil")
    ln(sh, [(111, yl), (128, yl)], "oil")
    ln(sh, [(152, yl), (167, yl)], "oil")
    ln(sh, [(193, yl), (230, yl), (230, yl - 30), (60, yl - 30), (60, yl - 7)], "oil", "o_02", lab_at=2)
    sh.line([(205, yl), (208.2, yl + 12)], lw=0.3, ls=LS["signal"], c=C["signal"])
    sh.line([(205, yl), (208.2, yl - 12)], lw=0.3, ls=LS["signal"], c=C["signal"])
    sh.mentioned.update({"lube_pipe_return", "lube_pipe_pressure", "lube_unit_frame"})
    # ================================================================ cooling water
    sh.text(250, 625, "4. Nước làm mát (cooling water)", 11, va="bottom", weight="bold")
    ys_, yr_ = 605, 540
    ln(sh, [(250, ys_), (640, ys_)], "water", "w_01", arrow=False)
    ln(sh, [(640, yr_), (250, yr_)], "water", "w_04", ret=True)
    sh.text(248, ys_, "CWS từ\nnhà máy", ha="right", va="center", color=C["water"])
    sh.text(248, yr_, "CWR về\nnhà máy", ha="right", va="center", color=C["water"])
    dft.sym_valve(sh, (262, ys_), 7, kind="ball")
    dft.sym_strainer(sh, (276, ys_), 7)
    sh.mentioned.update({"util_cw_supply_riser", "util_cw_return_riser", "barrel_cw_supply", "barrel_cw_return"})
    zx = 300
    ln(sh, [(zx, ys_), (zx, 588)], "water", arrow=False)
    dft.sym_valve(sh, (zx, 584), 7, orient="v", kind="ball")
    dft.sym_strainer(sh, (zx + 10, 575), 6)
    dft.sym_valve(sh, (zx, 566), 7, orient="v", kind="solenoid")
    box(sh, (zx + 22, 553), 22, 10, "vùng xi lanh", "barrel_cw_valves")
    dft.sym_valve(sh, (zx + 44, 562), 7, orient="v", kind="throttle")
    inst(sh, (zx + 60, 575), "FI", "z")
    inst(sh, (zx - 16, 570), "TIC", "z", panel=True)
    sh.line([(zx - 9.2, 570), (zx - 3, 570)], lw=0.3, ls=LS["signal"], c=C["signal"])
    ln(sh, [(zx, 580), (zx, 570)], "water", arrow=False)
    ln(sh, [(zx, 562), (zx, 553), (zx + 11, 553)], "water", "w_02", lab_at=1)
    ln(sh, [(zx + 33, 553), (zx + 44, 553), (zx + 44, 558)], "water", arrow=False)
    ln(sh, [(zx + 44, 566), (zx + 44, 572), (zx + 44, 548), (zx + 44, yr_)], "water", "w_03", ret=True)
    sh.text(zx + 22, 545, "× 6 vùng (B1 áo nước)", ha="center", va="top")
    sh.mentioned.add("barrel_cw_hoses")
    branches = [(380, "w_05", "làm mát dầu", "lube_oil_cooler"), (430, "w_10", "làm mát động cơ", "util_cw_motor_hoses"),
                (480, "w_06", "áo miệng nạp", "util_cw_throat_hoses"), (530, "w_07", "áo side feeder", "util_cw_sidefeed_hoses"),
                (580, "w_08", "ống xoắn bình tách", "util_cw_vac_hoses"), (630, "w_09", "bơm chân không", "vac_pump_unit")]
    for x, cid, t, pid in branches:
        if cid not in CID:
            continue
        ln(sh, [(x, ys_), (x, 585)], "water", cid, lab_at=0)
        box(sh, (x, 578), 40 if len(t) > 14 else 34, 12, t, pid)
        ln(sh, [(x + 6, 572), (x + 6, yr_)], "water", ret=True)
        dft.sym_valve(sh, (x - 8, 595), 6, orient="v", kind="ball")
    # ================================================================ hydraulics and air
    sh.text(660, 625, "5. Thuỷ lực (hydraulic) và khí nén (air)", 11, va="bottom", weight="bold")
    box(sh, (690, 580), 36, 22, "HPU\nbể 250 L, M 7,5 kW", "melt_hpu")
    for i, (yy, cid, t, pid) in enumerate(((600, "h_01", "xi lanh tay quay bộ lọc", "melt_sc_drive"), (565, "h_02", "xi lanh van khởi động", "melt_startup_cyl"))):
        dft.poly(ax, [(740, yy - 5), (764, yy - 5), (764, yy + 5), (740, yy + 5)], fc="white", lw=0.35, z=40)
        sh.line([(748, yy - 5), (748, yy + 5)], lw=0.3)
        sh.line([(756, yy - 5), (756, yy + 5)], lw=0.3)
        sh.text(752, yy + 6, "4/3 S", ha="center", va="bottom")
        ln(sh, [(708, 580 + (8 if i == 0 else -8)), (725, 580 + (8 if i == 0 else -8)), (725, yy), (740, yy)], "hydraulic", cid, lab_at=0)
        box(sh, (820, yy), 50, 10, t, pid)
        ln(sh, [(764, yy), (795, yy)], "hydraulic")
        sh.mentioned.add("melt_hyd_hoses_sc" if i == 0 else "melt_hyd_hoses_suv")
    ya = 515
    sh.text(660, ya + 14, "khí nén 6 bar từ nhà máy", ha="left", va="bottom", color=C["air"])
    box(sh, (700, ya), 22, 10, "FRL 1", "util_frl")
    box(sh, (700, ya - 25), 22, 10, "FRL 2", "util_frl_2")
    ln(sh, [(660, ya + 12), (660, ya), (689, ya)], "air", "a_01", lab_at=1)
    ln(sh, [(660, ya), (660, ya - 25), (689, ya - 25)], "air", arrow=False)
    box(sh, (800, ya), 52, 10, "ống gió bulông nhiệt", "die_bolt_actuator_rail")
    ln(sh, [(711, ya), (774, ya)], "air")
    box(sh, (800, ya - 18), 52, 10, "van bướm chân không", "vac_valve")
    box(sh, (800, ya - 32), 52, 10, "van lật máy hút liệu", "feed_vacuum_loader")
    ln(sh, [(711, ya - 25), (740, ya - 25), (740, ya - 18), (774, ya - 18)], "air", "a_02", lab_at=2)
    ln(sh, [(740, ya - 25), (740, ya - 32), (774, ya - 32)], "air", "a_03", lab_at=1)
    sh.mentioned.update({"util_air_drop", "util_air_drop_2", "util_air_hose_die", "util_air_tube_vac", "util_air_tube_loader"})
    # ================================================================ power one-line + safety chain
    sh.text(40, 440, "6. Cấp điện (power one-line)", 11, va="bottom", weight="bold")
    box(sh, (70, 410), 44, 14, "trạm biến áp 3 kV", "ctrl_infeed_mv", ls="phantom")
    box(sh, (70, 370), 44, 16, "tủ biến tần TT", "ctrl_drive_cabinet")
    box(sh, (70, 330), 44, 14, "động cơ chính", "drive_motor_terminal_box")
    ln(sh, [(70, 403), (70, 378)], "power", "p_12")
    ln(sh, [(70, 362), (70, 337)], "power", "p_01")
    box(sh, (190, 410), 44, 14, "tủ phân phối 400 V", "ctrl_infeed_lv", ls="phantom")
    box(sh, (190, 370), 50, 16, "tủ điều khiển + nhiệt (PLC)", "ctrl_heater_cabinet")
    ln(sh, [(190, 403), (190, 378)], "power", "p_13")
    loads = [("p_02", "nhiệt xi lanh", "barrel_heater_jboxes"), ("p_10", "nhiệt đường chảy", "melt_heater_jbox"), ("p_03", "nhiệt khuôn", "die_junction_box"),
             ("p_04", "M bơm nhựa", "melt_pump_motor"), ("p_05", "cụm chân không", "vac_control_box"), ("p_06", "HPU", "melt_hpu"),
             ("p_07", "M side feeder", "sidefeed_motor"), ("p_08", "tủ cân", "feed_control_cabinet")]
    for i, (cid, t, pid) in enumerate(loads):
        x = 128 + i * 35
        ln(sh, [(190, 362), (190, 350), (x, 350), (x, 330)], "power", cid, lab_at=2)
        box(sh, (x, 322), 33, 14, t, pid)
    box(sh, (420, 370), 44, 14, "tủ bulông nhiệt", "ctrl_die_bolt_cabinet")
    ln(sh, [(420, 363), (420, 337)], "power", "p_11")
    box(sh, (420, 330), 40, 12, "hộp khuôn", "die_junction_box")
    box(sh, (480, 370), 40, 14, "tủ đầu máy", "ctrl_machine_cabinet")
    ln(sh, [(480, 363), (480, 337)], "power", "p_09")
    box(sh, (480, 330), 40, 12, "M bơm dầu", "lube_pump_motor")
    ln(sh, [(215, 370), (398, 370)], "power", arrow=False)
    ln(sh, [(442, 370), (460, 370)], "power", arrow=False)
    sh.text(40, 280, "7. Chuỗi dừng khẩn và liên động (safety chain, interlocks)", 11, va="bottom", weight="bold")
    es = [("ES1–3", "ctrl_estops"), ("ES4", "ctrl_estop_melt"), ("ES5", "ctrl_estop_die"), ("ES6", "ctrl_estop_platform"),
          ("ES7", "ctrl_hmi"), ("ES8", "ctrl_machine_cabinet"), ("ES9", "die_junction_box")]
    xe = 50
    for i, (t, pid) in enumerate(es):
        x = xe + i * 30
        dft.circ(ax, (x, 255), 5.2, fc="#c8102e", lw=0.3, z=40)
        sh.text(x, 255, "E", ha="center", va="center", color="white", weight="bold", zorder=41)
        sh.text(x, 247, t, ha="center", va="top")
        sh.mentioned.add(pid)
        if i:
            sh.line([(x - 24.8, 255), (x - 5.2, 255)], lw=0.4, ls=LS["signal"], c=C["signal"])
    sh.text(xe + 90, 262, "mắc nối tiếp, 2 kênh (s_06, s_09, s_18, s_19)", ha="center", va="bottom")
    box(sh, (290, 255), 48, 14, f"rơ-le an toàn ({NUM['ctrl_heater_cabinet']})", "ctrl_heater_cabinet")
    sh.line([(xe + 6 * 30 + 5.2, 255), (266, 255)], lw=0.4, ls=LS["signal"], c=C["signal"])
    box(sh, (400, 255), 46, 14, f"STO biến tần ({NUM['ctrl_drive_cabinet']})", "ctrl_drive_cabinet")
    ln(sh, [(314, 255), (377, 255)], "signal", "s_10")
    trips = [("PAHH P1 350 bar", "s_11"), ("đứt đĩa nổ 1", "s_12"), ("đứt đĩa nổ 2", "s_13")]
    for i, (t, cid) in enumerate(trips):
        y = 230 - i * 13
        box(sh, (300, y), 48, 10, t)
        ln(sh, [(324, y), (390 + i * 6, y), (390 + i * 6, 248)], "signal", cid, lab_at=0)
    locks = [("PSL / TT dầu hộp số", "s_14"), ("liên động vỏ che", "s_15"), ("công tắc nhả khớp an toàn", "s_16")]
    for i, (t, cid) in enumerate(locks):
        y = 230 - i * 13
        box(sh, (120, y), 58, 10, t)
        ln(sh, [(149, y), (190, y)], "signal", cid, lab_at=0)
    box(sh, (205, 217), 30, 34, f"tủ đầu\nmáy\n({NUM['ctrl_machine_cabinet']})", "ctrl_machine_cabinet")
    ln(sh, [(220, 217), (240, 217), (240, 248), (266, 252)], "signal", "s_17", lab_at=0)
    box(sh, (480, 230), 54, 10, "P3 → PIC → biến tần bơm", None)
    ln(sh, [(453, 230), (440, 230)], "signal", "s_20", lab_at=0)
    box(sh, (480, 215), 54, 10, "encoder → biến tần", "drive_encoder")
    ln(sh, [(453, 215), (428, 215), (428, 248)], "signal", "s_02", lab_at=0)
    box(sh, (480, 200), 54, 10, "HMI ↔ PLC (Profinet)", "ctrl_hmi")
    ln(sh, [(453, 200), (300, 200), (300, 248)], "signal", "s_01", lab_at=0)
    # ================================================================ legend, cause & effect, instrument list
    lx, ly = 925, 812
    sh.text(lx, ly, "Chú giải (legend)", 11, va="top", weight="bold")
    items = [("melt", "nhựa nóng chảy"), ("material", "vật liệu rắn"), ("water", "nước cấp; nét đứt = nước hồi"), ("vacuum", "chân không"),
             ("oil", "dầu bôi trơn"), ("hydraulic", "thuỷ lực"), ("air", "khí nén"), ("power", "động lực"), ("signal", "tín hiệu / liên động"),
             ("mechanical", "trục cơ khí")]
    for i, (m, t) in enumerate(items):
        y = ly - 9 - i * 6
        sh.line([(lx, y), (lx + 24, y)], lw=LW[m], ls=LS.get(m, "solid"), c=C[m])
        sh.text(lx + 27, y, f"{m} – {t}", va="center")
    sy = ly - 76
    dft.sym_valve(sh, (lx + 5, sy), 7, kind="ball")
    sh.text(lx + 12, sy, "van bi", va="center")
    dft.sym_valve(sh, (lx + 58, sy), 7, kind="solenoid")
    sh.text(lx + 65, sy, "van điện từ", va="center")
    dft.sym_valve(sh, (lx + 128, sy), 7, kind="throttle")
    sh.text(lx + 135, sy, "van tiết lưu", va="center")
    dft.sym_valve(sh, (lx + 196, sy), 7, kind="relief")
    sh.text(lx + 203, sy, "van an toàn", va="center")
    sy -= 16
    dft.sym_instrument(sh, (lx + 6, sy), "PT", "P1")
    sh.text(lx + 15, sy, "thiết bị tại chỗ", va="center")
    dft.sym_instrument(sh, (lx + 76, sy), "PIC", "P3", panel=True)
    sh.text(lx + 85, sy, "trên tủ (vạch ngang)", va="center")
    dft.sym_pump(sh, (lx + 175, sy), 5.5, kind="gear")
    sh.text(lx + 183, sy, "bơm", va="center")
    ce = cause_effect()
    yy = sh.table(lx, sy - 14, [("Nguyên nhân (cause)", 92, "l"), ("Tác động (effect)", 156, "l")],
                  [[a, b] for a, b in ce], title="Bảng nguyên nhân → tác động (design.md §7)", rowh=5.4)
    rows = [["PT/TT P1, T1", "đầu xi lanh", "PAHH 350 bar → ngắt cứng"], ["PT P2 / PDI", "trước lọc", "chênh áp lưới → báo đổi lưới"],
            ["PT P3 / PIC", "hút bơm", "≈ 50 bar → tốc độ bơm"], ["PT P4", "ra bơm", "HH 330 bar → dừng bơm + vít"],
            ["PT/TT P5, T5", "vào khuôn", "theo dõi"], ["RD1 / RD2", "đầu XL / sau bơm", "400 / 350 bar, đứt → ngắt"],
            ["PSL, TT dầu", "cụm dầu", "cấm khởi động"], ["WIC 01–03", "cân", "lưu lượng 3 500 kg/h"], ["PI/PIT V1–V2", "vòm chân không", "50 / 5–20 mbar"],
            ["TIC z", "mỗi vùng nhiệt", "nhiệt + van điện từ nước"]]
    sh.table(lx, yy - 10, [("Thiết bị (tag)", 54, "l"), ("Vị trí", 64, "l"), ("Chức năng / ngưỡng", 130, "l")], rows,
             title="Danh mục thiết bị đo (instrument list)")
    sh.text(40, 140, "Số đường = id mối nối trong parts.json (connections). Bảng mối nối đủ và tuyến đi thật theo path_mm: tờ 08.",
            ha="left", va="bottom")
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
