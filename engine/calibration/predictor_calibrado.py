"""Fase 5 — Predictor calibrado + abstención (curva riesgo-cobertura).

Hasta ahora medimos ACIERTO de dirección. Un producto serio necesita además:
  1. una PROBABILIDAD calibrada (no solo "sube/baja"): si dice 70%, que acierte ~70%.
  2. una política de ABSTENCIÓN: actuar solo cuando hay convicción, y REPORTAR la
     cobertura (no se puede comparar un modelo que opina en el 100% con otro que opina
     en el 20% sin igualar cobertura).

Toma la mejor señal disponible (el consenso A3, campo `senal`), la calibra con Platt
(logística de 1 variable) ENTRENANDO SOLO con el pasado, y evalúa fuera de muestra:
Brier, calibración (ECE) y la curva riesgo-cobertura (acierto si solo tomamos el X%
más confiado). Exploratorio (banco histórico). Sin IA.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

ZONA = 0.3


def armar(ruta_con_fecha, mercado="indice", campo="senal"):
    cf = json.loads(Path(ruta_con_fecha).read_text())
    filas = []
    for r in cf:
        if mercado and r.get("mercado") != mercado:
            continue
        pc = r.get("pct_corr")
        s = r.get(campo)
        if pc is None or abs(pc) < ZONA or s is None:
            continue
        filas.append({"x": float(s), "y": 1.0 if pc > 0 else 0.0, "fecha": str(r.get("fecha", ""))[:10]})
    return sorted(filas, key=lambda f: f["fecha"])


def _platt(x, y, pasos=4000, lr=0.3, l2=0.01):
    """Logística 1-D (a·x + b) → prob. Ajuste por gradiente. x estandarizado fuera."""
    a = b = 0.0
    n = len(x)
    for _ in range(pasos):
        p = 1.0 / (1.0 + np.exp(-(a * x + b)))
        g = p - y
        a -= lr * (float(np.mean(g * x)) + l2 * a)
        b -= lr * float(np.mean(g))
    return a, b


def _ece(p, y, bins=10):
    """Error de calibración esperado: |prob predicha − frecuencia real| por tramo."""
    e = 0.0
    for i in range(bins):
        lo, hi = i / bins, (i + 1) / bins
        m = (p >= lo) & (p < hi) if i < bins - 1 else (p >= lo) & (p <= hi)
        if m.sum() == 0:
            continue
        e += (m.sum() / len(p)) * abs(p[m].mean() - y[m].mean())
    return float(e)


def evaluar(ruta_con_fecha, mercado="indice", campo="senal", frac_train=0.7):
    filas = armar(ruta_con_fecha, mercado, campo)
    if len(filas) < 20:
        return {"suficiente": False, "n": len(filas)}
    k = int(len(filas) * frac_train)
    tr, te = filas[:k], filas[k:]
    xtr = np.array([f["x"] for f in tr]); ytr = np.array([f["y"] for f in tr])
    xte = np.array([f["x"] for f in te]); yte = np.array([f["y"] for f in te])
    mu, sd = xtr.mean(), xtr.std() + 1e-9
    a, b = _platt((xtr - mu) / sd, ytr)
    pte = 1.0 / (1.0 + np.exp(-(a * (xte - mu) / sd + b)))
    brier = float(np.mean((pte - yte) ** 2))
    base = ytr.mean()                      # tasa base del train
    brier_base = float(np.mean((base - yte) ** 2))
    # curva riesgo-cobertura: ordenar por confianza |p-0.5| y acierto acumulado
    conf = np.abs(pte - 0.5)
    orden = np.argsort(-conf)
    acierto = (np.round(pte) == yte).astype(float)[orden]
    cob = {}
    for frac in (1.0, 0.75, 0.5, 0.25):
        m = max(1, int(len(te) * frac))
        cob[f"{int(frac*100)}%"] = round(100 * acierto[:m].mean(), 1)
    return {
        "suficiente": True, "n": len(filas), "n_test": len(te),
        "brier": round(brier, 4), "brier_base": round(brier_base, 4),
        "brier_skill": round(1 - brier / brier_base, 3) if brier_base else None,
        "ece": round(_ece(pte, yte), 3),
        "acierto_por_cobertura": cob,
    }


def imprimir(ruta_con_fecha, mercados=("indice", None), campo="senal"):
    for m in mercados:
        r = evaluar(ruta_con_fecha, m, campo)
        etq = (m or "TODOS").upper()
        if not r.get("suficiente"):
            print(f"\n=== {etq}: muestra insuficiente (n={r['n']}) ===")
            continue
        print(f"\n=== Predictor calibrado · {etq} (test n={r['n_test']}) ===")
        print(f"  Brier {r['brier']} vs base {r['brier_base']}  →  skill {r['brier_skill']} "
              f"(>0 mejor que la tasa base; menor Brier = mejor)")
        print(f"  ECE (error de calibración) {r['ece']}  (0 = perfecto)")
        print(f"  acierto por cobertura (abstención): " +
              " · ".join(f"{k}:{v}%" for k, v in r["acierto_por_cobertura"].items()))


if __name__ == "__main__":
    campo = sys.argv[2] if len(sys.argv) > 2 else "senal"
    imprimir(sys.argv[1], campo=campo)
