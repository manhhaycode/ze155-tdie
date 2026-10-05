# Kế hoạch đưa mô hình ZE 155 lên web React Three Fiber

Bản 1.1: đã sửa theo `review-plan-01.md` và `review-plan-02.md`, đã gộp `ADDENDUM-discussion.md`. Vẫn chỉ là kế hoạch, chưa dựng gì.

- Dữ liệu máy đọc ở `model-contract.json` (contract 1.1); code mẫu ở `r3f-snippets.md`.
- Số liệu lấy từ hai lần kiểm chỉ đọc (read-only) trong Blender 5.2.2 ngày 2026-10-05. Lần hai là sau khi A1b xong: scene `ze155_anim` có 618 vật thể.

**Tóm tắt**
- **Đích chỉ là web R3F** (DECISIONS 29):
  - không làm MP4, không render khung, không làm overlay Pillow;
  - Blender chỉ làm những gì hiện được lên web;
  - dự án R3F của người dùng chưa có; sandbox `web/web-check/` chứng minh tương thích, sau đó chép component sang dự án thật.
- **Hai file GLB:**
  - `line.glb`: phần ngoài, khoảng 1,19 triệu tam giác, 189 thiết bị;
  - `interior.glb`: phần bên trong, khoảng 0,41 triệu tam giác, chỉ tải khi mở mặt cắt lần đầu (lazy-load).
- **Đơn vị chọn là thiết bị (device):** 190 thiết bị = 186 id của `parts.json` + 4 nhóm tổng hợp (cáp, băng tải, đầu đo).
- **Mặt cắt kiểu lai (hybrid):**
  - các trạng thái dạy học cố định dùng lại bản cắt sẵn của A1a/A1b;
  - mặt phẳng cắt chạy lúc runtime (clipping plane) với nắp tô mặt sau chỉ dùng cho mặt cắt tự do và cho những chỗ chưa có bản cắt sẵn.
- **Chuyển động:** 12 bộ phận quay, 3 clip glTF, lột vỏ (peel) lúc runtime, shader khối nhựa.
- **Làm theo 3 đợt (vertical slice) và 4 luồng song song:**
  - Đợt 1 xem được trên trình duyệt sau khoảng 2,5–3 h;
  - xong cả ba đợt sau khoảng 6–7 h thực (tốt nhất 5 h).
- **Cần người dùng duyệt 6 quyết định** (mục 9), trong đó Q6 là bản sao lưu phiên Blender trước khi làm.

---

## 1. Mục tiêu và tiêu chí "tương thích R3F"

**Mục tiêu:**
- Xoay quanh dây chuyền và bấm chọn từng thiết bị như trong Blender.
- Mở các mặt cắt cố định hoặc tự cắt.
- Xem vít quay và nhựa chảy.
- Chạy tour 16 shot.

**Máy đo:** máy này (Apple M3 Pro, Chrome, canvas 1920 × 1080). Mọi ngân sách đo ở **DPR 1**; khi mở `?selfcheck`, trang ép `dpr={1}`. Hook kiểm thử `window.__ze` ở mục 6.

| # | Tiêu chí | Cách kiểm |
|---|---|---|
| A1 | `line.glb` hiện khung đầu ≤ 6 s (localhost, cache trống). `interior.glb` tải ≤ 3 s sau lần mở mặt cắt đầu. 0 lỗi console. Không có request nào ra ngoài localhost. | network + console của chrome-devtools; `__ze.stats()` |
| A2 | **190 thiết bị:** 189 node `dev_*` trong `line.glb` + `dev_screws` trong `interior.glb`. Mỗi thiết bị có `device_id`, `name_vi`, `group`, `bbox_m`. 0 mesh mồ côi. Tên node không trùng giữa hai file. | `__ze.selfcheck()`; `tools/check_glb.py` |
| A3 | **Chọn kiểu Blender:**<br>• di chuột: viền sáng;<br>• bấm: viền cam + hộp bao (bbox) + bảng thông tin;<br>• bấm đúp hoặc F: zoom vừa thiết bị;<br>• Esc: bỏ chọn.<br>Cả 190 thiết bị chọn được bằng `select(id)`. | `clickAt` lên ≥ 10 thiết bị; vòng lặp `select` |
| A4 | **Chi tiết bên trong chọn được dưới thiết bị chủ.** Bấm phần tử vít thì chọn `screws`; Alt + bấm thì chọn `p_int_screw_elem_a_07`. | `clickAt` có Alt |
| A5 | **Mọi trạng thái cố định bật/tắt được:** FULL, GHOST_DRIVE, CUT_FEED, CUT_Z_BARREL, CUT_X2450, CUT_X4120, GHOST_SC, CUT_PUMP, CUT_DIE_PLAN, CUT_DIE_AA, ST1_Z_FULL.<br>• chuyển trạng thái ≤ 200 ms, đo lần vào thứ hai hoặc sau khi biên dịch trước (precompile);<br>• có nắp, không bao giờ hiện hai bản ở cùng một chỗ;<br>• bấm vào vùng đã bỏ thì chọn vật phía sau. | `setState` + ảnh chụp; `clickAt` |
| **A5b** | **Bấm vào mặt cắt (nắp) hoặc mặt trong nhìn thấy của một thiết bị đã cắt thì chọn đúng thiết bị đó.** Ví dụ: `barrel_b3` ở CUT_Z_BARREL và CUT_X2450, `feed_throat` ở CUT_FEED, `ctx_roll_middle` ở CUT_DIE_AA. | `__ze.capCheck(state, device)` |
| A6 | **Mặt cắt tự do:**<br>• trục X/Y/Z, thanh trượt, lật chiều;<br>• cắt cả hai file;<br>• lưới kín có nắp;<br>• chỉ hiện các bản đủ (full): không hiện ghost, marker hay bản cắt sẵn;<br>• van chỉ hiện khối nhựa CHẠY; bộ đĩa lọc bị ẩn (vành đĩa nhô qua vỏ ngoài);<br>• vùng đã cắt không bấm trúng được, còn nắp thì bấm trúng được;<br>• rời FREE thì trả lại đúng FULL hoặc trạng thái cố định trước đó. | `setFreeClip` + ảnh chụp + `capCheck` + `cutRoundTrip` |
| A7 | **12 bộ phận quay đúng trục và đúng chiều:**<br>• vít cùng chiều;<br>• bánh răng bơm ngược chiều nhau;<br>• trục cán +/−/+;<br>• hộp số sơ đồ ×3,73;<br>• khớp nối.<br>Có các chế độ tắt / chậm / thực. Sau 1 s, góc khớp 2π·rpm/60/hệ số chậm, sai ≤ 5 %. | `__ze.rotors()` |
| A8 | **Shader khối nhựa (Đợt 2):** pha hạt chuyển sang hổ phách giữa X 1,52 và 1,90 m, vân trôi; có chế độ nhiệt độ; 0 lỗi shader. | ảnh CUT_Z_BARREL ở hai chế độ |
| A9 | **3 clip phát qua `useAnimations`:**<br>• `valve_run`: chốt đi 0,20 m, khối nhựa đổi từ XẢ sang CHẠY;<br>• `sc_index`: 12 bước × 30°, piston xả ngược chạy sau mỗi bước;<br>• `die_open`: các đích nhấc 0,90 m và nhìn thấy được trong suốt clip. | `playClip` + vị trí node |
| A10 | **`tour.json` lái `CameraControls` (Đợt 3):**<br>• 16 shot + 7 ảnh tĩnh;<br>• trạng thái FLOWS quy về FULL;<br>• camera dừng lệch ≤ 1 cm. | `__ze.tour(i)` |
| A11 | **Hiệu năng:**<br>• FULL ≥ 55 fps, trạng thái cắt ≥ 45 fps, mặt cắt tự do ≥ 40 fps;<br>• draw call ≤ 1 000 / 1 150 / 1 350;<br>• tam giác hiện ≤ 1,5 triệu;<br>• heap ≤ 600 MB.<br>**Mục tiêu mềm** (chỉ báo cáo, không chặn nghiệm thu): giảm CPU 4× vẫn ≥ 30 fps ở FULL. | trace + `__ze.stats()` |
| A12 | `line.glb` ≤ 15 MB, `interior.glb` ≤ 6 MB (meshopt). | `check_glb.py` |

