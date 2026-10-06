# Sửa M1 (camera khi đổi hướng cắt) và M3 (lõi trục cán): kế hoạch

> **Bản 2.** Đã sửa theo `web/review/flow/review-plan-m1-m3.md` (2 C, 5 I, 7 M). Bảng cuối file ghi mỗi mục được xử lý ở đâu.
>
> Làm ngay trong phiên (native). Xong thì một reviewer độc lập kiểm lại. Các bước dùng checkbox (`- [ ]`).

**Mục tiêu:** sửa hai lỗi nhỏ còn lại sau vòng kiểm lại của `web/review/flow/review-flow-01.md`. Không sửa Blender, không xuất lại GLB.
- **M1:** đang ở "Tự cắt" mà đổi hướng cắt hoặc lật phía giữ thì camera không xoay theo, nên mặt cắt có thể nằm dọc tia nhìn hoặc ở sau lưng camera.
- **M3:** tâm mặt cắt trục cán có một "đĩa xám sáng" trông như lỗ thủng.

Lỗi N1 (vạch cam của màn nhựa trên mặt cắt trục giữa) cùng nguyên nhân với M3. Bản thử của reviewer cho thấy cách sửa M3 cũng xoá N1, nên N1 được kiểm như một mục bắt buộc.

**Cách làm:**
- **M1:** sửa ở web (`store.ts`).
- **M3:**
  - thêm profile trục cán vào dữ liệu (`make_data.py` → `node_map.json`);
  - thêm một nhánh shader trong nắp cắt lúc chạy (`Cuts.ts`);
  - sửa phép bắn tia (`Picking.ts`) để bấm vào mặt cắt chọn đúng trục cán.

**Công nghệ:** Python 3 stdlib (dữ liệu); Vite + React 19 + R3F 9 + three 0.186 + camera-controls 3.1.2 + zustand 5 (web). Kiểm tra bằng Chrome riêng điều khiển qua puppeteer.

**Spec:**
- `web/PLAN-FLOW.md` §10;
- `web/review/flow/review-flow-01.md`, mục "Kiểm lại sau sửa (vòng 1)";
- `web/review/flow/review-plan-m1-m3.md`.

## Nguyên nhân (đã đo, reviewer đo lại khớp)

### M3: "lõi rỗng" không phải lõi rỗng
Mesh `ctx_roll_*_1` (`ze_chrome`) trong `public/models/line.glb` là một **khối đặc tròn xoay quanh trục three z**. Không có mặt nào hướng vào trong.

Các vòng đỉnh thật của `_1`, dạng (nửa chiều dài h; bán kính r):
- (1,292; 0,400);
- (1,300; 0,392 và 0,190);
- (1,310; 0,190 và 0,150);
- (1,600; 0,150).

Mesh `_2` (`ze_steel`, cổ trục thép) có r 0,150–0,151 ở h 1,31–1,60, bọc ngoài cổ trục chrome. Tâm 3 trục: (9,776; 0,799 / 1,601 / 2,403; 0). Cả `_1` và `_2` đều thuộc cap class `steel`.

Nắp cắt lúc chạy được vẽ ở **thành xa**, tức mặt sau cùng mà tia nhìn gặp, kéo lại 0,6 mm (README "Cap depth bias"). Nhìn dọc trục, tia đi trong vùng r < 0,15 gặp **mặt trước của `ctx_roll_stand_1`** (gối đỡ, vỏ ổ bi ôm cổ trục) ở z ≈ 1,40, trước thành xa. Mặt này thắng phép thử độ sâu và hiện thành đĩa xám sáng.

Bằng chứng (`pickAt`, FLOW, camera (10,05; 1,85; −3,2) → (9,776; 1,601; 0)):
- r 0,05 / 0,10 / 0,14: trúng `ctx_roll_stand_1`, mặt trước, z 1,40;
- r 0,16 / 0,17 / 0,25: trúng `ctx_roll_middle_1`, mặt sau (nắp).

Màu pixel: đĩa (190; 194; 198), nắp (142; 149; 156) / (122; 128; 134). Ẩn `ctx_roll_*_2` thì đĩa **vẫn còn**.

### M1: chọn camera hiện tại
`faceFreeCut` chỉ chạy khi vào FREE. Phép thử của nó dùng `|dir·n| ≥ 0,3`, lấy trị tuyệt đối, nên camera **quay lưng** với mặt cắt cũng đạt.

Bảng dưới ghi `khoảng cách tới mặt / dir·n`. Tên trục là trục three: y = "Cắt nằm" (Z Blender), z = "Bổ dọc" (Y Blender).

| Mặt cắt | FULL | CUT_FEED | CUT_Z_BARREL | CUT_X2450 | CUT_X4120 | FLOW |
|---|---|---|---|---|---|---|
| x = 3 | **−16,2 / +0,59** | +1,3 / +0,42 | +1,2 / −0,05 | −0,8 / +0,78 | −2,1 / +0,55 | −2,9 / 0,00 |
| x = 3, lật | +16,2 / −0,59 | **−1,3 / −0,42**: quay lưng mà vẫn được chọn | | | | |
| y = 1,2 | −7,4 / +0,28 | | **−1,1 / +0,57** | | | |
| y lật, z lật | không preset nào đứng ở phía bị bỏ | | | | | |
| z = 0 | **−17,3 / +0,76** | | | | | −25 / +0,99 |

