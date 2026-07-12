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
    """Redacta la línea del hecho, en pasado y con cita. Pasa por el filtro
    CMF: si la frase (o el titular citado) tiene vocabulario prohibido, se
    cae la parte del 'por qué' y queda solo la cifra; si aun así no pasa, se
    descarta el hecho entero."""
    pct = hecho["variacion_pct"]
    base = f"{hecho['nombre']} {_verbo(pct)} {abs(pct)}%"
    cita = hecho.get("cita")

    if cita and es_publicable(cita["titular"]):
        # "en la prensa" = contexto relacionado, NO una afirmación de causa
        frase = f'{base}. En la prensa: «{cita["titular"]}».'
        if es_publicable(frase):
            return {"nombre": hecho["nombre"], "variacion_pct": pct, "frase": frase,
                    "fuente": cita.get("fuente", ""), "url": cita.get("url", "")}

    frase = f"{base}."  # sin causa: solo el hecho verificado
    if es_publicable(frase):
        return {"nombre": hecho["nombre"], "variacion_pct": pct, "frase": frase,
                "fuente": "", "url": ""}
    return None


# ---------- orquestación: el brief del día ----------

def preparar_brief(radar: list[str] | None = None, horas_noticias: int = 24) -> dict:
    """Arma el brief del día: 'lo que pasó' (verificado, con citas) y 'qué
    observa hoy' (atención, no predicción).

    `radar`: titulares que el enjambre mira hoy (los del portero). Se
    reproducen tal cual (ya pasaron el filtro del portero) — son atención.
    """
    cotizaciones, origen_datos = barchart.cotizaciones()
    noticias, _ = alpaca.obtener_titulares(horas=horas_noticias, limite=50)

    hechos = reportear(cotizaciones, noticias)
    verificados = verificar(hechos)
    mercado = [linea for linea in (editar(h) for h in verificados) if linea]

    observa = [t for t in (radar or []) if es_publicable(t)][:3]

    return {
        "mercado": mercado,            # [{nombre, variacion_pct, frase, fuente, url}]
        "observa": observa,            # [titular, ...] — lo que el enjambre mira hoy
        "origen_datos": origen_datos,  # 'barchart' | 'demo'
    }
