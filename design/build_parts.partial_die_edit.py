#!/usr/bin/env python3
"""Single source of truth for the ZE 155 A UT 34D + T-die line.

Writes design/parts.json and fills the part list / connection list sections of
design/design.md (between the BEGIN/END markers). Run:

    uv run -q python design/build_parts.py

Units mm. X along the screws, +X = flow, X = 0 at the drive-side face of barrel B1.
Y = 0 midway between the screws, +Y = operator side. Z up, Z = 0 floor.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- constants
AXZ = 1200.0          # screw axis height (c006)
D = 169.0             # screw diameter ZE 155 A (c001)
A_CD = 142.0          # centre distance (specs §1, derived)
L34 = 34 * D          # 5746
BAR = [(0, 676), (676, 1690), (1690, 2704), (2704, 3718), (3718, 4732), (4732, 5746)]
JOINTS = [676, 1690, 2704, 3718, 4732]
R_BODY, R_FL, R_HEAT = 260.0, 320.0, 290.0
R_NECK, L_NECK = 250.0, 40.0   # relief neck behind each flange for socket access to the joint nuts
R_JOINT = 300.0                 # envelope of the stud + nut ring (nuts r 262-298)
PCD, N_BOLT, L_BOLT = 560.0, 20, 164.0   # flange joint studs M24 + 12-point nuts
FT = 650.0            # base frame top
FY = 1000.0           # base frame half width
LIP_X = 9576.0        # die lip
DIE_XB = 9060.0       # die back face (DECISIONS 20: body deepened from 9126)
ROLL_X = 9776.0       # roll centres (air gap 200)
ROLL_R = 400.0

COL = {
    "frame": "#DCDDDE", "cover": "#C4C9CE", "steel": "#8C9298", "polished": "#D5D9DD",
    "chrome": "#E3E6E9", "blue_drive": "#2C5FAE", "motor": "#2B528C", "km_blue": "#008DC3",
    "yellow": "#F2C200", "orange": "#EE7A12", "black": "#1F1F1F", "galv": "#A9AFB4",
    "cabinet": "#D8DAD6", "red": "#C8102E", "glass": "#9CCFE0", "stainless": "#B8BEC4",
    "cast": "#7E848A", "dark_steel": "#5F656B", "grating": "#9EA3A6", "floor": "#B9B7B0",
    "rubber": "#2A2A2A", "white": "#EDEEEE", "hose": "#9A9FA4",
}

GROUPS = {
    "base": "Khung đế và giá đỡ (base and supports)",
    "drive": "Truyền động (drive)",
    "feed": "Cấp liệu (feeding)",
    "barrel": "Đoạn gia công (processing section)",
    "vacuum": "Hệ chân không (vacuum system)",
    "melt": "Đường chảy nhựa (melt line)",
    "die": "Khuôn chữ T (T-die)",
    "control": "Điều khiển và điện (control and electrical)",
    "util": "Tiện ích (utilities)",
    "context": "Bối cảnh (context, collection ze155_context)",
}


def r1(v):
    return round(float(v), 1)


def bb(x0, x1, y0, y1, z0, z1):
    return [r1(x0), r1(x1), r1(y0), r1(y1), r1(z0), r1(z1)]


def cylx(x0, x1, r, yc=0.0, zc=AXZ):
    return bb(x0, x1, yc - r, yc + r, zc - r, zc + r)


def cyly(y0, y1, r, xc, zc):
    return bb(xc - r, xc + r, y0, y1, zc - r, zc + r)


def cylz(z0, z1, r, xc, yc):
    return bb(xc - r, xc + r, yc - r, yc + r, z0, z1)


def pipe_bb(path, r):
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for a, b in zip(path, path[1:]):
        d = [b[i] - a[i] for i in range(3)]
        L = math.sqrt(sum(x * x for x in d))
        u = [x / L for x in d]
        for i in range(3):
            e = r * math.sqrt(max(0.0, 1 - u[i] ** 2))
            lo[i] = min(lo[i], a[i] - e, b[i] - e)
            hi[i] = max(hi[i], a[i] + e, b[i] + e)
    return bb(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])


def pipes_bb(paths, r):
    bs = [pipe_bb(pa, r) for pa in paths]
    return bb(min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs),
              max(b[3] for b in bs), min(b[4] for b in bs), max(b[5] for b in bs))


def lp(path):
    return [[r1(v) for v in q] for q in path]


def arc(R, a0, a1, n, cy=0.0, cz=AXZ):
    pts = []
    for k in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * k / n)
        pts.append([r1(cy + R * math.cos(t)), r1(cz + R * math.sin(t))])
    return pts


def c_ring_outline(R, r, gap):
    a0, a1 = -90 + gap, 270 - gap
    return arc(R, a0, a1, 24) + arc(r, a1, a0, 24)


PARTS = []


def add(pid, group, vi, en, fn, shape, bbox, mat, conn, src, details=None, col=None, **kw):
    p = {"id": pid, "group": group, "name_vi": vi, "name_en": en, "function": fn,
         "shape": shape, "bbox_mm": bbox}
    if "center_mm" not in kw:
        kw["center_mm"] = [r1((bbox[0] + bbox[1]) / 2), r1((bbox[2] + bbox[3]) / 2),
                           r1((bbox[4] + bbox[5]) / 2)]
    p.update(kw)
    p["material"] = mat
    p["colour_hex"] = col or COL[mat]
    p["details"] = details or []
    p["connects_to"] = [{"part": t, "interface": i, "at_mm": [r1(v) for v in a]} for t, i, a in conn]
    p["source"] = src
    PARTS.append(p)


def prof_flanged(L, R, r, t):
    return [[0, 0], [R, 0], [R, t], [r, t], [r, L - t], [R, L - t], [R, L], [0, L]]


# =========================================================== BASE AND SUPPORTS
frame_yz = [[-1000, 650], [1000, 650], [1000, 450], [950, 450], [950, 60], [-950, 60],
            [-950, 450], [-1000, 450]]
FEET_X = [-5050, -3900, -2700, -1500, -300, 600, 1700, 2800, 3900, 5000, 5850]

add("base_frame_drive", "base", "Khung đế đoạn truyền động", "Base frame, drive segment",
    "Đỡ hộp số, động cơ, lantern, vỏ khớp nối và cụm dầu; truyền tải trọng xuống chân đế.",
    "frame", bb(-5150, 330, -1000, 1000, 60, 650), "frame",
    [("base_feet", "bulông chân chỉnh cao M30", (-5050, 900, 60)),
     ("base_frame_process", "mặt bích nối khung 12 bulông M24 tại X = 330", (330, 0, 400)),
     ("gearbox", "chân hộp số bắt 8 bulông M42 lên tấm gia công", (-1500, 0, 650)),
     ("drive_motor_base", "đế động cơ bắt bulông, chêm căn chỉnh", (-4000, 0, 650)),
     ("lantern", "chân lantern bắt bulông", (-375, 0, 650)),
     ("drive_coupling_guard", "thanh góc chân vỏ che bắt vít", (-2640, 0, 650)),
     ("lube_unit_frame", "khay dầu bắt vít lên mặt khung", (-3000, 800, 650)),
     ("ctrl_machine_cabinet", "tủ áp sát đầu khung, bắt 4 vít", (-5150, 0, 400))],
    "pdf_measures §2.2/§4 (khung 2 đoạn, dầm trên 210 / hộp dưới 390 mm, mối chia X ≈ +330); chiều rộng 2 000 giả định theo specs §1 (ZE 110 × 1,42)",
    ["Dầm trên (top beam) hộp hàn Z 450–650, mặt trên gia công phẳng có các tấm đệm cho hộp số, đế động cơ, lantern.",
     "Hộp tủ dưới (cabinet box) Z 60–450 lùi vào 50 mm mỗi bên, cửa bản lề rộng 520 mm bước ≈ 860 mm, tay nắm lõm, hai bên ±Y.",
     "Lỗ tròn vận chuyển Ø140 có nút nhựa vàng tại X = −541 và −3 858, cả hai mặt bên (theo trang 9).",
     "Mối hàn dọc trên dầm trên bước ≈ 1 050 mm (theo trang 9).",
     "Bên trong hộp tủ: kênh cáp ngang nối phía +Y với phía −Y (cho cáp HMI, side feeder, nút dừng khẩn)."],
    outline_mm={"plane": "YZ", "pts": frame_yz, "d0": -5150, "d1": 330})

add("base_frame_process", "base", "Khung đế đoạn gia công", "Base frame, processing segment",
    "Đỡ các gối xi lanh, vỏ che, ống góp nước, máng cáp và hộp đấu dây suốt 34D.",
    "frame", bb(330, 5950, -1000, 1000, 60, 650), "frame",
    [("base_feet", "bulông chân chỉnh cao M30", (5850, 900, 60)),
     ("base_frame_drive", "mặt bích nối khung tại X = 330", (330, 0, 400)),
     ("base_drip_tray", "khay đặt trên mặt khung, hàn kín mép", (3000, 0, 650)),
     ("barrel_support_1", "gối bắt 4 bulông M30 + chốt định vị", (1183, 0, 650)),
     ("barrel_support_2", "gối bắt 4 bulông M30", (3211, 0, 650)),
     ("barrel_support_3", "gối bắt 4 bulông M30", (5239, 0, 650)),
     ("barrel_cover_c1", "chân vỏ che bắt vít vào mép khung", (5400, 0, 650))],
    "pdf_measures §2.2/§4; chiều dài theo khoảng X đầu ra +5 922 của hình bóng quy đổi về 34D = 5 746 (DECISIONS 9)",
    ["Cùng tiết diện với đoạn truyền động: dầm trên Z 450–650, hộp tủ Z 60–450 có cửa và lỗ tròn Ø140 tại X = 1 185 và 5 170.",
     "Trong hộp tủ chứa bộ điều nhiệt / phân phối nước (temperature control unit) như catalogue c034; cửa có lưới thông gió.",
     "Đầu khung phía khuôn (X = 5 950) có tấm bịt và 2 tai cẩu."],
    outline_mm={"plane": "YZ", "pts": frame_yz, "d0": 330, "d1": 5950})

add("base_feet", "base", "Chân chỉnh cao / bulông neo", "Levelling feet and anchors",
    "Chỉnh cao và neo khung đế xuống nền, hấp thụ rung.", "cyl",
    bb(-5150, 5950, -1000, 1000, 0, 60), "dark_steel",
    [("base_frame_drive", "bulông chỉnh cao M30 xuyên dầm", (-5050, 900, 60)),
     ("base_frame_process", "bulông chỉnh cao M30", (5850, 900, 60)),
     ("ctx_floor", "bulông neo hoá chất M24", (-300, 900, 0))],
    "pdf_measures §2.2 (chân cao 57 mm, 12 vị trí); số lượng và vị trí giả định theo chiều dài khung mới",
    ["22 chân Ø200 × 60 (đĩa đệm cao su + vít chỉnh M30), mỗi bên 11 chân tại Y = ±900.",
     "X = −5 050, −3 900, −2 700, −1 500, −300, 600, 1 700, 2 800, 3 900, 5 000, 5 850."],
    count=22, item_mm=[200, 200, 60], positions_mm=[[x, y, 30] for x in FEET_X for y in (-900, 900)])

add("base_drip_tray", "base", "Khay hứng nhỏ giọt trên khung", "Drip tray on frame top",
    "Hứng nước, dầu, nhựa rơi dưới xi lanh để không chảy vào hộp tủ.", "sheet",
    bb(400, 5900, -440, 440, 650, 690), "stainless",
    [("base_frame_process", "đặt trên mặt khung, mép gập 40 mm", (3000, 0, 650))],
    "giả định: chi tiết thường có trên máy đùn (web-01 cho thấy mặt khung kín dưới xi lanh)",
    ["Tôn inox 3 mm, mép gập cao 40 mm, có lỗ xả ở đầu X = 5 900."])

for i, xc in enumerate([1183, 3211, 5239], start=1):
    bname = {1: "barrel_b2", 2: "barrel_b4", 3: "barrel_b6"}[i]
    add(f"barrel_support_{i}", "base", f"Gối đỡ xi lanh số {i}", f"Barrel support saddle {i}",
        "Đỡ xi lanh từ dưới, cho phép xi lanh giãn nở nhiệt trượt theo X (điểm cố định ở lantern X = 0).",
        "extrude", bb(xc - 125, xc + 125, -350, 350, 650, 1034), "frame",
        [("base_frame_process", "bắt 4 bulông M30, lỗ ô van cho chỉnh", (xc, 0, 650)),
         (bname, "tấm trượt đồng/PTFE dưới thân xi lanh, kẹp giữ Y nhưng tự do X", (xc, 0, 940))],
        "web-02 (gối đúc trắng hình chữ A có lỗ); vị trí giả định: giữa B2, B4, B6, tránh các mối nối bích",
        ["Gối đúc hình chữ A, tấm đế 700 × 250, lỗ tròn Ø120 giữa thân tại Z ≈ 800.",
         "Lòng đỡ cong bán kính 260 ôm đáy thân xi lanh, có tấm trượt (slide pad) mỏng.",
         "Đệm trên của gối rộng 70 mm (X), tì vào băng thân trần rộng 74 mm giữa hai vỏ nhiệt của đoạn."],
        outline_mm={"plane": "YZ", "d0": xc - 125, "d1": xc + 125,
                    "pts": [[-350, 650], [350, 650], [350, 690], [230, 690], [200, 1034], [140, 981],
                            [0, 940], [-140, 981], [-200, 1034], [-230, 690], [-350, 690]]})

add("melt_stand_sc", "base", "Giá đỡ bộ lọc lưới", "Screen changer stand",
    "Đỡ bộ lọc lưới 3,8 t và giữ tâm dòng chảy ở Z = 1 200.", "frame",
    bb(6550, 7350, -600, 600, 0, 650), "frame",
    [("melt_screen_changer", "tấm trượt PTFE, chốt dẫn hướng Y", (6950, 0, 650)),
     ("ctx_floor", "tấm đế bắt bulông neo", (6950, 0, 0)),
     ("melt_heater_jbox", "giá gá mặt −Y", (6950, -600, 550))],
    "giả định: Gneuss giao bộ lọc kèm khung; chiều cao = 1 200 − D 550 (c050)",
    ["Khung thép hộp 4 chân, tấm đỉnh 800 × 1 200 × 30, giằng chéo hai bên.",
     "Mặt đỉnh Z = 650 trùng đáy thân bộ lọc; giữa bộ lọc và tấm đỉnh có tấm trượt PTFE: tự do theo X ±40 mm (giãn nở của xi lanh + đường chảy), dẫn hướng theo Y.",
     "Chỉ tấm đế (sole plate) được neo xuống sàn; mặt −Y mang hộp đấu nhiệt đường chảy."])

add("melt_stand_pump", "base", "Giá đỡ bơm nhựa và ống", "Gear pump and melt pipe stand",
    "Đỡ bơm bánh răng, ống nhựa và bộ trộn tĩnh.", "frame",
    bb(7400, 8650, -450, 450, 0, 970), "frame",
    [("melt_gear_pump", "chân bơm trên tấm trượt PTFE", (7700, 0, 970)),
     ("melt_pipe_saddles", "gối ống bắt vít lên mặt đỉnh", (8250, 0, 970)),
     ("ctx_floor", "tấm đế bắt bulông neo", (8000, 0, 0))],
    "giả định: khung riêng cho bơm như ảnh web-07 (khung đỡ dưới đường chảy); rút ngắn để xe khuôn chạy vào dưới bộ trộn",
    ["Khung thép hộp 6 chân, mặt đỉnh 1 250 × 900, Z = 970; kết thúc ở X = 8 650 để chừa chỗ cho đế xe khuôn.",
     "Bơm đặt trên tấm trượt PTFE (tự do X ±40, dẫn hướng Y); chỉ tấm đế được neo."])

add("melt_pipe_saddles", "base", "Gối đỡ ống nhựa", "Melt pipe saddles",
    "Đỡ ống nhựa và bộ trộn tĩnh, cho trượt theo X khi giãn nở.", "box",
    bb(8175, 8635, -120, 120, 970, 1050), "steel",
    [("melt_stand_pump", "bắt vít lên mặt khung", (8250, 0, 970)),
     ("melt_pipe", "gối chữ V có đệm cách nhiệt", (8250, 0, 1050)),
     ("melt_static_mixer", "gối chữ V có đệm cách nhiệt", (8560, 0, 1050))],
    "giả định", ["2 gối chữ V 150 × 240 cao 80 tại X = 8 250 (ống) và 8 560 (bộ trộn), mặt trượt cho X."],
    count=2, item_mm=[150, 240, 80], positions_mm=[[8250, 0, 1010], [8560, 0, 1010]])

add("melt_valve_support", "base", "Giá đỡ van khởi động", "Diverter valve support bracket",
    "Đỡ van khởi động và đầu xi lanh (≈ 1,3 t) đang treo ngoài gối đỡ cuối; con lăn/PTFE cho phép giãn nở theo X.",
    "extrude", bb(5950, 6090, -260, 260, 560, 940), "frame",
    [("base_frame_process", "bắt 4 bulông vào tấm đầu khung X = 5 950", (5950, 0, 600)),
     ("melt_startup_valve", "2 đệm PTFE dưới đáy van tại Y = ±205", (6040, 205, 940))],
    "review-01 I8; giả định",
    ["Hai tai thép chữ L tại Y = ±(150…260), bắt vào mặt đầu khung (Z 560–650) rồi vươn lên Z 940; mỗi tai mang 1 đệm PTFE 90 × 110.",
     "Chừa giữa Y ±150 cho máng xả nhựa; đáy giá ở Z 560, trên miệng xe hứng (Z 520)."],
    outline_mm={"plane": "XZ", "d0": -260, "d1": 260,
                "pts": [[5950, 560], [6000, 560], [6090, 880], [6090, 940], [5996, 940], [5996, 650], [5950, 650]]})

add("pump_drive_pedestal", "base", "Bệ hộp giảm tốc bơm", "Gear pump drive pedestal",
    "Đỡ hộp giảm tốc và động cơ bơm nhựa phía sau (−Y).", "frame",
    bb(7451, 7951, -1750, -1300, 0, 950), "frame",
    [("melt_pump_gearbox", "4 bulông M24", (7701, -1525, 950)),
     ("ctx_floor", "bulông neo", (7701, -1525, 0))],
    "giả định: bố trí như web-07 (hộp giảm tốc + động cơ đứng cạnh bơm)",
    ["Khung hộp thép 500 × 450, cao 950."])

# =========================================================== DRIVE
add("lantern", "drive", "Lantern (hộp nối hộp số – xi lanh)", "Lantern / intermediate housing",
    "Nối mặt bích ra hộp số với xi lanh B1; chứa khớp then hoa nối trục ra hộp số với trục vít; có cửa thăm.",
    "extrude", bb(-750, 0, -450, 450, 650, 1660), "blue_drive",
    [("gearbox", "mặt bích 16 bulông M30 tại X = −750", (-750, 0, 1200)),
     ("barrel_b1", "mặt bích Ø700, 20 bulông cấy M24 trên PCD 560 tại X = 0", (0, 0, 1200)),
     ("base_frame_drive", "chân lantern bắt 4 bulông", (-375, 0, 650)),
     ("screws", "ống then hoa (spline sleeve) bên trong", (-400, 0, 1200))],
    "pdf_measures §2.2 (lantern 15,26 × 19,68 pt có cửa thăm bo góc); màu theo web-01 (khối nối xanh như hộp số)",
    ["Cửa thăm chữ nhật bo góc 380 × 250 trên mặt +Y, tâm X = −375, Z = 1 200, 8 vít + tay nắm.",
     "Vành mặt bích Ø700 dày 60 ở đầu X = 0: 20 lỗ ren M24 trên PCD 560 nhận bulông cấy từ bích B1 (đai ốc 12 cạnh nằm phía B1).",
     "Ống xả dầu rò rỉ ở đáy, tai cẩu trên nóc.",
     "Trong: 2 khớp then hoa (spline coupling) tại Y = ±71."],
    outline_mm={"plane": "XZ", "d0": -450, "d1": 450,
                "pts": [[-750, 760], [-600, 760], [-600, 650], [-150, 650], [-150, 760], [0, 760],
                        [0, 1660], [-750, 1660]]})

add("gearbox", "drive", "Hộp số chia công suất", "Power-split twin-screw gearbox",
    "Giảm tốc từ động cơ (≈ 1 490 v/ph) xuống tối đa 400 v/ph và chia mômen 2 × 35 kNm ra hai trục vít đồng hướng.",
    "extrude", bb(-2300, -750, -700, 700, 650, 1720), "blue_drive",
    [("base_frame_drive", "8 chân bắt bulông M42", (-1500, 0, 650)),
     ("lantern", "mặt bích ra", (-750, 0, 1200)),
     ("drive_safety_coupling", "trục vào Ø160 có then, nắp ổ trục vào", (-2300, 0, 1200)),
     ("lube_pipe_pressure", "cổng dầu áp lực G1¼ phía +Y", (-2000, 700, 1500)),
     ("lube_pipe_return", "cổng hút đáy carter G2 phía +Y", (-1500, 700, 760)),
     ("drive_coupling_guard", "vỏ che áp mặt hộp số", (-2300, 0, 1500))],
    "c033 (chia công suất, bôi trơn ngâm + áp lực, khớp an toàn); c005 mômen; tỷ lệ dài/cao theo pdf_measures §2.3; màu xanh theo web-01/web-03, c023",
    ["Vỏ gang hộp có gân, phần bướu trên cao Z 1 720 bao 2 trục ra ở đầu X −1 250 … −750.",
     "Nắp ổ trục vào tròn Ø500 nhô 50 mm ở đầu X = −2 300 quanh Z = 1 200.",
     "4 tai cẩu (lifting eyes) trên nóc, nắp thăm chữ nhật trên nóc, ống thở (breather), kính thăm mức dầu phía +Y, nút xả dầu ở đáy.",
     "Biển tên, tem cảnh báo vàng; cảm biến nhiệt dầu PT100 cạnh cổng dầu.",
     "Tỷ số truyền ≈ 3,73 (1 490/400)."],
    outline_mm={"plane": "XZ", "d0": -700, "d1": 700,
                "pts": [[-2250, 650], [-750, 650], [-750, 1720], [-1250, 1720], [-1320, 1650],
                        [-2250, 1650], [-2250, 1450], [-2300, 1450], [-2300, 950], [-2250, 950]]})

add("drive_safety_coupling", "drive", "Khớp an toàn giới hạn mômen", "Torque-limiting safety coupling",
    "Tách động cơ khỏi hộp số khi quá tải (vít kẹt, vật lạ) để bảo vệ trục vít và hộp số.",
    "revolve", cylx(-2700, -2300, 320), "polished",
    [("gearbox", "moay-ơ côn trên trục vào", (-2300, 0, 1200)),
     ("drive_flex_coupling", "mặt bích 12 bulông", (-2700, 0, 1200))],
    "c033 (safety coupling); p05/p19 (đĩa ly hợp bạc giữa động cơ và hộp số); cỡ giả định",
    ["Đĩa thép bạc Ø640 có rãnh vòng (như ảnh p19), vòng bulông 12 lỗ, công tắc giám sát nhả khớp."],
    axis="X", radius_mm=320, length_mm=400,
    profile_mm=[[0, 0], [320, 0], [320, 300], [200, 300], [200, 400], [0, 400]])

add("drive_flex_coupling", "drive", "Khớp nối đàn hồi", "Flexible coupling",
    "Bù lệch tâm giữa trục động cơ và trục vào hộp số, giảm va đập.", "revolve",
    cylx(-2950, -2700, 280), "steel",
    [("drive_motor", "moay-ơ trên trục động cơ Ø140", (-2950, 0, 1200)),
     ("drive_safety_coupling", "mặt bích 12 bulông", (-2700, 0, 1200))],
    "giả định (khớp đĩa/đàn hồi tiêu chuẩn cỡ 10 kNm)",
    ["Hai moay-ơ thép + bộ đĩa lò xo, Ø560."],
    axis="X", radius_mm=280, length_mm=250,
    profile_mm=[[0, 0], [150, 0], [150, 40], [280, 40], [280, 210], [150, 210], [150, 250], [0, 250]])

add("drive_coupling_guard", "drive", "Vỏ che khớp nối", "Coupling guard",
    "Che phần quay giữa động cơ và hộp số, có khoá liên động.", "box",
    bb(-2980, -2300, -450, 450, 650, 1650), "orange",
    [("base_frame_drive", "thanh góc chân bắt vít", (-2640, 0, 650)),
     ("gearbox", "áp vào mặt hộp số", (-2300, 0, 1500))],
    "pdf_measures §2.2 (vỏ khớp nối có móc cẩu trên nóc); màu cam theo web-12",
    ["Tôn 3 mm, tấm hông +Y tháo được có ô lưới quan sát, móc cẩu trên nóc.",
     "Công tắc liên động (interlock) cấm chạy khi mở nắp."])

add("drive_motor", "drive", "Động cơ chính 1 500 kW, làm mát gió–nước trên nóc", "Main AC motor 1 500 kW, IC81W top air-to-water cooler (ABB AMI 450L4 frame)",
    "Động cơ cảm ứng trung thế 4 cực, chạy biến tần, quay trục vít qua khớp nối và hộp số; bộ làm mát gió–nước trên nóc thải nhiệt vào nước, không thổi gió nóng vào xưởng.",
    "extrude", bb(-4975, -2950, -575, 575, 750, 2610), "motor",
    [("drive_motor_base", "4 chân bắt bulông M36 (B 1 400 × A 850)", (-4000, 0, 750)),
     ("drive_flex_coupling", "đầu trục Ø140", (-2950, 0, 1200)),
     ("drive_motor_terminal_box", "hộp đấu dây bắt mặt bên −Y", (-4000, -575, 1350)),
     ("drive_encoder", "bích encoder ở đầu NDE", (-4975, 0, 1200)),
     ("util_cw_motor_hoses", "2 bích nước DN40 trên mặt +Y bộ làm mát", (-3500, 575, 2300))],
    "c066 (AMI 450L: L 2 025, H 450, HC 1 860, A 850, B 1 400, AB 980, AE 1 500); c065 khối lượng ≈ 4,7 t; công suất 1 500 kW giả định (xem design.md §3); DECISIONS 11.3 + review-01 M9: kiểu làm mát IC81W (bộ làm mát gió–nước trên nóc), giả định giữ nguyên hình bao HC 1 860 như bản IC01",
    ["Thân hộp có gân Z 750–1 680; trên nóc là hộp bộ làm mát gió–nước (IC81W top air-to-water cooler) Z 1 680–2 610, X −4 800 … −3 300: vỏ hộp kín, 2 nắp thăm ống trao đổi nhiệt ở đầu −X, không có cửa gió hở.",
     "Hai bích nước DN40 trên mặt +Y của hộp làm mát: vào tại X −3 500, Z 2 300; ra tại X −3 700, Z 2 400; cảm biến rò nước ở đáy hộp.",
     "Đầu trục Ø140 dài 200 ở phía hộp số; nắp ổ NDE nhô 75 mm mang encoder.",
     "4 tai cẩu, biển tên, cọc tiếp địa; tâm trục Z = 1 200 (H 450 trên mặt đế Z 750)."],
    axis="X",
    outline_mm={"plane": "XZ", "d0": -575, "d1": 575,
                "pts": [[-4900, 750], [-3150, 750], [-3150, 1130], [-2950, 1130], [-2950, 1270],
                        [-3150, 1270], [-3150, 1680], [-3300, 1680], [-3300, 2610], [-4800, 2610],
                        [-4800, 1680], [-4900, 1680], [-4900, 1400], [-4975, 1400], [-4975, 1000],
                        [-4900, 1000]]})

add("drive_motor_terminal_box", "drive", "Hộp đấu dây động cơ", "Motor terminal box",
    "Đấu cáp trung thế từ biến tần vào động cơ.", "box",
    bb(-4300, -3700, -925, -575, 1100, 1600), "motor",
    [("drive_motor", "bắt bulông lên thân", (-4000, -575, 1350)),
     ("ctrl_cable_mv", "đầu cáp vào qua đáy hộp", (-4000, -925, 1150))],
    "c066 (AE 1 500 gồm hộp đấu dây); phía −Y giả định để tránh lối thao tác",
    ["Hộp thép 600 × 350 × 500, nắp 12 vít, ốc siết cáp ở đáy."])

add("drive_motor_base", "drive", "Đế động cơ", "Motor sub-base",
    "Nâng động cơ để tâm trục khớp Z = 1 200, cho phép căn chỉnh đồng tâm.", "frame",
    bb(-5000, -3000, -600, 600, 650, 750), "dark_steel",
    [("base_frame_drive", "bắt bulông, chêm căn", (-4000, 0, 650)),
     ("drive_motor", "4 chân động cơ, vít đẩy căn chỉnh", (-4000, 0, 750))],
    "giả định: 1 200 − H 450 − đỉnh khung 650 = 100 mm",
    ["Hai ray thép dày 100 có vít đẩy (jack screws) căn chỉnh ngang."])

add("drive_encoder", "drive", "Encoder tốc độ", "Speed encoder",
    "Đo tốc độ / vị trí trục động cơ cho biến tần điều khiển vector.", "cyl",
    cylx(-5075, -4975, 80), "black",
    [("drive_motor", "bích + khớp nối nhỏ ở đầu trục NDE", (-4975, 0, 1200))],
    "giả định (biến tần trung thế điều khiển vòng kín)",
    ["Vỏ Ø160 × 100, đầu cáp tín hiệu."], axis="X", radius_mm=80, length_mm=100)

add("lube_unit_frame", "drive", "Khay đế cụm dầu bôi trơn", "Lube unit tray",
    "Đế và khay hứng dầu cho cụm bơm, lọc, làm mát dầu hộp số.", "sheet",
    bb(-3600, -2450, 600, 1000, 650, 700), "blue_drive",
    [("base_frame_drive", "bắt vít lên mặt khung", (-3000, 800, 650)),
     ("lube_pump_motor", "bắt bulông", (-3350, 800, 700)),
     ("lube_filter_duplex", "giá đỡ bắt vít", (-3075, 800, 700)),
     ("lube_oil_cooler", "giá đỡ bắt vít", (-2775, 775, 700))],
    "pdf_measures §2.2 (cụm dầu phía trước động cơ trên hình bóng); web-03; c034",
    ["Khay có mép gập, tấm thấm dầu vàng như web-03."])

add("lube_pump_motor", "drive", "Bơm dầu + động cơ mặt bích đứng", "Lube oil pump with vertical flange motor",
    "Hút dầu từ carter hộp số và đẩy qua lọc, bộ làm mát tới vòi phun bánh răng/ổ trục.", "composite",
    bb(-3500, -3200, 650, 950, 700, 1450), "blue_drive",
    [("lube_unit_frame", "chân bơm bắt bulông", (-3350, 800, 700)),
     ("lube_filter_duplex", "ống nối ren", (-3200, 800, 1000)),
     ("lube_pipe_return", "cổng hút", (-3350, 950, 760))],
    "web-03 (bơm có động cơ mặt bích đứng, sơn xanh); p19_3",
    ["Động cơ 4 kW đặt đứng Ø260 có nắp quạt, chuông nối, bơm bánh răng ở đáy; 2 đồng hồ áp.",
     "Van an toàn (relief valve) tích hợp trên thân bơm xả về carter; lọc hút (suction strainer) trên ống hút ngay trước bơm."])

add("lube_filter_duplex", "drive", "Lọc dầu kép", "Duplex oil filter",
    "Lọc dầu, đổi bầu lọc khi máy chạy.", "composite",
    bb(-3200, -2950, 680, 950, 700, 1400), "blue_drive",
    [("lube_pump_motor", "ống nối", (-3200, 800, 1000)),
     ("lube_oil_cooler", "ống nối", (-2950, 800, 900)),
     ("lube_unit_frame", "giá đỡ", (-3075, 800, 700))],
    "web-03 (2 bầu lọc + tay gạt chuyển đổi); pdf_measures §2.2 (lọc kép trước động cơ)",
    ["2 bầu lọc đứng Ø110, tay gạt chuyển đổi, chỉ báo chênh áp, đồng hồ áp."])

add("lube_oil_cooler", "drive", "Bộ làm mát dầu tấm", "Plate oil cooler (oil/water)",
    "Giải nhiệt dầu hộp số bằng nước làm mát.", "box",
    bb(-2950, -2600, 650, 900, 700, 1050), "stainless",
    [("lube_filter_duplex", "ống nối", (-2950, 800, 900)),
     ("lube_pipe_pressure", "cổng dầu ra F3", (-2775, 775, 1050)),
     ("util_cw_lube_hoses", "cổng nước F2/F4", (-2775, 900, 850)),
     ("lube_unit_frame", "giá đỡ", (-2775, 775, 700))],
    "web-03 (bộ trao đổi nhiệt tấm inox có cổng F1–F4)",
    ["Khối tấm hàn inox 350 × 250 × 350, 4 cổng ren F1–F4 trên mặt +Y."])

LUBE_P = [(-2775, 775, 1050), (-2775, 775, 1500), (-2000, 775, 1500), (-2000, 700, 1500)]
add("lube_pipe_pressure", "drive", "Ống dầu áp lực tới hộp số", "Lube pressure line",
    "Dẫn dầu đã lọc, làm mát tới hệ phun trong hộp số.", "pipe", pipe_bb(LUBE_P, 21), "blue_drive",
    [("lube_oil_cooler", "ren G1¼", LUBE_P[0]), ("gearbox", "ren G1¼", LUBE_P[-1])],
    "web-03 (ống dầu sơn xanh); tuyến ống giả định", ["Ống thép DN32 (OD 42) sơn xanh; công tắc áp suất (PS, khoá khởi động truyền động) gần cổng vào hộp số, tín hiệu về tủ đầu máy (s_14)."],
    path_mm=[list(p) for p in LUBE_P], radius_mm=21)

LUBE_R = [(-1500, 700, 760), (-1500, 975, 760), (-3350, 975, 760), (-3350, 950, 760)]
add("lube_pipe_return", "drive", "Ống hút dầu từ carter", "Lube suction line",
    "Dẫn dầu từ carter hộp số về bơm.", "pipe", pipe_bb(LUBE_R, 25), "blue_drive",
    [("gearbox", "ren G2 đáy carter", LUBE_R[0]), ("lube_pump_motor", "cổng hút", LUBE_R[-1])],
    "giả định", ["Ống thép DN40 (OD 50) chạy dọc mép +Y của khung, Z = 760."],
    path_mm=[list(p) for p in LUBE_R], radius_mm=25)

# =========================================================== BARREL
BNAME = ["b1", "b2", "b3", "b4", "b5", "b6"]
BDESC = {
    "B1": ("Xi lanh B1 – cấp liệu 4D", "Barrel B1, feed barrel 4D (water-cooled)",
           "Nhận hạt PET từ miệng cấp liệu; làm mát bằng nước để hạt không chảy sớm.",
           ["Lỗ nạp trên đỉnh 360 × 300 tại X 160–520, mặt gia công phẳng cho hộp miệng nạp.",
            "Không có băng nhiệt; áo nước làm mát, 2 đầu nối nước ở đáy tại X = 200 (vào) và 476 (ra).",
            "Đầu X = 0: bích Ø640 bắt 20 bulông cấy M24 trên PCD 560 vào lantern, đai ốc 12 cạnh phía B1.",
            "Cặp nhiệt B1 cắm nghiêng 40° ở góc trên phía −Y, chân tại (X 338, Y -167, Z 1399), để tránh hộp miệng nạp."]),
    "B2": ("Xi lanh B2 – 6D mở bên (side feeder)", "Barrel B2, 6D side-open (combination) barrel",
           "Vận chuyển hạt, nhận liệu phụ từ side feeder qua cửa bên +Y, bắt đầu nóng chảy ở cuối đoạn.",
           ["Cửa bên +Y 340 × 260 tại X 1 180–1 520 (hình số 8 nhìn ngang) có mặt bích cho side feeder.",
            "2 băng nhiệt có cửa sổ tránh cửa bên; lỗ khoan nước làm mát dọc thân."]),
    "B3": ("Xi lanh B3 – 6D thoát khí chân không vùng 1", "Barrel B3, 6D top-open (first vacuum vent)",
           "Nóng chảy (khối nhào) rồi hút chân không nhẹ (≈ 50 mbar) ngay khi nhựa vừa chảy, rút phần lớn hơi nước trước khi PET bị thuỷ phân và không cho không khí lọt vào.",
           ["Lỗ trên đỉnh 320 × 280 tại X 1 990–2 310 với tấm lót (vent insert); vòm chân không 2 lắp trên.", "2 băng nhiệt có khe tại lỗ."]),
    "B4": ("Xi lanh B4 – 6D kín", "Barrel B4, 6D closed",
           "Trộn, đồng nhất nhựa nóng chảy; trước B5 có phần tử nghịch tạo nút nhựa kín chân không.",
           ["2 băng nhiệt, lỗ khoan nước làm mát, 1 cặp nhiệt."]),
    "B5": ("Xi lanh B5 – 6D thoát khí chân không sâu (vùng 2)", "Barrel B5, 6D top-open (deep vacuum vent)",
           "Hút chân không sâu (5–20 mbar) để khử nốt ẩm, acetaldehyde và oligome của PET không sấy.",
           ["Lỗ trên đỉnh 520 × 280 tại X 3 860–4 380 (≈ 3D) với tấm lót (vent insert); vòm chân không lắp trên.",
            "2 băng nhiệt có khe tại lỗ."]),
    "B6": ("Xi lanh B6 – 6D kín tăng áp", "Barrel B6, 6D closed (pressure build-up)",
           "Tăng áp đẩy nhựa vào đầu xi lanh.",
           ["Cổng bên +Y bịt mặt bích tròn (cổng phun lỏng dự phòng) tại X ≈ 5 400, Z = 1 200 – thấy qua tấm tròn 10 bulông của vỏ che C1 (trang 9).",
            "Mặt bích ra X = 5 746: 20 bulông cấy M24 trên PCD 560 vào bích đầu xi lanh."]),
}
for k, (s, e) in enumerate(BAR):
    nm = BNAME[k]
    vi, en, fn, det = BDESC[nm.upper()]
    conn = []
    if k == 0:
        conn.append(("lantern", "mặt bích, 20 bulông cấy M24 trên PCD 560", (0, 0, 1200)))
        conn.append(("feed_throat", "mặt gia công đỉnh, 8 bulông M20", (340, 0, 1460)))
    if k > 0:
        conn.append((f"barrel_joint_{k}", "mặt bích Ø640, 20 bulông cấy M24", (s + 10, 0, 1480)))
    if k < 5:
        conn.append((f"barrel_joint_{k + 1}", "mặt bích Ø640, 20 bulông cấy M24", (e - 10, 0, 1480)))
    if k == 5:
        conn.append(("melt_head_adapter", "mặt bích, 20 bulông cấy M24 trên PCD 560", (5746, 0, 1200)))
    conn.append(("screws", "lỗ hình số 8 chứa 2 trục vít", ((s + e) / 2, 0, 1200)))
    if k == 0:
        conn.append(("barrel_cw_hoses", "đầu nối nhanh nước vào ở đáy", (200, 0, 940)))
        conn.append(("barrel_cw_hoses", "đầu nối nhanh nước ra ở đáy", (476, 0, 940)))
    else:
        conn.append(("barrel_cw_hoses", "đầu nối nước vào, góc dưới +Y 45°", (s + 200, 184, 1016)))
        conn.append(("barrel_cw_hoses", "đầu nối nước ra, góc dưới +Y 45°", (e - 200, 184, 1016)))
        det = det + [f"2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = {s + 200} (vào) và {e - 200} (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ."]
    if k == 1:
        conn.append(("sidefeed_adapter", "mặt bích cửa bên +Y", (1350, 260, 1200)))
        conn.append(("barrel_support_1", "tấm trượt", (1183, 0, 940)))
    if k == 2:
        conn.append(("barrel_vent_dome_2", "mặt bích vent insert", (2150, 0, 1460)))
    if k == 3:
        conn.append(("barrel_support_2", "tấm trượt", (3211, 0, 940)))
    if k == 4:
        conn.append(("barrel_vent_dome", "mặt bích vent insert", (4120, 0, 1460)))
    if k == 5:
        conn.append(("barrel_support_3", "tấm trượt", (5239, 0, 940)))
    L = e - s
    add(f"barrel_{nm}", "barrel", vi, en, fn, "revolve", cylx(s, e, R_FL), "steel", conn,
        "c001 D = 169, c031 đoạn 4D/6D, c032 thép thấm nitơ; DECISIONS 9 (1×4D + 5×6D), DECISIONS 11 (nối bích bắt bulông); hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut); Ø thân 520 / bích 600 giả định (lỗ số 8 rộng 311 + thành ≈ 105)",
        ["Thân trụ Ø520, mặt bích Ø640 × 50 hai đầu; mỗi bích 20 lỗ Ø26 trên PCD 560 (mép lỗ cách mép bích 27 mm), một bích có gờ định tâm, bích kia có rãnh.",
         "Sau mỗi bích thân tiện thắt Ø500 dài 40 mm (vùng đặt đai ốc), để có khe 12 mm cho khẩu 12 cạnh thành mỏng khi tháo vỏ nhiệt; vỏ nhiệt bắt đầu ngay sau đoạn thắt.",
         "Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71)."] + det,
        axis="X", radius_mm=R_BODY, length_mm=L,
        profile_mm=[[0, 0], [R_FL, 0], [R_FL, 50], [R_NECK, 50], [R_NECK, 50 + L_NECK], [R_BODY, 50 + L_NECK],
                    [R_BODY, L - 50 - L_NECK], [R_NECK, L - 50 - L_NECK], [R_NECK, L - 50], [R_FL, L - 50], [R_FL, L], [0, L]])

for j, J in enumerate(JOINTS, start=1):
    stud_pos = []
    for k in range(N_BOLT):
        t = math.radians(9 + 360.0 * k / N_BOLT)
        stud_pos.append([J, r1(PCD / 2 * math.cos(t)), r1(AXZ + PCD / 2 * math.sin(t))])
    add(f"barrel_joint_{j}", "barrel", f"Mối nối bích bắt bulông {j} (X = {J})", f"Bolted flange joint {j}",
        "Ép hai mặt bích Ø640 của hai đoạn xi lanh vào nhau cho kín áp nhựa, định tâm hai lỗ số 8; tháo được khi đổi cấu hình xi lanh.",
        "revolve", cylx(J - L_BOLT / 2, J + L_BOLT / 2, R_JOINT), "steel",
        [(f"barrel_{BNAME[j - 1]}", "mặt bích đoạn trước, 20 lỗ Ø26", (J - 10, 0, 1480)),
         (f"barrel_{BNAME[j]}", "mặt bích đoạn sau, 20 lỗ Ø26", (J + 10, 0, 1480))],
        "c037 (ZE cỡ lớn nối các đoạn bằng bulông thay kẹp), web-01/02 (vành bích bắt bulông trên ZE 110 R UT thật); DECISIONS 11; cỡ bulông giả định (tính lực siết, kiểm tra chỗ đặt đai ốc)",
        ["20 bulông cấy M24 cấp 10.9 chịu nhiệt, mỗi bulông 2 đai ốc 12 cạnh (Ø36 qua đỉnh) có vòng đệm, trên PCD 560, chia đều 18°, lệch 9° để không có bulông đúng đỉnh/đáy.",
         "Bulông dài 164: xuyên 2 bích × 50 mm, mỗi đầu đai ốc cao 24 + 8 mm ren thừa; đai ốc nằm trong vành r 262–298, trên đoạn thân thắt Ø500 (khe 12 mm), mép lỗ cách mép bích Ø640 27 mm.",
         "Giữa hai bích: gờ định tâm (centring spigot) Ø400 và mặt kín kim loại; mặt ngoài vành bích tiện bóng, đai ốc thép đen.",
         "Lực siết ≈ 20 × 200 kN = 4 MN, gấp ≈ 3 lần lực đẩy của nhựa 300 bar trên lỗ số 8 (≈ 1,2 MN).",
         "Không dùng M30 trên PCD 545: đai ốc M30 (đối đỉnh 53 mm) sẽ chạm thân xi lanh Ø520."],
        axis="X", radius_mm=R_FL, length_mm=L_BOLT,
        profile_mm=[[262, 0], [298, 0], [298, L_BOLT], [262, L_BOLT]],
        count=N_BOLT, item_mm=[L_BOLT, 36, 36], positions_mm=stud_pos)

HS_POS = []
for s, e in BAR[1:]:
    HS_POS += [[s + 90 + 190, 0, AXZ], [e - 90 - 190, 0, AXZ]]
add("barrel_heater_shells", "barrel", "Băng nhiệt gốm bọc inox", "Ceramic band heater shells",
    "Gia nhiệt xi lanh B2–B6, mỗi đoạn 6D một vùng nhiệt ≈ 25 kW.", "revolve",
    bb(766, 5656, -290, 290, 910, 1490), "polished",
    [("barrel_b2", "kẹp bulông quanh thân", (1183, 0, 1490)),
     ("barrel_b3", "kẹp bulông quanh thân", (2197, 0, 1490)),
     ("barrel_b4", "kẹp bulông quanh thân", (3211, 0, 1490)),
     ("barrel_b5", "kẹp bulông quanh thân", (4225, 0, 1490)),
     ("barrel_b6", "kẹp bulông quanh thân", (5239, 0, 1490))],
    "web-01/02 (vỏ nhiệt inox bóng, mép có gân); c018 (30 kW/đoạn trên ZE 180) → 25 kW giả định",
    ["10 vỏ (2 mỗi đoạn 6D), mỗi vỏ Ø580 dài 380, gồm 2 nửa bản lề, kẹp bằng 2 bulông, mép có vòng gân đục lỗ.",
     "Mỗi vỏ bắt đầu cách mặt đầu đoạn 90 mm (chừa chỗ đai ốc của mối nối bích); giữa hai vỏ của một đoạn có băng thân trần 74 mm cho gối đỡ.",
     "Vỏ có cửa sổ tại cửa bên B2 và lỗ đỉnh B3/B5; rãnh 50 mm ở góc dưới +Y tại X = đầu đoạn + 200 và cuối đoạn − 200 cho đầu nối nước.",
     "Hộp đấu nhỏ trên mỗi vỏ, cáp bọc lưới inox đi xuống hộp đấu dây phía −Y."],
    count=10, item_mm=[380, 580, 580], positions_mm=HS_POS, axis="X")

add("screws", "barrel", "Hai trục vít đồng hướng", "Co-rotating twin screws",
    "Vận chuyển, nóng chảy, trộn, khử khí và tăng áp nhựa; tự làm sạch lẫn nhau.", "composite",
    bb(-400, 5746, -71 - 83.8, 71 + 83.8, AXZ - 83.8, AXZ + 83.8), "dark_steel",
    [("lantern", "trục then hoa 24 răng vào ống then hoa", (-400, 0, 1200)),
     ("barrel_b1", "nằm trong lỗ số 8", (338, 0, 1200)),
     ("barrel_b5", "thấy qua lỗ thoát khí", (4120, 0, 1200))],
    "c001/c002 (D 169, rãnh 27,2 → lõi 114,6), centre distance 142 (specs §1); c017 (then hoa 24 răng trên ZE 180); trình tự phần tử giả định",
    ["2 trục tại Y = ±71, Z = 1 200, Ø ngoài 167,5, lõi 114,6, 2 đầu ren (2-flight).",
     "Trình tự phần tử (X từ–tới): −400–0 trục then hoa trong lantern; 0–1 100 vận chuyển bước 1,5D (miệng nạp 160–520); 1 100–1 560 vận chuyển bước 1,5D dưới cửa side feeder (1 180–1 520); 1 560–1 880 khối nhào KB 45°/5 (nóng chảy); 1 880–1 950 KB 90° (nút nhựa, kết thúc trước lỗ vùng 1 ở 1 990); 1 950–2 420 vận chuyển bước rộng 1,5D dưới lỗ vùng 1 (1 990–2 310); 2 420–2 900 vận chuyển 1D; 2 900–3 380 khối nhào KB 45°/5 + KB 90° (trộn); 3 380–3 620 vận chuyển 1D; 3 620–3 720 phần tử nghịch LH (nút nhựa trước vùng 2); 3 720–4 450 vận chuyển bước rộng 1,5D dưới lỗ vùng 2 (3 860–4 380); 4 450–5 746 vận chuyển 1D → 0,75D (tăng áp).",
     "Thấy được qua miệng nạp B1, cửa B3 và vòm B5; cho bản vẽ cắt riêng (cut-away)."],
    axis="X")

add("barrel_vent_dome_2", "barrel", "Vòm thoát khí chân không vùng 1 (B3)", "First vacuum vent dome on B3",
    "Buồng kín trên lỗ B3, hút chân không nhẹ (≈ 50 mbar) để rút hơi nước ngay sau vùng chảy.", "extrude",
    bb(1950, 2350, -240, 210, 1455, 1960), "stainless",
    [("barrel_b3", "mặt bích vent insert 8 bulông", (2150, 0, 1460)),
     ("barrel_cover_c6", "xuyên qua lỗ khoét 420 × 380", (2150, 0, 1650)),
     ("vac_valve_2", "bích DN100 phía −Y", (2150, -240, 1800)),
     ("vac_gauge_dome_2", "ren trên nắp", (2280, 0, 1960))],
    "review-01 I4 (PET không sấy: hút chân không ngay sau vùng chảy, c040, c062); cỡ giả định",
    ["Thân hộp inox 400 × 360 bo góc R30 từ Z 1 460 lên 1 920; nắp dày 40 (Z 1 920–1 960) kẹp 4 bulông bướm, 2 tai.",
     "1 kính quan sát Ø120 có vành kẹp trên mặt +Y tại X 2 150, Z 1 750.",
     "Đầu ra DN100 có bích Ø220 trên mặt −Y tại X 2 150, Z 1 800."],
    outline_mm={"plane": "XZ", "pts": [[1950, 1460], [2350, 1460], [2350, 1960], [1950, 1960]], "d0": -180, "d1": 180})
dome_xz = [[3820, 1460], [4420, 1460], [4420, 2100], [4440, 2100], [4440, 2150], [3800, 2150],
           [3800, 2100], [3820, 2100]]
add("barrel_vent_dome", "barrel", "Vòm thoát khí chân không (B5)", "Vacuum vent dome on B5",
    "Tạo buồng kín trên lỗ thoát khí B5 để hút chân không; kính quan sát cho thấy nhựa không trào lên.",
    "extrude", bb(3800, 4440, -200, 230, 1455, 2150), "stainless",
    [("barrel_b5", "mặt bích vent insert 8 bulông", (4120, 0, 1460)),
     ("vac_valve", "mặt bích DN150 PN16 trên nắp", (4120, 0, 2150)),
     ("barrel_cover_c3", "xuyên qua lỗ khoét trên vỏ che", (4120, 0, 1650)),
     ("vac_gauge_dome", "ren trên nắp", (4310, 0, 2150))],
    "pdf_measures §2.2 (vòm dạng hộp cao, 2 kính quan sát, tai trên đỉnh); p01 (kính tròn có tay kẹp); c036 lỗ dài",
    ["Thân hộp inox 600 × 400, bo góc R40, từ Z 1 460 lên 2 100; nắp 640 × 450 dày 50 kẹp bằng 4 bulông bướm, 2 tai (lugs) trên nắp.",
     "2 kính quan sát Ø160 có vành kẹp trên mặt +Y tại X = 3 970 và 4 270, Z = 1 880.",
     "Đầu ra chân không DN150 ở giữa nắp (X 4 120, Y 0, Z 2 150), đi thẳng lên van chặn; mặt −Y của vòm phẳng, không có cổng.",
     "Tay nắm nâng nắp, đèn soi kính (tuỳ chọn)."],
    outline_mm={"plane": "XZ", "pts": dome_xz, "d0": -200, "d1": 200})

COVERS = {"C6": (1690, 2366), "C5": (2366, 3042), "C4": (3042, 3718), "C3": (3718, 4450),
          "C2": (4450, 5100), "C1": (5100, 5760)}
cover_yz = [[-480, 650], [480, 650], [480, 1480], [330, 1650], [-330, 1650], [-480, 1480]]
for cn in ["C1", "C2", "C3", "C4", "C5", "C6"]:
    cid = cn.lower()
    x0, x1 = COVERS[cn]
    xc = (x0 + x1) / 2
    conn = [("base_frame_process", "chân vỏ bắt vít vào mép khung", (xc, 0, 650))]
    det = ["Hộp inox xước 1,5 mm có cách nhiệt bông khoáng bên trong, vát 45° hai mép trên (xem outline).",
           "Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650 bản lề phía −Y, mở lên.",
           "Mặt +Y: tay nắm đen trên nắp và trên tấm dưới, tam giác vàng 'bề mặt nóng' ở giữa (như trang 9); 1 tay nắm trên đỉnh.",
           "Khe dưới hai bên cho ống nước và cáp nhiệt đi vào."]
    if cn == "C1":
        conn.append(("melt_head_adapter", "tấm đầu có lỗ Ø660 quanh bích đầu xi lanh", (5753, 0, 1480)))
        det.append("Tấm đầu X = 5 746–5 760 có lỗ tròn Ø660 (bích Ø640); mặt +Y có tấm tròn Ø420 bắt 10 bulông tại X ≈ 5 400, Z = 1 200 (trang 9) che cổng bên B6, cùng một hộp đấu dây nhỏ phía dưới.")
    if cn == "C3":
        conn.append(("barrel_vent_dome", "lỗ khoét 620 × 420 ôm vòm", (4120, 0, 1650)))
        det.append("Lỗ khoét 620 × 420 cho vòm chân không.")
    if cn == "C6":
        conn.append(("barrel_vent_dome_2", "lỗ khoét 420 × 380 ôm vòm vùng 1", (2150, 0, 1650)))
        det.append("Lỗ khoét 420 × 380 (X 1 940–2 360) cho vòm chân không vùng 1.")
        det.append("Tấm đầu phía X = 1 690 có lỗ Ø660 ôm vành bích Ø640 và đai ốc của mối nối 2 (nửa mối nối nằm ngoài vỏ, phía vùng nạp để lộ).")
    add(f"barrel_cover_{cid}", "barrel", f"Vỏ che xi lanh {cn}", f"Barrel insulation cover box {cn}",
        "Cách nhiệt và che bề mặt nóng của xi lanh, giữ nhiệt ổn định, bảo vệ người vận hành.",
        "extrude", bb(x0, x1, -480, 480, 650, 1650), "cover", conn,
        "pdf_measures §2.2 (6 vỏ hộp có tay nắm + tam giác cảnh báo, cao ≈ 0,98 × khoảng tâm, phủ ≈ 71 % chiều dài xi lanh); p16_1/p16_2; web-07",
        det, outline_mm={"plane": "YZ", "pts": cover_yz, "d0": x0, "d1": x1})

add("barrel_thermocouples", "barrel", "Cặp nhiệt xi lanh", "Barrel thermocouples",
    "Đo nhiệt độ từng vùng xi lanh cho bộ điều nhiệt.", "cyl",
    bb(323, 5254, -215, 15, 1321, 1548), "stainless",
    [("barrel_b1", "ren M14 lắp lưỡi lê, cắm nghiêng góc trên −Y", (338, -167.1, 1399.2)),
     ("barrel_b4", "ren M14", (3211, 0, 1460)),
     ("barrel_b6", "ren M14", (5239, 0, 1460))],
    "giả định (mỗi vùng 1 cặp nhiệt, như cáp nhiệt thấy ở web-01); vị trí theo review-01 C1",
    ["6 cặp nhiệt loại J Ø30 dài 90 (35 mm nằm trong thành xi lanh, 55 mm lộ ra): B1 cắm nghiêng 40° so với phương đứng về phía −Y, chân tại (338, -167, 1399) trên mặt thân, đầu dưới đáy hộp miệng nạp; còn lại cắm đứng trên đỉnh thân tại X = 1 450, 2 450, 3 211, 4 600, 5 239 (xuyên lỗ trên vỏ nhiệt), nắp lưỡi lê, cáp bọc lưới inox.",
     "item_mm = [Ø, Ø, dài] theo hệ trục riêng; trục từng cái trong item_axes."],
    count=6, item_mm=[30, 30, 90],
    item_axes=[[0.0, -0.6428, 0.766]] + [[0.0, 0.0, 1.0]] * 5,
    positions_mm=[[338, -173.6, 1406.8]] + [[x, 0, 1502.5] for x in (1450, 2450, 3211, 4600, 5239)])

CW_X = [338, 1183, 2197, 3211, 4225, 5239]
CWS = [(-300, 880, 710), (5400, 880, 710)]
add("barrel_cw_supply", "barrel", "Ống góp nước cấp", "Cooling-water supply header",
    "Phân phối nước làm mát tới các vùng xi lanh.", "pipe", pipe_bb(CWS, 30), "stainless",
    [("util_cw_supply_riser", "mặt bích DN50", CWS[0]), ("barrel_cw_valves", "6 nhánh T", (338, 880, 710))],
    "web-02, web-06 (ống góp inox dọc khung, 1 cụm van mỗi vùng); phía +Y theo web-06",
    ["Ống inox DN50 (OD 60), mũi tên chiều dòng, gá trên bát đỡ cách mặt khung 30 mm."],
    path_mm=[list(p) for p in CWS], radius_mm=30)
CWR = [(-300, 950, 800), (5400, 950, 800)]
add("barrel_cw_return", "barrel", "Ống góp nước hồi", "Cooling-water return header",
    "Gom nước hồi từ các vùng xi lanh.", "pipe", pipe_bb(CWR, 30), "stainless",
    [("util_cw_return_riser", "mặt bích DN50", CWR[0]), ("barrel_cw_valves", "6 nhánh T", (338, 950, 800))],
    "web-02", ["Ống inox DN50 (OD 60) song song phía ngoài ống cấp, Z = 800."],
    path_mm=[list(p) for p in CWR], radius_mm=30)
add("barrel_cw_valves", "barrel", "Cụm van điện từ nước làm mát", "Cooling-water solenoid valve stations",
    "Đóng/mở nước làm mát từng vùng theo lệnh bộ điều nhiệt.", "composite",
    bb(238, 5339, 820, 1000, 650, 1000), "stainless",
    [("barrel_cw_supply", "nhánh T", (338, 880, 710)),
     ("barrel_cw_return", "nhánh T", (338, 950, 800)),
     ("barrel_cw_hoses", "đầu nối ống mềm trên đỉnh cụm", (298, 910, 1000)),
     ("base_frame_process", "bát gá trên mặt khung", (1183, 900, 650))],
    "web-02 (mỗi vùng 1 van điện từ + van bi tay đỏ, đồng hồ áp); c023",
    ["6 cụm tại X = 338, 1 183, 2 197, 3 211, 4 225, 5 239; mỗi cụm: van bi tay đỏ, lọc Y, van điện từ (cuộn đen), van tiết lưu, chỉ báo dòng chảy.",
     "1 đồng hồ áp trên ống cấp, 1 trên ống hồi."], count=6, item_mm=[200, 180, 350],
    positions_mm=[[x, 910, 825] for x in CW_X])
CWH = [[(298, 910, 1000), (200, 560, 980), (200, 230, 960), (200, 0, 940)],
       [(476, 0, 940), (476, 230, 960), (476, 560, 980), (378, 910, 1000)]]
for (s_, e_), xc in zip(BAR[1:], CW_X[1:]):
    CWH.append([(xc - 40, 910, 1000), (s_ + 200, 560, 980), (s_ + 200, 230, 1000), (s_ + 200, 184, 1016)])
    CWH.append([(e_ - 200, 184, 1016), (e_ - 200, 230, 1000), (e_ - 200, 560, 980), (xc + 40, 910, 1000)])
add("barrel_cw_hoses", "barrel", "Ống mềm nước tới xi lanh", "Armoured cooling hoses to barrels",
    "Dẫn nước từ cụm van lên lỗ khoan làm mát xi lanh và về.", "pipe", pipes_bb(CWH, 12), "hose",
    [("barrel_cw_valves", "đầu nối ren trên đỉnh cụm van", (298, 910, 1000)),
     ("barrel_b1", "khớp nối nhanh ở đáy", (200, 0, 940)),
     ("barrel_b2", "khớp nối nhanh góc dưới +Y", (876, 184, 1016)),
     ("barrel_b3", "khớp nối nhanh góc dưới +Y", (1890, 184, 1016)),
     ("barrel_b4", "khớp nối nhanh góc dưới +Y", (2904, 184, 1016)),
     ("barrel_b5", "khớp nối nhanh góc dưới +Y", (3918, 184, 1016)),
     ("barrel_b6", "khớp nối nhanh góc dưới +Y", (4932, 184, 1016))],
    "web-02 (ống mềm inox bọc lưới, đầu nối ở mặt bên dưới gần đầu đoạn); p05; vị trí theo review-01 I1",
    ["12 ống mềm inox bọc lưới DN15 (OD 24), mỗi đoạn 1 ống vào + 1 ống ra (đường đi trong paths_mm).",
     "Ống vào: từ đỉnh cụm van (X tâm − 40) chéo tới X = đầu đoạn + 200, xuyên tấm dưới của vỏ che ở Y 480, Z ≈ 990, rồi vào đầu nối 45° dưới +Y; ống ra đối xứng ở X = cuối đoạn − 200.",
     "B1: hai đầu nối ở đáy tại X 200 và 476; không ống nào đi dưới gối đỡ."],
    count=12, radius_mm=12, paths_mm=[lp(pa) for pa in CWH])
add("barrel_heater_jboxes", "barrel", "Hộp đấu dây nhiệt", "Heater junction boxes",
    "Đấu cáp băng nhiệt và cặp nhiệt của từng vùng vào cáp chính.", "box",
    bb(250, 5800, -700, -520, 700, 960), "stainless",
    [("barrel_cable_tray", "giá gá trên máng cáp", (338, -700, 740))],
    "web-01/02 (hộp đấu vuông dưới mỗi đoạn xi lanh)",
    ["7 hộp inox 180 × 120 × 200 có nắp kính nhỏ / ổ cắm công nghiệp, tại X = 338, 1 183, 2 197, 3 211, 4 225, 5 239, 5 700 (đầu xi lanh)."],
    count=7, item_mm=[180, 180, 260], positions_mm=[[x, -610, 830] for x in CW_X + [5700]])
add("barrel_cable_tray", "barrel", "Máng cáp nhiệt", "Heater cable tray",
    "Dẫn cáp nhiệt, cặp nhiệt, cảm biến dọc máy về tủ điện.", "sheet",
    bb(-1000, 5800, -1000, -700, 650, 750), "galv",
    [("base_frame_drive", "giá đỡ trên mặt khung", (-500, -850, 650)),
     ("base_frame_process", "giá đỡ trên mặt khung", (3000, -850, 650)),
     ("ctrl_cable_drop", "nối máng đứng", (-990, -1000, 700))],
    "web-01 (máng thép mạ kẽm đục lỗ dọc dưới xi lanh); phía −Y giả định",
    ["Máng đục lỗ mạ kẽm 300 × 100 có nắp, chạy X −1 000 … 5 800 trên mép −Y của khung."])

# =========================================================== FEED
add("feed_throat", "feed", "Hộp miệng nạp", "Feed throat housing",
    "Nối phễu với lỗ nạp B1, có áo nước làm mát chống dính hạt.", "box",
    bb(90, 590, -210, 210, 1455, 1640), "stainless",
    [("barrel_b1", "8 bulông M20 trên mặt gia công", (340, 0, 1460)),
     ("feed_hopper", "mặt bích vuông", (340, 0, 1640))],
    "giả định (miệng nạp 300 × 250 theo specs §2, nới thành 360 × 300 cho D 169)",
    ["Khối inox 500 × 420 × 185, lỗ trong 360 × 300, 2 đầu nối nước làm mát."])
hop_xz = [[160, 1640], [520, 1640], [590, 1900], [90, 1900]]
add("feed_hopper", "feed", "Phễu nạp có cổng nghiêng 45°", "Feed hopper with 45° inlet",
    "Gom hạt từ ống rơi xuống miệng nạp; cổng nghiêng 45° về phía hộp số.", "extrude",
    bb(90, 590, -250, 250, 1640, 1900), "stainless",
    [("feed_throat", "mặt bích vuông", (340, 0, 1640)),
     ("feed_flex_sleeve", "cổ nghiêng 45° Ø250", (200, 0, 1900))],
    "pdf_measures §2.2 (phễu nhỏ có ống nạp nghiêng 45° về phía dẫn động); p06",
    ["Phễu hình chóp ngược inox: đỉnh 500 × 500, đáy 360 × 300 (côn cả theo Y).",
     "Nắp đỉnh có cổ nghiêng 45° Ø250 hướng −X, cổng khí N₂ (inert) nhỏ, kính thăm và cảm biến mức."],
    outline_mm={"plane": "XZ", "pts": hop_xz, "d0": -250, "d1": 250})
SLV = [(200, 0, 1900), (90, 0, 2010)]
add("feed_flex_sleeve", "feed", "Ống mềm nối phễu", "Flexible sleeve",
    "Nối mềm ống rơi với phễu, cách rung và cho phép tháo nhanh.", "pipe", pipe_bb(SLV, 130), "white",
    [("feed_hopper", "đai kẹp", SLV[0]), ("feed_downpipe", "đai kẹp", SLV[1])],
    "giả định (ống mềm nối phổ biến dưới cân cấp liệu, thấy ở p01)",
    ["Ống bạt trắng Ø260 dài 155 với 2 đai kẹp inox."], path_mm=[list(p) for p in SLV], radius_mm=130)
DP = [(90, 0, 2010), (-450, 0, 2550), (-450, 0, 2850)]
add("feed_downpipe", "feed", "Ống rơi liệu chính", "Main feed down-pipe",
    "Dẫn hạt từ cân cấp liệu trên sàn thao tác xuống phễu.", "pipe", pipe_bb(DP, 125), "stainless",
    [("feed_flex_sleeve", "đai kẹp", DP[0]), ("feed_feeder_sleeves", "đai kẹp, ống mềm cách cân", DP[-1]),
     ("feed_additive_tube", "nhánh chữ Y", (-450, 125, 2700))],
    "giả định (bố trí sàn cân trên cao theo web-04); ống mềm cách cân theo review-01 M8",
    ["Ống inox Ø250: đoạn đứng từ Z 2 850 (dưới ống mềm cách cân) xuống Z 2 550, rồi nghiêng 45° xuống tới phễu; treo bằng giá dưới dầm sàn, vành chắn ở lỗ sàn không chạm ống.",
     "Nhánh Y cho ống phụ gia tại Z = 2 700, cửa thăm có nắp."], path_mm=[list(p) for p in DP], radius_mm=125)
add("feed_main_feeder", "feed", "Cân cấp liệu chính (loss-in-weight)", "Main loss-in-weight feeder (K-Tron BSP-150-S)",
    "Định lượng 3 500 kg/h hạt PET theo khối lượng hao hụt.", "composite",
    bb(-1000, 100, -450, 450, 3000, 3700), "stainless",
    [("feed_platform_deck", "khung 3 cảm biến cân bắt lên sàn", (-450, 0, 3000)),
     ("feed_main_hopper", "mặt bích + ống mềm cách cân", (-450, 0, 3700)),
     ("feed_feeder_sleeves", "cửa xả đáy, ống mềm cách cân", (-450, 0, 3000))],
    "c069 (K-Tron BSP-150-S, 34–6 700 dm³/h, 3 cảm biến cân); kích thước thân giả định",
    ["Thân bơm rắn BSP trên khung 3 cảm biến cân (load cells), động cơ hộp số phía −Y, hộp điều khiển KCM nhỏ phía +Y.",
     "Cửa xả đáy tại X = −450, Y = 0."])
add("feed_main_hopper", "feed", "Phễu cân chính", "Main feeder extension hopper",
    "Chứa hạt cho cân, ≈ 450 L (≈ 6 phút ở 3,5 t/h).", "revolve",
    cylz(3700, 4900, 450, -450, 0), "stainless",
    [("feed_main_feeder", "mặt bích", (-450, 0, 3700)), ("feed_vacuum_loader", "van nạp", (-450, 0, 4900))],
    "c069 (phễu nối thêm); dung tích giả định lớn hơn 320 dm³ để thời gian nạp lại hợp lý",
    ["Côn 400 + trụ Ø900 cao 800, kính thăm mức, cảm biến mức cao/thấp."], axis="Z", radius_mm=450,
    profile_mm=[[0, 0], [150, 0], [450, 400], [450, 1200], [0, 1200]])
add("feed_vacuum_loader", "feed", "Máy hút liệu chân không", "Vacuum loader / receiver",
    "Hút hạt từ silo và nạp lại phễu cân.", "revolve", cylz(4900, 5800, 320, -450, 0), "stainless",
    [("feed_main_hopper", "van lật xả", (-450, 0, 4900)),
     ("feed_conveying_line", "cổng vào liệu", (-450, 320, 5500))],
    "specs §2 (máy hút liệu trên phễu); cỡ giả định",
    ["Bình Ø640 cao 900 với nắp lọc, van lật đáy, cổng liệu vào bên +Y, cổng hút khí trên nắp."],
    axis="Z", radius_mm=320,
    profile_mm=[[0, 0], [100, 0], [320, 250], [320, 900], [0, 900]])
CVL = [(-450, 320, 5500), (-450, 700, 5500), (-450, 700, 6300)]
add("feed_conveying_line", "feed", "Ống hút liệu từ silo", "Pneumatic conveying line (stub)",
    "Ống vận chuyển hạt từ silo tới máy hút liệu (vẽ tới mép trên khung nhìn).", "pipe",
    pipe_bb(CVL, 40), "stainless",
    [("feed_vacuum_loader", "khớp nối nhanh", CVL[0])],
    "giả định", ["Ống inox DN80 (OD 80), đầu trên để hở ký hiệu 'tới silo'."],
    path_mm=[list(p) for p in CVL], radius_mm=40)
add("feed_additive_feeder", "feed", "Cân phụ gia / masterbatch", "Additive micro-feeder",
    "Định lượng phụ gia (masterbatch, chất chống dính) vào ống rơi chính.", "composite",
    bb(-1000, -300, 600, 1100, 3000, 4200), "stainless",
    [("feed_platform_deck", "khung cân bắt lên sàn", (-650, 850, 3000)),
     ("feed_feeder_sleeves", "cửa xả, ống mềm cách cân", (-650, 850, 3000))],
    "specs §2 (cân trục vít đôi nhỏ K-ML-D5-T35); giả định",
    ["Cân trục vít đôi 700 × 500 × 600 + phễu Ø500 cao 600 trên đỉnh."])
ADT = [(-650, 850, 2850), (-650, 850, 2700), (-450, 125, 2700)]
add("feed_additive_tube", "feed", "Ống phụ gia", "Additive feed tube",
    "Dẫn phụ gia vào nhánh Y của ống rơi chính.", "pipe", pipe_bb(ADT, 40), "stainless",
    [("feed_feeder_sleeves", "đai kẹp, ống mềm cách cân", ADT[0]), ("feed_downpipe", "nhánh Y", ADT[-1])],
    "giả định", ["Ống inox Ø80 bắt đầu dưới ống mềm cách cân (Z 2 850)."], path_mm=[list(p) for p in ADT], radius_mm=40)

add("feed_feeder_sleeves", "feed", "Ống mềm cách cân ở cửa xả", "Feeder outlet flexible sleeves",
    "Tách cửa xả của các cân loss-in-weight khỏi ống cứng để ống không tì lên cân, giữ độ chính xác định lượng.", "cyl",
    bb(-785, 1485, -135, 1085, 2850, 3000), "white",
    [("feed_main_feeder", "đai kẹp cửa xả", (-450, 0, 3000)), ("feed_downpipe", "đai kẹp", (-450, 0, 2850)),
     ("feed_additive_feeder", "đai kẹp cửa xả", (-650, 850, 3000)), ("feed_additive_tube", "đai kẹp", (-650, 850, 2850)),
     ("sidefeed_feeder", "đai kẹp cửa xả", (1350, 950, 3000)), ("sidefeed_downpipe", "đai kẹp", (1350, 950, 2850))],
    "review-01 M8; giả định (thực hành chuẩn cho cân loss-in-weight)",
    ["3 ống bạt trắng dài 150 (Z 2 850–3 000) nằm trong lỗ sàn: Ø270 tại (−450, 0), Ø100 tại (−650, 850), Ø170 tại (1 350, 950); mỗi ống 2 đai kẹp inox."],
    count=3, item_mm=[270, 270, 150], positions_mm=[[-450, 0, 2925], [-650, 850, 2925], [1350, 950, 2925]])

add("feed_platform_deck", "feed", "Sàn thao tác cân cấp liệu", "Feeder mezzanine deck",
    "Mặt bằng đặt các cân cấp liệu, lối đi bảo trì trên cao.", "frame",
    bb(-2700, 1850, -2700, 1400, 2780, 3000), "grating",
    [("feed_platform_columns_rear", "dầm bắt bulông lên đỉnh cột", (-450, -2600, 2780)),
     ("feed_platform_columns_front", "dầm bắt bulông lên đỉnh cột", (-450, 1300, 2780)),
     ("feed_platform_railing", "cột lan can bắt mép dầm", (0, 1400, 3000)),
     ("feed_stair", "chiếu nghỉ đầu cầu thang", (-2700, -2300, 3000)),
     ("feed_main_feeder", "đỡ cân", (-450, 0, 3000))],
    "web-04/05 (cân trên tầng lửng); specs §2 (mặt sàn 2 800–3 200); kích thước giả định",
    ["Dầm chính HEA180 (Z 2 780–2 960) + sàn lưới mạ kẽm 40 mm (Z 2 960–3 000).",
     "Lỗ sàn có vành chắn cho ống mềm cách cân của ống rơi chính (X −450, Y 0), ống phụ gia (X −650, Y 850), ống side feeder (X 1 350, Y 950); vành không chạm ống.",
     "Diện tích 4 550 × 4 100 (Y −2 700 … 1 400), phủ trên lantern, hộp số, B1, B2; mép sau lùi ra để lối đi phía −Y rộng ≥ 950.",
     "Bố trí dầm (beams_mm, tâm dầm Z 2 870): dầm biên HEA180 theo X trên hai hàng cột (Y −2 600 và 1 300); dầm chính HEA180 theo Y trên các đường cột X −2 600, −450, 1 750.",
     "Dầm chính X −450 bị ngắt tại Y ±260 quanh lỗ ống rơi chính (Ø270 + vành chắn); hai dầm viền (trimmer) HEA180 theo X ở Y ±260 từ X −760 tới −140 đỡ hai đầu dầm ngắt; đầu dầm viền tựa lên hai dầm phụ IPE160 theo Y tại X −760 và −140.",
     "Dầm phụ IPE160 theo Y tại X −1 900, −1 200, 300, 1 000 đỡ tấm lưới (khoảng ≤ 750); lỗ ống phụ gia (−650, 850) và ống side feeder (1 350, 950) nằm giữa các dầm phụ."],
    beams_mm=[
        {"id": "edge_rear", "section": "HEA180", "from": [-2700, -2600, 2870], "to": [1850, -2600, 2870]},
        {"id": "edge_front", "section": "HEA180", "from": [-2700, 1300, 2870], "to": [1850, 1300, 2870]},
        {"id": "main_x-2600", "section": "HEA180", "from": [-2600, -2600, 2870], "to": [-2600, 1300, 2870]},
        {"id": "main_x-450_rear", "section": "HEA180", "from": [-450, -2600, 2870], "to": [-450, -260, 2870]},
        {"id": "main_x-450_front", "section": "HEA180", "from": [-450, 260, 2870], "to": [-450, 1300, 2870]},
        {"id": "main_x1750", "section": "HEA180", "from": [1750, -2600, 2870], "to": [1750, 1300, 2870]},
        {"id": "trimmer_y-260", "section": "HEA180", "from": [-760, -260, 2870], "to": [-140, -260, 2870]},
        {"id": "trimmer_y+260", "section": "HEA180", "from": [-760, 260, 2870], "to": [-140, 260, 2870]},
        {"id": "sec_x-760", "section": "IPE160", "from": [-760, -2600, 2880], "to": [-760, 1300, 2880]},
        {"id": "sec_x-140", "section": "IPE160", "from": [-140, -2600, 2880], "to": [-140, 1300, 2880]},
        {"id": "sec_x-1900", "section": "IPE160", "from": [-1900, -2600, 2880], "to": [-1900, 1300, 2880]},
        {"id": "sec_x-1200", "section": "IPE160", "from": [-1200, -2600, 2880], "to": [-1200, 1300, 2880]},
        {"id": "sec_x300", "section": "IPE160", "from": [300, -2600, 2880], "to": [300, 1300, 2880]},
        {"id": "sec_x1000", "section": "IPE160", "from": [1000, -2600, 2880], "to": [1000, 1300, 2880]}])
for side, yc in (("rear", -2600), ("front", 1300)):
    add(f"feed_platform_columns_{side}", "feed", f"Cột sàn thao tác ({'phía sau −Y' if side == 'rear' else 'phía vận hành +Y'})",
        f"Mezzanine columns, {side} row", "Đỡ sàn thao tác xuống nền.", "frame",
        bb(-2700, 1850, yc - 100, yc + 100, 0, 2780), "grating",
        [("feed_platform_deck", "đỉnh cột bắt dầm", (-450, yc, 2780)),
         ("ctx_floor", "tấm đế + bulông neo", (-450, yc, 0))],
        "giả định", [f"3 cột HEB200 tại X = −2 600, −450, 1 750; Y = {yc}; tấm đế 400 × 400, giằng góc dưới dầm."],
        count=3, item_mm=[200, 200, 2780], positions_mm=[[x, yc, 1390] for x in (-2600, -450, 1750)])
rail_xy = [[-2700, -1950], [-2700, 1400], [1850, 1400], [1850, -2700], [-2700, -2700], [-2700, -2650]]
add("feed_platform_railing", "feed", "Lan can sàn thao tác", "Mezzanine railing with kick plates",
    "Chống ngã từ sàn cao 3 m.", "frame", bb(-2700, 1850, -2700, 1400, 3000, 4100), "yellow",
    [("feed_platform_deck", "cột lan can bắt mép dầm", (0, 1400, 3000)),
     ("ctrl_estop_platform", "hộp dừng khẩn trên cột lan can", (-450, 1390, 4000))],
    "web-04/05 (lan can và tấm chắn chân màu vàng)",
    ["Tay vịn ống Ø42 cao 1 100, thanh giữa 550, tấm chắn chân 150, cột bước ≤ 1 500, màu vàng an toàn.",
     "Chừa lối lên cầu thang ở mép −X đoạn Y −2 650 … −1 950."],
    outline_mm={"plane": "XY", "pts": rail_xy, "d0": 3000, "d1": 4100, "closed": False})
add("feed_stair", "feed", "Cầu thang lên sàn", "Mezzanine stair",
    "Lối lên sàn cân cấp liệu (45°).", "frame", bb(-5700, -2700, -2650, -1950, 0, 4000), "yellow",
    [("feed_platform_deck", "chiếu nghỉ trên bắt vào dầm sàn", (-2700, -2300, 3000)),
     ("ctx_floor", "chân thang bắt bulông neo", (-5700, -2300, 0))],
    "web-04 (cầu thang vàng cạnh máy); vị trí phía −Y, lùi ra theo review-01 I2 (lối đi 950 dọc khung, 850 trước ống cáp trung thế)",
    ["Rộng 700, 45°, 15 bậc lưới cao 200, hai dầm thang (stringers) thép mạ kẽm, tay vịn vàng hai bên cao 1 000.",
     "Outline XZ là hình bao bên: mép dưới dầm thang từ (−5 400, 0) tới (−2 700, 2 700), tay vịn từ (−5 700, 1 000) tới (−2 700, 4 000)."],
    outline_mm={"plane": "XZ", "pts": [[-5700, 0], [-5400, 0], [-2700, 2700], [-2700, 4000], [-5700, 1000]],
                "d0": -2650, "d1": -1950})
add("feed_control_cabinet", "feed", "Tủ điều khiển cân cấp liệu", "Feeder control cabinet",
    "Bộ điều khiển các cân (KCM), cấp nguồn máy hút liệu.", "box",
    bb(-2400, -1800, 1050, 1350, 3000, 4400), "cabinet",
    [("feed_platform_deck", "chân tủ bắt lên sàn", (-2100, 1200, 3000))],
    "giả định", ["Tủ 600 × 300 × 1 400 RAL 7035 có màn hình nhỏ ở cửa."])

add("sidefeed_adapter", "feed", "Bích cửa bên B2", "Side-feeder adapter plate",
    "Nối thân side feeder vào cửa bên +Y của B2.", "box",
    bb(1165, 1535, 250, 330, 1040, 1360), "steel",
    [("barrel_b2", "8 bulông M24 quanh cửa bên", (1350, 260, 1200)),
     ("sidefeed_barrel", "8 bulông M24", (1350, 330, 1200))],
    "p08_side_feeder (mặt bích bắt bulông vào hông xi lanh)", ["Tấm thép 370 × 80 × 320 lỗ hình số 8."])
add("sidefeed_barrel", "feed", "Thân side feeder trục vít đôi (ZSB)", "Twin-screw side feeder barrel (ZSB, size assumed)",
    "Ép liệu phụ (mảnh vụn biên tấm, phụ gia bột) vào cửa bên B2.", "box",
    bb(1185, 1515, 330, 1100, 1070, 1330), "steel",
    [("sidefeed_adapter", "mặt bích", (1350, 330, 1200)),
     ("sidefeed_gearbox", "mặt bích + khớp then", (1350, 1100, 1200)),
     ("sidefeed_hopper", "lỗ nạp đỉnh", (1350, 950, 1330))],
    "p08_side_feeder, p06 cutaway (side feeder 2 trục vít ngang vào hông xi lanh); c024 (ZE 110 dùng ZSFE 120) → cỡ 160 giả định",
    ["Thân hình số 8 ngang 330 × 260 dài 770 theo Y: hai cung tròn R130 tâm X 1 315 và 1 385 (outline_mm), eo nhỏ trên và dưới tại X 1 350; 2 lỗ trục vít Ø112 tâm X 1 305 và 1 395, trục theo Y tại Z = 1 200.",
     "Lỗ nạp đỉnh gần đầu ngoài, áo nước làm mát, bích hai đầu."], axis="Y",
    outline_mm={"plane": "XZ", "d0": 330, "d1": 1100,
                "pts": arc(130, -105.6, 105.6, 14, cy=1385) + arc(130, 74.4, 285.6, 14, cy=1315)})
add("sidefeed_hopper", "feed", "Phễu side feeder", "Side-feeder inlet hopper",
    "Nhận liệu từ cân phụ.", "box", bb(1200, 1500, 820, 1080, 1330, 1600), "stainless",
    [("sidefeed_barrel", "mặt bích", (1350, 950, 1330)), ("sidefeed_downpipe", "cổ ống", (1350, 950, 1600))],
    "p08_side_feeder", ["Phễu inox 300 × 260 cao 270, kính thăm."])
add("sidefeed_gearbox", "feed", "Hộp số side feeder", "Side-feeder gearbox",
    "Giảm tốc và chia mômen ra 2 trục vít side feeder.", "box",
    bb(1175, 1525, 1100, 1450, 1000, 1400), "km_blue",
    [("sidefeed_barrel", "mặt bích", (1350, 1100, 1200)), ("sidefeed_motor", "mặt bích động cơ", (1350, 1450, 1200)),
     ("sidefeed_cart", "chân hộp số bắt lên xe", (1350, 1300, 1000))],
    "p06 cutaway (hộp số + động cơ xám nhỏ trên xe đẩy); màu giả định",
    ["Hộp 350 × 350 × 400, nút thăm dầu."])
add("sidefeed_motor", "feed", "Động cơ side feeder 22 kW", "Side-feeder motor 22 kW",
    "Quay trục vít side feeder.", "cyl", bb(1170, 1530, 1450, 2050, 1000, 1380), "motor",
    [("sidefeed_gearbox", "mặt bích B5", (1350, 1450, 1200)), ("sidefeed_cart", "chân đỡ", (1350, 1750, 1000))],
    "giả định (động cơ AC 22 kW biến tần)", ["Động cơ nằm Ø360 dài 600, nắp quạt, hộp đấu dây trên nóc."],
    axis="Y", radius_mm=180)
add("sidefeed_cart", "feed", "Xe đỡ side feeder", "Side-feeder wheeled cart",
    "Đỡ hộp số + động cơ, cho phép kéo side feeder ra theo +Y khi bảo trì.", "frame",
    bb(1100, 1600, 1010, 2100, 0, 1000), "frame",
    [("sidefeed_gearbox", "tấm đỉnh", (1350, 1300, 1000)), ("sidefeed_motor", "tấm đỉnh", (1350, 1750, 1000)),
     ("ctx_floor", "4 bánh xe khoá", (1350, 1500, 0))],
    "p06_cutaway_side_feeder_cart (xe thép trắng có bánh xe)",
    ["Khung thép trắng 500 × 1 090 cao 1 000, 4 bánh xe có khoá, tem cảnh báo điện."])
SFD = [(1350, 950, 2850), (1350, 950, 1600)]
add("sidefeed_downpipe", "feed", "Ống rơi side feeder", "Side-feeder down-pipe",
    "Dẫn liệu phụ từ cân trên sàn xuống phễu side feeder.", "pipe", pipe_bb(SFD, 75), "stainless",
    [("feed_feeder_sleeves", "đai kẹp, ống mềm cách cân", SFD[0]), ("sidefeed_hopper", "cổ ống", SFD[1])],
    "giả định", ["Ống inox Ø150 có đoạn ống mềm ở đáy."], path_mm=[list(p) for p in SFD], radius_mm=75)
add("sidefeed_feeder", "feed", "Cân cấp liệu side feeder", "Side-feeder loss-in-weight feeder",
    "Định lượng liệu phụ cho side feeder.", "composite", bb(1000, 1700, 650, 1250, 3000, 3550), "stainless",
    [("feed_platform_deck", "khung cân", (1350, 950, 3000)), ("feed_feeder_sleeves", "cửa xả, ống mềm cách cân", (1350, 950, 3000)),
     ("sidefeed_feeder_hopper", "mặt bích", (1350, 950, 3550))],
    "giả định (cân trục vít đôi cỡ K-ML-D5-T35)", ["Cân trục vít đôi trên 3 cảm biến cân, động cơ phía −X."])
add("sidefeed_feeder_hopper", "feed", "Phễu cân side feeder", "Side-feeder feeder hopper",
    "Chứa liệu phụ.", "revolve", cylz(3550, 4250, 300, 1350, 950), "stainless",
    [("sidefeed_feeder", "mặt bích", (1350, 950, 3550))], "giả định", ["Phễu Ø600 cao 700 có nắp."],
    axis="Z", radius_mm=300, profile_mm=[[0, 0], [100, 0], [300, 250], [300, 700], [0, 700]])

# =========================================================== VACUUM
# Deep vacuum (zone 2, B5): dome lid -> valve -> elbow + bellows -> DN150 at Z 2300 -> separator top.
# First vacuum (zone 1, B3): dome_2 -> valve_2 -> bellows_2 -> DN100 rising to Z 2250 -> separator side inlet.
SEP_X, SEP_Y = 4120, -2700
add("vac_valve", "vacuum", "Van chặn chân không DN150 (vùng 2)", "Vacuum shut-off valve DN150 (zone 2)",
    "Cách ly vòm B5 với đường hút khi mở vòm hoặc khởi động.", "composite",
    bb(4020, 4220, -300, 110, 2150, 2260), "stainless",
    [("barrel_vent_dome", "mặt bích DN150 trên nắp vòm", (4120, 0, 2150)),
     ("vac_bellows", "mặt bích DN150", (4120, 0, 2260))],
    "giả định (van bướm có bộ tác động khí nén); đặt đứng trên nắp vòm theo review-01 M4",
    ["Van bướm DN150 đặt đứng trên nắp vòm (Z 2 150–2 260), bộ tác động khí nén vuông nằm ngang phía −Y (Y −300 … −110).",
     "Ống khí Ø12 tới bộ tác động (util_air_tube_vac)."])
add("vac_bellows", "vacuum", "Cút + khớp giãn nở chân không", "Vacuum elbow with bellows",
    "Đổi hướng từ đứng sang ngang và hấp thụ giãn nở nhiệt, rung giữa vòm và ống.", "composite",
    bb(4010, 4230, -340, 110, 2190, 2410), "stainless",
    [("vac_valve", "mặt bích", (4120, 0, 2260)), ("vac_pipe", "mặt bích", (4120, -340, 2300))],
    "p01 (ống mềm inox gợn sóng)",
    ["Cút 90° DN150 từ đỉnh van (Z 2 260) lên tâm Z 2 300 rồi quay về −Y; ống xếp inox DN150 dài 200 (Y −120 … −320), 2 bích."],
    axis="Y", radius_mm=110)
VP = [(4120, -340, 2300), (SEP_X, SEP_Y, 2300), (SEP_X, SEP_Y, 1900)]
add("vac_pipe", "vacuum", "Ống hút chân không DN150 (vùng 2)", "Vacuum line DN150 (zone 2)",
    "Dẫn hơi và khí từ vòm B5 tới bình tách ngưng.", "pipe", pipe_bb(VP, 84), "stainless",
    [("vac_bellows", "mặt bích", VP[0]), ("vac_separator", "mặt bích nắp", VP[-1]),
     ("vac_pipe_support", "đai ôm", (4120, -1900, 2216))],
    "giả định (DN150 theo specs §3); cao độ theo review-01 M4",
    ["Ống inox DN150 (OD 168) đi ngang theo −Y ở tâm Z 2 300 (đáy ống Z 2 216, trên lối đi 2 100), xuống bình tách tại Y −2 700."],
    path_mm=lp(VP), radius_mm=84)
add("vac_pipe_support", "vacuum", "Cột đỡ ống chân không", "Vacuum pipe support post",
    "Đỡ đoạn ống ngang DN150.", "frame", bb(4070, 4170, -1950, -1850, 0, 2216), "frame",
    [("vac_pipe", "đai ôm", (4120, -1900, 2216)), ("ctx_floor", "tấm đế", (4120, -1900, 0))],
    "giả định", ["Ống thép Ø100 có tấm đế và đai ôm trên đỉnh, tại Y −1 900 (ngoài lối đi dọc khung)."])
add("vac_gauge_dome", "vacuum", "Đồng hồ chân không trên vòm B5", "Vacuum gauge on dome (zone 2)",
    "Hiển thị mức chân không tại vòm cho người vận hành.", "cyl",
    bb(4280, 4340, -30, 30, 2150, 2300), "black",
    [("barrel_vent_dome", "ren trên nắp", (4310, 0, 2150))], "p01 (đồng hồ trên đường chân không); giả định",
    ["Đồng hồ Ø100 mặt hướng +Y + cảm biến áp suất tuyệt đối (truyền tín hiệu)."])
add("vac_valve_2", "vacuum", "Van chặn chân không DN100 (vùng 1)", "Vacuum shut-off valve DN100 (zone 1)",
    "Cách ly vòm B3 với đường hút.", "composite", bb(2085, 2215, -320, -240, 1735, 1865), "stainless",
    [("barrel_vent_dome_2", "bích DN100", (2150, -240, 1800)), ("vac_bellows_2", "bích DN100", (2150, -320, 1800))],
    "review-01 I4; giả định", ["Van bi DN100 tay gạt đỏ."])
add("vac_bellows_2", "vacuum", "Khớp giãn nở chân không DN100", "Vacuum bellows DN100 (zone 1)",
    "Hấp thụ giãn nở nhiệt giữa vòm B3 và ống.", "cyl", cyly(-480, -320, 75, 2150, 1800), "stainless",
    [("vac_valve_2", "bích", (2150, -320, 1800)), ("vac_pipe_3", "bích", (2150, -480, 1800))],
    "review-01 I4; giả định", ["Ống xếp inox DN100 dài 160."], axis="Y", radius_mm=75)
VP3 = [(2150, -480, 1800), (2150, -560, 1800), (2150, -560, 2250), (2150, SEP_Y, 2250), (3700, SEP_Y, 2250),
       (3700, SEP_Y, 1400), (3820, SEP_Y, 1400)]
add("vac_pipe_3", "vacuum", "Ống hút chân không DN100 (vùng 1)", "Vacuum line DN100 (zone 1)",
    "Dẫn hơi nước từ vòm B3 tới cổng bên của bình tách ngưng.", "pipe", pipe_bb(VP3, 57), "stainless",
    [("vac_bellows_2", "bích", VP3[0]), ("vac_separator", "cổng vào bên −X", VP3[-1]),
     ("vac_reg_valve_2", "bích", (3700, SEP_Y, 1650))],
    "review-01 I4; giả định",
    ["Ống inox DN100 (OD 114): lên đứng ngoài vỏ che tại Y −560 tới Z 2 250, đi ngang về −Y tới Y −2 700, theo +X tới X 3 700, xuống tới Z 1 400 rồi vào bình tách."],
    path_mm=lp(VP3), radius_mm=57)
add("vac_reg_valve_2", "vacuum", "Van tiết lưu chân không vùng 1", "Zone-1 vacuum regulating valve",
    "Tiết lưu để vùng 1 giữ ≈ 50 mbar trong khi vùng 2 vẫn đạt 5–20 mbar trên cùng cụm bơm.", "composite",
    bb(3630, 3790, -2780, -2620, 1580, 1720), "stainless",
    [("vac_pipe_3", "bích DN100", (3700, SEP_Y, 1650))], "review-01 I4; giả định",
    ["Van tiết lưu tay quay DN100 trên đoạn ống đứng, tay quay hướng +Y ở cao 1,65 m; đồng hồ chân không nhỏ bên cạnh."])
add("vac_gauge_dome_2", "vacuum", "Đồng hồ chân không trên vòm B3", "Vacuum gauge on dome (zone 1)",
    "Hiển thị mức chân không vùng 1.", "cyl", bb(2250, 2310, -30, 30, 1960, 2110), "black",
    [("barrel_vent_dome_2", "ren trên nắp", (2280, 0, 1960))], "review-01 I4; giả định",
    ["Đồng hồ Ø100 mặt hướng +Y + cảm biến áp suất."])
add("vac_separator", "vacuum", "Bình tách ngưng", "Condensate separator / knock-out vessel",
    "Ngưng và gom hơi nước, oligome, bụi của cả hai vùng chân không trước bơm.", "revolve",
    bb(3820, 4420, -3000, -2400, 0, 1900), "stainless",
    [("vac_pipe", "mặt bích nắp (vùng 2)", (SEP_X, SEP_Y, 1900)), ("vac_pipe_3", "cổng vào bên −X (vùng 1)", (3820, SEP_Y, 1400)),
     ("vac_pipe_2", "cổng ra bên +X", (4420, SEP_Y, 1600)), ("vac_drain", "van trên của nồi xả", (SEP_X, SEP_Y, 450)),
     ("util_cw_vac_hoses", "cổng nước ống xoắn", (4420, -2600, 1000)), ("ctx_floor", "3 chân", (SEP_X, SEP_Y, 0))],
    "c060 (Busch PLASTEX: bình lọc đứng trước bơm), web-15; c063 (buồng ngưng có làm mát)",
    ["Bình đứng Ø600 cao 1 450 (Z 450–1 900) trên 3 chân cao 450 (nâng 150 để đặt nồi xả), nắp bích bắt bulông, ống xoắn làm mát bên trong (nước 10–15 °C), kính thăm mức, đồng hồ chân không.",
     "Cổng: nắp (vùng 2, DN150), bên −X ở Z 1 400 (vùng 1, DN100), ra bên +X ở Z 1 600 (DN150), 2 cổng nước bên +X ở Z 1 000 và 1 100."],
    axis="Z", radius_mm=300,
    profile_mm=[[0, 450], [260, 450], [300, 530], [300, 1770], [220, 1870], [0, 1900]])
add("vac_drain", "vacuum", "Nồi xả ngưng kiểu khoá (lock pot)", "Condensate lock pot",
    "Xả nước ngưng khi máy đang chạy mà không phá chân không.", "composite",
    bb(3970, 4270, -2850, -2550, 0, 450), "stainless",
    [("vac_separator", "van trên (thường mở)", (SEP_X, SEP_Y, 450)), ("ctx_floor", "3 chân ngắn", (SEP_X, SEP_Y, 0))],
    "review-01 M5; web-15 (van xả đáy tay đỏ)",
    ["Nồi Ø300 cao 350 (Z 50–400) trên 3 chân ngắn, nằm giữa 3 chân bình tách.",
     "Van trên (thường mở) ở Z 400–450, van thông hơi trên nắp nồi, van xả đáy; 3 tay van màu đỏ.",
     "Xả: đóng van trên, mở thông hơi, mở van xả; xong đóng lại rồi mở van trên."])
VP2 = [(4420, SEP_Y, 1600), (4860, SEP_Y, 1600), (4860, SEP_Y, 1500)]   # DN150 (review M1)
add("vac_pipe_2", "vacuum", "Ống chân không tới bơm", "Vacuum line to pump",
    "Dẫn khí sau tách ngưng tới bơm Roots.", "pipe", pipe_bb(VP2, 84), "stainless",
    [("vac_separator", "cổng ra", VP2[0]), ("vac_pump_unit", "cổng hút bơm Roots", VP2[-1]),
     ("vac_bleed_valve", "măng sông", (4640, SEP_Y, 1684))],
    "giả định; nâng lên DN150 theo drawing review-01 M1", ["Ống inox DN150 (OD 168), bằng cỡ bích hút của bơm Roots; vận tốc ≈ 30 m/s ở 2 000 m³/h."],
    path_mm=lp(VP2), radius_mm=84)
add("vac_bleed_valve", "vacuum", "Van điều chỉnh / xả chân không", "Vacuum bleed valve",
    "Chỉnh mức chân không chung và phá chân không trước khi mở vòm.", "composite",
    bb(4600, 4680, -2740, -2660, 1680, 1825), "stainless",
    [("vac_pipe_2", "măng sông ren", (4640, SEP_Y, 1684))], "giả định",
    ["Van kim + van bi nhỏ tay đỏ trên đỉnh ống ra, cao ≈ 1,7 m để thao tác từ sàn."])
add("vac_pump_unit", "vacuum", "Cụm bơm chân không", "Vacuum pump unit (Roots + dry backing pump)",
    "Tạo chân không 5–20 mbar cho vòm B5 và ≈ 50 mbar (qua van tiết lưu) cho vòm B3.", "composite",
    bb(4500, 6300, -3300, -2200, 0, 1500), "black",
    [("vac_pipe_2", "cổng hút", (4860, SEP_Y, 1500)), ("vac_exhaust", "cổng xả", (6150, -3100, 1500)),
     ("vac_control_box", "bắt lên khung skid", (6100, -2200, 1000)), ("ctx_floor", "khung skid", (5400, -2750, 0)),
     ("util_cw_vac_hoses", "ống góp nước của skid", (4500, -2350, 400))],
    "c059/c060 (Busch MINK, PLASTEX), c062 (PET không sấy dùng Roots hai cấp); cỡ giả định (design.md §7)",
    ["Khung skid thép đen 1 800 × 1 100: bơm Roots ≈ 2 000 m³/h trên bơm trục vít khô ≈ 400 m³/h làm mát bằng nước, động cơ, giảm thanh.",
     "Vỏ bơm đen/cam như web-15; ống góp nước vào/ra ở mặt −X, Z 400."])
add("vac_control_box", "vacuum", "Hộp điều khiển cụm chân không", "Vacuum unit control box",
    "Khởi động bơm, đo áp, khoá liên động.", "box", bb(5900, 6300, -2200, -2000, 700, 1500), "cabinet",
    [("vac_pump_unit", "bắt lên khung skid", (6100, -2200, 1000))], "web-15 (hộp điều khiển xám có công tắc chính đỏ-vàng)",
    ["Hộp 400 × 200 × 800, công tắc chính đỏ-vàng, đèn báo; mặt hướng +Y ra lối đi."])
VEX = [(6150, -3100, 1500), (6150, -3100, 3500)]
add("vac_exhaust", "vacuum", "Ống xả bơm chân không", "Vacuum pump exhaust",
    "Xả khí sau bơm ra ngoài nhà xưởng.", "pipe", pipe_bb(VEX, 60), "galv",
    [("vac_pump_unit", "mặt bích", VEX[0])], "giả định", ["Ống DN100 đứng có bình giảm thanh, đầu trên để hở 'ra ngoài'."],
    path_mm=lp(VEX), radius_mm=60)

# =========================================================== MELT LINE
add("melt_head_adapter", "melt", "Đầu xi lanh / bích chuyển", "Barrel head adapter (figure-8 to round)",
    "Chuyển dòng từ lỗ số 8 sang lỗ tròn Ø120, nối van khởi động.", "revolve", cylx(5746, 5996, R_FL), "steel",
    [("barrel_b6", "20 bulông cấy M24 trên PCD 560", (5746, 0, 1200)),
     ("melt_startup_valve", "12 vít M24 lục giác chìm từ phía van vào lỗ ren của bích ra", (5996, 0, 1200)),
     ("melt_sensor_head", "2 lỗ ren 1/2\"-20UNF", (5896, 0, 1420)),
     ("melt_rupture_disc", "lỗ ren bên −Y", (5896, -215, 1200)),
     ("barrel_cover_c1", "xuyên qua tấm đầu vỏ che", (5753, 0, 1480)),
     ("melt_heater_conduits", "hộp đấu băng nhiệt", (5836, -245, 1100))],
    "pdf_measures §4 ghi chú 4 (mặt bích tròn bắt bulông ở đầu ra, dựng adapter đồng trục); specs §4 (≈ 250 mm); bulông theo review-01 M1",
    ["Bích Ø640 × 60 nhận 20 bulông cấy M24 trên PCD 560 từ B6 (đai ốc phía B6), thân côn Ø520 → Ø400, bích ra Ø420 × 50 có 12 lỗ ren M24 (vít bắt từ phía van, không có đai ốc sau bích nên không chạm thân côn); 2 băng nhiệt."], axis="X", radius_mm=R_FL,
    length_mm=250, profile_mm=[[0, 0], [R_FL, 0], [R_FL, 60], [260, 60], [200, 200], [210, 200], [210, 250], [0, 250]])
add("melt_rupture_disc", "melt", "Đĩa nổ an toàn", "Rupture disc",
    "Xả áp khi áp suất đầu xi lanh vượt giới hạn (bảo vệ quá áp).", "cyl",
    bb(5876, 5916, -330, -210, 1180, 1220), "steel",
    [("melt_head_adapter", "ren 1/2\"-20UNF", (5896, -215, 1200))], "giả định (thiết bị an toàn tiêu chuẩn của máy đùn)",
    ["Đầu đĩa nổ Ø40 có nắp chụp hướng xuống, đặt phía −Y."], axis="Y", radius_mm=20)
add("melt_sensor_head", "melt", "Cảm biến áp suất + nhiệt nhựa đầu xi lanh (P1, T1)", "Head melt pressure + temperature (P1, T1)",
    "Đo áp và nhiệt nhựa ra khỏi trục vít; P1 dùng cho khoá quá áp.", "cyl",
    bb(5856, 5936, -20, 20, 1414, 1700), "stainless",
    [("melt_head_adapter", "ren 1/2\"-20UNF", (5896, 0, 1420))], "p01 (cảm biến áp suất có cáp trên đầu ra); giả định",
    ["2 thân cảm biến Ø25 có cổ mềm, đầu điện tử Ø40 cao tới Z 1 700, X = 5 876 và 5 916 (băng nhiệt X 5 906 có khe tại hai lỗ)."],
    count=2, item_mm=[40, 40, 285], positions_mm=[[5876, 0, 1557], [5916, 0, 1557]])
add("melt_startup_valve", "melt", "Van khởi động / chuyển hướng", "Start-up (diverter) valve",
    "Khi khởi động xả nhựa xuống máng; khi chạy cho nhựa đi tiếp vào bộ lọc.", "box",
    bb(5996, 6446, -260, 260, 940, 1460), "steel",
    [("melt_head_adapter", "12 vít M24 lục giác chìm qua lỗ khoét bậc trên thân van", (5996, 0, 1200)),
     ("melt_sc_adapter_in", "12 vít M24 lục giác chìm qua lỗ khoét bậc trên thân van", (6446, 0, 1200)),
     ("melt_startup_cyl", "chạc nối cần piston", (6221, -260, 1200)), ("melt_drain_chute", "cổng xả đáy", (6221, 0, 940)),
     ("melt_valve_support", "2 đệm PTFE dưới đáy", (6040, 205, 940)),
     ("melt_heater_conduits", "hộp đấu thanh nhiệt", (6380, -260, 980))],
    "c035 (diverter valve trong sơ đồ catalogue); kích thước theo specs §4 (giả định)",
    ["Khối thép 450 × 520 × 520 có thanh nhiệt cắm, tấm cách nhiệt, cổng xả đáy, chốt xoay (rotary bolt) theo Y.",
     "Hai mặt bích là mặt phẳng của khối van có 12 lỗ khoét bậc (counterbore) cho vít M24 bắt vào bích kề; đáy tì lên giá đỡ PTFE."])
add("melt_startup_cyl", "melt", "Xi lanh thuỷ lực van khởi động", "Diverter valve hydraulic cylinder",
    "Xoay chốt van giữa vị trí xả và vị trí chạy.", "cyl", cyly(-860, -260, 80, 6221, 1200), "steel",
    [("melt_startup_valve", "chạc nối", (6221, -260, 1200)), ("melt_hyd_hoses_suv", "cổng thuỷ lực", (6221, -860, 1170))],
    "specs §4 (xi lanh thuỷ lực nằm ngang); giả định phía −Y", ["Xi lanh Ø160 dài 600 nằm theo Y, 2 công tắc hành trình."],
    axis="Y", radius_mm=80)
add("melt_drain_chute", "melt", "Máng xả nhựa khởi động", "Start-up drain chute",
    "Dẫn nhựa xả khi khởi động xuống xe hứng.", "box", bb(6096, 6346, -125, 125, 520, 940), "stainless",
    [("melt_startup_valve", "bích cổng xả", (6221, 0, 940)), ("melt_purge_cart", "miệng xe", (6221, 0, 520))],
    "giả định", ["Máng inox 250 × 250, có tấm chắn bắn."])
add("melt_purge_cart", "melt", "Xe hứng nhựa xả", "Purge cart",
    "Hứng cục nhựa xả khi khởi động/đổi màu.", "box", bb(5980, 6500, -400, 400, 0, 520), "steel",
    [("melt_drain_chute", "miệng xe", (6221, 0, 520)), ("ctx_floor", "4 bánh xe", (6240, 0, 0))],
    "giả định", ["Thùng thép 520 × 800 × 450 trên 4 bánh xe, tay kéo phía −Y."])
add("melt_sc_adapter_in", "melt", "Bích chuyển vào bộ lọc (P2)", "Screen changer inlet adapter",
    "Nối van khởi động với bộ lọc; mang cảm biến áp P2 trước lưới.", "revolve", cylx(6446, 6596, 210), "steel",
    [("melt_startup_valve", "12 vít M24 từ phía van", (6446, 0, 1200)), ("melt_screen_changer", "8 bulông", (6596, 0, 1200)),
     ("melt_sensor_p2", "lỗ ren", (6521, 0, 1410))], "giả định",
    ["Ống bích Ø420 dài 150, 1 băng nhiệt."], axis="X", radius_mm=210, length_mm=150,
    profile_mm=prof_flanged(150, 210, 180, 30))
add("melt_sensor_p2", "melt", "Cảm biến áp suất trước lọc (P2)", "Pressure transducer before screen changer (P2)",
    "Đo áp trước lưới để điều khiển xả ngược / đổi lưới.", "cyl", bb(6491, 6551, -30, 30, 1405, 1650), "stainless",
    [("melt_sc_adapter_in", "ren 1/2\"-20UNF", (6521, 0, 1410))], "giả định", ["Thân Ø25, đầu Ø40."])
sc_yz = [[-520, 650], [520, 650], [520, 1880], [420, 2079], [-380, 1820], [-520, 1820]]
add("melt_screen_changer", "melt", "Bộ lọc lưới quay xả ngược", "Backflush screen changer (Gneuss RSFgenius 200)",
    "Lọc tạp chất khỏi nhựa (lưới 60 µm, 970 cm²) liên tục, tự làm sạch bằng xả ngược.", "extrude",
    bb(6596, 7301, -520, 520, 650, 2079), "stainless",
    [("melt_stand_sc", "4 bulông", (6950, 0, 650)), ("melt_sc_adapter_in", "bích vào", (6596, 0, 1200)),
     ("melt_pump_adapter_in", "bích ra", (7301, 0, 1200)), ("melt_sc_drive", "trục quay đĩa lưới", (6950, -520, 1175)),
     ("melt_sc_backflush", "bắt mặt +Y", (6950, 520, 1250)),
     ("melt_heater_conduits", "hộp đầu nối nhiệt 6 vùng mặt −Y", (6700, -520, 980))],
    "c050 (RSFgenius 200: A 1 955 / B 705 / C 1 429 / D 550 / E 1 040, 3 800 kg, 39 kW 6 vùng, 200 bar); web-13; c043; cách hiểu B = dày theo dòng chảy, D = cao tâm nhựa trên đáy, E = rộng thân là giả định",
    ["Thân hộp inox rộng 1 040 (Y), dày 705 (X), mũ nghiêng có khe thông gió lên tới Z 2 079, logo đỏ Gneuss trên mũ.",
     "Bích vào/ra tròn 8 bulông ở giữa mặt trước/sau, tại Z = 1 200.",
     "Tấm hông phẳng phải, hộp đầu nối nhiệt 6 vùng."],
    outline_mm={"plane": "YZ", "pts": sc_yz, "d0": 6596, "d1": 7301})
add("melt_sc_drive", "melt", "Tay quay thuỷ lực bộ lọc", "Screen changer hydraulic drive arm",
    "Xoay đĩa lưới từng bước bằng xi lanh thuỷ lực.", "composite",
    bb(6750, 7150, -1085, -520, 1000, 1350), "stainless",
    [("melt_screen_changer", "trục đĩa lưới", (6950, -520, 1175)), ("melt_hyd_hoses_sc", "cổng thuỷ lực", (6860, -1085, 1150))],
    "web-13 (tay quay + xi lanh nhô một bên); A − E = 1 955 − 1 040 chia hai bên (giả định)",
    ["Tay đòn + xi lanh Ø100 nằm theo Y, nhô 565 mm phía −Y."])
add("melt_sc_backflush", "melt", "Cụm xả ngược + cửa thay lưới", "Backflush unit and screen access hatch",
    "Đẩy nhựa sạch ngược qua lưới để làm sạch, xả ra máng; cửa thay lưới.", "composite",
    bb(6700, 7200, 520, 870, 1050, 1450), "stainless",
    [("melt_screen_changer", "bắt mặt +Y", (6950, 520, 1250))], "web-13 (khối nhọn + cửa thăm lưới bên trái)",
    ["Khối mũi nhọn 500 × 350 có piston xả ngược, cửa bản lề thay lưới, máng xả nhỏ hướng xuống."])
add("melt_hpu", "melt", "Bộ nguồn thuỷ lực", "Hydraulic power unit",
    "Cấp dầu thuỷ lực cho xi lanh bộ lọc và van khởi động.", "composite",
    bb(6400, 7250, -2700, -2000, 0, 1200), "cabinet",
    [("melt_hyd_hoses_sc", "khối van", (6860, -2000, 1150)), ("melt_hyd_hoses_suv", "khối van", (6460, -2000, 1080)),
     ("ctx_floor", "khung đế", (6800, -2350, 0))],
    "c043 (bộ lọc dẫn động thuỷ lực); cỡ giả định; lùi về Y −2 700 … −2 000 theo review-01 I2",
    ["Thùng dầu 250 L, động cơ-bơm 7,5 kW đứng, khối van, bình tích áp, lọc, đồng hồ áp, nhiệt-mức kế.",
     "Làm mát dầu bằng quạt gió–dầu gắn trên nắp (không cần nước); mặt khối van hướng +Y ra lối đi."])
HSC = [[(6860, -2000, 1150), (6860, -1085, 1150)], [(6940, -2000, 1150), (6940, -1085, 1150)]]
add("melt_hyd_hoses_sc", "melt", "Ống thuỷ lực bộ lọc", "Screen changer hydraulic hoses",
    "Dẫn dầu áp lực/hồi tới xi lanh bộ lọc.", "pipe", pipes_bb(HSC, 13), "black",
    [("melt_hpu", "đầu nối", HSC[0][0]), ("melt_sc_drive", "đầu nối", HSC[0][-1])],
    "giả định", ["2 ống mềm thuỷ lực DN12 (P, T), cách nhau 80 mm, treo trên giá ở Z 1 150 qua lối đi."],
    paths_mm=[lp(pa) for pa in HSC], radius_mm=13, count=2)
HSV = [[(6460, -2000, 1080), (6460, -1000, 1080), (6221, -860, 1170)],
       [(6540, -2000, 1160), (6540, -1000, 1160), (6221, -860, 1230)]]
add("melt_hyd_hoses_suv", "melt", "Ống thuỷ lực van khởi động", "Diverter valve hydraulic hoses",
    "Dẫn dầu tới xi lanh van khởi động.", "pipe", pipes_bb(HSV, 13), "black",
    [("melt_hpu", "đầu nối", HSV[0][0]), ("melt_startup_cyl", "đầu nối", HSV[0][-1])],
    "giả định", ["2 ống mềm DN10."], paths_mm=[lp(pa) for pa in HSV], radius_mm=13, count=2)
add("melt_pump_adapter_in", "melt", "Bích chuyển vào bơm (P3)", "Gear pump inlet adapter",
    "Nối bộ lọc với bơm; mang cảm biến P3 (áp hút bơm, điều khiển tốc độ bơm bánh răng).", "revolve",
    cylx(7301, 7476, 180), "steel",
    [("melt_screen_changer", "bích ra", (7301, 0, 1200)), ("melt_gear_pump", "bích vào", (7476, 0, 1200)),
     ("melt_sensor_p3", "lỗ ren", (7388, 0, 1380)),
     ("melt_heater_conduits", "hộp đấu băng nhiệt", (7388, -175, 1050))], "giả định",
    ["Ống bích Ø360 dài 175, 1 băng nhiệt."], axis="X", radius_mm=180, length_mm=175,
    profile_mm=prof_flanged(175, 180, 150, 30))
add("melt_sensor_p3", "melt", "Cảm biến áp suất hút bơm (P3)", "Pump inlet pressure transducer (P3)",
    "Giữ áp hút bơm ổn định (≈ 50 bar) bằng cách chỉnh tốc độ bơm bánh răng; lưu lượng do các cân loss-in-weight quyết định.", "cyl",
    bb(7358, 7418, -30, 30, 1375, 1620), "stainless",
    [("melt_pump_adapter_in", "ren", (7388, 0, 1380))], "giả định", ["Thân Ø25, đầu Ø40."])
add("melt_gear_pump", "melt", "Bơm bánh răng nhựa", "Melt gear pump (Maag extrex6 GU 100/125)",
    "Tạo áp ổn định không dao động (≈ 250 bar) cho khuôn, tách áp trục vít khỏi khuôn.", "box",
    bb(7476, 7926, -300, 230, 970, 1430), "steel",
    [("melt_pump_adapter_in", "bích vào", (7476, 0, 1200)), ("melt_pump_adapter_out", "bích ra", (7926, 0, 1200)),
     ("melt_stand_pump", "chân bơm trên tấm trượt", (7700, 0, 970)), ("melt_pump_cardan", "đầu trục then", (7701, -300, 1250))],
    "c047 (764 cm³/v, 4 474 kg/h ở 134 v/ph → ≈ 105 v/ph ở 3 500 kg/h), c049 (370 bar), web-14; kích thước thân giả định",
    ["Khối thép 420 × 460 × 460, mặt bên vòng 12 bulông lục giác chìm, đĩa bích tròn lớn Ø360 trên mặt vào/ra (như web-14).",
     "Đầu trục dẫn động nhô ra phía −Y tại Z = 1 250; lỗ thanh nhiệt cắm."])
add("melt_pump_cardan", "melt", "Trục các-đăng + vỏ che", "Cardan shaft with guard",
    "Truyền mômen từ hộp giảm tốc tới trục bơm, bù lệch.", "box", bb(7551, 7851, -1300, -300, 1100, 1400), "white",
    [("melt_gear_pump", "khớp then", (7701, -300, 1250)), ("melt_pump_gearbox", "mặt bích", (7701, -1300, 1250))],
    "web-07 (hộp che dài có lưới thông gió giữa bơm và hộp số)", ["Vỏ che tôn 300 × 300 có ô lưới, trục các-đăng bên trong."])
add("melt_pump_gearbox", "melt", "Hộp giảm tốc bơm", "Gear pump reducer (bevel-helical)",
    "Giảm tốc động cơ 1 480 → ≈ 105 v/ph.", "box", bb(7451, 7951, -1750, -1300, 950, 1450), "white",
    [("melt_pump_cardan", "trục ra", (7701, -1300, 1250)), ("pump_drive_pedestal", "4 bulông", (7701, -1525, 950)),
     ("melt_pump_motor", "mặt bích động cơ", (7701, -1525, 1450))],
    "web-07 (hộp giảm tốc góc + động cơ đứng)", ["Hộp góc côn-trụ 500 × 450 × 500, i ≈ 14."])
add("melt_pump_motor", "melt", "Động cơ bơm 45 kW", "Gear pump motor 45 kW (vertical)",
    "Quay bơm bánh răng qua hộp giảm tốc.", "cyl", cylz(1450, 2300, 220, 7701, -1525), "white",
    [("melt_pump_gearbox", "mặt bích V1", (7701, -1525, 1450))],
    "web-07 (động cơ đứng trên hộp số); công suất giả định (thuỷ lực ≈ 16 kW, hiệu suất + dự phòng)",
    ["Động cơ đứng Ø440 cao 850, nắp quạt trên đỉnh, hộp đấu dây bên."], axis="Z", radius_mm=220)
add("melt_pump_adapter_out", "melt", "Bích ra bơm (P4)", "Gear pump outlet adapter",
    "Nối bơm với ống nhựa; mang cảm biến P4 (áp ra bơm).", "revolve", cylx(7926, 8076, 150), "steel",
    [("melt_gear_pump", "bích ra", (7926, 0, 1200)), ("melt_pipe", "bích", (8076, 0, 1200)),
     ("melt_sensor_p4", "lỗ ren", (8001, 0, 1350)),
     ("melt_rupture_disc_2", "lỗ ren bên −Y", (8001, -150, 1200)),
     ("melt_heater_conduits", "hộp đấu băng nhiệt + thanh nhiệt bơm", (8001, -155, 1100))], "giả định",
    ["Ống bích Ø300 dài 150, 1 băng nhiệt; lỗ cảm biến P4 trên đỉnh và lỗ đĩa nổ 2 bên −Y."], axis="X", radius_mm=150, length_mm=150,
    profile_mm=prof_flanged(150, 150, 120, 30))
add("melt_sensor_p4", "melt", "Cảm biến áp suất ra bơm (P4)", "Pump outlet pressure transducer (P4)",
    "Giám sát áp ra bơm, ngắt bơm và trục vít khi vượt 330 bar.", "cyl", bb(7971, 8031, -30, 30, 1345, 1590), "stainless",
    [("melt_pump_adapter_out", "ren", (8001, 0, 1350))], "giả định", ["Thân Ø25, đầu Ø40."])
add("melt_rupture_disc_2", "melt", "Đĩa nổ sau bơm", "Rupture disc after gear pump",
    "Bảo vệ cơ khí ống, bộ trộn và khuôn khi khuôn bị nghẹt (bơm tạo được tới 370 bar).", "cyl",
    cyly(-270, -150, 20, 8001, 1200), "steel",
    [("melt_pump_adapter_out", "ren 1/2\"-20UNF", (8001, -150, 1200))], "review-01 I5; c049 (370 bar)",
    ["Đầu đĩa nổ Ø40 dài 120 theo −Y, áp nổ 350 bar, nắp chụp hướng xuống; tín hiệu đứt đĩa về tủ điều khiển."],
    axis="Y", radius_mm=20)
add("melt_pipe", "melt", "Ống nhựa nóng có gia nhiệt", "Heated melt pipe",
    "Dẫn nhựa từ bơm tới bộ trộn tĩnh, giữ nhiệt ≈ 280 °C.", "revolve", cylx(8076, 8426, 150), "stainless",
    [("melt_pump_adapter_out", "bích", (8076, 0, 1200)), ("melt_static_mixer", "bích", (8426, 0, 1200)),
     ("melt_pipe_saddles", "gối", (8250, 0, 1050)), ("melt_heater_conduits", "hộp đấu trên vỏ bọc −Y", (8250, -150, 1100))],
    "specs §4 (ống gia nhiệt, cách nhiệt, vỏ inox); giả định",
    ["Ống DN100 (lỗ Ø100); 3 băng nhiệt nằm dưới lớp cách nhiệt và vỏ inox Ø300 (không thấy từ ngoài); 1 hộp đấu nhỏ 120 × 80 trên vỏ bọc phía −Y tại X 8 250."], axis="X", radius_mm=150, length_mm=350)
add("melt_static_mixer", "melt", "Bộ trộn tĩnh", "Static mixer",
    "Đồng nhất nhiệt độ nhựa trước khuôn.", "revolve", cylx(8426, 8926, 150), "stainless",
    [("melt_pipe", "bích", (8426, 0, 1200)), ("melt_die_adapter", "bích", (8926, 0, 1200)),
     ("melt_pipe_saddles", "gối", (8560, 0, 1050)), ("melt_heater_conduits", "hộp đấu trên vỏ bọc −Y", (8676, -150, 1100))],
    "specs §4 (tuỳ chọn DN ≈ 120, dài ≈ 600); giả định",
    ["Vỏ DN100 với 6 phần tử trộn; 4 băng nhiệt dưới vỏ inox Ø300 (không thấy từ ngoài), 1 hộp đấu trên vỏ bọc phía −Y tại X 8 676; bích hai đầu."], axis="X", radius_mm=150, length_mm=500)
add("melt_die_adapter", "melt", "Bích chuyển vào khuôn", "Die inlet adapter",
    "Chuyển lỗ tròn Ø100 sang cửa vào khuôn ở giữa mặt sau khuôn.", "composite",
    bb(8926, DIE_XB, -260, 260, 1010, 1390), "steel",
    [("melt_static_mixer", "bích", (8926, 0, 1200)), ("die_body_upper", "bích chữ nhật 8 vít M30", (DIE_XB, 0, 1300)),
     ("die_body_lower", "bích chữ nhật 8 vít M30", (DIE_XB, 0, 1100)), ("melt_sensor_die", "lỗ ren", (9035, 0, 1390))],
    "giả định; rút ngắn theo DECISIONS 20",
    ["Dài 134 (X 8 926–9 060): bích tròn Ø300 dày 24 (X 8 926–8 950, 8 × M24 PCD 250 về bộ trộn), cổ Ø240 (X 8 950–9 015) mang 1 băng nhiệt Ø260, bích chữ nhật 520 × 380 dày 45 (X 9 015–9 060, Y ±260, Z 1 010–1 390) áp vào mặt sau khuôn.",
     "Lòng Ø100 thẳng suốt, đồng trục với cửa vào khuôn (Y 0, Z 1 200).",
     "8 vít M30 lục giác chìm bắt từ phía bộ trộn vào lỗ ren sâu 60 trên mặt sau khuôn (X 9 060–9 120): 4 vít vào nửa trên tại Y ±110, ±220, Z 1 350; 4 vít vào nửa dưới tại Y ±55, ±165, Z 1 050. Các vị trí này xen giữa vít thân khuôn (xem die_body_bolts, khe ≥ 20 mm).",
     "2 cảm biến P5/T5 cắm đứng trên đỉnh bích chữ nhật tại X 9 035, Y ±30, lỗ sâu 150 xuống lòng Ø100."])
add("melt_sensor_die", "melt", "Cảm biến áp + nhiệt vào khuôn (P5, T5)", "Die inlet pressure + temperature (P5, T5)",
    "Đo áp và nhiệt nhựa vào khuôn.", "cyl", bb(9015, 9055, -50, 50, 1385, 1630), "stainless",
    [("melt_die_adapter", "ren", (9035, 0, 1390))], "giả định; dời theo DECISIONS 20",
    ["2 cảm biến cắm đứng trên đỉnh bích chữ nhật của bích chuyển, tại X 9 035, Y = −30 (P5, áp) và +30 (T5, nhiệt); thân cứng dài 150 xuống lòng Ø100."],
    count=2, item_mm=[40, 40, 245], positions_mm=[[9035, -30, 1507.5], [9035, 30, 1507.5]])
add("melt_heater_bands", "melt", "Băng nhiệt đường chảy (lộ ra ngoài)", "Melt line heater bands (visible)",
    "Giữ nhiệt các bích chuyển và đầu xi lanh.", "revolve", bb(5801, 9018, -257, 257, 943, 1457), "polished",
    [("melt_head_adapter", "kẹp", (5836, 0, 1440)), ("melt_sc_adapter_in", "kẹp", (6521, 0, 1390)),
     ("melt_pump_adapter_out", "kẹp", (8001, 0, 1330)), ("melt_die_adapter", "kẹp", (8983, 0, 1330))],
    "giả định; vị trí theo review-01 C1",
    ["6 băng mica/gốm rộng 70 có hộp đấu nhỏ và cáp bọc lưới: đầu xi lanh X 5 836 (Ø514) và 5 906 (Ø454, khe dưới 2 cảm biến), bích vào lọc X 6 521 (Ø380, khe dưới P2), bích vào bơm X 7 388 (Ø320, khe dưới P3), bích ra bơm X 8 001 (Ø260, khe dưới P4), cổ bích khuôn X 8 983 (Ø260, trên cổ Ø240).",
     "7 băng trên ống và bộ trộn nằm dưới vỏ inox Ø300, không dựng thành vòng (xem melt_pipe, melt_static_mixer)."],
    count=6, item_mm=[70, 514, 514],
    positions_mm=[[x, 0, AXZ] for x in (5836, 5906, 6521, 7388, 8001, 8983)])
add("melt_heater_jbox", "melt", "Hộp đấu nhiệt đường chảy", "Melt-line heater junction box",
    "Đấu nguồn nhiệt và cặp nhiệt cho bộ lọc (6 vùng, 39 kW), van khởi động, bơm, các bích và ống (≈ 75 kW tổng).", "box",
    bb(6650, 7250, -850, -600, 150, 950), "cabinet",
    [("melt_stand_sc", "bắt mặt −Y giá bộ lọc", (6950, -600, 550)),
     ("melt_heater_conduits", "ốc siết ống luồn", (6700, -650, 950))],
    "review-01 I6; giả định",
    ["Hộp RAL 7035 600 × 250 × 800 dưới tay quay bộ lọc; cửa bản lề, ổ cắm công nghiệp nhiều chân, tem cảnh báo điện; cáp nguồn vào từ hào cáp qua đáy."])
MHC = [[(6700, -650, 950), (6700, -650, 980), (6700, -520, 980)],
       [(6650, -700, 800), (6380, -700, 800), (6380, -300, 980), (6380, -260, 980)],
       [(6650, -780, 760), (5836, -780, 760), (5836, -780, 1100), (5836, -245, 1100)],
       [(7250, -700, 900), (7388, -700, 900), (7388, -700, 1050), (7388, -175, 1050)],
       [(7250, -780, 850), (8001, -780, 850), (8001, -780, 1100), (8001, -155, 1100)],
       [(7250, -820, 800), (8250, -820, 800), (8250, -820, 1100), (8250, -150, 1100)],
       [(7250, -840, 750), (8676, -840, 750), (8676, -840, 1100), (8676, -150, 1100)]]
add("melt_heater_conduits", "melt", "Ống luồn cáp nhiệt đường chảy", "Melt-line heater conduits",
    "Dẫn cáp nhiệt từ hộp đấu tới từng vùng nhiệt của đường chảy.", "pipe", pipes_bb(MHC, 15), "galv",
    [("melt_heater_jbox", "ốc siết", (6700, -650, 950)), ("melt_screen_changer", "hộp nhiệt 6 vùng", (6700, -520, 980)),
     ("melt_startup_valve", "hộp đấu", (6380, -260, 980)), ("melt_head_adapter", "băng nhiệt", (5836, -245, 1100)),
     ("melt_pump_adapter_in", "băng nhiệt", (7388, -175, 1050)), ("melt_pump_adapter_out", "băng nhiệt + bơm", (8001, -155, 1100)),
     ("melt_pipe", "hộp đấu vỏ bọc", (8250, -150, 1100)), ("melt_static_mixer", "hộp đấu vỏ bọc", (8676, -150, 1100))],
    "review-01 I6; giả định",
    ["7 ống luồn kim loại mềm Ø30 (đường đi trong paths_mm): bộ lọc, van khởi động, đầu xi lanh, bích vào bơm, bích ra bơm (kèm thanh nhiệt thân bơm), ống nhựa, bộ trộn; đi thấp ở Z 750–900 phía −Y rồi lên hộp đấu từng vùng."],
    count=7, radius_mm=15, paths_mm=[lp(pa) for pa in MHC])

# =========================================================== DIE
up_xz = [[9126, 1200], [9576, 1200], [9576, 1208], [9446, 1290], [9404, 1347.9], [9404, 1212], [9392, 1212],
         [9392, 1364.5], [9330, 1450], [9126, 1450]]
lo_xz = [[9126, 950], [9330, 950], [9446, 1110], [9576, 1192], [9576, 1200], [9126, 1200]]
add("die_body_upper", "die", "Nửa khuôn trên (có môi mềm)", "Upper die body (with flex lip)",
    "Nửa trên ống phân phối móc áo (coat-hanger manifold), mang môi mềm, thanh chắn và bulông chỉnh.",
    "extrude", bb(9126, 9576, -1300, 1300, 1200, 1450), "chrome",
    [("die_body_lower", "mặt phân khuôn, bulông M24 bước 100", (9350, 0, 1200)),
     ("melt_die_adapter", "bích cửa vào", (9126, 0, 1300)),
     ("die_end_plate_op", "bulông", (9350, 1300, 1325)), ("die_end_plate_rear", "bulông", (9350, -1300, 1325)),
     ("die_thermal_bolts", "lỗ ren trong thân", (9400, 0, 1370)), ("die_choker_bolts", "lỗ ren mặt đỉnh", (9255, 0, 1450)),
     ("die_bolt_actuator_rail", "bắt vít lên mặt đỉnh", (9315, 0, 1450)), ("die_flex_lip", "liền khối, rãnh bản lề", (9450, 0, 1250)),
     ("die_heater_boxes", "bắt mặt sau", (9126, 600, 1385))],
    "c053/c055/c056/c057 (khuôn móc áo, môi mềm, thanh chắn); DECISIONS 10 (môi rộng 2 400); chiều cao/chiều sâu giả định theo web-19/20",
    ["Rộng 2 600 (Y ±1 300), cao 250 (Z 1 200–1 450), sâu 450 (X 9 126–9 576), mũi vát 30° về phía khe trục.",
     "Mạ crôm bóng; 9 vùng thanh nhiệt cắm từ mặt sau.",
     "Rãnh bản lề môi mềm (flex-lip hinge slot) hở, chạy suốt bề rộng 2 400 tại X 9 392–9 404 (rộng 12), cắt từ mặt vát xuống tới Z 1 212, để lại gân bản lề dày 12 mm trên mặt chảy (Z 1 200); phần sau rãnh là môi mềm. Đầu bulông nhiệt tì lên môi tại X 9 440, cách gân 36 mm.",
     "Mặt đỉnh từ sau ra trước: hộp nhiệt mặt sau (X ≤ 9 126), tai cẩu ở tấm đầu, hàng bulông thanh chắn X 9 255 (thanh chắn trong thân X 9 240–9 270), máng bulông nhiệt X 9 285–9 345, rồi mặt vát mang 94 bulông nhiệt."],
    outline_mm={"plane": "XZ", "pts": up_xz, "d0": -1300, "d1": 1300})
add("die_body_lower", "die", "Nửa khuôn dưới", "Lower die body",
    "Nửa dưới ống phân phối, môi dưới thay được.", "extrude",
    bb(9126, 9576, -1300, 1300, 950, 1200), "chrome",
    [("die_body_upper", "mặt phân khuôn", (9350, 0, 1200)), ("die_cart", "2 đệm đỡ", (9240, 700, 950)),
     ("melt_die_adapter", "bích", (9126, 0, 1100)),
     ("die_end_plate_op", "bulông", (9350, 1300, 1075)), ("die_end_plate_rear", "bulông", (9350, -1300, 1075)),
     ("die_heater_boxes", "bắt mặt sau", (9126, 600, 1015))],
    "như trên", ["Cao 250 (Z 950–1 200); 9 vùng thanh nhiệt.",
                 "Môi dưới (lower lip) là thanh chèn thay được dọc mũi, X 9 446–9 576 × cao 60, bắt 24 vít M12 lục giác chìm từ mặt vát dưới (bước 100)."],
    outline_mm={"plane": "XZ", "pts": lo_xz, "d0": -1300, "d1": 1300})
add("die_flex_lip", "die", "Môi mềm khuôn", "Flex lip",
    "Chỉnh khe môi cục bộ (hành trình ≈ 1–2,5 mm) để đều chiều dày tấm.", "extrude",
    bb(9404, 9576, -1200, 1200, 1200, 1348), "chrome",
    [("die_body_upper", "liền khối qua rãnh bản lề", (9450, 0, 1250)), ("die_thermal_bolts", "đầu bulông đẩy", (9440, 0, 1290)),
     ("ctx_sheet", "khe môi → màn nhựa", (9576, 0, 1200))],
    "c053, c055 (0,040\"), c056 (2,5 mm); rãnh bản lề hở theo drawing review-01 I5",
    ["Dải môi rộng 2 400, khe làm việc 0,5–2 mm tại Z = 1 200, X = 9 576; là phần mũi của nửa trên phía sau rãnh bản lề hở (X 9 392–9 404, suốt bề rộng, gân 12 mm).",
     "Bulông nhiệt bắc qua rãnh (ren trong thân phía trước rãnh), đầu bulông tì lên môi tại X 9 440 (cách gân 36 mm), nên môi uốn quanh gân."],
    outline_mm={"plane": "XZ", "pts": [[9404, 1200], [9576, 1200], [9576, 1208], [9446, 1290], [9404, 1347.9]], "d0": -1200, "d1": 1200})
for side, (y0, y1), sgn in (("op", (1300, 1375), 1), ("rear", (-1375, -1300), -1)):
    add(f"die_end_plate_{side}", "die", f"Tấm đầu khuôn ({'+Y' if sgn > 0 else '−Y'})",
        f"Die end plate ({'operator' if sgn > 0 else 'rear'} side)",
        "Bịt hai đầu ống phân phối, mang thanh deckle và hộp đấu nhiệt tấm đầu.", "box",
        bb(9126, 9560, y0, y1, 950, 1450), "chrome",
        [("die_body_upper", "bulông", (9350, sgn * 1300, 1325)), ("die_body_lower", "bulông", (9350, sgn * 1300, 1075)),
         ("die_deckles", "lỗ dẫn hướng", (9480, sgn * 1375, 1200)), ("die_lifting_lugs", "lỗ ren tai cẩu", (9190, sgn * 1337, 1450))],
        "web-19/20 (tấm đầu có khối đầu nối nhiệt)", ["Tấm thép 75 mm, khối đầu nối thanh nhiệt (terminal block) 6 lỗ, 1 vùng nhiệt."])
add("die_deckles", "die", "Thanh deckle chỉnh bề rộng", "Deckle rods (internal/external)",
    "Thu hẹp bề rộng màn nhựa ở hai đầu khi đổi khổ tấm.", "cyl", bb(9380, 9520, -1525, 1525, 1180, 1220), "steel",
    [("die_end_plate_op", "lỗ dẫn", (9480, 1375, 1200)), ("die_end_plate_rear", "lỗ dẫn", (9480, -1375, 1200))],
    "c057 (deckle trong/ngoài); rút ngắn theo review-01 M6",
    ["Mỗi đầu 1 thanh Ø30 nhô 150 ngoài tấm đầu (tới |Y| 1 525) tại X 9 480, có núm vặn + thước; lưỡi deckle trong nằm trong khuôn, không vượt X 9 520 (tránh khung cụm trục)."],
    count=2, item_mm=[40, 150, 40], positions_mm=[[9480, 1450, 1200], [9480, -1450, 1200]])
TB_AX = [-98 / 170.0, 0.0, 139 / 170.0]
add("die_thermal_bolts", "die", "Bulông nhiệt chỉnh môi", "Thermal lip-adjust bolts",
    "Đẩy môi mềm theo điều khiển tự động (giãn nở nhiệt), chỉnh profin chiều dày ngang tấm.", "cyl",
    bb(9330, 9452, -1197, 1197, 1284, 1446), "black",
    [("die_body_upper", "lỗ ren", (9400, 0, 1370)), ("die_flex_lip", "đầu đẩy", (9440, 0, 1290)),
     ("die_bolt_actuator_rail", "khối gia nhiệt + ống gió", (9340, 0, 1448))],
    "c053/c054 (bước 25,4 mm, 80 W, hành trình 300 µm); web-17/18; trục bulông theo review-01 C1",
    ["94 bulông, y = −1 181 + 25,4·k (k = 0…93); mỗi bulông Ø30 (thân Ø16 trong ống gia nhiệt 80 W) dài 170, trục từ (9 440, y, 1 295) tới (9 342, y, 1 434), tức 35° so với phương đứng, nằm dọc mặt vát của nửa trên.",
     "Đầu bulông nằm trong rãnh phay, nhô tối đa 30 mm khỏi mặt vát, còn ≈ 20 mm khe hở tới trục giữa (đã kiểm tra bằng hình học).",
     "positions_mm là tâm bulông; item_mm = [Ø, Ø, dài] theo hệ trục riêng của bulông, trục dài là item_axis."],
    count=94, pitch_mm=25.4, item_mm=[30, 30, 170], item_axis=[round(v, 4) for v in TB_AX], item_length_mm=170,
    positions_mm=[[9391, r1(-1181 + 25.4 * k), 1364.5] for k in range(94)])
add("die_bolt_actuator_rail", "die", "Thanh cơ cấu bulông nhiệt + máng cáp + ống gió", "Thermal-bolt actuator rail with cable duct and air duct",
    "Gom cáp 94 thanh nhiệt bulông và dẫn gió làm mát bulông.", "box",
    bb(9285, 9345, -1250, 1250, 1450, 1540), "stainless",
    [("die_body_upper", "bắt vít", (9315, 0, 1450)), ("die_thermal_bolts", "khối gia nhiệt", (9340, 0, 1448)),
     ("die_cable_harness", "ổ cắm đầu −Y", (9290, -1250, 1495)), ("util_air_hose_die", "đầu nối khí", (9290, -1240, 1540))],
    "web-17/18 (hàng dây và ống gió dọc môi); c054; thu hẹp theo ghi chú drafter (design_issues #1)",
    ["Máng inox 60 × 90 dài 2 500 trên dải trước của mặt đỉnh (X 9 285–9 345), ngay sau đầu trên các bulông nhiệt; trong máng: cáp 94 thanh nhiệt (tầng trên) và ống gió làm mát (tầng dưới).",
     "2 ổ cắm nhiều chân đánh số ở đầu −Y; nắp máng tháo được để chừa lối vặn bulông thanh chắn ngay phía sau."])
add("die_choker_bolts", "die", "Bulông chỉnh thanh chắn", "Choker (restrictor) bar adjusting bolts",
    "Chỉnh thô dòng chảy ngang khuôn qua thanh chắn (restrictor bar) nằm sau ống phân phối, trước vùng preland.", "cyl",
    bb(9240, 9270, -1215, 1215, 1450, 1530), "black",
    [("die_body_upper", "lỗ ren mặt đỉnh, đẩy thẳng đứng xuống thanh chắn", (9255, 0, 1450))],
    "c053 (thanh chắn chỉnh thô), web-19; vị trí theo ghi chú drafter (design_issues #1)",
    ["33 bulông đầu đen Ø30 cao 80 đặt đứng trên mặt đỉnh tại X 9 255, ngay trên thanh chắn (X 9 240–9 270), Y = −1 200 + 75·k (k = 0…32), đai ốc khoá; bulông đẩy/kéo thẳng thanh chắn như khuôn môi mềm thông thường.",
     "Vặn bằng khẩu từ trên xuống; khe 15 mm tới máng bulông nhiệt phía trước (X 9 285)."],
    count=33, pitch_mm=75, item_mm=[30, 30, 80], positions_mm=[[9255, -1200 + 75 * k, 1490] for k in range(33)])
DBB_ROWS = [(9160, -1265, 24, 1435), (9210, -1210, 23, 1435), (9160, -1210, 23, 965), (9270, -1265, 24, 965)]
DBB = [[x, y0 + 110 * k, z] for x, y0, n, z in DBB_ROWS for k in range(n)]
add("die_body_bolts", "die", "Bulông thân khuôn M30", "Die body bolts (M30 socket-head cap screws)",
    "Kẹp hai nửa khuôn vào nhau, chịu lực tách ≈ 7 MN do áp nhựa trong ống phân phối và preland.", "cyl",
    bb(9137.5, 9292.5, -1287.5, 1287.5, 950, 1450), "black",
    [("die_body_upper", "lỗ khoét bậc trên mặt đỉnh / lỗ ren nhận bulông từ dưới", (9160, 0, 1440)),
     ("die_body_lower", "lỗ khoét bậc ở mặt đáy / lỗ ren nhận bulông từ trên", (9160, 0, 960))],
    "drawing review-01 I4; cỡ và vị trí giả định (tính lực kẹp)",
    ["94 vít lục giác chìm M30 cấp 10.9 dài 260, đầu Ø45 nằm chìm trong lỗ khoét bậc Ø48 × 32 (mặt khuôn phẳng); positions_mm là tâm đầu vít (đầu cao 30).",
     "Mặt đỉnh nửa trên: hàng X 9 160 (24 vít, Y = −1 265 … +1 265 bước 110) và hàng X 9 210 (23 vít, Y = −1 210 … +1 210), cả hai nằm sau hàng bulông thanh chắn (X 9 240–9 270) và máng bulông nhiệt (X 9 285–9 345).",
     "Mặt đáy nửa dưới: hàng X 9 160 (23 vít, Y = −1 210 …) và hàng X 9 270 (24 vít, Y = −1 265 …), tức cách mép trước mặt đáy (X 9 330) 170 và 60 mm.",
     "Vít từ trên ren vào nửa dưới, vít từ dưới ren vào nửa trên; các hàng lệch nhau 55 mm theo Y nên thân vít đi song song không chạm nhau.",
     "Lực kẹp ≈ 94 × 330 kN ≈ 31 MN, gấp ≈ 4 lần lực tách; ống phân phối (G) phải đi giữa và trước các hàng vít (xem design.md §9)."],
    count=len(DBB), item_mm=[45, 45, 30], positions_mm=DBB)
add("die_heater_boxes", "die", "Hộp đầu nối nhiệt khuôn", "Die heater terminal boxes",
    "Đấu dây 20 vùng nhiệt khuôn (≈ 50 kW).", "box", bb(9050, 9126, -1250, 1250, 960, 1440), "stainless",
    [("die_body_upper", "bắt mặt sau", (9126, 600, 1385)), ("die_body_lower", "bắt mặt sau", (9126, 600, 1015)),
     ("die_heater_conduit", "ống luồn cáp", (9090, -1250, 1000))],
    "web-17 (hộp nhiệt inox có tem vàng), c055 (≈ 21 kW/m)",
    ["2 hộp dài (trên Z 1 330–1 440, dưới Z 960–1 070) chạy Y ±1 250, chừa giữa ±260 cho bích vào; tem cảnh báo vàng."])
add("die_lifting_lugs", "die", "Tai cẩu khuôn", "Die lifting eyes",
    "Cẩu khuôn khi lắp/tháo.", "cyl", bb(9150, 9510, -1360, 1360, 1450, 1580), "steel",
    [("die_end_plate_op", "ren M36", (9190, 1337, 1450)), ("die_end_plate_rear", "ren M36", (9190, -1337, 1450))],
    "web-07 (2 tai cẩu trên khuôn); vị trí theo review-01 C1",
    ["4 tai cẩu M36 cao 130, 2 trên mỗi tấm đầu tại X 9 190 và 9 470, |Y| = 1 337 (ngoài mặt trục ±1 300, trước cổ trục X ≥ 9 626)."],
    count=4, item_mm=[80, 46, 130],
    positions_mm=[[x, y, 1515] for x in (9190, 9470) for y in (-1337, 1337)])
DH = [(9290, -1250, 1495), (9290, -1450, 1495), (9290, -1450, 1100), (9100, -1650, 1000)]
add("die_cable_harness", "die", "Bó cáp khuôn (cắm rút)", "Die cable harness (plug-in)",
    "Dẫn cáp bulông nhiệt và cảm biến khuôn xuống hộp đấu dây khuôn; rút phích ra khi kéo khuôn đi.", "pipe",
    pipe_bb(DH, 30), "rubber",
    [("die_bolt_actuator_rail", "ổ cắm", DH[0]), ("die_junction_box", "phích cắm nhiều chân trên nóc hộp", DH[-1])],
    "web-17 (cáp xám có đầu cắm đánh số); review-01 I6",
    ["Ống luồn cáp mềm Ø60 đi xuống phía −Y rồi chéo về nóc hộp đấu dây khuôn; 2 phích nhiều chân đánh số ở đầu hộp."],
    path_mm=lp(DH), radius_mm=30)
HC = [(9090, -1250, 1000), (9090, -1500, 1000), (9000, -1650, 950)]
add("die_heater_conduit", "die", "Ống luồn cáp nhiệt khuôn (cắm rút)", "Die heater cable conduit (plug-in)",
    "Dẫn cáp 20 vùng nhiệt khuôn từ hộp đầu nối tới hộp đấu dây khuôn; có phích cắm để tách khuôn.", "pipe",
    pipe_bb(HC, 20), "galv",
    [("die_heater_boxes", "ốc siết cáp", HC[0]), ("die_junction_box", "phích cắm", HC[-1])],
    "giả định", ["Ống mềm kim loại Ø40."], path_mm=lp(HC), radius_mm=20)
cart_xz = [[8700, 60], [9380, 60], [9380, 300], [9350, 300], [9350, 950], [9150, 950], [9150, 300], [8700, 300]]
add("die_cart", "die", "Xe đỡ khuôn chỉnh cao", "Die support cart with height adjustment",
    "Đỡ khuôn ≈ 3,4 t, chỉnh cao ±50 mm bằng kích vít, tự do ±40 mm theo X (giãn nở), kéo khuôn ra theo +Y trên ray.", "frame",
    bb(8700, 9380, -1200, 1200, 60, 950), "frame",
    [("die_body_lower", "2 đệm trên bàn trượt", (9240, 700, 950)), ("die_cart_rails", "4 bánh xe", (8760, 0, 60))],
    "web-08 (xe khuôn đế rộng có bánh và cột chỉnh), c057 (die carts); review-01 I3, I8",
    ["Đế thép hộp rộng X 8 700–9 380, Z 60–300, luồn dưới bộ trộn và bích khuôn; 4 bánh: 2 bánh trụ trên ray phẳng X 8 760, 2 bánh rãnh V trên ray dẫn hướng X 9 320 (khổ 560).",
     "Hai cột kích vít có tay quay ở X 9 150–9 350, xà đỡ trên có bàn trượt ±40 mm theo X và 2 đệm tại Y = ±700.",
     "Phía trước đế không vượt X 9 380 dưới Z 600 (trục dưới ở X ≥ 9 429 tại Z 600); khoá bánh khi chạy.",
     "Phải lùi cụm trục cán trước khi kéo khuôn ra theo +Y."],
    outline_mm={"plane": "XZ", "pts": cart_xz, "d0": -1200, "d1": 1200})
add("die_cart_rails", "die", "Ray xe khuôn", "Die cart rails",
    "Dẫn xe khuôn ra phía +Y khi bảo trì.", "frame", bb(8740, 9340, -1500, 2800, 0, 60), "steel",
    [("die_cart", "bánh xe", (8760, 0, 60)), ("ctx_floor", "bulông neo", (8760, 0, 0))],
    "giả định; khổ ray theo review-01 I3",
    ["2 ray dài 4 300 theo Y: ray phẳng tại X 8 760, ray có gờ dẫn hướng tại X 9 320 (khổ 560); khoá sàn ở vị trí làm việc."],
    count=2, item_mm=[40, 4300, 60], positions_mm=[[8760, 650, 30], [9320, 650, 30]])
add("die_junction_box", "die", "Hộp đấu dây khuôn", "Die junction box",
    "Tập trung cáp nhiệt khuôn (20 vùng), 94 mạch bulông nhiệt, cảm biến; phích cắm để tách khuôn; nút dừng khẩn.", "box",
    bb(8700, 9300, -1900, -1600, 0, 1000), "cabinet",
    [("die_cable_harness", "phích cắm", (9100, -1650, 1000)), ("die_heater_conduit", "phích cắm", (9000, -1650, 950)),
     ("ctrl_trench_die_branch", "cáp vào đáy", (8700, -1625, 5)), ("util_frl", "giá gá mặt +X", (9300, -1705, 775)),
     ("ctx_floor", "đế", (9000, -1750, 0))],
    "review-01 I6; giả định",
    ["Tủ đứng RAL 7035 600 × 300 × 1 000 trên sàn, cửa hướng +Y, đặt ngoài ray xe khuôn để không đi theo xe.",
     "Nóc: 2 ổ cắm nhiều chân cho bó cáp bulông nhiệt, 1 ổ cho cáp nhiệt khuôn; nút dừng khẩn đỏ trên cửa."])
add("die_drip_pan", "die", "Khay hứng dưới môi khuôn", "Drip pan under die lip",
    "Hứng nhựa rơi khi khởi động màn nhựa.", "sheet", bb(9576, 9900, -1350, 1350, 0, 80), "stainless",
    [("ctx_floor", "đặt trên sàn", (9700, 0, 0))], "giả định", ["Khay inox 324 × 2 700 cao 80."])

# =========================================================== CONTROL
add("ctrl_drive_cabinet", "control", "Tủ biến tần trung thế", "MV drive converter cabinet",
    "Biến tần điều khiển tốc độ động cơ chính 1 500 kW.", "box", bb(-5200, -1600, -4900, -3700, 0, 2400), "cabinet",
    [("ctrl_heater_cabinet", "đặt sát cạnh", (-1600, -4000, 1000)), ("ctrl_trench_mv", "cáp ra đáy vào hào", (-4000, -3700, 5)),
     ("ctx_floor", "đế 100", (-3400, -4300, 0))],
    "giả định (biến tần trung thế 3 kV ≈ 3,6 m; thường đặt phòng điện, ở đây đặt sau máy để thể hiện); mặt cửa ở Y −3 700 theo review-01 I2",
    ["6 khoang RAL 7035 rộng 600, sâu 1 200, cao 2 400 kể cả đế, cửa mở về +Y có lưới thông gió, đèn báo; trước cửa chừa ≥ 1 000 mm."])
add("ctrl_heater_cabinet", "control", "Tủ điều khiển + nhiệt", "Control and heater cabinets (PLC, heater zones, MCC)",
    "PLC, rơ-le bán dẫn cho vùng nhiệt xi lanh/đường chảy/khuôn, khởi động động cơ phụ.", "box",
    bb(-1600, 800, -4300, -3700, 0, 2200), "cabinet",
    [("ctrl_drive_cabinet", "đặt sát cạnh", (-1600, -4000, 1000)), ("ctrl_floor_duct", "cáp ra đáy", (-1000, -3700, 5)),
     ("ctrl_die_bolt_cabinet", "đặt sát cạnh", (800, -4000, 1000))],
    "c034 (tủ điện), giả định; mặt cửa ở Y −3 700 theo review-01 I2",
    ["4 khoang 600 × 600 × 2 200 RAL 7035, khoang đầu có dải xanh KM và logo; cửa mở về +Y."])
add("ctrl_die_bolt_cabinet", "control", "Tủ điều khiển bulông nhiệt", "Thermal-bolt controller cabinet",
    "Điều khiển 94 thanh nhiệt bulông theo profin chiều dày (bộ điều khiển riêng của hệ bulông nhiệt).", "box",
    bb(800, 1600, -4300, -3700, 0, 2000), "cabinet",
    [("ctrl_heater_cabinet", "đặt sát cạnh", (800, -4000, 1000)), ("ctx_floor", "đế", (1200, -4000, 0))],
    "review-01 I6; c054 (bulông nhiệt 80 W)", ["Tủ 800 × 600 × 2 000 RAL 7035, màn hình profin trên cửa."])
add("ctrl_machine_cabinet", "control", "Tủ đầu máy (khối cao cuối máy)", "Machine-end terminal cabinet",
    "Tủ đấu dây tại chỗ cho truyền động: cấp nguồn cụm dầu, encoder, cảm biến hộp số, an toàn.", "box",
    bb(-5650, -5150, -500, 500, 0, 2000), "km_blue",
    [("base_frame_drive", "áp sát đầu khung", (-5150, 0, 400)), ("ctrl_signal_tower", "bắt trên nóc", (-5400, 0, 2000))],
    "pdf_measures §2.2/§4 ghi chú 3 (khối cao trơn sau động cơ); web-06/07 (tủ trắng có dải xanh KM ở đầu dẫn động)",
    ["Tủ 500 × 1 000 × 2 000, mặt +Y và −X sơn xanh KM có chữ KraussMaffei trắng chạy dọc, còn lại trắng; nút dừng khẩn trên mặt +Y."],
    col=COL["km_blue"])
add("ctrl_signal_tower", "control", "Đèn tháp báo trạng thái", "Signal tower",
    "Báo trạng thái máy (đỏ/vàng/xanh/còi).", "revolve", cylz(2000, 2650, 40, -5400, 0), "black",
    [("ctrl_machine_cabinet", "chân đế", (-5400, 0, 2000))], "giả định", ["4 tầng đèn Ø70 + còi, cột Ø40."],
    axis="Z", radius_mm=40, profile_mm=[[0, 0], [40, 0], [40, 650], [0, 650]])
add("ctrl_hmi", "control", "Bảng điều khiển HMI trên chân đế xoay", "Operator HMI on swivel pedestal",
    "Màn hình cảm ứng + bàn phím màng điều khiển toàn dây chuyền; nút dừng khẩn.", "composite",
    bb(-1700, -900, 1400, 1650, 0, 1850), "white",
    [("ctx_floor", "tấm đế bắt bulông neo", (-1300, 1525, 0))],
    "p22_5/p23_4 (tấm HMI ngang ≈ 1,57 : 1, viền xám đen, phím màng, 2 nút tròn, logo KM, ống đỡ có khớp xoay); web-04/05 (HMI trên chân đế phía vận hành)",
    ["Chân đế ống Ø120 cao 1 300 có khớp xoay đen, tay xoay ngắn; tấm HMI 800 × 510 × 120 nghiêng 15°, mặt hướng +Y.",
     "Nút dừng khẩn đỏ trên vỏ HMI."])
add("ctrl_estops", "control", "Hộp nút dừng khẩn dọc máy", "Emergency-stop stations along the machine",
    "Dừng khẩn toàn dây chuyền từ dọc máy phía vận hành, ở tầm tay.", "box", bb(550, 5750, 480, 1000, 650, 1190), "yellow",
    [("base_frame_process", "cột gá trên mặt khung", (600, 940, 650)),
     ("barrel_cover_c4", "giá gá trên tấm dưới vỏ che", (3700, 480, 1120)),
     ("barrel_cover_c1", "giá gá trên tấm dưới vỏ che", (5700, 480, 1120))],
    "giả định; cao độ theo review-01 M3",
    ["3 hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm Z 1 120 (tầm 1,05–1,19 m): X 600 trên cột gá 60 × 60 từ mặt khung (vùng nạp để lộ), X 3 700 trên tấm dưới vỏ C4, X 5 700 trên tấm dưới vỏ C1.",
     "Thêm nút trên HMI, tủ đầu máy, hộp đấu dây khuôn (−Y), lan can sàn thao tác (ctrl_estop_platform), khuôn phía +Y (ctrl_estop_die) và bộ lọc phía +Y (ctrl_estop_melt)."],
    count=3, item_mm=[100, 80, 140], positions_mm=[[600, 940, 1120], [3700, 520, 1120], [5700, 520, 1120]])
add("ctrl_estop_platform", "control", "Hộp dừng khẩn trên sàn thao tác", "Emergency stop on mezzanine railing",
    "Dừng khẩn từ sàn cân cấp liệu.", "box", bb(-500, -400, 1340, 1420, 3930, 4070), "yellow",
    [("feed_platform_railing", "kẹp lên cột lan can", (-450, 1390, 4000))], "review-01 M3",
    ["Hộp vàng 100 × 80 × 140 có nút nấm đỏ trên cột lan can mép +Y."])
add("ctrl_estop_die", "control", "Hộp dừng khẩn tại khuôn (+Y)", "Emergency stop at die, operator side",
    "Dừng khẩn khi chỉnh môi, deckle, xử lý màn nhựa ở phía vận hành.", "composite",
    bb(9200, 9300, 1200, 1490, 300, 1170), "yellow",
    [("die_cart", "tay đòn gá trên đầu +Y của xe khuôn", (9250, 1200, 350))], "drawing review-01 I2; giả định",
    ["Hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm (9 250, 1 450, 1 100), trên cột ống Ø50 dựng từ tay đòn thấp (Z 300–400) gá vào đầu +Y của xe khuôn; nằm ngoài tấm đầu khuôn (|Y| > 1 375) và trước khung cụm trục.",
     "Cáp nối bằng phích cắm qua hộp đấu dây khuôn để xe khuôn kéo đi được.",
     "outline_mm (mặt YZ) là hình chữ L: tay đòn thấp Y 1 200–1 475, Z 300–400; cột Y 1 425–1 475 lên Z 1 030; hộp Y 1 410–1 490, Z 1 030–1 170."],
    outline_mm={"plane": "YZ", "d0": 9200, "d1": 9300,
                "pts": [[1200, 300], [1475, 300], [1475, 1030], [1490, 1030], [1490, 1170], [1410, 1170],
                        [1410, 1030], [1425, 1030], [1425, 400], [1200, 400]]})
add("ctrl_estop_melt", "control", "Hộp dừng khẩn tại bộ lọc (+Y)", "Emergency stop at screen changer, operator side",
    "Dừng khẩn khi thay lưới / xử lý ở bộ lọc phía vận hành.", "composite",
    bb(7270, 7370, 600, 690, 300, 1170), "yellow",
    [("melt_stand_sc", "cột gá trên mặt +Y giá bộ lọc", (7320, 600, 500))], "drawing review-01 I2; giả định",
    ["Hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm (7 320, 650, 1 100), trên cột 60 × 60 gá vào mặt +Y của giá bộ lọc, ngay sau cụm xả ngược (X ≤ 7 200)."])
add("ctrl_infeed_mv", "control", "Hào cáp trung thế cấp vào", "Incoming MV feed trench",
    "Đưa cáp trung thế 3 kV từ trạm biến áp nhà máy vào tủ biến tần.", "sheet",
    bb(-3600, -3200, -5100, -4900, 0, 10), "galv",
    [("ctrl_drive_cabinet", "vào đáy tủ", (-3400, -4900, 5)), ("ctx_floor", "nắp phẳng sàn", (-3400, -5000, 0))],
    "drawing review-01 I2; giả định (≈ 1,8 MVA)", ["Đoạn hào có nắp rộng 400 phẳng sàn dài 200 sau tủ, đầu ngoài để hở 'từ trạm biến áp' (tuyến tiếp theo thuộc nhà xưởng)."])
add("ctrl_infeed_lv", "control", "Hào cáp hạ thế cấp vào", "Incoming LV feed trench",
    "Đưa cáp hạ thế 400 V từ tủ phân phối nhà máy vào tủ điều khiển + nhiệt.", "sheet",
    bb(-600, -200, -4500, -4300, 0, 10), "galv",
    [("ctrl_heater_cabinet", "vào đáy tủ", (-400, -4300, 5)), ("ctx_floor", "nắp phẳng sàn", (-400, -4400, 0))],
    "drawing review-01 I2; giả định (≈ 500 kVA: nhiệt ≈ 260 kW + động cơ phụ)", ["Đoạn hào có nắp rộng 400 phẳng sàn dài 200 sau tủ, đầu ngoài để hở 'từ tủ phân phối' (tuyến tiếp theo thuộc nhà xưởng)."])
add("ctrl_floor_duct", "control", "Hào cáp tới tủ điều khiển", "Covered floor trench to control cabinets",
    "Dẫn cáp từ máy về tủ điều khiển, nắp phẳng sàn.", "sheet", bb(-1200, -800, -3700, -1050, 0, 10), "galv",
    [("ctrl_heater_cabinet", "vào đáy tủ", (-1000, -3700, 5)), ("ctrl_cable_drop", "nối máng đứng", (-1000, -1050, 5)),
     ("ctrl_floor_trench", "nối hào cáp", (-1000, -1150, 5))], "giả định; hào phẳng sàn theo review-01 I2",
    ["Hào cáp có nắp tôn mạ kẽm chống trượt rộng 400, phẳng sàn (nắp dày 10)."])
add("ctrl_cable_drop", "control", "Máng cáp đứng", "Vertical cable drop",
    "Đưa cáp từ máng trên khung xuống sàn.", "sheet", bb(-1150, -850, -1100, -1000, 0, 750), "galv",
    [("barrel_cable_tray", "nối máng", (-990, -1000, 700)), ("ctrl_floor_duct", "nối máng sàn", (-1000, -1050, 5))],
    "giả định", ["Máng đứng 300 × 100 áp mặt bên khung."])
add("ctrl_floor_trench", "control", "Hào cáp có nắp dọc dây chuyền", "Covered floor cable trench along the line",
    "Dẫn cáp động lực/tín hiệu tới bơm nhựa, hộp nhiệt đường chảy, HPU, cụm chân không, khuôn.", "sheet",
    bb(-1000, 8700, -1250, -1050, 0, 10), "galv",
    [("ctrl_floor_duct", "nối", (-1000, -1150, 5)), ("ctrl_trench_die_branch", "nối", (8600, -1250, 5))],
    "giả định", ["Nắp tôn chống trượt rộng 200 phẳng sàn; kết thúc ở X 8 700, trước ray xe khuôn."])
add("ctrl_trench_die_branch", "control", "Nhánh hào cáp tới hộp khuôn", "Cable trench branch to die junction box",
    "Đưa cáp từ hào chính tới hộp đấu dây khuôn đặt trên sàn.", "sheet", bb(8500, 8700, -1650, -1250, 0, 10), "galv",
    [("ctrl_floor_trench", "nối", (8600, -1250, 5)), ("die_junction_box", "cáp vào đáy hộp", (8700, -1625, 5))],
    "review-01 I3/I6; giả định", ["Nắp tôn rộng 200 phẳng sàn."])
add("ctrl_trench_mv", "control", "Hào cáp trung thế", "MV cable trench",
    "Dẫn cáp trung thế từ tủ biến tần tới động cơ dưới sàn, không vắt qua lối đi.", "sheet",
    bb(-4200, -3800, -3700, -1050, 0, 10), "galv",
    [("ctrl_drive_cabinet", "vào đáy tủ", (-4000, -3700, 5)), ("ctrl_cable_mv", "cáp lên", (-4000, -1100, 10))],
    "review-01 I2; giả định", ["Hào có nắp tôn mạ kẽm rộng 400 phẳng sàn."])
MV = [(-4000, -1100, 10), (-4000, -1100, 1150), (-4000, -925, 1150)]
add("ctrl_cable_mv", "control", "Cáp trung thế động cơ (đoạn lên)", "MV motor cable riser",
    "Đưa cáp trung thế từ hào lên hộp đấu dây động cơ.", "pipe", pipe_bb(MV, 40), "rubber",
    [("ctrl_trench_mv", "ra khỏi hào", MV[0]), ("drive_motor_terminal_box", "ốc siết cáp", MV[-1])],
    "giả định", ["3 cáp trung thế trong ống bảo vệ Ø80 dựng lên sát mặt bên khung (Y −1 100) rồi vào đáy hộp đấu dây."],
    path_mm=lp(MV), radius_mm=40)

# =========================================================== UTILITIES
SR = [(-400, 1060, 0), (-400, 1060, 710), (-400, 880, 710), (-300, 880, 710)]
add("util_cw_supply_riser", "util", "Ống nước cấp từ nhà máy", "Plant cooling-water supply riser",
    "Đưa nước làm mát (≈ 15 °C, 4 bar) từ đường ống nhà máy lên ống góp.", "pipe", pipe_bb(SR, 30), "stainless",
    [("ctx_floor", "bích sàn", SR[0]), ("barrel_cw_supply", "bích DN50", SR[-1]),
     ("util_cw_lube_hoses", "nhánh T", (-400, 1060, 380)), ("util_cw_motor_hoses", "nhánh T", (-400, 1060, 250))], "giả định",
    ["DN50 có van bi tay đỏ, lọc Y và đồng hồ áp ở đoạn đứng."], path_mm=lp(SR), radius_mm=30)
RR = [(-500, 1130, 0), (-500, 1130, 800), (-500, 950, 800), (-300, 950, 800)]
add("util_cw_return_riser", "util", "Ống nước hồi về nhà máy", "Plant cooling-water return riser",
    "Trả nước hồi về đường ống nhà máy.", "pipe", pipe_bb(RR, 30), "stainless",
    [("ctx_floor", "bích sàn", RR[0]), ("barrel_cw_return", "bích DN50", RR[-1]),
     ("util_cw_lube_hoses", "nhánh T", (-500, 1130, 440)), ("util_cw_motor_hoses", "nhánh T", (-500, 1130, 150))], "giả định",
    ["DN50 có van bi tay đỏ và nhiệt kế."], path_mm=lp(RR), radius_mm=30)
LH = [[(-400, 1060, 380), (-2815, 1060, 380), (-2815, 1060, 820), (-2815, 900, 820)],
      [(-500, 1130, 440), (-2735, 1130, 440), (-2735, 1130, 880), (-2735, 900, 880)]]
add("util_cw_lube_hoses", "util", "Ống nước làm mát dầu hộp số", "Cooling water to lube oil cooler",
    "Cấp/hồi nước cho bộ làm mát dầu hộp số.", "pipe", pipes_bb(LH, 20), "hose",
    [("util_cw_supply_riser", "nhánh T (cấp)", LH[0][0]), ("util_cw_return_riser", "nhánh T (hồi)", LH[1][0]),
     ("lube_oil_cooler", "cổng F2/F4", LH[0][-1])], "web-03 (ống mềm đen vào bộ làm mát)",
    ["2 ống mềm DN25 chạy ngoài mép +Y của khung: cấp ở Y 1 060, Z 380; hồi ở Y 1 130, Z 440; lên và vào cổng F2/F4 của bộ làm mát.",
     "Van bi tay đỏ trên mỗi ống ngay trước bộ làm mát; van điều nhiệt nước trên ống hồi."],
    paths_mm=[lp(pa) for pa in LH], radius_mm=20, count=2)
MH = [[(-400, 1060, 250), (-3500, 1060, 250), (-3500, 1060, 2300), (-3500, 575, 2300)],
      [(-500, 1130, 150), (-3700, 1130, 150), (-3700, 1130, 2400), (-3700, 575, 2400)]]
add("util_cw_motor_hoses", "util", "Ống nước bộ làm mát động cơ", "Cooling water to motor top cooler",
    "Cấp/hồi nước cho bộ làm mát gió–nước trên nóc động cơ chính (IC81W).", "pipe", pipes_bb(MH, 24), "stainless",
    [("util_cw_supply_riser", "nhánh T (cấp)", MH[0][0]), ("util_cw_return_riser", "nhánh T (hồi)", MH[1][0]),
     ("drive_motor", "bích DN40 trên mặt +Y bộ làm mát", MH[0][-1])],
    "review-01 M9; giả định (≈ 45 kW nhiệt, 2 × DN40)",
    ["2 ống inox DN40 (OD 48) chạy thấp ngoài mép +Y khung (cấp Y 1 060 Z 250, hồi Y 1 130 Z 150), dựng lên tại X −3 500 / −3 700 cạnh cụm dầu, rồi vào bích trên mặt +Y bộ làm mát động cơ ở Z 2 300 / 2 400; van bi tay đỏ ở mỗi ống."],
    paths_mm=[lp(pa) for pa in MH], radius_mm=24, count=2)
TH = [[(318, 980, 1000), (318, 980, 1550), (318, 210, 1550)],
      [(358, 980, 1000), (358, 980, 1600), (358, 210, 1600)]]
add("util_cw_throat_hoses", "util", "Ống nước áo hộp miệng nạp", "Cooling water to feed throat jacket",
    "Làm mát hộp miệng nạp để hạt không dính chảy ở miệng.", "pipe", pipes_bb(TH, 15), "hose",
    [("barrel_cw_valves", "cụm van 1 (nhánh thứ hai)", TH[0][0]), ("feed_throat", "2 đầu nối nước mặt +Y", TH[0][-1])],
    "review-01 I7; giả định", ["2 ống mềm inox DN20 từ đỉnh cụm van 1 lên Z 1 550/1 600 rồi vào mặt +Y hộp miệng nạp."],
    paths_mm=[lp(pa) for pa in TH], radius_mm=15, count=2)
SH = [[(1163, 980, 1000), (1300, 980, 1040), (1300, 900, 1070)],
      [(1203, 950, 1000), (1400, 950, 1040), (1400, 900, 1070)]]
add("util_cw_sidefeed_hoses", "util", "Ống nước áo side feeder", "Cooling water to side-feeder jacket",
    "Làm mát thân side feeder.", "pipe", pipes_bb(SH, 12), "hose",
    [("barrel_cw_valves", "cụm van 2 (nhánh thứ hai)", SH[0][0]), ("sidefeed_barrel", "2 đầu nối dưới thân", SH[0][-1])],
    "review-01 I7; giả định", ["2 ống mềm inox DN15 từ đỉnh cụm van 2 vào mặt dưới thân side feeder."],
    paths_mm=[lp(pa) for pa in SH], radius_mm=12, count=2)
VH = [[(4460, -2450, 0), (4460, -2450, 1000), (4420, -2600, 1000)],
      [(4460, -2950, 0), (4460, -2950, 1100), (4420, -2800, 1100)],
      [(4470, -2350, 0), (4470, -2350, 400), (4500, -2350, 400)],
      [(4470, -3050, 0), (4470, -3050, 400), (4500, -3050, 400)]]
add("util_cw_vac_hoses", "util", "Ống nước cụm chân không", "Cooling water to vacuum separator and pump skid",
    "Cấp/hồi nước cho ống xoắn ngưng của bình tách và cho bơm Roots/bơm khô làm mát nước.", "pipe", pipes_bb(VH, 16), "stainless",
    [("ctx_floor", "đầu nối nước nhà máy dưới sàn", VH[0][0]), ("vac_separator", "cổng ống xoắn", VH[0][-1]),
     ("vac_pump_unit", "ống góp nước skid", VH[2][-1])],
    "review-01 I7; giả định (lấy nước nhà máy tại chỗ qua hai đầu nối sàn, không băng qua máy)",
    ["4 ống inox DN25 (OD 32) đứng lên từ hai cặp đầu nối sàn giữa bình tách và skid: cặp cho bình tách vào Z 1 000 / ra Z 1 100, cặp cho skid vào/ra ở Z 400; van bi tay đỏ ở chân mỗi ống."],
    paths_mm=[lp(pa) for pa in VH], radius_mm=16, count=4)
AD = [(9360, -1705, 4500), (9360, -1705, 900)]
add("util_air_drop", "util", "Ống khí nén xuống khuôn", "Compressed-air drop at die",
    "Cấp khí nén 6 bar từ đường trên cao cho làm mát bulông nhiệt.", "pipe", pipe_bb(AD, 15), "galv",
    [("util_frl", "đầu nối ren", AD[-1])], "c054 (bulông nhiệt có làm mát gió); giả định",
    ["Ống thép mạ Ø30, đầu trên để hở 'từ đường khí nhà máy'."], path_mm=lp(AD), radius_mm=15)
add("util_frl", "util", "Bộ lọc–điều áp khí nén (khuôn)", "Air filter-regulator at die (FRL)",
    "Lọc, điều áp khí làm mát bulông nhiệt.", "composite", bb(9300, 9420, -1760, -1650, 650, 900), "stainless",
    [("die_junction_box", "giá gá mặt +X hộp khuôn", (9300, -1705, 775)), ("util_air_drop", "cổng vào", (9360, -1705, 900)),
     ("util_air_hose_die", "cổng ra", (9360, -1650, 880))], "giả định", ["Bộ lọc + van điều áp + đồng hồ, van khoá tay."])
AH = [(9360, -1650, 880), (9360, -1500, 880), (9360, -1500, 1600), (9290, -1500, 1600), (9290, -1240, 1600), (9290, -1240, 1540)]
add("util_air_hose_die", "util", "Ống khí làm mát bulông nhiệt", "Cooling-air hose to thermal bolts",
    "Dẫn khí làm mát tới ống gió của thanh bulông nhiệt.", "pipe", pipe_bb(AH, 12), "black",
    [("util_frl", "cổng ra", AH[0]), ("die_bolt_actuator_rail", "đầu nối khí", AH[-1])],
    "web-18 (ống gió làm mát đen tại môi khuôn)", ["Ống mềm PU Ø24, khớp nối nhanh ở đầu thanh để tách khuôn."],
    path_mm=lp(AH), radius_mm=12)
AD2 = [(-300, -2600, 4500), (-300, -2600, 1600)]
add("util_air_drop_2", "util", "Ống khí nén xuống cột sàn", "Compressed-air drop at mezzanine column",
    "Cấp khí nén cho van chân không và thiết bị cấp liệu.", "pipe", pipe_bb(AD2, 15), "galv",
    [("util_frl_2", "đầu nối ren", AD2[-1])], "review-01 M10; giả định",
    ["Ống thép mạ Ø30 dọc cột sàn X −450, Y −2 600, xuyên sàn; đầu trên để hở 'từ đường khí nhà máy'."], path_mm=lp(AD2), radius_mm=15)
add("util_frl_2", "util", "Bộ lọc–điều áp khí nén (cấp liệu, chân không)", "Air filter-regulator at mezzanine column",
    "Lọc, điều áp khí cho van bướm chân không, van nạp máy hút liệu, van cân.", "composite",
    bb(-350, -250, -2660, -2540, 1350, 1600), "stainless",
    [("feed_platform_columns_rear", "giá gá mặt +X cột", (-350, -2600, 1475)), ("util_air_drop_2", "cổng vào", (-300, -2600, 1600)),
     ("util_air_tube_vac", "cổng ra", (-250, -2600, 1500)), ("util_air_tube_loader", "cổng ra", (-300, -2540, 1600))],
    "review-01 M10; giả định", ["Bộ lọc + van điều áp + đồng hồ, van khoá tay, cao 1,35–1,6 m."])
AT1 = [(-250, -2600, 1500), (-250, -2450, 1500), (-250, -2450, 2450), (3950, -2450, 2450), (3950, -250, 2450),
       (3950, -250, 2180), (4020, -250, 2180)]
add("util_air_tube_vac", "util", "Ống khí tới van chân không", "Air tube to vacuum valve actuator",
    "Cấp khí cho bộ tác động van bướm chân không vùng 2.", "pipe", pipe_bb(AT1, 6), "black",
    [("util_frl_2", "cổng ra", AT1[0]), ("vac_valve", "bộ tác động", AT1[-1])], "review-01 M10; giả định",
    ["Ống PU Ø12 đi trên máng nhỏ dưới sàn thao tác ở Z 2 450 rồi tới bộ tác động van."], path_mm=lp(AT1), radius_mm=6)
AT2 = [(-300, -2540, 1600), (-300, -2540, 3050), (-300, -500, 3050), (-300, -500, 5000), (-300, -320, 5000)]
add("util_air_tube_loader", "util", "Ống khí tới máy hút liệu", "Air tube to vacuum loader",
    "Cấp khí cho van lật xả của máy hút liệu và van nạp của cân.", "pipe", pipe_bb(AT2, 6), "black",
    [("util_frl_2", "cổng ra", AT2[0]), ("feed_vacuum_loader", "van lật xả", AT2[-1])], "review-01 M10; giả định",
    ["Ống PU Ø12 lên dọc cột, đi trên mặt sàn, rồi dọc phễu cân lên van máy hút liệu."], path_mm=lp(AT2), radius_mm=6)

# =========================================================== CONTEXT
add("ctx_floor", "context", "Sàn nhà xưởng", "Workshop floor", "Mặt bằng đặt máy (Z = 0).", "box",
    bb(-7000, 13500, -5500, 3500, -20, 0), "floor", [("base_feet", "nền bê tông", (-300, 900, 0))],
    "BRIEF (Z = 0 sàn)", ["Tấm phẳng xám, có vạch vàng lối đi quanh máy (tuỳ chọn)."])
ROLL_Z = {"bottom": 799, "middle": 1601, "top": 2403}
prof_roll = [[0, 0], [150, 0], [150, 300], [400, 300], [400, 2900], [150, 2900], [150, 3200], [0, 3200]]
for nm, zc in ROLL_Z.items():
    conn = [("ctx_roll_stand", "gối đỡ trục trong khung", (ROLL_X, 1500, zc))]
    if nm == "middle":
        conn.append(("ctx_sheet", "tấm ôm trục giữa", (ROLL_X, 0, 1201)))
    if nm == "top":
        conn.append(("ctx_sheet", "tấm ôm nửa −X trục trên", (ROLL_X - ROLL_R, 0, 2403)))
    add(f"ctx_roll_{nm}", "context", f"Trục cán láng {('dưới' if nm == 'bottom' else 'giữa' if nm == 'middle' else 'trên')}",
        f"Polishing roll ({nm})", "Làm nguội và cán bóng tấm nhựa.", "revolve",
        bb(ROLL_X - ROLL_R, ROLL_X + ROLL_R, -1600, 1600, zc - ROLL_R, zc + ROLL_R), "chrome", conn,
        "c046 (Ø 400–800), c044 (PlanetCalender 3 trục); DECISIONS 10 (khe trục giữa–dưới tại cao độ môi khuôn)",
        ["Trục Ø800 mặt 2 600 (Y ±1 300) mạ crôm gương, cổ trục Ø300 tới Y ±1 600, tâm X = 9 776, Z = " + str(zc) + "."],
        axis="Y", center_mm=[ROLL_X, 0, zc], radius_mm=ROLL_R, length_mm=3200, profile_mm=prof_roll)
add("ctx_roll_stand", "context", "Khung cụm trục cán", "Roll stack stand",
    "Đỡ 3 trục, chỉnh khe trục, chạy trên ray để lùi xa khuôn.", "frame",
    bb(9540, 11200, -1750, 1750, 60, 3100), "frame",
    [("ctx_roll_middle", "gối trục", (ROLL_X, 1500, 1601)), ("ctx_roll_rails", "bánh xe", (10000, 1550, 60))],
    "p24-25 (khung đứng sau trục), web-09 (khung trắng dải xanh KM); kích thước giả định specs §6",
    ["2 khung bên dày 350 tại Y ±(1 400…1 750), dầm ngang phía sau, xi lanh ép khe trục, dải xanh KM có chữ KraussMaffei.",
     "Mép trước khung bên ở X 9 540 tại gối trục dưới và trục giữa, nhưng lõm vào tới X 9 800 trong dải Z 1 060–1 340 quanh khe trục, để núm deckle và tấm đầu khuôn có khe hở thật (≈ 280 mm).",
     "outline_mm là hình bên của khung +Y (Y 1 400…1 750); khung −Y đối xứng qua Y = 0."],
    outline_mm={"plane": "XZ", "d0": 1400, "d1": 1750,
                "pts": [[9540, 60], [11200, 60], [11200, 3100], [9540, 3100], [9540, 1340], [9800, 1340],
                        [9800, 1060], [9540, 1060]]})
add("ctx_roll_drives", "context", "Động cơ trục cán", "Roll drives", "Quay 3 trục cán.", "composite",
    bb(9551, 10001, -2350, -1750, 549, 2653), "white", [("ctx_roll_stand", "mặt bích", (9776, -1750, 1600))],
    "p24-25 (3 khối nhỏ sau khung)", ["3 động cơ hộp số 450 × 600 × 500 phía −Y, đồng trục với từng trục cán."],
    count=3, item_mm=[450, 600, 500], positions_mm=[[ROLL_X, -2050, z] for z in (799, 1601, 2403)])
add("ctx_roll_rails", "context", "Ray cụm trục cán", "Roll stack floor rails", "Cho cụm trục lùi theo +X.", "frame",
    bb(9550, 12500, -1580, 1580, 0, 60), "steel",
    [("ctx_roll_stand", "bánh xe", (10000, 1550, 60)), ("ctx_floor", "bulông neo", (10000, 1550, 0))],
    "specs §6 (lùi 1 000–1 500 mm)", ["2 ray 60 × 60 dài 2 950 tại Y = ±1 550."],
    count=2, item_mm=[2950, 60, 60], positions_mm=[[11025, -1550, 30], [11025, 1550, 30]])
def _arc_pts(cx, cz, r, angs):
    return [(r1(cx + r * math.cos(math.radians(a))), 0, r1(cz + r * math.sin(math.radians(a)))) for a in angs]


SHEET = ([(LIP_X, 0, 1200)] + _arc_pts(ROLL_X, 1601, 401, [-90, -45, 0, 45, 90])
         + _arc_pts(ROLL_X, 2403, 401, [225, 180, 135, 90])[0:4] + [(10400, 0, 2804)])
add("ctx_sheet", "context", "Màn nhựa / tấm", "Melt curtain and sheet",
    "Màn nhựa từ môi khuôn vào khe trục giữa–dưới, ôm nửa +X trục giữa, ôm nửa −X trục trên rồi ra theo +X (đường chữ S).", "sheet",
    bb(9375, 10400, -1050, 1050, 1199, 2805), "glass",
    [("die_flex_lip", "khe môi", (LIP_X, 0, 1200)), ("ctx_roll_middle", "ôm trục", (ROLL_X, 0, 1201)),
     ("ctx_roll_top", "ôm trục", (ROLL_X - ROLL_R, 0, 2403))],
    "pdf_measures §5 và p24-25_slot_die_smoothing_roll (đường tấm chữ S); specs §0 (tấm 2 100); review-01 M7",
    ["Tấm rộng 2 100, dày 1 mm; đường tâm trong path_mm (mặt XZ, Y = 0): môi khuôn (9 576, 1 200) → khe trục (9 776, 1 200) → ôm nửa +X trục giữa tới đỉnh (9 776, 2 002) → ôm nửa −X trục trên (qua X 9 375) tới đỉnh (9 776, 2 804) → ra +X ở Z 2 804.",
     "Đầu đo chiều dày quét ngang (traversing gauge) cho điều khiển profin đặt sau cụm trục, không dựng."],
    col="#7FB6C9", path_mm=lp(SHEET), width_mm=2100)

# =========================================================== CONNECTIONS
CONN = []


def con(cid, a, b, medium, typ, path):
    CONN.append({"id": cid, "from": a, "to": b, "medium": medium, "type": typ,
                 "path_mm": [[r1(v) for v in p] for p in path]})


CAB = (-1000, -3800, 100)        # inside the control cabinet, at its floor-duct entry
con("melt_01", "barrel_b6", "melt_head_adapter", "melt", "bích 20 × M24, lỗ số 8 → tròn", [(5600, 0, 1200), (5746, 0, 1200), (5850, 0, 1200)])
con("melt_02", "melt_head_adapter", "melt_startup_valve", "melt", "12 vít M24 từ phía van", [(5900, 0, 1200), (5996, 0, 1200), (6100, 0, 1200)])
con("melt_03", "melt_startup_valve", "melt_screen_changer", "melt", "12 vít M24 từ phía van (PCD 360) → bích Ø420 → 8 × M30 PCD 360 vào bộ lọc; lòng Ø120; qua melt_sc_adapter_in (P2)", [(6300, 0, 1200), (6446, 0, 1200), (6596, 0, 1200), (6700, 0, 1200)])
con("melt_04", "melt_startup_valve", "melt_purge_cart", "melt", "vị trí khởi động: xả xuống máng", [(6221, 0, 1100), (6221, 0, 940), (6221, 0, 520), (6221, 0, 300)])
con("melt_05", "melt_screen_changer", "melt_gear_pump", "melt", "bích Ø360, 8 × M30 PCD 300 ra bộ lọc / 8 × M24 PCD 300 vào bơm; lòng Ø110 → Ø100; qua melt_pump_adapter_in (P3)", [(7200, 0, 1200), (7301, 0, 1200), (7476, 0, 1200), (7600, 0, 1200)])
con("melt_06", "melt_gear_pump", "melt_static_mixer", "melt", "bích Ø300, 8 × M24 PCD 250, lòng Ø100; qua adapter ra (P4, đĩa nổ 2) và ống gia nhiệt", [(7800, 0, 1200), (7926, 0, 1200), (8076, 0, 1200), (8426, 0, 1200), (8600, 0, 1200)])
con("melt_07", "melt_static_mixer", "die_body_upper", "melt", "bích Ø300, 8 × M24 PCD 250 → bích chữ nhật 500 × 360, 8 × M30 vào khuôn; lòng Ø100; qua melt_die_adapter (P5/T5) vào ống phân phối", [(8800, 0, 1200), (8926, 0, 1200), (9126, 0, 1200), (9300, 0, 1200)])
con("melt_08", "die_flex_lip", "ctx_sheet", "melt", "khe môi 2 400 → màn nhựa vào khe trục", [(9500, 0, 1200), (9576, 0, 1200), (9776, 0, 1200)])
con("melt_09", "melt_screen_changer", "melt_sc_backflush", "melt", "nhựa xả ngược ra máng", [(6950, 300, 1250), (6950, 700, 1250)])
con("mat_01", "feed_conveying_line", "feed_vacuum_loader", "material", "hút khí nén chân không", [(-450, 700, 6300), (-450, 700, 5500), (-450, 320, 5500)])
con("mat_02", "feed_vacuum_loader", "feed_main_feeder", "material", "rơi tự do qua phễu", [(-450, 0, 5000), (-450, 0, 3700), (-450, 0, 3200)])
con("mat_03", "feed_main_feeder", "barrel_b1", "material", "ống mềm cách cân → ống rơi → ống mềm → phễu → miệng nạp", [(-450, 0, 3100), (-450, 0, 2850), (-450, 0, 2550), (90, 0, 2010), (200, 0, 1900), (340, 0, 1640), (340, 0, 1400)])
con("mat_04", "feed_additive_feeder", "feed_downpipe", "material", "ống mềm cách cân → ống phụ gia → nhánh Y", [(-650, 850, 3200), (-650, 850, 2850), (-650, 850, 2700), (-450, 125, 2700)])
con("mat_05", "sidefeed_feeder", "barrel_b2", "material", "ống mềm cách cân → ống rơi → side feeder → cửa bên", [(1350, 950, 3200), (1350, 950, 2850), (1350, 950, 1600), (1350, 950, 1200), (1350, 330, 1200), (1350, 200, 1200)])
con("w_01", "util_cw_supply_riser", "barrel_cw_valves", "water", "DN50 nước cấp", [(-400, 1060, 0), (-400, 1060, 710), (-400, 880, 710), (338, 880, 710)])
con("w_02", "barrel_cw_valves", "barrel_b4", "water", "ống mềm DN15 vào đầu nối 45° dưới +Y tại X = đầu đoạn + 200 (tương tự các đoạn khác; B1 ở đáy X 200)", [(3171, 910, 1000), (2904, 560, 980), (2904, 230, 1000), (2904, 184, 1016)])
con("w_03", "barrel_b4", "barrel_cw_return", "water", "ống mềm ra tại X = cuối đoạn − 200 qua cụm van về ống hồi", [(3518, 184, 1016), (3518, 230, 1000), (3518, 560, 980), (3251, 910, 1000), (3251, 950, 800)])
con("w_04", "barrel_cw_return", "util_cw_return_riser", "water", "DN50 nước hồi", [(0, 950, 800), (-300, 950, 800), (-500, 950, 800), (-500, 1130, 800), (-500, 1130, 0)])
con("w_05", "util_cw_supply_riser", "lube_oil_cooler", "water", "ống mềm DN25 cấp/hồi bộ làm mát dầu", [(-400, 1060, 380), (-2815, 1060, 380), (-2815, 1060, 820), (-2815, 900, 820)])
con("w_06", "barrel_cw_valves", "feed_throat", "water", "2 ống mềm DN20 tới áo hộp miệng nạp", [(318, 980, 1000), (318, 980, 1550), (318, 210, 1550)])
con("w_07", "barrel_cw_valves", "sidefeed_barrel", "water", "2 ống mềm DN15 tới áo side feeder", [(1163, 980, 1000), (1300, 980, 1040), (1300, 900, 1070)])
con("w_08", "ctx_floor", "vac_separator", "water", "đầu nối nước sàn → ống xoắn bình tách", [(4460, -2450, 0), (4460, -2450, 1000), (4420, -2600, 1000)])
con("w_09", "ctx_floor", "vac_pump_unit", "water", "đầu nối nước sàn → ống góp skid bơm", [(4470, -2350, 0), (4470, -2350, 400), (4500, -2350, 400)])
con("w_10", "util_cw_supply_riser", "drive_motor", "water", "2 ống DN40 tới bộ làm mát gió–nước trên nóc động cơ", [(-400, 1060, 250), (-3500, 1060, 250), (-3500, 1060, 2300), (-3500, 575, 2300)])
con("v_01", "barrel_vent_dome", "vac_pump_unit", "vacuum", "DN150 qua nắp vòm, Z 2 300 → bình tách → DN100 → Roots", [(4120, 0, 1900), (4120, 0, 2150), (4120, 0, 2300), (4120, -2700, 2300), (4120, -2700, 1900), (4420, -2700, 1600), (4860, -2700, 1600), (4860, -2700, 1400)])
con("v_02", "vac_pump_unit", "vac_exhaust", "vacuum", "khí xả sau bơm", [(6150, -3100, 1400), (6150, -3100, 3500)])
con("v_03", "barrel_b3", "barrel_vent_dome_2", "vacuum", "hơi nước từ lỗ thoát khí B3 vào vòm vùng 1", [(2150, 0, 1300), (2150, 0, 1800)])
con("v_04", "vac_separator", "vac_drain", "water", "nước ngưng qua van trên vào nồi xả", [(4120, -2700, 600), (4120, -2700, 200)])
con("v_05", "barrel_vent_dome_2", "vac_separator", "vacuum", "DN100 qua van chặn, ống xếp, Z 2 250, van tiết lưu → cổng bên bình tách (≈ 50 mbar)", [(2150, 0, 1800), (2150, -240, 1800), (2150, -560, 1800), (2150, -560, 2250), (2150, -2700, 2250), (3700, -2700, 2250), (3700, -2700, 1400), (3900, -2700, 1400)])
con("o_01", "gearbox", "lube_pump_motor", "oil", "ống hút DN40 từ carter", [(-1500, 690, 760), (-1500, 975, 760), (-3350, 975, 760), (-3350, 940, 760)])
con("o_02", "lube_pump_motor", "gearbox", "oil", "bơm → lọc kép → làm mát → ống DN32 → vòi phun", [(-3350, 800, 1000), (-3075, 800, 1000), (-2775, 775, 900), (-2775, 775, 1500), (-2000, 775, 1500), (-2000, 690, 1500)])
con("h_01", "melt_hpu", "melt_sc_drive", "hydraulic", "2 ống mềm P/T", [(6860, -2100, 1100), (6860, -2000, 1150), (6860, -1085, 1150), (6860, -900, 1150)])
con("h_02", "melt_hpu", "melt_startup_cyl", "hydraulic", "2 ống mềm", [(6460, -2100, 1000), (6460, -2000, 1080), (6460, -1000, 1080), (6221, -860, 1170), (6221, -700, 1200)])
con("p_01", "ctrl_drive_cabinet", "drive_motor_terminal_box", "power", "cáp trung thế 3 kV trong hào rồi dựng lên", [(-4000, -3800, 100), (-4000, -3700, 5), (-4000, -1100, 5), (-4000, -1100, 1150), (-4000, -900, 1150)])
con("p_02", "ctrl_heater_cabinet", "barrel_heater_jboxes", "power", "cáp nhiệt qua hào, máng đứng, máng trên khung", [CAB, (-1000, -3700, 5), (-1000, -1050, 5), (-1000, -1050, 700), (-990, -900, 700), (338, -900, 700), (338, -650, 800)])
con("p_03", "ctrl_heater_cabinet", "die_junction_box", "power", "cáp nhiệt khuôn qua hào và nhánh hào", [CAB, (-1000, -1150, 5), (8600, -1150, 5), (8600, -1600, 5), (8800, -1750, 300)])
con("p_04", "ctrl_heater_cabinet", "melt_pump_motor", "power", "cáp động lực qua hào", [CAB, (-1000, -1150, 5), (7700, -1150, 5), (7700, -1290, 900), (7700, -1400, 1700)])
con("p_05", "ctrl_heater_cabinet", "vac_control_box", "power", "cáp động lực qua hào", [CAB, (-1000, -1150, 5), (6100, -1150, 5), (6100, -2050, 5), (6100, -2100, 1000)])
con("p_06", "ctrl_heater_cabinet", "melt_hpu", "power", "cáp động lực qua hào", [CAB, (-1000, -1150, 5), (6800, -1150, 5), (6800, -2050, 600)])
con("p_07", "ctrl_heater_cabinet", "sidefeed_motor", "power", "cáp qua kênh ngang trong khung đế", [CAB, (-1000, -1050, 5), (-1000, 0, 300), (1350, 0, 300), (1350, 1300, 300), (1350, 1750, 1000)])
con("p_08", "ctrl_heater_cabinet", "feed_control_cabinet", "power", "cáp theo cột sàn lên tủ cân", [CAB, (-1000, -3700, 5), (-1000, -2600, 5), (-450, -2600, 30), (-450, -2600, 2900), (-2100, 1200, 3100)])
con("p_09", "ctrl_machine_cabinet", "lube_pump_motor", "power", "cáp động cơ bơm dầu", [(-5300, 400, 700), (-5150, 400, 700), (-3350, 800, 700), (-3350, 800, 900)])
con("p_10", "ctrl_heater_cabinet", "melt_heater_jbox", "power", "cáp nhiệt đường chảy (≈ 75 kW) qua hào", [CAB, (-1000, -1150, 5), (6950, -1150, 5), (6950, -850, 200)])
con("p_11", "ctrl_die_bolt_cabinet", "die_junction_box", "power", "cáp 94 mạch bulông nhiệt qua kênh đế tủ, hào chính, nhánh hào", [(1200, -4000, 100), (-1000, -4000, 50), (-1000, -3700, 5), (-1000, -1150, 5), (8600, -1150, 5), (8600, -1600, 5), (8900, -1750, 300)])
con("s_01", "ctrl_hmi", "ctrl_heater_cabinet", "signal", "Ethernet/Profinet qua kênh khung đế", [(-1300, 1500, 100), (-1300, 1500, 10), (-1300, 1050, 10), (-1000, 0, 300), (-1000, -1050, 5), (-1000, -3700, 5), CAB])
con("s_02", "drive_encoder", "ctrl_drive_cabinet", "signal", "cáp encoder theo hào trung thế (ống riêng)", [(-5025, 0, 1200), (-5025, -1060, 1200), (-4100, -1100, 10), (-4100, -3700, 5), (-4100, -3800, 500)])
con("s_03", "melt_sensor_head", "ctrl_heater_cabinet", "signal", "cáp cảm biến P1…P5/T qua hào", [(5896, 0, 1650), (5896, -1150, 1650), (5896, -1150, 5), (-1000, -1150, 5), (-1000, -3700, 5), CAB])
con("s_04", "barrel_thermocouples", "barrel_heater_jboxes", "signal", "cáp bù cặp nhiệt", [(2450, 0, 1500), (2450, -400, 1400), (2450, -600, 900)])
con("s_05", "ctrl_machine_cabinet", "ctrl_signal_tower", "signal", "cáp đèn", [(-5400, 0, 1900), (-5400, 0, 2100)])
con("s_06", "ctrl_estops", "ctrl_heater_cabinet", "signal", "mạch an toàn dừng khẩn (cả nút trên sàn thao tác)", [(600, 940, 1120), (600, 940, 700), (-1000, 0, 300), (-1000, -1050, 5), (-1000, -3700, 5), CAB])
con("s_07", "die_bolt_actuator_rail", "die_junction_box", "signal", "cáp bulông nhiệt + cặp nhiệt (phích cắm)", [(9290, -1250, 1495), (9290, -1450, 1495), (9290, -1450, 1100), (9100, -1650, 1000)])
con("s_08", "melt_rupture_disc_2", "ctrl_heater_cabinet", "signal", "tín hiệu đứt đĩa nổ 2 + P4 qua hào", [(8001, -260, 1200), (8001, -1150, 1200), (8001, -1150, 5), (-1000, -1150, 5), (-1000, -3700, 5), CAB])
con("s_09", "ctrl_estop_platform", "ctrl_estops", "signal", "nút dừng khẩn sàn thao tác nối vào mạch an toàn theo cột sàn", [(-450, 1380, 4000), (-450, 1300, 3000), (-450, 1300, 300), (600, 940, 700), (600, 940, 1100)])
DRV = (-1700, -4000, 500)       # inside the MV drive cabinet, next to the control cabinet
con("s_10", "ctrl_heater_cabinet", "ctrl_drive_cabinet", "signal", "Profinet + STO nối cứng từ rơ-le an toàn (dừng khẩn, P1 HH, đĩa nổ, khoá liên động truyền động)", [(-1500, -4000, 1800), (-1700, -4000, 1800)])
con("s_11", "melt_sensor_head", "ctrl_drive_cabinet", "signal", "P1 HH 350 bar → ngắt cứng truyền động chính", [(5896, 0, 1650), (5896, -1150, 1650), (5896, -1150, 5), (-1000, -1150, 5), (-1000, -3700, 5), (-1000, -4000, 50), DRV])
con("s_12", "melt_rupture_disc", "ctrl_drive_cabinet", "signal", "tín hiệu đứt đĩa nổ 1 → ngắt truyền động chính", [(5896, -330, 1200), (5896, -1150, 1200), (5896, -1150, 5), (-1000, -1150, 5), (-1000, -3700, 5), (-1000, -4000, 50), DRV])
con("s_13", "melt_rupture_disc_2", "ctrl_drive_cabinet", "signal", "tín hiệu đứt đĩa nổ 2 → ngắt truyền động chính và bơm", [(8001, -270, 1200), (8001, -1150, 1200), (8001, -1150, 5), (-1000, -1150, 5), (-1000, -3700, 5), (-1000, -4000, 50), DRV])
con("s_14", "lube_pipe_pressure", "ctrl_machine_cabinet", "signal", "công tắc áp dầu (PS) + PT100 dầu hộp số → khoá khởi động truyền động", [(-2775, 775, 1300), (-2775, 1000, 1300), (-5300, 1000, 1300), (-5300, 400, 1300)])
con("s_15", "drive_coupling_guard", "ctrl_machine_cabinet", "signal", "công tắc liên động vỏ che khớp nối", [(-2640, 450, 1500), (-2640, 1000, 1500), (-5300, 1000, 1500), (-5300, 400, 1500)])
con("s_16", "drive_safety_coupling", "ctrl_machine_cabinet", "signal", "công tắc giám sát nhả khớp an toàn", [(-2500, 300, 1500), (-2500, 1000, 1550), (-5300, 1000, 1550), (-5300, 400, 1550)])
con("s_17", "ctrl_machine_cabinet", "ctrl_heater_cabinet", "signal", "I/O tại chỗ (dầu, vỏ che, khớp an toàn) về PLC qua kênh khung đế", [(-5300, 0, 400), (-5150, 0, 400), (-1000, 0, 300), (-1000, -1050, 5), (-1000, -3700, 5), CAB])
con("s_18", "ctrl_estop_die", "ctrl_heater_cabinet", "signal", "nút dừng khẩn khuôn (+Y) vào mạch an toàn qua hộp đấu dây khuôn", [(9250, 1450, 1100), (9250, 1210, 350), (9250, -1100, 350), (9000, -1600, 300), (8600, -1500, 5), (8600, -1150, 5), (-1000, -1150, 5), (-1000, -3700, 5), CAB])
con("s_19", "ctrl_estop_melt", "ctrl_heater_cabinet", "signal", "nút dừng khẩn bộ lọc (+Y) vào mạch an toàn qua hộp nhiệt đường chảy", [(7320, 650, 1100), (7320, 620, 300), (7320, -600, 300), (6950, -850, 300), (6950, -1150, 5), (-1000, -1150, 5), (-1000, -3700, 5), CAB])
con("s_20", "melt_sensor_p3", "ctrl_heater_cabinet", "signal", "PT-P3 → PIC trong PLC → biến tần bơm nhựa (giữ áp hút ≈ 50 bar bằng tốc độ bơm)", [(7388, 0, 1600), (7388, -1150, 1600), (7388, -1150, 5), (-1000, -1150, 5), (-1000, -3700, 5), CAB])
con("p_12", "ctrl_infeed_mv", "ctrl_drive_cabinet", "power", "cáp trung thế 3 kV từ trạm biến áp (≈ 1,8 MVA)", [(-3400, -5100, 5), (-3400, -4900, 5), (-3400, -4800, 300)])
con("p_13", "ctrl_infeed_lv", "ctrl_heater_cabinet", "power", "cáp hạ thế 400 V 3 pha từ tủ phân phối nhà máy (≈ 500 kVA)", [(-400, -4500, 5), (-400, -4300, 5), (-400, -4200, 300)])
con("m_01", "drive_motor", "screws", "mechanical", "trục động cơ → khớp đàn hồi → khớp an toàn → hộp số → then hoa → trục vít", [(-3100, 0, 1200), (-2950, 0, 1200), (-2700, 0, 1200), (-2300, 0, 1200), (-750, 0, 1200), (-400, 0, 1200), (0, 0, 1200), (300, 0, 1200)])
con("m_02", "melt_pump_motor", "melt_gear_pump", "mechanical", "động cơ đứng → hộp góc → các-đăng → trục bơm", [(7701, -1525, 1800), (7701, -1525, 1250), (7701, -1300, 1250), (7701, -300, 1250), (7701, -200, 1250)])
con("m_03", "sidefeed_motor", "sidefeed_barrel", "mechanical", "động cơ → hộp số → 2 trục vít", [(1350, 1800, 1200), (1350, 1100, 1200), (1350, 900, 1200)])
con("a_01", "util_air_drop", "die_bolt_actuator_rail", "air", "khí nén 6 bar → FRL → ống PU → ống gió bulông nhiệt", [(9360, -1705, 4500), (9360, -1705, 900), (9360, -1650, 880), (9360, -1500, 1600), (9290, -1500, 1600), (9290, -1240, 1600), (9290, -1240, 1530)])
con("a_02", "util_air_drop_2", "vac_valve", "air", "khí nén → FRL cột sàn → ống Ø12 → bộ tác động van chân không", [(-300, -2600, 4500), (-300, -2600, 1600), (-250, -2600, 1500), (-250, -2450, 2450), (3950, -2450, 2450), (3950, -250, 2180), (4030, -250, 2180)])
con("a_03", "util_air_drop_2", "feed_vacuum_loader", "air", "khí nén → FRL cột sàn → ống Ø12 → van lật máy hút liệu", [(-300, -2600, 4500), (-300, -2600, 1600), (-300, -2540, 3050), (-300, -500, 3050), (-300, -500, 5000), (-300, -320, 5000)])

# =========================================================== WRITE
META = {
    "units": "mm",
    "axes": "X flow, Y operator(+), Z up, X=0 barrel drive-side face",
    "version": 1,
    "machine": "KraussMaffei Berstorff ZE 155 A UT, L/D 34, PET direct sheet line with horizontal T-die",
    "conventions": {
        "bbox_mm": "[x0, x1, y0, y1, z0, z1] axis-aligned, world mm",
        "center_mm": "bbox centre unless stated; for revolve/cyl it lies on the axis",
        "profile_mm": "[[r, h], ...] revolved about `axis` through center_mm; h measured from the bbox face at the minimum end of that axis",
        "outline_mm": "polygon in `plane` (XZ: u=X, v=Z; YZ: u=Y, v=Z; XY: u=X, v=Y), extruded along the remaining axis from d0 to d1; closed unless closed=false",
        "path_mm": "pipe/hose/cable centreline polyline, radius_mm = outer radius",
        "count/positions_mm/pitch_mm/item_mm": "repeated items in one entry; bbox is the union; positions_mm are item centres; item_mm is the axis-aligned size of one item (X, Y, Z), except when item_axis (one axis for all items) or item_axes (one per item) is given: then item_mm = [diameter, diameter, length] in the item's own frame, length along that axis",
        "beams_mm": "structural members of a frame part: id, section, centreline from/to (feed_platform_deck)",
        "paths_mm": "for pipe entries with count > 1: one centreline polyline per hose/conduit (radius_mm each)",
        "width_mm": "sheet width across its path (ctx_sheet)",
        "group_to_collection": "ze155_<group>; group 'context' -> ze155_context",
        "medium": "melt|water|vacuum|oil|hydraulic|power|signal|material|mechanical, plus 'air' for compressed air",
    },
    "groups": GROUPS,
    "palette": COL,
}


def main():
    data = {"meta": META, "parts": PARTS, "connections": CONN}
    (HERE / "parts.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    write_md()
    print(f"parts: {len(PARTS)}  connections: {len(CONN)}")


def fmt_pt(p):
    return "(" + ", ".join(f"{v:g}" for v in p) + ")"


def part_md(p):
    b = p["bbox_mm"]
    L, W, H = b[1] - b[0], b[3] - b[2], b[5] - b[4]
    lines = [f"#### `{p['id']}` — {p['name_vi']} ({p['name_en']})", ""]
    lines.append(f"- **Chức năng:** {p['function']}")
    extra = ""
    if p.get("count"):
        extra = f"; số lượng {p['count']}"
    if p.get("pitch_mm"):
        extra += f", bước {p['pitch_mm']:g}"
    lines.append(f"- **Hình dạng / kích thước:** {p['shape']}; bao {L:g} × {W:g} × {H:g} (X × Y × Z){extra}"
                 + (f"; trục {p['axis']}" if p.get("axis") else "")
                 + (f"; R {p['radius_mm']:g}" if p.get("radius_mm") else ""))
    lines.append(f"- **Vị trí:** X {b[0]:g} … {b[1]:g}, Y {b[2]:g} … {b[3]:g}, Z {b[4]:g} … {b[5]:g}")
    lines.append(f"- **Vật liệu / màu:** {p['material']} `{p['colour_hex']}`")
    cs = "; ".join(f"`{c['part']}` – {c['interface']} tại {fmt_pt(c['at_mm'])}" for c in p["connects_to"])
    lines.append(f"- **Nối với:** {cs}")
    if p["details"]:
        lines.append("- **Chi tiết phải dựng:** " + " ".join(p["details"]))
    lines.append(f"- **Nguồn:** {p['source']}")
    lines.append("")
    return "\n".join(lines)


def write_md():
    md_path = HERE / "design.md"
    if not md_path.exists():
        return
    text = md_path.read_text()
    out = []
    for g, title in GROUPS.items():
        ps = [p for p in PARTS if p["group"] == g]
        out.append(f"### {title} — {len(ps)} mục\n")
        out.extend(part_md(p) for p in ps)
    parts_block = "\n".join(out)
    conn_lines = ["| id | từ | tới | môi chất | kiểu nối | số điểm đường đi |", "|---|---|---|---|---|---|"]
    for c in CONN:
        conn_lines.append(f"| `{c['id']}` | `{c['from']}` | `{c['to']}` | {c['medium']} | {c['type']} | {len(c['path_mm'])} |")
    conn_block = "\n".join(conn_lines)
    for tag, block in (("PARTS", parts_block), ("CONNECTIONS", conn_block)):
        b, e = f"<!-- BEGIN {tag} -->", f"<!-- END {tag} -->"
        if b in text and e in text:
            pre, rest = text.split(b, 1)
            _, post = rest.split(e, 1)
            text = pre + b + "\n" + block + "\n" + e + post
    md_path.write_text(text)


if __name__ == "__main__":
    main()
