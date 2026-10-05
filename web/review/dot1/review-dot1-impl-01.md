# Review: Đợt 1 implementation (web-check), round 1

Independent reviewer, 2026-10-05. I tested the running dev server (`npm run dev`, StrictMode) at `http://localhost:5178/?selfcheck=1` in my own isolated Chrome tab (`isolatedContext: reviewer`, viewport 1920 × 1080, DPR 1; then 1366 × 768). I re-measured every criterion myself and did not reuse SELFTEST numbers. I changed no code or data.

**Inputs used:**
- `window.__ze` hooks.
- Real CDP input through chrome-devtools MCP:
  - clicks, a double-click and a hover on the canvas, landing at chosen pixels through a `pointer-events:none` probe element;
  - clicks on tree items and toolbar buttons;
  - real F and Escape key presses.
- Every canvas event I relied on was logged as `isTrusted: true`.

**Not run:** Blender, `make -C web all` (it starts a background Blender) and the MCP.

All evidence is in `web/review/dot1/`. File names below are relative to that folder.

**Test environment notes:**
- Two odd events came from outside my session, and neither reproduced on a re-check:
  - the rotor mode flipped to "Thực tế";
  - `ctrl_drive_cabinet` became selected.
- The window was occluded twice. rAF then dropped to about 1 Hz and screenshots timed out.
- After `bringToFront`, one MCP click landed at 2× the coordinates. Re-applying the viewport emulation fixed it.
- Two other copies of the app were rendering in the same Chrome during the fps runs, so my fps figures are lower than builder B's.

## D1–D15

