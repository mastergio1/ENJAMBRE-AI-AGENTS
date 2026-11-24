"""L4/L5 — Tests de modelos P0–P5: probabilidades, control de información,
serialización y selección de C."""
import random

import numpy as np

from research.last_experiment import models as M
from research.last_experiment.config import ABMCfg, ARQUETIPOS


def _datos(n=200, seed=0):
    rng = random.Random(seed); np.random.seed(seed)
    regs, ys = [], []
    for _ in range(n):
        r5 = rng.gauss(0, 0.02); sc = rng.gauss(0, 1)
        y = 1.0 if (1 / (1 + np.exp(-(8 * r5 + 0.8 * sc)))) > rng.random() else 0.0
        arqs = {a: sc + rng.gauss(0, 0.3) for a in ARQUETIPOS}
        regs.append({
            "features_mercado": {"ret_1": rng.gauss(0, 0.01), "ret_5": r5,
                                 "ret_20": rng.gauss(0, 0.03),
                                 "vol_20": abs(rng.gauss(0.01, 0.003)),
                                 "momentum_5_20": rng.gauss(0, 0.01)},
            "features_macro": {"sorpresa": rng.gauss(0, 1), "sorpresa_falta": 0.0,
                               "sorpresa_std": rng.gauss(0, 1), "sorpresa_std_falta": 0.0},
            "llm": {"score_titular": sc + rng.gauss(0, 0.2), "score_contextual": sc,
                    "archetypes": arqs, "uncertainty": 0.5},
            "abm": {k: rng.gauss(0, 1) for k in ABMCfg().features}})
        ys.append(y)
    return regs, ys


def test_p0_beta_binomial():
    p0 = M.ModeloP0.entrenar([1.0, 1.0, 0.0])  # (2+1)/(3+2)=0.6
    assert abs(p0.p - 0.6) < 1e-9


def test_probabilidades_en_rango():
    regs, ys = _datos()
    for cual, mid in (("P1", "P1"), ("P4", "P4"), ("P5", "P5")):
        m = M.ModeloLogistico.entrenar(mid, regs, ys, cual)
        for r in regs[:20]:
            p = m.proba_una(r)
            assert 0.0 <= p <= 1.0


def test_control_informacion_p5_superconjunto_p4():
    # P5 debe contener EXACTAMENTE las features de P4 + solo las del ABM
    n4 = M.nombres_P4(); n5 = M.nombres_P5()
    assert n5[:len(n4)] == n4
    extra = n5[len(n4):]
    assert extra == [f"abm_{k}" for k in ABMCfg().features]


def test_seleccion_C_dentro_del_grid():
    regs, ys = _datos()
    nombres = M.nombres_P1()
    C = M.seleccionar_C([M.fila_features(r, "P1") for r in regs], nombres, ys)
    assert C in (0.01, 0.1, 1.0)


def test_serializacion_roundtrip():
    regs, ys = _datos()
    m = M.ModeloLogistico.entrenar("P4", regs, ys, "P4")
    d = m.a_dict()
    m2 = M.cargar_modelo(d)
    for r in regs[:10]:
        assert abs(m.proba_una(r) - m2.proba_una(r)) < 1e-12
    # Platt y P0 también
    p2 = M.ModeloPlatt.entrenar("P2", [r["llm"]["score_titular"] for r in regs], ys,
                                "score_titular")
    assert abs(p2.proba_una(regs[0]) - M.cargar_modelo(p2.a_dict()).proba_una(regs[0])) < 1e-12
    p0 = M.ModeloP0.entrenar(ys)
    assert M.cargar_modelo(p0.a_dict()).p == p0.p


def test_model_hash_cambia_con_pesos():
    regs, ys = _datos()
    m1 = M.ModeloLogistico.entrenar("P4", regs, ys, "P4")
    m2 = M.ModeloLogistico.entrenar("P4", regs[:100], ys[:100], "P4")
    assert m1.model_hash() != m2.model_hash()


def test_llm_score_baja_brier_vs_p0():
    regs, ys = _datos()
    p0 = M.ModeloP0.entrenar(ys)
    p2 = M.ModeloPlatt.entrenar("P2", [r["llm"]["score_titular"] for r in regs], ys,
                                "score_titular")
    b0 = M.brier([p0.proba_una(r) for r in regs], ys)
    b2 = M.brier([p2.proba_una(r) for r in regs], ys)
    assert b2 < b0  # el score LLM informa (en estos datos sintéticos)
