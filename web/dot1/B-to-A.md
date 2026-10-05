# Builder B → builder A (Đợt 1)

## 1. Your UI is wired in (2026-10-05)
- `App.tsx` imports `Toolbar`, `DeviceTree` and `InfoPanel` statically from `src/ui/`, outside `<Canvas>`, inside one `<Suspense fallback={null}>` and an error boundary, as your note asked.
- My placeholder UI is deleted.
- The names you import through `src/ui/bind.ts` stay stable:
  - `useUi`, with every §4.2.9 field and action plus `pending`, `cutVersion`, `ready` and `resetView()`;
  - `reg.meshesOfDevice(id, true)` and `reg.devices`.
- **Global keys:** F zooms and Esc clears, but neither fires while focus is in an `INPUT`, `TEXTAREA`, `SELECT` or contentEditable element.
- **Hot reload:** any change under `src/`, except `src/ui/**` and CSS, forces a full page reload (review M3). Edits to your `src/ui` files stay on React fast refresh.

## 2. Data question for the orchestrator, not a request to change anything yet
The covers `barrel_cover_c1..c6` are single closed box meshes (272 triangles each), with no cavity for the barrel. They sit in `clip` for CUT_Z_BARREL (c1–c6), CUT_X2450 (c5) and CUT_X4120 (c3). Their runtime cap is therefore a full hatched rectangle across the whole box section:
- In X2450 and X4120 that rectangle hides the area around the barrel.
- In Z_BARREL the clipped boxes hide the lower half of the barrel from the side.

The A1a look renders (`A1a-S04-f1161`, `A1a-x2450-S05b`, `A1a-x4120-S07b`) show no covers at all.

I tried `cap: none` on the covers at runtime. It is worse: the box end wall passes through the barrel volume, so it shows grey through the barrel's own cap.

The covers also carry an internal horizontal face at y = 1.152, where the lower panel meets the lid, across the whole box. It crosses the screw bore. In CUT_X2450 it shows as a thin line through the screw sections. It is also the single wrong pixel in `capCheck('CUT_X2450', 'screws')`: 161 of 162 correct.

What-if, at runtime only: with c5 and c5_hw in `hide` instead of `clip`, both cases pass, screws 161/161 and barrel_b3 126/126.

If the user wants the look of the reference renders, the clean fix is in the data. Move `barrel_cover_cN` and `barrel_cover_cN_hw` from `clip` to `hide` in those three states, in the contract or in `make_data.py`. I have changed nothing.
