// Device tree (left): 10 sections, devices sorted by name_vi, accent-insensitive search (PLAN-DOT1 §4.2.10).
import { use, useDeferredValue, useEffect, useMemo, useRef, useState, type KeyboardEvent } from 'react'
import { dataPromise, type DeviceRec } from '../data'
import { useUi } from './bind'
import { buildIndex, byNameVi, search } from './search'
import { T } from './text'
import './ui.css'

export function DeviceTree() {
  const data = use(dataPromise)
  const selected = useUi((s) => s.selected)
  const hovered = useUi((s) => s.hovered)
  const select = useUi((s) => s.select)
  const zoomTo = useUi((s) => s.zoomTo)
  const hover = useUi((s) => s.hover)

  const [query, setQuery] = useState('')
  const q = useDeferredValue(query)
  const [open, setOpen] = useState<Record<string, boolean>>({})
  // review M5: the panel folds to its header, so a narrow window keeps a usable canvas
  const [collapsed, setCollapsed] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)

  const index = useMemo(() => buildIndex(data.devices.devices), [data])
  const total = data.devices.devices.length
  const searching = q.trim().length > 0
  // matching devices per section: ranked while searching, alphabetical otherwise
  const bySection = useMemo(() => {
    const hits = searching ? search(index, q) : [...data.devices.devices].sort(byNameVi)
    const m = new Map<string, DeviceRec[]>()
    for (const s of data.devices.sections) m.set(s.group, [])
    for (const d of hits) m.get(d.group)?.push(d)
    return { m, count: hits.length, first: hits[0] as DeviceRec | undefined }
  }, [index, q, searching, data])

  const selectedGroup = selected ? data.deviceById.get(selected)?.group : undefined

  // a new selection (from the tree or the canvas) opens its section (state adjusted during render, no effect),
  // then the effect below scrolls it into view
  const [prevSelected, setPrevSelected] = useState(selected)
  if (selected !== prevSelected) {
    setPrevSelected(selected)
    if (selectedGroup && !open[selectedGroup]) setOpen({ ...open, [selectedGroup]: true })
  }
  useEffect(() => {
    if (!selected || !listRef.current) return
    const id = requestAnimationFrame(() => {
      const el = listRef.current?.querySelector<HTMLElement>(`[data-device="${CSS.escape(selected)}"]`)
      el?.scrollIntoView({ block: 'nearest' })
    })
    return () => cancelAnimationFrame(id)
  }, [selected, open, q])

  const pick = (id: string) => {
    select(id)
    zoomTo(id)
  }
  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      e.stopPropagation()
      setQuery('')
      e.currentTarget.blur()
    } else if (e.key === 'Enter' && bySection.first) {
      pick(bySection.first.device_id)
    }
  }

  return (
    <aside className="ze-panel ze-tree" aria-label={T.tree.title} data-collapsed={collapsed || undefined}>
      <div className="ze-tree-head">
        <h2 className="ze-h">{T.tree.title}</h2>
        <span className="ze-muted ze-tree-count">{T.tree.count(bySection.count, total)}</span>
        <button
          type="button"
          className="ze-btn ze-btn-sm ze-fold"
          aria-expanded={!collapsed}
          title={collapsed ? T.tree.expand : T.tree.collapse}
          aria-label={collapsed ? T.tree.expand : T.tree.collapse}
          onClick={() => setCollapsed((c) => !c)}
        >
          {collapsed ? '▼' : '▲'}
        </button>
      </div>
      {!collapsed && (
      <>
      <div className="ze-search">
        <input
          id="ze-search"
          type="search"
          value={query}
          placeholder={T.tree.search}
          aria-label={T.tree.searchLabel}
          autoComplete="off"
          spellCheck={false}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onKey}
        />
        {query && (
          <button type="button" className="ze-search-clear" title={T.tree.clear} aria-label={T.tree.clear} onClick={() => setQuery('')}>
            ×
          </button>
        )}
      </div>
      <div className="ze-tree-list" ref={listRef}>
        {bySection.count === 0 && <p className="ze-muted ze-pad">{T.tree.noResult}</p>}
        {data.devices.sections.map((sec) => {
          const devs = bySection.m.get(sec.group) ?? []
          if (searching && devs.length === 0) return null
          const isOpen = searching || !!open[sec.group]
          return (
            <section key={sec.group} className="ze-sec" aria-label={sec.name_vi}>
              <button
                type="button"
                className="ze-sec-head"
                aria-expanded={isOpen}
                onClick={() => setOpen((o) => ({ ...o, [sec.group]: !isOpen }))}
                disabled={searching}
              >
                <span className="ze-caret" aria-hidden="true">{isOpen ? '▾' : '▸'}</span>
                <span className="ze-sec-name">{sec.name_vi}</span>
                <span className="ze-muted">{devs.length}</span>
              </button>
              {isOpen && (
                <ul className="ze-sec-list">
                  {devs.map((d) => (
                    <li key={d.device_id}>
                      <button
                        type="button"
                        className="ze-tree-item"
                        data-device={d.device_id}
                        aria-current={d.device_id === selected ? 'true' : undefined}
                        data-hovered={d.device_id === hovered || undefined}
                        title={`${d.name_en} (${d.device_id})`}
                        onClick={() => pick(d.device_id)}
                        onMouseEnter={() => hover(d.device_id)}
                        onMouseLeave={() => hover(null)}
                      >
                        <span className="ze-item-name">{d.name_vi}</span>
                        {d.has_interior && <span className="ze-badge-int" role="img" title={T.tree.hasInterior} aria-label={T.tree.hasInterior}>◐</span>}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )
        })}
      </div>
      </>
      )}
    </aside>
  )
}
