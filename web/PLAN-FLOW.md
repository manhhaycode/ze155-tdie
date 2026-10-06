# Kế hoạch: flow "Quy trình" — từ hạt nhựa tới tấm film (mặt cắt Y = 0)

Bản 1.0, 2026-10-05. Thiết kế đã được người dùng duyệt trong hội thoại. Flow này dựng thêm trên Đợt 1 (`PLAN-DOT1.md` + `dot1/AMENDMENTS.md` + các bản sửa đã review). Không cần Blender, không xuất lại GLB.

**Người dùng đã chọn:**
- **Chế độ xem tự do.** Không có camera tự đi, không có chú thích theo chặng. Người xem tự xoay, zoom, chọn thiết bị.
- **Hạt 3D thật cộng khối nhựa**, không chỉ dùng shader.
- **Mặt cắt đứng dọc Y = 0**, nhìn từ phía vận hành.
- **Chỉ màu.** Không tooltip, không dải biên dạng, không HUD.
- **Bản đủ, cộng một reviewer độc lập**, rồi sửa lỗi.
- **Đổi nhãn mọi nút mặt cắt sang kiểu "thấy gì"** (2026-10-06, §4.1). Lý do: nhãn cũ ghi toạ độ và mã đoạn ("Y = 0", "B3"), người dùng thấy khó hiểu.

**Ngoài phạm vi:**
- 6 trạng thái Đợt 2, 3 clip (`valve_run`, `sc_index`, `die_open`), khe môi (morph), tách node lúc chạy (splits);
- tour, nhãn 3D, HUD (quyết định 32 vẫn giữ);
- peel;
- hạt ở các trạng thái khác FLOW;
- mọi sửa trong Blender.

---

## 1. Tiêu chí nghiệm thu

**Cách đo:** như Đợt 1. Apple M3 Pro, Chrome qua chrome-devtools MCP trong `isolatedContext` riêng, 1920 × 1080, DPR 1. Chạy `npm run dev -- --port 5178 --strictPort`, mở `/?selfcheck=1`. Mọi ảnh chụp và mọi phép lấy mẫu pixel chạy sau `__ze.freeze(true)`.

| # | Tiêu chí | Ngưỡng / cách kiểm |
|---|---|---|
| F1 | Dữ liệu | `make -C web data verify publish` exit 0 (đường chỉ dữ liệu; GLB không đổi). `check.json.failures = []`. Luật §2.5 cho FLOW 0 lỗi. `selfcheck()`: `unknownNodes` 0, `missingNodes` 0, `orphans` 0, `devices` 190 |
| F2 | Trạng thái FLOW | • `setState('FLOW')` resolve;<br>• `timeState('FLOW')` ≤ 200 ms ở lần vào thứ hai;<br>• `cutRoundTrip()` ok, có FLOW: FULL → FLOW → FULL và FLOW → FREE → FLOW cho cùng tập node, cùng vật liệu; rời FLOW thì hạt ẩn và khối nhựa về vật liệu Đợt 1;<br>• `rayUnfiltered` = 0 |
| F3 | Nắp và chọn | `capCheck('FLOW', d)` ok 3 lần liền cho 5 thiết bị: `feed_throat`, `barrel_b3`, `melt_gear_pump`, `die_body_lower`, `ctx_roll_middle`. Một `clickAt` thật lên một pixel nắp chọn đúng thiết bị |
| F4 | Hạt | `pelletTest(2)`:<br>• chế độ chậm: tốc độ dọc trục ở z01 **0,0634 m/s**, ở z02 **0,0423 m/s** (sai ≤ 5 %); chế độ thực ×20;<br>• chế độ tắt: vị trí không đổi sau 1 s;<br>• không hạt nào hiện ở x > 1,905 m hay z < 0 (three);<br>• số hạt = `N` |
| F5 | Khối nhựa | `fillProbe()`: trong FLOW mọi mesh `za_fill_melt` đang hiện, cùng `ctx_melt_curtain`, dùng chương trình `ze-fill-*` (`leftovers` = 0). `fillColorAt(1.0, 'phase')` = màu hạt; `fillColorAt(2.5, 'phase')` = màu nhựa chảy; `fillColorAt(5.9, 'heat')` = heat(285 °C). Hai ảnh cách 1 s (không freeze): vân trôi về +X |
| F6 | Tấm film | `sheetProbe()`: vật liệu `ze-sheet`, tốc độ sọc **0,4168 m/s** (sai ≤ 1 %), bằng 0 khi tắt. Ở s = 0: chế độ pha cho hổ phách, chế độ nhiệt cho heat(250 °C) |
| F7 | So ảnh | Sau freeze, ở preset FLOW và khi zoom vào từng cụm, ở 1920 × 1080 và 1366 × 768. Thấy liền mạch:<br>• hạt trong cột cấp liệu;<br>• trục vít B trong lỗ;<br>• màu đổi ở khối nhào;<br>• van, lọc, bơm, ống;<br>• khuôn A-A có nhựa;<br>• màn nhựa;<br>• tấm ôm trục và ra băng tải.<br>Không có khối đặc phủ kênh nhựa, không z-fighting, không hai bản ở một chỗ. So với ảnh tham chiếu:<br>• cụm khuôn ↔ `anim/look/A1b-S12-f3351-ev-r2.png`;<br>• cụm bơm ↔ `A1b-S10-f2701-ev-r3.png`;<br>• cột cấp liệu ↔ `A1a-feedcol-ext-wb.png` |
| F8 | Hiệu năng | FLOW ≥ 45 fps, ≤ 1 000 draw call, tam giác hiện ≤ 1,7 triệu, heap ≤ 600 MB |
| F9 | Hồi quy Đợt 1 | 6 trạng thái cũ không đổi:<br>• `capCheck` D4 6/6;<br>• `cutRoundTrip` D6;<br>• console 0 lỗi (D11);<br>• chỉ request tới localhost (D12).<br>`SELFTEST.json` cập nhật mục FLOW |
| F10 | Ngôn ngữ, nhãn | • Mọi chữ mới có bản tiếng Việt và tiếng Nhật; đổi ngôn ngữ ở FLOW không mất trạng thái màu.<br>• 7 nút trạng thái và 3 nút hướng cắt hiện đúng nhãn và tooltip của §4.1 ở cả hai ngôn ngữ; không nút nào còn toạ độ trên chữ.<br>• Toolbar ≤ 2 hàng ở 1920 px, ≤ 3 hàng ở 1366 px |

