// Toolbar (top): customer logo, cut states, FREE plane controls with the cap legend, rotor mode, camera preset,
// language switch (PLAN-DOT1 §4.2.10).
import { use, useLayoutEffect, useRef } from 'react'
import { dataPromise, STATE_IDS, type Axis } from '../data'
import { useUi } from './bind'
import { LANGS, useLang, useLoc } from './i18n'
import './ui.css'

// FREE axes in Blender names, like the state buttons ("Y = 0" vertical along the line, "Z = 1 200" height).
// The store and the hooks keep three axes: Blender X = three x, Blender Y = three −z, Blender Z = three y
// (review I3). `sign` turns the three offset into the Blender coordinate shown on the slider and readout.
const AXES: { ui: 'X' | 'Y' | 'Z'; three: Axis; sign: 1 | -1 }[] = [
  { ui: 'X', three: 'x', sign: 1 },
  { ui: 'Y', three: 'z', sign: -1 },
  { ui: 'Z', three: 'y', sign: 1 },
]
const CAP_ORDER = ['steel', 'screw', 'rubber', 'insulation', 'melt']
const STEP_M = 0.005

export function Toolbar() {
  const data = use(dataPromise)
  const state = useUi((s) => s.state)
  const free = useUi((s) => s.free)
  const rotorMode = useUi((s) => s.rotorMode)
  const busy = useUi((s) => s.busy)
  const interiorWanted = useUi((s) => s.interiorWanted)
  const interiorLoaded = useUi((s) => s.interiorLoaded)
  const setStateId = useUi((s) => s.setStateId)
  const setFree = useUi((s) => s.setFree)
  const setRotorMode = useUi((s) => s.setRotorMode)
  const resetView = useUi((s) => s.resetView)
  const pending = useUi((s) => s.pending)
  const loc = useLoc()
  const { T } = loc
  const setLang = useLang((s) => s.setLang)

  // publish the toolbar height so the side panels start below it (the FREE row makes it taller)
  const ref = useRef<HTMLElement>(null)
  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    const put = () => document.documentElement.style.setProperty('--ze-top', `${Math.ceil(el.getBoundingClientRect().height)}px`)
    put()
    const ro = new ResizeObserver(put)
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  const F = data.states.FREE
  const screw = data.rotors.find((r) => r.id === 'screw_a') ?? data.rotors[0]
  const slow = screw?.display_slow ?? 20
  const rpm = Math.abs(screw?.rpm ?? 0)
  const ax = AXES.find((a) => a.three === free.axis) ?? AXES[0]
  const [lo3, hi3] = F.slider_range_m[free.axis]
  const [lo, hi] = ax.sign > 0 ? [lo3, hi3] : [-hi3, -lo3] // slider in the Blender coordinate
  const shown = ax.sign * free.offset + 0 // + 0: no "−0"
  const loading = interiorWanted && !interiorLoaded

  return (
    <header ref={ref} className="ze-panel ze-toolbar">
      <div className="ze-row">
        <img className="ze-brand" src="/brand/toyobo-official.svg" alt={T.brand} width={133} height={51} draggable={false} />
        <span className="ze-sep" />
        <div className="ze-group" role="group" aria-label={T.toolbar.states}>
          {STATE_IDS.map((id) => (
            <button
              key={id}
              type="button"
              className="ze-btn"
              data-state={id}
              aria-pressed={state === id}
              data-pending={pending === id || undefined}
              onClick={() => void setStateId(id)}
            >
              {loc.state(id, data.states[id])}
            </button>
          ))}
        </div>
        <span className="ze-sep" />
        <div className="ze-group" role="group" aria-label={T.toolbar.rotor}>
          <span className="ze-label">{T.toolbar.rotor}:</span>
          {(['off', 'slow', 'real'] as const).map((m) => (
            <button key={m} type="button" className="ze-btn" data-rotor={m} aria-pressed={rotorMode === m} onClick={() => setRotorMode(m)}>
              {m === 'off' ? T.toolbar.rotorOff : m === 'slow' ? T.toolbar.rotorSlow(slow) : T.toolbar.rotorReal}
            </button>
          ))}
          <span className="ze-badge">{T.toolbar.rotorBadge(rpm, rotorMode, slow)}</span>
        </div>
        <span className="ze-sep" />
        <button type="button" className="ze-btn" data-action="reset-view" onClick={() => resetView()}>
          {T.toolbar.resetView}
        </button>
        <div className="ze-end">
          {(loading || busy) && (
            <span className="ze-busy" role="status">
              <span className="ze-spinner" aria-hidden="true" />
              {loading ? T.toolbar.loadingInterior : T.toolbar.busy}
            </span>
          )}
          <div className="ze-group ze-lang" role="group" aria-label={T.lang}>
            {LANGS.map((l) => (
              <button
                key={l.id}
                type="button"
                className="ze-btn ze-btn-sm"
                data-lang={l.id}
                lang={l.id}
                title={l.label}
                aria-pressed={loc.lang === l.id}
                onClick={() => setLang(l.id)}
              >
                {l.short}
              </button>
            ))}
          </div>
        </div>
      </div>

      {state !== 'FULL' && (
        <div className="ze-row">
          {state === 'FREE' && (
            <>
              <div className="ze-group" role="group" aria-label={T.toolbar.freeAxis}>
                <span className="ze-label">{T.toolbar.freeAxis}:</span>
                {AXES.map((a) => (
                  <button
                    key={a.ui}
                    type="button"
                    className="ze-btn ze-btn-sm"
                    data-axis={a.three}
                    data-axis-blender={a.ui}
                    aria-pressed={free.axis === a.three}
                    title={T.toolbar.axisHint[a.ui]}
                    onClick={() => free.axis !== a.three && setFree({ axis: a.three, offset: F.offset_default_m[a.three] })}
                  >
                    {a.ui}
                  </button>
                ))}
              </div>
              <label className="ze-group ze-slider">
                <span className="ze-label">{T.toolbar.freeOffset}:</span>
                <input
                  id="ze-free-offset"
                  type="range"
                  min={lo}
                  max={hi}
                  step={STEP_M}
                  value={shown}
                  onChange={(e) => setFree({ offset: ax.sign * Number(e.target.value) + 0 })}
                />
                <output className="ze-mono">{T.toolbar.freeValue(ax.ui, shown * 1000)}</output>
              </label>
              <label className="ze-group ze-check" title={T.toolbar.freeKeep(ax.ui, free.flip, shown * 1000)}>
                <input type="checkbox" checked={free.flip} onChange={(e) => setFree({ flip: e.target.checked })} />
                <span>{T.toolbar.freeFlip}</span>
              </label>
              <span className="ze-sep" />
            </>
          )}
          <div className="ze-group ze-legend" role="group" aria-label={T.toolbar.capLegend}>
            <span className="ze-label">{T.toolbar.capLegend}:</span>
            {CAP_ORDER.filter((k) => data.materials.cap_colors[k]).map((k) => (
              <span key={k} className="ze-legend-item">
                <span
                  className={`ze-swatch${k === 'steel' ? ' ze-swatch-hatch' : ''}`}
                  style={{ backgroundColor: data.materials.cap_colors[k] ?? undefined }}
                  aria-hidden="true"
                />
                {T.caps[k] ?? k}
              </span>
            ))}
          </div>
        </div>
      )}
    </header>
  )
}
