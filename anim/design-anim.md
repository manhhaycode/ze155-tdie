# Thiết kế animation và mặt cắt – dây chuyền tấm PET ZE 155 + khuôn chữ T

Brief để người dùng duyệt trước khi dựng. Bản 2, đã sửa theo review độc lập `anim/review-anim-01.md`. Mới là thiết kế: chưa dựng hay sửa gì trong Blender.

**Tóm tắt**
- **16 shot, 3 phút 31 giây** (5 275 khung, 1920 × 1080, 25 khung/giây). Thêm **7 ảnh tĩnh mặt cắt** 2400 × 1350.
- **Render:**
  - qua MCP theo từng đợt, có thể chạy tiếp nếu bị ngắt, mất ≈ **3–4,5 giờ**; trong thời gian đó Blender của người dùng bận;
  - hoặc chạy một tiến trình Blender nền riêng (Q7).
- **Bên trong:** dựng thêm **33 hạng mục** (vít, lỗ số 8, đĩa lọc, bánh răng bơm, rãnh khuôn, khối nhựa chảy…), khoảng **364 nghìn tam giác**, cộng khoảng 150 nghìn cho các bản cắt.
- **Đã duyệt:**
  - D1: dựng trong scene mới `ze155_anim`, giữ `ze155` sạch.
  - D2: dọn camera thừa là một bước của việc làm animation.
- **Cần duyệt: 7 quyết định Q1–Q7** (mục 11).
  - Q6 quyết định phim kể vòng điều khiển bơm theo cách nào. Cần trả lời trước khi dựng S10, S14–S16.

| Tệp trong `anim/` | Nội dung |
|---|---|
| `shots.json` | Mọi thông số cho builder:<br>• shot, khung hình, camera (m);<br>• **nhóm hiển thị và trạng thái cắt**;<br>• chuyển động, nhãn đã xếp giờ;<br>• kế hoạch render |
| `interior_parts.json` | 33 hạng mục bên trong; bảng 32 phần tử vít mỗi trục; công thức biên dạng tự làm sạch |
| `storyboard/S01…S16.png`, `contact.png`, `make_storyboard.py` | Mỗi shot một khung chú thích; tờ tổng hợp; script sinh storyboard |

> **Lưu ý cho người dùng: Blender đang mở `out/ze155.blend` và có thay đổi chưa lưu.**
> - **Không bấm Ctrl+S trong lúc builder làm việc, và cả sau đó nếu scene `ze155_anim` còn trong phiên.** Ctrl+S sẽ ghi scene anim và mọi dữ liệu `int_*`/`anim_*` vào `out/ze155.blend`, làm bẩn mô hình tĩnh đã chốt.
> - **Thay đổi chưa lưu nghĩa là gì:**
>   - Phiên đang mở khác bản trên đĩa (kiểm tra chỉ đọc: `is_dirty = True`, vẫn 610 vật thể, khung hiện tại 34). Không biết chính xác đã đổi gì.
>   - Scene anim lấy vật thể của `ze155` **từ bộ nhớ**, nên các thay đổi đó sẽ đi vào `out/ze155_anim.blend`. Bản `out/ze155.blend` trên đĩa không đổi.
> - **Nếu muốn bỏ các thay đổi đó**, người dùng tự chọn File → Revert **trước khi builder bắt đầu**. Builder không được phép revert.
> - **Khi xong việc**, có thể đóng Blender mà không lưu: animation đã nằm trong `out/ze155_anim.blend`.

## 1. Mục tiêu: người xem phải tự kiểm được gì

| # | Điều cốt lõi phải thấy được | Shot |
|---|---|---|
| 1 | Hai vít **quay cùng chiều (co-rotating)**, ăn khớp trong **lỗ hình số 8 (figure-8 bore)**. Đỉnh ren vét sườn ren trục kia: **tự làm sạch (self-wiping)** | S04, S05 |
| 2 | **Cấu hình vít theo chức năng:**<br>• vận chuyển → khối nhào (kneading block) làm chảy → nút nhựa (melt seal);<br>• lỗ chân không với độ điền thấp (vòm vẽ mờ);<br>• trộn → nút ren trái (left-handed) → chân không sâu;<br>• tăng áp | S04, S06–S08 |
| 3 | **PET không cần sấy**: ẩm được hút ở hai vùng chân không ngay khi nhựa vừa chảy. Không hút thì PET thủy phân, độ nhớt (IV) tụt | S03, S07 |
| 4 | **Cấp đói (starve-fed)**: máy trục vít đôi không tự hút đầy; cân hao hụt khối lượng (loss-in-weight, LIW) đưa liệu vào | S03 |
| 5 | **Bơm bánh răng (melt gear pump):**<br>• tốc độ bơm là **giá trị đặt**, quyết định lưu lượng ra khuôn; cùng tốc độ trục cán, nó quyết định chiều dày;<br>• **áp hút P3 chỉnh cân + vít theo tỉ lệ** (Q6a);<br>• áp lên ≈ 250 bar ổn định, không đập mạch | S10, S15 |
| 6 | **Lọc lưới quay (rotary screen changer)** đổi lưới không dừng dòng, có **xả ngược (backflush)** | S09 |
| 7 | **Khuôn móc áo (coat-hanger)** chia đều trên 2 400 mm. **Thanh chặn (choker bar)** chỉnh thô, **bu-lông nhiệt (thermal bolts)** chỉnh tinh môi mềm (flex lip) | S11, S12 |
| 8 | Màn nhựa nguội nhanh trên trục cán → **tấm vô định hình**. Đầu đo chiều dày đóng vòng về khuôn và tốc độ trục | S13, S15 |
| 9 | **Truyền động chia công suất**: 1 động cơ → khớp nối → hộp số → 2 trục ra | S02 |

## 2. Chuỗi công nghệ lõi, từ hạt tới tấm

Điểm vận hành mẫu: **3 500 kg/h** tổng, vít **300 v/ph**, tấm **0,8 mm**, rộng **2 100 mm** sau xén biên.
- Trên hình, **dấu \* = giả định** (không có nguồn công bố). Mỗi shot có chú thích chân hình "* = giả định".
- X tính bằng mm.

