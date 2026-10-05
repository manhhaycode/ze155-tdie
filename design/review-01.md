# Design review 01: ZE 155 A UT 34D + melt line + horizontal T-die

Reviewer: independent, fresh eyes. Scope: `design/design.md`, `design/parts.json` (161 parts, 47 connections), checked against `research/` (specs, claims, pdf_measures, pdf_catalog, web photos, pdf crops) and `design/layout_preview.png`. No design file was edited.

Method: I read everything listed above. I ran `check_parts.py` (PASS). I also wrote three read-only scripts over `parts.json`: pairwise bbox overlap of unconnected parts, pipe centrelines against part bboxes, and pipe-to-pipe distances. On top of that I checked the die-to-roll geometry by hand against the actual `outline_mm` polygons, not the bboxes. Most bbox overlaps are intended (covers around barrels, couplings inside their guard, railing around the feeders). The findings below are the real ones.

Totals: **1 Critical, 8 Important, 11 Minor.**

---

## Critical

### C1. Repeated and pipe entries have no geometry the builder can place. `check_parts.py` does not catch this.
**Parts:** `barrel_cw_hoses`, `melt_heater_bands`, `barrel_thermocouples`, `melt_sensor_head`, `melt_sensor_die`, `die_thermal_bolts`, `die_choker_bolts`, `die_lifting_lugs`, `die_deckles`, `die_cart_rails`, `melt_pipe_saddles`, `ctx_roll_drives`, `ctx_roll_rails`; also `melt_hyd_hoses_sc`, `melt_hyd_hoses_suv` and `util_cw_lube_hoses` (count 2, one shared path).

**Problem:**
- `meta.conventions` says repeated items carry `positions_mm` and `item_mm`. The 16 entries above have `count` set but no positions.
- `barrel_cw_hoses` has `shape: pipe` with **no `path_mm` at all**. It is the 12 hoses that design.md §8.13 lists as a recognition feature.
- `melt_heater_bands` (13 bands) has only a group bbox, X 5806–9126. The overlap script places "bands" inside the screen changer, the pump and the die heater boxes.
- `die_lifting_lugs` asks for "2 per end plate", but its bbox (X 9150–9230) holds only one per plate.
- `barrel_thermocouples` puts the B1 couple at (338, 0, 1455–1545). That point is inside `feed_throat` (X 90–590, Y ±210, Z 1455–1640), i.e. inside the feed opening.
- `check_parts.py` only checks `positions_mm` when the key exists (line 135), so all of this passes.

**Fix (in `build_parts.py`, then rerun):**
- **`check_parts.py`:** make it an error when `count > 1` has neither `positions_mm` nor `pitch_mm` + `start_mm` + `axis_dir`, or when a `pipe` has no `path_mm`. For hose bundles, give one path per hose, offset ±40 mm.
- **`melt_heater_bands`:** `positions_mm` along Y = 0, Z = 1200, with item width 60–90 and a cut-out under each sensor port:
  - head adapter X 5836, 5906;
  - `melt_sc_adapter_in` X 6521;
  - `melt_pump_adapter_in` X 7388;
  - `melt_pump_adapter_out` X 8001;
  - `melt_pipe` X 8160, 8250, 8340;
  - `melt_static_mixer` X 8500, 8620, 8740, 8860;
  - `melt_die_adapter` X 9000.

  The 7 bands on the pipe and mixer sit under the Ø300 cladding. Model them as cladding plus one terminal box each, not as visible rings.
- **`barrel_thermocouples`:** B1 at (338, −200, 1366), 45° upper −Y quadrant, clear of the throat. The others on top at X 1450, 2450, 3211, 4600, 5239, Z 1460–1545, item [30, 30, 90].
- **Sensors:** `melt_sensor_head` [[5876, 0, 1557], [5916, 0, 1557]]; `melt_sensor_die` [[9006, 0, 1497], [9046, 0, 1497]]; item [40, 40, 285/245].
- **`die_thermal_bolts`:** Y = −1181 + 25.4·k (k = 0…93). Axis from (9440, y, 1295) to (9342, y, 1434), which is 35° from vertical and 170 mm long.
- **`die_choker_bolts`:** Y = −1200 + 75·k (k = 0…32), X 9185.
- **`die_lifting_lugs`:** (9190, ±1337, 1515) and (9470, ±1337, 1515). Widen the bbox to X 9150–9510. At \|Y\| 1337 they are outside the roll face (±1300) and in front of the journals (X ≥ 9626).
- **`die_deckles`:** (9480, ±1450, 1200).
- **`melt_pipe_saddles`:** [[8250, 0, 1010], [8676, 0, 1010]], item [150, 240, 80].
- **Context:** `ctx_roll_drives` at (9776, −2050, 799 / 1601 / 2403); `ctx_roll_rails` at Y ±1550; `die_cart_rails` as in I3.
- **`barrel_cw_hoses`:** 12 paths as in I1.

