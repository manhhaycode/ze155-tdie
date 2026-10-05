# Addendum: decisions and proposals from the user discussion (2026-10-05), to fold into PLAN-R3F.md

Status: items 1–3 are user decisions. Items 4–9 are orchestrator proposals the user is leaning towards; the user approves them after the plan review. Q1–Q5 of PLAN-R3F.md are still open.

1. **Target is web R3F only** (DECISIONS 29). No MP4, no frame render, no Pillow overlay. `anim/post/` is a layout reference only.
2. **Blender does only what can show on the web.** The film-style A2/A3 is not built:
   - no Geometry Nodes pellets or bubbles;
   - no Blender-only flow shaders;
   - no per-shot collection-visibility keys;
   - no camera re-keying.
   Those become R3F code or `tour.json` data.
3. **The user's R3F project does not exist yet.** The sandbox `web/web-check/` proves compatibility; its components are later copied into the real project.
4. **Blender preview merged into W1, web-first.** Pivots for rotating parts are empties, per the contract.
   - Drivers may be added on those empties only so the user can press Play in Blender. They are not exported; the web uses `useFrame` with userData rpm.
   - Choreographed moves are NLA clips named per the contract: valve run, screen-disc index, die open; also barrel-shell peel or backflush piston if cheap.
   - Baked cut copies are made only if Q2 chooses baked states.
5. **Vertical slices.** Each slice runs end to end (Blender prep → export → sandbox → review) before the next one starts, so the user sees results early:
   - **Đợt 1:**
     - the whole exterior with the device tree and userData, clickable like Blender (hover and selection outline, bbox, zoom, info panel);
     - the barrel cutaway with the screws turning in the figure-8 bore: the A1a interior under its host, the screw pivots, the free and fixed cut states for the barrel (Z 1200 half and X 2450 / 4120);
     - target: viewable in a browser about 2 h after start.
   - **Đợt 2:**
     - the melt line interior: head, valve, screen changer, gear pump, pipe/mixer, die sections;
     - pivots for the pump gears, gearbox schematic and rolls;
     - the 3 clips;
     - flow attributes and the fill shader;
     - the die cut states.
   - **Đợt 3:** `tour.json`-driven step tour, `<Html>` labels, screw-configuration strip and control-loop block diagram as React components; S14/S15 flow graphics if time allows.
6. **Parallel streams.** One Blender agent at a time, serial; at most about 4 agents concurrently overall.
   - **A, Blender (serial, via MCP in the open session):**
     1. first a quick raw GLB export of the current exterior as a stand-in for the web stream (about 10 min);
     2. W1 for Đợt 1, then W2 for Đợt 1;
     3. W1 for Đợt 2, then W2 for Đợt 2.
   - **B, web core:** the Vite + R3F sandbox on the stand-in GLB: loading, picking/outline/bbox/zoom, clipping and caps, rotation from userData. It swaps in the real GLBs as stream A delivers them.
   - **C, data and HUD (no Blender):** first `devices.json`, `tour.json`, the gltf-transform compression script and `check_glb.py`; then the tour UI, labels, screw strip and control diagram components.
   - **D, review:** an independent reviewer per slice, in Chrome via the chrome-devtools MCP, running while stream A builds the next slice. A separate fixer applies the findings. Reviewers never fix.
7. **Contract discipline.** All streams follow `model-contract.json`. After every export, `check_glb.py` validates the GLB against the contract before stream B integrates it.
8. **Constraints:**
   - no headless Blender;
   - no MCP `export_scene` tool; export runs through `bpy.ops.export_scene.gltf` inside `execute_blender_code`, pending Q1;
   - never change `ze155` or `ze155_anim` objects, meshes or materials in place;
   - save only via `libraries.write` to separate files;
   - the user must not press Ctrl+S.
9. **Estimate to verify:** about 5 h wall clock in parallel, against 7–9 h serial; about 10–15 % more total effort from the per-slice export and review rounds.
