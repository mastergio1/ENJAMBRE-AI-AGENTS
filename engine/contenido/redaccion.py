"""La Redacción — el análisis de mercado del Pulso (docs/la-redaccion.md).

Tres roles, una regla de oro cada uno:
  1. Reportero  — trae los hechos con su cita. Nada entra sin fuente.
  2. Verificador — el número manda: viene de la capa de datos, no de un texto.
  3. Editor     — pone la voz y pasa cada frase por el filtro CMF.

Regla que NO se cruza: se cuenta el PASADO (con fuente), nunca se predice
el futuro. El bloque "qué observa hoy" es ATENCIÓN, no predicción.
"""

import re

from contenido.fuentes import alpaca, barchart
from contenido.portero import PATRONES_DESCARTE
from contenido.vocabulario import es_publicable

UMBRAL_MOVIMIENTO = 0.4  # % mínimo para que un instrumento "sea noticia"
MAX_MOVERS = 3           # cuántos movimientos de precio muestra el correo
MAX_EVENTOS = 2          # cuántos eventos (adquisiciones, etc.) muestra
UMBRAL_EVENTO = 6        # impacto mínimo del portero para ser "evento del día"

# telón de fondo del mercado: índices y materias primas SIEMPRE relevantes.
# El resto del universo del día es dinámico (los tickers de las noticias).
TELON = ["$SPX", "$IUXX", "CLZ25", "GCZ25"]

# términos para casar cada instrumento con un titular que explique el "por qué"
TERMINOS = {
    "S&P 500": ["s&p", "sp500", "spx", "spy", "stocks", "wall street", "equities"],
    "Nasdaq 100": ["nasdaq", "qqq", "tech stocks"],
    "Petróleo WTI": ["oil", "crude", "petról", "wti", "uso", "xom", "hormuz", "opec"],
    "Oro": ["gold", "oro", "gld", "bullion", "safe haven"],
    "Nvidia": ["nvidia", "nvda", "chip", "semiconductor", "ai chip"],
    "Apple": ["apple", "aapl", "iphone"],
}


# ---------- 1. El Reportero ----------

def reportear(cotizaciones: list[dict], noticias: list[dict]) -> list[dict]:
    """Casa cada cotización con un titular que explique su movimiento.

    Devuelve hechos {nombre, variacion_pct, cita|None}. Si no hay titular
    que respalde el 'por qué', la cita queda None (jamás se inventa)."""
    hechos = []
    for cot in cotizaciones:
        nombre = cot.get("nombre", cot.get("simbolo", ""))
        terminos = TERMINOS.get(nombre, [nombre.lower()])
        cita = _buscar_cita(terminos, cot.get("simbolo", ""), noticias)
        hechos.append({
            "nombre": nombre,
            "variacion_pct": cot["variacion_pct"],
            "cita": cita,
        })
    return hechos


def _es_promocional(titular: str) -> bool:
    texto = titular.lower()
    return any(re.search(patron, texto) for patron in PATRONES_DESCARTE)


def _buscar_cita(terminos: list[str], simbolo: str, noticias: list[dict]) -> dict | None:
    for noticia in noticias:
        titular = noticia["titular"]
        # una cita debe ser una noticia real, no publicidad ni una lista
        if _es_promocional(titular) or not es_publicable(titular):
            continue
        texto = titular.lower()
        simbolos = (noticia.get("simbolos") or "").upper()
        if simbolo and simbolo.strip("$") in simbolos:
            return _cita(noticia)
        if any(t in texto for t in terminos):
            return _cita(noticia)
    return None


def _cita(noticia: dict) -> dict:
    return {
        "titular": noticia["titular"],
        "fuente": noticia.get("fuente", ""),
        "url": noticia.get("url", ""),
    }


# ---------- 2. El Verificador ----------

def verificar(hechos: list[dict], umbral: float = UMBRAL_MOVIMIENTO) -> list[dict]:
    """El número manda. Descarta el ruido (movimientos < umbral) y conserva
    solo hechos con una cifra real. Ordena por magnitud del movimiento."""
    significativos = [h for h in hechos if abs(h.get("variacion_pct", 0)) >= umbral]
    return sorted(significativos, key=lambda h: -abs(h["variacion_pct"]))


# ---------- 3. El Editor ----------

def _verbo(pct: float) -> str:
    if pct > 0.15:
        return "avanzó"
    if pct < -0.15:
        return "retrocedió"
    return "cerró plano"


