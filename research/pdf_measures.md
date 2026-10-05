# Số đo từ catalogue – ZE 155 UT (silhouette trang 9) và sơ đồ slot die (trang 24–25)

Nguồn: `research/pdf/ZE_twin-screw_extruders.pdf`. Mọi toạ độ gốc là **điểm PDF (pt, 1/72 inch)** trên trang 9, trục y hướng xuống, lấy trực tiếp từ đường vector (PyMuPDF `page.get_drawings()`), nên sai số đọc chỉ khoảng ±0,05 pt. Phần không chắc chắn nằm ở **thang đo** (§3) và ở việc **hình vẽ là hình mẫu minh hoạ** (§1), không phải ở phép đo.

Tệp liên quan trong `research/pdf_crops/`:
- `ze155ut_side.svg`: vector sạch (drawing #85–#125, giữ nguyên toạ độ trang, viewBox 327 456 225 54 pt). Có thêm `ze130ut_side.svg`, `ze180ut_side.svg`.
- `ze155ut_side_svg_render.png` (4000 px), `ze155ut_side_600dpi.png` (1875×450, 8,333 px/pt), `ze155ut_side_1200dpi.png` (3750×900, 16,667 px/pt; gốc vùng cắt x = 327 pt, y = 456 pt).
- `ze155ut_side_annotated.png`: ô bao từng cụm, kích thước mm, đường sàn/trục vít, thước X theo BRIEF.
- `ze155ut_side_outline_pt.json`: đa giác đường bao ngoài (267 đỉnh) cùng 3 lỗ trắng, tính bằng pt.

---

## 1. Hình vẽ là gì

- Trang 9 là vector thuần (135 đối tượng, không có bitmap). ZE 155 UT gồm: #85 nền navy `#173467` (đường bao ngoài cộng 3 lỗ), #86–87 khối cao ở cuối máy, #88–108 chân (feet), #125 nét trắng chi tiết (4697 đoạn).
- **Không cùng tỉ lệ giữa các cỡ máy.** Chiều dài vẽ: ZE 130 = 219,9 pt, ZE 155 = 209,3 pt (219,8 pt nếu tính khối cuối), ZE 180 = 230,9 pt. Nếu vẽ theo tỉ lệ thì ZE 180 phải dài gấp khoảng 1,16 lần ZE 155. Thực tế **ZE 180 UT là đúng hình ZE 155 UT phóng ×1,05** (bước vỏ che 14,44 so với 13,72 pt, chiều cao 49,75 so với 47,41 pt, hộp số 31,4 so với 29,85 pt). Kết luận: đây là hình mẫu chung cho các cỡ UT lớn. Chỉ dùng được **tỉ lệ nội bộ**. Thang mm phải lấy từ một mốc bên trong hình (§3).
- Hướng nhìn: đầu ra (+X) ở **trái**, động cơ ở phải, khớp với hình chiếu đứng trong BRIEF. Hình không cho biết đó là phía người vận hành hay phía sau. Cụm dầu bôi trơn vẽ phía trước motor, tức nằm ở phía người xem.

## 2. Số đo silhouette (pt), tỉ lệ

Mốc dùng:
- **Sàn** (đáy chân đế) y = 507,23 pt.
- **Mối nối barrel/lantern** x = 449,10 pt, là tâm C-clamp cuối cùng. Đây là X = 0 theo BRIEF, +X sang trái.
- **Bước barrel p** = 13,72 pt. Bước vỏ che đo được 13,57 / 13,69 / 13,73 / 13,735 / 13,72 / 13,635 (trung bình 4 khe giữa = 13,719). Bước clamp ở đoạn lộ: 422,48 → 436,215 → 449,095, tức 13,735 và 12,88 (feed barrel).

### 2.1 Cao độ (y → chiều cao trên sàn)
| Mốc | y (pt) | Cao trên sàn (pt) | ÷ p |
|---|---|---|---|
| Đáy khung đế | 505,96 | 1,27 | 0,09 |
| Ranh dầm trên / hộp dưới khung đế | 497,36 | 9,87 | 0,72 |
| Đỉnh khung đế | 492,67 | 14,56 | 1,06 |
| Đáy barrel (đoạn lộ) | 484,07 | 23,16 | 1,69 |
| **Trục vít** (tâm barrel lộ) | 478,79 | 28,44 | 2,07 |
| Đỉnh barrel | 473,51 | 33,72 | 2,46 |
| Đỉnh vỏ che barrel | 471,03 | 36,20 | 2,64 |
| Đỉnh hộp số | 467,64 | 39,59 | 2,89 |
| Đỉnh lantern / hộp trên motor | 467,25 | 39,98 | 2,91 |
| Đỉnh phễu | 466,99 | 40,24 | 2,93 |
| Đỉnh thân vent dome | 460,47 | 46,76 | 3,41 |
| Đỉnh tai vent (cao nhất) | 459,82 | 47,41 | 3,46 |

### 2.2 Các cụm (pt)
| Cụm | x (pt) | y (pt) | Dài × cao (pt) | ÷ p (dài; cao) |
|---|---|---|---|---|
| Khung đế toàn bộ | 329,87–539,19 | 492,67–505,96 | 209,32 × 13,29 | 15,26; 0,97 |
| – đoạn trái (dưới barrel) | 329,87–442,44 | | 112,57 | 8,20 |
| – đoạn phải (dưới cụm dẫn động) | 443,19–539,19 | 492,41–505,96 | 96,00 | 7,00 |
| – dầm trên (top beam) | toàn chiều dài | 492,67–497,36 | – × 4,69 | 0,34 |
| – hộp tủ dưới (cửa, lỗ tròn) | toàn chiều dài | 497,36–505,96 | – × 8,60 | 0,63 |
| 6 vỏ che barrel C1–C6 | 333,42–415,50 | 471,03–492,67 | 82,08 × 21,64 | 5,98; 1,58 |
| Vent dome (thân) | 376,51–386,05 (trục 381,27) | 460,47–471,16 | 9,54 × 10,69 | 0,70; 0,78 |
| Barrel lộ 2D | 415,50–420,82 | 473,51–484,07 | 5,32 × 10,56 | 0,39; 0,77 |
| C-clamp (3 cái, ví dụ) | 434,55–437,88 | 472,47–485,11 | 3,33 × 12,64 | 0,24; 0,92 |
| Barrel lộ 4D (thân, không clamp) | 424,52–434,43 | 473,51–484,07 | 9,91 × 10,56 | 0,72; 0,77 |
| Barrel 1 – feed (thân) | 437,98–448,14 | 473,90–484,07 | 10,16 × 10,17 | 0,74; 0,74 |
| Gối đỡ barrel tại clamp (2 cái thấy được: 367,4–369,7 và 422,2–424,5) | 422,24–424,52 | 476,64–494,23 | 2,28 × 17,59 | – |
| Phễu + ống nạp nghiêng 45° | 439,64–451,04 | 466,99–473,90 | 11,40 × 6,91 | 0,83; 0,50 |
| Lantern (cửa thăm 453,74–461,36 × 476,25–481,20) | 449,93–465,19 | 467,25–486,93 | 15,26 × 19,68 | 1,11; 1,43 |
| Mặt bích vào hộp số | 465,19–467,50 | 467,25–490,58 | 2,31 × 23,33 | – |
| **Hộp số** | 467,50–497,55 | 467,64–490,58 | 30,05 × 22,94 | 2,19; 1,67 |
| Vỏ khớp nối (móc cẩu trên nóc) | 498,32–511,16 | 470,77–489,93 | 12,84 × 19,16 | 0,94; 1,40 |
| **Motor chính** (thân) | 511,92–537,08 | 471,16–489,93 | 25,16 × 18,77 | 1,83; 1,37 |
| Hộp trên motor (hộp đấu dây/quạt) | 515,78–529,15 | 467,25–473,77 | 13,37 × 6,52 | – |
| Lọc dầu kép (trước motor) | 518,01–524,88 | 475,99–482,24 | 6,87 × 6,25 | – |
| Đế motor + cụm dầu | 503,45–533,97 | 489,93–492,02 | 30,52 × 2,09 | – |
| Khối cao cuối máy | 540,14–549,67 | 469,73–500,23 | 9,53 × 30,50 | 0,69; 2,22 |

Tâm các chân đế (x, pt): 331,8; 356,5; 366,1; 371,7; 378,9; 383,8; 400,4; 434,7; 446,0; 474,7; 503,2; 531,9. Chân cao 1,27 pt. Tâm lỗ tròn trên hộp tủ (y = 501,6, Ø ≈ 3,1 pt): x ≈ 345,0; 425,2; 460,0; 526,8. Các mối dọc trên dầm trên: 347,12; 364,30; 385,28; 406,26; 427,24; 444,39; 461,55 (bước ~20,98 pt). Cửa ở hộp tủ trái: bước 19,1 pt (cửa 11,45 + khe 7,65).

### 2.3 Tỉ lệ chính
- Dài khung đế : cao trục vít : cao đỉnh vỏ che = 209,32 : 28,44 : 36,20 = **7,36 : 1 : 1,27**.
- Dài barrel (từ mặt đầu ra 333,42 đến mối nối 449,10) = 115,68 pt = **8,43 p**.
- Hộp số : lantern : motor (dài) = 30,05 : 15,26 : 25,16. Cao hộp số / cao trục = 0,81. Tâm hộp số y = 479,11, trùng trục vít (478,79), lệch 0,3 pt.
- Thân barrel / mặt bích-clamp (cao) = 10,56 / 12,64 = **0,84**. Khớp với barrel dòng UT là trụ tròn có mặt bích (trang 12).

### 2.4 L/D mà hình thể hiện
- Đoạn barrel gồm khoảng **8,5 bước p**. Có hai cách khớp bước clamp vào vỏ che. Cách 1: khe giữa các vỏ che là clamp, khi đó vent nằm giữa đoạn 4, gồm 6 đoạn che + 1 đoạn lộ 2D + 1 đoạn 4D + feed barrel. Cách 2: clamp lệch nửa bước so với khe vỏ che. Cách nào cũng cho tổng 8,43 p.
- Nếu mỗi bước là **4D** thì L/D = 8,43 × 4 = **33,7 ≈ 34**, khớp với máy mục tiêu. Nếu là 6D thì L/D ≈ 51, nhưng bị loại ở §3.
- Lưu ý: đây là hình mẫu chung (ZE 180 dùng lại y hệt), nên L/D 34 có thể chỉ là trùng hợp minh hoạ.

## 3. Thang đo pt → mm

| Mốc | Giả thiết | mm/pt | Hệ quả kiểm tra |
|---|---|---|---|
| **A (chọn)** | bước barrel p = 4D = 4 × 155 = 620 mm | **45,2** | trục vít 1285 mm; dài máy 9,46 m; barrel 33,7D |
| B | dài barrel = 34D = 5270 mm | 45,6 | lệch A +0,8 % (không độc lập với A) |
| C | bước p = 6D = 930 mm | 67,8 | trục vít 1,93 m, dài máy 14,2 m nhưng barrel 51D; đỉnh vent 3,2 m → **loại** |
| D | trục vít cao 1100 mm (mức thường gặp) | 38,7 | bước barrel thành 531 mm = 3,4D (không phải module chuẩn), barrel 29D → ít khả năng |
| E | trục vít cao 1200 mm | 42,2 | bước = 3,7D, barrel 31,5D |

- **Đề xuất: 45,2 mm/pt.** Khoảng tin cậy hợp lý là **41,5–46,5 mm/pt (−8 %/+3 %)**. Cận dưới ứng với trường hợp hình vẽ ép chiều dài barrel hoặc trục vít thực chỉ khoảng 1150–1200 mm. Cận trên ứng với trường hợp barrel đúng 34D cộng thêm adapter.
- Trục vít 1285 mm cao hơn mức thường gặp khoảng 1100 mm. Với máy Ø155 có hộp số lớn thì 1,2–1,3 m vẫn hợp lý, nhưng đây là chỗ cần đối chiếu với số liệu web nếu có.
- Hai thông số chưa kiểm chứng trong catalogue: **D = 155 mm**, catalogue không ghi đường kính, BRIEF yêu cầu dùng 155; và **module 4D/6D**, catalogue chỉ nói barrel có L/D 4 hoặc 6. Nếu D thực khác thì mọi số mm dưới đây đổi theo tỉ lệ D/155.

## 4. Kích thước suy ra cho ZE 155 UT (mm, thang 45,2 mm/pt)

Toạ độ theo BRIEF: X = 0 tại mối nối barrel/gearbox-lantern, +X về phía die. Z = 0 là sàn. Sai số cho mỗi số = sai số thang (−8 %/+3 %) cộng sai số đọc ±0,1 pt (±5 mm). Riêng các mục ghi "diễn giải" còn phụ thuộc cách hiểu chi tiết.

| Kích thước | Giá trị (mm) | Khoảng (mm) | Cách suy ra |
|---|---|---|---|
| **Khung đế dài × cao** | **9460 × 600** (đỉnh khung Z = 660) | 8700–9750 × 550–620 | 209,32 × 13,29 pt; chân 57 mm |
| Khung đế: X từ +5390 (đầu ra) đến −4070 (đầu motor) | | ±8 % | x = 329,87 / 539,19 |
| Khung đế đoạn trái / phải | 5090 / 4340 | ±8 % | mối nối tại x = 442,4 (X ≈ +300) |
| Dầm trên / hộp tủ dưới (cao) | 210 / 390 | ±8 % | 4,69 / 8,60 pt |
| **Chiều dài tổng không tính melt line** | **9460** (khung đế/máy) | 8700–9750 | đầu ra khung đế → đầu motor; motor kết thúc tại X ≈ −4005 |
| Chiều dài tổng tính cả khối cao cuối máy | 9935 | 9140–10230 | 219,8 pt |
| Dài barrel (mặt đầu ra → mối nối) | 5230 (= 33,7D) | | 115,68 pt; mặt đầu ra barrel X ≈ +5230 |
| **Cao trục vít** | **1285** | 1180–1325 | tâm barrel lộ |
| Barrel: cao thân / mặt bích-clamp | 477 / 571 | ±8 % | thân trụ ≈ Ø480, mặt bích/clamp ≈ Ø570 (diễn giải: UT tròn) |
| C-clamp rộng | 150 | ±8 % | 3,33 pt |
| Bước barrel (module) | 620 (giả thiết 4D) | – | mốc A |
| **Vỏ che barrel: cao trên sàn / cao bản thân** | **1636 / 978** | 1505–1685 | đỉnh 471,03; đáy = đỉnh khung đế |
| Vỏ che: tổng dài, X | 3710, X +5230 → +1520 | ±8 % | 6 tấm × 620 |
| Vent dome: rộng × cao trên vỏ che, đỉnh | 430 × 485, đỉnh Z 2115 (tai 2145) | ±8 % | trục X ≈ +3065 |
| Phễu: thân rộng, đỉnh, tâm | 240, Z 1820, X ≈ +235 | ±8 % | ống nạp nghiêng 45° về phía motor |
| Lantern: dài × cao (Z 918–1807) | 690 × 890 | ±8 % | X −40 → −730; cửa thăm 345 × 225 |
| **Hộp số: dài × cao** (Z 753–1789) | **1360 × 1040** | 1250–1400 × 955–1070 | X −830 → −2190; tâm trùng trục vít |
| Vỏ khớp nối: dài × cao | 580 × 865 | ±8 % | X −2225 → −2805 (diễn giải) |
| **Motor chính: dài × cao thân** (Z 782–1630) | **1140 × 850** | 1045–1170 × 780–875 | X −2840 → −3975; hộp trên nóc 605 × 295, đỉnh Z 1807 (diễn giải) |
| Cụm motor + khớp nối (tổng) | 1780 dài | ±8 % | x 498,3–537,7 |
| Đế motor/cụm dầu | Z 687–782 | | ray trượt nhiều lớp Z 445–670 dưới cụm dẫn động |
| Khối cao cuối máy | 430 rộng × 1380 cao, Z 316–1695, X −4115 → −4545 | ±8 % | không chạm sàn |
| Chiều cao lớn nhất (tai vent) | 2145 | 1975–2210 | |

Lưu ý cho người thiết kế (designer):
1. Vỏ che barrel trên hình là **dạng hộp đứng trên khung đế**, bao cả barrel lẫn khoảng dưới barrel. Barrel thật bên trong là trụ tròn có mặt bích/C-clamp, kê trên **gối đỡ đặt tại vị trí clamp** (thấy 2 gối, cách nhau 4p = 2480 mm).
2. Đoạn barrel ở vùng nạp liệu, khoảng X 0 → +1520, **không có vỏ che** (2D + 4D + feed). Dưới đoạn này là khoảng hở xuống tới đỉnh khung đế.
3. **Khối cao cuối máy** là chữ nhật trơn, không có chi tiết, đứng rời và đáy cách sàn khoảng 316 mm. Ứng viên theo mức khả năng: (a) tủ điện/biến tần (drive/switch cabinet) vẽ tượng trưng; (b) quạt làm mát cưỡng bức hoặc bộ trao đổi nhiệt gắn đuôi motor (forced-ventilation unit); (c) cột HMI hoặc tấm che. Catalogue không cho biết. Đề xuất: mô hình hoá như tủ điện đứng riêng đặt sau đuôi motor, hoặc bỏ qua, và ghi vào giả định.
4. Vỏ che C1 (đầu ra) có tấm vòm với **mặt bích tròn 10 bulông** vẽ chính diện, tâm ở cao độ trục vít (y = 478,5 pt). Đây có thể là mặt bích đầu barrel/adapter (barrel head flange), một cổng xả hoặc cảm biến lắp bên hông. Với T-die, chỗ này là điểm nối melt line, nên dựng adapter đồng trục tại X ≈ +5230.
5. Hộp số là khối trơn. Chi tiết (gân, móc cẩu, nắp thăm) lấy theo p19_3/p05_3. Motor có thể lấy màu xanh tím như p16_1 hoặc xám đen như p06; designer quyết định.

## 5. Slot die và trục cán láng (trang 24–25, sơ đồ, không theo tỉ lệ)

Toạ độ vector trang 24 (pt). Bản vẽ trải sang trang 25, vượt ra ngoài mép trang 24.
- **Melt line**: ống cam nằm ngang, tâm y ≈ 440 pt, nối mặt bích cuối extruder với die. Trên sơ đồ, melt line dài và thẳng, **đồng trục** với trục barrel.
- **Slot die 22** (nhìn cạnh): khối adapter x 568,2–577,4 (cao 433,2–448,0), **tấm mặt bích lớn** x 577,4–585,7 (cao 427,9–453,2, tức 25,3 pt), thân die **hình nêm** x 585,7–604,1, đáy nêm cao 15,4 pt thu nhọn về **môi die** (lip) tại (604,1; 440,2). Môi die nằm ngang, hướng theo dòng chảy.
- **Smoothing roll 23**: **3 trục đứng chồng nhau** Ø 20,8 pt, tâm x ≈ 608,7, y = 405,65 / 428,70 / 451,40 (bước 23 pt), đặt trên **khung đứng** (roll stand) ở phía sau trục (x 609 → 644, đỉnh y ≈ 386). Ba khối nhỏ trên mặt sau khung (x 644–652, mỗi trục một khối) có thể là xi lanh ép/cụm truyền động trục.
- **Cách bố trí:** môi die chĩa thẳng vào **khe giữa trục giữa và trục dưới** (nip y = 440,05 trùng lip y = 440,2). Tấm nhựa ôm nửa phải trục giữa đi lên, ôm trục trên phía trái và qua đỉnh, sang một con lăn nhỏ, rồi chạy trên **băng con lăn làm nguội** dài (cooling roller conveyor, x ≈ 644–743, hai ray y 397–404) tới cụm kéo **24**. Dưới băng con lăn có 3 tủ điện.
- Tỉ lệ sơ đồ (chỉ để tham khảo dáng): cao mặt bích die / Ø trục = 1,22; dài nêm die / Ø trục = 0,88; nip dưới cao khoảng 2,5 Ø trục so với sàn sơ đồ (y ≈ 492).
- Giả định cho bản vẽ (không có trong catalogue): sơ đồ cho thấy môi die, melt line và trục vít cùng một cao độ. Có thể đặt môi die gần Z ≈ 1285 mm (cao trục vít) với trục cán Ø khoảng 400–600 mm. Kích thước thật của die/trục cán phải lấy từ nguồn web hoặc giả định có ghi rõ.
- Crop: `pdf_crops/p24-25_line_layout_spread.png`, `pdf_crops/p24-25_slot_die_smoothing_roll_600dpi.png`.

## 6. Những điểm chưa chắc chắn
- Thang 45,2 mm/pt dựa trên giả thiết bước barrel = 4D và D = 155 mm. Sai số ước tính −8 %/+3 %.
- Silhouette là hình mẫu dùng chung cho ZE 155/180 (và có lẽ 230): số vỏ che, vị trí vent, bố trí dẫn động có thể không đúng với một máy ZE 155 cụ thể.
- Cách hiểu các khối "lantern / hộp số / vỏ khớp nối / motor" dựa trên mẫu ZE 130 cùng trang và ảnh cắt lớp trang 6. Khối hộp số (1360 mm) và motor (1140 mm) cũng có thể bị hoán đổi vai trò, dù ít khả năng.
- Khối cao cuối máy và mặt bích tròn ở vỏ che C1 chưa xác định được.
- Màu sắc lấy mẫu từ ảnh in (UTX/Basic có tủ xanh `#0092D2`, khung xám sáng). Máy cỡ lớn trên p16_1 có khung xám đậm, dẫn động xanh tím. Catalogue không cho biết màu của chính ZE 155 UT.