---

## Important

### I1. Cooling-water fittings sit exactly where the barrel saddles are. There is no bare barrel surface left for them.
**Parts:** `barrel_cw_hoses`, `barrel_b2`/`b4`/`b6` connects_to (X, 0, 940), connections `w_02`, `w_03`, `barrel_support_1..3`, `barrel_heater_shells`.

**Problem:**
- The hose couplings for B2, B4 and B6 are at (1183 / 3211 / 5239, 0, 940): the bottom of the barrel at mid-section.
- That is the same point where `barrel_support_1..3` contacts the barrel. The saddle cradle covers Y ±200 up to Z 1034, and design.md says its 70 mm pad bears on the 74 mm bare band.
- `w_03` runs straight through `barrel_support_2` (14 samples).
- The rest of the barrel surface is also taken. The heater shells start 90 mm from each face, the joint nuts reach 82 mm (50 flange + 32 nut), and the middle band belongs to the saddle.
- Photo web-02 (ZE 110 R) shows where real fittings go: on the lower sides near the section ends, through notches in the heater shells, never under a saddle.

**Fix:**
- **Fittings:** two per 6D section at X = start + 200 (in) and end − 200 (out), on the +Y lower quadrant at (Y 184, Z 1016), i.e. 45° below horizontal. Cut a 50 mm notch in the heater shell at each. B1 keeps its two bottom fittings at X 200 and 476 (B1 has no saddle).
- **Hose path:** valve top (Xc ± 40, 910, 1000) → (X_fit, 560, 980) → (X_fit, 230, 1000) → fitting. It passes the cover wall at Y 480, Z ≈ 990, through the lower removable panel.
- **B2 outlet check:** the outlet at X 1490 stays 70 mm below and outside `sidefeed_adapter` (Z ≥ 1040, Y ≥ 250).
- Update `w_02`/`w_03` and the barrel connects_to points to match.

### I2. Rear side (−Y): walkways of 200–500 mm, cabinets with no door space, and the stair blocking the motor.
**Parts:** `feed_stair`, `ctrl_drive_cabinet`, `ctrl_heater_cabinet`, `feed_platform_columns_rear`, `vac_pump_unit`, `vac_control_box`, `vac_pipe_support`, `melt_hpu`, `ctrl_cable_mv`.

**Problem (clear widths measured from `parts.json`):**

| Location | Clear width | Requirement |
|---|---|---|
| Frame edge Y −1000 → stair Y −1450, along the motor | 450 mm | |
| MV cable riser (Y −1100) → stair, in front of the MV terminal box | **350 mm** | an MV box needs ≥ 1 m working space |
| Drive cabinet front Y −2500 → stair outer edge Y −2150 | **350 mm** | 6-section MV drive; door swing alone is 600 mm |
| Heater cabinet front Y −2500 → rear column at Y −2300 | **200 mm** | |
| Frame → vacuum skid at Y −1500 | 500 mm | |
| Frame → `vac_control_box` (Y −1300, X 5900–5950) | **300 mm** | |

- The MV cable also lies on the floor across the walkway (`ctrl_cable_mv` at Z 40).
- No real line has these clearances. Plant practice is ≥ 1 000 mm in front of cabinets and ≥ 800 mm for maintenance passages.
- The plan view of `layout_preview.png` shows the clutter.

