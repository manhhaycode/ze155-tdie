// check_glb.mjs - Đợt 1 GLB analysis and data verification (PLAN-DOT1 §3.4). Node ESM, three r186 + MeshoptDecoder.
//
//   node tools/check_glb.mjs analyze                 -> build/reports/glb_analysis.json   (exit 1 on any failure)
//   node tools/check_glb.mjs verify [--data DIR] [--report FILE]
//                                                    -> build/reports/check.json          (exit 1 on any failure)
//
// cwd does not matter: every path is resolved from this file (web/tools/). Nothing outside web/build/ is written.
// Ported from web/build/probe/scripts/load_check.mjs and closed_check.mjs.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js'

const WEB = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const BUILD = path.join(WEB, 'build')
const R = (...p) => path.join(WEB, ...p)
const FILES = ['line', 'interior']

// Deliberate expectations (PLAN-DOT1 §0.2, §3.4). If the model changes on purpose, update them here, on purpose.
const EXPECT = {
  line: { nodes: 354, meshNodes: 351, empties: 3, meshes: 771, tris: 1189654, closed: 344, maxBytes: 7_000_000 },
  interior: { nodes: 207, meshNodes: 205, empties: 2, meshes: 438, tris: 413006, closed: 177, maxBytes: 2_500_000 },
}
const QUANTIZE_SPLIT = ['int_pump_gear_bottom', 'int_pump_gear_top', 'int_sc_disc', 'int_valve_bolt']
const MORPH = { nodes: ['int_die_section_upper', 'int_die_thermal_bolt_y0', 'int_die_thermal_bolts_y0', 'int_fill_die_y0'], keys: ['gap_x10', 'lip_push'] }
const BBOX_DEV_MAX_M = 0.001 // raw vs compressed, per named node, world AABB of the subtree
const DEVICE_BBOX_TOL_M = 0.001 // devices.json bbox_m vs union of the device's line nodes (compressed, exact vertices)
const PIVOT_TOL_M = 0.001 // rotor pivot_m vs world position of an exported empty in its attach list
const VARIANT_SUFFIXES = ['_lo', '_y0', '_x2450', '_x4120']

// ---------------------------------------------------------------- loading and node helpers
async function load(file) {
  const buf = fs.readFileSync(file)
  const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength)
  const loader = new GLTFLoader()
  loader.setMeshoptDecoder(MeshoptDecoder)
  const t0 = performance.now()
  const gltf = await new Promise((res, rej) => loader.parse(ab, '', res, rej))
  gltf.scene.updateMatrixWorld(true)
  return { scene: gltf.scene, ms: performance.now() - t0, bytes: buf.byteLength }
}
const isNamed = (o) => typeof o.userData.name === 'string' && o.userData.name.length > 0
function namedParent(o) {
  for (let p = o.parent; p; p = p.parent) if (isNamed(p)) return p.userData.name
  return null
}
// meshes that belong to this named node and not to a named descendant
function payloadMeshes(o) {
  const out = []
  const walk = (x) => { if (x !== o && isNamed(x)) return; if (x.isMesh) out.push(x); x.children.forEach(walk) }
  walk(o)
  return out
}
// how the node carries its geometry: self (Mesh), group (Group of unnamed meshes), child (one unnamed child, the
// quantize split), mixed (unnamed meshes next to named children; raw GLB only), none (empty)
function payloadForm(o) {
  if (o.isMesh) return 'self'
  const unnamed = o.children.filter((c) => !isNamed(c))
  const named = o.children.filter(isNamed)
  if (!unnamed.length) return 'none'
  if (unnamed.every((c) => c.isMesh) && !named.length) return 'group'
  if (unnamed.every((c) => c.isMesh)) return 'mixed'
  if (unnamed.length === 1) return 'child'
  return 'other'
}
const triCount = (m) => (m.geometry.index ? m.geometry.index.count : m.geometry.attributes.position.count) / 3
const r6 = (v) => Math.round(v * 1e6) / 1e6
const boxArr = (b) => (b.isEmpty() ? null : [b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z].map(r6))
function boxDev(a, b) {
  return Math.max(...['x', 'y', 'z'].flatMap((k) => [Math.abs(a.min[k] - b.min[k]), Math.abs(a.max[k] - b.max[k])]))
}
function exactBox(meshes) {
  const b = new THREE.Box3()
  for (const m of meshes) b.expandByObject(m, true)
  return b
}

