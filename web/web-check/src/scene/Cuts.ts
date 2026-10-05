import * as THREE from 'three'
import type { FixedStateId } from '../data'
import { reg, isShown, type Part } from './rig'
import { ghostMaterial } from './GhostMaterial'
import { applyPreset } from './CameraRig'
import { useUi } from '../store'

// PLAN-DOT1 §4.2.6 (cut model) = r3f-snippets §6 without showChain / interiorRoot.
// Invariants: only payloads change `visible` (through setVisible, recorded); materials change only through
// setMaterial (recorded); resetCuts restores both, so FULL is exactly the load state again.
// Peel (lột vỏ) is deferred to Đợt 1b (AMENDMENTS): states just show their cut.

const variants = new Map<string, THREE.Material>()
const original = new Map<THREE.Mesh, THREE.Material>()
const changedVis = new Map<THREE.Object3D, boolean>()
const statePlanes = new Map<string, THREE.Plane>()

/** Clip variant of a material (DoubleSide; back faces of closed meshes drawn as a flat/hatched cap). */
export function cutVariant(src: THREE.Material, planes: THREE.Plane[], key: string, cap: string | null, hatch: boolean) {
  const id = `${src.uuid}|${key}|${cap}|${hatch ? 1 : 0}`
  let m = variants.get(id)
  if (m) return m
  if ((src as THREE.ShaderMaterial).isShaderMaterial) {
    variants.set(id, src) // ghost shader has no clipping chunks; never clipped (ghosts are not in clip lists)
    return src
  }
  m = src.clone()
  m.name = src.name
  m.userData = { ...src.userData, zeCut: key }
  m.clippingPlanes = planes
  m.side = THREE.DoubleSide // back faces must render (cap) and be hit by the raycast
  if (cap) {
    const uCap = { value: new THREE.Color(cap) }
    const uHatch = { value: hatch ? 1 : 0 }
    m.onBeforeCompile = (shader) => {
      shader.uniforms.uCapColor = uCap
      shader.uniforms.uCapHatch = uHatch
      // Cap fragments are back faces of the far inner wall. Where that wall touches another solid (stacked
      // screw elements, barrel segments meeting at a flange), the neighbour's front face lies at the same
      // depth (± the meshopt quantisation: median 4–21 µm, max 0.49 mm) and z-fights with the cap. The cap
      // therefore writes a depth pulled 0.6 mm towards the camera so it wins those ties. The bias must stay
      // below the thinnest sheet wall (1.5 mm), or caps leak through thin panels of uncut parts in FREE.
      const bias = shader.fragmentShader.includes('varying vec3 vViewPosition')
      shader.fragmentShader = shader.fragmentShader
        .replace(
          '#include <clipping_planes_pars_fragment>',
          `#include <clipping_planes_pars_fragment>
uniform vec3 uCapColor;
uniform float uCapHatch;
${bias ? 'uniform mat4 projectionMatrix;' : ''}`,
        )
        .replace(
          '#include <clipping_planes_fragment>',
          `#include <clipping_planes_fragment>
  ${bias ? 'gl_FragDepth = gl_FragCoord.z;' : ''}
  if (!gl_FrontFacing) {
    float hatch = mix(1.0, mix(0.72, 1.0, step(0.5, fract((gl_FragCoord.x + gl_FragCoord.y) * 0.0833))), uCapHatch);
    gl_FragColor = linearToOutputTexel(vec4(uCapColor * hatch, 1.0));
    ${
      bias
        ? `vec3 zeV = -vViewPosition;
    float zeD = length(zeV);
    vec4 zeC = projectionMatrix * vec4(zeV * (1.0 - 0.0006 / max(zeD, 1e-4)), 1.0);
    gl_FragDepth = clamp(zeC.z / zeC.w * 0.5 + 0.5, 0.0, 1.0);`
        : ''
    }
    return;
  }`,
        )
    }
    m.customProgramCacheKey = () => 'ze-cap'
    m.userData.zeCap = cap
  }
  variants.set(id, m)
  return m
}

export function statePlane(id: string): THREE.Plane | null {
  const s = reg.data.states[id as FixedStateId]
  if (!s || !('plane' in s) || !s.plane) return null
  let p = statePlanes.get(id)
  if (!p) {
    p = new THREE.Plane(new THREE.Vector3(...s.plane.normal), s.plane.constant)
    statePlanes.set(id, p)
  }
  return p
}

