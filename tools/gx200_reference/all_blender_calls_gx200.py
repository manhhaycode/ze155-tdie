
# ===== call 1 2026-10-04T10:35:27.567Z =====
import bpy, sys
print(bpy.app.version_string, bpy.data.filepath, [s.name for s in bpy.data.scenes])
print([o.name for o in bpy.data.objects])
print([m.name for m in bpy.data.materials])
print(bpy.context.window.scene.name if bpy.context.window else None)
print([a.type for a in bpy.context.screen.areas])


# ===== call 2 2026-10-04T10:39:51.073Z =====
import bpy
if 'gx200' not in bpy.data.scenes:
    sc = bpy.data.scenes.new('gx200')
else:
    sc = bpy.data.scenes['gx200']
sc.unit_settings.system = 'METRIC'
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.unit_settings.scale_length = 1.0
if 'gx200_parts' not in bpy.data.collections:
    c = bpy.data.collections.new('gx200_parts'); sc.collection.children.link(c)
if 'gx200_rig' not in bpy.data.collections:
    c = bpy.data.collections.new('gx200_rig'); sc.collection.children.link(c)
bpy.context.window.scene = sc
print([s.name for s in bpy.data.scenes], bpy.context.window.scene.name)
print([i.identifier for i in sc.render.bl_rna.properties['engine'].enum_items], sc.render.engine)


# ===== call 3 2026-10-04T10:40:23.563Z =====
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


# ===== call 4 2026-10-04T10:40:35.667Z =====
import bpy, math
from mathutils import Vector, Euler
G = bpy.app.driver_namespace['gx']; MM = G.MM

# view definitions: rotation, image, size, px/mm, image-centre world coords (mm)
def px2w_02a(px,py): return (None, -65 - (px-550)/1.415, (618-py)/1.434)
def px2w_02b(px,py): return (None, -188 + (px-148)/1.423, (617-py)/1.425)
def px2w_02c(px,py): return (156.5 - (px-220)/1.406, None, (619-py)/1.419)
def px2w_02d(px,py): return (156.5 - (px-57)/1.423, -188 + (py-207)/1.423, None)
VIEWS = {
 '02a': dict(rot=(90,0,-90), W=940, H=650, s=(1.415+1.434)/2, conv=px2w_02a, pos_axis=0, pos=-1500),
 '02b': dict(rot=(90,0,90),  W=840, H=730, s=1.424, conv=px2w_02b, pos_axis=0, pos=1500),
 '02c': dict(rot=(90,0,180), W=810, H=710, s=(1.406+1.419)/2, conv=px2w_02c, pos_axis=1, pos=1500),
 '02d': dict(rot=(0,0,180),  W=610, H=900, s=1.423, conv=px2w_02d, pos_axis=2, pos=1500),
}
G.VIEWS = VIEWS
def make_ortho_cam(key):
    v = VIEWS[key]
    name = 'cam_' + key
    G.remove(name)
    cd = bpy.data.cameras.new(name)
    cd.type = 'ORTHO'
    cd.ortho_scale = max(v['W'], v['H'])/v['s']*MM
    cd.clip_start = 0.01; cd.clip_end = 5.0
    cam = bpy.data.objects.new(name, cd)
    G.link(cam, 'gx200_rig')
    cam.rotation_euler = Euler([math.radians(a) for a in v['rot']])
    c = list(v['conv'](v['W']/2, v['H']/2))
    c[v['pos_axis']] = v['pos']
    cam.location = Vector(c)*MM
    img = bpy.data.images.load(G.REF + 'ref-images-%s.png' % key, check_existing=True)
    cd.show_background_images = True
    cd.background_images.clear()
    bg = cd.background_images.new()
    bg.image = img; bg.alpha = 0.5; bg.display_depth = 'FRONT'; bg.frame_method = 'FIT'
    cd.sensor_fit = 'AUTO'
    return cam
for k in VIEWS: make_ortho_cam(k)
G.make_ortho_cam = make_ortho_cam
print([ (o.name, tuple(round(x,4) for x in o.location), round(o.data.ortho_scale,4)) for o in bpy.data.collections['gx200_rig'].objects])


# ===== call 5 2026-10-04T10:40:45.006Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
def view3d():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                reg = next(r for r in area.regions if r.type == 'WINDOW')
                return win, area, reg
G.view3d = view3d
def look(cam_name, shading='SOLID', bg_alpha=None, res=None):
    sc = G.scn()
    cam = bpy.data.objects[cam_name]
    sc.camera = cam
    if res: sc.render.resolution_x, sc.render.resolution_y = res
    elif cam_name[4:] in G.VIEWS:
        v = G.VIEWS[cam_name[4:]]; sc.render.resolution_x, sc.render.resolution_y = v['W'], v['H']
    sc.render.resolution_percentage = 100
    if bg_alpha is not None and cam.data.background_images:
        cam.data.background_images[0].alpha = bg_alpha
    win, area, reg = view3d()
    sp = area.spaces.active
    sp.region_3d.view_perspective = 'CAMERA'
    sp.shading.type = shading
    sp.overlay.show_overlays = True
    sp.overlay.show_floor = False; sp.overlay.show_axis_x = False; sp.overlay.show_axis_y = False
    sp.overlay.show_extras = False
    sp.overlay.show_relationship_lines = False
    with bpy.context.temp_override(window=win, area=area, region=reg):
        bpy.ops.view3d.view_center_camera()
    return area
G.look = look
win, area, reg = view3d()
print(area.width, area.height, win.scene.name)
look('cam_02c')


# ===== call 6 2026-10-04T10:40:58.911Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
if 'gx200_blockout' not in bpy.data.collections:
    c = bpy.data.collections.new('gx200_blockout'); G.scn().collection.children.link(c)
def B(name, *a, mat='alu'):
    o = G.obj_from_bm(name, G.box_bm(*a), mat, coll='gx200_blockout'); return o
B('blk_crankcase', -110,103, -158,50, 21,195)
B('blk_base', -43,103, -156,54, 0,21)
B('blk_shroud', -150,-110, -172,70, 5,204, mat='red')
B('blk_tank', -128,110, -188,28, 200,327, mat='white')
B('blk_aircleaner', -134,-26, 42,177, 222,323, mat='black_plastic')
B('blk_ac_case', -128,-70, 112,172, 124,222, mat='black_plastic')
B('blk_muffler', 21,134, 44,188, 238,328, mat='black_paint')
o = G.revolve('blk_recoil', [(0,0),(90,0),(90,6.5),(0,6.5)], (-156.5,-65,106), (1,0,0), 48, 'red'); G.scn().collection.children['gx200_blockout'].objects.link(o); bpy.data.collections['gx200_parts'].objects.unlink(o)
o = G.revolve('blk_shaft', [(0,0),(10,0),(10,53.2),(0,53.2)], (103.3,-65,106), (1,0,0), 32, 'steel'); bpy.data.collections['gx200_blockout'].objects.link(o); bpy.data.collections['gx200_parts'].objects.unlink(o)
o = G.revolve('blk_cap', [(0,0),(38,0),(38,24),(0,24)], (-9,-76,322), (0,0,1), 32, 'chrome'); bpy.data.collections['gx200_blockout'].objects.link(o); bpy.data.collections['gx200_parts'].objects.unlink(o)
o = G.revolve('blk_ac_knob', [(0,0),(22,0),(22,16),(0,16)], (-80,110,323), (0,0,1), 32, 'black_plastic'); bpy.data.collections['gx200_blockout'].objects.link(o); bpy.data.collections['gx200_parts'].objects.unlink(o)
# inclined cylinder block: box along axis at 25deg in plane X=28
import bmesh
from mathutils import Matrix, Vector
bm = G.box_bm(-58,58, -55,55, 40,175)   # local: x=X, y=perp, z=along axis
bm.transform(Matrix.Translation(Vector((28,-65,106))*G.MM) @ Matrix.Rotation(math.radians(-65), 4, 'X'))
o = G.obj_from_bm('blk_cylinder', bm, 'alu', coll='gx200_blockout')
print([o.name for o in bpy.data.collections['gx200_blockout'].objects])


# ===== call 7 2026-10-04T10:41:16.596Z =====
import bpy, math, os
G = bpy.app.driver_namespace['gx']
def set_engine(sc, eng):
    try:
        sc.render.engine = eng
    except TypeError as e:
        print('engine err', e)
G.set_engine = set_engine
def render(cam_name, path, engine='BLENDER_WORKBENCH', res=None, transparent=True, samples=16):
    sc = G.scn()
    cam = bpy.data.objects[cam_name]
    sc.camera = cam
    if res: sc.render.resolution_x, sc.render.resolution_y = res
    elif cam_name[4:] in G.VIEWS:
        v = G.VIEWS[cam_name[4:]]; sc.render.resolution_x, sc.render.resolution_y = v['W'], v['H']
    sc.render.resolution_percentage = 100
    set_engine(sc, engine)
    sc.render.film_transparent = transparent
    if engine == 'BLENDER_WORKBENCH':
        sh = sc.display.shading
        sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
        sh.show_cavity = True; sh.cavity_type = 'BOTH'
        sh.show_object_outline = True
        sh.show_specular_highlight = True
        sc.display.render_aa = '8'
    else:
        try: sc.eevee.taa_render_samples = samples
        except Exception: pass
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.filepath = path
    # hide blockout or parts per caller (handled outside)
    bpy.ops.render.render(write_still=True, scene=sc.name)
    return path
G.render = render
print([i.identifier for i in G.scn().display.bl_rna.properties['render_aa'].enum_items])


# ===== call 8 2026-10-04T10:41:20.529Z =====
import bpy, time
G = bpy.app.driver_namespace['gx']
t=time.time()
for k in ['02a','02b','02c','02d']:
    G.render('cam_'+k, G.OUT+'look/blockout-%s-r1.png'%k)
print('done', time.time()-t)


# ===== call 9 2026-10-04T10:44:59.585Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 106.0   # crank axis
# hide blockout
for o in bpy.data.collections['gx200_blockout'].objects:
    o.hide_set(True, view_layer=G.scn().view_layers[0]); o.hide_render = True

# --- crankcase main body (YZ profile from 02b, extruded along X)
P = [(-120,8),(28,8),(42,18),(47,45),(48,100),(42,140),(25,175),(5,196),(-10,201),(-128,201),(-146,193),(-152,178),(-152,48),(-146,28),(-134,14)]
cc = G.extrude('part_crankcase', P, 'X', -112, 99, 'alu')
G.smooth(cc); G.bevel(cc, 5, 3, 35); G.wnormal(cc)

# --- PTO side cover flange lip (slightly proud ring around the face) 
P2 = [(y*0.97+CY*0.03, z*0.97+CZ*0.03) for (y,z) in P]
lip = G.extrude('part_crankcase_cover', P2, 'X', 96, 100.5, 'alu')
G.smooth(lip); G.bevel(lip, 2.0, 2, 35); G.wnormal(lip)

# --- ATT. FACE pad (rounded square 93 x 90) + tapped holes
pad = G.extrude('part_att_face', G.rrect(CY, CZ, 93, 90, 14, 6), 'X', 99, 103.3, 'alu')
cut = G.obj_from_bm('cut_att_holes', bmesh.new(), None, coll='gx200_rig')
bm = bmesh.new()
for dy in (-32.5, 32.5):
    for dz in (-33, 33):
        b2 = G.revolve_bm([(0,-1),(3.4,-1),(3.4,10),(0,10)], 16)
        b2.transform(G.axis_matrix((95, CY+dy, CZ+dz), (1,0,0)))
        me = bpy.data.meshes.new('tmp'); b2.to_mesh(me); b2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
# bore recess for oil seal
b2 = G.revolve_bm([(0,-1),(19,-1),(19,6),(0,6)], 48); b2.transform(G.axis_matrix((101.3, CY, CZ), (1,0,0)))
me = bpy.data.meshes.new('tmp'); b2.to_mesh(me); b2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
bm.to_mesh(cut.data); bm.free()
G.boolean(pad, cut); G.apply_mods(pad)
G.smooth(pad); G.bevel(pad, 1.2, 2, 35); G.wnormal(pad)
# raised ring on the boss (concentric lines in 02b)
ring = G.revolve('part_bearing_boss', [(19,101.3-101.3),(26,0),(26,2.2),(25,2.6),(20,2.6),(19,2.0)], (101.3,CY,CZ), (1,0,0), 64, 'alu')
# oil seal (black rubber)
seal = G.revolve('part_oil_seal', [(10.2,0),(18.9,0),(18.9,0.5),(17,1.2),(11,1.2),(10.2,0.8)], (101.5,CY,CZ), (1,0,0), 48, 'rubber')
print('ok')


# ===== call 10 2026-10-04T10:45:17.098Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 106.0
bpy.data.objects['part_bearing_boss'].location.x = -0.6*MM
def merge_bms(bms):
    out = bmesh.new()
    for b in bms:
        me = bpy.data.meshes.new('tmp'); b.to_mesh(me); b.free(); out.from_mesh(me); bpy.data.meshes.remove(me)
    return out
G.merge_bms = merge_bms
# --- mounting feet: two rails along X, holes / slots
rails = []
for (y0,y1) in [(-156,-104),(4,54)]:
    b = G.extrude_bm(G.rrect((-40+101)/2, (y0+y1)/2, 141, y1-y0, 8, 4), 'Z', 0, 12)
    rails.append(b)
# webs joining rails up into crankcase walls
rails.append(G.extrude_bm([(-150,0),(-104,0),(-118,30),(-150,40)], 'X', -36, 97))
rails.append(G.extrude_bm([(4,0),(54,0),(46,40),(20,30)], 'X', -36, 97))
feet = G.obj_from_bm('part_base_feet', merge_bms(rails), 'alu')
# holes: round on -Y rail, slots 9x14 (along Y) on +Y rail
cut = []
for x in (67.3, -12.7):
    b = G.revolve_bm([(0,-2),(4.5,-2),(4.5,30),(0,30)], 20); b.transform(G.axis_matrix((x,-131,-1),(0,0,1))); cut.append(b)
    cut.append(G.extrude_bm(G.rrect(x, 31, 9, 14, 4.4, 4), 'Z', -2, 30))
# spot-face counterbores on top of the feet
cobj = G.obj_from_bm('cut_feet', merge_bms(cut), None, coll='gx200_rig')
G.boolean(feet, cobj); G.apply_mods(feet)
G.smooth(feet); G.bevel(feet, 2.0, 2, 35); G.wnormal(feet)

# --- output shaft (S type) Ø20, 53.2 from ATT face, keyway 5 wide x 3 deep, M8 centre hole
prof = [(0,0),(12.5,0),(12.5,3.0),(11.0,3.6),(10,4.2),(10,52.2),(9.0,53.2),(0,53.2)]
sh = G.revolve('part_output_shaft', [(r, h) for (r,h) in prof], (103.3-3,CY,CZ), (1,0,0), 64, 'steel')
kw = G.obj_from_bm('cut_keyway', G.box_bm(121.5, 160, CY-2.5, CY+2.5, CZ+7, CZ+15), None, coll='gx200_rig')
b = G.revolve_bm([(0,-20),(3.4,-20),(3.4,1),(0,1)], 20); b.transform(G.axis_matrix((156.5,CY,CZ),(1,0,0)))
hole = G.obj_from_bm('cut_shaft_hole', b, None, coll='gx200_rig')
G.boolean(sh, kw); G.boolean(sh, hole); G.apply_mods(sh)
sh.data.shade_smooth()
m = sh.modifiers.new('Smooth', 'WEIGHTED_NORMAL'); m.keep_sharp=True
# set sharp edges by angle for the shaft so keyway stays crisp
bm = bmesh.new(); bm.from_mesh(sh.data)
for e in bm.edges:
    if len(e.link_faces)==2 and e.calc_face_angle(0) > math.radians(35): e.smooth = False
bm.to_mesh(sh.data); bm.free()
print('ok', len(sh.data.polygons))


# ===== call 11 2026-10-04T10:47:20.713Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 106.0
TILT = 25.0
# cylinder frame: local x = X, local z = cylinder axis a, local -y = p (up side)
MC = Matrix.Translation(Vector((28, CY, CZ))*MM) @ Matrix.Rotation(math.radians(-(90-TILT)), 4, 'X')
G.MC = MC
def L(u, p, w): return Vector((u, -p, w))*MM   # local coords for cylinder-frame meshes
G.Lc = L
def cyl_obj(name, bm, mat, coll='gx200_parts'):
    o = G.obj_from_bm(name, bm, mat, coll=coll); o.matrix_world = MC; return o
