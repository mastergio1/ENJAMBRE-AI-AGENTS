"""Fase 6 — Evaluador del experimento prospectivo (sellado → resuelto sin fuga).

Consume los registros YA RESUELTOS del registro prospectivo (tabla `predicciones`) y
calcula, según el pre-registro (`docs/preregistro-fase6.md`): acierto direccional con
cobertura, acierto "solo fiables" (gating), Brier calibrado vs tasa base, y el IC
pareado por evento (cluster bootstrap). No mira el histórico sesgado: solo predicciones
hechas ANTES de conocer el desenlace. Sin IA.

Cada registro: {mercado, direccion('alza'|'baja'|'neutra'), probabilidad|None,
pct_real(resuelto), fiable(0/1), abstenido(0/1), fecha}. Para alimentarlo en vivo,
exportar las filas resueltas de `predicciones` a una lista de dicts.
"""
import json
import random
import sys
from pathlib import Path


def _sg(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _dir_sign(d):
    return {"alza": 1, "baja": -1}.get(d, 0)


def _puntuables(registros, solo_fiables=False, zona=0.0):
    """Resueltas, no abstenidas, con dirección y movimiento real no neutro."""
    out = []
    for r in registros:
        pc = r.get("pct_real")
        if pc is None or abs(pc) < zona:
            continue
        if r.get("abstenido"):
            continue
        pred = _dir_sign(r.get("direccion"))
        if pred == 0:
            continue
        if solo_fiables and not r.get("fiable"):
            continue
        out.append({**r, "ok": 1 if pred == _sg(pc) else 0,
                    "y": 1.0 if pc > 0 else 0.0})
    return out


def _ci_evento(items, n_boot=3000, seed=42):
    """IC 95% del acierto re-muestreando EVENTOS (misma fecha = mismo anuncio)."""
    if not items:
        return {"punto": None, "lo": None, "hi": None}
    por = {}
    for it in items:
        por.setdefault(str(it.get("fecha", ""))[:10], []).append(it["ok"])
    grupos = list(por.values())
    punto = round(100 * sum(it["ok"] for it in items) / len(items), 1)
    rng = random.Random(seed)
    muestras = []
    for _ in range(n_boot):
        pool = []
        for _ in range(len(grupos)):
            pool.extend(rng.choice(grupos))
        if pool:
            muestras.append(sum(pool) / len(pool))
    muestras.sort()
    lo = round(100 * muestras[int(0.025 * len(muestras))], 1)
    hi = round(100 * muestras[int(0.975 * len(muestras)) - 1], 1)
    return {"punto": punto, "lo": lo, "hi": hi, "n": len(items), "n_eventos": len(grupos)}


def _brier(items):
    """Brier de la probabilidad calibrada vs tasa base (solo items con probabilidad)."""
    con_p = [it for it in items if it.get("probabilidad") is not None]
    if not con_p:
        return None
    y = [it["y"] for it in con_p]
    p = [float(it["probabilidad"]) for it in con_p]
    base = sum(y) / len(y)
    bm = sum((pi - yi) ** 2 for pi, yi in zip(p, y)) / len(y)
    bb = sum((base - yi) ** 2 for yi in y) / len(y)
    return {"brier": round(bm, 4), "brier_base": round(bb, 4),
            "skill": round(1 - bm / bb, 3) if bb else None, "n": len(con_p)}


def evaluar(registros, mercado=None):
    sub = [r for r in registros if mercado is None or r.get("mercado") == mercado]
    resueltas = [r for r in sub if r.get("pct_real") is not None]
    todos = _puntuables(sub)
    fiables = _puntuables(sub, solo_fiables=True)
    cobertura = round(100 * len(todos) / len(resueltas), 1) if resueltas else None
    return {
        "n_total": len(sub), "n_resueltas": len(resueltas),
        "cobertura_pct": cobertura,
        "acierto_todos": _ci_evento(todos),
        "acierto_fiables": _ci_evento(fiables),
        "brier": _brier(todos),
    }


def imprimir(registros, mercados=("indice", "accion", None)):
    for m in mercados:
        r = evaluar(registros, m)
        etq = (m or "TODOS").upper()
        print(f"\n=== Prospectivo · {etq} ===")
        print(f"  resueltas: {r['n_resueltas']}  ·  cobertura: {r['cobertura_pct']}%")
        a = r["acierto_todos"]
        if a["punto"] is not None:
            print(f"  acierto (todos):   {a['punto']}%  IC95 [{a['lo']}, {a['hi']}]  "
                  f"(n={a['n']}, {a['n_eventos']} eventos)")
        f = r["acierto_fiables"]
        if f["punto"] is not None:
            print(f"  acierto (fiables): {f['punto']}%  IC95 [{f['lo']}, {f['hi']}]  (n={f['n']})")
        if r["brier"]:
            print(f"  Brier {r['brier']['brier']} vs base {r['brier']['brier_base']} "
                  f"(skill {r['brier']['skill']})")
        if (a["n"] if a["punto"] is not None else 0) < 100:
            print("  ⚠️ muestra INSUFICIENTE para veredicto (pre-registro: ≥100 eventos).")


if __name__ == "__main__":
    registros = json.loads(Path(sys.argv[1]).read_text())
    imprimir(registros)
