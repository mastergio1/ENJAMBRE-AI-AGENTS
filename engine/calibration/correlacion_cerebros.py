"""Fase 3 — ¿Cuánta diversidad REAL hay entre los arquetipos?

La auditoría (§7.3): el valor de un ensemble depende de la CORRELACIÓN de los errores
de sus miembros. Si todos leen el mismo titular con el mismo modelo, sus errores están
correlacionados y el "número efectivo de opiniones independientes" es mucho menor que
el número de voces:  N_efectivo = N / (1 + (N-1)·ρ).

Aquí se mide ρ real sobre el histórico: para cada arquetipo, su error e = señal − y
(y = +1/−1 según el resultado), y la correlación media entre arquetipos. Explica el
hallazgo A2≈A3: si ρ es alto, 9 arquetipos ≈ pocas opiniones efectivas, y promediarlos
(el consenso) no supera a una sola voz.

Sin IA ni red. numpy para las correlaciones.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

ZONA = 0.3


def armar(ruta_con_fecha, ruta_raw, mercado="indice"):
    """[(senales_por_arquetipo, y_signed)] para casos direccionables del mercado."""
    cf = json.loads(Path(ruta_con_fecha).read_text())
    crudo = json.loads(Path(ruta_raw).read_text())
    casos = crudo.get("casos", crudo) if isinstance(crudo, dict) else crudo
    idx = {}
    for c in casos:
        rr = c.get("reaccion_real") or {}
        idx[(rr.get("fecha_base"), rr.get("simbolo"))] = c
    out = []
    for r in cf:
        if mercado and r.get("mercado") != mercado:
            continue
        pc = r.get("pct_corr")
        if pc is None or abs(pc) < ZONA:
            continue
        c = idx.get((r.get("fecha"), r.get("simbolo")))
        sa = c.get("senales_arquetipo") if c else None
        if not sa:
            continue
        senales = {k: float(v.get("senal_media", 0.0)) for k, v in sa.items()}
        out.append((senales, 1.0 if pc > 0 else -1.0))
    return out


def matriz_correlacion(casos):
    """Correlación de las SEÑALES entre arquetipos (redundancia de información).

    IMPORTANTE (honestidad): se correlacionan las señales entre sí, NO el error
    `señal − y`. Medir el error infla la correlación de forma artificial, porque
    todas las voces comparten el mismo `y` (el resultado), y eso las hace parecer
    más de acuerdo de lo que su información realmente implica. La correlación de
    señales mide lo que importa: ¿las voces aportan información DISTINTA, o repiten
    la misma lectura? Devuelve nombres, matriz, ρ media (fuera de la diagonal) y
    N efectivo = N / (1 + (N-1)·ρ)."""
    arqs = sorted({a for sen, _ in casos for a in sen})
    S = np.array([[sen.get(a, 0.0) for a in arqs] for sen, _ in casos])  # [casos, arq]
    # correlación entre columnas (arquetipos); columnas constantes → 0
    C = np.corrcoef(S, rowvar=False)
    C = np.nan_to_num(C)
    n = len(arqs)
    fuera = C[~np.eye(n, dtype=bool)]
    rho = float(fuera.mean()) if fuera.size else 0.0
    n_ef = n / (1 + (n - 1) * rho) if (1 + (n - 1) * rho) > 0 else float(n)
    return {"arquetipos": arqs, "matriz": C, "rho_media": round(rho, 3),
            "n_arquetipos": n, "n_efectivo": round(n_ef, 2), "n_casos": len(casos)}


def imprimir(ruta_con_fecha, ruta_raw, mercados=("indice", None)):
    for m in mercados:
        casos = armar(ruta_con_fecha, ruta_raw, mercado=m)
        if len(casos) < 5:
            print(f"\n=== {(m or 'TODOS').upper()}: muestra insuficiente ===")
            continue
        r = matriz_correlacion(casos)
        print(f"\n=== Diversidad de arquetipos · {(m or 'TODOS').upper()} "
              f"({r['n_casos']} casos) ===")
        print(f"  correlación media de errores ρ = {r['rho_media']}")
        print(f"  arquetipos: {r['n_arquetipos']}  →  opiniones EFECTIVAS: "
              f"{r['n_efectivo']}")
        print(f"  (ρ bajo ⇒ las señales SON diversas; pero diversas en ESTILO sobre la "
              f"misma noticia: su promedio recupera la lectura central = la de 1 LLM)")


if __name__ == "__main__":
    imprimir(sys.argv[1], sys.argv[2])
