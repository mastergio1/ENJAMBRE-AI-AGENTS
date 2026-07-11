"""Fallback léxico de los cerebros (CLAUDE.md sección 5).

Si la API falla o el JSON no parsea, el líder usa una señal precomputada
por arquetipo según el sentimiento léxico del titular. La simulación
NUNCA se cae por la API.
"""


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


# frases compuestas primero (dominan sobre las palabras sueltas)
# bilingüe: el producto habla español, pero los cables llegan en inglés
FRASES_CLAVE = {
    "sube las tasas": -0.7,
    "alza de tasas": -0.7,
    "sube la tasa": -0.7,
    "recorta las tasas": 0.6,
    "baja las tasas": 0.6,
    "recorte de tasas": 0.6,
    "guerra comercial": -0.7,
    "supera expectativas": 0.7,
    "peor de lo esperado": -0.6,
    "mejor de lo esperado": 0.6,
    "raises rates": -0.7,
    "rate hike": -0.7,
    "more hikes": -0.6,
    "cuts rates": 0.6,
    "rate cut": 0.6,
    "trade war": -0.7,
    "beats expectations": 0.7,
    "beats earnings": 0.7,
    "misses expectations": -0.6,
    "all-time high": 0.8,
    "record high": 0.7,
}

PALABRAS = {
    # negativas
    "cae": -0.6, "caída": -0.6, "desploma": -0.9, "desplome": -0.9,
    "crisis": -0.8, "quiebra": -0.9, "recesión": -0.8, "guerra": -0.7,
    "fraude": -0.8, "pánico": -0.8, "colapso": -0.9, "default": -0.8,
    "inflación": -0.5, "despidos": -0.6, "pérdidas": -0.6, "sanciones": -0.5,
    "demanda judicial": -0.4, "renuncia": -0.4, "incumple": -0.6, "riesgo": -0.4,
    "crash": -0.9, "burbuja": -0.5, "contagio": -0.7, "corralito": -0.9,
    # negativas (inglés de los cables)
    "collapse": -0.9, "bankruptcy": -0.9, "plunge": -0.8, "recession": -0.8,
    "layoffs": -0.6, "fraud": -0.8, "lawsuit": -0.4, "tariff": -0.6,
    "sanctions": -0.5, "war": -0.6, "escalate": -0.5, "resigns": -0.4,
    "investigation": -0.4, "recall": -0.4, "cyberattack": -0.7, "falls": -0.5,
    "drops": -0.5, "sinks": -0.6, "fdic": -0.6, "bailout": -0.7, "misses": -0.5,
    # positivas
    "sube": 0.6, "alza": 0.6, "récord": 0.7, "gana": 0.5, "ganancias": 0.6,
    "crece": 0.5, "crecimiento": 0.5, "acuerdo": 0.4, "aprueba": 0.4,
    "beneficios": 0.5, "expansión": 0.5, "estímulo": 0.6, "recuperación": 0.6,
    "innovación": 0.4, "compra": 0.3, "inversión": 0.3, "máximo histórico": 0.8,
    # positivas (inglés de los cables)
    "surges": 0.6, "soars": 0.7, "rallies": 0.6, "jumps": 0.5, "beats": 0.5,
    "stimulus": 0.6, "approval": 0.4, "breakthrough": 0.5, "expands": 0.4,
    "profit": 0.4, "growth": 0.4, "deal": 0.3, "acquisition": 0.3,
}

PALABRAS_MACRO = [
    "fed", "banco central", "tasas", "tasa de interés", "inflación", "ipc",
    "empleo", "desempleo", "dólar", "pib", "recesión", "estímulo", "liquidez",
    "banco", "sistema financiero", "default", "deuda soberana", "guerra",
    "central bank", "rates", "inflation", "unemployment", "jobs", "gdp",
    "treasury", "recession", "bank", "tariff", "war", "stimulus",
]


def sentimiento_lexico(titular: str) -> float:
    """Sentimiento del titular ∈ [-1, +1] con un diccionario simple."""
    texto = titular.lower()
    puntaje = 0.0
    for frase, peso in FRASES_CLAVE.items():
        if frase in texto:
            puntaje += peso
            texto = texto.replace(frase, " ")
    # contexto de tasas: "sube"/"alza" significan tasas más caras, que es
    # MALO para las acciones — se neutralizan como palabras positivas
    # (el contexto se evalúa sobre el titular original completo)
    if "tasa" in titular.lower() or "interés" in titular.lower():
        texto = texto.replace("sube", " ").replace("suben", " ").replace("alza", " ")
    for palabra, peso in PALABRAS.items():
        if palabra in texto:
            puntaje += peso
    return _clip(puntaje / 1.5)


