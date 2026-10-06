#!/usr/bin/env python3
"""make_data.py - Đợt 1 runtime data (PLAN-DOT1 §3.3). Python 3, standard library only.

    python3 tools/make_data.py                     -> build/data/{devices,node_map,cut_states,rotors,materials}.json
    python3 tools/make_data.py --compare dot1      also diff the output against web/dot1/*.dot1.json (task A4)

Inputs: web/model-contract.json, design/parts.json, anim/shots.json, web/build/reports/glb_analysis.json
(exported node names and the closed test come from `check_glb.mjs analyze`, not from the probe).
Port of web/dot1/gen_drafts.py. Any unresolved name or broken exclusion rule stops with exit 1.
"""
import argparse
import collections as C
import json
import math
import os
import re
import sys

WEB = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
WS = os.path.dirname(WEB)
BUILD = os.path.join(WEB, 'build') + os.sep
FIXED = ['FULL', 'CUT_FEED', 'CUT_Z_BARREL', 'CUT_X2450', 'CUT_X4120']
# FLOW (web/PLAN-FLOW.md) is a fixed state too, but it is derived here (build_flow), not read from the contract
FIXED_STATE_IDS = FIXED + ['FLOW']
VARIANT_SUFFIXES = ['_lo', '_y0', '_x2450', '_x4120']
# Output keys that may differ from the web/dot1 drafts on purpose (see web/build/REPORT-A.md).
INTENDED_DRAFT_DIFFS = {
    ('cut_states', 'generated_from'): 'names now resolved against build/reports/glb_analysis.json, not the probe report',
    ('cut_states', 'states.FREE.clip'): 'amendment M1: one shared local plane on the materials, never renderer.clippingPlanes',
}
FREE_CLIP_NOTE = ('all visible parts: one shared local THREE.Plane (freePlane) set as material.clippingPlanes on the '
                  'clipped variants of the visible parts; never renderer.clippingPlanes (that would also cut the '
                  'ground, Box3Helper and outline hulls)')

# ---------------------------------------------------------------- web overrides of the contract states
# Fixer round 1 (web/review/dot1/review-dot1-impl-01.md). The contract and anim/shots.json stay untouched;
# these tables are applied on top of them, after the name rule, and every entry is checked: a name that is
# not where the table expects it stops the build, so a contract change cannot silently void an override.
#
# I1: the barrel covers barrel_cover_c1..c6 are single solid closed boxes with no cavity for the barrel, plus
# an internal panel-joint face (_hw, y = 1.152). Clipped, their full-section caps hide or frame the barrel and
# the joint face crosses the screw bore (the D4 X2450/screws failure). The A1a look renders show no covers in
# these views, so they move from `clip` to `hide`.
COVERS = [f'barrel_cover_c{i}{s}' for i in range(1, 7) for s in ('', '_hw')]
CLIP_TO_HIDE = {
    'CUT_Z_BARREL': COVERS,
    'CUT_X2450': ['barrel_cover_c5', 'barrel_cover_c5_hw'],
    'CUT_X4120': ['barrel_cover_c3', 'barrel_cover_c3_hw'],
}
# I1/I2 follow-up: in CUT_X2450 the uncut cover c6 (x 1.692..2.364) is a solid box around barrel B3. The runtime
# cap is drawn by the back faces of B3's far inner wall (its end face at x = 1.69), so c6's end face at
# x = 2.364 sits in front of the cap and hides it as soon as the wider preset shows the barrel. Hidden too.
# In CUT_X4120 the wider preset (below) brings barrel B6, on the removed side (x >= 4.732), into the left edge.
EXTRA_HIDE = {
    'CUT_X2450': ['barrel_cover_c6', 'barrel_cover_c6_hw'],
    'CUT_X4120': ['barrel_b6'],
}
# M2: in FREE every visible part is clipped; the solid covers become large hatched areas that merge with the
# barrel cap. Hidden in FREE as well (the barrel, heaters and flanges show instead, as in the A1a renders).
FREE_EXTRA_HIDE = COVERS
# I2 / M1: camera presets that replace the shots.json ones (three coordinates, metres; lens on a 36 mm gauge).
# Tuned in the sandbox at 1920 x 1080 so the subject fits the canvas area between the side panels.
CAMERA_OVERRIDES = {
    'FULL': {'pos': [19.2, 8.61, -17.28], 'target': [5.0, 2.0, 0.9], 'lens_mm': 35,
             'source': 'web override (review M1): hero-like view of the whole line from the die end, operator side, '
                       'like out/renders/ze155-hero.png (35 mm, elevation 16 deg); the camera is on the +X side, so '
                       'the FREE default cut X = 3 000 faces it (review M4)'},
    'CUT_X2450': {'pos': [3.807, 1.765, -0.95], 'target': [2.45, 1.2, 0.0], 'lens_mm': 40,
                  'source': 'web override (review I2): direction of shots.json still ST2, 1.75 m instead of 0.77 m and '
                            '40 mm instead of 60 mm, so the flange, the figure-8 bore and some barrel fit between the panels'},
    'CUT_X4120': {'pos': [5.067, 2.021, -1.278], 'target': [4.12, 1.36, 0.0], 'lens_mm': 35,
                  'source': 'web override (review I2 + M5/Codex review): direction of shots.json still ST3, '
                            '1.7 m instead of 1.13 m, 35 mm lens and target lowered to 1.36 m so both screw profiles, '
                            'the whole barrel section and the bottom of the cut face fit at 1920 and 1366 px'},
}

