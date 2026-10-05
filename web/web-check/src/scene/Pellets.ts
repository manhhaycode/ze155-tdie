import * as THREE from 'three'
import type { FlowParams } from '../data'
import { heatColor, hexToRgb, tempAt, zoneAt } from './heat'
import { noRaycast } from './Picking'

// PLAN-FLOW §3.2: the pellets of the FLOW state. One InstancedMesh (1 draw call), a helper outside the line
// tree: raycast is a no-op and userData.__helper is set, so picking and rayUnfiltered never see it.
// Each pellet runs three segments, then starts again at the top:
//   A  falls through the feed column along path_a_xy (sideways offset, z on the kept side), then to its own
//      landing point in the bore of screw B;
//   B  is conveyed along +X in the bed of zone z01 at pitch(x) * rpm / 60 * kScrew (no rotation around the
//      screw: that would need the flight geometry);
//   C  melts over melt_x_m: shrinks, flattens in y and turns from pellet colour to melt colour.
// Motion uses only kScrew and dt, so rotor mode off / freeze keep every pellet where it is.

const SEG_FALL = 0
const SEG_BARREL = 1
const SIDES = 6
/** ± sideways shake of a conveyed pellet (m) */
const WOBBLE = 0.003

/** mulberry32: a seeded generator, so a reload gives the same pellets (stable screenshots) */
function rng(seed: number) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const _m = new THREE.Matrix4()
const _s = new THREE.Matrix4()
const _q = new THREE.Quaternion()
const _ax = new THREE.Vector3()
const _c = new THREE.Color()

export class Pellets {
  readonly mesh: THREE.InstancedMesh
  readonly N: number
  private readonly flow: FlowParams
  private readonly P: FlowParams['pellets']
  private readonly rand = rng(155)
  // common part of path A
  private readonly ax: number[]
  private readonly ay: number[]
  private readonly cum: number[] = [0]
  private readonly aLen: number
  private readonly endN: [number, number]
  // per pellet
  readonly seg: Uint8Array
  /** A: distance from the top of the path; barrel: world x */
  readonly u: Float32Array
  private readonly off: Float32Array
  private readonly za: Float32Array
  private readonly landX: Float32Array
  private readonly bedY: Float32Array
  private readonly bedZ: Float32Array
  private readonly leg: Float32Array
  private readonly ph: Float32Array
  private readonly axis: Float32Array
  /** last written world position and scale (test hooks) */
  readonly pos: Float32Array
  readonly scale: Float32Array

  constructor(flow: FlowParams, plane: THREE.Plane) {
    this.flow = flow
    this.P = flow.pellets
    const N = (this.N = this.P.N)
    const r = this.P.size_m / 2
    const geo = new THREE.CylinderGeometry(r, r, this.P.size_m, SIDES, 1)
    const mat = new THREE.MeshStandardMaterial({ roughness: 0.55, metalness: 0, clippingPlanes: [plane] })
    mat.name = 'ze-pellet'
    this.mesh = new THREE.InstancedMesh(geo, mat, N)
    this.mesh.name = 'flow_pellets'
    this.mesh.frustumCulled = false
    this.mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage)
    this.mesh.userData.__helper = true
    this.mesh.raycast = noRaycast
    this.mesh.visible = false
    this.mesh.renderOrder = 0

    const path = this.P.path_a_xy
    this.ax = path.map((p) => p[0])
    this.ay = path.map((p) => p[1])
    for (let k = 1; k < path.length; k++)
      this.cum.push(this.cum[k - 1] + Math.hypot(this.ax[k] - this.ax[k - 1], this.ay[k] - this.ay[k - 1]))
    this.aLen = this.cum[this.cum.length - 1]
    const k = path.length - 1
    const dx = this.ax[k] - this.ax[k - 1]
    const dy = this.ay[k] - this.ay[k - 1]
    const l = Math.hypot(dx, dy)
    this.endN = [-dy / l, dx / l]

