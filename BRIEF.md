# ZE 155/34D twin-screw extruder with T-die — shared brief for every agent

Read this whole file before doing anything. It is the contract between the orchestrator and every subagent.

## Goal
1. Research the KraussMaffei Berstorff **ZE 155 UT** co-rotating twin-screw extruder, L/D **34**, fitted with a flat **T-die** (slot / coat-hanger die) for sheet or film.
2. Produce a detailed drawing set (`drawings/`). It must show the full exterior and **every part that matters for operating the machine**, connected the way the real machine is connected.
3. Build a complete, realistic 3D model in the open Blender, **only through Blender MCP**, following the GX200 spike method (`METHOD.md`).

Where no source gives a value, the agent may assume it. Every assumption is written down with its reasoning (scale from photos, typical ratios for this machine class, catalogue of a similar size). The user explicitly allowed assumptions and brainstorming for undocumented parts. Do not stop to ask the user anything: decide, write the decision down, continue.

## Workspace: `~/m3d-e2e/ze155-tdie/`
| Path | Content | Owner |
|---|---|---|
| `research/pdf/ZE_twin-screw_extruders.pdf`, `ZE_text.txt` | the KraussMaffei Berstorff ZE catalogue (public, plastrading.com) and its text | given |
| `research/pages/pNN.png` | the 30 catalogue pages at 150 dpi | given |
| `research/pdf_images/pNN_M.jpeg` | the 45 images embedded in the catalogue | given |
| `research/pdf_catalog.md`, `research/pdf_crops/` | what each catalogue image shows, crops, measured ratios | pdf analyst |
| `research/web/` | downloaded reference photos plus `images.md` (source URL, what is shown, view angle) | web researcher |
| `research/claims.jsonl`, `research/specs.md` | sourced facts and the spec summary | web researcher |
| `design/` | `design.md` (part list, dimensions, positions, connections, assumptions), `parts.json`, the drawing scripts | designer |
| `drawings/` | drawing sheets (`sheet-*.svg` + `.png`), scaled orthographic views for Blender (`views/*.png` + `views.json`) | designer |
| `tools/ze_helpers.py` | Blender helper library (exec'd inside Blender through MCP) | builder |
| `out/` | `ze155.blend`, `log.md`, `look/`, `compare/`, `renders/`, `report.md` | builders |
| `DECISIONS.md` | orchestrator decisions | orchestrator |

## Coordinate system (fixed, everybody uses it)
- Units: millimetres in documents and drawings; Blender data in metres (mm × 0.001), scene unit display in mm.
- **X** along the screw axes, **+X = flow direction** (motor → gearbox → barrel → melt line → T-die).
- **X = 0** at the drive-side face of barrel section 1 (the gearbox output flange / barrel interface).
- **Y** horizontal across the machine, **Y = 0** on the vertical plane midway between the two screw axes. **+Y = operator side** (control panel, HMI).
- **Z** up, **Z = 0** floor level.
- Front elevation = viewed from +Y looking toward −Y. In that view +X (die end) appears on the **left**, like the ZE UT silhouettes on catalogue page 9.

## Hard rules
- Web research uses public sources only. Never send anything from the user's own folders (for example `~/ideathon-toyobo/`) to any web service.
- Image files are viewed with Read. Image processing with `uv run -q --with pillow --with numpy python …` (PyMuPDF: `--with pymupdf`). Drawings with matplotlib or hand-written SVG (`--with matplotlib`).
- Blender (builders only):
  - only `mcp__blender__execute_blender_code`, `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `get_addon_status`;
  - **never** use any generate/download/import tool (Hunyuan3D, Hyper3D/Rodin, Tripo, Sketchfab, Poly Haven, Poly Pizza, `import_generated_asset*`, `set_texture`, `export_scene`);
  - never run Blender headless (`Blender -b`), never build geometry in a script outside Blender;
  - work only in the scene **`ze155`** and its collections (`ze155_*`). Never delete or change objects, materials, cameras or settings that belong to another scene;
  - never call `save_mainfile`, `save_as_mainfile`, `open_mainfile`, `read_factory_settings`, `wm.revert`, or anything that replaces or saves the open file. Save only with `bpy.data.libraries.write(path, {scene}, fake_user=True)`;
  - Blender 5.2 rules: find shader nodes by `type`; read enum values before assigning; set the render engine inside `try/except TypeError`; pass `view_layer=` to `hide_set` and `select_set`.
- Keep `out/log.md` (builders) or your own notes file current, so the next agent can continue after a context reset.
- Write user-facing documents (`design.md`, `report.md`, drawing labels) in Vietnamese with the English technical term in parentheses the first time it appears. Notes for other agents can be English.
- When you finish, end your reply with: files written, what is done, what is assumed, and open problems. Do not claim anything you did not check.
