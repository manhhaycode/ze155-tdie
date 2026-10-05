# ZE 155 animation helper library (created in phase C0). Load inside Blender through MCP, after ze_helpers:
#   exec(open('/Users/manhhaycode/m3d-e2e/ze155-tdie/tools/ze_helpers.py').read())
#   Z = bpy.app.driver_namespace['ze']; Z.load_views()
#   exec(open('/Users/manhhaycode/m3d-e2e/ze155-tdie/anim/anim_helpers.py').read())
#   za = bpy.app.driver_namespace['za']
#
# Everything lives inside _za_install() so that no top-level name collides with the ze_helpers globals
# (link, obj, mat, render, ...) when both files are exec'd in the same MCP call.
#
# Safety contract (see anim/BUILD-ANIM.md):
#   - scene ze155 is never changed; only the anim scene ze155_anim is.
#   - ze155 objects enter the anim scene only by LINKING into an anim-only ax_* collection (za.link_ze).
#   - every object an anim phase creates lives only in anim_* / ax_* collections of ze155_anim (za.link, za.new_obj,
#     za.obj, za.copy_obj). Loading za guards Z: Z.obj / Z.box / Z.tube / ... refuse a non-anim collection
#     (the ze155_parts default raises), Z.mat never rewrites a ze_* material, Z modifier helpers refuse ze155 objects,
#     and the ze155 scene/render/save helpers raise.
#   - saving is only za.save() -> out/ze155_anim.blend (bpy.data.libraries.write), never the open file.
import bpy


