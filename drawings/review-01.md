# Drawing review 01: sheets 01–07 (ZE 155 A UT 34D + melt line + horizontal T-die)

Independent review of `drawings/sheet-01-ga` … `sheet-07-process-utilities` (PNG and SVG text), `drawings/README.md`, checked against `design/parts.json` (182 parts, 59 connections).

**Method.** I viewed each sheet whole, then cropped it at full resolution. I extracted balloon numbers and dimension strings from the SVG `<text>` elements, and spot-checked 15 dimensions against `parts.json` with a read-only script. I also read the drawing scripts to see which part ids each view draws.

**Coordinates.** Zones use the sheet border grid: columns 1–8 and rows A–F on A1 (columns 1–12, rows A–H on A0). "px" means pixel coordinates `(x0–x1, y0–y1)` in the sheet PNG.

**Scale of the findings.** 2 Critical, 10 Important, 8 Minor.

---

## Critical

### C1. The melt path is broken at the die inlet in both die sections
- **Where:**
  - sheet 05, section A–A, zone B5–B6 (px 3830–4200, 980–1330);
  - sheet 05, section B–B, zone D2 (px 1550–1630, 2540–2600).
- **What is wrong:**
  - **In A–A:**
    - The cross-hatched block behind the die (labelled "bích + hộp nối nhiệt", the `melt_die_adapter` cut at Y = 0) is drawn solid. There is no Ø100 bore through it.
    - The inlet into the manifold is drawn as a small open pocket in the lower half only, about 37 × 50 mm below Z 1 200. Above it is a hidden-line rectangle in the upper half.
    - So the melt cannot get from the adapter into the Ø72 manifold. Because the section is at Y = 0, the inlet should appear as a symmetric open channel.
  - **In B–B:**
    - The "cửa vào Ø100 từ bích chuyển" is drawn as a **hatched** (solid) square.
  - **Effect:** the melt path is continuous from barrel to static mixer on sheet 04, but it stops at the die back face in both die sections. This is the one connection that the brief's "melt path continuous to the die lip" depends on.
- **Fix:**
  - **A–A:** draw the adapter bore Ø100, symmetric about Z 1 200 (±50), unhatched, through the adapter flange (`melt_die_adapter`, X 8 926–9 126). Continue it as an inlet throat into the manifold, with half in each die body. Leave out the asymmetric pocket and the hidden box.
  - **B–B:** show the inlet as an open (white) channel that joins the manifold at Y = 0.
  - **Sheet 04, view A:** add the die back face, so that the hidden channel line visibly runs into the die.

### C2. The melt-line flange specifications contradict `parts.json` and sheet 02
- **Where:** sheet 04, view D "Mối nối mặt bích", zones B3–C5. Compare with:
  - sheet 02, Detail B, flange view and note 2 (zones A6–B8, C5);
  - `parts.json`: connections `melt_01` and `melt_02`, and part `melt_head_adapter.details`.
- **What is wrong:**

  | Joint | Sheet 04 says | `parts.json` / sheet 02 say |
  |---|---|---|
  | B6 → head adapter (X 5 746) | 16 × M36 on PCD 540 | 20 × M24 studs on PCD 560 (`melt_01`, head-adapter details, sheet 02) |
  | Head adapter → start-up valve | 12 × M30 on PCD 370 | 12 × M24 screws fitted from the valve side (`melt_02`, valve counterbores) |

  - The same joint therefore has two different bolt patterns. The builder works from `parts.json`, so the 3D model and the drawing will disagree.
  - All six melt flanges are shown only as face views. No section shows flange thickness, centring spigot or recess, seal ring, bolt length or the heater band. As a result the requirement "flanges shown connected in detail" is met only for the barrel joints.
- **Fix:**
  - Take the values from `parts.json`, i.e. 20 × M24 / PCD 560 / Ø600 and 12 × M24 into the Ø420 face. Alternatively, change `parts.json` and sheet 02 together. Either way, keep one source.
  - Add one typical melt-flange half-section at 1:2 or 1:5, for example pump → P4 adapter. Show the spigot, seal, stud and nut, the heater band, the sensor port and the PCD.

