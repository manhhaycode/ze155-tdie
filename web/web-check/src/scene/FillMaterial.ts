import * as THREE from 'three'
import type { FlowParams } from '../data'
import { glf as f, glVec3 as vec3, heatGlsl, heatRgb, hexToRgb, tempAt, zoneAt } from './heat'

// PLAN-FLOW §3.3: the melt fill of the FLOW state. One shared material per kind, built with the FLOW plane
// already in clippingPlanes, so it never goes through cutVariant (whose clone() would drop onBeforeCompile).
// Colour: phase (pellet -> melt over the X 1.52–1.90 m ramp) or heat (zone set point on the 20–300 °C scale).
// Drifting stripes show the conveying speed. The clocks are integrated speeds, not uTime * v, so switching
// the rotor mode never makes the stripes jump: uScrewT = ∫ kScrew dt, uRollT = ∫ kRoll dt (Flow.tsx).

export type FillKind = 'line' | 'die' | 'curtain'

/** shared by every FLOW material (fills, curtain, sheet); written once per frame by <Flow/> */
export const flowUniforms = {
  uScrewT: { value: 0 },
  uRollT: { value: 0 },
  /** 0 = phase, 1 = heat */
  uMode: { value: 0 },
}

const KIND_ID: Record<FillKind, number> = { line: 0, die: 1, curtain: 2 }
/** extra emissive share of the fill colour, so the colours read inside dark bores and on the far side */
const GLOW = 0.35
const cache = new Map<string, THREE.MeshStandardMaterial>()


/** speed of the melt stripes downstream of the screws (illustrative: zone z09's conveying speed) */
export function meltSpeedReal(flow: FlowParams): number {
  const z = flow.zones.find((q) => q.zone === flow.melt.speed_zone)
  return ((z?.pitch_m ?? 0.12) * flow.screw_rpm) / 60
}

function glslZones(flow: FlowParams) {
  const line = flow.zones.filter((z) => z.speed !== 'roll_lip')
  const a = line.map((z) => `vec4(${f(z.x_m[0])}, ${f(z.x_m[1])}, ${f(z.temp_c[0])}, ${f(z.temp_c[1])})`)
  const b = line.map((z) => `vec3(${f(z.pitch_m)}, ${z.speed === 'screw' ? '0.0' : '1.0'}, ${f(z.fill_top_m ?? 0)})`)
  return `#define ZE_NZ ${line.length}
const vec4 ZE_ZA[ZE_NZ] = vec4[ZE_NZ](${a.join(', ')});
const vec3 ZE_ZB[ZE_NZ] = vec3[ZE_NZ](${b.join(', ')});
const float ZE_T_FIRST = ${f(line[0].temp_c[0])};
const float ZE_T_LAST = ${f(line[line.length - 1].temp_c[1])};
const float ZE_X_FIRST = ${f(line[0].x_m[0])};
`
}

export function fillHeader(flow: FlowParams): string {
  const [r0, r1] = flow.phase_ramp_x_m
  const bore = flow.pellets.bore
  return `uniform float uScrewT;
uniform float uRollT;
uniform float uMode;
varying vec3 vZeWorld;
${heatGlsl(flow.heat_stops)}
${glslZones(flow)}
const vec3 ZE_PELLET = ${vec3(flow.colors.pellet)};
const vec3 ZE_MELT = ${vec3(flow.colors.melt)};
const float ZE_RAMP0 = ${f(r0)};
const float ZE_RAMP1 = ${f(r1)};
const float ZE_RPS = ${f(flow.screw_rpm / 60)};
const float ZE_MELT_V = ${f(meltSpeedReal(flow))};
const float ZE_MELT_STRIPE = ${f(flow.melt.stripe_m)};
const float ZE_OP = ${f(flow.opacity)};
const float ZE_OP_SOLID = ${f(flow.opacity_solid)};
const vec2 ZE_DIE_O = vec2(${f(flow.die.origin_m[0])}, ${f(flow.die.origin_m[2])});
const float ZE_DIE_T = ${f(flow.die.temp_c[0])};
const vec2 ZE_C_X = vec2(${f(flow.curtain.x_m[0])}, ${f(flow.curtain.x_m[1])});
const vec2 ZE_C_T = vec2(${f(flow.curtain.temp_c[0])}, ${f(flow.curtain.temp_c[1])});
const float ZE_C_V = ${f(flow.curtain.speed_m_s_real)};
const float ZE_C_STRIPE = ${f(flow.curtain.stripe_m)};
const float ZE_BORE_Y = ${f(bore.centre_y_m)};
const float ZE_BORE_WAIST = ${f(Math.sqrt(bore.r_m ** 2 - bore.centre_z_m ** 2))};
`
}

