# Kế hoạch Đợt 2: đường nhựa, khuôn, truyền động (bản ngắn)

Bản 1.0, 2026-10-05. Đợt 2 dựng tiếp trên kiến trúc Đợt 1 (`PLAN-DOT1.md` + `dot1/AMENDMENTS.md` + các bản sửa sau review Đợt 1). Không cần Blender, không xuất lại GLB: `interior.glb` đã có đủ mọi chi tiết slice 2.

**File đi kèm:**
- `web/dot2/gen_dot2.py`: script nháp, đã chạy. Nó tra **mọi tên** dùng trong tài liệu này với `build/data/node_map.json`, `devices.json` và `glb_analysis.json`, rồi kiểm luật trạng thái của PLAN-DOT1 §3.3.5. Kết quả: **0 tên không tra được**, 0 lỗi luật.
- `web/dot2/states.dot2.json`: dữ liệu nháp máy đọc được, gồm 6 trạng thái, 3 clip, vùng khối nhựa, 3 node cần tách và rotor. Builder dữ liệu port script này vào `make_data.py`. Builder web dùng file này làm bản thay thế (stand-in) cho tới khi dữ liệu thật xong.

**Chỗ khác PLAN-R3F:** PLAN-R3F §3.8 và §4.1, cùng `r3f-snippets.md` §11, **giả định clip glTF** (`useAnimations`; xuất lại `line.glb` có track `die_open`; mỗi file một action). Đợt 2 không làm như vậy. Theo phương án C, clip là **tween runtime** đọc từ `clips.json`, không dùng animation trong GLB và không xuất lại. Peel (lột vỏ) vẫn để Đợt 1b; dữ liệu `peel` vẫn giữ trong JSON.

**Ngoài phạm vi (quyết định 32):** tour, nhãn 3D, HUD, sơ đồ khối. Giao diện chỉ thêm nút và một dòng điều khiển theo ngữ cảnh.

---

## 1. Mục tiêu và tiêu chí nghiệm thu

**Mục tiêu:** xem được đường nhựa từ đầu xi lanh tới tấm, qua 6 trạng thái mới:
- van khởi động XẢ → CHẠY;
- đĩa lọc quay từng bước;
- bơm bánh răng quay;
- khuôn mở và khe môi;
- khối nhựa đổi màu theo pha hoặc nhiệt độ, chạy theo dòng chảy;
- tấm PET chạy theo trục cán.

**Cách đo:** như Đợt 1. Máy M3 Pro, Chrome qua chrome-devtools MCP trong **ngữ cảnh riêng** (`isolatedContext`), canvas 1920 × 1080, DPR 1, `npm run dev -- --port 5178 --strictPort`, URL `/?selfcheck=1`. Hook mới nằm ở `window.__ze` (mục 3).

**Quy ước "đóng băng":** mọi phép kiểm lấy mẫu pixel đều chạy sau `__ze.freeze(true)`, tức rotor tắt, clip dừng, thời gian khối nhựa đứng yên. Ảnh chụp so sánh cũng vậy. Clip được kiểm bằng `clipSeek(t)` (tất định), không đo theo đồng hồ thật.

