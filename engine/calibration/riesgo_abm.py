"""Fase 4 — ¿El enjambre predice el RIESGO (magnitud del movimiento), no la dirección?

La hipótesis que podría rescatar al ABM (auditoría H14): aunque no acierte HACIA DÓNDE
se mueve el mercado, quizá anticipa CUÁNTO se mueve (volatilidad/fragilidad). Un buen
predictor de riesgo es un producto legítimo de gestión, aun sin alpha direccional.

Primer pase, SIN re-correr simulaciones: usa lo que el dataset ya tiene:
  - `volatilidad_pct`  : la volatilidad que SIMULÓ el enjambre.
  - `|direccion_pct|`  : la magnitud que simuló.
  - dispersión del consenso: desviación estándar de las señales por arquetipo
    (desacuerdo entre las voces → fragilidad esperada).
  - `|consenso|`       : fuerza de la señal (baseline).
Objetivo: `|pct_corr|` (cuánto se movió DE VERDAD el mercado, sin fuga).

Mide: (1) correlación de rango (Spearman) de cada feature con la magnitud real;
(2) fuera de muestra, ¿añadir las features del ABM reduce el error (MAE) al predecir
la magnitud, sobre un baseline que solo usa |consenso|? Exploratorio. Sin IA.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

ZONA = 0.3


def armar(ruta_con_fecha, ruta_raw, mercado="indice"):
    cf = json.loads(Path(ruta_con_fecha).read_text())
    crudo = json.loads(Path(ruta_raw).read_text())
    casos = crudo.get("casos", crudo) if isinstance(crudo, dict) else crudo
    idx = {}
    for c in casos:
        rr = c.get("reaccion_real") or {}
        idx[(rr.get("fecha_base"), rr.get("simbolo"))] = c
    filas = []
    for r in cf:
        if mercado and r.get("mercado") != mercado:
            continue
        pc = r.get("pct_corr")
        if pc is None:
            continue
        c = idx.get((r.get("fecha"), r.get("simbolo")))
        if not c:
            continue
        sa = c.get("senales_arquetipo") or {}
        señales = [float(v.get("senal_media", 0.0)) for v in sa.values()]
        dispersion = float(np.std(señales)) if señales else 0.0
        filas.append({
            "vol_abm": float(c.get("volatilidad_pct") or 0.0),
            "dir_abm_abs": abs(float(c.get("direccion_pct") or 0.0)),
            "dispersion": dispersion,
            "consenso_abs": abs(float(r.get("senal") or 0.0)),
            "magnitud_real": abs(float(pc)),
            "fecha": str(r.get("fecha", ""))[:10],
        })
    return filas


def spearman(x, y):
    """Correlación de rango de Spearman (rangos medios en empates, vía scipy).

    Fix F12 (auditoría): el doble `argsort` anterior asignaba rangos arbitrarios a los
    empates (una constante [1,1,1,1] recibía rangos [0,1,2,3], escapando al chequeo de
    varianza y produciendo correlación espuria). Ahora usa `scipy.stats.spearmanr`
    (rangos medios correctos) y devuelve `None` si alguna variable es constante.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3:
        return None
    if np.unique(x).size < 2 or np.unique(y).size < 2:
        return None  # variable constante: correlación indefinida
    from scipy.stats import spearmanr
    rho, _ = spearmanr(x, y)
    return None if np.isnan(rho) else float(rho)


def _mae_oos(filas, feats, frac_train=0.7):
    """MAE fuera de muestra al predecir la magnitud real con regresión lineal sobre
    `feats` (ajuste y estandarización solo con train). feats=[] → predice la media."""
    filas = sorted(filas, key=lambda f: f["fecha"])
    k = int(len(filas) * frac_train)
    tr, te = filas[:k], filas[k:]
    ytr = np.array([f["magnitud_real"] for f in tr])
    yte = np.array([f["magnitud_real"] for f in te])
    if not feats:
        return float(np.abs(yte - ytr.mean()).mean())
    Xtr = np.array([[f[c] for c in feats] for f in tr], float)
    Xte = np.array([[f[c] for c in feats] for f in te], float)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    Xtr = np.column_stack([np.ones(len(tr)), (Xtr - mu) / sd])
    Xte = np.column_stack([np.ones(len(te)), (Xte - mu) / sd])
    w, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
    pred = Xte @ w
    return float(np.abs(yte - pred).mean())