# PLAN-FLOW §4.1: every state button says what the viewer will see; coordinates and zone codes only in the
# tooltip. Overrides the contract label_vi (the contract stays untouched) and adds tooltip_vi.
_NB = ' '  # no-break space inside numbers, as in the UI (fmtInt)
LABEL_OVERRIDES = {
    'FULL': ('Toàn bộ máy', 'Nhìn toàn dây chuyền, không cắt'),
    'CUT_FEED': ('Phễu nạp hạt', 'Bổ dọc phễu và cột nạp, thấy đường hạt rơi vào xi lanh (mặt cắt Y = 0)'),
    'CUT_Z_BARREL': ('Bên trong xi lanh', f'Mở nắp xi lanh, thấy hai trục vít đang quay (mặt cắt Z = 1{_NB}200)'),
    'CUT_X2450': ('Lát cắt hai trục vít',
                  f'Cắt ngang xi lanh B3, thấy lỗ hình số 8 và hai trục vít ăn khớp (X = 2{_NB}450 mm)'),
    'CUT_X4120': ('Lát cắt chỗ hút ẩm',
                  f'Cắt ngang ở lỗ hút chân không thứ 2 của xi lanh B5, nơi hơi ẩm được rút ra (X = 4{_NB}120 mm)'),
    'FREE': ('Tự cắt', 'Tự chọn hướng và vị trí dao cắt'),
    'FLOW': ('Quy trình: hạt → film',
             'Bổ dọc cả dây chuyền, xem hạt nhựa chảy ra rồi thành tấm film (mặt cắt Y = 0)'),
}

# ---------------------------------------------------------------- FLOW (web/PLAN-FLOW.md §2)
# One vertical cut at Blender Y = 0 (three z >= 0 kept) through the whole line. The lists are derived from the
# bbox of every exterior part plus the swaps / pre-cut sets of CUT_FEED, CUT_Z_BARREL, FREE and the Đợt 2
# drafts CUT_PUMP / CUT_DIE_AA (web/dot2/states.dot2.json, read only for these two states).
FLOW_PLANE = {'normal': [0.0, 0.0, 1.0], 'constant': 0.0}
FLOW_CUT_ONLY_FROM = ['CUT_PUMP', 'CUT_DIE_AA']  # their pre-cut cut_only nodes are shown in FLOW too
FLOW_FREE_SWAPS = ['barrel_vent_dome', 'barrel_vent_dome_2', 'melt_head_adapter', 'melt_startup_valve', 'melt_sc_adapter_in']
FLOW_CAMERA = {'pos': [5.9, 6.55, -25.0], 'target': [5.9, 3.0, 0.0], 'lens_mm': 35,
               'source': 'PLAN-FLOW §2.1, tuned in the sandbox (start value pos [6.0, 4.5, -19.0], target [6.0, 1.4, 0.0] '
                         'cut off the feed column and the drive): side view from the operator side, 8 deg high; the whole '
                         'material path x -0.95 ... 12.65 m and the hopper top fit between the side panels and below the '
                         'info panel at 1920 x 1080 and 1366 x 768'}
# §2.2 step 3: closed parts crossing the plane whose volume fills > 80 % of their bbox. Clipped, they become
# large hatched slabs (lesson of review I1), so these are hidden; each entry says why.
FLOW_SOLID_HIDE = {
    **{n: 'review I1: solid barrel cover box (and its joint face); its cap would cover barrel and screw' for n in COVERS},
    'ctrl_machine_cabinet': 'solid cabinet box in front of the barrel; its cap would hide the line behind it',
    'melt_drain_chute': 'solid chute block under the start-up valve; its cap would hide the valve section',
}
# FLOW only: steel and screw sections in neutral greys (runtime caps by cap class, pre-cut za_cap_* materials)
FLOW_CAP_COLORS = {'steel': '#8E959C', 'screw': '#5C636B'}
# solids that stay clipped after the visual check of §7 step 2 (any other solid prints a warning). Checked in the
# sandbox at the FLOW preset and close up (2026-10-06): none of them lies in front of the material path.
_DRIVE = 'drive train upstream of the feed (x < 0): its section reads as the cut drive, no melt path behind it'
FLOW_SOLID_CLIP = {
    'drive_motor_body': _DRIVE, 'drive_motor_cooler': _DRIVE, 'drive_motor_fan_cover': _DRIVE,
    'gbx_housing': _DRIVE, 'lantern_body': _DRIVE + ' (screw B spline shaft stays hidden inside it)',
    'frame_drive_body': 'base frame below the drive; its section is under the line, never over the barrel',
    'frame_process_body': 'base frame below the barrel; its section is under the barrel and the melt path',
}
# exterior parts hidden although the bbox rule keeps them (one line of reason each)
FLOW_EXTRA_HIDE = {
    'melt_screen_changer_logo_in': 'logo plate of the screen changer body, which is a ghost in FLOW (as in GHOST_SC)',
    'melt_screen_changer_logo_out': 'logo plate of the screen changer body, which is a ghost in FLOW (as in GHOST_SC)',
}


class DataError(Exception):
    pass


def load(rel):
    with open(os.path.join(WS, rel), encoding='utf-8') as f:
        return json.load(f)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default=os.path.join(WEB, 'build', 'data'))
    p.add_argument('--analysis', default=os.path.join(WEB, 'build', 'reports', 'glb_analysis.json'))
    p.add_argument('--compare', metavar='DIR', help='diff the output against DIR/*.dot1.json (relative to web/)')
    a = p.parse_args()
    a.out = os.path.abspath(a.out)
    if not (a.out + os.sep).startswith(BUILD):
        raise SystemExit(f'refusing to write outside web/build/: {a.out}')
    return a


