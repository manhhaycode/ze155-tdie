import { create } from 'zustand'
import * as THREE from 'three'
import { FIXED_STATE_IDS, type Axis, type FixedStateId, type StateId } from './data'
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

/** a camera sees the FREE section when it is on the removed side and not looking along the plane */
const MIN_FACING = 0.3
const facing = (pos: THREE.Vector3, dir: THREE.Vector3) =>
  freePlane.distanceToPoint(pos) < 0 && Math.abs(dir.dot(freePlane.normal)) >= MIN_FACING
/**
 * review-flow-01 M1: FREE keeps the current camera, but from some views (FLOW looks along +z, so the default
 * X = 3 000 cut is edge-on) its section cannot be seen. Then the first fixed-state preset that faces the cut is
 * used (FULL for X and Z, FLOW for Y); otherwise the camera stays.
 */
function faceFreeCut(smooth: boolean) {
  const c = controlsRef.current
  if (!c) return
  const cam = c.camera
  if (facing(cam.position, cam.getWorldDirection(new THREE.Vector3()))) return
  const _p = new THREE.Vector3()
  const _t = new THREE.Vector3()
  for (const id of FIXED_STATE_IDS) {
    const p = reg.data.states[id].camera
    if (!p) continue
    _p.fromArray(p.pos)
    _t.fromArray(p.target).sub(_p).normalize()
    if (facing(_p, _t)) {
      void applyPreset(p, smooth)
      return
    }
  }
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
    set((s) => ({ free: { ...s.free, ...p } }))
    const f = get().free
    // the shared plane is only referenced by FREE variants, so updating it is always safe (no queue needed;
    // enterFree also reads the store values when it starts)
    setFreePlane(f.axis, f.offset, f.flip)
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
