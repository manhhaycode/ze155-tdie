#!/usr/bin/env python3
"""Sheet 08 – utility routing (A0): cable trenches and trays, MV/LV infeeds, cable drops, compressed air, cooling water,
signal routes, drawn from parts.json `connections[].path_mm` on a scaled plan (1:25) plus transverse sections where the
routes rise to the machine; full connection schedule."""
import math

from matplotlib.patches import Circle, Rectangle

import drafting as dft
from geom import ORDER, P, NUM, CONN, VIEWS
from sheet import Sheet, VP, fmt, PT, MIN_FS, BOM_COLS, bom_rows
from sheet07_pid import C, LW, LS

UTIL_MEDIA = ("power", "signal", "air", "water", "hydraulic", "oil")
MED_VI = {"melt": "nhựa", "material": "vật liệu", "water": "nước", "vacuum": "chân không", "oil": "dầu", "hydraulic": "thuỷ lực",
          "air": "khí nén", "power": "động lực", "signal": "tín hiệu", "mechanical": "cơ khí"}
TRENCH = ["ctrl_floor_trench", "ctrl_floor_duct", "ctrl_trench_mv", "ctrl_trench_die_branch", "ctrl_infeed_mv", "ctrl_infeed_lv"]
UTIL_PARTS = [q for q in ORDER if q.startswith(("ctrl_", "util_")) and q not in TRENCH] + [
    "barrel_cw_supply", "barrel_cw_return", "barrel_cw_valves", "barrel_cw_hoses", "barrel_heater_jboxes", "barrel_cable_tray",
    "melt_heater_jbox", "die_junction_box", "die_heater_conduit", "vac_control_box", "drive_motor_terminal_box", "feed_control_cabinet",
    "melt_hpu", "melt_hyd_hoses_sc", "melt_hyd_hoses_suv", "die_bolt_actuator_rail"]
UTIL_PARTS = [q for q in UTIL_PARTS if q in P]
ROUTES = [c for c in CONN if c["medium"] in UTIL_MEDIA and c.get("path_mm")]
LANE_MM = 7.0  # lateral spacing of runs sharing a trench (world mm)


def in_trench(p):
    x, y, z = p
    if z > 60:
        return False
    return (-1250 <= y <= -1050 and x >= -1000) or (-1200 <= x <= -800 and y <= -1000) or (-4200 <= x <= -3800 and y <= -1000)


def lanes():
    """Runs that share the floor trenches get a lateral offset so each one can be followed."""
    tr = [c for c in ROUTES if sum(in_trench(p) for p in c["path_mm"]) >= 2]
    tr.sort(key=lambda c: (c["medium"] != "power", c["id"]))
    n = len(tr)
    return {c["id"]: (i - (n - 1) / 2) * LANE_MM for i, c in enumerate(tr)}


def route_pts(c, off):
    o = off.get(c["id"], 0.0)
    out = []
    for p in c["path_mm"]:
        q = list(p)
        if in_trench(p) or (q[2] <= 120 and o):
            q[0] += o
            q[1] += o
        out.append(tuple(q))
    return out


def machine_end(c, pts):
    """The end of the run that lands on the machine (the other end is usually a cabinet)."""
    a, b = pts[0], pts[-1]
    cab = ("ctrl_drive_cabinet", "ctrl_heater_cabinet", "ctrl_die_bolt_cabinet", "ctrl_infeed_mv", "ctrl_infeed_lv",
           "util_cw_supply_riser", "util_cw_return_riser", "util_air_drop", "util_air_drop_2", "ctx_floor")
    if c["from"] in cab and c["to"] not in cab:
        return b
    if c["to"] in cab and c["from"] not in cab:
        return a
    return b