---

## 2. Trạng thái `FLOW`

### 2.1 Mặt phẳng và camera
- **Mặt phẳng:** three `normal [0, 0, 1]`, `constant 0`. Giữ phần three z ≥ 0, tức Blender Y ≤ 0, là nửa xa phía người vận hành. Đúng bằng mặt phẳng của CUT_FEED, CUT_PUMP và CUT_DIE_AA, nên các bản cắt sẵn `_y0` khớp chính xác.
- **Nhãn:** theo §4.1. Nút ghi "Quy trình: hạt → film"; tooltip ghi "Bổ dọc cả dây chuyền, xem hạt nhựa chảy ra rồi thành tấm film".
- **Camera** (three, ống kính 35 mm):
  - nhìn ngang từ phía vận hành, hơi cao, khung trọn đường vật liệu X −0,6 … 12,65 m trong vùng canvas giữa hai panel;
  - giá trị khởi điểm: pos `[6.0, 4.5, −19.0]`, target `[6.0, 1.4, 0.0]`;
  - builder chỉnh theo ảnh và ghi lý do vào `source`.
  - Ở khung này hạt chưa thấy được; người xem zoom vào. Chấp nhận.

### 2.2 Luật sinh danh sách (`make_data.py`, hàm mới `build_flow()`)
**Nguồn tên** (đều đã kiểm tên):
- `cut_states` hiện tại: CUT_FEED, CUT_Z_BARREL, FREE.
- `web/dot2/states.dot2.json`: CUT_PUMP, CUT_DIE_AA. Chỉ đọc hai trạng thái này; đây không phải port Đợt 2.
- `build/reports/glb_analysis.json`: `files.<file>.nodes.<n>.bbox` (toạ độ three) và `vol`.

**Bước 1: đổi chi tiết (`swap`).** Không dùng bản `_lo`.

| Thiết bị ngoài | Thay bằng | Nguồn |
|---|---|---|
| `feed_throat`, `feed_hopper`, `feed_flex_sleeve`, `feed_downpipe` | `int_feed_column_hollow` (3 cái sau: `[]`, tức ẩn) | CUT_FEED |
| `barrel_b1` … `barrel_b6` | `int_barrel_hollow_b1` … `_b6` | CUT_Z_BARREL |
| `barrel_vent_dome`, `barrel_vent_dome_2` | `int_dome_hollow_2`, `int_dome_hollow_1` | FREE |
| `melt_head_adapter` | `int_head_hollow`, `int_fill_head` | FREE |
| `melt_startup_valve` | `int_valve_body`, `int_valve_bolt`, `int_fill_valve_in`, `int_fill_valve_run_bolt`, `int_fill_valve_run_out` (chỉ bộ CHẠY) | FREE |
| `melt_sc_adapter_in` | `int_melt_adapters_hollow_sc_in`, `int_fill_adapter_sc_in` | FREE |
| `melt_screen_changer` | `anim_ghost_sc` (ghost) | GHOST_SC |
| `melt_gear_pump`, `melt_pump_adapter_in/out` | `int_pump_body_cut`, các bộ `_y0` | CUT_PUMP |
| `die_body_upper`, `die_body_lower`, `die_flex_lip`, `die_thermal_bolts`, `die_choker_bolts`, `melt_die_adapter`, `melt_pipe`, `melt_static_mixer` | các bản A-A / `_y0` | CUT_DIE_AA |

