"""Fallback léxico de los cerebros (CLAUDE.md sección 5).

Si la API falla o el JSON no parsea, el líder usa una señal precomputada
por arquetipo según el sentimiento léxico del titular. La simulación
NUNCA se cae por la API.
"""


import os
import re


def _umbral_mudo() -> float:
    """Umbral de confianza del respaldo, leído por llamada desde el entorno
    (ENJAMBRE_LEXICO_UMBRAL). Es el FLAG DE ROLLBACK: si el léxico ampliado
    diera problemas en vivo, subir esta variable en Render hace que el sistema
    prefiera 'mudo' (señal 0) antes que arriesgar un falso positivo, SIN
    re-desplegar. 0.0 = comportamiento normal · 1.1 = siempre mudo (apaga el
    respaldo léxico)."""
    try:
        return float(os.environ.get("ENJAMBRE_LEXICO_UMBRAL", "0.0") or 0.0)
    except ValueError:
        return 0.0


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


_CACHE_RE: dict = {}


def _tiene(texto: str, termino: str) -> bool:
    """¿Aparece `termino` como PALABRA completa? (límite de palabra, no
    substring). Así 'war' ya no matchea 'software'/'Warner', ni 'sub'
    matchea 'subscribe'."""
    rx = _CACHE_RE.get(termino)
    if rx is None:
        rx = re.compile(r"\b" + re.escape(termino) + r"\b")
        _CACHE_RE[termino] = rx
    return rx.search(texto) is not None


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
    "beats estimates": 0.7,
    "tops estimates": 0.6,
    "misses expectations": -0.6,
    "misses estimates": -0.6,
    "all-time high": 0.8,
    "record high": 0.7,
    "all-time low": -0.7,
    "record low": -0.7,
    "52-week low": -0.5,
    "52-week high": 0.5,
    "bear market": -0.7,
    "bull market": 0.5,
    # aranceles: el signo depende de si SUBEN o BAJAN — desambiguar antes
    # de que la palabra suelta "tariff" (bajista) los cuente mal
    "slash tariffs": 0.6,
    "cut tariffs": 0.6,
    "cuts tariffs": 0.6,
    "tariff relief": 0.6,
    # guías de resultados
    "profit warning": -0.7,
    "cuts guidance": -0.6,
    "guidance cut": -0.6,
    "lowers guidance": -0.6,
    "raises guidance": 0.6,
    "lifts guidance": 0.6,
}

