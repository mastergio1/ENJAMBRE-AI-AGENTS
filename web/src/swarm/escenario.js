// Escenarios falsos de la Etapa 3: un mini-analizador léxico (espejo
// simplificado de engine/brains/fallback.py) convierte el titular en
// señales por arquetipo. En la Etapa 4 esto lo hará el motor real.

const FRASES_CLAVE = [
  ['sube las tasas', -0.7], ['alza de tasas', -0.7], ['recorta las tasas', 0.6],
  ['baja las tasas', 0.6], ['guerra comercial', -0.7], ['supera expectativas', 0.7],
]

const PALABRAS = [
  ['desploma', -0.9], ['quiebra', -0.9], ['colapso', -0.9], ['crash', -0.9],
  ['crisis', -0.8], ['recesión', -0.8], ['pánico', -0.8], ['fraude', -0.8],
  ['guerra', -0.7], ['cae', -0.6], ['despidos', -0.6], ['pérdidas', -0.6],
  ['inflación', -0.5], ['riesgo', -0.4], ['máximo histórico', 0.8], ['récord', 0.7],
  ['sube', 0.6], ['alza', 0.6], ['ganancias', 0.6], ['estímulo', 0.6],
  ['recuperación', 0.6], ['crece', 0.5], ['gana', 0.5], ['acuerdo', 0.4],
]

const MACRO = ['fed', 'banco', 'tasas', 'inflación', 'empleo', 'dólar', 'pib', 'recesión', 'liquidez', 'guerra']

export function sentimientoLexico(titular) {
  let texto = titular.toLowerCase()
  let puntaje = 0
  for (const [frase, peso] of FRASES_CLAVE) {
    if (texto.includes(frase)) { puntaje += peso; texto = texto.replaceAll(frase, ' ') }
  }
  if (titular.toLowerCase().includes('tasa') || titular.toLowerCase().includes('interés')) {
    texto = texto.replaceAll('sube', ' ').replaceAll('alza', ' ')
  }
  for (const [palabra, peso] of PALABRAS) {
    if (texto.includes(palabra)) puntaje += peso
  }
  return Math.max(-1, Math.min(1, puntaje / 1.5))
}

const clip = (x, lo = -1, hi = 1) => Math.max(lo, Math.min(hi, x))

// cómo transforma cada arquetipo el sentimiento del titular en su señal,
// y qué frase dice (negativa / neutra / positiva)
const PERSONALIDADES = {
  institucional_frio: {
    senal: (s) => clip(0.4 * s, -0.5, 0.5),
    frases: [
      'Ajustamos flujos de caja proyectados; sin dramatismos.',
      'Sin impacto material en fundamentales. Seguimos.',
      'Mejora marginal en márgenes; posición sin grandes cambios.',
    ],
  },
  quant_esceptico: {
    senal: (s) => clip(-0.5 * s, -0.6, 0.6),
    frases: [
      'El pánico está sobrevendido; apuesto a la reversión.',
      'Ruido estadístico. Nada que operar.',
      'La euforia ya está en el precio; me pongo del otro lado.',
    ],
  },
  fomo_evangelista: {
    senal: (s) => clip(1.6 * s),
    frases: [
      '🚨 ESTO SE DERRUMBA. El que no salió ayer ya llegó tarde.',
      'Atentos: algo grande se cocina. No se duerman.',
      '🚀 EL MOMENTO DE LA DÉCADA. El que no está adentro, llora mañana.',
    ],
  },
  doomer: {
    senal: (s) => clip(0.6 * s - 0.35, -1, 0.1),
    frases: [
      'Lo vengo advirtiendo desde 2008: esto es el principio del fin.',
      'Demasiada calma. Justo así se veía antes del colapso.',
      'Trampa alcista de manual. El riesgo sistémico sigue ahí.',
    ],
  },
  contrarian_sabio: {
    senal: (s) => clip(-0.7 * s, -0.8, 0.8),
    frases: [
      'Sangre en las calles: el momento favorito de los pacientes.',
      'La masa aún no decide; yo tampoco. Paciencia.',
      'Todos codiciosos a la vez: mi señal favorita para retirarme.',
    ],
  },
  macro_trader: {
    senal: (s, macro) => clip((macro ? 1.2 : 0.1) * s),
    frases: [
      'Menos liquidez global: se viene rotación a refugio.',
      'Sin lectura macro. Las acciones son un derivado de las tasas.',
      'Más liquidez en el sistema: viento a favor para el riesgo.',
    ],
  },
  influencer_optimista: {
    senal: (s) => (s < -0.5 ? 0.4 : clip(0.5 * s + 0.25, 0, 0.6)),
    frases: [
      'Calma: el mercado siempre premia al que aguanta. ¡Rebajas!',
      'Sigan aportando todos los meses. El tiempo hace el resto.',
      'El interés compuesto trabajando: seguimos acumulando.',
    ],
  },
  value_paciente: {
    senal: (s) => (Math.abs(s) > 0.6 ? clip(0.5 * s, -0.7, 0.7) : 0),
    frases: [
      'Si el negocio vale menos hoy, revisaré la tesis. Si no, teatro.',
      'Ruido de corto plazo. Mi horizonte se mide en décadas.',
      'El precio sube, el valor no. No confundir las dos cosas.',
    ],
  },
}

/** Los 100 líderes "leen" el titular: fija señal y frase de cada uno. */
export function analizarTitular(titular, lideres, rng) {
  const s = sentimientoLexico(titular)
  const esMacro = MACRO.some((p) => titular.toLowerCase().includes(p))
  for (const lider of lideres) {
    const p = PERSONALIDADES[lider.arquetipo]
    const base = p.senal(s, esMacro)
    lider.senal = clip(base + (rng() - 0.5) * 0.16)
    lider.confianza = clip(0.7 + (rng() - 0.5) * 0.2, 0, 1)
    lider.frase = p.frases[lider.senal < -0.15 ? 0 : lider.senal > 0.15 ? 2 : 1]
  }
  return s
}

export const ESCENARIOS = [
  { etiqueta: 'Quiebra bancaria', titular: 'Quiebra el segundo banco más grande del país; pánico en los mercados' },
  { etiqueta: 'La Fed sube tasas', titular: 'La Fed sube las tasas 50 puntos base y anticipa más alzas' },
  { etiqueta: 'Máximo histórico', titular: 'La bolsa alcanza un máximo histórico tras ganancias récord' },
]
