import * as THREE from 'three'
import type { FlowParams } from '../data'
import { glf as f, glVec3 as vec3, heatGlsl, heatRgb, hexToRgb } from './heat'
import { flowUniforms, injectWorldPos, mixRgb, toHex } from './FillMaterial'

// PLAN-FLOW §3.4: the PET sheet (ctx_sheet) in FLOW. ctx_sheet has no UV (POSITION + NORMAL only), so the
// pattern runs on the path length s(x, y) of PLAN-DOT2 §2.5: wrap over the +X side of the middle roll, wrap
// over the −X side of the top roll, then the straight take-off run. Phase: amber at the nip, clear PET by
// s = clear_at_m. Heat: the assumed cooling profile 250 -> 70 -> 50 -> 35 °C along s.

let shared: THREE.MeshStandardMaterial | null = null

interface Path { mid: [number, number]; top: [number, number]; r: number; lineY: number; lineX0: number; L1: number }

function pathOf(flow: FlowParams): Path {
  const [w1, w2, ln] = flow.sheet.path_three_xy
  return {
    mid: w1.centre!,
    top: w2.centre!,
    r: w1.r!,
    lineY: ln.from![1],
    lineX0: ln.from![0],
    L1: flow.sheet.lengths_m[0],
  }
}

/** path length along the sheet at a point (three x, y); same rule as the shader (dot2 select_rule) */
export function sheetS(x: number, y: number, flow: FlowParams): number {
  const p = pathOf(flow)
  if (y > p.lineY - 0.015 && x > p.lineX0) return 2 * p.L1 + (x - p.lineX0)
  if (y < (p.mid[1] + p.top[1]) / 2) {
    const th = Math.atan2(y - p.mid[1], x - p.mid[0])
    return THREE.MathUtils.clamp(th + Math.PI / 2, 0, Math.PI) * p.r
  }
  const ph = Math.atan2(y - p.top[1], x - p.top[0])
  const u = (((-Math.PI / 2 - ph) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)
  return p.L1 + THREE.MathUtils.clamp(u, 0, Math.PI) * p.r
}

export function sheetTempAt(s: number, flow: FlowParams): number {
  const pr = flow.sheet.temp_profile
  if (s <= pr[0][0]) return pr[0][1]
  for (let i = 1; i < pr.length; i++)
    if (s <= pr[i][0]) return pr[i - 1][1] + ((pr[i][1] - pr[i - 1][1]) * (s - pr[i - 1][0])) / (pr[i][0] - pr[i - 1][0])
  return pr[pr.length - 1][1]
}

/** test hook (F6): unlit sheet colour at path length s */
export function sheetColorAt(s: number, mode: 'phase' | 'heat', flow: FlowParams) {
  const k = THREE.MathUtils.smoothstep(s, 0, flow.sheet.clear_at_m)
  const T = sheetTempAt(s, flow)
  const rgb = mode === 'phase' ? mixRgb(hexToRgb(flow.colors.melt), hexToRgb(flow.colors.sheet_clear), k) : heatRgb(T, flow.heat_stops)
  return { s, mode, hex: toHex(rgb), T: Math.round(T * 10) / 10 }
}

function header(flow: FlowParams) {
  const p = pathOf(flow)
  const pr = flow.sheet.temp_profile
  let temp = `  if (s <= ${f(pr[0][0])}) return ${f(pr[0][1])};\n`
  for (let i = 1; i < pr.length; i++)
    temp += `  if (s <= ${f(pr[i][0])}) return mix(${f(pr[i - 1][1])}, ${f(pr[i][1])}, (s - ${f(pr[i - 1][0])}) / ${f(pr[i][0] - pr[i - 1][0])});\n`
  temp += `  return ${f(pr[pr.length - 1][1])};\n`
  return `uniform float uScrewT;
uniform float uRollT;
uniform float uMode;
varying vec3 vZeWorld;
${heatGlsl(flow.heat_stops)}
const vec3 ZE_MELT = ${vec3(flow.colors.melt)};
const vec3 ZE_CLEAR = ${vec3(flow.colors.sheet_clear)};
float zeSheetS(vec2 q) {
  if (q.y > ${f(p.lineY - 0.015)} && q.x > ${f(p.lineX0)}) return ${f(2 * p.L1)} + (q.x - ${f(p.lineX0)});
  if (q.y < ${f((p.mid[1] + p.top[1]) / 2)}) {
    float th = atan(q.y - ${f(p.mid[1])}, q.x - ${f(p.mid[0])});
    return clamp(th + 1.5707963, 0.0, 3.1415927) * ${f(p.r)};
  }
  float ph = atan(q.y - ${f(p.top[1])}, q.x - ${f(p.top[0])});
  float u = mod(-1.5707963 - ph, 6.2831853);
  return ${f(p.L1)} + clamp(u, 0.0, 3.1415927) * ${f(p.r)};
}
float zeSheetT(float s) {
${temp}}
`
}

function fragment(flow: FlowParams) {
  const sh = flow.sheet
  return `
  float zeS = zeSheetS(vZeWorld.xy);
  float zeK = smoothstep(0.0, ${f(sh.clear_at_m)}, zeS);
  vec3 zeC = uMode < 0.5 ? mix(ZE_MELT, ZE_CLEAR, zeK) : zeHeat(zeSheetT(zeS));
  float zeBand = step(fract((zeS - ${f(sh.speed_m_s_real)} * uRollT) / ${f(sh.stripe_m)}), ${f(sh.stripe_width)});
  float zeA = mix(0.75, 0.35, zeK) + 0.25 * zeBand;
  diffuseColor = vec4(zeSrgbToLinear(zeC) * (1.0 - 0.25 * zeBand), zeA);
`
}

export function makeSheetMaterial(plane: THREE.Plane, flow: FlowParams): THREE.MeshStandardMaterial {
  if (shared) return shared
  const m = new THREE.MeshStandardMaterial({
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    roughness: 0.1,
    metalness: 0,
    clippingPlanes: [plane],
  })
  m.name = 'ze-sheet'
  m.userData = { zeFlow: 'sheet' }
  const h = header(flow)
  const frag = fragment(flow)
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, flowUniforms)
    injectWorldPos(shader)
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>\n${h}`)
      .replace('#include <color_fragment>', `#include <color_fragment>\n${frag}`)
      .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\n  totalEmissiveRadiance += diffuseColor.rgb * 0.25;')
  }
  m.customProgramCacheKey = () => 'ze-sheet'
  shared = m
  return m
}
