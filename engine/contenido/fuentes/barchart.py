"""Capa de DATOS de mercado (La Redacción — el "cuánto").

Cliente de Barchart (u otra API de cotizaciones). Es la ÚNICA fuente de
números: precios y % de variación. El relato (el "por qué") viene de las
noticias; jamás al revés. Clave en el entorno: BARCHART_API_KEY.

Degradación elegante: sin clave o sin red, devuelve un snapshot de
demostración marcado como tal — la redacción nunca inventa cifras ni se
cae. Los % de demo son verosímiles pero NO reales (por eso van con
`fuente: "demo"` y el correo queda como borrador hasta tu visto bueno).
"""

import json
import os
from pathlib import Path

import httpx

URL_QUOTE = "https://ondemand.websol.barchart.com/getQuote.json"
RUTA_DEMO = Path(__file__).parent / "mercado_demo.json"

# el "mercado global" a cubrir al inicio (símbolo → nombre editorial)
INSTRUMENTOS = {
    "$SPX": "S&P 500",
    "$IUXX": "Nasdaq 100",
    "CLZ25": "Petróleo WTI",
    "GCZ25": "Oro",
    "NVDA": "Nvidia",
    "AAPL": "Apple",
}


def hay_credenciales() -> bool:
    return bool(os.environ.get("BARCHART_API_KEY"))


def _parsear(item: dict) -> dict | None:
    """Extrae de la respuesta de Barchart lo único que nos importa: el número."""
    try:
        return {
            "simbolo": item["symbol"],
            "ultimo": float(item["lastPrice"]),
            "variacion_pct": round(float(item["percentChange"]), 2),
        }
    except (KeyError, TypeError, ValueError):
        return None


def cotizaciones(simbolos: list[str] | None = None) -> tuple[list[dict], str]:
    """Devuelve ([{simbolo, nombre, ultimo, variacion_pct}], origen).

    origen ∈ {"barchart", "demo"}. Nunca lanza hacia la redacción.
    """
    simbolos = simbolos or list(INSTRUMENTOS)
    if hay_credenciales():
        try:
            respuesta = httpx.get(
                URL_QUOTE,
                params={
                    "apikey": os.environ["BARCHART_API_KEY"],
                    "symbols": ",".join(simbolos),
                    "fields": "lastPrice,percentChange",
                },
                timeout=15,
            )
            respuesta.raise_for_status()
            crudo = respuesta.json().get("results", [])
            datos = [d for d in (_parsear(i) for i in crudo) if d]
            if datos:
                for d in datos:
                    d["nombre"] = INSTRUMENTOS.get(d["simbolo"], d["simbolo"])
                return datos, "barchart"
        except Exception:
            pass  # degradación elegante
    # sin clave / sin datos: snapshot de demostración
    with open(RUTA_DEMO, encoding="utf-8") as archivo:
        demo = json.load(archivo)
    return demo, "demo"
