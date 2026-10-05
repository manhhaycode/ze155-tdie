# Animation builder instructions (shared by every animation build phase)

The animation design is approved. You build it in the live Blender through MCP, one phase per agent. You never certify your own work: an independent reviewer checks it after phase A3.

## Read first
- `BRIEF.md`: hard rules. The rule that limits work to scene `ze155` is overridden by D1 below; every other rule still holds, including no headless Blender and no generator/download tools.
- `METHOD.md`, `BUILD.md`: modelling technique, the realism checklist and look → compare → fix. Ignore BUILD.md's "Start of every phase" and "End of every phase" sections and its save step; this file replaces them.
- `anim/design-anim.md`: the approved brief (Vietnamese). §7 covers technique, §8 scene, save and camera cleanup, §9 the phases and the reviewer checklist.
- `anim/shots.json`, `anim/interior_parts.json`: the exact data. `anim/review-anim-01.md` is background only; its fixes are already applied.
- `anim/log.md`: what earlier animation phases did. Continue from there.

## Decisions (all resolved)
- **D1:** build in a new scene `ze155_anim` in the open session. Scene `ze155` stays clean.
- **D2:** camera cleanup happens only through the anim scene. `ze155_anim` gets its own 24-camera rig and does not link `ze155_rig`. Nothing in `ze155` is deleted.
- **Q1:** the full version: 16 shots, 3:31, 5 275 frames, 1920 × 1080 at 25 fps.
- **Q2:** keep the existing 450 mm die. Near-T coat-hanger (preland 32 → 11 mm), plus a 2D exaggerated inset in post.
- **Q3:** labels and HUD in post with Pillow. Blender exports per-frame anchor coordinates.
- **Q4:** speed badges (screws 20×, pump 4×, rolls real speed), flows marked "minh họa", assumed values marked `*`.
- **Q5:** the design deviations of brief §10 are fixed only in the animation (pump about 69 rpm, screen-changer disc axis parallel to X, sliding start-up valve bolt). Do not edit `design/`.
- **Q6 (a):** the sheet-line control scheme. Pump speed is the setpoint; P3 trims feeder rate and screw speed in ratio.
- **Q7: no headless Blender.** Every build step and the final render run through MCP, in resumable chunks. Phases run one after another; never two Blender agents at once.

## Blender safety (hard)
- The live session has `out/ze155.blend` open with unsaved changes that are not ours. Never call:
  - `save_mainfile`, `save_as_mainfile`, `open_mainfile`;
  - `wm.revert`, `read_factory_settings`;
  - anything that saves, reverts or replaces the open file.
- Never call `Z.save_blend()`: it targets `out/ze155.blend`, and its read-back fails on the open file. Never call `Z.setup_scene()` either: it re-targets scene `ze155`.
- Never change any `ze155` object:
  - no transforms, parenting, `hide_render` or `hide_viewport`, modifiers, mesh data or deletion;
  - material changes count too: copy a material before changing it for the anim;
  - in the anim, use copies (`anim_split_*`, `anim_cut_*`) or new objects.
  Linking a `ze155` object into an anim-only `ax_*` collection is allowed; that is how the anim scene sees it.
- Only key the visibility of anim-only collections.
- `Z` geometry helpers (`bm_*`, `revolve_bm`, `extrude_bm`, …) are fine. Check where `Z.obj` and `Z.link` link new objects, and make sure every object you create ends up only in `anim_*` or `ax_*` collections of `ze155_anim`, never in a `ze155_*` collection.
- Keep each `execute_blender_code` call under about 2 minutes (render at most about 40 frames per call).
- If Blender restarts, or `ze155_anim` is missing when you start, STOP. Report to the orchestrator; do not improvise an append.

## Anim helpers
- C0 creates `anim/anim_helpers.py`, which registers `bpy.app.driver_namespace['za']`. It needs at least:
  - `za.scene()`;
  - collection getters;
  - object creation into anim collections;
  - `za.save()`;
  - `za.look(shot, frame, path, engine)`;
  - `za.render_range(...)`, which skips frames whose PNG already exists.
- Later phases extend it; only one agent edits it at a time.
- `za.save()` must:
  1. call `bpy.data.libraries.write(OUT+'ze155_anim.blend', {ze155_anim}, fake_user=True)`;
  2. copy the file to `anim/tmp/verify.blend` and load that copy with `bpy.data.libraries.load` to list scenes, collections and object counts;
  3. return them.

## Start of every phase
1. `get_addon_status`, then `get_scene_info`.
2. Exec the helpers in this order:
   1. `exec(open('/Users/manhhaycode/m3d-e2e/ze155-tdie/tools/ze_helpers.py').read())`, then `Z = bpy.app.driver_namespace['ze']; Z.load_views()`;
   2. after C0, also `exec(open('/Users/manhhaycode/m3d-e2e/ze155-tdie/anim/anim_helpers.py').read())`, then `za = bpy.app.driver_namespace['za']`.
3. Check the state:
   - `ze155` still has 610 objects and 73 cameras;
   - after C0, `ze155_anim` exists with the object count from the last `anim/log.md` entry.
4. Append a phase header with the time to `anim/log.md`.

## While building
- Build what `interior_parts.json` and `shots.json` specify, at their positions. Where the data is silent or wrong against the scene, decide, build it, and log `DESIGN-DEVIATION: <item> <what> <why>` in `anim/log.md`. Do not edit the design files: `design-anim.md`, `shots.json`, `interior_parts.json`.
- Check by numbers, not only by eye:
  - positions against parts.json;
  - screw intersection at 8 rotation angles, and clearance to the bore ≥ 0.4 mm;
  - seals end before the vents at X 1990 / 3860;
  - no part sticks through a section plane;
  - rotation directions as in brief §7.
- Look → compare → fix: render the key frames of each shot you touch (Workbench or a low-sample EEVEE at 960 × 540) into `anim/look/`. Compare against `anim/storyboard/S*.png` and the reviewer checklist in brief §9. Do at least 2 rounds for big items and stop at 4. Log the concrete differences and fixes.
- Keep the scene light, within the triangle budgets in `interior_parts.json`. Use linked duplicates for repeated screw elements.
- If your context grows large, write `anim/HANDOVER-<phase>.md` (state, scripts, conventions, open issues) and tell the orchestrator.

## End of every phase
1. Call `za.save()` (after C0 exists) and check the returned counts.
2. Re-check that `ze155` is unchanged: 610 objects, 73 cameras.
3. Append to `anim/log.md`:
   - what you built (object names);
   - checks by numbers;
   - look rounds;
   - remaining differences;
   - triangles;
   - what the next phase must know.
4. Reply with the same summary. Do not claim anything you did not check.
