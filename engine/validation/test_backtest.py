"""Tests del backtesting histórico (contenido/backtest.py).

Reglas: tandas con freno de presupuesto, casos fuente='backtest' que
JAMÁS son destacadas (no contaminan el muro ni la hemeroteca), reintento
sin datos, libreta separando en vivo vs histórico, y respaldo automático.
"""

import re

import pytest

from contenido import backtest, corrector, persistencia, respaldo


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_RESPALDO_TOKEN", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


def _simulador_falso(titular, seed):
    reporte = {"direccion_pct": -2.0 if "plunge" in titular.lower() or "crash" in titular.lower() else 1.0,
               "volatilidad_pct": 1.0}
    return reporte, [{"arquetipo": "doomer", "senal": -0.5, "confianza": 0.8, "frase": "x"}], [100.0, 99.0], []


def _variacion_falsa(simbolo, fecha, ruedas=2):
    return {"simbolo": simbolo, "pct_real": -1.5, "cierre_base": 100.0, "cierre_final": 98.5,
            "fecha_base": fecha, "fecha_final": fecha, "ruedas": ruedas}


# ---------- la lista de exámenes ----------

def test_eventos_estan_bien_formados_y_balanceados():
    eventos = backtest.cargar_eventos()
    assert len(eventos) >= 30
    ids = [e["id"] for e in eventos]
    assert len(ids) == len(set(ids))  # sin duplicados
    conteo = {"negativa": 0, "positiva": 0, "neutra": 0}
    for e in eventos:
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", e["fecha"])
        assert e["titular"].strip() and e["simbolo"].strip()
        assert e["categoria"] in conteo
        conteo[e["categoria"]] += 1
    # mezcla balanceada (guía de calibración): nada domina, lo neutro existe
    assert conteo["negativa"] >= 10
    assert conteo["positiva"] >= 10
    assert conteo["neutra"] >= 5


# ---------- la tanda ----------

def test_tanda_respeta_el_freno_y_avanza_por_partes():
    conexion = persistencia.conectar()
    r1 = backtest.correr_tanda(conexion, tamano=5, simular=_simulador_falso,
                               obtener_variacion=_variacion_falsa)
    assert len(r1["hechas"]) == 5
    total = backtest.estado(conexion)["total"]
    assert r1["pendientes"] == total - 5

    # la segunda tanda continúa donde quedó (no repite exámenes)
    r2 = backtest.correr_tanda(conexion, tamano=5, simular=_simulador_falso,
                               obtener_variacion=_variacion_falsa)
    ids1 = {h["id"] for h in r1["hechas"]}
    ids2 = {h["id"] for h in r2["hechas"]}
    assert not ids1 & ids2
    assert backtest.estado(conexion)["hechos"] == 10
    conexion.close()


def test_tamano_se_recorta_al_tope_maximo():
    conexion = persistencia.conectar()
    r = backtest.correr_tanda(conexion, tamano=999, simular=_simulador_falso,
                              obtener_variacion=_variacion_falsa)
    conexion.close()
    assert len(r["hechas"]) == backtest.TANDA_MAXIMA  # freno de presupuesto


def test_los_casos_historicos_no_contaminan_el_muro_ni_el_archivo():
    conexion = persistencia.conectar()
    backtest.correr_tanda(conexion, tamano=3, simular=_simulador_falso,
                          obtener_variacion=_variacion_falsa)
    destacadas = conexion.execute(
        "SELECT COUNT(*) FROM simulaciones WHERE destacada = 1"
    ).fetchone()[0]
    fuentes = {f[0] for f in conexion.execute(
        "SELECT DISTINCT fuente FROM simulaciones").fetchall()}
    conexion.close()
    assert destacadas == 0          # el archivo/hemeroteca queda intacto
    assert fuentes == {"backtest"}  # marcados aparte, peras con peras


def test_sin_datos_reintenta_en_la_proxima_tanda():
    conexion = persistencia.conectar()
    r1 = backtest.correr_tanda(conexion, tamano=2, simular=_simulador_falso,
                               obtener_variacion=lambda *a: None)
    assert r1["hechas"] == []
    assert len(r1["sin_datos"]) == 2
    # con datos, esos mismos exámenes se completan
    r2 = backtest.correr_tanda(conexion, tamano=2, simular=_simulador_falso,
                               obtener_variacion=_variacion_falsa)
    conexion.close()
    assert {h["id"] for h in r2["hechas"]} == set(r1["sin_datos"])


# ---------- libreta y caja fuerte ----------

def test_libreta_separa_en_vivo_de_historico():
    conexion = persistencia.conectar()
    # un caso EN VIVO (destacada corregida)
    vivo = persistencia.guardar_simulacion(
        conexion, titular="Caso en vivo", fuente="alpaca", seed=1,
        resumen={"direccion_pct": 2.0, "volatilidad_pct": 1.0},
        lideres=[], serie_precios=[100.0], destacada=True)
    persistencia.guardar_reaccion_real(conexion, vivo, {"pct_real": 1.0})
    # dos casos históricos
    backtest.correr_tanda(conexion, tamano=2, simular=_simulador_falso,
                          obtener_variacion=_variacion_falsa)
    resumen = corrector.libreta(conexion)
    conexion.close()
    assert resumen["casos"] == 3
    assert resumen["en_vivo"]["casos"] == 1
    assert resumen["historico"]["casos"] == 2


def test_el_respaldo_incluye_el_backtest_con_su_origen():
    conexion = persistencia.conectar()
    backtest.correr_tanda(conexion, tamano=2, simular=_simulador_falso,
                          obtener_variacion=_variacion_falsa)
    casos = respaldo.exportar_casos(conexion)
    conexion.close()
    assert len(casos) == 2
    assert all(c["origen"] == "historico" for c in casos)
    assert all(c["simbolos"] for c in casos)  # el símbolo viene de la reacción
    assert all(c["reaccion_real"]["categoria"] in ("negativa", "positiva", "neutra")
               for c in casos)


def test_endpoints_del_backtest_exigen_token(monkeypatch):
    from fastapi.testclient import TestClient

    import server
    from contenido import limites, seguridad

    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    seguridad.reiniciar()
    limites.reiniciar()
    cliente = TestClient(server.app)
    assert cliente.post("/api/backtest").status_code == 403
    assert cliente.get("/api/backtest").status_code == 403
    avance = cliente.get("/api/backtest", headers={"X-Pipeline-Token": "secreto-de-prueba"})
    assert avance.status_code == 200
    assert avance.json()["hechos"] == 0
    assert avance.json()["pendientes"] == avance.json()["total"]
    assert "_lista_pendiente" not in avance.json()
