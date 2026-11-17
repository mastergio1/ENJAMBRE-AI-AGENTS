"""Fase 0 — Intervalos de confianza y bancos por magnitud.

Dos piezas de la Fase 0 ("la verdad estadística"):

1. **Intervalos de confianza por bootstrap AGRUPADO POR ACTIVO.** Un acierto de
   "62%" sin barra de error no dice si es señal o ruido. El bootstrap re-muestrea
   los ACTIVOS (no los casos sueltos), porque varias noticias del mismo símbolo
   están correlacionadas y no son observaciones independientes (lo pidió la
   auditoría predictiva). Devuelve (punto, lo, hi).

2. **Bancos por magnitud del movimiento.** El cosechador eligió días de gran
   movimiento; esto separa el acierto por tamaño del movimiento POSTERIOR a la
   noticia (chico/medio/grande) para ver si el acierto se infla en los extremos.

Puro: opera sobre las filas re-medidas sin fuga (`contaminacion_temporal`),
sin red ni IA. Testeable con datos sintéticos.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration.remedir_sin_fuga import _sg


def items_acierto(filas, por_senal=True, zona=0.3, corte_senal=0.0):
    """[(acierto 0/1, grupo)] para casos direccionables. grupo = símbolo (para
    el bootstrap agrupado). `por_senal`: dirección de la señal (si no, del precio)."""
    out = []
    for f in filas:
        pc = f.get("pct_corr")
        if pc is None or abs(pc) < zona or abs(f["senal"]) < corte_senal:
            continue
        pred = f["senal"] if por_senal else f["direccion_pct"]
        ok = 1 if _sg(pred) == _sg(pc) else 0
        out.append((ok, f.get("simbolo", f.get("fecha", "?"))))
    return out


def bootstrap_ci(items, n_boot=3000, alpha=0.05, seed=42):
    """IC del acierto por bootstrap AGRUPADO: re-muestrea los grupos (activos) con
    reemplazo y junta todos sus casos. Devuelve punto, lo, hi (percentiles), n,
    n_grupos. Si hay <2 grupos cae al bootstrap de casos (mejor que nada)."""
    if not items:
        return {"punto": None, "lo": None, "hi": None, "n": 0, "n_grupos": 0}
    punto = round(100 * sum(a for a, _ in items) / len(items), 1)
    por_grupo = {}
    for ok, g in items:
        por_grupo.setdefault(g, []).append(ok)
    grupos = list(por_grupo.values())
    rng = random.Random(seed)
    muestras = []
    fuente = grupos if len(grupos) >= 2 else [[x] for x, _ in items]
    for _ in range(n_boot):
        pool = []
        for _ in range(len(fuente)):
            pool.extend(rng.choice(fuente))
        if pool:
            muestras.append(sum(pool) / len(pool))
    muestras.sort()
    lo = round(100 * muestras[int((alpha / 2) * len(muestras))], 1)
    hi = round(100 * muestras[int((1 - alpha / 2) * len(muestras)) - 1], 1)
    return {"punto": punto, "lo": lo, "hi": hi, "n": len(items), "n_grupos": len(grupos)}


def banco_magnitud(pct, chico=1.0, grande=3.0):
    """Clasifica el movimiento POSTERIOR por tamaño: chico / medio / grande."""
    a = abs(pct)
    if a < chico:
        return "chico"
    if a < grande:
        return "medio"
    return "grande"


def resumen_bancos(filas, por_senal=True, corte_senal=0.0, zona=0.3):
    """Acierto con IC por banco de magnitud del movimiento posterior."""
    bancos = {"chico": [], "medio": [], "grande": []}
    for f in filas:
        pc = f.get("pct_corr")
        if pc is None or abs(pc) < zona:
            continue
        bancos[banco_magnitud(pc)].append(f)
    return {b: bootstrap_ci(items_acierto(fs, por_senal, zona, corte_senal))
            for b, fs in bancos.items()}


def _linea(nombre, ci):
    p, lo, hi = ci["punto"], ci["lo"], ci["hi"]
    rango = f"[{lo}–{hi}]" if p is not None else "—"
    return f"{nombre:28}{str(p):>7} % {rango:>16}  (n={ci['n']}, activos={ci['n_grupos']})"


def imprimir(filas):
    indice = [f for f in filas if f["mercado"] == "indice"]
    print("\n=== INTERVALOS DE CONFIANZA (95%, bootstrap agrupado por activo) ===")
    print(_linea("TODOS — señal", bootstrap_ci(items_acierto(filas))))
    print(_linea("ÍNDICE — señal", bootstrap_ci(items_acierto(indice))))
    print(_linea("ÍNDICE — |señal|≥0.3", bootstrap_ci(items_acierto(indice, corte_senal=0.3))))
    print("\n=== BANCOS POR MAGNITUD (ÍNDICE, señal) — ¿se infla en los extremos? ===")
    for b, ci in resumen_bancos(indice).items():
        print(_linea(f"movimiento {b}", ci))


def main(cache):
    import json
    filas = json.load(open(cache))
    print(f"filas: {len(filas)}")
    imprimir(filas)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "calibracion.json.con_fecha.json")
