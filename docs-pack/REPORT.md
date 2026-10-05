# Báo cáo tài liệu nguồn và giả định: mô hình 3D dây chuyền tấm PET KraussMaffei Berstorff ZE 155 A UT 34D + khuôn chữ T

Ngày tạo: 2026-10-05 14:24. Gói: `docs-pack/ze155-sources-and-assumptions.zip` (143,0 MB). Bản này cũng nằm trong zip dưới tên `00_REPORT.md`.

## 1. Tóm tắt

Dự án dựng mô hình 3D trong Blender cho một dây chuyền đùn tấm PET: máy đùn trục vít đôi đồng hướng (co-rotating twin-screw extruder) KraussMaffei Berstorff ZE 155 A UT, chiều dài gia công L/D 34, cùng đường chảy nhựa (melt line) và khuôn phẳng chữ T (flat T-die) rộng 2 400 mm, chĩa vào cụm cán láng 3 trục (polishing roll stack). Sau đó có thiết kế animation và mặt cắt bên trong (interior / cutaway), rồi kế hoạch đưa mô hình lên web bằng React Three Fiber (R3F).

**Quy trình (pipeline)** và sản phẩm của từng bước:

| Bước | Sản phẩm chính | Thư mục trong zip |
|---|---|---|
| 1. Nghiên cứu (research): catalogue PDF + web, chạy song song | 70 claim có URL, `specs.md`, 20 ảnh tham chiếu, 30 trang catalogue, 45 ảnh nhúng, 46 ảnh cắt, số đo hình bóng trang 9 | `01_sources/` |
| 2. Thiết kế (design) | `design.md` (tiếng Việt, đánh dấu giả định), `parts.json` 187 chi tiết + 72 mối nối, review thiết kế | `03_design/` |
| 3. Bản vẽ (drawings) | 9 tờ A0 (SVG + PNG), 12 ảnh chiếu có tỷ lệ cho Blender, review bản vẽ | `04_drawings/` |
| 4. Dựng trong Blender (build) qua MCP | `out/ze155.blend` (610 object, ≈ 1,25 triệu tam giác; không đưa vào zip), nhật ký dựng, 11 ảnh render, 8 ảnh so sánh | `05_model_build/` |
| 5. Review mô hình độc lập + vòng sửa | `review-model-01.md` và ảnh bằng chứng | `05_model_build/review/` |
| 6. Animation và nội thất (interior) | `design-anim.md`, `shots.json` (16 shot), `interior_parts.json` (33 hạng mục), nhật ký dựng nội thất A1a/A1b, storyboard | `06_animation_interior/` |
| 7. Kế hoạch web R3F | `PLAN-R3F.md`, `model-contract.json`, `r3f-snippets.md`, `PLAN-DOT1.md` + `AMENDMENTS.md`, các review | `07_web_plan/` |

Mọi bước do agent riêng làm theo `BRIEF.md`, `METHOD.md` (phương pháp lấy từ phiên dựng Honda GX200 trước đó), `BUILD.md` và `BUILD-ANIM.md` (`08_method/`). Mọi quyết định thay người dùng ghi trong `DECISIONS.md` (31 mục). Các giả định được gom thành sổ giả định `02_assumptions/ASSUMPTIONS.md`.

## 2. Nguồn đã dùng (có sẵn trên máy)

Chỉ dùng file đã có trên máy. URL chép từ `research/web/images.md`, `research/claims.jsonl`, `research/specs.md` (và `BRIEF.md` cho catalogue); không mở lại URL nào khi lập gói này.

### 2.1 Tài liệu có bản lưu cục bộ

| Tài liệu | Nguồn gốc (như ghi trong file cục bộ) | Dùng để làm gì | Đường dẫn gốc → trong zip |
|---|---|---|---|
| Catalogue KraussMaffei Berstorff "ZE twin-screw extruders", 30 trang, ấn bản 10/13 (EXT 001 A PRO 10/13 EN) | catalogue KM, bản công khai trên plastrading.com: https://plastrading.com/wp-content/uploads/2018/03/ZE_twin-screw_extruders.pdf (c028–c035) | Hình bóng vector ZE 155 UT trang 9 (tỷ lệ toàn máy), barrel dòng UT trang 12, sơ đồ slot die → smoothing roll trang 24–25, HMI, màu, D/d 1,46, đoạn 4D/6D, hộp số chia công suất | `research/pdf/ZE_twin-screw_extruders.pdf` → `01_sources/pdf/` |
| Chữ trích từ catalogue | trích từ PDF trên | Tra cứu nội dung catalogue | `research/pdf/ZE_text.txt` → `01_sources/pdf/` |
| 30 ảnh trang (150 dpi), 45 ảnh nhúng, 46 ảnh cắt / SVG hình bóng | catalogue KM (sinh từ PDF) | Đọc chi tiết, đo tỷ lệ, lấy màu | `research/pages/`, `research/pdf_images/`, `research/pdf_crops/` → `01_sources/pdf/` |
| Danh mục ảnh catalogue, số đo hình bóng | phân tích của PDF analyst trên catalogue KM | Bộ phận ↔ nguồn tốt nhất; số đo pt và tỷ lệ (L/D ≈ 34 trên hình mẫu) | `research/pdf_catalog.md`, `research/pdf_measures.md` → `01_sources/pdf/` |
| Bảng kỹ thuật ZE UT/UTX trong brochure KM tiếng Đức "Anlagenkompetenz von KraussMaffei Berstorff" (3. Auflage 09/10), bản chữ | https://www.yumpu.com/de/document/view/6244774/anlagenkompetenz-von-kraussmaffei-berstorff (c001–c016) | **Nguồn chính của thông số máy:** D 169, rãnh 27,2, 400 v/ph, 2 930 kW, 2 × 35 000 Nm, cao trục 1 200, L 11 700 (44D), 34 000 kg; các cỡ lân cận | `research/web/src/yumpu_anlagenkompetenz_de_2010.txt` → `01_sources/web/src/` |
| 70 claim có nguồn | 34 URL khác nhau (bảng 2.3) | Mọi số liệu có mã `cNNN` trong specs và design | `research/claims.jsonl` → `01_sources/web/` |
| Tổng hợp thông số | tổng hợp của web researcher từ claim + ước lượng | Thông số chuẩn, ước lượng có ghi cách suy ra, bố trí, màu, "chưa tìm thấy" | `research/specs.md` → `01_sources/web/` |

### 2.2 Ảnh tham chiếu web (`research/web/img/web-01…20.jpg` → `01_sources/web/img/`)