## Ràng buộc chung
- Không Blender, không xuất GLB. Chỉ dùng `make -C web data verify publish` và `make -C web compare-drafts`. Hai GLB giữ nguyên byte: 5 793 436 / 1 982 388 B.
- Không sửa tay `web-check/public/data`.
- Toạ độ three = Blender (x, z, −y).
- Trong shader, mặt phẳng lấy từ uniform `clippingPlanes[0]` của three:
  - hệ view;
  - điểm X bị bỏ khi `n·X + w < 0`;
  - chỉ đúng khi `renderer.clippingPlanes` rỗng (`cutRoundTrip` kiểm `glClippingPlanes = 0`).
- Vật liệu chỉ đổi qua `setMaterial`; hiển thị chỉ đổi qua `setVisible`.
- Kéo thanh trượt **không** làm camera chạy. Camera chỉ tự xoay khi vào FREE, khi đổi hướng cắt, hoặc khi bật/tắt "Lật phía giữ".
- Chữ trên giao diện không đổi.

## Điểm reviewer cần soi
1. **Vạch đánh dấu quay** `anim_roll_markers_*_aa`, nằm trước mặt phẳng 0,7 mm: vẫn hiện liền ở preset FLOW (25 m).
2. **FREE cắt ngang qua trục** (x = 9,776): cả phần cổ trục cũng là màu nắp, không lộ gối đỡ.
3. **Camera đứng phía bị giữ lại** (FREE vừa lật): ảnh không đổi so với trước khi sửa.
4. **Tấm film và màn nhựa sát trục** (I1, N1): không hiện trên mặt cắt ở FLOW và FREE Y = 0.
5. **Bấm hướng cắt liên tục** (X → Y → X trong 120 ms): camera dừng ở góc của lần bấm cuối, không kẹt hàng đợi.
6. **Bấm vào tâm mặt cắt trục cán:** chọn trục cán, không chọn gối đỡ.

---

### Task 1: M1, camera theo hướng cắt

**Files:**
- Modify: `web/web-check/src/store.ts`: `facing`, `facingPreset`, `mirrored`, `faceFreeCut`, `setFree`, `freeCamDebug`.
- Modify: `web/web-check/src/test/hooks.ts`:
  - thêm hook `freeCamTest`;
  - thêm khoá `M1` vào `selftest`;
  - `capCheckFrozen` FREE chờ hàng đợi rồi đặt lại ống kính.

**Interfaces:**
- Dùng:
  - `freePlane` (`scene/FreeClip.ts`);
  - `applyPreset(p, smooth)` (`scene/CameraRig.tsx`);
  - `enqueue` (`scene/stateQueue.ts`), `queueDrained` (đã import trong `hooks.ts`);
  - `FIXED_STATE_IDS`, `CameraPreset`, `V3`.
- Tạo:
  - `export const freeCamDebug = { last: '' }` trong `store.ts`, giá trị `'keep'`, hoặc id preset, hoặc `'mirror:<id>'`;
  - `__ze.freeCamTest(): Promise<{ cases, ok }>`.

- [ ] **Bước 1: hook kiểm thử (sẽ fail).** Trong `hooks.ts`, thêm các hàm sau. Chúng đọc **giá trị đích** của camera-controls, nên không phải chờ máy bay xong.
```ts
/** review-flow-01 recheck M1: after entering FREE, changing the axis or flipping, the camera's END pose faces the section */
const endPose = () => {
  const c = controlsRef.current!
  const pos = c.getPosition(new THREE.Vector3(), true)
  const dir = c.getTarget(new THREE.Vector3(), true).sub(pos).normalize()
  return { pos, side: round(freePlane.distanceToPoint(pos)), dot: round(dir.dot(freePlane.normal)) }
}
const freeCamTest = async () => {
  const ui = useUi.getState
  const off = reg.data.states.FREE.offset_default_m
  const cases: Record<string, unknown>[] = []
  const check = (name: string, o: { still?: THREE.Vector3 } = {}) => {
    const e = endPose()
    const moved = o.still ? round(o.still.distanceTo(e.pos), 4) : null
    // gate on geometry only (cap-pixel counts depend on framing, see the plan)
    const ok = e.side < 0 && e.dot >= 0.3 && (moved === null || moved < 1e-3)
    cases.push({ name, side: e.side, dot: e.dot, used: freeCamDebug.last, moved, ok })
  }
  for (const start of ['FLOW', 'FULL', 'CUT_X2450'] as FixedStateId[])
    for (const axis of ['x', 'y', 'z'] as Axis[])
      for (const flip of [false, true]) {
        await changeState(start, { camera: true, smooth: false })
        const before = endPose().pos
        ui().setFree({ axis, offset: off[axis], flip }) // not in FREE: no camera job
        await changeState('FREE')
        // FULL and CUT_X2450 already face x = 3: the camera must not move (review recheck)
        check(`${start}->FREE ${axis}${flip ? ' flip' : ''}`, !flip && axis === 'x' && start !== 'FLOW' ? { still: before } : {})
      }
  // inside FREE, from the FLOW camera (z cut): change axis and flip
  await changeState('FLOW', { camera: true, smooth: false })
  ui().setFree({ axis: 'z', offset: 0, flip: false })
  await changeState('FREE')
  for (const [axis, flip] of [['x', false], ['x', true], ['y', true], ['y', false], ['z', true], ['z', false]] as [Axis, boolean][]) {
    ui().setFree({ axis, offset: off[axis], flip })
    await queueDrained()
    check(`in FREE -> ${axis}${flip ? ' flip' : ''}`)
  }
  // fast clicks: y then x at once; the second job must see the first flight's END pose (review I1)
  ui().setFree({ axis: 'y', offset: off.y, flip: false })
  ui().setFree({ axis: 'x', offset: off.x, flip: false })
  await queueDrained()
  check('fast y -> x')
  // a low horizontal cut, flipped: mirror fallback near the floor (review I2)
  ui().setFree({ axis: 'y', offset: 0.3, flip: true })
  await queueDrained()
  check('y = 0.3 flip')
  await changeState('FULL', { camera: true, smooth: false })
  return { cases, ok: cases.every((c) => c.ok) }
}
```
  Thêm `freeCamTest` vào `api`. Trong `selftest`, đặt `out.M1 = await freeCamTest()` ngay trước `changeState('FULL')` cuối hàm. Thời gian chạy dự kiến dưới 5 s, vì không chờ camera bay.

