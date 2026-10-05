import bpy, bmesh, math, types
from mathutils import Vector, Matrix
G = types.SimpleNamespace()
MM = 0.001
G.MM = MM
OUT = '/Users/manhhaycode/m3d-e2e/gx200-spike/out/'
G.OUT = OUT
G.REF = '/Users/manhhaycode/m3d-e2e/gx200-spike/research/img/work/'

def scn(): return bpy.data.scenes['gx200']
G.scn = scn

def _remove(name):
    o = bpy.data.objects.get(name)
    if o is None: return
    us = list(o.users_scene)
    if us and any(s.name != 'gx200' for s in us):
        raise RuntimeError('object %s belongs to another scene' % name)
    data = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    if data is not None and data.users == 0:
        if isinstance(data, bpy.types.Mesh): bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Camera): bpy.data.cameras.remove(data)
        elif isinstance(data, bpy.types.Light): bpy.data.lights.remove(data)
        elif isinstance(data, bpy.types.Curve): bpy.data.curves.remove(data)
G.remove = _remove

def link(o, coll='gx200_parts'):
    bpy.data.collections[coll].objects.link(o); return o
G.link = link

def obj_from_bm(name, bm, mat=None, smooth=False, coll='gx200_parts'):
    _remove(name)
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me); bm.free()
    if smooth:
        me.shade_smooth()
    o = bpy.data.objects.new(name, me)
    link(o, coll)
    if mat is not None:
        me.materials.append(G.mat(mat) if isinstance(mat, str) else mat)
    return o
G.obj_from_bm = obj_from_bm

# --- materials (Principled, find by type)
MATS = {
 'alu':      ((0.70,0.70,0.68), 0.55, 0.85),
 'red':      ((0.80,0.06,0.09), 0.32, 0.0),
 'white':    ((0.93,0.92,0.88), 0.35, 0.0),
 'black_plastic': ((0.035,0.037,0.042), 0.5, 0.0),
 'black_paint':   ((0.025,0.025,0.027), 0.45, 0.2),
 'steel':    ((0.75,0.75,0.75), 0.25, 1.0),
 'chrome':   ((0.92,0.92,0.93), 0.08, 1.0),
 'rubber':   ((0.02,0.02,0.02), 0.7, 0.0),
 'zinc':     ((0.80,0.78,0.70), 0.35, 1.0),
 'logo_black': ((0.02,0.02,0.022), 0.4, 0.0),
}
def srgb2lin(c):
    return tuple(((x+0.055)/1.055)**2.4 if x > 0.04045 else x/12.92 for x in c)
def mat(name):
    mname = 'gx_' + name
    m = bpy.data.materials.get(mname)
    if m is None:
        m = bpy.data.materials.new(mname)
    col, rough, metal = MATS[name]
    try: m.use_nodes = True
    except Exception: pass
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    lc = srgb2lin(col)
    bsdf.inputs['Base Color'].default_value = (*lc, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*lc, 1)
    return m
G.mat = mat; G.MATS = MATS; G.srgb2lin = srgb2lin

# --- modifiers
def bevel(o, w_mm, segs=2, angle=40, harden=False, name='Bevel'):
    m = o.modifiers.new(name, 'BEVEL')
    m.width = w_mm*MM; m.segments = segs
    m.limit_method = 'ANGLE'; m.angle_limit = math.radians(angle)
    m.use_clamp_overlap = True
    m.harden_normals = harden
    return m
def wnormal(o):
    m = o.modifiers.new('WNormal', 'WEIGHTED_NORMAL'); m.keep_sharp = True; return m
def solidify(o, t_mm, offset=-1):
    m = o.modifiers.new('Solidify', 'SOLIDIFY'); m.thickness = t_mm*MM; m.offset = offset; return m
def smooth(o, on=True):
    if on: o.data.shade_smooth()
    else: o.data.shade_flat()
G.bevel = bevel; G.wnormal = wnormal; G.solidify = solidify; G.smooth = smooth

def hard(o, w_mm, segs=2, angle=40):
    """bevel + smooth + weighted normals (hard-surface cast look)"""
    smooth(o); bevel(o, w_mm, segs, angle, harden=False); wnormal(o)
G.hard = hard