G.cyl_obj = cyl_obj
def plate_bm(pts_up, w0, w1):
    """pts in (u,p) -> extruded along local z from w0 to w1 (mm)"""
    bm = bmesh.new()
    vs = [bm.verts.new(L(u,p,w0)) for (u,p) in pts_up]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=Vector((0,0,(w1-w0)*MM)), verts=[e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
G.plate_bm = plate_bm

# barrel core (round-ish), from inside crankcase to head
core = cyl_obj('part_cylinder', plate_bm(G.rrect(0, -2, 92, 96, 30, 6), 30, 150), 'alu')
G.smooth(core); G.bevel(core, 3, 2, 35); G.wnormal(core)
# fins: one plate + Array along local z
fin_pts = G.rrect(0, 0, 124, 146, 16, 6)
fins = cyl_obj('part_cylinder_fins', plate_bm(fin_pts, 62, 64.4), 'alu')
arr = fins.modifiers.new('Array', 'ARRAY'); arr.use_relative_offset = False; arr.use_constant_offset = True
arr.constant_offset_displace = (0, 0, 8.6*MM); arr.count = 9
G.smooth(fins); G.bevel(fins, 0.9, 1, 35); G.wnormal(fins)
# head block (fins on head too) w 140..205, offset to lower side
head = cyl_obj('part_cylinder_head', plate_bm(G.rrect(0, -22, 118, 120, 18, 6), 138, 206), 'alu')
G.smooth(head); G.bevel(head, 3, 2, 35); G.wnormal(head)
hf = cyl_obj('part_head_fins', plate_bm(G.rrect(0, -18, 126, 136, 16, 6), 150, 152.2), 'alu')
arr = hf.modifiers.new('Array', 'ARRAY'); arr.use_relative_offset=False; arr.use_constant_offset=True
arr.constant_offset_displace=(0,0,9.0*MM); arr.count = 5
G.smooth(hf); G.bevel(hf, 0.8, 1, 35); G.wnormal(hf)
print('ok')


# ===== call 12 2026-10-04T10:47:41.095Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
L = G.Lc; MC = G.MC
PC = -33.0
fl = G.cyl_obj('part_head_cover', G.merge_bms([
        G.plate_bm(G.rrect(0, PC, 104, 96, 14, 6), 204, 209),
        G.plate_bm(G.rrect(0, PC, 86, 88, 12, 6), 208, 220.5)]), 'black_paint')
G.smooth(fl); G.bevel(fl, 3.5, 3, 30); G.wnormal(fl)
# bolt bosses + flange bolts
bms = []
for u in (-38, 38):
    for p in (PC-39.5, PC+39.5):
        b = G.revolve_bm([(0,0),(7.5,0),(7.5,13),(6.5,14),(0,14)], 24)
        b.transform(Matrix.Translation(L(u,p,207)))
        bms.append(b)
bo = G.cyl_obj('part_head_cover_bosses', G.merge_bms(bms), 'black_paint'); G.smooth(bo)
bms = []
for u in (-38, 38):
    for p in (PC-39.5, PC+39.5):
        b = G.revolve_bm([(0,0),(7,0),(7,1.2),(0,1.2)], 24); b.transform(Matrix.Translation(L(u,p,221)))
        bms.append(b)
        h = G.revolve_bm([(0,0),(5.8,0),(5.8,5),(5.0,5.6),(0,5.6)], 6); h.transform(Matrix.Translation(L(u,p,222.2)))
        bms.append(h)
bh = G.cyl_obj('part_head_cover_bolts', G.merge_bms(bms), 'zinc')
bh.data.shade_flat()
# OHV letters (text -> mesh), on the cover face
G.remove('txt_ohv')
cu = bpy.data.curves.get('txt_ohv') or bpy.data.curves.new('txt_ohv', 'FONT')
cu.body = 'OHV'; cu.size = 22*MM; cu.extrude = 0.9*MM; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
cu.space_character = 1.15
t = bpy.data.objects.new('txt_ohv', cu); G.link(t, 'gx200_rig')
# letters lie in local XY of text -> map to cover face: text x -> u (but mirrored for view from +Y?), text y -> p
# cover face normal = local +z of MC; viewer looks from outside (+a). text normal is +z -> fine.
t.matrix_world = MC @ Matrix.Translation(L(0, PC+2, 220.6)) @ Matrix.Rotation(math.radians(180), 4, 'Z')
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(t.evaluated_get(dg))
G.remove('part_ohv_letters')
o = bpy.data.objects.new('part_ohv_letters', me); G.link(o)
o.matrix_world = t.matrix_world.copy()
me.materials.append(G.mat('black_paint'))
bpy.data.objects.remove(t); bpy.data.curves.remove(cu)
print('ok', len(me.polygons))


# ===== call 13 2026-10-04T10:47:48.547Z =====
import bpy
G = bpy.app.driver_namespace['gx']
for k in ['02b','02c','02a','02d']:
    G.render('cam_'+k, G.OUT+'look/crankcase_cyl-%s-r1.png'%k)
print('ok')


# ===== call 14 2026-10-04T10:48:14.661Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
fins = bpy.data.objects['part_cylinder_fins']
bm = G.plate_bm(G.rrect(0, 8.5, 124, 133, 16, 6), 62, 64.4)
bm.to_mesh(fins.data); bm.free(); fins.data.shade_smooth()
# delete applied cutters to keep scene tidy
for n in ['cut_att_holes','cut_feet','cut_keyway','cut_shaft_hole']:
    G.remove(n)
print([o.name for o in bpy.data.collections['gx200_rig'].objects])


# ===== call 15 2026-10-04T10:49:07.224Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 105.5
OUTL = [(-173,32),(-173,186),(-168,200),(-158,206),(62,206),(80,202),(91,192),(97,162),(97,118),(92,92),(80,68),(62,46),(42,28),(22,18),(0,14),(-150,14),(-164,18),(-171,25)]
X0, X1 = -149.5, -103.0
bm = G.extrude_bm(OUTL, 'X', X0, X1)
# remove the +X cap face (open shell towards the crankcase)
cap = [f for f in bm.faces if f.normal.x > 0.9]
bmesh.ops.delete(bm, geom=cap, context='FACES_ONLY')
sh = G.obj_from_bm('part_fan_shroud', bm, 'red')
G.smooth(sh)
b = G.bevel(sh, 9, 4, 30); 
s = G.solidify(sh, 1.6, -1); s.use_even_offset = True
G.wnormal(sh)
# inner dark fan visible through slots
fan = G.revolve('part_flywheel_fan', [(0,0),(88,0),(88,30),(0,30)], (-147,CY,CZ), (-1,0,0), 48, 'black_paint')
fan.location.x = 0
# --- side vent slots on the +Y wall (02c x 610..650): boolean, applied
cuts = []
for zc in (170, 140, 112):
    for xc in (-138, -127, -116):
        cuts.append(G.extrude_bm(G.rrect(xc, zc, 6, 22, 2.9, 3), 'Y', 60, 120))
for zc in (60, 36):
    for xc in (-138, -127, -116):
        cuts.append(G.extrude_bm(G.rrect(xc, zc, 6, 18, 2.9, 3), 'Y', 30, 120))
cobj = G.obj_from_bm('cut_shroud_slots', G.merge_bms(cuts), None, coll='gx200_rig')
G.boolean(sh, cobj)
print([m.name for m in sh.modifiers])


# ===== call 16 2026-10-04T10:49:24.067Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 105.5
sh = bpy.data.objects['part_fan_shroud']
sh.modifiers.move(3, 2)
# --- recoil starter cover: pressed dome, profile (r, h) h outward (-X) from shroud face
XF = -149.0
prof = [(0,7.5),(36,7.5),(37,7.3),(78,7.3),(84,6.8),(89,5.6),(93,3.4),(95.5,1.0),(96,0),(94,0)]
# build as surface then solidify
rc = G.revolve('part_recoil_starter', prof, (XF,CY,CZ), (-1,0,0), 96, 'red')
G.solidify(rc, 1.4, -1)
# slots: inner ring 24 (r 41..57), outer ring 36 (r 61..77)
cuts = []
def slot_bm(r0, r1, ang, w):
    pts = G.rrect((r0+r1)/2, 0, r1-r0, w, w/2-0.05, 4)
    b = G.extrude_bm(pts, 'Z', -5, 20)
    rot = Matrix.Rotation(ang, 4, 'Z')
    b.transform(rot)
    return b
for i in range(24):
    cuts.append(slot_bm(41, 57, 2*math.pi*(i+0.5)/24, 4.6))
for i in range(36):
    cuts.append(slot_bm(61, 77.5, 2*math.pi*i/36, 4.4))
cb = G.merge_bms(cuts)
cb.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
cobj = G.obj_from_bm('cut_recoil_slots', cb, None, coll='gx200_rig')
G.boolean(rc, cobj)
G.smooth(rc); wn = G.wnormal(rc)
# centre logo disc (black), slightly proud
G.revolve('part_recoil_logo_disc', [(0,9.6),(33,9.6),(35,8.8),(36,7.0),(30,6.0),(0,6.0)], (XF,CY,CZ), (-1,0,0), 64, 'logo_black')
# 6 screws at r=82 (30 + 60k deg)
bms = []
for k in range(6):
    a = math.radians(30 + 60*k)
    y = CY + 82*math.cos(a); z = CZ + 82*math.sin(a)
    # in view from -X, +Y is to the left; angle measured in Y-Z plane is fine (symmetric set)
    b = G.revolve_bm([(0,0),(5.5,0),(5.5,1.0),(4.8,3.0),(2.5,3.6),(0,3.6)], 20)
    b.transform(G.axis_matrix((XF-6.6, y, z), (-1,0,0)))
    bms.append(b)
scr = G.obj_from_bm('part_recoil_screws', G.merge_bms(bms), 'zinc', smooth=True)
print('ok')


# ===== call 17 2026-10-04T10:49:42.363Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 105.5
XF = -149.0
G.revolve('part_recoil_logo_disc', [(0,7.9),(33,7.9),(34.5,7.5),(35.5,6.6),(30,6.0),(0,6.0)], (XF,CY,CZ), (-1,0,0), 64, 'logo_black')
bms = []
for k in range(6):
    a = math.radians(30 + 60*k)
    y = CY + 82*math.cos(a); z = CZ + 82*math.sin(a)
    b = G.revolve_bm([(0,0),(5.5,0),(5.5,0.8),(4.6,2.0),(2.5,2.5),(0,2.5)], 20)
    b.transform(G.axis_matrix((XF-5.8, y, z), (-1,0,0)))
    bms.append(b)
G.obj_from_bm('part_recoil_screws', G.merge_bms(bms), 'zinc', smooth=True)

# --- recoil handle: T-grip lying in a plane parallel to YZ, X ~ -168
# grip bar axis from (Y 66, Z 117) to (Y 16, Z 166) (02a: crop->orig), rope guide at (Y 13, Z 117)
XG = -167.0
p0 = Vector((XG, 64, 118)); p1 = Vector((XG, 16, 165))
d = (p1 - p0); Lg = d.length; d.normalize()
# grip: revolve a fat capsule profile along its axis then flatten
prof = [(0,0),(6,0.4),(9.5,2.5),(11.5,6),(12,10),(11.2,Lg*0.5),(12,Lg-10),(11.5,Lg-6),(9.5,Lg-2.5),(6,Lg-0.4),(0,Lg)]
b = G.revolve_bm(prof, 28)
# flatten in local x (becomes world X thickness)
for v in b.verts: v.co.x *= 0.62
b.transform(G.axis_matrix(tuple(p0), tuple(d)))
grip = G.obj_from_bm('part_recoil_handle', b, 'black_plastic', smooth=True)
# stem from grip middle to rope guide at shroud face
gm = (p0 + p1)/2
q0 = gm + Vector((0,-6,-6)); q1 = Vector((-152.5, 18, 120))
dv = q1 - q0; Ls = dv.length
b = G.revolve_bm([(0,0),(7.5,0),(7.0,Ls*0.5),(5.5,Ls),(0,Ls)], 20)
b.transform(G.axis_matrix(tuple(q0), tuple(dv.normalized())))
G.obj_from_bm('part_recoil_handle_stem', b, 'black_plastic', smooth=True)
# rope guide grommet on shroud face
G.revolve('part_rope_guide', [(3,0),(9,0),(9,3.5),(7,5),(3,5)], (XF-0.5, 18, 120), (-1,0,0), 24, 'zinc')
print('ok', Lg, Ls)


# ===== call 18 2026-10-04T10:49:50.014Z =====
import bpy
G = bpy.app.driver_namespace['gx']
for k in ['02a','02c','02d','02b']:
    G.render('cam_'+k, G.OUT+'look/shroud_recoil-%s-r1.png'%k)
print('ok')


# ===== call 19 2026-10-04T10:51:26.070Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
# fix flywheel fan direction (inward +X)
G.revolve('part_flywheel_fan', [(0,0),(88,0),(88,28),(0,28)], (-147.5,-65,105.5), (1,0,0), 48, 'black_paint')

def rr_ring(x0,x1,y0,y1,r,n=6):
    w=x1-x0; h=y1-y0
    return G.rrect((x0+x1)/2,(y0+y1)/2,w,h,r,n)
def shoulder(dz, H, base0, base1, Rh, Rv):
    base = base0 + (base1-base0)*dz/H
    s = H - Rv
    if dz <= s: return base
    t = min(1.0, (dz - s)/Rv)
    return base + Rh*(1 - math.sqrt(max(0.0, 1 - t*t)))
G.shoulder = shoulder
def loft_bm(rings, cap_top=True, cap_bot=True):
    bm = bmesh.new()
    vr = []
    for (pts, z) in rings:
        vr.append([bm.verts.new(Vector((x*MM, y*MM, z*MM))) for (x,y) in pts])
    n = len(vr[0])
    for a, b in zip(vr[:-1], vr[1:]):
        for i in range(n):
            j = (i+1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap_bot: bm.faces.new(list(reversed(vr[0])))
    if cap_top: bm.faces.new(vr[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
G.loft_bm = loft_bm
G.rr_ring = rr_ring

X0, X1, Y0, Y1 = -128.0, 110.0, -188.0, 28.0
ZR = 255.0; H = 72.0
# --- upper shell
rings = []
N = 22
for k in range(N+1):
    dz = H * (1 - (1 - k/N)**1.6) if k < N else H
    iy0 = shoulder(dz, H, 4, 5, 62, 56)
    iy1 = shoulder(dz, H, 4, 5, 36, 40)
    ix0 = shoulder(dz, H, 4, 5, 26, 32)
    ix1 = shoulder(dz, H, 4, 5, 26, 32)
    xa, xb, ya, yb = X0+ix0, X1-ix1, Y0+iy0, Y1-iy1
    r = max(6, 22 - 10*dz/H)
    rings.append((rr_ring(xa, xb, ya, yb, r, 6), ZR + 1 + dz*(H-1)/H))
# slight crown: two inner rings
last = rings[-1][0]
cx = sum(p[0] for p in last)/len(last); cy = sum(p[1] for p in last)/len(last)
for s, dzz in ((0.75, 1.2), (0.45, 2.0)):
    rings.append(([(cx+(x-cx)*s, cy+(y-cy)*s) for (x,y) in last], ZR + H + dzz))
up = G.obj_from_bm('part_fuel_tank', loft_bm(rings, cap_top=True, cap_bot=False), 'white', smooth=True)
G.wnormal(up)
# --- seam rim (flange) around the tank
rim = G.extrude('part_fuel_tank_rim', rr_ring(X0, X1, Y0, Y1, 24, 8), 'Z', ZR-2.6, ZR+2.6, 'white')
G.smooth(rim); G.bevel(rim, 2.2, 3, 30); G.wnormal(rim)
# --- lower shell: tapers inward going down, rounded bottom edge
ZB = 204.0
rings = []
M = 14
for k in range(M+1):
    t = k/M
    z = ZR - 1 - t*(ZR - 1 - ZB)
    # side taper + bottom rounding (radius 12)
    dzb = z - ZB
    rb = 12.0
    extra = 0.0 if dzb >= rb else rb*(1 - math.sqrt(max(0.0, 1 - ((rb - dzb)/rb)**2)))
    iy0 = 5 + 12*t + extra
    iy1 = 4 + 6*t + extra
    ix0 = 5 + 5*t + extra
    ix1 = 5 + 5*t + extra
    rings.append((rr_ring(X0+ix0, X1-ix1, Y0+iy0, Y1-iy1, max(6, 20 - 6*t), 6), z))
rings = rings[::-1]   # bottom first
lo = G.obj_from_bm('part_fuel_tank_lower', loft_bm(rings, cap_top=False, cap_bot=True), 'white', smooth=True)
# notch above the cylinder fins (+Y part of bottom raised to ~222)
notch = G.obj_from_bm('cut_tank_notch', G.extrude_bm(G.rrect(25, 25, 150, 80, 14, 6), 'Z', 150, 222), None, coll='gx200_rig')
G.boolean(lo, notch); G.apply_mods(lo); G.remove('cut_tank_notch')
lo.data.shade_smooth(); G.bevel(lo, 2.5, 3, 40); G.wnormal(lo)
print('ok')


# ===== call 20 2026-10-04T10:51:43.859Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CX, CYc = -9.0, -76.0
# filler neck boss on tank top (white)
G.revolve('part_fuel_filler_neck', [(30,0),(46,0),(45,2.5),(42,4.6),(37,5.2),(30,5.2)], (CX,CYc,325.5), (0,0,1), 64, 'white')
# chrome cap: skirt + crown
prof = [(0,0),(35.5,0),(36,1.5),(38.0,3.5),(38.5,6),(38.5,17),(37.8,19.0),(36.5,20.3),(30,20.9),(12,21.3),(0,21.4)]
cap = G.revolve('part_fuel_cap', prof, (CX,CYc,325.0), (0,0,1), 96, 'chrome')
# 4 grip scallops (flower shape in 02d)
cuts = []
for k in range(4):
    a = math.radians(45 + 90*k)
    b = G.revolve_bm([(0,-1),(10.5,-1),(10.5,30),(0,30)], 24)
    b.transform(Matrix.Translation(Vector((CX + 41*math.cos(a), CYc + 41*math.sin(a), 336))*MM))
    cuts.append(b)
c = G.obj_from_bm('cut_cap', G.merge_bms(cuts), None, coll='gx200_rig')
G.boolean(cap, c); G.apply_mods(cap); G.remove('cut_cap')
cap.data.shade_smooth(); G.bevel(cap, 0.8, 2, 40); G.wnormal(cap)
for k in ['02b','02a','02d','02c']:
    G.render('cam_'+k, G.OUT+'look/tank-%s-r1.png'%k)
print('ok')


# ===== call 21 2026-10-04T10:52:58.058Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
X0, X1, Y0, Y1 = -134.0, -26.0, 42.0, 177.0
# --- lid: lower skirt Z 222..258 (full size, slight flare), upper lid Z 258..323 inset 4, rounded top
rings = []
# skirt
for (z, ins, r) in [(222.5, 0.0, 12), (224, 0.0, 12), (257, 1.2, 12), (258.5, 1.6, 12)]:
    rings.append((G.rr_ring(X0+ins, X1-ins, Y0+ins, Y1-ins, r, 6), z))
# step in, then upper lid with rounded top edge (R ~11)
H = 323.0 - 259.0
for k in range(0, 13):
    t = k/12
    z = 259.0 + H*t if k < 12 else 323.0
    dz = z - 259.0
    ins = 4.0 + 0.8*t + G.shoulder(dz, H, 0, 0, 11, 12)
    rings.append((G.rr_ring(X0+ins, X1-ins, Y0+ins, Y1-ins, max(5, 12 - 4*t), 6), z))
lid = G.obj_from_bm('part_air_cleaner', G.loft_bm(rings), 'black_plastic', smooth=True)
G.wnormal(lid)
# small edge between skirt and lid gets a crisp look via weighted normal; add a shallow groove line at Z 257
KX, KY = -78.0, 108.0
# raised centre dome + wing knob
G.revolve('part_air_cleaner_knob_base', [(0,4),(17,4),(21,3),(23.5,1.0),(24,0),(0,0)], (KX,KY,322.5), (0,0,1), 48, 'black_plastic')
# wing knob: thin in X (13 mm), wide in Y (32 mm), tapered top
pts = [(-16,0),(16,0),(14,5),(8.5,11.5),(5,13.5),(-5,13.5),(-8.5,11.5),(-14,5)]
kb = G.extrude_bm(pts, 'X', -6.5, 6.5)
kb.transform(Matrix.Translation(Vector((KX, KY, 326.5))*MM))
kn = G.obj_from_bm('part_air_cleaner_knob', kb, 'black_plastic'); G.hard(kn, 2.2, 3, 30)
# --- air cleaner case (below lid) -> carb
case_pts = [(126,222),(180,222),(181,200),(178,165),(170,145),(150,136),(126,138)]
case = G.extrude('part_air_cleaner_case', case_pts, 'X', -131, -84, 'black_plastic', bev=4, segs=3)
# --- carburetor body (alu) between case and head intake
carb = G.box('part_carburetor', -92, -40, 92, 132, 150, 196, 'alu', bev=4)
ins = G.box('part_carb_insulator', -42, -10, 98, 126, 156, 192, 'black_plastic', bev=3)
# bowl under carb
G.revolve('part_carb_bowl', [(0,0),(16,0),(19,4),(20,14),(0,14)], (-66,112,136), (0,0,1), 32, 'alu')
print('ok')


# ===== call 22 2026-10-04T10:53:22.879Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
X0, X1, Y0, Y1 = 21.5, 134.0, 44.0, 188.0
# --- muffler body (inner can), slightly smaller than shield
body = G.box('part_muffler', X0+2, X1-2, Y0+2, Y1-2, 237, 298, 'black_paint', bev=4, segs=2)
# --- heat shield cap (shell): loft vertical skirt then 45deg chamfer to flat top
rings = []
for (z, ins, r) in [(293, 0, 8), (312, 0, 8), (314.5, 0.6, 8), (326, 13.5, 6), (328, 15.5, 5)]:
    rings.append((G.rr_ring(X0+ins, X1-ins, Y0+ins, Y1-ins, r, 4), z))
cap = G.obj_from_bm('part_muffler_shield', G.loft_bm(rings, cap_top=True, cap_bot=False), 'black_paint')
G.smooth(cap); G.bevel(cap, 1.5, 2, 25)
# louvre slots on the chamfer: 9 across +X/-X sides, 7 along +Y/-Y sides
cuts = []
def slot_on_chamfer(cx, cy, axis, length=6.0, width=8.0):
    # vertical cutter through the chamfer band (Z 314..327)
    if axis == 'X':   # slot elongated along X (on +Y/-Y chamfer)
        b = G.box_bm(cx-length/2, cx+length/2, cy-width, cy+width, 316, 335)
    else:
        b = G.box_bm(cx-width, cx+width, cy-length/2, cy+length/2, 316, 335)
    return b
for i in range(9):
    y = 63 + i*(169-63)/8
    cuts.append(slot_on_chamfer(X1-7, y, 'Y', 6.5, 6))
    cuts.append(slot_on_chamfer(X0+7, y, 'Y', 6.5, 6))
for i in range(7):
    x = 42 + i*(114-42)/6
    cuts.append(slot_on_chamfer(x, Y1-7, 'X', 6.5, 6))
    cuts.append(slot_on_chamfer(x, Y0+7, 'X', 6.5, 6))
c = G.obj_from_bm('cut_muffler_louvres', G.merge_bms(cuts), None, coll='gx200_rig')
G.boolean(cap, c); G.apply_mods(cap); G.remove('cut_muffler_louvres')
cap.data.shade_smooth()
G.solidify(cap, 1.2, -1); G.wnormal(cap)
# --- slots on the body faces (+X face: 2 cols x 3 rows + 1; +Y face: 5 + 3), 3 mm deep
cuts = []
for (y0, y1) in [(67, 113), (120, 165)]:
    for (zc) in (289, 280, 269):
        cuts.append(G.extrude_bm(G.rrect((y0+y1)/2, zc, y1-y0, 6.0, 2.9, 3), 'X', X1-6, X1+5))
cuts.append(G.extrude_bm(G.rrect(149.5, 259, 31, 6.0, 2.9, 3), 'X', X1-6, X1+5))
for zc in (291, 282, 273, 264, 255):
    cuts.append(G.extrude_bm(G.rrect(102, zc, 24, 6.0, 2.9, 3), 'Y', Y1-6, Y1+5))
for zc in (289, 280, 271):
    cuts.append(G.extrude_bm(G.rrect(41, zc, 13, 6.0, 2.9, 3), 'Y', Y1-6, Y1+5))
c = G.obj_from_bm('cut_muffler_slots', G.merge_bms(cuts), None, coll='gx200_rig')
G.boolean(body, c); body.modifiers.move(len(body.modifiers)-1, 0); G.apply_mods(body); G.remove('cut_muffler_slots')
body.data.shade_smooth(); G.bevel(body, 1.0, 1, 35); G.wnormal(body)
# --- exhaust outlet on +Y face at (X 67, Z 270): flange ring + pipe stub + 4 screws
EX, EZ = 67.2, 270.0
G.revolve('part_muffler_outlet', [(9.5,0),(21,0),(21,2.2),(19.5,3.2),(13.8,3.2),(13.8,9),(12.6,10),(11.0,10),(11.0,-2)], (EX, Y1-2, EZ), (0,1,0), 48, 'black_paint')
bms = []
for k in range(4):
    a = math.radians(45 + 90*k)
    b = G.revolve_bm([(0,0),(3.8,0),(3.8,1.5),(2.8,2.6),(0,2.6)], 12)
    b.transform(G.axis_matrix((EX + 26*math.cos(a), Y1-0.5, EZ + 26*math.sin(a)), (0,1,0)))
    bms.append(b)
G.obj_from_bm('part_muffler_screws', G.merge_bms(bms), 'zinc', smooth=True)
# --- exhaust pipe + port flange (from head top up into muffler)
PX, PY = 45.0, 90.0
G.revolve('part_exhaust_pipe', [(0,0),(12,0),(12,52),(0,52)], (PX,PY,186), (0,0,1), 32, 'black_paint')
fl = G.extrude('part_exhaust_flange', G.rrect(PX, PY, 34, 62, 9, 4), 'Z', 186, 192, 'black_paint', bev=1.5)
bms = []
for dy in (-22, 22):
    b = G.revolve_bm([(0,0),(6,0),(6,5.5),(5,6.2),(0,6.2)], 6); b.transform(Matrix.Translation(Vector((PX, PY+dy, 192))*MM)); bms.append(b)
G.obj_from_bm('part_exhaust_nuts', G.merge_bms(bms), 'zinc')
# port boss under the flange, joining the head
G.revolve('part_exhaust_port', [(0,0),(16,0),(16,26),(0,26)], (PX,PY,162), (0,0,1), 32, 'alu')
print('ok')


# ===== call 23 2026-10-04T10:53:28.176Z =====
import bpy
G = bpy.app.driver_namespace['gx']
for k in ['02a','02b','02c','02d']:
    G.render('cam_'+k, G.OUT+'look/ac_muffler-%s-r1.png'%k)
print('ok')


# ===== call 24 2026-10-04T10:53:54.293Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
G.revolve('part_muffler_outlet', [(9.5,0),(21,0),(21,1.8),(19.5,2.6),(13.8,2.6),(13.0,3.2),(11.0,3.2),(11.0,-3)], (67.2, 186.0, 270.0), (0,1,0), 48, 'black_paint')
# bbox check of parts collection
import mathutils
mn = mathutils.Vector((1e9,)*3); mx = -mn
dg = bpy.context.evaluated_depsgraph_get()
for o in bpy.data.collections['gx200_parts'].objects:
    if o.type != 'MESH': continue
    oe = o.evaluated_get(dg)
    for c in oe.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        mn = mathutils.Vector(map(min, mn, w)); mx = mathutils.Vector(map(max, mx, w))
print('bbox mm', [round(v*1000,1) for v in mn], [round(v*1000,1) for v in mx], 'size', [round((b-a)*1000,1) for a,b in zip(mn,mx)])


# ===== call 25 2026-10-04T10:54:04.691Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 106.0
bpy.data.objects['part_muffler_outlet'].location.y = -0.5*MM
prof = [(0,0),(12.5,0),(12.5,3.0),(11.0,3.6),(10,4.2),(10,55.2),(9.0,56.2),(0,56.2)]
sh = G.revolve('part_output_shaft', prof, (100.3,CY,CZ), (1,0,0), 64, 'steel')
kw = G.obj_from_bm('cut_keyway', G.box_bm(121.5, 160, CY-2.5, CY+2.5, CZ+7, CZ+15), None, coll='gx200_rig')
b = G.revolve_bm([(0,-20),(3.4,-20),(3.4,1),(0,1)], 20); b.transform(G.axis_matrix((156.5,CY,CZ),(1,0,0)))
hole = G.obj_from_bm('cut_shaft_hole', b, None, coll='gx200_rig')
G.boolean(sh, kw); G.boolean(sh, hole); G.apply_mods(sh); G.remove('cut_keyway'); G.remove('cut_shaft_hole')
sh.data.shade_smooth()
bm = bmesh.new(); bm.from_mesh(sh.data)
for e in bm.edges:
    if len(e.link_faces)==2 and e.calc_face_angle(0) > math.radians(35): e.smooth = False
bm.to_mesh(sh.data); bm.free()
G.wnormal(sh)
print('ok')


# ===== call 26 2026-10-04T10:54:36.193Z =====
import bpy, math
from mathutils import Vector, Matrix, Euler
from bpy_extras.object_utils import world_to_camera_view
G = bpy.app.driver_namespace['gx']; MM = G.MM

def sample_points(stride=7):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in bpy.data.collections['gx200_parts'].objects:
        if o.type != 'MESH' or o.hide_render: continue
        oe = o.evaluated_get(dg); me = oe.to_mesh()
        mw = o.matrix_world
        vs = me.vertices
        for i in range(0, len(vs), stride):
            pts.append(mw @ vs[i].co)
        oe.to_mesh_clear()
    return pts
G.sample_points = sample_points

PHOTOS = {
 '07': dict(W=836, H=822, bbox=(88,77,766,705)),
 '01': dict(W=1000, H=1000, bbox=(34,56,937,882)),
 '09': dict(W=640, H=480, bbox=(130,28,533,441)),
 '03': dict(W=640, H=480, bbox=(146,91,497,402)),
}
G.PHOTOS = PHOTOS

def fit_photo_cam(key, az, el, focal, roll=0.0, target=(0,0,170), pts=None, iters=12):
    ph = PHOTOS[key]; W, H = ph['W'], ph['H']
    x0,y0,x1,y1 = ph['bbox']
    name = 'cam_' + key
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name); cam = bpy.data.objects.new(name, cd); G.link(cam, 'gx200_rig')
    cd = cam.data; cd.type = 'PERSP'; cd.lens = focal; cd.sensor_fit = 'AUTO'; cd.sensor_width = 36
    cd.clip_start = 0.01; cd.clip_end = 20
    sc = G.scn(); sc.render.resolution_x = W; sc.render.resolution_y = H
    T = Vector(target)*MM
    # forward vector: camera looks from direction (az, el); az measured from -X axis towards -Y
    a = math.radians(az); e = math.radians(el)
    dirv = Vector((-math.cos(e)*math.cos(a), -math.cos(e)*math.sin(a), math.sin(e)))   # from target to camera
    dist = 1.5
    cd.shift_x = 0; cd.shift_y = 0
    if pts is None: pts = sample_points()
    for it in range(iters):
        cam.location = T + dirv*dist
        q = (-dirv).to_track_quat('-Z', 'Y')
        cam.rotation_euler = (q.to_matrix().to_4x4() @ Matrix.Rotation(math.radians(roll), 4, 'Z')).to_euler()
        bpy.context.view_layer.update()
        xs=[]; ys=[]
        for p in pts:
            c = world_to_camera_view(sc, cam, p)
            xs.append(c.x*W); ys.append((1-c.y)*H)
        px0,px1,py0,py1 = min(xs),max(xs),min(ys),max(ys)
        wr = (px1-px0)/(x1-x0); hr = (py1-py0)/(y1-y0)
        s = (wr+hr)/2
        dist *= s
        # shift to align centres (shift is in units of the larger image dimension)
        cxe = ((x0+x1)/2 - (px0+px1)/2)/max(W,H); cye = ((y0+y1)/2 - (py0+py1)/2)/max(W,H)
        cd.shift_x -= cxe; cd.shift_y += cye
    return dict(dist=round(dist,3), proj=(round(px0),round(py0),round(px1),round(py1)), wr=round(wr,3), hr=round(hr,3))
G.fit_photo_cam = fit_photo_cam
pts = sample_points()
print(len(pts))
for f in (60, 100, 150):
    print(f, fit_photo_cam('07', 0.0, 8.0, f, pts=pts))


# ===== call 27 2026-10-04T10:54:47.402Z =====
import bpy, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
G = bpy.app.driver_namespace['gx']; MM = G.MM
pts = G.sample_points(1)
FEAT07 = [((-156.5,-65,105.5),(550,520)), ((-9,-76,346),(548,80)), ((-78,108,339),(220,102)), ((-128,-188,255),(764,240)), ((-134,177,240),(92,270))]
def feat_err(key, feats):
    sc = G.scn(); cam = bpy.data.objects['cam_'+key]; ph = G.PHOTOS[key]
    e = 0; out=[]
    for (p, (u,v)) in feats:
        c = world_to_camera_view(sc, cam, Vector(p)*MM)
        x, y = c.x*ph['W'], (1-c.y)*ph['H']
        out.append((round(x),round(y))); e += (x-u)**2 + (y-v)**2
    return math.sqrt(e/len(feats)), out
G.feat_err = feat_err
best = None
for f in (50, 70, 100, 140):
    for el in (2, 6, 10, 14):
        for az in (-4, 0, 4):
            r = G.fit_photo_cam('07', az, el, f, pts=pts, iters=6)
            e, out = feat_err('07', FEAT07)
            if best is None or e < best[0]: best = (e, f, el, az, out, r)
print(best)


# ===== call 28 2026-10-04T10:55:04.304Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
pts = G.sample_points(1)
FEAT07 = [((-156.5,-65,105.5),(550,520)), ((-9,-76,346),(548,80)), ((-78,108,339),(220,102)), ((-128,-188,255),(764,240)), ((-134,177,240),(92,270))]
best=None
for f in (120, 160, 220, 300):
    for el in (0, 2, 4):
        for az in (-2, 0, 2):
            r = G.fit_photo_cam('07', az, el, f, pts=pts, iters=6)
            e, out = G.feat_err('07', FEAT07)
            if best is None or e < best[0]: best = (e, f, el, az, out, r)
print(best)
e,f,el,az,out,r = best
print(G.fit_photo_cam('07', az, el, f, pts=pts, iters=10), G.feat_err('07', FEAT07))


# ===== call 29 2026-10-04T10:55:27.354Z =====
import bpy, math
from mathutils import Vector
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
# world
w = bpy.data.worlds.get('gx200_world') or bpy.data.worlds.new('gx200_world')
sc.world = w
try: w.use_nodes = True
except Exception: pass
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.78, 0.79, 0.80, 1)
bg.inputs['Strength'].default_value = 0.55
def area_light(name, loc, energy, size, color=(1,1,1)):
    G.remove(name)
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = color
    o = bpy.data.objects.new(name, ld); G.link(o, 'gx200_rig')
    o.location = Vector(loc)
    d = Vector((0,0,0.17)) - o.location
    o.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
    return o
area_light('light_key',  (-0.9, -0.75, 1.0), 260, 0.9)
area_light('light_fill', (-0.8,  0.95, 0.45), 90, 1.2, (0.95,0.97,1.0))
area_light('light_rim',  ( 0.9,  0.3, 1.1), 160, 0.8)
area_light('light_top',  ( 0.0,  0.0, 1.4), 60, 1.5)
# eevee settings
G.set_engine(sc, 'BLENDER_EEVEE')
ee = sc.eevee
for attr, val in (('taa_render_samples', 32), ('use_shadows', True), ('use_raytracing', True)):
    try: setattr(ee, attr, val)
    except Exception as ex: print('skip', attr, ex)
try:
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'None'
except Exception as ex: print(ex)
print([i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items])


# ===== call 30 2026-10-04T10:55:33.232Z =====
import bpy, time
G = bpy.app.driver_namespace['gx']
sc = G.scn()
print(sc.view_settings.view_transform, sc.view_settings.look, sc.display_settings.display_device)
t=time.time()
G.render('cam_07', G.OUT+'look/full-07-r1.png', engine='BLENDER_EEVEE', res=(836,822), transparent=False, samples=32)
print('t', time.time()-t)


# ===== call 31 2026-10-04T10:57:14.096Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
try:
    sc.view_settings.view_transform = 'Standard'
except TypeError as e: print('vt', e)
print(sc.view_settings.view_transform)
CY, CZ = -65.0, 105.5
# ---- shroud outline v2 (photo 07 + 02a)
OUTL = [(-173,40),(-173,180),(-170,196),(-160,205),(-140,207),(50,207),(64,203),(76,193),(86,174),(94,148),(97,122),(95,100),(88,80),(76,62),(60,45),(40,28),(18,17),(0,14),(-135,14),(-152,19),(-164,28),(-171,40)]
X0, X1 = -149.5, -103.0
bm = G.extrude_bm(OUTL, 'X', X0, X1)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.x > 0.9], context='FACES_ONLY')
sh = bpy.data.objects['part_fan_shroud']
old = sh.data
me = bpy.data.meshes.new('part_fan_shroud'); bm.to_mesh(me); bm.free()
me.materials.append(G.mat('red')); me.shade_smooth()
sh.data = me; bpy.data.meshes.remove(old)
# ---- recoil cover v2: wider, longer slots
XF = -149.0
prof = [(0,7.5),(36,7.5),(37,7.3),(84,7.3),(88,6.6),(92,5.0),(95,2.8),(96.5,0.8),(97,0),(95,0)]
rc = bpy.data.objects['part_recoil_starter']
for m in list(rc.modifiers): rc.modifiers.remove(m)
b = G.revolve_bm(prof, 120); b.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
old = rc.data; me = bpy.data.meshes.new('part_recoil_starter'); b.to_mesh(me); b.free()
me.materials.append(G.mat('red')); rc.data = me; bpy.data.meshes.remove(old)
G.solidify(rc, 1.4, -1)
cuts = []
def slot_bm(r0, r1, ang, w0, w1):
    # tapered radial slot (wider at outer end)
    pts = []
    n = 5
    for i in range(n+1):
        a = math.pi/2 + math.pi*i/n
        pts.append((r0 + (w0/2)*math.cos(a), (w0/2)*math.sin(a)))
    for i in range(n+1):
        a = -math.pi/2 + math.pi*i/n
        pts.append((r1 + (w1/2)*math.cos(a), (w1/2)*math.sin(a)))
    b = G.extrude_bm(pts, 'Z', -5, 20)
    b.transform(Matrix.Rotation(ang, 4, 'Z'))
    return b