- [ ] **Bước 2: `capCheckFrozen` FREE ổn định.**
  - Sau `await changeState('FREE')`: thêm `await queueDrained()`, rồi đặt `(controlsRef.current!.camera as THREE.PerspectiveCamera).setFocalLength(35)`, trước khi tính camera riêng.
  - Lý do: từ giờ `setFree` lúc đang ở FREE có thể xếp một job camera. Preset CUT_Z_BARREL đổi ống kính sang 40 mm, làm số pixel D4 FREE y/z đổi.
  - Ghi số D4 FREE y/z trước và sau thay đổi này.

- [ ] **Bước 3: chạy để thấy fail.**
  - Tải lại `http://127.0.0.1:5178/?selfcheck=1` (1920 × 1080, DPR 1), chạy `await __ze.freeCamTest()`. Kỳ vọng `ok: false`.
  - Ít nhất các ca sau phải fail:
    - `in FREE -> x`: `dot` ≈ 0;
    - `FLOW->FREE x flip`: `dot` ≈ −0,42 (CUT_FEED);
    - các ca `y flip` và `z flip`: `side` > 0;
    - `fast y -> x`.
  - `freeCamDebug` chưa có ở bước này, nên tạm khai báo `{ last: '' }`.
  - **Vì sao chỉ chấm theo hình học:** đếm điểm nắp phụ thuộc khung hình, không phản ánh việc nhìn được hay không. Đo ngày 2026-10-06:
    - lưới 24 × 24 trên màn hình: góc FULL (đã được chấp nhận) với x = 3 được 1 điểm, góc FLOW với z = 0 được 16;
    - tia bắn vào lưới trên mặt phẳng: FULL x được 20/315, FLOW x nhìn dọc (xấu) được 4/111.
  - Phần "đọc được hay không" xét bằng ảnh ở Bước 6.

- [ ] **Bước 4: sửa `store.ts`.** Thay `facing` và `faceFreeCut` bằng:
```ts
/** a camera sees the FREE section when it is on the removed side and looks towards the kept side */
const MIN_FACING = 0.3
const facing = (pos: THREE.Vector3, dir: THREE.Vector3) =>
  freePlane.distanceToPoint(pos) < 0 && dir.dot(freePlane.normal) >= MIN_FACING

/** which camera faceFreeCut used last: 'keep', a fixed-state id, or 'mirror:<id>' (test hooks) */
export const freeCamDebug = { last: '' }

const _p = new THREE.Vector3()
const _d = new THREE.Vector3()
function facingPreset(): FixedStateId | null {
  for (const id of FIXED_STATE_IDS) {
    const p = reg.data.states[id].camera
    if (!p) continue
    _p.fromArray(p.pos)
    _d.fromArray(p.target).sub(_p).normalize()
    if (facing(_p, _d)) return id
  }
  return null
}
/** the preset seen in the mirror of the FREE plane, its target moved onto the plane (the section's middle) */
function mirrored(id: FixedStateId): CameraPreset {
  const p = reg.data.states[id].camera!
  const n = freePlane.normal
  const dist = (v: V3) => n.x * v[0] + n.y * v[1] + n.z * v[2] + freePlane.constant
  const m = (v: V3): V3 => {
    const d = 2 * dist(v)
    return [v[0] - d * n.x, v[1] - d * n.y, v[2] - d * n.z]
  }
  const t = m(p.target)
  const dt = dist(t)
  return { ...p, pos: m(p.pos), target: [t[0] - dt * n.x, t[1] - dt * n.y, t[2] - dt * n.z], source: `mirror of ${id}` }
}
/**
 * review-flow-01 M1 (+ recheck): keep the camera when its END pose (where a running flight will stop) already
 * sees the section; else the first fixed-state preset that faces it; else (flipped cuts: every preset stands on
 * the kept side) the mirror image of the first preset that faces the unflipped plane.
 */
function faceFreeCut(smooth: boolean) {
  const c = controlsRef.current
  if (!c) return
  const pos = c.getPosition(new THREE.Vector3(), true)
  const dir = c.getTarget(new THREE.Vector3(), true).sub(pos).normalize()
  if (facing(pos, dir)) {
    freeCamDebug.last = 'keep'
    return
  }
  let id = facingPreset()
  let p = id ? reg.data.states[id].camera! : null
  if (!id) {
    freePlane.negate()
    id = facingPreset()
    freePlane.negate()
    if (id) p = mirrored(id)
  }
  freeCamDebug.last = p ? (p.source?.startsWith('mirror') ? `mirror:${id}` : id!) : 'keep'
  if (p) void applyPreset(p, smooth)
}
```
  Trong `setFree`:
  - ở đầu hàm thêm `const before = get().free`;
  - sau `setFreePlane(...)` thêm:
