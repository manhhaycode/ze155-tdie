# Kiểm nguồn nhóm util

Người kiểm: lead (Opus, làm tại chỗ). Hạn mức Sonnet hết giữa chừng nên người dùng chọn để lead tự kiểm; lead không gắn nhóm này. Ngày 2026-10-06.
Tổng: 29 dòng, 58 fact (✓ 16, ≈ 5, ⚠ 37 sau khi kiểm). Hạ mức (cả lượt kiểm trước nếu có): 0. Nâng mức: 0. Sửa chữ hoặc tách fact: 1.

Hình đã mở: web-02, web-03 (cắt phóng vùng cổng F2–F4), web-05 (cắt phóng góc dưới trái), web-12, web-18, crop trang 5 (kênh nước xi lanh), crop trang 19 (bộ điều nhiệt trong khung đế). Claim đã đọc: c023, c024, c054, c063, c066. Bản tiếng Nhật đã đối chiếu, khớp nghĩa.

Ghi chú cho người thiết kế: ảnh web-03 cho thấy nước (ống mềm đen) ở F3 và dầu (ống thép xanh) ở F2/F4, ngược với thiết kế đặt nước ở F2/F4 (dòng 352ae4132fbf ghi rõ trong lý do).

## Thay đổi

| Khoá | Thiết bị | Fact | Trước → sau | Lý do |
|---|---|---|---|---|
| 8e7e20b6f6e6, 352ae4132fbf | util_cw_lube_hoses | 0 | chữ (✓ giữ nguyên) | ảnh web-03 chỉ có ống mềm đen ở F3; F2, F4 là ống thép sơn xanh. Chữ cũ "ống mềm đen nối vào các cổng" nói quá |

## Bằng chứng từng dòng

### ec92c400c238 – util_air_drop:function
> Cấp khí nén 6 bar từ đường trên cao cho làm mát bulông nhiệt.
- ⚠ "Khí nén 6 bar lấy từ đường khí nhà máy trên cao": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ≈ "Khí làm mát bulông nhiệt: ống mềm đen dẫn khí tới ống gió dọc hàng bulông nhiệt ở môi kh…": web-18 (SBI, hãng khác, nên ≈): ống mềm đen gợn sóng đi vào vỏ ống gió trên hàng bulông nhiệt; images.md ghi "air duct, cooling-air hose": khớp.

### 64aab58b966c – util_air_drop:details[0]
> Ống thép mạ Ø30, đầu trên để hở 'từ đường khí nhà máy'.
- ⚠ "Ống thép mạ Ø30, đầu trên để hở làm điểm nối với đường khí nhà máy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7fc44db13aa4 – util_air_drop_2:function
> Cấp khí nén cho van chân không và thiết bị cấp liệu.
- ⚠ "Khí nén cấp cho van bướm chân không (bộ tác động khí nén), van lật xả máy hút liệu và va…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 5dfb9c26828c – util_air_drop_2:details[0]
> Ống thép mạ Ø30 dọc cột sàn X −450, Y −2 600, xuyên sàn; đầu trên để hở 'từ đường khí nhà máy'.
- ⚠ "Ống thép mạ Ø30 xuyên sàn, đầu trên để hở": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đi dọc cột sàn tại X −450, Y −2 600": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 3ebaf8f7f465 – util_air_hose_die:function
> Dẫn khí làm mát tới ống gió của thanh bulông nhiệt.
- ≈ "Ống mềm đen dẫn khí làm mát tới ống gió dọc hàng bulông nhiệt (ảnh SBI)": web-18 (SBI, hãng khác, nên ≈): ống mềm đen gợn sóng đi vào vỏ ống gió trên hàng bulông nhiệt; images.md ghi "air duct, cooling-air hose": khớp.

