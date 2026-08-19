"""Tests de la integración de pagos (Polar → llave Premium de El Pulso)."""

import base64
import hashlib
import hmac
import json
import time

import pytest
from fastapi.testclient import TestClient

import server
from contenido import pagos, persistencia

SECRETO = "whsec_" + base64.b64encode(b"secreto-de-prueba-para-polar").decode()


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    monkeypatch.setenv("POLAR_WEBHOOK_SECRET", SECRETO)


def _firmar(cuerpo: bytes, wid: str = "msg_1", wts: int | None = None) -> dict:
    """Firma un cuerpo como lo haría Polar (Standard Webhooks)."""
    wts = wts if wts is not None else int(time.time())
    clave = base64.b64decode(SECRETO.split("_", 1)[1])
    firmado = f"{wid}.{wts}.".encode() + cuerpo
    firma = base64.b64encode(hmac.new(clave, firmado, hashlib.sha256).digest()).decode()
    return {"webhook-id": wid, "webhook-timestamp": str(wts), "webhook-signature": f"v1,{firma}"}


def _evento(tipo: str, email: str = "pagador@lector.cl", hasta: str = "2027-01-01") -> bytes:
    data = {"customer": {"email": email}, "current_period_end": hasta + "T00:00:00Z",
            "status": "active"}
    return json.dumps({"type": tipo, "data": data}).encode()


# ---------- firma ----------

def test_firma_valida_y_activa_premium():
    conexion = persistencia.conectar()
    cuerpo = _evento("subscription.active")
    res = pagos.procesar_evento(conexion, json.loads(cuerpo))
    assert res["accion"] == "premium_on"
    assert persistencia.es_premium(conexion, "pagador@lector.cl")   # alta directa + premium
    conexion.close()


def test_firma_invalida_rechaza():
    cabeceras = {"webhook-id": "msg_1", "webhook-timestamp": str(int(time.time())),
                 "webhook-signature": "v1,firmafalsa"}
    assert not pagos.verificar_firma(_evento("subscription.active"), cabeceras)


def test_sin_secreto_falla_cerrado(monkeypatch):
    monkeypatch.delenv("POLAR_WEBHOOK_SECRET", raising=False)
    cuerpo = _evento("subscription.active")
    assert not pagos.verificar_firma(cuerpo, _firmar(cuerpo))


def test_timestamp_viejo_se_rechaza():
    cuerpo = _evento("subscription.active")
    viejo = _firmar(cuerpo, wts=int(time.time()) - 10_000)
    assert not pagos.verificar_firma(cuerpo, viejo)


# ---------- lógica de negocio ----------

def test_cancelacion_deja_vencer_no_corta_ya():
    """Cancelar (al final del período) mantiene Premium hasta el vencimiento."""
    conexion = persistencia.conectar()
    pagos.procesar_evento(conexion, json.loads(_evento("subscription.active", hasta="2027-06-01")))
    res = pagos.procesar_evento(conexion, json.loads(_evento("subscription.canceled", hasta="2027-06-01")))
    assert res["accion"] == "premium_on"                       # sigue activo…
    assert persistencia.es_premium(conexion, "pagador@lector.cl")  # …hasta que venza
    conexion.close()


def test_revocacion_corta_de_inmediato():
    conexion = persistencia.conectar()
    pagos.procesar_evento(conexion, json.loads(_evento("subscription.active")))
    res = pagos.procesar_evento(conexion, json.loads(_evento("subscription.revoked")))
    assert res["accion"] == "premium_off"
    assert not persistencia.es_premium(conexion, "pagador@lector.cl")
    conexion.close()


def test_evento_sin_email_se_ignora():
    conexion = persistencia.conectar()
    res = pagos.procesar_evento(conexion, {"type": "subscription.active", "data": {}})
    assert res["accion"] == "ignorado"
    conexion.close()


# ---------- endpoint completo ----------

def test_endpoint_webhook_activa_premium():
    cliente = TestClient(server.app)
    cuerpo = _evento("subscription.active", email="nuevo@lector.cl")
    r = cliente.post("/pulso/webhook/polar", content=cuerpo, headers=_firmar(cuerpo))
    assert r.status_code == 200 and r.json()["accion"] == "premium_on"
    conexion = persistencia.conectar()
    assert persistencia.es_premium(conexion, "nuevo@lector.cl")
    conexion.close()


def test_endpoint_webhook_rechaza_sin_firma():
    cliente = TestClient(server.app)
    cuerpo = _evento("subscription.active")
    r = cliente.post("/pulso/webhook/polar", content=cuerpo)  # sin cabeceras de firma
    assert r.status_code == 401


def test_endpoint_estado_premium():
    """El Enjambre pregunta si un correo es Premium para elevar su cupo diario."""
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, "vip@lector.cl")
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    persistencia.set_premium(conexion, "vip@lector.cl", True)
    conexion.close()

    cliente = TestClient(server.app)
    r = cliente.get("/api/pulso/premium", params={"email": "vip@lector.cl"}).json()
    assert r["premium"] is True and r["limite"] == 10
    r2 = cliente.get("/api/pulso/premium", params={"email": "nadie@lector.cl"}).json()
    assert r2["premium"] is False and r2["limite"] == 3
