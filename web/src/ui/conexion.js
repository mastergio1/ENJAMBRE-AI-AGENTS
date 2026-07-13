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
  async simular(titular, { alInicio, alTick, alFin, alLimite, alDespertar }, extras = {}) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.ws = await this._conectarConPaciencia(alDespertar)
    }
    this.ws.onmessage = (evento) => {
      if (typeof evento.data === 'string') {
        const mensaje = JSON.parse(evento.data)
        if (mensaje.tipo === 'inicio') alInicio(mensaje)
        else if (mensaje.tipo === 'fin') alFin(mensaje.reporte, mensaje.sim_id)
        else if (mensaje.tipo === 'limite') alLimite?.(mensaje.mensaje)
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
    this.ws.send(JSON.stringify({ tipo: 'simular', titular, seed, ...extras }))
  }

  /**
   * Modo observatorio: abre una sesión continua donde el enjambre sigue
   * vivo. Devuelve un mando con soltarNoticia(titular) y detener().
   */
  async observatorio(titular, { alInicio, alTick, alLimite, alFin, alDespertar }) {
    const ws = await this._conectarConPaciencia(alDespertar)
    this.wsObs = ws
    ws.onmessage = (evento) => {
      if (typeof evento.data === 'string') {
        const m = JSON.parse(evento.data)
        if (m.tipo === 'inicio') alInicio?.(m)
        else if (m.tipo === 'limite') alLimite?.(m.mensaje)
        else if (m.tipo === 'observatorio-fin') alFin?.()
      } else {
        const v = new DataView(evento.data)
        alTick(v.getFloat32(0, true), v.getUint32(4, true), new Int8Array(evento.data, 8))
      }
    }
    ws.send(JSON.stringify({ tipo: 'observatorio', titular, seed: Math.floor(Math.random() * 2_000_000_000) }))
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
