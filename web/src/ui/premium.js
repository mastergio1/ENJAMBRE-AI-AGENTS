// Desbloqueo Premium en El Enjambre: un chip discreto que deja al suscriptor
// de pago de El Pulso elevar su cupo de 1/día a 40 simulaciones al mes. Sin
// cuentas ni contraseñas: escribe su correo, el motor verifica que sea Premium
// y lo recuerda en el navegador. Autónomo — inyecta su propio estilo y DOM.

import { borrarPremium, correoPremium, guardarPremium, verificarPremium } from './conexion.js'

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

const ESTILO = `
.pz-chip{position:fixed;right:16px;bottom:16px;z-index:40;display:inline-flex;align-items:center;gap:7px;
  background:rgba(18,16,13,.82);backdrop-filter:blur(6px);border:1px solid #4a3f22;color:#e3c565;
  font:600 12px/1 'Jost',system-ui,sans-serif;letter-spacing:.3px;padding:9px 14px;border-radius:22px;
  cursor:pointer;transition:border-color .15s,transform .15s}
.pz-chip:hover{border-color:#e3c565;transform:translateY(-1px)}
.pz-chip.on{color:#f4efe6;border-color:#2f7a6f}
.pz-pop{position:fixed;right:16px;bottom:60px;z-index:41;width:290px;max-width:calc(100vw - 32px);
  background:#161009;border:1px solid #4a3f22;border-radius:14px;padding:18px;color:#f4efe6;
  font-family:'Jost',system-ui,sans-serif;box-shadow:0 18px 40px rgba(0,0,0,.5)}
.pz-pop h4{margin:0 0 4px;font-family:'Cormorant Garamond',Georgia,serif;font-size:19px;color:#fbf7ee;font-weight:700}
.pz-pop p{margin:0 0 12px;font-size:13px;line-height:1.5;color:#c7bfb2}
.pz-pop input{width:100%;box-sizing:border-box;padding:11px 13px;border-radius:9px;border:1px solid #4a3f22;
  background:rgba(255,255,255,.05);color:#fbf7ee;font:400 14px 'Jost',sans-serif}
.pz-pop input:focus{outline:none;border-color:#e3c565}
.pz-pop .row{display:flex;gap:8px;margin-top:10px}
.pz-btn{flex:1;border:none;border-radius:9px;padding:11px;font:700 14px 'Jost',sans-serif;cursor:pointer}
.pz-go{background:#e3c565;color:#1b1410}
.pz-x{background:transparent;color:#a8a291;border:1px solid #4a3f22;flex:0 0 auto;padding:11px 14px}
.pz-msg{margin-top:10px;font-size:12.5px;min-height:16px;line-height:1.4}
.pz-msg.ok{color:#7fd6a8}.pz-msg.err{color:#e89b98}
.pz-link{background:none;border:none;color:#a8a291;font:500 12px 'Jost',sans-serif;text-decoration:underline;
  cursor:pointer;padding:0;margin-top:10px}
@media (prefers-reduced-motion: reduce){.pz-chip{transition:none}}
`

function inyectarEstilo() {
  if (document.getElementById('pz-estilo')) return
  const s = document.createElement('style')
  s.id = 'pz-estilo'
  s.textContent = ESTILO
  document.head.appendChild(s)
}

/** Monta el chip de Premium. Idempotente. */
export function montarPremium() {
  inyectarEstilo()
  if (document.querySelector('.pz-chip')) return

  const chip = document.createElement('button')
  chip.className = 'pz-chip'
  chip.type = 'button'
  document.body.appendChild(chip)

  let pop = null

  function pintarChip() {
    const correo = correoPremium()
    if (correo) {
      chip.classList.add('on')
      chip.innerHTML = '⭐ Premium · 40/mes'
      chip.title = correo
    } else {
      chip.classList.remove('on')
      chip.innerHTML = '🔓 ¿Eres Premium?'
      chip.title = 'Desbloquea 40 simulaciones al mes'
    }
  }

  let temporizadorCierre = null

  function cerrar() {
    if (temporizadorCierre) { clearTimeout(temporizadorCierre); temporizadorCierre = null }
    pop?.remove()
    pop = null
  }

  function abrir() {
    if (pop) return cerrar()
    const activo = correoPremium()
    pop = document.createElement('div')
    pop.className = 'pz-pop'
    pop.innerHTML = activo
      ? `<h4>Premium activo ⭐</h4>
         <p>Tienes <b>40 simulaciones al mes</b> con <b>${escapar(activo)}</b>.</p>
         <button class="pz-link" data-salir>Cerrar sesión Premium en este dispositivo</button>`
      : `<h4>Desbloquea tu Premium</h4>
         <p>Suscriptor de El Pulso Premium: escribe tu correo y desbloquea <b>40 simulaciones al mes</b> (el free es 1 al día).</p>
         <input type="email" inputmode="email" placeholder="tu@correo.com" aria-label="Tu correo Premium">
         <div class="row">
           <button class="pz-btn pz-go" data-go>Desbloquear</button>
           <button class="pz-btn pz-x" data-x>Cerrar</button>
         </div>
         <div class="pz-msg" role="status"></div>`
    document.body.appendChild(pop)

    if (activo) {
      pop.querySelector('[data-salir]').addEventListener('click', () => {
        borrarPremium(); pintarChip(); cerrar()
      })
      return
    }

    const input = pop.querySelector('input')
    const msg = pop.querySelector('.pz-msg')
    const go = pop.querySelector('[data-go]')
    input.focus()
    pop.querySelector('[data-x]').addEventListener('click', cerrar)

    async function desbloquear() {
      const correo = (input.value || '').trim().toLowerCase()
      msg.className = 'pz-msg'
      if (!EMAIL.test(correo) || correo.length > 200) {
        msg.textContent = 'Escribe un correo válido.'; msg.classList.add('err'); return
      }
      go.disabled = true; go.textContent = 'Verificando…'
      const estado = await verificarPremium(correo)
      go.disabled = false; go.textContent = 'Desbloquear'
      if (estado && estado.premium) {
        guardarPremium(correo); pintarChip()
        msg.textContent = '¡Listo! Ya tienes 40 simulaciones al mes. 🐝'; msg.classList.add('ok')
        const mio = pop
        temporizadorCierre = setTimeout(() => { if (pop === mio) cerrar() }, 1400)
      } else if (estado) {
        msg.textContent = 'Ese correo no figura como Premium activo. ¿Aún no lo eres?'; msg.classList.add('err')
      } else {
        msg.textContent = 'No pudimos verificar ahora. Intenta en un momento.'; msg.classList.add('err')
      }
    }
    go.addEventListener('click', desbloquear)
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') desbloquear() })
  }

  chip.addEventListener('click', abrir)
  pintarChip()

  // si había un Premium guardado, revalida en silencio: si canceló, vuelve a 3/día
  const guardado = correoPremium()
  if (guardado) {
    verificarPremium(guardado).then((e) => {
      if (e && !e.premium) { borrarPremium(); pintarChip() }
    })
  }
}

function escapar(s) {
  const d = document.createElement('div')
  d.textContent = String(s || '')
  return d.innerHTML
}