| # | Tiêu chí | Ngưỡng / cách kiểm |
|---|---|---|
| E1 | Dữ liệu, tách node | `make -C web all` exit 0; `make_data.py --compare dot2` 0 khác biệt ngoài danh sách đã ghi; `check.json.failures = []`.<br>`selfcheck()`: `unknownNodes` 0, `missingNodes` 0, `orphans` 0, `devices` 190, `parts` **571** (561 + 10 phần tách), `splits` = {melt_heater_bands: 6, die_body_bolts: 2, die_heater_boxes: 2}, `ambiguous` 0. Mỗi phần tách có tam giác > 0, tổng bằng node gốc (6 996 / 16 168 / 21 704). Tâm mỗi băng nhiệt cách X của contract ≤ 25 mm |
| E2 | 6 trạng thái mới | Với mỗi id: `setState(id)` resolve; `stateDiff(id)` = `{extra: [], missing: []}` (payload đang hiện so với tập suy ra từ dữ liệu); `timeState(id)` ≤ **200 ms** ở lần vào thứ hai; `frameCheck(id)`: ở 1920 × 1080 ≥ 95 % góc của `frame_box_m` nằm trong vùng canvas trống (trừ toolbar và hai panel) và bề rộng chiếm 30–90 % vùng đó; ở 1366 × 768 ≥ 80 % góc nằm trong |
| E3 | Nắp và chọn | `capCheck` (hook tự đóng băng), 6 cặp: (CUT_PUMP, `melt_gear_pump`) qua nắp cắt sẵn `int_pump_body_cut`; (CUT_PUMP, `melt_sensor_p3`); (CUT_DIE_AA, `die_body_lower`) qua `int_die_section_lower`; (CUT_DIE_AA, `ctx_roll_middle`, nắp `force`); (CUT_DIE_PLAN, `die_end_plate_op`); (ST1_Z_FULL, `barrel_b3`). Cả 6 ok, 3 lần liền cùng kết quả; một `clickAt` thật lên pixel mẫu chọn đúng thiết bị.<br>GHOST_DRIVE: `pickAt` tâm `int_gbx_schematic_counter` trả về part đó (tia xuyên ghost). CUT_DIE_PLAN sau khi nhấc: `pickAt` vào `die_body_bolts__top` trả về thiết bị `die_body_bolts` |
| E4 | Rotor | `rotorTest(2)`: 12 rotor sai ≤ 5 %. Quanh [0, 0, −1]: bơm trên **+103,5 °/s**, dưới **−103,5 °/s** (69 vòng/phút, chậm 4×). Quanh [1, 0, 0]: hộp số vào **−335,4 °/s**, trung gian **+171,4 °/s**, vít −90 °/s. Quaternion thế giới của `int_gbx_schematic_out_a` bằng của `rot_screw_a`. Ảnh CUT_PUMP 2 ảnh cách 0,5 s: răng trên đi về +X, không chồng nhau |
| E5 | Clip (`clipSeek`) | • `valve_run`: t = 0 → chốt lệch z **+0,200 m** (± 0,5 mm), hiện bộ XẢ; t = 2,2 → 0, bộ CHẠY. 50 mẫu trong [0; 2,2]: không lúc nào hiện cả hai bộ hay thiếu cả hai. CUT_Z_BARREL dùng `_lo`, FREE dùng tên đầy đủ.<br>• `sc_index`: t = 3 → đĩa **+30,0°** (± 0,1°), t = 36 → 0°. Piston z: 0 ở t = 0,8, **+0,060 m** ở 1,4, 0 ở 2,0. `screens()`: độ bẩn tăng dần trong cửa sổ dòng chảy, bằng 0 ở trạm 0° sau giây 1,4 của chu kỳ.<br>• `die_open`: t = 2,4 → 9 nhóm thiết bị và 2 phần `__top` lệch **+0,900 m Y** (± 1 mm); `__bottom` và `die_body_lower` không đổi. Mặt trước khối nhựa khuôn bằng 0 ở t = 2,4, bằng 1 ở t = 4,4.<br>• Rời trạng thái: mọi mover và nhóm về 0, `clipState()` = null |
| E6 | Khe môi (morph) | CUT_DIE_AA: `morph('gap_x10', 1)` → 13 mesh của 4 node có influence 1, dòng đọc số ghi "Khe môi thật 1,00 mm (vẽ ×10)"; thêm `lip_push` → "0,85 mm"; nút `lip_push` tắt khi `gap_x10` = 0; rời trạng thái → influence 0. Ảnh S12 khoá 2 ↔ `A1b-S12-f3501-ev-r3-gapx10.png` |
| E7 | Shader khối nhựa | `fillProbe()`: `leftovers` 0 (không còn mesh khối nhựa dùng vật liệu Đợt 1); có chương trình `ze-fill`; tốc độ ở chế độ chậm: z01 **0,0634 m/s**, z09 **0,0317 m/s**, màn nhựa **0,347 m/s** (± 1 %); rotor tắt thì `uTime` đứng yên.<br>`fillColorAt(x)` (bản JS của shader): x = 1,0 ra màu hạt, x = 2,5 ra màu nhựa chảy, chế độ nhiệt ở x = 5,9 ra heat(285 °C).<br>Ảnh: CUT_Z_BARREL 2 ảnh cách 1 s, vân trôi về +X; chế độ nhiệt xanh → đỏ dọc xi lanh; FREE x = 3,0 khối nhựa bị cắt vẫn hổ phách có vân, không thành trắng |
| E8 | Tấm PET, màn nhựa | `sheetProbe()`: vật liệu `ze-sheet`, trong suốt, `depthWrite` false, **0,4168 m/s** (± 1 %) ở chậm và thực, 0 khi tắt. Ảnh S13 khoá 1, 2 ảnh cách 0,5 s: sọc chạy theo chiều trục cán trên đoạn ôm trục lẫn đoạn ra. `ctx_melt_curtain` dùng vùng `curtain` |
| E9 | Giao diện | Bấm CDP thật vào từng nút và điều khiển mới: đều chạy. Toolbar ≤ 2 hàng ở 1920 px, ≤ 3 hàng ở 1366 px. Chữ tiếng Việt, mặt cắt ghi theo **trục Blender**. Dòng ngữ cảnh chỉ hiện ở trạng thái liên quan (2.6) |
| E10 | Hồi quy Đợt 1 | • **D5** `rayUnfiltered` = 0 sau 11 trạng thái cố định + FREE + 3 clip + morph + chọn.<br>• **D6** `cutRoundTrip()` qua 11 trạng thái; kiểm thêm mover và nhóm thiết bị ở 0, morph 0, van ở bộ CHẠY, không clip nào chạy.<br>• **D9** mỗi trạng thái mới ≥ 45 fps, ≤ 1 000 draw call; FULL vẫn ≤ 850 (ước từ dữ liệu, chưa tính frustum: FULL 792, trạng thái mới 790–841).<br>• **D11** console sạch. **D12** 7 JSON + 2 GLB, chỉ localhost |
| E11 | So ảnh | Ở preset, sau `freeze`: GHOST_DRIVE ↔ `A1b-S02-f301-ev-r2.png`; GHOST_SC ↔ `A1b-ST6-fNone-ev-r2.png`; CUT_PUMP ↔ `A1b-S10-f2701-ev-r3.png`; CUT_DIE_PLAN (sau nhấc + mặt trước) ↔ `A1b-S11-f3201-ev-r2.png`; CUT_DIE_AA ↔ `A1b-S12-f3351-ev-r2.png`; van ↔ `A1b-S08-f2276-ev-r2-drain.png` / `-r2.png`; ST1 không có ảnh A1b.<br>Đạt khi: nắp gạch chéo; không z-fighting, không hai bản một chỗ, **không khối đặc phủ mặt cắt**; bánh răng ăn khớp; đĩa và lưới đọc được dưới ghost; thấy rõ móc áo ở CUT_DIE_PLAN |

