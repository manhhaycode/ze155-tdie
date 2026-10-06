# web-check: ZE 155 line in R3F (Đợt 1)

This is the sandbox for Đợt 1 of the ZE 155 web viewer, built with Vite, React 19.3, @react-three/fiber 9.8.1, drei 10.7.9 and three 0.186.1. It loads the real exported line (`line.glb`, meshopt) and picks devices like Blender. On demand it lazy-loads the interior (`interior.glb`). It shows the fixed cut states with caps, a free X/Y/Z cut plane, and the rotating screws.

Specs: `../PLAN-DOT1.md` (§4) as amended by `../dot1/AMENDMENTS.md`.

## Run

```bash
cd web/web-check
npm install                                  # pinned versions, see package.json
npm run dev -- --port 5178 --strictPort      # http://localhost:5178/
```

- `http://localhost:5178/?selfcheck=1` renders at DPR 1 and prints `selfcheck()` into `<pre id="selfcheck">`, ending with `SELFCHECK DONE`. The element is visually hidden (it stays in the DOM and the accessibility tree for the tests); `?selfcheck=show` shows it as a panel.
- `npm run build` runs `tsc -b` and `vite build`.
- The models and data in `public/models` and `public/data` come from builder A's `make -C web all`, which runs `publish`. Do not edit them by hand.

## Use

