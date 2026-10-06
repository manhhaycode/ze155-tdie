# Review kế hoạch `web/PLAN-FLOW-M1-M3.md` (M1, M3)

Reviewer độc lập, 2026-10-06, nhánh `flow-hat-film`. Kế hoạch chưa được thực hiện. Tôi chỉ đọc code, đo trong một Chrome riêng (1920 × 1080, DPR 1, `?selfcheck=1`) và chạy `make -C web data verify` cùng `make_data.py --compare dot1` (chỉ ghi vào `web/build/`). Không sửa code, dữ liệu hay kế hoạch.

Để kiểm nhánh shader của Task 3, tôi dựng **bản thử lúc chạy**, chỉ trong tab của mình. Mỗi trục cán được gán một bản sao của biến thể nắp hiện có, thêm đúng `zeInSection` và đoạn GLSL ở Task 3 Bước 4 (profile `[[1.29, 0.399], [1.309, 0.189], [1.599, 0.149]]`, đẩy lùi `4.8e-7`). Mọi số "sau sửa" dưới đây là của bản thử này. Ảnh nằm trong `web/review/flow/reviewer/plan-m1-m3/`.

## Kết luận

**Duyệt, kèm điều kiện sửa trước khi làm** (approve with changes): 2 C, 5 I, 7 M.

- Hướng sửa M3 (nắp vẽ trên mặt phẳng trong profile tròn xoay) đúng và đã đo được:
  - đĩa xám mất;
  - N1 mất;
  - vạch đánh dấu vẫn hiện ở preset FLOW;
  - camera đứng phía bị giữ lại thì ảnh không đổi một pixel nào.
- Hướng sửa M1 (phép thử có dấu, ảnh gương cho phía lật, chạy qua hàng đợi) cũng đúng. Bảng preset khớp từng số.
- Nhưng có 2 chỗ sẽ chặn ngay người làm:
  - hook `rollCoreProbe` so màu sai không gian màu, nên không bao giờ đạt (C1);
  - luật kiểm profile trong `check_glb.mjs` loại bỏ chính GLB hiện tại (C2).
- Ngoài ra, M1 còn hai lỗ hổng:
  - có race khi bấm nhanh (I1);
  - lật Y ở vị trí thấp đưa camera xuống dưới sàn (I2).

## Lỗi

### C1. `rollCoreProbe` so pixel sRGB với màu tuyến tính, nên `capRatio` = 0 cả trước lẫn sau khi sửa
- **Chỗ:** plan dòng 331–333.
  - `cap.clone().multiplyScalar(k).getStyle(SRGBColorSpace)` trả chuỗi `rgb(...)` sRGB.
  - `new THREE.Color(t)` đọc chuỗi đó **rồi đổi về tuyến tính**, vì ColorManagement đang bật (đo: `true`).
  - Do đó `c.r * 255` là giá trị tuyến tính × 255.
- **Đo ở FLOW, nhìn dọc trục, cap `#8E959C`:**
  - plan tính ra tông (69; 76,6; 84,8) và (49,6; 55; 60,8);
  - pixel thật là (142; 149; 156) và (122; 128; 134).
  - Chạy đúng `run()` của plan thì được `capRatio` = **0** (94 mẫu đều "xấu"). Sau khi sửa shader vẫn là 0.
- **Hậu quả:** Task 3 Bước 2 và 5, Task 4 Bước 1 không bao giờ đạt. Người làm dễ đi sửa shader hoặc nới ngưỡng để đuổi theo một lỗi của test.
- **Sửa plan:** tính tông bằng `const o = {r:0,g:0,b:0}; cap.clone().multiplyScalar(k).getRGB(o, THREE.SRGBColorSpace); [o.r*255, o.g*255, o.b*255]`. Đã thử, kết quả sau khi sửa:
  - FLOW dọc trục: 0,851 → 1,000;
  - FREE z = 0: 0,802 → 1,000.
- **Phụ:** `pixel()` đọc hàng `H − y` (dòng 313), lệch một hàng. Đúng phải là `H − 1 − round(y)`.

