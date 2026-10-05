# R3F reference snippets for `web-check/` (contract 1.1)

These are short reference snippets for the sandbox builder (stream B). They follow `model-contract.json` 1.1: node names, userData keys, the per-state cut model (`hide` / `swap` / `clip` / `show_whole` / `show_clipped` / `ghost`), rotors, clips and the closed rule. UI strings are Vietnamese; code and comments are English.

## Versions checked

Each API below was checked against the library source or type definitions of these versions on 2026-10-05:

| Package | Version | What was checked |
|---|---|---|
| three | 0.186.1 (r186) | `Raycaster.intersect`: no visibility check, and `raycast() === false` prunes the subtree; `GLTFLoader` (extras, mesh groups, child mesh names come from the glTF mesh); `compileAsync`; `meshphysical` shader chunks; `linearToOutputTexel` / `gl_FragColor` |
| @react-three/fiber | 9.8.1 | `core/events.ts`: hits are de-duplicated per object (`uuid/index/instanceId`) **before** `events.filter`, so filtering must happen inside `mesh.raycast`; the `gl` prop goes through `applyProps` |
| @react-three/drei | 10.7.9 | `useGLTF`, `Outlines` (**`screenspace={false}` is the pixel-thickness branch**; `clippingPlanes`), `CameraControls`, `Html`, `useAnimations`, `Environment`, `Lightformer`. **`Bvh` is not used:** its effect cleanup sets `child.raycast = Mesh.prototype.raycast` on every mesh with a `boundsTree` (`core/Bvh.js:76-81`), which drops the §3 filter on StrictMode's dev remount (N1) |
| three-mesh-bvh | 0.8.3 (drei's range) | `MeshBVH` + `SAH` (options as drei's `Bvh` defaults); `acceleratedRaycast` returns every hit unless `raycaster.firstHitOnly === true`, honours `material.side`, and falls back to `Mesh.prototype.raycast` when the geometry has no `boundsTree` |
| three-stdlib | 2.36.1 | GLTFLoader: `EXT_meshopt_compression` and `KHR_mesh_quantization` yes; `KHR_meshopt_compression` no |
| camera-controls | 3.1.2 | `setLookAt`, `fitToBox(box, transition, {padding*})`, `enabled` |

**Build check:** all TS/TSX blocks pass `tsc --strict` (TypeScript 5.9.3) in a throwaway probe, using exactly these package versions and a stub zustand store.

**Node probe (no WebGL), same versions:** §3, §6 and §7 were compiled and run on a synthetic scene. The filter is re-installed after a Bvh-style reset, a click on a cap keeps the far back-face hit, FREE hides the DRAIN fills and the disc range, and FULL → FREE → FULL and fixed → FREE → fixed give back the same visible set.

**Not yet done:** the snippets have not run in a browser. Shader patches, picking, the cap look and the Outlines thickness still need the sandbox.

Conventions:
- three.js coordinates are `(x, z, −y)` of Blender.
- Units are metres.
- `reg` is the registry from §2.
- `CutState` matches `public/data/cut_states.json`, which `tools/make_cut_states.py` writes with resolved node names only.

---

## 1. Canvas and loading the two GLBs (meshopt, no Draco)

```tsx
// src/App.tsx
import * as THREE from 'three'
import { Suspense, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { CameraControls, Environment, Lightformer } from '@react-three/drei'
import { LineModel, InteriorModel } from './scene/Models'
import { useUi } from './store'

const selfcheck = new URLSearchParams(location.search).has('selfcheck')

export default function App() {
  const controls = useRef<CameraControls>(null)
  const interiorWanted = useUi((s) => s.interiorWanted) // true on the first cut / ghost / free clip
  return (
    <Canvas
      camera={{ position: [-9, 6.5, -9], fov: 35, near: 0.05, far: 400 }} // S01 key 1
      gl={{ antialias: true, localClippingEnabled: true, toneMapping: THREE.NeutralToneMapping }}
      dpr={selfcheck ? 1 : [1, 2]} // budgets are defined at DPR 1
      onPointerMissed={() => useUi.getState().select(null)}
    >
      <color attach="background" args={['#e9ecef']} />
      <Suspense fallback={null}><LineModel /></Suspense>
      <Suspense fallback={null}>{interiorWanted && <InteriorModel />}</Suspense>
      <CameraControls ref={controls} makeDefault smoothTime={0.35} />
      <Environment resolution={256} frames={1}>
        <Lightformer form="rect" intensity={2.5} position={[3, 10, 0]} rotation-x={Math.PI / 2} scale={[24, 8, 1]} />
        <Lightformer form="rect" intensity={1.2} position={[3, 3, -10]} scale={[24, 4, 1]} />
        <Lightformer form="rect" intensity={0.8} position={[3, 3, 10]} rotation-y={Math.PI} scale={[24, 4, 1]} />
      </Environment>
      <directionalLight position={[5, 12, 6]} intensity={1.2} />
    </Canvas>
  )
}
```

