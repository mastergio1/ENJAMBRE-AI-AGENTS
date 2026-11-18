"""Tests de la confianza efectiva (Fase 2). Sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import confianza_efectiva as ce


def _c(pc, sen):
    return {"pc": pc, "sen": sen}


def test_pesos_premian_al_que_acierta_y_anulan_al_que_falla():
    # "bueno" siempre acierta; "malo" siempre falla
    train = [_c(2.0, {"bueno": 0.5, "malo": -0.5}),
             _c(-2.0, {"bueno": -0.5, "malo": -0.5})]
    w = ce.pesos_historicos(train, ["bueno", "malo"])
    assert w["bueno"] > 0 and w["malo"] == 0.0  # malo bajo 50% → peso 0


def test_pond_actual_baja_contrarians():
    # un contrarian en contra no debe dominar
    c = _c(2.0, {"macro_trader": 0.6, "quant_esceptico": -0.6})
    assert ce.pond_actual(c) > 0  # el no-contrarian pesa más


def test_acierto_cuenta_direccion():
    casos = [_c(2.0, {"a": 0.5}), _c(-2.0, {"a": 0.5})]  # acierta 1, falla 1
    acc, n = ce.acierto(casos, lambda c: c["sen"]["a"])
    assert n == 2 and acc == 50.0


def test_comparar_devuelve_las_tres_y_cambios_de_signo():
    train = [_c(2.0, {"macro_trader": 0.5, "doomer": -0.5}),
             _c(2.0, {"macro_trader": 0.5, "doomer": -0.5})]
    test = [_c(2.0, {"macro_trader": 0.5, "doomer": -0.5})]
    r = ce.comparar(train, test, ["macro_trader", "doomer"])
    assert r["n_test_dir"] == 1
    assert r["ponderada_actual"][0] is not None and r["efectiva"][0] is not None
    assert r["cambios_de_signo"] >= 0
