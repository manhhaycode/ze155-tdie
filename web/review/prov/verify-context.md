# Kiểm nguồn nhóm context

Người kiểm: verify-context (agent độc lập, không phải người gắn). Ngày 2026-10-06.
Tổng: 15 dòng, 55 fact (✓ 15, ≈ 1, ⚠ 39 sau khi kiểm; trước khi kiểm: 53 fact, ✓ 14, ≈ 4, ⚠ 35). Hạ mức: 4 (3 fact ≈ → ⚠, 1 phần của fact ✓ → ⚠). Nâng mức: 1. Sửa chữ: 9.

Quy ước kiểm: mở từng ref bằng `show`, đọc ảnh web-09 và hình trang 24–25 (kể cả phóng to vùng cụm trục), đối chiếu `quote` với `text_vi`. Các claim dùng cho ✓ đều có độ tin cậy high (c035, c044); c046 (medium) và c041, c054, c006 chỉ đứng trong fact ⚠ hoặc ≈. Không có ✓ nào dựa vào claim mức low.

## Thay đổi

| Khoá | Thiết bị | Fact | Trước → sau | Lý do |
|---|---|---|---|---|
| 40a473039036 | ctx_roll_stand details[2] | "đối xứng qua Y = 0" | ✓ → ⚠ (tách khỏi fact ✓) | Ảnh web-09 chỉ cho thấy hai khung chữ C cùng dạng ở hai đầu cụm trục. Mặt Y = 0 là toạ độ riêng của mô hình, không thấy được trên ảnh. Fact ✓ còn lại chỉ nói "hai khung giống nhau, đặt ở hai đầu cụm trục". Fact ⚠ mới ghi đối xứng qua Y = 0 là do thiết kế đặt (tâm dòng chảy Y = 0, design §4.1). |
| d44c88e28cd7, 3c6e4af3f0cf, aeeac684800e | ctx_roll_bottom / middle / top details[0] | "Khe giữa–dưới ở Z = 1 200, ngang tầm trục vít" | ≈ → ⚠ | specs §4 ghi việc giữ đường chảy và môi khuôn ở 1 200 là "ước lượng, để đơn giản"; meas-5 gọi việc đặt cao độ này là giả định cho bản vẽ và sơ đồ không theo tỉ lệ. Phần đo trên hình (môi die và khe cùng độ cao) đã nằm trong fact ✓ "môi khuôn chĩa vào khe giữa–dưới", nên fact này còn lại là lựa chọn cao độ, chuyển sang ⚠ và giữ phép đo trong lý do. |
| 3e0e56adc474 | ctx_roll_stand details[0] | "dầm ngang nối hai khung" | ⚠ → tách: ✓ (thanh ngang phía trên nối hai khung) + ⚠ (dầm đặt phía sau) | Ảnh web-09 thấy rõ thanh ngang phía trên nối hai khung chữ C. Vị trí "phía sau" vẫn là lựa chọn của thiết kế. |
| 2b0e1e87a9a6 | ctx_roll_rails details[0] | chiều dài ray 2 950 | sửa chữ (⚠) | Số liệu thiết kế: ray X 9 550…12 500 = 1 650 dưới khung (đến X 11 200) + 1 300 sau mép sau khung. Chữ cũ "1 660 + 1 300" cho 2 960, lệch 10. Đã ghi lại đúng phép tính. |
| d44c88e28cd7, 3c6e4af3f0cf | ctx_roll_bottom / middle details[0] | Z = 799 / Z = 1601 | sửa chữ (⚠) | Chữ cũ "nửa khe 2 mm" mâu thuẫn với phép tính (−1 / +1). Sửa thành "nửa khe 1 mm, khe 2 mm giữa hai trục". |
| d44c88e28cd7, 3c6e4af3f0cf, aeeac684800e | roll details[0] | "Trục crôm bóng gương" | sửa chữ (✓) | Ảnh web-09 thấy rõ một trục mặt gương; số trục nhìn rõ là chưa chắc. Chữ "các trục" đổi thành "thấy rõ ở trục trong ảnh". |
| d44c88e28cd7, 3c6e4af3f0cf, aeeac684800e, bbb8eba312d1 | roll details[0], ctx_sheet details[0] | khe gió 200 | sửa chữ (⚠) | `reason_vi` nay nói thẳng 200 mm lệch khỏi ước lượng 50–150 mm của specs §6 và DECISIONS 11 chấp nhận. |
| 4555e0e84bc8, bbb8eba312d1 | ctx_sheet function, details[0] | đường chữ S | sửa chữ (✓) | Trên hình, sau trục trên tấm còn qua một con lăn nhỏ rồi mới ra +X; mô hình bỏ con lăn này. Đã ghi vào chữ của fact để ✓ không nói nhiều hơn hình. |
| 031fdbd3e579 | ctx_roll_drives function | động cơ riêng từng trục | sửa chữ (⚠) | Lý do cũ nói ảnh web-09 "không ghi chú". Ảnh thật có thấy hộp trắng và khối trụ đen giống động cơ ở đầu khung trái, nhưng không chỉ rõ mỗi trục một bộ. Giữ ⚠ và ghi đúng điều ảnh cho thấy. |
| ed0e0cccb76e | ctx_roll_* function | làm nguội tấm | sửa chữ (⚠) | Thêm lý do: c044 chỉ nói băng con lăn làm nguội đi theo trục cuối, không nói trục cán làm nguội tấm. Thêm ref c044. |
| dcb65dc98ef9 | ctx_roll_stand details[1] | chỗ lõm X 9 800 | sửa chữ (⚠) | M6 gợi ý khung bắt đầu từ X 9 600 trong Z 1 000–1 400; bản dựng dùng X 9 800, Z 1 060–1 340. Đổi "theo gợi ý M6" thành "cùng hướng với M6" kèm hai bộ số. |
| dcb65dc98ef9 | ctx_roll_stand details[1] | khe hở ≈ 280 | thêm ref (⚠) | Thêm `design-10.1` (design §10.1 ghi ≈ 300 mm) để người xem tự mở số lệch. JA của ref này nằm trong `web/prov/i18n-new/context.json`. |

