// El Enjambre — punto de entrada del frontend.
// Etapa 0: escena mínima que confirma que Three.js y GSAP funcionan.
// El enjambre de partículas real (instanced) llega en la Etapa 3.

import * as THREE from 'three'
import gsap from 'gsap'

const canvas = document.getElementById('escena')
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
// Regla de performance: pixelRatio limitado a 2 (CLAUDE.md sección 2.6)
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.setSize(window.innerWidth, window.innerHeight)

const escena = new THREE.Scene()
escena.background = new THREE.Color('#0b0e14')

const camara = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  100,
)
camara.position.z = 8

// Nube de puntos de prueba: una sola geometría y un solo material,
// nunca objetos nuevos dentro del loop (regla de performance).
const CANTIDAD = 500
const posiciones = new Float32Array(CANTIDAD * 3)
for (let i = 0; i < CANTIDAD * 3; i++) {
  posiciones[i] = (Math.random() - 0.5) * 10
}
const geometria = new THREE.BufferGeometry()
geometria.setAttribute('position', new THREE.BufferAttribute(posiciones, 3))
const material = new THREE.PointsMaterial({ color: '#c9a227', size: 0.04 })
const puntos = new THREE.Points(geometria, material)
escena.add(puntos)

// Respetar prefers-reduced-motion (CLAUDE.md sección 8)
const reducirMovimiento = window.matchMedia(
  '(prefers-reduced-motion: reduce)',
).matches

if (!reducirMovimiento) {
  gsap.to(puntos.rotation, { y: Math.PI * 2, duration: 60, repeat: -1, ease: 'none' })
}

window.addEventListener('resize', () => {
  camara.aspect = window.innerWidth / window.innerHeight
  camara.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})

renderer.setAnimationLoop(() => {
  renderer.render(escena, camara)
})
