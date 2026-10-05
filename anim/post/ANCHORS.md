# Anchor contract: Blender (phase A3) → post (overlay.py)

Blender renders the frames without any text. Post draws every label, leader line and HUD element with Pillow.
For that, the A3 builder exports, per shot, where each label's anchor point lands on screen in every frame.
This file is the whole contract. The overlay already runs without the files: it then simulates the cameras from
the `shots.json` keys and marks the result as approximate in its report.

## 1. Files

| What | Where |
|---|---|
| One JSON file per shot | `anim/render/anchors/<SHOT>.json`, e.g. `anim/render/anchors/S04.json` |
| Shots that need one | S01–S15 (every shot with labels). S16 has no labels: the file is optional. |
| Encoding | UTF-8, plain JSON. Compact separators are fine. |
| Example files (synthetic, same format) | `anim/post/test/anchors/S04.json`, `S11`, `S12`, `S15`, `S16` |

## 2. Format

```json
{
  "format": "ze155-anchors/1",
  "shot": "S04",
  "frame_start": 901,
  "frame_end": 1350,
  "ref_resolution": [1920, 1080],
  "frames": [901, 902, 903, "…", 1350],
  "camera_names": ["anim_cam_S04", "…"],
  "anchors": {
    "L0": {"anchor_m": [0.34, 0.45, 1.25], "text": "B1 · cấp liệu · áo nước ≈ 50 °C*",
           "xy": [[812.4, 655.0, 1, 0], "…"]},
    "L1": {"anchor_m": [0.65, 0.15, 1.3], "text": "…", "xy": ["…"]}
  },
  "tracks": {
    "cam_target_m": [[0.5, 0.0, 1.2], "…"],
    "gap_x10": [0.0, "…"],
    "lip_push": [0.0, "…"]
  },
  "camera": {
    "matrix_world": [[1.0, 0.0, 0.0, -0.35, "… 16 floats, row-major"], "…"],
    "lens_mm": [30.0, "…"], "type": ["PERSP", "…"], "ortho_scale": [6.0, "…"], "shift": [[0.0, 0.0], "…"],
    "sensor_width_mm": 36.0, "sensor_fit": "AUTO"
  }
}
```

| Field | Required | Meaning |
|---|---|---|
| `format` | yes | Always `"ze155-anchors/1"`. |
| `frames` | yes | Ascending frame numbers. Every frame of the shot is best. A step of 2–3 is accepted: the overlay interpolates x/y linearly, `in_front` is ANDed and `occluded` is ORed between the two samples. The first and last frame of the shot must be present. |
| `anchors.L<i>` | yes | `i` = index of the label in `shots.json → shots[...].labels` (0-based, file order). |
| `anchors.L<i>.anchor_m` | yes | The world point used (metres), copied from `shots.json`. The overlay compares it with `shots.json`; if it changed there later, the overlay reprojects that label from the `camera` block (or warns if there is none). |
| `anchors.L<i>.text` | no | Copy of the label text, for humans only. Text edits never need a new export. |
| `anchors.L<i>.xy` | yes | One `[x_px, y_px, in_front, occluded]` per entry of `frames`. Pixels in the **1920 × 1080 reference frame, origin top-left, y down**: `x = co.x × 1920`, `y = (1 − co.y) × 1080` with `co = world_to_camera_view(scene, cam, point)`. `in_front` = 1 if `co.z > clip_start`. `occluded` = 1 if an opaque, render-visible object sits between the camera and the point (see §4); write 0 if unsure. Export every frame of the shot, also outside the label's `frame_in..frame_out`. |
| `tracks.cam_target_m` | **S04, S06, S08** | World location (m) of the camera's Track-To target `anim_tgt_<camera>` per frame. It drives the position marker on the screw strip. |
| `tracks.gap_x10`, `tracks.lip_push` | **S12** | Shape-key values (0…1) of `int_die_section_upper` per frame. They drive the ×10 badge and the true-value gauge (1,00 mm − 0,15 × lip_push). Without them the overlay uses the `shots.json` windows (+140…+170, +180…+300). |
| `camera` | recommended | Per-frame camera state. With it the overlay can reproject moved or new anchors without a new export, draw the "in frame" bracket on the screw strip, and orient the strip. `matrix_world` is `cam.matrix_world` flattened row by row. |

Rules: render resolution aspect must be 16:9 (1920 × 1080 or 960 × 540 previews give identical numbers);
pixel aspect 1. Values may be rounded to 0.1 px. Do not put NaN in the file (use a far off-screen value).

