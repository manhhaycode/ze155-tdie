# Kiểm nguồn nhóm barrel

Người kiểm: lead (Opus, làm tại chỗ). Hạn mức Sonnet hết giữa chừng nên người dùng chọn để lead tự kiểm; lead không gắn nhóm này, trừ các dòng pilot ghi rõ bên dưới (với các dòng đó việc kiểm không độc lập). Ngày 2026-10-06.
Tổng: 77 dòng, 183 fact (✓ 77, ≈ 12, ⚠ 94 sau khi kiểm). Hạ mức (cả lượt kiểm trước nếu có): 0. Nâng mức: 0. Sửa chữ hoặc tách fact: 4.

Hình đã mở: web-01 (cả cắt phóng khung), web-02, web-06, web-07, crop trang 1 (vỏ che, vòm), trang 5 (lỗ số 8; kênh nước), trang 8 (side feeder), trang 12 (loại xi lanh), trang 21 (ZE Basic), img-p16_2, trang 9 (bản 1 200 dpi, cắt phóng vòm, bản chú thích). Chữ catalogue: trang 11 "figure 8 shaped barrel bore … Closely intermeshing screw elements along the entire processing section ensure excellent self-wiping"; trang 12 "building block system … Two barrel section lengths", "Closed barrels for the ZE-UT range … Top-open barrels"; trang 13 phần tử "conveying elements with different lengths and pitches, multi-start … kneading … back-pumping elements" và xi lanh "open barrels for feed zones, open barrels equipped with inserts for degassing … closed barrels, combined barrels for horizontal side feeding"; trang 16 "removal of volatile matter such as water, monomers, oligomers, solvents, etc. (degassing)". Claim đã đọc: c001, c002, c006, c017, c018, c023, c030, c031, c036, c037, c040, c061, c062. Tính lại: tâm đoạn 338 / 1 183 / 2 197 / 3 211 / 4 225 / 5 239 (4D = 676, 6D = 1 014); 34 × 169 = 5 746; 169 − 2 × 27,2 = 114,6; (169 + 114,6)/2 = 141,8; 142 + 169 = 311; diện tích lỗ số 8 = 2 × 22 432 − 1 681 = 43 182 mm², × 30 N/mm² = 1,30 MN, 4 / 1,3 = 3,1; 360/20 = 18°; 2 × 50 + 2 × (24 + 8) = 164; 280 ± 18; (640 − 560)/2 − 13 = 27; 272,5 − 26,5 = 246 < 260; −260 sin 40° = −167, 1 200 + 260 cos 40° = 1 399; 1 014 − 2 × 90 − 2 × 380 = 74; 520/169 = 3,1; atan(170/150) = 48,6°; 169 × 192,3/194 = 167,5. Số trong bản tiếng Nhật khớp bản tiếng Việt (kiểm bằng máy).

Ghi chú cho người thiết kế: hộp đấu dây xi lanh ghi 180 × 120 × 200 nhưng parts.json là [180, 180, 260]; vỏ che ghi vát 45° nhưng outline 150 × 170 là ≈ 49°; vỏ che trang 1 là vỏ tròn, thiết kế theo vỏ hộp của trang 9 và web-07.

## Thay đổi

| Khoá | Thiết bị | Fact | Trước → sau | Lý do |
|---|---|---|---|---|
| 4f00ec2344a6 | barrel_cover_c6 | 0 | chữ, bỏ ref web-01 (✓ giữ) | web-01 không có vỏ che nào; chỉ hình trang 9 cho thấy vỏ phủ phía đầu ra |
| e5a3d9afc242, 55591a3774ef | barrel_cover_c3, barrel_cover_c6 | 0 | chữ (✓ giữ) | web-07 là ảnh dựng, không phải "máy thật" |
| c64329da3cc4 | barrel_cw_supply | 0 | chữ (✓ giữ) | ống góp trong web-02 bọc vỏ bạc, không thấy là inox; bỏ chữ "inox" |
| 8f0de34875f5 | barrel_vent_dome | 0 | chữ (✓ giữ) | "2 kính quan sát" trên hình bóng trang 9 là cách đọc, bỏ khỏi fact ✓ |
| b217f1fdea3f | barrel_vent_dome | 0 + 2 (mới) | tách ✓ → ✓ + ≈ | ✓ chỉ cho kính kẹp vành có tay gạt (trang 1); 2 kính trên hình trang 9 thành fact ≈ |

## Bằng chứng từng dòng

### 0ca7fa864a43 – barrel_b1:function
> Nhận hạt PET từ miệng cấp liệu; làm mát bằng nước để hạt không chảy sớm.
- ✓ "B1 là đoạn xi lanh mở trên đỉnh dùng làm vùng cấp liệu (open barrel for feed zone) của Z…": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp.
- ✓ "KM đùn tấm PET trực tiếp trên máy trục vít đôi ZE UT, không cần kết tinh hay sấy trước": c040 (high) quote "the material does not have to be crystallized or pre-dried": khớp.
- ⚠ "Nhận hạt PET qua miệng cấp liệu; làm mát bằng nước để hạt không chảy sớm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 344cb5315968 – barrel_b1:details[0], barrel_b2:details[0], barrel_b3:details[0] …
> Thân trụ Ø520, mặt bích Ø640 × 50 hai đầu; mỗi bích 20 lỗ Ø26 trên PCD 560 (mép lỗ cách mép bích 27 mm), một bích có gờ định tâm, bích kia có rãnh.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ✓ "Xi lanh ZE-UT là thân trụ có mặt bích hai đầu; các đoạn nối với nhau bằng bích bắt bulông": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp. web-01 (ZE 110 R): các đoạn tròn nối bằng vành bích bắt bulông.
- ⚠ "Thân trụ Ø520": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Mặt bích Ø640 × 50; 20 lỗ Ø26 trên PCD 560; mép lỗ cách mép bích 27 mm = (640 − 560)/2 −…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Một bích có gờ định tâm, bích kia có rãnh": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4fccbfffa464 – barrel_b1:details[1], barrel_b2:details[1], barrel_b3:details[1] …
> Sau mỗi bích thân tiện thắt Ø500 dài 40 mm (vùng đặt đai ốc), để có khe 12 mm cho khẩu 12 cạnh thành mỏng khi tháo vỏ nhiệt; vỏ nhiệt bắt đầu ngay sau đoạn thắt.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ⚠ "Sau mỗi bích thân tiện thắt Ø500 dài 40 mm, chừa khe 12 mm cho khẩu 12 cạnh thành mỏng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Vỏ nhiệt bắt đầu ngay sau đoạn thắt": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6bfa5899dc76 – barrel_b1:details[2], barrel_b2:details[2], barrel_b3:details[2] …
> Bên trong: lỗ hình số 8 rộng 311 × cao 169 (2 lỗ Ø169 tâm Y = ±71).
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ✓ "Lỗ xi lanh hình số 8 (2 lỗ tròn giao nhau) chứa 2 trục vít": crop trang 5: mặt cắt xi lanh có lỗ hình số 8 với trục vít; trang 11 "figure 8 shaped barrel bore": khớp.
- ✓ "Ø169 = đường kính vít ZE 155 A UTi (bảng KM)": c001 quote "169": khớp.
- ≈ "Tâm hai lỗ Y = ±71: khoảng cách tâm a ≈ 142 = (D + d)/2 = (169 + 114,6)/2": tính lại d = 169 − 54,4 = 114,6; a = 141,8; a/2 ≈ 71 ✓ (c001, c002; cách tính khớp ZE 180 với c017).
- ≈ "Rộng 311 = a 142 + D 169": tính lại 142 + 169 = 311 ✓.