| Ảnh | Nguồn (URL trang hoặc ảnh, theo `images.md`) | Ảnh cho thấy gì | Máy |
|---|---|---|---|
| web-01.jpg | https://plama.de/maschinen/doppelschneckenextruder-kraussmaffei-berstorff-ze-110-r-2/ | Toàn bộ đoạn gia công của ZE 110 R × 28D UTmi (2016), nhìn từ đầu xả: xi lanh tròn có vành bích bu-lông, vỏ nhiệt inox, máng cáp mạ kẽm, khung trắng, hộp số xanh | ZE 110 R UTmi (KM Berstorff) |
| web-02.jpg | https://plama.de/wp-content/uploads/2021/07/Doppelschneckenextruder-KraussMaffei-Berstorff-ZE-110-R-2.jpg | Cùng máy, nhìn dọc: 7 đoạn xi lanh, hộp đấu dây nhiệt, ống góp nước cấp/hồi với van điện từ và van bi tay đỏ, gối đỡ đúc trắng | ZE 110 R |
| web-03.jpg | https://plama.de/wp-content/uploads/2021/07/Doppelschneckenextruder-KraussMaffei-Berstorff-ZE-110-R-3.jpg | Cụm dầu bôi trơn hộp số trên khung đế: bơm có động cơ đứng, lọc, đồng hồ áp, bộ làm mát tấm, tất cả sơn xanh | ZE 110 R |
| web-04.jpg | https://press.kraussmaffei.com/en/news/kraussmaffei-implements-successful-compounding-project-for-lanxess-china | Dây chuyền compounding ZE 110 UT (2022) trong kết cấu thép: vỏ che inox bản lề, cân trên tầng lửng, HMI trên chân đế, cầu thang và lan can vàng | ZE 110 UT |
| web-05.jpg | https://press.kraussmaffei.com/Press/Lanxess/66844/image-thumb__66844__full-background/Photo3_%2020220324_PM_EXT_Lanxess.jpg | Cùng dây chuyền ở mặt sàn, có ba người vận hành (thước tỷ lệ ≈ 1,75 m) | ZE 110 UT |
| web-06.jpg | https://press.kraussmaffei.com/en/news/kraussmaffei-supplies-highly-efficient-extrusion-technologies-for-ground-breaking-purecycle-recycling-process | Render ZE BluePower cỡ lớn (4 t/h PP), kiểu KM hiện nay: khung thấp, tủ có dải xanh KM, ống góp nước có van, vòm khử khí | ZE BluePower (kế thừa UT) |
| web-07.jpg | https://press.kraussmaffei.com/en/news/bundled-expertise-for-the-production-of-alternative-polyolefin-based-floor-coverings | Render ZE BluePower với slot die cho tấm sàn PP: hàng bu-lông môi, bơm nhựa có động cơ đứng, adapter, giá khuôn. Gần nhất với bố trí ZE + T-die của dự án | ZE BluePower + slot die KM |
| web-08.jpg | ảnh nhúng, trang 19 của brochure KM: https://press.kraussmaffei.com/Downloadportal/public-brochures/Brochures/Brochures/03%20Technologies%20%20Series/04%20EXT%20-%20Extrusion%20Technology/02%20Series/Sheet%20Extrusion%20Lines/EXT_BR_FolienPlatten_EN.pdf | Đầu xả máy trục vít đôi KM làm tấm, khuôn tấm trên xe khuôn có bánh, tủ xanh KM | Máy trục vít đôi KM (kiểu ZE) |
| web-09.jpg | ảnh nhúng, trang 21 của brochure KM: https://press.kraussmaffei.com/Downloadportal/public-brochures/Brochures/Brochures/03%20Technologies%20%20Series/04%20EXT%20-%20Extrusion%20Technology/02%20Series/Sheet%20Extrusion%20Lines/EXT_BR_FolienPlatten_EN.pdf | Cụm cán láng 3 trục PlanetCalender: trục crôm, khung chữ C, trục 3 xoay quanh trục 2 | KM PlanetCalender |
| web-10.jpg | ảnh nhúng, trang 24 của brochure KM: https://press.kraussmaffei.com/Downloadportal/public-brochures/Brochures/Brochures/03%20Technologies%20%20Series/04%20EXT%20-%20Extrusion%20Technology/02%20Series/Sheet%20Extrusion%20Lines/EXT_BR_FolienPlatten_EN.pdf | Hình đứng toàn dây chuyền tấm: máy đùn, cụm cán, băng làm nguội, kéo và cắt. Chỉ tham khảo bố trí, chiều dài | Dây chuyền tấm KM |
| web-11.jpg | https://commons.wikimedia.org/wiki/File:Gleichl%C3%A4ufiges_Doppelschnecken_Extrudergetriebe.jpg (CC BY-SA 3.0) | Render hộp số trục vít đôi đồng hướng: vỏ hộp, hai trục ra then hoa, lọc dầu và ống | Hộp số Eisenbeiss (hãng dùng trên ZE, c026), không riêng ZE |
| web-12.jpg | https://press.kraussmaffei.com/Press/PureCycle/48221/image-thumb__48221__full-background/Photo2_20210908_PM_EXT_Purecycle.jpg | Render dây chuyền đơn trục KM KE 400: động cơ trung thế lớn có bộ làm mát trên nóc, hộp số trắng, vỏ khớp cam | Máy khác; chỉ dùng cho hình khối động cơ, hộp số |
| web-13.jpg | https://www.gneuss.com/en/polymer-technologies/filtration/rsfgenius-series/ | Ảnh sản phẩm bộ lọc lưới quay Gneuss RSFgenius: thân hộp, mũ nghiêng có khe gió, bích vào, tay quay | Gneuss (ứng viên bộ lọc) |
| web-14.jpg | cắt từ trang 1 của data sheet: https://www.suurmond.com/wp-content/uploads/2020/03/2020-MAAG-NGP-Extrex-GU-EP-SP_Class6_2s_EN_s.pdf | Thân bơm bánh răng Maag extrex6: khối chữ nhật, vòng bu-lông nắp, đầu trục, bích vào/ra | Maag (ứng viên bơm) |
| web-15.jpg | https://www.buschvacuum.com/uk/en/success-stories/modern-vacuum-technology-for-melt-degassing-during-extrusion.html | Cụm khử khí Busch PLASTEX trên khung có bánh: bình tách inox đứng, bơm MINK, hộp điều khiển | Busch (cụm chân không) |
| web-16.jpg | https://www.buschvacuum.com/media/medien/news/success-stories/q3-2020/polycomp/case-study-polycomp_fig.-3_news_article_1200x675.jpg | ZE BluePower tại PolyComp: vỏ che bản lề có tam giác vàng, side feeder, ống chân không đi trên cao | ZE BluePower |
| web-17.jpg | https://www.sbi-mechatronik.com/thermal-bolts/ | Khuôn phẳng có bu-lông nhiệt tự động trên dây chuyền, trục làm nguội phía sau, khối adapter bên trái | Hãng khác (khuôn phẳng chung) |
| web-18.jpg | https://www.sbi-mechatronik.com/wp-content/uploads/2021/09/ThermalBolt.jpg | Môi khuôn sát khe trục làm nguội: cho thấy khoảng cách khuôn–trục và hàng bu-lông môi | Hãng khác |
| web-19.jpg | https://www.tzjingyue.com/en/Products-Solution/Flat-extrusion-die/Plastic-sheet-die-series/ | Khuôn tấm móc áo (ảnh sản phẩm): bu-lông thanh chắn trên đỉnh, bu-lông đẩy môi mềm, tấm đầu có hộp đấu nhiệt | Hãng khác |
| web-20.jpg | https://www.tzjingyue.com/upload/CFECB61C1DD39AFA706BDF1616ED0B6F.jpg | Cùng loại khuôn, nhìn gần thẳng vào môi: khe môi, hai hàng bu-lông, tấm đầu | Hãng khác |

