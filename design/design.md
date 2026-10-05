# Thiết kế máy đùn trục vít đôi ZE 155 A UT, L/D 34, với đường chảy nhựa và khuôn chữ T nằm ngang

Tài liệu này là dữ liệu thiết kế để người vẽ (drafter) lập bản vẽ và người dựng (builder) dựng mô hình Blender. Mọi kích thước tính bằng mm.

Các tệp đi kèm trong `design/`:

| Tệp | Nội dung |
|---|---|
| `parts.json` | Danh mục 182 chi tiết và 59 mối nối, máy đọc được. Đây là dữ liệu chuẩn; khi có khác biệt thì `parts.json` đúng. |
| `build_parts.py` | Nguồn duy nhất của dữ liệu: sinh `parts.json` và điền lại mục 5 và bảng ở mục 6 của tài liệu này (`uv run -q python design/build_parts.py`). Muốn sửa chi tiết thì sửa tệp này rồi chạy lại. |
| `check_parts.py` | Kiểm tra lược đồ, đích nối, độ chạm tại điểm nối, không có chi tiết lơ lửng, chi tiết lặp lại phải có vị trí từng cái, ống phải có đường đi; in kích thước bao (`uv run -q python design/check_parts.py`). |
| `layout_preview.py`, `layout_preview.png` | Hình chiếu đứng và mặt bằng vẽ nhanh từ hộp bao, chỉ để kiểm tra bố trí bằng mắt. |

Quy ước dữ liệu hình học trong `parts.json` (cũng ghi ở `meta.conventions`):
- `bbox_mm` = [x0, x1, y0, y1, z0, z1], hộp bao thẳng trục theo hệ toạ độ thế giới.
- `profile_mm` = các cặp [r, h], xoay quanh trục `axis` đi qua `center_mm`. h đo từ mặt hộp bao ở đầu nhỏ của trục đó (ví dụ xi lanh B2: h = 0 tại X = 676).
- `outline_mm` = đa giác trong mặt phẳng `plane` (XZ: u = X, v = Z; YZ: u = Y, v = Z; XY: u = X, v = Y), đùn theo trục còn lại từ `d0` tới `d1`. Nếu `closed: false` thì là đường hở (lan can).
- `path_mm` + `radius_mm` = đường tâm ống, ống mềm, cáp và bán kính ngoài.
- Chi tiết lặp lại (bulông, băng nhiệt, chân đế, cột) gộp thành một mục: `count`, `pitch_mm`, `positions_mm` (tâm từng cái), `item_mm` (hộp bao thẳng trục của một cái). Khi đó `bbox_mm` là hộp bao chung của cả nhóm. Chi tiết có trục riêng có thêm `item_axis` (một trục chung, như bulông nhiệt) hoặc `item_axes` (mỗi cái một trục, như cặp nhiệt); khi đó `item_mm` = [Ø, Ø, dài] theo hệ trục riêng, chiều dài dọc trục đó.
- `beams_mm` (ở sàn thao tác): danh sách dầm với `id`, `section` và đường tâm `from` → `to`.
- Mục ống có `count` > 1 (bó ống mềm, ống luồn cáp) có `paths_mm`: mỗi ống một đường tâm riêng. Tấm nhựa (`ctx_sheet`) có `path_mm` là đường tâm trong mặt XZ và `width_mm`.
- Nhóm (`group`) ứng với collection Blender `ze155_<group>`; nhóm `context` vào `ze155_context`.
- Môi chất mối nối gồm melt, water, vacuum, oil, hydraulic, power, signal, material, mechanical. Có thêm `air` cho khí nén.

---

## 1. Máy và quy trình

**Máy:** KraussMaffei Berstorff ZE 155 A UT, máy đùn trục vít đôi đồng hướng (co-rotating twin-screw extruder). Đường kính vít 169 mm, khoảng cách tâm 142 mm. Chiều dài gia công (processing length) 34D = 5 746 mm, gồm 1 đoạn 4D và 5 đoạn 6D. Xi lanh dòng UT là trụ tròn có mặt bích hai đầu. Các đoạn nối nhau bằng mặt bích bắt bulông (bolted flange joint), như trên máy ZE UT cỡ lớn thật.

**Ứng dụng:** đùn tấm PET trực tiếp (direct sheet extrusion), không sấy, không kết tinh trước. Năng suất thiết kế 3 500 kg/h. Tấm thành phẩm rộng 2 100 mm, dày 0,3–1,5 mm. Khe môi khuôn rộng 2 400 mm.

**Dòng vật liệu theo thứ tự:**
1. Hạt PET được máy hút liệu (vacuum loader) đưa từ silo lên phễu cân trên sàn thao tác (mezzanine, Z = 3 000).
2. Cân cấp liệu theo khối lượng hao hụt (loss-in-weight feeder) định lượng 3 500 kg/h. Hạt rơi qua ống rơi, ống mềm và phễu có cổng nghiêng 45° vào miệng nạp xi lanh B1. B1 làm mát bằng nước.
3. Cân phụ gia trên sàn đổ phụ gia vào nhánh Y của ống rơi. Side feeder trục vít đôi ở phía người vận hành (+Y) ép liệu phụ vào cửa bên của B2: mảnh vụn biên tấm (edge trim) nghiền nhỏ, hoặc phụ gia dạng bột có tỷ trọng thấp.
4. Cuối B2 và đầu B3 có khối nhào (kneading block) làm chảy nhựa. Ngay sau đó vòm chân không vùng 1 trên B3 hút nhẹ (≈ 50 mbar) để rút phần lớn hơi nước trước khi PET bị thuỷ phân, và không cho không khí lọt vào nhựa nóng.
5. B4 trộn và đồng nhất. Cuối B4 có phần tử nghịch (left-handed element) tạo nút nhựa để bịt kín vùng chân không.
6. B5 hút chân không sâu (5–20 mbar) qua vòm chân không vùng 2 (vacuum vent dome) để khử nốt ẩm, acetaldehyde và oligome. Hơi của cả hai vùng đi vào một bình tách ngưng (condensate separator) rồi tới cụm bơm Roots kèm bơm khô; van tiết lưu trên đường vùng 1 giữ chênh lệch áp giữa hai vùng.
7. B6 tăng áp, đẩy nhựa qua đầu xi lanh (barrel head adapter) vào van khởi động (start-up/diverter valve). Khi khởi động, van xả nhựa xuống máng và xe hứng. Khi chạy, nhựa đi tiếp.
8. Bộ lọc lưới quay xả ngược (backflush screen changer) Gneuss RSFgenius 200 lọc nhựa qua lưới 60 µm, đổi lưới liên tục bằng tay quay thuỷ lực.
9. Bơm bánh răng (melt gear pump) Maag extrex6 GU 100/125 tạo áp ổn định ≈ 250 bar.
   - Lưu lượng do các cân loss-in-weight quyết định (máy trục vít đôi cấp thiếu, starve-fed); tốc độ trục vít chỉ đổi độ điền đầy và năng lượng nhập vào.
   - Cảm biến áp hút P3 điều khiển tốc độ bơm bánh răng (PT-P3 → PIC → biến tần bơm) để giữ áp vào bơm khoảng 50 bar. Nhờ đó trục vít chỉ cần tạo áp thấp, vùng chân không ổn định, và lưu lượng ra khuôn bằng lưu lượng cân.
10. Nhựa qua ống gia nhiệt (heated melt pipe), bộ trộn tĩnh (static mixer) và bích chuyển vào khuôn chữ T móc áo (coat-hanger T-die).
11. Màn nhựa (melt curtain) ra khỏi môi khuôn theo phương ngang +X, sau khe gió (air gap) 200 mm thì vào khe giữa trục giữa và trục dưới của cụm cán láng 3 trục đứng (vertical polishing roll stack). Tấm ôm trục giữa, đi lên qua trục trên, rồi ra băng con lăn làm nguội (băng này không dựng).

**Vận hành:**
- Gia nhiệt toàn bộ xi lanh, đường chảy và khuôn tới nhiệt độ đặt (≈ 270–290 °C).
- Chạy trục vít chậm với van khởi động ở vị trí xả. Khi nhựa ra đều thì xoay van sang vị trí chạy, bật bơm bánh răng và vòng điều khiển áp P3.
- Bật chân không vùng 1 khi nhựa đã chảy đều ở B3, rồi vùng 2 khi nút nhựa trước B5 đã kín. Người vận hành nhìn qua kính quan sát của hai vòm để chắc chắn nhựa không trào lên.
- Bảo vệ quá áp: P1 và P4 ngắt máy (P4 ở 330 bar); hai đĩa nổ cơ khí ở đầu xi lanh và sau bơm (350 bar).
- Chỉnh khe môi:
  - thô bằng bulông thanh chắn (choker bar);
  - tinh bằng 94 bulông nhiệt (thermal bolts), điều khiển tự động theo profin chiều dày.
- Dừng khẩn: nút trên HMI, tủ đầu máy, ba hộp dọc khung phía +Y, hộp khuôn và trên sàn thao tác.

## 2. Hệ toạ độ

- Đơn vị mm. Blender dùng m (mm × 0,001).
- **X** dọc trục vít, **+X theo chiều chảy** (động cơ → hộp số → xi lanh → đường chảy → khuôn). **X = 0** tại mặt xi lanh B1 phía hộp số, cũng là mặt bích lantern.
- **Y** ngang máy, **Y = 0** là mặt phẳng đứng giữa hai trục vít (hai trục vít ở Y = ±71). **+Y là phía người vận hành** (HMI).
- **Z** hướng lên, **Z = 0** là mặt sàn. Trục vít ở Z = 1 200.
- Hình chiếu đứng chính nhìn từ +Y về −Y, nên đầu khuôn (+X) nằm bên trái, giống hình bóng ZE UT ở trang 9 catalogue.

## 3. Thông số chính

| Thông số | Giá trị | Nguồn |
|---|---|---|
| Kiểu máy | ZE 155 A UT(i), trục vít đôi đồng hướng, bản A (D/d ≈ 1,47) | c001, DECISIONS 9 |
| Đường kính vít D / rãnh / lõi | 169 / 27,2 / 114,6 mm (Ø ngoài vít thực 167,5) | c001, c002; lõi = D − 2 × rãnh |
| Khoảng cách tâm trục a | 142 mm (hai trục ở Y = ±71) | specs §1, suy từ (D + d)/2, đã kiểm với ZE 180 và ZE 110 (c017, c020) |
| Lỗ xi lanh hình số 8 | rộng 311 × cao 169 mm | hình học từ a và D |
| Chiều dài gia công | 34D = 5 746 mm: B1 4D = 676, B2…B6 6D = 1 014 | c031, DECISIONS 9 |
| Tốc độ vít tối đa | 400 v/ph | c003 |
| Mômen | 2 × 35 000 Nm | c005 |
| Công suất truyền động tối đa của hộp số | 2 930 kW | c004 |
| **Công suất động cơ lắp đặt** | **1 500 kW**, 4 cực, trung thế, chạy biến tần; khung ABB AMI 450L4; làm mát IC81W (bộ làm mát gió–nước trên nóc) | giả định (xem §3.1); kích thước khung theo c066; kiểu làm mát theo DECISIONS 11.3 |
| Tỷ số truyền hộp số | ≈ 3,73 (1 490 → 400 v/ph) | giả định |
| Cao tâm trục vít | 1 200 mm | c006 |
| Năng suất thiết kế | 3 500 kg/h PET (dải 2 500–5 000) | specs §0 |
| Tấm / môi khuôn | tấm rộng 2 100, dày 0,3–1,5 mm; môi rộng 2 400 | specs §0, DECISIONS 10 |
| Gia nhiệt | xi lanh 5 × 25 kW, bộ lọc 39 kW (6 vùng), khuôn ≈ 50 kW (20 vùng) + bulông nhiệt 7,5 kW, các bích/ống ≈ 35 kW, tổng ≈ 260 kW | c018 (ZE 180: 30 kW/đoạn), c050, c055, c054; còn lại giả định |
| Bộ lọc lưới | Gneuss RSFgenius 200: 970 cm², 4 560 kg/h, 3 800 kg, bao 1 955 × 705 × 1 429 | c050 |
| Bơm bánh răng | Maag extrex6 GU 100/125: 764 cm³/v, ≈ 105 v/ph ở 3 500 kg/h, áp ra tối đa 370 bar | c047, c049 |
| Động cơ bơm | 45 kW, hộp giảm tốc góc i ≈ 14 | giả định (công suất thuỷ lực ≈ 0,81 L/s × 200 bar ≈ 16 kW, hiệu suất và dự phòng) |
| Cân cấp liệu chính | Coperion K-Tron BSP-150-S, 34–6 700 dm³/h | c069; 3 500 kg/h ÷ 0,8 kg/dm³ ≈ 4 400 dm³/h |
| Chân không | 2 vùng: B3 ≈ 50 mbar, B5 5–20 mbar; một cụm bơm Roots ≈ 2 000 m³/h trên bơm trục vít khô ≈ 400 m³/h, chung một bình tách | c040, c062 (độ tin cậy thấp), c059/c060; cỡ giả định (§7) |
| Cụm cán láng | 3 trục Ø800 × mặt 2 600, đứng; khe trục giữa và dưới ở Z = 1 200, X = 9 776 | c046, c044, DECISIONS 10 |
| Khối lượng máy đùn | ≈ 31 t (chưa tính đường chảy, khuôn) | specs §1 |
| Khối lượng khuôn chữ T | ≈ 3,4 t (2 nửa ≈ 0,40 m³ thép + tấm đầu, môi, bulông) | tính từ outline thân khuôn |

### 3.1 Vì sao chọn động cơ 1 500 kW

- **Năng lượng riêng (specific energy):** PET không sấy trên máy trục vít đôi cần khoảng 0,20–0,25 kWh/kg ở trục vít, đã gồm phần năng lượng cho khử khí. Ở 3 500 kg/h, công suất cần ≈ 3 500 × 0,23 ≈ **800 kW**.
- **Dự phòng:**
  - Dải năng suất mở rộng tới 5 000 kg/h cần ≈ 1 150 kW.
  - Tổn hao hộp số khoảng 2–3 %.
  - Cần thêm 15–20 % cho khởi động lạnh và các mác nhựa độ nhớt cao.
  - Cộng lại khoảng 1 400 kW. Chọn cấp tiêu chuẩn kế tiếp là **1 500 kW**. Cấp này nằm trong khung AMI 450L4; khung này lên tới 1 750 kW (c065).
- **Kiểm tra mômen:**
  - Động cơ 1 490 v/ph có mômen định mức ≈ 9,6 kNm. Qua tỷ số 3,73, mỗi trục vít nhận tối đa ≈ 17,9 kNm, bằng 51 % mức 35 kNm của hộp số. Hộp số vì vậy không bị quá tải.
  - Ở 300 v/ph (vùng chạy thường), biến tần giữ mômen không đổi, nên động cơ cho ≈ 1 125 kW. Mức này hơn 800 kW cần cho 3,5 t/h, dư khoảng 40 %.
- **Vì sao không lắp hết 2 930 kW:** dây chuyền tấm PET bị giới hạn bởi thể tích và khả năng khử khí, không bởi mômen. Nếu sau này muốn dùng máy cho compounding thì đổi sang khung AMI 500L4 (2 500 kW, c064/c067). Bệ động cơ phải dài thêm 240 mm.
- **Kích thước khung AMI 450L4 (c066):**
  - dài L 2 025, tâm trục H 450, cao tổng HC 1 860;
  - khoảng chân A 850 × B 1 400, rộng qua chân AB 980;
  - rộng gồm hộp đấu dây AE 1 500;
  - khối lượng ≈ 4,7 t.
- **Làm mát:** chọn IC81W, bộ làm mát gió–nước đặt trên nóc trong cùng hình bao HC 1 860 (giả định giữ hình bao như bản IC01). Nhiệt thải ≈ 45 kW (≈ 3 % công suất) đi vào nước qua 2 ống DN40 từ ống nhà máy dọc mép +Y khung, không thổi gió nóng vào xưởng.

## 4. Bố trí tổng thể

### 4.1 Các trạm theo trục X (tâm dòng chảy Y = 0, Z = 1 200)

| Cụm | X từ → tới | Ghi chú |
|---|---|---|
| Tủ đầu máy (khối cao cuối máy) | −5 650 → −5 150 | sơn xanh KM, đèn tháp trên nóc |
| Encoder | −5 075 → −4 975 | đầu trục NDE động cơ |
| Động cơ chính 1 500 kW | −4 975 → −2 950 | đế động cơ X −5 000 → −3 000 |
| Khớp đàn hồi + khớp an toàn, vỏ che cam | −2 980 → −2 300 | |
| Hộp số chia công suất | −2 300 → −750 | cao Z 650–1 720, rộng 1 400 |
| Lantern | −750 → 0 | cửa thăm phía +Y |
| B1 (4D, cấp liệu) | 0 → 676 | miệng nạp X 160–520 |
| B2 (6D, mở bên) | 676 → 1 690 | cửa side feeder +Y X 1 180–1 520 |
| B3 (6D, chân không vùng 1) | 1 690 → 2 704 | vòm 1 X 1 950–2 350, tâm X 2 150 |
| B4 (6D, kín) | 2 704 → 3 718 | |
| B5 (6D, chân không sâu vùng 2) | 3 718 → 4 732 | vòm 2 X 3 800–4 440, tâm X 4 120, ống ra trên nắp |
| B6 (6D, tăng áp) | 4 732 → 5 746 | |
| Mối nối bích bắt bulông | tại X = 676, 1 690, 2 704, 3 718, 4 732 | 20 × M24 trên PCD 560, cụm bulông dài 164 |
| Gối đỡ xi lanh | tâm X = 1 183, 3 211, 5 239 (giữa B2, B4, B6) | điểm cố định ở lantern |
| Vỏ che hộp C6 … C1 | 1 690 → 5 760 | C6 1 690–2 366, C5 –3 042, C4 –3 718, C3 –4 450 (dài hơn để chứa vòm), C2 –5 100, C1 –5 760 |
| Đầu xi lanh / bích chuyển | 5 746 → 5 996 | |
| Van khởi động | 5 996 → 6 446 | máng xả và xe hứng bên dưới; giá đỡ PTFE từ đầu khung (X 5 950–6 090) |
| Bích vào bộ lọc (P2) | 6 446 → 6 596 | |
| Bộ lọc lưới | 6 596 → 7 301 | đặt trên giá Z 0–650 |
| Bích vào bơm (P3) | 7 301 → 7 476 | |
| Bơm bánh răng | 7 476 → 7 926 | trục dẫn động hướng −Y |
| Bích ra bơm (P4) | 7 926 → 8 076 | |
| Ống nhựa gia nhiệt | 8 076 → 8 426 | |
| Bộ trộn tĩnh | 8 426 → 8 926 | |
| Bích chuyển vào khuôn (P5/T5) | 8 926 → 9 126 | |
| Khuôn chữ T | 9 126 → 9 576 | môi tại X = 9 576, Z = 1 200 |
| Xe đỡ khuôn | đế 8 700 → 9 380, ray tại X 8 760 và 9 320 (khổ 560) | đế luồn dưới bộ trộn; ray chạy theo Y từ −1 500 tới 2 800 |
| Khe gió → tâm trục cán | 9 576 → 9 776 | air gap 200 |
| Cụm cán láng (context) | 9 376 → 11 200, ray tới 12 500 | |
| Khung đế | −5 150 → 330 (đoạn truyền động), 330 → 5 950 (đoạn gia công) | rộng 2 000, đỉnh Z 650 |
| Sàn thao tác | X −2 700 → 1 850, Y −2 700 → 1 400, mặt sàn Z 3 000 | cầu thang phía −Y, X −5 700 → −2 700, Y −2 650 … −1 950 |
| Dãy tủ điện | X −5 200 → 1 600, Y −4 900 … −3 700 | biến tần trung thế, tủ điều khiển + nhiệt, tủ bulông nhiệt; mặt cửa ở Y −3 700 |

### 4.2 Phân bổ hai phía

| Phía người vận hành (+Y) | Phía sau (−Y) |
|---|---|
| Bảng HMI trên chân đế xoay (X ≈ −1 300, Y ≈ 1 500) | Máng cáp nhiệt và 7 hộp đấu dây nhiệt dọc mép khung |
| Ống góp nước cấp/hồi với 6 cụm van điện từ, tay van đỏ; đầu nối nước của xi lanh ở góc dưới +Y | Hộp đấu dây động cơ, cáp trung thế dựng lên từ hào cáp |
| Cụm dầu bôi trơn hộp số (trước động cơ, đúng như trang 9); ống nước bộ làm mát động cơ dọc mép khung | Hai đường chân không đi cao (đáy ống ≥ 2 190): DN100 từ vòm B3, DN150 từ nắp vòm B5, xuống bình tách ở Y −2 700; cụm bơm chân không, ống xả |
| Side feeder trên xe đẩy (B2) | Xi lanh thuỷ lực van khởi động, tay quay bộ lọc, hộp nhiệt đường chảy, bộ nguồn thuỷ lực (HPU) |
| Kính quan sát của hai vòm chân không | Bộ dẫn động bơm nhựa (các-đăng, hộp giảm tốc, động cơ đứng), đĩa nổ thứ hai |
| Cụm xả ngược và cửa thay lưới của bộ lọc | Hào cáp có nắp phẳng sàn, dãy tủ điện, cầu thang lên sàn, bộ lọc khí nén ở cột sàn |
| Cửa thăm lantern, kính thăm dầu hộp số, 3 hộp dừng khẩn ở tầm 1,1 m | Hộp đấu dây khuôn đặt sàn ngoài ray, bộ lọc khí nén khuôn, bó cáp bulông nhiệt |
| Ray kéo khuôn ra phía +Y khi bảo trì | Động cơ trục cán (context) |

Lối đi phía −Y: 950 mm từ mép khung tới cầu thang dọc động cơ, 850 mm trước ống cáp trung thế, ≥ 1 000 mm trước cửa tủ và cột sàn, ≈ 1 200 mm từ khung tới cụm chân không.

### 4.3 Cao độ chính (Z)

| Mốc | Z (mm) |
|---|---|
| sàn / đỉnh chân chỉnh cao | 0 / 60 |
| ranh hộp tủ và dầm trên khung đế / đỉnh khung đế | 450 / 650 |
| đáy thân xi lanh / trục vít / đỉnh thân xi lanh | 940 / 1 200 / 1 460 |
| đỉnh mặt bích xi lanh / đỉnh vỏ che | 1 500 / 1 650 |
| hộp dừng khẩn dọc máy | 1 050–1 190 |
| đỉnh hộp số / đỉnh vòm vùng 1 / đỉnh vòm vùng 2 | 1 720 / 1 960 / 2 150 |
| đáy ống chân không DN100 / DN150 khi đi ngang qua lối đi | 2 193 / 2 216 |
| đỉnh bộ lọc lưới / đỉnh động cơ chính | 2 079 / 2 610 |
| mặt sàn thao tác / tay vịn lan can | 3 000 / 4 100 |
| đỉnh phễu cân / đỉnh máy hút liệu / đầu ống hút liệu (vẽ cụt) | 4 900 / 5 800 / 6 300 |

### 4.4 Kích thước bao

`check_parts.py` in ra các kích thước bao sau:

- **Máy (không có context), gồm sàn thao tác, cầu thang, tủ điện, cụm chân không:**
  - X −5 700 … 9 900, Y −4 900 … 2 800, Z 0 … 6 300;
  - tức **15 600 × 7 700 × 6 300 mm**. Chiều rộng tăng so với bản đầu vì dãy tủ và cụm chân không được lùi ra để có lối đi.
- **Cả dây chuyền có cụm cán láng (không tính sàn nhà):** X −5 700 … 12 500, tức **18 200 × 7 700 × 6 300 mm**.
- **Máy chính** (khung đế, truyền động, xi lanh, đường chảy, khuôn, chưa tính sàn thao tác, tủ, cụm chân không):
  - X −5 150 … 9 900, Y −2 700 … 1 525, Z 0 … 2 610 (Y −2 700 là HPU);
  - tức dài ≈ 15,0 m; cao 2,6 m tới đỉnh động cơ.

## 5. Danh mục chi tiết theo cụm

Mỗi mục ghi: id, tên, chức năng khi vận hành, hình dạng và kích thước, vị trí (hộp bao), vật liệu và màu, nối với gì và bằng cách nào, nguồn. "giả định" nghĩa là không có tài liệu; lý do ghi ngay sau.

<!-- BEGIN PARTS -->
### Khung đế và giá đỡ (base and supports) — 12 mục

#### `base_frame_drive` — Khung đế đoạn truyền động (Base frame, drive segment)

- **Chức năng:** Đỡ hộp số, động cơ, lantern, vỏ khớp nối và cụm dầu; truyền tải trọng xuống chân đế.
- **Hình dạng / kích thước:** frame; bao 5480 × 2000 × 590 (X × Y × Z)
- **Vị trí:** X -5150 … 330, Y -1000 … 1000, Z 60 … 650
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `base_feet` – bulông chân chỉnh cao M30 tại (-5050, 900, 60); `base_frame_process` – mặt bích nối khung 12 bulông M24 tại X = 330 tại (330, 0, 400); `gearbox` – chân hộp số bắt 8 bulông M42 lên tấm gia công tại (-1500, 0, 650); `drive_motor_base` – đế động cơ bắt bulông, chêm căn chỉnh tại (-4000, 0, 650); `lantern` – chân lantern bắt bulông tại (-375, 0, 650); `drive_coupling_guard` – thanh góc chân vỏ che bắt vít tại (-2640, 0, 650); `lube_unit_frame` – khay dầu bắt vít lên mặt khung tại (-3000, 800, 650); `ctrl_machine_cabinet` – tủ áp sát đầu khung, bắt 4 vít tại (-5150, 0, 400)
- **Chi tiết phải dựng:** Dầm trên (top beam) hộp hàn Z 450–650, mặt trên gia công phẳng có các tấm đệm cho hộp số, đế động cơ, lantern. Hộp tủ dưới (cabinet box) Z 60–450 lùi vào 50 mm mỗi bên, cửa bản lề rộng 520 mm bước ≈ 860 mm, tay nắm lõm, hai bên ±Y. Lỗ tròn vận chuyển Ø140 có nút nhựa vàng tại X = −541 và −3 858, cả hai mặt bên (theo trang 9). Mối hàn dọc trên dầm trên bước ≈ 1 050 mm (theo trang 9). Bên trong hộp tủ: kênh cáp ngang nối phía +Y với phía −Y (cho cáp HMI, side feeder, nút dừng khẩn).
- **Nguồn:** pdf_measures §2.2/§4 (khung 2 đoạn, dầm trên 210 / hộp dưới 390 mm, mối chia X ≈ +330); chiều rộng 2 000 giả định theo specs §1 (ZE 110 × 1,42)

#### `base_frame_process` — Khung đế đoạn gia công (Base frame, processing segment)

- **Chức năng:** Đỡ các gối xi lanh, vỏ che, ống góp nước, máng cáp và hộp đấu dây suốt 34D.
- **Hình dạng / kích thước:** frame; bao 5620 × 2000 × 590 (X × Y × Z)
- **Vị trí:** X 330 … 5950, Y -1000 … 1000, Z 60 … 650
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `base_feet` – bulông chân chỉnh cao M30 tại (5850, 900, 60); `base_frame_drive` – mặt bích nối khung tại X = 330 tại (330, 0, 400); `base_drip_tray` – khay đặt trên mặt khung, hàn kín mép tại (3000, 0, 650); `barrel_support_1` – gối bắt 4 bulông M30 + chốt định vị tại (1183, 0, 650); `barrel_support_2` – gối bắt 4 bulông M30 tại (3211, 0, 650); `barrel_support_3` – gối bắt 4 bulông M30 tại (5239, 0, 650); `barrel_cover_c1` – chân vỏ che bắt vít vào mép khung tại (5400, 0, 650)
- **Chi tiết phải dựng:** Cùng tiết diện với đoạn truyền động: dầm trên Z 450–650, hộp tủ Z 60–450 có cửa và lỗ tròn Ø140 tại X = 1 185 và 5 170. Trong hộp tủ chứa bộ điều nhiệt / phân phối nước (temperature control unit) như catalogue c034; cửa có lưới thông gió. Đầu khung phía khuôn (X = 5 950) có tấm bịt và 2 tai cẩu.
- **Nguồn:** pdf_measures §2.2/§4; chiều dài theo khoảng X đầu ra +5 922 của hình bóng quy đổi về 34D = 5 746 (DECISIONS 9)

#### `base_feet` — Chân chỉnh cao / bulông neo (Levelling feet and anchors)

- **Chức năng:** Chỉnh cao và neo khung đế xuống nền, hấp thụ rung.
- **Hình dạng / kích thước:** cyl; bao 11100 × 2000 × 60 (X × Y × Z); số lượng 22
- **Vị trí:** X -5150 … 5950, Y -1000 … 1000, Z 0 … 60
- **Vật liệu / màu:** dark_steel `#5F656B`
- **Nối với:** `base_frame_drive` – bulông chỉnh cao M30 xuyên dầm tại (-5050, 900, 60); `base_frame_process` – bulông chỉnh cao M30 tại (5850, 900, 60); `ctx_floor` – bulông neo hoá chất M24 tại (-300, 900, 0)
- **Chi tiết phải dựng:** 22 chân Ø200 × 60 (đĩa đệm cao su + vít chỉnh M30), mỗi bên 11 chân tại Y = ±900. X = −5 050, −3 900, −2 700, −1 500, −300, 600, 1 700, 2 800, 3 900, 5 000, 5 850.
- **Nguồn:** pdf_measures §2.2 (chân cao 57 mm, 12 vị trí); số lượng và vị trí giả định theo chiều dài khung mới

#### `base_drip_tray` — Khay hứng nhỏ giọt trên khung (Drip tray on frame top)

- **Chức năng:** Hứng nước, dầu, nhựa rơi dưới xi lanh để không chảy vào hộp tủ.
- **Hình dạng / kích thước:** sheet; bao 5500 × 880 × 40 (X × Y × Z)
- **Vị trí:** X 400 … 5900, Y -440 … 440, Z 650 … 690
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `base_frame_process` – đặt trên mặt khung, mép gập 40 mm tại (3000, 0, 650)
- **Chi tiết phải dựng:** Tôn inox 3 mm, mép gập cao 40 mm, có lỗ xả ở đầu X = 5 900.
- **Nguồn:** giả định: chi tiết thường có trên máy đùn (web-01 cho thấy mặt khung kín dưới xi lanh)

#### `barrel_support_1` — Gối đỡ xi lanh số 1 (Barrel support saddle 1)

- **Chức năng:** Đỡ xi lanh từ dưới, cho phép xi lanh giãn nở nhiệt trượt theo X (điểm cố định ở lantern X = 0).
- **Hình dạng / kích thước:** extrude; bao 250 × 700 × 384 (X × Y × Z)
- **Vị trí:** X 1058 … 1308, Y -350 … 350, Z 650 … 1034
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `base_frame_process` – bắt 4 bulông M30, lỗ ô van cho chỉnh tại (1183, 0, 650); `barrel_b2` – tấm trượt đồng/PTFE dưới thân xi lanh, kẹp giữ Y nhưng tự do X tại (1183, 0, 940)
- **Chi tiết phải dựng:** Gối đúc hình chữ A, tấm đế 700 × 250, lỗ tròn Ø120 giữa thân tại Z ≈ 800. Lòng đỡ cong bán kính 260 ôm đáy thân xi lanh, có tấm trượt (slide pad) mỏng. Đệm trên của gối rộng 70 mm (X), tì vào băng thân trần rộng 74 mm giữa hai vỏ nhiệt của đoạn.
- **Nguồn:** web-02 (gối đúc trắng hình chữ A có lỗ); vị trí giả định: giữa B2, B4, B6, tránh các mối nối bích

#### `barrel_support_2` — Gối đỡ xi lanh số 2 (Barrel support saddle 2)

- **Chức năng:** Đỡ xi lanh từ dưới, cho phép xi lanh giãn nở nhiệt trượt theo X (điểm cố định ở lantern X = 0).
- **Hình dạng / kích thước:** extrude; bao 250 × 700 × 384 (X × Y × Z)
- **Vị trí:** X 3086 … 3336, Y -350 … 350, Z 650 … 1034
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `base_frame_process` – bắt 4 bulông M30, lỗ ô van cho chỉnh tại (3211, 0, 650); `barrel_b4` – tấm trượt đồng/PTFE dưới thân xi lanh, kẹp giữ Y nhưng tự do X tại (3211, 0, 940)
- **Chi tiết phải dựng:** Gối đúc hình chữ A, tấm đế 700 × 250, lỗ tròn Ø120 giữa thân tại Z ≈ 800. Lòng đỡ cong bán kính 260 ôm đáy thân xi lanh, có tấm trượt (slide pad) mỏng. Đệm trên của gối rộng 70 mm (X), tì vào băng thân trần rộng 74 mm giữa hai vỏ nhiệt của đoạn.
- **Nguồn:** web-02 (gối đúc trắng hình chữ A có lỗ); vị trí giả định: giữa B2, B4, B6, tránh các mối nối bích

#### `barrel_support_3` — Gối đỡ xi lanh số 3 (Barrel support saddle 3)

- **Chức năng:** Đỡ xi lanh từ dưới, cho phép xi lanh giãn nở nhiệt trượt theo X (điểm cố định ở lantern X = 0).
- **Hình dạng / kích thước:** extrude; bao 250 × 700 × 384 (X × Y × Z)
- **Vị trí:** X 5114 … 5364, Y -350 … 350, Z 650 … 1034
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `base_frame_process` – bắt 4 bulông M30, lỗ ô van cho chỉnh tại (5239, 0, 650); `barrel_b6` – tấm trượt đồng/PTFE dưới thân xi lanh, kẹp giữ Y nhưng tự do X tại (5239, 0, 940)
- **Chi tiết phải dựng:** Gối đúc hình chữ A, tấm đế 700 × 250, lỗ tròn Ø120 giữa thân tại Z ≈ 800. Lòng đỡ cong bán kính 260 ôm đáy thân xi lanh, có tấm trượt (slide pad) mỏng. Đệm trên của gối rộng 70 mm (X), tì vào băng thân trần rộng 74 mm giữa hai vỏ nhiệt của đoạn.
- **Nguồn:** web-02 (gối đúc trắng hình chữ A có lỗ); vị trí giả định: giữa B2, B4, B6, tránh các mối nối bích

#### `melt_stand_sc` — Giá đỡ bộ lọc lưới (Screen changer stand)

- **Chức năng:** Đỡ bộ lọc lưới 3,8 t và giữ tâm dòng chảy ở Z = 1 200.
- **Hình dạng / kích thước:** frame; bao 800 × 1200 × 650 (X × Y × Z)
- **Vị trí:** X 6550 … 7350, Y -600 … 600, Z 0 … 650
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `melt_screen_changer` – tấm trượt PTFE, chốt dẫn hướng Y tại (6950, 0, 650); `ctx_floor` – tấm đế bắt bulông neo tại (6950, 0, 0); `melt_heater_jbox` – giá gá mặt −Y tại (6950, -600, 550)
- **Chi tiết phải dựng:** Khung thép hộp 4 chân, tấm đỉnh 800 × 1 200 × 30, giằng chéo hai bên. Mặt đỉnh Z = 650 trùng đáy thân bộ lọc; giữa bộ lọc và tấm đỉnh có tấm trượt PTFE: tự do theo X ±40 mm (giãn nở của xi lanh + đường chảy), dẫn hướng theo Y. Chỉ tấm đế (sole plate) được neo xuống sàn; mặt −Y mang hộp đấu nhiệt đường chảy.
- **Nguồn:** giả định: Gneuss giao bộ lọc kèm khung; chiều cao = 1 200 − D 550 (c050)

#### `melt_stand_pump` — Giá đỡ bơm nhựa và ống (Gear pump and melt pipe stand)

