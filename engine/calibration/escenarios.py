"""Banco de escenarios de estrés — reproducibles, SIN IA (sentimiento numérico).

Para medir el comportamiento del enjambre por régimen y comparar configuraciones
(con/sin `overrides`) de forma justa, usando `aplicar_noticia` (número), que no
llama a la API. No imponen que el precio suba o baje de cierta forma: sirven para
observar la dinámica y detectar comportamientos patológicos o cambios al calibrar.

Uso:
    from calibration.escenarios import correr_todos, correr_escenario, variabilidad
    print(correr_todos(seed=42))
    print(correr_escenario("cinco_negativas", seed=42, overrides={...}))
    print(variabilidad("negativa_fuerte", seeds=[1,7,42,99]))
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model import MercadoEnjambre

# cada escenario: lista de (tick tras el calentamiento, sentimiento de la noticia)
ESCENARIOS = {
    "negativa_fuerte":  [(0, -0.9)],
    "positiva_fuerte":  [(0, 0.9)],
    "negativa_leve":    [(0, -0.3)],
    "cinco_negativas":  [(0, -0.4), (10, -0.4), (20, -0.4), (30, -0.4), (40, -0.4)],
    "neutral":          [(0, 0.0)],
    "pos_luego_neg":    [(0, 0.6), (30, -0.8)],
    "crash_profundo":   [(0, -0.95)],
}


def correr_escenario(nombre: str, seed: int = 42, overrides: dict | None = None,
                     calienta: int = 60, post: int = 120,
                     instrumentar: bool = False) -> dict:
    """Corre un escenario y devuelve métricas observables (relativas al precio al
    terminar el calentamiento, justo antes de la primera noticia)."""
    if nombre not in ESCENARIOS:
        raise ValueError(f"escenario desconocido: {nombre}. Opciones: {sorted(ESCENARIOS)}")
    eventos = ESCENARIOS[nombre]
    m = MercadoEnjambre(seed=seed, ticks_horizonte=calienta + post + 10, overrides=overrides)
    if instrumentar:
        m.activar_instrumentacion()
    for _ in range(calienta):
        m.step()
    base = m.historial_precios[-1]
    plan = dict(eventos)
    for t in range(post):
        if t in plan:
            m.aplicar_noticia(plan[t])
        m.step()
    precios = m.historial_precios[-post:]
    retornos = m.retornos[-post:]
    media = sum(retornos) / len(retornos)
    vol = (sum((r - media) ** 2 for r in retornos) / len(retornos)) ** 0.5
    res = {
        "escenario": nombre,
        "seed": seed,
        "direccion_pct": round((precios[-1] / base - 1) * 100, 2),
        "minimo_pct": round((min(precios) / base - 1) * 100, 2),
        "maximo_pct": round((max(precios) / base - 1) * 100, 2),
        "volatilidad_pct": round(vol * 100, 2),
    }
    if instrumentar:
        res["instrumentacion"] = m.resumen_instrumentacion()
    return res


def correr_todos(seed: int = 42, overrides: dict | None = None) -> dict:
    return {n: correr_escenario(n, seed=seed, overrides=overrides) for n in ESCENARIOS}


def variabilidad(nombre: str, seeds=(1, 7, 42, 99), overrides: dict | None = None) -> dict:
    """Corre el mismo escenario en varias semillas y reporta la dispersión de la
    dirección final — para saber cuánto depende el resultado del azar."""
    dirs = [correr_escenario(nombre, seed=s, overrides=overrides)["direccion_pct"]
            for s in seeds]
    media = sum(dirs) / len(dirs)
    desv = (sum((d - media) ** 2 for d in dirs) / len(dirs)) ** 0.5
    return {"escenario": nombre, "direcciones": dirs,
            "media": round(media, 2), "desv": round(desv, 2),
            "rango": [min(dirs), max(dirs)]}


if __name__ == "__main__":
    import json
    print(json.dumps(correr_todos(), ensure_ascii=False, indent=1))
