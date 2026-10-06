# Kiểm nguồn nhóm die

Người kiểm: lead (Opus, làm tại chỗ). Hạn mức Sonnet hết giữa chừng nên người dùng chọn để lead tự kiểm; lead không gắn nhóm này. Ngày 2026-10-06.
Tổng: 51 dòng, 111 fact (✓ 25, ≈ 12, ⚠ 74 sau khi kiểm). Hạ mức (cả lượt kiểm trước nếu có): 0. Nâng mức: 0. Sửa chữ hoặc tách fact: 2.

Hình đã mở: web-07, web-08, web-17, web-18, web-19, web-20, crop trang 24–25 (khuôn khe và cụm trục). Claim đã đọc: c035, c053–c058. Các phép tính đã làm lại: √(98² + 139²) = 170,1 và arctan(98/139) = 35,2°; 2 400 / 25,4 = 94,5 → 94, y cuối = −1 181 + 93 × 25,4 = 1 181,2; 94 × 330 kN = 31,0 MN, 31 / 7,2 = 4,3; 2,4 × 0,3 × 10 = 7,2 MN; 32,8 / 1,575 × 2,4 = 50 kW; 0,040″ × 25,4 = 1,02 mm; 9 900 − 9 576 = 324; 32 × 75 = 2 400. Số trong bản tiếng Nhật khớp bản tiếng Việt (kiểm bằng máy).

Ghi chú cho người thiết kế (không đổi mức): thanh deckle trong dòng ghi Ø30 nhưng parts.json là Ø40; bulông nhiệt Ø30 lớn hơn bước 25,4 (chồng 4,6 mm nếu là đường kính ngoài); khối đầu nối tấm đầu 6 lỗ trong khi ảnh hãng khác có 2 × 5 = 10; khối lượng khuôn 3,4 t (review I3) so với ≈ 2 t (specs) và ≈ 1 t (Cloeren 62″, c055); web-08 dùng bánh tự do không có ray; web-07 có 2 tai cẩu giữa mặt đỉnh, thiết kế đặt 4 ở tấm đầu.

## Thay đổi

| Khoá | Thiết bị | Fact | Trước → sau | Lý do |
|---|---|---|---|---|
| e25572f863a4, 63454c318d31 | die_body_lower, die_body_upper | 1 | chữ (✓ giữ nguyên) | c058 nói dầu 4 vùng cộng thêm thanh nhiệt cắm; chữ cũ chỉ nói thanh nhiệt cắm |
| 83d2c40b3839 | die_choker_bolts | 0 | chữ (≈ giữ nguyên) | ảnh không cho thấy thanh chắn, bỏ "ngay trên thanh chắn" khỏi fact ≈ (đã có trong fact ⚠ 1) |

## Bằng chứng từng dòng

