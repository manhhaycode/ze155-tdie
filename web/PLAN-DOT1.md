# Kế hoạch Đợt 1: dây chuyền ZE 155 lên web R3F (phương án C)

Bản 1.0, 2026-10-05. Đây là kế hoạch, chưa dựng sản phẩm. Mọi con số trong tài liệu là **số đo thật** từ probe ngày 2026-10-05 (mục 0.2): xuất GLB bằng tiến trình Blender nền, nén bằng gltf-transform, tải bằng GLTFLoader trong Node.

**Quan hệ với tài liệu cũ:** `PLAN-R3F.md`, `model-contract.json` và `r3f-snippets.md` giữ nguyên. Contract vẫn là nguồn cho danh sách thiết bị, trạng thái cắt, rotor và vật liệu. Tài liệu này thay thế PLAN-R3F cho Đợt 1 ở những điểm liệt kê trong mục 10. Tên node trong contract (`p_*`, `dev_*`, `rot_*`) được ánh xạ sang tên thật theo mục 3.3.

---

## 0. Tóm tắt

- **Xuất (export):** một lệnh Blender nền đọc `out/ze155_anim.blend`, không lưu. Xuất cả hai file mất **2,8 s** wall. Nén meshopt mất 2,6 s. Cả chuỗi `make -C web all` dự kiến dưới 15 s, chạy lại bao nhiêu lần cũng được.
- **Kết quả:**
  - `line.glb`: **5,79 MB**, 354 node, 771 draw call, 1 189 654 tam giác;
  - `interior.glb`: **1,98 MB**, 207 node, 438 draw call, 413 006 tam giác.
- **Tên node = tên object Blender.** Tất cả 561 tên đều nằm trong `[a-z0-9_]`, không trùng trong một file và giữa hai file. Qua GLTFLoader, `userData.name === name` cho cả 561 node, với cả three r186 lẫn three-stdlib 2.36.1.
- **Cấu trúc dựng lúc chạy (runtime) từ JSON:**
  - 190 nhóm thiết bị (device group) bằng `attach`;
  - 8 pivot quay;
  - 6 trạng thái cắt (cut state);
  - bộ lọc tia chọn (raycast filter) nằm trong `mesh.raycast`.
- **Quyết định: Đợt 1 xuất toàn bộ phần bên trong** (cả các mục `slice: 2`), lý do ở mục 3.1.4.
- **Hai builder song song:**
  - A: xuất, dữ liệu, kiểm, rồi làm các component UI, khoảng 3,5 h;
  - B: sandbox `web/web-check/`, khoảng 5 h.
  - Mốc xem được trong trình duyệt (tải và chọn thiết bị) sau khoảng 2,5 h. Đủ Đợt 1 sau khoảng 5 h, rồi review 1 h và sửa 1 h.
- **B không phải chờ A:** probe đã sinh GLB thật và JSON nháp để làm bản thay thế (stand-in), xem mục 4.4.

### 0.1 File đi kèm (đã có)

| File | Nội dung |
|---|---|
| `web/dot1/export_glb.py` | Script xuất **đã chạy thật** trong probe; A chép sang `web/tools/` |
| `web/dot1/selection-rules.json` | Quy tắc chọn object cho `line` và `interior` (máy đọc) |
| `web/dot1/cut_states.dot1.json` | 6 trạng thái Đợt 1 với tên đã xuất, mặt phẳng, peel và camera |
| `web/dot1/node_map.dot1.json` | 561 node → thiết bị, loại, vai trò, `closed`, `cap` |
| `web/dot1/rotors.dot1.json` | 12 rotor (8 chạy ở Đợt 1) với pivot, trục, rpm, danh sách `attach` |
| `web/dot1/devices.dot1.json` | 190 thiết bị + 10 section, chữ tiếng Việt lấy từ `parts.json` |
| `web/dot1/materials.dot1.json` | 79 vật liệu: cách xử lý ở web và màu nắp (cap) |
| `web/dot1/gen_drafts.py` | Prototype sinh 5 file nháp trên; A port thành `web/tools/make_data.py` |
| `web/build/probe/models/{line,interior}.glb` | GLB nén thật, dùng làm stand-in cho B |
| `web/build/probe/raw/{line,interior}.glb` | GLB thô (chưa nén), dùng cho phép kiểm lưới kín |
| `web/build/probe/*.json` | Báo cáo probe: `export_report.json`, `load_check.json`, `closed_check.json`, `inventory.json`, `line/interior.nodes.json` |
| `web/build/probe/scripts/` | Script probe: `inventory.py`, `load_check.mjs`, `closed_check.mjs`, `bvh_time.mjs`, `stdlib_check.mjs` |
| `web/build/probe/tmp/*.validate.txt` | Kết quả validator của GLB thô và GLB nén |

### 0.2 Số đo probe (2026-10-05, Apple M3 Pro, Blender 5.2.2, io_scene_gltf2 5.2.40, Node 24.12)

| Hạng mục | Số đo |
|---|---|
| Lệnh nền | `Blender -b --factory-startup --python-exit-code 1 out/ze155_anim.blend --python web/dot1/export_glb.py -- …` |
| Thời gian | Tải `.blend` khoảng 0,4 s; xuất `line` 1,53 s, `interior` 0,26 s; cả tiến trình **2,8 s** wall |
| GLB thô | `line.glb` **23 668 860 B**; `interior.glb` **8 423 768 B** |
| GLB nén (dedup → prune → meshopt) | `line.glb` **5 793 436 B** (−75 %); `interior.glb` **1 982 388 B** (−76 %). Chuỗi lệnh mất 1,46 s + 1,10 s |
| Validator (gltf-transform 4.5.1) | Thô: 0 lỗi, 0 cảnh báo. Nén: 0 lỗi, 0 cảnh báo, 2 info (validator không đọc được `EXT_meshopt_compression`; buffer dự phòng không dùng) |
| `line` | 354 node = 351 mesh (gồm **59 curve đã thành mesh**) + 3 empty `anim_roll_axis_*`. 351 mesh glTF, **771 primitive = 771 draw call**, 1 189 654 tam giác, 48 vật liệu. 199 node nhiều vật liệu. Không có mesh dùng chung; dedup gộp được 8 geometry giống hệt (771 → 763 geometry) |
| `interior` | 207 node = 205 mesh + 2 empty `int_screw_axis_a/b`. 130 mesh glTF, 293 primitive riêng, **438 draw call**, 413 006 tam giác (tính cả bản dùng chung), 45 vật liệu. 133 node nhiều vật liệu |
| Mesh dùng chung | 19 mesh glTF ở `interior`: 10 mesh phần tử vít cho 64 node, cặp `_x2450` / `_x4120`, 4 nắp `int_xsec_*`, 2 trục then hoa, 12 lưới lọc, 4 khối nhựa dùng chung giữa bản đủ và `_lo` |
| Modifier | Áp đúng: tam giác sau đánh giá (evaluated) = tam giác trong glTF (1 189 654; interior 413 007 so với 413 006: `Mesh.validate()` bỏ 1 mặt suy biến của `int_fill_valve_drain_bolt_lo` trong bộ nhớ, có cảnh báo trong log) |
| Collection / object ẩn | Depsgraph chứa đủ 618 object, kể cả các collection tắt mắt. **Xuất không bỏ ẩn cho ra GLB giống từng byte** với xuất có bỏ ẩn. Script vẫn bỏ ẩn trong bộ nhớ để phòng trường hợp có collection bị `exclude` (object khi đó không vào depsgraph) |
| Custom property | Thành extras của node: `line` 5 node (`note`, `source`); `interior` 183 node (`phase_deg`, `zone`, `x_mm`, `dirt`, `type`…). Extras của mesh chỉ có `targetNames` |
| Shape key | Còn nguyên: 4 mesh (`int_die_section_upper`, `int_die_thermal_bolts_y0`, `int_die_thermal_bolt_y0`, `int_fill_die_y0`) có morph target `gap_x10`, `lip_push`; `morphTargetDictionary` vẫn đúng sau meshopt |
| Tên mesh con | Node nhiều vật liệu thành `Group` (tên node), các mesh con mang tên `<tên mesh>_1…_n`, ví dụ `barrel_b1` → `barrel_b1_1`, `_2`, `_3`. Tên mesh có `.001` bị bỏ dấu chấm. **Không code nào được dựa vào tên mesh con** |
| Quantize (meshopt) | Ghi lại TRS của node mesh (translation, scale). Node mesh **có con** bị tách: mesh chuyển sang một node con **không tên**. Đúng 4 trường hợp: `int_valve_bolt`, `int_sc_disc`, `int_pump_gear_top`, `int_pump_gear_bottom`. Lệch bbox thế giới tối đa 0,35 mm (`line`, `frame_feet`), 0,49 mm (`interior`, `int_fill_die_y0`); trung vị 21 µm / 4 µm |
| Lưới kín (hàn đỉnh theo vị trí, trên GLB thô) | `line` 344/351 kín; 7 hở: 3 trục cán, `feed_platform_deck`, `melt_pipe`, `melt_static_mixer`, `vac_reg_valve_2`. `interior` 177/205 kín; 28 hở: 25 khối nhựa (hở đầu, đúng thiết kế), `int_melt_adapters_hollow_die_y0`, `int_pump_body_lo`, `int_fill_valve_drain_bolt_lo`. 59/59 curve kín. 0 mặt lật, 0 thể tích âm |
| Tải trong Node (không vẽ) | Giải nén meshopt (WASM): `line` **38 ms**, `interior` **11 ms** |
| BVH (three-mesh-bvh 0.8.3) | `SAH`: 1 195 ms + 361 ms. **`CENTER`: 332 ms + 74 ms** |
| `attach` | 345 node gốc: 1,4 ms; 109 node: 0,3 ms |
| Raycast | 200 tia lấy mọi điểm trúng trên `line`: 34 ms (0,17 ms/tia) |
| Đối chiếu tên với dữ liệu | 351/351 khoá `object_to_device` có trong `line`. Mọi tên trong 6 trạng thái Đợt 1 (bỏ tiền tố `p_`) đều có trong GLB. 207/207 node `interior` có mục trong `interior_export.items`. 190/190 thiết bị có ít nhất 1 node; 24 thiết bị có phần bên trong |
| `.blend` | mtime 1791173730, 29 470 668 B; **không đổi** sau cả 3 lần chạy nền. Không sinh `quit.blend` hay autosave |
| Xung đột | Blender của người dùng (PID 63386) giữ cổng 127.0.0.1:9876 (addon MCP). Tiến trình nền chạy `--factory-startup` không nạp addon nào, nên không đụng cổng này |

---

## 1. Mục tiêu và tiêu chí nghiệm thu của Đợt 1

**Mục tiêu:**
- Xem cả dây chuyền phía ngoài; chọn theo thiết bị như trong Blender.
- Mở phần xi lanh bằng 5 trạng thái cắt cố định cùng mặt cắt tự do.
- Xem hai trục vít quay trong lỗ số 8.
- Phần bên trong chỉ tải khi cần (lazy-load).

**Cách đo chung:**
- Máy này (M3 Pro), Chrome qua chrome-devtools MCP, canvas 1920 × 1080.
- `npm run dev -- --port 5178 --strictPort`. StrictMode vẫn bật như mẫu create-vite.
- URL `http://localhost:5178/?selfcheck=1`. Tham số này ép `dpr={1}` và in `<pre id="selfcheck">`.
- Mọi hook nằm ở `window.__ze` (mục 4.2.11). Gọi bằng `evaluate_script`; ví dụ `await __ze.ready; return __ze.selfcheck()`.

