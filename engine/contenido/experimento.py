"""Experimentos de calibración — baratos, versionados, sin gastar la API.

Una sesión = una hipótesis (cambiar 1-2 perillas). Corre shocks numéricos
sobre el enjambre (aplicar_noticia, sin LLM) y mide magnitud + dirección.
La Loss oficial contra el mercado REAL vive en corrector.evaluar_casos;
este script alimenta la caja de experimentos con seed + perillas + métricas.

Uso (desde engine/):

    python -m contenido.experimento --set baseline --n 6
    python -m contenido.experimento --set hipotesis_v1a --n 6
    python -m contenido.experimento --set baseline --vs hipotesis_v1a --n 2

No toca producción: el conjunto se elige por bandera / env, no reescribe
el JSON. Los resultados se imprimen y, si se pide --guardar, van a
engine/config/experimentos/.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from brains import impacto
from contenido.corrector import evaluar_casos

RUTA_EXPERIMENTOS = Path(__file__).resolve().parent.parent / "config" / "experimentos"

# shocks de calibración: mezcla 70% normales + 30% extremos (regla de oro)
SHOCKS = (
    -0.25, 0.20, -0.35, 0.40,   # días normales
    -0.90, 0.85,                # extremos
)


def _correr_shock(seed: int, shock: float, ticks_calentamiento: int = 40,
                  ticks_reaccion: int = 120) -> dict:
    """Una corrida numérica. Import tardío para no cargar Mesa al testear la Loss."""
    from model import MercadoEnjambre

    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=ticks_calentamiento + ticks_reaccion)
    modelo.correr(ticks_calentamiento)
    base = modelo.historial_precios[-1]
    modelo.aplicar_noticia(shock)
    modelo.correr(ticks_reaccion)
    final = modelo.historial_precios[-1]
    minimo = min(modelo.historial_precios[ticks_calentamiento:])
    maximo = max(modelo.historial_precios[ticks_calentamiento:])
    pct = (final - base) / base * 100
    return {
        "seed": seed,
        "shock": shock,
        "pct": round(pct, 4),
        "min_pct": round((minimo - base) / base * 100, 4),
        "max_pct": round((maximo - base) / base * 100, 4),
        "direccion_ok": (pct < 0) == (shock < 0) if abs(pct) >= 0.05 and abs(shock) >= 0.05 else None,
    }


def resumir_corridas(corridas: list[dict]) -> dict:
    """Métricas de un set de shocks numéricos (sin mercado real)."""
    pcts = [c["pct"] for c in corridas]
    extremos = [c for c in corridas if abs(c["shock"]) >= 0.8]
    normales = [c for c in corridas if abs(c["shock"]) < 0.8]
    dirs = [c["direccion_ok"] for c in corridas if c["direccion_ok"] is not None]
    mag_ext = [abs(c["pct"]) for c in extremos]
    mag_nor = [abs(c["pct"]) for c in normales]
    return {
        "n": len(corridas),
        "acierto_direccion": round(sum(1 for d in dirs if d) / len(dirs), 3) if dirs else None,
        "magnitud_media_extremos": round(statistics.mean(mag_ext), 3) if mag_ext else None,
        "magnitud_media_normales": round(statistics.mean(mag_nor), 3) if mag_nor else None,
        "magnitud_media": round(statistics.mean(abs(p) for p in pcts), 3) if pcts else None,
        "pcts": [round(p, 3) for p in pcts],
    }


def correr(conjunto: str = "baseline", n_semillas: int = 3, semillas: list[int] | None = None,
           guardar: bool = False) -> dict:
    """Corre el banco de shocks con un conjunto de perillas."""
    os.environ["ENJAMBRE_PERILLAS"] = conjunto
    impacto.reiniciar_cache()
    cfg = impacto.cargar_perillas(conjunto)
    semillas = semillas or [42, 7, 19, 3, 11, 29][:max(1, n_semillas)]
    t0 = time.time()
    corridas = []
    for seed in semillas:
        for shock in SHOCKS:
            corridas.append(_correr_shock(seed, shock))
    resumen = resumir_corridas(corridas)
    informe = {
        "cuando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "conjunto": cfg["nombre"],
        "version": cfg["version"],
        "perillas": cfg["globales"],
        "nota": cfg["nota"],
        "semillas": semillas,
        "shocks": list(SHOCKS),
        "resumen": resumen,
        "corridas": corridas,
        "segundos": round(time.time() - t0, 1),
        "aviso": (
            "Esto mide RESPUESTA A SHOCK numérico, no acierto vs mercado real. "
            "La Loss oficial (dirección + ratio de fuerza) está en corrector.evaluar_casos "
            "y se llena con el backtest / la libreta."
        ),
    }
    if guardar:
        RUTA_EXPERIMENTOS.mkdir(parents=True, exist_ok=True)
        nombre = f"{cfg['nombre']}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        ruta = RUTA_EXPERIMENTOS / nombre
        ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
        informe["archivo"] = str(ruta)
    return informe


def comparar_libreta(casos: list[tuple[float, float]]) -> dict:
    """Atajo: Loss oficial sobre pares (sim_pct, real_pct) ya medidos."""
    return evaluar_casos(casos)


def contraste(base: dict, hypo: dict) -> dict:
    """Compara dos informes del mismo banco de shocks (mismas semillas)."""
    rb, rh = base["resumen"], hypo["resumen"]

    def _ratio(antes, despues):
        if antes is None or despues is None or abs(antes) < 1e-12:
            return None
        return round(despues / antes, 3)

    por_base = {(c["seed"], c["shock"]): c for c in base["corridas"]}
    pares = []
    for c in hypo["corridas"]:
        o = por_base.get((c["seed"], c["shock"]))
        if o is None:
            continue
        pares.append({
            "seed": c["seed"],
            "shock": c["shock"],
            "pct_base": o["pct"],
            "pct_hypo": c["pct"],
            "dir_base": o["direccion_ok"],
            "dir_hypo": c["direccion_ok"],
            "extremo": abs(c["shock"]) >= 0.8,
        })
    ratio_ext = _ratio(rb.get("magnitud_media_extremos"), rh.get("magnitud_media_extremos"))
    ratio_nor = _ratio(rb.get("magnitud_media_normales"), rh.get("magnitud_media_normales"))
    # v1a sirve si los extremos crecen más que los días normales y la dirección no cae
    dir_ok = (
        rb.get("acierto_direccion") is None
        or rh.get("acierto_direccion") is None
        or rh["acierto_direccion"] + 1e-9 >= rb["acierto_direccion"]
    )
    extrema_gana = ratio_ext is not None and ratio_ext >= 1.15
    no_explota_normales = (ratio_nor is None or ratio_ext is None
                           or ratio_nor <= ratio_ext)
    return {
        "base": base["conjunto"],
        "hipotesis": hypo["conjunto"],
        "acierto_direccion_base": rb.get("acierto_direccion"),
        "acierto_direccion_hypo": rh.get("acierto_direccion"),
        "magnitud_normales_base": rb.get("magnitud_media_normales"),
        "magnitud_normales_hypo": rh.get("magnitud_media_normales"),
        "magnitud_extremos_base": rb.get("magnitud_media_extremos"),
        "magnitud_extremos_hypo": rh.get("magnitud_media_extremos"),
        "ratio_normales": ratio_nor,
        "ratio_extremos": ratio_ext,
        "direccion_se_mantiene": dir_ok,
        "extremos_crecen_mas": bool(extrema_gana and no_explota_normales),
        "pares": pares,
        "segundos": round((base.get("segundos") or 0) + (hypo.get("segundos") or 0), 1),
        "aviso": (
            "Respuesta a shock numérico, no acierto vs mercado real. "
            "v1a (subir el volumen) ya no pasa. v1c (zona muerta) se juzga "
            "al revés: no debe inflar días chicos ni tumbar los extremos."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Experimento de calibración (sin API).")
    parser.add_argument("--set", dest="conjunto", default=os.environ.get("ENJAMBRE_PERILLAS", "baseline"))
    parser.add_argument("--vs", dest="versus", default=None,
                        help="Si se pasa, corre --set y --vs y imprime el contraste.")
    parser.add_argument("--n", dest="n_semillas", type=int, default=2)
    parser.add_argument("--guardar", action="store_true")
    args = parser.parse_args(argv)
    if args.versus:
        inf_a = correr(conjunto=args.conjunto, n_semillas=args.n_semillas, guardar=args.guardar)
        inf_b = correr(conjunto=args.versus, n_semillas=args.n_semillas, guardar=args.guardar)
        informe = contraste(inf_a, inf_b)
        print(json.dumps(informe, ensure_ascii=False, indent=2))
        return 0
    informe = correr(conjunto=args.conjunto, n_semillas=args.n_semillas, guardar=args.guardar)
    print(json.dumps({k: informe[k] for k in ("conjunto", "version", "perillas", "resumen", "segundos", "aviso")
                      if k in informe}, ensure_ascii=False, indent=2))
    if informe.get("archivo"):
        print(f"\nguardado: {informe['archivo']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
