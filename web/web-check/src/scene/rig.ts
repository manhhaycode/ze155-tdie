import * as THREE from 'three'
import type { Data, DeviceRec, NodeRec, RotorRec } from '../data'
import { prepareMesh } from './materials'
import { installRaycastFilter } from './Picking'

// PLAN-DOT1 §4.2.3: runtime rig. Device groups (attach), payloads, rotor pivots, materials, BVH + ray filter.
// Six rules (§2): name is the key (userData.name); only payloads change `visible`; never rotate an exported
// mesh node; never rely on child-mesh names; runtime metadata lives in userData.ze; the interior is attached
// into the line tree.

export interface Part {
  name: string
  meta: NodeRec
  node: THREE.Object3D
  payload: THREE.Object3D | null
  meshes: THREE.Mesh[]
}
export interface Device { id: string; rec: DeviceRec; group: THREE.Group; parts: Part[] }
export interface Rotor { rec: RotorRec; pivot: THREE.Object3D; axis: THREE.Vector3; angle: number; ready: boolean }

export interface LoadStats {
  bvh_ms: number
  line_rig_ms: number | null
  interior_rig_ms: number | null
  line_first_frame_ms: number | null
  interior_requested_at: number | null
  interior_ready_ms: number | null
}

const _box = new THREE.Box3()

/** true when the object and every ancestor is visible */
export function isShown(o: THREE.Object3D | null): boolean {
  for (; o; o = o.parent) if (!o.visible) return false
  return true
}

class Registry {
  data!: Data
  gl!: THREE.WebGLRenderer
  lineScene: THREE.Object3D | null = null
  parts = new Map<string, Part>()
  devices = new Map<string, Device>()
  sections = new Map<string, THREE.Group>()
  rotors: Rotor[] = []
  unknownNodes: string[] = []
  missingNodes: string[] = []
  quantizeSplit: string[] = [] // parts whose payload is an unnamed child (meshopt quantize moved the mesh)
  interiorLoaded = false
  interiorReady: Promise<void>
  private resolveInterior!: () => void
  stats: LoadStats = {
    bvh_ms: 0,
    line_rig_ms: null,
    interior_rig_ms: null,
    line_first_frame_ms: null,
    interior_requested_at: null,
    interior_ready_ms: null,
  }

  constructor() {
    this.interiorReady = new Promise<void>((r) => (this.resolveInterior = r))
  }

  markInteriorReady() {
    this.interiorLoaded = true
    this.resolveInterior()
  }

  /** walks up to the first object that carries a part (mesh: userData.ze.part, node: userData.ze.name) */
  partOfObject(o: THREE.Object3D | null): Part | null {
    for (; o; o = o.parent) {
      const z = o.userData.ze
      if (!z) continue
      if (z.part) return this.parts.get(z.part) ?? null
      if (z.name && this.parts.has(z.name)) return this.parts.get(z.name)!
    }
    return null
  }

  deviceOfObject(o: THREE.Object3D | null): string | null {
    const p = this.partOfObject(o)
    if (p) return p.meta.device_id
    for (; o; o = o.parent) if (o.userData.ze?.device_id) return o.userData.ze.device_id as string
    return null
  }

  /** from device.parts (data), never from a tree walk; visibleOnly = mesh and all ancestors visible */
  meshesOfDevice(id: string, visibleOnly = true): THREE.Mesh[] {
    const d = this.devices.get(id)
    const out: THREE.Mesh[] = []
    if (!d) return out
    for (const p of d.parts) for (const m of p.meshes) if (!visibleOnly || isShown(m)) out.push(m)
    return out
  }

  meshesOfPart(name: string, visibleOnly = true): THREE.Mesh[] {
    const p = this.parts.get(name)
    return p ? p.meshes.filter((m) => !visibleOnly || isShown(m)) : []
  }

  boxOfMeshes(meshes: THREE.Mesh[]): THREE.Box3 {
    const box = new THREE.Box3()
    for (const m of meshes) {
      const g = m.geometry
      if (!g.boundingBox) g.computeBoundingBox()
      m.updateWorldMatrix(true, false)
      box.union(_box.copy(g.boundingBox!).applyMatrix4(m.matrixWorld))
    }
    return box
  }

  boxOfDevice(id: string, visibleOnly = true): THREE.Box3 {
    return this.boxOfMeshes(this.meshesOfDevice(id, visibleOnly))
  }

