// PLAN-PROV Task 4: the viewer's provenance model (web-check/src/ui/provModel.ts) and lazy loader (prov.ts) against
// build/prov/out and build/data/devices.json. Node type stripping, like test_search.mjs.
// Usage: node tools/test_prov.mjs   (or make -C web test-prov, after make prov)
import fs from 'node:fs'
import { countLevels, lineFor, panelLines, pick, weakest } from '../web-check/src/ui/provModel.ts'
import { loadProv } from '../web-check/src/ui/prov.ts'

const out = new URL('../build/prov/out/', import.meta.url)
const devices = JSON.parse(fs.readFileSync(new URL('../build/data/devices.json', import.meta.url), 'utf8')).devices
let bad = 0
const ok = (cond, msg) => {
  if (!cond) {
    bad++
    console.log('FAIL', msg)
  }
}

// pure helpers
ok(weakest([]) === null, 'weakest([]) is null')
ok(weakest([{ level: 'sourced' }, { level: 'assumption' }, { level: 'derived' }]) === 'assumption', 'weakest picks assumption')
ok(weakest([{ level: 'sourced' }, { level: 'derived' }]) === 'derived', 'weakest picks derived')
ok(pick('ja', 'vi text', '') === 'vi text' && pick('ja', 'a', 'b') === 'b' && pick('vi', 'a', 'b') === 'a', 'pick falls back to VI')

// every device file against the panel lines
let files = 0, lines = 0, levels = { sourced: 0, derived: 0, assumption: 0, unknown: 0 }
for (const d of devices) {
  const shown = panelLines(d.function_vi, d.details_vi)
  const f = new URL(`${d.device_id}.json`, out)
  if (d.synthetic || shown.length === 0) {
    ok(!fs.existsSync(f), `${d.device_id}: synthetic device has no prov file`)
    continue
  }
  if (!fs.existsSync(f)) {
    ok(false, `${d.device_id}: prov file missing`)
    continue
  }
  files++
  const prov = JSON.parse(fs.readFileSync(f, 'utf8'))
  ok(prov.device_id === d.device_id, `${d.device_id}: device_id`)
  for (const s of shown) {
    lines++
    const ln = lineFor(prov, s.kind, s.index, s.vi)
    ok(ln !== null, `${d.device_id} ${s.kind}[${s.index}]: line found`)
    if (!ln) continue
    ok(weakest(ln.facts) === ln.level, `${d.device_id} ${s.kind}[${s.index}]: level ${ln.level} is the weakest fact`)
    for (const fact of ln.facts) {
      for (const r of fact.refs ?? []) ok(r in prov.sources, `${d.device_id}: ref ${r} in sources`)
    }
  }
  ok(lineFor(prov, 'function', 0, (d.function_vi ?? '') + ' (đổi)') === null, `${d.device_id}: changed text gives no line (drift)`)
  const c = countLevels(prov, shown)
  ok(Object.values(c).reduce((a, b) => a + b, 0) === shown.length, `${d.device_id}: counts add up`)
  for (const k of Object.keys(levels)) levels[k] += c[k]
  for (const [id, s] of Object.entries(prov.sources)) {
    if (s.kind !== 'figure' && s.kind !== 'photo') continue
    for (const p of [s.thumb, s.large]) ok(fs.existsSync(new URL(p.replace('/data/prov/', ''), out)), `${id}: image ${p}`)
  }
}

// lazy loader: one fetch per device, a non-JSON answer (Vite dev serves index.html for a missing file) is a failure
// that is retried on the next call, a file of another device is rejected
const calls = []
globalThis.fetch = async (url) => {
  calls.push(url)
  const id = decodeURIComponent(url.match(/\/data\/prov\/(.*)\.json$/)[1])
  if (id === 'missing') return new Response('<!doctype html>', { status: 200, headers: { 'content-type': 'text/html' } })
  const body = id === 'wrong' ? { version: 1, device_id: 'other', lines: [], sources: {} } : { version: 1, device_id: id, lines: [], sources: {} }
  return new Response(JSON.stringify(body), { status: 200, headers: { 'content-type': 'application/json' } })
}
console.warn = () => {}
const [a, b] = await Promise.all([loadProv('barrel_b3'), loadProv('barrel_b3')])
ok(a && a === b && calls.length === 1, 'loadProv: one request for two calls')
await loadProv('barrel_b3')
ok(calls.length === 1, 'loadProv: cached')
ok((await loadProv('missing')) === null, 'loadProv: HTML answer is null')
await loadProv('missing')
ok(calls.filter((u) => u.includes('missing')).length === 2, 'loadProv: a failed load is retried')
ok((await loadProv('wrong')) === null, 'loadProv: file of another device is null')

console.log(`test_prov: ${files} device files, ${lines} lines`, levels, `| failures ${bad}`)
process.exit(bad ? 1 : 0)