### f3d6fd6efdfe – util_air_hose_die:details[0]
> Ống mềm PU Ø24, khớp nối nhanh ở đầu thanh để tách khuôn.
- ≈ "Ống mềm đen nối vào ống gió của thanh bulông nhiệt (ảnh SBI)": web-18 (SBI, hãng khác, nên ≈): ống mềm đen gợn sóng đi vào vỏ ống gió trên hàng bulông nhiệt; images.md ghi "air duct, cooling-air hose": khớp.
- ⚠ "Ống mềm PU Ø24": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Khớp nối nhanh ở đầu thanh để tách khuôn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 8f7c0fefff38 – util_air_tube_loader:function
> Cấp khí cho van lật xả của máy hút liệu và van nạp của cân.
- ⚠ "Cấp khí cho van lật xả của máy hút liệu và van nạp của cân": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### e46e6a3b4bf9 – util_air_tube_loader:details[0]
> Ống PU Ø12 lên dọc cột, đi trên mặt sàn, rồi dọc phễu cân lên van máy hút liệu.
- ⚠ "Ống PU Ø12": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tuyến ống: lên dọc cột, đi trên mặt sàn, rồi dọc phễu cân lên van máy hút liệu": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7392919161f0 – util_air_tube_vac:function
> Cấp khí cho bộ tác động van bướm chân không vùng 2.
- ⚠ "Khí cấp cho bộ tác động khí nén của van bướm chân không vùng 2": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 510111e136f1 – util_air_tube_vac:details[0]
> Ống PU Ø12 đi trên máng nhỏ dưới sàn thao tác ở Z 2 450 rồi tới bộ tác động van.
- ⚠ "Ống PU Ø12": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đi trên máng nhỏ dưới sàn thao tác ở Z 2 450 rồi tới bộ tác động van": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 8e7e20b6f6e6 – util_cw_lube_hoses:function
> Cấp/hồi nước cho bộ làm mát dầu hộp số.
- ✓ "Cụm dầu hộp số của máy ZE 110 R có bộ làm mát dạng tấm inox (nhãn cổng F2, F3, F4): ống …": web-03 (cắt phóng): bộ làm mát tấm inox có nhãn F2, F3, F4; ống mềm đen ở F3, ống thép xanh ở F2, F4. Chữ đã sửa cho đúng ảnh.
- ⚠ "Môi chất làm mát là nước cấp/hồi từ ống nhà máy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 352ae4132fbf – util_cw_lube_hoses:details[0]
> 2 ống mềm DN25 chạy ngoài mép +Y của khung: cấp ở Y 1 060, Z 380; hồi ở Y 1 130, Z 440; lên và vào cổng F2/F4 của bộ làm mát.
- ✓ "Cụm dầu hộp số của máy ZE 110 R có bộ làm mát dạng tấm inox (nhãn cổng F2, F3, F4): ống …": như dòng trên (cùng fact).
- ⚠ "2 ống mềm DN25: một cấp, một hồi": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tuyến ngoài mép +Y khung: cấp Y 1 060 Z 380, hồi Y 1 130 Z 440; lên và vào cổng F2/F4": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 2a0b258c0b80 – util_cw_lube_hoses:details[1]
> Van bi tay đỏ trên mỗi ống ngay trước bộ làm mát; van điều nhiệt nước trên ống hồi.
- ✓ "Van bi có tay gạt đỏ trên mạch nước làm mát của máy ZE": web-02 (ZE 110 R): trên ống góp nước có các van tay gạt nhỏ màu đỏ ở từng nhánh: thấy rõ; c023 (medium) quote "valvole con maniglie rosse". ✓ chỉ cho loại van, vị trí là ⚠ (đúng như fact).
- ⚠ "Mỗi ống một van bi, đặt ngay trước bộ làm mát": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Van điều nhiệt nước trên ống hồi": đã xem web-03: có một thiết bị nhỏ có cáp ở chân bộ làm mát (kiểu van điện từ/cảm biến), không phải van điều nhiệt; lý do đúng.

### 318e096fcd33 – util_cw_motor_hoses:function
> Cấp/hồi nước cho bộ làm mát gió–nước trên nóc động cơ chính (IC81W).
- ✓ "Máy ZE 110 R × 28D UTmi có động cơ AC làm mát bằng nước (bản rao 250 kW)": c024 (high): "water-cooled AC motor" nằm trong claim (high, nói thẳng), quote chỉ có phần bơm chân không và side feeder. Đủ cho ✓ theo luật kiểm; fact ghi đúng là máy ZE 110 R, 250 kW. W1 (127 = D vít) không liên quan, giữ.
- ≈ "Động cơ lớn của máy KM có hộp làm mát đặt trên nóc (ảnh KE 400, không phải ZE)": web-12 (bản dựng KE 400, không phải ZE): motor xanh lớn có hộp đặt trên nóc: thấy rõ; ≈ vì khác máy.
- ⚠ "Bộ làm mát gió–nước IC81W trên nóc động cơ 1 500 kW, nhiệt thải đi vào nước": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 3b874ab4e2e5 – util_cw_motor_hoses:details[0]
> 2 ống inox DN40 (OD 48) chạy thấp ngoài mép +Y khung (cấp Y 1 060 Z 250, hồi Y 1 130 Z 150), dựng lên tại X −3 500 / −3 700 cạnh cụm dầu, rồi vào bích trên mặt +Y bộ làm mát động cơ ở Z 2 300 / 2 400; van bi tay đỏ ở mỗi ống.
- ⚠ "2 ống inox DN40 (OD 48): một cấp, một hồi": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Tuyến: cấp Y 1 060 Z 250, hồi Y 1 130 Z 150 chạy thấp ngoài mép +Y khung; dựng lên tại X…": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ✓ "Van bi có tay gạt đỏ trên mạch nước làm mát của máy ZE": web-02 (ZE 110 R): trên ống góp nước có các van tay gạt nhỏ màu đỏ ở từng nhánh: thấy rõ; c023 (medium) quote "valvole con maniglie rosse". ✓ chỉ cho loại van, vị trí là ⚠ (đúng như fact).