## Bằng chứng từng dòng

### ed0e0cccb76e – ctx_roll_bottom / ctx_roll_middle / ctx_roll_top function
> Làm nguội và cán bóng tấm nhựa.
- ✓ "Cụm trục cán láng (smoothing roll, KM PlanetCalender) đặt ngay sau khuôn khe, cán bóng tấm nhựa": c035 quote "21 Diverter valve 22 Slot die 23 Smoothing roll" (high) khớp tên cụm. Hình trang 24–25 thấy khuôn khe (22) rồi liền cụm 3 trục (23). web-09 ghi chú "PlanetCalender – flexible polishing calender" (ảnh của KM, chính hãng của dây chuyền). c044 (high) nêu PlanetCalender có trục giữa 2.
- ⚠ "Làm nguội tấm khi tiếp xúc các trục": đã soát claims, ZE_text và images.md: chỉ có băng con lăn làm nguội sau trục cuối (c044) và ảnh web-18 của hãng khác gọi "chill roll". Không có ref nào nói cụm trục này làm nguội tấm. Lý do đúng.

### d44c88e28cd7 / 3c6e4af3f0cf / aeeac684800e – ctx_roll_bottom / middle / top details[0]
> Trục Ø800 mặt 2 600 (Y ±1 300) mạ crôm gương, cổ trục Ø300 tới Y ±1 600, tâm X = 9 776, Z = 799 / 1601 / 2403.
- ✓ "3 trục xếp chồng đứng, cùng toạ độ X; môi khuôn chĩa vào khe giữa trục giữa và trục dưới": phóng to hình trang 24–25: ba hình tròn cùng x (≈ 911, 911, 913 trên ảnh hiển thị), mũi khuôn nêm chĩa đúng vào chỗ tiếp giáp trục giữa và trục dưới, đường cam bắt đầu từ môi khuôn tại đó. meas-5: "môi die chĩa thẳng vào khe giữa trục giữa và trục dưới". c044 (high, claim nêu trục 1, 2, 3) khớp số trục.
- ✓ "Bề mặt trục crôm bóng gương": web-09, trục lớn phía trên có phản chiếu gương rõ (bóng xanh đậm, các điểm sáng). Sau khi soát: chỉ chắc một trục thấy rõ, nên đã bỏ chữ "các trục".
- ⚠ "Ø800, đầu trên của dải Ø 400–800": c046 quote "diameters between 400 – 800 mm" (SML, hãng khác, medium) và spec-6 "lấy đầu trên vì năng suất cao". Đúng là lựa chọn của thiết kế, không phải số của dây chuyền này.
- ⚠ "Mặt trục 2 600 (Y ±1 300) = 2 400 + 2 × 100": 2 400 + 200 = 2 600 ✓. spec-6 ghi "2 600 mm (ước lượng …)". c046: "widths from 1,050 – 2,200 mm", 2 600 vượt dải; lý do đã nói. Y ±1 300 = 2 600 / 2 ✓.
- ⚠ "Cổ trục Ø300 tới Y ±1 600, thò ra 300 mỗi bên": 1 600 − 1 300 = 300 ✓; profile_mm của thiết kế có bán kính 150 ở hai đầu. Không có ref nào nêu cổ trục. Lý do đúng.
- ⚠ "Tâm X = 9 776 = 9 576 + 200": 9 576 + 200 = 9 776 ✓. design-4.1 "9 576 → 9 776 · air gap 200", dec-11 "Chấp nhận khe khí 200 mm". specs §6 ước 50–150 mm theo web-18, nên 200 mm lệch; `reason_vi` nay nói rõ điều này. Không có fact nào trình bày 200 mm như số có nguồn.
- ⚠ "Khe giữa–dưới ở Z = 1 200, ngang tầm trục vít" (trước: ≈, hạ xuống ⚠): đo lại trên hình: nip y = 440,05 ≈ lip y = 440,2 pt (meas-5); melt line đồng trục với barrel (meas-5); c006 quote "ZE 155 A UTi | 169 27,2 400 2.930 2x 35.000 1.200 …", claim: trục vít cao 1 200 mm. Nhưng spec-4 gọi việc giữ 1 200 là "Ước lượng, để đơn giản", sơ đồ không theo tỉ lệ. Chuyển ⚠ (xem bảng).
- ⚠ "Z = 799 = 1 200 − 400 − 1" (bottom): 1 200 − 400 − 1 = 799 ✓. Đầu vào là các giá trị thiết kế (Ø800, khe 2 mm). Hình catalogue: bước tâm 23 / 20,8 = 1,106 ≈ 1,11 Ø ✓ (meas-5). Không có số của hãng.
- ⚠ "Z = 1601 = 1 200 + 400 + 1" (middle): 1 200 + 401 = 1 601 ✓. Lý do như trên.
- ⚠ "Z = 2403 = 1601 + 802" (top): 1 601 + 802 = 2 403 ✓; 802 = 800 + 2 ✓. Lý do như trên.
- Số của dòng gốc đều đã nằm trong text_vi của một fact (check P11 đạt).