for i in range(24):
    cuts.append(slot_bm(40, 58, 2*math.pi*(i+0.5)/24, 5.0, 7.0))
for i in range(36):
    cuts.append(slot_bm(63, 82, 2*math.pi*i/36, 5.6, 7.4))
cb = G.merge_bms(cuts); cb.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
G.remove('cut_recoil_slots')
cobj = G.obj_from_bm('cut_recoil_slots', cb, None, coll='gx200_rig')
G.boolean(rc, cobj); G.apply_mods(rc); G.remove('cut_recoil_slots')
rc.data.shade_smooth(); G.wnormal(rc)
# screws: move to r=88.5 on the rim between slots? keep r 82 but they collide with outer slots -> put at r 89
bms = []
for k in range(6):
    a = math.radians(30 + 60*k)
    b = G.revolve_bm([(0,0),(5.0,0),(5.0,0.8),(4.2,2.0),(2.2,2.5),(0,2.5)], 20)
    b.transform(G.axis_matrix((XF-6.0, CY + 89*math.cos(a), CZ + 89*math.sin(a)), (-1,0,0)))
    bms.append(b)
G.obj_from_bm('part_recoil_screws', G.merge_bms(bms), 'zinc', smooth=True)
print('ok')


# ===== call 32 2026-10-04T10:57:37.994Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
XF = -149.0
# ---- recoil handle v2: paddle grip (photo 07 + 02a)
XG = -166.5
p0 = Vector((XG, 72, 108)); p1 = Vector((XG, 22, 162))
d = (p1-p0); Lg = d.length; d.normalize()
prof = [(0,0),(6,0.3),(10,1.8),(12.5,5),(13.2,10),(12.0,Lg*0.45),(12.6,Lg-12),(12.2,Lg-6),(10,Lg-2),(6,Lg-0.4),(0,Lg)]
b = G.revolve_bm(prof, 32)
for v in b.verts: v.co.x *= 0.66
b.transform(G.axis_matrix(tuple(p0), tuple(d)))
G.obj_from_bm('part_recoil_handle', b, 'black_plastic', smooth=True)
# stem/body: from grip (lower-right side near its middle-upper) down to rope guide (Y 13, Z 110)
RG = Vector((XF-1.0, 13, 110))
q0 = p0 + d*(Lg*0.62) + Vector((-1, -6, -6))
dv = RG - q0; Ls = dv.length
b = G.revolve_bm([(0,0),(9.5,0),(9.0,Ls*0.35),(7.0,Ls*0.8),(5.5,Ls),(0,Ls)], 24)
for v in b.verts: v.co.x *= 0.75
b.transform(G.axis_matrix(tuple(q0), tuple(dv.normalized())))
G.obj_from_bm('part_recoil_handle_stem', b, 'black_plastic', smooth=True)
G.revolve('part_rope_guide', [(3,0),(9.5,0),(9.5,3.5),(7.5,5),(3,5)], (XF-0.5, 13, 110), (-1,0,0), 24, 'zinc')