### 1640fe9c1ce9 – die_body_bolts:function
> Kẹp hai nửa khuôn vào nhau, chịu lực tách ≈ 7 MN do áp nhựa trong ống phân phối và preland.
- ✓ "Thân khuôn tấm gồm nhiều phần ghép với nhau (Reifenhäuser: thân 2–5 phần, môi mềm ở nửa …": c056 (high) quote "2-5 part die body with flex lip in upper die body": khớp (W1 3 500 là dải bề rộng, không liên quan).
- ⚠ "Lực tách ≈ 7 MN ≈ 2,4 m × 0,3 m × 10 MPa (= 7,2 MN)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4cbc4d4be0f5 – die_body_bolts:details[0]
> 94 vít lục giác chìm M30 cấp 10.9 dài 260, đầu Ø45 nằm chìm trong lỗ khoét bậc Ø48 × 32 (mặt khuôn phẳng); positions_mm là tâm đầu vít (đầu cao 30).
- ⚠ "94 vít lục giác chìm M30 cấp 10.9, dài 260": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đầu Ø45 chìm trong lỗ khoét bậc Ø48 × 32 (mặt khuôn phẳng); đầu cao 30": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7244bdbdb892 – die_body_bolts:details[1]
> Mặt đỉnh nửa trên: hàng X 9 160 (24 vít, Y = −1 265 … +1 265 bước 110) và hàng X 9 210 (23 vít, Y = −1 210 … +1 210), cả hai nằm sau hàng bulông thanh chắn (X 9 240–9 270) và máng bulông nhiệt (X 9 285–9 345).
- ⚠ "Hai hàng vít mặt đỉnh nửa trên: X 9 160 (24 vít, Y ±1 265, bước 110) và X 9 210 (23 vít,…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 96ef01f4c947 – die_body_bolts:details[2]
> Mặt đáy nửa dưới: hàng X 9 160 (23 vít, Y = −1 210 …) và hàng X 9 270 (24 vít, Y = −1 265 …), tức cách mép trước mặt đáy (X 9 330) 170 và 60 mm.
- ⚠ "Hai hàng vít mặt đáy nửa dưới: X 9 160 (23 vít, Y ±1 210) và X 9 270 (24 vít, Y ±1 265),…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 03288894b5c7 – die_body_bolts:details[3]
> Vít từ trên ren vào nửa dưới, vít từ dưới ren vào nửa trên; các hàng lệch nhau 55 mm theo Y nên thân vít đi song song không chạm nhau.
- ⚠ "Các hàng lệch nhau 55 mm theo Y (= nửa bước 110) nên thân vít từ trên và từ dưới đi song…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b6ed7bb7b225 – die_body_bolts:details[4]
> Lực kẹp ≈ 94 × 330 kN ≈ 31 MN, gấp ≈ 4 lần lực tách; ống phân phối (G) phải đi giữa và trước các hàng vít (xem design.md §9).
- ⚠ "Lực kẹp ≈ 94 × 330 kN ≈ 31 MN, gấp ≈ 4 lần lực tách (31 / 7,2 ≈ 4,3)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Ống phân phối (G) phải đi giữa và trước các hàng vít": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 394abcf27fe3 – die_body_lower:function
> Nửa dưới ống phân phối, môi dưới thay được.
- ✓ "Khuôn tấm có ống phân phối móc áo (coat-hanger) và môi tháo thay được (Nordson EDI)": c057 (high) quote "Autoflex™ automatic or manual lip adjustment" và "Multiflow™ … coathanger-shaped manifold"; môi tháo được, deckle trong/ngoài, xe khuôn, thanh chắn tuỳ chọn nằm trong claim (high, nói thẳng): khớp.
- ⚠ "Nửa dưới mang nửa dưới của ống phân phối; mặt phân khuôn nằm ngang tại Z 1 200": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e25572f863a4 – die_body_lower:details[0]
> Cao 250 (Z 950–1 200); 9 vùng thanh nhiệt.
- ⚠ "Cao 250 (Z 950–1 200): mặt phân khuôn ở Z 1 200 = cao độ trục vít": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ✓ "Khuôn khe KM (dây chuyền xốp) gia nhiệt bằng dầu 4 vùng cộng thêm thanh nhiệt cắm (cartr…": c058 (medium) quote "The 4-zone oil temperature control system and additional cartridge heaters provide … heating or cooling of the slot die": khớp chữ đã sửa.
- ⚠ "9 vùng thanh nhiệt mỗi nửa (bước ≈ 270, 2 400 / 270 ≈ 9)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c7ec5e746502 – die_body_lower:details[1]
> Môi dưới (lower lip) là thanh chèn thay được dọc mũi, X 9 446–9 576 × cao 60, bắt 24 vít M12 lục giác chìm từ mặt vát dưới (bước 100).
- ✓ "Môi khuôn tháo thay được (removable lips)": c057 (high) quote "Autoflex™ automatic or manual lip adjustment" và "Multiflow™ … coathanger-shaped manifold"; môi tháo được, deckle trong/ngoài, xe khuôn, thanh chắn tuỳ chọn nằm trong claim (high, nói thẳng): khớp.
- ⚠ "Thanh môi dưới X 9 446–9 576 × cao 60, bắt 24 vít M12 lục giác chìm từ mặt vát dưới, bướ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4c07e3e71b8c – die_body_upper:function
> Nửa trên ống phân phối móc áo (coat-hanger manifold), mang môi mềm, thanh chắn và bulông chỉnh.
- ✓ "Khuôn tấm có ống phân phối móc áo (coat-hanger manifold)": c057 (high) quote "Autoflex™ automatic or manual lip adjustment" và "Multiflow™ … coathanger-shaped manifold"; môi tháo được, deckle trong/ngoài, xe khuôn, thanh chắn tuỳ chọn nằm trong claim (high, nói thẳng): khớp.
- ✓ "Môi mềm nằm trong nửa trên thân khuôn (Reifenhäuser)": c056 (high) quote "2-5 part die body with flex lip in upper die body": khớp (W1 3 500 là dải bề rộng, không liên quan).
- ✓ "Thanh chắn (choker bar) đặt trước môi mềm để chỉnh thô; bulông chỉnh môi cách nhau ≈ 25 mm": c053 (high) quote "die lip bolts, which are generally spaced about 25 mm apart"; thanh chắn trước môi để chỉnh thô nằm trong claim (high, nói thẳng): khớp.

