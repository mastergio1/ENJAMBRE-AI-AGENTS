"""Tests del reparto de cerebros (brains/reparto.py).

La regla sagrada (CLAUDE.md §2.7): ~100-120 llamadas a la IA por
simulación. Con 1000 líderes, el reparto debe mantenerse en ese techo,
cubrir a TODOS los líderes, y respetar el arquetipo de cada uno.
"""

from brains import reparto


class _Lider:
    def __init__(self, uid, arquetipo):
        self.unique_id = uid
        self.arquetipo = arquetipo


def _mil_lideres():
    arquetipos = ["institucional_frio"] * 150 + ["quant_esceptico"] * 100 + \
                 ["fomo_evangelista"] * 150 + ["doomer"] * 150 + \
                 ["contrarian_sabio"] * 100 + ["macro_trader"] * 100 + \
                 ["influencer_optimista"] * 150 + ["value_paciente"] * 100
    return [_Lider(i, a) for i, a in enumerate(arquetipos)]


def test_mil_lideres_no_superan_el_presupuesto():
    lideres = _mil_lideres()
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    assert len(lideres) == 1000
    # el techo de la biblia: nunca más de ~120 llamadas a la IA
    assert len(consultas) <= 120
    assert len(consultas) >= 60  # pero sí suficientes para variedad de frases


def test_cada_lider_recibe_un_cerebro_de_su_arquetipo():
    lideres = _mil_lideres()
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    assert len(asignacion) == len(lideres)
    for i, lider in enumerate(lideres):
        cerebro_idx = asignacion[i]
        assert 0 <= cerebro_idx < len(consultas)
        # el cerebro asignado es del MISMO arquetipo que el líder
        assert consultas[cerebro_idx][1] == lider.arquetipo


def test_expandir_devuelve_una_respuesta_por_lider():
    lideres = _mil_lideres()
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    respuestas_cerebros = [{"senal": i / 100, "confianza": 0.5, "frase": f"c{i}"}
                           for i in range(len(consultas))]
    expandidas = reparto.expandir(respuestas_cerebros, asignacion)
    assert len(expandidas) == 1000
    # cada líder recibe exactamente la respuesta de su cerebro
    for i in range(len(lideres)):
        assert expandidas[i] is respuestas_cerebros[asignacion[i]]


def test_pocos_lideres_es_uno_a_uno_como_antes():
    """Con pocos líderes (por debajo del objetivo) cada uno es su propio cerebro."""
    lideres = [_Lider(i, "doomer") for i in range(50)]
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    assert len(consultas) == 50
    assert sorted(asignacion) == list(range(50))
