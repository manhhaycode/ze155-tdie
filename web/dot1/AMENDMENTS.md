# Amendments to PLAN-DOT1.md (orchestrator, approved by the user on 2026-10-05)

These override `web/PLAN-DOT1.md` where they conflict. Source: `web/review-dot1-01.md`.

## Scope (review M2): build in two milestones; Đợt 1b is deferred
- **Milestone 1a**, shown to the user first:
  - `line.glb` loaded;
  - device grouping at runtime, 190 devices;
  - selection like Blender: hover outline, click orange outline + Box3Helper + info panel, double-click or F `fitToBox`, Alt+click single part, Esc;
  - the raycast filter installed (`rayUnfiltered === 0` under `npm run dev`);
  - a basic info panel.
  The device tree with Vietnamese search may land shortly after 1a.
- **Milestone 1 (full Đợt 1):**
  - interior lazy-load;
  - the fixed states FULL, CUT_FEED, CUT_Z_BARREL, CUT_X2450, CUT_X4120 with caps (pre-cut variants and runtime caps per the plan), **without the peel animation**;
  - the FREE plane on X/Y/Z with caps;
  - the screws rotating, via runtime pivots, at 300 rpm shown 20× slower;
  - `cutRoundTrip().ok`, `capCheck` cases, state switch ≤ 200 ms;
  - the device tree, the info panel and the toolbar.
- **Deferred to Đợt 1b** (do NOT build now):
  - the peel animation for CUT_Z_BARREL: just show the cut state;
  - tuning the precompile timing beyond a simple safe version;
  - the `pickSweep` reporting tool;
  - the performance trace.

## I1: acceptance criterion D2
- **Gate:** `__ze.selectAll()` selects 190/190 devices by code, and every device can be selected from the device tree.
- **Not a gate:** ray-pickability from the screen, because many devices are enclosed (barrels B3–B6 under covers, etc.). A later `pickSweep` may report it against a computed visible list.

## I2: one state queue
- Every cut-state change goes through ONE serial queue: user clicks, camera presets, interior load, and any shader precompile pass.
- After a precompile pass, re-apply the state the user is currently in.
- A click during precompile is queued; it never interleaves.
- Keep precompile simple. One acceptable approach: precompile once, right after the interior loads, inside the queue, then re-apply the current state.

## Minors
- **M (FREE note):** the FREE plane uses ONE shared local clipping plane on the relevant materials, not `renderer.clippingPlanes`, so the ground and helpers are not cut. Fix the contradicting note in the stand-in `cut_states.dot1.json` when generating the real `cut_states.json`.
- **M (Vite HMR):** the registry must rebuild on hot reload, or the dev page must force a full reload when scene modules change. The registry must never stay empty after an HMR update.
- **M (unsaved edits):** the export reads only the saved `out/ze155_anim.blend`. The user knows to save before an export. Builder A records the .blend mtime and size in the build report.

## Small decisions (all as the planner recommended)
- BVH strategy: CENTER.
- Rolls: forced caps (`cap: force`) with a visual check; if the caps look wrong, use `none` and note it.
- The FREE state also shows slice-2 interiors: yes.
- Entering a state moves the camera to the state's preset (from `shots.json`): yes, inside the state queue.
