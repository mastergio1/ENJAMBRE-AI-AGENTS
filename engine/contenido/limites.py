"""Límites de las simulaciones disparadas por visitantes.

Cada simulación pública cuesta ~$0,12 en llamadas LLM. Tres frenos:
- GRATIS, por IP y día: 1/día (en memoria; su reinicio es de horas y no cuesta
  plata; la clave lleva la fecha, así se vacía sola cada día).
- PREMIUM, por correo y MES: 40/mes (en DISCO, tabla `gasto_premium`): un
  reinicio de Render NO le regala el mes de nuevo. Tope pensado para que un
  Premium a tope cueste ~$4,80 < los $6,99 que paga → nunca se pierde plata.
- GLOBAL, por día: tope diario (ENJAMBRE_MAX_SIM_DIA) en DISCO — la muralla de
  la billetera: manda sobre gratis y Premium por igual.

El on-demand es un lujo, no un regalo; al agotar el cupo, el muro invita al
Pulso (y al Premium, a esperar al próximo mes).
"""

import os
from datetime import date

from contenido import persistencia

LIMITE_DIA_GRATIS = 1     # defecto; ENJAMBRE_SIM_DIA_GRATIS
LIMITE_MES_PREMIUM = 40   # defecto; ENJAMBRE_SIM_MES_PREMIUM


def tope_dia_gratis() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_SIM_DIA_GRATIS", str(LIMITE_DIA_GRATIS))))
    except (TypeError, ValueError):
        return LIMITE_DIA_GRATIS


def tope_mes_premium() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_SIM_MES_PREMIUM", str(LIMITE_MES_PREMIUM))))
    except (TypeError, ValueError):
        return LIMITE_MES_PREMIUM


def tope_global_dia() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_MAX_SIM_DIA", "30")))
    except (TypeError, ValueError):
        return 30


# uso diario GRATIS por IP: clave -> (fecha_iso, cuenta). La fecha en el valor
# hace que el cupo se reinicie solo al cambiar el día (el Premium va en disco).
_uso: dict[str, tuple[str, int]] = {}

MENSAJE_GLOBAL = (
    "El enjambre agotó sus simulaciones públicas de hoy. "
    "Suscríbete al Pulso para no perderte la reacción de mañana."
)


def _mensaje_gratis() -> str:
    n = tope_dia_gratis()
    cuantas = "tu simulación gratis de hoy" if n == 1 else f"tus {n} simulaciones gratis de hoy"
    return (f"Usaste {cuantas}. Con El Pulso Premium son {tope_mes_premium()} al mes — "
            "y el análisis del domingo completo.")


def _mensaje_premium() -> str:
    return (f"Usaste tus {tope_mes_premium()} simulaciones Premium del mes. "
            "Se renuevan el día 1.")


def permitir(ip: str, premium_email: str | None = None,
             consumir: bool = True) -> tuple[bool, str]:
    """¿Puede esta persona disparar una simulación ahora? (permitido, motivo).

    Nivel según Premium: un suscriptor Premium activo tiene 40/MES (por correo,
    en disco); el resto, 1/DÍA (por IP, en memoria). El tope global (billetera)
    manda sobre ambos.
    """
    conexion = persistencia.conectar()
    try:
        hoy = date.today().isoformat()
        # 1) la muralla de la billetera (en disco) — sobre todos
        if persistencia.gasto_dia(conexion, hoy) >= tope_global_dia():
            return False, MENSAJE_GLOBAL

        email = (premium_email or "").strip().lower()
        es_prem = bool(email) and persistencia.es_premium(conexion, email)

        if es_prem:
            # PREMIUM: cupo mensual en disco
            mes = hoy[:7]
            if persistencia.gasto_premium_mes(conexion, email, mes) >= tope_mes_premium():
                return False, _mensaje_premium()
            if consumir:
                persistencia.sumar_gasto_premium(conexion, email, mes, 1)
                persistencia.sumar_gasto_dia(conexion, hoy, 1)
            return True, ""

        # GRATIS: cupo diario en memoria por IP
        clave = f"ip:{ip}"
        fecha, cuenta = _uso.get(clave, (hoy, 0))
        if fecha != hoy:          # cambió el día: cupo fresco
            cuenta = 0
        if cuenta >= tope_dia_gratis():
            _uso[clave] = (hoy, cuenta)
            return False, _mensaje_gratis()
        if consumir:
            _uso[clave] = (hoy, cuenta + 1)
            persistencia.sumar_gasto_dia(conexion, hoy, 1)
        return True, ""
    finally:
        conexion.close()


def limpiar(ahora=None) -> None:
    """Descarta las cuentas de días pasados — evita que _uso crezca sin fin al
    acumular visitantes distintos (fuga de memoria lenta)."""
    hoy = date.today().isoformat()
    for clave in list(_uso):
        if _uso[clave][0] != hoy:
            del _uso[clave]


def reiniciar() -> None:
    """Borra el estado (para los tests): el uso en memoria y el gasto en disco."""
    _uso.clear()
    try:
        conexion = persistencia.conectar()
        try:
            persistencia.reiniciar_gasto(conexion)
        finally:
            conexion.close()
    except Exception:
        pass  # sin base todavía (algún test muy temprano): nada que borrar
