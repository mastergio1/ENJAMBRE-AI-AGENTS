"""Piloto de acontecimientos macroeconómicos, exclusivamente offline.

Valida fixtures y emite un informe JSON por stdout. Los aceptados quedan en
staging con precios pendientes. No conecta con SQLite, el motor ni proveedores.
Ejemplo desde engine/:
    python -m contenido.cosechador_macro --input ruta/events.json
"""

import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SCHEMA_VERSION = 1
HORIZON = "event_minus_1m_to_plus_5m"
BLOCKERS = ["missing_intraday_prices", "grouped_evaluation_protocol_pending",
            "missing_expectations"]


class ValidationError(ValueError):
    """Error de contrato que se puede incluir en el informe."""


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field}: se requiere texto no vacío")
    return value


def _object(value, field):
    if not isinstance(value, dict):
        raise ValidationError(f"{field}: se requiere un objeto")
    return value


def _timestamp(value, field):
    _text(value, field)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValidationError(f"{field}: timestamp ISO inválido") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValidationError(f"{field}: falta zona horaria explícita")
    return parsed


def _utc(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _url(value, field):
    _text(value, field)
    try:
        parts = urlsplit(value)
        if (parts.scheme != "https" or not parts.hostname or parts.username
                or parts.password or parts.port not in (None, 443)):
            raise ValueError()
    except ValueError as error:
        raise ValidationError(f"{field}: se requiere una URL HTTPS pública") from error
    query = sorted((key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
                   if not key.lower().startswith("utm_")
                   and key.lower() not in {"fbclid", "gclid"})
    return urlunsplit(("https", parts.hostname.lower(), parts.path.rstrip("/"),
                       urlencode(query), ""))


def _facts(facts, field, event_time, available):
    if not isinstance(facts, list):
        raise ValidationError(f"{field}: se requiere una lista")
    if field == "released" and not facts:
        raise ValidationError("released: se requiere al menos un dato publicado")
    names = set()
    for fact in facts:
        _object(fact, field)
        name = _text(fact.get("name"), f"{field}.name")
        if name in names:
            raise ValidationError(f"{field}: dato repetido {name}")
        names.add(name)
        _text(fact.get("unit"), f"{field}.unit")
        value = fact.get("value")
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            raise ValidationError(f"{field}.value: se requiere texto o número")
        if isinstance(value, str):
            _text(value, f"{field}.value")
        else:
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValidationError(f"{field}.value: número no finito o fuera de rango")
        _url(fact.get("source_url"), f"{field}.source_url")
        fact_time = _timestamp(fact.get("available_at"), f"{field}.available_at")
        if field == "known_before" and fact_time >= event_time:
            raise ValidationError("known_before: contiene información del anuncio o posterior")
        if field == "released" and fact_time != available:
            raise ValidationError("released: disponibilidad distinta de la del anuncio")


def _validate_event(event, fixture_root):
    _object(event, "event")
    try:
        json.dumps(event, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValidationError("event: contenido JSON inválido o número no finito") from error
    for field in ("event_id", "correlation_group", "event_type", "headline"):
        _text(event.get(field), field)
    source = _object(event.get("primary_source"), "primary_source")
    _url(source.get("url"), "primary_source.url")
    _text(source.get("publisher"), "primary_source.publisher")
    event_time = _timestamp(event.get("timestamp"), "timestamp")
    available = _timestamp(event.get("available_at"), "available_at")
    zone_name = _text(event.get("timezone"), "timezone")
    try:
        zone = ZoneInfo(zone_name)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise ValidationError("timezone: zona IANA desconocida") from error
    local = event_time.astimezone(zone)
    if (local.utcoffset() != event_time.utcoffset()
            or local.replace(tzinfo=None) != event_time.replace(tzinfo=None)):
        raise ValidationError("timestamp: offset incompatible con la zona IANA y su horario estacional")
    if available < event_time:
        raise ValidationError("available_at: anterior al acontecimiento")
    _facts(event.get("known_before"), "known_before", event_time, available)
    if not event["known_before"]:
        _text(event.get("known_before_missing_reason"), "known_before_missing_reason")
    _facts(event.get("released"), "released", event_time, available)
    if "expected" not in event or event["expected"] is not None:
        raise ValidationError("expected: este piloto requiere null y documentar el consenso faltante")
    _text(event.get("expected_missing_reason"), "expected_missing_reason")
    if event.get("validation_status") != "source_verified":
        raise ValidationError("validation_status: se requiere source_verified")

    instruments = event.get("instruments")
    if not isinstance(instruments, list) or not instruments:
        raise ValidationError("instruments: se requiere una lista no vacía")
    symbols = set()
    for instrument in instruments:
        _object(instrument, "instrument")
        symbol = _text(instrument.get("symbol"), "instrument.symbol")
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9.^=-]{0,19}", symbol):
            raise ValidationError("instrument.symbol: símbolo canónico inválido")
        if symbol in symbols:
            raise ValidationError(f"instruments: símbolo repetido {symbol}")
        symbols.add(symbol)
        if instrument.get("market") not in {"indice", "accion", "cripto", "oro", "petroleo"}:
            raise ValidationError("instrument.market: mercado desconocido")
        _text(instrument.get("exposure_reason"), "instrument.exposure_reason")

    measurement = _object(event.get("measurement"), "measurement")
    if (measurement.get("horizon") != HORIZON
            or type(measurement.get("start_offset_seconds")) is not int
            or measurement["start_offset_seconds"] != -60
            or type(measurement.get("end_offset_seconds")) is not int
            or measurement["end_offset_seconds"] != 300):
        raise ValidationError("measurement: horizonte del piloto incompatible")
    if ("price_provider" not in measurement or measurement["price_provider"] is not None
            or measurement.get("price_status") != "missing"):
        raise ValidationError("measurement: este piloto admite únicamente precios pendientes")
    if measurement.get("session") not in {"regular", "extended"}:
        raise ValidationError("measurement.session: sesión inválida")
    if measurement.get("interpretation") != "descriptive_event_window":
        raise ValidationError("measurement.interpretation: se requiere ventana descriptiva")
    if available > event_time + timedelta(seconds=300):
        raise ValidationError("available_at: posterior al cierre de la ventana")

    provenance = _object(event.get("provenance"), "provenance")
    _text(provenance.get("extractor_version"), "provenance.extractor_version")
    retrieved = _timestamp(provenance.get("retrieved_at"), "provenance.retrieved_at")
    if retrieved < available:
        raise ValidationError("provenance.retrieved_at: anterior a la disponibilidad")
    relative = Path(_text(provenance.get("snapshot_path"), "provenance.snapshot_path"))
    root = Path(fixture_root).resolve()
    snapshot = (root / relative).resolve()
    if relative.is_absolute() or not snapshot.is_relative_to(root):
        raise ValidationError("provenance.snapshot_path: fuera del directorio de fixtures")
    digest = provenance.get("snapshot_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValidationError("provenance.snapshot_sha256: hash inválido")
    try:
        actual = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    except OSError as error:
        raise ValidationError("provenance.snapshot_path: snapshot no disponible") from error
    if actual != digest:
        raise ValidationError("provenance.snapshot_sha256: contenido distinto del verificado")


def _event_key(event):
    return (_url(event["primary_source"]["url"], "primary_source.url"),
            _utc(_timestamp(event["timestamp"], "timestamp")))


def _case_key(case):
    return (*_event_key(case["event"]), case["symbol"], case["measurement"]["horizon"])


def _event_metadata(event):
    """Congela el contenido común del anuncio al incorporar más instrumentos."""
    metadata = deepcopy(event)
    for field in ("event_id", "correlation_group", "instruments"):
        metadata.pop(field)
    metadata["primary_source"]["url"] = _url(metadata["primary_source"]["url"], "source")
    for field in ("timestamp", "available_at"):
        metadata[field] = _utc(_timestamp(metadata[field], field))
    for field in ("known_before", "released"):
        for fact in metadata[field]:
            fact["source_url"] = _url(fact["source_url"], "source")
            fact["available_at"] = _utc(_timestamp(fact["available_at"], "available_at"))
    return metadata


def _make_case(event, instrument):
    event_time = _timestamp(event["timestamp"], "timestamp")
    measurement = deepcopy(event["measurement"])
    measurement["start_at"] = _utc(event_time + timedelta(seconds=-60))
    measurement["end_at"] = _utc(event_time + timedelta(seconds=300))
    identity = json.dumps([event["event_id"], instrument["symbol"], HORIZON],
                          ensure_ascii=False, separators=(",", ":"))
    case_id = "macro-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()
    blockers = list(BLOCKERS)
    if not event["known_before"]:
        blockers.append("missing_prior_context")
    return {
        "case_id": case_id,
        "event_id": event["event_id"],
        "correlation_group": event["correlation_group"],
        "symbol": instrument["symbol"],
        "market": instrument["market"],
        "exposure_reason": instrument["exposure_reason"],
        "event": deepcopy(event),
        "measurement": measurement,
        "origin": "historical_reconstruction",
        "validation_status": "accepted_staging",
        "evaluation_ready": False,
        "blockers": blockers,
        "legacy_candidate": {
            "id": case_id, "fecha": event_time.date().isoformat(),
            "titular": event["headline"], "simbolo": instrument["symbol"],
            "mercado": instrument["market"],
        },
    }


def _existing_cases(existing, fixture_root):
    if existing is None:
        return []
    _object(existing, "existing")
    if (type(existing.get("schema_version")) is not int
            or existing["schema_version"] != SCHEMA_VERSION
            or existing.get("mode") != "offline_staging"
            or not isinstance(existing.get("staged"), list)):
        raise ValidationError("existing: formato de informe incompatible")
    result = []
    keys = set()
    case_ids = set()
    event_ids = {}
    event_groups = {}
    event_metadata = {}
    for case in existing["staged"]:
        _object(case, "existing.staged")
        event = case.get("event")
        _validate_event(event, fixture_root)
        instruments = {item["symbol"]: item for item in event["instruments"]}
        symbol = _text(case.get("symbol"), "existing.symbol")
        instrument = instruments.get(symbol)
        if instrument is None or case != _make_case(event, instrument):
            raise ValidationError("existing: registro inconsistente o alterado")
        key = _case_key(case)
        if key in keys or case["case_id"] in case_ids:
            raise ValidationError("existing: contiene registros duplicados")
        event_key = _event_key(event)
        if event["event_id"] in event_ids and event_ids[event["event_id"]] != event_key:
            raise ValidationError("existing: event_id reutilizado")
        if event_key in event_groups and event_groups[event_key] != event["correlation_group"]:
            raise ValidationError("existing: correlation_group incompatible")
        metadata = _event_metadata(event)
        if event_key in event_metadata and event_metadata[event_key] != metadata:
            raise ValidationError("existing: versiones incompatibles del mismo acontecimiento")
        event_ids[event["event_id"]] = event_key
        event_groups[event_key] = event["correlation_group"]
        event_metadata[event_key] = metadata
        keys.add(key)
        case_ids.add(case["case_id"])
        result.append(deepcopy(case))
    return result


def build_report(document, fixture_root, existing=None):
    """Valida y prepara candidatos, conservando el acumulado para reintentos.

    Un evento inválido se rechaza completo. Los demás continúan. Un informe
    previo corrupto aborta la operación para no perder la deduplicación.
    """
    _object(document, "input")
    if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise ValidationError("schema_version: versión incompatible")
    events = document.get("events")
    if not isinstance(events, list):
        raise ValidationError("events: se requiere una lista")
    previous = _existing_cases(existing, fixture_root)
    accepted, rejected, candidates = [], [], []
    seen_cases = {_case_key(case) for case in previous}
    event_ids = {case["event_id"]: _event_key(case["event"]) for case in previous}
    event_groups = {_event_key(case["event"]): case["correlation_group"] for case in previous}
    event_metadata = {_event_key(case["event"]): _event_metadata(case["event"]) for case in previous}
    for index, event in enumerate(events):
        label = {"input_index": index, "event_id": None}
        if isinstance(event, dict):
            label["event_id"] = event.get("event_id")
        try:
            _validate_event(event, fixture_root)
            event_key = _event_key(event)
            if event["event_id"] in event_ids and event_ids[event["event_id"]] != event_key:
                raise ValidationError("event_id: reutilizado para otro acontecimiento")
            if event_key in event_groups and event_groups[event_key] != event["correlation_group"]:
                raise ValidationError("correlation_group: conflicto para el mismo acontecimiento")
            metadata = _event_metadata(event)
            if event_key in event_metadata and event_metadata[event_key] != metadata:
                raise ValidationError("event: conflicto de versiones del mismo acontecimiento")
        except ValidationError as error:
            candidates.append(label)
            rejected.append({**label, "code": "invalid_event", "reason": str(error)})
            continue
        event_ids[event["event_id"]] = event_key
        event_groups[event_key] = event["correlation_group"]
        event_metadata[event_key] = metadata
        for instrument in event["instruments"]:
            case = _make_case(event, instrument)
            candidate = {**label, "case_id": case["case_id"], "symbol": case["symbol"]}
            candidates.append(candidate)
            key = _case_key(case)
            if key in seen_cases:
                rejected.append({**candidate, "code": "duplicate_case",
                                 "reason": "Acontecimiento, instrumento y horizonte ya presentes"})
                continue
            seen_cases.add(key)
            accepted.append(case)
    staged = previous + accepted
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "offline_staging",
        "counts": {
            "events": len(events), "candidates": len(candidates),
            "accepted": len(accepted), "rejected": len(rejected),
            "existing": len(previous), "staged": len(staged),
            "correlation_groups": len({case["correlation_group"] for case in staged}),
            "evaluation_ready": 0,
        },
        "candidates": candidates,
        "accepted": accepted,
        "rejected": rejected,
        "staged": staged,
    }


def _reject_json_constant(value):
    raise ValidationError(f"JSON: constante numérica no permitida {value}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Fixture JSON de acontecimientos")
    parser.add_argument("--existing", type=Path, help="Informe anterior para deduplicar")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"),
                              parse_constant=_reject_json_constant)
        existing = None
        if args.existing:
            existing = json.loads(args.existing.read_text(encoding="utf-8"),
                                  parse_constant=_reject_json_constant)
        report = build_report(document, args.input.parent, existing)
        output = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    except (OSError, UnicodeError, ValueError) as error:
        json.dump({"schema_version": SCHEMA_VERSION, "mode": "offline_staging",
                   "error": str(error)}, sys.stdout, ensure_ascii=False)
        print()
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
