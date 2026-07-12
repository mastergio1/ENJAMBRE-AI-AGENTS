// El Duelo de Escenarios (CONTENIDO.md sección 8).
// Dos titulares lado a lado, dos enjambres reaccionando en paralelo,
// sincronizados tick a tick, con sus curvas de precio superpuestas.
// Botón "exportar Reel": graba 12 s verticales (9:16) para redes.

import * as THREE from 'three'
import { Enjambre } from '../swarm/enjambre.js'
import { urlApi } from '../ui/conexion.js'

const TAMANO_FRAME = 8 + 5000
const COLOR_A = '#c9a227' // dorado
const COLOR_B = '#8fb8d8' // azul frío, para distinguir el segundo enjambre

const CARACTERES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => CARACTERES[c])

function framesDe(buffer) {
  const total = Math.floor(buffer.byteLength / TAMANO_FRAME)
  return {
    total,
    en(i) {
      const base = Math.min(i, total - 1) * TAMANO_FRAME
      return {
        precio: new DataView(buffer, base, 8).getFloat32(0, true),
        sent: new Int8Array(buffer, base + 8, 5000),
      }
    },
  }
}

/** Monta el duelo. Devuelve { cerrar }. */
export async function abrirDuelo({ idA, idB, reducirMovimiento, alCerrar }) {
  const api = urlApi()
  const capa = document.getElementById('duelo')
  capa.hidden = false
  document.body.classList.add('duelo-abierto')

  let anim = null
  let reloj = null
  let grabadora = null

  function cerrar() {
    if (anim) cancelAnimationFrame(anim)
    if (reloj) clearInterval(reloj)
    if (grabadora && grabadora.state === 'recording') grabadora.stop()
    capa.hidden = true
    capa.innerHTML = ''
    document.body.classList.remove('duelo-abierto')
    alCerrar?.()
  }

  let datos
  try {
    datos = await (await fetch(`${api}/api/duelo/${idA}/${idB}`)).json()
  } catch {
    capa.innerHTML = `<div class="duelo-panel"><p class="duelo-error">No se pudo cargar el duelo.</p>
      <button class="duelo-cerrar">×</button></div>`
    capa.querySelector('.duelo-cerrar').addEventListener('click', cerrar)
    return { cerrar }
  }

  capa.innerHTML = `
    <button class="duelo-cerrar" aria-label="cerrar">×</button>
    <div class="duelo-titulares">
      <div class="duelo-lado" style="--c:${COLOR_A}"><span>A</span><h3>${esc(datos.a.titular)}</h3>
        <div class="duelo-dir">${esc(datos.a.tarjeta.direccion)} ${datos.a.resumen.direccion_pct}%</div></div>
      <div class="duelo-vs">vs</div>
      <div class="duelo-lado" style="--c:${COLOR_B}"><span>B</span><h3>${esc(datos.b.titular)}</h3>
        <div class="duelo-dir">${esc(datos.b.tarjeta.direccion)} ${datos.b.resumen.direccion_pct}%</div></div>
    </div>
    <canvas class="duelo-escena"></canvas>
    <canvas class="duelo-precios" width="720" height="120"></canvas>
    <div class="duelo-barra">
      <button class="duelo-toggle">Alternar A / B</button>
      <button class="duelo-reel">● Exportar Reel (12s)</button>
      <span class="duelo-estado"></span>
    </div>
    <p class="duelo-descargo">${esc(datos.descargo)}</p>`

  capa.querySelector('.duelo-cerrar').addEventListener('click', cerrar)

  // modo estático (reduce-motion): solo las curvas de precio, sin 3D
  const canvas = capa.querySelector('.duelo-escena')
  if (reducirMovimiento) {
    canvas.style.display = 'none'
    dibujarPrecios(capa.querySelector('.duelo-precios'), datos.a.serie_precios, datos.b.serie_precios)
    return { cerrar }
  }

  // ---------- escena con los dos enjambres ----------
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  const escena = new THREE.Scene()
  escena.background = new THREE.Color('#0b0e14')
  escena.fog = new THREE.FogExp2('#0b0e14', 0.02)
  const camara = new THREE.PerspectiveCamera(55, 2, 0.1, 200)

  const enjA = new Enjambre(11)
  const enjB = new Enjambre(23)
  enjA.modoRemoto = enjB.modoRemoto = true
  enjA.fijarProporcion(0.5)
  enjB.fijarProporcion(0.5) // dos enjambres: cada uno con la mitad de partículas
  enjA.grupo.position.x = -11
  enjB.grupo.position.x = 11
  escena.add(enjA.grupo, enjB.grupo)
  enjA.fijarLideresRemotos(datos.a.lideres || [])
  enjB.fijarLideresRemotos(datos.b.lideres || [])

  // frames (replay) de cada lado
  let fA = null
  let fB = null
  try {
    fA = framesDe(await (await fetch(`${api}/api/simulacion/${idA}/replay`)).arrayBuffer())
    fB = framesDe(await (await fetch(`${api}/api/simulacion/${idB}/replay`)).arrayBuffer())
  } catch {
    /* sin replay: los enjambres quedan en su calma, igual se ve el duelo */
  }

  let movil = window.innerWidth < 820
  let mostrandoA = true
  function encuadrar() {
    movil = window.innerWidth < 820
    const w = canvas.clientWidth || window.innerWidth
    const h = canvas.clientHeight || 420
    renderer.setSize(w, h, false)
    camara.aspect = w / h
    if (movil) {
      // móvil: uno a la vez (dos canvas 3D rompen el presupuesto de fps)
      enjA.grupo.visible = mostrandoA
      enjB.grupo.visible = !mostrandoA
      enjA.grupo.position.x = enjB.grupo.position.x = 0
      camara.position.set(0, 6, 26)
    } else {
      enjA.grupo.visible = enjB.grupo.visible = true
      enjA.grupo.position.x = -11
      enjB.grupo.position.x = 11
      camara.position.set(0, 7, 40)
    }
    camara.lookAt(0, 0, 0)
    camara.updateProjectionMatrix()
  }
  encuadrar()
  window.addEventListener('resize', encuadrar)

  capa.querySelector('.duelo-toggle').addEventListener('click', () => {
    mostrandoA = !mostrandoA
    encuadrar()
  })

  // ---------- replay sincronizado ----------
  const serieA = [datos.a.serie_precios[0]]
  const serieB = [datos.b.serie_precios[0]]
  const lienzoPrecios = capa.querySelector('.duelo-precios')
  let cuadro = 0
  const totalCuadros = Math.max(fA?.total || 1, fB?.total || 1)
  reloj = setInterval(() => {
    if (fA) { const f = fA.en(cuadro); enjA.aplicarEstadoRemoto(f.precio, f.sent); serieA.push(f.precio) }
    if (fB) { const f = fB.en(cuadro); enjB.aplicarEstadoRemoto(f.precio, f.sent); serieB.push(f.precio) }
    dibujarPrecios(lienzoPrecios, serieA, serieB)
    cuadro = (cuadro + 1) % totalCuadros
    if (cuadro === 0) { serieA.length = 1; serieB.length = 1 } // vuelve a empezar en bucle
  }, 80)

  // ---------- loop de render ----------
  const relojThree = new THREE.Clock()
  function frame() {
    const dt = Math.min(relojThree.getDelta(), 0.05)
    const t = relojThree.getElapsedTime()
    enjA.actualizar(t, dt)
    enjB.actualizar(t, dt)
    renderer.render(escena, camara)
    anim = requestAnimationFrame(frame)
  }
  frame()

  // ---------- exportar Reel (9:16) ----------
  capa.querySelector('.duelo-reel').addEventListener('click', () =>
    exportarReel(renderer, datos, capa.querySelector('.duelo-estado')))

  return { cerrar }
}

