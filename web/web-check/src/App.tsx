import * as THREE from 'three'
import { Component, Suspense, use, useEffect, useState, type ReactNode } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Environment, Lightformer } from '@react-three/drei'
import { dataPromise } from './data'
import { useUi } from './store'
import { reg } from './scene/rig'
import { InteriorLoader, LineModel } from './scene/Models'
import { CameraRig } from './scene/CameraRig'
import { Selection } from './scene/Selection'
import { Rotors } from './scene/Rotors'
import { Ground } from './scene/Ground'
import { r3f } from './scene/precompile'
import { frameCounter, installHooks, ready, signalReady } from './test/hooks'
import { Toolbar } from './ui/Toolbar'
import { DeviceTree } from './ui/DeviceTree'
import { InfoPanel } from './ui/InfoPanel'

const params = new URLSearchParams(location.search)
const selfcheck = params.has('selfcheck')
/** review I4 (user: "Bỏ cái bảng trắng này luôn đi nhé"): the selfcheck text stays in the DOM for the tests
 * but is visually hidden; `?selfcheck=show` shows the old panel */
const selfcheckShown = params.get('selfcheck') === 'show'

/** a crashing overlay panel must not take the 3D view down with it */
class UiBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  componentDidCatch(e: unknown) {
    console.error('[ui] overlay panel crashed', e)
  }
  render() {
    return this.state.failed ? null : this.props.children
  }
}

/** frame counter, ready signal, R3F state getter for precompile, window.__ze */
function Bridge() {
  const get = useThree((s) => s.get)
  useEffect(() => {
    r3f.get = get
    installHooks(get)
  }, [get])
  useFrame(() => {
    frameCounter.n++
    if (reg.lineScene && reg.stats.line_first_frame_ms === null) {
      reg.stats.line_first_frame_ms = performance.now() // this frame renders the rigged line
      requestAnimationFrame(() => {
        useUi.setState({ ready: true })
        signalReady()
      })
    }
  })
  return null
}

function Lights() {
  return (
    <>
      <Environment resolution={256} frames={1}>
        {/* grey world (like the Eevee look renders): fully metallic surfaces inside the hollows would
            otherwise reflect black between the light formers */}
        <color attach="background" args={['#8d959c']} />
        <Lightformer form="rect" intensity={2.5} position={[3, 10, 0]} rotation-x={Math.PI / 2} scale={[24, 8, 1]} />
        <Lightformer form="rect" intensity={1.2} position={[3, 3, -10]} scale={[24, 4, 1]} />
        <Lightformer form="rect" intensity={0.8} position={[3, 3, 10]} rotation-y={Math.PI} scale={[24, 4, 1]} />
      </Environment>
      <ambientLight intensity={0.25} />
      <directionalLight position={[5, 12, -6]} intensity={1.2} />
    </>
  )
}

function useKeys() {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)) return
      const ui = useUi.getState()
      if (e.key === 'f' || e.key === 'F') ui.zoomTo(ui.selected)
      else if (e.key === 'Escape') ui.clear()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])
}

function SelfcheckOut() {
  const [text, setText] = useState<string | null>(null)
  useEffect(() => {
    let alive = true
    void ready.then(async () => {
      await new Promise((r) => requestAnimationFrame(r))
      const ze = (window as unknown as { __ze: { selfcheck(): unknown } }).__ze
      if (alive) setText(JSON.stringify(ze.selfcheck(), null, 1) + '\nSELFCHECK DONE')
    })
    return () => {
      alive = false
    }
  }, [])
  return text ? (
    <pre id="selfcheck" className={selfcheckShown ? 'ze-selfcheck-shown' : undefined}>
      {text}
    </pre>
  ) : null
}

function InitFree() {
  const data = use(dataPromise)
  useEffect(() => {
    const F = data.states.FREE
    useUi.setState({ free: { axis: F.axis_default, offset: F.offset_default_m[F.axis_default], flip: false } })
  }, [data])
  return null
}

export default function App() {
  const interiorWanted = useUi((s) => s.interiorWanted)
  useKeys()
  return (
    <div className="ze-app">
      <Canvas
        className="ze-canvas"
        camera={{ position: [2.5, 5, -10], fov: 35, near: 0.02, far: 200 }}
        gl={{ antialias: true, localClippingEnabled: true, toneMapping: THREE.NeutralToneMapping }}
        dpr={selfcheck ? 1 : [1, 2]}
        onPointerMissed={() => useUi.getState().clear()}
      >
        <color attach="background" args={['#e9ecef']} />
        <Lights />
        <Ground />
        <Suspense fallback={null}>
          <LineModel />
          <CameraRig />
          <InitFree />
        </Suspense>
        <Suspense fallback={null}>{interiorWanted && <InteriorLoader />}</Suspense>
        <Selection />
        <Rotors />
        <Bridge />
      </Canvas>
      <UiBoundary>
        <Suspense fallback={null}>
          <Toolbar />
          <DeviceTree />
          <InfoPanel />
        </Suspense>
      </UiBoundary>
      {selfcheck && <SelfcheckOut />}
    </div>
  )
}
