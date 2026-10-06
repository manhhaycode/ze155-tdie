import * as THREE from 'three'
import type { FixedStateId, SolidSectionRec } from '../data'
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

/**
 * Clip variant of a material (DoubleSide; back faces of closed meshes drawn as a flat/hatched cap). section: the
 * mesh's solid of revolution (node_map section): inside it the cap is drawn on the plane (review-flow-01 M3).
 */
export function cutVariant(
  src: THREE.Material,
  planes: THREE.Plane[],
  key: string,
  cap: string | null,
  hatch: boolean,
  section: SolidSectionRec | null = null,
) {
  const sec = section ? `${section.centre.join(',')}/${section.profile.flat().join(',')}` : '-'
  const id = `${src.uuid}|${key}|${cap}|${hatch ? 1 : 0}|${sec}`
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
    const uSecC = { value: new THREE.Vector3(...(section?.centre ?? [0, 0, 0])) }
    const uSecP = { value: (section?.profile ?? [[0, 0], [0, 0], [0, 0]]).map(([h, r]) => new THREE.Vector2(h, r)) }
    m.onBeforeCompile = (shader) => {
      shader.uniforms.uCapColor = uCap
      shader.uniforms.uCapHatch = uHatch
      // Cap fragments are back faces of the far inner wall. Where that wall touches another solid (stacked
      // screw elements, barrel segments meeting at a flange), the neighbour's front face lies at the same
      // depth (± the meshopt quantisation: median 4–21 µm, max 0.49 mm) and z-fights with the cap. The cap
      // therefore writes a depth pulled 0.6 mm towards the camera so it wins those ties. The bias must stay
      // below the thinnest sheet wall (1.5 mm), or caps leak through thin panels of uncut parts in FREE.
      const bias = shader.fragmentShader.includes('varying vec3 vViewPosition')
      const onPlane = bias && !!section
      if (onPlane) {
        shader.uniforms.uSecC = uSecC
        shader.uniforms.uSecP = uSecP
      }
      shader.fragmentShader = shader.fragmentShader
        .replace(
          '#include <clipping_planes_pars_fragment>',
          `#include <clipping_planes_pars_fragment>
uniform vec3 uCapColor;
uniform float uCapHatch;
${bias ? 'uniform mat4 projectionMatrix;' : ''}
${onPlane ? SECTION_GLSL : ''}`,
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
    ${onPlane ? SECTION_DEPTH_GLSL : ''}
    return;
  }`,
        )
    }
    m.customProgramCacheKey = () => (section ? 'ze-cap-sec' : 'ze-cap') // one program for every roll: uniforms
    m.userData.zeCap = cap
  }
  variants.set(id, m)
  return m
}

/** review-flow-01 M3: is a world point inside the solid (3 bands, uniforms; JS twin: section.ts inSection) */
const SECTION_GLSL = `uniform vec3 uSecC;
uniform vec2 uSecP[3];
bool zeInSection(vec3 w) {
  float r = length(w.xy - uSecC.xy);
  float h = abs(w.z - uSecC.z);
  for (int i = 0; i < 3; i++) if (h <= uSecP[i].x && r <= uSecP[i].y) return true;
  return false;
}`
/**
 * review-flow-01 M3: inside the solid the section lies ON the plane. Draw the cap there, 8 depth steps behind the
 * plane (24-bit buffer) so the roll markers 0.7 mm in front still win, and anything inside the volume (roll stand,
 * journal) stays hidden. Only when the eye is on the removed side (w < 0) and the plane lies between eye and
 * fragment (den > 0). clippingPlanes[0] is this material's plane (view space): renderer.clippingPlanes stays empty.
 */
const SECTION_DEPTH_GLSL = `vec3 zeQ = -vViewPosition;
    vec4 zePl = clippingPlanes[0];
    float zeDen = dot(zePl.xyz, zeQ);
    if (zePl.w < 0.0 && zeDen > 1e-6) {
      vec3 zeP = zeQ * (-zePl.w / zeDen);
      vec3 zeW = (zeP - viewMatrix[3].xyz) * mat3(viewMatrix);
      if (zeInSection(zeW)) {
        vec4 zeS = projectionMatrix * vec4(zeP, 1.0);
        gl_FragDepth = clamp(zeS.z / zeS.w * 0.5 + 0.5 + 4.8e-7, 0.0, 1.0);
      }
    }`

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

/** a state's surface colour for a source material (cut_states material_colors); shared per material + colour */
const recoloured = new Map<string, THREE.Material>()
function recolour(src: THREE.Material, color: string | undefined): THREE.Material {
  if (!color) return src
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

export interface CutStyle {
  /** section colour by cap class */
  caps?: Record<string, string>
  /** surface colour by source material name */
  materials?: Record<string, string>
}

/** per-mesh clip variant; cap only on closed meshes with a cap colour (style: per-state colours, FLOW) */
export function clipPart(p: Part, planes: THREE.Plane[], key: string, style: CutStyle = {}) {
  const capColors = style.caps
  for (const mesh of p.meshes) {
    const base = original.get(mesh) ?? (mesh.material as THREE.Material)
    const src = recolour(base, style.materials?.[base.name])
    const own = (mesh.userData.zeCapColor as string | null) ?? null
    const cap = mesh.userData.zeClosed && own ? (capColors?.[mesh.userData.zeCapClass as string] ?? own) : null
    setMaterial(mesh, cutVariant(src, planes, key, cap, !!mesh.userData.zeHatch && !!cap, mesh.userData.zeSection ?? null))
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
  const caps: CutStyle = { caps: s.cap_colors, materials: s.material_colors }
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
