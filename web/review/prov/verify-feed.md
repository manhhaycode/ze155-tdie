# Kiểm nguồn nhóm feed

Người kiểm: lead (Opus, làm tại chỗ). Hạn mức Sonnet hết giữa chừng nên người dùng chọn để lead tự kiểm; lead không gắn nhóm này, trừ các dòng pilot ghi rõ bên dưới (với các dòng đó việc kiểm không độc lập). Ngày 2026-10-06.
Tổng: 62 dòng, 101 fact (✓ 26, ≈ 5, ⚠ 70 sau khi kiểm). Hạ mức (cả lượt kiểm trước nếu có): 0. Nâng mức: 0. Sửa chữ hoặc tách fact: 1.

Hình đã mở: web-04, web-05, web-16, sơ đồ trang 24–25 (toàn bộ), trang 9 (bản có chú thích), crop trang 6 (xe side feeder), crop trang 8 (side feeder). Chữ catalogue trang 27 (`ZE_text.txt` dòng 894–990): chú giải "1 Polymer … 3 Additives 4 Twin-screw side-feeder 5 Twin-screw extruder … 12 Silo …" và mục Feeding: "Whether it is powder, fine particle, pellets or fibers … feeding can be done gravimetrically … co-rotating twin-screw side-feeder units … used in a split-feed arrangement". Claim đã đọc: c001, c006, c024, c069. Tính lại: 450 × 0,8 / 3 500 × 60 = 6,2 phút; thể tích côn cụt 400 (Ø900 → Ø300) + trụ Ø900 × 800 ≈ 122 + 509 ≈ 630 L. Số trong bản tiếng Nhật khớp bản tiếng Việt (kiểm bằng máy).

## Thay đổi

| Khoá | Thiết bị | Fact | Trước → sau | Lý do |
|---|---|---|---|---|
| 045b7c70b8a5 | sidefeed_barrel | 1 | chữ (⚠ giữ nguyên) | "số 8 330" bị đọc thành một số 8 330; viết lại "hình số 8, cỡ 330" |

## Bằng chứng từng dòng

