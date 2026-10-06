# Kiểm nguồn nhóm drive

Người kiểm: lead (Opus, làm tại chỗ). Hạn mức Sonnet hết giữa chừng nên người dùng chọn để lead tự kiểm; lead không gắn nhóm này. Ngày 2026-10-06.
Tổng: 42 dòng, 86 fact (✓ 26, ≈ 14, ⚠ 46 sau khi kiểm). Hạ mức (cả lượt kiểm trước nếu có): 0. Nâng mức: 0. Sửa chữ hoặc tách fact: 1.

Hình đã mở: web-03 (cả vùng cổng F2–F4 cắt phóng), web-11, web-12, crop trang 5 (khớp an toàn), crop trang 19 (hộp số, khớp, motor bơm dầu), trang 9 (bản có chú thích). Chữ catalogue: "branching system in the gear unit" và "a safety coupling instantaneously separates" (trang 6), "co-rotating" (trang 11), "the gearbox and the multi-spline shafts" (trang 18). Claim đã đọc: c001–c006, c017, c033, c034, c064–c066. Các phép tính đã làm lại: 1 490/400 = 3,725; 1 200 − 450 = 750; 750 + 1 860 = 2 610; 75 + 1 750 + 200 = 2 025; 1 200 − 450 − 650 = 100; (169 + 114,6)/2 = 141,8, a/2 ≈ 71; tỷ lệ cửa lantern 7,62/15,26 = 0,50 và 4,95/19,68 = 0,25 (meas §2.2), tâm cửa 457,55 / 478,73 pt so với tâm lantern 457,56 và trục 478,79. Số trong bản tiếng Nhật khớp bản tiếng Việt (kiểm bằng máy).

## Thay đổi

| Khoá | Thiết bị | Fact | Trước → sau | Lý do |
|---|---|---|---|---|
| ed33b46fb0ab | lube_unit_frame | 2 (mới) | thêm ⚠ | dòng ghi "tấm thấm dầu như web-03" nhưng ảnh là ống thấm dạng xúc xích; dòng hạ từ ✓ xuống ⚠ |

## Bằng chứng từng dòng