```ts
    // review recheck M1: a new direction or side can leave the section edge-on or behind the camera.
    // The job re-checks the state: a state change queued before it may have left FREE.
    if (get().state === 'FREE' && (f.axis !== before.axis || f.flip !== before.flip))
      void enqueue('free camera', async () => {
        if (useUi.getState().state === 'FREE') faceFreeCut(true)
      })
```
  Thanh trượt chỉ đổi `offset`, nên không đi vào nhánh này. Chú thích cũ ở `store.ts:58–62` ("FULL for X and Z, FLOW for Y") sai với y, bỏ đi cùng hàm cũ. Import `enqueue` và các type nếu thiếu.

- [ ] **Bước 5: chạy lại.**
  - `await __ze.freeCamTest()`: `ok: true`, cả 26 ca đạt. Kỳ vọng cột `used`:

| Ca | `used` |
|---|---|
| x | FULL; `keep` khi bắt đầu từ FULL hoặc CUT_X2450 |
| y | CUT_Z_BARREL |
| z | `keep` (từ FLOW, FULL), hoặc FULL |
| x lật | `mirror:FULL` |
| y lật | `mirror:CUT_Z_BARREL` |
| z lật | `mirror:FULL` |
| fast y → x | FULL |

  - `await __ze.cutRoundTrip()`: `ok`.
  - `capCheck` FREE ở D4: vẫn đạt; ghi mốc mới.

- [ ] **Bước 6: soát bằng mắt.** Chụp ở 1920 × 1080 sau khi camera dừng, lưu vào `web/review/flow/builder/m1-*.png`:
  - 6 ảnh "trong FREE → đổi hướng / lật";
  - ảnh `y = 0.3 flip`.

  Tiêu chí: mặt cắt nằm trong khung, đọc được, không bị toolbar che.

  Riêng `y = 0.3 flip`: camera nằm dưới sàn nhìn lên. Đây là cách duy nhất thấy mặt dưới của một lát cắt nằm thấp, và target đã nằm trên mặt cắt. Chấp nhận góc này nếu mặt cắt chiếm ít nhất 1/4 khung. Nếu không đạt thì dừng lại và báo, không tự chế thêm luật.

- [ ] **Bước 7: commit.** Commit `store.ts` và `hooks.ts` với message "FREE: turn the camera to the section on axis change and flip (review M1)".

### Task 2: M3, dữ liệu profile trục cán

**Files:**
- Modify: `web/tools/make_data.py`: hằng `ROLL_SECTION_PROFILE`, `nodes[n]['section']`, luật `intended_diff` cho `node_map`.
- Modify: `web/tools/check_glb.mjs`: thêm vào `verify` phép bắn tia kiểm profile.
- Modify: `web/web-check/src/data.ts`: `SolidSectionRec`, `NodeRec.section`.

**Interfaces:**
- Tạo `node_map.json.nodes.ctx_roll_{bottom,middle,top}.section`:
```ts
export interface SolidSectionRec { shape: 'revolve_z'; centre: V3; profile: [number, number][] } // profile: exactly 3 [half length, radius] bands
```
  và `NodeRec.section?: SolidSectionRec`. Không dùng tên `SectionRec`, vì `data.ts:136` đã có.

- [ ] **Bước 1: kiểm tra trong `check_glb.mjs` verify (sẽ fail vì chưa có dữ liệu).**
  - Có ít nhất 3 node có `section`, và mỗi profile có đúng 3 dải; nếu không thì `fail('SECTION_COUNT', …)`.
  - Với mỗi node có `section`, gom mọi mesh con (toạ độ world) vào một `Raycaster`, đặt `side = DoubleSide` cho vật liệu.
  - Với dải i (h nằm trong (h_{i−1}, h_i], h_{−1} = 0), lấy 3 độ cao: `h_{i−1} + 0,0005`, giữa dải, `h_i`. Ở mỗi độ cao bắn 8 tia từ điểm trên trục (cx, cy, cz ± h) ra ngoài theo phương bán kính. Khoảng cách trúng đầu tiên d là bán kính bề mặt ở đó.
  - **Profile nằm trong khối:** mọi mẫu phải có `d ≥ r_i + 0,0005`.
  - **Profile sát bề mặt:** riêng ở `h = h_i` phải có `d ≤ r_i + 0,003`.
  - Lỗi ghi kiểu `fail('SECTION_PROFILE', name, {band, h, angle, d})`.
  - Mesh `_2` to hơn profile là hợp lệ: phép thử chỉ đòi bề mặt nằm **ngoài** profile.
  - Chạy `make -C web data verify`: kỳ vọng fail `SECTION_COUNT`.

