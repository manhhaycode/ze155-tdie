import { use, useLayoutEffect } from 'react'
import { useThree } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import { dataPromise } from '../data'
import { rigInterior, rigLine } from './rig'
import { onClick, onDoubleClick, onPointerMove, onPointerOut } from './Picking'
import { enqueuePrecompile } from './precompile'
import { useUi } from '../store'

// PLAN-DOT1 §4.2.2. useGLTF(path, useDraco = false, useMeshopt = true): no Draco, inline meshopt decoder.
export const LINE_URL = '/models/line.glb'
export const INTERIOR_URL = '/models/interior.glb'
useGLTF.preload(LINE_URL, false, true) // line only: interior.glb is never prefetched (D12)

export function LineModel() {
  const data = use(dataPromise)
  const { scene } = useGLTF(LINE_URL, false, true)
  const gl = useThree((s) => s.gl)
  useLayoutEffect(() => {
    rigLine(scene, data, gl) // idempotent (scene.userData.zeRigged)
  }, [scene, data, gl])
  return (
    <primitive
      object={scene}
      onPointerMove={onPointerMove}
      onPointerOut={onPointerOut}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
    />
  )
}

/** Mounted only once store.interiorWanted is true. Rigs the interior into the line tree, renders nothing. */
export function InteriorLoader() {
  const data = use(dataPromise)
  const { scene } = useGLTF(INTERIOR_URL, false, true)
  const gl = useThree((s) => s.gl)
  useLayoutEffect(() => {
    if (rigInterior(scene, data, gl)) {
      useUi.getState().setInteriorLoaded(true)
      void enqueuePrecompile()
    }
  }, [scene, data, gl])
  return null
}
