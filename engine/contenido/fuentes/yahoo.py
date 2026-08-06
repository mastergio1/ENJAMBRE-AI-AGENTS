"""Precios históricos de Yahoo Finance — la fuente robusta del backtest.

Reemplaza a Stooq (cuya API de descarga dejó de responder). Yahoo cubre
acciones, ETFs y cripto con histórico largo y sin clave: SPY desde los 90,
GBTC/COIN, GLD, USO, y hasta BTC-USD directo. Misma semántica que
alpaca.variacion_real: base = último cierre ANTES de la fecha de la
noticia; final = cierre `ruedas` días de mercado después.

Devuelve None ante cualquier problema — nunca lanza.
"""

from datetime import datetime

import httpx

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"

# el "telón de fondo" del diario en símbolos Yahoo (símbolo → nombre editorial).
# Los índices y materias primas siempre relevantes; las acciones del día se
# consultan por su ticker directo (NVDA, AAPL…), que Yahoo acepta tal cual.
NOMBRES = {
    "^GSPC": "S&P 500", "^IXIC": "Nasdaq 100", "^DJI": "Dow Jones",
    "CL=F": "Petróleo WTI", "GC=F": "Oro", "BTC-USD": "Bitcoin",
}


def _serie_anual(simbolo: str) -> list[float] | None:
    """Los cierres diarios del último año (viejo → nuevo). None ante fallo."""
    try:
        respuesta = httpx.get(
            URL.format(simbolo=simbolo),
            params={"range": "1y", "interval": "1d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        respuesta.raise_for_status()
        resultado = respuesta.json()["chart"]["result"][0]
        cierres = resultado["indicators"]["quote"][0]["close"]
    except Exception:
        return None
    limpios = [float(c) for c in cierres if c is not None]
    return limpios if len(limpios) >= 2 else None


def _pct(nuevo: float, viejo: float) -> float | None:
    return round((nuevo - viejo) / viejo * 100, 2) if viejo else None


def _variaciones(cierres: list[float]) -> dict | None:
    """Día/Mes/Año a partir de la serie anual de cierres."""
    if len(cierres) < 2:
        return None
    ult = cierres[-1]
    return {
        "ultimo": round(ult, 2),
        "variacion_pct": _pct(ult, cierres[-2]),                       # día
        "var_mes_pct": _pct(ult, cierres[-22]) if len(cierres) >= 22 else None,  # ~1 mes
        "var_ano_pct": _pct(ult, cierres[0]),                          # ~1 año
    }


def cotizaciones(simbolos: list[str]) -> tuple[list[dict], str]:
    """Cotizaciones de HOY desde Yahoo (gratis): [{simbolo, nombre, ultimo,
    variacion_pct, var_mes_pct, var_ano_pct}], origen 'yahoo'. Una llamada por
    símbolo; los que fallan se omiten. Nunca lanza hacia la redacción."""
    datos = []
    for simbolo in simbolos:
        serie = _serie_anual(simbolo)
        if not serie:
            continue
        var = _variaciones(serie)
        if not var:
            continue
        datos.append({"simbolo": simbolo, "nombre": NOMBRES.get(simbolo, simbolo), **var})
    return datos, "yahoo"


def variacion_real(simbolo: str, desde_iso: str, ruedas: int = 2) -> dict | None:
    if not simbolo:
        return None
    fecha = desde_iso[:10]
    try:
        base_dt = datetime.fromisoformat(fecha)
        # margen amplio: cubre fines de semana, feriados y la ventana futura
        p1 = int(base_dt.timestamp()) - 12 * 86400
        p2 = int(base_dt.timestamp()) + (ruedas * 2 + 10) * 86400
        respuesta = httpx.get(
            URL.format(simbolo=simbolo),
            params={"period1": p1, "period2": p2, "interval": "1d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        respuesta.raise_for_status()
        resultado = respuesta.json()["chart"]["result"][0]
        marcas = resultado["timestamp"]
        cierres = resultado["indicators"]["quote"][0]["close"]
    except Exception:
        return None

    # (fecha_iso, cierre) de cada rueda con dato válido
    barras = []
    for ts, cierre in zip(marcas, cierres):
        if cierre is None:
            continue
        dia = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        barras.append((dia, float(cierre)))

    previas = [b for b in barras if b[0] < fecha]
    posteriores = [b for b in barras if b[0] >= fecha]
    if not previas or len(posteriores) < ruedas:
        return None

    fecha_base, base = previas[-1]
    fecha_final, final = posteriores[ruedas - 1]
    if not base:
        return None
    return {
        "simbolo": simbolo,
        "pct_real": round((final - base) / base * 100, 2),
        "cierre_base": round(base, 2),
        "cierre_final": round(final, 2),
        "fecha_base": fecha_base,
        "fecha_final": fecha_final,
        "ruedas": ruedas,
        "fuente_datos": "yahoo",
    }