| Bước | Chuyện gì xảy ra | Bộ phận (X mm) | Giá trị chính | Nguồn |
|---|---|---|---|---|
| 1 Cấp liệu | Hạt rơi vào họng nạp, vít chỉ đầy một phần | cân BSP-150 → ống rơi → họng nạp B1 (160–520) | Cân chính ≈ 3 300\* + biên tấm ≈ 160\* + phụ gia ≈ 40\* = 3 500 kg/h; ẩm 0,2–0,4 %\* → 7–14 kg/h nước | c069; design §7 |
| 2 Vận chuyển rắn | Rãnh sâu bước 1,5D nhận hạt; biên tấm nghiền vào qua side feeder (B2) | phần tử 1–6 (0–1 521) | B1 áo nước ≈ 50 °C\*; B2 260 °C\*; độ điền ≈ 30 %\* | giả định |
| 3 Nóng chảy | Khối nhào thuận 45°/5 ép, cắt; năng lượng chủ yếu từ trục vít | phần tử 7–8 (1 521–1 859) | năng lượng riêng 0,20–0,25 kWh/kg\* → ≈ 800 kW\* | design §3.1 |
| 4 Nút 1 + chân không 1 | KB 90° + ren trái tạo nút đầy; sau nút độ điền thấp; phần lớn hơi nước thoát ở đây | phần tử 9–10 (1 859–1 986); lỗ 1 990–2 310 | ≈ 50 mbar\*; B3 275 °C\* | design §1, §7 |
| 5 Trộn + nút 2 | Khối nhào trộn đồng nhất; ren trái cuối B4 đẩy ngược, đầy 100 % | phần tử 15–17 (2 831–3 338); LH 20 (3 634–3 718) | B4 270 °C\* | design §1 |
| 6 Chân không sâu | Điền thấp, mặt nhựa liên tục làm mới; ẩm và acetaldehyde → bình tách ngưng → Roots + bơm khô | lỗ B5 (3 860–4 380) | 5–20 mbar\*; ẩm → < 50 ppm\*; IV 0,80 → ≥ 0,77 dl/g\* | design §7; c062 (tin cậy thấp); Gneuss: 25–40 mbar đủ với ẩm 1 % trên máy MRS |
| 7 Tăng áp | Bước 1D → 0,75D, 2–3D cuối đầy 100 %; số 8 → tròn Ø120; van khởi động XẢ/CHẠY | B6, đầu xi lanh, van | P1 ≈ 100 bar\*, nhựa ≈ 285 °C\*; ngắt 350 bar, đĩa nổ 350 bar | design §1 |
| 8 Lọc | Đĩa lưới quay từng bước, 5 lưới trong dòng; lưới bẩn được xả ngược | RSFgenius 200 (6 596–7 301) | 970 cm²; lưới 60 µm\*; P2 ≈ 95\*, Δp ≈ 45 bar\* | c050; Δp là giả định (c052 chỉ là cơ sở tính năng suất: 40 bar ở 1 000 Pa·s) |
| 9 Bơm | **Tốc độ đặt** → lưu lượng cố định; nhựa đi vòng ngoài trong rãnh răng | Maag GU 100/125 (7 476–7 926) | 764 cm³/vòng, ≈ 69 v/ph\*; P3 = 50\* → P4 ≈ 250 bar\*; ngắt 330 bar | c047, c049; design §1 |
| 10 Ống + trộn tĩnh | Giữ nhiệt, đồng nhất | 8 076–8 926 | 275 °C\*; P5 ≈ 200 bar\* | giả định |
| 11 Khuôn | Cửa vào → móc áo → tiền môi (preland) → thanh chặn → môi | 9 126–9 576 | 270–280 °C\*; khe môi 1,0 mm\* (chỉnh 0,5–2); bu-lông nhiệt hành trình 0,3 mm = ±0,15 mm | c053–c056 |
| 12 Cụm cán | Màn nhựa qua khe gió 200 mm vào khe trục giữa–dưới; nguội dưới Tg ≈ 75 °C khi ôm trục giữa | trục Ø800, X 9 776 | dưới ≈ 60, giữa ≈ 55, trên ≈ 45 °C\*; ≈ 10 v/ph | c046; sáng chế tấm PET vô định hình (27–80 °C) |
| 13 Tấm | Kéo giãn ≈ 1,2; đo chiều dày quét ngang; xén biên ≈ 4,5 % về side feeder | băng tải X 11 750–12 650 | 0,8 × 2 100 mm\*, ≈ 25 m/min | tính ở dưới |

**Cân bằng khối lượng (kiểm được):**
- **Ra môi:** ρ nóng chảy ≈ 1,17 kg/L\*, nên 3 500 kg/h ≈ 2,99 m³/h. Qua khe 2,4 m × 1,0 mm cho **20,8 m/min**.
- **Trên trục cán:** tấm 2,2 m (co hẹp\*) × 0,8 mm, ρ rắn 1,335 → **24,8 m/min**, kéo giãn 1,19.
- **Trục cán:** 9,9 v/ph.
- **Giới hạn cụm cán:** 3 500 / 2,1 = 1 670 kg/h·m, dưới mức 1 800 của c046.
- **Mô-men:** 800 kW ở 300 v/ph cho ≈ 12,7 kNm mỗi trục, tức 36 % của 35 kNm.
- **Tấm thành phẩm:** ≈ 3 340 kg/h sau xén biên.

**Điểm riêng của PET và cách điều khiển:**
- **Vì sao phải khử ẩm:** ẩm làm PET **thủy phân (hydrolysis)** ở nhiệt độ chảy, cắt mạch, làm tụt IV. Rút phần lớn ẩm ngay sau khi chảy (vùng 1), rút nốt ở vùng 2 (Gneuss/Plastech).
- **Vì sao cần nút nhựa:** lỗ thoát khí chỉ làm việc khi phía trước có nút đầy và dưới lỗ độ điền thấp (Plastics Technology).
- **Điều khiển (Q6a, kiểu thường dùng cho dây chuyền tấm, Leistritz/PlasticsToday):**
  - tốc độ bơm bánh răng là **giá trị đặt chủ**, giữ lưu lượng thể tích ra khuôn không đổi;
  - PLC **chỉnh tốc độ cân LIW và tốc độ vít theo tỉ lệ** để giữ áp hút P3 = 50 bar;
  - chiều dày trung bình do **tốc độ bơm + tốc độ trục cán** quyết định;
  - đầu đo chỉnh tốc độ trục (chiều dày trung bình) và 94 bu-lông nhiệt (profin ngang).
