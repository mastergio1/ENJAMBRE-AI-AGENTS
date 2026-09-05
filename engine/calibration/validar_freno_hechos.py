"""
Reja de seguridad: corre los 5 hechos estilizados (CLAUDE.md §7) con un valor
dado de `factor_freno_cautela`, para confirmar que el freno de la manada NO
rompe el realismo del mercado antes de mergear.

Replica la lógica de test_hechos_estilizados.py pero apuntando a un config
temporal con el factor inyectado. Imprime el valor medido de cada criterio,
no solo pasa/falla.

Uso:
    python calibration/validar_freno_hechos.py --factor 0.5
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/

from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402
from validation.hechos_estilizados import (  # noqa: E402
    asimetria_panico, autocorrelacion, curtosis,
)

TICKS_SESION = 600
_TEMP = Path(__file__).resolve().parent.parent / "config" / "_temp_optuna_freno.json"


def _config(factor: float) -> Path:
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    for t in config["tipos"]:
        if t["id"] == "manada":
            t.setdefault("parametros", {})["factor_freno_cautela"] = factor
    with open(_TEMP, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return _TEMP


def _retornos(seed: int, ruta: Path) -> tuple:
    m = MercadoEnjambre(seed=seed, ticks_horizonte=TICKS_SESION, ruta_config=ruta)
    for _ in range(TICKS_SESION):
        if m.random.random() < 0.02:
            m.aplicar_noticia(m.random.gauss(0, 0.45))
        m.step()
    return tuple(m.retornos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factor", type=float, required=True)
    args = ap.parse_args()
    ruta = _config(args.factor)
    ok = True
    try:
        print(f"🛡️  Hechos estilizados con factor_freno_cautela = {args.factor}")
        print("=" * 60)
        cache = {s: _retornos(s, ruta) for s in [42, 3, 7, 11, 19]}

        # 1. Colas gordas: curtosis > 3
        for s in [42, 3]:
            k = curtosis(cache[s])
            paso = k > 3
            ok &= paso
            print(f"  1. Colas gordas   seed {s:>2}: curtosis={k:6.2f}  (>3)  "
                  f"{'✅' if paso else '❌'}")

        # 2. Clustering de volatilidad: ac1>0.1 y ac1>ac10
        for s in [42, 3]:
            absns = [abs(r) for r in cache[s]]
            ac1, ac10 = autocorrelacion(absns, 1), autocorrelacion(absns, 10)
            paso = ac1 > 0.1 and ac1 > ac10
            ok &= paso
            print(f"  2. Vol clustering seed {s:>2}: ac1={ac1:.3f} ac10={ac10:.3f}"
                  f"  {'✅' if paso else '❌'}")

        # 3. Sin autocorrelación de retornos: media≈0, max<0.2
        acs = [autocorrelacion(cache[s], 1) for s in [42, 3, 7, 11, 19]]
        paso = abs(statistics.mean(acs)) < 0.1 and max(abs(a) for a in acs) < 0.2
        ok &= paso
        print(f"  3. Sin autocorr.        media={statistics.mean(acs):+.3f} "
              f"max|ac|={max(abs(a) for a in acs):.3f}  {'✅' if paso else '❌'}")

        # 4. Asimetría de pánico > 1
        for s in [42, 3]:
            a = asimetria_panico(cache[s])
            paso = a > 1.0
            ok &= paso
            print(f"  4. Asim. pánico   seed {s:>2}: ratio={a:5.2f}  (>1)  "
                  f"{'✅' if paso else '❌'}")

        # 5. Respuesta a shock: cae >5%, rebota, rebote parcial
        for s in [42, 3]:
            m = MercadoEnjambre(seed=s, ticks_horizonte=300, ruta_config=ruta)
            m.correr(80)
            previo = m.historial_precios[-1]
            m.aplicar_noticia(-0.9)
            m.correr(120)
            post = np.array(m.historial_precios[80:])
            cae = post.min() < previo * 0.95
            rebota = post[-1] > post.min()
            parcial = post[-1] < previo * 0.995
            paso = cae and rebota and parcial
            ok &= paso
            print(f"  5. Shock -0.9     seed {s:>2}: min={post.min():.1f} "
                  f"fin={post[-1]:.1f} previo={previo:.1f}  "
                  f"cae/rebota/parcial={int(cae)}{int(rebota)}{int(parcial)}  "
                  f"{'✅' if paso else '❌'}")
    finally:
        if _TEMP.exists():
            _TEMP.unlink()

    print("=" * 60)
    print("✅ TODOS pasan — el freno no rompe el realismo."
          if ok else "❌ Algún criterio falló — revisar antes de mergear.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
