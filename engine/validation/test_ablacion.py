"""Tests de la ablación A0–A5 (Fase 3). Sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import ablacion as ab


def _f(pct, senal, direccion, simbolo="SPY", fecha="2020-01-01", lexico=None):
    d = {"pct_corr": pct, "senal": senal, "direccion_pct": direccion,
         "simbolo": simbolo, "fecha": fecha, "anio": int(fecha[:4]), "mercado": "indice"}
    if lexico is not None:
        d["lexico"] = lexico
    return d


def test_signo_mayoria_sigue_a_las_subas():
    filas = [_f(2.0, 0, 0), _f(3.0, 0, 0), _f(-1.0, 0, 0)]  # 2 subas, 1 baja
    assert ab._signo_mayoria(filas) == 1


def test_items_descarta_zona_muerta_y_abstenciones():
    filas = [_f(0.1, 0.5, 0.5),      # |pct|<0.3 → fuera
             _f(2.0, 0.0, 0.5),       # A3 se abstiene (senal=0)
             _f(2.0, 0.5, 0.5)]       # cuenta
    assert len(ab._items(filas, "A3_consenso", 1)) == 1
    assert len(ab._items(filas, "A4_abm", 1)) == 2  # A4 opina en los dos >zona


def test_gate_detecta_que_el_abm_empeora():
    # consenso (A3) acierta siempre; el ABM (A4) invierte el signo y falla
    filas = [_f(2.0, 0.6, -0.6), _f(3.0, 0.7, -0.7), _f(2.5, 0.5, -0.5)]
    g = ab.gate_abm(filas)
    assert g["A3"] == 100.0 and g["A4"] == 0.0
    assert g["delta_A4_menos_A3"] == -100.0
    assert g["abm_cambia_signo"] == 3 and g["abm_acierta_al_cambiar"] == 0


def test_gate_cuenta_aciertos_del_abm_al_cambiar():
    # A3 falla (dice baja), el ABM corrige a subida y acierta
    filas = [_f(2.0, -0.4, 0.6), _f(3.0, -0.3, 0.7)]
    g = ab.gate_abm(filas)
    assert g["A3"] == 0.0 and g["A4"] == 100.0
    assert g["abm_cambia_signo"] == 2 and g["abm_acierta_al_cambiar"] == 2


def test_evaluar_trae_todos_los_escalones():
    filas = [_f(2.0, 0.5, 0.5, lexico=0.3), _f(-2.0, -0.5, -0.5, lexico=-0.3)]
    res = ab.evaluar(filas, n_boot=200)
    assert set(res) == {"A0_mayoria", "A1_lexico", "A2_un_llm", "A3_consenso", "A4_abm"}
    assert res["A3_consenso"]["punto"] == 100.0  # consenso perfecto en el juguete


def test_pred_de_lee_el_campo_correcto():
    f = _f(2.0, 0.5, -0.9, lexico=0.2)
    assert ab.pred_de(f, "A3_consenso", 1) == 0.5
    assert ab.pred_de(f, "A4_abm", 1) == -0.9
    assert ab.pred_de(f, "A1_lexico", 1) == 0.2
    assert ab.pred_de(f, "A0_mayoria", -1) == -1


# ---- A0 honesto (train-only) y gate pareado por evento (auditoría v4) ----

def test_a0_no_mira_el_futuro_ni_su_propia_etiqueta():
    # fechas crecientes: 3 suben, la 4ª baja. A0 usa solo el pasado.
    filas = [_f(2.0, 0, 0, "A", "2020-01-01"), _f(2.0, 0, 0, "B", "2020-01-02"),
             _f(2.0, 0, 0, "C", "2020-01-03"), _f(-2.0, 0, 0, "D", "2020-01-04")]
    items = ab._items_a0(filas)
    assert len(items) == 3          # el 1º se abstiene (sin historia)
    assert [ok for ok, _ in items] == [1, 1, 0]  # +,+ aciertan; el 4º predice + y baja


def test_a0_en_evaluar_no_usa_signo_mayoria_global():
    # si A0 mirara TODO el set, con 2 subas vs 1 baja predeciría + y "acertaría" la
    # baja final nunca; aquí se comprueba que usa el pasado (expanding).
    filas = [_f(2.0, 0, 0, "A", "2020-01-01"), _f(-2.0, 0, 0, "B", "2020-01-02"),
             _f(2.0, 0, 0, "C", "2020-01-03")]
    items = ab._items_a0(filas)
    # caso2: historia=+1 → predice +, real baja → falla; caso3: historia 1-1 empate → abstiene
    assert [ok for ok, _ in items] == [0]


def test_gate_pareado_detecta_que_abm_resta():
    # mismo evento (misma fecha): A3 acierta, A4 invierte y falla → d = -1
    filas = [_f(2.0, 0.6, -0.6, "SPY", "2020-03-02"),
             _f(2.0, 0.6, -0.6, "QQQ", "2020-03-02"),
             _f(3.0, 0.6, -0.6, "DIA", "2020-03-03")]
    p = ab.gate_pareado(filas, n_boot=500)
    assert p["media"] == -1.0 and p["n"] == 3 and p["n_eventos"] == 2
    assert p["hi"] < 0 and p["excluye_cero"]  # IC excluye 0 por abajo


def test_gate_pareado_empate_no_concluyente():
    # A3 y A4 igual de buenos (ambos aciertan) → d = 0, IC no excluye 0
    filas = [_f(2.0, 0.5, 0.5, "SPY", "2020-03-02"),
             _f(-2.0, -0.5, -0.5, "QQQ", "2020-03-03")]
    p = ab.gate_pareado(filas, n_boot=500)
    assert p["media"] == 0.0 and not p["excluye_cero"]


def test_f02_a0_no_usa_etiquetas_del_mismo_dia():
    """Auditoría científica F02: 3 ETFs del MISMO día no deben informarse entre sí
    (sus etiquetas no están disponibles hasta días después)."""
    filas = [_f(2.0, 0, 0, "SPY", "2026-01-01"), _f(2.0, 0, 0, "QQQ", "2026-01-01"),
             _f(2.0, 0, 0, "DIA", "2026-01-01")]
    items = ab._items_a0(filas)
    assert items == []  # ninguno tiene historia previa madura → todos se abstienen