---

## Important

### I1. The barrel cooling-water circuit is not drawn or identified on any scaled sheet
- **Where:**
  - sheet 02, view A, zones A1–B4;
  - `sheet02_barrel.py` `IDS_ELEV0` leaves out `barrel_cw_*`.
- **What is wrong:**
  - **Not drawn at scale, never ballooned:**
    - `barrel_cw_return` (51);
    - `barrel_cw_valves` (52): 6 stations, each with ball valve, Y-strainer, solenoid valve, throttle and flow indicator;
    - `barrel_cw_hoses` (53): 12 hoses to the 45° fittings at X = start + 200 / end − 200.
  - **Never ballooned:** `util_cw_motor_hoses` (164), `util_cw_throat_hoses` (165), `util_cw_sidefeed_hoses` (166) and `util_cw_vac_hoses` (167).
  - The water path therefore exists only as NTS boxes on sheet 07, and on sheet 02 as note 7. Barrel temperature control (heating plus solenoid cooling per zone) is operation-critical.
- **Fix:** on sheet 02, rows D–F are empty and can take this.
  - Add a front-elevation strip at Z 600–1 100, without covers. Show supply and return manifolds, the 6 valve stations and the 12 hoses running to the fittings. Balloon 50–53, 165 and 166.
  - Add a small section through one fitting, at 45° lower +Y through the heater-shell notch.
  - Add a one-zone schematic: supply → ball valve → Y-strainer → solenoid (from the zone controller) → bores → throttle → flow indicator → return, with the thermocouple and heater of that zone.

### I2. Interlocks and safety wiring are missing, and e-stop coverage is thin
- **Where:**
  - sheet 07, power/signal lane, zones F1–G12;
  - sheet 03, coupling labels, zone A5–A6;
  - sheet 04, sensor table, zone D3–E4;
  - `parts.json` connections.
- **What is wrong:**
  - **No link between control cabinet 148 and MV drive cabinet 147.** Neither the drawings nor the connections list contain one.
    - The e-stop chain (`s_06`, `s_09`) ends at 148.
    - P1 "ngắt ≥ 350 bar" has no path to the main drive.
  - **Rupture discs:**
    - Rupture disc 1 (100) has no signal at all.
    - The sensor table gives "Nối –" for rupture disc 2, although `s_08` exists.
  - **Switches named on sheet 03 have no signal line anywhere:**
    - torque-limiter switch ("công tắc giám sát");
    - coupling-guard interlock;
    - lube pressure switch and PT100.
  - **No incoming MV/LV power feed** is shown.
  - **E-stops:**
    - The design text puts extra e-stops on the HMI, machine cabinet 150 and die box 145. None of these is drawn.
    - The three line e-stops sit at X 600 / 3 700 / 5 700. There is none on the operator side of the melt line (screen change, X ≈ 6 900–7 200, +Y) or at the die and deckles (X ≈ 9 300, +Y). Die box 145 is on −Y.
- **Fix:**
  - Add connections, and draw them on sheet 07:
    - 148 ↔ 147: fieldbus plus hard-wired STO (safe torque off);
    - 15, 17 and the lube PS/PT100 → 148/150;
    - 100 / 122 burst signals and P1 HH → 147 trip.
  - Add a plant infeed (MV and LV).
  - Add a cause-and-effect table (trip → action).
  - Add e-stop pushbuttons at about (7 000, +Y) and (9 300, +Y). Draw and balloon the ones on 145, 150 and 152, and dimension all e-stop positions on the GA.

### I3. The P3 control loop is implausible for a starve-fed twin-screw extruder
- **Where:** sheet 04, sensor table, row P3 "≈ 50 bar → vòng tốc độ vít", zone D3–E4. The same logic appears on sheet 07.
- **What is wrong:** throughput is set by the loss-in-weight feeders. Screw speed only changes the degree of fill, so a loop from P3 to screw speed does not hold the pump inlet pressure in steady state.
- **Fix:** use one of these two options:
  - P3 → gear-pump speed, with the feeders fixing the rate;
  - P3 → total feeder rate (main plus additive, ratio-locked), with the pump fixing the output to the die.

  State which option is used, and draw the loop (PT-P3 → PIC → feeder or pump drive) on sheet 07.

