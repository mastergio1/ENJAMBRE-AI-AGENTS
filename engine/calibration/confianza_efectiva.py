"""Fase 2 — ¿Reponderar por acierto histórico mejora la DIRECCIÓN? (resultado: no)

Prueba fuera de muestra la "confianza efectiva" que proponía la auditoría: en vez
de ponderar el consenso por la confianza que DECLARA cada LLM, ponderar por el
acierto HISTÓRICO de cada arquetipo. Se estima el peso en TRAIN (casos viejos) y
se evalúa en TEST (casos nuevos), comparando contra la ponderada actual y el
promedio simple.

Hallazgo (índice, 2026-11-18): las tres formas dan el MISMO acierto direccional,
porque el SIGNO del agregado lo fija la mayoría y no se voltea al reponderar
(0/37 casos cambian de signo, aun quitando al doomer). Para la DIRECCIÓN, el
esquema de agregación es irrelevante; el lastre está en los insumos, no en los
pesos. (Podría importar para la CALIBRACIÓN de probabilidad / Brier, no medido
aquí.) Núcleo puro y testeable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration.remedir_sin_fuga import _sg

CONTRARIANS = {"quant_esceptico", "contrarian_sabio"}


def _dire(casos, zona=0.3):
    return [c for c in casos if abs(c["pc"]) >= zona]


def pesos_historicos(train, arqs, zona=0.3):
    """Peso por arquetipo = max(0, acierto_train - 0.5): premia solo a los que
    superan el azar en la dirección (el doomer, bajo 50%, queda en 0)."""
    pesos = {}
    for a in arqs:
        ok = n = 0
        for c in _dire(train, zona):
            s = c["sen"].get(a, 0)
            if s != 0:
                n += 1
                ok += (_sg(s) == _sg(c["pc"]))
        acc = ok / n if n else 0.5
        pesos[a] = max(0.0, acc - 0.5)
    return pesos


def _consenso(caso, pesos):
    num = den = 0.0
    for a, s in caso["sen"].items():
        w = pesos.get(a, 0)
        num += s * w
        den += w
    return num / den if den else 0.0


def pond_actual(caso):
    """La ponderada de producción: contrarians ×0.3, el resto ×1."""
    num = den = 0.0
    for a, s in caso["sen"].items():
        w = 0.3 if a in CONTRARIANS else 1.0
        num += s * w
        den += w
    return num / den if den else 0.0


def flat(caso):
    v = list(caso["sen"].values())
    return sum(v) / len(v) if v else 0.0


def acierto(casos, fn, zona=0.3):
    d = _dire(casos, zona)
    if not d:
        return (None, 0)
    ok = sum(1 for c in d if _sg(fn(c)) == _sg(c["pc"]))
    return (round(100 * ok / len(d), 1), len(d))


def comparar(train, test, arqs, zona=0.3):
    """Compara en TEST: flat vs ponderada actual vs efectiva (peso histórico de
    TRAIN). Devuelve acierto de cada una y en cuántos casos la efectiva cambia el
    signo respecto de la ponderada."""
    w = pesos_historicos(train, arqs, zona)
    d = _dire(test, zona)
    cambios = sum(1 for c in d if _sg(_consenso(c, w)) != _sg(pond_actual(c)))
    return {
        "n_test_dir": len(d),
        "flat": acierto(test, flat, zona),
        "ponderada_actual": acierto(test, pond_actual, zona),
        "efectiva": acierto(test, lambda c: _consenso(c, w), zona),
        "cambios_de_signo": cambios,
        "pesos": {a: round(w[a], 3) for a in arqs},
    }