- **design.md (s_20)** chọn cách ngược lại (Q6b): P3 chỉnh tốc độ bơm, cân đặt lưu lượng. Đây là cách hay dùng cho compounding/tạo hạt. Mỗi lần cân nạp lại hay có dao động áp, lưu lượng ra khuôn đổi theo, sinh dao động chiều dày theo chiều máy (MD).

**Logic cấu hình vít** (bảng đầy đủ: `interior_parts.json`, 32 phần tử, tổng 34D):

| Vùng | X (mm) | Phần tử | Vì sao |
|---|---|---|---|
| Nhận hạt | 0–1 521 | 6 × SE 1,5D | thể tích tự do lớn, nhận hạt và liệu side feeder |
| Nóng chảy | 1 521–1 859 | 2 × KB 45°/5/1D | ép, cắt, vẫn đẩy tới |
| Nút 1 | 1 859–1 986 | KB 90°/5/0,5D + LH 0,5D dài 0,25D | đầy 100 %, kín trước lỗ 1 (1 990) |
| Thoát khí 1 | 1 986–2 493 | 2 × SE 1,5D | độ điền thấp |
| Vận chuyển | 2 493–2 831 | 2 × SE 1D | |
| Trộn | 2 831–3 338 | 2 × KB 45°/5 + KB 90°/5 | đồng nhất nhiệt |
| Nút 2 | 3 338–3 718 | SE 1D, SE 1D × 0,75, LH 0,5D | kết thúc đúng mặt nối B4/B5, trước lỗ 2 (3 860) |
| Thoát khí 2 | 3 718–4 479 | 3 × SE 1,5D | dưới lỗ 3 860–4 380 |
| Tăng áp | 4 479–5 746 | 4 × SE 1D, 4 × SE 0,75D, đầu vít 0,5D | bước nhỏ dần, đầy 100 % ở cuối |

## 3. Danh sách shot

**Cấu trúc:**
- I. Toàn cảnh (S01)
- II. Từ hạt tới nhựa chảy (S02–S08)
- III. Lọc, bơm, khuôn, tấm (S09–S13)
- IV. Cả hệ thống (S14–S16)

Toạ độ camera, trạng thái cắt và giờ nhãn ghi trong `shots.json`.

| Shot | Thời lượng | Dạy gì | Camera (m) | Chuyển động | Trạng thái |
|---|---|---|---|---|---|
| S01 | 12 s | cả dây chuyền + trục quy trình | bay dọc (−9, 9, 6,5) → (13,5, 7,5, 3,8) | vạch sáng dọc đường vật liệu; tấm và trục tốc độ thực | FULL |
| S02 | 10 s | 1 động cơ → 2 trục | (−3,6, 4,2, 2,4) → (−0,4, 3,0, 1,9) | khớp nối, sơ đồ bánh răng, trục then hoa quay (chậm 20×) | GHOST_DRIVE |
| S03 | 14 s | cấp liệu, cấp đói | **2 camera:**<br>• a: trên sàn (1,9, 4,6, 5,4) → (1,5, 3,4, 5,6);<br>• cắt cảnh sang b: dưới sàn (2,2, 2,6, 2,3) → (1,3, 2,0, 1,95) | hạt rơi; hạt trong rãnh vít đi 63 mm/s (= bước × vòng/s) | FULL → CUT_FEED |
| S04 | 18 s | vận chuyển → chảy → nút → chân không 1 | dọc B1 → B3 nhìn chéo xuống | nửa trên nhấc lên; vít quay; hạt chuyển màu thành nhựa; bọt dày ở lỗ 1 | CUT_Z_BARREL: **sàn thao tác ẩn**; vòm vẽ mờ + dải tím cửa sổ lỗ |
| S05 | 9 s | lỗ số 8, tự làm sạch | (3,3, 0,75, 1,62) → (3,05, 0,42, 1,45) | hai biên dạng quay cùng chiều | CUT_X2450: **vít cắt sẵn tại mặt cắt**, phần sau ẩn |
| S06 | 11 s | trộn + nút ren trái | dọc B4 → B5 | vít quay; mũi tên ngược ở LH | CUT_Z_BARREL |
| S07 | 11 s | chân không sâu, vì sao không cần sấy | (4,95, 1,2, 2,15) → (4,75, 0,85, 1,95) | bọt nhỏ, thưa hơn vùng 1; hơi vào DN150 | CUT_X4120 (vít cắt sẵn) |
| S08 | 11 s | tăng áp, đầu, van khởi động | dọc B6 → van | độ điền lên 100 %; chốt van −0,2 → 0 m (XẢ → CHẠY) | CUT_Z_BARREL |
| S09 | 12 s | lọc liên tục, xả ngược | (6,05, 2,3, 1,95) → (6,4, 1,7, 1,75) | đĩa +30° mỗi 3 s; lưới bẩn dần; piston xả ngược | GHOST_SC |
| S10 | 12 s | **bơm đặt lưu lượng** | (7,7, 1,75, 1,5) → (7,72, 1,1, 1,3) | bánh trên +, dưới − (chậm 4×) | CUT_PUMP |
| S11 | 14 s | phân phối móc áo | nhìn xuống mặt phân khuôn rồi xoay sang +Y | nửa trên + thanh chặn nhấc lên; nhựa lan từ cửa vào; hình chèn 2D (Q2) | CUT_DIE_PLAN |
| S12 | 13 s | chỉnh thô, chỉnh tinh | đẩy tới môi, ống kính 45 → 80 mm | khe môi và hành trình **cùng vẽ ×10**; bu-lông nhiệt đỏ dần; đồng hồ số giá trị thật | CUT_DIE_AA |
| S13 | 12 s | tạo tấm, đo chiều dày | khe trục → băng tải (13,4, 4,3, 3,1) | trục và tấm tốc độ thực; tấm trong dần từ khe trục | FULL |
| S14 | 16 s | năng lượng, nhiệt + nước, vật liệu + chân không | quỹ đạo cao | bật 3 lớp, mỗi lớp ≈ 5 s | FLOWS |
| S15 | 26 s | **7 vòng điều khiển** | 3 vùng: cấp liệu–bơm, khuôn–trục–đầu đo, đường chảy–xi lanh | mỗi vòng ≥ 3 s: cung nét đứt + sơ đồ khối 2D tô sáng | FLOWS |
| S16 | 10 s | 3 điểm lõi | trực giao mặt đứng | tấm chạy | FULL |

