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
