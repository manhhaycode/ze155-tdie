# Prototype generator for the Đợt 1 data drafts (planner). Builders re-implement it as web/tools/make_data.mjs.
import json, re, collections as C
W = '/Users/manhhaycode/m3d-e2e/ze155-tdie/web/'
con = json.load(open(W + 'model-contract.json'))
lc = json.load(open(W + 'build/probe/load_check.json'))
cl = json.load(open(W + 'build/probe/closed_check.json'))
shots = json.load(open(W + '../anim/shots.json'))
L = lc['line']['names']; I = lc['interior']['names']; ALL = set(L) | set(I)
RENAME = {'rot_screw_a': 'int_screw_axis_a', 'rot_screw_b': 'int_screw_axis_b'}
def expand(n):
    m = re.match(r'^(.*_)(\d+)\.\.(\d+)$', n)
    if not m: return [n]
    w = len(m.group(2)); return [f'{m.group(1)}{i:0{w}d}' for i in range(int(m.group(2)), int(m.group(3)) + 1)]
def conv(n): return RENAME.get(n, n[2:] if n.startswith('p_') else n)
def names(lst):
    out = []
    for n in lst:
        for e in expand(n):
            c = conv(e)
            if c not in ALL: raise SystemExit(f'unresolved {e}')
            if c not in out: out.append(c)
    return out
def b2t(p): return [round(p[0], 4) + 0.0, round(p[2], 4) + 0.0, round(-p[1], 4) + 0.0]
def cam(c): return {'pos': b2t(c['loc']), 'target': b2t(c['target']), 'lens_mm': c['lens_mm'], 'sensor_mm': 36}
SH = {s['id']: s for s in shots['shots']}; ST = {s['id']: s for s in shots['stills']}
CAMS = {
  'FULL': dict(cam(SH['S01']['cameras'][0]['keys'][1]), source='shots.json S01 key 2 (frame 151)'),
  'CUT_FEED': dict(cam(SH['S03']['cameras'][1]['keys'][1]), source='shots.json S03b key 2 (frame 900)'),
  'CUT_Z_BARREL': dict(cam(SH['S04']['cameras'][0]['keys'][2]), source='shots.json S04 key 3 (frame 1161) = look A1a-S04-f1161'),
  'CUT_X2450': dict(cam(ST['ST2']['camera']), source='shots.json still ST2 (= S05 key 2)'),
  'CUT_X4120': dict(cam(ST['ST3']['camera']), source='shots.json still ST3 (= S07 key 2)'),
  'FREE': None,
}
states = {}
for sid in ['FULL', 'CUT_FEED', 'CUT_Z_BARREL', 'CUT_X2450', 'CUT_X4120']:
    s = con['cut_states'][sid]
    p = s.get('plane')
    out = {'label_vi': s['label_vi'], 'plane': ({'normal': p['normal'], 'constant': p['constant']} if p else None),
           'needs_interior': sid != 'FULL',
           'hide': names(s.get('hide', [])), 'swap': {conv(k): names(v) for k, v in (s.get('swap') or {}).items()},
           'clip': names(s.get('clip', [])), 'show_whole': names(s.get('show_whole', [])),
           'show_clipped': names(s.get('show_clipped', [])), 'ghost': names(s.get('ghost', [])),
           'peel': s.get('peel') and {k: s['peel'][k] for k in ('offset_m', 'duration_s')},
           'camera': CAMS[sid]}
    if sid == 'FULL': out['note'] = 'load state: interior hidden; every recorded change undone (resetCuts)'
    states[sid] = out
F = con['cut_states']['FREE']
states['FREE'] = {'label_vi': F['label_vi'], 'plane': None, 'needs_interior': True,
    'axis_default': 'x', 'offset_default_m': {'x': 3.0, 'y': 1.2, 'z': 0.0}, 'slider_range_m': {'x': [-5.72, 12.5], 'y': [0.0, 6.3], 'z': [-2.8, 4.9]}, 'slider_range_source': 'model-contract coordinates.line_extent_m',
    'hide': names(F['hide']), 'swap': {conv(k): names(v) for k, v in con['free_swap'].items()},
    'show_roles': ['full'], 'hide_roles': ['cut_only', 'ghost', 'marker'],
    'clip': 'all visible parts (renderer.clippingPlanes, global plane)', 'caps': 'parts with closed=true or cap=force',
    'camera': None,
    'note': 'Đợt 1 exports all interior items, so every FREE swap value resolves (no missing_target exception).'}
# checks: no overlap hide/show, swap values shown
for sid, s in states.items():
    shown = set(s.get('show_whole', []) if isinstance(s.get('show_whole'), list) else []) | set(s.get('show_clipped', []) if isinstance(s.get('show_clipped'), list) else [])
    hid = set(s['hide'])
    assert not (shown & hid), (sid, shown & hid)
    if sid != 'FREE':
        for k, vs in s['swap'].items():
            for v in vs: assert v in shown, (sid, k, v)
        assert not (set(s['clip']) & hid), sid
json.dump({'version': 1, 'slice': 1,
           'generated_from': 'model-contract.json cut_states + free_swap, names resolved against the probe export (web/build/probe/load_check.json); cameras from anim/shots.json converted to three (x, z, -y)',
           'name_rule': 'contract p_<name> -> <name> (exported Blender object name); rot_screw_a|b -> int_screw_axis_a|b; NN..MM ranges expanded',
           'plane_rule': 'three.js keeps points with normal . p + constant >= 0',
           'states': states}, open(W + 'dot1/cut_states.dot1.json', 'w'), ensure_ascii=False, indent=1)

