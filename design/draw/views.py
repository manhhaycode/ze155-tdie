#!/usr/bin/env python3
"""Scaled orthographic views of parts.json for Blender camera backgrounds.

    uv run -q --with matplotlib --with numpy --with pillow python design/draw/views.py

Writes drawings/views/<name>.png, drawings/views.json (METHOD.md §2 format) and
drawings/views/check/<name>_parts.json (pixel bounds of every part's silhouette, used by verify_views.py).
White background, black outlines, light grey fills per group, no text.  Context parts (roll stack, rails,
sheet) are drawn as grey outlines without fill so that they never hide the machine; the floor slab is
omitted (a grey floor line marks Z = 0 in elevations); the mezzanine grating is drawn unfilled in plan
views (it is see-through), its beams stay filled.
"""
import json
import math

from PIL import Image, ImageDraw

import geom
from geom import VIEWS, View, scene, item_bounds, ROOT, P

OUT = ROOT / "drawings"
VDIR = OUT / "views"

GROUP_GREY = {"base": 206, "drive": 192, "feed": 226, "barrel": 214, "vacuum": 200, "melt": 210, "die": 222,
              "control": 232, "util": 186, "context": None}
SHADE = {"dark": 112, "mid": 165, "light": 240}

# name: (view key, px_per_mm, (xmin, xmax), (ymin, ymax), (zmin, zmax))  world extents of the crop
SPECS = {
    "front": ("front", 0.2, (-6000, 12800), None, (-300, 6600)),
    "rear": ("rear", 0.2, (-6000, 12800), None, (-300, 6600)),
    "top": ("top", 0.2, (-6000, 12800), (-5200, 3100), None),
    "die_end": ("die_end", 0.2, None, (-5200, 3100), (-300, 6600)),
    "drive_end": ("drive_end", 0.2, None, (-5200, 3100), (-300, 6600)),
    "drive_front": ("front", 0.5, (-5800, 500), None, (-100, 2800)),
    "barrel_front": ("front", 0.5, (-150, 6100), None, (-100, 2300)),
    "feed_front": ("front", 0.5, (-1250, 2000), None, (1300, 6400)),
    "melt_front": ("front", 1.0, (5650, 9250), None, (-50, 2400)),
    "die_front": ("front", 1.0, (8950, 10350), None, (-50, 3000)),
    "die_end_detail": ("die_end", 0.5, None, (-2500, 3000), (-50, 3200)),
    "melt_top": ("top", 0.8, (5650, 9950), (-2900, 1700), None),
}


def view_frame(name):
    key, s, xr, yr, zr = SPECS[name]
    v = VIEWS[key]
    ext = {0: xr, 1: yr, 2: zr}

    def rng(vec):
        i = int(abs(vec).argmax())
        lo, hi = ext[i]
        sgn = vec[i]
        return sorted((sgn * lo, sgn * hi)), i, sgn
    (u0, u1), iu, su = rng(v.R)
    (w0, w1), iw, sw = rng(v.U)
    W = int(round((u1 - u0) * s))
    Hh = int(round((w1 - w0) * s))
    uc, wc = (u0 + u1) / 2, (w0 + w1) / 2
    center = [0.0, 0.0, 0.0]
    center[iu] = uc * su
    center[iw] = wc * sw
    il = int(abs(v.L).argmax())
    center[il] = 0.0
    return v, s, W, Hh, uc, wc, center


def to_px(u, w, s, W, Hh, uc, wc):
    return W / 2 + s * (u - uc), Hh / 2 - s * (w - wc)


def render(name):
    v, s, W, Hh, uc, wc, center = view_frame(name)
    img = Image.new("RGB", (W, Hh), "white")
    dr = ImageDraw.Draw(img)
    thick = 2 if s >= 0.5 else 1
    if v.U[2] > 0.5:  # elevation: floor line at Z = 0
        y = Hh / 2 - s * (0 - wc)
        dr.line([(0, y), (W, y)], fill=(160, 160, 160), width=1)
    items = scene(v, exclude=("ctx_floor",))
    bounds = {}
    for it in items:
        grp = P[it["part"]]["group"]
        ctx = grp == "context"
        g = GROUP_GREY[grp]
        if it["shade"] in SHADE and g is not None:
            g = SHADE[it["shade"]]
        fill = None if (ctx or not it["fill"] or g is None) else (g, g, g)
        col = (150, 150, 150) if ctx else (0, 0, 0)
        lw = 1 if (ctx or it["lw"] == "thin") else thick
        if it["type"] == "poly":
            pts = [to_px(a, b, s, W, Hh, uc, wc) for a, b in it["geo"]]
            if len(pts) >= 3 and it.get("noline"):
                if fill:
                    dr.polygon(pts, fill=fill)
            elif len(pts) >= 3:
                dr.polygon(pts, fill=fill, outline=col, width=lw)
            elif len(pts) == 2:
                dr.line(pts, fill=col, width=lw)
        elif it["type"] == "circle":
            (a, b), r = it["geo"]
            cx, cy = to_px(a, b, s, W, Hh, uc, wc)
            rp = r * s
            if rp < 0.6:
                dr.point((cx, cy), fill=col)
            else:
                dr.ellipse([cx - rp, cy - rp, cx + rp, cy + rp], fill=fill, outline=col, width=min(lw, max(1, int(rp))))
        else:
            pts = [to_px(a, b, s, W, Hh, uc, wc) for a, b in it["geo"]]
            dr.line(pts, fill=col, width=1)
        if it["sil"]:
            a0, a1, b0, b1 = item_bounds(it)
            pa0, pb1 = to_px(a0, b0, s, W, Hh, uc, wc)
            pa1, pb0 = to_px(a1, b1, s, W, Hh, uc, wc)
            bb = bounds.setdefault(it["part"], [1e9, -1e9, 1e9, -1e9])
            bounds[it["part"]] = [min(bb[0], pa0), max(bb[1], pa1), min(bb[2], pb0), max(bb[3], pb1)]
    img.save(VDIR / f"{name}.png", optimize=True)
    (VDIR / "check").mkdir(parents=True, exist_ok=True)
    (VDIR / "check" / f"{name}_parts.json").write_text(json.dumps({k: [round(x, 2) for x in b] for k, b in bounds.items()}, indent=0))
    entry = {"image": f"views/{name}.png", "width_px": W, "height_px": Hh, "px_per_mm": s,
             "center_mm": [round(c, 3) for c in center], "right": v.rs, "up": v.us, "look": v.ls}
    return entry


def main():
    VDIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for name in SPECS:
        out[name] = render(name)
        print(name, out[name]["width_px"], "x", out[name]["height_px"], out[name]["px_per_mm"], "px/mm")
    (OUT / "views.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