### 031fdbd3e579 – ctx_roll_drives function
> Quay 3 trục cán.
- ✓ "Cụm cán láng KM PlanetCalender có 3 trục (trục 1 và 3 chỉnh quanh trục giữa 2)": c044 claim (high): "rolls 1 and 3 adjustable relative to central roll 2"; quote của c044 chỉ nêu "rotating the entire frame" và "the change of the central roll", nên chữ về trục 1 và 3 dựa vào claim; claim nêu trực tiếp, độ tin cậy high, và hình trang 24–25 vẽ đúng 3 trục. Đạt điều kiện ✓.
- ⚠ "Mỗi trục có một động cơ hộp số riêng": đọc web-09 phóng to: có hộp trắng và khối trụ đen giống động cơ ở đầu khung bên trái, nhưng không chỉ rõ mỗi trục một bộ; images.md cũng chỉ ghi "roll drives". Không có ref nào nêu truyền động từng trục. Lý do đã sửa cho đúng ảnh.

### b57dd10af24f – ctx_roll_drives details[0]
> 3 động cơ hộp số 450 × 600 × 500 phía −Y, đồng trục với từng trục cán.
- ≈ "3 khối nhỏ sau khung, mỗi trục một khối": đếm lại trên hình đã phóng to: có đúng 3 khối (mỗi khối gồm thân và một chốt nhỏ) ở mặt sau (+X) của khung, ngang tầm từng trục (trên, giữa, dưới). 3 ✓. meas-5: "Ba khối nhỏ trên mặt sau khung (x 644–652, mỗi trục một khối)" ✓. Hình không ghi nhãn, meas-5 nói có thể là xi lanh ép hoặc truyền động; đã nêu trong lý do.
- ⚠ "Là động cơ hộp số đặt phía −Y, đồng trục": hình là hình nhìn cạnh, ba khối lệch +X sau khung nên không cho thấy đồng trục; vị trí (9 776, −2 050, …) có trong rev-C1 ("ctx_roll_drives at (9776, −2050, 799 / 1601 / 2403)"). Lý do đúng.
- ⚠ "Cỡ 450 × 600 × 500": không có ref nào nêu kích thước; hình không theo tỉ lệ. Lý do đúng.

### 1ffdbe6b1a68 – ctx_roll_rails function
> Cho cụm trục lùi theo +X.
- ⚠ "Cụm trục lùi theo +X trên ray sàn": spec-6 "Lùi ra … chạy trên ray sàn theo X, hành trình ≈ 1 000–1 500 mm … (ước lượng)"; design-7 "Cụm trục chạy trên ray, lùi được 1 000–1 500 mm theo +X". c044 và web-09 chỉ có khung xoay quanh trục (swivel), không có ray tịnh tiến. Lý do đúng.

