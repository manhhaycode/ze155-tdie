# Review 02: PLAN-R3F.md 1.1, model-contract.json 1.1, r3f-snippets.md

Independent reviewer, round 2, 2026-10-05. I re-checked each round-1 finding and spot-checked the revision for new problems.

**How I checked:**
- **Contract:** Python scripts in the scratchpad that:
  - resolve names in every cut-state list;
  - check that each `swap` value is shown, that each cut-only item is shown only in its own states, that no state shows two copies of the same place, and that clip and hide lists do not overlap;
  - re-check device parts and bboxes.
- **Snippets:** read against the drei 10.7.9 sources (`Bvh` and `Outlines`) and the A1a/A1b build scripts.
- **Live Blender:** not touched. The user's standing rule is to ask before any Blender MCP use, so I checked A1a/A1b names against `anim/log.md` and the `anim/tmp/*.py` build scripts instead. Every interior source name matches those files, either literally or through the scripts' name patterns.

## Round-1 findings

| ID | Status | Evidence |
|---|---|---|
| C1 | **Partly fixed** | The design is right: hits are filtered inside `mesh.raycast`, hidden empties return `false`, cut variants are DoubleSide, shared meshes get `acceleratedRaycast`, and A5b was added. The snippet, however, loses the filter in dev mode (see **N1**). |
| I1 | Fixed | Snippet §4 uses `screenspace={false}` (the pixel branch, as in `drei/core/Outlines.js:41-47`), and hull meshes are marked as helpers with raycast disabled. |
| I2 | Fixed | CUT_Z_BARREL and ST1 list all 64 screw elements in `show_whole`. CUT_X2450 and X4120 use the pre-cut element plus the xsec cap and hide the elements beyond the plane. |
| I3 | Fixed | `swap` is now per state, and `missing_target_rule` is in both the contract and snippet §6. Script check: every exterior and interior name in every state list resolves. Every `swap` value also appears in a show list. No state shows two copies of the same place (full with cut-only, or exterior with its pre-cut). |
| I4 | Fixed | `interior_export.items` has 215 nodes, each with a role, states and parent. The pipe uses the layered `_lo`/`_y0` halves. The die `_y0` parts are included. The gear halves are CUT_PUMP only, with `_full` gears for ST1 and FREE. The gearbox schematic, its ghost and 2 rotors are added. The object count now reads 618. Small leftover in **N5**. |
| I5 | Fixed | Q2 is now a hybrid that keeps the existing pre-cuts, citing DECISIONS 29, at a cost of about 0 h and about 54 k triangles. |
| I6 | Fixed | New `closed_test` (allows edges with 3+ faces, checks winding and signed volume), measured at 269/343 exterior and 100/130 interior, plus `cap: force/none` and a `_y0` fallback for the feed column. |
| I7 | Fixed | Script check: no `die_open` target, and none of their 10 parts, appears in CUT_DIE_PLAN `hide` or `clip`. Only the end plates and deckles are clipped. |
| I8 | Fixed | W1.4 now does `obj.data = obj.data.copy()`, split parts come from `new_from_object(evaluated)`, the fingerprint includes per-mesh vertex and polygon counts, and the risk table cites `Mesh.validate()`. I checked that the A-A pieces carrying shape keys (`int_die_*_y0`) were decimated through `new_from_object` and have no modifiers left (`a1b_common.py:386`, `a1b_die.py:258`), so W1.7's claim that shape keys survive holds. |
| I9 | Fixed | W2.1 runs one GLB per MCP call (warm-up and fingerprint are separate calls), with `try/finally`, `done.json`, a check on disk and a rule never to re-run an export while its result is unknown. |
| I10 | Fixed | Q1 states the crash risk, and the new Q6 adds a `save_as_mainfile(copy=True)` session backup. One path nit in **N4**. |
| M1 | Fixed | The naming text now says child meshes take the glTF mesh name. The registry indexes only nodes with `kind`. |
| M2 | Fixed | 189 + 1 = 190 devices everywhere. All `devices[].parts` lists match `object_to_device` plus the splits (script). `dev_screws` has a real bbox and a documented identity transform. |
| M3 | Fixed | `make_cut_states.py` fails on any unknown name. `valve_run.fill_switch` covers the `_lo` variants. FLOWS maps to FULL. |
| M4 | Fixed | `precompileStates` with `compileAsync`. The 200 ms is measured on the second entry. `?selfcheck` forces DPR 1. |
| M5 | Fixed | The CPU 4× throttle target is now soft, with a `join` fallback and an early measurement. |
| M6 | Fixed | GHOST_SC shows `p_anim_ghost_sc` and hides the exterior hood. FREE excludes ghost and marker kinds and cut-only roles. A new FREE side effect is listed in **N3**. |
| M7 | Fixed | No `unit_settings` writes at all, and the `ze155_anim` settings are in the fingerprint. |
| AD1 | Fixed | Đợt 1 now exports the head, valve and sc-adapter `_lo` set that CUT_Z_BARREL needs (script check: every node a Đợt 1 state references belongs to the Đợt 1 scope). There is a missing-target rule. The gearbox rotors are in the contract. Peel runs at runtime. The backflush piston is inside `sc_index`, so there are still 3 clips. The 2D control loop is in Đợt 3 and Q4 agrees. W1 can be re-run. |
| AD2 | Fixed | Stream B uses a synthetic `standin.glb` shaped like the contract. |
| AD3 | Fixed | Drivers go on `ze155_web` `rot_*` only, and the export code mutes them and zeroes `rot_*` inside `try/finally`. I checked that the pump-gear phase is baked into the mesh (`a1b_pump.py:108`), so zeroing the rotors does not break the gear mesh. |
| AD4 | Fixed | Review of slice N overlaps the build of slice N+1, except for the last slice. The estimate is 6–7 h (best case 5 h), and the critical path is stated. |

