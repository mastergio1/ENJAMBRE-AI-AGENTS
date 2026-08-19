"""Límites de las simulaciones disparadas por visitantes.

Cada simulación pública cuesta ~100 llamadas LLM. Tres frenos:
- por persona y día (FREEMIUM): gratis 3/día (por IP); Premium de El Pulso
  10/día (por su correo verificado). En memoria: su reinicio es de horas y no
  cuesta plata; la clave incluye la fecha, así se vacía sola cada día.
- global: tope diario configurable (ENJAMBRE_MAX_SIM_DIA) — en DISCO (tabla
  `gasto_diario`): NO se reinicia con cada despliegue de Render. Es la muralla
  de la billetera: nada la traspasa, ni siquiera los Premium.

El on-demand es un lujo, no un regalo; al agotar el cupo diario, el muro invita
al Pulso (y al que ya es Premium, a volver mañana).
"""

import os
from datetime import date

from contenido import persistencia

LIMITE_DIA_GRATIS = 3    # defecto; ENJAMBRE_SIM_DIA_GRATIS
LIMITE_DIA_PREMIUM = 10  # defecto; ENJAMBRE_SIM_DIA_PREMIUM


def tope_dia_gratis() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_SIM_DIA_GRATIS", str(LIMITE_DIA_GRATIS))))
    except (TypeError, ValueError):
        return LIMITE_DIA_GRATIS


def tope_dia_premium() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_SIM_DIA_PREMIUM", str(LIMITE_DIA_PREMIUM))))
    except (TypeError, ValueError):
        return LIMITE_DIA_PREMIUM


def tope_global_dia() -> int:
    try:
        return max(0, int(os.environ.get("ENJAMBRE_MAX_SIM_DIA", "60")))
    except (TypeError, ValueError):
        return 60


# uso diario por persona: clave -> (fecha_iso, cuenta). La clave lleva prefijo
# 'p:' (premium, por correo) o 'ip:' (gratis, por IP). La fecha en el valor hace
# que el cupo se reinicie solo al cambiar el día, sin contador que rotar.
_uso: dict[str, tuple[str, int]] = {}

MENSAJE_GLOBAL = (
    "El enjambre agotó sus simulaciones públicas de hoy. "
    "Suscríbete al Pulso para no perderte la reacción de mañana."
)


def _mensaje_gratis() -> str:
    return (f"Llegaste a tus {tope_dia_gratis()} simulaciones gratis de hoy. "
            f"Con El Pulso Premium son {tope_dia_premium()} al día — "
            "y el análisis del domingo completo.")


def _mensaje_premium() -> str:
    return (f"Usaste tus {tope_dia_premium()} simulaciones Premium de hoy. "
            "El enjambre te espera mañana.")


def permitir(ip: str, premium_email: str | None = None,
             consumir: bool = True) -> tuple[bool, str]:
    """¿Puede esta persona disparar una simulación ahora? (permitido, motivo).

    Nivel según Premium: si `premium_email` es un suscriptor Premium activo, el
    cupo es el de pago (10/día) contado por correo; si no, el gratis (3/día)
    contado por IP. El tope global (billetera) manda sobre ambos.
    """
    conexion = persistencia.conectar()
    try:
        hoy = date.today().isoformat()
        # 1) la muralla de la billetera (en disco) — sobre todos
        if persistencia.gasto_dia(conexion, hoy) >= tope_global_dia():
            return False, MENSAJE_GLOBAL

        # 2) nivel de la persona
        email = (premium_email or "").strip().lower()
        es_prem = bool(email) and persistencia.es_premium(conexion, email)
        if es_prem:
            clave, limite = f"p:{email}", tope_dia_premium()
        else:
            clave, limite = f"ip:{ip}", tope_dia_gratis()

        fecha, cuenta = _uso.get(clave, (hoy, 0))
        if fecha != hoy:          # cambió el día: cupo fresco
            cuenta = 0
        if cuenta >= limite:
            _uso[clave] = (hoy, cuenta)
            return False, (_mensaje_premium() if es_prem else _mensaje_gratis())

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