**Fix:**
- **Mezzanine:** move the rear deck edge to Y −2700 and the rear column row to Y −2600. The deck becomes 4 100 deep.
- **Stair:** move to Y −2650…−1950, keeping the landing at X −2700. That gives 850 mm to the MV riser and 950 mm to the frame.
- **Cabinets:** put the door fronts at Y −3700 (drive Y −4900…−3700, control Y −4300…−3700). That gives ≥ 1 000 mm to the stair and the columns.
- **Vacuum:** skid to Y −3300…−2200, separator centre to Y −2700, `vac_pipe` down-leg to Y −2700, support post to Y −1900. That gives 1 200 mm along the barrel.
- **HPU:** to Y −2700…−2000.
- **MV cable and floor duct:** run them in a covered floor trench, flush galvanised cover 400 wide, like `ctrl_floor_trench`, not on the floor.
- **Floor:** extend `ctx_floor` to Y −5500. The operator side stays unchanged.

### I3. Die cart: 160 mm track under a ≈ 3.4 t die, with the centre of gravity 1.1 m up.
**Parts:** `die_cart`, `die_cart_rails`, `die_body_upper`/`lower`, `melt_stand_pump`, `ctrl_riser_die`, `die_junction_box`.

**Problem:**
- The cart is X 9126–9350 (224 deep). Its rails are at X 9160 and 9320, a **gauge of 160 mm**.
- From the actual outlines, the die bodies are 2 × 0.077 m² × 2 600 ≈ 0.40 m³, about 3.1 t of steel. With the end plates (0.26 t), lips and bolts the die is ≈ **3.4 t**, not the "≈ 2 t" in the cart text.
- With the centre of gravity ≈ 1 150 mm above the rails, the cart tips at about 4°. It would fall over in X as soon as the die is unbolted to roll out to +Y.
- web-08 shows the real form: a wide four-castor base with outriggers that reach under the melt line.
- Side clash: `die_cart_rails` overlaps `ctrl_riser_die` (X 9140–9150, Y −1300…−1200).

**Fix:**
- **Cart:** base X 8700–9380 at Z 60–300, running under the static mixer and die adapter (mixer underside Z 1050). Uprights and jack columns stay at X 9150–9350 with the pads at (9240, ±700, 950).
- **Rails:** at X 8760 and 9320 (gauge 560), Y −1500…+2800, with floor locks.
- **Bottom-roll clearance:** keep the cart front at X ≤ 9380 only below Z 600. The bottom roll is at X ≥ 9429 there.
- **Pump stand:** shorten `melt_stand_pump` to X 7400–8650 and move the mixer saddle to X 8560.
- **Electrics:** move `die_junction_box` and its riser off the cart (see I6). They must not ride on a cart that moves.
- **Text:** change the die mass to ≈ 3.4 t in design.md.

### I4. Undried PET with an atmospheric vent right after melting and a single vacuum vent.
**Parts:** `barrel_vent_atm`, `barrel_b3`, `barrel_cover_c6`, vacuum group.

**Problem:**
- The application is direct sheet from undried PET (0.2–0.4 % moisture, design §7.1, DECISIONS 3).
- The design opens B3 to air right after the melting block and has one deep-vacuum vent on B5.
- Twin-screw lines for undried PET (KM ZE UT for PET sheet, c040; two-stage Roots vacuum, c062) remove the water under vacuum as soon as the melt forms. They normally use two vacuum zones: a first vent at ≈ 30–100 mbar after melting and a deep vent at ≤ 10 mbar before pressure build-up.
- Otherwise hydrolysis at 280 °C costs IV before the moisture is out, and the open vent lets oxygen reach the melt (yellowing).
- An experienced PET engineer will query an open stack on B3.

**Fix:**
- **Vacuum vent on B3:** replace `barrel_vent_atm` with `barrel_vent_dome_2`, a box dome 400 × 360 at X 1950–2350, Z 1460–1960. That keeps it inside C6 (ends at X 2366) and clear of the joint-2 nuts (X ≤ 1772). Enlarge the B3 opening to 320 × 280 (X 1990–2310) and cut C6 to 420 × 380.
- **Vent hardware:** DN100 outlet on −Y at Z 1800, with a shut-off valve, bellows and a manual regulating valve set to ≈ 50 mbar.
- **Line:** DN100 to Y −2700, then along X at Z 2250 to a second inlet on `vac_separator`, with a throttling valve so B5 keeps 5–20 mbar.
- **Wiring:** add `v_05` (barrel_vent_dome_2 → vac_separator) and a second vacuum gauge.
- **Alternative:** if the atmospheric vent is kept, design.md §7.2 must say why and add the fume hood it mentions. Otherwise the model shows an open steam vent indoors.

