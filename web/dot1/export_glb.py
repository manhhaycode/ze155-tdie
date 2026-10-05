# export_glb.py - Đợt 1 GLB export from the SAVED out/ze155_anim.blend (option C, DECISIONS 30).
#
# Run ONLY as a separate background process, never inside the user's open Blender, never via MCP:
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup out/ze155_anim.blend \
#       --python web/dot1/export_glb.py -- --rules web/dot1/selection-rules.json --file all \
#       --out web/build/raw --report web/build/reports/export.json
#
# Safety: works on the in-memory copy only. There is NO save call in this file. It writes only under
# web/build/ (refuses any other --out / --report). It checks the .blend mtime/size before and after.
# --factory-startup keeps add-ons (BlenderMCP on 127.0.0.1:9876) and user prefs out of this process.
import bpy, json, os, sys, time, argparse

def args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--rules', required=True)
    p.add_argument('--file', choices=['line', 'interior', 'all'], default='all')
    p.add_argument('--out', required=True)
    p.add_argument('--report', required=True)
    p.add_argument('--tris', action='store_true', help='also count evaluated triangles per object (slower)')
    return p.parse_args(argv)

A = args()
WS = os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), '..'))  # workspace root (blend lives in out/)
BUILD = os.path.join(WS, 'web', 'build') + os.sep
for p in (A.out, A.report):
    ap = os.path.abspath(p if os.path.isabs(p) else os.path.join(WS, p))
    if not ap.startswith(BUILD):
        raise SystemExit(f'refusing to write outside web/build/: {ap}')
OUT = os.path.abspath(A.out if os.path.isabs(A.out) else os.path.join(WS, A.out))
REPORT = os.path.abspath(A.report if os.path.isabs(A.report) else os.path.join(WS, A.report))
os.makedirs(OUT, exist_ok=True); os.makedirs(os.path.dirname(REPORT), exist_ok=True)

rules = json.load(open(A.rules if os.path.isabs(A.rules) else os.path.join(WS, A.rules)))
blend = bpy.data.filepath
if not blend.endswith(rules['source_blend']):
    raise SystemExit(f'unexpected blend {blend}')
st0 = os.stat(blend)
report = {'blend': blend, 'blend_mtime_before': st0.st_mtime, 'blend_size_before': st0.st_size,
          'blender': bpy.app.version_string, 'files': {}}

scene = bpy.data.scenes[rules['scene']]
bpy.context.window.scene = scene
vl = scene.view_layers[0]
TYPES = set(rules['object_types'])
NEVER = set(rules['never_collections'])

def find_lc(lc, name):
    if lc.collection.name == name:
        return lc
    for c in lc.children:
        r = find_lc(c, name)
        if r:
            return r
    return None

def unhide_tree(lc):  # in memory only
    lc.exclude = False
    lc.hide_viewport = False
    lc.collection.hide_viewport = False
    for c in lc.children:
        unhide_tree(c)

def select(spec):
    objs = set()
    for cname in spec['include_collections']:
        lc = find_lc(vl.layer_collection, cname)
        if lc is None:
            raise SystemExit(f'collection {cname} not found')
        unhide_tree(lc)
        objs |= set(bpy.data.collections[cname].all_objects)
    for cname in spec.get('exclude_collections', []) + list(NEVER):
        if cname in bpy.data.collections:
            objs -= set(bpy.data.collections[cname].all_objects)
    objs = {o for o in objs if o.type in TYPES and o.name not in set(spec.get('exclude_objects', []))}
    for o in objs:
        o.hide_viewport = False
        o.hide_set(False, view_layer=vl)
    return objs

# rest pose for the rotor empties (already 0 in the saved file; re-asserted in memory)
for n in ('int_screw_axis_a', 'int_screw_axis_b', 'anim_roll_axis_bottom', 'anim_roll_axis_middle', 'anim_roll_axis_top'):
    if n in bpy.data.objects:
        report.setdefault('rest_pose_before', {})[n] = list(bpy.data.objects[n].rotation_euler)
        bpy.data.objects[n].rotation_euler = (0.0, 0.0, 0.0)
scene.frame_set(1)

COMMON = dict(
    export_format='GLB', check_existing=False, use_active_scene=True,
    use_selection=False, use_visible=False, use_renderable=False, use_active_collection=False,
    at_collection_center=False, export_hierarchy_full_collections=False, export_hierarchy_flatten_objs=False,
    export_extras=True, export_yup=True, export_apply=True,
    export_cameras=False, export_lights=False,
    export_materials='EXPORT', export_image_format='NONE', export_texcoords=False, export_normals=True,
    export_tangents=False, export_attributes=False, export_vertex_color='NONE',
    use_mesh_edges=False, use_mesh_vertices=False, export_gn_mesh=False, export_gpu_instances=False,
    export_shared_accessors=False,
    export_morph=True, export_morph_normal=True, export_morph_tangent=False, export_morph_animation=False,
    export_animations=False, export_skins=False,
    export_draco_mesh_compression_enable=False, export_meshopt_compression_enable=False, export_use_gltfpack=False,
    will_save_settings=False,
)

files = ['line', 'interior'] if A.file == 'all' else [A.file]
depsgraph = None
for name in files:
    spec = rules['files'][name]
    objs = select(spec)
    tmp = bpy.data.collections.new(f'__web_{name}')  # not linked to the scene; only used as the export filter
    for o in objs:
        tmp.objects.link(o)
    bpy.context.view_layer.update()
    rec = {'objects': len(objs),
           'by_type': {t: sum(1 for o in objs if o.type == t) for t in sorted({o.type for o in objs})},
           'names': sorted(o.name for o in objs)}
    exp = spec.get('expect', {})
    rec['expect_ok'] = (exp.get('objects') in (None, len(objs)) and exp.get('empties') in (None, rec['by_type'].get('EMPTY', 0))
                        and exp.get('curves') in (None, rec['by_type'].get('CURVE', 0)))
    if A.tris:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        tris = {}
        for o in objs:
            if o.type in ('MESH', 'CURVE'):
                oe = o.evaluated_get(depsgraph)
                m = oe.to_mesh()
                if m:
                    m.calc_loop_triangles(); tris[o.name] = len(m.loop_triangles)
                oe.to_mesh_clear()
        rec['tris_eval'] = sum(tris.values()); rec['tris_per_object'] = tris
    path = os.path.join(OUT, f'{name}.glb')
    t0 = time.time()
    bpy.ops.export_scene.gltf(filepath=path, collection=tmp.name, **COMMON)
    rec['seconds'] = round(time.time() - t0, 2)
    rec['bytes'] = os.path.getsize(path)
    rec['path'] = path
    report['files'][name] = rec
    for o in list(tmp.objects):
        tmp.objects.unlink(o)
    bpy.data.collections.remove(tmp)
    print(f'EXPORTED {name}: {rec["objects"]} objects, {rec["bytes"]/1e6:.1f} MB, {rec["seconds"]} s, expect_ok={rec["expect_ok"]}')

st1 = os.stat(blend)
report['blend_mtime_after'] = st1.st_mtime
report['blend_size_after'] = st1.st_size
report['blend_unchanged'] = (st0.st_mtime == st1.st_mtime and st0.st_size == st1.st_size)
report['is_dirty_in_memory'] = bpy.data.is_dirty  # True is expected (in-memory edits); nothing is written
json.dump(report, open(REPORT, 'w'), indent=1)
print('EXPORT DONE blend_unchanged=', report['blend_unchanged'])
if not report['blend_unchanged'] or not all(r['expect_ok'] for r in report['files'].values()):
    sys.exit(1)
