// El enjambre 3D: 5.000 inversionistas + 100 líderes en 3 draw calls
// (instanced rendering). Geometrías y materiales se crean UNA vez;
// nada de objetos nuevos dentro del loop de animación.

import * as THREE from 'three'
import { TIPOS, generarEnjambre } from './datos.js'
import { analizarTitular } from './escenario.js'

// paleta editorial (nada de colores puros saturados)
const NEUTRO = new THREE.Color('#57534a')   // gris oliva apagado
const COMPRA = new THREE.Color('#4fae7f')   // verde salvia
const VENTA = new THREE.Color('#c4472a')    // rojo teja profundo
const LIDER = new THREE.Color('#e3c565')    // dorado

const _dummy = new THREE.Object3D()
const _color = new THREE.Color()

export class Enjambre {
  constructor(semilla = 7) {
    const { agentes, lideres, rng } = generarEnjambre(semilla)
    this.agentes = agentes
    this.lideres = lideres
    this.rng = rng
    this.grupo = new THREE.Group()
    this.precio = 100
    this.seriePrecio = [100]
    this._ultimaMuestra = 0
    this.sentimientoGlobal = 0
    this.modoRemoto = false  // true: el motor real manda por WebSocket

    this._construirClusters()
    this._construirParticulas()
    this._construirLideres()
  }

  // ---------- construcción ----------

  _construirClusters() {
    // cada tipo vive en un cluster; centros en espiral de ángulo áureo
    this.clusters = TIPOS.map((tipo, i) => {
      const angulo = i * 2.39996
      const radio = 4.5 + 9 * Math.sqrt(i / TIPOS.length)
      return {
        centro: new THREE.Vector3(
          Math.cos(angulo) * radio,
          (this.rng() - 0.5) * 3,
          Math.sin(angulo) * radio,
        ),
        radio: 1.0 + 3.4 * Math.sqrt(tipo.cantidad / 2000),
      }
    })
  }

