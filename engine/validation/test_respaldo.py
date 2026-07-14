"""Tests del respaldo de calibración a GitHub (contenido/respaldo.py).

La regla de oro: el respaldo FUSIONA con lo ya subido (inmune a los
borrones del disco efímero de Render), va a una rama distinta de main
(un commit a main redesplegaría el motor) y jamás tumba al corrector.
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest

from contenido import corrector, persistencia, respaldo


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_RESPALDO_TOKEN", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


def _caso(conexion, titular: str, pct_sim: float, pct_real: float | None,
          hace_dias: int = 3) -> str:
    sim_id = persistencia.guardar_simulacion(
        conexion, titular=titular, fuente="test", seed=abs(hash(titular)) % 1000,
        resumen={"direccion_pct": pct_sim, "volatilidad_pct": 1.0},
        lideres=[], serie_precios=[100.0], destacada=True,
    )
    persistencia.registrar_titular(conexion, titular=titular, fuente="test",
                                   veredicto="simular", simbolos="SPY", sim_id=sim_id)
    fecha = (datetime.now(timezone.utc) - timedelta(days=hace_dias)).isoformat(timespec="seconds")
    conexion.execute("UPDATE simulaciones SET fecha = ? WHERE id = ?", (fecha, sim_id))
    if pct_real is not None:
        persistencia.guardar_reaccion_real(conexion, sim_id, {"simbolo": "SPY", "pct_real": pct_real})
    conexion.commit()
    return sim_id


def test_exportar_solo_incluye_casos_corregidos():
    conexion = persistencia.conectar()
    corregida = _caso(conexion, "Con corrección", -2.0, -1.1)
    _caso(conexion, "Sin corrección aún", 1.0, None)
    casos = respaldo.exportar_casos(conexion)
    conexion.close()
    assert [c["sim_id"] for c in casos] == [corregida]
    assert casos[0]["reaccion_real"]["pct_real"] == -1.1
    assert casos[0]["direccion_pct"] == -2.0
    assert casos[0]["simbolos"] == "SPY"


def test_fusionar_es_inmune_al_borron_de_disco():
    # lo ya respaldado (de antes del redeploy) + lo nuevo (base recién nacida)
    previos = [{"sim_id": "a", "fecha": "2026-07-01", "titular": "vieja"},
               {"sim_id": "b", "fecha": "2026-07-02", "titular": "se actualiza"}]
    nuevos = [{"sim_id": "b", "fecha": "2026-07-02", "titular": "versión nueva"},
              {"sim_id": "c", "fecha": "2026-07-03", "titular": "nueva"}]
    fusion = respaldo.fusionar(previos, nuevos)
    assert [c["sim_id"] for c in fusion] == ["a", "b", "c"]  # nada se pierde
    assert fusion[1]["titular"] == "versión nueva"           # lo nuevo manda


def test_sin_token_no_hace_nada_y_no_lanza():
    resultado = respaldo.respaldar()
    assert resultado["subido"] is False
    assert "GITHUB_RESPALDO_TOKEN" in resultado["motivo"]


def test_subida_fusiona_con_lo_remoto(monkeypatch):
    """Simula GitHub: ya hay 1 caso remoto; el local aporta otro → quedan 2."""
    monkeypatch.setenv("GITHUB_RESPALDO_TOKEN", "tok-prueba")
    conexion = persistencia.conectar()
    _caso(conexion, "Caso local", 2.0, 1.5)

    remoto = {"casos": [{"sim_id": "remoto1", "fecha": "2026-07-01"}]}
    contenido_b64 = base64.b64encode(json.dumps(remoto).encode()).decode()
    subidas = {}

    class RespuestaGet:
        status_code = 200
        def json(self):
            return {"sha": "abc123", "content": contenido_b64}

    class RespuestaPut:
        status_code = 200
        def raise_for_status(self):
            pass

    def falso_get(url, **kwargs):
        assert kwargs["params"]["ref"] == "respaldo-datos"  # jamás main
        return RespuestaGet()

    def falso_put(url, **kwargs):
        subidas["cuerpo"] = kwargs["json"]
        return RespuestaPut()

    monkeypatch.setattr(respaldo.httpx, "get", falso_get)
    monkeypatch.setattr(respaldo.httpx, "put", falso_put)

    resultado = respaldo.respaldar(conexion)
    conexion.close()

    assert resultado == {"subido": True, "casos": 2}  # remoto + local
    assert subidas["cuerpo"]["branch"] == "respaldo-datos"
    assert subidas["cuerpo"]["sha"] == "abc123"
    subido = json.loads(base64.b64decode(subidas["cuerpo"]["content"]))
    assert len(subido["casos"]) == 2


def test_falla_de_red_no_lanza(monkeypatch):
    monkeypatch.setenv("GITHUB_RESPALDO_TOKEN", "tok-prueba")
    conexion = persistencia.conectar()
    _caso(conexion, "Caso local", 2.0, 1.5)
    monkeypatch.setattr(respaldo.httpx, "get",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("sin red")))
    resultado = respaldo.respaldar(conexion)
    conexion.close()
    assert resultado["subido"] is False
    assert "OSError" in resultado["motivo"]


def test_el_corrector_dispara_el_respaldo_solo_si_corrigio(monkeypatch):
    llamadas = []
    monkeypatch.setattr(respaldo, "respaldar", lambda conexion=None: llamadas.append(1) or {"subido": True, "casos": 1})
    conexion = persistencia.conectar()
    _caso(conexion, "Pendiente de corregir", -2.0, None)

    # sin datos de mercado: no corrige → no respalda
    corrector.corregir_pendientes(conexion, obtener_variacion=lambda *a: None)
    assert llamadas == []

    # con datos: corrige → respalda
    variacion = {"simbolo": "SPY", "pct_real": -0.9, "cierre_base": 100.0,
                 "cierre_final": 99.1, "fecha_base": "2026-07-10",
                 "fecha_final": "2026-07-14", "ruedas": 2}
    resultado = corrector.corregir_pendientes(conexion, obtener_variacion=lambda *a: variacion)
    conexion.close()
    assert llamadas == [1]
    assert resultado["respaldo"] == {"subido": True, "casos": 1}
