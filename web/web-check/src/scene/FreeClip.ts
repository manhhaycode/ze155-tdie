import * as THREE from 'three'
import type { Axis, FixedStateId } from '../data'
import { reg } from './rig'
import { applyState, clipPart, ensureInterior, partVisible, resetCuts, setPartVisible } from './Cuts'

// PLAN-DOT1 §4.2.6 FREE + AMENDMENTS (M, FREE note): ONE shared local plane on the clipped materials,
// never renderer.clippingPlanes, so the ground, the Box3Helper and the outline hulls are not cut.
// three re-projects material.clippingPlanes from this instance every frame: changing constant/normal is
// seen by every clipped material, the raycast filter and the outlines at once (no material rebuild).

export const freePlane = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 3)
// `axis` and `offset` are three.js (the store, the hooks); the UI shows Blender axes (review I3):
// Blender X = three x, Blender Y = three −z, Blender Z = three y. Unflipped, every axis keeps the side where
// the BLENDER coordinate is <= the plane, like the fixed states: "X = 2 450" keeps x <= 2.45, "Y = 0"
// (CUT_FEED, normal [0, 0, 1]) keeps Blender y <= 0, "Z = 1 200" keeps the part below 1.2 m. Blender Y is
// three −z, so for three z the kept side is z >= offset (normal [0, 0, 1]); free z = 0 equals CUT_FEED's plane.
const AXES: Record<Axis, [number, number, number]> = { x: [-1, 0, 0], y: [0, -1, 0], z: [0, 0, 1] }
const AXIS_INDEX: Record<Axis, 0 | 1 | 2> = { x: 0, y: 1, z: 2 }
const cur = { axis: 'x' as Axis, offset: 3, flip: false }

/** three x / y: keeps coordinate <= offset; three z: keeps z >= offset (Blender y <= −offset). flip: the other side */
export function setFreePlane(axis: Axis, offset: number, flip: boolean) {
  cur.axis = axis
  cur.offset = offset
  cur.flip = flip
  const n = AXES[axis]
  const s = flip ? -1 : 1
  freePlane.normal.set(n[0] * s, n[1] * s, n[2] * s)
  freePlane.constant = -n[AXIS_INDEX[axis]] * s * offset // plane through the point at `offset` on the axis
}

/** Call only from inside the state queue. */
export async function enterFree(axis: Axis, offset: number, flip: boolean): Promise<void> {
  await ensureInterior()
  resetCuts(reg.gl)
  setFreePlane(axis, offset, flip)
  const F = reg.data.states.FREE
  // interior payloads whose role is in show_roles (slice 2 included, Q3); hide_roles stay hidden (load state)
  for (const p of reg.parts.values())
    if (p.meta.file === 'interior' && p.meta.role && F.show_roles.includes(p.meta.role)) setPartVisible(p, true)
  for (const n of F.hide) {
    const p = reg.parts.get(n)
    if (p) setPartVisible(p, false)
  }
  for (const [ext, ints] of Object.entries(F.swap)) {
    const e = reg.parts.get(ext)
    if (e && (ints.length === 0 || ints.some((i) => reg.parts.has(i)))) setPartVisible(e, false)
  }
  for (const p of reg.parts.values()) if (partVisible(p)) clipPart(p, [freePlane], 'free')
}

/** slider: only the constant changes */
export function setFreeOffset(offset: number) {
  setFreePlane(cur.axis, offset, cur.flip)
}

/** normal + constant; no material rebuild */
export function setFreeAxis(axis: Axis, flip: boolean, offset = cur.offset) {
  setFreePlane(axis, offset, flip)
}

/** resetCuts -> applyState(back) without camera. Call only from inside the state queue. */
export async function leaveFree(back: FixedStateId): Promise<void> {
  resetCuts(reg.gl)
  await applyState(back, { camera: false })
}

export const freeParams = () => ({ ...cur })