### c24996ed5b56 – feed_additive_feeder:function
> Định lượng phụ gia (masterbatch, chất chống dính) vào ống rơi chính.
- ✓ "Cân định lượng phụ gia cấp vào phễu chính của máy đùn (sơ đồ dây chuyền trong catalogue)": sơ đồ trang 24–25 + chú giải trang 27 ("3 Additives", "4 Twin-screw side-feeder", "12 Silo"): cụm cân C (phụ gia) đổ chung vào phễu chính trên máy đùn: thấy rõ.
- ⚠ "Phụ gia là masterbatch và chất chống dính (anti-block), đưa vào nhánh Y của ống rơi chính": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f49b454c9ee3 – feed_additive_feeder:details[0]
> Cân trục vít đôi 700 × 500 × 600 + phễu Ø500 cao 600 trên đỉnh.
- ⚠ "Cân trục vít đôi cỡ nhỏ (loại K-ML-D5-T35), thân 700 × 500 × 600, phễu Ø500 cao 600: loạ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a72321c85aa9 – feed_additive_tube:function
> Dẫn phụ gia vào nhánh Y của ống rơi chính.
- ⚠ "Ống phụ gia nối cửa xả cân phụ gia vào nhánh Y của ống rơi chính: cách nối do thiết kế c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 706300394433 – feed_additive_tube:details[0]
> Ống inox Ø80 bắt đầu dưới ống mềm cách cân (Z 2 850).
- ⚠ "Ống inox Ø80: cỡ ống do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Bắt đầu ở Z 2 850: mặt sàn Z 3 000 trừ ống mềm cách cân dài 150 (review-01 M8)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 0e7e1213b355 – feed_control_cabinet:function
> Bộ điều khiển các cân (KCM), cấp nguồn máy hút liệu.
- ⚠ "Tủ chứa bộ điều khiển các cân (KCM) và cấp nguồn máy hút liệu: chức năng do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6fe478b351af – feed_control_cabinet:details[0]
> Tủ 600 × 300 × 1 400 RAL 7035 có màn hình nhỏ ở cửa.
- ⚠ "Tủ 600 × 300 × 1 400, sơn RAL 7035, màn hình nhỏ ở cửa: kích thước, màu và cấu hình do t…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### ef15dfa0bcfa – feed_conveying_line:function
> Ống vận chuyển hạt từ silo tới máy hút liệu (vẽ tới mép trên khung nhìn).
- ✓ "Sơ đồ dây chuyền catalogue: silo nối bằng ống vận chuyển tới phễu đặt trên phễu cân của …": sơ đồ trang 24–25 + chú giải trang 27 ("3 Additives", "4 Twin-screw side-feeder", "12 Silo"): silo bên trái nối bằng đường ống lên các phễu nhận A, B đặt trên phễu cân: thấy rõ (sơ đồ ký hiệu, chỉ dùng thứ tự).
- ⚠ "Chỉ vẽ đoạn ống tới mép trên khung nhìn; phần nối tiếp tới silo không dựng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5367092983e1 – feed_conveying_line:details[0]
> Ống inox DN80 (OD 80), đầu trên để hở ký hiệu 'tới silo'.
- ⚠ "Ống inox DN80 (OD 80), đầu trên để hở ký hiệu "tới silo": cỡ ống và cách vẽ do thiết kế …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 41c076e02ac5 – feed_downpipe:function
> Dẫn hạt từ cân cấp liệu trên sàn thao tác xuống phễu.
- ✓ "Phễu inox nhỏ ở miệng nạp của máy nhận liệu qua ống đi xuống từ phía trên, dưới sàn tầng…": web-04, web-05 (ZE 110 UT): phễu inox nhỏ ở miệng nạp, ống mềm/ống trắng đi xuống từ trên, sàn tầng lửng thép ngay phía trên: thấy rõ.
- ⚠ "Cân cấp liệu đặt trên sàn thao tác cao 3 m ngay phía trên B1": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 53bd607709ff – feed_downpipe:details[0]
> Ống inox Ø250: đoạn đứng từ Z 2 850 (dưới ống mềm cách cân) xuống Z 2 550, rồi nghiêng 45° xuống tới phễu; treo bằng giá dưới dầm sàn, vành chắn ở lỗ sàn không chạm ống.
- ⚠ "Ống inox Ø250: cỡ ống do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đoạn đứng từ Z 2 850 (dưới ống mềm cách cân) xuống Z 2 550: cao độ do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "Đoạn dưới nghiêng 45° xuống tới phễu, cùng góc với cổ nạp 45° của phễu": góc 45° lấy theo cổ nạp phễu đo trên hình trang 9 (meas §2.2, góc là số đo tương đối, đúng luật trang 9); việc ống đi thẳng hàng với cổ là chọn của thiết kế, lý do ghi rõ: ≈ chấp nhận.
- ⚠ "Treo bằng giá dưới dầm sàn; vành chắn ở lỗ sàn không chạm ống": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f897e781d09a – feed_downpipe:details[1]
> Nhánh Y cho ống phụ gia tại Z = 2 700, cửa thăm có nắp.
- ⚠ "Nhánh Y cho ống phụ gia tại Z = 2 700, cửa thăm có nắp: vị trí và chi tiết do thiết kế c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### dabfd04d9385 – feed_feeder_sleeves:function
> Tách cửa xả của các cân loss-in-weight khỏi ống cứng để ống không tì lên cân, giữ độ chính xác định lượng.
- ⚠ "Ống mềm cách cân tách cửa xả cân loss-in-weight khỏi ống cứng để giữ độ chính xác định l…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 14019b568b5b – feed_feeder_sleeves:details[0]
> 3 ống bạt trắng dài 150 (Z 2 850–3 000) nằm trong lỗ sàn: Ø270 tại (−450, 0), Ø100 tại (−650, 850), Ø170 tại (1 350, 950); mỗi ống 2 đai kẹp inox.
- ⚠ "3 ống bạt trắng dài 150 (Z 2 850–3 000); Ø = Ø ống cứng + 20: 270 / 100 / 170 cho ống 25…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đặt tại (−450, 0), (−650, 850), (1 350, 950): tâm cân chính, cân phụ gia, cân side feede…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 0f502b9d5e15 – feed_flex_sleeve:function
> Nối mềm ống rơi với phễu, cách rung và cho phép tháo nhanh.
- ⚠ "Nối mềm ống rơi với phễu để cách rung và tháo nhanh: chức năng do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 995da586f670 – feed_flex_sleeve:details[0]
> Ống bạt trắng Ø260 dài 155 với 2 đai kẹp inox.
- ⚠ "Ống bạt trắng Ø260 dài 155 với 2 đai kẹp inox: kích thước do thiết kế chọn; 155 = √(110²…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 35c53cb1359f – feed_hopper:function
> Gom hạt từ ống rơi xuống miệng nạp; cổng nghiêng 45° về phía hộp số.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ≈ "Phễu trên miệng nạp có cổng nghiêng 45° hướng về phía dẫn động (đo trên hình bóng trang …": trang 9 (bản chú thích): phễu nhỏ có ống nghiêng về phía dẫn động; meas §2.2 "Phễu + ống nạp nghiêng 45°": khớp.
- ⚠ "Hạt đến phễu qua ống rơi từ cân cấp liệu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 890357ef2c59 – feed_hopper:details[0]
> Phễu hình chóp ngược inox: đỉnh 500 × 500, đáy 360 × 300 (côn cả theo Y).
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ≈ "Phễu hình chóp ngược trên miệng nạp": trang 9: phễu dạng chóp ngược trên miệng nạp: thấy.
- ⚠ "Inox; đỉnh 500 × 500, đáy 360 × 300": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### ff8b413a3c00 – feed_hopper:details[1]
> Nắp đỉnh có cổ nghiêng 45° Ø250 hướng −X, cổng khí N₂ (inert) nhỏ, kính thăm và cảm biến mức.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ≈ "Cổ nạp nghiêng 45° hướng −X (về phía dẫn động)": như 35c53cb1359f.
- ⚠ "Cổ Ø250, cổng khí N₂, kính thăm, cảm biến mức": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 85c7f154c257 – feed_main_feeder:function
> Định lượng 3 500 kg/h hạt PET theo khối lượng hao hụt.
- ✓ "Cân loss-in-weight cho hạt (pellet): Coperion K-Tron BSP-150-S, dải 34–6 700 dm³/h (bảng…": c069 (high) quote "Nominal feed rate: 34 to 6700 dm 3/hr … 320 (11.3) 1684 (66.3) 600 (23.6)"; loss-in-weight cho hạt, 3 cảm biến SFT, phễu nối thêm tới 320 dm³ nằm trong claim (high): khớp.
- ⚠ "3 500 kg/h hạt PET: năng suất thiết kế do thiết kế ước lượng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7896f0a651fe – feed_main_feeder:details[0]
> Thân bơm rắn BSP trên khung 3 cảm biến cân (load cells), động cơ hộp số phía −Y, hộp điều khiển KCM nhỏ phía +Y.
- ✓ "Thân bơm rắn BSP (bulk solids pump) trên 3 cảm biến cân SFT; cân K-Tron BSP-150-S dải 34…": c069 (high) quote "Nominal feed rate: 34 to 6700 dm 3/hr … 320 (11.3) 1684 (66.3) 600 (23.6)"; loss-in-weight cho hạt, 3 cảm biến SFT, phễu nối thêm tới 320 dm³ nằm trong claim (high): khớp.
- ⚠ "Động cơ hộp số đặt phía −Y, hộp điều khiển KCM nhỏ phía +Y: bố trí do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4d9e19fc4b1e – feed_main_feeder:details[1]
> Cửa xả đáy tại X = −450, Y = 0.
- ⚠ "Cửa xả đáy tại X = −450, Y = 0: vị trí do thiết kế chọn, trùng trục ống rơi chính và đườ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9af8e858ddde – feed_main_hopper:function
> Chứa hạt cho cân, ≈ 450 L (≈ 6 phút ở 3,5 t/h).
- ✓ "Cân BSP-150-S (34–6 700 dm³/h) có phễu nối thêm chứa hạt, bản hãng tới 320 dm³ (cao 1 68…": c069 (high) quote "Nominal feed rate: 34 to 6700 dm 3/hr … 320 (11.3) 1684 (66.3) 600 (23.6)"; loss-in-weight cho hạt, 3 cảm biến SFT, phễu nối thêm tới 320 dm³ nằm trong claim (high): khớp.
- ⚠ "Dung tích ≈ 450 L: do thiết kế chọn, lớn hơn 320 dm³ của hãng để thời gian nạp lại hợp lý": lý do đã ghi thể tích hình học ≈ 631 L (côn 400 + trụ Ø900 × 800) so với 450 L làm việc: đúng.
- ⚠ "≈ 6 phút ở 3,5 t/h: 450 L × 0,8 kg/L ÷ 3 500 kg/h × 60 ≈ 6 phút": tính lại 450 × 0,8 / 3 500 × 60 = 6,2 phút: ✓; cả ba đầu vào là giả định.

