# Kiểm nguồn nhóm control

Người kiểm: lead (Opus, làm tại chỗ). Hạn mức Sonnet hết giữa chừng nên người dùng chọn để lead tự kiểm; lead không gắn nhóm này. Ngày 2026-10-06.
Tổng: 40 dòng, 81 fact (✓ 19, ≈ 3, ⚠ 59 sau khi kiểm). Hạ mức (cả lượt kiểm trước nếu có): 2. Nâng mức: 0. Sửa chữ hoặc tách fact: 1.

Hình đã mở: web-01, web-04 (cắt phóng vùng HMI và đèn tháp), web-05, web-06, web-07, web-17, crop trang 7 (tủ xanh), crop trang 22–23 (tấm HMI). Chữ catalogue trang 22–23 đọc trong `research/pdf/ZE_text.txt`: "Central operation and visualization of the entire extrusion process", "based on Siemens Simatic S7® and WinCC®", "All line components … are visualized on clearly structured screen pages" (trang 22), "easy operation via touch screen and membrane keypad" (trang 23). Claim đã đọc: c003, c004, c013, c034, c054, c064, c065. design.md không nêu SBI là sản phẩm đã chọn (chỉ dùng c054 làm số liệu bước), nên ảnh SBI không mang ✓. Bản tiếng Nhật đã đối chiếu.

Lượt kiểm trước (agent Sonnet) dừng vì hạn mức trước khi viết file bằng chứng; lead kiểm lại toàn bộ 40 dòng.

## Thay đổi

| Khoá | Thiết bị | Fact | Trước → sau | Lý do |
|---|---|---|---|---|
| 7fddb076a16c | ctrl_die_bolt_cabinet | 1 | ✓ → ≈ | lượt kiểm trước (dừng giữa chừng vì hạn mức) đã hạ; lead đồng ý: design.md không chọn đích danh SBI, web-17 là khuôn hãng khác |
| 21f184e2f48c | ctrl_die_bolt_cabinet | 2 | ✓ → ≈ | như trên |
| 64e42041d94b | ctrl_hmi | 1, 3 | chữ (mức giữ nguyên) | bỏ "+Y theo quy ước thiết kế" khỏi fact ✓ (ảnh không cho thấy toạ độ của thiết kế); hướng +Y chuyển vào fact ⚠ 3 |

## Bằng chứng từng dòng

