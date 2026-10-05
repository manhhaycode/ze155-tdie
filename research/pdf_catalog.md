# Danh mục catalogue KraussMaffei Berstorff "ZE twin-screw extruders" (30 trang)

Nguồn: `research/pdf/ZE_twin-screw_extruders.pdf` (ấn bản 1st edition 10/13, EXT 001 A PRO 10/13 EN). Ảnh trang: `research/pages/pNN.png` (150 dpi). Ảnh nhúng: `research/pdf_images/pNN_M.*`. Ảnh cắt/phóng to: `research/pdf_crops/`. Số đo silhouette: `research/pdf_measures.md`.

Ghi chú chung (đọc trước):
- Catalogue **không có bảng thông số kỹ thuật** (technical data table) và **không có bản vẽ có kích thước**. Thông tin hình học chỉ có thể đo tỉ lệ từ hình silhouette vector trang 9 và ước lượng từ ảnh.
- Hầu hết ảnh 3D/ảnh chụp là cỡ nhỏ **ZE UTX** (ZE 25–75) hoặc **ZE Basic**, không phải ZE 155 UT. Riêng trang 9 có silhouette "ZE 155 UT"; trang 12 có thân barrel dòng **ZE-UT** (dạng trụ tròn có mặt bích – khác hẳn barrel khối vuông của UTX); trang 16 có ảnh dây chuyền cỡ lớn.
- Silhouette ZE 155 UT và ZE 180 UT trên trang 9 là **cùng một hình mẫu** (template), ZE 180 chỉ phóng ×1,05; các hình không cùng tỉ lệ với nhau → chỉ dùng được tỉ lệ nội bộ.
- Hướng: trên trang 9 đầu ra (die end, +X) nằm **bên trái**, động cơ bên phải – trùng với quy ước hình chiếu đứng (front elevation) của BRIEF. Trên sơ đồ dây chuyền trang 24–25 thì ngược lại (dòng chảy trái → phải).
- Giá trị màu là trung vị pixel lấy mẫu trên ảnh in (sai lệch do ánh sáng/in ấn), chỉ để tham khảo.

Thang đánh giá "Hữu ích": **cao / trung bình / thấp**, kèm bộ phận cần dựng.

---

## Bảng tổng hợp nhanh (ưu tiên cho dựng mô hình ZE 155 UT + T-die)

| Ưu tiên | Tệp | Dùng cho |
|---|---|---|
| 1 | trang 9 vector → `pdf_crops/ze155ut_side.svg`, `ze155ut_side_annotated.png` | tỉ lệ toàn máy, khung đế, vỏ che barrel, vent, phễu, lantern, hộp số, motor |
| 2 | `pdf_crops/p12_barrel_types_utx_vs_ut_250dpi.png` | barrel dòng UT: thân trụ tròn + mặt bích hai đầu |
| 3 | `p16_1.jpeg`, `p16_2.jpeg` (crop `p16_*_x3.png`) | dáng/màu máy cỡ lớn: vỏ che hộp, cụm truyền động lớn màu xanh tím, khung đế xám |
| 4 | `p06_1.jpeg` + `p07_1.jpeg` (crop `p06-07_ze_utx_cutaway_spread.png`) | bố trí toàn cụm, màu thương hiệu, side feeder, C-clamp, cartridge sưởi, chân đế |
| 5 | `p01_1.jpeg` (crop `p01_cover_*`) | vent dome có kính quan sát, vỏ che inox, đầu ra, ống chân không, tem cảnh báo |
| 6 | `pdf_crops/p24-25_slot_die_smoothing_roll_600dpi.png` | bố trí slot die (22) → cụm 3 trục cán láng (23) |
| 7 | `pdf_crops/p22-23_hmi_panel_touch_keypad.png` | màn hình HMI (touch + phím màng) trên tay đỡ |
| 8 | `p08_2`, `p19_2` (C-clamp), `p05_1` (cartridge/khoan làm mát), `p05_3`, `p19_3` (khớp nối, hộp số), `p19_4` (bộ điều nhiệt trong khung đế) | chi tiết |

---

## Theo từng trang