- **Chức năng:** Đỡ bơm bánh răng, ống nhựa và bộ trộn tĩnh.
- **Hình dạng / kích thước:** frame; bao 1250 × 900 × 970 (X × Y × Z)
- **Vị trí:** X 7400 … 8650, Y -450 … 450, Z 0 … 970
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `melt_gear_pump` – chân bơm trên tấm trượt PTFE tại (7700, 0, 970); `melt_pipe_saddles` – gối ống bắt vít lên mặt đỉnh tại (8250, 0, 970); `ctx_floor` – tấm đế bắt bulông neo tại (8000, 0, 0)
- **Chi tiết phải dựng:** Khung thép hộp 6 chân, mặt đỉnh 1 250 × 900, Z = 970; kết thúc ở X = 8 650 để chừa chỗ cho đế xe khuôn. Bơm đặt trên tấm trượt PTFE (tự do X ±40, dẫn hướng Y); chỉ tấm đế được neo.
- **Nguồn:** giả định: khung riêng cho bơm như ảnh web-07 (khung đỡ dưới đường chảy); rút ngắn để xe khuôn chạy vào dưới bộ trộn

#### `melt_pipe_saddles` — Gối đỡ ống nhựa (Melt pipe saddles)

- **Chức năng:** Đỡ ống nhựa và bộ trộn tĩnh, cho trượt theo X khi giãn nở.
- **Hình dạng / kích thước:** box; bao 460 × 240 × 80 (X × Y × Z); số lượng 2
- **Vị trí:** X 8175 … 8635, Y -120 … 120, Z 970 … 1050
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_stand_pump` – bắt vít lên mặt khung tại (8250, 0, 970); `melt_pipe` – gối chữ V có đệm cách nhiệt tại (8250, 0, 1050); `melt_static_mixer` – gối chữ V có đệm cách nhiệt tại (8560, 0, 1050)
- **Chi tiết phải dựng:** 2 gối chữ V 150 × 240 cao 80 tại X = 8 250 (ống) và 8 560 (bộ trộn), mặt trượt cho X.
- **Nguồn:** giả định

#### `melt_valve_support` — Giá đỡ van khởi động (Diverter valve support bracket)

- **Chức năng:** Đỡ van khởi động và đầu xi lanh (≈ 1,3 t) đang treo ngoài gối đỡ cuối; con lăn/PTFE cho phép giãn nở theo X.
- **Hình dạng / kích thước:** extrude; bao 140 × 520 × 380 (X × Y × Z)
- **Vị trí:** X 5950 … 6090, Y -260 … 260, Z 560 … 940
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `base_frame_process` – bắt 4 bulông vào tấm đầu khung X = 5 950 tại (5950, 0, 600); `melt_startup_valve` – 2 đệm PTFE dưới đáy van tại Y = ±205 tại (6040, 205, 940)
- **Chi tiết phải dựng:** Hai tai thép chữ L tại Y = ±(150…260), bắt vào mặt đầu khung (Z 560–650) rồi vươn lên Z 940; mỗi tai mang 1 đệm PTFE 90 × 110. Chừa giữa Y ±150 cho máng xả nhựa; đáy giá ở Z 560, trên miệng xe hứng (Z 520).
- **Nguồn:** review-01 I8; giả định

#### `pump_drive_pedestal` — Bệ hộp giảm tốc bơm (Gear pump drive pedestal)

- **Chức năng:** Đỡ hộp giảm tốc và động cơ bơm nhựa phía sau (−Y).
- **Hình dạng / kích thước:** frame; bao 500 × 450 × 950 (X × Y × Z)
- **Vị trí:** X 7451 … 7951, Y -1750 … -1300, Z 0 … 950
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `melt_pump_gearbox` – 4 bulông M24 tại (7701, -1525, 950); `ctx_floor` – bulông neo tại (7701, -1525, 0)
- **Chi tiết phải dựng:** Khung hộp thép 500 × 450, cao 950.
- **Nguồn:** giả định: bố trí như web-07 (hộp giảm tốc + động cơ đứng cạnh bơm)

### Truyền động (drive) — 15 mục

#### `lantern` — Lantern (hộp nối hộp số – xi lanh) (Lantern / intermediate housing)

- **Chức năng:** Nối mặt bích ra hộp số với xi lanh B1; chứa khớp then hoa nối trục ra hộp số với trục vít; có cửa thăm.
- **Hình dạng / kích thước:** extrude; bao 750 × 900 × 1010 (X × Y × Z)
- **Vị trí:** X -750 … 0, Y -450 … 450, Z 650 … 1660
- **Vật liệu / màu:** blue_drive `#2C5FAE`
- **Nối với:** `gearbox` – mặt bích 16 bulông M30 tại X = −750 tại (-750, 0, 1200); `barrel_b1` – mặt bích Ø700, 20 bulông cấy M24 trên PCD 560 tại X = 0 tại (0, 0, 1200); `base_frame_drive` – chân lantern bắt 4 bulông tại (-375, 0, 650); `screws` – ống then hoa (spline sleeve) bên trong tại (-400, 0, 1200)
- **Chi tiết phải dựng:** Cửa thăm chữ nhật bo góc 380 × 250 trên mặt +Y, tâm X = −375, Z = 1 200, 8 vít + tay nắm. Vành mặt bích Ø700 dày 60 ở đầu X = 0: 20 lỗ ren M24 trên PCD 560 nhận bulông cấy từ bích B1 (đai ốc 12 cạnh nằm phía B1). Ống xả dầu rò rỉ ở đáy, tai cẩu trên nóc. Trong: 2 khớp then hoa (spline coupling) tại Y = ±71.
- **Nguồn:** pdf_measures §2.2 (lantern 15,26 × 19,68 pt có cửa thăm bo góc); màu theo web-01 (khối nối xanh như hộp số)

#### `gearbox` — Hộp số chia công suất (Power-split twin-screw gearbox)

- **Chức năng:** Giảm tốc từ động cơ (≈ 1 490 v/ph) xuống tối đa 400 v/ph và chia mômen 2 × 35 kNm ra hai trục vít đồng hướng.
- **Hình dạng / kích thước:** extrude; bao 1550 × 1400 × 1070 (X × Y × Z)
- **Vị trí:** X -2300 … -750, Y -700 … 700, Z 650 … 1720
- **Vật liệu / màu:** blue_drive `#2C5FAE`
- **Nối với:** `base_frame_drive` – 8 chân bắt bulông M42 tại (-1500, 0, 650); `lantern` – mặt bích ra tại (-750, 0, 1200); `drive_safety_coupling` – trục vào Ø160 có then, nắp ổ trục vào tại (-2300, 0, 1200); `lube_pipe_pressure` – cổng dầu áp lực G1¼ phía +Y tại (-2000, 700, 1500); `lube_pipe_return` – cổng hút đáy carter G2 phía +Y tại (-1500, 700, 760); `drive_coupling_guard` – vỏ che áp mặt hộp số tại (-2300, 0, 1500)
- **Chi tiết phải dựng:** Vỏ gang hộp có gân, phần bướu trên cao Z 1 720 bao 2 trục ra ở đầu X −1 250 … −750. Nắp ổ trục vào tròn Ø500 nhô 50 mm ở đầu X = −2 300 quanh Z = 1 200. 4 tai cẩu (lifting eyes) trên nóc, nắp thăm chữ nhật trên nóc, ống thở (breather), kính thăm mức dầu phía +Y, nút xả dầu ở đáy. Biển tên, tem cảnh báo vàng; cảm biến nhiệt dầu PT100 cạnh cổng dầu. Tỷ số truyền ≈ 3,73 (1 490/400).
- **Nguồn:** c033 (chia công suất, bôi trơn ngâm + áp lực, khớp an toàn); c005 mômen; tỷ lệ dài/cao theo pdf_measures §2.3; màu xanh theo web-01/web-03, c023

#### `drive_safety_coupling` — Khớp an toàn giới hạn mômen (Torque-limiting safety coupling)

- **Chức năng:** Tách động cơ khỏi hộp số khi quá tải (vít kẹt, vật lạ) để bảo vệ trục vít và hộp số.
- **Hình dạng / kích thước:** revolve; bao 400 × 640 × 640 (X × Y × Z); trục X; R 320
- **Vị trí:** X -2700 … -2300, Y -320 … 320, Z 880 … 1520
- **Vật liệu / màu:** polished `#D5D9DD`
- **Nối với:** `gearbox` – moay-ơ côn trên trục vào tại (-2300, 0, 1200); `drive_flex_coupling` – mặt bích 12 bulông tại (-2700, 0, 1200)
- **Chi tiết phải dựng:** Đĩa thép bạc Ø640 có rãnh vòng (như ảnh p19), vòng bulông 12 lỗ, công tắc giám sát nhả khớp.
- **Nguồn:** c033 (safety coupling); p05/p19 (đĩa ly hợp bạc giữa động cơ và hộp số); cỡ giả định

#### `drive_flex_coupling` — Khớp nối đàn hồi (Flexible coupling)

- **Chức năng:** Bù lệch tâm giữa trục động cơ và trục vào hộp số, giảm va đập.
- **Hình dạng / kích thước:** revolve; bao 250 × 560 × 560 (X × Y × Z); trục X; R 280
- **Vị trí:** X -2950 … -2700, Y -280 … 280, Z 920 … 1480
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `drive_motor` – moay-ơ trên trục động cơ Ø140 tại (-2950, 0, 1200); `drive_safety_coupling` – mặt bích 12 bulông tại (-2700, 0, 1200)
- **Chi tiết phải dựng:** Hai moay-ơ thép + bộ đĩa lò xo, Ø560.
- **Nguồn:** giả định (khớp đĩa/đàn hồi tiêu chuẩn cỡ 10 kNm)

#### `drive_coupling_guard` — Vỏ che khớp nối (Coupling guard)

- **Chức năng:** Che phần quay giữa động cơ và hộp số, có khoá liên động.
- **Hình dạng / kích thước:** box; bao 680 × 900 × 1000 (X × Y × Z)
- **Vị trí:** X -2980 … -2300, Y -450 … 450, Z 650 … 1650
- **Vật liệu / màu:** orange `#EE7A12`
- **Nối với:** `base_frame_drive` – thanh góc chân bắt vít tại (-2640, 0, 650); `gearbox` – áp vào mặt hộp số tại (-2300, 0, 1500)
- **Chi tiết phải dựng:** Tôn 3 mm, tấm hông +Y tháo được có ô lưới quan sát, móc cẩu trên nóc. Công tắc liên động (interlock) cấm chạy khi mở nắp.
- **Nguồn:** pdf_measures §2.2 (vỏ khớp nối có móc cẩu trên nóc); màu cam theo web-12

#### `drive_motor` — Động cơ chính 1 500 kW, làm mát gió–nước trên nóc (Main AC motor 1 500 kW, IC81W top air-to-water cooler (ABB AMI 450L4 frame))

- **Chức năng:** Động cơ cảm ứng trung thế 4 cực, chạy biến tần, quay trục vít qua khớp nối và hộp số; bộ làm mát gió–nước trên nóc thải nhiệt vào nước, không thổi gió nóng vào xưởng.
- **Hình dạng / kích thước:** extrude; bao 2025 × 1150 × 1860 (X × Y × Z); trục X
- **Vị trí:** X -4975 … -2950, Y -575 … 575, Z 750 … 2610
- **Vật liệu / màu:** motor `#2B528C`
- **Nối với:** `drive_motor_base` – 4 chân bắt bulông M36 (B 1 400 × A 850) tại (-4000, 0, 750); `drive_flex_coupling` – đầu trục Ø140 tại (-2950, 0, 1200); `drive_motor_terminal_box` – hộp đấu dây bắt mặt bên −Y tại (-4000, -575, 1350); `drive_encoder` – bích encoder ở đầu NDE tại (-4975, 0, 1200); `util_cw_motor_hoses` – 2 bích nước DN40 trên mặt +Y bộ làm mát tại (-3500, 575, 2300)
- **Chi tiết phải dựng:** Thân hộp có gân Z 750–1 680; trên nóc là hộp bộ làm mát gió–nước (IC81W top air-to-water cooler) Z 1 680–2 610, X −4 800 … −3 300: vỏ hộp kín, 2 nắp thăm ống trao đổi nhiệt ở đầu −X, không có cửa gió hở. Hai bích nước DN40 trên mặt +Y của hộp làm mát: vào tại X −3 500, Z 2 300; ra tại X −3 700, Z 2 400; cảm biến rò nước ở đáy hộp. Đầu trục Ø140 dài 200 ở phía hộp số; nắp ổ NDE nhô 75 mm mang encoder. 4 tai cẩu, biển tên, cọc tiếp địa; tâm trục Z = 1 200 (H 450 trên mặt đế Z 750).
- **Nguồn:** c066 (AMI 450L: L 2 025, H 450, HC 1 860, A 850, B 1 400, AB 980, AE 1 500); c065 khối lượng ≈ 4,7 t; công suất 1 500 kW giả định (xem design.md §3); DECISIONS 11.3 + review-01 M9: kiểu làm mát IC81W (bộ làm mát gió–nước trên nóc), giả định giữ nguyên hình bao HC 1 860 như bản IC01

#### `drive_motor_terminal_box` — Hộp đấu dây động cơ (Motor terminal box)

- **Chức năng:** Đấu cáp trung thế từ biến tần vào động cơ.
- **Hình dạng / kích thước:** box; bao 600 × 350 × 500 (X × Y × Z)
- **Vị trí:** X -4300 … -3700, Y -925 … -575, Z 1100 … 1600
- **Vật liệu / màu:** motor `#2B528C`
- **Nối với:** `drive_motor` – bắt bulông lên thân tại (-4000, -575, 1350); `ctrl_cable_mv` – đầu cáp vào qua đáy hộp tại (-4000, -925, 1150)
- **Chi tiết phải dựng:** Hộp thép 600 × 350 × 500, nắp 12 vít, ốc siết cáp ở đáy.
- **Nguồn:** c066 (AE 1 500 gồm hộp đấu dây); phía −Y giả định để tránh lối thao tác

#### `drive_motor_base` — Đế động cơ (Motor sub-base)

- **Chức năng:** Nâng động cơ để tâm trục khớp Z = 1 200, cho phép căn chỉnh đồng tâm.
- **Hình dạng / kích thước:** frame; bao 2000 × 1200 × 100 (X × Y × Z)
- **Vị trí:** X -5000 … -3000, Y -600 … 600, Z 650 … 750
- **Vật liệu / màu:** dark_steel `#5F656B`
- **Nối với:** `base_frame_drive` – bắt bulông, chêm căn tại (-4000, 0, 650); `drive_motor` – 4 chân động cơ, vít đẩy căn chỉnh tại (-4000, 0, 750)
- **Chi tiết phải dựng:** Hai ray thép dày 100 có vít đẩy (jack screws) căn chỉnh ngang.
- **Nguồn:** giả định: 1 200 − H 450 − đỉnh khung 650 = 100 mm

#### `drive_encoder` — Encoder tốc độ (Speed encoder)

- **Chức năng:** Đo tốc độ / vị trí trục động cơ cho biến tần điều khiển vector.
- **Hình dạng / kích thước:** cyl; bao 100 × 160 × 160 (X × Y × Z); trục X; R 80
- **Vị trí:** X -5075 … -4975, Y -80 … 80, Z 1120 … 1280
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `drive_motor` – bích + khớp nối nhỏ ở đầu trục NDE tại (-4975, 0, 1200)
- **Chi tiết phải dựng:** Vỏ Ø160 × 100, đầu cáp tín hiệu.
- **Nguồn:** giả định (biến tần trung thế điều khiển vòng kín)

#### `lube_unit_frame` — Khay đế cụm dầu bôi trơn (Lube unit tray)

- **Chức năng:** Đế và khay hứng dầu cho cụm bơm, lọc, làm mát dầu hộp số.
- **Hình dạng / kích thước:** sheet; bao 1150 × 400 × 50 (X × Y × Z)
- **Vị trí:** X -3600 … -2450, Y 600 … 1000, Z 650 … 700
- **Vật liệu / màu:** blue_drive `#2C5FAE`
- **Nối với:** `base_frame_drive` – bắt vít lên mặt khung tại (-3000, 800, 650); `lube_pump_motor` – bắt bulông tại (-3350, 800, 700); `lube_filter_duplex` – giá đỡ bắt vít tại (-3075, 800, 700); `lube_oil_cooler` – giá đỡ bắt vít tại (-2775, 775, 700)
- **Chi tiết phải dựng:** Khay có mép gập, tấm thấm dầu vàng như web-03.
- **Nguồn:** pdf_measures §2.2 (cụm dầu phía trước động cơ trên hình bóng); web-03; c034

#### `lube_pump_motor` — Bơm dầu + động cơ mặt bích đứng (Lube oil pump with vertical flange motor)

- **Chức năng:** Hút dầu từ carter hộp số và đẩy qua lọc, bộ làm mát tới vòi phun bánh răng/ổ trục.
- **Hình dạng / kích thước:** composite; bao 300 × 300 × 750 (X × Y × Z)
- **Vị trí:** X -3500 … -3200, Y 650 … 950, Z 700 … 1450
- **Vật liệu / màu:** blue_drive `#2C5FAE`
- **Nối với:** `lube_unit_frame` – chân bơm bắt bulông tại (-3350, 800, 700); `lube_filter_duplex` – ống nối ren tại (-3200, 800, 1000); `lube_pipe_return` – cổng hút tại (-3350, 950, 760)
- **Chi tiết phải dựng:** Động cơ 4 kW đặt đứng Ø260 có nắp quạt, chuông nối, bơm bánh răng ở đáy; 2 đồng hồ áp. Van an toàn (relief valve) tích hợp trên thân bơm xả về carter; lọc hút (suction strainer) trên ống hút ngay trước bơm.
- **Nguồn:** web-03 (bơm có động cơ mặt bích đứng, sơn xanh); p19_3

#### `lube_filter_duplex` — Lọc dầu kép (Duplex oil filter)

- **Chức năng:** Lọc dầu, đổi bầu lọc khi máy chạy.
- **Hình dạng / kích thước:** composite; bao 250 × 270 × 700 (X × Y × Z)
- **Vị trí:** X -3200 … -2950, Y 680 … 950, Z 700 … 1400
- **Vật liệu / màu:** blue_drive `#2C5FAE`
- **Nối với:** `lube_pump_motor` – ống nối tại (-3200, 800, 1000); `lube_oil_cooler` – ống nối tại (-2950, 800, 900); `lube_unit_frame` – giá đỡ tại (-3075, 800, 700)
- **Chi tiết phải dựng:** 2 bầu lọc đứng Ø110, tay gạt chuyển đổi, chỉ báo chênh áp, đồng hồ áp.
- **Nguồn:** web-03 (2 bầu lọc + tay gạt chuyển đổi); pdf_measures §2.2 (lọc kép trước động cơ)

#### `lube_oil_cooler` — Bộ làm mát dầu tấm (Plate oil cooler (oil/water))

- **Chức năng:** Giải nhiệt dầu hộp số bằng nước làm mát.
- **Hình dạng / kích thước:** box; bao 350 × 250 × 350 (X × Y × Z)
- **Vị trí:** X -2950 … -2600, Y 650 … 900, Z 700 … 1050
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `lube_filter_duplex` – ống nối tại (-2950, 800, 900); `lube_pipe_pressure` – cổng dầu ra F3 tại (-2775, 775, 1050); `util_cw_lube_hoses` – cổng nước F2/F4 tại (-2775, 900, 850); `lube_unit_frame` – giá đỡ tại (-2775, 775, 700)
- **Chi tiết phải dựng:** Khối tấm hàn inox 350 × 250 × 350, 4 cổng ren F1–F4 trên mặt +Y.
- **Nguồn:** web-03 (bộ trao đổi nhiệt tấm inox có cổng F1–F4)

#### `lube_pipe_pressure` — Ống dầu áp lực tới hộp số (Lube pressure line)

- **Chức năng:** Dẫn dầu đã lọc, làm mát tới hệ phun trong hộp số.
- **Hình dạng / kích thước:** pipe; bao 817 × 96 × 471 (X × Y × Z); R 21
- **Vị trí:** X -2796 … -1979, Y 700 … 796, Z 1050 … 1521
- **Vật liệu / màu:** blue_drive `#2C5FAE`
- **Nối với:** `lube_oil_cooler` – ren G1¼ tại (-2775, 775, 1050); `gearbox` – ren G1¼ tại (-2000, 700, 1500)
- **Chi tiết phải dựng:** Ống thép DN32 (OD 42) sơn xanh; công tắc áp suất (PS, khoá khởi động truyền động) gần cổng vào hộp số, tín hiệu về tủ đầu máy (s_14).
- **Nguồn:** web-03 (ống dầu sơn xanh); tuyến ống giả định

#### `lube_pipe_return` — Ống hút dầu từ carter (Lube suction line)

- **Chức năng:** Dẫn dầu từ carter hộp số về bơm.
- **Hình dạng / kích thước:** pipe; bao 1900 × 300 × 50 (X × Y × Z); R 25
- **Vị trí:** X -3375 … -1475, Y 700 … 1000, Z 735 … 785
- **Vật liệu / màu:** blue_drive `#2C5FAE`
- **Nối với:** `gearbox` – ren G2 đáy carter tại (-1500, 700, 760); `lube_pump_motor` – cổng hút tại (-3350, 950, 760)
- **Chi tiết phải dựng:** Ống thép DN40 (OD 50) chạy dọc mép +Y của khung, Z = 760.
- **Nguồn:** giả định

### Cấp liệu (feeding) — 26 mục

#### `feed_throat` — Hộp miệng nạp (Feed throat housing)

- **Chức năng:** Nối phễu với lỗ nạp B1, có áo nước làm mát chống dính hạt.
- **Hình dạng / kích thước:** box; bao 500 × 420 × 185 (X × Y × Z)
- **Vị trí:** X 90 … 590, Y -210 … 210, Z 1455 … 1640
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `barrel_b1` – 8 bulông M20 trên mặt gia công tại (340, 0, 1460); `feed_hopper` – mặt bích vuông tại (340, 0, 1640)
- **Chi tiết phải dựng:** Khối inox 500 × 420 × 185, lỗ trong 360 × 300, 2 đầu nối nước làm mát.
- **Nguồn:** giả định (miệng nạp 300 × 250 theo specs §2, nới thành 360 × 300 cho D 169)

#### `feed_hopper` — Phễu nạp có cổng nghiêng 45° (Feed hopper with 45° inlet)

- **Chức năng:** Gom hạt từ ống rơi xuống miệng nạp; cổng nghiêng 45° về phía hộp số.
- **Hình dạng / kích thước:** extrude; bao 500 × 500 × 260 (X × Y × Z)
- **Vị trí:** X 90 … 590, Y -250 … 250, Z 1640 … 1900
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_throat` – mặt bích vuông tại (340, 0, 1640); `feed_flex_sleeve` – cổ nghiêng 45° Ø250 tại (200, 0, 1900)
- **Chi tiết phải dựng:** Phễu hình chóp ngược inox: đỉnh 500 × 500, đáy 360 × 300 (côn cả theo Y). Nắp đỉnh có cổ nghiêng 45° Ø250 hướng −X, cổng khí N₂ (inert) nhỏ, kính thăm và cảm biến mức.
- **Nguồn:** pdf_measures §2.2 (phễu nhỏ có ống nạp nghiêng 45° về phía dẫn động); p06

#### `feed_flex_sleeve` — Ống mềm nối phễu (Flexible sleeve)

- **Chức năng:** Nối mềm ống rơi với phễu, cách rung và cho phép tháo nhanh.
- **Hình dạng / kích thước:** pipe; bao 293.8 × 260 × 293.8 (X × Y × Z); R 130
- **Vị trí:** X -1.9 … 291.9, Y -130 … 130, Z 1808.1 … 2101.9
- **Vật liệu / màu:** white `#EDEEEE`
- **Nối với:** `feed_hopper` – đai kẹp tại (200, 0, 1900); `feed_downpipe` – đai kẹp tại (90, 0, 2010)
- **Chi tiết phải dựng:** Ống bạt trắng Ø260 dài 155 với 2 đai kẹp inox.
- **Nguồn:** giả định (ống mềm nối phổ biến dưới cân cấp liệu, thấy ở p01)

#### `feed_downpipe` — Ống rơi liệu chính (Main feed down-pipe)

- **Chức năng:** Dẫn hạt từ cân cấp liệu trên sàn thao tác xuống phễu.
- **Hình dạng / kích thước:** pipe; bao 753.4 × 250 × 928.4 (X × Y × Z); R 125
- **Vị trí:** X -575 … 178.4, Y -125 … 125, Z 1921.6 … 2850
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_flex_sleeve` – đai kẹp tại (90, 0, 2010); `feed_feeder_sleeves` – đai kẹp, ống mềm cách cân tại (-450, 0, 2850); `feed_additive_tube` – nhánh chữ Y tại (-450, 125, 2700)
- **Chi tiết phải dựng:** Ống inox Ø250: đoạn đứng từ Z 2 850 (dưới ống mềm cách cân) xuống Z 2 550, rồi nghiêng 45° xuống tới phễu; treo bằng giá dưới dầm sàn, vành chắn ở lỗ sàn không chạm ống. Nhánh Y cho ống phụ gia tại Z = 2 700, cửa thăm có nắp.
- **Nguồn:** giả định (bố trí sàn cân trên cao theo web-04); ống mềm cách cân theo review-01 M8

#### `feed_main_feeder` — Cân cấp liệu chính (loss-in-weight) (Main loss-in-weight feeder (K-Tron BSP-150-S))

- **Chức năng:** Định lượng 3 500 kg/h hạt PET theo khối lượng hao hụt.
- **Hình dạng / kích thước:** composite; bao 1100 × 900 × 700 (X × Y × Z)
- **Vị trí:** X -1000 … 100, Y -450 … 450, Z 3000 … 3700
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_platform_deck` – khung 3 cảm biến cân bắt lên sàn tại (-450, 0, 3000); `feed_main_hopper` – mặt bích + ống mềm cách cân tại (-450, 0, 3700); `feed_feeder_sleeves` – cửa xả đáy, ống mềm cách cân tại (-450, 0, 3000)
- **Chi tiết phải dựng:** Thân bơm rắn BSP trên khung 3 cảm biến cân (load cells), động cơ hộp số phía −Y, hộp điều khiển KCM nhỏ phía +Y. Cửa xả đáy tại X = −450, Y = 0.
- **Nguồn:** c069 (K-Tron BSP-150-S, 34–6 700 dm³/h, 3 cảm biến cân); kích thước thân giả định

#### `feed_main_hopper` — Phễu cân chính (Main feeder extension hopper)

- **Chức năng:** Chứa hạt cho cân, ≈ 450 L (≈ 6 phút ở 3,5 t/h).
- **Hình dạng / kích thước:** revolve; bao 900 × 900 × 1200 (X × Y × Z); trục Z; R 450
- **Vị trí:** X -900 … 0, Y -450 … 450, Z 3700 … 4900
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_main_feeder` – mặt bích tại (-450, 0, 3700); `feed_vacuum_loader` – van nạp tại (-450, 0, 4900)
- **Chi tiết phải dựng:** Côn 400 + trụ Ø900 cao 800, kính thăm mức, cảm biến mức cao/thấp.
- **Nguồn:** c069 (phễu nối thêm); dung tích giả định lớn hơn 320 dm³ để thời gian nạp lại hợp lý

#### `feed_vacuum_loader` — Máy hút liệu chân không (Vacuum loader / receiver)

- **Chức năng:** Hút hạt từ silo và nạp lại phễu cân.
- **Hình dạng / kích thước:** revolve; bao 640 × 640 × 900 (X × Y × Z); trục Z; R 320
- **Vị trí:** X -770 … -130, Y -320 … 320, Z 4900 … 5800
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_main_hopper` – van lật xả tại (-450, 0, 4900); `feed_conveying_line` – cổng vào liệu tại (-450, 320, 5500)
- **Chi tiết phải dựng:** Bình Ø640 cao 900 với nắp lọc, van lật đáy, cổng liệu vào bên +Y, cổng hút khí trên nắp.
- **Nguồn:** specs §2 (máy hút liệu trên phễu); cỡ giả định

#### `feed_conveying_line` — Ống hút liệu từ silo (Pneumatic conveying line (stub))

- **Chức năng:** Ống vận chuyển hạt từ silo tới máy hút liệu (vẽ tới mép trên khung nhìn).
- **Hình dạng / kích thước:** pipe; bao 80 × 420 × 840 (X × Y × Z); R 40
- **Vị trí:** X -490 … -410, Y 320 … 740, Z 5460 … 6300
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_vacuum_loader` – khớp nối nhanh tại (-450, 320, 5500)
- **Chi tiết phải dựng:** Ống inox DN80 (OD 80), đầu trên để hở ký hiệu 'tới silo'.
- **Nguồn:** giả định

#### `feed_additive_feeder` — Cân phụ gia / masterbatch (Additive micro-feeder)

- **Chức năng:** Định lượng phụ gia (masterbatch, chất chống dính) vào ống rơi chính.
- **Hình dạng / kích thước:** composite; bao 700 × 500 × 1200 (X × Y × Z)
- **Vị trí:** X -1000 … -300, Y 600 … 1100, Z 3000 … 4200
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_platform_deck` – khung cân bắt lên sàn tại (-650, 850, 3000); `feed_feeder_sleeves` – cửa xả, ống mềm cách cân tại (-650, 850, 3000)
- **Chi tiết phải dựng:** Cân trục vít đôi 700 × 500 × 600 + phễu Ø500 cao 600 trên đỉnh.
- **Nguồn:** specs §2 (cân trục vít đôi nhỏ K-ML-D5-T35); giả định

#### `feed_additive_tube` — Ống phụ gia (Additive feed tube)

- **Chức năng:** Dẫn phụ gia vào nhánh Y của ống rơi chính.
- **Hình dạng / kích thước:** pipe; bao 278.6 × 775.6 × 190 (X × Y × Z); R 40
- **Vị trí:** X -690 … -411.4, Y 114.4 … 890, Z 2660 … 2850
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_feeder_sleeves` – đai kẹp, ống mềm cách cân tại (-650, 850, 2850); `feed_downpipe` – nhánh Y tại (-450, 125, 2700)
- **Chi tiết phải dựng:** Ống inox Ø80 bắt đầu dưới ống mềm cách cân (Z 2 850).
- **Nguồn:** giả định

#### `feed_feeder_sleeves` — Ống mềm cách cân ở cửa xả (Feeder outlet flexible sleeves)

- **Chức năng:** Tách cửa xả của các cân loss-in-weight khỏi ống cứng để ống không tì lên cân, giữ độ chính xác định lượng.
- **Hình dạng / kích thước:** cyl; bao 2270 × 1220 × 150 (X × Y × Z); số lượng 3
- **Vị trí:** X -785 … 1485, Y -135 … 1085, Z 2850 … 3000
- **Vật liệu / màu:** white `#EDEEEE`
- **Nối với:** `feed_main_feeder` – đai kẹp cửa xả tại (-450, 0, 3000); `feed_downpipe` – đai kẹp tại (-450, 0, 2850); `feed_additive_feeder` – đai kẹp cửa xả tại (-650, 850, 3000); `feed_additive_tube` – đai kẹp tại (-650, 850, 2850); `sidefeed_feeder` – đai kẹp cửa xả tại (1350, 950, 3000); `sidefeed_downpipe` – đai kẹp tại (1350, 950, 2850)
- **Chi tiết phải dựng:** 3 ống bạt trắng dài 150 (Z 2 850–3 000) nằm trong lỗ sàn: Ø270 tại (−450, 0), Ø100 tại (−650, 850), Ø170 tại (1 350, 950); mỗi ống 2 đai kẹp inox.
- **Nguồn:** review-01 M8; giả định (thực hành chuẩn cho cân loss-in-weight)

#### `feed_platform_deck` — Sàn thao tác cân cấp liệu (Feeder mezzanine deck)

- **Chức năng:** Mặt bằng đặt các cân cấp liệu, lối đi bảo trì trên cao.
- **Hình dạng / kích thước:** frame; bao 4550 × 4100 × 220 (X × Y × Z)
- **Vị trí:** X -2700 … 1850, Y -2700 … 1400, Z 2780 … 3000
- **Vật liệu / màu:** grating `#9EA3A6`
- **Nối với:** `feed_platform_columns_rear` – dầm bắt bulông lên đỉnh cột tại (-450, -2600, 2780); `feed_platform_columns_front` – dầm bắt bulông lên đỉnh cột tại (-450, 1300, 2780); `feed_platform_railing` – cột lan can bắt mép dầm tại (0, 1400, 3000); `feed_stair` – chiếu nghỉ đầu cầu thang tại (-2700, -2300, 3000); `feed_main_feeder` – đỡ cân tại (-450, 0, 3000)
- **Chi tiết phải dựng:** Dầm chính HEA180 (Z 2 780–2 960) + sàn lưới mạ kẽm 40 mm (Z 2 960–3 000). Lỗ sàn có vành chắn cho ống mềm cách cân của ống rơi chính (X −450, Y 0), ống phụ gia (X −650, Y 850), ống side feeder (X 1 350, Y 950); vành không chạm ống. Diện tích 4 550 × 4 100 (Y −2 700 … 1 400), phủ trên lantern, hộp số, B1, B2; mép sau lùi ra để lối đi phía −Y rộng ≥ 950. Bố trí dầm (beams_mm, tâm dầm Z 2 870): dầm biên HEA180 theo X trên hai hàng cột (Y −2 600 và 1 300); dầm chính HEA180 theo Y trên các đường cột X −2 600, −450, 1 750. Dầm chính X −450 bị ngắt tại Y ±260 quanh lỗ ống rơi chính (Ø270 + vành chắn); hai dầm viền (trimmer) HEA180 theo X ở Y ±260 từ X −760 tới −140 đỡ hai đầu dầm ngắt; đầu dầm viền tựa lên hai dầm phụ IPE160 theo Y tại X −760 và −140. Dầm phụ IPE160 theo Y tại X −1 900, −1 200, 300, 1 000 đỡ tấm lưới (khoảng ≤ 750); lỗ ống phụ gia (−650, 850) và ống side feeder (1 350, 950) nằm giữa các dầm phụ.
- **Nguồn:** web-04/05 (cân trên tầng lửng); specs §2 (mặt sàn 2 800–3 200); kích thước giả định

#### `feed_platform_columns_rear` — Cột sàn thao tác (phía sau −Y) (Mezzanine columns, rear row)

- **Chức năng:** Đỡ sàn thao tác xuống nền.
- **Hình dạng / kích thước:** frame; bao 4550 × 200 × 2780 (X × Y × Z); số lượng 3
- **Vị trí:** X -2700 … 1850, Y -2700 … -2500, Z 0 … 2780
- **Vật liệu / màu:** grating `#9EA3A6`
- **Nối với:** `feed_platform_deck` – đỉnh cột bắt dầm tại (-450, -2600, 2780); `ctx_floor` – tấm đế + bulông neo tại (-450, -2600, 0)
- **Chi tiết phải dựng:** 3 cột HEB200 tại X = −2 600, −450, 1 750; Y = -2600; tấm đế 400 × 400, giằng góc dưới dầm.
- **Nguồn:** giả định

#### `feed_platform_columns_front` — Cột sàn thao tác (phía vận hành +Y) (Mezzanine columns, front row)

- **Chức năng:** Đỡ sàn thao tác xuống nền.
- **Hình dạng / kích thước:** frame; bao 4550 × 200 × 2780 (X × Y × Z); số lượng 3
- **Vị trí:** X -2700 … 1850, Y 1200 … 1400, Z 0 … 2780
- **Vật liệu / màu:** grating `#9EA3A6`
- **Nối với:** `feed_platform_deck` – đỉnh cột bắt dầm tại (-450, 1300, 2780); `ctx_floor` – tấm đế + bulông neo tại (-450, 1300, 0)
- **Chi tiết phải dựng:** 3 cột HEB200 tại X = −2 600, −450, 1 750; Y = 1300; tấm đế 400 × 400, giằng góc dưới dầm.
- **Nguồn:** giả định

#### `feed_platform_railing` — Lan can sàn thao tác (Mezzanine railing with kick plates)

