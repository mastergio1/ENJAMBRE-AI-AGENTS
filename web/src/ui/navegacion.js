// La barra de navegación — editorial y discreta, siempre a mano.
// Vive por encima de los overlays (archivo, duelo) para que el visitante
// nunca quede "atrapado" en una sección; solo la guía modal la cubre.

export function montarNavegacion(acciones) {
  const barra = document.createElement('nav')
  barra.className = 'navegacion'
  barra.setAttribute('aria-label', 'principal')
  barra.innerHTML = `
    <button class="nav-marca" data-nav="inicio" aria-label="El Enjambre — inicio">El Enjambre</button>
    <div class="nav-enlaces">
      <button data-nav="inicio">Inicio</button>
      <button data-nav="muro">Muro</button>
      <button data-nav="archivo">Archivo</button>
      <button data-nav="duelo">Duelo</button>
      <button data-nav="pulso">El Pulso</button>
    </div>`
  barra.addEventListener('click', (evento) => {
    const destino = evento.target.closest('[data-nav]')?.dataset.nav
    if (destino && acciones[destino]) {
      barra.querySelectorAll('[data-nav]').forEach((b) =>
        b.classList.toggle('activo', b.dataset.nav === destino && b.className !== 'nav-marca'))
      acciones[destino]()
    }
  })
  document.body.appendChild(barra)
  return barra
}