def build(analysis):
    con = load('web/model-contract.json')
    shots = load('anim/shots.json')
    parts = load('design/parts.json')
    files = analysis['files']
    L = list(files['line']['names'])
    I = list(files['interior']['names'])
    ALL = set(L) | set(I)
    if len(ALL) != len(L) + len(I):
        raise DataError('a node name appears in both GLBs')
    rename = {'rot_screw_a': 'int_screw_axis_a', 'rot_screw_b': 'int_screw_axis_b'}

    def expand(n):
        m = re.match(r'^(.*_)(\d+)\.\.(\d+)$', n)
        if not m:
            return [n]
        w = len(m.group(2))
        return [f'{m.group(1)}{i:0{w}d}' for i in range(int(m.group(2)), int(m.group(3)) + 1)]

    def conv(n):
        return rename.get(n, n[2:] if n.startswith('p_') else n)

    def names(lst, ctx):
        out = []
        for n in lst:
            for e in expand(n):
                c = conv(e)
                if c not in ALL:
                    raise DataError(f'unresolved name {e} -> {c} ({ctx})')
                if c not in out:
                    out.append(c)
        return out

    def key(n, ctx):
        c = conv(n)
        if c not in ALL:
            raise DataError(f'unresolved swap key {n} -> {c} ({ctx})')
        return c

    # ------------------------------------------------------------ cut_states
    def b2t(p):
        return [round(p[0], 4) + 0.0, round(p[2], 4) + 0.0, round(-p[1], 4) + 0.0]

    def cam(c):
        return {'pos': b2t(c['loc']), 'target': b2t(c['target']), 'lens_mm': c['lens_mm'], 'sensor_mm': 36}

    SH = {s['id']: s for s in shots['shots']}
    ST = {s['id']: s for s in shots['stills']}
    cams = {
        'FULL': dict(cam(SH['S01']['cameras'][0]['keys'][1]), source='shots.json S01 key 2 (frame 151)'),
        'CUT_FEED': dict(cam(SH['S03']['cameras'][1]['keys'][1]), source='shots.json S03b key 2 (frame 900)'),
        'CUT_Z_BARREL': dict(cam(SH['S04']['cameras'][0]['keys'][2]), source='shots.json S04 key 3 (frame 1161) = look A1a-S04-f1161'),
        'CUT_X2450': dict(cam(ST['ST2']['camera']), source='shots.json still ST2 (= S05 key 2)'),
        'CUT_X4120': dict(cam(ST['ST3']['camera']), source='shots.json still ST3 (= S07 key 2)'),
    }
    states = {}
    for sid in FIXED:
        s = con['cut_states'][sid]
        p = s.get('plane')
        out = {'label_vi': s['label_vi'], 'plane': ({'normal': p['normal'], 'constant': p['constant']} if p else None),
               'needs_interior': sid != 'FULL',
               'hide': names(s.get('hide', []), f'{sid}.hide'),
               'swap': {key(k, f'{sid}.swap'): names(v, f'{sid}.swap[{k}]') for k, v in (s.get('swap') or {}).items()},
               'clip': names(s.get('clip', []), f'{sid}.clip'),
               'show_whole': names(s.get('show_whole', []), f'{sid}.show_whole'),
               'show_clipped': names(s.get('show_clipped', []), f'{sid}.show_clipped'),
               'ghost': names(s.get('ghost', []), f'{sid}.ghost'),
               'peel': s.get('peel') and {k: s['peel'][k] for k in ('offset_m', 'duration_s')},
               'camera': cams[sid]}
        if sid == 'FULL':
            out['note'] = 'load state: interior hidden; every recorded change undone (resetCuts)'
        for n in CLIP_TO_HIDE.get(sid, []):  # review I1
            if n not in out['clip'] or n in out['hide']:
                raise DataError(f'CLIP_TO_HIDE {sid}: {n} is not in clip, or already hidden; update the override table')
            out['clip'].remove(n)
            out['hide'].append(n)
        for n in EXTRA_HIDE.get(sid, []):
            if n not in ALL or n in out['hide'] or n in out['clip'] or n in out['show_whole'] + out['show_clipped'] + out['ghost']:
                raise DataError(f'EXTRA_HIDE {sid}: {n} is unknown or already listed in this state; update the override table')
            out['hide'].append(n)
        if sid in CAMERA_OVERRIDES:  # review I2 / M1
            o = CAMERA_OVERRIDES[sid]
            out['camera'] = {'pos': o['pos'], 'target': o['target'], 'lens_mm': o['lens_mm'], 'sensor_mm': 36,
                             'source': o['source'], 'replaces': cams[sid]['source']}
        states[sid] = out
    F = con['cut_states']['FREE']
    ext = con['coordinates']['line_extent_m']
    free_hide = names(F['hide'], 'FREE.hide')
    for n in FREE_EXTRA_HIDE:  # review M2
        if n not in ALL or n in free_hide:
            raise DataError(f'FREE_EXTRA_HIDE: {n} is unknown or already hidden; update the override table')
        free_hide.append(n)
    states['FREE'] = {
        'label_vi': F['label_vi'], 'plane': None, 'needs_interior': True,
        'axis_default': 'x', 'offset_default_m': {'x': 3.0, 'y': 1.2, 'z': 0.0},
        'slider_range_m': {'x': ext['x'], 'y': [float(v) for v in ext['y_three']], 'z': ext['z_three']},
        'slider_range_source': 'model-contract coordinates.line_extent_m',
        'hide': free_hide,
        'swap': {key(k, 'free_swap'): names(v, f'free_swap[{k}]') for k, v in con['free_swap'].items()},
        'show_roles': ['full'], 'hide_roles': ['cut_only', 'ghost', 'marker'],
        'clip': FREE_CLIP_NOTE, 'caps': 'parts with closed=true or cap=force',
        'camera': None,
        'note': 'Đợt 1 exports all interior items, so every FREE swap value resolves (no missing_target exception).'}
    states['FLOW'] = build_flow(states, files, con, names, key)
    for sid, (label, tip) in LABEL_OVERRIDES.items():  # PLAN-FLOW §4.1
        states[sid]['label_vi'] = label
        states[sid]['tooltip_vi'] = tip
    cut_states = {'version': 1, 'flow_version': 1, 'slice': 1,
                  'generated_from': 'model-contract.json cut_states + free_swap, names resolved against the exported GLBs (web/build/reports/glb_analysis.json, from tools/check_glb.mjs analyze); cameras from anim/shots.json converted to three (x, z, -y); web overrides from tools/make_data.py (CLIP_TO_HIDE, EXTRA_HIDE, FREE_EXTRA_HIDE, CAMERA_OVERRIDES, LABEL_OVERRIDES); FLOW from build_flow (PLAN-FLOW §2: bbox rule + CUT_FEED / CUT_Z_BARREL / FREE swaps + web/dot2/states.dot2.json CUT_PUMP / CUT_DIE_AA)',
                  'name_rule': 'contract p_<name> -> <name> (exported Blender object name); rot_screw_a|b -> int_screw_axis_a|b; NN..MM ranges expanded',
                  'plane_rule': 'three.js keeps points with normal . p + constant >= 0',
                  'states': states}

    # ------------------------------------------------------------ node_map
    o2d = con['object_to_device']
    info = {}
    for it in con['interior_export']['items']:
        s = it['src']
        if s.startswith('('):
            continue
        origin = '(origin)' in s
        s = s.split(' ')[0]
        for e in expand(s):
            d = info.setdefault(e, {'device_id': it['host'], 'slice': it['slice']})
            if origin:
                d['moves_as'] = it['role']
            else:
                d['role'] = it['role']
                d['states'] = it.get('states', [])
            d['slice'] = min(d['slice'], it['slice'])
    for e in ('int_screw_axis_a', 'int_screw_axis_b'):
        info[e].update(role='pivot', states=[])
    roll_dev = {'anim_roll_axis_bottom': 'ctx_roll_bottom', 'anim_roll_axis_middle': 'ctx_roll_middle', 'anim_roll_axis_top': 'ctx_roll_top'}
    force_cap = {'ctx_roll_bottom', 'ctx_roll_middle', 'ctx_roll_top'}
    an_line, an_int = files['line']['nodes'], files['interior']['nodes']
    nodes = {}
    for n in L:
        if n in roll_dev:
            if an_line[n]['type'] != 'empty':
                raise DataError(f'{n} is expected to be an empty')
            nodes[n] = {'file': 'line', 'device_id': roll_dev[n], 'kind': 'pivot'}
            continue
        if n not in o2d:
            raise DataError(f'line node {n} has no object_to_device entry')
        if an_line[n]['type'] != 'mesh':
            raise DataError(f'line node {n} is an empty but not a roll pivot')
        nodes[n] = {'file': 'line', 'device_id': o2d[n], 'kind': 'part', 'closed': an_line[n]['closed']}
        if n in force_cap:
            nodes[n]['cap'] = 'force'
    for n in I:
        if n not in info:
            raise DataError(f'interior node {n} has no interior_export item')
        d = info[n]
        rec = {'file': 'interior', 'device_id': d['device_id'], 'kind': 'pivot' if d.get('role') == 'pivot' else 'interior',
               'role': d.get('role'), 'slice': d['slice']}
        if d.get('states'):
            rec['states'] = d['states']
        if d.get('moves_as'):
            rec['moves_in_dot2'] = d['moves_as']
        if 'closed' in an_int[n]:
            rec['closed'] = an_int[n]['closed']
        if (rec['kind'] == 'pivot') != (an_int[n]['type'] == 'empty'):
            raise DataError(f'interior node {n}: kind {rec["kind"]} but GLB node is {an_int[n]["type"]}')
        nodes[n] = rec
    devs = {d['device_id']: d for d in con['devices']}
    for n, r in nodes.items():
        if r['device_id'] not in devs:
            raise DataError(f'{n}: unknown device {r["device_id"]}')
    cnt = C.Counter(r['device_id'] for r in nodes.values())
    missing_dev = [d for d in devs if d not in cnt]
    if missing_dev:
        raise DataError(f'devices without any node: {missing_dev}')
    node_map = {'version': 1, 'slice': 1,
                'doc': 'exported node name (= Blender object name = three userData.name) -> runtime metadata. kind part = exterior mesh node; interior = interior mesh node; pivot = exported empty used only as a rotation parent. closed = position-welded closed test on the RAW GLB (no boundary edge, consistent winding, signed volume > 0). Runtime keeps these under userData.ze.',
                'counts': {'line': len(L), 'interior': len(I), 'devices': len(devs)},
                'nodes': nodes}

    # ------------------------------------------------------------ rotors
    R = {r['node']: r for r in con['rotors']}

    def rot(rid, node, attach, slice_):
        r = R[node]
        for a in attach:
            if a not in ALL:
                raise DataError(f'rotor {rid}: unresolved attach {a}')
        return {'id': rid, 'pivot': node, 'slice': slice_, 'device_id': r['device_id'], 'pivot_m': r['pivot_m'], 'axis': r['axis'],
                'rpm': r['rpm'], 'display_slow': r['display_slow'], 'attach': attach, 'label_vi': r['label_vi']}
    rotors = [
        rot('screw_a', 'rot_screw_a', ['int_screw_axis_a'], 1),
        rot('screw_b', 'rot_screw_b', ['int_screw_axis_b'], 1),
        rot('motor_shaft', 'rot_motor_shaft', ['drive_motor_shaft'], 1),
        rot('flex_coupling', 'rot_flex_coupling', ['drive_flex_coupling'], 1),
        rot('safety_coupling', 'rot_safety_coupling', ['drive_safety_coupling'], 1),
        rot('roll_bottom', 'rot_roll_bottom', ['anim_roll_axis_bottom', 'ctx_roll_bottom'], 1),
        rot('roll_middle', 'rot_roll_middle', ['anim_roll_axis_middle', 'ctx_roll_middle'], 1),
        rot('roll_top', 'rot_roll_top', ['anim_roll_axis_top', 'ctx_roll_top'], 1),
        rot('pump_gear_top', 'rot_pump_gear_top', ['int_pump_gear_top'], 2),
        rot('pump_gear_bottom', 'rot_pump_gear_bottom', ['int_pump_gear_bottom'], 2),
        rot('gbx_input', 'rot_gbx_input', ['int_gbx_schematic_input'], 2),
        rot('gbx_counter', 'rot_gbx_counter', ['int_gbx_schematic_counter'], 2),
    ]
    rotors_json = {'version': 1, 'doc': 'Runtime rotors. For each: create Object3D named pivot at pivot_m (three world, metres, identity rotation) inside dev_<device_id>, attach() the listed exported nodes (subtrees keep world pose), then useFrame: pivot.rotateOnAxis(axis, 2*PI*rpm/60/slow*dt). Never rotate an exported mesh node directly (quantize rewrites mesh-node TRS). Slice 2 entries are loaded but not driven in Đợt 1.',
                   'modes': {'off': 0, 'slow': 'rpm / display_slow', 'real': 'rpm'}, 'default_mode': 'slow',
                   'rotors': rotors}

    # ------------------------------------------------------------ devices
    sec_vi = {'base': 'Khung đế', 'drive': 'Truyền động', 'feed': 'Cấp liệu', 'barrel': 'Xi lanh và trục vít',
              'vacuum': 'Hút chân không', 'melt': 'Đường nhựa nóng chảy', 'die': 'Khuôn phẳng', 'control': 'Điều khiển và cáp',
              'util': 'Khí nén và nước làm mát', 'context': 'Cán, tấm và đo (ngữ cảnh)'}
    pj = {p['id']: p for p in parts['parts']}
    dev_nodes = C.defaultdict(list)
    for n, r in nodes.items():
        dev_nodes[r['device_id']].append(n)
    devices_out = []
    for d in con['devices']:
        p = pj.get(d['device_id'], {})
        b = d['bbox_m']
        devices_out.append({
            'device_id': d['device_id'], 'group': d['group'], 'name_vi': d['name_vi'], 'name_en': d['name_en'],
            'synthetic': d['synthetic'], 'function_vi': p.get('function', ''), 'details_vi': p.get('details', []),
            'connects_to': [{'part': x.get('part'), 'interface_vi': x.get('interface')} for x in p.get('connects_to', [])],
            'bbox_m': b, 'size_mm': [round((b[3] - b[0]) * 1000), round((b[4] - b[1]) * 1000), round((b[5] - b[2]) * 1000)],
            'has_interior': any(nodes[n]['file'] == 'interior' for n in dev_nodes[d['device_id']]),
            'nodes': sorted(dev_nodes[d['device_id']])})
    devices_json = {'version': 1, 'slice': 1, 'size_mm_axes': 'three X (along flow), Y (height), Z (depth)',
                    'sections': [{'group': g, 'name_vi': sec_vi[g]} for g in con['naming']['groups']],
                    'devices': devices_out}

    # ------------------------------------------------------------ materials
    mats = {}
    for m in con['materials']:
        if m['web'] == 'exclude':
            continue
        rec = {'web': m['web'], 'cap_class': m['cap_class'], 'cap_color': m['cap_color']}
        if m.get('three_override'):
            rec['three_override'] = m['three_override']
        mats[m['material']] = rec
    for m in analysis['materials']['used']:
        if m not in mats:
            raise DataError(f'material {m} is used in a GLB but has no materials.json entry')
    materials_json = {'version': 1, 'doc': 'material name -> web handling. cap_color = runtime back-face cap colour (null = no runtime cap); pre-cut za_cap_* materials are drawn as exported. Đợt 1: za_fill_melt keeps the exported translucent amber (FillMaterial is Đợt 2) but gets DoubleSide; za_ghost_vent -> GhostMaterial; ze_sheet_pet / ze_melt_curtain / za_sc_* -> flat overrides (see PLAN-DOT1 §4).',
                      'cap_colors': con['cap_colors'], 'materials': mats}

    out = {'cut_states': cut_states, 'node_map': node_map, 'rotors': rotors_json, 'devices': devices_json, 'materials': materials_json}
    check_states(states, nodes)
    check_flow(states['FLOW'], nodes, files)
    return out


