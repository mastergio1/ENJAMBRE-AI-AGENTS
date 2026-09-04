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
        assert impacto.zona_muerta(s) == pytest.approx(s)
    assert impacto.ganancia_contagio() == pytest.approx(0.7)
    assert impacto.ganancia_consenso() == pytest.approx(0.8)
    assert impacto.ruido_lider_sigma() == 0.0
    assert impacto.cargar_perillas()["globales"]["umbral_consenso"] == 0.0


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


def test_clasificar_titular_casillas_conocidas():
    from brains.fallback import clasificar_titular
    fed = clasificar_titular("Fed raises rates a quarter point, as widely expected")
    assert fed["tipo"] == "macro_tasas"
    assert fed["regimen"] == "priced_in"
    nvda = clasificar_titular("Nvidia earnings smash expectations; shares soar")
    assert nvda["tipo"] == "resultados"
    assert nvda["regimen"] == "sorpresa"
    tar = clasificar_titular("Sweeping new US tariffs stun markets; stocks sink on trade war fears")
    assert tar["tipo"] == "geopolitica"
    assert tar["regimen"] == "sorpresa"
    guia = clasificar_titular("Target Raises FY2026 GAAP EPS Guidance from $8.50 to $9.90")
    assert guia["tipo"] == "resultados"
    linea = clasificar_titular("Consumer prices come in line with expectations; Fed keeps rates unchanged")
    assert linea["regimen"] == "priced_in"
    assert linea["tipo"] == "macro_tasas"



def test_v1c_zona_muerta_anti_v1a(monkeypatch):
    """v1c = 1 perilla. Silencia lo tibio, no multiplica todo (eso era v1a)."""
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1c")
    impacto.reiniciar_cache()
    cfg = impacto.cargar_perillas()
    assert cfg["nombre"] == "hipotesis_v1c"
    g = cfg["globales"]
    assert g["umbral_consenso"] == 0.25
    assert g["impacto_base"] == 1.0  # no se toca el parlante
    assert not g.get("prompt_microfono")
    assert impacto.calcular_impacto(0.20) == pytest.approx(0.20)
    assert impacto.zona_muerta(0.15) == 0.0
    assert impacto.zona_muerta(0.20) == 0.0
    assert impacto.zona_muerta(-0.20) == 0.0
    # soft-threshold: 0.80 - 0.25 = 0.55; el extremo sobrevive, achicado
    assert impacto.zona_muerta(0.80) == pytest.approx(0.55)
    assert impacto.zona_muerta(-0.90) == pytest.approx(-0.65)


def test_v1d_enciende_el_microfono(monkeypatch):
    """v1d = 1 perilla de prompt. No toca impacto_base ni umbral."""
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1d")
    impacto.reiniciar_cache()
    assert impacto.prompt_microfono() is True
    g = impacto.cargar_perillas()["globales"]
    assert g["impacto_base"] == 1.0
    assert g["umbral_consenso"] == 0.0
    from brains.cerebro import _system_lider, _version_cache
    sysmsg = _system_lider("doomer")
    assert "YA ESTABA EN EL PRECIO" in sysmsg
    assert _version_cache() == "microfono_v1"


def test_baseline_no_lleva_microfono():
    assert impacto.prompt_microfono() is False
    from brains.cerebro import _system_lider, _version_cache
    assert "YA ESTABA EN EL PRECIO" not in _system_lider("doomer")
    assert _version_cache() == "v0"


def test_v1f_escala_senal_por_sorpresa(monkeypatch):
    """v1f = 1 perilla. No toca impacto_base. senal × sorpresa."""
    assert impacto.escalar_sorpresa() is False
    assert impacto.aplicar_sorpresa(0.80, 0.10) == pytest.approx(0.80)
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1f")
    impacto.reiniciar_cache()
    assert impacto.escalar_sorpresa() is True
    assert impacto.prompt_microfono() is False
    g = impacto.cargar_perillas()["globales"]
    assert g["impacto_base"] == 1.0
    assert g["umbral_consenso"] == 0.0
    assert impacto.aplicar_sorpresa(0.80, 0.10) == pytest.approx(0.08)
    assert impacto.aplicar_sorpresa(-0.90, 1.0) == pytest.approx(-0.90)
    assert impacto.aplicar_sorpresa(0.50, None) == pytest.approx(0.50)
    from brains.cerebro import _system_lider, _validar_respuesta, _version_cache
    sysmsg = _system_lider("fomo_evangelista")
    assert '"sorpresa"' in sysmsg
    assert "YA ESTABA EN EL PRECIO" not in sysmsg
    assert _version_cache() == "sorpresa_v1"
    parsed = _validar_respuesta(
        '{"senal": 0.9, "confianza": 1, "sorpresa": 0.1, "frase": "ok"}'
    )
    assert parsed["sorpresa"] == pytest.approx(0.1)
    assert parsed["senal"] == pytest.approx(0.09)


def test_fallback_v1f_calla_priced_in(monkeypatch):
    from brains.fallback import respuesta_fallback
    tit = "Fed holds rates and flags a March increase, as widely expected"
    base = respuesta_fallback(tit, "fomo_evangelista", 1)
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1f")
    impacto.reiniciar_cache()
    hypo = respuesta_fallback(tit, "fomo_evangelista", 1)
    assert hypo["sorpresa"] == pytest.approx(0.1)
    assert abs(hypo["senal"]) <= abs(base["senal"]) * 0.15 + 1e-9
    crash = respuesta_fallback(
        "Lehman Brothers files for bankruptcy; global financial system reels",
        "doomer", 1)
    assert crash["sorpresa"] == pytest.approx(1.0)



def test_fallback_priced_in_se_suaviza_solo_en_v1d(monkeypatch):
    from brains.fallback import respuesta_fallback
    tit = "Fed holds rates and flags a March increase, as widely expected"
    base = respuesta_fallback(tit, "fomo_evangelista", 1)
    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1d")
    impacto.reiniciar_cache()
    hypo = respuesta_fallback(tit, "fomo_evangelista", 1)
    assert abs(hypo["senal"]) <= 0.15
    assert abs(hypo["senal"]) <= abs(base["senal"]) + 1e-9


def test_overlay_perfil_no_pisa_volatilidad_en_baseline():
    from brains.mercado import perfil_de
    assert perfil_de("cripto")["volatilidad"] == 3.6
    assert perfil_de("indice")["volatilidad"] == 1.0


def test_overlay_perfil_aplica_volatilidad_base():
    overlay = impacto.overlay_perfil({"tipo": "indice", "volatilidad": 1.0, "volatilidad_base": 1.4})
    assert overlay["volatilidad"] == 1.4
