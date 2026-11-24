"""Fase 1/5 — Metamodelo M13 vs M13-null (la comparación PRIMARIA del plan v5).

Pregunta: ¿las features del ABM (dirección y volatilidad simuladas) reducen la
pérdida predictiva (Brier) sobre EXACTAMENTE la misma información SIN el ABM (solo el
consenso de líderes)? Es el test de valor incremental del motor de agentes.

- **M13**      = logística(consenso, direccion_pct_ABM, volatilidad_pct_ABM)
- **M13-null** = logística(consenso)              ← mismo pipeline, sin features ABM

Honestidad (auditoría científica):
- Partición TEMPORAL: se ajusta con el pasado (70%) y se evalúa en el futuro (30%).
- Estandarización y ajuste SOLO con train (sin mirar el test).
- Diferencia PAREADA por evento (misma fecha) con cluster bootstrap → IC honesto.
- Este resultado es EXPLORATORIO: corre sobre el banco histórico de shocks (sesgado
  por selección). El veredicto definitivo es prospectivo. d>0 ⇒ el ABM ayuda; que el
  IC excluya 0 ⇒ diferencia significativa dentro de esta muestra.

Sin red ni IA: usa números ya calculados. Logística L2 propia (numpy), sin sklearn.
"""
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

ZONA = 0.3
FEAT_CON = ["senal", "direccion_pct", "volatilidad_pct"]
FEAT_SIN = ["senal"]


def armar_filas(ruta_con_fecha, ruta_raw):
    """Une con_fecha (senal, direccion_pct, pct_corr, fecha, mercado) con el export
    crudo (volatilidad_pct) por (fecha_base, simbolo). Etiqueta y=1 si pct_corr>0.
    Solo casos direccionables (|pct_corr|>=ZONA)."""
    cf = json.loads(Path(ruta_con_fecha).read_text())
    crudo = json.loads(Path(ruta_raw).read_text())
    casos = crudo.get("casos", crudo) if isinstance(crudo, dict) else crudo
    vol_por = {}
    for c in casos:
        rr = c.get("reaccion_real") or {}
        k = (rr.get("fecha_base"), rr.get("simbolo"))
        if k[0] and k[1]:
            vol_por.setdefault(k, c.get("volatilidad_pct"))
    filas = []
    for r in cf:
        pc = r.get("pct_corr")
        if pc is None or abs(pc) < ZONA:
            continue
        vol = vol_por.get((r.get("fecha"), r.get("simbolo")))
        if vol is None:
            continue
        filas.append({"senal": float(r.get("senal") or 0.0),
                      "direccion_pct": float(r.get("direccion_pct") or 0.0),
                      "volatilidad_pct": float(vol),
                      "y": 1.0 if pc > 0 else 0.0,
                      "fecha": str(r.get("fecha", ""))[:10],
                      "mercado": r.get("mercado")})
    return filas


def _entrenar(X, y, l2=1.0, pasos=3000, lr=0.2):
    """Logística con regularización L2 por descenso de gradiente. X estandarizada."""
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    for _ in range(pasos):
        p = 1.0 / (1.0 + np.exp(-(X @ w + b)))
        g = p - y
        w -= lr * (X.T @ g / n + l2 * w / n)
        b -= lr * g.mean()
    return w, b


def _ajustar_y_predecir(tr, te, feats, l2):
    Xtr = np.array([[f[c] for c in feats] for f in tr], float)
    Xte = np.array([[f[c] for c in feats] for f in te], float)
    ytr = np.array([f["y"] for f in tr], float)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9  # estandarización SOLO con train
    w, b = _entrenar((Xtr - mu) / sd, ytr, l2)
    return 1.0 / (1.0 + np.exp(-(((Xte - mu) / sd) @ w + b)))


def evaluar(filas, mercado=None, l2=1.0, frac_train=0.7, n_boot=3000, seed=42):
    """Brier de M13 y M13-null fuera de muestra + diferencia pareada por evento."""
    sub = [f for f in filas if mercado is None or f.get("mercado") == mercado]
    sub = sorted(sub, key=lambda f: f["fecha"])
    k = int(len(sub) * frac_train)
    tr, te = sub[:k], sub[k:]
    if len(tr) < 10 or len(te) < 5:
        return {"n_train": len(tr), "n_test": len(te), "suficiente": False}
    yte = np.array([f["y"] for f in te], float)
    p_con = _ajustar_y_predecir(tr, te, FEAT_CON, l2)
    p_sin = _ajustar_y_predecir(tr, te, FEAT_SIN, l2)
    brier_con = float(((p_con - yte) ** 2).mean())
    brier_sin = float(((p_sin - yte) ** 2).mean())
    # d_i = (p_sinABM - y)^2 - (p_conABM - y)^2 ; media>0 favorece al ABM
    d = (p_sin - yte) ** 2 - (p_con - yte) ** 2
    por_evento = {}
    for fila, di in zip(te, d):
        por_evento.setdefault(fila["fecha"], []).append(float(di))
    grupos = list(por_evento.values())
    rng = random.Random(seed)
    muestras = []
    for _ in range(n_boot):
        pool = []
        for _ in range(len(grupos)):
            pool.extend(rng.choice(grupos))
        if pool:
            muestras.append(sum(pool) / len(pool))
    muestras.sort()
    lo = muestras[int(0.025 * len(muestras))]
    hi = muestras[int(0.975 * len(muestras)) - 1]
    return {
        "suficiente": True, "n_train": len(tr), "n_test": len(te),
        "n_eventos_test": len(grupos),
        "brier_M13": round(brier_con, 4), "brier_M13_null": round(brier_sin, 4),
        "media_d": round(float(d.mean()), 4),
        "ic95": [round(lo, 4), round(hi, 4)],
        "abm_ayuda": bool(d.mean() > 0),
        "significativo": bool(hi < 0 or lo > 0),
    }


def imprimir(filas, mercados=("indice", None)):
    for m in mercados:
        r = evaluar(filas, mercado=m)
        etq = (m or "TODOS").upper()
        print(f"\n=== M13 vs M13-null · {etq} (EXPLORATORIO, banco histórico) ===")
        if not r.get("suficiente"):
            print(f"  muestra insuficiente (train={r['n_train']}, test={r['n_test']})")
            continue
        print(f"  Brier M13 (con ABM)  = {r['brier_M13']}   (menor es mejor)")
        print(f"  Brier M13-null (sin) = {r['brier_M13_null']}")
        print(f"  media(d)=Brier_null−Brier_con = {r['media_d']}  IC95 {r['ic95']}  "
              f"({r['n_test']} casos / {r['n_eventos_test']} eventos)")
        if r["significativo"]:
            print(f"  → {'el ABM AYUDA' if r['abm_ayuda'] else 'el ABM RESTA'} (IC excluye 0)")
        else:
            print("  → no concluyente (IC cruza 0): el ABM no muestra valor incremental claro")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    imprimir(armar_filas(sys.argv[1], sys.argv[2]))
