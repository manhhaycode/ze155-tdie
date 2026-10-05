// Task A6 check: the device-tree search (web-check/src/ui/search.ts, run with Node type stripping) on build/data/devices.json.
// Usage: node tools/test_search.mjs   (or make -C web test-search)
import fs from 'node:fs'
import { buildIndex, search, normVi } from '../web-check/src/ui/search.ts'
const d = JSON.parse(fs.readFileSync(new URL('../build/data/devices.json', import.meta.url), 'utf8'))
const idx = buildIndex(d.devices)
const cases = [
  ['xi lanh b3', (r) => r.length >= 1 && r[0].device_id === 'barrel_b3'],
  ['Xi lanh B3', (r) => r[0]?.device_id === 'barrel_b3'],
  ['xi lanh', (r) => ['barrel_b1','barrel_b2','barrel_b3','barrel_b4','barrel_b5','barrel_b6'].every((id) => r.slice(0, 8).some((x) => x.device_id === id))],
  ['bom', (r) => r.some((x) => x.device_id === 'melt_gear_pump') && r.some((x) => x.device_id === 'vac_pump_unit')],
  ['bơm bánh răng', (r) => r[0]?.device_id === 'melt_gear_pump'],
  ['barrel_b3', (r) => r[0]?.device_id === 'barrel_b3'],
  ['dong co', (r) => r.length > 0],
  ['zzzz', (r) => r.length === 0],
  ['', (r) => r.length === 190],
]
let bad = 0
for (const [q, ok] of cases) {
  const r = search(idx, q)
  const pass = ok(r)
  if (!pass) bad++
  console.log(pass ? 'PASS' : 'FAIL', JSON.stringify(q), r.length, r.slice(0, 7).map((x) => x.device_id).join(','))
}
console.log(normVi('Đường ống Bơm'), '| failures', bad)
process.exit(bad ? 1 : 0)