def build_flow(states, files, con, names, key):
    """PLAN-FLOW §2.2 + §3.6: the FLOW state (lists, camera, labels come from LABEL_OVERRIDES) and its `flow` block."""
    dot2 = load('web/dot2/states.dot2.json')
    D = dot2['states']
    split = dot2['name_rules']['virtual_split_parts']  # step 5: split names -> whole nodes (no runtime splits)

    def whole(lst, ctx):
        out = []
        for n in lst:
            n = split.get(n, n)
            if n not in out:
                out.append(n)
        return names(out, ctx)

    an_line = files['line']['nodes']
    # step 1: swaps (never the _lo variants)
    swap = {}
    swap.update(states['CUT_FEED']['swap'])
    for i in range(1, 7):
        swap[f'barrel_b{i}'] = states['CUT_Z_BARREL']['swap'][f'barrel_b{i}']
    for k in FLOW_FREE_SWAPS:
        swap[k] = states['FREE']['swap'][k]
    swap[key('melt_screen_changer', 'FLOW.swap')] = names(D['GHOST_SC']['swap']['melt_screen_changer'], 'GHOST_SC.swap')
    for sid in FLOW_CUT_ONLY_FROM:
        for k, v in D[sid]['swap'].items():
            swap[key(k, f'{sid}.swap')] = names(v, f'{sid}.swap[{k}]')
    # step 2: bbox rule on every exterior mesh part that is not a swap key (three z: zmax <= 0 is the removed half)
    hide, clip, kept = [], [], []
    for n in files['line']['names']:
        a = an_line[n]
        if a['type'] != 'mesh' or n in swap:
            continue
        zmin, zmax = a['bbox'][2], a['bbox'][5]
        (hide if zmax <= 0 else clip if zmin < 0 < zmax else kept).append(n)
    counts = {'bbox_hide': len(hide), 'bbox_clip': len(clip), 'bbox_kept': len(kept), 'swap_keys': len(swap)}
    # step 3: solids
    for n, why in FLOW_SOLID_HIDE.items():
        if n not in clip:
            raise DataError(f'FLOW_SOLID_HIDE: {n} does not cross the plane ({why}); update the table')
        clip.remove(n)
        hide.append(n)
    for n in FLOW_SOLID_CLIP:
        if n not in clip:
            raise DataError(f'FLOW_SOLID_CLIP: {n} is not clipped in FLOW; update the table')
    for n, why in FLOW_EXTRA_HIDE.items():
        if n not in kept:
            raise DataError(f'FLOW_EXTRA_HIDE: {n} is not kept by the bbox rule ({why}); update the table')
        hide.append(n)
    warn = []
    for n in clip:
        a = an_line[n]
        b = a['bbox']
        v = (b[3] - b[0]) * (b[4] - b[1]) * (b[5] - b[2])
        if a.get('closed') and v > 0 and a.get('vol', 0) / v > 0.8 and n not in FLOW_SOLID_CLIP:
            warn.append(f'{n} ({a["vol"] / v:.2f})')
    if warn:
        print('make_data WARNING FLOW: solid parts clipped, check them by eye (PLAN-FLOW §2.2 step 3):', ', '.join(warn), file=sys.stderr)
    # step 4: interior
    screw_b = [f'int_screw_elem_b_{i:02d}' for i in range(1, 33)]
    screw_a = [f'int_screw_elem_a_{i:02d}' for i in range(1, 33)]
    show_whole = []
    for sid in FLOW_CUT_ONLY_FROM:
        show_whole += whole(D[sid]['show_whole'], f'{sid}.show_whole')
    # screw B (axis 71 mm behind the plane, flight radius 83 mm) pokes 12 mm through the cut and would fill the
    # whole bore opening in front of the melt section; clipped, it loses only its flight tips and keeps turning
    show_whole += names(['int_screw_axis_b'], 'FLOW.show_whole')
    hollow = [v for k in ['feed_throat'] + [f'barrel_b{i}' for i in range(1, 7)] + FLOW_FREE_SWAPS for v in swap[k]]
    sc = ['int_sc_disc'] + [f'int_sc_screens_{i:02d}' for i in range(1, 13)] + \
         ['int_sc_channels', 'int_sc_backflush_piston', 'int_fill_sc', 'int_fill_sc_cavities']
    fills = [f'int_fill_screw_{z}' for z in ('z01_feed', 'z02_melt', 'z03_vent1', 'z04_convey', 'z05_mix', 'z06_seal2',
                                             'z07_vent2', 'z08_meter', 'z09_pump')]
    show_clipped = names(hollow + screw_b + fills + sc, 'FLOW.show_clipped')
    ghost = names(D['GHOST_SC']['ghost'], 'GHOST_SC.ghost')
    hide += names(['int_screw_axis_a'] + screw_a + ['int_fill_valve_drain_bolt', 'int_fill_valve_drain_port'], 'FLOW.hide')
    hide += whole(D['CUT_DIE_AA']['hide'], 'CUT_DIE_AA.hide')
    for sid in FLOW_CUT_ONLY_FROM:  # step 5: the pre-cut states' clip lists (ctx_sheet, ctx_melt_curtain, rolls ...)
        clip += whole(D[sid]['clip'], f'{sid}.clip')
    shown = set(show_whole) | set(show_clipped) | set(ghost)
    hide = [n for i, n in enumerate(hide) if n not in hide[:i] and n not in shown]
    clip = [n for i, n in enumerate(clip) if n not in clip[:i] and n not in hide and n not in shown and n not in swap]

    fl = dot2['fills']
    zones = [{k: z[k] for k in ('zone', 'x_m', 'temp_c', 'pitch_m', 'speed', 'phase') if k in z} for z in fl['zones']]
    an_int = files['interior']['nodes']
    for z in zones:  # melt level of the screw zones (the fills of the starve-fed zones are a bed, not the full bore)
        n = f'int_fill_screw_{z["zone"]}'
        if z['speed'] == 'screw':
            if n not in an_int:
                raise DataError(f'FLOW: screw zone {z["zone"]} has no fill node {n}')
            z['fill_top_m'] = round(an_int[n]['bbox'][4], 4)
    rpm = abs(next(r for r in con['rotors'] if r['node'] == 'rot_screw_b')['rpm'])
    sh = fl['sheet']
    L1 = round(math.pi * 0.4005, 4)
    # take-off run after the top roll, from the ctx_sheet vertices (build/models line.glb, |z| < 1.2 m): straight at
    # y 2.805 to the idler near x 11.40, down the incline to the conveyor at y 1.15, then flat to x 12.5. The dot2
    # draft had one straight segment to x 12.5, which gave the incline and the conveyor part the wrong path length.
    takeoff = [[9.776, 2.805], [11.40, 2.805], [11.46, 2.74], [11.70, 1.31], [11.88, 1.15], [12.5, 1.15]]
    L3 = round(sum(math.dist(takeoff[i], takeoff[i + 1]) for i in range(len(takeoff) - 1)), 4)
    flow = {
        'doc': 'PLAN-FLOW §3: illustration with numbers, not CFD. Temperatures are the zone set points (assumed, '
               'design-anim §2), not the pellet core temperature. Speeds: screw zones pitch * rpm / 60 * kScrew '
               '(kScrew off 0, slow 1/20, real 1); rolls * kRoll (off 0, slow 1, real 1).',
        'screw_rpm': rpm,
        'phase_ramp_x_m': fl['phase_ramp_x_m'],
        'colors': {**fl['colors'], 'sheet_clear': '#E8EEF0'},
        'opacity': fl['opacity'], 'opacity_solid': 0.08,
        'heat_stops': [[20, '#2F5DA8'], [120, '#4FB0C6'], [220, '#F2C94C'], [300, '#D7301F']],
        'heat_range_c': [20, 300],
        'zones': zones,
        'melt': {'stripe_m': 0.12, 'speed_zone': 'z09_pump', 'source': fl['speeds']['melt']},
        'die': {'origin_m': fl['die']['origin_m'], 'radius_m': fl['die']['radius_m'], 'temp_c': fl['die']['temp_c']},
        'curtain': {'x_m': [9.576, 9.776], 'temp_c': [270, 250], 'speed_m_s_real': 0.347, 'stripe_m': 0.05,
                    'source': fl['speeds']['roll_lip'] + '; temperatures assumed'},
        'sheet': {'path_three_xy': sh['path_three_xy'][:2], 'takeoff_xy': takeoff, 'roll_x_max_m': 10.18,
                  'select_rule': 'x > roll_x_max_m, or y > 2.79 and x > 9.776 -> take-off polyline; else y < 2.002 -> '
                                 'middle wrap; else top wrap',
                  'stripe_m': sh['stripe_m'], 'stripe_width': sh['stripe_width'],
                  'speed_m_s_real': sh['speed_m_s_real'], 'clear_at_m': 0.3,
                  'lengths_m': [L1, L1, L3],
                  'temp_profile': [[0, 250], [L1, 70], [round(2 * L1, 4), 50], [round(2 * L1 + L3, 4), 35]],
                  'source': sh['source'] + '; temperatures 250 -> 70 -> 50 -> 35 °C assumed'},
        'pellets': {
            'N': 2000, 'size_m': 0.009, 'scale_note': 'PET pellet about 3 mm, drawn x3',
            'fall_speed_m_s': 0.6,
            'path_a_xy': [[-0.45, 2.8], [-0.45, 2.45], [0.09, 2.01], [0.3, 1.8], [0.34, 1.55]],
            'path_a_source': 'build/models line.glb vertices at |z| < 0.2 m: downpipe vertical part x -0.575 ... -0.325 '
                             'down to y 2.36, then inclined to its lower end (0.00 ... 0.18, 1.92 ... 2.10); hopper '
                             'body x 0.15 ... 0.53 at y 1.64 ... 1.95; throat x 0.09 ... 0.59 at y 1.455 ... 1.64',
            'spread_m': 0.025, 'z_m': [0.01, 0.045],
            'land_x_m': [0.16, 0.52], 'bed_y_m': [1.118, 1.165], 'bed_z_m': [0.005, 0.145],
            'bore': {'centre_y_m': 1.2, 'centre_z_m': 0.071, 'r_m': 0.084,
                     'source': 'screw B pivot (0, 1.2, 0.071); bed = int_fill_screw_z01_feed layer y 1.116 ... 1.166 (about 30 % fill*)'},
            'melt_x_m': [1.521, 1.9], 'temp_fall_c': 30,
        },
    }
    mats = {}
    vis = [n for n in files['line']['names'] if an_line[n]['type'] == 'mesh' and n not in hide and n not in swap] + \
          [n for n in show_whole + show_clipped if n not in files['line']['names']]
    an_all = {**an_line, **files['interior']['nodes']}
    die_nodes = set(fl['die']['nodes'])
    for n in vis:
        m = an_all[n].get('materials', [])
        if 'za_fill_melt' in m:
            mats[n] = 'die' if n in die_nodes else 'line'
        elif 'ze_melt_curtain' in m:
            mats[n] = 'curtain'
        elif 'ze_sheet_pet' in m:
            mats[n] = 'sheet'
    flow['materials'] = mats
    return {'label_vi': '', 'plane': FLOW_PLANE, 'needs_interior': True,
            'hide': hide, 'swap': swap, 'clip': clip, 'show_whole': show_whole, 'show_clipped': show_clipped,
            'ghost': ghost, 'peel': None, 'camera': {**{k: FLOW_CAMERA[k] for k in ('pos', 'target', 'lens_mm')}, 'sensor_mm': 36,
                                                     'source': FLOW_CAMERA['source']},
            'cut_only_from': FLOW_CUT_ONLY_FROM,
            'cap_colors': FLOW_CAP_COLORS,
            'cap_colors_source': 'web choice (PLAN-FLOW review): neutral section colours in FLOW only, so the melt phase '
                                 'and heat colours read; the red steel / screw caps match the 270-300 °C end of the heat scale',
            'counts': counts,
            'flow': flow}


