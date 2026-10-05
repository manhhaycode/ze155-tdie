# Review 01: PLAN-R3F.md, model-contract.json, r3f-snippets.md, ADDENDUM-discussion.md

Independent reviewer, 2026-10-05. Scope: the technical claims, internal consistency, whether W1/W2 is feasible and safe in the open session, how well the plan fits the user's requirements, and decisions Q1–Q5. The addendum is reviewed in its own section at the end.

**How I checked:**
- **Library sources:** read the published npm tarballs, unpacked in the session scratchpad (nothing installed in any project). Packages: @react-three/fiber 9.8.1, @react-three/drei 10.7.9 (and 9.122.0 for comparison), three 0.186.1, three-stdlib 2.36.1, three-mesh-bvh 0.8.3, @gltf-transform/cli, functions and extensions 4.5.1, camera-controls 3.1.2.
- **Blender exporter:** read the io_scene_gltf2 5.2.40 source on disk at `/Applications/Blender.app/.../addons_core/io_scene_gltf2`.
- **Blender MCP limit:** read the MCP server source at `~/.cache/uv/.../blender_mcp/server.py`.
- **Contract:** spot-checked with Python against `design/parts.json`, `anim/tmp/c0_bboxes.json`, `anim/tmp/ze155_fingerprint.json`, `anim/shots.json` and `anim/log.md`.
- **Live Blender:** not touched. Every name and number came from files.

Severity: **C** = would break a requirement or mislead builders into a broken design. **I** = would cause visible defects or rework, or a safety gap. **M** = small inconsistency or risk.

## Findings

- **C1**
  - **Where:** PLAN §3.5 step 5 and §6 risk 1; snippets §1 and §3 (`eventManager.filter`, `Bvh firstHitOnly={false}`).
  - **Problem:** You cannot pick the visible half, or the cap, of a clipped mesh. R3F removes duplicate hits per object *before* it calls `events.filter`. Only the nearest hit on each mesh survives. When that hit is on the removed side, the filter drops it, and the valid hit further back on the same mesh is already gone. So `firstHitOnly={false}` does not do what the plan says. In CUT_Z_BARREL or the free plane, clicking the red cut face or the bore floor of a cut barrel selects the frame behind it, or nothing. A5 does not catch this, because it only tests clicks on the removed region.
  - **Evidence:**
    - `fiber/dist/events-9ce18a08.esm.js:539-541`: `makeId = (eventObject||object).uuid + '/' + index + instanceId`. For meshes, `index` and `instanceId` are undefined, so every hit on a mesh gets the same id.
    - Lines 664-676 remove the duplicates, and line 679 runs the filter afterwards.
  - **Fix:**
    - Filter at the source. After Bvh has patched the meshes, wrap each `mesh.raycast` so that it skips clipped hits (local and global planes), ghosted meshes and invisible ancestors before it pushes hits.
    - Give empty Object3D nodes a `raycast` that returns `false` when they are hidden. three r186 then prunes the whole subtree (`Raycaster.js:246-248`).
    - Keep cut variants `DoubleSide`, so cap back faces are hit.
    - drei `Bvh` skips meshes whose geometry already has a `boundsTree` (`core/Bvh.js:69`), so 54 of the 64 shared screw meshes keep brute-force raycasting. Assign `acceleratedRaycast` to those meshes too.
    - Add an acceptance check: "clicking a cap or the visible inside of a clipped device selects that device".

- **I1**
  - **Where:** snippets §4 `<Outlines screenspace thickness={px}>`.
  - **Problem:** In drei 10.7.9 (and 9.122), `screenspace: true` runs the object-space branch: the vertex moves by `thickness` local units. Pixel thickness is the `false` branch. With `thickness` 2 to 3, and with quantized meshes, where one local unit is about half the mesh extent, every hover or selection outline becomes a huge hull. The snippet header says `Outlines (screenspace)` was checked.
  - **Evidence:** `drei/core/Outlines.js:41-47`. The `if (screenspace)` branch computes `tPosition.xyz + tNormal.xyz * thickness`, and the `else` branch computes `thickness / size * clipPosition.w * 2.0`.
  - **Fix:**
    - Use `screenspace={false}` with a thickness in pixels, and confirm it in the sandbox.
    - Set `raycast = () => {}` on the outline meshes. They sit inside `gltf.scene`, so they are raycast, and the creased-normal copies have no BVH.

