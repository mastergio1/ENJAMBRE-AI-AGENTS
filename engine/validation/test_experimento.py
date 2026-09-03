"""Tests de la Loss oficial y del resumen de experimentos (sin Mesa)."""

from contenido.corrector import evaluar_casos, ratio_fuerza
from contenido.experimento import contraste, resumir_corridas


def test_evaluar_casos_perfecto():
    casos = [(8.0, 8.0), (-5.0, -5.0), (2.0, 2.0)]
    m = evaluar_casos(casos)
    assert m["tasa_acierto"] == 1.0
    assert m["ratio_fuerza_medio"] == 1.0
    assert m["pct_dentro_30"] == 1.0
    assert m["loss"] < 0.05
    assert m["listo_produccion"] is True


def test_evaluar_casos_corto_en_fuerza():
    # acierta dirección pero se queda a mitad de camino (el cuello de botella actual)
    casos = [(4.0, 10.0), (-3.0, -8.0), (2.0, 5.0)]
    m = evaluar_casos(casos)
    assert m["tasa_acierto"] == 1.0
    assert 0.35 < m["ratio_fuerza_medio"] < 0.50
    assert m["listo_produccion"] is False
    assert m["loss"] > 0.20


def test_evaluar_casos_vacio():
    m = evaluar_casos([])
    assert m["casos"] == 0
    assert m["loss"] is None
    assert m["listo_produccion"] is False


def test_ratio_fuerza_capeado():
    assert ratio_fuerza(20.0, 5.0) == 1.5
    assert ratio_fuerza(1.0, 0.0) is None


def test_resumir_corridas_cuenta_direccion():
    corridas = [
        {"shock": -0.9, "pct": -4.0, "direccion_ok": True},
        {"shock": 0.85, "pct": 3.0, "direccion_ok": True},
        {"shock": -0.25, "pct": 0.4, "direccion_ok": False},
        {"shock": 0.20, "pct": 0.3, "direccion_ok": True},
    ]
    r = resumir_corridas(corridas)
    assert r["n"] == 4
    assert r["acierto_direccion"] == 0.75
    assert r["magnitud_media_extremos"] == 3.5


def test_contraste_extremos_crecen_mas():
    def _inf(nombre, corridas):
        return {"conjunto": nombre, "resumen": resumir_corridas(corridas),
                "corridas": corridas, "segundos": 1.0}

    base = _inf("baseline", [
        {"seed": 1, "shock": -0.25, "pct": -0.8, "direccion_ok": True},
        {"seed": 1, "shock": -0.90, "pct": -3.0, "direccion_ok": True},
    ])
    hypo = _inf("hipotesis_v1a", [
        {"seed": 1, "shock": -0.25, "pct": -1.0, "direccion_ok": True},
        {"seed": 1, "shock": -0.90, "pct": -6.0, "direccion_ok": True},
    ])
    c = contraste(base, hypo)
    assert c["ratio_extremos"] == 2.0
    assert c["ratio_normales"] == 1.25
    assert c["direccion_se_mantiene"] is True
    assert c["extremos_crecen_mas"] is True
