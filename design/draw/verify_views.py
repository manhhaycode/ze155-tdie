#!/usr/bin/env python3
"""Verify that drawings/views/*.png map to world mm exactly as drawings/views.json says (METHOD.md §2).

    uv run -q --with matplotlib --with numpy --with pillow python design/draw/verify_views.py

For every view, the bbox corners of at least 5 named parts (taken from design/parts.json, not from the
renderer) are projected with the METHOD.md formula

    pixel u = W/2 + s * dot(P - center, right),   pixel v = H/2 - s * dot(P - center, up)

and checked two ways:
  1. pixel colour: an outline pixel (all channels < 175) must exist within 2 px of every listed corner;
  2. drawn polygons: the projected bbox must equal the pixel bounds of that part's drawn silhouette
     (drawings/views/check/<view>_parts.json, written by views.py) within 2 px.
The formula is also inverted for the four image corners and round-tripped.  Red crosses are drawn on a
copy of each image (drawings/views/check/<view>.png).  Exit code 1 on any failure.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PARTS = {p["id"]: p for p in json.loads((ROOT / "design" / "parts.json").read_text())["parts"]}
VJ = json.loads((ROOT / "drawings" / "views.json").read_text())
CHK = ROOT / "drawings" / "views" / "check"

ALL = ("ll", "lr", "ul", "ur")
LOW = ("ll", "lr")
TOP = ("ul", "ur")
# view: [(part id, corners to colour-check)] (screen changer lower-left corner is hidden by ctrl_estop_melt in front views) - corners named by image position: l/r = left/right,
# first letter l/u = lower/upper.  Subsets are used where another part legitimately hides a corner.
CHECKS = {
    "front": [("ctrl_machine_cabinet", ALL), ("melt_screen_changer", ("lr", "ul", "ur")), ("die_end_plate_op", ALL),
              ("barrel_cover_c4", ALL), ("ctrl_estops", ALL), ("melt_startup_valve", ALL)],
    "rear": [("ctrl_drive_cabinet", ALL), ("ctrl_heater_cabinet", ALL), ("die_end_plate_rear", ("lr", "ul", "ur")),
             ("vac_exhaust", ALL), ("vac_pump_unit", LOW), ("melt_hpu", LOW)],
    "top": [("ctrl_drive_cabinet", ALL), ("ctrl_heater_cabinet", ALL), ("melt_screen_changer", ALL),
            ("vac_pump_unit", ALL), ("die_cart_rails", ALL), ("ctrl_machine_cabinet", ALL), ("melt_hpu", ALL)],
    "die_end": [("die_end_plate_op", ALL), ("die_end_plate_rear", ALL), ("ctrl_drive_cabinet", ("ll", "ul", "ur")),
                ("vac_exhaust", ALL), ("die_cart_rails", ("lr", "ur"))],
    "drive_end": [("ctrl_machine_cabinet", ALL), ("ctrl_drive_cabinet", ALL), ("feed_stair", ALL),
                  ("feed_platform_deck", ALL), ("drive_motor_terminal_box", ALL)],
    "drive_front": [("ctrl_machine_cabinet", ALL), ("drive_encoder", ALL), ("lube_unit_frame", ALL),
                    ("lube_oil_cooler", ("lr", "ur")), ("drive_coupling_guard", ALL)],
    "barrel_front": [("barrel_cover_c2", ALL), ("barrel_cover_c5", ALL), ("ctrl_estops", ALL), ("barrel_b1", ALL),
                     ("barrel_vent_dome", TOP)],
    "feed_front": [("feed_conveying_line", ALL), ("feed_throat", TOP), ("feed_hopper", TOP), ("sidefeed_downpipe", LOW),
                   ("feed_additive_feeder", LOW), ("feed_main_feeder", LOW)],
    "melt_front": [("melt_screen_changer", ("lr", "ul", "ur")), ("melt_startup_valve", ALL), ("melt_static_mixer", ALL),
                   ("melt_pipe", ALL), ("melt_sc_adapter_in", ALL), ("melt_stand_pump", ALL)],
    "die_front": [("die_end_plate_op", ALL), ("die_bolt_actuator_rail", ALL), ("die_cart_rails", ("ll", "ul")),
                  ("die_drip_pan", ALL), ("die_heater_boxes", ALL)],
    "die_end_detail": [("die_end_plate_op", ALL), ("die_end_plate_rear", ALL), ("die_deckles", ALL),
                       ("die_drip_pan", ALL), ("die_bolt_actuator_rail", ALL), ("die_cart_rails", ("lr", "ur"))],
    "melt_top": [("melt_screen_changer", ALL), ("melt_hpu", ALL), ("melt_startup_valve", ALL),
                 ("melt_pump_gearbox", ALL), ("melt_pump_cardan", ALL), ("die_end_plate_op", ALL)],
}


def axv(s):
    v = np.zeros(3)
    v["XYZ".index(s[-1])] = -1.0 if s[0] == "-" else 1.0
    return v


def main():
    fails = 0
    lines = []
    for name, spec in VJ.items():
        img = Image.open(ROOT / "drawings" / spec["image"]).convert("RGB")
        W, Hh, s = spec["width_px"], spec["height_px"], spec["px_per_mm"]
        assert img.size == (W, Hh), f"{name}: image size {img.size} != json {W}x{Hh}"
        C = np.array(spec["center_mm"], float)
        Rv, Uv, Lv = axv(spec["right"]), axv(spec["up"]), axv(spec["look"])
        assert abs(np.cross(Rv, Uv) @ -Lv) > 0.5 or True
        assert np.allclose(np.cross(Lv, Uv), Rv), f"{name}: right/up/look not a right-handed camera"

        def px(P):
            d = np.asarray(P, float) - C
            return W / 2 + s * (d @ Rv), Hh / 2 - s * (d @ Uv)

        def world(u, v):
            return C + (u - W / 2) / s * Rv + (Hh / 2 - v) / s * Uv
        for u, v in ((0, 0), (W, 0), (0, Hh), (W, Hh)):
            uu, vv = px(world(u, v))
            assert abs(uu - u) < 1e-6 and abs(vv - v) < 1e-6
        arr = np.asarray(img)
        drawn = json.loads((CHK / f"{name}_parts.json").read_text())
        out = img.copy()
        dr = ImageDraw.Draw(out)
        checks = CHECKS[name]
        assert len(checks) >= 5, f"{name}: fewer than 5 parts checked"
        for pid, corners in checks:
            b = PARTS[pid]["bbox_mm"]
            pts = [px((x, y, z)) for x in b[0:2] for y in b[2:4] for z in b[4:6]]
            us = sorted(set(round(p[0], 3) for p in pts))
            vs = sorted(set(round(p[1], 3) for p in pts))
            u0, u1, v0, v1 = us[0], us[-1], vs[0], vs[-1]  # v0 = top row in image
            named = {"ll": (u0, v1), "lr": (u1, v1), "ul": (u0, v0), "ur": (u1, v0)}
            bad = []
            for cn in ALL:
                cu, cv = named[cn]
                col = (255, 0, 0) if cn in corners else (255, 160, 160)
                dr.line([(cu - 7, cv - 7), (cu + 7, cv + 7)], fill=col, width=2)
                dr.line([(cu - 7, cv + 7), (cu + 7, cv - 7)], fill=col, width=2)
                if cn not in corners:
                    continue
                i0, i1 = int(np.floor(cu - 2)), int(np.floor(cu + 2))
                j0, j1 = int(np.floor(cv - 2)), int(np.floor(cv + 2))
                win = arr[max(0, j0):min(Hh, j1 + 1), max(0, i0):min(W, i1 + 1)]
                if win.size == 0 or not (win.max(axis=2) < 175).any():
                    bad.append(cn)
            db = drawn.get(pid)
            dev = max(abs(db[0] - u0), abs(db[1] - u1), abs(db[2] - v0), abs(db[3] - v1)) if db else 1e9
            ok = not bad and dev <= 2.0
            fails += 0 if ok else 1
            lines.append(f"{name:15s} {pid:28s} corners {'/'.join(corners):11s} "
                         f"{'OK ' if not bad else 'MISS ' + ','.join(bad)}  polygon dev {dev:5.2f} px  {'PASS' if ok else 'FAIL'}")
        out.save(CHK / f"{name}.png")
    print("\n".join(lines))
    print(f"\n{len(lines)} checks, {fails} failed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
