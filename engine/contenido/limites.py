"""Límites de las simulaciones disparadas por visitantes.

Cada simulación pública cuesta ~100 llamadas LLM. Dos frenos:
- por IP: 5 por hora (CONTENIDO.md sección 3.2)
- global: tope diario configurable (ENJAMBRE_MAX_SIM_DIA, defecto 20) —
  un día viral no puede quemar el presupuesto; al agotarse, el muro
  invita a suscribirse al Pulso.

Estado en memoria: suficiente para una instancia (el deploy actual).
"""

import os
import time
from datetime import date

LIMITE_IP_HORA = 5

_por_ip: dict[str, list[float]] = {}
_dia_actual: date = date.today()
_consumidas_hoy = 0

MENSAJE_IP = "Alcanzaste el límite de 5 simulaciones por hora. El enjambre necesita un respiro."
MENSAJE_GLOBAL = (
    "El enjambre agotó sus simulaciones públicas de hoy. "
    "Suscríbete al Pulso para no perderte la reacción de mañana."
)


def tope_global_dia() -> int:
    return int(os.environ.get("ENJAMBRE_MAX_SIM_DIA", "20"))


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