- **I2**
  - **Where:** snippets §6 `applyCutState` (`if (plane && !o.userData.cut_only) clipObject(...)`); contract `CUT_Z_BARREL.show_interior` ("dev_screws (all)").
  - **Problem:** In the barrel half-lift, every interior item that is not `cut_only` is clipped, including the screws. The screws would be sliced lengthwise at their own axis height (y = 1.2), with rotating caps. The design shows whole screws lying in the opened trough, which is the key teaching image for S04 and ST1.
  - **Evidence:** In `shots.json` `meta.states.CUT_Z_BARREL.show`, the screws are `int_screw_*` (whole) and only the fills use `int_fill_*_lo`. A1a built no `_lo` screws.
  - **Fix:** Split `show_interior` per state into `show_whole` and `show_clipped`:
    - screws and spline shafts whole in CUT_Z_BARREL and ST1;
    - screws clipped in CUT_X2450 and CUT_X4120;
    - fills clipped everywhere.

- **I3**
  - **Where:** contract `swap_map` and `cut_states.*.swap_then_clip`; snippets §6 (swap driven only by `part.userData.swap_to`).
  - **Problem:** One global `swap_to` per part cannot express swaps that differ per state. Some swaps exist only as free text, so exterior and interior copies end up drawn on top of each other:
    - **CUT_DIE_PLAN and ST1:** they keep `p_die_body_lower` whole (it is in `keep_whole`, and it is not in `swap_map`) and also show `p_int_die_lower_face`, which has exactly the same bbox. Result: z-fighting at the parting plane, and the coat-hanger manifold stays hidden.
    - **CUT_DIE_AA:** clips the exterior die bodies and also shows the pre-cut `p_int_die_section_*` in the same place.
    - **CUT_PUMP:** swaps `p_melt_gear_pump` to `p_int_pump_body_hollow` and also shows `p_int_pump_body_cut`.
    - **Pipe and mixer:** the targets `p_int_pipe_mixer_section*` and `p_melt_pipe(?)` resolve to nothing. The code then neither hides nor clips the exterior.
  - **Evidence:** contract `cut_states.CUT_DIE_PLAN.keep_whole` and `swap_then_clip`, `CUT_DIE_AA`, `CUT_PUMP.show_interior`, `swap_map`. A1b log: "die lower face = host bboxes exactly".
  - **Fix:**
    - Give each state an explicit `swap: {ext_node: int_node}` map.
    - The code hides `ext_node` whenever its replacement is shown.
    - Drop the global `swap_to`, or use it only for FREE.

- **I4**
  - **Where:** contract `interior_export`, `host_map`, `rotors[].from`, the `GHOST_DRIVE` note; PLAN §2 "ze155_anim 523 objects".
  - **Problem:** The A1b mapping was written while A1b was still running. Several items are stale or contradict each other:
    - **Pipe and mixer:** they exist only as the layered halves `int_pipe_mixer_section_lo` and `_y0`, plus `int_pipe_mixer_elements` (whole), and there is no full section. The `*_lo` and `*_y0` excludes drop the halves, so the pipe has no interior at all.
    - **Die `_y0` parts:** they are excluded, yet `host_map` and CUT_DIE_AA still list them.
    - **Pump gears:** `int_pump_gear_top` and `int_pump_gear_bottom` are the Y-cut halves, with `_full` children. "(_full)" is ambiguous, and exporting both gives coplanar caps.
    - **Gearbox schematic:** `int_gbx_schematic_*` and `anim_ghost_drive_gbx` *were* built, but the contract says "never built" and the include list omits them. The `_out_a` and `_out_b` gears are children of the screw axes.
    - **Object count:** the scene now holds 618 objects (343 + 275), not 523.
  - **Evidence:** `anim/log.md` A1b, under "Built" and the DESIGN-DEVIATION lines (pipe layers, gear halves, gbx schematic); contract `interior_export.exclude` and `host_map`.
  - **Fix:**
    - Rebuild `interior_export` from the final A1b log, with one explicit choice per item: full, cut_only for named states, or omit.
    - Export only the `_full` gears under `rot_pump_gear_*` and drop the halves, or the reverse.
    - Decide whether GHOST_DRIVE includes the gearbox schematic. If it does, add its rotors.

