// El Widget embebible (CONTENIDO.md sección 9).
// Un iframe del enjambre reaccionando, que un medio incrusta en sus notas.
// - Solo LEE simulaciones cacheadas; JAMÁS dispara simulaciones nuevas.
// - Firma + link a la web + disclaimer CMF SIEMPRE visible.
// - Parámetros: ?sim=<id> (fija) o ?modo=hoy (la destacada del día).
// - Dominio fuera de la lista blanca (CORS lo bloquea) → versión con CTA.

import * as THREE from 'three'
import { Enjambre } from '../swarm/enjambre.js'
import { urlApi } from '../ui/conexion.js'

const TAMANO_FRAME = 8 + 5000
const DISCLAIMER =
  'Simulación educativa de comportamiento de masas con agentes de IA. No constituye asesoría ni recomendación de inversión.'
const WEB = (urlApi() || '').replace(/\/$/, '') && (import.meta.env.VITE_WEB_URL || 'https://enjambre.vercel.app')

const raiz = document.getElementById('widget')
const canvas = document.getElementById('wcanvas')
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

const params = new URLSearchParams(location.search)
const api = urlApi()

function superponer(html) {
  const capa = document.createElement('div')
  capa.innerHTML = html
  Object.assign(capa.style, {
    position: 'absolute', inset: '0', pointerEvents: 'none',
    display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
    padding: '14px 16px', boxSizing: 'border-box', color: '#f3eee8',
    fontFamily: 'system-ui, sans-serif',
  })
  raiz.appendChild(capa)
  return capa
}

const ESTILO_LINK = 'color:#6fa89e;text-decoration:none;pointer-events:auto;'
const ESTILO_DISCLAIMER = 'font-size:10px;line-height:1.4;color:rgba(243,238,232,0.55);'
const ESTILO_FIRMA = 'font-size:12px;color:#f3eee8;font-weight:600;'

function pie(extra = '') {
  return `<div>${extra}
    <div style="${ESTILO_FIRMA}">El Enjambre <span style="opacity:.7;font-weight:400">by Rubicón Lab</span>
      &nbsp;·&nbsp;<a href="${WEB}" target="_blank" rel="noopener" style="${ESTILO_LINK}">ver en vivo →</a></div>
    <div style="${ESTILO_DISCLAIMER}">${DISCLAIMER}</div>
  </div>`
}

function mostrarCTA() {
  canvas.style.display = 'none'
  superponer(`
    <div></div>
    <div style="pointer-events:auto;text-align:center;">
      <div style="font-family:Georgia,serif;font-size:22px;color:#6fa89e;font-weight:bold;">El Enjambre</div>
      <p style="font-size:14px;color:#f3eee8;max-width:320px;margin:8px auto;">
        El focus group sintético del mercado, para tu medio.</p>
      <a href="${WEB}" target="_blank" rel="noopener"
        style="display:inline-block;background:#6fa89e;color:#1b1916;text-decoration:none;font-weight:bold;
        padding:10px 20px;font-size:13px;pointer-events:auto;">Consigue el widget para tu medio</a>
    </div>
    ${pie()}`)
}

// ---------- carga de la simulación (solo cacheada) ----------

async function idDelDia() {
  const muro = await (await fetch(`${api}/api/muro`)).json()
  const dest = muro.tarjetas.find((t) => t.destacada && t.sim_id)
  return dest ? dest.sim_id : null
}

async function iniciar() {
  if (!api) return mostrarCTA()
  let id = params.get('sim')
  if (!/^[0-9a-f]{16}$/.test(id || '')) id = params.get('modo') === 'hoy' ? null : id
  try {
    if (!id) id = await idDelDia()
    if (!/^[0-9a-f]{16}$/.test(id || '')) return mostrarCTA()
    const sim = await (await fetch(`${api}/api/simulacion/${id}`)).json()
    let frames = null
    if (sim.tiene_replay) {
      frames = await (await fetch(`${api}/api/simulacion/${id}/replay`)).arrayBuffer()
    }
    render(sim, frames)
  } catch {
    // dominio no permitido (CORS) o motor caído → la versión con CTA
    mostrarCTA()
  }
}

// ---------- render minimal del enjambre ----------

function render(sim, buffer) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  const escena = new THREE.Scene()
  escena.background = new THREE.Color('#1b1916')
  escena.fog = new THREE.FogExp2('#1b1916', 0.02)
  const camara = new THREE.PerspectiveCamera(55, 1, 0.1, 120)

  const enjambre = new Enjambre(7)
  enjambre.modoRemoto = true
  enjambre.fijarProporcion(0.6)
  enjambre.fijarLideresRemotos(sim.lideres || [])
  escena.add(enjambre.grupo)

  function encuadrar() {
    const w = raiz.clientWidth || 480, h = raiz.clientHeight || 360
    renderer.setSize(w, h, false)
    camara.aspect = w / h
    camara.position.set(0, 6, 30)
    camara.lookAt(0, 0, 0)
    camara.updateProjectionMatrix()
  }
  encuadrar()
  window.addEventListener('resize', encuadrar)

  // replay en bucle (si hay frames)
  if (buffer) {
    const total = Math.floor(buffer.byteLength / TAMANO_FRAME)
    let c = 0
    setInterval(() => {
      const base = Math.min(c, total - 1) * TAMANO_FRAME
      const precio = new DataView(buffer, base, 8).getFloat32(0, true)
      enjambre.aplicarEstadoRemoto(precio, new Int8Array(buffer, base + 8, 5000))
      c = (c + 1) % total
    }, 80)
  }

  const reloj = new THREE.Clock()
  renderer.setAnimationLoop(() => {
    const dt = Math.min(reloj.getDelta(), 0.05)
    enjambre.actualizar(reloj.getElapsedTime(), dt)
    renderer.render(escena, camara)
  })

  superponer(`
    <div style="pointer-events:none;">
      <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:rgba(243,238,232,0.5);">
        El enjambre reaccionó a</div>
      <div style="font-family:Georgia,serif;font-size:16px;font-weight:bold;line-height:1.2;max-width:80%;">
        ${esc(sim.titular)}</div>
    </div>
    ${pie()}`)
}

iniciar()