- [ ] **Bước 2: thêm dữ liệu vào `make_data.py`.** Đặt cạnh `force_cap`:
```python
# review-flow-01 M3: the chill rolls are solids of revolution about three z. Their runtime cap is drawn ON the cut plane
# where the plane point is inside this profile (web Cuts.ts, Picking.ts), so the roll stand that overlaps the journal
# volume no longer shows through the section. [half length, radius] in m, 1 mm inside the surface; measured from
# build/models/line.glb ctx_roll_*_1: body r 0.400 to |z| 1.292 (0.392 at 1.300), shoulder r 0.190 to 1.310,
# journal r 0.150 to 1.600. check_glb.mjs verify casts rays from the axis to check it stays inside the solid.
# The centres come from the same bboxes as FLOW flow.sheet.rolls_xy (keep the two in step).
ROLL_SECTION_PROFILE = [[1.29, 0.399], [1.309, 0.189], [1.599, 0.149]]
```
  và trong vòng lặp:
```python
        if n in force_cap:
            nodes[n]['cap'] = 'force'
            b = an_line[n]['bbox']
            nodes[n]['section'] = {'shape': 'revolve_z',
                                   'centre': [round((b[0] + b[3]) / 2, 4), round((b[1] + b[4]) / 2, 4), round((b[2] + b[5]) / 2, 4)],
                                   'profile': ROLL_SECTION_PROFILE}
```
  Trong `intended_diff`, **trước** dòng `if k != 'cut_states': return None` (`make_data.py:665`), thêm:
```python
    if k == 'node_map' and re.match(r'^nodes\.ctx_roll_(bottom|middle|top)\.section$', p):
        return 'review-flow-01 M3: roll section profile (runtime cap on the plane)'
```

- [ ] **Bước 3: chạy.**
  - `make -C web data verify publish`: exit 0.
  - `make -C web compare-drafts`: 0 khác biệt ngoài ý muốn; 3 khác biệt "intended" cho `section`.
  - `git diff --stat web/web-check/public/data`: chỉ có `node_map.json`.
  - Hai GLB giữ nguyên byte.
  - Thử đổi tạm profile thân thành 0,42: verify phải fail `SECTION_PROFILE`. Trả lại 0,399.

- [ ] **Bước 4: commit.** Commit `make_data.py`, `check_glb.mjs`, `data.ts` và `public/data/node_map.json` với message "Data: roll section profile for the on-plane roll cap (review M3)".

### Task 3: M3, nắp trục cán trên mặt phẳng cắt, và chọn đúng khi bấm

**Files:**
- Create: `web/web-check/src/scene/section.ts`: `inSection(p, s, shrink)`, dùng chung cho JS.
- Modify:
  - `web/web-check/src/scene/materials.ts`: `mesh.userData.zeSection`;
  - `web/web-check/src/scene/Cuts.ts`: tham số `section` của `cutVariant`, nhánh shader; `clipPart` truyền vào;
  - `web/web-check/src/scene/Picking.ts`: `filteredRaycast` cho mesh có section;
  - `web/web-check/src/test/hooks.ts`: `readFrame`, `rollCoreProbe`, khoá `M3` của `selftest`, chú thích của `capCheck`.

**Interfaces:**
- Dùng: `SolidSectionRec`, `NodeRec.section` (Task 2).
- Tạo:
```ts
// section.ts: JS twin of the shader's zeInSection
export function inSection(p: THREE.Vector3, s: SolidSectionRec, shrink = 0): boolean {
  const r = Math.hypot(p.x - s.centre[0], p.y - s.centre[1])
  const h = Math.abs(p.z - s.centre[2])
  return s.profile.some(([hh, rr]) => h <= hh - shrink && r <= rr - shrink)
}
```
  - `cutVariant(src, planes, key, cap, hatch, section: SolidSectionRec | null = null)`;
  - `__ze.rollCoreProbe(): Promise<{ views, ok }>`.