### 2b154d20dc55 – feed_main_hopper:details[0]
> Côn 400 + trụ Ø900 cao 800, kính thăm mức, cảm biến mức cao/thấp.
- ⚠ "Côn cao 400 + trụ Ø900 cao 800: hình học do thiết kế chọn, rộng hơn phễu nối thêm Ø600 c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Kính thăm mức, cảm biến mức cao/thấp": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### cf44aae6163e – feed_platform_columns_front:function, feed_platform_columns_rear:function
> Đỡ sàn thao tác xuống nền.
- ⚠ "Cột đỡ sàn thao tác xuống nền: kết cấu đỡ do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f1055aaff2f9 – feed_platform_columns_front:details[0]
> 3 cột HEB200 tại X = −2 600, −450, 1 750; Y = 1300; tấm đế 400 × 400, giằng góc dưới dầm.
- ⚠ "3 cột HEB200 tại X = −2 600, −450, 1 750; Y = 1300; tấm đế 400 × 400, giằng góc: tiết di…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7160017bf0cf – feed_platform_columns_rear:details[0]
> 3 cột HEB200 tại X = −2 600, −450, 1 750; Y = -2600; tấm đế 400 × 400, giằng góc dưới dầm.
- ⚠ "3 cột HEB200 tại X = −2 600, −450, 1 750; Y = -2600; tấm đế 400 × 400, giằng góc: tiết d…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9351dea40fb5 – feed_platform_deck:function
> Mặt bằng đặt các cân cấp liệu, lối đi bảo trì trên cao.
- ✓ "Sàn thép tầng lửng có lan can vàng nằm ngay trên khu cấp liệu của máy ZE 110 UT, có ống …": web-04, web-05 (ZE 110 UT): sàn thép tầng lửng có lan can vàng ngay trên khu miệng nạp, ống đi xuống phễu: thấy rõ.
- ⚠ "Các cân cấp liệu và lối bảo trì nằm trên sàn này: bố trí do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6a2b57ff4b5d – feed_platform_deck:details[0]
> Dầm chính HEA180 (Z 2 780–2 960) + sàn lưới mạ kẽm 40 mm (Z 2 960–3 000).
- ✓ "Sàn tầng lửng đỡ bằng dầm thép màu xám, có lan can vàng (ảnh ZE 110 UT)": web-04, web-05 (ZE 110 UT): dầm thép xám đỡ sàn, lan can vàng: thấy rõ.
- ⚠ "Dầm chính HEA180 (Z 2 780–2 960) + sàn lưới mạ kẽm 40 mm (Z 2 960–3 000): tiết diện, độ …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d441779b90ed – feed_platform_deck:details[1]
> Lỗ sàn có vành chắn cho ống mềm cách cân của ống rơi chính (X −450, Y 0), ống phụ gia (X −650, Y 850), ống side feeder (X 1 350, Y 950); vành không chạm ống.
- ⚠ "Lỗ sàn có vành chắn tại (−450, 0), (−650, 850), (1 350, 950) cho 3 ống mềm cách cân; vàn…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 35e4c51e0a8f – feed_platform_deck:details[2]
> Diện tích 4 550 × 4 100 (Y −2 700 … 1 400), phủ trên lantern, hộp số, B1, B2; mép sau lùi ra để lối đi phía −Y rộng ≥ 950.
- ⚠ "Sàn 4 550 × 4 100 (Y −2 700 … 1 400), phủ trên lantern, hộp số, B1, B2: kích thước do th…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Mép sau lùi ra Y −2 700 để lối đi phía −Y rộng ≥ 950 (theo review-01 I2)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 2f7f933d96dd – feed_platform_deck:details[3]
> Bố trí dầm (beams_mm, tâm dầm Z 2 870): dầm biên HEA180 theo X trên hai hàng cột (Y −2 600 và 1 300); dầm chính HEA180 theo Y trên các đường cột X −2 600, −450, 1 750.
- ⚠ "Dầm biên HEA180 theo X trên hai hàng cột (Y −2 600 và 1 300), dầm chính HEA180 theo Y tr…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9b1adea9a7ed – feed_platform_deck:details[4]
> Dầm chính X −450 bị ngắt tại Y ±260 quanh lỗ ống rơi chính (Ø270 + vành chắn); hai dầm viền (trimmer) HEA180 theo X ở Y ±260 từ X −760 tới −140 đỡ hai đầu dầm ngắt; đầu dầm viền tựa lên hai dầm phụ IPE160 theo Y tại X −760 và −140.
- ⚠ "Dầm chính X −450 ngắt tại Y ±260 quanh lỗ Ø270 của ống rơi chính; 2 dầm viền HEA180 đỡ đ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4bba4fc6a13d – feed_platform_deck:details[5]
> Dầm phụ IPE160 theo Y tại X −1 900, −1 200, 300, 1 000 đỡ tấm lưới (khoảng ≤ 750); lỗ ống phụ gia (−650, 850) và ống side feeder (1 350, 950) nằm giữa các dầm phụ.
- ⚠ "Dầm phụ IPE160 theo Y tại X −1 900, −1 200, 300, 1 000 đỡ tấm lưới (khoảng ≤ 750); lỗ (−…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 705609a75530 – feed_platform_railing:function
> Chống ngã từ sàn cao 3 m.
- ✓ "Lan can vàng bao quanh sàn tầng lửng của dây chuyền ZE 110 UT (ảnh)": web-04, web-05 (ZE 110 UT): lan can vàng quanh sàn tầng lửng: thấy rõ.
- ⚠ "Sàn cao 3 m (Z 3 000): cao độ do thiết kế ước lượng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e7b360999160 – feed_platform_railing:details[0]
> Tay vịn ống Ø42 cao 1 100, thanh giữa 550, tấm chắn chân 150, cột bước ≤ 1 500, màu vàng an toàn.
- ✓ "Tay vịn ống có thanh giữa, sơn vàng an toàn (ảnh ZE 110 UT)": web-04, web-05 (ZE 110 UT): tay vịn trên và thanh giữa sơn vàng: thấy rõ; tấm chắn chân không thấy rõ nên để ⚠ là đúng.
- ⚠ "Tay vịn Ø42 cao 1 100, thanh giữa 550, tấm chắn chân 150, cột bước ≤ 1 500: kích thước d…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 0b9157920c1b – feed_platform_railing:details[1]
> Chừa lối lên cầu thang ở mép −X đoạn Y −2 650 … −1 950.
- ⚠ "Chừa lối lên cầu thang ở mép −X, đoạn Y −2 650 … −1 950: trùng bề rộng cầu thang 700": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d65fde4d7fe8 – feed_stair:function
> Lối lên sàn cân cấp liệu (45°).
- ✓ "Cầu thang thép bậc lưới, tay vịn vàng, lên sàn tầng lửng cạnh máy (ảnh ZE 110 UT)": web-04, web-05 (ZE 110 UT): cầu thang thép bậc lưới, tay vịn vàng, lên sàn tầng lửng cạnh máy: thấy rõ.
- ⚠ "Độ dốc 45°: do thiết kế chọn; ảnh không đo được góc": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 69dad68b87a3 – feed_stair:details[0]
> Rộng 700, 45°, 15 bậc lưới cao 200, hai dầm thang (stringers) thép mạ kẽm, tay vịn vàng hai bên cao 1 000.
- ✓ "Bậc dạng lưới, hai dầm thang màu sáng, tay vịn vàng hai bên (ảnh ZE 110 UT)": web-05: bậc lưới, hai dầm thang màu sáng, tay vịn vàng hai bên: thấy rõ.
- ⚠ "Rộng 700, 45°, 15 bậc cao 200, thép mạ kẽm, tay vịn cao 1 000: kích thước do thiết kế ch…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f5dd49ee7d28 – feed_stair:details[1]
> Outline XZ là hình bao bên: mép dưới dầm thang từ (−5 400, 0) tới (−2 700, 2 700), tay vịn từ (−5 700, 1 000) tới (−2 700, 4 000).
- ⚠ "Hình bao XZ của cầu thang: dầm thang (−5 400, 0) → (−2 700, 2 700), tay vịn (−5 700, 1 0…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 0933003fa30f – feed_throat:function
> Nối phễu với lỗ nạp B1, có áo nước làm mát chống dính hạt.
- ⚠ "Hộp miệng nạp nối phễu với lỗ nạp B1: khối trung gian do thiết kế thêm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Áo nước làm mát chống dính hạt (bridging)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5534ccf4618b – feed_throat:details[0]
> Khối inox 500 × 420 × 185, lỗ trong 360 × 300, 2 đầu nối nước làm mát.
- ⚠ "Khối inox 500 × 420 × 185: kích thước do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Lỗ trong 360 × 300: nới từ 300 × 250 (ước lượng ở specs §2) cho vít D = 169": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "2 đầu nối nước làm mát cho áo nước": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 324092530379 – feed_vacuum_loader:function
> Hút hạt từ silo và nạp lại phễu cân.
- ✓ "Sơ đồ dây chuyền catalogue: silo nối bằng ống vận chuyển tới phễu đặt cao hơn phễu cân, …": sơ đồ trang 24–25 + chú giải trang 27 ("3 Additives", "4 Twin-screw side-feeder", "12 Silo"): đường ống từ silo lên phễu nhận đặt cao hơn phễu cân: thấy rõ (ký hiệu).
- ⚠ "Thiết bị hút/nhận liệu là máy hút liệu chân không đặt trên phễu cân: ước lượng của specs…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4ec95a187471 – feed_vacuum_loader:details[0]
> Bình Ø640 cao 900 với nắp lọc, van lật đáy, cổng liệu vào bên +Y, cổng hút khí trên nắp.
- ⚠ "Bình Ø640 cao 900 với nắp lọc, van lật đáy, cổng liệu vào bên +Y, cổng hút khí trên nắp:…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 069a4145b522 – sidefeed_adapter:function
> Nối thân side feeder vào cửa bên +Y của B2.
- ✓ "Side feeder nối vào hông xi lanh bằng mặt bích bắt bulông (hình ZE UTX, trang 8)": crop trang 8: hai trục vít nằm ngang trong thân, đi vào hông xi lanh; phễu nạp phía trên; bích bắt bulông: thấy rõ.
- ⚠ "Cửa bên ở B2, phía +Y (người vận hành): vị trí do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4e9be21199af – sidefeed_adapter:details[0]
> Tấm thép 370 × 80 × 320 lỗ hình số 8.
- ⚠ "Tấm thép 370 × 80 × 320: kích thước do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Lỗ hình số 8: khớp thân side feeder hai trục vít": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 09520cdf289c – sidefeed_barrel:function
> Ép liệu phụ (mảnh vụn biên tấm, phụ gia bột) vào cửa bên B2.
- ✓ "Side feeder trục vít đôi ép liệu rắn (phụ gia, bột) vào đoạn xi lanh có cửa bên cấp ngan…": chữ trang 27 "co-rotating twin-screw side-feeder units … introduction of solids into the melt", "powder, fine particle, pellets or fibers"; crop trang 8: hai trục vít nằm ngang trong thân, đi vào hông xi lanh; phễu nạp phía trên; bích bắt bulông: thấy rõ.
- ⚠ "Liệu phụ là mảnh vụn biên tấm (edge trim) nghiền nhỏ: do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 045b7c70b8a5 – sidefeed_barrel:details[0]
> Thân hình số 8 ngang 330 × 260 dài 770 theo Y: hai cung tròn R130 tâm X 1 315 và 1 385 (outline_mm), eo nhỏ trên và dưới tại X 1 350; 2 lỗ trục vít Ø112 tâm X 1 305 và 1 395, trục theo Y tại Z = 1 200.
- ✓ "Side feeder có 2 trục vít đặt ngang song song, đi vào hông xi lanh (hình trang 8)": crop trang 8: hai trục vít nằm ngang trong thân, đi vào hông xi lanh; phễu nạp phía trên; bích bắt bulông: thấy rõ.
- ⚠ "Thân hình số 8, cỡ 330 × 260, dài 770; 2 cung R130 tâm X 1 315 và 1 385, eo X 1 350; lỗ …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "Trục side feeder ngang tầm trục vít chính: Z = 1 200 (cao trục ZE 155 UTi theo bảng KM)": trục side feeder nằm ngang đi vào hông xi lanh (crop trang 8) nên cùng cao độ trục vít; c006 quote "1.200": ≈ đúng.