### 2b0e1e87a9a6 – ctx_roll_rails details[0]
> 2 ray 60 × 60 dài 2 950 tại Y = ±1 550.
- ⚠ "2 ray tại Y = ±1 550, mỗi ray dưới một khung bên (Y 1 400…1 750)": 1 550 nằm trong 1 400…1 750 ✓. rev-C1 ghi "ctx_roll_rails at Y ±1550". Không có ref công khai về ray. Lý do đúng.
- ⚠ "Tiết diện 60 × 60, dài 2 950 (X 9 550…12 500) ≈ 1 650 dưới khung + hành trình lùi ≈ 1 300": tính lại: 12 500 − 9 550 = 2 950 ✓; 11 200 − 9 550 = 1 650; 12 500 − 11 200 = 1 300; 1 650 + 1 300 = 2 950 ✓ (1 660 + 1 300 = 2 960 là lệch 10, đã sửa chữ). 1 300 nằm trong ước lượng 1 000–1 500 của spec-6.

### 5487837392f0 – ctx_roll_stand function
> Đỡ 3 trục, chỉnh khe trục, chạy trên ray để lùi xa khuôn.
- ✓ "Khung đỡ 3 trục; trục 1 và 3 chỉnh được quanh trục giữa 2": web-09 thấy rõ hai khung lớn đỡ cụm trục; c044 claim (high) "rolls 1 and 3 adjustable relative to central roll 2" nêu trực tiếp. Chữ "(chỉnh khe trục)" là cách hiểu của thiết kế về việc chỉnh vị trí trục 1 và 3 so với trục 2; đã soát, không thêm số nào.
- ⚠ "Khung chạy trên ray để lùi xa khuôn": cùng lý do với 1ffdbe6b1a68; spec-6 và design-7 đã đọc.

### 3e0e56adc474 – ctx_roll_stand details[0]
> 2 khung bên dày 350 tại Y ±(1 400…1 750), dầm ngang phía sau, xi lanh ép khe trục, dải xanh KM có chữ KraussMaffei.
- ✓ "2 khung bên đỡ các trục, như PlanetCalender của KM": web-09 hai khung chữ C lớn hai bên cụm trục. Chữ trong ngoặc đã nói khung KM hình chữ C còn mô hình dựng khung hộp.
- ✓ "Dải xanh KM có chữ KraussMaffei": web-09 thấy rõ dải xanh chéo trên khung trái, chữ "KraussMaffei" in dọc dải.
- ✓ (mới, nâng từ ⚠) "Hai khung bên được nối với nhau bằng thanh ngang phía trên": web-09 thấy thanh ngang nối hai đỉnh khung chữ C.
- ⚠ "Khung dày 350 tại Y ±(1 400…1 750)": 1 750 − 1 400 = 350 ✓. spec-6 "≈ rộng 3 800 (Y) × dài 2 500 (X) × cao 2 800 mm (ước lượng)"; mô hình dùng 3 500 × 1 660 × 3 040 (bbox 9 540…11 200, ±1 750, Z 60…3 100). Số lệch đã nêu trong `reason_vi`; không có fact ✓ nào dùng số này.
- ⚠ "Dầm ngang đặt phía sau cụm": xem bảng thay đổi.
- ⚠ "Xi lanh ép khe trục": c044 không nói cơ cấu chỉnh; meas-5 "có thể là xi lanh ép". Lý do đúng.

### dcb65dc98ef9 – ctx_roll_stand details[1]
> Mép trước khung bên ở X 9 540 … lõm vào tới X 9 800 trong dải Z 1 060–1 340 … (≈ 280 mm).
- ⚠ "Mép trước khung bên ở X 9 540, sau mặt trước các trục (X 9 376)": 9 776 − 400 = 9 376 ✓; 9 540 > 9 376 ✓.
- ⚠ "Lõm tới X 9 800 trong Z 1 060–1 340 (= 1 200 ± 140)": 1 200 − 140 = 1 060, 1 200 + 140 = 1 340 ✓. issue-3: "Khung bên cụm cán chỉ cách núm deckle 20 mm … Mép trước khung lõm tới X 9 800 … Z 1 060–1 340" ✓; rev-M6 đã đọc (gợi ý khác về số, đã sửa chữ).
- ⚠ "Khe hở ≈ 280 = 9 800 − 9 520": 9 800 − 9 520 = 280 ✓. design-7: "Thanh deckle không vượt X 9 520". design.md §10.1 ghi ≈ 300 mm; `reason_vi` nêu lệch và nay có ref `design-10.1`. Không trình bày là số có nguồn.

