"""
Plan A — corrección del sesgo alcista en el consenso.

El enjambre acierta ~80% en positivas pero ~53% en negativas porque el TONO se
suaviza hacia arriba: el descuento de magnitud (GANANCIA_CONSENSO) encoge una
mala noticia clara. La corrección: cuando los líderes que hablaron con la IA ya
leen la noticia como CLARAMENTE bajista (consenso < -umbral), NO la suavizamos;
usamos la lectura a plena magnitud (la MÁS bajista entre consenso y léxico),
nunca para invertir el signo.

Verifica que:
1. Con umbral 0.0 (desactivada) el tono es IDÉNTICO al histórico
   (consenso * GANANCIA_CONSENSO).
2. Con umbral activo, ante una mala noticia clara el tono es MÁS negativo
   (más fiel) que con la corrección apagada.
3. La corrección NUNCA invierte el signo (jamás vuelve el tono menos bajista
   que el consenso crudo).

Corre local, sin LLM: las señales por arquetipo salen del fallback (mismo
espíritu que el LLM real), marcadas 'api' para ejercer la ruta de consenso.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import RUTA_CONFIG, GANANCIA_CONSENSO, MercadoEnjambre  # noqa: E402

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"


def _respuestas(modelo, titular):
    """Señal por arquetipo como la daría el fallback, marcada 'api' para
    ejercer la ruta de consenso (no el atajo léxico)."""
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def _tono(umbral: float) -> float:
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = umbral
    resp = _respuestas(m, TITULAR_MALO)
    return m._tono_de_titular(TITULAR_MALO, resp)


def _consenso(modelo, resp) -> float:
    """El consenso crudo (promedio ponderado por confianza), sin descuento."""
    ia = [(l.arquetipo, r) for l, r in zip(modelo._lideres, resp)
          if r["fuente"] in ("api", "cache")]
    num = sum(r["senal"] * r["confianza"] for _, r in ia)
    den = sum(r["confianza"] for _, r in ia)
    return num / den


def test_umbral_0_preserva_el_historico():
    """umbral 0.0 = corrección apagada = consenso * GANANCIA_CONSENSO."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0
    m._peso_doomer = 1.0  # doomer selectivo a peso pleno = promedio de TODAS
    resp = _respuestas(m, TITULAR_MALO)
    esperado = max(-1.0, min(1.0, _consenso(m, resp) * GANANCIA_CONSENSO))
    assert abs(m._tono_de_titular(TITULAR_MALO, resp) - esperado) < 1e-9


def test_correccion_hace_el_tono_mas_fiel():
    """Ante una mala noticia clara, la corrección hace el tono MÁS negativo.

    El consenso de este titular malo está DILUIDO a ~-0.27 (los invertidores lo
    suben) y la base lo suaviza aún más (×0.8 → -0.22). Con la corrección a un
    umbral que dispara (0.2 < 0.27), el tono salta a la lectura fiel (~-0.80).
    """
    tono_off = _tono(0.0)
    tono_on = _tono(0.2)
    assert tono_off < 0, "el titular es malo: el tono base debe ser negativo"
    assert tono_on < tono_off, \
        f"la corrección debe hacer el tono MÁS bajista: {tono_on} vs {tono_off}"


def test_nunca_invierte_el_signo():
    """La corrección jamás vuelve el tono menos bajista que el consenso crudo."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.2
    resp = _respuestas(m, TITULAR_MALO)
    consenso = _consenso(m, resp)
    tono = m._tono_de_titular(TITULAR_MALO, resp)
    if consenso < -0.2:  # solo cuando la corrección de verdad dispara
        assert tono <= max(-1.0, consenso), \
            "el tono corregido nunca es menos bajista que el consenso crudo"


if __name__ == "__main__":
    print("\n🧪 Plan A: corrección del sesgo alcista")
    print("=" * 45)
    print(f"  tono con umbral 0.0 (base):      {_tono(0.0):+.3f}")
    print(f"  tono con umbral 0.3 (corrección): {_tono(0.3):+.3f}")
    print("=" * 45)
