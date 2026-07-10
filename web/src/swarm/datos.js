// Datos falsos de la Etapa 3: la misma mezcla de 5.000 agentes del motor
// (engine/config/agentes.json), generada en el navegador. En la Etapa 4
// estos datos llegarán en vivo por WebSocket.

export const TIPOS = [
  { id: 'fundamentalista', nombre: 'Fundamentalista', cantidad: 200, capital: 50, social: false, sensibilidad: 0.25 },
  { id: 'quant',           nombre: 'Quant institucional', cantidad: 120, capital: 40, social: false, sensibilidad: 0.3 },
  { id: 'pasivo',          nombre: 'Fondo pasivo', cantidad: 80, capital: 60, social: false, sensibilidad: 0.0 },
  { id: 'market_maker',    nombre: 'Market maker', cantidad: 5, capital: 100, social: false, sensibilidad: 0.15 },
  { id: 'twap',            nombre: 'Ejecutor TWAP', cantidad: 15, capital: 30, social: false, sensibilidad: 0.05 },
  { id: 'arbitrajista',    nombre: 'Arbitrajista', cantidad: 30, capital: 20, social: false, sensibilidad: 0.2 },
  { id: 'noise',           nombre: 'Noise trader', cantidad: 2000, capital: 1, social: true, sensibilidad: 0.45 },
  { id: 'manada',          nombre: 'Manada', cantidad: 900, capital: 1, social: true, sensibilidad: 1.0 },
  { id: 'fomo',            nombre: 'FOMO retail', cantidad: 600, capital: 1, social: true, sensibilidad: 1.1 },
  { id: 'miedoso',         nombre: 'Miedoso', cantidad: 500, capital: 1, social: true, sensibilidad: 1.2 },
  { id: 'contrarian',      nombre: 'Contrarian', cantidad: 250, capital: 1.5, social: true, sensibilidad: 0.7 },
  { id: 'buyhold',         nombre: 'Buy & hold', cantidad: 200, capital: 2, social: false, sensibilidad: 0.1 },
]

export const ARQUETIPOS = [
  { id: 'institucional_frio', nombre: 'El Institucional Frío', cantidad: 15, sigue: ['buyhold', 'contrarian'] },
  { id: 'quant_esceptico',    nombre: 'El Quant Escéptico', cantidad: 10, sigue: ['contrarian', 'noise'] },
  { id: 'fomo_evangelista',   nombre: 'El FOMO Evangelista', cantidad: 15, sigue: ['fomo', 'manada'] },
  { id: 'doomer',             nombre: 'El Doomer', cantidad: 15, sigue: ['miedoso'] },
  { id: 'contrarian_sabio',   nombre: 'El Contrarian Sabio', cantidad: 10, sigue: ['contrarian'] },
  { id: 'macro_trader',       nombre: 'El Macro Trader', cantidad: 10, sigue: ['manada', 'noise'] },
  { id: 'influencer_optimista', nombre: 'El Influencer Optimista', cantidad: 15, sigue: ['manada', 'noise'] },
  { id: 'value_paciente',     nombre: 'El Value Paciente', cantidad: 10, sigue: ['buyhold'] },
]

// generador determinístico simple (mulberry32) para poder repetir demos
export function crearRng(semilla) {
  let a = semilla >>> 0
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/** Genera los 5.000 agentes de reglas + 100 líderes con sus posiciones de cluster. */
export function generarEnjambre(semilla = 7) {
  const rng = crearRng(semilla)
  const agentes = []
  const indicePorTipo = {}

  TIPOS.forEach((tipo, t) => {
    indicePorTipo[tipo.id] = []
    for (let i = 0; i < tipo.cantidad; i++) {
      indicePorTipo[tipo.id].push(agentes.length)
      agentes.push({
        tipo: t,
        tipoId: tipo.id,
        capital: tipo.capital * (0.7 + rng() * 0.6),
        social: tipo.social,
        sensibilidad: tipo.sensibilidad * (0.7 + rng() * 0.6),
        lider: -1,          // índice del líder que sigue (si es social)
        sent: 0,            // sentimiento actual ∈ [-1, 1]
        sentObjetivo: 0,
        tLlegada: Infinity, // cuándo le llega el rumor (segundos de escena)
      })
    }
  })

  // líderes: cada uno anclado al cluster de su tipo de seguidor principal
  const lideres = []
  ARQUETIPOS.forEach((arq) => {
    for (let i = 0; i < arq.cantidad; i++) {
      lideres.push({
        arquetipo: arq.id,
        nombre: arq.nombre,
        tipoAncla: arq.sigue[Math.floor(rng() * arq.sigue.length)],
        senal: 0,
        confianza: 0.7,
        frase: '',
      })
    }
  })

  // seguidores: cada agente social sigue a un líder cuyo arquetipo lo incluye
  const lideresPorTipo = {}
  lideres.forEach((lider, li) => {
    const arq = ARQUETIPOS.find((a) => a.id === lider.arquetipo)
    for (const tipoId of arq.sigue) {
      ;(lideresPorTipo[tipoId] ??= []).push(li)
    }
  })
  for (const agente of agentes) {
    const candidatos = lideresPorTipo[agente.tipoId]
    if (agente.social && candidatos) {
      agente.lider = candidatos[Math.floor(rng() * candidatos.length)]
    }
  }

  return { agentes, lideres, rng }
}
