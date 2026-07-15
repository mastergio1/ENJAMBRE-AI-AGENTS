// El muro de noticias — la nueva portada (CONTENIDO.md sección 4).
// Columna editorial tipo periódico sobre el enjambre; las destacadas del
// día ya vienen simuladas (Estado A, con replay 3D), el resto se puede
// soltar al enjambre en vivo (Estado B). Todo desde caché: el costo
// marginal de cada visitante es cero.

import { urlApi } from '../ui/conexion.js'

const TAMANO_FRAME = 8 + 5000 // [precio f32][tick u32][sentimiento i8 × 5000]
const TARJETAS_VISIBLES = 12

// La firma de autoría "Creada por Rubicón Lab" (manual de marca §10).
// TODO Giorgio: confirmar el destino real (dominio del estudio o Instagram).
const URL_ESTUDIO = 'https://instagram.com/rubiconlab'
const FIRMA_RUBICON = `
  <div class="cruce" aria-hidden="true"></div>
  <div class="muro-firma">
    <a href="${URL_ESTUDIO}" target="_blank" rel="noopener noreferrer"
       class="rl-credit" aria-label="Sitio creado por Rubicón Lab">
      <span class="rl-pre">Creada por</span>
      <span class="rl-full">
        <span class="rl-name">Rubicón</span><span class="rl-bar"></span><span class="rl-lab">Lab</span>
      </span>
      <span class="rl-compact" aria-hidden="true">
        <span class="rl-iso"><span class="rl-name">R</span><span class="rl-bar"></span></span>
        <span class="rl-iso-text">Rubicón Lab</span>
      </span>
    </a>
  </div>`

/** Reproduce los frames binarios de una simulación guardada sobre el enjambre. */
export class ReproductorReplay {
  constructor(enjambre) {
    this.enjambre = enjambre
    this.temporizador = null
    this.buffer = null
  }

  async cargar(url) {
    const respuesta = await fetch(url)
    if (!respuesta.ok) throw new Error('sin replay')
    this.buffer = await respuesta.arrayBuffer()
    this.total = Math.floor(this.buffer.byteLength / TAMANO_FRAME)
  }

  reproducir({ bucle = false, alTerminar } = {}) {
    this.detener()
    if (!this.buffer || this.total === 0) return
    this.enjambre.modoRemoto = true
    let cuadro = 0
    this.temporizador = setInterval(() => {
      if (cuadro >= this.total) {
        if (bucle) {
          cuadro = 0
        } else {
          this.detener()
          this.enjambre.modoRemoto = false // el enjambre vuelve a su calma
          alTerminar?.()
          return
        }
      }
      const base = cuadro * TAMANO_FRAME
      const vista = new DataView(this.buffer, base, 8)
      const sentimientos = new Int8Array(this.buffer, base + 8, 5000)
      this.enjambre.aplicarEstadoRemoto(vista.getFloat32(0, true), sentimientos)
      cuadro++
    }, 80)
  }

  detener() {
    if (this.temporizador) clearInterval(this.temporizador)
    this.temporizador = null
  }
}

const HORA = new Intl.DateTimeFormat('es-CL', { hour: '2-digit', minute: '2-digit' })

