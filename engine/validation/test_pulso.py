"""Tests de la Etapa 8: El Pulso — captura, boletín, double opt-in, ritual."""

import struct

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import boletin, captura, limites, persistencia, pipeline, seguridad
from contenido.vocabulario import DISCLAIMER, verificar_pieza


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    limites.reiniciar()
    seguridad.reiniciar()


@pytest.fixture()
def dia():
    return pipeline.preparar_dia(semilla_base=42)


# ---------- captura del momento dramático ----------

def test_captura_genera_png_valido():
    serie = [100.0 + (i % 7) - 3 for i in range(151)]
    png = captura.generar_png(
        "Quiebra un banco", {"direccion_pct": -8.4, "volatilidad_pct": 1.6}, serie)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"  # firma PNG
    assert len(png) > 5000


def test_endpoint_imagen(dia):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    respuesta = cliente.get(f"/api/simulacion/{sim_id}/imagen")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "image/png"
    assert respuesta.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert "max-age" in respuesta.headers.get("Cache-Control", "")
    # sim_id inválido → 404 (misma defensa que el resto)
    assert cliente.get("/api/simulacion/no-hex/imagen").status_code == 404


# ---------- el correo ----------

def test_html_del_pulso_lleva_disclaimer_y_vocabulario_limpio(dia):
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    html = boletin.construir_html(destacadas, "sábado 11 de julio", token_baja="ABC")
    # el disclaimer CMF está presente (test obligatorio de CONTENIDO.md)
    assert DISCLAIMER in html
    # y no hay vocabulario prohibido en toda la pieza
    assert verificar_pieza(html) == []
    # el link de baja usa el token del suscriptor
    assert "/api/baja/ABC" in html
    # referencia la imagen del momento dramático
    assert "/imagen" in html


def test_correo_de_confirmacion_lleva_disclaimer():
    # sin RESEND no envía, pero el HTML se arma igual: lo probamos directo
    from contenido import boletin as b
    # reconstruye el cuerpo llamando a enviar con un doble que capture el html
    capturado = {}

    def falso_enviar(destinatario, asunto, html):
        capturado["html"] = html
        capturado["asunto"] = asunto
        return True

    b.enviar = falso_enviar  # monkeypatch simple
    assert b.enviar_confirmacion("x@y.cl", "tok123")
    assert DISCLAIMER in capturado["html"]
    assert "/api/confirmar/tok123" in capturado["html"]
    assert "Confirma" in capturado["asunto"]


# ---------- suscripción por la API (double opt-in) ----------

def test_flujo_suscripcion_completo():
    cliente = TestClient(server.app)

    # alta con correo inválido → 400
    assert cliente.post("/api/suscribir", json={"email": "no-es-correo"}).status_code == 400

    # alta válida → pendiente
    respuesta = cliente.post("/api/suscribir", json={"email": "giorgio@rubicon.cl"}).json()
    assert respuesta["estado"] == "pendiente"

    # aún no está activo
    conexion = persistencia.conectar()
    assert persistencia.suscriptores_activos(conexion) == []
    token = conexion.execute("SELECT token_confirma FROM suscriptores").fetchone()[0]
    baja = conexion.execute("SELECT token_baja FROM suscriptores").fetchone()[0]
    conexion.close()

    # confirmar por el link → página HTML de éxito
    conf = cliente.get(f"/api/confirmar/{token}")
    assert conf.status_code == 200
    assert "confirmada" in conf.text.lower()

    conexion = persistencia.conectar()
    assert len(persistencia.suscriptores_activos(conexion)) == 1
    conexion.close()

    # baja de un clic
    assert cliente.get(f"/api/baja/{baja}").status_code == 200
    conexion = persistencia.conectar()
    assert persistencia.suscriptores_activos(conexion) == []
    conexion.close()


def test_suscribir_dos_veces_no_duplica():
    cliente = TestClient(server.app)
    cliente.post("/api/suscribir", json={"email": "a@b.cl"})
    cliente.post("/api/suscribir", json={"email": "a@b.cl"})
    conexion = persistencia.conectar()
    total = conexion.execute("SELECT COUNT(*) FROM suscriptores").fetchone()[0]
    conexion.close()
    assert total == 1


# ---------- el ritual completo ----------

def test_ritual_matutino_arma_todo_sin_enviar(monkeypatch):
    avisos = []
    from contenido import notificar
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: avisos.append(mensaje) or True)

    resultado = pipeline.ritual_matutino(semilla_base=99, enviar=False)
    assert len(resultado["publicadas"]) == 3
    assert resultado["destacadas"] == 3
    assert resultado["envio"] is None          # enviar=False
    assert DISCLAIMER in resultado["html_preview"]
    assert avisos and "El Pulso" in avisos[0]   # paso 8: avisó a Giorgio


def test_endpoint_pipeline_exige_token(monkeypatch):
    cliente = TestClient(server.app)
    # sin token configurado → 403
    monkeypatch.delenv("ENJAMBRE_PIPELINE_TOKEN", raising=False)
    assert cliente.post("/api/pipeline").status_code == 403

    # con token configurado pero header incorrecto → 403
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    assert cliente.post("/api/pipeline", headers={"X-Pipeline-Token": "malo"}).status_code == 403

    # header correcto → 200 e inicia en segundo plano (el ritual se neutraliza
    # para probar solo la puerta de autorización, no correr 3 simulaciones)
    corridas = []
    monkeypatch.setattr(pipeline, "ritual_matutino", lambda **k: corridas.append(k))
    respuesta = cliente.post("/api/pipeline", headers={"X-Pipeline-Token": "secreto"})
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "iniciado"
    assert corridas  # el ritual se disparó en segundo plano


def test_ritual_envia_a_suscriptores_confirmados(monkeypatch):
    # un suscriptor confirmado
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, "lector@medio.cl")
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    conexion.close()

    enviados = []
    monkeypatch.setattr(boletin, "enviar", lambda *a: enviados.append(a) or True)
    from contenido import notificar
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: True)

    resultado = pipeline.ritual_matutino(semilla_base=7, enviar=True)
    assert resultado["envio"]["suscriptores"] == 1
    assert resultado["envio"]["enviados"] == 1
    # el correo salió al suscriptor confirmado
    assert enviados[0][0] == "lector@medio.cl"
