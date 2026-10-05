// Accent-insensitive device search for the device tree (PLAN-DOT1 §4.2.10).
// normalize('NFD') -> drop U+0300..U+036F -> đ/Đ -> d -> lower case. Every query token must occur in
// name_vi, name_en or device_id; results are ranked (exact id, then phrase at the start of name_vi, ...) then by name_vi.

export interface Searchable { device_id: string; group: string; name_vi: string; name_en: string }
export interface IndexEntry<D extends Searchable> { dev: D; id: string; vi: string; hay: string }

export function normVi(s: string): string {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[đĐ]/g, 'd').toLowerCase()
}

/** normalized words joined by single spaces (punctuation and `_` become separators) */
export function words(s: string): string {
  return normVi(s).replace(/[^a-z0-9]+/g, ' ').trim()
}

export function buildIndex<D extends Searchable>(devices: D[]): IndexEntry<D>[] {
  return devices.map((dev) => ({
    dev,
    id: dev.device_id.toLowerCase(),
    vi: words(dev.name_vi),
    hay: ` ${words(dev.name_vi)} | ${words(dev.name_en)} | ${words(dev.device_id)} | ${dev.device_id.toLowerCase()} `,
  }))
}

const collator = new Intl.Collator('vi', { sensitivity: 'base', numeric: true })
export const byNameVi = (a: { name_vi: string }, b: { name_vi: string }) => collator.compare(a.name_vi, b.name_vi)

/** rank: 0 exact device_id, 1 phrase starts name_vi, 2 phrase inside name_vi, 3 phrase in name_en or device_id,
 *  4 all tokens in name_vi, 5 tokens spread over the fields; -1 no match */
export function rank(e: { vi: string; hay: string; id: string }, query: string): number {
  const phrase = words(query)
  if (!phrase) return 5
  const tokens = phrase.split(' ')
  if (!tokens.every((t) => e.hay.includes(t))) return -1
  if (query.trim().toLowerCase() === e.id) return 0
  const vi = ` ${e.vi} `
  if (vi.startsWith(` ${phrase}`)) return 1
  if (vi.includes(` ${phrase}`)) return 2
  if (e.hay.includes(` ${phrase}`)) return 3
  if (tokens.every((t) => vi.includes(t))) return 4
  return 5
}

/** matching devices, best first; an empty query returns every device sorted by name_vi */
export function search<D extends Searchable>(index: IndexEntry<D>[], query: string): D[] {
  const hits: { d: D; r: number }[] = []
  for (const e of index) {
    const r = rank(e, query)
    if (r >= 0) hits.push({ d: e.dev, r })
  }
  hits.sort((a, b) => a.r - b.r || byNameVi(a.d, b.d))
  return hits.map((h) => h.d)
}
