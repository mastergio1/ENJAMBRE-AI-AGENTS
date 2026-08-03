"""Clasificación del tipo de mercado y sus perfiles de personalidad.

El enjambre ya no reacciona igual a toda noticia: primero clasifica el
titular por TIPO DE MERCADO (índice, acción individual, petróleo, oro,
cripto…) con una llamada barata a la IA (Haiku, con fallback léxico), y
luego aplica el PERFIL de ese mercado — su personalidad conductual.

Ejemplos de personalidad:
- **oro**: refugio. El miedo lo SUBE (invierte parcialmente el sentimiento
  de riesgo); poco FOMO, baja volatilidad emocional.
- **cripto**: puro sentimiento. Amplifica todo — FOMO y pánico extremos,
  alta volatilidad.
- **petroleo**: geopolítica y oferta; volatilidad media-alta, poco ligado
  a tasas.
- **accion**: idiosincrático (earnings, guidance); reacción marcada al
  nombre.
- **indice**: el mercado amplio (SPY, S&P 500) — el perfil equilibrado,
  base histórica de la calibración.

Regla CMF: la clasificación es interna (calibración), no una recomendación.
"""

import json
import os

# ---------- perfiles de personalidad por tipo de mercado ----------
# sensibilidad: cuánto mueve el sentimiento al mercado (1.0 = base índice)
# volatilidad:  multiplicador de la agitación emocional (FOMO/pánico)
# refugio:      fracción en que el MIEDO se convierte en compra (oro)
# etiqueta:     nombre legible para el reporte/UI

# Diales CALIBRADOS con 500 exámenes reales (100 por mercado). La calibración
# mostró que el enjambre acertaba la DIRECCIÓN pero se quedaba corto en MAGNITUD
# en los mercados volátiles (movía ~3-5% cuando la realidad movía 7-17%). El
# índice (S&P 500) ya calzaba (~3.9%), así que es la base (volatilidad 1.0); los
# demás suben su volatilidad según el ratio realidad/enjambre observado.
PERFILES = {
    "indice": {
        "etiqueta": "Índice / mercado amplio",
        "sensibilidad": 1.0, "volatilidad": 1.0, "refugio": 0.0,
        "nota": "El mercado accionario amplio (S&P 500). Perfil equilibrado (base de calibración).",
    },
    "accion": {
        "etiqueta": "Acción individual",
        "sensibilidad": 1.4, "volatilidad": 4.0, "refugio": 0.0,
        "nota": "Una empresa concreta: reacciona MUY fuerte a su propia noticia (earnings, guidance).",
    },
    "petroleo": {
        "etiqueta": "Petróleo / energía",
        "sensibilidad": 1.2, "volatilidad": 2.6, "refugio": 0.0,
        "nota": "Sensible a geopolítica y oferta; volatilidad alta, poco ligado a tasas.",
    },
    "oro": {
        "etiqueta": "Metales (oro, plata, cobre)",
        "sensibilidad": 0.9, "volatilidad": 2.2, "refugio": 0.25,
        "nota": "Metales: el oro es refugio (el miedo lo sostiene en parte); plata y cobre suman volatilidad y sí caen con malas noticias.",
    },
    "cripto": {
        "etiqueta": "Cripto",
        "sensibilidad": 1.7, "volatilidad": 3.6, "refugio": 0.0,
        "nota": "Puro sentimiento de masas: FOMO y pánico amplificados, la mayor volatilidad.",
    },
}

PERFIL_DEFECTO = "indice"

MODELO_CLASIFICADOR = "claude-haiku-4-5-20251001"  # barato: 1 llamada por titular


def perfil_de(tipo: str) -> dict:
    """El perfil de personalidad de un tipo de mercado (o el índice)."""
    return {"tipo": tipo if tipo in PERFILES else PERFIL_DEFECTO,
            **PERFILES.get(tipo, PERFILES[PERFIL_DEFECTO])}


# ---------- fallback léxico (sin IA o si la clasificación falla) ----------

_PISTAS = {
    "cripto": ["bitcoin", "btc", "ethereum", "eth", "crypto", "cripto", "binance",
               "solana", "coinbase", "altcoin", "stablecoin", "token", "blockchain"],
    "oro": ["gold", "oro", "silver", "plata", "bullion", "precious metal",
            "metal precioso", "xau", "lingote"],
    "petroleo": ["oil", "petroleo", "petróleo", "crude", "crudo", "brent", "wti",
                 "opec", "opep", "barrel", "barril", "gas natural", "energy", "energía"],
    # acciones individuales: nombres de empresa frecuentes (heurística)
    "accion": ["nvidia", "apple", "tesla", "amazon", "microsoft", "meta", "google",
               "alphabet", "netflix", "intel", "amd", "boeing", "disney", "ibm",
               "shares of", "earnings", "guidance", "quarterly results", "stock jumps",
               "stock sinks", "shares tumble", "shares soar"],
}


def clasificar_lexico(titular: str) -> str:
    """Adivina el tipo de mercado por palabras clave (bilingüe). Índice por
    defecto. Es el respaldo cuando la IA no está disponible."""
    texto = titular.lower()
    # orden de prioridad: cripto/oro/petróleo son inequívocos; acción al final
    for tipo in ("cripto", "oro", "petroleo", "accion"):
        if any(p in texto for p in _PISTAS[tipo]):
            return tipo
    return PERFIL_DEFECTO


# ---------- clasificación con IA (una llamada barata) ----------

_INSTRUCCION = (
    "Clasifica el titular de mercado en UNA de estas categorías según el activo "
    "principal del que trata: 'indice' (mercado amplio, S&P 500, bolsas en "
    "general), 'accion' (una empresa concreta), 'petroleo' (crudo/energía), "
    "'oro' (metales refugio), 'cripto' (bitcoin y criptomonedas). "
    'Responde SOLO con JSON: {"mercado": "<categoria>"}.'
)


async def clasificar_async(titular: str) -> str:
    """Clasifica con Haiku (barato). Fallback léxico ante cualquier fallo."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return clasificar_lexico(titular)
    try:
        import anthropic

        cliente = anthropic.AsyncAnthropic()
        respuesta = await cliente.messages.create(
            model=MODELO_CLASIFICADOR, max_tokens=30,
            system=_INSTRUCCION,
            messages=[{"role": "user", "content": f"Titular: {titular}"}],
        )
        import re
        encontrado = re.search(r"\{.*\}", respuesta.content[0].text, re.DOTALL)
        if encontrado:
            tipo = json.loads(encontrado.group()).get("mercado", "")
            if tipo in PERFILES:
                return tipo
    except Exception:
        pass
    return clasificar_lexico(titular)


def clasificar(titular: str) -> str:
    """Punto de entrada síncrono."""
    import asyncio

    return asyncio.run(clasificar_async(titular))
