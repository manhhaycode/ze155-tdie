# FLOW (hạt → film) Implementation Plan

> **For agentic workers:** executed natively in the session (user: "Bắt đầu implement đi nhé"), then one independent reviewer (spec §7 step 6). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** add the fixed cut state `FLOW` (whole line cut at Y = 0) with 3D pellets, animated melt fill, sheet material and a phase / heat colour switch, plus the §4.1 button relabel, without touching Blender or the GLBs.

**Architecture:** data first (`make_data.py` derives FLOW lists from the bbox rule + borrowed CUT_FEED / CUT_Z_BARREL / FREE / CUT_PUMP / CUT_DIE_AA lists and writes a `flow` block), then a runtime layer (`Flow.tsx`) that runs after `applyState('FLOW')` inside the state queue and only swaps materials through the recorded `setMaterial`, so `resetCuts` undoes it; pellets are one helper `InstancedMesh` outside the line tree.

**Tech Stack:** Python 3 stdlib (data), Vite + React 19 + R3F 9 + three 0.186 + zustand 5 (web), chrome-devtools MCP (checks).

**Spec:** `web/PLAN-FLOW.md` (read it with this plan).

## Global Constraints
- No Blender, no GLB re-export: `make -C web data verify publish` only (GLBs byte-identical).
- Never edit `web-check/public/data` by hand; old states in `cut_states.json` keep every byte except the §4.1 labels (`label_vi`, new `tooltip_vi`).
- `cut_states.json` keeps `version: 1`, adds `flow_version: 1`.
- Three coords = Blender (x, z, −y); FLOW plane three normal `[0, 0, 1]`, constant 0 (keeps z ≥ 0).
- Materials change only through the recorded `setMaterial`; visibility only through `setVisible`.
- Pellets: `raycast` no-op + `userData.__helper = true`; never inside `reg.lineScene`.
- Every new UI string in VI (`T`) and JA (`T_JA`); no coordinates on button text.
- Values marked \* are assumptions (design-anim §2 set points), shown as "\* giả định".

## Review Focus
1. Switching FLOW → FREE → FLOW (and any state → FLOW while the interior still loads): the fill / sheet materials and pellets must come back identical, never stacked.
2. Rotor mode `off` and `freeze(true)`: pellets, stripes and rotors stand still (no drift from accumulated time when switching back).
3. Language switch while in FLOW keeps the colour mode and the context row.
4. Picking in FLOW: pellets and fills never break `rayUnfiltered`; a click on a cap selects the right device.
5. Precompile with FLOW added stays ≤ 1.5 s and leaves the user's current state applied.

---

### Task 1: Data — `build_flow()`, labels, checks, verify

**Files:**
- Modify: `web/tools/make_data.py` (FIXED + FLOW, `LABEL_OVERRIDES`, `build_flow`, `check_states` cut_only_from, `check_flow`, intended diffs)
- Modify: `web/tools/check_glb.mjs` (verify FLOW like a fixed state; honour `cut_only_from`)

**Interfaces (produced, read by Task 2+):** `cut_states.json.states.FLOW` = fixed-state shape + `tooltip_vi`, `cut_only_from: ['CUT_PUMP','CUT_DIE_AA']`, `flow: { screw_rpm, phase_ramp_x_m, colors{pellet,melt,sheet_clear}, opacity, opacity_solid, heat_stops[[T,hex]], zones[{zone,x_m,temp_c,pitch_m,speed}], melt{stripe_m,speed_zone}, die{origin_m,radius_m,temp_c}, curtain{x_m,temp_c,speed_m_s_real,stripe_m}, sheet{path_three_xy,stripe_m,stripe_width,speed_m_s_real,clear_at_m,temp_profile[[s,T]]}, pellets{N,size_m,fall_speed_m_s,path_a[[x,y]],spread_m,z_m,land_x_m,bed_y_m,bed_z_m,bore{centre_y_m,centre_z_m,r_m},melt_x_m,temp_fall_c}, materials{node: 'line'|'die'|'curtain'|'sheet'} }`; every state gets `tooltip_vi`.

- [ ] Step 1: add FLOW constants (`FLOW_SOLID_HIDE`, `FLOW_SOLID_CLIP` decisions with reasons, `FLOW_EXTRA_HIDE` = screen changer logos as in GHOST_SC, split map from `dot2.name_rules.virtual_split_parts`).
- [ ] Step 2: `build_flow()` per spec §2.2 steps 1–5; FLOW camera; `flow` block (§3.6) with `source` strings; pellet path A from the feed-column probe (downpipe top x −0.45 y 2.80 → elbow −0.45/2.45 → downpipe end 0.09/2.01 → hopper 0.30/1.80 → throat 0.34/1.55).
- [ ] Step 3: checks §2.5 (exit 1): names, `check_states` (cut_only allowed for `cut_only_from`), screw A/B, valve run/drain, fill zones, one list per name; warnings for solids.
- [ ] Step 4: `LABEL_OVERRIDES` §4.1 (label_vi + tooltip_vi for 7 states); `intended_diff` for labels/FLOW.
- [ ] Step 5: `check_glb.mjs verify`: FLOW in the fixed list when present; `cut_only_from`.
- [ ] Step 6: run `make -C web data verify publish` → exit 0; `make -C web compare-drafts` → 0 unexpected; `make -C web verify-negative` still OK. Diff old states: only labels/tooltips changed.
- [ ] Step 7: commit.