### C2. Luật kiểm profile của Task 2 làm fail chính GLB hiện tại, và kiểm sai chiều
- **Chỗ:** plan dòng 251–254: "dải đầu tiên có `h ≤ h_i + 0,0015`, mọi đỉnh `r ≤ r_i + 0,0015`" và "mỗi dải có một đỉnh `r ≥ r_i − 0,0015`".
- **Đo:** chạy đúng luật này trên `web/build/models/line.glb` bằng script nháp, cùng loader và meshopt như `check_glb.mjs`, cho cả 3 trục:
  - Vòng đỉnh thân ở `h = 1,292` (r 0,400) và `h = 1,300` (r 0,392) rơi vào dải **vai**, vì 1,292 > 1,29 + 0,0015. Dải vai cho phép r ≤ 0,1905, nên fail 384 đỉnh mỗi trục.
  - Mesh `_2` (cổ trục thép) có r tới **0,1509–0,1511** ở `h` 1,31–1,60. Dải cổ trục cho phép r ≤ 0,1505, nên fail. Theo câu "0,401 = profile + 1 mm biên + 1 mm dung sai" (+2 mm) thì giới hạn là 0,151, vẫn fail. Công thức (+1,5 mm) và lời giải thích (+2 mm) cũng mâu thuẫn nhau.
  - Dải thân có **0 đỉnh "chạm"**: không có đỉnh nào ở `h ≤ 1,2915`, vì mặt trụ thân chỉ có hai vòng đỉnh ở ±1,292.
  - Các vòng đỉnh thật của `ctx_roll_middle_1`: (1,292; 0,400), (1,300; 0,392 và 0,190), (1,310; 0,190 và 0,150), (1,600; 0,150). Của `_2`: (1,31 và 1,60; 0,150–0,151).
- **Chiều kiểm:** cái cần giữ là **profile nằm trong khối**. Nếu profile to hơn khối, nắp sẽ vẽ lơ lửng trên khe giữa hai trục. Luật "đỉnh không vượt profile + dung sai" chỉ chặn trường hợp khối to ra, mà khối to ra thì vô hại.
- **Sửa plan:** thay hai luật trên bằng phép thử trực tiếp. Với mỗi dải i, bắn tia từ trục ra ngoài ở `h ∈ {0, h_i/2, h_i}` × 8 góc, dùng `Raycaster` DoubleSide trên các mesh của node. Khoảng cách trúng đầu tiên (tức bán kính bề mặt) phải nằm trong `[r_i + 0,0005; r_i + 0,003]`.
  - Đổi profile thân thành 0,42 thì luật này fail, như Bước 3 muốn.
  - Đổi tên mesh con mà còn ít nhất 3 node `section` thì vẫn bắt được.
  - Ghi rõ là `_2` được phép to hơn profile.

### I1. `faceFreeCut` đọc vị trí camera **hiện tại**, nên bấm nhanh X → Y → X thì camera kẹt ở phía bị giữ lại
- **Chỗ:** plan dòng 199 dùng `c.camera.position` / `getWorldDirection`.
  - Job trong hàng đợi chạy ngay, khi chuyến bay mượt của lần bấm trước mới bắt đầu.
  - Lần bấm sau thấy camera "đang nhìn được" ở điểm xuất phát, nên giữ nguyên.
  - Chuyến bay cũ vẫn bay tiếp tới preset của lần bấm trước.
- **Đo:** mô phỏng đúng logic của plan với camera-controls thật.
  - Bắt đầu ở FREE x = 3, camera FULL. Đổi sang y (bay tới CUT_Z_BARREL), 120 ms sau đổi lại x thì job trả "keep". Camera dừng ở CUT_Z_BARREL với `side` **+1,25**, `dot` **−0,05**: đứng phía bị giữ, nhìn dọc mặt cắt.
  - Dùng giá trị đích (`c.getPosition(v, true)`, `c.getTarget(t, true)`, camera-controls 3.1.2, mặc định `receiveEndValue = true`) thì job chọn FULL. Camera dừng ở `side` −16,2, `dot` +0,59.
  - Điểm soi số 5 của plan ("camera dừng ở góc của lần bấm cuối") sẽ fail nếu làm như plan.
