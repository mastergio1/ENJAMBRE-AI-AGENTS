"""Tests de la diversidad de arquetipos (Fase 3). Sin red."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from calibration import correlacion_cerebros as cc


def test_voces_identicas_dan_una_sola_efectiva():
    # 3 arquetipos con señal IDÉNTICA → ρ=1 → N efectivo = 1
    casos = [({"a": 0.5, "b": 0.5, "c": 0.5}, 1.0),
             ({"a": -0.3, "b": -0.3, "c": -0.3}, -1.0),
             ({"a": 0.8, "b": 0.8, "c": 0.8}, 1.0),
             ({"a": -0.6, "b": -0.6, "c": -0.6}, -1.0)]
    r = cc.matriz_correlacion(casos)
    assert r["n_arquetipos"] == 3 and abs(r["rho_media"] - 1.0) < 1e-6
    assert abs(r["n_efectivo"] - 1.0) < 1e-6


def test_voces_independientes_dan_mas_efectivas():
    import random
    rng = random.Random(0)
    casos = []
    for _ in range(60):
        y = rng.choice([1.0, -1.0])
        casos.append(({"a": rng.uniform(-1, 1), "b": rng.uniform(-1, 1),
                       "c": rng.uniform(-1, 1)}, y))
    r = cc.matriz_correlacion(casos)
    assert r["n_efectivo"] > 2.0  # errores poco correlacionados → más de 2 efectivas
