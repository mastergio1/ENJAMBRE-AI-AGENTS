"""Tests del laboratorio de experimentos (Fase 1): overrides de parámetros."""

from agents.reglas import Manada
from model import MercadoEnjambre


def test_override_por_tipo_se_aplica():
    m = MercadoEnjambre(seed=1, overrides={"manada": {"factor_freno_cautela": 0.3}})
    vals = {round(a.factor_freno_cautela, 3) for a in m.agents if isinstance(a, Manada)}
    assert vals == {0.3}


def test_override_global_se_aplica():
    m = MercadoEnjambre(seed=1, overrides={"global": {"umbral_correccion_sesgo": 0.5}})
    assert m._umbral_correccion == 0.5


def test_sin_override_no_cambia_nada():
    m = MercadoEnjambre(seed=1)
    # factor_freno_cautela del config es 0.5
    vals = {round(a.factor_freno_cautela, 3) for a in m.agents if isinstance(a, Manada)}
    assert vals == {0.5}


def test_override_desconocido_por_tipo_lanza():
    try:
        MercadoEnjambre(seed=1, overrides={"manada": {"inexistente": 1}})
        assert False, "debió lanzar ValueError"
    except ValueError:
        pass


def test_override_global_desconocido_lanza():
    try:
        MercadoEnjambre(seed=1, overrides={"global": {"inexistente": 1}})
        assert False, "debió lanzar ValueError"
    except ValueError:
        pass