- **Sửa plan:**
  - `faceFreeCut` lấy pos và dir từ giá trị đích của controls.
  - Trong job, kiểm lại `useUi.getState().state === 'FREE'`, phòng trường hợp một lệnh đổi trạng thái được xếp hàng trước job camera.
  - Thêm vào `freeCamTest` một ca "bấm nhanh": `setFree(y)`, rồi `setFree(x)` ngay sau đó, rồi mới kiểm.

### I2. Ảnh gương cho Y lật ở vị trí thấp đặt camera dưới sàn
- **Ở Y = 1 200 (mặc định):** gương của CUT_Z_BARREL là camera (1,75; **0,10**; −1,6) nhìn lên (1,85; 1,2; 0). Góc này đọc được: thấy mặt dưới của nắp xi lanh và vít.
- **Ở Y = 300 (thanh trượt cho 0 … 6,3 m):** camera ở (1,75; **−1,70**; −1,6), target (1,85; **−0,60**; 0), cả hai dưới sàn.
  - Ảnh nhìn qua lưới sàn từ bên dưới.
  - Các tủ điện (phần trên 0,3 m được giữ) che gần hết khung. Mặt cắt chỉ còn một dải ở mép trên.
  - Camera ở dưới sàn khi `offset < 1,15`.
- **Ảnh:** `reviewer/plan-m1-m3/m1-mirror-fallback-x-y-z-y0300.png`, xếp theo thứ tự: trên trái X lật, trên phải Y lật, dưới trái Z lật, dưới phải Y = 300 lật.
  - X lật (gương FULL) và Z lật (gương FULL) đều hợp lý.
  - Mặt cắt X lật hơi nhỏ, cỡ như góc FULL với X = 3 000 vốn đã được chấp nhận.
- **Sửa plan:** với trục y, sau khi lấy ảnh gương:
  - đặt `target` lên mặt phẳng (chiếu target xuống mặt cắt);
  - nếu `pos.y < 0,05` thì đẩy camera theo hướng nhìn tới khi y ≥ 0,05 m.
  - Hoặc ghi rõ là chấp nhận góc này. Thêm ca `y lật, offset 0,3` vào `freeCamTest` và ảnh Bước 5.

### I3. Hai view của `rollCoreProbe` không phân biệt được trước và sau, nên N1 không đo được
- **`FREE x=9.776`:** chỉ lấy mẫu `|z| ≤ 1,2` (thân), nên **đạt cả trước khi sửa**.
  - Phần cổ trục mới là chỗ gối đỡ lộ ra (điểm soi 2).
  - Tôi thêm 24 mẫu ở dải cổ trục (|z| 1,32–1,545; y = cy ± 0,06). Trước khi sửa: 4/24 trúng `ctx_roll_stand_1`, ratio gộp 0,967. Sau: 1,000.
  - Ảnh: `m3-free-x9776-journal-before-after.png`. Trước là nửa đĩa xám, sau đã hết. Còn vài pixel lẻ ở mép đầu cổ trục, do biên 1 mm (1,599 so với 1,600).
- **`FLOW oblique (N1)`:** 96 mẫu thưa không trúng vạch 1 px, nên `capRatio` = 1,000 cả trước lẫn sau. Task 4 Bước 2 ("ghi rõ trạng thái N1 theo `FLOW oblique (N1)`") sẽ luôn báo "đã hết".
  - Tôi quét dày mọi pixel có điểm trên mặt phẳng r ≤ 0,39 quanh trục giữa, bỏ pixel tối (vạch).
  - Pixel không phải màu nắp, trước → sau: FLOW xiên **542 → 115**, FLOW dọc trục **11 887 → 123**. Phần còn lại là viền khử răng cưa của vạch.
  - Vạch cam N1 hết hẳn (`n1-flow-oblique-before-after.png`). Vạch này là màn nhựa và tấm ở khe cán z 0,26–0,58, nhìn qua nắp tường xa.
- **Sửa plan:**
  - thêm mẫu dải cổ trục cho view x = 9,776;
  - đổi view N1 sang quét dày, bỏ pixel tối và viền 2 px quanh pixel tối, rồi cho nó thành **bắt buộc**, vì Task 3 sửa được N1;
  - lấy mẫu cả trục trên và trục dưới (rẻ, mà đĩa có ở cả 3).