const FILL_FRAGMENT = /* glsl */ `
  float zeT = ZE_T_FIRST;
  float zeM = 1.0;
  float zeS = vZeWorld.x;
  float zeTravel = 0.0;
  float zePer = ZE_MELT_STRIPE;
  float zeAlpha = ZE_OP;
#if ZE_KIND == 0
  {
    float x = vZeWorld.x;
    bool found = false;
    for (int i = 0; i < ZE_NZ; i++) {
      vec4 a = ZE_ZA[i];
      if (x >= a.x && x <= a.y) {
        zeT = mix(a.z, a.w, clamp((x - a.x) / max(a.y - a.x, 1e-4), 0.0, 1.0));
        zePer = ZE_ZB[i].y < 0.5 ? ZE_ZB[i].x : ZE_MELT_STRIPE;
        zeTravel = ZE_ZB[i].y < 0.5 ? ZE_ZB[i].x * ZE_RPS * uScrewT : ZE_MELT_V * uScrewT;
        found = true;
        break;
      }
    }
    if (!found) zeT = x < ZE_X_FIRST ? ZE_T_FIRST : ZE_T_LAST;
    zeM = smoothstep(ZE_RAMP0, ZE_RAMP1, x);
    zeAlpha = mix(ZE_OP_SOLID, ZE_OP, zeM);
  }
#elif ZE_KIND == 1
  zeS = length(vec2(vZeWorld.x, vZeWorld.z) - ZE_DIE_O);
  zeT = ZE_DIE_T;
  zeTravel = ZE_MELT_V * uScrewT;
#else
  zeT = mix(ZE_C_T.x, ZE_C_T.y, clamp((vZeWorld.x - ZE_C_X.x) / (ZE_C_X.y - ZE_C_X.x), 0.0, 1.0));
  zePer = ZE_C_STRIPE;
  zeTravel = ZE_C_V * uRollT;
  zeAlpha = 0.8;
#endif
  float zePh = fract((zeS - zeTravel) / zePer);
  float zeBright = 0.85 + 0.15 * (0.5 + 0.5 * cos(6.2831853 * zePh));
  vec3 zeC = uMode < 0.5 ? mix(ZE_PELLET, ZE_MELT, zeM) : zeHeat(zeT);
  diffuseColor = vec4(zeSrgbToLinear(zeC) * zeBright, zeAlpha);
#ifdef ZE_CAP
  // Section of a runtime-clipped screw-zone fill. Its cut face does not exist as geometry: through the cut the
  // camera sees the back faces of the far wall, which sit behind the (clipped) screw. Such a fragment is drawn
  // at the depth of the cut plane on the same view ray when that plane point lies in the melt's section: inside
  // the bore waist at the plane and below the zone's melt level. Elsewhere it keeps its own depth.
  float zeSide = dot(ZE_PN, cameraPosition) + ZE_PC;
  bool zeCapped = false;
  if (!gl_FrontFacing && zeSide < 0.0) {
    vec3 zeD = vZeWorld - cameraPosition;
    vec3 zeP = cameraPosition + zeD * clamp(-zeSide / dot(ZE_PN, zeD), 0.0, 1.0);
    float zeTop = 0.0;
    for (int i = 0; i < ZE_NZ; i++) {
      if (zeP.x >= ZE_ZA[i].x && zeP.x <= ZE_ZA[i].y) {
        zeTop = ZE_ZB[i].z;
        break;
      }
    }
    if (zeTop > 0.0 && abs(zeP.y - ZE_BORE_Y) <= ZE_BORE_WAIST && zeP.y <= zeTop) {
      vec4 zeClip = projectionMatrix * viewMatrix * vec4(zeP, 1.0);
      gl_FragDepth = clamp(zeClip.z / zeClip.w * 0.5 + 0.5, 0.0, 1.0);
      zeCapped = true;
    }
  }
  if (!zeCapped) gl_FragDepth = gl_FragCoord.z;
#endif
`

