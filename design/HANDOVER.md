# Designer handover — ZE 155 A UT 34D + melt line + horizontal T-die

State at handover: 187 parts, 72 connections, `check_parts.py` PASS (0 errors). Builder phases 1 (drive + end
cabinet) and 2 (barrel, covers, vents, feeding, vacuum) are modelled or in progress; phase 3 (melt line + die) is in
progress. Any bbox change from now on must be reported to the orchestrator as a list of part ids.

## 1. Files and how to run
- `build_parts.py` — single source of truth. Writes `parts.json` and refills the generated blocks in `design.md`.
  `uv run -q python design/build_parts.py`
- `check_parts.py` — validator, stdlib only. `uv run -q python design/check_parts.py` (exit 1 on any error).
- `layout_preview.py` → `layout_preview.png`. `uv run -q --with matplotlib python design/layout_preview.py`
- `design.md` — Vietnamese user document. Inside `<!-- BEGIN PARTS -->…<!-- END PARTS -->` (§5, per-part blocks)
  and `<!-- BEGIN CONNECTIONS -->…<!-- END CONNECTIONS -->` (§6.2 table) everything is generated: never edit there.
  All other sections (§0–4, §6.1, §6.3, §7–§10) are hand-written: edit design.md directly and keep them in sync.
- Change log of past rounds: design.md §10 (review-01), §10.1 (drafter issues), §10.2 (drawing review-01).

## 2. build_parts.py structure
- **Constants** (top): `AXZ=1200` (screw axis), `D=169`, `BAR` (6 sections), `JOINTS`, `R_BODY=260`, `R_FL=320`
  (flange Ø640), `R_HEAT=290`, `R_NECK=250`/`L_NECK=40` (relief neck), `R_JOINT=300` (stud+nut ring envelope),
  `PCD=560`/`N_BOLT=20`/`L_BOLT=164`, `FT=650` (frame top), `FY=1000`, `LIP_X=9576`, `ROLL_X=9776`, `ROLL_R=400`.
  Also `COL` (palette by material name) and `GROUPS` (group → Vietnamese title; group → collection `ze155_<group>`).
- **Helpers:** `r1`, `bb(x0,x1,y0,y1,z0,z1)`, `cylx/cyly/cylz` (cylinder bboxes), `pipe_bb(path,r)` (exact
  perpendicular extents), `pipes_bb(paths,r)`, `lp(path)` (round to lists), `arc(R,a0,a1,n,cy,cz)` (2D arc points),
  `prof_flanged(L,R,r,t)`, `c_ring_outline` (unused since C-clamps were removed).
- **Sections** (comment banners): BASE AND SUPPORTS, DRIVE, BARREL, FEED, VACUUM, MELT LINE, DIE, CONTROL,
  UTILITIES, CONTEXT, CONNECTIONS, WRITE.
- **Part:** `add(id, group, name_vi, name_en, function, shape, bbox, material, connects, source, details, col=None, **kw)`.
  `connects` = list of `(target_id, interface_text, (x, y, z))`; the point must lie on/in BOTH bboxes (±5 mm).
  `center_mm` defaults to the bbox centre. Extra geometry goes in `**kw`: `axis`, `radius_mm`, `length_mm`,
  `profile_mm` ([[r, h]], h from the bbox face at the axis-min end), `outline_mm` ({plane XZ|YZ|XY, pts, d0, d1,
  closed}), `path_mm`, `paths_mm`, `count`, `pitch_mm`, `positions_mm`, `item_mm`, `item_axis`, `item_axes`,
  `item_length_mm`, `beams_mm`, `width_mm`.
- **Repeated item:** `count=n, positions_mm=[centres], item_mm=[dx,dy,dz]` (axis-aligned item size). When
  `item_axis` (one axis for all, e.g. `die_thermal_bolts`) or `item_axes` (one per item, e.g. `barrel_thermocouples`)
  is given, `item_mm = [Ø, Ø, length]` in the item frame. The bbox is the union of all items.