### Trang 1 – Bìa trước
- **p01_1.jpeg** (830×1106, toàn trang). Ảnh chụp thật, góc 3/4 từ phía đầu ra, hơi cao. Máy cỡ trung (có thể UTX/UT nhỏ, không xác định).
  - Thấy: vỏ che barrel inox dạng **bán trụ** từng đoạn (barrel covers) mỗi đoạn một tem vàng "bề mặt nóng" (hot surface); **thanh ray/ống xanh dương** chạy dọc hai bên mép vỏ che (cover rails); **2 vent dome** chân không (vacuum vent domes) dạng ống trụ inox, nắp kính tròn (sight glass) có tay kẹp, nối ống mềm inox (flexible vacuum hose); bộ cấp liệu định lượng (gravimetric feeder) và phễu phía trên; **đầu ra** kiểu đầu sợi (strand die head) đặt nghiêng, hộp đấu dây (terminal box), cảm biến áp suất (pressure transducer), bó cáp sưởi; góc phải dưới là bể nước (water bath); dưới barrel có cụm phân phối nước làm mát (cooling-water manifold) với đồng hồ áp; sàn tôn chống trượt (checker plate).
  - Màu: inox xám bạc, tem vàng, ray xanh dương, khung xám sáng.
  - Hữu ích: **cao** cho vent dome, kiểu vỏ che, đầu ra barrel, ống/cáp; trung bình cho màu.
  - Crop: `p01_cover_full_x2.png`, `p01_cover_vent_domes_x3.png`, `p01_cover_die_end_strand_die_x3.png`, `p01_cover_barrel_covers_rails_x3.png`.

### Trang 2 – Ảnh hạt nhựa
- **p02_1.jpeg** (830×1106): đống hạt nhựa đen + màng xanh. Không có máy. Hữu ích: **thấp** (không dùng).

### Trang 3 – Giới thiệu
- **p03_1.jpeg** (322×1106): phần tiếp của ảnh hạt nhựa. Chữ: giới thiệu chung. Hữu ích: **thấp**.

### Trang 4 – "Technical data" (tờ gấp ngoài)
- Không có ảnh bitmap; có 6 silhouette vector nhỏ ZE 25/30/40/50/60/75 UTX (hình chiếu cạnh, xanh navy). Chữ nói 6 cỡ UTX, bản A/R, "Ultra Glide". **Không có bảng số liệu** dù tiêu đề là Technical data.
- Hữu ích: **thấp** (máy nhỏ, khác dòng).

### Trang 5 – tờ gấp trong: 1 Drive train / 2 Barrel cooling and heating / 3 8-shaped bore
- **p05_3.jpeg** (260×227, ảnh trên – "1 Drive train"). Render CAD, góc 3/4 cận cảnh. Thấy: **khớp nối an toàn** (safety coupling) dạng đĩa ly hợp bạc giữa motor (xám đen, nắp quạt có khe tản nhiệt) và hộp số (đen), giá đỡ chữ L, mặt khung đế xám sáng, móc cẩu tròn. Hữu ích: **trung bình** (khớp nối, giá đỡ, màu).
- **p05_1.jpeg** (259×226, ảnh giữa – "2 Barrel cooling and heating"). Render barrel trong suốt, góc chính diện hơi cao. Thấy: **cartridge sưởi** (heating cartridges) cắm từ dưới lên theo hình chữ V, **lỗ khoan làm mát** (cooling bores) dọc, ống mềm bọc thép (armoured hoses), khớp nối nhanh, cửa nạp trên đỉnh. Hữu ích: **trung bình** cho chi tiết barrel (đầu cắm cartridge, ống nước dưới barrel).
- **p05_2.jpeg** (260×227, ảnh dưới – "3 8-shaped bore"). Cận cảnh mặt cắt barrel lỗ số 8 (figure-8 bore) với 2 trục vít, các lỗ khoan bên, đầu nối ống. Hữu ích: **trung bình** (mặt cắt barrel, tỉ lệ lỗ/thành).
- Crop: `p05_drive_train_safety_coupling_x3.png`, `p05_barrel_heating_cartridges_cooling_bores_x3.png`, `p05_8shaped_bore_barrel_section_x3.png`.