| # | Tiêu chí | Ngưỡng | Cách kiểm trong Chrome |
|---|---|---|---|
| D1 | Thời gian tải | `line` hiện khung đầu ≤ **4 s** sau `navigate_page` (cache trống, localhost). `interior` sẵn sàng ≤ **1,5 s** sau lần đầu vào một trạng thái cắt. BVH ≤ **800 ms** tổng | `navigate_page` (bỏ cache) → `__ze.stats().load` = `{line_first_frame_ms, interior_ready_ms, bvh_ms}` |
| D2 | **190 thiết bị chọn được** | `__ze.devices().length === 190`. `__ze.selectAll()` trả 190 ok. `__ze.pickSweep()` ở FULL: ≥ **180/189** thiết bị ngoài chọn được bằng tia thật sau khi `fitToBox`; `screws` chọn được ở CUT_Z_BARREL. Thiết bị không chọn được phải có lý do (bị che kín) | `evaluate_script` |
| D3 | Chọn kiểu Blender | • di chuột: viền 2 px `#9fd3ff`;<br>• bấm: viền 3 px `#ff8a1f` + hộp bao (`Box3Helper`) + bảng thông tin;<br>• bấm đúp hoặc phím F: `fitToBox`;<br>• Alt + bấm: chọn một chi tiết;<br>• Esc hoặc bấm vào chỗ trống: bỏ chọn | `__ze.clickAt(x, y, {alt, dbl})` + `__ze.selection()`; `press_key` F và Escape; `take_screenshot` |
| D4 | **Bấm vào nắp chọn đúng thiết bị bị cắt** | `__ze.capCheck(state, device).ok` cho cả 6 cặp: (CUT_Z_BARREL, `barrel_b3`), (CUT_X2450, `barrel_b3`), (CUT_X4120, `barrel_b5`), (CUT_FEED, `feed_throat`), (FREE x = 3,0, `barrel_b4`), (CUT_X2450, `screws`, nắp cắt sẵn `int_xsec_*`). Thêm một `clickAt` thật lên một pixel nắp mà capCheck trả về: `selection().selected` phải đúng thiết bị | `evaluate_script` |
| D5 | Bộ lọc tia không mất | `__ze.selfcheck().rayUnfiltered === 0` ngay dưới `npm run dev` (StrictMode). Kiểm cả sau khi chạy hết các trạng thái và sau khi chọn (viền chọn tạo hull mới) | `evaluate_script` |
| D6 | Khứ hồi trạng thái | `__ze.cutRoundTrip()` → `{ok: true, bad: []}`. Hook này kiểm tập payload đang hiện, vật liệu của từng mesh, và khi kết thúc `gl.clippingPlanes.length === 0` cùng không còn vật liệu nào trỏ tới `freePlane` | `evaluate_script` |
| D7 | Đổi trạng thái nhanh | `__ze.timeState(id)` ≤ **200 ms** cho cả 5 trạng thái cố định và lúc vào FREE, đo ở lần vào thứ hai (sau precompile). Kéo thanh trượt FREE ≤ 16 ms mỗi bước (chỉ đổi `plane.constant`) | `evaluate_script` |
| D8 | Quay đúng tốc độ, đúng trục | `__ze.rotorTest(2)`: 8 rotor Đợt 1, góc đo so với 2π·rpm/60/slow·t sai ≤ **5 %**. Vít −300 rpm, chậm 20× → **−90°/s** quanh trục three [1, 0, 0], hai vít cùng dấu (đồng hướng). Trục cán quanh [0, 0, −1] theo dấu +/−/+. Nhìn bằng mắt ở CUT_Z_BARREL: cánh vít trôi về +X (2 ảnh cách nhau 0,5 s) | `evaluate_script` + 2 `take_screenshot` |
| D9 | fps và draw call | DPR 1, 1920 × 1080:<br>• FULL ≥ 55 fps, ≤ **850** draw call;<br>• mỗi trạng thái cắt ≥ 45 fps, ≤ **1 000** (đo sau khi peel xong);<br>• FREE ≥ 40 fps, ≤ **1 100**;<br>• tam giác hiện ≤ 1,7 triệu; JS heap ≤ 600 MB.<br>Đã đo: FULL có 771 draw call từ mesh. Ước từ dữ liệu: CUT_FEED 769, CUT_Z_BARREL 824, CUT_X2450 816, CUT_X4120 859, FREE 953 (chưa tính viền chọn, ground) | `__ze.stats()` (đọc sau 3 s ở trạng thái đó); `performance_start_trace` 5 s với `__ze.orbitTest()` ở FULL |
| D10 | Dung lượng file | `public/models/line.glb` ≤ **7 MB** (đo 5,79), `interior.glb` ≤ **2,5 MB** (đo 1,98) | `build/reports/check.json`; `list_network_requests` (kích thước) |
| D11 | Console sạch | 0 error, 0 warning của ứng dụng sau khi tải, chạy hết trạng thái và chọn | `list_console_messages` |
| D12 | Chỉ mạng nội bộ | Mọi request đều tới `localhost:5178`: trang, JS, 2 GLB, 5 JSON. Không CDN: không Draco gstatic, không font ngoài, không HDR. `interior.glb` **chỉ** được tải sau lần vào trạng thái cắt đầu tiên | `list_network_requests` trước và sau `setState('CUT_Z_BARREL')` |
| D13 | So ảnh bằng mắt | Mỗi trạng thái chụp ở camera preset của nó (mục 3.3.5), so với:<br>• CUT_Z_BARREL ↔ `anim/look/A1a-S04-f1161-ev-r2.png`, `anim/storyboard/S04.png`;<br>• CUT_X2450 ↔ `A1a-x2450-S05b-ev-r2.png`, `S05.png`;<br>• CUT_X4120 ↔ `A1a-x4120-S07b-ev-r2.png`, `S07.png`;<br>• CUT_FEED ↔ `A1a-feedcol-ext-wb.png`, `S03.png`;<br>• FULL ↔ `out/renders/ze155-hero.png`.<br>Đạt khi:<br>• nắp đỏ gạch có vân chéo ở thép bị cắt;<br>• vít nguyên, ăn khớp trong lỗ số 8 (CUT_Z_BARREL);<br>• vòng biên dạng và đĩa trục Ø72 ở X 2 450 / 4 120;<br>• không z-fighting, không hiện hai bản ở cùng một chỗ;<br>• cửa sổ tím, vòm ghost xanh nhạt, khối nhựa hổ phách | `take_screenshot` → `web/review/dot1/shot-<STATE>.png` |
| D14 | Toàn vẹn dữ liệu | `make -C web all` exit 0; `check.json.failures = []`. `selfcheck()`: `unknownNodes = 0`, `missingNodes = 0`, `orphans = 0`, `devices = 190` | terminal + `evaluate_script` |
| D15 | `.blend` không bị ghi | `build/reports/export.json.blend_unchanged === true`; `stat` của `out/ze155_anim.blend` trước và sau `make all` giống nhau | terminal |

---

## 2. Kiến trúc Đợt 1

```
out/ze155_anim.blend (chỉ đọc)
        │  Blender -b --factory-startup … --python tools/export_glb.py   (mục 3.1, ~3 s)
        │  bộ nhớ: bỏ ẩn, collection tạm __web_<file>, KHÔNG lưu
        ▼
web/build/raw/{line,interior}.glb  ──► build/reports/export.json (số object, tam giác, thời gian, blend_unchanged)
        │  gltf-transform 4.5.1: dedup --materials false → prune --keep-leaves true → meshopt --level high   (mục 3.2)
        ▼
web/build/models/{line,interior}.glb ──► validate *.txt
        │  node tools/check_glb.mjs analyze   (tên, số đếm, closed, lệch bbox, quantize, vật liệu, morph)
        ▼
build/reports/glb_analysis.json
        │  python3 tools/make_data.py   (contract + parts.json + shots.json + glb_analysis)
        ▼
build/data/{devices,node_map,cut_states,rotors,materials}.json
        │  node tools/check_glb.mjs verify   (mọi tên phải tra được; luật loại trừ; ngân sách)  → exit 1 nếu sai
        ▼
make publish ──► web-check/public/models/*.glb + web-check/public/data/*.json
        │
        ▼  trình duyệt (Vite dev 5178)
 data.ts (fetch 5 JSON) ─┐
 useGLTF(line) ──────────┼─► rigLine:   sec_* / dev_* bằng attach, payload, pivot rot_*, vật liệu, BVH + lọc tia
 useGLTF(interior)*  ────┘   rigInterior: attach vào dev_<chủ>, payload mặc định ẩn, pivot vít, BVH
                                    │
              ┌──────────────┬──────┴───────┬──────────────┬─────────────┐
           Picking        Selection        Cuts / Free     Rotors       UI (Toolbar, DeviceTree, InfoPanel)
         (mesh.raycast)  (Outlines, bbox,  (setVisible,   (useFrame)         │
                          fitToBox)         nắp, peel)                  zustand store ◄── window.__ze (test)
 * interior chỉ tải khi trạng thái đầu tiên có needs_interior = true
```

**Cây runtime sau khi rig:**

```
lineScene (gltf.scene của line.glb, render bằng <primitive>)
 ├─ sec_<group> ×10                (Group, transform đơn vị, userData.ze = {kind:'section'})
 │   └─ dev_<device_id> ×190       (Group, transform đơn vị, userData.ze = {kind:'device', device_id})
 │        ├─ <node đã xuất>        (Mesh hoặc Group mesh; userData.ze = {kind:'part'|'interior', name, device_id, …})
 │        ├─ rot_<id>              (Object3D tại pivot_m, quay ở useFrame)
 │        │    └─ <node attach>    (vd. int_screw_axis_a ─ 32 phần tử, trục then hoa, bản cắt sẵn, nắp xsec, bánh răng ra)
 │        └─ …
 ├─ ground                         (helper, không chọn được)
 └─ peel                           (helper, tạm thời)
interiorScene: rỗng sau rigInterior (mọi node đã attach sang lineScene); không render
```

**Sáu nguyên tắc runtime:**
1. **Tên là khoá.** Mọi tra cứu dùng `userData.name` (tên node glTF gốc = tên object Blender). Bảng tra chỉ đánh chỉ mục các node có trong `node_map.json`.
2. **Chỉ payload đổi `visible`.** Payload là Object3D mang hình của một chi tiết (mục 4.2.3). Nhóm thiết bị, section, pivot và node chi tiết có con thì không bao giờ bị ẩn. Nhờ vậy `resetCuts` khôi phục đúng, và tia không phải xét tổ tiên.
3. **Không bao giờ quay trực tiếp một node mesh.** Quantize ghi lại TRS của node mesh. Rotor luôn là Object3D tạo lúc chạy, đặt tại `pivot_m`, rồi `attach` các node vào.
4. **Không dựa vào tên mesh con** (`barrel_b1_1`…) hay node không tên do quantize tạo ra.
5. **Siêu dữ liệu runtime nằm ở `userData.ze`.** Extras từ Blender (`type`, `zone`, `note`…) giữ nguyên ở `userData`, không bị ghi đè hay bị hiểu nhầm.
6. **Phần bên trong gắn vào cây `line`** sau khi tải: mỗi node gốc của `interior` được attach vào `dev_<chủ>`. Vì vậy chọn, viền, bbox và sự kiện chuột của R3F dùng chung một cây và một bộ xử lý.

---

## 3. Luồng A: xuất và dữ liệu (không MCP)

### 3.1 `export_glb.py`

Bản đã chạy thật nằm ở `web/dot1/export_glb.py`. A chép sang `web/tools/export_glb.py` mà không đổi logic.

#### 3.1.1 Lệnh và tham số dòng lệnh (CLI)

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 \
  ../out/ze155_anim.blend --python tools/export_glb.py -- \
  --rules web/dot1/selection-rules.json --file all \
  --out web/build/raw --report web/build/reports/export.json --tris