| # | Result | My evidence |
|---|---|---|
| D1 | **pass** | Fresh isolated context, empty cache: `line_first_frame_ms` 1 734, `interior_ready_ms` 399, `bvh_ms` 454 in total (373 line + 81 interior). The one precompile pass took 587 ms. On the first cut the busy label went "Đang chuyển trạng thái…" → "Đang tải phần bên trong…" → cleared, about 1.0 s after the click |
| D2 | **pass** | `devices()` = 190; `selectAll()` 190/190. Tree: every item in all 10 sections clicked through the DOM → 190/190 selected. One real CDP click on "Xi lanh B3" selects `barrel_b3` and zooms to it (`shot-D2-tree-click-b3.png`) |
| D3 | **pass** | Real click selects `vac_separator` (5 outline meshes plus bbox; `shot-D3-realclick-select.png`). Real hover sets `barrel_b1` with the light blue outline (`crop-hover.png`). Alt+click selects part `feed_platform_grating` (1 of the device's 4 meshes). Real Esc clears. Real F: target 0.6 mm from the bbox centre. Real double-click on `base_drip_tray`: selected, target on the bbox centre. Real click on empty space clears |
| D4 | **partial** | 5 cases pass every time, and the real click on the sample pixel selects the right device: Z_BARREL/b3 24/24, X2450/b3 114/114, X4120/b5 23/23, FEED/throat 22/22, FREE x 3.0/b4 55/55. **X2450/screws is flaky** and depends on the screw angle: it passed once (164/164), then failed 3 of 6 repeat runs, each time with exactly 1 wrong pixel from `barrel_cover_c5`. A real CDP click on an X2450 cap pixel (999, 292) selects `barrel_b3` |
| D5 | **pass** | `rayUnfiltered` 0 after load, after all states, after selections (outline hulls) and after the round trips |
| D6 | **pass** | `cutRoundTrip()` ok, `bad` [], 0 `gl.clippingPlanes`, 0 `freePlane` references. Passed twice, the second time after my what-if restores |
| D7 | **pass** | `timeState` 33–43 ms for all 6 states. That is 2 rAF at about 60 Hz in this contended session; B measured 17 ms. Slider: 0.2 ms of JS per step |
| D8 | **pass** | `rotorTest(2)`: both screws −89.5 °/s (0.6 % error) about [1, 0, 0], same sign. Motor chain −333.7 °/s. Rolls +59.4 / −59.4 / +59.4 °/s about [0, 0, −1]. Visual: rotors frozen for two shots 45.6° apart; the flights moved about 35 px towards +X (`crop-d8-pair.png`) |
| D9 | **pass** | Contended session. FULL 61–70 fps (one sample of 50.6 fps while another window was in front), 686–702 calls, 1.14 M triangles. CUT_FEED 67 fps / 204 calls; Z_BARREL 68 / 200; X2450 60 / 190; X4120 51 / 240. FREE x 3.0 at the FULL camera: 43 fps / 909 calls / 1.33 M triangles; FREE y: 58 / 908. Heap ≤ 220 MB |
| D10 | **pass** | Network transfers: `line.glb` 5 793 436 B, `interior.glb` 1 982 388 B; both match `check.json` |
| D11 | **pass** | 0 errors. 1 warning: "THREE.Clock … deprecated". It comes from R3F (`@react-three/fiber/dist/events-*.esm.js`); no app code uses Clock. The rest is Vite debug lines and the React DevTools info line |
| D12 | **pass** | 54 requests, all to `http://localhost:5178`: page, JS, 5 JSON, 2 GLB, favicon. No font, Draco or HDR request. `interior.glb` was not requested before the first cut and was requested once after it |
| D13 | **partial** | See below. CUT_Z_BARREL and CUT_FEED teach what they should, apart from the covers. CUT_X2450 and CUT_X4120 are spoiled by the solid cover boxes (I1), and X2450 is framed too tight (I2). FULL frames only the extruder (M1) |
| D14 | **pass** | Existing reports, since I did not re-run `make`: `check.json` `ok: true`, `failures: []`. Runtime `selfcheck()`: 0 unknown, 0 missing, 0 orphans, 190 devices, 561 parts after the interior loaded, 8 rotors ready |
| D15 | **pass** | `stat -f '%m %z' out/ze155_anim.blend` = `1791173730 29470668`. It equals `export.json` before and after (`blend_unchanged: true`) |

## D13: what each state teaches

- **FULL** (`shot-FULL.png`):
  - Clean and well lit, no artefacts.
  - The preset (S01 key 2) shows only the extruder. The die, the roll stack and the sheet are off screen or behind the tree panel; `ze155-hero.png` shows the whole line.
- **CUT_Z_BARREL** (`shot-CUT_Z_BARREL.png` against `anim/look/A1a-S04-f1161-ev-r2.png`): a very close match.
  - The barrel is opened at the axis plane.
  - Both screws are whole and turning.
  - Conveying, KB and seal elements are readable; the purple vent windows and the blue ghost dome are right.
  - **But** the cover hardware `barrel_cover_c6_hw` has a horizontal face at y = 1.154. It draws a dark slab over the lower quarter of the frame, where the barrel's outer wall should show (`crop-zb-lower.png`).
  - With the covers hidden (`whatif-CUT_Z_BARREL-covers-hidden.png`) the view matches the A1a render almost exactly: lower barrel, flanges and heater shells.
- **CUT_X2450** (`shot-CUT_X2450.png` against `A1a-x2450-S05b-ev-r2.png`):
  - The figure-8 bore, the two screw profiles with the dark Ø72 disc, and the amber fill are right. The pre-cut plates turn with the screws.
  - **But** the `barrel_cover_c5` cap fills the whole frame.
  - The `_hw` face draws a dark band and a thin line straight through both screw profiles. It reads as a crack, and it is the D4 failure.
  - Even with the covers hidden (`whatif-CUT_X2450-covers-hidden.png`), the 60 mm / 0.77 m preset shows nothing but hatch around the bore: no barrel edge, no heater ring, no context.
- **CUT_X4120** (`shot-CUT_X4120.png` against `A1a-x4120-S07b-ev-r2.png`):
  - The dome walls, the screws and the pre-cut profiles are right.
  - **But** two large hatched `barrel_cover_c3` blocks frame the dome, the `c3_hw` face draws a black triangle, and a line crosses the bore.
  - With the covers hidden (`whatif-CUT_X4120-covers-hidden.png`) it matches the A1a render closely.
- **CUT_FEED** (`shot-CUT_FEED.png` against S03 and `A1a-feedcol-ext-wb.png`):
  - The hopper and throat walls are hatched and the inside of the column is visible.
  - It reads correctly as "the feed column, cut at Y = 0".
  - The top of the hopper sits under the toolbar.
- **FREE** (`shot-FREE-x3000-close.png`, `shot-FREE-y1200.png`, `shot-FREE-z0.png`):
  - Caps everywhere, correct colours per material. Hatch on steel, solid screw caps, amber fill.
  - The slider is smooth.
  - The solid covers and the solid base frame turn into large hatched areas that merge with the barrel's cap. The `_hw` line shows again in X and Y.
  - From the FULL camera, the default X = 3 000 shows no cap at all, because the cut face points away from the viewer (`shot-FREE-x3000.png`).
- **Rolls, `cap: force`** (`shot-FREE-z0-rolls.png`):
  - They read as solid hatched discs.
  - Two artefacts:
    - an off-centre grey disc: `ctx_roll_stand` at z −1.4, seen through the open end of the roll mesh;
    - the translucent `ctx_sheet` drawn over the cap. The back-face cap sits at the depth of the far wall, not on the plane.
- **Checked and not found** in any state:
  - z-fighting;
  - an exterior shown together with its hollow copy;
  - floating parts;
  - outlines on the wrong object (selecting `screws` in Z_BARREL outlines 139 meshes, `shot-ZB-select-screws.png`);
  - broken Vietnamese diacritics.

## Findings

| ID | Sev | Location | What is wrong | Evidence | Suggested fix |
|---|---|---|---|---|---|
| I1 | I | `cut_states.json`: CUT_Z_BARREL (c1–c6), CUT_X2450 (c5), CUT_X4120 (c3) | The solid cover boxes `barrel_cover_cN` and `_hw` are in `clip`. Their full-section caps and the internal `_hw` face at y = 1.154 hide or frame the barrel, draw a dark slab, band or triangle, and put a line through the screw profiles. They also make D4 flaky (X2450/screws fails about half the time, depending on the screw angle) | `shot-CUT_Z_BARREL.png`, `crop-zb-lower.png`, `shot-CUT_X2450.png`, `shot-CUT_X4120.png`; capCheck runs: 3/6 fail by 1 px of `barrel_cover_c5`; the three `whatif-*-covers-hidden.png` | **Data.** I agree with B's proposal: move `barrel_cover_cN` and `barrel_cover_cN_hw` from `clip` to `hide` in those three states (in `make_data.py` or the contract), then `make -C web all`. The what-ifs match the A1a renders |
| I2 | I | CUT_X2450 camera (ST2) | Too tight: 60 mm lens at 0.77 m. The hatched cap fills the whole frame, with no barrel outline, heater ring or surroundings. The left side of the bore is under the tree panel | `shot-CUT_X2450.png`, `whatif-CUT_X2450-covers-hidden.png` | **Data:** a wider preset, so the Ø640 flange and the Ø580 band fit inside the canvas area between the panels (for example, about twice the distance, or a 40 mm lens). Check X4120 the same way; it is acceptable now |
| I3 | I | `ui/Toolbar.tsx` / `ui/text.ts` (FREE) | Axis names mix conventions. The state buttons use Blender axes ("Y = 0" is the vertical plane along the line; "Z = 1 200" is height). The FREE buttons and readout use three.js axes, where Y is height. The same plane reads "Z = 1 200" on a state button and "Y = 1 200 mm" in FREE. A user who picks FREE Y to repeat the feed cut gets a horizontal cut. Smaller: the label says "Vị trí (m)" but the readout is in mm | `shot-FREE-y1200.png` against the toolbar labels | **Code:** show Blender names in the FREE UI (three x → X, three −z → Y, three y → Z) for the buttons, the tooltips and the readout. Keep three axes internally. Make the label unit match the readout |
| I4 | I | `App.tsx:100,144`, `index.css:24` (`<pre id="selfcheck">`) | **User request (mid-review): remove this white panel.** At `?selfcheck=1` it covers the bottom-left of the device tree | `shot-FULL.png` (bottom left) | **Code:** keep the element and its `textContent` for the tests, but hide it visually (off-screen or `display:none`). Or show it only with `?selfcheck=show` |
| M1 | M | FULL camera preset | It frames only the extruder; the die, the roll stack and the sheet are not seen. D13 compares FULL with the hero render of the whole line | `shot-FULL.png` against `out/renders/ze155-hero.png` | **Data:** a hero-like preset that fits `line_extent_m` inside the canvas area between the panels |
| M2 | M | FREE + cover and base-frame geometry | In FREE every visible part is clipped. The solid covers and the base frame turn into big hatched areas that merge with the barrel's steel cap, and the `_hw` line shows | `shot-FREE-x3000-close.png`, `shot-FREE-y1200.png`, `shot-FREE-z0.png` | **Data:** give the covers an insulation cap colour (beige) so they read apart from the barrel steel, or add them to `FREE.hide`. Later: model the covers hollow in Blender |
| M3 | M | `node_map`: `ctx_roll_*` with `cap: force` | Visual check for AMENDMENTS. They mostly read as solid rolls, with two artefacts: the far `ctx_roll_stand` shows through the open roll end as an off-centre grey disc, and the translucent sheet draws over the cap | `shot-FREE-z0-rolls.png` | **Data:** keep `force` for Đợt 1 (better than a hollow tube) and note the artefacts. Close the roll ends in the model in Đợt 2 |
| M4 | M | Entering FREE (`store.ts` / `FreeClip.ts`) | FREE keeps the current camera. From FULL the default X = 3 000 removes half the line, but the cut face points away, so no cap is visible | `shot-FREE-x3000.png` | **Code:** on entering FREE, or on an axis change, move to a view facing the kept cut face when the current view cannot see it. Or choose a default axis that faces the FULL camera |
| M5 | M | 1366 × 768 layout (`ui.css`) | The toolbar wraps to 3 rows (106 px); the panels take 640 px and leave 726 px of canvas. The subject of each cut preset sits partly behind the panels | `shot-1366-ZB-select.png` | **Code:** collapsible or narrower panels below about 1600 px, and/or offset the camera framing by the panel insets |
| M6 | M | `ui/InfoPanel.tsx` / `ui.css:54` (`.ze-link`) | In "Nối với", a long link wraps as a block, so the bullet sits next to its second line. A target that is not a device shows its raw id (`ctx_floor`) | `crop-info-bullet.png`, `shot-D3-F-zoom.png` (info panel) | **Code:** `.ze-link { display: inline }`. Show non-device targets as plain readable text |
| M7 | M | `zoomTo` (F, double-click, tree) | It keeps the view direction, as Blender does. For a device behind others the result shows only the occluder: `vac_separator` → the B5 vent dome fills the view | `shot-D3-F-zoom.png` | **Code, optional:** when the bbox centre is occluded, pick a direction from the device's open side |
| M8 | M | `test/hooks.ts` `capCheck` | The result depends on the screw angle, because the rotors keep turning during sampling | 6 repeat runs: 158–164 cap pixels, pass or fail | **Code (test):** set `rotorMode` to `off` during `capCheck`, then restore it |

Counts: 0 C, 4 I, 8 M.

## Verified OK

- Real input works:
  - canvas click, double-click and hover, all events `isTrusted`;
  - Alt+click through `clickAt`;
  - F and Escape keys;
  - tree items and toolbar buttons.
- Picking honours the cuts, including cap clicks.
- `rayUnfiltered` stays 0 throughout.
- **State queue and busy labels:** behave as designed. The interior lazy-loads only on the first cut, the single precompile pass runs inside the queue, and every state switch finishes within 2 frames.
- **Screws:** co-rotating at −90 °/s and conveying towards +X. The pre-cut X2450/X4120 plates turn with the screws.
- **Caps:** colours follow the materials. Hatch on steel, solid #99362A on the screws, amber fill, purple windows, ghost dome.
- **No duplicates:** no z-fighting and no exterior shown with its hollow copy in any fixed state.
- **Selection details:**
  - the dashed bbox and "Nằm bên trong – mở một mặt cắt để xem" for `screws` at FULL (`shot-FULL-select-screws-dashed.png`);
  - "Về góc nhìn của trạng thái" in FREE uses the preset of `prevFixed`.
- **Search** ignores accents: "xi lanh b3" → `barrel_b3`, "bom banh rang" → `melt_gear_pump`, "dong co" → 10 devices.
- **Text and layout:**
  - Vietnamese text renders correctly everywhere;
  - no horizontal page overflow at 1366 px;
  - the panels start below the wrapped toolbar.
- **Console:** the THREE.Clock warning is upstream R3F on three r186; no action needed in Đợt 1.

## Verdict

**Ready to show the user after fixes.**
- **Required:**
  - I1, a data change plus one `make -C web all`; it also settles D4;
  - I4, the user's request.
- **Strongly recommended before the user looks at the cross-sections:**
  - I2, the X2450 camera;
  - I3, the axis names.
- The M items can follow.
- Load, selection, lazy-load, rotors, round trips, network and performance all pass. Nothing in the code needs rework.