/** vertex: world position for the fragment (fills are plain meshes: no instancing, no skinning) */
export function injectWorldPos(shader: THREE.WebGLProgramParametersWithUniforms) {
  shader.vertexShader = shader.vertexShader
    .replace('#include <common>', '#include <common>\nvarying vec3 vZeWorld;')
    .replace('#include <project_vertex>', '#include <project_vertex>\n  vZeWorld = (modelMatrix * vec4(transformed, 1.0)).xyz;')
}

/**
 * cap: the mesh is clipped at runtime (show_clipped), so its section is drawn at the plane (ZE_CAP above);
 * pre-cut fills (_y0, modelled cut face) use cap = false.
 */
export function makeFillMaterial(kind: FillKind, plane: THREE.Plane, flow: FlowParams, cap = false): THREE.MeshStandardMaterial {
  const key = `ze-fill-${kind}${cap ? '-cap' : ''}`
  let m = cache.get(key)
  if (m) return m
  m = new THREE.MeshStandardMaterial({
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    roughness: 0.45,
    metalness: 0,
    clippingPlanes: [plane],
  })
  // three draws transparent DoubleSide materials in two passes (back, then front) and flips the winding for
  // the back pass, so gl_FrontFacing would be true for back faces there; one pass keeps it meaningful (ZE_CAP)
  m.forceSinglePass = true
  m.name = key
  m.defines = cap ? { ZE_KIND: KIND_ID[kind], ZE_CAP: 1 } : { ZE_KIND: KIND_ID[kind] }
  m.userData = { zeFlow: kind, zeFlowCap: cap }
  const n = plane.normal
  const header = `${fillHeader(flow)}${cap ? `uniform mat4 projectionMatrix;\nconst vec3 ZE_PN = vec3(${f(n.x)}, ${f(n.y)}, ${f(n.z)});\nconst float ZE_PC = ${f(plane.constant)};\n` : ''}`
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, flowUniforms)
    injectWorldPos(shader)
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>\n${header}`)
      .replace('#include <color_fragment>', `#include <color_fragment>\n${FILL_FRAGMENT}`)
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>\n  totalEmissiveRadiance += diffuseColor.rgb * ${GLOW};`)
  }
  m.customProgramCacheKey = () => key
  cache.set(key, m)
  return m
}

const toHex = (rgb: [number, number, number]) =>
  '#' + rgb.map((v) => Math.round(THREE.MathUtils.clamp(v, 0, 1) * 255).toString(16).padStart(2, '0')).join('').toUpperCase()
const mixRgb = (a: [number, number, number], b: [number, number, number], k: number): [number, number, number] =>
  [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k]
const rgbOf = hexToRgb

/** test hook (F5): the unlit colour (sRGB, before stripes and light) the 'line' fill shader gives at x */
export function fillColorAt(x: number, mode: 'phase' | 'heat', flow: FlowParams) {
  const [r0, r1] = flow.phase_ramp_x_m
  const m = THREE.MathUtils.smoothstep(x, r0, r1)
  const T = tempAt(x, flow.zones)
  const rgb = mode === 'phase' ? mixRgb(rgbOf(flow.colors.pellet), rgbOf(flow.colors.melt), m) : heatRgb(T, flow.heat_stops)
  return {
    x,
    mode,
    hex: toHex(rgb),
    T: Math.round(T * 10) / 10,
    phase: Math.round(m * 1000) / 1000,
    alpha: Math.round((flow.opacity_solid + (flow.opacity - flow.opacity_solid) * m) * 1000) / 1000,
    zone: zoneAt(x, flow.zones)?.zone ?? null,
  }
}
export { toHex, rgbOf, mixRgb }
