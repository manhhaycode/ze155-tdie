# Thông số tổng hợp — ZE 155 UT, L/D 34, khuôn phẳng chữ T (T-die)

Tài liệu này gom các số liệu có nguồn (mã `cNNN` trỏ tới `research/claims.jsonl`) và các giá trị **ước lượng** (ghi rõ "ước lượng" và cách suy ra). Ảnh tham chiếu: `research/web/images.md` (web-01 … web-20). Hệ toạ độ theo `BRIEF.md`: X dọc trục vít, +X theo chiều chảy (động cơ → hộp số → xi lanh → đường chảy nhựa nóng → khuôn), X = 0 tại mặt bích ra của hộp số / mặt đầu xi lanh số 1, Z = 0 mặt sàn, +Y phía người vận hành.

## 0. Quyết định thiết kế (vì không có nguồn nào mô tả đúng một dây chuyền ZE 155 + T-die)

| Hạng mục | Quyết định | Lý do |
|---|---|---|
| Phiên bản máy | **ZE 155 A UTi** (D/d ≈ 1,46). Bản R chỉ khác vít (đường kính 181 mm, rãnh sâu hơn) và mômen nhỏ hơn; nhìn từ ngoài thì giống bản A. | Bảng KM có cả A và R (c001–c012); hai bản cùng khoảng cách tâm trục (c030), nên xi lanh, hộp số, khung đế giống nhau. |
| Ứng dụng | Đùn tấm PET trực tiếp, không sấy trước (direct sheet extrusion): ZE → van khởi động (start-up/diverter valve) → bộ lọc lưới (screen changer) → bơm bánh răng (melt gear pump) → ống/adapter → khuôn T → cụm cán láng 3 trục (polishing roll stack) | KM xác nhận dùng ZE UT cho tấm PET trực tiếp cùng PlanetCalender (c040); dây chuyền tấm quang học của KM có bộ lọc thuỷ lực và bơm nhựa nóng (c043); sơ đồ catalogue có diverter valve, slot die, smoothing roll (c035). |
| Năng suất thiết kế | **3 500 kg/h** (dải 2 500–5 000 kg/h) — ước lượng | ZE 180 A cũ chạy 1 750–7 000 kg/h (c019). Lấy theo tỷ lệ mômen 35 000/48 500 = 0,72 thì ZE 155 vào khoảng 1 260–5 050 kg/h. KM đã làm dây chuyền tấm trục đôi tới 6 t/h (c041). |
| Khổ tấm | Tấm thành phẩm rộng 2 100 mm, dày 0,3–1,5 mm; **khe môi khuôn (lip/slot) rộng 2 400 mm** — ước lượng | Cụm trục cán xử lý được tối đa khoảng 1 800 kg/h PET trên mỗi mét khổ (c046). 3 500 kg/h ÷ 2,1 m = 1 670 kg/h·m, dưới giới hạn đó. Khe môi lấy rộng hơn tấm khoảng 150 mm mỗi bên để bù co hẹp (neck-in) và phần xén biên (edge trim). |

## 1. Máy đùn ZE 155 UT — số liệu chính

