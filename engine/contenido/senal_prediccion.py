"""Señal de PREDICCIÓN ponderada del reporte (sin dependencias de web).

La ablación por arquetipo sobre 678 casos reales (docs/calibracion-por-arquetipo.md)
mostró que las voces CONTRARIAN (quant escéptico, contrarian sabio) aciertan
<50% y DESORIENTAN el consenso. Esta señal baja su peso SOLO para el número que
alimenta la calibración (`senal_media_ponderada`). NO toca el enjambre, ni el
tono de mercado, ni las frases, ni la `senal_media_lideres` histórica (promedio
simple). El optimista NO se baja: la medición lo halló útil.

Reversible con el env ENJAMBRE_PESO_CONTRARIANS (vacío = 0.3; 1.0 = promedio
simple, sin cambio).
"""
import os

ARQUETIPOS_CONTRARIAN_SENAL = frozenset({"quant_esceptico", "contrarian_sabio"})
PESO_DEFECTO = 0.3


def peso_contrarians() -> float:
    try:
        v = os.environ.get("ENJAMBRE_PESO_CONTRARIANS", "")
        return float(v) if v != "" else PESO_DEFECTO
    except ValueError:
        return PESO_DEFECTO


def senal_media_ponderada(lideres, respuestas) -> float:
    """Media de las señales de los líderes bajando el peso de las voces
    contrarian. `lideres[i].arquetipo` empareja con `respuestas[i]["senal"]`."""
    peso = peso_contrarians()
    num = den = 0.0
    for lider, r in zip(lideres, respuestas):
        w = peso if lider.arquetipo in ARQUETIPOS_CONTRARIAN_SENAL else 1.0
        num += r["senal"] * w
        den += w
    return round(num / den, 2) if den else 0.0
