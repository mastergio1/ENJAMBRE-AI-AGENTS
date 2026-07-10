// UI de El Enjambre: entrada de noticia, tooltip de líderes y HUD.
// Estética editorial Rubicón Lab: tinta profunda, dorado como acento.

import { ESCENARIOS } from '../swarm/escenario.js'

export function crearPanel(alEnviarTitular) {
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
        <button type="submit">Soltar al enjambre</button>
      </form>
      <div class="chips">
        ${ESCENARIOS.map((e, i) => `<button class="chip" data-i="${i}">${e.etiqueta}</button>`).join('')}
      </div>
      <p class="descargo">Simulación educativa de comportamiento de masas con agentes de IA. No constituye asesoría ni recomendación de inversión.</p>
    </div>

    <div id="tooltip" class="tooltip" hidden></div>
    <aside id="reporte" class="reporte" hidden></aside>
  `

  const campo = raiz.querySelector('#campo-titular')
  raiz.querySelector('#form-noticia').addEventListener('submit', (evento) => {
    evento.preventDefault()
    if (campo.value.trim()) alEnviarTitular(campo.value.trim())
  })
  raiz.querySelectorAll('.chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const escenario = ESCENARIOS[Number(chip.dataset.i)]
      campo.value = escenario.titular
      alEnviarTitular(escenario.titular)
    })
  })

  const tooltip = raiz.querySelector('#tooltip')
  const precioEl = raiz.querySelector('#hud-precio')
  const detalleEl = raiz.querySelector('#hud-detalle')
  const lienzo = raiz.querySelector('#sparkline')
  const ctx = lienzo.getContext('2d')

  return {
    mostrarTooltip(lider, x, y) {
      tooltip.innerHTML = `<strong>${lider.nombre}</strong>${
        lider.frase ? `<em>«${lider.frase}»</em>` : '<em>aún no opina</em>'
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
    mostrarReporte(reporte) {
      const panelReporte = raiz.querySelector('#reporte')
      const desglose = Object.entries(reporte.desglose).slice(0, 6)
      panelReporte.innerHTML = `
        <button class="cerrar" aria-label="cerrar">×</button>
        <h2>Reporte del enjambre</h2>
        <div class="cifras">
          <div><span>${reporte.direccion_pct > 0 ? '+' : ''}${reporte.direccion_pct}%</span><label>dirección</label></div>
          <div><span>${reporte.minimo_pct}%</span><label>mínimo</label></div>
          <div><span>${reporte.volatilidad_pct}%</span><label>volatilidad/tick</label></div>
        </div>
        <table>${desglose.map(([tipo, d]) =>
          `<tr><td>${tipo}</td><td>${d.compras} compras</td><td>${d.ventas} ventas</td></tr>`).join('')}
        </table>
        <div class="voces">${reporte.frases.map((f) => `<p>«${f.frase}»</p>`).join('')}</div>
        <p class="descargo">${reporte.descargo}</p>
      `
      panelReporte.hidden = false
      panelReporte.querySelector('.cerrar').addEventListener('click', () => {
        panelReporte.hidden = true
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
      ctx.strokeStyle = '#c9a227'
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
  ctx.strokeStyle = 'rgba(244,239,230,0.12)'
  ctx.lineWidth = 1
  for (const v of [minimo, maximo]) {
    ctx.beginPath(); ctx.moveTo(margen.izq, aY(v)); ctx.lineTo(ancho - margen.der, aY(v)); ctx.stroke()
  }

  ctx.beginPath()
  serie.forEach((v, i) => (i === 0 ? ctx.moveTo(aX(i), aY(v)) : ctx.lineTo(aX(i), aY(v))))
  ctx.strokeStyle = '#c9a227'
  ctx.lineWidth = 2
  ctx.lineJoin = 'round'
  ctx.stroke()

  // etiquetas en tinta (no en el color de la serie)
  ctx.fillStyle = 'rgba(244,239,230,0.75)'
  ctx.font = '12px Jost, sans-serif'
  ctx.fillText(maximo.toFixed(1), ancho - margen.der + 6, aY(maximo) + 4)
  ctx.fillText(minimo.toFixed(1), ancho - margen.der + 6, aY(minimo) + 4)
  ctx.fillText('evolución del precio simulado', margen.izq, alto - 6)
}