| Thông số | Giá trị | Nguồn / cách suy ra |
|---|---|---|
| Đường kính vít danh nghĩa (screw diameter), bản A | **169 mm** | c001 (bảng KM). Đã kiểm tra cách khớp dòng với loại máy: ZE 130 A = 140 mm (khớp máy cũ "2x140 mm"), ZE 180 A = 194 mm (khớp lỗ xi lanh 194 mm của máy cũ, c017). |
| Đường kính vít, bản R | 181 mm | c009 |
| Chiều sâu rãnh vít (flight depth) A / R | 27,2 / 38,9 mm | c002, c010 |
| Đường kính lõi vít (core d), A | **114,6 mm** | Tính d = D − 2h = 169 − 2×27,2. Cách tính này đúng với ZE 180: 194 − 2×31,2 = 131,6, máy cũ ghi 131,7 (c017). |
| D/d | 1,47 (A), 1,75 (R) | Tính từ hai dòng trên; catalogue ghi danh nghĩa 1,46 / 1,74 (c028, c029). |
| Đường kính ngoài thực của vít | ≈ 167,5 mm (ước lượng) | Bảng ghi đường kính bằng lỗ xi lanh (ZE 180: 194 mm lỗ, vít 192,3 mm, c017). Lấy cùng tỷ lệ 0,991. |
| **Khoảng cách tâm hai trục vít (centre distance a)** | **≈ 142 mm** (ước lượng, độ tin cậy cao) | a = (D + d)/2 = (169 + 114,6)/2 = 141,8. Cách tính này khớp ZE 180 (162,8 so với 163, c017) và ZE 110 (99,7 so với 100, c020). Bản R cho ra 142,1, đúng như việc A và R cùng khoảng cách tâm (c030). |
| Lỗ xi lanh hình số 8 (figure-8 bore) | rộng 311 mm (a + D) × cao 169 mm | Hình học suy từ a và D. |
| Tốc độ vít tối đa | **400 v/ph** (cao hơn thì theo yêu cầu) | c003, c013 |
| Mômen mỗi trục | **2 × 35 000 Nm** (A); 2 × 30 000 Nm (R) | c005, c012 |
| Mômen riêng (Md/a³) | ≈ 12,2 Nm/cm³ (A); 10,5 (R) | Tính: 35 000 / 14,2³. |
| Công suất truyền động tối đa | **2 930 kW** (A); 2 515 kW (R) | c004, c011. Kiểm tra: 2 × 35 000 Nm × 2π × 400/60 = 2 932 kW, tức là đủ mômen ở tốc độ tối đa. Công suất thực lắp đặt chọn theo quy trình (c013). |
| Chiều cao trục vít so với sàn (axis height) | **1 200 mm** | c006 |
| Chiều dài toàn máy tại L/D 44 | 11 700 mm (số không ràng buộc) | c007 |
| **Chiều dài toàn máy tại L/D 34** | **≈ 10 000 mm** (ước lượng) | 11 700 − 10 × 169 = 10 010. Kiểm tra bằng ZE 110: bảng ghi 9 000 mm tại 44D, trừ 16D ra 7 096 mm, máy thật 28D đo được 6 850 mm (c021), lệch 3,5 %. |
| Khối lượng tại 44D | ≈ 34 000 kg | c008 |
| Khối lượng tại 34D | ≈ 31 000 kg (ước lượng) | Bớt 10D xi lanh và vít, ≈ 1 330 kg/m × 1,69 m + vỏ/ống ≈ 2,5 t. |
| Chiều rộng máy (khung đế, chưa tính HMI) | ≈ 2 000 mm (ước lượng) | ZE 110 28D rộng 1 400 mm (c021), nhân tỷ lệ 169/119 = 1,42. |
| Chiều cao tới đỉnh xi lanh (chưa tính phễu, ống hút chân không) | ≈ 2 000 mm (ước lượng) | ZE 110 cao 1 650 với trục ở 1 100, tức 550 mm trên trục; × 1,42 ≈ 780 mm; 1 200 + 780. |
| Chiều dài đoạn gia công (processing section) 34D | **5 746 mm** | 34 × 169 |
| Các đoạn xi lanh (barrel sections) | Dài 4D = 676 mm, 6D = 1 014 mm | Loại 4D/6D: c031 |
| Cấu hình đề xuất (ước lượng) | B1 4D cấp liệu (mở phía trên) · B2 6D kín (nóng chảy) · B3 6D mở: thoát khí khí quyển hoặc chân không nhẹ · B4 6D kín (trộn) · B5 6D **thoát khí chân không**, miệng dài 6D · B6 6D kín (tăng áp). Tổng 4 + 5×6 = 34D | ZE có miệng thoát khí dài 6D (c036). Tấm PET cần hút ẩm và hút sâu; có một máy ZE-R dùng 3 cửa thoát khí khí quyển + 1 cửa chân không (c070; chỉ là bối cảnh, không phải bằng chứng cho cấu hình này). |
| Vật liệu, cách nối xi lanh | ZE ≥ 90: xi lanh thép thấm nitơ nguyên khối, có lót CrMo hoặc composite (c032). Cỡ lớn nối bằng **bích bắt bulông**, không dùng kẹp chữ C | Ảnh web-01/02 (ZE 110 R) cho thấy vành bích bulông. KM cũng ghi rằng ZE BluePower cỡ lớn chuyển sang nối bulông (c037). |
| Gia nhiệt xi lanh | ≈ 25 kW mỗi đoạn 6D (ước lượng) | ZE 180: 30 kW/đoạn (c018); giảm theo cỡ máy. |
| Làm mát xi lanh | Nước, mỗi vùng một van điện từ (solenoid) + van bi, có ống góp cấp/hồi (manifold) | Ảnh web-02 |