### 9a4c9f1048b2 – sidefeed_barrel:details[1]
> Lỗ nạp đỉnh gần đầu ngoài, áo nước làm mát, bích hai đầu.
- ✓ "Lỗ nạp ở đỉnh thân (phễu nhỏ phía trên) và mặt bích bắt bulông nối vào xi lanh (hình tra…": crop trang 8: hai trục vít nằm ngang trong thân, đi vào hông xi lanh; phễu nạp phía trên; bích bắt bulông: thấy rõ.
- ⚠ "Lỗ nạp gần đầu ngoài, áo nước làm mát, bích ở đầu kia: chi tiết do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9d3deef9557e – sidefeed_cart:function
> Đỡ hộp số + động cơ, cho phép kéo side feeder ra theo +Y khi bảo trì.
- ✓ "Hộp số và động cơ side feeder đặt trên xe đẩy thép trắng có bánh xe (hình cắt trang 6–7;…": crop trang 6: motor nằm ngang (nắp quạt, hộp điện tối màu trên nóc) và hộp số đặt trên xe khung thép trắng có bánh và tem cảnh báo điện: thấy rõ. web-16: cụm truyền động side feeder trên khung có bánh: thấy rõ.
- ⚠ "Kéo side feeder ra theo +Y khi bảo trì: hướng và cách bảo trì do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 51b117206543 – sidefeed_cart:details[0]
> Khung thép trắng 500 × 1 090 cao 1 000, 4 bánh xe có khoá, tem cảnh báo điện.
- ✓ "Xe khung thép trắng có bánh xe và tem cảnh báo điện (hình cắt trang 6–7)": crop trang 6: motor nằm ngang (nắp quạt, hộp điện tối màu trên nóc) và hộp số đặt trên xe khung thép trắng có bánh và tem cảnh báo điện: thấy rõ.
- ⚠ "Khung 500 × 1 090 cao 1 000, 4 bánh xe có khoá: kích thước, số bánh và khoá do thiết kế …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 92b172a92262 – sidefeed_downpipe:function
> Dẫn liệu phụ từ cân trên sàn xuống phễu side feeder.
- ✓ "Sơ đồ dây chuyền catalogue: liệu từ cân (feeder) đi theo đường dẫn xuống phễu side feeder": sơ đồ trang 24–25 + chú giải trang 27 ("3 Additives", "4 Twin-screw side-feeder", "12 Silo"): đường từ cân D/E xuống side feeder (4): thấy rõ.
- ⚠ "Cân side feeder đặt trên sàn thao tác, ống rơi dài từ Z 2 850 xuống phễu: bố trí do thiế…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f97e3d9320cd – sidefeed_downpipe:details[0]
> Ống inox Ø150 có đoạn ống mềm ở đáy.
- ⚠ "Ống inox Ø150 có đoạn ống mềm ở đáy (cân): cỡ ống do thiết kế chọn; ống mềm là ống mềm c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c9144ccbd8c1 – sidefeed_feeder:function
> Định lượng liệu phụ cho side feeder.
- ✓ "Cân (feeder) định lượng liệu phụ vào side feeder (sơ đồ dây chuyền catalogue)": sơ đồ trang 24–25 + chú giải trang 27 ("3 Additives", "4 Twin-screw side-feeder", "12 Silo"): cân định lượng cấp vào side feeder (4): thấy rõ.

