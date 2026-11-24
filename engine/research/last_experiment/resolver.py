"""L6 — Resolución de eventos: precio de entrada/salida y maduración de etiqueta.

Resuelve SOLO con barras FINALES (F13): el número de barras no certifica el cierre; se
verifica el calendario, los timestamps y el estado final de la barra. `r = exit/entry-1`
en decimal. `y=1` si r>0 estricto. No resuelve con barras provisionales ni antes de que
la sesión de salida haya cerrado (F08). El proveedor de precios es inyectable; para el
dry-run se usa un fixture determinista, para producción un adaptador Alpaca/Yahoo que
cumpla el contrato (validar licencia y calidad; pendiente de aprobación).
"""
from __future__ import annotations

import datetime as dt
from typing import Protocol

from . import calendar as cal
from .config import hash_canonico
from .ledger import Outcome


class ProveedorPrecios(Protocol):
    def cierre_final(self, symbol: str, session: str) -> tuple[float, bool] | None:
        """Devuelve (precio_cierre, es_final) de la sesión `session` (YYYY-MM-DD), o
        None si no hay dato. `es_final=False` indica barra provisional (no sellar)."""
        ...


class NoMaduro(RuntimeError):
    pass


class BarraProvisional(RuntimeError):
    pass


def resolver_evento(event: dict, proveedor: ProveedorPrecios,
                    ahora_utc: dt.datetime) -> Outcome:
    """Construye el Outcome inmutable de un evento ya maduro.

    `event` requiere: event_id, symbol, entry_session, exit_session,
    label_available_after_utc. Lanza NoMaduro/BarraProvisional si no procede sellar.
    """
    if ahora_utc.tzinfo is None:
        raise ValueError("ahora_utc debe ser aware (UTC)")
    cierre_salida = dt.datetime.fromisoformat(event["label_available_after_utc"])
    if ahora_utc <= cierre_salida:
        raise NoMaduro(f"{event['event_id']}: sesión de salida aún no cerró")

    entrada = event.get("entrada_sesion") or event.get("entry_session")
    salida = event.get("salida_sesion") or event.get("exit_session")
    entry = proveedor.cierre_final(event["symbol"], entrada)
    exit_ = proveedor.cierre_final(event["symbol"], salida)
    if entry is None or exit_ is None:
        raise NoMaduro(f"{event['event_id']}: faltan barras de entrada/salida")
    ep, ep_final = entry
    xp, xp_final = exit_
    if not (ep_final and xp_final):
        raise BarraProvisional(f"{event['event_id']}: barra provisional, no se sella")
    if ep <= 0:
        raise ValueError("precio de entrada no positivo")
    r = xp / ep - 1.0
    data_hash = hash_canonico({"ev": event["event_id"], "ep": ep, "xp": xp})
    return Outcome(
        event_id=event["event_id"], entry_session=entrada,
        exit_session=salida, entry_price=ep, exit_price=xp,
        return_decimal=r, label_available_at=cierre_salida.isoformat(),
        data_hash=data_hash,
        resolved_at=dt.datetime.now(dt.timezone.utc).isoformat())


def contrato_desde_emision(symbol: str, emision: str, horizonte: int = 2) -> dict:
    """Construye el contrato temporal + event_id de un evento (usa el calendario)."""
    from .config import event_id
    c = cal.contrato_evento(dt.date.fromisoformat(emision), horizonte)
    c["event_id"] = event_id(symbol, emision, horizonte)
    c["symbol"] = symbol
    return c


class FixturePrecios:
    """Proveedor de precios DETERMINISTA para dry-run/tests (no es dato real)."""
    def __init__(self, precios: dict, finales: set | None = None):
        self.precios = precios          # {(symbol, session): precio}
        self.finales = finales          # sesiones con barra final; None = todas finales

    def cierre_final(self, symbol, session):
        v = self.precios.get((symbol, session))
        if v is None:
            return None
        final = True if self.finales is None else (session in self.finales)
        return (float(v), final)
