"""L7 — Evaluación estadística pareada y gate de decisión (I.9).

Consume pronósticos sellados + outcomes maduros y decide el veredicto. La diferencia
primaria es `Δ = mean(loss_P4 − loss_P5)` por sesión (una SPY por día); se compara
también P5 contra B* (mejor no-ABM preseleccionado). El gate exige
`lower95(Δ_P4) > 0.005` **y** `lower95(Δ_B*) > 0.005` (gate de intersección).

IC95 por moving-block bootstrap de sesiones consecutivas: bloques de 5 (sensibilidad
10), 10.000 remuestreos, seed 20261124. No se puentean huecos por fallos. Las
abstenciones SÍ entran en el Brier (abstención solo controla trading). Sin IA.

Correcciones de auditoría: usa probabilidades SELLADAS (F05/F06), agrupa por sesión/
evento explícito (F07), diferencias pareadas verdaderas (F06), cobertura y fallos
explícitos. No usa la prevalencia del test como benchmark.
"""
from __future__ import annotations

import random
from dataclasses import dataclass


def _brier_loss(p: float, y: float) -> float:
    return (p - y) ** 2


def _por_sesion(registros: list[dict]) -> dict:
    """Agrupa por sesión de emisión (`emision`/`session_id`). Una SPY por día: si
    hubiera más de una fila por sesión/modelo, se promedia (no debería ocurrir con el
    contrato de máximo una fila primaria por sesión)."""
    out: dict = {}
    for r in registros:
        s = r.get("session_id") or r.get("emision") or r.get("event_id")
        out.setdefault(s, {}).setdefault(r["model_id"], []).append(r)
    return out


@dataclass
class Conteos:
    n_sesiones: int
    n_mature: int
    n_paired: int
    cobertura: float | None
    fallos_por_modelo: dict


def _emparejar(registros: list[dict], modelo_a: str, modelo_b: str):
    """Pares (sesión con ambos modelos resueltos). Devuelve listas alineadas por
    sesión ordenada: sesiones, dA (loss_a-loss_b por sesión), conteos."""
    pors = _por_sesion(registros)
    sesiones = sorted(pors.keys())
    d = []
    usadas = []
    n_mature = 0
    fallos = {modelo_a: 0, modelo_b: 0}
    for s in sesiones:
        grupo = pors[s]
        # outcome maduro: cualquier fila de la sesión con y no None
        ys = [r.get("y") for r in sum(grupo.values(), []) if r.get("y") is not None]
        if not ys:
            continue
        n_mature += 1
        y = ys[0]
        ra = grupo.get(modelo_a); rb = grupo.get(modelo_b)
        if not ra:
            fallos[modelo_a] += 1
        if not rb:
            fallos[modelo_b] += 1
        if not ra or not rb:
            continue
        pa = sum(float(x["p_up"]) for x in ra) / len(ra)
        pb = sum(float(x["p_up"]) for x in rb) / len(rb)
        d.append(_brier_loss(pa, y) - _brier_loss(pb, y))
        usadas.append(s)
    cobertura = (len(d) / n_mature) if n_mature else None
    return usadas, d, Conteos(len(sesiones), n_mature, len(d), cobertura, fallos)


def moving_block_bootstrap(d: list[float], block: int = 5, resamples: int = 10000,
                           seed: int = 20261124) -> dict:
    """IC95 bilateral de la media por moving-block bootstrap (bloques consecutivos).

    Reconstruye series de longitud ~n concatenando bloques de longitud `block`
    tomados al azar (con reemplazo) de las posiciones [0, n-block]. No puentea huecos:
    los bloques respetan el orden real de las sesiones provistas.
    """
    n = len(d)
    if n == 0:
        return {"media": None, "lo": None, "hi": None, "n": 0}
    if n < block:
        block = n
    rng = random.Random(seed)
    n_bloques = (n + block - 1) // block
    inicios_max = n - block
    medias = []
    for _ in range(resamples):
        serie = []
        for _ in range(n_bloques):
            ini = rng.randint(0, inicios_max) if inicios_max > 0 else 0
            serie.extend(d[ini:ini + block])
        serie = serie[:n]
        medias.append(sum(serie) / len(serie))
    medias.sort()
    lo = medias[int(0.025 * resamples)]
    hi = medias[min(int(0.975 * resamples), resamples - 1)]
    return {"media": sum(d) / n, "lo": lo, "hi": hi, "n": n}


