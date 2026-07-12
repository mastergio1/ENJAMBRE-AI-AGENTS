// El Archivo — la hemeroteca (CONTENIDO.md sección 5).
// "El Enjambre dijo": toda simulación destacada queda para siempre,
// navegable por mes, buscable por titular y filtrable por ticker. Cada
// una tiene URL propia y compartible (?sim=<id>).

import { urlApi } from '../ui/conexion.js'

const CARACTERES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => CARACTERES[c])
const idSeguro = (v) => String(v ?? '').replace(/[^0-9a-f]/g, '')

const FECHA = new Intl.DateTimeFormat('es-CL', { day: 'numeric', month: 'short', year: 'numeric' })
const MES = new Intl.DateTimeFormat('es-CL', { month: 'long', year: 'numeric' })

function nombreMes(mes) {
  const [a, m] = mes.split('-')
  return MES.format(new Date(Number(a), Number(m) - 1, 1))
}

function tarjetaArchivo(item) {
  const t = item.tarjeta || {}
  const clase = t.direccion === '▲' ? 'sube' : t.direccion === '▼' ? 'baja' : 'plana'
  const simbolos = (item.simbolos || '').split(',').filter(Boolean).slice(0, 4).map(esc).join(' · ')
  const pct = Number(t.direccion_pct) || 0
  return `
    <a class="arch-item" href="?sim=${idSeguro(item.id)}">
      <div class="arch-meta">${FECHA.format(new Date(item.fecha))}${simbolos ? ' · ' + simbolos : ''}
        ${item.tiene_epilogo ? '· <span class="arch-epi">¿y qué pasó?</span>' : ''}</div>
      <h3>${esc(item.titular)}</h3>
      <div class="arch-res">
        <span class="flecha ${clase}">${esc(t.direccion)} ${pct > 0 ? '+' : ''}${pct}%</span>
        <span class="agitacion">agitación ${esc(t.agitacion)}</span>
      </div>
    </a>`
}

/**
 * Monta la hemeroteca como overlay. `alAbrirSim(id)` la cierra y abre esa
 * simulación. Devuelve { cerrar }.
 */
export async function abrirArchivo({ alAbrirSim, alCerrar }) {
  const api = urlApi()
  const capa = document.getElementById('archivo')
  capa.hidden = false
  document.body.classList.add('archivo-abierto')

  const estado = { mes: '', q: '', ticker: '', pagina: 0 }

  function cerrar() {
    capa.hidden = true
    document.body.classList.remove('archivo-abierto')
    alCerrar?.()
  }

  async function cargar() {
    const params = new URLSearchParams()
    if (estado.mes) params.set('mes', estado.mes)
    if (estado.q) params.set('q', estado.q)
    if (estado.ticker) params.set('ticker', estado.ticker)
    params.set('pagina', estado.pagina)
    try {
      const r = await fetch(`${api}/api/archivo?${params}`)
      if (!r.ok) throw new Error('archivo')
      return await r.json()
    } catch {
      return null
    }
  }

  function render(datos) {
    if (!datos) {
      capa.querySelector('.arch-lista').innerHTML =
        '<p class="arch-vacio">El archivo descansa. Vuelve cuando el enjambre haya reaccionado.</p>'
      return
    }
    const chips = datos.meses.map((m) =>
      `<button class="arch-chip ${m === estado.mes ? 'activo' : ''}" data-mes="${m}">${nombreMes(m)}</button>`
    ).join('')
    const lista = datos.items.length
      ? datos.items.map(tarjetaArchivo).join('')
      : '<p class="arch-vacio">Sin resultados para esa búsqueda.</p>'
    const totalPaginas = Math.ceil(datos.total / datos.por_pagina)
    const paginador = totalPaginas > 1
      ? `<div class="arch-pag">
          <button class="arch-prev" ${estado.pagina === 0 ? 'disabled' : ''}>‹ anteriores</button>
          <span>${estado.pagina + 1} / ${totalPaginas}</span>
          <button class="arch-next" ${estado.pagina + 1 >= totalPaginas ? 'disabled' : ''}>siguientes ›</button>
        </div>` : ''

    capa.querySelector('.arch-meses').innerHTML =
      `<button class="arch-chip ${!estado.mes ? 'activo' : ''}" data-mes="">Todos</button>${chips}`
    capa.querySelector('.arch-lista').innerHTML = lista + paginador
    capa.querySelector('.arch-total').textContent =
      `${datos.total} ${datos.total === 1 ? 'reacción archivada' : 'reacciones archivadas'}`

    conectar()
  }

  function conectar() {
    capa.querySelectorAll('.arch-chip').forEach((b) =>
      b.addEventListener('click', () => { estado.mes = b.dataset.mes; estado.pagina = 0; recargar() }))
    capa.querySelector('.arch-prev')?.addEventListener('click', () => { estado.pagina--; recargar() })
    capa.querySelector('.arch-next')?.addEventListener('click', () => { estado.pagina++; recargar() })
    capa.querySelectorAll('.arch-item').forEach((a) =>
      a.addEventListener('click', (e) => {
        e.preventDefault()
        const id = idSeguro(new URL(a.href).searchParams.get('sim'))
        alAbrirSim(id)
      }))
  }

  async function recargar() {
    render(await cargar())
  }

  capa.innerHTML = `
    <div class="arch-panel">
      <header class="arch-cab">
        <button class="arch-cerrar" aria-label="cerrar">×</button>
        <h1>El Enjambre dijo</h1>
        <p>La hemeroteca de las reacciones del enjambre. <span class="arch-total"></span></p>
      </header>
      <div class="arch-filtros">
        <input class="arch-buscar" type="search" placeholder="Buscar en los titulares…" />
        <input class="arch-ticker" type="text" placeholder="Ticker (ej: SPY)" />
      </div>
      <div class="arch-meses"></div>
      <div class="arch-lista"></div>
      <p class="arch-descargo"></p>
    </div>`

  capa.querySelector('.arch-cerrar').addEventListener('click', cerrar)
  let debounce
  capa.querySelector('.arch-buscar').addEventListener('input', (e) => {
    clearTimeout(debounce)
    debounce = setTimeout(() => { estado.q = e.target.value.trim(); estado.pagina = 0; recargar() }, 300)
  })
  capa.querySelector('.arch-ticker').addEventListener('input', (e) => {
    clearTimeout(debounce)
    debounce = setTimeout(() => { estado.ticker = e.target.value.trim(); estado.pagina = 0; recargar() }, 300)
  })

  const datos = await cargar()
  render(datos)
  if (datos) capa.querySelector('.arch-descargo').textContent = datos.descargo

  return { cerrar }
}
