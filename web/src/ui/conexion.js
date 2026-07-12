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

  _conectar() {
    return new Promise((resolver, rechazar) => {
      const ws = new WebSocket(this.url)
      ws.binaryType = 'arraybuffer'
      const temporizador = setTimeout(() => {
        ws.close()
        rechazar(new Error('el motor no respondió a tiempo'))
      }, 3000)
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

  /** Envía el titular y entrega los eventos: alInicio, alTick, alFin, alLimite. */
  async simular(titular, { alInicio, alTick, alFin, alLimite }, extras = {}) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.ws = await this._conectar()
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
    this.ws.send(JSON.stringify({ tipo: 'simular', titular, ...extras }))
  }

  /**
   * Modo observatorio: abre una sesión continua donde el enjambre sigue
   * vivo. Devuelve un mando con soltarNoticia(titular) y detener().
   */
  async observatorio(titular, { alInicio, alTick, alLimite, alFin }) {
    const ws = await this._conectar()
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
    ws.send(JSON.stringify({ tipo: 'observatorio', titular }))
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
