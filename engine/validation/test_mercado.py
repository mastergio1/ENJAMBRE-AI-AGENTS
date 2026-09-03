"""Tests de la clasificación por tipo de mercado y sus perfiles (Fase 1).

El enjambre razona de qué mercado habla la noticia (índice, acción,
petróleo, oro, cripto) y aplica su personalidad: el oro sube con el miedo,
el cripto amplifica todo, cada mercado reacciona a su manera.
"""

import pytest

from brains import mercado
from model import MercadoEnjambre


@pytest.fixture(autouse=True)
def sin_api(monkeypatch):
    # los tests no llaman a la IA: se prueba el clasificador léxico
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


# ---------- clasificación léxica (fallback sin IA) ----------

def test_clasifica_por_palabras_clave():
    assert mercado.clasificar_lexico("Bitcoin surges past $100,000") == "cripto"
    assert mercado.clasificar_lexico("Nvidia earnings smash expectations") == "accion"
    # una noticia macro amplia cae en índice (el perfil por defecto)
    assert mercado.clasificar_lexico("La Fed sube las tasas 50 puntos base") == "indice"


def test_oro_y_petroleo_en_pausa_caen_a_indice():
    """Foco del producto: SP500 + acciones + cripto. Oro y petróleo están en
    pausa → sus noticias se tratan con el perfil por defecto (índice), no con
    su dial propio (que se conserva para reactivar)."""
    assert mercado.clasificar_lexico("Oro alcanza máximo histórico como refugio") == "indice"
    assert mercado.clasificar_lexico("Oil prices spike as OPEC cuts output") == "indice"
    assert "oro" not in mercado.MERCADOS_ACTIVOS
    assert "petroleo" not in mercado.MERCADOS_ACTIVOS
    # los diales calibrados se conservan (para reactivar sin recalibrar)
    assert mercado.perfil_de("oro")["refugio"] == 0.25


def test_clasificar_sin_api_usa_el_lexico():
    # sin ANTHROPIC_API_KEY, clasificar() no llama afuera
    assert mercado.clasificar("Ethereum crashes 20% overnight") == "cripto"


def test_perfil_de_devuelve_defecto_para_tipo_desconocido():
    p = mercado.perfil_de("no-existe")
    assert p["tipo"] == "indice"
    assert p["sensibilidad"] == 1.0


# ---------- el perfil cambia la reacción del enjambre ----------

def _reaccion(perfil_tipo: str, tono: float, seed: int = 7) -> float:
    """Corre una simulación breve con un tono dado bajo un perfil y devuelve
    la dirección del precio (%)."""
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=200)
    modelo.correr(60)  # calentamiento
    base = modelo.historial_precios[-1]
    modelo.perfil = mercado.perfil_de(perfil_tipo)
    # inyecta el tono directamente por el mismo camino que una noticia real
    modelo.sentimiento = modelo._aplicar_perfil(tono)
    for _ in range(120):
        modelo.step()
    return (modelo.historial_precios[-1] - base) / base * 100


def test_los_metales_resisten_el_miedo():
    """Refugio parcial: ante un tono NEGATIVO (miedo), los metales (oro+plata+
    cobre) caen MUCHO MENOS que el índice — el oro los sostiene en parte —,
    aunque el cobre/plata no lo invierten del todo. Se compara el tono efectivo."""
    indice = mercado.perfil_de("indice")
    oro = mercado.perfil_de("oro")
    modelo = MercadoEnjambre(seed=1, ticks_horizonte=10)
    modelo.perfil = indice
    tono_indice = modelo._aplicar_perfil(-0.6)
    modelo.perfil = oro
    tono_oro = modelo._aplicar_perfil(-0.6)
    assert tono_indice < 0                          # el índice cae con el miedo
    assert tono_oro > tono_indice                   # los metales resisten…
    assert abs(tono_oro) < abs(tono_indice) * 0.7   # …caen bastante menos (refugio parcial)


def test_el_cripto_amplifica_el_movimiento():
    """Mayor sensibilidad: un mismo tono positivo mueve más al cripto."""
    modelo = MercadoEnjambre(seed=1, ticks_horizonte=10)
    modelo.perfil = mercado.perfil_de("indice")
    t_indice = modelo._aplicar_perfil(0.5)
    modelo.perfil = mercado.perfil_de("cripto")
    t_cripto = modelo._aplicar_perfil(0.5)
    assert t_cripto > t_indice             # el cripto exagera la euforia


def test_aplicar_titular_acepta_y_guarda_el_perfil():
    modelo = MercadoEnjambre(seed=3, ticks_horizonte=180)
    modelo.correr(60)
    perfil = mercado.perfil_de("petroleo")
    respuestas = [{"senal": 0.0, "confianza": 0.5, "frase": "x", "fuente": "fallback"}
                  for _ in modelo._lideres]
    modelo.aplicar_titular("Oil jumps on supply fears", respuestas=respuestas, perfil=perfil)
    assert modelo.perfil["tipo"] == "petroleo"


def test_v1c_silencia_ambiente_y_los_lideres_hablan(monkeypatch):
    """Anti-v1a: el tono de fondo se apaga si es tibio; los líderes no."""
    from brains import impacto

    monkeypatch.setenv("ENJAMBRE_PERILLAS", "hipotesis_v1c")
    impacto.reiniciar_cache()
    modelo = MercadoEnjambre(seed=5, ticks_horizonte=10)
    modelo.aplicar_noticia(0.20)  # por debajo del umbral 0.25
    assert modelo.sentimiento == pytest.approx(0.0)
    hablan = sum(1 for l in modelo._lideres if abs(l.senal) > 0.05)
    assert hablan > 0
    monkeypatch.delenv("ENJAMBRE_PERILLAS", raising=False)
    impacto.reiniciar_cache()
