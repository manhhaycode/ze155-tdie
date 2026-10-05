# Method — copied from the GX200 spike (session 41763e1d), adapted to ZE 155

The GX200 spike built a Honda GX200 in Blender through MCP in about 47 minutes and 75 `execute_blender_code` calls. All three bounding-box dimensions came within 0.3 % of the drawings, and the model looked like the photos (`~/m3d-e2e/gx200-spike/out/compare/ref-images-07.png`). This file records what that session did, so the ZE 155 build can do the same.

## 1. Helper library, loaded once, reused by every call
- The GX200 session wrote one helper library and stored it in `bpy.app.driver_namespace['gx']`. Every later call started with `G = bpy.app.driver_namespace['gx']`. Its source is in `tools/gx200_reference/call03_helpers.py`; all 100 calls are in `all_blender_calls_gx200.py`.
- For ZE 155 the library lives in a file, `tools/ze_helpers.py`. It is loaded inside Blender with `exec(open('/Users/manhhaycode/m3d-e2e/ze155-tdie/tools/ze_helpers.py').read())` and registers `bpy.app.driver_namespace['ze']`. Because it is a file, it survives agent hand-overs and Blender restarts. If you change the file, re-exec it.
- What the library provides:
  - `box`, `extrude` (polygon in one plane, extruded along the third axis), `revolve` (r, h profile spun about any axis), `rrect` (rounded-rectangle outline);
  - `bevel`, `solidify`, `wnormal`, `hard` (smooth shading + bevel + weighted normals), `boolean` (cutter hidden), `apply_mods`;
  - `mat(name)`: Principled materials found by node type, colours given in sRGB;
  - `remove(name)`: refuses to touch objects that belong to another scene.
- Part geometry itself is written by hand, one part per call. Each call is about 1–4 kB of bmesh or modifier code, built from outlines read off the drawings. Not primitives left as-is.

## 2. Scale frame first: orthographic cameras with the drawing as background
- One orthographic camera per drawing view: `cam_<view>`.
  - `ortho_scale` = longest image side (px) ÷ px_per_mm × 0.001.
  - Location is the world point at the image centre, pulled back along the view direction.
  - `background_images` holds the drawing with alpha 0.5.
- Big blocks first. Render each view in Workbench (cavity + outline, transparent film) at the drawing's resolution, then build the comparison with `tools/cmp.py ref.png render.png out.png` (panels: original | overlay with blue model outline | render). Read the comparison and write the concrete differences to `out/log.md`. Fix and repeat until the outlines match. Only then start detailing.
- `drawings/views.json` (written by the designer) has one entry per view:
  ```json
  {"front": {"image": "views/front.png", "width_px": 3200, "height_px": 1000, "px_per_mm": 0.25,
             "center_mm": [5000, 0, 1500], "right": "-X", "up": "+Z", "look": "-Y"}}
  ```
  - `center_mm` is the world point at the image centre; the coordinate along the look axis is ignored.
  - `right`, `up` and `look` are the world axes that point to image right, image up, and into the screen.
  - Pixel (u, v), with v counted from the top, maps to `center + (u − W/2)/s · right + (H/2 − v)/s · up`, where s = px_per_mm.

## 3. Detail, big to small, each part attached to its neighbour
- Revolve: shafts, flanges, couplings, motor housing, pipes, knobs, vent domes, pump bodies.
- Extrude traced outlines: frame members, gearbox casing, die body, guards, brackets.
- Bevel on every hard edge, 1–10 mm depending on size, plus smooth shading and weighted normals.
- Solidify for sheet metal (covers, guards, cabinets). Array for repeated items (bolts, heater bands, fins, frame cross-members, die lip bolts). Boolean for holes and slots:
  - use the MANIFOLD solver for closed solids, EXACT for open shells;
  - EXACT returned empty meshes on some shells in Blender 5.2.
- Nothing floats: flanges meet flanges, pipes end at a fitting, feet stand on the floor (Z = 0). Bolts sit on bolt circles.
- Object names are ASCII snake_case with a group prefix, for example `drive_motor`, `barrel_sec03`, `melt_screen_changer`, `die_body`.

## 4. Look → compare → fix, after every part group (mandatory)
1. Render the part group from the matching drawing camera (Workbench) to `out/look/<group>-<view>-r<n>.png`. For realism, also render from a perspective camera close to a reference photo (EEVEE).
2. Build the comparison with `tools/cmp.py`. For photos of a different machine or angle, use mode `side`: the photo then guides style, proportion and detail rather than exact overlay.
3. Read the comparison. Write concrete differences in `out/log.md`, for example: "gearbox 12 % too short in X, top cover too square, oil cooler missing".
4. Fix and repeat. Big groups get at least 2 rounds; stop after 4 and write down what still differs.

## 5. Matching a perspective camera to a photo (GX200 did this for 3 photos)
- Search a grid of azimuth, elevation and focal length, then iterate distance and shift until the projected bounding box matches the photo's machine box. Pick the best by the error on 5 feature points.
- Helper: `persp_cam(name, az, el, lens, target, dist)`. Azimuth 0 looks along +X; the camera sits at `target + dist·(−cos e·cos a, −cos e·sin a, sin e)`.

## 6. Materials, light, render
- Simple Principled materials. Colours are measured from the photos by averaging Pillow pixels over a patch. No image textures, no downloaded HDRI.
- Three area lights plus a grey world. View transform Standard; AgX shifted saturated colours in the GX200 run. Look Medium High Contrast.
- Final renders in EEVEE: `out/renders/` (hero 3/4 from the operator side, 3/4 from the die end, front, top, die end). Final comparisons with `tools/final_cmp.py` go to `out/compare/`.
- Print the bounding box with code and check it against the design.
- Save with `bpy.data.libraries.write(out/ze155.blend, {scene}, fake_user=True)`, then verify the file by loading it back with `bpy.data.libraries.load` and listing what is inside.

## 7. Pitfalls the GX200 session hit
- EXACT boolean can return an empty mesh on open shells. Use MANIFOLD for closed solids.
- AgX makes saturated colours drift (red turned orange). Use the Standard view transform.
- Rendering: set `bpy.context.window.scene` to the work scene, then call `bpy.ops.render.render(write_still=True, scene=sc.name)`.
- Keep `out/log.md` current, so work can resume after a context reset.
