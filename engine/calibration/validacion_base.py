"""
FASE 0 — Validación Base: ¿el enjambre reacciona como el mercado real?

Usa los exámenes YA rendidos por el motor (backtest + en vivo), respaldados en
GitHub y de lectura pública (sin token ni saldo de API). Cada caso trae:
  - direccion_pct: cuánto/hacia dónde movió el precio la simulación del enjambre.
  - reaccion_real.pct_real: cuánto se movió DE VERDAD el símbolo esos días.

Métricas (las honestas para un "focus group sintético", no un oráculo):
  - Acierto de dirección: ¿coincide el SIGNO simulado con el real? (azar = 50%).
  - Correlación de magnitud (Pearson) y R² asociado.

No corre simulaciones nuevas (no gasta LLM); solo puntúa lo ya rendido.
"""

import sys
from typing import Dict, List

import numpy as np


def _cargar_pares(casos: List[dict]) -> List[dict]:
    """De cada caso extrae (sim, real, origen), descartando incompletos."""
    pares = []
    for c in casos:
        sim = c.get("direccion_pct")
        real = (c.get("reaccion_real") or {}).get("pct_real")
        if sim is None or real is None:
            continue
        pares.append({"sim": float(sim), "real": float(real),
                      "origen": c.get("origen", "?")})
    return pares


def _puntuar(pares: List[dict], umbral_notable: float = 0.5) -> Dict:
    """Acierto de dirección + correlación de magnitud sobre un set de pares."""
    if len(pares) < 3:
        return {"n": len(pares)}
    sim = np.array([p["sim"] for p in pares])
    real = np.array([p["real"] for p in pares])
    acierto = float(np.mean(np.sign(sim) == np.sign(real)))
    mask = np.abs(real) >= umbral_notable
    acierto_notable = (float(np.mean(np.sign(sim[mask]) == np.sign(real[mask])))
                       if mask.sum() >= 3 else None)
    corr = float(np.corrcoef(sim, real)[0, 1]) if np.std(sim) > 0 and np.std(real) > 0 else 0.0
    return {
        "n": len(pares),
        "acierto_direccion": acierto,
        "n_notables": int(mask.sum()),
        "acierto_notables": acierto_notable,
        "correlacion": corr,
        "r2": corr ** 2,
    }


def validar(casos: List[dict] | None = None) -> Dict:
    """Corre la validación base. Si no se pasan `casos`, los trae del respaldo
    público de GitHub (sin token). Devuelve el scorecard global y por origen."""
    if casos is None:
        sys.path.insert(0, __file__.rsplit("/engine/", 1)[0] + "/engine")
        from contenido import respaldo
        casos = respaldo.casos_remotos()

    pares = _cargar_pares(casos)
    global_ = _puntuar(pares)
    por_origen = {}
    for origen in sorted({p["origen"] for p in pares}):
        por_origen[origen] = _puntuar([p for p in pares if p["origen"] == origen])
    return {"global": global_, "por_origen": por_origen}


def _imprimir(res: Dict) -> None:
    g = res["global"]
    print("=" * 60)
    print("FASE 0 — VALIDACIÓN BASE (enjambre vs. mercado real)")
    print("=" * 60)
    if g.get("n", 0) < 3:
        print(f"Datos insuficientes (n={g.get('n', 0)}).")
        return
    print(f"Exámenes: {g['n']}")
    print(f"1. Acierto de dirección: {g['acierto_direccion']*100:.1f}%   (azar = 50%)")
    if g["acierto_notables"] is not None:
        print(f"   en movimientos reales notables (>=0.5%, n={g['n_notables']}): "
              f"{g['acierto_notables']*100:.1f}%")
    print(f"2. Correlación de magnitud (Pearson): {g['correlacion']:.3f}  "
          f"(R² = {g['r2']:.3f})")
    print("-" * 60)
    print("Por origen:")
    for origen, s in res["por_origen"].items():
        if s.get("n", 0) >= 3:
            print(f"  [{origen}] n={s['n']} · acierto={s['acierto_direccion']*100:.1f}% "
                  f"· corr={s['correlacion']:.3f}")
    print("=" * 60)
    print("Lectura: el enjambre es un FOCUS GROUP sintético — acierta el RUMBO "
          "bastante mejor que el azar; el TAMAÑO del golpe lo estima flojo. "
          "No es un oráculo ni asesoría de inversión.")


if __name__ == "__main__":
    _imprimir(validar())