## 3. Framing rules the overlay needs from the cameras

An anchor gets a leader line only when it is in the frame and not under a HUD panel. Otherwise the label text
still shows for its full time, but floats without pointing at anything. Keep every anchor inside the frame and
outside these panels for its whole `frame_in..frame_out`:

| Panel (1920 × 1080 px) | Shots | Rectangle x0, y0 – x1, y1 |
|---|---|---|
| Title bar | all | 0, 0 – 1920, 64 |
| Values panel | S01–S05, S07–S13 | 24, 74 – up to 738, up to 180 (size per shot, see `overlay_report.md`) |
| Footer "* = giả định" | all | 24, 1036 – 393, 1068 |
| Screw strip | S04, S06, S08 | 24, 818 – 1896, 1028 (bottom fifth of the frame) |
| Legend | S14 | 24, 828 – 584, 1028 |
| Coat-hanger inset | S11 from frame 3191 | 1296, 72 – 1896, 432 |
| True-value gauge | S12 from gap_x10 > 0 (≈ 3491) | 1456, 832 – 1896, 1028 |
| Block diagram | S15 | 1300, 72 – 1896, 1028 (right third) |
| Summary card | S16 | 240, 96 – 1680, 440 |

**Pre-check with the `shots.json` camera keys** (`anim/post/anchor_precheck_simulated.md`): simulating the cameras from
the keys, 23 of the 74 labels have no leader for more than 25 % of their time, because the anchor leaves the frame or
falls under a panel. The worst cases:
- S03 L5, S05 L3, S07 L2, S07 L3, S15 L1: the anchor is never usable (100 %).
- S15 zone 1: the cameras look from +Y, so the feeder and drive (low X) sit on the right of the frame, under the
  block diagram. Fix it with lens shift, e.g. `shift_x ≈ +0.15`, or by moving the targets, so that all S15 anchors
  stay at x < 1260 px.
- S04 L0, S04 L2, S07 L0, S09 L0: the anchors are low in the frame or behind the strip.
Treat this list as a to-do for the A3 cameras. After the real export, run the check in §5; it reports the same
table from the exported data.

## 4. Occlusion

`occluded` only changes the style: a dashed leader and a hollow dot ("behind something"). The anchor is still
drawn. Rules for the exporter:
- Cast a ray from the camera to the anchor (`scene.ray_cast`). The anchor counts as occluded when the first hit
  is more than 5 mm in front of the point.
- Skip translucent or helper geometry and keep casting past it: ghost shells, fill blocks, flow FX, vent domes drawn
  translucent. The snippet below skips the prefixes `anim_fx_`, `int_fill_` and `anim_ghost_`; extend the list to
  your naming.
- `ray_cast` sees the viewport depsgraph. If shot visibility is keyed only on `hide_render`, objects hidden from
  the render can still block the ray. Key `hide_viewport` together with `hide_render` on the `ax_*` / `anim_*`
  collections, or rely on the `render_visible()` test in the snippet.

## 5. Check after exporting

```sh
uv run -q --with pillow --with numpy python anim/post/overlay.py --layout-only      # no drawing, about 30 s
# -> anim/render/overlay_report.md: anchor source per shot, mismatches, and per label how many frames have
#    no leader (off-screen or under a HUD panel) or an occluded anchor
```

## 6. Reference exporter (Blender side, text only)

This is not run by post. Paste it into one `execute_blender_code` call, then call `export_anchors('S04')` per shot.
`frame_set` cost decides the speed. Time 10 frames first and keep each call under about 2 minutes: pass
`f_from`/`f_to` to export a long shot in chunks (the file is merged by frame), or `step=2`.

