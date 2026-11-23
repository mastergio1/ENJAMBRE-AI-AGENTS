"""Tests del resolvedor de predicciones (Fase 7-mínima). Sin red (fetch mockeado)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido import persistencia as p
from contenido import resolver_predicciones as rp


@pytest.fixture
def con(tmp_path):
    return p.conectar(tmp_path / "test.db")


def _barras_suben(sim, fecha):
    return [("2026-03-02", 100.0), ("2026-03-03", 101.0),
            ("2026-03-04", 103.0), ("2026-03-05", 104.0)]


def test_resuelve_las_maduras(con):
    p.registrar_prediccion(con, titular="x", simbolo="SPY", horizonte=2,
                           direccion="alza", mercado="indice",
                           as_of_iso="2026-03-02T12:00:00+00:00")
    res = rp.resolver_pendientes(con, fetch=_barras_suben)
    assert res["resueltas"] == 1
    fila = p.listar_predicciones(con)[0]
    assert fila["direccion_real"] == "alza" and fila["acierto"] == 1


def test_no_madura_queda_pendiente(con):
    p.registrar_prediccion(con, titular="x", simbolo="SPY", horizonte=5,  # pide 5 ruedas
                           direccion="alza", mercado="indice",
                           as_of_iso="2026-03-02T12:00:00+00:00")
    # solo hay 4 barras → no alcanza para 5 ruedas → aún verde, no resuelta
    res = rp.resolver_pendientes(con, fetch=_barras_suben)
    assert res["resueltas"] == 0 and res["aun_verdes"] == 1


def test_sin_datos_no_rompe(con):
    p.registrar_prediccion(con, titular="x", simbolo="ZZZ", horizonte=2,
                           direccion="alza", as_of_iso="2026-03-02T12:00:00+00:00")
    res = rp.resolver_pendientes(con, fetch=lambda s, f: None)
    assert res["resueltas"] == 0 and res["sin_datos"] == 1


def test_pct_resolucion_toma_primera_sesion_posterior():
    # as_of sábado: entra en la primera sesión POSTERIOR, no exige barra del sábado
    barras = [("2026-11-20", 100.0), ("2026-11-23", 101.0),
              ("2026-11-24", 102.0), ("2026-11-25", 103.0)]
    pct = rp.pct_resolucion(barras, "2026-11-21", 2)  # sábado → entra el lunes (101)
    assert pct is not None and round(pct, 2) == round((103 - 101) / 101 * 100, 2)


def test_resuelve_aunque_as_of_sea_fin_de_semana(con):
    # P0-04: una noticia con as_of de sábado DEBE resolverse (antes daba None eterno)
    p.registrar_prediccion(con, titular="x", simbolo="SPY", horizonte=2,
                           direccion="alza", mercado="indice",
                           as_of_iso="2026-11-21T12:00:00+00:00")  # sábado

    def barras(sim, fecha):
        return [("2026-11-20", 100.0), ("2026-11-23", 101.0),
                ("2026-11-24", 102.0), ("2026-11-25", 103.0)]

    res = rp.resolver_pendientes(con, fetch=barras)
    assert res["resueltas"] == 1
    assert p.listar_predicciones(con)[0]["direccion_real"] == "alza"