function inspect(scene) {
  const named = new Map(); const dups = []; const renamed = []; const unnamedNonMesh = []
  let meshes = 0, tris = 0; const geos = new Set()
  scene.traverse((o) => {
    if (o === scene) return
    if (isNamed(o)) {
      const n = o.userData.name
      if (named.has(n)) dups.push(n)
      named.set(n, o)
      if (o.name !== THREE.PropertyBinding.sanitizeNodeName(n) || o.name !== n) renamed.push([n, o.name])
    } else if (!o.isMesh) unnamedNonMesh.push({ type: o.type, parent: namedParent(o) })
    if (o.isMesh) { meshes++; geos.add(o.geometry); tris += triCount(o) }
  })
  return { named, dups, renamed, unnamedNonMesh, meshes, tris, geos: geos.size }
}

// closed test on the RAW GLB: weld by exact position (6 decimals), all primitives of the payload together
function closedTest(meshes, root) {
  const key = new Map(); let nid = 0; const edges = new Map(); let vol = 0
  const inv = new THREE.Matrix4().copy(root.matrixWorld).invert()
  const v = new THREE.Vector3(); const cr = new THREE.Vector3()
  for (const m of meshes) {
    const g = m.geometry, pos = g.attributes.position, idx = g.index
    const mat = new THREE.Matrix4().multiplyMatrices(inv, m.matrixWorld)
    const ids = new Int32Array(pos.count); const P3 = new Array(pos.count)
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i).applyMatrix4(mat)
      const k = `${v.x.toFixed(6)},${v.y.toFixed(6)},${v.z.toFixed(6)}`
      let id = key.get(k); if (id === undefined) { id = nid++; key.set(k, id) }
      ids[i] = id; P3[i] = v.clone()
    }
    const n = idx ? idx.count : pos.count
    for (let t = 0; t < n; t += 3) {
      const a = idx ? idx.getX(t) : t, b = idx ? idx.getX(t + 1) : t + 1, c = idx ? idx.getX(t + 2) : t + 2
      vol += P3[a].dot(cr.crossVectors(P3[b], P3[c])) / 6
      const tri = [ids[a], ids[b], ids[c]]
      if (tri[0] === tri[1] || tri[1] === tri[2] || tri[0] === tri[2]) continue
      for (let e = 0; e < 3; e++) {
        const u = tri[e], w = tri[(e + 1) % 3]; const k = u < w ? `${u}_${w}` : `${w}_${u}`
        let r = edges.get(k); if (!r) { r = [0, 0]; edges.set(k, r) }
        r[u < w ? 0 : 1]++
      }
    }
  }
  let boundary = 0, flipped = 0, multi = 0
  for (const [f, b] of edges.values()) {
    const tot = f + b
    if (tot === 1) boundary++
    else if (tot === 2 && (f === 2 || b === 2)) flipped++
    else if (tot > 2) multi++
  }
  return { closed: boundary === 0 && flipped === 0 && vol > 0, boundary, flipped, multi, vol: r6(vol) }
}

const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'))
function writeJson(p, obj) {
  const ap = path.resolve(p)
  if (!ap.startsWith(BUILD + path.sep)) throw new Error(`refusing to write outside web/build/: ${ap}`)
  fs.mkdirSync(path.dirname(ap), { recursive: true })
  fs.writeFileSync(ap, JSON.stringify(obj, null, 1))
}
function argVal(flag, dflt) {
  const i = process.argv.indexOf(flag)
  return i > 0 && process.argv[i + 1] ? path.resolve(process.argv[i + 1]) : dflt
}
function finish(kind, report, outPath, summary) {
  report.ok = report.failures.length === 0
  writeJson(outPath, report)
  console.log(`${kind}: ${summary}`)
  if (!report.ok) {
    console.log(`${kind} FAILED: ${report.failures.length} failure(s)`)
    for (const f of report.failures.slice(0, 40)) console.log(`  [${f.code}] ${f.name ?? ''} ${f.detail ?? ''}`)
    if (report.failures.length > 40) console.log(`  ... ${report.failures.length - 40} more in ${path.relative(WEB, outPath)}`)
    process.exit(1)
  }
  console.log(`${kind} OK -> ${path.relative(WEB, outPath)}`)
}