// Escapa todo lo que provenga de datos (titulares de Alpaca, frases del
// LLM, tickers): estos textos NO son de confianza y se pintan con
// innerHTML. Sin esto, un titular con <img onerror> sería XSS almacenado.
const CARACTERES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
function esc(valor) {
  return String(valor ?? '').replace(/[&<>"']/g, (c) => CARACTERES[c])
}
// para atributos que además usamos como selectores: solo hex del id
const idSeguro = (valor) => String(valor ?? '').replace(/[^0-9a-f]/g, '')

function plantillaTarjeta(tarjeta) {
  const hora = tarjeta.fecha ? HORA.format(new Date(tarjeta.fecha)) : ''
  const simbolos = (tarjeta.simbolos || '').split(',').filter(Boolean).slice(0, 3).join(' · ')
  const meta = [hora, tarjeta.fuente, simbolos].filter(Boolean).map(esc).join(' · ')

  let cuerpo
  if (tarjeta.estado === 'simulada' && tarjeta.resumen) {
    const r = tarjeta.resumen
    const clase = r.direccion === '▲' ? 'sube' : r.direccion === '▼' ? 'baja' : 'plana'
    const pct = Number(r.direccion_pct) || 0
    cuerpo = `
      <div class="resultado">
        <span class="flecha ${clase}">${esc(r.direccion)} ${pct > 0 ? '+' : ''}${pct}%</span>
        <span class="agitacion">agitación ${esc(r.agitacion)}</span>
      </div>
      ${r.frase ? `<p class="voz">«${esc(r.frase.frase)}» — <span>${esc(r.frase.arquetipo)}</span></p>` : ''}
      <button class="accion ver-simulacion" data-sim="${idSeguro(tarjeta.sim_id)}">Ver la simulación</button>`
  } else {
    cuerpo = `<button class="accion ver-reaccion" data-id="${idSeguro(tarjeta.id)}">Ver reacción del enjambre</button>`
  }

  return `
    <article class="tarjeta ${tarjeta.destacada ? 'portada' : ''}" data-id="${idSeguro(tarjeta.id)}">
      <div class="meta">${meta}${tarjeta.destacada ? ' · <strong>destacada del día</strong>' : ''}</div>
      <h3>${esc(tarjeta.titular)}</h3>
      ${cuerpo}
    </article>`
}

/**
 * Monta el muro. Devuelve {recargar, detenerReplay} para coordinarse
 * con las simulaciones en vivo que dispara main.js.
 */
export async function inicializarMuro({ enjambre, panel, correrTitular, reducirMovimiento, fijarModo, abrirArchivo }) {
  const api = urlApi()
  const contenedor = document.getElementById('muro')
  const replay = new ReproductorReplay(enjambre)
  let visibles = TARJETAS_VISIBLES

  async function cargarDatos() {
    const respuesta = await fetch(`${api}/api/muro`)
    if (!respuesta.ok) throw new Error('motor sin respuesta')
    return respuesta.json()
  }

  function renderAviso(mensaje) {
    contenedor.innerHTML = `
      <header class="muro-cabecera"><h1>El Enjambre</h1>
        <p>el focus group sintético del mercado</p></header>
      <p class="muro-aviso">${mensaje}</p>
      ${FIRMA_RUBICON}`
    document.body.classList.add('con-muro')
  }

  function render(datos) {
    const tarjetas = datos.tarjetas.slice(0, visibles)
    const fecha = new Intl.DateTimeFormat('es-CL', { weekday: 'long', day: 'numeric', month: 'long' })
      .format(new Date())
    contenedor.innerHTML = `
      <header class="muro-cabecera">
        <button class="plegar" aria-label="plegar el muro">⟨</button>
        <h1>El Enjambre</h1>
        <p>el focus group sintético del mercado</p>
        <time>${fecha}</time>
        <button class="ver-archivo" data-guia>¿Cómo funciona? · Guía rápida</button>
        <button class="ver-archivo">El archivo · «El Enjambre dijo» →</button>
      </header>
      <div class="muro-lista">${tarjetas.map(plantillaTarjeta).join('')}</div>
      ${datos.tarjetas.length > visibles
        ? '<button class="accion ver-mas">Ver más titulares</button>' : ''}
      <section class="pulso">
        <h2>El Pulso del Enjambre</h2>
        <p>Cada mañana, la reacción del enjambre a los titulares del día. Un correo, sin ruido.</p>
        <form class="pulso-form">
          <input type="email" name="email" placeholder="tu@correo.cl" autocomplete="email" required />
          <button type="submit" class="accion">Suscribirme</button>
        </form>
        <p class="pulso-estado" hidden></p>
      </section>
      <section class="organizaciones">
        <h2>El Enjambre para tu organización</h2>
        <p>Educación financiera, medios y fintechs: demos guiadas, el widget
        embebible para tu sitio y escenarios a medida para tus cursos o
        coberturas. Herramienta educativa de simulación — cuéntanos tu caso.</p>
        <form class="org-form">
          <input type="text" name="nombre" placeholder="Tu nombre" autocomplete="name" required aria-label="Tu nombre" />
          <input type="text" name="organizacion" placeholder="Organización (opcional)" autocomplete="organization" aria-label="Organización" />
          <input type="email" name="email" placeholder="tu@correo.cl" autocomplete="email" required aria-label="Tu correo" />
          <textarea name="mensaje" rows="3" maxlength="800" placeholder="¿Qué te gustaría hacer con El Enjambre?" aria-label="Mensaje"></textarea>
          <button type="submit" class="accion">Conversemos</button>
        </form>
        <p class="org-estado" role="status" hidden></p>
      </section>
      <p class="muro-descargo">${esc(datos.descargo)}</p>
      <footer class="pie">
        <span>© ${new Date().getFullYear()} · El Enjambre</span>
        <button class="pie-enlace" data-guia>Guía rápida</button>
        <button class="pie-enlace pie-archivo">El archivo</button>
        <button class="pie-enlace pie-org">Organizaciones</button>
      </footer>
      ${FIRMA_RUBICON}`
    document.body.classList.add('con-muro')
    conectarEventos(datos)
  }

  /** Pliega o despliega el muro manteniendo la flecha sincronizada. */
  function fijarPlegado(plegado) {
    document.body.classList.toggle('muro-plegado', plegado)
    const boton = contenedor.querySelector('.plegar')
    if (boton) boton.textContent = plegado ? '⟩' : '⟨'
  }

  function conectarPulso() {
    const form = contenedor.querySelector('.pulso-form')
    const estado = contenedor.querySelector('.pulso-estado')
    if (!form) return
    form.addEventListener('submit', async (evento) => {
      evento.preventDefault()
      const email = form.email.value.trim()
      estado.hidden = false
      estado.textContent = 'Enviando…'
      try {
        const r = await (await fetch(`${api}/api/suscribir`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, origen: 'web' }),
        })).json()
        estado.textContent = r.mensaje || 'Listo.'
        if (r.estado === 'pendiente' || r.estado === 'ya_suscrito') form.reset()
      } catch {
        estado.textContent = 'No se pudo completar. Intenta más tarde.'
      }
    })
  }

  function conectarOrganizaciones() {
    const form = contenedor.querySelector('.org-form')
    const estado = contenedor.querySelector('.org-estado')
    if (!form) return
    form.addEventListener('submit', async (evento) => {
      evento.preventDefault()
      estado.hidden = false
      estado.textContent = 'Enviando…'
      try {
        const r = await (await fetch(`${api}/api/contacto`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nombre: form.nombre.value.trim(),
            organizacion: form.organizacion.value.trim(),
            email: form.email.value.trim(),
            mensaje: form.mensaje.value.trim(),
          }),
        })).json()
        estado.textContent = r.mensaje || r.error || 'Listo.'
        if (r.estado === 'recibido') form.reset()
      } catch {
        estado.textContent = 'No se pudo enviar. Intenta más tarde.'
      }
    })
  }

  function conectarEventos(datos) {
    conectarPulso()
    conectarOrganizaciones()
    contenedor.querySelector('.ver-archivo')?.addEventListener('click', () => abrirArchivo?.())
    contenedor.querySelector('.pie-archivo')?.addEventListener('click', () => abrirArchivo?.())
    contenedor.querySelector('.pie-org')?.addEventListener('click', () =>
      contenedor.querySelector('.organizaciones')?.scrollIntoView({ behavior: 'smooth', block: 'center' }))
    contenedor.querySelector('.plegar')?.addEventListener('click', () =>
      fijarPlegado(!document.body.classList.contains('muro-plegado')))
    contenedor.querySelector('.ver-mas')?.addEventListener('click', () => {
      visibles += TARJETAS_VISIBLES
      render(datos)
    })

    // Estado A: re-ver la simulación cacheada (costo cero)
    contenedor.querySelectorAll('.ver-simulacion').forEach((boton) => {
      boton.addEventListener('click', async () => {
        replay.detener()
        try {
          const detalle = await (await fetch(`${api}/api/simulacion/${boton.dataset.sim}`)).json()
          enjambre.fijarLideresRemotos(detalle.lideres || [])
          panel.mostrarReporte(detalle.resumen)
          if (detalle.tiene_replay && !reducirMovimiento) {
            await replay.cargar(`${api}/api/simulacion/${boton.dataset.sim}/replay`)
            replay.reproducir({})
          }
        } catch {
          panel.avisar('No se pudo cargar esa simulación.')
        }
      })
    })

    // Estado B: soltar el titular al enjambre EN VIVO (el espectáculo es la espera)
    contenedor.querySelectorAll('.ver-reaccion').forEach((boton) => {
      boton.addEventListener('click', async () => {
        boton.disabled = true
        boton.textContent = 'El enjambre está leyendo…'
        try {
          const respuesta = await (await fetch(`${api}/api/simular-titular`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: boton.dataset.id }),
          })).json()
          if (respuesta.estado === 'adelante') {
            replay.detener()
            correrTitular(respuesta.titular, respuesta.titular_id)
          } else if (respuesta.estado === 'limite') {
            panel.avisar(respuesta.mensaje)
            boton.textContent = 'El enjambre descansa hasta mañana'
          } else if (respuesta.estado === 'simulada') {
            await recargar()
          }
        } catch {
          boton.disabled = false
          boton.textContent = 'Ver reacción del enjambre'
          panel.avisar('El motor no respondió. Intenta de nuevo.')
        }
      })
    })
  }

  async function recargar() {
    try {
      render(await cargarDatos())
    } catch {
      /* el muro anterior sigue en pantalla: nunca una página en blanco */
    }
  }

  // el mando del muro para la navegación (abrir, plegar, ir al Pulso)
  const mando = {
    recargar,
    detenerReplay: () => replay.detener(),
    abrir: () => fijarPlegado(false),
    plegar: () => fijarPlegado(true),
    irAlPulso: () => {
      fijarPlegado(false)
      contenedor.querySelector('.pulso')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    },
  }

  // ---------- arranque ----------
  if (!api) {
    renderAviso('Modo demo local: escribe un titular abajo y suéltalo al enjambre.')
    return { ...mando, recargar: async () => {} }
  }
  try {
    const datos = await cargarDatos()
    render(datos)
    fijarModo?.('motor real') // el muro viene de la caché del motor
    // la portada del día se anima en loop suave detrás del muro
    const portada = datos.tarjetas.find((t) => t.destacada && t.sim_id)
    if (portada && !reducirMovimiento) {
      try {
        await replay.cargar(`${api}/api/simulacion/${portada.sim_id}/replay`)
        replay.reproducir({ bucle: true })
      } catch { /* sin replay: el enjambre queda en su calma dorada */ }
    }
  } catch {
    renderAviso('El motor descansa en este momento. Mostrando el enjambre en modo demo — escribe un titular abajo.')
  }

  return mando
}
