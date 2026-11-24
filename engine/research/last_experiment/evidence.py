"""L3 — Snapshot de evidencia point-in-time (PIT) y paquete de titulares determinista.

Cada pieza de evidencia lleva su procedencia y SOLO entra si estaba disponible al
cutoff (prevención de fuga, I.4). Fechas naive se rechazan: todo timestamp debe ser
UTC aware. El snapshot es inmutable y se identifica por su `content_hash`.

El paquete de titulares es DETERMINISTA: dedup por source_id/hash, orden estable
(timestamp, fuente, id), máximo 5, token `NO_MACRO_EVENT` si no hay noticia macro.
Los textos de noticias son DATOS NO CONFIABLES: nunca instrucciones (I.4.1).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from .config import TOKEN_SIN_EVENTO, hash_canonico


class EvidenciaInvalida(ValueError):
    pass


def _exigir_aware(name: str, t: dt.datetime) -> dt.datetime:
    if not isinstance(t, dt.datetime):
        raise EvidenciaInvalida(f"{name} debe ser datetime")
    if t.tzinfo is None or t.utcoffset() is None:
        raise EvidenciaInvalida(f"{name} es naive; se exige UTC aware")
    return t.astimezone(dt.timezone.utc)


@dataclass(frozen=True)
class FuenteEvidencia:
    """Una pieza de evidencia con procedencia completa (I.4 / L3)."""
    source_id: str
    tipo: str                 # 'titular' | 'precio' | 'macro' | 'expectativa' | ...
    contenido: dict           # payload estructurado (no texto libre ejecutable)
    published_at: dt.datetime
    observed_at: dt.datetime
    available_at: dt.datetime

    def __post_init__(self):
        for name in ("published_at", "observed_at", "available_at"):
            object.__setattr__(self, name, _exigir_aware(name, getattr(self, name)))

    @property
    def content_hash(self) -> str:
        return hash_canonico({
            "source_id": self.source_id, "tipo": self.tipo,
            "contenido": self.contenido,
            "published_at": self.published_at.isoformat(),
        })

    def a_dict(self) -> dict:
        return {
            "source_id": self.source_id, "tipo": self.tipo, "contenido": self.contenido,
            "published_at": self.published_at.isoformat(),
            "observed_at": self.observed_at.isoformat(),
            "available_at": self.available_at.isoformat(),
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True)
class Snapshot:
    """Snapshot PIT inmutable para un evento, sellado al cutoff."""
    event_id: str
    symbol: str
    cutoff_utc: dt.datetime
    fuentes: tuple = field(default_factory=tuple)

    @property
    def evidence_hash(self) -> str:
        return hash_canonico({
            "event_id": self.event_id, "symbol": self.symbol,
            "cutoff_utc": self.cutoff_utc.isoformat(),
            "fuentes": sorted(f.content_hash for f in self.fuentes),
        })

    def evidence_ids(self) -> list[str]:
        return sorted(f.source_id for f in self.fuentes)

    def titulares(self) -> list[dict]:
        return [f.contenido for f in self.fuentes if f.tipo == "titular"]

    def a_dict(self) -> dict:
        return {
            "event_id": self.event_id, "symbol": self.symbol,
            "cutoff_utc": self.cutoff_utc.isoformat(),
            "evidence_hash": self.evidence_hash,
            "fuentes": [f.a_dict() for f in self.fuentes],
        }


def construir_snapshot(event_id: str, symbol: str, cutoff_utc: dt.datetime,
                       fuentes: list[FuenteEvidencia]) -> Snapshot:
    """Construye un snapshot RECHAZANDO cualquier fuente no disponible al cutoff.

    Verifica `available_at <= cutoff` y `published_at <= cutoff` (F03/I.4). Una fuente
    futura invalida el snapshot: no se filtra en silencio, se lanza error, porque su
    presencia indica un bug de recolección que podría contaminar el experimento.
    """
    cutoff_utc = _exigir_aware("cutoff_utc", cutoff_utc)
    for f in fuentes:
        if f.available_at > cutoff_utc:
            raise EvidenciaInvalida(
                f"fuente {f.source_id} available_at {f.available_at.isoformat()} "
                f"> cutoff {cutoff_utc.isoformat()} (fuga temporal)")
        if f.published_at > cutoff_utc:
            raise EvidenciaInvalida(
                f"fuente {f.source_id} published_at posterior al cutoff (fuga)")
    return Snapshot(event_id=event_id, symbol=symbol, cutoff_utc=cutoff_utc,
                    fuentes=tuple(fuentes))


def paquete_titulares(fuentes: list[FuenteEvidencia], max_titulares: int = 5) -> dict:
    """Paquete textual determinista para P2/P3 (I.4).

    - solo fuentes tipo 'titular';
    - dedup por `content_hash` (identidad canónica) y por `source_id`;
    - orden estable: (published_at, source_id, content_hash);
    - máximo `max_titulares`;
    - si no hay ninguno: token NO_MACRO_EVENT, score central 0, vector neutral.
    """
    titulares = [f for f in fuentes if f.tipo == "titular"]
    vistos_hash: set[str] = set()
    vistos_src: set[str] = set()
    unicos: list[FuenteEvidencia] = []
    for f in titulares:
        h = f.content_hash
        if h in vistos_hash or f.source_id in vistos_src:
            continue
        vistos_hash.add(h)
        vistos_src.add(f.source_id)
        unicos.append(f)
    unicos.sort(key=lambda f: (f.published_at.isoformat(), f.source_id, f.content_hash))
    unicos = unicos[:max_titulares]
    if not unicos:
        return {
            "token": TOKEN_SIN_EVENTO, "items": [],
            "hash": hash_canonico({"token": TOKEN_SIN_EVENTO}),
        }
    items = [{
        "source_id": f.source_id,
        "texto": str(f.contenido.get("texto", ""))[:1000],
        "categoria": f.contenido.get("categoria"),
        "published_at": f.published_at.isoformat(),
        "content_hash": f.content_hash,
    } for f in unicos]
    return {
        "token": "MACRO", "items": items,
        "hash": hash_canonico([it["content_hash"] for it in items]),
    }