- **I5**
  - **Where:** PLAN Q2 and §3.5; contract `interior_export.why_exclude`.
  - **Problem:**
    - Q2 frames the choice as "runtime" against "bake 8 new states (+150 k tris, +2 h)". But A1a and A1b already built the pre-cut variants. Dropping them saves about 54 k triangles in a file that is loaded lazily anyway, and it goes against DECISIONS 29, which keeps those variants.
    - Runtime back-face caps cannot reproduce what some variants show:
      - the layered pipe cap (steel, copper heater, beige insulation, cladding);
      - the screw cross-section ring plus the Ø72 shaft disc at X 2450 and 4120 (runtime gives a hole where the shaft is);
      - the clean fill end face.
    - For the X sections, runtime clipping of rotating screws does work (the profile stays correct while they turn), and FREE has to be runtime anyway.
  - **Evidence:** DECISIONS 29 ("Giữ … bản cắt sẵn"); A1a log (xsec caps, fill X variants); A1b log (pipe layers, die sections).
  - **Fix:**
    - Recommend a hybrid in Q2: runtime clipping for FREE and for parts with a closed full source, and the existing variants kept as `cut_only` in the fixed states where they are the only or the better source (pipe, die A-A, pump body, optionally the X-section screw caps).
    - Present the real cost of the alternative: about 0 h and about 54 k lazily loaded triangles.

- **I6**
  - **Where:** PLAN W1.4 (`closed` = 0 non-manifold edges), §3.5 step 3, §6.
  - **Problem:**
    - The criterion is too strict. Touching shells, where four faces meet at an edge, make a solid "open", so it gets no cap.
    - It also does not check winding. With FrontSide on "closed" parts, flipped faces disappear in FULL, and in cut states they show cap colour from outside.
  - **Evidence:** A1a log: `int_feed_column_hollow` has "57 four-face edges where small parts touch". By the plan's rule, CUT_FEED (S03) would show no cap.
  - **Fix:**
    - Set `closed` = no boundary (one-face) edges, and every two-face edge `is_contiguous`. Four-face edges are fine for back-face caps.
    - Log the result per part, and list any clipped part per state that comes out open.

- **I7**
  - **Where:** contract `CUT_DIE_PLAN` (`hide`, `clip`, `clips_on_enter: die_open`); `clips.die_open.targets`.
  - **Problem:** The state fights its own clip:
    - It hides `p_die_body_upper` (plus the rail, choker bolts, lugs and thermal bolts) at once, while `die_open` lifts those same devices. The lift therefore plays on hidden objects.
    - The flex lip, plugs, cable harness and air hose are clipped at the fixed plane y ≤ 1.2 and are also lifted by +0.9 m with their device nodes, so they drop out of view.
    - S11 is meant to show the upper half and the choker bar *lifting off*.
  - **Evidence:** `shots.json` CUT_DIE_PLAN ("int_die_choker_bar (peels with the upper half)"); `die_open.targets` includes `dev_die_body_upper`, `dev_die_flex_lip`, `dev_util_air_hose_die` and `dev_die_cable_harness`.
  - **Fix:**
    - In CUT_DIE_PLAN, do not hide or clip any `die_open` target.
    - Play `die_open` with the targets visible, then hide them after the clip or keep them lifted.
    - Clip only the lower-half group.

