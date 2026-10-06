// Sources of the info-panel lines (web/PLAN-PROV.md §2.3): types of /data/prov/<device_id>.json and pure helpers.
// No runtime imports, so tools/test_prov.mjs runs it in Node.

export type ProvLevel = 'sourced' | 'derived' | 'assumption'
export type LevelOrUnknown = ProvLevel | 'unknown'
/** weakest first: a line takes the weakest level of its facts */
export const LEVELS: ProvLevel[] = ['assumption', 'derived', 'sourced']

export interface ProvFact {
  level: ProvLevel
  text_vi: string
  text_ja?: string
  refs?: string[]
  /** assumption: why; derived: how it was derived */
  reason_vi?: string
  reason_ja?: string
}

export type LineKind = 'function' | 'details'
export interface ProvLine { kind: LineKind; index: number; vi: string; level: ProvLevel | null; facts: ProvFact[] }

interface ImageRef { thumb: string; large: string; tw?: number; th?: number; w?: number; h?: number }
export interface ClaimSource {
  kind: 'claim'
  title: string
  url: string
  quote: string
  claim: string
  value: number | string | null
  unit: string
  confidence: 'high' | 'medium' | 'low'
}
export interface FigureSource extends ImageRef { kind: 'figure'; page: number; pdf_url: string; caption_vi: string; caption_ja?: string }
export interface PhotoSource extends ImageRef {
  kind: 'photo'
  title: string
  page_url: string
  image_url: string | null
  shows_en: string
  shows_vi?: string
  shows_ja?: string
  credit: string | null
}
export interface DocSource {
  kind: 'doc'
  label: string
  title: string
  title_vi?: string
  title_ja?: string
  excerpt: string
  excerpt_lang: 'vi' | 'en'
  excerpt_ja?: string
  pin?: string
}
export type ProvSource = ClaimSource | FigureSource | PhotoSource | DocSource
/** the device's own source note in the design (design/parts.json `source`), split at ';'; shown for lines without facts */
export interface DeviceSource { clauses: { text: string; assumed: boolean }[]; refs: string[] }
export interface ProvDevice {
  version: number
  device_id: string
  lines: ProvLine[]
  device_source?: DeviceSource
  sources: Record<string, ProvSource>
}

/** a line the panel shows: the function (index 0) or a details line */
export interface PanelLine { kind: LineKind; index: number; vi: string }

export function panelLines(func: string | undefined, details: string[] | undefined): PanelLine[] {
  const out: PanelLine[] = func ? [{ kind: 'function', index: 0, vi: func }] : []
  details?.forEach((vi, index) => out.push({ kind: 'details', index, vi }))
  return out
}

export function weakest(facts: { level: ProvLevel }[]): ProvLevel | null {
  let best: ProvLevel | null = null
  for (const f of facts) if (best === null || LEVELS.indexOf(f.level) < LEVELS.indexOf(best)) best = f.level
  return best
}

/** the line as published, or null when it is missing or its text differs from what the panel shows (stale data) */
export function lineFor(prov: ProvDevice, kind: LineKind, index: number, vi: string): ProvLine | null {
  return prov.lines.find((l) => l.kind === kind && l.index === index && l.vi === vi) ?? null
}

export function countLevels(prov: ProvDevice, shown: PanelLine[]): Record<LevelOrUnknown, number> {
  const c: Record<LevelOrUnknown, number> = { sourced: 0, derived: 0, assumption: 0, unknown: 0 }
  for (const s of shown) c[lineFor(prov, s.kind, s.index, s.vi)?.level ?? 'unknown']++
  return c
}

/** Japanese text when there is one, else the Vietnamese */
export function pick(lang: 'vi' | 'ja', vi: string, ja: string | undefined): string {
  return lang === 'ja' && ja ? ja : vi
}
