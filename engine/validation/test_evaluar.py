"""
El endpoint de evaluación (`backtest.evaluar`): mide el acierto de dirección
sobre los exámenes ya respaldados, bajo el código/entorno actual, SIN re-
respaldar. Se prueba con la simulación inyectada (sin LLM ni red).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from contenido import backtest, persistencia  # noqa: E402


def _evento(id_, titular, fecha, categoria):
    return {"id": id_, "titular": titular, "fecha": fecha,
            "simbolo": "SPY", "categoria": categoria}


def _caso(titular, fecha, pct_real, categoria):
    seed = int(fecha.replace("-", ""))
    return {"sim_id": persistencia.id_simulacion(titular, seed),
            "reaccion_real": {"pct_real": pct_real, "categoria": categoria}}


def test_evaluar_cuenta_acierto_por_categoria(monkeypatch):
    eventos = [
        _evento("e1", "Crash del mercado", "2020-03-12", "negativa"),
        _evento("e2", "Rally histórico", "2021-11-08", "positiva"),
        _evento("e3", "Otra caída fuerte", "2022-06-13", "negativa"),
    ]
    casos = [
        _caso("Crash del mercado", "2020-03-12", -8.0, "negativa"),
        _caso("Rally histórico", "2021-11-08", +5.0, "positiva"),
        _caso("Otra caída fuerte", "2022-06-13", -6.0, "negativa"),
    ]
    monkeypatch.setattr(backtest, "cargar_eventos", lambda: eventos)
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: casos)

    # simulación inyectada: acierta la 1ª negativa (baja) y la positiva (sube),
    # pero FALLA la 2ª negativa (predice subir). Líderes con fuente 'api'.
    predicho = {"Crash del mercado": -3.0, "Rally histórico": +2.0,
                "Otra caída fuerte": +4.0}
    def simular(titular, seed):
        return ({"direccion_pct": predicho[titular]},
                [{"fuente": "api"}], [], None)

    r = backtest.evaluar(simular=simular, guardar=False)
    assert r["evaluados"] == 3
    assert r["con_ia"] == 3 and r["sin_ia"] == 0
    # negativas: 1 de 2 (acertó el crash, falló la otra) = 0.5
    assert r["negativa"] == {"aciertos": 1, "total": 2, "acierto": 0.5}
    # positivas: 1 de 1 = 1.0
    assert r["positiva"]["acierto"] == 1.0
    # global: 2 de 3
    assert r["acierto_global"] == round(2 / 3, 4)
    # reporta la perilla P2 vigente
    assert "peso_tono_invertidores" in r


def test_evaluar_respeta_env_de_p2(monkeypatch):
    monkeypatch.setattr(backtest, "cargar_eventos", lambda: [])
    from contenido import respaldo
    monkeypatch.setattr(respaldo, "casos_remotos", lambda: [])
    monkeypatch.setenv("ENJAMBRE_PESO_TONO_INVERSORES", "0.3")
    r = backtest.evaluar(simular=lambda t, s: ({}, [], [], None), guardar=False)
    assert r["peso_tono_invertidores"] == 0.3
    assert r["evaluados"] == 0
