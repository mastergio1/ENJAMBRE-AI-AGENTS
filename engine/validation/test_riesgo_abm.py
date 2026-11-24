"""Tests de la predicción de riesgo del ABM (Fase 4). Sin red."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from calibration import riesgo_abm as ra


def test_spearman_monotono():
    assert ra.spearman([1, 2, 3, 4], [10, 20, 30, 40]) > 0.99
    assert ra.spearman([1, 2, 3, 4], [40, 30, 20, 10]) < -0.99


def test_feature_informativa_baja_el_mae(tmp_path):
    # construye filas donde vol_abm predice casi perfecto la magnitud real
    import json, numpy as np, random
    rng = random.Random(0)
    cf, raw = [], []
    for i in range(60):
        mag = rng.uniform(0.5, 5.0)
        fecha = "2020-%02d-%02d" % (1 + i // 28, 1 + i % 28)
        cf.append({"fecha": fecha, "simbolo": "SPY", "mercado": "indice",
                   "pct_corr": mag, "senal": rng.uniform(-1, 1), "direccion_pct": 0.0})
        raw.append({"reaccion_real": {"fecha_base": fecha, "simbolo": "SPY"},
                    "volatilidad_pct": mag + rng.uniform(-0.2, 0.2),  # informativa
                    "direccion_pct": 0.0, "senales_arquetipo": {"a": {"senal_media": 0.1}}})
    pcf = tmp_path / "cf.json"; pcf.write_text(json.dumps(cf))
    praw = tmp_path / "raw.json"; praw.write_text(json.dumps({"casos": raw}))
    r = ra.evaluar(str(pcf), str(praw))
    assert r["spearman"]["vol_abm"] > 0.8          # la vol simulada rankea la magnitud
    assert r["mae_oos"]["+ features ABM"] < r["mae_oos"]["constante (media)"]