## New findings

- **N1 (I)**
  - **Where:** snippets §1 (`useModel`) and §3 (`installRaycastFilter`, the `userData.__rayWrapped` guard).
  - **Problem:** In dev mode, the C1 filter silently disappears:
    - React StrictMode, which the create-vite `react-ts` template turns on, mounts, cleans up and remounts effects.
    - drei `Bvh` cleanup sets `child.raycast = Mesh.prototype.raycast` (`drei/core/Bvh.js:76-81`), which throws away the wrapper.
    - On the remount, `installRaycastFilter` returns early because `userData.__rayWrapped` is already true.
  - **Effect:** Under `npm run dev`, which is exactly how §6 says the reviewer tests, removed halves, hidden meshes and ghosts become pickable again. A5, A5b and A6 then fail for a reason the builder cannot see.
  - **Fix:** Any one of these:
    - mark the wrapper function itself (e.g. `raycast.__ze`) and re-wrap whenever `mesh.raycast` is not the wrapper;
    - return a cleanup that unwraps the meshes and clears the flag;
    - build the BVH in `installRaycastFilter` and drop `<Bvh>`.

- **N2 (I)**
  - **Where:** snippet §7 `setFreeClip`.
  - **Problem:** `setFreeClip` changes visibility directly (`o.visible = false` for cut-only, ghost and marker nodes; `e.visible = false` for `free_swap` keys; `interiorRoot.visible = true`). It does not use the recorded `setVisible`, so `resetCuts` cannot undo these changes.
  - **Effect:** After FREE, the swapped exterior parts stay hidden in FULL and in every fixed state: 6 barrels, 2 domes, the feed column parts, the head, valve and adapters, and the pump. For example, CUT_X2450 then shows no B1, B2, B5 or B6, and FULL has holes. `setFreeClip(null)` also leaves the interior root visible.
  - **Fix:** Export a recorded `setVisible` from `Cuts.ts` and use it in `setFreeClip`. Add a selfcheck step that goes FREE → FULL and compares the visible-node set with the set right after load.

- **N3 (M)**
  - **Where:** contract `FREE` (`show_role: ["full"]`) and snippet §7.
  - **Problem:**
    - FREE shows every node with the `full` role. That includes both the RUN and the DRAIN valve fills (`p_int_fill_valve_drain_bolt` and `_drain_port` are full), so both melt paths appear at once.
    - FREE keeps the exterior `p_melt_screen_changer` and shows the full disc. A1b reports that the disc rim sticks 67–190 mm through that hood, so it shows above the hood on the kept side.
  - **Fix:** In FREE, apply the valve fill switch so only the run set shows. Either hide the disc set in FREE, or swap the hood for an opaque copy of the raised hood from `anim_ghost_sc`.

- **N4 (M)**
  - **Where:** PLAN Q6, `save_as_mainfile(filepath='out/ze155_session_backup.blend', copy=True)`.
  - **Problem:** A relative `filepath` resolves against Blender's process working directory, which is often `/` when Blender is launched from the GUI, not against the folder of the .blend. The backup could fail, or land somewhere unexpected.
  - **Fix:** Use the absolute path `/Users/manhhaycode/m3d-e2e/ze155-tdie/out/ze155_session_backup.blend`, or `'//ze155_session_backup.blend'` (the open file is in `out/`). Then check that the file exists, that `bpy.data.filepath` is unchanged, and that `is_dirty` is still True.