**Tốc độ hiển thị (badge góc hình):**
- **Vít:** thực 300 v/ph tức 72° mỗi khung, sẽ nhòe và có hiệu ứng bánh xe quay ngược. Hiển thị **chậm 20×** (15 v/ph).
- **Bơm:** chậm 4×.
- **Trục cán và tấm:** tốc độ thực.
- **Đĩa lọc:** tua nhanh.
- **Dòng nhựa:** "minh họa".

**Nhịp đọc:**
- Mỗi nhãn ở trên màn hình ≥ max(3 s, 0,4 s mỗi từ).
- Tối đa 4 nhãn cùng lúc; S15 tối đa 2.
- Nhãn cuối của shot giữ ≥ 3 s.
- `shots.json` đã xếp giờ và kiểm tự động các quy tắc này.

## 4. Mặt cắt

| Trạng thái | Mặt phẳng (m) / hộp cắt | Thay bằng gì | Shot |
|---|---|---|---|
| CUT_FEED | Y = 0, bỏ +Y; hộp X −1…0,75, Z 1,45–3 | cột cấp liệu rỗng cắt đôi | S03b |
| CUT_Z_BARREL | Z = 1,2, bỏ trên; **một hộp X −0,05…6,5, Y ±0,5** cho cả S04/S06/S08 | xi lanh rỗng `_lo`, đầu + van `_lo`, khối điền `_lo`; vòm mờ + dải cửa sổ tím | S04, S06, S08 |
| CUT_X2450 | X = 2,45, bỏ +X; hộp tới X 3,8 | B3 cắt ngang; phần tử 12 cắt sẵn + nắp biên dạng; phần tử 13–32 ẩn | S05, ST2 |
| CUT_X4120 | X = 4,12, bỏ +X; hộp tới X 5,0 | B5 + vòm 2 cắt ngang; phần tử 22 cắt sẵn; 23–32 ẩn | S07, ST3 |
| CUT_PUMP | Y = 0, bỏ +Y; hộp X 7,25–8,15 | thân bơm rỗng + 2 bánh răng | S10, ST7 |
| CUT_DIE_PLAN | Z = 1,2 (mặt phân khuôn) | nửa dưới có rãnh móc áo; nửa trên và thanh chặn nhấc lên | S11, ST5 |
| CUT_DIE_AA | Y = 0, bỏ +Y; hộp X 8,4–10,4, Y 0–2,1, Z 0–2,9 | khuôn A-A; trục cán, xe khuôn, tấm cắt đôi | S12, ST4 |
| GHOST_DRIVE / GHOST_SC | không cắt | vỏ trong suốt α 0,12–0,15 có viền | S02, S09, ST6 |

**Quy tắc cắt (cho mọi trạng thái):** xét các vật thuộc nhóm bị ẩn có tâm bao nằm trong hộp cắt.
- Vật cắt ngang mặt phẳng: tạo bản sao cắt đôi `_keep`/`_rm`.
  - Curve được đổi sang mesh trước; modifier được áp; mặt cắt được lấp nắp.
- Vật nằm hẳn bên giữ: bản sao nguyên `_keep`.
- Vật nằm hẳn bên bỏ: chỉ có bản `_rm` dùng cho peel.
- Vật có tâm ngoài hộp: bản sao nguyên.
- Kết quả: ẩn một nhóm không bao giờ làm mất phần phải còn thấy. Thêm vào đó:
  - ống chân không bị ẩn trong các shot cắt Z;
  - vít không bao giờ thò qua mặt cắt ngang.

**Cách cắt đã chọn: bản sao cắt sẵn (bisect + fill) + peel.**
- **Peel:** nửa bỏ tách ra, nhấc 0,9–2,2 m, mờ dần trong 1,5–2,5 s.
- **Vì sao không dùng boolean động:** ≈ 100 vật thể phải tính lại mỗi khung; vỏ tôn hở mép làm boolean hỏng.
- **Vì sao không cắt bằng shader:** nắp chỉ đúng với lưới kín, và phải sửa vật liệu dùng chung với `ze155`.
- **Màu nắp:** thép đỏ gạch có gạch chéo; cách nhiệt be; nhựa hổ phách.

**Ảnh tĩnh:** mỗi ảnh có trạng thái riêng, không lấy theo khung của timeline.

| Ảnh | Nội dung |
|---|---|
| ST1 | toàn tuyến cắt Z 1 200; bộ lọc dùng vỏ trong suốt, đĩa không bị cắt |
| ST2 | lỗ số 8 |
| ST3 | vùng chân không 2 |
| ST4 | khuôn A-A với khe thật 1,0 mm |
| ST5 | rãnh móc áo |
| ST6 | đĩa lọc |
| ST7 | bơm bánh răng |

## 5. Tương tác hệ thống (S14 + S15)

**S14 (16 s), mỗi lớp ≈ 5 s:**
1. **Năng lượng:** trung thế → tủ biến tần → động cơ; hạ thế → tủ điều khiển + nhiệt. Ống sáng đỏ chấm gạch, sinh từ 13 mối nối `power` trong `parts.json`.
2. **Nhiệt + nước:** 20 vùng nhiệt, vỏ sáng theo nhiệt độ đặt; nước cấp liền / hồi đứt, từ 11 mối nối `water`.
3. **Vật liệu + nhựa + chân không:** hạt nâu → nhựa đỏ → tấm; xung tím ở 4 mối nối `vacuum`.

Đèn dịu còn 45 % để các dòng phát sáng nổi lên.

**S15 (26 s):** 7 vòng, mỗi vòng ≥ 3 s. Cung nét đứt trên mô hình kèm sơ đồ khối 2D ở ⅓ phải màn hình, tô sáng vòng đang nói. Camera đẩy qua 3 vùng.

