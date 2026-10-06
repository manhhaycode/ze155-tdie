// Runtime data (PLAN-DOT1 §4.2.1). Five JSON files under /data, fetched once, in parallel.
export type V3 = [number, number, number]
export type StateId = 'FULL' | 'CUT_FEED' | 'CUT_Z_BARREL' | 'CUT_X2450' | 'CUT_X4120' | 'FLOW' | 'FREE'
export type FixedStateId = Exclude<StateId, 'FREE'>
export type Axis = 'x' | 'y' | 'z'

// toolbar order (PLAN-FLOW §4.2: FLOW after CUT_X4120)
export const STATE_IDS: StateId[] = ['FULL', 'CUT_FEED', 'CUT_Z_BARREL', 'CUT_X2450', 'CUT_X4120', 'FLOW', 'FREE']
export const FIXED_STATE_IDS: FixedStateId[] = ['FULL', 'CUT_FEED', 'CUT_Z_BARREL', 'CUT_X2450', 'CUT_X4120', 'FLOW']

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
  /** PLAN-FLOW §4.1: coordinates and zone codes live here, not on the button */
  tooltip_vi?: string
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
  /** FLOW: also shows the pre-cut cut_only sets of these states */
  cut_only_from?: string[]
  /** FLOW: section colour per cap class, replacing materials.json cap_colors (runtime caps and pre-cut za_cap_*) */
  cap_colors?: Record<string, string>
  /** FLOW only: simulation parameters (PLAN-FLOW §3.6) */
  flow?: FlowParams
}

export type FlowKind = 'line' | 'die' | 'curtain' | 'sheet'
export interface FlowZone {
  zone: string
  x_m: [number, number]
  temp_c: [number, number]
  pitch_m: number
  speed: 'screw' | 'melt' | 'roll_lip'
  /** screw zones: top of the melt (y) in that zone's fill (a bed in the starve-fed zones, the full bore elsewhere) */
  fill_top_m?: number
}
export interface SheetSeg { seg: 'wrap' | 'line'; centre?: [number, number]; r?: number; from?: [number, number]; to?: [number, number]; sense?: string }
/** PLAN-FLOW §3.6 (cut_states.json states.FLOW.flow); every value has a source in the JSON */
export interface FlowParams {
  screw_rpm: number
  phase_ramp_x_m: [number, number]
  colors: { pellet: string; melt: string; sheet_clear: string }
  opacity: number
  opacity_solid: number
  heat_stops: [number, string][]
  heat_range_c: [number, number]
  zones: FlowZone[]
  melt: { stripe_m: number; speed_zone: string }
  die: { origin_m: V3; radius_m: number; temp_c: [number, number] }
  curtain: { x_m: [number, number]; temp_c: [number, number]; speed_m_s_real: number; stripe_m: number }
  sheet: {
    /** the two roll wraps (middle, top) */
    path_three_xy: SheetSeg[]
    /** after the top roll: polyline over the idler, down the incline, along the conveyor */
    takeoff_xy: [number, number][]
    /** points beyond the rolls (x > this) always lie on the take-off run */
    roll_x_max_m: number
    stripe_m: number
    stripe_width: number
    speed_m_s_real: number
    clear_at_m: number
    lengths_m: [number, number, number]
    temp_profile: [number, number][]
  }
  pellets: {
    N: number
    size_m: number
    fall_speed_m_s: number
    path_a_xy: [number, number][]
    spread_m: number
    z_m: [number, number]
    land_x_m: [number, number]
    bed_y_m: [number, number]
    bed_z_m: [number, number]
    bore: { centre_y_m: number; centre_z_m: number; r_m: number }
    melt_x_m: [number, number]
    temp_fall_c: number
  }
  /** node name -> which FLOW material its fill / curtain / sheet meshes get */
  materials: Record<string, FlowKind>
}

export interface FreeState {
  label_vi: string
  tooltip_vi?: string
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
