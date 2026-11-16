"""Tests de la validación walk-forward + promoción (Fase 5), con casos sintéticos."""

import json
import random

from calibration import walk_forward as wf


def _archivo(tmp_path, n=400, seed=5, senal_util=True):
    """Casos ordenables por fecha donde la señal ponderada ordena bien (o no)."""
    rng = random.Random(seed)
    casos = []
    for i in range(n):
        sube = rng.random() < 0.5
        pct = rng.uniform(0.1, 3) if sube else -rng.uniform(0.1, 3)
        base = (0.6 if sube else -0.6) if senal_util else 0.0
        sa = {}
        for a in wf.BASE:
            s = base + rng.uniform(-0.2, 0.2) if senal_util else rng.uniform(-1, 1)
            # los contrarians apuntan al revés (ruido direccional)
            if a in wf.CONTRARIANS and senal_util:
                s = -base + rng.uniform(-0.2, 0.2)
            sa[a] = {"senal_media": s, "confianza_media": 0.7, "n": 10}
        casos.append({"fecha": f"2026-08-{i % 28 + 1:02d}T{i%24:02d}:00:00",
                      "reaccion_real": {"pct_real": pct}, "senales_arquetipo": sa,
                      "direccion_pct": base * 2})
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"casos": casos}))
    return str(ruta)


def test_walk_forward_devuelve_metricas(tmp_path):
    casos = wf.cargar(_archivo(tmp_path))
    r = wf.walk_forward(casos, "senal_ponderada", min_entrena=150, paso=20)
    for k in ("brier", "brier_base", "skill", "n_oos", "confiabilidad"):
        assert k in r
    assert r["n_oos"] > 0


def test_promueve_con_senal_util(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=True))
    rep = wf.promover(casos, min_entrena=150, paso=20)
    assert rep["promovido"] is True
    assert "calibrador" in rep and rep["calibrador"]["params"]
    # el mejor modo debe ser uno de los de señal (no la dirección constante)
    assert rep["mejor"]["modo"] in ("senal_media", "senal_ponderada")


def test_no_promueve_sin_senal(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=False))
    rep = wf.promover(casos, min_entrena=150, paso=20)
    # con señales puro ruido, no debe superar la base por el margen
    assert rep["promovido"] is False


def test_ponderada_no_es_peor_que_simple(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=True))
    pon = wf.walk_forward(casos, "senal_ponderada", min_entrena=150, paso=20)
    sim = wf.walk_forward(casos, "senal_media", min_entrena=150, paso=20)
    assert pon["brier"] <= sim["brier"] + 0.01