```

| Tham số | Ý nghĩa |
|---|---|
| `--rules` | đường dẫn tới `selection-rules.json`, tương đối theo gốc workspace `ze155-tdie/` |
| `--file` | `line`, `interior` hoặc `all` |
| `--out` | thư mục ghi GLB, tương đối theo workspace. **Bắt buộc nằm trong `web/build/`**, nếu không thì script dừng |
| `--report` | file JSON báo cáo, cũng phải nằm trong `web/build/` |
| `--tris` | đếm tam giác evaluated cho từng object (thêm dưới 0,5 s) |

**Exit code:**
- 0: đạt;
- 1: Python có exception (nhờ `--python-exit-code 1`), số đếm khác `expect`, hoặc mtime/size của `.blend` đổi.

#### 3.1.2 Quy tắc chọn (đã đo trên file thật, xem `selection-rules.json`)

Collection của scene `ze155_anim` (đọc từ file):

| Collection | Object | Ẩn trong file | Thuộc file |
|---|---|---|---|
| `anim_ax` > 18 nhóm `ax_*` | 343 (phần ngoài của `ze155`) | chỉ `ax_always_replaced` (collection `hide_render` + layer tắt mắt) | `line` |
| `anim_int` > `anim_int_context` | 14: `anim_ctx_scanner`, `anim_ctx_scanner_head`, 3 empty `anim_roll_axis_*` cùng 9 con `anim_roll_markers_*` | không | `line` |
| `anim_int` > 20 collection còn lại (`anim_int_screws`, `_barrel`, `_feed`, `_fill`, `_fill_lo`, `_fill_x2450/x4120`, `_screws_x2450/x4120`, `_vent_markers`, `_melt`, `_melt_zb`, `_st1_lo`, `_sc`, `_pump`, `_pump_full`, `_die_plan`, `_die_aa`, `_drive`, `_die` rỗng) | 205 | 17/20 tắt mắt và `hide_render` (trừ `_screws`, `_fill` và `_die` rỗng) | `interior` |
| `anim_cut` > `anim_cut_ghost_sc`, `anim_cut_ghost_drive` | 2 ghost; 8 collection `anim_cut_*` khác rỗng | có | `interior` |
| `anim_rig` (24 camera, 24 `anim_tgt_*`, 5 đèn, `anim_ctrl`), `anim_cutters` (rỗng), `anim_fx` (rỗng) | — | — | không bao giờ |

| File | Lấy | Bỏ | Loại object | Kỳ vọng (đã đo) |
|---|---|---|---|---|
| `line` | `anim_ax` + `anim_int_context` (đệ quy, `all_objects`) | `screws_a`, `screws_b`, `ctx_floor` | MESH, CURVE, EMPTY | 354 object: 292 mesh + 59 curve + 3 empty |
| `interior` | `anim_int` + `anim_cut` | collection `anim_int_context` | MESH, CURVE, EMPTY | 207 object: 205 mesh + 2 empty |

**Xử lý `ax_always_replaced` (7 object, ẩn trong file):**

| Object | Đợt 1 | Lý do |
|---|---|---|
| `screws_a`, `screws_b` | **bỏ** | 64 phần tử vít trong `interior` thay thế. Hai lưới cũ 30 788 tam giác mỗi cái sẽ nằm trùng chỗ vít mới |
| `ctx_sheet` | xuất nguyên | web ghi đè vật liệu `ze_sheet_pet` (trong mờ) |
| `ctx_melt_curtain` | xuất nguyên | web ghi đè `ze_melt_curtain` |
| `melt_heater_bands` | xuất nguyên, **1 node, không tách** 6 phần | không có trạng thái Đợt 1 nào cắt nó. Việc tách theo nhóm ax (contract `split_objects`) chỉ cần ở Đợt 2, và nếu cần thì tách theo island ở runtime |
| `die_body_bolts`, `die_heater_boxes` | xuất nguyên, **không tách** trên/dưới | `die_open` là tween runtime ở Đợt 2. Nửa trên lúc đó tách bằng island (Y > 1,2) ở runtime, không tách trong Blender |

**Việc làm trong bộ nhớ (không lưu):**
1. Đặt scene cửa sổ là `ze155_anim`.
2. Với mỗi collection được lấy: `layer_collection.exclude = False`, `hide_viewport = False`, `collection.hide_viewport = False`. Với object: `hide_set(False)`, `hide_viewport = False`.
3. `rotation_euler = 0` cho `int_screw_axis_a/b` và `anim_roll_axis_*`. Trong file chúng đã bằng 0; script ghi giá trị trước vào báo cáo.
4. Tạo collection tạm `__web_<file>` (không gắn vào scene), link các object đã chọn vào đó, rồi truyền làm tham số `collection` của exporter. Xuất xong thì gỡ collection.

#### 3.1.3 Tham số exporter (tên thật trong io_scene_gltf2 5.2.40, đã chạy)

```python
COMMON = dict(
    export_format='GLB', check_existing=False, use_active_scene=True,
    use_selection=False, use_visible=False, use_renderable=False, use_active_collection=False,
    at_collection_center=False, export_hierarchy_full_collections=False, export_hierarchy_flatten_objs=False,
    export_extras=True, export_yup=True, export_apply=True,
    export_cameras=False, export_lights=False,
    export_materials='EXPORT', export_image_format='NONE', export_texcoords=False, export_normals=True,
    export_tangents=False, export_attributes=False, export_vertex_color='NONE',
    use_mesh_edges=False, use_mesh_vertices=False, export_gn_mesh=False, export_gpu_instances=False,
    export_shared_accessors=False,
    export_morph=True, export_morph_normal=True, export_morph_tangent=False, export_morph_animation=False,
    export_animations=False, export_skins=False,
    export_draco_mesh_compression_enable=False, export_meshopt_compression_enable=False, export_use_gltfpack=False,
    will_save_settings=False,
)
bpy.ops.export_scene.gltf(filepath=out, collection='__web_line', **COMMON)
```

**Ghi chú về tham số:**
- `use_visible=False` và `use_renderable=False`: exporter không lọc theo cờ ẩn. Lý do chọn là cây của exporter dựng từ `scene_eval.objects`, rồi lọc theo `collection.all_objects`.
- `export_apply=True`: áp Bevel (257), Weighted Normal (262), Boolean, Array, Solidify. Object không có modifier giữ mesh gốc, nên mesh dùng chung vẫn dùng chung.
- `export_animations=False`: theo phương án C, clip và tween nằm trong JSON và code. File có 34 action, đều của camera rig.
- `export_texcoords=False`: không có texture.
- `export_morph=True`: giữ shape key cho Đợt 2.
- Không dùng meshopt/Draco của Blender: GLB thô phải còn đọc được để kiểm.

#### 3.1.4 Quyết định: Đợt 1 xuất toàn bộ phần bên trong (slice 1 + 2)

| | Chỉ slice 1 | **Toàn bộ (chọn)** |
|---|---|---|
| Dung lượng `interior.glb` nén | khoảng 1,3 MB (ước theo tỉ lệ tam giác 262 k / 413 k) | 1,98 MB (đo) |
| Thời gian xuất | ≈ 0,2 s | 0,26 s (đo) |
| FREE | thiếu 36 tên melt-line trong `free_swap` và `FREE.hide`, phải dùng luật `missing_target_rule`, và đầu xi lanh, van, bơm bị cắt như khối đặc | **đủ:** 19 cặp `free_swap` đều tra được; thấy được kênh chảy, bánh răng bơm, van khi cắt tự do |
| Kiểm tên | cần ngoại lệ "tên thuộc slice sau thì chỉ ghi log" | **nghiêm:** mọi tên phải tra được, không có ngoại lệ |
| Đợt 2 | phải sửa quy tắc chọn và xuất lại | không phải xuất lại; chỉ nối thêm trạng thái |
| Tải | lazy | lazy (chỉ thêm 0,7 MB, localhost) |

Web chỉ nối 6 trạng thái Đợt 1. Các node slice 2 ẩn sẵn và chỉ hiện trong FREE theo vai trò `full` (quyết định mở Q3).

### 3.2 Chuỗi nén gltf-transform

`web/tools/package.json` khai báo `@gltf-transform/cli@4.5.1`, `three@0.186.1`, `three-mesh-bvh@0.8.3`. Cài một lần bằng `npm i`, không gọi `npx` qua mạng mỗi lần.

```bash
GT=tools/node_modules/.bin/gltf-transform
for f in line interior; do
  $GT dedup   build/raw/$f.glb   build/tmp/$f.1.glb  --materials false                          --vertex-layout separate
  $GT prune   build/tmp/$f.1.glb build/tmp/$f.2.glb  --keep-leaves true --keep-attributes false --vertex-layout separate
  $GT meshopt build/tmp/$f.2.glb build/models/$f.glb --level high                              --vertex-layout separate
  $GT validate build/models/$f.glb | sed 's/\x1b\[[0-9;]*m//g' > build/reports/$f.validate.txt
  $GT validate build/raw/$f.glb    | sed 's/\x1b\[[0-9;]*m//g' > build/reports/$f.raw.validate.txt
