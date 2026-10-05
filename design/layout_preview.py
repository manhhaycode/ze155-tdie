#!/usr/bin/env python3
"""Quick layout check drawn from parts.json: front elevation (from +Y, +X to the left) and plan
(+X to the left, +Y toward the bottom, aligned under the front view).

    uv run -q --with matplotlib python design/layout_preview.py
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "parts.json").read_text())
parts = [p for p in data["parts"] if p["id"] != "ctx_floor"]

LABELS = {
    "drive_motor": "motor 1500 kW", "gearbox": "gearbox", "lantern": "lantern",
    "drive_coupling_guard": "coupling", "barrel_b1": "B1", "barrel_b2": "B2", "barrel_cover_c6": "C6",
    "barrel_cover_c1": "C1", "barrel_vent_dome": "vac dome", "feed_main_hopper": "feeder",
    "melt_screen_changer": "screen ch.", "melt_gear_pump": "pump", "melt_static_mixer": "mixer",
    "die_body_upper": "T-die", "ctx_roll_middle": "rolls", "vac_pump_unit": "vac unit",
    "vac_separator": "separator", "melt_hpu": "HPU", "ctrl_drive_cabinet": "MV drive",
    "ctrl_heater_cabinet": "control cab.", "barrel_vent_dome_2": "vac dome 1", "melt_heater_jbox": "melt jbox", "die_junction_box": "die jbox", "ctrl_die_bolt_cabinet": "bolt cab.", "ctrl_machine_cabinet": "end cab.", "ctrl_hmi": "HMI",
    "feed_stair": "stair", "sidefeed_motor": "side feeder", "melt_startup_valve": "diverter",
    "feed_platform_deck": "mezzanine Z3000", "lube_pump_motor": "lube",
}


def darker(hx, f=0.55):
    h = hx.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


def pipe_polys(path, r, i, j):
    polys = []
    for a, b in zip(path, path[1:]):
        du, dv = b[i] - a[i], b[j] - a[j]
        L = math.hypot(du, dv)
        if L < 1e-6:
            polys.append([(a[i] - r, a[j] - r), (a[i] + r, a[j] - r), (a[i] + r, a[j] + r), (a[i] - r, a[j] + r)])
            continue
        nu, nv = -dv / L * r, du / L * r
        polys.append([(a[i] + nu, a[j] + nv), (b[i] + nu, b[j] + nv), (b[i] - nu, b[j] - nv), (a[i] - nu, a[j] - nv)])
    return polys


def draw(ax, view):
    # view 'front': u = X, v = Z, depth = Y (near = +Y drawn last); 'plan': u = X, v = Y, depth = Z
    if view == "front":
        i, j, k, plane = 0, 2, 1, "XZ"
    else:
        i, j, k, plane = 0, 1, 2, "XY"
    order = sorted(parts, key=lambda p: p["bbox_mm"][2 * k + 1])
    for p in order:
        b = p["bbox_mm"]
        fc, ec = p["colour_hex"], darker(p["colour_hex"])
        alpha = 0.35 if p["group"] == "context" else 0.85
        if p["id"] in ("feed_platform_deck",) and view == "plan":
            alpha = 0.18
        if p["id"].startswith("barrel_cover") and view == "plan":
            alpha = 0.55
        if view == "front" and b[3] < -1300:
            alpha = 0.15
        o = p.get("outline_mm")
        if p.get("positions_mm") and p.get("item_mm"):
            sz = p["item_mm"]
            for q in p["positions_mm"]:
                ax.add_patch(Rectangle((q[i] - sz[i] / 2, q[j] - sz[j] / 2), sz[i], sz[j],
                                       fc=fc, ec=ec, lw=0.4, alpha=alpha))
            continue
        if o and not o.get("closed", True) and view == "front":
            ax.plot([b[0], b[1]], [b[5], b[5]], color=fc, lw=2.0)
            ax.plot([b[0], b[1]], [b[5] - 550, b[5] - 550], color=fc, lw=1.0)
            continue
        if (p.get("path_mm") or p.get("paths_mm")) and p["shape"] != "sheet":
            for pa in (p.get("paths_mm") or [p["path_mm"]]):
                for poly in pipe_polys(pa, p.get("radius_mm", 20), i, j):
                    ax.add_patch(Polygon(poly, closed=True, fc=fc, ec=ec, lw=0.3, alpha=alpha))
            continue
        if o and o["plane"] == plane and o.get("closed", True):
            ax.add_patch(Polygon(o["pts"], closed=True, fc=fc, ec=ec, lw=0.5, alpha=alpha))
            continue
        if o and o["plane"] == plane and not o.get("closed", True):
            xs, ys = zip(*o["pts"])
            ax.plot(xs, ys, color=fc, lw=2.0, alpha=0.9)
            continue
        ax_name = p.get("axis")
        if p["shape"] in ("revolve", "cyl") and ax_name and "XYZ"[k] == ax_name:
            c = p["center_mm"]
            r = (b[2 * i + 1] - b[2 * i]) / 2
            ax.add_patch(Circle((c[i], c[j]), r, fc=fc, ec=ec, lw=0.5, alpha=alpha))
            continue
        ax.add_patch(Rectangle((b[2 * i], b[2 * j]), b[2 * i + 1] - b[2 * i], b[2 * j + 1] - b[2 * j],
                               fc=fc, ec=ec, lw=0.4, alpha=alpha))
    for pid, txt in LABELS.items():
        p = next((q for q in parts if q["id"] == pid), None)
        if not p:
            continue
        b = p["bbox_mm"]
        u = (b[2 * i] + b[2 * i + 1]) / 2
        v = b[2 * j + 1] + 60 if view == "front" else (b[2 * j] + b[2 * j + 1]) / 2
        ax.text(u, v, txt, fontsize=7, ha="center", va="bottom" if view == "front" else "center",
                color="#111", bbox=dict(fc="white", ec="none", alpha=0.6, pad=0.5))


fig, (a1, a2) = plt.subplots(2, 1, figsize=(26, 15), sharex=True,
                             gridspec_kw={"height_ratios": [6.6, 8.0]})
draw(a1, "front")
draw(a2, "plan")
for a in (a1, a2):
    a.set_aspect("equal")
    a.grid(True, lw=0.3, alpha=0.5)
    a.axvline(0, color="red", lw=0.6, ls="--")
a1.axhline(0, color="k", lw=1)
a1.axhline(1200, color="red", lw=0.4, ls=":")
a1.set_xlim(13000, -6200)          # +X to the left (front elevation seen from +Y)
a1.set_ylim(-100, 6500)
a2.set_ylim(3200, -5200)           # +Y toward the bottom (operator side nearest the front view)
a1.set_title("ZE 155 A UT 34D + T-die — front elevation from +Y (X=0 barrel drive face, red dash; axis Z=1200, red dots)")
a2.set_title("plan view (+Y operator side at bottom)")
a1.set_ylabel("Z mm")
a2.set_ylabel("Y mm")
a2.set_xlabel("X mm (flow → left)")
fig.tight_layout()
out = HERE / "layout_preview.png"
fig.savefig(out, dpi=90)
print("wrote", out)
