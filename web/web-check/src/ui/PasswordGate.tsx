import { useState, type FormEvent, type ReactNode } from 'react'
import './gate.css'

// Password gate in front of the viewer. A static site has no server to check a password, so this only keeps
// casual visitors out: the models stay reachable by direct URL, and the check can be bypassed in the browser.
// Real protection needs a server-side check (e.g. Vercel middleware). The password itself is not in the source,
// only a salted SHA-256; unlocking lasts only until this page is reloaded.

const SALT = 'ze155-virtual-factory:'
const HASH = '2f1ec37f1201ea1af31ea4f402a9d1abfef5e6cc16bfcd6500179c31a315627d'

try {
  localStorage.removeItem('ze-unlock')
} catch {
  // Storage may be unavailable.
}

/** SHA-256 of a UTF-8 string, hex (pure JS: crypto.subtle is missing on plain-http LAN addresses) */
function sha256(text: string): string {
  const K: number[] = []
  const H: number[] = []
  const frac = (x: number) => ((x - Math.floor(x)) * 2 ** 32) >>> 0
  for (let n = 2, found = 0; found < 64; n++) {
    let prime = true
    for (let d = 2; d * d <= n; d++) if (n % d === 0) prime = false
    if (!prime) continue
    if (found < 8) H.push(frac(Math.sqrt(n)))
    K.push(frac(Math.cbrt(n)))
    found++
  }
  const bytes = [...new TextEncoder().encode(text)]
  const bits = bytes.length * 8
  bytes.push(0x80)
  while (bytes.length % 64 !== 56) bytes.push(0)
  for (let i = 7; i >= 0; i--) bytes.push(i >= 4 ? 0 : (bits >>> (i * 8)) & 0xff)
  const rotr = (x: number, n: number) => (x >>> n) | (x << (32 - n))
  const w = new Array<number>(64)
  for (let off = 0; off < bytes.length; off += 64) {
    for (let i = 0; i < 16; i++)
      w[i] = (bytes[off + 4 * i] << 24) | (bytes[off + 4 * i + 1] << 16) | (bytes[off + 4 * i + 2] << 8) | bytes[off + 4 * i + 3]
    for (let i = 16; i < 64; i++) {
      const s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3)
      const s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10)
      w[i] = (w[i - 16] + s0 + w[i - 7] + s1) | 0
    }
    let [a, b, c, d, e, f, g, h] = H
    for (let i = 0; i < 64; i++) {
      const t1 = (h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i]) | 0
      const t2 = ((rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) | 0
      h = g
      g = f
      f = e
      e = (d + t1) | 0
      d = c
      c = b
      b = a
      a = (t1 + t2) | 0
    }
    ;[a, b, c, d, e, f, g, h].forEach((v, i) => (H[i] = (H[i] + v) >>> 0))
  }
  return H.map((v) => v.toString(16).padStart(8, '0')).join('')
}

export function PasswordGate({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const [value, setValue] = useState('')
  const [wrong, setWrong] = useState(false)
  if (open) return <>{children}</>
  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (sha256(SALT + value) !== HASH) {
      setWrong(true)
      return
    }
    setOpen(true)
  }
  return (
    <div className="ze-gate">
      <form className="ze-gate-card" onSubmit={submit}>
        <label className="ze-gate-title" htmlFor="ze-gate-pw">
          Enter the password to open the virtual factory
        </label>
        <input
          id="ze-gate-pw"
          className="ze-gate-input"
          type="password"
          placeholder="Password"
          autoComplete="current-password"
          autoFocus
          value={value}
          aria-invalid={wrong}
          onChange={(e) => {
            setValue(e.target.value)
            setWrong(false)
          }}
        />
        {wrong && (
          <p className="ze-gate-error" role="alert">
            Wrong password
          </p>
        )}
        <button className="ze-gate-button" type="submit" disabled={!value}>
          Enter
        </button>
      </form>
    </div>
  )
}