done
```

| Bước | Vì sao | Đã đo |
|---|---|---|
| `dedup --materials false` | Gộp accessor và mesh giống hệt nhau, **giữ tên vật liệu** (ghi đè và màu nắp tra theo tên) | 48/45 vật liệu, tên giống bản thô |
| `prune --keep-leaves true` | Giữ empty lá (`anim_roll_axis_*` khi không có con, pivot) | 354/207 node giữ nguyên |
| `meshopt --level high` | = reorder + quantize (vị trí 14 bit, pháp tuyến 10 bit, lưới lượng tử theo từng mesh) + `EXT_meshopt_compression` (FILTER) + `KHR_mesh_quantization` | 23,7 → 5,79 MB; 8,4 → 1,98 MB |
| `--vertex-layout separate` | BufferAttribute thường, không xen kẽ (interleaved), cho three-mesh-bvh và clipping | — |

**Cấm:**
- `gltf-transform optimize` mặc định: flatten + join + palette phá cây node và tên vật liệu.
- `gltfjsx --transform`.
- `instance`.
- Draco (giải mã từ CDN).
- `KHR_meshopt_compression`: three-stdlib không đọc.

**Hệ quả của quantize** (đã đo, code phải chịu được):
- TRS của node mesh bị ghi lại.
- 4 node mesh có con thành `Object3D` cùng tên, còn mesh nằm ở node con **không tên**: `int_valve_bolt`, `int_sc_disc`, `int_pump_gear_top`, `int_pump_gear_bottom`.
- `check_glb` kiểm đúng danh sách 4 node này.

### 3.3 Sinh dữ liệu: `web/tools/make_data.py` (Python 3, chỉ thư viện chuẩn)

Port từ `web/dot1/gen_drafts.py`, khác ở hai điểm:
1. Tên node đọc từ `build/reports/glb_analysis.json`, không đọc từ báo cáo probe.
2. `closed` lấy từ phép kiểm của `check_glb analyze`.

Đầu vào: `model-contract.json`, `design/parts.json`, `anim/shots.json`, `glb_analysis.json`. Đầu ra ở `build/data/`. **Kết quả phải trùng với các file `web/dot1/*.dot1.json`.** Đó là phép kiểm của task A4, trừ khi contract đổi.

#### 3.3.1 Luật đổi tên contract → tên đã xuất

| Contract | Tên thật | Ghi chú |
|---|---|---|
| `p_<x>` | `<x>` | tên object Blender (contract cũ đặt tiền tố cho bản sao trong Blender; phương án C không còn bản sao) |
| `rot_screw_a`, `rot_screw_b` (trong `show_whole`) | `int_screw_axis_a`, `int_screw_axis_b` | là empty đã xuất; pivot runtime vẫn có tên `rot_screw_a/b` (mục 3.3.4) |
| `<tiền tố>_NN..MM` | mở rộng từng số, giữ số chữ số | ví dụ `p_int_sc_screens_01..12` |
| `dev_<id>`, `ih_<id>`, `sec_<g>` | không phải node glTF | nhóm tạo lúc chạy |

**Tên nào không tra được thì dừng lỗi (exit 1).** Không có ngoại lệ slice, vì Đợt 1 xuất toàn bộ phần bên trong.

#### 3.3.2 `devices.json`

```json
{ "version": 1, "slice": 1, "size_mm_axes": "three X (dọc dòng chảy), Y (cao), Z (sâu)",
  "sections": [ { "group": "barrel", "name_vi": "Xi lanh và trục vít" }, … 10 mục ],
  "devices": [ { "device_id": "barrel_b3", "group": "barrel", "name_vi": "Xi lanh B3 – 6D …", "name_en": "…",
      "synthetic": false, "function_vi": "…", "details_vi": ["…"], "connects_to": [ {"part": "…", "interface_vi": "…"} ],
      "bbox_m": [1.69, 0.88, -0.32, 2.704, 1.52, 0.32], "size_mm": [1014, 640, 640],
      "has_interior": true, "nodes": ["anim_vent_window_1", "barrel_b3", "int_barrel_hollow_b3"] }, … 190 mục ] }
```

**Nguồn:**
- `bbox_m`, `name_*`, `group`, `synthetic` lấy từ contract `devices` (toạ độ three, mét).
- `function`, `details`, `connects_to` lấy từ `parts.json`. 4 thiết bị tổng hợp không có văn bản chi tiết.
- `nodes` = mọi node có `device_id` đó trong `node_map`.

#### 3.3.3 `node_map.json` (bảng node → thiết bị, dựng từ tên ĐÃ XUẤT)

```json
{ "version": 1, "counts": { "line": 354, "interior": 207, "devices": 190 },
  "nodes": {
    "barrel_b1":            { "file": "line", "device_id": "barrel_b1", "kind": "part", "closed": true },
    "ctx_roll_top":         { "file": "line", "device_id": "ctx_roll_top", "kind": "part", "closed": false, "cap": "force" },
    "anim_roll_axis_top":   { "file": "line", "device_id": "ctx_roll_top", "kind": "pivot" },
    "int_screw_axis_a":     { "file": "interior", "device_id": "screws", "kind": "pivot", "role": "pivot", "slice": 1 },
    "int_barrel_hollow_b3": { "file": "interior", "device_id": "barrel_b3", "kind": "interior", "role": "full", "slice": 1,
                              "states": ["CUT_Z_BARREL", "ST1_Z_FULL", "FREE", "CUT_X2450"], "closed": true },
    "int_pump_gear_top":    { "file": "interior", "device_id": "melt_gear_pump", "kind": "interior", "role": "cut_only",
                              "slice": 2, "states": ["CUT_PUMP"], "moves_in_dot2": "rotor", "closed": true } } }
```

**Nguồn:**
- `line`: `device_id` lấy từ contract `object_to_device` (351 khoá). 3 empty trục cán gán cho thiết bị trục cán tương ứng.
- `interior`: `device_id` (chủ), `role`, `states`, `slice` lấy từ `interior_export.items`. Mục "(origin)" chỉ thêm `moves_in_dot2`.
- `closed`: phép kiểm hàn đỉnh (mục 3.4).
- `cap: "force"` cho 3 trục cán: lưới hở 192 cạnh biên ở lỗ cổ trục, bị cổ trục che (quyết định mở Q2).

#### 3.3.4 `rotors.json`

Mỗi rotor:
- tạo `Object3D` tên `pivot` tại `pivot_m` (three, mét, không xoay) trong `dev_<device_id>`;
- `attach()` các node trong `attach`;
- quay bằng `rotateOnAxis(axis, 2π·rpm/60/display_slow·dt)`.

| id (`pivot`) | slice | `attach` | `pivot_m` | `axis` | rpm | chậm |
|---|---|---|---|---|---|---|
| `screw_a` (`rot_screw_a`) | 1 | `int_screw_axis_a` (+ 38 con) | [0, 1.2, −0.071] | [1, 0, 0] | −300 | 20 |
| `screw_b` (`rot_screw_b`) | 1 | `int_screw_axis_b` | [0, 1.2, 0.071] | [1, 0, 0] | −300 | 20 |
| `motor_shaft` | 1 | `drive_motor_shaft` | [−3.025, 1.2, 0] | [1, 0, 0] | −1 119 | 20 |
| `flex_coupling` | 1 | `drive_flex_coupling` | [−2.825, 1.2, 0] | [1, 0, 0] | −1 119 | 20 |
| `safety_coupling` | 1 | `drive_safety_coupling` | [−2.5085, 1.2, 0] | [1, 0, 0] | −1 119 | 20 |
| `roll_bottom` / `_middle` / `_top` | 1 | `anim_roll_axis_<r>` (+ 3 vạch) và `ctx_roll_<r>` | [9.776, 0.799 / 1.601 / 2.403, 0] | [0, 0, −1] | +9,95 / −9,95 / +9,95 | 1 |
| `pump_gear_top` / `_bottom`, `gbx_input`, `gbx_counter` | 2 | node tương ứng | như contract | | | không chạy ở Đợt 1 |

**Đã kiểm:**
- `pivot_m` của vít và trục cán trùng vị trí thế giới của empty đã xuất (`int_screw_axis_a` có translation [0, 1.2, −0.071]; `anim_roll_axis_bottom` có [9.776, 0.799, 0]).
- Các empty không xoay.

#### 3.3.5 `cut_states.json` (nháp đã sinh: `web/dot1/cut_states.dot1.json`)

**Khoá của một trạng thái cố định:**
- `label_vi`;
- `plane` `{normal, constant}`: three.js giữ điểm có `normal·p + constant ≥ 0`;
- `needs_interior`;
- `hide`, `swap {ngoài: [trong]}`, `clip`, `show_whole`, `show_clipped`, `ghost`;
- `peel {offset_m, duration_s}`;
- `camera {pos, target, lens_mm, sensor_mm: 36, source}`.

**FREE:**
- `hide` và `swap` (= contract `free_swap`, 19 cặp);
- `show_roles: ["full"]`, `hide_roles: ["cut_only", "ghost", "marker"]`;
- `axis_default`, `offset_default_m`, `slider_range_m` (= `line_extent_m`: x [−5,72; 12,5], y [0; 6,3], z [−2,8; 4,9]).

| Trạng thái | Mặt phẳng | hide | swap | clip | show_whole | show_clipped | ghost | peel |
|---|---|---|---|---|---|---|---|---|
| FULL | — | 0 | 0 | 0 | 0 | 0 | 0 | — |
| CUT_FEED | n [0, 0, 1], c 0 | 0 | 4 (`feed_throat` → `int_feed_column_hollow`; phễu, ống mềm, ống xuống → []) | 2 | 0 | 1 | 0 | [0, 0.6, −1.2] 1,4 s |
| CUT_Z_BARREL | n [0, −1, 0], c 1.2 | 52 (sàn thao tác, cấp liệu, vòm, đường chân không…) | 9 (6 xi lanh → hollow; đầu, van, adapter lọc → bộ `_lo`) | 26 (vỏ che, vỏ nhiệt, mặt bích, cáp) | 2 pivot + 64 phần tử + 2 trục then hoa + 9 khối nhựa `_lo` + 9 bộ `_lo` đầu/van/adapter + 2 ghost + 2 cửa sổ | 6 hollow | 2 vòm | [0, 2.2, 0] 1,6 s |
| CUT_X2450 | n [−1, 0, 0], c 2.45 | 56 (B4, vỏ, phần tử 12–32, 9 khối nhựa) | 1 (B3) | 13 | phần tử 1–11, trục then hoa, 2 phần tử `12_x2450`, 2 nắp `xsec_2450`, khối nhựa `x2450` | 1 | 0 | [1.5, 0.4, 0] 1,5 s |
| CUT_X4120 | n [−1, 0, 0], c 4.12 | 35 | 2 (B5, vòm 2) | 13 | phần tử 1–21, `22_x4120`, `xsec_4120`, khối nhựa `x4120` | 2 | 0 | [1.5, 0.4, 0] 1,5 s |
| FREE | runtime x/y/z | 16 (khối nhựa XẢ của van, đĩa lọc + 12 lưới + hốc) | 19 | mọi thứ đang hiện | theo vai trò `full` | — | — | — |

**Camera preset** (`shots.json`, đổi `(x, y, z)` của Blender → `(x, z, −y)`):

| Trạng thái | Nguồn | pos | target | lens |
|---|---|---|---|---|
| FULL | S01 khoá 2 (khung 151) | [2.5, 5.0, −10.0] | [3.0, 1.4, 0] | 30 mm |
| CUT_FEED | S03b khoá 2 (khung 900) | [1.3, 1.95, −2.0] | [0.34, 1.45, 0] | 40 mm |
| CUT_Z_BARREL | S04 khoá 3 (khung 1161) = ảnh tham chiếu `A1a-S04-f1161` | [1.75, 2.3, −1.6] | [1.85, 1.2, 0] | 40 mm |
| CUT_X2450 | ST2 (= S05 khoá 2) | [3.05, 1.45, −0.42] | [2.45, 1.2, 0] | 60 mm |
| CUT_X4120 | ST3 (= S07 khoá 2) | [4.75, 1.95, −0.85] | [4.12, 1.55, 0] | 38 mm |
| FREE | giữ camera hiện tại | | | |

**Phép kiểm khi sinh (dừng lỗi nếu sai):**
- `hide ∩ (show_whole ∪ show_clipped ∪ ghost) = ∅`;
- mọi giá trị `swap` đều có trong một danh sách show;
- `clip ∩ hide = ∅`;
- không có node `cut_only` nào được hiện ngoài `states` của nó;
- **luật loại trừ:** không trạng thái nào hiện cả một node lẫn bản cắt sẵn hoặc bản sao rỗng của nó. Cụ thể là các cặp `swap`, và các cặp `X` / `X_lo` / `X_y0` / `X_x2450` / `X_x4120`, `int_screw_elem_*_12` / `_12_x2450`, `_22` / `_22_x4120`.

#### 3.3.6 `materials.json`

Tên vật liệu → `{web, cap_class, cap_color, three_override?}` lấy từ contract `materials` (79 mục, bỏ `ze_floor`).

| Vật liệu | Xử lý ở Đợt 1 |
|---|---|
| `ze_sheet_pet` | `MeshPhysicalMaterial` `#7FB7B0`, trong mờ 0,35, không ghi depth, DoubleSide |
| `ze_melt_curtain` | `#ED9E38`, emissive `#7A2E00` 0,4, trong mờ 0,8 |
| `za_ghost_vent` | GhostMaterial (snippet §10) |
| `za_fill_melt` | giữ màu hổ phách đã xuất; `transparent`, opacity 0,6, không ghi depth, **DoubleSide**. FillMaterial để Đợt 2 |
| `za_sc_screenpack`, `za_sc_breaker` | PBR phẳng như snippet §2 (chỉ hiện ở Đợt 2) |
| còn lại (73) | giữ nguyên |

**Mặt (side) và nắp:**
- Lưới kín: `FrontSide` (exporter ghi `doubleSided: true` cho mọi vật liệu trừ `za_fill_melt`).
- Lưới hở: bản sao DoubleSide có chiếu sáng, không nắp.
- Nắp runtime có màu `cap_color` theo **vật liệu của từng mesh con**: thép `#B84533` có vân chéo, vít `#99362A`, cao su `#3A3A3A`, cách nhiệt `#BFB89E`, nhựa `#ED9E38`.
- `cap_color = null` (kính, ghost, `none`) thì không có nắp.

### 3.4 `web/tools/check_glb.mjs` (Node ESM, three r186 + MeshoptDecoder)

Port từ `web/build/probe/scripts/load_check.mjs` và `closed_check.mjs`.

**`node tools/check_glb.mjs analyze`** → `build/reports/glb_analysis.json`:

| Kiểm | Ngưỡng (hỏng thì exit 1) |
|---|---|
| Tải cả GLB thô và GLB nén bằng GLTFLoader + MeshoptDecoder | không exception |
| Tên: mọi node có `userData.name`; `name === sanitize(userData.name)`; không trùng trong file và giữa hai file | 0 đổi tên, 0 trùng |
| Số đếm so với `export.json` | `line` 354 node / 351 mesh / 3 empty / 771 mesh three / 1 189 654 tam giác; `interior` 207 / 205 / 2 / 438 / 413 006. Sai lệch thì exit 1 (contract đổi thì cập nhật kỳ vọng có chủ ý) |
| Quantize tách node | đúng tập {`int_valve_bolt`, `int_sc_disc`, `int_pump_gear_top`, `int_pump_gear_bottom`} |
| Lệch bbox thế giới giữa bản thô và bản nén, theo từng node có tên | ≤ 1 mm (đo 0,49 mm) |
| Lưới kín trên GLB thô: hàn đỉnh theo vị trí (6 chữ số thập phân), gộp mọi primitive của payload | ghi `closed`, `boundary`, `flipped`, `multi`, `vol` cho từng node |
| Vật liệu | tên giống bản thô; có đủ tên cần ghi đè |
| Morph | 4 node có `gap_x10`, `lip_push` |
| Validator | file `*.validate.txt` có "No errors found." và "No warnings found." |
| Dung lượng | nén: `line` ≤ 7 MB, `interior` ≤ 2,5 MB |

**`node tools/check_glb.mjs verify`** (chạy sau `make_data`) → `build/reports/check.json`:
- Mọi node trong `node_map` có trong đúng file của nó, và mọi node có tên trong GLB đều có trong `node_map`: 0 mồ côi, 0 thiếu.
- Mọi tên trong `cut_states` (cả khoá và giá trị `swap`) và trong `rotors[].attach` đều tra được.
- Chạy lại toàn bộ phép kiểm luật loại trừ của mục 3.3.5.
- 190 thiết bị, mỗi thiết bị ≥ 1 node; 189 thiết bị có ít nhất một node `line`.
- `pivot_m` của rotor có empty thì lệch ≤ 1 mm so với vị trí thế giới của empty đó.
- **Thất bại:** ghi `failures[]` (mỗi mục có mã và tên), in tóm tắt, exit 1. `make` dừng và không publish.
- **Phép thử âm tính** của task A5: sửa một tên trong một bản sao `cut_states.json` thì `verify` phải exit 1.

### 3.5 Một lệnh: `web/Makefile`

```make
# make -C web all   (cwd = web/)
BLENDER ?= /Applications/Blender.app/Contents/MacOS/Blender
BLEND   := ../out/ze155_anim.blend
GT      := tools/node_modules/.bin/gltf-transform
FILES   := line interior

all: export compress analyze data verify publish

tools/node_modules: tools/package.json
	cd tools && npm i

export:
	mkdir -p build/raw build/reports
	stat -f '%m %z' $(BLEND) > build/reports/blend_before.txt
	$(BLENDER) -b --factory-startup --python-exit-code 1 $(BLEND) --python tools/export_glb.py -- \
	  --rules web/dot1/selection-rules.json --file all --out web/build/raw --report web/build/reports/export.json --tris
	stat -f '%m %z' $(BLEND) | diff - build/reports/blend_before.txt

compress: tools/node_modules
	mkdir -p build/tmp build/models
	for f in $(FILES); do \
	  $(GT) dedup build/raw/$$f.glb build/tmp/$$f.1.glb --materials false --vertex-layout separate && \
	  $(GT) prune build/tmp/$$f.1.glb build/tmp/$$f.2.glb --keep-leaves true --keep-attributes false --vertex-layout separate && \
	  $(GT) meshopt build/tmp/$$f.2.glb build/models/$$f.glb --level high --vertex-layout separate && \
	  $(GT) validate build/models/$$f.glb | sed 's/\x1b\[[0-9;]*m//g' > build/reports/$$f.validate.txt && \
	  $(GT) validate build/raw/$$f.glb | sed 's/\x1b\[[0-9;]*m//g' > build/reports/$$f.raw.validate.txt || exit 1; \
	done

analyze: tools/node_modules
	node tools/check_glb.mjs analyze

data:
	python3 tools/make_data.py

verify:
	node tools/check_glb.mjs verify

publish:
	mkdir -p web-check/public/models web-check/public/data
	cp build/models/line.glb build/models/interior.glb web-check/public/models/
	cp build/data/*.json web-check/public/data/

clean:
	rm -rf build/tmp
```

`make -C web all` mất khoảng 3 s (xuất) + 3 s (nén) + vài giây (kiểm, sinh dữ liệu).

---

## 4. Luồng B: sandbox `web/web-check/`

### 4.1 Cây file

```
web/web-check/
  index.html  package.json  vite.config.ts  tsconfig*.json   (mẫu create-vite react-ts; giữ StrictMode)
  public/models/line.glb  interior.glb
  public/data/devices.json  node_map.json  cut_states.json  rotors.json  materials.json
  src/
    main.tsx              App.tsx            store.ts            data.ts
    scene/
      Models.tsx          (LineModel, InteriorLoader)
      rig.ts              (rigLine, rigInterior, Registry `reg`, payload)
      materials.ts        (ghi đè, side theo closed, màu nắp)
      Picking.ts          (BVH, filteredRaycast, emptyRaycast, handler chuột)
      Cuts.ts             (setVisible, resetCuts, applyState, biến thể cắt + nắp, precompile)
      FreeClip.ts         (enterFree, setFreeOffset, leaveFree)
      Peel.ts             (lột vỏ runtime)
      GhostMaterial.ts    (snippet §10)
      Selection.tsx       (Outlines, Box3Helper)
      CameraRig.tsx       (CameraControls, preset, fitToBox)
      Rotors.tsx          (pivot, useFrame)
      Ground.tsx
    ui/
      Toolbar.tsx  DeviceTree.tsx  InfoPanel.tsx  LoadingBadge.tsx  text.ts  ui.css
    test/
      hooks.ts            (window.__ze, ?selfcheck)
```

### 4.2 Trách nhiệm và API từng module

#### 4.2.1 `data.ts`

```ts
export type V3 = [number, number, number]
export type StateId = 'FULL' | 'CUT_FEED' | 'CUT_Z_BARREL' | 'CUT_X2450' | 'CUT_X4120' | 'FREE'
export interface NodeRec { file: 'line' | 'interior'; device_id: string; kind: 'part' | 'interior' | 'pivot';
  role?: 'full' | 'cut_only' | 'ghost' | 'marker' | 'pivot'; closed?: boolean; cap?: 'force' | 'none'; states?: string[]; slice?: 1 | 2 }
export interface CameraPreset { pos: V3; target: V3; lens_mm: number; sensor_mm: number }
export interface CutState { label_vi: string; plane: { normal: V3; constant: number } | null; needs_interior: boolean
  hide: string[]; swap: Record<string, string[]>; clip: string[]; show_whole: string[]; show_clipped: string[]; ghost: string[]
  peel: { offset_m: V3; duration_s: number } | null; camera: CameraPreset | null }
export interface FreeState { label_vi: string; needs_interior: true; hide: string[]; swap: Record<string, string[]>
  show_roles: string[]; hide_roles: string[]; axis_default: 'x' | 'y' | 'z'; offset_default_m: Record<'x'|'y'|'z', number>
  slider_range_m: Record<'x'|'y'|'z', [number, number]> }
export interface Data { devices: DevicesJson; nodes: Record<string, NodeRec>; states: Record<StateId, CutState | FreeState>
  rotors: RotorRec[]; materials: MaterialsJson }
export const dataPromise: Promise<Data>   // fetch 5 file song song, một lần; dùng React 19 `use(dataPromise)` trong Suspense
```

#### 4.2.2 `Models.tsx`

- **`LineModel`:**
  - `useGLTF('/models/line.glb', false, true)`: tắt Draco, bật meshopt. three-stdlib 2.36.1 đã kiểm: 354 tên đúng, 771 mesh.
  - Trong `useLayoutEffect`: `rigLine(gltf.scene, data, gl)`, chạy được nhiều lần.
  - `<primitive object={gltf.scene} onPointerMove onPointerOut onClick onDoubleClick />`.
  - `useGLTF.preload` chỉ cho `line`.
- **`InteriorLoader`:**
  - chỉ mount khi `store.interiorWanted`, trong `<Suspense>`;
  - `useGLTF('/models/interior.glb', false, true)` → `rigInterior(gltf.scene, data, gl)` → `store.setInteriorLoaded(true)` → giải `reg.interiorReady`;
  - trả `null` (node đã chuyển sang cây `line`).
- **Không prefetch `interior.glb`** (tiêu chí D12).

#### 4.2.3 `rig.ts`: Registry, nhóm thiết bị, payload, pivot

```ts
export interface Part { name: string; meta: NodeRec; node: THREE.Object3D; payload: THREE.Object3D | null; meshes: THREE.Mesh[] }
export interface Device { id: string; rec: DeviceRec; group: THREE.Group; parts: Part[] }
export interface Rotor { rec: RotorRec; pivot: THREE.Object3D; axis: THREE.Vector3; angle: number; ready: boolean }
class Registry {
  data!: Data; gl!: THREE.WebGLRenderer; lineScene: THREE.Object3D | null = null
  parts = new Map<string, Part>(); devices = new Map<string, Device>(); rotors: Rotor[] = []
  unknownNodes: string[] = []; missingNodes: string[] = []
  interiorLoaded = false; interiorReady: Promise<void>   // giải khi rigInterior xong
  partOfObject(o: THREE.Object3D | null): Part | null    // đi lên tới userData.ze.part đầu tiên
  deviceOfObject(o: THREE.Object3D | null): string | null
  meshesOfDevice(id: string, visibleOnly = true): THREE.Mesh[]   // từ device.parts, KHÔNG từ duyệt cây
  boxOfDevice(id: string, visibleOnly = true): THREE.Box3
  boxOfPart(name: string): THREE.Box3
}
export const reg: Registry
export function rigLine(scene: THREE.Object3D, data: Data, gl: THREE.WebGLRenderer): void
export function rigInterior(scene: THREE.Object3D, data: Data, gl: THREE.WebGLRenderer): void
```

**`rigLine`:**
1. `scene.userData.zeRigged` đã có thì return (StrictMode chạy useMemo/useLayoutEffect hai lần ở dev).
2. Gọi `scene.updateMatrixWorld(true)`. Gom các node có `userData.name`. Tên không có trong `node_map` thì vào `unknownNodes`; tên của file `line` có trong `node_map` mà thiếu trong GLB thì vào `missingNodes`. Cả hai đều in `console.error` và hiện trong `selfcheck`.
3. **Chuẩn hoá cha có mesh** (no-op với GLB nén, cần cho GLB thô): node có tên là `Mesh` và có con có tên → tạo `Object3D` cùng tên và cùng TRS thay chỗ nó; mesh thành con (transform đơn vị, `userData.name` bị xoá); các con có tên chuyển sang Object3D mới.
4. Tạo 10 `sec_<group>` và 190 `dev_<id>` (cả `dev_screws`) dưới `scene`, transform đơn vị, `userData.ze = {kind, device_id}`.
5. Với mỗi node gốc của `line` (con trực tiếp của `scene`): `reg.devices.get(meta.device_id).group.attach(node)`. Con của node (vạch trục cán) đi theo cha.
6. **Payload** của mỗi chi tiết (`kind` là `part` hoặc `interior`):
   - node là `Mesh` → payload = node;
   - node là `Group` chỉ gồm mesh không tên (nhiều vật liệu) → payload = node;
   - node có con có tên (4 node bị quantize tách) → payload = con **không tên** duy nhất (Group hoặc Mesh);
   - `kind: 'pivot'` → payload = `null`.

   Sau đó `meshes` = các mesh trong payload, đặt `mesh.userData.ze = {part: name}` và `node.userData.ze = {...meta, name}`.
7. Pivot rotor có đủ node `attach` trong file này (động cơ, khớp nối, trục cán): `pivot = new Object3D()`, `pivot.name = rec.pivot`, đặt `position = pivot_m`, thêm vào `dev_<device_id>`, `updateMatrixWorld`, rồi `pivot.attach(node)` cho từng node.
8. `prepareMaterials(scene)` (4.2.4), `installRaycastFilter(scene, gl)` (4.2.5), ghi `reg.lineScene`, `reg.gl`. Đặt `scene.userData.zeRigged = true`.

**`rigInterior`:** cũng các bước 1–3 và 6–8, khác ở chỗ:
- mỗi node gốc của `interior` được attach vào `dev_<device_id>` **của cây `line`**;
- mọi payload của `interior` đặt `visible = false` ngay. Đây là trạng thái lúc tải, không ghi lại, nên `resetCuts` trả về đúng trạng thái này;
- rotor `screw_a/b` được tạo tại đây (attach `int_screw_axis_a/b`);
- `installRaycastFilter(reg.lineScene, gl)` chạy lại (idempotent), rồi gọi `precompileStates` lúc rảnh.

**Chi phí đo trong Node:** attach 1,4 ms + 0,3 ms; BVH `CENTER` 332 + 74 ms.

#### 4.2.4 `materials.ts`

Theo snippet §2, đổi như sau:
- Bảng ghi đè đọc từ `materials.json`.
- `mesh.userData.capColor = materials[mesh.material.name].cap_color`.
- `closed` hiệu dụng = `(meta.closed && meta.cap !== 'none') || meta.cap === 'force'`.
- Lưới hở dùng bản sao DoubleSide dùng chung theo uuid của vật liệu gốc.
- Lưới kín đặt `src.side = FrontSide`.
- `za_fill_melt` theo bảng ở mục 3.3.6.

Chạy một lần cho mỗi scene (WeakSet).

#### 4.2.5 `Picking.ts`

Giữ thiết kế C1/N1 của snippet §3 (lọc trong `mesh.raycast`, không dùng drei `<Bvh>`, kiểm "đã gắn" bằng so khớp hàm). Thay đổi:
- **BVH dùng `strategy: CENTER`**: 0,41 s tổng, so với `SAH` 1,56 s (đo). `maxLeafTris` 10, `setBoundingBox` true. Mỗi geometry dùng chung chỉ dựng một lần. Ghi tổng thời gian vào `reg.stats.bvh_ms`.
- `filteredRaycast`: `if (!this.visible) return false` để cắt cả nhánh con. Ghost thì `return`. Sau đó gọi `acceleratedRaycast` và bỏ các điểm trúng ở phía đã cắt của mọi mặt phẳng trong `material.clippingPlanes` (gồm cả `freePlane`) và `renderer.clippingPlanes` (luôn rỗng ở Đợt 1, giữ cho chắc). Không bao giờ đặt `firstHitOnly`.
- `emptyRaycast` cho node không phải mesh: trả `false` khi `!visible`. Trong thực tế chỉ payload Group bị ẩn.
- Helper (hull của Outlines, bản sao peel, `Box3Helper`, ground) gán `noRaycast`.
- `unfilteredMeshes(root)` cho `selfcheck().rayUnfiltered`.

**Handler chuột:**
- `onPointerMove`: `stopPropagation`, rồi `hover(reg.deviceOfObject(e.object))`.
- `onClick`: bỏ qua nếu `e.delta > 4` (đang kéo xoay); Alt thì `select(device, part.name)`, không thì `select(device)`.
- `onDoubleClick`: `zoomTo(device)`.
- `onPointerMissed` trên Canvas: `clear()`.
- Phím: F gọi `zoomTo(selected)`, Esc gọi `clear()`; bỏ qua khi focus đang ở ô nhập liệu.

#### 4.2.6 `Cuts.ts`, `FreeClip.ts`, `Peel.ts`

```ts
export function setVisible(o: THREE.Object3D, v: boolean): void      // ghi giá trị gốc lần đầu; chỉ gọi cho payload
export function setPartVisible(p: Part, v: boolean): void            // payload; pivot thì không làm gì
export function partVisible(p: Part): boolean
export function clipPart(p: Part, planes: THREE.Plane[], key: string): void   // biến thể cắt cho từng mesh (snippet §6 cutVariant)
export function ghostPart(p: Part): void
export function resetCuts(gl: THREE.WebGLRenderer): void            // khôi phục vật liệu + visible, gỡ freePlane, dừng peel
export async function applyState(id: Exclude<StateId, 'FREE'>, o?: { peel?: boolean; camera?: boolean }): Promise<void>
export async function precompileStates(gl, scene, camera): Promise<void>  // mỗi trạng thái: apply (không peel, không camera) + gl.compileAsync
// FreeClip.ts
export async function enterFree(axis: 'x'|'y'|'z', offset: number, flip: boolean): Promise<void>
export function setFreeOffset(offset: number): void                 // chỉ đổi freePlane.constant
export function setFreeAxis(axis: 'x'|'y'|'z', flip: boolean): void // đổi normal + constant, không dựng lại vật liệu
export async function leaveFree(back: Exclude<StateId, 'FREE'>): Promise<void>  // resetCuts → applyState(back, {peel:false, camera:false})
// Peel.ts
export function startPeel(parts: Part[], plane: THREE.Plane, offset: V3, duration: number): void
export function stopPeel(): void
```

**`applyState(id)`, theo đúng thứ tự:**
1. `resetCuts`.
2. Nếu `needs_interior` mà chưa tải: `store.requestInterior()`, rồi `await reg.interiorReady`.
3. `hide`: `setPartVisible(false)`.
4. `swap`: ẩn khoá. Giá trị không tra được thì giữ khoá và cắt nó (`missing_target_rule`; ở Đợt 1 không xảy ra, nhưng giữ để chắc chắn).
5. `clip`: `clipPart(plane)`.
6. `show_whole`: `setPartVisible(true)`; pivot thì bỏ qua.
7. `show_clipped`: hiện + `clipPart`.
8. `ghost`: hiện + `ghostPart`.
9. `peel` (nếu `o.peel !== false`): `startPeel(clip ∪ khoá swap có giá trị, plane, offset, duration)`.
10. Camera (nếu `o.camera !== false`): `applyPreset(state.camera, smooth)`.

**Bất biến:**
- Chỉ payload đổi `visible`, nên không cần `showChain`: tổ tiên không bao giờ bị ẩn.
- Biến thể cắt dùng DoubleSide; nắp vẽ ở mặt sau, có vân chéo theo `gl_FragCoord` (snippet §6). `customProgramCacheKey` là `'ze-cap'`.
- Lưới hở và `cap_color = null` thì cắt mà không có nắp.

**FREE:**
1. `resetCuts`, rồi chờ interior nếu chưa tải.
2. Đặt **một** `THREE.Plane` dùng chung `freePlane` (module-level) với `AXES = {x: [−1,0,0], y: [0,−1,0], z: [0,0,−1]}`; khi lật thì đổi dấu normal và constant. **Không dùng `renderer.clippingPlanes`** như snippet §7: mặt phẳng chung của renderer cắt cả ground, `Box3Helper` và hull viền. Vật liệu cắt giữ tham chiếu tới cùng instance `freePlane`, three chiếu lại mặt phẳng mỗi khung, nên đổi `constant` hay `normal` là mọi vật liệu thấy ngay.
3. Hiện payload của các node `interior` có `role` trong `show_roles` (gồm cả slice 2: đầu xi lanh, van, adapter, bơm `_full`, kênh lọc, trộn tĩnh). Node có `role` trong `hide_roles` vẫn ẩn như lúc tải.
4. `hide` (16).
5. Ẩn khoá `swap`.
6. `clipPart(p, [freePlane], 'free')` cho **mọi chi tiết đang hiện** (cache biến thể theo khoá `'free'`).

Kéo thanh trượt chỉ đổi `constant`, không dựng lại vật liệu.

**Peel (lột vỏ):** theo snippet §6.
- Bản sao `new Mesh(mesh.geometry, mat)`; `mat` = vật liệu gốc `.clone()` với `clippingPlanes = [plane.clone().negate()]`, `transparent`.
- Đặt `matrixWorld` từ mesh gốc (decompose).
- Đánh dấu `__helper`, gán `noRaycast`, thêm vào nhóm `peel` ở `lineScene`.
- Trong `duration_s`: dời theo `offset_m` (easing `smoothstep`), `opacity` từ 1 về 0.
- Xong thì dispose vật liệu, giữ geometry.
- `resetCuts` gọi `stopPeel`.
- `cutRoundTrip`, `timeState` và `precompile` chạy với `peel: false`.

#### 4.2.7 `Selection.tsx` và `CameraRig.tsx`

- **Viền (Outlines):** theo snippet §4. drei `Outlines` `screenspace={false}` (độ dày pixel), `clippingPlanes = (mesh.material.clippingPlanes ?? [])` (gồm `freePlane` khi ở FREE). Hull được đánh dấu helper và tắt raycast.
  - Di chuột: `#9fd3ff` 2 px, `angle 0`.
  - Chọn: `#ff8a1f` 3 px, `angle π` (creased).
  - Danh sách mesh = `reg.meshesOfDevice(id)` (chỉ mesh đang hiện); nếu Alt thì là mesh của chi tiết đó.
- **Hộp bao:** `Box3Helper(reg.boxOfDevice(id))` màu cam, tính lại khi trạng thái đổi. Thiết bị không có mesh nào đang hiện (ví dụ `screws` ở FULL): vẽ bbox của toàn bộ mesh bằng nét đứt, bảng thông tin ghi "Nằm bên trong – mở một mặt cắt để xem".
- **`CameraRig.tsx`:**
  - `CameraControls` `makeDefault`, `smoothTime` 0,35, ref ở module;
  - `applyPreset(p, smooth)`: `cam.filmGauge = 36; cam.setFocalLength(lens)`, rồi `controls.setLookAt(...pos, ...target, smooth)`;
  - `zoomTo(box)`: `fitToBox(box, true, {padding*: max(0,15; |size|·0,15)})`;
  - camera ban đầu = preset FULL; `near` 0,02, `far` 200.

#### 4.2.8 `Rotors.tsx`

- Đọc `reg.rotors` có `ready` (pivot vít sẵn sàng sau khi tải interior).
- `useFrame((_, dt))` với `step = min(dt, 0.1)`:
  - mode `off`: không quay;
  - `slow`: rpm/`display_slow`;
  - `real`: rpm.
- Gọi `pivot.rotateOnAxis(axis, 2π·rpm/60·k·step)` và cộng `rotor.angle`.
- Mặc định `slow`. Badge "Vít 300 vòng/phút – hiển thị chậm 20×".
- Rotor slice 2 không được tạo ở Đợt 1.

#### 4.2.9 `store.ts` (zustand 5)

```ts
interface Ui {
  hovered: string | null; selected: string | null; selectedPart: string | null
  state: StateId; prevFixed: Exclude<StateId, 'FREE'>; free: { axis: 'x' | 'y' | 'z'; offset: number; flip: boolean }
  rotorMode: 'off' | 'slow' | 'real'; interiorWanted: boolean; interiorLoaded: boolean; busy: boolean
  hover(id: string | null): void; select(id: string | null, part?: string | null): void; clear(): void
  zoomTo(id: string | null): void
  setStateId(id: StateId): Promise<void>      // gọi applyState / enterFree / leaveFree, rồi cập nhật state
  setFree(p: Partial<Ui['free']>): void       // setFreeOffset / setFreeAxis
  setRotorMode(m: Ui['rotorMode']): void; requestInterior(): void; setInteriorLoaded(v: boolean): void
}
```

#### 4.2.10 UI (chữ trên giao diện là tiếng Việt, nằm trong `ui/text.ts`)

**Toolbar (trên cùng):**
- Nút trạng thái lấy chữ từ `label_vi`:
  - "Toàn bộ (không cắt)";
  - "Cột cấp liệu cắt dọc (Y = 0)";
  - "Xi lanh mở nửa trên (Z = 1 200)";
  - "Mặt cắt ngang B3 (X = 2 450)";
  - "Mặt cắt ngang vùng chân không 2 (X = 4 120)";
  - "Mặt cắt tự do".
- Khi ở FREE:
  - "Trục cắt" X / Y / Z;
  - thanh trượt "Vị trí (m)" theo `slider_range_m`, hiện số mm;
  - "Lật phía giữ";
  - chú thích màu nắp.
- "Quay: Tắt / Chậm 20× / Thực tế".
- "Về góc nhìn của trạng thái".
- Nhãn "Đang tải phần bên trong…" khi `busy`.

**DeviceTree (trái):**
- 10 section theo `sections[].name_vi`, thiết bị xếp theo `name_vi`.
- Ô tìm "Tìm thiết bị (gõ không dấu cũng được)…". Chuẩn hoá: `normalize('NFD')`, bỏ `̀-ͯ`, `đ→d`, viết thường. So khớp trên `name_vi`, `name_en`, `device_id`.
- Bấm thì chọn + zoom; mục đang chọn được tô sáng và cuộn tới.

**InfoPanel (phải):**
- `name_vi` (đậm), `name_en`, nhóm, "Chức năng", "Chi tiết" (danh sách), "Nối với", "Kích thước (mm)" D × C × S từ `size_mm`.
- Khi Alt chọn chi tiết: "Chi tiết: `<tên>`".
- Dòng gợi ý: "Bấm đúp hoặc F: phóng to · Alt + bấm: chọn một chi tiết · Esc: bỏ chọn".

**Phông chữ:** dùng phông hệ thống, không tải font ngoài.

#### 4.2.11 `test/hooks.ts` (`window.__ze`)

| Hook | Trả về / việc làm |
|---|---|
| `ready: Promise<void>` | xong khi `line` đã rig và đã vẽ khung đầu |
| `stats(): Promise<{fps, calls, triangles, geometries, programs, devices, heap_mb, load: {line_first_frame_ms, interior_ready_ms, bvh_ms}}>` | đo trong 3 s; `calls` đọc sau một khung ở trạng thái hiện tại |
| `selfcheck()` | `{devices, parts, unknownNodes, missingNodes, orphans, rayUnfiltered, interiorLoaded, rotorsReady, dataVersion}` |
| `devices()`, `select(id, part?)`, `selectAll()`, `selection()` | `selection()` = `{hovered, selected, part, outlineMeshes, bbox}` |
| `clickAt(x, y, {alt?, dbl?})`, `pickAt(x, y)` | PointerEvent thật lên canvas; `pickAt` dùng cùng bộ lọc → `{device_id, part, point, backFace, cutOnly}` |
| `project(id)` | toạ độ màn hình của tâm bbox thiết bị |
| `pickSweep()` | với mỗi thiết bị: `fitToBox` tức thì, vẽ, lấy mẫu lưới 16 × 16 trong vùng màn hình của bbox, gọi `pickAt` → `{pickable, total, unpickable[]}` |
| `setState(id, {peel?, camera?})`, `setFreeClip(axis \| null, offset, flip?)` | Promise |
| `timeState(id)` | ms từ trước `applyState` tới sau 2 rAF; vào lần hai, không peel |
| `cutRoundTrip()` | FULL → FREE → FULL và mỗi trạng thái cố định → FREE → chính nó: so tập payload đang hiện, uuid vật liệu của từng mesh, và cuối cùng `gl.clippingPlanes` rỗng, không vật liệu nào còn `freePlane` → `{ok, bad[]}` |
| `capCheck(state, device, {axis?, offset?})` | áp trạng thái với camera preset của nó (FREE: trục/vị trí cho trước, rồi `fitToBox` thiết bị); lấy mẫu 24 × 24 pixel trong bbox màn hình của thiết bị; giữ điểm trúng nằm trên mặt phẳng (\|n·p + c\| < 2 mm) và là mặt sau (nắp runtime) hoặc mặt của một chi tiết `cut_only` (nắp cắt sẵn, ví dụ `int_xsec_a_2450`) → `{capPixels, correct, sample: {x, y}, ok: capPixels ≥ 5 && correct === capPixels}` |
| `rotors()`, `rotorTest(s)` | `[{id, angle, axis_world, rpm, slow}]`; `rotorTest` đo góc trong `s` giây ở chế độ `slow` → `[{id, expected, measured, err}]` |
| `camera(stateId)`, `orbitTest()` | áp preset; quay quanh 360° trong 5 s để đo trace |

`?selfcheck=1`: `dpr={1}`. Sau `ready`, chạy `selfcheck()` và in JSON vào `<pre id="selfcheck">` kèm dòng `SELFCHECK DONE`.

### 4.3 Chỗ đổi so với `r3f-snippets.md`

| Snippet | Đợt 1 |
|---|---|
| §1 Canvas | giữ (`localClippingEnabled`, NeutralToneMapping, Lightformer, không CDN). `InteriorModel` không render `<primitive>`; nó chỉ rig rồi trả `null` |
| §2 Registry | thay bằng `rig.ts`: `kind` lấy từ `node_map`, payload, `userData.ze`, thiết bị → chi tiết lấy từ dữ liệu chứ không duyệt cây. `materials.ts` giữ, đọc `materials.json` |
| §3 Picking | giữ C1/N1; BVH `CENTER`; `filteredRaycast` trả `false` khi ẩn; chi tiết lấy qua `mesh.userData.ze.part` |
| §4 Viền, §5 zoom | giữ; danh sách mesh lấy từ `reg.meshesOfDevice` |
| §6 Cắt | `cutVariant`, `setVisible` và `resetCuts` giữ. Bỏ `showChain` và việc bật/tắt `interiorRoot`; tên lấy thẳng từ `cut_states.json` (đã là tên thật) |
| §7 FREE | vai trò lấy từ `node_map`; `hide`/`swap` lấy từ `cut_states.FREE` |
| §8 Rotor | thay bằng pivot runtime từ `rotors.json` (không đọc `userData` của node) |
| §10 Ghost | giữ |
| §9, §11, §12, §13 | Đợt 2–3, không dùng |
| §14 hooks | mở rộng như mục 4.2.11 |

### 4.4 B làm việc trước khi A giao: stand-in

**Không làm `standin.glb` tổng hợp.** Probe đã sinh **GLB thật, đúng định dạng** và JSON nháp, sát dữ liệu thật hơn mọi bản tổng hợp. Người làm: planner (đã xong).

Ở task B1, B chép:
- `web/build/probe/models/line.glb`, `interior.glb` → `web-check/public/models/`;
- `web/dot1/devices.dot1.json` → `public/data/devices.json`; tương tự cho `node_map`, `cut_states`, `rotors`, `materials`, bỏ `.dot1`.

`closed` trong `node_map.dot1.json` đã là kết quả phép kiểm hàn đỉnh trên GLB thô của probe.

**Điểm tích hợp I1:** khi A5 xong, `make -C web publish` ghi đè đúng các đường dẫn đó. B chỉ tải lại trang và chạy lại `selfcheck`. Định dạng giống hệt, vì `make_data.py` được kiểm bằng cách so với các file nháp.

### 4.5 Lệnh

```bash
cd /Users/manhhaycode/m3d-e2e/ze155-tdie/web
npm create vite@9.2.1 web-check -- --template react-ts      # mẫu: React ^19.2.8, TS ~6.0.2, Vite ^8.3.0, StrictMode
cd web-check
npm i -E react@19.3.0 react-dom@19.3.0 three@0.186.1 @react-three/fiber@9.8.1 @react-three/drei@10.7.9 \
        three-mesh-bvh@0.8.3 zustand@5.0.15
npm i -D -E @types/three@0.186.0 @types/react@19.3.0 vite@8.3.2 @vitejs/plugin-react@6.1.1
npm ls three three-mesh-bvh          # phải chỉ có một bản three 0.186.1 và một bản three-mesh-bvh 0.8.3 (drei cần ^0.8.3; bản mới nhất 0.9.15 KHÔNG dùng)
npm run dev -- --port 5178 --strictPort
npm run build && npx vite preview --port 5179 --strictPort   # kiểm bản build (không phải tiêu chí chính)
```

- R3F 9.8.1 yêu cầu `react >=19 <19.4`, vì vậy ghim chính xác (`-E`) 19.3.0.
- TypeScript giữ bản của mẫu (~6.0.2).

---

## 5. Chia việc

Hai builder chạy song song. Reviewer và fixer là agent riêng; reviewer không sửa, builder không tự nghiệm thu bản cuối.

### Luồng A (builder A)

| Task | Phụ thuộc | Vào | Ra | Nghiệm thu | Công |
|---|---|---|---|---|---|
| **A1** Công cụ + xuất | — | `web/dot1/export_glb.py`, `selection-rules.json` | `web/tools/export_glb.py`, `tools/package.json`, target `export` | `make -C web export`: `build/raw/line.glb` 23 668 860 B ± 1 %, `interior.glb` 8 423 768 B ± 1 %; `export.json`: `expect_ok` và `blend_unchanged` đều true; `diff` mtime/size trống | 20′ |
| **A2** Nén | A1 | `build/raw/*.glb` | target `compress`, `build/models/*.glb`, `*.validate.txt` | 5,79 / 1,98 MB ± 2 %; 0 lỗi, 0 cảnh báo | 15′ |
| **A3** `check_glb.mjs analyze` | A2 | `scripts/load_check.mjs`, `closed_check.mjs` | `glb_analysis.json` | số liệu trùng bảng 0.2 (node, mesh, tam giác, 4 node tách, lệch ≤ 1 mm, closed 344/351 và 177/205) | 45′ |
| **A4** `make_data.py` | A3 | `gen_drafts.py`, contract, `parts.json`, `shots.json` | `build/data/*.json` (5 file) | so với `web/dot1/*.dot1.json` (bỏ qua thứ tự khoá): khác 0 | 45′ |
| **A5** `verify` + `make all` + publish | A4 | — | `check.json`, target `all` / `publish` | `make -C web all` exit 0 trong < 30 s; `failures: []`; phép thử âm tính (sửa một tên) → exit 1; **I1** | 30′ |
| **A6** Component UI: `DeviceTree`, `InfoPanel`, `Toolbar`, `text.ts`, `ui.css` | B2 (API `reg` + store); có thể bắt đầu với store giả và `devices.dot1.json` | mục 4.2.9, 4.2.10 | `src/ui/*` | tìm "xi lanh b3", "xi lanh", "bom" đều ra kết quả đúng; bấm một mục thì chọn + zoom; toolbar gọi `setStateId`, `setFree`, `setRotorMode`; 0 lỗi tsc | 75′ |

**Tổng A ≈ 3,8 h** (A1–A5 ≈ 2,6 h).

### Luồng B (builder B)

| Task | Phụ thuộc | Vào | Ra | Nghiệm thu | Công |
|---|---|---|---|---|---|
| **B1** Khung sandbox | — | mục 4.4, 4.5 | scaffold, Canvas, Lightformer, Ground, stand-in trong `public/` | dây chuyền hiện ra; D11, D12 đạt | 30′ |
| **B2** `data.ts` + `rig.ts` + `materials.ts` + BVH/lọc + `selfcheck` | B1 | mục 4.2.1–4.2.5 | | `selfcheck`: 190 thiết bị, `unknownNodes` / `missingNodes` / `orphans` = 0, `rayUnfiltered` 0 (dev); `bvh_ms` ≤ 800 | 60′ |
| **B3** Store + chuột + Selection + CameraRig + hook chọn | B2 | 4.2.5, 4.2.7, 4.2.9 | | D2 (`selectAll`, `pickSweep`), D3 | 60′ |
| **B4** Tải interior lazy + `rigInterior` + 4 trạng thái cố định + nắp + peel + camera preset + `capCheck` / `timeState` | B3 | 4.2.3, 4.2.6 | | D4 (4 cặp cố định), D12 (interior chỉ tải khi cần), ảnh nhìn ổn | 90′ |
| **B5** FREE + `cutRoundTrip` | B4 | 4.2.6 | | D4 (FREE, nắp `xsec`), D6 | 45′ |
| **B6** Rotor + precompile + `stats` / `orbitTest` | B4 | 4.2.8 | | D8; D7 sau precompile; D9 | 40′ |
| **B7** Tích hợp I1 + tự chạy bộ kiểm D1–D15 | A5, A6, B6 | file thật đã publish | `web/web-check/SELFTEST.json` (kết quả hook) | mọi tiêu chí D1–D15 đạt hoặc có ghi chú lý do | 30′ |

**Tổng B ≈ 5,9 h.**

### Lịch thực tế

| Thời điểm | Mốc |
|---|---|
| t0 | A1 và B1 bắt đầu cùng lúc |
| t ≈ 2,5 h | B3 xong: xem được dây chuyền, chọn thiết bị (mốc cho người dùng xem sớm) |
| t ≈ 2,6 h | A5 xong (**I1**: file thật thay stand-in); A làm A6 |
| t ≈ 5–6 h | B7 xong |
| sau đó | review khoảng 1 h, fixer khoảng 1 h, reviewer kiểm lại các mục đã sửa khoảng 20′ |

**Đường găng (critical path):** B2 → B3 → B4 → B5/B6 → B7.

---

## 6. Review và sửa

**Reviewer độc lập** (agent riêng, không sửa code), làm theo thứ tự:

1. Kiểm `.blend`: `stat -f '%m %z' out/ze155_anim.blend` trước, rồi `make -C web all`, rồi `stat` sau; đọc `build/reports/export.json` và `check.json` (D14, D15). Không mở Blender, không dùng MCP Blender.
2. `cd web/web-check && npm run dev -- --port 5178 --strictPort` (chạy nền).
3. chrome-devtools: `new_page` → `navigate_page http://localhost:5178/?selfcheck=1` (bỏ cache) → `wait_for "SELFCHECK DONE"`.
4. `evaluate_script`:
   - `await __ze.ready`;
   - `selfcheck()`: D5, D14;
   - `stats()`: D1, D9 ở FULL;
   - `devices().length`, `selectAll()`, `pickSweep()`: D2.
5. `list_network_requests`: chỉ có localhost, chưa có `interior.glb` (D12). `list_console_messages`: D11.
6. Kiểm D3: `clickAt` lên 10 thiết bị (lấy toạ độ từ `project`), có và không có Alt, `dbl: true`; `press_key` F và Escape; chụp ảnh viền và bbox.
7. Với mỗi trạng thái CUT_FEED, CUT_Z_BARREL, CUT_X2450, CUT_X4120:
   - `setState(id)`;
   - kiểm network: `interior.glb` xuất hiện đúng một lần;
   - `take_screenshot` → `shot-<id>.png`;
   - `stats()`: D9;
   - `capCheck`: D4;
   - `clickAt(sample)` + `selection()`.
8. FREE: `setFreeClip('x', 3.0)` → ảnh `shot-FREE-x3000.png`, `capCheck('FREE', 'barrel_b4', {axis: 'x', offset: 3})`; thêm trục y (1,2) và z (0). Kéo thanh trượt bằng `drag` hoặc `fill`.
9. `timeState` cho 6 trạng thái (D7); `cutRoundTrip()` (D6); `rotorTest(2)` + 2 ảnh cách nhau 0,5 s ở CUT_Z_BARREL (D8).
10. `performance_start_trace` + `orbitTest()` + `performance_stop_trace` ở FULL; với CUT_Z_BARREL và FREE chỉ đọc `stats()`.
11. So ảnh với tham chiếu (D13). Ghi từng khác biệt kèm mức độ: C (Critical), I (Important), M (Minor).
12. Chạy lại `selfcheck().rayUnfiltered` sau toàn bộ quá trình (D5).

**File bằng chứng** (`web/review/dot1/`):
- `review-dot1.md`: kết quả D1–D15, phát hiện C/I/M, mỗi mục ghi nơi xảy ra, cách tái hiện và bằng chứng;
- `selfcheck.json`, `stats-<state>.json`, `capcheck.json`, `roundtrip.json`, `rotors.json`, `timing.json`, `pickSweep.json`;
- `console.txt`, `network.txt`;
- `shot-*.png`, `trace-full.json`;
- `blend-stat.txt`.

**Fixer** (agent riêng):
- Chỉ sửa theo `review-dot1.md`, mỗi phát hiện C/I một lần sửa, ghi vào `web/review/dot1/fixes.md` (mã phát hiện → file → thay đổi → hook đã chạy lại).
- Không đổi tiêu chí.
- Phát hiện cần đổi dữ liệu thì sửa `make_data.py` hoặc contract, rồi `make all`; không sửa tay file trong `public/data`.
- Reviewer kiểm lại đúng các mục đã sửa.

---

## 7. Rủi ro riêng của Đợt 1 và cách giảm

| Rủi ro | Số đo | Cách giảm |
|---|---|---|
| Dựng BVH lúc khởi động làm treo luồng chính | 1,6 triệu tam giác: `SAH` 1,56 s, **`CENTER` 0,41 s** | dùng `CENTER`; dựng BVH cho `interior` lúc tải nó; nếu vượt 800 ms trong trình duyệt thì dựng lười (dựng BVH lần đầu một mesh qua được phép kiểm bounding sphere) |
| Chi phí `attach` | 1,4 ms + 0,3 ms | không đáng kể; gọi `updateMatrixWorld(true)` một lần trước khi attach |
| Z-fighting khi hiện cùng lúc phần ngoài và bản sao rỗng (hollow là bản sao chính xác; quantize làm tròn khác nhau theo lưới của từng mesh, nên chắc chắn bị nhấp nháy) | lệch quantize ≤ 0,49 mm | payload `interior` ẩn sẵn; luật loại trừ kiểm ở `make_data` và `verify`; `cutRoundTrip`; peel chỉ là nửa đã bỏ (không chồng lên nửa còn lại) |
| Tên bị đổi khi xuất hoặc khi tải | 561/561 tên giữ nguyên với cả hai loader | `check_glb analyze` dừng lỗi khi có tên bị thêm hậu tố, bị trùng, mồ côi hay thiếu; mọi tra cứu dùng `userData.name` |
| Meshopt đổi TRS của node | 4 node bị tách cha; mọi node mesh có TRS mới | không quay node mesh (pivot runtime); payload biết node con không tên; `check_glb` khoá danh sách 4 node |
| Lưới hở và nắp | 7 lưới ngoài và 28 lưới trong bị hở; curve thì kín | `closed` từ phép kiểm hàn đỉnh; lưới hở được vẽ DoubleSide không nắp; trục cán dùng `cap: force` (Q2); khối nhựa không bao giờ có nắp |
| Kích thước phần bên trong | 1,98 MB nén, 413 k tam giác, 438 draw call nếu hiện hết | lazy-load; FREE chỉ hiện vai trò `full` (ước 241 draw call bên trong, tổng FREE 953); ngân sách FREE ≤ 1 100 draw call |
| Draw call ở FREE (khoảng 771 + vài trăm bên trong) | 771 ở FULL | đo ở D9; nếu vượt thì dự phòng gộp mesh trong từng thiết bị (`join` theo vật liệu, snippet cũ M5) cho các thiết bị tĩnh |
| Lần đầu đổi trạng thái chậm vì biên dịch shader | chưa đo trong trình duyệt | `precompileStates` + `compileAsync` sau khi tải `interior`; D7 đo ở lần vào thứ hai |
| StrictMode dev làm mất bộ lọc tia | — | không dùng drei `<Bvh>`; `installRaycastFilter` idempotent; rig có cờ; `rayUnfiltered` ở D5 |
| Viền quá to trên mesh đã quantize (1 đơn vị cục bộ ≈ nửa kích thước mesh) | — | `screenspace={false}` (pixel); kiểm bằng ảnh D3 |
| Bản cắt nằm trùng mặt phẳng (nắp `xsec` với phần tử) | A1a đã lùi phần tử 2 mm, khối nhựa 0,5 mm | giữ nguyên hình đã xuất; nhìn ảnh D13 |
| Hai bản three hoặc three-mesh-bvh trong bundle | latest three-mesh-bvh là 0.9.15 | `npm i -E` + `npm ls` ở task B1 |
| Extras của Blender trùng khoá runtime (`type`, `zone`, `note`) | 183 node có extras | siêu dữ liệu runtime chỉ nằm ở `userData.ze` |
| `.blend` bị đổi trong lúc xuất (người dùng lưu) | tải chỉ mất 0,4 s; Blender ghi `.blend@` rồi đổi tên | đọc file một lần lúc bắt đầu; nếu mtime đổi thì `make export` dừng (diff), chạy lại là xong |

---

## 8. An toàn

1. **Không bao giờ ghi `.blend`.**
   - Script không có lệnh lưu nào.
   - Mọi chỉnh sửa (bỏ ẩn, collection tạm, đặt rotor về 0) chỉ nằm trong bộ nhớ của tiến trình nền và mất khi tiến trình thoát.
   - Script so mtime/size trước và sau, rồi exit 1 nếu khác. Makefile so thêm bằng `stat` và `diff`.
   - Probe đã kiểm: 3 lần chạy, `.blend` vẫn 1791173730 / 29 470 668 B; không sinh `quit.blend` hay autosave (file `quit.blend` trong `$TMPDIR` lúc 12:43 là của phiên GUI người dùng, có trước probe).
2. **Không dùng MCP Blender, không đụng Blender đang mở.**
   - Xuất là một tiến trình riêng `-b --factory-startup`: không nạp addon (nên không mở socket 9876 mà phiên người dùng PID 63386 đang giữ), không đọc hay ghi userpref, không autosave.
   - Có thể chạy khi Blender của người dùng đang mở, vì chỉ đọc file đã lưu trên đĩa.
   - Không được chạy hai lệnh `make export` cùng lúc: cùng ghi `build/raw`.
3. **Chỉ ghi trong `web/`.**
   - Script từ chối `--out` và `--report` nằm ngoài `web/build/`.
   - Các lệnh còn lại chỉ ghi `web/build/`, `web/web-check/`, `web/tools/`, `web/review/`.
   - Ngoại lệ không tránh được: cache npm ở `~/.npm`.
4. **Không đổi** `PLAN-R3F.md`, `model-contract.json`, `r3f-snippets.md`, `anim/*`, `design/*`, `out/*`.
5. **Web chỉ dùng localhost:** không Draco (`useGLTF(..., false, true)`), meshopt decoder nhúng trong three-stdlib, `Environment` chỉ gồm Lightformer, phông hệ thống.

---

## 9. Quyết định nhỏ còn mở (đề xuất kèm theo)

| # | Câu hỏi | Đề xuất | Khác |
|---|---|---|---|
| Q1 | Kiểu dựng BVH | **`CENTER`** (0,41 s tổng; raycast vẫn khoảng 0,17 ms/tia) | `SAH` (1,56 s, raycast nhanh hơn chút) hoặc dựng lười |
| Q2 | Nắp cho 3 trục cán (lưới hở 192 cạnh biên ở lỗ cổ trục) khi FREE cắt qua | **`cap: force`**, reviewer xem ảnh; xấu thì chuyển sang `none` | `none`: thấy lòng trục rỗng |
| Q3 | FREE có hiện phần bên trong slice 2 không (đầu, van, adapter, bơm `_full`, kênh lọc, trộn tĩnh) | **Có**: đã xuất, đúng vật lý; nếu không hiện thì các phần ngoài đó bị cắt như khối đặc | Chỉ slice 1: lọc `slice` trong `make_data` |
| Q4 | Có tự đưa camera về preset khi vào trạng thái cố định không | **Có**, chuyển mượt; FREE giữ camera; có nút "Về góc nhìn của trạng thái" | Giữ camera, chỉ đổi khi bấm nút |

---

## 10. Chỗ tài liệu này thay thế PLAN-R3F.md và contract (chỉ cho Đợt 1)

| PLAN-R3F / contract | Đợt 1 dùng |
|---|---|
| §4.3 "không chạy Blender nền", Q1 (xuất qua MCP), Q6 (sao lưu phiên), W0–W2 (scene `ze155_web`, bản sao `p_*`, `libraries.write`, fingerprint) | **Phương án C** (DECISIONS 30): `export_glb.py` chạy nền trên file đã lưu; không có bản sao, không scene mới, không lưu |
| Cây node `ze155_line > sec_* > dev_* > p_*`, `ih_*`, `rot_*` trong GLB (contract `hierarchy`, `naming.patterns`, `node_kinds`) | GLB giữ cây Blender (node gốc = object). `sec_*`, `dev_*`, `rot_*` là nhóm runtime; `userData.ze` thay cho `userData.kind` |
| Tên `p_<object>` trong `cut_states`, `devices[].parts`, `free_swap`, `interior_export.node` | tên object thật; luật đổi ở mục 3.3.1 |
| `interior_export.slice_rule` / ngoại lệ slice ở `make_cut_states.py` | Đợt 1 xuất toàn bộ phần bên trong; kiểm tên nghiêm, không ngoại lệ |
| `split_objects` (tách băng nhiệt, bu-lông, hộp nhiệt khuôn) | không tách ở Đợt 1; Đợt 2 tách theo island ở runtime nếu cần |
| `clips` / `export_animation_mode: NLA_TRACKS` | `export_animations=False`; clip là tween runtime (Đợt 2) |
| `closed_test` (bmesh; 269/343 kín, curve tính là hở) | hàn đỉnh theo vị trí trên GLB thô: 344/351 và 177/205 kín; curve kín |
| `tools/check_glb.py`, `tools/make_cut_states.py`, `tools/make_standin.mjs`, `standin.glb` | `web/tools/check_glb.mjs` (analyze / verify), `web/tools/make_data.py`; stand-in là GLB thật của probe |
| Pipeline nén `dedup --materials false → prune → meshopt` | giữ, thêm `--vertex-layout separate` ở mọi bước (đã chạy) |
| `budgets` (`line` ≤ 15 MB, `interior` ≤ 6 MB, draw call 1 000 / 1 150 / 1 350, load 6 s) | siết theo số đo: 7 / 2,5 MB; 850 / 1 000 / 1 100; khung đầu ≤ 4 s; BVH ≤ 800 ms |
| Snippet §2 Registry, §8 Rotor, §6 `showChain` / `interiorRoot` | mục 4.3 |
| 12 rotor | 8 chạy ở Đợt 1 (vít ×2, trục động cơ, 2 khớp nối, trục cán ×3); 4 rotor slice 2 có trong `rotors.json` nhưng không tạo |