### I4. Sau khi sửa, bấm vào tâm mặt cắt trục cán lại chọn gối đỡ
- **Đo (bản thử, FLOW nhìn dọc trục):**
  - pixel (902, 540) là màu nắp có vân (122; 128; 134);
  - `pickAt` trả `ctx_roll_stand_1`;
  - `clickAt` chọn **`ctx_roll_stand`**.
- **Nguyên nhân:** `filteredRaycast` (`src/scene/Picking.ts:23–41`) vẫn trúng mặt trước gối đỡ ở z 1,40. Trước khi sửa, pixel cũng là gối đỡ nên việc chọn gối đỡ còn nhất quán. Sau khi sửa, cái người dùng thấy và cái được chọn không còn khớp.
- **Liên quan tới `capCheck`:** cũng vì thế mà `capCheck` (`hooks.ts:521`) không thấy được M3. Các pixel đĩa bị bỏ qua theo nhánh "cap hidden behind something", nên F3 `ctx_roll_middle` đạt cả trước khi sửa. Chú thích của `capCheck` ("they lie on the far inner wall") sẽ sai với trục cán.
- **Sửa plan:** thêm vào Task 3 một bước sửa `filteredRaycast` cho mesh có `zeSection`:
  - nếu điểm tia cắt mặt phẳng P (`ray.distanceToPlane`) nằm trong profile, thì hit mặt sau của mesh đó lấy `distance = t_P` và `point = P`;
  - ba sẽ tự sắp lại theo khoảng cách, nên trục cán thắng gối đỡ, đúng như ảnh.
  - `isCapHit` của `capCheck` vẫn đúng với hit này (`t ≤ distance`). Cập nhật chú thích.
  - Nếu không sửa thì ghi rõ trong plan là chấp nhận sự lệch này.

### I5. Mỗi trục một program, chi phí biên dịch lớn hơn nhiều so với "≤ ~30 ms", và khoá cache thiếu thông tin
- **Đo:**
  - bản thử theo khoá `ze-cap-sec-${cx},${cy}` thêm **3 program** (32 → 35);
  - `compileAsync` (đã dừng vòng frame, như `precompile.ts`) cho 3 program mới mất **239–251 ms**;
  - cùng một khoá cho cả 3 trục (1 program) mất **135–138 ms**;
  - so sánh: precompile hiện tại là 137 ms cho 20 program, vì cache shader Metal đã có sẵn.
- **Khoá cache:** khoá thiếu `cz` và profile. Ba cache program theo khoá, nên một section sau này trùng (cx, cy) mà khác profile sẽ dùng nhầm shader.
- **Sửa plan:**
  - Đưa tâm và profile thành uniform (`uniform vec3 uSecC; uniform vec2 uSecP[3];`, mỗi biến thể một object uniform riêng như `uCapColor`). Dùng một khoá cố định `'ze-cap-sec'`, chỉ còn 1 program.
  - Đo `precompileStats.ms` ở hai lần tải liên tiếp (lần 2 là cache ấm) và ghi cả hai.
  - Đặt ngưỡng theo số đo, không theo 30 ms.

### M1. Lời dặn về `projectionMatrix` dễ gây lỗi biên dịch
Dòng 405 viết "thêm `uniform mat4 projectionMatrix;`, vì đã có sẵn khi `bias`". Nhánh section chỉ chạy khi `bias`, mà `bias` thì đã khai báo uniform này rồi (`Cuts.ts:50`). Khai báo thêm lần nữa sẽ lỗi "redefinition". Nên đổi thành "**không** khai báo lại; `projectionMatrix` đã có khi `bias`, còn `viewMatrix` có sẵn trong prefix fragment (three `WebGLProgram.js:770`)".

### M2. Tên `SectionRec` chắc chắn trùng
`data.ts:136` đã có `SectionRec { group; name_vi }`. Plan nên dùng thẳng `SolidSectionRec`, cả trong chữ ký `cutVariant` ở dòng 301.