# ---- air cleaner case v2 (photo 07: Y 123..181, Z 143..227) with rounded lower corner
case_pts = [(123,227),(181,227),(182,200),(181,170),(176,152),(165,143),(140,141),(123,143)]
G.extrude('part_air_cleaner_case', case_pts, 'X', -133, -86, 'black_plastic', bev=4, segs=3)
# carb cover (lower left extension) with window showing carb
cov_pts = [(82,196),(125,196),(125,141),(92,141),(82,150)]
cov = G.extrude('part_carb_cover', cov_pts, 'X', -122, -86, 'black_plastic')
win = G.obj_from_bm('cut_carb_window', G.extrude_bm(G.rrect(105, 168, 30, 40, 5, 4), 'X', -130, -110), None, coll='gx200_rig')
G.boolean(cov, win); G.apply_mods(cov); G.remove('cut_carb_window')
G.hard(cov, 3, 2, 35)
# carb body visible through window
G.box('part_carburetor', -112, -40, 90, 124, 148, 192, 'alu', bev=3)
G.revolve('part_carb_bowl', [(0,0),(14,0),(17,3),(18,22),(0,22)], (-100,128,118), (0,0,1), 32, 'zinc')
G.revolve('part_carb_drain', [(0,0),(4,0),(4,8),(0,8)], (-100,128,110), (0,0,1), 12, 'zinc')
# fuel cock lever (white tab) on case -X face
fl = G.box('part_fuel_cock_lever', -139, -133, 116, 136, 178, 186, 'white', bev=1.2)
# choke lever (black) small on case top-front
G.box('part_choke_lever', -140, -133, 140, 150, 196, 214, 'black_plastic', bev=1.2)
# AC case side stud nut
G.revolve('part_ac_stud', [(0,0),(5.5,0),(5.5,6),(0,6)], (-110,181,166), (0,1,0), 6, 'zinc')
# ---- throttle (speed control) lever: stamped channel on top, ends at (Y 15..32, Z 209..220)
pts = [(-140,0),(-100,0),(-80,4),(-60,10),(-40,12),(-40,-12)]
thr = G.extrude('part_throttle_lever', [(70,0),(24,0),(18,4),(16,10),(70,10)], 'Y', 0, 1, 'zinc')
# simpler: a bent bar from pivot (X -100, Y 70, Z 222) to knob end (X -140, Y 18, Z 214)
G.remove('part_throttle_lever')
a = Vector((-98, 76, 224)); bpt = Vector((-145, 20, 214))
dv = bpt - a; Lb = dv.length
b = G.box_bm(-6, 6, -2, 2, 0, Lb)   # local z along bar
q = Vector((0,0,1)).rotation_difference(dv.normalized())
b.transform(Matrix.Translation(a*MM) @ q.to_matrix().to_4x4())
lev = G.obj_from_bm('part_throttle_lever', b, 'zinc'); G.hard(lev, 1.0, 2, 35)
G.box('part_throttle_lever_tab', -152, -138, 14, 30, 206, 218, 'zinc', bev=1.5)
G.revolve('part_throttle_pivot', [(0,0),(7,0),(7,8),(0,8)], (-98,76,216), (0,0,1), 16, 'zinc')
print('ok')


# ===== call 33 2026-10-04T10:58:14.260Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
def hexbolt_bm(pos, axis, af=12, h=6, flange=True):
    rh = af/2/math.cos(math.radians(30))
    bms = []
    if flange:
        f = G.revolve_bm([(0,0),(rh*1.15,0),(rh*1.15,1.2),(0,1.2)], 24); bms.append(f)
        hb = G.revolve_bm([(0,1.2),(rh,1.2),(rh,h),(rh*0.85,h+0.6),(0,h+0.6)], 6); bms.append(hb)
    else:
        hb = G.revolve_bm([(0,0),(rh,0),(rh,h),(rh*0.85,h+0.6),(0,h+0.6)], 6); bms.append(hb)
    b = G.merge_bms(bms); b.transform(G.axis_matrix(pos, axis)); return b
G.hexbolt_bm = hexbolt_bm
# PTO cover bolts
bms = [hexbolt_bm((99.5, y, z), (1,0,0), 12, 5.5) for (y,z) in [(-130.4,165.6),(-42.5,165.6),(-140.9,95.4),(31.3,98.9),(-112,26),(10,26)]]
G.obj_from_bm('part_crankcase_bolts', G.merge_bms(bms), 'zinc')
# engine switch on shroud -Y side wall
sw = G.box('part_engine_switch', -144, -120, -183, -171, 146, 184, 'red', bev=2.5)
G.box('part_engine_switch_toggle', -138, -126, -188, -182, 160, 172, 'red', bev=1.5)
# oil filler caps (two, at X~88, angled 45deg outward)
for name, base, dirv in [('part_oil_filler_cap_l', (88,-148,52), (0,-0.62,0.78)), ('part_oil_filler_cap_r', (88,44,50), (0,0.62,0.78))]:
    neck = G.revolve_bm([(0,0),(13,0),(13,18),(0,18)], 24)
    capb = G.revolve_bm([(0,18),(15,18),(15.5,21),(15,29),(13,31),(0,31)], 24)
    grip = G.box_bm(-3.5, 3.5, -14, 14, 29, 40)
    for b in (neck, capb, grip):
        b.transform(G.axis_matrix(base, dirv))
    G.obj_from_bm(name+'_neck', neck, 'alu', smooth=True)
    o = G.obj_from_bm(name, G.merge_bms([capb, grip]), 'black_plastic'); G.hard(o, 1.5, 2, 35)
# oil drain plug (+Y side, bottom)
G.obj_from_bm('part_oil_drain_plug', hexbolt_bm((26, 46, 13), (0,1,0), 12, 6), 'zinc')
# tank bracket (black) at PTO end under tank + recoil-end bracket (zinc) with bolt
br = G.extrude('part_tank_bracket', [(-170,190),(32,190),(32,207),(-170,207)], 'X', 86, 104, 'black_paint', bev=1.5)
G.obj_from_bm('part_tank_bracket_bolts', G.merge_bms([hexbolt_bm((104, y, 198), (1,0,0), 10, 5) for y in (-158, 20)]), 'zinc')
br2 = G.box('part_tank_bracket_rear', -132, -118, -168, -140, 178, 207, 'zinc', bev=1.5)
G.obj_from_bm('part_tank_bracket_rear_bolt', hexbolt_bm((-132, -154, 188), (-1,0,0), 10, 5), 'zinc')
print('ok')


# ===== call 34 2026-10-04T10:58:28.467Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
def tube(name, pts, r, mat, res=12):
    G.remove(name)
    cu = bpy.data.curves.new(name+'_crv', 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = r*MM; cu.bevel_resolution = 3; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = Vector(p)*MM; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.resolution_u = res
    tmp = bpy.data.objects.new(name+'_tmp', cu); G.link(tmp, 'gx200_rig')
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp); bpy.data.curves.remove(cu)
    me.name = name
    o = bpy.data.objects.new(name, me); G.link(o)
    me.materials.append(G.mat(mat)); me.shade_smooth()
    return o
G.tube = tube
# spark plug: hex + insulator on head top, boot over it
PB = Vector((10, 92, 214))
axis = Vector((0, -0.25, 1)).normalized()
G.revolve('part_spark_plug', [(0,0),(10.5,0),(10.5,8),(7,9),(6,22),(0,22)], tuple(PB), tuple(axis), 6, 'steel', smooth_=False)
# rubber boot: curved, from plug up and bending toward -X
tube('part_spark_plug_cap', [(10, 89, 222), (8, 86, 240), (-4, 84, 252), (-16, 84, 254)], 9.5, 'rubber')
# HT lead from boot to ignition coil under shroud
tube('part_ht_lead', [(-16, 84, 254), (-40, 84, 246), (-70, 70, 218), (-104, 55, 196)], 3.5, 'rubber')
# fuel hose from tank bottom to carb
tube('part_fuel_hose', [(-112, 8, 208), (-116, 30, 200), (-112, 70, 196), (-104, 96, 190)], 4.5, 'rubber')
# governor / throttle link rod
tube('part_governor_rod', [(-98, 76, 222), (-60, 92, 214), (-30, 104, 200)], 1.2, 'steel', 6)
print('ok')


# ===== call 35 2026-10-04T10:58:33.738Z =====
import bpy
G = bpy.app.driver_namespace['gx']
G.render('cam_07', G.OUT+'look/full-07-r2.png', engine='BLENDER_EEVEE', res=(836,822), transparent=False, samples=32)
print('ok')


# ===== call 36 2026-10-04T10:58:51.700Z =====
import bpy
G = bpy.app.driver_namespace['gx']
for n in ['part_recoil_starter','part_fan_shroud']:
    o = bpy.data.objects[n]
    print(n, len(o.data.vertices), len(o.data.polygons), [(m.name, m.type) for m in o.modifiers], o.hide_render, o.hide_get(view_layer=G.scn().view_layers[0]))
print([o.name for o in bpy.data.collections['gx200_rig'].objects])


# ===== call 37 2026-10-04T10:59:11.999Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 105.5; XF = -149.0
# closed (manifold) recoil cover profile: outer surface then inner surface back to the axis
outer = [(0,7.5),(36,7.5),(37,7.3),(84,7.3),(88,6.6),(92,5.0),(95,2.8),(96.5,0.8),(97,0)]
inner = [(95.4,0),(95.0,0.6),(93.6,2.2),(90.8,4.0),(87.2,5.3),(83.6,5.9),(37,5.9),(36,6.1),(0,6.1)]
prof = outer + inner
b = G.revolve_bm(prof, 120)
b.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
rc = G.obj_from_bm('part_recoil_starter', b, 'red')
cuts = []
def slot_bm(r0, r1, ang, w0, w1):
    pts = []
    n = 5
    for i in range(n+1):
        a = math.pi/2 + math.pi*i/n
        pts.append((r0 + (w0/2)*math.cos(a), (w0/2)*math.sin(a)))
    for i in range(n+1):
        a = -math.pi/2 + math.pi*i/n
        pts.append((r1 + (w1/2)*math.cos(a), (w1/2)*math.sin(a)))
    bb = G.extrude_bm(pts, 'Z', 3, 12)
    bb.transform(Matrix.Rotation(ang, 4, 'Z'))
    return bb
for i in range(24):
    cuts.append(slot_bm(40, 58, 2*math.pi*(i+0.5)/24, 5.0, 7.0))
for i in range(36):
    cuts.append(slot_bm(63, 82, 2*math.pi*i/36, 5.6, 7.4))
cb = G.merge_bms(cuts); cb.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
cobj = G.obj_from_bm('cut_recoil_slots', cb, None, coll='gx200_rig')
G.boolean(rc, cobj); G.apply_mods(rc)
print('verts after bool', len(rc.data.vertices))
G.remove('cut_recoil_slots')
rc.data.shade_smooth(); G.wnormal(rc)
# lighting / colour management
sc = G.scn()
for look in ('AgX - Punchy', 'Punchy', 'AgX - Medium High Contrast'):
    try:
        sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = look; print('look', look); break
    except TypeError as e: print('look fail', look)
sc.view_settings.exposure = 0.0
bpy.data.objects['light_key'].data.energy = 180
bpy.data.objects['light_fill'].data.energy = 70
bpy.data.objects['light_rim'].data.energy = 120
bpy.data.objects['light_top'].data.energy = 40
w = sc.world; bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.9, 0.9, 0.9, 1); bg.inputs['Strength'].default_value = 0.6
G.render('cam_07', G.OUT+'look/full-07-r3.png', engine='BLENDER_EEVEE', res=(836,822), transparent=False, samples=32)


# ===== call 38 2026-10-04T10:59:27.284Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 105.5; XF = -149.0
outer = [(0,7.5),(36,7.5),(37,7.3),(84,7.3),(88,6.6),(92,5.0),(95,2.8),(96.5,0.8),(97,0)]
inner = [(95.4,0),(95.0,0.6),(93.6,2.2),(90.8,4.0),(87.2,5.3),(83.6,5.9),(37,5.9),(36,6.1),(0,6.1)]
b = G.revolve_bm(outer+inner, 120)
print('manifold edges bad:', sum(1 for e in b.edges if not e.is_manifold), 'verts', len(b.verts), 'faces', len(b.faces))
# check degenerate faces
print('deg faces', sum(1 for f in b.faces if f.calc_area() < 1e-12))
b.free()


# ===== call 39 2026-10-04T10:59:47.331Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 105.5; XF = -149.0
rc = bpy.data.objects['part_recoil_starter']
outer = [(0,7.5),(36,7.5),(37,7.3),(84,7.3),(88,6.6),(92,5.0),(95,2.8),(96.5,0.8),(97,0)]
inner = [(95.4,0),(95.0,0.6),(93.6,2.2),(90.8,4.0),(87.2,5.3),(83.6,5.9),(37,5.9),(36,6.1),(0,6.1)]
b = G.revolve_bm(outer+inner, 120); b.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
for m in list(rc.modifiers): rc.modifiers.remove(m)
b.to_mesh(rc.data); b.free()
print('base verts', len(rc.data.vertices))
def slot_bm(r0, r1, ang, w0, w1):
    pts = []
    n = 5
    for i in range(n+1):
        a = math.pi/2 + math.pi*i/n
        pts.append((r0 + (w0/2)*math.cos(a), (w0/2)*math.sin(a)))
    for i in range(n+1):
        a = -math.pi/2 + math.pi*i/n
        pts.append((r1 + (w1/2)*math.cos(a), (w1/2)*math.sin(a)))
    bb = G.extrude_bm(pts, 'Z', 3, 12)
    bb.transform(Matrix.Rotation(ang, 4, 'Z'))
    return bb
cuts = [slot_bm(40, 58, 2*math.pi*(i+0.5)/24, 5.0, 7.0) for i in range(24)] + [slot_bm(63, 82, 2*math.pi*i/36, 5.6, 7.4) for i in range(36)]
cb = G.merge_bms(cuts); cb.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
print('cutter bad edges', sum(1 for e in cb.edges if not e.is_manifold))
cobj = G.obj_from_bm('cut_recoil_slots', cb, None, coll='gx200_rig')
m = G.boolean(rc, cobj)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
for solver in ('EXACT','FLOAT'):
    try: m.solver = solver
    except Exception as e: print('solver err', e); continue
    dg.update()
    print(solver, len(rc.evaluated_get(dg).data.vertices))
print([i.identifier for i in m.bl_rna.properties['solver'].enum_items])


# ===== call 40 2026-10-04T10:59:57.955Z =====
import bpy
G = bpy.app.driver_namespace['gx']
rc = bpy.data.objects['part_recoil_starter']
m = rc.modifiers[-1]
m.solver = 'MANIFOLD'
dg = bpy.context.evaluated_depsgraph_get(); dg.update()
print('MANIFOLD', len(rc.evaluated_get(dg).data.vertices))
G.apply_mods(rc); G.remove('cut_recoil_slots')
rc.data.shade_smooth()
import bmesh, math
bm = bmesh.new(); bm.from_mesh(rc.data)
for e in bm.edges:
    if len(e.link_faces)==2 and e.calc_face_angle(0) > math.radians(40): e.smooth = False
bm.to_mesh(rc.data); bm.free()
G.wnormal(rc)
# make MANIFOLD the default solver
def boolean(o, cutter, op='DIFFERENCE', apply=False, solver='MANIFOLD'):
    mm = o.modifiers.new('Bool_'+cutter.name, 'BOOLEAN')
    mm.operation = op; mm.object = cutter
    try: mm.solver = solver
    except Exception: pass
    cutter.display_type = 'WIRE'; cutter.hide_render = True
    cutter.hide_set(True, view_layer=G.scn().view_layers[0])
    return mm
G.boolean = boolean
# shroud slots: check & switch solver
sh = bpy.data.objects['part_fan_shroud']
sh.modifiers['Bool_cut_shroud_slots'].solver = 'MANIFOLD'
dg.update(); print('shroud', len(sh.evaluated_get(dg).data.vertices))


# ===== call 41 2026-10-04T11:00:10.622Z =====
import bpy
G = bpy.app.driver_namespace['gx']
G.MATS['red'] = ((0.70, 0.015, 0.04), 0.30, 0.0)
G.MATS['white'] = ((0.90, 0.89, 0.85), 0.35, 0.0)
G.MATS['black_plastic'] = ((0.05, 0.052, 0.058), 0.55, 0.0)
for k in ('red','white','black_plastic'): G.mat(k)
G.render('cam_07', G.OUT+'look/full-07-r4.png', engine='BLENDER_EEVEE', res=(836,822), transparent=False, samples=32)


# ===== call 42 2026-10-04T11:01:22.545Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
CY, CZ = -65.0, 105.5; XF = -149.0
sc = G.scn()
sc.view_settings.view_transform = 'Standard'; 
try: sc.view_settings.look = 'None'
except TypeError: pass
# ---- shroud outline v3 (photo 07)
OUTL = [(-171,170),(-171,80),(-169,62),(-163,44),(-153,28),(-138,15),(-120,8),(-100,6),(10,6),(30,12),(50,26),(66,42),(78,58),(87,78),(92,100),(92,118),(88,140),(80,160),(70,177),(60,193),(52,203),(44,207),(-135,207),(-150,204),(-161,197),(-168,186)]
bm = G.extrude_bm(OUTL, 'X', -149.5, -103.0)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.x > 0.9], context='FACES_ONLY')
sh = bpy.data.objects['part_fan_shroud']
old = sh.data; me = bpy.data.meshes.new('part_fan_shroud'); bm.to_mesh(me); bm.free()
me.materials.append(G.mat('red')); me.shade_smooth(); sh.data = me; bpy.data.meshes.remove(old)
# big air-intake hole behind the recoil cover + side slots
cs = bpy.data.objects['cut_shroud_slots']
b = bmesh.new(); b.from_mesh(cs.data)
h = G.revolve_bm([(0,-8),(88,-8),(88,8),(0,8)], 64); h.transform(G.axis_matrix((-149.5,CY,CZ),(1,0,0)))
me2 = bpy.data.meshes.new('tmp'); h.to_mesh(me2); h.free(); b.from_mesh(me2); bpy.data.meshes.remove(me2)
# move upper side slots to follow new outline (wall at Y ~ 88..92 for Z 100..140)
b.to_mesh(cs.data); b.free()
# ---- recoil cover v3: r 98, slots inner 39..60, outer 63..85
outer = [(0,7.5),(36,7.5),(37,7.3),(86.5,7.3),(90,6.7),(94,5.1),(96.6,3.0),(97.8,0.9),(98.2,0)]
inner = [(96.8,0),(96.4,0.6),(95.0,2.3),(92.4,4.2),(89.0,5.5),(86.0,5.9),(37,5.9),(36,6.1),(0,6.1)]
b = G.revolve_bm(outer+inner, 120); b.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
rc = bpy.data.objects['part_recoil_starter']
for m in list(rc.modifiers): rc.modifiers.remove(m)
b.to_mesh(rc.data); b.free()
def slot_bm(r0, r1, ang, w0, w1):
    pts = []
    for i in range(6):
        a = math.pi/2 + math.pi*i/5; pts.append((r0 + (w0/2)*math.cos(a), (w0/2)*math.sin(a)))
    for i in range(6):
        a = -math.pi/2 + math.pi*i/5; pts.append((r1 + (w1/2)*math.cos(a), (w1/2)*math.sin(a)))
    bb = G.extrude_bm(pts, 'Z', 3, 12); bb.transform(Matrix.Rotation(ang, 4, 'Z')); return bb
cuts = [slot_bm(39.5, 60, 2*math.pi*(i+0.5)/24, 5.6, 7.8) for i in range(24)] + [slot_bm(63.5, 85, 2*math.pi*i/36, 5.8, 8.0) for i in range(36)]
cb = G.merge_bms(cuts); cb.transform(G.axis_matrix((XF,CY,CZ), (-1,0,0)))
cobj = G.obj_from_bm('cut_recoil_slots', cb, None, coll='gx200_rig')
G.boolean(rc, cobj); G.apply_mods(rc); G.remove('cut_recoil_slots')
rc.data.shade_smooth()
bm = bmesh.new(); bm.from_mesh(rc.data)
for e in bm.edges:
    if len(e.link_faces)==2 and e.calc_face_angle(0) > math.radians(40): e.smooth = False
bm.to_mesh(rc.data); bm.free(); G.wnormal(rc)
print('recoil verts', len(rc.data.vertices))
# logo disc r 32 and screws at r 91.5 (on the rim)
G.revolve('part_recoil_logo_disc', [(0,7.9),(30.5,7.9),(32,7.5),(33,6.6),(28,6.0),(0,6.0)], (XF,CY,CZ), (-1,0,0), 64, 'logo_black')
bms = []
for k in range(6):
    a = math.radians(30 + 60*k)
    bb = G.revolve_bm([(0,0),(5.0,0),(5.0,0.8),(4.2,2.0),(2.2,2.5),(0,2.5)], 20)
    bb.transform(G.axis_matrix((XF-4.0, CY + 91.5*math.cos(a), CZ + 91.5*math.sin(a)), (-1,0,0)))
    bms.append(bb)