### 40a473039036 – ctx_roll_stand details[2]
> outline_mm là hình bên của khung +Y (Y 1 400…1 750); khung −Y đối xứng qua Y = 0.
- ✓ "Hai khung bên giống nhau, đặt ở hai đầu cụm trục": web-09 hai khung chữ C cùng dạng ở hai đầu trục (khung xa bị che một phần nhưng cung tròn và dải cùng dạng). Chỉ gắn ✓ cho điều ảnh thật sự thấy.
- ⚠ "Khung −Y là ảnh phản chiếu của khung +Y qua mặt giữa Y = 0 của mô hình": Y = 0 là toạ độ của mô hình, ảnh không thể cho thấy mặt này; design-4.1 ghi tâm dòng chảy Y = 0. Chuyển từ ✓ sang ⚠ (xem bảng).
- ⚠ "Hình bên outline_mm của khung +Y nằm ở Y 1 400…1 750": outline_mm là tên trường dữ liệu của thiết kế; issue-3 nêu lõm quanh khe trục. Lý do đúng.

### aeeac684800e – xem nhóm trục ở trên
Mọi fact của ctx_roll_top đã kiểm cùng nhóm với d44c88e28cd7 (bảng "Z = 2403 = 1601 + 802" nằm trong nhóm đó).

### 4555e0e84bc8 – ctx_sheet function
> Màn nhựa từ môi khuôn vào khe trục giữa–dưới, ôm nửa +X trục giữa, ôm nửa −X trục trên rồi ra theo +X (đường chữ S).
- ✓ "Màn nhựa vào khe giữa–dưới, ôm nửa +X trục giữa đi lên, ôm nửa −X trục trên qua đỉnh rồi ra +X (chữ S; …)": phóng to hình trang 24–25: đường cam đi ra từ môi khuôn vào chỗ tiếp giáp trục giữa và dưới, vòng qua phía +X của trục giữa lên trên, qua giữa trục giữa và trục trên, ôm phía −X của trục trên và qua đỉnh, xuống một con lăn nhỏ rồi ra +X. meas-5 "Tấm nhựa ôm nửa phải trục giữa đi lên, ôm trục trên phía trái và qua đỉnh, sang một con lăn nhỏ" ✓. Hình có thêm con lăn nhỏ; mô hình bỏ qua, đã ghi trong chữ.

### bbb8eba312d1 – ctx_sheet details[0]
> Tấm rộng 2 100, dày 1 mm; đường tâm trong path_mm …
- ✓ "Màn nhựa vào khe giữa–dưới … (chữ S)": như trên.
- ⚠ "Tấm rộng 2 100, đối xứng qua Y = 0": spec-0 "Tấm thành phẩm rộng 2 100 mm … — ước lượng". c046 "widths from 1,050 – 2,200 mm" (2 100 nằm trong dải); c041 "widths from 2 to 7.5 m" ✓. Giữ ⚠.
- ⚠ "Tấm dày 1 mm": spec-0 "dày 0,3–1,5 mm … ước lượng"; c041 "thicknesses from 0.1 to 6 mm" ✓ khớp. Giữ ⚠.
- ⚠ "Môi khuôn (9 576, 1 200) → khe trục (9 776, 1 200): khe gió 200": 9 776 − 9 576 = 200 ✓. Lệch ước 50–150 của specs §6; đã nói rõ.
- ⚠ "Đỉnh trục giữa Z 2 002 = 1601 + 400 + 1; X 9 375 = 9 776 − 400 − 1; Z 2 804 = 2403 + 400 + 1": 1 601 + 401 = 2 002 ✓; 9 776 − 401 = 9 375 ✓; 2 403 + 401 = 2 804 ✓. Khớp path_mm của thiết kế (đỉnh 2002, 2804, X 9375). rev-M7 ghi cửa ra Z 2803, đường tấm dùng 2804 (cách mặt trục 1 mm); không đưa 2803 như số có nguồn.

### 09f404be3be8 – ctx_sheet details[1]
> Đầu đo chiều dày quét ngang (traversing gauge) … không dựng.
- ⚠ "Đầu đo chiều dày quét ngang đặt sau cụm trục": đã tìm "gauge", "traversing", "thickness" trong claims, specs, ZE_text và images.md: không có tài liệu nào. rev-M7 nêu "automatic thermal-bolt profile control also needs a traversing thickness gauge"; c054 chỉ là thông số bulông nhiệt, không nói đầu đo. design-7 ghi "không dựng". Lý do đúng.