def evaluar(ruta_con_fecha, ruta_raw, mercado="indice"):
    filas = armar(ruta_con_fecha, ruta_raw, mercado)
    y = [f["magnitud_real"] for f in filas]
    def _r(c):
        v = spearman([f[c] for f in filas], y)
        return round(v, 3) if v is not None else None
    corr = {c: _r(c) for c in ("vol_abm", "dir_abm_abs", "dispersion", "consenso_abs")}
    mae = {
        "constante (media)": round(_mae_oos(filas, []), 3),
        "solo |consenso|": round(_mae_oos(filas, ["consenso_abs"]), 3),
        "+ features ABM": round(_mae_oos(filas, ["consenso_abs", "vol_abm", "dir_abm_abs", "dispersion"]), 3),
    }
    return {"n": len(filas), "spearman": corr, "mae_oos": mae}


def imprimir(ruta_con_fecha, ruta_raw, mercados=("indice", None)):
    for m in mercados:
        r = evaluar(ruta_con_fecha, ruta_raw, m)
        print(f"\n=== Riesgo (magnitud) · {(m or 'TODOS').upper()} ({r['n']} casos) ===")
        print("  correlación de rango (Spearman) con la magnitud REAL:")
        for c, v in r["spearman"].items():
            print(f"    {c:16} {'  n/d (constante)' if v is None else f'{v:+.3f}'}")
        print("  MAE fuera de muestra al predecir la magnitud (menor = mejor):")
        for c, v in r["mae_oos"].items():
            print(f"    {c:20} {v}")


if __name__ == "__main__":
    imprimir(sys.argv[1], sys.argv[2])


# ---------- Versión COMPLETA de H14: features ricas re-corriendo la simulación ----------

def correr_rico(titular, sa, mercado, magnitud_real, seed=20260101):
    """Corre una simulación (N completo, señales congeladas) y extrae features de
    RIESGO/microestructura del tramo posterior a la noticia."""
    import numpy as np
    from agents.lider import LiderOpinion
    from brains.mercado import perfil_de
    from calibration.barrido_poblacion import (TICKS_CAL, TICKS_POST, TICKS_PREV,
                                               _respuestas_congeladas)
    from model import MercadoEnjambre

    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=TICKS_CAL + TICKS_POST)
    modelo.correr(TICKS_CAL)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]
    resp = _respuestas_congeladas(lideres, sa)
    for _ in range(TICKS_PREV):
        modelo.step()
    previo = modelo.historial_precios[-1]
    modelo.aplicar_titular(titular, respuestas=resp, perfil=perfil_de(mercado or "indice"))
    serie = [previo]
    imbs = []
    for _ in range(TICKS_POST):
        modelo.step()
        serie.append(modelo.historial_precios[-1])
        fc = modelo.fraccion_compras(20)
        if fc is not None:
            imbs.append(abs(fc - 0.5))  # desequilibrio de órdenes (0 = balance)
    rets = [(serie[i] - serie[i - 1]) / serie[i - 1] for i in range(1, len(serie)) if serie[i - 1]]
    excur = max(abs(p - previo) for p in serie) / previo if previo else 0.0  # sobre-reacción
    final = abs(serie[-1] - previo) / previo if previo else 0.0
    disp = float(np.std([v.get("senal_media", 0.0) for v in sa.values()])) if sa else 0.0
    return {
        "vol_sim": float(np.std(rets)) if rets else 0.0,
        "imbalance": float(np.mean(imbs)) if imbs else 0.0,
        "overshoot": excur,
        "reversal": max(0.0, excur - final),       # cuánto se devolvió tras el pico
        "rango": (max(serie) - min(serie)) / previo if previo else 0.0,
        "dispersion": disp,
        "magnitud_real": magnitud_real,
        "fecha": "",
    }


def extraer_todos(ruta_con_fecha, ruta_raw, salida, seed=20260101):
    """Corre la sim por cada caso de índice y guarda sus features ricas (lento)."""
    import json as _json

    from calibration.barrido_poblacion import _casos_indice
    casos = _casos_indice(ruta_con_fecha, ruta_raw)
    filas = []
    for i, c in enumerate(casos):
        f = correr_rico(c["titular"], c["sa"], c["mercado"], abs(c["pct_corr"]), seed)
        f["fecha"] = c["fecha"]
        filas.append(f)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(casos)}", flush=True)
    Path(salida).write_text(_json.dumps(filas))
    return filas


def evaluar_rico(filas):
    FEATS = ["vol_sim", "imbalance", "overshoot", "reversal", "rango", "dispersion"]
    y = [f["magnitud_real"] for f in filas]

    def _r(c):
        v = spearman([f[c] for f in filas], y)
        return round(v, 3) if v is not None else None
    corr = {c: _r(c) for c in FEATS}
    mae = {
        "constante (media)": round(_mae_oos(filas, []), 3),
        "+ features ricas ABM": round(_mae_oos(filas, FEATS), 3),
    }
    return {"n": len(filas), "spearman": corr, "mae_oos": mae}