---

## 2. Trạng thái và tính năng

### 2.1 Luật tên bổ sung (đã kiểm bằng `gen_dot2.py`)

| Tên trong contract | Xử lý ở Đợt 2 |
|---|---|
| `rot_gbx_input`, `rot_gbx_counter`, `rot_pump_gear_top`, `rot_pump_gear_bottom` trong danh sách show | **bỏ**. Đây là pivot runtime, tạo từ `rotors.json`; node thật (`int_gbx_schematic_*`, `int_pump_gear_*` hoặc con `_full` của nó) đã có trong cùng danh sách |
| `anim_sc_disc`, `anim_sc_piston`, `anim_die_choker_bar` | **bỏ**. Phương án C không xuất các empty này. Node thật là `int_sc_disc`, `int_sc_backflush_piston`, `int_die_choker_bar`; mover runtime thay cho empty |
| Đích clip `anim_valve_bolt`, `anim_sc_disc`, `anim_sc_piston` | mover gắn `int_valve_bolt`, `int_sc_disc`, `int_sc_backflush_piston` |
| Đích `anim_die_bolts_top`, `anim_die_heater_boxes_top` | mover gắn phần tách `die_body_bolts__top`, `die_heater_boxes__top` |
| Đích `anim_die_choker_bar` | không cần: `int_die_choker_bar` thuộc `dev_die_choker_bolts`, vốn đã là đích của `die_open` |
| `melt_heater_bands__{head1, head2, scin, pumpin, pumpout, dieadapter}`, `die_body_bolts__{top, bottom}`, `die_heater_boxes__{top, bottom}` | **phần ảo** do runtime tách (mục 2.3). `node_map.json` thêm khoá `splits`; `nodes` giữ nguyên |

**Sửa so với contract** (mỗi chỗ đều ghi trong `planner_fix` của bản nháp):
- **ST1_Z_FULL:** chuyển `barrel_cover_c1…c6` và `_hw` từ `clip` sang `hide`. Đây là cùng lỗi khối đặc I1 của Đợt 1: tỉ lệ thể tích / bbox của các vỏ che là 0,88–0,97.
- **CUT_DIE_AA:** thêm `ctx_sheet` và `ctx_melt_curtain` vào `clip`. Hai mesh trong suốt này trải z −1,1…1,1 và sẽ phủ màu lên mặt cắt A-A. Vật liệu của chúng có `cap_color` null, nên bị cắt mà không có nắp.

### 2.2 Sáu trạng thái

Mặt phẳng, `hide`, `swap`, `clip`, `show_*` và `ghost` lấy từ contract, đã đổi tên theo 2.1. Số đếm là số đã sinh trong `states.dot2.json`.

