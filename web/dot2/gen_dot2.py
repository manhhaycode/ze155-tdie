#!/usr/bin/env python3
"""gen_dot2.py - planner's draft of the Đợt 2 data (PLAN-DOT2 §2). Python 3, standard library only.

    python3 web/dot2/gen_dot2.py      -> web/dot2/states.dot2.json + a name-resolution report on stdout

Reads (never writes) web/model-contract.json, web/build/data/{node_map,devices}.json,
web/build/reports/glb_analysis.json, anim/shots.json. Exit 1 on any unresolved name or broken state rule.
The data builder ports this into web/tools/make_data.py (new outputs clips.json, fills.json, node_map.splits,
6 more states in cut_states.json); the output of make_data must equal this draft except for the documented diffs.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
WS = os.path.dirname(WEB)


def load(p):
    with open(os.path.join(WS, p), encoding='utf-8') as f:
        return json.load(f)


con = load('web/model-contract.json')
nm = load('web/build/data/node_map.json')['nodes']
devs = {d['device_id']: d for d in load('web/build/data/devices.json')['devices']}
an = load('web/build/reports/glb_analysis.json')['files']
shots = load('anim/shots.json')
errs, notes = [], []

# ---------------------------------------------------------------- name rules (Đợt 1 rules + Đợt 2 additions)
RENAME = {'rot_screw_a': 'int_screw_axis_a', 'rot_screw_b': 'int_screw_axis_b'}
# Runtime-only names in contract show lists. Option C has no exported empty for them; the real node is listed
# next to them in the same list, and the runtime pivot / mover is created from rotors.json / clips.json.
DROP = {'rot_gbx_input': 'int_gbx_schematic_input', 'rot_gbx_counter': 'int_gbx_schematic_counter',
        'rot_pump_gear_top': 'int_pump_gear_top', 'rot_pump_gear_bottom': 'int_pump_gear_bottom',
        'anim_sc_disc': 'int_sc_disc', 'anim_sc_piston': 'int_sc_backflush_piston',
        'anim_die_choker_bar': 'int_die_choker_bar'}
SPLITS = {}
for src, rec in con['split_objects'].items():
    if src not in nm:
        errs.append(f'split source {src} is not an exported node')
    SPLITS[src] = rec
VIRTUAL = {f'{src}__{p}': src for src, rec in SPLITS.items() for p in rec['parts']}


def expand(n):
    m = re.match(r'^(.*_)(\d+)\.\.(\d+)$', n)
    if not m:
        return [n]
    w = len(m.group(2))
    return [f'{m.group(1)}{i:0{w}d}' for i in range(int(m.group(2)), int(m.group(3)) + 1)]


def conv(n):
    return RENAME.get(n, n[2:] if n.startswith('p_') else n)


def resolve(lst, ctx, allow_drop=True):
    out = []
    for n in lst:
        for e in expand(n):
            c = conv(e)
            if c in DROP and allow_drop:
                if not any(conv(x).startswith(DROP[c]) for x in lst):  # the node or its _full child
                    errs.append(f'{ctx}: {c} dropped but neither {DROP[c]} nor its _full child is in the same list')
                notes.append(f'{ctx}: dropped runtime name {c} (real node {DROP[c]} listed)')
                continue
            if c not in nm and c not in VIRTUAL:
                errs.append(f'unresolved {e} -> {c} ({ctx})')
                continue
            if c not in out:
                out.append(c)
    return out


# ---------------------------------------------------------------- cameras (Blender (x, y, z) -> three (x, z, -y))
def b2t(p):
    return [round(p[0], 4) + 0.0, round(p[2], 4) + 0.0, round(-p[1], 4) + 0.0]


SH = {s['id']: s for s in shots['shots']}
ST = {s['id']: s for s in shots['stills']}


def cam_shot(sid, cam_i, key_i, why):
    k = SH[sid]['cameras'][cam_i]['keys'][key_i]
    return {'pos': b2t(k['loc']), 'target': b2t(k['target']), 'lens_mm': k['lens_mm'], 'sensor_mm': 36,
            'source': f'shots.json {sid} key {key_i + 1} (frame {k.get("frame")}); {why}'}


def cam_still(sid, why):
    c = ST[sid]['camera']
    return {'pos': b2t(c['loc']), 'target': b2t(c['target']), 'lens_mm': c['lens_mm'], 'sensor_mm': 36,
            'source': f'shots.json still {sid}; {why}'}


def box_from_dev(d):
    b = devs[d]['bbox_m']
    return {'min': b[:3], 'max': b[3:], 'source': f'devices.json {d}.bbox_m'}


CAMS = {
    'GHOST_DRIVE': cam_shot('S02', 0, 0, 'wider key: gearbox + lantern + couplings; key 2 cuts the gearbox'),
    'GHOST_SC': cam_still('ST6', 'disc, screens, channels and piston under the raised ghost hood'),
    'CUT_PUMP': cam_shot('S10', 0, 0, '45 mm at 1.78 m; ST7 / S10 key 2 (55 mm at 1.2 m) is as tight as the rejected X2450 preset'),
    'CUT_DIE_PLAN': cam_shot('S11', 0, 1, 'oblique from upstream so the lifted upper half (+0.9 m) does not cover the lower face'),
    'CUT_DIE_AA': cam_shot('S12', 0, 0, 'whole A-A section with rolls; keys 2-3 are close-ups of the lip'),
    'ST1_Z_FULL': cam_still('ST1', 'whole line half-section from above'),
}
FRAME = {
    'GHOST_DRIVE': box_from_dev('gearbox'),
    'GHOST_SC': box_from_dev('melt_screen_changer'),
}
SHORT = {'GHOST_DRIVE': 'Hộp số (vỏ trong suốt)', 'GHOST_SC': 'Bộ lọc (vỏ trong suốt)', 'CUT_PUMP': 'Bơm cắt Y = 0',
         'CUT_DIE_PLAN': 'Mặt phân khuôn Z = 1 200', 'CUT_DIE_AA': 'Khuôn A-A Y = 0', 'ST1_Z_FULL': 'Toàn tuyến Z = 1 200'}
GROUP = {'GHOST_DRIVE': 'drive', 'GHOST_SC': 'melt', 'CUT_PUMP': 'melt', 'CUT_DIE_PLAN': 'die', 'CUT_DIE_AA': 'die',
         'ST1_Z_FULL': 'line'}

# Planner fixes on top of the contract (each one is written in PLAN-DOT2 §2.1)
COVERS = [f'barrel_cover_c{i}{s}' for i in range(1, 7) for s in ('', '_hw')]
FIX = {
    'ST1_Z_FULL': {'clip_to_hide': COVERS, 'why': 'review-dot1-impl-01 I1: solid cover boxes (volume / bbox 0.88-0.97) draw full-section slabs; hide them as in the Đợt 1 fix'},
    'CUT_DIE_AA': {'add_clip': ['ctx_sheet', 'ctx_melt_curtain'], 'why': 'the translucent sheet and curtain span z -1.1...1.1 and would tint the A-A section; cap_color null -> clipped without a cap'},
}

D2 = ['GHOST_DRIVE', 'GHOST_SC', 'CUT_PUMP', 'CUT_DIE_PLAN', 'CUT_DIE_AA', 'ST1_Z_FULL']
states = {}
for sid in D2:
    s = con['cut_states'][sid]
    p = s.get('plane')
    st = {'label_vi': s['label_vi'], 'label_short_vi': SHORT[sid], 'group': GROUP[sid],
          'plane': ({'normal': p['normal'], 'constant': p['constant']} if p else None), 'needs_interior': True,
          'hide': resolve(s.get('hide', []), f'{sid}.hide'),
          'swap': {conv(k): resolve(v, f'{sid}.swap[{k}]') for k, v in (s.get('swap') or {}).items()},
          'clip': resolve(s.get('clip', []), f'{sid}.clip'),
          'show_whole': resolve(s.get('show_whole', []), f'{sid}.show_whole'),
          'show_clipped': resolve(s.get('show_clipped', []), f'{sid}.show_clipped'),
          'ghost': resolve(s.get('ghost', []), f'{sid}.ghost'),
          'peel': s.get('peel') and {k: s['peel'][k] for k in ('offset_m', 'duration_s')},
          'clips_on_enter': s.get('clips_on_enter', []),
          'camera': CAMS[sid],
          'frame_box_m': FRAME.get(sid) or {'min': s['box_m']['min'], 'max': s['box_m']['max'], 'source': 'contract box_m'}}
    for k in st['swap']:
        if k not in nm and k not in VIRTUAL:
            errs.append(f'{sid}: unresolved swap key {k}')
    fx = FIX.get(sid)
    if fx:
        for n in fx.get('clip_to_hide', []):
            if n in st['clip']:
                st['clip'].remove(n)
                st['hide'].append(n)
            else:
                errs.append(f'{sid}: fix expects {n} in clip')
        for n in fx.get('add_clip', []):
            if n not in nm:
                errs.append(f'{sid}: fix adds unknown {n}')
            elif n not in st['clip']:
                st['clip'].append(n)
        st['planner_fix'] = fx['why']
    states[sid] = st
states['CUT_DIE_AA']['morphs'] = {
    'keys': ['gap_x10', 'lip_push'],
    'nodes': ['int_die_section_upper', 'int_die_thermal_bolts_y0', 'int_die_thermal_bolt_y0', 'int_fill_die_y0'],
    'rule': 'all meshes of the 4 nodes together; lip_push only with gap_x10 = 1 (alone it would close the 1.0 mm gap past zero)',
    'readout': {'true_gap_mm': '1.00 - 0.15 * lip_push', 'drawn_gap_mm': '1.00 + 8.975 * gap_x10 - 1.5 * lip_push',
                'source': 'anim/log.md A1b: lip gap 1.000 mm, 9.975 mm with gap_x10 = 1, lip_push tip down 1.5 mm drawn; design-anim §2 thermal bolt stroke 0.3 mm = ±0.15 mm'},
    'tween_s': 0.6}

# ---------------------------------------------------------------- clips (runtime tweens, no glTF animation)
C = {c['name']: c for c in con['clips']}
v = C['valve_run']
fs = v['fill_switch']
drain = resolve(fs['drain_set'], 'valve_run.drain_set')
run = resolve(fs['run_set'], 'valve_run.run_set')
for n in drain + run:
    if n + '_lo' not in nm:
        errs.append(f'valve_run: {n}_lo missing')
rest = v['tracks'][0]['to_m']
frm = v['tracks'][0]['from_m']
sc = C['sc_index']
disc_t, pist_t = sc['tracks']
die = C['die_open']
die_devs, die_nodes = [], []
for t in die['targets']:
    t0 = t.split(' ')[0]
    if t0.startswith('dev_'):
        d = t0[4:]
        (die_devs if d in devs else errs).append(d if d in devs else f'die_open: unknown device {d}')
    elif t0 == 'anim_die_bolts_top':
        die_nodes.append('die_body_bolts__top')
    elif t0 == 'anim_die_heater_boxes_top':
        die_nodes.append('die_heater_boxes__top')
    elif t0 == 'anim_die_choker_bar':
        if nm['int_die_choker_bar']['device_id'] not in die_devs + ['die_choker_bolts']:
            errs.append('die_open: int_die_choker_bar is not owned by a lifted device')
        notes.append('die_open: anim_die_choker_bar dropped, int_die_choker_bar rides with dev_die_choker_bolts')
    else:
        errs.append(f'die_open: unknown target {t}')
for n in die_nodes:
    if n not in VIRTUAL:
        errs.append(f'die_open: {n} is not a split part')


def node_pos(n):
    d = an['interior']['nodes'].get(n) or an['line']['nodes'].get(n)
    return d['pos']


clips = {
    'valve_run': {'label_vi': 'Van khởi động: XẢ → CHẠY', 'states': ['CUT_Z_BARREL', 'ST1_Z_FULL', 'FREE'],
                  'camera_on_play': {**cam_shot('S08', 0, 2, 'valve close-up; only from CUT_Z_BARREL'), 'only_from': ['CUT_Z_BARREL']},
                  'movers': [{'id': 'valve_bolt', 'attach': ['int_valve_bolt'], 'device_id': 'melt_startup_valve',
                              'pivot_m': [0, 0, 0], 'kind': 'translate'}],
                  'tracks': [{'mover': 'valve_bolt', 'offset_from_m': [round(frm[i] - rest[i], 4) + 0.0 for i in range(3)],
                              'offset_to_m': [0.0, 0.0, 0.0], 't0_s': 1.0, 't1_s': 2.2, 'ease': 'inOutCubic'}],
                  'duration_s': 2.2, 'loop': False, 'rest': 'offset 0 = RUN (the bolt is exported at RUN)',
                  'fill_switch': {'drain_set': drain, 'run_set': run, 'drain_until_s': 2.2,
                                  'variant_rule': 'toggle the variant that the current state shows: _lo in CUT_Z_BARREL and ST1_Z_FULL, the full name in FREE',
                                  'rule': 'drain set while t < drain_until_s, run set at the end and at rest; never both; through setVisible (recorded)'},
                  'source': 'contract clips.valve_run (from [6.221, 1.2, 0.2] to [6.221, 1.2, 0] in 1.2 s) + 1.0 s hold at DRAIN so the elbow can be seen'},
    'sc_index': {'label_vi': 'Đĩa lọc quay từng bước', 'states': ['GHOST_SC'],
                 'movers': [{'id': 'sc_disc', 'attach': ['int_sc_disc'], 'device_id': 'melt_screen_changer',
                             'pivot_m': node_pos('int_sc_disc'), 'axis': disc_t['axis'], 'kind': 'rotate'},
                            {'id': 'sc_piston', 'attach': ['int_sc_backflush_piston'], 'device_id': 'melt_screen_changer',
                             'pivot_m': [0, 0, 0], 'kind': 'translate'}],
                 'tracks': [{'mover': 'sc_disc', 'step_deg': disc_t['step_deg'], 'steps': disc_t['steps'],
                             'step_time_s': disc_t['step_time_s'], 'period_s': disc_t['period_s'], 'ease': 'inOutCubic',
                             'step_at_s': 0.0},
                            {'mover': 'sc_piston', 'offset_to_m': [round(pist_t['stroke_to_m'][i] - pist_t['rest_m'][i], 4) + 0.0 for i in range(3)],
                             'out_s': pist_t['out_s'], 'back_s': pist_t['back_s'], 'per_period': True}],
                 'duration_s': sc['duration_s'], 'loop': True,
                 'dirt': {'nodes': [f'int_sc_screens_{i:02d}' for i in range(1, 13)], 'material': 'za_sc_screenpack',
                          'cavity_angle_deg_from': 'node extras cavity_angle_deg (01 = 0 ... 12 = -30)',
                          'flow_window_deg': [-150, -30], 'backflush_deg': 0,
                          'rule': 'angle = cavity_angle_deg + 30 * completed steps (wrapped to -180...180). In the flow window: dirt ramps from i/5 to (i+1)/5 over the dwell (i = (angle + 150) / 30). At 0 deg: dirt goes to 0 during the piston stroke (out_s). Elsewhere: unchanged (dirty from -30 to 0, clean after the backflush).',
                          'colors': {'clean': '#A8B0B8', 'dirty': '#4A3320'}},
                 'source': 'contract clips.sc_index; anim/log.md A1b (cavities at 0...330 deg, flow window -150...-30, backflush at 0)'},
    'die_open': {'label_vi': 'Nhấc nửa khuôn trên', 'states': ['CUT_DIE_PLAN'],
                 'device_groups': die_devs,
                 'movers': [{'id': f'lift_{n}', 'attach': [n], 'device_id': VIRTUAL[n], 'pivot_m': [0, 0, 0], 'kind': 'translate'}
                            for n in die_nodes],
                 'tracks': [{'targets': 'device_groups + movers', 'offset_from_m': [0.0, 0.0, 0.0], 'offset_to_m': die['offset_m'],
                             't0_s': 0.0, 't1_s': die['duration_s'], 'ease': 'inOutCubic'},
                            {'fill_front': 'die', 'from': 0.0, 'to': 1.0, 't0_s': die['duration_s'], 't1_s': die['duration_s'] + 2.0}],
                 'duration_s': die['duration_s'] + 2.0, 'loop': False,
                 'rule': 'device groups are runtime groups at identity: tween group.position directly. Targets are never hidden or clipped in CUT_DIE_PLAN.',
                 'source': 'contract clips.die_open (+0.9 m in 2.4 s) + fills die front 0 -> 1 (contract fills int_fill_die note)'},
}

# ---------------------------------------------------------------- fills (one world-X profile + the radial die)
F = con['fills']
zones = []
for z in F:
    n = conv(z['node'])
    if n not in nm:
        errs.append(f'fills: unresolved {z["node"]}')
    if z['flow_mode'] != 'x':
        continue
    speed = 'screw' if z.get('pitch_m') else 'melt'
    zones.append({'zone': z['zone'], 'x_m': z['x_range_m'], 'temp_c': z['temp_c'], 'pitch_m': z.get('pitch_m') or 0.12,
                  'speed': speed, 'phase': z['phase']})
zones.append({'zone': 'curtain', 'x_m': [9.576, 9.776], 'temp_c': [270, 250], 'pitch_m': 0.05, 'speed': 'roll_lip',
              'phase': 'melt', 'note': 'ctx_melt_curtain; temperatures assumed (*), lip exit 20.8 m/min (design-anim §2)'})
zones.sort(key=lambda z: z['x_m'][0])
die_zone = next(z for z in F if z['flow_mode'] == 'radial')
fill_nodes = {}
fill_meshes = [n for f in ('line', 'interior') for n, d in an[f]['nodes'].items() if 'za_fill_melt' in d.get('materials', [])]
for n in fill_meshes:
    fill_nodes[n] = 'die' if n.startswith('int_fill_die') else 'line'
fill_nodes['ctx_melt_curtain'] = 'line'
fills = {'phase_ramp_x_m': [1.52, 1.90], 'colors': {'pellet': '#DBD6C2', 'melt': '#D95709'}, 'opacity': 0.6,
         'temp_legend_c': [50, 300],
         'speeds': {'screw': 'pitch_m * rpm_screw / 60 / slow_screw (rotor mode: off 0, slow 1/20, real 1)',
                    'melt': 'stripe 0.12 m at the speed of zone z09 (0.1268 m pitch): illustrative, proportional to throughput',
                    'roll_lip': '0.347 m/s real (20.8 m/min) * roll factor (rolls display_slow 1)'},
         'zones': zones,
         'die': {'nodes': [n for n in fill_nodes if fill_nodes[n] == 'die'], 'origin_m': die_zone['origin_m'],
                 'radius_m': die_zone['radius_m'], 'temp_c': die_zone['temp_c'], 'front_default': 1.0},
         'nodes': fill_nodes,
         'sheet': {'node': 'ctx_sheet', 'material': 'ze_sheet_pet', 'speed_m_s_real': round(2 * 3.141592653589793 * 0.4 * 9.95 / 60, 4),
                   'stripe_m': 0.30, 'stripe_width': 0.12,
                   'path_three_xy': [
                       {'seg': 'wrap', 'centre': [9.776, 1.601], 'r': 0.4005, 'from_deg': -90, 'to_deg': 90, 'sense': 'ccw',
                        'note': 'middle roll, nip at the bottom, sheet over the +X side (middle rpm -9.95: bottom surface moves +X)'},
                       {'seg': 'wrap', 'centre': [9.776, 2.403], 'r': 0.4005, 'from_deg': -90, 'to_deg': 90, 'sense': 'cw_via_180',
                        'note': 'top roll, sheet over the -X side (bbox min x 9.37)'},
                       {'seg': 'line', 'from': [9.776, 2.805], 'to': [12.5, 2.805], 'note': 'take-off run'}],
                   'select_rule': 'y > 2.79 and x > 9.776 -> line; else y < 2.002 -> middle wrap; else top wrap',
                   'source': 'design-anim §2 (rolls 9.9 rpm, sheet about 25 m/min); ctx_sheet has POSITION + NORMAL only (no UV), so the pattern is procedural'}}
for n, kind in fill_nodes.items():
    if n not in nm:
        errs.append(f'fills: node {n} not exported')

# ---------------------------------------------------------------- splits (runtime island split of 3 line nodes)
splits = {}
for src, rec in SPLITS.items():
    a = an['line']['nodes'][src]
    if 'X' in rec['by']:
        rule = {'by': 'x_nearest', 'centres_x_m': {f'{src}__{p}': q['x'] for p, q in rec['parts'].items()}}
    else:
        rule = {'by': 'y_threshold', 'y_m': 1.2, 'above': f'{src}__top', 'below': f'{src}__bottom',
                'note': 'contract: Blender Z of the island bbox centre > 1.2 -> top; three Y = Blender Z'}
    splits[src] = {**rule, 'device_id': nm[src]['device_id'], 'source_tris': a['tris'], 'source_meshes': a['meshes'],
                   'materials': a['materials'], 'island': 'connected triangles over position-welded vertices (1e-5 m), classified by island bbox centre',
                   'ambiguity_check': 'x_nearest: fail if the two nearest centres are closer than 10 mm to each other for any island'}

# ---------------------------------------------------------------- rotors to drive in Đợt 2
rotors_dot2 = {'enable_slice': [1, 2], 'new': ['pump_gear_top', 'pump_gear_bottom', 'gbx_input', 'gbx_counter'],
               'expected_deg_s_slow': {'pump_gear_top': 103.5, 'pump_gear_bottom': -103.5, 'gbx_input': -335.4, 'gbx_counter': 171.42},
               'note': 'int_gbx_schematic_out_a/b are children of int_screw_axis_a/b in interior.glb and turn with the screws'}

# ---------------------------------------------------------------- state checks (PLAN-DOT1 §3.3.5 rules, with split parts)
line_parts = [n for n, r in nm.items() if r['file'] == 'line' and r['kind'] == 'part' and n not in SPLITS] + list(VIRTUAL)
fam = []
for n in nm:
    f = [n] + [n + s for s in ('_lo', '_y0', '_x2450', '_x4120') if n + s in nm]
    if len(f) > 1:
        fam.append(f)
swap_pairs = {(k, x) for s in states.values() for k, xs in s['swap'].items() for x in xs}
for sid, s in states.items():
    hide, keys = set(s['hide']), set(s['swap'])
    shown = set(s['show_whole']) | set(s['show_clipped']) | set(s['ghost'])
    errs += [f'{sid}: {n} hidden and shown' for n in sorted(shown & hide)]
    errs += [f'{sid}: {n} clipped and hidden' for n in sorted(set(s['clip']) & hide)]
    errs += [f'{sid}: {n} clipped and a swap key' for n in sorted(set(s['clip']) & keys)]
    vis = {n for n in line_parts if n not in hide and n not in keys} | {n for n in shown if nm.get(n, {}).get('kind') != 'pivot'}
    for k, xs in s['swap'].items():
        errs += [f'{sid}: swap value {x} not shown' for x in xs if x not in vis]
    for n in sorted(vis):
        r = nm.get(n)
        if r and r['file'] == 'interior' and r.get('role') == 'cut_only' and sid not in r.get('states', []):
            errs.append(f'{sid}: cut_only {n} shown outside {r.get("states")}')
    for f in fam:
        on = [n for n in f if n in vis]
        if len(on) > 1:
            errs.append(f'{sid}: variants shown together {on}')
    for k, x in swap_pairs:
        if k in vis and x in vis:
            errs.append(f'{sid}: swap pair shown together {k} + {x}')
    if sid == 'CUT_DIE_PLAN':
        lifted = {n for d in die_devs for n in devs[d]['nodes']} | set(die_nodes)
        bad = lifted & (hide | set(s['clip']) | set(s['show_clipped']))
        errs += [f'CUT_DIE_PLAN: die_open target {n} is hidden or clipped' for n in sorted(bad)]
    s['counts'] = {k: len(s[k]) for k in ('hide', 'swap', 'clip', 'show_whole', 'show_clipped', 'ghost')}
    s['visible_parts_estimate'] = len(vis)

out = {'version': 2, 'draft_of': 'PLAN-DOT2.md §2 (planner draft; make_data.py is the real generator)',
       'name_rules': {'from_dot1': 'p_<x> -> <x>; rot_screw_a|b -> int_screw_axis_a|b; NN..MM expanded',
                      'drop_runtime_names': DROP, 'virtual_split_parts': VIRTUAL},
       'states': states, 'clips': clips, 'fills': fills, 'splits': splits, 'rotors': rotors_dot2,
       'notes': sorted(set(notes))}
with open(os.path.join(HERE, 'states.dot2.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('states:', {k: v['counts'] for k, v in states.items()})
print('visible parts:', {k: v['visible_parts_estimate'] for k, v in states.items()})
print('clips: valve drain', drain, 'run', run, '| die devices', len(die_devs), 'die nodes', die_nodes)
print('fills: zones', len(zones), 'nodes', len(fill_nodes), '| splits', {k: len(v.get('centres_x_m', {})) or 2 for k, v in splits.items()})
print('notes:', len(set(notes)))
if errs:
    print('ERRORS:\n  ' + '\n  '.join(errs))
    sys.exit(1)
print('OK: every name resolved; state rules hold')
