"""L5 — Adaptador congelado del motor ABM (features deterministas).

Reutiliza los primitivos REALES del motor (`model.MercadoEnjambre`,
`agents.lider.LiderOpinion`, `brains.mercado.perfil_de`,
`calibration.barrido_poblacion._respuestas_congeladas` y los ticks TICKS_CAL/PREV/POST)
tal como los usa `calibration.riesgo_abm.correr_rico`, SIN hacer llamadas LLM extra: las
señales por arquetipo vienen CONGELADAS de la lectura P3 (confianza común 0.5).

Config FIJA: 10.150 agentes (la de HEAD), 3 semillas congeladas (1701,1702,1703). Extrae
las 6 features congeladas (I.5): retorno final mediano, dispersión de retornos finales,
volatilidad simulada mediana, desequilibrio de volumen agresor, max drawdown simulado,
rango. P5 recibe EXACTAMENTE P4 + este resumen (paridad de información).
"""
from __future__ import annotations

import statistics as stats

from .config import ABMCfg

SEEDS = ABMCfg().seeds  # (1701, 1702, 1703)


def disponible() -> bool:
    try:
        import mesa  # noqa: F401
        from model import MercadoEnjambre  # noqa: F401
        return True
    except Exception:
        return False


def _sa_desde_lectura(lectura: dict, confianza: float = 0.5) -> dict:
    """Convierte la lectura LLM (vector de arquetipos) al formato `senales_arquetipo`
    que espera `_respuestas_congeladas`: {arquetipo: {senal_media, confianza_media}}."""
    return {a: {"senal_media": float(v), "confianza_media": confianza}
            for a, v in lectura["archetypes"].items()}


def _max_drawdown(serie: list[float]) -> float:
    pico = serie[0] if serie else 0.0
    dd = 0.0
    for p in serie:
        pico = max(pico, p)
        if pico > 0:
            dd = max(dd, (pico - p) / pico)
    return dd


def _correr_una(sa: dict, mercado: str, seed: int) -> dict:
    """Una simulación con señales congeladas; mismas rutas que correr_rico."""
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
    modelo.aplicar_titular("", respuestas=resp, perfil=perfil_de(mercado or "indice"))
    serie = [previo]
    imbs = []
    for _ in range(TICKS_POST):
        modelo.step()
        serie.append(modelo.historial_precios[-1])
        fc = modelo.fraccion_compras(20)
        if fc is not None:
            imbs.append(abs(fc - 0.5))
    rets = [(serie[i] - serie[i - 1]) / serie[i - 1]
            for i in range(1, len(serie)) if serie[i - 1]]
    return {
        "ret_final": (serie[-1] - previo) / previo if previo else 0.0,  # SIGNED
        "vol_sim": float(np.std(rets)) if rets else 0.0,
        "imbalance": float(np.mean(imbs)) if imbs else 0.0,
        "drawdown": _max_drawdown(serie),
        "rango": (max(serie) - min(serie)) / previo if previo else 0.0,
    }


def features(lectura: dict, mercado: str = "indice", seeds=SEEDS,
             confianza: float = 0.5) -> dict:
    """Corre las `seeds` congeladas y agrega las 6 features del ABM. Determinista."""
    sa = _sa_desde_lectura(lectura, confianza)
    corridas = [_correr_una(sa, mercado, s) for s in seeds]
    finales = [c["ret_final"] for c in corridas]
    return {
        "ret_final_mediano": stats.median(finales),
        "dispersion_ret_final": stats.pstdev(finales) if len(finales) > 1 else 0.0,
        "vol_sim_mediana": stats.median(c["vol_sim"] for c in corridas),
        "desequilibrio_agresor": stats.median(c["imbalance"] for c in corridas),
        "max_drawdown_sim": stats.median(c["drawdown"] for c in corridas),
        "rango_sim": stats.median(c["rango"] for c in corridas),
    }