### I5. Melt-pressure safety: nothing protects the line downstream of the gear pump.
**Parts:** `melt_rupture_disc`, `melt_pump_adapter_out`, `melt_sensor_p4`.

**Problem:**
- The only rupture disc is on the head adapter, upstream of the diverter valve.
- The Maag GU 100/125 can build 370 bar (c049) into the pipe, mixer and die.
- A blocked die (cold lip, closed choker) is protected only by the P4 software trip.
- Standard practice is a mechanical burst device after the pump as well.

**Fix:**
- Add `melt_rupture_disc_2` on `melt_pump_adapter_out`, −Y side: cylinder Ø40 × 120 along Y at (8001, −150…−270, 1200), shroud pointing down, burst 350 bar.
- Add a P4 trip at 330 bar to design.md §7.6.
- Add a signal connection to the control cabinet.

### I6. Heater power stops at the barrel. The melt line and screen changer (≈ 75 kW) are not wired, and the die junction box is far too small.
**Parts:** `melt_screen_changer`, `melt_heater_bands`, `melt_startup_valve`, `melt_gear_pump`, `die_junction_box`, connections `p_02`/`p_03`.

**Problem:**
- `p_02` feeds only `barrel_heater_jboxes`.
- Nothing powers the screen changer's 6 zones (39 kW, c050), the cartridge heaters of the valve and pump, or the 13 bands (≈ 35 kW).
- All die power (20 zones ≈ 50 kW, plus 94 thermal bolts at 80 W, c054) goes to a box 180 × 150 × 500. That box cannot hold 20 zone terminals, 94 bolt circuits, 2 multi-pin harness sockets (web-17) and an E-stop.
- Real thermal-bolt systems come with their own controller cabinet.

**Fix:**
- **Melt-line junction box:** add `melt_heater_jbox`, 600 × 250 × 800, RAL 7035, on the −Y face of `melt_stand_sc` at X 6650–7250, Y −850…−600, Z 150–950 (below `melt_sc_drive`). Feed it by `p_10` from the control cabinet via the trench. Run flexible conduits from it to the screen changer terminal box, valve, adapters, pump and cladding terminal boxes.
- **Die junction box:** resize to 600 × 300 × 1000, floor-standing at X 8700–9300, Y −1900…−1600. Give it a plug-in harness to the die, so the die cart can leave.
- **Thermal-bolt controller:** add `ctrl_die_bolt_cabinet`, 800 × 600 × 2000, in the cabinet row.

### I7. Cooling water reaches only the barrels and the lube cooler.
**Parts:** `feed_throat`, `sidefeed_barrel`, `vac_separator`, `vac_pump_unit`, `melt_hpu`, `barrel_cw_supply`/`return`.

**Problem:**
- design.md requires water for the feed-throat jacket ("2 đầu nối nước"), the side-feeder barrel jacket, the separator cooling coil (§7.1: 10–15 °C) and the water-cooled Roots and dry-screw skid.
- None of these has a hose or a connection.
- The vacuum condenser does not work without water.

**Fix (add `util_cw_*` parts and `w_06…w_09`):**
- feed throat: 2 × DN20 from valve station 1, (338, 910, 1000) → throat ports (340, 210, 1550);
- side feeder: 2 × DN15 from station 2 → (1350, 1000, 1150);
- vacuum: 2 × DN25 from the header ends at X 5400, down into the floor trench at Y −1150, then to the separator coil ports (separator +X face, Z 1000) and the skid manifold (Z 400);
- HPU, if its cooler is water-cooled: 2 × DN15.

### I8. Thermal growth and support of the discharge end are not designed.
**Parts:** `melt_head_adapter`, `melt_startup_valve`, `melt_stand_sc`, `melt_stand_pump`, `die_cart`.

**Problem:**
- The barrel grows ≈ 17 mm toward the die (design §7.7). The 3 380 mm melt line adds ≈ 3.38 m × 12e-6 × 260 K ≈ 10 mm.
- Hot, the die therefore sits ≈ 28 mm further +X than cold.
- But `melt_stand_sc` (3.8 t screen changer) is "bulông neo" to the floor, and the die cart runs on flanged wheels in Y only.
- The diverter valve and head adapter (≈ 1.3 t) hang about 1 m beyond `barrel_support_3` (X 5239) with no support.

