# Drafter handover (drawing set ZE 155 A UT 34D + melt line + T-die)

State at hand-over: parts.json has 187 parts and 72 connections. `make_all.py` runs end to end in about 20 s. `verify_views.py` passes **68/68**. Sheets 01–07 are regenerated on A0 (Rev. B). The work in response to `drawings/review-01.md` is partly done; see §3.

## 1. Script architecture (`design/draw/`)
- **`geom.py`: single geometry engine.**
  - Reads `design/parts.json`.
  - `part_prims(pid)` builds 3D prims for one part: `B` box, `C` cylinder, `R` revolve (profile r,h), `PR` prism (outline + extrusion), `H` convex hull, `PI` pipe/rod (any direction), `Q3` planar polygon, `L3` polyline, `D` decal (2D shapes on an axis-aligned face, drawn only when the face looks at the viewer).
  - Dispatch order:
    1. `SPECIAL[pid]`, the hand-written per-part functions, then the `SPECIAL.update({...})` block near the end of the file, which holds the data-driven rev-2 functions;
    2. `paths_mm` → one pipe per path;
    3. `positions_mm` + `item_mm` → `g_repeat`, or `g_tilted` when `item_axis` / `item_axes` is present;
    4. `outline_mm` → prism;
    5. shape fallbacks.
  - **To add or improve a part:** write `g_<name>(p)` returning prims, and register it in the final `SPECIAL.update`. Keep the silhouette inside the bbox: views and verify compare against the bbox.
  - **Projection:**
    - `View(name, right, up, look)` with axis strings; the predefined views are in `VIEWS`.
    - `project(prim, view)` gives 2D items: poly, circle or line, each with a depth.
    - `scene(view, ids)` returns the items painter-sorted, far first.
    - `bbox_uv(pid, view)` returns the projected bbox.
- **`views.py`:** Blender background PNGs (Pillow) and `drawings/views.json`.
  - `SPECS` = name → (view, px/mm, world extents). Keys and image names must stay stable.
  - Also writes `views/check/<view>_parts.json`, the pixel bounds of each part's drawn outline.
- **`verify_views.py`:** METHOD.md formula check.
  - `CHECKS` = view → [(part, corners)]. Corner subsets are used where another part legitimately hides a corner.
  - Writes `views/check/<view>.png` with red crosses.
  - When a new part hides a checked corner, drop that corner from the subset and add a comment.
