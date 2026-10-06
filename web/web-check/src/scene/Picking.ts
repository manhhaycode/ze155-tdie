import * as THREE from 'three'
import type { ThreeEvent } from '@react-three/fiber'
import { MeshBVH, CENTER, acceleratedRaycast } from 'three-mesh-bvh'
import { reg } from './rig'
import { useUi } from '../store'
import { inSection } from './section'
import { SECTION_DEPTH_M } from './Cuts'
import type { SolidSectionRec } from '../data'

// PLAN-DOT1 §4.2.5 = r3f-snippets §3 (C1/N1): the filter lives inside mesh.raycast, there is no drei <Bvh>,
// and "installed" means `mesh.raycast === filteredRaycast` (function identity, not a userData flag).

const BVH_OPTIONS = { strategy: CENTER, maxLeafTris: 10, setBoundingBox: true }
let renderer: THREE.WebGLRenderer | null = null

export const isHelper = (o: THREE.Object3D) => o.userData.__helper === true

export const noRaycast: THREE.Object3D['raycast'] = () => {}

// Empties / groups: returning false makes three's Raycaster skip the whole (hidden) subtree.
// In practice only payload Groups are ever hidden (only payloads change `visible`).
export const emptyRaycast = function (this: THREE.Object3D) {
  return this.visible ? undefined : false
} as unknown as THREE.Object3D['raycast']

export const filteredRaycast = function (this: THREE.Mesh, raycaster: THREE.Raycaster, hits: THREE.Intersection[]) {
  if (!this.visible) return false // also prunes the outline hulls below
  const m = this.material as THREE.Material
  if (m.userData.zeGhost) return // ghosts are never picked
  const start = hits.length
  acceleratedRaycast.call(this, raycaster, hits) // all hits (firstHitOnly is never set); honours material.side
  const local = m.clippingPlanes
  const global = renderer?.clippingPlanes
  const hasLocal = !!local && local.length > 0
  const hasGlobal = !!global && global.length > 0
  if (!hasLocal && !hasGlobal) return
  for (let i = hits.length - 1; i >= start; i--) {
    const p = hits[i].point
    let cut = false
    if (hasLocal) for (const pl of local!) if (pl.distanceToPoint(p) < 0) { cut = true; break }
    if (!cut && hasGlobal) for (const pl of global!) if (pl.distanceToPoint(p) < 0) { cut = true; break }
    if (cut) hits.splice(i, 1) // the removed side
  }
  // review-flow-01 M3: a capped solid with a section draws its cap ON the plane (Cuts.ts). A back-face hit behind
  // the plane is that cap when the ray crosses the plane inside the solid: report it there, so a click selects
  // what the pixel shows (the roll, not the stand inside its journal volume). three sorts the hits afterwards.
  const section = this.userData.zeSection as SolidSectionRec | null
  if (!section || !hasLocal || !m.userData.zeCap || hits.length === start) return
  const ray = raycaster.ray
  _secPl.copy(local![0]).constant -= SECTION_DEPTH_M // the cap's depth: 1 mm into the kept side, as in the shader
  const P = ray.intersectPlane(_secPl, _secP)
  if (!P || !inSection(P, section)) return
  const t = ray.origin.distanceTo(P)
  _secNm.getNormalMatrix(this.matrixWorld)
  for (let i = start; i < hits.length; i++) {
    const h = hits[i]
    if (!h.face || h.distance <= t) continue
    if (_secN.copy(h.face.normal).applyMatrix3(_secNm).dot(ray.direction) <= 0) continue // a front face
    h.distance = t
    h.point.copy(P)
  }
} as unknown as THREE.Object3D['raycast']
const _secP = new THREE.Vector3()
const _secPl = new THREE.Plane()
const _secN = new THREE.Vector3()
const _secNm = new THREE.Matrix3()

/** Marks everything below a part mesh (drei Outlines hulls) as a non-raycast helper. */
function markHelpersBelow(mesh: THREE.Object3D) {
  for (const c of mesh.children)
    c.traverse((o) => {
      o.userData.__helper = true
      o.raycast = noRaycast
    })
}

/**
 * Idempotent: every run (StrictMode double effect, remount, the interior attached later) ends with the
 * filter installed on every mesh. Builds one CENTER BVH per (shared) geometry; returns the BVH ms spent.
 */
export function installRaycastFilter(root: THREE.Object3D, gl: THREE.WebGLRenderer): number {
  renderer = gl
  let ms = 0
  root.traverse((o) => {
    if (isHelper(o)) {
      o.raycast = noRaycast
      return
    }
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh) {
      o.raycast = emptyRaycast
      return
    }
    if (mesh.userData.ze?.part) markHelpersBelow(mesh)
    if (!mesh.geometry.boundsTree) {
      const t0 = performance.now()
      mesh.geometry.boundsTree = new MeshBVH(mesh.geometry, BVH_OPTIONS)
      ms += performance.now() - t0
    }
    mesh.raycast = filteredRaycast
  })
  reg.stats.bvh_ms += ms
  return ms
}

/** selfcheck `rayUnfiltered`: meshes (not helpers) whose raycast is not the filter. Must be 0, also in dev. */
export function unfilteredMeshes(root: THREE.Object3D | null) {
  let meshes = 0
  let empties = 0
  root?.traverse((o) => {
    if (isHelper(o)) return
    if ((o as THREE.Mesh).isMesh) {
      if (o.raycast !== filteredRaycast) meshes++
    } else if (o.raycast !== emptyRaycast) empties++
  })
  return { meshes, empties }
}

// ---- pointer handlers (on the <primitive object={lineScene}>) ----

export function onPointerMove(e: ThreeEvent<PointerEvent>) {
  e.stopPropagation() // nearest valid hit wins
  const id = reg.deviceOfObject(e.object)
  if (useUi.getState().hovered !== id) useUi.getState().hover(id)
}

export function onPointerOut(e: ThreeEvent<PointerEvent>) {
  // R3F passes the current hits; if the pointer moved onto another mesh, onPointerMove sets the new hover
  if (!e.intersections.length) useUi.getState().hover(null)
}

export function onClick(e: ThreeEvent<MouseEvent>) {
  if (e.delta > 4) return // orbit drag
  e.stopPropagation()
  const part = reg.partOfObject(e.object)
  const id = reg.deviceOfObject(e.object)
  useUi.getState().select(id, e.nativeEvent.altKey && part ? part.name : null)
}

export function onDoubleClick(e: ThreeEvent<MouseEvent>) {
  e.stopPropagation()
  const id = reg.deviceOfObject(e.object)
  const ui = useUi.getState()
  if (id && ui.selected !== id) ui.select(id)
  ui.zoomTo(id)
}
