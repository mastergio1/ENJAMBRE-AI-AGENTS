"""Fase 0.5 — Bootstrap multiway (por evento, activo y período).

El bootstrap por activo (intervalos.py) sube el peso de la dependencia entre
noticias del mismo símbolo, pero NO la de cuatro ETFs reaccionando a la MISMA
noticia (mismo día) ni la de bloques temporales (mismo régimen). Esta herramienta
recalcula el intervalo re-muestreando por distintas unidades de dependencia y
reporta todas, más la sensibilidad a excluir un instrumento. Si el intervalo se
ensancha mucho al agrupar por fecha, la independencia era menor de lo que parecía.

Puro y testeable (sin red).
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration.remedir_sin_fuga import _sg


def items_multi(filas, por_senal=True, zona=0.3, corte_senal=0.0):
    """[(acierto, claves)] para casos direccionables; claves = {simbolo, fecha, anio}."""
    out = []
    for f in filas:
        pc = f.get("pct_corr")
        if pc is None or abs(pc) < zona or abs(f["senal"]) < corte_senal:
            continue
        pred = f["senal"] if por_senal else f.get("direccion_pct", 0)
        ok = 1 if _sg(pred) == _sg(pc) else 0
        fecha = str(f.get("fecha", ""))[:10]
        out.append((ok, {"simbolo": f.get("simbolo"), "fecha": fecha,
                         "anio": str(f.get("anio") or fecha[:4])}))
    return out


def _ci_por_clave(items, clave, n_boot=3000, alpha=0.05, seed=42):
    """IC del acierto re-muestreando los CLÚSTERES definidos por `clave` (con
    reemplazo) y juntando sus casos. Devuelve punto, lo, hi, n, n_grupos."""
    if not items:
        return {"punto": None, "lo": None, "hi": None, "n": 0, "n_grupos": 0}
    punto = round(100 * sum(a for a, _ in items) / len(items), 1)
    por_grupo = {}
    for ok, claves in items:
        por_grupo.setdefault(claves.get(clave), []).append(ok)
    grupos = list(por_grupo.values())
    rng = random.Random(seed)
    fuente = grupos if len(grupos) >= 2 else [[x] for x, _ in items]
    muestras = []
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


def comparar_clusterings(filas, por_senal=True, zona=0.3, corte_senal=0.0, **kw):
    """IC bajo distintas unidades de dependencia: por activo, por evento (fecha) y
    por período (año). El más honesto es el más ANCHO."""
    items = items_multi(filas, por_senal, zona, corte_senal)
    return {clave: _ci_por_clave(items, clave, **kw)
            for clave in ("simbolo", "fecha", "anio")}


def sensibilidad_dejar_uno(filas, por_senal=True, zona=0.3, corte_senal=0.0):
    """Acierto excluyendo cada instrumento, uno a la vez. Si el resultado depende
    de un solo ETF, salta aquí."""
    simbolos = sorted({f.get("simbolo") for f in filas if f.get("simbolo")})
    out = {}
    for s in simbolos:
        sub = [f for f in filas if f.get("simbolo") != s]
        items = items_multi(sub, por_senal, zona, corte_senal)
        if items:
            acc = round(100 * sum(a for a, _ in items) / len(items), 1)
            out[f"sin {s}"] = {"acierto": acc, "n": len(items)}
    return out


def imprimir(filas, titulo=""):
    print(f"\n=== {titulo} — IC 95% según la unidad de dependencia ===")
    print(f"{'agrupado por':16}{'acierto%':>9}{'IC 95%':>16}{'n':>6}{'grupos':>8}")
    res = comparar_clusterings(filas)
    for clave in ("simbolo", "fecha", "anio"):
        d = res[clave]
        rango = f"[{d['lo']}–{d['hi']}]" if d["punto"] is not None else "—"
        print(f"{clave:16}{str(d['punto']):>9}{rango:>16}{d['n']:>6}{d['n_grupos']:>8}")
    print("\n  sensibilidad a excluir un instrumento:")
    for k, v in sensibilidad_dejar_uno(filas).items():
        print(f"    {k:14} acierto {v['acierto']}%  (n={v['n']})")