### 1.0 Cỡ máy lân cận dùng để quy tỷ lệ (bảng KM, tại L/D 44)

| Cỡ (bản A) | D (mm) | Rãnh (mm) | v/ph | kW | Mômen mỗi trục (Nm) | Cao trục (mm) | Dài L (mm) | Khối lượng (kg) | Nguồn |
|---|---|---|---|---|---|---|---|---|---|
| ZE 110 A UTi | 119 | 19,3 | 900 | 2 300 | 12 200 | 1 100 | 9 000 | 20 000 | c016 |
| ZE 130 A UTi | 140 | 22,6 | 600 | 2 515 | 20 000 | 1 200 | 10 400 | 28 000 | c014 |
| **ZE 155 A UTi** | **169** | **27,2** | **400** | **2 930** | **35 000** | **1 200** | **11 700** | **34 000** | c001–c008 |
| ZE 180 A UTi | 194 | 31,2 | 300 | 3 050 | 48 500 | 1 400 | 13 400 | 45 000 | c015 |

Máy thật để đối chiếu: ZE 110 R 28D (2016) có L × W × H = 6 850 × 1 400 × 1 650 mm, nặng 12 800 kg (c021, c022). ZE 25 UTXi cũng có cao trục 1 200 mm (c027).

### 1.1 Bộ truyền động (drive train)

| Bộ phận | Giá trị | Nguồn / cách suy ra |
|---|---|---|
| Hộp số (gearbox) | Kiểu chia công suất (power branching), hai trục ra then hoa (spline), bôi trơn kết hợp ngâm dầu và dầu áp lực (dip + pressure), có khớp an toàn chống quá tải (safety coupling) | c033; ZE 180 có trục then hoa 24 răng (c017) |
| Hãng hộp số | Flender (ZE 110 R 56D, c025; tem "SIEMENS FLENDER DRIVES" trên ZE 110 R, c023) hoặc Eisenbeiss (ZE 52, c026); ZE 180 ghi "Berstorff gearbox" (c018) | Chưa tìm thấy hãng cụ thể cho ZE 155 |
| Kích thước hộp số | ≈ dài 1 600 × rộng 1 400 × cao 1 700 mm, ≈ 8–10 t (ước lượng) | Phải chịu 2 × 35 kNm. Hình khối theo ảnh web-11 (Eisenbeiss) và web-01 (hộp số xanh). Nên chỉnh lại theo ảnh catalogue (người phân tích PDF). |
| Tỷ số truyền | ≈ 3,7 (ước lượng) | Động cơ 4 cực 1 490 v/ph chia 400 v/ph |
| **Động cơ chính đề xuất vẽ** | **Động cơ cảm ứng trung thế 4 cực ≈ 2 000 kW, chạy biến tần (VFD), cỡ khung ABB AMI 450L4**: dài L = 2 025 mm, tâm trục H = 450 mm, cao tổng HC = 1 860 mm, rộng AE = 1 500 mm, ≈ 4,5–4,7 t | Kích thước: c066; khối lượng: c065 (1 750 kW, 4 680 kg). Ước lượng công suất: 3 500 kg/h × 0,22 kWh/kg ≈ 770 kW cho PET, nhân thêm dự phòng cho PP độn và lúc khởi động; 2 000 kW cho phép đủ mômen tới khoảng 270 v/ph. |
| Phương án dùng hết công suất tối đa | 2 930 kW, khung AMI 500L4 (2 500 kW): L = 2 265, H = 500, HC = 2 060 mm, ≈ 6,0 t | c064, c067. ZE 180 dùng động cơ Siemens 3 000 HP (c018). |
| Vị trí động cơ | Trục động cơ đồng trục với trục vào hộp số; đặt trên bệ thép. Nếu trục vào nằm ở độ cao trục vít 1 200 mm thì bệ cao ≈ 750 mm (ước lượng) | Chưa tìm thấy bản vẽ |
| Khớp nối + vỏ che (coupling guard) | Dài ≈ 600–700 mm (ước lượng) | Ảnh web-12 (vỏ che màu cam trên dây chuyền KM) |
| Cụm dầu bôi trơn (lube unit) | Bơm có động cơ mặt bích đứng, lọc kép, đồng hồ áp, bộ trao đổi nhiệt dạng tấm dầu/nước; đặt trên khung đế cạnh hộp số | Ảnh web-03; catalogue ghi khung đế chứa hệ dầu (c034) |

