"""
Validación de la memoria de agentes: el "modo cautela" en rachas de noticias.

La memoria (últimas 5 noticias) sirve para UNA cosa que sí funciona: detectar
rachas malas y activar `modo_cautela`, que dispara el freno de la manada
(ver test_freno_manada.py, donde se mide que el freno reduce el sobre-pánico).

Nota histórica: hubo un segundo mecanismo, la "memoria de percepción"
(`ajustar_por_contexto` sobre el miedoso/noise), que se PROBÓ y NO amortiguaba
el pánico (INFORME_NIVEL1_RESULTADO.md). Se retiró por peso muerto; la palanca
que quedó es el freno de la manada. Este test cubre lo que sostiene ese freno:
que la cautela se activa cuando debe.

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402


def test_cautela_se_activa_en_racha():
    """La cautela se dispara tras 3 malas y NO antes (es lo que enciende el freno)."""
    m = MercadoEnjambre(seed=1, ticks_horizonte=30, ruta_config=RUTA_CONFIG)
    mie = next(a for a in m.agents if type(a).__name__ == "Miedoso")
    assert not mie.modo_cautela
    m.aplicar_noticia(-0.5); m.aplicar_noticia(-0.5)
    assert not mie.modo_cautela, "cautela no debe activarse con 2 malas"
    m.aplicar_noticia(-0.5)
    assert mie.modo_cautela, "cautela debe activarse con 3 malas"


if __name__ == "__main__":
    print("\n🧪 Memoria: activación del modo cautela")
    print("=" * 45)
    test_cautela_se_activa_en_racha()
    print("✅ La cautela se activa con 3 malas (y no antes).")
    print("   El efecto de amortiguación se mide en test_freno_manada.py.")
    print("=" * 45)
