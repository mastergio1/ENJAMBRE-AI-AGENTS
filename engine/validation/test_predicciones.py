"""Tests del registro prospectivo de predicciones (Fase 7-mínima). Sin red."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido import persistencia as p


@pytest.fixture
def con(tmp_path):
    return p.conectar(tmp_path / "test.db")


def test_registrar_y_resolver_acierto(con):
    pid = p.registrar_prediccion(con, titular="Fed sube tasas", simbolo="SPY",
                                 horizonte=2, direccion="baja", mercado="indice")
    assert p.resolver_prediccion(con, pid, -1.8) is True
    fila = p.listar_predicciones(con)[0]
    assert fila["direccion_real"] == "baja" and fila["acierto"] == 1


def test_resolver_fallo(con):
    pid = p.registrar_prediccion(con, titular="x", simbolo="QQQ", horizonte=2,
                                 direccion="alza", mercado="indice")
    p.resolver_prediccion(con, pid, -2.0)  # predijo alza, bajó → fallo
    assert p.listar_predicciones(con)[0]["acierto"] == 0


def test_movimiento_neutro_no_puntua(con):
    pid = p.registrar_prediccion(con, titular="x", simbolo="SPY", horizonte=2,
                                 direccion="alza", mercado="indice")
    p.resolver_prediccion(con, pid, 0.1)  # |0.1| < zona 0.3 → neutro
    fila = p.listar_predicciones(con)[0]
    assert fila["direccion_real"] == "neutra" and fila["acierto"] is None


def test_abstencion_no_puntua(con):
    pid = p.registrar_prediccion(con, titular="x", simbolo="SPY", horizonte=2,
                                 direccion="neutra", abstenido=True, mercado="indice")
    p.resolver_prediccion(con, pid, 2.0)
    assert p.listar_predicciones(con)[0]["acierto"] is None


def test_inmutabilidad_registro(con):
    # registrar dos veces la MISMA predicción no la sobrescribe
    pid1 = p.registrar_prediccion(con, titular="x", simbolo="SPY", horizonte=2,
                                  direccion="alza", as_of_iso="2026-01-01T00:00:00+00:00")
    pid2 = p.registrar_prediccion(con, titular="x", simbolo="SPY", horizonte=2,
                                  direccion="baja", as_of_iso="2026-01-01T00:00:00+00:00")
    assert pid1 == pid2
    assert p.listar_predicciones(con)[0]["direccion"] == "alza"  # la primera manda


def test_doble_resolucion_rechazada(con):
    pid = p.registrar_prediccion(con, titular="x", simbolo="SPY", horizonte=2,
                                 direccion="alza", mercado="indice")
    assert p.resolver_prediccion(con, pid, 2.0) is True
    assert p.resolver_prediccion(con, pid, -9.0) is False  # ya resuelta, no cambia
    assert p.listar_predicciones(con)[0]["pct_real"] == 2.0


def test_por_resolver_filtra_resueltas(con):
    pid = p.registrar_prediccion(con, titular="a", simbolo="SPY", horizonte=2,
                                 direccion="alza", mercado="indice")
    p.registrar_prediccion(con, titular="b", simbolo="QQQ", horizonte=2,
                           direccion="baja", mercado="indice")
    assert len(p.predicciones_por_resolver(con)) == 2
    p.resolver_prediccion(con, pid, 1.0)
    assert len(p.predicciones_por_resolver(con)) == 1


def test_resumen_cobertura_y_acierto(con):
    # 2 puntuables (1 acierto, 1 fallo), 1 neutra (no puntúa)
    a = p.registrar_prediccion(con, titular="a", simbolo="SPY", horizonte=2, direccion="alza", mercado="indice")
    b = p.registrar_prediccion(con, titular="b", simbolo="QQQ", horizonte=2, direccion="baja", mercado="indice")
    d = p.registrar_prediccion(con, titular="d", simbolo="DIA", horizonte=2, direccion="alza", mercado="indice")
    p.resolver_prediccion(con, a, 2.0)    # acierto
    p.resolver_prediccion(con, b, 2.0)    # fallo (predijo baja)
    p.resolver_prediccion(con, d, 0.0)    # neutra, no puntúa
    r = p.resumen_predicciones(con, "indice")
    assert r["resueltas"] == 3 and r["puntuables"] == 2 and r["acierto"] == 50.0


def test_resumen_cuenta_mas_de_500(con):
    # P1-09: el tablero debe contar sobre el universo COMPLETO, no truncar a 500
    for i in range(501):
        p.registrar_prediccion(con, titular=f"noticia-{i}", simbolo="SPY", horizonte=2,
                               direccion="alza", mercado="indice")
    assert p.resumen_predicciones(con, "indice")["total"] == 501
