"""Fase 3/4 (preview) — ¿El enjambre le gana a un baseline razonable?

La pregunta central de la auditoría: un 63% suelto no dice nada si un modelo tonto
también acierta 63%. Aquí comparamos, fuera de muestra y con el mismo resultado SIN
FUGA, la señal del enjambre contra baselines honestos:

- **mayoría:** predecir siempre la dirección más común del TRAIN (el piso a batir).
- **momentum:** predecir que el movimiento PREVIO a la noticia continúa.
- **señal del enjambre:** la dirección de la señal ponderada de los líderes.
- **precio simulado:** la dirección del precio que produce el ABM (separar A3 vs A4).

Núcleo puro y testeable; la recolección de datos (Yahoo) vive aparte.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration.remedir_sin_fuga import _sg


def acc_regla(filas, pred_fn, zona=0.3):
    """(acierto%, n_opina, n_direccionable) de una regla sobre casos con
    movimiento |pct_corr| ≥ zona. `pred_fn(fila)` devuelve un número cuyo SIGNO es
    la predicción (0 = la regla se abstiene en ese caso)."""
    dire = [f for f in filas if f.get("pct_corr") is not None and abs(f["pct_corr"]) >= zona]
    usables = [f for f in dire if pred_fn(f) not in (0, None)]
    if not usables:
        return (None, 0, len(dire))
    ok = sum(1 for f in usables if _sg(pred_fn(f)) == _sg(f["pct_corr"]))
    return (round(100 * ok / len(usables), 1), len(usables), len(dire))


def regla_mayoria(train, zona=0.3):
    """Devuelve una regla que predice SIEMPRE la dirección mayoritaria del train
    (el predictor constante óptimo: el piso honesto a batir)."""
    dire = [f for f in train if f.get("pct_corr") is not None and abs(f["pct_corr"]) >= zona]
    subas = sum(1 for f in dire if f["pct_corr"] > 0)
    bajas = len(dire) - subas
    signo = 1 if subas >= bajas else -1
    return lambda f: signo


def regla_momentum(f):
    """Predice que el movimiento PREVIO a la noticia continúa."""
    return f.get("mom_prev", 0)


def regla_senal(f):
    return f.get("senal", 0)


def regla_precio(f):
    return f.get("direccion_pct", 0)


def comparar(train, test, zona=0.3):
    """Compara en TEST (fuera de muestra) los baselines y el enjambre."""
    reglas = {
        "mayoria": regla_mayoria(train, zona),
        "momentum": regla_momentum,
        "senal_enjambre": regla_senal,
        "precio_simulado": regla_precio,
    }
    return {nombre: acc_regla(test, fn, zona) for nombre, fn in reglas.items()}


def imprimir(res, titulo=""):
    print(f"\n=== {titulo} — acierto fuera de muestra (sin fuga) ===")
    print(f"{'regla':18}{'acierto%':>10}{'n_opina':>9}{'n_dir':>8}")
    for nombre in ("mayoria", "momentum", "senal_enjambre", "precio_simulado"):
        a, nop, ndir = res[nombre]
        print(f"{nombre:18}{str(a):>10}{nop:>9}{ndir:>8}")


def main(cache):
    import json
    filas = [f for f in json.load(open(cache)) if f.get("mercado") == "indice"]
    filas.sort(key=lambda x: x["fecha"])
    corte = int(len(filas) * 0.7)
    train, test = filas[:corte], filas[corte:]
    print(f"índice: {len(filas)} casos | train {len(train)} test {len(test)}")
    imprimir(comparar(train, test), "ÍNDICE")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "indice_baselines.json")