### M3. Các hook gọi `setFree` khi đang ở FREE nhưng không chờ hàng đợi
- `rollCoreProbe` (dòng 379–381) đổi z → x rồi chỉ `raf2()`. Job camera mới (bay mượt tới FULL) chạy trước `setLookAt(false)` của probe. Hiện tại nó vô hại chỉ vì FULL và FLOW cùng ống kính 35 mm.
- `capCheck` FREE y và z trong selftest D4 (`hooks.ts:847–848`) cũng gặp chuyện này. Lúc đó `applyPreset(CUT_Z_BARREL)` đổi ống kính sang **40 mm** trước khi `zoomToBox`, nên số pixel `extra_free_y_z` sẽ đổi.
- **Sửa plan:**
  - thêm `await queueDrained()` sau `setFree` trong hai hook;
  - cho `capCheck` đặt lại ống kính 35 mm;
  - ghi rằng D4 FREE y/z cần lấy mốc lại.
- Cũng trong `rollCoreProbe`: cuối hàm đặt cứng `rotorMode 'slow'` và `frozen false`. Nên trả về giá trị cũ như `capCheck`.
- Ghi chú về `slider_range_m.x` (dòng 393) không cần: dải là −5,72 … 12,5, và `setFree` không chặn giá trị.

### M4. Lệnh kiểm "0 khác biệt ngoài ý muốn" chưa đúng
- `intended_diff` chỉ được dùng trong `make -C web compare-drafts` (`make_data.py --compare dot1`), không chạy trong `data verify publish`.
- Luật mới phải đặt **trước** dòng `if k != 'cut_states': return None` (`make_data.py:665`).
- Mốc hiện tại: `compare-drafts` cho 0 khác biệt ngoài ý muốn, `data verify` OK.
- **Sửa plan:** Task 2 Bước 3 thêm `make -C web compare-drafts`.

### M5. `freeCamTest` chậm và không ghi được preset đã dùng
- **Chậm:** 24 ca, mỗi ca chờ `rest`, tối đa 2 s. Ca giữ camera không bao giờ phát `rest`, nên luôn hết 2 s. Ước tính selftest dài thêm khoảng 30–50 s.
  - Đọc giá trị đích của controls (cùng chỗ sửa I1) thì không cần chờ.
  - Có thể vào FREE với `smooth:false`.
- **Không ghi được preset:** Bước 4 yêu cầu "ghi ca nào giữ, ca nào preset, ca nào gương", nhưng giá trị trả về của `faceFreeCut` không đi ra ngoài `setFree` hay `changeState`.
  - Nên lưu `lastFreeCam` (`'keep' | id | 'mirror:' + id`) để hook đọc.
  - Gắn `source: 'mirror of FULL'` vào preset gương.

### M6. Tên trục trong tài liệu
- Task 1 dùng tên trục three: y = "cắt nằm", và y → CUT_Z_BARREL.
- Task 4 dòng 459 dùng tên Blender: "Z dùng CUT_Z_BARREL, không phải FULL".
- Câu cũ trong `PLAN-FLOW.md` §10 mục 9 (dòng 367) dùng tên Blender, nên sửa "Z" là đúng.
- Còn chú thích trong `store.ts:58–62` ("FULL for X and Z, FLOW for Y") dùng tên three, nên sai với y (thực tế là CUT_Z_BARREL). Plan thay chú thích này, vậy là ổn.
- Nên ghi "Z (Blender) = y (three)". Đây là mục 9 của §10, không có mục "§10.9".

### M7. Nhỏ, gom chung
- F8 không có ngưỡng số program (dòng 442).
- Biên 1 mm ở đầu cổ trục (1,599 so với 1,600) để lại vài pixel sáng lẻ ở FREE x = 9,776. Nên giữ mẫu cách đầu profile ít nhất 2 mm.
- `clippingPlanes[0]` chỉ đúng khi `renderer.clippingPlanes` rỗng. Điều này đang được giữ, `cutRoundTrip` kiểm `glClippingPlanes = 0`. Nên ghi một dòng chú thích trong shader.
- Lùi 8 bước độ sâu tương đương khoảng 2,4·10⁻⁵·d² m: 15 mm ở 25 m, 86 mm ở 60 m. Hiện vô hại, vì trong profile không có hình học nào khác sát mặt phẳng. Nên ghi thành ràng buộc trong README "Cap depth bias".
- `flow.sheet.rolls_xy` / `roll_r_m` (I1) và `node_map.section` cùng lấy từ bbox, nên đang khớp (tâm 9,776 / 0,799 / 1,601 / 2,403; r 0,4001). Hai nguồn này có thể lệch nhau về sau; ghi lại trong plan.

