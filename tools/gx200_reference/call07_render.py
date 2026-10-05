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

