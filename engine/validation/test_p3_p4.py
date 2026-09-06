"""
P3 — acotar magnitudes absurdas por mercado.
P4 — confianza (fuerza del consenso) en el reporte.

P3: `acotar_magnitud` recorta la MAGNITUD al tope del mercado (cripto ±30,
acción ±40) SIN tocar el signo; los mercados sin tope quedan igual.
P4: al aplicar un titular, el modelo guarda la fuerza del consenso, y el reporte
la expone como `confianza` = abs(consenso) ∈ [0, 1].

Corre local, sin LLM ni red.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import TRANSFORMACIONES, sentimiento_lexico  # noqa: E402
from model import (  # noqa: E402
    FACTORES_LIQUIDEZ, RUTA_CONFIG, MercadoEnjambre, acotar_magnitud,
)

TITULAR_MALO = "Bitcoin tumbles below 23000 after Celsius freezes customer withdrawals"


# ---------- P3 ----------

def test_p3_acota_cripto_conservando_signo():
    """Cripto (tope 30): +45 → +30, −52 → −30; el signo se conserva."""
    assert acotar_magnitud("cripto", 45.0) == 30.0
    assert acotar_magnitud("cripto", -52.0) == -30.0
    assert acotar_magnitud("cripto", 12.0) == 12.0  # dentro del tope, intacto


def test_p3_accion_tiene_tope_mayor():
    assert acotar_magnitud("accion", 55.0) == 40.0
    assert acotar_magnitud("accion", 55.0) > acotar_magnitud("cripto", 55.0)


def test_p3_indice_sin_tope():
    """El índice (base de calibración) no se acota."""
    assert acotar_magnitud("indice", 45.0) == 45.0
    assert acotar_magnitud(None, 999.0) == 999.0


def test_p3_no_toca_valores_dentro_del_rango():
    for m in ("cripto", "accion"):
        tope = FACTORES_LIQUIDEZ[m]
        assert acotar_magnitud(m, tope - 1) == tope - 1
        assert acotar_magnitud(m, -(tope - 1)) == -(tope - 1)


# ---------- P4 ----------

def _respuestas(modelo, titular):
    s = sentimiento_lexico(titular)
    out = []
    for lider in modelo._lideres:
        senal, conf, _ = TRANSFORMACIONES[lider.arquetipo](s, titular)
        out.append({"senal": senal, "confianza": conf, "frase": "", "fuente": "api"})
    return out


def test_p4_guarda_la_fuerza_del_consenso():
    """Tras leer un titular, el modelo guarda abs(consenso) > 0."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    assert m._ultimo_consenso == 0.0  # antes de cualquier noticia
    resp = _respuestas(m, TITULAR_MALO)
    m._tono_de_titular(TITULAR_MALO, resp)
    assert abs(m._ultimo_consenso) > 0.0, "el consenso de una noticia clara no es 0"


def test_p4_confianza_es_abs_del_consenso():
    """La confianza que expondrá el reporte = abs(consenso) ∈ [0, 1]."""
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    resp = _respuestas(m, TITULAR_MALO)
    m._tono_de_titular(TITULAR_MALO, resp)
    confianza = abs(m._ultimo_consenso)
    assert 0.0 <= confianza <= 1.0


if __name__ == "__main__":
    print("\n🧪 P3 (acotar magnitudes) + P4 (confianza)")
    print("=" * 45)
    print(f"  P3 cripto +45 → {acotar_magnitud('cripto', 45.0)}  (tope 30)")
    print(f"  P3 accion +55 → {acotar_magnitud('accion', 55.0)}  (tope 40)")
    print(f"  P3 indice +45 → {acotar_magnitud('indice', 45.0)}  (sin tope)")
    m = MercadoEnjambre(seed=42, ticks_horizonte=5, ruta_config=RUTA_CONFIG)
    m._tono_de_titular(TITULAR_MALO, _respuestas(m, TITULAR_MALO))
    print(f"  P4 confianza (abs consenso): {abs(m._ultimo_consenso):.2f}")
    print("=" * 45)