- **I8**
  - **Where:** PLAN W1.4 (split `melt_heater_bands`, `die_body_bolts`, `die_heater_boxes` on `obj.copy()` copies), W2.1, Q1.
  - **Problem:** Two steps can write to mesh data that `ze155` shares:
    - Splitting a copy that shares its mesh (with `separate` or bmesh on `obj.data`) edits the `ze155` mesh, and the plan does not say to make new data first.
    - The exporter calls `Mesh.validate()` on every mesh object's *original* data. That call corrects (rewrites) any invalid geometry.
  - **Evidence:**
    - `io_scene_gltf2/blender/exp/nodes.py:288`: `res = blender_object.data.validate()`.
    - W1.4 says "obj.copy() (dùng chung mesh, giữ modifier)".
    - The ze155 fingerprint stores no vertex counts.
  - **Fix:**
    - Build split parts from `bpy.data.meshes.new_from_object(evaluated)`, with no modifiers.
    - Consider `obj.data = obj.data.copy()` for every exterior copy. Copies with modifiers export through `to_mesh` anyway, so sharing brings no glTF benefit. Keep shared data only for the screw meshes.
    - Never put custom properties on `obj.data`.
    - Add vertex and polygon counts per mesh to the before/after fingerprint around W2.1.

- **I9**
  - **Where:** PLAN W2.1 code block ("Mỗi lần xuất < 2 phút", both exports in one call).
  - **Problem:**
    - The MCP socket times out at 180 s. The single call does three things: the first evaluation of `ze155_web` (347 copies with Bevel, WN and Boolean modifiers), a 1.19 M-triangle export, and the interior export. That can exceed the limit.
    - On a timeout the server drops the socket while Blender keeps exporting with its UI blocked. The agent cannot tell whether the export succeeded and may run it again.
    - There is no `try/finally`, so an exception leaves the window on `ze155_web`.
  - **Evidence:** `blender_mcp/server.py:147,230` (`settimeout(180.0)`) and 244-247 (`self.sock = None` on timeout).
  - **Fix:**
    - Split W2.1 into separate calls:
      1. switch the scene and warm the depsgraph (`evaluated_depsgraph_get()`), timed;
      2. export `line.glb`;
      3. export `interior.glb`;
      4. restore the scene and run the checks.
    - Wrap each call in `try/finally` and write a small done-marker JSON with timings. Verify the file on disk rather than trusting the reply.

- **I10**
  - **Where:** PLAN Q1, §6 "Phiên Blender đang mở"; Addendum item 8 ("the user must not press Ctrl+S").
  - **Problem:**
    - Q1 recommends the first-ever GLB export of this model inside the live session, which holds the user's unsaved changes. It does not mention crash risk.
    - On 2026-10-03, Blender 5.2.2 crashed with SIGSEGV on a GLB export. The root cause found then was `use_active_scene=False`, which the plan avoids, but the exporter still switches `window.scene` itself.
    - A crash would lose the user's unsaved work. No mitigation is listed.
  - **Evidence:**
    - `exp/tree.py:140` and `exp/gather.py:53` set `bpy.context.window.scene`.
    - Project memory: the Blender 5.2.2 crash note.
    - DECISIONS 27/28: there are unsaved changes, and the user asked to keep them.
  - **Fix:**
    - State the residual crash risk in Q1.
    - Before W1, with the user's OK, write a full session backup with `bpy.ops.wm.save_as_mainfile(filepath='out/ze155_session_backup.blend', copy=True)`. This does not change the open file's path or its dirty flag. Alternatively, the user saves a copy.
    - Then export.

- **M1**
  - **Where:** PLAN §3.2 and contract `naming.patterns.three_child_meshes` ("child Mesh objects p_*_1, p_*_2").
  - **Problem:** GLTFLoader names child meshes after the glTF *mesh* (the Blender mesh-data name, made unique), not after the node. The snippet code walks up the tree, so it still works. But `check_glb.py` and `selfcheck` must not expect `p_*_N`, and `byName` will also contain the mesh-data names.
  - **Evidence:** `three/examples/jsm/loaders/GLTFLoader.js:3960` (`mesh.name = parser.createUniqueName(meshDef.name ...)`); the same is true in three-stdlib, line 2140.
  - **Fix:** Correct the text. Register only nodes that have `userData.kind`.

