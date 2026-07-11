"""Aviso a Giorgio por Telegram (CONTENIDO.md paso 8 del ritual).

Un resumen de la ejecución del pipeline (qué se simuló, cuántos correos
salieron, errores). Degradación elegante: sin TELEGRAM_BOT_TOKEN o
TELEGRAM_CHAT_ID, no hace nada (devuelve False), nunca lanza.

Nota: este es el aviso SALIENTE. El oyente del canal de noticias de
Giorgio (fuentes/telegram.py) es la fase 2.
"""

import os

import httpx


def avisar(mensaje: str) -> bool:
    """Envía un mensaje al chat de Telegram de Giorgio. False si no configurado."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        respuesta = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"},
            timeout=15,
        )
        return respuesta.status_code < 300
    except Exception:
        return False


def resumen_ejecucion(origen: str, publicadas: list[dict], envio: dict | None) -> str:
    """Arma el texto del aviso de una corrida del pipeline."""
    lineas = ["🐝 <b>El Pulso — corrida del día</b>", f"Fuente de titulares: {origen}"]
    if publicadas:
        lineas.append(f"Simuladas ({len(publicadas)}):")
        for p in publicadas:
            lineas.append(f"  ★ [{p['impacto']}/10] {p['titular'][:60]}")
    else:
        lineas.append("Sin simulaciones nuevas (el día ya estaba preparado).")
    if envio:
        lineas.append(
            f"Correos: {envio['enviados']} enviados / {envio['suscriptores']} suscriptores"
            + (f" · {envio['fallidos']} fallidos" if envio.get("fallidos") else "")
        )
    return "\n".join(lineas)