```tsx
// src/scene/Models.tsx
import { useEffect, useMemo } from 'react'
import { useThree } from '@react-three/fiber'
import { useGLTF, useAnimations } from '@react-three/drei'
import { reg } from './Registry'
import { prepareMaterials } from './materials'
import { installRaycastFilter, onPointerMove, onPointerOut, onClick, onDoubleClick } from './Picking'

const LINE = '/models/line.glb'
const INTERIOR = '/models/interior.glb'
useGLTF.preload(LINE, false, true) // useDraco = false, useMeshopt = true

function useModel(path: string, file: 'line' | 'interior') {
  const gltf = useGLTF(path, false, true)
  const gl = useThree((s) => s.gl)
  useMemo(() => { prepareMaterials(gltf.scene); reg.add(gltf.scene, file) }, [gltf.scene, file])
  const { actions } = useAnimations(gltf.animations, gltf.scene) // one mixer per file, rooted in that file
  useEffect(() => reg.addActions(actions), [actions])
  // builds the BVH and installs the hit filter (§3). No drei <Bvh>: its cleanup resets mesh.raycast (N1).
  // Safe to run twice (StrictMode) or again after a remount: it only re-assigns the same functions.
  useEffect(() => installRaycastFilter(gltf.scene, gl), [gltf.scene, gl])
  return gltf
}

export function LineModel() {
  const gltf = useModel(LINE, 'line')
  return <primitive object={gltf.scene} onPointerMove={onPointerMove} onPointerOut={onPointerOut} onClick={onClick} onDoubleClick={onDoubleClick} />
}

export function InteriorModel() {
  const gltf = useModel(INTERIOR, 'interior')
  useMemo(() => { gltf.scene.visible = false }, [gltf.scene]) // load state; cut states change it only through setVisible (§6)
  return <primitive object={gltf.scene} onPointerMove={onPointerMove} onPointerOut={onPointerOut} onClick={onClick} onDoubleClick={onDoubleClick} />
}
```

## 2. Registry and materials

```ts
// src/scene/Registry.ts
import * as THREE from 'three'
import type { AnimationAction } from 'three'

const PART_KINDS = new Set(['part', 'interior', 'fill', 'ghost', 'marker'])
export const isHelper = (o: THREE.Object3D) => !!o.userData.__helper // outline hulls, peel clones, box helpers
export const ownerPart = (o: THREE.Object3D | null) => {
  while (o && !PART_KINDS.has(o.userData.kind)) o = o.parent
  return o
}
export const deviceIdOf = (o: THREE.Object3D | null): string | null => {
  while (o && !o.userData.device_id) o = o.parent
  return o ? (o.userData.device_id as string) : null
}
export const isVisibleDeep = (o: THREE.Object3D | null) => {
  for (; o; o = o.parent) if (!o.visible) return false
  return true
}
export const isGhost = (o: THREE.Object3D | null) => {
  for (; o; o = o.parent) if (o.userData.__ghost) return true
  return false
}

class Registry {
  byName = new Map<string, THREE.Object3D>() // only nodes with userData.kind (never glTF child-mesh names)
  devices = new Map<string, THREE.Object3D[]>() // dev_<id> (line) + ih_<id> / dev_screws (interior)
  actions: Record<string, AnimationAction[]> = {}
  roots: THREE.Object3D[] = []
  add(root: THREE.Object3D, _file: 'line' | 'interior') {
    if (this.roots.includes(root)) return // idempotent (StrictMode runs useMemo twice in dev)
    this.roots.push(root)
    root.traverse((o) => {
      const k = o.userData.kind as string | undefined
      if (!k) return
      this.byName.set((o.userData.name as string) ?? o.name, o) // GLTFLoader keeps the raw node name in userData.name
      if (k === 'device' || k === 'int_host') {
        const id = o.userData.device_id as string
        this.devices.set(id, [...(this.devices.get(id) ?? []), o])
      }
    })
  }
  addActions(a: Record<string, AnimationAction | null>) {
    for (const [n, act] of Object.entries(a)) if (act && !(this.actions[n] ??= []).includes(act)) this.actions[n].push(act)
  }
  meshesOfDevice(id: string) {
    const out: THREE.Mesh[] = []
    for (const n of this.devices.get(id) ?? [])
      n.traverse((o) => { if ((o as THREE.Mesh).isMesh && !isHelper(o) && isVisibleDeep(o)) out.push(o as THREE.Mesh) })
    return out
  }
}
export const reg = new Registry()
```

```ts
// src/scene/materials.ts
import * as THREE from 'three'
import { ownerPart } from './Registry'
import { makeFillMaterial } from './FillMaterial'
import { makeGhostMaterial } from './GhostMaterial'

const OVERRIDES: Record<string, () => THREE.Material> = {
  ze_sheet_pet: () => new THREE.MeshPhysicalMaterial({ color: '#7FB7B0', transparent: true, opacity: 0.35, roughness: 0.08, metalness: 0, depthWrite: false, side: THREE.DoubleSide }),
  ze_melt_curtain: () => new THREE.MeshStandardMaterial({ color: '#ED9E38', emissive: '#7A2E00', emissiveIntensity: 0.4, transparent: true, opacity: 0.8, roughness: 0.05, side: THREE.DoubleSide }),
  za_ghost_vent: () => makeGhostMaterial(),
  za_sc_screenpack: () => new THREE.MeshStandardMaterial({ color: '#2A3038', metalness: 0.6, roughness: 0.5 }),
  za_sc_breaker: () => new THREE.MeshStandardMaterial({ color: '#8A9099', metalness: 1, roughness: 0.35 }),
}
const made = new Map<string, THREE.Material>()
const doubleSided = new Map<string, THREE.Material>()
const prepared = new WeakSet<THREE.Object3D>()
export const useFillShader = { current: false } // Đợt 2 switches the fills to FillMaterial

export function prepareMaterials(root: THREE.Object3D) {
  if (prepared.has(root)) return
  prepared.add(root)
  root.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh) return
    const part = ownerPart(mesh)
    const src = mesh.material as THREE.Material
    mesh.userData.capColor = CAP_BY_MATERIAL[src.name] ?? null
    mesh.userData.closed = (part?.userData.closed === true && part?.userData.cap !== 'none') || part?.userData.cap === 'force'
    if (OVERRIDES[src.name]) {
      if (!made.has(src.name)) made.set(src.name, OVERRIDES[src.name]())
      mesh.material = made.get(src.name)!
      return
    }
    if (part?.userData.kind === 'fill' && useFillShader.current) { mesh.material = makeFillMaterial(part.userData as any); return }
    if (!mesh.userData.closed) { // open or flipped: lit DoubleSide copy, no cap
      let m = doubleSided.get(src.uuid)
      if (!m) { m = src.clone(); m.side = THREE.DoubleSide; doubleSided.set(src.uuid, m) }
      mesh.material = m
    } else {
      src.side = THREE.FrontSide // exporter wrote doubleSided:true everywhere; closed solids cull back faces
    }
  })
}
export const CAP_BY_MATERIAL: Record<string, string | null> = { /* generated from model-contract.json "materials": ze_steel: '#B84533', … */ }
```

