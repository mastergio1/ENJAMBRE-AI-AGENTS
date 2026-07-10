// El Enjambre — Etapa 3: el enjambre 3D con datos falsos.
// Un solo loop, tres draw calls, gobernador de fps para móvil.

import * as THREE from 'three'
import { Enjambre } from './swarm/enjambre.js'
import { MotorRemoto } from './ui/conexion.js'
import { crearPanel, dibujarGraficoEstatico } from './ui/panel.js'

const canvas = document.getElementById('escena')
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' })
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.setSize(window.innerWidth, window.innerHeight)

const escena = new THREE.Scene()
escena.background = new THREE.Color('#0b0e14')
escena.fog = new THREE.FogExp2('#0b0e14', 0.022)

const camara = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 120)
camara.position.set(0, 7, 30)
camara.lookAt(0, 0, 0)

const enjambre = new Enjambre(7)
escena.add(enjambre.grupo)

// ---------- interacción ----------

const reducirMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches

// el motor real (WebSocket): configurable por entorno; en localhost se
// asume el uvicorn de desarrollo; si no responde, demo local en el navegador
const urlMotor =
  import.meta.env.VITE_WS_URL ||
  (['localhost', '127.0.0.1'].includes(location.hostname) ? 'ws://localhost:8000/ws' : null)
let motor = urlMotor ? new MotorRemoto(urlMotor) : null
let modo = 'demo local'

async function soltarTitular(titular) {
  if (reducirMovimiento) {
    correrEstatico(titular)
    return
  }
  if (motor) {
    try {
      await motor.simular(titular, {
        alInicio: (mensaje) => enjambre.fijarLideresRemotos(mensaje.lideres),
        alTick: (precio, _tick, sentimientos) => enjambre.aplicarEstadoRemoto(precio, sentimientos),
        alFin: (reporte) => panel.mostrarReporte(reporte),
      })
      enjambre.modoRemoto = true
      modo = 'motor real'
      return
    } catch {
      motor = null // el motor no está: de aquí en adelante, demo local
    }
  }
  enjambre.modoRemoto = false
  modo = 'demo local'
  enjambre.aplicarTitular(titular, reloj.getElapsedTime())
}

const panel = crearPanel(soltarTitular)

// parallax sutil con el puntero (vectores reutilizados, nada nuevo por frame)
const punteroMeta = new THREE.Vector2()
const rayo = new THREE.Raycaster()
const punteroNDC = new THREE.Vector2()
let ultimoRaycast = 0

window.addEventListener('pointermove', (evento) => {
  punteroMeta.set(
    (evento.clientX / window.innerWidth) * 2 - 1,
    (evento.clientY / window.innerHeight) * 2 - 1,
  )
  // hover sobre líderes: raycast acotado (cada 80 ms, solo contra los halos)
  const ahora = performance.now()
  if (ahora - ultimoRaycast < 80) return
  ultimoRaycast = ahora
  punteroNDC.set(punteroMeta.x, -punteroMeta.y)
  rayo.setFromCamera(punteroNDC, camara)
  const impactos = rayo.intersectObject(enjambre.mallaHalos)
  if (impactos.length > 0) {
    const lider = enjambre.lideres[impactos[0].instanceId]
    panel.mostrarTooltip(lider, evento.clientX, evento.clientY)
    canvas.style.cursor = 'pointer'
  } else {
    panel.ocultarTooltip()
    canvas.style.cursor = 'default'
  }
})

window.addEventListener('resize', () => {
  camara.aspect = window.innerWidth / window.innerHeight
  camara.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})

// ---------- gobernador de fps: bajo 45 recorta partículas ----------

let fpsSuavizado = 60
let proporcion = 1
let ultimoAjuste = 0

function gobernarFps(dt, t) {
  fpsSuavizado += (1 / Math.max(dt, 1e-4) - fpsSuavizado) * 0.05
  if (t - ultimoAjuste < 1.5) return
  if (fpsSuavizado < 45 && proporcion > 0.3) {
    proporcion = Math.max(0.3, proporcion - 0.15)
    enjambre.fijarProporcion(proporcion)
    ultimoAjuste = t
  } else if (fpsSuavizado > 57 && proporcion < 1) {
    proporcion = Math.min(1, proporcion + 0.1)
    enjambre.fijarProporcion(proporcion)
    ultimoAjuste = t
  }
}

// ---------- loop principal ----------

const reloj = new THREE.Clock()
let ultimoHud = 0

function cuadro() {
  const dt = Math.min(reloj.getDelta(), 0.05)
  const t = reloj.getElapsedTime()

  enjambre.actualizar(t, dt)
  camara.position.x += (punteroMeta.x * 2.5 - camara.position.x) * 0.03
  camara.position.y += (7 - punteroMeta.y * 2 - camara.position.y) * 0.03
  camara.lookAt(0, 0, 0)
  gobernarFps(dt, t)

  if (t - ultimoHud > 0.25) {
    ultimoHud = t
    panel.actualizarHUD(enjambre.precio, fpsSuavizado, enjambre.malla.count + enjambre.lideres.length, modo)
    panel.dibujarSparkline(enjambre.seriePrecio)
  }
  renderer.render(escena, camara)
}

// ---------- modo estático (prefers-reduced-motion) ----------

function correrEstatico(titular) {
  // simula 25 segundos "fuera de línea" y muestra una sola imagen + gráfico
  if (titular) enjambre.aplicarTitular(titular, 0)
  let t = 0
  const paso = 1 / 30
  for (let i = 0; i < 25 * 30; i++) {
    t += paso
    enjambre.actualizar(t, paso)
  }
  renderer.render(escena, camara)
  panel.actualizarHUD(enjambre.precio, 0, enjambre.malla.count + enjambre.lideres.length)
  dibujarGraficoEstatico(enjambre.seriePrecio)
  document.getElementById('aviso-estatico').hidden = false
}

if (reducirMovimiento) {
  correrEstatico(null)
} else {
  renderer.setAnimationLoop(cuadro)
}
