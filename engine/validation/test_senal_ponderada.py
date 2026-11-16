"""Tests de la señal de predicción ponderada (baja el peso de los contrarians).

Garantizan que:
- el nuevo campo baja el peso SOLO de las voces contrarian (quant/contrarian),
  no del optimista ni del resto;
- el env ENJAMBRE_PESO_CONTRARIANS lo controla (1.0 = vuelve al promedio simple);
- el mapeo de calibración "senal_ponderada" usa el campo nuevo y cae al viejo.
"""
from contenido import calibracion as cal
from contenido import senal_prediccion as sp


class _Lider:
    def __init__(self, arquetipo):
        self.arquetipo = arquetipo


def _caso():
    lideres = [_Lider("doomer"), _Lider("quant_esceptico"),
               _Lider("contrarian_sabio"), _Lider("influencer_optimista")]
    # el doomer y el optimista dicen +1; los dos contrarians dicen -1
    respuestas = [{"senal": 1.0}, {"senal": -1.0}, {"senal": -1.0}, {"senal": 1.0}]
    return lideres, respuestas


def test_ponderada_baja_contrarians(monkeypatch):
    monkeypatch.delenv("ENJAMBRE_PESO_CONTRARIANS", raising=False)
    lideres, respuestas = _caso()
    simple = round(sum(r["senal"] for r in respuestas) / len(respuestas), 2)  # 0.0
    ponderada = sp.senal_media_ponderada(lideres, respuestas)
    assert simple == 0.0
    # con los contrarians a 0.3, los que dicen +1 pesan más → señal positiva
    assert ponderada > simple
    # cálculo exacto: (1 + 1 - 0.3 - 0.3) / (1 + 1 + 0.3 + 0.3)
    esperado = round((1 + 1 - 0.3 - 0.3) / (1 + 1 + 0.3 + 0.3), 2)
    assert ponderada == esperado


def test_env_1_0_vuelve_al_promedio_simple(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PESO_CONTRARIANS", "1.0")
    lideres, respuestas = _caso()
    simple = round(sum(r["senal"] for r in respuestas) / len(respuestas), 2)
    assert sp.senal_media_ponderada(lideres, respuestas) == simple


def test_env_invalido_cae_al_defecto(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PESO_CONTRARIANS", "abc")
    assert sp.peso_contrarians() == 0.3


def test_mapeo_usa_campo_nuevo_y_cae_al_viejo():
    # con el campo nuevo
    p = cal.senal_a_prob_cruda({"senal_media_ponderada": 1.0}, modo="senal_ponderada")
    assert p == 1.0
    # sin el campo nuevo, cae al viejo
    p2 = cal.senal_a_prob_cruda({"senal_media_lideres": -1.0}, modo="senal_ponderada")
    assert p2 == 0.0
