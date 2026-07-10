// Conexión con el motor real (engine/server.py) por WebSocket.
// Si el motor no está disponible, main.js degrada al modo demo local.

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

  /** Envía el titular y entrega los eventos: alInicio, alTick, alFin. */
  async simular(titular, { alInicio, alTick, alFin }) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.ws = await this._conectar()
    }
    this.ws.onmessage = (evento) => {
      if (typeof evento.data === 'string') {
        const mensaje = JSON.parse(evento.data)
        if (mensaje.tipo === 'inicio') alInicio(mensaje)
        else if (mensaje.tipo === 'fin') alFin(mensaje.reporte)
      } else {
        const vista = new DataView(evento.data)
        alTick(
          vista.getFloat32(0, true),                 // precio
          vista.getUint32(4, true),                  // tick
          new Int8Array(evento.data, 8),             // sentimiento por agente
        )
      }
    }
    this.ws.send(JSON.stringify({ tipo: 'simular', titular }))
  }
}