**Bước 2: luật bbox** cho mọi part ngoài (`line.glb`, `kind: part`) không phải khoá của `swap`. Các số đếm dưới đây đo trước khi trừ khoá `swap`:
- `bbox.zmax ≤ 0` (nằm hẳn ở nửa bỏ) → `hide`. Đo trên dữ liệu: 81 part.
- `bbox.zmin < 0 < bbox.zmax` (cắt qua mặt phẳng) → `clip`, có nắp theo `closed`. Đo trên dữ liệu: 159 part.
- Còn lại → giữ nguyên. Đo trên dữ liệu: 111 part.

**Bước 3: phần đặc.** Phần cắt qua mặt phẳng, kín, có `vol / bbox > 0,8`:
- Bảng `FLOW_SOLID_HIDE`, chuyển sang `hide`: `barrel_cover_c1…c6` và `_hw` (như bản sửa I1 Đợt 1), `ctrl_machine_cabinet`, `melt_drain_chute`.
- Các phần đặc còn lại để `clip` và in cảnh báo để soát bằng mắt: `drive_motor_body`, `drive_motor_cooler`, `drive_motor_fan_cover`, `frame_drive_body`, `frame_process_body`, `gbx_housing`, `lantern_body`.
- Kết quả soát ghi thành bảng quyết định trong code, mỗi mục một dòng lý do.

**Bước 4: phần bên trong.**
- `show_whole`:
  - toàn bộ `show_whole` của CUT_PUMP và CUT_DIE_AA (bản cắt sẵn, không cắt lại);
  - `int_screw_axis_b` và `int_screw_elem_b_01…32` (trục vít B nguyên, quay);
  - `anim_roll_markers_*_aa`.
- `show_clipped`:
  - các bản rỗng ở bước 1 (cột cấp liệu, 6 thân, 2 vòm, đầu, van, adapter lọc);
  - `int_fill_screw_z01_feed … z09_pump` (bản đầy đủ);
  - `int_fill_head`, bộ CHẠY của van, `int_fill_adapter_sc_in`;
  - `int_sc_disc`, `int_sc_screens_01…12`, `int_sc_channels`, `int_sc_backflush_piston`, `int_fill_sc`, `int_fill_sc_cavities`. Đĩa lọc cắt hay để nguyên do soát bằng mắt quyết định; mặc định là cắt.
- `hide`:
  - `int_screw_axis_a`, `int_screw_elem_a_01…32` (trục vít A nằm ở nửa bỏ);
  - bộ XẢ của van;
  - `hide` của CUT_DIE_AA.
- `ghost`: `anim_ghost_sc`.

**Bước 5: đổi tên phần tách sang node nguyên** (không có splits):
- `melt_heater_bands__*` → `melt_heater_bands` (clip);
- `die_body_bolts__top/__bottom` → `die_body_bolts` (hide);
- `die_heater_boxes__*` → `die_heater_boxes` (clip).
- Gộp `clip` của CUT_PUMP và CUT_DIE_AA (`ctx_sheet` và `ctx_melt_curtain` có trong đó) vào danh sách clip của bước 2. Bỏ trùng; một tên không được nằm ở hai danh sách.

### 2.3 Thứ tự trạng thái và kiểu
- `FIXED` trong `make_data.py` và `FIXED_STATE_IDS` trong `data.ts` thêm `FLOW` vào cuối:
  FULL, CUT_FEED, CUT_Z_BARREL, CUT_X2450, CUT_X4120, FLOW.
- `cut_states.json` thêm khoá `flow` vào FLOW (xem §3.6): tham số mô phỏng, đường hạt, vùng, thang màu.
- `cut_states.json` giữ `version: 1` và thêm `flow_version: 1`; các trạng thái cũ không đổi một byte nào.

### 2.4 Áp trạng thái
- `applyState('FLOW')` chạy như mọi trạng thái cố định.
- Sau đó gọi `enterFlowLayer()` (§3), vẫn trong hàng đợi:
  - gán vật liệu khối nhựa, màn nhựa và tấm qua `setMaterial` có ghi lại. `Cuts.ts` export hàm này; hiện là hàm nội bộ;
  - bật hạt.
- `resetCuts` trả lại vật liệu như cũ; `leaveFlowLayer()` ẩn hạt. Mọi lối rời FLOW (bấm trạng thái khác, FREE, `cutRoundTrip`) đều đi qua `resetCuts`.

