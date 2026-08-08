// La puerta de correo (gancho de crecimiento): en público se pide UNA vez para
// soltar tu propio titular al enjambre, y de paso quedas suscrito gratis a El
// Pulso. Sin login, sin contraseñas. Devuelve el correo (string) o null si el
// visitante cierra. La estética sigue la del enjambre (tinta + dorado).

const _EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

export function pedirCorreo(mensaje) {
  return new Promise((resolver) => {
    let resuelto = false
    const capa = document.createElement('div')
    capa.setAttribute('role', 'dialog')
    capa.setAttribute('aria-modal', 'true')
    capa.setAttribute('aria-label', 'Deja tu correo para soltar un titular')
    Object.assign(capa.style, {
      position: 'fixed', inset: '0', background: 'rgba(11,14,20,0.72)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: '9999', padding: '20px', boxSizing: 'border-box',
    })
    capa.innerHTML = `
      <div style="position:relative;background:#1b1916;border:1px solid rgba(227,197,101,0.3);
        border-radius:10px;max-width:420px;width:100%;padding:28px;color:#f3eee8;
        font-family:system-ui,-apple-system,sans-serif;box-shadow:0 30px 80px -30px rgba(0,0,0,0.8);">
        <button type="button" data-cerrar aria-label="cerrar"
          style="position:absolute;top:12px;right:14px;background:none;border:none;color:#8a867e;
          font-size:22px;line-height:1;cursor:pointer;">×</button>
        <div style="font-family:Georgia,serif;font-size:24px;color:#e3c565;font-weight:bold;margin-bottom:6px;">Suéltalo al enjambre 🐝</div>
        <p style="font-size:14px;line-height:1.5;color:#cfc9bd;margin:0 0 16px;"></p>
        <form>
          <input type="email" required placeholder="tu@correo.com" autocomplete="email" inputmode="email"
            style="width:100%;box-sizing:border-box;padding:12px 14px;border-radius:6px;
            border:1px solid rgba(243,238,232,0.2);background:#14120f;color:#f3eee8;font-size:15px;" />
          <div data-err style="color:#d99a9a;font-size:12px;min-height:16px;margin:6px 2px 0;"></div>
          <button type="submit"
            style="width:100%;margin-top:6px;background:#e3c565;color:#1b1916;border:none;border-radius:6px;
            padding:13px;font-weight:bold;font-size:15px;cursor:pointer;">Ver el enjambre reaccionar →</button>
        </form>
        <p style="font-size:11px;color:#8a867e;line-height:1.5;margin:14px 0 0;">
          Un solo dato, sin contraseñas. Puedes darte de baja en un clic.
          No es asesoría ni recomendación de inversión.</p>
      </div>`

    capa.querySelector('p').textContent = mensaje ||
      'Deja tu correo para soltar tu propio titular. De paso te suscribes gratis a El Pulso, el diario del enjambre.'

    const input = capa.querySelector('input')
    const err = capa.querySelector('[data-err]')
    const form = capa.querySelector('form')

    function cerrar(valor) {
      if (resuelto) return
      resuelto = true
      document.removeEventListener('keydown', alTecla)
      capa.remove()
      resolver(valor)
    }
    function alTecla(e) { if (e.key === 'Escape') cerrar(null) }

    form.addEventListener('submit', (e) => {
      e.preventDefault()
      const email = input.value.trim().toLowerCase()
      if (!_EMAIL.test(email) || email.length > 200) {
        err.textContent = 'Escribe un correo válido (ej: tu@correo.com).'
        input.focus()
        return
      }
      cerrar(email)
    })
    capa.querySelector('[data-cerrar]').addEventListener('click', () => cerrar(null))
    capa.addEventListener('click', (e) => { if (e.target === capa) cerrar(null) })
    document.addEventListener('keydown', alTecla)

    document.body.appendChild(capa)
    input.focus()
  })
}
