"""Comprueba particiones con metadatos locales y cortes de ejemplo."""

import json
from pathlib import Path

import pytest

from calibration.particiones_macro import partition_metadata
from contenido.cosechador_macro import build_report


FIXTURES = Path(__file__).parent / "fixtures" / "macro"
CUTS = {
    "train_from": "2024-09-01T00:00:00Z",
    "development_from": "2024-09-12T00:00:00Z",
    "evaluation_from": "2024-09-18T00:00:00Z",
    "evaluation_until": "2024-09-30T00:00:00Z",
    "embargo_seconds": 0,
}


@pytest.fixture
def events():
    return json.loads((FIXTURES / "events.json").read_text(encoding="utf-8"))


def test_export_import_particion_conserva_identidades(events):
    staged = build_report(events, FIXTURES)
    report = json.loads(json.dumps(staged))
    preview = partition_metadata(report, FIXTURES, **CUTS)
    rows = preview["observations"]
    assert preview["mode"] == "offline_partition_preview"
    assert {r["observation_id"] for r in rows} == {c["case_id"] for c in staged["staged"]}
    assert len(rows) == 8
    expected_partitions = {"us-cpi-2024-09-11": "train", "us-fomc-2024-09-18": "evaluation"}
    by_id = {c["case_id"]: c for c in staged["staged"]}
    for row in rows:
        case = by_id[row["observation_id"]]
        assert row["partition"] == expected_partitions[case["event_id"]]
        assert row["event_id"] == case["event_id"]
        assert row["event_group_id"] == case["correlation_group"]
        assert row["symbol"] == case["symbol"]
        assert row["horizon"] == case["measurement"]["horizon"]
        assert row["origin"] == "historical_reconstruction"
        assert row["simulation_id"] is None
        assert row["evaluation_ready"] is False
        assert row["reason"] is None
    assert report == staged


def test_grupo_que_abarca_dos_periodos_se_excluye_entero(events):
    for event in events["events"]:
        event["correlation_group"] = "grupo-compartido-de-prueba"
    report = build_report(events, FIXTURES)
    rows = partition_metadata(report, FIXTURES, **CUTS)["observations"]
    assert len(rows) == 8
    assert {r["event_id"] for r in rows} == {"us-cpi-2024-09-11", "us-fomc-2024-09-18"}
    assert {r["event_group_id"] for r in rows} == {"grupo-compartido-de-prueba"}
    assert {(r["partition"], r["reason"]) for r in rows} == {("excluded", "boundary_or_embargo")}


def test_particion_admite_export_original_v1():
    legacy = json.loads((FIXTURES / "report_v1.json").read_text(encoding="utf-8"))
    previous = legacy["staged"][0]
    row, = partition_metadata(legacy, FIXTURES, **CUTS)["observations"]
    assert row["observation_id"] == previous["case_id"]
    assert row["event_group_id"] == previous["correlation_group"]
    assert row["event_id"] == previous["event_id"]
    assert row["simulation_id"] is None


def test_fuera_del_periodo_se_documenta_y_evaluacion_no_recibe_embargo_final(events):
    cuts = dict(CUTS, train_from="2024-09-12T00:00:00Z", development_from="2024-09-14T00:00:00Z",
                evaluation_until="2024-09-18T18:05:01Z", embargo_seconds=60)
    rows = partition_metadata(build_report(events, FIXTURES), FIXTURES, **cuts)["observations"]
    classifications = {(r["event_id"], r["partition"], r["reason"]) for r in rows}
    assert classifications == {
        ("us-cpi-2024-09-11", "excluded", "outside_period"),
        ("us-fomc-2024-09-18", "evaluation", None),
    }


@pytest.mark.parametrize(
    ("development_from", "embargo_seconds", "partition"),
    [
        ("2024-09-11T12:29:00Z", 0, "development"),  # inicio inclusivo
        ("2024-09-11T12:35:00Z", 0, "excluded"),     # fin toca la frontera
        ("2024-09-11T12:35:01Z", 0, "train"),        # encaja por un segundo
        ("2024-09-11T12:36:00Z", 60, "excluded"),    # toca el embargo
        ("2024-09-11T12:36:01Z", 60, "train"),
    ],
)
def test_fronteras_y_embargo_en_tiempo_real(events, development_from, embargo_seconds, partition):
    events["events"] = events["events"][:1]
    cuts = dict(CUTS, development_from=development_from, embargo_seconds=embargo_seconds)
    rows = partition_metadata(build_report(events, FIXTURES), FIXTURES, **cuts)["observations"]
    assert len(rows) == 4
    assert {r["partition"] for r in rows} == {partition}


@pytest.mark.parametrize("changes", [
    {"embargo_seconds": -1},
    {"development_from": "2024-09-12T00:00:00"},
    {"evaluation_until": "fecha-inválida"},
    {"evaluation_from": CUTS["development_from"]},
    {"evaluation_until": CUTS["train_from"]},
])
def test_fechas_ambiguas_y_periodos_invalidos_se_rechazan(events, changes):
    with pytest.raises(ValueError):
        partition_metadata(build_report(events, FIXTURES), FIXTURES, **(CUTS | changes))


def test_rechaza_informe_con_registro_prospectivo_inyectado(events):
    report = build_report(events, FIXTURES)
    report["staged"][0]["origin"] = "prospective"
    with pytest.raises(ValueError):
        partition_metadata(report, FIXTURES, **CUTS)
