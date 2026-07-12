// El Enjambre — Etapa 3: el enjambre 3D con datos falsos.
// Un solo loop, tres draw calls, gobernador de fps para móvil.

import * as THREE from 'three'
import { abrirArchivo } from './archivo/archivo.js'
import { abrirDuelo } from './duelo/duelo.js'
import { ReproductorReplay, inicializarMuro } from './muro/muro.js'
import { Enjambre } from './swarm/enjambre.js'
import { MotorRemoto, urlApi } from './ui/conexion.js'
import { crearPanel, dibujarGraficoEstatico } from './ui/panel.js'

const canvas = document.getElementById('escena')
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' })
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.setSize(window.innerWidth, window.innerHeight)

const escena = new THREE.Scene()
escena.background = new THREE.Color('#1b1916')
escena.fog = new THREE.FogExp2('#1b1916', 0.022)

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

let muroCtl = { recargar: async () => {}, detenerReplay: () => {} }
let observatorio = null // el mando cuando el enjambre está "dejado corriendo"

async function soltarTitular(titular, titularId = null) {
  if (reducirMovimiento) {
    correrEstatico(titular)
    return
  }
  // si el observatorio está activo, la noticia se suelta ENCIMA (no reinicia)
  if (observatorio) {
    if (titular) observatorio.soltarNoticia(titular)
    return
  }
  muroCtl.detenerReplay() // la portada cede el escenario a la simulación en vivo
  if (motor) {
    try {
      await motor.simular(titular, {
        alInicio: (mensaje) => enjambre.fijarLideresRemotos(mensaje.lideres),
        alTick: (precio, _tick, sentimientos) => enjambre.aplicarEstadoRemoto(precio, sentimientos),
        alFin: (reporte) => {
          panel.mostrarReporte(reporte)
          muroCtl.recargar() // la tarjeta recién simulada pasa a Estado A
        },
        alLimite: (mensaje) => panel.avisar(mensaje),
      }, titularId ? { titular_id: titularId } : {})
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

// Modo observatorio: el enjambre sigue vivo y recibe noticias encima
async function alternarObservatorio(titular) {
  if (observatorio) {
    observatorio.detener()
    observatorio = null
    enjambre.modoRemoto = false
    modo = 'demo local'
    panel.fijarModoObservatorio(false)
    return
  }
  if (reducirMovimiento || !motor) {
    panel.avisar('El modo observatorio necesita el motor en vivo.')
    return
  }
  try {
    muroCtl.detenerReplay()
    observatorio = await motor.observatorio(titular, {
      alInicio: (m) => enjambre.fijarLideresRemotos(m.lideres),
      alTick: (precio, _t, sent) => enjambre.aplicarEstadoRemoto(precio, sent),
      alLimite: (m) => panel.avisar(m),
      alFin: () => {
        observatorio = null
        enjambre.modoRemoto = false
        panel.fijarModoObservatorio(false)
        panel.avisar('El observatorio descansó. Puedes reabrirlo cuando quieras.')
      },
    })
    enjambre.modoRemoto = true
    modo = 'observatorio'
    panel.fijarModoObservatorio(true)
  } catch {
    observatorio = null
    panel.avisar('No se pudo abrir el observatorio.')
  }
}

const panel = crearPanel(soltarTitular, alternarObservatorio)

// ---------- el archivo + enlaces compartibles (?sim=<id>) ----------

const reproductorArchivo = new ReproductorReplay(enjambre)

/** Abre una simulación guardada: replay + reporte con las 8 voces y epílogo. */
async function abrirSimulacion(id) {
  const api = urlApi()
  if (!api || !/^[0-9a-f]{16}$/.test(id)) return
  muroCtl.detenerReplay()
  reproductorArchivo.detener()
  try {
    const d = await (await fetch(`${api}/api/simulacion/${id}`)).json()
    enjambre.fijarLideresRemotos(d.lideres || [])
    panel.mostrarReporte(d.resumen, { voces: d.voces, epilogo: d.epilogo, titular: d.titular, id: d.id })
    history.replaceState({}, '', `?sim=${id}`)
    if (d.tiene_replay && !reducirMovimiento) {
      await reproductorArchivo.cargar(`${api}/api/simulacion/${id}/replay`)
      reproductorArchivo.reproducir({})
    }
  } catch {
    panel.avisar('No se pudo cargar esa simulación.')
  }
}

async function mostrarArchivo() {
  history.pushState({}, '', '/archivo')
  const control = await abrirArchivo({
    alAbrirSim: (id) => {
      control?.cerrar()          // la hemeroteca cede el paso al reporte
      abrirSimulacion(id)
    },
    alDuelo: (idA, idB) => {
      control?.cerrar()
      mostrarDuelo(idA, idB)
    },
    alCerrar: () => history.pushState({}, '', '/'),
  })
}

async function mostrarDuelo(idA, idB) {
  if (!/^[0-9a-f]{16}$/.test(idA) || !/^[0-9a-f]{16}$/.test(idB)) return
  muroCtl.detenerReplay()
  reproductorArchivo.detener()
  history.pushState({}, '', `/duelo/${idA}-vs-${idB}`)
  await abrirDuelo({
    idA, idB, reducirMovimiento,
    alCerrar: () => history.pushState({}, '', '/'),
  })
}

// el muro de noticias: la nueva portada (carga en paralelo, nunca bloquea)
inicializarMuro({
  enjambre,
  panel,
  correrTitular: soltarTitular,
  reducirMovimiento,
  fijarModo: (nuevo) => { modo = nuevo },
  abrirArchivo: mostrarArchivo,
})
  .then((control) => { muroCtl = control })
  .catch(() => {})

// enrutamiento inicial: enlace compartible, duelo o la hemeroteca
const paramsIniciales = new URLSearchParams(location.search)
const dueloRuta = location.pathname.match(/^\/duelo\/([0-9a-f]{16})-vs-([0-9a-f]{16})/)
if (paramsIniciales.get('sim')) {
  abrirSimulacion(paramsIniciales.get('sim'))
} else if (dueloRuta) {
  mostrarDuelo(dueloRuta[1], dueloRuta[2])
} else if (location.pathname.startsWith('/archivo')) {
  mostrarArchivo()
}

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
