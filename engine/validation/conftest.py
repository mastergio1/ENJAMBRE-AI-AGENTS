"""Configuración compartida de los tests.

Neutraliza la fuente de "movers" de Yahoo: los tests NO deben salir a la red por
los mayores movimientos del día (haría al pipeline lento y no determinista). Los
tests del reportero IA (test_investigador) prueban su lógica con datos explícitos.
"""

import pytest


@pytest.fixture(autouse=True)
def _sin_movers_de_red(monkeypatch):
    try:
        monkeypatch.setattr("contenido.fuentes.yahoo.movers_del_dia", lambda **k: [])
    except Exception:
        pass
