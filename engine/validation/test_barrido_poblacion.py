"""Tests del barrido de población (Fase 2). Sin red."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from calibration import barrido_poblacion as bp


def test_escalar_mantiene_capital_agregado_y_escala_cantidad():
    cfg = {"tipos": [
        {"id": "noise", "cantidad": 1000, "capital_relativo": 1},
        {"id": "market_maker", "cantidad": 9, "capital_relativo": 100},
        {"id": "lider_opinion", "capital_relativo": 5,
         "arquetipos": [{"id": "a", "cantidad": 100}, {"id": "b", "cantidad": 50}]},
    ]}
    e = bp.escalar_config(cfg, 0.1)
    noise = next(t for t in e["tipos"] if t["id"] == "noise")
    assert noise["cantidad"] == 100                  # 1000 × 0.1
    assert noise["capital_relativo"] == 1 / 0.1      # capital agregado constante
    assert noise["cantidad"] * noise["capital_relativo"] == 1000 * 1  # invariante
    mm = next(t for t in e["tipos"] if t["id"] == "market_maker")
    assert mm["cantidad"] >= 1                        # esencial: mínimo 1
    lid = next(t for t in e["tipos"] if t["id"] == "lider_opinion")
    assert [a["cantidad"] for a in lid["arquetipos"]] == [10, 5]
    assert e["total_agentes"] == 100 + 1 + 10 + 5


def test_escalar_factor_1_no_cambia_cantidades():
    cfg = {"tipos": [{"id": "x", "cantidad": 370, "capital_relativo": 50}]}
    e = bp.escalar_config(cfg, 1.0)
    assert e["tipos"][0]["cantidad"] == 370 and e["tipos"][0]["capital_relativo"] == 50