- **Chức năng:** Chống ngã từ sàn cao 3 m.
- **Hình dạng / kích thước:** frame; bao 4550 × 4100 × 1100 (X × Y × Z)
- **Vị trí:** X -2700 … 1850, Y -2700 … 1400, Z 3000 … 4100
- **Vật liệu / màu:** yellow `#F2C200`
- **Nối với:** `feed_platform_deck` – cột lan can bắt mép dầm tại (0, 1400, 3000); `ctrl_estop_platform` – hộp dừng khẩn trên cột lan can tại (-450, 1390, 4000)
- **Chi tiết phải dựng:** Tay vịn ống Ø42 cao 1 100, thanh giữa 550, tấm chắn chân 150, cột bước ≤ 1 500, màu vàng an toàn. Chừa lối lên cầu thang ở mép −X đoạn Y −2 650 … −1 950.
- **Nguồn:** web-04/05 (lan can và tấm chắn chân màu vàng)

#### `feed_stair` — Cầu thang lên sàn (Mezzanine stair)

- **Chức năng:** Lối lên sàn cân cấp liệu (45°).
- **Hình dạng / kích thước:** frame; bao 3000 × 700 × 4000 (X × Y × Z)
- **Vị trí:** X -5700 … -2700, Y -2650 … -1950, Z 0 … 4000
- **Vật liệu / màu:** yellow `#F2C200`
- **Nối với:** `feed_platform_deck` – chiếu nghỉ trên bắt vào dầm sàn tại (-2700, -2300, 3000); `ctx_floor` – chân thang bắt bulông neo tại (-5700, -2300, 0)
- **Chi tiết phải dựng:** Rộng 700, 45°, 15 bậc lưới cao 200, hai dầm thang (stringers) thép mạ kẽm, tay vịn vàng hai bên cao 1 000. Outline XZ là hình bao bên: mép dưới dầm thang từ (−5 400, 0) tới (−2 700, 2 700), tay vịn từ (−5 700, 1 000) tới (−2 700, 4 000).
- **Nguồn:** web-04 (cầu thang vàng cạnh máy); vị trí phía −Y, lùi ra theo review-01 I2 (lối đi 950 dọc khung, 850 trước ống cáp trung thế)

#### `feed_control_cabinet` — Tủ điều khiển cân cấp liệu (Feeder control cabinet)

- **Chức năng:** Bộ điều khiển các cân (KCM), cấp nguồn máy hút liệu.
- **Hình dạng / kích thước:** box; bao 600 × 300 × 1400 (X × Y × Z)
- **Vị trí:** X -2400 … -1800, Y 1050 … 1350, Z 3000 … 4400
- **Vật liệu / màu:** cabinet `#D8DAD6`
- **Nối với:** `feed_platform_deck` – chân tủ bắt lên sàn tại (-2100, 1200, 3000)
- **Chi tiết phải dựng:** Tủ 600 × 300 × 1 400 RAL 7035 có màn hình nhỏ ở cửa.
- **Nguồn:** giả định

#### `sidefeed_adapter` — Bích cửa bên B2 (Side-feeder adapter plate)

- **Chức năng:** Nối thân side feeder vào cửa bên +Y của B2.
- **Hình dạng / kích thước:** box; bao 370 × 80 × 320 (X × Y × Z)
- **Vị trí:** X 1165 … 1535, Y 250 … 330, Z 1040 … 1360
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_b2` – 8 bulông M24 quanh cửa bên tại (1350, 260, 1200); `sidefeed_barrel` – 8 bulông M24 tại (1350, 330, 1200)
- **Chi tiết phải dựng:** Tấm thép 370 × 80 × 320 lỗ hình số 8.
- **Nguồn:** p08_side_feeder (mặt bích bắt bulông vào hông xi lanh)

#### `sidefeed_barrel` — Thân side feeder trục vít đôi (ZSB) (Twin-screw side feeder barrel (ZSB, size assumed))

- **Chức năng:** Ép liệu phụ (mảnh vụn biên tấm, phụ gia bột) vào cửa bên B2.
- **Hình dạng / kích thước:** box; bao 330 × 770 × 260 (X × Y × Z); trục Y
- **Vị trí:** X 1185 … 1515, Y 330 … 1100, Z 1070 … 1330
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `sidefeed_adapter` – mặt bích tại (1350, 330, 1200); `sidefeed_gearbox` – mặt bích + khớp then tại (1350, 1100, 1200); `sidefeed_hopper` – lỗ nạp đỉnh tại (1350, 950, 1330)
- **Chi tiết phải dựng:** Thân hình số 8 ngang 330 × 260 dài 770 theo Y: hai cung tròn R130 tâm X 1 315 và 1 385 (outline_mm), eo nhỏ trên và dưới tại X 1 350; 2 lỗ trục vít Ø112 tâm X 1 305 và 1 395, trục theo Y tại Z = 1 200. Lỗ nạp đỉnh gần đầu ngoài, áo nước làm mát, bích hai đầu.
- **Nguồn:** p08_side_feeder, p06 cutaway (side feeder 2 trục vít ngang vào hông xi lanh); c024 (ZE 110 dùng ZSFE 120) → cỡ 160 giả định

#### `sidefeed_hopper` — Phễu side feeder (Side-feeder inlet hopper)

- **Chức năng:** Nhận liệu từ cân phụ.
- **Hình dạng / kích thước:** box; bao 300 × 260 × 270 (X × Y × Z)
- **Vị trí:** X 1200 … 1500, Y 820 … 1080, Z 1330 … 1600
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `sidefeed_barrel` – mặt bích tại (1350, 950, 1330); `sidefeed_downpipe` – cổ ống tại (1350, 950, 1600)
- **Chi tiết phải dựng:** Phễu inox 300 × 260 cao 270, kính thăm.
- **Nguồn:** p08_side_feeder

#### `sidefeed_gearbox` — Hộp số side feeder (Side-feeder gearbox)

- **Chức năng:** Giảm tốc và chia mômen ra 2 trục vít side feeder.
- **Hình dạng / kích thước:** box; bao 350 × 350 × 400 (X × Y × Z)
- **Vị trí:** X 1175 … 1525, Y 1100 … 1450, Z 1000 … 1400
- **Vật liệu / màu:** km_blue `#008DC3`
- **Nối với:** `sidefeed_barrel` – mặt bích tại (1350, 1100, 1200); `sidefeed_motor` – mặt bích động cơ tại (1350, 1450, 1200); `sidefeed_cart` – chân hộp số bắt lên xe tại (1350, 1300, 1000)
- **Chi tiết phải dựng:** Hộp 350 × 350 × 400, nút thăm dầu.
- **Nguồn:** p06 cutaway (hộp số + động cơ xám nhỏ trên xe đẩy); màu giả định

#### `sidefeed_motor` — Động cơ side feeder 22 kW (Side-feeder motor 22 kW)

- **Chức năng:** Quay trục vít side feeder.
- **Hình dạng / kích thước:** cyl; bao 360 × 600 × 380 (X × Y × Z); trục Y; R 180
- **Vị trí:** X 1170 … 1530, Y 1450 … 2050, Z 1000 … 1380
- **Vật liệu / màu:** motor `#2B528C`
- **Nối với:** `sidefeed_gearbox` – mặt bích B5 tại (1350, 1450, 1200); `sidefeed_cart` – chân đỡ tại (1350, 1750, 1000)
- **Chi tiết phải dựng:** Động cơ nằm Ø360 dài 600, nắp quạt, hộp đấu dây trên nóc.
- **Nguồn:** giả định (động cơ AC 22 kW biến tần)

#### `sidefeed_cart` — Xe đỡ side feeder (Side-feeder wheeled cart)

- **Chức năng:** Đỡ hộp số + động cơ, cho phép kéo side feeder ra theo +Y khi bảo trì.
- **Hình dạng / kích thước:** frame; bao 500 × 1090 × 1000 (X × Y × Z)
- **Vị trí:** X 1100 … 1600, Y 1010 … 2100, Z 0 … 1000
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `sidefeed_gearbox` – tấm đỉnh tại (1350, 1300, 1000); `sidefeed_motor` – tấm đỉnh tại (1350, 1750, 1000); `ctx_floor` – 4 bánh xe khoá tại (1350, 1500, 0)
- **Chi tiết phải dựng:** Khung thép trắng 500 × 1 090 cao 1 000, 4 bánh xe có khoá, tem cảnh báo điện.
- **Nguồn:** p06_cutaway_side_feeder_cart (xe thép trắng có bánh xe)

#### `sidefeed_downpipe` — Ống rơi side feeder (Side-feeder down-pipe)

- **Chức năng:** Dẫn liệu phụ từ cân trên sàn xuống phễu side feeder.
- **Hình dạng / kích thước:** pipe; bao 150 × 150 × 1250 (X × Y × Z); R 75
- **Vị trí:** X 1275 … 1425, Y 875 … 1025, Z 1600 … 2850
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_feeder_sleeves` – đai kẹp, ống mềm cách cân tại (1350, 950, 2850); `sidefeed_hopper` – cổ ống tại (1350, 950, 1600)
- **Chi tiết phải dựng:** Ống inox Ø150 có đoạn ống mềm ở đáy.
- **Nguồn:** giả định

#### `sidefeed_feeder` — Cân cấp liệu side feeder (Side-feeder loss-in-weight feeder)

- **Chức năng:** Định lượng liệu phụ cho side feeder.
- **Hình dạng / kích thước:** composite; bao 700 × 600 × 550 (X × Y × Z)
- **Vị trí:** X 1000 … 1700, Y 650 … 1250, Z 3000 … 3550
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_platform_deck` – khung cân tại (1350, 950, 3000); `feed_feeder_sleeves` – cửa xả, ống mềm cách cân tại (1350, 950, 3000); `sidefeed_feeder_hopper` – mặt bích tại (1350, 950, 3550)
- **Chi tiết phải dựng:** Cân trục vít đôi trên 3 cảm biến cân, động cơ phía −X.
- **Nguồn:** giả định (cân trục vít đôi cỡ K-ML-D5-T35)

#### `sidefeed_feeder_hopper` — Phễu cân side feeder (Side-feeder feeder hopper)

- **Chức năng:** Chứa liệu phụ.
- **Hình dạng / kích thước:** revolve; bao 600 × 600 × 700 (X × Y × Z); trục Z; R 300
- **Vị trí:** X 1050 … 1650, Y 650 … 1250, Z 3550 … 4250
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `sidefeed_feeder` – mặt bích tại (1350, 950, 3550)
- **Chi tiết phải dựng:** Phễu Ø600 cao 700 có nắp.
- **Nguồn:** giả định

### Đoạn gia công (processing section) — 28 mục

#### `barrel_b1` — Xi lanh B1 – cấp liệu 4D (Barrel B1, feed barrel 4D (water-cooled))

- **Chức năng:** Nhận hạt PET từ miệng cấp liệu; làm mát bằng nước để hạt không chảy sớm.
- **Hình dạng / kích thước:** revolve; bao 676 × 640 × 640 (X × Y × Z); trục X; R 260
- **Vị trí:** X 0 … 676, Y -320 … 320, Z 880 … 1520
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `lantern` – mặt bích, 20 bulông cấy M24 trên PCD 560 tại (0, 0, 1200); `feed_throat` – mặt gia công đỉnh, 8 bulông M20 tại (340, 0, 1460); `barrel_joint_1` – mặt bích Ø640, 20 bulông cấy M24 tại (666, 0, 1480); `screws` – lỗ hình số 8 chứa 2 trục vít tại (338, 0, 1200); `barrel_cw_hoses` – đầu nối nhanh nước vào ở đáy tại (200, 0, 940); `barrel_cw_hoses` – đầu nối nhanh nước ra ở đáy tại (476, 0, 940)
- **Chi tiết phải dựng:** Thân trụ Ø520, mặt bích Ø640 × 50 hai đầu; mỗi bích 20 lỗ Ø26 trên PCD 560 (mép lỗ cách mép bích 27 mm), một bích có gờ định tâm, bích kia có rãnh. Sau mỗi bích thân tiện thắt Ø500 dài 40 mm (vùng đặt đai ốc), để có khe 12 mm cho khẩu 12 cạnh thành mỏng khi tháo vỏ nhiệt; vỏ nhiệt bắt đầu ngay sau đoạn thắt. Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71). Lỗ nạp trên đỉnh 360 × 300 tại X 160–520, mặt gia công phẳng cho hộp miệng nạp. Không có băng nhiệt; áo nước làm mát, 2 đầu nối nước ở đáy tại X = 200 (vào) và 476 (ra). Đầu X = 0: bích Ø640 bắt 20 bulông cấy M24 trên PCD 560 vào lantern, đai ốc 12 cạnh phía B1. Cặp nhiệt B1 cắm nghiêng 40° ở góc trên phía −Y, chân tại (X 338, Y -167, Z 1399), để tránh hộp miệng nạp.
- **Nguồn:** c001 D = 169, c031 đoạn 4D/6D, c032 thép thấm nitơ; DECISIONS 9 (1×4D + 5×6D), DECISIONS 11 (nối bích bắt bulông); hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut); Ø thân 520 / bích 600 giả định (lỗ số 8 rộng 311 + thành ≈ 105)

#### `barrel_b2` — Xi lanh B2 – 6D mở bên (side feeder) (Barrel B2, 6D side-open (combination) barrel)

- **Chức năng:** Vận chuyển hạt, nhận liệu phụ từ side feeder qua cửa bên +Y, bắt đầu nóng chảy ở cuối đoạn.
- **Hình dạng / kích thước:** revolve; bao 1014 × 640 × 640 (X × Y × Z); trục X; R 260
- **Vị trí:** X 676 … 1690, Y -320 … 320, Z 880 … 1520
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_joint_1` – mặt bích Ø640, 20 bulông cấy M24 tại (686, 0, 1480); `barrel_joint_2` – mặt bích Ø640, 20 bulông cấy M24 tại (1680, 0, 1480); `screws` – lỗ hình số 8 chứa 2 trục vít tại (1183, 0, 1200); `barrel_cw_hoses` – đầu nối nước vào, góc dưới +Y 45° tại (876, 184, 1016); `barrel_cw_hoses` – đầu nối nước ra, góc dưới +Y 45° tại (1490, 184, 1016); `sidefeed_adapter` – mặt bích cửa bên +Y tại (1350, 260, 1200); `barrel_support_1` – tấm trượt tại (1183, 0, 940)
- **Chi tiết phải dựng:** Thân trụ Ø520, mặt bích Ø640 × 50 hai đầu; mỗi bích 20 lỗ Ø26 trên PCD 560 (mép lỗ cách mép bích 27 mm), một bích có gờ định tâm, bích kia có rãnh. Sau mỗi bích thân tiện thắt Ø500 dài 40 mm (vùng đặt đai ốc), để có khe 12 mm cho khẩu 12 cạnh thành mỏng khi tháo vỏ nhiệt; vỏ nhiệt bắt đầu ngay sau đoạn thắt. Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71). Cửa bên +Y 340 × 260 tại X 1 180–1 520 (hình số 8 nhìn ngang) có mặt bích cho side feeder. 2 băng nhiệt có cửa sổ tránh cửa bên; lỗ khoan nước làm mát dọc thân. 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 876 (vào) và 1490 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- **Nguồn:** c001 D = 169, c031 đoạn 4D/6D, c032 thép thấm nitơ; DECISIONS 9 (1×4D + 5×6D), DECISIONS 11 (nối bích bắt bulông); hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut); Ø thân 520 / bích 600 giả định (lỗ số 8 rộng 311 + thành ≈ 105)

#### `barrel_b3` — Xi lanh B3 – 6D thoát khí chân không vùng 1 (Barrel B3, 6D top-open (first vacuum vent))

- **Chức năng:** Nóng chảy (khối nhào) rồi hút chân không nhẹ (≈ 50 mbar) ngay khi nhựa vừa chảy, rút phần lớn hơi nước trước khi PET bị thuỷ phân và không cho không khí lọt vào.
- **Hình dạng / kích thước:** revolve; bao 1014 × 640 × 640 (X × Y × Z); trục X; R 260
- **Vị trí:** X 1690 … 2704, Y -320 … 320, Z 880 … 1520
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_joint_2` – mặt bích Ø640, 20 bulông cấy M24 tại (1700, 0, 1480); `barrel_joint_3` – mặt bích Ø640, 20 bulông cấy M24 tại (2694, 0, 1480); `screws` – lỗ hình số 8 chứa 2 trục vít tại (2197, 0, 1200); `barrel_cw_hoses` – đầu nối nước vào, góc dưới +Y 45° tại (1890, 184, 1016); `barrel_cw_hoses` – đầu nối nước ra, góc dưới +Y 45° tại (2504, 184, 1016); `barrel_vent_dome_2` – mặt bích vent insert tại (2150, 0, 1460)
- **Chi tiết phải dựng:** Thân trụ Ø520, mặt bích Ø640 × 50 hai đầu; mỗi bích 20 lỗ Ø26 trên PCD 560 (mép lỗ cách mép bích 27 mm), một bích có gờ định tâm, bích kia có rãnh. Sau mỗi bích thân tiện thắt Ø500 dài 40 mm (vùng đặt đai ốc), để có khe 12 mm cho khẩu 12 cạnh thành mỏng khi tháo vỏ nhiệt; vỏ nhiệt bắt đầu ngay sau đoạn thắt. Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71). Lỗ trên đỉnh 320 × 280 tại X 1 990–2 310 với tấm lót (vent insert); vòm chân không 2 lắp trên. 2 băng nhiệt có khe tại lỗ. 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 1890 (vào) và 2504 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- **Nguồn:** c001 D = 169, c031 đoạn 4D/6D, c032 thép thấm nitơ; DECISIONS 9 (1×4D + 5×6D), DECISIONS 11 (nối bích bắt bulông); hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut); Ø thân 520 / bích 600 giả định (lỗ số 8 rộng 311 + thành ≈ 105)

#### `barrel_b4` — Xi lanh B4 – 6D kín (Barrel B4, 6D closed)

- **Chức năng:** Trộn, đồng nhất nhựa nóng chảy; trước B5 có phần tử nghịch tạo nút nhựa kín chân không.
- **Hình dạng / kích thước:** revolve; bao 1014 × 640 × 640 (X × Y × Z); trục X; R 260
- **Vị trí:** X 2704 … 3718, Y -320 … 320, Z 880 … 1520
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_joint_3` – mặt bích Ø640, 20 bulông cấy M24 tại (2714, 0, 1480); `barrel_joint_4` – mặt bích Ø640, 20 bulông cấy M24 tại (3708, 0, 1480); `screws` – lỗ hình số 8 chứa 2 trục vít tại (3211, 0, 1200); `barrel_cw_hoses` – đầu nối nước vào, góc dưới +Y 45° tại (2904, 184, 1016); `barrel_cw_hoses` – đầu nối nước ra, góc dưới +Y 45° tại (3518, 184, 1016); `barrel_support_2` – tấm trượt tại (3211, 0, 940)
- **Chi tiết phải dựng:** Thân trụ Ø520, mặt bích Ø640 × 50 hai đầu; mỗi bích 20 lỗ Ø26 trên PCD 560 (mép lỗ cách mép bích 27 mm), một bích có gờ định tâm, bích kia có rãnh. Sau mỗi bích thân tiện thắt Ø500 dài 40 mm (vùng đặt đai ốc), để có khe 12 mm cho khẩu 12 cạnh thành mỏng khi tháo vỏ nhiệt; vỏ nhiệt bắt đầu ngay sau đoạn thắt. Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71). 2 băng nhiệt, lỗ khoan nước làm mát, 1 cặp nhiệt. 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 2904 (vào) và 3518 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- **Nguồn:** c001 D = 169, c031 đoạn 4D/6D, c032 thép thấm nitơ; DECISIONS 9 (1×4D + 5×6D), DECISIONS 11 (nối bích bắt bulông); hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut); Ø thân 520 / bích 600 giả định (lỗ số 8 rộng 311 + thành ≈ 105)

#### `barrel_b5` — Xi lanh B5 – 6D thoát khí chân không sâu (vùng 2) (Barrel B5, 6D top-open (deep vacuum vent))

- **Chức năng:** Hút chân không sâu (5–20 mbar) để khử nốt ẩm, acetaldehyde và oligome của PET không sấy.
- **Hình dạng / kích thước:** revolve; bao 1014 × 640 × 640 (X × Y × Z); trục X; R 260
- **Vị trí:** X 3718 … 4732, Y -320 … 320, Z 880 … 1520
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_joint_4` – mặt bích Ø640, 20 bulông cấy M24 tại (3728, 0, 1480); `barrel_joint_5` – mặt bích Ø640, 20 bulông cấy M24 tại (4722, 0, 1480); `screws` – lỗ hình số 8 chứa 2 trục vít tại (4225, 0, 1200); `barrel_cw_hoses` – đầu nối nước vào, góc dưới +Y 45° tại (3918, 184, 1016); `barrel_cw_hoses` – đầu nối nước ra, góc dưới +Y 45° tại (4532, 184, 1016); `barrel_vent_dome` – mặt bích vent insert tại (4120, 0, 1460)
- **Chi tiết phải dựng:** Thân trụ Ø520, mặt bích Ø640 × 50 hai đầu; mỗi bích 20 lỗ Ø26 trên PCD 560 (mép lỗ cách mép bích 27 mm), một bích có gờ định tâm, bích kia có rãnh. Sau mỗi bích thân tiện thắt Ø500 dài 40 mm (vùng đặt đai ốc), để có khe 12 mm cho khẩu 12 cạnh thành mỏng khi tháo vỏ nhiệt; vỏ nhiệt bắt đầu ngay sau đoạn thắt. Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71). Lỗ trên đỉnh 520 × 280 tại X 3 860–4 380 (≈ 3D) với tấm lót (vent insert); vòm chân không lắp trên. 2 băng nhiệt có khe tại lỗ. 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 3918 (vào) và 4532 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- **Nguồn:** c001 D = 169, c031 đoạn 4D/6D, c032 thép thấm nitơ; DECISIONS 9 (1×4D + 5×6D), DECISIONS 11 (nối bích bắt bulông); hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut); Ø thân 520 / bích 600 giả định (lỗ số 8 rộng 311 + thành ≈ 105)

#### `barrel_b6` — Xi lanh B6 – 6D kín tăng áp (Barrel B6, 6D closed (pressure build-up))

- **Chức năng:** Tăng áp đẩy nhựa vào đầu xi lanh.
- **Hình dạng / kích thước:** revolve; bao 1014 × 640 × 640 (X × Y × Z); trục X; R 260
- **Vị trí:** X 4732 … 5746, Y -320 … 320, Z 880 … 1520
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_joint_5` – mặt bích Ø640, 20 bulông cấy M24 tại (4742, 0, 1480); `melt_head_adapter` – mặt bích, 20 bulông cấy M24 trên PCD 560 tại (5746, 0, 1200); `screws` – lỗ hình số 8 chứa 2 trục vít tại (5239, 0, 1200); `barrel_cw_hoses` – đầu nối nước vào, góc dưới +Y 45° tại (4932, 184, 1016); `barrel_cw_hoses` – đầu nối nước ra, góc dưới +Y 45° tại (5546, 184, 1016); `barrel_support_3` – tấm trượt tại (5239, 0, 940)
- **Chi tiết phải dựng:** Thân trụ Ø520, mặt bích Ø640 × 50 hai đầu; mỗi bích 20 lỗ Ø26 trên PCD 560 (mép lỗ cách mép bích 27 mm), một bích có gờ định tâm, bích kia có rãnh. Sau mỗi bích thân tiện thắt Ø500 dài 40 mm (vùng đặt đai ốc), để có khe 12 mm cho khẩu 12 cạnh thành mỏng khi tháo vỏ nhiệt; vỏ nhiệt bắt đầu ngay sau đoạn thắt. Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71). Cổng bên +Y bịt mặt bích tròn (cổng phun lỏng dự phòng) tại X ≈ 5 400, Z = 1 200 – thấy qua tấm tròn 10 bulông của vỏ che C1 (trang 9). Mặt bích ra X = 5 746: 20 bulông cấy M24 trên PCD 560 vào bích đầu xi lanh. 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 4932 (vào) và 5546 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- **Nguồn:** c001 D = 169, c031 đoạn 4D/6D, c032 thép thấm nitơ; DECISIONS 9 (1×4D + 5×6D), DECISIONS 11 (nối bích bắt bulông); hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut); Ø thân 520 / bích 600 giả định (lỗ số 8 rộng 311 + thành ≈ 105)

#### `barrel_joint_1` — Mối nối bích bắt bulông 1 (X = 676) (Bolted flange joint 1)

- **Chức năng:** Ép hai mặt bích Ø640 của hai đoạn xi lanh vào nhau cho kín áp nhựa, định tâm hai lỗ số 8; tháo được khi đổi cấu hình xi lanh.
- **Hình dạng / kích thước:** revolve; bao 164 × 600 × 600 (X × Y × Z); số lượng 20; trục X; R 320
- **Vị trí:** X 594 … 758, Y -300 … 300, Z 900 … 1500
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_b1` – mặt bích đoạn trước, 20 lỗ Ø26 tại (666, 0, 1480); `barrel_b2` – mặt bích đoạn sau, 20 lỗ Ø26 tại (686, 0, 1480)
- **Chi tiết phải dựng:** 20 bulông cấy M24 cấp 10.9 chịu nhiệt, mỗi bulông 2 đai ốc 12 cạnh (Ø36 qua đỉnh) có vòng đệm, trên PCD 560, chia đều 18°, lệch 9° để không có bulông đúng đỉnh/đáy. Bulông dài 164: xuyên 2 bích × 50 mm, mỗi đầu đai ốc cao 24 + 8 mm ren thừa; đai ốc nằm trong vành r 262–298, trên đoạn thân thắt Ø500 (khe 12 mm), mép lỗ cách mép bích Ø640 27 mm. Giữa hai bích: gờ định tâm (centring spigot) Ø400 và mặt kín kim loại; mặt ngoài vành bích tiện bóng, đai ốc thép đen. Lực siết ≈ 20 × 200 kN = 4 MN, gấp ≈ 3 lần lực đẩy của nhựa 300 bar trên lỗ số 8 (≈ 1,2 MN). Không dùng M30 trên PCD 545: đai ốc M30 (đối đỉnh 53 mm) sẽ chạm thân xi lanh Ø520.
- **Nguồn:** c037 (ZE cỡ lớn nối các đoạn bằng bulông thay kẹp), web-01/02 (vành bích bắt bulông trên ZE 110 R UT thật); DECISIONS 11; cỡ bulông giả định (tính lực siết, kiểm tra chỗ đặt đai ốc)

#### `barrel_joint_2` — Mối nối bích bắt bulông 2 (X = 1690) (Bolted flange joint 2)

- **Chức năng:** Ép hai mặt bích Ø640 của hai đoạn xi lanh vào nhau cho kín áp nhựa, định tâm hai lỗ số 8; tháo được khi đổi cấu hình xi lanh.
- **Hình dạng / kích thước:** revolve; bao 164 × 600 × 600 (X × Y × Z); số lượng 20; trục X; R 320
- **Vị trí:** X 1608 … 1772, Y -300 … 300, Z 900 … 1500
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_b2` – mặt bích đoạn trước, 20 lỗ Ø26 tại (1680, 0, 1480); `barrel_b3` – mặt bích đoạn sau, 20 lỗ Ø26 tại (1700, 0, 1480)
- **Chi tiết phải dựng:** 20 bulông cấy M24 cấp 10.9 chịu nhiệt, mỗi bulông 2 đai ốc 12 cạnh (Ø36 qua đỉnh) có vòng đệm, trên PCD 560, chia đều 18°, lệch 9° để không có bulông đúng đỉnh/đáy. Bulông dài 164: xuyên 2 bích × 50 mm, mỗi đầu đai ốc cao 24 + 8 mm ren thừa; đai ốc nằm trong vành r 262–298, trên đoạn thân thắt Ø500 (khe 12 mm), mép lỗ cách mép bích Ø640 27 mm. Giữa hai bích: gờ định tâm (centring spigot) Ø400 và mặt kín kim loại; mặt ngoài vành bích tiện bóng, đai ốc thép đen. Lực siết ≈ 20 × 200 kN = 4 MN, gấp ≈ 3 lần lực đẩy của nhựa 300 bar trên lỗ số 8 (≈ 1,2 MN). Không dùng M30 trên PCD 545: đai ốc M30 (đối đỉnh 53 mm) sẽ chạm thân xi lanh Ø520.
- **Nguồn:** c037 (ZE cỡ lớn nối các đoạn bằng bulông thay kẹp), web-01/02 (vành bích bắt bulông trên ZE 110 R UT thật); DECISIONS 11; cỡ bulông giả định (tính lực siết, kiểm tra chỗ đặt đai ốc)

#### `barrel_joint_3` — Mối nối bích bắt bulông 3 (X = 2704) (Bolted flange joint 3)

- **Chức năng:** Ép hai mặt bích Ø640 của hai đoạn xi lanh vào nhau cho kín áp nhựa, định tâm hai lỗ số 8; tháo được khi đổi cấu hình xi lanh.
- **Hình dạng / kích thước:** revolve; bao 164 × 600 × 600 (X × Y × Z); số lượng 20; trục X; R 320
- **Vị trí:** X 2622 … 2786, Y -300 … 300, Z 900 … 1500
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_b3` – mặt bích đoạn trước, 20 lỗ Ø26 tại (2694, 0, 1480); `barrel_b4` – mặt bích đoạn sau, 20 lỗ Ø26 tại (2714, 0, 1480)
- **Chi tiết phải dựng:** 20 bulông cấy M24 cấp 10.9 chịu nhiệt, mỗi bulông 2 đai ốc 12 cạnh (Ø36 qua đỉnh) có vòng đệm, trên PCD 560, chia đều 18°, lệch 9° để không có bulông đúng đỉnh/đáy. Bulông dài 164: xuyên 2 bích × 50 mm, mỗi đầu đai ốc cao 24 + 8 mm ren thừa; đai ốc nằm trong vành r 262–298, trên đoạn thân thắt Ø500 (khe 12 mm), mép lỗ cách mép bích Ø640 27 mm. Giữa hai bích: gờ định tâm (centring spigot) Ø400 và mặt kín kim loại; mặt ngoài vành bích tiện bóng, đai ốc thép đen. Lực siết ≈ 20 × 200 kN = 4 MN, gấp ≈ 3 lần lực đẩy của nhựa 300 bar trên lỗ số 8 (≈ 1,2 MN). Không dùng M30 trên PCD 545: đai ốc M30 (đối đỉnh 53 mm) sẽ chạm thân xi lanh Ø520.
- **Nguồn:** c037 (ZE cỡ lớn nối các đoạn bằng bulông thay kẹp), web-01/02 (vành bích bắt bulông trên ZE 110 R UT thật); DECISIONS 11; cỡ bulông giả định (tính lực siết, kiểm tra chỗ đặt đai ốc)

#### `barrel_joint_4` — Mối nối bích bắt bulông 4 (X = 3718) (Bolted flange joint 4)

- **Chức năng:** Ép hai mặt bích Ø640 của hai đoạn xi lanh vào nhau cho kín áp nhựa, định tâm hai lỗ số 8; tháo được khi đổi cấu hình xi lanh.
- **Hình dạng / kích thước:** revolve; bao 164 × 600 × 600 (X × Y × Z); số lượng 20; trục X; R 320
- **Vị trí:** X 3636 … 3800, Y -300 … 300, Z 900 … 1500
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_b4` – mặt bích đoạn trước, 20 lỗ Ø26 tại (3708, 0, 1480); `barrel_b5` – mặt bích đoạn sau, 20 lỗ Ø26 tại (3728, 0, 1480)
- **Chi tiết phải dựng:** 20 bulông cấy M24 cấp 10.9 chịu nhiệt, mỗi bulông 2 đai ốc 12 cạnh (Ø36 qua đỉnh) có vòng đệm, trên PCD 560, chia đều 18°, lệch 9° để không có bulông đúng đỉnh/đáy. Bulông dài 164: xuyên 2 bích × 50 mm, mỗi đầu đai ốc cao 24 + 8 mm ren thừa; đai ốc nằm trong vành r 262–298, trên đoạn thân thắt Ø500 (khe 12 mm), mép lỗ cách mép bích Ø640 27 mm. Giữa hai bích: gờ định tâm (centring spigot) Ø400 và mặt kín kim loại; mặt ngoài vành bích tiện bóng, đai ốc thép đen. Lực siết ≈ 20 × 200 kN = 4 MN, gấp ≈ 3 lần lực đẩy của nhựa 300 bar trên lỗ số 8 (≈ 1,2 MN). Không dùng M30 trên PCD 545: đai ốc M30 (đối đỉnh 53 mm) sẽ chạm thân xi lanh Ø520.
- **Nguồn:** c037 (ZE cỡ lớn nối các đoạn bằng bulông thay kẹp), web-01/02 (vành bích bắt bulông trên ZE 110 R UT thật); DECISIONS 11; cỡ bulông giả định (tính lực siết, kiểm tra chỗ đặt đai ốc)

#### `barrel_joint_5` — Mối nối bích bắt bulông 5 (X = 4732) (Bolted flange joint 5)

- **Chức năng:** Ép hai mặt bích Ø640 của hai đoạn xi lanh vào nhau cho kín áp nhựa, định tâm hai lỗ số 8; tháo được khi đổi cấu hình xi lanh.
- **Hình dạng / kích thước:** revolve; bao 164 × 600 × 600 (X × Y × Z); số lượng 20; trục X; R 320
- **Vị trí:** X 4650 … 4814, Y -300 … 300, Z 900 … 1500
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_b5` – mặt bích đoạn trước, 20 lỗ Ø26 tại (4722, 0, 1480); `barrel_b6` – mặt bích đoạn sau, 20 lỗ Ø26 tại (4742, 0, 1480)
- **Chi tiết phải dựng:** 20 bulông cấy M24 cấp 10.9 chịu nhiệt, mỗi bulông 2 đai ốc 12 cạnh (Ø36 qua đỉnh) có vòng đệm, trên PCD 560, chia đều 18°, lệch 9° để không có bulông đúng đỉnh/đáy. Bulông dài 164: xuyên 2 bích × 50 mm, mỗi đầu đai ốc cao 24 + 8 mm ren thừa; đai ốc nằm trong vành r 262–298, trên đoạn thân thắt Ø500 (khe 12 mm), mép lỗ cách mép bích Ø640 27 mm. Giữa hai bích: gờ định tâm (centring spigot) Ø400 và mặt kín kim loại; mặt ngoài vành bích tiện bóng, đai ốc thép đen. Lực siết ≈ 20 × 200 kN = 4 MN, gấp ≈ 3 lần lực đẩy của nhựa 300 bar trên lỗ số 8 (≈ 1,2 MN). Không dùng M30 trên PCD 545: đai ốc M30 (đối đỉnh 53 mm) sẽ chạm thân xi lanh Ø520.
- **Nguồn:** c037 (ZE cỡ lớn nối các đoạn bằng bulông thay kẹp), web-01/02 (vành bích bắt bulông trên ZE 110 R UT thật); DECISIONS 11; cỡ bulông giả định (tính lực siết, kiểm tra chỗ đặt đai ốc)

#### `barrel_heater_shells` — Băng nhiệt gốm bọc inox (Ceramic band heater shells)

- **Chức năng:** Gia nhiệt xi lanh B2–B6, mỗi đoạn 6D một vùng nhiệt ≈ 25 kW.
- **Hình dạng / kích thước:** revolve; bao 4890 × 580 × 580 (X × Y × Z); số lượng 10; trục X
- **Vị trí:** X 766 … 5656, Y -290 … 290, Z 910 … 1490
- **Vật liệu / màu:** polished `#D5D9DD`
- **Nối với:** `barrel_b2` – kẹp bulông quanh thân tại (1183, 0, 1490); `barrel_b3` – kẹp bulông quanh thân tại (2197, 0, 1490); `barrel_b4` – kẹp bulông quanh thân tại (3211, 0, 1490); `barrel_b5` – kẹp bulông quanh thân tại (4225, 0, 1490); `barrel_b6` – kẹp bulông quanh thân tại (5239, 0, 1490)
- **Chi tiết phải dựng:** 10 vỏ (2 mỗi đoạn 6D), mỗi vỏ Ø580 dài 380, gồm 2 nửa bản lề, kẹp bằng 2 bulông, mép có vòng gân đục lỗ. Mỗi vỏ bắt đầu cách mặt đầu đoạn 90 mm (chừa chỗ đai ốc của mối nối bích); giữa hai vỏ của một đoạn có băng thân trần 74 mm cho gối đỡ. Vỏ có cửa sổ tại cửa bên B2 và lỗ đỉnh B3/B5; rãnh 50 mm ở góc dưới +Y tại X = đầu đoạn + 200 và cuối đoạn − 200 cho đầu nối nước. Hộp đấu nhỏ trên mỗi vỏ, cáp bọc lưới inox đi xuống hộp đấu dây phía −Y.
- **Nguồn:** web-01/02 (vỏ nhiệt inox bóng, mép có gân); c018 (30 kW/đoạn trên ZE 180) → 25 kW giả định

