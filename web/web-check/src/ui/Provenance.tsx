// Source badges of the info-panel lines and their dialog (web/PLAN-PROV.md §1, §2.3). Data: prov.ts (lazy).
import { useEffect, useRef, useState, type KeyboardEvent } from 'react'
import { createPortal } from 'react-dom'
import type { Loc } from './i18n'
import { countLevels, pick, type LevelOrUnknown, type PanelLine, type ProvDevice, type ProvFact, type ProvLine, type ProvSource } from './provModel'
import './ui.css'

const GLYPH: Record<LevelOrUnknown, string> = { sourced: '✓', derived: '≈', assumption: '⚠', unknown: '?' }
const SUMMARY_ORDER: LevelOrUnknown[] = ['sourced', 'derived', 'assumption', 'unknown']

/** the mark at the end of a line; "?" (not a button) when the line has no published source */
export function ProvBadge({ line, loc, onOpen }: { line: ProvLine | null; loc: Loc; onOpen(line: ProvLine, opener: HTMLElement): void }) {
  const P = loc.T.prov
  if (!line?.level) {
    return (
      <span className="ze-prov" data-level="unknown" role="img" aria-label={P.level.unknown} title={P.levelHint.unknown}>
        ?
      </span>
    )
  }
  const level = line.level
  return (
    <button
      type="button"
      className="ze-prov"
      data-level={level}
      aria-haspopup="dialog"
      aria-label={P.open(P.level[level])}
      title={`${P.level[level]}: ${P.levelHint[level]}`}
      onClick={(e) => onOpen(line, e.currentTarget)}
    >
      {GLYPH[level]}
    </button>
  )
}

/** counts per level under the device name; also the legend of the marks */
export function ProvSummary({ prov, shown, loc }: { prov: ProvDevice; shown: PanelLine[]; loc: Loc }) {
  const P = loc.T.prov
  const c = countLevels(prov, shown)
  return (
    <div className="ze-prov-sum">
      <p className="ze-prov-counts">
        {SUMMARY_ORDER.filter((l) => c[l] > 0).map((l) => (
          <span key={l} className="ze-prov-count" data-level={l} title={P.levelHint[l]}>
            <span className="ze-prov-glyph" aria-hidden="true">{GLYPH[l]}</span> {c[l]} {P.level[l].toLowerCase()}
          </span>
        ))}
      </p>
      <p className="ze-prov-hint">{P.summaryHint}</p>
    </div>
  )
}

export interface OpenLine {
  line: ProvLine
  /** the line as the panel shows it (Japanese when there is a translation) */
  text: string
  /** "Chức năng" / "Chi tiết 3/6" */
  label: string
}

/** modal dialog with the facts of one line and their sources; keys never reach the viewer's shortcuts (Esc, F) */
export function ProvDialog({ prov, open, device, loc, onClose }: { prov: ProvDevice; open: OpenLine; device: string; loc: Loc; onClose(): void }) {
  const P = loc.T.prov
  const ref = useRef<HTMLDialogElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)
  const [zoom, setZoom] = useState<string | null>(null)
  const { line } = open

  useEffect(() => {
    const d = ref.current
    // StrictMode runs effects twice; a second showModal on an open dialog throws
    if (d && !d.open) d.showModal()
    closeRef.current?.focus()
  }, [])

  const close = () => ref.current?.close()
  const onKey = (e: KeyboardEvent<HTMLDialogElement>) => {
    e.stopPropagation()
    if (e.key === 'Escape' && zoom) {
      // first Esc leaves the enlarged image, the second closes the dialog
      e.preventDefault()
      setZoom(null)
    }
  }

  const z = zoom ? prov.sources[zoom] : undefined
  return createPortal(
    <dialog
      ref={ref}
      className="ze-dialog"
      lang={loc.lang}
      aria-labelledby="ze-prov-title"
      onClose={onClose}
      onKeyDown={onKey}
      onClick={(e) => {
        if (e.target === e.currentTarget) close()
      }}
    >
      <header className="ze-dlg-head">
        <div className="ze-dlg-headtext">
          <p className="ze-dlg-kicker">
            {device} – {open.label}
          </p>
          <h2 id="ze-prov-title" className="ze-dlg-title">
            {open.text}
          </h2>
        </div>
        <button ref={closeRef} type="button" className="ze-dlg-close" aria-label={P.close} onClick={close}>
          ×
        </button>
      </header>
      <div className="ze-dlg-body">
        {z && (z.kind === 'figure' || z.kind === 'photo') ? (
          <div className="ze-zoom">
            <button type="button" className="ze-btn ze-btn-sm" onClick={() => setZoom(null)} autoFocus>
              {P.back}
            </button>
            <img src={z.large} width={z.w} height={z.h} alt={z.kind === 'figure' ? P.catalogue(z.page) : z.title} />
            <SourceCard id={zoom!} src={z} loc={loc} />
          </div>
        ) : (
          <>
            {line.level && (
              <p className="ze-dlg-level" data-level={line.level}>
                <span className="ze-tag">
                  <span aria-hidden="true">{GLYPH[line.level]}</span> {P.level[line.level]}
                </span>{' '}
                {P.lineLevel[line.level]}
              </p>
            )}
            <ul className="ze-facts">
              {line.facts.map((f, i) => (
                <Fact key={i} fact={f} prov={prov} loc={loc} onZoom={setZoom} />
              ))}
            </ul>
          </>
        )}
      </div>
    </dialog>,
    document.body,
  )
}