- [ ] **Bước 1: hook `rollCoreProbe` (sẽ fail).** Trong `hooks.ts`:
```ts
/** render now and read the whole canvas once (sRGB bytes, row 0 = bottom) */
const readFrame = () => {
  const s = get()
  s.gl.render(s.scene, s.camera)
  const g = s.gl.getContext()
  const w = g.drawingBufferWidth
  const h = g.drawingBufferHeight
  const buf = new Uint8Array(w * h * 4)
  g.readPixels(0, 0, w, h, g.RGBA, g.UNSIGNED_BYTE, buf)
  return { w, h, at: (x: number, y: number) => { const i = ((h - 1 - y) * w + x) * 4; return [buf[i], buf[i + 1], buf[i + 2]] } }
}
/**
 * review-flow-01 M3 + N1: every pixel whose view ray meets the cut plane inside a roll's section (profile shrunk
 * by 10 mm, away from the edges) must show the state's steel cap colour, hatched (x 1 or x 0.72). Dark marker
 * pixels and a 2 px ring around them (antialiased edges) are skipped. Plus: the marker stays dark at the FLOW
 * preset, and a ray at the middle roll's centre picks the roll, not the stand.
 */
const rollCoreProbe = async () => {
  const ui = useUi.getState
  const mode = ui().rotorMode
  const frozen = ui().frozen
  ui().setRotorMode('off')
  ui().setFrozen(true)
  const rolls = (['bottom', 'middle', 'top'] as const).map((k) => reg.data.nodes[`ctx_roll_${k}`].section!)
  const views: Record<string, unknown>[] = []
  const tonesOf = (hex: string) =>
    [1, 0.72].map((k) => {
      const o = { r: 0, g: 0, b: 0 }
      new THREE.Color(hex).multiplyScalar(k).getRGB(o, THREE.SRGBColorSpace)
      return [o.r * 255, o.g * 255, o.b * 255]
    })
  const scan = async (name: string, pos: V3, target: V3, plane: () => THREE.Plane, capHex: string) => {
    if (pos.length) await controlsRef.current!.setLookAt(...pos, ...target, false)
    await raf2()
    const s = get()
    const f = readFrame()
    const dpr = f.w / s.size.width
    const tones = tonesOf(capHex)
    const pl = plane()
    const ray = new THREE.Raycaster()
    const P = new THREE.Vector3()
    const dark = (x: number, y: number) => Math.max(...f.at(x, y)) < 70
    let n = 0
    let bad = 0
    const badAt: unknown[] = []
    for (let y = 2; y < f.h - 2; y += 1)
      for (let x = 2; x < f.w - 2; x += 1) {
        ray.setFromCamera(new THREE.Vector2(((x + 0.5) / f.w) * 2 - 1, -((y + 0.5) / f.h) * 2 + 1), s.camera)
        if (!ray.ray.intersectPlane(pl, P) || !rolls.some((r) => inSection(P, r, 0.01))) continue
        let nearDark = false
        for (let dy = -2; dy <= 2 && !nearDark; dy++) for (let dx = -2; dx <= 2 && !nearDark; dx++) nearDark = dark(x + dx, y + dy)
        if (nearDark) continue
        n++
        const c = f.at(x, y)
        if (!tones.some((t) => Math.max(...t.map((q, j) => Math.abs(q - c[j]))) <= 8)) {
          bad++
          if (badAt.length < 6) badAt.push({ x: Math.round(x / dpr), y: Math.round(y / dpr), rgb: c })
        }
      }
    views.push({ name, pixels: n, bad, badAt, ok: n >= 2000 && bad / n <= 0.005 })
  }
  await changeState('FLOW', { camera: true, smooth: false })
  const flowPlane = () => statePlane('FLOW')!
  const capFlow = reg.data.states.FLOW.cap_colors!.steel
  await scan('FLOW axis', [10.05, 1.85, -3.2], [9.776, 1.601, 0], flowPlane, capFlow)
  // pick at the middle roll's centre (review I4): the roll, not the stand behind it
  const c = new THREE.Vector3(9.776, 1.601, 0).project(get().camera)
  const pick = pickAt(((c.x + 1) / 2) * get().size.width, ((1 - c.y) / 2) * get().size.height)
  views.push({ name: 'FLOW axis pick', object: pick?.object, ok: pick?.device_id === 'ctx_roll_middle' })
  await scan('FLOW oblique (N1)', [11.6, 2.6, -2.4], [9.78, 1.6, 0.2], flowPlane, capFlow)
  // the marker stays dark at the FLOW preset (cap 8 depth steps behind the plane, marker 0.7 mm in front, 25 m away)
  await applyPreset(reg.data.states.FLOW.camera!, false)
  await raf2()
  const mk = reg.parts.get('anim_roll_markers_middle_aa')
  const mc = mk ? reg.boxOfMeshes(mk.meshes).getCenter(new THREE.Vector3()).project(get().camera) : null
  const fr = readFrame()
  const sx = (v: number) => Math.round(((v + 1) / 2) * fr.w)
  const sy = (v: number) => Math.round(((1 - v) / 2) * fr.h)
  const markerRgb = mc ? fr.at(sx(mc.x), sy(mc.y)) : null
  views.push({ name: 'FLOW preset marker', rgb: markerRgb, ok: !!markerRgb && Math.max(...markerRgb) < 70 })
  const capSteel = reg.data.materials.cap_colors.steel!
  ui().setFree({ axis: 'z', offset: 0, flip: false })
  await changeState('FREE')
  await queueDrained()
  await scan('FREE z=0 axis', [10.05, 1.85, -3.2], [9.776, 1.601, 0], () => freePlane, capSteel)
  ui().setFree({ axis: 'z', offset: 0, flip: true })
  await queueDrained()
  await scan('FREE z=0 flip, from +z', [10.05, 1.85, 3.2], [9.776, 1.601, 0], () => freePlane, capSteel)
  ui().setFree({ axis: 'x', offset: 9.776, flip: false })
  await queueDrained()
  // plane through the 3 axes: body and journal bands (the stand showed through the journal before the fix)
  await scan('FREE x=9.776', [13.2, 1.9, -1.2], [9.776, 1.601, 0], () => freePlane, capSteel)
  await changeState('FULL', { camera: true, smooth: false })
  ui().setFrozen(frozen)
  ui().setRotorMode(mode)
  return { views, ok: views.every((v) => v.ok) }
}
```
  Thêm vào `api`. Trong `selftest`, đặt `out.M3 = await rollCoreProbe()` ngay trước `out.M1`. Mỗi view quét khoảng 2 triệu pixel bằng JS, mất khoảng 0,3–1 s; ghi thời gian thật.

- [ ] **Bước 2: chạy để thấy fail.** Đây là mốc "trước khi sửa", ghi lại số. Theo bản thử của reviewer, số pixel không phải màu nắp trước khi sửa là:

| View | Pixel sai |
|---|---|
| FLOW axis | khoảng 11 900 |
| FLOW oblique (N1) | khoảng 540, chính là vạch cam |
| FREE x=9.776 | có nửa đĩa ở cổ trục |

  `FLOW axis pick` trước khi sửa trả `ctx_roll_stand_1`.

