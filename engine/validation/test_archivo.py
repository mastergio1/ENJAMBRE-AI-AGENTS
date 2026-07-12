"""Tests de la Etapa 9: El Archivo — hemeroteca, búsqueda, voces, epílogo."""

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, persistencia, pipeline, seguridad


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
    """3 destacadas guardadas (con sus titulares vinculados = simbolos)."""
    return pipeline.preparar_dia(semilla_base=42)


# ---------- la consulta del archivo ----------

def test_archivo_lista_destacadas(dia):
    conexion = persistencia.conectar()
    resultado = persistencia.archivo(conexion)
    conexion.close()
    assert resultado["total"] == 3
    assert len(resultado["items"]) == 3
    assert all(item["fecha"] for item in resultado["items"])


def test_archivo_busca_por_texto(dia):
    conexion = persistencia.conectar()
    # los titulares demo incluyen "Treasury yields spike..."
    r = persistencia.archivo(conexion, texto="treasury")
    conexion.close()
    assert r["total"] == 1
    assert "Treasury" in r["items"][0]["titular"]


def test_archivo_filtra_por_ticker(dia):
    conexion = persistencia.conectar()
    # "Regional bank First Meridian collapses" trae simbolos FMRD,KRE
    r = persistencia.archivo(conexion, ticker="KRE")
    conexion.close()
    assert r["total"] == 1
    assert "FMRD" in (r["items"][0]["simbolos"] or "")


def test_archivo_pagina(dia):
    conexion = persistencia.conectar()
    p0 = persistencia.archivo(conexion, por_pagina=2, pagina=0)
    p1 = persistencia.archivo(conexion, por_pagina=2, pagina=1)
    conexion.close()
    assert p0["total"] == 3
    assert len(p0["items"]) == 2
    assert len(p1["items"]) == 1
    assert p0["items"][0]["id"] != p1["items"][0]["id"]


def test_meses_disponibles(dia):
    conexion = persistencia.conectar()
    meses = persistencia.meses_disponibles(conexion)
    conexion.close()
    assert len(meses) == 1
    assert meses[0] == persistencia.ahora_iso()[:7]


# ---------- el endpoint del archivo ----------

def test_api_archivo(dia):
    cliente = TestClient(server.app)
    datos = cliente.get("/api/archivo").json()
    assert datos["total"] == 3
    assert len(datos["items"]) == 3
    assert datos["meses"]
    item = datos["items"][0]
    assert item["tarjeta"]["direccion"] in "▲▼◆"
    assert item["tarjeta"]["agitacion"] in ("bajo", "medio", "alto")
    assert "asesoría" in datos["descargo"] or "asesoria" in datos["descargo"]
    assert "max-age" in cliente.get("/api/archivo").headers.get("Cache-Control", "")


def test_api_archivo_busca_y_filtra(dia):
    cliente = TestClient(server.app)
    assert cliente.get("/api/archivo", params={"q": "oil"}).json()["total"] == 1
    assert cliente.get("/api/archivo", params={"ticker": "USO"}).json()["total"] == 1
    assert cliente.get("/api/archivo", params={"q": "no-existe-nada"}).json()["total"] == 0


# ---------- las 8 voces en la página de una simulación ----------

def test_simulacion_incluye_ocho_voces(dia):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    datos = cliente.get(f"/api/simulacion/{sim_id}").json()
    voces = datos["voces"]
    assert len(voces) == 8  # los 8 arquetipos
    for voz in voces:
        assert -1.0 <= voz["senal_media"] <= 1.0
        assert voz["frase"]
        assert voz["nombre"]
    # vienen ordenadas de la señal más baja (más bajista) a la más alta
    assert voces == sorted(voces, key=lambda v: v["senal_media"])


# ---------- '¿y qué pasó después?' (epílogo, protegido) ----------

def test_epilogo_exige_token(dia, monkeypatch):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")

    # sin token → 403
    assert cliente.post(f"/api/epilogo/{sim_id}", json={"texto": "x"}).status_code == 403
    # con token → guarda y aparece en la simulación
    r = cliente.post(f"/api/epilogo/{sim_id}", json={"texto": "El IPSA cerró -1,2% ese día."},
                     headers={"X-Pipeline-Token": "secreto"})
    assert r.status_code == 200
    datos = cliente.get(f"/api/simulacion/{sim_id}").json()
    assert "IPSA" in datos["epilogo"]


def test_epilogo_rechaza_vocabulario_prohibido(dia, monkeypatch):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    r = cliente.post(f"/api/epilogo/{sim_id}",
                     json={"texto": "Esto confirma nuestra predicción de compra"},
                     headers={"X-Pipeline-Token": "secreto"})
    assert r.status_code == 400  # el filtro CMF lo bloquea