### 58b6c7f9ab95 – sidefeed_feeder:details[0]
> Cân trục vít đôi trên 3 cảm biến cân, động cơ phía −X.
- ⚠ "Cân trục vít đôi (cỡ K-ML-D5-T35) trên 3 cảm biến cân, động cơ phía −X: loại, số cảm biế…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 525c3a37b9bb – sidefeed_feeder_hopper:function
> Chứa liệu phụ.
- ⚠ "Phễu chứa liệu phụ cho cân side feeder: chức năng do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b5d6a0c8a690 – sidefeed_feeder_hopper:details[0]
> Phễu Ø600 cao 700 có nắp.
- ⚠ "Phễu Ø600 cao 700 có nắp: kích thước do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f1744da4e89e – sidefeed_gearbox:function
> Giảm tốc và chia mômen ra 2 trục vít side feeder.
- ✓ "Side feeder có hộp số và động cơ riêng dẫn 2 trục vít, đặt trên xe đẩy (hình cắt trang 6…": crop trang 6: motor nằm ngang (nắp quạt, hộp điện tối màu trên nóc) và hộp số đặt trên xe khung thép trắng có bánh và tem cảnh báo điện: thấy rõ. "twin-screw side-feeder" (chú giải trang 27).
- ⚠ "Giảm tốc và chia mômen ra 2 trục vít: chức năng chung của hộp số trục vít đôi, không có …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5b379d5d17f1 – sidefeed_gearbox:details[0]
> Hộp 350 × 350 × 400, nút thăm dầu.
- ⚠ "Hộp 350 × 350 × 400, nút thăm dầu: kích thước và chi tiết do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 49b0d416e315 – sidefeed_hopper:function
> Nhận liệu từ cân phụ.
- ✓ "Side feeder có phễu nhỏ phía trên thân nhận liệu; sơ đồ dây chuyền vẽ cân cấp liệu vào p…": crop trang 8: hai trục vít nằm ngang trong thân, đi vào hông xi lanh; phễu nạp phía trên; bích bắt bulông: thấy rõ. Sơ đồ trang 24–25: cân cấp vào side feeder.

