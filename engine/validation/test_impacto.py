"""Tests de la función de impacto no lineal (Fase 1 de calibración).

No levantan el mercado: son la garantía de que 'baseline' es identidad
y de que 'hipotesis_v1a' / 'v1b' sí amplifican los shocks grandes.
"""

import pytest

from brains import impacto


@pytest.fixture(autouse=True)
def baseline(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "baseline")
    impacto.reiniciar_cache()
    yield
    monkeypatch.delenv("ENJAMBRE_PERILLAS", raising=False)
    impacto.reiniciar_cache()


def test_baseline_es_identidad():
    for s in (-0.9, -0.4, -0.05, 0.0, 0.2, 0.6, 0.95):
        assert impacto.calcular_impacto(s) == pytest.approx(s)
        assert impacto.transformar_senal(s) == pytest.approx(s)
        assert impacto.factor_residual(s) == pytest.approx(1.0)
        assert impacto.factor_shock(s) == pytest.approx(1.0)
    assert impacto.ganancia_contagio() == pytest.approx(0.7)
    assert impacto.ganancia_consenso() == pytest.approx(0.8)
    assert impacto.ruido_lider_sigma() == 0.0


def test_v1a_solo_dos_perillas(monkeypatch):
    """v1a = 2.0× + umbral 0.45. Sin asimetría, sin ruido, sin más cerebros."""
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1a")
    impacto.reiniciar_cache()
    cfg = impacto.cargar_perillas()
    assert cfg["nombre"] == "hipotesis_v1a"
    g = cfg["globales"]
    assert g["impacto_base"] == 2.0
    assert g["umbral_panico"] == 0.45
    assert g["asimetria_downside"] == 1.0
    assert g["ruido_lider_sigma"] == 0.0
    assert g["peso_cerebro_fomo_evangelista"] == 1.0
    chico = impacto.calcular_impacto(0.20)
    grande = impacto.calcular_impacto(0.80)
    caida = impacto.calcular_impacto(-0.80)
    assert chico == pytest.approx(0.40, abs=0.02)
    assert abs(grande) > abs(chico) * 2
    assert abs(caida) == pytest.approx(abs(grande))
    assert impacto.ruido_lider_sigma() == 0.0


def test_hipotesis_amplifica_shocks_grandes(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1b")
    impacto.reiniciar_cache()
    chico = impacto.calcular_impacto(0.20)
    grande = impacto.calcular_impacto(0.80)
    caida = impacto.calcular_impacto(-0.80)
    # lineal ×2 más extra de pánico cuando |s| ≥ 0.45
    assert chico == pytest.approx(0.40, abs=0.02)          # bajo el umbral: solo k×
    assert abs(grande) > abs(chico) * 2                    # el pánico empuja más que lineal
    assert abs(caida) > abs(grande)                        # asimetría a la baja
    assert impacto.factor_residual(-0.90) > 1.0            # el recorte deja residual
    assert impacto.transformar_senal(-0.90) == pytest.approx(-1.0)


def test_cripto_mas_nervioso_que_indice(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1b")
    impacto.reiniciar_cache()
    s = 0.70
    i = abs(impacto.calcular_impacto(s, {"tipo": "indice"}))
    c = abs(impacto.calcular_impacto(s, {"tipo": "cripto"}))
    assert c > i


def test_conjunto_por_env(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1b")
    impacto.reiniciar_cache()
    assert impacto.cargar_perillas()["nombre"] == "hipotesis_v1b"
    assert impacto.cargar_perillas()["globales"]["impacto_base"] == 2.0


def test_fallback_entiende_aranceles_y_wipeout():
    from brains.fallback import sentimiento_lexico
    assert sentimiento_lexico("US slashes tariffs on Chinese goods") > 0
    assert sentimiento_lexico("Crash wipes out $2 trillion in value") < -0.5


def test_overlay_perfil_no_pisa_volatilidad_en_baseline():
    from brains.mercado import perfil_de
    assert perfil_de("cripto")["volatilidad"] == 3.6
    assert perfil_de("indice")["volatilidad"] == 1.0


def test_overlay_perfil_aplica_volatilidad_base():
    overlay = impacto.overlay_perfil({"tipo": "indice", "volatilidad": 1.0, "volatilidad_base": 1.4})
    assert overlay["volatilidad"] == 1.4