## 2. Cấp liệu (feeding)

| Bộ phận | Giá trị | Nguồn / cách suy ra |
|---|---|---|
| Cân cấp liệu chính (loss-in-weight) | Coperion K-Tron BSP-150-S cho hạt PET: 34–6 700 dm³/h, treo trên 3 cảm biến cân, phễu nối thêm tới 320 dm³ (cao 1 684, Ø 600 mm) | c069. 3 500 kg/h ÷ 0,8 kg/dm³ ≈ 4 400 dm³/h, nằm trong dải. Nếu cấp vảy chai (bulk ≈ 0,3) thì phải dùng cân trục vít đôi lớn hơn (ước lượng). |
| Cân phụ gia / masterbatch | 1–2 cân trục vít đôi cỡ nhỏ (loại K-ML-D5-T35) | Ước lượng |
| Sàn đặt cân (feeder platform) | Sàn thép ngay trên B1, mặt sàn cao ≈ 2 800–3 200 mm, có lan can vàng và cầu thang; ống rơi liệu xuống miệng B1 | Ước lượng theo ảnh web-04/05 (Lanxess: cân đặt trên tầng lửng) |
| Miệng cấp liệu (feed opening) trên B1 | ≈ 300 × 250 mm (ước lượng) | Chưa tìm thấy |
| Máy hút liệu (vacuum loader) | Đặt trên phễu từng cân | Ước lượng |

## 3. Thoát khí và chân không (venting / vacuum)

| Bộ phận | Giá trị | Nguồn / cách suy ra |
|---|---|---|
| Cửa thoát khí chân không trên B5 | Miệng dài 6D (≈ 1 000 mm) × ≈ 300 mm; nắp vòm (vent dome) có kính quan sát; ống DN 150 đi lên rồi sang bình tách ngưng | Miệng 6D: c036. Kích thước nắp: ước lượng từ lỗ xi lanh rộng 311 mm. |
| Cửa trên B3 | Thoát khí khí quyển (hoặc chân không nhẹ), có ống xả nhỏ | Ước lượng |
| Mức chân không cho PET không sấy | Hút sâu, khoảng 1–10 mbar, dùng bơm Roots hai cấp | c062 (nguồn nhà máy TQ, độ tin cậy thấp). Compounding thông thường chỉ 100–300 mbar (c061). |
| Cụm chân không (vacuum unit) | Skid ≈ 2 000 × 1 200 × 1 800 mm gồm bình tách ngưng (condensate separator) inox đứng, bơm Roots, bơm lót khô; đặt phía −Y cạnh B5 (ước lượng) | Hình dáng theo web-15 (Busch PLASTEX: bình lọc đứng + bơm MINK, c060); bộ TK-V có buồng ngưng và bơm vòng nước (c063) |
| Bơm cỡ tham khảo | Busch MINK MM 1202 AV: 200 m³/h, 4,3 kW, 1 010 × 515 × 450 mm, 240 kg (ZE 110 R dùng 2 bơm loại này, c024) | c059 |

## 4. Đường chảy nhựa nóng (melt line), theo thứ tự +X

