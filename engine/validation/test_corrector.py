"""Tests del corrector automático — paso 2 de la ruta de calibración.

El corrector guarda cuánto se movió DE VERDAD el símbolo de cada
destacada (Alpaca) y redacta el epílogo educativo si no hay uno manual.
La libreta de calificaciones resume enjambre vs mercado real.
"""

from datetime import datetime, timedelta, timezone

import pytest

from contenido import corrector, persistencia, vocabulario
from contenido.fuentes import alpaca


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


def _variacion(pct: float):
    """Una función de variación falsa (no toca la red)."""
    def obtener(simbolo, desde_iso, ruedas=2):
        return {"simbolo": simbolo, "pct_real": pct, "cierre_base": 100.0,
                "cierre_final": round(100.0 * (1 + pct / 100), 2),
                "fecha_base": "2026-07-10", "fecha_final": "2026-07-14", "ruedas": ruedas}
    return obtener


def _destacada(conexion, titular: str, direccion_pct: float, simbolos: str,
               hace_dias: int = 3, epilogo: str | None = None) -> str:
    """Crea una destacada vinculada a un titular, con fecha retrocedida."""
    sim_id = persistencia.guardar_simulacion(
        conexion, titular=titular, fuente="test", seed=hash(titular) % 1000,
        resumen={"direccion_pct": direccion_pct, "volatilidad_pct": 1.0},
        lideres=[], serie_precios=[100.0], destacada=True,
    )
    persistencia.registrar_titular(
        conexion, titular=titular, fuente="test", veredicto="simular",
        simbolos=simbolos, sim_id=sim_id,
    )
    fecha = (datetime.now(timezone.utc) - timedelta(days=hace_dias)).isoformat(timespec="seconds")
    conexion.execute("UPDATE simulaciones SET fecha = ? WHERE id = ?", (fecha, sim_id))
    if epilogo:
        persistencia.guardar_epilogo(conexion, sim_id, epilogo)
    conexion.commit()
    return sim_id


def test_corrige_y_redacta_epilogo_publicable():
    conexion = persistencia.conectar()
    sim_id = _destacada(conexion, "Banco X colapsa", -3.2, "BX,KRE")
    resultado = corrector.corregir_pendientes(conexion, obtener_variacion=_variacion(-1.8))
    datos = persistencia.obtener_simulacion(conexion, sim_id)
    conexion.close()

    assert [c["sim_id"] for c in resultado["corregidas"]] == [sim_id]
    assert resultado["corregidas"][0]["simbolo"] == "BX"  # el símbolo del hecho

    assert datos["reaccion_real"]["pct_real"] == -1.8
    # el epílogo automático existe, menciona lo esencial y es CMF-limpio
    assert "BX" in datos["epilogo"]
    assert "-1.8%" in datos["epilogo"]
    assert vocabulario.es_publicable(datos["epilogo"])


def test_no_pisa_el_epilogo_manual():
    conexion = persistencia.conectar()
    sim_id = _destacada(conexion, "Petróleo sube fuerte", 2.0, "USO",
                        epilogo="Nota manual de Giorgio.")
    corrector.corregir_pendientes(conexion, obtener_variacion=_variacion(1.1))
    datos = persistencia.obtener_simulacion(conexion, sim_id)
    conexion.close()
    # lo manual manda; la reacción real igual queda registrada
    assert datos["epilogo"] == "Nota manual de Giorgio."
    assert datos["reaccion_real"]["pct_real"] == 1.1


def test_respeta_la_espera_y_reintenta_sin_datos():
    conexion = persistencia.conectar()
    _destacada(conexion, "Noticia de hoy mismo", 1.0, "SPY", hace_dias=0)
    vieja = _destacada(conexion, "Noticia de hace días", 1.0, "QQQ", hace_dias=3)

    # la reciente no se toca; la vieja espera si Alpaca aún no tiene datos
    sin_datos = corrector.corregir_pendientes(conexion, obtener_variacion=lambda *a: None)
    assert sin_datos == {"corregidas": [], "esperando": 1}

    # la próxima corrida sí la corrige (nada quedó marcado a medias)
    con_datos = corrector.corregir_pendientes(conexion, obtener_variacion=_variacion(0.5))
    conexion.close()
    assert [c["sim_id"] for c in con_datos["corregidas"]] == [vieja]


