"""Tests de la validación walk-forward + promoción (Fase 5), con casos sintéticos."""

import json
import random
from datetime import date, timedelta

from calibration import walk_forward as wf

INICIO = date(2026, 1, 1)


def _fecha(i: int) -> str:
    """Fecha ESTRICTAMENTE creciente con i (auditoría 4.8): el orden de generación
    coincide con el cronológico, así el test no esconde un error de ordenamiento."""
    return (INICIO + timedelta(days=i)).isoformat() + "T00:00:00"


def _archivo(tmp_path, n=400, seed=5, senal_util=True):
    """Casos ordenables por fecha donde la señal ponderada ordena bien (o no)."""
    rng = random.Random(seed)
    casos = []
    for i in range(n):
        sube = rng.random() < 0.5
        pct = rng.uniform(0.1, 3) if sube else -rng.uniform(0.1, 3)
        base = (0.6 if sube else -0.6) if senal_util else 0.0
        sa = {}
        for a in wf.BASE:
            s = base + rng.uniform(-0.2, 0.2) if senal_util else rng.uniform(-1, 1)
            # los contrarians apuntan al revés (ruido direccional)
            if a in wf.CONTRARIANS and senal_util:
                s = -base + rng.uniform(-0.2, 0.2)
            sa[a] = {"senal_media": s, "confianza_media": 0.7, "n": 10}
        # etiqueta CERTIFICADA (pct_corr, sin fuga) — el contrato nuevo de cargar
        # (auditoría científica F01); pct_real queda como la etiqueta de selección
        casos.append({"fecha": _fecha(i),
                      "reaccion_real": {"pct_corr": pct, "pct_real": pct},
                      "senales_arquetipo": sa, "direccion_pct": base * 2})
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"casos": casos}))
    return str(ruta)


def test_walk_forward_devuelve_metricas(tmp_path):
    casos = wf.cargar(_archivo(tmp_path))
    r = wf.walk_forward(casos, "senal_ponderada", min_entrena=150, paso=20)
    for k in ("brier", "brier_base", "skill", "n_oos", "confiabilidad"):
        assert k in r
    assert r["n_oos"] > 0


def test_promueve_con_senal_util(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=True))
    rep = wf.promover(casos, min_entrena=150, paso=20)
    assert rep["promovido"] is True
    assert "calibrador" in rep and rep["calibrador"]["params"]
    # el mejor modo debe ser uno de los de señal (no la dirección constante)
    assert rep["mejor"]["modo"] in ("senal_media", "senal_ponderada")


def test_no_promueve_sin_senal(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=False))
    rep = wf.promover(casos, min_entrena=150, paso=20)
    # con señales puro ruido, no debe superar la base por el margen
    assert rep["promovido"] is False


def test_ponderada_no_es_peor_que_simple(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, senal_util=True))
    pon = wf.walk_forward(casos, "senal_ponderada", min_entrena=150, paso=20)
    sim = wf.walk_forward(casos, "senal_media", min_entrena=150, paso=20)
    assert pon["brier"] <= sim["brier"] + 0.01


def test_senal_incluye_doomer_selectivo(tmp_path):
    """Auditoría ampliada: la señal reconstruida offline debe incluir al
    doomer_selectivo (9º arquetipo), igual que la señal de producción. Antes la
    lista BASE de 8 lo ignoraba → se medía una señal distinta de la real."""
    base_sa = {a: {"senal_media": 0.5, "confianza_media": 0.7, "n": 10} for a in wf.BASE}
    sin_ds = wf._senal(base_sa)
    # el doomer_selectivo tira fuerte a la baja: debe mover la señal
    con_ds = wf._senal({**base_sa,
                        "doomer_selectivo": {"senal_media": -1.0, "confianza_media": 0.9, "n": 10}})
    assert con_ds < sin_ds, "doomer_selectivo debe contribuir a la señal reconstruida"
    assert "doomer_selectivo" in wf.VOCES and "doomer_selectivo" not in wf.BASE


def test_walk_forward_con_embargo_sigue_funcionando(tmp_path):
    """Auditoría 4.7/C: con embargo el walk-forward entrena excluyendo los casos
    justo antes del test (anti-solape) y sigue produciendo métricas válidas."""
    casos = wf.cargar(_archivo(tmp_path, senal_util=True))
    r = wf.walk_forward(casos, "senal_ponderada", min_entrena=150, paso=20, embargo=5)
    assert r["n_oos"] > 0 and 0.0 <= r["ece"] <= 1.0
    # con señal útil, aun con embargo le gana a la base honesta
    assert r["brier"] < r["brier_base"]


