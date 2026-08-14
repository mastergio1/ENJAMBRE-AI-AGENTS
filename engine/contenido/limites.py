"""Límites de las simulaciones disparadas por visitantes.

Cada simulación pública cuesta ~100 llamadas LLM. Dos frenos:
- por IP: 3 por hora (una fracción del tope diario) — en memoria: su reinicio
  es de minutos y no cuesta plata.
- global: tope diario configurable (ENJAMBRE_MAX_SIM_DIA, defecto 5) — en DISCO
  (tabla `gasto_diario`): así NO se reinicia con cada despliegue de Render. El
  on-demand es un lujo, no un regalo; al agotarse, el muro invita al Pulso.
"""

import os
import time
from datetime import date

from contenido import persistencia

LIMITE_IP_HORA = 3  # defecto; configurable con ENJAMBRE_MAX_SIM_IP_HORA


def tope_ip_hora() -> int:
    try:
        return max(1, int(os.environ.get("ENJAMBRE_MAX_SIM_IP_HORA", str(LIMITE_IP_HORA))))
    except (TypeError, ValueError):
        return LIMITE_IP_HORA

_por_ip: dict[str, list[float]] = {}

MENSAJE_IP = "Alcanzaste el límite por hora. El enjambre necesita un respiro."
MENSAJE_GLOBAL = (
    "El enjambre agotó sus simulaciones públicas de hoy. "
    "Suscríbete al Pulso para no perderte la reacción de mañana."
)


def tope_global_dia() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_MAX_SIM_DIA", "5")))
    except (TypeError, ValueError):
        return 5


def permitir(ip: str, consumir: bool = True) -> tuple[bool, str]:
    """¿Puede esta IP disparar una simulación ahora? (permitido, motivo).

    El tope global vive en disco (sobrevive a los reinicios); el por-IP en
    memoria. El día se maneja por la clave de fecha, sin contador que rotar."""
    conexion = persistencia.conectar()
    try:
        hoy = date.today().isoformat()
        if persistencia.gasto_dia(conexion, hoy) >= tope_global_dia():
            return False, MENSAJE_GLOBAL
        hace_una_hora = time.time() - 3600
        recientes = [t for t in _por_ip.get(ip, []) if t > hace_una_hora]
        if len(recientes) >= tope_ip_hora():
            _por_ip[ip] = recientes
            return False, MENSAJE_IP
        if consumir:
            recientes.append(time.time())
            _por_ip[ip] = recientes
            persistencia.sumar_gasto_dia(conexion, hoy, 1)
        return True, ""
    finally:
        conexion.close()


def limpiar(ahora: float | None = None) -> None:
    """Descarta IPs sin actividad en la última hora — evita que _por_ip crezca
    sin fin al acumular visitantes distintos (fuga de memoria lenta)."""
    ahora = time.time() if ahora is None else ahora
    hace_una_hora = ahora - 3600
    for ip in list(_por_ip):
        recientes = [t for t in _por_ip[ip] if t > hace_una_hora]
        if recientes:
            _por_ip[ip] = recientes
        else:
            del _por_ip[ip]


def reiniciar() -> None:
    """Borra el estado (para los tests): las IPs en memoria y el gasto en disco."""
    _por_ip.clear()
    try:
        conexion = persistencia.conectar()
        try:
            persistencia.reiniciar_gasto(conexion)
        finally:
            conexion.close()
    except Exception:
        pass  # sin base todavía (algún test muy temprano): nada que borrar
