"""Planifica particiones temporales usando exclusivamente metadatos del piloto."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from contenido.cosechador_macro import staged_observations


def _instant(value):
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError(f"El instante requiere zona horaria explícita: {value}")
    return dt.astimezone(timezone.utc)


def partition_metadata(report, fixture_root, *, train_from, development_from,
                       evaluation_from, evaluation_until, embargo_seconds):
    """Asigna cada grupo completo a un período o lo excluye con un motivo.

    Los extremos de una ventana cuentan como información utilizada. Por tanto,
    el final de la ventana debe preceder estrictamente al corte siguiente.
    """
    cuts = tuple(map(_instant, (train_from, development_from, evaluation_from, evaluation_until)))
    if not cuts[0] < cuts[1] < cuts[2] < cuts[3]:
        raise ValueError("Los cuatro límites temporales deben ser estrictamente crecientes")
    if type(embargo_seconds) is not int or embargo_seconds < 0:
        raise ValueError("El embargo debe expresarse en segundos enteros no negativos")

    groups = {}
    for row in staged_observations(report, fixture_root):
        groups.setdefault(row["event_group_id"], []).append(row)

    observations = []
    periods = ("train", "development", "evaluation")
    for group_id, rows in sorted(groups.items()):
        # La ventana descriptiva actual empieza antes del anuncio. Un grupo
        # puede abarcar varios comunicados y debe permanecer indivisible.
        start = min(_instant(row["measurement"]["start_at"]) for row in rows)
        end = max(_instant(row["measurement"]["end_at"]) for row in rows)
        partition = "excluded"
        reason = "outside_period" if start < cuts[0] or end >= cuts[-1] else "boundary_or_embargo"
        for index, name in enumerate(periods):
            remaining_seconds = (cuts[index + 1] - end).total_seconds()
            gap = embargo_seconds if name != "evaluation" else 0
            if start >= cuts[index] and remaining_seconds > gap:
                partition, reason = name, None
                break
        for row in sorted(rows, key=lambda r: r["observation_id"]):
            observations.append({
                "event_id": row["event_id"], "event_group_id": group_id,
                "observation_id": row["observation_id"], "simulation_id": row["simulation_id"],
                "symbol": row["symbol"], "horizon": row["measurement"]["horizon"],
                "origin": row["origin"], "evaluation_ready": row["evaluation_ready"],
                "available_at": row["event"]["available_at"],
                "start_at": row["measurement"]["start_at"], "end_at": row["measurement"]["end_at"],
                "partition": partition, "reason": reason,
            })
    return {
        "mode": "offline_partition_preview",
        "train_from": cuts[0].isoformat(), "development_from": cuts[1].isoformat(),
        "evaluation_from": cuts[2].isoformat(), "evaluation_until": cuts[3].isoformat(),
        "embargo_seconds": embargo_seconds, "observations": observations,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True, help="Informe completo de staging")
    parser.add_argument("--fixture-root", type=Path, required=True, help="Directorio de los extractos")
    for flag in ("train-from", "development-from", "evaluation-from", "evaluation-until"):
        parser.add_argument(f"--{flag}", required=True, help="Instante ISO 8601 con zona")
    parser.add_argument("--embargo-seconds", type=int, required=True)
    args = parser.parse_args()
    try:
        preview = partition_metadata(
            json.loads(args.report.read_text(encoding="utf-8")), args.fixture_root,
            train_from=args.train_from, development_from=args.development_from,
            evaluation_from=args.evaluation_from, evaluation_until=args.evaluation_until,
            embargo_seconds=args.embargo_seconds,
        )
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error al preparar las particiones: {error}\n")
    print(json.dumps(preview, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
