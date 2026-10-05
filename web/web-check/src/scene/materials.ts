import * as THREE from 'three'
import type { Data, NodeRec } from '../data'
import { makeGhostMaterial } from './GhostMaterial'

// PLAN-DOT1 §3.3.6 / §4.2.4. Runs once per mesh (WeakSet), so it is safe for both GLBs and for re-runs.
const prepared = new WeakSet<THREE.Mesh>()
const overrides = new Map<string, THREE.Material>() // material name -> shared override
const doubleSided = new Map<string, THREE.Material>() // source uuid -> shared lit DoubleSide copy
export const unknownMaterials = new Set<string>()

const SIDES: Record<string, THREE.Side> = { FrontSide: THREE.FrontSide, BackSide: THREE.BackSide, DoubleSide: THREE.DoubleSide }

function makeOverride(name: string, src: THREE.Material, o: Record<string, unknown> & { type: string }): THREE.Material {
  let m: THREE.Material
  if (o.type.startsWith('GhostMaterial')) {
    m = makeGhostMaterial(
      (o.color as string) ?? '#B4D6F5',
      (o.alpha_face as number) ?? 0.1,
      (o.alpha_edge as number) ?? 0.75,
    )
  } else if (o.type.startsWith('FillMaterial')) {
    // Đợt 1: keep the exported amber, translucent, no depth write, DoubleSide (FillMaterial is Đợt 2)
    m = src.clone()
    m.transparent = true
    m.opacity = 0.6
    m.depthWrite = false
    m.side = THREE.DoubleSide
  } else {
    const p: Record<string, unknown> = {}
    for (const k of ['color', 'emissive', 'emissiveIntensity', 'transparent', 'opacity', 'roughness', 'metalness', 'depthWrite'])
      if (o[k] !== undefined) p[k] = o[k]
    if (typeof o.side === 'string') p.side = SIDES[o.side] ?? THREE.FrontSide
    m = o.type === 'MeshPhysicalMaterial' ? new THREE.MeshPhysicalMaterial(p) : new THREE.MeshStandardMaterial(p)
    m.userData.zeSideFixed = typeof o.side === 'string'
  }
  m.name = name
  m.userData.zeOverride = true
  if (o.type.startsWith('GhostMaterial') || o.type.startsWith('FillMaterial')) m.userData.zeSideFixed = true
  return m
}

/** closed (effective) = (meta.closed && cap !== 'none') || cap === 'force' */
export const effectiveClosed = (meta: NodeRec | null | undefined) =>
  !!meta && ((meta.closed === true && meta.cap !== 'none') || meta.cap === 'force')

export function prepareMesh(mesh: THREE.Mesh, meta: NodeRec | null, data: Data) {
  if (prepared.has(mesh)) return
  prepared.add(mesh)
  const src = mesh.material as THREE.Material
  const name = src.name
  const rec = data.materials.materials[name]
  if (!rec) unknownMaterials.add(name)
  const closed = effectiveClosed(meta)
  mesh.userData.zeCapColor = rec?.cap_color ?? null
  mesh.userData.zeHatch = rec?.cap_class === 'steel'
  mesh.userData.zeClosed = closed

  let base = src
  if (rec?.web === 'override' && rec.three_override) {
    let m = overrides.get(name)
    if (!m) overrides.set(name, (m = makeOverride(name, src, rec.three_override)))
    base = m
    if (m.userData.zeSideFixed) {
      mesh.material = m
      return
    }
  }
  if (!closed) {
    // open or flipped mesh: shared lit DoubleSide copy, never capped
    let m = doubleSided.get(base.uuid)
    if (!m) {
      m = base.clone()
      m.side = THREE.DoubleSide
      m.userData.zeOpenCopy = true
      doubleSided.set(base.uuid, m)
    }
    mesh.material = m
  } else {
    base.side = THREE.FrontSide // exporter wrote doubleSided: true everywhere; closed solids cull back faces
    mesh.material = base
  }
}