/** The only way cut code changes visibility. Records the value before the first change. Payloads only. */
export function setVisible(o: THREE.Object3D, v: boolean) {
  if (!changedVis.has(o)) changedVis.set(o, o.visible)
  o.visible = v
}
export function setPartVisible(p: Part, v: boolean) {
  if (p.payload) setVisible(p.payload, v) // pivots: nothing to do
}
export function partVisible(p: Part): boolean {
  return !!p.payload && isShown(p.payload)
}

/** The only way cut code changes materials. Records the load-state material before the first change. */
export function setMaterial(mesh: THREE.Mesh, m: THREE.Material) {
  if (!original.has(mesh)) original.set(mesh, mesh.material as THREE.Material)
  mesh.material = m
}

/** layers on top of a state (the FLOW layer) undo their own extras here; runs at the start of every resetCuts */
const resetHooks: (() => void)[] = []
export function onResetCuts(fn: () => void) {
  if (!resetHooks.includes(fn)) resetHooks.push(fn)
}

/** per-mesh clip variant; cap only on closed meshes with a cap colour (capColors: per-state colour by cap class) */
export function clipPart(p: Part, planes: THREE.Plane[], key: string, capColors?: Record<string, string>) {
  for (const mesh of p.meshes) {
    const src = original.get(mesh) ?? (mesh.material as THREE.Material)
    const own = (mesh.userData.zeCapColor as string | null) ?? null
    const cap = mesh.userData.zeClosed && own ? (capColors?.[mesh.userData.zeCapClass as string] ?? own) : null
    setMaterial(mesh, cutVariant(src, planes, key, cap, !!mesh.userData.zeHatch && !!cap))
  }
}

export function ghostPart(p: Part) {
  for (const mesh of p.meshes) setMaterial(mesh, ghostMaterial())
}

/** back to the load state: materials, visibility; no global planes */
export function resetCuts(gl: THREE.WebGLRenderer) {
  for (const fn of resetHooks) fn()
  for (const [mesh, m] of original) mesh.material = m
  original.clear()
  for (const [o, v] of changedVis) o.visible = v
  changedVis.clear()
  if (gl.clippingPlanes.length) gl.clippingPlanes = []
}

export async function ensureInterior() {
  if (reg.interiorLoaded) return
  useUi.getState().requestInterior()
  await reg.interiorReady
}

const part = (n: string) => reg.parts.get(n)

export interface ApplyOpts { camera?: boolean; smooth?: boolean }

/** PLAN §4.2.6 order. Call only from inside the state queue. */
export async function applyState(id: FixedStateId, o: ApplyOpts = {}): Promise<void> {
  const s = reg.data.states[id]
  if (s.needs_interior) await ensureInterior() // step 2 (the queue waits; nothing else runs meanwhile)
  resetCuts(reg.gl) // step 1
  const plane = statePlane(id)
  const planes = plane ? [plane] : []
  const caps = s.cap_colors
  for (const n of s.hide) {
    const p = part(n)
    if (p) setPartVisible(p, false)
  }
  for (const [ext, ints] of Object.entries(s.swap)) {
    const e = part(ext)
    if (!e) continue
    const targets = ints.filter((i) => reg.parts.has(i))
    if (ints.length === 0 || targets.length > 0) setPartVisible(e, false)
    else if (planes.length) clipPart(e, planes, id, caps) // missing_target_rule (never happens in Đợt 1)
  }
  if (planes.length)
    for (const n of s.clip) {
      const p = part(n)
      if (p) clipPart(p, planes, id, caps)
    }
  for (const n of s.show_whole) {
    const p = part(n)
    if (p) setPartVisible(p, true)
  }
  for (const n of s.show_clipped) {
    const p = part(n)
    if (!p) continue
    setPartVisible(p, true)
    if (planes.length) clipPart(p, planes, id, caps)
  }
  for (const n of s.ghost) {
    const p = part(n)
    if (!p) continue
    setPartVisible(p, true)
    ghostPart(p)
  }
  if (o.camera !== false && s.camera) applyPreset(s.camera, o.smooth !== false)
}

// ---- introspection for hooks ----
export const cutDebug = {
  variants: () => variants.size,
  changedMaterials: () => original.size,
  changedVisibility: () => changedVis.size,
}