| Bộ phận | Giá trị | Nguồn / cách suy ra |
|---|---|---|
| Tấm đầu xi lanh + adapter chuyển từ lỗ số 8 sang lỗ tròn | Dài ≈ 250 mm, Ø ngoài ≈ 450 mm (ước lượng) | — |
| Van khởi động / van chuyển hướng (start-up/diverter valve) | Khối ≈ 400 (X) × 500 × 500 mm, xi lanh thuỷ lực đặt ngang, có máng xả nhựa xuống sàn (ước lượng) | Có trong sơ đồ catalogue (c035) |
| **Bộ lọc lưới (screen changer)** | **Gneuss RSFgenius 200**: lưới hoạt động 970 cm², 4 560 kg/h, kích thước A 1 955 (dài tổng) · B 705 · C 1 429 (cao tổng) · D 550 · E 1 040 mm, 3 800 kg, gia nhiệt điện 39 kW chia 6 vùng, 200 bar | c050; công suất tính ở 1 000 Pa·s, 60 µm, Δp 40 bar (c052). Phương án nhỏ hơn: RSFgenius 175, 3 300 kg/h, 2 200 kg (c051). Chiều dày thân theo chiều chảy ≈ 600–800 mm (ước lượng, chưa rõ ý nghĩa từng chữ F/G/I trong bản vẽ hãng). Ảnh web-13. |
| **Bơm bánh răng nhựa nóng (melt gear pump)** | **Maag extrex6 GU 100/125**: 764 cm³/vòng, 4 474 kg/h ở 134 v/ph (ở 3 500 kg/h chạy ≈ 105 v/ph); áp ra ≤ 370 bar, Δp ≤ 250 bar | c047, c049. Thân bơm ≈ 500 × 450 × 450 mm (ước lượng); ảnh web-14. |
| Động cơ bơm | Động cơ hộp số ≈ 45–55 kW, nối trục các-đăng; động cơ đặt đứng trên hộp giảm tốc như ảnh web-07 (ước lượng) | Công suất thuỷ lực Q·Δp ≈ 0,75 L/s × 200 bar ≈ 15 kW, nhân dự phòng |
| Bộ trộn tĩnh (static mixer) | Tuỳ chọn, ống DN ≈ 120, dài ≈ 600 mm (ước lượng) | — |
| Ống/adapter dẫn vào khuôn | Ống có gia nhiệt, lớp cách nhiệt và vỏ inox | Ước lượng |
| Tổng chiều dài từ cuối xi lanh tới cửa vào khuôn | ≈ 2 500–3 000 mm (ước lượng) | — |
| Cao độ đường tâm nhựa | Giữ 1 200 mm suốt (bằng trục vít), môi khuôn ở Z ≈ 1 200 | Ước lượng, để đơn giản |
| Giá đỡ | Bộ lọc và bơm ngồi trên khung thép riêng; khuôn đặt trên xe khuôn (die cart) có bánh và kích vít chỉnh cao | Xe khuôn: ảnh web-08 (KM), Nordson có die cart (c057) |

## 5. Khuôn phẳng chữ T (flat T-die, coat-hanger)

