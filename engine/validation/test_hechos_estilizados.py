"""Tests de hechos estilizados — los criterios de realismo de la Etapa 1.

La simulación es creíble solo si reproduce las huellas digitales de un
mercado real (CLAUDE.md sección 7). Si un test falla, se ajustan los
parámetros de la mezcla (sección 4), NUNCA se hardcodea el resultado.
"""

import statistics
from functools import lru_cache

import numpy as np
import pytest

from model import MercadoEnjambre
from validation.hechos_estilizados import asimetria_panico, autocorrelacion, curtosis

SEMILLAS = [42, 3]
TICKS_SESION = 600


@lru_cache(maxsize=None)
def retornos_de_sesion(seed: int) -> tuple:
    """Una sesión de mercado con flujo de noticias aleatorias (día típico)."""
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=TICKS_SESION)
    for _ in range(TICKS_SESION):
        if modelo.random.random() < 0.02:
            modelo.aplicar_noticia(modelo.random.gauss(0, 0.45))
        modelo.step()
    return tuple(modelo.retornos)


@pytest.mark.parametrize("seed", SEMILLAS)
def test_1_colas_gordas(seed):
    """Los extremos ocurren más que en una campana de Gauss (curtosis > 3)."""
    assert curtosis(retornos_de_sesion(seed)) > 3


@pytest.mark.parametrize("seed", SEMILLAS)
def test_2_clustering_de_volatilidad(seed):
    """La turbulencia viene en rachas: la autocorrelación de |retornos|
    es positiva en el corto plazo y decae."""
    absolutos = [abs(r) for r in retornos_de_sesion(seed)]
    ac1 = autocorrelacion(absolutos, 1)
    ac10 = autocorrelacion(absolutos, 10)
    assert ac1 > 0.1
    assert ac1 > ac10  # decae


def test_3_sin_autocorrelacion_de_retornos():
    """No free lunch: el signo del retorno no predice el siguiente.

    Criterio de conjunto: la media entre semillas debe ser ≈ 0 y ninguna
    trayectoria individual puede mostrar predictibilidad fuerte. (Una
    trayectoria puntual de 600 ticks tiene varianza muestral alta.)
    """
    acs = [autocorrelacion(retornos_de_sesion(s), 1) for s in SEMILLAS]
    assert abs(statistics.mean(acs)) < 0.1
    assert max(abs(a) for a in acs) < 0.2


@pytest.mark.parametrize("seed", SEMILLAS)
def test_4_asimetria_de_panico(seed):
    """Las caídas son más rápidas y violentas que las subidas."""
    assert asimetria_panico(retornos_de_sesion(seed)) > 1.0


@pytest.mark.parametrize("seed", SEMILLAS)
def test_5_respuesta_a_shock(seed):
    """Ante una noticia muy negativa el precio cae, sobre-reacciona
    y rebota parcialmente (patrón documentado de sobre-reacción)."""
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=300)
    modelo.correr(80)  # calentamiento: el mercado encuentra su ritmo
    precio_previo = modelo.historial_precios[-1]

    modelo.aplicar_noticia(-0.9)
    modelo.correr(120)

    post = np.array(modelo.historial_precios[80:])
    precio_minimo = post.min()
    precio_final = post[-1]

    assert precio_minimo < precio_previo * 0.95, "debe caer con fuerza (> 5%)"
    assert precio_final > precio_minimo, "debe rebotar desde el mínimo"
    assert precio_final < precio_previo * 0.995, "el rebote es parcial, no total"