### 991bac395012 – die_body_upper:details[0]
> Rộng 2 600 (Y ±1 300), cao 250 (Z 1 200–1 450), sâu 450 (X 9 126–9 576), mũi vát 30° về phía khe trục.
- ⚠ "Rộng 2 600 (Y ±1 300) = môi 2 400 + 2 × 100": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Cao 250 (Z 1 200–1 450), sâu 450 (X 9 126–9 576)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ✓ "Thân khuôn thu nhọn dạng nêm về phía môi, mũi chĩa vào khe giữa các trục cán (sơ đồ cata…": crop trang 24–25: khuôn (22) hình nêm, mũi chĩa vào khe giữa các trục (23): thấy rõ; c035 quote "22 Slot die 23 Smoothing roll" cho tên gọi.
- ⚠ "Mũi vát 30° về phía khe trục": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 63454c318d31 – die_body_upper:details[1]
> Mạ crôm bóng; 9 vùng thanh nhiệt cắm từ mặt sau.
- ⚠ "Mạ crôm bóng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ✓ "Khuôn khe KM (dây chuyền xốp) gia nhiệt bằng dầu 4 vùng cộng thêm thanh nhiệt cắm (cartr…": như trên (c058).
- ⚠ "9 vùng thanh nhiệt cắm từ mặt sau (bước ≈ 270)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6937b6e03651 – die_body_upper:details[2]
> Rãnh bản lề môi mềm (flex-lip hinge slot) hở, chạy suốt bề rộng 2 400 tại X 9 392–9 404 (rộng 12), cắt từ mặt vát xuống tới Z 1 212, để lại gân bản lề dày 12 mm trên mặt chảy (Z 1 200); phần sau rãnh là môi mềm. Đầu bulông nhiệt tì lên môi tại X 9 440, cách gân 36 mm.
- ✓ "Hàng bulông chỉnh môi (cách nhau ≈ 25 mm) tác động lên môi mềm của khuôn tấm": c053 (high) quote "die lip bolts, which are generally spaced about 25 mm apart"; thanh chắn trước môi để chỉnh thô nằm trong claim (high, nói thẳng): khớp.
- ⚠ "Rãnh bản lề hở tại X 9 392–9 404 (rộng 12), cắt từ mặt vát xuống Z 1 212, chừa gân dày 1…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Rãnh chạy suốt bề rộng môi 2 400": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đầu bulông nhiệt tì lên môi tại X 9 440, cách gân 36 mm = 9 440 − 9 404": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 6d29e3fa00bd – die_body_upper:details[3]
> Mặt đỉnh từ sau ra trước: hộp nhiệt mặt sau (X ≤ 9 126), tai cẩu ở tấm đầu, hàng bulông thanh chắn X 9 255 (thanh chắn trong thân X 9 240–9 270), máng bulông nhiệt X 9 285–9 345, rồi mặt vát mang 94 bulông nhiệt.
- ≈ "Trên khuôn tấm hãng khác, hàng bulông thanh chắn nằm trên mặt đỉnh phía sau, hàng bulông…": web-19, web-20 (Taizhou Jingyue, hãng khác, nên ≈): hàng bulông đầu đen đứng trên mặt đỉnh phía sau, hàng bulông chỉnh môi trên mặt vát phía trước: thấy rõ.
- ⚠ "Từ sau ra trước: hộp nhiệt X ≤ 9 126, tai cẩu ở tấm đầu, bulông thanh chắn X 9 255 (than…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 76582454c207 – die_bolt_actuator_rail:function
> Gom cáp 94 thanh nhiệt bulông và dẫn gió làm mát bulông.
- ⚠ "94 thanh nhiệt = 94 bulông nhiệt (2 400 / 25,4 làm tròn xuống), mỗi bulông một thanh gia…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "Cáp của bulông nhiệt và ống gió làm mát chạy dọc hàng bulông nhiệt trên môi": web-17 (SBI, hãng khác, nên ≈): cáp xám dọc hàng bulông; web-18: ống gió nối vào máng trên hàng bulông: thấy rõ.

### f6629fff8666 – die_bolt_actuator_rail:details[0]
> Máng inox 60 × 90 dài 2 500 trên dải trước của mặt đỉnh (X 9 285–9 345), ngay sau đầu trên các bulông nhiệt; trong máng: cáp 94 thanh nhiệt (tầng trên) và ống gió làm mát (tầng dưới).
- ⚠ "Máng inox 60 × 90 dài 2 500 tại X 9 285–9 345, ngay sau đầu trên các bulông nhiệt; chứa …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d7993c2292f4 – die_bolt_actuator_rail:details[1]
> 2 ổ cắm nhiều chân đánh số ở đầu −Y; nắp máng tháo được để chừa lối vặn bulông thanh chắn ngay phía sau.
- ≈ "2 ổ cắm nhiều chân đánh số 1 và 2 ở đầu hàng cáp (đếm trên ảnh web-17)": web-17 (SBI, hãng khác, nên ≈): hai phích nhiều chân ghi số 1 và 2: đếm được 2.
- ⚠ "Ổ cắm đặt ở đầu −Y; nắp máng tháo được để chừa lối vặn bulông thanh chắn ngay phía sau": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d5b2340d1785 – die_cable_harness:function
> Dẫn cáp bulông nhiệt và cảm biến khuôn xuống hộp đấu dây khuôn; rút phích ra khi kéo khuôn đi.
- ≈ "Khuôn có bulông nhiệt tự động dùng cáp xám có phích nhiều chân đánh số, rút cắm được (ản…": web-17 (SBI, hãng khác, nên ≈): cáp xám đầu phích nhiều chân đánh số: thấy rõ.
- ⚠ "Bó cáp dẫn xuống hộp đấu dây khuôn; rút phích ra khi kéo khuôn đi": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c851bbefcdab – die_cable_harness:details[0]
> Ống luồn cáp mềm Ø60 đi xuống phía −Y rồi chéo về nóc hộp đấu dây khuôn; 2 phích nhiều chân đánh số ở đầu hộp.
- ⚠ "Ống luồn cáp mềm Ø60 đi xuống phía −Y rồi chéo về nóc hộp đấu dây khuôn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "2 phích nhiều chân đánh số ở đầu hộp (đếm 2 phích số 1 và 2 trên ảnh web-17)": web-17 (SBI, hãng khác, nên ≈): đếm được 2 phích số 1 và 2.

### de3fd7e85c5b – die_cart:function
> Đỡ khuôn ≈ 3,4 t, chỉnh cao ±50 mm bằng kích vít, tự do ±40 mm theo X (giãn nở), kéo khuôn ra theo +Y trên ray.
- ✓ "Khuôn tấm KM đặt trên xe khuôn (die cart) có bánh và cột chỉnh cao": web-08 (KM): khuôn đặt trên xe có 4 bánh tự do (castor) và hai cột ren chỉnh cao: thấy rõ. c057 claim "die carts": khớp.
- ⚠ "Khối lượng khuôn ≈ 3,4 t": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Chỉnh cao ±50 mm bằng kích vít": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tự do ±40 mm theo X (giãn nở): giãn tại khuôn ≈ 28 mm = 17 (xi lanh) + 10 (đường chảy)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Kéo khuôn ra theo +Y trên ray": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1a5a00936cfb – die_cart:details[0]
> Đế thép hộp rộng X 8 700–9 380, Z 60–300, luồn dưới bộ trộn và bích khuôn; 4 bánh: 2 bánh trụ trên ray phẳng X 8 760, 2 bánh rãnh V trên ray dẫn hướng X 9 320 (khổ 560).
- ✓ "Xe khuôn KM có đế khung rộng đặt trên bánh xe": web-08 (KM): khuôn đặt trên xe có 4 bánh tự do (castor) và hai cột ren chỉnh cao: thấy rõ.
- ⚠ "Đế thép hộp rộng X 8 700–9 380, Z 60–300, luồn dưới bộ trộn và bích khuôn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "4 bánh: 2 bánh trụ trên ray phẳng X 8 760, 2 bánh rãnh V trên ray dẫn hướng X 9 320 (khổ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 10c4750cce5b – die_cart:details[1]
> Hai cột kích vít có tay quay ở X 9 150–9 350, xà đỡ trên có bàn trượt ±40 mm theo X và 2 đệm tại Y = ±700.
- ✓ "Xe khuôn KM nâng khuôn bằng cột có trục vít (kích vít)": web-08 (KM): khuôn đặt trên xe có 4 bánh tự do (castor) và hai cột ren chỉnh cao: thấy rõ.
- ⚠ "2 cột kích vít có tay quay ở X 9 150–9 350; xà đỡ trên có bàn trượt ±40 mm theo X và 2 đ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### ad0c8bfa3e55 – die_cart:details[2]
> Phía trước đế không vượt X 9 380 dưới Z 600 (trục dưới ở X ≥ 9 429 tại Z 600); khoá bánh khi chạy.
- ⚠ "Phía trước đế không vượt X 9 380 dưới Z 600, vì trục dưới ở X ≥ 9 429 tại Z 600 (khe 49 …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Khoá bánh khi chạy (khoá sàn ở vị trí làm việc)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a781ea8512b1 – die_cart:details[3]
> Phải lùi cụm trục cán trước khi kéo khuôn ra theo +Y.
- ⚠ "Phải lùi cụm trục cán trước khi kéo khuôn ra theo +Y": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b450737aa45f – die_cart_rails:function
> Dẫn xe khuôn ra phía +Y khi bảo trì.
- ⚠ "Dẫn xe khuôn ra phía +Y khi bảo trì": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f901eebfafc7 – die_cart_rails:details[0]
> 2 ray dài 4 300 theo Y: ray phẳng tại X 8 760, ray có gờ dẫn hướng tại X 9 320 (khổ 560); khoá sàn ở vị trí làm việc.
- ⚠ "2 ray dài 4 300 theo Y: ray phẳng X 8 760, ray dẫn hướng X 9 320 (khổ 560); khoá sàn ở v…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 80f4064326e6 – die_choker_bolts:function
> Chỉnh thô dòng chảy ngang khuôn qua thanh chắn (restrictor bar) nằm sau ống phân phối, trước vùng preland.
- ✓ "Thanh chắn (choker bar) nằm trước môi mềm, dùng chỉnh thô; bulông chỉnh môi cách nhau ≈ …": c053 (high) quote "die lip bolts, which are generally spaced about 25 mm apart"; thanh chắn trước môi để chỉnh thô nằm trong claim (high, nói thẳng): khớp. c057 (high) quote "Autoflex™ automatic or manual lip adjustment" và "Multiflow™ … coathanger-shaped manifold"; môi tháo được, deckle trong/ngoài, xe khuôn, thanh chắn tuỳ chọn nằm trong claim (high, nói thẳng): khớp.
- ⚠ "Thanh chắn nằm sau ống phân phối, trước vùng preland": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 83d2c40b3839 – die_choker_bolts:details[0]
> 33 bulông đầu đen Ø30 cao 80 đặt đứng trên mặt đỉnh tại X 9 255, ngay trên thanh chắn (X 9 240–9 270), Y = −1 200 + 75·k (k = 0…32), đai ốc khoá; bulông đẩy/kéo thẳng thanh chắn như khuôn môi mềm thông thường.
- ≈ "Hàng bulông đầu đen đặt đứng trên mặt đỉnh nửa trên, phía sau hàng bulông chỉnh môi (qua…": web-19, web-20 (Taizhou Jingyue, hãng khác, nên ≈): hàng bulông đầu đen đứng trên mặt đỉnh, sau hàng bulông chỉnh môi: thấy rõ; chữ đã bỏ phần "trên thanh chắn" vì ảnh không cho thấy.
- ⚠ "33 bulông Ø30 cao 80 tại X 9 255, trên thanh chắn X 9 240–9 270; Y = −1 200 + 75·k (k = …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đai ốc khoá; bulông đẩy/kéo thẳng thanh chắn như khuôn môi mềm thông thường": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9234e1cd5dd9 – die_choker_bolts:details[1]
> Vặn bằng khẩu từ trên xuống; khe 15 mm tới máng bulông nhiệt phía trước (X 9 285).
- ⚠ "Khe 15 mm = 9 285 − 9 270 tới máng bulông nhiệt phía trước (X 9 285); vặn bằng khẩu từ t…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9e9f98acc99a – die_deckles:function
> Thu hẹp bề rộng màn nhựa ở hai đầu khi đổi khổ tấm.
- ✓ "Khuôn tấm có deckle trong và ngoài (internal/external deckles); ảnh KM có thanh deckle n…": c057 (high) quote "Autoflex™ automatic or manual lip adjustment" và "Multiflow™ … coathanger-shaped manifold"; môi tháo được, deckle trong/ngoài, xe khuôn, thanh chắn tuỳ chọn nằm trong claim (high, nói thẳng): khớp. web-07: thanh đen nhô ra ở hai đầu khuôn: thấy rõ.
- ⚠ "Deckle thu hẹp bề rộng màn nhựa ở hai đầu khi đổi khổ tấm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c380bd0c906d – die_deckles:details[0]
> Mỗi đầu 1 thanh Ø30 nhô 150 ngoài tấm đầu (tới |Y| 1 525) tại X 9 480, có núm vặn + thước; lưỡi deckle trong nằm trong khuôn, không vượt X 9 520 (tránh khung cụm trục).
- ✓ "Mỗi đầu khuôn có 1 thanh deckle nhô ra ngoài tấm đầu (ảnh KM)": web-07 (KM): mỗi đầu khuôn một thanh đen nhô ra ngoài tấm đầu: thấy rõ.
- ⚠ "Thanh Ø30 nhô 150 ngoài tấm đầu (tới |Y| 1 525 = 1 375 + 150) tại X 9 480": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Có núm vặn + thước; lưỡi deckle trong nằm trong khuôn, không vượt X 9 520 (tránh khung c…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 112b8899e7cf – die_drip_pan:function
> Hứng nhựa rơi khi khởi động màn nhựa.
- ⚠ "Khay đặt dưới môi để hứng nhựa rơi khi khởi động màn nhựa": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e26e4beda322 – die_drip_pan:details[0]
> Khay inox 324 × 2 700 cao 80.
- ⚠ "Khay inox 324 × 2 700 cao 80 (X 9 576–9 900, Y ±1 350)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### ccb3394ec07d – die_end_plate_op:function, die_end_plate_rear:function
> Bịt hai đầu ống phân phối, mang thanh deckle và hộp đấu nhiệt tấm đầu.
- ✓ "Hai đầu khuôn có tấm đầu (end plate) mang thanh deckle nhô ra (ảnh KM); Nordson có deckl…": web-07: tấm đầu ở hai đầu khuôn mang thanh nhô ra; c057 (high) quote "Autoflex™ automatic or manual lip adjustment" và "Multiflow™ … coathanger-shaped manifold"; môi tháo được, deckle trong/ngoài, xe khuôn, thanh chắn tuỳ chọn nằm trong claim (high, nói thẳng): khớp.
- ≈ "Tấm đầu mang khối đầu nối nhiệt (terminal block) có nhiều lỗ (ảnh khuôn hãng khác)": web-19, web-20 (Taizhou Jingyue, hãng khác, nên ≈): khối đầu nối nhiều lỗ (2 × 5) ở mỗi tấm đầu: thấy rõ.
- ⚠ "Tấm đầu bịt hai đầu ống phân phối": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b32defec3e5c – die_end_plate_op:details[0], die_end_plate_rear:details[0]
> Tấm thép 75 mm, khối đầu nối thanh nhiệt (terminal block) 6 lỗ, 1 vùng nhiệt.
- ⚠ "Tấm thép dày 75 mm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Khối đầu nối thanh nhiệt (terminal block) 6 lỗ": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "1 vùng nhiệt trên mỗi tấm đầu (20 vùng = 9 + 9 + 2 tấm đầu)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f1a4b4879ce6 – die_flex_lip:function
> Chỉnh khe môi cục bộ (hành trình ≈ 1–2,5 mm) để đều chiều dày tấm.
- ✓ "Chỉnh khe môi cục bộ bằng hàng bulông chỉnh môi (cách ≈ 25 mm); hệ chỉnh môi là điều khi…": c053 (high) quote "die lip bolts, which are generally spaced about 25 mm apart"; thanh chắn trước môi để chỉnh thô nằm trong claim (high, nói thẳng): khớp. c057 (high) quote "Autoflex™ automatic or manual lip adjustment" và "Multiflow™ … coathanger-shaped manifold"; môi tháo được, deckle trong/ngoài, xe khuôn, thanh chắn tuỳ chọn nằm trong claim (high, nói thẳng): khớp.
- ≈ "Hành trình ≈ 1–2,5 mm: 0,040″ × 25,4 = 1,02 mm (Cloeren) đến 2,5 mm (Reifenhäuser)": tính lại 0,040 × 25,4 = 1,016 mm (c055 quote "0.040″ flex adjustment"); 2,5 mm từ c056 quote "adjustable range of 2.5 mm": ✓.

### 741321a5a47c – die_flex_lip:details[0]
> Dải môi rộng 2 400, khe làm việc 0,5–2 mm tại Z = 1 200, X = 9 576; là phần mũi của nửa trên phía sau rãnh bản lề hở (X 9 392–9 404, suốt bề rộng, gân 12 mm).
- ✓ "Môi mềm nằm trong nửa trên thân khuôn, là phần mũi của nửa trên (Reifenhäuser)": c056 (high) quote "2-5 part die body with flex lip in upper die body": khớp (W1 3 500 là dải bề rộng, không liên quan).
- ⚠ "Dải môi rộng 2 400": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Khe làm việc 0,5–2 mm tại Z = 1 200, X = 9 576 (= 9 126 + 450)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Sau rãnh bản lề hở X 9 392–9 404, suốt bề rộng, gân 12 mm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c25ba16480ba – die_flex_lip:details[1]
> Bulông nhiệt bắc qua rãnh (ren trong thân phía trước rãnh), đầu bulông tì lên môi tại X 9 440 (cách gân 36 mm), nên môi uốn quanh gân.
- ✓ "Hàng bulông chỉnh môi cách nhau ≈ 25 mm; bulông nhiệt tự động bước 25,4 mm, thanh gia nh…": c053 (high) quote "die lip bolts, which are generally spaced about 25 mm apart"; thanh chắn trước môi để chỉnh thô nằm trong claim (high, nói thẳng): khớp. c054 (high) quote "Division (bolt spacing) | 30, 28, 25.4 mm (1″)"; 80 W và hành trình 300 µm nằm trong claim (high): khớp.
- ⚠ "Bulông nhiệt bắc qua rãnh (ren trong thân phía trước rãnh), đầu tì lên môi tại X 9 440, …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 905f0498f7a6 – die_heater_boxes:function
> Đấu dây 20 vùng nhiệt khuôn (≈ 50 kW).
- ⚠ "20 vùng nhiệt khuôn = 9 + 9 + 2 tấm đầu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Công suất ≈ 50 kW: 32,8 kW / 1,575 m ≈ 21 kW/m, nhân bề rộng môi 2,4 m (21 × 2,4 ≈ 50)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1eff208002ba – die_heater_boxes:details[0]
> 2 hộp dài (trên Z 1 330–1 440, dưới Z 960–1 070) chạy Y ±1 250, chừa giữa ±260 cho bích vào; tem cảnh báo vàng.
- ≈ "2 hộp nhiệt inox dài xếp trên và dưới, có tem cảnh báo vàng (đếm trên ảnh web-17)": web-17 (SBI, hãng khác, nên ≈): hai hộp lưới inox xếp chồng có tem tam giác vàng ở phía cấp nhựa: đếm được 2.
- ⚠ "Hộp trên Z 1 330–1 440, hộp dưới Z 960–1 070, chạy Y ±1 250, chừa giữa ±260 cho bích vào": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 598f42a0ee60 – die_heater_conduit:function
> Dẫn cáp 20 vùng nhiệt khuôn từ hộp đầu nối tới hộp đấu dây khuôn; có phích cắm để tách khuôn.
- ⚠ "20 vùng nhiệt khuôn = 9 + 9 + 2 tấm đầu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Ống luồn dẫn cáp từ hộp đầu nối tới hộp đấu dây khuôn, có phích cắm để tách khuôn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 14e3c8bf0e23 – die_heater_conduit:details[0]
> Ống mềm kim loại Ø40.
- ⚠ "Ống mềm kim loại Ø40": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d0a2ad9efc89 – die_junction_box:function
> Tập trung cáp nhiệt khuôn (20 vùng), 94 mạch bulông nhiệt, cảm biến; phích cắm để tách khuôn; nút dừng khẩn.
- ⚠ "20 vùng nhiệt khuôn = 9 + 9 + 2 tấm đầu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "94 mạch bulông nhiệt = 94 bulông (2 400 / 25,4 làm tròn xuống), mỗi bulông có thanh 80 W…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "Phích nhiều chân đánh số để tách khuôn (ảnh web-17)": web-17 (SBI, hãng khác, nên ≈): cáp kết thúc bằng phích nhiều chân đánh số: thấy rõ.
- ⚠ "Tập trung cả cáp cảm biến khuôn; có nút dừng khẩn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### fd1743a2ed52 – die_junction_box:details[0]
> Tủ đứng RAL 7035 600 × 300 × 1 000 trên sàn, cửa hướng +Y, đặt ngoài ray xe khuôn để không đi theo xe.
- ⚠ "Tủ đứng RAL 7035 600 × 300 × 1 000 trên sàn, cửa hướng +Y, đặt ngoài ray xe khuôn để khô…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b94886ab16e5 – die_junction_box:details[1]
> Nóc: 2 ổ cắm nhiều chân cho bó cáp bulông nhiệt, 1 ổ cho cáp nhiệt khuôn; nút dừng khẩn đỏ trên cửa.
- ≈ "2 ổ cắm nhiều chân cho bó cáp bulông nhiệt (đếm 2 phích trên ảnh web-17; review I6 dùng …": web-17 (SBI, hãng khác, nên ≈): đếm 2 phích; rev-I6 dùng cùng số.
- ⚠ "1 ổ cho cáp nhiệt khuôn; nút dừng khẩn đỏ trên cửa": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 563259d6b304 – die_lifting_lugs:function
> Cẩu khuôn khi lắp/tháo.
- ✓ "Khuôn khe KM có tai cẩu dạng vòng trên mặt đỉnh để nâng khuôn": web-07 (KM): hai tai cẩu dạng vòng trên mặt đỉnh khuôn khe: thấy rõ.

### 4c3a618a552d – die_lifting_lugs:details[0]
> 4 tai cẩu M36 cao 130, 2 trên mỗi tấm đầu tại X 9 190 và 9 470, |Y| = 1 337 (ngoài mặt trục ±1 300, trước cổ trục X ≥ 9 626).
- ✓ "Ảnh KM thấy 2 tai cẩu dạng vòng trên khuôn khe": như trên: đếm được 2 tai cẩu trên ảnh web-07.
- ⚠ "4 tai cẩu M36 cao 130, 2 trên mỗi tấm đầu tại X 9 190 và 9 470": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "|Y| = 1 337 = (1 300 + 1 375)/2, ngoài mặt trục ±1 300 và trước cổ trục X ≥ 9 626": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e83fcd682043 – die_thermal_bolts:function
> Đẩy môi mềm theo điều khiển tự động (giãn nở nhiệt), chỉnh profin chiều dày ngang tấm.
- ✓ "Bulông nhiệt (thermal bolt) là bulông chỉnh môi tự động: bước 25,4 mm, thanh gia nhiệt 8…": c054 (high) quote "Division (bolt spacing) | 30, 28, 25.4 mm (1″)"; 80 W và hành trình 300 µm nằm trong claim (high): khớp.
- ✓ "Chỉnh môi tự động là hệ điều khiển chiều dày (gauge control) của khuôn tấm": c057 (high) quote "Autoflex™ automatic or manual lip adjustment" và "Multiflow™ … coathanger-shaped manifold"; môi tháo được, deckle trong/ngoài, xe khuôn, thanh chắn tuỳ chọn nằm trong claim (high, nói thẳng): khớp.
- ⚠ "Bulông giãn nở khi nóng và đẩy môi mềm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c0ef067bde88 – die_thermal_bolts:details[0]
> 94 bulông, y = −1 181 + 25,4·k (k = 0…93); mỗi bulông Ø30 (thân Ø16 trong ống gia nhiệt 80 W) dài 170, trục từ (9 440, y, 1 295) tới (9 342, y, 1 434), tức 35° so với phương đứng, nằm dọc mặt vát của nửa trên.
- ✓ "Bước 25,4 mm (1″), mỗi bulông có thanh gia nhiệt 80 W": c054 (high) quote "Division (bolt spacing) | 30, 28, 25.4 mm (1″)"; 80 W và hành trình 300 µm nằm trong claim (high): khớp.
- ⚠ "94 bulông = 2 400 / 25,4 làm tròn xuống; y = −1 181 + 25,4·k (k = 0…93), phủ y từ −1 181…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Mỗi bulông Ø30 (thân Ø16 trong ống gia nhiệt 80 W), dài 170": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Trục từ (9 440, y, 1 295) tới (9 342, y, 1 434): dài √(98² + 139²) ≈ 170, nghiêng arctan…": tính lại √(98² + 139²) = 170,1, arctan(98/139) = 35,2°: ✓ (vẫn ⚠ vì toạ độ do thiết kế).
- ≈ "Bulông nằm dọc mặt vát của nửa trên, thành một hàng suốt bề rộng (quan sát ảnh SBI)": web-17 (SBI, hãng khác, nên ≈): hàng bulông nhiệt nghiêng dọc mặt vát phía môi; web-18 cũng vậy: thấy rõ.

### b312e5fce503 – die_thermal_bolts:details[1]
> Đầu bulông nằm trong rãnh phay, nhô tối đa 30 mm khỏi mặt vát, còn ≈ 20 mm khe hở tới trục giữa (đã kiểm tra bằng hình học).
- ⚠ "Đầu bulông nằm trong rãnh phay, nhô tối đa 30 mm khỏi mặt vát, còn ≈ 20 mm khe hở tới tr…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 260e2898a4b7 – die_thermal_bolts:details[2]
> positions_mm là tâm bulông; item_mm = [Ø, Ø, dài] theo hệ trục riêng của bulông, trục dài là item_axis.
- ⚠ "positions_mm là tâm bulông; item_mm = [Ø, Ø, dài] theo hệ trục riêng của bulông, trục dà…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

