import { useFrame } from '@react-three/fiber'
import { reg } from './rig'
import { useUi } from '../store'

// PLAN-DOT1 §4.2.8: runtime pivots from rotors.json (slice 1 only), turned in useFrame.
// The pivot quaternion is set from the accumulated angle (mod 2π) instead of being multiplied every frame,
// so it never drifts; for an identity-rotation pivot this equals rotateOnAxis(axis, step).
const TAU = Math.PI * 2

export function Rotors() {
  useFrame((_, dt) => {
    const mode = useUi.getState().rotorMode
    if (mode === 'off') return
    const step = Math.min(dt, 0.1)
    for (const r of reg.rotors) {
      if (!r.ready) continue
      const k = mode === 'real' ? 1 : 1 / r.rec.display_slow
      r.angle += ((TAU * r.rec.rpm) / 60) * k * step
      r.pivot.quaternion.setFromAxisAngle(r.axis, r.angle % TAU)
    }
  })
  return null
}