---

## 2. Hiện trạng

| Hạng mục | Số liệu |
|---|---|
| Scene `ze155` | 610 vật thể (284 mesh + 59 curve cần render, 73 camera); 1 250 266 tam giác; bỏ vít cũ và sàn còn **1 188 402** |
| Scene `ze155_anim` | **618 vật thể** = 343 liên kết + 275 của anim. A1b đã xong và đã lưu `out/ze155_anim.blend` |
| Primitive (draw call) | 927; ghép trong từng thiết bị chỉ còn 782 (−16 %) |
| Thông tin thiết bị | 0 custom property. Ghép vật thể với thiết bị: 177 trùng tên, 166 theo quy tắc (bảng `object_to_device`) |
| Gốc toạ độ | 337/343 vật thể có gốc ở (0, 0, 0), nên trục quay cần empty riêng. A1b đã có sẵn empty trục cho trục cán, bánh răng bơm, đĩa lọc, hộp số sơ đồ |
| Modifier | Bevel 257, Weighted Normal 262, Boolean 9, Array 6, Solidify 2 → xuất với `export_apply` |
| Lưới kín (quy tắc mới, mục 3.3) | **Ngoài:** 269/343 kín; 74 hở (59 curve + 15 mesh); 0 mặt lật; 0 lưới lộn trong ra ngoài.<br>**Trong:** 100/130 kín; 30 hở (khối nhựa hở đầu, 2 mặt cắt A-A, `int_pump_body_lo`); 1 lưới có 3 cạnh lật |
| Bên trong | **A1a ≈ 252 nghìn tam giác:**<br>• vít: 64 phần tử dùng chung 10 mesh;<br>• thân rỗng, vòm, cột cấp liệu;<br>• 9 khối nhựa + các bản `_lo` / `x2450` / `x4120`;<br>• vít cắt sẵn + nắp biên dạng có đĩa trục Ø72.<br>**A1b ≈ 160 nghìn tam giác:**<br>• đầu xi lanh, van, adapter;<br>• đĩa lọc, bơm (nửa cắt + `_full`);<br>• ống/trộn tĩnh (bản cắt nhiều lớp `_lo` / `_y0`);<br>• khuôn (mặt dưới, mặt cắt A-A có shape key);<br>• hộp số sơ đồ, ghost lọc và ghost hộp số, đầu đo, vạch trên trục cán |
| Bộ xuất glTF | io_scene_gltf2 5.2.40:<br>• `export_apply` dùng depsgraph theo context;<br>• `Mesh.validate()` sửa trực tiếp mesh gốc của vật thể được xuất;<br>• NLA_TRACKS gộp các track cùng tên;<br>• chỉ xuất driver của shape key |
| Giới hạn MCP | socket ngắt sau 180 s, còn Blender vẫn chạy tiếp lệnh đang dở |

**Vật liệu cần xử lý ở web** (bảng đủ trong contract `materials`):

| Vật liệu | Vấn đề | Ở web |
|---|---|---|
| `ze_sheet_pet`, `ze_melt_curtain` | Mix + Transparent, xuất ra đục | ghi đè theo tên |
| `za_ghost_vent` (ghost vòm, lọc, hộp số) | alpha lấy từ Layer Weight | GhostMaterial |
| `za_fill_melt` | trong mờ | Đợt 1: giữ amber; Đợt 2: FillMaterial |
| `za_sc_screenpack`, `za_sc_breaker` | thủ tục + prop `dirt` | ghi đè PBR phẳng |
| `ze_blue_cast`, `ze_chequer` | mất bump | PBR phẳng |
| `ze_floor` | thủ tục | không xuất |
| Mọi vật liệu | `doubleSided: true` | đặt lại `side` theo cờ `closed` |

---

## 3. Model contract (tóm tắt)

### 3.1 Toạ độ
- Mét, trục +Y lên. Đổi toạ độ Blender sang three.js: `(x, y, z) → (x, z, −y)` (`export_yup`).
- Giữ gốc Blender: X = 0 ở mặt B1 phía hộp số, sàn ở Y = 0, phía người vận hành nằm về −Z.
- Phép quay quanh trục a trong Blender bằng phép quay quanh M·a; trục +Y của Blender thành `[0, 0, −1]`.

### 3.2 Cây node
- Tên chỉ dùng `[a-z0-9_]` và không trùng giữa hai file.
- Mesh con của một Group nhiều vật liệu mang tên **mesh glTF** (tên data, đổi thành `m_<node>`), không phải tên node. Bảng tra chỉ đánh chỉ mục những node có `userData.kind`.

```
line.glb      ze155_line ─ sec_<nhóm> (10) ─ dev_<id> (189) ─ p_<vật thể>   (mesh lá)
                                                          ├─ rot_<tên> ─ p_*   (trục động cơ, 2 khớp nối, 3 trục cán + vạch)
                                                          └─ anim_<tên> ─ p_*  (bu-lông, hộp nhiệt nửa khuôn trên: đích die_open)
interior.glb  ze155_interior ─ dev_screws (transform đơn vị, ngoại lệ có ghi) ─ rot_screw_a|b ─ phần tử, trục then hoa, bản cắt sẵn, bánh răng ra
                              │                                               └─ p_int_fill_screw_*  (không quay)
                              └─ ih_<thiết bị chủ> ─ p_int_* | rot_pump_gear_* | rot_gbx_* | anim_valve_bolt | anim_sc_disc | anim_sc_piston | anim_die_choker_bar
```

**Quy tắc:**
- Mesh là lá và không chuyển động. Thứ gì chuyển động là empty.
- Không chuyển node từ file này sang file kia; `device_id` trên từng node bên trong nối nó với thiết bị chủ.

### 3.3 userData, lưới kín

