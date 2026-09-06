"""Configuración de pytest para las dos tandas (mejora C7).

Marca como `lento` —en un solo lugar, por nombre de archivo— los módulos de
prueba que levantan simulaciones de mercado completas. Así:

    pytest -m "not lento"   → tanda rápida (~1 min), a cada rato
    pytest                  → tanda completa, antes de desplegar y en CI

Para sumar un módulo a la tanda lenta, basta agregar su archivo a LENTOS.
"""

import pytest

# módulos que corren el mercado completo (10.000 agentes, ~150 latidos)
LENTOS = {
    "test_hechos_estilizados.py",
    "test_pulso.py",
    "test_mercado.py",
    "test_duelo.py",
    "test_observatorio.py",
    "test_muro.py",
    "test_archivo.py",
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        archivo = getattr(item, "path", None)
        nombre = archivo.name if archivo is not None else ""
        if nombre in LENTOS:
            item.add_marker(pytest.mark.lento)
