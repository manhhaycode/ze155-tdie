import * as THREE from 'three'
import { use, useEffect, useLayoutEffect, useRef } from 'react'
import { useThree } from '@react-three/fiber'
import { CameraControls } from '@react-three/drei'
import type { CameraControls as CameraControlsImpl } from '@react-three/drei'
import { dataPromise, type CameraPreset } from '../data'
import { reg } from './rig'

// PLAN-DOT1 §4.2.7: CameraControls (makeDefault), presets from cut_states.json, fitToSphere zoom.
//
// Zoom tuning (dot1/USER-FEEDBACK.md, "tốc độ zoom hơi chậm"). camera-controls dollies by a fraction of the
// distance to the orbit target, so the wheel slowed down and stalled near a target that was often far from
// what the user was looking at, and it zoomed to the target instead of the cursor. Now:
// - dollySpeed 2 and dollyToCursor; draggingSmoothTime 0.08 s is the smoothing camera-controls uses while
//   the user drives the camera (wheel, drag); smoothTime 0.2 s is for programmatic flights (state presets,
//   F / double click), which settle in about 0.6–0.8 s;
// - "auto depth" like Blender: when a zoom-in gesture starts, the orbit target slides along the view axis to
//   the depth of the surface under the cursor (camera position and view direction unchanged). The wheel then
//   closes in on that surface at a speed proportional to the distance to it, instead of stalling at a far
//   target or flying through a near surface;
// - infinityDolly with a 5 cm minDistance: at the surface the zoom keeps pushing forward (into a cut screw);
// - a trackpad pinch (wheel + ctrlKey) dollies to the cursor like the wheel, instead of camera-controls'
//   default FOV zoom to the centre of the view.
export const CONTROL_TUNING = {
  smoothTime: 0.2,
  draggingSmoothTime: 0.08,
  dollySpeed: 2,
  dollyToCursor: true,
  infinityDolly: true,
  minDistance: 0.05,
} as const
/** a new wheel gesture starts after this many ms without wheel events */
const GESTURE_GAP_MS = 250

export const controlsRef: { current: CameraControlsImpl | null } = { current: null }

export function applyPreset(p: CameraPreset, smooth: boolean): Promise<void> {
  const c = controlsRef.current
  if (!c) return Promise.resolve()
  const cam = c.camera as THREE.PerspectiveCamera
  cam.filmGauge = p.sensor_mm ?? 36
  cam.setFocalLength(p.lens_mm) // also updates the projection matrix
  // a preset defines the lens: drop any zoom and any focal offset
  return Promise.all([
    c.zoomTo(1, smooth),
    c.setFocalOffset(0, 0, 0, smooth),
    c.setLookAt(p.pos[0], p.pos[1], p.pos[2], p.target[0], p.target[1], p.target[2], smooth),
  ]).then(() => {})
}

/**
 * Frame a box like Blender's "View Selected": keep the current view direction, move the target to the box
 * centre and dolly to fit. camera-controls' fitToBox would also snap the camera to the nearest axis
 * (`roundToStep(theta, PI/2)`), which is not what a Blender user expects, so this uses fitToSphere on
 * the box's bounding sphere with the plan's padding (max(0.15 m, |size| * 0.15)).
 */
const FOCUS_CLEAR_MIN_SAMPLES = 3
const FOCUS_CLEAR_RATIO = 0.8
const FOCUS_EPSILON = 1e-4

type FocusScore = { valid: number; clear: number; ratio: number }

function focusSamples(box: THREE.Box3): THREE.Vector3[] {
  const { min, max } = box
  const c = box.getCenter(new THREE.Vector3())
  return [
    c,
    new THREE.Vector3(min.x, c.y, c.z), new THREE.Vector3(max.x, c.y, c.z),
    new THREE.Vector3(c.x, min.y, c.z), new THREE.Vector3(c.x, max.y, c.z),
    new THREE.Vector3(c.x, c.y, min.z), new THREE.Vector3(c.x, c.y, max.z),
    ...[
      [min.x, min.y, min.z], [min.x, min.y, max.z], [min.x, max.y, min.z], [min.x, max.y, max.z],
      [max.x, min.y, min.z], [max.x, min.y, max.z], [max.x, max.y, min.z], [max.x, max.y, max.z],
    ].map(([x, y, z]) => new THREE.Vector3(x, y, z)),
  ]
}

function isFocusTarget(object: THREE.Object3D, targets: Set<THREE.Mesh>): boolean {
  return targets.has(object as THREE.Mesh)
}