### Task 2: Enter FLOW with Đợt 1 materials (types, store, toolbar labels)

**Files:** `src/data.ts`, `src/scene/Cuts.ts` (export `setMaterial`, `onResetCuts`), `src/store.ts`, `src/ui/Toolbar.tsx`, `src/ui/text.ts`, `src/ui/i18n.ts`, `src/scene/precompile.ts`.

**Interfaces:** `StateId |= 'FLOW'`; `STATE_IDS = [FULL, CUT_FEED, CUT_Z_BARREL, CUT_X2450, CUT_X4120, FLOW, FREE]`; `CutState.tooltip_vi?`, `CutState.flow?: FlowParams`; `Loc.stateTip(id, s)`; `Cuts.setMaterial(mesh, m)`, `Cuts.onResetCuts(fn)`.

- [ ] Step 1: types + ids; toolbar buttons get `title` tooltips; FREE axis buttons show "Cắt ngang / Bổ dọc / Cắt nằm" (`data-axis*` unchanged).
- [ ] Step 2: in Chrome: `__ze.setState('FLOW')` resolves, `selfcheck()` clean; screenshot; eyeball the 7 solids (§2.2 step 3) and settle `FLOW_SOLID_*` in make_data (re-run Task 1 step 6 if changed).
- [ ] Step 3: commit.

### Task 3: Flow materials (`heat.ts`, `FillMaterial.ts`, `SheetMaterial.ts`, `Flow.tsx`)

**Interfaces:** `heat.ts`: `heatColor(T, stops) → THREE.Color`, `heatGlsl(stops) → string` (`vec3 zeHeat(float T)` in sRGB), `tempAt(x, zones)`, `zoneAt(x, zones)`; `FillMaterial.ts`: `flowUniforms {uScrewT, uRollT, uMode}`, `makeFillMaterial(kind, plane, flow)` cached per kind, `fillColorAt(x, mode, flow)`; `SheetMaterial.ts`: `makeSheetMaterial(plane, flow)`, `sheetS(x, y, flow)`, `sheetColorAt(s, mode, flow)`; `Flow.tsx`: `enterFlowLayer()`, `leaveFlowLayer()` (registered with `onResetCuts`), `flowDebug`, `<Flow/>` (useFrame clock: `uScrewT += kScrew·dt`, `uRollT += kRoll·dt`, stops when off or frozen).

Shader time uses accumulated screw/roll time instead of `uTime · v`, so switching slow ↔ real never jumps the stripes.

- [ ] Step 1: write the modules; store `flowColor`, `frozen`; Rotors respect `frozen`; precompile includes FLOW layer.
- [ ] Step 2: Chrome: FLOW shows phase colours, heat colours, stripes drift +X, sheet stripes move; console clean.
- [ ] Step 3: commit.

### Task 4: Pellets (`Pellets.tsx`)

**Interfaces:** `pellets.build(flow, plane)`, `pellets.step(dt, kScrew)`, `pellets.recolor(mode)`, `pelletDebug {N, x(i), seg(i), visible()}`; mounted by `<Flow/>` at scene root.

- [ ] Step 1: InstancedMesh N = 2 000, Ø9 × 9 mm hex prism; segments A/B/C per spec §3.2; warm start (pre-simulated phases).
- [ ] Step 2: Chrome: pellets fall in the column, crawl in the bore of screw B, shrink and turn amber at X 1.52–1.90.
- [ ] Step 3: commit.

### Task 5: UI colour row, hooks, self-check F1–F10

**Files:** `src/ui/Toolbar.tsx`, `src/ui/text.ts`, `src/ui/ui.css`, `src/test/hooks.ts`, `web-check/README.md`, `DECISIONS.md`, `web-check/SELFTEST.json`.

- [ ] Step 1: FLOW context row (Màu: [Pha] [Nhiệt độ], legend, "* giả định") VI/JA.
- [ ] Step 2: hooks `freeze`, `flowProbe`, `pelletTest`, `fillColorAt`, `sheetProbe`; extend `selfcheck`, `cutRoundTrip`, `capCheck`, `selftest`.
- [ ] Step 3: run F1–F10 in Chrome (1920 × 1080 and 1366 × 768, VI/JA); screenshots to `web/review/flow/builder/`; update SELFTEST.json; README Use row; DECISIONS 33.
- [ ] Step 4: commit.

### Task 6: Independent review, fixes, re-check
- [ ] Step 1: reviewer agent (no edits) per spec §7 step 6 → `web/review/flow/review-flow-01.md`.
- [ ] Step 2: fix C / I (and M ≤ 15 min each); Blender-only issues noted.
- [ ] Step 3: reviewer re-checks the fixed items; commit.