| Trạng thái (`label_short_vi`) | Hiện gì, làm sao | Đếm hide / swap / clip / show / ghost | Camera (three) | Khi vào |
|---|---|---|---|---|
| GHOST_DRIVE "Hộp số (vỏ trong suốt)" | Ẩn `gbx_housing`, `gbx_castings`, `gbx_covers`; ghost `anim_ghost_drive_gbx` và 10 chi tiết ngoài (lantern, vỏ khớp nối, bu-lông hộp số). Hiện bánh răng sơ đồ `int_gbx_schematic_{input, counter, out_a, out_b, bearings}` và trục then hoa. `out_a/b` là con của `int_screw_axis_a/b` nên tự quay theo vít | 3 / 3 / 0 / 10 / 11 | S02 khoá 1: pos [−3,6, 2,4, −4,2], target [−2,6, 1,2, 0], 35 mm | – |
| GHOST_SC "Bộ lọc (vỏ trong suốt)" | Ẩn `melt_screen_changer` và 2 logo; ghost `anim_ghost_sc` (nắp đã nâng). Hiện `int_sc_disc`, 12 `int_sc_screens_NN`, `int_fill_sc_cavities`, `int_sc_channels`, `int_sc_backflush_piston`, `int_fill_sc` | 3 / 1 / 0 / 18 / 1 | ST6: [6,2, 1,85, −1,9] → [6,95, 1,45, −0,05], 38 mm | `sc_index` (lặp) |
| CUT_PUMP "Bơm cắt Y = 0" | Mặt phẳng n [0, 0, 1], c 0. Đổi `melt_gear_pump` → `int_pump_body_cut`, 2 adapter → bộ `_y0`. Hiện 2 nửa bánh răng `int_pump_gear_top/bottom` cùng túi nhựa. Cắt `melt_sensor_p3/p4`, `melt_heater_bands__pumpin/pumpout` | 0 / 3 / 4 / 11 / 0 | S10 khoá 1: [7,7, 1,5, −1,75] → [7,7, 1,2, 0], 45 mm. Không dùng ST7 (55 mm ở 1,2 m), vì chật như preset X2450 đã bị chê | – |
| CUT_DIE_PLAN "Mặt phân khuôn Z = 1 200" | Mặt phẳng n [0, −1, 0], c 1,2. Đổi `die_body_lower` → `int_die_lower_face` + `int_fill_die_lo`; adapter → `_lo`. Cắt deckle và 2 tấm đầu. **Nhóm nửa trên không ẩn, không cắt** (`gen_dot2` kiểm luật này) | 1 / 2 / 3 / 5 / 0 | S11 khoá 2: [8,35, 3,3, −1,6] → [9,35, 1,2, 0], 26 mm. Nhìn xiên từ phía thượng nguồn để nửa trên đã nhấc không che mặt khuôn | `die_open`, rồi mặt trước khối nhựa 0 → 1 |
| CUT_DIE_AA "Khuôn A-A Y = 0" | Mặt phẳng n [0, 0, 1], c 0. Đổi khuôn, adapter, ống, trộn tĩnh sang bản cắt sẵn `_y0` (nắp nhiều lớp). Ẩn `die_body_bolts__top/__bottom` và vạch `_pos`. Cắt trục cán (nắp `force`), khung, xe khuôn, `die_heater_boxes__*`, `melt_heater_bands__dieadapter`, tấm và màn nhựa. Có điều khiển morph | 10 / 8 / 17 / 15 / 0 | S12 khoá 1: [9,4, 1,5, −1,65] → [9,42, 1,25, 0], 45 mm | – |
| ST1_Z_FULL "Toàn tuyến Z = 1 200" | Mặt phẳng n [0, −1, 0], c 1,2. Như CUT_Z_BARREL, cộng bộ `_lo` của cả đường nhựa, mặt khuôn dưới, ghost lọc với đĩa nguyên. `int_pump_gear_*_full` bị cắt runtime trong lúc quay. Nửa khuôn trên bị ẩn | 77 / 17 / 21 / 122 / 3 | still ST1: [2,0, 11,0, −11,5] → [2,5, 1,2, 0], 35 mm | – |

`frame_box_m` dùng cho `frameCheck`:
- CUT_PUMP, CUT_DIE_PLAN, CUT_DIE_AA, ST1: `box_m` trong contract;
- GHOST_DRIVE: bbox của `gearbox`;
- GHOST_SC: bbox của `melt_screen_changer`.

Builder được chỉnh camera nếu `frameCheck` hay ảnh không đạt, và ghi lại lý do trong `source`.

### 2.3 Tách 3 node ở runtime (`splits`)

Đợt 1 xuất nguyên `melt_heater_bands`, `die_body_bolts`, `die_heater_boxes` (PLAN-DOT1 §3.1.2). Đợt 2 tách chúng ở runtime trong `rigLine`, trước `prepareMaterials` và `installRaycastFilter`:
1. Với mỗi mesh con (nhóm nhiều vật liệu: 3, 2 và 4 mesh), gom tam giác thành **island**: các tam giác nối nhau qua đỉnh hàn theo vị trí (1e-5 m).
2. Phân loại island theo tâm bbox:
   - băng nhiệt: X gần nhất trong 6 tâm của contract (5,836 / 5,906 / 6,521 / 7,388 / 8,001 / 9,0);
   - bu-lông và hộp nhiệt khuôn: Y > 1,2 → `__top`, ngược lại → `__bottom`.
3. Mỗi lớp thành một `Group` mới, gồm các `Mesh` dùng chung attribute gốc nhưng có index riêng, cùng vật liệu và cùng ma trận với mesh gốc. Group gắn vào node gốc. Payload cũ bị **gỡ khỏi cây** (không chỉ ẩn).
4. Đăng ký `Part` cho từng tên ảo: `meta` = meta gốc cộng `split_of`, `payload` = group mới. Part gốc vẫn còn, `payload = null`, `meshes = []`.
5. Dựng BVH cho từng geometry mới. Ghi báo cáo `reg.splitReport`: số tam giác mỗi phần và `ambiguous`. Ambiguous là trường hợp hai tâm X gần nhất cách nhau dưới 10 mm; khi đó in `console.error`.

Draw call tăng tối đa +21.

### 2.4 Clip runtime (`clips.json`)

**Mover:**
- là `Object3D` tạo lúc chạy trong `dev_<chủ>`, đặt tại `pivot_m`, rồi `attach` node đích, giống pivot rotor;
- **không bao giờ** đặt TRS trực tiếp lên node mesh đã xuất (lý do: quantize);
- riêng `die_open` tween thẳng `group.position` của 9 nhóm `dev_*`, vì đó là nhóm runtime ở transform đơn vị.

