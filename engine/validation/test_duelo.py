"""Tests de la Etapa 10: el duelo de escenarios (backend)."""

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, pipeline, seguridad


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    limites.reiniciar()
    seguridad.reiniciar()


@pytest.fixture()
def dia():
    return pipeline.preparar_dia(semilla_base=42)


def test_duelo_devuelve_los_dos_resumenes(dia):
    cliente = TestClient(server.app)
    a, b = dia["publicadas"][0]["sim_id"], dia["publicadas"][1]["sim_id"]
    datos = cliente.get(f"/api/duelo/{a}/{b}").json()
    assert datos["a"]["id"] == a
    assert datos["b"]["id"] == b
    assert datos["a"]["titular"] and datos["b"]["titular"]
    assert datos["a"]["serie_precios"] and datos["b"]["serie_precios"]
    assert "asesoría" in datos["descargo"] or "asesoria" in datos["descargo"]
    assert "max-age" in cliente.get(f"/api/duelo/{a}/{b}").headers.get("Cache-Control", "")


def test_duelo_valida_los_ids(dia):
    cliente = TestClient(server.app)
    bueno = dia["publicadas"][0]["sim_id"]
    # id inválido → 404 (misma defensa anti path-traversal)
    assert cliente.get(f"/api/duelo/no-hex/{bueno}").status_code == 404
    assert cliente.get(f"/api/duelo/{bueno}/..%2f..%2fx").status_code == 404
    # id válido pero inexistente → 404
    assert cliente.get(f"/api/duelo/{bueno}/0000000000000000").status_code == 404


def test_duelo_reutiliza_el_payload_de_simulacion(dia):
    """El duelo trae lo mismo que /api/simulacion (voces incluidas)."""
    cliente = TestClient(server.app)
    a, b = dia["publicadas"][0]["sim_id"], dia["publicadas"][1]["sim_id"]
    datos = cliente.get(f"/api/duelo/{a}/{b}").json()
    assert len(datos["a"]["voces"]) == 8
    assert datos["a"]["tiene_replay"] is True
