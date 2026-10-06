import * as THREE from 'three'
import type { RootState } from '@react-three/fiber'
import { FIXED_STATE_IDS, type Axis, type FixedStateId, type StateId, type V3 } from '../data'
import { reg, isShown } from '../scene/rig'
import { unfilteredMeshes, isHelper } from '../scene/Picking'
import { statePlane, cutDebug } from '../scene/Cuts'
import { freePlane } from '../scene/FreeClip'
import { applyPreset, controlsRef, zoomToBox } from '../scene/CameraRig'
import { unknownMaterials } from '../scene/materials'
import { precompileStats } from '../scene/precompile'
import { queueDrained, queueIdle, queueRunning } from '../scene/stateQueue'
import { changeState as changeStateRaw, freeCamDebug, useUi, type ChangeOpts } from '../store'
import { HOVER_COLOR, SELECT_COLOR, selectionInfo } from '../scene/Selection'
import { flowDebug, flowRates, K_ROLL, K_SCREW } from '../scene/Flow'
import { fillColorAt as fillColor, flowUniforms, toHex } from '../scene/FillMaterial'
import { sheetColorAt } from '../scene/SheetMaterial'
import { heatRgb } from '../scene/heat'
import { inSection } from '../scene/section'

// PLAN-DOT1 §4.2.11 (window.__ze), minus the Đợt 1b items (AMENDMENTS): pickSweep and the perf trace.

let resolveReady!: () => void
export const ready = new Promise<void>((r) => (resolveReady = r))
export function signalReady() {
  resolveReady()
}
export const frameCounter = { n: 0 }

const raf = () => new Promise<number>((r) => requestAnimationFrame(r))
const raf2 = async () => {
  await raf()
  await raf()
}
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))
const round = (x: number, d = 1) => Math.round(x * 10 ** d) / 10 ** d
/** a state change, then wait until the queue is empty (the interior load queues a precompile pass) */
async function changeState(id: StateId, o: ChangeOpts = {}) {
  await changeStateRaw(id, o)
  await queueDrained()
}

interface Hit {
  device_id: string | null
  part: string | null
  object: string
  point: number[]
  distance: number
  backFace: boolean
  cutOnly: boolean
}

