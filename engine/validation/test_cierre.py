"""Tests de la edición de la TARDE — 'el cierre del mercado' (Premium)."""

import pytest

import server  # noqa: F401 (asegura que la app importa con los cambios)
from contenido import boletin, persistencia, pipeline

CIERRE = {
    "titulo": "El cierre del mercado",
    "movers": [
        {"titular": "Moderna (MRNA) sube 40% tras un avance en su vacuna contra el cáncer",
         "razon": "resultados clínicos positivos", "simbolos": "MRNA",
         "var_pct": 40.0, "verificado": True, "sesion": "sesión"},
        {"titular": "OneSpaWorld (OSW) cae 10% tras una guía débil",
         "razon": "recortó su previsión", "simbolos": "OSW",
         "var_pct": -10.0, "verificado": True, "sesion": "sesión"},
    ],
}


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


def test_bloque_cierre_renderiza():
    html = boletin.construir_html([], "lunes 1 de septiembre · cierre", brief={"cierre": CIERRE})
    assert "Edición de la tarde" in html
    assert "Moderna" in html and "vacuna contra el cáncer" in html
    assert "OneSpaWorld" in html
    assert "No es asesoría de inversión" in html


def test_ritual_tarde_arma_pendiente(monkeypatch):
    from contenido import cierre, notificar
    monkeypatch.setattr(notificar, "avisar", lambda m: True)
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: CIERRE)

    res = pipeline.ritual_matutino(enviar=False, momento="tarde")
    assert res["edicion"] == "cierre" and res["estado"] == "pendiente"
    assert res["clave"].endswith("-t")           # clave propia de la tarde
    assert "El cierre del mercado" in res["html_preview"]


def test_ritual_tarde_sin_movers_no_edicion(monkeypatch):
    from contenido import cierre
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: None)
    res = pipeline.ritual_matutino(enviar=False, momento="tarde")
    assert res["estado"] == "sin_edicion" and res["edicion"] == "cierre"


def test_cierre_sale_solo_a_premium(monkeypatch):
    conexion = persistencia.conectar()
    for correo in ("gratis@lector.cl", "pago@lector.cl"):
        alta = persistencia.agregar_suscriptor(conexion, correo)
        persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    persistencia.set_premium(conexion, "pago@lector.cl", True)

    from contenido import cierre, notificar
    monkeypatch.setattr(notificar, "avisar", lambda m: True)
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: CIERRE)
    res = pipeline.ritual_matutino(conexion, enviar=False, momento="tarde")
    clave = res["clave"]
    conexion.close()

    enviados = []
    monkeypatch.setattr(boletin, "enviar",
                        lambda dest, asunto, html, **k: enviados.append(dest) or True)
    r = pipeline.aprobar_y_enviar(fecha=clave)
    assert r["ok"] and r["enviados"] == 1
    assert enviados == ["pago@lector.cl"]         # el gratuito NO recibe la tarde
