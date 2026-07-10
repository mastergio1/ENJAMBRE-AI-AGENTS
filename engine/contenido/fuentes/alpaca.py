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
            "fuente": "alpaca",
            "simbolos": ",".join(n.get("symbols", [])),
            "fecha": n.get("created_at", ""),
        }
        for n in noticias
        if n.get("headline")
    ]


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