# node map
o2d = con['object_to_device']
items = con['interior_export']['items']
info = {}
for it in items:
    s = it['src']
    if s.startswith('('): continue
    origin = '(origin)' in s
    s = s.split(' ')[0]
    for e in expand(s):
        d = info.setdefault(e, {'device_id': it['host'], 'slice': it['slice']})
        if origin: d['moves_as'] = it['role']
        else:
            d['role'] = it['role']; d['states'] = it.get('states', [])
        d['slice'] = min(d['slice'], it['slice'])
for e in ('int_screw_axis_a', 'int_screw_axis_b'):
    info[e].update(role='pivot', states=[])
roll_dev = {'anim_roll_axis_bottom': 'ctx_roll_bottom', 'anim_roll_axis_middle': 'ctx_roll_middle', 'anim_roll_axis_top': 'ctx_roll_top'}
FORCE_CAP = {'ctx_roll_bottom', 'ctx_roll_middle', 'ctx_roll_top'}
nodes = {}
for n in L:
    if n in roll_dev:
        nodes[n] = {'file': 'line', 'device_id': roll_dev[n], 'kind': 'pivot'}
        continue
    r = cl['line'][n]
    nodes[n] = {'file': 'line', 'device_id': o2d[n], 'kind': 'part', 'closed': r['closed']}
    if n in FORCE_CAP: nodes[n]['cap'] = 'force'
for n in I:
    d = info[n]
    rec = {'file': 'interior', 'device_id': d['device_id'], 'kind': 'pivot' if d.get('role') == 'pivot' else 'interior',
           'role': d.get('role'), 'slice': d['slice']}
    if d.get('states'): rec['states'] = d['states']
    if d.get('moves_as'): rec['moves_in_dot2'] = d['moves_as']
    if n in cl['interior']: rec['closed'] = cl['interior'][n]['closed']
    nodes[n] = rec
devs = {d['device_id']: {'group': d['group'], 'file': d['file'], 'synthetic': d['synthetic']} for d in con['devices']}
for n, r in nodes.items():
    assert r['device_id'] in devs, (n, r)
cnt = C.Counter(r['device_id'] for r in nodes.values())
print('devices with nodes', len(cnt), 'devices total', len(devs), 'missing', [d for d in devs if d not in cnt])
json.dump({'version': 1, 'slice': 1,
           'doc': 'exported node name (= Blender object name = three userData.name) -> runtime metadata. kind part = exterior mesh node; interior = interior mesh node; pivot = exported empty used only as a rotation parent. closed = position-welded closed test on the RAW GLB (no boundary edge, consistent winding, signed volume > 0). Runtime keeps these under userData.ze.',
           'counts': {'line': len(L), 'interior': len(I), 'devices': len(devs)},
           'nodes': nodes}, open(W + 'dot1/node_map.dot1.json', 'w'), ensure_ascii=False, indent=0)

# rotors
R = {r['node']: r for r in con['rotors']}
def rot(rid, node, attach, slice_):
    r = R[node]
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
for r in rotors:
    for a in r['attach']: assert a in ALL, a
json.dump({'version': 1, 'doc': 'Runtime rotors. For each: create Object3D named pivot at pivot_m (three world, metres, identity rotation) inside dev_<device_id>, attach() the listed exported nodes (subtrees keep world pose), then useFrame: pivot.rotateOnAxis(axis, 2*PI*rpm/60/slow*dt). Never rotate an exported mesh node directly (quantize rewrites mesh-node TRS). Slice 2 entries are loaded but not driven in Đợt 1.',
           'modes': {'off': 0, 'slow': 'rpm / display_slow', 'real': 'rpm'}, 'default_mode': 'slow',
           'rotors': rotors}, open(W + 'dot1/rotors.dot1.json', 'w'), ensure_ascii=False, indent=1)
print('ok', {k: (len(v['hide']), len(v['swap']), len(v['clip']) if isinstance(v['clip'], list) else 'all') for k, v in states.items()})

# devices + materials (added: stand-in data for stream B)
SEC_VI = {'base': 'Khung đế', 'drive': 'Truyền động', 'feed': 'Cấp liệu', 'barrel': 'Xi lanh và trục vít',
          'vacuum': 'Hút chân không', 'melt': 'Đường nhựa nóng chảy', 'die': 'Khuôn phẳng', 'control': 'Điều khiển và cáp',
          'util': 'Khí nén và nước làm mát', 'context': 'Cán, tấm và đo (ngữ cảnh)'}
pj = {p['id']: p for p in json.load(open(W + '../design/parts.json'))['parts']}
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
json.dump({'version': 1, 'slice': 1, 'size_mm_axes': 'three X (along flow), Y (height), Z (depth)',
           'sections': [{'group': g, 'name_vi': SEC_VI[g]} for g in con['naming']['groups']],
           'devices': devices_out}, open(W + 'dot1/devices.dot1.json', 'w'), ensure_ascii=False, indent=0)
mats = {}
for m in con['materials']:
    if m['web'] == 'exclude': continue
    rec = {'web': m['web'], 'cap_class': m['cap_class'], 'cap_color': m['cap_color']}
    if m.get('three_override'): rec['three_override'] = m['three_override']
    mats[m['material']] = rec
json.dump({'version': 1, 'doc': 'material name -> web handling. cap_color = runtime back-face cap colour (null = no runtime cap); pre-cut za_cap_* materials are drawn as exported. Đợt 1: za_fill_melt keeps the exported translucent amber (FillMaterial is Đợt 2) but gets DoubleSide; za_ghost_vent -> GhostMaterial; ze_sheet_pet / ze_melt_curtain / za_sc_* -> flat overrides (see PLAN-DOT1 §4).',
           'cap_colors': con['cap_colors'], 'materials': mats}, open(W + 'dot1/materials.dot1.json', 'w'), ensure_ascii=False, indent=0)
print('devices', len(devices_out), 'materials', len(mats))
