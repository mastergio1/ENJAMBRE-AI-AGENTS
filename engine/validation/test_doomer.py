"""
Intervención 1 — voz "doomer pura" (fiel, que NO invierte) mezclada en el
consenso con peso `peso_doomer`.

El sesgo alcista viene de que los invertidores (quant/contrarian/optimista)
empujan positivo ante una mala noticia y diluyen el consenso hacia arriba. Esta
voz añade la lectura FIEL del léxico (que no invierte) al consenso, de forma
INCONDICIONAL (a diferencia del Plan A, que solo dispara si el consenso ya está
muy bajista).

Verifica que:
1. Con peso_doomer 0.0 el consenso/tono es IDÉNTICO al histórico.
2. Con peso_doomer > 0, ante una mala noticia (cuyo consenso está diluido por
   los invertidores) el tono se vuelve MÁS bajista (más fiel).
3. La voz nunca fuerza a positivo un consenso negativo (no invierte el signo).

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"


def _respuestas(modelo, titular):
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def _tono(peso_doomer: float) -> float:
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._peso_doomer = peso_doomer
    m._umbral_correccion = 0.0  # aísla la voz doomer del Plan A
    resp = _respuestas(m, TITULAR_MALO)
    return m._tono_de_titular(TITULAR_MALO, resp)


def test_doomer_0_preserva_el_historico():
    """peso_doomer 0.0 = comportamiento histórico (sin mezcla)."""
    from model import GANANCIA_CONSENSO
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._peso_doomer = 0.0
    m._umbral_correccion = 0.0
    resp = _respuestas(m, TITULAR_MALO)
    ia = [r for r in resp if r["fuente"] in ("api", "cache")]
    peso = sum(r["confianza"] for r in ia)
    consenso = sum(r["senal"] * r["confianza"] for r in ia) / peso
    esperado = max(-1.0, min(1.0, consenso * GANANCIA_CONSENSO))
    assert abs(m._tono_de_titular(TITULAR_MALO, resp) - esperado) < 1e-9


def test_doomer_hace_el_tono_mas_bajista():
    """Ante mala noticia, la voz doomer hace el tono MÁS negativo (más fiel)."""
    tono_off = _tono(0.0)
    tono_on = _tono(0.2)
    assert tono_off < 0, "el titular es malo: el tono base debe ser negativo"
    assert tono_on < tono_off, \
        f"la voz doomer debe hacer el tono más bajista: {tono_on} vs {tono_off}"


def test_doomer_no_invierte_el_signo():
    """La mezcla no vuelve positivo un tono que era negativo."""
    tono_on = _tono(0.2)
    assert tono_on < 0, "la voz doomer nunca debe invertir un tono negativo a positivo"


if __name__ == "__main__":
    print("\n🧪 Intervención 1: voz doomer pura")
    print("=" * 45)
    print(f"  tono con doomer 0.0 (base): {_tono(0.0):+.3f}")
    print(f"  tono con doomer 0.2:        {_tono(0.2):+.3f}")
    print("=" * 45)