### Trang 6–7 – "Technology made transparent" (ảnh cắt lớp ZE UTX trải 2 trang)
- **p06_1.jpeg** (593×616) + **p07_1.jpeg** (507×616) ghép thành một render CAD **ZE UTX** (cỡ nhỏ/trung), góc **3/4 từ trên, phía người vận hành**, đầu dẫn động bên trái, đầu ra bên phải. Chú thích 1–6: Drive train, Barrel cooling and heating, 8-shaped bore, Side-feeders, Base frame, C-clamp barrel connectors.
  - Thấy (trái → phải): **motor chính** xám đen có nắp quạt lá chớp (louvred fan cover); **khớp nối an toàn** bạc; **hộp số** xám đen với cụm bơm dầu bôi trơn (lube oil pump) và ống trắng phía trước, đồng hồ áp; **phễu cấp liệu** inox hình phễu có 2 ống vào; khối trắng (lantern/hộp nối) có nắp tròn; **side feeder** hai trục vít với motor điện xám nhỏ và hộp số, đặt trên **xe đẩy có bánh xe** (wheeled cart) bằng thép trắng, tem cảnh báo điện; barrel dưới **vỏ che trong suốt** (cho thấy C-clamp, cartridge sưởi, ống mềm đen); 2–3 vent dome inox; **đầu ra**: vỏ chụp inox bán nguyệt lớn và đầu sợi nghiêng; khung đế **xám sáng** dạng hộp kín, **tủ đầu cuối màu xanh KraussMaffei** có logo "KraussMaffei Berstorff" ở phía đầu ra; chân đế tròn chỉnh cao (levelling feet).
  - Màu đo: xanh thương hiệu ≈ `#0092D2`; khung đế mặt sáng ≈ `#DBDBD7`, mặt tối ≈ `#958F8C`; motor ≈ `#5D5C61`; hộp số ≈ `#484148`; inox ≈ `#8D8D8D`.
  - Hữu ích: **cao** cho bố trí tổng thể, màu, side feeder + giá đỡ, C-clamp, chân đế; trung bình cho tỉ lệ (máy nhỏ hơn ZE 155).
  - Crop: `p06-07_ze_utx_cutaway_spread.png`, `p06_cutaway_drive_motor_gearbox.png`, `p06_cutaway_side_feeder_cart.png`, `p07_cutaway_barrel_cclamp_cartridges.png`, `p07_cutaway_die_end_head.png`, `p07_cutaway_blue_end_cabinet.png`.

### Trang 8 – tờ gấp ngoài: 4 Side-feeder / 5 Base frame / 6 C-clamp
- **p08_1.jpeg** (260×227, ảnh trên – "4 Side-feeder"). Render cận cảnh: side feeder hai trục vít (twin-screw side feeder) vỏ trong suốt, trục vít đi ngang vào hông barrel, mặt bích bắt bulông, phễu nhỏ phía trên, giá đỡ. Hữu ích: **trung bình** (side feeder; ZE 155 với T-die có thể không cần).
- **p08_3.jpeg** (260×227, ảnh giữa – "5 Base frame"). Render toàn máy UTX, góc 3/4 từ trên, nền tím. Thấy: khung đế dài xám sáng có **ô mở** (open bays) ở thành bên, chân tròn, hộp số + phễu ở đầu trái, barrel có cáp sưởi, vent, đầu ra bên phải. Hữu ích: **trung bình** cho dạng khung đế (ZE 155 UT trên trang 9 có khung hai tầng với cửa tủ).
- **p08_2.jpeg** (259×227, ảnh dưới – "6 C-clamp barrel connectors"). Render cận cảnh: **kẹp chữ C** (C-clamp) hình móng ngựa ôm hai mặt bích barrel, bulông siết dọc, trục vít lộ ra, khối barrel vuông với cổng bên. Hữu ích: **cao** cho dạng C-clamp (tỉ lệ kẹp/barrel).
- Crop: `p08_side_feeder_x3.png`, `p08_base_frame_ze_utx_x3.png`, `p08_c_clamp_connector_x3.png`.

