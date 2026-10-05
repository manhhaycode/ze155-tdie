# Review 01 – animation and cutaway design (ZE 155 + T-die)

Reviewer: independent, findings only. Reviewed `anim/design-anim.md`, `anim/shots.json`, `anim/interior_parts.json`, and `anim/storyboard/*`. I checked these against `design/design.md`, `design/parts.json`, `research/claims.jsonl`, `tools/ze_helpers.py` and the live scene `ze155`. The scene check was read-only. It covered object names, world bounding boxes, mesh islands, cameras, evaluated triangles, and the open-file state. I verified the numbers in Python. I used public web sources for two process questions.

## Findings

Severity: C = Critical, I = Important, M = Minor.

**C1** – design-anim §1 row 5, §2 bullet "Vì sao cân đặt lưu lượng", §5 loop table (PIC-P3), S10 HUD, S14 labels, S15 HUD line 2.
- **What is wrong:** The control story is presented as the only correct one: "P3 → pump speed, the feeder sets the flow". The brief also says the classic "P3 → screw speed" loop is only for flood-fed machines. S15 makes this one of the three core take-aways. For a sheet line this teaches the opposite of the usual practice.
- **Evidence:**
  - In twin-screw direct sheet extrusion, the gear-pump rpm is normally locked. This gives a constant volume flow to the die, so it sets mean thickness together with roll speed.
  - The PLC then trims extruder screw rpm and feed rate together to hold the pump inlet pressure. Source: PlasticsToday "Direct extrusion with twin-screw extruders" (Leistritz). The brief's argument "starve-fed ⇒ screw speed cannot change flow" is true for screw speed alone, not for feed rate.
  - "Pump follows P3" is the compounding/pelletizing mode. In that mode every LIW refill and pressure disturbance goes straight into the die output, which shows up as thickness variation along the machine direction (MD).
  - The design (s_20, I3) chose pump-follows, and the anim promotes it.
- **Fix:** Add a decision Q6 for the user. Recommend that the anim tell the standard sheet-line story:
  - pump speed is the master;
  - PIC-P3 trims LIW feed and screw speed in ratio;
  - pump speed and roll speed set the mean thickness;
  - the scanner drives the thermal bolts and trims roll or pump speed;
  - the deviation from design s_20 is listed in §10.

  If the user keeps s_20, label it as the design's choice and remove the claim that the alternative is wrong. Rewrite S15 line 2 either way.

**I1** – design-anim §8 "Lưu: Z.save_blend()" and §9 C0 "file lưu và đọc lại được"; §7 save strategy.
- **What is wrong:** `Z.save_blend()` writes scene `ze155` to `out/ze155.blend`, which is the file now open in the live session (dirty). Three problems follow:
  - The helper's read-back `bpy.data.libraries.load(path)` fails on the open file. Live check: `ValueError: Cannot load from the current blend file`. So C0's "done when" can never pass.
  - The write persists whatever unsaved changes make the session dirty into the frozen model file.
  - After the anim build, the open session also holds `ze155_anim` and all `int_*`/`anim_*` data. A normal Ctrl+S by the user would write all of it into `out/ze155.blend`, which breaks "keep ze155 clean".
- **Fix:**
  - Before C0, ask the user what the dirty changes are (keep or discard). The user decides; builders cannot revert.
  - Verify C0 by writing a temp copy, e.g. `out/tmp_c0_check.blend`, and loading that, or check in-session counts (11 cameras, 610 − 62 objects).
  - Add a clear line in the brief: "do not press Ctrl+S in the open Blender once the anim scene exists".
  - Save the anim only to `anim/ze155_anim.blend` (as already planned).

**I2** – shots.json `visible.hide` lists vs design-anim §8 (8 `ax_*` groups, "mỗi vật đúng một nhóm").
- **What is wrong:** The per-shot hide lists are per object, but the only allowed mechanism toggles 8 collection groups. Per-object `hide_render` is shared with `ze155`, so it is forbidden. No object→group table is given, and the patterns conflict.
- **Evidence:**
  - `melt_heater_bands` is a single object spanning X 5801–9035. It is bisected in S08, hidden in S10, and whole in S09.
  - `melt_screen_changer` is hidden only in S09. `melt_gear_pump` and its adapters and sensors are hidden only in S10.
  - `die_body_lower` is hidden in S11 and S12, and `die_body_upper` is peeled.
  - With an `ax_melt_shell` group, S09 and S10 would blank the whole melt line in frame.
