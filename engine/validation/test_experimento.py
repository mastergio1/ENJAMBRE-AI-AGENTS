"""Tests de la Loss oficial y del resumen de experimentos (sin Mesa)."""

import pytest

from contenido.corrector import (
    clasificar_error,
    evaluar_casos,
    ratio_fuerza,
    ratio_fuerza_bruto,
    wilson_intervalo,
)
from contenido.experimento import contraste, resumir_corridas


def test_evaluar_casos_perfecto():
    casos = [(8.0, 8.0), (-5.0, -5.0), (2.0, 2.0)]
    m = evaluar_casos(casos)
    assert m["tasa_acierto"] == 1.0
    assert m["ratio_fuerza_medio"] == 1.0
    assert m["pct_dentro_30"] == 1.0
    assert m["loss"] < 0.05
    assert m["pasa_metricas"] is True
    # n=3 no basta para declarar producción: hace falta el hold-out de 80
    assert m["listo_produccion"] is False
    assert m["n_minimo_produccion"] == 80


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
    assert m["pasa_metricas"] is False


def test_ratio_fuerza_simetrico_no_premia_exceso():
    # el doble y la mitad puntúan igual (0.5); 4× ya no es "perfecto"
    assert ratio_fuerza(10.0, 5.0) == pytest.approx(0.5)
    assert ratio_fuerza(5.0, 10.0) == pytest.approx(0.5)
    assert ratio_fuerza(20.0, 5.0) == pytest.approx(0.25)
    assert ratio_fuerza(8.0, 8.0) == pytest.approx(1.0)
    assert ratio_fuerza(1.0, 0.0) is None
    assert ratio_fuerza_bruto(20.0, 5.0) == pytest.approx(4.0)


def test_exceso_sube_la_loss():
    # antes: R capeado a 1.5 → (1-min(1,1.5))=0 → Loss de fuerza nula
    m = evaluar_casos([(20.0, 5.0)])
    assert m["ratio_fuerza_medio"] == pytest.approx(0.25)
    assert m["desglose_errores"]["exagera"] == 1
    assert m["loss"] > 0.20
    assert m["pasa_metricas"] is False


def test_listo_produccion_exige_ochenta():
    pocos = [(8.0, 8.0)] * 12
    muchos = [(8.0, 8.0)] * 80
    assert evaluar_casos(pocos)["pasa_metricas"] is True
    assert evaluar_casos(pocos)["listo_produccion"] is False
    assert evaluar_casos(muchos)["listo_produccion"] is True


def test_wilson_8_de_12_no_es_setenta():
    # el número que parece "casi 70 %" y no lo es
    lo, hi = wilson_intervalo(8, 12)
    assert lo == pytest.approx(0.391, abs=0.02)
    assert hi == pytest.approx(0.862, abs=0.02)
    m = evaluar_casos([(1.0, 1.0)] * 8 + [(-1.0, 1.0)] * 4)
    assert m["tasa_acierto"] == pytest.approx(0.67, abs=0.01)
    assert m["wilson_lo"] < 0.50
    assert m["wilson_hi"] > 0.80


def test_clasificar_error_casillas():
    assert clasificar_error(8.0, 9.0) == "acierto"
    assert clasificar_error(-4.0, 5.0) == "signo"
    assert clasificar_error(20.0, 5.0) == "exagera"
    assert clasificar_error(2.0, 8.0) == "se_queda_corto"
    assert clasificar_error(0.1, 4.0) == "plano"


def test_taxonomia_parte_la_libreta():
    casos = [(8.0, 9.0), (-7.0, 1.4), (-0.1, 16.8)]
    tits = [
        "Sweeping new US tariffs stun markets; stocks sink on trade war fears",
        "Fed raises rates a quarter point, as widely expected",
        "Nvidia earnings smash expectations; shares soar",
    ]
    m = evaluar_casos(casos, titulares=tits)
    tax = m["desglose_taxonomia"]
    assert "geopolitica|sorpresa|acierto" in tax
    assert "macro_tasas|priced_in|signo" in tax
    assert "resultados|sorpresa|plano" in tax


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
