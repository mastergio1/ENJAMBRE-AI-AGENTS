// La guía rápida: "¿Cómo funciona El Enjambre?" — para el visitante que
// llega sin contexto (retail curioso). Lenguaje llano, con analogías, y bajo
// la línea CMF: es una simulación educativa, NUNCA asesoría ni predicción.
//
// Se abre desde cualquier elemento con [data-guia] (el botón flotante y el
// enlace del muro) y, la primera vez que alguien entra, se muestra sola.

const CLAVE_VISTA = 'enjambre_guia_vista'

const CONTENIDO = `
  <button class="guia-cerrar" aria-label="cerrar la guía">×</button>
  <p class="guia-eyebrow">Guía rápida · 1 minuto</p>
  <h2 id="guia-titulo">¿Cómo funciona El Enjambre?</h2>
  <p class="guia-intro">
    El Enjambre es un <strong>simulador</strong>: 5.000 inversionistas de mentira
    —hechos con inteligencia artificial— leen una noticia y reaccionan como lo
    haría una multitud real. No adivina el futuro del mercado: te muestra
    <strong>cómo se comporta una manada</strong> cuando llega una noticia.
  </p>

  <div class="cruce" aria-hidden="true"></div>

  <section class="guia-seccion">
    <h3>Cómo usarlo</h3>
    <ol class="guia-pasos">
      <li><span class="n">1</span><span class="t">Escribe un titular abajo (o toca uno de los ejemplos). Ej: <em>«la Fed sube las tasas»</em>.</span></li>
      <li><span class="n">2</span><span class="t">Toca <strong>«Soltar al enjambre»</strong>.</span></li>
      <li><span class="n">3</span><span class="t">Mira reaccionar a los 5.000 en vivo. Al terminar, aparece un pequeño reporte.</span></li>
    </ol>
  </section>

  <section class="guia-seccion">
    <h3>Qué significan los colores</h3>
    <ul class="guia-colores">
      <li><span class="pt" style="background:#4f9e86"></span><span><b>Verde</b> — está comprando (optimismo).</span></li>
      <li><span class="pt" style="background:#c47b7b"></span><span><b>Rosa</b> — está vendiendo (miedo).</span></li>
      <li><span class="pt" style="background:#5c574f"></span><span><b>Grafito</b> — en calma, sin decidir.</span></li>
      <li><span class="pt" style="background:#e3c565"></span><span><b>Dorado</b> — los 100 <b>líderes de opinión</b>. Pasa el cursor (o toca) uno para leer qué dijo.</span></li>
    </ul>
  </section>

  <section class="guia-seccion">
    <h3>Qué significa el movimiento</h3>
    <p>Las partículas que <strong>suben</strong> están comprando; las que
    <strong>se hunden</strong>, vendiendo. Cuando la manada se asusta, verás
    <strong>estelas largas</strong> y el fondo se tiñe de rosa: es turbulencia.</p>
  </section>

  <section class="guia-seccion">
    <h3>Qué significan los números</h3>
    <dl class="guia-numeros">
      <dt>Precio</dt>
      <dd>Arriba a la izquierda. Empieza en <strong>100</strong> (el punto de partida). Emerge de todas las compras y ventas: si suben los compradores, sube; si mandan los vendedores, baja.</dd>
      <dt>Dirección</dt>
      <dd>Cuánto se movió el precio en total (ej: <em>−3%</em>).</dd>
      <dt>Mínimo</dt>
      <dd>Qué tan abajo llegó en el peor momento del susto.</dd>
      <dt>Agitación / volatilidad</dt>
      <dd>Qué tan nerviosa estuvo la manada: bajo, medio o alto.</dd>
      <dt>fps</dt>
      <dd>Solo un dato técnico (qué tan fluida va tu pantalla). Puedes ignorarlo.</dd>
    </dl>
  </section>

  <section class="guia-seccion">
    <h3>Las voces del enjambre</h3>
    <p>Los dorados son 8 personalidades distintas —el pesimista, el eufórico, el
    que va contra la corriente…—. Cada uno interpreta la misma noticia a su
    manera y contagia a sus seguidores. Ahí nace el contagio que ves. Pasa el
    cursor por un dorado para leer su frase.</p>
  </section>

  <p class="guia-descargo">Simulación educativa de comportamiento de masas con agentes de IA. No constituye asesoría ni recomendación de inversión.</p>
  <button class="guia-listo">Entendido — quiero probar</button>
`

/** Monta el botón flotante y el panel de la guía. Devuelve { abrir, cerrar }. */
export function montarGuia() {
  const boton = document.createElement('button')
  boton.className = 'guia-boton'
  boton.setAttribute('data-guia', '')
  boton.setAttribute('aria-haspopup', 'dialog')
  boton.setAttribute('aria-label', '¿Cómo funciona?')
  // el texto va en su propio nodo para poder ocultarlo en móvil (queda el ?)
  boton.innerHTML = '<span aria-hidden="true">?</span><em class="guia-boton-texto">¿Cómo funciona?</em>'

  const capa = document.createElement('div')
  capa.id = 'guia'
  capa.className = 'guia'
  capa.hidden = true
  capa.setAttribute('role', 'dialog')
  capa.setAttribute('aria-modal', 'true')
  capa.setAttribute('aria-labelledby', 'guia-titulo')
  capa.innerHTML = `<div class="guia-panel">${CONTENIDO}</div>`

  document.body.append(boton, capa)

  let ultimoFoco = null

  function abrir() {
    ultimoFoco = document.activeElement
    capa.hidden = false
    document.body.classList.add('guia-abierta')
    capa.querySelector('.guia-cerrar')?.focus()
    try { localStorage.setItem(CLAVE_VISTA, '1') } catch { /* modo privado: da igual */ }
  }

  function cerrar({ alCampo = false } = {}) {
    capa.hidden = true
    document.body.classList.remove('guia-abierta')
    // devuelve el foco a donde estaba (accesibilidad); o al campo si van a probar
    const campo = document.getElementById('campo-titular')
    if (alCampo && campo) campo.focus()
    else ultimoFoco?.focus?.()
  }

  // abrir desde cualquier [data-guia]; cerrar con ×, "entendido", fondo o Esc
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-guia]')) { abrir(); return }
    if (e.target.closest('.guia-cerrar')) { cerrar(); return }
    if (e.target.closest('.guia-listo')) { cerrar({ alCampo: true }); return }
    if (e.target === capa) cerrar() // clic en el fondo oscuro
  })
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !capa.hidden) cerrar()
  })

  // primera visita: la guía saluda sola (salvo enlaces profundos a contenido)
  const params = new URLSearchParams(location.search)
  const enlaceProfundo = params.get('sim') || location.pathname.startsWith('/duelo') ||
    location.pathname.startsWith('/archivo')
  let vista = false
  try { vista = localStorage.getItem(CLAVE_VISTA) === '1' } catch { /* nada */ }
  if (!vista && !enlaceProfundo) {
    setTimeout(abrir, 900) // deja respirar al enjambre un momento antes
  }

  return { abrir, cerrar }
}
