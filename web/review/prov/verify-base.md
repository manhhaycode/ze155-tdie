# Kiểm nguồn nhóm base

Người kiểm: lead (Opus, làm tại chỗ). Hạn mức Sonnet hết giữa chừng nên người dùng chọn để lead tự kiểm; lead không gắn nhóm này. Ngày 2026-10-06.
Tổng: 33 dòng, 64 fact (✓ 14, ≈ 6, ⚠ 44 sau khi kiểm). Hạ mức (cả lượt kiểm trước nếu có): 6. Nâng mức: 0. Sửa chữ hoặc tách fact: 2.

Hình đã mở: trang 9 (`ze155ut_side_annotated.png`), crop trang 8 (khung đế ZE UTX), trang 18 (ZE Basic), trang 19 (bộ điều nhiệt), web-01 (cắt phóng khung đế), web-02, web-07. Chữ catalogue: chú giải "21 Diverter valve / 22 Slot die / 23 Smoothing roll" ở trang 27 (`ZE_text.txt` dòng 933–935). Claim đã đọc: c001, c006, c034, c035, c050.

Luật thang trang 9 (DECISIONS #9): các vị trí X đo theo thang 49,67 mm/pt = 5 746 / 115,68 pt là tỷ lệ trên chiều dài xi lanh 34D (DECISIONS 9) nên giữ ≈; tính lại: (449,10 − 460,0) × 49,672 = −541; (449,10 − 526,8) × 49,672 = −3 859 (dòng ghi −3 858); (449,10 − 425,2) × 49,672 = 1 187 (dòng ghi 1 185); (449,10 − 345,0) × 49,672 = 5 171; (449,10 − 329,87) × 49,672 = 5 922; 20,98 × 49,672 = 1 042. Các số đổi bằng thang tuyệt đối 45,2 mm/pt hạ xuống ⚠. Bản tiếng Nhật đã đối chiếu.

## Thay đổi

| Khoá | Thiết bị | Fact | Trước → sau | Lý do |
|---|---|---|---|---|
| 33b190624f43 | base_feet | 0 | ≈ → ⚠ | chiều cao chân lấy thang tuyệt đối 45,2 mm/pt của hình mẫu trang 9 (DECISIONS #9 không cho) |
| a1be77cea0f9 | base_frame_drive | 1 | ≈ → ⚠ | cao độ dầm trên lấy thang 45,2 mm/pt (như trên) |
| 732401ab4db6 | base_frame_drive | 1 | ≈ → ⚠ | cao hộp tủ, cửa, bước cửa lấy thang 45,2 mm/pt (như trên) |
| 831dc31a4591 | base_frame_drive | 2 | ≈ → ⚠ | Ø140 lấy thang 45,2 mm/pt (như trên) |
| 2cf93346d40f | base_frame_process | 1, 3 | ≈ → ⚠ | cao độ và Ø140 lấy thang 45,2 mm/pt (như trên) |
| 1e9742d9ba8d | melt_valve_support | 0 | chữ (✓ giữ nguyên) | chú giải 21–23 nằm ở trang 27, không chắc thuộc hình dây chuyền tấm; fact chỉ còn nói đúng chú giải |
| 2a297cb7db2c | base_frame_drive | 0 | lý do (≈ giữ nguyên) | ghi thêm: hai khoảng mối ở hai đầu chỉ ≈ 17,2 pt |

## Bằng chứng từng dòng

### ae4c028c7f24 – barrel_support_1:function, barrel_support_2:function, barrel_support_3:function
> Đỡ xi lanh từ dưới, cho phép xi lanh giãn nở nhiệt trượt theo X (điểm cố định ở lantern X = 0).
- ✓ "Xi lanh nằm trên các gối đỡ đúc gắn xuống khung đế (ảnh ZE 110 R; hình ZE 155 UT trang 9…": web-02, web-01: gối đúc trắng có lỗ tròn dưới xi lanh, bắt xuống khung: thấy rõ; hình trang 9 (bản có chú thích `ze155ut_side_annotated.png`): có gối tại vị trí kẹp (meas §2.2).
- ⚠ "Xi lanh trượt tự do theo X trên gối; điểm cố định ở lantern X = 0": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c05517a15aa5 – barrel_support_1:details[0], barrel_support_2:details[0], barrel_support_3:details[0]
> Gối đúc hình chữ A, tấm đế 700 × 250, lỗ tròn Ø120 giữa thân tại Z ≈ 800.
- ✓ "Gối đỡ là chi tiết đúc sơn trắng, có lỗ tròn xuyên ở phần thân, bắt bulông xuống tấm đế …": web-01 (cắt phóng khung đế): gối đúc trắng, lỗ tròn xuyên phần thân, bulông ở tấm đế: thấy rõ.
- ⚠ "Hình chữ A, tấm đế 700 × 250, lỗ tròn Ø120 giữa thân tại Z ≈ 800": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c75491624c56 – barrel_support_1:details[1], barrel_support_2:details[1], barrel_support_3:details[1]
> Lòng đỡ cong bán kính 260 ôm đáy thân xi lanh, có tấm trượt (slide pad) mỏng.
- ⚠ "Lòng đỡ cong bán kính 260 ôm đáy thân xi lanh": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tấm trượt (slide pad) mỏng giữa gối và thân xi lanh": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 75f6274945a9 – barrel_support_1:details[2], barrel_support_2:details[2], barrel_support_3:details[2]
> Đệm trên của gối rộng 70 mm (X), tì vào băng thân trần rộng 74 mm giữa hai vỏ nhiệt của đoạn.
- ⚠ "Đệm trên rộng 70 mm (X) tì vào băng thân trần rộng 74 mm giữa hai vỏ nhiệt của đoạn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 724d8fab4c84 – base_drip_tray:function
> Hứng nước, dầu, nhựa rơi dưới xi lanh để không chảy vào hộp tủ.
- ⚠ "Khay hứng nước, dầu, nhựa rơi dưới xi lanh để không chảy vào hộp tủ": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f53503cdc28d – base_drip_tray:details[0]
> Tôn inox 3 mm, mép gập cao 40 mm, có lỗ xả ở đầu X = 5 900.
- ⚠ "Tôn inox 3 mm, mép gập cao 40 mm, lỗ xả ở đầu X = 5 900": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### aafa1c23d104 – base_feet:function
> Chỉnh cao và neo khung đế xuống nền, hấp thụ rung.
- ✓ "Khung đế ZE đứng trên các chân tròn dưới đáy khung (hình ZE UTX trang 8; hình ZE 155 UT …": crop trang 8: chân tròn dưới đáy khung ZE UTX: thấy rõ; hình trang 9 (bản có chú thích `ze155ut_side_annotated.png`): 12 vị trí chân (meas §2.2).
- ⚠ "Chân chỉnh cao được, neo xuống nền bằng bulông, đệm giảm rung": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 33b190624f43 – base_feet:details[0]
> 22 chân Ø200 × 60 (đĩa đệm cao su + vít chỉnh M30), mỗi bên 11 chân tại Y = ±900.
- ⚠ "Chân cao 60 ≈ 57 mm = 1,27 pt × 45,2 mm/pt (đo trên hình ZE 155 UT trang 9)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "22 chân, mỗi bên 11 chân tại Y = ±900": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Chân Ø200, đĩa đệm cao su + vít chỉnh M30": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4dbd7dfa142f – base_feet:details[1]
> X = −5 050, −3 900, −2 700, −1 500, −300, 600, 1 700, 2 800, 3 900, 5 000, 5 850.
- ⚠ "11 vị trí chân dọc khung đế, X = −5 050 … 5 850 (liệt kê trong dòng)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6886be8b84be – base_frame_drive:function
> Đỡ hộp số, động cơ, lantern, vỏ khớp nối và cụm dầu; truyền tải trọng xuống chân đế.
- ✓ "Trên hình ZE 155 UT trang 9, lantern, hộp số, vỏ khớp nối, động cơ và cụm dầu nằm trên đ…": hình trang 9 (bản có chú thích `ze155ut_side_annotated.png`): các khối lantern, hộp số, vỏ khớp nối, cụm động cơ + dầu đứng trên đoạn khung phải; web-01: hộp số xanh đặt trên khung đế trắng. Tên khối theo nhận diện của pdf_measures, khớp hình dạng.

### a1be77cea0f9 – base_frame_drive:details[0]
> Dầm trên (top beam) hộp hàn Z 450–650, mặt trên gia công phẳng có các tấm đệm cho hộp số, đế động cơ, lantern.
- ✓ "Khung đế hai tầng: dầm trên chạy suốt chiều dài đặt trên hộp tủ dưới có cửa (trang 9); ả…": hình trang 9 (bản có chú thích `ze155ut_side_annotated.png`): khung hai tầng (dầm trên, hộp tủ dưới có cửa) chạy suốt; web-01 (cắt phóng khung đế): khung hộp thép tấm sơn trắng, đường hàn dọc mép trên: thấy được.
- ⚠ "Z 450–650: dầm trên cao ≈ 210 = 4,69 pt × 45,2 mm/pt; đỉnh khung ≈ 660 làm tròn 650": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Mặt trên gia công phẳng, có các tấm đệm cho hộp số, đế động cơ, lantern": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 732401ab4db6 – base_frame_drive:details[1]
> Hộp tủ dưới (cabinet box) Z 60–450 lùi vào 50 mm mỗi bên, cửa bản lề rộng 520 mm bước ≈ 860 mm, tay nắm lõm, hai bên ±Y.
- ✓ "Khung đế có hộp tủ dưới với cửa ở mặt bên (hình ZE 155 UT trang 9; hình ZE Basic trang 1…": hình trang 9 (bản có chú thích `ze155ut_side_annotated.png`): hộp tủ dưới có các ô cửa chữ nhật; crop trang 18: cửa khung đế (một cửa có lưới): thấy rõ.
- ⚠ "Hộp tủ Z 60–450 (cao ≈ 390); cửa rộng 520 ≈ 11,45 pt, bước ≈ 860 ≈ 19,1 pt, đều × 45,2 m…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Hộp tủ lùi vào 50 mm mỗi bên; cửa bản lề, tay nắm lõm, có ở cả hai bên ±Y": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 831dc31a4591 – base_frame_drive:details[2]
> Lỗ tròn vận chuyển Ø140 có nút nhựa vàng tại X = −541 và −3 858, cả hai mặt bên (theo trang 9).
- ✓ "Mặt bên khung đế có lỗ tròn, một lỗ gắn chốt màu vàng (ZE 110 R); hình ZE 155 UT trang 9…": web-01 (cắt phóng khung đế): mặt bên khung có lỗ tròn, một lỗ cắm chốt trụ màu vàng: thấy rõ; hình trang 9 (bản có chú thích `ze155ut_side_annotated.png`): 4 lỗ tròn trên hộp tủ.
- ≈ "X = −541 và −3 858: 2 lỗ phía dẫn động đo trên hình trang 9, X = (449,10 − x) × 49,67 vớ…": tính lại: (449,10 − 460,0) × 49,672 = −541; (449,10 − 526,8) × 49,672 = −3 859 ≈ −3 858 ✓. Thang dựng từ 34D (DECISIONS 9) trên chiều dài xi lanh đo được (meas §2.3): tỷ lệ trên mốc có nguồn, đúng luật trang 9.
- ⚠ "Ø140 ≈ 3,1 pt × 45,2 mm/pt (đường kính lỗ đo trên hình trang 9)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Lỗ dùng để vận chuyển, có nút nhựa vàng, có ở cả hai mặt bên": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 2a297cb7db2c – base_frame_drive:details[3]
> Mối hàn dọc trên dầm trên bước ≈ 1 050 mm (theo trang 9).
- ≈ "Các mối chia trên dầm trên cách nhau ≈ 1 050 mm (20,98 pt × 49,67 mm/pt = 1 042, làm trò…": tính lại: 20,98 × 49,672 = 1 042 → làm tròn 1 050 ✓; khoảng cách các mối không đều (đã ghi vào lý do).
- ⚠ "Các đường chia trên dầm trên là mối hàn của hộp hàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7457dc2293a0 – base_frame_drive:details[4]
> Bên trong hộp tủ: kênh cáp ngang nối phía +Y với phía −Y (cho cáp HMI, side feeder, nút dừng khẩn).
- ✓ "Khung đế chứa hệ bôi trơn, bộ điều nhiệt và thiết bị điều khiển điện (KM nêu cho ZE UTX)": c034 (medium) quote "the electrical control equipment are all integrated into the extruder base frame": khớp.
- ⚠ "Kênh cáp ngang trong hộp tủ nối phía +Y với phía −Y, cho cáp HMI, side feeder, nút dừng …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a38832d69035 – base_frame_process:function
> Đỡ các gối xi lanh, vỏ che, ống góp nước, máng cáp và hộp đấu dây suốt 34D.
- ✓ "Dọc khung đế ZE 110 R có gối xi lanh, ống góp nước, máng cáp mạ kẽm và hộp đấu dây vuông…": web-01, web-02: gối xi lanh, ống góp nước, máng lưới mạ kẽm, hộp đấu vuông dọc khung: thấy rõ; hình trang 9 (bản có chú thích `ze155ut_side_annotated.png`): 6 vỏ che hộp đứng trên khung.
- ≈ "Suốt 34D = 34 × 169 = 5 746 mm: chiều dài đoạn xi lanh mà khung đỡ": c001 quote "169"; 34D theo DECISIONS 9; 34 × 169 = 5 746 ✓. Ghi chú X 330–5 950 đúng.

### 2cf93346d40f – base_frame_process:details[0]
> Cùng tiết diện với đoạn truyền động: dầm trên Z 450–650, hộp tủ Z 60–450 có cửa và lỗ tròn Ø140 tại X = 1 185 và 5 170.
- ✓ "Cả hai đoạn khung có cùng hai tầng: dầm trên và hộp tủ dưới có cửa, lỗ tròn (hình ZE 155…": hình trang 9 (bản có chú thích `ze155ut_side_annotated.png`): cả đoạn trái và phải đều có dầm trên và hộp tủ dưới với lỗ tròn và ô cửa: thấy rõ.
- ⚠ "Dầm trên Z 450–650, hộp tủ Z 60–450: cùng số đo với đoạn truyền động (dầm 4,69 pt, hộp 8…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "Lỗ tròn tại X = 1 185 và 5 170: 2 lỗ phía xi lanh đo trên hình trang 9, X = (449,10 − x)…": tính lại: (449,10 − 425,2) × 49,672 = 1 187 ≈ 1 185; (449,10 − 345,0) × 49,672 = 5 171 ✓.
- ⚠ "Ø140 ≈ 3,1 pt × 45,2 mm/pt (đường kính lỗ đo trên hình trang 9)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Cùng bề rộng 2 000 mm với đoạn truyền động": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 480bb97bdbad – base_frame_process:details[1]
> Trong hộp tủ chứa bộ điều nhiệt / phân phối nước (temperature control unit) như catalogue c034; cửa có lưới thông gió.
- ✓ "Khung đế chứa bộ điều nhiệt (temperature control unit); hình ZE Basic thấy bơm, bình, va…": c034 quote "the temperature control unit … integrated into the extruder base frame"; crop trang 19: bơm, bình, van tay đỏ, ống mềm đen trong khung ZE Basic: thấy rõ.
- ⚠ "Bộ điều nhiệt kèm phân phối nước đặt ở hộp tủ đoạn gia công": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Cửa có lưới thông gió": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d9e17f1f498e – base_frame_process:details[2]
> Đầu khung phía khuôn (X = 5 950) có tấm bịt và 2 tai cẩu.
- ≈ "Đầu khung phía khuôn X = 5 950 ≈ 5 922 đo trên hình trang 9: (449,10 − 329,87) × 49,67": tính lại: (449,10 − 329,87) × 49,672 = 5 922 → làm tròn 5 950 ✓.
- ⚠ "Đầu khung có tấm bịt và 2 tai cẩu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5ad34e859e8d – melt_pipe_saddles:function
> Đỡ ống nhựa và bộ trộn tĩnh, cho trượt theo X khi giãn nở.
- ⚠ "Gối chữ V đỡ ống nhựa và bộ trộn tĩnh, cho trượt theo X khi giãn nở": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 0420adfc4269 – melt_pipe_saddles:details[0]
> 2 gối chữ V 150 × 240 cao 80 tại X = 8 250 (ống) và 8 560 (bộ trộn), mặt trượt cho X.
- ⚠ "2 gối chữ V 150 × 240 cao 80 tại X = 8 250 (đỡ ống) và 8 560 (đỡ bộ trộn), mặt trượt cho X": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 959874b19375 – melt_stand_pump:function
> Đỡ bơm bánh răng, ống nhựa và bộ trộn tĩnh.
- ⚠ "Bơm bánh răng, ống nhựa và bộ trộn tĩnh ngồi trên một khung thép riêng": đã xem web-07: thấy khung đỡ khuôn chân trắng, không thấy khung riêng dưới bơm; ⚠ đúng.

### 1403754e210e – melt_stand_pump:details[0]
> Khung thép hộp 6 chân, mặt đỉnh 1 250 × 900, Z = 970; kết thúc ở X = 8 650 để chừa chỗ cho đế xe khuôn.
- ⚠ "Khung thép hộp 6 chân, mặt đỉnh 1 250 × 900 tại Z = 970": 1 200 − 460/2 = 970 ✓; mọi kích thước là giả định.
- ⚠ "Khung kết thúc ở X = 8 650 để chừa chỗ cho đế xe khuôn (X 8 700–9 380)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d54f3c58f68b – melt_stand_pump:details[1]
> Bơm đặt trên tấm trượt PTFE (tự do X ±40, dẫn hướng Y); chỉ tấm đế được neo.
- ⚠ "Bơm trên tấm trượt PTFE, tự do X ±40 mm, dẫn hướng Y; chỉ tấm đế được neo": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 07e1ac7f4036 – melt_stand_sc:function
> Đỡ bộ lọc lưới 3,8 t và giữ tâm dòng chảy ở Z = 1 200.
- ✓ "Bộ lọc Gneuss RSFgenius 200 nặng 3 800 kg ≈ 3,8 t": c050 (high) quote kết thúc "| 3.800" (kg), claim "weight 3800 kg": khớp.
- ≈ "Tâm dòng chảy Z = 1 200 bằng cao trục vít (c006); sơ đồ catalogue vẽ melt line đồng trục…": c006 quote "1.200" (Achshöhe); sơ đồ trang 24–25 vẽ đường nhựa thẳng, đồng trục với trục xi lanh (bố cục, không cần tỷ lệ): ≈ đúng.
- ⚠ "Bộ lọc đặt trên giá thép riêng; Gneuss giao giá kèm bộ lọc": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6e6bc715f493 – melt_stand_sc:details[0]
> Khung thép hộp 4 chân, tấm đỉnh 800 × 1 200 × 30, giằng chéo hai bên.
- ⚠ "Khung thép hộp 4 chân, tấm đỉnh 800 × 1 200 × 30, giằng chéo hai bên": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 37c3cf77cac3 – melt_stand_sc:details[1]
> Mặt đỉnh Z = 650 trùng đáy thân bộ lọc; giữa bộ lọc và tấm đỉnh có tấm trượt PTFE: tự do theo X ±40 mm (giãn nở của xi lanh + đường chảy), dẫn hướng theo Y.
- ⚠ "Mặt đỉnh Z = 650 = 1 200 − D, với D = 550 (cao tâm nhựa trên đáy thân bộ lọc)": 1 200 − 550 = 650 ✓; ý nghĩa chữ D của Gneuss không rõ (design §9) nên ⚠ đúng.
- ⚠ "Tấm trượt PTFE giữa bộ lọc và tấm đỉnh: tự do theo X ±40 mm, dẫn hướng theo Y": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b133ff3de795 – melt_stand_sc:details[2]
> Chỉ tấm đế (sole plate) được neo xuống sàn; mặt −Y mang hộp đấu nhiệt đường chảy.
- ⚠ "Chỉ tấm đế (sole plate) neo xuống sàn; mặt −Y mang hộp đấu nhiệt đường chảy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1e9742d9ba8d – melt_valve_support:function
> Đỡ van khởi động và đầu xi lanh (≈ 1,3 t) đang treo ngoài gối đỡ cuối; con lăn/PTFE cho phép giãn nở theo X.
- ✓ "Chú giải sơ đồ dây chuyền trong catalogue KM (trang 27) có mục 21 van chuyển hướng (dive…": c035 (high) quote "21 Diverter valve 22 Slot die 23 Smoothing roll": khớp với chữ đã sửa (chú giải trang 27).
- ⚠ "Khối lượng van khởi động + đầu xi lanh ≈ 1,3 t": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Van và đầu xi lanh treo ngoài gối đỡ cuối, đỡ bằng giá có con lăn/PTFE cho giãn nở theo X": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f4e5085cdafb – melt_valve_support:details[0]
> Hai tai thép chữ L tại Y = ±(150…260), bắt vào mặt đầu khung (Z 560–650) rồi vươn lên Z 940; mỗi tai mang 1 đệm PTFE 90 × 110.
- ⚠ "Hai tai thép chữ L tại Y = ±(150…260), bắt vào mặt đầu khung (Z 560–650) rồi vươn lên Z …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Mỗi tai mang 1 đệm PTFE 90 × 110": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b1f4f5c5f1d7 – melt_valve_support:details[1]
> Chừa giữa Y ±150 cho máng xả nhựa; đáy giá ở Z 560, trên miệng xe hứng (Z 520).
- ⚠ "Chừa giữa Y ±150 cho máng xả nhựa; đáy giá ở Z 560, trên miệng xe hứng (Z 520)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d9fee3a1c668 – pump_drive_pedestal:function
> Đỡ hộp giảm tốc và động cơ bơm nhựa phía sau (−Y).
- ✓ "Bơm nhựa của dây chuyền KM có động cơ đứng gắn hộp giảm tốc đặt cạnh bơm, nối với bơm qu…": web-07 (ảnh dựng KM): khối bơm nối hộp giảm tốc góc và motor đứng qua hộp che có lưới thông gió: thấy rõ.
- ⚠ "Cụm hộp giảm tốc + động cơ đặt trên bệ riêng ở phía sau (−Y)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 900967c17dec – pump_drive_pedestal:details[0]
> Khung hộp thép 500 × 450, cao 950.
- ⚠ "Khung hộp thép 500 × 450, cao 950": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