### I4. The T-die has no body bolts holding the two halves together
- **Where:**
  - sheet 05, section A–A, zones A5–B5;
  - sheet 05, view A;
  - `parts.json` `die_body_upper` and `die_body_lower` (no bolt part exists).
- **What is wrong:**
  - The split plane at Z 1 200 has nothing clamping it. The circles in A–A are cartridge-heater holes.
  - Separating force is roughly 2.4 m × 0.3 m × 10 MPa ≈ 7 MN. That needs about 2 rows of M30 bolts at about 100 mm pitch.
  - The layout also leaves only about 38 mm of land behind the Ø72 manifold, which is centred at X ≈ 9 200, to the back face at X 9 126.
- **Fix:**
  - Add part `die_body_bolts`: 2 rows of M30 10.9 through the lower body into the upper. One row goes behind the manifold, and one between the manifold and the choker slot (X 9 240).
  - To make room, deepen the die backwards to about X 9 060, or move the manifold forward.
  - Show the bolts in A–A as cut studs and the bolt heads in view A.

### I5. The flex-lip hinge is drawn as a closed internal pocket, so the lip cannot flex
- **Where:**
  - sheet 05, A–A, zone B4–B5 (px 3330–3800, 820–1140);
  - `die_flex_lip`.
- **What is wrong:**
  - The "rãnh bản lề (hinge groove)" is a closed rectangle at X ≈ 9 416–9 427, Z ≈ 1 237–1 291. The outer chamfer surface at that X is at Z ≈ 1 326, so the groove does not break out anywhere. There is no thin web, and it cannot be machined.
  - The thermal-bolt push point, (9 440, 1 295) from `item_axis`, sits at the groove corner. That leaves almost no lever arm.
- **Fix:**
  - Draw the hinge as an open slot cut from the chamfer (or top) face, leaving a web of about 8–12 mm above the lip flow surface.
  - Put the bolt bearing point at least 30–40 mm downstream of the web.
  - Add the lip-gap symbol "0,5–2". Update the `die_flex_lip` and `die_body_upper` outlines to match.

### I6. The barrel flange bolt circle leaves a 7 mm ligament and no wrench access
- **Where:**
  - sheet 02, Detail B (zone A6–B6);
  - sheet 02, "Mặt bích nhìn dọc trục" (zone A8–B8);
  - sheet 02, note 2.
- **What is wrong:**
  - Ø26 holes on PCD 560 in a Ø600 flange leave 7 mm of material to the outside diameter.
  - The nut corners at r 262–298 are 2 mm from the Ø520 barrel body and 2 mm inside the flange edge.
  - No socket or ring spanner fits, so the 20 studs cannot be tightened to the 200 kN each that is claimed. Note 2 itself says that M30 "chạm thân".
- **Fix:**
  - Enlarge the flange to about Ø680 with PCD 610 (ligament about 22 mm), or neck the barrel body down near the flange.
  - Change the `barrel_joint_*` and `barrel_b*` bbox to ±340.
  - Redraw Detail B with a socket clearance envelope, and update the flange face view.

### I7. The coupling train is not connected, and the lantern/spline connection is not drawn
- **Where:**
  - sheet 03, "Khớp nối – nửa mặt cắt", zones A5–B6 (px 3950–4950, 130–1000);
  - sheet 03, front view, lantern zone A2–B3.
- **What is wrong:**
  - The label says "đầu trục động cơ Ø140 × 200", but the motor shaft is drawn as a stub of about 50 mm that ends at the face of the flex-coupling hub. The hub bore is empty, so the motor shaft does not engage the coupling.
  - The connection from gearbox output shafts through spline couplings to the screw shanks (`m_01` "then hoa"), together with the gearbox thrust bearing, is shown only as hidden lines. It is a key mechanical connection and has no detail view.