### Trang 9 – tờ gấp ngoài: silhouette dòng UT (vector)
- Không có bitmap; 135 đối tượng vector. 6 hình chiếu cạnh (side view) xanh navy `#173467` có nét trắng: ZE 90 UT, ZE 110 UT, ZE 130 UT (mẫu cũ: vỏ che thấp, phễu lớn, hộp số có ống cong, cụm bơm dầu chi tiết) và ZE 155 UT, ZE 180 UT, ZE 230 UT (mẫu mới: vỏ che dạng hộp cao, khung đế hai tầng dài, khối cao rời ở cuối).
- **ZE 155 UT** (drawing #85–#125, khung x 329,87–549,67 pt, y 459,82–507,23 pt). Thấy (trái = đầu ra → phải = dẫn động): 6 **vỏ che hộp** (barrel covers) có tay nắm và tam giác cảnh báo; vỏ 1 (đầu ra) có tấm vòm với **mặt bích tròn bắt bulông** (bolt-circle flange) và hộp đấu dây; **vent dome** dạng hộp cao có 2 kính quan sát trên vỏ 4; đoạn barrel lộ (2D + 4D + feed) với **C-clamp** và **gối đỡ barrel** (barrel support) xuống khung đế; **phễu cấp liệu** nhỏ có ống nạp nghiêng 45° về phía dẫn động; **lantern** (khoang nối/intermediate housing) có cửa thăm chữ nhật bo góc; mặt bích; **hộp số** khối chữ nhật lớn trơn; vỏ khớp nối có móc cẩu; **motor chính** có hộp trên nóc; phía trước motor là **cụm dầu bôi trơn** (bơm, lọc kép, bộ làm mát dầu, ống); dưới cụm truyền động là **ray trượt/đế** nhiều lớp; **khung đế** hai tầng (dầm trên + hộp tủ dưới có cửa, lỗ tròn) chia 2 đoạn; một **khối cao chữ nhật trơn** đứng rời ở cuối (không chạm sàn – chưa xác định, xem pdf_measures.md).
  - Hữu ích: **cao** – nguồn tỉ lệ chính cho toàn máy.
  - Crop: `ze155ut_side.svg` (vector sạch), `ze155ut_side_svg_render.png` (4000 px), `ze155ut_side_600dpi.png`, `ze155ut_side_1200dpi.png`, `ze155ut_side_annotated.png`, `ze155ut_side_outline_pt.json`; so sánh `ze130ut_side.svg/_600dpi.png/_svg_render.png`, `ze180ut_side.svg/_600dpi.png/_svg_render.png`; toàn trang `p09_all_ut_silhouettes_300dpi.png`.

### Trang 10 – "Process implementation with utmost precision"
- **p10_1.jpeg** (783×267): cận cảnh phần tử trục vít (screw element) màu đen bóng. Vector: mặt cắt lỗ số 8 với 2 trục vít ZE-A (D/d = 1,46) và ZE-R (D/d = 1,74). Hữu ích: **thấp–trung bình** (tỉ lệ lỗ số 8, khoảng cách tâm).

### Trang 11 – ZE-A / ZE-R
- **p11_1.jpeg** (783×267): cùng ảnh trục vít. Vector: mặt cắt hai trục vít ăn khớp. Hữu ích: **thấp**.

### Trang 12 – "Perfect fine-tuning" (barrel module)
- **p12_1.jpeg** (830×244): render hàng barrel **UTX** (khối vuông inox) gồm 6 đoạn 4D/6D: đoạn mở đỉnh (top-open, nạp liệu/vent), đoạn kín, các **C-clamp** nhô cao hơn đỉnh barrel, bulông dưới; nhìn chính diện cạnh hơi cao. Hữu ích: **trung bình** (tỉ lệ clamp/barrel, kiểu lỗ cartridge) – nhưng đây là UTX.
- 8 ảnh nhỏ (không có trong `pdf_images/`, chỉ thấy trên trang): hàng trên là barrel UTX (closed / top-open 4D-6D / side-open & combination / 6D liquid injection), hàng dưới là **barrel dòng ZE-UT: thân trụ tròn, mặt bích tròn lớn ở hai đầu** (closed / top-open / side-open / injection, kèm một đĩa đệm/vòng nối). Màu vàng đồng là màu CAD, không phải màu thật.
  - Tỉ lệ đọc được (gần đúng, phối cảnh): đường kính thân ≈ 0,8 × đường kính mặt bích; khớp với trang 9 (thân 477 mm / mặt bích-kẹp 571 mm ≈ 0,84).
  - Hữu ích: **cao** cho hình dạng barrel ZE 155 UT (trụ tròn có mặt bích, không phải khối vuông).
- Crop: `p12_barrel_sections_c_clamps_x2.png`, `p12_barrel_types_utx_vs_ut_250dpi.png`.

### Trang 13 – phần tử trục vít
- **p13_1/2/3.jpeg** (232×242 mỗi ảnh): cặp trục vít với phần tử vận chuyển, nhào trộn (kneading), trộn. Vector: các loại phần tử. Hữu ích: **thấp** (bên trong barrel, không thấy từ ngoài).

### Trang 14 – máy phòng thí nghiệm ZE 25 UTX
- **p14_1.jpeg** (220×752): kỹ thuật viên cầm trục vít. Thấp.
- **p14_2.jpeg** (306×242): xưởng thí nghiệm, máy nhỏ trên khung thép, sàn thao tác. Thấp.
- **p14_3.jpeg** (307×242): sợi nhựa bốc khói. Không dùng.
- **p14_4.jpeg** (307×261): **ZE 25 UTX** toàn máy, góc 3/4 trước: tủ đầu cuối xanh (≈ KM blue), khung đế xám sáng có cửa lưới, barrel nhiều cáp, phễu inox, **HMI trên tay đỡ** cao ở đầu dẫn động. Hữu ích: **trung bình** (bố trí HMI, màu).
- (1 ảnh nhỏ xref 0 trên trang không trích được – lớp mask.)

### Trang 15 – ảnh HMI
- **p15_1.jpeg** (830×752): người vận hành + **màn hình cảm ứng** (touch screen) cận cảnh, giao diện thanh nhiệt độ các vùng, bàn phím màng bên trái, viền xám đen. Hữu ích: **trung bình** cho HMI.

### Trang 16 – ứng dụng (Plastifying/Filling)
- Vector: 2 sơ đồ dây chuyền (extruder xanh navy + phễu, side feeder, vent).
- **p16_1.jpeg** (352×155): ảnh thật **dây chuyền ZE cỡ lớn**, góc 3/4 trước-trái. Thấy: vỏ che barrel **dạng hộp xám nhạt** (≈ `#CECBCC`), phễu và khối lantern/hộp số **trắng xám** (≈ `#D4DCE1`), **cụm truyền động lớn màu xanh tím** (≈ `#7B88B5`, motor + hộp số có đồng hồ, ống dầu), khung đế **xám đậm** (≈ `#707885`), sàn xưởng. Hữu ích: **cao** – gần nhất với hình dáng ZE 155 UT trên trang 9.
- **p16_2.jpeg** (352×155): dây chuyền có vỏ che **inox dạng hộp bo đỉnh** với tam giác vàng, **đầu ra nghiêng** có quạt/khay sợi (strand die với tấm dẫn) ở trái, khung đế xám sáng, cụm dẫn động xám ở phải, cột nhà xưởng. Hữu ích: **cao** cho vỏ che hộp + tem cảnh báo.
- Crop: `p16_large_ze_production_line_box_covers_x3.png`, `p16_ze_line_stainless_box_covers_die_x3.png`.

### Trang 17 – ứng dụng (Masterbatch/Reaction & degassing)
- Vector: 2 sơ đồ (chú thích 1–9: polymer, filler, additives, pigment, side feeder, extruder, vacuum degassing, stripping agent injection, water bath).
- **p17_1.jpeg** (352×155): máy giữa khung thép tím, barrel có tem vàng, tủ điều khiển. Thấp–trung bình.
- **p17_2.jpeg** (352×155): ZE cỡ trung, vỏ che **inox bán trụ** nhiều tem vàng, phễu trên cao, khung đế xám sáng có cửa, HMI trên giá trắng. Hữu ích: **trung bình**.
- Crop: `p17_ze_rounded_covers_x3.png`.

### Trang 18 – ZE Basic
- **p18_1.jpeg** (744×390): **ZE Basic** toàn máy, 3/4 trước, nền trắng. Thấy: tủ đầu cuối **xanh KM** có logo dọc, khung đế xám sáng với cửa có lưới, **khoang hở** (open bay) có sàn lưới ở đầu dẫn động, motor + hộp số trên khung, barrel có cáp sưởi chụm, phễu inox, 2 vent, **HMI trên tay đỡ** cao. Hữu ích: **trung bình** (bố trí, HMI, chân đế; nhưng là máy nhỏ).
- Crop: `p18_ze_basic_full_side_x2.png`.

### Trang 19 – ZE Basic chi tiết
- **p19_1.jpeg** (456×258): ZE Basic góc 3/4 **phía sau** (rear side): khung đế hở có giá đỡ, cụm thủy lực/bôi trơn trong khoang, motor có quạt, HMI. Trung bình.
- **p19_2.jpeg** (232×197, "C-clamp barrels"): ảnh đen trắng **nhìn dọc trục** (end view) barrel: lỗ số 8 với 2 trục vít, mặt bích tròn 4 vấu, kẹp C, ống nối. Hữu ích: **cao** cho mặt đầu barrel/clamp.
- **p19_3.jpeg** (232×198, "Drive train: solid technology"): hộp số xám có **móc cẩu**, khớp nối bạc, motor bơm dầu đứng nhỏ, motor chính có khe gió. Hữu ích: **trung bình–cao** cho hộp số + khớp nối.
- **p19_4.jpeg** (232×197, "Temperature control"): **bộ điều nhiệt** (temperature control unit) trong khung đế: bơm, lọc, ống mềm đen, van, sàn lưới. Hữu ích: **trung bình** (chi tiết bên trong cửa khung đế).
- Crop: `p19_ze_basic_rear_view_x2.png`, `p19_c_clamp_barrel_endview_x3.png`, `p19_gearbox_coupling_oilpump_x3.png`, `p19_temperature_control_unit_in_base_x3.png`.

### Trang 20 – ZE Basic D/d = 1,55
- **p20_1.jpeg** (830×267): trục vít đen + góc phễu/barrel. Vector: 4 sơ đồ ứng dụng nhỏ. Hữu ích: **thấp**.

### Trang 21 – barrel ZE Basic
- **p21_1.jpeg** (830×267): hàng barrel ZE Basic có C-clamp, 2 vent dome inox, cổng side feeder (lỗ số 8 nhìn ngang), **adapter đầu ra nghiêng** ở phải, rất nhiều cáp sưởi phía dưới. Nhìn chính diện cạnh. Hữu ích: **trung bình** (vent, cáp sưởi, adapter).
- 4 ảnh nhỏ (không trích được): 8D closed, 8D/10D top-open, 8D/10D combination, 4D feed barrel.
- Crop: `p21_ze_basic_barrel_vents_x2.png`, `p21_ze_basic_barrel_types_250dpi.png`.

### Trang 22 – Process Control Advanced
- **p22_1.jpeg** (213×171): màn hình tổng quan dây chuyền (line overview). Thấp.
- **p22_2.jpeg** (213×171): màn hình extruder với các vùng nhiệt barrel đánh số. Thấp–trung bình (số vùng nhiệt).
- **p22_3.jpeg** (213×160): màn hình quản lý công thức (recipe). Thấp.
- **p22_4.jpeg** (213×160): màn hình biểu đồ xu hướng (trend). Thấp.
- **p22_5.jpeg** (248×432): **nửa trái tấm HMI** (ghép với p23_4).

### Trang 23 – HMI
- **p23_1/2/3.jpeg** (213×160): màn hình cấp liệu, tổng quan extruder (có hình motor xanh), nhiệt độ. Thấp.
- **p23_4.jpeg** (240×432): **nửa phải tấm HMI**.
- Ghép p22_5 + p23_4 → **tấm điều khiển** khổ ngang (≈ 1,57 : 1), viền xám đen, màn cảm ứng ở giữa, bàn phím màng 3 cột bên trái, cột giá trị + phím chức năng bên phải, 2 nút tròn (đen "0", xanh lá "I") góc trái dưới, 2 nút xanh dương góc phải dưới, logo KraussMaffei Berstorff; gắn trên **ống đỡ** trắng-xám với khớp xoay đen. Giao diện có 16 vùng nhiệt (zones 1–16). Hữu ích: **cao** cho HMI.
- Crop: `p22-23_hmi_panel_touch_keypad.png`, `p22_2_hmi_screen_extruder_overview_x3.png`, `p23_2_hmi_screen_extruder_overview_x3.png`.

### Trang 24–25 – "Implementing integrated concepts" (sơ đồ dây chuyền, vector trải 2 trang)
- Sơ đồ màu navy/cam: silo, cân định lượng A–E (Recycling, Rework, Resin blend, Premix, Big bag), feeder (1–3), **extruder 5** (motor + hộp số bên trái, phễu chính, **side feeder 4**, 2 cổng **vacuum degassing 6**, một chân đỡ barrel gần đầu ra), **đường ống chảy dẻo** (melt line, cam) nằm ngang, **22 slot die**, **23 smoothing roll** (cụm 3 trục cán láng đứng), băng con lăn làm nguội với 3 tủ điện bên dưới, **24 tensioning unit** (cụm kéo căng/haul-off), **25 material accumulator** (bộ tích màng kiểu festoon), **26 winder** (máy cuốn 2 trạm).
- Hướng: dòng chảy trái → phải (ngược trang 9). Không theo tỉ lệ.
- Hữu ích: **cao** cho cách nối die – trục cán và các thiết bị sau (downstream); thấp cho kích thước.
- Crop: `p24-25_line_layout_spread.png`, `p24-25_slot_die_smoothing_roll_600dpi.png` (mô tả chi tiết trong `pdf_measures.md` §5).

### Trang 26 – "From planning to production" (modular concept)
- **p26_4.png** (877×453): bản vẽ nét trắng/xanh của nhà máy compounding trong khung thép nhiều tầng (silo, sàn, cầu thang). Thấp.
- 3 ảnh nhỏ (không trích được): cẩu lắp module, module khung thép, dây chuyền lắp sẵn. Thấp.

### Trang 27 – sơ đồ dây chuyền tạo hạt (pelletizing)
- Vector: strand die head (7), water bath (8), vacuum air knife (9), strand pelletizer (10), classifier (11), silo (12–14), underwater pelletizer (15), heat exchanger (16), water tank (17), dryer (18), bow screen (19), agglomerate separator (20), diverter valve (21). Chú thích 1–26 dùng chung với trang 24–25 (22 slot die, 23 smoothing roll…).
- Hữu ích: **thấp** (dây chuyền tạo hạt, không phải T-die); trung bình nếu cần biểu tượng van chuyển hướng (diverter valve).

### Trang 28 – OEE Plus
- **p28_1.jpeg** (535×319): ảnh thuyền đua chèo. Không dùng.

### Trang 29 – Tập đoàn KraussMaffei
- Vector bản đồ thế giới. Không dùng.

### Trang 30 – Bìa sau
- **p30_1.jpeg** (315×1106): ảnh thật vùng nạp liệu: khung đế **xám sáng** với ống inox chạy dọc chân, vỏ che barrel inox có tem vàng, giá đỡ xanh dương, bộ cấp liệu treo với ống mềm, tay quay van trượt, sàn tôn chống trượt. Góc nghiêng từ trên. Hữu ích: **trung bình** (màu khung đế, ống dọc khung, vùng phễu).

---

## Bộ phận ↔ nguồn tốt nhất

| Bộ phận | Nguồn tốt nhất | Ghi chú |
|---|---|---|
| Khung đế (base frame) | trang 9 (ZE 155 UT), p16_1, p06/07, p08_3, p30_1 | ZE 155: hai tầng, chia 2 đoạn; màu xám sáng (UTX/Basic) hoặc xám đậm (p16_1) |
| Barrel (thân trụ + mặt bích UT) | p12 hàng dưới, trang 9 | UT = trụ tròn có mặt bích; UTX = khối vuông |
| C-clamp | p08_2, p19_2, p12_1, trang 9 | trang 9: kẹp cao 571 mm, rộng 151 mm (ước tính) |
| Cartridge sưởi / khoan làm mát | p05_1, p07 cutaway, p21_1 | cáp sưởi chụm xuống dưới barrel |
| Vỏ che barrel | trang 9 (hộp), p16_1, p16_2 (hộp), p01, p17_2 (bán trụ) | ZE 155 trang 9: dạng hộp, 6 tấm |
| Vent dome | p01 (kính tròn), trang 9 (hộp 2 kính), p21_1 | |
| Phễu cấp liệu | trang 9, p06 cutaway, p18_1 | |
| Side feeder | p08_1, p06 cutaway (xe đẩy) | T-die sheet line thường không cần |
| Lantern + hộp số | trang 9, p19_3, p05_3 | |
| Khớp nối an toàn | p05_3, p19_3 | |
| Motor chính | trang 9, p16_1 (xanh tím), p06 cutaway (xám đen, nắp quạt lá chớp) | |
| Cụm dầu bôi trơn | trang 9 (trước motor), p19_4, p06 | |
| Tủ điện / HMI | p22_5+p23_4, p15_1, p14_4, p18_1 | HMI trên tay đỡ |
| Slot die + trục cán | trang 24–25 | chỉ sơ đồ |