**Fix:**
- **Valve support:** add `melt_valve_support`, a bracket from the `base_frame_process` end plate (X 5950) up to the valve underside (Z 940), with a roller or PTFE pad.
- **Stands:** give `melt_stand_sc` and `melt_stand_pump` PTFE slide plates (X free ±40 mm, Y guided). Anchor only their sole plates.
- **Die cart:** let it float in X: one flat rail, plus a ±40 mm slide on the cart top.
- **Text:** state in §7.7 that the 200 mm air gap is set hot.

---

## Minor

### M1. Flange bolting at the barrel ends breaks the design's own fit check.
**Parts:** `barrel_b1`/`lantern`, `barrel_b6`/`melt_head_adapter`, `melt_startup_valve`.

**Problem:**
- "16 × M36" on a Ø600 flange around a Ø520 body does not fit. The nut corners (≈ 63 mm) need PCD ≥ 583 and then overhang the flange.
- design.md rejects M30 at the inner joints for exactly this reason.
- The 12 × M30 on the Ø420 adapter outlet flange collides with the r 200 cone.

**Fix:**
- Use 20 × M24 studs on PCD 560 at both barrel ends, as at the joints. The design's own 4 MN preload check covers 300 bar.
- At the valve, use tapped holes in the valve body with nuts on the valve side, or a Ø480 adapter flange.

### M2. The drive train is longer than the KM table implies.
**Parts:** `drive_flex_coupling`, `drive_safety_coupling`, `lantern`, `gearbox`, `base_frame_drive`.

**Problem:**
- From c007, L = 11 700 mm at 44D, which gives ≈ 10 000 mm at 34D (specs §1).
- The design measures 10 721 mm from the motor NDE to the barrel end (+7 %).
- Most of the excess is a separate 250 mm flex coupling plus a 400 mm safety coupling, and a 750 mm lantern. The silhouette gives 690 mm at 45.2 mm/pt, or ≈ 645 mm at the 1 200 mm axis-height scale.

**Fix:**
- Use one combined flex-plus-torque-limiting coupling, 450 long at X −2750…−2300.
- Lantern 600, at X −600…0. Gearbox at X −2150…−600.
- Shift the motor and base forward by 380 mm.
- Overall length becomes ≈ 10 340 mm.

### M3. E-stops are at knee height, and one listed station has no part.
**Parts:** `ctrl_estops`.

**Problem:**
- The boxes are at Z 480–620. Typical mounting is 0.6–1.7 m, usually 1.0–1.2 m.
- design.md §1 lists an E-stop on the mezzanine, but there is no part for it.

**Fix:**
- Mount the boxes on brackets on the lower cover panels at Z 1050–1190, same X positions.
- Add an E-stop box on a mezzanine railing post at (−450, 1380, 4000). Add it to `s_06`.

### M4. The vacuum line is a head-strike over the rear walkway.
**Parts:** `vac_valve`, `vac_bellows`, `vac_pipe`, `vac_pipe_support`, `vac_bleed_valve`.

**Problem:** The horizontal DN150 run at Z 1980 has its underside at 1896 mm. Walkway headroom must be 2 100 mm.

**Fix:**
- Take the outlet from the dome lid instead of the −Y side: valve and bellows vertical over Z 2150–2400.
- Run the horizontal at Z 2300 (underside 2216), then down to the separator.
- Raise the support post and bleed valve to match.

### M5. The condensate drain cannot be emptied while running.
**Parts:** `vac_drain`.

**Problem:** A single ball valve that is "closed during suction" means the separator fills up during production.

**Fix:**
- Build a lock pot of Ø300 × 400: upper valve (normally open), vent valve, and lower drain valve with red handles.
- Raise the separator legs by 150 mm to fit it.

### M6. Small hard clashes.
**Parts:** `die_deckles` and `ctx_roll_stand`; `die_heater_conduit` and `util_air_drop`.

**Problems and fixes:**
- **Deckles in the roll stand:** the deckle rods (to \|Y\| 1525, X ≤ 9560) enter the roll-stand side frames (\|Y\| ≥ 1400, X ≥ 9540). Either shorten the deckle knobs to X ≤ 9520 or start the side frames at X 9600 between Z 1000 and 1400. Also note in design.md that the stack must retract before the die rolls out in +Y.
- **Conduit through the air drop:** `die_heater_conduit` passes 16 mm from the centre of `util_air_drop` at (9090, −1270, 1000); the two radii need 35. Move the air drop to Y −1330.

