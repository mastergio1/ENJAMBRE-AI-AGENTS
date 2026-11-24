"""Tests del predictor calibrado (Fase 5). Sin red."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from calibration import predictor_calibrado as pc


def test_platt_aprende_direccion():
    x = np.array([-2.,-1.,-0.5,0.5,1.,2.]); y = np.array([0,0,0,1,1,1.])
    a, b = pc._platt(x, y)
    p = 1/(1+np.exp(-(a*x+b)))
    assert (p[:3] < 0.5).all() and (p[3:] > 0.5).all()


def test_ece_cero_si_calibrado_perfecto():
    # prob = frecuencia real en cada grupo
    p = np.array([0.1]*10 + [0.9]*10)
    y = np.array([0]*9 + [1] + [1]*9 + [0])  # 10% y 90%
    assert pc._ece(p, y, bins=10) < 0.05


def test_evaluar_insuficiente(tmp_path):
    import json
    f = tmp_path/"cf.json"; f.write_text(json.dumps([
        {"mercado":"indice","pct_corr":2.0,"senal":0.5,"fecha":"2020-01-01"}]))
    assert pc.evaluar(str(f))["suficiente"] is False
