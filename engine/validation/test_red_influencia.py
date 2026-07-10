"""Tests de la red de influencia (CLAUDE.md sección 6)."""

import pytest

from agents.lider import LiderOpinion
from agents.reglas import FomoRetail, FondoPasivo, Fundamentalista, Manada, Miedoso, QuantMomentum
from model import MercadoEnjambre


@pytest.fixture(scope="module")
def modelo():
    return MercadoEnjambre(seed=42, ticks_horizonte=300)


def test_lideres_tienen_seguidores_segun_arquetipo(modelo):
    """Cada líder arrastra entre 20 y ~150 seguidores (más los mínimos
    garantizados de manada/FOMO que exige la sección 4)."""
    lideres = [a for a in modelo.agents if isinstance(a, LiderOpinion)]
    assert len(lideres) == 100
    for lider in lideres:
        assert len(lider.seguidores) >= 20


def test_red_scale_free_pocos_hubs(modelo):
    """Pocos nodos muy conectados, muchos poco conectados."""
    lideres = [a for a in modelo.agents if isinstance(a, LiderOpinion)]
    seguidores = sorted((len(l.seguidores) for l in lideres), reverse=True)
    top10 = sum(seguidores[:10])
    total = sum(seguidores)
    assert top10 / total > 0.15  # el 10% más popular concentra audiencia


def test_retail_tiene_pares_horizontales(modelo):
    """Los tipos 8-10 tienen al menos 3 vecinos pares (el rumor viaja
    también horizontalmente)."""
    for clase in (Manada, FomoRetail, Miedoso):
        for agente in (a for a in modelo.agents if isinstance(a, clase)):
            assert len(agente.pares) >= 3


def test_manada_siempre_tiene_un_lider(modelo):
    for agente in (a for a in modelo.agents if isinstance(a, Manada)):
        assert len(agente.lideres_seguidos) >= 1


def test_institucionales_fuera_de_la_red(modelo):
    """Los tipos 1-3 NO están en la red social: sin vecinos, sin rumor."""
    for clase in (Fundamentalista, QuantMomentum, FondoPasivo):
        for agente in (a for a in modelo.agents if isinstance(a, clase)):
            assert agente.vecinos == []
            assert agente.lideres_seguidos == []


def test_propagacion_con_retardo_y_atenuacion():
    """La señal llega a los seguidores con delay de 1-4 ticks y atenuada
    (0.7 por salto) — sin retardo no hay ola, solo un salto feo."""
    modelo = MercadoEnjambre(seed=7, ticks_horizonte=300)
    modelo.aplicar_noticia(-0.9)

    # nada llega en el mismo tick de la noticia: todo va a la cola
    assert all(a.senal_social == 0.0 for a in modelo.agents)
    assert len(modelo.cola_senales) > 1000

    # cada envío en la cola respeta retardo 1-4 y atenuación 0.7 por salto
    for tick_entrega, _, valor, salto in modelo.cola_senales:
        assert 1 <= tick_entrega - modelo.tick <= 4
        assert abs(valor) <= 0.7**salto + 1e-9
        assert salto == 1  # el segundo salto se encola recién al entregar

    alcanzados_por_tick = []
    for _ in range(6):
        modelo.step()
        alcanzados = [a for a in modelo.agents if a.senal_social != 0.0]
        alcanzados_por_tick.append(len(alcanzados))

    # la ola crece durante los primeros ticks (retardo distribuido 1-4)
    assert alcanzados_por_tick[0] > 0
    assert alcanzados_por_tick[3] > alcanzados_por_tick[0]

    # el rumor acumulado queda acotado y es coherente con la noticia
    assert all(abs(a.senal_social) <= 1.0 for a in modelo.agents)
    negativos = sum(1 for a in modelo.agents if a.senal_social < 0)
    positivos = sum(1 for a in modelo.agents if a.senal_social > 0)
    assert negativos > positivos * 3