// ---------------------------------------------------------------- analyze
async function analyze() {
  const t0 = performance.now()
  const failures = []
  const fail = (code, name, detail) => failures.push({ code, name, detail })
  const exportReport = readJson(R('build/reports/export.json'))
  const exportLog = fs.existsSync(R('build/reports/export.log')) ? fs.readFileSync(R('build/reports/export.log'), 'utf8') : ''
  const invalidMeshes = [...exportLog.matchAll(/WARNING: Mesh (\S+) is not valid/g)].map((m) => m[1])
  if (!exportReport.blend_unchanged) fail('BLEND_CHANGED', exportReport.blend, 'export.json blend_unchanged is not true')
  const contract = readJson(R('model-contract.json'))
  const contractMats = new Map(contract.materials.map((m) => [m.material, m]))
  const out = { version: 1, tool: 'web/tools/check_glb.mjs analyze', three: THREE.REVISION, generated_at: new Date().toISOString(),
    blend: { path: exportReport.blend, mtime: exportReport.blend_mtime_before, size: exportReport.blend_size_before, unchanged: exportReport.blend_unchanged },
    export_invalid_meshes: invalidMeshes, files: {}, failures }
  const allNames = new Map()
  const usedMats = new Set()

  for (const f of FILES) {
    const E = EXPECT[f]
    const raw = await load(R(`build/raw/${f}.glb`))
    const cmp = await load(R(`build/models/${f}.glb`))
    const a = inspect(raw.scene), b = inspect(cmp.scene)
    const ex = exportReport.files[f]
    const rec = { bytes_raw: raw.bytes, bytes: cmp.bytes, parse_ms_raw: Math.round(raw.ms), parse_ms: Math.round(cmp.ms) }

    // names
    for (const [x, label] of [[a, 'raw'], [b, 'compressed']]) {
      for (const n of x.dups) fail('NAME_DUP', n, `${f} ${label}`)
      for (const [n, got] of x.renamed) fail('NAME_RENAMED', n, `${f} ${label}: three name ${got}`)
    }
    const namesCmp = [...b.named.keys()].sort()
    const namesRaw = [...a.named.keys()].sort()
    if (JSON.stringify(namesCmp) !== JSON.stringify(namesRaw)) fail('NAMES_RAW_VS_COMPRESSED', f, 'named node sets differ')
    const exported = [...ex.names].sort()
    for (const n of exported) if (!b.named.has(n)) fail('NAME_MISSING', n, `${f}: exported by Blender, absent from the GLB`)
    for (const n of namesCmp) if (!exported.includes(n)) fail('NAME_EXTRA', n, `${f}: in the GLB, not in export.json names`)
    for (const n of namesCmp) {
      if (allNames.has(n)) fail('NAME_DUP_ACROSS_FILES', n, `${allNames.get(n)} and ${f}`)
      allNames.set(n, f)
    }

    // per node
    const nodes = {}
    let meshNodes = 0, empties = 0, closedCount = 0
    const split = []; const devs = []; let maxDev = 0, worst = null
    const triMismatch = []
    const exportedMesh = ex.tris_per_object || {}
    for (const n of namesCmp) {
      const o = b.named.get(n), r = a.named.get(n)
      const pm = payloadMeshes(o), pmRaw = payloadMeshes(r)
      const form = payloadForm(o)
      const node = { parent: namedParent(o), form, form_raw: payloadForm(r), meshes: pm.length }
      const p = new THREE.Vector3().setFromMatrixPosition(o.matrixWorld)
      node.pos = [p.x, p.y, p.z].map(r6)
      if (pm.length) {
        meshNodes++
        node.type = 'mesh'
        node.tris = pm.reduce((s, m) => s + triCount(m), 0)
        node.materials = [...new Set(pm.map((m) => m.material.name))]
        node.materials.forEach((m) => usedMats.add(m))
        const matsRaw = [...new Set(pmRaw.map((m) => m.material.name))]
        if (JSON.stringify([...node.materials].sort()) !== JSON.stringify([...matsRaw].sort())) fail('MATERIALS_RAW_VS_COMPRESSED', n, `${matsRaw} -> ${node.materials}`)
        node.bbox = boxArr(exactBox(pm))
        if (form === 'child') split.push(n)
        if (form === 'other' || form === 'none') fail('PAYLOAD_FORM', n, `${f}: compressed payload form ${form}`)
        const c = closedTest(pmRaw, r)
        Object.assign(node, { closed: c.closed, boundary: c.boundary, flipped: c.flipped, multi: c.multi, vol: c.vol })
        if (c.closed) closedCount++
        const tRaw = pmRaw.reduce((s, m) => s + triCount(m), 0)
        if (tRaw !== node.tris) fail('TRIS_RAW_VS_COMPRESSED', n, `${tRaw} -> ${node.tris}`)
        if (exportedMesh[n] !== undefined && exportedMesh[n] !== node.tris) {
          triMismatch.push({ name: n, blender_eval: exportedMesh[n], glb: node.tris })
          if (!invalidMeshes.includes(n)) fail('TRIS_VS_BLENDER', n, `evaluated ${exportedMesh[n]} vs GLB ${node.tris}`)
        }
      } else {
        empties++
        node.type = 'empty'
      }
      // world bbox deviation raw vs compressed (whole subtree, like the probe)
      const ba = new THREE.Box3().setFromObject(r), bb = new THREE.Box3().setFromObject(o)
      if (!ba.isEmpty()) {
        const d = boxDev(ba, bb)
        node.bbox_dev_mm = Math.round(d * 1e6) / 1e3
        devs.push(d)
        if (d > maxDev) { maxDev = d; worst = n }
        if (d > BBOX_DEV_MAX_M) fail('BBOX_DEV', n, `${(d * 1000).toFixed(3)} mm > ${BBOX_DEV_MAX_M * 1000} mm`)
      }
      nodes[n] = node
    }
    devs.sort((x, y) => x - y)

    // morph targets
    const morph = {}
    for (const [label, x] of [['raw', a], ['compressed', b]]) {
      for (const [n, o] of x.named) for (const m of payloadMeshes(o)) {
        if (m.morphTargetDictionary && Object.keys(m.morphTargetDictionary).length) {
          const keys = Object.keys(m.morphTargetDictionary).sort()
          if (label === 'compressed') morph[n] = keys
          if (JSON.stringify(keys) !== JSON.stringify(MORPH.keys)) fail('MORPH_KEYS', n, `${f} ${label}: ${keys}`)
        }
      }
    }

    // counts
    const counts = { nodes: b.named.size, meshNodes, empties, meshes: b.meshes, tris: b.tris, geometries: b.geos,
      geometries_raw: a.geos, closed: closedCount, open: meshNodes - closedCount }
    for (const k of ['nodes', 'meshNodes', 'empties', 'meshes', 'tris', 'closed']) {
      if (counts[k] !== E[k]) fail('COUNT', `${f}.${k}`, `got ${counts[k]}, expected ${E[k]}`)
    }
    if (a.meshes !== b.meshes || a.tris !== b.tris) fail('COUNT_RAW_VS_COMPRESSED', f, `meshes ${a.meshes}/${b.meshes}, tris ${a.tris}/${b.tris}`)
    const exMeshNodes = (ex.by_type.MESH || 0) + (ex.by_type.CURVE || 0)
    if (ex.objects !== counts.nodes || exMeshNodes !== meshNodes || (ex.by_type.EMPTY || 0) !== empties) {
      fail('COUNT_VS_EXPORT', f, `export.json ${ex.objects}/${exMeshNodes}/${ex.by_type.EMPTY || 0} vs GLB ${counts.nodes}/${meshNodes}/${empties}`)
    }
    if (!ex.expect_ok) fail('EXPORT_EXPECT', f, 'export.json expect_ok is false')
    if (cmp.bytes > E.maxBytes) fail('SIZE_BUDGET', f, `${cmp.bytes} B > ${E.maxBytes} B`)

    // unnamed non-mesh objects in the compressed file must be exactly the quantize-split payload children
    const unnamedParents = b.unnamedNonMesh.map((u) => u.parent).sort()
    if (JSON.stringify(unnamedParents) !== JSON.stringify(split.slice().sort())) fail('UNNAMED_OBJECTS', f, JSON.stringify(b.unnamedNonMesh))
    if (a.unnamedNonMesh.length) fail('UNNAMED_OBJECTS_RAW', f, JSON.stringify(a.unnamedNonMesh))

    // validator output
    const validate = {}
    for (const [label, file] of [['compressed', `build/reports/${f}.validate.txt`], ['raw', `build/reports/${f}.raw.validate.txt`]]) {
      const txt = fs.existsSync(R(file)) ? fs.readFileSync(R(file), 'utf8') : ''
      const ok = txt.includes('No errors found.') && txt.includes('No warnings found.')
      const infos = [...txt.matchAll(/│\s*([A-Z_]{4,})\s*│/g)].map((m) => m[1]).filter((c) => c !== 'code')
      validate[label] = { file, errors: txt.includes('No errors found.') ? 0 : null, warnings: txt.includes('No warnings found.') ? 0 : null, info_codes: infos }
      if (!ok) fail('VALIDATOR', file, 'missing "No errors found." or "No warnings found."')
    }

    const open = Object.entries(nodes).filter(([, x]) => x.type === 'mesh' && !x.closed).map(([n]) => n)
    Object.assign(rec, {
      counts, names: namesCmp, quantize_split: split.sort(),
      bbox_dev: { max_mm: Math.round(maxDev * 1e6) / 1e3, worst, p50_mm: Math.round(devs[devs.length >> 1] * 1e6) / 1e3 },
      materials: [...new Set(Object.values(nodes).flatMap((x) => x.materials || []))].sort(),
      morph, tri_mismatch_vs_blender: triMismatch, open, validate, nodes,
    })
    out.files[f] = rec
    console.log(`${f}: ${counts.nodes} nodes (${meshNodes} mesh, ${empties} empty), ${counts.meshes} three meshes, ${counts.tris} tris, ` +
      `closed ${closedCount}/${meshNodes}, split [${split}], bbox dev max ${rec.bbox_dev.max_mm} mm (${worst}), ${cmp.bytes} B`)
  }

  const split = [...out.files.line.quantize_split, ...out.files.interior.quantize_split].sort()
  if (JSON.stringify(split) !== JSON.stringify(QUANTIZE_SPLIT)) fail('QUANTIZE_SPLIT', split.join(','), `expected ${QUANTIZE_SPLIT.join(',')}`)
  const morphNodes = Object.keys({ ...out.files.line.morph, ...out.files.interior.morph }).sort()
  if (JSON.stringify(morphNodes) !== JSON.stringify(MORPH.nodes)) fail('MORPH_NODES', morphNodes.join(','), `expected ${MORPH.nodes.join(',')}`)
  // materials: every used name must be in the contract (materials.json carries its cap colour); overrides must exist
  for (const m of usedMats) {
    const c = contractMats.get(m)
    if (!c) fail('MATERIAL_UNKNOWN', m, 'used in a GLB, absent from model-contract materials')
    else if (c.web === 'exclude') fail('MATERIAL_EXCLUDED', m, 'used in a GLB, contract says web: exclude')
  }
  const overrides = contract.materials.filter((m) => m.web === 'override').map((m) => m.material)
  for (const m of overrides) if (!usedMats.has(m)) fail('MATERIAL_OVERRIDE_MISSING', m, 'override target not used by any exported mesh')
  out.materials = { used: [...usedMats].sort(), overrides }
  out.seconds = Math.round(performance.now() - t0) / 1000
  finish('analyze', out, R('build/reports/glb_analysis.json'),
    `${allNames.size} names, split [${split}], morph ${morphNodes.length} nodes, ${usedMats.size} materials, ${out.seconds} s`)
}