def check_flow(s, nodes, files):
    """PLAN-FLOW §2.5 checks that check_states does not cover. Raises DataError."""
    errs = []
    shown = set(s['show_whole']) | set(s['show_clipped']) | set(s['ghost'])
    lists = {k: s[k] for k in ('hide', 'clip', 'show_whole', 'show_clipped', 'ghost')}
    lists['swap keys'] = list(s['swap'])
    seen = {}
    for k, lst in lists.items():
        for n in lst:
            if n in seen:
                errs.append(f'FLOW: {n} in {seen[n]} and in {k}')
            seen.setdefault(n, k)
            if n not in nodes:
                errs.append(f'FLOW: {n} ({k}) is not in node_map')
    vis = {n for n in nodes if nodes[n]['file'] == 'line' and nodes[n]['kind'] == 'part' and n not in s['hide'] and n not in s['swap']} | \
          {n for n in shown if nodes[n]['kind'] != 'pivot'}
    a_on = [n for n in vis if n.startswith('int_screw_elem_a_')]
    b_on = [n for n in vis if n.startswith('int_screw_elem_b_')]
    if a_on and b_on:
        errs.append(f'FLOW: screw A {a_on[:3]} and screw B shown together')
    drain = [n for n in vis if 'valve_drain' in n]
    run = [n for n in vis if 'valve_run' in n]
    if drain and run:
        errs.append(f'FLOW: valve drain set {drain} and run set {run} shown together')
    zones = [z for z in s['flow']['zones'] if z['speed'] != 'roll_lip']
    an_all = {**files['line']['nodes'], **files['interior']['nodes']}
    for n in vis:
        if 'za_fill_melt' not in an_all[n].get('materials', []):
            continue
        kind = s['flow']['materials'].get(n)
        if kind == 'die':
            continue
        b = an_all[n]['bbox']
        cx = (b[0] + b[3]) / 2
        if kind != 'line' or not any(z['x_m'][0] - 1e-3 <= cx <= z['x_m'][1] + 1e-3 for z in zones):
            errs.append(f'FLOW: fill {n} (x centre {cx:.3f}) has no zone in flow.zones and is not the die')
    if errs:
        raise DataError('FLOW checks failed:\n  ' + '\n  '.join(errs))


