"""El benchmark del motor (Fase 3): mide sin cambiar el comportamiento y es
reproducible por semilla — misma semilla da el MISMO resultado de simulación
(precio final, volumen), que es lo que permitirá verificar que una optimización
futura solo cambió la velocidad, no el modelo."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from calibration import benchmark_motor as bm


def test_reproducible_por_semilla():
    a = bm.correr(seed=7, ticks=40, medir_memoria=False)
    b = bm.correr(seed=7, ticks=40, medir_memoria=False)
    # el COMPORTAMIENTO es idéntico (los tiempos no, dependen de la máquina)
    assert a["precio_final"] == b["precio_final"]
    assert a["volumen_total"] == b["volumen_total"]


def test_semillas_distintas_dan_sesiones_distintas():
    a = bm.correr(seed=1, ticks=40, medir_memoria=False)
    b = bm.correr(seed=2, ticks=40, medir_memoria=False)
    assert a["precio_final"] != b["precio_final"]


def test_estructura_de_metricas():
    r = bm.correr(seed=3, ticks=30)
    assert r["n_agentes"] == 10150
    assert r["ticks"] == 30 and r["total_s"] > 0
    for k in ("p50", "p95", "max"):
        assert r["ms_por_tick"][k] >= 0
    assert r["mem_pico_mb"] is not None and r["mem_pico_mb"] > 0


def test_percentil_borde():
    assert bm._percentil([], 50) is None
    assert bm._percentil([5], 95) == 5
    assert bm._percentil([1, 2, 3, 4], 50) in (2, 3)  # cercano a la mediana
