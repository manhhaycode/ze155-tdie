import type * as THREE from 'three'
import type { SolidSectionRec } from '../data'

/**
 * review-flow-01 M3: is a point inside a node's solid of revolution (about three z)? JS twin of the cap shader's
 * zeInSection (Cuts.ts); used by the picking filter (Picking.ts) and the test hooks. shrink (m) keeps away from
 * the profile's edges.
 */
export function inSection(p: THREE.Vector3, s: SolidSectionRec, shrink = 0): boolean {
  const r = Math.hypot(p.x - s.centre[0], p.y - s.centre[1])
  const h = Math.abs(p.z - s.centre[2])
  return s.profile.some(([hh, rr]) => h <= hh - shrink && r <= rr - shrink)
}
