"""
Optimiza `factor_freno_cautela` de la MANADA con Optuna (Nivel 1).

Contexto (ver INFORME_FRENO_MANADA.md): en una racha de malas noticias, la
manada (imitadores) arma una cascada auto-alimentada y la 4ª mala noticia cae
MÁS que la 1ª — eso es sobre-pánico. El freno reduce cuánto vende la manada en
"modo cautela". Este script busca el valor del freno que mejor corrige el
sobre-pánico sin caer en la trampa degenerada (factor=0 = la manada nunca vende
= el mercado ignora las malas noticias = irreal).

OBJETIVO (honesto, anclado al propio modelo):
  que la 4ª mala noticia NO golpee más fuerte que la 1ª  →  minimizar (d4 - d1)^2
  - d1 = caída tras la 1ª mala (reacción "normal", NO depende del freno:
         la cautela necesita 3 malas para activarse).
  - d4 = caída tras la 4ª mala (aquí la cascada de la manada explota).
  Bajar el freno de más hace d4 MÁS suave que d1 (el mercado ignorando la mala
  noticia): el objetivo también lo penaliza. El óptimo es d4 ≈ d1.

Los hechos estilizados NO se corren por trial (son caros y el freno apenas los
toca porque solo actúa en cautela); se validan aparte, una vez, sobre el factor
ganador (ver `--validar` abajo o corre test_hechos_estilizados.py con el config).

Uso:
    python calibration/optimizar_freno.py --trials 15 --seeds 42 7 123 3 11 19
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import optuna

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402

SECUENCIA = [-0.5, -0.5, -0.5, -0.5, 0.5]   # 4 malas seguidas + 1 buena
TICKS_POR_NOTICIA = 20
_TEMP = Path(__file__).resolve().parent.parent / "config" / "_temp_optuna_freno.json"


def _config_con_freno(factor: float) -> Path:
    """Escribe un config temporal con `factor_freno_cautela` en el tipo MANADA."""
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    for t in config["tipos"]:
        if t["id"] == "manada":
            t.setdefault("parametros", {})["factor_freno_cautela"] = factor
    with open(_TEMP, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return _TEMP


def _caidas(seed: int, ruta: Path) -> list[float]:
    """Cambio de precio tras cada noticia de la secuencia (d1..d5)."""
    m = MercadoEnjambre(seed=seed, precio_inicial=100.0,
                        ticks_horizonte=len(SECUENCIA) * TICKS_POR_NOTICIA + 5,
                        ruta_config=ruta)
    precios = [m.historial_precios[-1]]
    for sent in SECUENCIA:
        m.aplicar_noticia(sentimiento=sent)
        for _ in range(TICKS_POR_NOTICIA):
            m.step()
        precios.append(m.historial_precios[-1])
    return [p2 - p1 for p1, p2 in zip(precios, precios[1:])]


def _evaluar(factor: float, seeds: list[int]) -> dict:
    """Corre la secuencia para cada semilla y devuelve d1, d4 y el objetivo."""
    ruta = _config_con_freno(factor)
    try:
        d1s, d4s = [], []
        for s in seeds:
            d = _caidas(s, ruta)
            d1s.append(d[0])
            d4s.append(d[3])
    finally:
        if _TEMP.exists():
            _TEMP.unlink()
    md1, md4 = float(np.mean(d1s)), float(np.mean(d4s))
    return {"d1": md1, "d4": md4, "objetivo": (md4 - md1) ** 2,
            "d1_por_semilla": [round(x, 2) for x in d1s],
            "d4_por_semilla": [round(x, 2) for x in d4s]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=15)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 7, 123, 3, 11, 19])
    args = ap.parse_args()

    print(f"🔧 Optimizando factor_freno_cautela · {args.trials} trials · "
          f"{len(args.seeds)} semillas")
    print(f"   Objetivo: 4ª mala ≈ 1ª mala (sin sobre-pánico, sin ignorar la noticia)")
    print("=" * 62)

    def objective(trial: optuna.Trial) -> float:
        factor = trial.suggest_float("factor_freno_cautela", 0.0, 1.0)
        r = _evaluar(factor, args.seeds)
        trial.set_user_attr("d1", r["d1"])
        trial.set_user_attr("d4", r["d4"])
        print(f"  factor={factor:.3f}  d1={r['d1']:+.2f}  d4={r['d4']:+.2f}  "
              f"obj={r['objetivo']:.3f}")
        return r["objetivo"]

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize",
                                sampler=optuna.samplers.TPESampler(seed=1))
    # Anclas: el freno actual (1.0 = sin freno) y el probado a mano (0.5)
    study.enqueue_trial({"factor_freno_cautela": 1.0})
    study.enqueue_trial({"factor_freno_cautela": 0.5})
    study.optimize(objective, n_trials=args.trials)

    best = study.best_trial
    print("=" * 62)
    print(f"🏆 Mejor factor: {best.params['factor_freno_cautela']:.3f}")
    print(f"   d1={best.user_attrs['d1']:+.2f}  d4={best.user_attrs['d4']:+.2f}  "
          f"(objetivo, cuanto menor mejor: {best.value:.4f})")
    r = _evaluar(best.params["factor_freno_cautela"], args.seeds)
    print(f"   d1 por semilla: {r['d1_por_semilla']}")
    print(f"   d4 por semilla: {r['d4_por_semilla']}")
    print("\n   Siguiente paso: validar hechos estilizados con este factor "
          "antes de mergear.")


if __name__ == "__main__":
    main()