### 06be4cccc1ed – sidefeed_hopper:details[0]
> Phễu inox 300 × 260 cao 270, kính thăm.
- ✓ "Phễu nhỏ ở đỉnh thân side feeder (hình trang 8)": crop trang 8: hai trục vít nằm ngang trong thân, đi vào hông xi lanh; phễu nạp phía trên; bích bắt bulông: thấy rõ.
- ⚠ "Phễu inox 300 × 260 cao 270, kính thăm: kích thước, vật liệu và kính thăm do thiết kế chọn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6e218df47241 – sidefeed_motor:function
> Quay trục vít side feeder.
- ✓ "Động cơ điện nhỏ trên xe đẩy dẫn động side feeder qua hộp số (hình cắt trang 6–7)": crop trang 6: motor nằm ngang (nắp quạt, hộp điện tối màu trên nóc) và hộp số đặt trên xe khung thép trắng có bánh và tem cảnh báo điện: thấy rõ.

### a92787778a59 – sidefeed_motor:details[0]
> Động cơ nằm Ø360 dài 600, nắp quạt, hộp đấu dây trên nóc.
- ✓ "Động cơ nằm ngang có nắp quạt ở đuôi và một hộp điện trên nóc (hình cắt trang 6–7)": crop trang 6: motor nằm ngang (nắp quạt, hộp điện tối màu trên nóc) và hộp số đặt trên xe khung thép trắng có bánh và tem cảnh báo điện: thấy rõ. Fact viết "hộp điện" (không khẳng định hộp đấu dây): đúng.
- ⚠ "Ø360 dài 600: kích thước do thiết kế chọn cho động cơ 22 kW": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