| Loại (`kind`) | Khoá bắt buộc |
|---|---|
| `device` | `device_id`, `name_vi`, `name_en`, `group`, `bbox_m[6]`, `synthetic` |
| `part` | `device_id`, `src`, `closed`, `ax_group`; tuỳ chọn `cap` = `auto` / `force` / `none` |
| `interior` | `device_id` (thiết bị chủ), `src`, `closed`, `role` = `full` / `cut_only`, `states[]` |
| `rotor` | `device_id`, `axis[3]`, `rpm` (có dấu), `display_slow`, `pivot_m`, `label_vi` |
| `anim_target`, `fill`, `ghost`, `marker`, `int_host`, `section`, `root` | xem `node_kinds` trong contract |

**`closed` (I6):**
- **Điều kiện:**
  - không có cạnh biên (cạnh chỉ có 1 mặt);
  - mọi cạnh 2 mặt có hướng mặt nhất quán (`is_contiguous`);
  - thể tích có dấu > 0, tức pháp tuyến hướng ra ngoài.
- Cạnh 3+ mặt (các vỏ chạm nhau) vẫn được tính là kín. Vì vậy `int_feed_column_hollow` (57 cạnh 4 mặt) vẫn có nắp.
- **Hiển thị:**
  - lưới kín: FrontSide;
  - lưới hở hoặc có mặt lật: DoubleSide có chiếu sáng, không có nắp;
  - `cap: force` cho phép dùng nắp với lưới gần kín (ví dụ trục cán) sau khi kiểm bằng mắt.

### 3.4 Vật liệu
- 49 + 24 vật liệu Principled xuất 1:1.
- Danh sách ghi đè ở mục 2.
- **Màu nắp:**
  - **bản cắt sẵn** dùng vật liệu nắp có sẵn `za_cap_*` (thép đỏ gạch, vít, bánh răng xám, dây nhiệt đồng, cách nhiệt be, vỏ bọc);
  - **nắp runtime** dùng `cap_colors`: thép `#B84533` có gạch chéo, vít `#99362A`, cao su `#3A3A3A`, cách nhiệt `#BFB89E`, nhựa `#ED9E38`.

### 3.5 Mặt cắt (hybrid) và chọn trong mặt cắt

**Mô hình theo trạng thái (I2, I3, I7):** mỗi trạng thái có các danh sách sau.

| Khoá | Ý nghĩa |
|---|---|
| `hide` | node bị ẩn |
| `swap` | `{node ngoài: [node trong]}`: ẩn node ngoài, hiện các node trong. Nếu node trong không có trong file (ví dụ ở Đợt 1), giữ node ngoài và cắt nó |
| `clip` | node cắt runtime bằng mặt phẳng của trạng thái |
| `show_whole` | node trong hiện nguyên, không cắt: bản cắt sẵn, vít nguyên, ghost, marker |
| `show_clipped` | node trong hiện và cắt runtime |
| `ghost` | node vẽ bằng GhostMaterial, không bấm chọn được |
| `peel`, `clips_on_enter` | lột vỏ runtime; clip phát khi vào trạng thái |

**Không bao giờ hiện hai bản ở cùng một chỗ:** bản `full` với bản `cut_only`, node ngoài với bản cắt sẵn của nó.

| Trạng thái | Đợt | Dùng bản cắt sẵn (A1a/A1b) | Cắt runtime |
|---|---|---|---|
| CUT_FEED | 1 | – | cột cấp liệu rỗng (kín); dự phòng là `_y0` làm bằng `za.cut_copy` |
| CUT_Z_BARREL | 1 | **vít nguyên**, khối nhựa `_lo`, đầu xi lanh, van, adapter lọc `_lo`, ghost vòm, cửa sổ tím | 6 thân rỗng, vỏ che, vỏ nhiệt, mặt bích, cáp |
| CUT_X2450 / CUT_X4120 | 1 | phần tử 12/22 cắt sẵn + nắp biên dạng có đĩa trục Ø72 + mặt đầu khối nhựa sạch. Các phần tử sau mặt cắt bị ẩn | B3/B5 rỗng, vòm 2, vỏ, cáp |
| GHOST_DRIVE | 2 | ghost hộp số (A1b), hộp số sơ đồ quay | lantern và vỏ khớp nối ghost runtime |
| GHOST_SC | 2 | `anim_ghost_sc` (nắp đã nâng), đĩa, lưới, kênh, piston. Vỏ lọc ngoài bị ẩn | – |
| CUT_PUMP | 2 | `int_pump_body_cut` + 2 nửa bánh răng (+ túi nhựa) + adapter và khối nhựa `_y0`. **Không hiện `int_pump_body_hollow`, không hiện bánh răng `_full`** | cảm biến P3/P4, băng nhiệt |
| CUT_DIE_PLAN | 2 | `int_die_lower_face` + `int_fill_die_lo`, adapter `_lo`, thanh chặn (đi theo `die_open`). **Nhóm nửa trên không bị ẩn hay cắt; `die_open` nhấc nó lên** | tấm đầu khuôn, deckle |
| CUT_DIE_AA | 2 | 2 nửa khuôn A-A (shape key `gap_x10`/`lip_push`), bu-lông nhiệt, thanh chặn, adapter, **ống/trộn cắt nhiều lớp**, khối nhựa `_y0`, vạch `_aa` | trục cán (nắp `force` nếu đạt), khung, xe khuôn. Đầu bu-lông thân khuôn bị ẩn |
| ST1_Z_FULL | 2 | như Z_BARREL + bộ `_lo` của đường chảy, mặt khuôn dưới, ghost lọc + đĩa nguyên | thân rỗng, bánh răng `_full` (cắt khi đang quay) |
| FREE | 1 | – | mọi thứ (mặt phẳng chung). Thay chi tiết theo `free_swap`; chỉ hiện bản `full`. **Ẩn** (`FREE.hide`): khối nhựa XẢ của van, nên chỉ hiện bộ CHẠY (bộ XẢ chỉ hiện khi `valve_run` chạy); bộ đĩa lọc (đĩa, 12 lưới, khối nhựa hốc), vì vành đĩa nhô 67–190 mm qua vỏ lọc ngoài. Chọn ẩn đĩa vì đơn giản nhất; GHOST_SC và ST1 vẫn hiện đĩa dưới nắp ghost đã nâng |

**Chọn trong mặt cắt (C1):**
- R3F chỉ giữ điểm trúng gần nhất của mỗi mesh, và việc này xảy ra *trước* `events.filter`. Vì thế bộ lọc phải nằm **trong `mesh.raycast`**:
  - bỏ điểm trúng ở bên đã cắt (theo mặt phẳng cục bộ và mặt phẳng chung);
  - bỏ vật đang ẩn và vật đang ghost;
  - với empty đang ẩn, `raycast` trả `false` để three.js bỏ qua cả nhánh con.
