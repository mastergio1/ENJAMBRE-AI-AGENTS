"""Métricas de hechos estilizados — las huellas digitales de un mercado real."""

import numpy as np
from scipy import stats


def curtosis(retornos) -> float:
    """Curtosis de Pearson (una normal da 3; un mercado real da más)."""
    return float(stats.kurtosis(retornos, fisher=False))


def autocorrelacion(serie, rezago: int) -> float:
    """Autocorrelación de una serie en un rezago dado."""
    x = np.asarray(serie, dtype=float)
    if len(x) <= rezago + 1:
        return 0.0
    x = x - x.mean()
    denominador = float(np.dot(x, x))
    if denominador == 0:
        return 0.0
    return float(np.dot(x[:-rezago], x[rezago:]) / denominador)


def asimetria_panico(retornos) -> float:
    """Razón entre la violencia de las caídas y la de las subidas.

    Compara el promedio del 2.5% de peores retornos (en valor absoluto)
    contra el promedio del 2.5% de mejores. > 1 significa que las caídas
    son más violentas que las subidas.
    """
    r = np.asarray(retornos, dtype=float)
    peores = np.abs(r[r <= np.quantile(r, 0.025)])
    mejores = r[r >= np.quantile(r, 0.975)]
    if len(mejores) == 0 or mejores.mean() <= 0:
        return float("inf")
    return float(peores.mean() / mejores.mean())