| # | Vòng (Q6a) | Đo | Tác động |
|---|---|---|---|
| 1 | Bơm bánh răng | tốc độ đặt (chủ) | lưu lượng thể tích ra khuôn cố định |
| 2 | PIC-P3 | áp hút bơm 50 bar\* | chỉnh **cân LIW + tốc độ vít theo tỉ lệ** |
| 3 | Chiều dày trung bình | đầu đo quét | tốc độ trục cán (hoặc chỉnh nhẹ tốc độ bơm) |
| 4 | Profin ngang | đầu đo quét | 94 bu-lông nhiệt (c054) |
| 5 | PDI P2/P3 | Δp qua lưới | nhịp quay đĩa lọc, xả ngược |
| 6 | TIC × 20 | cặp nhiệt | băng nhiệt / van điện từ nước |
| 7 | Liên động | P1 HH 350, P4 HH 330 bar, đĩa nổ | dừng truyền động (STO), dừng bơm, dừng cân |

Nếu Q6 = b, nhãn (1) và (2) đổi thành:
- (1) "Cân đặt lưu lượng 3 500 kg/h";
- (2) "PIC-P3 → tốc độ bơm".

Các nội dung thay thế đã ghi sẵn trong `shots.json` ở khoá `alt_if_Q6b`.

Màu theo tờ 07:
- nhựa đỏ, hạt nâu;
- nước xanh, chân không tím;
- dầu cam, thuỷ lực xanh lá;
- khí lam nhạt;
- điện đỏ gạch chấm, tín hiệu xám đứt.

## 6. Hình học bên trong cần dựng thêm

| Nhóm | Hạng mục | Mức chi tiết | Tam giác |
|---|---|---|---|
| Vít | 2 trục quay (empty); 32 phần tử mỗi trục (10 lưới duy nhất, 64 bản sao liên kết); trục then hoa; 4 nắp biên dạng; **phần tử 12 và 22 cắt sẵn** | biên dạng Erdmenger 2 đầu ren đúng hình học (a = 142, Ro = 83,75, góc đỉnh 25,9°); khối nhào 5 đĩa; vít B lệch 90° | 200 k (thực tế có thể ≈ 260 k) |
| Xi lanh | 6 thân rỗng, 2 vòm rỗng, cột cấp liệu rỗng; **vòm mờ + dải cửa sổ** | lỗ số 8, 8 lỗ nước Ø18, các cửa | 43 k |
| Đường chảy | đầu xi lanh rỗng; thân van + chốt trượt; các bích (**Ø100 tới khuôn**); ống + trộn tĩnh | đơn giản | 21 k |
| Bộ lọc | đĩa Ø930 với 12 lỗ lưới, lưới, rãnh thận, piston xả ngược | trục đĩa song song dòng chảy | 20 k |
| Bơm | 2 bánh răng 16 răng, m 7,8, rộng 125; thân rỗng | | 15 k |
| Khuôn | nửa dưới có rãnh móc áo (tâm X 9 172, vách 10 mm); 2 nửa A-A với shape key `gap_x10` và `lip_push`; thanh chặn | theo tờ 05 | 15 k |
| Khối nhựa | khối điền từng vùng, có biến thể `_lo` và cắt ngang | trong mờ | 35 k |
| Khác | sơ đồ bánh răng hộp số; đầu đo chiều dày; vạch trên đầu trục cán; bản sao tách (`anim_split_*`) | | 15 k |
| **Tổng** | **33 hạng mục** | | **≈ 364 k** (+ ≈ 150 k bản cắt; cả scene ≈ 1,8 M) |

**Đơn giản hóa:**
- Nhựa trong rãnh là khối mờ có vân trôi, không quay theo vít; riêng túi răng bơm thì quay theo bánh răng.
- Hộp số là sơ đồ nguyên lý.
- Không dựng: vít side feeder, ruột cân, ruột bình tách. Trục cán vẽ đặc, chỉ có vạch quay.

## 7. Kỹ thuật trong Blender 5.2 (EEVEE)

**Quay:**
- Mỗi trục quay có một empty ở đúng tâm; driver dùng biểu thức đơn giản (`frame`, biến), lấy tốc độ từ empty `anim_ctrl`.
  - Ví dụ vít: `rotation_euler[0] = −2π·(300/20/60)·frame/25`, cùng dấu cho hai trục.
- Quy ước chiều:
  - phần tử RH dựng sao cho góc biên dạng tăng theo X; gân ren trông như chạy về +X, đoạn LH chạy về −X;
  - bơm: trên +, dưới −;
  - trục cán: dưới +, giữa −, trên +.
- Vật của `ze155` có gốc ở (0, 0, 0): chỉ quay bản sao anim hoặc vật mới. **Không đặt cha, không quay, không đổi `hide_render` của vật `ze155`.**

**Dòng vật liệu:**
- **Hạt (geometry nodes):** lặp theo `fract(t)`. Trong rãnh vít, hạt đi dọc trục với tốc độ = bước × vòng/s hiển thị (1,5D: 63 mm/s, 1D: 42 mm/s), nên không xuyên qua gân ren.
- **Khối điền:**
  - color ramp theo X: trắng hạt (X < 1,52) → loang → hổ phách (X > 1,90);
  - render method Blended;
  - vân trôi cùng tốc độ trên.
- **Bọt:** vùng 1 dày và nhanh (0,25 m/s), vì đây là nơi rút phần lớn nước; vùng 2 nhỏ và thưa (0,15 m/s).
- **Màn nhựa:** giữ màu hổ phách qua khe gió.
- **Tấm:** chuyển dần từ hổ phách sang trong, bắt đầu ở khe trục và kéo dài qua 90° đầu của đoạn ôm trục giữa.
- **Khe môi S12:**
  - khe thật 1,0 mm, hành trình bu-lông nhiệt ±0,15 mm (0,3 mm tổng, c054);
  - trong shot, khe và hành trình **cùng phóng đại ×10**: khe vẽ 10 mm, môi hạ 1,5 mm, nên không bao giờ đóng khe;
  - badge "Khe môi và hành trình vẽ phóng đại ×10" và đồng hồ số hiện giá trị thật 1,00 ↔ 0,85–1,15 mm;
  - ST4 dùng khe thật.

**Nhãn và HUD làm ở hậu kỳ:**
- Blender xuất toạ độ 2D từng khung của điểm neo (`world_to_camera_view`).
- Pillow vẽ:
  - khung chú thích;
  - thanh tiêu đề;
  - badge tốc độ;
  - dải "cấu hình vít + độ điền + áp suất + cửa sổ lỗ chân không";
  - sơ đồ khối S15;
  - chân hình "* = giả định".
