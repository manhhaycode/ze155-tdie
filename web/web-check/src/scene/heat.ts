import * as THREE from 'three'
import type { FlowParams, FlowZone } from '../data'

// PLAN-FLOW §3.5: temperature profile along the line and the 20–300 °C colour scale. One definition for the
// shaders (generated GLSL constants), the pellet instance colours and the test hook fillColorAt.
// The scale interpolates linearly between its stops in sRGB; Color.setRGB(..., SRGBColorSpace) then
// converts to three's linear working space, exactly like the GLSL zeSrgbToLinear below.

type Stops = FlowParams['heat_stops']

export const hexToRgb = (hex: string): [number, number, number] => {
  const n = parseInt(hex.replace('#', ''), 16)
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255]
}

/** sRGB components of the scale at T (clamped to the first / last stop) */
export function heatRgb(T: number, stops: Stops): [number, number, number] {
  if (T <= stops[0][0]) return hexToRgb(stops[0][1])
  for (let i = 1; i < stops.length; i++) {
    const [t1, c1] = stops[i]
    if (T <= t1) {
      const [t0, c0] = stops[i - 1]
      const k = (T - t0) / (t1 - t0)
      const a = hexToRgb(c0)
      const b = hexToRgb(c1)
      return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k]
    }
  }
  return hexToRgb(stops[stops.length - 1][1])
}

export function heatColor(T: number, stops: Stops, out = new THREE.Color()): THREE.Color {
  const [r, g, b] = heatRgb(T, stops)
  return out.setRGB(r, g, b, THREE.SRGBColorSpace)
}

/** CSS gradient of the scale over [lo, hi] °C, for the toolbar legend */
export function heatGradientCss(stops: Stops, lo: number, hi: number): string {
  const parts = stops.map(([t, c]) => `${c} ${(((t - lo) / (hi - lo)) * 100).toFixed(1)}%`)
  return `linear-gradient(90deg, ${parts.join(', ')})`
}

/** GLSL float literal */
export const glf = (v: number) => (Number.isInteger(v) ? v.toFixed(1) : String(v))
const f = glf
/** GLSL vec3 of a hex colour's sRGB components */
export const glVec3 = (hex: string) => `vec3(${hexToRgb(hex).map((v) => v.toFixed(5)).join(', ')})`
const vec3 = glVec3

/** GLSL: `vec3 zeHeat(float T)` (sRGB) and `vec3 zeSrgbToLinear(vec3 c)` */
export function heatGlsl(stops: Stops): string {
  let body = `  if (T <= ${f(stops[0][0])}) return ${vec3(stops[0][1])};\n`
  for (let i = 1; i < stops.length; i++) {
    const [t0, c0] = stops[i - 1]
    const [t1, c1] = stops[i]
    body += `  if (T <= ${f(t1)}) return mix(${vec3(c0)}, ${vec3(c1)}, (T - ${f(t0)}) / ${f(t1 - t0)});\n`
  }
  body += `  return ${vec3(stops[stops.length - 1][1])};\n`
  return `vec3 zeHeat(float T) {\n${body}}
vec3 zeSrgbToLinear(vec3 c) {
  return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(0.04045, c));
}
`
}

/** first zone whose x range holds x (zone order = list order, like the shader loop); null outside every zone */
export function zoneAt(x: number, zones: FlowZone[]): FlowZone | null {
  for (const z of zones) if (z.speed !== 'roll_lip' && x >= z.x_m[0] && x <= z.x_m[1]) return z
  return null
}

/** zone set point at x (linear inside a zone, clamped to the line's first / last zone outside) */
export function tempAt(x: number, zones: FlowZone[]): number {
  const line = zones.filter((z) => z.speed !== 'roll_lip')
  const z = zoneAt(x, line) ?? (x < line[0].x_m[0] ? line[0] : line[line.length - 1])
  const k = THREE.MathUtils.clamp((x - z.x_m[0]) / (z.x_m[1] - z.x_m[0]), 0, 1)
  return z.temp_c[0] + (z.temp_c[1] - z.temp_c[0]) * k
}