// ---------------------------------------------------------------- verify
async function verify() {
  const t0 = performance.now()
  const dataDir = argVal('--data', R('build/data'))
  const outPath = argVal('--report', R('build/reports/check.json'))
  const failures = []
  const fail = (code, name, detail) => failures.push({ code, name, detail })
  const D = {}
  for (const k of ['devices', 'node_map', 'cut_states', 'rotors', 'materials']) D[k] = readJson(path.join(dataDir, `${k}.json`))
  const analysis = readJson(R('build/reports/glb_analysis.json'))
  const NM = D.node_map.nodes
  const devices = new Map(D.devices.devices.map((d) => [d.device_id, d]))
  const sections = new Set(D.devices.sections.map((s) => s.group))

  // load the compressed GLBs that will be published
  const glb = {}; const where = new Map(); const sizes = {}
  for (const f of FILES) {
    const g = await load(R(`build/models/${f}.glb`))
    sizes[f] = g.bytes
    const named = new Map()
    g.scene.traverse((o) => { if (isNamed(o)) named.set(o.userData.name, o) })
    glb[f] = { scene: g.scene, named }
    for (const n of named.keys()) where.set(n, f)
    if (g.bytes > EXPECT[f].maxBytes) fail('SIZE_BUDGET', f, `${g.bytes} B > ${EXPECT[f].maxBytes} B`)
  }

  // 1. node_map <-> GLB: 0 missing, 0 orphans, right file
  let missing = 0, orphans = 0
  for (const [n, r] of Object.entries(NM)) {
    if (!where.has(n)) { missing++; fail('NODE_MISSING', n, `node_map says ${r.file}, not in any GLB`) }
    else if (where.get(n) !== r.file) fail('NODE_WRONG_FILE', n, `node_map ${r.file}, GLB ${where.get(n)}`)
    if (!devices.has(r.device_id)) fail('NODE_UNKNOWN_DEVICE', n, r.device_id)
    if (!['part', 'interior', 'pivot'].includes(r.kind)) fail('NODE_KIND', n, r.kind)
    if ((r.kind === 'part') !== (r.file === 'line' && r.kind !== 'pivot')) fail('NODE_KIND_FILE', n, `${r.kind} in ${r.file}`)
    const an = analysis.files[r.file]?.nodes?.[n]
    if (an) {
      if ((an.type === 'empty') !== (r.kind === 'pivot')) fail('NODE_KIND_VS_GLB', n, `kind ${r.kind}, GLB node is ${an.type}`)
      if (an.type === 'mesh' && r.closed !== an.closed) fail('CLOSED_VS_ANALYSIS', n, `node_map ${r.closed}, analysis ${an.closed}`)
    }
  }
  for (const [n, f] of where) if (!NM[n]) { orphans++; fail('NODE_ORPHAN', n, `in ${f}.glb, not in node_map`) }
  const counts = { line: 0, interior: 0 }
  for (const r of Object.values(NM)) counts[r.file]++
  for (const f of FILES) if (D.node_map.counts[f] !== counts[f] || counts[f] !== glb[f].named.size) fail('NODE_COUNT', f, `counts ${D.node_map.counts[f]}, entries ${counts[f]}, GLB ${glb[f].named.size}`)

  // 2. every three Mesh maps to a device through its nearest named ancestor
  let meshes = 0, meshesMapped = 0
  for (const f of FILES) glb[f].scene.traverse((o) => {
    if (!o.isMesh) return
    meshes++
    let p = o; while (p && !isNamed(p)) p = p.parent
    const n = p?.userData.name
    if (n && NM[n] && devices.has(NM[n].device_id)) meshesMapped++
    else fail('MESH_UNMAPPED', o.name, `${f}: nearest named ancestor ${n ?? 'none'}`)
  })

  // 3. devices: 190, each >= 1 node, 189 with a line node; devices.json nodes == node_map; bbox matches the GLB
  const devNodes = new Map()
  for (const [n, r] of Object.entries(NM)) { if (!devNodes.has(r.device_id)) devNodes.set(r.device_id, []); devNodes.get(r.device_id).push(n) }
  let withLine = 0; let bboxMax = 0, bboxWorst = null
  for (const d of D.devices.devices) {
    if (!sections.has(d.group)) fail('DEVICE_GROUP', d.device_id, d.group)
    const ns = (devNodes.get(d.device_id) || []).sort()
    if (!ns.length) fail('DEVICE_NO_NODE', d.device_id, '')
    if (JSON.stringify(ns) !== JSON.stringify([...d.nodes].sort())) fail('DEVICE_NODES', d.device_id, 'devices.json nodes differ from node_map')
    if (d.has_interior !== ns.some((n) => NM[n].file === 'interior')) fail('DEVICE_HAS_INTERIOR', d.device_id, String(d.has_interior))
    const lineParts = ns.filter((n) => NM[n].file === 'line' && NM[n].kind === 'part')
    if (lineParts.length) withLine++
    const use = lineParts.length ? lineParts : ns.filter((n) => NM[n].kind !== 'pivot')
    const b = new THREE.Box3()
    for (const n of use) b.union(exactBox(payloadMeshes(glb[NM[n].file].named.get(n))))
    const c = d.bbox_m
    if (b.isEmpty() || !Array.isArray(c) || c.length !== 6) { fail('DEVICE_BBOX', d.device_id, 'no geometry or no bbox_m'); continue }
    const dev = Math.max(Math.abs(b.min.x - c[0]), Math.abs(b.min.y - c[1]), Math.abs(b.min.z - c[2]), Math.abs(b.max.x - c[3]), Math.abs(b.max.y - c[4]), Math.abs(b.max.z - c[5]))
    if (dev > bboxMax) { bboxMax = dev; bboxWorst = d.device_id }
    if (dev > DEVICE_BBOX_TOL_M) fail('DEVICE_BBOX', d.device_id, `${(dev * 1000).toFixed(2)} mm from the GLB (${lineParts.length ? 'line nodes' : 'all nodes'})`)
    const size = [0, 1, 2].map((i) => Math.round((c[i + 3] - c[i]) * 1000))
    // size_mm is rounded in Python (half-even); allow the 1 mm rounding difference
    if (!Array.isArray(d.size_mm) || d.size_mm.length !== 3 || size.some((v, i) => Math.abs(v - d.size_mm[i]) > 1)) fail('DEVICE_SIZE', d.device_id, `${d.size_mm} vs ${size}`)
  }
  if (D.devices.devices.length !== 190 || devices.size !== 190) fail('DEVICE_COUNT', '', `${D.devices.devices.length} entries, ${devices.size} unique`)
  if (withLine !== 189) fail('DEVICE_LINE_COUNT', '', `${withLine} devices with a line node, expected 189`)

  // 4. cut states: every name resolves; exclusion rules (PLAN §3.3.5)
  const S = D.cut_states.states
  const resolve = (n, ctx) => { if (!NM[n] || !where.has(n)) fail('STATE_NAME', n, ctx); return !!NM[n] }
  const fixedIds = ['FULL', 'CUT_FEED', 'CUT_Z_BARREL', 'CUT_X2450', 'CUT_X4120']
  for (const id of [...fixedIds, 'FREE']) if (!S[id]) fail('STATE_MISSING', id, '')
  const allNames = Object.keys(NM)
  // variant families: X with X_lo / X_y0 / X_x2450 / X_x4120 (covers int_screw_elem_*_12 / _12_x2450 and _22 / _22_x4120)
  const families = []
  for (const n of allNames) {
    const fam = [n, ...VARIANT_SUFFIXES.map((s) => n + s).filter((v) => NM[v])]
    if (fam.length > 1) families.push(fam)
  }
  const pairSet = new Set()
  for (const s of Object.values(S)) for (const [k, vs] of Object.entries(s.swap || {})) for (const v of vs) pairSet.add(`${k}|${v}`)
  const swapPairs = [...pairSet].map((p) => p.split('|'))
  const lineParts = allNames.filter((n) => NM[n].file === 'line' && NM[n].kind === 'part')
  const visible = {}
  for (const id of [...fixedIds, 'FREE']) {
    const s = S[id]; if (!s) continue
    const lists = ['hide', 'clip', 'show_whole', 'show_clipped', 'ghost'].filter((k) => Array.isArray(s[k]))
    for (const k of lists) for (const n of s[k]) resolve(n, `${id}.${k}`)
    for (const [k, vs] of Object.entries(s.swap || {})) { resolve(k, `${id}.swap key`); for (const v of vs) resolve(v, `${id}.swap[${k}]`) }
    const hide = new Set(s.hide || []); const swapKeys = new Set(Object.keys(s.swap || {}))
    let vis
    if (id === 'FREE') {
      const shownByRole = allNames.filter((n) => NM[n].file === 'interior' && NM[n].kind !== 'pivot' && (s.show_roles || []).includes(NM[n].role))
      for (const n of allNames) if (NM[n].file === 'interior' && NM[n].kind !== 'pivot' && !(s.show_roles || []).includes(NM[n].role) && !(s.hide_roles || []).includes(NM[n].role)) fail('FREE_ROLE_UNCOVERED', n, `role ${NM[n].role}`)
      vis = new Set([...lineParts, ...shownByRole].filter((n) => !hide.has(n) && !swapKeys.has(n)))
      if (typeof s.clip === 'string' && /renderer\.clippingPlanes/.test(s.clip) && !/not renderer\.clippingPlanes|never renderer\.clippingPlanes/.test(s.clip)) fail('FREE_NOTE', 'FREE.clip', 'note still says renderer.clippingPlanes (amendment M1)')
    } else {
      const shown = new Set([...(s.show_whole || []), ...(s.show_clipped || []), ...(s.ghost || [])])
      for (const n of shown) if (hide.has(n)) fail('STATE_HIDE_AND_SHOW', n, id)
      for (const n of s.clip || []) if (hide.has(n)) fail('STATE_CLIP_AND_HIDE', n, id)
      for (const n of s.clip || []) if (swapKeys.has(n)) fail('STATE_CLIP_AND_SWAPPED', n, id)
      vis = new Set([...lineParts.filter((n) => !hide.has(n) && !swapKeys.has(n)), ...[...shown].filter((n) => NM[n] && NM[n].kind !== 'pivot')])
      if (id === 'FULL' && (hide.size || swapKeys.size || shown.size || (s.clip || []).length)) fail('FULL_NOT_EMPTY', id, '')
      if (id !== 'FULL' && !s.plane) fail('STATE_PLANE', id, 'fixed cut state without a plane')
      if (id !== 'FULL' && !s.needs_interior) fail('STATE_NEEDS_INTERIOR', id, 'cut state must load the interior')
    }
    for (const [k, vs] of Object.entries(s.swap || {})) for (const v of vs) if (!vis.has(v)) fail('SWAP_VALUE_NOT_SHOWN', v, `${id} swap[${k}]`)
    for (const n of vis) {
      const r = NM[n]
      if (r.file === 'interior' && r.role === 'cut_only' && !(r.states || []).includes(id)) fail('CUT_ONLY_OUTSIDE_STATES', n, id)
    }
    for (const fam of families) {
      const shownFam = fam.filter((n) => vis.has(n))
      if (shownFam.length > 1) fail('EXCLUSION_VARIANTS', shownFam.join('+'), id)
    }
    for (const [k, v] of swapPairs) if (vis.has(k) && vis.has(v)) fail('EXCLUSION_SWAP_PAIR', `${k}+${v}`, id)
    visible[id] = vis.size
  }

  // 5. rotors: attach names resolve; pivot_m matches the world position of an exported empty in attach
  const pivots = []
  for (const r of D.rotors.rotors) {
    if (!devices.has(r.device_id)) fail('ROTOR_DEVICE', r.id, r.device_id)
    for (const a of r.attach) {
      resolve(a, `rotor ${r.id}.attach`)
      if (NM[a] && NM[a].device_id !== r.device_id) fail('ROTOR_ATTACH_DEVICE', a, `rotor ${r.id} device ${r.device_id}, node device ${NM[a].device_id}`)
      if (NM[a] && NM[a].kind === 'pivot') {
        const o = glb[NM[a].file].named.get(a)
        const p = new THREE.Vector3().setFromMatrixPosition(o.matrixWorld)
        const d = p.distanceTo(new THREE.Vector3(...r.pivot_m))
        pivots.push({ rotor: r.id, empty: a, dist_mm: Math.round(d * 1e6) / 1e3 })
        if (d > PIVOT_TOL_M) fail('ROTOR_PIVOT', r.id, `${(d * 1000).toFixed(3)} mm from ${a}`)
      }
    }
    const len = Math.hypot(...r.axis)
    if (Math.abs(len - 1) > 1e-6) fail('ROTOR_AXIS', r.id, String(r.axis))
  }
  const slice1 = D.rotors.rotors.filter((r) => r.slice === 1).length
  if (slice1 !== 8) fail('ROTOR_COUNT', '', `${slice1} slice-1 rotors, expected 8`)

  // 6. materials.json covers every material in the GLBs
  for (const m of analysis.materials.used) {
    const rec = D.materials.materials[m]
    if (!rec) fail('MATERIAL_MISSING', m, 'used in a GLB, absent from materials.json')
  }

  const report = { version: 1, tool: 'web/tools/check_glb.mjs verify', generated_at: new Date().toISOString(), data_dir: path.relative(WEB, dataDir),
    sizes_bytes: sizes, budgets_bytes: { line: EXPECT.line.maxBytes, interior: EXPECT.interior.maxBytes },
    counts: { nodes: Object.keys(NM).length, line: counts.line, interior: counts.interior, devices: devices.size, devices_with_line: withLine,
      missing, orphans, meshes, meshes_mapped: meshesMapped, variant_families: families.length, swap_pairs: swapPairs.length, visible_per_state: visible },
    device_bbox_dev_max_mm: Math.round(bboxMax * 1e6) / 1e3, device_bbox_worst: bboxWorst, rotor_pivots: pivots,
    blend: analysis.blend, failures }
  report.seconds = Math.round(performance.now() - t0) / 1000
  finish('verify', report, outPath,
    `${Object.keys(NM).length} nodes, ${devices.size} devices (${withLine} with line), ${meshesMapped}/${meshes} meshes mapped, ` +
    `missing ${missing}, orphans ${orphans}, device bbox max ${report.device_bbox_dev_max_mm} mm, line ${sizes.line} B, interior ${sizes.interior} B`)
}

const cmd = process.argv[2]
if (cmd === 'analyze') await analyze()
else if (cmd === 'verify') await verify()
else { console.error('usage: node tools/check_glb.mjs analyze | verify [--data DIR] [--report FILE]'); process.exit(2) }