def test_anidado_promueve_y_mide_en_holdout_congelado(tmp_path):
    """Problema B (auditoría 4.6): la selección se hace en desarrollo y el veredicto
    se mide en un holdout final que la selección nunca tocó."""
    casos = wf.cargar(_archivo(tmp_path, n=500, senal_util=True))
    rep = wf.promover_anidado(casos, min_entrena=150, paso=20, pct_holdout=20)
    assert rep["promovido"] is True
    assert rep["elegido"]["modo"] in ("senal_media", "senal_ponderada")
    # el veredicto honesto vive en holdout_final, aparte de la métrica de selección
    assert "holdout_final" in rep and rep["holdout_final"]["n"] == 100  # 20% de 500
    assert rep["holdout_final"]["brier"] < rep["holdout_final"]["brier_base"]
    assert "calibrador" in rep


def test_anidado_no_promueve_sin_senal(tmp_path):
    casos = wf.cargar(_archivo(tmp_path, n=500, senal_util=False))
    rep = wf.promover_anidado(casos, min_entrena=150, paso=20, pct_holdout=20)
    assert rep["promovido"] is False


def test_cargar_ordena_cronologicamente_aunque_entren_desordenados(tmp_path):
    """Auditoría 4.8: el contrato es que los casos se procesan en orden temporal.
    Aunque lleguen desordenados, `cargar` los ordena por fecha."""
    casos_raw = []
    for i in (5, 0, 3, 1, 4, 2):  # fechas deliberadamente desordenadas
        sa = {a: {"senal_media": 0.3, "confianza_media": 0.7, "n": 10} for a in wf.BASE}
        casos_raw.append({"fecha": _fecha(i), "reaccion_real": {"pct_corr": 1.0},
                          "senales_arquetipo": sa, "direccion_pct": 0.6})
    ruta = tmp_path / "desord.json"
    ruta.write_text(json.dumps({"casos": casos_raw}))
    cargados = wf.cargar(str(ruta))
    fechas = [c["fecha"] for c in cargados]
    assert fechas == sorted(fechas), "cargar debe entregar los casos en orden temporal"


def test_baseline_honesto_se_reporta_y_no_usa_el_futuro(tmp_path):
    """Auditoría 4.5: el reporte trae la tasa base (solo-train) y la usa para el
    skill. La base media queda en [0,1] y el Brier del baseline es finito."""
    casos = wf.cargar(_archivo(tmp_path, senal_util=True))
    r = wf.walk_forward(casos, "senal_ponderada", min_entrena=150, paso=20)
    assert "base" in r and 0.0 <= r["base"] <= 1.0
    assert r["brier_base"] > 0
    # con señal útil, el modelo le gana a la base honesta
    assert r["brier"] < r["brier_base"]


def test_f01_cargar_rehusa_etiqueta_no_certificada(tmp_path):
    """Auditoría científica F01: solo pct_real (sin pct_corr) NO se usa por defecto;
    con pct_corr sí; el opt-in permite pct_real explícitamente."""
    sa = {a: {"senal_media": 0.3, "confianza_media": 0.7, "n": 10} for a in wf.BASE}
    solo_real = tmp_path / "real.json"
    solo_real.write_text(json.dumps({"casos": [
        {"fecha": "2026-01-01", "reaccion_real": {"pct_real": 2.0},
         "senales_arquetipo": sa, "direccion_pct": 0.6}]}))
    assert wf.cargar(str(solo_real)) == []                       # rehúsa por defecto
    assert len(wf.cargar(str(solo_real), permitir_no_certificada=True)) == 1  # opt-in
    con_corr = tmp_path / "corr.json"
    con_corr.write_text(json.dumps({"casos": [
        {"fecha": "2026-01-01", "reaccion_real": {"pct_corr": -2.0, "pct_real": 2.0},
         "senales_arquetipo": sa, "direccion_pct": 0.6}]}))
    cs = wf.cargar(str(con_corr))
    assert len(cs) == 1 and cs[0]["y"] == 0 and cs[0]["label_certificada"] is True
