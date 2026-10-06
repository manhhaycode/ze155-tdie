// Lazy loader of /data/prov/<device_id>.json (web/PLAN-PROV.md): fetched on the first selection of a device, never
// at start; images load only in the open dialog. A missing or broken file means no badges, never a broken panel.
import { useEffect, useState } from 'react'
import type { ProvDevice } from './provModel'

const cache = new Map<string, Promise<ProvDevice | null>>()

export function loadProv(id: string): Promise<ProvDevice | null> {
  let p = cache.get(id)
  if (!p) {
    const url = `/data/prov/${encodeURIComponent(id)}.json`
    p = fetch(url)
      .then(async (r) => {
        // the Vite dev server answers a missing file with index.html (200, text/html)
        const type = r.headers.get('content-type') ?? ''
        if (!r.ok || !type.includes('json')) throw new Error(`HTTP ${r.status} ${type}`)
        const d = (await r.json()) as ProvDevice
        if (d?.device_id !== id || !Array.isArray(d.lines)) throw new Error('not the file of this device')
        return d
      })
      .catch((e: unknown) => {
        console.warn(`[prov] ${url} not loaded, no source badges`, e)
        cache.delete(id) // tried again on the next selection
        return null
      })
    cache.set(id, p)
  }
  return p
}

/** undefined while loading, null when there is nothing to show; keyed by id, so a slow answer for the previous
 *  device never shows on the next one */
export function useProv(id: string | undefined): ProvDevice | null | undefined {
  const [got, setGot] = useState<{ id: string; data: ProvDevice | null } | null>(null)
  useEffect(() => {
    if (!id) return
    let alive = true
    void loadProv(id).then((data) => {
      if (alive) setGot({ id, data })
    })
    return () => {
      alive = false
    }
  }, [id])
  if (!id) return null
  return got?.id === id ? got.data : undefined
}
