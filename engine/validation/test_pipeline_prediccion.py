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