## Các điều plan nói đã được xác nhận
1. **Nguyên nhân M3:** `pickAt` từ (10,05; 1,85; −3,2) → (9,776; 1,601; 0) ở FLOW:
   - r 0,05 / 0,10 / 0,14 trúng `ctx_roll_stand_1`, mặt trước, z 1,3999;
   - r 0,16 / 0,17 / 0,25 trúng `ctx_roll_middle_1`, mặt sau, z 1,31 / 1,30;
   - pixel đĩa (190; 194; 198), pixel nắp (142; 149; 156) và (122; 128; 134);
   - ẩn `ctx_roll_middle_2` thì đĩa vẫn còn;
   - ảnh `m3-flow-axis-before-after.png`.
2. **Profile và tâm** của `_1` khớp bảng trong plan. Tâm 3 trục (9,776; 0,799 / 1,601 / 2,403; 0). `_1` là `ze_chrome`, `_2` là `ze_steel`, cả hai cap class steel, cùng màu nắp: FLOW `#8E959C`, FREE `#B84533`, có vân. Hai nắp trùng độ sâu trên mặt phẳng không thấy z-fight.
3. **Quy ước của three 0.186.1:**
   - mặt phẳng ở hệ view (`WebGLClipping.js:147–150`);
   - bỏ khi `dot(vClipPosition, n) > w` (`clipping_planes_fragment.glsl.js:53`), với `vClipPosition = −mvPosition`;
   - `viewMatrix` có trong prefix fragment;
   - phép nghịch đảo `(P − viewMatrix[3].xyz) * mat3(viewMatrix)` đúng;
   - điều kiện `w < 0 && den > 0` cho t ∈ (0, 1].
4. **Bộ đệm độ sâu:** `DEPTH_BITS` 24, stencil tắt, 4 mẫu MSAA, ANGLE Metal (Apple M3 Pro), near 0,02, far 200. Một bước ≈ 1,86 mm ở 25 m, nên 8 bước = 4,77·10⁻⁷.
5. **Bản thử nhánh shader:**
   - FLOW dọc trục 0,851 → 1,000;
   - FREE z = 0 0,802 → 1,000 (tấm `ctx_sheet` mờ phủ lên nắp cũng hết, `m3-free-z0-axis-before-after.png`);
   - FREE z = 0 lật, nhìn từ +z 0,787 → 1,000;
   - camera phía bị giữ: 0 pixel khác;
   - vạch ở preset FLOW vẫn tối (7; 10; 12), số pixel tối trong hộp vạch của 3 trục: 39 / 47 / 42 (`m3-flow-preset-marker-after.png`).
6. **`pixel()`** (render rồi `readPixels`, có antialias) đọc đúng byte màu nắp.
7. **M1:**
   - Phép thử trị tuyệt đối chọn CUT_FEED khi vào FREE từ FLOW với X lật (đo được).
   - Trong FREE, đổi z → x thì camera đứng yên ở FLOW, `dot` 0,00.
   - Bảng phía / dot của plan khớp từng số.
   - Các preset mong đợi ở Bước 4 khớp tính toán: x → FULL, y → CUT_Z_BARREL, z → giữ hoặc FULL, lật → gương của FULL / CUT_Z_BARREL / FULL.
   - `freeCamTest` (phần hình học) fail trước và đạt sau với cả 24 ca.
8. **Thanh trượt** chỉ đổi `offset`, nên không làm chạy camera. Nút trục chỉ hiện khi đang ở FREE (`Toolbar.tsx:141`).
9. **Chỉ chấm theo hình học cho M1** là hợp lý: số điểm nắp phụ thuộc khung hình, không theo việc nhìn được hay không. Có thể thêm điều kiện "điểm trục nhìn cắt mặt phẳng nằm trong khung".