### b14cffc40bfc – ctrl_cable_drop:function
> Đưa cáp từ máng trên khung xuống sàn.
- ✓ "Máy ZE có máng cáp thép mạ kẽm dọc khung đế mang cáp nhiệt; cáp từ khung chạy xuống sàn": web-01, web-02 (ZE 110 R): thanh thép mạ kẽm dọc khung đế, các máng lưới mạ kẽm dưới xi lanh mang hộp đấu và cáp nhiệt, cáp đen chạy xuống sàn: thấy rõ.
- ⚠ "Máng đứng nối máng cáp trên khung với hào sàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 477a4c72c90c – ctrl_cable_drop:details[0]
> Máng đứng 300 × 100 áp mặt bên khung.
- ⚠ "Máng đứng 300 × 100 áp mặt bên khung": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 50306e1d6479 – ctrl_cable_mv:function
> Đưa cáp trung thế từ hào lên hộp đấu dây động cơ.
- ⚠ "Cáp trung thế đi trong hào rồi dựng lên hộp đấu dây động cơ": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 53f60c8344c5 – ctrl_cable_mv:details[0]
> 3 cáp trung thế trong ống bảo vệ Ø80 dựng lên sát mặt bên khung (Y −1 100) rồi vào đáy hộp đấu dây.
- ⚠ "3 cáp trung thế (3 pha) trong ống bảo vệ Ø80": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Dựng lên sát mặt bên khung (Y −1 100) rồi vào đáy hộp đấu dây": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7fddb076a16c – ctrl_die_bolt_cabinet:function
> Điều khiển 94 thanh nhiệt bulông theo profin chiều dày (bộ điều khiển riêng của hệ bulông nhiệt).
- ✓ "Bulông nhiệt (tự động) của khuôn có bước 30, 28 hoặc 25,4 mm: bảng thông số SBI Mechatro…": c054 (high) quote "Division (bolt spacing) | 30, 28, 25.4 mm (1″)": khớp.
- ≈ "Điều khiển theo profin chiều dày: màn hình hiện chiều dày từng phần tử bulông (hệ SBI Me…": web-17: màn hình "Dickenmesspunkt-Regelung" vẽ chiều dày theo từng phần tử điều chỉnh 2…60; ≈ đúng (tham chiếu hãng khác, thiết kế theo cách điều khiển này).
- ⚠ "94 bulông nhiệt ≈ 2 400 / 25,4: khe môi rộng 2 400 chia cho bước bulông 25,4 mm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Bộ điều khiển riêng của hệ bulông nhiệt, đặt trong tủ riêng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 21f184e2f48c – ctrl_die_bolt_cabinet:details[0]
> Tủ 800 × 600 × 2 000 RAL 7035, màn hình profin trên cửa.
- ⚠ "Tủ 800 × 600 × 2 000": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Màu RAL 7035 (xám sáng)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "Màn hình hiện profin chiều dày (cột theo từng phần tử bulông) là giao diện điều khiển củ…": như trên (web-17).
- ⚠ "Màn hình gắn trên cửa tủ": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1acbb1ec452a – ctrl_drive_cabinet:function
> Biến tần điều khiển tốc độ động cơ chính 1 500 kW.
- ⚠ "Biến tần (VFD) điều khiển tốc độ động cơ chính": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Công suất động cơ chính 1 500 kW": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 07fc6a5412e8 – ctrl_drive_cabinet:details[0]
> 6 khoang RAL 7035 rộng 600, sâu 1 200, cao 2 400 kể cả đế, cửa mở về +Y có lưới thông gió, đèn báo; trước cửa chừa ≥ 1 000 mm.
- ⚠ "6 khoang RAL 7035: rộng 600, sâu 1 200, cao 2 400 kể cả đế": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Cửa mở về +Y, có lưới thông gió và đèn báo": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Trước cửa chừa ≥ 1 000 mm": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5f3b9ce96d89 – ctrl_estop_die:function
> Dừng khẩn khi chỉnh môi, deckle, xử lý màn nhựa ở phía vận hành.
- ⚠ "Nút dừng khẩn đặt ở khuôn, phía vận hành": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### dcd3e013add6 – ctrl_estop_die:details[0]
> Hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm (9 250, 1 450, 1 100), trên cột ống Ø50 dựng từ tay đòn thấp (Z 300–400) gá vào đầu +Y của xe khuôn; nằm ngoài tấm đầu khuôn (|Y| > 1 375) và trước khung cụm trục.
- ✓ "Nút dừng khẩn dạng nấm đỏ là thiết bị có trên dây chuyền ZE (thấy trên vỏ HMI của ZE 110…": web-04 (cắt phóng vùng HMI): vỏ HMI có nút nấm đỏ trên đế vàng ở góc dưới trái: thấy rõ. ✓ chỉ cho loại thiết bị.
- ⚠ "Hộp vàng 100 × 80 × 140": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tâm (9 250, 1 450, 1 100)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Trên cột ống Ø50 dựng từ tay đòn thấp (Z 300–400) gá vào đầu +Y của xe khuôn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Nằm ngoài tấm đầu khuôn (|Y| > 1 375) và trước khung cụm trục": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 2805359b44ae – ctrl_estop_die:details[1]
> Cáp nối bằng phích cắm qua hộp đấu dây khuôn để xe khuôn kéo đi được.
- ⚠ "Cáp nối bằng phích cắm qua hộp đấu dây khuôn để xe khuôn kéo đi được": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 86732894e81d – ctrl_estop_die:details[2]
> outline_mm (mặt YZ) là hình chữ L: tay đòn thấp Y 1 200–1 475, Z 300–400; cột Y 1 425–1 475 lên Z 1 030; hộp Y 1 410–1 490, Z 1 030–1 170.
- ⚠ "Hình bao theo mặt YZ là chữ L: tay đòn thấp Y 1 200–1 475, Z 300–400; cột Y 1 425–1 475 …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 92ca1beb2358 – ctrl_estop_melt:function
> Dừng khẩn khi thay lưới / xử lý ở bộ lọc phía vận hành.
- ⚠ "Nút dừng khẩn đặt ở bộ lọc, phía vận hành": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f09590d0f5b7 – ctrl_estop_melt:details[0]
> Hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm (7 320, 650, 1 100), trên cột 60 × 60 gá vào mặt +Y của giá bộ lọc, ngay sau cụm xả ngược (X ≤ 7 200).
- ✓ "Nút dừng khẩn dạng nấm đỏ là thiết bị có trên dây chuyền ZE (thấy trên vỏ HMI của ZE 110…": web-04 (cắt phóng vùng HMI): vỏ HMI có nút nấm đỏ trên đế vàng ở góc dưới trái: thấy rõ. ✓ chỉ cho loại thiết bị.
- ⚠ "Hộp vàng 100 × 80 × 140": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tâm (7 320, 650, 1 100)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Trên cột 60 × 60 gá vào mặt +Y của giá bộ lọc, ngay sau cụm xả ngược (X ≤ 7 200)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### fb6cd1f4096e – ctrl_estop_platform:function
> Dừng khẩn từ sàn cân cấp liệu.
- ⚠ "Nút dừng khẩn đặt trên sàn thao tác của cân cấp liệu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 795e6e0e151a – ctrl_estop_platform:details[0]
> Hộp vàng 100 × 80 × 140 có nút nấm đỏ trên cột lan can mép +Y.
- ✓ "Nút dừng khẩn dạng nấm đỏ là thiết bị có trên dây chuyền ZE (thấy trên vỏ HMI của ZE 110…": web-04 (cắt phóng vùng HMI): vỏ HMI có nút nấm đỏ trên đế vàng ở góc dưới trái: thấy rõ. ✓ chỉ cho loại thiết bị.
- ⚠ "Hộp vàng 100 × 80 × 140": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Gắn trên cột lan can mép +Y của sàn thao tác": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a6caf0d1ccf6 – ctrl_estops:function
> Dừng khẩn toàn dây chuyền từ dọc máy phía vận hành, ở tầm tay.
- ⚠ "Dừng khẩn toàn dây chuyền từ các hộp đặt dọc máy phía vận hành, ở tầm tay": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b90f07574975 – ctrl_estops:details[0]
> 3 hộp vàng 100 × 80 × 140 có nút nấm đỏ, tâm Z 1 120 (tầm 1,05–1,19 m): X 600 trên cột gá 60 × 60 từ mặt khung (vùng nạp để lộ), X 3 700 trên tấm dưới vỏ C4, X 5 700 trên tấm dưới vỏ C1.
- ✓ "Nút dừng khẩn dạng nấm đỏ là thiết bị có trên dây chuyền ZE (thấy trên vỏ HMI của ZE 110…": web-04 (cắt phóng vùng HMI): vỏ HMI có nút nấm đỏ trên đế vàng ở góc dưới trái: thấy rõ. ✓ chỉ cho loại thiết bị.
- ⚠ "3 hộp vàng 100 × 80 × 140": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tâm Z 1 120 (tầm 1,05–1,19 m)": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "X 600 trên cột gá 60 × 60 từ mặt khung (vùng nạp để lộ); X 3 700 trên tấm dưới vỏ C4; X …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1d0ab82874bd – ctrl_estops:details[1]
> Thêm nút trên HMI, tủ đầu máy, hộp đấu dây khuôn (−Y), lan can sàn thao tác (ctrl_estop_platform), khuôn phía +Y (ctrl_estop_die) và bộ lọc phía +Y (ctrl_estop_melt).
- ✓ "Nút dừng khẩn nấm đỏ trên vỏ HMI (thấy trên dây chuyền ZE 110 UT)": web-04 (cắt phóng vùng HMI): vỏ HMI có nút nấm đỏ trên đế vàng ở góc dưới trái: thấy rõ. ✓ chỉ cho loại thiết bị.
- ⚠ "Thêm nút ở tủ đầu máy, hộp đấu dây khuôn (−Y), lan can sàn thao tác, khuôn phía +Y và bộ…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 82b65411ce37 – ctrl_floor_duct:function
> Dẫn cáp từ máy về tủ điều khiển, nắp phẳng sàn.
- ⚠ "Hào cáp từ máy về tủ điều khiển, nắp phẳng sàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 8db78070bb94 – ctrl_floor_duct:details[0]
> Hào cáp có nắp tôn mạ kẽm chống trượt rộng 400, phẳng sàn (nắp dày 10).
- ⚠ "Hào có nắp tôn mạ kẽm chống trượt rộng 400, phẳng sàn, nắp dày 10": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 13efd7c95507 – ctrl_floor_trench:function
> Dẫn cáp động lực/tín hiệu tới bơm nhựa, hộp nhiệt đường chảy, HPU, cụm chân không, khuôn.
- ⚠ "Hào dẫn cáp động lực/tín hiệu tới bơm nhựa, hộp nhiệt đường chảy, HPU, cụm chân không, k…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### ce2e3f40c7ee – ctrl_floor_trench:details[0]
> Nắp tôn chống trượt rộng 200 phẳng sàn; kết thúc ở X 8 700, trước ray xe khuôn.
- ⚠ "Nắp tôn chống trượt rộng 200 phẳng sàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Kết thúc ở X 8 700, trước ray xe khuôn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4643483c62a5 – ctrl_heater_cabinet:function
> PLC, rơ-le bán dẫn cho vùng nhiệt xi lanh/đường chảy/khuôn, khởi động động cơ phụ.
- ✓ "Hệ điều khiển phức tạp của ZE, làm theo yêu cầu khách, dựa trên Siemens Simatic S7 (họ P…": cat-p22, chữ catalogue: "More complex control systems are tailored to individual customer requirements and based on Siemens Simatic S7® and WinCC®": khớp.
- ✓ "Bộ điều nhiệt và thiết bị điều khiển điện là một phần của máy ZE (catalogue đặt chúng tr…": c034 (medium) quote "the temperature control unit and the electrical control equipment are all integrated into the extruder base frame": khớp; fact ghi rõ thiết kế tách thành tủ riêng.
- ⚠ "Rơ-le bán dẫn đóng cắt các vùng nhiệt xi lanh / đường chảy / khuôn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Khởi động động cơ phụ (MCC) đặt chung trong tủ này": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### f531f8b31062 – ctrl_heater_cabinet:details[0]
> 4 khoang 600 × 600 × 2 200 RAL 7035, khoang đầu có dải xanh KM và logo; cửa mở về +Y.
- ✓ "Tủ điện nhiều khoang của máy ZE (ảnh dựng ZE BluePower của KM) có dải xanh KM với chữ Kr…": web-06, web-07: dãy tủ trắng nhiều cửa, dải xanh có chữ KraussMaffei trắng viết dọc; crop trang 7: khối tủ xanh có chữ trắng: thấy rõ.
- ⚠ "4 khoang 600 × 600 × 2 200 RAL 7035, dải xanh ở khoang đầu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Cửa mở về +Y": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1a6876758a14 – ctrl_hmi:function
> Màn hình cảm ứng + bàn phím màng điều khiển toàn dây chuyền; nút dừng khẩn.
- ✓ "Điều khiển bằng màn hình cảm ứng kết hợp bàn phím màng": cat-p23 chữ "easy operation via touch screen and membrane keypad"; crop trang 22–23: màn hình có các phím xung quanh: khớp.
- ✓ "Vận hành và hiển thị tập trung toàn bộ quá trình đùn: mọi thiết bị của dây chuyền hiện t…": cat-p22 chữ "Central operation and visualization of the entire extrusion process" và "All line components … visualized on clearly structured screen pages": khớp.
- ✓ "Nút dừng khẩn nấm đỏ trên vỏ HMI (thấy trên dây chuyền ZE 110 UT)": web-04 (cắt phóng vùng HMI): vỏ HMI có nút nấm đỏ trên đế vàng ở góc dưới trái: thấy rõ. ✓ chỉ cho loại thiết bị.