- **Fix:** Add an object→group table with one group per visibility pattern (about 15–20, e.g. `ax_sc`, `ax_pump`, `ax_head_valve`, `ax_melt_bands`, `ax_die_lower`, `ax_rolls_sheet`…). Alternatively, state the rule: every member of a hidden group gets an `anim_cut_*_keep` copy (an unchanged copy if it is outside the box) that is shown in that shot.

**I3** – S05 and S07 sections ("screws stay whole, their cut face is int_xsec_*"); interior_parts `int_xsec_*`.
- **What is wrong:** Whole screws would stick out of the cut face toward the camera and hide the figure-8: 3.3 m past X 2.45 and 1.6 m past X 4.12. They sit at Y ±0.071, Z 1.2, while the camera at (3.05, 0.42, 1.45) looks straight along them.
- **Fix:**
  - Hide elements 13–32 (for X 2450) and 23–32 (for X 4120).
  - Pre-bisect the element that straddles the plane: no. 12 (2239–2493) and no. 22 (3971.5–4225). The cut stays valid while the element spins, because the plane is perpendicular to the rotation axis. Use `int_xsec_*` as its cap.
  - Cut `int_fill_screw_b3`/`_b5` the same way.

**I4** – S04 camera keys 960–1250 (also S03 frame 700).
- **What is wrong:** At frame 1100 the camera is at (1.75, 1.6, 2.3) aiming at (1.85, 0, 1.2). The line of sight passes 0.2–0.4 m from the lens through a feed-platform H-column: island of `feed_platform_columns_front` at X 1.65–1.85, Y 1.2–1.4, Z 0–2.77, plus a knee brace at Y 0.8–1.22, Z 2.38–2.8. At 40 mm the column fills about ¾ of the frame, right while the KB 45° and seal-1 labels play (frames 1040–1220).
- **Evidence:** The S04 path also runs just under the deck edge (Z 2.78–3.05, Y ≤ 1.4). In S03 at frame 700, the ray to (−0.1, 0, 2.6) crosses the deck edge beam at Y 1.4 → 1.075. ST1 already hides the platform group; S03 and S04 do not.
- **Fix:** Hide the feed-platform group (columns, deck, gratings, railing, and the feeders/loader if they are in frame) for S04. Alternatively keep the S04 path at Y ≥ 2.2 and skip X 1.55–1.95 at low height. Re-aim S03 frame 700 above the deck or hide the deck edge.

**I5** – S04/S06 (SEC_Z1200 with the upper half peeled).
- **What is wrong:** Both vent openings and both domes lie entirely above Z 1200, so the cut removes them. The core check "seal ends before the vent, low fill under the vent" (§1 goal 2, checklist item 4) is then only a label at X 2.15 plus sparse bubbles. Nothing in 3D marks where the vent is relative to the LH element.
- **Fix:** Keep a ghost of each vent opening and dome (α ≈ 0.15 outline) over X 1990–2310 and 3860–4380, or put a coloured vent-window band on the cut barrel. Also draw the vent windows on the HUD strip next to the seal positions.

**I6** – S12 animation and interior_parts `int_die_section_*` (shape key `lip_push`).
- **What is wrong:** The shape key lowers the flex-lip tip by 5 mm (0.1 mm × 50), but the land gap is 1.0 mm. The lip would pass about 4 mm through the lower lip and the curtain in the key fine-adjustment shot. The numbers also disagree: 0.1 mm in interior_parts, "±0,15 mm" in the label, 300 µm stroke in §2.
- **Fix:** Use one value (±0.15 mm). Exaggerate the drawn gap and the motion by the same factor in this shot (badge "khe và hành trình phóng đại ×N"), or keep the true gap and show the motion in a 2D inset or gauge.

