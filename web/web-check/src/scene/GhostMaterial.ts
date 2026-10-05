import * as THREE from 'three'

// r3f-snippets §10: fresnel ghost (vent domes in CUT_Z_BARREL)
export function makeGhostMaterial(color = '#B4D6F5', face = 0.1, edge = 0.75) {
  const m = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    uniforms: { uColor: { value: new THREE.Color(color) }, uFace: { value: face }, uEdge: { value: edge } },
    vertexShader: /* glsl */ `
      varying vec3 vN; varying vec3 vV;
      void main() { vec4 mv = modelViewMatrix * vec4(position, 1.0);
        vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uColor; uniform float uFace, uEdge; varying vec3 vN; varying vec3 vV;
      void main() { float f = 1.0 - abs(dot(normalize(vN), normalize(vV)));
        gl_FragColor = vec4(uColor, mix(uFace, uEdge, f * f));
        #include <colorspace_fragment>
      }`,
  })
  m.name = 'za_ghost_vent'
  m.userData.zeGhost = true
  return m
}

let shared: THREE.ShaderMaterial | null = null
export function ghostMaterial() {
  return (shared ??= makeGhostMaterial())
}
