# Sổ giả định (assumptions register): ZE 155 A UT 34D + khuôn chữ T, dây chuyền tấm PET

Sinh ngày 2026-10-05 14:24 từ các file trên máy trong `~/m3d-e2e/ze155-tdie/`. Không dùng mạng. Mỗi mục ghi: hạng mục, giá trị giả định, lý do hoặc cơ sở, nơi ghi (file + mục/dòng), độ tin cậy nếu file có ghi.

**Quy ước**
- "Giả định" (assumption) = giá trị không có tài liệu công khai, do agent chọn và ghi lý do. "Ước lượng" (estimate) trong `specs.md` cũng được tính là giả định.
- Mã `cNNN` trỏ tới `01_sources/web/claims.jsonl` (nguồn có URL). Dấu `*` là cách `design-anim.md` và `shots.json` đánh dấu giá trị giả định trên hình. Chữ `G` trên bản vẽ đánh dấu giá trị giả định.
- Đường dẫn file là đường dẫn gốc trong workspace; bản sao trong zip: `research/` → `01_sources/`, `design/` → `03_design/`, `drawings/` → `04_drawings/`, `out/` → `05_model_build/`, `anim/` → `06_animation_interior/`, `web/` → `07_web_plan/`.
- `file:N` = số dòng trong file đó (tại thời điểm sinh sổ này).
- Độ tin cậy: chỉ ghi khi file nguồn có ghi (ví dụ "cao", "thấp (c062)", "ước lượng", "giả định (*)"); còn lại là "không ghi".

Mỗi khu vực có tối đa bốn loại mục:
1. **Giả định chính:** gom tay từ `specs.md`, `design.md` (§1, §3, §3.1, §7, §9, §10), `DECISIONS.md`, `design-anim.md`, `interior_parts.json`, `drawings/design_issues.md` và kế hoạch web.
2. **Chi tiết `design.md` §5 có nguồn ghi "giả định":** trích tự động dòng "Nguồn" của từng chi tiết; các chi tiết cùng một câu nguồn được gộp một dòng.
3. **Lệch thiết kế khi dựng (`DESIGN-DEVIATION`):** mọi dòng trong `out/log.md` và `anim/log.md`, tóm tắt tiếng Việt. Nguyên văn tiếng Anh ở `DESIGN-DEVIATIONS.md` cùng thư mục.
4. **Lỗi thiết kế do review phát hiện:** con số hoặc lựa chọn của thiết kế bị review chỉ ra là sai hoặc mâu thuẫn, và cách xử lý.

## Tổng hợp số mục theo khu vực

