// Info panel (right): texts of the selected device (PLAN-DOT1 §4.2.10).
import { use, useState } from 'react'
import { dataPromise } from '../data'
import { reg, useUi } from './bind'
import { useLoc } from './i18n'
import { useProv } from './prov'
import { lineFor, panelLines, type LineKind, type ProvLine } from './provModel'
import { ProvBadge, ProvDialog, ProvSummary, type OpenLine } from './Provenance'
import { fmtInt } from './text'
import './ui.css'

/** true when the device has no visible mesh in the current state (e.g. `screws` at FULL) */
function isHiddenInside(id: string): boolean {
  if (reg.devices.size === 0 || !reg.devices.has(id)) return false
  return reg.meshesOfDevice(id, true).length === 0
}

/** where the unbreakable tail of a line starts: its last word, or the last 2 characters of a Japanese line */
function glueAt(text: string): number {
  const sp = text.lastIndexOf(' ')
  return sp >= 0 && text.length - sp <= 24 ? sp + 1 : Math.max(0, text.length - 2)
}

export function InfoPanel() {
  const data = use(dataPromise)
  const selected = useUi((s) => s.selected)
  const part = useUi((s) => s.selectedPart)
  const select = useUi((s) => s.select)
  const zoomTo = useUi((s) => s.zoomTo)
  const clear = useUi((s) => s.clear)
  const loc = useLoc()
  const { T } = loc
  // subscribed so the "inside" note follows the visibility after a state change or the interior load
  useUi((s) => s.cutVersion)
  useUi((s) => s.interiorLoaded)

  const dev = selected ? data.deviceById.get(selected) : undefined
  const section = dev ? data.devices.sections.find((s) => s.group === dev.group) : undefined
  const pick = (id: string) => {
    select(id)
    zoomTo(id)
  }
  // PLAN-PROV: sources of the function and details lines, fetched when the device is selected
  const shown = dev && !dev.synthetic ? panelLines(dev.function_vi, dev.details_vi) : []
  const prov = useProv(shown.length ? dev?.device_id : undefined)
  const [open, setOpen] = useState<(OpenLine & { device: string; opener: HTMLElement }) | null>(null)
  // the line text with its mark; the last word and the mark never wrap apart
  const withMark = (kind: LineKind, index: number, vi: string, text: string, label: string) => {
    if (!prov || !dev) return text
    const cut = glueAt(text)
    return (
      <>
        {text.slice(0, cut)}
        <span className="ze-nowrap">
          {text.slice(cut)}
          <ProvBadge
            line={lineFor(prov, kind, index, vi)}
            loc={loc}
            onOpen={(line: ProvLine, opener) => setOpen({ line, text, label, device: dev.device_id, opener })}
          />
        </span>
      </>
    )
  }
  const closeDialog = () => {
    const opener = open?.opener
    setOpen(null)
    if (opener?.isConnected) opener.focus()
  }

  return (
    <aside id="ze-info" className="ze-panel ze-info" aria-live="polite">
      {!dev ? (
        <p className="ze-muted">{T.info.empty}</p>
      ) : (
        <>
          <div className="ze-info-head">
            <h2 className="ze-info-title">{loc.name(dev)}</h2>
            <div className="ze-info-actions">
              <button type="button" className="ze-btn ze-btn-sm" onClick={() => zoomTo(dev.device_id)}>{T.info.zoom}</button>
              <button type="button" className="ze-btn ze-btn-sm" onClick={() => clear()}>{T.info.deselect}</button>
            </div>
          </div>
          <p className="ze-info-en">{dev.name_en}</p>
          <p className="ze-info-meta">
            <span className="ze-muted">{T.info.group}: </span>{section ? loc.section(section) : dev.group}
            <code className="ze-id">{dev.device_id}</code>
          </p>
          {prov && <ProvSummary prov={prov} shown={shown} loc={loc} />}
          {part && <p className="ze-info-part">{T.info.part(part)}</p>}
          {isHiddenInside(dev.device_id) && <p className="ze-info-inside">{T.info.inside}</p>}

          {dev.function_vi ? (
            <section className="ze-info-sec">
              <h3 className="ze-h3">{T.info.function}</h3>
              <p>{withMark('function', 0, dev.function_vi, loc.func(dev) ?? dev.function_vi, T.prov.lineFunction)}</p>
            </section>
          ) : (
            dev.synthetic && <p className="ze-muted">{T.info.synthetic}</p>
          )}

          {!!dev.details_vi?.length && (
            <section className="ze-info-sec">
              <h3 className="ze-h3">{T.info.details}</h3>
              <ul className="ze-list">
                {loc.details(dev)?.map((t, i, all) => (
                  <li key={i}>{withMark('details', i, dev.details_vi?.[i] ?? '', t, T.prov.lineDetail(i + 1, all.length))}</li>
                ))}
              </ul>
            </section>
          )}

          {!!dev.connects_to?.length && (
            <section className="ze-info-sec">
              <h3 className="ze-h3">{T.info.connects}</h3>
              <ul className="ze-list">
                {dev.connects_to.map((c, i) => {
                  const other = data.deviceById.get(c.part)
                  return (
                    <li key={i}>
                      {other ? (
                        // an inline link (not an inline-block button), so a long name wraps with the text and
                        // the list bullet stays on its first line (review M6)
                        <a
                          className="ze-link"
                          href={`#${other.device_id}`}
                          onClick={(e) => {
                            e.preventDefault()
                            pick(other.device_id)
                          }}
                        >
                          {loc.name(other)}
                        </a>
                      ) : (
                        <span>{T.info.otherTargets[c.part] ?? c.part.replace(/_/g, ' ')}</span>
                      )}
                      {c.interface_vi && <span className="ze-muted"> – {loc.iface(dev, i)}</span>}
                    </li>
                  )
                })}
              </ul>
            </section>
          )}

          {dev.size_mm && (
            <section className="ze-info-sec">
              <h3 className="ze-h3">{T.info.size}</h3>
              <p>
                <span className="ze-muted">{T.info.sizeAxes}: </span>
                {dev.size_mm.map(fmtInt).join(' × ')}
              </p>
            </section>
          )}
        </>
      )}
      <p className="ze-hint">{T.info.hint}</p>
      {open && prov && dev && open.device === dev.device_id && (
        <ProvDialog prov={prov} open={open} device={loc.name(dev)} loc={loc} onClose={closeDialog} />
      )}
    </aside>
  )
}