- Bản vật liệu cắt dùng DoubleSide. Khi bấm vào nắp, tia trúng mặt sau của chính lưới đó, nên chọn đúng thiết bị (A5b).
- **Không dùng drei `<Bvh>`:** khi dọn effect (StrictMode chạy việc này một lần ở dev, hoặc lúc unmount), nó đặt lại `raycast = Mesh.prototype.raycast` và làm mất bộ lọc. `installRaycastFilter` tự dựng BVH (mỗi geometry một lần, kể cả geometry dùng chung) và là nơi duy nhất gán `mesh.raycast`. Việc kiểm "đã gắn" so khớp hàm, không dùng cờ `userData`, nên chạy lại bao nhiêu lần cũng được. `selfcheck().rayUnfiltered` phải bằng 0, kể cả khi chạy `npm run dev`.
- **Mọi thay đổi hiển thị** của trạng thái cắt, FREE và công tắc khối nhựa van đều đi qua `setVisible` có ghi lại, nên `resetCuts` trả lại đúng trạng thái lúc tải. Rời FREE thì về đúng FULL hoặc trạng thái cố định (kiểm bằng `__ze.cutRoundTrip()`).

### 3.6 Bộ phận quay (12)

| Node | Trục (three) | rpm thực | Chậm | Nguồn trong Blender |
|---|---|---|---|---|
| `rot_screw_a`, `rot_screw_b` | [1, 0, 0] | −300 | 20 | `int_screw_axis_a/b` |
| `rot_gbx_input` / `rot_gbx_counter` | [1, 0, 0] | −1 118 / +571 | 20 | gốc của các bánh răng hộp số sơ đồ (A1b); bánh răng ra quay theo vít |
| `rot_pump_gear_top` / `_bottom` | [0, 0, −1] | +69 / −69 | 4 | gốc của `int_pump_gear_*` (con: nửa cắt, `_full`, túi nhựa) |
| `rot_roll_bottom` / `_middle` / `_top` | [0, 0, −1] | +9,95 / −9,95 / +9,95 | 1 | `anim_roll_axis_*` (A1b) + bản sao trục cán + vạch |
| `rot_motor_shaft`, `rot_flex_coupling`, `rot_safety_coupling` | [1, 0, 0] | −1 119 | 20 | empty mới tại Z 1,2 |

### 3.7 Khối nhựa
- Shader lấy toạ độ X thế giới: pha, vân trôi theo bước vít, nhiệt độ. Không thêm thuộc tính đỉnh.
- 9 vùng vít và 17 đoạn đường chảy mang tên thật của A1b, có `x_range_m` đo từ bbox.
- Khuôn dùng chế độ `radial`.
- Khối nhựa là lưới hở, nên không có nắp. Mặt đầu sạch lấy từ các bản `_lo` / `_y0` / `x*`.

### 3.8 Clip (3)

| Clip | Đích | Nội dung |
|---|---|---|
| `valve_run` | `anim_valve_bolt` | z +0,20 → 0 trong 1,2 s. Khi chạy hiện khối nhựa XẢ; khi xong và lúc nghỉ hiện khối nhựa CHẠY |
| `sc_index` | `anim_sc_disc` + `anim_sc_piston` | đĩa +30° mỗi 3 s, 12 bước = 360° lặp liền; piston xả ngược đi 60 mm rồi về sau mỗi bước |
| `die_open` | 9 thiết bị nửa trên + 2 `anim_*_top` (`line.glb`) + `anim_die_choker_bar` (`interior.glb`) | +0,9 m trong 2,4 s. Hai file mỗi file một action cùng tên. Đích không bao giờ bị ẩn hay cắt |

- Lột vỏ là code runtime, không phải clip glTF.
- Shape key `gap_x10` / `lip_push` (CUT_DIE_AA) điều khiển bằng `morphTargetInfluences`.

### 3.9 Chia file, nén

**Nén:**
- **EXT_meshopt_compression + KHR_mesh_quantization**, làm bằng gltf-transform 4.5.1.
- Không dùng Draco, không dùng KHR_meshopt.
- Không dùng `optimize` mặc định, không dùng `gltfjsx --transform`.

**Instancing, LOD:**
- Không dùng instancing. Ở web, 64 phần tử vít dùng chung 10 mesh, 12 lưới lọc dùng chung 1 mesh.
- Không dùng LOD.

**Ghép mesh** (`join({ filter })`) chỉ là dự phòng nếu thiếu fps.

**Dữ liệu đi kèm:**
- `devices.json`;
- `tour.json`;
- `cut_states.json`: sinh từ contract và tên node thật, **dừng lỗi nếu có tên không khớp**;
- `standin.glb`: GLB tổng hợp đúng contract, cho luồng B dùng từ đầu.

---

## 4. Đợt, luồng, ràng buộc

### 4.1 Ba đợt (vertical slice)

| Đợt | Blender (luồng A) | Web | Trạng thái, chuyển động |
|---|---|---|---|
| **1** | • `line.glb` đủ 189 thiết bị, pivot ngoài (trục động cơ, khớp nối, trục cán), đầu đo, vạch;<br>• `interior.glb` phần xi lanh: vít + bản cắt sẵn, thân rỗng, vòm, cột cấp liệu, 9 khối nhựa (+ `_lo`, `x*`), ghost vòm, cửa sổ tím, và **bộ đầu xi lanh/van/adapter lọc `_lo`** mà CUT_Z_BARREL cần | tải, chọn kiểu Blender, viền, bbox, zoom, bảng thông tin, cắt + nắp, chọn trong mặt cắt, quay | FULL, CUT_FEED, CUT_Z_BARREL, CUT_X2450, CUT_X4120, FREE; quay vít, động cơ, trục cán; lột vỏ |
| **2** | • `interior.glb` đủ: đường chảy, lọc, bơm, ống/trộn, khuôn, hộp số sơ đồ, ghost;<br>• `line.glb` xuất lại có track `die_open`;<br>• 3 clip | shader khối nhựa, đổi khối nhựa van, shape key, ghost | GHOST_DRIVE, GHOST_SC, CUT_PUMP, CUT_DIE_PLAN, CUT_DIE_AA, ST1; quay bơm, hộp số; `valve_run`, `sc_index`, `die_open` |
| **3** | – (không cần Blender) | tour `tour.json` (16 bước, 7 ảnh tĩnh), nhãn `Html`, HUD, dải cấu hình vít, **sơ đồ khối vòng điều khiển 2D (S15)**, tuỳ chọn cho đầu đo chạy qua lại | dùng lại toàn bộ |

**Để sang v2:** dòng chảy 3D S14, cung vòng điều khiển 3D, hạt, bọt.

### 4.2 Bốn luồng song song

Mỗi lúc chỉ một agent dùng Blender; tối đa khoảng 4 agent cùng lúc.

| Luồng | Việc |
|---|---|
| **A: Blender** (tuần tự, qua MCP) | W0 (fingerprint, bản sao lưu nếu Q6 được duyệt) → W1 + W2 Đợt 1 → W1 + W2 Đợt 2. Script `tools/w1_build.py` **chạy lại được**: chỉ xoá và dựng lại những vật nó sở hữu trong `ze155_web` |
| **B: lõi web** | sandbox trên `standin.glb` (GLB tổng hợp, đúng contract) từ phút đầu; thay bằng GLB thật khi `check_glb.py` báo qua |
| **C: dữ liệu và công cụ** (không cần Blender) | `standin.glb`, `devices.json`, `tour.json`, `make_cut_states.py`, script nén, `check_glb.py`; sau đó UI tour, nhãn, HUD, dải vít, sơ đồ khối (Đợt 3) |
| **D: review** | một reviewer độc lập cho mỗi đợt, kiểm trong Chrome bằng chrome-devtools MCP; fixer riêng sửa lỗi. Reviewer không sửa |