- Font Arial, đủ dấu tiếng Việt. Ghép bằng ffmpeg (`uv run --with imageio-ffmpeg`).
- Sửa chữ không phải render lại 3D.

**Đầu ra:**
- **Khung render:** PNG 1920 × 1080 trong `anim/render/frames/`.
- **Overlay:** `anim/render/overlay/`.
- **Video:** MP4 H.264, CRF 18, 25 khung/s, tại `anim/render/ze155_anim.mp4`.
- **Ảnh tĩnh:** `anim/render/stills/`.

**Render:**

| Bước | Cách chạy | Thời gian |
|---|---|---|
| Bản xem trước cho reviewer | 960 × 540, 8 sample | ≈ 35 phút |
| Bản cuối, mặc định qua MCP | Mỗi lần gọi `execute_blender_code` render ≤ 40 khung (≈ 2 phút) và bỏ qua khung đã có PNG, nên chạy tiếp được sau khi bị ngắt. Ghi tiến độ vào `anim/log.md`. 32 sample, tắt raytracing trừ S01/S12/S13; ≈ 2–3 s/khung (suy từ ảnh cuối hiện có: 12–16 s ở 2400 × 1350, 96 sample) | ≈ 130 lần gọi, ≈ 3–4,5 giờ, **Blender của người dùng bận suốt thời gian này** |
| Bản cuối, nếu duyệt Q7 | `blender -b out/ze155_anim.blend --python anim/render_frames.py -- <đầu> <cuối>`: tiến trình riêng, cùng quy tắc bỏ qua khung đã có, chia 2–4 đợt; thử 1 khung trước (EEVEE chạy nền trên macOS) | nhanh hơn một chút, không chặn Blender đang mở |

## 8. Tổ chức scene, lưu file, dọn camera

**Scene và lưu:**
- **Tạo `ze155_anim` ngay trong phiên đang mở** (`bpy.data.scenes.new`).
- **Không bao giờ ghi đè `out/ze155.blend`:** không `Z.save_blend()`, không `save_mainfile`, không Ctrl+S.
- **Lưu riêng:** `bpy.data.libraries.write('out/ze155_anim.blend', {bpy.data.scenes['ze155_anim']}, fake_user=True)`. File này chỉ chứa scene anim cùng các vật, lưới, vật liệu nó dùng; scene `ze155` không đi theo.
- **Kiểm bản lưu:** đọc lại bằng `bpy.data.libraries.load('out/ze155_anim.blend')`, liệt kê scene, collection, số vật. Nếu đọc lại báo lỗi, chép sang bản tạm `anim/tmp/verify.blend` rồi đọc bản tạm.

**Nhóm hiển thị:**
- `hide_render` của vật dùng chung mọi scene, nên chỉ được key ẩn/hiện của **collection** riêng của anim (nội suy hằng).
- Vật `ze155` được liên kết vào đúng một nhóm `ax_*`. Danh sách thành viên đầy đủ ở `shots.json` → `meta.visibility_groups`; builder in danh sách đã khớp tên vào log.
- Vật dùng ở nhiều nơi được tách thành bản sao `anim_split_*`, mỗi bản về nhóm của bộ phận nó gắn vào:
  - `melt_heater_bands` tách thành 6 băng;
  - `die_body_bolts` và `die_heater_boxes` tách thành phần trên / phần dưới.

| Nhóm (× = ẩn, thay bằng bản sao theo quy tắc cắt) | S02 | S03b | S04/06/08 | S05 | S07 | S09 | S10 | S11 | S12 | ST1 |
|---|---|---|---|---|---|---|---|---|---|---|
| `ax_drive_housing`, `ax_drive_rot` | × | | | | | | | | | |
| `ax_feed_platform` | | | × | | | | | | | × |
| `ax_feed_column` | | × | × | | | | | | | × |
| `ax_barrel_shell` | | | × | × | × | | | | | × |
| `ax_vents` (vòm, van, ống chân không) | | | × | × | × | | | | | × |
| `ax_head_valve`, `ax_melt_cables` | | | × | | | | | | | × |
| `ax_sc` | | | | | | × | | | | × |
| `ax_pump` | | | | | | | × | | | × |
| `ax_pipe` | | | | | | | | × | × | × |
| `ax_die_upper`, `ax_die_lower` | | | | | | | | × | × | × |
| `ax_die_cart`, `ax_rolls` | | | | | | | | | × | |
| `ax_always_replaced` (vít cũ, tấm, màn nhựa, băng nhiệt, bu-lông khuôn, hộp nhiệt khuôn) | × | × | × | × | × | × | × | × | × | × |

**Collection riêng của anim:**
- `anim_int_*`;
- `anim_cut_*`;
- `anim_fx_*`;
- `anim_rig`: 24 camera (17 camera shot, vì S03 có 2 camera, cộng 7 camera ST1…ST7), bản sao 5 đèn, `anim_ctrl`.

Camera gắn vào marker ở khung đầu mỗi shot.

**Dọn camera (D2), bước C0: chỉ dọn trong scene anim, không xoá vật nào của `ze155`.**
- `ze155_anim` không liên kết `ze155_rig`, nên không có camera nào trong 73 camera cũ.
- Rig riêng chỉ gồm 24 camera cần cho phim.
- Đường viền của các đèn diện tích lớn được ẩn khỏi viewport bằng `hide_set` theo view layer; render không bị ảnh hưởng.
- Kết quả: viewport của scene anim sạch, và file `out/ze155_anim.blend` chỉ chứa camera cần dùng.
- Scene `ze155` giữ nguyên 73 camera; phiên không bao giờ lưu, nên `out/ze155.blend` không đổi.
- Nếu sau này người dùng muốn dọn chính `ze155`, đó là một bước riêng và lưu ra file mới.
- **Xong khi:**
  - scene anim có đúng 24 camera;
  - `ze155` vẫn còn 73 camera và 610 vật;
  - bản lưu đọc lại được.

## 9. Các phase dựng và vai trò

Mỗi vai là một agent riêng. Builder không tự nghiệm thu; reviewer chỉ ghi lỗi, không sửa.

