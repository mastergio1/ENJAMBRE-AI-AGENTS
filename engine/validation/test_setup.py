"""Tests de la Etapa 0: la configuración de agentes es coherente con CLAUDE.md.

Los tests de hechos estilizados (colas gordas, clustering de volatilidad, etc.)
se agregarán en la Etapa 1, cuando exista el motor.
"""

import json
from pathlib import Path

RUTA_CONFIG = Path(__file__).parent.parent / "config" / "agentes.json"


def cargar_config() -> dict:
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        return json.load(f)


def test_la_mezcla_suma_5000_agentes():
    config = cargar_config()
    total = sum(t["cantidad"] for t in config["tipos"])
    assert total == config["total_agentes"] == 5000


def test_hay_13_tipos_de_agentes():
    config = cargar_config()
    assert len(config["tipos"]) == 13


def test_los_arquetipos_de_lideres_suman_100():
    config = cargar_config()
    lideres = next(t for t in config["tipos"] if t["id"] == "lider_opinion")
    total_arquetipos = sum(a["cantidad"] for a in lideres["arquetipos"])
    assert total_arquetipos == lideres["cantidad"] == 100
    assert len(lideres["arquetipos"]) == 8


def test_los_institucionales_no_estan_en_la_red_social():
    """CLAUDE.md sección 6: los tipos 1-3 no reaccionan a rumores."""
    config = cargar_config()
    institucionales = ["fundamentalista", "quant_momentum", "fondo_pasivo"]
    for tipo in config["tipos"]:
        if tipo["id"] in institucionales:
            assert tipo["en_red_social"] is False


def test_el_servidor_responde_salud():
    from fastapi.testclient import TestClient

    import server

    cliente = TestClient(server.app)
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"
