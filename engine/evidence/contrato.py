"""Contrato de la capa de evidencia point-in-time (Fase 1).

El objeto de evidencia representa LO QUE SE SABÍA en el momento del evento
(`as_of`): hechos, expectativas previas, qué pudo estar descontado, fuentes con su
fecha, contradicciones e incertidumbre. La regla sagrada: **nada posterior al
`as_of` puede entrar** — si una fuente o una expectativa es más nueva que el
`as_of`, se rechaza (eso sería ver el futuro, la fuga que arruina un backtest).

Este módulo define y VALIDA el contrato; es puro (sin red). La recuperación real de
fuentes (macro, consenso) vive en adaptadores aparte. Se usa en MODO SOMBRA:
produce la evidencia sin alterar todavía las predicciones del enjambre.
"""
import hashlib
import json
from datetime import datetime, timezone

ESQUEMA_VERSION = "v1"


class EvidenciaInvalida(ValueError):
    """El objeto de evidencia viola el contrato (p. ej. una fuente del futuro)."""


def _parse(ts, campo="timestamp"):
    """ISO-8601 → datetime con zona (UTC si viene naive). Lanza si no parsea."""
    if not ts or not isinstance(ts, str):
        raise EvidenciaInvalida(f"{campo} ausente o no es texto: {ts!r}")
    try:
        d = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError as e:
        raise EvidenciaInvalida(f"{campo} no es ISO-8601 válido: {ts!r}") from e
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def validar_fuente(fuente, as_of):
    """Una fuente debe tener `published_at` fiable y NO posterior al `as_of`.

    `as_of` puede ser str ISO o datetime. Lanza EvidenciaInvalida si falla."""
    as_of_dt = as_of if isinstance(as_of, datetime) else _parse(as_of, "as_of")
    pub = _parse(fuente.get("published_at"), "fuente.published_at")
    if pub > as_of_dt:
        raise EvidenciaInvalida(
            f"fuente {fuente.get('source_id','?')} publicada {pub.isoformat()} "
            f"es POSTERIOR al as_of {as_of_dt.isoformat()} (fuga de futuro)")


def validar_expectativa(exp, as_of):
    """Una expectativa (consenso previo) debe traer `vintage` (cuándo se fijó), y
    ese vintage no puede ser posterior al as_of."""
    as_of_dt = as_of if isinstance(as_of, datetime) else _parse(as_of, "as_of")
    vintage = _parse(exp.get("vintage"), "expectativa.vintage")
    if vintage > as_of_dt:
        raise EvidenciaInvalida(
            f"expectativa con vintage {vintage.isoformat()} posterior al as_of")


def hash_evidencia(ev: dict) -> str:
    """Hash estable del objeto (JSON canónico, sin el propio campo de hash)."""
    sin_hash = {k: v for k, v in ev.items() if k != "evidence_hash"}
    crudo = json.dumps(sin_hash, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()


def construir_evidencia(*, event_id, activo, as_of, titular, event_timestamp=None,
                        entity=None, hechos=None, expectativas=None, info_nueva=None,
                        descontado=None, fuentes=None, contradicciones=None,
                        incertidumbres=None, info_faltante=None, zona_horaria="UTC"):
    """Ensambla y VALIDA un objeto de evidencia (el ensamblador de modo sombra).

    Rechaza cualquier fuente o expectativa posterior al `as_of`. Devuelve el objeto
    versionado y con su hash. No toca el enjambre ni las predicciones."""
    as_of_dt = _parse(as_of, "as_of")
    fuentes = fuentes or []
    expectativas = expectativas or []
    for f in fuentes:
        validar_fuente(f, as_of_dt)
    for e in expectativas:
        validar_expectativa(e, as_of_dt)
    # F03 (auditoría científica): un HECHO observado no puede ser posterior al corte.
    # El hash garantiza integridad del contenido, no su validez causal: una fecha de
    # evento en el futuro contaminaría la predicción aun con hash válido. Un evento
    # FUTURO programado (p. ej. el próximo FOMC) es admisible, pero como `scheduled_at`,
    # no como `event_timestamp` de un hecho ya ocurrido.
    if event_timestamp is not None:
        if _parse(event_timestamp, "event_timestamp") > as_of_dt:
            raise EvidenciaInvalida(
                f"event_timestamp ({event_timestamp}) es posterior al as_of ({as_of}): "
                f"un hecho observado no puede venir del futuro. Si es un evento "
                f"programado conocido, pásalo como scheduled_at, no como event_timestamp.")

    ev = {
        "event_id": event_id,
        "asset": activo,
        "entity": entity,
        "event_timestamp": event_timestamp,
        "as_of_timestamp": as_of_dt.isoformat(),
        "timezone": zona_horaria,
        "headline": titular,
        "facts": hechos or [],
        "expectations": expectativas,
        "new_information": info_nueva or [],
        "priced_in_assessment": descontado or {"value": None, "evidence": [],
                                               "uncertainty": "high"},
        "sources": fuentes,
        "contradictions": contradicciones or [],
        "uncertainties": incertidumbres or [],
        "missing_information": info_faltante or [],
        "evidence_version": ESQUEMA_VERSION,
    }
    ev["evidence_hash"] = hash_evidencia(ev)
    return ev


def formatear_para_cerebro(ev: dict) -> str:
    """Convierte la evidencia en un bloque de texto conciso para el prompt del
    cerebro (la entrada del brazo 'D' del experimento B-vs-D). Solo vuelca lo que
    la evidencia ya trae validado; nunca inventa. El brazo 'B' usa solo el titular;
    el 'D' usa titular + este bloque."""
    lineas = [f"Titular: {ev.get('headline', '')}"]
    ctx = []

    def _agrega(etiqueta, items, campo="texto"):
        vals = [str(x.get(campo, x) if isinstance(x, dict) else x) for x in (items or [])]
        vals = [v for v in vals if v]
        if vals:
            ctx.append(f"{etiqueta}:\n- " + "\n- ".join(vals))

    _agrega("Hechos verificados", ev.get("facts"))
    exps = [f"{e.get('valor', '')} (fijada {e.get('vintage', '?')[:10]})"
            for e in ev.get("expectations", []) if e.get("valor")]
    if exps:
        ctx.append("Expectativa previa:\n- " + "\n- ".join(exps))
    _agrega("Información nueva", ev.get("new_information"))
    pia = ev.get("priced_in_assessment") or {}
    if pia.get("value") is not None:
        ctx.append(f"¿Ya estaba descontado?: {pia.get('value')} "
                   f"(certeza {pia.get('uncertainty', '?')})")
    _agrega("Contradicciones", ev.get("contradictions"))
    _agrega("Incertidumbre", ev.get("uncertainties"))
    _agrega("Información faltante", ev.get("missing_information"))

    if ctx:
        lineas.append("\nContexto disponible a la fecha del evento:")
        lineas.append("\n".join(ctx))
    return "\n".join(lineas)