G.obj_from_bm('part_recoil_screws', G.merge_bms(bms), 'zinc', smooth=True)
print('ok')


# ===== call 43 2026-10-04T11:01:38.498Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
bpy.data.objects['part_recoil_screws'].location.x = -1.6*MM
# ---- tank upper shell v2: -Y shoulder a bit tighter (photo 07 vs 02b compromise)
X0, X1, Y0, Y1 = -128.0, 110.0, -188.0, 28.0
ZR = 255.0; H = 72.0
rings = []; N = 22
for k in range(N+1):
    dz = H * (1 - (1 - k/N)**1.6) if k < N else H
    iy0 = G.shoulder(dz, H, 4, 5, 50, 50)
    iy1 = G.shoulder(dz, H, 4, 5, 34, 38)
    ix0 = G.shoulder(dz, H, 4, 5, 26, 32)
    ix1 = G.shoulder(dz, H, 4, 5, 26, 32)
    r = max(6, 22 - 10*dz/H)
    rings.append((G.rr_ring(X0+ix0, X1-ix1, Y0+iy0, Y1-iy1, r, 6), ZR + 1 + dz*(H-1)/H))
last = rings[-1][0]
cx = sum(p[0] for p in last)/len(last); cy = sum(p[1] for p in last)/len(last)
for s, dzz in ((0.75, 1.2), (0.45, 2.0)):
    rings.append(([(cx+(x-cx)*s, cy+(y-cy)*s) for (x,y) in last], ZR + H + dzz))
up = bpy.data.objects['part_fuel_tank']
b = G.loft_bm(rings, cap_top=True, cap_bot=False); b.to_mesh(up.data); b.free(); up.data.shade_smooth()
# ---- air cleaner case v3: extends to Y 82 at the top
case_pts = [(82,227),(181,227),(182,200),(181,170),(176,152),(165,143),(140,141),(123,143),(123,190),(82,198)]
G.extrude('part_air_cleaner_case', case_pts, 'X', -133, -86, 'black_plastic', bev=3, segs=2)
cov_pts = [(66,198),(125,198),(125,141),(80,141),(66,156)]
cov = G.extrude('part_carb_cover', cov_pts, 'X', -122, -86, 'black_plastic')
win = G.obj_from_bm('cut_carb_window', G.extrude_bm(G.rrect(100, 168, 34, 40, 5, 4), 'X', -130, -110), None, coll='gx200_rig')
G.boolean(cov, win); G.apply_mods(cov); G.remove('cut_carb_window')
G.hard(cov, 3, 2, 35)
G.render('cam_07', G.OUT+'look/full-07-r5.png', engine='BLENDER_EEVEE', res=(836,822), transparent=False, samples=32)


# ===== call 44 2026-10-04T11:02:26.095Z =====
import bpy, math, time
G = bpy.app.driver_namespace['gx']
pts = G.sample_points(12)
FEAT = {
 '01': [((-156.5,-65,105.5),(490,690)), ((-9,-76,346),(640,72)), ((-78,108,339),(190,112)), ((100,-182,255),(935,242)), ((-121,22,255),(352,292))],
 '09': [((-156.5,-65,105.5),(237,330)), ((-9,-76,346),(375,72)), ((-78,108,339),(200,45)), ((156.5,-65,106),(512,275)), ((100,-182,255),(532,162))],
}
G.FEAT = FEAT
t = time.time()
res = {}
for key in ('01','09'):
    best = None
    for f in (50, 85, 135):
        for el in (12, 18, 24, 30):
            for az in (20, 28, 36, 44):
                r = G.fit_photo_cam(key, az, el, f, pts=pts, iters=5)
                e, out = G.feat_err(key, FEAT[key])
                if best is None or e < best[0]: best = (round(e,1), f, el, az, out, r)
    res[key] = best
    print(key, best)
print('t', time.time()-t, len(pts))


# ===== call 45 2026-10-04T11:02:35.023Z =====
import bpy, math, time
G = bpy.app.driver_namespace['gx']
pts = G.sample_points(12)
def search(key, fs, els, azs, rolls=(0,)):
    best=None
    for f in fs:
        for el in els:
            for az in azs:
                for ro in rolls:
                    r = G.fit_photo_cam(key, az, el, f, roll=ro, pts=pts, iters=5)
                    e, out = G.feat_err(key, G.FEAT[key])
                    if best is None or e < best[0]: best = (round(e,1), f, el, az, ro, out, r)
    return best
b1 = search('01', (60,75,85,100,120), (14,17,20,23), (22,25,28,31,34), (-2,0,2))
print('01', b1)
b9 = search('09', (85,110,135,170), (8,12,16,20), (40,46,52,58,64), (-2,0,2))
print('09', b9)
G.CAM_FIT = {'01': b1, '09': b9}


# ===== call 46 2026-10-04T11:02:54.310Z =====
import bpy
G = bpy.app.driver_namespace['gx']
pts = G.sample_points(3)
G.CAM_PARAMS = {'07': (-2, 2, 160, 0), '01': (25, 17, 100, -2), '09': (58, 16, 170, -2)}
for k,(az,el,f,ro) in G.CAM_PARAMS.items():
    r = G.fit_photo_cam(k, az, el, f, roll=ro, pts=pts, iters=10)
    print(k, r, G.feat_err(k, G.FEAT[k])[0] if k in G.FEAT else '')
# exposure / lights
sc = G.scn()
sc.view_settings.exposure = -0.25
bpy.data.objects['light_key'].data.energy = 150
bpy.data.objects['light_top'].data.energy = 25
G.MATS['white'] = ((0.86, 0.85, 0.81), 0.35, 0.0); G.mat('white')
w = sc.world; bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs['Strength'].default_value = 0.5
# smaller fuel cock tab
G.box('part_fuel_cock_lever', -138, -133, 120, 133, 179, 186, 'white', bev=1.0)
for k,res in (('07',(836,822)),('01',(1000,1000)),('09',(640,480))):
    G.render('cam_'+k, G.OUT+'look/full-%s-r6.png'%k, engine='BLENDER_EEVEE', res=res, transparent=False, samples=32)


# ===== call 47 2026-10-04T11:04:52.405Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
# ---- shroud extension over the flywheel/ignition side (-Y half + bottom), X -104..-38
SUB = [(-20,6),(-100,6),(-120,8),(-138,15),(-153,28),(-163,44),(-169,62),(-171,80),(-171,170),(-168,186),(-161,197),(-150,204),(-135,207),(-20,207)]
bm = G.extrude_bm(SUB, 'X', -104.0, -38.0)
# delete the end caps (+/-X) and the open +Y face at Y=-20
dele = [f for f in bm.faces if abs(f.normal.x) > 0.9 or (f.normal.y > 0.9 and all(abs(v.co.y + 0.020) < 1e-6 for v in f.verts))]
bmesh.ops.delete(bm, geom=dele, context='FACES_ONLY')
ext = G.obj_from_bm('part_fan_shroud_side', bm, 'red', smooth=True)
b = G.bevel(ext, 9, 4, 30); s = G.solidify(ext, 1.6, -1); s.use_even_offset = True; G.wnormal(ext)
# rolled back edge (lip) along X=-38: small half-round bead
# ---- crankcase: -Y side ribs + bosses, bigger top chamfer
bms = []
for x in (-25, 15, 55):
    bms.append(G.extrude_bm([(-156,30),(-152,30),(-152,185),(-156,178)], 'X', x-3, x+3))
bms.append(G.extrude_bm(G.rrect(-30, 120, 26, 26, 8, 4), 'Y', -158, -150))   # governor boss (on -Y face): (x,z)
rib = G.obj_from_bm('part_crankcase_ribs', G.merge_bms(bms), 'alu'); G.hard(rib, 1.5, 2, 35)
cc = bpy.data.objects['part_crankcase']
P = [(-120,8),(28,8),(42,18),(47,45),(48,100),(42,140),(25,175),(5,196),(-10,201),(-118,201),(-140,190),(-150,172),(-152,48),(-146,28),(-134,14)]
b = G.extrude_bm(P, 'X', -112, 99); b.to_mesh(cc.data); b.free(); cc.data.shade_smooth()
# ---- feet: four lugs + crankcase bottom webs
bms = []
for xc in (67.3, -12.7):
    for (yc, w) in ((-131, 50), (31, 46)):
        bms.append(G.extrude_bm(G.rrect(xc, yc, 36, w, 7, 4), 'Z', 0, 12))
        # web from lug up into the crankcase wall
        sgn = -1 if yc < 0 else 1
        y_in = -112 if yc < 0 else 14
        y_out = yc + sgn*14
        bms.append(G.extrude_bm([(y_in, 0), (y_out, 0), (y_out - sgn*6, 12), (y_in, 40)] if sgn<0 else [(y_out,0),(y_in,0),(y_in,40),(y_out - sgn*6,12)], 'X', xc-9, xc+9))
feet = G.obj_from_bm('part_base_feet', G.merge_bms(bms), 'alu')
cut = []
for x in (67.3, -12.7):
    b = G.revolve_bm([(0,-2),(4.5,-2),(4.5,30),(0,30)], 20); b.transform(G.axis_matrix((x,-131,-1),(0,0,1))); cut.append(b)
    cut.append(G.extrude_bm(G.rrect(x, 31, 9, 14, 4.4, 4), 'Z', -2, 30))
cobj = G.obj_from_bm('cut_feet', G.merge_bms(cut), None, coll='gx200_rig')
G.boolean(feet, cobj); G.apply_mods(feet); G.remove('cut_feet')
feet.data.shade_smooth(); G.bevel(feet, 1.5, 2, 35); G.wnormal(feet)
# ---- carb cover without window (solid), keep carb bowl below
cov_pts = [(66,198),(125,198),(125,141),(80,141),(66,156)]
G.extrude('part_carb_cover', cov_pts, 'X', -122, -86, 'black_plastic', bev=3, segs=2)
G.box('part_choke_lever', -141, -133, 96, 112, 186, 192, 'black_plastic', bev=1.0)
# ---- lighting
sc = G.scn(); sc.view_settings.exposure = -0.3
L = bpy.data.objects
L['light_key'].data.energy = 120; L['light_fill'].data.energy = 55; L['light_rim'].data.energy = 90; L['light_top'].data.energy = 0
G.MATS['white'] = ((0.84, 0.83, 0.79), 0.35, 0.0); G.mat('white')
w = sc.world; bgn = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bgn.inputs['Strength'].default_value = 0.3
for k,res in (('01',(1000,1000)),('09',(640,480))):
    G.render('cam_'+k, G.OUT+'look/full-%s-r7.png'%k, engine='BLENDER_EEVEE', res=res, transparent=False, samples=32)
print('ok')


