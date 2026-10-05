// Runtime data (PLAN-DOT1 §4.2.1). Five JSON files under /data, fetched once, in parallel.
export type V3 = [number, number, number]
export type StateId = 'FULL' | 'CUT_FEED' | 'CUT_Z_BARREL' | 'CUT_X2450' | 'CUT_X4120' | 'FREE'
export type FixedStateId = Exclude<StateId, 'FREE'>
export type Axis = 'x' | 'y' | 'z'

export const STATE_IDS: StateId[] = ['FULL', 'CUT_FEED', 'CUT_Z_BARREL', 'CUT_X2450', 'CUT_X4120', 'FREE']
export const FIXED_STATE_IDS: FixedStateId[] = ['FULL', 'CUT_FEED', 'CUT_Z_BARREL', 'CUT_X2450', 'CUT_X4120']

export interface NodeRec {
  file: 'line' | 'interior'
  device_id: string
  kind: 'part' | 'interior' | 'pivot'
  role?: 'full' | 'cut_only' | 'ghost' | 'marker' | 'pivot'
  closed?: boolean
  cap?: 'force' | 'none'
  states?: string[]
  slice?: 1 | 2
  moves_in_dot2?: string
}

export interface CameraPreset { pos: V3; target: V3; lens_mm: number; sensor_mm: number; source?: string }

export interface CutState {
  label_vi: string
  plane: { normal: V3; constant: number } | null
  needs_interior: boolean
  hide: string[]
  swap: Record<string, string[]>
  clip: string[]
  show_whole: string[]
  show_clipped: string[]
  ghost: string[]
  peel: { offset_m: V3; duration_s: number } | null
  camera: CameraPreset | null
}

export interface FreeState {
  label_vi: string
  needs_interior: true
  hide: string[]
  swap: Record<string, string[]>
  show_roles: string[]
  hide_roles: string[]
  axis_default: Axis
  offset_default_m: Record<Axis, number>
  slider_range_m: Record<Axis, [number, number]>
}

export interface ConnectRec { part: string; interface_vi: string }
export interface DeviceRec {
  device_id: string
  group: string
  name_vi: string
  name_en: string
  synthetic: boolean
  function_vi?: string
  details_vi?: string[]
  connects_to?: ConnectRec[]
  bbox_m: [number, number, number, number, number, number] | null
  size_mm: V3 | null
  has_interior: boolean
  nodes: string[]
}
export interface SectionRec { group: string; name_vi: string }
export interface DevicesJson { version: number; slice: number; sections: SectionRec[]; devices: DeviceRec[] }

export interface RotorRec {
  id: string
  pivot: string
  slice: 1 | 2
  device_id: string
  pivot_m: V3
  axis: V3
  rpm: number
  display_slow: number
  attach: string[]
  label_vi?: string
}
export interface RotorsJson { version: number; default_mode?: 'off' | 'slow' | 'real'; rotors: RotorRec[] }

export interface MaterialRec {
  web: 'keep' | 'override'
  cap_class: string
  cap_color: string | null
  three_override?: Record<string, unknown> & { type: string }
}
export interface MaterialsJson { version: number; cap_colors: Record<string, string | null>; materials: Record<string, MaterialRec> }

export interface Data {
  devices: DevicesJson
  nodes: Record<string, NodeRec>
  states: Record<FixedStateId, CutState> & { FREE: FreeState }
  rotors: RotorRec[]
  materials: MaterialsJson
  version: { devices: number; node_map: number; cut_states: number; rotors: number; materials: number }
  // lookups built once
  deviceById: Map<string, DeviceRec>
}

async function getJson<T>(name: string): Promise<T> {
  const r = await fetch(`/data/${name}.json`)
  if (!r.ok) throw new Error(`fetch /data/${name}.json: HTTP ${r.status}`)
  return (await r.json()) as T
}

async function load(): Promise<Data> {
  const [devices, nodeMap, cutStates, rotors, materials] = await Promise.all([
    getJson<DevicesJson>('devices'),
    getJson<{ version: number; nodes: Record<string, NodeRec> }>('node_map'),
    getJson<{ version: number; states: Data['states'] }>('cut_states'),
    getJson<RotorsJson>('rotors'),
    getJson<MaterialsJson>('materials'),
  ])
  return {
    devices,
    nodes: nodeMap.nodes,
    states: cutStates.states,
    rotors: rotors.rotors,
    materials,
    version: {
      devices: devices.version,
      node_map: nodeMap.version,
      cut_states: cutStates.version,
      rotors: rotors.version,
      materials: materials.version,
    },
    deviceById: new Map(devices.devices.map((d) => [d.device_id, d])),
  }
}

/** Fetched once; use React 19 `use(dataPromise)` inside Suspense, or `await dataPromise` in plain code. */
export const dataPromise: Promise<Data> = load()

export const isFree = (s: CutState | FreeState): s is FreeState => 'show_roles' in s
