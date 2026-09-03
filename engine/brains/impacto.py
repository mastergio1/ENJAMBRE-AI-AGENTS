"""Impacto no lineal: señal agregada → fuerza del shock.

El precio SIGUE emergiendo del libro de órdenes. Esta función no lo
fija. Solo transforma la señal (tono de la noticia / señal del líder)
para que un shock grande mueve más que uno chico, con umbral de pánico
y asimetría a la baja.

Conjunto 'baseline' (perillas identidad): calcular_impacto(s) == s y
zona_muerta(s) == s. Así esta rama no cambia el enjambre hasta que se
active una hipótesis.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

RUTA_PERILLAS = Path(__file__).resolve().parent.parent / "config" / "perillas_calibracion.json"

# claves que un perfil de mercado puede sobreescribir
_PERILLAS_IMPACTO = (
    "impacto_base",
    "umbral_panico",
    "amplificacion_panico",
    "asimetria_downside",
    "ganancia_contagio",
    "factor_shock_max",
    "volatilidad_base",
    "umbral_consenso",
)


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


@lru_cache(maxsize=1)
def _leer_json() -> dict:
    with open(RUTA_PERILLAS, encoding="utf-8") as f:
        return json.load(f)


def cargar_perillas(conjunto: str | None = None) -> dict:
    """Lee config/perillas_calibracion.json y resuelve el conjunto activo.

    `conjunto` gana a ENJAMBRE_PERILLAS, que gana a conjunto_activo del JSON.
    El archivo se cachea; el nombre del conjunto se resuelve en cada llamada
    para que cambiar la env surta efecto sin reiniciar el proceso.
    """
    crudo = _leer_json()
    nombre = conjunto or os.environ.get("ENJAMBRE_PERILLAS") or crudo.get("conjunto_activo") or "baseline"
    base = dict(crudo.get("globales") or {})
    sets = crudo.get("conjuntos") or {}
    elegido = sets.get(nombre) or sets.get("baseline") or {}
    base.update(elegido.get("globales") or {})
    return {
        "nombre": nombre,
        "version": crudo.get("version", "perillas_v1"),
        "globales": base,
        "por_mercado": dict(elegido.get("por_mercado") or {}),
        "nota": elegido.get("nota", ""),
    }


def reiniciar_cache() -> None:
    """Para tests: si cambió el JSON, vuelve a leerlo."""
    _leer_json.cache_clear()


def knobs_de(perfil: dict | None = None, conjunto: str | None = None) -> dict:
    """Perillas efectivas: globales del conjunto + override del tipo de mercado."""
    cfg = cargar_perillas(conjunto)
    knobs = dict(cfg["globales"])
    tipo = (perfil or {}).get("tipo")
    if tipo and tipo in cfg["por_mercado"]:
        knobs.update(cfg["por_mercado"][tipo])
    # el perfil puede traer las perillas ya fusionadas (tests / experimentos)
    for clave in _PERILLAS_IMPACTO:
        if perfil and clave in perfil and perfil[clave] is not None:
            knobs[clave] = perfil[clave]
    return knobs


def overlay_perfil(perfil: dict | None = None) -> dict:
    """Copia del perfil con volatilidad_base del conjunto, si está definida.

    Si el conjunto no declara volatilidad_base, el perfil queda igual
    (los diales de brains/mercado.py mandan).
    """
    perfil = dict(perfil or {})
    vb = knobs_de(perfil).get("volatilidad_base")
    if vb is not None:
        perfil["volatilidad"] = float(vb)
    return perfil


def calcular_impacto(senal_agregada: float, perfil: dict | None = None) -> float:
    """Señal amplificada, SIN recortar a [-1, +1].

    senal_agregada ∈ ℝ (en la práctica [-1, +1]).
    Devuelve la señal con umbral de pánico y asimetría a la baja.
    El recorte a [-1, +1] es responsabilidad de quien alimenta el sentimiento.
    """
    knobs = knobs_de(perfil)
    k = float(knobs.get("impacto_base", 1.0))
    umbral = float(knobs.get("umbral_panico", 1.01))
    amp = float(knobs.get("amplificacion_panico", 2.0))
    asim = float(knobs.get("asimetria_downside", 1.0))

    magnitud = abs(senal_agregada)
    signo = 1.0 if senal_agregada >= 0 else -1.0

    impacto = k * senal_agregada
    if magnitud >= umbral:
        extra = (magnitud - umbral) ** 1.3 * amp
        impacto += signo * extra
    if senal_agregada < 0:
        impacto *= asim
    return impacto


def transformar_senal(senal_agregada: float, perfil: dict | None = None) -> float:
    """Versión recortada a [-1, +1] para el sentimiento del modelo."""
    return _clip(calcular_impacto(senal_agregada, perfil))


def factor_shock(senal_agregada: float, perfil: dict | None = None) -> float:
    """Cuántas veces más fuerte que la señal lineal. Siempre ≥ 0, tope de seguridad."""
    knobs = knobs_de(perfil)
    tope = float(knobs.get("factor_shock_max", 3.0))
    if abs(senal_agregada) < 1e-9:
        return 1.0
    cruda = calcular_impacto(senal_agregada, perfil)
    return max(0.0, min(tope, abs(cruda) / abs(senal_agregada)))


def factor_residual(senal_agregada: float, perfil: dict | None = None) -> float:
    """Lo que el recorte a [-1, +1] se comió: 1.0 si no recortó, >1 si sí.

    Así un shock enorme (el enjambre se quedaba en 3-5% cuando la realidad
    hacía 8-12%) todavía puede empujar órdenes y contagio sin romper el
    sentimiento, que sigue ∈ [-1, +1].
    """
    knobs = knobs_de(perfil)
    tope = float(knobs.get("factor_shock_max", 3.0))
    cruda = calcular_impacto(senal_agregada, perfil)
    recortada = _clip(cruda)
    if abs(recortada) < 1e-9:
        return 1.0
    return max(1.0, min(tope, abs(cruda) / abs(recortada)))


def zona_muerta(senal: float, perfil: dict | None = None) -> float:
    """Soft-threshold del consenso ambiente. Identidad si umbral_consenso ≤ 0.

    Si |señal| ≤ umbral → 0 (el mercado no siente un titular tibio).
    Si |señal| > umbral → se le resta el umbral (lasso / James-Stein suave).

    Solo debe aplicarse al TONO AMBIENTE (lo que sienten todos por leer el
    mismo titular). Los líderes siguen hablando por la red: esa es la
    hipótesis v1c, anti-v1a.
    """
    umbral = float(knobs_de(perfil).get("umbral_consenso", 0.0))
    if umbral <= 0:
        return senal
    magnitud = abs(senal)
    if magnitud <= umbral:
        return 0.0
    signo = 1.0 if senal >= 0 else -1.0
    return signo * (magnitud - umbral)


def ganancia_contagio(perfil: dict | None = None) -> float:
    return float(knobs_de(perfil).get("ganancia_contagio", 0.7))


def ganancia_consenso() -> float:
    return float(cargar_perillas()["globales"].get("ganancia_consenso", 0.8))


def ruido_lider_sigma() -> float:
    return float(cargar_perillas()["globales"].get("ruido_lider_sigma", 0.0))


def prompt_microfono() -> bool:
    """¿Los cerebros llevan las reglas sorpresa / priced-in / earnings?

    False en baseline (el prompt de producción no cambia).
    True en hipotesis_v1d / v1e. Cambia la clave de caché para no
    reciclar voces viejas.
    """
    v = cargar_perillas()["globales"].get("prompt_microfono", False)
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "si", "sí", "on")
    return bool(v)


def pesos_cerebro() -> dict[str, float]:
    g = cargar_perillas()["globales"]
    return {
        "fomo_evangelista": float(g.get("peso_cerebro_fomo_evangelista", 1.0)),
        "influencer_optimista": float(g.get("peso_cerebro_influencer_optimista", 1.0)),
    }
