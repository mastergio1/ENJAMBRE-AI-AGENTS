"""Tests del canal B2B (formulario de organizaciones) — Sprint 3."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import server
from contenido import limites, persistencia, seguridad, vocabulario


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)  # sin red en tests
    seguridad.reiniciar()
    limites.reiniciar()


def test_contacto_se_guarda_y_responde_amable():
    cliente = TestClient(server.app)
    r = cliente.post("/api/contacto", json={
        "nombre": "Ana Profesora", "email": "ana@colegio.cl",
        "organizacion": "Colegio X", "mensaje": "Quiero usarlo en mi curso.",
    })
    assert r.status_code == 200
    assert r.json()["estado"] == "recibido"

    conexion = persistencia.conectar()
    guardados = persistencia.listar_contactos(conexion)
    conexion.close()
    assert len(guardados) == 1
    assert guardados[0]["email"] == "ana@colegio.cl"
    assert guardados[0]["organizacion"] == "Colegio X"


def test_contacto_valida_entradas():
    cliente = TestClient(server.app)
    assert cliente.post("/api/contacto", json={"nombre": "", "email": "a@b.cl"}).status_code == 400
    assert cliente.post("/api/contacto", json={"nombre": "Ana", "email": "no-es-correo"}).status_code == 400
    # entradas gigantes se recortan, no rompen
    r = cliente.post("/api/contacto", json={
        "nombre": "Ana", "email": "ana@b.cl", "mensaje": "x" * 5000,
    })
    assert r.status_code == 200
    conexion = persistencia.conectar()
    assert len(persistencia.listar_contactos(conexion)[0]["mensaje"]) <= 800
    conexion.close()


def test_lista_de_contactos_exige_token(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    cliente = TestClient(server.app)
    assert cliente.get("/api/contactos").status_code == 403
    ok = cliente.get("/api/contactos", headers={"X-Pipeline-Token": "secreto-de-prueba"})
    assert ok.status_code == 200
    assert ok.json()["contactos"] == []


def test_seccion_organizaciones_es_cmf_limpia():
    """El CTA B2B no usa lenguaje de recomendación de inversión (guard)."""
    muro = (Path(__file__).parent.parent.parent / "web" / "src" / "muro" / "muro.js").read_text(encoding="utf-8")
    inicio = muro.find('class="organizaciones"')
    assert inicio > 0, "la sección de organizaciones existe en el muro"
    seccion = muro[inicio:inicio + 1200]
    assert vocabulario.es_publicable(seccion)
    assert "educativa" in seccion  # el posicionamiento educativo, explícito