# ===== call 48 2026-10-04T11:06:16.023Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
G.MATS['red'] = ((0.60, 0.018, 0.035), 0.28, 0.0); G.mat('red')
G.MATS['logo_white'] = ((0.92,0.92,0.92), 0.4, 0.0); G.MATS['logo_red'] = ((0.75,0.03,0.05), 0.35, 0.0)
CY, CZ = -65.0, 105.5
def text_mesh(name, body, size, mat, M, extrude=0.3, italic=False, bold=False):
    G.remove(name)
    cu = bpy.data.curves.new(name+'_txt', 'FONT'); cu.body = body; cu.size = size*MM; cu.extrude = extrude*MM
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    if italic: cu.shear = 0.25
    t = bpy.data.objects.new(name+'_tmp', cu); G.link(t, 'gx200_rig'); t.matrix_world = M
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(t.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(t); bpy.data.curves.remove(cu)
    me.name = name; o = bpy.data.objects.new(name, me); G.link(o); o.matrix_world = M
    me.materials.append(G.mat(mat)); return o
G.text_mesh = text_mesh
# frame on the recoil logo disc: x -> -Y, y -> +Z, normal -> -X
R = Matrix(((0,0,-1),(-1,0,0),(0,1,0))).to_4x4()   # columns: x=(0,-1,0), y=(0,0,1), z=(-1,0,0)
def at(y, z, x=-156.95): return Matrix.Translation(Vector((x, y, z))*MM) @ R
o1 = text_mesh('part_logo_honda', 'HONDA', 8.5, 'logo_white', at(CY, CZ+12))
o1.scale = (1.05, 1, 1)
o2 = text_mesh('part_logo_gx', 'GX', 18, 'logo_red', at(CY, CZ-3.5), italic=True)
o3 = text_mesh('part_logo_200', '200', 9.5, 'logo_white', at(CY, CZ-19), italic=True)
# decals on shroud face
G.box('part_shroud_label', -150.1, -149.3, 32, 53, 80, 170, 'logo_white', bev=None)
G.box('part_shroud_rpm_plate', -150.1, -149.3, -6, 40, 175, 188, 'logo_black', bev=None)
# muffler stay strap to head
G.box('part_muffler_stay', 82, 88, 92, 110, 198, 240, 'black_paint', bev=1.0)
print(R)


# ===== call 49 2026-10-04T11:06:23.015Z =====
import bpy
G = bpy.app.driver_namespace['gx']
G.render('cam_07', G.OUT+'look/full-07-r8.png', engine='BLENDER_EEVEE', res=(836,822), transparent=False, samples=32)


# ===== call 50 2026-10-04T11:06:47.468Z =====
import bpy
G = bpy.app.driver_namespace['gx']
G.MATS['white'] = ((0.80, 0.79, 0.75), 0.4, 0.0); G.mat('white')
for k in ['02a','02b','02c','02d']:
    G.render('cam_'+k, G.OUT+'look/full-%s-r2.png'%k)
print('ok')


# ===== call 51 2026-10-04T11:07:42.001Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
# fuel cap: 6 scallops
CX, CYc = -9.0, -76.0
prof = [(0,0),(35.5,0),(36,1.5),(38.0,3.5),(38.5,6),(38.5,17),(37.8,19.0),(36.5,20.3),(30,20.9),(12,21.3),(0,21.4)]
cap = G.revolve('part_fuel_cap', prof, (CX,CYc,325.0), (0,0,1), 96, 'chrome')
cuts = []
for k in range(6):
    a = math.radians(30 + 60*k)
    b = G.revolve_bm([(0,-1),(8.5,-1),(8.5,30),(0,30)], 24)
    b.transform(Matrix.Translation(Vector((CX + 40.5*math.cos(a), CYc + 40.5*math.sin(a), 333))*MM)); cuts.append(b)
c = G.obj_from_bm('cut_cap', G.merge_bms(cuts), None, coll='gx200_rig')
G.boolean(cap, c); G.apply_mods(cap); G.remove('cut_cap')
cap.data.shade_smooth(); G.bevel(cap, 0.8, 2, 40); G.wnormal(cap)
# fuel gauge on tank top (X 70, Y -80)
G.revolve('part_fuel_gauge', [(0,4.2),(9,4.2),(11,3.5),(12.5,1.5),(13,0),(0,0)], (70,-80,325.5), (0,0,1), 32, 'black_plastic')
G.revolve('part_fuel_gauge_lens', [(0,4.4),(7.5,4.4),(7.5,4.0),(0,4.0)], (70,-80,325.5), (0,0,1), 32, 'chrome')
# exhaust flange on head top surface
PX, PY = 45.0, 88.0
G.revolve('part_exhaust_pipe', [(0,0),(12,0),(12,30),(0,30)], (PX,PY,210), (0,0,1), 32, 'black_paint')
G.extrude('part_exhaust_flange', G.rrect(PX, PY, 30, 60, 9, 4), 'Z', 208, 214, 'black_paint', bev=1.5)
bms = []
for dy in (-21, 21):
    b = G.hexbolt_bm((PX, PY+dy, 214), (0,0,1), 10, 5); bms.append(b)
G.obj_from_bm('part_exhaust_nuts', G.merge_bms(bms), 'zinc')
G.revolve('part_exhaust_port', [(0,0),(16,0),(16,48),(0,48)], (PX,PY,162), (0,0,1), 32, 'alu')
# perspective check cam from PTO/muffler side
cd = bpy.data.cameras.get('cam_iso_pto') or bpy.data.cameras.new('cam_iso_pto')
cam = bpy.data.objects.get('cam_iso_pto') or bpy.data.objects.new('cam_iso_pto', cd)
if cam.name not in bpy.data.collections['gx200_rig'].objects: G.link(cam, 'gx200_rig')
cd.lens = 70; cd.clip_start = 0.01
T = Vector((0,0,0.17)); pos = T + Vector((1.05, 0.95, 0.55))
cam.location = pos; cam.rotation_euler = (T-pos).to_track_quat('-Z','Y').to_euler()
G.render('cam_iso_pto', G.OUT+'look/iso_pto-r1.png', engine='BLENDER_EEVEE', res=(1000,900), transparent=False, samples=32)


# ===== call 52 2026-10-04T11:08:07.875Z =====
import bpy, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
o = bpy.data.objects['part_ohv_letters']
M = o.matrix_world.to_3x3()
print('text x ->', [round(v,3) for v in M @ Vector((1,0,0))], 'text y ->', [round(v,3) for v in M @ Vector((0,1,0))], 'normal', [round(v,3) for v in M @ Vector((0,0,1))])


# ===== call 53 2026-10-04T11:08:27.486Z =====
import bpy, math
from mathutils import Vector
G = bpy.app.driver_namespace['gx']; MM = G.MM
G.MATS['alu'] = ((0.56, 0.56, 0.55), 0.5, 0.8); G.mat('alu')
G.MATS['zinc'] = ((0.72, 0.71, 0.66), 0.35, 1.0); G.mat('zinc')
# thinner tank bracket (stamped strap) at PTO end
G.extrude('part_tank_bracket', [(-168,196),(30,196),(30,207),(-168,207)], 'X', 96, 100, 'black_paint', bev=1.0)
G.obj_from_bm('part_tank_bracket_bolts', G.merge_bms([G.hexbolt_bm((100, y, 201.5), (1,0,0), 10, 4.5) for y in (-156, 18)]), 'zinc')
# bbox
import mathutils
mn = mathutils.Vector((1e9,)*3); mx = -mn
dg = bpy.context.evaluated_depsgraph_get()
for o in bpy.data.collections['gx200_parts'].objects:
    if o.type != 'MESH' or o.hide_render: continue
    oe = o.evaluated_get(dg); me = oe.to_mesh()
    for v in me.vertices:
        w = o.matrix_world @ v.co
        mn = mathutils.Vector(map(min, mn, w)); mx = mathutils.Vector(map(max, mx, w))
    oe.to_mesh_clear()
print('bbox mm', [round(v*1000,1) for v in mn], [round(v*1000,1) for v in mx], 'size', [round((b-a)*1000,1) for a,b in zip(mn,mx)])
print(len(bpy.data.collections['gx200_parts'].objects))


# ===== call 54 2026-10-04T11:08:40.962Z =====
import bpy, math
from mathutils import Vector
G = bpy.app.driver_namespace['gx']; MM = G.MM
EX, EZ = 67.2, 270.0
G.revolve('part_muffler_outlet', [(9.5,0),(21,0),(21,1.8),(19.5,2.6),(13.8,2.6),(13.0,2.8),(11.0,2.8),(11.0,-3)], (EX, 185.2, EZ), (0,1,0), 48, 'black_paint')
bms = []
for k in range(4):
    a = math.radians(45 + 90*k)
    b = G.revolve_bm([(0,0),(3.8,0),(3.8,1.5),(2.8,2.6),(0,2.6)], 12)
    b.transform(G.axis_matrix((EX + 26*math.cos(a), 185.3, EZ + 26*math.sin(a)), (0,1,0))); bms.append(b)
G.obj_from_bm('part_muffler_screws', G.merge_bms(bms), 'zinc', smooth=True)
def bbox(exclude=()):
    import mathutils
    mn = mathutils.Vector((1e9,)*3); mx = -mn
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.collections['gx200_parts'].objects:
        if o.type != 'MESH' or o.hide_render or o.name in exclude: continue
        oe = o.evaluated_get(dg); me = oe.to_mesh()
        for v in me.vertices:
            w = o.matrix_world @ v.co
            mn = mathutils.Vector(map(min, mn, w)); mx = mathutils.Vector(map(max, mx, w))
        oe.to_mesh_clear()
    return [round(v*1000,1) for v in mn], [round(v*1000,1) for v in mx], [round((b-a)*1000,1) for a,b in zip(mn,mx)]
G.bbox = bbox
print('all', bbox())
print('no handle', bbox(('part_recoil_handle','part_recoil_handle_stem')))


# ===== call 55 2026-10-04T11:08:47.311Z =====
import bpy
G = bpy.app.driver_namespace['gx']
sc = G.scn()
bpy.data.libraries.write(G.OUT + 'gx200.blend', {sc}, fake_user=True, path_remap='ABSOLUTE')
import os
print(os.path.getsize(G.OUT + 'gx200.blend'))


# ===== call 56 2026-10-04T11:09:13.188Z =====
import bpy
G = bpy.app.driver_namespace['gx']
for k in ['02b','02c']:
    G.render('cam_'+k, G.OUT+'look/muffler-%s-r2.png'%k, engine='BLENDER_EEVEE', transparent=True, samples=24)
G.render('cam_09', G.OUT+'look/full-09-r8.png', engine='BLENDER_EEVEE', res=(640,480), transparent=False, samples=32)
G.render('cam_01', G.OUT+'look/full-01-r8.png', engine='BLENDER_EEVEE', res=(1000,1000), transparent=False, samples=32)


# ===== call 57 2026-10-04T11:10:39.622Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
head = bpy.data.objects['part_cylinder_head']
b = G.plate_bm(G.rrect(0, -32, 118, 100, 16, 6), 138, 206); b.to_mesh(head.data); b.free(); head.data.shade_smooth()
hf = bpy.data.objects['part_head_fins']
b = G.plate_bm(G.rrect(0, -27, 126, 118, 16, 6), 150, 152.2); b.to_mesh(hf.data); b.free(); hf.data.shade_smooth()
PX, PY = 50.0, 92.0
G.revolve('part_exhaust_pipe', [(0,0),(12,0),(12,44),(0,44)], (PX,PY,196), (0,0,1), 32, 'black_paint')
G.extrude('part_exhaust_flange', G.rrect(PX, PY, 28, 62, 9, 4), 'Z', 194, 200, 'black_paint', bev=1.5)
G.obj_from_bm('part_exhaust_nuts', G.merge_bms([G.hexbolt_bm((PX, PY+dy, 200), (0,0,1), 10, 5) for dy in (-22, 22)]), 'zinc')
G.revolve('part_exhaust_port', [(0,0),(17,0),(17,34),(0,34)], (PX,PY,162), (0,0,1), 32, 'alu')
# stay strap: muffler -> head +X face
G.extrude('part_muffler_stay', [(122,240),(146,240),(146,160),(140,142),(128,142),(122,160)], 'X', 87, 90.5, 'black_paint', bev=1.0)
G.obj_from_bm('part_muffler_stay_bolt', G.hexbolt_bm((90.5, 134, 151), (1,0,0), 10, 5), 'zinc')
# spark plug: move to new head top
G.render('cam_02b', G.OUT+'look/muffler-02b-r3.png', engine='BLENDER_EEVEE', transparent=True, samples=24)


# ===== call 58 2026-10-04T11:11:05.261Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
X0, X1, Y0, Y1 = 21.5, 134.0, 44.0, 188.0
# body taller (to 308), re-cut slots
body = G.box('part_muffler', X0+2, X1-2, Y0+2, Y1-2, 237, 308, 'black_paint')
cuts = []
for (y0, y1) in [(67, 113), (120, 165)]:
    for zc in (291, 282, 273):
        cuts.append(G.extrude_bm(G.rrect((y0+y1)/2, zc, y1-y0, 6.0, 2.9, 3), 'X', X1-6, X1+5))
cuts.append(G.extrude_bm(G.rrect(149.5, 263, 31, 6.0, 2.9, 3), 'X', X1-6, X1+5))
for zc in (293, 284, 275, 266, 257):
    cuts.append(G.extrude_bm(G.rrect(102, zc, 24, 6.0, 2.9, 3), 'Y', Y1-6, Y1+5))
for zc in (291, 282, 273):
    cuts.append(G.extrude_bm(G.rrect(41, zc, 13, 6.0, 2.9, 3), 'Y', Y1-6, Y1+5))
c = G.obj_from_bm('cut_muffler_slots', G.merge_bms(cuts), None, coll='gx200_rig')
body.modifiers.clear(); G.bevel(body, 4, 2, 35)
G.boolean(body, c); G.apply_mods(body); G.remove('cut_muffler_slots')
body.data.shade_smooth(); G.bevel(body, 0.8, 1, 35); G.wnormal(body)
# embossed swoosh rib on +X face below slots
G.extrude('part_muffler_rib', [(62,257),(150,257),(158,252),(168,252),(168,249.5),(157,249.5),(149,254.5),(62,254.5)], 'X', X1-2.2, X1-0.6, 'black_paint', bev=0.5)
# shield: skirt bottom raised to 305
cap = bpy.data.objects['part_muffler_shield']
rings = []
for (z, ins, r) in [(305, 0, 8), (312, 0, 8), (314.5, 0.6, 8), (326, 13.5, 6), (328, 15.5, 5)]:
    rings.append((G.rr_ring(X0+ins, X1-ins, Y0+ins, Y1-ins, r, 4), z))
b = G.loft_bm(rings, cap_top=True, cap_bot=False)
cuts = []
for i in range(9):
    y = 63 + i*(169-63)/8
    for xc in (X1-7, X0+7): cuts.append(G.box_bm(xc-6, xc+6, y-3.25, y+3.25, 316, 335))
for i in range(7):
    x = 42 + i*(114-42)/6
    for yc in (Y1-7, Y0+7): cuts.append(G.box_bm(x-3.25, x+3.25, yc-6, yc+6, 316, 335))
tmp = G.obj_from_bm('tmp_shield', b, 'black_paint', coll='gx200_rig')
c = G.obj_from_bm('cut_muffler_louvres', G.merge_bms(cuts), None, coll='gx200_rig')
G.boolean(tmp, c); G.apply_mods(tmp); G.remove('cut_muffler_louvres')
old = cap.data; cap.data = tmp.data; cap.data.name = 'part_muffler_shield'
bpy.data.objects.remove(tmp); 
if old.users == 0: bpy.data.meshes.remove(old)
cap.modifiers.clear(); cap.data.shade_smooth(); G.solidify(cap, 1.2, -1); G.wnormal(cap)
print(len(cap.data.vertices), len(body.data.vertices))


# ===== call 59 2026-10-04T11:11:15.030Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
X0, X1, Y0, Y1 = 21.5, 134.0, 44.0, 188.0
cap = bpy.data.objects['part_muffler_shield']
rings = []
for (z, ins, r) in [(305, 0, 8), (312, 0, 8), (314.5, 0.6, 8), (326, 13.5, 6), (328, 15.5, 5)]:
    rings.append((G.rr_ring(X0+ins, X1-ins, Y0+ins, Y1-ins, r, 4), z))
b = G.loft_bm(rings, cap_top=True, cap_bot=False)
cuts = []
for i in range(9):
    y = 63 + i*(169-63)/8
    for xc in (X1-7, X0+7): cuts.append(G.box_bm(xc-6, xc+6, y-3.25, y+3.25, 316, 335))
for i in range(7):
    x = 42 + i*(114-42)/6
    for yc in (Y1-7, Y0+7): cuts.append(G.box_bm(x-3.25, x+3.25, yc-6, yc+6, 316, 335))
cap.modifiers.clear()
b.to_mesh(cap.data); b.free()
c = G.obj_from_bm('cut_muffler_louvres', G.merge_bms(cuts), None, coll='gx200_rig')
G.boolean(cap, c, solver='EXACT'); G.apply_mods(cap); G.remove('cut_muffler_louvres')
cap.data.shade_smooth(); G.solidify(cap, 1.2, -1); G.wnormal(cap)
print(len(cap.data.vertices))
for k in ['02b','02c']:
    G.render('cam_'+k, G.OUT+'look/muffler-%s-r4.png'%k, engine='BLENDER_EEVEE', transparent=True, samples=24)


# ===== call 60 2026-10-04T11:11:35.119Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
EX, EZ = 67.2, 270.0
G.revolve('part_muffler_outlet', [(13.5,-3),(13.5,0),(22,0),(22,1.8),(20.5,2.6),(16.5,2.6),(16.5,7.5),(15.6,8.2),(14.6,8.2),(13.8,7.6)], (EX, 185.2, EZ), (0,1,0), 48, 'black_paint')
# rounder shield top: replace hard chamfer by a 3-step curve, skirt bottom 303
from mathutils import Vector
X0, X1, Y0, Y1 = 21.5, 134.0, 44.0, 188.0
print('ok')


# ===== call 61 2026-10-04T11:11:46.154Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
EX, EZ = 67.2, 270.0
G.revolve('part_muffler_outlet', [(14,-6),(14,0),(22,0),(22,1.0),(21,1.6),(17,1.6),(16.6,2.6),(15.0,2.7),(14.2,2.2)], (EX, 185.2, EZ), (0,1,0), 48, 'black_paint')
# dark inner hole disc to suggest depth
G.revolve('part_muffler_outlet_hole', [(0,-5),(14,-5),(14,-4.5),(0,-4.5)], (EX, 185.2, EZ), (0,1,0), 32, 'rubber')
print(G.bbox(('part_recoil_handle','part_recoil_handle_stem')))
G.render('cam_01', G.OUT+'look/full-01-r9.png', engine='BLENDER_EEVEE', res=(1000,1000), transparent=False, samples=32)


# ===== call 62 2026-10-04T11:12:13.730Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
G.MATS['black_plastic'] = ((0.035, 0.037, 0.04), 0.45, 0.0); G.mat('black_plastic')
# lid v2: flared skirt with lip, domed top
X0, X1, Y0, Y1 = -134.0, -26.0, 42.0, 177.0
rings = []
for (z, ins, r) in [(222.5, -1.2, 13), (224.5, -1.2, 13), (226, -0.4, 12), (256, 1.0, 12), (258.5, 1.4, 12)]:
    rings.append((G.rr_ring(X0+ins, X1-ins, Y0+ins, Y1-ins, r, 6), z))
H = 323.0 - 259.0
for k in range(0, 13):
    t = k/12
    z = 259.0 + H*t if k < 12 else 323.0
    dz = z - 259.0
    ins = 4.5 + 1.0*t + G.shoulder(dz, H, 0, 0, 13, 15)
    rings.append((G.rr_ring(X0+ins, X1-ins, Y0+ins, Y1-ins, max(5, 12 - 4*t), 6), z))
last = rings[-1][0]
cx = sum(p[0] for p in last)/len(last); cy = sum(p[1] for p in last)/len(last)
rings.append(([(cx+(x-cx)*0.6, cy+(y-cy)*0.6) for (x,y) in last], 324.5))
lid = bpy.data.objects['part_air_cleaner']
b = G.loft_bm(rings); b.to_mesh(lid.data); b.free(); lid.data.shade_smooth()
KX, KY = -78.0, 108.0
G.revolve('part_air_cleaner_knob_base', [(0,7),(14,7),(19,6),(23,3.5),(26,1.0),(27,0),(0,0)], (KX,KY,323.0), (0,0,1), 48, 'black_plastic')
kn = bpy.data.objects['part_air_cleaner_knob']; kn.location.z = 3.0*MM
# narrower lower column (Y 132..181)
case_pts = [(82,227),(181,227),(182,200),(181,170),(176,152),(165,143),(145,141),(132,143),(132,190),(82,198)]
G.extrude('part_air_cleaner_case', case_pts, 'X', -133, -86, 'black_plastic', bev=3, segs=2)
cov_pts = [(66,198),(132,198),(132,170),(80,166),(66,172)]
G.extrude('part_carb_cover', cov_pts, 'X', -122, -86, 'black_plastic', bev=2.5, segs=2)
# control panel plate with choke + fuel-cock levers in front of carb
G.box('part_control_plate', -126, -122, 70, 132, 160, 168, 'black_plastic', bev=1.0)
G.box('part_fuel_cock_lever', -136, -126, 112, 130, 162, 168, 'white', bev=1.0)
G.box('part_choke_lever', -136, -126, 84, 100, 175, 181, 'black_plastic', bev=1.0)
print('ok')


# ===== call 63 2026-10-04T11:12:22.653Z =====
import bpy
G = bpy.app.driver_namespace['gx']; MM = G.MM
bpy.data.objects['part_air_cleaner_knob'].location.z = -1.0*MM
print(G.bbox(('part_recoil_handle','part_recoil_handle_stem')))
import mathutils
dg = bpy.context.evaluated_depsgraph_get()
o = bpy.data.objects['part_air_cleaner_knob']; me = o.evaluated_get(dg).to_mesh()
print('knob top', max((o.matrix_world @ v.co).z for v in me.vertices)*1000)
for k,res in (('07',(836,822)),('01',(1000,1000)),('09',(640,480))):
    G.render('cam_'+k, G.OUT+'look/full-%s-r10.png'%k, engine='BLENDER_EEVEE', res=res, transparent=False, samples=32)


# ===== call 64 2026-10-04T11:12:56.704Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
# governor arm on -Y side boss (X -30, Z 120), lever up toward the tank bottom
a = Vector((-30, -160, 120)); b2 = Vector((-60, -162, 182))
dv = b2 - a; L = dv.length
bm = G.box_bm(-5, 5, -1.5, 1.5, 0, L); q = Vector((0,0,1)).rotation_difference(dv.normalized())
bm.transform(Matrix.Translation(a*MM) @ q.to_matrix().to_4x4())
o = G.obj_from_bm('part_governor_arm', bm, 'zinc'); G.hard(o, 0.8, 2, 35)
G.obj_from_bm('part_governor_arm_nut', G.hexbolt_bm((-30, -158, 120), (0,-1,0), 10, 5), 'zinc')
G.tube('part_governor_spring', [(-60,-163,182),(-80,-150,196),(-104,-120,204)], 1.8, 'steel', 8)
# engine switch wire (black) from switch down along shroud edge into crankcase side
G.tube('part_switch_wire', [(-120,-176,150),(-100,-170,140),(-70,-160,128),(-40,-158,110)], 2.2, 'rubber', 10)
# dipstick-style breather boss & bolts on -Y face
G.obj_from_bm('part_crankcase_side_bolts', G.merge_bms([G.hexbolt_bm((x, -152, z), (0,-1,0), 10, 5) for (x,z) in [(10,180),(60,180),(-70,60),(60,40)]]), 'zinc')
for k,res in (('09',(640,480)),):
    G.render('cam_'+k, G.OUT+'look/full-%s-r11.png'%k, engine='BLENDER_EEVEE', res=res, transparent=False, samples=32)


# ===== call 65 2026-10-04T11:13:28.722Z =====
import bpy, time
G = bpy.app.driver_namespace['gx']
t = time.time()
for k in ['02a','02b','02c','02d']:
    G.render('cam_'+k, G.OUT+'look/final-%s-r1.png'%k, engine='BLENDER_EEVEE', transparent=True, samples=32)
for k,res in (('07',(836,822)),('09',(640,480)),('01',(1000,1000))):
    G.render('cam_'+k, G.OUT+'look/final-%s-r1.png'%k, engine='BLENDER_EEVEE', res=res, transparent=True, samples=48)
print(time.time()-t)


# ===== call 66 2026-10-04T11:15:02.721Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
# engine switch closer to shroud wall (07: Y -152..-174)
G.box('part_engine_switch', -146, -124, -176, -166, 146, 182, 'red', bev=2.5)
G.box('part_engine_switch_toggle', -140, -130, -180, -175, 158, 170, 'red', bev=1.2)
# embossed raised plateau on tank top around the filler (02d oval: X -60..60, Y -130..-10), 2 mm high
pts = []
for i in range(48):
    a = 2*math.pi*i/48
    pts.append((-4 + 66*math.cos(a), -74 + 52*math.sin(a)))
rings = [(pts, 320.0), ([(x*1.0, y) for (x,y) in pts], 327.3)]
cx, cy = -4, -74
inner = [(cx+(x-cx)*0.96, cy+(y-cy)*0.96) for (x,y) in pts]
rings.append((inner, 328.3))
o = G.obj_from_bm('part_fuel_tank_emboss', G.loft_bm(rings), 'white', smooth=True)
G.wnormal(o)
G.MATS['white'] = ((0.76, 0.75, 0.71), 0.38, 0.0); G.mat('white')
# check top of tank under the emboss
dg = bpy.context.evaluated_depsgraph_get()
t = bpy.data.objects['part_fuel_tank']; me = t.evaluated_get(dg).to_mesh()
print('tank top z', max((t.matrix_world@v.co).z for v in me.vertices)*1000)


# ===== call 67 2026-10-04T11:15:13.401Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']; MM = G.MM
pts = [(-4 + 66*math.cos(2*math.pi*i/48), -74 + 52*math.sin(2*math.pi*i/48)) for i in range(48)]
cx, cy = -4, -74
rings = [(pts, 322.0), (pts, 329.6), ([(cx+(x-cx)*0.95, cy+(y-cy)*0.95) for (x,y) in pts], 330.6)]
o = G.obj_from_bm('part_fuel_tank_emboss', G.loft_bm(rings), 'white', smooth=True); G.bevel(o, 1.2, 2, 30); G.wnormal(o)
G.revolve('part_fuel_filler_neck', [(30,0),(44,0),(43,2.0),(40,3.8),(35,4.4),(30,4.4)], (-9,-76,330.0), (0,0,1), 64, 'white')
print(G.bbox(('part_recoil_handle','part_recoil_handle_stem')))
for k in ['02a','02b','02c','02d']:
    G.render('cam_'+k, G.OUT+'look/final-%s-r2.png'%k, engine='BLENDER_EEVEE', transparent=True, samples=32)
for k,res in (('07',(836,822)),('09',(640,480)),('01',(1000,1000))):
    G.render('cam_'+k, G.OUT+'look/final-%s-r2.png'%k, engine='BLENDER_EEVEE', res=res, transparent=True, samples=48)


# ===== call 68 2026-10-04T11:15:39.810Z =====
import bpy, math
from mathutils import Vector
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
# floor
G.remove('stage_floor')
import bmesh
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=2.0)
me = bpy.data.meshes.new('stage_floor'); bm.to_mesh(me); bm.free()
fl = bpy.data.objects.new('stage_floor', me); G.link(fl, 'gx200_rig')
fm = bpy.data.materials.get('gx_floor') or bpy.data.materials.new('gx_floor')
try: fm.use_nodes = True
except Exception: pass
bs = next(n for n in fm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value = (0.55, 0.56, 0.58, 1); bs.inputs['Roughness'].default_value = 0.6
me.materials.append(fm)
fl.location.z = -0.0002
def persp_cam(name, az, el, lens, target=(0,0,170), dist=None):
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, cd)
    if cam.name not in bpy.data.collections['gx200_rig'].objects: G.link(cam, 'gx200_rig')
    cd.type = 'PERSP'; cd.lens = lens; cd.clip_start = 0.01; cd.clip_end = 30; cd.shift_x = cd.shift_y = 0
    a, e = math.radians(az), math.radians(el)
    d = Vector((-math.cos(e)*math.cos(a), -math.cos(e)*math.sin(a), math.sin(e)))
    T = Vector(target)*MM
    cam.location = T + d*dist
    cam.rotation_euler = (-d).to_track_quat('-Z','Y').to_euler()
    return cam