### 2.5 Phép kiểm trong `make_data.py` (exit 1 nếu sai)
1. Mọi tên tra được. Tên dùng trong FLOW có trong `node_map`.
2. Luật PLAN-DOT1 §3.3.5:
   - không hiện cùng lúc bản `full` và bản `cut_only` của một chỗ;
   - không hiện node ngoài cùng với bản thay thế của nó.
3. Không hiện cùng lúc trục vít A và B. Bộ XẢ và bộ CHẠY của van không cùng hiện.
4. Mỗi mesh `za_fill_melt` đang hiện trong FLOW có vùng trong `flow.zones` hoặc là khuôn.
5. Không tên nào nằm ở hai danh sách.

**Cảnh báo (không dừng):** danh sách phần đặc ở bước 3.

---

## 3. Lớp mô phỏng

### 3.1 Tốc độ, đóng băng
- **Hệ số vít:** `kScrew` = 0 / 1/20 / 1 theo `rotorMode` tắt / chậm / thực.
- **Hệ số trục cán:** `kRoll` = 0 / 1 / 1, vì `display_slow` của trục cán là 1.
- **Một bộ đếm thời gian** `flowTime` cho shader và hạt, chạy trong `useFrame` của `Flow.tsx`. Đứng yên khi `rotorMode === 'off'` hoặc `frozen`.
- **`freeze(true)`** dừng rotor, hạt và `flowTime`. `capCheck` và `pickAt` tự gọi.

### 3.2 Hạt (`scene/Pellets.tsx`)
**Dựng:**
- `InstancedMesh`, `N = 2 000` (chỉnh trong khoảng 1 500–3 000).
- Hình trụ Ø9 × 9 mm, 6 cạnh, khoảng 24 tam giác. Đây là hạt PET 3 mm phóng ×3 cho dễ thấy.
- `MeshStandardMaterial` có `instanceColor`, `clippingPlanes = [mặt phẳng FLOW]`.
- `raycast` không làm gì; `userData.__helper = true`, nên không tính vào `rayUnfiltered`.
- Chỉ dựng ở lần vào FLOW đầu tiên, chỉ hiện trong FLOW. Khoảng 48 nghìn tam giác, 1 draw call.

**Đường đi:** mỗi hạt có toạ độ đường `s`. Mỗi khung, `s += v(s) · dt` cho từng hạt; hạt quay vòng khi ra khỏi đoạn C.

| Đoạn | Hình học | Tốc độ | Biến đổi |
|---|---|---|---|
| A rơi | Đường gấp khúc trong `int_feed_column_hollow`: đỉnh ống rơi → ống mềm → phễu → đáy họng (y ≈ 1,17). Builder đọc điểm trên mô hình, ghi nguồn trong code. Hạt rải trong dải bán kính 25 mm quanh đường; điểm chạm đáy rải đều trên X 0,16–0,52 m | 0,6 m/s, minh hoạ (`kScrew` > 0 thì chạy) | Lộn vòng ngẫu nhiên |
| B vận chuyển rắn | X từ điểm chạm tới 1,521. y ∈ [1,118; 1,165] (đúng lớp `int_fill_screw_z01_feed`, độ điền khoảng 30 %\*). z ∈ [0,005; 0,145] và nằm trong lỗ của trục vít B (tâm z 0,071, r 0,084) | `pitch(x) · 300/60 · kScrew`, `pitch` lấy theo vùng (z01: 0,2535 m) | Lắc ± 3 mm, tự xoay |
| C nóng chảy | X 1,521–1,90 | như trên (z02: 0,169 m) | `m = smoothstep(1,52; 1,90; x)`:<br>• kích thước × (1 − m);<br>• chiều y dẹt thêm × (1 − 0,6m);<br>• màu chuyển hạt → nhựa chảy.<br>Ở x ≥ 1,90 thì quay về đầu đoạn A, rải lại ngẫu nhiên |

- Mật độ hạt tự thưa ở đoạn rơi và dày lên trong rãnh vít, đúng kiểu cấp đói (starve-fed).
- Hạt không quay quanh trục vít, vì việc đó cần hình học rãnh vít; chỉ trôi dọc trục.

**Màu hạt:**
- chế độ pha: `#DBD6C2`, rồi chuyển sang `#D95709` ở đoạn C;
- chế độ nhiệt: đoạn A 30 °C\*, đoạn B và C theo biên dạng vùng (§3.5).

### 3.3 Khối nhựa (`scene/FillMaterial.ts`)
**Dựng:** `makeFillMaterial(kind: 'line' | 'die' | 'curtain', plane, flow)`.
- `MeshStandardMaterial` trong suốt, `opacity` 0,6, `depthWrite` false, DoubleSide, `clippingPlanes = [plane]`.
- Thêm `onBeforeCompile` (varying vị trí thế giới), `customProgramCacheKey` `'ze-fill-' + kind`.
- Gắn sẵn mặt phẳng ngay khi tạo, nên không đi qua `cutVariant`. Nhờ vậy tránh lỗi `clone()` làm mất `onBeforeCompile`.
- Mỗi `kind` dùng chung một vật liệu.

