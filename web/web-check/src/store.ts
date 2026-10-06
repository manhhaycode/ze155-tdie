import { create } from 'zustand'
import * as THREE from 'three'
import { FIXED_STATE_IDS, type Axis, type CameraPreset, type FixedStateId, type StateId, type V3 } from './data'
import { reg } from './scene/rig'
import { enqueue } from './scene/stateQueue'
import { applyState } from './scene/Cuts'
import { enterFree, freePlane, setFreePlane } from './scene/FreeClip'
import { applyPreset, controlsRef, zoomToBox } from './scene/CameraRig'
import { enterFlowLayer } from './scene/Flow'

// PLAN-DOT1 §4.2.9 (zustand 5). Builder A's UI codes against this interface; extras are marked "B extra".
export type RotorMode = 'off' | 'slow' | 'real'
/** PLAN-FLOW §4.2: colour of the melt in FLOW (material phase, or zone set-point temperature) */
export type FlowColor = 'phase' | 'heat'
export interface FreeParams { axis: Axis; offset: number; flip: boolean }

export interface Ui {
  hovered: string | null
  selected: string | null
  selectedPart: string | null
  state: StateId
  prevFixed: FixedStateId
  free: FreeParams
  rotorMode: RotorMode
  interiorWanted: boolean
  interiorLoaded: boolean
  busy: boolean
  /** B extra: the state being applied by the queue (null when idle) */
  pending: StateId | null
  /** B extra: +1 after every applied state change (visible meshes / materials changed) */
  cutVersion: number
  /** B extra: true once line.glb is rigged and the first frame is drawn */
  ready: boolean
  flowColor: FlowColor
  /** rotors, pellets and FLOW stripes stand still (tests and screenshots: __ze.freeze) */
  frozen: boolean
  hover(id: string | null): void
  select(id: string | null, part?: string | null): void
  clear(): void
  zoomTo(id: string | null): void
  setStateId(id: StateId): Promise<void>
  setFree(p: Partial<FreeParams>): void
  setRotorMode(m: RotorMode): void
  setFlowColor(m: FlowColor): void
  setFrozen(v: boolean): void
  requestInterior(): void
  setInteriorLoaded(v: boolean): void
  /** B extra: "Về góc nhìn của trạng thái": camera preset of the current fixed state (FREE: of prevFixed) */
  resetView(): void
}

export interface ChangeOpts { camera?: boolean; smooth?: boolean }

/** a camera sees the FREE section when it is on the removed side and looks towards the kept side */
const MIN_FACING = 0.3
const facing = (pos: THREE.Vector3, dir: THREE.Vector3) =>
  freePlane.distanceToPoint(pos) < 0 && dir.dot(freePlane.normal) >= MIN_FACING

/** which camera faceFreeCut used last: 'keep', a fixed-state id, or 'mirror:<id>' (test hooks) */
export const freeCamDebug = { last: '' }

const _p = new THREE.Vector3()
const _d = new THREE.Vector3()
function facingPreset(): FixedStateId | null {
  for (const id of FIXED_STATE_IDS) {
    const p = reg.data.states[id].camera
    if (!p) continue
    _p.fromArray(p.pos)
    _d.fromArray(p.target).sub(_p).normalize()
    if (facing(_p, _d)) return id
  }
  return null
}
/** the preset seen in the mirror of the FREE plane, its target moved onto the plane (the section's middle) */
function mirrored(id: FixedStateId): CameraPreset {
  const p = reg.data.states[id].camera!
  const n = freePlane.normal
  const dist = (v: V3) => n.x * v[0] + n.y * v[1] + n.z * v[2] + freePlane.constant
  const m = (v: V3): V3 => {
    const d = 2 * dist(v)
    return [v[0] - d * n.x, v[1] - d * n.y, v[2] - d * n.z]
  }
  const t = m(p.target)
  const dt = dist(t)
  return { ...p, pos: m(p.pos), target: [t[0] - dt * n.x, t[1] - dt * n.y, t[2] - dt * n.z], source: `mirror of ${id}` }
}
/**
 * review-flow-01 M1 (+ recheck): keep the camera when its END pose (where a running flight will stop; also right
 * after an instant preset, whose camera.position is only written on the next controls update) already sees the
 * section; else the first fixed-state preset that faces it; else (flipped cuts: every preset stands on the kept
 * side) the mirror image of the first preset that faces the unflipped plane.
 */
