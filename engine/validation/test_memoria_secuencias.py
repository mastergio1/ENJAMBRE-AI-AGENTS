"""
Validación de la memoria de agentes en SECUENCIAS de noticias (Nivel 1).

Mide, de forma honesta, si la memoria AMORTIGUA el pánico ante rachas de 3+
malas noticias — aislando el efecto con una comparación A/B (memoria ON vs OFF)
sobre la MISMA secuencia y semilla. Comparar solo "la 4ª caída vs la 3ª" no
sirve: mezcla el efecto de la memoria con la acumulación/decaimiento del
sentimiento del propio modelo.

Corre local, sin LLM ni red. (Import estilo proyecto: `from model import …`,
con engine/ en el path vía conftest.py o el sys.path de abajo.)
"""

import os
import sys
from contextlib import contextmanager

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from agents.base import AgenteBase   # noqa: E402
from model import RUTA_CONFIG, MercadoEnjambre  # noqa: E402

SECUENCIA = [-0.5, -0.5, -0.5, -0.5, 0.5]   # 4 malas seguidas + 1 buena
TICKS_POR_NOTICIA = 20
SEEDS = [42, 7, 123]


@contextmanager
def _memoria_desactivada():
    """Desactiva SOLO el ajuste por contexto (deja el motor idéntico en todo lo
    demás), para el brazo OFF del A/B."""
    original = AgenteBase.ajustar_por_contexto
    AgenteBase.ajustar_por_contexto = lambda self, x: x
    try:
        yield
    finally:
        AgenteBase.ajustar_por_contexto = original


def _caidas_de_secuencia(seed: int) -> list[float]:
    """Corre la secuencia y devuelve el cambio de precio tras cada noticia."""
    m = MercadoEnjambre(seed=seed, precio_inicial=100.0,
                        ticks_horizonte=len(SECUENCIA) * TICKS_POR_NOTICIA + 5,
                        ruta_config=RUTA_CONFIG)
    precios = [m.historial_precios[-1]]
    for sent in SECUENCIA:
        m.aplicar_noticia(sentimiento=sent)
        for _ in range(TICKS_POR_NOTICIA):
            m.step()
        precios.append(m.historial_precios[-1])
    return [p2 - p1 for p1, p2 in zip(precios, precios[1:])]


def _drop_4a_mala(seed: int, memoria_on: bool) -> float:
    """La caída tras la 4ª mala noticia (índice 3), cuando la cautela YA está
    activa (se dispara con la 3ª). Con memoria ON debería ser MENOS negativa."""
    if memoria_on:
        return _caidas_de_secuencia(seed)[3]
    with _memoria_desactivada():
        return _caidas_de_secuencia(seed)[3]


@pytest.mark.xfail(
    reason="Resultado NEGATIVO documentado: la memoria de PERCEPCIÓN "
    "(ajustar_por_contexto sobre miedoso/noise) NO amortigua el pánico — el "
    "A/B mostró que no reduce la 4ª caída. La palanca que SÍ funciona es el "
    "freno de la manada (test_freno_manada.py). Se conserva como evidencia del "
    "experimento; ver INFORME_NIVEL1_RESULTADO.md e INFORME_FRENO_MANADA.md.",
    strict=False,
)
def test_memoria_amortigua_el_panico():
    """A/B: sobre las mismas semillas, la 4ª mala cae MENOS con memoria ON.

    Falla esperada (xfail): la memoria de percepción NO amortigua — el propósito
    lo cumple el freno de la manada, no este mecanismo. Ver el docstring del
    marcador xfail de arriba."""
    on = [_drop_4a_mala(s, memoria_on=True) for s in SEEDS]
    off = [_drop_4a_mala(s, memoria_on=False) for s in SEEDS]
    media_on = sum(on) / len(on)
    media_off = sum(off) / len(off)
    print(f"\n4ª mala — caída media  ON: {media_on:+.3f} · OFF: {media_off:+.3f}")
    print(f"  por semilla ON : {[round(x,3) for x in on]}")
    print(f"  por semilla OFF: {[round(x,3) for x in off]}")
    # amortiguación: la caída con memoria es menos profunda (menos negativa)
    assert media_on > media_off, "La memoria NO amortiguó (ON no cae menos que OFF)"


def test_cautela_se_activa_en_racha():
    """La cautela se dispara tras 3 malas y NO antes."""
    m = MercadoEnjambre(seed=1, ticks_horizonte=30, ruta_config=RUTA_CONFIG)
    mie = next(a for a in m.agents if type(a).__name__ == "Miedoso")
    assert not mie.modo_cautela
    m.aplicar_noticia(-0.5); m.aplicar_noticia(-0.5)
    assert not mie.modo_cautela, "cautela no debe activarse con 2 malas"
    m.aplicar_noticia(-0.5)
    assert mie.modo_cautela, "cautela debe activarse con 3 malas"


if __name__ == "__main__":
    print("\n🧪 Validación de Memoria en Secuencias (A/B)")
    print("=" * 55)
    test_cautela_se_activa_en_racha()
    print("✅ La cautela se activa con 3 malas (y no antes).")
    try:
        test_memoria_amortigua_el_panico()
        print("✅ La memoria AMORTIGUA el pánico (ON cae menos que OFF).")
    except AssertionError as e:
        print(f"⚠️ {e}")
    print("=" * 55)
    print("Nota: los hechos estilizados con memoria ya se validaron aparte "
          "(test_hechos_estilizados.py → 9 passed).")