### 4e7ee2eff0d2 – drive_coupling_guard:function
> Che phần quay giữa động cơ và hộp số, có khoá liên động.
- ≈ "Vỏ che khớp nối là khối giữa hộp số và motor trên hình bóng ZE 155 UT (trang 9), có móc …": trang 9: khối 12,84 × 19,16 pt giữa hộp số và motor, có móc trên nóc; tên "vỏ khớp nối" là nhận diện của pdf_measures: ≈ đúng.
- ⚠ "Vỏ che có khoá liên động (interlock)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d18eb2ae3e54 – drive_coupling_guard:details[0]
> Tôn 3 mm, tấm hông +Y tháo được có ô lưới quan sát, móc cẩu trên nóc.
- ≈ "Móc cẩu trên nóc vỏ che khớp nối, đọc trên hình bóng ZE 155 UT (trang 9)": như trên (móc cẩu trên nóc khối vỏ khớp nối, trang 9).
- ⚠ "Tôn 3 mm; tấm hông +Y tháo được có ô lưới quan sát": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 99b9767401df – drive_coupling_guard:details[1]
> Công tắc liên động (interlock) cấm chạy khi mở nắp.
- ⚠ "Công tắc liên động (interlock) cấm chạy khi mở nắp": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 342c454985d7 – drive_encoder:function
> Đo tốc độ / vị trí trục động cơ cho biến tần điều khiển vector.
- ⚠ "Encoder đo tốc độ / vị trí trục motor cho biến tần điều khiển vector (vòng kín)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### bffa8b5c224c – drive_encoder:details[0]
> Vỏ Ø160 × 100, đầu cáp tín hiệu.
- ⚠ "Vỏ Ø160 × 100 có đầu cáp tín hiệu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b017d60be888 – drive_flex_coupling:function
> Bù lệch tâm giữa trục động cơ và trục vào hộp số, giảm va đập.
- ⚠ "Khớp đàn hồi bù lệch tâm và giảm va đập giữa trục motor và trục vào hộp số": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 791448ce5e9d – drive_flex_coupling:details[0]
> Hai moay-ơ thép + bộ đĩa lò xo, Ø560.
- ⚠ "Hai moay-ơ thép + bộ đĩa lò xo, Ø560: khớp đĩa/đàn hồi tiêu chuẩn cỡ ≈ 10 kNm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a2ab8e1d15a3 – drive_motor:function
> Động cơ cảm ứng trung thế 4 cực, chạy biến tần, quay trục vít qua khớp nối và hộp số; bộ làm mát gió–nước trên nóc thải nhiệt vào nước, không thổi gió nóng vào xưởng.
- ≈ "Động cơ cảm ứng 4 cực trung thế (3 kV), họ ABB AMI, khung 450L4A": c064 claim (medium) "AMI 500L4A (4-pole, 3 kV, 50 Hz)"; c065 quote "AMI 450L4A … 1489": 4 cực từ mã L4 và tốc độ 1 489; 3 kV suy theo cùng họ: ≈ đúng.
- ⚠ "Chạy biến tần (điều khiển tốc độ vít tới 400 v/ph)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ✓ "Motor quay trục vít qua khớp nối an toàn rồi hộp số": crop trang 5: khớp đĩa bạc nằm giữa motor (có gân) và hộp số; c033 quote "a safety coupling instantaneously separates the drive from the extruder": khớp.
- ⚠ "Bộ làm mát gió–nước trên nóc (IC81W) thải nhiệt vào nước, không thổi gió nóng vào xưởng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 8b1527f516b8 – drive_motor:details[0]
> Thân hộp có gân Z 750–1 680; trên nóc là hộp bộ làm mát gió–nước (IC81W top air-to-water cooler) Z 1 680–2 610, X −4 800 … −3 300: vỏ hộp kín, 2 nắp thăm ống trao đổi nhiệt ở đầu −X, không có cửa gió hở.
- ⚠ "Thân Z 750–1 680; hộp làm mát Z 1 680–2 610 (đỉnh = 750 + HC 1 860), X −4 800 … −3 300": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Hộp làm mát kín, 2 nắp thăm ống trao đổi nhiệt ở đầu −X, không cửa gió hở; thân hộp có gân": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e3a8ec1d4957 – drive_motor:details[1]
> Hai bích nước DN40 trên mặt +Y của hộp làm mát: vào tại X −3 500, Z 2 300; ra tại X −3 700, Z 2 400; cảm biến rò nước ở đáy hộp.
- ⚠ "Hai bích nước DN40 trên mặt +Y: vào X −3 500, Z 2 300; ra X −3 700, Z 2 400; cảm biến rò…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 40a9bab71fd4 – drive_motor:details[2]
> Đầu trục Ø140 dài 200 ở phía hộp số; nắp ổ NDE nhô 75 mm mang encoder.
- ⚠ "Đầu trục Ø140 dài 200 ở phía hộp số; nắp ổ NDE nhô 75 mm mang encoder": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 13c980231bbc – drive_motor:details[3]
> 4 tai cẩu, biển tên, cọc tiếp địa; tâm trục Z = 1 200 (H 450 trên mặt đế Z 750).
- ✓ "H = 450 mm (cùng hàng L = 2 025 mm): chiều cao tâm trục của ABB AMI 450L": c066 (medium) quote hàng "450L ≥ 4 … 450 42 2025 …", claim "shaft height H 450, overall length L 2025": khớp.
- ✓ "Tâm trục Z = 1 200: chiều cao tâm trục ZE 155 A UTi theo bảng KM (A = 1 200)": c006 quote "1.200" (Achshöhe A): khớp.
- ≈ "Mặt đế Z 750 = 1 200 − 450": tính lại 1 200 − 450 = 750 ✓.
- ⚠ "4 tai cẩu, biển tên, cọc tiếp địa": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7ded4e4e6484 – drive_motor_base:function
> Nâng động cơ để tâm trục khớp Z = 1 200, cho phép căn chỉnh đồng tâm.
- ✓ "Tâm trục khớp Z = 1 200 theo chiều cao tâm trục ZE 155 A UTi trong bảng KM": c006 quote "1.200": khớp.
- ⚠ "Đế nâng motor 100 mm lên mặt Z 750 trên đỉnh khung 650, cho phép căn chỉnh đồng tâm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 8e112926859e – drive_motor_base:details[0]
> Hai ray thép dày 100 có vít đẩy (jack screws) căn chỉnh ngang.
- ⚠ "Hai ray thép dày 100 = 1 200 − 450 − 650": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Vít đẩy (jack screws) căn chỉnh ngang": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e3c524effa27 – drive_motor_terminal_box:function
> Đấu cáp trung thế từ biến tần vào động cơ.
- ⚠ "Hộp đấu dây riêng ở mặt −Y nhận cáp trung thế từ biến tần": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1ef6608ddd0c – drive_motor_terminal_box:details[0]
> Hộp thép 600 × 350 × 500, nắp 12 vít, ốc siết cáp ở đáy.
- ⚠ "Hộp thép 600 × 350 × 500, nắp 12 vít, ốc siết cáp ở đáy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 96c8c6cc3498 – drive_safety_coupling:function
> Tách động cơ khỏi hộp số khi quá tải (vít kẹt, vật lạ) để bảo vệ trục vít và hộp số.
- ✓ "Khớp an toàn nằm giữa motor và hộp số, tách ngay truyền động khỏi máy đùn khi quá tải": c033 quote "a safety coupling instantaneously separates the drive from the extruder"; crop trang 5 và 19: khớp nằm giữa motor và hộp số: khớp.
- ⚠ "Nguyên nhân quá tải là vít kẹt hoặc vật lạ; khớp bảo vệ trục vít và hộp số": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 050d1d30b14e – drive_safety_coupling:details[0]
> Đĩa thép bạc Ø640 có rãnh vòng (như ảnh p19), vòng bulông 12 lỗ, công tắc giám sát nhả khớp.
- ✓ "Khớp an toàn là đĩa bạc có rãnh vòng và vòng bulông (ảnh catalogue trang 5 và 19)": crop trang 5 và 19: khớp đĩa bạc có các rãnh vòng và vòng bulông: thấy rõ (máy nhỏ, chỉ dùng cho dạng).
- ⚠ "Ø640; vòng bulông 12 lỗ": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Công tắc giám sát nhả khớp": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 657dbc19a725 – gearbox:function
> Giảm tốc từ động cơ (≈ 1 490 v/ph) xuống tối đa 400 v/ph và chia mômen 2 × 35 kNm ra hai trục vít đồng hướng.
- ✓ "Hộp số chia công suất (power branching) chia mômen ra hai trục vít đồng hướng": c033 claim (high) "power branching"; chữ catalogue trang 6 "branching system in the gear unit"; trang 11 nguyên lý trục vít đôi đồng hướng: khớp.
- ✓ "2 × 35 kNm (= 2 × 35 000 Nm): mômen mỗi trục vít ZE 155 A UTi theo bảng KM": c005 quote "2x 35.000": khớp.
- ✓ "400 v/ph: tốc độ vít tối đa ZE 155 A UTi theo bảng KM": c003 quote "400": khớp.
- ≈ "≈ 1 490 v/ph: tốc độ định mức motor 4 cực họ AMI (1 489 ở 450L4A, 1 490 ở 500L4A)": c065 quote "1489", c064 quote "1490": khớp; motor 1 500 kW không có hàng riêng, ghi rõ trong lý do.