- **M2**
  - **Where:** contract `hierarchy` vs PLAN §3.2, and contract `devices`.
  - **Problem:** Small inconsistencies:
    - the contract says "dev_<id> (190)", while PLAN gives 188 in line.glb plus 1 in interior.glb;
    - `devices[].parts` lists the unsplit `p_die_body_bolts`, `p_die_heater_boxes` and `p_melt_heater_bands`, while `split_objects` names `__top`/`__bottom` parts and 6 bands;
    - `dev_screws` has `bbox_m: null`, but A2 requires `bbox_m[6]`;
    - its note "attach under sec_barrel at load" contradicts "no re-parenting";
    - it has translation 0, which breaks the device-node rule.
  - **Evidence:** script check. All other device `parts` lists match `object_to_device`.
  - **Fix:** Align the counts and part lists. Give `dev_screws` a real bbox, and allow its zero translation as a documented exception.

- **M3**
  - **Where:** contract `files.cut_states.json` ("normalized by B2"); PLAN W1.1 and W2.3.
  - **Problem:**
    - No W step produces `cut_states.json`, even though the state lists contain free text ("dev_screws (all)", "p_int_fill_valve_*", "p_melt_pipe(?)", "if A1b exported them"). The snippet silently skips names it cannot resolve.
    - Valve RUN and DRAIN fill sets (`int_fill_valve_run_*` vs `_drain_*`) are not toggled with `valve_run`.
    - The `shots.json` state `FLOWS` (S14/S15) has no cut state.
  - **Evidence:** contract `cut_states`; A1b log "DRAIN fills / RUN fills"; `shots.json` states.
  - **Fix:**
    - Add a B2 step that writes `cut_states.json` with real node names only, and fail it if any name does not resolve.
    - Model the valve fill switch.
    - Map `FLOWS` to FULL in `tour.json`.

- **M4**
  - **Where:** A5 "chuyển trạng thái ≤ 200 ms"; A11 "DPR 1"; snippets §1 `dpr={[1, 2]}`.
  - **Problem:**
    - The first time each state is entered, new cap programs compile (one per material type and flag set), which can exceed 200 ms.
    - The canvas uses DPR 2 on this Retina Mac, while the budget is defined at DPR 1.
  - **Fix:**
    - Precompile on interior load (`gl.compileAsync(scene, camera)` with the variants in place), or measure on the second entry.
    - Force `dpr={1}` under `?selfcheck`, or emulate DPR 1.

- **M5**
  - **Where:** A11, "giảm CPU 4× vẫn ≥ 30 fps ở FULL".
  - **Problem:** This target is borderline with about 930–1 000 individual draw calls (roughly 5–10 ms of renderer CPU per frame unthrottled). The other fps and size budgets look realistic: about 12 MB for line.glb under meshopt high, and at least 55 fps on an M3 Pro.
  - **Fix:** Measure early on the stand-in GLB. Keep `join({filter})` per device ready as a fallback, or relax this one target.

- **M6**
  - **Where:** contract `GHOST_SC` and `FREE`.
  - **Problem:**
    - GHOST_SC ghosts the exterior `p_melt_screen_changer`, and the A1b disc pokes 67–190 mm through that hood. The raised hood exists only on `anim_ghost_sc`.
    - FREE ("interior: all") would also show ghosts and vent windows on top of the domes.
  - **Evidence:** A1b DESIGN-DEVIATION (`anim_ghost_sc` hood raised).
  - **Fix:**
    - In GHOST_SC, show `p_anim_ghost_sc` and hide the exterior.
    - In FREE, exclude the `ghost` and `marker` kinds.

- **M7**
  - **Where:** PLAN §4 preconditions ("không đổi unit settings khi đang ở ze155").
  - **Problem:** The C0 incident shows that setting `unit_settings` resets the *context* scene. Creating `ze155_web` while `ze155_anim` is the window scene would therefore corrupt `ze155_anim`.
  - **Fix:** Never touch `unit_settings` on `ze155_web` (the exporter does not need it). Also guard the fingerprint of `ze155_anim` scene settings.

## Verified OK

- **Version numbers:** all match `npm view` today:
  - react and react-dom 19.3.0; R3F 9.8.1, whose peer range is react `>=19 <19.4`;
  - drei 10.7.9, which pulls three-stdlib 2.36.1, three-mesh-bvh ^0.8.3 and camera-controls ^3.1;
  - three 0.186.1, @types/three 0.186.0, zustand 5.0.15;
  - vite 8.3.2, @vitejs/plugin-react 6.1.1 (vite ^8), create-vite 9.2.1, TypeScript 7.0.2;
  - gltf-transform 4.5.1, gltfjsx 6.5.3, postprocessing 6.39.5, @react-three/postprocessing 3.1.3.