| Phase | Vai | Việc | Xong khi | Công |
|---|---|---|---|---|
| 0 | người dùng | trả lời Q1–Q7; quyết định giữ hay revert thay đổi chưa lưu | | |
| C0 | builder dọn dẹp | tạo `ze155_anim`, rig sạch, nhóm `ax_*` (mục 8) | 24 camera, đếm vật đúng, bản lưu đọc lại được | 0,5 h |
| A1 | builder hình học | toàn bộ `int_*`; kiểm vít bằng số: không xuyên nhau ở 8 góc quay, khe tới lỗ ≥ 0,4 mm | bảng phần tử khớp từng X | 3 h |
| A2 | builder chuyển động | driver, hạt, khối điền, bọt, màn nhựa, tấm, dòng chảy S14, cung điều khiển S15, bản sao tách | tua được cả phim trong viewport | 3 h |
| A3 | builder mặt cắt + camera + nhãn | bản cắt và nắp, peel, 24 camera, xuất toạ độ neo, overlay, bản xem trước | video xem trước + 7 ảnh nháp | 3 h |
| R1 | reviewer độc lập | xem theo danh sách kiểm dưới | báo cáo | 1 h |
| F1 | fixer riêng | sửa Critical + Important | | 1–1,5 h |
| R | render | qua MCP theo đợt (hoặc tiến trình nền nếu duyệt Q7); ghép MP4 | MP4 + 7 PNG | 3–4,5 h máy |

**Danh sách kiểm của reviewer:**
1. Vít quay cùng chiều, cùng tốc độ. Gân RH chạy về +X, đoạn LH chạy về −X.
2. Hai vít không xuyên nhau. Vít B lệch 90°.
3. Thứ tự phần tử khớp bảng. Các nút nhựa kết thúc trước lỗ 1 990 và 3 860; dải cửa sổ tím đúng vị trí.
4. Độ điền: đầy ở khối nhào, nút và đầu vít; thấp dưới các lỗ.
5. Mặt cắt ngang: không phần vít nào thò qua mặt cắt.
6. Túi nhựa trong bơm đi vòng ngoài, không qua vùng ăn khớp.
7. Trục cán quay khớp hướng tấm, cùng tốc độ bề mặt.
8. Đĩa lọc: trục song song dòng; 5 lưới trong dòng; xả ngược ở vị trí vừa ra khỏi dòng.
9. Khe môi không bao giờ đóng; badge ×10 và đồng hồ số hiện đúng lúc.
10. Số liệu khớp mục 2. Giá trị giả định có dấu \*; mỗi shot có badge tốc độ.
11. Mặt cắt có nắp. Không có vật lơ lửng: ống chân không, thanh chặn, mép hộp cắt.
12. Camera không bị cột hay mép sàn che (S03, S04).
13. Chữ đủ dấu, đọc kịp.

## 10. Điểm lệch với design phát hiện khi thiết kế anim

Không sửa `design/`; anim xử lý như sau.

1. **Vòng điều khiển bơm:**
   - design s_20: P3 → tốc độ bơm, cân đặt lưu lượng.
   - Dây chuyền tấm thường làm ngược lại: bơm đặt lưu lượng, P3 chỉnh cân + vít.
   - Anim đề xuất cách thường dùng (Q6).
2. **Tốc độ bơm:**
   - design ghi ≈ 105 v/ph, theo bảng Maag ứng với ≈ 0,73 kg/L.
   - Với PET nóng chảy 1,17 kg/L và hiệu suất 0,95, ra ≈ **69 v/ph** (reviewer đã kiểm).
3. **Đĩa lọc:** trục đĩa phải song song dòng chảy (X), không ở mặt −Y. Tay quay −Y tác động lên vành đĩa qua cóc (giả định).
4. **Van khởi động:** design ghi "chốt xoay", nhưng xi lanh theo Y đẩy thẳng đầu chốt. Anim dùng chốt trượt 200 mm: XẢ ở Y −0,2, CHẠY ở Y 0.
5. **Khuôn:**
   - Thân sâu 450 mm và thanh chặn ở X 9 255 ép ống phân phối vào khoảng X 9 136–9 240.
   - Móc áo trong anim gần như chữ T: tâm X 9 172 → mép X 9 215; tiền môi 32 mm ở giữa, 11 mm ở mép.
   - Xem Q2.
6. **Lõi vít:**
   - design dùng D = 169 là đường kính vít và lõi 114,6. Đây cũng là một cặp tự làm sạch hợp lệ; **không phải design sai**.
   - Mô hình anim coi 169 là lỗ xi lanh, vít Ø167,5, lõi 116,5. Chênh 1,9 mm, không thấy được.
7. **Ranh giới phần tử vít** xếp lại theo bước 0,25D, lệch ≤ 70 mm so với `parts.json`.
8. **Khe gió 200 mm** lớn hơn mức thường gặp 50–150 mm (đã biết, design §9.5). Anim giữ nguyên.

## 11. Quyết định

**Đã duyệt:**
- **D1:** scene mới `ze155_anim`, giữ `ze155` sạch.
- **D2:** dọn camera là một bước của animation (C0). Đã chọn dọn chỉ trong scene anim; không xoá vật nào của `ze155`.

**Cần duyệt:**

