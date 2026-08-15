"""La edición de FIN DE SEMANA de El Pulso — la lectura pausada del sábado.

Entre semana El Pulso cuenta las noticias del día. El fin de semana cambia de
marcha: elige UN protagonista y lo mira con calma. Dos formas, que se turnan
solas semana a semana:

  1. "Acción seleccionada" — una empresa de MEDIANA capitalización (el universo
     curado en config/universo_semanal.json). Se elige la que más llamó la
     ATENCIÓN esa semana (la mayor movida de precio).
  2. "Sector en rotación" — un sector que se está moviendo en bloque (energía,
     semiconductores, bancos regionales…). También se elige por atención.

La regla de oro (marco CMF, innegociable): esto NO es consejo de inversión. Es
"lo que nuestros inversionistas IA están viendo o analizando". Por eso el formato
es CONTEXTO primero (qué ES la empresa/sector, factual) y luego un DEBATE de
arquetipos (miradas contrastantes), nunca un "nosotros le vemos potencial".

Este módulo solo SELECCIONA y arma los hechos (el número manda: la variación
viene de Yahoo, gratis). La voz la pone redaccion_ia.redactar_analisis, y el
correo lo dibuja boletin. Degradación elegante: si no hay datos, devuelve None
y el fin de semana cae a la edición normal (o a nada). NUNCA lanza.
"""

import json
import os

from contenido.fuentes import yahoo

# el universo curado vive junto al código; se puede crecer sin tocar Python
_RUTA_UNIVERSO = os.path.join(os.path.dirname(__file__), "config", "universo_semanal.json")

# cuántas sesiones (ruedas) atrás miramos para "la movida de la semana"
RUEDAS_SEMANA = 5


def cargar_universo(ruta: str | None = None) -> dict:
    """Lee el universo curado. Devuelve {} si falta o está roto (nunca lanza)."""
    try:
        with open(ruta or _RUTA_UNIVERSO, encoding="utf-8") as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except Exception:
        return {}


def elegir_modo(cuando: dict | None = None, semana_iso: int | None = None) -> str:
    """Turna 'accion' y 'sector' solo, semana a semana, para que la lectura del
    fin de semana no repita siempre lo mismo. Determinista (par/impar de la
    semana ISO), así el mismo sábado siempre da lo mismo (demos reproducibles)."""
    if semana_iso is None:
        from datetime import date
        semana_iso = date.today().isocalendar().week
    return "accion" if semana_iso % 2 == 0 else "sector"


def _movida(serie, ruedas: int = RUEDAS_SEMANA) -> dict | None:
    """A partir de (fechas, cierres) de ~1 mes, calcula la movida de la semana y
    del mes, y la etiqueta de fechas del gráfico. None si la serie es muy corta."""
    if not serie:
        return None
    fechas, cierres = serie
    if not cierres or len(cierres) < 2:
        return None
    ult = cierres[-1]
    ref_semana = cierres[-(ruedas + 1)] if len(cierres) > ruedas else cierres[0]
    var_semana = round((ult - ref_semana) / ref_semana * 100, 2) if ref_semana else None
    var_mes = round((ult - cierres[0]) / cierres[0] * 100, 2) if cierres[0] else None
    if var_semana is None:
        return None
    return {
        "var_semana_pct": var_semana,
        "var_mes_pct": var_mes,
        "ultimo": round(ult, 2),
        "fecha_inicio": yahoo.etiqueta_fecha(fechas[0]),
        "fecha_fin": yahoo.etiqueta_fecha(fechas[-1]),
    }


def _mayor_atencion(candidatos: list[dict], simbolo_de, fetch) -> dict | None:
    """De una lista de candidatos, devuelve el que MÁS se movió esta semana
    (en valor absoluto), enriquecido con su movida y su serie. None si ninguno
    trae datos (todos fallaron en Yahoo)."""
    mejor = None
    for c in candidatos:
        simbolo = simbolo_de(c)
        serie = fetch(simbolo, rango="1mo", intervalo="1d")
        movida = _movida(serie)
        if not movida:
            continue
        enriquecido = {**c, **movida, "serie": serie}
        if mejor is None or abs(movida["var_semana_pct"]) > abs(mejor["var_semana_pct"]):
            mejor = enriquecido
    return mejor


def _grafico_de(ticker: str, nombre: str) -> dict:
    """La especificación del gráfico del protagonista (periodo 'mes' para dar
    contexto: el fin de semana se lee con calma, no al minuto)."""
    return {"ticker": ticker, "nombre": nombre, "periodo": "mes", "moneda": "$"}


def seleccionar_accion(universo: dict, fetch=yahoo.serie_reciente) -> dict | None:
    """La 'acción seleccionada' del fin de semana: la mid-cap del universo que
    más llamó la atención esta semana. None si no hay datos."""
    acciones = universo.get("acciones") or []
    elegida = _mayor_atencion(acciones, lambda c: c.get("ticker", ""), fetch)
    if not elegida:
        return None
    return {
        "modo": "accion",
        "titulo": "Acción seleccionada",
        "encuadre": "mediana capitalización",
        "ticker": elegida["ticker"],
        "nombre": elegida["nombre"],
        "sector": elegida.get("sector", ""),
        "contexto": elegida.get("contexto", ""),
        "var_semana_pct": elegida["var_semana_pct"],
        "var_mes_pct": elegida.get("var_mes_pct"),
        "fecha_inicio": elegida["fecha_inicio"],
        "fecha_fin": elegida["fecha_fin"],
        "grafico": _grafico_de(elegida["ticker"], elegida["nombre"]),
    }


def seleccionar_sector(universo: dict, fetch=yahoo.serie_reciente) -> dict | None:
    """El 'sector en rotación' del fin de semana: el sector del universo que más
    se movió en bloque esta semana. None si no hay datos."""
    sectores = universo.get("sectores") or []
    elegido = _mayor_atencion(sectores, lambda c: c.get("etf", ""), fetch)
    if not elegido:
        return None
    return {
        "modo": "sector",
        "titulo": "Sector en rotación",
        "encuadre": "sector completo",
        "ticker": elegido["etf"],
        "nombre": elegido["nombre"],
        "sector": elegido["nombre"],
        "contexto": elegido.get("contexto", ""),
        "en_rotacion_por": elegido.get("en_rotacion_por", ""),
        "ejemplos": elegido.get("ejemplos", []),
        "var_semana_pct": elegido["var_semana_pct"],
        "var_mes_pct": elegido.get("var_mes_pct"),
        "fecha_inicio": elegido["fecha_inicio"],
        "fecha_fin": elegido["fecha_fin"],
        "grafico": _grafico_de(elegido["etf"], elegido["nombre"]),
    }


def preparar_analisis(universo: dict | None = None, modo: str | None = None,
                      cuando: dict | None = None, fetch=yahoo.serie_reciente) -> dict | None:
    """Arma los HECHOS del deep-dive del fin de semana (sin voz todavía).

    Elige el modo (turnándolo solo si no se fuerza), selecciona el protagonista
    por atención y devuelve el dict de hechos para el redactor y el correo. Si el
    modo elegido no trae datos, intenta el otro antes de rendirse. None si nada
    trae datos (entonces el fin de semana cae a la edición normal)."""
    universo = universo if universo is not None else cargar_universo()
    if not universo:
        return None
    modo = modo or elegir_modo(cuando)
    orden = [modo, "sector" if modo == "accion" else "accion"]  # el elegido, luego el otro
    for m in orden:
        sel = (seleccionar_accion if m == "accion" else seleccionar_sector)(universo, fetch)
        if sel:
            return sel
    return None