- **Meshopt chain:**
  - three-stdlib 2.36.1 GLTFLoader reads EXT_meshopt_compression and KHR_mesh_quantization, but not KHR_meshopt_compression. three r186 reads both meshopt extensions.
  - gltf-transform 4.5.1 `meshopt` writes **EXT** (`functions/dist/index.js:4407`), so the chain works with `useGLTF`.
  - The meshopt decoder is inline (no CDN), and Draco loads only when `useDraco` is true.
- **gltf-transform quantize:** it rewrites the TRS of mesh nodes. It moves the mesh to a new unnamed child if the node has children or animated TRS (`index.js:3960-3986`). The rule "mesh = static leaf, motion on empties" is therefore right. The CLI options `dedup --materials`, `prune --keep-leaves` and `--keep-attributes`, and the global `--vertex-layout` all exist.
- **three-mesh-bvh 0.8.3** handles normalized (quantized) positions (`computeBoundsUtils.js`).
- **Raycasting:** three r186 Raycaster has no visibility check. R3F 9.8.1 has no visibility filter, and it does have `events.filter`.
- **drei Bounds** needs `controls.target` and `update()`, so using `fitToBox` with CameraControls is right. **drei Outlines** passes `clippingPlanes` through.
- **Snippet caveats:** `Material.copy` does not copy `onBeforeCompile`, as the snippet's fill caveat says. `linearToOutputTexel` and the `gl_FragColor` define exist in r186.
- **Blender 5.2.40 exporter:**
  - It uses the context depsgraph and sets and restores `window.scene` itself, so the window scene must be `ze155_web`.
  - Collection export keeps only the active scene, and `at_collection_center` is False by default.
  - Objects without modifiers reuse the original data, so the shared screw meshes become a single glTF mesh (`nodes.py:298`).
  - NLA_TRACKS merges tracks of the same name across objects.
  - Only shape-key drivers are exported, and curves go through `to_mesh`.
  - Every property name in the W2.1 call exists.
- **Contract data:**
  - All 343 render objects are mapped (340 plus 3 excluded) and match `c0_bboxes.json`.
  - The 189 devices are 186 `parts.json` ids (all except `ctx_floor`) plus 3 synthetic devices.
  - Device bboxes match the union of their object bboxes within 0.05 mm.
  - Every exterior name in the clip, hide and keep_whole lists exists.
  - 337 of 343 origins sit at world zero (the 6 exceptions are logos). The modifier counts match the fingerprint.
- **Rotors:**
  - The pivots of the rolls, motor shaft and couplings match the bbox centres.
  - The axes and signs agree with the A1a/A1b driver notes:
    - screws at −300 rpm about +X, so right-hand flights travel +X;
    - pump gears top +, bottom −;
    - rolls +/−/+ about three `[0,0,−1]`, which is Blender +Y.
  - The `valve_run` from/to positions match A1b (DRAIN `location[1]` −0.2 → three z +0.2).
- **MCP patterns:** switching `window.scene` and saving with `libraries.write` are proven in C0 and A1 (`anim_helpers.py:746,910`; the save lines in log.md).
- **Acceptance criteria:** A1–A12 can be tested with the chrome-devtools MCP and `window.__ze`, apart from the gaps noted in C1 and M4.

## Addendum (ADDENDUM-discussion.md)

