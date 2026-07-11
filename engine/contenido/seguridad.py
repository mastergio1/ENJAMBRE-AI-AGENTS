"""Blindaje HTTP de El Enjambre.

Reúne las murallas de la capa web pública: identidad real del cliente
detrás del proxy, rate-limiting por IP, validación de identificadores y
las cabeceras de seguridad. Estado en memoria: suficiente para una
instancia (el deploy actual en Render).
"""

import re
import time
from collections import deque

# los ids de simulación son sha256 recortado a 16 hex — nada más se acepta
HEX16 = re.compile(r"^[0-9a-f]{16}$")

# ---------- identidad real del cliente ----------

def sim_id_valido(sim_id: str | None) -> bool:
    return bool(sim_id and HEX16.match(sim_id))


def ip_cliente(headers, fallback: str | None) -> str:
    """La IP real del visitante detrás de EXACTAMENTE un proxy (Render).

    Render añade la IP que observa al final de X-Forwarded-For. Tomar el
    último salto anula el spoofing: si el cliente falsifica el header,
    Render igual agrega su IP real después, y esa es la que contamos.
    """
    xff = headers.get("x-forwarded-for") if headers else None
    if xff:
        partes = [p.strip() for p in xff.split(",") if p.strip()]
        if partes:
            return partes[-1]
    return fallback or "desconocida"


# ---------- rate-limiting HTTP (ventana deslizante por IP) ----------

# (máximo de solicitudes, ventana en segundos)
LIMITE_GENERAL = (120, 60)   # /api/* liviano
LIMITE_PESADO = (30, 60)     # /replay: 734 KB de disco por llamada

_ventanas: dict[str, deque] = {}


def _clase(ruta: str) -> str:
    return "replay" if ruta.endswith("/replay") else "api"


def permitir_http(ip: str, ruta: str, ahora: float | None = None) -> bool:
    """¿Puede esta IP hacer esta request ahora? (rate-limit deslizante)."""
    ahora = time.monotonic() if ahora is None else ahora
    clase = _clase(ruta)
    limite, ventana = LIMITE_PESADO if clase == "replay" else LIMITE_GENERAL
    cola = _ventanas.setdefault(f"{ip}|{clase}", deque())
    corte = ahora - ventana
    while cola and cola[0] < corte:
        cola.popleft()
    if len(cola) >= limite:
        return False
    cola.append(ahora)
    return True


def limpiar(ahora: float | None = None) -> None:
    """Descarta ventanas vencidas — evita que _ventanas crezca sin fin."""
    ahora = time.monotonic() if ahora is None else ahora
    for clave in list(_ventanas):
        cola = _ventanas[clave]
        while cola and cola[0] < ahora - 120:
            cola.popleft()
        if not cola:
            del _ventanas[clave]


def reiniciar() -> None:
    """Borra el estado (para los tests)."""
    _ventanas.clear()


# ---------- cabeceras de seguridad ----------

# la API sirve JSON y binario consumidos por fetch: default-src 'none' basta.
# (La CSP de la página HTML vive en web/vercel.json, no aquí.)
CABECERAS_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}
