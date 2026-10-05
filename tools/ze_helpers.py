# ZE 155/34D helper library. Load inside Blender (via MCP execute_blender_code) with:
#   exec(open('/Users/manhhaycode/m3d-e2e/ze155-tdie/tools/ze_helpers.py').read())
# then in every later call:  Z = bpy.app.driver_namespace['ze']; MM = Z.MM
# Adapted from the GX200 spike helpers (tools/gx200_reference/call03_helpers.py).
import bpy, bmesh, math, json, os, types
from mathutils import Vector, Matrix

Z = types.SimpleNamespace()
MM = 0.001
Z.MM = MM
Z.ROOT = '/Users/manhhaycode/m3d-e2e/ze155-tdie/'
Z.OUT = Z.ROOT + 'out/'
Z.DRAW = Z.ROOT + 'drawings/'
Z.SCENE = 'ze155'
Z.COLLS = ('ze155_parts', 'ze155_rig', 'ze155_blockout', 'ze155_cutters', 'ze155_context')


def setup_scene():
    """Create (or reuse) the work scene and its collections; make it the window scene."""
    sc = bpy.data.scenes.get(Z.SCENE) or bpy.data.scenes.new(Z.SCENE)
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.length_unit = 'MILLIMETERS'
    sc.unit_settings.scale_length = 1.0
    for cn in Z.COLLS:
        c = bpy.data.collections.get(cn)
        if c is None:
            c = bpy.data.collections.new(cn)
        if c.name not in sc.collection.children:
            sc.collection.children.link(c)
    bpy.context.window.scene = sc
    return sc
Z.setup_scene = setup_scene


def scn():
    return bpy.data.scenes[Z.SCENE]
Z.scn = scn


def _remove(name):
    o = bpy.data.objects.get(name)
    if o is None:
        return
    us = list(o.users_scene)
    if us and any(s.name != Z.SCENE for s in us):
        raise RuntimeError('object %s belongs to another scene' % name)
    data = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    if data is not None and data.users == 0:
        if isinstance(data, bpy.types.Mesh): bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Camera): bpy.data.cameras.remove(data)
        elif isinstance(data, bpy.types.Light): bpy.data.lights.remove(data)
        elif isinstance(data, bpy.types.Curve): bpy.data.curves.remove(data)
Z.remove = _remove


def remove_prefix(prefix):
    """Remove every object of the work scene whose name starts with prefix."""
    names = [o.name for o in scn().objects if o.name.startswith(prefix)]
    for n in names:
        _remove(n)
    return names
Z.remove_prefix = remove_prefix


def link(o, coll='ze155_parts'):
    bpy.data.collections[coll].objects.link(o)
    return o
Z.link = link


def obj_from_bm(name, bm, mat=None, smooth=False, coll='ze155_parts'):
    _remove(name)
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    o = bpy.data.objects.new(name, me)
    link(o, coll)
    if mat is not None:
        me.materials.append(Z.mat(mat) if isinstance(mat, str) else mat)
    return o
Z.obj_from_bm = obj_from_bm


# ---------------------------------------------------------------- materials
# name: (sRGB colour, roughness, metallic). Extend with Z.MATS['x'] = (...) or Z.mat('x', col=..., ...).
MATS = {
    'frame':        ((0.62, 0.64, 0.66), 0.55, 0.0),   # placeholder, set from photos
    'cover':        ((0.80, 0.81, 0.82), 0.45, 0.0),
    'steel':        ((0.62, 0.62, 0.63), 0.35, 1.0),
    'steel_dark':   ((0.30, 0.30, 0.31), 0.45, 1.0),
    'chrome':       ((0.92, 0.92, 0.93), 0.08, 1.0),
    'cast':         ((0.55, 0.56, 0.57), 0.6, 0.6),
    'black':        ((0.03, 0.03, 0.035), 0.5, 0.0),
    'rubber':       ((0.02, 0.02, 0.02), 0.7, 0.0),
    'copper':       ((0.72, 0.45, 0.30), 0.35, 1.0),
    'yellow':       ((0.95, 0.75, 0.05), 0.4, 0.0),
    'red':          ((0.75, 0.06, 0.06), 0.4, 0.0),
    'blue':         ((0.05, 0.25, 0.55), 0.4, 0.0),
    'glass':        ((0.85, 0.9, 0.95), 0.05, 0.0),
    'floor':        ((0.55, 0.56, 0.58), 0.6, 0.0),
}
Z.MATS = MATS

# phase 1: palette from design/parts.json (sRGB hex) with roughness / metallic per finish
_RM = {"frame": (0.5, 0), "cover": (0.4, 0.3), "steel": (0.35, 0.9), "polished": (0.18, 1.0), "chrome": (0.06, 1.0),
       "blue_drive": (0.42, 0), "motor": (0.45, 0), "km_blue": (0.4, 0), "yellow": (0.45, 0), "orange": (0.45, 0),
       "black": (0.55, 0), "galv": (0.45, 0.8), "cabinet": (0.5, 0), "red": (0.4, 0), "glass": (0.05, 0),
       "stainless": (0.28, 0.9), "cast": (0.6, 0.5), "dark_steel": (0.45, 0.7), "grating": (0.5, 0.6),
       "floor": (0.75, 0), "rubber": (0.7, 0), "white": (0.45, 0), "hose": (0.4, 0.6)}
try:
    with open(Z.ROOT + 'design/parts.json') as _f:
        Z.PAL = json.load(_f)['meta']['palette']
    for _k, _h in Z.PAL.items():
        _h = _h.lstrip('#')
        MATS[_k] = (tuple(int(_h[i:i + 2], 16) / 255 for i in (0, 2, 4)),) + _RM.get(_k, (0.5, 0.0))
except Exception as _e:
    print('palette not loaded', _e)
MATS.setdefault('oilmat', ((0.93, 0.80, 0.10), 0.9, 0.0))     # yellow oil-absorbent mat (web-03)
MATS.setdefault('gauge_face', ((0.95, 0.95, 0.93), 0.3, 0.0))


def srgb2lin(c):
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)
Z.srgb2lin = srgb2lin


def mat(name, col=None, rough=None, metal=None):
    if col is not None or name not in MATS:
        old = MATS.get(name, ((0.6, 0.6, 0.6), 0.5, 0.0))
        MATS[name] = (col or old[0], old[1] if rough is None else rough, old[2] if metal is None else metal)
    elif rough is not None or metal is not None:
        old = MATS[name]
        MATS[name] = (old[0], old[1] if rough is None else rough, old[2] if metal is None else metal)
    mname = 'ze_' + name
    m = bpy.data.materials.get(mname) or bpy.data.materials.new(mname)
    try:
        m.use_nodes = True
    except Exception:
        pass
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    c, r, me = MATS[name]
    lc = srgb2lin(c)
    bsdf.inputs['Base Color'].default_value = (*lc, 1)
    bsdf.inputs['Roughness'].default_value = r
    bsdf.inputs['Metallic'].default_value = me
    m.diffuse_color = (*lc, 1)
    return m
Z.mat = mat


# ---------------------------------------------------------------- modifiers
def bevel(o, w_mm, segs=2, angle=40, harden=False, name='Bevel'):
    m = o.modifiers.new(name, 'BEVEL')
    m.width = w_mm * MM
    m.segments = segs
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.use_clamp_overlap = True
    m.harden_normals = harden
    return m


def wnormal(o):
    m = o.modifiers.new('WNormal', 'WEIGHTED_NORMAL')
    m.keep_sharp = True
    return m


def solidify(o, t_mm, offset=-1):
    m = o.modifiers.new('Solidify', 'SOLIDIFY')
    m.thickness = t_mm * MM
    m.offset = offset
    return m


def smooth(o, on=True):
    if on:
        o.data.shade_smooth()
    else:
        o.data.shade_flat()


def hard(o, w_mm, segs=2, angle=40):
    """smooth shading + bevel + weighted normals (cast / machined look)"""
    smooth(o)
    bevel(o, w_mm, segs, angle)
    wnormal(o)


