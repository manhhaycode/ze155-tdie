import * as THREE from 'three'
import { useEffect, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { reg } from './rig'
import { onResetCuts, partVisible, setMaterial, statePlane } from './Cuts'
import { flowUniforms, makeFillMaterial } from './FillMaterial'
import { makeSheetMaterial } from './SheetMaterial'
import { Pellets } from './Pellets'
import { useUi, type RotorMode } from '../store'

// PLAN-FLOW §2.4 / §3: the FLOW layer. applyState('FLOW') builds the cut like any fixed state; then, still
// inside the state queue, enterFlowLayer() swaps the fill, curtain and sheet materials through the recorded
// setMaterial and shows the pellets. resetCuts (every way out of FLOW: another state, FREE, the round trip,
// precompile) first calls leaveFlowLayer through onResetCuts, then restores the load-state materials.
//
// Draw order of the translucent layers (renderOrder): fill 1, screen-changer channels 2, ghost hood 3,
// sheet and curtain 4. One clock for shaders and pellets: kScrew (off 0, slow 1/20, real 1) and kRoll
// (off 0, slow 1, real 1: the rolls' display_slow is 1); both stop while frozen.

export const K_SCREW: Record<RotorMode, number> = { off: 0, slow: 1 / 20, real: 1 }
export const K_ROLL: Record<RotorMode, number> = { off: 0, slow: 1, real: 1 }
const ORDER = { fill: 1, channels: 2, ghost: 3, sheet: 4 }
const SOURCE_MATERIAL = { line: 'za_fill_melt', die: 'za_fill_melt', curtain: 'ze_melt_curtain', sheet: 'ze_sheet_pet' } as const

/** pre-cut section materials recoloured with the FLOW cap_colors (by cap class; flat, as exported) */
const PRECUT_CAP_CLASS: Record<string, string> = {
  za_cap_steel: 'steel',
  za_cap_clad: 'steel',
  za_cap_gear: 'steel',
  za_cap_heater: 'steel',
  za_cap_screw: 'screw',
  za_cap_shaft: 'screw',
}
const recoloured = new Map<string, THREE.Material>()
function recolourCap(src: THREE.Material, color: string) {
  const id = `${src.uuid}|${color}`
  let m = recoloured.get(id)
  if (!m) {
    m = src.clone()
    m.name = src.name
    ;(m as THREE.MeshStandardMaterial).color?.set(color)
    recoloured.set(id, m)
  }
  return m
}

let holder: THREE.Group | null = null
let pellets: Pellets | null = null
let active = false
const orders = new Map<THREE.Object3D, number>()

function setOrder(o: THREE.Object3D, n: number) {
  if (!orders.has(o)) orders.set(o, o.renderOrder)
  o.renderOrder = n
}

/** FLOW kScrew / kRoll now (0 while frozen) */
export function flowRates() {
  const ui = useUi.getState()
  return ui.frozen ? { kScrew: 0, kRoll: 0 } : { kScrew: K_SCREW[ui.rotorMode], kRoll: K_ROLL[ui.rotorMode] }
}

/** Call only from inside the state queue, right after applyState('FLOW'). */
export function enterFlowLayer() {
  const flow = reg.data.states.FLOW.flow
  const plane = statePlane('FLOW')
  if (!flow || !plane) return
  const clipped = new Set(reg.data.states.FLOW.show_clipped)
  for (const [node, kind] of Object.entries(flow.materials)) {
    const p = reg.parts.get(node)
    if (!p) continue
    for (const mesh of p.meshes) {
      // a clip variant keeps its source name; multi-material nodes only swap their fill / sheet meshes
      if ((mesh.material as THREE.Material).name !== SOURCE_MATERIAL[kind]) continue
      setMaterial(mesh, kind === 'sheet' ? makeSheetMaterial(plane, flow) : makeFillMaterial(kind, plane, flow, clipped.has(node)))
      setOrder(mesh, kind === 'sheet' || kind === 'curtain' ? ORDER.sheet : ORDER.fill)
    }
  }
  const caps = reg.data.states.FLOW.cap_colors
  if (caps)
    for (const p of reg.parts.values()) {
      if (!partVisible(p)) continue
      for (const mesh of p.meshes) {
        const m = mesh.material as THREE.Material
        const cls = PRECUT_CAP_CLASS[m.name]
        // only uncut pre-cut parts: a runtime clip variant must keep its onBeforeCompile (no clone of it)
        if (cls && caps[cls] && !m.clippingPlanes?.length) setMaterial(mesh, recolourCap(m, caps[cls]))
      }
    }
  for (const m of reg.parts.get('int_sc_channels')?.meshes ?? []) setOrder(m, ORDER.channels)
  for (const n of reg.data.states.FLOW.ghost) for (const m of reg.parts.get(n)?.meshes ?? []) setOrder(m, ORDER.ghost)
  if (!pellets && holder) {
    pellets = new Pellets(flow, plane)
    holder.add(pellets.mesh)
  }
  if (pellets) {
    pellets.write(useUi.getState().flowColor)
    pellets.mesh.visible = true
  }
  active = true
}

/** undoes the extras of the layer (render order, pellets); materials are restored by resetCuts itself */
export function leaveFlowLayer() {
  for (const [o, n] of orders) o.renderOrder = n
  orders.clear()
  if (pellets) pellets.mesh.visible = false
  active = false
}
onResetCuts(leaveFlowLayer)

export const flowDebug = {
  active: () => active,
  pellets: () => pellets,
  renderOrders: () => orders.size,
}

/** mounted once in the Canvas, at the scene root (never inside the line tree) */
export function Flow() {
  const ref = useRef<THREE.Group>(null)
  useEffect(() => {
    holder = ref.current
    if (holder && pellets && pellets.mesh.parent !== holder) holder.add(pellets.mesh)
    return () => {
      holder = null
    }
  }, [])
  useFrame((_, dt) => {
    const ui = useUi.getState()
    flowUniforms.uMode.value = ui.flowColor === 'heat' ? 1 : 0
    if (!active) return
    const { kScrew, kRoll } = flowRates()
    const step = Math.min(dt, 0.1)
    flowUniforms.uScrewT.value += kScrew * step
    flowUniforms.uRollT.value += kRoll * step
    pellets?.step(step, kScrew, ui.flowColor)
  })
  return <group ref={ref} name="flow_layer" userData={{ __helper: true }} />
}