#### `screws` — Hai trục vít đồng hướng (Co-rotating twin screws)

- **Chức năng:** Vận chuyển, nóng chảy, trộn, khử khí và tăng áp nhựa; tự làm sạch lẫn nhau.
- **Hình dạng / kích thước:** composite; bao 6146 × 309.6 × 167.6 (X × Y × Z); trục X
- **Vị trí:** X -400 … 5746, Y -154.8 … 154.8, Z 1116.2 … 1283.8
- **Vật liệu / màu:** dark_steel `#5F656B`
- **Nối với:** `lantern` – trục then hoa 24 răng vào ống then hoa tại (-400, 0, 1200); `barrel_b1` – nằm trong lỗ số 8 tại (338, 0, 1200); `barrel_b5` – thấy qua lỗ thoát khí tại (4120, 0, 1200)
- **Chi tiết phải dựng:** 2 trục tại Y = ±71, Z = 1 200, Ø ngoài 167,5, lõi 114,6, 2 đầu ren (2-flight). Trình tự phần tử (X từ–tới): −400–0 trục then hoa trong lantern; 0–1 100 vận chuyển bước 1,5D (miệng nạp 160–520); 1 100–1 560 vận chuyển bước 1,5D dưới cửa side feeder (1 180–1 520); 1 560–1 880 khối nhào KB 45°/5 (nóng chảy); 1 880–1 950 KB 90° (nút nhựa, kết thúc trước lỗ vùng 1 ở 1 990); 1 950–2 420 vận chuyển bước rộng 1,5D dưới lỗ vùng 1 (1 990–2 310); 2 420–2 900 vận chuyển 1D; 2 900–3 380 khối nhào KB 45°/5 + KB 90° (trộn); 3 380–3 620 vận chuyển 1D; 3 620–3 720 phần tử nghịch LH (nút nhựa trước vùng 2); 3 720–4 450 vận chuyển bước rộng 1,5D dưới lỗ vùng 2 (3 860–4 380); 4 450–5 746 vận chuyển 1D → 0,75D (tăng áp). Thấy được qua miệng nạp B1, cửa B3 và vòm B5; cho bản vẽ cắt riêng (cut-away).
- **Nguồn:** c001/c002 (D 169, rãnh 27,2 → lõi 114,6), centre distance 142 (specs §1); c017 (then hoa 24 răng trên ZE 180); trình tự phần tử giả định

#### `barrel_vent_dome_2` — Vòm thoát khí chân không vùng 1 (B3) (First vacuum vent dome on B3)

- **Chức năng:** Buồng kín trên lỗ B3, hút chân không nhẹ (≈ 50 mbar) để rút hơi nước ngay sau vùng chảy.
- **Hình dạng / kích thước:** extrude; bao 400 × 450 × 505 (X × Y × Z)
- **Vị trí:** X 1950 … 2350, Y -240 … 210, Z 1455 … 1960
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `barrel_b3` – mặt bích vent insert 8 bulông tại (2150, 0, 1460); `barrel_cover_c6` – xuyên qua lỗ khoét 420 × 380 tại (2150, 0, 1650); `vac_valve_2` – bích DN100 phía −Y tại (2150, -240, 1800); `vac_gauge_dome_2` – ren trên nắp tại (2280, 0, 1960)
- **Chi tiết phải dựng:** Thân hộp inox 400 × 360 bo góc R30 từ Z 1 460 lên 1 920; nắp dày 40 (Z 1 920–1 960) kẹp 4 bulông bướm, 2 tai. 1 kính quan sát Ø120 có vành kẹp trên mặt +Y tại X 2 150, Z 1 750. Đầu ra DN100 có bích Ø220 trên mặt −Y tại X 2 150, Z 1 800.
- **Nguồn:** review-01 I4 (PET không sấy: hút chân không ngay sau vùng chảy, c040, c062); cỡ giả định

#### `barrel_vent_dome` — Vòm thoát khí chân không (B5) (Vacuum vent dome on B5)

- **Chức năng:** Tạo buồng kín trên lỗ thoát khí B5 để hút chân không; kính quan sát cho thấy nhựa không trào lên.
- **Hình dạng / kích thước:** extrude; bao 640 × 430 × 695 (X × Y × Z)
- **Vị trí:** X 3800 … 4440, Y -200 … 230, Z 1455 … 2150
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `barrel_b5` – mặt bích vent insert 8 bulông tại (4120, 0, 1460); `vac_valve` – mặt bích DN150 PN16 trên nắp tại (4120, 0, 2150); `barrel_cover_c3` – xuyên qua lỗ khoét trên vỏ che tại (4120, 0, 1650); `vac_gauge_dome` – ren trên nắp tại (4310, 0, 2150)
- **Chi tiết phải dựng:** Thân hộp inox 600 × 400, bo góc R40, từ Z 1 460 lên 2 100; nắp 640 × 450 dày 50 kẹp bằng 4 bulông bướm, 2 tai (lugs) trên nắp. 2 kính quan sát Ø160 có vành kẹp trên mặt +Y tại X = 3 970 và 4 270, Z = 1 880. Đầu ra chân không DN150 ở giữa nắp (X 4 120, Y 0, Z 2 150), đi thẳng lên van chặn; mặt −Y của vòm phẳng, không có cổng. Tay nắm nâng nắp, đèn soi kính (tuỳ chọn).
- **Nguồn:** pdf_measures §2.2 (vòm dạng hộp cao, 2 kính quan sát, tai trên đỉnh); p01 (kính tròn có tay kẹp); c036 lỗ dài

#### `barrel_cover_c1` — Vỏ che xi lanh C1 (Barrel insulation cover box C1)

- **Chức năng:** Cách nhiệt và che bề mặt nóng của xi lanh, giữ nhiệt ổn định, bảo vệ người vận hành.
- **Hình dạng / kích thước:** extrude; bao 660 × 960 × 1000 (X × Y × Z)
- **Vị trí:** X 5100 … 5760, Y -480 … 480, Z 650 … 1650
- **Vật liệu / màu:** cover `#C4C9CE`
- **Nối với:** `base_frame_process` – chân vỏ bắt vít vào mép khung tại (5430, 0, 650); `melt_head_adapter` – tấm đầu có lỗ Ø660 quanh bích đầu xi lanh tại (5753, 0, 1480)
- **Chi tiết phải dựng:** Hộp inox xước 1,5 mm có cách nhiệt bông khoáng bên trong, vát 45° hai mép trên (xem outline). Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650 bản lề phía −Y, mở lên. Mặt +Y: tay nắm đen trên nắp và trên tấm dưới, tam giác vàng 'bề mặt nóng' ở giữa (như trang 9); 1 tay nắm trên đỉnh. Khe dưới hai bên cho ống nước và cáp nhiệt đi vào. Tấm đầu X = 5 746–5 760 có lỗ tròn Ø660 (bích Ø640); mặt +Y có tấm tròn Ø420 bắt 10 bulông tại X ≈ 5 400, Z = 1 200 (trang 9) che cổng bên B6, cùng một hộp đấu dây nhỏ phía dưới.
- **Nguồn:** pdf_measures §2.2 (6 vỏ hộp có tay nắm + tam giác cảnh báo, cao ≈ 0,98 × khoảng tâm, phủ ≈ 71 % chiều dài xi lanh); p16_1/p16_2; web-07

#### `barrel_cover_c2` — Vỏ che xi lanh C2 (Barrel insulation cover box C2)

- **Chức năng:** Cách nhiệt và che bề mặt nóng của xi lanh, giữ nhiệt ổn định, bảo vệ người vận hành.
- **Hình dạng / kích thước:** extrude; bao 650 × 960 × 1000 (X × Y × Z)
- **Vị trí:** X 4450 … 5100, Y -480 … 480, Z 650 … 1650
- **Vật liệu / màu:** cover `#C4C9CE`
- **Nối với:** `base_frame_process` – chân vỏ bắt vít vào mép khung tại (4775, 0, 650)
- **Chi tiết phải dựng:** Hộp inox xước 1,5 mm có cách nhiệt bông khoáng bên trong, vát 45° hai mép trên (xem outline). Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650 bản lề phía −Y, mở lên. Mặt +Y: tay nắm đen trên nắp và trên tấm dưới, tam giác vàng 'bề mặt nóng' ở giữa (như trang 9); 1 tay nắm trên đỉnh. Khe dưới hai bên cho ống nước và cáp nhiệt đi vào.
- **Nguồn:** pdf_measures §2.2 (6 vỏ hộp có tay nắm + tam giác cảnh báo, cao ≈ 0,98 × khoảng tâm, phủ ≈ 71 % chiều dài xi lanh); p16_1/p16_2; web-07

#### `barrel_cover_c3` — Vỏ che xi lanh C3 (Barrel insulation cover box C3)

- **Chức năng:** Cách nhiệt và che bề mặt nóng của xi lanh, giữ nhiệt ổn định, bảo vệ người vận hành.
- **Hình dạng / kích thước:** extrude; bao 732 × 960 × 1000 (X × Y × Z)
- **Vị trí:** X 3718 … 4450, Y -480 … 480, Z 650 … 1650
- **Vật liệu / màu:** cover `#C4C9CE`
- **Nối với:** `base_frame_process` – chân vỏ bắt vít vào mép khung tại (4084, 0, 650); `barrel_vent_dome` – lỗ khoét 620 × 420 ôm vòm tại (4120, 0, 1650)
- **Chi tiết phải dựng:** Hộp inox xước 1,5 mm có cách nhiệt bông khoáng bên trong, vát 45° hai mép trên (xem outline). Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650 bản lề phía −Y, mở lên. Mặt +Y: tay nắm đen trên nắp và trên tấm dưới, tam giác vàng 'bề mặt nóng' ở giữa (như trang 9); 1 tay nắm trên đỉnh. Khe dưới hai bên cho ống nước và cáp nhiệt đi vào. Lỗ khoét 620 × 420 cho vòm chân không.
- **Nguồn:** pdf_measures §2.2 (6 vỏ hộp có tay nắm + tam giác cảnh báo, cao ≈ 0,98 × khoảng tâm, phủ ≈ 71 % chiều dài xi lanh); p16_1/p16_2; web-07

#### `barrel_cover_c4` — Vỏ che xi lanh C4 (Barrel insulation cover box C4)

- **Chức năng:** Cách nhiệt và che bề mặt nóng của xi lanh, giữ nhiệt ổn định, bảo vệ người vận hành.
- **Hình dạng / kích thước:** extrude; bao 676 × 960 × 1000 (X × Y × Z)
- **Vị trí:** X 3042 … 3718, Y -480 … 480, Z 650 … 1650
- **Vật liệu / màu:** cover `#C4C9CE`
- **Nối với:** `base_frame_process` – chân vỏ bắt vít vào mép khung tại (3380, 0, 650)
- **Chi tiết phải dựng:** Hộp inox xước 1,5 mm có cách nhiệt bông khoáng bên trong, vát 45° hai mép trên (xem outline). Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650 bản lề phía −Y, mở lên. Mặt +Y: tay nắm đen trên nắp và trên tấm dưới, tam giác vàng 'bề mặt nóng' ở giữa (như trang 9); 1 tay nắm trên đỉnh. Khe dưới hai bên cho ống nước và cáp nhiệt đi vào.
- **Nguồn:** pdf_measures §2.2 (6 vỏ hộp có tay nắm + tam giác cảnh báo, cao ≈ 0,98 × khoảng tâm, phủ ≈ 71 % chiều dài xi lanh); p16_1/p16_2; web-07

#### `barrel_cover_c5` — Vỏ che xi lanh C5 (Barrel insulation cover box C5)

- **Chức năng:** Cách nhiệt và che bề mặt nóng của xi lanh, giữ nhiệt ổn định, bảo vệ người vận hành.
- **Hình dạng / kích thước:** extrude; bao 676 × 960 × 1000 (X × Y × Z)
- **Vị trí:** X 2366 … 3042, Y -480 … 480, Z 650 … 1650
- **Vật liệu / màu:** cover `#C4C9CE`
- **Nối với:** `base_frame_process` – chân vỏ bắt vít vào mép khung tại (2704, 0, 650)
- **Chi tiết phải dựng:** Hộp inox xước 1,5 mm có cách nhiệt bông khoáng bên trong, vát 45° hai mép trên (xem outline). Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650 bản lề phía −Y, mở lên. Mặt +Y: tay nắm đen trên nắp và trên tấm dưới, tam giác vàng 'bề mặt nóng' ở giữa (như trang 9); 1 tay nắm trên đỉnh. Khe dưới hai bên cho ống nước và cáp nhiệt đi vào.
- **Nguồn:** pdf_measures §2.2 (6 vỏ hộp có tay nắm + tam giác cảnh báo, cao ≈ 0,98 × khoảng tâm, phủ ≈ 71 % chiều dài xi lanh); p16_1/p16_2; web-07

#### `barrel_cover_c6` — Vỏ che xi lanh C6 (Barrel insulation cover box C6)

- **Chức năng:** Cách nhiệt và che bề mặt nóng của xi lanh, giữ nhiệt ổn định, bảo vệ người vận hành.
- **Hình dạng / kích thước:** extrude; bao 676 × 960 × 1000 (X × Y × Z)
- **Vị trí:** X 1690 … 2366, Y -480 … 480, Z 650 … 1650
- **Vật liệu / màu:** cover `#C4C9CE`
- **Nối với:** `base_frame_process` – chân vỏ bắt vít vào mép khung tại (2028, 0, 650); `barrel_vent_dome_2` – lỗ khoét 420 × 380 ôm vòm vùng 1 tại (2150, 0, 1650)
- **Chi tiết phải dựng:** Hộp inox xước 1,5 mm có cách nhiệt bông khoáng bên trong, vát 45° hai mép trên (xem outline). Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650 bản lề phía −Y, mở lên. Mặt +Y: tay nắm đen trên nắp và trên tấm dưới, tam giác vàng 'bề mặt nóng' ở giữa (như trang 9); 1 tay nắm trên đỉnh. Khe dưới hai bên cho ống nước và cáp nhiệt đi vào. Lỗ khoét 420 × 380 (X 1 940–2 360) cho vòm chân không vùng 1. Tấm đầu phía X = 1 690 có lỗ Ø660 ôm vành bích Ø640 và đai ốc của mối nối 2 (nửa mối nối nằm ngoài vỏ, phía vùng nạp để lộ).
- **Nguồn:** pdf_measures §2.2 (6 vỏ hộp có tay nắm + tam giác cảnh báo, cao ≈ 0,98 × khoảng tâm, phủ ≈ 71 % chiều dài xi lanh); p16_1/p16_2; web-07

#### `barrel_thermocouples` — Cặp nhiệt xi lanh (Barrel thermocouples)

- **Chức năng:** Đo nhiệt độ từng vùng xi lanh cho bộ điều nhiệt.
- **Hình dạng / kích thước:** cyl; bao 4931 × 230 × 227 (X × Y × Z); số lượng 6
- **Vị trí:** X 323 … 5254, Y -215 … 15, Z 1321 … 1548
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `barrel_b1` – ren M14 lắp lưỡi lê, cắm nghiêng góc trên −Y tại (338, -167.1, 1399.2); `barrel_b4` – ren M14 tại (3211, 0, 1460); `barrel_b6` – ren M14 tại (5239, 0, 1460)
- **Chi tiết phải dựng:** 6 cặp nhiệt loại J Ø30 dài 90 (35 mm nằm trong thành xi lanh, 55 mm lộ ra): B1 cắm nghiêng 40° so với phương đứng về phía −Y, chân tại (338, -167, 1399) trên mặt thân, đầu dưới đáy hộp miệng nạp; còn lại cắm đứng trên đỉnh thân tại X = 1 450, 2 450, 3 211, 4 600, 5 239 (xuyên lỗ trên vỏ nhiệt), nắp lưỡi lê, cáp bọc lưới inox. item_mm = [Ø, Ø, dài] theo hệ trục riêng; trục từng cái trong item_axes.
- **Nguồn:** giả định (mỗi vùng 1 cặp nhiệt, như cáp nhiệt thấy ở web-01); vị trí theo review-01 C1

#### `barrel_cw_supply` — Ống góp nước cấp (Cooling-water supply header)

- **Chức năng:** Phân phối nước làm mát tới các vùng xi lanh.
- **Hình dạng / kích thước:** pipe; bao 5700 × 60 × 60 (X × Y × Z); R 30
- **Vị trí:** X -300 … 5400, Y 850 … 910, Z 680 … 740
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `util_cw_supply_riser` – mặt bích DN50 tại (-300, 880, 710); `barrel_cw_valves` – 6 nhánh T tại (338, 880, 710)
- **Chi tiết phải dựng:** Ống inox DN50 (OD 60), mũi tên chiều dòng, gá trên bát đỡ cách mặt khung 30 mm.
- **Nguồn:** web-02, web-06 (ống góp inox dọc khung, 1 cụm van mỗi vùng); phía +Y theo web-06

#### `barrel_cw_return` — Ống góp nước hồi (Cooling-water return header)

- **Chức năng:** Gom nước hồi từ các vùng xi lanh.
- **Hình dạng / kích thước:** pipe; bao 5700 × 60 × 60 (X × Y × Z); R 30
- **Vị trí:** X -300 … 5400, Y 920 … 980, Z 770 … 830
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `util_cw_return_riser` – mặt bích DN50 tại (-300, 950, 800); `barrel_cw_valves` – 6 nhánh T tại (338, 950, 800)
- **Chi tiết phải dựng:** Ống inox DN50 (OD 60) song song phía ngoài ống cấp, Z = 800.
- **Nguồn:** web-02

#### `barrel_cw_valves` — Cụm van điện từ nước làm mát (Cooling-water solenoid valve stations)

- **Chức năng:** Đóng/mở nước làm mát từng vùng theo lệnh bộ điều nhiệt.
- **Hình dạng / kích thước:** composite; bao 5101 × 180 × 350 (X × Y × Z); số lượng 6
- **Vị trí:** X 238 … 5339, Y 820 … 1000, Z 650 … 1000
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `barrel_cw_supply` – nhánh T tại (338, 880, 710); `barrel_cw_return` – nhánh T tại (338, 950, 800); `barrel_cw_hoses` – đầu nối ống mềm trên đỉnh cụm tại (298, 910, 1000); `base_frame_process` – bát gá trên mặt khung tại (1183, 900, 650)
- **Chi tiết phải dựng:** 6 cụm tại X = 338, 1 183, 2 197, 3 211, 4 225, 5 239; mỗi cụm: van bi tay đỏ, lọc Y, van điện từ (cuộn đen), van tiết lưu, chỉ báo dòng chảy. 1 đồng hồ áp trên ống cấp, 1 trên ống hồi.
- **Nguồn:** web-02 (mỗi vùng 1 van điện từ + van bi tay đỏ, đồng hồ áp); c023

#### `barrel_cw_hoses` — Ống mềm nước tới xi lanh (Armoured cooling hoses to barrels)

- **Chức năng:** Dẫn nước từ cụm van lên lỗ khoan làm mát xi lanh và về.
- **Hình dạng / kích thước:** pipe; bao 5370 × 918.3 × 99.3 (X × Y × Z); số lượng 12; R 12
- **Vị trí:** X 188 … 5558, Y -1 … 917.3, Z 928 … 1027.3
- **Vật liệu / màu:** hose `#9A9FA4`
- **Nối với:** `barrel_cw_valves` – đầu nối ren trên đỉnh cụm van tại (298, 910, 1000); `barrel_b1` – khớp nối nhanh ở đáy tại (200, 0, 940); `barrel_b2` – khớp nối nhanh góc dưới +Y tại (876, 184, 1016); `barrel_b3` – khớp nối nhanh góc dưới +Y tại (1890, 184, 1016); `barrel_b4` – khớp nối nhanh góc dưới +Y tại (2904, 184, 1016); `barrel_b5` – khớp nối nhanh góc dưới +Y tại (3918, 184, 1016); `barrel_b6` – khớp nối nhanh góc dưới +Y tại (4932, 184, 1016)
- **Chi tiết phải dựng:** 12 ống mềm inox bọc lưới DN15 (OD 24), mỗi đoạn 1 ống vào + 1 ống ra (đường đi trong paths_mm). Ống vào: từ đỉnh cụm van (X tâm − 40) chéo tới X = đầu đoạn + 200, xuyên tấm dưới của vỏ che ở Y 480, Z ≈ 990, rồi vào đầu nối 45° dưới +Y; ống ra đối xứng ở X = cuối đoạn − 200. B1: hai đầu nối ở đáy tại X 200 và 476; không ống nào đi dưới gối đỡ.
- **Nguồn:** web-02 (ống mềm inox bọc lưới, đầu nối ở mặt bên dưới gần đầu đoạn); p05; vị trí theo review-01 I1

#### `barrel_heater_jboxes` — Hộp đấu dây nhiệt (Heater junction boxes)

- **Chức năng:** Đấu cáp băng nhiệt và cặp nhiệt của từng vùng vào cáp chính.
- **Hình dạng / kích thước:** box; bao 5550 × 180 × 260 (X × Y × Z); số lượng 7
- **Vị trí:** X 250 … 5800, Y -700 … -520, Z 700 … 960
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `barrel_cable_tray` – giá gá trên máng cáp tại (338, -700, 740)
- **Chi tiết phải dựng:** 7 hộp inox 180 × 120 × 200 có nắp kính nhỏ / ổ cắm công nghiệp, tại X = 338, 1 183, 2 197, 3 211, 4 225, 5 239, 5 700 (đầu xi lanh).
- **Nguồn:** web-01/02 (hộp đấu vuông dưới mỗi đoạn xi lanh)

#### `barrel_cable_tray` — Máng cáp nhiệt (Heater cable tray)

- **Chức năng:** Dẫn cáp nhiệt, cặp nhiệt, cảm biến dọc máy về tủ điện.
- **Hình dạng / kích thước:** sheet; bao 6800 × 300 × 100 (X × Y × Z)
- **Vị trí:** X -1000 … 5800, Y -1000 … -700, Z 650 … 750
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `base_frame_drive` – giá đỡ trên mặt khung tại (-500, -850, 650); `base_frame_process` – giá đỡ trên mặt khung tại (3000, -850, 650); `ctrl_cable_drop` – nối máng đứng tại (-990, -1000, 700)
- **Chi tiết phải dựng:** Máng đục lỗ mạ kẽm 300 × 100 có nắp, chạy X −1 000 … 5 800 trên mép −Y của khung.
- **Nguồn:** web-01 (máng thép mạ kẽm đục lỗ dọc dưới xi lanh); phía −Y giả định

### Hệ chân không (vacuum system) — 17 mục

#### `vac_valve` — Van chặn chân không DN150 (vùng 2) (Vacuum shut-off valve DN150 (zone 2))

- **Chức năng:** Cách ly vòm B5 với đường hút khi mở vòm hoặc khởi động.
- **Hình dạng / kích thước:** composite; bao 200 × 410 × 110 (X × Y × Z)
- **Vị trí:** X 4020 … 4220, Y -300 … 110, Z 2150 … 2260
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `barrel_vent_dome` – mặt bích DN150 trên nắp vòm tại (4120, 0, 2150); `vac_bellows` – mặt bích DN150 tại (4120, 0, 2260)
- **Chi tiết phải dựng:** Van bướm DN150 đặt đứng trên nắp vòm (Z 2 150–2 260), bộ tác động khí nén vuông nằm ngang phía −Y (Y −300 … −110). Ống khí Ø12 tới bộ tác động (util_air_tube_vac).
- **Nguồn:** giả định (van bướm có bộ tác động khí nén); đặt đứng trên nắp vòm theo review-01 M4

#### `vac_bellows` — Cút + khớp giãn nở chân không (Vacuum elbow with bellows)

- **Chức năng:** Đổi hướng từ đứng sang ngang và hấp thụ giãn nở nhiệt, rung giữa vòm và ống.
- **Hình dạng / kích thước:** composite; bao 220 × 450 × 220 (X × Y × Z); trục Y; R 110
- **Vị trí:** X 4010 … 4230, Y -340 … 110, Z 2190 … 2410
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_valve` – mặt bích tại (4120, 0, 2260); `vac_pipe` – mặt bích tại (4120, -340, 2300)
- **Chi tiết phải dựng:** Cút 90° DN150 từ đỉnh van (Z 2 260) lên tâm Z 2 300 rồi quay về −Y; ống xếp inox DN150 dài 200 (Y −120 … −320), 2 bích.
- **Nguồn:** p01 (ống mềm inox gợn sóng)

#### `vac_pipe` — Ống hút chân không DN150 (vùng 2) (Vacuum line DN150 (zone 2))

- **Chức năng:** Dẫn hơi và khí từ vòm B5 tới bình tách ngưng.
- **Hình dạng / kích thước:** pipe; bao 168 × 2444 × 484 (X × Y × Z); R 84
- **Vị trí:** X 4036 … 4204, Y -2784 … -340, Z 1900 … 2384
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_bellows` – mặt bích tại (4120, -340, 2300); `vac_separator` – mặt bích nắp tại (4120, -2700, 1900); `vac_pipe_support` – đai ôm tại (4120, -1900, 2216)
- **Chi tiết phải dựng:** Ống inox DN150 (OD 168) đi ngang theo −Y ở tâm Z 2 300 (đáy ống Z 2 216, trên lối đi 2 100), xuống bình tách tại Y −2 700.
- **Nguồn:** giả định (DN150 theo specs §3); cao độ theo review-01 M4

#### `vac_pipe_support` — Cột đỡ ống chân không (Vacuum pipe support post)

- **Chức năng:** Đỡ đoạn ống ngang DN150.
- **Hình dạng / kích thước:** frame; bao 100 × 100 × 2216 (X × Y × Z)
- **Vị trí:** X 4070 … 4170, Y -1950 … -1850, Z 0 … 2216
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `vac_pipe` – đai ôm tại (4120, -1900, 2216); `ctx_floor` – tấm đế tại (4120, -1900, 0)
- **Chi tiết phải dựng:** Ống thép Ø100 có tấm đế và đai ôm trên đỉnh, tại Y −1 900 (ngoài lối đi dọc khung).
- **Nguồn:** giả định

#### `vac_gauge_dome` — Đồng hồ chân không trên vòm B5 (Vacuum gauge on dome (zone 2))

- **Chức năng:** Hiển thị mức chân không tại vòm cho người vận hành.
- **Hình dạng / kích thước:** cyl; bao 60 × 60 × 150 (X × Y × Z)
- **Vị trí:** X 4280 … 4340, Y -30 … 30, Z 2150 … 2300
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `barrel_vent_dome` – ren trên nắp tại (4310, 0, 2150)
- **Chi tiết phải dựng:** Đồng hồ Ø100 mặt hướng +Y + cảm biến áp suất tuyệt đối (truyền tín hiệu).
- **Nguồn:** p01 (đồng hồ trên đường chân không); giả định

#### `vac_valve_2` — Van chặn chân không DN100 (vùng 1) (Vacuum shut-off valve DN100 (zone 1))

- **Chức năng:** Cách ly vòm B3 với đường hút.
- **Hình dạng / kích thước:** composite; bao 130 × 80 × 130 (X × Y × Z)
- **Vị trí:** X 2085 … 2215, Y -320 … -240, Z 1735 … 1865
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `barrel_vent_dome_2` – bích DN100 tại (2150, -240, 1800); `vac_bellows_2` – bích DN100 tại (2150, -320, 1800)
- **Chi tiết phải dựng:** Van bi DN100 tay gạt đỏ.
- **Nguồn:** review-01 I4; giả định

#### `vac_bellows_2` — Khớp giãn nở chân không DN100 (Vacuum bellows DN100 (zone 1))

- **Chức năng:** Hấp thụ giãn nở nhiệt giữa vòm B3 và ống.
- **Hình dạng / kích thước:** cyl; bao 150 × 160 × 150 (X × Y × Z); trục Y; R 75
- **Vị trí:** X 2075 … 2225, Y -480 … -320, Z 1725 … 1875
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_valve_2` – bích tại (2150, -320, 1800); `vac_pipe_3` – bích tại (2150, -480, 1800)
- **Chi tiết phải dựng:** Ống xếp inox DN100 dài 160.
- **Nguồn:** review-01 I4; giả định

#### `vac_pipe_3` — Ống hút chân không DN100 (vùng 1) (Vacuum line DN100 (zone 1))

- **Chức năng:** Dẫn hơi nước từ vòm B3 tới cổng bên của bình tách ngưng.
- **Hình dạng / kích thước:** pipe; bao 1727 × 2277 × 964 (X × Y × Z); R 57
- **Vị trí:** X 2093 … 3820, Y -2757 … -480, Z 1343 … 2307
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_bellows_2` – bích tại (2150, -480, 1800); `vac_separator` – cổng vào bên −X tại (3820, -2700, 1400); `vac_reg_valve_2` – bích tại (3700, -2700, 1650)
- **Chi tiết phải dựng:** Ống inox DN100 (OD 114): lên đứng ngoài vỏ che tại Y −560 tới Z 2 250, đi ngang về −Y tới Y −2 700, theo +X tới X 3 700, xuống tới Z 1 400 rồi vào bình tách.
- **Nguồn:** review-01 I4; giả định

#### `vac_reg_valve_2` — Van tiết lưu chân không vùng 1 (Zone-1 vacuum regulating valve)

- **Chức năng:** Tiết lưu để vùng 1 giữ ≈ 50 mbar trong khi vùng 2 vẫn đạt 5–20 mbar trên cùng cụm bơm.
- **Hình dạng / kích thước:** composite; bao 160 × 160 × 140 (X × Y × Z)
- **Vị trí:** X 3630 … 3790, Y -2780 … -2620, Z 1580 … 1720
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_pipe_3` – bích DN100 tại (3700, -2700, 1650)
- **Chi tiết phải dựng:** Van tiết lưu tay quay DN100 trên đoạn ống đứng, tay quay hướng +Y ở cao 1,65 m; đồng hồ chân không nhỏ bên cạnh.
- **Nguồn:** review-01 I4; giả định

#### `vac_gauge_dome_2` — Đồng hồ chân không trên vòm B3 (Vacuum gauge on dome (zone 1))

- **Chức năng:** Hiển thị mức chân không vùng 1.
- **Hình dạng / kích thước:** cyl; bao 60 × 60 × 150 (X × Y × Z)
- **Vị trí:** X 2250 … 2310, Y -30 … 30, Z 1960 … 2110
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `barrel_vent_dome_2` – ren trên nắp tại (2280, 0, 1960)
- **Chi tiết phải dựng:** Đồng hồ Ø100 mặt hướng +Y + cảm biến áp suất.
- **Nguồn:** review-01 I4; giả định

#### `vac_separator` — Bình tách ngưng (Condensate separator / knock-out vessel)

- **Chức năng:** Ngưng và gom hơi nước, oligome, bụi của cả hai vùng chân không trước bơm.
- **Hình dạng / kích thước:** revolve; bao 600 × 600 × 1900 (X × Y × Z); trục Z; R 300
- **Vị trí:** X 3820 … 4420, Y -3000 … -2400, Z 0 … 1900
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_pipe` – mặt bích nắp (vùng 2) tại (4120, -2700, 1900); `vac_pipe_3` – cổng vào bên −X (vùng 1) tại (3820, -2700, 1400); `vac_pipe_2` – cổng ra bên +X tại (4420, -2700, 1600); `vac_drain` – van trên của nồi xả tại (4120, -2700, 450); `util_cw_vac_hoses` – cổng nước ống xoắn tại (4420, -2600, 1000); `ctx_floor` – 3 chân tại (4120, -2700, 0)
- **Chi tiết phải dựng:** Bình đứng Ø600 cao 1 450 (Z 450–1 900) trên 3 chân cao 450 (nâng 150 để đặt nồi xả), nắp bích bắt bulông, ống xoắn làm mát bên trong (nước 10–15 °C), kính thăm mức, đồng hồ chân không. Cổng: nắp (vùng 2, DN150), bên −X ở Z 1 400 (vùng 1, DN100), ra bên +X ở Z 1 600 (DN150), 2 cổng nước bên +X ở Z 1 000 và 1 100.
- **Nguồn:** c060 (Busch PLASTEX: bình lọc đứng trước bơm), web-15; c063 (buồng ngưng có làm mát)

#### `vac_drain` — Nồi xả ngưng kiểu khoá (lock pot) (Condensate lock pot)

- **Chức năng:** Xả nước ngưng khi máy đang chạy mà không phá chân không.
- **Hình dạng / kích thước:** composite; bao 300 × 300 × 450 (X × Y × Z)
- **Vị trí:** X 3970 … 4270, Y -2850 … -2550, Z 0 … 450
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_separator` – van trên (thường mở) tại (4120, -2700, 450); `ctx_floor` – 3 chân ngắn tại (4120, -2700, 0)
- **Chi tiết phải dựng:** Nồi Ø300 cao 350 (Z 50–400) trên 3 chân ngắn, nằm giữa 3 chân bình tách. Van trên (thường mở) ở Z 400–450, van thông hơi trên nắp nồi, van xả đáy; 3 tay van màu đỏ. Xả: đóng van trên, mở thông hơi, mở van xả; xong đóng lại rồi mở van trên.
- **Nguồn:** review-01 M5; web-15 (van xả đáy tay đỏ)

#### `vac_pipe_2` — Ống chân không tới bơm (Vacuum line to pump)

- **Chức năng:** Dẫn khí sau tách ngưng tới bơm Roots.
- **Hình dạng / kích thước:** pipe; bao 524 × 168 × 184 (X × Y × Z); R 84
- **Vị trí:** X 4420 … 4944, Y -2784 … -2616, Z 1500 … 1684
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_separator` – cổng ra tại (4420, -2700, 1600); `vac_pump_unit` – cổng hút bơm Roots tại (4860, -2700, 1500); `vac_bleed_valve` – măng sông tại (4640, -2700, 1684)
- **Chi tiết phải dựng:** Ống inox DN150 (OD 168), bằng cỡ bích hút của bơm Roots; vận tốc ≈ 30 m/s ở 2 000 m³/h.
- **Nguồn:** giả định; nâng lên DN150 theo drawing review-01 M1

#### `vac_bleed_valve` — Van điều chỉnh / xả chân không (Vacuum bleed valve)

- **Chức năng:** Chỉnh mức chân không chung và phá chân không trước khi mở vòm.
- **Hình dạng / kích thước:** composite; bao 80 × 80 × 145 (X × Y × Z)
- **Vị trí:** X 4600 … 4680, Y -2740 … -2660, Z 1680 … 1825
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `vac_pipe_2` – măng sông ren tại (4640, -2700, 1684)
- **Chi tiết phải dựng:** Van kim + van bi nhỏ tay đỏ trên đỉnh ống ra, cao ≈ 1,7 m để thao tác từ sàn.
- **Nguồn:** giả định

#### `vac_pump_unit` — Cụm bơm chân không (Vacuum pump unit (Roots + dry backing pump))

