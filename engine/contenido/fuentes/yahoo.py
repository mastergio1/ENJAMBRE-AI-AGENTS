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


_MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago",
             "sep", "oct", "nov", "dic"]


def etiqueta_fecha(dt: datetime) -> str:
    """'7 ago' — etiqueta corta en español para los ejes del gráfico."""
    return f"{dt.day} {_MESES_ES[dt.month - 1]}"


def serie_reciente(simbolo: str, rango: str = "5d", intervalo: str = "1d"):
    """(fechas, cierres) recientes de un símbolo, para dibujar su gráfico.
    `rango` e `intervalo` en la jerga de Yahoo (5d/1mo/1y, 1d/15m…).
    Devuelve (list[datetime], list[float]) o None ante cualquier problema."""
    try:
        respuesta = httpx.get(
            URL.format(simbolo=simbolo),
            params={"range": rango, "interval": intervalo},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        respuesta.raise_for_status()
        r = respuesta.json()["chart"]["result"][0]
        marcas = r["timestamp"]
        cierres = r["indicators"]["quote"][0]["close"]
    except Exception:
        return None
    pares = [(datetime.utcfromtimestamp(ts), float(c))
             for ts, c in zip(marcas, cierres) if c is not None]
    if len(pares) < 2:
        return None
    return [p[0] for p in pares], [p[1] for p in pares]


# ---------- fundamentales (para el análisis de fin de semana) ----------
# El endpoint quoteSummary pide un "crumb" (cookie + token). Lo pedimos una vez
# por proceso y lo reusamos. Si el flujo falla, fundamentales() devuelve None y
# el deep-dive sale SIN el bloque de números (nunca inventa cifras).

_URL_CRUMB = "https://query1.finance.yahoo.com/v1/test/getcrumb"
_URL_RESUMEN = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{simbolo}"
_UA_NAV = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/120 Safari/537.36")
_MODULOS = "financialData,defaultKeyStatistics,summaryDetail,price"

_crumb_cache: dict = {"cliente": None, "crumb": None}


def _sesion_crumb():
    """(cliente httpx con cookie, crumb) reutilizable. None si no se pudo obtener."""
    if _crumb_cache["crumb"]:
        return _crumb_cache["cliente"], _crumb_cache["crumb"]
    try:
        cliente = httpx.Client(headers={"User-Agent": _UA_NAV}, timeout=15, follow_redirects=True)
        cliente.get("https://fc.yahoo.com")  # siembra la cookie (puede dar 404, da igual)
        crumb = cliente.get(_URL_CRUMB).text.strip()
        # un crumb válido es un token corto sin espacios ni HTML
        if not crumb or len(crumb) > 40 or "<" in crumb or " " in crumb:
            cliente.close()
            return None, None
        _crumb_cache["cliente"], _crumb_cache["crumb"] = cliente, crumb
        return cliente, crumb
    except Exception:
        return None, None


_URL_SCREENER = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"


def _valor(nodo):
    """El número crudo de un campo de Yahoo, sea {raw,fmt} o un número pelado."""
    if isinstance(nodo, dict):
        return nodo.get("raw")
    return nodo if isinstance(nodo, (int, float)) else None


def movers_del_dia(n: int = 8, min_pct: float = 5.0) -> list[dict]:
    """Los mayores movimientos del día del mercado de EE.UU. (gainers + losers):
    lista de {ticker, nombre, var_pct, precio}, los más movidos primero. Es lo que
    de verdad movió al mercado hoy, no solo lo que un feed decidió titular. [] ante
    cualquier problema (degradación elegante). Nunca lanza."""
    cliente, crumb = _sesion_crumb()
    if not cliente or not crumb:
        return []
    vistos: set[str] = set()
    movimientos: list[dict] = []
    for tablero in ("day_gainers", "day_losers"):
        try:
            r = cliente.get(_URL_SCREENER,
                            params={"count": 25, "scrIds": tablero, "crumb": crumb})
            if r.status_code != 200:
                continue
            res = (r.json().get("finance", {}).get("result") or [None])[0]
            quotes = (res or {}).get("quotes") or []
        except Exception:
            continue
        for q in quotes:
            tk = str(q.get("symbol", "")).strip().upper()
            pct = _valor(q.get("regularMarketChangePercent"))
            if not tk or tk in vistos or not isinstance(pct, (int, float)):
                continue
            if abs(pct) < min_pct:  # ignora ruido: solo movimientos con peso
                continue
            vistos.add(tk)
            movimientos.append({
                "ticker": tk,
                "nombre": str(q.get("shortName") or q.get("longName") or tk)[:60],
                "var_pct": round(float(pct), 2),
                "precio": _valor(q.get("regularMarketPrice")),
            })
    movimientos.sort(key=lambda m: abs(m["var_pct"]), reverse=True)
    return movimientos[:n]


def _fmt(nodo) -> str | None:
    """El texto formateado de un campo de Yahoo ({raw, fmt}); None si no hay dato."""
    if isinstance(nodo, dict):
        f = nodo.get("fmt")
        return f if f else None
    return None


def _num(nodo) -> float | None:
    return nodo.get("raw") if isinstance(nodo, dict) and isinstance(nodo.get("raw"), (int, float)) else None


def fundamentales(simbolo: str) -> dict | None:
    """Los fundamentales VERIFICADos de una empresa (para el análisis de fin de
    semana): capitalización, ingresos y su crecimiento, márgenes, EBITDA, deuda y
    caja. Los valores van formateados (para mostrar) tal como los da Yahoo. None
    ante cualquier problema o si es un instrumento sin fundamentales (un ETF).
    Nunca lanza."""
    cliente, crumb = _sesion_crumb()
    if not cliente or not crumb:
        return None
    try:
        r = cliente.get(_URL_RESUMEN.format(simbolo=simbolo),
                        params={"modules": _MODULOS, "crumb": crumb})
        if r.status_code != 200:
            return None
        res = (r.json().get("quoteSummary", {}).get("result") or [None])[0]
        if not res:
            return None
    except Exception:
        return None
    fd = res.get("financialData", {}) or {}
    sd = res.get("summaryDetail", {}) or {}
    price = res.get("price", {}) or {}

    cap_num = _num(sd.get("marketCap")) or _num(price.get("marketCap"))
    ingresos = _fmt(fd.get("totalRevenue"))
    ebitda = _fmt(fd.get("ebitda"))
    # sin ingresos ni EBITDA no hay ficha que valga (típico de ETFs/índices)
    if ingresos is None and ebitda is None:
        return None
    datos = {
        "market_cap": _fmt(sd.get("marketCap")) or _fmt(price.get("marketCap")),
        "market_cap_num": cap_num,
        "ingresos": ingresos,
        "crecimiento_ingresos": _fmt(fd.get("revenueGrowth")),
        "ebitda": ebitda,
        "margen_bruto": _fmt(fd.get("grossMargins")),
        "margen_operativo": _fmt(fd.get("operatingMargins")),
        "margen_neto": _fmt(fd.get("profitMargins")),
        "deuda": _fmt(fd.get("totalDebt")),
        "caja": _fmt(fd.get("totalCash")),
        "flujo_caja_libre": _fmt(fd.get("freeCashflow")),
    }
    # descarta claves sin dato para no arrastrar None hasta la plantilla
    return {k: v for k, v in datos.items() if v is not None}


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