  _construirParticulas() {
    const n = this.agentes.length
    const geometria = new THREE.IcosahedronGeometry(0.06, 0)
    const material = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.9 })
    this.malla = new THREE.InstancedMesh(geometria, material, n)
    this.malla.instanceMatrix.setUsage(THREE.DynamicDrawUsage)

    // orden de dibujo barajado: al recortar instancias (gobernador de fps)
    // se pierde una muestra pareja del enjambre, no un tipo completo
    this.orden = [...Array(n).keys()]
    for (let i = n - 1; i > 0; i--) {
      const j = Math.floor(this.rng() * (i + 1))
      ;[this.orden[i], this.orden[j]] = [this.orden[j], this.orden[i]]
    }

    // parámetros de órbita por partícula (planos: rápido de leer por frame)
    this.p = {
      centro: new Float32Array(n * 3),
      ejeU: new Float32Array(n * 3),
      ejeV: new Float32Array(n * 3),
      radioA: new Float32Array(n),
      radioB: new Float32Array(n),
      velocidad: new Float32Array(n),
      fase: new Float32Array(n),
      escala: new Float32Array(n),
    }

    for (let i = 0; i < n; i++) {
      const agente = this.agentes[i]
      const cluster = this.clusters[agente.tipo]
      // plano orbital propio: dos ejes ortogonales aleatorios
      const normal = new THREE.Vector3(this.rng() - 0.5, (this.rng() - 0.5) * 2.2, this.rng() - 0.5).normalize()
      const u = new THREE.Vector3(1, 0, 0).cross(normal).normalize()
      if (u.lengthSq() < 0.01) u.set(0, 0, 1)
      const v = normal.clone().cross(u).normalize()
      const r = cluster.radio * (0.25 + 0.75 * Math.sqrt(this.rng()))

      this.p.centro.set([cluster.centro.x, cluster.centro.y, cluster.centro.z], i * 3)
      this.p.ejeU.set([u.x, u.y, u.z], i * 3)
      this.p.ejeV.set([v.x, v.y, v.z], i * 3)
      this.p.radioA[i] = r
      this.p.radioB[i] = r * (0.55 + this.rng() * 0.45)
      this.p.velocidad[i] = (0.05 + this.rng() * 0.12) * (this.rng() < 0.5 ? 1 : -1)
      this.p.fase[i] = this.rng() * Math.PI * 2
      // tamaño = capital (escala logarítmica para que los 100x no tapen todo)
      this.p.escala[i] = 0.65 + 0.55 * Math.log10(1 + agente.capital)

      this.malla.setColorAt(i, _variarColor(NEUTRO, this.rng, 0.08))
    }
    this.malla.instanceColor.needsUpdate = true
    this.grupo.add(this.malla)
  }

  _construirLideres() {
    const n = this.lideres.length
    const geoLider = new THREE.IcosahedronGeometry(0.17, 1)
    const matLider = new THREE.MeshBasicMaterial()
    this.mallaLideres = new THREE.InstancedMesh(geoLider, matLider, n)
    this.mallaLideres.instanceMatrix.setUsage(THREE.DynamicDrawUsage)

    const geoHalo = new THREE.IcosahedronGeometry(0.34, 1)
    const matHalo = new THREE.MeshBasicMaterial({
      color: LIDER, transparent: true, opacity: 0.22,
      blending: THREE.AdditiveBlending, depthWrite: false,
    })
    this.mallaHalos = new THREE.InstancedMesh(geoHalo, matHalo, n)
    this.mallaHalos.instanceMatrix.setUsage(THREE.DynamicDrawUsage)

    this.pl = { centro: new Float32Array(n * 3), fase: new Float32Array(n), velocidad: new Float32Array(n) }
    const tipoIndice = Object.fromEntries(TIPOS.map((t, i) => [t.id, i]))
    for (let i = 0; i < n; i++) {
      const cluster = this.clusters[tipoIndice[this.lideres[i].tipoAncla]]
      // el líder flota sobre su cluster de seguidores, como un faro
      const angulo = this.rng() * Math.PI * 2
      const r = cluster.radio * (0.4 + this.rng() * 0.5)
      this.pl.centro.set([
        cluster.centro.x + Math.cos(angulo) * r,
        cluster.centro.y + 0.8 + this.rng() * 1.2,
        cluster.centro.z + Math.sin(angulo) * r,
      ], i * 3)
      this.pl.fase[i] = this.rng() * Math.PI * 2
      this.pl.velocidad[i] = 0.3 + this.rng() * 0.4
      this.mallaLideres.setColorAt(i, LIDER.clone())
    }
    this.mallaLideres.instanceColor.needsUpdate = true
    this.grupo.add(this.mallaLideres, this.mallaHalos)
  }

  // ---------- la noticia ----------

  /** El enjambre lee un titular: los líderes forman señal y la ola se agenda. */
  aplicarTitular(titular, ahora) {
    const sentimiento = analizarTitular(titular, this.lideres, this.rng)
    this.sentimientoGlobal = sentimiento
    for (const agente of this.agentes) {
      if (agente.lider >= 0) {
        const lider = this.lideres[agente.lider]
        // retardo 1er salto + a veces 2º salto (el rumor de par en par),
        // atenuación 0.7 por salto — la ola, no un salto feo
        const segundoSalto = this.rng() < 0.4
        agente.tLlegada = ahora + 0.4 + this.rng() * 2.0 + (segundoSalto ? 0.9 + this.rng() * 1.5 : 0)
        const atenuacion = segundoSalto ? 0.49 : 0.7
        const cruda = lider.senal * lider.confianza * atenuacion * agente.sensibilidad
        agente.sentObjetivo = Math.max(-1, Math.min(1, cruda + (this.rng() - 0.5) * 0.12))
      } else if (agente.sensibilidad > 0) {
        // institucionales: no escuchan rumores; reaccionan tarde, al precio
        agente.tLlegada = ahora + 2.5 + this.rng() * 3.5
        agente.sentObjetivo = sentimiento * agente.sensibilidad * 0.5
      }
    }
    return sentimiento
  }

  /** El motor real dicta el estado: sentimiento por agente + precio. */
  aplicarEstadoRemoto(precio, sentimientos) {
    const nReglas = this.agentes.length
    for (let i = 0; i < nReglas; i++) {
      const agente = this.agentes[i]
      agente.sentObjetivo = sentimientos[i] / 127
      agente.tLlegada = -1 // ya llegó: el retardo lo puso el motor
    }
    for (let l = 0; l < this.lideres.length; l++) {
      this.lideres[l].senal = sentimientos[nReglas + l] / 127
    }
    this.precio = precio
  }

  /** Las opiniones de los líderes reales (para el hover). */
  fijarLideresRemotos(lideres) {
    lideres.forEach((datos, i) => {
      if (i >= this.lideres.length) return
      this.lideres[i].senal = datos.senal
      this.lideres[i].confianza = datos.confianza
      this.lideres[i].frase = datos.frase
    })
  }

  // ---------- animación ----------

  actualizar(t, dt) {
    const n = this.malla.count
    const respiracion = 1 + 0.045 * Math.sin(t * 0.35)

    for (let d = 0; d < n; d++) {
      const i = this.orden[d]
      const agente = this.agentes[i]

      // el rumor llega, el sentimiento se acerca a su objetivo y luego se agota
      if (t >= agente.tLlegada) {
        agente.sent += (agente.sentObjetivo - agente.sent) * Math.min(1, dt * 2.5)
        // en modo remoto el motor refresca el objetivo; aquí no se decae
        if (!this.modoRemoto) agente.sentObjetivo *= Math.exp(-dt / 9)
      }
      const s = agente.sent
      const intensidad = Math.abs(s)

      // órbita elíptica propia; la emoción acelera el vuelo
      const angulo = this.p.fase[i] + t * this.p.velocidad[i] * (1 + 1.6 * intensidad)
      const cosA = Math.cos(angulo) * this.p.radioA[i] * respiracion
      const sinA = Math.sin(angulo) * this.p.radioB[i] * respiracion
      const o = i * 3
      _dummy.position.set(
        this.p.centro[o] + this.p.ejeU[o] * cosA + this.p.ejeV[o] * sinA,
        // compra = asciende · venta = se hunde
        this.p.centro[o + 1] + this.p.ejeU[o + 1] * cosA + this.p.ejeV[o + 1] * sinA + s * 1.5,
        this.p.centro[o + 2] + this.p.ejeU[o + 2] * cosA + this.p.ejeV[o + 2] * sinA,
      )
      const escala = this.p.escala[i] * (1 + 0.25 * intensidad)
      _dummy.scale.setScalar(escala)
      _dummy.updateMatrix()
      this.malla.setMatrixAt(d, _dummy.matrix)

      // color = sentimiento (verde compra ← neutro → rojo venta)
      _color.copy(NEUTRO).lerp(s > 0 ? COMPRA : VENTA, Math.pow(intensidad, 0.7))
      this.malla.setColorAt(d, _color)
    }
    this.malla.instanceMatrix.needsUpdate = true
    this.malla.instanceColor.needsUpdate = true

    // líderes: flotan y pulsan según su convicción
    for (let i = 0; i < this.lideres.length; i++) {
      const lider = this.lideres[i]
      if (!this.modoRemoto) lider.senal *= Math.exp(-dt / 14) // su opinión se apaga
      const o = i * 3
      const bob = Math.sin(t * this.pl.velocidad[i] + this.pl.fase[i]) * 0.25
      _dummy.position.set(this.pl.centro[o], this.pl.centro[o + 1] + bob + lider.senal * 1.2, this.pl.centro[o + 2])
      _dummy.scale.setScalar(1)
      _dummy.updateMatrix()
      this.mallaLideres.setMatrixAt(i, _dummy.matrix)

      const pulso = 1 + 0.18 * Math.sin(t * 2.2 + this.pl.fase[i]) + 0.9 * Math.abs(lider.senal)
      _dummy.scale.setScalar(pulso)
      _dummy.updateMatrix()
      this.mallaHalos.setMatrixAt(i, _dummy.matrix)

      _color.copy(LIDER).lerp(lider.senal > 0 ? COMPRA : VENTA, Math.abs(lider.senal) * 0.55)
      this.mallaLideres.setColorAt(i, _color)
    }
    this.mallaLideres.instanceMatrix.needsUpdate = true
    this.mallaHalos.instanceMatrix.needsUpdate = true
    this.mallaLideres.instanceColor.needsUpdate = true

    // precio: en modo remoto lo dicta el motor; en local emerge del
    // sentimiento promedio del enjambre (demo sin backend)
    let suma = 0
    for (const a of this.agentes) suma += a.sent
    const sentMedio = suma / this.agentes.length
    if (!this.modoRemoto) {
      this.precio *= 1 + sentMedio * dt * 0.09 + (this.rng() - 0.5) * dt * 0.004
    }
    if (t - this._ultimaMuestra > 0.15) {
      this._ultimaMuestra = t
      this.seriePrecio.push(this.precio)
      if (this.seriePrecio.length > 400) this.seriePrecio.shift()
    }
    this.sentimientoMedio = sentMedio

    // rotación lenta de todo el enjambre: hipnosis
    this.grupo.rotation.y = t * 0.03
  }

  /** Gobernador de fps: recorta o restaura partículas dibujadas. */
  fijarProporcion(proporcion) {
    this.malla.count = Math.max(1200, Math.round(this.agentes.length * proporcion))
  }
}

function _variarColor(base, rng, cuanto) {
  return base.clone().offsetHSL((rng() - 0.5) * cuanto, (rng() - 0.5) * cuanto, (rng() - 0.5) * cuanto)
}