**Quy tắc chồng lấp:**
- Review đợt N chạy song song với việc dựng đợt N+1; fixer sửa lỗi đợt N cùng lúc.
- Riêng review và sửa của đợt cuối thì làm tuần tự.
- Mỗi lần xuất GLB đều phải qua `check_glb.py` trước khi luồng B tích hợp.

### 4.3 Ràng buộc
- Không chạy Blender nền (`blender -b`). Không dùng tool MCP `export_scene`; xuất bằng `bpy.ops.export_scene.gltf` trong `execute_blender_code` (chờ Q1).
- **Không sửa tại chỗ** vật thể, mesh hay vật liệu của `ze155` và `ze155_anim`. Bản sao web có mesh data riêng.
- Không bao giờ chỉnh `unit_settings` của scene nào (sự cố C0). Scene cửa sổ không bao giờ là `ze155`.
- Chỉ lưu bằng `libraries.write` ra file riêng. Ngoại lệ duy nhất là bản sao lưu phiên ở Q6, nếu người dùng duyệt.
- Người dùng không bấm Ctrl+S.
- Driver xem trước trong Blender chỉ đặt trên empty `rot_*` của `ze155_web`, chỉ dùng biểu thức đơn giản theo `frame`, và bị tắt khi xuất. Không bao giờ thêm driver vào `ze155_anim`.

---

## 5. Các bước W0–W2

**Điều kiện:** chỉ một agent Blender; bắt đầu bằng `get_addon_status` và `get_scene_info`; ghi log vào `web/build/log.md`.

| Bước | Đợt | Việc | Nghiệm thu |
|---|---|---|---|
| W0 | 1 | **Fingerprint trước:** vật thể của `ze155` và `ze155_anim`, số đỉnh và số mặt của từng mesh, vật liệu, cài đặt scene, ghi `build/reports/fp_before.json`. Bản sao lưu phiên nếu Q6 được duyệt (mục 9) | file có; `ze155` 610/73, `ze155_anim` 618 |
| W1.1 | 1 | (C) `standin.glb`, `devices.json`, `tour.json`, `make_cut_states.py`, `check_glb.py`, script nén | standin qua `check_glb.py`; 186 + 4 thiết bị; 17 camera, 7 ảnh tĩnh |
| W1.2 | 1 | `bpy.data.scenes.new('ze155_web')` (không đụng unit), các collection `web_line`, `web_interior`, `web_helpers` | fingerprint không đổi |
| W1.3 | 1 | root, 10 `sec_*`, 189 `dev_*` ở tâm bbox, kèm extras | 189 node, đủ khoá |
| W1.4 | 1 | **Bản sao phần ngoài:**<br>• `obj.copy()`, rồi **`obj.data = obj.data.copy()`** (mesh data riêng, đổi tên `m_<node>`);<br>• giữ modifier, gắn cha là `dev_*` mà không đổi toạ độ thế giới, `animation_data_clear()`;<br>• tách băng nhiệt (6) và bu-lông, hộp nhiệt khuôn (trên/dưới) từ **`new_from_object(evaluated)`** (đã áp modifier, mesh mới);<br>• tính `closed` theo quy tắc mới;<br>• ghi danh sách lưới hở nằm trong danh sách `clip` | 358 `p_*` (340 ngoài − 3 nguồn tách + 10 phần tách + 11 vật ngữ cảnh A1b: 2 đầu đo, 9 vạch trục cán); bbox thế giới khớp ≤ 0,1 mm; mesh của `ze155` không đổi số đỉnh |
| W1.5 | 1 | Pivot ngoài: `rot_motor_shaft`, `rot_flex_coupling`, `rot_safety_coupling`, `rot_roll_*` (chép từ `anim_roll_axis_*`, kèm trục cán + vạch); đầu đo vào `x_thickness_scanner`; `anim_die_*_top` bọc phần tách nửa trên | quay thử 90° thì tâm lệch ≤ 0,5 mm; trả về 0 |
| W1.6 | 1 / 2 | **Bản sao bên trong** theo trường `slice` của `interior_export.items` (Đợt 1 chép các mục `slice: 1`; Đợt 2 thêm các mục `slice: 2`):<br>• mỗi mesh riêng được chép một lần (vít: 10 mesh dùng chung trong các bản web; lưới lọc: 1 mesh);<br>• empty bọc: `anim_valve_bolt`, `anim_sc_disc`, `anim_sc_piston`, `anim_die_choker_bar`, `rot_pump_gear_*`, `rot_gbx_*`;<br>• `dev_screws`, `ih_<chủ>`; ghi `role` và `states` | mọi node có `device_id` thật; vít 64/10; transform khớp bản anim |
| W1.7 | 2 | Prop khối nhựa (`fills`); giữ shape key (bản sao A-A không có modifier) | đủ khoá; 4 node có morph target |
| W1.8 | 2 | NLA: `valve_run`, `sc_index` (đĩa + piston), `die_open` (track trên `dev_*` / `anim_*_top`, và `anim_die_choker_bar`) | tính thử khung cuối: 0,20 m; 360° + piston 60 mm; 0,90 m |
| W1.9 | tuỳ chọn | Driver xem trước trên `rot_*` (biểu thức `frame` đơn giản) để bấm Play trong Blender | Play chạy; driver nằm trong danh sách để tắt khi xuất |
| W1.10 | 1 / 2 | Prop root; kiểm tên; lưu `out/ze155_web.blend` (`libraries.write`) rồi đọc lại bản chép | đếm khớp |
| W2.1 | 1 / 2 | **Mỗi file GLB một lệnh MCP:**<br>(a) làm nóng (warm-up): chuyển scene, `evaluated_depsgraph_get()`, đo thời gian;<br>(b) `line.glb`;<br>(c) `interior.glb`;<br>(d) fingerprint sau, so với trước.<br>Mỗi lệnh có `try/finally`, ghi `build/raw/<tên>.done.json` (thời gian, dung lượng, lỗi). Nếu một lệnh > 150 s, lần sau xuất `line.glb` theo nhóm (`line_a`, `line_b`) | file trên đĩa khớp `done.json`; fp_before = fp_after |
| W2.2 | 1 / 2 | (C) nén (lệnh ở dưới) | `validate` 0 lỗi; ≤ 15 / 6 MB |
| W2.3 | 1 / 2 | (C) `check_glb.py` (tên, `kind` + khoá, mesh lá, `device_id`, tam giác, primitive, animation, vật liệu ghi đè); `make_cut_states.py` | 0 lỗi, 0 tên không khớp, rồi mới chuyển cho B |

**Một lệnh xuất** (W2.1 b/c, đổi `NAME`):