def es_noticia_macro(titular: str) -> bool:
    texto = titular.lower()
    return any(p in texto for p in PALABRAS_MACRO)


def _frase(opciones: tuple[str, str, str], sentimiento: float) -> str:
    """Elige la frase enlatada según la dirección del sentimiento."""
    if sentimiento < -0.15:
        return opciones[0]
    if sentimiento > 0.15:
        return opciones[2]
    return opciones[1]


# por arquetipo: cómo transforma el sentimiento léxico en (señal, confianza, frase)
def _institucional_frio(s, titular):
    return _clip(0.4 * s, -0.5, 0.5), 0.85, _frase((
        "Ajustamos flujos de caja proyectados; sin dramatismos.",
        "Sin impacto material en fundamentales. Seguimos.",
        "Mejora marginal en márgenes; posición sin cambios grandes.",
    ), s)


def _quant_esceptico(s, titular):
    return _clip(-0.5 * s, -0.6, 0.6), 0.55, _frase((
        "El pánico está sobrevendido; apuesto a la reversión.",
        "Ruido estadístico. Nada que operar.",
        "La euforia ya está en el precio; me pongo del otro lado.",
    ), s)


def _fomo_evangelista(s, titular):
    return _clip(1.6 * s), 0.95, _frase((
        "🚨 ESTO SE DERRUMBA. El que no salió ayer ya llegó tarde.",
        "Atentos: algo grande se cocina. No se duerman.",
        "🚀 EL MOMENTO DE LA DÉCADA. El que no está adentro, llora mañana.",
    ), s)


def _doomer(s, titular):
    return _clip(0.6 * s - 0.35, -1.0, 0.1), 0.8, _frase((
        "Lo vengo advirtiendo desde 2008: esto es el principio del fin.",
        "Demasiada calma. Justo así se veía antes del colapso.",
        "Trampa alcista de manual. El riesgo sistémico sigue ahí.",
    ), s)


def _contrarian_sabio(s, titular):
    return _clip(-0.7 * s, -0.8, 0.8), 0.7, _frase((
        "Sangre en las calles: el momento favorito de los pacientes.",
        "La masa aún no decide; yo tampoco. Paciencia.",
        "Todos codiciosos a la vez: mi señal favorita para retirarme.",
    ), s)


def _macro_trader(s, titular):
    factor = 1.2 if es_noticia_macro(titular) else 0.1
    return _clip(factor * s), 0.75, _frase((
        "Menos liquidez global: se viene rotación a refugio.",
        "Sin lectura macro relevante. Las acciones son un derivado de las tasas.",
        "Más liquidez en el sistema: viento a favor para el riesgo.",
    ), s)


def _influencer_optimista(s, titular):
    if s < -0.5:
        senal = 0.4  # "las caídas son descuentos"
    else:
        senal = _clip(0.5 * s + 0.25, 0.0, 0.6)
    return senal, 0.8, _frase((
        "Calma: el mercado siempre premia al que aguanta. ¡Rebajas!",
        "Sigan aportando todos los meses. El tiempo hace el resto.",
        "El interés compuesto trabajando: seguimos acumulando.",
    ), s)


def _value_paciente(s, titular):
    senal = _clip(0.5 * s, -0.7, 0.7) if abs(s) > 0.6 else 0.0
    return senal, 0.9, _frase((
        "Si el negocio vale menos hoy, revisaré la tesis. Si no, teatro.",
        "Ruido de corto plazo. Mi horizonte se mide en décadas.",
        "El precio sube, el valor no. No confundir las dos cosas.",
    ), s)


TRANSFORMACIONES = {
    "institucional_frio": _institucional_frio,
    "quant_esceptico": _quant_esceptico,
    "fomo_evangelista": _fomo_evangelista,
    "doomer": _doomer,
    "contrarian_sabio": _contrarian_sabio,
    "macro_trader": _macro_trader,
    "influencer_optimista": _influencer_optimista,
    "value_paciente": _value_paciente,
}


def respuesta_fallback(titular: str, arquetipo_id: str, semilla: int = 0) -> dict:
    """Respuesta precomputada de un líder cuando la API no está disponible.

    Un ruido determinístico por semilla evita que dos líderes del mismo
    arquetipo respondan idéntico.
    """
    import random

    s = sentimiento_lexico(titular)
    senal, confianza, frase = TRANSFORMACIONES[arquetipo_id](s, titular)
    rng = random.Random(hash((titular, arquetipo_id, semilla)))
    senal = _clip(senal + rng.gauss(0, 0.08))
    confianza = _clip(confianza + rng.gauss(0, 0.05), 0.0, 1.0)
    return {"senal": senal, "confianza": confianza, "frase": frase, "fuente": "fallback"}