def test_texto_del_epilogo_es_publicable_en_toda_direccion():
    variacion = _variacion(-2.5)("XYZ", "2026-07-10")
    for pct_sim in (-4.0, 0.0, 3.5):
        texto = corrector._texto_epilogo(pct_sim, variacion)
        assert vocabulario.es_publicable(texto), texto


def test_libreta_cuenta_aciertos_de_direccion():
    conexion = persistencia.conectar()
    a = _destacada(conexion, "Caso acierto", 2.0, "AAA")   # enjambre ▲, real ▲
    b = _destacada(conexion, "Caso fallo", -2.0, "BBB")    # enjambre ▼, real ▲
    persistencia.guardar_reaccion_real(conexion, a, {"pct_real": 1.5})
    persistencia.guardar_reaccion_real(conexion, b, {"pct_real": 1.5})
    resumen = corrector.libreta(conexion)
    conexion.close()
    assert resumen["casos"] == 2
    assert resumen["aciertos_direccion"] == 1
    assert resumen["tasa_acierto"] == 0.5
    assert resumen["magnitud_media_sim"] == 2.0


def test_variacion_real_sin_claves_devuelve_none():
    assert alpaca.variacion_real("SPY", "2026-07-10") is None


def test_endpoints_del_corrector_exigen_token(monkeypatch):
    from fastapi.testclient import TestClient

    import server
    from contenido import limites, seguridad

    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    seguridad.reiniciar()
    limites.reiniciar()
    cliente = TestClient(server.app)
    assert cliente.post("/api/corrector").status_code == 403
    assert cliente.get("/api/libreta").status_code == 403
    # con token: el corrector responde (sin claves de Alpaca, todo espera)
    ok = cliente.post("/api/corrector", headers={"X-Pipeline-Token": "secreto-de-prueba"})
    assert ok.status_code == 200
    assert "corregidas" in ok.json()
    libreta = cliente.get("/api/libreta", headers={"X-Pipeline-Token": "secreto-de-prueba"})
    assert libreta.status_code == 200
    assert libreta.json()["casos"] == 0


def test_libreta_incluye_loss_y_ratio_fuerza():
    conexion = persistencia.conectar()
    a = _destacada(conexion, "Caso acierto fuerte", 8.0, "AAA")
    b = _destacada(conexion, "Caso acierto corto", 3.0, "BBB")
    persistencia.guardar_reaccion_real(conexion, a, {"pct_real": 10.0})
    persistencia.guardar_reaccion_real(conexion, b, {"pct_real": 9.0})
    resumen = corrector.libreta(conexion)
    conexion.close()
    assert resumen["tasa_acierto"] == 1.0
    assert resumen["ratio_fuerza_medio"] is not None
    assert resumen["loss"] is not None
    assert "listo_produccion" in resumen


def test_corrige_lilly_no_app():
    conexion = persistencia.conectar()
    sim_id = _destacada(
        conexion,
        "Eli Lilly Could Swing Over $76 Billion In Value After Earnings",
        3.0,
        "APP,GILD,HWM,LLY,NET,SHOP",
    )
    visto = []

    def obtener(simbolo, desde_iso, ruedas=2):
        visto.append(simbolo)
        return _variacion(1.2)(simbolo, desde_iso, ruedas)

    resultado = corrector.corregir_pendientes(conexion, obtener_variacion=obtener)
    conexion.close()
    assert visto == ["LLY"]
    assert resultado["corregidas"][0]["simbolo"] == "LLY"


def test_no_corrige_ruido_whale():
    conexion = persistencia.conectar()
    _destacada(conexion, "Check Out What Whales Are Doing With SLB", 4.0, "SLB")
    resultado = corrector.corregir_pendientes(conexion, obtener_variacion=_variacion(1.0))
    conexion.close()
    assert resultado["corregidas"] == []
    assert resultado["esperando"] == 1


def test_libreta_excluye_ruido():
    conexion = persistencia.conectar()
    bueno = _destacada(conexion, "Apple reports record iPhone sales", 2.0, "AAPL")
    ruido = _destacada(conexion, "Check Out What Whales Are Doing With SLB", 8.0, "SLB")
    persistencia.guardar_reaccion_real(conexion, bueno, {"pct_real": 1.5, "simbolo": "AAPL"})
    persistencia.guardar_reaccion_real(conexion, ruido, {"pct_real": 1.5, "simbolo": "SLB"})
    resumen = corrector.libreta(conexion)
    conexion.close()
    assert resumen["casos"] == 1
    assert resumen["excluidos_ruido"] == 1
    assert resumen["excluidos_respaldo"] == 0