- **AD1 (I)**
  - **Where:** items 4–5, Đợt 1–3, and stream A; checked against the contract and PLAN.
  - **Problem:** The slice scope conflicts with the contract and the plan:
    1. **Đợt 1 CUT_Z_BARREL needs A1b parts:** its swap targets and interior items include `p_int_head_hollow`, `p_int_valve_body`/`_bolt`, the head and valve fills, and `p_int_melt_adapters_hollow_sc_in`. With the snippet's logic, a missing swap target leaves the exterior head and valve neither hidden nor clipped.
    2. **Gearbox schematic pivots (Đợt 2):** the contract has no rotors for them and says the schematic was never built.
    3. **Peel and backflush as NLA clips:**
       - "barrel-shell peel" cannot be a glTF clip, because PLAN §3.8 says the removed half exists only at runtime;
       - a backflush clip would be a fourth animation, while A9 and W2.1 expect exactly 3.
    4. **Đợt 3 control-loop diagram:** it contradicts Q4's recommendation (S15 control loop in v2).
    5. **Rolls in Đợt 2:** they move to Đợt 2 while W1.5 builds them with the drive pivots in the exterior pass, so line.glb is exported twice. That is acceptable, but W1 must be re-runnable.
  - **Fix:**
    - Add a per-slice subset of `cut_states.json`, or a rule: "if the swap target is missing, clip the exterior".
    - Update the contract for the gearbox rotors, or drop them.
    - Keep peel at runtime, and add a backflush clip only by amending the contract and A9.
    - Settle Đợt 3 against Q4.

- **AD2 (M)**
  - **Where:** item 6.A.1, the stand-in GLB.
  - **Problem:**
    - A raw export of the current exterior has none of the contract names or userData (`dev_*`, `p_*`, `kind`, `device_id`, `closed`, `swap_to`). Stream B would therefore build picking, cuts and rotors against a different structure, and then rework them.
    - The stand-in is also a 1.25 M-triangle export in the live session, so it carries the same crash and 180 s risks as W2.1 (I9, I10).
  - **Fix:** Either of these:
    - Let B work against a small synthetic contract-shaped GLB made with a gltf-transform script (PLAN §4 already did this to test the pipeline), and use the raw export only for load, fps and material checks.
    - Or make the "stand-in" the real output of W1.2–W1.4 plus W2 (device tree and part copies, without pivots or interior), which is the cheap part of W1.

- **AD3 (M)**
  - **Where:** item 4, preview drivers.
  - **Problem:** The idea is feasible. The exporter exports only shape-key drivers (`exp/animation/drivers.py`), so object drivers are not baked in NLA_TRACKS mode. But:
    - drivers make the export-frame rotation the GLB rest pose, while W1.5 expects rotation 0;
    - they keep evaluating during NLA sampling;
    - Python-expression drivers need auto-run enabled.
  - **Fix:**
    - Use simple expressions only (`frame`-based), on the `ze155_web` empties only.
    - Mute them, or export at a frame where they evaluate to 0, during W2.1.
    - Never add drivers to `ze155_anim` objects.

- **AD4 (M)**
  - **Where:** items 5, 6 and 9 (estimate about 5 h).
  - **Problem:**
    - Item 5 says each slice runs end to end before the next one starts. Item 6 has stream D reviewing while A builds the next slice. The two cannot both hold, and the 5 h figure depends on the overlap.
    - The critical path is the serial Blender stream (Đợt 1 W1/W2 is most of B1; Đợt 2 adds the A1b mapping, clips and fills) plus the final slice's review and fix, which cannot overlap with anything.
    - The A1a/A1b builders were fast (about 40–50 min each, from the log headers), so 5 h is possible only with no rework. A realistic plan is 6–7 h. "Đợt 1 in about 2 h" is reachable only if B starts at t0 and the review is not counted.
  - **Fix:** State that review overlaps with the next slice's build (keep item 6, reword item 5). Plan 6–7 h, with the 5 h figure as the best case.

## Verdict

**Revise, then build. No rewrite needed.** The architecture is sound and should be kept:
- two GLBs, with the interior loaded lazily;
- the `parts.json` device tree with userData;
- meshopt EXT with quantize, plus the "mesh is a static leaf" rule;
- runtime clipping for the free plane;
- CameraControls with `tour.json`.

The version numbers and most exporter claims hold.

**Before builders start:**
- fix the picking design (C1) and the Outlines snippet (I1);
- rework the cut-state data model and its A1b mapping (I2–I4, I7), in particular per-state swap and whole/clipped lists, so that the fixed teaching states read correctly;
- reframe Q2 as a hybrid that keeps the existing pre-cut variants where they are the better source (I5);
- add the W1/W2 safety steps (I8–I10): own mesh data for split parts, exports split into separate MCP calls, and a session backup with the crash risk stated in Q1.

Q3–Q5 are the right questions, with sound recommendations.
