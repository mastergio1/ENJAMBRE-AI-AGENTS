"""Tests de la instrumentación por segmento (Fase 0 del plan combinado)."""

import json

from calibration import evaluar_por_segmento as ev


def _caso(simbolos, direccion_pct, pct_real, senal_arq=0.0, conf=0.7, cerebros="api"):
    sa = {a: {"senal_media": senal_arq, "confianza_media": conf, "n": 10} for a in ev.BASE}
    return {"simbolos": simbolos, "direccion_pct": direccion_pct,
            "senales_arquetipo": sa,
            "reaccion_real": {"pct_real": pct_real, "cerebros": cerebros}}


def test_hit_y_signo():
    assert ev._hit(_caso("SPY", 2.0, 1.0)) is True     # ambos suben
    assert ev._hit(_caso("SPY", -2.0, 1.0)) is False   # predijo baja, subió
    assert ev._signo(0.0) == 0 and ev._signo(-3) == -1 and ev._signo(3) == 1


def test_consenso_desde_arquetipos():
    c = _caso("SPY", 1.0, 1.0, senal_arq=0.5)
    assert abs(ev._consenso(c) - 0.5) < 1e-9
    assert ev._consenso(_caso("SPY", 1.0, 1.0, senal_arq=0.0)) == 0.0


def test_reporte_estructura_y_filtro(tmp_path):
    casos = [
        _caso("SPY", 2.0, 1.5),    # índice, sube, hit
        _caso("QQQ", -1.0, -0.8),  # índice, baja, hit
        _caso("COIN", 1.0, -2.0),  # cripto, miss
        _caso("SPY", 1.0, 0.0),    # pct_real 0 → se descarta
    ]
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"casos": casos}))
    rep = ev.reporte(str(ruta))
    assert rep["n"] == 3                      # el de pct_real 0 se filtró
    assert "indice" in rep["por_mercado"] and "cripto" in rep["por_mercado"]
    assert set(rep["por_arquetipo"]) == set(ev.BASE)
    assert "ia_real" in rep["por_fuente"]
    assert 0 <= rep["hit_global"] <= 100


def test_corr_robusta_a_constantes():
    assert ev._corr([1, 1, 1], [0, 1, 0]) is None   # varianza 0 → None, no crash
    assert ev._corr([1, 2, 3], [1, 2, 3]) == 1.0