**Vào và ra:**
- `playClip` luôn đi qua **hàng đợi trạng thái**.
- `resetCuts` gọi `stopClips()`: mọi offset về 0, van về bộ CHẠY, độ bẩn về 0, mặt trước khối nhựa về 1.
- `applyState(id, {clips})` chạy `clips_on_enter` sau bước hiện/ẩn. Precompile, `cutRoundTrip` và `timeState` dùng `clips: false`.

| Clip | Mover / đích | Diễn biến | Ở đâu |
|---|---|---|---|
| `valve_run` "Van khởi động: XẢ → CHẠY" | `valve_bolt` ← `int_valve_bolt` (kéo theo các con `_lo` và khối nhựa chốt) | Nhảy về XẢ (offset [0, 0, +0,2]), giữ 1,0 s, rồi về 0 trong 1,2 s (inOutCubic). Công tắc khối nhựa qua `setVisible`: bộ XẢ `int_fill_valve_{in, drain_bolt, drain_port}` khi t < 2,2 s; bộ CHẠY `int_fill_valve_{in, run_bolt, run_out}` khi kết thúc và lúc nghỉ. Dùng bản `_lo` ở CUT_Z_BARREL và ST1, tên đầy đủ ở FREE. Từ CUT_Z_BARREL, camera bay tới S08 khoá 3 | nút ở CUT_Z_BARREL, ST1, FREE |
| `sc_index` | `sc_disc` ← `int_sc_disc`, pivot [6,95, 1,545, 0], trục [1, 0, 0]. `sc_piston` ← `int_sc_backflush_piston` | Mỗi chu kỳ 3 s: quay +30° trong 0,48 s; piston đi +0,060 m z ở 0,8–1,4 s, về ở 1,4–2,0 s. 12 bước = 36 s, lặp liền. **Độ bẩn** của từng lưới (12 bản sao vật liệu `za_sc_screenpack`, màu `#A8B0B8` → `#4A3320`): góc = `cavity_angle_deg` (extras) + 30 × số bước. Trong cửa sổ dòng chảy [−150°; −30°]: bẩn tăng từ i/5 lên (i+1)/5 trong lúc dừng. Ở trạm 0°: về 0 trong lúc piston đẩy | tự chạy ở GHOST_SC; nút Dừng/Chạy |
| `die_open` | 9 nhóm `dev_die_{body_upper, flex_lip, thermal_bolts, choker_bolts, bolt_actuator_rail, lifting_lugs, cable_harness, heater_conduit}`, `dev_util_air_hose_die`; mover cho `die_body_bolts__top`, `die_heater_boxes__top` | +0,9 m Y trong 2,4 s, giữ nguyên ở đó. Sau đó mặt trước khối nhựa khuôn (`uFront`) chạy 0 → 1 trong 2,0 s. Xong thì tính lại hộp bao của vùng chọn | tự chạy ở CUT_DIE_PLAN; nút "Nhấc lại" |

### 2.5 Khối nhựa, tấm PET, màn nhựa (`fills.json`)

**FillMaterial** (`MeshStandardMaterial` + `onBeforeCompile`, cache key `'ze-fill'`), áp cho 60 node (59 mesh `za_fill_melt` + `ctx_melt_curtain`), độ mờ 0,6 như Đợt 1:
- **Một biên dạng X thế giới cho cả tuyến:** 27 vùng xếp theo X trong mảng uniform (`x0`, `x1`, `T_in`, `T_out`, `pitch`, `speed`). Cần biên dạng chung vì có mesh trải nhiều vùng (`int_fill_screw_x2450` đi từ X 0 tới 2,45).
- **Màu pha:** hạt `#DBD6C2` → nhựa chảy `#D95709`, smoothstep trên X 1,52–1,90.
- **Vân trôi** `fract((x − t·v)/pitch)`: vùng vít v = pitch × rpm/60 × k (k = 0 / 1/20 / 1 theo chế độ rotor); vùng đường nhựa sọc 0,12 m cùng tốc độ z09 (minh hoạ); vùng `curtain` 0,347 m/s × hệ số trục cán.
- **Chế độ nhiệt:** thang 20–300 °C (xanh → vàng → đỏ), T nội suy theo X trong từng vùng; chú thích "50–300 °C, *: giả định" cạnh nút.
- **Khuôn** (`int_fill_die*`): vật liệu riêng, `radial`, gốc [9,126, 1,2, 0], bán kính 1,25 m, `uFront` bỏ fragment khi u > front.
- **Khi bị cắt (FREE):** `Material.clone()` **không chép `onBeforeCompile`**. Vì vậy `cutVariant` gọi `src.userData.zeVariant(planes, cap, hatch)` để dựng lại vật liệu có cả phần chèn khối nhựa lẫn phần chèn nắp. Vật liệu tấm và lưới bẩn dùng cùng hook.

**SheetMaterial** (`ctx_sheet` không có UV, nên hoa văn là thủ tục): tham số đường đi s(p) theo từng đoạn trên mặt (x, y):
- ôm trục giữa, tâm [9,776, 1,601], r 0,4005, −90° → 90° qua phía +X;
- ôm trục trên, tâm [9,776, 2,403], −90° → 90° qua 180°;
- đoạn thẳng y 2,805, x 9,776 → 12,5.

