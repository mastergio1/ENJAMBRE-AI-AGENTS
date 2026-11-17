"""Benchmark REPRODUCIBLE del motor (Fase 3, paso 1 de la auditoría).

"No optimizar a ciegas: primero un benchmark reproducible." Esta herramienta mide
el coste del motor (tiempo por tick, ticks/seg, memoria pico) con semilla FIJA y
SIN IA, para tener una línea base antes de tocar nada — y para comprobar después
que una optimización no cambió el comportamiento ni empeoró el tiempo.

NO cambia el motor. Es determinística: misma semilla → mismos números de
comportamiento (precio final, volumen); los tiempos varían con la máquina, por eso
se reportan percentiles, no un único promedio frágil.

Uso:
    python3 engine/calibration/benchmark_motor.py [seed] [ticks]
"""
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from model import MercadoEnjambre


def _percentil(valores, p):
    if not valores:
        return None
    orden = sorted(valores)
    k = max(0, min(len(orden) - 1, int(round((p / 100) * (len(orden) - 1)))))
    return orden[k]


def correr(seed: int = 42, ticks: int = 600, prob_noticia: float = 0.02,
           medir_memoria: bool = True) -> dict:
    """Corre una sesión headless cronometrando cada step(). Devuelve métricas de
    tiempo (ms por tick) + de comportamiento (para confirmar reproducibilidad)."""
    if medir_memoria:
        tracemalloc.start()
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=ticks)
    por_tick_ms = []
    t0 = time.perf_counter()
    for _ in range(ticks):
        if modelo.random.random() < prob_noticia:
            modelo.aplicar_noticia(modelo.random.gauss(0, 0.45))
        ini = time.perf_counter()
        modelo.step()
        por_tick_ms.append((time.perf_counter() - ini) * 1000)
    total_s = time.perf_counter() - t0

    mem_pico_mb = None
    if medir_memoria:
        _, pico = tracemalloc.get_traced_memory()
        mem_pico_mb = round(pico / 1_000_000, 1)
        tracemalloc.stop()

    volumen = sum(modelo.flujo_compras) + sum(modelo.flujo_ventas)
    return {
        "seed": seed,
        "ticks": ticks,
        "n_agentes": len(modelo.agents) if hasattr(modelo, "agents") else None,
        "total_s": round(total_s, 3),
        "ticks_por_seg": round(ticks / total_s, 1) if total_s else None,
        "ms_por_tick": {
            "p50": round(_percentil(por_tick_ms, 50), 3),
            "p95": round(_percentil(por_tick_ms, 95), 3),
            "max": round(max(por_tick_ms), 3),
        },
        "mem_pico_mb": mem_pico_mb,
        # comportamiento (reproducible por semilla): sirve para verificar que una
        # optimización futura NO cambió la simulación, solo su velocidad.
        "precio_final": round(modelo.historial_precios[-1], 4),
        "volumen_total": round(volumen, 1),
    }


def imprimir(r: dict) -> None:
    print(f"seed={r['seed']}  ticks={r['ticks']}  agentes={r['n_agentes']}")
    print(f"total: {r['total_s']}s   {r['ticks_por_seg']} ticks/seg")
    m = r["ms_por_tick"]
    print(f"ms/tick  p50={m['p50']}  p95={m['p95']}  max={m['max']}")
    print(f"memoria pico: {r['mem_pico_mb']} MB")
    print(f"[reproducibilidad] precio_final={r['precio_final']}  volumen={r['volumen_total']}")


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    imprimir(correr(seed, ticks))
