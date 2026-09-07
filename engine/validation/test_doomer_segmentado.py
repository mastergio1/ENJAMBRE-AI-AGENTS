"""
Segmentación por mercado del doomer selectivo (Intervención 1).

La medición mostró que el Analista de Riesgo Selectivo ayuda en ÍNDICE
(+7.6 pts en negativas) pero es INERTE en cripto (0.0). Por eso el peso en el
tono depende del MERCADO detectado (config `peso_doomer_por_mercado`).

Verifica que, SIN override global (producción):
1. Ante una mala noticia clara, el tono en ÍNDICE es MÁS bajista que en CRIPTO
   (el doomer participa del clima en índice, no en cripto).
2. El override global ENJAMBRE_PESO_DOOMER, si está fijado (medición/rollback),
   manda sobre la segmentación y aplica ese peso en cualquier mercado.

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from brains.mercado import perfil_de  # noqa: E402
from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"


def _respuestas(modelo, titular):
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def _tono_en(mercado, monkeypatch):
    monkeypatch.delenv("ENJAMBRE_PESO_DOOMER", raising=False)  # producción: por-mercado
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0            # aísla del Plan A: solo se ve el doomer
    m._peso_doomer = None                 # sin override global → segmentación
    m.perfil = perfil_de(mercado)
    return m._tono_de_titular(TITULAR_MALO, _respuestas(m, TITULAR_MALO))


def test_indice_mas_bajista_que_cripto(monkeypatch):
    """En producción, el doomer participa del tono en índice (peso 1.0) pero no
    en cripto (peso 0.0): ante la misma mala noticia, índice queda MÁS bajista."""
    tono_indice = _tono_en("indice", monkeypatch)
    tono_cripto = _tono_en("cripto", monkeypatch)
    assert tono_indice < tono_cripto, \
        f"índice debe ser más bajista que cripto: {tono_indice} vs {tono_cripto}"


def test_cripto_inerte_igual_a_accion(monkeypatch):
    """cripto y accion están ambos en 0.0 (inertes): mismo tono."""
    assert abs(_tono_en("cripto", monkeypatch) - _tono_en("accion", monkeypatch)) < 1e-9


def test_override_global_manda_sobre_la_segmentacion(monkeypatch):
    """Con ENJAMBRE_PESO_DOOMER fijado (medición), ese peso aplica en cualquier
    mercado: cripto con override=1 iguala a índice segmentado (peso 1.0)."""
    tono_indice = _tono_en("indice", monkeypatch)  # segmentado, peso 1.0
    monkeypatch.setenv("ENJAMBRE_PESO_DOOMER", "1")
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._umbral_correccion = 0.0
    m.perfil = perfil_de("cripto")
    tono_cripto_forzado = m._tono_de_titular(TITULAR_MALO, _respuestas(m, TITULAR_MALO))
    assert abs(tono_cripto_forzado - tono_indice) < 1e-9, \
        "el override global debe forzar el mismo peso en cualquier mercado"


if __name__ == "__main__":
    import pytest
    print("\n🧪 Segmentación por mercado del doomer")
    print("=" * 45)
    class _MP:
        def delenv(self, k, raising=False): os.environ.pop(k, None)
        def setenv(self, k, v): os.environ[k] = v
    mp = _MP()
    print(f"  tono índice (peso 1.0): {_tono_en('indice', mp):+.4f}")
    print(f"  tono cripto (peso 0.0): {_tono_en('cripto', mp):+.4f}")
    print("=" * 45)
