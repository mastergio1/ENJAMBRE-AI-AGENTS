"""Tests del bootstrap multiway (Fase 0.5). Sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import intervalos_multiway as mw


def _f(pct, senal, simbolo="SPY", fecha="2020-01-01"):
    return {"pct_corr": pct, "senal": senal, "simbolo": simbolo, "fecha": fecha,
            "anio": int(fecha[:4])}


def test_items_multi_trae_las_tres_claves():
    items = mw.items_multi([_f(2.0, 0.5, "SPY", "2020-03-02")])
    assert len(items) == 1
    ok, claves = items[0]
    assert ok == 1 and claves == {"simbolo": "SPY", "fecha": "2020-03-02", "anio": "2020"}


def test_ci_todo_acierto_da_100():
    items = [(1, {"simbolo": f"s{i}", "fecha": f"2020-01-{i+1:02d}", "anio": "2020"})
             for i in range(10)]
    ci = mw._ci_por_clave(items, "simbolo", n_boot=300)
    assert ci["punto"] == 100.0 and ci["lo"] == 100.0 and ci["n_grupos"] == 10


def test_agrupar_por_fecha_reduce_los_grupos():
    # 4 casos el MISMO día → 1 solo grupo por fecha, pero 4 por símbolo
    filas = [_f(2.0, 0.5, s, "2020-03-02") for s in ("SPY", "QQQ", "DIA", "IWM")]
    res = mw.comparar_clusterings(filas, n_boot=200)
    assert res["simbolo"]["n_grupos"] == 4
    assert res["fecha"]["n_grupos"] == 1  # el mismo evento no son 4 experimentos


def test_sensibilidad_dejar_uno():
    filas = [_f(2.0, 0.5, "SPY"), _f(-2.0, 0.5, "QQQ")]  # SPY acierta, QQQ falla
    s = mw.sensibilidad_dejar_uno(filas)
    assert s["sin QQQ"]["acierto"] == 100.0  # sin el que falla, 100%
    assert s["sin SPY"]["acierto"] == 0.0     # sin el que acierta, 0%


def test_ci_mitad_mitad_cubre_50():
    items = ([(1, {"simbolo": f"a{i}", "fecha": f"d{i}", "anio": "2020"}) for i in range(40)]
             + [(0, {"simbolo": f"b{i}", "fecha": f"e{i}", "anio": "2020"}) for i in range(40)])
    ci = mw._ci_por_clave(items, "simbolo", n_boot=800)
    assert ci["punto"] == 50.0 and ci["lo"] < 50.0 < ci["hi"]
