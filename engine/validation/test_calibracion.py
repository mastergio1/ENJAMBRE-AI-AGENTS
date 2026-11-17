"""Tests del módulo de calibración (Python puro, sin dependencias nuevas).

Comprueban lo esencial:
- El mapeo señal→probabilidad está acotado en [0, 1] y es monótono.
- Platt e isotónica MEJORAN el Brier sobre datos sintéticos descalibrados.
- La isotónica es monótona (a mayor señal, no menor probabilidad).
- El calibrador NUNCA recibe el resultado al predecir (sin fuga).
- Reproducibilidad: mismo input → mismo output.
- Brier y log_loss dan valores correctos conocidos.
"""

import math
import random

from contenido import calibracion as cal


# ---------- mapeo señal → probabilidad ----------

def test_mapeo_senal_media_acotado_y_monotono():
    assert cal.senal_a_prob_cruda({"senal_media_lideres": -1.0}) == 0.0
    assert cal.senal_a_prob_cruda({"senal_media_lideres": 1.0}) == 1.0
    assert cal.senal_a_prob_cruda({"senal_media_lideres": 0.0}) == 0.5
    # fuera de rango se recorta
    assert cal.senal_a_prob_cruda({"senal_media_lideres": 5.0}) == 1.0
    assert cal.senal_a_prob_cruda({"senal_media_lideres": -5.0}) == 0.0
    # monótono
    a = cal.senal_a_prob_cruda({"senal_media_lideres": -0.5})
    b = cal.senal_a_prob_cruda({"senal_media_lideres": 0.3})
    assert a < b


def test_mapeo_direccion_acotado():
    for d in (-50, -2, 0, 2, 50):
        p = cal.senal_a_prob_cruda({"direccion_pct": d}, modo="direccion")
        assert 0.0 <= p <= 1.0
    assert cal.senal_a_prob_cruda({"direccion_pct": 0.0}, modo="direccion") == 0.5


def test_mapeo_desconocido_lanza():
    try:
        cal.senal_a_prob_cruda({}, modo="inexistente")
        assert False, "debió lanzar"
    except ValueError:
        pass


# ---------- métricas ----------

def test_brier_valores_conocidos():
    # predicción perfecta → 0
    assert cal.brier([1.0, 0.0], [1, 0]) == 0.0
    # predicción pésima → 1
    assert cal.brier([0.0, 1.0], [1, 0]) == 1.0
    # 0.5 siempre → 0.25
    assert abs(cal.brier([0.5, 0.5], [1, 0]) - 0.25) < 1e-9


def test_log_loss_no_explota_en_extremos():
    # predecir 0 cuando el resultado es 1: recortado, finito
    v = cal.log_loss([0.0], [1])
    assert math.isfinite(v) and v > 0


def test_tasa_base():
    assert cal.tasa_base([1, 1, 0, 0]) == 0.5
    assert cal.tasa_base([1, 1, 1, 0]) == 0.75


# ---------- datos sintéticos descalibrados ----------

def _datos_descalibrados(n=400, seed=7):
    """Genera (señal, resultado) donde la señal SÍ ordena, pero está mal
    escalada: la probabilidad real es sigmoide de la señal, pero la 'señal cruda'
    que entregamos es demasiado extrema. Un calibrador debería arreglarlo."""
    rng = random.Random(seed)
    scores, ys = [], []
    for _ in range(n):
        s = rng.uniform(-1, 1)
        p_real = cal._sigmoid(1.5 * s)          # probabilidad verdadera
        y = 1 if rng.random() < p_real else 0
        # señal CRUDA mal calibrada: empujada a los extremos
        cruda = cal._clip((s * 3 + 1) / 2, 0, 1)
        scores.append(cruda)
        ys.append(y)
    return scores, ys


def test_ece_cero_si_perfectamente_calibrado():
    """ECE = 0 cuando en cada tramo la predicción iguala la frecuencia observada."""
    # 10 casos con p=0.0 y resultado 0; 10 con p=1.0 y resultado 1 → calibración perfecta
    probs = [0.0] * 10 + [1.0] * 10
    ys = [0] * 10 + [1] * 10
    assert cal.ece(probs, ys) == 0.0
    assert cal.mce(probs, ys) == 0.0


def test_ece_detecta_descalibracion():
    """Si el modelo dice 0.9 pero solo acierta la mitad, ECE y MCE lo delatan."""
    probs = [0.9] * 10
    ys = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # obs_frac = 0.5, pred = 0.9 → error 0.4
    assert abs(cal.ece(probs, ys) - 0.4) < 1e-9
    assert abs(cal.mce(probs, ys) - 0.4) < 1e-9


def test_platt_mejora_brier():
    scores, ys = _datos_descalibrados()
    corte = len(scores) // 2
    s_tr, y_tr = scores[:corte], ys[:corte]
    s_te, y_te = scores[corte:], ys[corte:]
    platt = cal.ajustar_calibrador(s_tr, y_tr, metodo="platt")
    brier_crudo = cal.brier(s_te, y_te)
    brier_cal = cal.brier(platt.predict(s_te), y_te)
    assert brier_cal < brier_crudo, (brier_cal, brier_crudo)


def test_isotonica_mejora_brier():
    scores, ys = _datos_descalibrados()
    corte = len(scores) // 2
    iso = cal.ajustar_calibrador(scores[:corte], ys[:corte], metodo="isotonic")
    s_te, y_te = scores[corte:], ys[corte:]
    assert cal.brier(iso.predict(s_te), y_te) < cal.brier(s_te, y_te)


def test_isotonica_es_monotona():
    scores, ys = _datos_descalibrados()
    iso = cal.ajustar_calibrador(scores, ys, metodo="isotonic")
    xs = [i / 50 for i in range(51)]
    preds = iso.predict(xs)
    for a, b in zip(preds, preds[1:]):
        assert b >= a - 1e-9, "la isotónica no puede bajar al subir la señal"


def test_calibrador_no_ve_resultado_al_predecir():
    # la firma de predict solo recibe scores — comprobamos que no hay forma de
    # colar el resultado y que predecir no depende de él.
    scores, ys = _datos_descalibrados(n=100)
    platt = cal.ajustar_calibrador(scores, ys, metodo="platt")
    p1 = platt.predict([0.3, 0.6, 0.9])
    p2 = platt.predict([0.3, 0.6, 0.9])
    assert p1 == p2  # reproducible y sin estado oculto del resultado


def test_predicciones_en_rango():
    scores, ys = _datos_descalibrados(n=200)
    for metodo in ("platt", "isotonic"):
        c = cal.ajustar_calibrador(scores, ys, metodo=metodo)
        for p in c.predict([-5, 0, 0.5, 1, 5]):
            assert 0.0 <= p <= 1.0


def test_evaluar_calibracion_reporta_lineas_base():
    scores, ys = _datos_descalibrados()
    corte = len(scores) // 2
    platt = cal.ajustar_calibrador(scores[:corte], ys[:corte], metodo="platt")
    rep = cal.evaluar_calibracion(scores[corte:], ys[corte:], calibrador=platt)
    assert "brier_constante_050" in rep
    assert "brier_tasa_base" in rep
    assert "brier_cruda" in rep
    assert "brier_calibrada" in rep
    # la calibrada debería ser mejor (menor) que la cruda en estos datos
    assert rep["brier_calibrada"] <= rep["brier_cruda"]
