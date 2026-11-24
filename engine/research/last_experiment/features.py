"""L4 — Variables financieras comunes point-in-time (sin fuga).

A partir de una serie de cierres de SPY TERMINADA antes del cutoff, calcula las
variables de mercado que alimentan P1/P4/P5 (I.4): retornos 1/5/20 sesiones,
volatilidad 20 sesiones, momentum. Exige un mínimo de historia (60 sesiones). No usa
`bfill` ni datos posteriores. También calcula la sorpresa macro con indicador de
ausencia (no imputa 0 silenciosamente).

La imputación (mediana de train) y la normalización se ajustan SOLO en train; eso vive
en `models.py`. Aquí solo se extraen variables crudas con sus indicadores de ausencia.
"""
from __future__ import annotations

import math

MIN_HISTORIA = 60  # sesiones mínimas de historia antes del cutoff (I.4)

# Nombres de features de mercado en orden estable (contrato con models.py).
FEATURES_MERCADO = (
    "ret_1", "ret_5", "ret_20", "vol_20", "momentum_5_20",
)
# Features de sorpresa macro (con indicadores de ausencia).
FEATURES_MACRO = (
    "sorpresa", "sorpresa_falta", "sorpresa_std", "sorpresa_std_falta",
)


def _log_ret(serie: list[float], n: int) -> float | None:
    """Retorno simple acumulado de las últimas n sesiones: serie[-1]/serie[-1-n]-1."""
    if len(serie) < n + 1:
        return None
    a, b = serie[-1 - n], serie[-1]
    if a <= 0:
        return None
    return b / a - 1.0


def features_mercado(cierres: list[float]) -> dict:
    """Variables de mercado a partir de cierres (el último es el de la sesión de
    emisión, ya terminada al cutoff). Devuelve dict con las features y `suficiente`.

    `cierres` debe contener SOLO sesiones cerradas antes del cutoff.
    """
    out: dict = {k: None for k in FEATURES_MERCADO}
    out["suficiente"] = len(cierres) >= MIN_HISTORIA
    if not cierres:
        return out
    out["ret_1"] = _log_ret(cierres, 1)
    out["ret_5"] = _log_ret(cierres, 5)
    out["ret_20"] = _log_ret(cierres, 20)
    # volatilidad 20 sesiones = desv. estándar de retornos diarios de las últimas 20
    if len(cierres) >= 21:
        rets = [cierres[i] / cierres[i - 1] - 1.0
                for i in range(len(cierres) - 20, len(cierres))
                if cierres[i - 1] > 0]
        if len(rets) >= 2:
            mu = sum(rets) / len(rets)
            var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
            out["vol_20"] = math.sqrt(var)
    # momentum: ret_5 - ret_20 (proxy de aceleración)
    if out["ret_5"] is not None and out["ret_20"] is not None:
        out["momentum_5_20"] = out["ret_5"] - out["ret_20"]
    return out


def features_macro(actual: float | None, esperado: float | None,
                   desv_historica: float | None = None) -> dict:
    """Sorpresa macro = actual - esperado, con indicador de ausencia (I.4).

    No convierte una expectativa ausente en cero: marca `sorpresa_falta=1`. La sorpresa
    estandarizada solo si hay desviación histórica conocida en desarrollo.
    """
    out = {k: 0.0 for k in FEATURES_MACRO}
    if actual is None or esperado is None:
        out["sorpresa_falta"] = 1.0
        out["sorpresa_std_falta"] = 1.0
        out["sorpresa"] = 0.0
        out["sorpresa_std"] = 0.0
        return out
    sp = actual - esperado
    out["sorpresa"] = sp
    out["sorpresa_falta"] = 0.0
    if desv_historica and desv_historica > 0:
        out["sorpresa_std"] = sp / desv_historica
        out["sorpresa_std_falta"] = 0.0
    else:
        out["sorpresa_std"] = 0.0
        out["sorpresa_std_falta"] = 1.0
    return out


def vector_features(mercado: dict, macro: dict | None = None) -> dict:
    """Une mercado + macro en un único dict de features crudas (valores o None)."""
    v = {k: mercado.get(k) for k in FEATURES_MERCADO}
    if macro:
        for k in FEATURES_MACRO:
            v[k] = macro.get(k)
    return v