- **Fix:**
  - Redraw the motor shaft running 200 mm into the hub, with a key or shrink fit. Show both hubs on their shafts.
  - Add a lantern section at 1:5: two output shafts at a = 142, spline sleeves, screw shanks, lantern window and drain, and the thrust-bearing location.
  - Add a detail marker on the front view where the coupling section is taken.

### I8. Utility runs (cables, air, trenches) are claimed but not drawn
- **Where:**
  - sheet 07, note 4 (zone D10);
  - the balloon sets of sheets 01–06.
- **What is wrong:**
  - Note 4 says "Đường đi thật (path_mm) … vẽ trên tờ 01–06". No sheet script draws the connection `path_mm` routes:
    - power `p_*`;
    - signal `s_*`;
    - air `a_*`.
  - **Never ballooned anywhere:**
    - trenches `ctrl_floor_duct` (155), `ctrl_trench_die_branch` (158) and `ctrl_trench_mv` (159);
    - air `util_air_hose_die` (170) and `util_air_drop_2`…`util_air_tube_loader` (171–174);
    - `die_heater_conduit` (142);
    - vacuum gauges 86 and 91.
  - **Effect:** cable, air and signal runs are not shown "ending at parts" on any sheet.
- **Fix:**
  - Add a utilities routing plan at 1:50: A1, or use the empty right half of sheet 06.
  - Draw it from `connections[].path_mm`, colour-coded per medium, with every util_/ctrl_ trench, hose and drop ballooned.
  - Add a utility connection schedule: point, X/Y, size, pressure, flow, kW.
  - Correct note 4.

### I9. Text is far below print size, and large areas of the sheets are empty
- **Where:** all sheets. Font sizes from the SVGs:

  | Sheet(s) | Font size | Font size in mm | Cap height |
  |---|---|---|---|
  | GA, most text (BOM, balloons, dimensions) | 5.5 pt | 1.9 mm | ≈ 1.4 mm |
  | Sheets 02–06, most text | 4.6–4.9 pt | — | ≈ 1.2 mm |
  | Sheet 07, connection table | 3.6–4.3 pt | — | ≈ 0.9 mm |

- **What is wrong:**
  - ISO 3098 / ISO 7200 practice for A0/A1 asks for 2.5 mm minimum for dimensions and notes, and 3.5 mm for titles and numbers. Printed at size, the BOM and most leader labels are unreadable.
  - **Empty areas:**
    - sheet 02, rows D–F, except the cover table;
    - sheet 03, rows D–F;
    - sheet 05, rows E–F;
    - sheet 06, right half rows C–E;
    - sheet 07, bottom quarter.
- **Fix:**
  - Set a minimum of 7 pt (2.5 mm) for notes, dimensions and tables, and 8–9 pt for balloons.
  - Move the 182-row BOM to its own sheet, or split it per sheet.
  - Use the empty areas for the new views from C2, I1, I4 and I7.

### I10. Sheet 07 is a block diagram, not a P&ID
- **Where:** sheet 07, whole sheet. The process lane is at zones C1–C10 (px 150–6150, 1250–1850).
- **What is wrong:**
  - There are no valve, pump or instrument symbols and no instrument tags (PT-101, TT, PSH, LSH).
  - Process boxes are placed about 15 px apart, so the melt connections between them are invisible stubs with truncated labels ("elt_").
  - Power and signal lines are bundled on shared buses, so individual runs cannot be followed.
  - The hydraulic circuit (HPU → directional valves → screen-changer actuator / start-up cylinder) is two unlabelled lines.
- **Fix:**
  - Use ISO 10628 / ISA 5.1 symbols. Show valves on water, vacuum, oil and air lines, and draw instruments as bubbles with trip setpoints (P1 HH 350, P4 HH 250, rupture disc 400).
  - Leave at least 25 mm between process boxes and print full connection ids.
  - Route each signal and power line separately, or with line numbers.
  - Add a small hydraulic schematic.

---

## Minor

