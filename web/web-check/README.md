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
| Toolbar | The 6 states, FREE axis / position / flip, rotor speed (off / 20× slower / real), and "Về góc nhìn của trạng thái" |
| FREE axes | Blender names, like the state buttons: X along the flow, Y across the line ("Y = 0" = the feed-column plane), Z height ("Z = 1 200" = the barrel axis plane). Unflipped, the part with the Blender coordinate ≤ the value is kept; the flip tooltip says which side. Internally the store and the hooks keep three axes: Blender X = three `x`, Blender Y = three `−z` (`data-axis="z"`), Blender Z = three `y` |
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
| `scene/Rotors.tsx` | 8 slice-1 rotors on runtime pivots |
| `scene/Models.tsx` | `LineModel` and `InteriorLoader` (mounted only after the first state that needs the interior) |
| `test/hooks.ts` | `window.__ze`, see below |
| `ui/*` | Builder A's Toolbar, DeviceTree and InfoPanel |

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
| `capCheck(state, device, {axis, offset})` | D4 cap check |
| `rotors()`, `rotorTest(s)` | Rotors |
| `camera(id)`, `cam()`, `orbitTest()` | Camera |
| `selftest()` | Runs the in-page part of D1–D9 and D14. Takes about 30 s |

The latest self-test results are in `SELFTEST.json`. Screenshots: `selftest/` (builder B, before the review fixes) and `../review/dot1/fix-01/` (after fixer round 1).

## Known points

- **Barrel covers.** `barrel_cover_c1..c6` are solid closed boxes with an internal panel-joint face. Their caps hid the barrel and the joint face crossed the screw bore (the old D4 X2450/screws failure). `tools/make_data.py` now hides them in CUT_Z_BARREL, CUT_X2450, CUT_X4120 and FREE (tables `CLIP_TO_HIDE`, `EXTRA_HIDE`, `FREE_EXTRA_HIDE`), as in the A1a look renders. D4 passes 6/6.
- **Camera presets.** FULL is a hero-like view of the whole line from the die end (camera on the +X side, so the FREE default cut X = 3 000 faces it). CUT_X2450 and CUT_X4120 are wider than shots.json ST2 / ST3. All three come from `CAMERA_OVERRIDES` in `tools/make_data.py`; `anim/shots.json` is unchanged.
- **The peel animation is deferred** to Đợt 1b. So are `pickSweep` and the performance trace (AMENDMENTS).
- **Cap depth bias.** Cap fragments write a depth 0.6 mm towards the camera. This stops them z-fighting with abutting solids, such as stacked screw elements or barrel flanges cut by FREE. A cap is drawn by the back faces of the far inner wall, so an uncut solid inside a cut part's volume hides the cap (the reason cover C6 is hidden in CUT_X2450).
- **Console.** R3F 9.8.1 on three r186 logs one library warning: "THREE.Clock … deprecated".