  boxOfPart(name: string): THREE.Box3 {
    return this.boxOfMeshes(this.parts.get(name)?.meshes ?? [])
  }
}

export const reg = new Registry()

// ---------------------------------------------------------------------------------------------------------

function collectNamed(root: THREE.Object3D): Map<string, THREE.Object3D> {
  const m = new Map<string, THREE.Object3D>()
  root.traverse((o) => {
    if (o !== root && typeof o.userData.name === 'string') m.set(o.userData.name, o)
  })
  return m
}

const isNamed = (o: THREE.Object3D) => typeof o.userData.name === 'string'

/**
 * Step 3: a named Mesh with named children (raw, un-quantized GLB) becomes an Object3D with the same
 * name and TRS; the mesh moves below it with an identity transform and loses its name. No-op on the
 * compressed GLBs (meshopt quantize already did this split).
 */
function normalizeMeshParents(named: Map<string, THREE.Object3D>) {
  for (const [name, node] of named) {
    if (!(node as THREE.Mesh).isMesh || !node.children.some(isNamed)) continue
    const holder = new THREE.Object3D()
    holder.name = node.name
    holder.userData = node.userData
    holder.position.copy(node.position)
    holder.quaternion.copy(node.quaternion)
    holder.scale.copy(node.scale)
    const parent = node.parent!
    parent.children[parent.children.indexOf(node)] = holder
    holder.parent = parent
    node.parent = null
    for (const c of node.children.filter(isNamed)) holder.add(c) // same local TRS: holder = old node TRS
    node.userData = {}
    node.name = ''
    node.position.set(0, 0, 0)
    node.quaternion.identity()
    node.scale.set(1, 1, 1)
    holder.add(node)
    named.set(name, holder)
  }
}

function checkNames(named: Map<string, THREE.Object3D>, file: 'line' | 'interior', data: Data) {
  for (const name of named.keys()) {
    const meta = data.nodes[name]
    if (!meta || meta.file !== file) reg.unknownNodes.push(name)
  }
  for (const [name, meta] of Object.entries(data.nodes))
    if (meta.file === file && !named.has(name)) reg.missingNodes.push(name)
  const unk = reg.unknownNodes.length
  const mis = reg.missingNodes.length
  if (unk || mis) console.error(`[rig ${file}] unknownNodes=${unk} missingNodes=${mis}`, reg.unknownNodes, reg.missingNodes)
}

/** Step 4: 10 sec_<group> and 190 dev_<id> under the line scene, identity transforms. */
function makeGroups(scene: THREE.Object3D, data: Data) {
  for (const s of data.devices.sections) {
    const g = new THREE.Group()
    g.name = `sec_${s.group}`
    g.userData.ze = { kind: 'section', group: s.group }
    scene.add(g)
    reg.sections.set(s.group, g)
  }
  for (const rec of data.devices.devices) {
    let sec = reg.sections.get(rec.group)
    if (!sec) {
      sec = new THREE.Group()
      sec.name = `sec_${rec.group}`
      sec.userData.ze = { kind: 'section', group: rec.group }
      scene.add(sec)
      reg.sections.set(rec.group, sec)
    }
    const g = new THREE.Group()
    g.name = `dev_${rec.device_id}`
    g.userData.ze = { kind: 'device', device_id: rec.device_id }
    sec.add(g)
    reg.devices.set(rec.device_id, { id: rec.device_id, rec, group: g, parts: [] })
  }
  scene.updateMatrixWorld(true)
}

/** Step 5: every root node of the file goes into dev_<device_id> of the line tree (attach keeps world pose). */
function attachRoots(fileRoot: THREE.Object3D, data: Data) {
  for (const child of [...fileRoot.children]) {
    if (!isNamed(child)) continue
    const meta = data.nodes[child.userData.name as string]
    if (!meta) continue // unknown: stays where it is, counted as orphan
    const dev = reg.devices.get(meta.device_id)
    if (!dev) {
      console.error(`[rig] device ${meta.device_id} of ${child.userData.name} not in devices.json`)
      continue
    }
    dev.group.attach(child)
  }
}