## 3. Picking that survives clipping (C1)

R3F keeps only the **nearest** hit per mesh before `events.filter` runs. A filter would therefore drop the removed-half hit, and the visible hit behind it on the same mesh would already be gone. The fix filters inside `mesh.raycast`.

**One owner of `mesh.raycast` (N1).** drei `<Bvh>` is not used. Its effect cleanup sets `raycast = Mesh.prototype.raycast` on every mesh that has a `boundsTree`. StrictMode (on in the create-vite template) runs that cleanup once in dev, so a wrapped filter would be dropped under `npm run dev`. `installRaycastFilter` builds the BVH itself and assigns shared module functions. "Installed" means `mesh.raycast === filteredRaycast`, checked by function identity rather than a `userData` flag. A flag would survive `clone()`, but `raycast` does not.

```ts
// src/scene/Picking.ts
import * as THREE from 'three'
import type { ThreeEvent } from '@react-three/fiber'
import { MeshBVH, SAH, acceleratedRaycast } from 'three-mesh-bvh'
import { deviceIdOf, isGhost, isHelper, isVisibleDeep, ownerPart } from './Registry'
import { useUi } from '../store'

const BVH_OPTIONS = { strategy: SAH, maxDepth: 40, maxLeafTris: 10, setBoundingBox: true } // drei Bvh defaults
let renderer: THREE.WebGLRenderer | null = null // global (free) clipping planes

const noRaycast = () => {}
// empties / groups: returning false makes three's Raycaster skip the whole hidden subtree
const emptyRaycast = function (this: THREE.Object3D) { return this.visible ? undefined : false } as THREE.Object3D['raycast']
const filteredRaycast = function (this: THREE.Mesh, raycaster: THREE.Raycaster, hits: THREE.Intersection[]) {
  if (!this.visible || isGhost(this)) return
  const start = hits.length
  acceleratedRaycast.call(this, raycaster, hits) // all hits (firstHitOnly never set), material.side honoured
  const m = this.material as THREE.Material
  const planes = [...(m.clippingPlanes ?? []), ...(renderer?.clippingPlanes ?? [])]
  if (!planes.length) return
  for (let i = hits.length - 1; i >= start; i--)
    if (planes.some((p) => p.distanceToPoint(hits[i].point) < 0)) hits.splice(i, 1) // removed side
}

// Idempotent: every run (StrictMode double effect, remount, new subtree) ends with the filter installed.
export function installRaycastFilter(root: THREE.Object3D, gl: THREE.WebGLRenderer) {
  renderer = gl
  root.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh) { o.raycast = emptyRaycast; return }
    if (isHelper(mesh)) { mesh.raycast = noRaycast; return }
    if (!mesh.geometry.boundsTree) mesh.geometry.boundsTree = new MeshBVH(mesh.geometry, BVH_OPTIONS) // once per (shared) geometry
    mesh.raycast = filteredRaycast
  })
}
// selfcheck `rayUnfiltered` (N1): must be 0 after load, also under `npm run dev`
export function unfilteredMeshes(root: THREE.Object3D) {
  let n = 0
  root.traverse((o) => { if ((o as THREE.Mesh).isMesh && !isHelper(o) && o.raycast !== filteredRaycast) n++ })
  return n
}

export function onPointerMove(e: ThreeEvent<PointerEvent>) {
  e.stopPropagation() // nearest valid hit wins
  if (!isVisibleDeep(e.object)) return
  useUi.getState().hover(deviceIdOf(e.object))
}
export function onPointerOut() { useUi.getState().hover(null) }
export function onClick(e: ThreeEvent<MouseEvent>) {
  if (e.delta > 4) return // orbit drag
  e.stopPropagation()
  const part = ownerPart(e.object)
  useUi.getState().select(deviceIdOf(e.object), e.nativeEvent.altKey ? ((part?.userData.name as string) ?? null) : null)
}
export function onDoubleClick(e: ThreeEvent<MouseEvent>) {
  e.stopPropagation()
  useUi.getState().zoomTo(deviceIdOf(e.object))
}
```

- **Cap variants are DoubleSide (§6).** When you click a cut face, the ray hits the back face of the far wall of the same closed mesh. That hit survives the filter, so the device behind the cap is selected (acceptance check A5b). This needs every hit per mesh, so never set `raycaster.firstHitOnly = true`.
- **Peel clones** are marked `__helper` and get `noRaycast`. Calling `installRaycastFilter` again on new subtrees (outline hulls, peel clones) is safe. Clones do not copy `raycast`, and the function is re-assigned on every run.

## 4. Outline and bounding box (I1)

drei 10.7.9 `Outlines` takes pixel thickness when `screenspace={false}`; the `true` branch offsets in local units. It does not forward a ref, so the hull meshes it adds under the part mesh are found by traversal. They are marked as helpers and are not raycast.

