"""Adaptadores de recuperación de evidencia (Fase 1).

Fuente REAL y point-in-time: el contexto de PRECIO previo a la noticia (Yahoo,
gratis). Responde "¿cómo venía el activo ANTES del evento?" — retorno reciente,
volatilidad y distancia al máximo. La regla sagrada se respeta por construcción:
solo se usan barras ANTERIORES al día del `as_of` (nada del evento ni posterior).

Otras fuentes (calendario macro CPI/FOMC, consenso, noticias oficiales) necesitan
llaves que viven en Render y, en el caso macro, las construye Codex (PR #34) — se
enchufan después con la misma interfaz, sin duplicar.
"""
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration.remedir_sin_fuga import obtener_barras


def _ret(cierres, n):
    if len(cierres) > n and cierres[-1 - n]:
        return (cierres[-1] / cierres[-1 - n] - 1) * 100
    return None


def contexto_precio(simbolo, as_of, fetch=obtener_barras):
    """Hechos de contexto de precio DISPONIBLES antes del evento (point-in-time).

    Devuelve (hechos, fuente) o (None, None) si no hay datos suficientes. `fetch`
    es inyectable para tests. Solo usa barras con día < día del `as_of`."""
    as_of_fecha = as_of[:10]
    barras = fetch(simbolo, as_of_fecha)
    if not barras:
        return None, None
    previas = [(d, c) for d, c in barras if d < as_of_fecha and c]  # SOLO antes del evento
    if len(previas) < 6:
        return None, None
    cierres = [c for _, c in previas]
    hechos = []

    r5, r20 = _ret(cierres, 5), _ret(cierres, 20)
    if r5 is not None:
        hechos.append({"clave": "ret_5", "valor": round(r5, 2),
                       "texto": f"retorno previo 5 sesiones: {r5:+.1f}%"})
    if r20 is not None:
        hechos.append({"clave": "ret_20", "valor": round(r20, 2),
                       "texto": f"retorno previo 20 sesiones: {r20:+.1f}%"})

    rets = [(cierres[i] / cierres[i - 1] - 1) * 100
            for i in range(1, len(cierres)) if cierres[i - 1]]
    if len(rets) >= 5:
        vol = statistics.pstdev(rets[-20:])
        hechos.append({"clave": "vol", "valor": round(vol, 3),
                       "texto": f"volatilidad diaria reciente: {vol:.2f}%"})

    ventana = cierres[-20:]
    if ventana and max(ventana):
        dist = (cierres[-1] / max(ventana) - 1) * 100
        hechos.append({"clave": "dist_max20", "valor": round(dist, 2),
                       "texto": f"a {dist:+.1f}% del máximo de 20 sesiones"})

    ultima = previas[-1][0]  # día < as_of → published_at nunca es futuro
    fuente = {"source_id": f"precio:{simbolo}",
              "published_at": f"{ultima}T23:59:59+00:00",
              "reliability": "alta", "supports": [h["clave"] for h in hechos]}
    return hechos, fuente
