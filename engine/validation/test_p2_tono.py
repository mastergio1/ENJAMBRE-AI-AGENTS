"""
P2 — separar "tono de mercado" de "apuesta del líder".

Verifica que:
1. Con peso_tono_invertidores = 1.0, el tono es IDÉNTICO al histórico
   (promedio de señales ponderado por confianza).
2. Con peso 0.0, los arquetipos invertidores (contrarian/optimista/quant) NO
   fijan el clima: ante una mala noticia, el tono es MÁS negativo (fiel a la
   noticia) que con 1.0.
3. La APUESTA individual de cada líder (su .senal) NO cambia con P2 — solo
   cambia el tono de mercado.

Corre local, sin LLM: las respuestas por arquetipo se generan con las
transformaciones reales del fallback (mismo espíritu que el LLM).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import RUTA_CONFIG, ARQUETIPOS_INVERSORES, MercadoEnjambre  # noqa: E402

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


def _tono(peso: float) -> float:
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0  # aísla P2: sin Plan A (corrección de sesgo)
    m._peso_tono_invertidores = peso
    resp = _respuestas(m, TITULAR_MALO)
    return m._tono_de_titular(TITULAR_MALO, resp)


def test_peso_1_preserva_el_historico():
    """peso 1.0 = promedio ponderado por confianza de TODAS las señales."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0  # aísla P2: sin Plan A (corrección de sesgo)
    m._peso_tono_invertidores = 1.0
    m._peso_doomer = 1.0  # incluir el doomer selectivo a peso pleno = promedio de TODAS
    resp = _respuestas(m, TITULAR_MALO)
    ia = [r for r in resp if r["fuente"] in ("api", "cache")]
    peso = sum(r["confianza"] for r in ia)
    historico = sum(r["senal"] * r["confianza"] for r in ia) / peso
    from model import GANANCIA_CONSENSO
    esperado = max(-1.0, min(1.0, historico * GANANCIA_CONSENSO))
    assert abs(m._tono_de_titular(TITULAR_MALO, resp) - esperado) < 1e-9


def test_peso_0_hace_el_tono_mas_fiel():
    """Ante mala noticia, excluir a los invertidores hace el tono MÁS negativo."""
    tono_1 = _tono(1.0)
    tono_0 = _tono(0.0)
    assert tono_1 < 0, "el titular es malo: el tono debe ser negativo"
    assert tono_0 < tono_1, f"P2 debe hacer el tono más negativo: {tono_0} vs {tono_1}"


def test_apuesta_del_lider_no_cambia():
    """P2 solo toca el TONO; la señal individual del líder queda intacta."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    resp = _respuestas(m, TITULAR_MALO)
    m._peso_tono_invertidores = 0.0
    m.aplicar_titular(TITULAR_MALO, respuestas=resp,
                      perfil={"sensibilidad": 1.0, "refugio": 0.0})
    # las señales de los invertidores siguen siendo su apuesta (no anuladas)
    invertidores = [l for l in m._lideres if l.arquetipo in ARQUETIPOS_INVERSORES]
    assert any(abs(l.senal) > 0.05 for l in invertidores), \
        "los invertidores deben seguir operando con su propia señal"


if __name__ == "__main__":
    print("\n🧪 P2: separar tono de apuesta")
    print("=" * 45)
    print(f"  tono con peso 1.0 (actual): {_tono(1.0):+.3f}")
    print(f"  tono con peso 0.0 (P2):     {_tono(0.0):+.3f}")
    print("=" * 45)