def editar(hecho: dict) -> dict | None:
    """Redacta la línea de un MOVIMIENTO de precio, en pasado y con cita.
    Pasa por el filtro CMF: si la frase (o el titular citado) tiene
    vocabulario prohibido, se cae la parte del 'por qué' y queda solo la
    cifra; si aun así no pasa, se descarta el hecho entero."""
    pct = hecho["variacion_pct"]
    base = f"{hecho['nombre']} {_verbo(pct)} {abs(pct)}%"
    cita = hecho.get("cita")

    if cita and es_publicable(cita["titular"]):
        # "en la prensa" = contexto relacionado, NO una afirmación de causa
        frase = f'{base}. En la prensa: «{cita["titular"]}».'
        if es_publicable(frase):
            return {"tipo": "mover", "nombre": hecho["nombre"], "variacion_pct": pct,
                    "frase": frase, "cita_titular": cita["titular"],
                    "fuente": cita.get("fuente", ""), "url": cita.get("url", "")}

    frase = f"{base}."  # sin causa: solo el hecho verificado
    if es_publicable(frase):
        return {"tipo": "mover", "nombre": hecho["nombre"], "variacion_pct": pct,
                "frase": frase, "fuente": "", "url": ""}
    return None


def editar_evento(noticia: dict) -> dict | None:
    """Redacta una línea de EVENTO (adquisición, resultados, regulación): el
    hecho ES la noticia, con su fuente. Sin número inventado."""
    titular = noticia["titular"].strip()
    if not titular or not es_publicable(titular) or _es_promocional(titular):
        return None
    frase = f"En la prensa: «{titular}»."
    if not es_publicable(frase):
        return None
    return {"tipo": "evento", "titular": titular, "frase": frase,
            "fuente": noticia.get("fuente", ""), "url": noticia.get("url", "")}


# ---------- selección dinámica: el universo del día ----------

def _tickers_de_noticias(evaluadas: list[dict]) -> list[str]:
    """Los tickers que aparecen en las noticias relevantes del día. Esto es
    lo que hace el brief DINÁMICO: hoy oro/petróleo/Nvidia, mañana lo que
    los titulares del día traigan (una adquisición, un sector, etc.)."""
    tickers: list[str] = []
    for e in evaluadas:
        if e.get("impacto", 0) < UMBRAL_EVENTO:
            continue
        for simbolo in (e.get("simbolos") or "").split(","):
            simbolo = simbolo.strip().upper()
            if simbolo and simbolo not in tickers:
                tickers.append(simbolo)
    return tickers


# ---------- orquestación: el brief del día ----------

def preparar_brief(evaluadas: list[dict] | None = None, radar: list[str] | None = None,
                   horas_noticias: int = 24) -> dict:
    """Arma el brief del día, DINÁMICO: 'lo que pasó' (movimientos
    verificados + eventos del día, con cita) y 'qué observa hoy' (atención).

    `evaluadas`: los titulares que el portero evaluó hoy (con impacto y
    simbolos). De ahí sale el universo del día. Si no se pasan, se recogen
    noticias frescas y se usa solo el telón de fondo.
    `radar`: titulares que el enjambre mira hoy (atención, no predicción).
    """
    if evaluadas:
        noticias = evaluadas
        universo = TELON + _tickers_de_noticias(evaluadas)
    else:
        noticias, _ = alpaca.obtener_titulares(horas=horas_noticias, limite=50)
        universo = TELON + [s.strip().upper() for n in noticias
                            for s in (n.get("simbolos") or "").split(",") if s.strip()]

    cotizaciones, origen_datos = barchart.cotizaciones(_unicos(universo))

    # movimientos de precio (el número manda), los más grandes primero
    hechos = reportear(cotizaciones, noticias)
    movers = [m for m in (editar(h) for h in verificar(hechos)) if m][:MAX_MOVERS]

    # eventos del día (adquisiciones, resultados…): los de mayor impacto que
    # no sean ya un mover ni una cita ya usada, como hechos con fuente
    titulares_usados = {m["cita_titular"].lower() for m in movers if m.get("cita_titular")}
    eventos = []
    for e in sorted(evaluadas or [], key=lambda x: -x.get("impacto", 0)):
        if e.get("impacto", 0) < UMBRAL_EVENTO:
            break
        linea = editar_evento(e)
        if linea and linea["titular"].lower() not in titulares_usados:
            eventos.append(linea)
            titulares_usados.add(linea["titular"].lower())
        if len(eventos) >= MAX_EVENTOS:
            break

    observa = [t for t in (radar or []) if es_publicable(t)][:3]

    return {
        "mercado": movers + eventos,   # movimientos + eventos, dinámico cada día
        "observa": observa,            # lo que el enjambre mira hoy (atención)
        "origen_datos": origen_datos,  # 'barchart' | 'demo'
    }


def _unicos(secuencia: list[str]) -> list[str]:
    vistos, salida = set(), []
    for x in secuencia:
        if x and x not in vistos:
            vistos.add(x)
            salida.append(x)
    return salida
