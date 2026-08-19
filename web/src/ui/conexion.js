// Conexión con el motor real (engine/server.py) por WebSocket.
// Si el motor no está disponible, main.js degrada al modo demo local.

/** La base HTTP del motor (para los endpoints /api del muro). */
export function urlApi() {
  const ws =
    import.meta.env.VITE_WS_URL ||
    (['localhost', '127.0.0.1'].includes(location.hostname) ? 'ws://localhost:8000/ws' : null)
  if (!ws) return null
  return ws.replace(/^ws/, 'http').replace(/\/ws$/, '')
}

/** La clave de pruebas privadas: llega en la URL (?acceso=…) y se recuerda
 * en el navegador. Durante las pruebas cerradas, solo quien la trae puede
 * soltar titulares (que gastan IA). El muro y el archivo quedan abiertos. */
export function claveAcceso() {
  try {
    const enUrl = new URLSearchParams(location.search).get('acceso')
    if (enUrl) localStorage.setItem('enjambre-acceso', enUrl)
    return localStorage.getItem('enjambre-acceso') || ''
  } catch {
    return ''
  }
}

/** El correo del visitante (la "puerta de crecimiento"): en público se pide UNA
 * vez para soltar tu propio titular, y de paso quedas suscrito gratis al Pulso.
 * Sin contraseñas, sin cuenta — solo un dato, recordado en el navegador. */
export function correoUsuario() {
  try {
    return localStorage.getItem('enjambre-correo') || ''
  } catch {
    return ''
  }
}

export function guardarCorreo(email) {
  try {
    localStorage.setItem('enjambre-correo', String(email || '').trim().toLowerCase())
  } catch {
    /* modo privado del navegador: da igual */
  }
}

/** El TOKEN Premium desbloqueado (secreto del enlace mágico): eleva el cupo a 40
 * simulaciones/mes. Se recuerda en el navegador y viaja con cada simulación; el
 * motor lo verifica en vivo (si canceló, vuelve a 1/día). Es un token, no el
 * correo: solo lo tiene quien recibió el enlace en su buzón. */
export function tokenPremium() {
  try {
    return localStorage.getItem('enjambre-premium-token') || ''
  } catch {
    return ''
  }
}

export function guardarTokenPremium(token) {
  try {
    localStorage.setItem('enjambre-premium-token', String(token || '').trim())
  } catch {
    /* da igual */
  }
}

export function borrarTokenPremium() {
  try {
    localStorage.removeItem('enjambre-premium-token')
  } catch {
    /* da igual */
  }
}

/** Huella suave del navegador: un id aleatorio, propio de este dispositivo, para
 * que el cupo gratis se cuente por dispositivo y no por IP (una red móvil o una
 * oficina no comparte 1/día). Se crea la primera vez y se recuerda. */
export function clienteId() {
  try {
    let id = localStorage.getItem('enjambre-cid')
    if (!id) {
      id = (crypto?.randomUUID?.() || String(Math.random()).slice(2) + Date.now().toString(36))
      localStorage.setItem('enjambre-cid', id)
    }
    return id
  } catch {
    return ''
  }
}

/** Pide el enlace mágico de desbloqueo para un correo. Respuesta neutra del
 * motor (no revela si es Premium). Devuelve true si la petición salió. */
