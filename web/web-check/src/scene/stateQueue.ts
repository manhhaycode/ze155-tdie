import { useUi } from '../store'

// AMENDMENTS I2: ONE serial queue for every cut-state change: user clicks, camera presets, the interior
// load (awaited inside a job) and the shader precompile pass. A job never interleaves with another one;
// a click during precompile simply waits its turn. `busy` is true while any job is queued or running.

let tail: Promise<void> = Promise.resolve()
let depth = 0
let running: string | null = null

export function enqueue<T>(label: string, job: () => Promise<T>): Promise<T> {
  depth++
  if (!useUi.getState().busy) useUi.setState({ busy: true })
  const run = tail.then(async () => {
    running = label
    try {
      return await job()
    } finally {
      running = null
    }
  })
  tail = run.then(
    () => {},
    (e: unknown) => {
      console.error(`[state queue] job "${label}" failed`, e)
    },
  ).finally(() => {
    depth--
    if (depth === 0) useUi.setState({ busy: false })
  })
  return run
}

export const queueIdle = () => depth === 0
export const queueRunning = () => running
/** resolves when every job queued so far has finished */
export const queueDrained = () => tail