### 657f4696647c – util_cw_return_riser:function
> Trả nước hồi về đường ống nhà máy.
- ✓ "Máy ZE có ống góp hồi nước riêng cạnh ống cấp, nối xuống sàn bằng ống đứng có bích": web-02 (ZE 110 R): hai ống bọc cách nhiệt chạy song song dọc khung, mũi tên chiều dòng ngược nhau, ống đứng có bích xuống sàn ở bên phải: thấy rõ. Không phân biệt được ống nào là cấp, fact không nói điều đó.
- ⚠ "Nước hồi trả về đường ống nước nhà máy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 2fca6309b1a7 – util_cw_return_riser:details[0]
> DN50 có van bi tay đỏ và nhiệt kế.
- ✓ "Van bi có tay gạt đỏ trên mạch nước làm mát của máy ZE": web-02 (ZE 110 R): trên ống góp nước có các van tay gạt nhỏ màu đỏ ở từng nhánh: thấy rõ; c023 (medium) quote "valvole con maniglie rosse". ✓ chỉ cho loại van, vị trí là ⚠ (đúng như fact).
- ⚠ "Ống DN50": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Nhiệt kế trên ống hồi": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 431a865448fb – util_cw_sidefeed_hoses:function
> Làm mát thân side feeder.
- ⚠ "Thân side feeder có áo nước làm mát": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### cf5cba094b06 – util_cw_sidefeed_hoses:details[0]
> 2 ống mềm inox DN15 từ đỉnh cụm van 2 vào mặt dưới thân side feeder.
- ✓ "Ống mềm inox bọc lưới dẫn nước từ cụm van tới xi lanh (máy ZE)": web-02 (ZE 110 R): ống mềm inox bọc lưới đi từ cụm van lên các xi lanh: thấy rõ. Crop trang 5 chỉ cho thấy ống mềm (đen) nối vào kênh nước xi lanh.
- ⚠ "2 ống DN15 từ đỉnh cụm van 2 vào mặt dưới thân side feeder": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### a5cf643a1f98 – util_cw_supply_riser:function
> Đưa nước làm mát (≈ 15 °C, 4 bar) từ đường ống nhà máy lên ống góp.
- ✓ "Máy ZE dùng nước lạnh (nhãn ống 'Chilled W…'), cấp qua ống góp dọc khung đế, nối xuống s…": web-02 (ZE 110 R): nhãn trên ống bọc cách nhiệt đọc được "hilled W…", cách đọc hợp lý duy nhất là "Chilled Water"; ống góp dọc khung đế và ống đứng có bích: thấy rõ.
- ⚠ "Nước ≈ 15 °C, 4 bar từ đường ống nhà máy": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 07689f91cda1 – util_cw_supply_riser:details[0]
> DN50 có van bi tay đỏ, lọc Y và đồng hồ áp ở đoạn đứng.
- ✓ "Van bi tay gạt đỏ và đồng hồ áp trên ống góp nước làm mát của máy ZE": web-02 (ZE 110 R): van tay gạt đỏ và đồng hồ áp (mặt tròn) trên ống góp nước: thấy rõ; c023 quote "valvole con maniglie rosse".
- ⚠ "Ống DN50": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Lọc Y, van bi và đồng hồ áp đặt ở đoạn đứng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 1186e94fe70c – util_cw_throat_hoses:function
> Làm mát hộp miệng nạp để hạt không dính chảy ở miệng.
- ⚠ "Hộp miệng nạp có áo nước làm mát để hạt không dính chảy ở miệng": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 0ba4d8f63f35 – util_cw_throat_hoses:details[0]
> 2 ống mềm inox DN20 từ đỉnh cụm van 1 lên Z 1 550/1 600 rồi vào mặt +Y hộp miệng nạp.
- ✓ "Ống mềm inox bọc lưới dẫn nước từ cụm van tới xi lanh (máy ZE)": như cf5cba094b06 (cùng fact).
- ⚠ "2 ống DN20 từ đỉnh cụm van 1 lên Z 1 550 / 1 600 rồi vào mặt +Y hộp miệng nạp": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 7782e23ae1dd – util_cw_vac_hoses:function
> Cấp/hồi nước cho ống xoắn ngưng của bình tách và cho bơm Roots/bơm khô làm mát nước.
- ⚠ "Nước cấp/hồi cho ống xoắn ngưng trong bình tách": c063 chỉ nói buồng ngưng điều nhiệt, không nói ống xoắn nước: ⚠ đúng.
- ⚠ "Bơm Roots và bơm trục vít khô làm mát bằng nước": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### c2612a13336b – util_cw_vac_hoses:details[0]
> 4 ống inox DN25 (OD 32) đứng lên từ hai cặp đầu nối sàn giữa bình tách và skid: cặp cho bình tách vào Z 1 000 / ra Z 1 100, cặp cho skid vào/ra ở Z 400; van bi tay đỏ ở chân mỗi ống.
- ⚠ "4 ống inox DN25 (OD 32): hai cặp vào/ra, mỗi thiết bị một cặp": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ⚠ "Đứng lên từ hai cặp đầu nối sàn: bình tách vào Z 1 000 / ra Z 1 100, skid vào/ra Z 400; …": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.
- ✓ "Van bi có tay gạt đỏ trên mạch nước làm mát của máy ZE": web-02 (ZE 110 R): trên ống góp nước có các van tay gạt nhỏ màu đỏ ở từng nhánh: thấy rõ; c023 (medium) quote "valvole con maniglie rosse". ✓ chỉ cho loại van, vị trí là ⚠ (đúng như fact).