- **Pipe:** `shape="pipe"`, `path_mm` + `radius_mm`; bundles (`count>1`) use `paths_mm`, one polyline per hose;
  bbox from `pipe_bb`/`pipes_bb`. Declare the path once as a module constant (e.g. `VP3 = [...]`) and reuse it in
  `connects` endpoints.
- **Connection:** `con(id, from, to, medium, type_text, path)`; first point inside `from` bbox, last inside `to`
  bbox. Media: melt, water, vacuum, oil, hydraulic, power, signal, material, mechanical, air. `CAB` = entry point in
  the control cabinet, `DRV` = entry point in the MV drive cabinet.
- **WRITE:** `META` (units, axes, conventions, groups, palette), `main()` writes parts.json then `write_md()`
  (`part_md` renders each part block).

## 3. check_parts.py rules
1. Schema: required fields (`id, group, name_vi, shape, bbox_mm, material, colour_hex, connects_to, source`),
   snake_case unique ids, ordered bbox, shape/axis/plane enums, #RRGGBB, `center_mm` inside bbox, outline/path/
   paths/positions/beams inside bbox, `item_axis(es)` unit vectors.
2. C1 rules: `count>1` needs `positions_mm` (or `pitch_mm+start_mm+axis_dir`); every pipe needs `path_mm`; a pipe
   with `count>1` needs `paths_mm` with exactly `count` paths; tilted items are bbox-checked through their axis.
3. Every `connects_to` target exists; `at_mm` lies in both bboxes (±5); bboxes ≤ 5 mm apart.
4. Nothing floats: z0 = 0 or touches a part, and every part is reachable from the floor via touching bboxes.
5. Connections: ids unique, from/to exist, path endpoints inside the from/to bboxes.
Prints the envelopes: machine without context 15 600 × 7 900 × 6 300; full line 18 200 × 7 900 × 6 300.
Bbox checks are coarse; for real clashes I used ad-hoc sampled scans (pipe centrelines vs bboxes, pipe-pipe
distance, die outline vs roll circle). Re-run something similar after geometric edits.

## 4. Fixed interfaces (already modelled — do not move)
- Axes: X flow, X=0 = B1 drive-side face; +Y operator; Z=0 floor; screws Y ±71, Z 1200; front view from +Y.
- Drive (phase 1): motor X −4975…−2950 (AMI 450L4, shaft Z 1200, top 2610, IC81W cooler on top), motor base
  Z 650–750, couplings −2950…−2300, guard −2980…−2300, gearbox −2300…−750 (Z 650–1720, Y ±700), lantern −750…0,
  lube unit X −3600…−2450 on +Y, base frames X −5150…330…5950 (top Z 650, Y ±1000), end cabinet X −5650…−5150.
- Barrel (phase 2): B1 0–676, B2–B6 6D to 5746; joints at 676/1690/2704/3718/4732 (20 × M24, PCD 560, flanges
  Ø640, relief neck Ø500 × 40); **B6 flange face X 5746**; supports at 1183/3211/5239; covers C6…C1 1690–5760;
  dome zone 1 X 1950–2350 (B3), dome zone 2 X 3800–4440 (B5); feed throat X 90–590; mezzanine deck top Z 3000.
- Melt line (phase 3), all coaxial at **Z 1200**: head 5746–5996, diverter 5996–6446, SC inlet 6446–6596,
  screen changer 6596–7301, pump inlet 7301–7476, pump 7476–7926, outlet 7926–8076, pipe 8076–8426, mixer
  8426–8926, die adapter 8926–9126, **die back face X 9126**, **die lip X 9576, Z 1200**.
- Rolls: centres X 9776, Z 799/1601/2403, R 400; **nip middle/bottom at Z 1200**; air gap 200 (set hot).
- Rear layout: cabinet fronts Y −3700; vacuum separator (4120, −2700); trench Y −1250…−1050 up to X 8700.