- **Chức năng:** Tạo chân không 5–20 mbar cho vòm B5 và ≈ 50 mbar (qua van tiết lưu) cho vòm B3.
- **Hình dạng / kích thước:** composite; bao 1800 × 1100 × 1500 (X × Y × Z)
- **Vị trí:** X 4500 … 6300, Y -3300 … -2200, Z 0 … 1500
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `vac_pipe_2` – cổng hút tại (4860, -2700, 1500); `vac_exhaust` – cổng xả tại (6150, -3100, 1500); `vac_control_box` – bắt lên khung skid tại (6100, -2200, 1000); `ctx_floor` – khung skid tại (5400, -2750, 0); `util_cw_vac_hoses` – ống góp nước của skid tại (4500, -2350, 400)
- **Chi tiết phải dựng:** Khung skid thép đen 1 800 × 1 100: bơm Roots ≈ 2 000 m³/h trên bơm trục vít khô ≈ 400 m³/h làm mát bằng nước, động cơ, giảm thanh. Vỏ bơm đen/cam như web-15; ống góp nước vào/ra ở mặt −X, Z 400.
- **Nguồn:** c059/c060 (Busch MINK, PLASTEX), c062 (PET không sấy dùng Roots hai cấp); cỡ giả định (design.md §7)

#### `vac_control_box` — Hộp điều khiển cụm chân không (Vacuum unit control box)

- **Chức năng:** Khởi động bơm, đo áp, khoá liên động.
- **Hình dạng / kích thước:** box; bao 400 × 200 × 800 (X × Y × Z)
- **Vị trí:** X 5900 … 6300, Y -2200 … -2000, Z 700 … 1500
- **Vật liệu / màu:** cabinet `#D8DAD6`
- **Nối với:** `vac_pump_unit` – bắt lên khung skid tại (6100, -2200, 1000)
- **Chi tiết phải dựng:** Hộp 400 × 200 × 800, công tắc chính đỏ-vàng, đèn báo; mặt hướng +Y ra lối đi.
- **Nguồn:** web-15 (hộp điều khiển xám có công tắc chính đỏ-vàng)

#### `vac_exhaust` — Ống xả bơm chân không (Vacuum pump exhaust)

- **Chức năng:** Xả khí sau bơm ra ngoài nhà xưởng.
- **Hình dạng / kích thước:** pipe; bao 120 × 120 × 2000 (X × Y × Z); R 60
- **Vị trí:** X 6090 … 6210, Y -3160 … -3040, Z 1500 … 3500
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `vac_pump_unit` – mặt bích tại (6150, -3100, 1500)
- **Chi tiết phải dựng:** Ống DN100 đứng có bình giảm thanh, đầu trên để hở 'ra ngoài'.
- **Nguồn:** giả định

### Đường chảy nhựa (melt line) — 31 mục

#### `melt_head_adapter` — Đầu xi lanh / bích chuyển (Barrel head adapter (figure-8 to round))

- **Chức năng:** Chuyển dòng từ lỗ số 8 sang lỗ tròn Ø120, nối van khởi động.
- **Hình dạng / kích thước:** revolve; bao 250 × 640 × 640 (X × Y × Z); trục X; R 320
- **Vị trí:** X 5746 … 5996, Y -320 … 320, Z 880 … 1520
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `barrel_b6` – 20 bulông cấy M24 trên PCD 560 tại (5746, 0, 1200); `melt_startup_valve` – 12 vít M24 lục giác chìm từ phía van vào lỗ ren của bích ra tại (5996, 0, 1200); `melt_sensor_head` – 2 lỗ ren 1/2"-20UNF tại (5896, 0, 1420); `melt_rupture_disc` – lỗ ren bên −Y tại (5896, -215, 1200); `barrel_cover_c1` – xuyên qua tấm đầu vỏ che tại (5753, 0, 1480); `melt_heater_conduits` – hộp đấu băng nhiệt tại (5836, -245, 1100)
- **Chi tiết phải dựng:** Bích Ø640 × 60 nhận 20 bulông cấy M24 trên PCD 560 từ B6 (đai ốc phía B6), thân côn Ø520 → Ø400, bích ra Ø420 × 50 có 12 lỗ ren M24 (vít bắt từ phía van, không có đai ốc sau bích nên không chạm thân côn); 2 băng nhiệt.
- **Nguồn:** pdf_measures §4 ghi chú 4 (mặt bích tròn bắt bulông ở đầu ra, dựng adapter đồng trục); specs §4 (≈ 250 mm); bulông theo review-01 M1

#### `melt_rupture_disc` — Đĩa nổ an toàn (Rupture disc)

- **Chức năng:** Xả áp khi áp suất đầu xi lanh vượt giới hạn (bảo vệ quá áp).
- **Hình dạng / kích thước:** cyl; bao 40 × 120 × 40 (X × Y × Z); trục Y; R 20
- **Vị trí:** X 5876 … 5916, Y -330 … -210, Z 1180 … 1220
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_head_adapter` – ren 1/2"-20UNF tại (5896, -215, 1200)
- **Chi tiết phải dựng:** Đầu đĩa nổ Ø40 có nắp chụp hướng xuống, đặt phía −Y.
- **Nguồn:** giả định (thiết bị an toàn tiêu chuẩn của máy đùn)

#### `melt_sensor_head` — Cảm biến áp suất + nhiệt nhựa đầu xi lanh (P1, T1) (Head melt pressure + temperature (P1, T1))

- **Chức năng:** Đo áp và nhiệt nhựa ra khỏi trục vít; P1 dùng cho khoá quá áp.
- **Hình dạng / kích thước:** cyl; bao 80 × 40 × 286 (X × Y × Z); số lượng 2
- **Vị trí:** X 5856 … 5936, Y -20 … 20, Z 1414 … 1700
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_head_adapter` – ren 1/2"-20UNF tại (5896, 0, 1420)
- **Chi tiết phải dựng:** 2 thân cảm biến Ø25 có cổ mềm, đầu điện tử Ø40 cao tới Z 1 700, X = 5 876 và 5 916 (băng nhiệt X 5 906 có khe tại hai lỗ).
- **Nguồn:** p01 (cảm biến áp suất có cáp trên đầu ra); giả định

#### `melt_startup_valve` — Van khởi động / chuyển hướng (Start-up (diverter) valve)

- **Chức năng:** Khi khởi động xả nhựa xuống máng; khi chạy cho nhựa đi tiếp vào bộ lọc.
- **Hình dạng / kích thước:** box; bao 450 × 520 × 520 (X × Y × Z)
- **Vị trí:** X 5996 … 6446, Y -260 … 260, Z 940 … 1460
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_head_adapter` – 12 vít M24 lục giác chìm qua lỗ khoét bậc trên thân van tại (5996, 0, 1200); `melt_sc_adapter_in` – 12 vít M24 lục giác chìm qua lỗ khoét bậc trên thân van tại (6446, 0, 1200); `melt_startup_cyl` – chạc nối cần piston tại (6221, -260, 1200); `melt_drain_chute` – cổng xả đáy tại (6221, 0, 940); `melt_valve_support` – 2 đệm PTFE dưới đáy tại (6040, 205, 940); `melt_heater_conduits` – hộp đấu thanh nhiệt tại (6380, -260, 980)
- **Chi tiết phải dựng:** Khối thép 450 × 520 × 520 có thanh nhiệt cắm, tấm cách nhiệt, cổng xả đáy, chốt xoay (rotary bolt) theo Y. Hai mặt bích là mặt phẳng của khối van có 12 lỗ khoét bậc (counterbore) cho vít M24 bắt vào bích kề; đáy tì lên giá đỡ PTFE.
- **Nguồn:** c035 (diverter valve trong sơ đồ catalogue); kích thước theo specs §4 (giả định)

#### `melt_startup_cyl` — Xi lanh thuỷ lực van khởi động (Diverter valve hydraulic cylinder)

- **Chức năng:** Xoay chốt van giữa vị trí xả và vị trí chạy.
- **Hình dạng / kích thước:** cyl; bao 160 × 600 × 160 (X × Y × Z); trục Y; R 80
- **Vị trí:** X 6141 … 6301, Y -860 … -260, Z 1120 … 1280
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_startup_valve` – chạc nối tại (6221, -260, 1200); `melt_hyd_hoses_suv` – cổng thuỷ lực tại (6221, -860, 1170)
- **Chi tiết phải dựng:** Xi lanh Ø160 dài 600 nằm theo Y, 2 công tắc hành trình.
- **Nguồn:** specs §4 (xi lanh thuỷ lực nằm ngang); giả định phía −Y

#### `melt_drain_chute` — Máng xả nhựa khởi động (Start-up drain chute)

- **Chức năng:** Dẫn nhựa xả khi khởi động xuống xe hứng.
- **Hình dạng / kích thước:** box; bao 250 × 250 × 420 (X × Y × Z)
- **Vị trí:** X 6096 … 6346, Y -125 … 125, Z 520 … 940
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_startup_valve` – bích cổng xả tại (6221, 0, 940); `melt_purge_cart` – miệng xe tại (6221, 0, 520)
- **Chi tiết phải dựng:** Máng inox 250 × 250, có tấm chắn bắn.
- **Nguồn:** giả định

#### `melt_purge_cart` — Xe hứng nhựa xả (Purge cart)

- **Chức năng:** Hứng cục nhựa xả khi khởi động/đổi màu.
- **Hình dạng / kích thước:** box; bao 520 × 800 × 520 (X × Y × Z)
- **Vị trí:** X 5980 … 6500, Y -400 … 400, Z 0 … 520
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_drain_chute` – miệng xe tại (6221, 0, 520); `ctx_floor` – 4 bánh xe tại (6240, 0, 0)
- **Chi tiết phải dựng:** Thùng thép 520 × 800 × 450 trên 4 bánh xe, tay kéo phía −Y.
- **Nguồn:** giả định

#### `melt_sc_adapter_in` — Bích chuyển vào bộ lọc (P2) (Screen changer inlet adapter)

- **Chức năng:** Nối van khởi động với bộ lọc; mang cảm biến áp P2 trước lưới.
- **Hình dạng / kích thước:** revolve; bao 150 × 420 × 420 (X × Y × Z); trục X; R 210
- **Vị trí:** X 6446 … 6596, Y -210 … 210, Z 990 … 1410
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_startup_valve` – 12 vít M24 từ phía van tại (6446, 0, 1200); `melt_screen_changer` – 8 bulông tại (6596, 0, 1200); `melt_sensor_p2` – lỗ ren tại (6521, 0, 1410)
- **Chi tiết phải dựng:** Ống bích Ø420 dài 150, 1 băng nhiệt.
- **Nguồn:** giả định

#### `melt_sensor_p2` — Cảm biến áp suất trước lọc (P2) (Pressure transducer before screen changer (P2))

- **Chức năng:** Đo áp trước lưới để điều khiển xả ngược / đổi lưới.
- **Hình dạng / kích thước:** cyl; bao 60 × 60 × 245 (X × Y × Z)
- **Vị trí:** X 6491 … 6551, Y -30 … 30, Z 1405 … 1650
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_sc_adapter_in` – ren 1/2"-20UNF tại (6521, 0, 1410)
- **Chi tiết phải dựng:** Thân Ø25, đầu Ø40.
- **Nguồn:** giả định

#### `melt_screen_changer` — Bộ lọc lưới quay xả ngược (Backflush screen changer (Gneuss RSFgenius 200))

- **Chức năng:** Lọc tạp chất khỏi nhựa (lưới 60 µm, 970 cm²) liên tục, tự làm sạch bằng xả ngược.
- **Hình dạng / kích thước:** extrude; bao 705 × 1040 × 1429 (X × Y × Z)
- **Vị trí:** X 6596 … 7301, Y -520 … 520, Z 650 … 2079
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_stand_sc` – 4 bulông tại (6950, 0, 650); `melt_sc_adapter_in` – bích vào tại (6596, 0, 1200); `melt_pump_adapter_in` – bích ra tại (7301, 0, 1200); `melt_sc_drive` – trục quay đĩa lưới tại (6950, -520, 1175); `melt_sc_backflush` – bắt mặt +Y tại (6950, 520, 1250); `melt_heater_conduits` – hộp đầu nối nhiệt 6 vùng mặt −Y tại (6700, -520, 980)
- **Chi tiết phải dựng:** Thân hộp inox rộng 1 040 (Y), dày 705 (X), mũ nghiêng có khe thông gió lên tới Z 2 079, logo đỏ Gneuss trên mũ. Bích vào/ra tròn 8 bulông ở giữa mặt trước/sau, tại Z = 1 200. Tấm hông phẳng phải, hộp đầu nối nhiệt 6 vùng.
- **Nguồn:** c050 (RSFgenius 200: A 1 955 / B 705 / C 1 429 / D 550 / E 1 040, 3 800 kg, 39 kW 6 vùng, 200 bar); web-13; c043; cách hiểu B = dày theo dòng chảy, D = cao tâm nhựa trên đáy, E = rộng thân là giả định

#### `melt_sc_drive` — Tay quay thuỷ lực bộ lọc (Screen changer hydraulic drive arm)

- **Chức năng:** Xoay đĩa lưới từng bước bằng xi lanh thuỷ lực.
- **Hình dạng / kích thước:** composite; bao 400 × 565 × 350 (X × Y × Z)
- **Vị trí:** X 6750 … 7150, Y -1085 … -520, Z 1000 … 1350
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_screen_changer` – trục đĩa lưới tại (6950, -520, 1175); `melt_hyd_hoses_sc` – cổng thuỷ lực tại (6860, -1085, 1150)
- **Chi tiết phải dựng:** Tay đòn + xi lanh Ø100 nằm theo Y, nhô 565 mm phía −Y.
- **Nguồn:** web-13 (tay quay + xi lanh nhô một bên); A − E = 1 955 − 1 040 chia hai bên (giả định)

#### `melt_sc_backflush` — Cụm xả ngược + cửa thay lưới (Backflush unit and screen access hatch)

- **Chức năng:** Đẩy nhựa sạch ngược qua lưới để làm sạch, xả ra máng; cửa thay lưới.
- **Hình dạng / kích thước:** composite; bao 500 × 350 × 400 (X × Y × Z)
- **Vị trí:** X 6700 … 7200, Y 520 … 870, Z 1050 … 1450
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_screen_changer` – bắt mặt +Y tại (6950, 520, 1250)
- **Chi tiết phải dựng:** Khối mũi nhọn 500 × 350 có piston xả ngược, cửa bản lề thay lưới, máng xả nhỏ hướng xuống.
- **Nguồn:** web-13 (khối nhọn + cửa thăm lưới bên trái)

#### `melt_hpu` — Bộ nguồn thuỷ lực (Hydraulic power unit)

- **Chức năng:** Cấp dầu thuỷ lực cho xi lanh bộ lọc và van khởi động.
- **Hình dạng / kích thước:** composite; bao 850 × 700 × 1200 (X × Y × Z)
- **Vị trí:** X 6400 … 7250, Y -2700 … -2000, Z 0 … 1200
- **Vật liệu / màu:** cabinet `#D8DAD6`
- **Nối với:** `melt_hyd_hoses_sc` – khối van tại (6860, -2000, 1150); `melt_hyd_hoses_suv` – khối van tại (6460, -2000, 1080); `ctx_floor` – khung đế tại (6800, -2350, 0)
- **Chi tiết phải dựng:** Thùng dầu 250 L, động cơ-bơm 7,5 kW đứng, khối van, bình tích áp, lọc, đồng hồ áp, nhiệt-mức kế. Làm mát dầu bằng quạt gió–dầu gắn trên nắp (không cần nước); mặt khối van hướng +Y ra lối đi.
- **Nguồn:** c043 (bộ lọc dẫn động thuỷ lực); cỡ giả định; lùi về Y −2 700 … −2 000 theo review-01 I2

#### `melt_hyd_hoses_sc` — Ống thuỷ lực bộ lọc (Screen changer hydraulic hoses)

- **Chức năng:** Dẫn dầu áp lực/hồi tới xi lanh bộ lọc.
- **Hình dạng / kích thước:** pipe; bao 106 × 915 × 26 (X × Y × Z); số lượng 2; R 13
- **Vị trí:** X 6847 … 6953, Y -2000 … -1085, Z 1137 … 1163
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `melt_hpu` – đầu nối tại (6860, -2000, 1150); `melt_sc_drive` – đầu nối tại (6860, -1085, 1150)
- **Chi tiết phải dựng:** 2 ống mềm thuỷ lực DN12 (P, T), cách nhau 80 mm, treo trên giá ở Z 1 150 qua lối đi.
- **Nguồn:** giả định

#### `melt_hyd_hoses_suv` — Ống thuỷ lực van khởi động (Diverter valve hydraulic hoses)

- **Chức năng:** Dẫn dầu tới xi lanh van khởi động.
- **Hình dạng / kích thước:** pipe; bao 339.4 × 1151.9 × 175.7 (X × Y × Z); số lượng 2; R 13
- **Vị trí:** X 6213.6 … 6553, Y -2000 … -848.1, Z 1067 … 1242.7
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `melt_hpu` – đầu nối tại (6460, -2000, 1080); `melt_startup_cyl` – đầu nối tại (6221, -860, 1170)
- **Chi tiết phải dựng:** 2 ống mềm DN10.
- **Nguồn:** giả định

#### `melt_pump_adapter_in` — Bích chuyển vào bơm (P3) (Gear pump inlet adapter)

- **Chức năng:** Nối bộ lọc với bơm; mang cảm biến P3 (áp hút bơm, điều khiển tốc độ bơm bánh răng).
- **Hình dạng / kích thước:** revolve; bao 175 × 360 × 360 (X × Y × Z); trục X; R 180
- **Vị trí:** X 7301 … 7476, Y -180 … 180, Z 1020 … 1380
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_screen_changer` – bích ra tại (7301, 0, 1200); `melt_gear_pump` – bích vào tại (7476, 0, 1200); `melt_sensor_p3` – lỗ ren tại (7388, 0, 1380); `melt_heater_conduits` – hộp đấu băng nhiệt tại (7388, -175, 1050)
- **Chi tiết phải dựng:** Ống bích Ø360 dài 175, 1 băng nhiệt.
- **Nguồn:** giả định

#### `melt_sensor_p3` — Cảm biến áp suất hút bơm (P3) (Pump inlet pressure transducer (P3))

- **Chức năng:** Giữ áp hút bơm ổn định (≈ 50 bar) bằng cách chỉnh tốc độ bơm bánh răng; lưu lượng do các cân loss-in-weight quyết định.
- **Hình dạng / kích thước:** cyl; bao 60 × 60 × 245 (X × Y × Z)
- **Vị trí:** X 7358 … 7418, Y -30 … 30, Z 1375 … 1620
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_pump_adapter_in` – ren tại (7388, 0, 1380)
- **Chi tiết phải dựng:** Thân Ø25, đầu Ø40.
- **Nguồn:** giả định

#### `melt_gear_pump` — Bơm bánh răng nhựa (Melt gear pump (Maag extrex6 GU 100/125))

- **Chức năng:** Tạo áp ổn định không dao động (≈ 250 bar) cho khuôn, tách áp trục vít khỏi khuôn.
- **Hình dạng / kích thước:** box; bao 450 × 530 × 460 (X × Y × Z)
- **Vị trí:** X 7476 … 7926, Y -300 … 230, Z 970 … 1430
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_pump_adapter_in` – bích vào tại (7476, 0, 1200); `melt_pump_adapter_out` – bích ra tại (7926, 0, 1200); `melt_stand_pump` – chân bơm trên tấm trượt tại (7700, 0, 970); `melt_pump_cardan` – đầu trục then tại (7701, -300, 1250)
- **Chi tiết phải dựng:** Khối thép 420 × 460 × 460, mặt bên vòng 12 bulông lục giác chìm, đĩa bích tròn lớn Ø360 trên mặt vào/ra (như web-14). Đầu trục dẫn động nhô ra phía −Y tại Z = 1 250; lỗ thanh nhiệt cắm.
- **Nguồn:** c047 (764 cm³/v, 4 474 kg/h ở 134 v/ph → ≈ 105 v/ph ở 3 500 kg/h), c049 (370 bar), web-14; kích thước thân giả định

#### `melt_pump_cardan` — Trục các-đăng + vỏ che (Cardan shaft with guard)

- **Chức năng:** Truyền mômen từ hộp giảm tốc tới trục bơm, bù lệch.
- **Hình dạng / kích thước:** box; bao 300 × 1000 × 300 (X × Y × Z)
- **Vị trí:** X 7551 … 7851, Y -1300 … -300, Z 1100 … 1400
- **Vật liệu / màu:** white `#EDEEEE`
- **Nối với:** `melt_gear_pump` – khớp then tại (7701, -300, 1250); `melt_pump_gearbox` – mặt bích tại (7701, -1300, 1250)
- **Chi tiết phải dựng:** Vỏ che tôn 300 × 300 có ô lưới, trục các-đăng bên trong.
- **Nguồn:** web-07 (hộp che dài có lưới thông gió giữa bơm và hộp số)

#### `melt_pump_gearbox` — Hộp giảm tốc bơm (Gear pump reducer (bevel-helical))

- **Chức năng:** Giảm tốc động cơ 1 480 → ≈ 105 v/ph.
- **Hình dạng / kích thước:** box; bao 500 × 450 × 500 (X × Y × Z)
- **Vị trí:** X 7451 … 7951, Y -1750 … -1300, Z 950 … 1450
- **Vật liệu / màu:** white `#EDEEEE`
- **Nối với:** `melt_pump_cardan` – trục ra tại (7701, -1300, 1250); `pump_drive_pedestal` – 4 bulông tại (7701, -1525, 950); `melt_pump_motor` – mặt bích động cơ tại (7701, -1525, 1450)
- **Chi tiết phải dựng:** Hộp góc côn-trụ 500 × 450 × 500, i ≈ 14.
- **Nguồn:** web-07 (hộp giảm tốc góc + động cơ đứng)

#### `melt_pump_motor` — Động cơ bơm 45 kW (Gear pump motor 45 kW (vertical))

- **Chức năng:** Quay bơm bánh răng qua hộp giảm tốc.
- **Hình dạng / kích thước:** cyl; bao 440 × 440 × 850 (X × Y × Z); trục Z; R 220
- **Vị trí:** X 7481 … 7921, Y -1745 … -1305, Z 1450 … 2300
- **Vật liệu / màu:** white `#EDEEEE`
- **Nối với:** `melt_pump_gearbox` – mặt bích V1 tại (7701, -1525, 1450)
- **Chi tiết phải dựng:** Động cơ đứng Ø440 cao 850, nắp quạt trên đỉnh, hộp đấu dây bên.
- **Nguồn:** web-07 (động cơ đứng trên hộp số); công suất giả định (thuỷ lực ≈ 16 kW, hiệu suất + dự phòng)

#### `melt_pump_adapter_out` — Bích ra bơm (P4) (Gear pump outlet adapter)

- **Chức năng:** Nối bơm với ống nhựa; mang cảm biến P4 (áp ra bơm).
- **Hình dạng / kích thước:** revolve; bao 150 × 300 × 300 (X × Y × Z); trục X; R 150
- **Vị trí:** X 7926 … 8076, Y -150 … 150, Z 1050 … 1350
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_gear_pump` – bích ra tại (7926, 0, 1200); `melt_pipe` – bích tại (8076, 0, 1200); `melt_sensor_p4` – lỗ ren tại (8001, 0, 1350); `melt_rupture_disc_2` – lỗ ren bên −Y tại (8001, -150, 1200); `melt_heater_conduits` – hộp đấu băng nhiệt + thanh nhiệt bơm tại (8001, -155, 1100)
- **Chi tiết phải dựng:** Ống bích Ø300 dài 150, 1 băng nhiệt; lỗ cảm biến P4 trên đỉnh và lỗ đĩa nổ 2 bên −Y.
- **Nguồn:** giả định

#### `melt_sensor_p4` — Cảm biến áp suất ra bơm (P4) (Pump outlet pressure transducer (P4))

- **Chức năng:** Giám sát áp ra bơm, ngắt bơm và trục vít khi vượt 330 bar.
- **Hình dạng / kích thước:** cyl; bao 60 × 60 × 245 (X × Y × Z)
- **Vị trí:** X 7971 … 8031, Y -30 … 30, Z 1345 … 1590
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_pump_adapter_out` – ren tại (8001, 0, 1350)
- **Chi tiết phải dựng:** Thân Ø25, đầu Ø40.
- **Nguồn:** giả định

#### `melt_rupture_disc_2` — Đĩa nổ sau bơm (Rupture disc after gear pump)

- **Chức năng:** Bảo vệ cơ khí ống, bộ trộn và khuôn khi khuôn bị nghẹt (bơm tạo được tới 370 bar).
- **Hình dạng / kích thước:** cyl; bao 40 × 120 × 40 (X × Y × Z); trục Y; R 20
- **Vị trí:** X 7981 … 8021, Y -270 … -150, Z 1180 … 1220
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_pump_adapter_out` – ren 1/2"-20UNF tại (8001, -150, 1200)
- **Chi tiết phải dựng:** Đầu đĩa nổ Ø40 dài 120 theo −Y, áp nổ 350 bar, nắp chụp hướng xuống; tín hiệu đứt đĩa về tủ điều khiển.
- **Nguồn:** review-01 I5; c049 (370 bar)

#### `melt_pipe` — Ống nhựa nóng có gia nhiệt (Heated melt pipe)

- **Chức năng:** Dẫn nhựa từ bơm tới bộ trộn tĩnh, giữ nhiệt ≈ 280 °C.
- **Hình dạng / kích thước:** revolve; bao 350 × 300 × 300 (X × Y × Z); trục X; R 150
- **Vị trí:** X 8076 … 8426, Y -150 … 150, Z 1050 … 1350
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_pump_adapter_out` – bích tại (8076, 0, 1200); `melt_static_mixer` – bích tại (8426, 0, 1200); `melt_pipe_saddles` – gối tại (8250, 0, 1050); `melt_heater_conduits` – hộp đấu trên vỏ bọc −Y tại (8250, -150, 1100)
- **Chi tiết phải dựng:** Ống DN100 (lỗ Ø100); 3 băng nhiệt nằm dưới lớp cách nhiệt và vỏ inox Ø300 (không thấy từ ngoài); 1 hộp đấu nhỏ 120 × 80 trên vỏ bọc phía −Y tại X 8 250.
- **Nguồn:** specs §4 (ống gia nhiệt, cách nhiệt, vỏ inox); giả định

#### `melt_static_mixer` — Bộ trộn tĩnh (Static mixer)

- **Chức năng:** Đồng nhất nhiệt độ nhựa trước khuôn.
- **Hình dạng / kích thước:** revolve; bao 500 × 300 × 300 (X × Y × Z); trục X; R 150
- **Vị trí:** X 8426 … 8926, Y -150 … 150, Z 1050 … 1350
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_pipe` – bích tại (8426, 0, 1200); `melt_die_adapter` – bích tại (8926, 0, 1200); `melt_pipe_saddles` – gối tại (8560, 0, 1050); `melt_heater_conduits` – hộp đấu trên vỏ bọc −Y tại (8676, -150, 1100)
- **Chi tiết phải dựng:** Vỏ DN100 với 6 phần tử trộn; 4 băng nhiệt dưới vỏ inox Ø300 (không thấy từ ngoài), 1 hộp đấu trên vỏ bọc phía −Y tại X 8 676; bích hai đầu.
- **Nguồn:** specs §4 (tuỳ chọn DN ≈ 120, dài ≈ 600); giả định

#### `melt_die_adapter` — Bích chuyển vào khuôn (Die inlet adapter)

- **Chức năng:** Chuyển lỗ tròn Ø100 sang cửa vào khuôn ở giữa mặt sau khuôn.
- **Hình dạng / kích thước:** composite; bao 200 × 500 × 360 (X × Y × Z)
- **Vị trí:** X 8926 … 9126, Y -250 … 250, Z 1020 … 1380
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `melt_static_mixer` – bích tại (8926, 0, 1200); `die_body_upper` – bích chữ nhật 8 bulông tại (9126, 0, 1300); `die_body_lower` – bích chữ nhật 8 bulông tại (9126, 0, 1100); `melt_sensor_die` – lỗ ren tại (9026, 0, 1380)
- **Chi tiết phải dựng:** Cổ tròn Ø300 nở thành bích chữ nhật 500 × 360 ở mặt khuôn, 1 băng nhiệt.
- **Nguồn:** giả định

#### `melt_sensor_die` — Cảm biến áp + nhiệt vào khuôn (P5, T5) (Die inlet pressure + temperature (P5, T5))

- **Chức năng:** Đo áp và nhiệt nhựa vào khuôn.
- **Hình dạng / kích thước:** cyl; bao 80 × 40 × 246 (X × Y × Z); số lượng 2
- **Vị trí:** X 8986 … 9066, Y -20 … 20, Z 1374 … 1620
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `melt_die_adapter` – ren tại (9026, 0, 1380)
- **Chi tiết phải dựng:** 2 cảm biến tại X = 9 006 và 9 046.
- **Nguồn:** giả định

#### `melt_heater_bands` — Băng nhiệt đường chảy (lộ ra ngoài) (Melt line heater bands (visible))

- **Chức năng:** Giữ nhiệt các bích chuyển và đầu xi lanh.
- **Hình dạng / kích thước:** revolve; bao 3234 × 514 × 514 (X × Y × Z); số lượng 6
- **Vị trí:** X 5801 … 9035, Y -257 … 257, Z 943 … 1457
- **Vật liệu / màu:** polished `#D5D9DD`
- **Nối với:** `melt_head_adapter` – kẹp tại (5836, 0, 1440); `melt_sc_adapter_in` – kẹp tại (6521, 0, 1390); `melt_pump_adapter_out` – kẹp tại (8001, 0, 1330); `melt_die_adapter` – kẹp tại (9000, 0, 1360)
- **Chi tiết phải dựng:** 6 băng mica/gốm rộng 70 có hộp đấu nhỏ và cáp bọc lưới: đầu xi lanh X 5 836 (Ø514) và 5 906 (Ø454, khe dưới 2 cảm biến), bích vào lọc X 6 521 (Ø380, khe dưới P2), bích vào bơm X 7 388 (Ø320, khe dưới P3), bích ra bơm X 8 001 (Ø260, khe dưới P4), cổ bích khuôn X 9 000 (Ø320). 7 băng trên ống và bộ trộn nằm dưới vỏ inox Ø300, không dựng thành vòng (xem melt_pipe, melt_static_mixer).
- **Nguồn:** giả định; vị trí theo review-01 C1

#### `melt_heater_jbox` — Hộp đấu nhiệt đường chảy (Melt-line heater junction box)

- **Chức năng:** Đấu nguồn nhiệt và cặp nhiệt cho bộ lọc (6 vùng, 39 kW), van khởi động, bơm, các bích và ống (≈ 75 kW tổng).
- **Hình dạng / kích thước:** box; bao 600 × 250 × 800 (X × Y × Z)
- **Vị trí:** X 6650 … 7250, Y -850 … -600, Z 150 … 950
- **Vật liệu / màu:** cabinet `#D8DAD6`
- **Nối với:** `melt_stand_sc` – bắt mặt −Y giá bộ lọc tại (6950, -600, 550); `melt_heater_conduits` – ốc siết ống luồn tại (6700, -650, 950)
- **Chi tiết phải dựng:** Hộp RAL 7035 600 × 250 × 800 dưới tay quay bộ lọc; cửa bản lề, ổ cắm công nghiệp nhiều chân, tem cảnh báo điện; cáp nguồn vào từ hào cáp qua đáy.
- **Nguồn:** review-01 I6; giả định

#### `melt_heater_conduits` — Ống luồn cáp nhiệt đường chảy (Melt-line heater conduits)

- **Chức năng:** Dẫn cáp nhiệt từ hộp đấu tới từng vùng nhiệt của đường chảy.
- **Hình dạng / kích thước:** pipe; bao 2870 × 705 × 380 (X × Y × Z); số lượng 7; R 15
- **Vị trí:** X 5821 … 8691, Y -855 … -150, Z 735 … 1115
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `melt_heater_jbox` – ốc siết tại (6700, -650, 950); `melt_screen_changer` – hộp nhiệt 6 vùng tại (6700, -520, 980); `melt_startup_valve` – hộp đấu tại (6380, -260, 980); `melt_head_adapter` – băng nhiệt tại (5836, -245, 1100); `melt_pump_adapter_in` – băng nhiệt tại (7388, -175, 1050); `melt_pump_adapter_out` – băng nhiệt + bơm tại (8001, -155, 1100); `melt_pipe` – hộp đấu vỏ bọc tại (8250, -150, 1100); `melt_static_mixer` – hộp đấu vỏ bọc tại (8676, -150, 1100)
- **Chi tiết phải dựng:** 7 ống luồn kim loại mềm Ø30 (đường đi trong paths_mm): bộ lọc, van khởi động, đầu xi lanh, bích vào bơm, bích ra bơm (kèm thanh nhiệt thân bơm), ống nhựa, bộ trộn; đi thấp ở Z 750–900 phía −Y rồi lên hộp đấu từng vùng.
- **Nguồn:** review-01 I6; giả định

### Khuôn chữ T (T-die) — 18 mục

#### `die_body_upper` — Nửa khuôn trên (có môi mềm) (Upper die body (with flex lip))

- **Chức năng:** Nửa trên ống phân phối móc áo (coat-hanger manifold), mang môi mềm, thanh chắn và bulông chỉnh.
- **Hình dạng / kích thước:** extrude; bao 450 × 2600 × 250 (X × Y × Z)
- **Vị trí:** X 9126 … 9576, Y -1300 … 1300, Z 1200 … 1450
- **Vật liệu / màu:** chrome `#E3E6E9`
- **Nối với:** `die_body_lower` – mặt phân khuôn, bulông M24 bước 100 tại (9350, 0, 1200); `melt_die_adapter` – bích cửa vào tại (9126, 0, 1300); `die_end_plate_op` – bulông tại (9350, 1300, 1325); `die_end_plate_rear` – bulông tại (9350, -1300, 1325); `die_thermal_bolts` – lỗ ren trong thân tại (9400, 0, 1370); `die_choker_bolts` – lỗ ren mặt đỉnh tại (9255, 0, 1450); `die_bolt_actuator_rail` – bắt vít lên mặt đỉnh tại (9315, 0, 1450); `die_flex_lip` – liền khối, rãnh bản lề tại (9450, 0, 1250); `die_heater_boxes` – bắt mặt sau tại (9126, 600, 1385)
- **Chi tiết phải dựng:** Rộng 2 600 (Y ±1 300), cao 250 (Z 1 200–1 450), sâu 450 (X 9 126–9 576), mũi vát 30° về phía khe trục. Mạ crôm bóng; 9 vùng thanh nhiệt cắm từ mặt sau. Rãnh bản lề môi mềm (flex-lip hinge slot) hở, chạy suốt bề rộng 2 400 tại X 9 392–9 404 (rộng 12), cắt từ mặt vát xuống tới Z 1 212, để lại gân bản lề dày 12 mm trên mặt chảy (Z 1 200); phần sau rãnh là môi mềm. Đầu bulông nhiệt tì lên môi tại X 9 440, cách gân 36 mm. Mặt đỉnh từ sau ra trước: hộp nhiệt mặt sau (X ≤ 9 126), tai cẩu ở tấm đầu, hàng bulông thanh chắn X 9 255 (thanh chắn trong thân X 9 240–9 270), máng bulông nhiệt X 9 285–9 345, rồi mặt vát mang 94 bulông nhiệt.
- **Nguồn:** c053/c055/c056/c057 (khuôn móc áo, môi mềm, thanh chắn); DECISIONS 10 (môi rộng 2 400); chiều cao/chiều sâu giả định theo web-19/20

#### `die_body_lower` — Nửa khuôn dưới (Lower die body)

- **Chức năng:** Nửa dưới ống phân phối, môi dưới thay được.
- **Hình dạng / kích thước:** extrude; bao 450 × 2600 × 250 (X × Y × Z)
- **Vị trí:** X 9126 … 9576, Y -1300 … 1300, Z 950 … 1200
- **Vật liệu / màu:** chrome `#E3E6E9`
- **Nối với:** `die_body_upper` – mặt phân khuôn tại (9350, 0, 1200); `die_cart` – 2 đệm đỡ tại (9240, 700, 950); `melt_die_adapter` – bích tại (9126, 0, 1100); `die_end_plate_op` – bulông tại (9350, 1300, 1075); `die_end_plate_rear` – bulông tại (9350, -1300, 1075); `die_heater_boxes` – bắt mặt sau tại (9126, 600, 1015)
- **Chi tiết phải dựng:** Cao 250 (Z 950–1 200); 9 vùng thanh nhiệt. Môi dưới (lower lip) là thanh chèn thay được dọc mũi, X 9 446–9 576 × cao 60, bắt 24 vít M12 lục giác chìm từ mặt vát dưới (bước 100).
- **Nguồn:** như trên

