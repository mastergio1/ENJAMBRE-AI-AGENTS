"""Tests del metamodelo M13 vs M13-null (Fase 1/5). Sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import metamodelo as mm


def _fila(senal, direccion, vol, y, fecha):
    return {"senal": senal, "direccion_pct": direccion, "volatilidad_pct": vol,
            "y": float(y), "fecha": fecha, "mercado": "indice"}


def test_logistica_aprende_separacion_simple():
    import numpy as np
    # dos clases separables por una feature
    X = np.array([[-2.0], [-1.5], [-1.0], [1.0], [1.5], [2.0]])
    y = np.array([0, 0, 0, 1, 1, 1], float)
    w, b = mm._entrenar(X, y, l2=0.01, pasos=4000, lr=0.3)
    p = 1 / (1 + np.exp(-(X @ w + b)))
    assert (p[:3] < 0.5).all() and (p[3:] > 0.5).all()


def test_evaluar_muestra_insuficiente():
    filas = [_fila(0.5, 0.5, 1.0, 1, "2020-01-0%d" % i) for i in range(1, 6)]
    r = mm.evaluar(filas)
    assert r["suficiente"] is False


def test_abm_feature_informativa_ayuda():
    # direccion_pct predice perfecto la etiqueta; senal es ruido. M13 (con ABM) debe
    # tener MENOR Brier que M13-null (solo senal) → media_d > 0.
    import random
    rng = random.Random(0)
    filas = []
    for i in range(80):
        y = i % 2
        filas.append(_fila(senal=rng.uniform(-1, 1),          # ruido
                           direccion=(1.0 if y else -1.0),     # informativa
                           vol=rng.uniform(0.5, 2.0), y=y,
                           fecha="2020-%02d-%02d" % (1 + i // 28, 1 + i % 28)))
    r = mm.evaluar(filas, n_boot=400)
    assert r["suficiente"] and r["brier_M13"] < r["brier_M13_null"]
    assert r["media_d"] > 0


def test_abm_feature_ruido_no_ayuda_claramente():
    # direccion y vol son RUIDO puro; no deben mejorar de forma significativa.
    import random
    rng = random.Random(1)
    filas = []
    for i in range(80):
        y = i % 2
        filas.append(_fila(senal=(0.6 if y else -0.6) + rng.uniform(-0.2, 0.2),
                           direccion=rng.uniform(-3, 3), vol=rng.uniform(0.5, 2),
                           y=y, fecha="2020-%02d-%02d" % (1 + i // 28, 1 + i % 28)))
    r = mm.evaluar(filas, n_boot=400)
    # el ABM (ruido) no debe salir significativamente a favor
    assert not (r["significativo"] and r["abm_ayuda"])