function Fact({ fact, prov, loc, onZoom }: { fact: ProvFact; prov: ProvDevice; loc: Loc; onZoom(id: string): void }) {
  const P = loc.T.prov
  const reason = fact.reason_vi ? pick(loc.lang, fact.reason_vi, fact.reason_ja) : ''
  return (
    <li className="ze-fact" data-level={fact.level}>
      <p className="ze-tag">
        <span aria-hidden="true">{GLYPH[fact.level]}</span> {P.level[fact.level]}
      </p>
      <p className="ze-fact-text">{pick(loc.lang, fact.text_vi, fact.text_ja)}</p>
      {reason && (
        <p className="ze-fact-reason">
          <span className="ze-muted">{fact.level === 'assumption' ? P.reason : P.howDerived}: </span>
          {reason}
        </p>
      )}
      {fact.refs?.map((r) => prov.sources[r] && <SourceCard key={r} id={r} src={prov.sources[r]} loc={loc} onZoom={onZoom} />)}
    </li>
  )
}

const ext = { target: '_blank', rel: 'noopener noreferrer' } as const

function SourceCard({ id, src, loc, onZoom }: { id: string; src: ProvSource; loc: Loc; onZoom?(id: string): void }) {
  const P = loc.T.prov
  const refId = <code className="ze-id">{id.split('|')[0]}</code>
  if (src.kind === 'claim') {
    return (
      <div className="ze-src" data-kind="claim">
        <div className="ze-src-text">
          <a className="ze-link" href={src.url} {...ext}>
            {src.title}
          </a>
          <blockquote className="ze-quote">{src.quote}</blockquote>
          <p className="ze-src-note" lang="en">
            {src.claim}
          </p>
          <p className="ze-src-meta">
            {P.confidence}: {P.conf[src.confidence] ?? src.confidence}
            {refId}
          </p>
        </div>
      </div>
    )
  }
  if (src.kind === 'doc') {
    const title = pick(loc.lang, src.title_vi ?? src.title, src.title_ja)
    const excerpt = loc.lang === 'ja' && src.excerpt_ja ? src.excerpt_ja : src.excerpt
    const note = loc.lang === 'ja' && src.excerpt_ja ? '' : P.original(src.excerpt_lang)
    return (
      <div className="ze-src" data-kind="doc">
        <div className="ze-src-text">
          <p className="ze-src-meta">
            {P.internal}: {src.label}
            {refId}
          </p>
          <p className="ze-src-title">{title}</p>
          <blockquote className="ze-quote" lang={excerpt === src.excerpt ? src.excerpt_lang : loc.lang}>
            {excerpt}
          </blockquote>
          {note && <p className="ze-src-meta">{note}</p>}
        </div>
      </div>
    )
  }
  const alt = src.kind === 'figure' ? P.catalogue(src.page) : src.title
  return (
    <div className="ze-src" data-kind={src.kind}>
      {onZoom && (
        <button type="button" className="ze-src-thumb" aria-label={`${P.enlarge}: ${alt}`} onClick={() => onZoom(id)}>
          <img src={src.thumb} width={src.tw} height={src.th} loading="lazy" decoding="async" alt={alt} />
        </button>
      )}
      <div className="ze-src-text">
        {src.kind === 'figure' ? (
          <>
            <p className="ze-src-title">{P.catalogue(src.page)}</p>
            <p className="ze-src-note">{pick(loc.lang, src.caption_vi, src.caption_ja)}</p>
            <p className="ze-src-meta">
              <a className="ze-link" href={src.pdf_url} {...ext}>
                {P.openPdf(src.page)}
              </a>
              {refId}
            </p>
          </>
        ) : (
          <>
            <p className="ze-src-title">{src.title}</p>
            <p className="ze-src-note">{pick(loc.lang, src.shows_vi ?? src.shows_en, src.shows_ja)}</p>
            <p className="ze-src-meta">
              <a className="ze-link" href={src.page_url} {...ext}>
                {P.openSource}
              </a>
              {src.credit && <span> · {src.credit}</span>}
              {refId}
            </p>
          </>
        )}
      </div>
    </div>
  )
}
