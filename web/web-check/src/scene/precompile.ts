import type { RootState } from '@react-three/fiber'
import { FIXED_STATE_IDS } from '../data'
import { reg } from './rig'
import { applyState } from './Cuts'
import { enterFree } from './FreeClip'
import { enterFlowLayer } from './Flow'
import { enqueue } from './stateQueue'
import { useUi } from '../store'

// AMENDMENTS I2 / small decisions: a simple precompile, once, right after the interior loads, INSIDE the
// state queue. Frames are paused while it runs (otherwise the intermediate states would flash on screen
// and the next render would compile synchronously anyway); then the user's current state is re-applied.

export const r3f: { get: (() => RootState) | null } = { get: null }
export const precompileStats = { ran: false, ms: 0, programs_before: 0, programs_after: 0 }

export function enqueuePrecompile(): Promise<void> {
  return enqueue('precompile', async () => {
    const get = r3f.get
    if (!get) return
    const { gl, scene, camera, setFrameloop } = get()
    const t0 = performance.now()
    precompileStats.programs_before = gl.info.programs?.length ?? 0
    const loop = get().frameloop
    setFrameloop('never')
    try {
      for (const id of FIXED_STATE_IDS) {
        if (id === 'FULL') continue
        await applyState(id, { camera: false })
        if (id === 'FLOW') enterFlowLayer() // fill, sheet and pellet programs (PLAN-FLOW §5)
        await gl.compileAsync(scene, camera)
      }
      const f = useUi.getState().free
      await enterFree(f.axis, f.offset, f.flip)
      await gl.compileAsync(scene, camera)
    } finally {
      // re-apply the state the user is in now (AMENDMENTS I2)
      const s = useUi.getState()
      if (s.state === 'FREE') await enterFree(s.free.axis, s.free.offset, s.free.flip)
      else {
        await applyState(s.state, { camera: false })
        if (s.state === 'FLOW') enterFlowLayer()
      }
      setFrameloop(loop === 'never' ? 'always' : loop)
      precompileStats.ran = true
      precompileStats.ms = performance.now() - t0
      precompileStats.programs_after = gl.info.programs?.length ?? 0
      void reg
    }
  })
}
