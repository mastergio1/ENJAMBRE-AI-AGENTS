"""Límites de las simulaciones disparadas por visitantes.

Cada simulación pública cuesta ~100 llamadas LLM. Dos frenos:
- por IP: 3 por hora (una fracción del tope diario)
- global: tope diario configurable (ENJAMBRE_MAX_SIM_DIA, defecto 5) —
  el on-demand es un lujo, no un regalo: pocas simulaciones nuevas al
  día. Al agotarse, el muro invita a suscribirse al Pulso.

Estado en memoria: suficiente para una instancia (el deploy actual).
"""

import os
import time
from datetime import date

LIMITE_IP_HORA = 3

_por_ip: dict[str, list[float]] = {}
_dia_actual: date = date.today()
_consumidas_hoy = 0

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


def _rotar_dia() -> None:
    global _dia_actual, _consumidas_hoy
    if date.today() != _dia_actual:
        _dia_actual = date.today()
        _consumidas_hoy = 0


def permitir(ip: str, consumir: bool = True) -> tuple[bool, str]:
    """¿Puede esta IP disparar una simulación ahora? (permitido, motivo)."""
    global _consumidas_hoy
    _rotar_dia()
    if _consumidas_hoy >= tope_global_dia():
        return False, MENSAJE_GLOBAL
    hace_una_hora = time.time() - 3600
    recientes = [t for t in _por_ip.get(ip, []) if t > hace_una_hora]
    if len(recientes) >= LIMITE_IP_HORA:
        _por_ip[ip] = recientes
        return False, MENSAJE_IP
    if consumir:
        recientes.append(time.time())
        _por_ip[ip] = recientes
        _consumidas_hoy += 1
    return True, ""


def reiniciar() -> None:
    """Borra el estado (para los tests)."""
    global _consumidas_hoy
    _por_ip.clear()
    _consumidas_hoy = 0