```python
import bpy, json, time, os
WEB = '/Users/manhhaycode/m3d-e2e/ze155-tdie/web/'
NAME = 'line'                      # 'line' hoặc 'interior': mỗi lệnh MCP chỉ một file
COMMON = dict(export_format='GLB', check_existing=False, use_active_scene=True,
    export_extras=True, export_apply=True, export_yup=True, export_cameras=False, export_lights=False,
    export_materials='EXPORT', export_image_format='NONE', export_texcoords=False, export_normals=True,
    export_tangents=False, export_attributes=False, export_vertex_color='NONE', export_morph=True,
    export_morph_normal=True, export_animations=True, export_animation_mode='NLA_TRACKS',
    export_force_sampling=True, export_frame_step=1, export_anim_slide_to_zero=True,
    export_optimize_animation_size=True, export_current_frame=False, export_hierarchy_flatten_objs=False,
    export_gpu_instances=False, export_draco_mesh_compression_enable=False,
    export_meshopt_compression_enable=False, export_use_gltfpack=False, will_save_settings=False)
win = bpy.context.window; prev = win.scene; t0 = time.time(); res = {'name': NAME, 'ok': False}; muted = []
try:
    ws = bpy.data.scenes['ze155_web']; win.scene = ws          # depsgraph theo context phải là ze155_web
    for o in ws.objects:                                       # tắt driver xem trước, rotor về 0
        ad = o.animation_data
        if ad:
            for fc in ad.drivers:
                if not fc.mute: fc.mute = True; muted.append(fc)
        if o.name.startswith('rot_'): o.rotation_euler = (0.0, 0.0, 0.0)
    ws.frame_set(1)
    out = WEB + f'build/raw/{NAME}.glb'
    bpy.ops.export_scene.gltf(filepath=out, collection=f'web_{NAME}', **COMMON)
    res.update(ok=True, bytes=os.path.getsize(out))
except Exception as e:
    res['error'] = repr(e)
finally:
    for fc in muted: fc.mute = False
    win.scene = prev
    res['seconds'] = round(time.time() - t0, 1)
    json.dump(res, open(WEB + f'build/raw/{NAME}.done.json', 'w'))
print(res)
```

- **Khi lệnh MCP quá 180 s:** không chạy lại ngay. Chờ đến khi `get_scene_info` trả lời, đọc `done.json`, rồi mới quyết định.

**Nén** (W2.2; dùng hàm nên chạy được cả bash lẫn zsh):

```bash
cd /Users/manhhaycode/m3d-e2e/ze155-tdie/web
gt() { npx -y @gltf-transform/cli@4.5.1 "$@" --vertex-layout separate; }
mkdir -p build/tmp build/reports web-check/public/models
for f in line interior; do
  gt dedup   build/raw/$f.glb  build/tmp/$f.1.glb --materials false
  gt prune   build/tmp/$f.1.glb build/tmp/$f.2.glb --keep-leaves true --keep-attributes false
  gt meshopt build/tmp/$f.2.glb web-check/public/models/$f.glb --level high
  gt validate web-check/public/models/$f.glb > build/reports/$f.validate.txt
done
python3 tools/check_glb.py web-check/public/models/*.glb > build/reports/check.json
python3 tools/make_cut_states.py model-contract.json web-check/public/models/*.glb web-check/public/data/cut_states.json
```

- **Chuỗi lệnh đã thử** trên GLB tổng hợp: giữ cây node, extras, empty lá và tên vật liệu. Quantize đổi TRS của node mesh, nên mesh phải là lá và không chuyển động.

---

## 6. Sandbox `web/web-check/`

**Tính năng:**
- Tải `line.glb` ngay; `interior.glb` khi lần đầu mở mặt cắt, ghost hoặc mặt cắt tự do.
- BVH dựng trong `installRaycastFilter` (không dùng drei `<Bvh>`), bộ lọc trong `mesh.raycast`.
- Cây thiết bị tìm được bằng tiếng Việt.
- Bảng thông tin lấy từ `devices.json`.
- **Chọn:**
  - di chuột: viền 2 px;
  - bấm: viền cam 3 px + `Box3Helper`;
  - bấm đúp hoặc F: `fitToBox`;
  - Alt + bấm: chọn chi tiết;
  - Esc: bỏ chọn.
- Thanh công cụ: trạng thái, mặt cắt tự do, quay, khối nhựa, 3 clip, tour.
- HUD, nhãn `Html`. Toàn bộ chữ trên giao diện là tiếng Việt.
- `Environment` dựng bằng `Lightformer`, không dùng CDN.
- Biên dịch trước các trạng thái sau khi `interior.glb` tải xong.
- **`window.__ze`:**

  | Hàm | Việc làm |
  |---|---|
  | `ready` | promise, xong khi đã tải |
  | `stats` | fps, draw call, tam giác, số thiết bị |
  | `devices` | danh sách thiết bị |
  | `select` | chọn thiết bị |
  | `clickAt` | phát PointerEvent thật lên canvas |
  | `pickAt` | thiết bị dưới một điểm màn hình |
  | `capCheck` | kiểm A5b |
  | `project` | toạ độ màn hình của thiết bị |
  | `setState`, `setFreeClip` | áp mặt cắt |
  | `cutRoundTrip` | FULL → FREE → FULL và mỗi trạng thái cố định → FREE → chính nó phải cho cùng tập node đang hiện |
  | `rotors`, `playClip`, `tour`, `orbitTest` | chuyển động, tour, đo hiệu năng |
  | `selfcheck` | báo cáo đối chiếu contract, gồm `rayUnfiltered` (số mesh mất bộ lọc raycast, phải bằng 0) |

**Cấu trúc:** như bản 1.0; thêm `src/scene/Picking.ts` (bộ lọc raycast) và `src/scene/Cuts.ts` theo mô hình hybrid.

**Thư viện** (`npm view` ngày 2026-10-05):

| Gói | Phiên bản | Ghi chú |
|---|---|---|
| react, react-dom | 19.3.0 | R3F 9.8 yêu cầu `>=19 <19.4` |
| three / @types/three | 0.186.1 / 0.186.0 | |
| @react-three/fiber | 9.8.1 | |
| @react-three/drei | 10.7.9 | `Outlines` dùng `screenspace={false}` cho độ dày tính bằng pixel |
| three-mesh-bvh | **0.8.3** (import trực tiếp `acceleratedRaycast`) | đúng range của drei; không dùng 0.9.x |
| zustand | 5.0.15 | |
| vite, @vitejs/plugin-react | 8.3.2, 6.1.1 | mẫu `react-ts` của create-vite 9.2.1 |
| typescript | theo mẫu | snippet qua `tsc --strict` 5.9.3 |

**Reviewer kiểm** (chrome-devtools MCP):
1. Chạy `npm run dev -- --port 5178 --strictPort`.
2. Mở `?selfcheck=1`, kiểm `selfcheck()` (`rayUnfiltered` = 0 ngay trong `npm run dev`) và `cutRoundTrip()` (`ok: true`).
3. Kiểm network chỉ có localhost, console 0 lỗi.
4. Chụp ảnh từng trạng thái; so với `anim/storyboard/S*.png` và `anim/look/A1*`.
5. Gọi `clickAt` / `capCheck`, rồi kiểm số A7, A9, A10.
6. Trace hiệu năng và `stats()` ở FULL, ở một trạng thái cắt, ở mặt cắt tự do; thêm lần đo giảm CPU 4× (mục tiêu mềm).
7. Trong Blender chỉ đọc: fingerprint.