### 64e42041d94b – ctrl_hmi:details[0]
> Chân đế ống Ø120 cao 1 300 có khớp xoay đen, tay xoay ngắn; tấm HMI 800 × 510 × 120 nghiêng 15°, mặt hướng +Y.
- ✓ "HMI gắn trên ống đỡ trắng xám có khớp xoay đen; màn hình HMI trên tay xoay cũng thấy trê…": crop trang 22–23: tấm HMI trên ống đỡ trắng xám có khớp đen; web-06/07: màn hình trên tay xoay: thấy rõ.
- ✓ "HMI đặt cạnh máy trên chân đế ở phía vận hành, mặt quay ra chỗ người vận hành đứng": web-04, web-05: HMI dạng hộp trên chân đế cạnh cầu thang, mặt quay về phía người đứng vận hành: thấy rõ. Đã bỏ phần toạ độ thiết kế (+Y) khỏi fact này.
- ≈ "Tỷ lệ tấm HMI 800 : 510 ≈ 1,57 : 1: đo viền ngoài tấm trên hình ghép trang 22–23": đo lại trên crop trang 22–23: viền ngoài ≈ 1 378 × 880 px → 1,57; 800/510 = 1,569 ✓.
- ⚠ "Kích thước tuyệt đối 800 × 510 × 120, nghiêng 15°, mặt hướng +Y (phía vận hành theo quy …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Chân đế ống Ø120 cao 1 300, tay xoay ngắn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9d0f3fb36e32 – ctrl_hmi:details[1]
> Nút dừng khẩn đỏ trên vỏ HMI.
- ✓ "Nút dừng khẩn nấm đỏ trên vỏ HMI (thấy trên dây chuyền ZE 110 UT)": web-04 (cắt phóng vùng HMI): vỏ HMI có nút nấm đỏ trên đế vàng ở góc dưới trái: thấy rõ. ✓ chỉ cho loại thiết bị.

