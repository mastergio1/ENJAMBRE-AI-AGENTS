// El tour de bienvenida — cinco pasos de la mano, solo la primera visita.
// Distinto de la guía (el "?"): el tour señala las piezas EN la pantalla.

const CLAVE = 'enjambre-tour-visto'

const PASOS = [
  { sel: '#form-noticia', titulo: 'Escribe una noticia',
    texto: 'Cualquier titular del mercado. Los 5.000 inversionistas simulados la leerán y reaccionarán en vivo.' },
  { sel: '.chips', titulo: 'O usa un ejemplo listo',
    texto: 'Escenarios preparados para soltar con un toque.' },
  { sel: '.hud', titulo: 'El pulso del mercado',
    texto: 'El precio simulado late aquí, con su mini-gráfico.' },
  { sel: '#escena', titulo: 'Los faros dorados', centrado: true,
    texto: 'Son los 100 líderes de opinión con IA. Toca uno para leer su frase. Puedes girar la escena arrastrando y acercarte con dos dedos (o la rueda).' },
  { sel: '.navegacion', titulo: 'Y para moverte',
    texto: 'El muro trae las noticias del día ya simuladas; el archivo guarda la historia; el duelo enfrenta dos escenarios.' },
]

export function tourVisto() {
  try { return localStorage.getItem(CLAVE) === '1' } catch { return true }
}

export function iniciarTour() {
  const capa = document.createElement('div')
  capa.className = 'tour'
  capa.innerHTML = `
    <div class="tour-halo" hidden></div>
    <div class="tour-carta" role="dialog" aria-label="tour de bienvenida">
      <div class="tour-paso"></div>
      <h3></h3>
      <p></p>
      <div class="tour-botones">
        <button class="tour-saltar">Saltar</button>
        <button class="tour-sigue">Siguiente →</button>
      </div>
    </div>`
  document.body.appendChild(capa)

  const halo = capa.querySelector('.tour-halo')
  const carta = capa.querySelector('.tour-carta')
  let indice = 0

  function pintar() {
    const paso = PASOS[indice]
    const objetivo = document.querySelector(paso.sel)
    capa.querySelector('.tour-paso').textContent = `${indice + 1} / ${PASOS.length}`
    capa.querySelector('h3').textContent = paso.titulo
    capa.querySelector('p').textContent = paso.texto
    capa.querySelector('.tour-sigue').textContent =
      indice === PASOS.length - 1 ? '¡A jugar!' : 'Siguiente →'

    if (paso.centrado || !objetivo) {
      halo.hidden = true
    } else {
      const caja = objetivo.getBoundingClientRect()
      halo.hidden = false
      halo.style.left = `${caja.left - 8}px`
      halo.style.top = `${caja.top - 8}px`
      halo.style.width = `${caja.width + 16}px`
      halo.style.height = `${caja.height + 16}px`
    }
    // la tarjeta se pone donde el objetivo no está (arriba o abajo)
    const enAbajo = objetivo && objetivo.getBoundingClientRect().top > window.innerHeight / 2
    carta.classList.toggle('arriba', Boolean(enAbajo))
  }

  function terminar() {
    try { localStorage.setItem(CLAVE, '1') } catch { /* modo privado */ }
    capa.remove()
    window.removeEventListener('resize', pintar)
    document.removeEventListener('keydown', alTeclado)
  }

  function alTeclado(e) {
    if (e.key === 'Escape') terminar()
  }

  capa.querySelector('.tour-saltar').addEventListener('click', terminar)
  capa.querySelector('.tour-sigue').addEventListener('click', () => {
    indice += 1
    if (indice >= PASOS.length) terminar()
    else pintar()
  })
  window.addEventListener('resize', pintar)
  document.addEventListener('keydown', alTeclado)
  pintar()
}