def check_states(states, nodes):
    """PLAN-DOT1 §3.3.5 generation checks. Raises DataError on the first broken rule."""
    errs = []
    all_names = list(nodes)
    line_parts = [n for n in all_names if nodes[n]['file'] == 'line' and nodes[n]['kind'] == 'part']
    families = []
    for n in all_names:
        fam = [n] + [n + s for s in VARIANT_SUFFIXES if n + s in nodes]
        if len(fam) > 1:
            families.append(fam)
    swap_pairs = sorted({(k, v) for s in states.values() for k, vs in s['swap'].items() for v in vs})
    for sid, s in states.items():
        hide = set(s['hide'])
        swap_keys = set(s['swap'])
        if sid == 'FREE':
            roles_shown = [n for n in all_names if nodes[n]['file'] == 'interior' and nodes[n]['kind'] != 'pivot'
                           and nodes[n].get('role') in s['show_roles']]
            for n in all_names:
                r = nodes[n]
                if r['file'] == 'interior' and r['kind'] != 'pivot' and r.get('role') not in s['show_roles'] + s['hide_roles']:
                    errs.append(f'FREE: role {r.get("role")} of {n} is neither shown nor hidden')
            vis = {n for n in line_parts + roles_shown if n not in hide and n not in swap_keys}
        else:
            shown = set(s['show_whole']) | set(s['show_clipped']) | set(s['ghost'])
            errs += [f'{sid}: {n} in hide and in a show list' for n in sorted(shown & hide)]
            errs += [f'{sid}: {n} in clip and in hide' for n in sorted(set(s['clip']) & hide)]
            errs += [f'{sid}: {n} in clip and a swap key' for n in sorted(set(s['clip']) & swap_keys)]
            vis = {n for n in line_parts if n not in hide and n not in swap_keys} | {n for n in shown if nodes[n]['kind'] != 'pivot'}
        for k, vs in s['swap'].items():
            errs += [f'{sid}: swap value {v} (of {k}) is not shown' for v in vs if v not in vis]
        for n in sorted(vis):
            r = nodes[n]
            allowed = [sid] + s.get('cut_only_from', [])  # FLOW also shows the pre-cut sets of CUT_PUMP / CUT_DIE_AA
            if r['file'] == 'interior' and r.get('role') == 'cut_only' and not set(allowed) & set(r.get('states', [])):
                errs.append(f'{sid}: cut_only node {n} shown outside its states {r.get("states")}')
        for fam in families:
            on = [n for n in fam if n in vis]
            if len(on) > 1:
                errs.append(f'{sid}: exclusion rule, variants shown together: {on}')
        for k, v in swap_pairs:
            if k in vis and v in vis:
                errs.append(f'{sid}: exclusion rule, swap pair shown together: {k} + {v}')
    if errs:
        raise DataError('state checks failed:\n  ' + '\n  '.join(errs))


