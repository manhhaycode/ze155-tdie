# Bộ bản vẽ ZE 155 A UT 34D + đường chảy + khuôn chữ T – Rev. B

Tất cả bản vẽ và ảnh chiếu được sinh bằng script Python từ `design/parts.json` (dữ liệu chuẩn, hiện 187 chi tiết và 72 mối nối). Vì vậy bản vẽ luôn khớp với dữ liệu. Muốn cập nhật sau khi sửa thiết kế thì chạy lại một lệnh:

```
uv run -q --with matplotlib --with numpy --with pillow python design/draw/make_all.py
```

Lệnh này sinh lại ảnh chiếu cho Blender cùng `views.json`, chạy kiểm tra `verify_views.py`, rồi sinh lại 9 tờ vẽ (khoảng 25 giây). Tờ 09 chạy sau cùng vì cột "Tờ" của nó đọc danh sách bóng số mà các tờ 01–08 ghi ra.

## Tờ vẽ (`sheet-NN-<tên>.svg` + `.png`)

Cả 9 tờ đều khổ A0. Mỗi tờ có khung, lưới toạ độ, khung tên (dự án, tên tờ, tỷ lệ, tờ n/9, ngày 2026-10-04, "vẽ: Claude (giả định ghi chú G)"), ô sửa đổi Rev. B và ký hiệu phép chiếu góc thứ nhất (ISO E). Chữ nhỏ nhất 9,8 pt, tức chiều cao chữ hoa 2,5 mm khi in đúng khổ (ISO 3098); script tự giữ mức này. Kiểu nét:
- nét liền đậm: cạnh thấy;
- nét đứt: cạnh khuất;
- nét chấm gạch: đường tâm;
- nét gạch hai chấm (phantom): bối cảnh (cụm cán láng, tấm nhựa);
- đường ngắt hình chữ Z (break line): mép hình chiếu bị cắt bớt.

Số trong bóng (balloon) là số thứ tự chi tiết trong `parts.json`, dùng chung cho mọi tờ; danh mục đủ ở tờ 09. Mỗi tờ có danh mục riêng gồm đúng các chi tiết có bóng số hoặc chú thích trên tờ đó. Chữ G đánh dấu giá trị giả định.

| Tờ | Khổ, tỷ lệ | Nội dung |
|---|---|---|
| `sheet-01-ga` | A0, 1:50 | Bố trí chung (general arrangement): hình chiếu đứng từ +Y, mặt bằng, nhìn từ đầu khuôn (+X) và đầu dẫn động (−X). Kích thước bao, cao độ, toạ độ X các trạm, bóng số các cụm chính, vị trí 9 nút dừng khẩn ES1–ES9 kèm bảng toạ độ. Danh mục chi tiết của tờ, bảng thông số chính, bảng trạm, ghi chú chung. |
| `sheet-02-barrel` | A0, 1:20 / 1:5 / 1:10 / 1:50 | Đoạn gia công (processing section): bố trí 1×4D + 5×6D, vỏ che C1–C6 vẽ phantom; cấu hình trục vít theo `screws.details` và bảng vùng thẳng hàng theo X; mặt cắt A–A qua lỗ số 8 (trục vít hatch, 20 đai ốc phía sau); chi tiết B mối nối bích Ø640, cổ thắt Ø500 × 40, vùng xoay khẩu; mặt bích 20 lỗ; chi tiết C gối đỡ. Mạch nước làm mát: hình D (1:10, bỏ vỏ che), mặt cắt E–E qua đầu nối, sơ đồ một vùng, mặt bằng nước F (1:50). |
| `sheet-03-drive` | A0, 1:20 / 1:10 / 1:5 | Truyền động (drive train): hình chiếu đứng, mặt bằng, nhìn từ −X; chi tiết D mặt cắt khớp đàn hồi + khớp an toàn (trục động cơ lắp 120 trong moay-ơ); mặt cắt E–E lantern (trục ra, ống then hoa, chuôi vít, ổ chặn); sơ đồ dầu bôi trơn có van an toàn, lọc hút, PSL, TT, van bi nước; bảng cao độ trục. |
| `sheet-04-melt-line` | A0, 1:10 / 1:20 / 1:2 | Đường chảy nhựa (melt line): hình A (1:10) có lòng chảy nét đứt tới ống phân phối khuôn, P1–P5/T1/T5, đĩa nổ, vòng P3 → PIC → tốc độ bơm; hình chiếu đứng B và mặt bằng C (1:20, HPU, ống thuỷ lực); hình D các mặt bích và bảng bích lấy từ design.md §6.3; hình E nửa mặt cắt bích bơm → P4 (1:2). |
| `sheet-05-tdie` | A0, 1:10 / 1:2 / 1:20 / 1:5 | Khuôn chữ T (T-die): mặt trước, hình chiếu bằng có đầu vít thân; mặt cắt A–A (1:2) với lòng Ø100 của bích chuyển hở vào ống phân phối, rãnh bản lề hở, gân 12, vít thân nét khuất; mặt cắt B–B dạng móc áo có lỗ vít thân; hình C khuôn + cụm cán; chi tiết D môi khuôn – khe trục. Mặt sau khuôn, bích chuyển và các hàng vít lấy từ parts.json. |
| `sheet-06-feed-vacuum` | A0, 1:50 / 1:20 | Cấp liệu và chân không (feeding and vacuum): sàn thao tác, cầu thang, cân, phễu, máy hút liệu; ống nạp liệu C; side feeder D; mặt bằng chân không E; hình F nhìn từ +X; sơ đồ chân không G. |
| `sheet-07-process-utilities` | A0, không tỷ lệ | Sơ đồ P&ID và liên động: ký hiệu ISA (bong bóng thiết bị đo có tag), van, bơm; số đường = id mối nối; thuỷ lực có van 4/3; sơ đồ cấp điện một sợi; chuỗi dừng khẩn ES1–ES9, các tín hiệu ngắt và khoá liên động; bảng nguyên nhân → tác động (design.md §7); danh mục thiết bị đo. |
| `sheet-08-utility-routing` | A0, 1:25 / 1:20 / 1:50 | **Mới.** Tuyến tiện ích (utility routing) vẽ từ `connections[].path_mm`: mặt bằng 1:25 có hào cáp, máng cáp, điểm cấp trung thế và hạ thế, cáp đứng, mạng khí nén, nước cấp và hồi, tuyến tín hiệu, màu theo môi chất, nhãn id ở đầu tuyến phía máy. Bốn mặt cắt nơi tuyến dựng lên máy: A–A cáp trung thế lên động cơ, B–B cáp đứng + ống nước + khí nén, C–C đường chảy, D–D khuôn. Bảng đủ 72 mối nối (từ, tới, môi chất, chiều dài tuyến, kiểu nối). |
| `sheet-09-bom` | A0 | **Mới.** Danh mục chi tiết đủ 187 mục (chữ 12 pt): số, mã, tên, số lượng, vật liệu/màu, các tờ có bóng số hoặc chú thích của chi tiết (sinh tự động), cờ G. |