| # | Câu hỏi | Đề xuất | Phương án khác |
|---|---|---|---|
| Q1 | Độ dài và render | **16 shot, 3:31, 1080p, ≈ 3–4,5 h render** | Bản ≈ 3:00: rút S01, S02, S03, S09, S13 mỗi shot 3 s, S14 còn 10 s, S15 còn 21 s, S16 còn 7 s. **Giữ S06**, vì đây là shot duy nhất cho nút ren trái trước chân không sâu |
| Q2 | Rãnh móc áo trong khuôn 450 mm | **Giữ khuôn hiện có. Móc áo gần chữ T (tiền môi 32 → 11 mm), thêm hình chèn 2D "móc áo phóng đại, không theo tỉ lệ" trong S11** | Làm khuôn sâu thêm ≈ 150 mm: phải sửa ngoại hình đã chốt, thêm ≈ 2 h |
| Q3 | Nhãn | **Hậu kỳ bằng Pillow, tiếng Việt, thuật ngữ Anh trong ngoặc cho ≈ 10 từ lõi** | Chữ 3D: sửa chữ phải render lại |
| Q4 | Thời gian | **Badge tốc độ (vít 20×, bơm 4×, trục cán tốc độ thực); dòng chảy "minh họa"; giả định có dấu \*** | Một hệ số chung: dòng nhựa gần như đứng yên |
| Q5 | Các điểm lệch 10.2–10.4 | **Sửa trong anim, ghi vào báo cáo, không sửa `design/`** | Mở lại design |
| Q6 | Phim kể vòng điều khiển nào | **(a) Kiểu dây chuyền tấm: tốc độ bơm đặt lưu lượng ra khuôn, cùng tốc độ trục cán quyết định chiều dày; P3 chỉnh cân + vít theo tỉ lệ** | (b) Theo design s_20: P3 chỉnh tốc độ bơm, cân đặt lưu lượng. Đây là kiểu compounding; dao động của cân đi thẳng ra khuôn thành dao động chiều dày |
| Q7 | Cho chạy một tiến trình nền `blender -b out/ze155_anim.blend` để render bản cuối | **Đồng ý, chỉ cho bước render cuối. Bản xem trước và mọi việc dựng vẫn qua MCP.** Không chặn Blender đang mở trong 3–4 h, nhanh hơn một chút, chạy tiếp được. BRIEF.md đang cấm nên cần người dùng cho phép | Render qua MCP theo đợt ≤ 40 khung; Blender bận ≈ 3–4,5 h |

## Nguồn

- **Claims (`research/claims.jsonl`):**
  - máy: c001–c006, c031, c036;
  - ứng dụng: c040, c043–c046;
  - bơm: c047, c049;
  - lọc: c050, c052;
  - khuôn: c053–c056;
  - chân không: c061, c062;
  - cấp liệu: c069.
- **Thiết kế:** `design/design.md` §1, §3, §3.1, §6.1, §7, §9; bản vẽ tờ 02, 05, 07.
- **Web:**
  - Plastech/Gneuss "Dryerless PET extrusion with viscosity control";
  - Plastics Technology "Solve venting problems…" và "How to configure your twin-screw extruder, part 3";
  - PlasticsToday "Direct extrusion with twin-screw extruders" (Leistritz, qua reviewer): bơm đặt, P3 chỉnh vít + cân;
  - Dynisco/AZoSensors "Closed loop pressure control";
  - sáng chế USPTO về tấm PET vô định hình (nhiệt độ trục cán).

## Đã sửa theo review

| Mã | Đã sửa / lý do bỏ qua |
|---|---|
| C1 | Đổi S10, S15, S16 và mục 1, 2, 5, 10 sang kiểu dây chuyền tấm: bơm đặt lưu lượng, P3 chỉnh cân + vít, chiều dày do bơm + trục. Thêm Q6; nội dung thay thế cho Q6b có trong `alt_if_Q6b`; bỏ câu cho rằng cách kia sai |
| I1 | Viết lại cách lưu: tạo scene trong phiên, chỉ lưu `out/ze155_anim.blend`, kiểm bằng đọc lại (bản tạm nếu lỗi), không `Z.save_blend()`. C0 dọn camera chỉ trong scene anim. Thêm khung lưu ý Ctrl+S và thay đổi chưa lưu |
| I2 | Thêm 17 nhóm `ax_*` với danh sách thành viên, bảng nhóm × shot, quy tắc bản sao `_keep`/`_rm`, bản sao tách `anim_split_*` |
| I3 | Phần tử 12 và 22 cắt sẵn tại X 2 450 và 4 120; phần tử sau mặt cắt ẩn; pha nắp tính sẵn; khối điền cắt theo |
| I4 | S04 ẩn sàn thao tác; S03 tách 2 camera (trên sàn, dưới sàn), đã kiểm tia nhìn không qua cột hay mép sàn |
| I5 | S04/S06 có vòm vẽ mờ + dải cửa sổ tím trên xi lanh đã cắt; dải HUD vẽ cửa sổ cạnh vị trí nút |
| I6 | Một giá trị ±0,15 mm; khe và hành trình cùng vẽ ×10 (`gap_x10` + `lip_push`); đồng hồ số giá trị thật; ST4 dùng khe thật |
| I7 | Nhãn được xếp tự động và kiểm (≥ 3 s, 0,4 s mỗi từ, ≤ 4 nhãn cùng lúc). S06 11 s; S14 tách thành S14 (16 s) + S15 vòng điều khiển (26 s, sơ đồ khối); S16 10 s. Tổng 3:31 |
| I8 | Kế hoạch render theo đợt ≤ 40 khung qua MCP, chạy tiếp được, nêu rõ Blender bận 3–4,5 h; thêm Q7 (tiến trình nền) |
| I9 | Dấu \* cho mọi giá trị giả định trên hình và trong bảng mục 2, chân hình "* = giả định"; sửa ô nguồn của Δp |
| M1 | Ghi rõ lõi 114,6 của design hợp lệ; HUD ghi "Vít Ø167,5 (mô hình)" |
| M2 | Bọt vùng 1 dày và nhanh, vùng 2 nhỏ và thưa |
| M3 | Hạt và vân trôi theo bước × vòng/s (63 / 42 mm/s) |
| M4 | Chốt van: XẢ ở Y −0,2 m, CHẠY ở 0; key −0,2 → 0 |
| M5 | 3 500 kg/h là tổng = cân chính ≈ 3 300 + biên tấm ≈ 160 + phụ gia ≈ 40; sửa nhãn cân |
| M6 | Màn nhựa giữ màu hổ phách trong khe gió; tấm trong dần từ khe trục |
| M7 | Quy tắc vật cắt ngang mặt phẳng (curve đổi sang mesh); một hộp X −0,05…6,5 cho S04/S06/S08; ẩn ống chân không; thanh chặn nhấc theo nửa trên |
| M8 | Ảnh tĩnh có trạng thái riêng; ST1 dùng vỏ lọc trong suốt, không cắt đĩa |
| M9 | Khối điền `_lo` cho mọi shot cắt Z |
| M10 | Phương án ngắn của Q1 giữ S06, rút shot khác |
| M11 | Ống phân phối dời về tâm X 9 172 (vách 10 mm); đã nêu trong Q2 và hình chèn S11 rằng móc áo gần chữ T; cửa vào Ø100 ở cả hai bộ phận |

Không bỏ qua mục nào.