def intended_diff(k, p):
    """Reason when output file k may differ from its draft at path p (exact key or anything below it)."""
    why = INTENDED_DRAFT_DIFFS.get((k, p))
    if why:
        return why
    if k != 'cut_states':
        return None
    if p in ('states.FLOW', 'flow_version'):
        return 'PLAN-FLOW: new FLOW state (build_flow) and its data version'
    m = re.match(r'^states\.(\w+)\.(label_vi|tooltip_vi)$', p)
    if m and m.group(1) in LABEL_OVERRIDES:
        return 'PLAN-FLOW §4.1: button label / tooltip says what the viewer sees (LABEL_OVERRIDES)'
    for sid, ns in CLIP_TO_HIDE.items():
        for lst in ('hide', 'clip'):
            q = f'states.{sid}.{lst}'
            if p == q or p.startswith(q + '['):
                extra = len(EXTRA_HIDE.get(sid, []))
                return (f'review I1: {len(ns)} barrel cover node(s) moved from clip to hide (CLIP_TO_HIDE)'
                        + (f', {extra} more node(s) hidden (EXTRA_HIDE)' if extra and lst == 'hide' else ''))
    q = 'states.FREE.hide'
    if FREE_EXTRA_HIDE and (p == q or p.startswith(q + '[')):
        return f'review M2: {len(FREE_EXTRA_HIDE)} barrel cover node(s) hidden in FREE (FREE_EXTRA_HIDE)'
    for sid in CAMERA_OVERRIDES:
        q = f'states.{sid}.camera'
        if p == q or p.startswith(q + '.'):
            return 'review I2/M1: camera preset override (CAMERA_OVERRIDES)'
    return None