function scoreFocus(position: THREE.Vector3, box: THREE.Box3, targets: THREE.Mesh[]): FocusScore {
  const targetSet = new Set(targets)
  const targetRay = new THREE.Raycaster()
  const sceneRay = new THREE.Raycaster()
  const samples = focusSamples(box)
  let valid = 0
  let clear = 0

  for (const aim of samples) {
    const direction = aim.clone().sub(position)
    const distance = direction.length()
    if (distance <= FOCUS_EPSILON) continue
    direction.multiplyScalar(1 / distance)
    targetRay.set(position, direction)
    const targetHits = targetRay.intersectObjects(targets, false)
    const targetHit = targetHits[0]
    if (!targetHit) continue // a bbox aim with no actual target surface is not clear
    valid++

    sceneRay.set(position, direction)
    sceneRay.far = targetHit.distance + FOCUS_EPSILON
    const sceneHit = sceneRay.intersectObject(reg.lineScene!, true)[0]
    if (sceneHit && isFocusTarget(sceneHit.object, targetSet)) clear++
  }

  return { valid, clear, ratio: valid ? clear / valid : 0 }
}

function focusDirections(current: THREE.Vector3): THREE.Vector3[] {
  const spherical = new THREE.Spherical().setFromVector3(current)
  const elevation = THREE.MathUtils.clamp(Math.PI / 2 - spherical.phi, -THREE.MathUtils.degToRad(75), THREE.MathUtils.degToRad(75))
  const azimuthOffsets = [0, -30, 30, -60, 60, -90, 90, 180].map(THREE.MathUtils.degToRad)
  const elevationOffsets = [0, 15, 30].map(THREE.MathUtils.degToRad)
  const out: THREE.Vector3[] = []
  for (const de of elevationOffsets) {
    const el = THREE.MathUtils.clamp(elevation + de, -THREE.MathUtils.degToRad(75), THREE.MathUtils.degToRad(75))
    for (const da of azimuthOffsets) {
      const d = new THREE.Vector3().setFromSphericalCoords(1, Math.PI / 2 - el, spherical.theta + da)
      if (d.y < -0.95 || out.some((x) => x.distanceToSquared(d) < 1e-8)) continue
      out.push(d)
    }
  }
  return out
}

function angularDistance(a: THREE.Vector3, b: THREE.Vector3): number {
  return Math.acos(THREE.MathUtils.clamp(a.dot(b), -1, 1))
}

/** Focus a box, changing the view direction only when the current fitted view is occluded. */
export async function zoomToBox(box: THREE.Box3, smooth = true, targetMeshes?: THREE.Mesh[]): Promise<void> {
  const c = controlsRef.current
  if (!c || box.isEmpty()) return
  const sphere = box.getBoundingSphere(new THREE.Sphere())
  const pad = Math.max(0.15, box.getSize(new THREE.Vector3()).length() * 0.15)
  sphere.radius = Math.max(sphere.radius + pad * 0.5, 0.05)
  if (!targetMeshes?.length || !reg.lineScene) {
    await c.fitToSphere(sphere, smooth)
    return
  }

  const position = new THREE.Vector3()
  const target = new THREE.Vector3()
  c.getPosition(position, false)
  c.getTarget(target, false)
  const currentOffset = position.sub(target)
  if (currentOffset.lengthSq() <= FOCUS_EPSILON * FOCUS_EPSILON) {
    await c.fitToSphere(sphere, smooth)
    return
  }
  const current = currentOffset.normalize()

  const fitDistance = c.getDistanceToFitSphere(sphere.radius)
  const center = sphere.center
  const currentPosition = center.clone().addScaledVector(current, fitDistance)
  const currentScore = scoreFocus(currentPosition, box, targetMeshes)
  const currentClear = currentScore.valid >= FOCUS_CLEAR_MIN_SAMPLES && currentScore.ratio >= FOCUS_CLEAR_RATIO
  if (currentClear || currentScore.valid < FOCUS_CLEAR_MIN_SAMPLES) {
    await c.fitToSphere(sphere, smooth)
    return
  }

  const candidates = focusDirections(current)
    .filter((direction) => center.y + direction.y * fitDistance >= 0.05)
    .map((direction) => ({ direction, angle: angularDistance(current, direction) }))
    .sort((a, b) => a.angle - b.angle)
  const scored = candidates.map(({ direction, angle }) => {
    const candidatePosition = center.clone().addScaledVector(direction, fitDistance)
    return { direction, angle, position: candidatePosition, score: scoreFocus(candidatePosition, box, targetMeshes) }
  })
  const clearCandidate = scored.find((x) => x.score.valid >= FOCUS_CLEAR_MIN_SAMPLES && x.score.ratio >= FOCUS_CLEAR_RATIO)
  const best = clearCandidate ?? scored
    .filter((x) => x.score.valid >= FOCUS_CLEAR_MIN_SAMPLES && x.score.ratio > currentScore.ratio + 1e-6)
    .sort((a, b) => b.score.ratio - a.score.ratio || a.angle - b.angle)[0]
  if (!best) {
    await c.fitToSphere(sphere, smooth)
    return
  }

  await Promise.all([
    c.setLookAt(best.position.x, best.position.y, best.position.z, center.x, center.y, center.z, smooth),
    c.setFocalOffset(0, 0, 0, smooth),
  ])
}

