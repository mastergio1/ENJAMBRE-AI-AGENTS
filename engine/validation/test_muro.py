"""Tests de la Etapa 7: el muro — endpoints, pipeline del día y límites."""

import json

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, persistencia, pipeline


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    monkeypatch.delenv("ENJAMBRE_MAX_SIM_DIA", raising=False)
    limites.reiniciar()


@pytest.fixture(scope="function")
def dia_preparado():
    """Corre el pipeline una vez: 3 destacadas simuladas con frames."""
    return pipeline.preparar_dia(semilla_base=42)


def test_pipeline_prepara_el_dia(dia_preparado):
    assert len(dia_preparado["publicadas"]) == 3
    conexion = persistencia.conectar()
    destacadas = persistencia.listar_simulaciones(conexion, solo_destacadas=True)
    conexion.close()
    assert len(destacadas) == 3
    # la regla del replay: las destacadas conservan sus frames binarios
    for publicada in dia_preparado["publicadas"]:
        frames = persistencia.leer_frames(publicada["sim_id"])
        assert frames is not None
        assert len(frames) == (server.TICKS_PREVIOS + server.TICKS_POSTERIORES) * (8 + 5000)


def test_pipeline_es_idempotente(dia_preparado):
    """Correrlo dos veces el mismo día no gasta de nuevo (presupuesto)."""
    segunda = pipeline.preparar_dia(semilla_base=42)
    assert segunda["publicadas"] == []
    conexion = persistencia.conectar()
    assert len(persistencia.listar_simulaciones(conexion, solo_destacadas=True)) == 3
    conexion.close()


def test_api_muro_muestra_tarjetas(dia_preparado):
    cliente = TestClient(server.app)
    datos = cliente.get("/api/muro").json()
    tarjetas = datos["tarjetas"]
    assert len(tarjetas) >= 6  # 3 destacadas + pendientes de impacto alto

    # destacadas primero, con su resumen editorial completo
    for tarjeta in tarjetas[:3]:
        assert tarjeta["estado"] == "simulada"
        assert tarjeta["destacada"] is True
        assert tarjeta["resumen"]["direccion"] in "▲▼◆"
        assert tarjeta["resumen"]["agitacion"] in ("bajo", "medio", "alto")
        assert tarjeta["resumen"]["frase"]["frase"]

    # las pendientes existen (Estado B) y las descartadas no aparecen
    pendientes = [t for t in tarjetas if t["estado"] == "pendiente"]
    assert pendientes
    titulares = " ".join(t["titular"] for t in tarjetas)
    assert "Celebrity chef" not in titulares  # Estado C: fuera del muro

    from contenido.vocabulario import DISCLAIMER
    assert datos["descargo"] == DISCLAIMER


def test_api_simulacion_y_replay(dia_preparado):
    cliente = TestClient(server.app)
    sim_id = dia_preparado["publicadas"][0]["sim_id"]

    detalle = cliente.get(f"/api/simulacion/{sim_id}").json()
    assert detalle["destacada"] is True
    assert detalle["tiene_replay"] is True
    assert len(detalle["serie_precios"]) == 151
    assert detalle["resumen"]["descargo"]

    replay = cliente.get(f"/api/simulacion/{sim_id}/replay")
    assert replay.status_code == 200
    assert len(replay.content) == 150 * 5008

    assert cliente.get("/api/simulacion/no-existe").status_code == 404
    assert cliente.get("/api/simulacion/no-existe/replay").status_code == 404


def test_api_simular_titular_pendiente(dia_preparado):
    cliente = TestClient(server.app)
    tarjetas = cliente.get("/api/muro").json()["tarjetas"]
    pendiente = next(t for t in tarjetas if t["estado"] == "pendiente")

    respuesta = cliente.post("/api/simular-titular", json={"id": pendiente["id"]}).json()
    assert respuesta["estado"] == "adelante"
    assert respuesta["titular"] == pendiente["titular"]

    # una ya simulada devuelve directo su sim_id (caché, costo cero)
    simulada = next(t for t in tarjetas if t["estado"] == "simulada")
    respuesta = cliente.post("/api/simular-titular", json={"id": simulada["id"]}).json()
    assert respuesta == {"estado": "simulada", "sim_id": simulada["sim_id"]}

    assert cliente.post("/api/simular-titular", json={"id": "no-existe"}).status_code == 404


def test_limite_por_ip():
    for _ in range(5):
        permitido, _ = limites.permitir("1.2.3.4")
        assert permitido
    permitido, motivo = limites.permitir("1.2.3.4")
    assert not permitido
    assert motivo == limites.MENSAJE_IP
    # otra IP sigue pudiendo
    assert limites.permitir("5.6.7.8")[0]


def test_tope_global_diario(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "2")
    assert limites.permitir("a")[0]
    assert limites.permitir("b")[0]
    permitido, motivo = limites.permitir("c")
    assert not permitido
    assert motivo == limites.MENSAJE_GLOBAL


def test_websocket_respeta_el_tope(monkeypatch):
    """Agotado el presupuesto del día, el canal responde 'limite' sin gastar."""
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "0")
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"tipo": "simular", "titular": "Prueba", "ritmo": 0}))
        mensaje = json.loads(ws.receive_text())
        assert mensaje["tipo"] == "limite"
        assert "Pulso" in mensaje["mensaje"]


def test_simulacion_del_muro_vincula_la_tarjeta(dia_preparado):
    """El flujo Estado B: simular on-demand deja la tarjeta en Estado A."""
    cliente = TestClient(server.app)
    tarjetas = cliente.get("/api/muro").json()["tarjetas"]
    pendiente = next(t for t in tarjetas if t["estado"] == "pendiente")

    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "tipo": "simular", "titular": pendiente["titular"],
            "titular_id": pendiente["id"], "seed": 7, "ritmo": 0,
        }))
        while True:
            try:
                mensaje = json.loads(ws.receive_text())
                if mensaje["tipo"] == "fin":
                    break
            except Exception:
                continue  # frames binarios intercalados

    tarjetas = cliente.get("/api/muro").json()["tarjetas"]
    actualizada = next(t for t in tarjetas if t["id"] == pendiente["id"])
    assert actualizada["estado"] == "simulada"
    assert actualizada["sim_id"] == mensaje["sim_id"]