persp_cam('cam_hero', 32, 20, 85, dist=2.05)
persp_cam('cam_hero_pto', 215, 22, 85, dist=2.05)
persp_cam('cam_front', 0, 4, 135, dist=3.15)
persp_cam('cam_side', -90, 4, 135, dist=3.15)     # from +Y (muffler side)
persp_cam('cam_top', 0, 89.9, 135, target=(0,0,150), dist=3.6)
bpy.data.objects['cam_top'].rotation_euler.z += math.radians(90)
for c in ('cam_front','cam_side','cam_top'): bpy.data.objects[c].data.lens = 120
sc.view_settings.exposure = -0.35
outs = {}
for name, res in (('hero',(1600,1300)),('hero_pto',(1600,1300)),('front',(1400,1300)),('side',(1400,1300)),('top',(1300,1400))):
    G.render('cam_'+name, G.OUT+'renders/gx200-%s.png'%name, engine='BLENDER_EEVEE', res=res, transparent=False, samples=64)
print('ok')


# ===== call 69 2026-10-04T11:16:01.024Z =====
import bpy, math
from mathutils import Vector
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
fm = bpy.data.materials['gx_floor']; bs = next(n for n in fm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value = (0.16, 0.165, 0.175, 1); bs.inputs['Roughness'].default_value = 0.7
bpy.data.objects['stage_floor'].scale = (3,3,1)
w = sc.world; bgn = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bgn.inputs['Color'].default_value = (0.32, 0.33, 0.35, 1); bgn.inputs['Strength'].default_value = 0.6
sc.view_settings.exposure = -0.2
def place(name, az, el, dist, target=(0,0,165)):
    cam = bpy.data.objects[name]
    a, e = math.radians(az), math.radians(el)
    d = Vector((-math.cos(e)*math.cos(a), -math.cos(e)*math.sin(a), math.sin(e)))
    T = Vector(target)*MM
    cam.location = T + d*dist; cam.rotation_euler = (-d).to_track_quat('-Z','Y').to_euler()
place('cam_hero', 32, 22, 1.55); place('cam_hero_pto', 215, 24, 1.55)
place('cam_front', 0, 5, 2.4); place('cam_side', -90, 5, 2.4)
for name, res in (('hero',(1600,1300)),('front',(1400,1300))):
    G.render('cam_'+name, G.OUT+'renders/gx200-%s.png'%name, engine='BLENDER_EEVEE', res=res, transparent=False, samples=64)


# ===== call 70 2026-10-04T11:16:15.428Z =====
import bpy
G = bpy.app.driver_namespace['gx']
sc = G.scn()
sc.view_settings.exposure = -0.55
L = bpy.data.objects
L['light_key'].data.energy = 100; L['light_fill'].data.energy = 60; L['light_rim'].data.energy = 110
G.MATS['chrome'] = ((0.85,0.85,0.87), 0.14, 1.0); G.mat('chrome')
try: sc.view_settings.look = 'Medium High Contrast'
except TypeError as e: print('look', e)
print(sc.view_settings.look)
for name, res in (('hero',(1600,1300)),('hero_pto',(1600,1300)),('front',(1400,1300)),('side',(1400,1300)),('top',(1300,1400))):
    G.render('cam_'+name, G.OUT+'renders/gx200-%s.png'%name, engine='BLENDER_EEVEE', res=res, transparent=False, samples=64)


# ===== call 71 2026-10-04T11:16:45.152Z =====
import bpy, math
from mathutils import Vector, Euler
G = bpy.app.driver_namespace['gx']; MM = G.MM
bpy.data.objects['stage_floor'].scale = (25,25,1)
def place(name, az, el, dist, target=(0,0,172)):
    cam = bpy.data.objects[name]
    a, e = math.radians(az), math.radians(el)
    d = Vector((-math.cos(e)*math.cos(a), -math.cos(e)*math.sin(a), math.sin(e)))
    cam.location = Vector(target)*MM + d*dist; cam.rotation_euler = (-d).to_track_quat('-Z','Y').to_euler()
place('cam_front', 0, 6, 1.75); place('cam_side', -90, 6, 1.75)
for n in ('cam_front','cam_side'): bpy.data.objects[n].data.lens = 120
top = bpy.data.objects['cam_top']; top.data.type = 'ORTHO'; top.data.ortho_scale = 0.50
top.location = Vector((0, 0, 1.5)); top.rotation_euler = Euler((0, 0, math.radians(180)))
for name, res in (('front',(1400,1300)),('side',(1400,1300)),('top',(1300,1400))):
    G.render('cam_'+name, G.OUT+'renders/gx200-%s.png'%name, engine='BLENDER_EEVEE', res=res, transparent=False, samples=64)


# ===== call 72 2026-10-04T11:17:05.679Z =====
import bpy
G = bpy.app.driver_namespace['gx']
sc = G.scn()
mn, mx, size = G.bbox(('part_recoil_handle','part_recoil_handle_stem'))
mn2, mx2, size2 = G.bbox()
tgt = (313, 376, 346)
print('bbox (không tính tay giật) mm:', size, 'sai lệch %:', [round((s-t)/t*100,2) for s,t in zip(size,tgt)])
print('bbox (tính tay giật) mm:', size2)
parts = [o for o in bpy.data.collections['gx200_parts'].objects]
print('objects in gx200_parts:', len(parts), 'tris:', sum(len(o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.loop_triangles) if o.type=='MESH' else 0 for o in parts))
nonascii = [o.name for o in parts if not o.name.isascii() or not o.name.startswith('part_')]
print('bad names:', nonascii)
# remove leftover cutter
print([o.name for o in bpy.data.collections['gx200_rig'].objects if o.name.startswith('cut_')])
bpy.data.libraries.write(G.OUT + 'gx200.blend', {sc}, fake_user=True, path_remap='ABSOLUTE')
import os; print('saved', os.path.getsize(G.OUT + 'gx200.blend'))
print('other scene untouched:', [o.name for o in bpy.data.scenes['Scene'].objects])


# ===== call 73 2026-10-04T11:17:11.211Z =====
import bpy
G = bpy.app.driver_namespace['gx']
with bpy.data.libraries.load(G.OUT + 'gx200.blend') as (src, dst):
    print('scenes', src.scenes, 'objects', len(src.objects), 'materials', len(src.materials), 'cameras', len(src.cameras))


# ===== call 74 2026-10-04T11:17:16.029Z =====
import bpy
print([l.filepath for l in bpy.data.libraries])


# ===== call 75 2026-10-04T11:17:41.008Z =====
import bpy
G = bpy.app.driver_namespace['gx']
fl = bpy.data.objects['stage_floor']; fl.hide_render = True
for k in ['02a','02b','02c','02d']:
    G.render('cam_'+k, G.OUT+'look/final-%s-r3.png'%k, engine='BLENDER_EEVEE', transparent=True, samples=32)
for k,res in (('07',(836,822)),('09',(640,480)),('01',(1000,1000))):
    G.render('cam_'+k, G.OUT+'look/final-%s-r3.png'%k, engine='BLENDER_EEVEE', res=res, transparent=True, samples=48)
fl.hide_render = False
bpy.data.libraries.write(G.OUT + 'gx200.blend', {G.scn()}, fake_user=True, path_remap='ABSOLUTE')
print('ok')


# ===== call 76 2026-10-04T12:03:19.177Z =====
import bpy
print(bpy.app.version_string, [s.name for s in bpy.data.scenes], bpy.context.window.scene.name)
G = bpy.app.driver_namespace.get('gx')
print('helpers', G is not None)
sc = bpy.data.scenes['gx200']
print(len(bpy.data.collections['gx200_parts'].objects), sc.frame_start, sc.frame_end, sc.render.fps)
print([i.identifier for i in sc.render.image_settings.bl_rna.properties['file_format'].enum_items])
print([o.name for o in bpy.data.collections['gx200_parts'].objects if o.animation_data])
print(sorted(o.name for o in bpy.data.collections['gx200_parts'].objects))


# ===== call 77 2026-10-04T12:04:23.146Z =====
import bpy, bmesh, math
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
sc.frame_set(1)
CY, CZ = -65.0, 106.0
# ---- flywheel fan with visible blades (rotation must read through recoil slots)
G.revolve('part_flywheel_fan', [(0,0),(88,0),(88,3),(27,3),(27,25),(0,25)], (-121.0,CY,105.5), (-1,0,0), 64, 'black_paint')
bms = []
for i in range(18):
    a = 2*math.pi*i/18
    b = G.box_bm(-146, -124, -1.6, 1.6, 27, 86)       # local: x=X, y=tangential, z=radial
    rot = Matrix.Rotation(a, 4, 'X')
    b.transform(Matrix.Translation(Vector((0, CY, 105.5))*MM) @ rot)
    bms.append(b)
bl = G.obj_from_bm('part_flywheel_fan_blades', G.merge_bms(bms), 'alu'); G.hard(bl, 0.6, 1, 35)
# ---- rope (unit length along local z, scaled in z = pulled length in mm)
GUIDE = Vector((-150.5, 13.0, 110.0))
PULL = Vector((-1.0, 0.22, 0.30)).normalized()
G.PULL = PULL; G.GUIDE = GUIDE
b = G.revolve_bm([(0,0),(2.2,0),(2.2,1.0),(0,1.0)], 12)    # 1 mm tall in local z
rope = G.obj_from_bm('part_recoil_rope', b, 'logo_white', smooth=True)
G.MATS['rope'] = ((0.85,0.84,0.78), 0.8, 0.0); rope.data.materials[0] = G.mat('rope')
rope.matrix_world = Matrix.Translation(GUIDE*MM) @ Vector((0,0,1)).rotation_difference(PULL).to_matrix().to_4x4()
rope.scale = (1, 1, 0.01)
# ---- empties
def empty(name, loc_mm, parent=None, shape='PLAIN_AXES', size=0.05):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, None); G.link(o, 'gx200_rig')
    o.empty_display_type = shape; o.empty_display_size = size
    o.parent = parent; o.matrix_parent_inverse = Matrix.Identity(4)
    o.location = Vector(loc_mm)*MM; o.rotation_euler = (0,0,0); o.scale = (1,1,1)
    return o
turn = empty('rig_turn', (0,0,0), None, 'CIRCLE', 0.25)
vib = empty('rig_vib', (0,0,0), turn, 'CUBE', 0.02)
crank = empty('rig_crank', (0, CY, CZ), vib, 'SINGLE_ARROW', 0.08)
crank.rotation_mode = 'XYZ'
pull = empty('rig_pull', (0,0,0), vib, 'SPHERE', 0.02)
bpy.context.view_layer.update()
def parent_keep(o, p):
    mw = o.matrix_world.copy()
    o.parent = p
    o.matrix_parent_inverse = p.matrix_world.inverted()
    o.matrix_world = mw
crank_parts = {'part_output_shaft','part_flywheel_fan','part_flywheel_fan_blades'}
pull_parts = {'part_recoil_handle','part_recoil_handle_stem','part_recoil_rope'}
for o in bpy.data.collections['gx200_parts'].objects:
    if o.name in crank_parts: parent_keep(o, crank)
    elif o.name in pull_parts: parent_keep(o, pull)
    else: parent_keep(o, vib)
bpy.context.view_layer.update()
# rope: scale along local z must stay a pure axis scale -> rope's own rotation holds the direction
print('parents ok', crank.matrix_world.translation*1000, rope.matrix_world.translation*1000)
print(G.bbox(('part_recoil_handle','part_recoil_handle_stem','part_recoil_rope')))


# ===== call 78 2026-10-04T12:04:36.916Z =====
import bpy, math, time
from mathutils import Vector, Matrix
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
rope = bpy.data.objects['part_recoil_rope']; vib = bpy.data.objects['rig_vib']
mw = rope.matrix_world.copy(); rope.parent = vib; rope.matrix_parent_inverse = vib.matrix_world.inverted(); rope.matrix_world = mw
bpy.context.view_layer.update()
print('rope scale', tuple(round(s,4) for s in rope.scale), 'loc', tuple(round(v*1000,2) for v in rope.matrix_world.translation))
# animation cameras
def persp(name, lens=60):
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, cd)
    if cam.name not in bpy.data.collections['gx200_rig'].objects: G.link(cam, 'gx200_rig')
    cd.type = 'PERSP'; cd.lens = lens; cd.clip_start = 0.01; cd.clip_end = 40; cd.shift_x = cd.shift_y = 0
    return cam
def aim(cam, az, el, dist, target_mm):
    a, e = math.radians(az), math.radians(el)
    d = Vector((-math.cos(e)*math.cos(a), -math.cos(e)*math.sin(a), math.sin(e)))
    T = Vector(target_mm)*MM
    cam.location = T + d*dist; cam.rotation_euler = (-d).to_track_quat('-Z','Y').to_euler()
G.aim = aim; G.persp = persp
c1 = persp('cam_anim_turn', 70); aim(c1, 30, 18, 1.75, (0,0,165))
c2 = persp('cam_anim_run', 50); aim(c2, 38, 16, 1.85, (-90,20,175))
c3 = persp('cam_anim_explode', 50); aim(c3, 35, 24, 2.6, (0,30,200))
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
sc.camera = c1
G.set_engine(sc, 'BLENDER_EEVEE'); sc.eevee.taa_render_samples = 32
sc.render.film_transparent = False
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
import os
os.makedirs(G.OUT + 'anim/check', exist_ok=True)
t = time.time()
sc.render.filepath = G.OUT + 'anim/check/turn_test.png'
bpy.ops.render.render(write_still=True, scene=sc.name)
print('1 frame', round(time.time()-t, 2))


# ===== call 79 2026-10-04T12:04:50.861Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
sc = G.scn()
turn = bpy.data.objects['rig_turn']
turn.animation_data_clear()
turn.rotation_euler = (0,0,0); turn.keyframe_insert('rotation_euler', index=2, frame=1)
turn.rotation_euler = (0,0,2*math.pi); turn.keyframe_insert('rotation_euler', index=2, frame=193)
for fc in turn.animation_data.action.fcurves if hasattr(turn.animation_data.action, 'fcurves') else []:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# Blender 5 layered actions: fallback to iterate channelbags
def fcurves_of(obj):
    act = obj.animation_data.action
    if hasattr(act, 'fcurves') and len(act.fcurves):
        return list(act.fcurves)
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                out.extend(cb.fcurves)
    return out
G.fcurves_of = fcurves_of
for fc in fcurves_of(turn):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# markers to switch cameras
sc.timeline_markers.clear()
for f, cam in ((1,'cam_anim_turn'), (201,'cam_anim_run'), (401,'cam_anim_explode')):
    m = sc.timeline_markers.new('cam_' + cam[9:], frame=f); m.camera = bpy.data.objects[cam]
sc.frame_start, sc.frame_end = 1, 592
sc.frame_set(97); print(round(math.degrees(turn.rotation_euler.z),1), sc.camera.name)
sc.frame_set(1)


# ===== call 80 2026-10-04T12:04:58.282Z =====
import bpy, os, time
G = bpy.app.driver_namespace['gx']
sc = G.scn()
def render_range(name, f0, f1, samples=32, motion_blur=False):
    d = G.OUT + 'anim/%s/' % name; os.makedirs(d, exist_ok=True)
    sc.eevee.taa_render_samples = samples
    sc.render.use_motion_blur = motion_blur
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
    sc.render.film_transparent = False
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    t = time.time(); n = 0
    for f in range(f0, f1+1):
        p = d + 'f%04d.png' % f
        if os.path.exists(p): continue
        sc.frame_set(f)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True, scene=sc.name)
        n += 1
    return n, round(time.time()-t, 1)
G.render_range = render_range
# preview frames first: 1, 49, 97, 145
os.makedirs(G.OUT + 'anim/check', exist_ok=True)
for f in (49, 97, 145):
    sc.frame_set(f); sc.render.filepath = G.OUT + 'anim/check/turn_%03d.png' % f
    bpy.ops.render.render(write_still=True, scene=sc.name)
print('ok')


# ===== call 81 2026-10-04T12:05:10.915Z =====
import bpy
G = bpy.app.driver_namespace['gx']
print(G.render_range('turntable', 1, 60))


# ===== call 82 2026-10-04T12:05:52.554Z =====
import bpy
G = bpy.app.driver_namespace['gx']
print(G.render_range('turntable', 61, 192))


# ===== call 83 2026-10-04T12:07:57.494Z =====
import bpy, math, random
from mathutils import Vector
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
pull = bpy.data.objects['rig_pull']; rope = bpy.data.objects['part_recoil_rope']
crank = bpy.data.objects['rig_crank']; vib = bpy.data.objects['rig_vib']
for o in (pull, crank, vib): o.animation_data_clear()
# rope: keep only scale-z animation
if rope.animation_data: rope.animation_data_clear()
def ss(u): u = max(0.0, min(1.0, u)); return u*u*(3-2*u)
F0, P0, P1, R1, RUN, F1 = 201, 210, 232, 250, 254, 392
LMAX = 280.0
W_RUN = math.radians(83.0)   # rad / frame while running (blades drift slowly forward, keyway reads as fast spin)
def pull_len(f):
    if f <= P0: return 0.0
    if f <= P1: return LMAX * ss((f-P0)/(P1-P0))**0.85
    if f <= R1: return LMAX * (1 - ss((f-P1)/(R1-P1)))
    return 0.0
ang = {}; a = 0.0
for f in range(F0, F1+1):
    if f <= P1:
        a = (pull_len(f) / 40.0)          # rope on 40 mm pulley turns the crank
    elif f <= RUN:
        u = (f - P1) / (RUN - P1)
        w0 = (pull_len(P1) - pull_len(P1-1)) / 40.0
        a += w0 + (W_RUN - w0) * ss(u)
    else:
        a += W_RUN
    ang[f] = a
random.seed(7)
def vib_amp(f):
    if f < P1 + 2: return 0.0
    if f < RUN + 6: return ss((f - P1 - 2) / (RUN + 6 - P1 - 2))
    return 1.0
for f in range(F0, F1+1):
    L = pull_len(f)
    pull.location = G.PULL * (L*MM); pull.keyframe_insert('location', frame=f)
    rope.scale = (1, 1, max(0.01, L)); rope.keyframe_insert('scale', index=2, frame=f)
    crank.rotation_euler = (ang[f], 0, 0); crank.keyframe_insert('rotation_euler', index=0, frame=f)
    k = vib_amp(f)
    # firing pulses (single-cylinder: one pulse every 2 revs) + small noise
    ph = ang[f] / 2.0
    pulse = math.sin(ph) * 0.7 + random.uniform(-0.3, 0.3)
    vib.location = Vector((random.uniform(-0.15,0.15), 0.45*pulse, 0.35*math.cos(ph*2) + random.uniform(-0.12,0.12))) * (k*MM)
    vib.rotation_euler = (math.radians(0.28*pulse*k), 0, math.radians(random.uniform(-0.05,0.05)*k))
    vib.keyframe_insert('location', frame=f); vib.keyframe_insert('rotation_euler', frame=f)
# rest keys just before/after segments so other segments stay untouched
for o, path in ((pull,'location'),(crank,'rotation_euler'),(vib,'location'),(vib,'rotation_euler')):
    pass
for o in (pull, crank, vib, rope):
    for fc in G.fcurves_of(o):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# hold rest before segment (frame 200) and reset after (frame 393)
for f in (200, 393):
    pull.location = (0,0,0); pull.keyframe_insert('location', frame=f)
    rope.scale = (1,1,0.01); rope.keyframe_insert('scale', index=2, frame=f)
    crank.rotation_euler = (0,0,0); crank.keyframe_insert('rotation_euler', index=0, frame=f)
    vib.location = (0,0,0); vib.rotation_euler = (0,0,0)
    vib.keyframe_insert('location', frame=f); vib.keyframe_insert('rotation_euler', frame=f)
