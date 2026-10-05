# Builder instructions (shared by every builder phase)

Read first, completely:
- `BRIEF.md` (hard rules, especially the Blender safety rules);
- `METHOD.md` (the GX200 method you must follow);
- `DECISIONS.md`;
- `design/design.md`, `design/parts.json` (the parts, positions, connections and visible details you must model);
- `drawings/views.json` and the drawing sheets in `drawings/` (`sheet-*.png`);
- `out/log.md` (what earlier builders did; continue from there).

The research photos are listed in `research/web/images.md` and `research/pdf_catalog.md`.

## Start of every phase
1. `get_addon_status`, then `get_scene_info`.
2. Load the helpers: `exec(open('/Users/manhhaycode/m3d-e2e/ze155-tdie/tools/ze_helpers.py').read())`, then `Z = bpy.app.driver_namespace['ze']; Z.setup_scene(); Z.load_views()`.
3. If the scene `ze155` is missing or empty but `out/ze155.blend` exists, Blender was restarted. Append the saved scene before working:
   ```python
   with bpy.data.libraries.load(path, link=False) as (src, dst): dst.scenes = ['ze155']
   ```
   Then make it the window scene. Check that the object count matches the last log entry.
4. Append a phase header to `out/log.md` with the time.

## While building
- Model what `parts.json` says, at its positions. Use `details` and `design.md` for the visible features.
- Where the design is silent or looks wrong against the photos, decide, fix it in the model, and write a line `DESIGN-DEVIATION: <part> <what> <why>` in `out/log.md`. Do not edit `design/` files.
- Realism means modelling what a person would see on the real line:
  - flange bolts on bolt circles and C-clamps at barrel joints;
  - cover handles, hinges and warning triangles;
  - heater cables in ducts, cooling hoses to the manifold, valve handles;
  - pipe elbows ending at fittings, cable glands;
  - door seams and louvres on cabinets;
  - lifting lugs, nameplates (plain plates, no text required), guards with mesh or slots;
  - floor anchors under feet.
  Every visible hard edge gets a bevel.
- Every part touches what `connects_to` says; nothing floats. Check with `Z.bbox([...prefix])` and numbers, not only by eye.
- Collections:
  - `ze155_parts` holds the machine;
  - `ze155_context` holds the roll stack, floor, platform surroundings if not part of the machine;
  - `ze155_rig` holds cameras and lights;
  - `ze155_cutters` holds boolean cutters;
  - `ze155_blockout` holds the blockout. Hide it from render once detailed parts replace it.
- Object names: ASCII snake_case with the group prefix from parts.json, e.g. `drive_`, `gbx_`, `barrel_`, `feed_`, `vac_`, `melt_`, `die_`, `frame_`, `ctrl_`, `util_`, `ctx_`.
- Keep the scene light. Bevel segments 1–3, cylinder segments 16–64 by size, arrays instead of thousands of separate objects. Target below about 3 M triangles for the whole line.

## Look → compare → fix (mandatory, per part group)
- Drawing check:
  1. `Z.render('cam_<view>', Z.OUT + 'look/<group>-<view>-r<n>.png')` (Workbench, transparent).
  2. `uv run -q --with pillow python tools/cmp.py drawings/<views image> out/look/... out/look/<...>-cmp.png`.
  3. Read the result.
  - Detail views in views.json have their own cameras: `Z.make_ortho_cam('<key>')`.
- Photo check:
  1. Make a perspective camera close to a reference photo's angle (`Z.persp_cam`).
  2. Render EEVEE (or Workbench for speed) at about 1200 px.
  3. Put it side by side with the photo: `tools/cmp.py photo render out side`.
  4. Read it and list what the photo has that the model lacks: proportion, shape, detail, colour.
- Write concrete differences and fixes in `out/log.md`. Big groups: at least 2 rounds; stop at 4 rounds and write down what still differs.

## End of every phase
1. `Z.save_blend()` writes `out/ze155.blend`. Check the returned info (scene and object count).
2. Append to `out/log.md`: what was built (object names), rounds per group, remaining differences, triangles, bbox, and anything the next phase must know.
3. Reply with the same summary. Do not claim what you did not check.