### Thay đổi của Rev. B (theo `review-01.md`)
- **C1:** lòng Ø100 hở từ bích chuyển vào ống phân phối trong A–A và B–B tờ 05; hình A tờ 04 vẽ tiếp lòng chảy vào khuôn.
- **C2:** thông số bích đường chảy lấy theo dữ liệu (một nguồn), thêm nửa mặt cắt bích tỷ lệ 1:2.
- **I1:** mạch nước làm mát xi lanh vẽ có tỷ lệ trên tờ 02 (hình D, E–E, F).
- **I2, I3:** liên động, nguồn cấp vào, nút dừng khẩn, vòng P3 → tốc độ bơm trên tờ 01, 04, 07.
- **I4, I5:** vít thân khuôn và rãnh bản lề hở trên tờ 05. Bố trí vít thân là đơn giản hoá đã biết, ghi "bố trí bu-lông thân khuôn đơn giản hóa (G)" (design_issues #9).
- **I6, I7:** bích Ø640 + cổ thắt trên tờ 02; khớp nối, trục then hoa, lantern trên tờ 03.
- **I8:** tờ 08 mới (tuyến tiện ích + bảng mối nối).
- **I9:** mọi tờ lên A0, chữ ≥ 2,5 mm; danh mục đủ chuyển sang tờ 09 nên danh mục trên tờ 01 dùng chữ 11 pt.
- **I10:** tờ 07 thành P&ID; hết chữ chồng nhau (số chi tiết đặt ngoài góc khung).
- **M1–M8:** đã xử lý; M4 thêm đường ngắt ở các hình bị cắt bớt (tờ 03 hình chiếu đứng và mặt bằng, tờ 04 hình B và C, tờ 06 hình C, D, E, tờ 08 các mặt cắt).
- Mỗi tờ khi lưu tự kiểm tra: không có chú thích nào ra ngoài khung, không có chữ chồng nhau. Lần chạy cuối: 0 trên cả 9 tờ.

`design_issues.md` liệt kê các chỗ thiếu hoặc mâu thuẫn trong thiết kế phát hiện khi vẽ (id, vấn đề, đề xuất, cách đang vẽ); mới có #9 (vít thân khuôn cắt qua ống phân phối) và #10 (đầu trục động cơ không ăn vào moay-ơ), cả hai ghi là đơn giản hoá đã biết vì thiết kế đã chốt.

## Ảnh chiếu tỷ lệ cho Blender (`views/*.png` + `views.json`)

Đây là ảnh nền camera, không phải tờ trình bày: nền trắng, viền đen 1–2 px, tô xám nhạt theo cụm, không chữ, không kích thước. Mỗi ảnh là phép chiếu trực giao đúng của parts.json theo `px_per_mm` cố định. `views.json` ghi đúng định dạng METHOD.md §2: điểm ảnh (u, v), v đếm từ trên xuống, ứng với `center + (u − W/2)/s · right + (H/2 − v)/s · up`.

| Khoá | Ảnh | Kích thước (px) | px/mm | look / right / up | center_mm |
|---|---|---|---|---|---|
| `front` | views/front.png | 3760 × 1380 | 0,2 | −Y / −X / +Z | [3400, 0, 3150] |
| `rear` | views/rear.png | 3760 × 1380 | 0,2 | +Y / +X / +Z | [3400, 0, 3150] |
| `top` | views/top.png | 3760 × 1660 | 0,2 | −Z / −X / −Y | [3400, −1050, 0] |
| `die_end` | views/die_end.png | 1660 × 1380 | 0,2 | −X / +Y / +Z | [0, −1050, 3150] |
| `drive_end` | views/drive_end.png | 1660 × 1380 | 0,2 | +X / −Y / +Z | [0, −1050, 3150] |
| `drive_front` | views/drive_front.png | 3150 × 1450 | 0,5 | −Y / −X / +Z | [−2650, 0, 1350] |
| `barrel_front` | views/barrel_front.png | 3125 × 1200 | 0,5 | −Y / −X / +Z | [2975, 0, 1100] |
| `feed_front` | views/feed_front.png | 1625 × 2550 | 0,5 | −Y / −X / +Z | [375, 0, 3850] |
| `melt_front` | views/melt_front.png | 3600 × 2450 | 1,0 | −Y / −X / +Z | [7450, 0, 1175] |
| `die_front` | views/die_front.png | 1400 × 3050 | 1,0 | −Y / −X / +Z | [9650, 0, 1475] |
| `die_end_detail` | views/die_end_detail.png | 2750 × 1625 | 0,5 | −X / +Y / +Z | [0, 250, 1575] |
| `melt_top` | views/melt_top.png | 3440 × 3680 | 0,8 | −Z / −X / −Y | [7800, −600, 0] |

Quy ước riêng của ảnh chiếu:
- Thứ tự vẽ theo độ sâu dọc trục nhìn: phần xa vẽ trước. Mặt vát của khối đùn được chia thành dải theo độ sâu, nên chi tiết gắn trên mặt vát (ví dụ bulông nhiệt trên mũi khuôn) không bị che sai.
- Chi tiết bối cảnh (cụm cán, ray, tấm nhựa) chỉ vẽ viền xám, không tô, để không che máy. Sàn nhà xưởng không vẽ; ảnh mặt đứng có đường xám ở Z = 0.
- Sàn lưới thao tác không tô trong ảnh nhìn từ trên (lưới nhìn xuyên được); dầm thép vẫn tô và che.
- Toạ độ dọc trục nhìn trong `center_mm` để 0 (METHOD.md: thành phần này bị bỏ qua).

## Kiểm tra ảnh chiếu

`design/draw/verify_views.py` đọc lại `views.json`. Với mỗi ảnh, script chiếu góc hộp bao (bbox) của 5–7 chi tiết có tên bằng công thức METHOD.md rồi kiểm hai điều:
1. Màu điểm ảnh: trong bán kính 2 px quanh mỗi góc phải có điểm viền tối.
2. Đa giác đã vẽ: biên điểm ảnh của chi tiết (`views/check/<khoá>_parts.json`) phải trùng hộp bao chiếu, sai lệch tối đa 2 px.

Script còn kiểm công thức theo chiều ngược và kiểm camera thuận tay phải. Mỗi tờ vẽ khi lưu còn tự kiểm tra không có đường dẫn (leader), bóng số hay kích thước nào vượt ra ngoài khung bản vẽ. Ảnh có dấu chữ thập đỏ nằm ở `views/check/<khoá>.png`; chữ thập hồng là góc bị chi tiết khác che hợp lệ nên không kiểm màu. Kết quả lần chạy cuối (Rev. B, parts.json 23:14): **68 kiểm tra, 0 lỗi**.

## Mã nguồn (`design/draw/`)

| Tệp | Vai trò |
|---|---|
| `geom.py` | Đọc parts.json và dựng hình học 3D cho từng chi tiết từ bbox, `outline_mm`, `profile_mm`, `path_mm`/`paths_mm`, `positions_mm` + `item_mm` (+ `item_axis`/`item_axes`: `item_mm` = [Ø, Ø, dài]), `beams_mm`; thêm cửa, tay nắm, bulông theo `details`. Sau đó chiếu trực giao theo trục và sắp thứ tự vẽ. |
| `views.py` | Vẽ ảnh chiếu cho Blender (Pillow) và `views.json`. |
| `verify_views.py` | Kiểm tra ánh xạ điểm ảnh ↔ mm như trên. |
| `sheet.py`, `drafting.py` | Khung tên, đặt hình chiếu, kích thước, bóng số, bảng, mặt cắt có gạch, profin trục vít, ký hiệu mặt cắt và chi tiết, ký hiệu P&ID, đường ngắt (break line). |
| `sheet01_ga.py` … `sheet09_bom.py` | Từng tờ vẽ (`sheet08_utilities.py`: tuyến tiện ích; `sheet09_bom.py`: danh mục đủ). |
| `make_all.py` | Chạy lại toàn bộ. |