---

## 7. Rủi ro và cách giảm

| Rủi ro | Cách giảm |
|---|---|
| Chọn trúng phần đã cắt, hoặc không chọn được nắp | lọc trong `mesh.raycast` + bản vật liệu DoubleSide + empty ẩn trả `false` (mục 3.5); không dùng drei `<Bvh>` để bộ lọc không mất khi StrictMode dọn effect; có A5b và `rayUnfiltered` |
| Viền chọn to bất thường hoặc bị chọn trúng | `screenspace={false}` (độ dày pixel); đánh dấu hull là helper và tắt raycast của nó |
| Hai bản hiện cùng một chỗ, hoặc z-fighting | thay chi tiết theo từng trạng thái; quy tắc loại trừ `full` / `cut_only`; `make_cut_states.py` dừng lỗi khi có tên không khớp |
| Lưới hở thì nắp sai | quy tắc `closed` mới + `cap: force/none` + log lưới hở trong danh sách `clip`; cột cấp liệu có dự phòng `_y0` |
| **Bộ xuất ghi đè mesh dùng chung** (`Mesh.validate()`), hoặc tách mesh làm hỏng `ze155` | bản sao web có mesh data riêng; phần tách tạo bằng `new_from_object`; fingerprint số đỉnh và số mặt trước/sau |
| MCP ngắt sau 180 s khi đang xuất | một file mỗi lệnh, làm nóng trước, `try/finally`, `done.json`, kiểm file trên đĩa, không chạy lại khi chưa có kết quả |
| **Blender crash khi xuất, mất thay đổi chưa lưu của người dùng** | **bản sao lưu phiên (Q6)** trước W1; `use_active_scene=True`; một lệnh xuất mỗi lần |
| Mất vật liệu khi xuất | bảng ghi đè trong contract (gồm 2 vật liệu lọc mới của A1b) |
| Draw call: giảm CPU 4× dưới 30 fps | mục tiêu mềm; dự phòng `join({ filter })` trong từng thiết bị |
| Driver xem trước làm sai tư thế nghỉ (rest pose) khi xuất | tắt driver và đưa rotor về 0 trong mọi lệnh xuất |
| Tên A1b sau này đổi | `interior_export.items` ghi tên thật (618 vật thể); `check_glb.py` và `make_cut_states.py` bắt lỗi |
| Lần đầu chuyển trạng thái chậm (biên dịch shader) | biên dịch trước (`compileAsync`) sau khi tải `interior.glb` |

---

## 8. Công và vai trò

| Luồng | Việc | Công |
|---|---|---|
| A: Blender | W0, W1 + W2 × 2 đợt | 4–5 h |
| B: lõi web | sandbox, tích hợp 3 đợt | 6–7 h |
| C: dữ liệu và UI | công cụ, dữ liệu, UI Đợt 3 | 4–5 h |
| D: review | 3 lần × khoảng 1 h | 3 h |
| F: fixer | sửa lỗi của 3 đợt | 2–3 h |
| **Tổng** | | **≈ 19–23 giờ-agent** |

**Thời gian thực ≈ 6–7 h; tốt nhất 5 h** nếu không phải làm lại.
- **Đợt 1:** xem được sau 2,5–3 h.
  - Luồng A cần khoảng 2 h cho W0 + W1 + W2.
  - Luồng B làm song song trên `standin.glb`.
- **Đợt 2:** sau khoảng 4,5–5 h. Review đợt 1 chạy song song.
- **Đợt 3 và review, sửa cuối:** xong sau khoảng 6–7 h.

Đường găng là luồng Blender tuần tự cộng với review và sửa của đợt cuối.

---

## 9. Quyết định cần người dùng duyệt

| # | Câu hỏi | Đề xuất | Phương án khác |
|---|---|---|---|
| Q1 | Chuẩn bị và xuất ở đâu | **Qua MCP trong phiên đang mở:**<br>• scene `ze155_web` gồm bản sao có mesh data riêng;<br>• `libraries.write`;<br>• xuất bằng `bpy.ops` trong `execute_blender_code`, mỗi file một lệnh.<br>**Rủi ro còn lại:** Blender 5.2.2 từng crash khi xuất GLB (ngày 2026-10-03; nguyên nhân khi đó là `use_active_scene=False`, kế hoạch này tránh được). Nên duyệt kèm Q6 | Blender nền trên bản `ze155_web.blend`: an toàn hơn nhưng BRIEF cấm |
| Q2 | Mặt cắt | **Hybrid:**<br>• trạng thái cố định dùng lại bản cắt sẵn của A1a/A1b (nắp mặt cắt vít, nắp ống nhiều lớp, bơm, khuôn A-A, mặt khuôn dưới, đầu xi lanh và van `_lo`);<br>• cắt runtime cho mặt cắt tự do và chỗ chưa có bản cắt sẵn.<br>Cái giá: khoảng 0 h dựng thêm, khoảng 54 nghìn tam giác trong file tải sau | Chỉ cắt runtime: ít dữ liệu hơn nhưng mất nắp nhiều lớp, đĩa trục Ø72, mặt đầu khối nhựa sạch |
| Q3 | Đơn vị chọn | **Thiết bị (190); Alt + bấm chọn chi tiết; không ghép mesh ở v1** | Theo vật thể Blender, hoặc ghép theo thiết bị |
| Q4 | Chuyển động bản v1 | **12 bộ phận quay, 3 clip (`sc_index` gồm cả piston xả ngược), lột vỏ, đổi khối nhựa van, shader khối nhựa, shape key khuôn, sơ đồ khối vòng điều khiển 2D (Đợt 3).** v2: dòng chảy 3D S14, cung vòng điều khiển 3D, hạt, bọt | Làm đủ như phim: thêm ≈ 4–6 h |
| Q5 | Bộ công cụ | **React 19.3, R3F 9.8.1, drei 10.7.9, three 0.186.1, three-mesh-bvh 0.8.3, Vite 8, TypeScript; meshopt; không CDN.** Người dùng cho đường dẫn dự án R3F khi có | Next.js; một file GLB duy nhất |
| **Q6** | **Sao lưu toàn phiên Blender trước W1** | **Đồng ý:**<br>• `bpy.ops.wm.save_as_mainfile(filepath='/Users/manhhaycode/m3d-e2e/ze155-tdie/out/ze155_session_backup.blend', copy=True)`, chạy một lần trước W1. Đường dẫn tuyệt đối, vì đường dẫn tương đối tính theo thư mục làm việc của tiến trình Blender (thường là `/` khi mở từ GUI);<br>• sau đó kiểm: file có trên đĩa, `bpy.data.filepath` không đổi, `bpy.data.is_dirty` vẫn là True;<br>• lưu bản sao toàn bộ phiên, kể cả thay đổi chưa lưu, mà không đổi đường dẫn hay cờ "chưa lưu" (dirty) của file đang mở;<br>• khoảng 30 MB, vài giây.<br>BRIEF cấm lệnh lưu, nên cần người dùng duyệt | Người dùng tự dùng File → Save Copy; hoặc không sao lưu và chấp nhận rủi ro mất thay đổi nếu Blender crash |