```tsx
// src/scene/Selection.tsx
import * as THREE from 'three'
import { useEffect, useMemo } from 'react'
import { createPortal, useThree } from '@react-three/fiber'
import { Outlines } from '@react-three/drei'
import { reg } from './Registry'
import { useUi } from '../store'

function DeviceOutline({ id, color, px, creased }: { id: string; color: string; px: number; creased: boolean }) {
  const gl = useThree((s) => s.gl)
  const meshes = useMemo(() => reg.meshesOfDevice(id), [id])
  useEffect(() => {
    // Outlines (no ref forwarding) adds a group + hull mesh under the part mesh in a layout effect.
    // Part meshes are leaves, so everything below them is a hull: mark it and stop it from being raycast.
    for (const m of meshes) m.traverse((o) => { if (o !== m) { o.userData.__helper = true; o.raycast = () => {} } })
  })
  return (
    <>
      {meshes.map((m) => {
        const local = ((m.material as THREE.Material).clippingPlanes ?? []) as THREE.Plane[]
        return createPortal(
          <Outlines screenspace={false} thickness={px} color={color} angle={creased ? Math.PI : 0}
            clippingPlanes={[...local, ...gl.clippingPlanes]} />, m)
      })}
    </>
  )
}

export function Selection() {
  const { hovered, selected } = useUi()
  const box = useMemo(() => {
    if (!selected) return null
    const b = new THREE.Box3()
    for (const n of reg.devices.get(selected) ?? []) b.expandByObject(n)
    return b
  }, [selected])
  return (
    <>
      {hovered && hovered !== selected && <DeviceOutline id={hovered} color="#9fd3ff" px={2} creased={false} />}
      {selected && <DeviceOutline id={selected} color="#ff8a1f" px={3} creased />}
      {box && <box3Helper args={[box, 0xff8a1f]} userData={{ __helper: true }} raycast={() => null} />}
    </>
  )
}
```

**Info panel:** `devices.json[selected]` gives `name_vi`, `name_en`, `group`, `function`, `details`, `connects_to` and `bbox_m`; show dimensions in mm.

## 5. Zoom to a device

`Bounds` from drei needs controls with `target` and `update()` (OrbitControls). With `CameraControls`, use `fitToBox` instead.

```ts
import * as THREE from 'three'
import type { CameraControls } from '@react-three/drei'
import { reg } from './scene/Registry'

export function zoomToDevice(controls: CameraControls, id: string) {
  const box = new THREE.Box3()
  for (const n of reg.devices.get(id) ?? []) box.expandByObject(n)
  if (box.isEmpty()) return
  const pad = Math.max(0.15, box.getSize(new THREE.Vector3()).length() * 0.15)
  void controls.fitToBox(box, true, { paddingTop: pad, paddingBottom: pad, paddingLeft: pad, paddingRight: pad })
}
```

## 6. Fixed cut states: hybrid model (I2, I3, I5, I7)

**State keys:**
- `hide`: nodes hidden in the state.
- `swap`: `{exterior: [interior…]}`. Every key is hidden and its values are shown. If a value does not resolve (for example in a Đợt 1 GLB), the key stays visible and is clipped instead.
- `clip`: nodes clipped with the state plane, with a runtime cap if the mesh is closed.
- `show_whole`: interior nodes shown unclipped: pre-cuts, whole screws, ghosts, markers.
- `show_clipped`: interior nodes shown and clipped with the state plane.
- `ghost`: nodes drawn with GhostMaterial and made non-pickable.