Sọc 0,30 m, rộng 12 %, trôi với v = 2π·0,4·9,95/60 = **0,4168 m/s** × hệ số trục cán. Giữ trong suốt 0,35, `depthWrite` false như Đợt 1.

**`renderOrder` của vật trong suốt:** khối nhựa 1 → kênh lọc 2 → ghost 3 → tấm và màn nhựa 4.

### 2.6 Rotor, morph và điều khiển

**Rotor:**
- bật thêm 4 rotor slice 2 trong `rigInterior`: `pump_gear_top/bottom`, `gbx_input/counter`. Trong `rotors.json` đã có pivot và `attach`, không cần dữ liệu mới;
- trục cán đã quay từ Đợt 1 (D8). Đợt 2 chỉ đồng bộ tấm PET với chúng.

**Morph (CUT_DIE_AA):**
- 2 nút bật/tắt: "Khe môi ×10" (`gap_x10`) và "Bu-lông nhiệt đẩy" (`lip_push`, chỉ dùng được khi đang ×10);
- tween 0,6 s trên mọi mesh của `int_die_section_upper`, `int_die_thermal_bolts_y0`, `int_die_thermal_bolt_y0`, `int_fill_die_y0`;
- dòng đọc số (Q1): khe thật = 1,00 − 0,15·`lip_push` mm, khe vẽ = 1,00 + 8,975·`gap_x10` − 1,5·`lip_push` mm.

**Dòng ngữ cảnh của toolbar:**

| Trạng thái | Điều khiển |
|---|---|
| CUT_Z_BARREL, ST1, FREE | nút van |
| GHOST_SC | Dừng/Chạy đĩa |
| CUT_DIE_PLAN | "Nhấc lại" |
| CUT_DIE_AA | 2 nút morph + dòng đọc số |
| mọi trạng thái | "Màu: Pha / Nhiệt độ" |

### 2.7 Thay đổi dữ liệu (`make_data.py`, `check_glb.mjs`, `Makefile`)

Port `gen_dot2.py` vào `make_data.py`:
1. **`FIXED`** thêm 6 trạng thái, theo thứ tự FULL, CUT_FEED, CUT_Z_BARREL, CUT_X2450, CUT_X4120, GHOST_DRIVE, GHOST_SC, CUT_PUMP, CUT_DIE_PLAN, CUT_DIE_AA, ST1_Z_FULL. Thêm luật tên ở 2.1 và hai chỗ sửa contract.
2. **Khoá mới của trạng thái:** `label_short_vi`, `group`, `clips_on_enter`, `frame_box_m`, `morphs` (CUT_DIE_AA), `planner_fix`. `cut_states.json` lên `version: 2`.
3. **File mới:**
   - `clips.json` = `states.dot2.json.clips`;
   - `fills.json` = `.fills`;
   - `node_map.json.splits` = `.splits`.
   Cập nhật `doc` của `rotors.json` và `materials.json`: FillMaterial, SheetMaterial, độ bẩn lưới.
4. **Phép kiểm (exit 1 nếu sai):**
   - luật của PLAN-DOT1 §3.3.5 cho 11 trạng thái, tính cả phần tách;
   - đích `die_open` không bị ẩn hay cắt ở CUT_DIE_PLAN;
   - mỗi tên van có bản `_lo`;
   - mọi mesh dùng `za_fill_melt` có trong `fills.nodes`;
   - nguồn tách tồn tại;
   - tên trong clip tra được.
   **Cảnh báo, không dừng:** phần nằm trong `clip` có thể tích / bbox > 0,8. Hiện chỉ có `sidefeed_adapter` 0,81 ở ST1; cần xem bằng mắt.
5. **`--compare dot2`** so với `web/dot2/states.dot2.json`.
6. **`check_glb.mjs verify`** kiểm tên trong `clips` / `fills` / `splits`. **`make publish`** chép 7 JSON.
7. **Gộp lên trên các sửa của fixer Đợt 1:** I1 ẩn vỏ che, I2 camera X2450, M1 camera FULL. Builder dữ liệu bắt đầu sau khi fixer xong.

---

## 3. Module code (cây `web/web-check/src/` của Đợt 1)

