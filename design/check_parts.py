#!/usr/bin/env python3
"""Validate design/parts.json for the ZE 155 line.

    uv run -q python design/check_parts.py

Checks
  1. schema: required fields, types, bbox order, enums, colour format, optional geometry fields;
     repeated items (count > 1) need positions_mm (or pitch_mm + start_mm + axis_dir), pipes need
     path_mm, multi-hose pipes need one paths_mm entry per hose;
  2. every connects_to target exists;
  3. connected parts touch/overlap within TOL at at_mm (at_mm inside both bboxes grown by TOL);
  4. nothing floats: each part has z0 = 0 or touches another part (bbox gap <= TOL), and every
     part is reachable from a floor-standing part through touching parts;
  5. connections: from/to exist, medium valid, path endpoints lie in the from/to bboxes (+TOL);
then prints the overall envelope without context and for the full line (floor excluded).
Exit code 1 on any error.
"""
import json
import re
import sys
from collections import deque
from pathlib import Path

TOL = 5.0
HERE = Path(__file__).resolve().parent
REQ = ["id", "group", "name_vi", "shape", "bbox_mm", "material", "colour_hex", "connects_to", "source"]
SHAPES = {"box", "cyl", "revolve", "extrude", "frame", "sheet", "pipe", "composite"}
AXES = {"X", "Y", "Z"}
PLANES = {"XZ", "YZ", "XY"}
MEDIA = {"melt", "water", "vacuum", "oil", "hydraulic", "power", "signal", "material", "mechanical", "air"}
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
FLOOR_ID = "ctx_floor"


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def vec(v, n):
    return isinstance(v, list) and len(v) == n and all(num(x) for x in v)


def inside(pt, b, tol=TOL):
    return all(b[2 * i] - tol <= pt[i] <= b[2 * i + 1] + tol for i in range(3))


def gap(a, b):
    """Largest separation along any axis (<= 0 means overlap)."""
    return max(max(a[2 * i] - b[2 * i + 1], b[2 * i] - a[2 * i + 1]) for i in range(3))