**Uniform:**
- `uTime`, `uMode` (0 = pha, 1 = nhiệt), `uKScrew`, `uKRoll`;
- mảng vùng ≤ 27 mục: `x0`, `x1`, `t0`, `t1`, `pitch`, `speedClass`.

**Màu:**
- **pha:** `mix(#DBD6C2, #D95709, smoothstep(1,52; 1,90; x))`. Alpha 0,08 ở x < 1,52 (hạt 3D thay chỗ), tăng lên 0,6 ở 1,90;
- **nhiệt:** `heat(T(x))`, alpha theo đúng luật của chế độ pha.

**Vân trôi:** độ sáng × [0,85; 1] theo `fract((x − uTime · v) / pitch)`.
- Vùng vít: `v = pitch · 300/60 · uKScrew`.
- Đường nhựa (từ đầu xi lanh tới adapter khuôn): sọc 0,12 m, cùng tốc độ vùng z09 (minh hoạ).
- `die`: toạ độ hướng tâm r = khoảng cách tới gốc `[9,126, 1,2, 0]` trong mặt x–z.
- `curtain`: theo x, `v = 0,347 m/s · uKRoll`.

**Áp cho:** mọi mesh `za_fill_melt` đang hiện trong FLOW (`die` cho `int_fill_die*`) và `ctx_melt_curtain` (`curtain`).

### 3.4 Tấm film (`scene/SheetMaterial.ts`)
- **Áp cho** `ctx_sheet` trong FLOW: `MeshStandardMaterial` trong suốt 0,35, `depthWrite` false, `clippingPlanes = [plane]`, `onBeforeCompile`, khoá `'ze-sheet'`.
- **Tham số đường đi s(x, y)** theo từng đoạn, như PLAN-DOT2 §2.5:
  - ôm trục giữa: tâm `[9,776; 1,601]`, r 0,4005, từ −90° tới 90° qua phía +X; dài 1,258 m;
  - ôm trục trên: tâm `[9,776; 2,403]`, từ −90° tới 90° qua 180°; dài 1,258 m;
  - đoạn thẳng: y 2,805, x từ 9,776 tới 12,5; dài 2,724 m.
- **Sọc** 0,30 m, rộng 12 %, trôi `0,4168 m/s · uKRoll`.
- **Màu theo s:**
  - pha: hổ phách `#D95709` ở s = 0, chuyển dần sang PET trong `#E8EEF0` ở s = 0,3 m;
  - nhiệt: 250 °C (s = 0) → 70 °C (s = 1,26) → 50 °C (s = 2,52) → 35 °C (cuối)\*.

### 3.5 Biên dạng nhiệt và thang màu
**Vùng:** 27 vùng lấy nguyên từ `web/dot2/states.dot2.json` → `fills.zones` (x, `temp_c`, `pitch_m`). Khuôn 275 °C, màn nhựa 270 → 250 °C\*.

| Vị trí | Nhiệt độ |
|---|---|
| B1 họng nạp (áo nước) | 50 °C\* |
| cuối vùng cấp liệu, X 1,52 | 260 °C\* |
| khối nhào → thoát khí → trộn | 260–275 °C\* |
| tăng áp, đầu xi lanh | 280–285 °C\* |
| lọc, bơm, ống | 282 → 275 °C\* |
| khuôn | 275 °C\* |
| màn nhựa | 270 → 250 °C\* |
| trục cán, tấm | 250 → 35 °C\* |

- **Thang `heat(T)`** 20–300 °C, 4 mốc nội suy tuyến tính trong sRGB: 20 `#2F5DA8`, 120 `#4FB0C6`, 220 `#F2C94C`, 300 `#D7301F`. Hàm JS `heatColor(T)` dùng chung cho shader (sinh hằng số GLSL), hạt và `fillColorAt`.
- Nhiệt độ hiện ra là **nhiệt độ đặt của vùng**, giả định từ `anim/design-anim.md` §2, không phải nhiệt độ lõi hạt.

### 3.6 Dữ liệu `flow` (trong `cut_states.json` → `FLOW.flow`)
- `zones`: chép từ `states.dot2.json`.
- `die`: `origin_m`, `radius_m`.
- `curtain`, `sheet`: đường đi và biên dạng nhiệt.
- `colors`: `pellet`, `melt`, `sheet_clear`.
- `heat_stops`.
- `pellets`: `N`, `size_m`, đường đoạn A, hộp đoạn B, X đoạn C.
- `screw_rpm` 300.

Mọi số đều ghi `source`.

---

## 4. Giao diện

### 4.1 Nhãn nút trạng thái (áp cho cả 7 nút)
**Nguyên tắc:** chữ trên nút nói người xem sẽ thấy gì. Toạ độ, mã đoạn và thuật ngữ chỉ nằm trong tooltip.