| File | Mới / sửa | API, trách nhiệm |
|---|---|---|
| `data.ts` | sửa | `StateId` thêm 6 id; `FIXED_STATE_IDS` theo thứ tự ở 2.7; kiểu `ClipsJson`, `FillsJson`, `SplitRec`, `CutState.{clips_on_enter, frame_box_m, morphs, label_short_vi, group}`; tải 7 JSON |
| `scene/splits.ts` | mới | `applySplits(scene, data): SplitReport`, gọi trong `rigLine` (mục 2.3); idempotent nhờ `zeRigged` |
| `scene/rig.ts` | sửa | rotor slice 2 trong `rigInterior`; `reg.movers`; `reg.splitReport`; gọi `rigMovers` sau `rigInterior`; dựng lại khi HMR |
| `scene/Clips.ts` | mới | `rigMovers(data)`, `playClip(name)` (chỉ gọi trong hàng đợi), `stopClips()`, `seekClip(name, t)`, `tickClips(dt)`, `clipInfo()`, `screenDirt()`. Dùng chung `ease.ts` (inOutCubic) |
| `scene/Animator.tsx` | mới | một `useFrame` theo thứ tự: rotor (code Đợt 1 chuyển vào đây) → `tickClips` → `flowGlobals.uTime`. Tôn trọng `freeze` |
| `scene/FillMaterial.ts` | mới | `flowGlobals {uTime, uMode, uScrewK, uRollK}`, `makeFillMaterial('line' \| 'die', fills)`, `setDieFront(v)`, `fillColorAt(x, mode)` (bản JS của shader cho test), `userData.zeVariant` |
| `scene/SheetMaterial.ts` | mới | `makeSheetMaterial(sheet)` cùng `zeVariant` |
| `scene/Morph.ts` | mới | `setMorph(key, 0 \| 1, smooth)`, `resetMorphs()`, `lipReadout() → {true_mm, drawn_mm}` |
| `scene/materials.ts` | sửa | `za_fill_melt` → FillMaterial (thay bản sao trong suốt của Đợt 1); `ze_sheet_pet` → SheetMaterial; `ze_melt_curtain` → FillMaterial vùng `curtain`; 12 bản sao `za_sc_screenpack` cho độ bẩn; `renderOrder` |
| `scene/Cuts.ts` | sửa | `cutVariant` dùng `src.userData.zeVariant` khi có; `resetCuts` gọi `stopClips()` và `resetMorphs()`; `applyState(id, {camera, smooth, clips})` chạy `clips_on_enter` |
| `scene/precompile.ts` | sửa | duyệt 11 trạng thái với `clips: false`; đo lại thời gian (mục tiêu ≤ 1,5 s) |
| `scene/Selection.tsx` | sửa nhỏ | tính lại bbox khi `store.clipTick` đổi (lúc clip kết thúc) |
| `store.ts` | sửa | `fillMode`, `clip`, `morph`, `frozen`; `playClip(name)` (enqueue), `setMorph`, `setFillMode`, `freeze` |
| `ui/Toolbar.tsx`, `ui/text.ts`, `ui/ui.css` | sửa | nhóm trạng thái (Q3), dòng ngữ cảnh, chú thích nhiệt, dòng đọc số `#ze-readout` |
| `test/hooks.ts` | sửa | mới: `freeze`, `stateDiff`, `frameCheck`, `clip`, `clipSeek`, `clipState`, `movers`, `screens`, `morph`, `morphs`, `fillProbe`, `fillColorAt`, `sheetProbe`, `selftest2`. Mở rộng: `selfcheck` (parts, splits), `rotorTest` (12), `cutRoundTrip` (11 trạng thái + kiểm vị trí nghỉ), `capCheck` (tự `freeze`) |

---

## 4. Việc và ước lượng

Một cặp: builder dữ liệu (ngắn) chạy song song với builder web. Builder web dùng `states.dot2.json` làm bản thay thế ngay từ đầu, nên không phải chờ. Cặp này rút ngắn khoảng 1,5 h và giữ ngữ cảnh của builder web nhỏ. Cả hai bắt đầu khi fixer Đợt 1 đã xong và người dùng đã xem Đợt 1.

| # | Builder | Việc | Ước |
|---|---|---|---|
| DB1 | dữ liệu | Port `gen_dot2.py` vào `make_data.py` (mục 2.7, bước 1–5), gộp với các sửa của fixer | 1,0 h |
| DB2 | dữ liệu | `check_glb verify`, `make publish` 7 JSON, `make -C web all`, mục Đợt 2 trong `REPORT-A.md` | 0,5 h |
| WB0 | web | Bản thay thế: tách `states.dot2.json` thành `public/data/*` (tạm) | 0,25 h |
| WB1 | web | `data.ts`, rotor slice 2, `Animator.tsx` | 0,5 h |
| WB2 | web | `splits.ts` + registry + BVH + `selfcheck.splits` | 1,0 h |
| WB3 | web | `Clips.ts`: mover, 3 clip, công tắc van, độ bẩn, mặt trước khuôn, nối với hàng đợi / `resetCuts` / `applyState` / precompile | 2,0 h |
| WB4 | web | `FillMaterial.ts`, `SheetMaterial.ts`, màn nhựa, `zeVariant` trong `cutVariant`, `renderOrder` | 1,75 h |
| WB5 | web | `Morph.ts` + điều khiển CUT_DIE_AA + dòng đọc số | 0,5 h |
| WB6 | web | Toolbar: nhóm, dòng ngữ cảnh, chú thích; `text.ts` | 1,0 h |
| WB7 | web | Hook mới, mở rộng hook cũ, `selftest2()` | 1,5 h |
| WB8 | web | Tự chạy E1–E11 trên Chrome (ngữ cảnh riêng), ảnh vào `web/review/dot2/builder/` | 1,0 h |

**Tổng:**
- builder dữ liệu khoảng 1,5 h;
- builder web khoảng 9,5 h (đổi sang dữ liệu thật ở khoảng giờ thứ 2);
- sau đó reviewer độc lập trên Chrome 1 h, rồi fixer riêng 1 h.

---