| Thông số | Giá trị | Nguồn / cách suy ra |
|---|---|---|
| Kiểu | Ống phân phối hình móc áo (coat-hanger manifold), cấp liệu chính giữa từ phía sau; môi trên mềm (flex lip) + thanh chắn (choker/restrictor bar) phía trước ống phân phối; môi dưới thay được | c053, c055, c057 |
| Chiều rộng khe môi (working width) | **2 400 mm** (quyết định ở §0) | Reifenhäuser làm khuôn tấm định hình nhiệt rộng 75–3 500 mm, khe 0,15–6 mm (c056) |
| Chiều rộng thân kể cả tấm đầu (end plates) | ≈ 2 750 mm; tính cả hộp đầu nối dây nhiệt / thanh deckle ≈ 3 050 mm (ước lượng) | — |
| Chiều cao thân (theo Z, hai nửa khuôn) | ≈ 500 mm (nửa trên 260, nửa dưới 240) (ước lượng) | Theo tỷ lệ trong ảnh web-19/20 |
| Chiều sâu theo chiều chảy (X), từ mặt vào tới môi | ≈ 450 mm, mũi môi vát nhọn 30–45° về phía khe trục cán (ước lượng) | Ảnh web-17/18 |
| Bulông chỉnh môi (lip adjusting bolts) | Bước **25,4 mm** → ≈ 94 bulông; nếu tự động thì dùng bulông nhiệt (thermal bolts) 80 W, có ống gió làm mát | c053, c054 |
| Bulông chỉnh thanh chắn | Bước ≈ 50–75 mm, nằm trên mặt nửa khuôn trên (ước lượng) | Ảnh web-19 |
| Hành trình môi mềm | ≈ 1–2,5 mm | c055 (0,040"), c056 (2,5 mm) |
| Gia nhiệt | Thanh nhiệt cắm (cartridge heaters), vùng rộng ≈ 250–300 mm → ≈ 9 vùng mỗi nửa + 2 tấm đầu ≈ 20 vùng; tổng ≈ 50 kW (ước lượng) | Khuôn Cloeren 62" (1 575 mm) dùng 32,8 kW (c055), tức ≈ 21 kW/m |
| Khối lượng | ≈ 2 000 kg (ước lượng) | Cloeren 62" nặng 1 032 kg (c055); quy theo chiều rộng 2 400 mm ra ≈ 1 570 kg, cộng thêm phần thân dày (heavy-duty) và thanh chắn |
| Hướng ra nhựa | Nằm ngang theo +X, vào khe giữa trục 1 và trục 2 | Ước lượng; PlanetCalender cho phép xoay cả khung để chỉnh góc vào của màng nhựa (c044) |

## 6. Cụm cán láng / trục làm nguội (polishing / chill roll stack)

| Thông số | Giá trị | Nguồn / cách suy ra |
|---|---|---|
| Kiểu | 3 trục, kiểu PlanetCalender: trục 1 và 3 chỉnh vị trí quanh trục giữa 2, khung xoay được, thay trục giữa trong 30 phút; sau đó là băng con lăn làm nguội đi theo trục cuối | c044; ảnh web-09 |
| Đường kính trục | **800 mm** | Đường kính trục thường 400–800 mm (c046); lấy đầu trên vì năng suất cao |
| Chiều dài mặt trục (face width) | 2 600 mm (ước lượng: khe môi 2 400 + 100 mỗi bên) | — |
| Khung tổng | ≈ rộng 3 800 (Y) × dài 2 500 (X) × cao 2 800 mm (ước lượng) | — |
| Vị trí so với khuôn | Khe trục 1–2 ở Z ≈ 1 200 mm; môi khuôn cách khe trục ≈ 50–150 mm | Ước lượng theo ảnh web-18 (môi khuôn sát khe) |
| Lùi ra | Cả cụm trục chạy trên ray sàn theo X, hành trình ≈ 1 000–1 500 mm, để mở khoảng trống trước khuôn (ước lượng) | — |

## 7. Điều khiển, điện, bảo vệ

| Bộ phận | Giá trị | Nguồn / cách suy ra |
|---|---|---|
| HMI | Màn hình cảm ứng trên chân đế hoặc tay xoay phía +Y, gần B1–B3; dây chuyền mới của KM đặt màn hình trên vỏ cụm truyền động (web-06), dây chuyền Lanxess đặt trên chân đế cạnh máy (web-04/05) | Ảnh |
| Tủ điện | Tủ điều khiển và tủ nhiệt nằm trong khung đế hoặc đặt sát máy (catalogue, c034); tủ biến tần trung thế đặt ở phòng điện riêng (ước lượng, không vẽ) | — |
| Nắp che xi lanh | Kiểu UT cũ: vỏ nhiệt kim loại tròn, để lộ (web-01/02). Kiểu KM mới: nắp inox có bản lề, dán tam giác cảnh báo màu vàng (web-06/07/16) | Ảnh |
| Máng cáp | Máng thép mạ kẽm đục lỗ chạy dọc dưới xi lanh; hộp đấu dây vuông dưới mỗi đoạn xi lanh | web-01/02 |
| Ống góp nước làm mát | Ống inox chạy dọc khung đế (ống cấp + ống hồi), mỗi vùng một van điện từ và một van bi tay đỏ, ống mềm inox dẫn lên xi lanh. Đặt phía +Y như ảnh web-06 (ước lượng) | web-02, web-06, c023 |

## 8. Bố trí và kích thước bao (overall envelope) đề xuất

Vị trí theo trục X (mm, ước lượng):

| Đoạn | X bắt đầu → kết thúc | Ghi chú |
|---|---|---|
| Động cơ AMI 450L4 | −4 250 → −2 225 | dài 2 025 (c066) |
| Khớp nối + vỏ che | −2 225 → −1 600 | |
| Hộp số | −1 600 → 0 | mặt bích ra ở X = 0 (theo BRIEF) |
| Đoạn gia công 34D (B1…B6) | 0 → 5 746 | B1 4D: 0–676; B2: 676–1 690; B3: 1 690–2 704; B4: 2 704–3 718; B5: 3 718–4 732; B6: 4 732–5 746 |
| Tấm đầu + adapter | 5 746 → 6 000 | |
| Van khởi động | 6 000 → 6 400 | |
| Bộ lọc RSFgenius 200 | 6 400 → 7 100 | |
| Bơm bánh răng + ống | 7 100 → 8 950 | gồm bơm ≈ 500, bộ trộn tĩnh ≈ 600, ống/adapter |
| Khuôn T | 8 950 → 9 400 | môi khuôn ở X ≈ 9 400 |
| (Cụm trục cán) | 9 500 → 12 000 | khe trục ở X ≈ 9 500 |

Kiểm tra lại: động cơ + hộp số + đoạn gia công = 4 250 + 5 746 ≈ 10 000 mm. Con số này khớp với chiều dài 34D suy ra từ bảng KM (§1).

**Kích thước bao đề xuất: ZE 155/34D + đường chảy nhựa + khuôn T (chưa tính cụm trục cán):**
- **Dài ≈ 13 700 mm** (X từ −4 250 tới +9 400). Nếu tính cả cụm trục cán: ≈ 16 300 mm.
- **Rộng ≈ 4 300 mm** (Y từ −2 600 tại mép skid chân không tới +1 700 tại chân HMI). Riêng khung máy rộng ≈ 2 000; khuôn T rộng ≈ 3 050; khung cụm trục ≈ 3 800.
- **Cao ≈ 5 500 mm** nếu tính sàn cân cấp liệu (mặt sàn ≈ 3 000, cộng cân, phễu, máy hút liệu). Riêng máy đùn và đường chảy nhựa (vòm chân không, ống) cao ≈ 2 800 mm; động cơ đặt trên bệ ≈ 750 + 1 860 = 2 610 mm.
- Cách suy ra: chiều dài máy lấy từ bảng KM tại 44D trừ 10D (§1), cộng chiều dày từng khối của đường chảy nhựa (bộ lọc theo bảng Gneuss, bơm theo cỡ Maag, phần còn lại ước lượng) và chiều sâu khuôn. Chiều rộng máy lấy từ ZE 110 thật nhân tỷ lệ 1,42. Chiều rộng khuôn theo §0/§5. Chiều cao từ cao độ trục 1 200 (c006) cộng phần trên trục quy đổi từ ZE 110.

## 9. Màu sắc (colour scheme)

| Bộ phận | Màu | Nguồn |
|---|---|---|
| Khung đế, tấm che, tủ trên máy | Trắng / xám rất nhạt; giá trị lấy mẫu ≈ #DCDCDC trên ảnh render KM, ≈ #A9BAC3 trên ảnh chụp trong xưởng (có bóng đổ) | web-01, web-06; c023 ("base bianca") |
| Màu nhấn KM | Xanh KraussMaffei ≈ **#008DC3** trên tấm tủ / dải khung, chữ "KraussMaffei" màu trắng | web-08, web-09 (lấy mẫu) |
| Hộp số + cụm dầu (máy UT 2016) | Xanh lam đậm ≈ **#1F6FD0 … #3665B0** (sơn chuẩn Flender) | web-01, web-03 (lấy mẫu); c023 |
| Hộp số (render KM mới) | Trắng / xám nhạt, nằm trong vỏ cụm truyền động | web-06 |
| Động cơ chính | Xanh lam (ABB: NCS 4822-B05G; động cơ lớn trong render KM màu xanh đậm) | c068 (độ tin cậy thấp), web-12 |
| Xi lanh / vỏ nhiệt | Inox sáng bóng (máy UT cũ); nắp inox xước + tam giác cảnh báo vàng (KM mới) | web-01/02, web-06/07 |
| Ống góp nước | Inox, tay van bi màu đỏ | web-02, c023 |
| Máng cáp | Thép mạ kẽm | web-01 |
| Sàn thao tác, lan can, cầu thang | Lan can và tấm chắn chân màu vàng an toàn, khung thép xám nhạt | web-04, web-05 |
| Bộ lọc lưới, bơm bánh răng | Inox / thép mài, không sơn (logo Gneuss màu đỏ) | web-13, web-14 |
| Khuôn T | Thép mạ crôm sáng, đầu bulông đen, hộp đầu nối dây nhiệt bằng inox | web-17…20 |
| Trục cán | Mạ crôm gương; khung cụm trục trắng có dải xanh KM | web-09 |
| Vỏ khớp nối | Cam hoặc vàng | web-12 |

## 10. Chưa tìm thấy (chưa có nguồn công khai)

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
