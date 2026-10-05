# Review: PLAN-DOT1.md and web/dot1/ (option C, Đợt 1)

Independent reviewer, 2026-10-05. This was a quick review, as the user asked: I only looked for things that would break the build or mislead the builders.

**How I checked:**
- **Read:** `PLAN-DOT1.md`, `dot1/export_glb.py`, `selection-rules.json`, and the drafts `cut_states.dot1.json`, `node_map.dot1.json` and `rotors.dot1.json`.
- **Ran in Node (scratchpad):** I loaded the compressed probe GLBs with three r186 `GLTFLoader` + `MeshoptDecoder`, using the existing scratchpad install (three 0.186.1, three-mesh-bvh 0.8.3), and resolved every draft name against the loaded nodes. I also ran a coarse ray sweep for D2.
- **Read in three r186:** the `WebGLClipping` and `WebGLRenderer` sources, for the free plane.
- **Not run:** Blender, and I did not touch the MCP.

## Findings

- **I1. D2's "≥ 180/189 pickable by `pickSweep`" is not justified, and it will probably fail.**
  - **Where:** §1 D2 and §4.2.11 `pickSweep`.
  - **Why:** `fitToBox` keeps the current view direction, and the plan does not say which direction `pickSweep` uses.
  - **Evidence:** a coarse Node ray sweep on `models/line.glb` (12 × 12 rays per device, first hit must belong to the device):
    | View direction | Devices with a first hit |
    |---|---|
    | FULL preset direction, camera at `fitToBox` distance | 112/189 |
    | Best of the 6 axis directions | 152/189 |
  - **Many devices are genuinely enclosed:**
    - barrels B3–B6 and joints 1–5 sit under the covers and heater shells;
    - the cooling-water parts sit under the barrel;
    - there are frame feet and parts in the floor trench.
  - The sampling is coarse and under-counts thin parts, but the gap to 180 is far too large to be noise.
  - **Fix:** gate D2 on `selectAll()` reaching 190/190 plus selection from the device tree. Make `pickSweep` report only: try 6 directions, and compare against an expected-unpickable list that a Node probe computes now with finer sampling and writes into the data.

- **I2. `precompileStates` can race the user's state changes.**
  - **Where:** §4.2.3 (`rigInterior` calls `precompileStates` "lúc rảnh") and §4.2.6.
  - **Problem:** precompile runs right after the interior loads, which is exactly when the user has just entered CUT_Z_BARREL. It calls `applyState` (`resetCuts` + apply) for every state, and `applyState` is async (it awaits `interiorReady`).
  - **Effects:**
    - A toolbar click during precompile interleaves `resetCuts` and the list steps, which leaves a mix of two states.
    - Even without a click, the last precompiled state stays on screen unless the current state is re-applied.
  - This will show up as flaky D6/D7 runs and wrong screenshots.
  - **Fix:** serialize every `setStateId`, `enterFree` and `leaveFree` and precompile through one promise queue (`store.busy`), and re-apply `store.state` at the end of precompile. Alternatively, compile the cut variants on an off-screen dummy scene without touching visibility.

- **M1. The FREE note in the stand-in data contradicts the plan.**
  - **Where:** `cut_states.dot1.json` FREE (`"clip": "all visible parts (renderer.clippingPlanes, global plane)"`) against PLAN §4.2.6 (one shared local `freePlane`, never `renderer.clippingPlanes`).
  - **Problem:** builder B starts from this file, so it can mislead them.
  - **Fix:** correct the string in `gen_drafts.py`. The plan's approach is the right one (see Verified OK).

- **M2. The scope is heavy for a slice the user wants to see soon.**
  - **Where:** §5. Builder B's critical path is 5.9 h, then review and fix.
  - **Estimates:** they are realistic for the stated scope; the probes already removed the export unknowns. But much of B4–B7 is polish or test machinery:
    - the peel;
    - camera presets for every state;
    - `pickSweep`, plus the 24 × 24 pixel sampling in `capCheck`;
    - `timeState` with precompile;
    - `orbitTest` with the performance trace;
    - an exact `rotorTest`;
    - the accent-insensitive device search (A6 is 75 min);
    - the FREE flip and axis switch.
  - **Fix:** show the user the B3 milestone (load, select, outline, bbox, zoom; about 2.5 h). Then do B4 (4 fixed states with caps, without peel) and B5 (FREE plus `cutRoundTrip`). That is about 4.5 h to a reviewable Đợt 1. Move peel, precompile/`timeState`, `pickSweep` and the trace to a "Đợt 1b". Keep `rayUnfiltered`, `cutRoundTrip`, `capCheck` (with simple sampling) and D12 as the gates.

