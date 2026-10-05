import * as THREE from 'three'
import { useMemo } from 'react'
import { noRaycast } from './Picking'

// Floor helper (not part of the line tree, never raycast, never clipped: no material clipping planes).
export function Ground() {
  const { plane, grid } = useMemo(() => {
    const plane = new THREE.Mesh(
      new THREE.PlaneGeometry(60, 40),
      new THREE.MeshStandardMaterial({ color: '#d9dde1', roughness: 0.95, metalness: 0 }),
    )
    plane.rotation.x = -Math.PI / 2
    plane.position.set(3.5, -0.012, 1)
    const grid = new THREE.GridHelper(60, 60, '#b9c0c7', '#c9ced4')
    grid.position.set(3.5, -0.01, 1)
    for (const o of [plane, grid]) {
      o.userData.__helper = true
      o.raycast = noRaycast
    }
    return { plane, grid }
  }, [])
  return (
    <>
      <primitive object={plane} />
      <primitive object={grid} />
    </>
  )
}