| Khu vực | Giả định chính | Chi tiết design §5 (nhóm / chi tiết) | Lệch khi dựng | Lỗi do review | Tổng |
|---|---|---|---|---|---|
| [Chung: máy, ứng dụng, bố trí, khung đế (general)](#chung-máy-ứng-dụng-bố-trí-khung-đế-general) | 14 | 3 / 3 | 2 | 1 | **20** |
| [Truyền động (drive)](#truyền-động-drive) | 11 | 8 / 8 | 7 | 2 | **28** |
| [Xi lanh và trục vít (barrel / screws)](#xi-lanh-và-trục-vít-barrel--screws) | 13 | 8 / 19 | 8 | 5 | **34** |
| [Cấp liệu (feeding)](#cấp-liệu-feeding) | 7 | 14 / 20 | 1 | 0 | **22** |
| [Chân không (vacuum)](#chân-không-vacuum) | 5 | 7 / 13 | 2 | 1 | **15** |
| [Đường chảy nhựa (melt line)](#đường-chảy-nhựa-melt-line) | 15 | 18 / 31 | 10 | 4 | **47** |
| [Khuôn chữ T (T-die)](#khuôn-chữ-t-t-die) | 12 | 5 / 6 | 6 | 3 | **26** |
| [Cụm trục cán (roll stack, context)](#cụm-trục-cán-roll-stack-context) | 6 | 1 / 1 | 5 | 0 | **12** |
| [Điều khiển và điện (control)](#điều-khiển-và-điện-control) | 5 | 10 / 14 | 11 | 1 | **27** |
| [Tiện ích (utilities)](#tiện-ích-utilities) | 3 | 6 / 12 | 5 | 0 | **14** |
| [Giá trị quy trình (process values)](#giá-trị-quy-trình-process-values) | 14 | 0 / 0 | 0 | 0 | **14** |
| [Animation và nội thất (animation / interior)](#animation-và-nội-thất-animation--interior) | 11 | 0 / 0 | 25 | 0 | **36** |
| [Kế hoạch web (web, R3F)](#kế-hoạch-web-web-r3f) | 11 | 0 / 0 | 0 | 0 | **11** |
| **Tổng** | 127 | 80 / 127 | 82 | 17 | **306** |

Phụ lục (không tính vào tổng vì phần lớn trùng các mục trên): A. 45 dòng bảng ghi "ước lượng" trong `specs.md`; B. 40 nhãn trên hình có dấu `*` trong `shots.json`.

## Chung: máy, ứng dụng, bố trí, khung đế (general)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Phiên bản máy | ZE 155 **A** UT(i), không phải bản R | Bản A là bản tiêu chuẩn, mômen cao nhất; A và R cùng khoảng cách tâm (c030) nên nhìn từ ngoài giống nhau | DECISIONS.md #9; specs.md §0 | không ghi |
| 2 | Ứng dụng | Đùn tấm PET trực tiếp, không sấy: ZE → van khởi động → lọc lưới → bơm bánh răng → khuôn T → cụm cán 3 trục | Catalogue có sơ đồ diverter valve + slot die + smoothing roll (c035); KM dùng ZE UT cho tấm PET trực tiếp (c040), dây chuyền tấm có lọc thủy lực + bơm (c043). Không nguồn nào mô tả đúng ZE 155 + T-die | DECISIONS.md #3, #10; specs.md §0; design.md §1 | không ghi |
| 3 | Đường kính danh nghĩa | "155" chỉ là tên gọi; D thực = 169 mm theo bảng KM (thay quyết định 4: D = 155, 34D = 5 270 mm) | Bảng KM (c001) | DECISIONS.md #4 → #9 | cao (c001) |
| 4 | Tỷ lệ hình bóng trang 9 | Chỉ dùng tỷ lệ nội bộ; không dùng thang 45,2 mm/pt | ZE 180 UT là đúng hình ZE 155 UT phóng ×1,05, tức hình mẫu chung | pdf_measures.md §1; DECISIONS.md #9; design.md §9 | không ghi |
| 5 | Chiều dài máy tại 34D | ≈ 10 000 mm (11 700 − 10 × 169) | Bảng KM cho 11 700 mm ở 44D (c007); kiểm bằng ZE 110 lệch 3,5 % | specs.md §1, §8 | ước lượng |
| 6 | Khối lượng tại 34D | ≈ 31 000 kg | 34 000 kg ở 44D (c008) trừ 10D xi lanh, vít, vỏ | specs.md §1; design.md §3 | ước lượng |
| 7 | Chiều rộng khung đế | ≈ 2 000 mm | ZE 110 thật rộng 1 400 mm (c021) × tỷ lệ 169/119 = 1,42 | specs.md §1; design.md `base_frame_drive` | ước lượng |
| 8 | Chiều cao tới đỉnh xi lanh | ≈ 2 000 mm (chưa tính phễu, ống chân không) | ZE 110: 550 mm trên trục × 1,42 + cao trục 1 200 | specs.md §1 | ước lượng |
| 9 | Phía người vận hành | +Y: HMI, ống góp nước, cụm dầu, side feeder | Không biết máy ZE UT lớn đặt HMI/ống góp ở phía nào (specs §10); chọn theo ảnh web-06 | specs.md §7, §10; design.md §4.2 | không ghi |
| 10 | Bố trí phụ trợ | Sàn thao tác, cầu thang, dãy tủ, cụm chân không, HPU, hào cáp, khí nén do người thiết kế bố trí; lối đi −Y ≥ 850 mm, ống qua lối đi ≥ 2 190 mm | Không có nguồn; theo thực hành dây chuyền thật | design.md §4.2, §7.12, §9 | không ghi |
| 11 | Kích thước bao theo thiết kế | Máy 15 600 × 7 700 × 6 300 mm; cả dây chuyền 18 200 × 7 700 × 6 300 mm (mô hình: 18 370 × 7 900 × 6 107 mm) | Kết quả của bố trí giả định (check_parts.py) | design.md §4.4; out/report.md §1 | không ghi |
| 12 | Khối cao cuối máy (trang 9) | Hiểu là tủ đầu máy đứng sàn, sơn xanh KM, có đèn tháp; không làm tủ treo như hình bóng | Hình bóng không chú thích; review-01 M11 không áp dụng vì phần đó đang được dựng | design.md §7.12, §9 (chưa giải quyết #2); DECISIONS.md #13 | không ghi |
| 13 | Màu sắc | Mã hex lấy mẫu từ ảnh (khung #DCDCDC, xanh KM ≈ #008DC3, cụm truyền động xanh Flender ≈ #1F6FD0…#3665B0); không có mã RAL chính thức | Lấy mẫu pixel trên web-01/03/06/08/09, p16 | specs.md §9, §10; design.md §7.15; pdf_catalog.md (ghi chú chung) | chỉ để tham khảo (pdf_catalog.md) |
| 14 | Đóng băng thiết kế | `design/parts.json` lúc 23:14 là bản cuối; chỉ sửa cái nhìn thấy được | Người dùng: "không cần quá hoàn hảo" | DECISIONS.md #21 | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `base_frame_drive`<br>Khung đế đoạn truyền động (Base frame, drive segment) | frame; bao 5480 × 2000 × 590 (X × Y × Z) | pdf_measures §2.2/§4 (khung 2 đoạn, dầm trên 210 / hộp dưới 390 mm, mối chia X ≈ +330); chiều rộng 2 000 giả định theo specs §1 (ZE 110 × 1,42) | design.md:208 |
| 2 | `base_feet`<br>Chân chỉnh cao / bulông neo (Levelling feet and anchors) | cyl; bao 11100 × 2000 × 60 (X × Y × Z); số lượng 22 | pdf_measures §2.2 (chân cao 57 mm, 12 vị trí); số lượng và vị trí giả định theo chiều dài khung mới | design.md:228 |
| 3 | `base_drip_tray`<br>Khay hứng nhỏ giọt trên khung (Drip tray on frame top) | sheet; bao 5500 × 880 × 40 (X × Y × Z) | giả định: chi tiết thường có trên máy đùn (web-01 cho thấy mặt khung kín dưới xi lanh) | design.md:238 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `frame_drip_tray` | Khay hứng khoét quanh 3 tấm đế gối, có cổ inox cao 30 mm | out/log.md:88 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 2 | `ctx_floor` | Sàn mở rộng từ 20,5 × 9 m thành mặt 180 × 180 m ở Z 0, mờ dần vào nền, để làm phông render | out/log.md:329 | Phase 4b — finishing: render quality, light, materials, casting look, cable density, final renders, report |

**Lỗi thiết kế do review phát hiện**

| # | Hạng mục | Phát hiện | Xử lý | Ghi ở đâu |
|---|---|---|---|---|
| 1 | Tủ đầu máy | Tủ đứng sàn không khớp khối treo của hình bóng trang 9 (review-01 M11) | Không sửa; chấp nhận | design/review-01.md M11; DECISIONS.md #13; design.md §9 #2 |

## Truyền động (drive)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Công suất động cơ lắp đặt | 1 500 kW, 4 cực, trung thế 3 kV, biến tần; khung ABB AMI 450L4 (L 2 025, H 450, HC 1 860) | 0,20–0,25 kWh/kg × 3 500 kg/h ≈ 800 kW; dự phòng tới 5 t/h, khởi động lạnh → ≈ 1 400 kW → cấp chuẩn 1 500 kW. Bảng KM chỉ cho công suất tối đa 2 930 kW (c004). specs.md ban đầu đề xuất 2 000 kW | design.md §3, §3.1; DECISIONS.md #11.3; specs.md §1.1 | không ghi |
| 2 | Làm mát động cơ | IC81W, bộ làm mát gió–nước trên nóc, giữ hình bao HC 1 860 của bản IC01; ≈ 45 kW nhiệt, 2 ống DN40 | Kích thước c066 chỉ cho bản IC01; giữ hình bao là giả định | design.md §3.1; review-01 M9; DECISIONS.md #11.3 | không ghi |
| 3 | Chiều cao động cơ | Đỉnh động cơ Z ≈ 2 610 (cao hơn hộp số ≈ 0,9 m) | Hình bóng trang 9 là hình mẫu chung nên không theo chiều cao đó | DECISIONS.md #11.3; design.md §4.3, §9 | không ghi |
| 4 | Tỷ số truyền hộp số | ≈ 3,73 (1 490 → 400 v/ph) | Động cơ 4 cực, tốc độ vít tối đa 400 v/ph (c003) | design.md §3 (ghi "giả định"); specs.md §1.1 | không ghi |
| 5 | Kích thước hộp số, lantern | Hộp số 1 550 × 1 400 × 1 070 mm (specs đề xuất ≈ 1 600 × 1 400 × 1 700, 8–10 t); lantern 750 × 900 × 1 010 mm | Phải chịu 2 × 35 kNm; hình khối theo web-11, web-01 | design.md §9; specs.md §1.1 | ước lượng |
| 6 | Hãng hộp số | Chưa rõ (Flender, Eisenbeiss hay Berstorff); vẽ màu xanh Flender | ZE 110 R dùng Flender (c023, c025); ZE 52 dùng Eisenbeiss (c026); ZE 180 ghi Berstorff (c018) | specs.md §1.1; design.md §7.15 | không ghi |
| 7 | Cao độ trục vào hộp số | Z = 1 200, đồng trục với mặt phẳng giữa hai trục vít | Chưa có nguồn | design.md §9 (chưa giải quyết #1) | không ghi |
| 8 | Chiều dài cụm truyền động | Đuôi động cơ tới cuối xi lanh ≈ 10 720 mm, dài hơn ≈ 7 % so với ≈ 10 000 suy từ bảng KM | Khớp đàn hồi + khớp an toàn tách rời (650 mm) và lantern 750 mm; review-01 M2 không áp dụng | design.md §9 (chưa giải quyết #3); DECISIONS.md #13 | không ghi |
| 9 | Kiểm mômen | Động cơ 9,6 kNm × 3,73 → ≈ 17,9 kNm mỗi trục = 51 % của 35 kNm | Tính từ công suất giả định | design.md §3.1 | không ghi |
| 10 | Cụm dầu bôi trơn | Bơm ≈ 60 L/ph, động cơ 4 kW đứng, lọc kép 25 µm, bộ làm mát tấm ≈ 30 kW; khay đế +Y trước động cơ | Thực hành thông thường; vị trí theo trang 9 và web-03 | design.md §7.10 | không ghi |
| 11 | Trục động cơ trong moay-ơ khớp | Outline cho trục dài 200 (không ăn vào moay-ơ); tờ 03 vẽ trục 320 lắp 120 (G) | Đơn giản hóa đã biết, nằm trong vỏ che | drawings/design_issues.md #10 | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `drive_safety_coupling`<br>Khớp an toàn giới hạn mômen (Torque-limiting safety coupling) | revolve; bao 400 × 640 × 640 (X × Y × Z); trục X; R 320 | c033 (safety coupling); p05/p19 (đĩa ly hợp bạc giữa động cơ và hộp số); cỡ giả định | design.md:350 |
| 2 | `drive_flex_coupling`<br>Khớp nối đàn hồi (Flexible coupling) | revolve; bao 250 × 560 × 560 (X × Y × Z); trục X; R 280 | giả định (khớp đĩa/đàn hồi tiêu chuẩn cỡ 10 kNm) | design.md:360 |
| 3 | `drive_motor`<br>Động cơ chính 1 500 kW, làm mát gió–nước trên nóc (Main AC motor 1 500 kW, IC81W top air-to-water cooler (ABB AMI 450L4 frame)) | extrude; bao 2025 × 1150 × 1860 (X × Y × Z); trục X | c066 (AMI 450L: L 2 025, H 450, HC 1 860, A 850, B 1 400, AB 980, AE 1 500); c065 khối lượng ≈ 4,7 t; công suất 1 500 kW giả định (xem design.md §3); DECISIONS 11.3 + review-01 M9: kiểu làm mát IC81W (bộ làm mát gió–nước trên nóc), giả định giữ nguyên hình bao HC 1 860 như bản IC01 | design.md:380 |
| 4 | `drive_motor_terminal_box`<br>Hộp đấu dây động cơ (Motor terminal box) | box; bao 600 × 350 × 500 (X × Y × Z) | c066 (AE 1 500 gồm hộp đấu dây); phía −Y giả định để tránh lối thao tác | design.md:390 |
| 5 | `drive_motor_base`<br>Đế động cơ (Motor sub-base) | frame; bao 2000 × 1200 × 100 (X × Y × Z) | giả định: 1 200 − H 450 − đỉnh khung 650 = 100 mm | design.md:400 |
| 6 | `drive_encoder`<br>Encoder tốc độ (Speed encoder) | cyl; bao 100 × 160 × 160 (X × Y × Z); trục X; R 80 | giả định (biến tần trung thế điều khiển vòng kín) | design.md:410 |
| 7 | `lube_pipe_pressure`<br>Ống dầu áp lực tới hộp số (Lube pressure line) | pipe; bao 817 × 96 × 471 (X × Y × Z); R 21 | web-03 (ống dầu sơn xanh); tuyến ống giả định | design.md:460 |
| 8 | `lube_pipe_return`<br>Ống hút dầu từ carter (Lube suction line) | pipe; bao 1900 × 300 × 50 (X × Y × Z); R 25 | giả định | design.md:470 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `drive_coupling_guard` | Vỏ che khớp bắt đầu ở X −3 168 thay vì −2 980, để che trục động cơ 200 mm (X −3 150…−2 950) | out/log.md:37 | Phase 1 — scene basics, blockout, base frame, drive train |
| 2 | `lube_pipe_pressure` | Ống dầu áp lực ra từ cổng F3 mặt +Y của bộ làm mát (theo web-03), đi ở Y 980 / Z 1 500; thiết kế bắt đầu ở nóc bộ làm mát | out/log.md:38 | Phase 1 — scene basics, blockout, base frame, drive train |
| 3 | `lube_filter_duplex → lube_oil_cooler` | Vào cổng F1 mặt +Y thay vì mặt −X: hai hộp bao chạm nhau ở X −2 950, không còn chỗ vào bên | out/log.md:39 | Phase 1 — scene basics, blockout, base frame, drive train |
| 4 | `lube_pump_motor` | Thân Ø224 (cánh Ø248) thay vì Ø260, để ống đẩy đứng ở X −3 212 không chạm động cơ | out/log.md:40 | Phase 1 — scene basics, blockout, base frame, drive train |
| 5 | `drive_motor` | Tấm cửa chớp nhô 30 mm (tới Y ±605); thêm chụp quạt NDE; bỏ tai cẩu trên nóc để giữ Z 2 610 | out/log.md:41 | Phase 1 — scene basics, blockout, base frame, drive train |
| 6 | `gearbox, drive_coupling_guard` | Tai cẩu cao hơn hộp bao (hộp số tới Z 1 860, vỏ che tới Z 1 772) | out/log.md:42 | Phase 1 — scene basics, blockout, base frame, drive train |
| 7 | `gearbox (gân)` | Gân bên vuốt kiểu gang đúc thay vì 28 × 24 không đổi; bo cạnh R55 | out/log.md:331 | Phase 4b — finishing: render quality, light, materials, casting look, cable density, final renders, report |

**Lỗi thiết kế do review phát hiện**

| # | Hạng mục | Phát hiện | Xử lý | Ghi ở đâu |
|---|---|---|---|---|
| 1 | Trục động cơ và khớp nối | Đầu trục dài 200 dừng đúng ở mặt moay-ơ, không ăn vào moay-ơ | Đơn giản hóa đã biết; tờ 03 chi tiết D vẽ trục 320 lắp 120 (G) | drawings/design_issues.md #10 |
| 2 | Chiều dài cụm truyền động | Dài hơn ≈ 7 % so với bảng KM (review-01 M2) | Không sửa (phần đó đang được dựng); chấp nhận | design/review-01.md M2; DECISIONS.md #13; design.md §9 #3 |

## Xi lanh và trục vít (barrel / screws)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Chia đoạn xi lanh | 1 × 4D (676) + 5 × 6D (1 014) = 34D = 5 746 mm | Catalogue có đoạn 4D và 6D (c031) | DECISIONS.md #4, #9; specs.md §1 | không ghi |
| 2 | Chức năng từng đoạn | B1 cấp liệu (áo nước), B2 mở bên (side feeder), B3 chân không vùng 1, B4 kín, B5 chân không sâu, B6 tăng áp | Thực hành cho PET không sấy; B3 đổi từ thoát khí khí quyển sang chân không sau review-01 I4 | design.md §1, §4.1, §10 I4; specs.md §1 | không ghi |
| 3 | Kiểu nối xi lanh | Mặt bích bắt bu-lông, không C-clamp | Ảnh ZE UT cỡ lớn (web-01/02); KM BluePower cỡ lớn nối bu-lông (c037) | DECISIONS.md #11.1; specs.md §1 | không ghi |
| 4 | Đường kính xi lanh và bích | Thân Ø520 (thắt Ø500 × 40 sau mỗi bích), bích Ø640 (ban đầu Ø600), 20 bu-lông cấy M24 trên PCD 560 | Lỗ số 8 rộng 311 + thành ≈ 105; tỷ lệ thân/bích ≈ 0,84 (trang 9); bích tăng Ø640 vì mép lỗ chỉ còn 7 mm (drawing review I6) | design.md §9, §10.2 I6; DECISIONS.md #17 | không ghi |
| 5 | Khoảng cách tâm hai trục | ≈ 142 mm (a = (D + d)/2) | Công thức khớp ZE 180 (c017) và ZE 110 (c020) | specs.md §1; design.md §3 | cao (ghi trong specs) |
| 6 | Đường kính lõi vít | 114,6 mm (D − 2 × rãnh); anim dùng lỗ 169, vít 167,5, lõi 116,5 | Tính từ c001/c002; anim coi 169 là lỗ xi lanh (chênh 1,9 mm, không thấy được) | specs.md §1; design-anim.md §10.6; review-anim-01 M1 | không ghi |
| 7 | Đường kính ngoài thực của vít | ≈ 167,5 mm | Cùng tỷ lệ 0,991 như ZE 180 (lỗ 194, vít 192,3; c017) | specs.md §1 | ước lượng |
| 8 | Công suất gia nhiệt xi lanh | ≈ 25 kW mỗi đoạn 6D (5 × 25 kW) | ZE 180: 30 kW/đoạn (c018), giảm theo cỡ máy | specs.md §1; design.md §3 | ước lượng |
| 9 | Vỏ che xi lanh | 6 vỏ che hộp C1–C6 (không vỏ tròn để lộ như ZE 110 trong ảnh) | Theo trang 9 và ảnh p16 | DECISIONS.md #11.2; out/report.md §6 | không ghi |
| 10 | Vòm chân không | Dạng hộp (B3 nhỏ, B5 lớn), kính quan sát tròn | Theo hình bóng trang 9; ảnh p01 có vòm tròn nhưng là máy UTX nhỏ | DECISIONS.md #16; design.md §8 | không ghi |
| 11 | Cấu hình trục vít | Trình tự phần tử giả định: tờ 02 vẽ 14 đoạn (G); anim dùng bảng 32 phần tử mỗi trục (SE 1,5D … KB 45°/5, KB 90°, LH, TIP) | Cấu hình thật của KM không công bố; logic: nhận hạt → nóng chảy → nút → thoát khí → trộn → nút ren trái → chân không sâu → tăng áp | design.md `screws`; drawings/design_issues.md #6; anim/interior_parts.json `screw_elements`; design-anim.md §2 | không ghi |
| 12 | Lỗ khoan nước làm mát | 8 lỗ Ø18 trên PCD 430 mỗi đoạn (G) | Không có nguồn; catalogue p05 chỉ cho thấy có lỗ khoan dọc | drawings/design_issues.md #6; anim/interior_parts.json | không ghi |
| 13 | Giãn nở nhiệt | Xi lanh cố định ở lantern; 5,75 m ở ΔT ≈ 250 K giãn ≈ 17 mm, đường chảy thêm ≈ 10 mm, tổng ≈ 28 mm tại khuôn | Tính từ hệ số giãn nở thép | design.md §7.6 | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `barrel_support_1`, `barrel_support_2`, `barrel_support_3`<br>Gối đỡ xi lanh số 1 (Barrel support saddle … | extrude; bao 250 × 700 × 384 (X × Y × Z) | web-02 (gối đúc trắng hình chữ A có lỗ); vị trí giả định: giữa B2, B4, B6, tránh các mối nối bích | design.md:248, design.md:258, design.md:268 |
| 2 | `barrel_b1`, `barrel_b2`, `barrel_b3`, `barrel_b4`, `barrel_b5`, `barrel_b6`<br>Xi lanh B1 – cấp liệu 4D (Barrel B1, feed barrel 4D … | revolve; bao 676 × 640 × 640 (X × Y × Z); trục X; R 260 / revolve; bao 1014 × 640 × 640 (X × Y × Z); trục X; R 260 | c001 D = 169, c031 đoạn 4D/6D, c032 thép thấm nitơ; DECISIONS 9 (1×4D + 5×6D), DECISIONS 11 (nối bích bắt bulông); hình trụ có bích theo trang 12 (p12_barrel_types_utx_vs_ut); Ø thân 520 / bích 600 giả định (lỗ số 8 rộng 311 + thành ≈ 105) | design.md:744…794 |
| 3 | `barrel_joint_1`, `barrel_joint_2`, `barrel_joint_3`, `barrel_joint_4`, `barrel_joint_5`<br>Mối nối bích bắt bulông 1 (X = 676) (Bolted flange joint … | revolve; bao 164 × 600 × 600 (X × Y × Z); số lượng 20; trục X; R 320 | c037 (ZE cỡ lớn nối các đoạn bằng bulông thay kẹp), web-01/02 (vành bích bắt bulông trên ZE 110 R UT thật); DECISIONS 11; cỡ bulông giả định (tính lực siết, kiểm tra chỗ đặt đai ốc) | design.md:804…844 |
| 4 | `barrel_heater_shells`<br>Băng nhiệt gốm bọc inox (Ceramic band heater shells) | revolve; bao 4890 × 580 × 580 (X × Y × Z); số lượng 10; trục X | web-01/02 (vỏ nhiệt inox bóng, mép có gân); c018 (30 kW/đoạn trên ZE 180) → 25 kW giả định | design.md:854 |
| 5 | `screws`<br>Hai trục vít đồng hướng (Co-rotating twin screws) | composite; bao 6146 × 309.6 × 167.6 (X × Y × Z); trục X | c001/c002 (D 169, rãnh 27,2 → lõi 114,6), centre distance 142 (specs §1); c017 (then hoa 24 răng trên ZE 180); trình tự phần tử giả định | design.md:864 |
| 6 | `barrel_vent_dome_2`<br>Vòm thoát khí chân không vùng 1 (B3) (First vacuum vent dome on B3) | extrude; bao 400 × 450 × 505 (X × Y × Z) | review-01 I4 (PET không sấy: hút chân không ngay sau vùng chảy, c040, c062); cỡ giả định | design.md:874 |
| 7 | `barrel_thermocouples`<br>Cặp nhiệt xi lanh (Barrel thermocouples) | cyl; bao 4931 × 230 × 227 (X × Y × Z); số lượng 6 | giả định (mỗi vùng 1 cặp nhiệt, như cáp nhiệt thấy ở web-01); vị trí theo review-01 C1 | design.md:954 |
| 8 | `barrel_cable_tray`<br>Máng cáp nhiệt (Heater cable tray) | sheet; bao 6800 × 300 × 100 (X × Y × Z) | web-01 (máng thép mạ kẽm đục lỗ dọc dưới xi lanh); phía −Y giả định | design.md:1014 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `barrel_b1` | Bệ gia công cho miệng nạp Y ±150 (hộp miệng nạp nhô 60 mm mỗi bên), để cặp nhiệt nghiêng của B1 ra khỏi thân tròn | out/log.md:85 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 2 | `barrel_b2 / b3 / b5` | Thêm bệ gia công (cửa bên, đế vòm) vì bích phẳng và đế vòm không ngồi được trên trụ Ø520; vỏ nhiệt có cửa sổ | out/log.md:86 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 3 | `barrel_support_1..3` | Thân gối dày 70 mm suốt chiều cao, 4 gân đúc (giữ tấm đế 250 × 700): thân rộng 250 sẽ chạm vỏ nhiệt, băng trần chỉ rộng 74 mm | out/log.md:87 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 4 | `lantern_bolts → barrel_joint_lantern` | Bỏ 16 × M36 PCD 620 của phase 1; mối B1/lantern dùng 20 bu-lông cấy M24 PCD 560, đai ốc 12 cạnh hai mặt (review M1) | out/log.md:89 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 5 | `barrel_cw_hoses` | Ống mềm nước kết thúc ở đầu khớp nối (r 300 trên đầu nối 45°; B1 dưới đầu nối đáy Z 902), không ở điểm trên mặt xi lanh | out/log.md:90 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 6 | `barrel_cover (tam giác cảnh báo)` | Tam giác cảnh báo ở Z 1 158…1 253 trên nắp; bản vẽ đặt giữa trên đường ghép Z 1 134 | out/log.md:91 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 7 | `vành bích xi lanh` | Vát 5 mm (biên dạng còn lại đúng parts.json) | out/log.md:230 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 8 | `cáp phía +Y (barrel_cable_duct_op …)` | Thêm máng cáp, cáp nhiệt, dây cặp nhiệt, gland phía +Y (design không nói; mật độ theo web-02) | out/log.md:330 | Phase 4b — finishing: render quality, light, materials, casting look, cable density, final renders, report |

**Lỗi thiết kế do review phát hiện**

| # | Hạng mục | Phát hiện | Xử lý | Ghi ở đâu |
|---|---|---|---|---|
| 1 | Lõi vít 114,6 mm | Bản nháp anim gọi lõi 114,6 của design là sai | Reviewer xác nhận 114,6 là cặp tự làm sạch hợp lệ; anim giữ mô hình 116,5 nhưng không gọi design sai | review-anim-01 M1; design-anim.md §10.6 |
| 2 | Thoát khí B3 cho PET không sấy | Design ban đầu có cửa thoát khí khí quyển ngay sau vùng chảy và chỉ một vùng chân không | Đổi B3 thành vòm chân không vùng 1 (≈ 50 mbar), thêm van, ống DN100 | design/review-01.md I4; design.md §10 I4 |
| 3 | Bích xi lanh | Vòng bu-lông chỉ còn mép 7 mm, không có chỗ vặn khẩu | Bích Ø600 → Ø640, cổ thắt Ø500 × 40 | drawings/review-01.md I6; design.md §10.2 I6; DECISIONS.md #17 |
| 4 | Nút nhựa dưới lỗ thoát khí | Trong cấu hình vít, nút nhựa nằm dưới lỗ thoát khí | Nút KB 90° kết thúc ở X 1 950, trước lỗ vùng 1 | drawings/review-01.md M8; design.md §10.2 (M8) |
| 5 | Hộp bao cặp nhiệt B1 | bbox_mm z0 = 1 321 vẫn theo vị trí cũ; vị trí mới đáy ở Z ≈ 1 361 | Còn sót, không sửa (thiết kế đóng băng) | drawings/design_issues.md #7 |

## Cấp liệu (feeding)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Lưu lượng các cân | Cân chính ≈ 3 300* + biên tấm ≈ 160* + phụ gia ≈ 40* = 3 500 kg/h tổng | Phân bổ giả định cho cân bằng khối lượng | design-anim.md §2 (bước 1); review-anim-01 M5 | giả định (*) |
| 2 | Thể tích hạt cấp | 3 500 kg/h ÷ 0,8 kg/dm³ ≈ 4 400 dm³/h, trong dải K-Tron BSP-150-S (34–6 700 dm³/h) | Mật độ khối hạt PET 0,8 là giả định; dải cân có nguồn (c069) | specs.md §2; design.md §3 | không ghi |
| 3 | Miệng nạp B1 | 300 × 250 (specs) → nới 360 × 300 cho D 169; anim làm lỗ rộng 280 | Chưa tìm thấy kích thước thật | specs.md §2; design.md `feed_throat`; anim/log.md:78 | không ghi |
| 4 | Sàn đặt cân | Mặt sàn Z ≈ 3 000 (2 800–3 200), lan can vàng, cầu thang phía −Y | Theo ảnh dây chuyền Lanxess (web-04/05) | specs.md §2; design.md §4.1 | ước lượng |
| 5 | Side feeder | ZSB 160 trục vít đôi, phía +Y vào B2, động cơ 22 kW, trên xe có bánh; cấp biên tấm nghiền hoặc phụ gia bột | Tỷ lệ với ZSFE 120 trên ZE 110 (c024); xe theo p06 | design.md §7.3 | không ghi |
| 6 | Cân phụ gia | 1–2 cân trục vít đôi nhỏ (cỡ K-ML-D5-T35) | Ước lượng | specs.md §2 | ước lượng |
| 7 | Khí trơ ở phễu | Cổng N₂ nhỏ (chỉ dựng cổng) | Giảm oxy hóa PET | design.md §7.2 | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `feed_throat`<br>Hộp miệng nạp (Feed throat housing) | box; bao 500 × 420 × 185 (X × Y × Z) | giả định (miệng nạp 300 × 250 theo specs §2, nới thành 360 × 300 cho D 169) | design.md:482 |
| 2 | `feed_flex_sleeve`<br>Ống mềm nối phễu (Flexible sleeve) | pipe; bao 293.8 × 260 × 293.8 (X × Y × Z); R 130 | giả định (ống mềm nối phổ biến dưới cân cấp liệu, thấy ở p01) | design.md:502 |
| 3 | `feed_downpipe`<br>Ống rơi liệu chính (Main feed down-pipe) | pipe; bao 753.4 × 250 × 928.4 (X × Y × Z); R 125 | giả định (bố trí sàn cân trên cao theo web-04); ống mềm cách cân theo review-01 M8 | design.md:512 |
| 4 | `feed_main_feeder`<br>Cân cấp liệu chính (loss-in-weight) (Main loss-in-weight feeder (K-Tron BSP-150-S)) | composite; bao 1100 × 900 × 700 (X × Y × Z) | c069 (K-Tron BSP-150-S, 34–6 700 dm³/h, 3 cảm biến cân); kích thước thân giả định | design.md:522 |
| 5 | `feed_main_hopper`<br>Phễu cân chính (Main feeder extension hopper) | revolve; bao 900 × 900 × 1200 (X × Y × Z); trục Z; R 450 | c069 (phễu nối thêm); dung tích giả định lớn hơn 320 dm³ để thời gian nạp lại hợp lý | design.md:532 |
| 6 | `feed_vacuum_loader`<br>Máy hút liệu chân không (Vacuum loader / receiver) | revolve; bao 640 × 640 × 900 (X × Y × Z); trục Z; R 320 | specs §2 (máy hút liệu trên phễu); cỡ giả định | design.md:542 |
| 7 | `feed_conveying_line`, `feed_additive_tube`, `feed_platform_columns_rear`, `feed_platform_columns_front`, `feed_control_cabinet`, `sidefeed_downpipe`, `sidefeed_feeder_hopper`<br>Ống hút liệu từ silo (Pneumatic conveying line … | pipe; bao 80 × 420 × 840 (X × Y × Z); R 40 / pipe; bao 278.6 × 775.6 × 190 (X × Y × Z); R 40 / frame; bao 4550 × 200 × 2780 (X × Y × Z); số lượng 3 / box; bao 600 × 300 × 1400 (X × Y × Z) / pipe; bao 150 × 150 × 1250 (X × Y × Z); R 75 / revolve; bao 600 × 600 × 700 (X × Y × Z); trục Z; R 300 | giả định | design.md:552…732 |
| 8 | `feed_additive_feeder`<br>Cân phụ gia / masterbatch (Additive micro-feeder) | composite; bao 700 × 500 × 1200 (X × Y × Z) | specs §2 (cân trục vít đôi nhỏ K-ML-D5-T35); giả định | design.md:562 |
| 9 | `feed_feeder_sleeves`<br>Ống mềm cách cân ở cửa xả (Feeder outlet flexible sleeves) | cyl; bao 2270 × 1220 × 150 (X × Y × Z); số lượng 3 | review-01 M8; giả định (thực hành chuẩn cho cân loss-in-weight) | design.md:582 |
| 10 | `feed_platform_deck`<br>Sàn thao tác cân cấp liệu (Feeder mezzanine deck) | frame; bao 4550 × 4100 × 220 (X × Y × Z) | web-04/05 (cân trên tầng lửng); specs §2 (mặt sàn 2 800–3 200); kích thước giả định | design.md:592 |
| 11 | `sidefeed_barrel`<br>Thân side feeder trục vít đôi (ZSB) (Twin-screw side feeder barrel (ZSB, size assumed)) | box; bao 330 × 770 × 260 (X × Y × Z); trục Y | p08_side_feeder, p06 cutaway (side feeder 2 trục vít ngang vào hông xi lanh); c024 (ZE 110 dùng ZSFE 120) → cỡ 160 giả định | design.md:662 |
| 12 | `sidefeed_gearbox`<br>Hộp số side feeder (Side-feeder gearbox) | box; bao 350 × 350 × 400 (X × Y × Z) | p06 cutaway (hộp số + động cơ xám nhỏ trên xe đẩy); màu giả định | design.md:682 |
| 13 | `sidefeed_motor`<br>Động cơ side feeder 22 kW (Side-feeder motor 22 kW) | cyl; bao 360 × 600 × 380 (X × Y × Z); trục Y; R 180 | giả định (động cơ AC 22 kW biến tần) | design.md:692 |
| 14 | `sidefeed_feeder`<br>Cân cấp liệu side feeder (Side-feeder loss-in-weight feeder) | composite; bao 700 × 600 × 550 (X × Y × Z) | giả định (cân trục vít đôi cỡ K-ML-D5-T35) | design.md:722 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `feed_platform columns` | Thêm giằng góc dưới dầm biên và dầm chính (design ghi "giằng góc", bản vẽ không có) | out/log.md:95 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |

## Chân không (vacuum)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Hai vùng chân không | B3 ≈ 50 mbar (vùng 1), B5 5–20 mbar (vùng 2) | Thực hành cho PET không sấy; compounding thường 100–300 mbar (c061); PET không sấy tới ≈ 10 Pa (c062, độ tin cậy thấp) | design.md §1, §3, §7.1, §9 | thấp (c062) |
| 2 | Cỡ cụm bơm | Roots ≈ 2 000 m³/h trên bơm trục vít khô ≈ 400 m³/h, chung một bình tách có ống xoắn làm lạnh (nước 10–15 °C) | Chưa có nguồn đáng tin cho PET 3,5 t/h | design.md §7.1, §9 (chưa giải quyết #4) | không ghi |
| 3 | Tải ẩm | PET không sấy 0,2–0,4 % ẩm → ≈ 7–14 kg/h nước ở 3,5 t/h | Giá trị điển hình | design.md §7.1 | không ghi |
| 4 | Cửa thoát khí B5 | Miệng dài 6D ≈ 1 000 × 300 mm; ống DN150 đi lên rồi sang bình tách | Chiều dài 6D có nguồn (c036); bề rộng ước lượng từ lỗ 311 mm | specs.md §3 | ước lượng |
| 5 | Skid chân không | ≈ 2 000 × 1 200 × 1 800 mm, phía −Y cạnh B5 | Hình dáng theo web-15 (Busch PLASTEX, c060); TK-V (c063) | specs.md §3 | ước lượng |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `vac_valve`<br>Van chặn chân không DN150 (vùng 2) (Vacuum shut-off valve DN150 (zone 2)) | composite; bao 200 × 410 × 110 (X × Y × Z) | giả định (van bướm có bộ tác động khí nén); đặt đứng trên nắp vòm theo review-01 M4 | design.md:1026 |
| 2 | `vac_pipe`<br>Ống hút chân không DN150 (vùng 2) (Vacuum line DN150 (zone 2)) | pipe; bao 168 × 2444 × 484 (X × Y × Z); R 84 | giả định (DN150 theo specs §3); cao độ theo review-01 M4 | design.md:1046 |
| 3 | `vac_pipe_support`, `vac_bleed_valve`, `vac_exhaust`<br>Cột đỡ ống chân không (Vacuum pipe support … | frame; bao 100 × 100 × 2216 (X × Y × Z) / composite; bao 80 × 80 × 145 (X × Y × Z) / pipe; bao 120 × 120 × 2000 (X × Y × Z); R 60 | giả định | design.md:1056, design.md:1156, design.md:1186 |
| 4 | `vac_gauge_dome`<br>Đồng hồ chân không trên vòm B5 (Vacuum gauge on dome (zone 2)) | cyl; bao 60 × 60 × 150 (X × Y × Z) | p01 (đồng hồ trên đường chân không); giả định | design.md:1066 |
| 5 | `vac_valve_2`, `vac_bellows_2`, `vac_pipe_3`, `vac_reg_valve_2`, `vac_gauge_dome_2`<br>Van chặn chân không DN100 (vùng 1) (Vacuum shut-off valve DN100 (zone … | composite; bao 130 × 80 × 130 (X × Y × Z) / cyl; bao 150 × 160 × 150 (X × Y × Z); trục Y; R 75 / pipe; bao 1727 × 2277 × 964 (X × Y × Z); R 57 / composite; bao 160 × 160 × 140 (X × Y × Z) / cyl; bao 60 × 60 × 150 (X × Y × Z) | review-01 I4; giả định | design.md:1076…1116 |
| 6 | `vac_pipe_2`<br>Ống chân không tới bơm (Vacuum line to pump) | pipe; bao 524 × 168 × 184 (X × Y × Z); R 84 | giả định; nâng lên DN150 theo drawing review-01 M1 | design.md:1146 |
| 7 | `vac_pump_unit`<br>Cụm bơm chân không (Vacuum pump unit (Roots + dry backing pump)) | composite; bao 1800 × 1100 × 1500 (X × Y × Z) | c059/c060 (Busch MINK, PLASTEX), c062 (PET không sấy dùng Roots hai cấp); cỡ giả định (design.md §7) | design.md:1166 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `bích chân không DN150 / DN100` | Bích DN150 r 112 (vừa hộp bao) thay vì PN16 Ø285; bích DN100 Ø220 để khớp bích ra của vòm | out/log.md:92 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 2 | `vac_pipe_3` | Thêm 2 cột đỡ sàn có gối tại (2 150, −1 900) và (2 900, −2 700): đoạn đi cao 4 m không có đỡ | out/log.md:93 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |

**Lỗi thiết kế do review phát hiện**

| # | Hạng mục | Phát hiện | Xử lý | Ghi ở đâu |
|---|---|---|---|---|
| 1 | Ống chân không sau bình tách | Ống sau bình tách nhỏ hơn cần thiết | Nâng lên DN150 | drawings/review-01.md M1; design.md §10.2 (M1) |

## Đường chảy nhựa (melt line)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Chọn bộ lọc lưới | Gneuss RSFgenius 200 (4 560 kg/h, 3 800 kg, 39 kW 6 vùng); phương án nhỏ RSFgenius 175 | Số liệu hãng có nguồn (c050, c051); việc chọn model là giả định theo năng suất | specs.md §4; design.md §3 | không ghi |
| 2 | Cách hiểu kích thước Gneuss | B = dày theo chiều chảy, D = cao tâm nhựa trên đáy, E = rộng thân, A = tổng rộng kể tay quay | Hãng không ghi rõ ý nghĩa các chữ | design.md §9; specs.md §4 | không ghi |
| 3 | Chọn bơm bánh răng | Maag extrex6 GU 100/125 (764 cm³/v, ≤ 370 bar) | Số liệu có nguồn (c047, c049); chọn model là giả định | specs.md §4; design.md §3 | không ghi |
| 4 | Thân bơm | ≈ 500 × 450 × 450 (specs); 450 × 530 × 460 mm (design) | Không có bản vẽ hãng | specs.md §4; design.md `melt_gear_pump` | ước lượng |
| 5 | Tốc độ bơm | Design ghi ≈ 105 v/ph (sai cho PET); anim/web dùng ≈ 69 v/ph | 105 từ bảng Maag (≈ 0,73 kg/L); PET nóng chảy 1,17 kg/L, hiệu suất 0,95 → 68,7 v/ph | design.md §3; design-anim.md §10.2; review-anim-01 "Verified OK" | không ghi |
| 6 | Động cơ bơm | 45 kW, hộp giảm tốc góc i ≈ 14, động cơ đứng, nối các-đăng | Công suất thủy lực ≈ 0,81 L/s × 200 bar ≈ 16 kW + hiệu suất + dự phòng | design.md §3; specs.md §4 | không ghi |
| 7 | Van khởi động | Kiểu chốt xoay hai vị trí, xi lanh thủy lực theo Y (design); anim dùng chốt trượt 200 mm | Xi lanh theo Y đẩy thẳng đầu chốt | design.md §7.4; design-anim.md §10.4 | không ghi |
| 8 | An toàn áp | Đĩa nổ 350 bar ở đầu xi lanh và sau bơm; P1 ngắt 350 bar, P4 ngắt 330 bar | Bơm tạo được tới 370 bar (c049); review-01 I5 | design.md §1, §7.5 | không ghi |
| 9 | Cao độ đường chảy | Tâm nhựa giữ Z = 1 200 suốt tới môi khuôn | Để đơn giản | specs.md §4 | không ghi |
| 10 | Chiều dài đường chảy | Cuối xi lanh → cửa khuôn ≈ 2 500–3 000 (specs); thiết kế X 5 746 → 9 126 = 3 380 mm | Cộng chiều dày từng khối | specs.md §4, §8; design.md §4.1 | ước lượng |
| 11 | Bộ trộn tĩnh, ống | DN ≈ 120, dài 500–600 mm; ống có gia nhiệt, cách nhiệt, vỏ inox | Tùy chọn thường gặp | specs.md §4; design.md §4.1 | ước lượng |
| 12 | Bảng bích đường chảy | Lòng chảy, PCD, số bu-lông các bích (G trên tờ 04) | Không có nguồn | drawings/design_issues.md #5; design.md §6.3 | không ghi |
| 13 | Trục đĩa lọc | Design đặt "trục đĩa" ở mặt −Y; anim đặt trục song song dòng chảy, tay quay tác động vành đĩa qua cóc (giả định) | Về vật lý trục đĩa phải song song dòng | design-anim.md §10.3; review-anim-01 "Verified OK" | không ghi |
| 14 | Gia nhiệt đường chảy | Bích/ống ≈ 35 kW; tổng gia nhiệt cả máy ≈ 260 kW | Bộ lọc 39 kW có nguồn (c050); phần còn lại giả định | design.md §3 | không ghi |
| 15 | Giá đỡ trượt | Giá van, giá lọc, giá bơm, xe khuôn có tấm trượt PTFE ±40 mm theo X | Cho giãn nở nhiệt | design.md §7.6; review-01 I8 | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `melt_stand_sc`<br>Giá đỡ bộ lọc lưới (Screen changer stand) | frame; bao 800 × 1200 × 650 (X × Y × Z) | giả định: Gneuss giao bộ lọc kèm khung; chiều cao = 1 200 − D 550 (c050) | design.md:278 |
| 2 | `melt_stand_pump`<br>Giá đỡ bơm nhựa và ống (Gear pump and melt pipe stand) | frame; bao 1250 × 900 × 970 (X × Y × Z) | giả định: khung riêng cho bơm như ảnh web-07 (khung đỡ dưới đường chảy); rút ngắn để xe khuôn chạy vào dưới bộ trộn | design.md:288 |
| 3 | `melt_pipe_saddles`, `melt_drain_chute`, `melt_purge_cart`, `melt_sc_adapter_in`, `melt_sensor_p2`, `melt_hyd_hoses_sc`, `melt_hyd_hoses_suv`, `melt_pump_adapter_in`, `melt_sensor_p3`, `melt_pump_adapter_out`, `melt_sensor_p4`, `melt_die_adapter`, `melt_sensor_die`<br>Gối đỡ ống nhựa (Melt pipe … | box; bao 460 × 240 × 80 (X × Y × Z); số lượng 2 / box; bao 250 × 250 × 420 (X × Y × Z) / box; bao 520 × 800 × 520 (X × Y × Z) / revolve; bao 150 × 420 × 420 (X × Y × Z); trục X; R 210 / cyl; bao 60 × 60 × 245 (X × Y × Z) / pipe; bao 106 × 915 × 26 (X × Y × Z); số lượng 2; R 13 / pipe; bao 339.4 × 1151.9 × 175.7 (X × Y × Z); số lượng 2; R 13 / revolve; bao 175 × 360 × 360 (X × Y × Z); trục X; R 180 / revolve; bao 150 × 300 × 300 (X × Y × Z); trục X; R 150 / composite; bao 200 × 500 × 360 (X × Y × Z) / cyl; bao 80 × 40 × 246 (X × Y × Z); số lượng 2 | giả định | design.md:298…1468 |
| 4 | `melt_valve_support`<br>Giá đỡ van khởi động (Diverter valve support bracket) | extrude; bao 140 × 520 × 380 (X × Y × Z) | review-01 I8; giả định | design.md:308 |
| 5 | `pump_drive_pedestal`<br>Bệ hộp giảm tốc bơm (Gear pump drive pedestal) | frame; bao 500 × 450 × 950 (X × Y × Z) | giả định: bố trí như web-07 (hộp giảm tốc + động cơ đứng cạnh bơm) | design.md:318 |
| 6 | `melt_rupture_disc`<br>Đĩa nổ an toàn (Rupture disc) | cyl; bao 40 × 120 × 40 (X × Y × Z); trục Y; R 20 | giả định (thiết bị an toàn tiêu chuẩn của máy đùn) | design.md:1208 |
| 7 | `melt_sensor_head`<br>Cảm biến áp suất + nhiệt nhựa đầu xi lanh (P1, T1) (Head melt pressure + temperature (P1, T1)) | cyl; bao 80 × 40 × 286 (X × Y × Z); số lượng 2 | p01 (cảm biến áp suất có cáp trên đầu ra); giả định | design.md:1218 |
| 8 | `melt_startup_valve`<br>Van khởi động / chuyển hướng (Start-up (diverter) valve) | box; bao 450 × 520 × 520 (X × Y × Z) | c035 (diverter valve trong sơ đồ catalogue); kích thước theo specs §4 (giả định) | design.md:1228 |
| 9 | `melt_startup_cyl`<br>Xi lanh thuỷ lực van khởi động (Diverter valve hydraulic cylinder) | cyl; bao 160 × 600 × 160 (X × Y × Z); trục Y; R 80 | specs §4 (xi lanh thuỷ lực nằm ngang); giả định phía −Y | design.md:1238 |
| 10 | `melt_screen_changer`<br>Bộ lọc lưới quay xả ngược (Backflush screen changer (Gneuss RSFgenius 200)) | extrude; bao 705 × 1040 × 1429 (X × Y × Z) | c050 (RSFgenius 200: A 1 955 / B 705 / C 1 429 / D 550 / E 1 040, 3 800 kg, 39 kW 6 vùng, 200 bar); web-13; c043; cách hiểu B = dày theo dòng chảy, D = cao tâm nhựa trên đáy, E = rộng thân là giả định | design.md:1288 |
| 11 | `melt_sc_drive`<br>Tay quay thuỷ lực bộ lọc (Screen changer hydraulic drive arm) | composite; bao 400 × 565 × 350 (X × Y × Z) | web-13 (tay quay + xi lanh nhô một bên); A − E = 1 955 − 1 040 chia hai bên (giả định) | design.md:1298 |
| 12 | `melt_hpu`<br>Bộ nguồn thuỷ lực (Hydraulic power unit) | composite; bao 850 × 700 × 1200 (X × Y × Z) | c043 (bộ lọc dẫn động thuỷ lực); cỡ giả định; lùi về Y −2 700 … −2 000 theo review-01 I2 | design.md:1318 |
| 13 | `melt_gear_pump`<br>Bơm bánh răng nhựa (Melt gear pump (Maag extrex6 GU 100/125)) | box; bao 450 × 530 × 460 (X × Y × Z) | c047 (764 cm³/v, 4 474 kg/h ở 134 v/ph → ≈ 105 v/ph ở 3 500 kg/h), c049 (370 bar), web-14; kích thước thân giả định | design.md:1368 |
| 14 | `melt_pump_motor`<br>Động cơ bơm 45 kW (Gear pump motor 45 kW (vertical)) | cyl; bao 440 × 440 × 850 (X × Y × Z); trục Z; R 220 | web-07 (động cơ đứng trên hộp số); công suất giả định (thuỷ lực ≈ 16 kW, hiệu suất + dự phòng) | design.md:1398 |
| 15 | `melt_pipe`<br>Ống nhựa nóng có gia nhiệt (Heated melt pipe) | revolve; bao 350 × 300 × 300 (X × Y × Z); trục X; R 150 | specs §4 (ống gia nhiệt, cách nhiệt, vỏ inox); giả định | design.md:1438 |
| 16 | `melt_static_mixer`<br>Bộ trộn tĩnh (Static mixer) | revolve; bao 500 × 300 × 300 (X × Y × Z); trục X; R 150 | specs §4 (tuỳ chọn DN ≈ 120, dài ≈ 600); giả định | design.md:1448 |
| 17 | `melt_heater_bands`<br>Băng nhiệt đường chảy (lộ ra ngoài) (Melt line heater bands (visible)) | revolve; bao 3234 × 514 × 514 (X × Y × Z); số lượng 6 | giả định; vị trí theo review-01 C1 | design.md:1478 |
| 18 | `melt_heater_jbox`, `melt_heater_conduits`<br>Hộp đấu nhiệt đường chảy (Melt-line heater junction … | box; bao 600 × 250 × 800 (X × Y × Z) / pipe; bao 2870 × 705 × 380 (X × Y × Z); số lượng 7; R 15 | review-01 I6; giả định | design.md:1488, design.md:1498 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `melt_head_adapter` | Bích vào Ø640 × 50 (parts.json 60) để bu-lông cấy B6 mang đai ốc; moay-ơ bậc Ø490/Ø430 thay vì côn thẳng để băng nhiệt ngồi trên trụ | out/log.md:148 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 2 | `melt_valve_support` | Giá ở X 6 000–6 090 (thiết kế 5 950–6 090) vì tấm bịt đầu khung chiếm X 5 950–6 000 | out/log.md:149 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 3 | `melt_screen_changer (mũ)` | Mũ lật: đỉnh ở phía −Y (phía dẫn động), mép thấp phía xả ngược +Y, theo web-13; bản vẽ đặt đỉnh ở +Y | out/log.md:150 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 4 | `melt_screen_changer (thân)` | Khối thân X 6 616–7 281; tấm nắp và đĩa bích lấp X 6 596–6 616 / 7 281–7 301 | out/log.md:151 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 5 | `melt_startup_valve` | Khối Y ±230, bệ chốt xoay tới ±252, đầu chốt tới −260; 12 vít chìm tới bích kề không dựng (nằm trong mối nối) | out/log.md:152 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 6 | `melt_heater_conduits` | Ống luồn kết thúc ở đầu gland hộp đấu (≤ 45 mm từ điểm thiết kế), bo góc R70, thêm giá đỡ | out/log.md:153 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 7 | `melt_sensor_tray (mới)` | Máng mạ kẽm 70 × 40 dọc Y −560 mang cáp P1…P5/T và tín hiệu đĩa nổ tới hộp nhiệt (design chỉ ghi "qua hào") | out/log.md:154 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 8 | `melt_hyd_hose_fittings` | Thêm cột đỡ sàn có gối ở Y −1 550: ống thủy lực 0,9–1,15 m băng qua lối đi không có đỡ | out/log.md:155 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 9 | `melt_pipe / melt_static_mixer` | Vỏ bọc dừng cách mỗi bích 80 mm để có chỗ cho 8 × M24 PCD 255; design vẽ vỏ Ø300 từ bích tới bích | out/log.md:156 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 10 | `melt_pump_motor` | Thân Ø350, cánh tới Ø375, hộp đấu dây hướng +X trong r 220 | out/log.md:157 | Phase 3 — melt line, T-die, die cart, roll stack context |

**Lỗi thiết kế do review phát hiện**

| # | Hạng mục | Phát hiện | Xử lý | Ghi ở đâu |
|---|---|---|---|---|
| 1 | Tốc độ bơm bánh răng | Design ghi ≈ 105 v/ph ở 3 500 kg/h. Con số này theo bảng Maag (4 474 kg/h ở 134 v/ph), ứng với ≈ 0,73 kg/L (nhựa polyolefin). Với PET nóng chảy 1,17 kg/L, hiệu suất 0,95: 2,99 m³/h ÷ (0,764 L × 0,95) = 68,7 v/ph | Anim và web dùng 69 v/ph; design.md và specs.md giữ 105 (thiết kế đã đóng băng) | review-anim-01 "Verified OK – Gear pump"; design-anim.md §10.2; design.md §3; specs.md §4 |
| 2 | Trục đĩa bộ lọc | Design đặt "trục đĩa" ở mặt −Y; về vật lý trục đĩa phải song song dòng chảy (X) | Anim đặt trục song song dòng; tay quay −Y tác động lên vành đĩa qua cóc (giả định) | design-anim.md §10.3; review-anim-01 "Verified OK – Screen changer" |
| 3 | Van khởi động | Design ghi "chốt xoay" nhưng xi lanh theo Y đẩy thẳng đầu chốt | Anim dùng chốt trượt 200 mm | design-anim.md §10.4; review-anim-01 M4 |
| 4 | Bảo vệ áp sau bơm | Không có gì bảo vệ đường chảy sau bơm bánh răng (bơm tạo được 370 bar) | Thêm đĩa nổ 2 (350 bar), P4 ngắt ở 330 bar | design/review-01.md I5; design.md §10 I5 |

## Khuôn chữ T (T-die)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Bề rộng khe môi | 2 400 mm (tấm 2 100 + ≈ 150 mỗi bên cho co hẹp và xén biên) | Reifenhäuser làm khuôn 75–3 500 mm (c056) | specs.md §0, §5; DECISIONS.md #10 | không ghi |
| 2 | Bề rộng thân | ≈ 2 750 mm kể tấm đầu; ≈ 3 050 kể hộp đầu nối, deckle | Ước lượng | specs.md §5 | ước lượng |
| 3 | Cao và sâu thân khuôn | Cao ≈ 500 (nửa trên 260, nửa dưới 240); sâu 450 mm (X 9 126–9 576) | Tỷ lệ theo ảnh web-19/20; giữ 450 mm (không lùi tới X 9 060) | specs.md §5; design.md §9; DECISIONS.md #18, #20, #21 | ước lượng |
| 4 | Khối lượng khuôn | ≈ 3,4 t (design, tính từ outline); specs ước ≈ 2 000 kg | Cloeren 62" nặng 1 032 kg (c055), quy theo bề rộng | design.md §3; specs.md §5 | ước lượng |
| 5 | Số bu-lông nhiệt | 94 bu-lông nhiệt bước 25,4 mm (94 × 25,4 = 2 388), 80 W | Bước có nguồn (c053, c054); số lượng suy ra | specs.md §5; design.md §1 | không ghi |
| 6 | Bu-lông thanh chắn | 33 bu-lông đứng ở X 9 255 (specs ước bước ≈ 50–75 mm) | Theo ảnh web-19; vị trí sửa sau ghi chú drafter #1 | specs.md §5; design.md §10.1 | không ghi |
| 7 | Gia nhiệt khuôn | 9 vùng mỗi nửa (bước ≈ 270) + 2 tấm đầu = 20 vùng, ≈ 50 kW; bu-lông nhiệt 7,5 kW | Khuôn Cloeren 1 575 mm dùng 32,8 kW (c055), tức ≈ 21 kW/m | specs.md §5; design.md §3, §7.14 | ước lượng |
| 8 | Kết cấu trong khuôn | Ống phân phối Ø72 → Ø28, preland khe 3–6, môi dài 156, thanh nhiệt Ø20 (G); anim: móc áo gần chữ T (tiền môi 32 → 11 mm) | Không có dữ liệu hãng; thân 450 mm quá chật | drawings/design_issues.md #4; design.md §9 (chưa giải quyết #6); design-anim.md §10.5, Q2 | không ghi |
| 9 | Vít thân khuôn | 94 vít M30 10.9 chìm, bước 110; hàng vít đi qua ống phân phối (đơn giản hóa đã biết) | Cỡ và vị trí tính lực kẹp; không sửa vì thiết kế đã đóng băng | design.md §10.2 I4; drawings/design_issues.md #9; DECISIONS.md #21 | không ghi |
| 10 | Khe gió môi khuôn → khe trục | 200 mm (thường 50–150 mm cho PET) | Trục Ø800 và mũi vát 30°; giữ khuôn nằm ngang | DECISIONS.md #11.4; design.md §7.7, §9 (chưa giải quyết #5) | không ghi |
| 11 | Hướng khuôn | Nằm ngang, môi chĩa vào khe trục giữa–dưới của cụm 3 trục đứng | Sơ đồ catalogue trang 24–25; thay quyết định 8 (chill roll dưới khuôn) | DECISIONS.md #10 | không ghi |
| 12 | Xe khuôn | Đế X 8 700–9 380, khổ ray 560 mm, trọng tâm ≈ 1,15 m trên ray | Khuôn ≈ 3,4 t; review-01 I3 (khổ ban đầu 160 mm) | design.md §7.8, §10 I3 | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `die_body_upper`<br>Nửa khuôn trên (có môi mềm) (Upper die body (with flex lip)) | extrude; bao 450 × 2600 × 250 (X × Y × Z) | c053/c055/c056/c057 (khuôn móc áo, môi mềm, thanh chắn); DECISIONS 10 (môi rộng 2 400); chiều cao/chiều sâu giả định theo web-19/20 | design.md:1510 |
| 2 | `die_body_bolts`<br>Bulông thân khuôn M30 (Die body bolts (M30 socket-head cap screws)) | cyl; bao 155 × 2575 × 500 (X × Y × Z); số lượng 94 | drawing review-01 I4; cỡ và vị trí giả định (tính lực kẹp) | design.md:1600 |
| 3 | `die_heater_conduit`, `die_drip_pan`<br>Ống luồn cáp nhiệt khuôn (cắm rút) (Die heater cable conduit … | pipe; bao 127.4 × 411.3 × 89.2 (X × Y × Z); R 20 / sheet; bao 324 × 2700 × 80 (X × Y × Z) | giả định | design.md:1640, design.md:1680 |
| 4 | `die_cart_rails`<br>Ray xe khuôn (Die cart rails) | frame; bao 600 × 4300 × 60 (X × Y × Z); số lượng 2 | giả định; khổ ray theo review-01 I3 | design.md:1660 |
| 5 | `die_junction_box`<br>Hộp đấu dây khuôn (Die junction box) | box; bao 600 × 300 × 1000 (X × Y × Z) | review-01 I6; giả định | design.md:1670 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `die_thermal_bolts` | Ống gia nhiệt bu-lông nhiệt Ø22 (design Ø30): ở bước 25,4 thì Ø30 chạm nhau | out/log.md:158 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 2 | `die_end_plate_op / _rear` | Tấm đầu theo biên dạng mũi vát thay vì chữ nhật 434 × 500 của tờ 05: chữ nhật ăn vào bao trục giữa và dưới | out/log.md:159 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 3 | `die_lifting_lugs` | Tai cẩu ở X 9 175 / 9 290 (design 9 190 / 9 470): ở X 9 470 mặt trên tấm đầu là mũi vát | out/log.md:160 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 4 | `die_heater_boxes` | Thêm ống cầu mảnh trên/dưới adapter và ống nối đứng hai đầu để 18 vùng tới một gland ở Y −1 250 | out/log.md:161 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 5 | `die_heater_conduit, die_cable_harness` | Kết thúc ở phích trên nóc hộp đấu (Z 1 040–1 045); điểm thiết kế nằm trong hộp | out/log.md:162 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 6 | `die_body_bolts` | Chỉ dựng đầu vít chìm phẳng theo vị trí parts.json (thay yêu cầu ban đầu của orchestrator: hàng 60/180 mm) | out/log.md:163 | Phase 3 — melt line, T-die, die cart, roll stack context |

**Lỗi thiết kế do review phát hiện**

| # | Hạng mục | Phát hiện | Xử lý | Ghi ở đâu |
|---|---|---|---|---|
| 1 | Kết cấu trong khuôn 450 mm | Thân sâu 450 mm quá chật cho ống phân phối Ø72, thanh chắn, preland và 4 hàng vít thân; hàng vít đi xuyên ống phân phối | Quyết định 18 giữ 450 → quyết định 20 lùi mặt sau tới X ≈ 9 060 → quyết định 21 hủy, giữ như đơn giản hóa đã biết (chỉ thấy trong mặt cắt) | design.md §9 #6; drawings/design_issues.md #9; DECISIONS.md #18, #20, #21 |
| 2 | Xe khuôn | Khổ ray 160 mm dưới khuôn ≈ 3,4 t, trọng tâm cao 1,1 m | Khổ ray 560 mm, đế xe luồn dưới bộ trộn | design/review-01.md I3; design.md §10 I3 |
| 3 | Khe gió 200 mm | Lớn hơn mức thường dùng cho PET (50–150 mm) | Chấp nhận để giữ khuôn nằm ngang (DECISIONS #11.4); anim giữ nguyên | design.md §9 #5; design-anim.md §10.8; review-anim-01 "Verified OK – Die" |

## Cụm trục cán (roll stack, context)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Đường kính trục | Ø800 mm (3 trục) | Dải thường gặp 400–800 mm (c046), lấy đầu trên vì năng suất cao | specs.md §6; design.md §3 | không ghi |
| 2 | Chiều dài mặt trục | 2 600 mm (khe môi 2 400 + 100 mỗi bên) | Ước lượng | specs.md §6 | ước lượng |
| 3 | Vị trí khe trục | Khe trục giữa–dưới ở X 9 776, Z 1 200 | Từ khe gió 200 mm | design.md §3, §4.1 | không ghi |
| 4 | Khung cụm trục | ≈ 3 800 × 2 500 × 2 800 (specs); khung chữ nhật đơn giản thay khung C của PlanetCalender, không dựng rèm quang | Cụm cán chỉ là bối cảnh (ze155_context) | specs.md §6; DECISIONS.md #8, #10; out/report.md §6 | ước lượng |
| 5 | Ray lùi | Cả cụm chạy trên ray theo X, hành trình 1 000–1 500 mm | Để mở khoảng trước khuôn | specs.md §6; design.md §7.7 | ước lượng |
| 6 | Đường tấm | Chữ S: ôm nửa +X trục giữa rồi nửa −X trục trên, ra +X ở Z 2 804 | Sơ đồ trang 24–25; review-01 M7 | design.md §10 M7 | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `ctx_roll_stand`<br>Khung cụm trục cán (Roll stack stand) | frame; bao 1660 × 3500 × 3040 (X × Y × Z) | p24-25 (khung đứng sau trục), web-09 (khung trắng dải xanh KM); kích thước giả định specs §6 | design.md:2056 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `ctx_roll_stand` | Khung bên vát góc, có cửa sổ và khối bánh xe; xi lanh ép ngoài mặt khung (Y ±1 890); dầm sau trên Z 1 900–2 100 để tấm ra ở Z 2 804; khớp quay và 2 ống góp nước ở +Y | out/log.md:164 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 2 | `ctx_melt_curtain` | Màn nhựa là vật riêng cho khe gió 200 mm (co hẹp 2 200 → 2 100, võng 5 mm); tấm bắt đầu ở khe trục | out/log.md:165 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 3 | `cáp động cơ trục cán` | Thêm cáp cấp và thang cáp sàn trong ze155_context (design không nói) | out/log.md:231 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 4 | `ctx_roll_stand_logo` | Logo thu nhỏ 0,82 để nằm trong dải xanh KM | out/log.md:332 | Phase 4b — finishing: render quality, light, materials, casting look, cable density, final renders, report |
| 5 | `ctx_takeoff_rollers` | Băng con lăn bắt đầu ở X 11 900, bước 150 (review đề xuất 11 700, bước 200): từ con lăn dẫn Z 2,7 m tấm chỉ đáp được ở X 11 700 với góc ≥ 81° và gấp khúc | out/log.md:370 | Phase 4c — fixes from model review 01 |

## Điều khiển và điện (control)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Vòng điều khiển bơm | Design s_20: P3 → tốc độ bơm, cân đặt lưu lượng. Anim/web (Q6a, người dùng chọn): tốc độ bơm là giá trị đặt chủ; PIC-P3 chỉnh cân LIW + tốc độ vít theo tỷ lệ | Drawing review I3 → design s_20; review-anim-01 C1 dẫn PlasticsToday/Leistritz: dây chuyền tấm thường để bơm đặt lưu lượng | design.md §1, §10.2 I3; design-anim.md §2, §10.1; DECISIONS.md #28 | không ghi |
| 2 | HMI | Bảng cảm ứng trên chân đế xoay phía +Y (X ≈ −1 300, Y ≈ 1 500) | Theo web-04/05 (Lanxess); catalogue p22–23 | specs.md §7; design.md §4.2 | không ghi |
| 3 | Biến tần trung thế | Dãy tủ phía −Y, mặt cửa ở Y −3 700 (thực tế thường đặt phòng điện riêng) | Để thể hiện đủ bộ phận | design.md §7.12 | không ghi |
| 4 | Dừng khẩn và liên động | 9 vị trí dừng khẩn ES1–ES9 ở tầm 1,05–1,19 m; bảng nguyên nhân → tác động (STO, dừng bơm, dừng cân) | Thực hành an toàn; review-01 M3, drawing review I2 | design.md §7.5, §10 M3, §10.2 I2 | không ghi |
| 5 | Đầu đo chiều dày | Đầu đo quét ngang sau cụm trục, không dựng trong mô hình tĩnh; anim/web thêm thiết bị "(giả định)" | Cần cho điều khiển profin bu-lông nhiệt | design.md §7.9; anim/interior_parts.json `anim_ctx_scanner`; web/model-contract.json | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `ctrl_drive_cabinet`<br>Tủ biến tần trung thế (MV drive converter cabinet) | box; bao 3600 × 1200 × 2400 (X × Y × Z) | giả định (biến tần trung thế 3 kV ≈ 3,6 m; thường đặt phòng điện, ở đây đặt sau máy để thể hiện); mặt cửa ở Y −3 700 theo review-01 I2 | design.md:1692 |
| 2 | `ctrl_heater_cabinet`<br>Tủ điều khiển + nhiệt (Control and heater cabinets (PLC, heater zones, MCC)) | box; bao 2400 × 600 × 2200 (X × Y × Z) | c034 (tủ điện), giả định; mặt cửa ở Y −3 700 theo review-01 I2 | design.md:1702 |
| 3 | `ctrl_signal_tower`, `ctrl_cable_drop`, `ctrl_floor_trench`, `ctrl_cable_mv`<br>Đèn tháp báo trạng thái (Signal … | revolve; bao 80 × 80 × 650 (X × Y × Z); trục Z; R 40 / sheet; bao 300 × 100 × 750 (X × Y × Z) / sheet; bao 9700 × 200 × 10 (X × Y × Z) / pipe; bao 80 × 215 × 1180 (X × Y × Z); R 40 | giả định | design.md:1732…1862 |
| 4 | `ctrl_estops`<br>Hộp nút dừng khẩn dọc máy (Emergency-stop stations along the machine) | box; bao 5200 × 520 × 540 (X × Y × Z); số lượng 3 | giả định; cao độ theo review-01 M3 | design.md:1752 |
| 5 | `ctrl_estop_die`, `ctrl_estop_melt`<br>Hộp dừng khẩn tại khuôn (+Y) (Emergency stop at die, operator … | composite; bao 100 × 290 × 870 (X × Y × Z) / composite; bao 100 × 90 × 870 (X × Y × Z) | drawing review-01 I2; giả định | design.md:1772, design.md:1782 |
| 6 | `ctrl_infeed_mv`<br>Hào cáp trung thế cấp vào (Incoming MV feed trench) | sheet; bao 400 × 200 × 10 (X × Y × Z) | drawing review-01 I2; giả định (≈ 1,8 MVA) | design.md:1792 |
| 7 | `ctrl_infeed_lv`<br>Hào cáp hạ thế cấp vào (Incoming LV feed trench) | sheet; bao 400 × 200 × 10 (X × Y × Z) | drawing review-01 I2; giả định (≈ 500 kVA: nhiệt ≈ 260 kW + động cơ phụ) | design.md:1802 |
| 8 | `ctrl_floor_duct`<br>Hào cáp tới tủ điều khiển (Covered floor trench to control cabinets) | sheet; bao 400 × 2650 × 10 (X × Y × Z) | giả định; hào phẳng sàn theo review-01 I2 | design.md:1812 |
| 9 | `ctrl_trench_die_branch`<br>Nhánh hào cáp tới hộp khuôn (Cable trench branch to die junction box) | sheet; bao 200 × 400 × 10 (X × Y × Z) | review-01 I3/I6; giả định | design.md:1842 |
| 10 | `ctrl_trench_mv`<br>Hào cáp trung thế (MV cable trench) | sheet; bao 400 × 2650 × 10 (X × Y × Z) | review-01 I2; giả định | design.md:1852 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `ctrl_machine_cabinet` | Nút dừng khẩn đặt ở X −5 220 gần đầu khung để không che logo dọc | out/log.md:43 | Phase 1 — scene basics, blockout, base frame, drive train |
| 2 | `ctrl_floor_trench, ctrl_floor_duct` | Hào bắt đầu ở X −800 thay vì −1 000 để nắp không chồng; ống sàn kết thúc ở Y −1 100 | out/log.md:221 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 3 | `ctrl_trench_die_branch` | Kéo tới Y −2 150; thêm nắp nhánh tới hộp nhiệt đường chảy, HPU, hộp chân không, cột sau, động cơ trục cán: thiết bị đứng cách hào 0,3–1 m | out/log.md:222 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 4 | `ctrl_cable_mv` | Cáp trung thế lên trong ống Ø80 tới Z 880, 3 cáp vào 3 gland dưới hộp đấu (Z 1 030) thay vì một lối vào mặt −Y | out/log.md:223 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 5 | `s_14 / s_15 / s_16 / p_09` | Đi trong 2 máng cáp mặt bên khung truyền động (Z 560–620) tới tủ đầu máy; công tắc ở vị trí đã dựng, không ở điểm parts.json | out/log.md:224 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 6 | `s_02 (cáp encoder)` | Kết thúc ở tủ đầu máy; tín hiệu tiếp tới tủ biến tần coi như đi trong kênh khung (ẩn) | out/log.md:225 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 7 | `p_07` | Ra mặt tủ khung ở X 1 030 thành cáp kéo sàn tới xe side feeder di động | out/log.md:226 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 8 | `p_08` | Đi trong máng mạ kẽm lên cột sau, dưới sàn ở Z 2 600, tránh ống rơi và ống phụ gia, thay đường chéo của design | out/log.md:227 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 9 | `s_09 / s_18 / s_19` | Tuyến cáp dừng khẩn đi theo cột trước, xe khuôn và giá bộ lọc tới phích/gland thật | out/log.md:228 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 10 | `ctrl_drive_cabinet` | Chụp quạt mái tới Z 2 625 (bbox Z 2 400), kiểu quạt mái biến tần trung thế; bản vẽ mái phẳng | out/log.md:229 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 11 | `ctrl_cable_estops` | Chân cáp dừng khẩn, nắp sàn và gland dời từ X −800 sang −640 vì chân ống nước đứng mới dời sẽ đứng trên nắp cáp | out/log.md:376 | Phase 4c — fixes from model review 01 |

**Lỗi thiết kế do review phát hiện**

| # | Hạng mục | Phát hiện | Xử lý | Ghi ở đâu |
|---|---|---|---|---|
| 1 | Vòng điều khiển áp P3 | Drawing review I3: vòng P3 → tốc độ vít không hợp với máy cấp đói → design đổi sang P3 → tốc độ bơm (s_20). Review anim C1: với dây chuyền tấm, cách thường dùng là bơm đặt lưu lượng, P3 chỉnh cân + vít | Người dùng chọn Q6a cho anim/web; design giữ s_20 | drawings/review-01.md I3; design.md §10.2 I3; anim/review-anim-01.md C1; DECISIONS.md #28 |

## Tiện ích (utilities)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Ống góp nước làm mát | Inox dọc mép +Y, mỗi vùng 1 van điện từ + 1 van bi tay đỏ, ống mềm inox lên xi lanh | Ảnh web-02, web-06; phía +Y là giả định | specs.md §7; design.md §4.2 | không ghi |
| 2 | Khí nén | Hai ống xuống: một ở khuôn (làm mát bu-lông nhiệt, c054), một ở cột sàn (van chân không, máy hút liệu, van cân) | Thực hành thông thường | design.md §7.13, §10 M10 | không ghi |
| 3 | Nước cho phụ trợ | Áo miệng nạp, áo side feeder, bình tách, skid chân không lấy nước nhà máy; HPU làm mát bằng gió | review-01 I7 | design.md §10 I7 | không ghi |

**Chi tiết trong `design.md` §5 có nguồn ghi "giả định"**

| # | Chi tiết (id) | Kích thước theo design (hộp bao, mm) | Nguồn / lý do (nguyên văn design.md) | Ghi ở đâu |
|---|---|---|---|---|
| 1 | `util_cw_supply_riser`, `util_cw_return_riser`, `util_frl`<br>Ống nước cấp từ nhà máy (Plant cooling-water supply … | pipe; bao 130 × 240 × 740 (X × Y × Z); R 30 / pipe; bao 230 × 240 × 830 (X × Y × Z); R 30 / composite; bao 120 × 110 × 250 (X × Y × Z) | giả định | design.md:1874, design.md:1884, design.md:1954 |
| 2 | `util_cw_motor_hoses`<br>Ống nước bộ làm mát động cơ (Cooling water to motor top cooler) | pipe; bao 3324 × 579 × 2298 (X × Y × Z); số lượng 2; R 24 | review-01 M9; giả định (≈ 45 kW nhiệt, 2 × DN40) | design.md:1904 |
| 3 | `util_cw_throat_hoses`, `util_cw_sidefeed_hoses`<br>Ống nước áo hộp miệng nạp (Cooling water to feed throat … | pipe; bao 70 × 785 × 615 (X × Y × Z); số lượng 2; R 15 / pipe; bao 252.4 × 98.2 × 93 (X × Y × Z); số lượng 2; R 12 | review-01 I7; giả định | design.md:1914, design.md:1924 |
| 4 | `util_cw_vac_hoses`<br>Ống nước cụm chân không (Cooling water to vacuum separator and pump skid) | pipe; bao 95.5 × 732 × 1116 (X × Y × Z); số lượng 4; R 16 | review-01 I7; giả định (lấy nước nhà máy tại chỗ qua hai đầu nối sàn, không băng qua máy) | design.md:1934 |
| 5 | `util_air_drop`<br>Ống khí nén xuống khuôn (Compressed-air drop at die) | pipe; bao 30 × 30 × 3600 (X × Y × Z); R 15 | c054 (bulông nhiệt có làm mát gió); giả định | design.md:1944 |
| 6 | `util_air_drop_2`, `util_frl_2`, `util_air_tube_vac`, `util_air_tube_loader`<br>Ống khí nén xuống cột sàn (Compressed-air drop at mezzanine … | pipe; bao 30 × 30 × 2900 (X × Y × Z); R 15 / composite; bao 100 × 120 × 250 (X × Y × Z) / pipe; bao 4276 × 2356 × 962 (X × Y × Z); R 6 / pipe; bao 12 × 2226 × 3406 (X × Y × Z); R 6 | review-01 M10; giả định | design.md:1974…2004 |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `util_air_drop_2, util_air_tube_loader, util_air_tube_vac` | Ống khí dời ra Y −2 725 (ngoài dầm biên sàn), ống tới máy hút liệu đứng ở Y −2 490, ống tới van chân không ở Z 2 350 kẹp dưới dầm sàn và dọc ống chân không | out/log.md:94 | Phase 2 — barrel, screws, feeding, side feeder, vacuum |
| 2 | `util_air_drop` | Đầu trên đóng bằng van bi ở Z 4 440 (thay cho điểm lấy khí nhà máy); một kẹp vào hộp đấu khuôn | out/log.md:166 | Phase 3 — melt line, T-die, die cart, roll stack context |
| 3 | `util_cw_lube_hoses` | Ống nước bộ làm mát dầu kết thúc ở cổng F2/F4 qua núm van 90/160 mm, không ở điểm parts.json; bắt đầu ở đầu tê X −478 / −578 | out/log.md:219 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 4 | `drive_motor_cooler, util_cw_motor_hoses` | Thêm 2 bích DN40 ở mặt +Y bộ làm mát động cơ; 4 giá ống sàn đỡ cả hai cặp ống (design không có đỡ) | out/log.md:220 | Phase 4a — stray materials, Ø640 flanges, cabinets/HMI/trenches/cables/hoses, connection audit |
| 5 | `util_air_drop (kẹp)` | Kẹp ở X 9 760 / 9 900, đoạn 600 mm (review: 9 560 / 9 760, 450 mm) vì đỉnh giá cán vát, kẹp ở 9 560 sẽ lơ lửng | out/log.md:372 | Phase 4c — fixes from model review 01 |

## Giá trị quy trình (process values)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Năng suất thiết kế | 3 500 kg/h PET (dải 2 500–5 000) | ZE 180 A cũ chạy 1 750–7 000 kg/h (c019); quy theo mômen 35 000/48 500 = 0,72 → 1 260–5 050; KM làm tới 6 t/h (c041) | specs.md §0; design.md §1, §3 | ước lượng |
| 2 | Khổ và chiều dày tấm | Tấm thành phẩm 2 100 mm, dày 0,3–1,5 mm; điểm mẫu 0,8 mm* | Giới hạn cụm cán 1 800 kg/h·m (c046): 3 500/2,1 = 1 670 kg/h·m | specs.md §0; design-anim.md §2 | ước lượng |
| 3 | Tốc độ vít vận hành | 300 v/ph* (tối đa 400 có nguồn, c003) | Điểm vận hành mẫu | design-anim.md §2; shots.json S01/S04 | giả định (*) |
| 4 | Năng lượng riêng | 0,20–0,25 kWh/kg* → ≈ 800 kW* ở 3 500 kg/h | PET không sấy, gồm năng lượng khử khí | design.md §3.1; design-anim.md §2 | giả định (*) |
| 5 | Mômen vận hành | ≈ 12,7 kNm* mỗi trục (36 % của 35 kNm) ở 300 v/ph | Tính từ 800 kW | design-anim.md §2; shots.json S02 | giả định (*) |
| 6 | Nhiệt độ đặt | Toàn bộ 270–290 °C; B1 áo nước ≈ 50 °C*, B2 260*, B3 275*, B4 270*, nhựa đầu xi lanh ≈ 285*, ống 275*, khuôn 270–280 °C* | Không có nguồn công bố | design.md §1; design-anim.md §2 | giả định (*) |
| 7 | Độ điền vùng rắn | ≈ 30 %* | Minh họa cấp đói | design-anim.md §2 | giả định (*) |
| 8 | Áp suất vận hành | P1 ≈ 100 bar*, P2 ≈ 95*, Δp lưới ≈ 45*, P3 = 50*, P4 ≈ 250*, P5 ≈ 200 bar* | Δp là giả định (c052 chỉ là cơ sở tính năng suất 40 bar ở 1 000 Pa·s) | design.md §1; design-anim.md §2 | giả định (*) |
| 9 | Chất lượng sau khử khí | Ẩm < 50 ppm*; IV 0,80 → ≥ 0,77 dl/g* | Minh họa | design-anim.md §2 | giả định (*) |
| 10 | Độ mịn lưới lọc | 60 µm* | c052 chỉ ghi 60 µm là điều kiện tính năng suất | design.md §1; design-anim.md §2 | giả định (*) |
| 11 | Khe môi vận hành | 1,0 mm* (chỉnh 0,5–2); bu-lông nhiệt ±0,15 mm (300 µm tổng, c054) | Phù hợp tấm 0,8 mm và kéo giãn 1,19 | design-anim.md §2, §7 | giả định (*) |
| 12 | Cân bằng khối lượng | ρ nóng chảy 1,17 kg/L*, ρ rắn 1,335; tấm trên trục 2,2 m (co hẹp*); môi 20,8 m/min, tấm 24,8 m/min, kéo giãn 1,19; trục 9,9 v/ph; tấm sau xén ≈ 3 340 kg/h (xén ≈ 4,5 %) | Tính từ các giá trị giả định | design-anim.md §2 | giả định (*) |
| 13 | Nhiệt độ trục cán | Dưới ≈ 60, giữa ≈ 55, trên ≈ 45 °C*; ≈ 10 v/ph | Sáng chế tấm PET vô định hình (27–80 °C), không có URL cục bộ | design-anim.md §2 | giả định (*) |
| 14 | Khe đỉnh vít | ≈ 0,7 mm* (mô hình: vít Ø167,5 / lõi 116,5) | Biên dạng Erdmenger thu 0,995 | shots.json S05; review-anim-01 "Verified OK" | giả định (*) |

## Animation và nội thất (animation / interior)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Độ dài phim | 16 shot, 3:31, 1920 × 1080, 25 khung/s, 7 ảnh tĩnh (sau đó hủy render MP4, chỉ giữ hình học và kịch bản) | Q1 được duyệt (DECISIONS #28); DECISIONS #29 đổi đích sang web | design-anim.md tóm tắt, §11; DECISIONS.md #28, #29 | không ghi |
| 2 | Tốc độ hiển thị | Vít chậm 20× (thực 300 v/ph → hiện 15 v/ph), bơm chậm 4×, trục cán tốc độ thực, đĩa lọc tua nhanh, dòng nhựa "minh họa" | Tránh nhòe và hiệu ứng bánh xe quay ngược | design-anim.md §3, Q4 | không ghi |
| 3 | Dòng nhựa trong rãnh | Khối mờ có vân trôi, không quay theo vít; hạt đi 63 mm/s (1,5D) / 42 mm/s (1D) | Đơn giản hóa | design-anim.md §6, §7 | không ghi |
| 4 | Hộp số | Sơ đồ nguyên lý: z23 → z45 (log; interior_parts ghi 43) + z21 → z40, tỷ số 3,727 | "sơ đồ nguyên lý (giả định)" | anim/interior_parts.json `int_gbx_schematic`; anim/log.md:138 | không ghi |
| 5 | Bánh răng bơm | 16 răng, mô-đun 7,8, rộng 125 mm (đỉnh Ø140,34 khi dựng) | Maag không công bố số răng; chọn để 2π·m²·z·b = 764 cm³/v (c047) | anim/interior_parts.json; anim/log.md:128; review-anim-01 "Verified OK" | không ghi |
| 6 | Đĩa lọc | Ø930 × 80, 12 lỗ Ø157 trên R 345 (bước 30°), 5 lỗ trong dòng (5 × Ø157 ≈ 970 cm²); răng cóc phía −Y | Khớp diện tích lưới c050; cơ cấu cóc là giả định | anim/interior_parts.json `int_sc_disc` | không ghi |
| 7 | Chốt van khởi động | Chốt trượt Ø198, hành trình 200 mm (XẢ Y −0,2, CHẠY 0); dựng dài 420 thay vì 600 | Design ghi chốt xoay; khối ngoài 460 mm không chứa chốt 600 | anim/interior_parts.json `int_valve_bolt`; anim/log.md:125 | không ghi |
| 8 | Biên dạng vít | Erdmenger 2 đầu ren: a 142, Ro 83,75, Rr 58,25, góc đỉnh 25,94°; vít B lệch 90° | Hình học chuẩn của vít tự làm sạch | anim/interior_parts.json `screw_profile` | không ghi |
| 9 | Ranh giới phần tử vít | Xếp lại theo bước 0,25D, lệch ≤ 70 mm so với parts.json | Để tổng 34D chẵn phần tử | anim/interior_parts.json `screw_elements`; design-anim.md §10.7 | không ghi |
| 10 | Khe môi phóng đại | Khe và hành trình cùng vẽ ×10 (shape key `gap_x10`, `lip_push`); ảnh ST4 dùng khe thật | Khe thật 1 mm không thấy được | design-anim.md §7; review-anim-01 I6 | không ghi |
| 11 | Bọt khử khí | Vùng 1 dày, nhanh (0,25 m/s); vùng 2 nhỏ, thưa (0,15 m/s) | Vùng 1 rút phần lớn hơi nước | design-anim.md §7; review-anim-01 M2 | không ghi |

**Lệch thiết kế khi dựng (`DESIGN-DEVIATION`)**

| # | Bộ phận | Giá trị / cách làm thay cho thiết kế, và lý do | Ghi ở đâu | Phase |
|---|---|---|---|---|
| 1 | `nhóm ax_* (side feeder, cáp, FRL)` | Chuyển sidefeed_feeder, phễu, ống rơi, cáp cấp liệu, util_frl_2 từ ax_static sang ax_feed_platform: chúng đứng trên sàn, nếu không sẽ lơ lửng khi ẩn sàn | anim/log.md:28 | Phase C0 – scene, groups, rig |
| 2 | `anim_cam_S13` | Đổi key 1 và 2 của camera S13 vì tia nhìn theo đường thiết kế bị khung cụm trục và tấm đầu khuôn che | anim/log.md:32 | Phase C0 – scene, groups, rig |
| 3 | `int_screw_elem (biên dạng)` | Biên dạng 40 điểm, xoắn 10° mỗi vòng thay vì 64 điểm × 40 bước, để 64 phần tử nằm trong ngân sách 190 nghìn tam giác | anim/log.md:74 | Phase A1a – barrel interior |
| 4 | `đĩa khối nhào KB` | Khe 1 mm giữa các đĩa (đĩa hẹp hơn 1 mm): nếu không đĩa của hai trục trùng mặt phẳng và xuyên nhau | anim/log.md:75 | Phase A1a – barrel interior |
| 5 | `phần tử cắt sẵn 12 / 22` | Dừng 2 mm trước mặt cắt, int_xsec 2 mm lấp đúng tới mặt, tránh z-fighting | anim/log.md:76 | Phase A1a – barrel interior |
| 6 | `mũi vít TIP` | Mũi 30° nằm gọn trong phần tử 32 (mũi phẳng Ø70 ở X 5 746), không nhô vào đầu xi lanh | anim/log.md:77 | Phase A1a – barrel interior |
| 7 | `miệng nạp B1 (nội thất)` | Lỗ rộng 280 (Y ±140) thay vì 300: bệ B1 chỉ rộng 300, lỗ 300 để lại thành dày 0 | anim/log.md:78 | Phase A1a – barrel interior |
| 8 | `cửa sổ lỗ chân không` | Dải cửa sổ Y ±260 thay vì ±140: dải ±140 nằm trên lỗ và bị gân ren che | anim/log.md:79 | Phase A1a – barrel interior |
| 9 | `viền vỏ ghost` | Viền làm trong shader (Layer Weight → alpha 0,10…0,75) thay vì hình học | anim/log.md:80 | Phase A1a – barrel interior |
| 10 | `khối điền / vòm rỗng` | Không có khối điền cột cấp liệu (cấp đói); bản sao vòm 1 đoạn vát; cửa phun B6 là lỗ tịt | anim/log.md:81 | Phase A1a – barrel interior |
| 11 | `int_valve_body / int_valve_bolt` | Chốt dài 420 thay vì 600: hành trình 200 + khoảng kênh 200 không vừa khối ngoài 460 mm | anim/log.md:125 | Phase A1b – melt line, die, remaining interior |
| 12 | `int_melt_adapters_hollow` | Tách thành _sc_in / _pump_in / _pump_out / _die (+ _lo, _y0) để mỗi trạng thái chỉ hiện adapter bị cắt | anim/log.md:126 | Phase A1b – melt line, die, remaining interior |
| 13 | `các thân rỗng (hollow)` | Bản sao đúng ngoại thất (1 đoạn vát, bu-lông giảm còn 30 %), vượt ngân sách để chuyển FULL → cắt liền mạch | anim/log.md:127 | Phase A1b – melt line, die, remaining interior |
| 14 | `int_pump_gear` | Nửa cắt −Y cho CUT_PUMP, bánh nguyên là con _full; đỉnh Ø140,34 (spec 140,6) để thể tích lý thuyết 764,5 cm³; rộng 124,6 (khe bên 0,2 mm) | anim/log.md:128 | Phase A1b – melt line, die, remaining interior |
| 15 | `thân bơm, rãnh lọc, đĩa` | Thân bơm 4 lỗ thanh nhiệt Ø16 (web-14); rãnh thận lọc cấp thẳng từ lỗ Ø120; đĩa có 72 răng cóc + trục Ø150 | anim/log.md:129 | Phase A1b – melt line, die, remaining interior |
| 16 | `anim_ghost_sc` | Mũ ghost của bộ lọc nâng phẳng tới Z 2 079 vì mũ nghiêng ngoài thấp hơn đỉnh đĩa Ø930 67–190 mm (chỉ cho ghost) | anim/log.md:130 | Phase A1b – melt line, die, remaining interior |
| 17 | `vít thân khuôn (nội thất)` | Không có thân vít/lỗ ren trong mặt phân khuôn và mặt cắt A-A (đơn giản hóa DECISIONS 20/21: hàng vít đi qua ống phân phối) | anim/log.md:131 | Phase A1b – melt line, die, remaining interior |
| 18 | `shape key gap_x10` | Nâng cả môi mềm cứng 9 mm (gân bản lề bị trượt); chỉ nâng mặt land sẽ đảo mũi môi 7,6 mm | anim/log.md:132 | Phase A1b – melt line, die, remaining interior |
| 19 | `rãnh bu-lông nhiệt` | Phay rãnh r 16 dọc 94 trục bu-lông trên mặt vát và qua môi (theo tờ 05); bu-lông 0–39 giảm lưới | anim/log.md:133 | Phase A1b – melt line, die, remaining interior |
| 20 | `vùng thanh chặn X 9 240–9 270` | Không có hốc dưới (khe dưới thanh 3 mm, preland 4, khe chảy 3, land 1,0); khối điền nửa dưới không thấy nhựa ở dải 30 mm này | anim/log.md:134 | Phase A1b – melt line, die, remaining interior |
| 21 | `ống + bộ trộn (mặt cắt)` | Dựng thành hai nửa xoay nhiều lớp (_lo, _y0), mỗi lớp một màu nắp, vì một vật cắt không tô được nhiều lớp | anim/log.md:135 | Phase A1b – melt line, die, remaining interior |
| 22 | `anim_ctx_scanner` | Dầm dưới và đầu đo chạy dưới mặt con lăn; khe dầm 400 thay vì 300; cặp đầu đo là một vật | anim/log.md:136 | Phase A1b – melt line, die, remaining interior |
| 23 | `vạch trên trục cán` | Vạch ở \|Y\| 1 330–1 360 trên mặt trục (cổ trục nằm trong tấm khung); thêm sọc _aa cho mặt cắt S12 | anim/log.md:137 | Phase A1b – melt line, die, remaining interior |
| 24 | `sơ đồ hộp số` | Bánh trung gian z45 (không phải 43) để 45/23 × 40/21 = 3,727 ≈ 3,73; răng hình thang vuốt mỏng để không cặp nào xuyên nhau | anim/log.md:138 | Phase A1b – melt line, die, remaining interior |
| 25 | `đầu xi lanh rỗng` | Không có hốc côn mũi vít (mũi côn kết thúc phẳng trong phần tử 32 tại X 5 746) | anim/log.md:139 | Phase A1b – melt line, die, remaining interior |

## Kế hoạch web (web, R3F)

**Giả định chính**

| # | Hạng mục | Giá trị giả định | Lý do / cơ sở | Ghi ở đâu | Độ tin cậy |
|---|---|---|---|---|---|
| 1 | Đích cuối | Web React Three Fiber, không MP4; xuất GLB bằng Blender nền trên file .blend đã lưu (phương án C) | Người dùng chọn | DECISIONS.md #29, #30; web/ADDENDUM-discussion.md | không ghi |
| 2 | Bộ công cụ | React 19.3, R3F 9.8.1, drei 10.7.9, three 0.186.1, three-mesh-bvh 0.8.3, Vite 8, TypeScript, meshopt, không CDN | Q5 được duyệt | DECISIONS.md #30; web/PLAN-R3F.md §9 | không ghi |
| 3 | Đơn vị chọn | 190 thiết bị = 186 id parts.json + 4 nhóm tổng hợp (cáp, băng tải, đầu đo) | Q3 | web/PLAN-R3F.md; review-plan-02 M2 | không ghi |
| 4 | Tốc độ rotor | Vít −300 v/ph (chậm 20×); trục động cơ và 2 khớp −1 119 v/ph (= 300 × 3,73, chiều quay "assumed equal to the screws (illustration)"); bơm ±69 (chậm 4×); trục cán ±9,95 (thực); hộp số vào −1 118, trung gian 571,4 | Lấy từ điểm vận hành giả định của anim | web/model-contract.json `rotors`; web/dot1/rotors.dot1.json | không ghi |
| 5 | Ngân sách hiệu năng | Contract: line ≤ 15 MB, interior ≤ 6 MB, draw call 1 000/1 150/1 350, khung đầu ≤ 6 s, FPS 55/45/40 trên Apple M3 Pro. Đợt 1 siết theo số đo: 7/2,5 MB; 850/1 000/1 100; ≤ 4 s; BVH ≤ 800 ms | Máy tham chiếu là máy này; số đo probe | web/model-contract.json `budgets`; web/PLAN-DOT1.md §10 | không ghi |
| 6 | Mặt cắt | Kiểu lai: trạng thái cố định dùng bản cắt sẵn của A1a/A1b; mặt cắt tự do bằng clipping plane có nắp | Q2 | web/PLAN-R3F.md §3.5, §9 | không ghi |
| 7 | Phạm vi Đợt 1 | Xuất toàn bộ phần bên trong (slice 1 + 2); hoãn peel, tinh chỉnh precompile, pickSweep, trace sang Đợt 1b | review-dot1-01 M2 | web/PLAN-DOT1.md §3.1.4; web/dot1/AMENDMENTS.md | không ghi |
| 8 | Tiêu chí D2 | `selectAll()` chọn được 190/190 thiết bị, chọn được từ cây; không bắt buộc bấm trúng trên màn hình | Nhiều thiết bị bị che (xi lanh dưới vỏ che); dò tia thô chỉ 112–152/189 | web/dot1/AMENDMENTS.md I1; web/review-dot1-01.md I1 | không ghi |
| 9 | Quyết định nhỏ Đợt 1 | BVH `CENTER`; nắp `force` cho trục cán; FREE hiện cả phần bên trong slice 2; vào trạng thái thì camera về preset | Đề xuất của người lập kế hoạch, được duyệt | web/PLAN-DOT1.md §9; web/dot1/AMENDMENTS.md | không ghi |
| 10 | Dữ liệu xuất | GLB chỉ phản ánh bản `.blend` đã lưu; thay đổi chưa lưu trong phiên Blender bị bỏ qua | Xuất bằng tiến trình nền đọc file trên đĩa | web/dot1/AMENDMENTS.md (M); web/review-dot1-01.md M4 | không ghi |
| 11 | Ước lượng thời gian | Đợt 1 xem được sau ≈ 2,5–3 h; cả ba đợt ≈ 6–7 h (tốt nhất 5 h) | Ước lượng của kế hoạch | web/PLAN-R3F.md tóm tắt; review-plan-02 AD4 | ước lượng |

## Phụ lục A. Các dòng ghi "ước lượng" trong `research/specs.md` (trích tự động)

| Dòng | Mục specs | Nội dung (các ô của dòng bảng, nguyên văn) |
|---|---|---|
| specs.md:11 | 0. Quyết định thiết kế (vì không có nguồn nào mô tả đúng một dây chuyền ZE 155 + T-die) | Năng suất thiết kế ‖ **3 500 kg/h** (dải 2 500–5 000 kg/h) — ước lượng ‖ ZE 180 A cũ chạy 1 750–7 000 kg/h (c019). Lấy theo tỷ lệ mômen 35 000/48 500 = 0,72 thì ZE 155 vào khoảng 1 260–5 050 kg/h. KM đã làm dây chuyền tấm trục đôi tới 6 t/h (c041). |
| specs.md:12 | 0. Quyết định thiết kế (vì không có nguồn nào mô tả đúng một dây chuyền ZE 155 + T-die) | Khổ tấm ‖ Tấm thành phẩm rộng 2 100 mm, dày 0,3–1,5 mm; **khe môi khuôn (lip/slot) rộng 2 400 mm** — ước lượng ‖ Cụm trục cán xử lý được tối đa khoảng 1 800 kg/h PET trên mỗi mét khổ (c046). 3 500 kg/h ÷ 2,1 m = 1 670 kg/h·m, dưới giới hạn đó. Khe môi lấy rộng hơn tấm khoảng 150 mm mỗi bên để bù co hẹp (neck-in) và phần xén biên (edge trim). |
| specs.md:23 | 1. Máy đùn ZE 155 UT — số liệu chính | Đường kính ngoài thực của vít ‖ ≈ 167,5 mm (ước lượng) ‖ Bảng ghi đường kính bằng lỗ xi lanh (ZE 180: 194 mm lỗ, vít 192,3 mm, c017). Lấy cùng tỷ lệ 0,991. |
| specs.md:24 | 1. Máy đùn ZE 155 UT — số liệu chính | **Khoảng cách tâm hai trục vít (centre distance a)** ‖ **≈ 142 mm** (ước lượng, độ tin cậy cao) ‖ a = (D + d)/2 = (169 + 114,6)/2 = 141,8. Cách tính này khớp ZE 180 (162,8 so với 163, c017) và ZE 110 (99,7 so với 100, c020). Bản R cho ra 142,1, đúng như việc A và R cùng khoảng cách tâm (c030). |
| specs.md:32 | 1. Máy đùn ZE 155 UT — số liệu chính | **Chiều dài toàn máy tại L/D 34** ‖ **≈ 10 000 mm** (ước lượng) ‖ 11 700 − 10 × 169 = 10 010. Kiểm tra bằng ZE 110: bảng ghi 9 000 mm tại 44D, trừ 16D ra 7 096 mm, máy thật 28D đo được 6 850 mm (c021), lệch 3,5 %. |
| specs.md:34 | 1. Máy đùn ZE 155 UT — số liệu chính | Khối lượng tại 34D ‖ ≈ 31 000 kg (ước lượng) ‖ Bớt 10D xi lanh và vít, ≈ 1 330 kg/m × 1,69 m + vỏ/ống ≈ 2,5 t. |
| specs.md:35 | 1. Máy đùn ZE 155 UT — số liệu chính | Chiều rộng máy (khung đế, chưa tính HMI) ‖ ≈ 2 000 mm (ước lượng) ‖ ZE 110 28D rộng 1 400 mm (c021), nhân tỷ lệ 169/119 = 1,42. |
| specs.md:36 | 1. Máy đùn ZE 155 UT — số liệu chính | Chiều cao tới đỉnh xi lanh (chưa tính phễu, ống hút chân không) ‖ ≈ 2 000 mm (ước lượng) ‖ ZE 110 cao 1 650 với trục ở 1 100, tức 550 mm trên trục; × 1,42 ≈ 780 mm; 1 200 + 780. |
| specs.md:39 | 1. Máy đùn ZE 155 UT — số liệu chính | Cấu hình đề xuất (ước lượng) ‖ B1 4D cấp liệu (mở phía trên) · B2 6D kín (nóng chảy) · B3 6D mở: thoát khí khí quyển hoặc chân không nhẹ · B4 6D kín (trộn) · B5 6D **thoát khí chân không**, miệng dài 6D · B6 6D kín (tăng áp). Tổng 4 + 5×6 = 34D ‖ ZE có miệng thoát khí dài 6D (c036). Tấm PET cần hút ẩm và hút sâu; có một máy ZE-R dùng 3 cửa thoát khí khí quyển + 1 cửa chân không (c070; chỉ là bối cảnh, không phải bằng chứng cho cấu hình này). |
| specs.md:41 | 1. Máy đùn ZE 155 UT — số liệu chính | Gia nhiệt xi lanh ‖ ≈ 25 kW mỗi đoạn 6D (ước lượng) ‖ ZE 180: 30 kW/đoạn (c018); giảm theo cỡ máy. |
| specs.md:61 | 1.1 Bộ truyền động (drive train) | Kích thước hộp số ‖ ≈ dài 1 600 × rộng 1 400 × cao 1 700 mm, ≈ 8–10 t (ước lượng) ‖ Phải chịu 2 × 35 kNm. Hình khối theo ảnh web-11 (Eisenbeiss) và web-01 (hộp số xanh). Nên chỉnh lại theo ảnh catalogue (người phân tích PDF). |
| specs.md:62 | 1.1 Bộ truyền động (drive train) | Tỷ số truyền ‖ ≈ 3,7 (ước lượng) ‖ Động cơ 4 cực 1 490 v/ph chia 400 v/ph |
| specs.md:63 | 1.1 Bộ truyền động (drive train) | **Động cơ chính đề xuất vẽ** ‖ **Động cơ cảm ứng trung thế 4 cực ≈ 2 000 kW, chạy biến tần (VFD), cỡ khung ABB AMI 450L4**: dài L = 2 025 mm, tâm trục H = 450 mm, cao tổng HC = 1 860 mm, rộng AE = 1 500 mm, ≈ 4,5–4,7 t ‖ Kích thước: c066; khối lượng: c065 (1 750 kW, 4 680 kg). Ước lượng công suất: 3 500 kg/h × 0,22 kWh/kg ≈ 770 kW cho PET, nhân thêm dự phòng cho PP độn và lúc khởi động; 2 000 kW cho phép đủ mômen tới khoảng 270 v/ph. |
| specs.md:65 | 1.1 Bộ truyền động (drive train) | Vị trí động cơ ‖ Trục động cơ đồng trục với trục vào hộp số; đặt trên bệ thép. Nếu trục vào nằm ở độ cao trục vít 1 200 mm thì bệ cao ≈ 750 mm (ước lượng) ‖ Chưa tìm thấy bản vẽ |
| specs.md:66 | 1.1 Bộ truyền động (drive train) | Khớp nối + vỏ che (coupling guard) ‖ Dài ≈ 600–700 mm (ước lượng) ‖ Ảnh web-12 (vỏ che màu cam trên dây chuyền KM) |
| specs.md:73 | 2. Cấp liệu (feeding) | Cân cấp liệu chính (loss-in-weight) ‖ Coperion K-Tron BSP-150-S cho hạt PET: 34–6 700 dm³/h, treo trên 3 cảm biến cân, phễu nối thêm tới 320 dm³ (cao 1 684, Ø 600 mm) ‖ c069. 3 500 kg/h ÷ 0,8 kg/dm³ ≈ 4 400 dm³/h, nằm trong dải. Nếu cấp vảy chai (bulk ≈ 0,3) thì phải dùng cân trục vít đôi lớn hơn (ước lượng). |
| specs.md:74 | 2. Cấp liệu (feeding) | Cân phụ gia / masterbatch ‖ 1–2 cân trục vít đôi cỡ nhỏ (loại K-ML-D5-T35) ‖ Ước lượng |
| specs.md:75 | 2. Cấp liệu (feeding) | Sàn đặt cân (feeder platform) ‖ Sàn thép ngay trên B1, mặt sàn cao ≈ 2 800–3 200 mm, có lan can vàng và cầu thang; ống rơi liệu xuống miệng B1 ‖ Ước lượng theo ảnh web-04/05 (Lanxess: cân đặt trên tầng lửng) |
| specs.md:76 | 2. Cấp liệu (feeding) | Miệng cấp liệu (feed opening) trên B1 ‖ ≈ 300 × 250 mm (ước lượng) ‖ Chưa tìm thấy |
| specs.md:77 | 2. Cấp liệu (feeding) | Máy hút liệu (vacuum loader) ‖ Đặt trên phễu từng cân ‖ Ước lượng |
| specs.md:83 | 3. Thoát khí và chân không (venting / vacuum) | Cửa thoát khí chân không trên B5 ‖ Miệng dài 6D (≈ 1 000 mm) × ≈ 300 mm; nắp vòm (vent dome) có kính quan sát; ống DN 150 đi lên rồi sang bình tách ngưng ‖ Miệng 6D: c036. Kích thước nắp: ước lượng từ lỗ xi lanh rộng 311 mm. |
| specs.md:84 | 3. Thoát khí và chân không (venting / vacuum) | Cửa trên B3 ‖ Thoát khí khí quyển (hoặc chân không nhẹ), có ống xả nhỏ ‖ Ước lượng |
| specs.md:86 | 3. Thoát khí và chân không (venting / vacuum) | Cụm chân không (vacuum unit) ‖ Skid ≈ 2 000 × 1 200 × 1 800 mm gồm bình tách ngưng (condensate separator) inox đứng, bơm Roots, bơm lót khô; đặt phía −Y cạnh B5 (ước lượng) ‖ Hình dáng theo web-15 (Busch PLASTEX: bình lọc đứng + bơm MINK, c060); bộ TK-V có buồng ngưng và bơm vòng nước (c063) |
| specs.md:93 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | Tấm đầu xi lanh + adapter chuyển từ lỗ số 8 sang lỗ tròn ‖ Dài ≈ 250 mm, Ø ngoài ≈ 450 mm (ước lượng) ‖ — |
| specs.md:94 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | Van khởi động / van chuyển hướng (start-up/diverter valve) ‖ Khối ≈ 400 (X) × 500 × 500 mm, xi lanh thuỷ lực đặt ngang, có máng xả nhựa xuống sàn (ước lượng) ‖ Có trong sơ đồ catalogue (c035) |
| specs.md:95 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | **Bộ lọc lưới (screen changer)** ‖ **Gneuss RSFgenius 200**: lưới hoạt động 970 cm², 4 560 kg/h, kích thước A 1 955 (dài tổng) · B 705 · C 1 429 (cao tổng) · D 550 · E 1 040 mm, 3 800 kg, gia nhiệt điện 39 kW chia 6 vùng, 200 bar ‖ c050; công suất tính ở 1 000 Pa·s, 60 µm, Δp 40 bar (c052). Phương án nhỏ hơn: RSFgenius 175, 3 300 kg/h, 2 200 kg (c051). Chiều dày thân theo chiều chảy ≈ 600–800 mm (ước lượng, chưa rõ ý nghĩa từng chữ F/G/I trong bản vẽ hãng). Ảnh web-13. |
| specs.md:96 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | **Bơm bánh răng nhựa nóng (melt gear pump)** ‖ **Maag extrex6 GU 100/125**: 764 cm³/vòng, 4 474 kg/h ở 134 v/ph (ở 3 500 kg/h chạy ≈ 105 v/ph); áp ra ≤ 370 bar, Δp ≤ 250 bar ‖ c047, c049. Thân bơm ≈ 500 × 450 × 450 mm (ước lượng); ảnh web-14. |
| specs.md:97 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | Động cơ bơm ‖ Động cơ hộp số ≈ 45–55 kW, nối trục các-đăng; động cơ đặt đứng trên hộp giảm tốc như ảnh web-07 (ước lượng) ‖ Công suất thuỷ lực Q·Δp ≈ 0,75 L/s × 200 bar ≈ 15 kW, nhân dự phòng |
| specs.md:98 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | Bộ trộn tĩnh (static mixer) ‖ Tuỳ chọn, ống DN ≈ 120, dài ≈ 600 mm (ước lượng) ‖ — |
| specs.md:99 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | Ống/adapter dẫn vào khuôn ‖ Ống có gia nhiệt, lớp cách nhiệt và vỏ inox ‖ Ước lượng |
| specs.md:100 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | Tổng chiều dài từ cuối xi lanh tới cửa vào khuôn ‖ ≈ 2 500–3 000 mm (ước lượng) ‖ — |
| specs.md:101 | 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X | Cao độ đường tâm nhựa ‖ Giữ 1 200 mm suốt (bằng trục vít), môi khuôn ở Z ≈ 1 200 ‖ Ước lượng, để đơn giản |
| specs.md:110 | 5. Khuôn phẳng chữ T (flat T-die, coat-hanger) | Chiều rộng thân kể cả tấm đầu (end plates) ‖ ≈ 2 750 mm; tính cả hộp đầu nối dây nhiệt / thanh deckle ≈ 3 050 mm (ước lượng) ‖ — |
| specs.md:111 | 5. Khuôn phẳng chữ T (flat T-die, coat-hanger) | Chiều cao thân (theo Z, hai nửa khuôn) ‖ ≈ 500 mm (nửa trên 260, nửa dưới 240) (ước lượng) ‖ Theo tỷ lệ trong ảnh web-19/20 |
| specs.md:112 | 5. Khuôn phẳng chữ T (flat T-die, coat-hanger) | Chiều sâu theo chiều chảy (X), từ mặt vào tới môi ‖ ≈ 450 mm, mũi môi vát nhọn 30–45° về phía khe trục cán (ước lượng) ‖ Ảnh web-17/18 |
| specs.md:114 | 5. Khuôn phẳng chữ T (flat T-die, coat-hanger) | Bulông chỉnh thanh chắn ‖ Bước ≈ 50–75 mm, nằm trên mặt nửa khuôn trên (ước lượng) ‖ Ảnh web-19 |
| specs.md:116 | 5. Khuôn phẳng chữ T (flat T-die, coat-hanger) | Gia nhiệt ‖ Thanh nhiệt cắm (cartridge heaters), vùng rộng ≈ 250–300 mm → ≈ 9 vùng mỗi nửa + 2 tấm đầu ≈ 20 vùng; tổng ≈ 50 kW (ước lượng) ‖ Khuôn Cloeren 62" (1 575 mm) dùng 32,8 kW (c055), tức ≈ 21 kW/m |
| specs.md:117 | 5. Khuôn phẳng chữ T (flat T-die, coat-hanger) | Khối lượng ‖ ≈ 2 000 kg (ước lượng) ‖ Cloeren 62" nặng 1 032 kg (c055); quy theo chiều rộng 2 400 mm ra ≈ 1 570 kg, cộng thêm phần thân dày (heavy-duty) và thanh chắn |
| specs.md:118 | 5. Khuôn phẳng chữ T (flat T-die, coat-hanger) | Hướng ra nhựa ‖ Nằm ngang theo +X, vào khe giữa trục 1 và trục 2 ‖ Ước lượng; PlanetCalender cho phép xoay cả khung để chỉnh góc vào của màng nhựa (c044) |
| specs.md:126 | 6. Cụm cán láng / trục làm nguội (polishing / chill roll stack) | Chiều dài mặt trục (face width) ‖ 2 600 mm (ước lượng: khe môi 2 400 + 100 mỗi bên) ‖ — |
| specs.md:127 | 6. Cụm cán láng / trục làm nguội (polishing / chill roll stack) | Khung tổng ‖ ≈ rộng 3 800 (Y) × dài 2 500 (X) × cao 2 800 mm (ước lượng) ‖ — |
| specs.md:128 | 6. Cụm cán láng / trục làm nguội (polishing / chill roll stack) | Vị trí so với khuôn ‖ Khe trục 1–2 ở Z ≈ 1 200 mm; môi khuôn cách khe trục ≈ 50–150 mm ‖ Ước lượng theo ảnh web-18 (môi khuôn sát khe) |
| specs.md:129 | 6. Cụm cán láng / trục làm nguội (polishing / chill roll stack) | Lùi ra ‖ Cả cụm trục chạy trên ray sàn theo X, hành trình ≈ 1 000–1 500 mm, để mở khoảng trống trước khuôn (ước lượng) ‖ — |
| specs.md:136 | 7. Điều khiển, điện, bảo vệ | Tủ điện ‖ Tủ điều khiển và tủ nhiệt nằm trong khung đế hoặc đặt sát máy (catalogue, c034); tủ biến tần trung thế đặt ở phòng điện riêng (ước lượng, không vẽ) ‖ — |
| specs.md:139 | 7. Điều khiển, điện, bảo vệ | Ống góp nước làm mát ‖ Ống inox chạy dọc khung đế (ống cấp + ống hồi), mỗi vùng một van điện từ và một van bi tay đỏ, ống mềm inox dẫn lên xi lanh. Đặt phía +Y như ảnh web-06 (ước lượng) ‖ web-02, web-06, c023 |

## Phụ lục B. Nhãn trên hình có dấu `*` (`anim/shots.json`, trích tự động)

Theo `design-anim.md` §2: "dấu * = giả định (không có nguồn công bố)". Mỗi shot có chân hình "* = giả định".

| Nhãn (nguyên văn) | Shot |
|---|---|
| Động cơ 1 500 kW* → hộp số chia công suất | S01 |
| 3 500 kg/h tổng* (gồm biên tấm + phụ gia) | S01 |
| Vít 300 v/ph* · ≈ 800 kW* | S01 |
| Tấm 2 100 × 0,8 mm* · ≈ 25 m/min | S01 |
| Động cơ 1 500 kW* · 1 119 v/ph khi vít 300 v/ph | S02 |
| Hộp số chia công suất i ≈ 3,73* (sơ đồ nguyên lý) | S02 |
| Mô-men ≈ 12,7 kNm* mỗi trục (36 % của 35 kNm) | S02 |
| Cân chính (LIW) ≈ 3 300 kg/h* | S03 |
| Phụ gia ≈ 40 kg/h* → nhánh Y | S03 |
| Biên tấm nghiền ≈ 160 kg/h* → side feeder (B2, +Y) | S03 |
| PET không sấy: ẩm 0,2–0,4 %* (2 000–4 000 ppm) | S03 |
| ≈ 7–14 kg/h* nước đi vào máy cùng hạt | S03 |
| B1 · cấp liệu · áo nước ≈ 50 °C* | S04 |
| B2 · 260 °C* · cửa side feeder | S04 |
| Chân không 1 (B3) ≈ 50 mbar*: rút phần lớn hơi nước | S04 |
| B3 · 275 °C* | S04 |
| Chậm 20× (thực 300 v/ph*) | S04 |
| Vít Ø167,5 / lõi 116,5 (mô hình) · khe đỉnh ≈ 0,7 mm* | S05 |
| B4 · 270 °C* · khối nhào trộn KB 45° × 2 + KB 90° | S06 |
| Chân không 2 (B5): 5–20 mbar* | S07 |
| Ẩm 2 000–4 000 ppm* → < 50 ppm* | S07 |
| IV 0,80 → ≥ 0,77 dl/g* | S07 |
| B6 · 265 °C* · bước 1D → 0,75D: tăng áp | S08 |
| 2–3D cuối đầy 100 % → P1 ≈ 100 bar* | S08 |
| Nhựa ra ≈ 285 °C* | S08 |
| Lưới 60 µm* · 970 cm² lọc | S09 |
| P2 ≈ 95 bar* → Δp ≈ 45 bar* → P3 = 50 bar* | S09 |
| P3 = 50 bar* (hút) | S10 |
| P4 ≈ 250 bar* (đẩy) | S10 |
| Tốc độ bơm đặt (chủ) ≈ 69 v/ph* → lưu lượng ra khuôn cố định | S10 |
| P3 giữ 50 bar* bằng cách chỉnh cân + vít theo tỉ lệ | S10 |
| Khuôn 270–280 °C* (mép +10 °C*) | S11 |
| P5 ≈ 200 bar* ở cửa vào khuôn | S11 |
| Khe môi 1,0 mm* · khe gió 200 mm → khe trục | S12 |
| Màn nhựa ≈ 275 °C* · 2 400 → ≈ 2 200 mm* (co hẹp) | S13 |
| Trục dưới ≈ 60 · giữa ≈ 55 · trên ≈ 45 °C* | S13 |
| Tấm 0,8 × 2 100 mm* · ≈ 25 m/min · đầu đo quét ngang | S13 |
| Trung thế → tủ biến tần → động cơ 1 500 kW* | S14 |
| Tủ điều khiển + nhiệt (PLC) · ≈ 260 kW* nhiệt | S14 |
| (2) PIC-P3: áp hút 50 bar* → chỉnh cân LIW + tốc độ vít theo tỉ lệ | S15 |

## Phụ lục C. Những gì chưa có nguồn công khai (theo `specs.md` §10 và `design.md` §9)

- Bản vẽ chính thức của ZE 155 UT: chiều rộng, chiều cao, kích thước khung đế, hình khối và kích thước hộp số, kích thước miệng cấp liệu, thể tích dầu bôi trơn, công suất nhiệt từng vùng.
- Dải năng suất chính thức của ZE 155 (chỉ suy ra từ ZE 180).
- Hãng hộp số và động cơ thực tế lắp trên ZE 155; độ cao trục vào hộp số và cách đặt động cơ.
- Không tìm thấy một dây chuyền ZE 155 nào lắp khuôn T. Nguồn KM chỉ nói chung chung là dùng ZE UT, ZE UTXi hoặc ZE BluePower cho tấm PET (c040).
- Đường kính và hình dáng ngoài xi lanh ZE 155 (vỏ tròn hay vuông, kích thước bích).
- Kích thước thân khuôn T 2,4 m từ một bảng dữ liệu của hãng (cao, sâu, khối lượng); các số ở §5 đều là ước lượng.
- Kích thước thân và công suất truyền động của bơm extrex cỡ 100/125; ý nghĩa đầy đủ các chữ F/G/H/I trong bản vẽ Gneuss.
- Cỡ cụm chân không đúng cho PET 3,5 t/h (lưu lượng hút, số cấp bơm).
- Mã màu RAL chính thức của KraussMaffei Berstorff; các mã hex ở §9 chỉ lấy mẫu từ ảnh.
- Vị trí thật của ống góp nước và HMI (+Y hay −Y) trên một máy ZE UT cỡ lớn.
