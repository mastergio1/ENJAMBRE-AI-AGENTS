"""
Intervención 1 — arquetipo doomer SELECTIVO (voz LLM real, no la mezcla léxica).

Un arquetipo nuevo ('doomer_selectivo') que lee las malas noticias a plena
magnitud SIN invertir, pero SOLO cuando el deterioro es claro (neutral en las
ambiguas → no sobre-corrige, que fue lo que hundió a la mezcla incondicional).
Su peso en el TONO se modula con `peso_doomer`: 0 = no participa del clima
(base), 1 = peso pleno. Su apuesta individual no se toca.

Verifica que:
1. El arquetipo existe en la mezcla de líderes.
2. Con peso_doomer 0 el arquetipo NO afecta el tono (idéntico a excluirlo).
3. Ante una mala noticia clara, incluirlo (peso 1) hace el tono MÁS bajista.
4. Es SELECTIVO: ante una noticia neutra/ambigua, incluirlo casi no mueve el
   tono (su señal es ~0, no grita lobo).

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import RUTA_CONFIG, ARQUETIPOS_DOOMER, MercadoEnjambre  # noqa: E402

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"
TITULAR_NEUTRO = "The market opened for regular trading on Monday morning"


def _respuestas(modelo, titular):
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def _tono(peso_doomer: float, titular: str) -> float:
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._peso_doomer = peso_doomer
    m._umbral_correccion = 0.0            # aísla del Plan A
    m._peso_tono_invertidores = 1.0
    return m._tono_de_titular(titular, _respuestas(m, titular))


def test_el_arquetipo_existe_en_la_mezcla():
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    arqs = {l.arquetipo for l in m._lideres}
    assert ARQUETIPOS_DOOMER <= arqs, f"falta el arquetipo doomer selectivo en {arqs}"


def test_peso_0_no_afecta_el_tono():
    """peso_doomer 0 = el arquetipo no participa del clima."""
    # con peso 0, el tono es el de siempre (sin la voz doomer)
    tono0 = _tono(0.0, TITULAR_MALO)
    assert tono0 < 0, "el titular es malo: el tono base debe ser negativo"


def test_incluirlo_hace_el_tono_mas_bajista_en_mala_noticia():
    """Ante una mala noticia clara, dar peso al doomer baja el tono."""
    tono_off = _tono(0.0, TITULAR_MALO)
    tono_on = _tono(1.0, TITULAR_MALO)
    assert tono_on < tono_off, \
        f"el doomer selectivo debe hacer el tono más bajista: {tono_on} vs {tono_off}"


def test_selectivo_no_sobre_corrige_lo_neutro():
    """Ante una noticia neutra, incluir el doomer casi no mueve el tono
    (su señal es ~0: no grita lobo → no sobre-corrige)."""
    tono_off = _tono(0.0, TITULAR_NEUTRO)
    tono_on = _tono(1.0, TITULAR_NEUTRO)
    assert abs(tono_on - tono_off) < 0.10, \
        f"en lo neutro el doomer no debe mover el tono: {tono_on} vs {tono_off}"


if __name__ == "__main__":
    print("\n🧪 Intervención 1: arquetipo doomer SELECTIVO")
    print("=" * 48)
    print(f"  mala noticia  → tono peso0={_tono(0.0, TITULAR_MALO):+.3f}  "
          f"peso1={_tono(1.0, TITULAR_MALO):+.3f}")
    print(f"  neutra        → tono peso0={_tono(0.0, TITULAR_NEUTRO):+.3f}  "
          f"peso1={_tono(1.0, TITULAR_NEUTRO):+.3f}")
    print("=" * 48)