| Id | Nút (VI) | Tooltip (VI) | Nút (JA) | Tooltip (JA) |
|---|---|---|---|---|
| FULL | Toàn bộ máy | Nhìn toàn dây chuyền, không cắt | 全体 | ライン全体（断面なし） |
| CUT_FEED | Phễu nạp hạt | Bổ dọc phễu và cột nạp, thấy đường hạt rơi vào xi lanh (mặt cắt Y = 0) | 投入ホッパー | ホッパーと投入口を縦に切断し、ペレットがバレルへ落ちる経路を表示（Y = 0） |
| CUT_Z_BARREL | Bên trong xi lanh | Mở nắp xi lanh, thấy hai trục vít đang quay (mặt cắt Z = 1 200) | バレル内部 | バレル上半分を外し、回転する2本のスクリューを表示（Z = 1 200） |
| CUT_X2450 | Lát cắt hai trục vít | Cắt ngang xi lanh B3, thấy lỗ hình số 8 và hai trục vít ăn khớp (X = 2 450 mm) | スクリュー断面 | B3 バレルの横断面：8の字の穴と噛み合う2本のスクリュー（X = 2 450 mm） |
| CUT_X4120 | Lát cắt chỗ hút ẩm | Cắt ngang ở lỗ hút chân không thứ 2 của xi lanh B5, nơi hơi ẩm được rút ra (X = 4 120 mm) | 脱気部の断面 | B5 の第2真空ベントの横断面：水分を吸い出す部分（X = 4 120 mm） |
| FREE | Tự cắt | Tự chọn hướng và vị trí dao cắt | 自由断面 | 切断方向と位置を自由に選択 |
| FLOW | Quy trình: hạt → film | Bổ dọc cả dây chuyền, xem hạt nhựa chảy ra rồi thành tấm film (mặt cắt Y = 0) | 工程：ペレット→フィルム | ライン全体を縦に切断し、ペレットが溶けてフィルムになるまでを表示（Y = 0） |

**Cách làm:**
- `make_data.py` thêm bảng `LABEL_OVERRIDES` (giống `CAMERA_OVERRIDES`): ghi đè `label_vi`, thêm `tooltip_vi`. Contract giữ nguyên.
- `ui/text.ts`: `T_JA.states` đổi theo bảng, thêm `T_JA.stateTips`.
- Toolbar: nút hiện nhãn, `title` lấy tooltip.

**Ba nút hướng cắt trong "Tự cắt":**
- Chữ trên nút đổi: X → "Cắt ngang" / 「横断」, Y → "Bổ dọc" / 「縦断」, Z → "Cắt nằm" / 「水平」.
- Tooltip giữ chữ trục và giải thích, ví dụ "Trục Y: bổ dọc máy, nhìn từ bên hông".
- Dòng số đo của thanh trượt giữ nguyên dạng "Y = 0 mm". `data-axis` và `data-axis-blender` không đổi, để hook test vẫn chạy.

### 4.2 Nút FLOW và điều khiển màu
- **Toolbar** thêm nút `data-state="FLOW"` (nhãn theo §4.1), nằm sau CUT_X4120.
- **Dòng ngữ cảnh**, chỉ hiện ở FLOW:
  - "Màu:" kèm hai nút bật/tắt [Pha] [Nhiệt độ] (`aria-pressed`) / 「色:」[相] [温度];
  - thang màu nhỏ: ở chế độ pha là 3 ô màu "Hạt rắn · Nhựa chảy · Tấm PET" / 「ペレット・溶融樹脂・PETシート」; ở chế độ nhiệt là dải màu 20 – 300 °C;
  - chú thích "\* giả định" / 「* 仮定」.
- **Store:** `flowColor: 'phase' | 'heat'` (mặc định `phase`), `frozen: boolean`. Đổi `flowColor` chỉ đổi uniform và màu instance; không qua hàng đợi.
- **Chữ:** thêm vào `ui/text.ts` (T và T_JA).
- **README:** bảng "Use" thêm một dòng cho FLOW.

---

## 5. Module

