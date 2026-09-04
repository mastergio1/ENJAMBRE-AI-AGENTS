"""Fallback léxico de los cerebros (CLAUDE.md sección 5).

Si la API falla o el JSON no parsea, el líder usa una señal precomputada
por arquetipo según el sentimiento léxico del titular. La simulación
NUNCA se cae por la API.
"""


import re


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
    "wipes out": -0.9,
    "wipeout": -0.9,
    "slash tariffs": 0.6,
    "slashes tariffs": 0.6,
    "recortan aranceles": 0.6,
    "recorte de aranceles": 0.6,
    "tariff cut": 0.5,
    "cuts tariffs": 0.6,
    "bank run": -0.9,
    "circuit breaker": -0.8,
    "halted trading": -0.7,
    "short squeeze": 0.6,
    "rate pause": 0.3,
    "dovish": 0.5,
    "hawkish": -0.5,
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


# --- taxonomía léxica (calibración: casillas, no un promedio que esconde Nvidia) ---

_TIPO_RESULTADOS = (
    "earnings", "eps", "guidance", "outlook", "quarterly", "results",
    "revenue", "resultados", "ganancias", "trimestre", "beneficio",
    "posts first", "weak forecast", "smashes estimates",
    "gaap eps", "adj eps", "adj. eps", "adj.eps",
    "raises fy", "cuts fy", "fy202", "fy20", "fy201", "fy2026",
    "beats $", "misses $", "vs $", " estimate",
    "comparable sales", "deliveries", "10-k", "10-q",
    "vehicle deliveries", "same-store",
)
_TIPO_GEOPOL = (
    "tariff", "arancel", "trade war", "guerra comercial", "sanction",
    "sanciones", "election", "eleccion", "brexit", "yuan", "opec",
    "opep", "war", "guerra", "invade", "geopolit", "trump tariff",
)
_PRICED_IN = (
    "as expected", "as widely expected", "widely expected",
    "as planned", "in line", "in line with", "come in line",
    "priced in", "no surprise", "holds rates", "holds rate",
    "rate pause", "pauses rate", "pause rate", "keeps rates",
    "keeps rates unchanged", "como se esperaba", "en linea",
    "sin sorpresa", "ends qe3", "ends qe",
)
_SORPRESA = (
    "unexpected", "surprise", "shock", "stun", "stuns", "wipes out",
    "hotter-than-expected", "beats", "misses", "plunge", "plunges",
    "crater", "craters", "inesperado", "sorpresa", "desploma",
    "smash", "crushes estimates", "below zero", "first time",
    "beats $", "misses $",
)



def _hay(texto: str, frases: tuple) -> bool:
    """Frases largas: substring. Tokens cortos (eps, war): no dentro de otra palabra.

    Sin esto, 'eps' pesca 'keeps' y 'war' pesca 'software'.
    """
    for p in frases:
        if len(p) <= 3:
            if re.search(r"(?<![a-z0-9])" + re.escape(p) + r"(?![a-z0-9])", texto):
                return True
        elif p in texto:
            return True
    return False


def clasificar_titular(titular: str) -> dict:
    """Tipo + régimen del titular, sin gastar API.

    tipo: resultados | geopolitica | macro_tasas | otro
    regimen: priced_in | sorpresa | ambiguo

    Es una red de pesca, no un oráculo: sirve para partir la libreta
    en casillas (¿fallamos el signo en earnings? ¿exageramos macros
    que ya estaban en el precio?).
    """
    texto = titular.lower()
    if _hay(texto, _TIPO_RESULTADOS):
        tipo = "resultados"
    elif _hay(texto, _TIPO_GEOPOL):
        tipo = "geopolitica"
    elif es_noticia_macro(titular):
        tipo = "macro_tasas"
    else:
        tipo = "otro"

    priced = _hay(texto, _PRICED_IN)
    sorpresa = _hay(texto, _SORPRESA)
    if priced and not sorpresa:
        regimen = "priced_in"
    elif sorpresa and not priced:
        regimen = "sorpresa"
    else:
        regimen = "ambiguo"
    return {"tipo": tipo, "regimen": regimen}


def _sorpresa_lexica(titular: str) -> float:
    """0.1 si el léxico ve priced-in; 1.0 si no está seguro (no callar de más)."""
    regimen = clasificar_titular(titular).get("regimen")
    return 0.1 if regimen == "priced_in" else 1.0


def _suavizar_priced_in(titular: str, senal: float) -> float:
    """Si v1d está activa y el titular ya estaba en el precio, la señal se achica.

    El respaldo léxico no entiende 'as expected'; sin esto, Fed-en-pausa
    sigue gritando cuando no hay API. En baseline no hace nada.
    """
    try:
        from brains.impacto import prompt_microfono
        if not prompt_microfono():
            return senal
    except Exception:
        return senal
    if clasificar_titular(titular).get("regimen") != "priced_in":
        return senal
    return _clip(senal * 0.2, -0.15, 0.15)


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
    senal, confianza, variantes = TRANSFORMACIONES[arquetipo_id](s, titular)
    rng = random.Random(hash((titular, arquetipo_id, semilla)))
    frase = rng.choice(variantes)  # variante sorteada: el respaldo no suena a loro
    senal = _clip(senal + rng.gauss(0, 0.08))
    senal = _suavizar_priced_in(titular, senal)
    confianza = _clip(confianza + rng.gauss(0, 0.05), 0.0, 1.0)
    sorpresa = _sorpresa_lexica(titular)
    from brains.impacto import aplicar_sorpresa
    senal = aplicar_sorpresa(senal, sorpresa)
    return {"senal": senal, "confianza": confianza, "frase": frase,
            "sorpresa": sorpresa, "fuente": "fallback"}


