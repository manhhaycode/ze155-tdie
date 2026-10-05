// UI language (Vietnamese / Japanese). Overlay strings come from text.ts; Japanese device texts from
// /i18n/devices.ja.json (loaded on first switch to ja). Any missing Japanese field falls back to Vietnamese.
import { useMemo } from 'react'
import { create } from 'zustand'
import type { CutState, DeviceRec, FreeState, SectionRec } from '../data'
import { byNameVi } from './search'
import { T, T_JA, type Texts } from './text'

export type Lang = 'vi' | 'ja'
export const LANGS: { id: Lang; short: string; label: string }[] = [
  { id: 'vi', short: 'VI', label: 'Tiếng Việt' },
  { id: 'ja', short: '日本語', label: '日本語' },
]

interface DeviceJa { name?: string; function?: string | null; details?: string[]; connects?: string[] }
type DevicesJa = Record<string, DeviceJa>

const KEY = 'ze-lang'
const isLang = (v: unknown): v is Lang => v === 'vi' || v === 'ja'

/** ?lang=vi|ja wins over the remembered choice; the default stays Vietnamese */
function initialLang(): Lang {
  const q = new URLSearchParams(location.search).get('lang')
  if (isLang(q)) return q
  try {
    const s = localStorage.getItem(KEY)
    if (isLang(s)) return s
  } catch {
    // storage blocked: keep the default
  }
  return 'vi'
}

let jaPromise: Promise<DevicesJa> | null = null
function loadJa(): Promise<DevicesJa> {
  jaPromise ??= fetch('/i18n/devices.ja.json')
    .then((r) => (r.ok ? (r.json() as Promise<DevicesJa>) : {}))
    .catch((e: unknown) => {
      console.warn('[i18n] /i18n/devices.ja.json not loaded, device texts stay Vietnamese', e)
      return {}
    })
  return jaPromise
}

interface LangStore { lang: Lang; ja: DevicesJa | null; setLang(lang: Lang): void }

export const useLang = create<LangStore>((set, get) => ({
  lang: initialLang(),
  ja: null,
  setLang(lang) {
    try {
      localStorage.setItem(KEY, lang)
    } catch {
      // storage blocked: the choice lasts for this page only
    }
    const url = new URL(location.href)
    if (url.searchParams.has('lang')) {
      url.searchParams.set('lang', lang)
      history.replaceState(history.state, '', url)
    }
    set({ lang })
    if (lang === 'ja' && !get().ja) void loadJa().then((ja) => set({ ja }))
  },
}))

function applyDocument(lang: Lang) {
  const t = lang === 'ja' ? T_JA : T
  document.documentElement.lang = lang
  document.title = t.docTitle
}
applyDocument(useLang.getState().lang)
if (useLang.getState().lang === 'ja') void loadJa().then((ja) => useLang.setState({ ja }))
useLang.subscribe((s, prev) => s.lang !== prev.lang && applyDocument(s.lang))

/** localized accessors for the overlay; data texts fall back to the Vietnamese fields */
export interface Loc {
  lang: Lang
  T: Texts
  name(d: DeviceRec): string
  func(d: DeviceRec): string | undefined
  details(d: DeviceRec): string[] | undefined
  iface(d: DeviceRec, i: number): string | undefined
  section(s: SectionRec): string
  state(id: string, s: CutState | FreeState): string
  compare(a: DeviceRec, b: DeviceRec): number
}

const VI: Loc = {
  lang: 'vi',
  T,
  name: (d) => d.name_vi,
  func: (d) => d.function_vi,
  details: (d) => d.details_vi,
  iface: (d, i) => d.connects_to?.[i]?.interface_vi,
  section: (s) => s.name_vi,
  state: (_id, s) => s.label_vi,
  compare: byNameVi,
}

const collatorJa = new Intl.Collator('ja', { numeric: true })

function makeJa(ja: DevicesJa | null): Loc {
  const tr = (d: DeviceRec) => ja?.[d.device_id]
  const name = (d: DeviceRec) => tr(d)?.name || d.name_vi
  return {
    lang: 'ja',
    T: T_JA,
    name,
    func: (d) => tr(d)?.function || d.function_vi,
    // a stale translation (other line count than the data) is not shown
    details: (d) => {
      const t = tr(d)?.details
      return t && t.length === d.details_vi?.length ? t : d.details_vi
    },
    iface: (d, i) => tr(d)?.connects?.[i] || d.connects_to?.[i]?.interface_vi,
    section: (s) => T_JA.sections[s.group] ?? s.name_vi,
    state: (id, s) => T_JA.states[id] ?? s.label_vi,
    compare: (a, b) => collatorJa.compare(name(a), name(b)),
  }
}

export function useLoc(): Loc {
  const lang = useLang((s) => s.lang)
  const ja = useLang((s) => s.ja)
  return useMemo(() => (lang === 'ja' ? makeJa(ja) : VI), [lang, ja])
}