export function installHooks(get: () => RootState) {
  const canvas = () => get().gl.domElement
  const _nm = new THREE.Matrix3()
  const _n = new THREE.Vector3()

  const toHit = (h: THREE.Intersection, ray: THREE.Ray): Hit => {
    const part = reg.partOfObject(h.object)
    let backFace = false
    if (h.face) {
      _nm.getNormalMatrix(h.object.matrixWorld)
      _n.copy(h.face.normal).applyMatrix3(_nm).normalize()
      backFace = _n.dot(ray.direction) > 0
    }
    return {
      device_id: reg.deviceOfObject(h.object),
      part: part?.name ?? null,
      object: h.object.name,
      point: h.point.toArray().map((v) => round(v, 4)),
      distance: h.distance,
      backFace,
      cutOnly: part?.meta.role === 'cut_only',
    }
  }

  const raycaster = new THREE.Raycaster()
  const setRay = (x: number, y: number) => {
    const s = get()
    const ndc = new THREE.Vector2((x / s.size.width) * 2 - 1, -(y / s.size.height) * 2 + 1)
    raycaster.setFromCamera(ndc, s.camera)
    return raycaster.ray
  }
  /** same mesh.raycast filters as the pointer events */
  const pickAt = (x: number, y: number): Hit | null => {
    if (!reg.lineScene) return null
    const ray = setRay(x, y)
    const hit = raycaster.intersectObject(reg.lineScene, true)[0]
    return hit ? toHit(hit, ray) : null
  }

  const dispatchClick = async (x: number, y: number, o: { alt?: boolean; dbl?: boolean } = {}) => {
    const c = canvas()
    const r = c.getBoundingClientRect()
    const init: PointerEventInit = {
      clientX: r.left + x,
      clientY: r.top + y,
      bubbles: true,
      cancelable: true,
      altKey: !!o.alt,
      pointerId: 1,
      pointerType: 'mouse',
      isPrimary: true,
      button: 0,
      buttons: 0,
      view: window,
    }
    const ctl = controlsRef.current
    const was = ctl?.enabled
    if (ctl) ctl.enabled = false // synthetic events must not start an orbit
    try {
      c.dispatchEvent(new PointerEvent('pointermove', init))
      c.dispatchEvent(new PointerEvent('pointerdown', { ...init, buttons: 1 }))
      c.dispatchEvent(new PointerEvent('pointerup', init))
      c.dispatchEvent(new MouseEvent('click', { ...init, detail: 1 }))
      if (o.dbl) {
        c.dispatchEvent(new PointerEvent('pointerdown', { ...init, buttons: 1 }))
        c.dispatchEvent(new PointerEvent('pointerup', init))
        c.dispatchEvent(new MouseEvent('click', { ...init, detail: 2 }))
        c.dispatchEvent(new MouseEvent('dblclick', { ...init, detail: 2 }))
      }
    } finally {
      if (ctl && was !== undefined) ctl.enabled = was
    }
    await raf2()
  }

  const selection = () => {
    const s = useUi.getState()
    const meshes = s.selected
      ? s.selectedPart
        ? reg.meshesOfPart(s.selectedPart)
        : reg.meshesOfDevice(s.selected)
      : []
    return {
      hovered: s.hovered,
      selected: s.selected,
      part: s.selectedPart,
      outlineMeshes: meshes.length,
      outlineMeshesDrawn: selectionInfo.outlineMeshes,
      bbox: selectionInfo.bbox,
      colors: { hover: HOVER_COLOR, select: SELECT_COLOR },
    }
  }

  const screenRectOfBox = (box: THREE.Box3) => {
    const s = get()
    const xs: number[] = []
    const ys: number[] = []
    for (let i = 0; i < 8; i++) {
      const p = new THREE.Vector3(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z)
      p.project(s.camera)
      xs.push(((p.x + 1) / 2) * s.size.width)
      ys.push(((1 - p.y) / 2) * s.size.height)
    }
    const clamp = (v: number, hi: number) => Math.min(Math.max(v, 0), hi)
    return {
      x0: clamp(Math.min(...xs), s.size.width - 1),
      x1: clamp(Math.max(...xs), s.size.width - 1),
      y0: clamp(Math.min(...ys), s.size.height - 1),
      y1: clamp(Math.max(...ys), s.size.height - 1),
    }
  }

  const project = (id: string) => {
    let box = reg.boxOfDevice(id)
    if (box.isEmpty()) box = reg.boxOfDevice(id, false)
    const s = get()
    const p = box.getCenter(new THREE.Vector3()).project(s.camera)
    return { x: round(((p.x + 1) / 2) * s.size.width), y: round(((1 - p.y) / 2) * s.size.height), onScreen: Math.abs(p.x) <= 1 && Math.abs(p.y) <= 1 && p.z < 1 }
  }

  const selfcheck = () => {
    let orphans = 0
    const orphanNames: string[] = []
    reg.lineScene?.traverse((o) => {
      if (isHelper(o) || !(o as THREE.Mesh).isMesh) return
      if (!reg.deviceOfObject(o)) {
        orphans++
        if (orphanNames.length < 10) orphanNames.push(o.name)
      }
    })
    const ray = unfilteredMeshes(reg.lineScene)
    return {
      devices: reg.devices.size,
      parts: reg.parts.size,
      unknownNodes: reg.unknownNodes.length,
      missingNodes: reg.missingNodes.length,
      orphans,
      orphanNames,
      rayUnfiltered: ray.meshes,
      rayUnfilteredEmpties: ray.empties,
      interiorLoaded: reg.interiorLoaded,
      rotorsReady: reg.rotors.filter((r) => r.ready).length,
      dataVersion: reg.data?.version ?? null,
      quantizeSplit: [...reg.quantizeSplit].sort(),
      unknownMaterials: [...unknownMaterials],
      devicesWithoutLineMeshes: [...reg.devices.values()].filter((d) => !d.parts.some((p) => p.meta.file === 'line' && p.meshes.length)).map((d) => d.id),
      bvh_ms: round(reg.stats.bvh_ms),
      state: useUi.getState().state,
      // FLOW (PLAN-FLOW §6): the pellets are a helper outside the line tree, so they never count above
      flowActive: flowDebug.active(),
      pellets: flowDebug.pellets()?.N ?? 0,
    }
  }

  // ---- FLOW (PLAN-FLOW §6) ----
  const flow = () => reg.data.states.FLOW.flow!
  const FLOW_MATERIAL = /^ze-(fill|sheet)/
  /** stops rotors, pellets and the FLOW clocks (screenshots, pixel samples) */
  const freeze = async (on = true) => {
    useUi.getState().setFrozen(on)
    await raf2()
    return useUi.getState().frozen
  }
  const flowProbe = () => {
    const p = flowDebug.pellets()
    const pr = p?.probe()
    const programs = new Set<string>()
    let fillMeshes = 0
    let leftovers = 0
    const leftoverNames: string[] = []
    for (const part of reg.parts.values())
      for (const mesh of part.meshes) {
        if (!isShown(mesh)) continue
        const m = mesh.material as THREE.Material
        if (FLOW_MATERIAL.test(m.name)) {
          fillMeshes++
          programs.add(m.name)
        } else if (flowDebug.active() && (m.name === 'za_fill_melt' || m.name === 'ze_melt_curtain' || m.name === 'ze_sheet_pet')) {
          leftovers++
          if (leftoverNames.length < 10) leftoverNames.push(part.name)
        }
      }
    const { kScrew, kRoll } = flowRates()
    return {
      active: flowDebug.active(),
      pellets: pr?.pellets ?? 0,
      pelletsShown: !!p?.mesh.visible && isShown(p.mesh),
      visiblePellets: pr?.visiblePellets ?? 0,
      falling: pr?.falling ?? 0,
      maxPelletX: pr ? round(pr.maxPelletX, 4) : null,
      minPelletZ: pr ? round(pr.minPelletZ, 4) : null,
      fillMeshes,
      fillPrograms: [...programs].sort(),
      leftovers,
      leftoverNames,
      renderOrders: flowDebug.renderOrders(),
      mode: useUi.getState().flowColor,
      kScrew,
      kRoll,
      frozen: useUi.getState().frozen,
    }
  }
  const median = (a: number[]) => {
    if (!a.length) return NaN
    const s = [...a].sort((x, y) => x - y)
    return s[Math.floor(s.length / 2)]
  }
  /** axial pellet speed in [x0, x1] (both samples inside), over `seconds`, at the current rotor mode */
  const pelletSpeed = async (seconds: number, ranges: [number, number][]) => {
    const p = flowDebug.pellets()!
    const f0 = frameCounter.n
    const a = p.barrelX()
    const t0 = performance.now()
    await sleep(seconds * 1000)
    const b = p.barrelX()
    const t = (performance.now() - t0) / 1000
    const hz = (frameCounter.n - f0) / t
    return {
      hz: round(hz),
      speeds: ranges.map(([x0, x1]) => {
        const v: number[] = []
        for (let i = 0; i < a.length; i++) if (a[i] >= x0 && a[i] <= x1 && b[i] >= x0 && b[i] <= x1 && b[i] > a[i]) v.push((b[i] - a[i]) / t)
        return { range: [x0, x1], n: v.length, v: round(median(v), 5) }
      }),
    }
  }
  /** F4: pellet speeds (slow, real), standstill (off), pellet bounds */
  const pelletTest = async (seconds = 2) => {
    const ui = useUi.getState()
    const modeBefore = ui.rotorMode
    const frozenBefore = ui.frozen
    if (ui.state !== 'FLOW') await changeState('FLOW', { camera: false })
    ui.setFrozen(false)
    const F = flow()
    const pitch = (zone: string) => F.zones.find((z) => z.zone === zone)!.pitch_m
    const exp = (zone: string, k: number) => ((pitch(zone) * F.screw_rpm) / 60) * k
    const Z1: [number, number] = [0.55, 1.45]
    const Z2: [number, number] = [1.55, 1.85]
    const run = async (mode: 'slow' | 'real', s: number) => {
      useUi.getState().setRotorMode(mode)
      await raf2()
      let r = await pelletSpeed(s, [Z1, Z2])
      if (r.hz < 50) r = await pelletSpeed(s, [Z1, Z2]) // a slow rAF window (other tabs, GC): measure again
      const k = K_SCREW[mode]
      const e1 = exp('z01_feed', k)
      const e2 = exp('z02_melt', k)
      return {
        mode,
        hz: r.hz,
        z01: { ...r.speeds[0], expected: round(e1, 5), err: round(Math.abs(r.speeds[0].v - e1) / e1, 4) },
        z02: { ...r.speeds[1], expected: round(e2, 5), err: round(Math.abs(r.speeds[1].v - e2) / e2, 4) },
      }
    }
    const slow = await run('slow', seconds)
    const real = await run('real', 0.25)
    useUi.getState().setRotorMode('off')
    await raf2()
    const p = flowDebug.pellets()!
    const before = Float32Array.from(p.pos)
    await sleep(1000)
    let moved = 0
    for (let i = 0; i < before.length; i++) if (Math.abs(before[i] - p.pos[i]) > 1e-7) moved++
    useUi.getState().setRotorMode(modeBefore)
    useUi.getState().setFrozen(frozenBefore)
    const pr = flowProbe()
    const speedOk = (r: typeof slow) => r.z01.n >= 5 && r.z02.n >= 5 && r.z01.err <= 0.05 && r.z02.err <= 0.05
    return {
      slow,
      real,
      off: { movedCoordinates: moved, ok: moved === 0 },
      bounds: { pellets: pr.pellets, N: F.pellets.N, maxPelletX: pr.maxPelletX, minPelletZ: pr.minPelletZ },
      ok:
        speedOk(slow) &&
        speedOk(real) &&
        moved === 0 &&
        pr.pellets === F.pellets.N &&
        (pr.maxPelletX ?? 0) <= 1.905 &&
        (pr.minPelletZ ?? -1) >= 0,
    }
  }
  const fillColorAt = (x: number, mode: 'phase' | 'heat') => fillColor(x, mode, flow())
  /** F5: every visible fill / curtain / sheet mesh runs a FLOW program; the colour rule at three points */
  const fillProbe = () => {
    const F = flow()
    const pr = flowProbe()
    const c1 = fillColorAt(1.0, 'phase')
    const c2 = fillColorAt(2.5, 'phase')
    const c3 = fillColorAt(5.9, 'heat')
    const heat285 = toHex(heatRgb(285, F.heat_stops))
    return {
      fillMeshes: pr.fillMeshes,
      fillPrograms: pr.fillPrograms,
      leftovers: pr.leftovers,
      leftoverNames: pr.leftoverNames,
      at1_0_phase: c1,
      at2_5_phase: c2,
      at5_9_heat: { ...c3, expected: heat285 },
      ok:
        pr.active &&
        pr.leftovers === 0 &&
        pr.fillMeshes > 0 &&
        c1.hex === F.colors.pellet.toUpperCase() &&
        c2.hex === F.colors.melt.toUpperCase() &&
        c3.hex === heat285,
    }
  }
  /** F6: sheet material, stripe speed (slow: kRoll 1), standstill when off, colours at s = 0 */
  const sheetProbe = async (seconds = 1) => {
    const F = flow()
    const ui = useUi.getState()
    const modeBefore = ui.rotorMode
    const frozenBefore = ui.frozen
    ui.setFrozen(false)
    const mats = reg.meshesOfPart('ctx_sheet').map((m) => (m.material as THREE.Material).name)
    const measure = async (mode: 'slow' | 'off', s: number) => {
      useUi.getState().setRotorMode(mode)
      await raf2()
      const u0 = flowUniforms.uRollT.value
      const t0 = performance.now()
      await sleep(s * 1000)
      const t = (performance.now() - t0) / 1000
      return (F.sheet.speed_m_s_real * (flowUniforms.uRollT.value - u0)) / t
    }
    const vSlow = await measure('slow', seconds)
    const vOff = await measure('off', 0.5)
    useUi.getState().setRotorMode(modeBefore)
    useUi.getState().setFrozen(frozenBefore)
    const expected = F.sheet.speed_m_s_real * K_ROLL.slow
    const phase0 = sheetColorAt(0, 'phase', F)
    const heat0 = sheetColorAt(0, 'heat', F)
    const heat250 = toHex(heatRgb(250, F.heat_stops))
    return {
      materials: mats,
      speed: { v: round(vSlow, 5), expected, err: round(Math.abs(vSlow - expected) / expected, 4) },
      speedOff: round(vOff, 6),
      phase0,
      heat0: { ...heat0, expected: heat250 },
      ok:
        mats.length > 0 &&
        mats.every((n) => n === 'ze-sheet') &&
        Math.abs(vSlow - expected) / expected <= 0.01 &&
        vOff === 0 &&
        phase0.hex === F.colors.melt.toUpperCase() &&
        heat0.hex === heat250,
    }
  }

  const visibleKey = () => {
    const v: string[] = []
    for (const p of reg.parts.values()) if (p.payload && isShown(p.payload)) v.push(p.name)
    return v.sort()
  }
  const materialKey = () => {
    const m = new Map<string, string>()
    for (const p of reg.parts.values()) for (const mesh of p.meshes) m.set(mesh.uuid, (mesh.material as THREE.Material).uuid)
    return m
  }
  const freePlaneRefs = () => {
    let n = 0
    reg.lineScene?.traverse((o) => {
      if (isHelper(o)) return
      const m = (o as THREE.Mesh).material as THREE.Material | undefined
      if (m && !Array.isArray(m) && m.clippingPlanes?.includes(freePlane)) n++
    })
    return n
  }

  const setFreeClip = async (axis: Axis | null, offset = 0, flip = false) => {
    if (axis === null) {
      const back = useUi.getState().prevFixed
      await changeState(back, { camera: false })
      return useUi.getState().state
    }
    useUi.getState().setFree({ axis, offset, flip })
    await changeState('FREE')
    return useUi.getState().state
  }

  const timeState = async (id: StateId) => {
    const enter = (s: StateId) => (s === 'FREE' ? changeState('FREE') : changeState(s, { camera: false }))
    const other: StateId = id === 'FULL' ? 'CUT_FEED' : 'FULL'
    await enter(other)
    await raf2()
    let t0 = performance.now()
    await enter(id)
    await raf2()
    const first = performance.now() - t0
    await enter(other)
    await raf2()
    t0 = performance.now()
    await enter(id)
    await raf2()
    const ms = performance.now() - t0
    return { id, ms: round(ms), first_ms: round(first), ok: ms <= 200 }
  }

  const cutRoundTrip = async () => {
    const bad: { state: string; visibleOnlyBefore: string[]; visibleOnlyAfter: string[]; materialDiffs: number }[] = []
    const freeBefore = { ...useUi.getState().free }
    useUi.getState().setFree({ axis: 'x', offset: 3.0, flip: false })
    let loadKey: string[] | null = null
    for (const id of FIXED_STATE_IDS) {
      await changeState(id, { camera: false })
      const vis0 = visibleKey()
      const mat0 = materialKey()
      if (id === 'FULL') loadKey = vis0
      await changeState('FREE')
      await raf()
      await changeState(id, { camera: false }) // leave FREE back to the same state
      const vis1 = visibleKey()
      const mat1 = materialKey()
      let materialDiffs = 0
      for (const [k, v] of mat0) if (mat1.get(k) !== v) materialDiffs++
      const s0 = new Set(vis0)
      const s1 = new Set(vis1)
      const onlyBefore = vis0.filter((n) => !s1.has(n))
      const onlyAfter = vis1.filter((n) => !s0.has(n))
      if (onlyBefore.length || onlyAfter.length || materialDiffs)
        bad.push({ state: id, visibleOnlyBefore: onlyBefore.slice(0, 20), visibleOnlyAfter: onlyAfter.slice(0, 20), materialDiffs })
    }
    await changeState('FULL', { camera: false })
    const endKey = visibleKey()
    const fullAgain = !!loadKey && endKey.join(',') === loadKey.join(',')
    if (!fullAgain) bad.push({ state: 'FULL(end)', visibleOnlyBefore: [], visibleOnlyAfter: [], materialDiffs: -1 })
    const glPlanes = get().gl.clippingPlanes.length
    const freeRefs = freePlaneRefs()
    // PLAN-FLOW F2: leaving FLOW hides the pellets and gives the fills their Đợt 1 materials back
    const fp = flowProbe()
    const flowLeft = !fp.active && !fp.pelletsShown && fp.fillMeshes === 0 && fp.renderOrders === 0
    const changedMaterials = cutDebug.changedMaterials()
    const changedVisibility = cutDebug.changedVisibility()
    useUi.getState().setFree(freeBefore)
    return {
      ok: bad.length === 0 && glPlanes === 0 && freeRefs === 0 && changedMaterials === 0 && changedVisibility === 0 && flowLeft,
      bad,
      states: [...FIXED_STATE_IDS],
      flowLeft,
      glClippingPlanes: glPlanes,
      freePlaneRefs: freeRefs,
      changedMaterialsAtEnd: changedMaterials,
      changedVisibilityAtEnd: changedVisibility,
    }
  }

  /**
   * D4. Applies the state (fixed: its camera preset, instantly; FREE: given axis/offset, the camera looks at
   * the cut face from the removed side, then frames the device). Samples 24 x 24 pixels in the device's
   * screen box. A sample counts as a cap pixel of the device when the device's own nearest hit there is a
   * cap and the scene's first filtered hit (what a click selects) is that same surface (same distance within
   * 2 mm). Cap = a back face of a closed, capped mesh behind the plane crossing (runtime cap: the renderer
   * paints exactly these back-face fragments; they lie on the far inner wall, not on the plane), or a
   * cut_only part's face on the plane within 2 mm (pre-cut cap, e.g. int_xsec_*).
   * correct = those cap pixels whose first hit belongs to the device. ok = capPixels >= 5 && correct === capPixels.
   */
  type CapOpts = { axis?: Axis; offset?: number; flip?: boolean; click?: boolean }
  /** review M8: the rotors stand still while capCheck samples (the screw angle no longer changes mid-run) */
  const capCheck = async (state: StateId, device: string, o: CapOpts = {}) => {
    const ui = useUi.getState()
    const modeBefore = ui.rotorMode
    const frozenBefore = ui.frozen
    ui.setRotorMode('off')
    ui.setFrozen(true) // PLAN-FLOW §3.1: pellets and FLOW stripes stand still too
    try {
      await raf()
      return await capCheckFrozen(state, device, o)
    } finally {
      useUi.getState().setRotorMode(modeBefore)
      useUi.getState().setFrozen(frozenBefore)
    }
  }
  const capCheckFrozen = async (state: StateId, device: string, o: CapOpts) => {
    let plane: THREE.Plane | null
    if (state === 'FREE') {
      useUi.getState().setFree({ axis: o.axis ?? 'x', offset: o.offset ?? 3, flip: !!o.flip })
      await changeState('FREE')
      // setFree inside FREE may queue a camera job (review M1) and a preset may change the lens (CUT_Z_BARREL
      // 40 mm): wait for it, then use one lens for every FREE sample
      await queueDrained()
      ;(controlsRef.current!.camera as THREE.PerspectiveCamera).setFocalLength(35)
      plane = freePlane
    } else {
      await changeState(state, { camera: true, smooth: false })
      plane = statePlane(state)
    }
    await raf2()
    if (!plane) return { state, device, ok: false, error: 'no plane' }
    let box = reg.boxOfDevice(device)
    if (box.isEmpty()) return { state, device, ok: false, error: 'device has no visible mesh' }
    if (state === 'FREE') {
      const c = box.getCenter(new THREE.Vector3())
      const away = plane.normal.clone().negate() // towards the removed side
      const d = Math.max(1.5, box.getSize(new THREE.Vector3()).length() * 1.5)
      const side = new THREE.Vector3(0, 1, 0).cross(away)
      if (side.lengthSq() < 1e-6) side.set(1, 0, 0)
      side.normalize()
      const pos = c.clone().addScaledVector(away, d).addScaledVector(side, d * 0.35).add(new THREE.Vector3(0, d * 0.3, 0))
      if (Math.abs(away.y) > 0.9) pos.set(c.x + d * 0.35, c.y + away.y * d, c.z - d * 0.35)
      await controlsRef.current?.setLookAt(pos.x, pos.y, pos.z, c.x, c.y, c.z, false)
      await zoomToBox(box, false)
      await raf2()
      box = reg.boxOfDevice(device)
    }
    const rect = screenRectOfBox(box)
    const meshes = reg.meshesOfDevice(device)
    const N = 24
    let capPixels = 0
    let correct = 0
    let sample: { x: number; y: number } | null = null
    const wrong: Record<string, number> = {}
    // runtime cap: what the renderer paints as cap is a back face of a closed, capped mesh seen through the
    // cut (the ray crosses the plane, then hits the far inner wall); pre-cut cap: a cut_only part face lying
    // on the plane (within 2 mm)
    const _p = new THREE.Vector3()
    const isCapHit = (h: Hit, obj: THREE.Object3D, ray: THREE.Ray) => {
      if (h.cutOnly) return Math.abs(plane!.distanceToPoint(_p.set(h.point[0], h.point[1], h.point[2]))) < 0.002
      if (!h.backFace || !obj.userData.zeClosed || !obj.userData.zeCapColor) return false
      const t = ray.distanceToPlane(plane!)
      return t !== null && t <= h.distance + 1e-4
    }
    const good: { x: number; y: number }[] = []
    for (let i = 0; i < N; i++)
      for (let j = 0; j < N; j++) {
        // integer pixels, so a dispatched click lands on exactly the sampled ray
        const x = Math.round(rect.x0 + ((i + 0.5) / N) * (rect.x1 - rect.x0))
        const y = Math.round(rect.y0 + ((j + 0.5) / N) * (rect.y1 - rect.y0))
        const ray = setRay(x, y)
        const own = raycaster.intersectObjects(meshes, false)[0]
        if (!own) continue
        const D = toHit(own, ray)
        if (!isCapHit(D, own.object, ray)) continue
        const all = raycaster.intersectObject(reg.lineScene!, true)[0]
        if (!all) continue
        const H = toHit(all, ray)
        if (Math.abs(H.distance - D.distance) > 0.002 || !isCapHit(H, all.object, ray)) continue // cap hidden behind something
        capPixels++
        if (H.device_id === device) {
          correct++
          good.push({ x, y })
        } else wrong[H.device_id ?? 'null'] = (wrong[H.device_id ?? 'null'] ?? 0) + 1
      }
    if (good.length) {
      // the correct cap pixel nearest to their centroid (away from cap edges)
      const cx = good.reduce((a, p) => a + p.x, 0) / good.length
      const cy = good.reduce((a, p) => a + p.y, 0) / good.length
      sample = good.reduce((b, p) => ((p.x - cx) ** 2 + (p.y - cy) ** 2 < (b.x - cx) ** 2 + (b.y - cy) ** 2 ? p : b))
    }
    let clickSelected: string | null | undefined
    if (o.click !== false && sample) {
      useUi.getState().clear()
      await dispatchClick(sample.x, sample.y)
      clickSelected = useUi.getState().selected
    }
    return {
      state,
      device,
      axis: state === 'FREE' ? (o.axis ?? 'x') : undefined,
      offset: state === 'FREE' ? (o.offset ?? 3) : undefined,
      capPixels,
      correct,
      wrong,
      sample,
      clickSelected,
      ok: capPixels >= 5 && correct === capPixels && (clickSelected === undefined || clickSelected === device),
    }
  }

  const rotors = () =>
    reg.rotors.map((r) => ({
      id: r.rec.id,
      ready: r.ready,
      angle: round(r.angle, 4),
      axis_world: r.axis.clone().transformDirection(r.pivot.parent!.matrixWorld).toArray().map((v) => round(v, 4)),
      rpm: r.rec.rpm,
      slow: r.rec.display_slow,
    }))

  const rotorTest = async (s = 2) => {
    const ui = useUi.getState()
    const modeBefore = ui.rotorMode
    ui.setRotorMode('slow')
    await raf()
    const a0 = new Map(reg.rotors.map((r) => [r.rec.id, r.angle]))
    const t0 = performance.now()
    await sleep(s * 1000)
    const t = (performance.now() - t0) / 1000
    const out = reg.rotors.map((r) => {
      const expected = ((2 * Math.PI * r.rec.rpm) / 60 / r.rec.display_slow) * t
      const measured = r.angle - (a0.get(r.rec.id) ?? 0)
      return {
        id: r.rec.id,
        ready: r.ready,
        deg_per_s: round((measured / t) * (180 / Math.PI), 2),
        expected: round(expected, 4),
        measured: round(measured, 4),
        err: round(Math.abs(measured - expected) / Math.abs(expected), 4),
      }
    })
    ui.setRotorMode(modeBefore)
    return { seconds: round(t, 3), rotors: out, ok: out.length === 8 && out.every((r) => r.ready && r.err <= 0.05) }
  }

  const stats = async () => {
    const f0 = frameCounter.n
    const t0 = performance.now()
    await sleep(3000)
    const fps = (frameCounter.n - f0) / ((performance.now() - t0) / 1000)
    await raf()
    const i = get().gl.info
    const mem = (performance as unknown as { memory?: { usedJSHeapSize: number } }).memory
    return {
      state: useUi.getState().state,
      fps: round(fps),
      calls: i.render.calls,
      triangles: i.render.triangles,
      geometries: i.memory.geometries,
      textures: i.memory.textures,
      programs: i.programs?.length ?? null,
      devices: reg.devices.size,
      heap_mb: mem ? round(mem.usedJSHeapSize / 1048576) : null,
      dpr: get().gl.getPixelRatio(),
      size: { w: get().size.width, h: get().size.height },
      load: {
        line_first_frame_ms: reg.stats.line_first_frame_ms === null ? null : round(reg.stats.line_first_frame_ms),
        interior_ready_ms: reg.stats.interior_ready_ms === null ? null : round(reg.stats.interior_ready_ms),
        bvh_ms: round(reg.stats.bvh_ms),
        line_rig_ms: reg.stats.line_rig_ms === null ? null : round(reg.stats.line_rig_ms),
        interior_rig_ms: reg.stats.interior_rig_ms === null ? null : round(reg.stats.interior_rig_ms),
      },
      precompile: { ...precompileStats, ms: round(precompileStats.ms) },
    }
  }

  const orbitTest = async (seconds = 5) => {
    const c = controlsRef.current
    if (!c) return { ok: false }
    const f0 = frameCounter.n
    const t0 = performance.now()
    let last = t0
    while (performance.now() - t0 < seconds * 1000) {
      await raf()
      const now = performance.now()
      void c.rotate(((2 * Math.PI) / seconds) * ((now - last) / 1000), 0, false)
      last = now
    }
    return { ok: true, fps: round((frameCounter.n - f0) / ((performance.now() - t0) / 1000)) }
  }

  // ---------------------------------------------------------------------------------------------------
  // selftest(): runs the in-page part of D1–D9 (network, console, file sizes and screenshots need the
  // chrome-devtools MCP / terminal). Results also land in window.__ze.lastSelftest while it runs.
  const canvasAt = (x: number, y: number) => document.elementFromPoint(x, y) === canvas()
  const findPixel = (id: string) => {
    const box = reg.boxOfDevice(id)
    if (box.isEmpty()) return null
    const r = screenRectOfBox(box)
    const cx = (r.x0 + r.x1) / 2
    const cy = (r.y0 + r.y1) / 2
    const pts: { x: number; y: number }[] = []
    const N = 16
    for (let i = 0; i < N; i++)
      for (let j = 0; j < N; j++)
        pts.push({ x: Math.round(r.x0 + ((i + 0.5) / N) * (r.x1 - r.x0)), y: Math.round(r.y0 + ((j + 0.5) / N) * (r.y1 - r.y0)) })
    pts.sort((a, b) => (a.x - cx) ** 2 + (a.y - cy) ** 2 - ((b.x - cx) ** 2 + (b.y - cy) ** 2))
    const s = get().size
    for (const p of pts) {
      // keep clear of the panels (tree 300 px left, info 340 px right, toolbar on top: the info panel grows
      // after a selection) so a real mouse click at the same pixel would also reach the canvas
      if (p.x < 320 || p.x > s.width - 360 || p.y < 90 || p.y > s.height - 12 || !canvasAt(p.x, p.y)) continue
      const h = pickAt(p.x, p.y)
      if (h && h.device_id === id) return { ...p, part: h.part }
    }
    return null
  }
  const key = (k: string) => window.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true }))
  const targetNow = () => {
    const t = new THREE.Vector3()
    controlsRef.current?.getTarget(t)
    return t
  }

  /** review-flow-01 recheck M1: after entering FREE, changing the axis or flipping, the camera's END pose faces the section */
  const endPose = () => {
    const c = controlsRef.current!
    const pos = c.getPosition(new THREE.Vector3(), true)
    const dir = c.getTarget(new THREE.Vector3(), true).sub(pos).normalize()
    return { pos, side: round(freePlane.distanceToPoint(pos), 2), dot: round(dir.dot(freePlane.normal), 2) }
  }
  const freeCamTest = async () => {
    const ui = useUi.getState
    const off = reg.data.states.FREE.offset_default_m
    const cases: Record<string, unknown>[] = []
    const check = (name: string, o: { still?: THREE.Vector3 } = {}) => {
      const e = endPose()
      const moved = o.still ? round(o.still.distanceTo(e.pos), 4) : null
      // gate on geometry only: cap-pixel counts depend on the framing (PLAN-FLOW-M1-M3 Task 1 step 3)
      const ok = e.side < 0 && e.dot >= 0.3 && (moved === null || moved < 1e-3)
      cases.push({ name, side: e.side, dot: e.dot, used: freeCamDebug.last, moved, ok })
    }
    for (const start of ['FLOW', 'FULL', 'CUT_X2450'] as FixedStateId[])
      for (const axis of ['x', 'y', 'z'] as Axis[])
        for (const flip of [false, true]) {
          await changeState(start, { camera: true, smooth: false })
          const before = endPose().pos
          ui().setFree({ axis, offset: off[axis], flip }) // not in FREE: no camera job
          await changeState('FREE')
          // FULL and CUT_X2450 already face x = 3: the camera must not move (review recheck)
          check(`${start}->FREE ${axis}${flip ? ' flip' : ''}`, !flip && axis === 'x' && start !== 'FLOW' ? { still: before } : {})
        }
    // inside FREE, from the FLOW camera (z cut): change axis and flip
    await changeState('FLOW', { camera: true, smooth: false })
    ui().setFree({ axis: 'z', offset: 0, flip: false })
    await changeState('FREE')
    const steps: [Axis, boolean][] = [['x', false], ['x', true], ['y', true], ['y', false], ['z', true], ['z', false]]
    for (const [axis, flip] of steps) {
      ui().setFree({ axis, offset: off[axis], flip })
      await queueDrained()
      check(`in FREE -> ${axis}${flip ? ' flip' : ''}`)
    }
    // fast clicks: y then x at once; the second job must see the first flight's END pose (review-plan I1)
    ui().setFree({ axis: 'y', offset: off.y, flip: false })
    ui().setFree({ axis: 'x', offset: off.x, flip: false })
    await queueDrained()
    check('fast y -> x')
    // a low horizontal cut, flipped: mirror fallback near the floor (review-plan I2)
    ui().setFree({ axis: 'y', offset: 0.3, flip: true })
    await queueDrained()
    check('y = 0.3 flip')
    await changeState('FULL', { camera: true, smooth: false })
    return { cases, ok: cases.every((c) => c.ok) }
  }

  /** render now and read the whole canvas once (sRGB bytes); at(x, y) takes buffer pixels, y from the top */
  const readFrame = () => {
    const s = get()
    s.gl.render(s.scene, s.camera)
    const g = s.gl.getContext()
    const w = g.drawingBufferWidth
    const h = g.drawingBufferHeight
    const buf = new Uint8Array(w * h * 4)
    g.readPixels(0, 0, w, h, g.RGBA, g.UNSIGNED_BYTE, buf)
    const at = (x: number, y: number): [number, number, number] => {
      const i = ((h - 1 - y) * w + x) * 4
      return [buf[i], buf[i + 1], buf[i + 2]]
    }
    return { w, h, at }
  }
  /**
   * review-flow-01 M3 + N1: every pixel whose view ray meets the cut plane inside a roll's section (profile shrunk
   * by 10 mm, away from the edges) must show the state's steel cap colour, hatched (x 1 or x 0.72); at most 0.05 %
   * may differ (the 1 px N1 curtain line was 562 of 306 296 = 0.18 %). Dark marker pixels, a 2 px ring around
   * them and marker / cap mixes (antialiased edges) are skipped. Plus: the marker stays dark at the FLOW
   * preset, and a ray at the middle roll's centre picks the roll, not the stand behind it.
   */
  const rollCoreProbe = async () => {
    const ui = useUi.getState
    const mode = ui().rotorMode
    const frozen = ui().frozen
    ui().setRotorMode('off')
    ui().setFrozen(true)
    const rolls = (['bottom', 'middle', 'top'] as const).map((k) => reg.data.nodes[`ctx_roll_${k}`].section!)
    const views: Record<string, unknown>[] = []
    const tonesOf = (hex: string) =>
      [1, 0.72].map((k) => {
        const o = { r: 0, g: 0, b: 0 }
        new THREE.Color(hex).multiplyScalar(k).getRGB(o, THREE.SRGBColorSpace)
        return [o.r * 255, o.g * 255, o.b * 255]
      })
    // a far, thin marker has no pixel dark enough for the 2 px ring: its antialiased pixels are a mix of the
    // marker (7, 10, 12) and a cap tone, a + k (t - a) with 0 < k < 1 (measured: k 0.43 .. 0.77). Skip those too.
    const MARKER = [7, 10, 12]
    const markerEdge = (c: number[], tones: number[][]) =>
      tones.some((t) => {
        const d = t.map((q, j) => q - MARKER[j])
        const k = d.reduce((acc, q, j) => acc + q * (c[j] - MARKER[j]), 0) / d.reduce((acc, q) => acc + q * q, 0)
        return k > 0 && k < 1 && d.every((q, j) => Math.abs(MARKER[j] + k * q - c[j]) <= 8)
      })
    const ray = new THREE.Raycaster()
    const ndc = new THREE.Vector2()
    const P = new THREE.Vector3()
    const scan = async (name: string, pos: V3, target: V3, plane: () => THREE.Plane, capHex: string) => {
      ;(controlsRef.current!.camera as THREE.PerspectiveCamera).setFocalLength(35)
      await controlsRef.current!.setLookAt(...pos, ...target, false)
      await raf2()
      const t0 = performance.now()
      const s = get()
      const f = readFrame()
      const dpr = f.w / s.size.width
      const tones = tonesOf(capHex)
      const pl = plane()
      const dark = (x: number, y: number) => Math.max(...f.at(x, y)) < 70
      // screen box of the rolls' bounding boxes (conservative), clamped to the buffer
      let x0 = f.w
      let y0 = f.h
      let x1 = 0
      let y1 = 0
      for (const r of rolls)
        for (const sx of [-1, 1])
          for (const sy of [-1, 1])
            for (const sz of [-1, 1]) {
              const v = new THREE.Vector3(r.centre[0] + sx * 0.4, r.centre[1] + sy * 0.4, r.centre[2] + sz * 1.6).project(s.camera)
              const px = ((v.x + 1) / 2) * f.w
              const py = ((1 - v.y) / 2) * f.h
              x0 = Math.min(x0, px)
              x1 = Math.max(x1, px)
              y0 = Math.min(y0, py)
              y1 = Math.max(y1, py)
            }
      x0 = Math.max(2, Math.floor(x0))
      y0 = Math.max(2, Math.floor(y0))
      x1 = Math.min(f.w - 3, Math.ceil(x1))
      y1 = Math.min(f.h - 3, Math.ceil(y1))
      let n = 0
      let bad = 0
      const badAt: unknown[] = []
      for (let y = y0; y <= y1; y++)
        for (let x = x0; x <= x1; x++) {
          ndc.set(((x + 0.5) / f.w) * 2 - 1, -((y + 0.5) / f.h) * 2 + 1)
          ray.setFromCamera(ndc, s.camera)
          if (!ray.ray.intersectPlane(pl, P) || !rolls.some((r) => inSection(P, r, 0.01))) continue
          let nearDark = false
          for (let dy = -2; dy <= 2 && !nearDark; dy++) for (let dx = -2; dx <= 2 && !nearDark; dx++) nearDark = dark(x + dx, y + dy)
          if (nearDark) continue
          const c = f.at(x, y)
          if (!tones.some((t) => Math.max(...t.map((q, j) => Math.abs(q - c[j]))) <= 8) && markerEdge(c, tones)) continue
          n++
          if (!tones.some((t) => Math.max(...t.map((q, j) => Math.abs(q - c[j]))) <= 8)) {
            bad++
            if (badAt.length < 6) badAt.push({ x: Math.round(x / dpr), y: Math.round(y / dpr), rgb: c })
          }
        }
      views.push({ name, pixels: n, bad, badAt, ms: Math.round(performance.now() - t0), ok: n >= 2000 && bad / n <= 0.0005 })
    }
    await changeState('FLOW', { camera: true, smooth: false })
    const flowPlane = () => statePlane('FLOW')!
    const capFlow = reg.data.states.FLOW.cap_colors!.steel
    await scan('FLOW axis', [10.05, 1.85, -3.2], [9.776, 1.601, 0], flowPlane, capFlow)
    // a ray 0.10 m from the middle roll's axis (inside the journal radius) picks the roll, not the stand behind it
    // (review-plan I4; at r = 0 the ray hits the journal's end-cap fan instead)
    const c = new THREE.Vector3(9.776, 1.701, 0).project(get().camera)
    const pick = pickAt(((c.x + 1) / 2) * get().size.width, ((1 - c.y) / 2) * get().size.height)
    views.push({ name: 'FLOW axis pick', object: pick?.object ?? null, ok: pick?.device_id === 'ctx_roll_middle' })
    await scan('FLOW oblique (N1)', [11.6, 2.6, -2.4], [9.78, 1.6, 0.2], flowPlane, capFlow)
    // the marker stays dark at the FLOW preset (cap 8 depth steps behind the plane, marker 0.7 mm in front, 25 m away)
    await applyPreset(reg.data.states.FLOW.camera!, false)
    await raf2()
    const mk = reg.parts.get('anim_roll_markers_middle_aa')
    const mc = mk ? reg.boxOfMeshes(mk.meshes).getCenter(new THREE.Vector3()).project(get().camera) : null
    const fr = readFrame()
    const markerRgb = mc ? fr.at(Math.round(((mc.x + 1) / 2) * fr.w), Math.round(((1 - mc.y) / 2) * fr.h)) : null
    views.push({ name: 'FLOW preset marker', rgb: markerRgb, ok: !!markerRgb && Math.max(...markerRgb) < 70 })
    const capSteel = reg.data.materials.cap_colors.steel!
    ui().setFree({ axis: 'z', offset: 0, flip: false })
    await changeState('FREE')
    await queueDrained()
    await scan('FREE z=0 axis', [10.05, 1.85, -3.2], [9.776, 1.601, 0], () => freePlane, capSteel)
    ui().setFree({ axis: 'z', offset: 0, flip: true })
    await queueDrained()
    await scan('FREE z=0 flip, from +z', [10.05, 1.85, 3.2], [9.776, 1.601, 0], () => freePlane, capSteel)
    ui().setFree({ axis: 'x', offset: 9.776, flip: false })
    await queueDrained()
    // plane through the 3 axes: body and journal bands (the stand showed through the journal before the fix)
    await scan('FREE x=9.776', [13.2, 1.9, -1.2], [9.776, 1.601, 0], () => freePlane, capSteel)
    await changeState('FULL', { camera: true, smooth: false })
    ui().setFrozen(frozen)
    ui().setRotorMode(mode)
    return { views, ok: views.every((v) => v.ok) }
  }

  const selftest = async () => {
    const out: Record<string, unknown> = { started: new Date().toISOString() }
    api.lastSelftest = out
    const ui = useUi.getState
    const full = reg.data.states.FULL.camera!
    await changeState('FULL', { camera: true, smooth: false })
    await raf2()
    out.selfcheck_start = selfcheck()
    out.stats_FULL = await stats()

    // D2 (amended gate: selectAll 190/190; tree selection is builder A's DeviceTree)
    out.D2_selectAll = api.selectAll()

    // D3: one visible device per section, at the FULL preset
    const picked: string[] = []
    for (const sec of reg.data.devices.sections)
      for (const d of reg.data.devices.devices.filter((x) => x.group === sec.group))
        if (findPixel(d.device_id)) {
          picked.push(d.device_id)
          break
        }
    // fill up to 10 when a section has nothing clickable at this camera
    for (const d of reg.data.devices.devices) {
      if (picked.length >= 10) break
      if (!picked.includes(d.device_id) && findPixel(d.device_id)) picked.push(d.device_id)
    }
    const d3: Record<string, unknown>[] = []
    for (const id of picked) {
      ui().clear()
      await raf()
      const p = findPixel(id)!
      const click = await api.clickAt(p.x, p.y)
      const alt = await api.clickAt(p.x, p.y, { alt: true })
      key('Escape')
      await raf()
      const afterEsc = ui().selected
      d3.push({
        id,
        x: p.x,
        y: p.y,
        click_ok: click.selected === id && click.part === null && click.outlineMeshes > 0 && !!click.bbox,
        alt_ok: alt.selected === id && alt.part === p.part,
        alt_part: alt.part,
        esc_ok: afterEsc === null,
      })
    }
    // double click zooms (target moves to the device), F zooms to the selection, empty click clears
    let extra: Record<string, unknown> = {}
    if (picked.length >= 2) {
      const a = picked[0]
      const pa = findPixel(a)!
      await api.clickAt(pa.x, pa.y, { dbl: true })
      await sleep(1200)
      const ca = reg.boxOfDevice(a).getBoundingSphere(new THREE.Sphere()).center
      const dblDist = targetNow().distanceTo(ca)
      await applyPreset(full, false)
      await raf2()
      const b = picked[picked.length - 1]
      ui().select(b)
      key('f')
      await sleep(1200)
      const cb = reg.boxOfDevice(b).getBoundingSphere(new THREE.Sphere()).center
      const fDist = targetNow().distanceTo(cb)
      await applyPreset(full, false)
      await raf2()
      let empty: { x: number; y: number } | null = null
      for (let y = 120; y < 1000 && !empty; y += 40)
        for (let x = 340; x < 1560 && !empty; x += 40) if (canvasAt(x, y) && !pickAt(x, y)) empty = { x, y }
      ui().select(b)
      let emptyClear: boolean | null = null
      if (empty) {
        await api.clickAt(empty.x, empty.y)
        emptyClear = ui().selected === null
      }
      extra = {
        dbl_device: a,
        dbl_target_dist_m: round(dblDist, 4),
        dbl_ok: dblDist < 0.01,
        f_device: b,
        f_target_dist_m: round(fDist, 4),
        f_ok: fDist < 0.01,
        empty,
        empty_click_clears: emptyClear,
      }
    }
    out.D3 = {
      devices: d3,
      ...extra,
      ok:
        d3.length >= 10 &&
        d3.every((r) => r.click_ok && r.alt_ok && r.esc_ok) &&
        extra.dbl_ok === true &&
        extra.f_ok === true &&
        extra.empty_click_clears === true,
    }
    ui().clear()

    // D4 + D9 per state
    const caps: { ok: boolean }[] = []
    const st: Record<string, unknown> = {}
    for (const [s, d] of [
      ['CUT_FEED', 'feed_throat'],
      ['CUT_Z_BARREL', 'barrel_b3'],
      ['CUT_X2450', 'barrel_b3'],
      ['CUT_X4120', 'barrel_b5'],
    ] as [FixedStateId, string][]) {
      await changeState(s, { camera: true, smooth: false })
      st[s] = await stats()
      caps.push(await capCheck(s, d))
      ui().clear()
    }
    caps.push(await capCheck('CUT_X2450', 'screws'))
    ui().clear()
    await changeState('FULL', { camera: true, smooth: false })
    caps.push(await capCheck('FREE', 'barrel_b4', { axis: 'x', offset: 3 }))
    ui().clear()
    await applyPreset(full, false)
    await raf2()
    st.FREE_x3000 = await stats()
    const extraCaps = [
      await capCheck('FREE', 'barrel_b3', { axis: 'y', offset: 1.2 }),
      await capCheck('FREE', 'barrel_b4', { axis: 'z', offset: 0 }),
    ]
    ui().clear()
    out.D4 = { cases: caps, ok: caps.every((c) => c.ok), extra_free_y_z: extraCaps }
    const budget: Record<string, [number, number]> = { FULL: [55, 850], FREE_x3000: [40, 1100] }
    const d9 = Object.entries({ FULL: out.stats_FULL, ...st }).map(([k, v]) => {
      const s = v as { fps: number; calls: number; triangles: number; heap_mb: number | null }
      const [fps, calls] = budget[k] ?? [45, 1000]
      return {
        state: k,
        fps: s.fps,
        calls: s.calls,
        triangles: s.triangles,
        heap_mb: s.heap_mb,
        ok: s.fps >= fps && s.calls <= calls && s.triangles <= 1.7e6 && (s.heap_mb ?? 0) <= 600,
      }
    })
    out.D9 = {
      states: d9,
      ok: d9.every((r) => r.ok),
      note: 'read after 3 s at each state camera preset (FREE x = 3.0 at the FULL preset camera), DPR 1, 1920x1080',
    }

    // D7
    const times = []
    for (const id of ['FULL', 'CUT_FEED', 'CUT_Z_BARREL', 'CUT_X2450', 'CUT_X4120', 'FLOW', 'FREE'] as StateId[])
      times.push(await timeState(id))
    await changeState('FREE')
    let sliderMax = 0
    const gaps: number[] = []
    let last = await raf()
    for (let i = 0; i < 30; i++) {
      const t0 = performance.now()
      ui().setFree({ offset: 2.0 + i * 0.05 })
      sliderMax = Math.max(sliderMax, performance.now() - t0)
      const now = await raf()
      gaps.push(now - last)
      last = now
    }
    ui().setFree({ offset: 3.0 })
    const avgGap = gaps.reduce((a, b) => a + b, 0) / gaps.length
    out.D7 = {
      times,
      slider: { js_ms_max: round(sliderMax, 3), frame_ms_avg: round(avgGap, 2), frame_ms_max: round(Math.max(...gaps), 2) },
      ok: times.every((t) => t.ok) && avgGap <= 16.7 && sliderMax < 1,
    }

    // D6, D8, D5, D1, D14 (runtime part)
    out.D6 = await cutRoundTrip()
    await changeState('FULL', { camera: true, smooth: false })
    out.D8 = await rotorTest(2)
    const sc = selfcheck()
    out.D5 = { rayUnfiltered: sc.rayUnfiltered, rayUnfilteredEmpties: sc.rayUnfilteredEmpties, ok: sc.rayUnfiltered === 0 && sc.rayUnfilteredEmpties === 0 }
    out.selfcheck_end = sc
    const l = (out.stats_FULL as { load: { line_first_frame_ms: number } }).load
    const iready = reg.stats.interior_ready_ms
    out.D1 = {
      line_first_frame_ms: l.line_first_frame_ms,
      interior_ready_ms: iready === null ? null : round(iready),
      bvh_ms: round(reg.stats.bvh_ms),
      ok: l.line_first_frame_ms <= 4000 && iready !== null && iready <= 1500 && reg.stats.bvh_ms <= 800,
    }
    out.D14_runtime = {
      devices: sc.devices,
      unknownNodes: sc.unknownNodes,
      missingNodes: sc.missingNodes,
      orphans: sc.orphans,
      ok: sc.devices === 190 && !sc.unknownNodes && !sc.missingNodes && !sc.orphans,
    }
    ui().clear()

    // PLAN-FLOW F2–F6, F8 (runtime part)
    await changeState('FLOW', { camera: true, smooth: false })
    await raf2()
    const fs = selfcheck()
    out.F2 = {
      time: await timeState('FLOW'),
      rayUnfiltered: fs.rayUnfiltered,
      roundTrip: { ok: (out.D6 as { ok: boolean }).ok, states: (out.D6 as { states: string[] }).states, flowLeft: (out.D6 as { flowLeft: boolean }).flowLeft },
    }
    ;(out.F2 as { ok?: boolean }).ok =
      (out.F2 as { time: { ok: boolean } }).time.ok && fs.rayUnfiltered === 0 && (out.D6 as { ok: boolean }).ok
    const f3: unknown[] = []
    for (const d of ['feed_throat', 'barrel_b3', 'melt_gear_pump', 'die_body_lower', 'ctx_roll_middle']) {
      const runs = []
      for (let k = 0; k < 3; k++) runs.push(await capCheck('FLOW', d, { click: k === 0 }))
      ui().clear()
      f3.push({ device: d, runs: runs.map((r) => ({ ok: r.ok, capPixels: r.capPixels, correct: r.correct, clickSelected: r.clickSelected })), ok: runs.every((r) => r.ok) })
    }
    out.F3 = { cases: f3, ok: f3.every((c) => (c as { ok: boolean }).ok) }
    await changeState('FLOW', { camera: true, smooth: false })
    out.F4 = await pelletTest(2)
    out.F5 = fillProbe()
    out.F6 = await sheetProbe(1)
    await applyPreset(reg.data.states.FLOW.camera!, false)
    await raf2()
    const sf = await stats()
    out.F8 = {
      fps: sf.fps,
      calls: sf.calls,
      triangles: sf.triangles,
      heap_mb: sf.heap_mb,
      precompile_ms: round(precompileStats.ms),
      ok: sf.fps >= 45 && sf.calls <= 1000 && sf.triangles <= 1.7e6 && (sf.heap_mb ?? 0) <= 600,
    }
    out.M3 = await rollCoreProbe()
    out.M1 = await freeCamTest()
    await changeState('FULL', { camera: true, smooth: false })
    out.finished = new Date().toISOString()
    return out
  }

  const api = {
    ready,
    selftest,
    lastSelftest: null as unknown,
    selfcheck,
    stats,
    devices: () => [...reg.devices.keys()],
    select: (id: string | null, part?: string | null) => {
      useUi.getState().select(id, part ?? null)
      return selection()
    },
    selectAll: () => {
      const failed: string[] = []
      for (const id of reg.devices.keys()) {
        useUi.getState().select(id)
        if (useUi.getState().selected !== id) failed.push(id)
      }
      useUi.getState().clear()
      return { ok: reg.devices.size - failed.length, total: reg.devices.size, failed }
    },
    selection,
    clear: () => useUi.getState().clear(),
    clickAt: async (x: number, y: number, o: { alt?: boolean; dbl?: boolean } = {}) => {
      await dispatchClick(x, y, o)
      return selection()
    },
    pickAt,
    project,
    setState: async (id: StateId, o: { camera?: boolean; smooth?: boolean; peel?: boolean } = {}) => {
      if (id === 'FREE') await changeState('FREE')
      else await changeState(id, { camera: o.camera, smooth: o.smooth })
      return useUi.getState().state
    },
    setFreeClip,
    timeState,
    freeze,
    flowProbe,
    pelletTest,
    fillColorAt,
    fillProbe,
    sheetProbe,
    cutRoundTrip,
    capCheck,
    freeCamTest,
    rollCoreProbe,
    rotors,
    rotorTest,
    camera: async (id: FixedStateId) => {
      const cam = reg.data.states[id]?.camera
      if (cam) await applyPreset(cam, false)
      await raf2()
    },
    orbitTest,
    cam: () => {
      const s = get()
      const cam = s.camera as THREE.PerspectiveCamera
      const t = new THREE.Vector3()
      controlsRef.current?.getTarget(t)
      return {
        pos: cam.position.toArray().map((v) => round(v, 3)),
        target: t.toArray().map((v) => round(v, 3)),
        fov: round(cam.fov, 2),
        lens: round(cam.getFocalLength(), 1),
        zoom: round(cam.zoom, 3),
        aspect: round(cam.aspect, 3),
        near: cam.near,
        far: cam.far,
        controls: !!controlsRef.current,
        sameCamera: controlsRef.current?.camera === cam,
      }
    },
    queue: () => ({ idle: queueIdle(), running: queueRunning() }),
    drained: () => queueDrained(),
    reg,
    store: useUi,
    controls: controlsRef,
    r3f: get,
  }
  ;(window as unknown as { __ze: typeof api }).__ze = api
  return api
}