```python
import bpy, json, os
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = '/Users/manhhaycode/m3d-e2e/ze155-tdie/'
REF_W, REF_H = 1920, 1080
SKIP = ('anim_fx_', 'int_fill_', 'anim_ghost_')          # translucent / helper objects never occlude
TRACKS = {'S12': {'gap_x10': ('int_die_section_upper', 'gap_x10'),
                  'lip_push': ('int_die_section_upper', 'lip_push')}}


def render_visible(ob):
    return not ob.hide_render and all(not c.hide_render for c in ob.users_collection)


def occluded(scene, dg, cam_pos, p, eps=0.005):
    d = p - cam_pos
    left = d.length - eps
    d.normalize()
    origin = cam_pos.copy()
    for _ in range(16):
        if left <= 0:
            return False
        hit, loc, _n, _i, ob, _m = scene.ray_cast(dg, origin, d, distance=left)
        if not hit:
            return False
        if render_visible(ob) and not ob.name.startswith(SKIP):
            return True
        step = (loc - origin).length + 1e-4
        origin, left = loc + d * 1e-4, left - step
    return False


def export_anchors(shot_id, f_from=None, f_to=None, step=1):
    scene = bpy.context.scene
    assert scene.name == 'ze155_anim', 'make ze155_anim the active scene first'
    assert abs(scene.render.resolution_x * 9 - scene.render.resolution_y * 16) < 16, 'render aspect must be 16:9'
    shot = next(s for s in json.load(open(ROOT + 'anim/shots.json'))['shots'] if s['id'] == shot_id)
    a, b = shot['frames']
    lo, hi = max(a, f_from or a), min(b, f_to or b)
    frames = list(range(lo, hi + 1, step))
    if frames[-1] != hi:
        frames.append(hi)
    path = ROOT + f'anim/render/anchors/{shot_id}.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    recs = {}                                          # frame -> record; merge with an earlier chunk
    if os.path.exists(path):
        old = json.load(open(path))
        for k, f in enumerate(old['frames']):
            recs[f] = {'cam': old['camera_names'][k],
                       'xy': {key: v['xy'][k] for key, v in old['anchors'].items()},
                       'tr': {key: v[k] for key, v in old['tracks'].items()},
                       'c': {key: old['camera'][key][k] for key in ('matrix_world', 'lens_mm', 'type', 'ortho_scale', 'shift')}}
    keep_frame = scene.frame_current
    for f in frames:
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        cam = scene.camera
        cpos = cam.matrix_world.translation.copy()
        rec = {'cam': cam.name, 'xy': {}, 'tr': {}, 'c': {}}
        for i, lab in enumerate(shot['labels']):
            p = Vector(lab['anchor_m'])
            co = world_to_camera_view(scene, cam, p)
            front = co.z > cam.data.clip_start
            occ = front and occluded(scene, dg, cpos, p)
            rec['xy'][f'L{i}'] = [round(co.x * REF_W, 1), round((1 - co.y) * REF_H, 1), int(front), int(occ)]
        tgt = bpy.data.objects.get('anim_tgt_' + cam.name)
        rec['tr']['cam_target_m'] = [round(v, 4) for v in (tgt.matrix_world.translation if tgt else cpos)]
        for name, (obname, key) in TRACKS.get(shot_id, {}).items():
            ob = bpy.data.objects.get(obname)
            kb = ob and ob.data.shape_keys and ob.data.shape_keys.key_blocks.get(key)
            rec['tr'][name] = round(kb.value, 4) if kb else 0.0
        cd = cam.data
        rec['c'] = {'matrix_world': [round(v, 6) for row in cam.matrix_world for v in row], 'lens_mm': round(cd.lens, 3),
                    'type': cd.type, 'ortho_scale': cd.ortho_scale, 'shift': [cd.shift_x, cd.shift_y]}
        recs[f] = rec
    scene.frame_set(keep_frame)
    fl = sorted(recs)
    out = {'format': 'ze155-anchors/1', 'shot': shot_id, 'frame_start': a, 'frame_end': b,
           'ref_resolution': [REF_W, REF_H], 'frames': fl, 'camera_names': [recs[f]['cam'] for f in fl],
           'anchors': {f'L{i}': {'anchor_m': lab['anchor_m'], 'text': lab['text'],
                                 'xy': [recs[f]['xy'][f'L{i}'] for f in fl]} for i, lab in enumerate(shot['labels'])},
           'tracks': {k: [recs[f]['tr'].get(k, 0.0) for f in fl] for k in recs[fl[0]]['tr']},
           'camera': {**{k: [recs[f]['c'][k] for f in fl] for k in ('matrix_world', 'lens_mm', 'type', 'ortho_scale', 'shift')},
                      'sensor_width_mm': scene.camera.data.sensor_width, 'sensor_fit': scene.camera.data.sensor_fit}}
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(',', ':'))
    return f'{shot_id}: {len(fl)} frames, {len(shot["labels"])} anchors -> {path}'
```

Notes on the snippet:
- `world_to_camera_view` already includes lens shift and sensor fit, so `xy` is exact.
- The `camera` block assumes one sensor width per shot; S03 switches cameras at frame 726, and both have 36 mm.
- `cam_target_m` falls back to the camera position when no `anim_tgt_<camera>` exists. The strip marker then
  shows the camera X, which is still close.