### f70178806fb4 – ctrl_infeed_lv:function
> Đưa cáp hạ thế 400 V từ tủ phân phối nhà máy vào tủ điều khiển + nhiệt.
- ⚠ "Cáp hạ thế 400 V từ tủ phân phối nhà máy vào tủ điều khiển + nhiệt": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 69defc93ff7c – ctrl_infeed_lv:details[0]
> Đoạn hào có nắp rộng 400 phẳng sàn dài 200 sau tủ, đầu ngoài để hở 'từ tủ phân phối' (tuyến tiếp theo thuộc nhà xưởng).
- ⚠ "Đoạn hào có nắp rộng 400 phẳng sàn dài 200 sau tủ, đầu ngoài để hở "từ tủ phân phối"": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### d7b88b67b401 – ctrl_infeed_mv:function
> Đưa cáp trung thế 3 kV từ trạm biến áp nhà máy vào tủ biến tần.
- ⚠ "Cáp trung thế 3 kV từ trạm biến áp nhà máy vào tủ biến tần": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 23236ec228af – ctrl_infeed_mv:details[0]
> Đoạn hào có nắp rộng 400 phẳng sàn dài 200 sau tủ, đầu ngoài để hở 'từ trạm biến áp' (tuyến tiếp theo thuộc nhà xưởng).
- ⚠ "Đoạn hào có nắp rộng 400 phẳng sàn dài 200 sau tủ, đầu ngoài để hở "từ trạm biến áp"": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a3306d7aa3d7 – ctrl_machine_cabinet:function
> Tủ đấu dây tại chỗ cho truyền động: cấp nguồn cụm dầu, encoder, cảm biến hộp số, an toàn.
- ✓ "Hệ bôi trơn, bộ điều nhiệt và thiết bị điều khiển điện của ZE UTX đều nằm ngay trên khun…": c034 quote như trên: khớp.
- ⚠ "Tủ đấu dây tại chỗ cho truyền động: cấp nguồn cụm dầu, encoder, cảm biến hộp số, an toàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 2efd9e47befa – ctrl_machine_cabinet:details[0]
> Tủ 500 × 1 000 × 2 000, mặt +Y và −X sơn xanh KM có chữ KraussMaffei trắng chạy dọc, còn lại trắng; nút dừng khẩn trên mặt +Y.
- ✓ "Tủ điện của máy ZE sơn xanh KM, chữ KraussMaffei trắng viết dọc (hình cắt ZE UTX trang 7…": crop trang 7: tủ sơn xanh KM, chữ "KraussMaffei Berstorff" trắng viết dọc; web-06/07: dải xanh chữ trắng dọc: thấy rõ.
- ⚠ "Tủ 500 × 1 000 × 2 000": meas-4: khối 430 × 1 380, Z 316–1 695; thiết kế 500 × 1 000 × 2 000 đặt sàn. Lệch đã ghi trong lý do (rev-M11, DECISIONS #13): đúng.
- ⚠ "Mặt +Y và −X sơn xanh KM, các mặt còn lại trắng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Nút dừng khẩn trên mặt +Y": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 909a8d19c6c2 – ctrl_signal_tower:function
> Báo trạng thái máy (đỏ/vàng/xanh/còi).
- ✓ "Dây chuyền ZE có đèn tháp nhiều tầng (thấy tầng đỏ và xanh lá) và còi báo": web-04: đèn tháp có tầng đỏ và tầng xanh lá trên cột phía sau; web-05: loa còi trên cột: thấy rõ.
- ⚠ "Báo trạng thái máy bằng ba màu đỏ / vàng / xanh và còi": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### fb3424fb62ef – ctrl_signal_tower:details[0]
> 4 tầng đèn Ø70 + còi, cột Ø40.
- ⚠ "4 tầng đèn Ø70 + còi, cột Ø40": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 9e427c01f29c – ctrl_trench_die_branch:function
> Đưa cáp từ hào chính tới hộp đấu dây khuôn đặt trên sàn.
- ⚠ "Hào nhánh đưa cáp từ hào chính tới hộp đấu dây khuôn đặt trên sàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a501e92a4395 – ctrl_trench_die_branch:details[0]
> Nắp tôn rộng 200 phẳng sàn.
- ⚠ "Nắp tôn rộng 200 phẳng sàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### b0f1b79a34c6 – ctrl_trench_mv:function
> Dẫn cáp trung thế từ tủ biến tần tới động cơ dưới sàn, không vắt qua lối đi.
- ⚠ "Dẫn cáp trung thế từ tủ biến tần tới động cơ dưới sàn, không vắt qua lối đi": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e20c720f441a – ctrl_trench_mv:details[0]
> Hào có nắp tôn mạ kẽm rộng 400 phẳng sàn.
- ⚠ "Hào có nắp tôn mạ kẽm rộng 400 phẳng sàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

