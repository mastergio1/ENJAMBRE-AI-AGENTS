"""Tests de la tubería calibrar_libreta (con casos sintéticos, sin base real)."""

import random

from contenido import calibrar_libreta as cl


def _casos_sinteticos(n=300, seed=3):
    """Genera casos tipo libreta: la señal del enjambre ordena bien, pero cruda
    está mal calibrada. El resultado real correlaciona con la señal."""
    rng = random.Random(seed)
    casos = []
    for _ in range(n):
        s = rng.uniform(-1, 1)                      # senal_media_lideres
        p_real = cl.cal._sigmoid(1.8 * s)          # prob verdadera de subir
        subio = 1 if rng.random() < p_real else 0
        pct_real = (rng.uniform(0.1, 3.0)) if subio else -(rng.uniform(0.1, 3.0))
        casos.append({"senal_media_lideres": s, "direccion_pct": s * 2,
                      "pct_real": pct_real, "fuente": "backtest"})
    return casos


def test_preparar_filtra_sin_resultado():
    casos = [{"senal_media_lideres": 0.5, "pct_real": 1.0},
             {"senal_media_lideres": 0.2, "pct_real": None},   # sin resultado
             {"senal_media_lideres": 0.1, "pct_real": 0.0}]    # cero exacto
    scores, ys = cl.preparar(casos)
    assert len(scores) == 1 and len(ys) == 1
    assert ys[0] == 1


def test_resultado_binario():
    assert cl._resultado_binario(2.3) == 1
    assert cl._resultado_binario(-0.4) == 0
    assert cl._resultado_binario(0.0) is None
    assert cl._resultado_binario(None) is None


def test_calibrar_devuelve_reporte_completo():
    rep = cl.calibrar(_casos_sinteticos())
    assert "error" not in rep
    for k in ("n_total", "n_entrena", "n_prueba", "platt", "isotonic"):
        assert k in rep
    assert "brier_calibrada" in rep["platt"]


def test_calibrar_pocos_casos_avisa():
    rep = cl.calibrar(_casos_sinteticos(n=5))
    assert "error" in rep


def test_calibracion_supera_base_en_datos_con_senal():
    rep = cl.calibrar(_casos_sinteticos(n=500))
    mejor = min(("platt", "isotonic"),
                key=lambda k: rep[k]["brier_calibrada"])
    # con señal real, el calibrado debe superar la línea base trivial
    assert rep[mejor]["brier_calibrada"] < rep["platt"]["brier_tasa_base"]
