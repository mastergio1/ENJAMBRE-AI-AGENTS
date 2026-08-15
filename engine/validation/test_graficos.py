"""Tests del generador de gráficos reales de El Pulso (rediseño)."""

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

import server
from contenido import graficos
from contenido.fuentes import yahoo


def test_grafico_png_valido():
    serie = [100.0, 101.5, 99.8, 103.2, 105.0, 104.6, 107.1]
    png = graficos.generar_grafico("Prueba", "PRB", serie, fecha_inicio="7 ago")
    assert png[:8] == b"\x89PNG\r\n\x1a\n"     # firma PNG
    assert len(png) > 3000


def test_grafico_serie_corta_es_none():
    assert graficos.generar_grafico("X", "X", [1.0]) is None
    assert graficos.generar_grafico("X", "X", []) is None
    # descarta huecos (None) de Yahoo y si no quedan 2 puntos, None
    assert graficos.generar_grafico("X", "X", [None, 5.0, None]) is None


def test_ticker_valido():
    for ok in ("AAPL", "^GSPC", "CL=F", "BTC-USD", "BRK-B"):
        assert server._ticker_valido(ok)
    for malo in ("", "a b", "../etc", "a/b", "x" * 16, "AA;PL"):
        assert not server._ticker_valido(malo)


def _serie_falsa(*a, **k):
    base = datetime(2026, 8, 7)
    fechas = [base + timedelta(days=i) for i in range(6)]
    return fechas, [10.0, 10.2, 10.1, 10.5, 10.9, 11.2]


def test_endpoint_grafico_devuelve_png(monkeypatch):
    monkeypatch.setattr(yahoo, "serie_reciente", _serie_falsa)
    cliente = TestClient(server.app)
    r = cliente.get("/api/grafico/AAPL?n=Apple%20Inc.&p=semana")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert "max-age" in r.headers.get("Cache-Control", "")


def test_endpoint_grafico_rechaza_ticker_malicioso():
    cliente = TestClient(server.app)
    assert cliente.get("/api/grafico/..%2f..%2fsecreto").status_code == 404


def test_endpoint_grafico_sin_datos_es_404(monkeypatch):
    monkeypatch.setattr(yahoo, "serie_reciente", lambda *a, **k: None)
    cliente = TestClient(server.app)
    assert cliente.get("/api/grafico/ZZZZ").status_code == 404