def _veredicto_una(ic: dict, delta_min: float) -> str:
    """Lectura de un IC de mejora (Δ = loss_comparador − loss_P5; >0 favorece P5)."""
    if ic["media"] is None:
        return "sin_datos"
    lo, hi = ic["lo"], ic["hi"]
    if lo > delta_min:
        return "supera"                 # mejora relevante significativa
    if hi < 0:
        return "inferior"               # P5 es peor
    if hi < delta_min:
        return "sin_mejora_relevante"   # mejor pero por debajo del umbral
    return "inconcluso"                 # IC ancho


def brier_por_modelo(registros: list[dict]) -> dict:
    """Brier global por modelo (todas las sesiones maduras, incluidas abstenciones)."""
    pors = _por_sesion(registros)
    acc: dict = {}
    for s, grupo in pors.items():
        ys = [r.get("y") for r in sum(grupo.values(), []) if r.get("y") is not None]
        if not ys:
            continue
        y = ys[0]
        for mid, filas in grupo.items():
            p = sum(float(x["p_up"]) for x in filas) / len(filas)
            acc.setdefault(mid, []).append(_brier_loss(p, y))
    return {mid: (sum(v) / len(v)) for mid, v in acc.items() if v}


def evaluar(registros: list[dict], b_star: str, *, delta_min: float = 0.005,
            block: int = 5, block_sensibilidad: int = 10,
            resamples: int = 10000, seed: int = 20261124,
            min_sesiones: int = 100, min_cobertura: float = 0.90) -> dict:
    """Evaluación completa y gate estadístico (I.9). `registros`: filas con
    {model_id, p_up, y (resuelto o None), session_id/emision}."""
    comparadores = ["P4"]
    if b_star and b_star != "P4":
        comparadores.append(b_star)

    res_cmp = {}
    for cmp in comparadores:
        _, d, conteos = _emparejar(registros, cmp, "P5")
        ic = moving_block_bootstrap(d, block, resamples, seed)
        ic_sens = moving_block_bootstrap(d, block_sensibilidad, resamples, seed)
        res_cmp[cmp] = {
            "ic": ic, "ic_sensibilidad": ic_sens,
            "conteos": conteos.__dict__,
            "veredicto": _veredicto_una(ic, delta_min),
            "veredicto_sensibilidad": _veredicto_una(ic_sens, delta_min),
        }

    # gate: todos los comparadores deben superar, y no contradecirse con bloque 10
    pasa = all(res_cmp[c]["veredicto"] == "supera"
               and res_cmp[c]["veredicto_sensibilidad"] != "inferior"
               for c in comparadores)

    # requisitos de muestra/cobertura (gate previo)
    cob_p4 = res_cmp["P4"]["conteos"]["cobertura"]
    n_paired_p4 = res_cmp["P4"]["conteos"]["n_paired"]
    muestra_ok = (n_paired_p4 >= min_sesiones
                  and cob_p4 is not None and cob_p4 >= min_cobertura)

    return {
        "comparadores": comparadores,
        "brier_por_modelo": brier_por_modelo(registros),
        "resultados": res_cmp,
        "muestra_suficiente": muestra_ok,
        "n_paired": n_paired_p4,
        "cobertura": cob_p4,
        "gate_estadistico": bool(pasa and muestra_ok),
        "delta_min": delta_min,
    }
