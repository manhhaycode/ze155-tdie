// Info panel (right): texts of the selected device (PLAN-DOT1 §4.2.10).
import { use } from 'react'
import { dataPromise } from '../data'
import { reg, useUi } from './bind'
import { useLoc } from './i18n'
import { fmtInt } from './text'
import './ui.css'

/** true when the device has no visible mesh in the current state (e.g. `screws` at FULL) */
function isHiddenInside(id: string): boolean {
  if (reg.devices.size === 0 || !reg.devices.has(id)) return false
  return reg.meshesOfDevice(id, true).length === 0
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
          {part && <p className="ze-info-part">{T.info.part(part)}</p>}
          {isHiddenInside(dev.device_id) && <p className="ze-info-inside">{T.info.inside}</p>}

          {dev.function_vi ? (
            <section className="ze-info-sec">
              <h3 className="ze-h3">{T.info.function}</h3>
              <p>{loc.func(dev)}</p>
            </section>
          ) : (
            dev.synthetic && <p className="ze-muted">{T.info.synthetic}</p>
          )}

          {!!dev.details_vi?.length && (
            <section className="ze-info-sec">
              <h3 className="ze-h3">{T.info.details}</h3>
              <ul className="ze-list">
                {loc.details(dev)?.map((t, i) => <li key={i}>{t}</li>)}
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
    </aside>
  )
}