- **`sheet.py`: drafting library.**
  - `Sheet(num, slug, title, size, scale, subtitle)`: A0 frame, zone grid, title block 250 × 84 plus revision and subtitle rows.
  - `text()` enforces `MIN_FS` = 9.8 pt, i.e. 2.5 mm cap height.
  - `dim()`, `balloon()`, `label()`, `labels_column()` (orders labels by target height so leaders don't cross), `heading()`, `table()`, `notes()`.
  - `save()` runs `frame_check()` (annotation outside the frame) and `text_overlaps()` (text box collisions). Set env `DRAW_VERBOSE=1` to list them.
  - `save()` also writes the per-sheet balloon/mention registry `design/draw/balloon_index.json`, intended for a future full-BOM sheet.
  - `VP(sheet, view, k, ox, oy, uc, wc, clip)`: places a projected view at scale 1:k.
    - `draw(ids, phantom=…)` puts context parts in phantom and draws `hidden` prims dashed.
    - `balloons(ids, sides, offset, rows)` picks a visible target point from an id-buffer.
    - `dimw()` dimensions between world points; `cline()` draws centre lines.
  - `sheet_parts_list(sh, x, ytop)` lists exactly the balloons and `label(..., pid=)` mentions on that sheet (review M6).
- **`drafting.py`:**
  - Section helpers: `region` (hatched with holes), `fig8` bore, `erdmenger` 2-flight screw profile, `hexagon`, `section_marker`, `detail_marker`.
  - P&ID symbols: `sym_valve` (gate/ball/solenoid/pneumatic/throttle/relief/check/manual), `sym_strainer`, `sym_pump`, `sym_instrument` (ISA bubble; `panel=True` adds the bar), `sym_box`.
- **`sheet01_ga.py` … `sheet07_pid.py`:** one script per sheet, positions in sheet mm (A0 = 1189 × 841, frame 20…1177 × 12…829). The title stack occupies the bottom-right x 927–1177, y 12–122. Parts lists are placed in the right column at x 925.
- **`make_all.py`:** runs views → verify → sheets 01–07. Add new sheet scripts to its list.

## 2. Conventions
- **Coordinates:** X along the flow, Y toward the operator, Z up, in mm. X = 0 at the B1 drive face. Screw axis at Z 1 200.
- **Projection:** first angle (ISO E).
  - Front view from +Y (die on the left), plan below it (+Y at the bottom).
  - Drive-end view (−X) on the left, die-end view (+X) on the right.
  - Die top view on sheet 05: `View("dietop", "+Y", "-X", "-Z")`, lip at the bottom.
- **Scales:** GA 1:50; detail views 1:20, 1:10, 1:5 and 1:2. The Blender views are listed in README.
- **Text:**
  - ≥ 9.8 pt everywhere, enforced in `Sheet.text` and `table`; headings 14 pt.
  - Balloons r 5.2 mm, 10.5 pt (r 4.8 on dense sheets).
  - Instrument bubbles r 6.8.
- **Lines:**
  - visible 0.35–0.5 mm, thin 0.18–0.25 mm;
  - hidden dashed (7, 3.5 pt);
  - centre lines dash-dot;
  - phantom dash-dot-dot in grey for context items (`group == "context"`).
- **Numbering:** balloon number = `geom.NUM[pid]`, the index in parts.json order. It changes when the designer inserts parts; that is expected and every sheet is regenerated.
- **Repeated items:** `positions_mm` are item centres. With `item_axis` / `item_axes`, `item_mm` = [Ø, Ø, length along the axis]. Without them, `item_mm` is an axis-aligned size.
- **Painter's order:** items sort by their near depth along the look axis.
  - Prisms seen side-on are split into depth strips (fill-only items flagged `noline`, plus an outline item), so parts sitting on slanted faces draw correctly.
  - Thin proud offsets (+0.5 mm) are used for flush heads, e.g. `g_body_bolts`.
- **Blender views:**
  - group greys come from `GROUP_GREY` in views.py;
  - context parts are grey outlines with no fill, and the floor slab is omitted;
  - the mezzanine grating is unfilled in plan views (`nofill={"-Z"}`).

## 3. Status per review-01 finding
- **C1 open melt bore into the manifold: done.**
  - Sheet 05 section A–A: adapter Ø100 open, inlet throat symmetric about Z 1 200.
  - Sheet 05 section B–B: inlet drawn as an open channel.
  - Sheet 04 view A: hidden channel continues into the die, with the manifold circle.
- **C2 flange specs: done.**
  - `sheet04_melt.flange_table()` parses design.md §6.3. It feeds both the face views (view D) and the table.
  - View E is a 1:2 half-section of the pump → P4 flange: spigot, metal seal, stud, nut, heater band, sensor port.
- **I1 cooling water: done.**
  - Sheet 02 view D: elevation at 1:10 without covers, with balloons for 50–53, 165, 166, 170, 171.
  - Section E–E through a fitting, one-zone schematic.
  - View F: 1:50 water plan with 164, 167, 168.
  - Balloon numbers shift with parts.json; check them after a data change.
- **I2 interlocks, infeeds, e-stops: done.**
  - Sheet 07 parts 6–7: power one-line with p_12 / p_13, ES chain, trips s_10–s_17, cause-and-effect table parsed from design.md §7.
  - Sheet 01: e-stop markers ES1–ES9 in the plan, with a position table.
- **I3 P3 loop: done.** P3 → PIC → pump speed (s_20) on sheets 04 and 07.
- **I4 die body bolts: partly done.**
  - Shown in the sheet 05 top view (heads), in B–B (cut holes), and dashed in A–A.
  - The data puts the bolt rows across the manifold band. This is drawn as-is and flagged in red on B–B; it still has to be added as design_issues **#9**.
- **I5 open hinge slot: done.** Taken from the `die_body_upper` outline; web 12 and bolt bearing 36 are labelled; lip gap "↕ 0,5–2".
- **I6 flange Ø640 and neck: done on sheet 02.** Detail B has the Ø500 × 40 neck and a phantom socket envelope; the face view and A–A are at Ø640.
- **I7 coupling and lantern: done on sheet 03.**
  - Detail D: full section, motor shaft 320 long with 120 inside the hub.
  - Section E–E: output shafts, spline sleeves, screw shanks, staggered thrust bearings, window, B1 studs.
  - Still to add to design_issues: the `drive_motor` outline shaft stub ends at X −2 950, but it must reach −2 830 to engage the hub.
- **I8 utility routing plan from `connections[].path_mm`: NOT STARTED.**
  - Plan: a new `sheet08_utilities.py` on A0 at 1:50, drawing each connection path coloured by medium (reuse `C`/`LW`/`LS` from sheet07).
  - Balloon the trenches 155, 158, 159 and the air items 170–174, 142.
  - Add the 72-row connection table there; it was removed from sheet 07.
  - Then set `N_SHEETS = 8` in sheet.py and add the script to make_all.
- **I9 text size / empty space: mostly done.**
  - All sheets are on A0 with ≥ 9.8 pt text.
  - Not yet done: the full 187-row BOM on its own sheet (planned `sheet09_bom.py`, 2 columns, with the "tờ" column from `balloon_index.json`). The GA now lists only its own ballooned items.
- **I10 real P&ID: largely done** (sheet 07): ISA bubbles with tags, valve and pump symbols, line ids per connection, hydraulic 4/3 valves, instrument list.
  - Remaining: 13 small text overlaps where part-number tags inside boxes collide with box text. Run `DRAW_VERBOSE=1` and move the tags in `box()` / `sym_box`.
  - Some lanes are dense; check visually.
- **M1:** data only, already done (DN150).
- **M2:** done; relief valve, suction strainer, PSL, TT and cooler ball valve on sheet 03.
- **M3:** done; single nose profile clipped by a circle in detail D, lower-lip insert hatched in A–A.
- **M4:**
  - GA end-view headings now carry scales;
  - sheet 04 view A has break lines;
  - other clipped views (sheet 03 plan left edge, sheet 06 C/D/E) still have no break lines.
- **M5:** the overlap checker is clean on sheets 01–06. Sheet 07 has 13 overlaps. Leader crossings remain in dense balloon rows, most visibly on the sheet 01 plan.
- **M6:** per-sheet parts list = balloons + mentions: done. The BOM "tờ" column from the registry depends on sheet 09.
- **M7:** done; nuts drawn behind A–A, shafts hatched, Detail B body and flange hatched as one part each.
- **M8:** done; the screw table follows `screws.details`.
- **README** has not been updated for Rev. B. It still says A1 for sheets 02–06 and describes the old sheet 07; update it.
- **`design_issues.md`:** add #9 (die body bolt rows vs manifold) and #10 (motor shaft stub length).

## 4. Commands
```
cd ~/m3d-e2e/ze155-tdie
uv run -q --with matplotlib --with numpy --with pillow python design/draw/make_all.py        # ~20 s, all views + verify + sheets
uv run -q --with matplotlib --with numpy --with pillow python design/draw/verify_views.py    # 68 checks, must print "0 failed"
DRAW_VERBOSE=1 uv run -q --with matplotlib --with numpy --with pillow python design/draw/sheet05_tdie.py  # one sheet, list overlaps / out-of-frame items
```
- PNGs are 7 900 px wide (A0 at about 169 dpi); SVGs keep text as text.
- To inspect a region, crop the PNG with Pillow: scale = width / 1189 px per mm, y measured from the top = 841 − y_sheet.

## 5. Pitfalls and open issues
- The designer edits parts.json in parallel. Ids, bboxes and NUM numbers change; re-run everything and re-check verify subsets and balloon lists. Balloon lists filter out missing ids automatically.
- Hard-coded geometry in old `SPECIAL` functions, e.g. `g_hpu` and `g_vac_pump`, is shifted by bbox offsets in the rev-2 wrappers. If those bboxes change shape, rewrite them as data-driven functions.
- `sh.line()` annotations are not clipped to view windows; keep them inside, and `frame_check` will tell you.
- Matplotlib hatch density scales with dpi. The minimum text size makes dense label columns tall: use `labels_column(step≈7)`.
- **Open design data (design_issues #4–6):**
  - die internals: manifold and preland are drawn as assumptions (G);
  - screw element bores and cooling bores (G);
  - plus the new #9 and #10 noted above.

## 6. Second drafter update (2026-10-04, 23:40)
- Design frozen at parts.json 23:14 (187 parts, 72 connections); no die change coming. `make_all.py` now runs 9 sheets; verify 68/68; overlaps and frame check 0 on every sheet.
- New: `sheet08_utilities.py` (plan 1:25 from `path_mm`, trench lanes offset 7 mm, greedy route-id tags, sections A–D, 72-row connection table), `sheet09_bom.py` (full BOM, 12 pt, "Tờ" column from `balloon_index.json`; must run last).
- `sheet.py`: `N_SHEETS = 9`; `VP.draw(ghost=colour, z0=)` draws parts as grey outlines; `VP.breaks(*edges)` adds break lines (`drafting.break_line`).
- Sheet 05 die geometry (back face, adapter, bolt rows, manifold X) and the die stations on sheets 01/04 now come from parts.json. Body-bolt layout is a known simplification (note on B–B, design_issues #9); #10 motor shaft stub likewise.
- Sheet 07: box part numbers moved outside the top-left corner; stale cabinet numbers in box texts now computed from NUM.