- **N5 (M)**
  - **Where:** contract `interior_export.items`.
  - **Problem:**
    - The screw-zone fills are written in shorthand (`int_fill_screw_z01..z09 (9)` and `..._lo`), which leaves out the real zone suffixes (`_feed`, `_melt` … `_pump`). The cut states use the real names. Neither the snippet's `expand` regex nor a literal expansion in W1.6 or `make_cut_states.py` would produce them.
    - Items have no `slice` field, although W1.6 says to copy "theo `interior_export.items` của đợt". Which slice an item belongs to is stated only in the prose of `slices`.
  - **Fix:** List the 9 + 9 real names (the `fills` table has them). Add `slice: 1 | 2` to each item.

## Verdict

**Needs another fix: small, and in the snippets only.**
- N1 and N2 are a few lines each in `r3f-snippets.md` §1, §3 and §7. A quick check of those three sections is enough; another full review is not needed.
- PLAN 1.1 and contract 1.1 are otherwise consistent and close all round-1 findings.
- The cut-state data passes every script check, and Đợt 1 is self-contained.

Once N1 and N2 are fixed, the package is ready to show the user for approval. N3–N5 can be folded in at the same time or left to the builders.

## Round 2b (after the fixer's N1–N5 changes)

**How I checked:**
- re-read snippets §1, §3, §7, §11 and §14, and the versions table;
- re-ran my contract scripts;
- ran the fixer's probe `scratchpad/tsprobe/run/test.cjs` (Node, no WebGL): ALL PASS, 13 checks covering N1, A5b, N2 and N3.

| ID | Status | Evidence |
|---|---|---|
| N1 | Fixed | `<Bvh>` is gone. `installRaycastFilter` builds one `MeshBVH` per geometry and assigns the shared `filteredRaycast`, so a re-run always re-installs it, even after a StrictMode remount. Installation is checked by function identity. `selfcheck().rayUnfiltered` counts meshes without the filter. The probe confirms the filter is re-installed after a Bvh-style reset, and that the far back-face hit on a cap survives. |
| N2 | Fixed | `setFreeClip` changes visibility only through the exported, recorded `setVisible`, so `resetCuts` returns to FULL exactly. The new `cutRoundTrip()` hook runs FULL → FREE → FULL and each state → FREE → back, and the probe passes it. |
| N3 | Fixed | FREE `hide` now holds the DRAIN valve fills and the disc set, and `valve_run` in FREE switches between the RUN and DRAIN sets with suffix `''`. |
| N4 | Fixed | Q6 and `contract.safety` use the absolute path, then check that the file exists, that `bpy.data.filepath` is unchanged and that `is_dirty` is still True. |
| N5 | Fixed | All 142 items have `slice` (59 in Đợt 1, 83 in Đợt 2). The screw-zone fills carry their real names. Script check: every name in every state resolves (0 unresolved). |

**Slice exception:** it does not weaken the safety check in a way that matters.
- It skips only names that match an `interior_export` item whose `slice` is later than the current export. A typo matches no item, so it still fails the step.
- At the Đợt 2 export nothing is later, so the full strict check applies.
- Script check: the only slice-1 state that references slice-2 items is FREE (36 names: the melt-line full parts, the sc disc set and the valve fills). Those exterior keys then follow `missing_target_rule`.
- Small residual risk: a slice-1 *teaching* state that wrongly names a slice-2 item would only log a line in Đợt 1. None does today. `make_cut_states.py` could fail if a non-FREE slice-1 state hits the exception.

**New issues, both Minor:**
- **R1 (M), contract `node_kinds.cut_state.required`:** this schema still lists the 1.0 keys (`keep_whole`, `swap_then_clip`, `show_interior`). It contradicts `cut_model.keys` and the 1.1 states. Today no tool validates against it, but a stream-C builder who writes `make_cut_states.py` or `check_glb.py` from this schema would require keys that no state has. Fix: replace it with the `cut_model.keys` set (`hide`, `swap`, `clip`, `show_whole`, `show_clipped`, `ghost`, `peel`, `clips_on_enter`, plus `plane`, `box_m`, `slice`).
- **R2 (M), snippet §11 valve fill switch:** the mixer `'finished'` listener reacts to *any* action on the interior mixer, such as `die_open`'s choker-bar action. If the state changes before `valve_run` ends, it can also flip the valve fill sets after the switch. Fix: check `e.action === acts[0]` in the listener, and remove the listener in `resetCuts` or `applyCutState`.

**Regressions:** none found. Removing `<Bvh>` keeps the all-hits behaviour, because `firstHitOnly` is never set. FREE, the fixed states and the hooks use the new recorded path consistently.

**Final verdict: ready to show the user for approval.** R1 and R2 are Minor and can be fixed by the builders or folded into the next edit.
