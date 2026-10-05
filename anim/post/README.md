# Post-production: labels, HUD and MP4

Blender renders the 5 275 frames without text. This folder draws every label and HUD element with Pillow and
assembles the MP4 with the ffmpeg binary of `imageio-ffmpeg`. Nothing here uses Blender.
Editing a label text only means re-running the overlay; the 3D frames are not rendered again.

Run everything from the workspace root `/Users/manhhaycode/m3d-e2e/ze155-tdie/`.

| File | Role |
|---|---|
| `ANCHORS.md` | Contract with the A3 builder: per-frame 2D anchor files exported from Blender (format, framing rules, reference exporter) |
| `check_timing.py` | Checks the pacing rules of `shots.json` and the font coverage → `timing_report.md` |
| `overlay.py` | Label layout and drawing of labels + HUD, in parallel processes, resumable |
| `assemble.py` | MP4 H.264, CRF 18, 25 fps; preview mode |
| `common.py` | Shared helpers: fonts, wrapping, timing, camera simulation and projection |
| `anchor_precheck_simulated.md` | Layout pre-check of the whole film with cameras simulated from the `shots.json` keys |
| `test/` | Test without real renders: `run_test.sh`, `make_test_inputs.py`, synthetic anchors, sample frames, previews |

Python always runs as `uv run -q --with pillow --with numpy python …`; add `--with imageio-ffmpeg` for `assemble.py`.

## Inputs and outputs

| | Path | Notes |
|---|---|---|
| in | `anim/shots.json`, `anim/interior_parts.json` | read only |
| in | `anim/render/anchors/<SHOT>.json` | from the A3 builder (`ANCHORS.md`). Missing file: anchors are simulated from the camera keys, and the report says so |
| in | `anim/render/frames/####.png` | Blender frames, frame number = timeline frame 1…5275 (4 digits) |
| out | `anim/render/overlay/####.png` | `--mode overlay` (default): RGBA 1920 × 1080, transparent except text and HUD, ≈ 110 kB each (≈ 0.6 GB for the film) |
| out | `anim/render/final/####.png` | `--mode final`: frame + overlay at the frame's own size, ≈ 2.6 MB each (≈ 14 GB for the film) |
| out | `anim/render/overlay_report.md` | anchor source per shot, warnings, labels without a leader, occluded anchors, box overlaps |
| out | `anim/render/ze155_anim.mp4` | full film; `anim/render/preview.mp4` for previews |

## Steps

### 0. Label timing check (any time)

```sh
uv run -q --with pillow --with numpy python anim/post/check_timing.py
```

Checks R1 each label ≥ max(3 s, 0.4 s/word) = max(75, 10 × words) frames; R2 ≤ 4 labels at once (S15 ≤ 2);
R3 the last label of a shot ≥ 3 s; R4 labels inside their shot and shots tiling 1…5275; R5 the footer on every shot
with a `*`; plus every glyph of every string in the font. Exit code 1 on failure. The full table is written to
`timing_report.md`.

Result for the current `shots.json`: **PASS, 0 failures, 13 notes.** No label breaks the rules under the convention
the file was scheduled with: a label is on screen frame_in…frame_out inclusive, with 8-frame fades. The notes:
- **Crossfades (R2):** at 16 hand-overs a label still fading out overlaps a label fading in, for 8 frames each. Then
  5 labels are partly visible (S15: 3), but never more than 4 (S15: 2) fully opaque. This affects S01, S03
  (2 times), S04 (3 times), S10, S11, S12, S13, S14 and S15 (5 times).
- **Zero margin (R1):** 4 labels reach their minimum only when frame_out is counted (one frame short if it is
  not): S03 L5, S13 L3, S14 L4, S15 L6.
- Not a timing issue, but `shots.json` gives S08 no `hud.strip` key, although the brief lists the screw strip for
  S04/S06/S08. The overlay draws it in S08 as well.

### 1. Anchors from Blender (A3 builder)

See `ANCHORS.md`. The overlay works before this step, with simulated anchors, which is enough for previews.

### 2. Layout pre-check (about 30 s, draws nothing)

```sh
uv run -q --with pillow --with numpy python anim/post/overlay.py --layout-only
```

Read `anim/render/overlay_report.md` → "Labels without a leader for more than 25 % of their time". With the
simulated cameras (`anchor_precheck_simulated.md`), 23 of 74 labels are listed. That is a camera framing to-do for
A3, not a post problem.

### 3. Overlay

```sh
# overlay-only RGBA frames for the whole film (default; composited later by ffmpeg)
uv run -q --with pillow --with numpy python anim/post/overlay.py
# or composited PNGs, e.g. for stills or review
uv run -q --with pillow --with numpy python anim/post/overlay.py --mode final
# subsets / options
uv run -q --with pillow --with numpy python anim/post/overlay.py --range 901-1350,3400-3500
uv run -q --with pillow --with numpy python anim/post/overlay.py --shot S12 --force     # redraw after a text edit
```

- **Resumable:** existing outputs are skipped (written to a temporary name, then renamed). `--force` redraws.
- **Parallel:** `--jobs` (default: CPU count − 1).
- **Speed** with 10 processes on this Mac: ≈ 200 frames/s overlay-only, ≈ 90 frames/s composited with stand-in
  frames. Real render PNGs decode slower, so expect a few minutes for the film. Layout takes ≈ 25 s for all shots.
- **Deterministic:** the layout of a shot is always computed from its first frame, so any subset gives the same
  pixels as a full run.
- **Final mode:** a missing input frame is skipped and reported; `--missing grey` draws on a grey placeholder.
  Frames of another size (e.g. 960 × 540 previews) get the overlay scaled to their size.