## 5. Die internals as defined now
- Bodies: upper `die_body_upper` Z 1200–1450, lower Z 950–1200, X 9126–9576, Y ±1300; end plates ±1300…±1375.
  Section outline (XZ): top face X 9126–9330 at Z 1450, chamfer (9330,1450)→(9446,1290)→ lip (9576,1208);
  lower mirror to (9576,1192).
- Inlet: `melt_die_adapter` rectangular flange 500 × 360 at X 9126, bore Ø100 at Y 0, Z 1200, into the manifold.
- Manifold, preland, lip land: only the drafter's assumed values (sheet 05, flagged G): coat-hanger Ø72 → Ø28,
  centred near X ≈ 9200 at Y 0; preland gap 3–6; lip land ≈ 156. Not in parts.json.
- Choker (restrictor) bar inside the upper body X 9240–9270; 33 vertical choker bolts at X 9255, Y −1200 + 75k.
- Thermal-bolt rail (cable + air duct) on top face X 9285–9345, Z 1450–1540.
- Hinge slot: open, full width, X 9392–9404 from the chamfer down to Z 1212 (12 mm web); `die_flex_lip` =
  X 9404–9576; 94 thermal bolts along the chamfer, axis (9440,y,1295)→(9342,y,1434), tips 36 mm past the web.
- Lower lip: replaceable insert X 9446–9576, 60 high, 24 × M12.
- Body bolts `die_body_bolts` (94 × M30 SHCS, flush counterbores Ø48 × 32, pitch 110): top face rows X 9160
  (Y −1265…) and X 9210 (Y −1210…); bottom face rows X 9160 (Y −1210…) and X 9270 (Y −1265…).
- **Open issue:** at 450 mm depth the bolt rows (X 9160/9210/9270) cross the manifold band (≈ X 9164–9236 at the
  centre) and leave a thin back land; the internals cannot be consistent. Fix option: deepen both bodies backwards
  to ≈ X 9060. Parts that would move: `die_body_upper/lower` and `die_end_plate_op/rear` (X0), `die_heater_boxes`
  (to ≈ 8984–9060), `melt_die_adapter` (shorten to 8926–9060 to keep the mixer fixed, or shift the melt line),
  `melt_sensor_die` (on the adapter), `die_body_bolts` (rows move back), `die_heater_conduit` and
  `die_cable_harness` start points, connection `melt_07`, possibly `die_cart` uprights (X 9150–9350). Not done
  because phase 3 is modelling the die; needs an orchestrator decision.

## 6. Open issues (design.md §9 and reviews)
1. Gearbox maker and input-shaft height: no source; input set coaxial at Z 1200.
2. Machine-end cabinet: floor-standing 500 × 1000 × 2000, while page 9 shows a 430 × 1380 block off the floor;
   review-01 M11 not applied (phase 1 built).
3. Drive train ≈ 10 720 mm motor-NDE → barrel end vs ≈ 10 000 implied by the KM table (+7 %); review-01 M2 not
   applied (separate flex + safety couplings 650, lantern 750).
4. Vacuum sizing for undried PET at 3.5 t/h: assumed two zones (≈ 50 mbar B3, 5–20 mbar B5), Roots ≈ 2 000 m³/h
   + dry screw ≈ 400 m³/h; c062 low confidence.
5. Air gap 200 mm, larger than typical for PET (50–150); accepted in DECISIONS 11.
6. Die internals vs 450 mm body depth (§5 above).
7. Drafter items still drawing-only or partly open: die internals (#4); flange table now in design.md §6.3 and in
   `melt_0x` types; screw element table now in `screws.details`. Drawing review-01 items C1, C2, I1, I7–I10,
   M4–M7 belong to the drafter.
8. Nut access at barrel joints relies on the Ø500 relief neck (12 mm socket clearance) with heater shells removed.

## 7. Practical notes
- Patch `build_parts.py` with exact-string replacements that assert one match; rerun build + check after each.
- Before a geometry change, snapshot parts.json and diff bbox/positions afterwards to report changed ids.
- Keep `function`/`details` Vietnamese; ids ASCII snake_case with a group prefix.