### 2c1c055c5181 – barrel_b1:details[3]
> Lỗ nạp trên đỉnh 360 × 300 tại X 160–520, mặt gia công phẳng cho hộp miệng nạp.
- ✓ "Xi lanh ZE UT có loại mở trên đỉnh (top-open) 4D hoặc 6D, dùng cho vùng cấp liệu": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp.
- ⚠ "Lỗ nạp 360 × 300 tại X 160–520, mặt gia công phẳng cho hộp miệng nạp": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f88d49a269bb – barrel_b1:details[4]
> Không có băng nhiệt; áo nước làm mát, 2 đầu nối nước ở đáy tại X = 200 (vào) và 476 (ra).
- ✓ "Xi lanh có lỗ khoan nước làm mát chạy dọc thân, nối bằng ống mềm": crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.
- ⚠ "B1 không có băng nhiệt, chỉ làm mát bằng nước (áo nước)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "2 đầu nối nước ở đáy tại X = 200 (vào) và 476 (ra) = 0 + 200 và 676 − 200": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 57340273293a – barrel_b1:details[5]
> Đầu X = 0: bích Ø640 bắt 20 bulông cấy M24 trên PCD 560 vào lantern, đai ốc 12 cạnh phía B1.
- ✓ "Trên máy ZE 110 R thật, đầu xi lanh phía hộp số là mặt bích tròn có vòng bulông cấy và đ…": web-01 (ZE 110 R): đầu xi lanh phía hộp số là vành bích tròn có bulông cấy và đai ốc: thấy rõ.
- ⚠ "Bích Ø640 bắt 20 bulông cấy M24 trên PCD 560 vào lantern, đai ốc 12 cạnh phía B1; X = 0 …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f2501f1f27fd – barrel_b1:details[6]
> Cặp nhiệt B1 cắm nghiêng 40° ở góc trên phía −Y, chân tại (X 338, Y -167, Z 1399), để tránh hộp miệng nạp.
- ✓ "Trên ZE 110 R thật, mỗi đoạn xi lanh có cặp nhiệt cắm vào thân, dây bọc lưới kim loại": web-01 (ZE 110 R): mỗi đoạn có cặp nhiệt cắm vào thân, dây bọc lưới: thấy rõ.
- ⚠ "Cặp nhiệt B1 cắm nghiêng 40° ở góc trên phía −Y, chân tại (X 338, Y −167, Z 1399): Y = −…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e0a9aa21352b – barrel_b2:function
> Vận chuyển hạt, nhận liệu phụ từ side feeder qua cửa bên +Y, bắt đầu nóng chảy ở cuối đoạn.
- ✓ "Xi lanh ZE UT có loại mở bên / kết hợp (side-open, combination) để cấp liệu phụ nằm ngan…": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp. Crop trang 8: side feeder hai trục vít vào hông xi lanh.
- ✓ "Phần tử vận chuyển nhiều bước ren và phần tử nhào có trong dải phần tử trục vít của KM": chữ trang 13 "conveying elements with different lengths and pitches, multi-start … kneading elements": khớp.
- ⚠ "Side feeder đặt ở phía +Y (phía người vận hành), cấp liệu phụ vào cửa bên B2": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Nóng chảy bắt đầu ở cuối B2 (khối nhào ở cuối B2 – đầu B3)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a5e4c9715e0a – barrel_b2:details[3]
> Cửa bên +Y 340 × 260 tại X 1 180–1 520 (hình số 8 nhìn ngang) có mặt bích cho side feeder.
- ✓ "Xi lanh ZE có cửa hông hình số 8 nhìn ngang, mặt phẳng bắt bulông để gắn side feeder hai…": crop trang 21: cửa hông có lỗ số 8 trên tấm phẳng bắt bulông; crop trang 8: side feeder hai trục vít: thấy rõ.
- ⚠ "Cửa bên +Y 340 × 260 tại X 1 180–1 520, mặt bích cho side feeder": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 332ddbd6d835 – barrel_b2:details[4]
> 2 băng nhiệt có cửa sổ tránh cửa bên; lỗ khoan nước làm mát dọc thân.
- ✓ "Xi lanh có lỗ khoan nước làm mát chạy dọc thân": crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.
- ✓ "Xi lanh ZE UT thật (ZE 110 R) có vỏ nhiệt inox bóng ôm thân giữa các vành bích, có lỗ ch…": web-01, web-02 (ZE 110 R): vỏ inox bóng ôm thân giữa các vành bích, có lỗ cho cặp nhiệt: thấy rõ.
- ⚠ "2 băng nhiệt trên B2, có cửa sổ tránh cửa bên +Y": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 724f9ad4b461 – barrel_b2:details[5]
> 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 876 (vào) và 1490 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- ✓ "Xi lanh có kênh nước làm mát nối ống mềm": crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.
- ⚠ "2 đầu nối ở góc dưới +Y (45°, Y 184, Z 1 016), X = 876 vào và 1490 ra, qua rãnh 50 mm củ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9f53a694bc38 – barrel_b3:function
> Nóng chảy (khối nhào) rồi hút chân không nhẹ (≈ 50 mbar) ngay khi nhựa vừa chảy, rút phần lớn hơi nước trước khi PET bị thuỷ phân và không cho không khí lọt vào.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ✓ "Xi lanh ZE UT có loại mở trên đỉnh, gắn tấm lót để thoát khí": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp.
- ✓ "PET không cần kết tinh hay sấy trước khi vào máy trục vít đôi ZE UT (KM đùn tấm PET trực…": c040 quote "does not have to be crystallized or pre-dried": khớp.
- ⚠ "Khối nhào (kneading block) làm chảy nhựa ở cuối B2 – đầu B3": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Chân không vùng 1 ≈ 50 mbar": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Hút ẩm ngay khi nhựa vừa chảy để PET không bị thuỷ phân (cắt mạch, tụt độ nhớt IV); vòm …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1ce0adb46e32 – barrel_b3:details[3]
> Lỗ trên đỉnh 320 × 280 tại X 1 990–2 310 với tấm lót (vent insert); vòm chân không 2 lắp trên.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ✓ "Xi lanh ZE UT có loại mở trên đỉnh, gắn tấm lót (insert) để thoát khí": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp.
- ⚠ "Lỗ 320 × 280 tại X 1 990–2 310": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Vòm chân không 2 (vùng 1) lắp trên lỗ": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a4e1eeeeeec3 – barrel_b3:details[4], barrel_b5:details[4]
> 2 băng nhiệt có khe tại lỗ.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ⚠ "2 băng nhiệt trên đoạn 6D, có khe tại lỗ thoát khí": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b9621c0bbd36 – barrel_b3:details[5]
> 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 1890 (vào) và 2504 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ✓ "Xi lanh có kênh nước làm mát nối ống mềm": crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.
- ⚠ "2 đầu nối ở góc dưới +Y (45°, Y 184, Z 1 016), X = 1890 vào và 2504 ra, qua rãnh 50 mm c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a52af91ac997 – barrel_b4:function
> Trộn, đồng nhất nhựa nóng chảy; trước B5 có phần tử nghịch tạo nút nhựa kín chân không.
- ✓ "Phần tử nhào, trộn, chặn và đẩy ngược (back-pumping) có trong dải phần tử trục vít của KM": chữ trang 13 "mixing elements … kneading elements … barrier elements … back-pumping elements": khớp.
- ⚠ "B4 trộn và đồng nhất nhựa chảy; cuối B4 có phần tử nghịch (left-handed) tạo nút nhựa bịt…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4422fb1d6171 – barrel_b4:details[3]
> 2 băng nhiệt, lỗ khoan nước làm mát, 1 cặp nhiệt.
- ✓ "Xi lanh có lỗ khoan nước làm mát chạy dọc thân": crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.
- ✓ "Xi lanh ZE UT thật (ZE 110 R) có vỏ nhiệt inox bóng ôm thân và cặp nhiệt dây bọc lưới tr…": web-01, web-02 (ZE 110 R): vỏ inox bóng và cặp nhiệt dây bọc lưới trên mỗi đoạn: thấy rõ.
- ⚠ "B4 có 2 băng nhiệt và 1 cặp nhiệt": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4fe1f5b80c29 – barrel_b4:details[4]
> 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 2904 (vào) và 3518 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- ✓ "Xi lanh có kênh nước làm mát nối ống mềm": crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.
- ⚠ "2 đầu nối ở góc dưới +Y (45°, Y 184, Z 1 016), X = 2904 vào và 3518 ra, qua rãnh 50 mm c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a7079581872d – barrel_b5:function
> Hút chân không sâu (5–20 mbar) để khử nốt ẩm, acetaldehyde và oligome của PET không sấy.
- ✓ "Catalogue ghi ZE dùng để khử khí (degassing): tách nước, monome, oligome, dung môi": chữ trang 16 "removal of volatile matter such as water, monomers, oligomers, solvents, etc. (degassing)": khớp.
- ✓ "KM đùn tấm PET trực tiếp trên ZE UT, không cần kết tinh hay sấy trước": c040 quote như trên: khớp.
- ⚠ "Chân không sâu 5–20 mbar ở vùng 2 (B5)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Khử nốt ẩm, acetaldehyde và oligome của PET không sấy ở vùng này": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 3e809ad8284e – barrel_b5:details[3]
> Lỗ trên đỉnh 520 × 280 tại X 3 860–4 380 (≈ 3D) với tấm lót (vent insert); vòm chân không lắp trên.
- ✓ "Xi lanh ZE UT có loại mở trên đỉnh, gắn tấm lót (insert) để thoát khí; trên máy ZE thật,…": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp. web-02 (ZE 110 R): ống thoát khí lắp trên lỗ đỉnh (nhãn "Vacuum Port").
- ⚠ "Lỗ 520 × 280 tại X 3 860–4 380 (≈ 3D, vì 520 / 169 ≈ 3,1)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Vòm chân không kín lắp trên lỗ B5 (vùng 2)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f6e57d75bdf2 – barrel_b5:details[5]
> 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 3918 (vào) và 4532 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- ✓ "Xi lanh có kênh nước làm mát nối ống mềm": crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.
- ⚠ "2 đầu nối ở góc dưới +Y (45°, Y 184, Z 1 016), X = 3918 vào và 4532 ra, qua rãnh 50 mm c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### bdde748629bd – barrel_b6:function
> Tăng áp đẩy nhựa vào đầu xi lanh.
- ✓ "ZE UT có đoạn xi lanh kín (closed barrel) 4D hoặc 6D": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp.
- ⚠ "B6 tăng áp (pressure build-up) để đẩy nhựa vào đầu xi lanh": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a3fe3c0faefb – barrel_b6:details[3]
> Cổng bên +Y bịt mặt bích tròn (cổng phun lỏng dự phòng) tại X ≈ 5 400, Z = 1 200 – thấy qua tấm tròn 10 bulông của vỏ che C1 (trang 9).
- ✓ "Dải xi lanh ZE-UT có loại phun lỏng (injection barrel)": crop trang 12: hàng ZE-UT có "Injection barrels": thấy rõ.
- ≈ "Hình ZE 155 UT (trang 9): vỏ che đầu ra có tấm tròn bắt bulông với 10 lỗ, đếm trên hình": trang 9 (bản 1 200 dpi và bản chú thích): tấm tròn trên vỏ che đầu ra có vòng lỗ, đếm 10 (meas §4 cũng 10); đếm là số tương đối: ≈ đúng.
- ⚠ "Cổng bên +Y của B6 bịt mặt bích tròn (cổng phun lỏng dự phòng) tại X ≈ 5 400, Z = 1 200,…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 11d9665c78fd – barrel_b6:details[4]
> Mặt bích ra X = 5 746: 20 bulông cấy M24 trên PCD 560 vào bích đầu xi lanh.
- ✓ "Trên ZE 110 R thật, đầu ra của dãy xi lanh là mặt bích tròn lớn có vòng lỗ bulông": web-01 (ZE 110 R): đầu ra dãy xi lanh là mặt bích tròn lớn có vòng lỗ bulông: thấy rõ.
- ≈ "Mặt bích ra tại X = 5 746 = 34 × 169 (chiều dài gia công 34D)": 34 × 169 = 5 746 ✓; 34D theo DECISIONS 9, lý do ghi rõ L/D 44 của bảng KM (c007): đúng.
- ⚠ "20 bulông cấy M24 trên PCD 560 vào bích đầu xi lanh": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d45ca25c0615 – barrel_b6:details[5]
> 2 đầu nối nước làm mát ở góc dưới +Y (45°, Y 184, Z 1 016) tại X = 4932 (vào) và 5546 (ra), qua rãnh 50 mm của băng nhiệt; không đặt dưới gối đỡ.
- ✓ "Xi lanh có kênh nước làm mát nối ống mềm": crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.
- ⚠ "2 đầu nối ở góc dưới +Y (45°, Y 184, Z 1 016), X = 4932 vào và 5546 ra, qua rãnh 50 mm c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### fe9a07239066 – barrel_cable_tray:function
> Dẫn cáp nhiệt, cặp nhiệt, cảm biến dọc máy về tủ điện.
- ✓ "Trên ZE 110 R thật, cáp nhiệt và cặp nhiệt đi vào máng thép mạ kẽm đục lỗ dọc dưới xi la…": web-01, web-02 (ZE 110 R): máng thép mạ kẽm đục lỗ dưới xi lanh mang cáp nhiệt và cặp nhiệt tới hộp đấu: thấy rõ.
- ⚠ "Máng đặt ở phía −Y, dẫn cả cáp cảm biến về tủ điện qua máng đứng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d22e59abf9f8 – barrel_cable_tray:details[0]
> Máng đục lỗ mạ kẽm 300 × 100 có nắp, chạy X −1 000 … 5 800 trên mép −Y của khung.
- ✓ "Máng cáp là máng thép mạ kẽm đục lỗ (ZE 110 R thật)": web-01, web-02 (ZE 110 R): máng mạ kẽm đục lỗ: thấy rõ.
- ⚠ "Máng 300 × 100 có nắp, chạy X −1 000 … 5 800 trên mép −Y của khung": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### db671e2be5b9 – barrel_cover_c1:function, barrel_cover_c2:function, barrel_cover_c3:function …
> Cách nhiệt và che bề mặt nóng của xi lanh, giữ nhiệt ổn định, bảo vệ người vận hành.
- ✓ "Barrel ZE được che theo từng đoạn bằng vỏ inox dán tam giác vàng cảnh báo bề mặt nóng, đ…": crop trang 1: vỏ inox từng đoạn dán tam giác vàng "bề mặt nóng", ray xanh dọc mép: thấy rõ. img-p16_2 và web-07: vỏ che hộp inox có tam giác vàng.
- ⚠ "Vỏ che cách nhiệt, giữ nhiệt xi lanh ổn định": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 3aea5bcc88cb – barrel_cover_c1:details[0], barrel_cover_c2:details[0], barrel_cover_c3:details[0] …
> Hộp inox xước 1,5 mm có cách nhiệt bông khoáng bên trong, vát 45° hai mép trên (xem outline).
- ✓ "Vỏ che dạng hộp inox, mép trên vát; hình ZE 155 UT (trang 9) cũng vẽ vỏ che dạng hộp": web-07, img-p16_2: vỏ che hộp inox, mép trên vát; trang 9 (bản 1 200 dpi và bản chú thích): vỏ che dạng hộp: thấy rõ.
- ⚠ "Tôn inox xước 1,5 mm, bông khoáng cách nhiệt bên trong, vát 45° hai mép trên (outline YZ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 68aa1ff3b4a0 – barrel_cover_c1:details[1], barrel_cover_c2:details[1], barrel_cover_c3:details[1] …
> Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650 bản lề phía −Y, mở lên.
- ✓ "Vỏ che trên ZE BluePower gồm nắp trên và tấm dưới, chia bởi một đường ngang chạy suốt": web-07 (ảnh dựng): vỏ che có đường chia ngang chạy suốt, nắp trên và tấm dưới: thấy rõ.
- ⚠ "Tấm dưới Z 650–1 150 tháo được; nắp trên Z 1 150–1 650, bản lề phía −Y, mở lên": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### ccd0383d6841 – barrel_cover_c1:details[2], barrel_cover_c2:details[2], barrel_cover_c3:details[2] …
> Mặt +Y: tay nắm đen trên nắp và trên tấm dưới, tam giác vàng 'bề mặt nóng' ở giữa (như trang 9); 1 tay nắm trên đỉnh.
- ✓ "Vỏ che có tay nắm đen trên nắp và tấm dưới, tam giác vàng "bề mặt nóng" giữa mặt, 1 tay …": web-07: tay nắm đen trên nắp và tấm dưới, tam giác vàng giữa mặt, tay nắm trên đỉnh; trang 9 (bản 1 200 dpi và bản chú thích): tay nắm và tam giác tương tự: thấy rõ.
- ⚠ "Mặt có tay nắm và tam giác là mặt +Y (phía người vận hành)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6f98e8629a11 – barrel_cover_c1:details[3], barrel_cover_c2:details[3], barrel_cover_c3:details[3] …
> Khe dưới hai bên cho ống nước và cáp nhiệt đi vào.
- ✓ "Trên máy ZE thật, ống mềm nước và cáp nhiệt đi từ phía dưới lên thân xi lanh": web-02 (ZE 110 R): ống mềm nước và cáp đi từ dưới lên thân; crop trang 1: ống mềm dưới vỏ che: thấy rõ.
- ⚠ "Vỏ che chừa khe dưới hai bên cho ống nước và cáp nhiệt đi vào": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 3114e969ceae – barrel_cover_c1:details[4]
> Tấm đầu X = 5 746–5 760 có lỗ tròn Ø660 (bích Ø640); mặt +Y có tấm tròn Ø420 bắt 10 bulông tại X ≈ 5 400, Z = 1 200 (trang 9) che cổng bên B6, cùng một hộp đấu dây nhỏ phía dưới.
- ✓ "Hình ZE 155 UT (trang 9): vỏ che đầu ra có tấm tròn bắt bulông và một cụm hộp nhỏ phía d…": trang 9 (bản 1 200 dpi và bản chú thích): vỏ che đầu ra có tấm tròn bắt bulông và cụm hộp nhỏ phía dưới: thấy rõ.
- ≈ "Tấm tròn có 10 lỗ bulông (đếm trên hình trang 9)": trang 9 (bản 1 200 dpi và bản chú thích): đếm 10 lỗ: ≈ đúng.
- ⚠ "Tấm đầu X = 5 746–5 760 có lỗ tròn Ø660 ôm bích Ø640": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tấm tròn Ø420 tại X ≈ 5 400, Z = 1 200 che cổng bên B6": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e5a3d9afc242 – barrel_cover_c3:details[4]
> Lỗ khoét 620 × 420 cho vòm chân không.
- ✓ "Hình ZE 155 UT (trang 9): vòm thoát khí dạng hộp cao nhô lên trên vỏ che; trên ảnh dựng …": trang 9 (bản 1 200 dpi và bản chú thích): vòm hộp cao nhô trên vỏ; web-07 (ảnh dựng): vòm xuyên nắp vỏ che: thấy rõ. Chữ đã sửa "máy thật" → "ảnh dựng".
- ⚠ "Lỗ khoét 620 × 420 = vòm B5 600 × 400 cộng 10 mm mỗi phía": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 55591a3774ef – barrel_cover_c6:details[4]
> Lỗ khoét 420 × 380 (X 1 940–2 360) cho vòm chân không vùng 1.
- ✓ "Trên ảnh dựng ZE BluePower, vòm thoát khí xuyên qua nắp vỏ che": web-07 (ảnh dựng): vòm xuyên nắp vỏ che: thấy rõ.
- ⚠ "Lỗ khoét 420 × 380 (X 1 940–2 360) cho vòm vùng 1 = vòm 400 × 360 (X 1 950–2 350) cộng 1…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4f00ec2344a6 – barrel_cover_c6:details[5]
> Tấm đầu phía X = 1 690 có lỗ Ø660 ôm vành bích Ø640 và đai ốc của mối nối 2 (nửa mối nối nằm ngoài vỏ, phía vùng nạp để lộ).
- ✓ "Hình ZE 155 UT (trang 9): vỏ che chỉ phủ phần phía đầu ra, vùng nạp để lộ xi lanh và vàn…": trang 9 (bản 1 200 dpi và bản chú thích): vỏ C1–C6 chỉ phủ từ đầu ra tới gần vùng nạp; vùng nạp để lộ xi lanh và vành bích: thấy rõ. Đã bỏ web-01 (ảnh đó không có vỏ che).
- ⚠ "Tấm đầu phía X = 1 690 có lỗ Ø660 ôm vành bích Ø640 và đai ốc của mối nối 2; nửa mối nối…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5575e4d138f7 – barrel_cw_hoses:function
> Dẫn nước từ cụm van lên lỗ khoan làm mát xi lanh và về.
- ✓ "Ống mềm inox bọc lưới dẫn nước từ cụm van trên khung lên đầu nối dưới xi lanh (ZE 110 R)…": web-02 (ZE 110 R): ống mềm inox bọc lưới từ cụm van lên đầu nối dưới xi lanh; crop trang 5: khối xi lanh có các lỗ khoan dọc thân và đầu nối ống mềm: thấy rõ.