## 5. Rủi ro và bài học từ review Đợt 1

| Rủi ro | Cách giảm |
|---|---|
| **Khối đặc thành nắp lớn** (I1: vỏ che đặc bị cắt thành mảng gạch chéo, làm `capCheck` chập chờn) | Luật: phần thực tế là vỏ rỗng mà mô hình đặc (vỏ che, tủ, nắp chắn) thì **ẩn, không cắt**. `make_data` cảnh báo khi thể tích / bbox > 0,8. Đã áp cho ST1 (vỏ che c1–c6). Các danh sách cắt mới có tỉ lệ ≤ 0,67, trừ `sidefeed_adapter` 0,81: xem bằng mắt |
| **Khung hình preset** (I2: X2450 quá chật; M1: FULL chỉ thấy máy đùn) | Chọn khoá rộng (S10 khoá 1 thay ST7; S11 khoá 2). Thêm `frameCheck` (E2) ở 1920 và 1366 px, có tính phần panel che |
| **Tên trục** (I3) | Chữ trên giao diện luôn dùng trục Blender ("Y = 0" là mặt đứng dọc dòng chảy, "Z = 1 200" là độ cao); đơn vị khớp với số hiện. Code vẫn dùng trục three ở bên trong |
| **Test chập chờn vì rotor** (M8) | Có `freeze()`. `capCheck` và `pickAt` tự đóng băng. Clip kiểm bằng `clipSeek`. `rotorTest` tự đo bằng `performance.now()` và báo tần số rAF; dưới 50 Hz (cửa sổ bị che) thì chạy lại |
| **Thao tác lạ trong Chrome dùng chung** (rotor tự đổi chế độ, thiết bị tự được chọn, click lệch 2×) | Dùng `isolatedContext` riêng. Đặt lại emulation sau `bringToFront`. Chỉ tin sự kiện `isTrusted`. Không đo fps khi còn bản app khác đang vẽ. Lặp lại một lần trước khi kết luận lỗi |
| Bản sao vật liệu mất `onBeforeCompile` (khối nhựa thành trắng ở FREE) | Hook `zeVariant` (2.5); ảnh ở E7 |
| Tách island mơ hồ | Kiểm khoảng cách 10 mm và tổng tam giác (E1); có lỗi thì `console.error`, D11 bắt được |
| Precompile dài ra với 11 trạng thái | Đo `precompileStats.ms`; nếu > 1,5 s thì chỉ precompile trạng thái có chương trình mới |
| Xung đột với fixer Đợt 1 | Không ai sửa `web-check/` hay `make_data.py` cho tới khi fixer xong |
| Chấp nhận, chỉ ghi chú | • GHOST_SC vốn rối (log A1b): `renderOrder` cố định, so với ảnh ST6.<br>• Chọn trên môi đã morph lệch khoảng 9 mm, vì three-mesh-bvh dùng hình gốc.<br>• Trục cán `cap: force` ở CUT_DIE_AA vẫn thấy giá qua đầu trục hở (M3); bịt đầu trục phải sửa trong Blender, ngoài Đợt 2 |

---

## 6. Quyết định mở (có đề xuất)

**Q1. Dòng đọc số khe môi ở CUT_DIE_AA có phải là HUD không?**
- **Đề xuất:** không phải HUD.
- Đó là một dòng chữ trong dòng ngữ cảnh của toolbar, cạnh nút ×10, cùng loại với số mm của thanh trượt FREE ở Đợt 1: "Khe môi thật 1,00 mm (vẽ ×10)".
- Không có nhãn 3D, không có panel nổi.
- Nếu người dùng coi đây là HUD thì bỏ dòng này; E6 chỉ còn kiểm influence.

**Q2. Tách băng nhiệt, bu-lông và hộp nhiệt khuôn bằng cách nào?**
- **Đề xuất:** tách island ở runtime (mục 2.3), đúng như PLAN-DOT1 §3.1.2 đã hẹn.
- Cách này không đổi GLB, không đổi số đếm của Đợt 1 (D14) và không cần Blender.
- Phương án khác: tách khi xuất, trong `export_glb.py` (Blender nền, `separate LOOSE`). Cách đó sạch hơn về tên, nhưng phải xuất lại `line.glb`, đổi 354 node và `object_to_device`, và đụng vào phạm vi của fixer.

**Q3. Toolbar với 11 trạng thái cố định cùng FREE: nhóm hay để phẳng?**
- **Đề xuất:** nhóm, mỗi nhóm một nút có menu thả. Chữ ngắn lấy từ `label_short_vi`, `label_vi` đầy đủ làm tooltip:
  - "Toàn bộ";
  - "Xi lanh ▾" (CUT_FEED, CUT_Z_BARREL, CUT_X2450, CUT_X4120);
  - "Đường nhựa ▾" (GHOST_SC, CUT_PUMP);
  - "Khuôn ▾" (CUT_DIE_PLAN, CUT_DIE_AA);
  - "Truyền động" (GHOST_DRIVE);
  - "Toàn tuyến" (ST1);
  - "Tự do".
- Để phẳng 12 nút sẽ thành 3–4 hàng ở 1366 px, làm lỗi M5 nặng thêm.
