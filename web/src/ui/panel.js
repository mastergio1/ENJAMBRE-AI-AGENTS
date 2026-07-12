// UI de El Enjambre: entrada de noticia, tooltip de líderes y HUD.
// Estética editorial Rubicón Lab: tinta cálida, el teal como acento — "el río".

import { ESCENARIOS } from '../swarm/escenario.js'

// escape para todo texto de datos (LLM/Alpaca) que va a innerHTML
const CARACTERES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
const esc = (valor) => String(valor ?? '').replace(/[&<>"']/g, (c) => CARACTERES[c])

export function crearPanel(alEnviarTitular, alObservatorio) {
  const raiz = document.getElementById('ui')

  raiz.innerHTML = `
    <header class="marca">
      <h1>El Enjambre</h1>
      <p>el focus group sintético del mercado</p>
    </header>

    <div class="hud" aria-live="polite">
      <canvas id="sparkline" width="180" height="44"></canvas>
      <div class="hud-datos">
        <span id="hud-precio">100.00</span>
        <span id="hud-detalle">5.000 inversionistas · 60 fps</span>
      </div>
    </div>

    <div class="panel-noticia">
      <form id="form-noticia">
        <input id="campo-titular" type="text" autocomplete="off"
          placeholder="Escribe un titular… ej: la Fed sube las tasas 50 puntos base" />
        <button type="submit" id="btn-soltar">Soltar al enjambre</button>
      </form>
      <div class="chips">
        ${ESCENARIOS.map((e, i) => `<button class="chip" data-i="${i}">${e.etiqueta}</button>`).join('')}
        <button class="chip" id="btn-observatorio">🔭 Dejar corriendo</button>
      </div>
      <p class="descargo">Simulación educativa de comportamiento de masas con agentes de IA. No constituye asesoría ni recomendación de inversión.</p>
    </div>

    <div id="tooltip" class="tooltip" hidden></div>
    <aside id="reporte" class="reporte" hidden></aside>
    <div id="aviso" class="aviso" hidden></div>
  `

  const campo = raiz.querySelector('#campo-titular')
  raiz.querySelector('#form-noticia').addEventListener('submit', (evento) => {
    evento.preventDefault()
    if (campo.value.trim()) alEnviarTitular(campo.value.trim())
  })
  raiz.querySelectorAll('.chip[data-i]').forEach((chip) => {
    chip.addEventListener('click', () => {
      const escenario = ESCENARIOS[Number(chip.dataset.i)]
      campo.value = escenario.titular
      alEnviarTitular(escenario.titular)
    })
  })
  const btnObs = raiz.querySelector('#btn-observatorio')
  const btnSoltar = raiz.querySelector('#btn-soltar')
  btnObs.addEventListener('click', () => alObservatorio?.(campo.value.trim()))

  const tooltip = raiz.querySelector('#tooltip')
  const precioEl = raiz.querySelector('#hud-precio')
  const detalleEl = raiz.querySelector('#hud-detalle')
  const lienzo = raiz.querySelector('#sparkline')
  const ctx = lienzo.getContext('2d')

  return {
    fijarModoObservatorio(activo) {
      btnObs.textContent = activo ? '⏹ Detener observatorio' : '🔭 Dejar corriendo'
      btnObs.classList.toggle('activo', activo)
      btnSoltar.textContent = activo ? 'Soltar noticia encima' : 'Soltar al enjambre'
    },
    mostrarTooltip(lider, x, y) {
      // nombre y frase provienen del LLM/datos: se escapan antes de innerHTML
      tooltip.innerHTML = `<strong>${esc(lider.nombre)}</strong>${
        lider.frase ? `<em>«${esc(lider.frase)}»</em>` : '<em>aún no opina</em>'
      }`
      tooltip.style.left = `${Math.min(x + 14, window.innerWidth - 280)}px`
      tooltip.style.top = `${y + 14}px`
      tooltip.hidden = false
    },
    ocultarTooltip() {
      tooltip.hidden = true
    },
    actualizarHUD(precio, fps, particulas, modo = '') {
      precioEl.textContent = precio.toFixed(2)
      detalleEl.textContent =
        `${particulas.toLocaleString('es-CL')} inversionistas · ${Math.round(fps)} fps${modo ? ` · ${modo}` : ''}`
    },
    avisar(mensaje) {
      const aviso = raiz.querySelector('#aviso')
      aviso.textContent = mensaje
      aviso.hidden = false
      clearTimeout(aviso._temporizador)
      aviso._temporizador = setTimeout(() => { aviso.hidden = true }, 6000)
    },
    mostrarReporte(reporte, extras = {}) {
      const panelReporte = raiz.querySelector('#reporte')
      const desglose = Object.entries(reporte.desglose || {}).slice(0, 6)
      const num = (v) => Number(v) || 0

      // las 8 voces (archivo) o las 3 frases del reporte en vivo
      const vocesHtml = extras.voces
        ? extras.voces.map((v) =>
            `<p class="voz-arq">«${esc(v.frase)}» <span>— ${esc(v.nombre)} (${v.senal_media > 0 ? '+' : ''}${num(v.senal_media)})</span></p>`).join('')
        : (reporte.frases || []).map((f) => `<p>«${esc(f.frase)}»</p>`).join('')

      const epilogoHtml = extras.epilogo
        ? `<div class="epilogo"><div class="epi-rotulo">Comparación educativa · ¿y qué pasó después?</div>
           <p>${esc(extras.epilogo)}</p></div>`
        : ''

      const cabecera = extras.titular
        ? `<div class="rep-titular">${esc(extras.titular)}</div>` : ''
      const compartir = extras.id
        ? `<button class="rep-compartir" data-id="${String(extras.id).replace(/[^0-9a-f]/g, '')}">Copiar enlace</button>` : ''

      panelReporte.innerHTML = `
        <button class="cerrar" aria-label="cerrar">×</button>
        <h2>Reporte del enjambre</h2>
        ${cabecera}
        <div class="cifras">
          <div><span>${num(reporte.direccion_pct) > 0 ? '+' : ''}${num(reporte.direccion_pct)}%</span><label>dirección</label></div>
          <div><span>${num(reporte.minimo_pct)}%</span><label>mínimo</label></div>
          <div><span>${num(reporte.volatilidad_pct)}%</span><label>volatilidad/tick</label></div>
        </div>
        <table>${desglose.map(([tipo, d]) =>
          `<tr><td>${esc(tipo)}</td><td>${num(d.compras)} compras</td><td>${num(d.ventas)} ventas</td></tr>`).join('')}
        </table>
        <div class="voces">${vocesHtml}</div>
        ${epilogoHtml}
        ${compartir}
        <p class="descargo">${esc(reporte.descargo)}</p>
      `
      panelReporte.hidden = false
      panelReporte.querySelector('.cerrar').addEventListener('click', () => {
        panelReporte.hidden = true
      })
      const botonCompartir = panelReporte.querySelector('.rep-compartir')
      botonCompartir?.addEventListener('click', () => {
        const url = `${location.origin}${location.pathname}?sim=${botonCompartir.dataset.id}`
        navigator.clipboard?.writeText(url)
        botonCompartir.textContent = '¡Enlace copiado!'
      })
    },
    // sparkline del precio: una serie, línea 2px, sin adornos —
    // el texto va en tinta, nunca en el color de la serie
    dibujarSparkline(serie) {
      const ancho = lienzo.width, alto = lienzo.height
      ctx.clearRect(0, 0, ancho, alto)
      if (serie.length < 2) return
      const minimo = Math.min(...serie), maximo = Math.max(...serie)
      const rango = Math.max(maximo - minimo, 0.5)
      ctx.beginPath()
      serie.forEach((v, i) => {
        const x = (i / (serie.length - 1)) * (ancho - 4) + 2
        const y = alto - 5 - ((v - minimo) / rango) * (alto - 10)
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
      })
      ctx.strokeStyle = '#6fa89e'
      ctx.lineWidth = 2
      ctx.lineJoin = 'round'
      ctx.stroke()
    },
  }
}

/** Modo estático (prefers-reduced-motion): gráfico 2D del precio en grande. */
export function dibujarGraficoEstatico(serie) {
  const lienzo = document.getElementById('grafico-estatico')
  lienzo.hidden = false
  const dpr = Math.min(window.devicePixelRatio, 2)
  const ancho = Math.min(window.innerWidth - 48, 720), alto = 220
  lienzo.width = ancho * dpr
  lienzo.height = alto * dpr
  lienzo.style.width = `${ancho}px`
  lienzo.style.height = `${alto}px`
  const ctx = lienzo.getContext('2d')
  ctx.scale(dpr, dpr)

  const minimo = Math.min(...serie), maximo = Math.max(...serie)
  const rango = Math.max(maximo - minimo, 0.5)
  const margen = { arriba: 14, abajo: 22, izq: 8, der: 54 }
  const aX = (i) => margen.izq + (i / (serie.length - 1)) * (ancho - margen.izq - margen.der)
  const aY = (v) => alto - margen.abajo - ((v - minimo) / rango) * (alto - margen.arriba - margen.abajo)

  // rejilla recesiva: dos líneas de referencia apenas visibles
  ctx.strokeStyle = 'rgba(243,238,232,0.12)'
  ctx.lineWidth = 1
  for (const v of [minimo, maximo]) {
    ctx.beginPath(); ctx.moveTo(margen.izq, aY(v)); ctx.lineTo(ancho - margen.der, aY(v)); ctx.stroke()
  }

  ctx.beginPath()
  serie.forEach((v, i) => (i === 0 ? ctx.moveTo(aX(i), aY(v)) : ctx.lineTo(aX(i), aY(v))))
  ctx.strokeStyle = '#6fa89e'
  ctx.lineWidth = 2
  ctx.lineJoin = 'round'
  ctx.stroke()

  // etiquetas en tinta (no en el color de la serie)
  ctx.fillStyle = 'rgba(243,238,232,0.75)'
  ctx.font = '12px Jost, sans-serif'
  ctx.fillText(maximo.toFixed(1), ancho - margen.der + 6, aY(maximo) + 4)
  ctx.fillText(minimo.toFixed(1), ancho - margen.der + 6, aY(minimo) + 4)
  ctx.fillText('evolución del precio simulado', margen.izq, alto - 6)
}