### acb2d99f20e9 – barrel_cw_hoses:details[0]
> 12 ống mềm inox bọc lưới DN15 (OD 24), mỗi đoạn 1 ống vào + 1 ống ra (đường đi trong paths_mm).
- ✓ "Ống mềm inox bọc lưới nối cụm van với đầu nối ở xi lanh (ZE 110 R)": web-02 (ZE 110 R): ống mềm inox bọc lưới nối cụm van với xi lanh: thấy rõ.
- ⚠ "12 ống = 6 đoạn xi lanh × (1 ống vào + 1 ống ra)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Cỡ DN15 (OD 24)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 8fa6cac73fc8 – barrel_cw_hoses:details[1]
> Ống vào: từ đỉnh cụm van (X tâm − 40) chéo tới X = đầu đoạn + 200, xuyên tấm dưới của vỏ che ở Y 480, Z ≈ 990, rồi vào đầu nối 45° dưới +Y; ống ra đối xứng ở X = cuối đoạn − 200.
- ✓ "Trên ZE 110 R thật, ống mềm từ cụm van uốn chéo lên đầu nối ở phần dưới xi lanh": web-02 (ZE 110 R): ống mềm uốn chéo từ cụm van lên phần dưới xi lanh: thấy rõ.
- ⚠ "Ống vào: từ đỉnh cụm van (X tâm − 40) chéo tới X = đầu đoạn + 200, xuyên tấm dưới vỏ che…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d6fb9167c2e9 – barrel_cw_hoses:details[2]
> B1: hai đầu nối ở đáy tại X 200 và 476; không ống nào đi dưới gối đỡ.
- ⚠ "B1: hai đầu nối ở đáy tại X 200 và 476 (= 0 + 200 và 676 − 200), không ống nào đi dưới g…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 13ab3a64c204 – barrel_cw_return:function
> Gom nước hồi từ các vùng xi lanh.
- ✓ "Ống góp nước cấp và hồi chạy song song dọc khung đế, nối với từng cụm van của mỗi vùng (…": web-02 (ZE 110 R): hai ống góp chạy song song dọc khung, nối các cụm van từng vùng: thấy rõ.

