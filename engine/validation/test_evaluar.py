"""
El endpoint de evaluación (`backtest.evaluar`): mide el acierto de dirección
DIRECTAMENTE sobre los casos ya respaldados (titular + resultado real), bajo el
código/entorno actual, SIN re-respaldar y SIN cruzar con el banco de eventos.
Se prueba con la simulación inyectada (sin LLM ni red).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from contenido import backtest  # noqa: E402


def _caso(sim_id, titular, pct_real, categoria, mercado="cripto"):
    return {"sim_id": sim_id, "titular": titular, "mercado": mercado,
            "reaccion_real": {"pct_real": pct_real, "categoria": categoria}}


def test_evaluar_cuenta_acierto_por_categoria(monkeypatch):
    casos = [
        _caso("aaaa1111bbbb2222", "Crash del mercado", -8.0, "negativa"),
        _caso("cccc3333dddd4444", "Rally histórico", +5.0, "positiva"),
        _caso("eeee5555ffff6666", "Otra caída fuerte", -6.0, "negativa"),
        # un caso sin categoría (en vivo) — debe ignorarse
        {"sim_id": "9999", "titular": "En vivo", "simbolos": "SPY,QQQ",
         "reaccion_real": {"pct_real": 1.0, "categoria": None}},
    ]
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: casos)

    # acierta la 1ª negativa (baja) y la positiva (sube), FALLA la 2ª negativa.
    predicho = {"Crash del mercado": -3.0, "Rally histórico": +2.0,
                "Otra caída fuerte": +4.0}
    def simular(titular, seed):
        assert isinstance(seed, int)  # semilla determinística por caso
        return ({"direccion_pct": predicho[titular]},
                [{"fuente": "api"}], [], None)

    r = backtest.evaluar(simular=simular, guardar=False)
    assert r["evaluados"] == 3           # el caso sin categoría se ignoró
    assert r["con_ia"] == 3 and r["sin_ia"] == 0
    assert r["negativa"] == {"aciertos": 1, "total": 2, "acierto": 0.5}
    assert r["positiva"]["acierto"] == 1.0
    assert r["acierto_global"] == round(2 / 3, 4)
    assert r["diag"]["casos_respaldados"] == 4
    assert r["diag"]["casos_categorizados"] == 3


def test_evaluar_filtra_por_mercado(monkeypatch):
    casos = [
        _caso("aaaa1111bbbb2222", "Cripto malo", -8.0, "negativa", mercado="cripto"),
        _caso("cccc3333dddd4444", "Indice bueno", +5.0, "positiva", mercado="indice"),
    ]
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: casos)
    r = backtest.evaluar(mercado="cripto", simular=lambda t, s: ({"direccion_pct": -1.0}, [], [], None),
                         guardar=False)
    assert r["evaluados"] == 1
    assert r["negativa"]["total"] == 1 and r["positiva"]["total"] == 0


def test_evaluar_respeta_env_de_p2(monkeypatch):
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: [])
    monkeypatch.setenv("ENJAMBRE_PESO_TONO_INVERSORES", "0.3")
    r = backtest.evaluar(simular=lambda t, s: ({}, [], [], None), guardar=False)
    assert r["peso_tono_invertidores"] == 0.3
    assert r["evaluados"] == 0
