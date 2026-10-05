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