def _za_install():
    import os, json, math, time, shutil, types
    from mathutils import Vector, Matrix

    za = types.SimpleNamespace()
    za.ROOT = '/Users/manhhaycode/m3d-e2e/ze155-tdie/'
    za.ANIM = za.ROOT + 'anim/'
    za.OUT = za.ROOT + 'out/'
    za.SCENE = 'ze155_anim'
    za.SRC = 'ze155'
    za.BLEND = za.OUT + 'ze155_anim.blend'
    za.VERIFY = za.ANIM + 'tmp/verify.blend'
    za.FINGERPRINT = za.ANIM + 'tmp/ze155_fingerprint.json'
    za.LOOK = za.ANIM + 'look/'
    za.FRAMES = za.ANIM + 'render/frames/'
    za.PREVIEW = za.ANIM + 'render/preview/'
    za.LOG = za.ANIM + 'log.md'
    za.SHOTS_PATH = za.ANIM + 'shots.json'
    za.PARTS_PATH = za.ANIM + 'interior_parts.json'
    za.ZE_OBJECTS, za.ZE_CAMERAS, za.N_CAMS = 610, 73, 24
    za.FPS = 25
    za.PARENTS = ('anim_ax', 'anim_int', 'anim_cut', 'anim_fx')
    za.CUTTERS = 'anim_cutters'
    za.RIG = 'anim_rig'
    # empty anim collections created by C0 (more can be made on demand with za.coll(name))
    za.INT_COLLS = ['anim_int_' + n for n in ('screws', 'barrel', 'feed', 'melt', 'sc', 'pump', 'die', 'fill',
                                              'drive', 'context')]
    za.CUT_COLLS = ['anim_cut_' + n for n in ('feed', 'zb', 'x2450', 'x4120', 'pump', 'dp', 'aa', 'st1',
                                              'ghost_drive', 'ghost_sc')]
    za.FX_COLLS = ['anim_fx_' + n for n in ('axis', 'material', 'vent', 'sc', 'flows', 'loops')]
    za.LIGHTS = ('light_key', 'light_fill', 'light_rim', 'light_top', 'light_die')
    # C0 DESIGN-DEVIATIONs: ze155 objects that shots.json leaves in ax_static but that stand on / hang from the feed
    # platform (they would float when ax_feed_platform hides in S04/S06/S08/ST1). See anim/log.md.
    za.GROUP_OVERRIDES = {
        'sidefeed_feeder': 'ax_feed_platform', 'sidefeed_feeder_hopper': 'ax_feed_platform',
        'sidefeed_downpipe': 'ax_feed_platform', 'sidefeed_downpipe_flex': 'ax_feed_platform',
        'sidefeed_downpipe_hw': 'ax_feed_platform',
        'ctrl_cable_feed': 'ax_feed_platform', 'ctrl_cable_tray_feed': 'ax_feed_platform',
        'util_frl_2': 'ax_feed_platform',
    }

    # ------------------------------------------------------------------ data files
    def load_shots():
        with open(za.SHOTS_PATH) as f:
            za.SHOTS = json.load(f)
        return za.SHOTS
    za.load_shots = load_shots

    def load_parts():
        with open(za.PARTS_PATH) as f:
            za.PARTS = json.load(f)
        return za.PARTS
    za.load_parts = load_parts

    def shot(sid):
        """shot dict by id ('S01'), or still dict ('ST1')."""
        for s in za.SHOTS['shots']:
            if s['id'] == sid:
                return s
        for s in za.SHOTS['stills']:
            if s['id'] == sid:
                return s
        raise KeyError(sid)
    za.shot = shot

    def shot_at(frame):
        for s in za.SHOTS['shots']:
            if s['frames'][0] <= frame <= s['frames'][1]:
                return s
        return None
    za.shot_at = shot_at

    # C0 DESIGN-DEVIATIONs on camera keys (shots.json stays unchanged; see anim/log.md)
    za.CAM_OVERRIDES = {
        'anim_cam_S13': {'keys': [
            {'frame': 3676, 'loc': [6.7, 2.2, 3.0], 'target': [9.7, 0.0, 1.5], 'lens_mm': 40},
            {'frame': 3826, 'loc': [11.0, 3.4, 4.6], 'target': [11.2, 0.0, 2.0], 'lens_mm': 28},
            {'frame': 3975, 'loc': [13.4, 4.3, 3.1], 'target': [11.4, 0.0, 1.6], 'lens_mm': 30}]},
    }

    def cam_specs():
        """[(camera_name, spec, kind)] for the 17 shot cameras and the 7 still cameras (with za.CAM_OVERRIDES)."""
        out = []
        for s in za.SHOTS['shots']:
            for c in s['cameras']:
                out.append((c['name'], dict(c, **za.CAM_OVERRIDES.get(c['name'], {})), 'shot'))
        for s in za.SHOTS['stills']:
            c = s['camera']
            out.append((c['name'], dict(c, **za.CAM_OVERRIDES.get(c['name'], {})), 'still'))
        return out
    za.cam_specs = cam_specs

    def cam_start(name):
        """first frame a shot camera is used (marker frame); None for still cameras."""
        for s in za.SHOTS['shots']:
            for c in s['cameras']:
                if c['name'] == name:
                    return c.get('frames', s['frames'])[0]
        return None
    za.cam_start = cam_start

    def resolve(shot_or_cam, frame=None):
        """('S03', 800) -> ('anim_cam_S03b', 800); ('S03a', None) -> ('anim_cam_S03a', 551); ('ST5') -> still cam."""
        key = shot_or_cam
        if key.startswith('anim_cam_'):
            key = key[len('anim_cam_'):]
        if key.startswith('ST'):
            sc = scene()
            return 'anim_cam_' + key, frame if frame is not None else sc.frame_current
        sid = key[:3]
        s = shot(sid)
        cams = s['cameras']
        if len(key) > 3:                                   # explicit sub-camera, e.g. S03b
            c = next(c for c in cams if c['name'] == 'anim_cam_' + key)
        elif frame is not None:
            c = next((c for c in cams if c.get('frames', s['frames'])[0] <= frame <= c.get('frames', s['frames'])[1]),
                     cams[0])
        else:
            c = cams[0]
        f = frame if frame is not None else c.get('frames', s['frames'])[0]
        return c['name'], f
    za.resolve = resolve

    # ------------------------------------------------------------------ scenes, collections
    def scene():
        sc = bpy.data.scenes.get(za.SCENE)
        if sc is None:
            raise RuntimeError('STOP: scene ze155_anim is missing (Blender restarted?). Report to the orchestrator; '
                               'do not improvise an append.')
        return sc
    za.scene = scene

    def src():
        return bpy.data.scenes[za.SRC]
    za.src = src

    def vl():
        return scene().view_layers[0]
    za.vl = vl

    def src_colls():
        s = src()
        return set(s.collection.children_recursive)
    za.src_colls = src_colls

    def is_ze(o):
        """True for an object of scene ze155 (or in any ze155_* collection)."""
        if isinstance(o, str):
            o = bpy.data.objects.get(o)
            if o is None:
                return False
        return (o.name in src().objects) or any(c.name.startswith('ze155_') for c in o.users_collection)
    za.is_ze = is_ze

    def _parent_for(name):
        if name.startswith('ax_'):
            return 'anim_ax'
        for p in ('anim_int', 'anim_cut', 'anim_fx'):
            if name.startswith(p + '_'):
                return p
        return None

    def coll(name, create=True):
        """get (or create) an anim-only collection of ze155_anim. Names must start with anim_ or ax_.
        ax_* go under anim_ax, anim_int_* under anim_int, anim_cut_* under anim_cut, anim_fx_* under anim_fx,
        everything else at the scene root."""
        if not name.startswith(('anim_', 'ax_')):
            raise ValueError('not an anim collection name: %r (must start with anim_ or ax_)' % name)
        sc = scene()
        c = bpy.data.collections.get(name)
        if c is not None:
            if c in src_colls():
                raise RuntimeError('collection %s belongs to scene ze155' % name)
        else:
            if not create:
                return None
            c = bpy.data.collections.new(name)
        pn = _parent_for(name)
        parent = coll(pn) if pn else sc.collection
        if c.name not in parent.children:
            parent.children.link(c)
        return c
    za.coll = coll

    def ax(group):
        """ax_* visibility group collection; accepts 'drive_housing' or 'ax_drive_housing'."""
        return coll(group if group.startswith('ax_') else 'ax_' + group)
    za.ax = ax

    def rig():
        return coll(za.RIG)
    za.rig = rig

    def colls(prefix=''):
        """anim collections of ze155_anim whose name starts with prefix."""
        return [c for c in scene().collection.children_recursive if c.name.startswith(prefix)]
    za.colls = colls

    def lcoll(name, view_layer=None):
        """layer collection of the anim view layer for collection name."""
        def walk(l):
            if l.collection.name == name:
                return l
            for ch in l.children:
                r = walk(ch)
                if r is not None:
                    return r
            return None
        v = view_layer or vl()
        root = v.layer_collection
        if root is None:                                   # a fresh scene's layer tree syncs lazily
            v.update()
            root = v.layer_collection
        return walk(root) if root is not None else None
    za.lcoll = lcoll

    def ax_of(o):
        """ax_* collections an object is linked into."""
        return [c.name for c in o.users_collection if c.name.startswith('ax_')]
    za.ax_of = ax_of

    def members(group):
        return [o.name for o in ax(group).objects]
    za.members = members

    # ------------------------------------------------------------------ objects (anim only)
    _DATA = {'Mesh': 'meshes', 'Curve': 'curves', 'TextCurve': 'curves', 'SurfaceCurve': 'curves',
             'Camera': 'cameras', 'Light': 'lights', 'AreaLight': 'lights', 'PointLight': 'lights',
             'SpotLight': 'lights', 'SunLight': 'lights', 'PointCloud': 'pointclouds', 'Curves': 'hair_curves',
             'GreasePencil': 'grease_pencils', 'Volume': 'volumes'}

    def remove(name, keep=None):
        """remove an anim-only object (and its orphan data). Refuses ze155 objects."""
        o = bpy.data.objects.get(name) if isinstance(name, str) else name
        if o is None:
            return False
        if is_ze(o) or any(s.name != za.SCENE for s in o.users_scene):
            raise RuntimeError('za.remove refuses %s: it belongs to scene ze155 (or another scene)' % o.name)
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and data is not keep and data.users == 0:
            attr = _DATA.get(type(data).__name__)
            if attr and hasattr(bpy.data, attr):
                getattr(bpy.data, attr).remove(data)
        return True
    za.remove = remove

    def remove_prefix(prefix):
        """remove every anim-only object of ze155_anim whose name starts with prefix (ze155 objects are skipped)."""
        names = [o.name for o in scene().objects if o.name.startswith(prefix) and not is_ze(o)]
        for n in names:
            remove(n)
        return names
    za.remove_prefix = remove_prefix

    def link(o, cname):
        """link an anim-only object into an anim collection (refuses ze155 objects and non-anim collections)."""
        c = coll(cname)
        if is_ze(o):
            raise RuntimeError('%s is a ze155 object: use za.link_ze(o, ax_group) or za.copy_obj' % o.name)
        if o.name not in c.objects:
            c.objects.link(o)
        return o
    za.link = link

    def link_ze(o, group):
        """link (not copy) a ze155 object into an ax_* group of the anim scene."""
        if isinstance(o, str):
            o = bpy.data.objects[o]
        c = ax(group)
        if not is_ze(o):
            raise RuntimeError('%s is not a ze155 object' % o.name)
        if o.name not in c.objects:
            c.objects.link(o)
        return o
    za.link_ze = link_ze

    def new_obj(name, data, cname):
        """new object (data may be None for an empty) linked only into anim collection cname."""
        remove(name, keep=data)
        o = bpy.data.objects.new(name, data)
        link(o, cname)
        return o
    za.new_obj = new_obj

    def empty(name, cname, loc=(0, 0, 0), size=0.1, kind='PLAIN_AXES'):
        o = new_obj(name, None, cname)
        o.empty_display_type = kind
        o.empty_display_size = size
        o.location = loc
        return o
    za.empty = empty

    def copy_obj(src_name, new_name, cname, share_data=False):
        """anim copy of any object (e.g. a ze155 part to rotate, split or recolour). Data is copied unless
        share_data; materials stay shared, so use za.copy_mat before changing one."""
        s = bpy.data.objects[src_name] if isinstance(src_name, str) else src_name
        remove(new_name)
        o = s.copy()
        o.name = new_name
        if s.data is not None and not share_data:
            o.data = s.data.copy()
            o.data.name = new_name
        if o.animation_data:
            o.animation_data_clear()
        link(o, cname)
        return o
    za.copy_obj = copy_obj

    def copy_mat(m, new_name=None):
        """anim copy of a material (named za_<...>), for any change to a material shared with ze155."""
        if isinstance(m, str):
            m = bpy.data.materials[m]
        nn = new_name or ('za_' + (m.name[3:] if m.name.startswith('ze_') else m.name))
        if not nn.startswith('za_'):
            nn = 'za_' + nn
        old = bpy.data.materials.get(nn)
        if old is not None:
            return old
        m2 = m.copy()
        m2.name = nn
        return m2
    za.copy_mat = copy_mat

    def _ze_mats():
        Z = bpy.app.driver_namespace.get('ze')
        if Z is None:
            return {}
        return getattr(Z, 'MATS', None) or Z.obj_from_bm.__globals__.get('MATS') or {}

    def srgb2lin(c):
        return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

    def mat(name, col=None, rough=None, metal=None, alpha=None):
        """safe material. No arguments: reuse za_<name> if it exists, else the ze155 material ze_<name> (read-only),
        else create za_<name> from the Z.MATS palette. With col/rough/metal/alpha: create or update za_<name>.
        A ze_* material is never modified."""
        if isinstance(name, bpy.types.Material):
            return name
        mz = bpy.data.materials.get('za_' + name)
        if col is None and rough is None and metal is None and alpha is None:
            if mz is not None:
                return mz
            ze = bpy.data.materials.get('ze_' + name)
            if ze is not None:
                return ze
        base = _ze_mats().get(name, ((0.6, 0.6, 0.6), 0.5, 0.0))
        c = col or base[0]
        r = base[1] if rough is None else rough
        me = base[2] if metal is None else metal
        m = mz or bpy.data.materials.new('za_' + name)
        try:
            m.use_nodes = True
        except Exception:
            pass
        bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        lc = srgb2lin(c)
        bsdf.inputs['Base Color'].default_value = (*lc, 1)
        bsdf.inputs['Roughness'].default_value = r
        bsdf.inputs['Metallic'].default_value = me
        if alpha is not None:
            bsdf.inputs['Alpha'].default_value = alpha
            try:
                m.surface_render_method = 'BLENDED'
            except Exception:
                pass
        m.diffuse_color = (*lc, 1 if alpha is None else alpha)
        return m
    za.mat = mat

    def boolean(o, cutter, op='DIFFERENCE', solver='MANIFOLD'):
        """Z.boolean for anim objects: the cutter goes to anim_cutters (hidden), never ze155_cutters."""
        if is_ze(o) or is_ze(cutter):
            raise RuntimeError('za.boolean refuses ze155 objects (%s, %s)' % (o.name, cutter.name))
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
        cc = coll(za.CUTTERS)
        for c in list(cutter.users_collection):
            if c is not cc:
                c.objects.unlink(cutter)
        if cutter.name not in cc.objects:
            cc.objects.link(cutter)
        try:
            cutter.hide_set(True, view_layer=vl())
        except Exception:
            pass
        return m
    za.boolean = boolean

    def obj(name, bm, mats, coll, **kw):
        """Z.obj into an anim collection (coll is required)."""
        guard_ze()
        Z = bpy.app.driver_namespace['ze']
        return Z.obj(name, bm, mats, coll=coll, **kw)
    za.obj = obj

    # ------------------------------------------------------------------ guard the ze helpers
    _FORBIDDEN = ('save_blend', 'setup_scene', 'render', 'remove_prefix', 'make_ortho_cam', 'persp_cam',
                  'ortho_free', 'render_check', 'render_parts', 'render_noblk', 'render_iso', 'frender',
                  'cmp_render', 'hide_blk')
    _OBJ_GUARD = ('bevel', 'wnormal', 'solidify', 'smooth', 'hard', 'array', 'apply_mods', 'fix_mixed')

    def _forbidden(nm):
        def f(*a, **k):
            raise RuntimeError('Z.%s is forbidden in the animation phases (it targets scene ze155 or the open '
                               'file). Use the za.* equivalent.' % nm)
        f._za_stub = True
        return f

    def _obj_guard(fn, nm):
        def w(o, *a, **k):
            if isinstance(o, bpy.types.Object) and is_ze(o):
                raise RuntimeError('Z.%s on ze155 object %s is forbidden; make an anim copy first (za.copy_obj)'
                                   % (nm, o.name))
            return fn(o, *a, **k)
        w._za_wrapped = fn
        return w

    def guard_ze():
        """patch the loaded Z helpers so they can only create objects in anim collections of ze155_anim."""
        Z = bpy.app.driver_namespace.get('ze')
        if Z is None:
            return False
        if getattr(Z, '_za_guarded', None) is za:
            return True
        g = Z.obj_from_bm.__globals__

        def ze_link(o, coll='ze155_parts'):
            try:
                return link(o, coll)
            except Exception:
                if not o.users_collection and not is_ze(o):     # drop the orphan Z just created
                    data = o.data
                    bpy.data.objects.remove(o)
                    if data is not None and data.users == 0:
                        attr = _DATA.get(type(data).__name__)
                        if attr and hasattr(bpy.data, attr):
                            getattr(bpy.data, attr).remove(data)
                raise

        def ze_remove(name):
            return remove(name)
        g['link'] = ze_link
        g['_remove'] = ze_remove
        Z.link = ze_link
        Z.remove = ze_remove
        Z.mat = mat
        Z.boolean = boolean
        g['boolean'] = boolean
        for nm in _FORBIDDEN:
            if hasattr(Z, nm):
                setattr(Z, nm, _forbidden(nm))
            if nm in g and callable(g[nm]):
                g[nm] = _forbidden(nm)
        for nm in _OBJ_GUARD:
            fn = getattr(Z, nm, None)
            if fn is not None and not hasattr(fn, '_za_wrapped'):
                w = _obj_guard(fn, nm)
                setattr(Z, nm, w)
                if g.get(nm) is fn:
                    g[nm] = w
        Z._za_guarded = za
        return True
    mat._za_safe = True
    za.guard_ze = guard_ze

    # ------------------------------------------------------------------ animation utilities
    def fcurves(id_):
        """F-curves of an ID's assigned action (Blender 5 slotted actions)."""
        ad = getattr(id_, 'animation_data', None)
        if ad is None or ad.action is None:
            return []
        try:
            from bpy_extras.anim_utils import animdata_get_channelbag_for_assigned_slot
            cb = animdata_get_channelbag_for_assigned_slot(ad)
            return list(cb.fcurves) if cb else []
        except Exception:
            return list(getattr(ad.action, 'fcurves', []))
    za.fcurves = fcurves

    def set_interp(id_, interp='BEZIER', handles='AUTO_CLAMPED'):
        for fc in fcurves(id_):
            for k in fc.keyframe_points:
                k.interpolation = interp
                if interp == 'BEZIER':
                    k.handle_left_type = handles
                    k.handle_right_type = handles
            fc.update()
    za.set_interp = set_interp

    def log(text, header=None):
        with open(za.LOG, 'a') as f:
            if header:
                f.write('\n## %s (%s)\n' % (header, time.strftime('%Y-%m-%d %H:%M')))
            f.write(text.rstrip('\n') + '\n')
    za.log = log

    def tris(prefix='anim_', objects=None):
        """triangles of evaluated render-visible objects in anim collections whose name starts with prefix."""
        dg = bpy.context.evaluated_depsgraph_get()
        seen, n = set(), 0
        obs = objects if objects is not None else [o for c in colls(prefix) for o in c.objects]
        for o in obs:
            if o.name in seen or o.type not in ('MESH', 'CURVE') or o.hide_render:
                continue
            seen.add(o.name)
            oe = o.evaluated_get(dg)
            try:
                me = oe.to_mesh()
                me.calc_loop_triangles()
                n += len(me.loop_triangles)
                oe.to_mesh_clear()
            except Exception:
                pass
        return n
    za.tris = tris

    # ------------------------------------------------------------------ ze155 integrity
    def _rna_dump(st):
        """simple (non-pointer) RNA properties of a struct, for change detection."""
        out = {}
        for p in st.bl_rna.properties:
            k = p.identifier
            if k == 'rna_type' or p.type in ('POINTER', 'COLLECTION'):
                continue
            try:
                v = getattr(st, k)
            except Exception:
                continue
            if isinstance(v, set):
                v = sorted(v)
            elif hasattr(v, '__len__') and not isinstance(v, str):
                v = [round(x, 5) if isinstance(x, float) else x for x in v]
            elif isinstance(v, float):
                v = round(v, 5)
            out[k] = v if isinstance(v, (int, float, str, bool, list, type(None))) else str(v)
        return out

    def fingerprint():
        """compact state of scene ze155: objects (transform, visibility, modifiers, data, materials, ze155
        collections), the materials they use, and the scene settings."""
        s = src()
        fp = {}
        mats = set()
        for o in s.objects:
            mw = [round(v, 5) for row in o.matrix_world for v in row]
            mods = [(m.name, m.type, m.show_viewport, m.show_render) for m in getattr(o, 'modifiers', [])]
            ms = [sl.material.name if sl.material else None for sl in o.material_slots]
            mats.update(m for m in ms if m)
            nv = len(o.data.vertices) if o.type == 'MESH' else None
            fp['obj:' + o.name] = json.dumps([mw, o.hide_render, o.hide_viewport, o.hide_select,
                                              o.parent.name if o.parent else None,
                                              o.data.name if o.data else None, nv, mods, ms,
                                              sorted(c.name for c in o.users_collection if c.name.startswith('ze155_'))])
        for mn in sorted(mats):
            m = bpy.data.materials[mn]
            vals = []
            if m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == 'BSDF_PRINCIPLED':
                        for k in ('Base Color', 'Roughness', 'Metallic', 'Alpha'):
                            v = n.inputs[k].default_value
                            vals.append([round(x, 4) for x in v] if hasattr(v, '__len__') else round(v, 4))
                vals.append(len(m.node_tree.nodes))
            fp['mat:' + mn] = json.dumps(vals)
        r = s.render
        fp['scene'] = json.dumps([r.engine, r.resolution_x, r.resolution_y, r.fps, s.frame_start, s.frame_end,
                                  s.frame_current, s.camera.name if s.camera else None,
                                  s.world.name if s.world else None, s.view_settings.view_transform,
                                  s.view_settings.look, len(s.timeline_markers),
                                  sorted(c.name for c in s.collection.children),
                                  [(c.name, c.hide_render, c.hide_viewport) for c in s.collection.children_recursive]])
        fp['settings'] = json.dumps([_rna_dump(s.unit_settings), _rna_dump(s.eevee), _rna_dump(r),
                                     _rna_dump(r.image_settings), _rna_dump(s.view_settings),
                                     _rna_dump(s.display_settings), s.sequencer_colorspace_settings.name,
                                     _rna_dump(s.display.shading)])
        return fp
    za.fingerprint = fingerprint

    def save_fingerprint():
        os.makedirs(os.path.dirname(za.FINGERPRINT), exist_ok=True)
        fp = fingerprint()
        with open(za.FINGERPRINT, 'w') as f:
            json.dump(fp, f)
        return len(fp)
    za.save_fingerprint = save_fingerprint

    def check_ze155(fp=True):
        """object and camera counts of scene ze155 (expect 610 / 73), plus a diff against the C0 fingerprint."""
        s = src()
        n = len(s.objects)
        nc = sum(1 for o in s.objects if o.type == 'CAMERA')
        res = dict(objects=n, cameras=nc, ok=(n == za.ZE_OBJECTS and nc == za.ZE_CAMERAS))
        if fp and os.path.exists(za.FINGERPRINT):
            with open(za.FINGERPRINT) as f:
                base = json.load(f)
            cur = fingerprint()
            diff = sorted(k for k in set(base) | set(cur) if base.get(k) != cur.get(k))
            res['fingerprint_diffs'] = len(diff)
            res['diff_sample'] = diff[:10]
            res['ok'] = res['ok'] and not diff
        return res
    za.check_ze155 = check_ze155

    def check_anim():
        """counts of the anim scene: objects, cameras, ze155_* links, ax membership."""
        sc = scene()
        cams = sorted(o.name for o in sc.objects if o.type == 'CAMERA')
        ze_obs = [o for o in sc.objects if is_ze(o)]
        bad_ax = [(o.name, ax_of(o)) for o in ze_obs if len(ax_of(o)) != 1]
        names = [c.name for c in sc.collection.children_recursive]
        bad_coll = [n for n in names if not n.startswith(('anim_', 'ax_'))]
        stray = [o.name for o in sc.objects if not is_ze(o)
                 and any(not c.name.startswith(('anim_', 'ax_')) for c in o.users_collection)]
        ax_counts = {c.name: len(c.objects) for c in colls('ax_')}
        return dict(objects=len(sc.objects), cameras=len(cams), ze_linked=len(ze_obs),
                    anim_objects=len(sc.objects) - len(ze_obs), ze155_rig_linked=('ze155_rig' in names),
                    non_anim_collections=bad_coll, ze_not_in_one_ax=bad_ax[:10], n_ze_not_in_one_ax=len(bad_ax),
                    anim_objects_in_non_anim_colls=stray[:10], ax_counts=ax_counts)
    za.check_anim = check_anim

    # ------------------------------------------------------------------ save
    def save(verify=True):
        """write only scene ze155_anim to out/ze155_anim.blend, copy it to anim/tmp/verify.blend and list the copy."""
        sc = scene()
        os.makedirs(os.path.dirname(za.VERIFY), exist_ok=True)
        t = time.time()
        bpy.data.libraries.write(za.BLEND, {sc}, fake_user=True)
        info = dict(path=za.BLEND, mb=round(os.path.getsize(za.BLEND) / 1e6, 1), write_s=round(time.time() - t, 1))
        live_cams = sorted(o.name for o in sc.objects if o.type == 'CAMERA')
        info['live'] = dict(objects=len(sc.objects), cameras=len(live_cams))
        if verify:
            shutil.copy2(za.BLEND, za.VERIFY)
            nlib = len(bpy.data.libraries)
            with bpy.data.libraries.load(za.VERIFY) as (src_, _dst):
                scenes = list(src_.scenes)
                objs = list(src_.objects)
                info.update(scenes=scenes, n_objects=len(objs), n_collections=len(src_.collections),
                            collections=sorted(src_.collections), n_cameras=len(src_.cameras),
                            n_lights=len(src_.lights), n_meshes=len(src_.meshes), n_materials=len(src_.materials),
                            n_actions=len(src_.actions), n_worlds=len(src_.worlds))
            ze_cams = set(o.name for o in src().objects if o.type == 'CAMERA')
            info['anim_cams_in_file'] = sum(1 for n in objs if n.startswith('anim_cam_'))
            info['ze155_cams_in_file'] = sorted(set(objs) & ze_cams)
            info['ze155_scene_in_file'] = za.SRC in scenes
            # libraries.load must not leave a library behind
            for lib in list(bpy.data.libraries)[nlib:]:
                if lib.users == 0 and os.path.abspath(bpy.path.abspath(lib.filepath)) == os.path.abspath(za.VERIFY):
                    bpy.data.libraries.remove(lib)
        return info
    za.save = save

    # ------------------------------------------------------------------ renders
    def _engine(name):
        return {'WORKBENCH': 'BLENDER_WORKBENCH', 'EEVEE': 'BLENDER_EEVEE'}.get(name.upper(), name)

    def _set_engine(sc, eng):
        try:
            sc.render.engine = eng
        except TypeError as e:
            print('engine err', e)
            raise

    def _snapshot(sc):
        r = sc.render
        return dict(engine=r.engine, rx=r.resolution_x, ry=r.resolution_y, pct=r.resolution_percentage,
                    fp=r.filepath, ft=r.film_transparent, cam=sc.camera, frame=sc.frame_current,
                    samples=sc.eevee.taa_render_samples, rt=sc.eevee.use_raytracing,
                    fmt=r.image_settings.file_format, cm=r.image_settings.color_mode)

    def _restore(sc, s):
        r = sc.render
        try:
            r.engine = s['engine']
        except TypeError:
            pass
        r.resolution_x, r.resolution_y, r.resolution_percentage = s['rx'], s['ry'], s['pct']
        r.filepath, r.film_transparent = s['fp'], s['ft']
        sc.eevee.taa_render_samples, sc.eevee.use_raytracing = s['samples'], s['rt']
        r.image_settings.file_format, r.image_settings.color_mode = s['fmt'], s['cm']
        sc.frame_set(s['frame'])
        sc.camera = s['cam']

    def _workbench(sc):
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

    def look(shot_or_cam, frame=None, path=None, engine='WORKBENCH', res=(960, 540), samples=8, tag=None,
             hide=None):
        """quick still of a shot camera at a frame into anim/look/. Markers are unbound during the render so the
        requested camera is used; every render setting is restored afterwards. hide: list of anim-only collections
        (e.g. a state's hide_groups) to hide for this render only, or True for the hide_groups of the shot's state
        (states without keyed visibility yet). Returns (path, seconds)."""
        sc = scene()
        camname, f = resolve(shot_or_cam, frame)
        if hide is True:
            hide = state_hide_groups(camname, f)
        tmp_hidden = []
        cam = bpy.data.objects[camname]
        eng = _engine(engine)
        wb = eng == 'BLENDER_WORKBENCH'
        os.makedirs(za.LOOK, exist_ok=True)
        path = path or za.LOOK + '%s-f%04d-%s%s.png' % (camname[len('anim_cam_'):], f, 'wb' if wb else 'ev',
                                                        ('-' + tag) if tag else '')
        snap = _snapshot(sc)
        marks = [(m, m.camera) for m in sc.timeline_markers]
        win = bpy.context.window
        wsc = win.scene
        t = time.time()
        try:
            for cn in (hide or []):
                c = coll(cn, create=False)
                if c is not None and not c.hide_render:
                    c.hide_render = True
                    tmp_hidden.append(c)
            win.scene = sc
            for m, _ in marks:
                m.camera = None
            sc.frame_set(f)
            sc.camera = cam
            _set_engine(sc, eng)
            r = sc.render
            r.resolution_x, r.resolution_y = res
            r.resolution_percentage = 100
            r.film_transparent = False
            if wb:
                _workbench(sc)
            else:
                sc.eevee.taa_render_samples = samples
            r.image_settings.file_format = 'PNG'
            r.image_settings.color_mode = 'RGB'
            r.filepath = path
            bpy.ops.render.render(write_still=True, scene=sc.name)
        finally:
            for m, c in marks:
                m.camera = c
            for c in tmp_hidden:
                c.hide_render = False
            _restore(sc, snap)
            win.scene = wsc
        return path, round(time.time() - t, 1)
    za.look = look

    def state_hide_groups(camname, frame):
        """hide_groups of the state a camera shows at a frame (shots.json); for S03 the CUT_FEED state applies from
        S03b on, for stills their own state."""
        cid = camname[len('anim_cam_'):]
        st = None
        if cid.startswith('ST'):
            st = shot(cid)['state']
        else:
            s = shot(cid[:3])
            st = s.get('state') or s.get('states')
            if cid == 'S03b':
                st = 'CUT_FEED'
        if isinstance(st, dict):
            return list(st.get('hide_groups', []))
        if not st:
            return []
        key = st.split()[0].split('→')[0].strip()
        spec = za.SHOTS['meta']['states'].get(key)
        return list(spec['hide_groups']) if spec else []
    za.state_hide_groups = state_hide_groups

    def render_range(start=None, end=None, max_frames=40, max_seconds=105, out=None, preview=False, log_it=True):
        """resumable frame render of ze155_anim: frames whose PNG exists are skipped; renders at most max_frames
        (and stops before max_seconds). Cameras switch by the timeline markers. Per-shot samples / raytracing come
        from shots.json (preview: 50 %, 8 samples, no raytracing, into anim/render/preview/)."""
        sc = scene()
        start = sc.frame_start if start is None else start
        end = sc.frame_end if end is None else end
        out = out or (za.PREVIEW if preview else za.FRAMES)
        os.makedirs(out, exist_ok=True)
        snap = _snapshot(sc)
        win = bpy.context.window
        wsc = win.scene
        done, skipped, t0, last = [], 0, time.time(), 0.0
        try:
            win.scene = sc
            r = sc.render
            r.image_settings.file_format = 'PNG'
            r.image_settings.color_mode = 'RGB'
            r.resolution_x, r.resolution_y = za.SHOTS['meta']['resolution']
            r.resolution_percentage = 50 if preview else 100
            r.film_transparent = False
            for f in range(start, end + 1):
                p = out + '%04d.png' % f
                if os.path.exists(p) and os.path.getsize(p) > 0:
                    skipped += 1
                    continue
                el = time.time() - t0
                if len(done) >= max_frames or (done and el + last > max_seconds):
                    break
                s = shot_at(f)
                rs = (s or {}).get('render', {})
                sc.eevee.taa_render_samples = 8 if preview else int(rs.get('samples', 32))
                sc.eevee.use_raytracing = False if preview else bool(rs.get('raytracing', False))
                sc.frame_set(f)
                tmp = out + '%04d_tmp.png' % f
                r.filepath = tmp
                tf = time.time()
                bpy.ops.render.render(write_still=True, scene=sc.name)
                os.replace(tmp, p)
                last = time.time() - tf
                done.append(f)
        finally:
            _restore(sc, snap)
            win.scene = wsc
        remaining = sum(1 for f in range(start, end + 1) if not os.path.exists(out + '%04d.png' % f))
        spf = round((time.time() - t0) / len(done), 2) if done else None
        res = dict(done=len(done), first=done[0] if done else None, last=done[-1] if done else None,
                   skipped=skipped, remaining=remaining, s_per_frame=spf, out=out)
        if log_it and done:
            log('- render_range%s chunk %d–%d done (%d frames), %.2f s/frame; %d still missing in %d–%d'
                % (' preview' if preview else '', done[0], done[-1], len(done), spf, remaining, start, end))
        return res
    za.render_range = render_range

    # ------------------------------------------------------------------ C0 setup (idempotent)
    def _copy_rna(dst, srcp, skip=()):
        n = 0
        for p in srcp.bl_rna.properties:
            k = p.identifier
            if k == 'rna_type' or k in skip or p.is_readonly or p.type in ('POINTER', 'COLLECTION'):
                continue
            try:
                setattr(dst, k, getattr(srcp, k))
                n += 1
            except Exception:
                pass
        return n

    def setup_scene():
        """create (or update) ze155_anim: EEVEE 1920x1080 @ 25 fps, frames 1-5275, colour management and units
        as ze155, world ze155_world (shared, not modified). Never touches ze155."""
        s = src()
        sc = bpy.data.scenes.get(za.SCENE) or bpy.data.scenes.new(za.SCENE)
        m = za.SHOTS['meta']
        r = sc.render
        try:
            r.engine = 'BLENDER_EEVEE'
        except TypeError as e:
            print('engine err', e)
            r.engine = s.render.engine
        r.resolution_x, r.resolution_y = m['resolution']
        r.resolution_percentage = 100
        r.fps, r.fps_base = m['fps'], 1.0
        sc.frame_start, sc.frame_end = m['frame_start'], m['frame_end']
        r.film_transparent = False
        r.image_settings.file_format = 'PNG'
        r.image_settings.color_mode = 'RGB'
        try:
            r.image_settings.color_depth = '8'
        except Exception:
            pass
        r.filepath = za.FRAMES
        sc.display_settings.display_device = s.display_settings.display_device
        v, v0 = sc.view_settings, s.view_settings
        v.view_transform = v0.view_transform
        v.look = v0.look
        v.exposure, v.gamma = v0.exposure, v0.gamma
        v.use_curve_mapping = v0.use_curve_mapping
        sc.sequencer_colorspace_settings.name = s.sequencer_colorspace_settings.name
        sc.world = s.world
        # Blender quirk: the RNA update of UnitSettings.system resets length/mass unit of the CONTEXT scene, not
        # the owner. Set units only while ze155_anim is the window scene, and verify ze155 afterwards.
        u, u0 = sc.unit_settings, s.unit_settings
        ukeys = ('system', 'system_rotation', 'length_unit', 'mass_unit', 'time_unit', 'temperature_unit',
                 'scale_length', 'use_separate')
        before = {k: getattr(u0, k) for k in ukeys}
        win = bpy.context.window
        wsc = win.scene
        win.scene = sc
        try:
            for k in ukeys:
                setattr(u, k, before[k])
        finally:
            win.scene = wsc
        changed = {k: getattr(u0, k) for k in ukeys if getattr(u0, k) != before[k]}
        if changed:
            raise RuntimeError('ze155 unit settings changed by setup_scene: %r (was %r)' % (changed, before))
        ne = _copy_rna(sc.eevee, s.eevee)
        sc.eevee.taa_render_samples = 32
        sc.eevee.use_raytracing = False
        return dict(scene=sc.name, eevee_props_copied=ne, engine=r.engine)
    za.setup_scene = setup_scene

    def setup_collections():
        sc = scene()
        for p in za.PARENTS + (za.RIG,):
            coll(p)
        for g in za.SHOTS['meta']['visibility_groups']:
            coll(g)
        for n in za.INT_COLLS + za.CUT_COLLS + za.FX_COLLS:
            coll(n)
        cc = coll(za.CUTTERS)
        cc.hide_render = True
        lc = lcoll(za.CUTTERS)
        if lc is not None:
            lc.hide_viewport = True
        return sorted(c.name for c in sc.collection.children_recursive)
    za.setup_collections = setup_collections

    def build_groups():
        """link ze155 objects into the ax_* groups of shots.json meta.visibility_groups. ax_static gets every
        render-visible object of ze155_parts / ze155_context that no other group lists. Rig, cutters, blockout and
        hide_render objects stay out. ax_always_replaced is hidden for render and in the anim viewport."""
        vg = za.SHOTS['meta']['visibility_groups']
        pool = {}
        for cn in ('ze155_parts', 'ze155_context'):
            for o in bpy.data.collections[cn].all_objects:
                pool[o.name] = o
        listed, missing, not_pool, hidden = {}, [], [], []
        for g, spec in vg.items():
            if not isinstance(spec['members'], list):
                continue
            for n in spec['members']:
                o = bpy.data.objects.get(n)
                if o is None:
                    missing.append((g, n))
                    continue
                if n not in pool:
                    not_pool.append((g, n))
                    continue
                if o.hide_render:
                    hidden.append((g, n))
                    continue
                if n in listed:
                    raise RuntimeError('%s listed in %s and %s' % (n, listed[n], g))
                listed[n] = g
        static = sorted(n for n, o in pool.items() if n not in listed and not o.hide_render)
        out_hidden = sorted(n for n, o in pool.items() if o.hide_render)
        # unlink ze155 objects that sit in a wrong ax group (re-run safety)
        want = dict(listed)
        want.update({n: 'ax_static' for n in static})
        overrides = {}
        for n, g in za.GROUP_OVERRIDES.items():
            if n in want and want[n] != g:
                overrides[n] = (want[n], g)
                want[n] = g
        for c in colls('ax_'):
            for o in list(c.objects):
                if is_ze(o) and want.get(o.name) != c.name:
                    c.objects.unlink(o)
        for n, g in want.items():
            link_ze(pool[n], g)
        c = ax('ax_always_replaced')
        c.hide_render = True
        lc = lcoll('ax_always_replaced')
        if lc is not None:
            lc.hide_viewport = True
        counts = {g: len(ax(g).objects) for g in vg}
        return dict(counts=counts, n_linked=len(want), n_static=counts.get('ax_static'), missing=missing,
                    overrides=overrides,
                    not_in_parts_or_context=not_pool, listed_but_hidden=hidden, pool_hidden_render=out_hidden,
                    groups={g: sorted(o.name for o in ax(g).objects) for g in vg})
    za.build_groups = build_groups

    def _look_rot(loc, target, up_hint=None):
        d = (Vector(target) - Vector(loc)).normalized()
        if up_hint is None and abs(d.z) < 0.999:
            return d.to_track_quat('-Z', 'Y').to_matrix()
        up = Vector(up_hint or (-1, 0, 0))
        zc = -d
        xc = up.cross(zc).normalized()
        yc = zc.cross(xc).normalized()
        return Matrix((xc, yc, zc)).transposed()

    def build_cameras(only=None):
        """the 24 cameras of shots.json (+ za.CAM_OVERRIDES) in anim_rig: keys for location, Track-To target empty
        anim_tgt_<id> and lens; ortho where specified; timeline markers at each shot camera's first frame.
        only: list of camera names to rebuild (markers are always rebuilt)."""
        sc = scene()
        rg = za.RIG
        made = []
        for name, spec, kind in cam_specs():
            if only and name not in only:
                continue
            cid = name[len('anim_cam_'):]
            keys = spec['keys'] if 'keys' in spec else [dict(frame=None, loc=spec['loc'], target=spec['target'],
                                                             lens_mm=spec.get('lens_mm', 50))]
            remove(name)
            remove('anim_tgt_' + cid)
            cd = bpy.data.cameras.get(name)
            if cd is None or cd.users:
                cd = bpy.data.cameras.new(name)
            cd.type = 'ORTHO' if spec['type'] == 'ORTHO' else 'PERSP'
            cd.sensor_width = 36.0
            cd.sensor_fit = 'AUTO'
            dmin = min((Vector(k['target']) - Vector(k['loc'])).length for k in keys)
            cd.clip_start = 0.02 if dmin < 3.0 else 0.1
            cd.clip_end = 250.0
            if cd.type == 'ORTHO':
                cd.ortho_scale = spec['ortho_scale_m']
            cam = new_obj(name, cd, rg)
            tgt = empty('anim_tgt_' + cid, rg, keys[0]['target'], size=0.08)
            vertical = any(abs((Vector(k['target']) - Vector(k['loc'])).normalized().z) > 0.999 for k in keys)
            if vertical:
                # straight down (ST5): Track-To is undefined, use an explicit rotation; image up = -X (inlet at
                # the top, lip at the bottom), image right = +Y (operator side)
                cam['tgt_note'] = 'vertical view: explicit rotation, image up -X, right +Y; target empty is a marker'
                cam.matrix_world = Matrix.Translation(keys[0]['loc']) @ _look_rot(keys[0]['loc'], keys[0]['target'],
                                                                                  (-1, 0, 0)).to_4x4()
            else:
                con = cam.constraints.new('TRACK_TO')
                con.name = 'track_tgt'
                con.target = tgt
                con.track_axis = 'TRACK_NEGATIVE_Z'
                con.up_axis = 'UP_Y'
                cam.rotation_euler = _look_rot(keys[0]['loc'], keys[0]['target']).to_euler()
            for k in keys:
                cam.location = k['loc']
                tgt.location = k['target']
                if cd.type == 'PERSP':
                    cd.lens = k['lens_mm']
                if k['frame'] is not None and len(keys) >= 1 and kind == 'shot':
                    cam.keyframe_insert('location', frame=k['frame'])
                    tgt.keyframe_insert('location', frame=k['frame'])
                    if cd.type == 'PERSP':
                        cd.keyframe_insert('lens', frame=k['frame'])
            interp = spec.get('interpolation', '')
            mode = 'LINEAR' if interp.startswith('LINEAR') else 'BEZIER'
            for idb in (cam, tgt, cd):
                set_interp(idb, mode)
            cam['shot'] = cid
            cam['kind'] = kind
            made.append(name)
        # markers bind the shot cameras
        sc.timeline_markers.clear()
        for name, spec, kind in cam_specs():
            if kind != 'shot':
                continue
            f = cam_start(name)
            mk = sc.timeline_markers.new(name[len('anim_cam_'):], frame=f)
            mk.camera = bpy.data.objects[name]
        sc.camera = bpy.data.objects[cam_specs()[0][0]]
        return made
    za.build_cameras = build_cameras

    def build_lights():
        """copies (not links) of the 5 ze155 area lights in anim_rig, outlines hidden in the anim viewport."""
        out = []
        for n in za.LIGHTS:
            s = bpy.data.objects[n]
            nn = 'anim_' + n
            o = copy_obj(s, nn, za.RIG)
            o['src_energy'] = s.data.energy
            o.hide_set(True, view_layer=vl())
            out.append((nn, o.data.type, o.data.energy))
        return out
    za.build_lights = build_lights

    def build_ctrl():
        """empty anim_ctrl with the speed factors (custom properties) that drivers read."""
        o = empty('anim_ctrl', za.RIG, (-4.0, -3.0, 0.0), size=0.4, kind='CUBE')
        props = dict(za.SHOTS['meta']['controller']['custom_props'])
        props.update(fps=float(za.FPS),
                     sc_step_deg=30.0, sc_step_s=3.0,              # screen disc +30 deg every 3 s (S09, fast-forward)
                     pellet_v_15D_mps=0.063, pellet_v_1D_mps=0.042,  # pitch x displayed rev/s (brief s7, M3)
                     bubble_v_vent1_mps=0.25, bubble_v_vent2_mps=0.15,
                     flow_dash_mps=0.8,                            # S14 dash scroll
                     lip_exaggeration=10.0,                        # S12 gap and travel drawn x10
                     light_scale=1.0)                              # S14/S15 dim the anim lights to 0.45
        for k, v in props.items():
            o[k] = float(v)
        o['note'] = ('Speed badges: screws %.0f rpm real / %.0f (display), pump %.0f rpm / %.0f, rolls and sheet real '
                     'speed. Drivers read these props.' % (props['screw_rpm_real'], props['drive_slow'],
                                                            props['pump_rpm_real'], props['pump_slow']))
        return {k: o[k] for k in props}
    za.build_ctrl = build_ctrl

    # ------------------------------------------------------------------ A1a additions: screw profile, free look
    # Erdmenger self-wiping 2-flight profile (interior_parts.json screw_profile). theta = polar angle about +X,
    # 0 = +Y at phase 0 (CCW seen from +X, i.e. +Y towards +Z); a point is (y, z) = r (cos(theta+phase), sin(theta+phase)).
    za.SCREW = dict(a=142.0, Ro=83.75, Rr=142.0 - 83.75, scale=0.995, bore_r=84.5, axis_y=71.0, axis_z=1200.0,
                    shaft_r=36.0)
    za.SCREW['psi'] = math.pi / 2 - 2 * math.acos(za.SCREW['a'] / (2 * za.SCREW['Ro']))   # tip angle 25.94 deg

    def screw_r(theta):
        """unscaled profile radius (mm) at polar angle theta (rad, 0 = centre of a tip)."""
        a, Ro, Rr, psi = za.SCREW['a'], za.SCREW['Ro'], za.SCREW['Rr'], za.SCREW['psi']
        t = theta % math.pi
        if t > math.pi / 2:
            t = math.pi - t
        if t <= psi / 2:
            return Ro
        if t >= math.pi / 2 - psi / 2:
            return Rr
        d = t + math.pi / 2 + psi / 2                       # theta - g with g = -(90 deg + psi/2)
        return Ro * math.cos(d) + math.sqrt(a * a - (Ro * math.sin(d)) ** 2)
    za.screw_r = screw_r

    def screw_profile(n_tip=2, n_flank=7, n_root=1, scale=None):
        """closed profile [(theta_rad, r_mm, is_land)], CCW from theta = 0 (tip centre). Vertices sit exactly on the
        tip/flank corners (+-psi/2, crisp land) and the flank/root joins; the flank is sampled uniformly along its
        arc (radius a, centre on r = Ro at -(90 deg + psi/2)). Scaled by za.SCREW['scale'] unless scale is given.
        Default 40 points (10 per quadrant)."""
        S = za.SCREW
        s = S['scale'] if scale is None else scale
        a, Ro, Rr, psi = S['a'], S['Ro'], S['Rr'], S['psi']
        g = -math.pi / 2 - psi / 2
        cx, cy = Ro * math.cos(g), Ro * math.sin(g)
        q = [(psi / 2 * k / n_tip, Ro, True) for k in range(n_tip)]
        p1 = (Ro * math.cos(psi / 2), Ro * math.sin(psi / 2))
        p2 = (Rr * math.cos(math.pi / 2 - psi / 2), Rr * math.sin(math.pi / 2 - psi / 2))
        f1 = math.atan2(p1[1] - cy, p1[0] - cx)
        f2 = math.atan2(p2[1] - cy, p2[0] - cx)
        for k in range(n_flank):
            f = f1 + (f2 - f1) * k / n_flank
            x, y = cx + a * math.cos(f), cy + a * math.sin(f)
            q.append((math.atan2(y, x), math.hypot(x, y), k == 0))
        for k in range(n_root + 1):
            q.append((math.pi / 2 - psi / 2 + psi / 2 * k / n_root, Rr, False))
        half = q[:-1] + [(math.pi - t, r, l) for (t, r, l) in reversed(q)][:-1]
        full = half + [(t + math.pi, r, l) for (t, r, l) in half]
        return [(t, r * s, l) for (t, r, l) in full]
    za.screw_profile = screw_profile

    def screw_phase(shaft, x_mm):
        """profile phase (deg, mod 360) of shaft 'a' or 'b' at world X from the screw_elements table (B = A + 90).
        KB elements return the phase of the disc that contains x."""
        rows = (za.PARTS if hasattr(za, 'PARTS') else load_parts())['screw_elements']['rows']
        for r in rows:
            if r['x_start_mm'] <= x_mm <= r['x_end_mm']:
                p0 = r['phase_A_start_deg']
                if r['type'] == 'KB':
                    k = min(int((x_mm - r['x_start_mm']) // r['kb_disc_width_mm']), r['kb_discs'] - 1)
                    p = p0 + k * r['kb_stagger_deg']
                else:
                    hand = -1 if r['hand'] == 'LH' else 1
                    p = p0 + hand * 360.0 * (x_mm - r['x_start_mm']) / r['pitch_mm']
                return (p + (90.0 if shaft == 'b' else 0.0)) % 360.0
        raise ValueError('x outside the screw: %r' % x_mm)
    za.screw_phase = screw_phase

    def look_free(loc, target, path, lens=50.0, engine='WORKBENCH', res=(960, 540), samples=16, frame=None,
                  show=(), hide=(), ortho=None, clip=(0.005, 200.0)):
        """still from a temporary camera (deleted afterwards, so the rig keeps its 24 cameras) into path.
        show / hide: anim-only collection names (anim_* or ax_*) whose hide_render is set False / True for this
        render only. ortho: ortho_scale in m for an orthographic camera. Every render setting is restored."""
        sc = scene()
        cd = bpy.data.cameras.new('za_tmp_look')
        cd.lens, cd.sensor_width = lens, 36.0
        cd.clip_start, cd.clip_end = clip
        if ortho:
            cd.type = 'ORTHO'
            cd.ortho_scale = ortho
        cam = bpy.data.objects.new('za_tmp_look', cd)
        coll(za.RIG).objects.link(cam)
        cam.location = Vector(loc)
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        eng = _engine(engine)
        wb = eng == 'BLENDER_WORKBENCH'
        snap = _snapshot(sc)
        marks = [(m, m.camera) for m in sc.timeline_markers]
        win = bpy.context.window
        wsc = win.scene
        changed = []
        t = time.time()
        try:
            for names, val in ((show, False), (hide, True)):
                for cn in names:
                    c = coll(cn, create=False)
                    if c is not None and c.hide_render != val:
                        changed.append((c, c.hide_render))
                        c.hide_render = val
            win.scene = sc
            for m, _ in marks:
                m.camera = None
            if frame is not None:
                sc.frame_set(frame)
            sc.camera = cam
            _set_engine(sc, eng)
            r = sc.render
            r.resolution_x, r.resolution_y = res
            r.resolution_percentage = 100
            r.film_transparent = False
            if wb:
                _workbench(sc)
            else:
                sc.eevee.taa_render_samples = samples
            r.image_settings.file_format = 'PNG'
            r.image_settings.color_mode = 'RGB'
            r.filepath = path
            bpy.ops.render.render(write_still=True, scene=sc.name)
        finally:
            for m, c in marks:
                m.camera = c
            for c, v in changed:
                c.hide_render = v
            _restore(sc, snap)
            win.scene = wsc
            bpy.data.objects.remove(cam, do_unlink=True)
            bpy.data.cameras.remove(cd)
        return path, round(time.time() - t, 1)
    za.look_free = look_free

    def cut_copy(src, name, co_mm, no, cname, cap_mat=None):
        """bisect + scanfill copy of an anim object in world space (identity matrix): keeps dot(p - co, no) <= 0 and
        caps the section with cap_mat. bmesh triangle_fill (scanfill) treats nested loops as holes, so a barrel
        section keeps its figure-8 bore and cooling bores open. Tested in A1a on int_barrel_hollow_* and
        int_dome_hollow_2 (Z 1200 and X 2450 / 4120). Refuses ze155 objects (copy them first)."""
        import bmesh
        o = bpy.data.objects[src] if isinstance(src, str) else src
        if is_ze(o):
            raise RuntimeError('cut_copy refuses ze155 object %s: copy it with za.copy_obj first' % o.name)
        dg = bpy.context.evaluated_depsgraph_get()
        oe = o.evaluated_get(dg)
        tmp = oe.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(tmp)
        oe.to_mesh_clear()
        bm.transform(o.matrix_world)
        n = Vector(no).normalized()
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-7,
                                     plane_co=Vector(co_mm) * 0.001, plane_no=n, clear_outer=True)
        cut = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
        mats = list(o.data.materials)
        cm = mat(cap_mat) if isinstance(cap_mat, str) else cap_mat
        if cm is not None and cm not in mats:
            mats.append(cm)
        ci = mats.index(cm) if cm is not None else 0
        if cut:
            fr = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=cut, normal=n)
            for f in fr['geom']:
                if isinstance(f, bmesh.types.BMFace):
                    f.material_index = ci
                    f.smooth = False
                    if f.normal.dot(n) < 0:
                        f.normal_flip()
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        for m in mats:
            me.materials.append(m)
        return new_obj(name, me, cname)
    za.cut_copy = cut_copy

    load_shots()
    guard_ze()
    bpy.app.driver_namespace['za'] = za
    return za


_za_install()
print('za helpers ok', len(vars(bpy.app.driver_namespace['za'])))