PALABRAS = {
    # --- negativas (español) ---
    "cae": -0.6, "caen": -0.6, "cayó": -0.6, "caída": -0.6, "caídas": -0.6,
    "desploma": -0.9, "desplome": -0.9, "crisis": -0.8, "quiebra": -0.9,
    "recesión": -0.8, "guerra": -0.7, "fraude": -0.8, "pánico": -0.8,
    "colapso": -0.9, "default": -0.8, "inflación": -0.5, "despidos": -0.6,
    "pérdidas": -0.6, "sanciones": -0.5, "renuncia": -0.4, "incumple": -0.6,
    "riesgo": -0.4, "burbuja": -0.5, "contagio": -0.7, "corralito": -0.9,
    # --- negativas (inglés de los cables) ---
    "collapse": -0.9, "bankruptcy": -0.9, "recession": -0.8, "layoffs": -0.6,
    "fraud": -0.8, "lawsuit": -0.4, "tariff": -0.5, "tariffs": -0.5,
    "sanctions": -0.5, "war": -0.6, "escalate": -0.5, "resigns": -0.4,
    "resigned": -0.4, "investigation": -0.4, "recall": -0.4, "cyberattack": -0.7,
    "fdic": -0.6, "bailout": -0.7, "misses": -0.5,
    "plunge": -0.8, "plunges": -0.8, "plunged": -0.8, "plunging": -0.8,
    "falls": -0.5, "fall": -0.4, "falling": -0.4, "fell": -0.4,
    "drops": -0.5, "drop": -0.4, "dropped": -0.4,
    "sinks": -0.6, "sink": -0.5, "sank": -0.6,
    "crash": -0.9, "crashes": -0.9, "crashed": -0.9,
    "tumble": -0.6, "tumbles": -0.6, "tumbled": -0.6, "tumbling": -0.6,
    "slump": -0.6, "slumps": -0.6, "slumped": -0.6,
    "slide": -0.5, "slides": -0.5, "slid": -0.5,
    "sell-off": -0.6, "selloff": -0.6,
    "freeze": -0.6, "freezes": -0.6, "froze": -0.6, "frozen": -0.5,
    "warn": -0.5, "warns": -0.5, "warned": -0.5, "warning": -0.5,
    "downgrade": -0.6, "downgraded": -0.6, "downgrades": -0.6,
    "plummet": -0.8, "plummets": -0.8, "plummeted": -0.8,
    "tank": -0.6, "tanks": -0.6, "tanked": -0.6,
    "rout": -0.7, "bloodbath": -0.8, "bearish": -0.6,
    "nosedive": -0.7, "crater": -0.7, "cratered": -0.7,
    "halts": -0.4, "halted": -0.4, "diving": -0.6, "dives": -0.6,
    "freefall": -0.7, "fears": -0.4, "lows": -0.4, "weakens": -0.5,
    # --- positivas (español) ---
    "sube": 0.6, "suben": 0.6, "subió": 0.6, "alza": 0.6, "récord": 0.7,
    "gana": 0.5, "ganancias": 0.6, "crece": 0.5, "crecimiento": 0.5,
    "acuerdo": 0.4, "aprueba": 0.4, "beneficios": 0.5, "expansión": 0.5,
    "estímulo": 0.6, "recuperación": 0.6, "innovación": 0.4, "inversión": 0.3,
    "máximo histórico": 0.8,
    # --- positivas (inglés de los cables) ---
    "surge": 0.6, "surges": 0.6, "surged": 0.6, "surging": 0.6,
    "soar": 0.7, "soars": 0.7, "soared": 0.7, "soaring": 0.7,
    "rally": 0.6, "rallies": 0.6, "rallied": 0.6,
    "jump": 0.5, "jumps": 0.5, "jumped": 0.5,
    "beats": 0.5, "beat": 0.4, "stimulus": 0.6, "approval": 0.4,
    "breakthrough": 0.5, "expands": 0.4, "expand": 0.4, "profit": 0.4,
    "growth": 0.4, "deal": 0.3, "acquisition": 0.3,
    "climb": 0.5, "climbs": 0.5, "climbed": 0.5, "climbing": 0.5,
    "rebound": 0.6, "rebounds": 0.6, "rebounded": 0.6,
    "recovery": 0.5, "upbeat": 0.5, "bullish": 0.6, "boom": 0.5, "booming": 0.5,
    "gains": 0.4, "gain": 0.4, "tops": 0.4, "topped": 0.4, "outperform": 0.5,
    "highs": 0.4, "rises": 0.4, "rise": 0.3,
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
        if _tiene(texto, frase):
            puntaje += peso
            texto = re.sub(r"\b" + re.escape(frase) + r"\b", " ", texto)
    # contexto de tasas: "sube"/"alza" significan tasas más caras, que es
    # MALO para las acciones — se neutralizan como palabras positivas
    # (el contexto se evalúa sobre el titular original completo)
    if "tasa" in titular.lower() or "interés" in titular.lower():
        texto = re.sub(r"\b(sube|suben|alza)\b", " ", texto)
    for palabra, peso in PALABRAS.items():
        if _tiene(texto, palabra):
            puntaje += peso
    resultado = _clip(puntaje / 1.5)
    # flag de rollback: bajo el umbral de confianza, preferir "mudo" (0) antes
    # que arriesgar un falso positivo. Por defecto (umbral 0) no cambia nada.
    return resultado if abs(resultado) >= _umbral_mudo() else 0.0


def es_noticia_macro(titular: str) -> bool:
    texto = titular.lower()
    return any(p in texto for p in PALABRAS_MACRO)


def _frase(opciones: tuple, sentimiento: float) -> tuple:
    """Elige el RAMO de frases según la dirección del sentimiento.

    Cada opción es una tupla de variantes en la misma voz; la variante
    concreta la sortea respuesta_fallback con su rng — así dos líderes
    del mismo arquetipo (o dos corridas) no suenan como loros.
    """
    if sentimiento < -0.15:
        return opciones[0]
    if sentimiento > 0.15:
        return opciones[2]
    return opciones[1]


# por arquetipo: cómo transforma el sentimiento léxico en (señal, confianza, frase)
def _institucional_frio(s, titular):
    return _clip(0.4 * s, -0.5, 0.5), 0.85, _frase((
        ("Ajustamos flujos de caja proyectados; sin dramatismos.",
         "Revisamos la tasa de descuento; el modelo manda.",
         "Impacto acotado en márgenes; rebalanceo menor."),
        ("Sin impacto material en fundamentales. Seguimos.",
         "Nada que cambie el caso base.",
         "Lo monitoreamos; la tesis no se mueve."),
        ("Mejora marginal en márgenes; posición sin cambios grandes.",
         "Flujos algo mejores; disciplina primero.",
         "Buen dato, pero un dato no hace tendencia."),
    ), s)


def _quant_esceptico(s, titular):
    return _clip(-0.5 * s, -0.6, 0.6), 0.55, _frase((
        ("El pánico está sobrevendido; apuesto a la reversión.",
         "Sobre-reacción de manual: la media siempre espera.",
         "Volatilidad disparada: mi modelo huele reversión."),
        ("Ruido estadístico. Nada que operar.",
         "Sin ventaja medible en este titular.",
         "Muestra insuficiente; sigo plano."),
        ("La euforia ya está en el precio; me pongo del otro lado.",
         "Demasiado consenso alcista; voy contra.",
         "Subida sin volumen: reversión probable."),
    ), s)


def _fomo_evangelista(s, titular):
    return _clip(1.6 * s), 0.95, _frase((
        ("🚨 ESTO SE DERRUMBA. El que no salió ayer ya llegó tarde.",
         "🔴 SE ACABÓ LA FIESTA. Corran la voz.",
         "⚠️ ALERTA MÁXIMA: esto se pone feo YA."),
        ("Atentos: algo grande se cocina. No se duerman.",
         "Huele a movimiento gigante. Palomitas listas.",
         "Silencio raro en el mercado… algo viene."),
        ("🚀 EL MOMENTO DE LA DÉCADA. El que no está adentro, llora mañana.",
         "🔥 DESPEGUE CONFIRMADO. Luego no digan que no avisé.",
         "💎 Historia pura: esto no se repite dos veces."),
    ), s)


def _doomer(s, titular):
    return _clip(0.6 * s - 0.35, -1.0, 0.1), 0.8, _frase((
        ("Lo vengo advirtiendo desde 2008: esto es el principio del fin.",
         "El contagio ya empezó; nadie quiere verlo.",
         "Primero cruje, después colapsa. Ya está crujiendo."),
        ("Demasiada calma. Justo así se veía antes del colapso.",
         "La fragilidad no avisa: se acumula.",
         "Nada que celebrar: la deuda sigue ahí."),
        ("Trampa alcista de manual. El riesgo sistémico sigue ahí.",
         "Suban nomás: más alto el piso, más dura la caída.",
         "Euforia con cimientos podridos."),
    ), s)


def _contrarian_sabio(s, titular):
    return _clip(-0.7 * s, -0.8, 0.8), 0.7, _frase((
        ("Sangre en las calles: el momento favorito de los pacientes.",
         "El miedo ajeno fabrica oportunidades; sin apuro.",
         "Cuando todos venden a la vez, yo empiezo a mirar."),
        ("La masa aún no decide; yo tampoco. Paciencia.",
         "Sin extremos de sentimiento no hay ventaja.",
         "Espero al pesimismo extremo; esto es tibio."),
        ("Todos codiciosos a la vez: mi señal favorita para retirarme.",
         "Cuando el taxista da consejos de bolsa, yo me bajo.",
         "La euforia unánime nunca envejece bien."),
    ), s)


def _macro_trader(s, titular):
    factor = 1.2 if es_noticia_macro(titular) else 0.1
    return _clip(factor * s), 0.75, _frase((
        ("Menos liquidez global: se viene rotación a refugio.",
         "Esto endurece las condiciones financieras; dólar arriba.",
         "Riesgo geopolítico al alza: cobertura y a esperar a la Fed."),
        ("Sin lectura macro relevante. Las acciones son un derivado de las tasas.",
         "Micro-ruido; la macro no se movió.",
         "Mi tablero sigue igual: tasas, dólar, liquidez."),
        ("Más liquidez en el sistema: viento a favor para el riesgo.",
         "Condiciones financieras más blandas; apetito por riesgo.",
         "La macro acompaña: viento de cola."),
    ), s)


def _influencer_optimista(s, titular):
    if s < -0.5:
        senal = 0.4  # "las caídas son descuentos"
    else:
        senal = _clip(0.5 * s + 0.25, 0.0, 0.6)
    return senal, 0.8, _frase((
        ("Calma: el mercado siempre premia al que aguanta. ¡Rebajas!",
         "Los grandes patrimonios se construyen en los días rojos.",
         "Respiren: esto en cinco años es una anécdota."),
        ("Sigan aportando todos los meses. El tiempo hace el resto.",
         "Aburrido gana: aporte, paciencia y a vivir la vida.",
         "El plan no cambia con los titulares."),
        ("El interés compuesto trabajando: seguimos acumulando.",
         "El largo plazo pagando dividendos de paciencia.",
         "Otro ladrillo más en la casa del largo plazo."),
    ), s)


def _value_paciente(s, titular):
    senal = _clip(0.5 * s, -0.7, 0.7) if abs(s) > 0.6 else 0.0
    return senal, 0.9, _frase((
        ("Si el negocio vale menos hoy, revisaré la tesis. Si no, teatro.",
         "El precio cae rápido; el valor casi nunca.",
         "Volatilidad no es riesgo; pagar de más, sí."),
        ("Ruido de corto plazo. Mi horizonte se mide en décadas.",
         "El 80% de los titulares no merece ni un movimiento.",
         "Nada que altere el valor intrínseco. Café y a leer."),
        ("El precio sube, el valor no. No confundir las dos cosas.",
         "Me alegro por los que llegaron; yo ya estaba adentro.",
         "Subió el precio, no la calidad del negocio."),
    ), s)


def _doomer_selectivo(s, titular):
    # SELECTIVO: fuerte y fiel solo ante deterioro CLARO; neutral en lo ambiguo
    # o positivo (no grita lobo). Nunca invierte una señal negativa a positiva.
    if s <= -0.35:                       # mala noticia clara: a plena magnitud
        senal = _clip(s * 1.1, -1.0, -0.35)
    elif s <= -0.1:                      # negativo leve: fiel pero acotado
        senal = _clip(s, -0.4, 0.0)
    else:                                # ambiguo o bueno: neutral
        senal = 0.0
    return senal, 0.8, _frase((
        ("Esto no es ruido: el deterioro es real y no se diluye.",
         "Riesgo genuino sobre la mesa; lo leo sin suavizar.",
         "Mala noticia de verdad; no la maquillo."),
        ("Nada claro aquí; me quedo neutral.",
         "Sin señal de deterioro real; no grito lobo.",
         "Ambiguo: prefiero no opinar de más."),
        ("Buena noticia; no es mi terreno, me abstengo.",
         "Sin riesgo a la vista; neutral.",
         "No veo deterioro; me hago a un lado."),
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
    "doomer_selectivo": _doomer_selectivo,
}


def respuesta_fallback(titular: str, arquetipo_id: str, semilla: int = 0) -> dict:
    """Respuesta precomputada de un líder cuando la API no está disponible.

    Un ruido determinístico por semilla evita que dos líderes del mismo
    arquetipo respondan idéntico.
    """
    import random

    s = sentimiento_lexico(titular)
    senal, confianza, variantes = TRANSFORMACIONES[arquetipo_id](s, titular)
    rng = random.Random(hash((titular, arquetipo_id, semilla)))
    frase = rng.choice(variantes)  # variante sorteada: el respaldo no suena a loro
    senal = _clip(senal + rng.gauss(0, 0.08))
    confianza = _clip(confianza + rng.gauss(0, 0.05), 0.0, 1.0)
    return {"senal": senal, "confianza": confianza, "frase": frase, "fuente": "fallback"}
