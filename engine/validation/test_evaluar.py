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


def _sin_progreso(monkeypatch):
    """Aísla el progreso persistente para que los tests no lo lean/escriban."""
    monkeypatch.setattr(backtest, "_cargar_progreso", lambda: {})
    monkeypatch.setattr(backtest, "_guardar_progreso", lambda p: None)


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
    _sin_progreso(monkeypatch)

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
    _sin_progreso(monkeypatch)
    r = backtest.evaluar(mercado="cripto", simular=lambda t, s: ({"direccion_pct": -1.0}, [], [], None),
                         guardar=False)
    assert r["evaluados"] == 1
    assert r["negativa"]["total"] == 1 and r["positiva"]["total"] == 0


def test_evaluar_resumible_acumula(monkeypatch):
    """Cada corrida hace a lo sumo una tanda y ACUMULA; re-correr avanza."""
    casos = [_caso(f"{i:016x}", f"titular {i}", -5.0, "negativa") for i in range(5)]
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: casos)
    prog: dict = {}
    monkeypatch.setattr(backtest, "_cargar_progreso", lambda: prog)
    monkeypatch.setattr(backtest, "_guardar_progreso", lambda p: prog.update(p))
    monkeypatch.setattr(backtest, "TANDA_EVAL_MAX", 2)  # tanda de 2 para el test
    sim = lambda t, s: ({"direccion_pct": -1.0}, [{"fuente": "api"}], [], None)

    r1 = backtest.evaluar(mercado="cripto", simular=sim)
    assert r1["progreso"]["hechos"] == 2 and r1["progreso"]["faltan"] == 3
    r2 = backtest.evaluar(mercado="cripto", simular=sim)
    assert r2["progreso"]["hechos"] == 4
    r3 = backtest.evaluar(mercado="cripto", simular=sim)
    assert r3["progreso"]["hechos"] == 5 and r3["progreso"]["completo"] is True
    # todas negativas y todas aciertan (sim baja, real baja)
    assert r3["negativa"] == {"aciertos": 5, "total": 5, "acierto": 1.0}


def test_evaluar_respeta_env_de_p2(monkeypatch):
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: [])
    _sin_progreso(monkeypatch)
    monkeypatch.setenv("ENJAMBRE_PESO_TONO_INVERSORES", "0.3")
    r = backtest.evaluar(simular=lambda t, s: ({}, [], [], None), guardar=False)
    assert r["peso_tono_invertidores"] == 0.3
    assert r["evaluados"] == 0