export async function pedirDesbloqueo(email) {
  const base = urlApi()
  if (!base) return false
  try {
    const r = await fetch(`${base}/api/pulso/desbloqueo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    return r.ok
  } catch {
    return false
  }
}

/** Canjea un token del enlace mágico por el nivel Premium. {premium, limite,
 * periodo} o null si no se pudo verificar. NO consume cupo. */
export async function verificarToken(token) {
  const base = urlApi()
  if (!base) return null
  try {
    const r = await fetch(`${base}/api/pulso/enjambre/verificar?token=${encodeURIComponent(token)}`)
    if (!r.ok) return null
    return await r.json()
  } catch {
    return null
  }
}

export class MotorRemoto {
  constructor(url) {
    this.url = url
    this.ws = null
  }

  _conectar(esperaMs = 8000) {
    return new Promise((resolver, rechazar) => {
      const ws = new WebSocket(this.url)
      ws.binaryType = 'arraybuffer'
      const temporizador = setTimeout(() => {
        ws.close()
        rechazar(new Error('el motor no respondió a tiempo'))
      }, esperaMs)
      ws.onopen = () => {
        clearTimeout(temporizador)
        resolver(ws)
      }
      ws.onerror = () => {
        clearTimeout(temporizador)
        rechazar(new Error('no se pudo conectar con el motor'))
      }
    })
  }

  /**
   * Conecta con paciencia: el motor gratuito de Render se duerme con la
   * inactividad y tarda ~50 s en despertar. Reintenta hasta ~75 s y avisa
   * (alLento) para que la UI diga "despertando el motor…" en vez de caer
   * al demo a los 3 segundos.
   */
  async _conectarConPaciencia(alLento = null) {
    const inicio = Date.now()
    let avisado = false
    for (;;) {
      try {
        return await this._conectar(8000)
      } catch (error) {
        if (!avisado) {
          avisado = true
          alLento?.()
        }
        if (Date.now() - inicio > 75000) throw error
        await new Promise((r) => setTimeout(r, 4000))
      }
    }
  }

  /** Envía el titular y entrega los eventos: alInicio, alTick, alFin, alLimite.
   * La semilla es aleatoria por corrida: dos corridas del mismo titular dan
   * reacciones y voces distintas — el enjambre nunca suena a loro. */
  async simular(titular, { alInicio, alTick, alFin, alLimite, alDespertar, alCorreo }, extras = {}) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.ws = await this._conectarConPaciencia(alDespertar)
    }
    this.ws.onmessage = (evento) => {
      if (typeof evento.data === 'string') {
        const mensaje = JSON.parse(evento.data)
        if (mensaje.tipo === 'inicio') alInicio(mensaje)
        else if (mensaje.tipo === 'fin') alFin(mensaje.reporte, mensaje.sim_id)
        else if (mensaje.tipo === 'limite') alLimite?.(mensaje.mensaje)
        else if (mensaje.tipo === 'privado') alLimite?.(mensaje.mensaje)
        else if (mensaje.tipo === 'correo') alCorreo?.(mensaje.mensaje)   // la puerta pide correo
      } else {
        const vista = new DataView(evento.data)
        alTick(
          vista.getFloat32(0, true),                 // precio
          vista.getUint32(4, true),                  // tick
          new Int8Array(evento.data, 8),             // sentimiento por agente
        )
      }
    }
    const seed = Math.floor(Math.random() * 2_000_000_000)
    this.ws.send(JSON.stringify({
      tipo: 'simular', titular, seed,
      acceso: claveAcceso(), email: correoUsuario(),
      premium_token: tokenPremium(), cid: clienteId(), ...extras,
    }))
  }

  /**
   * Modo observatorio: abre una sesión continua donde el enjambre sigue
   * vivo. Devuelve un mando con soltarNoticia(titular) y detener().
   */
  async observatorio(titular, { alInicio, alTick, alLimite, alFin, alDespertar, alCorreo }) {
    const ws = await this._conectarConPaciencia(alDespertar)
    this.wsObs = ws
    ws.onmessage = (evento) => {
      if (typeof evento.data === 'string') {
        const m = JSON.parse(evento.data)
        if (m.tipo === 'inicio') alInicio?.(m)
        else if (m.tipo === 'limite') alLimite?.(m.mensaje)
        else if (m.tipo === 'privado') alLimite?.(m.mensaje)
        else if (m.tipo === 'correo') alCorreo?.(m.mensaje)
        else if (m.tipo === 'observatorio-fin') alFin?.()
      } else {
        const v = new DataView(evento.data)
        alTick(v.getFloat32(0, true), v.getUint32(4, true), new Int8Array(evento.data, 8))
      }
    }
    ws.send(JSON.stringify({
      tipo: 'observatorio', titular, seed: Math.floor(Math.random() * 2_000_000_000),
      acceso: claveAcceso(), email: correoUsuario(),
      premium_token: tokenPremium(), cid: clienteId(),
    }))
    return {
      soltarNoticia(t) {
        if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ tipo: 'noticia', titular: t }))
      },
      detener() {
        if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ tipo: 'detener' }))
        try { ws.close() } catch { /* ya cerrado */ }
      },
    }
  }
}