def main():
    path = HERE / "parts.json"
    data = json.loads(path.read_text())
    errs, warns = [], []

    # ------------------------------------------------------------ top level
    meta = data.get("meta")
    if not isinstance(meta, dict):
        errs.append("meta missing")
    else:
        for k in ("units", "axes", "version"):
            if k not in meta:
                errs.append(f"meta.{k} missing")
        if meta.get("units") != "mm":
            errs.append("meta.units must be 'mm'")
    parts = data.get("parts")
    if not isinstance(parts, list) or not parts:
        print("ERROR: parts missing")
        return 1

    # ------------------------------------------------------------ 1. schema
    ids = {}
    for k, p in enumerate(parts):
        pid = p.get("id", f"#{k}")
        for f in REQ:
            if f not in p:
                errs.append(f"{pid}: missing '{f}'")
        if not isinstance(pid, str) or not re.match(r"^[a-z][a-z0-9_]*$", pid):
            errs.append(f"{pid}: id must be ascii snake_case")
        if pid in ids:
            errs.append(f"{pid}: duplicate id")
        ids[pid] = p
        for f in ("group", "name_vi", "material", "source"):
            if f in p and (not isinstance(p[f], str) or not p[f].strip()):
                errs.append(f"{pid}: '{f}' must be a non-empty string")
        if p.get("shape") not in SHAPES:
            errs.append(f"{pid}: shape '{p.get('shape')}' not in {sorted(SHAPES)}")
        b = p.get("bbox_mm")
        if not vec(b, 6):
            errs.append(f"{pid}: bbox_mm must be 6 numbers")
        elif not (b[0] < b[1] and b[2] < b[3] and b[4] < b[5]):
            errs.append(f"{pid}: bbox_mm not ordered x0<x1, y0<y1, z0<z1: {b}")
        if not isinstance(p.get("colour_hex"), str) or not HEX.match(p.get("colour_hex", "")):
            errs.append(f"{pid}: colour_hex '{p.get('colour_hex')}' not #RRGGBB")
        if "axis" in p and p["axis"] not in AXES:
            errs.append(f"{pid}: axis '{p['axis']}' not X|Y|Z")
        if "center_mm" in p:
            if not vec(p["center_mm"], 3):
                errs.append(f"{pid}: center_mm must be 3 numbers")
            elif vec(b, 6) and not inside(p["center_mm"], b, 0.5):
                errs.append(f"{pid}: center_mm outside bbox")
        for f in ("radius_mm", "length_mm", "count", "pitch_mm"):
            if f in p and (not num(p[f]) or p[f] < 0):
                errs.append(f"{pid}: {f} must be a non-negative number")
        if "profile_mm" in p:
            pr = p["profile_mm"]
            if not (isinstance(pr, list) and len(pr) >= 3 and all(vec(q, 2) for q in pr)):
                errs.append(f"{pid}: profile_mm must be >= 3 [r, h] pairs")
            elif "axis" not in p:
                errs.append(f"{pid}: profile_mm needs axis")
            elif any(q[0] < 0 for q in pr):
                errs.append(f"{pid}: profile_mm radius negative")
        if "outline_mm" in p:
            o = p["outline_mm"]
            if not isinstance(o, dict) or o.get("plane") not in PLANES:
                errs.append(f"{pid}: outline_mm.plane must be XZ|YZ|XY")
            elif not (isinstance(o.get("pts"), list) and len(o["pts"]) >= 3 and all(vec(q, 2) for q in o["pts"])):
                if not (o.get("closed") is False and isinstance(o.get("pts"), list) and len(o["pts"]) >= 2):
                    errs.append(f"{pid}: outline_mm.pts must be >= 3 [u, v] points")
            elif not (num(o.get("d0")) and num(o.get("d1")) and o["d0"] < o["d1"]):
                errs.append(f"{pid}: outline_mm needs d0 < d1")
            elif vec(b, 6):
                ax = {"XZ": (0, 2, 1), "YZ": (1, 2, 0), "XY": (0, 1, 2)}[o["plane"]]
                us = [q[0] for q in o["pts"]]
                vs = [q[1] for q in o["pts"]]
                if (min(us) < b[2 * ax[0]] - TOL or max(us) > b[2 * ax[0] + 1] + TOL or
                        min(vs) < b[2 * ax[1]] - TOL or max(vs) > b[2 * ax[1] + 1] + TOL or
                        o["d0"] < b[2 * ax[2]] - TOL or o["d1"] > b[2 * ax[2] + 1] + TOL):
                    errs.append(f"{pid}: outline_mm exceeds bbox")
        if "path_mm" in p:
            pa = p["path_mm"]
            if not (isinstance(pa, list) and len(pa) >= 2 and all(vec(q, 3) for q in pa)):
                errs.append(f"{pid}: path_mm must be >= 2 [x, y, z] points")
            elif vec(b, 6) and not all(inside(q, b) for q in pa):
                errs.append(f"{pid}: path_mm point outside bbox")
        # C1: repeated items and pipes must carry placeable geometry
        cnt = p.get("count", 1)
        if p.get("shape") == "pipe":
            if cnt > 1:
                pas = p.get("paths_mm")
                if not (isinstance(pas, list) and len(pas) == cnt):
                    errs.append(f"{pid}: pipe with count {cnt} needs paths_mm with {cnt} paths")
            elif "path_mm" not in p and "paths_mm" not in p:
                errs.append(f"{pid}: pipe needs path_mm")
        elif cnt > 1:
            has_pos = isinstance(p.get("positions_mm"), list)
            has_pitch = all(k in p for k in ("pitch_mm", "start_mm", "axis_dir"))
            if not (has_pos or has_pitch):
                errs.append(f"{pid}: count {cnt} needs positions_mm or pitch_mm + start_mm + axis_dir")
        if "paths_mm" in p:
            pas = p["paths_mm"]
            if not (isinstance(pas, list) and pas and all(
                    isinstance(pa, list) and len(pa) >= 2 and all(vec(q, 3) for q in pa) for pa in pas)):
                errs.append(f"{pid}: paths_mm must be a list of >= 2-point [x, y, z] polylines")
            elif vec(b, 6) and not all(inside(q, b) for pa in pas for q in pa):
                errs.append(f"{pid}: paths_mm point outside bbox")
        if "item_axis" in p:
            ia = p["item_axis"]
            if not vec(ia, 3) or abs(sum(v * v for v in ia) - 1) > 0.02:
                errs.append(f"{pid}: item_axis must be a unit vector")
        if "item_axes" in p:
            ias = p["item_axes"]
            if not (isinstance(ias, list) and all(vec(a, 3) and abs(sum(v * v for v in a) - 1) <= 0.02 for a in ias)):
                errs.append(f"{pid}: item_axes must be a list of unit vectors")
            elif len(ias) != len(p.get("positions_mm", [])):
                errs.append(f"{pid}: item_axes must have one axis per position")
        if "beams_mm" in p:
            bms = p["beams_mm"]
            if not (isinstance(bms, list) and all(isinstance(m, dict) and vec(m.get("from"), 3) and vec(m.get("to"), 3)
                                                  and isinstance(m.get("section"), str) for m in bms)):
                errs.append(f"{pid}: beams_mm items need section, from[3], to[3]")
            elif vec(b, 6) and not all(inside(m["from"], b) and inside(m["to"], b) for m in bms):
                errs.append(f"{pid}: beams_mm endpoint outside bbox")
        if "positions_mm" in p:
            ps = p["positions_mm"]
            sz = p.get("item_mm", [0, 0, 0])
            if not (isinstance(ps, list) and all(vec(q, 3) for q in ps)) or not vec(sz, 3):
                errs.append(f"{pid}: positions_mm must be [x, y, z] items, item_mm 3 numbers")
            else:
                if "count" in p and p["count"] != len(ps):
                    errs.append(f"{pid}: count {p['count']} != {len(ps)} positions")
                axes = p.get("item_axes") or ([p["item_axis"]] * len(ps) if "item_axis" in p else None)
                for n, q in enumerate(ps):
                    if axes and n < len(axes) and vec(axes[n], 3):
                        # item_mm = [d, d, L] in the item frame: world half-extent = L/2|a_i| + d/2 sqrt(1 - a_i^2)
                        dd, ll = sz[0], sz[2]
                        half = [ll / 2 * abs(axes[n][a]) + dd / 2 * (max(0.0, 1 - axes[n][a] ** 2)) ** 0.5 for a in range(3)]
                    else:
                        half = [sz[a] / 2 for a in range(3)]
                    lo = [q[a] - half[a] for a in range(3)]
                    hi = [q[a] + half[a] for a in range(3)]
                    if vec(b, 6) and not (inside(lo, b) and inside(hi, b)):
                        errs.append(f"{pid}: item at {q} (size {sz}) exceeds bbox")
                        break
        if "details" in p and not (isinstance(p["details"], list) and all(isinstance(d, str) for d in p["details"])):
            errs.append(f"{pid}: details must be a list of strings")
        ct = p.get("connects_to")
        if not isinstance(ct, list):
            errs.append(f"{pid}: connects_to must be a list")
        else:
            if not ct:
                warns.append(f"{pid}: connects_to empty")
            for c in ct:
                if not (isinstance(c, dict) and isinstance(c.get("part"), str) and isinstance(c.get("interface"), str)
                        and vec(c.get("at_mm"), 3)):
                    errs.append(f"{pid}: connects_to item needs part, interface, at_mm[3]: {c}")

    # ------------------------------------------------------------ 2+3. connects_to
    n_links = 0
    for pid, p in ids.items():
        for c in p.get("connects_to", []):
            t = c.get("part")
            if t not in ids:
                errs.append(f"{pid}: connects_to target '{t}' does not exist")
                continue
            if t == pid:
                errs.append(f"{pid}: connects_to itself")
                continue
            a, bq = p["bbox_mm"], ids[t]["bbox_mm"]
            at = c["at_mm"]
            n_links += 1
            if not inside(at, a):
                errs.append(f"{pid} -> {t}: at_mm {at} not on/in {pid} bbox {a}")
            if not inside(at, bq):
                errs.append(f"{pid} -> {t}: at_mm {at} not on/in {t} bbox {bq}")
            if gap(a, bq) > TOL:
                errs.append(f"{pid} -> {t}: bboxes {gap(a, bq):.1f} mm apart")

    # ------------------------------------------------------------ 4. floating
    plist = list(ids.values())
    grounded = set()
    for p in plist:
        if abs(p["bbox_mm"][4]) <= 0.5 or p["id"] == FLOOR_ID:
            grounded.add(p["id"])
    touch = {p["id"]: [] for p in plist}
    for i, p in enumerate(plist):
        for q in plist[i + 1:]:
            if gap(p["bbox_mm"], q["bbox_mm"]) <= TOL:
                touch[p["id"]].append(q["id"])
                touch[q["id"]].append(p["id"])
    for p in plist:
        pid = p["id"]
        if pid in grounded:
            continue
        if not [t for t in touch[pid] if t != FLOOR_ID]:
            errs.append(f"{pid}: floats (z0 = {p['bbox_mm'][4]}, touches nothing)")
    seen = set(grounded)
    dq = deque(grounded)
    while dq:
        u = dq.popleft()
        for v in touch[u]:
            if v not in seen:
                seen.add(v)
                dq.append(v)
    for p in plist:
        if p["id"] not in seen:
            errs.append(f"{p['id']}: not connected to the floor through touching parts")

    # ------------------------------------------------------------ 5. connections
    conns = data.get("connections", [])
    if not isinstance(conns, list):
        errs.append("connections must be a list")
        conns = []
    cids = set()
    for c in conns:
        cid = c.get("id", "?")
        if cid in cids:
            errs.append(f"connection {cid}: duplicate id")
        cids.add(cid)
        for f in ("id", "from", "to", "medium", "type", "path_mm"):
            if f not in c:
                errs.append(f"connection {cid}: missing '{f}'")
        if c.get("medium") not in MEDIA:
            errs.append(f"connection {cid}: medium '{c.get('medium')}' invalid")
        for end in ("from", "to"):
            if c.get(end) not in ids:
                errs.append(f"connection {cid}: {end} '{c.get(end)}' does not exist")
        pa = c.get("path_mm", [])
        if not (isinstance(pa, list) and len(pa) >= 2 and all(vec(q, 3) for q in pa)):
            errs.append(f"connection {cid}: path_mm must be >= 2 points")
            continue
        if c.get("from") in ids and not inside(pa[0], ids[c["from"]]["bbox_mm"]):
            errs.append(f"connection {cid}: first path point {pa[0]} not in '{c['from']}'")
        if c.get("to") in ids and not inside(pa[-1], ids[c["to"]]["bbox_mm"]):
            errs.append(f"connection {cid}: last path point {pa[-1]} not in '{c['to']}'")

    # ------------------------------------------------------------ report
    def env(sel):
        bs = [p["bbox_mm"] for p in sel]
        return [min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs),
                max(b[3] for b in bs), min(b[4] for b in bs), max(b[5] for b in bs)]

    groups = {}
    for p in plist:
        groups[p["group"]] = groups.get(p["group"], 0) + 1
    print(f"parts: {len(plist)}  connects_to links: {n_links}  connections: {len(conns)}")
    print("groups: " + ", ".join(f"{g} {n}" for g, n in groups.items()))
    mach = [p for p in plist if p["group"] != "context"]
    line = [p for p in plist if p["id"] != FLOOR_ID]
    for name, sel in (("machine (without context)", mach), ("full line (context, floor excluded)", line)):
        e = env(sel)
        print(f"envelope {name}: X {e[0]:g} .. {e[1]:g}  Y {e[2]:g} .. {e[3]:g}  Z {e[4]:g} .. {e[5]:g}"
              f"  ->  {e[1] - e[0]:g} x {e[3] - e[2]:g} x {e[5] - e[4]:g} mm")
    for w in warns:
        print("WARN:", w)
    for e in errs:
        print("ERROR:", e)
    print("RESULT:", "FAIL" if errs else "PASS", f"({len(errs)} errors, {len(warns)} warnings)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
