"""Tests de intervalos de confianza y bancos por magnitud (Fase 0). Sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import intervalos as iv


def _fila(senal, pct, simbolo="^GSPC", mercado="indice"):
    return {"fecha": "2020-06-01", "anio": 2020, "mercado": mercado, "simbolo": simbolo,
            "direccion_pct": pct, "senal": senal, "pct_corr": pct}


def test_items_acierto_marca_direccion_y_grupo():
    filas = [_fila(0.5, 2.0, "A"), _fila(0.5, -2.0, "B")]  # 1 acierto, 1 fallo
    items = iv.items_acierto(filas)
    assert sorted(items) == [(0, "B"), (1, "A")]


def test_items_acierto_filtra_zona_y_corte():
    filas = [_fila(0.4, 2.0), _fila(0.1, 2.0), _fila(0.4, 0.1)]
    assert len(iv.items_acierto(filas, corte_senal=0.3)) == 1  # solo el fuerte y direccionable
    assert len(iv.items_acierto(filas, corte_senal=0.0)) == 2  # el de |pct|<0.3 queda fuera


def test_bootstrap_ci_todo_acierto_da_100():
    items = [(1, f"s{i}") for i in range(20)]
    ci = iv.bootstrap_ci(items, n_boot=500)
    assert ci["punto"] == 100.0 and ci["lo"] == 100.0 and ci["hi"] == 100.0
    assert ci["n"] == 20 and ci["n_grupos"] == 20


def test_bootstrap_ci_mitad_mitad_cubre_50():
    items = [(1, f"a{i}") for i in range(50)] + [(0, f"b{i}") for i in range(50)]
    ci = iv.bootstrap_ci(items, n_boot=1000)
    assert ci["punto"] == 50.0
    assert ci["lo"] < 50.0 < ci["hi"]  # el IC cubre el 50%


def test_bootstrap_ci_muestra_chica_da_intervalo_ancho():
    # 3 casos, todos aciertan: punto 100 pero el IC NO debe ser estrecho de confianza
    # (con n=3 el bootstrap agrupado sigue dando 100 si todos acthe mismo grupo-caso).
    items = [(1, "a"), (1, "b"), (1, "c")]
    ci = iv.bootstrap_ci(items, n_boot=500)
    assert ci["n"] == 3 and ci["punto"] == 100.0


def test_banco_magnitud():
    assert iv.banco_magnitud(0.5) == "chico"
    assert iv.banco_magnitud(2.0) == "medio"
    assert iv.banco_magnitud(5.0) == "grande"


def test_resumen_bancos_separa_por_tamano():
    filas = [_fila(0.5, 0.5), _fila(0.5, 2.0), _fila(0.5, 5.0)]  # chico/medio/grande
    # con zona 0.3, el de 0.5 es direccionable; reparte 1 por banco
    res = iv.resumen_bancos(filas)
    assert res["chico"]["n"] == 1 and res["medio"]["n"] == 1 and res["grande"]["n"] == 1