Ảnh web dùng cho: dáng ZE UT cỡ lớn (web-01…05: xi lanh tròn bích bu-lông, ống góp nước, cụm dầu xanh), kiểu KM mới (web-06/07/16), cách KM đặt slot die lên ZE (web-07/08), cụm PlanetCalender (web-09), bố trí dây chuyền (web-10), hộp số (web-11), động cơ lớn (web-12), bộ lọc Gneuss (web-13), bơm Maag (web-14), cụm chân không Busch (web-15), khuôn và bu-lông nhiệt (web-17…20). Ảnh so sánh cuối ở `05_model_build/compare/` đặt mô hình cạnh p16, web-02, web-12, web-13, web-17.

### 2.3 Nguồn chỉ có trích dẫn trong `claims.jsonl` (không lưu bản gốc trên máy)

| URL | Tiêu đề (theo claim) | Claim | Chủ đề | Độ tin cậy |
|---|---|---|---|---|
| https://www.yumpu.com/de/document/view/6244774/anlagenkompetenz-von-kraussmaffei-berstorff | Anlagenkompetenz von KraussMaffei Berstorff – Zweischneckenextruder ZE-Baureihe (DE brochure, 3. Auflage 09/10 | c001…c016 (16) | `neighbour_sizes`, `ze155_machine_data` | high, medium |
| https://aimequipmentcompany.com/products/berstorff-ze-180ax28d-ut-extruder-used-item-ue-081720c-arizona/ | AIM Equipment – Berstorff ZE 180Ax28D-UT Extruder (used listing) | c017 | `neighbour_sizes` | high |
| https://www.perry-equipment.com/equipment/7774063-berstorff-ze180a-x-28d-ut-co-rotating-twin-screw-extruders | Perry Equipment – 194mm Berstorff ZE180A X 28D-UT Twin Screw Extruder (used listing ZP60098) | c018…c019 (2) | `neighbour_sizes` | high, medium |
| https://www.equipt.com/listings/56323-used-krauss-maffei-ze110ax53d-ut-processing-misc-in-south-carolina | Equipt – USED KRAUSS MAFFEI ZE110Ax53D-UT | c020 | `neighbour_sizes` | high |
| https://www.exapro.it/kraussmaffei-berstorff-ze-110-r-x-28-d-utx-p00109129/ | Exapro – Estrusore bivite Kraussmaffei-Berstorff ZE 110 R x 28 D UTX (2016) | c021…c023 (3) | `neighbour_sizes`, `ze_colours` | medium |
| https://www.maschinensucher.at/krauss-maffei+berstorff-ze+110+r+x+28d+utmi/i-7884650 | Maschinensucher – Doppelschneckenextruder Krauss-Maffei Berstorff ZE 110 R x 28D UTmi | c024 | `neighbour_sizes` | high |
| https://www.plastemart.com/used-Krauss-maffei-berstorff-110-mm-twin-screw-pelletizing-line-usa/21100/um | Plastemart – Krauss Maffei-Berstorff 110 mm twin screw pelletizing line (ZE110RX56DUT) | c025 | `ze_gearbox` | medium |
| https://www.plastemart.com/used-krauss-maffei-berstorff-twin-screw-extruder-usa/33206/um | Plastemart – Krauss Maffei Berstorff Twin Screw Extruder ZE 52-48D | c026 | `ze_gearbox` | medium |
| https://www.euro-machinery.com/machinery/berstoff-ze25a-co-rotating-twin-screw-extruder/ | Euro-Machinery – BERSTOFF ZE25A Co-rotating Twin Screw Extruder | c027 | `neighbour_sizes` | medium |
| https://plastrading.com/wp-content/uploads/2018/03/ZE_twin-screw_extruders.pdf | KraussMaffei Berstorff – ZE twin-screw extruders catalogue (1st ed. 10/13), local copy research/pdf/ZE_text.tx | c028…c035 (8) | `ze_catalogue` | high, medium |
| https://doczz.net/doc/536453/ahead-edition-02-2014---kraussmaffei-berstorff | KraussMaffei Berstorff AHEAD edition 02/2014 | c036 | `ze_catalogue` | medium |
| https://press.kraussmaffei.com/en/news/powerful-and-highly-efficient-successful-market-launch-of-the-four-large-ze-bluepower-compounding-extruders | KraussMaffei press release 22.09.2020 – four large ZE BluePower extruders | c037 | `ze_catalogue` | medium |
| https://kraussmaffei.com/products/Extrusion/BluePower/Brosch%C3%BCre_ZE%20BP_final.pdf | KraussMaffei – ZE BluePower brochure | c038 | `ze_catalogue` | high |
| https://press.kraussmaffei.com/en/news/kraussmaffei-implements-successful-compounding-project-for-lanxess-china | KraussMaffei press release 23.03.2022 – Lanxess China | c039 | `ze_catalogue` | high |
| https://press.kraussmaffei.com/Downloadportal/public-brochures/Brochures/Brochures/03%20Technologies%20%20Series/04%20EXT%20-%20Extrusion%20Technology/02%20Series/Sheet%20Extrusion%20Lines/EXT_BR_FolienPlatten_EN.pdf | KraussMaffei – Maximum product quality and production reliability: discover our sheet extrusion lines (brochur | c040, c041, c044 | `sheet_line_application` | high |
| https://www.plasticsinfomart.com/kraussmaffei-berstorff-delivers-high-performance-extrusion-line-to-china/ | Plastics Infomart – KraussMaffei Berstorff delivers high-performance extrusion line to China (2011) | c042 | `sheet_line_application` | high |
| https://www.kunststofforum.de/information/news_archiv_komplettanlage-fuer-optische-platten-aus-einer-hand_6692 | kunststoffFORUM – Komplettanlage für optische Platten aus einer Hand | c043 | `sheet_line_application` | high |
| http://coresectorcommunique.blogspot.com/2010/04/reinforced-plastics-hanover-april-22.html | Core Sector Communique – KraussMaffei Berstorff ZE-UTX press text (2010) | c045 | `sheet_line_application` | medium |
| https://www.sml.at/sites/default/files/2023-09/prospekt%20PP%2C%20PS%20sheet%20lines%20.pdf | SML – Sheet lines brochure | c046 | `sheet_line_application` | medium |
| https://www.suurmond.com/wp-content/uploads/2020/03/2020-MAAG-NGP-Extrex-GU-EP-SP_Class6_2s_EN_s.pdf | MAAG – extrex6 GU/EP/SP booster pump data sheet | c047…c049 (3) | `melt_pump` | high |
| https://www.gneuss.com/wp-content/uploads/2026/06/Technical-data_RSFgenius_2026.pdf | Gneuss – RSFgenius Series Technical Data (2026) | c050…c052 (3) | `screen_changer` | high |
| https://www.plasticstoday.com/plastics-processing/tooling-corner-die-design-for-plastic-extrusion-part-2 | PlasticsToday – Tooling Corner: Die design for plastic extrusion, Part 2 | c053 | `t_die` | high |
| https://www.sbi-mechatronik.com/thermal-bolts/ | SBI Mechatronik – Thermal Bolts | c054 | `t_die` | high |
| https://www.bladesmachinery.com/product/used-62-cloeren-sheet-die/ | Blades Machinery – Used 62" Cloeren sheet die | c055 | `t_die` | high |
| https://reifenhauser.com/en/lines-components/components/flat-dies/ | Reifenhauser – Flat dies | c056 | `t_die` | high |
| https://www.nordson.com/en/products/polymer-processing-systems-products/edi-ultraflex-sheet-dies | Nordson – EDI Sheet Dies | c057 | `t_die` | high |
| https://press.kraussmaffei.com/Downloadportal/public-brochures/Brochures/Brochures/03%20Technologies%20%20Series/04%20EXT%20-%20Extrusion%20Technology/01%20Technologies/Flat/EXT_BR_Schaumex_Schaumtandex_XE_EN.pdf | KraussMaffei – Productivity and efficiency in foam extrusion (brochure) | c058 | `t_die` | medium |
| https://www.buschvacuum.com/global/assets/137797/1/Product%20Leaflet%20MINK%20MM%201202_1252%20AV%20Global%20EN.pdf | Busch – Product leaflet MINK MM 1202/1252 AV | c059 | `vacuum` | high |
| https://www.buschvacuum.com/uk/en/success-stories/modern-vacuum-technology-for-melt-degassing-during-extrusion.html | Busch – Modern vacuum technology for melt degassing during extrusion (PolyComp) | c060 | `vacuum` | high |
| https://www.ptonline.com/articles/solve-venting-problems-on-twin-screw-compounding-extruders | Plastics Technology – Solve venting problems on twin-screw compounding extruders | c061 | `vacuum` | medium |
| https://granuwelextruder.com/non-crystallization-dry-pet-or-pla-sheet-extrusion-production-line/ | Granuwel – Non-crystallization dry PET or PLA sheet extrusion line | c062 | `vacuum` | low |
| https://exportpagescdn.net/v2/pdfs/product/7169bcd8-b0f0-11e6-90ca-3a6bba99afcb/vakuum-gassfjerningsanlegg-tk-v-av-trendelkamp-technologie-gmbh.pdf | Trendelkamp – Extruder Vacuum Unit TK-V | c063 | `vacuum` | medium |
| https://www.aaronequipment.com/equipmentattachments/44239014_abb_model%20ami_engineered_induction_motors_catalog.pdf | ABB – High voltage engineered induction motors technical catalog, Modular induction motors type AMI | c064…c067 (4) | `main_motor` | medium |
| https://abb.bonwaygroup.com/ami-450l4w-2000kw-690v-50hz.html | AMI 450L4W 2000 KW ABB high voltage induction motor (reseller page with data sheet text) | c068 | `ze_colours` | low |
| http://indigostorage.co.za/Proindustrial/Page2%20Principals/1%20Coperion%20K-Tron/Coperion%20K-Tron%20Feeders/11%20BulkSolidPumpFeeders/3%20Specifications%20K-ML-BSP-150-S.pdf | Coperion K-Tron – Product specification K-ML-BSP-150-S | c069 | `feeder` | high |
| https://docest.com/doc/186464/tailored-ze-ut-r-twin-screw-extruder-for-highly-filled-masterbatch-compounds | KraussMaffei Berstorff press text 20.09.2012 – Tailored ZE-UT-R twin-screw extruder for highly-filled masterba | c070 | `vacuum` | medium |

