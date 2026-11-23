"""Test del enganche prospectivo en el ritual (Fase 7-mínima). Sin red ni IA."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido import persistencia as p
from contenido import pipeline


@pytest.fixture
def con(tmp_path):
    return p.conectar(tmp_path / "test.db")


@pytest.fixture(autouse=True)
def _sin_red(monkeypatch):
    """Evita que el enganche llame a Yahoo en los tests: stub de la evidencia."""
    from evidence import recoleccion
    monkeypatch.setattr(recoleccion, "evidencia_para",
                        lambda simbolo, titular, as_of, **k: {
                            "evidence_hash": f"hash-{simbolo}", "headline": titular,
                            "facts": [], "sources": [], "evidence_version": "v1"})


def _reporte(direccion="baja", fiable=True, nivel="fuerte", senal=-0.5):
    return {
        "direccion_titular": direccion,
        "senal_media_ponderada": senal,
        "conviccion": {"nivel": nivel, "fiable_direccion": fiable, "nota": ""},
    }


def _lideres():
    return [{"arquetipo": "macro_trader", "fuente": "api"},
            {"arquetipo": "doomer", "fuente": "cache"},
            {"arquetipo": "fomo_evangelista", "fuente": "fallback"}]


def test_registra_prediccion_de_destacada(con):
    elegido = {"titular": "La Fed sube tasas por sorpresa", "simbolos": "SPY", "fuente": "alpaca"}
    pipeline._registrar_prediccion_prospectiva(con, elegido, _reporte(), _lideres(), "sim123", 42)
    preds = p.listar_predicciones(con)
    assert len(preds) == 1
    pr = preds[0]
    assert pr["simbolo"] == "SPY" and pr["mercado"] == "indice"
    assert pr["direccion"] == "baja" and pr["fiable"] == 1 and pr["conviccion"] == "fuerte"
    assert pr["sim_id"] == "sim123"
    import json
    assert json.loads(pr["fuentes_json"]) == {"api": 1, "cache": 1, "fallback": 1}


def test_registra_todos_los_tickers(con):
    # P0-03: una noticia con varios tickers registra UNA predicción por cada uno
    elegido = {"titular": "CPI sorprende al alza", "simbolos": "SPY,QQQ,DIA", "fuente": "alpaca"}
    pipeline._registrar_prediccion_prospectiva(con, elegido, _reporte(), _lideres(), "s", 1)
    preds = p.listar_predicciones(con)
    assert len(preds) == 3
    assert {x["simbolo"] for x in preds} == {"SPY", "QQQ", "DIA"}


def test_guarda_evidencia_en_modo_sombra(con):
    # Fase 1: cada predicción guarda su evidencia point-in-time (sin cambiar la predicción)
    elegido = {"titular": "Dato de empleo", "simbolos": "SPY", "fuente": "alpaca"}
    pipeline._registrar_prediccion_prospectiva(con, elegido, _reporte(), _lideres(), "s", 1)
    fila = p.listar_predicciones(con)[0]
    assert fila["evidencia_hash"] == "hash-SPY"
    # la predicción sigue siendo la del enjambre (la evidencia NO la cambió)
    assert fila["direccion"] == "baja"


def test_sin_simbolo_no_registra(con):
    elegido = {"titular": "Noticia sin ticker", "simbolos": "", "fuente": "alpaca"}
    pipeline._registrar_prediccion_prospectiva(con, elegido, _reporte(), _lideres(), "s", 1)
    assert p.listar_predicciones(con) == []


def test_neutra_marca_abstencion(con):
    elegido = {"titular": "Noticia ambigua", "simbolos": "QQQ", "fuente": "alpaca"}
    pipeline._registrar_prediccion_prospectiva(
        con, elegido, _reporte(direccion="neutra", fiable=False, nivel="debil", senal=0.0),
        _lideres(), "s", 1)
    pr = p.listar_predicciones(con)[0]
    assert pr["abstenido"] == 1


def test_blindado_ante_reporte_malo(con):
    # un reporte corrupto NO debe lanzar excepción (el ritual no se cae)
    elegido = {"titular": "x", "simbolos": "SPY"}
    pipeline._registrar_prediccion_prospectiva(con, elegido, None, None, "s", 1)
    # no se registró, pero tampoco explotó
    assert p.listar_predicciones(con) == []