- [ ] **Bước 3: `section.ts` và `materials.ts`.**
  - Tạo `section.ts` như trên.
  - Trong `prepareMesh`, ngay sau `zeClosed`, đặt `mesh.userData.zeSection = meta?.section ?? null`.

- [ ] **Bước 4: `Cuts.ts`.**
  - `clipPart` truyền `mesh.userData.zeSection ?? null` vào `cutVariant`.
  - Id biến thể thêm `section ? section.centre.join(',') + '/' + section.profile.flat().join(',') : '-'`.
  - Tâm và profile là **uniform**. Mỗi biến thể có object uniform riêng, như `uCapColor`. Khoá program cố định là `'ze-cap-sec'` khi có section, `'ze-cap'` khi không có. Cả 3 trục dùng chung **1 program**.
  - Chỉ thêm nhánh section khi `cap && bias && section`. **Không** khai báo lại `projectionMatrix` (khi `bias` thì đã có, `Cuts.ts:50`). `viewMatrix` có sẵn trong prefix fragment.

  Phần khai báo, ngay sau `uniform float uCapHatch;`:
```glsl
uniform vec3 uSecC;
uniform vec2 uSecP[3];
bool zeInSection(vec3 w) {
  float r = length(w.xy - uSecC.xy);
  float h = abs(w.z - uSecC.z);
  for (int i = 0; i < 3; i++) if (h <= uSecP[i].x && r <= uSecP[i].y) return true;
  return false;
}
```
  Trong `onBeforeCompile`:
```ts
shader.uniforms.uSecC = uSecC // { value: new THREE.Vector3(...section.centre) }
shader.uniforms.uSecP = uSecP // { value: section.profile.map(([h, r]) => new THREE.Vector2(h, r)) }
```
  Trong nhánh `!gl_FrontFacing`, **sau** đoạn tính `gl_FragDepth` theo bias:
```glsl
    // review-flow-01 M3: inside this solid the section lies ON the plane. Draw the cap there, 8 depth steps behind
    // the plane (24-bit buffer) so the markers 0.7 mm in front still win, and anything inside the volume (roll
    // stand, journal) stays hidden. Only when the eye is on the removed side (w < 0) and the plane lies between eye
    // and fragment (den > 0). clippingPlanes[0] is this material's plane: renderer.clippingPlanes stays empty.
    vec3 zeQ = -vViewPosition;
    vec4 zePl = clippingPlanes[0];
    float zeDen = dot(zePl.xyz, zeQ);
    if (zePl.w < 0.0 && zeDen > 1e-6) {
      vec3 zeP = zeQ * (-zePl.w / zeDen);
      vec3 zeW = (zeP - viewMatrix[3].xyz) * mat3(viewMatrix);
      if (zeInSection(zeW)) {
        vec4 zeS = projectionMatrix * vec4(zeP, 1.0);
        gl_FragDepth = clamp(zeS.z / zeS.w * 0.5 + 0.5 + 4.8e-7, 0.0, 1.0);
      }
    }
```

- [ ] **Bước 5: `Picking.ts`.** Trong `filteredRaycast`, sau vòng lọc phía bị bỏ, nếu `this.userData.zeSection && hasLocal && m.userData.zeCap`:
  - lấy P = `raycaster.ray.intersectPlane(local[0], _P)`;
  - nếu có P, P nằm phía trước camera, và `inSection(P, section)`:
    - mỗi hit còn lại của mesh này là **mặt sau** (pháp tuyến world · hướng tia > 0) và nằm xa hơn P thì đặt `hit.distance = ray.origin.distanceTo(P)` và `hit.point.copy(P)`;
    - three tự sắp lại theo khoảng cách, nên trục cán thắng gối đỡ, khớp với ảnh.
  - `isCapHit` của `capCheck` vẫn đúng (`t ≤ distance`). Sửa chú thích của `capCheck` (`hooks.ts`, đoạn "they lie on the far inner wall"): mesh có `section` thì nắp nằm trên mặt phẳng.

- [ ] **Bước 6: chạy lại.**
  - `await __ze.rollCoreProbe()`: `ok: true`. Mọi view quét có `bad / pixels ≤ 0,5 %`, kể cả `FLOW oblique (N1)`. `FLOW axis pick` trả `ctx_roll_middle`. Vạch ở preset FLOW tối.
  - `await __ze.capCheck('FLOW', 'ctx_roll_middle')`: đạt.
  - `await __ze.sheetProbe(1)` và `await __ze.cutRoundTrip()`: đạt.
  - Tải trang hai lần liên tiếp; lần 2 là cache shader ấm. Ghi `precompileStats.ms` và số program (`renderer.info.programs.length`) cả hai lần. Theo bản thử, số program dự kiến 32 → 33. Lần ấm không được tăng quá 50 ms so với mốc 137 ms. Lần lạnh chỉ ghi số.

- [ ] **Bước 7: soát bằng mắt.** Chụp ở 1920 và 1366; với FLOW chụp cả hai chế độ màu. Lưu vào `web/review/flow/builder/m3-*.png`. Các góc:
  - FLOW nhìn dọc trục;
  - FLOW nhìn xiên khe cán (N1);
  - FREE bổ dọc Y = 0;
  - FREE cắt ngang qua trục (x = 9,776);
  - FREE vừa lật, camera đứng phía bị giữ nhìn vào máy, để so với ảnh trước khi sửa (điểm soi 3).