### 880453a21999 – barrel_cw_return:details[0]
> Ống inox DN50 (OD 60) song song phía ngoài ống cấp, Z = 800.
- ✓ "Hai ống góp (cấp, hồi) chạy song song dọc khung đế, có mũi tên chiều dòng (ZE 110 R)": web-02 (ZE 110 R): hai ống góp song song có mũi tên chiều dòng: thấy rõ.
- ⚠ "Ống inox DN50 (OD 60) song song phía ngoài ống cấp, Z = 800": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c64329da3cc4 – barrel_cw_supply:function
> Phân phối nước làm mát tới các vùng xi lanh.
- ✓ "Ống góp nước dọc khung đế, mỗi vùng xi lanh một cụm van (ZE 110 R và ảnh dựng ZE BluePow…": web-02 (ZE 110 R): ống góp dọc khung với cụm van từng vùng; web-06 (ảnh dựng): ống và van dưới xi lanh: thấy rõ. Đã bỏ chữ "inox".

### ad241248a38c – barrel_cw_supply:details[0]
> Ống inox DN50 (OD 60), mũi tên chiều dòng, gá trên bát đỡ cách mặt khung 30 mm.
- ✓ "Ống góp có mũi tên chiều dòng dán trên ống, gá trên các bát đỡ dọc khung (ZE 110 R)": web-02 (ZE 110 R): mũi tên chiều dòng dán trên ống góp, ống gá trên bát đỡ dọc khung: thấy rõ.
- ⚠ "Ống inox DN50 (OD 60), gá trên bát đỡ cách mặt khung 30 mm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b19964c06101 – barrel_cw_valves:function
> Đóng/mở nước làm mát từng vùng theo lệnh bộ điều nhiệt.
- ✓ "Mỗi vùng xi lanh của ZE 110 R có van điện từ (cuộn đen) và van bi tay đỏ trên ống góp nước": web-02 (ZE 110 R): mỗi vùng có van điện từ cuộn đen và van tay đỏ; c023 quote "valvole con maniglie rosse": khớp.
- ⚠ "Van đóng/mở nước làm mát từng vùng theo lệnh của bộ điều nhiệt (vòng điều khiển nhiệt độ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 304d819d533b – barrel_cw_valves:details[0]
> 6 cụm tại X = 338, 1 183, 2 197, 3 211, 4 225, 5 239; mỗi cụm: van bi tay đỏ, lọc Y, van điện từ (cuộn đen), van tiết lưu, chỉ báo dòng chảy.
- ✓ "Ống góp của ZE 110 R có, cho mỗi vùng, van bi tay đỏ và van điện từ cuộn đen": như b19964c06101.
- ≈ "6 cụm tại X = 338, 1 183, 2 197, 3 211, 4 225, 5 239 = tâm các đoạn B1…B6": tính lại tâm các đoạn (4D = 676, 6D = 1 014): 338, 1 183, 2 197, 3 211, 4 225, 5 239 ✓.
- ⚠ "Mỗi đoạn một cụm đặt tại tâm đoạn; mỗi cụm có thêm lọc Y, van tiết lưu và chỉ báo dòng c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a6c7e88af200 – barrel_cw_valves:details[1]
> 1 đồng hồ áp trên ống cấp, 1 trên ống hồi.
- ✓ "Ống góp nước của ZE 110 R có đồng hồ áp": web-02 (ZE 110 R): đồng hồ áp trên ống góp: thấy rõ.
- ⚠ "1 đồng hồ áp trên ống cấp, 1 trên ống hồi": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1a84a1d99672 – barrel_heater_jboxes:function
> Đấu cáp băng nhiệt và cặp nhiệt của từng vùng vào cáp chính.
- ✓ "Trên ZE 110 R thật, dưới mỗi đoạn xi lanh có hộp đấu vuông nhận cáp nhiệt và cặp nhiệt": web-01, web-02 (ZE 110 R): hộp đấu vuông dưới mỗi đoạn nhận cáp nhiệt và cặp nhiệt: thấy rõ.
- ⚠ "Hộp đấu cáp băng nhiệt và cặp nhiệt của từng vùng vào cáp chính, về tủ điều khiển và nhiệt": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d81cc18551d2 – barrel_heater_jboxes:details[0]
> 7 hộp inox 180 × 120 × 200 có nắp kính nhỏ / ổ cắm công nghiệp, tại X = 338, 1 183, 2 197, 3 211, 4 225, 5 239, 5 700 (đầu xi lanh).
- ✓ "Hộp đấu vuông nhỏ đặt dưới mỗi đoạn xi lanh trên ZE 110 R": web-01, web-02 (ZE 110 R): hộp đấu vuông nhỏ dưới mỗi đoạn: thấy rõ.
- ≈ "6 hộp đầu tại X = 338, 1 183, 2 197, 3 211, 4 225, 5 239 = tâm các đoạn B1…B6": như 304d819d533b (tâm đoạn) ✓.
- ⚠ "7 hộp inox 180 × 120 × 200 có nắp kính nhỏ hoặc ổ cắm công nghiệp; hộp thứ 7 tại X = 5 7…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9cad6bb4acb0 – barrel_heater_shells:function
> Gia nhiệt xi lanh B2–B6, mỗi đoạn 6D một vùng nhiệt ≈ 25 kW.
- ✓ "Trên ZE UT thật (ZE 110 R), vỏ nhiệt inox bóng ôm thân xi lanh; ZE BluePower cỡ lớn dùng…": web-01, web-02 (ZE 110 R): vỏ inox bóng ôm thân; c037 (medium) quote "the cartridge heaters are replaced by ceramic heaters" (ZE BluePower cỡ lớn): khớp.
- ⚠ "Gia nhiệt B2–B6, mỗi đoạn 6D một vùng nhiệt; B1 chỉ làm mát": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Công suất ≈ 25 kW mỗi vùng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a7000c2ddd98 – barrel_heater_shells:details[0]
> 10 vỏ (2 mỗi đoạn 6D), mỗi vỏ Ø580 dài 380, gồm 2 nửa bản lề, kẹp bằng 2 bulông, mép có vòng gân đục lỗ.
- ✓ "Vỏ nhiệt inox bóng ôm thân xi lanh giữa các vành bích, mép có vòng gân đục lỗ (ZE 110 R …": web-01, web-02 (ZE 110 R): vỏ inox bóng giữa các vành bích, mép có vòng gân đục lỗ: thấy rõ.
- ⚠ "10 vỏ = 2 vỏ × 5 đoạn 6D (B2–B6), mỗi vỏ Ø580 dài 380, gồm 2 nửa bản lề, kẹp bằng 2 bulông": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e239bc80876e – barrel_heater_shells:details[1]
> Mỗi vỏ bắt đầu cách mặt đầu đoạn 90 mm (chừa chỗ đai ốc của mối nối bích); giữa hai vỏ của một đoạn có băng thân trần 74 mm cho gối đỡ.
- ✓ "Trên ZE 110 R thật, vỏ nhiệt nằm giữa các vành bích bắt bulông, chừa chỗ cho đai ốc bích": web-01, web-02 (ZE 110 R): vỏ nằm giữa các vành bích, chừa chỗ đai ốc: thấy rõ.
- ⚠ "Vỏ bắt đầu cách mặt đầu đoạn 90 mm (= bích 50 + đoạn thắt 40), chừa chỗ đai ốc của mối n…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Giữa hai vỏ của một đoạn có băng thân trần 74 mm cho gối đỡ: 74 = 1 014 − 2 × 90 − 2 × 380": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5c30d7141f9b – barrel_heater_shells:details[2]
> Vỏ có cửa sổ tại cửa bên B2 và lỗ đỉnh B3/B5; rãnh 50 mm ở góc dưới +Y tại X = đầu đoạn + 200 và cuối đoạn − 200 cho đầu nối nước.
- ✓ "Trên ZE 110 R thật, vỏ nhiệt có lỗ ở chỗ cặp nhiệt và chỗ khuyết cho đầu nối ống đi qua": web-02 (ZE 110 R): lỗ cặp nhiệt trên vỏ, chỗ khuyết cho đầu nối ở dưới: thấy.
- ⚠ "Vỏ có cửa sổ tại cửa bên B2 và lỗ đỉnh B3/B5; rãnh 50 mm ở góc dưới +Y tại X = đầu đoạn …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### fe13b01590ce – barrel_heater_shells:details[3]
> Hộp đấu nhỏ trên mỗi vỏ, cáp bọc lưới inox đi xuống hộp đấu dây phía −Y.
- ✓ "Trên ZE 110 R thật, vỏ nhiệt có khối đấu nhỏ ở đỉnh; cáp đi xuống các hộp đấu vuông dưới…": web-01 (ZE 110 R): khối đấu nhỏ trên đỉnh vỏ, cáp đi xuống hộp đấu vuông: thấy rõ.
- ⚠ "Cáp bọc lưới inox; hộp đấu dây đặt phía −Y": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 84fcb8bd4839 – barrel_joint_1:function, barrel_joint_2:function, barrel_joint_3:function …
> Ép hai mặt bích Ø640 của hai đoạn xi lanh vào nhau cho kín áp nhựa, định tâm hai lỗ số 8; tháo được khi đổi cấu hình xi lanh.
- ✓ "Các đoạn xi lanh ZE UT nối nhau bằng mặt bích bắt bulông (ZE 110 R thật); ZE cỡ lớn nối …": web-01 (ZE 110 R): các đoạn nối bằng bích bắt bulông; c037 quote "connected by means of screw unions instead of clamping flanges"; crop trang 12 thân có bích: khớp.
- ✓ "Xi lanh và trục vít ZE theo nguyên tắc module, ghép lại và đổi được khi đổi cấu hình hay…": chữ trang 12 "building block system … can all be combined"; c030 (high) claim "screws and barrels interchangeable": khớp.
- ⚠ "Ép hai mặt bích Ø640 vào nhau cho kín áp nhựa và định tâm hai lỗ số 8 (qua gờ định tâm)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1a2ef460e906 – barrel_joint_1:details[0], barrel_joint_2:details[0], barrel_joint_3:details[0] …
> 20 bulông cấy M24 cấp 10.9 chịu nhiệt, mỗi bulông 2 đai ốc 12 cạnh (Ø36 qua đỉnh) có vòng đệm, trên PCD 560, chia đều 18°, lệch 9° để không có bulông đúng đỉnh/đáy.
- ✓ "Vành bích nối xi lanh có vòng bulông cấy, đai ốc và vòng đệm (ZE 110 R thật)": web-01, web-02 (ZE 110 R): vành bích có vòng bulông cấy, đai ốc, vòng đệm: thấy rõ.
- ⚠ "Bulông cấy M24 cấp 10.9 chịu nhiệt; mỗi bulông 2 đai ốc 12 cạnh (Ø36 qua đỉnh) có vòng đệm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "20 bulông trên PCD 560, chia đều 18° (= 360° / 20), lệch 9° (= 18° / 2) để không có bulô…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### ce76804cecf5 – barrel_joint_1:details[1], barrel_joint_2:details[1], barrel_joint_3:details[1] …
> Bulông dài 164: xuyên 2 bích × 50 mm, mỗi đầu đai ốc cao 24 + 8 mm ren thừa; đai ốc nằm trong vành r 262–298, trên đoạn thân thắt Ø500 (khe 12 mm), mép lỗ cách mép bích Ø640 27 mm.
- ⚠ "Bulông dài 164 = 2 × 50 (hai bích) + 2 × (24 đai ốc + 8 ren thừa)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đai ốc nằm trong vành r 262–298 (= 280 ± 18, tức PCD 560 / 2 ± Ø36 / 2), trên đoạn thân …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Mép lỗ cách mép bích Ø640 27 mm = (640 − 560) / 2 − 26 / 2": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 8c0048dd3d1e – barrel_joint_1:details[2], barrel_joint_2:details[2], barrel_joint_3:details[2] …
> Giữa hai bích: gờ định tâm (centring spigot) Ø400 và mặt kín kim loại; mặt ngoài vành bích tiện bóng, đai ốc thép đen.
- ⚠ "Giữa hai bích: gờ định tâm (centring spigot) Ø400 và mặt kín kim loại; mặt ngoài vành bí…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 55bf9ca9efe1 – barrel_joint_1:details[3], barrel_joint_2:details[3], barrel_joint_3:details[3] …
> Lực siết ≈ 20 × 200 kN = 4 MN, gấp ≈ 3 lần lực đẩy của nhựa 300 bar trên lỗ số 8 (≈ 1,2 MN).
- ≈ "Diện tích lỗ số 8 ≈ 43 200 mm² (hai lỗ Ø169 trừ phần giao, tâm cách 142)": tính lại: 2 × π × 84,5² − giao (≈ 1 681) = 43 182 mm² ✓ (D từ c001, a từ specs §1).
- ⚠ "Áp tính 300 bar cho lực đẩy nhựa trên lỗ số 8 ≈ 1,2 MN (= 30 N/mm² × 43 200 mm²; tính lạ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Lực siết ≈ 20 × 200 kN = 4 MN, gấp ≈ 3 lần lực đẩy nhựa": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 2bd06d09fbf2 – barrel_joint_1:details[4], barrel_joint_2:details[4], barrel_joint_3:details[4] …
> Không dùng M30 trên PCD 545: đai ốc M30 (đối đỉnh 53 mm) sẽ chạm thân xi lanh Ø520.
- ⚠ "Không dùng M30 trên PCD 545: đai ốc M30 (đối đỉnh 53 mm) chạm thân xi lanh Ø520, vì 545 …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c35b925c84a3 – barrel_thermocouples:function
> Đo nhiệt độ từng vùng xi lanh cho bộ điều nhiệt.
- ✓ "Trên ZE 110 R thật, mỗi đoạn xi lanh có cặp nhiệt cắm vào thân, dây bọc lưới kim loại": web-01 (ZE 110 R): cặp nhiệt cắm vào thân mỗi đoạn, dây bọc lưới: thấy rõ.
- ⚠ "Mỗi vùng xi lanh một cặp nhiệt, tín hiệu nối bộ điều nhiệt": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### bbbcaefa7132 – barrel_thermocouples:details[0]
> 6 cặp nhiệt loại J Ø30 dài 90 (35 mm nằm trong thành xi lanh, 55 mm lộ ra): B1 cắm nghiêng 40° so với phương đứng về phía −Y, chân tại (338, -167, 1399) trên mặt thân, đầu dưới đáy hộp miệng nạp; còn lại cắm đứng trên đỉnh thân tại X = 1 450, 2 450, 3 211, 4 600, 5 239 (xuyên lỗ trên vỏ nhiệt), nắp lưỡi lê, cáp bọc lưới inox.
- ✓ "Trên ZE 110 R thật, cặp nhiệt cắm qua lỗ của vỏ nhiệt vào thân xi lanh, đầu có khớp nối …": web-01, web-02 (ZE 110 R): cặp nhiệt qua lỗ vỏ nhiệt, đầu khớp vặn, dây bọc lưới: thấy rõ.
- ⚠ "6 cặp nhiệt loại J Ø30 dài 90 (35 mm trong thành xi lanh + 55 mm lộ ra), nắp lưỡi lê": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "B1 cắm nghiêng 40° so với phương đứng về phía −Y, chân tại (338, −167, 1399) trên mặt th…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "5 cặp còn lại cắm đứng trên đỉnh thân tại X = 1 450, 2 450, 3 211, 4 600, 5 239 (xuyên l…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e24c633d029f – barrel_thermocouples:details[1]
> item_mm = [Ø, Ø, dài] theo hệ trục riêng; trục từng cái trong item_axes.
- ⚠ "Ghi chú quy ước dữ liệu của mô hình (item_mm, item_axes), không phải thông tin về máy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 8f0de34875f5 – barrel_vent_dome:function
> Tạo buồng kín trên lỗ thoát khí B5 để hút chân không; kính quan sát cho thấy nhựa không trào lên.
- ✓ "ZE có vòm thoát khí inox với kính quan sát tròn kẹp bằng vành, lắp trên lỗ thoát khí (tr…": crop trang 1: vòm inox, kính tròn kẹp vành, lắp trên lỗ; web-07: vòm có kính; trang 9 (bản 1 200 dpi và bản chú thích): vòm hộp cao. Đã bỏ phần "2 kính" khỏi fact ✓.
- ⚠ "Vòm tạo buồng kín trên lỗ B5 để hút chân không; người vận hành nhìn qua kính để chắc nhự…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 0f74ad55a699 – barrel_vent_dome:details[0]
> Thân hộp inox 600 × 400, bo góc R40, từ Z 1 460 lên 2 100; nắp 640 × 450 dày 50 kẹp bằng 4 bulông bướm, 2 tai (lugs) trên nắp.
- ✓ "Hình ZE 155 UT (trang 9) vẽ vòm thoát khí dạng hộp cao đặt trên vỏ che": trang 9 (bản 1 200 dpi và bản chú thích): vòm thoát khí dạng hộp cao trên vỏ che: thấy rõ.
- ⚠ "Thân hộp inox 600 × 400, bo góc R40, từ Z 1 460 (đỉnh thân xi lanh = 1 200 + 260) lên 2 …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b217f1fdea3f – barrel_vent_dome:details[1]
> 2 kính quan sát Ø160 có vành kẹp trên mặt +Y tại X = 3 970 và 4 270, Z = 1 880.
- ✓ "Trên máy ZE (ảnh catalogue trang 1), kính quan sát tròn kẹp bằng vành có tay gạt": crop trang 1: kính tròn kẹp bằng vành có tay gạt đen: thấy rõ.
- ⚠ "2 kính Ø160 trên mặt +Y tại X = 3 970 và 4 270 (= tâm vòm 4 120 ± 150), Z = 1 880": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "Hình ZE 155 UT (trang 9) vẽ 2 chi tiết giống nhau có vòng tròn trên mặt vòm, đọc là 2 kí…": trang 9 (bản 1 200 dpi và bản chú thích): cắt phóng vòm: 2 chi tiết giống nhau có vòng tròn; đọc là kính quan sát: ≈.

### d4288427bcd1 – barrel_vent_dome:details[2]
> Đầu ra chân không DN150 ở giữa nắp (X 4 120, Y 0, Z 2 150), đi thẳng lên van chặn; mặt −Y của vòm phẳng, không có cổng.
- ✓ "Vòm thoát khí trên máy ZE thật có cổng ra dạng bích kẹp để nối ống hút chân không": web-02 (ZE 110 R): cổng bên có bích trên ống thoát khí ("Vacuum Port"); crop trang 1: cổng ra nối ống bằng vòng kẹp: thấy rõ.
- ⚠ "Đầu ra chân không DN150 ở giữa nắp (X 4 120, Y 0, Z 2 150), đi thẳng lên van chặn; mặt −…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 81b9f26d103c – barrel_vent_dome:details[3]
> Tay nắm nâng nắp, đèn soi kính (tuỳ chọn).
- ✓ "Nắp vòm thoát khí trên máy ZE thật có tay cầm đen (trên vành kẹp kính)": crop trang 1: tay cầm đen trên vành kẹp kính; web-07 tương tự: thấy rõ.
- ⚠ "Đèn soi kính (tuỳ chọn)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 34c76b914d74 – barrel_vent_dome_2:function
> Buồng kín trên lỗ B3, hút chân không nhẹ (≈ 50 mbar) để rút hơi nước ngay sau vùng chảy.
- ✓ "ZE UT có đoạn xi lanh mở trên đỉnh, gắn tấm lót (insert) để thoát khí": crop trang 12: dải xi lanh ZE-UT là thân trụ có bích hai đầu, loại kín, mở trên đỉnh, mở bên/kết hợp, phun lỏng; c031 (high) quote "Barrel sections with an L/D ratio of 4 or 6", claim "open feed barrels, open barrels with inserts for degassing, closed barrels, combined barrels": khớp.
- ⚠ "Chân không vùng 1 ≈ 50 mbar": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Hút ngay sau vùng chảy trong buồng kín để rút hơi nước": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### bd274c66402a – barrel_vent_dome_2:details[0]
> Thân hộp inox 400 × 360 bo góc R30 từ Z 1 460 lên 1 920; nắp dày 40 (Z 1 920–1 960) kẹp 4 bulông bướm, 2 tai.
- ✓ "Hình ZE 155 UT (trang 9) vẽ vòm thoát khí dạng hộp cao đặt trên vỏ che": trang 9 (bản 1 200 dpi và bản chú thích): vòm hộp cao trên vỏ che: thấy rõ.
- ⚠ "Thân hộp inox 400 × 360, bo góc R30, từ Z 1 460 lên 1 920; nắp dày 40 (Z 1 920–1 960) kẹ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9648b2bdc7c4 – barrel_vent_dome_2:details[1]
> 1 kính quan sát Ø120 có vành kẹp trên mặt +Y tại X 2 150, Z 1 750.
- ✓ "Vòm thoát khí ZE có kính quan sát tròn kẹp bằng vành (trang 1 và ảnh ZE BluePower)": crop trang 1, web-07: kính tròn kẹp vành trên vòm: thấy rõ.
- ⚠ "1 kính Ø120 trên mặt +Y tại X 2 150 (tâm vòm), Z 1 750": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6edefc6b38fd – barrel_vent_dome_2:details[2]
> Đầu ra DN100 có bích Ø220 trên mặt −Y tại X 2 150, Z 1 800.
- ✓ "Vòm thoát khí trên máy ZE thật có cổng ra dạng bích để nối ống hút chân không": web-02 (ZE 110 R): cổng ra có bích trên ống thoát khí; crop trang 1 vòng kẹp: thấy rõ.
- ⚠ "Đầu ra DN100 có bích Ø220 trên mặt −Y tại X 2 150, Z 1 800": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### bd7b5cdda32a – screws:function
> Vận chuyển, nóng chảy, trộn, khử khí và tăng áp nhựa; tự làm sạch lẫn nhau.
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ✓ "Hai trục vít đồng hướng ăn khớp sát nhau dọc cả máy, tự làm sạch lẫn nhau": chữ trang 11 "Closely intermeshing screw elements along the entire processing section ensure excellent self-wiping": khớp.
- ✓ "Các loại phần tử trục vít: vận chuyển, nhào, trộn, chặn và đẩy ngược; xi lanh có đoạn mở…": chữ trang 13 (các loại phần tử, xi lanh mở cho nạp liệu và thoát khí) và c031: khớp.
- ⚠ "Tăng áp ở cuối để đẩy nhựa qua lọc, bơm và khuôn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 41a9b8b42ae5 – screws:details[0]
> 2 trục tại Y = ±71, Z = 1 200, Ø ngoài 167,5, lõi 114,6, 2 đầu ren (2-flight).
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ≈ "2 trục tại Y = ±71 = a/2, a ≈ 142 = (D + d)/2": tính lại a/2 = 141,8/2 ≈ 71 ✓.
- ✓ "Z = 1 200: chiều cao tâm trục ZE 155 theo bảng KM": c006 quote "1.200": khớp.
- ≈ "Lõi 114,6 = D − 2h = 169 − 2 × 27,2": tính lại 169 − 2 × 27,2 = 114,6 ✓.
- ⚠ "Ø ngoài 167,5": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Ren 2 đầu (2-flight)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f92ac5ad51ff – screws:details[1]
> Trình tự phần tử (X từ–tới): −400–0 trục then hoa trong lantern; 0–1 100 vận chuyển bước 1,5D (miệng nạp 160–520); 1 100–1 560 vận chuyển bước 1,5D dưới cửa side feeder (1 180–1 520); 1 560–1 880 khối nhào KB 45°/5 (nóng chảy); 1 880–1 950 KB 90° (nút nhựa, kết thúc trước lỗ vùng 1 ở 1 990); 1 950–2 420 vận chuyển bước rộng 1,5D dưới lỗ vùng 1 (1 990–2 310); 2 420–2 900 vận chuyển 1D; 2 900–3 380 khối nhào KB 45°/5 + KB 90° (trộn); 3 380–3 620 vận chuyển 1D; 3 620–3 720 phần tử nghịch LH (nút nhựa trước vùng 2); 3 720–4 450 vận chuyển bước rộng 1,5D dưới lỗ vùng 2 (3 860–4 380); 4 450–5 746 vận chuyển 1D → 0,75D (tăng áp).
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ✓ "Các loại phần tử trong trình tự (vận chuyển nhiều bước ren, khối nhào lệch góc, phần tử …": chữ trang 13 (vận chuyển nhiều bước, khối nhào lệch góc, phần tử chặn/đẩy ngược): khớp.
- ⚠ "Toàn bộ trình tự và vị trí các phần tử trong dòng này": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 70fabc921767 – screws:details[2]
> Thấy được qua miệng nạp B1, cửa B3 và vòm B5; cho bản vẽ cắt riêng (cut-away).
- (dòng pilot do lead viết: việc kiểm không độc lập)
- ≈ "Trục vít thấy được qua các lỗ mở của mô hình: miệng nạp B1, lỗ thoát khí B3, vòm B5": c031 claim "open feed barrels, open barrels with inserts for degassing": các lỗ mở có trong catalogue; việc thấy trục vít qua lỗ là hệ quả của mô hình: ≈ đúng.