# --- primitives in mm
def box_bm(x0,x1,y0,y1,z0,z1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (x0 if v.co.x < 0 else x1)*MM
        v.co.y = (y0 if v.co.y < 0 else y1)*MM
        v.co.z = (z0 if v.co.z < 0 else z1)*MM
    return bm
G.box_bm = box_bm
def box(name, x0,x1,y0,y1,z0,z1, mat=None, bev=None, segs=2):
    o = obj_from_bm(name, box_bm(x0,x1,y0,y1,z0,z1), mat)
    if bev: hard(o, bev, segs)
    return o
G.box = box

def _plane_map(axis):
    # returns function (u,v,d)->Vector in mm
    if axis == 'X': return lambda u,v,d: Vector((d,u,v))
    if axis == 'Y': return lambda u,v,d: Vector((u,d,v))
    return lambda u,v,d: Vector((u,v,d))
def extrude_bm(pts, axis, d0, d1):
    f = _plane_map(axis)
    bm = bmesh.new()
    vs = [bm.verts.new(f(u,v,d0)*MM) for (u,v) in pts]
    face = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    nv = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
    dv = f(0,0,d1-d0)*MM
    bmesh.ops.translate(bm, vec=dv, verts=nv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
G.extrude_bm = extrude_bm
def extrude(name, pts, axis, d0, d1, mat=None, bev=None, segs=2, angle=40):
    o = obj_from_bm(name, extrude_bm(pts, axis, d0, d1), mat)
    if bev: hard(o, bev, segs, angle)
    return o
G.extrude = extrude

def revolve_bm(prof, segs=48, close_caps=False):
    """prof: list of (r, h) mm, revolved around local Z. returns bm"""
    bm = bmesh.new()
    vs = [bm.verts.new(Vector((r*MM, 0, h*MM))) for (r,h) in prof]
    es = [bm.edges.new((vs[i], vs[i+1])) for i in range(len(vs)-1)]
    bmesh.ops.spin(bm, geom=vs+es, cent=(0,0,0), axis=(0,0,1), angle=math.radians(360), steps=segs, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
G.revolve_bm = revolve_bm
def axis_matrix(origin_mm, axis):
    a = Vector(axis).normalized()
    q = Vector((0,0,1)).rotation_difference(a)
    return Matrix.Translation(Vector(origin_mm)*MM) @ q.to_matrix().to_4x4()
G.axis_matrix = axis_matrix
def revolve(name, prof, origin, axis=(0,0,1), segs=48, mat=None, smooth_=True):
    bm = revolve_bm(prof, segs)
    bm.transform(axis_matrix(origin, axis))
    o = obj_from_bm(name, bm, mat, smooth=smooth_)
    return o
G.revolve = revolve

def rrect(cx, cy, w, h, r, n=6):
    """rounded rectangle points (mm) centred at cx,cy"""
    pts = []
    r = min(r, w/2-1e-3, h/2-1e-3)
    for (qx,qy,a0) in [(cx+w/2-r, cy+h/2-r, 0),(cx-w/2+r, cy+h/2-r, 90),(cx-w/2+r, cy-h/2+r, 180),(cx+w/2-r, cy-h/2+r, 270)]:
        for i in range(n+1):
            a = math.radians(a0 + 90*i/n)
            pts.append((qx + r*math.cos(a), qy + r*math.sin(a)))
    return pts
G.rrect = rrect

def boolean(o, cutter, op='DIFFERENCE', apply=False, solver='EXACT'):
    m = o.modifiers.new('Bool_'+cutter.name, 'BOOLEAN')
    m.operation = op; m.object = cutter
    try: m.solver = solver
    except Exception: pass
    cutter.display_type = 'WIRE'; cutter.hide_render = True
    cutter.hide_set(True, view_layer=scn().view_layers[0])
    return m
G.boolean = boolean

def apply_mods(o, keep_last=0):
    """apply all modifiers via evaluated mesh (no ops)"""
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(oe)
    old = o.data
    o.modifiers.clear()
    o.data = me
    me.name = o.name
    if old.users == 0: bpy.data.meshes.remove(old)
G.apply_mods = apply_mods

bpy.app.driver_namespace['gx'] = G
print('helpers ok', len(vars(G)))