| Action | What it does |
|---|---|
| Wheel / trackpad scroll | Dolly to the cursor. A zoom-in gesture first moves the orbit target to the depth of the surface under the cursor, so the zoom slows down on that surface instead of stalling at a far target; at 5 cm it keeps pushing forward (into a cut screw) |
| Trackpad pinch (wheel + Ctrl) | Same dolly to the cursor (not camera-controls' default FOV zoom) |
| Hover | Light blue 2 px outline on the device |
| Click | Orange 3 px outline, bounding box, and the info panel on the right |
| Alt + click | Selects one part of the device |
| Double click or F | Zooms to the selection and keeps the view direction, like Blender's View Selected |
| Esc, or click on empty space | Clears the selection |
| Toolbar | The 7 states, FREE direction / position / flip, rotor speed (off / 20× slower / real), and "Về góc nhìn của trạng thái". Each state button says what you will see ("Phễu nạp hạt", "Bên trong xi lanh" …); its tooltip adds the cut plane and zone codes (PLAN-FLOW §4.1) |
| FREE directions | "Cắt ngang" / "Bổ dọc" / "Cắt nằm" (横断 / 縦断 / 水平). The tooltip names the Blender axis: X along the flow, Y across the line ("Y = 0" = the feed-column plane), Z height ("Z = 1 200" = the barrel axis plane); the slider readout keeps "X = 3 000 mm". Unflipped, the part with the Blender coordinate ≤ the value is kept; the flip tooltip says which side. Internally the store and the hooks keep three axes: Blender X = three `x`, Blender Y = three `−z` (`data-axis="z"`), Blender Z = three `y` |
| Quy trình: hạt → film (FLOW) | The whole line cut at Y = 0, seen from the operator side: pellets fall through the feed column into the bore of screw B, melt over X 1.52–1.90 m, the melt runs through valve, screen changer, pump, pipe and T-die, then the sheet wraps the rolls and runs onto the conveyor. Free view: orbit and zoom in to see the pellets. "Màu:" switches between **Pha** (pellet / melt / PET sheet) and **Nhiệt độ** (zone set points on a 20–300 °C scale, assumed). Stripes drift at the conveying speed; rotor "Tắt" stops everything. Steel and screw sections are grey in this state so the melt colours read |
| VI / 日本語 (toolbar, right) | Switches the overlay language (Vietnamese / Japanese). Remembered in `localStorage` (`ze-lang`); `?lang=vi` or `?lang=ja` in the URL wins. Japanese device texts come from `public/i18n/devices.ja.json`, any missing field falls back to Vietnamese. In Japanese the device search also matches the Japanese names |
| ✓ / ≈ / ⚠ at the end of an info line | Opens the sources of that line (PLAN-PROV): each fact with its level (✓ public document, ≈ derived from one, ⚠ assumption with its reason) and its sources: claim quote and link, catalogue page with a thumbnail and "open PDF at page N", web photo with credit and link, or an internal document excerpt. Click a thumbnail for the large image. Esc closes the dialog first, a second Esc clears the selection. The counts under the device name sum the marks |
| ▲ next to the device count | Folds the device tree to its header (useful below 1600 px, where the panels are also narrower) |

## Code map (`src/`)

| File | Role |
|---|---|
| `data.ts` | Types and `dataPromise`: the 5 JSON files, fetched once |
| `store.ts` | zustand `useUi`, the PLAN §4.2.9 API plus `pending`, `cutVersion`, `ready` and `resetView()`. `changeState()` puts every state change on the single queue |
| `scene/rig.ts` | Registry `reg`, `rigLine` and `rigInterior`. Builds the `sec_*` / `dev_*` groups with attach, applies the payload rule, creates the rotor pivots, then calls the materials and the BVH. Guarded for StrictMode |
| `scene/materials.ts` | Overrides from `materials.json`. Closed meshes are FrontSide, open meshes get a shared DoubleSide copy, plus per-mesh cap colour |
| `scene/Picking.ts` | CENTER BVH per geometry. `filteredRaycast` lives inside `mesh.raycast`: it drops hidden meshes, ghosts and hits on the removed side. `emptyRaycast` for groups, plus the pointer handlers. No drei `<Bvh>` |
| `scene/Cuts.ts` | `setVisible` (recorded; payloads only), `clipPart` and cut variants with a back-face cap and hatch, `resetCuts`, `applyState` |
| `scene/FreeClip.ts` | One shared local `freePlane` on the clipped materials, never `renderer.clippingPlanes` |
| `scene/stateQueue.ts` | The one serial queue (AMENDMENTS I2) |
| `scene/precompile.ts` | One precompile pass after the interior loads, inside the queue, with frames paused; then it re-applies the current state |
| `scene/Selection.tsx` | drei Outlines (`screenspace={false}`, so thickness is in pixels) with hulls marked as helpers, plus `Box3Helper`, or a dashed box when nothing is visible |
| `scene/CameraRig.tsx` | CameraControls (zoom tuning in `CONTROL_TUNING`), the wheel listener (auto depth, pinch to dolly), `applyPreset` and `zoomToBox` |
| `scene/Rotors.tsx` | 8 slice-1 rotors on runtime pivots; they stand still while `frozen` |
| `scene/Flow.tsx` | FLOW layer (PLAN-FLOW): `enterFlowLayer()` after `applyState('FLOW')` swaps fill / curtain / sheet / pre-cut section materials through the recorded `setMaterial`; `leaveFlowLayer()` runs from `resetCuts`. `<Flow/>` drives the shader clocks and the pellets |
| `scene/FillMaterial.ts`, `scene/SheetMaterial.ts`, `scene/heat.ts` | Melt fill and sheet materials (clipping plane built in, never through `cutVariant`), the 20–300 °C scale and the zone temperature profile |
| `scene/Pellets.ts` | 2 000 pellets in one `InstancedMesh` (helper: no raycast), outside the line tree |
| `scene/Models.tsx` | `LineModel` and `InteriorLoader` (mounted only after the first state that needs the interior) |
| `test/hooks.ts` | `window.__ze`, see below |
| `ui/*` | Builder A's Toolbar, DeviceTree and InfoPanel |
| `ui/prov.ts`, `ui/provModel.ts`, `ui/Provenance.tsx` | Source badges: lazy loader of `/data/prov/<device_id>.json` (on the first selection of a device, never at start), the pure model (`lineFor` returns nothing when the line text changed, so a stale file shows no mark rather than a wrong one), badges, counts and the `<dialog>`. The files come from `make -C web prov publish-prov` (`../tools/make_prov.py`, hand-sourced lines in `../prov/lines/`) |
| `ui/i18n.ts`, `ui/text.ts` | Language store `useLang`, `useLoc()` accessors (names, texts, sections, state labels, sort order); `T` (vi) and `T_JA` UI strings |
| `public/brand/toyobo-official.svg` | Customer logo shown at the left of the toolbar |

**Hot reload.** Any change under `src/` other than `src/ui/**` and CSS forces a full page reload, through a plugin in `vite.config.ts`. A fresh registry is therefore never left next to cached scenes (review M3).

## Test hooks (`window.__ze`)

Always start with `await __ze.ready`.

| Hook | Use |
|---|---|
| `selfcheck()` | devices, parts, unknown/missing nodes, orphans, `rayUnfiltered`, rotors |
| `stats()` | fps over 3 s, draw calls, triangles, heap, load times |
| `devices()`, `select(id, part?)`, `selectAll()`, `selection()`, `clear()` | Selection |
| `clickAt(x, y, {alt, dbl})` | Dispatches real pointer events on the canvas |
| `pickAt(x, y)` | Same filters as the clicks |
| `project(id)` | Screen position of a device |
| `setState(id, {camera, smooth})`, `setFreeClip(axis, offset, flip)`, `timeState(id)`, `cutRoundTrip()` | Cut states |
| `capCheck(state, device, {axis, offset})` | D4 cap check (rotors off and frozen while it samples) |
| `freeze(on)` | Stops rotors, pellets and FLOW stripes (screenshots, pixel samples) |
| `flowProbe()`, `pelletTest(s)`, `fillColorAt(x, mode)`, `fillProbe()`, `sheetProbe(s)` | FLOW checks F4–F6 (PLAN-FLOW §6) |
| `freeCamTest()`, `rollCoreProbe()` | Fix round 2 (PLAN-FLOW-M1-M3): the FREE camera faces the section after entry, axis change and flip (end pose, 26 cases); roll sections show only cap colour (dense pixel scan of 5 views), the marker stays visible, a click at a roll section picks the roll |
| `rotors()`, `rotorTest(s)` | Rotors |
| `camera(id)`, `cam()`, `orbitTest()` | Camera |
| `provCheck()` | Source badges of the info panel (PLAN-PROV): no `/data/prov/` request at `ready`, 1 request on the first selection of a device and none on the next, one badge per function/details line, no "?" line left, no request for a synthetic device, thumbnails only once a dialog opens and the large image only on a click, Esc inside the dialog never clears the selection, focus returns to the badge, Japanese labels. Needs a fresh page (it picks a device whose file was not requested yet). About 2 s |
| `selftest()` | Runs the in-page part of D1–D9, D14, FLOW F2–F6, F8 and `provCheck()` (P1). Takes about 70 s |

The latest self-test results are in `SELFTEST.json`. Screenshots: `selftest/` (builder B, before the review fixes) and `../review/dot1/fix-01/` (after fixer round 1).

## Known points

- **Password gate.** `src/ui/PasswordGate.tsx` asks for a password before the viewer loads; the 3D code is a separate chunk (`src/AppLazy.tsx`) fetched only after it opens, so no GLB is requested before. The source holds only a salted SHA-256, never the password (ask the owner). Unlocking lasts only until the page is reloaded, and any previous `localStorage` unlock key is removed. It keeps casual visitors out only: a static site cannot check a password, the models stay reachable by direct URL, and the check can be bypassed in the browser. Real protection needs a server-side check (e.g. Vercel middleware or Vercel's password protection).
- **Barrel covers.** `barrel_cover_c1..c6` are solid closed boxes with an internal panel-joint face. Their caps hid the barrel and the joint face crossed the screw bore (the old D4 X2450/screws failure). `tools/make_data.py` now hides them in CUT_Z_BARREL, CUT_X2450, CUT_X4120 and FREE (tables `CLIP_TO_HIDE`, `EXTRA_HIDE`, `FREE_EXTRA_HIDE`), as in the A1a look renders. D4 passes 6/6.
- **Camera presets.** CUT_FEED is pulled back (review-flow-01 M2) so the hopper sits below the toolbar at 1366 px. FULL is a hero-like view of the whole line from the die end (camera on the +X side, so the FREE default cut X = 3 000 faces it). CUT_X2450 and CUT_X4120 are wider than shots.json ST2 / ST3. All three come from `CAMERA_OVERRIDES` in `tools/make_data.py`; `anim/shots.json` is unchanged.
- **The peel animation is deferred** to Đợt 1b. So are `pickSweep` and the performance trace (AMENDMENTS).
- **Cap depth bias.** Cap fragments write a depth 0.6 mm towards the camera. This stops them z-fighting with abutting solids, such as stacked screw elements or barrel flanges cut by FREE. A cap is drawn by the back faces of the far inner wall, so an uncut solid inside a cut part's volume hides the cap (the reason cover C6 is hidden in CUT_X2450). Exception: nodes with a `section` in `node_map` (the 3 chill rolls) draw their cap at the cut plane where the plane point is inside the profile: 1 mm into the kept side (the roll markers lie up to 0.7 mm behind the plane when FREE is flipped) plus 8 depth steps (about 2.4·10⁻⁵·d² m: 15 mm at 25 m, 86 mm at 60 m); picking reports such hits at the same point. Constraint: nothing else may lie inside such a profile closer to the plane than that (the roll stand's face inside the journal leaves a 1 px line when a FREE X cut runs through the roll axes).
- **Console.** R3F 9.8.1 on three r186 logs one library warning: "THREE.Clock … deprecated".
- **FLOW.** Screw B (axis 71 mm behind the cut, flight radius 83 mm) is clipped in FLOW: whole, it poked 12 mm through the plane and filled the bore opening in front of the melt. The melt section of the screw zones is drawn at the cut plane (fill back faces get the plane's depth inside the bore waist, below the zone's melt level), so the screw shows through the translucent melt; the conveying and vent zones are a bed at the bottom of the bore, as modelled. The fill materials render in one pass (`forceSinglePass`), otherwise three's back pass flips `gl_FrontFacing`. Temperatures are zone set points (assumed), the pellets are drawn ×3.