for o in (pull, crank, vib, rope):
    for fc in G.fcurves_of(o):
        for kp in fc.keyframe_points:
            if kp.co.x in (200, 392, 393): kp.interpolation = 'CONSTANT'
G.RUN_FRAMES = (F0, F1)
print('max angle rad', round(ang[F1],1), 'pull@232', round(pull_len(232),1))
for f in (1, 150, 200, 232, 300, 393, 450):
    sc.frame_set(f); print(f, tuple(round(v*1000,1) for v in pull.location), round(rope.scale.z,1), round(crank.rotation_euler.x,2))
sc.frame_set(1)


# ===== call 84 2026-10-04T12:08:05.458Z =====
import bpy, time
G = bpy.app.driver_namespace['gx']
sc = G.scn()
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.5
for attr, v in (('motion_blur_steps', 3),):
    try: setattr(sc.eevee, attr, v)
    except Exception as e: print('no', attr, e)
print([p for p in dir(sc.eevee) if 'motion' in p], [p for p in dir(sc.render) if 'motion' in p])
t = time.time()
for f in (222, 232, 244, 300):
    sc.frame_set(f); sc.render.filepath = G.OUT + 'anim/check/run_%03d.png' % f
    bpy.ops.render.render(write_still=True, scene=sc.name)
print('t', round(time.time()-t,1))
sc.frame_set(1)


# ===== call 85 2026-10-04T12:08:24.772Z =====
import bpy, math
from mathutils import Vector
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
c2 = bpy.data.objects['cam_anim_run']; c2.animation_data_clear(); c2.data.lens = 50
def key_cam(cam, f, az, el, dist, tgt):
    G.aim(cam, az, el, dist, tgt)
    cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f)
key_cam(c2, 201, 40, 18, 1.30, (-150, 10, 165))
key_cam(c2, 236, 40, 18, 1.30, (-150, 10, 165))
key_cam(c2, 300, 34, 15, 0.98, (-60, 0, 160))
key_cam(c2, 392, 30, 14, 0.90, (-50, 0, 160))
for f in (232, 330):
    sc.frame_set(f); sc.render.filepath = G.OUT + 'anim/check/run2_%03d.png' % f
    bpy.ops.render.render(write_still=True, scene=sc.name)
sc.frame_set(1)


# ===== call 86 2026-10-04T12:08:41.574Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
sc = G.scn()
c2 = bpy.data.objects['cam_anim_run']; c2.animation_data_clear()
def key_cam(f, az, el, dist, tgt):
    G.aim(c2, az, el, dist, tgt); c2.keyframe_insert('location', frame=f); c2.keyframe_insert('rotation_euler', frame=f)
key_cam(201, 40, 18, 1.30, (-150, 10, 165))
key_cam(236, 40, 18, 1.30, (-150, 10, 165))
# after start: move in, then orbit around the -Y (tank) side to the PTO end to show the spinning shaft
def ss(u): u = max(0.0, min(1.0, u)); return u*u*(3-2*u)
for f in range(244, 393, 4):
    u = ss((f - 244) / (392 - 244))
    az = 40 + (150 - 40) * u
    dist = 1.30 + (1.0 - 1.30) * ss((f - 244) / 40)
    tx = -150 + (40 + 150) * ss((f - 244) / 90)
    key_cam(f, az, 16, dist, (tx, -10, 170))
for fc in G.fcurves_of(c2):
    for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'
# euler continuity
for f in (300, 360, 392):
    sc.frame_set(f); sc.render.filepath = G.OUT + 'anim/check/run3_%03d.png' % f
    bpy.ops.render.render(write_still=True, scene=sc.name)
sc.frame_set(1)


# ===== call 87 2026-10-04T12:08:58.169Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
sc = G.scn()
c2 = bpy.data.objects['cam_anim_run']; c2.animation_data_clear()
def key_cam(f, az, el, dist, tgt):
    G.aim(c2, az, el, dist, tgt); c2.keyframe_insert('location', frame=f); c2.keyframe_insert('rotation_euler', frame=f)
def ss(u): u = max(0.0, min(1.0, u)); return u*u*(3-2*u)
key_cam(201, 40, 18, 1.30, (-150, 10, 165))
key_cam(236, 40, 18, 1.30, (-150, 10, 165))
for f in range(244, 393, 4):
    u = ss((f - 244) / (392 - 244))
    az = 40 + (150 - 40) * u
    dist = 1.30 + (1.12 - 1.30) * ss((f - 244) / 40)
    tx = -150 + (30 + 150) * ss((f - 244) / 90)
    key_cam(f, az, 18, dist, (tx, -10, 178))
sc.frame_set(300); sc.render.filepath = G.OUT + 'anim/check/run4_300.png'
bpy.ops.render.render(write_still=True, scene=sc.name)
sc.frame_set(1)


# ===== call 88 2026-10-04T12:09:07.659Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
sc = G.scn()
c2 = bpy.data.objects['cam_anim_run']; c2.animation_data_clear()
def key_cam(f, az, el, dist, tgt):
    G.aim(c2, az, el, dist, tgt); c2.keyframe_insert('location', frame=f); c2.keyframe_insert('rotation_euler', frame=f)
def ss(u): u = max(0.0, min(1.0, u)); return u*u*(3-2*u)
key_cam(201, 40, 18, 1.30, (-150, 10, 165))
key_cam(236, 40, 18, 1.30, (-150, 10, 165))
for f in range(244, 393, 4):
    u = ss((f - 244) / (392 - 244))
    az = 40 + (150 - 40) * u
    dist = 1.30 + (1.22 - 1.30) * ss((f - 244) / 40)
    tx = -150 + (30 + 150) * ss((f - 244) / 90)
    key_cam(f, az, 18, dist, (tx, -10, 168))
print(G.render_range('start_run', 201, 260, motion_blur=True))


# ===== call 89 2026-10-04T12:09:54.963Z =====
import bpy
G = bpy.app.driver_namespace['gx']
print(G.render_range('start_run', 261, 392, motion_blur=True))


# ===== call 90 2026-10-04T12:12:17.858Z =====
import bpy, math
from mathutils import Vector
G = bpy.app.driver_namespace['gx']; MM = G.MM
sc = G.scn()
A = Vector((0, math.cos(math.radians(25)), math.sin(math.radians(25))))   # cylinder axis
GROUPS = [
 # (name, objects, offset mm, order)
 ('fuel_cap',   ['part_fuel_cap'], Vector((0,-40,270)), 0),
 ('ac_knob',    ['part_air_cleaner_knob','part_air_cleaner_knob_base'], Vector((-40,130,250)), 0),
 ('tank',       ['part_fuel_tank','part_fuel_tank_rim','part_fuel_tank_lower','part_fuel_tank_emboss','part_fuel_filler_neck','part_fuel_gauge','part_fuel_gauge_lens'], Vector((0,-40,180)), 1),
 ('ac_lid',     ['part_air_cleaner'], Vector((-40,130,170)), 1),
 ('mf_shield',  ['part_muffler_shield'], Vector((90,150,230)), 1),
 ('muffler',    ['part_muffler','part_muffler_rib','part_muffler_outlet','part_muffler_outlet_hole','part_muffler_screws','part_muffler_stay','part_muffler_stay_bolt'], Vector((90,150,150)), 2),
 ('recoil',     ['part_recoil_starter','part_recoil_logo_disc','part_recoil_screws','part_logo_honda','part_logo_gx','part_logo_200','part_rope_guide','part_recoil_handle','part_recoil_handle_stem','part_recoil_rope'], Vector((-270,0,0)), 2),
 ('tank_brkt',  ['part_tank_bracket','part_tank_bracket_bolts','part_tank_bracket_rear','part_tank_bracket_rear_bolt','part_fuel_hose'], Vector((0,-40,100)), 2),
 ('ac_case',    ['part_air_cleaner_case','part_carb_cover','part_control_plate','part_fuel_cock_lever','part_choke_lever','part_ac_stud'], Vector((-60,190,70)), 3),
 ('shroud',     ['part_fan_shroud','part_fan_shroud_side','part_shroud_label','part_shroud_rpm_plate','part_engine_switch','part_engine_switch_toggle','part_switch_wire'], Vector((-180,-20,0)), 3),
 ('exhaust',    ['part_exhaust_pipe','part_exhaust_flange','part_exhaust_nuts'], Vector((60,70,90)), 3),
 ('head_cover', ['part_head_cover','part_head_cover_bosses','part_head_cover_bolts','part_ohv_letters'], A*170, 4),
 ('carb',       ['part_carburetor','part_carb_bowl','part_carb_drain','part_carb_insulator','part_throttle_lever','part_throttle_lever_tab','part_throttle_pivot','part_governor_rod'], Vector((-40,120,20)), 4),
 ('flywheel',   ['part_flywheel_fan','part_flywheel_fan_blades'], Vector((-95,0,0)), 4),
 ('spark',      ['part_spark_plug','part_spark_plug_cap','part_ht_lead'], A*95 + Vector((0,0,70)), 5),
 ('head',       ['part_cylinder_head','part_head_fins','part_exhaust_port'], A*95, 5),
 ('shaft',      ['part_output_shaft'], Vector((170,0,0)), 5),
 ('pto_cover',  ['part_crankcase_cover','part_att_face','part_bearing_boss','part_oil_seal','part_crankcase_bolts'], Vector((85,0,0)), 6),
 ('oil_l',      ['part_oil_filler_cap_l'], Vector((0,-55,60)), 6),
 ('oil_r',      ['part_oil_filler_cap_r'], Vector((0,55,60)), 6),
 ('side_parts', ['part_governor_arm','part_governor_arm_nut','part_governor_spring','part_crankcase_side_bolts'], Vector((0,-60,0)), 6),
 ('drain',      ['part_oil_drain_plug'], Vector((0,50,0)), 6),
]
allnames = {o.name for o in bpy.data.collections['gx200_parts'].objects}
used = [n for g in GROUPS for n in g[1]]
missing = [n for n in used if n not in allnames]
static = sorted(allnames - set(used))
print('missing', missing); print('static', static)
E0, DUR, STEP = 414, 34, 7       # explode start, move duration, stagger per order level
HOLD_END = 500                   # reassembly starts (reverse order)
R_STEP = 6
nlev = max(g[3] for g in GROUPS)
for gname, names, off, lev in GROUPS:
    a0 = E0 + lev*STEP; a1 = a0 + DUR
    b0 = HOLD_END + (nlev - lev)*R_STEP; b1 = b0 + DUR
    for n in names:
        o = bpy.data.objects[n]
        # strip previous delta keys
        if o.animation_data and o.animation_data.action:
            for fc in list(G.fcurves_of(o)):
                if fc.data_path == 'delta_location':
                    fc.keyframe_points.clear()
        for f, v in ((400, Vector()), (a0, Vector()), (a1, off), (b0, off), (b1, Vector())):
            o.delta_location = v*MM; o.keyframe_insert('delta_location', frame=f)
print('last reassembly end', HOLD_END + nlev*R_STEP + DUR)
o = bpy.data.objects['part_fuel_tank']
for f in (400, 450, 520, 592, 300, 1):
    sc.frame_set(f); print(f, tuple(round(v*1000,1) for v in o.delta_location))
sc.frame_set(1)
G.EXPL_GROUPS = GROUPS


# ===== call 91 2026-10-04T12:12:27.370Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
sc = G.scn()
c3 = bpy.data.objects['cam_anim_explode']; c3.animation_data_clear(); c3.data.lens = 50
def ss(u): u = max(0.0, min(1.0, u)); return u*u*(3-2*u)
for f in range(401, 593, 8):
    u = (f - 401) / (592 - 401)
    e = ss((f - 414) / 60) * (1 - ss((f - 520) / 50))      # 0 assembled .. 1 exploded
    az = 28 + 44*u
    dist = 1.45 + 0.75*e
    tz = 175 + 70*e
    G.aim(c3, az, 20 + 6*e, dist, (-25*e, 25*e, tz))
    c3.keyframe_insert('location', frame=f); c3.keyframe_insert('rotation_euler', frame=f)
G.aim(c3, 72, 20, 1.45, (0,0,175)); c3.keyframe_insert('location', frame=592); c3.keyframe_insert('rotation_euler', frame=592)
sc.render.use_motion_blur = False
for f in (430, 470, 500, 545):
    sc.frame_set(f); sc.render.filepath = G.OUT + 'anim/check/expl_%03d.png' % f
    bpy.ops.render.render(write_still=True, scene=sc.name)
sc.frame_set(1)


# ===== call 92 2026-10-04T12:12:43.793Z =====
import bpy, math
G = bpy.app.driver_namespace['gx']
sc = G.scn()
c3 = bpy.data.objects['cam_anim_explode']; c3.animation_data_clear()
def ss(u): u = max(0.0, min(1.0, u)); return u*u*(3-2*u)
for f in list(range(401, 593, 8)) + [592]:
    u = (f - 401) / (592 - 401)
    e = ss((f - 414) / 60) * (1 - ss((f - 520) / 50))
    G.aim(c3, 28 + 44*u, 22 + 10*e, 1.45 + 1.0*e, (-30*e, 30*e, 175 + 105*e))
    c3.keyframe_insert('location', frame=f); c3.keyframe_insert('rotation_euler', frame=f)
for f in (480, 500):
    sc.frame_set(f); sc.render.filepath = G.OUT + 'anim/check/expl2_%03d.png' % f
    bpy.ops.render.render(write_still=True, scene=sc.name)
sc.frame_set(1)


# ===== call 93 2026-10-04T12:12:50.593Z =====
import bpy
G = bpy.app.driver_namespace['gx']
print(G.render_range('exploded', 401, 490, motion_blur=False))


# ===== call 94 2026-10-04T12:13:54.982Z =====
import bpy
G = bpy.app.driver_namespace['gx']
print(G.render_range('exploded', 491, 592, motion_blur=False))


# ===== call 95 2026-10-04T12:15:11.772Z =====
import bpy, os, time
G = bpy.app.driver_namespace['gx']
sc = G.scn()
se = sc.sequence_editor_create()
print([p for p in dir(se) if not p.startswith('_')][:40])
r = sc.render
print([i.identifier for i in r.ffmpeg.bl_rna.properties['format'].enum_items])
print([i.identifier for i in r.ffmpeg.bl_rna.properties['codec'].enum_items])
print([i.identifier for i in r.ffmpeg.bl_rna.properties['constant_rate_factor'].enum_items])
sc.sequence_editor_clear()


# ===== call 96 2026-10-04T12:15:21.319Z =====
import bpy, os, time
G = bpy.app.driver_namespace['gx']
sc = G.scn(); r = sc.render
saved = dict(fs=sc.frame_start, fe=sc.frame_end, fmt=r.image_settings.file_format, path=r.filepath, seq=r.use_sequencer, mb=r.use_motion_blur, cm=r.image_settings.color_mode)
def encode(name, title_frames=None):
    d = G.OUT + 'anim/%s/' % name
    files = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    se = sc.sequence_editor_create()
    for s in list(se.strips): se.strips.remove(s)
    strip = se.strips.new_image(name, d + files[0], channel=1, frame_start=1)
    for f in files[1:]: strip.elements.append(f)
    sc.frame_start, sc.frame_end = 1, len(files)
    r.use_sequencer = True
    r.image_settings.file_format = 'FFMPEG'
    r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'; r.ffmpeg.constant_rate_factor = 'HIGH'
    r.ffmpeg.ffmpeg_preset = 'GOOD' if 'GOOD' in [i.identifier for i in r.ffmpeg.bl_rna.properties['ffmpeg_preset'].enum_items] else r.ffmpeg.ffmpeg_preset
    r.fps = 24; r.fps_base = 1.0
    r.filepath = G.OUT + 'anim/%s.mp4' % name
    t = time.time()
    bpy.ops.render.render(animation=True, scene=sc.name)
    sc.sequence_editor_clear()
    return len(files), round(time.time()-t, 1)
try:
    for n in ('turntable', 'start_run', 'exploded'):
        print(n, encode(n))
finally:
    sc.sequence_editor_clear()
    sc.frame_start, sc.frame_end = saved['fs'], saved['fe']
    r.image_settings.file_format = saved['fmt']; r.image_settings.color_mode = saved['cm']
    r.filepath = saved['path']; r.use_sequencer = saved['seq']; r.use_motion_blur = saved['mb']
print(os.listdir(G.OUT + 'anim'))


# ===== call 97 2026-10-04T12:15:29.451Z =====
import bpy
G = bpy.app.driver_namespace['gx']
sc = G.scn(); r = sc.render; ims = r.image_settings
print(sc.frame_start, sc.frame_end, ims.file_format, r.use_sequencer, sc.sequence_editor)
print([p for p in dir(ims) if 'media' in p or 'type' in p])
if hasattr(ims, 'media_type'):
    print([i.identifier for i in ims.bl_rna.properties['media_type'].enum_items], ims.media_type)


# ===== call 98 2026-10-04T12:15:38.921Z =====
import bpy, os, time
G = bpy.app.driver_namespace['gx']
sc = G.scn(); r = sc.render; ims = r.image_settings
saved = dict(fs=sc.frame_start, fe=sc.frame_end, path=r.filepath, seq=r.use_sequencer)
def encode(name):
    d = G.OUT + 'anim/%s/' % name
    files = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    se = sc.sequence_editor_create()
    strip = se.strips.new_image(name, d + files[0], channel=1, frame_start=1)
    for f in files[1:]: strip.elements.append(f)
    sc.frame_start, sc.frame_end = 1, len(files)
    r.use_sequencer = True
    ims.media_type = 'VIDEO'
    ims.file_format = 'FFMPEG'
    r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'; r.ffmpeg.constant_rate_factor = 'HIGH'
    r.fps = 24; r.fps_base = 1.0
    r.filepath = G.OUT + 'anim/%s.mp4' % name
    t = time.time()
    bpy.ops.render.render(animation=True, scene=sc.name)
    sc.sequence_editor_clear()
    return len(files), round(time.time()-t, 1)
try:
    for n in ('turntable', 'start_run', 'exploded'):
        print(n, encode(n))
finally:
    sc.sequence_editor_clear()
    ims.media_type = 'IMAGE'; ims.file_format = 'PNG'; ims.color_mode = 'RGB'
    sc.frame_start, sc.frame_end = saved['fs'], saved['fe']
    r.filepath = saved['path']; r.use_sequencer = saved['seq']
print(sorted(os.listdir(G.OUT + 'anim')))


# ===== call 99 2026-10-04T12:15:56.064Z =====
import bpy, os
G = bpy.app.driver_namespace['gx']
for n in ('turntable','start_run','exploded'):
    p = G.OUT + 'anim/%s.mp4' % n
    mc = bpy.data.movieclips.load(p)
    print(n, os.path.getsize(p)//1024, 'KB', mc.frame_duration, 'frames', tuple(mc.size), round(mc.fps,2), 'fps')
    bpy.data.movieclips.remove(mc)


# ===== call 100 2026-10-04T12:16:26.717Z =====
import bpy
G = bpy.app.driver_namespace['gx']
sc = G.scn()
ex = ('part_recoil_handle','part_recoil_handle_stem','part_recoil_rope')
for f in (1, 200, 400, 592):
    sc.frame_set(f)
    print(f, G.bbox(ex)[2], G.bbox(('part_recoil_rope',))[2])
sc.frame_set(1)
sc.render.use_motion_blur = False
bpy.data.libraries.write(G.OUT + 'gx200_anim.blend', {sc}, fake_user=True, path_remap='ABSOLUTE')
import os; print('saved', os.path.getsize(G.OUT + 'gx200_anim.blend'))
with bpy.data.libraries.load(G.OUT + 'gx200_anim.blend') as (src, dst):
    print('scenes', src.scenes, 'objects', len(src.objects), 'actions', len(src.actions))
print('other scene untouched:', [o.name for o in bpy.data.scenes['Scene'].objects], [l.filepath for l in bpy.data.libraries])