def array(o, count, offset_mm, name='Array'):
    """constant-offset array; offset_mm = (dx, dy, dz) in mm"""
    m = o.modifiers.new(name, 'ARRAY')
    m.count = count
    m.use_relative_offset = False
    m.use_constant_offset = True
    m.constant_offset_displace = Vector(offset_mm) * MM
    return m
Z.bevel, Z.wnormal, Z.solidify, Z.smooth, Z.hard, Z.array = bevel, wnormal, solidify, smooth, hard, array


# ---------------------------------------------------------------- geometry (all inputs in mm)
def box_bm(x0, x1, y0, y1, z0, z1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (x0 if v.co.x < 0 else x1) * MM
        v.co.y = (y0 if v.co.y < 0 else y1) * MM
        v.co.z = (z0 if v.co.z < 0 else z1) * MM
    return bm
Z.box_bm = box_bm


def box(name, x0, x1, y0, y1, z0, z1, mat=None, bev=None, segs=2, coll='ze155_parts'):
    o = obj_from_bm(name, box_bm(x0, x1, y0, y1, z0, z1), mat, coll=coll)
    if bev:
        hard(o, bev, segs)
    return o
Z.box = box


def _plane_map(axis):
    # (u, v, d) -> world mm. axis = extrusion axis.
    if axis == 'X':
        return lambda u, v, d: Vector((d, u, v))     # outline in YZ
    if axis == 'Y':
        return lambda u, v, d: Vector((u, d, v))     # outline in XZ
    return lambda u, v, d: Vector((u, v, d))         # outline in XY


def extrude_bm(pts, axis, d0, d1):
    f = _plane_map(axis)
    bm = bmesh.new()
    vs = [bm.verts.new(f(u, v, d0) * MM) for (u, v) in pts]
    face = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    nv = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=f(0, 0, d1 - d0) * MM, verts=nv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
Z.extrude_bm = extrude_bm


def extrude(name, pts, axis, d0, d1, mat=None, bev=None, segs=2, angle=40, coll='ze155_parts'):
    """pts: outline (u, v) in mm in the plane normal to axis; extruded from d0 to d1 along axis.
    axis 'X': (u, v) = (y, z); 'Y': (u, v) = (x, z); 'Z': (u, v) = (x, y)."""
    o = obj_from_bm(name, extrude_bm(pts, axis, d0, d1), mat, coll=coll)
    if bev:
        hard(o, bev, segs, angle)
    return o
Z.extrude = extrude


def revolve_bm(prof, segs=48):
    """prof: list of (r, h) in mm, revolved about local Z."""
    bm = bmesh.new()
    vs = [bm.verts.new(Vector((r * MM, 0, h * MM))) for (r, h) in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1),
                   angle=math.radians(360), steps=segs, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
Z.revolve_bm = revolve_bm


def axis_matrix(origin_mm, axis):
    a = Vector(axis).normalized()
    q = Vector((0, 0, 1)).rotation_difference(a)
    return Matrix.Translation(Vector(origin_mm) * MM) @ q.to_matrix().to_4x4()
Z.axis_matrix = axis_matrix


def revolve(name, prof, origin, axis=(0, 0, 1), segs=48, mat=None, smooth_=True, coll='ze155_parts'):
    """profile (r, h) mm revolved about `axis` through `origin` (mm); h runs along axis."""
    bm = revolve_bm(prof, segs)
    bm.transform(axis_matrix(origin, axis))
    return obj_from_bm(name, bm, mat, smooth=smooth_, coll=coll)
Z.revolve = revolve


def cyl(name, r, h0, h1, origin, axis=(0, 0, 1), segs=48, mat=None, coll='ze155_parts'):
    """closed cylinder radius r (mm) from h0 to h1 along axis through origin."""
    return revolve(name, [(0, h0), (r, h0), (r, h1), (0, h1)], origin, axis, segs, mat, coll=coll)
Z.cyl = cyl


def tube(name, path_mm, r, segs=16, mat=None, coll='ze155_parts'):
    """pipe/hose/cable along a polyline (mm) using a bevelled curve; returns the curve object."""
    _remove(name)
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r * MM
    cu.bevel_resolution = max(1, segs // 4)
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(path_mm) - 1)
    for p, q in zip(sp.points, path_mm):
        p.co = (q[0] * MM, q[1] * MM, q[2] * MM, 1)
    o = bpy.data.objects.new(name, cu)
    link(o, coll)
    if mat is not None:
        cu.materials.append(Z.mat(mat) if isinstance(mat, str) else mat)
    return o
Z.tube = tube


def rrect(cx, cy, w, h, r, n=6):
    """rounded-rectangle outline (mm) centred at (cx, cy)."""
    pts = []
    r = min(r, w / 2 - 1e-3, h / 2 - 1e-3)
    for (qx, qy, a0) in [(cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90),
                         (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)]:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((qx + r * math.cos(a), qy + r * math.sin(a)))
    return pts
Z.rrect = rrect


def boolean(o, cutter, op='DIFFERENCE', solver='MANIFOLD'):
    m = o.modifiers.new('Bool_' + cutter.name, 'BOOLEAN')
    m.operation = op
    m.object = cutter
    try:
        m.solver = solver
    except Exception:
        try:
            m.solver = 'EXACT'
        except Exception:
            pass
    cutter.display_type = 'WIRE'
    cutter.hide_render = True
    if cutter.name not in bpy.data.collections['ze155_cutters'].objects:
        for c in list(cutter.users_collection):
            c.objects.unlink(cutter)
        bpy.data.collections['ze155_cutters'].objects.link(cutter)
    cutter.hide_set(True, view_layer=scn().view_layers[0])
    return m
Z.boolean = boolean


def apply_mods(o):
    """apply all modifiers via the evaluated mesh (no bpy.ops)."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    old = o.data
    o.modifiers.clear()
    o.data = me
    me.name = o.name
    if old.users == 0:
        bpy.data.meshes.remove(old)
Z.apply_mods = apply_mods


# ---------------------------------------------------------------- cameras
_AX = {'+X': (1, 0, 0), '-X': (-1, 0, 0), '+Y': (0, 1, 0), '-Y': (0, -1, 0), '+Z': (0, 0, 1), '-Z': (0, 0, -1)}


def load_views():
    p = Z.DRAW + 'views.json'
    with open(p) as f:
        Z.VIEWS = json.load(f)
    return Z.VIEWS
Z.load_views = load_views


def make_ortho_cam(key, dist_mm=20000, alpha=0.5):
    """orthographic camera matching drawings/views.json[key], drawing as background image."""
    v = Z.VIEWS[key]
    name = 'cam_' + key
    _remove(name)
    cd = bpy.data.cameras.new(name)
    cd.type = 'ORTHO'
    W, H, s = v['width_px'], v['height_px'], v['px_per_mm']
    cd.ortho_scale = max(W, H) / s * MM
    cd.sensor_fit = 'AUTO'
    cd.clip_start = 0.01
    cd.clip_end = 2 * dist_mm * MM
    cam = bpy.data.objects.new(name, cd)
    link(cam, 'ze155_rig')
    right, up, look = Vector(_AX[v['right']]), Vector(_AX[v['up']]), Vector(_AX[v['look']])
    rot = Matrix((right, up, -look)).transposed()          # camera local X, Y, Z(back) columns
    c = Vector(v['center_mm'])
    c = c - look * c.dot(look)                             # drop the depth coordinate
    cam.matrix_world = Matrix.Translation((c - look * dist_mm) * MM) @ rot.to_4x4()
    img_path = Z.DRAW + v['image']
    if os.path.exists(img_path):
        img = bpy.data.images.load(img_path, check_existing=True)
        cd.show_background_images = True
        cd.background_images.clear()
        bg = cd.background_images.new()
        bg.image = img
        bg.alpha = alpha
        bg.display_depth = 'FRONT'
        bg.frame_method = 'FIT'
    return cam
Z.make_ortho_cam = make_ortho_cam


def persp_cam(name, az, el, lens, target_mm, dist_m, shift=(0, 0)):
    """az 0 looks along +X; camera at target + dist*(-cos e cos a, -cos e sin a, sin e)."""
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, cd)
    if cam.name not in bpy.data.collections['ze155_rig'].objects:
        link(cam, 'ze155_rig')
    cd.type = 'PERSP'
    cd.lens = lens
    cd.clip_start = 0.05
    cd.clip_end = 200
    cd.shift_x, cd.shift_y = shift
    a, e = math.radians(az), math.radians(el)
    d = Vector((-math.cos(e) * math.cos(a), -math.cos(e) * math.sin(a), math.sin(e)))
    T = Vector(target_mm) * MM
    cam.location = T + d * dist_m
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    return cam
Z.persp_cam = persp_cam


# ---------------------------------------------------------------- render & checks
def set_engine(sc, eng):
    try:
        sc.render.engine = eng
    except TypeError as e:
        print('engine err', e)
Z.set_engine = set_engine


def render(cam_name, path, engine='BLENDER_WORKBENCH', res=None, transparent=True, samples=16):
    sc = scn()
    bpy.context.window.scene = sc
    cam = bpy.data.objects[cam_name]
    sc.camera = cam
    key = cam_name[4:]
    if res:
        sc.render.resolution_x, sc.render.resolution_y = res
    elif getattr(Z, 'VIEWS', None) and key in Z.VIEWS:
        sc.render.resolution_x, sc.render.resolution_y = Z.VIEWS[key]['width_px'], Z.VIEWS[key]['height_px']
    sc.render.resolution_percentage = 100
    set_engine(sc, engine)
    sc.render.film_transparent = transparent
    if engine == 'BLENDER_WORKBENCH':
        sh = sc.display.shading
        sh.light = 'STUDIO'
        sh.color_type = 'MATERIAL'
        sh.show_cavity = True
        sh.cavity_type = 'BOTH'
        sh.show_object_outline = True
        sh.show_specular_highlight = True
        try:
            sc.display.render_aa = '8'
        except Exception:
            pass
    else:
        try:
            sc.eevee.taa_render_samples = samples
        except Exception:
            pass
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    return path
Z.render = render


def bbox(prefixes=None, colls=('ze155_parts',)):
    """world bounding box (mm) of evaluated objects in the given collections."""
    dg = bpy.context.evaluated_depsgraph_get()
    lo = Vector((1e9, 1e9, 1e9)); hi = -lo
    n = 0
    for cn in colls:
        for o in bpy.data.collections[cn].all_objects:
            if o.type not in ('MESH', 'CURVE') or o.hide_render:
                continue
            if prefixes and not o.name.startswith(tuple(prefixes)):
                continue
            oe = o.evaluated_get(dg)
            if o.type == 'CURVE':          # curve bound_box is unreliable in 5.2: use the evaluated mesh
                me = oe.to_mesh()
                pts = [oe.matrix_world @ v.co for v in me.vertices]
                oe.to_mesh_clear()
            else:
                pts = [oe.matrix_world @ Vector(c) for c in oe.bound_box]
            for w in pts:
                lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
            n += 1
    lo, hi = lo / MM, hi / MM
    return dict(n=n, min=tuple(round(x, 1) for x in lo), max=tuple(round(x, 1) for x in hi),
                size=tuple(round(x, 1) for x in (hi - lo)))
Z.bbox = bbox


def save_blend(path=None):
    """write only the work scene to a .blend (never touches the open file)."""
    path = path or Z.OUT + 'ze155.blend'
    bpy.data.libraries.write(path, {scn()}, fake_user=True)
    with bpy.data.libraries.load(path) as (src, _):
        info = dict(scenes=list(src.scenes), n_objects=len(src.objects), n_materials=len(src.materials))
    return path, info
Z.save_blend = save_blend



# ---------------------------------------------------------------- phase-1 additions: multi-part bmesh builders (mm)
# Build several primitives into one bmesh (one object, several materials by index), then Z.obj().
def _tag(bm, verts, mi):
    fs = set()
    for v in verts:
        fs.update(v.link_faces)
    for f in fs:
        f.material_index = mi
    return list(fs)


def bm_box(bm, x0, x1, y0, y1, z0, z1, mi=0):
    """axis-aligned box appended to bm."""
    t = box_bm(x0, x1, y0, y1, z0, z1)
    me = bpy.data.meshes.new('_tmp'); t.to_mesh(me); t.free()
    old = set(bm.verts)
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bm.verts.ensure_lookup_table()
    return _tag(bm, [v for v in bm.verts if v not in old], mi)
Z.bm_box = bm_box


def bm_cyl(bm, r, h0, h1, origin, axis=(0, 0, 1), segs=24, r2=None, mi=0, rot=0.0):
    """cylinder/cone (r at h0, r2 at h1) along axis through origin (mm), appended to bm."""
    a = Vector(axis).normalized()
    c = Vector(origin) + a * ((h0 + h1) / 2)
    M = axis_matrix(c, a) @ Matrix.Rotation(rot, 4, 'Z')
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                                radius1=r * MM, radius2=(r if r2 is None else r2) * MM,
                                depth=abs(h1 - h0) * MM, matrix=M)
    return _tag(bm, res['verts'], mi)
Z.bm_cyl = bm_cyl


def bm_rev(bm, prof, origin, axis=(0, 0, 1), segs=32, mi=0):
    """revolved (r, h) profile appended to bm."""
    t = revolve_bm(prof, segs)
    t.transform(axis_matrix(origin, axis))
    me = bpy.data.meshes.new('_tmp'); t.to_mesh(me); t.free()
    old = set(bm.verts)
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bm.verts.ensure_lookup_table()
    return _tag(bm, [v for v in bm.verts if v not in old], mi)
Z.bm_rev = bm_rev


def bm_ext(bm, pts, axis, d0, d1, mi=0):
    """extruded outline appended to bm (same convention as Z.extrude)."""
    t = extrude_bm(pts, axis, d0, d1)
    me = bpy.data.meshes.new('_tmp'); t.to_mesh(me); t.free()
    old = set(bm.verts)
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bm.verts.ensure_lookup_table()
    return _tag(bm, [v for v in bm.verts if v not in old], mi)
Z.bm_ext = bm_ext


def bm_bolts(bm, centre, axis, pcd, n, r_head, h, segs=6, phase=0.0, mi=0, washer=0.0):
    """n hex heads (or studs) on a bolt circle of diameter pcd around `axis` through centre (mm);
    heads extend from the centre plane along +axis by h."""
    a = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = a.cross(ref).normalized(); v = a.cross(u)
    for i in range(n):
        t = phase + 2 * math.pi * i / n
        p = Vector(centre) + (u * math.cos(t) + v * math.sin(t)) * (pcd / 2)
        if washer:
            bm_cyl(bm, r_head * 1.35, 0, washer, p, a, 16, mi=mi)
        bm_cyl(bm, r_head, washer, washer + h, p, a, segs, mi=mi)
Z.bm_bolts = bm_bolts


def obj(name, bm, mats, bev=None, segs=2, angle=40, smooth_=True, coll='ze155_parts', wn=True):
    """object from a multi-material bmesh; mats = list of material keys (index = face material_index)."""
    o = obj_from_bm(name, bm, None, coll=coll)
    for m in mats:
        o.data.materials.append(Z.mat(m) if isinstance(m, str) else m)
    if smooth_:
        o.data.shade_smooth()
    if bev:
        bevel(o, bev, segs, angle)
    if wn and smooth_:
        wnormal(o)
    return o
Z.obj = obj


def tris(colls=('ze155_parts',)):
    """triangle count of evaluated, render-visible objects."""
    dg = bpy.context.evaluated_depsgraph_get()
    n = 0
    for cn in colls:
        for o in bpy.data.collections[cn].all_objects:
            if o.type not in ('MESH', 'CURVE') or o.hide_render:
                continue
            oe = o.evaluated_get(dg)
            me = oe.to_mesh()
            me.calc_loop_triangles()
            n += len(me.loop_triangles)
            oe.to_mesh_clear()
    return n
Z.tris = tris



def pipe(name, path_mm, r, mat='steel', fit_mat='steel', fittings=True, segs=16, coll='ze155_parts'):
    """pipe along a polyline: tube + hex unions at both ends + elbow sleeves at the corners (one extra object)."""
    o = tube(name, path_mm, r, segs, mat, coll)
    if not fittings:
        return o
    bm = bmesh.new()
    P = [Vector(p) for p in path_mm]
    for (a, b) in [(P[0], P[1]), (P[-1], P[-2])]:
        d = (b - a).normalized()
        bm_cyl(bm, r * 1.55, 0, r * 1.6, a, d, 6, mi=0)
        bm_cyl(bm, r * 1.25, r * 1.6, r * 2.6, a, d, 16, mi=0)
    for i in range(1, len(P) - 1):
        for q in (P[i - 1], P[i + 1]):
            d = (q - P[i]).normalized()
            L = min(r * 2.2, (q - P[i]).length * 0.45)
            bm_cyl(bm, r * 1.18, -r * 1.18, L, P[i], d, 16, mi=0)
    obj(name + '_fit', bm, [fit_mat], bev=max(0.5, r * 0.08), segs=1, coll=coll)
    return o
Z.pipe = pipe



def ortho_free(name, center_mm, look, up, scale_m, dist_mm=30000):
    """free orthographic camera (no views.json needed): look/up are world vectors, centre in mm."""
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    cd.type = 'ORTHO'; cd.ortho_scale = scale_m; cd.clip_start = 0.01; cd.clip_end = 2 * dist_mm * MM + 20
    o = bpy.data.objects.get(name) or bpy.data.objects.new(name, cd)
    if o.name not in bpy.data.collections['ze155_rig'].objects:
        link(o, 'ze155_rig')
    look = Vector(look); up = Vector(up); right = look.cross(up)
    rot = Matrix((right, up, -look)).transposed()
    o.matrix_world = Matrix.Translation((Vector(center_mm) - look * dist_mm) * MM) @ rot.to_4x4()
    return o
Z.ortho_free = ortho_free


def load_parts():
    with open(Z.ROOT + 'design/parts.json') as f:
        Z.PARTS = {p['id']: p for p in json.load(f)['parts']}
    return Z.PARTS
Z.load_parts = load_parts


def hide_blk(ids):
    """hide blockout boxes (viewport + render) of parts that detailed geometry replaces."""
    vl = scn().view_layers[0]
    for i in ids:
        o = bpy.data.objects.get('blk_' + i)
        if o:
            o.hide_render = True
            o.hide_set(True, view_layer=vl)
Z.hide_blk = hide_blk



def render_check(cam, path, hide_ids=(), hide_prefixes=(), **kw):
    """render with some blockout boxes / objects temporarily hidden from render, then restore."""
    tmp = []
    for o in scn().objects:
        n = o.name[4:] if o.name.startswith('blk_') else o.name
        if (o.name.startswith('blk_') and (n in hide_ids or n.startswith(tuple(hide_prefixes)) if hide_prefixes else n in hide_ids)) and not o.hide_render:
            o.hide_render = True; tmp.append(o)
    try:
        return render(cam, path, **kw)
    finally:
        for o in tmp:
            o.hide_render = False
Z.render_check = render_check
Z.OBSTRUCT = ('feed_platform', 'feed_stair', 'ctrl_drive_cabinet', 'ctrl_heater_cabinet', 'ctrl_hmi', 'feed_control', 'ctrl_cable_mv', 'ctrl_floor_duct', 'ctrl_cable_drop')



def gauge(bm, c, axis=(0, 1, 0), r=34, mi_body=0, mi_face=3):
    """pressure gauge (body + face disc) centred at c, face toward +axis."""
    bm_cyl(bm, r, -14, 12, c, axis, 32, mi=mi_body)
    bm_cyl(bm, r - 5, 12, 15, c, axis, 32, mi=mi_face)
Z.gauge = gauge


def add_bm(bm, t, mi=0):
    """append a free-standing bmesh t (already transformed) to bm with material index mi."""
    me = bpy.data.meshes.new('_t'); t.to_mesh(me); t.free()
    old = set(bm.verts); bm.from_mesh(me); bpy.data.meshes.remove(me)
    bm.verts.ensure_lookup_table()
    return _tag(bm, [v for v in bm.verts if v not in old], mi)
Z.add_bm = add_bm


bpy.app.driver_namespace['ze'] = Z
print('ze helpers ok', len(vars(Z)))


# ---------------------------------------------------------------- phase-2 additions (barrel, feeding, vacuum)
def bm_arc(bm, x0, x1, ri, ro, a0, a1, cy=0.0, cz=1200.0, segs=None, mi=0):
    """annular sector solid along X (x0..x1), radii ri..ro about the line (y=cy, z=cz);
    angles in degrees in the YZ plane: 0 = +Y, 90 = +Z, -90 = -Z. Full ring when a1 - a0 >= 360."""
    full = (a1 - a0) >= 359.999
    n = segs or max(4, int(abs(a1 - a0) / 7.5))
    angs = [math.radians(a0 + (a1 - a0) * i / n) for i in range(n + (0 if full else 1))]
    def P(x, r, t):
        return Vector((x * MM, (cy + r * math.cos(t)) * MM, (cz + r * math.sin(t)) * MM))
    rings = []
    for x in (x0, x1):
        rings.append(([bm.verts.new(P(x, ri, t)) for t in angs], [bm.verts.new(P(x, ro, t)) for t in angs]))
    m = len(angs)
    fs = []
    rng = range(m) if full else range(m - 1)
    (i0, o0), (i1, o1) = rings
    for k in rng:
        j = (k + 1) % m
        fs.append(bm.faces.new((o0[k], o0[j], o1[j], o1[k])))      # outer
        fs.append(bm.faces.new((i0[j], i0[k], i1[k], i1[j])))      # inner
        fs.append(bm.faces.new((i0[k], i0[j], o0[j], o0[k])))      # end x0
        fs.append(bm.faces.new((o1[k], o1[j], i1[j], i1[k])))      # end x1
    if not full:
        fs.append(bm.faces.new((i0[0], o0[0], o1[0], i1[0])))
        fs.append(bm.faces.new((o0[-1], i0[-1], i1[-1], o1[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.material_index = mi
    return fs
Z.bm_arc = bm_arc


def bm_star(bm, centre, axis, r_out, r_in, n_pts, h0, h1, mi=0, rot=0.0):
    """star prism (12-point nut: n_pts=12) along axis through centre (mm), from h0 to h1."""
    pts = []
    for i in range(2 * n_pts):
        t = rot + math.pi * i / n_pts
        r = r_out if i % 2 == 0 else r_in
        pts.append((r * math.cos(t), r * math.sin(t)))
    t = extrude_bm(pts, 'Z', h0, h1)
    t.transform(axis_matrix(centre, axis))
    return add_bm(bm, t, mi)
Z.bm_star = bm_star


def bm_frustum(bm, z0, z1, b, t, mi=0):
    """rectangular frustum: b = (x0, x1, y0, y1) at z0, t = (x0, x1, y0, y1) at z1 (mm)."""
    vs = [bm.verts.new(Vector(p) * MM) for p in
          [(b[0], b[2], z0), (b[1], b[2], z0), (b[1], b[3], z0), (b[0], b[3], z0),
           (t[0], t[2], z1), (t[1], t[2], z1), (t[1], t[3], z1), (t[0], t[3], z1)]]
    F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    fs = [bm.faces.new([vs[i] for i in f]) for f in F]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.material_index = mi
    return fs
Z.bm_frustum = bm_frustum


def bm_seg(bm, a, b, r, segs=12, mi=0):
    """cylinder between two points a, b (mm)."""
    a = Vector(a); b = Vector(b); d = b - a
    return bm_cyl(bm, r, 0, d.length, a, d.normalized(), segs, mi=mi)
Z.bm_seg = bm_seg


def hose(name, path_mm, r, mat='hose', segs=12, order=3, coll='ze155_parts'):
    """smooth flexible hose / cable: NURBS tube through the end points, pulled toward the inner points."""
    o = tube(name, path_mm, r, segs, mat, coll)
    sp = o.data.splines[0]
    sp.type = 'NURBS'
    sp.order_u = min(order, len(path_mm))
    sp.use_endpoint_u = True
    sp.resolution_u = 8
    return o
Z.hose = hose


def hoses(name, paths, r, mat='hose', segs=12, coll='ze155_parts'):
    """several smooth hoses in one curve object."""
    o = hose(name, paths[0], r, mat, segs, coll=coll)
    cu = o.data
    for pth in paths[1:]:
        sp = cu.splines.new('NURBS')
        sp.points.add(len(pth) - 1)
        for p, q in zip(sp.points, pth):
            p.co = (q[0] * MM, q[1] * MM, q[2] * MM, 1)
        sp.order_u = min(3, len(pth)); sp.use_endpoint_u = True; sp.resolution_u = 8
    return o
Z.hoses = hoses


def bm_flange(bm, c, axis, r_out, t, n_bolts, pcd, r_bolt=None, mi=0, mi_bolt=None, segs=32):
    """pipe flange disc with hex bolt heads on both faces (mm)."""
    a = Vector(axis).normalized()
    bm_cyl(bm, r_out, -t / 2, t / 2, c, a, segs, mi=mi)
    rb = r_bolt or max(5, r_out * 0.09)
    mb = mi if mi_bolt is None else mi_bolt
    bm_bolts(bm, Vector(c) + a * (t / 2), a, pcd, n_bolts, rb, rb * 0.9, 6, math.pi / n_bolts, mi=mb)
    bm_bolts(bm, Vector(c) - a * (t / 2), -a, pcd, n_bolts, rb, rb * 0.9, 6, math.pi / n_bolts, mi=mb)
Z.bm_flange = bm_flange


def bm_valve_lever(bm, c, axis_stem=(0, 0, 1), lever_dir=(1, 0, 0), L=180, mi_body=0, mi_handle=1, r_body=None, body_axis=(1, 0, 0), dn=50):
    """ball valve: body along body_axis, stem along axis_stem, red lever toward lever_dir (mm)."""
    rb = r_body or dn * 0.75
    bm_cyl(bm, rb, -dn * 0.9, dn * 0.9, c, body_axis, 16, mi=mi_body)
    bm_cyl(bm, rb * 0.62, -dn * 1.15, dn * 1.15, c, body_axis, 6, mi=mi_body)
    s = Vector(axis_stem).normalized()
    top = Vector(c) + s * (rb + dn * 0.35)
    bm_cyl(bm, dn * 0.12, 0, rb + dn * 0.35, c, s, 8, mi=mi_body)
    d = Vector(lever_dir).normalized()
    w = max(6, dn * 0.14)
    a = top; b = top + d * L
    bm_seg(bm, a, b, w * 0.6, 8, mi=mi_handle)
    bm_cyl(bm, w, 0, w * 1.6, b - d * w * 0.8, d, 10, mi=mi_handle)
Z.bm_valve_lever = bm_valve_lever


def fillet_path(path_mm, R, n=6):
    """polyline with every interior corner replaced by an arc of radius R (mm), for rigid pipes."""
    P = [Vector(p) for p in path_mm]
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        d1 = (b - a).normalized(); d2 = (c - b).normalized()
        ang = d1.angle(d2)
        if ang < 1e-3:
            out.append(b); continue
        t = min(R * math.tan(ang / 2), (b - a).length * 0.48, (c - b).length * 0.48)
        p1 = b - d1 * t; p2 = b + d2 * t
        for k in range(n + 1):
            s = k / n      # quadratic Bezier approximates the arc well enough at these angles
            out.append(p1 * (1 - s) ** 2 + b * 2 * s * (1 - s) + p2 * s * s)
    out.append(P[-1])
    return [tuple(v) for v in out]
Z.fillet_path = fillet_path


def render_parts(cam, path, **kw):
    """render with the whole blockout and context collections hidden (parts only), then restore."""
    bc = bpy.data.collections['ze155_blockout']; ctx = bpy.data.collections['ze155_context']
    st = bc.hide_render, ctx.hide_render
    bc.hide_render = True; ctx.hide_render = True
    try:
        return render(cam, path, **kw)
    finally:
        bc.hide_render, ctx.hide_render = st
Z.render_parts = render_parts
Z.MATS.setdefault('barrel_steel', ((0.62, 0.64, 0.66), 0.32, 0.65))


# ---------------------------------------------------------------- phase-3 additions (melt line, T-die, roll stack)
# Phase-3 fix: bm_box / bm_rev / bm_ext / add_bm now find the appended verts by set difference. In Blender 5.2 the
# vertex table after bmesh.ops.create_cone (bm_cyl) is stale, so bm.verts[n0:] picked cone verts and re-tagged some
# cylinder faces with the next primitive's material (seen as stray red/yellow faces in phases 1-3).
def bm_socket(bm, centre, axis, pcd, n, r, h, phase=0.0, mi=0, mi_hole=None, ref=None):
    """n socket-head cap screws on a bolt circle (pcd) about axis through centre; heads stand h along +axis.
    A dark hex disc on each head reads as the socket (mi_hole)."""
    a = Vector(axis).normalized()
    rv = Vector(ref) if ref is not None else (Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0)))
    u = a.cross(rv).normalized(); v = a.cross(u)
    for i in range(n):
        t = phase + 2 * math.pi * i / n
        p = Vector(centre) + (u * math.cos(t) + v * math.sin(t)) * (pcd / 2)
        bm_cyl(bm, r, 0, h, p, a, 16, mi=mi)
        if mi_hole is not None:
            bm_cyl(bm, r * 0.48, h, h + 0.8, p, a, 6, mi=mi_hole)
Z.bm_socket = bm_socket


def bm_socket_at(bm, p, axis, r, h, mi=0, mi_hole=None):
    """one socket-head cap screw at point p (mm), head along +axis."""
    a = Vector(axis).normalized()
    bm_cyl(bm, r, 0, h, p, a, 16, mi=mi)
    if mi_hole is not None:
        bm_cyl(bm, r * 0.48, h, h + 0.8, p, a, 6, mi=mi_hole)
Z.bm_socket_at = bm_socket_at


def bm_torus(bm, centre, axis, R, a, segs=24, rsegs=8, mi=0):
    """torus (major radius R, tube radius a) about axis through centre (mm)."""
    prof = [(R + a * math.cos(2 * math.pi * k / rsegs), a * math.sin(2 * math.pi * k / rsegs)) for k in range(rsegs + 1)]
    return bm_rev(bm, prof, centre, axis, segs, mi)
Z.bm_torus = bm_torus


def bm_loft(bm, ra, rb, mi=0, caps=True):
    """solid between two closed rings of world points (mm, same count, same winding)."""
    A = [bm.verts.new(Vector(p) * MM) for p in ra]
    B = [bm.verts.new(Vector(p) * MM) for p in rb]
    n = len(A); fs = []
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    if caps:
        fs.append(bm.faces.new(A[::-1])); fs.append(bm.faces.new(B))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.material_index = mi
    return fs
Z.bm_loft = bm_loft


def ring_circle_x(x, r, n, cy=0.0, cz=1200.0):
    """closed ring of n points (mm) on a circle in the plane X = x."""
    return [(x, cy + r * math.cos(2 * math.pi * k / n), cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
Z.ring_circle_x = ring_circle_x


def ring_rect_x(x, w, h, n, cy=0.0, cz=1200.0):
    """closed ring of n points (mm) on a w x h rectangle in the plane X = x, same angular order as ring_circle_x."""
    out = []
    for k in range(n):
        t = 2 * math.pi * k / n
        c, s = math.cos(t), math.sin(t)
        f = min((w / 2) / abs(c) if abs(c) > 1e-9 else 1e9, (h / 2) / abs(s) if abs(s) > 1e-9 else 1e9)
        out.append((x, cy + c * f, cz + s * f))
    return out
Z.ring_rect_x = ring_rect_x


def bm_eyebolt(bm, base, axis=(0, 0, 1), d=36, ring_R=40, plane_ref=(1, 0, 0), mi=0):
    """lifting eye bolt (DIN 580 style) standing on base along axis: shank, collar, ring."""
    a = Vector(axis).normalized()
    bm_cyl(bm, d * 1.05, 0, d * 0.45, base, a, 20, mi=mi)
    bm_cyl(bm, d * 0.55, d * 0.45, d * 1.3, base, a, 12, mi=mi)
    c = Vector(base) + a * (d * 1.3 + ring_R)
    ring_axis = a.cross(Vector(plane_ref)).normalized()
    bm_torus(bm, c, ring_axis, ring_R - d * 0.25, d * 0.28, 20, 8, mi)
Z.bm_eyebolt = bm_eyebolt


def tubes(name, paths, r, mat='galv', segs=12, coll='ze155_parts'):
    """several rigid tubes / conduits (poly splines, already filleted if wanted) in one curve object."""
    o = tube(name, paths[0], r, segs, mat, coll)
    cu = o.data
    for pth in paths[1:]:
        sp = cu.splines.new('POLY')
        sp.points.add(len(pth) - 1)
        for p, q in zip(sp.points, pth):
            p.co = (q[0] * MM, q[1] * MM, q[2] * MM, 1)
    return o
Z.tubes = tubes


def bm_gland(bm, p, d, r, mi=0):
    """cable gland / conduit fitting: hex nut + dome along direction d at point p (mm)."""
    d = Vector(d).normalized()
    bm_cyl(bm, r * 1.5, 0, r * 0.9, p, d, 6, mi=mi)
    bm_cyl(bm, r * 1.25, r * 0.9, r * 2.0, p, d, 12, r2=r * 1.05, mi=mi)
Z.bm_gland = bm_gland


def bm_band(bm, x, w, ri, ro, gaps=(), cz=1200.0, mi=0, mi_clamp=None):
    """heater band ring (X centre x, width w) with angular gaps [(a0, a1), ...] in degrees (0 = +Y, 90 = +Z)."""
    segs = sorted(gaps)
    spans = []
    if not segs:
        spans = [(0, 360)]
    else:
        for i, (g0, g1) in enumerate(segs):
            nxt = segs[(i + 1) % len(segs)][0] + (360 if i == len(segs) - 1 else 0)
            spans.append((g1, nxt))
    for (a0, a1) in spans:
        bm_arc(bm, x - w / 2, x + w / 2, ri, ro, a0, a1, cz=cz, mi=mi)
    mc = mi if mi_clamp is None else mi_clamp
    for (g0, g1) in segs:            # clamp lugs at the gap edges
        for ang in (g0, g1):
            t = math.radians(ang)
            p = Vector((x, ro * math.cos(t), cz + ro * math.sin(t)))
            n = Vector((0, math.cos(t), math.sin(t)))
            bm_cyl(bm, w * 0.18, -2, 14, p, n, 8, mi=mc)
Z.bm_band = bm_band


# phase-3 materials (sRGB, roughness, metallic); alpha of sheet_pet (0.38) and melt_curtain (0.8) is set on the node
for _k, _v in {'ptfe': ((0.93, 0.93, 0.9), 0.6, 0.0), 'terminal_grey': ((0.62, 0.64, 0.66), 0.5, 0.2),
               'insul_pad': ((0.75, 0.72, 0.62), 0.8, 0.0), 'purge': ((0.28, 0.2, 0.12), 0.3, 0.0),
               'die_chrome': ((0xE3 / 255, 0xE6 / 255, 0xE9 / 255), 0.16, 0.78), 'screen': ((0.05, 0.12, 0.2), 0.15, 0.0),
               'lamp_green': ((0.1, 0.75, 0.2), 0.3, 0.0), 'lamp_white': ((0.95, 0.95, 0.9), 0.3, 0.0),
               'sheet_pet': ((0.72, 0.86, 0.9), 0.05, 0.0), 'melt_curtain': ((0.93, 0.72, 0.38), 0.04, 0.0),
               'pipe_blue': ((0.2, 0.45, 0.75), 0.4, 0.0)}.items():
    MATS.setdefault(_k, _v)


def render_noblk(cam, path, **kw):
    """render with the blockout collection and the floor hidden (parts + context), then restore."""
    bc = bpy.data.collections['ze155_blockout']; st = bc.hide_render; bc.hide_render = True
    fl = bpy.data.objects.get('ctx_floor'); fs = fl.hide_render if fl else None
    if fl: fl.hide_render = True
    try:
        return render(cam, path, **kw)
    finally:
        bc.hide_render = st
        if fl: fl.hide_render = fs
Z.render_noblk = render_noblk


def render_iso(cam, path, keep=None, hide=(), res=(1200, 900), engine='BLENDER_EEVEE', ctx=True):
    """photo-check render: optional keep-prefix isolation, blockout hidden, context optional (EEVEE, opaque)."""
    sc = scn(); tmp = []
    bc = bpy.data.collections['ze155_blockout']; bst = bc.hide_render; bc.hide_render = True
    for o in sc.objects:
        if o.type not in ('MESH', 'CURVE') or o.hide_render:
            continue
        if o.users_collection and o.users_collection[0].name in ('ze155_blockout', 'ze155_cutters', 'ze155_rig'):
            continue
        drop = (keep is not None and not o.name.startswith(tuple(keep))) or o.name.startswith(tuple(hide)) \
            or (not ctx and o.users_collection[0].name == 'ze155_context')
        if drop:
            o.hide_render = True; tmp.append(o)
    try:
        return render(cam, path, engine=engine, res=res, transparent=False, samples=24)
    finally:
        for o in tmp:
            o.hide_render = False
        bc.hide_render = bst
Z.render_iso = render_iso


# ---------------------------------------------------------------- phase-4a additions (material audit, cabinets, trenches)
MATS.setdefault('chequer', ((0.66, 0.69, 0.71), 0.42, 0.75))   # trench covers; raised-bar bump nodes live on ze_chequer


def fix_mixed(o, apply=False):
    """Stray-material audit: every connected face island of a multi-material mesh should carry one material.
    Mixed islands get the material of identical non-mixed islands (same face count and size) in the same object,
    else the island majority; ties are reported (target None). Returns [(how, counts, target, lo_mm, key)]."""
    from collections import Counter
    bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    seen = set(); isl = []
    for f in bm.faces:
        if f.index in seen: continue
        stack = [f]; seen.add(f.index); comp = []
        while stack:
            a = stack.pop(); comp.append(a)
            for v in a.verts:
                for b in v.link_faces:
                    if b.index not in seen: seen.add(b.index); stack.append(b)
        vs = {v for x in comp for v in x.verts}
        lo = [min(v.co[i] for v in vs) / MM for i in range(3)]; hi = [max(v.co[i] for v in vs) / MM for i in range(3)]
        key = (len(comp), tuple(sorted(round(hi[i] - lo[i]) for i in range(3))))
        isl.append((comp, Counter(x.material_index for x in comp), key, lo))
    sig = {}
    for comp, c, key, lo in isl:
        if len(c) == 1:
            sig.setdefault(key, Counter())[next(iter(c))] += 1
    out = []
    for comp, c, key, lo in isl:
        if len(c) < 2: continue
        if key in sig:
            tgt = sig[key].most_common(1)[0][0]; how = 'similar'
        else:
            mc = c.most_common()
            tgt, how = (mc[0][0], 'majority') if mc[0][1] > mc[1][1] else (None, 'TIE')
        out.append((how, dict(c), tgt, [round(x) for x in lo], key))
        if apply and tgt is not None:
            for f in comp: f.material_index = tgt
    if apply:
        bm.to_mesh(o.data); o.data.update()
    bm.free()
    return out
Z.fix_mixed = fix_mixed


def grille(bm, cx, w, z0, z1, yf, pitch=22, mi_back=0, mi_slat=1, frame=True):
    """louvre grille on a +Y facing panel at Y = yf (mm): dark back plate, frame, horizontal slats."""
    bm_box(bm, cx - w / 2, cx + w / 2, yf - 0.5, yf + 1.0, z0, z1, mi=mi_back)
    if frame:
        for (a, b, c, d) in [(cx - w / 2 - 12, cx - w / 2, z0 - 12, z1 + 12), (cx + w / 2, cx + w / 2 + 12, z0 - 12, z1 + 12),
                             (cx - w / 2, cx + w / 2, z0 - 12, z0), (cx - w / 2, cx + w / 2, z1, z1 + 12)]:
            bm_box(bm, a, b, yf - 0.5, yf + 4, c, d, mi=mi_slat)
    n = int((z1 - z0) / pitch)
    for k in range(n):
        z = z0 + (k + 0.5) * (z1 - z0) / n
        bm_box(bm, cx - w / 2, cx + w / 2, yf + 0.5, yf + 5, z - 3, z + 3, mi=mi_slat)
Z.grille = grille


def cab_row(prefix, x0, nb, bw, yf, depth, h, plinth=100, low=None, up=None, fans=(), lamps=(), handle_z=None, stripe=None, label_bay=0, eyes=True):
    """row of floor-standing cabinets (nb bays bw wide) whose doors face +Y at Y = yf (mm).
    Objects: prefix (carcass + plinth), _doors, _seams (dark gaps), _hw (handles, hinges, grilles, lamps, display, labels, roof fans, eyes).
    low/up = (width, offset, height) of the lower/upper door grilles; fans = [(x, size)] roof fan hoods; stripe = (bay, width) KM blue band."""
    x1 = x0 + nb * bw; yb = yf - depth
    bm = bmesh.new()
    bm_box(bm, x0 + 10, x1 - 10, yb + 10, yf - 25, 0, plinth, mi=1)
    bm_box(bm, x0, x1, yb, yf - 3, plinth, h - 30, mi=0)
    bm_box(bm, x0 - 8, x1 + 8, yb - 8, yf + 6, h - 30, h, mi=0)
    for i in range(nb + 1):
        xx = x0 + i * bw
        bm_box(bm, max(x0, xx - 15), min(x1, xx + 15), yb - 2, yb, plinth, h - 30, mi=0)
    obj(prefix, bm, ['cabinet', 'steel_dark'], bev=3, segs=2)
    bd = bmesh.new(); bs = bmesh.new(); hw = bmesh.new()
    hz = handle_z or (plinth + (h - plinth) * 0.48)
    zl = (h - 36 - up[1] - up[2] - 60) if up else h - 260
    for i in range(nb):
        bx0 = x0 + i * bw; bx1 = bx0 + bw; cx = (bx0 + bx1) / 2
        bm_box(bd, bx0 + 4, bx1 - 4, yf - 3, yf, plinth + 6, h - 36, mi=0)
        bm_box(bs, bx0 + 0.5, bx1 - 0.5, yf - 3.6, yf - 1.2, plinth + 2, h - 32, mi=0)
        bm_box(hw, bx1 - 60, bx1 - 30, yf, yf + 12, hz - 90, hz + 90, mi=0)
        bm_box(hw, bx1 - 56, bx1 - 34, yf + 12, yf + 34, hz - 70, hz + 40, mi=0)
        bm_cyl(hw, 7, 0, 6, (bx1 - 45, yf + 12, hz + 65), (0, 1, 0), 12, mi=2)
        for zz in (plinth + 180, (plinth + h) / 2, h - 230):
            bm_cyl(hw, 9, -40, 40, (bx0 + 4, yf + 6, zz), (0, 0, 1), 12, mi=2)
        if low:
            grille(hw, cx, low[0], plinth + low[1], plinth + low[1] + low[2], yf, mi_back=0, mi_slat=1)
        if up:
            grille(hw, cx, up[0], h - 36 - up[1] - up[2], h - 36 - up[1], yf, mi_back=0, mi_slat=1)
        if i in lamps:
            for k, mi in enumerate((3, 4, 5)):
                bm_cyl(hw, 18, 0, 6, (cx - 70 + 70 * k, yf, zl), (0, 1, 0), 16, mi=0)
                bm_cyl(hw, 13, 6, 16, (cx - 70 + 70 * k, yf, zl), (0, 1, 0), 16, mi=mi)
            bm_box(hw, cx - 110, cx + 110, yf, yf + 3, zl - 150, zl - 50, mi=0)
            bm_box(hw, cx - 100, cx + 100, yf + 3, yf + 4, zl - 142, zl - 58, mi=6)
        if i == label_bay:
            bm_box(hw, cx - 90, cx + 90, yf, yf + 1.5, zl - 230, zl - 180, mi=2)
        bm_ext(hw, [(cx - 35, zl - 330), (cx + 35, zl - 330), (cx, zl - 270)], 'Y', yf, yf + 1.2, mi=8)
    if stripe is not None:
        i, w = stripe
        bm_box(hw, x0 + i * bw + 14, x0 + i * bw + 14 + w, yf, yf + 1.5, plinth + 40, h - 60, mi=7)
    for (fx, fw) in fans:
        fy = yf - depth / 2
        bm_box(hw, fx - fw / 2, fx + fw / 2, fy - fw / 2, fy + fw / 2, h, h + 200, mi=1)
        bm_box(hw, fx - fw / 2 - 15, fx + fw / 2 + 15, fy - fw / 2 - 15, fy + fw / 2 + 15, h + 200, h + 225, mi=1)
        for s in (-1, 1):
            yy = fy + s * fw / 2
            for k in range(6):
                z = h + 30 + k * 26
                bm_box(hw, fx - fw / 2 + 25, fx + fw / 2 - 25, yy - 4 if s > 0 else yy - 1, yy + 1 if s > 0 else yy + 4, z, z + 14, mi=0)
        bm_cyl(hw, fw * 0.36, h + 225, h + 232, (fx, fy, 0), (0, 0, 1), 32, mi=0)
        for k in range(4):
            a = math.pi * k / 4
            dd = Vector((math.cos(a), math.sin(a), 0))
            bm_seg(hw, Vector((fx, fy, h + 233)) - dd * fw * 0.36, Vector((fx, fy, h + 233)) + dd * fw * 0.36, 4, 6, mi=2)
    if eyes:
        for (ex, ey) in [(x0 + 60, yf - 60), (x1 - 60, yf - 60), (x0 + 60, yb + 60), (x1 - 60, yb + 60)]:
            bm_eyebolt(hw, (ex, ey, h), (0, 0, 1), d=20, ring_R=26, mi=2)
    obj(prefix + '_doors', bd, ['cabinet'], bev=2, segs=2)
    obj(prefix + '_seams', bs, ['black'], bev=None, smooth_=False, wn=False)
    obj(prefix + '_hw', hw, ['black', 'cabinet', 'steel', 'lamp_green', 'lamp_white', 'red', 'screen', 'km_blue', 'yellow'], bev=1, segs=1)
Z.cab_row = cab_row


def trench(name, x0, x1, y0, y1, along='X', plate=1000, mats=('chequer', 'galv', 'black')):
    """flush floor-trench cover run (mm): chequer plates Z 0-8 on an angle frame Z 0-10, lifting slots, dark joints."""
    bm = bmesh.new()
    L0, L1 = (x0, x1) if along == 'X' else (y0, y1)
    W0, W1 = (y0, y1) if along == 'X' else (x0, x1)
    def B(l0, l1, w0, w1, z0, z1, mi):
        if along == 'X': bm_box(bm, l0, l1, w0, w1, z0, z1, mi=mi)
        else: bm_box(bm, w0, w1, l0, l1, z0, z1, mi=mi)
    B(L0, L1, W0, W0 + 18, 0, 10, 1); B(L0, L1, W1 - 18, W1, 0, 10, 1)
    B(L0, L0 + 18, W0, W1, 0, 10, 1); B(L1 - 18, L1, W0, W1, 0, 10, 1)
    n = max(1, round((L1 - L0 - 36) / plate)); pl = (L1 - L0 - 36) / n
    for k in range(n):
        a = L0 + 18 + k * pl + 2; b = a + pl - 4
        B(a, b, W0 + 20, W1 - 20, 0, 8, 0)
        wm = (W0 + W1) / 2
        for s in (0.25, 0.75):
            lm = a + (b - a) * s
            B(lm - 25, lm + 25, wm - 6, wm + 6, 8, 8.6, 2)
        B(a - 2, a, W0 + 18, W1 - 18, 0, 7, 2); B(b, b + 2, W0 + 18, W1 - 18, 0, 7, 2)
    return obj(name, bm, list(mats), bev=1, segs=1)
Z.trench = trench


# ---------------------------------------------------------------- phase-4b finishing (materials kept after a re-exec, final render helpers)
# Colours toned toward the photos (web-02 / p16): less saturated drive blue, real chrome rolls; polished / stainless
# values that phases 2-4a re-applied by hand are now stored here. sheet_pet / melt_curtain / floor / blue_cast have
# custom node trees in the .blend (transparent + fresnel gloss, floor fade into the world horizon, cast-paint bump);
# Z.mat only touches their Principled node, so a re-exec keeps them.
MATS.update({
    'blue_drive': ((63 / 255, 102 / 255, 158 / 255), 0.42, 0.0),
    'motor': ((59 / 255, 92 / 255, 142 / 255), 0.45, 0.0),
    'km_blue': ((36 / 255, 128 / 255, 184 / 255), 0.4, 0.0),
    'blue_cast': ((63 / 255, 102 / 255, 158 / 255), 0.5, 0.0),
    'chrome': ((0.95, 0.955, 0.96), 0.035, 1.0),
    'polished': (MATS['polished'][0], 0.22, 0.75),
    'stainless': (MATS['stainless'][0], 0.3, 0.7),
    'sheet_pet': ((0.80, 0.90, 0.90), 0.04, 0.0),
    'melt_curtain': ((0.92, 0.62, 0.22), 0.05, 0.0),
    'floor': ((0.52, 0.53, 0.54), 0.36, 0.0),
    'duct_slot': ((0.18, 0.19, 0.2), 0.6, 0.0),
})


def frender(cam, path, res=(2400, 1350), samples=96, transparent=False):
    """final EEVEE render with the scene's light/world/raytracing settings (blockout hidden). Returns seconds."""
    import time
    sc = scn(); bpy.context.window.scene = sc
    sc.camera = bpy.data.objects[cam]
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    set_engine(sc, 'BLENDER_EEVEE')
    sc.render.film_transparent = transparent
    sc.eevee.taa_render_samples = samples
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA' if transparent else 'RGB'
    sc.render.filepath = path
    bpy.data.collections['ze155_blockout'].hide_render = True
    t = time.time(); bpy.ops.render.render(write_still=True, scene=sc.name)
    return round(time.time() - t, 1)
Z.frender = frender


def cmp_render(cam, path, res, keep=None, samples=64):
    """photo-comparison render for tools/final_cmp.py: transparent film, floor hidden, optional keep-prefix isolation."""
    sc = scn(); tmp = []
    fl = bpy.data.objects.get('ctx_floor')
    if fl and not fl.hide_render:
        fl.hide_render = True; tmp.append(fl)
    if keep:
        for o in sc.objects:
            if o.type in ('MESH', 'CURVE') and not o.hide_render and o.users_collection \
                    and o.users_collection[0].name in ('ze155_parts', 'ze155_context') and not o.name.startswith(tuple(keep)):
                o.hide_render = True; tmp.append(o)
    try:
        return frender(cam, path, res=res, samples=samples, transparent=True)
    finally:
        for o in tmp:
            o.hide_render = False
Z.cmp_render = cmp_render


# ---------------------------------------------------------------- phase-4c fixes (model review 01)
# C1: PET web reads as a tinted band, rolls as polished steel (not a mirror). The sheet's Map Range (0.30 -> 0.75) and
# Transparent colour (0.78, 0.86, 0.84) live in the .blend node tree; Z.mat only sets its Principled node.
# I3: dark reflective sight glass (coat 1.0 / 0.02 set on the node in the .blend) and a separate hopper level window.
MATS.update({
    'chrome': ((0.8962, 0.8962, 0.8962), 0.09, 1.0),          # linear 0.78
    'sheet_pet': ((0.7014, 0.8095, 0.7977), 0.10, 0.0),       # linear (0.45, 0.62, 0.60)
    'glass': ((0.1897, 0.2478, 0.2717), 0.02, 0.0),           # linear (0.03, 0.05, 0.06)
    'glass_level': ((0.3492, 0.4366, 0.4614), 0.04, 0.0),     # linear (0.10, 0.16, 0.18)
})


def bm_obox(bm, c, ax, ay, az, sx, sy, sz, mi=0):
    """oriented box appended to bm: centre c (mm), axes ax/ay/az, full sizes sx/sy/sz (mm)."""
    ax, ay, az = Vector(ax).normalized(), Vector(ay).normalized(), Vector(az).normalized()
    M = Matrix(((ax.x * sx * MM, ay.x * sy * MM, az.x * sz * MM, c[0] * MM),
                (ax.y * sx * MM, ay.y * sy * MM, az.y * sz * MM, c[1] * MM),
                (ax.z * sx * MM, ay.z * sy * MM, az.z * sz * MM, c[2] * MM),
                (0, 0, 0, 1)))
    r = bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    return _tag(bm, r['verts'], mi)
Z.bm_obox = bm_obox


def bm_flat_lever(bm, p, d, s, L=120, mi_steel=0, mi_red=1, w=25, t=5):
    """ball-valve handle: steel flat bar w x t (t along the stem s) from the stem top p along d, red grip on the outer end."""
    p, d, s = Vector(p), Vector(d).normalized(), Vector(s).normalized()
    s = (s - d * s.dot(d)).normalized()
    u = d.cross(s).normalized()
    g = min(76.0, 0.62 * L)
    bm_obox(bm, p + d * (L / 2), d, u, s, L + 10, w, t, mi_steel)
    bm_obox(bm, p + d * (L + 3 - g / 2), d, u, s, g, w + 6, t + 7, mi_red)
    bm_obox(bm, p, d, u, s, 34, 34, 8, mi_steel)
Z.bm_flat_lever = bm_flat_lever


def overlaps(names, colls=('ze155_parts', 'ze155_context')):
    """BVH overlap check: for each named object, the visible objects whose evaluated mesh intersects it (name, pairs)."""
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()

    def bvh(o):
        oe = o.evaluated_get(dg); me = oe.to_mesh()
        bm = bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); oe.to_mesh_clear()
        if not bm.verts:
            bm.free(); return None
        lo = [min(v.co[i] for v in bm.verts) for i in range(3)]
        hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
        t = BVHTree.FromBMesh(bm); bm.free()
        return t, lo, hi
    others = [o for o in scn().objects if o.type in ('MESH', 'CURVE') and not o.hide_render and o.users_collection
              and o.users_collection[0].name in colls and o.name != 'ctx_floor']
    cache, out = {}, {}
    for n in names:
        a = bvh(bpy.data.objects[n])
        hits = []
        for o in others:
            if o.name == n or a is None:
                continue
            if o.name not in cache:
                cache[o.name] = bvh(o)
            b = cache[o.name]
            if b is None or any(a[2][i] < b[1][i] or b[2][i] < a[1][i] for i in range(3)):
                continue
            k = len(a[0].overlap(b[0]))
            if k:
                hits.append((o.name, k))
        out[n] = hits
    return out
Z.overlaps = overlaps


def comps(bm):
    """loose parts of a bmesh as lists of verts."""
    seen, res = set(), []
    for v in bm.verts:
        if v in seen:
            continue
        st, c = [v], []
        seen.add(v)
        while st:
            a = st.pop(); c.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b not in seen:
                    seen.add(b); st.append(b)
        res.append(c)
    return res
Z.comps = comps