**I7** – pacing: S06, S14, S15 and label times in shots.json.
- **What is wrong:** Key teaching labels are on screen too briefly to read. Reading rate is about 3 words/s.
  - S06: "Sau nút: điền thấp, mặt nhựa mở cho chân không" for 2.0 s; the LH label for 3.6 s.
  - S04: vent-1 label for 3.2 s.
  - S14: 7 control loops in 9.6 s; the interlock label for 1.6 s (15 words); "Chiều dày TB → tốc độ trục cán" for 2.6 s; up to 7 labels at once, seen from about 16 m at 28 mm, so the sensor anchors (42 mm transducers) are specks.
  - S15: 3 lines of about 35 words in 6 s.
- **Evidence:** The control loops are the heart of "how the line interacts" (one of the user's three asks).
- **Fix:**
  - S14 control layer at least 20 s: about 3 s per loop, with a camera push or a 2D block-diagram overlay.
  - Hold the last labels at least 3 s.
  - S06 at 10–12 s; S15 at about 10 s.
  - Cost: about +25 s, i.e. about +25 min render.

**I8** – design-anim §7 render plan, §9 phase R ("chạy không cần người trông").
- **What is wrong:** 4 400 frames take 2.5–3.7 h. BRIEF forbids headless Blender, and one MCP execute call cannot run for hours. The plan does not say how the render runs. It would also occupy the user's open Blender for about 3 h.
- **Fix:**
  - Specify chunked, resumable rendering: ≤ about 50 frames per call, or a `bpy.app.timers` job that skips existing PNGs, with a progress line in `anim/log.md`.
  - Tell the user up front that their Blender is busy during R.

**I9** – on-screen numbers, all shots; design-anim §2 "Nguồn" column.
- **What is wrong:** Assumed values appear on screen as facts. Examples:
  - S04 "≈ 50 mbar"; S07 "5–20 mbar";
  - S09 "P2 ≈ 95 → Δp ≈ 45 → P3 = 50 bar"; S10 "P4 ≈ 250"; S11 "P5 ≈ 200 bar";
  - barrel and melt temperatures; S05 "khe đỉnh ≈ 0,75".
- **Evidence:** Design §9 itself calls the vacuum levels assumptions. The §2 table cites c050/c052 for Δp 45 bar, but c052 is only the catalogue rating basis (40 bar at 1 000 Pa·s), not an operating value.
- **Fix:** Use one convention, e.g. "*" = giả định with a footer in every shot. Correct the source cell for Δp.

**M1** – design-anim §10.5, interior_parts `screw_profile.note_vi`, S04/S05 HUD.
- **What is wrong:** The brief says design's core Ø114.6 is wrong and 116.5 is "đúng hình học".
- **Evidence:** c001/c002 give screw diameter 169 (Schneckendurchmesser) and flight depth 27.2, so core = 114.6. Then 84.5 + 57.3 = 141.8 < 142, a consistent self-wiping pair with 0.2 mm clearance. The anim instead treats 169 as the bore.
- **Fix:** Keep the model if you like (no one can see 1.9 mm), but do not call the design wrong. The HUD can say "Vít Ø167,5 (mô hình)".

**M2** – S04 `anim_bubbles_vent1` "0.15 m/s, sparse" vs S07 vent 2 "0.25 m/s".
- **What is wrong:** Labels say vent 1 removes most of the 7–14 kg/h of water, but the visuals show vent 1 weaker than vent 2.
- **Fix:** Make vent 1 the heavy vapour flow. Vent 2 then reads as the finer, deeper-vacuum stage.

**M3** – S04 `anim_pellets_screws`.
- **What is wrong:** Pellets on a straight path at a schematic speed will pass through the turning flights.
- **Fix:** Set the axial speed to pitch × shown rev/s (1.5D: 0.2535 × 0.25 ≈ 63 mm/s; 1D: 42 mm/s), or move the pellets helically with the channel.

**M4** – S08 / interior_parts `int_valve_bolt`.
- **What is wrong:** The valve bolt is specified three different ways:
  - `position_mm`: DRAIN at Y −200, RUN at 0;
  - `details`: "slide −200 mm DRAIN → RUN";
  - shots.json: `location[1]` +0.200 → 0.

  `melt_startup_cyl` sits on −Y (Y −873…−252).
- **Fix:** Pick one: DRAIN = bolt at −0.200, RUN = 0, elbow at local +0.200; animate −0.2 → 0.

**M5** – mass balance (§2, S03/S14 "WIC-01 3 500 kg/h").
- **What is wrong:** About 4.5 % edge trim (≈ 160 kg/h) returns through the side feeder, and masterbatch is also added. So either the extruder/pump flow exceeds 3 500 kg/h, or the main LIW runs at about 3 340 kg/h.
- **Fix:** Say "3 500 kg/h tổng (gồm biên tấm + phụ gia)" and adjust the WIC label.

**M6** – S13 `anim_curtain` ramp and §7 ("đổi từ hổ phách sang trong khi tới khe trục").
- **What is wrong:** The curtain turns clear in the air gap, which suggests it solidifies before the rolls.
- **Fix:** Start the clearing at the nip and over the middle-roll wrap.

**M7** – section edge cases.
- **What is wrong:** Several objects that cross a cut or a box edge are not handled:
  - `vac_pipe`/`vac_pipe_3` (curves) are left floating over the open barrel in S04/S06/S08 once the domes and valves are hidden. ST1 hides them; those shots do not.
  - `barrel_cw_hoses` (one curve, X 189–5558) straddles the S05/S07 planes.
  - `feed_platform_columns_front` is partly inside the S04 box (Y 0.8–1.0), so it would be sliced.
  - The S08 box starts at X 4.7, so covers and heater shells for X < 4.7 stay closed while B1–B5 are swapped for lower halves.
  - The choker bar floats 3 mm above the lower die after the S11 peel.
- **Fix:**
  - Add a rule: any object whose evaluated bbox straddles the plane inside the box gets a bisected copy (curves converted to mesh first).
  - Use one box X −0.05…6.5 for S04/S06/S08.
  - Hide the vacuum pipes (and their `_hw`) in those shots.
  - Peel the choker bar with the upper die half.

**M8** – stills ST1–ST7.
- **What is wrong:** ST1 is tied to frame 4400. That is the S15 state, where the collection keys hide all the interior. ST1 also cuts `int_sc_disc` at Z 1.2, which leaves only a 120 mm sliver (the disc spans Z 1.08–2.01).
- **Fix:** Give the stills their own visibility state, not a timeline frame. Use the ghost screen changer in ST1.

**M9** – interior_parts `int_fill_*` in Z-cut shots.
- **What is wrong:** Full-fill zones are a "full figure-8", so the amber volume above Z 1.2 would sit over the screws seen from above.
- **Fix:** Use `_lo` fill variants in S04/S06/S08.

**M10** – §11 Q1 alternative (2:00 version drops S06).
- **What is wrong:** S06 is the only shot that shows seal 2 (LH) before the deep vacuum, which is core goal 2.
- **Fix:** Say this in Q1, or shorten S01/S02 instead.

**M11** – interior_parts `int_die_lower_face`, `int_melt_adapters_hollow`; §10.4 / Q2.
- **What is wrong:**
  - The manifold centre at X 9162 with r 36 puts its rear edge exactly on the die back face (X 9126): zero wall at the centre.
  - The preland is only about 31 mm longer at the centre than at the edges. A viewer will read a near-T manifold.
  - The die adapter "widens to a 300 × 40 slot at the die face" contradicts the "Cửa vào Ø100" inlet.
- **Fix:** State both points in Q2 and in the S11 inset. Use the Ø100 inlet in both parts.

## Verified OK

- **Screw table:** 32 elements sum to 34D = 5 746 mm. Barrel labels match the joints at 676/1690/2704/3718/4732. The helix phase is continuous across all elements (RH +360·L/p, LH −, KB 4 × stagger). Seal 1 ends at 1 985.75 < 1 990 and seal 2 at 3 718 < 3 860. Pitch-1.5D low-fill SE sit under both vents, and the last 3.5D are full. The fill and pressure strip in the S06 storyboard has the pressure peaks on the upstream side of the restrictions.
- **Self-wiping profile:**
  - ψ = 90° − 2·acos(142/167.5) = 25.94°.
  - The flank is an arc of radius a centred on r = Ro; r(ψ/2) = Ro and r(90 − ψ/2) = Rr both check.
  - The 0.995 scaling gives a uniform 0.71 mm screw–screw gap (the contact normal lies on the centre line) and about 1.2 mm to the bore.
  - Shaft B phase +90°, same-sign rotation; with ω < 0 the RH flights travel +X (checked analytically).
- **Figure-8 and barrel:** 142 + 169 = 311. The bore fits the Ø520 barrel with at least 104 mm wall. Cooling bores on PCD 430 are clear of the bore and the OD.
- **Gear pump:**
  - **69 rpm is right:** 2.99 m³/h ÷ (0.764 L × 0.95) = 68.7 rpm. The Maag row (4 474 kg/h at 134 rpm, 764 cm³/rev) implies 0.73 kg/L, a polyolefin-type melt density. So design's 105 rpm is wrong for PET.
  - 16 teeth, m 7.8, b 125 give 2π·m²·z·b = 764 cm³.
  - The chamber (125 + 141 = 266 mm) fits the body (Z 970–1448).
  - Pressures are within limits: ΔP = 200 < 250 bar, trip 330 < 370 bar.
- **Rotation directions:** The pump gears (top +, bottom − about +Y) carry melt around the outside, −X → +X. The rolls (bottom +, middle −, top +) match the S-wrap of `ctx_sheet` (X min 9 374 = the −X side of the top roll). 9.95 rpm ↔ 0.417 m/s.
- **Mass balance and drive:** Lip speed 20.8 m/min, sheet 24.8 m/min, draw-down 1.19. 1 670 kg/h·m < 1 800 (c046). Torque 12.7 kNm per shaft = 36 % of 35 kNm. Motor 1 119 rpm = 300 × 3.73. Specific energy 0.20–0.25 kWh/kg is plausible for PET.
- **Screen changer:** 5 × Ø157 = 968 ≈ 970 cm² (c050). A disc axis parallel to the flow is correct (the design's −Y shaft is rightly overridden). The Ø930 disc at Z 1.545 fits the housing (Z 650–2079 = C 1 429, X 705 = B 705). The +30° step takes the loaded screen from −30° to the 0° backflush station.
- **Die:** 94 × 25.4 = 2 388 mm. Thermal bolts work as heat → expand → close the lip, and the scanner drives the bolts. Choker = coarse adjustment, flex lip = fine adjustment. The air gap of 200 mm is stated honestly.
- **PET degassing story:** Hydrolysis and IV loss, removing water right after melting, the melt seal before each vent, low fill under the vents, and vacuum instead of a dryer are all correct. The vacuum levels are plausible: Gneuss MRS works at 20–40 mbar, and the general range is 1–200 mbar. The temperature profile and the amorphous quench below Tg are fine.
- **Scene check:**
  - All `ze155` object names referenced in the hide lists and `connects_to` exist.
  - Positions match: vent domes (`barrel_vent_dome` = vent 2 at X 3 790–4 450, `_2` = vent 1 at X 1 920–2 380, used correctly), feed throat X 90–590, die X 9 126–9 576, rolls at X 9 776 / Z 799, 1 601, 2 403, P3/P4 sensors at the label X.
  - The `parts.json` connection counts (power 13, water 11, vacuum 4) match S14.
- **C0 camera cleanup:**
  - 73 cameras = 11 kept + 62 deleted; every category count matches the brief.
  - No shared camera data, no timeline markers, no constraints pointing at cameras.
  - The scene camera is `cam_photo_web12` today, and the brief sets `cam_fin_hero` before deleting.
  - The 5 lights are left alone.
  - The drawing cameras can be recreated with `Z.make_ortho_cam`.
- **Budget:** The scene's evaluated triangle count is 1.25 M (measured), plus about 0.35 M interior and 0.15 M cut copies, for about 1.75 M total. That is fine for EEVEE. The screw instances will be nearer 260 k than 194 k, still fine. The render estimate is consistent with the finals scaled by pixels × samples (about 2.5–3.4 s per frame).
- **Cutaway method:** Pre-bisected copies plus peel, new closed hollow barrels for the main cuts, and hollow proxies as a fallback is the right choice for the bevelled, multi-island, partly curve-based exteriors.
- **Brief:** Clear and scannable. Vietnamese terms are correct, with English in parentheses. The decisions come with recommendations.

## Verdict

**Ready after these fixes.** C1 has to go back to the user as a decision (Q6) before S10/S14/S15 are built. I1 (save and dirty-file handling) has to be settled before C0. I2–I9 are fixes inside the anim spec and need no further user input.