### M7. The sheet path is not the S-wrap of page 24–25, and auto-profile control has no gauge.
**Parts:** `ctx_sheet`.

**Problem:**
- In `p24-25_slot_die_smoothing_roll_600dpi.png` the sheet wraps the middle roll on +X, then the **top roll on its die side (−X)** over the top. `ctx_sheet` stops at X ≥ 9576.
- The "automatic" thermal-bolt profile control (§1) also needs a traversing thickness gauge.

**Fix:**
- Path: lip → nip (9776, 1200) → middle roll +X wrap → top roll −X wrap (reaching X 9376) → exit +X at Z 2803. Widen the bbox to X 9376–10400.
- Optionally add a context O-frame gauge downstream.

### M8. Loss-in-weight feeder outlet is hard-piped.
**Parts:** `feed_downpipe`, `feed_main_feeder`, `sidefeed_downpipe`, `feed_additive_tube`.

**Problem:**
- A loss-in-weight feeder must be decoupled at its discharge, or the pipe carries weight and spoils the dosing.
- Here the downpipe bolts straight to the feeder outlet and has a collar in the deck.

**Fix:**
- Add a 150 mm white flexible sleeve at each feeder outlet, Z 2850–3000, inside the deck opening.
- Start the rigid pipes at Z 2850. The deck collar must not touch them.

### M9. Motor cooling differs between DECISIONS and design.md.
**Parts:** `drive_motor`.

**Problem:**
- DECISIONS 11.3 says the motor has a cooler on top ("có bộ làm mát trên nóc").
- design.md and c066 describe an IP24W open, louvred top housing.

**Fix:**
- Pick one. For an extrusion hall, IC81W (air-to-water top cooler, same HC envelope) is the more realistic choice. It needs 2 × DN40 water pipes from the plant risers along the +Y frame edge.
- Otherwise correct DECISIONS 11.3.

### M10. Compressed air reaches only the die.
**Parts:** `util_air_drop`, `vac_valve`, `feed_vacuum_loader`.

**Problem:**
- The pneumatic butterfly valve, the loader's discharge flap and the feeder refill valves need air.
- design §7.13 mentions them, but no line is modelled.

**Fix:**
- Add one drop with an FRL at the mezzanine column (−450, −2600). Run Ø12 tubes to `vac_valve` and the loader. Add connection `a_02`.

### M11. The machine-end cabinet does not match the page-9 element.
**Parts:** `ctrl_machine_cabinet`.

**Problem:** Page 9 shows a 430 × 1 380 block standing off the floor at Z 316–1695 (pdf_measures §4). The design has a floor cabinet 500 × 1 000 × 2 000, only 75 mm behind the motor NDE and encoder, so there is no bearing access.

**Fix:**
- Make it a frame-hung cabinet at X −5700…−5250, Z 300–1700.
- Leave ≥ 150 mm behind the encoder.

---

## What is good, keep it

- **Process train:** the station order and the straight, coaxial melt line at Z 1200 are right: diverter → screen changer → gear pump → mixer → die, with P1–P5 sensing and the P3 pump-inlet loop controlling screw speed.
- **Sizing:** the numbers are consistent and sourced. D 169 / 34D = 5 746 is split 4D + 5 × 6D. The RSFgenius 200 runs at 77 % and the GU 100/125 at 78 % of rating. Rolls Ø800 × 2 600 give 1 670 kg/h·m, under the 1 800 limit in c046.
- **Main motor:** the 1 500 kW choice has a correct torque check: 17.9 kNm per shaft is 51 % of the gearbox rating.
- **Silhouette heights:** frame 650, covers 1 650, dome 2 150 and gearbox 1 720 match page 9 within a few percent. Covers span 71 % of the barrel and the feed zone is left exposed, as on page 9.
- **Die and rolls:** the geometry was really checked. Using the actual outlines, the die nose clears the middle and bottom rolls by 39–53 mm.
- **Bolted joints:** the nut-to-body clearance was checked for the flange joints.
- **Photo-based details:** lube unit per web-03; side feeder on a wheeled cart per p06; pump drive with vertical motor and cardan guard per web-07.
- **Data pipeline:** `build_parts.py` is the single source and `check_parts.py` validates it. Keep both. Just make the checker enforce C1.
