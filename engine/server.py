"""Servidor de El Enjambre — FastAPI + WebSocket.

Etapa 0: solo un esqueleto que confirma que el entorno funciona.
El motor de simulación se conectará aquí en la Etapa 1.
"""

import json
from pathlib import Path

from fastapi import FastAPI

RUTA_CONFIG = Path(__file__).parent / "config" / "agentes.json"

app = FastAPI(title="El Enjambre", version="0.1.0")


def cargar_config() -> dict:
    """Carga la mezcla de agentes desde config/agentes.json."""
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        return json.load(f)


@app.get("/salud")
def salud() -> dict:
    """Confirma que el servidor está vivo y la configuración es válida."""
    config = cargar_config()
    total = sum(t["cantidad"] for t in config["tipos"])
    return {
        "estado": "ok",
        "proyecto": "El Enjambre",
        "etapa": 0,
        "agentes_configurados": total,
    }