- [ ] **Bước 8: commit.** Commit `section.ts`, `materials.ts`, `Cuts.ts`, `Picking.ts` và `hooks.ts` với message "Roll section cap on the cut plane, picking follows it (review M3, N1)".

### Task 4: Kiểm toàn bộ và tài liệu

**Files:**
- Modify: `web/PLAN-FLOW.md`:
  - ở §10 mục 9, câu M1 sửa thành: "FULL cho X, CUT_Z_BARREL cho Z (Blender; y của three), FLOW hoặc FULL cho Y";
  - thêm mục 10 cho đợt sửa này.
- Modify: `web/web-check/README.md`:
  - bảng hook thêm `freeCamTest` và `rollCoreProbe`;
  - mục "Cap depth bias" thêm hai ý:
    - trục cán (`node_map.section`) vẽ nắp trên mặt phẳng, lùi 8 bước độ sâu, xấp xỉ 2,4·10⁻⁵·d² m: 15 mm ở 25 m, 86 mm ở 60 m;
    - ràng buộc: trong profile không được có hình học nào khác sát mặt phẳng hơn mức đó.
- Modify: `web/web-check/SELFTEST.json`: khoá `flow.fix_round_2`.

- [ ] **Bước 1: chạy toàn bộ.**
  - `await __ze.selftest()`: mọi mục true, kể cả `M1` và `M3`. Ghi thời gian chạy.
  - Console 0 lỗi; chỉ còn cảnh báo THREE.Clock đã biết.
  - Mọi request chỉ tới 127.0.0.1:5178.
  - `make -C web data verify` và `make -C web compare-drafts` đều exit 0.
- [ ] **Bước 2: tài liệu và SELFTEST.**
  - Ghi số đo, gồm mốc D4 FREE y/z mới và precompile lạnh / ấm.
  - Ghi N1 là đã sửa.
- [ ] **Bước 3: commit** với message "FLOW fix round 2: docs and self-test (M1, M3, N1)".
- [ ] **Bước 4: reviewer độc lập** (agent mới, prompt gọn).
  - Chỉ kiểm M1, M3, N1, 6 điểm soi ở trên, và hồi quy nhanh.
  - Ghi mục "## Kiểm lại sau sửa (vòng 2)" vào `web/review/flow/review-flow-01.md`.
  - Ảnh lưu vào `web/review/flow/reviewer/recheck-02/`.

## Ngoài phạm vi
- **Gốc của M4 ở FREE Y = 0:** tấm đệm đồng lấn vào thân xi lanh và hiện qua nắp đỏ. Có thể sửa bằng cách như Task 3 cho xi lanh, hoặc sửa trong Blender. Không làm đợt này.
- **Làm quy trình hạt → tấm dễ hiểu hơn:** chờ người dùng chọn hướng; sẽ có kế hoạch riêng.

## Xử lý các mục của `review-plan-m1-m3.md`

| Mục | Xử lý |
|---|---|
| C1 (màu tuyến tính / sRGB) | Task 3 Bước 1: `tonesOf` dùng `getRGB(o, SRGBColorSpace)`. Đọc pixel theo hàng `h − 1 − y` từ một khung đọc một lần |
| C2 (luật profile sai) | Task 2 Bước 1: bắn tia từ trục ra, chỉ đòi bề mặt nằm ngoài profile và sát ở đỉnh dải; `_2` hợp lệ |
| I1 (bấm nhanh) | Task 1 Bước 4: `faceFreeCut` đọc giá trị đích; job kiểm lại `state === 'FREE'`. Ca `fast y -> x` |
| I2 (Y lật thấp) | Task 1 Bước 4: target ảnh gương chiếu lên mặt phẳng. Ca `y = 0.3 flip` và tiêu chí ảnh ở Bước 6 |
| I3 (probe không phân biệt) | Task 3 Bước 1: quét dày mọi pixel trong section, cả cổ trục và cả 3 trục. N1 bắt buộc |
| I4 (bấm chọn gối đỡ) | Task 3 Bước 5: `filteredRaycast` đặt hit mặt sau lên P; `FLOW axis pick` |
| I5 (program, compile) | Task 3 Bước 4: uniform, 1 program `'ze-cap-sec'`. Bước 6 đo lạnh / ấm |
| M1 (`projectionMatrix`) | Task 3 Bước 4: không khai báo lại |
| M2 (tên trùng) | `SolidSectionRec` |
| M3 (chờ hàng đợi) | `queueDrained()` sau `setFree` trong các hook; `capCheckFrozen` đặt lại 35 mm; probe trả lại rotor / freeze cũ |
| M4 (`compare-drafts`) | Task 2 Bước 2–3 |
| M5 (`freeCamTest` chậm, không ghi preset) | Đọc giá trị đích, không chờ; `freeCamDebug.last`; `source: 'mirror of …'` |
| M6 (tên trục) | Bảng nguyên nhân và Task 4 ghi rõ trục three / Blender; "§10 mục 9" |
| M7 (nhỏ) | Ghi chú `clippingPlanes[0]` trong shader; README độ lùi theo d²; profile co 10 mm khi lấy mẫu; tâm cùng nguồn bbox với `rolls_xy`; ghi số program |
