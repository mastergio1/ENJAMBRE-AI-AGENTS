"""Pagos de El Pulso Premium — integración con Polar (Merchant of Record).

Polar cobra la suscripción (USD, global) y nos avisa por webhook cuando alguien
paga, cancela o se le revoca el acceso. Aquí:

  1. verificamos la firma del webhook (estándar Standard Webhooks / Svix), y
  2. traducimos el evento a la LLAVE `premium` del suscriptor (persistencia).

Por qué Polar y no Stripe: Stripe no acepta negocios de Chile; Polar sí paga a
vendedores chilenos y, al ser Merchant of Record, es el vendedor legal y maneja
los impuestos. La firma es el MISMO esquema que ya usamos para Resend (Svix);
solo cambian los nombres de las cabeceras (webhook-id/-timestamp/-signature).

Degradación segura: sin POLAR_WEBHOOK_SECRET, la verificación SIEMPRE falla
(nunca se activa un Premium con una firma no comprobada).
"""

import base64
import hashlib
import hmac
import os
import time

from contenido import persistencia

TOLERANCIA_SEG = 3600  # antirreplay: margen amplio para el reloj de Render

# Eventos de Polar (Standard Webhooks). Referencia: docs de Polar → webhooks.
# ACTIVA: hay una suscripción vigente → Premium ON hasta el fin del período.
EVENTOS_ACTIVA = {
    "subscription.created", "subscription.active", "subscription.updated",
    "subscription.resumed", "subscription.uncanceled", "subscription.cycled",
}
# CANCELA: cancelación al final del período. NO se corta ya: se deja vencer
# (pagó por el período en curso). El vencimiento lo maneja `premium_hasta`.
EVENTOS_CANCELA = {"subscription.canceled"}
# REVOCA: el acceso terminó de inmediato (impago definitivo, reembolso) → OFF ya.
EVENTOS_REVOCA = {"subscription.revoked"}


def _secreto_bytes(secreto: str) -> bytes | None:
    """La clave del webhook, en bytes. Standard Webhooks la entrega en base64,
    a veces con prefijo 'whsec_'."""
    clave = secreto.split("_", 1)[1] if secreto.startswith("whsec_") else secreto
    try:
        return base64.b64decode(clave)
    except Exception:
        return None


def verificar_firma(cuerpo: bytes, cabeceras) -> bool:
    """Valida la firma Standard Webhooks de Polar. Constante en el tiempo.
    Sin secreto configurado → False (nunca confía en un cuerpo sin comprobar)."""
    secreto = os.environ.get("POLAR_WEBHOOK_SECRET", "").strip()
    if not secreto:
        return False
    wid = cabeceras.get("webhook-id", "")
    wts = cabeceras.get("webhook-timestamp", "")
    firmas = cabeceras.get("webhook-signature", "")
    if not (wid and wts and firmas):
        return False
    try:
        if abs(int(time.time()) - int(wts)) > TOLERANCIA_SEG:
            return False
    except (ValueError, TypeError):
        return False
    clave_bytes = _secreto_bytes(secreto)
    if clave_bytes is None:
        return False
    firmado = f"{wid}.{wts}.".encode() + cuerpo
    esperada = base64.b64encode(hmac.new(clave_bytes, firmado, hashlib.sha256).digest()).decode()
    for parte in firmas.split():
        _, _, valor = parte.partition(",")
        if valor and hmac.compare_digest(valor, esperada):
            return True
    return False


def _email_de(data: dict) -> str | None:
    """Saca el correo del pagador del payload, tolerante a la forma exacta
    (Polar lo trae en data.customer.email; dejamos respaldos por si cambia)."""
    if not isinstance(data, dict):
        return None
    for ruta in (("customer", "email"), ("user", "email"), ("customer", "billing_email")):
        d = data
        for clave in ruta:
            d = d.get(clave) if isinstance(d, dict) else None
        if isinstance(d, str) and "@" in d:
            return d.strip().lower()
    for clave in ("customer_email", "email"):
        v = data.get(clave)
        if isinstance(v, str) and "@" in v:
            return v.strip().lower()
    return None


def _hasta_de(data: dict) -> str | None:
    """La fecha de vencimiento del período (AAAA-MM-DD) desde el payload."""
    if not isinstance(data, dict):
        return None
    for clave in ("current_period_end", "ends_at", "current_period_end_at"):
        v = data.get(clave)
        if isinstance(v, str) and len(v) >= 10:
            return v[:10]
    return None


def procesar_evento(conexion, evento: dict) -> dict:
    """Traduce un evento de Polar a la llave Premium del suscriptor. Idempotente:
    reprocesar el mismo evento deja el mismo estado (Polar reintenta si fallamos)."""
    tipo = (evento.get("type") or "").strip()
    data = evento.get("data") or {}
    email = _email_de(data)
    if not email:
        return {"ok": True, "accion": "ignorado", "motivo": "sin correo en el evento"}

    if tipo in EVENTOS_ACTIVA or tipo in EVENTOS_CANCELA:
        # un pagador SIEMPRE recibe El Pulso: si no era suscriptor, alta directa
        # (ya dio consentimiento explícito al pagar → sin doble opt-in).
        persistencia.alta_directa(conexion, email, origen="premium")
        persistencia.set_premium(conexion, email, True, hasta=_hasta_de(data))
        return {"ok": True, "accion": "premium_on", "email": email, "hasta": _hasta_de(data)}

    if tipo in EVENTOS_REVOCA:
        persistencia.set_premium(conexion, email, False)
        return {"ok": True, "accion": "premium_off", "email": email}

    return {"ok": True, "accion": "ignorado", "tipo": tipo}