| File | Mới / sửa | Việc |
|---|---|---|
| `tools/make_data.py` | sửa | `build_flow()` §2.2, `FLOW` trong `FIXED`, phép kiểm §2.5, khoá `flow` §3.6, `LABEL_OVERRIDES` §4.1 |
| `src/data.ts` | sửa | `StateId` / `FIXED_STATE_IDS` thêm `FLOW`; kiểu `FlowParams` |
| `src/scene/Cuts.ts` | sửa nhỏ | export `setMaterial` có ghi lại; không đổi gì khác |
| `src/scene/heat.ts` | mới | `heatColor(T)`, chuỗi GLSL `HEAT_GLSL`, `zoneAt(x)`, `tempAt(x)` |
| `src/scene/FillMaterial.ts` | mới | §3.3; `fillColorAt(x, mode)` cho test |
| `src/scene/SheetMaterial.ts` | mới | §3.4 |
| `src/scene/Pellets.tsx` | mới | §3.2 |
| `src/scene/Flow.tsx` | mới | `enterFlowLayer` / `leaveFlowLayer`, `flowTime` và uniform trong `useFrame`, `renderOrder` (khối nhựa 1, kênh lọc 2, ghost 3, tấm và màn nhựa 4) |
| `src/store.ts` | sửa | `flowColor`, `frozen`, gọi lớp flow sau `applyState('FLOW')` |
| `src/scene/Rotors.tsx` | sửa nhỏ | tôn trọng `frozen` |
| `src/scene/precompile.ts` | sửa | duyệt cả FLOW, gồm các chương trình `ze-fill-*`, `ze-sheet`, hạt; ≤ 1,5 s |
| `src/ui/Toolbar.tsx`, `ui/text.ts`, `ui/i18n.ts`, `ui/ui.css` | sửa | §4: nhãn và tooltip 7 nút, nhãn 3 nút hướng cắt, nút FLOW, dòng màu |
| `src/test/hooks.ts` | sửa | §6 |
| `README.md` (web-check), `DECISIONS.md` | sửa | bảng Use; quyết định 33 |

---

## 6. Hook test (`window.__ze`)
- **Mới:**
  - `freeze(on)`;
  - `flowProbe()` → `{pellets, visiblePellets, maxPelletX, minPelletZ, fillMeshes, fillPrograms, mode, kScrew, kRoll}`;
  - `pelletTest(s)`: đo tốc độ dọc trục ở z01/z02 bằng `performance.now()`, báo tần số rAF và chạy lại nếu dưới 50 Hz;
  - `fillColorAt(x, mode)`;
  - `sheetProbe()`.
- **Mở rộng:**
  - `selfcheck()` đếm FLOW, bỏ helper;
  - `cutRoundTrip()` có FLOW, kiểm thêm hạt ẩn và khối nhựa về vật liệu Đợt 1 khi rời FLOW;
  - `capCheck` dùng được với FLOW, tự `freeze`;
  - `selftest()` thêm F2–F6.

---

## 7. Thứ tự làm, review, sửa
1. **Dữ liệu:** `build_flow()` + kiểm, rồi `make -C web data verify publish`.
2. **Code:**
   - Cuts export, data, store, Toolbar → vào được FLOW với vật liệu Đợt 1;
   - soát bằng mắt phần đặc (§2.2 bước 3), chốt bảng.
3. `heat.ts`, `FillMaterial`, `SheetMaterial`, `Flow.tsx`.
4. `Pellets.tsx`.
5. Hook, rồi tự chạy F1–F10 trên Chrome. Ảnh lưu vào `web/review/flow/builder/`; cập nhật `SELFTEST.json`.
6. **Reviewer độc lập** (agent riêng, không sửa code hay dữ liệu, Chrome `isolatedContext` riêng):
   - phạm vi: cả 7 trạng thái × 1920 / 1366 px × VI / JA; chọn, hover, double-click / F, cây thiết bị, FREE 3 trục, đổi màu ở FLOW;
   - đo lại F1–F10;
   - ghi `web/review/flow/review-flow-01.md` cùng ảnh, mỗi lỗi C / I / M có vị trí, bằng chứng, cách sửa đề xuất.
   - **Phải xem lại các lỗi đã biết:**
     - CUT_FEED: phễu dưới toolbar;
     - vào FREE thấy mặt cắt quay lưng (M4);
     - nắp trục cán (M3);
     - chấm đầu dòng và id thô ở bảng thông tin (M6);
     - toolbar 7 nút ở 1366 px (M5).
7. **Sửa:**
   - C và I ở mức dữ liệu, camera, CSS, code web: sửa hết;
   - M: sửa nếu mỗi lỗi ≤ 15 phút, còn lại ghi lại;
   - lỗi phải sửa trong Blender: chỉ ghi lại.
   Sau đó reviewer kiểm lại đúng các mục đã sửa.

---

## 8. Rủi ro

| Rủi ro | Cách giảm |
|---|---|
| Phần đặc thành mảng gạch chéo che mặt cắt (bài học I1) | Luật bước 3 + bảng `FLOW_SOLID_HIDE` + soát bằng mắt ở bước 2 của §7 |
| Hai bản ở một chỗ khi trộn danh sách của 4 trạng thái | Phép kiểm §2.5; `cutRoundTrip`; ảnh F7 |
| `clone()` mất `onBeforeCompile` | Vật liệu FLOW gắn sẵn mặt phẳng, không qua `cutVariant` |
| Thứ tự vẽ vật trong suốt (khối nhựa, ghost lọc, tấm) | `renderOrder` cố định (§5); soát ảnh |
| Hạt làm sai phép chọn hoặc `rayUnfiltered` | `raycast` không làm gì + `__helper` |
| Precompile dài thêm | Đo `precompileStats.ms`; > 1,5 s thì chỉ biên dịch chương trình mới |
| Ở camera vào FLOW không thấy hạt | Chấp nhận (chế độ xem tự do); người xem zoom vào |
| Hồi quy 6 trạng thái cũ | Lớp flow chỉ đổi vật liệu qua `setMaterial` có ghi lại; F9 |