---

## 10. Đã sửa theo review

| Mã | Đã sửa |
|---|---|
| C1 | Lọc trong `mesh.raycast` (bên đã cắt, vật ẩn, vật ghost); empty ẩn trả `false`; bản vật liệu DoubleSide; `acceleratedRaycast` cho mesh dùng chung; thêm tiêu chí **A5b** bấm vào nắp. Snippet §3 |
| I1 | `Outlines screenspace={false}` (độ dày pixel); hull đánh dấu helper, tắt raycast (Outlines không chuyển ref). Snippet §4 |
| I2 | Tách `show_whole` / `show_clipped`: vít nguyên ở CUT_Z_BARREL/ST1, vít cắt sẵn ở CUT_X*, khối nhựa dùng bản cắt sẵn |
| I3 | `swap` theo từng trạng thái thay cho `swap_to` chung; thân khuôn có trong swap; CUT_PUMP không hiện thân rỗng chung với bản cắt; ống/trộn dùng bản cắt nhiều lớp; `free_swap` riêng cho FREE |
| I4 | `interior_export.items` dựng lại từ log A1b và scene thật (618 vật thể), mỗi mục một vai trò; bánh răng: nửa cắt cho CUT_PUMP, `_full` cho ST1/FREE, cùng nằm dưới rotor; hộp số sơ đồ + ghost được đưa vào, thêm 2 rotor |
| I5 | Q2 thành hybrid, có đề xuất; giữ bản cắt sẵn đúng theo DECISIONS 29; nêu cái giá thật (≈ 0 h, ≈ 54 nghìn tam giác) |
| I6 | Quy tắc `closed` mới (cho phép cạnh 3+ mặt, kiểm hướng mặt, thể tích > 0), đã đo trên scene; `cap: force/none`; dự phòng `_y0` cho cột cấp liệu |
| I7 | CUT_DIE_PLAN không ẩn hay cắt đích của `die_open`; chỉ cắt nhóm nửa dưới; giữ trạng thái đã nhấc |
| I8 | Bản sao có mesh data riêng (để `Mesh.validate()` không chạm `ze155`); phần tách từ `new_from_object`; fingerprint có số đỉnh và số mặt |
| I9 | Mỗi file một lệnh MCP, làm nóng trước, `try/finally`, `done.json`, kiểm file trên đĩa, quy tắc khi bị ngắt |
| I10 | Q6 mới (`save_as_mainfile copy=True`), đề xuất đồng ý; Q1 nêu rủi ro crash |
| M1 | Sửa mô tả tên mesh con; bảng tra chỉ đánh chỉ mục node có `kind`; đặt tên data `m_<node>` |
| M2 | Thống nhất số: 189 + 1 = 190 thiết bị; danh sách phần dùng tên đã tách; `dev_screws` có bbox thật và ghi rõ ngoại lệ transform đơn vị; bỏ ghi chú "attach" |
| M3 | Bước `make_cut_states.py` dừng lỗi khi có tên không khớp; đổi khối nhựa van theo `valve_run`; FLOWS quy về FULL |
| M4 | Biên dịch trước các trạng thái; đo 200 ms ở lần vào thứ hai; `?selfcheck` ép DPR 1 |
| M5 | Mục tiêu giảm CPU 4× thành mục tiêu mềm, có dự phòng `join({ filter })`, đo sớm |
| M6 | GHOST_SC hiện `anim_ghost_sc` và ẩn vỏ ngoài; FREE bỏ ghost, marker, `cut_only` |
| M7 | Không bao giờ chỉnh `unit_settings`; fingerprint có cả cài đặt scene của `ze155_anim` |
| AD1 | Đợt 1 gồm bộ đầu xi lanh/van `_lo` mà CUT_Z_BARREL cần, cộng quy tắc "thiếu bản thay thì cắt node ngoài"; rotor hộp số đã có trong contract; lột vỏ là code runtime; 3 clip (piston xả ngược nằm trong `sc_index`); sơ đồ vòng điều khiển 2D ở Đợt 3, bản 3D để v2 (khớp Q4); W1 chạy lại được |
| AD2 | Luồng B dùng `standin.glb` tổng hợp đúng contract, không dùng bản xuất thô |
| AD3 | Driver xem trước chỉ trên `rot_*` của `ze155_web`, biểu thức đơn giản, tắt và đưa về 0 khi xuất |
| AD4 | Review đợt N chạy song song với dựng đợt N+1, trừ đợt cuối; ước lượng 6–7 h (tốt nhất 5 h) |
| N1 | Bỏ drei `<Bvh>` (khi StrictMode dọn effect, nó đặt lại `mesh.raycast` và làm mất bộ lọc). `installRaycastFilter` tự dựng BVH, gán hàm dùng chung, kiểm "đã gắn" bằng so khớp hàm thay cho cờ `__rayWrapped`, chạy lại bao nhiêu lần cũng được. Thêm `selfcheck().rayUnfiltered`. Vẫn giữ A5b: lấy mọi điểm trúng, bản cắt DoubleSide. Snippet §1, §3, §14 |
| N2 | `setVisible` được export từ `Cuts.ts`. `setFreeClip`, `applyCutState` (gốc interior) và công tắc khối nhựa van đều đổi hiển thị qua nó, nên `resetCuts` trả lại đúng trạng thái lúc tải. Hook `cutRoundTrip()` kiểm FULL → FREE → FULL và mỗi trạng thái cố định → FREE → chính nó. Snippet §6, §7, §11, §14 |
| N3 | FREE có danh sách `hide`: khối nhựa XẢ của van (chỉ hiện bộ CHẠY, không bao giờ hiện cả hai) và bộ đĩa lọc (vành đĩa nhô qua vỏ ngoài; chọn ẩn vì đơn giản nhất). Contract: `cut_states.FREE.hide`, các mục đó bỏ `FREE` khỏi `states` |
| N4 | Q6 dùng đường dẫn tuyệt đối `/Users/manhhaycode/m3d-e2e/ze155-tdie/out/ze155_session_backup.blend`, rồi kiểm file có, `filepath` không đổi, `is_dirty` vẫn True (Q6 và contract `safety`) |
| N5 | `interior_export.items` ghi đủ tên thật của 9 + 9 khối nhựa vùng vít (`_feed` … `_pump`, kèm `_lo`); mọi mục có `slice` 1 hoặc 2 theo mục 4.1; W1.6 chép theo `slice`. Tên thuộc đợt sau (`slice: 2`) trong FREE được bỏ qua có ghi log khi sinh `cut_states.json` ở Đợt 1 |

Không bỏ qua mục nào. M5 được làm mềm chứ không bỏ.