```ts
// src/scene/Cuts.ts
import * as THREE from 'three'
import { reg, isHelper } from './Registry'
import { makeGhostMaterial } from './GhostMaterial'

type V3 = [number, number, number]
export type CutState = {
  plane: { normal: V3; constant: number } | null
  hide: string[]; swap: Record<string, string[]>; clip: string[]
  show_whole: string[]; show_clipped: string[]; ghost: string[]
  peel: { offset_m: V3; duration_s: number } | null; clips_on_enter: string[]
}

const variants = new Map<string, THREE.Material>()
const original = new Map<THREE.Mesh, THREE.Material>()
const changedVis = new Map<THREE.Object3D, boolean>()
const ghostMat = makeGhostMaterial()

export function cutVariant(src: THREE.Material, planes: THREE.Plane[], key: string, cap: string | null) {
  const id = `${src.uuid}|${key}|${cap}`
  let m = variants.get(id)
  if (m) return m
  m = src.clone()
  m.clippingPlanes = planes.length ? planes : null // [] = only the global (free) plane applies
  m.side = THREE.DoubleSide // back faces must render (cap) and be hit by the raycast (§3)
  if (cap) {
    const uCap = { value: new THREE.Color(cap) }
    m.onBeforeCompile = (shader) => {
      shader.uniforms.uCapColor = uCap
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <clipping_planes_pars_fragment>', '#include <clipping_planes_pars_fragment>\nuniform vec3 uCapColor;')
        .replace('#include <clipping_planes_fragment>', `#include <clipping_planes_fragment>
  if (!gl_FrontFacing) {
    float hatch = step(0.5, fract((gl_FragCoord.x + gl_FragCoord.y) * 0.1));
    gl_FragColor = linearToOutputTexel(vec4(uCapColor * mix(0.78, 1.0, hatch), 1.0));
    return;
  }`)
    }
    m.customProgramCacheKey = () => 'ze-cap'
  }
  variants.set(id, m)
  return m
}

// The only way cut code changes visibility (Cuts, FreeClip, Clips). resetCuts restores every recorded change,
// so FULL is the load state again and leaving FREE gives back FULL or any fixed state exactly (N2).
export function setVisible(o: THREE.Object3D | undefined, v: boolean) {
  if (!o) return
  if (!changedVis.has(o)) changedVis.set(o, o.visible)
  o.visible = v
}
function setMaterial(mesh: THREE.Mesh, m: THREE.Material) {
  if (!original.has(mesh)) original.set(mesh, mesh.material as THREE.Material)
  mesh.material = m
}
export function clipObject(o: THREE.Object3D, planes: THREE.Plane[], key: string) {
  o.traverse((c) => {
    const mesh = c as THREE.Mesh
    if (!mesh.isMesh || isHelper(mesh)) return
    const src = original.get(mesh) ?? (mesh.material as THREE.Material)
    setMaterial(mesh, cutVariant(src, planes, key, mesh.userData.closed ? (mesh.userData.capColor as string | null) : null))
  })
}
export function ghostObject(o: THREE.Object3D) {
  o.userData.__ghost = true
  o.traverse((c) => { const mesh = c as THREE.Mesh; if (mesh.isMesh && !isHelper(mesh)) setMaterial(mesh, ghostMat) })
}
export function resetCuts(gl: THREE.WebGLRenderer) {
  for (const [mesh, m] of original) mesh.material = m
  original.clear()
  for (const [o, v] of changedVis) o.visible = v
  changedVis.clear()
  reg.byName.forEach((o) => { delete o.userData.__ghost })
  gl.clippingPlanes = []
}
function showChain(o: THREE.Object3D) {
  setVisible(o, true)
  o.traverse((c) => { if (c !== o && !c.userData.kind) setVisible(c, true) }) // glTF child meshes of a Group, not sibling parts
  for (let p = o.parent; p; p = p.parent) setVisible(p, true)
}
const expand = (n: string) => {
  const m = /^(.*_)(\d+)\.\.(\d+)$/.exec(n)
  if (!m) return [n]
  const out: string[] = []
  for (let i = +m[2]; i <= +m[3]; i++) out.push(m[1] + String(i).padStart(m[2].length, '0'))
  return out
}
export const nodes = (names: string[]) => names.flatMap(expand).map((n) => reg.byName.get(n)).filter((o): o is THREE.Object3D => !!o)

export function applyCutState(gl: THREE.WebGLRenderer, id: string, s: CutState | null, interiorRoot: THREE.Object3D | null) {
  resetCuts(gl) // back to the load state (interior root hidden again)
  if (!s || id === 'FULL') return
  if (interiorRoot) { // start from "all interior hidden", then show what the state lists
    setVisible(interiorRoot, true)
    interiorRoot.traverse((o) => { if (o !== interiorRoot && o.userData.kind && o.userData.kind !== 'device' && o.userData.kind !== 'int_host') setVisible(o, false) })
  }
  const plane = s.plane ? [new THREE.Plane(new THREE.Vector3(...s.plane.normal), s.plane.constant)] : []
  for (const o of nodes(s.hide)) setVisible(o, false)
  for (const [ext, ints] of Object.entries(s.swap)) {
    const targets = nodes(ints)
    const e = reg.byName.get(ext)
    if (!e) continue
    if (ints.length === 0 || targets.length > 0) setVisible(e, false) // partner already shown by another key, or replacement present
    else if (plane.length) clipObject(e, plane, id) // missing replacement (Đợt 1): clip the exterior instead
  }
  for (const o of nodes(s.clip)) if (plane.length) clipObject(o, plane, id)
  for (const o of nodes(s.show_whole)) showChain(o)
  for (const o of nodes(s.show_clipped)) { showChain(o); if (plane.length) clipObject(o, plane, id) }
  for (const o of nodes(s.ghost)) { showChain(o); ghostObject(o) }
}

// first-switch cost: compile every state's programs once after interior.glb loads (A5 ≤ 200 ms)
export async function precompileStates(gl: THREE.WebGLRenderer, scene: THREE.Object3D, camera: THREE.Camera,
  states: Record<string, CutState>, interiorRoot: THREE.Object3D | null) {
  for (const [id, s] of Object.entries(states)) { applyCutState(gl, id, s, interiorRoot); await gl.compileAsync(scene, camera) }
  applyCutState(gl, 'FULL', null, interiorRoot)
}
```

**Peel (runtime "lột vỏ"), when entering a state with `peel`:**
1. For every node in `clip`, and every `swap` key whose replacement exists, add `new THREE.Mesh(mesh.geometry, peelMat)` with the same `matrixWorld`. `peelMat` = `src.clone()` with `clippingPlanes = [plane.clone().negate()]`, transparent. Mark it `userData.__helper = true` and `raycast = () => {}`.
2. Over `peel.duration_s`, move it by `peel.offset_m` and fade `opacity` 1 → 0.
3. Dispose the clone and keep the shared geometry.

`die_open` targets are never in `hide` or `clip` (I7). Play the clip on entering CUT_DIE_PLAN; when the state is left, stop it (`action.stop()` returns the nodes to rest).

## 7. Free clipping plane (X / Y / Z) with caps

```ts
// src/scene/FreeClip.ts
import * as THREE from 'three'
import { reg } from './Registry'
import { clipObject, nodes, resetCuts, setVisible, type CutState } from './Cuts'

// cut_states.json "FREE": swap = free_swap; hide = DRAIN valve fills + screen-changer disc set (N3)
export type FreeState = Pick<CutState, 'hide' | 'swap'>
const AXES = { x: new THREE.Vector3(-1, 0, 0), y: new THREE.Vector3(0, -1, 0), z: new THREE.Vector3(0, 0, -1) }
export function setFreeClip(gl: THREE.WebGLRenderer, axis: 'x' | 'y' | 'z' | null, offset = 0, flip = false,
  free: FreeState = { hide: [], swap: {} }, interiorRoot: THREE.Object3D | null = null) {
  resetCuts(gl) // axis null = leave FREE: back to FULL exactly, because every change below is recorded (N2)
  if (!axis) return
  const n = AXES[axis].clone().multiplyScalar(flip ? -1 : 1)
  gl.clippingPlanes = [new THREE.Plane(n, flip ? -offset : offset)] // keeps coordinate <= offset (flip: >= offset)
  if (interiorRoot) {
    setVisible(interiorRoot, true)
    interiorRoot.traverse((o) => {
      const k = o.userData.kind, role = o.userData.role
      if (k === 'ghost' || k === 'marker' || role === 'cut_only') setVisible(o, false) // FREE shows only full sources (M6)
    })
  }
  for (const o of nodes(free.hide)) setVisible(o, false) // RUN valve fills only; no disc rim above the hood (N3)
  for (const [ext, ints] of Object.entries(free.swap)) {
    const e = reg.byName.get(ext)
    if (e && (ints.length === 0 || ints.some((i) => reg.byName.has(i)))) setVisible(e, false)
  }
  for (const root of reg.roots) clipObject(root, [], 'free') // cap variant on closed meshes; [] = global plane only
}
```