    this.seg = new Uint8Array(N)
    this.u = new Float32Array(N)
    this.off = new Float32Array(N)
    this.za = new Float32Array(N)
    this.landX = new Float32Array(N)
    this.bedY = new Float32Array(N)
    this.bedZ = new Float32Array(N)
    this.leg = new Float32Array(N)
    this.ph = new Float32Array(N)
    this.axis = new Float32Array(N * 3)
    this.pos = new Float32Array(N * 3)
    this.scale = new Float32Array(N)
    for (let i = 0; i < N; i++) this.respawn(i)
    this.warmStart()
    this.write('phase')
  }

  /** back to the top of path A with new random offsets, landing point and bed position */
  private respawn(i: number) {
    const P = this.P
    const R = this.rand
    this.seg[i] = SEG_FALL
    this.u[i] = 0
    this.off[i] = (R() * 2 - 1) * P.spread_m
    this.za[i] = P.z_m[0] + R() * (P.z_m[1] - P.z_m[0])
    this.landX[i] = P.land_x_m[0] + R() * (P.land_x_m[1] - P.land_x_m[0])
    // bed: inside the bore of screw B and inside the z01 fill layer; the margin keeps the whole pellet (any
    // tumble angle: half its 3D diagonal) plus the 3 mm wobble inside the bore
    const rr = P.bore.r_m - P.size_m * 0.71 - WOBBLE
    let y = 0
    let z = 0
    for (let t = 0; t < 50; t++) {
      y = P.bed_y_m[0] + R() * (P.bed_y_m[1] - P.bed_y_m[0])
      z = P.bed_z_m[0] + R() * (P.bed_z_m[1] - P.bed_z_m[0])
      if ((y - P.bore.centre_y_m) ** 2 + (z - P.bore.centre_z_m) ** 2 <= rr * rr) break
    }
    this.bedY[i] = y
    this.bedZ[i] = z
    const ex = this.ax[this.ax.length - 1] + this.endN[0] * this.off[i]
    const ey = this.ay[this.ay.length - 1] + this.endN[1] * this.off[i]
    this.leg[i] = Math.hypot(this.landX[i] - ex, y - ey)
    this.ph[i] = R() * Math.PI * 2
    _ax.set(R() - 0.5, R() - 0.5, R() - 0.5).normalize()
    this.axis.set([_ax.x, _ax.y, _ax.z], i * 3)
  }

  /** conveying speed along +X in the barrel (m/s) */
  private barrelSpeed(x: number, kScrew: number) {
    const z = zoneAt(x, this.flow.zones)
    return (((z?.pitch_m ?? 0.2535) * this.flow.screw_rpm) / 60) * kScrew
  }

  private advance(i: number, dt: number, kScrew: number) {
    if (kScrew <= 0) return
    if (this.seg[i] === SEG_FALL) {
      this.u[i] += this.P.fall_speed_m_s * dt
      if (this.u[i] >= this.aLen + this.leg[i]) {
        this.seg[i] = SEG_BARREL
        this.u[i] = this.landX[i]
      }
      return
    }
    this.u[i] += this.barrelSpeed(this.u[i], kScrew) * dt
    if (this.u[i] >= this.P.melt_x_m[1]) this.respawn(i)
  }

  /** spread the pellets over one full cycle at the slow display speed, so FLOW opens on a running line */
  private warmStart() {
    const slow = 1 / 20
    const dt = 0.05
    let cycle = (this.aLen + 0.4) / this.P.fall_speed_m_s
    for (let x = 0.34; x < this.P.melt_x_m[1]; ) {
      const v = this.barrelSpeed(x, slow)
      x += v * dt
      cycle += dt
    }
    for (let i = 0; i < this.N; i++) {
      const steps = Math.floor((this.rand() * cycle) / dt)
      for (let s = 0; s < steps; s++) this.advance(i, dt, slow)
    }
  }

  step(dt: number, kScrew: number, mode: 'phase' | 'heat') {
    for (let i = 0; i < this.N; i++) this.advance(i, dt, kScrew)
    this.write(mode)
  }

  /** matrices and colours from the current state */
  write(mode: 'phase' | 'heat') {
    const P = this.P
    const [m0, m1] = P.melt_x_m
    const pellet = hexToRgb(this.flow.colors.pellet)
    const melt = hexToRgb(this.flow.colors.melt)
    for (let i = 0; i < this.N; i++) {
      let x: number
      let y: number
      let z: number
      let angle: number
      let m = 0
      if (this.seg[i] === SEG_FALL) {
        const d = this.u[i]
        if (d < this.aLen) {
          let k = 1
          while (k < this.cum.length - 1 && this.cum[k] < d) k++
          const t = (d - this.cum[k - 1]) / (this.cum[k] - this.cum[k - 1])
          const dx = this.ax[k] - this.ax[k - 1]
          const dy = this.ay[k] - this.ay[k - 1]
          const l = Math.hypot(dx, dy)
          x = this.ax[k - 1] + dx * t - (dy / l) * this.off[i]
          y = this.ay[k - 1] + dy * t + (dx / l) * this.off[i]
          z = this.za[i]
        } else {
          const q = Math.min((d - this.aLen) / this.leg[i], 1)
          const ex = this.ax[this.ax.length - 1] + this.endN[0] * this.off[i]
          const ey = this.ay[this.ay.length - 1] + this.endN[1] * this.off[i]
          x = ex + (this.landX[i] - ex) * q
          y = ey + (this.bedY[i] - ey) * q
          z = this.za[i] + (this.bedZ[i] - this.za[i]) * q
        }
        angle = d * 12 + this.ph[i]
      } else {
        x = this.u[i]
        y = this.bedY[i] + WOBBLE * Math.sin(x * 37 + this.ph[i])
        z = Math.max(0.002, this.bedZ[i] + WOBBLE * Math.cos(x * 29 + this.ph[i]))
        angle = x * 20 + this.ph[i]
        m = THREE.MathUtils.smoothstep(x, m0, m1)
      }
      const s = 1 - m
      _ax.fromArray(this.axis, i * 3)
      _q.setFromAxisAngle(_ax, angle)
      _m.makeRotationFromQuaternion(_q).premultiply(_s.makeScale(s, s * (1 - 0.6 * m), s)).setPosition(x, y, z)
      this.mesh.setMatrixAt(i, _m)
      this.pos[i * 3] = x
      this.pos[i * 3 + 1] = y
      this.pos[i * 3 + 2] = z
      this.scale[i] = s
      if (mode === 'heat') heatColor(this.seg[i] === SEG_FALL ? P.temp_fall_c : tempAt(x, this.flow.zones), this.flow.heat_stops, _c)
      else
        _c.setRGB(
          pellet[0] + (melt[0] - pellet[0]) * m,
          pellet[1] + (melt[1] - pellet[1]) * m,
          pellet[2] + (melt[2] - pellet[2]) * m,
          THREE.SRGBColorSpace,
        )
      this.mesh.setColorAt(i, _c)
    }
    this.mesh.instanceMatrix.needsUpdate = true
    if (this.mesh.instanceColor) this.mesh.instanceColor.needsUpdate = true
  }

  /** test hook: pellets that are drawn (scale > 0.1 %) and where they are */
  probe() {
    let visible = 0
    let maxX = -Infinity
    let minZ = Infinity
    let falling = 0
    for (let i = 0; i < this.N; i++) {
      if (this.scale[i] <= 1e-3) continue
      visible++
      if (this.seg[i] === SEG_FALL) falling++
      maxX = Math.max(maxX, this.pos[i * 3])
      minZ = Math.min(minZ, this.pos[i * 3 + 2])
    }
    return { pellets: this.N, visiblePellets: visible, falling, maxPelletX: maxX, minPelletZ: minZ }
  }

  /** test hook: barrel x of every pellet (NaN while it falls) */
  barrelX(): Float64Array {
    const out = new Float64Array(this.N)
    for (let i = 0; i < this.N; i++) out[i] = this.seg[i] === SEG_BARREL ? this.u[i] : NaN
    return out
  }

  dispose() {
    this.mesh.geometry.dispose()
    ;(this.mesh.material as THREE.Material).dispose()
    this.mesh.dispose()
  }
}