### 2.4 Nguồn khác được nhắc tới

- **Phiên dựng Honda GX200 trước đó** (transcript `41763e1d-….jsonl`): nguồn phương pháp. Phương pháp chép vào `METHOD.md`, code tham chiếu ở `08_method/tools/gx200_reference/`. Transcript không được chép vào gói.
- **Nguồn quy trình trong `design-anim.md`** (chỉ có tên, không có URL trong file cục bộ): Plastech/Gneuss "Dryerless PET extrusion with viscosity control"; Plastics Technology "Solve venting problems…" và "How to configure your twin-screw extruder, part 3"; PlasticsToday "Direct extrusion with twin-screw extruders" (Leistritz); Dynisco/AZoSensors "Closed loop pressure control"; một sáng chế USPTO về tấm PET vô định hình.
- **Không dùng:** `~/ideathon-toyobo/22_3_160.pdf` (tài liệu riêng của người dùng, chỉ xác nhận chuỗi máy đùn → T-die → trục làm nguội; DECISIONS #2). Không có trong gói.

## 3. Thông số chính

**Có nguồn** = có claim hoặc tài liệu cục bộ ghi đúng giá trị đó. **Giả định** = không có tài liệu công khai; cơ sở ghi ở cột cuối. Giá trị suy ra bằng công thức từ số có nguồn được xếp vào giả định và ghi rõ cách suy.

| Thông số | Giá trị dùng trong mô hình | Phân loại | Nguồn hoặc cơ sở |
|---|---|---|---|
| Kiểu máy | ZE 155 A UT(i), co-rotating, bản A (D/d ≈ 1,46) | có nguồn (dòng bảng) + giả định (chọn bản A) | c001; c028; chọn A thay R: DECISIONS #9 |
| Đường kính vít D | 169 mm ("155" là tên gọi) | có nguồn | c001 (brochure KM, yumpu), độ tin cậy cao |
| Chiều sâu rãnh / lõi d | 27,2 mm / 114,6 mm | rãnh có nguồn; lõi giả định (suy ra) | c002; d = D − 2 × rãnh (specs §1) |
| Khoảng cách tâm a | 142 mm (trục ở Y = ±71) | giả định (suy ra, độ tin cậy cao) | a = (D + d)/2, khớp ZE 180 (c017) và ZE 110 (c020); A và R cùng a (c030) |
| Lỗ số 8 | 311 × 169 mm | giả định (suy ra) | a + D; hình học |
| L/D và chiều dài gia công | 34D = 5 746 mm | L/D theo đề bài; số mm suy ra | BRIEF.md; 34 × 169 |
| Chia đoạn xi lanh | 1 × 4D (676) + 5 × 6D (1 014) | giả định | Có đoạn 4D/6D (c031); cách chia: DECISIONS #4, #9 |
| Tốc độ vít | tối đa 400 v/ph; vận hành 300 v/ph | 400 có nguồn; 300 giả định (*) | c003; design-anim.md §2 |
| Mômen | 2 × 35 000 Nm | có nguồn | c005 |
| Cao tâm trục vít | 1 200 mm | có nguồn | c006 (ZE 25 UTXi cũng 1 200, c027) |
| Công suất truyền động tối đa | 2 930 kW | có nguồn | c004 |
| Công suất động cơ lắp đặt | 1 500 kW, 4 cực, 3 kV, biến tần, khung ABB AMI 450L4, làm mát IC81W | giả định | design.md §3.1 (≈ 800 kW cần + dự phòng); kích thước khung có nguồn c066; DECISIONS #11.3 |
| Tỷ số truyền hộp số | ≈ 3,73 | giả định | 1 490 → 400 v/ph (design.md §3) |
| Năng suất | 3 500 kg/h PET (dải 2 500–5 000) | giả định | Quy từ ZE 180 (c019) theo mômen; KM tới 6 t/h (c041); specs §0 |
| Chiều dài máy tại 34D / khối lượng | ≈ 10 000 mm / ≈ 31 t | giả định (ước lượng) | Từ 11 700 mm và 34 000 kg ở 44D (c007, c008) |
| Khe môi khuôn / tấm | Môi 2 400 mm; tấm 2 100 × 0,3–1,5 mm (mẫu 0,8 mm) | giả định | specs §0; DECISIONS #10; giới hạn cụm cán 1 800 kg/h·m (c046) |
| Khuôn chữ T | Coat-hanger, môi mềm + thanh chắn, 94 bu-lông nhiệt bước 25,4; thân 500 × 450 mm, ≈ 3,4 t, 20 vùng ≈ 50 kW | kiểu và bước có nguồn; kích thước, khối lượng giả định | c053–c057; specs §5; design.md §3 |
| Khe gió môi → khe trục | 200 mm | giả định | DECISIONS #11.4; design.md §7.7 |
| Cụm cán | 3 trục Ø800 × 2 600 mm, đứng; khe giữa–dưới ở X 9 776, Z 1 200 | Ø trong dải có nguồn; chọn Ø800 và chiều dài là giả định | c046 (400–800 mm), c044 (PlanetCalender); specs §6 |
| Bộ lọc lưới | Gneuss RSFgenius 200: 970 cm², 4 560 kg/h, 1 955 × 705 × 1 429, 3 800 kg, 39 kW | số liệu có nguồn; chọn model giả định | c050 |
| Bơm bánh răng | Maag extrex6 GU 100/125: 764 cm³/v; ≤ 370 bar, Δp ≤ 250 bar | số liệu có nguồn; chọn model giả định | c047, c049 |
| Tốc độ bơm | ≈ 69 v/ph (anim/web); design ghi ≈ 105 v/ph | giả định (105 là lỗi thiết kế) | review-anim-01: 2,99 m³/h ÷ (0,764 L × 0,95) |
| Cấu hình trục vít | 32 phần tử mỗi trục: SE 1,5D → KB 45°/5 → KB 90° + LH (nút 1) → SE (thoát khí 1) → KB trộn → LH (nút 2) → SE (thoát khí 2) → SE 1D/0,75D tăng áp | giả định | Cấu hình KM không công bố; interior_parts.json; design.md `screws` |
| Chân không | 2 vùng: B3 ≈ 50 mbar, B5 5–20 mbar; Roots ≈ 2 000 m³/h + bơm khô ≈ 400 m³/h | giả định | Thực hành PET không sấy; c061, c062 (độ tin cậy thấp) |
| Áp suất vận hành | P1 ≈ 100, P2 ≈ 95, P3 = 50, P4 ≈ 250, P5 ≈ 200 bar; ngắt P1 350, P4 330; đĩa nổ 350 bar | giả định (*) | design.md §1, §7.5; design-anim.md §2 |
| Nhiệt độ | 270–290 °C; B1 ≈ 50 (áo nước), B2 260, B3 275, B4 270, nhựa ≈ 285, khuôn 270–280 °C; trục cán 60/55/45 °C | giả định (*) | design.md §1; design-anim.md §2 |
| Gia nhiệt | Xi lanh 5 × 25 kW, lọc 39 kW, khuôn ≈ 50 kW + bu-lông nhiệt 7,5 kW, tổng ≈ 260 kW | 39 kW có nguồn; còn lại giả định | c050, c018 (ZE 180: 30 kW/đoạn), c055 |
| Xi lanh và bích | Thân Ø520, bích Ø640, 20 × M24 trên PCD 560; nối bích bu-lông (không C-clamp) | giả định | design.md §9; DECISIONS #11.1, #17; c037 |
| Cân cấp liệu | Coperion K-Tron BSP-150-S (34–6 700 dm³/h) | số liệu có nguồn; chọn giả định | c069 |

## 4. Sổ giả định: tóm tắt

Sổ đầy đủ: [`02_assumptions/ASSUMPTIONS.md`](02_assumptions/ASSUMPTIONS.md) (306 mục). Nguyên văn các dòng lệch thiết kế: [`02_assumptions/DESIGN-DEVIATIONS.md`](02_assumptions/DESIGN-DEVIATIONS.md).

| Khu vực | Giả định chính | Nhóm chi tiết design §5 | Lệch khi dựng | Lỗi do review | Tổng |
|---|---|---|---|---|---|
| Chung: máy, ứng dụng, bố trí, khung đế (general) | 14 | 3 | 2 | 1 | 20 |
| Truyền động (drive) | 11 | 8 | 7 | 2 | 28 |
| Xi lanh và trục vít (barrel / screws) | 13 | 8 | 8 | 5 | 34 |
| Cấp liệu (feeding) | 7 | 14 | 1 | 0 | 22 |
| Chân không (vacuum) | 5 | 7 | 2 | 1 | 15 |
| Đường chảy nhựa (melt line) | 15 | 18 | 10 | 4 | 47 |
| Khuôn chữ T (T-die) | 12 | 5 | 6 | 3 | 26 |
| Cụm trục cán (roll stack, context) | 6 | 1 | 5 | 0 | 12 |
| Điều khiển và điện (control) | 5 | 10 | 11 | 1 | 27 |
| Tiện ích (utilities) | 3 | 6 | 5 | 0 | 14 |
| Giá trị quy trình (process values) | 14 | 0 | 0 | 0 | 14 |
| Animation và nội thất (animation / interior) | 11 | 0 | 25 | 0 | 36 |
| Kế hoạch web (web, R3F) | 11 | 0 | 0 | 0 | 11 |
| **Tổng** | 127 | 80 | 82 | 17 | **306** |

- 127 chi tiết trong `design.md` §5 có dòng nguồn ghi "giả định" (gộp thành 80 nhóm cùng câu nguồn).
- 57 dòng `DESIGN-DEVIATION` trong `out/log.md` (mô hình tĩnh) và 25 dòng trong `anim/log.md` (nội thất A1a/A1b).
- Phụ lục: 45 dòng "ước lượng" trong `specs.md`, 40 nhãn có dấu `*` trong `shots.json` (trùng một phần với các mục trên, không cộng vào tổng).
- **Giả định có hệ quả lớn nhất:** công suất động cơ 1 500 kW; năng suất 3 500 kg/h; cấu hình trục vít; hai vùng chân không và cỡ bơm; kích thước và kết cấu trong khuôn (thân 450 mm, ống phân phối); khe gió 200 mm; đường kính xi lanh Ø520 / bích Ø640; toàn bộ nhiệt độ và áp suất vận hành.

## 5. Quyết định và review

### 5.1 Quyết định chính (`DECISIONS.md`, 31 mục)

| Nhóm | Quyết định | Mục |
|---|---|---|
| Phạm vi, nguồn | Chỉ đọc transcript phiên GX200 để lấy phương pháp; không dùng tài liệu riêng của người dùng | #1, #2 |
| Máy và thông số | Ứng dụng tấm PET trực tiếp; số liệu chuẩn là ZE 155 A UT theo bảng KM (D 169, a ≈ 142, 400 v/ph, 35 kNm, cao trục 1 200); 34D = 5 746 = 1 × 4D + 5 × 6D; hình bóng trang 9 chỉ cho tỷ lệ nội bộ | #3, #4 → #9 |
| Bố trí khuôn | Khuôn nằm ngang, môi chĩa vào khe trục giữa–dưới của cụm 3 trục đứng; 3,5 t/h, tấm 2,1 m, môi 2,4 m (thay phương án chill roll dưới khuôn) | #8 → #10 |
| Bốn điểm để ngỏ | Nối bích bu-lông; vỏ che hộp C1–C6; động cơ 1 500 kW cao ≈ 2,6 m; khe gió 200 mm | #11 |
| Hệ trục, công cụ | +X theo dòng chảy, X = 0 mặt B1, +Y phía vận hành; thư viện `tools/ze_helpers.py` | #5, #6 |
| Tổ chức agent | Research song song → designer → reviewer → drafter → builder nối tiếp; vai tách riêng, reviewer không sửa, agent dài thì bàn giao | #7, #12, #19 |
| Phân loại review | Thiết kế 01: sửa C1, I1–I8, M1, M3–M10; hoãn M2, M11. Bản vẽ 01: sửa mọi Critical và Important | #13, #17 |
| Khuôn sâu 450 mm | Giữ 450 → lùi tới X ≈ 9 060 → hủy, giữ đơn giản hóa (hàng vít qua ống phân phối) | #18 → #20 → #21 |
| Đóng băng | `parts.json` 23:14 là bản cuối; không còn review bản vẽ vòng hai; chỉ sửa cái nhìn thấy | #21, #22 |
| Tiến độ dựng | Builder 1, 2, 4a, 4b, 4c; review mô hình 01; mô hình 610 object | #14, #16, #23–#26 |
| Animation | Thiết kế anim + review (21 lỗi đã sửa); dựng trong scene mới `ze155_anim`; Q1–Q6 theo đề xuất, Q6a (vòng điều khiển kiểu dây chuyền tấm) | #27, #28 |
| Web | Đổi đích sang web R3F, hủy MP4; phương án C (xuất GLB bằng Blender nền, chỉ đọc file đã lưu); toolchain React 19.3 / R3F 9.8.1 / drei 10.7.9 / three 0.186.1 / Vite 8; bắt đầu Đợt 1 theo PLAN-DOT1 + AMENDMENTS | #29–#31 |

### 5.2 Các vòng review

| Vòng | File | Critical | Important | Minor | Xử lý |
|---|---|---|---|---|---|
| Thiết kế 01 | `03_design/review-01.md` | 1 | 8 | 11 | Designer sửa C1, I1–I8, M1, M3–M10 (design.md §10). Hoãn M2 (truyền động dài hơn ≈ 7 %) và M11 (tủ đầu máy) vì phần đó đang được dựng (DECISIONS #13) |
| Ghi chú của drafter | `04_drawings/design_issues.md` | – | – | 10 mục | #1–#3, #7, #8 đã sửa trong parts.json; #4–#6 còn mở, bản vẽ dùng giá trị G; #9, #10 là đơn giản hóa đã biết |
| Bản vẽ 01 | `04_drawings/review-01.md` | 2 | 10 | 8 | Designer sửa phần dữ liệu (I2–I6), drafter vẽ lại (C1, C2, I1, I7–I10, M1–M8) → Rev. B 9 tờ, 68 phép kiểm 0 lỗi. Không chạy vòng hai (DECISIONS #21, #22) |
| Mô hình 01 | `05_model_build/review/review-model-01.md` | 1 | 6 | 5 | Builder 4c sửa 11/12 (bỏ M5 theo cho phép); orchestrator nghiệm thu bằng ảnh hero và die-end34; không review vòng hai |
| Animation 01 | `06_animation_interior/review-anim-01.md` | 1 | 9 | 11 | Designer anim sửa đủ 21 mục; C1 thành quyết định Q6 cho người dùng (chọn Q6a). Review cũng xác nhận lỗi tốc độ bơm 105 → 69 v/ph |
| Kế hoạch web 01 | `07_web_plan/review-plan-01.md` | 1 | 10 (+ AD1) | 7 (+ AD2–AD4) | Planner sửa thành PLAN 1.1 / contract 1.1 |
| Kế hoạch web 02 (+ 2b) | `07_web_plan/review-plan-02.md` | 0 mới | 2 mới (N1, N2) | 3 mới (N3–N5); vòng 2b thêm 2 (R1, R2) | Vòng 2: mọi mục vòng 1 đã sửa, riêng C1 sửa một phần (N1). Vòng 2b: N1–N5 đã sửa; R1, R2 Minor để builder xử lý. Kết luận: sẵn sàng trình người dùng |
| Kế hoạch Đợt 1 | `07_web_plan/review-dot1-01.md` | 0 | 2 | 4 | `dot1/AMENDMENTS.md`: chia mốc 1a / Đợt 1, hoãn Đợt 1b (M2), đổi tiêu chí D2 (I1), một hàng đợi trạng thái (I2), sửa các Minor |

Ngoài các review trên, orchestrator tự nghiệm thu một số mốc bằng cách xem ảnh (DECISIONS #14–#16, #22–#26). Kết quả review Đợt 1 trên Chrome chưa có trong workspace lúc lập gói (builder đang làm trong `web/`).

## 6. Nội dung gói zip

Kích thước zip: **143,0 MB**. Số file theo loại (cột `category` của `MANIFEST.csv`):

| Loại | Số file | Dung lượng (chưa nén) |
|---|---|---|
| source | 150 | 48,6 MB |
| assumption | 3 | 146,6 kB |
| design | 90 | 35,4 MB |
| output | 28 | 71,0 MB |
| **tổng** | 271 | 155,2 MB |

Zip chứa 272 file: 271 file có dòng trong `MANIFEST.csv` cộng chính `MANIFEST.csv`.

`MANIFEST.csv` ghi cho từng file: đường dẫn trong zip, đường dẫn gốc, kích thước, sha256, loại. `design` gồm cả bản vẽ, thiết kế animation, kế hoạch web và tài liệu phương pháp (`08_method/`); `output` là sản phẩm dựng (nhật ký, render, so sánh, review mô hình, nhật ký anim) và báo cáo này. Bản thân `MANIFEST.csv` không có dòng của chính nó.

```
ze155-sources-and-assumptions.zip
├── 00_REPORT.md  (44,2 kB)
├── 01_sources/  (150 file, 48,6 MB)
│   ├── pdf/  (125 file, 42,4 MB)
│   │   ├── pages/  (30 file, 21,4 MB)
│   │   ├── pdf_crops/  (46 file, 17,1 MB)
│   │   ├── pdf_images/  (45 file, 1,0 MB)
│   │   ├── ZE_twin-screw_extruders.pdf  (2,8 MB)
│   │   ├── ZE_text.txt  (33,7 kB)
│   │   ├── pdf_catalog.md  (24,1 kB)
│   │   ├── pdf_measures.md  (16,8 kB)
│   ├── web/  (25 file, 6,2 MB)
│   │   ├── img/  (20 file, 6,1 MB)
│   │   ├── src/  (1 file, 50,9 kB)
│   │   ├── images.md  (13,7 kB)
│   │   ├── claims.jsonl  (38,1 kB)
│   │   ├── specs.md  (24,3 kB)
│   │   ├── notes_web.md  (1,4 kB)
├── 02_assumptions/  (3 file, 146,6 kB)
│   ├── ASSUMPTIONS.md  (106,7 kB)
│   ├── DECISIONS.md  (17,9 kB)
│   ├── DESIGN-DEVIATIONS.md  (21,9 kB)
├── 03_design/  (7 file, 820,5 kB)
│   ├── HANDOVER.md  (10,0 kB)
│   ├── check_parts.py  (15,5 kB)
│   ├── design.md  (243,8 kB)
│   ├── layout_preview.png  (190,6 kB)
│   ├── layout_preview.py  (6,1 kB)
│   ├── parts.json  (331,9 kB)
│   ├── review-01.md  (22,7 kB)
├── 04_drawings/  (51 file, 30,4 MB)
│   ├── HANDOVER.md  (12,7 kB)
│   ├── README.md  (12,1 kB)
│   ├── design_issues.md  (5,5 kB)
│   ├── review-01.md  (22,6 kB)
│   ├── scripts/  (16 file, 264,3 kB)
│   │   └── 15 × .py, 1 × .json
│   ├── sheet-01-ga.png  (2,4 MB)
│   ├── sheet-01-ga.svg  (2,8 MB)
│   ├── sheet-02-barrel.png  (2,4 MB)
│   ├── sheet-02-barrel.svg  (956,1 kB)
│   ├── sheet-03-drive.png  (1,5 MB)
│   ├── sheet-03-drive.svg  (831,4 kB)
│   ├── sheet-04-melt-line.png  (2,0 MB)
│   ├── sheet-04-melt-line.svg  (970,3 kB)
│   ├── sheet-05-tdie.png  (1,8 MB)
│   ├── sheet-05-tdie.svg  (710,3 kB)
│   ├── sheet-06-feed-vacuum.png  (1,7 MB)
│   ├── sheet-06-feed-vacuum.svg  (2,2 MB)
│   ├── sheet-07-process-utilities.png  (1,3 MB)
│   ├── sheet-07-process-utilities.svg  (245,2 kB)
│   ├── sheet-08-utility-routing.png  (3,0 MB)
│   ├── sheet-08-utility-routing.svg  (1,6 MB)
│   ├── sheet-09-bom.png  (3,0 MB)
│   ├── sheet-09-bom.svg  (354,7 kB)
│   ├── views.json  (2,9 kB)
│   ├── views/  (12 file, 442,2 kB)
│   │   └── 12 × .png
├── 05_model_build/  (26 file, 70,9 MB)
│   ├── compare/  (8 file, 32,7 MB)
│   │   ├── drawing-die_end.png  (1,8 MB)
│   │   ├── drawing-front.png  (4,1 MB)
│   │   ├── drawing-top.png  (5,9 MB)
│   │   ├── photo-p16.png  (1,6 MB)
│   │   ├── photo-web02.png  (7,5 MB)
│   │   ├── photo-web12-drive.png  (2,0 MB)
│   │   ├── photo-web13.png  (2,1 MB)
│   │   ├── photo-web17.png  (7,7 MB)
│   ├── log.md  (88,6 kB)
│   ├── renders/  (11 file, 36,5 MB)
│   │   └── 11 × .png
│   ├── report.md  (14,8 kB)
│   ├── review/  (5 file, 1,6 MB)
│   │   ├── review-model-01.md  (15,0 kB)
│   │   ├── rev_crop_front_cabinet_logo.png  (95,4 kB)
│   │   ├── rev_crop_front_rollstand_logo.png  (123,7 kB)
│   │   ├── rev_crop_hero_rolls_airdrop.png  (557,1 kB)
│   │   ├── rev_crop_manifold_cables.png  (803,8 kB)
├── 06_animation_interior/  (6 file, 3,2 MB)
│   ├── design-anim.md  (39,1 kB)
│   ├── interior_parts.json  (53,2 kB)
│   ├── log.md  (54,7 kB)
│   ├── review-anim-01.md  (19,2 kB)
│   ├── shots.json  (68,3 kB)
│   ├── storyboard/  (1 file, 3,0 MB)
│   │   ├── contact.png  (3,0 MB)
├── 07_web_plan/  (15 file, 770,6 kB)
│   ├── ADDENDUM-discussion.md  (4,0 kB)
│   ├── PLAN-DOT1.md  (80,4 kB)
│   ├── PLAN-R3F.md  (45,5 kB)
│   ├── dot1/  (7 file, 284,4 kB)
│   │   ├── AMENDMENTS.md  (3,2 kB)
│   │   ├── cut_states.dot1.json  (17,4 kB)
│   │   ├── devices.dot1.json  (176,1 kB)
│   │   ├── materials.dot1.json  (8,0 kB)
│   │   ├── node_map.dot1.json  (72,2 kB)
│   │   ├── rotors.dot1.json  (4,5 kB)
│   │   ├── selection-rules.json  (3,1 kB)
│   ├── model-contract.json  (263,9 kB)
│   ├── r3f-snippets.md  (42,1 kB)
│   ├── review-dot1-01.md  (9,2 kB)
│   ├── review-plan-01.md  (27,4 kB)
│   ├── review-plan-02.md  (13,5 kB)
├── 08_method/  (12 file, 282,8 kB)
│   ├── BRIEF.md  (4,9 kB)
│   ├── BUILD-ANIM.md  (6,5 kB)
│   ├── BUILD.md  (4,0 kB)
│   ├── METHOD.md  (6,3 kB)
│   ├── tools/  (8 file, 261,0 kB)
│   │   ├── gx200_reference/  (4 file, 144,5 kB)
│   │   ├── ze_helpers.py  (55,1 kB)
│   │   ├── cmp.py  (1,6 kB)
│   │   ├── final_cmp.py  (1,4 kB)
│   │   ├── anim_helpers.py  (58,5 kB)
├── MANIFEST.csv  (40,1 kB)
```

Bản chụp (snapshot) của `web/` lấy lúc 2026-10-05 14:24: mỗi file được đọc một lần, sha256 tính trên đúng nội dung đã ghi vào zip.

## 7. Khoảng trống

### 7.1 Không có nguồn công khai, nên đã giả định

- **Cấu hình trục vít thật của KM** (loại, thứ tự, bước phần tử): dùng cấu hình theo logic quy trình PET không sấy (32 phần tử mỗi trục trong anim; 14 đoạn G trên tờ 02).
- **Bơm Maag extrex6 GU 100/125:** số răng, mô-đun, kích thước thân và công suất truyền động không công bố. Anim chọn 16 răng, m 7,8, rộng 125 để khớp 764 cm³/v; thân 450 × 530 × 460 mm, động cơ 45 kW là giả định.
- **Kết cấu trong khuôn chữ T:** ống phân phối, preland, thanh chắn, thanh nhiệt, chiều cao/sâu/khối lượng thân khuôn 2,4 m. Thân 450 mm chật nên móc áo trong anim gần chữ T và hàng vít thân đi qua ống phân phối (đơn giản hóa đã biết).
- **Bản vẽ chính thức ZE 155 UT:** chiều rộng, chiều cao, khung đế, hình khối và kích thước hộp số, miệng cấp liệu, kích thước bích và vỏ xi lanh, công suất nhiệt từng vùng.
- **Hãng và cao độ trục vào hộp số**, hãng và công suất động cơ thật trên ZE 155.
- **Dải năng suất chính thức của ZE 155** (chỉ suy ra từ ZE 180).
- **Một dây chuyền ZE 155 lắp khuôn chữ T thật:** không tìm thấy; cả chuỗi thiết bị sau máy đùn là tổ hợp hợp lý từ catalogue và brochure KM.
- **Cỡ cụm chân không cho PET không sấy 3,5 t/h** (lưu lượng hút, số cấp); mức chân không chỉ có nguồn độ tin cậy thấp (c062).
- **Ý nghĩa các chữ kích thước Gneuss** (B, D, E, F/G/H/I).
- **Nhiệt độ, áp suất, tốc độ vận hành** thực tế của dây chuyền: toàn bộ là giá trị điển hình có dấu `*`.
- **Mã màu RAL chính thức của KM** và vị trí thật (phía +Y hay −Y) của HMI và ống góp nước trên ZE UT cỡ lớn.

### 7.2 Không đưa vào zip, và lý do

| Không đưa vào | Lý do |
|---|---|
| `out/ze155.blend` (19,7 MB), `out/ze155_anim.blend` (29,5 MB) | Theo yêu cầu: không đưa file .blend. Mô hình được mô tả qua report, log, render |
| GLB trong `web/build/` (≈ 143 MB), `web/web-check/` (≈ 220 MB, có node_modules), `web/tools/` (node_modules), `web/Makefile` | Theo yêu cầu: không GLB, không node_modules; builder đang làm việc trong các thư mục này |
| `out/look/` (204 ảnh, ≈ 468 MB), `anim/look/` (95 ảnh, ≈ 54 MB) | Ảnh kiểm tra trung gian của vòng xem → so → sửa; nội dung đã được ghi thành chữ trong `out/log.md`, `anim/log.md` |
| `anim/tmp/` (23 file, ≈ 29 MB), `anim/render/` (rỗng) | File tạm của builder anim (script, bbox, bản kiểm đọc lại) |
| `anim/post/` (≈ 18 MB: pipeline Pillow vẽ HUD, video thử) | Đã bỏ khi đổi đích sang web (DECISIONS #29); chỉ còn để tham khảo bố cục |
| `anim/storyboard/S01…S16.png` (16 khung, ≈ 12 MB) và `make_storyboard.py` | Tờ tổng hợp `contact.png` đã chứa cả 16 khung; bỏ để giữ zip dưới ≈ 150 MB |
| 10 ảnh bằng chứng cỡ lớn của review mô hình `out/review/rev_*.png` (≈ 13 MB; giữ 4 ảnh cắt `rev_crop_*` và `review-model-01.md`) | Ảnh chụp trạng thái trước vòng sửa 4c; mô hình đã sửa thể hiện ở 11 ảnh render cuối. Bỏ để giữ zip dưới ≈ 150 MB |
| `drawings/views/check/` (24 ảnh kiểm), `design/draw/__pycache__/` | Ảnh kiểm tự động của `verify_views.py` (kết quả 68/68 đã ghi trong README) và cache Python |
| `design/build_parts.partial_die_edit.py` | Bản sửa khuôn dang dở, bị đổi tên để không ai chạy lại (DECISIONS #21); `parts.json` đóng băng là dữ liệu chuẩn |
| Transcript phiên GX200 và mọi transcript khác | Theo yêu cầu; chỉ ghi tên làm nguồn phương pháp |
| `web/dot1/A-to-B.md`, `web/dot1/B-to-A.md`, các script `web/dot1/*.py` | Ghi chú trao đổi giữa hai builder đang làm việc (xuất hiện trong lúc lập gói) và script prototype; không phải tài liệu kế hoạch |
| Bản gốc các data sheet, trang web trong `claims.jsonl` | Không có bản lưu trên máy (chỉ có trích dẫn trong claim); không tải lại vì gói này không dùng mạng |

## 8. Ngày tạo và cách làm

- Ngày tạo: 2026-10-05 14:24 (giờ máy). Người lập: agent biên soạn tài liệu (documentation compiler), chạy trên Claude Opus 5.5.
- Chỉ dùng file có sẵn trong `~/m3d-e2e/ze155-tdie/`; không truy cập mạng, không dùng Blender hay MCP. Chỉ ghi vào `docs-pack/`.
- Một script Python (chỉ thư viện chuẩn: `zipfile`, `hashlib`, `json`, `re`, `csv`) chọn file, đọc mỗi file một lần, tính sha256, ghi zip và `MANIFEST.csv`.
- Sổ giả định: phần "giả định chính" và các tóm tắt tiếng Việt do người lập gom tay từ các file nguồn; phần chi tiết `design.md` §5, các dòng `DESIGN-DEVIATION`, phụ lục `specs.md` và `shots.json` được trích tự động bằng biểu thức chính quy, có số dòng để kiểm lại.
- Số liệu trong báo cáo lấy từ chính các file nguồn ở thời điểm lập; nếu builder web sửa `web/` sau thời điểm snapshot thì bản trong zip là bản cũ hơn.
