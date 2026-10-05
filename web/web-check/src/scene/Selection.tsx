import * as THREE from 'three'
import { useEffect, useLayoutEffect, useMemo } from 'react'
import { createPortal } from '@react-three/fiber'
import { Outlines } from '@react-three/drei'
import { reg } from './rig'
import { noRaycast } from './Picking'
import { useUi } from '../store'

// PLAN-DOT1 §4.2.7 = r3f-snippets §4: drei Outlines with screenspace={false} (pixel thickness), hull meshes
// marked as helpers and never raycast; clipping planes copied from the part material (incl. freePlane).
export const HOVER_COLOR = '#9fd3ff'
export const SELECT_COLOR = '#ff8a1f'

function markHelpers(mesh: THREE.Object3D) {
  for (const c of mesh.children)
    c.traverse((o) => {
      o.userData.__helper = true
      o.raycast = noRaycast
    })
}

function MeshOutline({ mesh, color, px, angle }: { mesh: THREE.Mesh; color: string; px: number; angle: number }) {
  const planes = ((mesh.material as THREE.Material).clippingPlanes ?? []) as THREE.Plane[]
  // Outlines adds its group + hull in its own layout effects, which run before this parent's
  useLayoutEffect(() => markHelpers(mesh))
  return createPortal(
    <Outlines screenspace={false} thickness={px} color={color} angle={angle} clippingPlanes={planes} toneMapped={false} />,
    mesh,
  )
}

/** current selection lists (shared with the test hooks) */
export const selectionInfo = {
  outlineMeshes: 0,
  bbox: null as null | { min: number[]; max: number[]; dashed: boolean },
}

function makeBox(box: THREE.Box3, dashed: boolean) {
  let obj: THREE.LineSegments
  if (!dashed) {
    obj = new THREE.Box3Helper(box, new THREE.Color(SELECT_COLOR))
  } else {
    const g = new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1))
    const size = box.getSize(new THREE.Vector3())
    const center = box.getCenter(new THREE.Vector3())
    g.scale(size.x, size.y, size.z)
    g.translate(center.x, center.y, center.z)
    obj = new THREE.LineSegments(g, new THREE.LineDashedMaterial({ color: SELECT_COLOR, dashSize: 0.04, gapSize: 0.03 }))
    obj.computeLineDistances()
  }
  const m = obj.material as THREE.LineBasicMaterial
  m.depthTest = false
  m.transparent = true
  m.opacity = 0.9
  m.toneMapped = false
  obj.renderOrder = 999
  obj.userData.__helper = true
  obj.raycast = noRaycast
  return obj
}

export function Selection() {
  const hovered = useUi((s) => s.hovered)
  const selected = useUi((s) => s.selected)
  const selectedPart = useUi((s) => s.selectedPart)
  const ver = useUi((s) => s.cutVersion)
  const busy = useUi((s) => s.busy)

  const selMeshes = useMemo(() => {
    void ver
    if (!selected) return []
    return selectedPart ? reg.meshesOfPart(selectedPart) : reg.meshesOfDevice(selected)
  }, [selected, selectedPart, ver])

  const hovMeshes = useMemo(() => {
    void ver
    return hovered && hovered !== selected ? reg.meshesOfDevice(hovered) : []
  }, [hovered, selected, ver])

  const box = useMemo(() => {
    void ver
    if (!selected) return null
    const vis = selectedPart ? reg.meshesOfPart(selectedPart) : reg.meshesOfDevice(selected)
    const dashed = vis.length === 0
    const b = dashed
      ? selectedPart
        ? reg.boxOfPart(selectedPart)
        : reg.boxOfDevice(selected, false)
      : reg.boxOfMeshes(vis)
    if (b.isEmpty()) return null
    return { obj: makeBox(b, dashed), b, dashed }
  }, [selected, selectedPart, ver])

  useEffect(() => {
    selectionInfo.outlineMeshes = selMeshes.length
    selectionInfo.bbox = box ? { min: box.b.min.toArray(), max: box.b.max.toArray(), dashed: box.dashed } : null
    return () => {
      if (box) {
        box.obj.geometry.dispose()
        ;(box.obj.material as THREE.Material).dispose()
      }
    }
  }, [selMeshes, box])

  // while the queue is busy (state change / precompile) the mesh lists are stale: draw nothing
  if (busy) return null
  return (
    <>
      {hovMeshes.map((m) => (
        <MeshOutline key={`h${m.uuid}`} mesh={m} color={HOVER_COLOR} px={2} angle={0} />
      ))}
      {selMeshes.map((m) => (
        <MeshOutline key={`s${m.uuid}`} mesh={m} color={SELECT_COLOR} px={3} angle={Math.PI} />
      ))}
      {box && <primitive object={box.obj} />}
    </>
  )
}
