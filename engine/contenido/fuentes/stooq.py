"""Precios históricos de Stooq — el plan B del backtest (sin clave).

Alpaca cubre desde ~2016; los exámenes más antiguos (Lehman 2008, la
rebaja del rating de EE.UU. 2011, el taper tantrum 2013…) se miden con
Stooq (stooq.com), que publica series diarias históricas en CSV público
sin autenticación. Misma semántica que alpaca.variacion_real:
base = último cierre ANTES de la fecha; final = cierre `ruedas` días de
mercado después. Devuelve None ante cualquier problema — nunca lanza.
"""

import csv
import io
from datetime import datetime, timedelta

import httpx

URL = "https://stooq.com/q/d/l/"


def variacion_real(simbolo: str, desde_iso: str, ruedas: int = 2) -> dict | None:
    if not simbolo:
        return None
    fecha = desde_iso[:10]
    try:
        d1 = (datetime.fromisoformat(fecha) - timedelta(days=7)).strftime("%Y%m%d")
        d2 = (datetime.fromisoformat(fecha) + timedelta(days=ruedas * 2 + 6)).strftime("%Y%m%d")
        respuesta = httpx.get(
            URL,
            params={"s": f"{simbolo.lower()}.us", "d1": d1, "d2": d2, "i": "d"},
            timeout=15,
        )
        respuesta.raise_for_status()
        filas = list(csv.DictReader(io.StringIO(respuesta.text)))
    except Exception:
        return None
    previas = [f for f in filas if f.get("Date", "") < fecha and f.get("Close")]
    posteriores = [f for f in filas if f.get("Date", "") >= fecha and f.get("Close")]
    if not previas or len(posteriores) < ruedas:
        return None
    try:
        base = float(previas[-1]["Close"])
        final = float(posteriores[ruedas - 1]["Close"])
    except (TypeError, ValueError):
        return None
    if not base:
        return None
    return {
        "simbolo": simbolo,
        "pct_real": round((final - base) / base * 100, 2),
        "cierre_base": base,
        "cierre_final": final,
        "fecha_base": previas[-1]["Date"],
        "fecha_final": posteriores[ruedas - 1]["Date"],
        "ruedas": ruedas,
        "fuente_datos": "stooq",
    }