### M1. The vacuum line downstream of the separator is undersized
- **Where:** sheet 06, schematic G, zone E3–E7.
- **What is wrong:** zone 2 enters the separator in DN150, but the outlet to the 2 000 m³/h Roots pump is DN100 (`vac_pipe_2`, OD 120). That gives about 70 m/s at the outlet and a large conductance loss at 5–20 mbar.
- **Fix:** use DN150–200 from the separator to the Roots pump, matching the pump inlet flange.

### M2. Lube schematic elements are missing
- **Where:** sheet 03, lube schematic, zone B5–C7.
- **What is wrong:**
  - There is no pressure-relief valve on the pump and no suction strainer.
  - The pressure switch and PT100 appear as text only, not as symbols on the line.
  - The cooler water side has no valve.
- **Fix:** add these elements as symbols, and link the pressure switch to the drive start interlock (see I2).

### M3. Detail D die-nose outline is duplicated and overruns into the notes
- **Where:** sheet 05, Detail D, zones C4–E6. The lines end at px (4285, 3140), touching the "Ghi chú" block.
- **What is wrong:**
  - Two die-nose outlines are superimposed, one straight and one with the kink.
  - The outline lines are not clipped to the detail and run into the notes.
  - A–A labels a "môi dưới thay được" that is not drawn as a separate part.
- **Fix:** draw a single nose profile from the `die_body_*` outlines, clipped to the detail circle. Show the lower lip as a separate bolted insert, or drop the label.

### M4. Views are cut at their frames without break lines, and some scales are missing
- **Clipped views:**
  - sheet 03, front view and plan: left edge at px x ≈ 1 390;
  - sheet 04, view A: the screen changer is cut at Z ≈ 1 770 and the pump motor is cut too; both ends are cut;
  - sheet 04, views B and C: right edge at px x ≈ 1 830;
  - sheet 06, views C, D and E.
- **Missing scales:** the GA end views (sheet 01, zones A2 and A8) have no scale in their headings.
- **Fix:** add zig-zag break lines or extend the views. Add "1:50" to the end-view headings.

### M5. Text and leader collisions
- **Sheet 02:**
  - B3: the screw-configuration labels "…chân không 1khối nhào 45°/5" run together;
  - B3: balloon 5 sits on the "1 014" dimension text;
  - C1: the Detail C heading overlaps "thân xi lanh R260 (phantom)".
- **Sheet 05:**
  - D3: the B–B labels "cửa vào Ø100…" and "…(manifold) Ø72 → Ø28" overlap;
  - B6: the A–A "500" is struck through by a hidden line;
  - B2–B3: "2 750 kể tấm đầu" is struck through by the cart plate.
- **Sheet 01:**
  - B8: "môi 2 400" in the die-end view sits on geometry;
  - row D: plan-view leaders cross (136/144, 117/118, 109–111, 84/92/157/90, 160/19/71).
- **Sheet 03, A4:** leaders 22/24/25 cross.
- **Shared leader starts:** sheet 02 Detail B and the sheet 03 coupling section start 4–5 leaders from one point. Which label belongs to which leader is ambiguous.
- **Sheet 04, B4:** "đĩa nổ phía −Y" text sits on geometry.
- **Fix:** run a label-collision pass, and use one leader per label with distinct start points.

### M6. Balloons and parts lists disagree per sheet
- **Listed but not ballooned:**
  - sheet 02: 6, 7, 35–38 and 50–53;
  - sheet 03: 164;
  - sheet 05: 139, 142, 168, 170, 125 and 126;
  - sheet 06: 86 and 91.
- **Ballooned but not listed:**
  - sheet 02: 4, 82 and 99;
  - sheet 03: 28, 50, 55, 161 and 162;
  - sheet 06: 28, 29, 41, 42 and 154.
- **BOM sheet references:** in the "tờ" column of the GA BOM, item 2 is given as "tờ 02,03,04" but is ballooned on none of them.
- **Fix:**
  - Make the per-sheet parts list equal to the set of balloons and text-labelled ids on that sheet.
  - Generate the BOM "tờ" column from the balloons actually placed.
  - Add an automated check next to `frame_check`.