- Moving the slider only changes `gl.clippingPlanes[0].constant`; no material rebuild is needed.
- **Valve in FREE:** only the RUN fill set shows, since `hide` holds `p_int_fill_valve_drain_bolt` and `_drain_port`. Playing `valve_run` in FREE uses `playClip('valve_run', false, '')`; the switch in §11 shows one set at a time.
- **Screen changer in FREE:** the disc set (`p_int_sc_disc`, `p_int_sc_screens_01..12`, `p_int_fill_sc_cavities`) is hidden. Its rim sticks 67–190 mm through the kept exterior hood. Hiding it is the simplest fix; GHOST_SC and ST1 show the disc under the raised ghost hood.
- **Check (N2):** `__ze.cutRoundTrip()` (§14) must return `ok: true`.

## 8. Rotating parts from userData (12 rotors)

```tsx
// src/scene/Rotors.tsx
import * as THREE from 'three'
import { useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { reg } from './Registry'
import { useUi } from '../store'

export function Rotors() {
  const mode = useUi((s) => s.rotorMode) // 'off' | 'slow' | 'real'
  const loaded = useUi((s) => s.loadedFiles)
  const rotors = useMemo(() => {
    const list: { o: THREE.Object3D; axis: THREE.Vector3; rpm: number; slow: number }[] = []
    for (const root of reg.roots) root.traverse((o) => {
      if (o.userData.kind !== 'rotor') return
      list.push({ o, axis: new THREE.Vector3(...(o.userData.axis as [number, number, number])).normalize(),
        rpm: o.userData.rpm as number, slow: (o.userData.display_slow as number) ?? 1 })
    })
    return list
  }, [loaded])
  useFrame((_, dt) => {
    if (mode === 'off') return
    const step = Math.min(dt, 0.1)
    for (const r of rotors) r.o.rotateOnAxis(r.axis, (r.rpm / 60) * 2 * Math.PI * (mode === 'real' ? 1 : 1 / r.slow) * step)
  })
  return null
}
```

**Expected directions:**
- screws `−300` about +X: the RH flights appear to travel +X;
- gearbox input `−1118`, counter `+571`; the outputs ride on the screw rotors;
- pump gear top `+69` about `[0, 0, −1]`: its top moves +X;
- rolls `+/−/+` about `[0, 0, −1]`: both nip surfaces move +X.

## 9. Fill shader skeleton (Đợt 2)

```ts
// src/scene/FillMaterial.ts
import * as THREE from 'three'

export const fillGlobals = { uTime: { value: 0 }, uMode: { value: 0 }, uRpm: { value: 300 }, uSlow: { value: 20 } }
type FillUD = { x_range_m?: [number, number] | null; pitch_m?: number | null; temp_c: [number, number];
  flow_mode: 'x' | 'radial'; origin_m?: [number, number, number]; radius_m?: number }

export function makeFillMaterial(ud: FillUD) {
  const m = new THREE.MeshStandardMaterial({ color: '#ED9E38', roughness: 0.25, metalness: 0, transparent: true, opacity: 0.6, depthWrite: false, side: THREE.DoubleSide })
  const local = {
    uX0: { value: ud.x_range_m?.[0] ?? 0 }, uX1: { value: ud.x_range_m?.[1] ?? 1 }, uPitch: { value: ud.pitch_m ?? 0.169 },
    uTIn: { value: ud.temp_c[0] }, uTOut: { value: ud.temp_c[1] }, uRadial: { value: ud.flow_mode === 'radial' ? 1 : 0 },
    uOrigin: { value: new THREE.Vector3(...(ud.origin_m ?? [0, 0, 0])) }, uRadius: { value: ud.radius_m ?? 1.25 }, uFront: { value: 1 },
  }
  m.onBeforeCompile = (s) => {
    Object.assign(s.uniforms, fillGlobals, local)
    s.vertexShader = s.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vZeW;')
      .replace('#include <project_vertex>', '#include <project_vertex>\nvZeW = (modelMatrix * vec4(transformed, 1.0)).xyz;')
    s.fragmentShader = s.fragmentShader
      .replace('#include <common>', `#include <common>
varying vec3 vZeW;
uniform float uTime, uMode, uRpm, uSlow, uX0, uX1, uPitch, uTIn, uTOut, uRadial, uRadius, uFront;
uniform vec3 uOrigin;
vec3 heat(float t) { t = clamp(t, 0., 1.);
  return mix(mix(vec3(0.03, 0.15, 0.8), vec3(0.9, 0.75, 0.05), smoothstep(0., 0.6, t)), vec3(0.85, 0.06, 0.03), smoothstep(0.6, 1., t)); }`)
      .replace('#include <color_fragment>', `#include <color_fragment>
  float x = vZeW.x;
  float u = clamp((x - uX0) / max(uX1 - uX0, 1e-4), 0., 1.);
  if (uRadial > 0.5) { u = clamp(length(vZeW.xz - uOrigin.xz) / uRadius, 0., 1.); if (u > uFront) discard; }
  float speed = uPitch * uRpm / 60.0 / uSlow;
  float s = fract((x - uTime * speed) / uPitch);
  vec3 c = mix(vec3(0.86, 0.84, 0.76), vec3(0.85, 0.34, 0.04), smoothstep(1.52, 1.90, x)); // pellet -> melt (linear)
  c *= mix(0.8, 1.0, smoothstep(0.0, 0.1, s) * (1.0 - smoothstep(0.45, 0.55, s)));
  if (uMode > 0.5) c = heat((mix(uTIn, uTOut, u) - 20.0) / 280.0);
  diffuseColor.rgb = c;`)
  }
  m.customProgramCacheKey = () => 'ze-fill'
  return m
}
// useFrame((_, dt) => { fillGlobals.uTime.value += dt })
```

