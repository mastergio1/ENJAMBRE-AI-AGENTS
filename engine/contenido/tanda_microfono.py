"""Tanda chica del micrófono (hipótesis v1d) — ~12 titulares, ~US$1.50.

No corre sola: hace falta ANTHROPIC_API_KEY. Compara baseline vs v1d
en los fallos conocidos (Fed priced-in, aranceles, resultados) sin
re-rendir los 632.

Uso (desde engine/):

    ENJAMBRE_PERILLAS=baseline python -m contenido.tanda_microfono --n 4
    ENJAMBRE_PERILLAS=hipotesis_v1d python -m contenido.tanda_microfono --n 4

Una hipótesis por corrida. No pisa producción.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# 70 % normales / priced-in + 30 % sorpresa. Titulares ya en el banco.
TITULARES = (
    # priced-in / tibios (el micrófono debería hablar bajito)
    ("fed-holds-expected", "Fed holds rates and flags a March increase, as widely expected", "SPY"),
    ("fed-pause", "Fed pauses rate hikes but signals two more increases may lie ahead", "SPY"),
    ("cpi-in-line", "Consumer prices come in line with expectations; Fed keeps rates unchanged", "SPY"),
    ("fed-transitory", "Fed holds rates steady and repeats view that inflation pressures are transitory", "SPY"),
    # sorpresa / extremos (no debería apagarse)
    ("tariffs-stun", "Sweeping new US tariffs stun markets; stocks sink on trade war fears", "SPY"),
    ("lehman", "Lehman Brothers files for bankruptcy; global financial system reels", "SPY"),
    ("fed-zero", "S&P 500 plunges 12% despite Fed emergency rate cut to zero", "SPY"),
    # resultados (beat/miss, no el mood)
    ("amazon-loss", "Amazon posts first quarterly loss since 2015 on weak outlook; shares tumble", "AMZN"),
    ("meta-crater", "Meta shares crater 20% on weak forecast and soaring metaverse spending", "META"),
    ("target-guidance", "Target Raises FY2026 GAAP EPS Guidance from $8.50 to $9.90-$10.90 vs $8.39 Est", "TGT"),
    # ruido / sopa de tickers
    ("lilly-soup", "Eli Lilly Could Swing Over $76 Billion In Value After Earnings", "LLY"),
    ("nvidia-ai", "NVIDIA CEO Says AI's Future Isn't Just Copper", "NVDA"),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=4, help="cuántos titulares (máx 12)")
    parser.add_argument("--dry", action="store_true", help="solo lista, no simula")
    args = parser.parse_args(argv)

    if not os.environ.get("ANTHROPIC_API_KEY") and not args.dry:
        print("sin ANTHROPIC_API_KEY: no gasto saldo. Pasa --dry para ver la tanda.",
              file=sys.stderr)
        print(json.dumps({
            "conjunto": os.environ.get("ENJAMBRE_PERILLAS", "baseline"),
            "aviso": "sin clave no se rinde. los 632 ya pagados están en docs/libreta-honesta.md",
            "tanda": [{"id": i, "titular": t, "simbolo": s} for i, t, s in TITULARES[:args.n]],
        }, ensure_ascii=False, indent=2))
        return 2

    n = max(1, min(args.n, len(TITULARES)))
    if args.dry:
        print(json.dumps({"tanda": [
            {"id": i, "titular": t, "simbolo": s} for i, t, s in TITULARES[:n]
        ]}, ensure_ascii=False, indent=2))
        return 0

    from contenido.pipeline import simular_titular_completo

    filas = []
    for i, (eid, titular, simbolo) in enumerate(TITULARES[:n]):
        reporte, lideres, *_ = simular_titular_completo(titular, seed=20260903 + i)
        fuentes = [l.get("fuente") for l in lideres]
        ia = sum(1 for f in fuentes if f in ("api", "cache"))
        sops = [float(l["sorpresa"]) for l in lideres if isinstance(l.get("sorpresa"), (int, float))]
        filas.append({
            "id": eid, "simbolo": simbolo, "titular": titular,
            "pct": reporte.get("direccion_pct"),
            "ia": ia, "n_lideres": len(lideres),
            "sorpresa": round(sum(sops) / len(sops), 3) if sops else None,
            "conjunto": os.environ.get("ENJAMBRE_PERILLAS", "baseline"),
        })
        print(json.dumps(filas[-1], ensure_ascii=False), flush=True)
    print(json.dumps({"hechas": filas}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