## 9. Giả định
- Có một thang màu nhỏ, dù người dùng chọn "chỉ màu": không có thang thì màu nhiệt độ không đọc ra được.
- Hạt phóng ×3.
- Nhiệt độ, độ điền và tốc độ rơi có dấu \* là giả định (`anim/design-anim.md` §2); đây là nhiệt độ đặt của vùng.
- Hình minh hoạ có số liệu, không phải mô phỏng CFD.
- Flow này là yêu cầu trực tiếp của người dùng, nên làm trước quyết định 32. Quyết định 32 vẫn giữ cho tour, nhãn, HUD.

---

## 10. Thay đổi khi dựng (2026-10-06, builder)
Những điểm dưới đây khác với §2–§6. Reviewer chấm theo bản này.

1. **Trục vít B bị cắt ở Y = 0** (`show_clipped`, không còn `show_whole`). Trục vít B có trục cách mặt cắt 71 mm, bán kính cánh 83 mm, nên nó nhô qua mặt cắt 12 mm. Để nguyên khối thì nó che kín khe nhìn vào lỗ, không thấy nhựa. Cắt rồi thì chỉ mất đỉnh cánh, vít vẫn quay.
2. **Mặt cắt nhựa vẽ tại mặt phẳng cắt.** Các khối nhựa vùng vít (`show_clipped`) dùng biến thể `ze-fill-line-cap`. Mặt sau của khối nhựa được đặt độ sâu bằng điểm trên mặt phẳng cắt cùng tia nhìn, nếu điểm đó nằm trong eo lỗ (|y − 1,2| ≤ 44,9 mm) và dưới mặt nhựa của vùng. Dữ liệu thêm `zones[].fill_top_m` lấy từ bbox `int_fill_screw_*`. Ở các vùng cấp đói (z01, z03, z04, z07) nhựa chỉ là lớp dưới đáy, đúng như mô hình. Vật liệu khối nhựa vẽ một lượt (`forceSinglePass`).
3. **Mặt cắt màu xám trong FLOW.** `FLOW.cap_colors`: thép `#8E959C` (vẫn vân chéo), trục vít `#5C636B`. Áp cho nắp lúc chạy (theo `cap_class`) và cho vật liệu cắt sẵn `za_cap_*`. Chú thích "Màu nắp cắt" hiện màu này ở FLOW. Lý do: đỏ thép `#B84533` trùng đầu nóng 270–300 °C của thang nhiệt.
4. **Đường đi của tấm** có thêm `sheet.takeoff_xy`, lấy từ đỉnh lưới `ctx_sheet`: đi ngang tới con lăn dẫn (x ≈ 11,40), xuống dốc, rồi theo băng tải ở y 1,15 tới x 12,5. Chiều dài 4,02 m; mốc 35 °C nằm ở s = 6,54 m. Bản nháp Đợt 2 chỉ có một đoạn thẳng, nên đoạn dốc và đoạn băng tải bị tính sai màu.
5. **Camera FLOW:** pos `[5.9, 6.55, −25.0]`, target `[5.9, 3.0, 0.0]`, 35 mm. Giá trị khởi điểm cắt mất cột cấp liệu và phần truyền động.
6. **Đồng hồ shader** là quãng đã đi `uScrewT = ∫ kScrew dt` và `uRollT = ∫ kRoll dt`, thay cho `uTime · v`. Nhờ vậy đổi chậm ↔ thực thì sọc không nhảy.
7. **Bảng phần đặc:**
   - `FLOW_SOLID_HIDE` giữ như §2.2;
   - `FLOW_SOLID_CLIP` cho 7 phần còn lại (truyền động và khung đế), lý do ghi trong code;
   - `FLOW_EXTRA_HIDE` ẩn 2 tấm logo của bộ lọc (bộ lọc là ghost, như GHOST_SC).
8. **Nhỏ:**
   - file hạt là `Pellets.ts` (không có JSX);
   - `pickAt` không tự đóng băng vì là phép bắn tia tức thời; `capCheck` có tự đóng băng;
   - nhãn nhóm FREE đổi thành "Hướng cắt" / 「切断方向」;
   - vùng rải hạt có biên an toàn để cả hạt lẫn độ lắc nằm trong lỗ.