/** Step 6: payload rule + userData.ze. Returns the parts of this file. */
function makeParts(named: Map<string, THREE.Object3D>, file: 'line' | 'interior', data: Data): Part[] {
  const out: Part[] = []
  for (const [name, node] of named) {
    const meta = data.nodes[name]
    if (!meta || meta.file !== file) continue
    let payload: THREE.Object3D | null = null
    if (meta.kind !== 'pivot') {
      if (!node.children.some(isNamed)) payload = node // Mesh, or Group of unnamed meshes (multi-material)
      else {
        const unnamed = node.children.filter((c) => !isNamed(c))
        if (unnamed.length === 1) {
          payload = unnamed[0]
          reg.quantizeSplit.push(name)
        } else if (unnamed.length > 1) console.error(`[rig] ${name}: ${unnamed.length} unnamed children, no payload`)
      }
    }
    const meshes: THREE.Mesh[] = []
    if (payload) {
      const walk = (o: THREE.Object3D) => {
        if ((o as THREE.Mesh).isMesh) meshes.push(o as THREE.Mesh)
        for (const c of o.children) if (!isNamed(c)) walk(c)
      }
      walk(payload)
    }
    for (const m of meshes) m.userData.ze = { part: name }
    node.userData.ze = { ...meta, name }
    const part: Part = { name, meta, node, payload, meshes }
    reg.parts.set(name, part)
    reg.devices.get(meta.device_id)?.parts.push(part)
    out.push(part)
  }
  return out
}

/** Step 7: pivots for slice-1 rotors whose attach nodes all live in this file. */
function makePivots(named: Map<string, THREE.Object3D>, data: Data) {
  for (const rec of data.rotors) {
    if (rec.slice !== 1) continue
    if (reg.rotors.some((r) => r.rec.id === rec.id)) continue
    const nodes = rec.attach.map((n) => named.get(n))
    if (nodes.some((n) => !n)) continue
    const dev = reg.devices.get(rec.device_id)
    if (!dev) continue
    const pivot = new THREE.Object3D()
    pivot.name = rec.pivot
    pivot.position.fromArray(rec.pivot_m)
    pivot.userData.ze = { kind: 'rotor', device_id: rec.device_id, rotor: rec.id }
    dev.group.add(pivot)
    pivot.updateMatrixWorld(true)
    for (const n of nodes) pivot.attach(n!)
    reg.rotors.push({ rec, pivot, axis: new THREE.Vector3(...rec.axis).normalize(), angle: 0, ready: true })
  }
}

export function rigLine(scene: THREE.Object3D, data: Data, gl: THREE.WebGLRenderer): void {
  if (scene.userData.zeRigged) return // StrictMode runs layout effects twice in dev
  const t0 = performance.now()
  reg.data = data
  reg.gl = gl
  scene.updateMatrixWorld(true)
  const named = collectNamed(scene)
  checkNames(named, 'line', data)
  normalizeMeshParents(named)
  makeGroups(scene, data)
  attachRoots(scene, data)
  const parts = makeParts(named, 'line', data)
  makePivots(named, data)
  for (const p of parts) for (const m of p.meshes) prepareMesh(m, p.meta, data)
  installRaycastFilter(scene, gl)
  reg.lineScene = scene
  scene.userData.zeRigged = true
  reg.stats.line_rig_ms = performance.now() - t0
}

export function rigInterior(scene: THREE.Object3D, data: Data, gl: THREE.WebGLRenderer): boolean {
  if (scene.userData.zeRigged || !reg.lineScene) return false
  const t0 = performance.now()
  const line = reg.lineScene
  scene.updateMatrixWorld(true)
  line.updateMatrixWorld(true)
  const named = collectNamed(scene)
  checkNames(named, 'interior', data)
  normalizeMeshParents(named)
  attachRoots(scene, data) // into dev_<owner> of the LINE tree
  const parts = makeParts(named, 'interior', data)
  // load state, not recorded: resetCuts returns to exactly this
  for (const p of parts) if (p.payload) p.payload.visible = false
  makePivots(named, data) // rot_screw_a / rot_screw_b
  for (const p of parts) for (const m of p.meshes) prepareMesh(m, p.meta, data)
  installRaycastFilter(line, gl) // idempotent; builds the interior BVHs
  scene.userData.zeRigged = true
  reg.stats.interior_rig_ms = performance.now() - t0
  if (reg.stats.interior_requested_at !== null)
    reg.stats.interior_ready_ms = performance.now() - reg.stats.interior_requested_at
  reg.markInteriorReady()
  return true
}