- Fills are open meshes (their ends are open), so they get no cap.
- In the fixed states, the `_lo`, `_y0` and `x*` fill pre-cuts show clean end faces.
- In FREE, a clipped fill keeps its own material through `clipObject` (`cap = null`, because the fill is not closed).

## 10. Ghost material

```ts
// src/scene/GhostMaterial.ts
import * as THREE from 'three'
export function makeGhostMaterial(color = '#B4D6F5', face = 0.1, edge = 0.75) {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: { uColor: { value: new THREE.Color(color) }, uFace: { value: face }, uEdge: { value: edge } },
    vertexShader: /* glsl */`
      varying vec3 vN; varying vec3 vV;
      void main() { vec4 mv = modelViewMatrix * vec4(position, 1.0);
        vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
    fragmentShader: /* glsl */`
      uniform vec3 uColor; uniform float uFace, uEdge; varying vec3 vN; varying vec3 vV;
      void main() { float f = 1.0 - abs(dot(normalize(vN), normalize(vV)));
        gl_FragColor = vec4(uColor, mix(uFace, uEdge, f * f));
        #include <colorspace_fragment>
      }`,
  })
}
```

## 11. Named clips (`useAnimations`) and the valve fill switch

```ts
// src/scene/Clips.ts
import * as THREE from 'three'
import { reg } from './Registry'
import { setVisible } from './Cuts'

const RUN = ['p_int_fill_valve_run_bolt', 'p_int_fill_valve_run_out']
const DRAIN = ['p_int_fill_valve_drain_bolt', 'p_int_fill_valve_drain_port']
function valveFills(run: boolean, suffix: '' | '_lo') { // recorded, so the next state change undoes it (N2)
  for (const n of RUN) setVisible(reg.byName.get(n + suffix), run)
  for (const n of DRAIN) setVisible(reg.byName.get(n + suffix), !run)
}

export function playClip(name: 'valve_run' | 'sc_index' | 'die_open', reverse = false, fillSuffix: '' | '_lo' = '_lo') {
  const acts = reg.actions[name] ?? [] // die_open has one action per file
  for (const a of acts) {
    a.reset()
    a.setLoop(name === 'sc_index' ? THREE.LoopRepeat : THREE.LoopOnce, Infinity)
    a.clampWhenFinished = true
    a.timeScale = reverse ? -1 : 1
    if (reverse) a.time = a.getClip().duration
    a.play()
  }
  if (name === 'valve_run' && acts[0]) {
    valveFills(false, fillSuffix) // DRAIN while the bolt moves
    const mixer = acts[0].getMixer()
    const done = () => { valveFills(true, fillSuffix); mixer.removeEventListener('finished', done) }
    mixer.addEventListener('finished', done)
  }
}
// check: after playClip('valve_run') + 1.3 s, reg.byName.get('anim_valve_bolt')!.position.z ≈ 0 (starts at +0.20)
```

## 12. `tour.json` step → `CameraControls` (Đợt 3)

```ts
// src/scene/Tour.ts (logic only)
import * as THREE from 'three'
import { useEffect, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import type { CameraControls } from '@react-three/drei'

type V3 = [number, number, number]
type Key = { t: number; pos: V3; target: V3; lens_mm: number }
const ease = (x: number) => x * x * (3 - 2 * x)
const lerp3 = (a: V3, b: V3, s: number): V3 => [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s, a[2] + (b[2] - a[2]) * s]

export function sampleKeys(keys: Key[], t: number): Key {
  if (t <= keys[0].t) return keys[0]
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1]
    if (t <= b.t) {
      const s = ease((t - a.t) / (b.t - a.t))
      return { t, pos: lerp3(a.pos, b.pos, s), target: lerp3(a.target, b.target, s), lens_mm: a.lens_mm + (b.lens_mm - a.lens_mm) * s }
    }
  }
  return keys[keys.length - 1]
}
export function setLens(cam: THREE.PerspectiveCamera, lens: number) { cam.filmGauge = 36; cam.setFocalLength(lens) }
export function goToStep(controls: CameraControls, cam: THREE.PerspectiveCamera, k0: Key) {
  setLens(cam, k0.lens_mm)
  return controls.setLookAt(...k0.pos, ...k0.target, true)
}
export function useTourPlayback(step: { camera: { keys: Key[] }; duration_s: number } | null, playing: boolean, controls: CameraControls | null) {
  const cam = useThree((s) => s.camera) as THREE.PerspectiveCamera
  const t = useRef(0)
  useEffect(() => { t.current = 0 }, [step])
  useFrame((_, dt) => {
    if (!step || !playing || !controls) return
    t.current = Math.min(t.current + dt, step.duration_s)
    const k = sampleKeys(step.camera.keys, t.current)
    setLens(cam, k.lens_mm)
    void controls.setLookAt(...k.pos, ...k.target, false)
  })
}
```

- Set `controls.enabled = false` while a step plays.
- The tour state `FLOWS` (S14/S15) maps to FULL.
- S03 is one step with two camera segments, plus `state_changes: [{t: 7.0, state: "CUT_FEED"}]`.

**Tour JSON shape** (stream C, from `shots.json` + `CAM_OVERRIDES`; coordinates `(x, z, −y)`, times `(frame − first frame) / 25`):

```json
{ "version": 1, "units": "m", "up": "Y", "sensor_mm": 36,
  "steps": [ { "id": "S04", "title_vi": "…", "duration_s": 18, "state": "CUT_Z_BARREL", "state_changes": [],
    "camera": { "type": "persp", "keys": [ { "t": 0, "pos": [-0.35, 2.9, -2.2], "target": [0.5, 1.2, 0], "lens_mm": 30 } ] },
    "labels": [ { "text": "…", "anchor": [0.9, 1.25, 0], "t_in": 0.6, "t_out": 7.4 } ],
    "hud": { "title": "…", "values": ["…"], "footer": "* = giả định (không có nguồn công bố)" },
    "speed_badge_vi": "Vít chậm 20×", "motion": { "rotors": "slow", "clips": [], "peel": true } } ],
  "stills": [ { "id": "ST2", "title_vi": "…", "state": "CUT_X2450", "camera": { "pos": [3.05, 1.45, -0.42], "target": [2.45, 1.2, 0], "lens_mm": 60 } } ] }
