"""Tests del Modo Observatorio: el enjambre sigue vivo y recibe noticias
encima, sin frenar, sin congelarse y sin crecer en memoria."""

import json

import numpy as np
import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, seguridad
from model import MercadoEnjambre


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "50")
    limites.reiniciar()
    seguridad.reiniciar()


# ---------- comportamiento del motor a lo largo del tiempo ----------

def test_el_enjambre_no_se_congela_tras_la_noticia():
    """Después de reaccionar, el mercado SIGUE vivo (produce retornos)."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=400)
    m.correr(80)
    m.aplicar_titular("Amazon sube 15% tras resultados excelentes",
                      respuestas=[{"senal": 0.8, "confianza": 0.9, "frase": "x"}] * 100)
    m.correr(120)
    # el mercado sigue moviéndose bien pasada la reacción (no está estancado)
    retornos_tardios = m.retornos[-30:]
    assert np.std(retornos_tardios) > 0


def test_el_animo_se_desvanece_hacia_la_calma():
    """La noticia pierde fuerza con el tiempo: el ánimo vuelve a ~0."""
    m = MercadoEnjambre(seed=7, ticks_horizonte=400)
    m.correr(60)
    m.aplicar_titular("Pánico: quiebra un banco enorme",
                      respuestas=[{"senal": -0.9, "confianza": 0.9, "frase": "x"}] * 100)
    animo_inicial = abs(m.sentimiento)
    m.correr(80)
    assert abs(m.sentimiento) < animo_inicial * 0.2  # se desvaneció


def test_se_puede_soltar_una_segunda_noticia_encima():
    """Una noticia nueva reactiva al enjambre aunque la vieja se apagó."""
    m = MercadoEnjambre(seed=3, ticks_horizonte=500)
    m.correr(60)
    m.aplicar_titular("Quiebra un banco; pánico en el mercado",
                      respuestas=[{"senal": -0.8, "confianza": 0.9, "frase": "x"}] * 100)
    m.correr(60)  # se apaga
    assert abs(m.sentimiento) < 0.2
    m.aplicar_titular("La bolsa alcanza máximo histórico tras ganancias récord",
                      respuestas=[{"senal": 0.9, "confianza": 0.9, "frase": "x"}] * 100)
    assert m.sentimiento > 0.3  # la nueva noticia lo reactivó


def test_las_listas_no_crecen_sin_fin_en_sesiones_largas():
    m = MercadoEnjambre(seed=1, ticks_horizonte=2000)
    m.correr(1500)
    assert len(m.historial_precios) <= m.MAX_HISTORIAL + 1
    assert len(m.retornos) <= m.MAX_HISTORIAL
    # y el tick sigue avanzando aunque la cola esté acotada
    assert m.tick >= 1500


# ---------- el flujo por WebSocket ----------

def test_observatorio_late_y_recibe_una_noticia_encima():
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "tipo": "observatorio", "ritmo": 0.001,
            "titular": "Amazon sube 15% tras resultados",
        }))

        frames = 0
        inicio_visto = False
        arranque_visto = False
        for _ in range(300):
            m = ws.receive()
            if m.get("text"):
                dato = json.loads(m["text"])
                if dato["tipo"] == "observatorio-inicio":
                    arranque_visto = True
                elif dato["tipo"] == "inicio":
                    inicio_visto = True
                    assert len(dato["lideres"]) == 100
            elif m.get("bytes"):
                frames += 1
                assert len(m["bytes"]) == 8 + 5000
            if arranque_visto and inicio_visto and frames > 8:
                break

        assert arranque_visto  # el enjambre arrancó vivo
        assert inicio_visto    # leyó la noticia inicial
        assert frames > 8      # y siguió latiendo (transmitiendo)

        ws.send_text(json.dumps({"tipo": "detener"}))


def test_observatorio_respeta_el_tope_de_noticias(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "1")
    limites.reiniciar()
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"tipo": "observatorio", "ritmo": 0.001, "titular": "Primera"}))
        # la primera noticia consume el único cupo; la segunda debe toparse
        ws.send_text(json.dumps({"tipo": "noticia", "titular": "Segunda noticia"}))
        limite_visto = False
        for _ in range(400):
            m = ws.receive()
            if m.get("text") and json.loads(m["text"]).get("tipo") == "limite":
                limite_visto = True
                break
        ws.send_text(json.dumps({"tipo": "detener"}))
    assert limite_visto