// ---------- curvas de precio superpuestas ----------

function dibujarPrecios(lienzo, serieA, serieB) {
  const ctx = lienzo.getContext('2d')
  const W = lienzo.width, H = lienzo.height
  ctx.clearRect(0, 0, W, H)
  const todos = [...serieA, ...serieB]
  const min = Math.min(...todos), max = Math.max(...todos)
  const rango = Math.max(max - min, 0.5)
  const curva = (serie, color) => {
    ctx.beginPath()
    serie.forEach((v, i) => {
      const x = (i / Math.max(serie.length - 1, 1)) * (W - 8) + 4
      const y = H - 6 - ((v - min) / rango) * (H - 12)
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)
    })
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.lineJoin = 'round'
    ctx.stroke()
  }
  curva(serieA, COLOR_A)
  curva(serieB, COLOR_B)
}

// ---------- el Reel vertical para redes ----------

async function exportarReel(renderer, datos, estado) {
  if (!window.MediaRecorder) { estado.textContent = 'Tu navegador no permite grabar.'; return }
  const comp = document.createElement('canvas')
  comp.width = 1080; comp.height = 1920
  const ctx = comp.getContext('2d')
  const flujo = comp.captureStream(30)
  const tipos = ['video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm']
  const mime = tipos.find((t) => MediaRecorder.isTypeSupported(t)) || 'video/webm'
  const trozos = []
  const rec = new MediaRecorder(flujo, { mimeType: mime, videoBitsPerSecond: 6_000_000 })
  rec.ondataavailable = (e) => e.data.size && trozos.push(e.data)
  rec.onstop = () => {
    const blob = new Blob(trozos, { type: 'video/webm' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'enjambre-duelo.webm'
    a.click()
    estado.textContent = '¡Reel listo! (video/webm)'
  }

  const gl = renderer.domElement
  let t0 = null
  function pinta(ts) {
    if (t0 === null) t0 = ts
    const seg = (ts - t0) / 1000
    ctx.fillStyle = '#0b0e14'; ctx.fillRect(0, 0, 1080, 1920)
    // el enjambre (recuadro central)
    ctx.drawImage(gl, 0, 420, 1080, 1080)
    // titulares
    ctx.fillStyle = COLOR_A; ctx.font = 'bold 40px Georgia, serif'
    ctx.fillText('A', 60, 200)
    ctx.fillStyle = '#f4efe6'; ctx.font = '34px Georgia, serif'
    envolver(ctx, datos.a.titular, 130, 175, 900, 40)
    ctx.fillStyle = COLOR_B; ctx.font = 'bold 40px Georgia, serif'
    ctx.fillText('B', 60, 360)
    ctx.fillStyle = '#f4efe6'; ctx.font = '34px Georgia, serif'
    envolver(ctx, datos.b.titular, 130, 335, 900, 40)
    // marca de agua + disclaimer
    ctx.fillStyle = '#c9a227'; ctx.font = 'bold 30px Georgia, serif'
    ctx.fillText('El Enjambre · Rubicón Lab', 60, 1600)
    ctx.fillStyle = 'rgba(244,239,230,0.6)'; ctx.font = '22px sans-serif'
    envolver(ctx, datos.descargo, 60, 1660, 960, 28)
    if (seg < 12) requestAnimationFrame(pinta)
    else if (rec.state === 'recording') rec.stop()
  }
  rec.start()
  estado.textContent = 'Grabando 12 s…'
  requestAnimationFrame(pinta)
}

function envolver(ctx, texto, x, y, ancho, alto) {
  const palabras = String(texto).split(' ')
  let linea = '', yy = y
  for (const p of palabras) {
    const prueba = `${linea}${p} `
    if (ctx.measureText(prueba).width > ancho && linea) {
      ctx.fillText(linea, x, yy); linea = `${p} `; yy += alto
    } else linea = prueba
  }
  ctx.fillText(linea, x, yy)
}
