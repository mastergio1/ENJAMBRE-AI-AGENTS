"""Cliente de Alpaca News API (titulares de Benzinga, tier gratuito).

Claves en el entorno: ALPACA_API_KEY_ID y ALPACA_API_SECRET_KEY.
Sin claves o sin red, devuelve lista vacía — degradación elegante:
el pipeline usará las simulaciones de ayer y el muro lo dirá con fecha.

El streaming por WebSocket (wss://stream.data.alpaca.markets/v1beta1/news)
queda para la fase de tiempo real; el ritual de la madrugada usa REST.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

URL_NOTICIAS = "https://data.alpaca.markets/v1beta1/news"
URL_BARRAS = "https://data.alpaca.markets/v2/stocks/{simbolo}/bars"
RUTA_DEMO = Path(__file__).parent / "titulares_demo.json"


def hay_credenciales() -> bool:
    return bool(os.environ.get("ALPACA_API_KEY_ID") and os.environ.get("ALPACA_API_SECRET_KEY"))


def titulares_recientes(horas: int = 18, limite: int = 50) -> list[dict]:
    """Los titulares de las últimas `horas` desde Alpaca (REST).

    Devuelve [{"titular", "fuente", "simbolos", "fecha"}]; vacía si no hay
    credenciales o la API no responde (nunca lanza hacia el pipeline).
    """
    if not hay_credenciales():
        return []
    desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat(timespec="seconds")
    try:
        respuesta = httpx.get(
            URL_NOTICIAS,
            params={"start": desde, "limit": limite, "sort": "desc"},
            headers={
                "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY_ID"],
                "APCA-API-SECRET-KEY": os.environ["ALPACA_API_SECRET_KEY"],
            },
            timeout=15,
        )
        respuesta.raise_for_status()
        noticias = respuesta.json().get("news", [])
    except Exception:
        return []  # degradación elegante: el muro mostrará lo de ayer
    return [
        {
            "titular": n.get("headline", "").strip(),
            "fuente": n.get("source", "alpaca"),
            "url": n.get("url", ""),
            "simbolos": ",".join(n.get("symbols", [])),
            "fecha": n.get("created_at", ""),
        }
        for n in noticias
        if n.get("headline")
    ]


def variacion_real(simbolo: str, desde_iso: str, ruedas: int = 2) -> dict | None:
    """Cuánto se movió el símbolo EN EL MERCADO REAL alrededor de una fecha.

    Para el corrector automático (calibración): base = último cierre ANTES
    de la fecha de la noticia (el mercado aún no la veía); final = cierre
    `ruedas` días de mercado después. Barras diarias del feed IEX (incluido
    en el tier gratuito de Alpaca).

    Devuelve None si no hay claves, red o todavía no pasaron `ruedas`
    días de mercado — el corrector simplemente reintenta en la próxima
    corrida. Nunca lanza.
    """
    if not hay_credenciales() or not simbolo:
        return None
    fecha = desde_iso[:10]
    # margen ancho: fines de semana y feriados no tienen barra
    inicio = (datetime.fromisoformat(fecha) - timedelta(days=7)).strftime("%Y-%m-%d")
    fin = (datetime.fromisoformat(fecha) + timedelta(days=ruedas * 2 + 6)).strftime("%Y-%m-%d")
    try:
        respuesta = httpx.get(
            URL_BARRAS.format(simbolo=simbolo),
            params={"timeframe": "1Day", "start": inicio, "end": fin,
                    "feed": "iex", "adjustment": "raw", "limit": 50},
            headers={
                "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY_ID"],
                "APCA-API-SECRET-KEY": os.environ["ALPACA_API_SECRET_KEY"],
            },
            timeout=15,
        )
        respuesta.raise_for_status()
        barras = respuesta.json().get("bars") or []
    except Exception:
        return None
    previas = [b for b in barras if b.get("t", "")[:10] < fecha]
    posteriores = [b for b in barras if b.get("t", "")[:10] >= fecha]
    # sin cierre previo, o aún no se completa la ventana: esperar
    if not previas or len(posteriores) < ruedas:
        return None
    base = previas[-1]
    final = posteriores[ruedas - 1]
    if not base.get("c"):
        return None
    pct = (final["c"] - base["c"]) / base["c"] * 100
    return {
        "simbolo": simbolo,
        "pct_real": round(pct, 2),
        "cierre_base": base["c"],
        "cierre_final": final["c"],
        "fecha_base": base["t"][:10],
        "fecha_final": final["t"][:10],
        "ruedas": ruedas,
    }


def titulares_demo() -> list[dict]:
    """Un día realista de titulares para desarrollo y pruebas sin claves."""
    with open(RUTA_DEMO, encoding="utf-8") as archivo:
        return json.load(archivo)


def obtener_titulares(horas: int = 18, limite: int = 50) -> tuple[list[dict], str]:
    """Titulares reales si hay claves; si no, el set de demo.

    Devuelve (titulares, origen) donde origen ∈ {"alpaca", "demo"}.
    """
    reales = titulares_recientes(horas, limite)
    if reales:
        return reales, "alpaca"
    return titulares_demo(), "demo"