- **M3. HMR can leave an empty registry.**
  - **Where:** `rig.ts`; the `scene.userData.zeRigged` guard with a module-level `reg`.
  - **Problem:** a Vite hot update of `rig.ts` creates a new, empty `reg`, while the cached `useGLTF` scenes stay marked as rigged. The registry then stays empty until a full reload. This affects dev only, but it will confuse builder B.
  - **Fix:** keep the registry on `scene.userData`, or call `import.meta.hot.invalidate()` (full reload) in `rig.ts`.

- **M4. The export always reflects the last save of the .blend.**
  - **Where:** §8 Safety, item 2.
  - **Problem:** the user has `out/ze155_anim.blend` open. A background read is safe, since Blender takes no lock and writes with an atomic rename, and the mtime/size check catches a save during the export. But edits in the user's session that are not yet saved are silently left out of the GLBs.
  - **Fix:** say so in the plan and in the export report, so nobody hunts for a "missing" change.

## Verified OK

- **Runtime rig and meshopt:**
  - All 561 exported names load unchanged with three r186. `node_map` has 0 missing and 0 extra entries, and no node is assigned to the wrong file.
  - Exactly 4 named nodes end up with an unnamed payload child: `int_valve_bolt`, `int_sc_disc`, `int_pump_gear_top` and `int_pump_gear_bottom`. The only other named nodes with named children are the `anim_roll_axis_*` and `int_screw_axis_*` empties.
  - The payload rule and "only payloads change `visible`" fit the GLBs. Rotors are runtime `Object3D`s at `pivot_m`, with nodes attached to them, so the TRS that meshopt rewrites is never animated.
  - Every Đợt 1 `pivot_m` matches the exported world position of its node (screw axes and roll axes to within 0.1 mm). The pivot of the gearbox schematic sits on its axis rather than at the quantize offset, which is intended (slice 2).
- **Raycast filter and round trip:** the plan keeps the C1/N1 design: filtering inside `mesh.raycast`, no drei `<Bvh>`, the identity check and `rayUnfiltered`. `filteredRaycast` returning `false` for hidden nodes is safe, because only payloads change visibility. `cutRoundTrip` compares visible payloads, material uuids, and leftover `freePlane` references.
- **Free plane:** one shared local plane works in r186.
  - `WebGLRenderer` calls `clipping.setState` for every material when local clipping is on.
  - `projectPlanes` re-projects `material.clippingPlanes` from the plane instance each frame, so changing `constant` or `normal` needs no material rebuild.
  - The raycast filter and Outlines read `material.clippingPlanes`, so they follow the plane.
  - The cap shader is the same as for state planes.
  - Keeping the ground, the `Box3Helper` and the hulls unclipped is a real improvement over `renderer.clippingPlanes`.
- **Data:**
  - Every name in the 6 states resolves (`swap` keys and values, all lists, `rotors[].attach`).
  - No state shows a node in both a show list and `hide`/`swap`. Every `swap` value is shown. No node is in both `clip` and `hide`. No cut-only node appears outside its own states.
- **No z-fighting:** with world bboxes from the compressed GLBs, no Đợt 1 state, FREE included (115 full interior parts), shows a visible exterior part together with an interior node of the same bbox (within 3 mm). Every hollow appears only while its exterior is swapped out.
- **Pre-cut swaps for X2450 and X4120:** elements 12–32 or 22–32 and the zone fills are hidden; the `_x2450`/`_x4120` elements, the `xsec` caps and the `x*` fill are shown; B3, or B5 plus dome 2, are swapped for runtime-clipped hollows. The pre-cuts are children of `int_screw_axis_*`, so they turn with the screws.
- **Peel:** clones of the clip parts and swap keys, clipped by the opposite plane, are helpers with no raycast and are stopped by `resetCuts`. Fine for CUT_Z_BARREL.
- **Safety:**
  - `export_glb.py` has no save call and refuses `--out` or `--report` outside `web/build/`.
  - It checks the mtime and size of the .blend, runs with `--factory-startup` (so the user's MCP port 9876 is not touched), and passes `use_active_scene=True`, which avoids the known 5.2.2 crash path.
- **Integration:** B can start on `build/probe/models` and the `.dot1.json` drafts. Integration point I1 is clean, because `make_data.py` is gated on reproducing the drafts exactly.

## Verdict

**Ready to build after two small plan edits:**
- I1: change the D2 gate to `selectAll` 190/190 plus selection from the tree, with `pickSweep` as a report against a computed expected list;
- I2: serialize state changes and precompile.

I also recommend the M2 scope cut so the user sees Đợt 1 sooner. Nothing in the export, the rig, the clipping or the data model needs rework.
