"""
Test A/B: frenar la MANADA en modo cautela (Nivel 1, rediseño del freno).

Mide la caída tras la 4ª mala noticia con el freno ON (la manada vende menos en
cautela) vs OFF (venta normal), sobre la MISMA secuencia y semilla, para aislar
el efecto. Correcciones vs. el borrador: import estilo proyecto, y el override
va al TIPO correcto (tipos[manada].parametros), no a una clave inexistente.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from model import RUTA_CONFIG, MercadoEnjambre   # noqa: E402

SECUENCIA = [-0.5, -0.5, -0.5, -0.5, 0.5]
TICKS = 20
SEEDS = [42, 7, 123]
_TEMP = Path(__file__).parent.parent / "config" / "_temp_freno.json"


def _config_con_freno(factor: float) -> Path:
    """Escribe un config temporal con factor_freno_cautela en el tipo MANADA."""
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    for t in config["tipos"]:
        if t["id"] == "manada":
            t.setdefault("parametros", {})["factor_freno_cautela"] = factor
    with open(_TEMP, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return _TEMP


def _caida_4a_mala(seed: int, factor: float) -> float:
    ruta = _config_con_freno(factor)
    try:
        m = MercadoEnjambre(seed=seed, precio_inicial=100.0,
                            ticks_horizonte=len(SECUENCIA) * TICKS + 5, ruta_config=ruta)
        precios = [m.historial_precios[-1]]
        for sent in SECUENCIA:
            m.aplicar_noticia(sentimiento=sent)
            for _ in range(TICKS):
                m.step()
            precios.append(m.historial_precios[-1])
    finally:
        if _TEMP.exists():
            _TEMP.unlink()
    return precios[4] - precios[3]   # caída tras la 4ª mala


def test_freno_manada_reduce_la_caida():
    """A/B: la 4ª mala cae MENOS con la manada frenada (0.5) que sin freno (1.0)."""
    con = [_caida_4a_mala(s, 0.5) for s in SEEDS]
    sin = [_caida_4a_mala(s, 1.0) for s in SEEDS]
    media_con, media_sin = float(np.mean(con)), float(np.mean(sin))
    print(f"\n4ª mala — caída media  CON freno: {media_con:+.3f} · SIN freno: {media_sin:+.3f}")
    print(f"  con freno (0.5): {[round(x,3) for x in con]}")
    print(f"  sin freno (1.0): {[round(x,3) for x in sin]}")
    print(f"  diferencia (SIN - CON): {media_sin - media_con:+.3f}  (positivo = el freno mejora)")
    assert media_con > media_sin, "El freno NO redujo la caída (CON no cae menos que SIN)"


if __name__ == "__main__":
    print("\n🧪 Test A/B: frenar la manada en modo cautela")
    print("=" * 55)
    try:
        test_freno_manada_reduce_la_caida()
        print("\n✅ El freno a la manada REDUCE la caída (mejora).")
    except AssertionError as e:
        print(f"\n❌ {e}")
    print("=" * 55)