### 589a08335ace – gearbox:details[0]
> Vỏ gang hộp có gân, phần bướu trên cao Z 1 720 bao 2 trục ra ở đầu X −1 250 … −750.
- ✓ "2 trục ra: máy trục vít đôi, mômen ghi 2 × 35 000 Nm (mỗi trục vít một trục)": c005 quote "2x 35.000": khớp; web-11 cũng có 2 trục ra then hoa.
- ⚠ "Vỏ gang hộp có gân; phần bướu cao Z 1 720 bao 2 trục ra ở đầu X −1 250 … −750": đã xem web-11: phần nhô cao ở đầu xa hai trục ra (đầu vào), trái với bướu ở đầu ra của thiết kế; lý do ghi đúng.

### 61e322d81d0f – gearbox:details[1]
> Nắp ổ trục vào tròn Ø500 nhô 50 mm ở đầu X = −2 300 quanh Z = 1 200.
- ✓ "Z = 1 200: chiều cao tâm trục ZE 155 A UTi theo bảng KM": c006 quote "1.200": khớp.
- ⚠ "Nắp ổ trục vào tròn Ø500 nhô 50 mm ở đầu X = −2 300": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 90e917b97eeb – gearbox:details[2]
> 4 tai cẩu (lifting eyes) trên nóc, nắp thăm chữ nhật trên nóc, ống thở (breather), kính thăm mức dầu phía +Y, nút xả dầu ở đáy.
- ✓ "Hộp số ZE có tai cẩu trên nóc (ảnh catalogue trang 19, ZE Basic)": crop trang 19 và img-p19_3: hai tai cẩu tròn trên nóc hộp số: thấy rõ.
- ≈ "Nắp thăm chữ nhật bắt vít trên nóc hộp số": web-11 (Eisenbeiss, hãng khác): nắp thăm chữ nhật bắt vít trên nóc: thấy rõ; ≈ đúng.
- ⚠ "4 tai cẩu; ống thở (breather), kính thăm mức dầu phía +Y, nút xả dầu ở đáy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 444bc64ef099 – gearbox:details[3]
> Biển tên, tem cảnh báo vàng; cảm biến nhiệt dầu PT100 cạnh cổng dầu.
- ✓ "Tem cảnh báo vàng hình tam giác trên vỏ hộp số": web-03 (ZE 110 R, đã xem cả cắt phóng): tem cảnh báo tam giác vàng trên vỏ hộp số xanh (mép trái ảnh): thấy rõ.
- ⚠ "Biển tên; cảm biến nhiệt dầu PT100 cạnh cổng dầu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b8b69657e571 – gearbox:details[4]
> Tỷ số truyền ≈ 3,73 (1 490/400).
- ≈ "Tỷ số ≈ 3,73 = 1 490 / 400 = 3,725": tính lại 1 490 / 400 = 3,725 ✓; đầu vào từ c065/c064 và c003.
- ⚠ "Chọn tỷ số để tốc độ định mức motor ứng với tốc độ vít tối đa": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 268f691e497c – lantern:function
> Nối mặt bích ra hộp số với xi lanh B1; chứa khớp then hoa nối trục ra hộp số với trục vít; có cửa thăm.
- ≈ "Lantern là khoang nối giữa hộp số và xi lanh, có cửa thăm chữ nhật bo góc, trên hình bón…": trang 9: khối có cửa thăm chữ nhật bo góc giữa hộp số và xi lanh; nhận diện "lantern" của pdf_measures: ≈ đúng.
- ✓ "Mômen tới trục vít qua trục then hoa (ZE Basic: "multi-spline shafts"; ZE 180 A UT, a = …": chữ catalogue trang 18 "the gearbox and the multi-spline shafts"; c017 claim (high) "spline shaft 24 teeth": khớp.
- ⚠ "Khớp then hoa đặt trong lantern, nối trục ra hộp số với trục vít": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b479684fb571 – lantern:details[0]
> Cửa thăm chữ nhật bo góc 380 × 250 trên mặt +Y, tâm X = −375, Z = 1 200, 8 vít + tay nắm.
- ≈ "Cửa thăm 380 × 250 = 0,51 × 0,25 cỡ lantern (750 × 1 010); hình bóng cho 7,62/15,26 = 0,…": meas §2.2: cửa 453,74–461,36 × 476,25–481,20 (7,62 × 4,95 pt), lantern 15,26 × 19,68 pt; 0,50 và 0,25 ✓; chỉ dùng tỷ lệ tương đối, đúng luật trang 9.
- ≈ "Tâm cửa X = −375 (giữa lantern −750 … 0) và Z = 1 200 (ngang tâm trục vít)": tâm cửa (457,55; 478,73) trùng tâm lantern 457,56 và trục 478,79 (meas): ✓; Z 1 200 từ c006.
- ⚠ "8 vít + tay nắm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 3dd99305cfdb – lantern:details[1]
> Vành mặt bích Ø700 dày 60 ở đầu X = 0: 20 lỗ ren M24 trên PCD 560 nhận bulông cấy từ bích B1 (đai ốc 12 cạnh nằm phía B1).
- ⚠ "20 lỗ ren M24 trên PCD 560 nhận 20 bulông cấy từ B1; đai ốc 12 cạnh nằm phía B1": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Vành bích Ø700 dày 60 ở đầu X = 0 (mối nối barrel/lantern, gốc toạ độ của thiết kế)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7f1755080ec3 – lantern:details[2]
> Ống xả dầu rò rỉ ở đáy, tai cẩu trên nóc.
- ⚠ "Ống xả dầu rò rỉ ở đáy, tai cẩu trên nóc": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c09ecacae4f9 – lantern:details[3]
> Trong: 2 khớp then hoa (spline coupling) tại Y = ±71.
- ≈ "2 khớp tại Y = ±71: mỗi trục vít một khớp; a ≈ 142 = (D + d)/2 = (169 + 114,6)/2, Y = a/2": tính lại d = 169 − 2 × 27,2 = 114,6; a = (169 + 114,6)/2 = 141,8; a/2 ≈ 71 ✓ (c001, c002).
- ✓ "Trục ra hộp số nối với trục vít bằng then hoa (ZE 180 A UT, a = 163 mm: trục then hoa 24…": như 268f691e497c (c017, trang 18).
- ⚠ "Hai khớp then hoa nằm bên trong lantern": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e43931fbad30 – lube_filter_duplex:function
> Lọc dầu, đổi bầu lọc khi máy chạy.
- ✓ "Cụm dầu của máy ZE có lọc dầu hai bầu kèm tay gạt chuyển đổi": web-03 (ZE 110 R, đã xem cả cắt phóng): hai bầu lọc xanh dưới một đầu lọc, tay gạt chuyển đổi: thấy rõ.
- ⚠ "Đổi bầu lọc khi máy chạy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e1289ac2a4b6 – lube_filter_duplex:details[0]
> 2 bầu lọc đứng Ø110, tay gạt chuyển đổi, chỉ báo chênh áp, đồng hồ áp.
- ✓ "Lọc có tay gạt chuyển đổi và đồng hồ áp ở đầu lọc (ảnh máy ZE 110 R)": web-03 (ZE 110 R, đã xem cả cắt phóng): tay gạt trên đầu lọc và đồng hồ áp: thấy rõ.
- ≈ "2 bầu lọc đứng; chỉ báo tròn có đầu nối điện trên đầu lọc, đọc là chỉ báo chênh áp": web-03 (ZE 110 R, đã xem cả cắt phóng): đếm được 2 bầu; chỉ báo tròn có cáp trên đầu lọc: thấy; gọi là chỉ báo chênh áp là cách đọc: ≈ đúng.
- ⚠ "Bầu lọc cỡ Ø110": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6c6409c43802 – lube_oil_cooler:function
> Giải nhiệt dầu hộp số bằng nước làm mát.
- ✓ "Cụm dầu của máy ZE có bộ trao đổi nhiệt dạng tấm inox, các cổng F2–F4 nối ống thép và ốn…": web-03 (ZE 110 R, đã xem cả cắt phóng): khối tấm inox, F2 và F4 nối ống thép xanh, F3 nối ống mềm đen: khớp.
- ⚠ "Môi chất làm mát là nước": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f18ab3460bf9 – lube_oil_cooler:details[0]
> Khối tấm hàn inox 350 × 250 × 350, 4 cổng ren F1–F4 trên mặt +Y.
- ✓ "Bộ trao đổi nhiệt dạng khối tấm inox (plate heat exchanger) có cổng ghi nhãn F2, F3, F4": web-03 (ZE 110 R, đã xem cả cắt phóng): nhãn F2, F3, F4 trên khối tấm inox: thấy rõ.
- ≈ "4 cổng F1–F4: thấy F2, F3, F4 trên ảnh; F1 ở mặt khuất": web-03 (ZE 110 R, đã xem cả cắt phóng): thấy F2, F3, F4, F1 khuất: ≈ đúng.
- ⚠ "Cỡ 350 × 250 × 350; 4 cổng ren trên mặt +Y": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 0fd30a110e25 – lube_pipe_pressure:function
> Dẫn dầu đã lọc, làm mát tới hệ phun trong hộp số.
- ✓ "Hộp số ZE được bôi trơn kết hợp ngâm dầu và dầu áp lực": c033 quote "A combined dip and pressure lubrication system protects the bearings and gears": khớp.
- ⚠ "Dầu đã lọc, làm mát đi tới hệ phun trong hộp số theo tuyến ống do thiết kế vẽ": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 251c33292e66 – lube_pipe_pressure:details[0]
> Ống thép DN32 (OD 42) sơn xanh; công tắc áp suất (PS, khoá khởi động truyền động) gần cổng vào hộp số, tín hiệu về tủ đầu máy (s_14).
- ✓ "Ống dầu thép sơn xanh cùng màu hộp số": web-03 (ZE 110 R, đã xem cả cắt phóng): ống dầu thép sơn xanh cùng màu hộp số: thấy rõ.
- ⚠ "Ống DN32 (OD 42)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Công tắc áp suất (PS) gần cổng vào hộp số khoá khởi động truyền động; tín hiệu về tủ đầu…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### bf5b703ad445 – lube_pipe_return:function
> Dẫn dầu từ carter hộp số về bơm.
- ⚠ "Ống hút dầu từ đáy carter hộp số về bơm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 36796d9dbd33 – lube_pipe_return:details[0]
> Ống thép DN40 (OD 50) chạy dọc mép +Y của khung, Z = 760.
- ⚠ "Ống thép DN40 (OD 50) chạy dọc mép +Y của khung, Z = 760": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5a105513f9aa – lube_pump_motor:function
> Hút dầu từ carter hộp số và đẩy qua lọc, bộ làm mát tới vòi phun bánh răng/ổ trục.
- ✓ "Hộp số ZE bôi trơn bằng dầu áp lực để bảo vệ ổ trục và bánh răng; cụm dầu có bơm, lọc và…": c033 quote như trên; web-03 (ZE 110 R, đã xem cả cắt phóng): bơm, lọc, bộ làm mát: thấy rõ.
- ⚠ "Thứ tự hút carter → bơm → lọc → làm mát → vòi phun bánh răng/ổ trục": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 84595cfc133a – lube_pump_motor:details[0]
> Động cơ 4 kW đặt đứng Ø260 có nắp quạt, chuông nối, bơm bánh răng ở đáy; 2 đồng hồ áp.
- ✓ "Motor đặt đứng có nắp quạt, chuông nối xuống bơm ở đáy, kèm đồng hồ áp, trong cụm dầu củ…": web-03 (ZE 110 R, đã xem cả cắt phóng): motor đứng có nắp quạt, chuông nối xuống bơm ở đáy, đồng hồ áp; img-p19_3 có motor bơm dầu đứng: thấy rõ.
- ≈ "2 đồng hồ áp, đếm trên web-03": web-03 (ZE 110 R, đã xem cả cắt phóng): đếm được 2 đồng hồ áp (đầu lọc và cạnh motor): ✓.
- ⚠ "Motor 4 kW Ø260; bơm kiểu bánh răng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### dec23ec96c6b – lube_pump_motor:details[1]
> Van an toàn (relief valve) tích hợp trên thân bơm xả về carter; lọc hút (suction strainer) trên ống hút ngay trước bơm.
- ⚠ "Van an toàn tích hợp trên thân bơm xả về carter; lọc hút trên ống hút ngay trước bơm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9e07d51e4055 – lube_unit_frame:function
> Đế và khay hứng dầu cho cụm bơm, lọc, làm mát dầu hộp số.
- ✓ "Hệ dầu bôi trơn nằm trong khung đế của máy ZE (nêu riêng cho ZE UTX)": c034 quote "The lubrication system … integrated into the extruder base frame": khớp.
- ✓ "Cụm bơm, lọc, làm mát dầu đặt trên khay sơn xanh có mép gập ở khung đế": web-03 (ZE 110 R, đã xem cả cắt phóng): cụm dầu đặt trên khay xanh có mép gập, trên khung đế trắng: thấy rõ.

### ed33b46fb0ab – lube_unit_frame:details[0]
> Khay có mép gập, tấm thấm dầu vàng như web-03.
- ✓ "Khay sơn xanh có mép gập, trong khay đặt vật thấm dầu màu vàng": web-03 (ZE 110 R, đã xem cả cắt phóng): khay xanh mép gập, trong khay có ống thấm dầu màu vàng: thấy rõ. Fact chỉ nói "vật thấm", đúng.
- ⚠ "Vật thấm dầu dạng tấm phẳng (trong ảnh web-03 là ống thấm dạng xúc xích)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