function faceFreeCut(smooth: boolean) {
  const c = controlsRef.current
  if (!c) return
  const pos = c.getPosition(new THREE.Vector3(), true)
  const dir = c.getTarget(new THREE.Vector3(), true).sub(pos).normalize()
  if (facing(pos, dir)) {
    freeCamDebug.last = 'keep'
    return
  }
  let id = facingPreset()
  let p = id ? reg.data.states[id].camera! : null
  if (!id) {
    freePlane.negate()
    id = facingPreset()
    freePlane.negate()
    if (id) p = mirrored(id)
  }
  freeCamDebug.last = p ? (p.source?.startsWith('mirror') ? `mirror:${id}` : id!) : 'keep'
  if (p) void applyPreset(p, smooth)
}

/** every cut-state change goes through the single queue (AMENDMENTS I2) */
export function changeState(id: StateId, o: ChangeOpts = {}): Promise<void> {
  return enqueue(`state ${id}`, async () => {
    useUi.setState({ pending: id })
    try {
      if (id === 'FREE') {
        const f = useUi.getState().free
        await enterFree(f.axis, f.offset, f.flip)
        if (o.camera !== false) faceFreeCut(o.smooth !== false)
      } else {
        await applyState(id, { camera: o.camera, smooth: o.smooth })
        if (id === 'FLOW') enterFlowLayer()
      }
      useUi.setState((s) => ({
        state: id,
        prevFixed: id === 'FREE' ? s.prevFixed : id,
        cutVersion: s.cutVersion + 1,
      }))
    } finally {
      useUi.setState({ pending: null })
    }
  })
}

export const useUi = create<Ui>()((set, get) => ({
  hovered: null,
  selected: null,
  selectedPart: null,
  state: 'FULL',
  prevFixed: 'FULL',
  free: { axis: 'x', offset: 3, flip: false },
  rotorMode: 'slow',
  interiorWanted: false,
  interiorLoaded: false,
  busy: false,
  pending: null,
  cutVersion: 0,
  ready: false,
  flowColor: 'phase',
  frozen: false,

  hover: (id) => set({ hovered: id }),
  select: (id, part = null) => set({ selected: id, selectedPart: id ? (part ?? null) : null }),
  clear: () => set({ selected: null, selectedPart: null }),
  zoomTo: (id) => {
    if (!id || !reg.devices.has(id)) return
    const part = get().selected === id ? get().selectedPart : null
    const visibleMeshes: THREE.Mesh[] = part ? reg.meshesOfPart(part) : reg.meshesOfDevice(id)
    let box = part ? reg.boxOfMeshes(visibleMeshes) : reg.boxOfDevice(id)
    let targets = visibleMeshes
    if (box.isEmpty()) {
      box = reg.boxOfDevice(id, false) // nothing visible (inside): frame all meshes
      targets = [] // hidden fallback must keep the original fitToSphere behavior
    }
    void zoomToBox(box, true, targets)
  },
  setStateId: (id) => changeState(id),
  setFree: (p) => {
    const before = get().free
    set((s) => ({ free: { ...s.free, ...p } }))
    const f = get().free
    // the shared plane is only referenced by FREE variants, so updating it is always safe (no queue needed;
    // enterFree also reads the store values when it starts)
    setFreePlane(f.axis, f.offset, f.flip)
    // review recheck M1: a new direction or side can leave the section edge-on or behind the camera (the slider
    // only changes the offset and never moves the camera). The job re-checks the state: a state change queued
    // before it may have left FREE.
    if (get().state === 'FREE' && (f.axis !== before.axis || f.flip !== before.flip))
      void enqueue('free camera', async () => {
        if (useUi.getState().state === 'FREE') faceFreeCut(true)
      })
  },
  setRotorMode: (m) => set({ rotorMode: m }),
  setFlowColor: (m) => set({ flowColor: m }),
  setFrozen: (v) => set({ frozen: v }),
  requestInterior: () => {
    if (get().interiorWanted) return
    reg.stats.interior_requested_at = performance.now()
    set({ interiorWanted: true })
  },
  setInteriorLoaded: (v) => set({ interiorLoaded: v }),
  resetView: () => {
    const s = get()
    const id = s.state === 'FREE' ? s.prevFixed : s.state
    const cam = reg.data?.states[id]?.camera
    if (cam) void enqueue('camera preset', async () => void applyPreset(cam, true))
  },
}))