class Tags:
    """Greedy placement of route-id tags next to their end points, avoiding earlier tags."""

    def __init__(self, sh, keepout=()):
        self.sh, self.boxes = sh, list(keepout)

    @staticmethod
    def size(t):
        lines = t.split("\n")
        return max(len(s) for s in lines) * 0.56 * MIN_FS / PT + 1.2, len(lines) * MIN_FS / PT * 1.2 + 0.6

    def free(self, b, lim):
        if b[0] < lim[0] or b[1] > lim[1] or b[2] < lim[2] or b[3] > lim[3]:
            return False
        return all(b[1] < q[0] or b[0] > q[1] or b[3] < q[2] or b[2] > q[3] for q in self.boxes)

    def place(self, at, text, color, lim, prefer=(1, 1)):
        w, h = self.size(text)
        dirs = [prefer, (prefer[0], -prefer[1]), (-prefer[0], prefer[1]), (-prefer[0], -prefer[1]), (0, 1), (0, -1), (1, 0), (-1, 0)]
        for r in (2.5, 6, 10, 14, 19, 25):
            for dx, dy in dirs:
                cx, cy = at[0] + dx * r, at[1] + dy * r
                x0 = cx if dx > 0 else (cx - w if dx < 0 else cx - w / 2)
                y0 = cy if dy > 0 else (cy - h if dy < 0 else cy - h / 2)
                b = (x0, x0 + w, y0, y0 + h)
                if self.free(b, lim):
                    self.boxes.append((b[0] - 0.6, b[1] + 0.6, b[2] - 0.6, b[3] + 0.6))
                    if r > 3:
                        ex = min(max(at[0], b[0]), b[1])
                        ey = min(max(at[1], b[2]), b[3])
                        self.sh.line([at, (ex, ey)], lw=0.15, c=color, z=44)
                    self.sh.text((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, text, ha="center", va="center", color=color, zorder=46,
                                 linespacing=1.0, bbox=dict(fc="white", ec=color, lw=0.25 * PT, pad=0.25))
                    return b
        print("   tag not placed:", text)
        return None


def draw_routes(sh, vp, off, slab=None, z=12.0):
    """Polylines per connection, coloured by medium. slab=(x0, x1): transverse section, keep only the part inside the slab
    and show runs crossing the cut as dots."""
    ends = []
    for c in ROUTES:
        pts = route_pts(c, off)
        med = c["medium"]
        segs = []
        for a, b in zip(pts, pts[1:]):
            if slab:
                x0, x1 = slab
                t0, t1 = 0.0, 1.0
                dx = b[0] - a[0]
                if abs(dx) < 1e-9:
                    if not (x0 <= a[0] <= x1):
                        continue
                else:
                    ta, tb = (x0 - a[0]) / dx, (x1 - a[0]) / dx
                    t0, t1 = max(0.0, min(ta, tb)), min(1.0, max(ta, tb))
                    if t0 > t1:
                        continue
                a2 = tuple(a[i] + (b[i] - a[i]) * t0 for i in range(3))
                b2 = tuple(a[i] + (b[i] - a[i]) * t1 for i in range(3))
                segs.append((a2, b2))
            else:
                segs.append((a, b))
        if not segs:
            continue
        for a, b in segs:
            pa, pb = vp.P(a), vp.P(b)
            if math.dist(pa, pb) < 0.35:
                sh.ax.add_patch(Circle(pa, 0.75, fc=C[med], ec="k", lw=0.1 * PT, zorder=z + 1))
            else:
                ls = LS.get(med, "solid")
                if c["id"] in ("w_03", "w_04"):
                    ls = (0, (6, 2.5))
                art, = sh.ax.plot([pa[0], pb[0]], [pa[1], pb[1]], c=C[med], lw=max(LW[med] * 0.7, 0.25) * PT, ls=ls, zorder=z,
                                  solid_capstyle="round")
                if vp.clip:
                    x0, x1, y0, y1 = vp.box()
                    art.set_clip_path(Rectangle((x0, y0), x1 - x0, y1 - y0, transform=sh.ax.transData))
        me = machine_end(c, pts)
        inside = (not slab) or (slab[0] <= me[0] <= slab[1])
        if inside:
            ends.append((c, vp.P(me)))
    return ends


def tag_ends(sh, vp, ends, tags, prefer=(1, 1), only=None):
    """Group end points that fall together and tag them once."""
    lim = vp.box()
    lim = (lim[0] + 1, lim[1] - 1, lim[2] + 1, lim[3] - 1)
    groups = []
    for c, p in ends:
        if only and c["id"] not in only:
            continue
        if not (lim[0] <= p[0] <= lim[1] and lim[2] <= p[1] <= lim[3]):
            continue  # end point outside the view window (clipped run)
        for g in groups:
            if math.dist(g[0], p) < 2.5:
                g[1].append(c)
                break
        else:
            groups.append([p, [c]])
    groups.sort(key=lambda g: (g[0][1], g[0][0]))
    for p, cs in groups:
        sh.ax.add_patch(Circle(p, 0.9, fc="white", ec=C[cs[0]["medium"]], lw=0.35 * PT, zorder=45))
        ids = [c["id"] for c in cs]
        text = "\n".join(", ".join(ids[i:i + 3]) for i in range(0, len(ids), 3))
        col = C[cs[0]["medium"]] if len({c["medium"] for c in cs}) == 1 else "#222222"
        tags.place(p, text, col, lim, prefer)


def section(sh, name, slab, k, x_left, y_top, win, off, tags, title, extra_ids=(), brk=None, labels=()):
    """Transverse projection of the slab X in [x0, x1], looking toward -X (+Y to the right). win = (y0, y1, z0, z1) world;
    the view is placed with its top-left corner at (x_left, y_top) on the sheet."""
    v = VIEWS["die_end"]
    x0, x1 = slab
    ids = [q for q in ORDER if q != "ctx_floor" and P[q]["bbox_mm"][1] >= x0 and P[q]["bbox_mm"][0] <= x1 and P[q]["group"] != "context"]
    W, H = (win[1] - win[0]) / k, (win[3] - win[2]) / k
    vp = VP(sh, v, k, x_left + W / 2, y_top - H / 2, (win[0] + win[1]) / 2, (win[2] + win[3]) / 2, clip=win)
    vp.draw(ids, ghost="#a6a6a6", z0=3.0, floor=True)
    hi = [q for q in ids if q in UTIL_PARTS or q in TRENCH or q in extra_ids]
    vp.draw(hi, z0=8.0, hidden_show=False, floor=False, thick=0.3, thin=0.18)
    ends = draw_routes(sh, vp, off, slab=slab, z=31.0)
    b = vp.box()
    sh.heading((b[0] + b[1]) / 2, b[3] + 9, title, f"1:{k}", fs=12, sub=f"lát cắt X {fmt(x0)} … {fmt(x1)}, nhìn về −X (+Y bên phải)")
    for i, (p3, t, pid, side) in enumerate(labels):
        a = vp.P(p3)
        pos = (b[0] + 3, b[3] - 5 - i * 6.5) if side == "l" else (b[1] - 3, b[3] - 5 - i * 6.5)
        sh.label(a, pos, t, ha="left" if side == "l" else "right", pid=pid)
        w = len(t) * 0.56 * MIN_FS / PT + 5
        tags.boxes.append((pos[0], pos[0] + w, pos[1] - 2.5, pos[1] + 2.5) if side == "l" else (pos[0] - w, pos[0], pos[1] - 2.5, pos[1] + 2.5))
    tag_ends(sh, vp, ends, tags)
    for edge in brk or ():
        # break line along a clipped edge of the view window: 'top', 'left', 'right'
        if edge == "top":
            dft.break_line(sh, (b[0] + 2, b[3]), (b[1] - 2, b[3]))
        elif edge == "left":
            dft.break_line(sh, (b[0], b[2] + 4), (b[0], b[3] - 2))
        elif edge == "right":
            dft.break_line(sh, (b[1], b[2] + 4), (b[1], b[3] - 2))
    return vp


def N(pid):
    """Balloon number as text (numbers follow parts.json order, so never hard-code them)."""
    return str(NUM[pid]) if pid in NUM else "?"


def parts_list_cols(sh, x, ytop, ncol, gap=8):
    ids = sorted(set(sh.ballooned) | set(sh.mentioned), key=lambda q: NUM[q])
    n = math.ceil(len(ids) / ncol)
    w = sum(c[1] for c in BOM_COLS)
    for j in range(ncol):
        chunk = ids[j * n:(j + 1) * n]
        if chunk:
            sh.table(x + j * (w + gap), ytop, BOM_COLS, bom_rows(chunk), rowh=5.0,
                     title="Chi tiết có số bóng trên tờ này (parts list)" if j == 0 else None)


def main():
    sh = Sheet(8, "utility-routing", "Tuyến tiện ích (utility routing)", size="A0", scale="1:25 / 1:20 / 1:50",
               subtitle="Hào và máng cáp, cấp điện trung/hạ thế, cáp đứng, khí nén, nước làm mát, tín hiệu; vẽ từ connections.path_mm")
    off = lanes()
    tags = Tags(sh)
    # ------------------------------------------------------------------ plan 1:25
    k = 25
    clip = (-9900, 5800, -1800, 5300)  # u = -X, w = -Y
    plan = VP(sh, "top", k, 36 + (5800 + 9900) / k / 2, 800 - (5300 + 1800) / k / 2, (clip[0] + clip[1]) / 2, (clip[2] + clip[3]) / 2,
              clip=clip)
    plan.draw([q for q in ORDER if q != "ctx_floor"], ghost="#a6a6a6", z0=3.0)
    pb = plan.box()
    for pid in TRENCH:
        b = P[pid]["bbox_mm"]
        (xa, ya), (xb, yb) = plan.P((b[0], b[2], 0)), plan.P((b[1], b[3], 0))
        dft.poly(sh.ax, [(xa, ya), (xb, ya), (xb, yb), (xa, yb)], fc="#f3efe6", ec="k", lw=0.3, z=7.0, hatch="////")
    plan.draw([q for q in UTIL_PARTS], z0=8.0, hidden_show=False, thick=0.3, thin=0.18)
    plan.items = plan.items  # id-buffer built from the utility parts only
    ends = draw_routes(sh, plan, off)
    # break line where the calender (context) is cut by the view window
    dft.break_line(sh, (pb[0], plan.P((0, 1500, 0))[1]), (pb[0], plan.P((0, -1500, 0))[1]))
    # headings and in-view notes in the empty floor area (-Y, downstream)
    hx, hy = plan.P((2800, -4800, 0))  # free floor between the leaders of the -Y balloons
    sh.heading(hx, hy, "Mặt bằng tuyến tiện ích", "1:25", sub="(utility routing plan) nhìn từ +Z")
    nb = [
        "Máy: nét mảnh xám; tiện ích: nét đậm.",
        "Hào cáp có nắp (gạch chéo): tuyến ở Z ≈ 5",
        "(mặt nắp); chiều sâu hào không có trong",
        f"dữ liệu. Tuyến chung hào vẽ lệch {LANE_MM:.0f} mm",
        "để lần theo được (mặt cắt: chấm màu).",
        "Nhãn = id mối nối ở đầu tuyến phía máy;",
        "chấm rỗng = điểm cuối.",
    ]
    for i, t in enumerate(nb):
        sh.text(hx - 58, hy - 12 - i * 5.0, t, ha="left", va="center")
    # balloons: utility parts
    up = [q for q in UTIL_PARTS + TRENCH if q not in ("ctrl_signal_tower",)]
    top_ids = [q for q in up if P[q]["center_mm"][1] < -1500]
    bot_ids = [q for q in up if P[q]["center_mm"][1] >= -1500]
    plan.balloons(top_ids, sides=("top",), offset=6, rows=2, r=4.8)
    plan.balloons(bot_ids, sides=("bottom",), offset=6, rows=2, r=4.8)
    tags.boxes.append((hx - 60, hx + 60, hy - 50, hy + 8))
    tag_ends(sh, plan, ends, tags)
    # section markers on the plan
    secs = [("A", (-4300, -3700)), ("B", (-1250, -150)), ("C", (5800, 8150)), ("D", (8450, 9450))]
    for letter, (xa, xb) in secs:
        xm = (xa + xb) / 2
        p1, p2 = plan.P((xm, -5150, 0)), plan.P((xm, 1700, 0))
        dft.section_marker(sh, p1, p2, letter, (1, 0))
    # ------------------------------------------------------------------ sections
    yt = 462
    section(sh, "A", (-4300, -3700), 25, 38, yt, (-5300, 0, -100, 2700), off, tags, "Mặt cắt A–A: cáp trung thế lên động cơ",
            brk=("right",),
            labels=[((-4000, -4300, 2400), "tủ biến tần trung thế", "ctrl_drive_cabinet", "l"),
                    ((-4000, -1030, 1190), "hộp đấu dây động cơ", "drive_motor_terminal_box", "r")])
    section(sh, "B", (-1250, -150), 25, 266, yt, (-4700, 1900, -100, 3600), off, tags, "Mặt cắt B–B: cáp đứng, nước, khí",
            extra_ids=("feed_platform_columns_rear",), brk=("top",),
            labels=[((-300, -2600, 3500), "ống khí xuống cột sàn (từ Z 4 500)", "util_air_drop_2", "l"),
                    ((-1000, -4000, 2200), "tủ điều khiển + nhiệt", "ctrl_heater_cabinet", "l"),
                    ((-1000, -1050, 750), "máng cáp đứng", "ctrl_cable_drop", "r"),
                    ((-400, 1060, 600), "ống nước cấp / hồi từ nhà máy", "util_cw_supply_riser", "r")])
    section(sh, "C", (5800, 8150), 20, 546, yt, (-2400, 900, -100, 1900), off, tags, "Mặt cắt C–C: đường chảy",
            labels=[((6100, -2100, 1400), "hộp điều khiển chân không", "vac_control_box", "l")])
    section(sh, "D", (8450, 9450), 20, 727, yt, (-2000, 1600, -100, 2000), off, tags, "Mặt cắt D–D: khuôn", brk=("top",),
            labels=[((9360, -1705, 1900), "ống khí xuống khuôn (từ Z 4 500)", "util_air_drop", "l"),
                    ((8800, -1750, 900), "hộp đấu dây khuôn", "die_junction_box", "l")])
    # ------------------------------------------------------------------ connection schedule (right column)
    def length(c):
        pts = c.get("path_mm") or []
        return sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) / 1000
    rows = [[c["id"], c["from"], c["to"], MED_VI[c["medium"]], f"{length(c):.1f}".replace(".", ","), c.get("type", "")] for c in CONN]
    yy = sh.table(925, 815, [("Id", 17, "c"), ("Từ (from)", 62, "l"), ("Tới (to)", 62, "l"), ("Môi chất", 24, "l"), ("L, m", 13, "c"),
                             ("Kiểu nối / cỡ", 72, "l")], rows, rowh=5.0, zebra=True,
                  title=f"Bảng mối nối (connection schedule) – {len(CONN)} mối nối, L = dài tuyến theo path_mm")
    # legend
    lx, ly = 925, yy - 8
    sh.text(lx, ly, "Chú giải (legend)", 11, va="top", weight="bold")
    legend = [("power", "động lực (p_*), cả trung thế 3 kV"), ("signal", "tín hiệu, an toàn (s_*)"), ("air", "khí nén 6 bar (a_*)"),
              ("water", "nước cấp (w_*); nét đứt dài = nước hồi"), ("hydraulic", "thuỷ lực (h_*)"), ("oil", "dầu bôi trơn (o_*)")]
    for i, (m, t) in enumerate(legend):
        y = ly - 9 - i * 6
        sh.line([(lx, y), (lx + 22, y)], lw=max(LW[m] * 0.7, 0.25), ls=LS.get(m, "solid"), c=C[m])
        sh.text(lx + 25, y, t, va="center")
    y = ly - 9 - len(legend) * 6
    dft.poly(sh.ax, [(lx, y - 2), (lx + 22, y - 2), (lx + 22, y + 2), (lx, y + 2)], fc="#f3efe6", ec="k", lw=0.3, z=30, hatch="////")
    sh.text(lx + 25, y, "hào cáp có nắp (cable trench)", va="center")
    y -= 7
    sh.ax.add_patch(Circle((lx + 11, y), 0.75, fc=C["power"], ec="k", lw=0.1 * PT, zorder=31))
    sh.text(lx + 25, y, "tuyến cắt ngang mặt cắt (chấm)", va="center")
    y -= 7
    sh.line([(lx, y), (lx + 22, y)], lw=0.15, c="#a6a6a6")
    sh.text(lx + 25, y, "máy (nét mảnh xám, không tô)", va="center")
    sh.notes(lx, y - 7, "Ghi chú (notes)", [
        "1. Toạ độ và tuyến lấy nguyên từ design/parts.json (connections[].path_mm); bản vẽ không thêm tuyến.",
        f"2. Điểm cấp vào: trung thế 3 kV (p_12) qua hào {N('ctrl_infeed_mv')} vào tủ biến tần {N('ctrl_drive_cabinet')}; hạ thế 400 V (p_13)"
        f" qua hào {N('ctrl_infeed_lv')} vào tủ {N('ctrl_heater_cabinet')}. Toạ độ: bảng mối nối và mặt bằng.",
        f"3. Khí nén 6 bar: ống xuống {N('util_air_drop_2')} tại cột sàn và {N('util_air_drop')} tại khuôn, mỗi nhánh có bộ FRL"
        f" ({N('util_frl_2')}, {N('util_frl')}).",
        f"4. Nước làm mát: ống đứng cấp {N('util_cw_supply_riser')} / hồi {N('util_cw_return_riser')} phía +Y; ống góp"
        f" {N('barrel_cw_supply')} / {N('barrel_cw_return')} dọc khung đế.",
        "5. Sơ đồ nguyên lý và liên động: tờ 07. Danh mục đủ: tờ 09.",
    ], width=245)
    parts_list_cols(sh, 36, 290, 3)
    name, dpi = sh.save()
    print(name, round(dpi))


if __name__ == "__main__":
    main()