const _ray = new THREE.Raycaster()
const _ndc = new THREE.Vector2()
const _pos = new THREE.Vector3()
const _tgt = new THREE.Vector3()
const _fwd = new THREE.Vector3()
const _hit = new THREE.Vector3()
const _floor = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)

/**
 * Auto depth: put the orbit target on the view axis at the depth of what is under the cursor (the line's
 * filtered raycast, so cuts, hidden parts and ghosts are honoured; the floor when nothing is hit). Only the
 * camera-to-target distance changes. Returns the new distance, or null when nothing changed.
 */
export function retargetToCursor(clientX: number, clientY: number, el: HTMLElement): number | null {
  const c = controlsRef.current
  if (!c || c.active || !reg.lineScene) return null // never cut a running flight short
  const r = el.getBoundingClientRect()
  _ndc.set(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1)
  const cam = c.camera as THREE.PerspectiveCamera
  cam.updateMatrixWorld()
  _ray.setFromCamera(_ndc, cam)
  const hit = _ray.intersectObject(reg.lineScene, true)[0]
  if (hit) _hit.copy(hit.point)
  else if (!_ray.ray.intersectPlane(_floor, _hit)) return null
  c.getPosition(_pos, true)
  c.getTarget(_tgt, true)
  _fwd.subVectors(_tgt, _pos)
  const dist = _fwd.length()
  if (dist < 1e-6) return null
  _fwd.divideScalar(dist)
  const depth = _hit.sub(_pos).dot(_fwd)
  if (!(depth > c.minDistance) || depth > 500 || Math.abs(depth - dist) < 1e-3) return null
  _tgt.copy(_pos).addScaledVector(_fwd, depth)
  void c.setLookAt(_pos.x, _pos.y, _pos.z, _tgt.x, _tgt.y, _tgt.z, false)
  return depth
}

/** wheel listener on the canvas: runs before camera-controls' listener on the wrapping element */
function useWheelTuning() {
  const gl = useThree((s) => s.gl)
  useEffect(() => {
    const el = gl.domElement
    let last = -Infinity
    const onWheel = (e: WheelEvent) => {
      const c = controlsRef.current
      if (!c || !c.enabled) return
      if (e.ctrlKey) {
        // trackpad pinch: hand camera-controls the same gesture as a plain wheel (dolly to the cursor)
        e.preventDefault() // no browser page zoom
        e.stopImmediatePropagation()
        el.dispatchEvent(
          new WheelEvent('wheel', {
            deltaX: e.deltaX,
            deltaY: e.deltaY,
            deltaMode: e.deltaMode,
            clientX: e.clientX,
            clientY: e.clientY,
            screenX: e.screenX,
            screenY: e.screenY,
            bubbles: true,
            cancelable: true,
          }),
        )
        return
      }
      const now = performance.now()
      if (now - last > GESTURE_GAP_MS && e.deltaY < 0) retargetToCursor(e.clientX, e.clientY, el)
      last = now
    }
    el.addEventListener('wheel', onWheel, { passive: false })
    return () => el.removeEventListener('wheel', onWheel)
  }, [gl])
}

export function CameraRig() {
  const data = use(dataPromise)
  const ref = useRef<CameraControlsImpl>(null)
  useWheelTuning()
  useLayoutEffect(() => {
    controlsRef.current = ref.current
    const full = data.states.FULL.camera
    if (full && ref.current) void applyPreset(full, false) // initial camera = FULL preset
    return () => {
      if (controlsRef.current === ref.current) controlsRef.current = null
    }
  }, [data])
  return <CameraControls ref={ref} makeDefault {...CONTROL_TUNING} />
}