- **Fonts:** Arial / Arial Bold from macOS. Every string is checked for missing glyphs before drawing. Set
  `ZE_FONT` / `ZE_FONT_BOLD` for another TTF.

### 4. Assemble

```sh
# full film, ffmpeg composites anim/render/overlay over anim/render/frames (recommended: no 14 GB of composites)
uv run -q --with pillow --with numpy --with imageio-ffmpeg python anim/post/assemble.py --src overlay
# full film from composited frames (overlay.py --mode final)
uv run -q --with pillow --with numpy --with imageio-ffmpeg python anim/post/assemble.py
# preview: frame subset, 960 x 540, CRF 23, veryfast -> anim/render/preview.mp4
uv run -q --with pillow --with numpy --with imageio-ffmpeg python anim/post/assemble.py --src overlay --preview --range 901-1350
```

- H.264 `libx264`, CRF 18, preset slow, yuv420p, 25 fps, faststart. `--size`, `--crf`, `--preset` and `--out`
  override the defaults.
- The full mode refuses gaps in the frame sequence. `--allow-gaps` repeats the previous frame instead, and preview
  mode drops missing frames.
- The frames are linked as a gap-free numbered sequence in a temporary folder next to the output, so any range list
  works.
- The ffmpeg composite blends straight alpha in RGB. It matches the Pillow composite to codec precision: PSNR
  38.7 dB at CRF 18 in the test.

### 5. Test without renders

```sh
sh anim/post/test/run_test.sh        # KEEP=1 keeps the stand-in frames and full-size composites
```

It runs the timing check, then makes stand-in frames (existing stills scaled to 1920 × 1080) and synthetic anchors.
The anchors use the ANCHORS.md format, projected through cameras simulated from the `shots.json` keys; some are
marked occluded, and S15 is sampled every 3rd frame. The script then runs both overlay modes on S04 1140–1260,
S11 3185–3270, S12 3480–3600, S15 4560–4690 and S16 5026–5075 (509 frames), checks resume, and builds the two
previews:
- `test/preview.mp4`, from the composited PNGs;
- `test/preview_overlay.mp4`, composited by ffmpeg.

It also copies the sample frames `test/sample_*.png`.

## What is drawn

| Element | Shots | Source / behaviour |
|---|---|---|
| Title bar | all | shot id + `title_vi` (shrinks to fit), speed badge = `speed_badge_vi` (hidden when "—"), "minh họa" flag pill |
| "minh họa" flag | S01, S04, S06, S08, S10, S12, S14, S15 | shots with schematic flows whose badge does not already say "minh họa" (S03, S07 and S11 say it in the badge) |
| Values panel | S01–S05, S07–S13 | `hud.values`, top left |
| Footer | all with `hud.footer` | "* = giả định (không có nguồn công bố)", bottom left |
| Callouts | S01–S15 | white box + amber accent, 26 px, ≤ 560 px wide, balanced 2-line wrap (numbers stay with their units); leader line + dot; 8-frame fades; dashed leader + hollow dot when occluded |
| Screw strip | S04, S06, S08 | from `interior_parts.json`: 32 elements (SE hatched at their pitch, KB discs, LH red, tip), zones, vent windows 1990–2310 / 3860–4380 (purple), fill degree, schematic pressure up to P1 ≈ 100 bar*, barrels B1–B6. Drawn with X increasing to the left, like the view from the operator side. Moving amber marker at the camera target X, and a white bracket for the X range in frame |
| Legend | S14 | `hud.legend` colours and line styles |
| Block diagram | S15 | 11 blocks of `hud.block_diagram` (process chain + PLC + TIC + STO), loop list (1)–(7). The newest visible S15 label = active loop (amber, animated dashes); the other visible label = previous loop (dim amber) |
| Coat-hanger inset | S11, frames +190…+349 (from `shots.json`) | exaggerated, "không theo tỉ lệ", says the 3D die is near-T (preland 32 → 11 mm); the flow front fills the manifold, then the preland, then pulses uniform exit arrows |
| True-value gauge | S12, from gap_x10 > 0 | "Khe môi thật" 1,00 → 0,85 mm = 1 − 0,15 × lip_push, scale 0,85–1,15, bolt heat dot. Badge: "Tốc độ thực" before the ×10 exaggeration starts, then the ×10 badge from `shots.json` |
| Summary card | S16 | `hud.title` + the 3 points, staggered fade-in in the first 1.5 s |

**Label layout.** Each frame, visible labels are placed in order of appearance, so older labels keep their place.
The candidates sit around the anchor (8 directions × 4 distances), on a coarse screen grid, and at "keep last
offset". The cost adds up:
- the leader length;
- overlaps with other boxes (with a 12 px margin) and with HUD panels;
- covering any anchor;
- leaders crossing leaders or boxes;
- being pushed back from the screen edges.

Boxes follow their anchor and glide to a new spot, never through a bad one. No box overlaps another box in any frame, both in the test shots and in
the whole film with simulated anchors. Anchors off-screen, behind the camera or under a HUD panel get no leader, and they are counted in the report.

**Not implemented:** `alt_if_Q6b` texts are ignored, because Q6 was decided as (a).

## Editing

- **Label text or HUD text:** edit `shots.json` (or the fixed Vietnamese strings at the top of `overlay.py`), then
  run `overlay.py --force --shot …` and `assemble.py`.
- **Anchor point moved in `shots.json`:** the overlay reprojects it from the exported `camera` block (occlusion
  unknown) and warns; re-export that shot's anchors for exact occlusion.
- **Timing changed:** run `check_timing.py` first.