#### `die_flex_lip` — Môi mềm khuôn (Flex lip)

- **Chức năng:** Chỉnh khe môi cục bộ (hành trình ≈ 1–2,5 mm) để đều chiều dày tấm.
- **Hình dạng / kích thước:** extrude; bao 172 × 2400 × 148 (X × Y × Z)
- **Vị trí:** X 9404 … 9576, Y -1200 … 1200, Z 1200 … 1348
- **Vật liệu / màu:** chrome `#E3E6E9`
- **Nối với:** `die_body_upper` – liền khối qua rãnh bản lề tại (9450, 0, 1250); `die_thermal_bolts` – đầu bulông đẩy tại (9440, 0, 1290); `ctx_sheet` – khe môi → màn nhựa tại (9576, 0, 1200)
- **Chi tiết phải dựng:** Dải môi rộng 2 400, khe làm việc 0,5–2 mm tại Z = 1 200, X = 9 576; là phần mũi của nửa trên phía sau rãnh bản lề hở (X 9 392–9 404, suốt bề rộng, gân 12 mm). Bulông nhiệt bắc qua rãnh (ren trong thân phía trước rãnh), đầu bulông tì lên môi tại X 9 440 (cách gân 36 mm), nên môi uốn quanh gân.
- **Nguồn:** c053, c055 (0,040"), c056 (2,5 mm); rãnh bản lề hở theo drawing review-01 I5

#### `die_end_plate_op` — Tấm đầu khuôn (+Y) (Die end plate (operator side))

- **Chức năng:** Bịt hai đầu ống phân phối, mang thanh deckle và hộp đấu nhiệt tấm đầu.
- **Hình dạng / kích thước:** box; bao 434 × 75 × 500 (X × Y × Z)
- **Vị trí:** X 9126 … 9560, Y 1300 … 1375, Z 950 … 1450
- **Vật liệu / màu:** chrome `#E3E6E9`
- **Nối với:** `die_body_upper` – bulông tại (9350, 1300, 1325); `die_body_lower` – bulông tại (9350, 1300, 1075); `die_deckles` – lỗ dẫn hướng tại (9480, 1375, 1200); `die_lifting_lugs` – lỗ ren tai cẩu tại (9190, 1337, 1450)
- **Chi tiết phải dựng:** Tấm thép 75 mm, khối đầu nối thanh nhiệt (terminal block) 6 lỗ, 1 vùng nhiệt.
- **Nguồn:** web-19/20 (tấm đầu có khối đầu nối nhiệt)

#### `die_end_plate_rear` — Tấm đầu khuôn (−Y) (Die end plate (rear side))

- **Chức năng:** Bịt hai đầu ống phân phối, mang thanh deckle và hộp đấu nhiệt tấm đầu.
- **Hình dạng / kích thước:** box; bao 434 × 75 × 500 (X × Y × Z)
- **Vị trí:** X 9126 … 9560, Y -1375 … -1300, Z 950 … 1450
- **Vật liệu / màu:** chrome `#E3E6E9`
- **Nối với:** `die_body_upper` – bulông tại (9350, -1300, 1325); `die_body_lower` – bulông tại (9350, -1300, 1075); `die_deckles` – lỗ dẫn hướng tại (9480, -1375, 1200); `die_lifting_lugs` – lỗ ren tai cẩu tại (9190, -1337, 1450)
- **Chi tiết phải dựng:** Tấm thép 75 mm, khối đầu nối thanh nhiệt (terminal block) 6 lỗ, 1 vùng nhiệt.
- **Nguồn:** web-19/20 (tấm đầu có khối đầu nối nhiệt)

#### `die_deckles` — Thanh deckle chỉnh bề rộng (Deckle rods (internal/external))

- **Chức năng:** Thu hẹp bề rộng màn nhựa ở hai đầu khi đổi khổ tấm.
- **Hình dạng / kích thước:** cyl; bao 140 × 3050 × 40 (X × Y × Z); số lượng 2
- **Vị trí:** X 9380 … 9520, Y -1525 … 1525, Z 1180 … 1220
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `die_end_plate_op` – lỗ dẫn tại (9480, 1375, 1200); `die_end_plate_rear` – lỗ dẫn tại (9480, -1375, 1200)
- **Chi tiết phải dựng:** Mỗi đầu 1 thanh Ø30 nhô 150 ngoài tấm đầu (tới |Y| 1 525) tại X 9 480, có núm vặn + thước; lưỡi deckle trong nằm trong khuôn, không vượt X 9 520 (tránh khung cụm trục).
- **Nguồn:** c057 (deckle trong/ngoài); rút ngắn theo review-01 M6

#### `die_thermal_bolts` — Bulông nhiệt chỉnh môi (Thermal lip-adjust bolts)

- **Chức năng:** Đẩy môi mềm theo điều khiển tự động (giãn nở nhiệt), chỉnh profin chiều dày ngang tấm.
- **Hình dạng / kích thước:** cyl; bao 122 × 2394 × 162 (X × Y × Z); số lượng 94, bước 25.4
- **Vị trí:** X 9330 … 9452, Y -1197 … 1197, Z 1284 … 1446
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `die_body_upper` – lỗ ren tại (9400, 0, 1370); `die_flex_lip` – đầu đẩy tại (9440, 0, 1290); `die_bolt_actuator_rail` – khối gia nhiệt + ống gió tại (9340, 0, 1448)
- **Chi tiết phải dựng:** 94 bulông, y = −1 181 + 25,4·k (k = 0…93); mỗi bulông Ø30 (thân Ø16 trong ống gia nhiệt 80 W) dài 170, trục từ (9 440, y, 1 295) tới (9 342, y, 1 434), tức 35° so với phương đứng, nằm dọc mặt vát của nửa trên. Đầu bulông nằm trong rãnh phay, nhô tối đa 30 mm khỏi mặt vát, còn ≈ 20 mm khe hở tới trục giữa (đã kiểm tra bằng hình học). positions_mm là tâm bulông; item_mm = [Ø, Ø, dài] theo hệ trục riêng của bulông, trục dài là item_axis.
- **Nguồn:** c053/c054 (bước 25,4 mm, 80 W, hành trình 300 µm); web-17/18; trục bulông theo review-01 C1

#### `die_bolt_actuator_rail` — Thanh cơ cấu bulông nhiệt + máng cáp + ống gió (Thermal-bolt actuator rail with cable duct and air duct)

- **Chức năng:** Gom cáp 94 thanh nhiệt bulông và dẫn gió làm mát bulông.
- **Hình dạng / kích thước:** box; bao 60 × 2500 × 90 (X × Y × Z)
- **Vị trí:** X 9285 … 9345, Y -1250 … 1250, Z 1450 … 1540
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `die_body_upper` – bắt vít tại (9315, 0, 1450); `die_thermal_bolts` – khối gia nhiệt tại (9340, 0, 1448); `die_cable_harness` – ổ cắm đầu −Y tại (9290, -1250, 1495); `util_air_hose_die` – đầu nối khí tại (9290, -1240, 1540)
- **Chi tiết phải dựng:** Máng inox 60 × 90 dài 2 500 trên dải trước của mặt đỉnh (X 9 285–9 345), ngay sau đầu trên các bulông nhiệt; trong máng: cáp 94 thanh nhiệt (tầng trên) và ống gió làm mát (tầng dưới). 2 ổ cắm nhiều chân đánh số ở đầu −Y; nắp máng tháo được để chừa lối vặn bulông thanh chắn ngay phía sau.
- **Nguồn:** web-17/18 (hàng dây và ống gió dọc môi); c054; thu hẹp theo ghi chú drafter (design_issues #1)

#### `die_choker_bolts` — Bulông chỉnh thanh chắn (Choker (restrictor) bar adjusting bolts)

- **Chức năng:** Chỉnh thô dòng chảy ngang khuôn qua thanh chắn (restrictor bar) nằm sau ống phân phối, trước vùng preland.
- **Hình dạng / kích thước:** cyl; bao 30 × 2430 × 80 (X × Y × Z); số lượng 33, bước 75
- **Vị trí:** X 9240 … 9270, Y -1215 … 1215, Z 1450 … 1530
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `die_body_upper` – lỗ ren mặt đỉnh, đẩy thẳng đứng xuống thanh chắn tại (9255, 0, 1450)
- **Chi tiết phải dựng:** 33 bulông đầu đen Ø30 cao 80 đặt đứng trên mặt đỉnh tại X 9 255, ngay trên thanh chắn (X 9 240–9 270), Y = −1 200 + 75·k (k = 0…32), đai ốc khoá; bulông đẩy/kéo thẳng thanh chắn như khuôn môi mềm thông thường. Vặn bằng khẩu từ trên xuống; khe 15 mm tới máng bulông nhiệt phía trước (X 9 285).
- **Nguồn:** c053 (thanh chắn chỉnh thô), web-19; vị trí theo ghi chú drafter (design_issues #1)

#### `die_body_bolts` — Bulông thân khuôn M30 (Die body bolts (M30 socket-head cap screws))

- **Chức năng:** Kẹp hai nửa khuôn vào nhau, chịu lực tách ≈ 7 MN do áp nhựa trong ống phân phối và preland.
- **Hình dạng / kích thước:** cyl; bao 155 × 2575 × 500 (X × Y × Z); số lượng 94
- **Vị trí:** X 9137.5 … 9292.5, Y -1287.5 … 1287.5, Z 950 … 1450
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `die_body_upper` – lỗ khoét bậc trên mặt đỉnh / lỗ ren nhận bulông từ dưới tại (9160, 0, 1440); `die_body_lower` – lỗ khoét bậc ở mặt đáy / lỗ ren nhận bulông từ trên tại (9160, 0, 960)
- **Chi tiết phải dựng:** 94 vít lục giác chìm M30 cấp 10.9 dài 260, đầu Ø45 nằm chìm trong lỗ khoét bậc Ø48 × 32 (mặt khuôn phẳng); positions_mm là tâm đầu vít (đầu cao 30). Mặt đỉnh nửa trên: hàng X 9 160 (24 vít, Y = −1 265 … +1 265 bước 110) và hàng X 9 210 (23 vít, Y = −1 210 … +1 210), cả hai nằm sau hàng bulông thanh chắn (X 9 240–9 270) và máng bulông nhiệt (X 9 285–9 345). Mặt đáy nửa dưới: hàng X 9 160 (23 vít, Y = −1 210 …) và hàng X 9 270 (24 vít, Y = −1 265 …), tức cách mép trước mặt đáy (X 9 330) 170 và 60 mm. Vít từ trên ren vào nửa dưới, vít từ dưới ren vào nửa trên; các hàng lệch nhau 55 mm theo Y nên thân vít đi song song không chạm nhau. Lực kẹp ≈ 94 × 330 kN ≈ 31 MN, gấp ≈ 4 lần lực tách; ống phân phối (G) phải đi giữa và trước các hàng vít (xem design.md §9).
- **Nguồn:** drawing review-01 I4; cỡ và vị trí giả định (tính lực kẹp)

#### `die_heater_boxes` — Hộp đầu nối nhiệt khuôn (Die heater terminal boxes)

- **Chức năng:** Đấu dây 20 vùng nhiệt khuôn (≈ 50 kW).
- **Hình dạng / kích thước:** box; bao 76 × 2500 × 480 (X × Y × Z)
- **Vị trí:** X 9050 … 9126, Y -1250 … 1250, Z 960 … 1440
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `die_body_upper` – bắt mặt sau tại (9126, 600, 1385); `die_body_lower` – bắt mặt sau tại (9126, 600, 1015); `die_heater_conduit` – ống luồn cáp tại (9090, -1250, 1000)
- **Chi tiết phải dựng:** 2 hộp dài (trên Z 1 330–1 440, dưới Z 960–1 070) chạy Y ±1 250, chừa giữa ±260 cho bích vào; tem cảnh báo vàng.
- **Nguồn:** web-17 (hộp nhiệt inox có tem vàng), c055 (≈ 21 kW/m)

#### `die_lifting_lugs` — Tai cẩu khuôn (Die lifting eyes)

- **Chức năng:** Cẩu khuôn khi lắp/tháo.
- **Hình dạng / kích thước:** cyl; bao 360 × 2720 × 130 (X × Y × Z); số lượng 4
- **Vị trí:** X 9150 … 9510, Y -1360 … 1360, Z 1450 … 1580
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `die_end_plate_op` – ren M36 tại (9190, 1337, 1450); `die_end_plate_rear` – ren M36 tại (9190, -1337, 1450)
- **Chi tiết phải dựng:** 4 tai cẩu M36 cao 130, 2 trên mỗi tấm đầu tại X 9 190 và 9 470, |Y| = 1 337 (ngoài mặt trục ±1 300, trước cổ trục X ≥ 9 626).
- **Nguồn:** web-07 (2 tai cẩu trên khuôn); vị trí theo review-01 C1

#### `die_cable_harness` — Bó cáp khuôn (cắm rút) (Die cable harness (plug-in))

- **Chức năng:** Dẫn cáp bulông nhiệt và cảm biến khuôn xuống hộp đấu dây khuôn; rút phích ra khi kéo khuôn đi.
- **Hình dạng / kích thước:** pipe; bao 242.9 × 422 × 553.2 (X × Y × Z); R 30
- **Vị trí:** X 9077.1 … 9320, Y -1672 … -1250, Z 971.8 … 1525
- **Vật liệu / màu:** rubber `#2A2A2A`
- **Nối với:** `die_bolt_actuator_rail` – ổ cắm tại (9290, -1250, 1495); `die_junction_box` – phích cắm nhiều chân trên nóc hộp tại (9100, -1650, 1000)
- **Chi tiết phải dựng:** Ống luồn cáp mềm Ø60 đi xuống phía −Y rồi chéo về nóc hộp đấu dây khuôn; 2 phích nhiều chân đánh số ở đầu hộp.
- **Nguồn:** web-17 (cáp xám có đầu cắm đánh số); review-01 I6

#### `die_heater_conduit` — Ống luồn cáp nhiệt khuôn (cắm rút) (Die heater cable conduit (plug-in))

- **Chức năng:** Dẫn cáp 20 vùng nhiệt khuôn từ hộp đầu nối tới hộp đấu dây khuôn; có phích cắm để tách khuôn.
- **Hình dạng / kích thước:** pipe; bao 127.4 × 411.3 × 89.2 (X × Y × Z); R 20
- **Vị trí:** X 8982.6 … 9110, Y -1661.3 … -1250, Z 930.8 … 1020
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `die_heater_boxes` – ốc siết cáp tại (9090, -1250, 1000); `die_junction_box` – phích cắm tại (9000, -1650, 950)
- **Chi tiết phải dựng:** Ống mềm kim loại Ø40.
- **Nguồn:** giả định

#### `die_cart` — Xe đỡ khuôn chỉnh cao (Die support cart with height adjustment)

- **Chức năng:** Đỡ khuôn ≈ 3,4 t, chỉnh cao ±50 mm bằng kích vít, tự do ±40 mm theo X (giãn nở), kéo khuôn ra theo +Y trên ray.
- **Hình dạng / kích thước:** frame; bao 680 × 2400 × 890 (X × Y × Z)
- **Vị trí:** X 8700 … 9380, Y -1200 … 1200, Z 60 … 950
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `die_body_lower` – 2 đệm trên bàn trượt tại (9240, 700, 950); `die_cart_rails` – 4 bánh xe tại (8760, 0, 60)
- **Chi tiết phải dựng:** Đế thép hộp rộng X 8 700–9 380, Z 60–300, luồn dưới bộ trộn và bích khuôn; 4 bánh: 2 bánh trụ trên ray phẳng X 8 760, 2 bánh rãnh V trên ray dẫn hướng X 9 320 (khổ 560). Hai cột kích vít có tay quay ở X 9 150–9 350, xà đỡ trên có bàn trượt ±40 mm theo X và 2 đệm tại Y = ±700. Phía trước đế không vượt X 9 380 dưới Z 600 (trục dưới ở X ≥ 9 429 tại Z 600); khoá bánh khi chạy. Phải lùi cụm trục cán trước khi kéo khuôn ra theo +Y.
- **Nguồn:** web-08 (xe khuôn đế rộng có bánh và cột chỉnh), c057 (die carts); review-01 I3, I8

#### `die_cart_rails` — Ray xe khuôn (Die cart rails)

- **Chức năng:** Dẫn xe khuôn ra phía +Y khi bảo trì.
- **Hình dạng / kích thước:** frame; bao 600 × 4300 × 60 (X × Y × Z); số lượng 2
- **Vị trí:** X 8740 … 9340, Y -1500 … 2800, Z 0 … 60
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `die_cart` – bánh xe tại (8760, 0, 60); `ctx_floor` – bulông neo tại (8760, 0, 0)
- **Chi tiết phải dựng:** 2 ray dài 4 300 theo Y: ray phẳng tại X 8 760, ray có gờ dẫn hướng tại X 9 320 (khổ 560); khoá sàn ở vị trí làm việc.
- **Nguồn:** giả định; khổ ray theo review-01 I3

#### `die_junction_box` — Hộp đấu dây khuôn (Die junction box)

- **Chức năng:** Tập trung cáp nhiệt khuôn (20 vùng), 94 mạch bulông nhiệt, cảm biến; phích cắm để tách khuôn; nút dừng khẩn.
- **Hình dạng / kích thước:** box; bao 600 × 300 × 1000 (X × Y × Z)
- **Vị trí:** X 8700 … 9300, Y -1900 … -1600, Z 0 … 1000
- **Vật liệu / màu:** cabinet `#D8DAD6`
- **Nối với:** `die_cable_harness` – phích cắm tại (9100, -1650, 1000); `die_heater_conduit` – phích cắm tại (9000, -1650, 950); `ctrl_trench_die_branch` – cáp vào đáy tại (8700, -1625, 5); `util_frl` – giá gá mặt +X tại (9300, -1705, 775); `ctx_floor` – đế tại (9000, -1750, 0)
- **Chi tiết phải dựng:** Tủ đứng RAL 7035 600 × 300 × 1 000 trên sàn, cửa hướng +Y, đặt ngoài ray xe khuôn để không đi theo xe. Nóc: 2 ổ cắm nhiều chân cho bó cáp bulông nhiệt, 1 ổ cho cáp nhiệt khuôn; nút dừng khẩn đỏ trên cửa.
- **Nguồn:** review-01 I6; giả định

#### `die_drip_pan` — Khay hứng dưới môi khuôn (Drip pan under die lip)

- **Chức năng:** Hứng nhựa rơi khi khởi động màn nhựa.
- **Hình dạng / kích thước:** sheet; bao 324 × 2700 × 80 (X × Y × Z)
- **Vị trí:** X 9576 … 9900, Y -1350 … 1350, Z 0 … 80
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `ctx_floor` – đặt trên sàn tại (9700, 0, 0)
- **Chi tiết phải dựng:** Khay inox 324 × 2 700 cao 80.
- **Nguồn:** giả định

### Điều khiển và điện (control and electrical) — 18 mục

#### `ctrl_drive_cabinet` — Tủ biến tần trung thế (MV drive converter cabinet)

- **Chức năng:** Biến tần điều khiển tốc độ động cơ chính 1 500 kW.
- **Hình dạng / kích thước:** box; bao 3600 × 1200 × 2400 (X × Y × Z)
- **Vị trí:** X -5200 … -1600, Y -4900 … -3700, Z 0 … 2400
- **Vật liệu / màu:** cabinet `#D8DAD6`
- **Nối với:** `ctrl_heater_cabinet` – đặt sát cạnh tại (-1600, -4000, 1000); `ctrl_trench_mv` – cáp ra đáy vào hào tại (-4000, -3700, 5); `ctx_floor` – đế 100 tại (-3400, -4300, 0)
- **Chi tiết phải dựng:** 6 khoang RAL 7035 rộng 600, sâu 1 200, cao 2 400 kể cả đế, cửa mở về +Y có lưới thông gió, đèn báo; trước cửa chừa ≥ 1 000 mm.
- **Nguồn:** giả định (biến tần trung thế 3 kV ≈ 3,6 m; thường đặt phòng điện, ở đây đặt sau máy để thể hiện); mặt cửa ở Y −3 700 theo review-01 I2

#### `ctrl_heater_cabinet` — Tủ điều khiển + nhiệt (Control and heater cabinets (PLC, heater zones, MCC))

- **Chức năng:** PLC, rơ-le bán dẫn cho vùng nhiệt xi lanh/đường chảy/khuôn, khởi động động cơ phụ.
- **Hình dạng / kích thước:** box; bao 2400 × 600 × 2200 (X × Y × Z)
- **Vị trí:** X -1600 … 800, Y -4300 … -3700, Z 0 … 2200
- **Vật liệu / màu:** cabinet `#D8DAD6`
- **Nối với:** `ctrl_drive_cabinet` – đặt sát cạnh tại (-1600, -4000, 1000); `ctrl_floor_duct` – cáp ra đáy tại (-1000, -3700, 5); `ctrl_die_bolt_cabinet` – đặt sát cạnh tại (800, -4000, 1000)
- **Chi tiết phải dựng:** 4 khoang 600 × 600 × 2 200 RAL 7035, khoang đầu có dải xanh KM và logo; cửa mở về +Y.
- **Nguồn:** c034 (tủ điện), giả định; mặt cửa ở Y −3 700 theo review-01 I2

#### `ctrl_die_bolt_cabinet` — Tủ điều khiển bulông nhiệt (Thermal-bolt controller cabinet)

- **Chức năng:** Điều khiển 94 thanh nhiệt bulông theo profin chiều dày (bộ điều khiển riêng của hệ bulông nhiệt).
- **Hình dạng / kích thước:** box; bao 800 × 600 × 2000 (X × Y × Z)
- **Vị trí:** X 800 … 1600, Y -4300 … -3700, Z 0 … 2000
- **Vật liệu / màu:** cabinet `#D8DAD6`
- **Nối với:** `ctrl_heater_cabinet` – đặt sát cạnh tại (800, -4000, 1000); `ctx_floor` – đế tại (1200, -4000, 0)
- **Chi tiết phải dựng:** Tủ 800 × 600 × 2 000 RAL 7035, màn hình profin trên cửa.
- **Nguồn:** review-01 I6; c054 (bulông nhiệt 80 W)

#### `ctrl_machine_cabinet` — Tủ đầu máy (khối cao cuối máy) (Machine-end terminal cabinet)

- **Chức năng:** Tủ đấu dây tại chỗ cho truyền động: cấp nguồn cụm dầu, encoder, cảm biến hộp số, an toàn.
- **Hình dạng / kích thước:** box; bao 500 × 1000 × 2000 (X × Y × Z)
- **Vị trí:** X -5650 … -5150, Y -500 … 500, Z 0 … 2000
- **Vật liệu / màu:** km_blue `#008DC3`
- **Nối với:** `base_frame_drive` – áp sát đầu khung tại (-5150, 0, 400); `ctrl_signal_tower` – bắt trên nóc tại (-5400, 0, 2000)
- **Chi tiết phải dựng:** Tủ 500 × 1 000 × 2 000, mặt +Y và −X sơn xanh KM có chữ KraussMaffei trắng chạy dọc, còn lại trắng; nút dừng khẩn trên mặt +Y.
- **Nguồn:** pdf_measures §2.2/§4 ghi chú 3 (khối cao trơn sau động cơ); web-06/07 (tủ trắng có dải xanh KM ở đầu dẫn động)

#### `ctrl_signal_tower` — Đèn tháp báo trạng thái (Signal tower)

- **Chức năng:** Báo trạng thái máy (đỏ/vàng/xanh/còi).
- **Hình dạng / kích thước:** revolve; bao 80 × 80 × 650 (X × Y × Z); trục Z; R 40
- **Vị trí:** X -5440 … -5360, Y -40 … 40, Z 2000 … 2650
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `ctrl_machine_cabinet` – chân đế tại (-5400, 0, 2000)
- **Chi tiết phải dựng:** 4 tầng đèn Ø70 + còi, cột Ø40.
- **Nguồn:** giả định

#### `ctrl_hmi` — Bảng điều khiển HMI trên chân đế xoay (Operator HMI on swivel pedestal)

- **Chức năng:** Màn hình cảm ứng + bàn phím màng điều khiển toàn dây chuyền; nút dừng khẩn.
- **Hình dạng / kích thước:** composite; bao 800 × 250 × 1850 (X × Y × Z)
- **Vị trí:** X -1700 … -900, Y 1400 … 1650, Z 0 … 1850
- **Vật liệu / màu:** white `#EDEEEE`
- **Nối với:** `ctx_floor` – tấm đế bắt bulông neo tại (-1300, 1525, 0)
- **Chi tiết phải dựng:** Chân đế ống Ø120 cao 1 300 có khớp xoay đen, tay xoay ngắn; tấm HMI 800 × 510 × 120 nghiêng 15°, mặt hướng +Y. Nút dừng khẩn đỏ trên vỏ HMI.
- **Nguồn:** p22_5/p23_4 (tấm HMI ngang ≈ 1,57 : 1, viền xám đen, phím màng, 2 nút tròn, logo KM, ống đỡ có khớp xoay); web-04/05 (HMI trên chân đế phía vận hành)

#### `ctrl_estops` — Hộp nút dừng khẩn dọc máy (Emergency-stop stations along the machine)

- **Chức năng:** Dừng khẩn toàn dây chuyền từ dọc máy phía vận hành, ở tầm tay.
- **Hình dạng / kích thước:** box; bao 5200 × 520 × 540 (X × Y × Z); số lượng 3
- **Vị trí:** X 550 … 5750, Y 480 … 1000, Z 650 … 1190
- **Vật liệu / màu:** yellow `#F2C200`
- **Nối với:** `base_frame_process` – cột gá trên mặt khung tại (600, 940, 650); `barrel_cover_c4` – giá gá trên tấm dưới vỏ che tại (3700, 480, 1120); `barrel_cover_c1` – giá gá trên tấm dưới vỏ che tại (5700, 480, 1120)
- **Chi tiết phải dựng:** 3 hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm Z 1 120 (tầm 1,05–1,19 m): X 600 trên cột gá 60 × 60 từ mặt khung (vùng nạp để lộ), X 3 700 trên tấm dưới vỏ C4, X 5 700 trên tấm dưới vỏ C1. Thêm nút trên HMI, tủ đầu máy, hộp đấu dây khuôn (−Y), lan can sàn thao tác (ctrl_estop_platform), khuôn phía +Y (ctrl_estop_die) và bộ lọc phía +Y (ctrl_estop_melt).
- **Nguồn:** giả định; cao độ theo review-01 M3

#### `ctrl_estop_platform` — Hộp dừng khẩn trên sàn thao tác (Emergency stop on mezzanine railing)

- **Chức năng:** Dừng khẩn từ sàn cân cấp liệu.
- **Hình dạng / kích thước:** box; bao 100 × 80 × 140 (X × Y × Z)
- **Vị trí:** X -500 … -400, Y 1340 … 1420, Z 3930 … 4070
- **Vật liệu / màu:** yellow `#F2C200`
- **Nối với:** `feed_platform_railing` – kẹp lên cột lan can tại (-450, 1390, 4000)
- **Chi tiết phải dựng:** Hộp vàng 100 × 80 × 140 có nút nấm đỏ trên cột lan can mép +Y.
- **Nguồn:** review-01 M3

#### `ctrl_estop_die` — Hộp dừng khẩn tại khuôn (+Y) (Emergency stop at die, operator side)

- **Chức năng:** Dừng khẩn khi chỉnh môi, deckle, xử lý màn nhựa ở phía vận hành.
- **Hình dạng / kích thước:** composite; bao 100 × 290 × 870 (X × Y × Z)
- **Vị trí:** X 9200 … 9300, Y 1200 … 1490, Z 300 … 1170
- **Vật liệu / màu:** yellow `#F2C200`
- **Nối với:** `die_cart` – tay đòn gá trên đầu +Y của xe khuôn tại (9250, 1200, 350)
- **Chi tiết phải dựng:** Hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm (9 250, 1 450, 1 100), trên cột ống Ø50 dựng từ tay đòn thấp (Z 300–400) gá vào đầu +Y của xe khuôn; nằm ngoài tấm đầu khuôn (|Y| > 1 375) và trước khung cụm trục. Cáp nối bằng phích cắm qua hộp đấu dây khuôn để xe khuôn kéo đi được. outline_mm (mặt YZ) là hình chữ L: tay đòn thấp Y 1 200–1 475, Z 300–400; cột Y 1 425–1 475 lên Z 1 030; hộp Y 1 410–1 490, Z 1 030–1 170.
- **Nguồn:** drawing review-01 I2; giả định

#### `ctrl_estop_melt` — Hộp dừng khẩn tại bộ lọc (+Y) (Emergency stop at screen changer, operator side)

- **Chức năng:** Dừng khẩn khi thay lưới / xử lý ở bộ lọc phía vận hành.
- **Hình dạng / kích thước:** composite; bao 100 × 90 × 870 (X × Y × Z)
- **Vị trí:** X 7270 … 7370, Y 600 … 690, Z 300 … 1170
- **Vật liệu / màu:** yellow `#F2C200`
- **Nối với:** `melt_stand_sc` – cột gá trên mặt +Y giá bộ lọc tại (7320, 600, 500)
- **Chi tiết phải dựng:** Hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm (7 320, 650, 1 100), trên cột 60 × 60 gá vào mặt +Y của giá bộ lọc, ngay sau cụm xả ngược (X ≤ 7 200).
- **Nguồn:** drawing review-01 I2; giả định

#### `ctrl_infeed_mv` — Hào cáp trung thế cấp vào (Incoming MV feed trench)

- **Chức năng:** Đưa cáp trung thế 3 kV từ trạm biến áp nhà máy vào tủ biến tần.
- **Hình dạng / kích thước:** sheet; bao 400 × 200 × 10 (X × Y × Z)
- **Vị trí:** X -3600 … -3200, Y -5100 … -4900, Z 0 … 10
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `ctrl_drive_cabinet` – vào đáy tủ tại (-3400, -4900, 5); `ctx_floor` – nắp phẳng sàn tại (-3400, -5000, 0)
- **Chi tiết phải dựng:** Đoạn hào có nắp rộng 400 phẳng sàn dài 200 sau tủ, đầu ngoài để hở 'từ trạm biến áp' (tuyến tiếp theo thuộc nhà xưởng).
- **Nguồn:** drawing review-01 I2; giả định (≈ 1,8 MVA)

#### `ctrl_infeed_lv` — Hào cáp hạ thế cấp vào (Incoming LV feed trench)

- **Chức năng:** Đưa cáp hạ thế 400 V từ tủ phân phối nhà máy vào tủ điều khiển + nhiệt.
- **Hình dạng / kích thước:** sheet; bao 400 × 200 × 10 (X × Y × Z)
- **Vị trí:** X -600 … -200, Y -4500 … -4300, Z 0 … 10
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `ctrl_heater_cabinet` – vào đáy tủ tại (-400, -4300, 5); `ctx_floor` – nắp phẳng sàn tại (-400, -4400, 0)
- **Chi tiết phải dựng:** Đoạn hào có nắp rộng 400 phẳng sàn dài 200 sau tủ, đầu ngoài để hở 'từ tủ phân phối' (tuyến tiếp theo thuộc nhà xưởng).
- **Nguồn:** drawing review-01 I2; giả định (≈ 500 kVA: nhiệt ≈ 260 kW + động cơ phụ)

#### `ctrl_floor_duct` — Hào cáp tới tủ điều khiển (Covered floor trench to control cabinets)

- **Chức năng:** Dẫn cáp từ máy về tủ điều khiển, nắp phẳng sàn.
- **Hình dạng / kích thước:** sheet; bao 400 × 2650 × 10 (X × Y × Z)
- **Vị trí:** X -1200 … -800, Y -3700 … -1050, Z 0 … 10
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `ctrl_heater_cabinet` – vào đáy tủ tại (-1000, -3700, 5); `ctrl_cable_drop` – nối máng đứng tại (-1000, -1050, 5); `ctrl_floor_trench` – nối hào cáp tại (-1000, -1150, 5)
- **Chi tiết phải dựng:** Hào cáp có nắp tôn mạ kẽm chống trượt rộng 400, phẳng sàn (nắp dày 10).
- **Nguồn:** giả định; hào phẳng sàn theo review-01 I2

#### `ctrl_cable_drop` — Máng cáp đứng (Vertical cable drop)

- **Chức năng:** Đưa cáp từ máng trên khung xuống sàn.
- **Hình dạng / kích thước:** sheet; bao 300 × 100 × 750 (X × Y × Z)
- **Vị trí:** X -1150 … -850, Y -1100 … -1000, Z 0 … 750
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `barrel_cable_tray` – nối máng tại (-990, -1000, 700); `ctrl_floor_duct` – nối máng sàn tại (-1000, -1050, 5)
- **Chi tiết phải dựng:** Máng đứng 300 × 100 áp mặt bên khung.
- **Nguồn:** giả định

#### `ctrl_floor_trench` — Hào cáp có nắp dọc dây chuyền (Covered floor cable trench along the line)

- **Chức năng:** Dẫn cáp động lực/tín hiệu tới bơm nhựa, hộp nhiệt đường chảy, HPU, cụm chân không, khuôn.
- **Hình dạng / kích thước:** sheet; bao 9700 × 200 × 10 (X × Y × Z)
- **Vị trí:** X -1000 … 8700, Y -1250 … -1050, Z 0 … 10
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `ctrl_floor_duct` – nối tại (-1000, -1150, 5); `ctrl_trench_die_branch` – nối tại (8600, -1250, 5)
- **Chi tiết phải dựng:** Nắp tôn chống trượt rộng 200 phẳng sàn; kết thúc ở X 8 700, trước ray xe khuôn.
- **Nguồn:** giả định

#### `ctrl_trench_die_branch` — Nhánh hào cáp tới hộp khuôn (Cable trench branch to die junction box)

- **Chức năng:** Đưa cáp từ hào chính tới hộp đấu dây khuôn đặt trên sàn.
- **Hình dạng / kích thước:** sheet; bao 200 × 400 × 10 (X × Y × Z)
- **Vị trí:** X 8500 … 8700, Y -1650 … -1250, Z 0 … 10
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `ctrl_floor_trench` – nối tại (8600, -1250, 5); `die_junction_box` – cáp vào đáy hộp tại (8700, -1625, 5)
- **Chi tiết phải dựng:** Nắp tôn rộng 200 phẳng sàn.
- **Nguồn:** review-01 I3/I6; giả định

#### `ctrl_trench_mv` — Hào cáp trung thế (MV cable trench)

- **Chức năng:** Dẫn cáp trung thế từ tủ biến tần tới động cơ dưới sàn, không vắt qua lối đi.
- **Hình dạng / kích thước:** sheet; bao 400 × 2650 × 10 (X × Y × Z)
- **Vị trí:** X -4200 … -3800, Y -3700 … -1050, Z 0 … 10
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `ctrl_drive_cabinet` – vào đáy tủ tại (-4000, -3700, 5); `ctrl_cable_mv` – cáp lên tại (-4000, -1100, 10)
- **Chi tiết phải dựng:** Hào có nắp tôn mạ kẽm rộng 400 phẳng sàn.
- **Nguồn:** review-01 I2; giả định

#### `ctrl_cable_mv` — Cáp trung thế động cơ (đoạn lên) (MV motor cable riser)

- **Chức năng:** Đưa cáp trung thế từ hào lên hộp đấu dây động cơ.
- **Hình dạng / kích thước:** pipe; bao 80 × 215 × 1180 (X × Y × Z); R 40
- **Vị trí:** X -4040 … -3960, Y -1140 … -925, Z 10 … 1190
- **Vật liệu / màu:** rubber `#2A2A2A`
- **Nối với:** `ctrl_trench_mv` – ra khỏi hào tại (-4000, -1100, 10); `drive_motor_terminal_box` – ốc siết cáp tại (-4000, -925, 1150)
- **Chi tiết phải dựng:** 3 cáp trung thế trong ống bảo vệ Ø80 dựng lên sát mặt bên khung (Y −1 100) rồi vào đáy hộp đấu dây.
- **Nguồn:** giả định

### Tiện ích (utilities) — 14 mục

#### `util_cw_supply_riser` — Ống nước cấp từ nhà máy (Plant cooling-water supply riser)

- **Chức năng:** Đưa nước làm mát (≈ 15 °C, 4 bar) từ đường ống nhà máy lên ống góp.
- **Hình dạng / kích thước:** pipe; bao 130 × 240 × 740 (X × Y × Z); R 30
- **Vị trí:** X -430 … -300, Y 850 … 1090, Z 0 … 740
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `ctx_floor` – bích sàn tại (-400, 1060, 0); `barrel_cw_supply` – bích DN50 tại (-300, 880, 710); `util_cw_lube_hoses` – nhánh T tại (-400, 1060, 380); `util_cw_motor_hoses` – nhánh T tại (-400, 1060, 250)
- **Chi tiết phải dựng:** DN50 có van bi tay đỏ, lọc Y và đồng hồ áp ở đoạn đứng.
- **Nguồn:** giả định

#### `util_cw_return_riser` — Ống nước hồi về nhà máy (Plant cooling-water return riser)

- **Chức năng:** Trả nước hồi về đường ống nhà máy.
- **Hình dạng / kích thước:** pipe; bao 230 × 240 × 830 (X × Y × Z); R 30
- **Vị trí:** X -530 … -300, Y 920 … 1160, Z 0 … 830
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `ctx_floor` – bích sàn tại (-500, 1130, 0); `barrel_cw_return` – bích DN50 tại (-300, 950, 800); `util_cw_lube_hoses` – nhánh T tại (-500, 1130, 440); `util_cw_motor_hoses` – nhánh T tại (-500, 1130, 150)
- **Chi tiết phải dựng:** DN50 có van bi tay đỏ và nhiệt kế.
- **Nguồn:** giả định

#### `util_cw_lube_hoses` — Ống nước làm mát dầu hộp số (Cooling water to lube oil cooler)

- **Chức năng:** Cấp/hồi nước cho bộ làm mát dầu hộp số.
- **Hình dạng / kích thước:** pipe; bao 2435 × 250 × 540 (X × Y × Z); số lượng 2; R 20
- **Vị trí:** X -2835 … -400, Y 900 … 1150, Z 360 … 900
- **Vật liệu / màu:** hose `#9A9FA4`
- **Nối với:** `util_cw_supply_riser` – nhánh T (cấp) tại (-400, 1060, 380); `util_cw_return_riser` – nhánh T (hồi) tại (-500, 1130, 440); `lube_oil_cooler` – cổng F2/F4 tại (-2815, 900, 820)
- **Chi tiết phải dựng:** 2 ống mềm DN25 chạy ngoài mép +Y của khung: cấp ở Y 1 060, Z 380; hồi ở Y 1 130, Z 440; lên và vào cổng F2/F4 của bộ làm mát. Van bi tay đỏ trên mỗi ống ngay trước bộ làm mát; van điều nhiệt nước trên ống hồi.
- **Nguồn:** web-03 (ống mềm đen vào bộ làm mát)

#### `util_cw_motor_hoses` — Ống nước bộ làm mát động cơ (Cooling water to motor top cooler)

- **Chức năng:** Cấp/hồi nước cho bộ làm mát gió–nước trên nóc động cơ chính (IC81W).
- **Hình dạng / kích thước:** pipe; bao 3324 × 579 × 2298 (X × Y × Z); số lượng 2; R 24
- **Vị trí:** X -3724 … -400, Y 575 … 1154, Z 126 … 2424
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `util_cw_supply_riser` – nhánh T (cấp) tại (-400, 1060, 250); `util_cw_return_riser` – nhánh T (hồi) tại (-500, 1130, 150); `drive_motor` – bích DN40 trên mặt +Y bộ làm mát tại (-3500, 575, 2300)
- **Chi tiết phải dựng:** 2 ống inox DN40 (OD 48) chạy thấp ngoài mép +Y khung (cấp Y 1 060 Z 250, hồi Y 1 130 Z 150), dựng lên tại X −3 500 / −3 700 cạnh cụm dầu, rồi vào bích trên mặt +Y bộ làm mát động cơ ở Z 2 300 / 2 400; van bi tay đỏ ở mỗi ống.
- **Nguồn:** review-01 M9; giả định (≈ 45 kW nhiệt, 2 × DN40)

#### `util_cw_throat_hoses` — Ống nước áo hộp miệng nạp (Cooling water to feed throat jacket)

- **Chức năng:** Làm mát hộp miệng nạp để hạt không dính chảy ở miệng.
- **Hình dạng / kích thước:** pipe; bao 70 × 785 × 615 (X × Y × Z); số lượng 2; R 15
- **Vị trí:** X 303 … 373, Y 210 … 995, Z 1000 … 1615
- **Vật liệu / màu:** hose `#9A9FA4`
- **Nối với:** `barrel_cw_valves` – cụm van 1 (nhánh thứ hai) tại (318, 980, 1000); `feed_throat` – 2 đầu nối nước mặt +Y tại (318, 210, 1550)
- **Chi tiết phải dựng:** 2 ống mềm inox DN20 từ đỉnh cụm van 1 lên Z 1 550/1 600 rồi vào mặt +Y hộp miệng nạp.
- **Nguồn:** review-01 I7; giả định

#### `util_cw_sidefeed_hoses` — Ống nước áo side feeder (Cooling water to side-feeder jacket)

- **Chức năng:** Làm mát thân side feeder.
- **Hình dạng / kích thước:** pipe; bao 252.4 × 98.2 × 93 (X × Y × Z); số lượng 2; R 12
- **Vị trí:** X 1159.6 … 1412, Y 893.8 … 992, Z 988.2 … 1081.2
- **Vật liệu / màu:** hose `#9A9FA4`
- **Nối với:** `barrel_cw_valves` – cụm van 2 (nhánh thứ hai) tại (1163, 980, 1000); `sidefeed_barrel` – 2 đầu nối dưới thân tại (1300, 900, 1070)
- **Chi tiết phải dựng:** 2 ống mềm inox DN15 từ đỉnh cụm van 2 vào mặt dưới thân side feeder.
- **Nguồn:** review-01 I7; giả định

#### `util_cw_vac_hoses` — Ống nước cụm chân không (Cooling water to vacuum separator and pump skid)

- **Chức năng:** Cấp/hồi nước cho ống xoắn ngưng của bình tách và cho bơm Roots/bơm khô làm mát nước.
- **Hình dạng / kích thước:** pipe; bao 95.5 × 732 × 1116 (X × Y × Z); số lượng 4; R 16
- **Vị trí:** X 4404.5 … 4500, Y -3066 … -2334, Z 0 … 1116
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `ctx_floor` – đầu nối nước nhà máy dưới sàn tại (4460, -2450, 0); `vac_separator` – cổng ống xoắn tại (4420, -2600, 1000); `vac_pump_unit` – ống góp nước skid tại (4500, -2350, 400)
- **Chi tiết phải dựng:** 4 ống inox DN25 (OD 32) đứng lên từ hai cặp đầu nối sàn giữa bình tách và skid: cặp cho bình tách vào Z 1 000 / ra Z 1 100, cặp cho skid vào/ra ở Z 400; van bi tay đỏ ở chân mỗi ống.
- **Nguồn:** review-01 I7; giả định (lấy nước nhà máy tại chỗ qua hai đầu nối sàn, không băng qua máy)

#### `util_air_drop` — Ống khí nén xuống khuôn (Compressed-air drop at die)

- **Chức năng:** Cấp khí nén 6 bar từ đường trên cao cho làm mát bulông nhiệt.
- **Hình dạng / kích thước:** pipe; bao 30 × 30 × 3600 (X × Y × Z); R 15
- **Vị trí:** X 9345 … 9375, Y -1720 … -1690, Z 900 … 4500
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `util_frl` – đầu nối ren tại (9360, -1705, 900)
- **Chi tiết phải dựng:** Ống thép mạ Ø30, đầu trên để hở 'từ đường khí nhà máy'.
- **Nguồn:** c054 (bulông nhiệt có làm mát gió); giả định

#### `util_frl` — Bộ lọc–điều áp khí nén (khuôn) (Air filter-regulator at die (FRL))

- **Chức năng:** Lọc, điều áp khí làm mát bulông nhiệt.
- **Hình dạng / kích thước:** composite; bao 120 × 110 × 250 (X × Y × Z)
- **Vị trí:** X 9300 … 9420, Y -1760 … -1650, Z 650 … 900
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `die_junction_box` – giá gá mặt +X hộp khuôn tại (9300, -1705, 775); `util_air_drop` – cổng vào tại (9360, -1705, 900); `util_air_hose_die` – cổng ra tại (9360, -1650, 880)
- **Chi tiết phải dựng:** Bộ lọc + van điều áp + đồng hồ, van khoá tay.
- **Nguồn:** giả định

#### `util_air_hose_die` — Ống khí làm mát bulông nhiệt (Cooling-air hose to thermal bolts)

- **Chức năng:** Dẫn khí làm mát tới ống gió của thanh bulông nhiệt.
- **Hình dạng / kích thước:** pipe; bao 94 × 422 × 744 (X × Y × Z); R 12
- **Vị trí:** X 9278 … 9372, Y -1650 … -1228, Z 868 … 1612
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `util_frl` – cổng ra tại (9360, -1650, 880); `die_bolt_actuator_rail` – đầu nối khí tại (9290, -1240, 1540)
- **Chi tiết phải dựng:** Ống mềm PU Ø24, khớp nối nhanh ở đầu thanh để tách khuôn.
- **Nguồn:** web-18 (ống gió làm mát đen tại môi khuôn)

#### `util_air_drop_2` — Ống khí nén xuống cột sàn (Compressed-air drop at mezzanine column)

- **Chức năng:** Cấp khí nén cho van chân không và thiết bị cấp liệu.
- **Hình dạng / kích thước:** pipe; bao 30 × 30 × 2900 (X × Y × Z); R 15
- **Vị trí:** X -315 … -285, Y -2615 … -2585, Z 1600 … 4500
- **Vật liệu / màu:** galv `#A9AFB4`
- **Nối với:** `util_frl_2` – đầu nối ren tại (-300, -2600, 1600)
- **Chi tiết phải dựng:** Ống thép mạ Ø30 dọc cột sàn X −450, Y −2 600, xuyên sàn; đầu trên để hở 'từ đường khí nhà máy'.
- **Nguồn:** review-01 M10; giả định

#### `util_frl_2` — Bộ lọc–điều áp khí nén (cấp liệu, chân không) (Air filter-regulator at mezzanine column)

- **Chức năng:** Lọc, điều áp khí cho van bướm chân không, van nạp máy hút liệu, van cân.
- **Hình dạng / kích thước:** composite; bao 100 × 120 × 250 (X × Y × Z)
- **Vị trí:** X -350 … -250, Y -2660 … -2540, Z 1350 … 1600
- **Vật liệu / màu:** stainless `#B8BEC4`
- **Nối với:** `feed_platform_columns_rear` – giá gá mặt +X cột tại (-350, -2600, 1475); `util_air_drop_2` – cổng vào tại (-300, -2600, 1600); `util_air_tube_vac` – cổng ra tại (-250, -2600, 1500); `util_air_tube_loader` – cổng ra tại (-300, -2540, 1600)
- **Chi tiết phải dựng:** Bộ lọc + van điều áp + đồng hồ, van khoá tay, cao 1,35–1,6 m.
- **Nguồn:** review-01 M10; giả định

#### `util_air_tube_vac` — Ống khí tới van chân không (Air tube to vacuum valve actuator)

- **Chức năng:** Cấp khí cho bộ tác động van bướm chân không vùng 2.
- **Hình dạng / kích thước:** pipe; bao 4276 × 2356 × 962 (X × Y × Z); R 6
- **Vị trí:** X -256 … 4020, Y -2600 … -244, Z 1494 … 2456
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `util_frl_2` – cổng ra tại (-250, -2600, 1500); `vac_valve` – bộ tác động tại (4020, -250, 2180)
- **Chi tiết phải dựng:** Ống PU Ø12 đi trên máng nhỏ dưới sàn thao tác ở Z 2 450 rồi tới bộ tác động van.
- **Nguồn:** review-01 M10; giả định

#### `util_air_tube_loader` — Ống khí tới máy hút liệu (Air tube to vacuum loader)

- **Chức năng:** Cấp khí cho van lật xả của máy hút liệu và van nạp của cân.
- **Hình dạng / kích thước:** pipe; bao 12 × 2226 × 3406 (X × Y × Z); R 6
- **Vị trí:** X -306 … -294, Y -2546 … -320, Z 1600 … 5006
- **Vật liệu / màu:** black `#1F1F1F`
- **Nối với:** `util_frl_2` – cổng ra tại (-300, -2540, 1600); `feed_vacuum_loader` – van lật xả tại (-300, -320, 5000)
- **Chi tiết phải dựng:** Ống PU Ø12 lên dọc cột, đi trên mặt sàn, rồi dọc phễu cân lên van máy hút liệu.
- **Nguồn:** review-01 M10; giả định

### Bối cảnh (context, collection ze155_context) — 8 mục

#### `ctx_floor` — Sàn nhà xưởng (Workshop floor)

- **Chức năng:** Mặt bằng đặt máy (Z = 0).
- **Hình dạng / kích thước:** box; bao 20500 × 9000 × 20 (X × Y × Z)
- **Vị trí:** X -7000 … 13500, Y -5500 … 3500, Z -20 … 0
- **Vật liệu / màu:** floor `#B9B7B0`
- **Nối với:** `base_feet` – nền bê tông tại (-300, 900, 0)
- **Chi tiết phải dựng:** Tấm phẳng xám, có vạch vàng lối đi quanh máy (tuỳ chọn).
- **Nguồn:** BRIEF (Z = 0 sàn)

#### `ctx_roll_bottom` — Trục cán láng dưới (Polishing roll (bottom))

- **Chức năng:** Làm nguội và cán bóng tấm nhựa.
- **Hình dạng / kích thước:** revolve; bao 800 × 3200 × 800 (X × Y × Z); trục Y; R 400
- **Vị trí:** X 9376 … 10176, Y -1600 … 1600, Z 399 … 1199
- **Vật liệu / màu:** chrome `#E3E6E9`
- **Nối với:** `ctx_roll_stand` – gối đỡ trục trong khung tại (9776, 1500, 799)
- **Chi tiết phải dựng:** Trục Ø800 mặt 2 600 (Y ±1 300) mạ crôm gương, cổ trục Ø300 tới Y ±1 600, tâm X = 9 776, Z = 799.
- **Nguồn:** c046 (Ø 400–800), c044 (PlanetCalender 3 trục); DECISIONS 10 (khe trục giữa–dưới tại cao độ môi khuôn)

#### `ctx_roll_middle` — Trục cán láng giữa (Polishing roll (middle))

- **Chức năng:** Làm nguội và cán bóng tấm nhựa.
- **Hình dạng / kích thước:** revolve; bao 800 × 3200 × 800 (X × Y × Z); trục Y; R 400
- **Vị trí:** X 9376 … 10176, Y -1600 … 1600, Z 1201 … 2001
- **Vật liệu / màu:** chrome `#E3E6E9`
- **Nối với:** `ctx_roll_stand` – gối đỡ trục trong khung tại (9776, 1500, 1601); `ctx_sheet` – tấm ôm trục giữa tại (9776, 0, 1201)
- **Chi tiết phải dựng:** Trục Ø800 mặt 2 600 (Y ±1 300) mạ crôm gương, cổ trục Ø300 tới Y ±1 600, tâm X = 9 776, Z = 1601.
- **Nguồn:** c046 (Ø 400–800), c044 (PlanetCalender 3 trục); DECISIONS 10 (khe trục giữa–dưới tại cao độ môi khuôn)

#### `ctx_roll_top` — Trục cán láng trên (Polishing roll (top))

- **Chức năng:** Làm nguội và cán bóng tấm nhựa.
- **Hình dạng / kích thước:** revolve; bao 800 × 3200 × 800 (X × Y × Z); trục Y; R 400
- **Vị trí:** X 9376 … 10176, Y -1600 … 1600, Z 2003 … 2803
- **Vật liệu / màu:** chrome `#E3E6E9`
- **Nối với:** `ctx_roll_stand` – gối đỡ trục trong khung tại (9776, 1500, 2403); `ctx_sheet` – tấm ôm nửa −X trục trên tại (9376, 0, 2403)
- **Chi tiết phải dựng:** Trục Ø800 mặt 2 600 (Y ±1 300) mạ crôm gương, cổ trục Ø300 tới Y ±1 600, tâm X = 9 776, Z = 2403.
- **Nguồn:** c046 (Ø 400–800), c044 (PlanetCalender 3 trục); DECISIONS 10 (khe trục giữa–dưới tại cao độ môi khuôn)

#### `ctx_roll_stand` — Khung cụm trục cán (Roll stack stand)

- **Chức năng:** Đỡ 3 trục, chỉnh khe trục, chạy trên ray để lùi xa khuôn.
- **Hình dạng / kích thước:** frame; bao 1660 × 3500 × 3040 (X × Y × Z)
- **Vị trí:** X 9540 … 11200, Y -1750 … 1750, Z 60 … 3100
- **Vật liệu / màu:** frame `#DCDDDE`
- **Nối với:** `ctx_roll_middle` – gối trục tại (9776, 1500, 1601); `ctx_roll_rails` – bánh xe tại (10000, 1550, 60)
- **Chi tiết phải dựng:** 2 khung bên dày 350 tại Y ±(1 400…1 750), dầm ngang phía sau, xi lanh ép khe trục, dải xanh KM có chữ KraussMaffei. Mép trước khung bên ở X 9 540 tại gối trục dưới và trục giữa, nhưng lõm vào tới X 9 800 trong dải Z 1 060–1 340 quanh khe trục, để núm deckle và tấm đầu khuôn có khe hở thật (≈ 280 mm). outline_mm là hình bên của khung +Y (Y 1 400…1 750); khung −Y đối xứng qua Y = 0.
- **Nguồn:** p24-25 (khung đứng sau trục), web-09 (khung trắng dải xanh KM); kích thước giả định specs §6

#### `ctx_roll_drives` — Động cơ trục cán (Roll drives)

- **Chức năng:** Quay 3 trục cán.
- **Hình dạng / kích thước:** composite; bao 450 × 600 × 2104 (X × Y × Z); số lượng 3
- **Vị trí:** X 9551 … 10001, Y -2350 … -1750, Z 549 … 2653
- **Vật liệu / màu:** white `#EDEEEE`
- **Nối với:** `ctx_roll_stand` – mặt bích tại (9776, -1750, 1600)
- **Chi tiết phải dựng:** 3 động cơ hộp số 450 × 600 × 500 phía −Y, đồng trục với từng trục cán.
- **Nguồn:** p24-25 (3 khối nhỏ sau khung)

#### `ctx_roll_rails` — Ray cụm trục cán (Roll stack floor rails)

- **Chức năng:** Cho cụm trục lùi theo +X.
- **Hình dạng / kích thước:** frame; bao 2950 × 3160 × 60 (X × Y × Z); số lượng 2
- **Vị trí:** X 9550 … 12500, Y -1580 … 1580, Z 0 … 60
- **Vật liệu / màu:** steel `#8C9298`
- **Nối với:** `ctx_roll_stand` – bánh xe tại (10000, 1550, 60); `ctx_floor` – bulông neo tại (10000, 1550, 0)
- **Chi tiết phải dựng:** 2 ray 60 × 60 dài 2 950 tại Y = ±1 550.
- **Nguồn:** specs §6 (lùi 1 000–1 500 mm)

#### `ctx_sheet` — Màn nhựa / tấm (Melt curtain and sheet)

- **Chức năng:** Màn nhựa từ môi khuôn vào khe trục giữa–dưới, ôm nửa +X trục giữa, ôm nửa −X trục trên rồi ra theo +X (đường chữ S).
- **Hình dạng / kích thước:** sheet; bao 1025 × 2100 × 1606 (X × Y × Z)
- **Vị trí:** X 9375 … 10400, Y -1050 … 1050, Z 1199 … 2805
- **Vật liệu / màu:** glass `#7FB6C9`
- **Nối với:** `die_flex_lip` – khe môi tại (9576, 0, 1200); `ctx_roll_middle` – ôm trục tại (9776, 0, 1201); `ctx_roll_top` – ôm trục tại (9376, 0, 2403)
- **Chi tiết phải dựng:** Tấm rộng 2 100, dày 1 mm; đường tâm trong path_mm (mặt XZ, Y = 0): môi khuôn (9 576, 1 200) → khe trục (9 776, 1 200) → ôm nửa +X trục giữa tới đỉnh (9 776, 2 002) → ôm nửa −X trục trên (qua X 9 375) tới đỉnh (9 776, 2 804) → ra +X ở Z 2 804. Đầu đo chiều dày quét ngang (traversing gauge) cho điều khiển profin đặt sau cụm trục, không dựng.
- **Nguồn:** pdf_measures §5 và p24-25_slot_die_smoothing_roll (đường tấm chữ S); specs §0 (tấm 2 100); review-01 M7

<!-- END PARTS -->

## 6. Các mối nối

### 6.1 Diễn giải theo môi chất

- **Đường nhựa (melt):**
  - B6 → đầu xi lanh: lỗ số 8 chuyển sang lỗ tròn Ø120, bích Ø640 với 20 bulông cấy M24 trên PCD 560 (cùng kiểu với các mối nối xi lanh). Bảng bích đầy đủ ở §6.3.
  - Đầu xi lanh → van khởi động → bích vào bộ lọc: 12 vít M24 lục giác chìm bắt từ phía van vào lỗ ren của bích kề, không có đai ốc sau bích nên không chạm thân côn. Có cảm biến P1, T1 và đĩa nổ 1.
    - Ở vị trí khởi động, van xả xuống máng và xe hứng.
    - Ở vị trí chạy: bích vào bộ lọc (P2) → bộ lọc lưới → bích vào bơm (P3) → bơm bánh răng → bích ra (P4, đĩa nổ 2) → ống gia nhiệt → bộ trộn tĩnh → bích khuôn (P5, T5) → ống phân phối móc áo → môi mềm → màn nhựa → khe trục cán.
  - Mọi mối nối đồng trục ở Z = 1 200. Bích lộ ra có băng nhiệt; ống và bộ trộn có băng nhiệt dưới vỏ inox.
- **Vật liệu (material):**
  - Silo → ống hút liệu → máy hút liệu → phễu cân → cân BSP-150 → ống mềm cách cân (Z 2 850–3 000) → ống rơi Ø250 (đứng rồi nghiêng 45°) → ống mềm → phễu → hộp miệng nạp → B1.
  - Phụ gia: cân nhỏ → ống mềm cách cân → ống Ø80 → nhánh Y của ống rơi.
  - Liệu phụ: cân side feeder → ống mềm cách cân → ống Ø150 → phễu side feeder → 2 trục vít ngang → cửa bên B2.
- **Nước làm mát (water):**
  - Ống nhà máy đứng ở X ≈ −400…−500, phía +Y ngoài khung → ống góp cấp DN50 (Z 710) → 6 cụm van (van bi, lọc Y, van điện từ, van tiết lưu, chỉ báo dòng) → ống mềm inox → đầu nối ở góc dưới +Y của mỗi đoạn 6D (45°, tại đầu đoạn + 200 vào, cuối đoạn − 200 ra; B1 ở đáy X 200/476). Không đầu nối nào nằm dưới gối đỡ.
  - Nước hồi theo ống mềm về ống góp hồi DN50 (Z 800) rồi ống nhà máy.
  - Cụm van 1 cấp thêm cho áo hộp miệng nạp (2 × DN20), cụm van 2 cấp thêm cho áo side feeder (2 × DN15).
  - Từ hai ống nhà máy: 2 × DN25 cho bộ làm mát dầu hộp số, 2 × DN40 cho bộ làm mát gió–nước trên nóc động cơ.
  - Cụm chân không lấy nước nhà máy tại chỗ qua hai cặp đầu nối sàn: ống xoắn ngưng của bình tách và ống góp của skid bơm (4 × DN25), không băng qua máy.
  - HPU làm mát dầu bằng quạt gió, không dùng nước.
  - Nước ngưng của bình tách xuống nồi xả kiểu khoá (lock pot), xả được khi đang chạy.
- **Chân không (vacuum):**
  - Vùng 2 (sâu, 5–20 mbar): nắp vòm B5 → van bướm khí nén (đứng trên nắp) → cút + ống xếp → ống DN150 đi ngang về −Y ở tâm Z 2 300 (đáy ống 2 216), đỡ bằng cột tại Y −1 900 → xuống nắp bình tách ở X 4 120, Y −2 700.
  - Vùng 1 (≈ 50 mbar): mặt −Y vòm B3 → van bi DN100 → ống xếp → ống DN100 dựng lên ngoài vỏ che tới Z 2 250, đi ngang về −Y rồi theo +X tới X 3 700 → van tiết lưu (cao 1,65 m) → cổng bên −X của bình tách.
  - Bình tách → ống DN100 (van điều chỉnh/xả trên đỉnh) → bơm Roots → bơm khô → ống xả lên mái.
  - Có đồng hồ trên mỗi vòm và trên bình tách.
- **Dầu bôi trơn (oil):**
  - Carter hộp số → ống hút DN40 dọc mép +Y (Z 760) → bơm có động cơ đứng → lọc kép → bộ làm mát dầu tấm → ống áp DN32 (Z 1 500) → cổng dầu phía +Y hộp số → vòi phun bánh răng và ổ trục.
  - Theo c033, hộp số bôi trơn kết hợp ngâm dầu và dầu áp lực.
- **Thuỷ lực (hydraulic):** HPU (−Y, X 6 400–7 250, Y −2 700 … −2 000) → 2 ống mềm P/T treo ở Z 1 150 tới tay quay bộ lọc; 2 ống mềm tới xi lanh van khởi động.
- **Động lực (power):**
  - Tủ biến tần trung thế → hào cáp trung thế có nắp phẳng sàn (X −4 000) → dựng lên cạnh khung tại Y −1 100 → hộp đấu dây động cơ (−Y).
  - Tủ điều khiển → hào cáp tới tủ (X −1 000) → máng đứng → máng trên khung (−Y) → hộp đấu dây nhiệt → băng nhiệt xi lanh.
  - Tủ điều khiển → hào cáp dọc dây chuyền (Y −1 150) → hộp nhiệt đường chảy (bộ lọc 39 kW, van, bơm, các bích, ống, bộ trộn, ≈ 75 kW) qua 7 ống luồn; → động cơ bơm nhựa, HPU, cụm chân không; → nhánh hào → hộp đấu dây khuôn (nhiệt khuôn).
  - Tủ bulông nhiệt → kênh đế tủ → hào → hộp đấu dây khuôn → bó cáp cắm rút tới 94 bulông nhiệt.
  - Cáp side feeder đi qua kênh ngang trong hộp tủ khung đế sang phía +Y; cáp tủ cân đi theo cột sàn thao tác; tủ đầu máy cấp nguồn cụm dầu.
- **Tín hiệu (signal):**
  - HMI ↔ tủ điều khiển (Ethernet, qua kênh khung đế và hào).
  - Encoder → tủ biến tần (ống riêng trong hào trung thế).
  - Cảm biến P1…P5, T, tín hiệu đứt đĩa nổ 2 → tủ điều khiển (qua hào cáp).
  - Cặp nhiệt → hộp đấu dây.
  - Mạch dừng khẩn nối tiếp các nút, kể cả nút trên lan can sàn thao tác.
  - Đèn tháp nối tủ đầu máy; bulông nhiệt → hộp khuôn.
  - Vòng điều khiển áp hút bơm: P3 → PIC trong PLC → biến tần bơm nhựa (`s_20`).
  - Khoá liên động truyền động: công tắc áp dầu + PT100 dầu (`s_14`), công tắc liên động vỏ che khớp nối (`s_15`), công tắc nhả khớp an toàn (`s_16`) → tủ đầu máy → PLC (`s_17`).
  - Ngắt cứng truyền động chính: P1 HH 350 bar (`s_11`), đứt đĩa nổ 1 và 2 (`s_12`, `s_13`) → tủ biến tần; mạch dừng khẩn và STO nối cứng tủ điều khiển ↔ tủ biến tần (`s_10`), cùng Profinet.
  - Nút dừng khẩn mới tại khuôn phía +Y (`s_18`) và tại bộ lọc phía +Y (`s_19`).
- **Cơ khí (mechanical):**
  - Trục động cơ Ø140 → khớp đàn hồi → khớp an toàn giới hạn mômen → trục vào hộp số → hai trục ra then hoa 24 răng → ống then hoa trong lantern → hai trục vít.
  - Động cơ bơm đứng → hộp giảm tốc góc → các-đăng → trục bơm.
  - Động cơ side feeder → hộp số → 2 trục vít.
- **Nguồn cấp vào:** trung thế 3 kV từ trạm biến áp vào tủ biến tần (`p_12`, ≈ 1,8 MVA); hạ thế 400 V từ tủ phân phối nhà máy vào tủ điều khiển + nhiệt (`p_13`, ≈ 500 kVA).
- **Khí nén (air):**
  - Ống khí xuống khuôn (X 9 360, Y −1 705) → bộ lọc–điều áp trên hông hộp khuôn → ống PU Ø24 → ống gió làm mát của thanh bulông nhiệt.
  - Ống khí xuống cột sàn (X −300, Y −2 600) → bộ lọc–điều áp trên cột → ống Ø12 tới bộ tác động van chân không vùng 2 và tới van lật của máy hút liệu.

### 6.2 Bảng mối nối (đường đi `path_mm` có trong `parts.json`)

<!-- BEGIN CONNECTIONS -->
| id | từ | tới | môi chất | kiểu nối | số điểm đường đi |
|---|---|---|---|---|---|
| `melt_01` | `barrel_b6` | `melt_head_adapter` | melt | bích 20 × M24, lỗ số 8 → tròn | 3 |
| `melt_02` | `melt_head_adapter` | `melt_startup_valve` | melt | 12 vít M24 từ phía van | 3 |
| `melt_03` | `melt_startup_valve` | `melt_screen_changer` | melt | 12 vít M24 từ phía van (PCD 360) → bích Ø420 → 8 × M30 PCD 360 vào bộ lọc; lòng Ø120; qua melt_sc_adapter_in (P2) | 4 |
| `melt_04` | `melt_startup_valve` | `melt_purge_cart` | melt | vị trí khởi động: xả xuống máng | 4 |
| `melt_05` | `melt_screen_changer` | `melt_gear_pump` | melt | bích Ø360, 8 × M30 PCD 300 ra bộ lọc / 8 × M24 PCD 300 vào bơm; lòng Ø110 → Ø100; qua melt_pump_adapter_in (P3) | 4 |
| `melt_06` | `melt_gear_pump` | `melt_static_mixer` | melt | bích Ø300, 8 × M24 PCD 250, lòng Ø100; qua adapter ra (P4, đĩa nổ 2) và ống gia nhiệt | 5 |
| `melt_07` | `melt_static_mixer` | `die_body_upper` | melt | bích Ø300, 8 × M24 PCD 250 → bích chữ nhật 500 × 360, 8 × M30 vào khuôn; lòng Ø100; qua melt_die_adapter (P5/T5) vào ống phân phối | 4 |
| `melt_08` | `die_flex_lip` | `ctx_sheet` | melt | khe môi 2 400 → màn nhựa vào khe trục | 3 |
| `melt_09` | `melt_screen_changer` | `melt_sc_backflush` | melt | nhựa xả ngược ra máng | 2 |
| `mat_01` | `feed_conveying_line` | `feed_vacuum_loader` | material | hút khí nén chân không | 3 |
| `mat_02` | `feed_vacuum_loader` | `feed_main_feeder` | material | rơi tự do qua phễu | 3 |
| `mat_03` | `feed_main_feeder` | `barrel_b1` | material | ống mềm cách cân → ống rơi → ống mềm → phễu → miệng nạp | 7 |
| `mat_04` | `feed_additive_feeder` | `feed_downpipe` | material | ống mềm cách cân → ống phụ gia → nhánh Y | 4 |
| `mat_05` | `sidefeed_feeder` | `barrel_b2` | material | ống mềm cách cân → ống rơi → side feeder → cửa bên | 6 |
| `w_01` | `util_cw_supply_riser` | `barrel_cw_valves` | water | DN50 nước cấp | 4 |
| `w_02` | `barrel_cw_valves` | `barrel_b4` | water | ống mềm DN15 vào đầu nối 45° dưới +Y tại X = đầu đoạn + 200 (tương tự các đoạn khác; B1 ở đáy X 200) | 4 |
| `w_03` | `barrel_b4` | `barrel_cw_return` | water | ống mềm ra tại X = cuối đoạn − 200 qua cụm van về ống hồi | 5 |
| `w_04` | `barrel_cw_return` | `util_cw_return_riser` | water | DN50 nước hồi | 5 |
| `w_05` | `util_cw_supply_riser` | `lube_oil_cooler` | water | ống mềm DN25 cấp/hồi bộ làm mát dầu | 4 |
| `w_06` | `barrel_cw_valves` | `feed_throat` | water | 2 ống mềm DN20 tới áo hộp miệng nạp | 3 |
| `w_07` | `barrel_cw_valves` | `sidefeed_barrel` | water | 2 ống mềm DN15 tới áo side feeder | 3 |
| `w_08` | `ctx_floor` | `vac_separator` | water | đầu nối nước sàn → ống xoắn bình tách | 3 |
| `w_09` | `ctx_floor` | `vac_pump_unit` | water | đầu nối nước sàn → ống góp skid bơm | 3 |
| `w_10` | `util_cw_supply_riser` | `drive_motor` | water | 2 ống DN40 tới bộ làm mát gió–nước trên nóc động cơ | 4 |
| `v_01` | `barrel_vent_dome` | `vac_pump_unit` | vacuum | DN150 qua nắp vòm, Z 2 300 → bình tách → DN100 → Roots | 8 |
| `v_02` | `vac_pump_unit` | `vac_exhaust` | vacuum | khí xả sau bơm | 2 |
| `v_03` | `barrel_b3` | `barrel_vent_dome_2` | vacuum | hơi nước từ lỗ thoát khí B3 vào vòm vùng 1 | 2 |
| `v_04` | `vac_separator` | `vac_drain` | water | nước ngưng qua van trên vào nồi xả | 2 |
| `v_05` | `barrel_vent_dome_2` | `vac_separator` | vacuum | DN100 qua van chặn, ống xếp, Z 2 250, van tiết lưu → cổng bên bình tách (≈ 50 mbar) | 8 |
| `o_01` | `gearbox` | `lube_pump_motor` | oil | ống hút DN40 từ carter | 4 |
| `o_02` | `lube_pump_motor` | `gearbox` | oil | bơm → lọc kép → làm mát → ống DN32 → vòi phun | 6 |
| `h_01` | `melt_hpu` | `melt_sc_drive` | hydraulic | 2 ống mềm P/T | 4 |
| `h_02` | `melt_hpu` | `melt_startup_cyl` | hydraulic | 2 ống mềm | 5 |
| `p_01` | `ctrl_drive_cabinet` | `drive_motor_terminal_box` | power | cáp trung thế 3 kV trong hào rồi dựng lên | 5 |
| `p_02` | `ctrl_heater_cabinet` | `barrel_heater_jboxes` | power | cáp nhiệt qua hào, máng đứng, máng trên khung | 7 |
| `p_03` | `ctrl_heater_cabinet` | `die_junction_box` | power | cáp nhiệt khuôn qua hào và nhánh hào | 5 |
| `p_04` | `ctrl_heater_cabinet` | `melt_pump_motor` | power | cáp động lực qua hào | 5 |
| `p_05` | `ctrl_heater_cabinet` | `vac_control_box` | power | cáp động lực qua hào | 5 |
| `p_06` | `ctrl_heater_cabinet` | `melt_hpu` | power | cáp động lực qua hào | 4 |
| `p_07` | `ctrl_heater_cabinet` | `sidefeed_motor` | power | cáp qua kênh ngang trong khung đế | 6 |
| `p_08` | `ctrl_heater_cabinet` | `feed_control_cabinet` | power | cáp theo cột sàn lên tủ cân | 6 |
| `p_09` | `ctrl_machine_cabinet` | `lube_pump_motor` | power | cáp động cơ bơm dầu | 4 |
| `p_10` | `ctrl_heater_cabinet` | `melt_heater_jbox` | power | cáp nhiệt đường chảy (≈ 75 kW) qua hào | 4 |
| `p_11` | `ctrl_die_bolt_cabinet` | `die_junction_box` | power | cáp 94 mạch bulông nhiệt qua kênh đế tủ, hào chính, nhánh hào | 7 |
| `s_01` | `ctrl_hmi` | `ctrl_heater_cabinet` | signal | Ethernet/Profinet qua kênh khung đế | 7 |
| `s_02` | `drive_encoder` | `ctrl_drive_cabinet` | signal | cáp encoder theo hào trung thế (ống riêng) | 5 |
| `s_03` | `melt_sensor_head` | `ctrl_heater_cabinet` | signal | cáp cảm biến P1…P5/T qua hào | 6 |
| `s_04` | `barrel_thermocouples` | `barrel_heater_jboxes` | signal | cáp bù cặp nhiệt | 3 |
| `s_05` | `ctrl_machine_cabinet` | `ctrl_signal_tower` | signal | cáp đèn | 2 |
| `s_06` | `ctrl_estops` | `ctrl_heater_cabinet` | signal | mạch an toàn dừng khẩn (cả nút trên sàn thao tác) | 6 |
| `s_07` | `die_bolt_actuator_rail` | `die_junction_box` | signal | cáp bulông nhiệt + cặp nhiệt (phích cắm) | 4 |
| `s_08` | `melt_rupture_disc_2` | `ctrl_heater_cabinet` | signal | tín hiệu đứt đĩa nổ 2 + P4 qua hào | 6 |
| `s_09` | `ctrl_estop_platform` | `ctrl_estops` | signal | nút dừng khẩn sàn thao tác nối vào mạch an toàn theo cột sàn | 5 |
| `s_10` | `ctrl_heater_cabinet` | `ctrl_drive_cabinet` | signal | Profinet + STO nối cứng từ rơ-le an toàn (dừng khẩn, P1 HH, đĩa nổ, khoá liên động truyền động) | 2 |
| `s_11` | `melt_sensor_head` | `ctrl_drive_cabinet` | signal | P1 HH 350 bar → ngắt cứng truyền động chính | 7 |
| `s_12` | `melt_rupture_disc` | `ctrl_drive_cabinet` | signal | tín hiệu đứt đĩa nổ 1 → ngắt truyền động chính | 7 |
| `s_13` | `melt_rupture_disc_2` | `ctrl_drive_cabinet` | signal | tín hiệu đứt đĩa nổ 2 → ngắt truyền động chính và bơm | 7 |
| `s_14` | `lube_pipe_pressure` | `ctrl_machine_cabinet` | signal | công tắc áp dầu (PS) + PT100 dầu hộp số → khoá khởi động truyền động | 4 |
| `s_15` | `drive_coupling_guard` | `ctrl_machine_cabinet` | signal | công tắc liên động vỏ che khớp nối | 4 |
| `s_16` | `drive_safety_coupling` | `ctrl_machine_cabinet` | signal | công tắc giám sát nhả khớp an toàn | 4 |
| `s_17` | `ctrl_machine_cabinet` | `ctrl_heater_cabinet` | signal | I/O tại chỗ (dầu, vỏ che, khớp an toàn) về PLC qua kênh khung đế | 6 |
| `s_18` | `ctrl_estop_die` | `ctrl_heater_cabinet` | signal | nút dừng khẩn khuôn (+Y) vào mạch an toàn qua hộp đấu dây khuôn | 9 |
| `s_19` | `ctrl_estop_melt` | `ctrl_heater_cabinet` | signal | nút dừng khẩn bộ lọc (+Y) vào mạch an toàn qua hộp nhiệt đường chảy | 8 |
| `s_20` | `melt_sensor_p3` | `ctrl_heater_cabinet` | signal | PT-P3 → PIC trong PLC → biến tần bơm nhựa (giữ áp hút ≈ 50 bar bằng tốc độ bơm) | 6 |
| `p_12` | `ctrl_infeed_mv` | `ctrl_drive_cabinet` | power | cáp trung thế 3 kV từ trạm biến áp (≈ 1,8 MVA) | 3 |
| `p_13` | `ctrl_infeed_lv` | `ctrl_heater_cabinet` | power | cáp hạ thế 400 V 3 pha từ tủ phân phối nhà máy (≈ 500 kVA) | 3 |
| `m_01` | `drive_motor` | `screws` | mechanical | trục động cơ → khớp đàn hồi → khớp an toàn → hộp số → then hoa → trục vít | 8 |
| `m_02` | `melt_pump_motor` | `melt_gear_pump` | mechanical | động cơ đứng → hộp góc → các-đăng → trục bơm | 5 |
| `m_03` | `sidefeed_motor` | `sidefeed_barrel` | mechanical | động cơ → hộp số → 2 trục vít | 3 |
| `a_01` | `util_air_drop` | `die_bolt_actuator_rail` | air | khí nén 6 bar → FRL → ống PU → ống gió bulông nhiệt | 7 |
| `a_02` | `util_air_drop_2` | `vac_valve` | air | khí nén → FRL cột sàn → ống Ø12 → bộ tác động van chân không | 7 |
| `a_03` | `util_air_drop_2` | `feed_vacuum_loader` | air | khí nén → FRL cột sàn → ống Ø12 → van lật máy hút liệu | 6 |
<!-- END CONNECTIONS -->

### 6.3 Bảng bích đường chảy

Mọi bích kín kim loại với gờ định tâm, có băng nhiệt hoặc nằm dưới vỏ inox; cảm biến cắm vào lỗ ren 1/2"-20UNF trên đỉnh bích chuyển.

| Mối nối | Ø ngoài bích | Bulông | Lòng chảy |
|---|---|---|---|
| B6 → đầu xi lanh (X 5 746) | Ø640 | 20 bulông cấy M24 trên PCD 560, đai ốc phía B6 | lỗ số 8 → Ø120 |
| Đầu xi lanh → van khởi động (X 5 996) | Ø420 (bích ra đầu xi lanh) | 12 vít M24 lục giác chìm từ phía van, PCD 360, lỗ ren trên bích | Ø120 |
| Van khởi động → bích vào bộ lọc (X 6 446) | Ø420 | 12 vít M24 lục giác chìm từ phía van, PCD 360 | Ø120 |
| Bích vào → bộ lọc (X 6 596) | Ø420 | 8 × M30, PCD 360 (bích Gneuss) | Ø120 |
| Bộ lọc → bích vào bơm (X 7 301) | Ø360 | 8 × M30, PCD 300 | Ø110 |
| Bích vào bơm → bơm (X 7 476) | Ø360 | 8 × M24, PCD 300 | Ø100 |
| Bơm → bích ra (X 7 926) | Ø300 | 8 × M24, PCD 250 | Ø100 |
| Bích ra → ống (X 8 076), ống → bộ trộn (X 8 426), bộ trộn → bích khuôn (X 8 926) | Ø300 | 8 × M24, PCD 250 | Ø100 |
| Bích khuôn → khuôn (X 9 126) | chữ nhật 500 × 360 | 8 × M30 | Ø100 → cửa vào ống phân phối |


## 7. Brainstorm cho các phần không có tài liệu

Các phần dưới đây không có nguồn công khai. Phương án chọn dựa trên cách các dây chuyền thật thường làm; người dựng có thể dựng theo đúng như mô tả.

1. **Hai vùng chân không và cỡ cụm bơm.**
   - Tải ẩm: PET không sấy chứa 0,2–0,4 % ẩm, tức ≈ 7–14 kg/h nước ở 3,5 t/h.
   - Vùng 1 trên B3 (≈ 50 mbar) rút phần lớn hơi nước ngay khi nhựa vừa chảy, nên PET ít bị thuỷ phân và không có cửa hở cho không khí lọt vào. Vùng 2 trên B5 (5–20 mbar) khử nốt ẩm và acetaldehyde.
   - Hai vùng dùng chung một bình tách có ống xoắn làm lạnh (nước 10–15 °C) và một cụm bơm: Roots ≈ 2 000 m³/h trên bơm trục vít khô ≈ 400 m³/h làm mát bằng nước. Van tiết lưu tay quay trên đường vùng 1 giữ chênh lệch áp.
   - Nếu cần dự phòng thì thêm bình tách thứ hai song song; ở đây chỉ dựng một bình.
2. **Khí trơ ở phễu.** Phễu có cổng N₂ nhỏ để giảm oxy hoá PET. Chỉ dựng cổng, không dựng đường ống N₂.
3. **Side feeder** dùng cho mảnh vụn biên tấm nghiền (cắt biên sau cụm cán) hoặc phụ gia bột. Cỡ ZSB 160 là giả định theo tỷ lệ với ZSFE 120 trên ZE 110 (c024). Side feeder đặt trên xe có bánh để kéo ra theo +Y khi bảo trì xi lanh (theo p06).
4. **Van khởi động** kiểu chốt xoay (rotary bolt) hai vị trí, xoay bằng xi lanh thuỷ lực nằm theo Y. Bên dưới có máng inox và xe hứng nhựa có bánh. Van và đầu xi lanh (≈ 1,3 t) tì lên giá đỡ PTFE bắt vào đầu khung đế.
5. **An toàn áp suất:**
   - Đĩa nổ 1 ở đầu xi lanh (phía −Y); đĩa nổ 2 sau bơm bánh răng (350 bar, phía −Y) để bảo vệ ống, bộ trộn, khuôn khi khuôn nghẹt, vì bơm tạo được tới 370 bar (c049).
   - P1 ngắt quá áp đầu xi lanh; P4 ngắt bơm và trục vít ở 330 bar.
   - Vòng điều khiển P3 → tốc độ bơm bánh răng (lưu lượng do cân quyết định).
   - Bảng nguyên nhân → tác động (cause and effect):

     | Nguyên nhân | Tác động |
     |---|---|
     | Nút dừng khẩn bất kỳ (8 vị trí) | STO truyền động chính, dừng bơm nhựa, side feeder, cân; cắt nhiệt không bắt buộc |
     | P1 HH 350 bar hoặc đứt đĩa nổ 1 | ngắt cứng truyền động chính, dừng cân |
     | P4 HH 330 bar hoặc đứt đĩa nổ 2 | dừng bơm nhựa và truyền động chính, dừng cân |
     | Áp dầu hộp số thấp / dầu quá nóng | cấm khởi động; khi đang chạy thì dừng có kiểm soát |
     | Mở vỏ che khớp nối | cấm khởi động / STO |
     | Khớp an toàn nhả | STO truyền động chính, báo lỗi |
   - Khớp an toàn giới hạn mômen trên trục vào hộp số (c033).
6. **Giãn nở nhiệt.**
   - Xi lanh cố định ở lantern (X = 0). Ba gối đỡ dùng tấm trượt nên xi lanh giãn tự do theo +X: 5,75 m thép ở ΔT ≈ 250 K giãn ≈ 17 mm. Đường chảy dài ≈ 3,4 m giãn thêm ≈ 10 mm, tổng ≈ 28 mm tại khuôn.
   - Giá van khởi động, giá bộ lọc và giá bơm có tấm trượt PTFE: tự do theo X ±40 mm, dẫn hướng theo Y; chỉ tấm đế được neo xuống sàn.
   - Xe khuôn có bàn trượt ±40 mm theo X trên xà đỡ, chạy trên một ray phẳng và một ray dẫn hướng.
   - Khe gió 200 mm được chỉnh khi máy đã nóng.
7. **Khoảng giữa khuôn và trục cán.**
   - Với trục Ø800 và mũi khuôn vát 30°, khe gió nhỏ nhất hợp lý là ≈ 200 mm. Khi đó thân khuôn cách mặt trục giữa và trục dưới 39–48 mm; bulông nhiệt nằm dọc mặt vát, đầu nhô tối đa 30 mm, còn khe hở ≈ 20 mm.
   - Muốn khe gió nhỏ hơn thì phải nghiêng khuôn hoặc xoay khung cụm trục (kiểu PlanetCalender, c044). Ở đây giữ khuôn nằm ngang theo DECISIONS 10 và 11.
   - Cụm trục chạy trên ray, lùi được 1 000–1 500 mm theo +X; phải lùi cụm trục trước khi kéo khuôn ra theo +Y. Thanh deckle không vượt X 9 520 để không chạm khung cụm trục.
8. **Xe khuôn.** Khuôn nặng ≈ 3,4 t, trọng tâm cao ≈ 1,15 m trên ray. Đế xe rộng X 8 700–9 380 luồn dưới bộ trộn và bích khuôn, khổ ray 560 mm, khoá sàn ở vị trí làm việc. Hộp đấu dây khuôn đứng trên sàn ngoài ray; cáp khuôn và ống khí có phích/khớp nhanh để tách khi kéo khuôn đi.
9. **Che chắn vùng khe trục:** thực tế có rào chắn và rèm quang (light curtain) quanh khe trục. Phần này thuộc cụm cán, không dựng. Đầu đo chiều dày quét ngang cho điều khiển profin đặt sau cụm trục, cũng không dựng.
10. **Cụm dầu bôi trơn:**
    - Bơm bánh răng ≈ 60 L/ph với động cơ 4 kW đặt đứng.
    - Lọc kép 25 µm.
    - Bộ làm mát tấm ≈ 30 kW nhiệt (≈ 2 % công suất truyền).
    - Bố trí trên khay đế phía +Y trước động cơ, như hình bóng trang 9 và ảnh web-03.
11. **Bên trong khung đế:**
    - Hộp tủ của đoạn gia công chứa bộ điều nhiệt và phân phối nước (c034).
    - Một kênh cáp ngang nối hai phía.
    - Cửa có lưới thông gió.
    - Khi dựng chỉ cần thể hiện cửa, tay nắm, lỗ tròn Ø140.
12. **Tủ điện và lối đi.**
    - Biến tần trung thế 1,5 MW thường đặt trong phòng điện riêng. Ở đây đặt thành dãy tủ phía −Y, mặt cửa ở Y −3 700, để thể hiện đủ bộ phận và vẫn chừa ≥ 1 000 mm trước cửa tủ.
    - Lối đi phía −Y tối thiểu 850 mm; mọi ống đi ngang lối đi ở cao ≥ 2 190 mm; cáp đi trong hào có nắp phẳng sàn.
    - Tủ đầu máy (khối cao cuối máy trên hình bóng) được hiểu là tủ đấu dây tại chỗ của cụm truyền động, sơn xanh KM như ảnh web-06/07.
13. **Khí nén:** hai ống xuống. Một ở khuôn cho làm mát bulông nhiệt (c054). Một ở cột sàn thao tác cho van bướm chân không, van lật máy hút liệu và van nạp các cân.
14. **Gia nhiệt khuôn:** 9 vùng mỗi nửa (bước ≈ 270 mm) cộng 2 tấm đầu, tổng 20 vùng. Hộp đầu nối dài chạy dọc mặt sau khuôn, chừa chỗ giữa cho bích vào. 94 bulông nhiệt có tủ điều khiển riêng.
15. **Màu sắc:**
    - Cụm truyền động màu xanh Flender: lantern, hộp số, cụm dầu, động cơ xanh đậm. Theo máy ZE UT thật năm 2016 (web-01/03, c023) và cụm dẫn động xanh tím trên p16_1.
    - Vỏ che inox xước, khung đế xám trắng.
    - Màu nhấn xanh KM trên tủ đầu máy, tủ điều khiển và khung cụm trục cán.

## 8. Đặc điểm nhận dạng không được bỏ sót

1. **Khung đế dài hai tầng màu xám trắng**, chia hai đoạn tại X = 330. Dầm trên cao 200; hộp tủ dưới lùi vào, có hàng cửa tay nắm lõm và lỗ tròn Ø140 nút vàng.
2. **Sáu vỏ che hộp inox** (C1…C6) từ mặt khung lên Z 1 650, vát 45° hai mép trên.
   - Mỗi vỏ có tay nắm đen trên nắp và trên tấm dưới, cùng tam giác vàng "bề mặt nóng".
   - C1 có tấm tròn 10 bulông ở mặt +Y; hộp dừng khẩn vàng trên tấm dưới của C4 và C1 ở tầm 1,1 m.
3. **Hai vòm chân không:**
   - vòm vùng 2 dạng hộp cao trên C3, 2 kính tròn ở mặt +Y, ống DN150 đi thẳng lên từ nắp qua van bướm, rồi ngang về phía sau ở cao 2,3 m và xuống bình tách đứng;
   - vòm vùng 1 nhỏ hơn trên C6 (B3), 1 kính tròn, ống DN100 ra mặt −Y dựng lên rồi cũng đi cao về bình tách.
4. **Vùng nạp liệu để lộ** (B1, B2), dài 1 690:
   - xi lanh trụ tròn có mặt bích;
   - vỏ nhiệt inox bóng;
   - **vành bích Ø640 ở mỗi mối nối, với vòng 20 bulông cấy và đai ốc** trên đoạn thân tiện thắt (như ảnh web-01/02);
   - gối đúc chữ A màu trắng có lỗ tròn;
   - ống mềm inox từ cụm van uốn lên đầu nối 45° ở góc dưới +Y.
5. **Phễu inox nhỏ có cổng nghiêng 45° về phía hộp số**. Ống rơi nghiêng đi lên tới sàn thao tác, nối với cân qua ống mềm trắng.
6. **Cụm truyền động xanh**, từ trước ra sau:
   - lantern có cửa thăm chữ nhật bo góc;
   - hộp số lớn có tai cẩu và bướu trên đầu ra;
   - vỏ khớp nối màu cam có móc cẩu;
   - **động cơ trung thế rất lớn có hộp làm mát gió–nước trên nóc** (cao 2,6 m), 2 ống nước DN40 ở mặt +Y;
   - cụm dầu xanh trước động cơ: động cơ bơm đứng, 2 bầu lọc, bộ làm mát tấm, ống xanh.
7. **Tủ đầu máy xanh KM có chữ KraussMaffei trắng chạy dọc** và đèn tháp, ở tận đầu dẫn động.
8. **Sàn thao tác** có lan can và tấm chắn chân vàng, cầu thang vàng. Trên sàn là cân cấp liệu, phễu trụ, máy hút liệu và tủ cân.
9. **Side feeder phía +Y**: thân ngang vào hông B2, phễu nhỏ trên đỉnh, hộp số và động cơ trên xe trắng có bánh.
10. **Đường chảy thẳng hàng ở Z = 1 200:**
    - đầu xi lanh côn trên giá đỡ từ đầu khung;
    - van khởi động có máng xả và xe hứng;
    - **bộ lọc Gneuss cao với mũ nghiêng có khe gió và logo đỏ**, hộp nhiệt xám bên dưới tay quay;
    - **bơm hình khối có đĩa bích tròn lớn**, cùng động cơ đứng và các-đăng ở phía sau;
    - ống bọc inox, bộ trộn;
    - cảm biến áp nhô lên trên mỗi bích; 2 đĩa nổ nhỏ phía −Y.
11. **Khuôn chữ T crôm rộng 2,75 m:**
    - hàng 94 bulông nhiệt đen nằm dọc mặt vát trên môi, bắc qua rãnh bản lề hở chạy suốt bề rộng; máng cáp, 33 bulông thanh chắn trên đỉnh;
    - 2 hàng vít thân M30 chìm trên mặt đỉnh và 2 hàng ở mặt đáy;
    - tấm đầu có núm deckle, 4 tai cẩu;
    - hộp nhiệt inox dài ở mặt sau;
    - đặt trên xe đế rộng chạy 2 ray theo Y; tủ đấu dây khuôn đứng riêng phía sau.
12. **Ba trục crôm gương xếp đứng.** Môi khuôn chĩa vào khe giữa trục giữa và trục dưới; tấm đi chữ S qua trục giữa và trục trên. Khung cụm trục có dải xanh KM.
13. **Ống góp nước inox dọc mép +Y với tay van đỏ** và các ống mềm inox uốn lên xi lanh. **Máng cáp mạ kẽm đục lỗ với hộp đấu vuông dọc mép −Y.**

## 9. Giả định chính và điểm chưa giải quyết

Giả định chính (chi tiết hơn ở từng mục):
- **Đường kính xi lanh:** thân xi lanh Ø520 (thắt Ø500 dài 40 sau mỗi bích), bích Ø640; mọi mối nối và hai đầu xi lanh dùng 20 bulông cấy M24 trên PCD 560. Suy từ lỗ số 8 rộng 311 cộng thành dày ≈ 105, và tỷ lệ thân/bích ≈ 0,84 trên trang 9.
- **Hình bóng trang 9 chỉ cho bố cục.** Chỉ dùng tỷ lệ tương đối: vỏ che phủ ≈ 71 % xi lanh, vùng nạp để lộ, khung đế hai tầng, vị trí cụm dầu, khối cao cuối máy. Kích thước tuyệt đối lấy theo dữ liệu KM (D 169, cao trục 1 200).
- **Kích thước hộp số** 1 550 × 1 400 × 1 070 là giả định cho 2 × 35 kNm. Lantern 750 × 900 × 1 010.
- **Động cơ** 1 500 kW (§3.1), làm mát IC81W trong hình bao HC 1 860 của c066 (bản IC01). Động cơ cao hơn hộp số khoảng 0,9 m, khác hình bóng; hình bóng dùng chung cho nhiều cỡ máy.
- **Cách hiểu kích thước bộ lọc Gneuss:** B = dày theo chiều chảy, D = cao tâm nhựa trên đáy thân, E = rộng thân, A = tổng rộng kể cả tay quay. Hãng không ghi rõ.
- **Thân bơm, ống, bộ trộn, khuôn:** kích thước thân bơm, chiều dài ống và bộ trộn, chiều cao và chiều sâu khuôn (500 × 450, ≈ 3,4 t), khe gió 200 đều là giả định.
- **Hai vùng chân không** (≈ 50 mbar và 5–20 mbar) và cỡ cụm bơm là giả định theo thực hành cho PET không sấy.
- **Bố trí phụ trợ:** sàn thao tác, cầu thang, dãy tủ, cụm chân không, HPU, hào cáp, khí nén, nước cho cụm chân không đều do người thiết kế bố trí.

Chưa giải quyết được:
1. **Hãng hộp số và cao độ trục vào.** Chưa có nguồn. Đặt trục vào ở Z = 1 200, đồng trục với mặt phẳng giữa hai trục vít.
2. **Khối cao cuối máy** trên hình bóng không có chú thích. Hiểu là tủ đầu máy đứng sàn. Hình bóng vẽ một khối 430 × 1 380 treo cách sàn ≈ 300 mm; giữ nguyên tủ đứng sàn vì phần truyền động đang được dựng (review-01 M11 không áp dụng).
3. **Chiều dài cụm truyền động** từ đuôi động cơ tới cuối xi lanh là ≈ 10 720 mm, dài hơn ≈ 7 % so với ≈ 10 000 mm suy từ bảng KM (c007). Phần dư do khớp đàn hồi và khớp an toàn tách rời (650 mm) và lantern 750 mm. Giữ nguyên vì phần truyền động đang được dựng (review-01 M2 không áp dụng).
4. **Cỡ cụm chân không** cho PET không sấy 3,5 t/h chưa có nguồn đáng tin; c062 có độ tin cậy thấp.
5. **Khe gió 200 mm** lớn hơn mức hay dùng cho PET (50–150 mm). Đã chấp nhận theo DECISIONS 11; muốn nhỏ hơn thì phải nghiêng khuôn hoặc xoay khung trục.
6. **Kết cấu trong khuôn.** Thân khuôn sâu 450 mm (X 9 126–9 576) quá chật để chứa ống phân phối Ø72, thanh chắn, preland và 4 hàng vít thân với mép thép đủ dày. Vị trí vít thân đã chốt để dựng; ống phân phối (G, của drafter) phải đi giữa và trước các hàng vít. Cách sửa triệt để là làm khuôn sâu hơn về phía sau (≈ X 9 060), nhưng việc đó dời bích khuôn và hộp nhiệt nên chưa làm vì khuôn đang được dựng.

## 10. Thay đổi sau review-01

Các thay đổi dưới đây theo `design/review-01.md` và quyết định của orchestrator. Hộp bao của truyền động, động cơ, hộp số, lantern, khớp nối, cụm dầu, khung đế và tủ đầu máy giữ nguyên.

- **C1 (vị trí chi tiết lặp lại):**
  - Mọi mục có `count` > 1 nay có `positions_mm` + `item_mm`. Gồm cặp nhiệt (B1 cắm nghiêng góc trên −Y, ngoài hộp miệng nạp), cảm biến P1/T1 và P5/T5, 94 bulông nhiệt (có `item_axis`, dọc mặt vát), 33 bulông thanh chắn, 4 tai cẩu (2 trên mỗi tấm đầu), deckle, gối ống, động cơ và ray cụm trục cán.
  - Băng nhiệt đường chảy còn 6 băng lộ ra; 7 băng trên ống và bộ trộn nằm dưới vỏ inox, mỗi đoạn có một hộp đấu.
  - Bó ống mềm và ống luồn có `paths_mm`, mỗi ống một đường.
  - `check_parts.py` nay báo lỗi khi mục lặp lại thiếu vị trí, khi ống thiếu đường đi, hoặc khi số đường ít hơn `count`.
- **I1 (đầu nối nước):** đầu nối nước của B2…B6 dời ra góc dưới +Y (45°) tại đầu đoạn + 200 và cuối đoạn − 200, qua rãnh 50 mm của băng nhiệt. B1 ở đáy X 200/476. 12 ống mềm có đường đi riêng; không ống nào đi dưới gối đỡ.
- **I2 (lối đi phía −Y):**
  - Mép sau sàn thao tác ra Y −2 700, cột sau ở Y −2 600; cầu thang dời ra Y −2 650 … −1 950.
  - Dãy tủ lùi ra, mặt cửa ở Y −3 700. Cụm chân không ra Y −3 300 … −2 200, bình tách ở Y −2 700, cột đỡ ống ở Y −1 900; HPU ra Y −2 700 … −2 000.
  - Cáp trung thế và cáp tới tủ đi trong hào có nắp phẳng sàn rộng 400. Sàn nhà mở rộng tới Y −5 500.
- **I3 (xe khuôn):** đế xe rộng X 8 700–9 380 luồn dưới bộ trộn, ray tại X 8 760 và 9 320 (khổ 560). Giá bơm rút ngắn tới X 8 650, gối bộ trộn dời về X 8 560. Hộp đấu dây khuôn rời khỏi xe. Khối lượng khuôn ghi lại ≈ 3,4 t.
- **I4 (khử khí PET không sấy):** bỏ ống thoát khí khí quyển trên B3, thay bằng vòm chân không vùng 1 (≈ 50 mbar). Thêm van DN100, ống xếp, ống DN100 đi cao, van tiết lưu, đồng hồ; lỗ B3 nới thành 320 × 280; lỗ khoét C6 420 × 380; thêm mối nối `v_05`.
- **I5 (an toàn sau bơm):** thêm đĩa nổ 2 (350 bar) trên bích ra bơm và tín hiệu `s_08`; P4 ngắt ở 330 bar.
- **I6 (cấp nhiệt):** thêm hộp nhiệt đường chảy dưới tay quay bộ lọc, 7 ống luồn tới các vùng nhiệt và mối nối `p_10`. Hộp đấu dây khuôn thành tủ đứng 600 × 300 × 1 000 trên sàn, bó cáp cắm rút. Thêm tủ điều khiển bulông nhiệt và mối nối `p_11`.
- **I7 (nước cho phụ trợ):** thêm ống nước cho áo hộp miệng nạp, áo side feeder, bình tách và skid chân không; mối nối `w_06…w_09`. HPU làm mát bằng gió.
- **I8 (giãn nở và đỡ đầu ra):** thêm giá đỡ van khởi động từ đầu khung đế. Giá bộ lọc, giá bơm và xe khuôn có tấm trượt ±40 mm theo X. Khe gió chỉnh khi nóng; tổng giãn nở ≈ 28 mm.
- **M1 (bulông đầu xi lanh):** B1/lantern và B6/đầu xi lanh dùng 20 bulông cấy M24 trên PCD 560. Phía van khởi động dùng vít M24 lục giác chìm bắt từ phía van vào lỗ ren, không còn đai ốc sau bích Ø420.
- **M3 (dừng khẩn):** hộp dừng khẩn nâng lên tầm 1,05–1,19 m: trên tấm dưới vỏ C4, C1 và một cột gá ở X 600. Thêm nút trên lan can sàn thao tác (`ctrl_estop_platform`, `s_09`).
- **M4 (độ cao ống chân không):** ống vùng 2 ra từ nắp vòm, đi ngang ở tâm Z 2 300 (đáy 2 216); cột đỡ và van điều chỉnh dời theo; van điều chỉnh/xả đặt trên ống ra của bình tách, cao 1,7 m.
- **M5 (xả ngưng):** thay bình hứng bằng nồi xả kiểu khoá Ø300 với 3 van; chân bình tách nâng 150 mm.
- **M6 (va chạm nhỏ):** thanh deckle không vượt X 9 520. Ống khí xuống khuôn dời ra X 9 360, Y −1 705, cách xa ống luồn cáp nhiệt.
- **M7 (đường tấm):** tấm đi chữ S: ôm nửa +X trục giữa rồi nửa −X trục trên, ra +X ở Z 2 804 (`path_mm`). Ghi chú đầu đo chiều dày quét ngang (không dựng).
- **M8 (cách cân):** thêm 3 ống mềm trắng dài 150 ở cửa xả các cân; ống cứng bắt đầu ở Z 2 850, vành lỗ sàn không chạm ống.
- **M9 (làm mát động cơ):** động cơ ghi là IC81W, bộ làm mát gió–nước trên nóc trong cùng hình bao (khớp DECISIONS 11.3). Thêm 2 ống DN40 từ ống nhà máy (`util_cw_motor_hoses`, `w_10`).
- **M10 (khí nén):** thêm ống khí xuống cột sàn, bộ lọc–điều áp và 2 ống Ø12 tới van chân không và máy hút liệu (`a_02`, `a_03`).
- **Không áp dụng:**
  - **M2** (rút ngắn cụm truyền động) và **M11** (đổi tủ đầu máy thành tủ treo): phần truyền động và tủ đầu máy đang được dựng theo vị trí hiện tại. Ghi vào §9 mục 2 và 3.
  - Cáp trung thế được đổi tuyến trong phạm vi I2 cho phép (hào cáp mới và đoạn dựng lên), không động tới hộp đấu dây động cơ.

### 10.1 Thay đổi sau ghi chú của drafter (`drawings/design_issues.md`)

- **#1 bulông thanh chắn:** hàng 33 bulông dời tới X 9 255, đặt đứng ngay trên thanh chắn (X 9 240–9 270) như khuôn môi mềm thông thường. Máng bulông nhiệt thu hẹp còn X 9 285–9 345 (60 × 90) trên dải trước của mặt đỉnh.
- **#2 dầm sàn thao tác:** thêm `beams_mm` và mô tả. Dầm chính X −450 ngắt tại Y ±260 quanh lỗ ống rơi chính; hai dầm viền theo X (X −760 … −140) tựa lên hai dầm phụ IPE160 tại X −760 và −140; thêm dầm biên và dầm phụ đỡ lưới. Hộp bao sàn không đổi.
- **#3 khung cụm cán:** mép trước khung bên lõm tới X 9 800 trong dải Z 1 060–1 340 quanh khe trục (outline XZ). Khe hở tới núm deckle ≈ 300 mm. Hộp bao không đổi.
- **#7 cặp nhiệt B1:** thêm `item_axes`. B1 nghiêng 40° so với phương đứng về −Y, chân tại (338, −167, 1 399), đầu dưới đáy hộp miệng nạp. `item_mm` của chi tiết có trục nay là [Ø, Ø, dài] theo hệ trục riêng (áp dụng cả cho bulông nhiệt); `check_parts.py` tính hộp bao từng cái theo trục.
- **#8 thân side feeder:** thêm `outline_mm` mặt XZ (hai cung R130 tâm X 1 315 và 1 385, đùn theo Y 330–1 100).
- **#4, #5, #6** (kết cấu trong khuôn, bảng bích đường chảy, bảng phần tử trục vít): chưa bổ sung vào dữ liệu; bản vẽ đang thể hiện phương án của drafter, đánh dấu G.

### 10.2 Thay đổi sau drawing review-01 (`drawings/review-01.md`, phần dữ liệu)

- **I2 khoá liên động:**
  - thêm tín hiệu `s_10` (tủ điều khiển ↔ tủ biến tần: Profinet + STO nối cứng), `s_11` (P1 HH → tủ biến tần), `s_12`/`s_13` (đứt đĩa nổ 1/2 → tủ biến tần), `s_14` (công tắc áp dầu + PT100), `s_15` (liên động vỏ che), `s_16` (công tắc khớp an toàn), `s_17` (tủ đầu máy → PLC);
  - nguồn cấp vào: hào `ctrl_infeed_mv` + `p_12` (3 kV), hào `ctrl_infeed_lv` + `p_13` (400 V);
  - 2 nút dừng khẩn mới: `ctrl_estop_die` (trên tay đòn xe khuôn phía +Y, tâm (9 250, 1 450, 1 100), `s_18`) và `ctrl_estop_melt` (cột trên giá bộ lọc phía +Y, tâm (7 320, 650, 1 100), `s_19`); thêm bảng nguyên nhân → tác động ở §7.
- **I3:** P3 điều khiển tốc độ bơm bánh răng, lưu lượng do cân quyết định; thêm `s_20`; sửa chức năng của `melt_sensor_p3`, `melt_pump_adapter_in` và §1, §7.
- **I4:** thêm `die_body_bolts`, 94 vít M30 10.9 chìm.
  - Mặt đỉnh: hàng X 9 160 (24 vít) và 9 210 (23 vít), sau bulông thanh chắn và máng bulông nhiệt.
  - Mặt đáy: hàng X 9 160 (23 vít) và 9 270 (24 vít), tức cách mép trước mặt đáy 170 và 60.
  - Bước 110, các hàng lệch nhau 55 mm theo Y.
  - Không dùng X 9 270 ở mặt đỉnh vì trùng hàng bulông thanh chắn.
- **I5:** rãnh bản lề hở suốt bề rộng tại X 9 392–9 404, gân 12 mm, có trong outline `die_body_upper`. `die_flex_lip` nay là phần sau rãnh (X 9 404–9 576, hộp bao đổi); đầu bulông nhiệt tì cách gân 36 mm.
- **I6:** bích xi lanh và bích đầu xi lanh từ Ø600 lên Ø640, giữ PCD 560 và 20 × M24 (mép lỗ cách mép bích 27 mm).
  - Thân thắt Ø500 dài 40 sau mỗi bích cho khẩu vặn đai ốc: khe 12 mm.
  - Lỗ C6 và tấm đầu C1 Ø660.
  - Đã kiểm khe hở: vỏ nhiệt bắt đầu ngay sau đoạn thắt; gối đỡ ở giữa đoạn; vòm chân không và hộp miệng nạp không chạm bích.
- **Phụ:**
  - M1: ống chân không sau bình tách lên DN150.
  - M2: van an toàn + lọc hút ở bơm dầu, van bi trên ống nước bộ làm mát dầu, công tắc áp dầu.
  - M3: môi dưới là thanh chèn bắt vít.
  - M8: bảng phần tử trục vít theo X trong `screws.details`; nút nhựa KB 90° kết thúc ở X 1 950, trước lỗ vùng 1.
  - Thêm bảng bích đường chảy (§6.3) và ghi bích vào kiểu mối nối `melt_03`, `melt_05`…`melt_07`.
- **Còn lại** (C1, C2, I1, I7–I10, M4–M7) là việc của bản vẽ.