### M7. Section A–A of the barrel and Detail B: drafting details
- **Where:** sheet 02, A–A (zones A4–B5) and Detail B.
- **What is wrong:**
  - **Nut leader:** the leader "20 đai ốc M24 trên PCD 560 (phía sau)" points to the heater ring, and the nuts are not drawn.
  - **Screw shafts:** in the transverse cut the shafts are left white; they should be hatched.
  - **Detail B:** the barrel body and its integral flange are separated by a full-depth line, yet share one hatch.
- **Fix:**
  - Draw the 20 nuts on PCD 560 behind the cut, as visible lines, and point the leader at one of them.
  - Hatch the shafts at a third angle.
  - Drop the body/flange line, or hatch the two as separate parts.

### M8. In the screw configuration, the melt seal sits under the vent opening
- **Where:** sheet 02, screw strip, zone B3.
- **What is wrong:** the KB 90° at X 1 960–2 030 lies under the upstream edge of vent 1 (dome X 1 950–2 350, opening about 1 990–2 310). The restrictive element should end upstream of the opening so that the melt seal isolates the vent.
- **Fix:** move the KB 90° to X ≈ 1 880–1 950, or add an LH element before X 1 950. Shift the kneading block accordingly.

---

## Good, keep
- **Dimensions match the data.** All 15 spot-checked dimensions agree with `parts.json`:

  | Dimension | Value |
  |---|---|
  | Machine length | 15 600 |
  | Line length incl. calender | 18 200 |
  | Overall width | 7 700 |
  | Overall height | 6 300 |
  | Motor | 2 025 |
  | Gearbox | 1 550 |
  | Coupling guard | 680 |
  | Screen changer | 705 |
  | Melt line | 3 380 |
  | Die incl. end plates | 2 750 |
  | Deckle span | 3 050 |
  | Die depth | 450 |
  | 34D | 5 746 |
  | Support height | 384 |
  | Platform | 4 550 |

  Generating every sheet from one data file works. Keep it, and extend it to the flange specs (C2).
- **First-angle projection is consistent on every sheet:**
  - front view from +Y with the die on the left;
  - plan below, with +Y at the bottom;
  - drive-end view on the left and die-end view on the right.

  The projection symbol is in every title block.
- **Markers match their sections:**
  - sheet 02: A–A at X 2 984 in B4, B on the joint at X 2 704, C on support 2;
  - sheet 05: A–A at Y = 0 and B–B at Z 1 200, with the correct viewing arrows.
- **Sheet 04, view A:**
  - the melt channel is continuous in hidden line from the figure-8 bore through Ø120 to Ø100;
  - P1–P5/T and both rupture discs are placed at stated X;
  - the station dimension chain sums correctly to 3 380.
- **Sheet 02, section A–A:**
  - the 2-flight Erdmenger profiles are correctly phased 90°;
  - a = 142 and the bore is 311 × 169;
  - Do/Di = 167,5/114,6 = 1,46.

  The barrel layout, the zone table aligned in X and the screw strip at the same X scale read well.
- **T-die:**
  - 94 thermal bolts × 25,4 ≈ the 2 400 lip;
  - 33 choker bolts × 75;
  - heater-zone table;
  - coat-hanger B–B;
  - die cart with rails and height adjustment;
  - Detail D die-to-nip geometry. I re-checked it from the `die_body_upper` outline and the roll centre (9 776, 1 601, R 400): about 75 mm from the die chamfer to the middle roll. The data gives about 20 mm at the bolt heads.
- **Feed and side feeder:**
  - feed chute view C shows the whole chain: feeder → sleeve → 45° downpipe → flex sleeve → hopper → throat → B1;
  - side-feeder view D shows B2 → adapter → ZSB → gearbox → motor → cart.
- **Vacuum:** the two zones are explained clearly in view F, schematic G and the notes. Throttling zone 1 to about 50 mbar into a shared 5–20 mbar separator is sound logic.
- **Title blocks and BOM:**
  - title blocks are complete: scale, n/7, date, projection, revision row, "G" assumption flag;
  - the BOM is complete at 182 rows, with material and quantity;
  - line types are consistent, with phantom for context.