```

## 13. `Html` label

```tsx
import { Html } from '@react-three/drei'

export function Label({ text, anchor, visible }: { text: string; anchor: [number, number, number]; visible: boolean }) {
  if (!visible) return null
  return (
    <Html position={anchor} center distanceFactor={10} zIndexRange={[20, 0]} style={{ pointerEvents: 'none' }}>
      <div className="ze-label">{text}</div>
    </Html>
  )
}
```

`occlude` stays off: it raycasts every frame. Labels follow the tour timing instead.

## 14. Test hooks (`window.__ze`)

```ts
// src/test/hooks.ts
import * as THREE from 'three'
import type { RootState } from '@react-three/fiber'
import { reg, deviceIdOf, isVisibleDeep } from '../scene/Registry'
import { applyCutState, type CutState } from '../scene/Cuts'
import { setFreeClip } from '../scene/FreeClip'
import { unfilteredMeshes } from '../scene/Picking'

const visibleKey = () => {
  const v: string[] = []
  reg.byName.forEach((o, n) => { if (isVisibleDeep(o)) v.push(n) })
  return v.sort().join(',')
}
// N2: FULL -> FREE -> FULL, and every fixed state -> FREE -> same state, must give the same visible-node set.
// FULL is first, so its "before" is the set right after load.
export function cutRoundTrip(gl: THREE.WebGLRenderer, states: Record<string, CutState>, interiorRoot: THREE.Object3D | null) {
  const bad: string[] = []
  for (const id of ['FULL', ...Object.keys(states).filter((k) => k !== 'FULL' && k !== 'FREE')]) {
    const enter = () => applyCutState(gl, id, id === 'FULL' ? null : states[id], interiorRoot)
    enter()
    const before = visibleKey()
    setFreeClip(gl, 'x', 3.0, false, states.FREE, interiorRoot)
    if (id === 'FULL') setFreeClip(gl, null); else enter() // leave FREE
    if (visibleKey() !== before) bad.push(id)
  }
  applyCutState(gl, 'FULL', null, interiorRoot)
  return { ok: bad.length === 0 && gl.clippingPlanes.length === 0, bad }
}

export function installHooks(state: RootState) {
  const canvas = state.gl.domElement
  const dispatch = (x: number, y: number, alt = false) => {
    const r = canvas.getBoundingClientRect()
    const init: PointerEventInit = { clientX: r.left + x, clientY: r.top + y, bubbles: true, altKey: alt, pointerId: 1, pointerType: 'mouse', isPrimary: true, button: 0 }
    canvas.dispatchEvent(new PointerEvent('pointermove', init))
    canvas.dispatchEvent(new PointerEvent('pointerdown', init))
    canvas.dispatchEvent(new PointerEvent('pointerup', init))
    canvas.dispatchEvent(new MouseEvent('click', init))
  }
  const pickAt = (x: number, y: number) => { // same mesh.raycast filters as the pointer events
    const ndc = new THREE.Vector2((x / state.size.width) * 2 - 1, -(y / state.size.height) * 2 + 1)
    const rc = new THREE.Raycaster()
    rc.setFromCamera(ndc, state.camera)
    const hit = rc.intersectObjects(reg.roots, true)[0]
    return hit ? { device_id: deviceIdOf(hit.object), point: hit.point.toArray() } : null
  }
  let frames = 0
  const tick = () => { frames++; requestAnimationFrame(tick) }
  requestAnimationFrame(tick)
  ;(window as any).__ze = {
    devices: () => [...reg.devices.keys()],
    clickAt: (x: number, y: number, o?: { alt?: boolean }) => dispatch(x, y, o?.alt),
    pickAt,
    project: (id: string) => {
      const b = new THREE.Box3()
      for (const n of reg.devices.get(id) ?? []) b.expandByObject(n)
      const p = b.getCenter(new THREE.Vector3()).project(state.camera)
      return { x: ((p.x + 1) / 2) * state.size.width, y: ((1 - p.y) / 2) * state.size.height }
    },
    stats: async () => {
      const f0 = frames
      await new Promise((r) => setTimeout(r, 3000))
      const i = state.gl.info
      return { fps: (frames - f0) / 3, calls: i.render.calls, triangles: i.render.triangles, geometries: i.memory.geometries, devices: reg.devices.size }
    },
    selfcheck: () => {
      let orphans = 0
      for (const r of reg.roots) r.traverse((o) => { if ((o as THREE.Mesh).isMesh && !o.userData.__helper && !deviceIdOf(o)) orphans++ })
      const rayUnfiltered = reg.roots.reduce((n, r) => n + unfilteredMeshes(r), 0) // N1: 0, also under npm run dev
      return { devices: reg.devices.size, orphans, rayUnfiltered, clips: Object.keys(reg.actions) }
    },
    // setState, setFreeClip, select, rotors, playClip, tour, orbitTest, capCheck -> wire to the modules above
    // cutRoundTrip: () => cutRoundTrip(state.gl, cutStates, interiorRoot)  (cut_states.json + the interior scene)
  }
}
// <Canvas onCreated={installHooks}>; with ?selfcheck also render <pre id="selfcheck">…SELFCHECK DONE</pre>
```

**`capCheck(state, device)` (acceptance check A5b):**
1. Apply the state.
2. Project a point on the cut plane inside the device bbox.
3. Call `pickAt` there.
4. Expect `device_id === device`, for example `barrel_b3` in CUT_Z_BARREL and `int_barrel_hollow_b3`'s host in CUT_X2450.

`renderer.info.render.calls` counts only the last frame; read it after a frame in the state you want to measure.
