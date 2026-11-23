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
    assert set(res) == {"A0_mayoria", "A1_lexico", "A3_consenso", "A4_abm"}
    assert res["A3_consenso"]["punto"] == 100.0  # consenso perfecto en el juguete


def test_pred_de_lee_el_campo_correcto():
    f = _f(2.0, 0.5, -0.9, lexico=0.2)
    assert ab.pred_de(f, "A3_consenso", 1) == 0.5
    assert ab.pred_de(f, "A4_abm", 1) == -0.9
    assert ab.pred_de(f, "A1_lexico", 1) == 0.2
    assert ab.pred_de(f, "A0_mayoria", -1) == -1
