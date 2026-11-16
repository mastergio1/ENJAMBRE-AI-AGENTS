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


def test_instrumentacion_registra_volumen_por_tipo():
    m = MercadoEnjambre(seed=42, ticks_horizonte=200)
    m.activar_instrumentacion()
    for _ in range(40):
        m.step()
    m.aplicar_noticia(-0.8)
    for _ in range(40):
        m.step()
    r = m.resumen_instrumentacion()
    assert r["agresor"] and r["proveedor"], "debe registrar volumen"
    # los porcentajes suman ~100
    assert abs(sum(r["agresor_pct"].values()) - 100) < 1.0
    assert abs(sum(r["proveedor_pct"].values()) - 100) < 1.0


def test_instrumentacion_es_opt_in():
    # sin activar, no hay callback ni contadores (producción intacta)
    m = MercadoEnjambre(seed=1, ticks_horizonte=50)
    assert m.libro.registrar_ejecucion_instr is None


def test_escenarios_de_estres_corren_y_devuelven_metricas():
    from calibration.escenarios import correr_escenario, variabilidad
    r = correr_escenario("negativa_fuerte", seed=42, post=60)
    for k in ("direccion_pct", "minimo_pct", "maximo_pct", "volatilidad_pct"):
        assert k in r
    # una noticia fuertemente negativa debe empujar la dirección hacia abajo
    assert r["direccion_pct"] < 0
    # la variabilidad entre semillas se reporta
    v = variabilidad("negativa_fuerte", seeds=(1, 42))
    assert "desv" in v and len(v["direcciones"]) == 2


def test_escenario_desconocido_lanza():
    from calibration.escenarios import correr_escenario
    try:
        correr_escenario("no_existe")
        assert False, "debió lanzar ValueError"
    except ValueError:
        pass


def test_senales_por_arquetipo_resume_bien():
    import json
    from contenido.respaldo import _senales_por_arquetipo
    lideres = json.dumps([
        {"arquetipo": "doomer", "senal": -0.8, "confianza": 0.9},
        {"arquetipo": "doomer", "senal": -0.6, "confianza": 0.7},
        {"arquetipo": "fomo_evangelista", "senal": 0.9, "confianza": 0.95},
    ])
    r = _senales_por_arquetipo(lideres)
    assert r["doomer"]["senal_media"] == -0.7
    assert r["doomer"]["n"] == 2
    assert r["fomo_evangelista"]["senal_media"] == 0.9
    # entrada vacía o inválida no rompe
    assert _senales_por_arquetipo(None) == {}
    assert _senales_por_arquetipo("no-json") == {}
