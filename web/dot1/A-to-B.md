# Builder A → builder B (Đợt 1)

## 1. Integration point I1: done, 2026-10-05 14:04:13
`make -C web all` ran export → compress → analyze → data → verify → publish with exit 0. These files in `web-check/public/` are now the real build output:
- `models/line.glb`, `models/interior.glb`;
- `data/{devices,node_map,cut_states,rotors,materials}.json`.

**What changed against your stand-ins:**
- **GLBs:** nothing. They are byte-identical to `build/probe/models/*` (`cmp` checked; the export and the compression are deterministic).
- **Data:** identical to `web/dot1/*.dot1.json` (deep compare, key order ignored), except two strings in `cut_states.json`:
  - `generated_from` now names `build/reports/glb_analysis.json`;
  - `states.FREE.clip` now says "one shared local plane on the materials, never renderer.clippingPlanes" (amendment M1).

So you only need to reload the page and re-run `selfcheck`.

**Rules for `public/models` and `public/data`:**
- Re-running `make -C web all` (about 7 s) overwrites them. Do not edit them by hand.
- If the data must change, change `web/tools/make_data.py` and tell me.

## 2. A6 UI: what I import from your modules
Every import of your code goes through one file of mine, `src/ui/bind.ts`:

```ts
export { useUi } from '../store'      // your zustand hook, the Ui interface of PLAN §4.2.9 (+ your extras)
export { reg } from '../scene/rig'    // reg.meshesOfDevice(id, true), reg.devices
```

Your `store.ts` already exports `useUi` with these names, and `tsc -p tsconfig.app.json` passes with my files (exit 0). I no longer import `applyPreset`: I use your `resetView()` instead (see below). Please keep these names stable, or tell me before you rename one.

**Fields and actions I read from `useUi` (all as in §4.2.9):**
- **State:** `hovered`, `selected`, `selectedPart`, `state`, `free: {axis, offset, flip}`, `rotorMode`, `interiorWanted`, `interiorLoaded`, `busy`, plus your extras `pending` and `cutVersion`.
- **Actions:** `hover(id|null)`, `select(id|null, part?)`, `clear()`, `zoomTo(id|null)`, `setStateId(id): Promise<void>`, `setFree(partial)`, `setRotorMode(m)`, plus your extra `resetView()`.

**How the components use them:**
- **Toolbar:**
  - The state buttons call `setStateId`. They are never disabled; your queue serializes the clicks (I2). The button of the state being applied gets `data-pending` (from `pending`).
  - In FREE, the axis buttons call `setFree({axis, offset: offset_default_m[axis]})`. The slider (`slider_range_m[axis]`, step 5 mm) calls `setFree({offset})` on every input event. The flip checkbox calls `setFree({flip})`.
  - The rotor buttons call `setRotorMode`.
  - "Về góc nhìn của trạng thái" calls your `resetView()`. It is always enabled; in FREE your action uses the preset of `prevFixed`.
- **Busy label:** "Đang tải phần bên trong…" shows while `interiorWanted && !interiorLoaded`. Otherwise "Đang chuyển trạng thái…" shows while `busy`.
- **InfoPanel:**
  - It shows "Nằm bên trong – mở một mặt cắt để xem" when `reg.devices.size > 0 && reg.meshesOfDevice(id, true).length === 0`.
  - It re-renders on `cutVersion` and `interiorLoaded`.
- **DeviceTree:**
  - A click calls `select(id)` then `zoomTo(id)`.
  - Mouse enter and leave call `hover(id)` and `hover(null)`.
  - The selected item is highlighted, its section expands, and it scrolls into view; this also works when the selection comes from the canvas.

## 3. Mounting (your App.tsx)
- **Where:** all three components are DOM overlays, so mount them outside `<Canvas>`. They read the data with React 19 `use(dataPromise)`, so put them inside a `<Suspense fallback={null}>`.

```tsx
import { Toolbar } from './ui/Toolbar'
import { DeviceTree } from './ui/DeviceTree'
import { InfoPanel } from './ui/InfoPanel'
// …
<Suspense fallback={null}><Toolbar /><DeviceTree /><InfoPanel /></Suspense>
```

- **CSS:** each component imports `./ui.css` itself.
- **Layout:**
  - The toolbar is fixed at the top. It writes its height to the CSS variable `--ze-top` on `<html>`, and the side panels start below it.
  - The tree is 300 px wide on the left; the info panel is 340 px wide on the right.
  - Only the panels take pointer events; the canvas stays clickable everywhere else.
- **Keys:** the search box is an `<input id="ze-search">`. Your global F/Esc handler must ignore keys while focus is in an input (PLAN §4.2.5). In the search box, Esc clears the text and blurs; Enter selects and zooms to the first result.
- **Test hooks:**
  - `#ze-search`;
  - `.ze-tree-item[data-device="<id>"]`, with `aria-current="true"` on the selected item;
  - `.ze-toolbar button[data-state="<id>"]`, with `aria-pressed`;
  - `#ze-info`.

## 4. Packages
A6 needs no new npm packages: it uses only react and zustand (through your store). Nothing to install.
