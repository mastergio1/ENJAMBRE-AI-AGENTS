"""Tests del servidor WebSocket (Etapa 4): el flujo end-to-end.

Corren sin API key (fallback) y con ritmo 0 (sin pausas entre ticks).
"""

import json
import struct

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    from contenido import limites, seguridad

    limites.reiniciar()
    seguridad.reiniciar()


def test_salud():
    cliente = TestClient(server.app)
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_flujo_completo_por_websocket():
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "tipo": "simular",
            "titular": "Quiebra el segundo banco más grande del país; pánico en los mercados",
            "seed": 42,
            "ritmo": 0,
        }))

        # 1) inicio: los 100 líderes con señal, confianza y frase
        inicio = json.loads(ws.receive_text())
        assert inicio["tipo"] == "inicio"
        assert len(inicio["lideres"]) == 100
        for lider in inicio["lideres"]:
            assert -1.0 <= lider["senal"] <= 1.0
            assert lider["frase"]

        # 2) un frame binario por tick: cabecera (precio, tick) + 5000 bytes
        total_ticks = server.TICKS_PREVIOS + server.TICKS_POSTERIORES
        precios = []
        for _ in range(total_ticks):
            frame = ws.receive_bytes()
            precio, tick = struct.unpack("<fI", frame[:8])
            assert len(frame) == 8 + 5000
            precios.append(precio)

        # el titular negativo golpea el precio durante la reacción
        assert min(precios) < precios[server.TICKS_PREVIOS - 1] * 0.97

        # los sentimientos del último frame son bytes con signo válidos
        sentimientos = [b - 256 if b > 127 else b for b in frame[8:]]
        assert all(-127 <= s <= 127 for s in sentimientos)

        # 3) fin: el reporte
        fin = json.loads(ws.receive_text())
        assert fin["tipo"] == "fin"
        reporte = fin["reporte"]
        assert reporte["direccion_pct"] < 2  # una quiebra no dispara el precio
        assert reporte["volatilidad_pct"] > 0
        assert len(reporte["frases"]) == 3
        assert reporte["desglose"]  # hay actividad por tipo

        from contenido.vocabulario import DISCLAIMER
        assert reporte["descargo"] == DISCLAIMER

        # 4) persistencia primero: la simulación quedó guardada
        from contenido import persistencia
        conexion = persistencia.conectar()
        guardada = persistencia.obtener_simulacion(conexion, fin["sim_id"])
        conexion.close()
        assert guardada is not None
        assert guardada["titular"].startswith("Quiebra el segundo banco")
        assert len(guardada["lideres"]) == 100
        assert len(guardada["serie_precios"]) >= total_ticks