def deep_diff(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            p = f'{path}.{k}' if path else k
            if k not in a:
                out.append((p, 'only in draft'))
            elif k not in b:
                out.append((p, 'only in output'))
            else:
                out += deep_diff(a[k], b[k], p)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [(path, f'list length {len(a)} vs draft {len(b)}')]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += deep_diff(x, y, f'{path}[{i}]')
        return out
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        return [(path, f'type {type(a).__name__} vs draft {type(b).__name__}')]
    return [] if a == b else [(path, f'{json.dumps(a, ensure_ascii=False)[:120]} vs draft {json.dumps(b, ensure_ascii=False)[:120]}')]


def main():
    a = parse_args()
    with open(a.analysis, encoding='utf-8') as f:
        analysis = json.load(f)
    if not analysis.get('ok'):
        raise SystemExit('glb_analysis.json is not ok; run `make analyze` first')
    try:
        out = build(analysis)
    except DataError as e:
        print(f'make_data FAILED: {e}', file=sys.stderr)
        sys.exit(1)
    os.makedirs(a.out, exist_ok=True)
    indent = {'cut_states': 1, 'rotors': 1, 'node_map': 0, 'devices': 0, 'materials': 0}
    for k, v in out.items():
        with open(os.path.join(a.out, f'{k}.json'), 'w', encoding='utf-8') as f:
            json.dump(v, f, ensure_ascii=False, indent=indent[k])
    st = out['cut_states']['states']
    print('make_data: devices', len(out['devices']['devices']), '| nodes', len(out['node_map']['nodes']),
          '| rotors', len(out['rotors']['rotors']), '| materials', len(out['materials']['materials']),
          '| states', {k: (len(v['hide']), len(v['swap']), len(v['clip']) if isinstance(v['clip'], list) else 'all') for k, v in st.items()},
          '->', os.path.relpath(a.out, WEB))
    if a.compare:
        cdir = os.path.join(WEB, a.compare)
        unexpected = 0
        for k, v in out.items():
            with open(os.path.join(cdir, f'{k}.dot1.json'), encoding='utf-8') as f:
                draft = json.load(f)
            for p, msg in deep_diff(v, draft):
                why = intended_diff(k, p)
                if why:
                    print(f'  intended  {k}: {p}: {why}')
                else:
                    unexpected += 1
                    print(f'  DIFF      {k}: {p}: {msg}')
        print(f'compare with {a.compare}/*.dot1.json: {unexpected} unexpected difference(s)')
        if unexpected:
            sys.exit(1)


if __name__ == '__main__':
    main()