### 265d0ee335b8 – util_frl:function
> Lọc, điều áp khí làm mát bulông nhiệt.
- ✓ "Máy ZE 110 UT trong ảnh dùng bộ lọc–điều áp khí có đồng hồ áp để lọc và điều áp khí cấp …": web-05 (cắt phóng góc dưới trái): bầu lọc–điều áp có núm chỉnh và đồng hồ áp, phía trước có van bi tay gạt đỏ: thấy rõ. ✓ chỉ cho loại thiết bị, không cho vị trí.
- ≈ "Khí này dùng làm mát bulông nhiệt (ảnh SBI)": web-18 (SBI, hãng khác, nên ≈): ống mềm đen gợn sóng đi vào vỏ ống gió trên hàng bulông nhiệt; images.md ghi "air duct, cooling-air hose": khớp.

### ab6e01afa56b – util_frl:details[0]
> Bộ lọc + van điều áp + đồng hồ, van khoá tay.
- ✓ "Bộ lọc–điều áp khí có đồng hồ áp và van bi tay gạt ở phía trước (ảnh máy ZE 110 UT)": web-05 (cắt phóng góc dưới trái): bầu lọc–điều áp có núm chỉnh và đồng hồ áp, phía trước có van bi tay gạt đỏ: thấy rõ. ✓ chỉ cho loại thiết bị, không cho vị trí.

### f09951259964 – util_frl_2:function
> Lọc, điều áp khí cho van bướm chân không, van nạp máy hút liệu, van cân.
- ✓ "Máy ZE 110 UT trong ảnh dùng bộ lọc–điều áp khí có đồng hồ áp để lọc và điều áp khí cấp …": web-05 (cắt phóng góc dưới trái): bầu lọc–điều áp có núm chỉnh và đồng hồ áp, phía trước có van bi tay gạt đỏ: thấy rõ. ✓ chỉ cho loại thiết bị, không cho vị trí.
- ⚠ "Cấp khí cho van bướm chân không, van nạp máy hút liệu và van cân": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

### 4c7c42150b50 – util_frl_2:details[0]
> Bộ lọc + van điều áp + đồng hồ, van khoá tay, cao 1,35–1,6 m.
- ✓ "Bộ lọc–điều áp khí có đồng hồ áp và van bi tay gạt ở phía trước (ảnh máy ZE 110 UT)": web-05 (cắt phóng góc dưới trái): bầu lọc–điều áp có núm chỉnh và đồng hồ áp, phía trước có van bi tay gạt đỏ: thấy rõ. ✓ chỉ cho loại thiết bị, không cho vị trí.
- ⚠ "Lắp cao 1,35–1,6 m trên cột sàn": lý do đúng; không có ref nào trong bộ nguồn ghi giá trị này.

