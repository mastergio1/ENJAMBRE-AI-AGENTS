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

# mercado inferido del símbolo medido (mismo mapa que engine/contenido/backtest.py).
# Los casos respaldados no traen "mercado" explícito, pero sí el símbolo real.
_MERCADO_POR_SIMBOLO = {
    "oro": {"GLD", "IAU", "GDX", "NEM", "GOLD"},
    "cripto": {"GBTC", "COIN", "MARA", "RIOT", "MSTR", "ETHE", "BITO", "BTC-USD"},
    "petroleo": {"USO", "XLE", "OXY", "SLB"},
    "indice": {"SPY", "QQQ", "DIA", "IWM"},
}


def _mercado(simbolo: str) -> str:
    s = (simbolo or "").upper()
    for mercado, simbolos in _MERCADO_POR_SIMBOLO.items():
        if s in simbolos:
            return mercado
    return "accion"


def _magnitud(pct_real: float) -> str:
    a = abs(pct_real)
    if a > 1.0:
        return "grande (>1%)"
    if a >= 0.5:
        return "medio (0.5-1%)"
    return "ruido (<0.5%)"


def _cargar_pares(casos: List[dict]) -> List[dict]:
    """De cada caso extrae sim/real + etiquetas (origen, mercado, magnitud,
    sentimiento), descartando incompletos."""
    pares = []
    for c in casos:
        rr = c.get("reaccion_real") or {}
        sim = c.get("direccion_pct")
        real = rr.get("pct_real")
        if sim is None or real is None:
            continue
        pares.append({
            "sim": float(sim), "real": float(real),
            "origen": c.get("origen", "?"),
            "mercado": _mercado(rr.get("simbolo", "")),
            "magnitud": _magnitud(float(real)),
            "sentimiento": rr.get("categoria", "(sin)"),
        })
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

    def _desglose_por(campo: str) -> Dict[str, Dict]:
        grupos = {}
        for valor in sorted({p[campo] for p in pares}):
            grupos[valor] = _puntuar([p for p in pares if p[campo] == valor])
        return grupos

    return {
        "global": _puntuar(pares),
        "por_origen": _desglose_por("origen"),
        "por_mercado": _desglose_por("mercado"),
        "por_magnitud": _desglose_por("magnitud"),
        "por_sentimiento": _desglose_por("sentimiento"),
    }


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


def _tabla(titulo: str, grupos: Dict[str, Dict]) -> None:
    print(f"\n{titulo}")
    filas = [(k, s) for k, s in grupos.items() if s.get("n", 0) >= 3]
    # ordena por acierto de dirección, de mayor a menor
    filas.sort(key=lambda kv: kv[1]["acierto_direccion"], reverse=True)
    for k, s in filas:
        print(f"  {k:<16} n={s['n']:<4} acierto={s['acierto_direccion']*100:5.1f}%  "
              f"corr={s['correlacion']:+.3f}")


def _imprimir_desglose(res: Dict) -> None:
    print("-" * 60)
    _tabla("Por MERCADO:", res["por_mercado"])
    _tabla("Por MAGNITUD del movimiento real:", res["por_magnitud"])
    _tabla("Por SENTIMIENTO de la noticia:", res["por_sentimiento"])
    _tabla("Por ORIGEN:", res["por_origen"])
    print("=" * 60)
    print("Lectura: el enjambre es un FOCUS GROUP sintético — acierta el RUMBO "
          "mejor que el azar; el TAMAÑO del golpe lo estima flojo. No es un "
          "oráculo ni asesoría de inversión.")


if __name__ == "__main__":
    resultado = validar()
    _imprimir(resultado)
    if "--desglose" in sys.argv:
        _imprimir_desglose(resultado)
    else:
        print("=" * 60)
        print("(usa --desglose para ver por mercado, magnitud y sentimiento)")
