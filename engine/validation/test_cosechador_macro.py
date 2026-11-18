"""Contrato del piloto macro offline y barreras contra fuga temporal."""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from shutil import copytree
import subprocess
import sys

import pytest

from contenido.cosechador_macro import ValidationError, build_report


FIXTURES = Path(__file__).parent / "fixtures" / "macro"
ENGINE = Path(__file__).resolve().parents[1]


@pytest.fixture
def document():
    return json.loads((FIXTURES / "events.json").read_text(encoding="utf-8"))


def test_piloto_conserva_ocho_casos_y_dos_acontecimientos(document):
    original = deepcopy(document)
    report = build_report(document, FIXTURES)

    assert report["counts"]["candidates"] == 8
    assert report["counts"]["accepted"] == 8
    assert report["counts"]["rejected"] == 0
    assert report["counts"]["correlation_groups"] == 2
    assert report["counts"]["evaluation_ready"] == 0
    assert len({case["case_id"] for case in report["accepted"]}) == 8
    assert document == original
    assert build_report(document, FIXTURES) == report

    for case in report["accepted"]:
        assert case["origin"] == "historical_reconstruction"
        assert case["evaluation_ready"] is False
        assert case["blockers"]
        assert case["measurement"]["price_provider"] is None
        assert "categoria" not in case["legacy_candidate"]
        assert "pct_real" not in case


def test_ventanas_intradia_se_convierten_a_utc(document):
    report = build_report(document, FIXTURES)
    windows = {
        (
            datetime.fromisoformat(case["measurement"]["start_at"]),
            datetime.fromisoformat(case["measurement"]["end_at"]),
        )
        for case in report["accepted"]
    }
    assert windows == {
        (
            datetime(2024, 9, 11, 12, 29, tzinfo=timezone.utc),
            datetime(2024, 9, 11, 12, 35, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 9, 18, 17, 59, tzinfo=timezone.utc),
            datetime(2024, 9, 18, 18, 5, tzinfo=timezone.utc),
        ),
    }


def test_reimportacion_rechaza_duplicados_sin_reemplazar(document):
    previous = build_report(document, FIXTURES)
    preserved = deepcopy(previous)
    report = build_report(document, FIXTURES, existing=previous)

    assert report["counts"]["accepted"] == 0
    assert report["counts"]["rejected"] == 8
    assert all(item["reason"] for item in report["rejected"])
    assert report["staged"] == previous["staged"]
    retry = build_report(document, FIXTURES, existing=report)
    assert retry["counts"]["accepted"] == 0
    assert retry["counts"]["rejected"] == 8
    assert previous == preserved


def test_duplicado_en_el_mismo_lote(document):
    document["events"].append(deepcopy(document["events"][0]))
    report = build_report(document, FIXTURES)
    assert report["counts"]["accepted"] == 8
    assert report["counts"]["rejected"] == 4


@pytest.mark.parametrize("url_suffix", ["#release", "?utm_source=fixture"])
def test_alias_de_evento_no_elude_deduplicacion(document, url_suffix):
    previous = build_report(document, FIXTURES)
    event = document["events"][0]
    document["events"] = [event]
    event["event_id"] += "-alias"
    event["primary_source"]["url"] += url_suffix

    report = build_report(document, FIXTURES, existing=previous)
    assert report["counts"]["accepted"] == 0
    assert report["rejected"]


def test_igual_instante_en_otro_formato_no_elude_deduplicacion(document):
    previous = build_report(document, FIXTURES)
    event = document["events"][0]
    document["events"] = [event]
    event["event_id"] += "-alias"
    event["timestamp"] = "2024-09-11T12:30:00+00:00"
    event["timezone"] = "UTC"
    report = build_report(document, FIXTURES, existing=previous)
    assert report["counts"]["accepted"] == 0
    assert report["rejected"]


def test_alias_de_tipo_id_y_grupo_no_duplica_la_misma_publicacion(document):
    previous = build_report(document, FIXTURES)
    event = document["events"][0]
    document["events"] = [event]
    event["event_type"] = "macro_release_alias"
    event["event_id"] += "-alias"
    event["correlation_group"] += "-alias"
    report = build_report(document, FIXTURES, existing=previous)
    assert not report["accepted"]
    assert report["rejected"]
    assert report["staged"] == previous["staged"]


def test_puerto_https_por_defecto_no_duplica_la_fuente(document):
    previous = build_report(document, FIXTURES)
    event = document["events"][0]
    document["events"] = [event]
    event["event_id"] += "-alias"
    event["primary_source"]["url"] = event["primary_source"]["url"].replace(
        "www.bls.gov/", "www.bls.gov:443/"
    )
    report = build_report(document, FIXTURES, existing=previous)
    assert not report["accepted"]
    assert report["rejected"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("timestamp", "2024-09-11T08:30:00"),
        ("timestamp", "2024-09-11T08:30:00-05:00"),
        ("timestamp", "2024-03-10T02:30:00-05:00"),
        ("timezone", "Mars/Olympus"),
        ("available_at", "2024-09-11T08:29:00-04:00"),
        ("event_id", ""),
        ("correlation_group", ""),
    ],
)
def test_rechaza_fechas_e_identidades_invalidas(document, field, value):
    document["events"] = [document["events"][0]]
    document["events"][0][field] = value
    report = build_report(document, FIXTURES)
    assert not report["accepted"]
    assert report["rejected"]


@pytest.mark.parametrize("field", ["primary_source", "headline", "released", "measurement"])
def test_exige_campos_para_reconstruir_el_caso(document, field):
    document["events"] = [document["events"][0]]
    del document["events"][0][field]
    report = build_report(document, FIXTURES)
    assert not report["accepted"]
    assert report["rejected"]


def test_dato_posterior_no_pasa_a_informacion_previa(document):
    event = document["events"][0]
    document["events"] = [event]
    fact = deepcopy(event["released"][0])
    fact["available_at"] = "2024-09-11T08:31:00-04:00"
    event["known_before"] = [fact]
    report = build_report(document, FIXTURES)
    assert not report["accepted"]
    assert report["rejected"]


def test_demora_de_disponibilidad_no_reclasifica_datos_del_anuncio(document):
    event = document["events"][0]
    document["events"] = [event]
    event["available_at"] = "2024-09-11T08:31:00-04:00"
    event["known_before"] = [deepcopy(event["released"][0])]
    for fact in event["released"]:
        fact["available_at"] = event["available_at"]
    report = build_report(document, FIXTURES)
    assert not report["accepted"]
    assert report["rejected"]


def test_cifra_fuera_de_rango_se_reporta_sin_abortar_el_lote(document):
    document["events"][0]["released"][0]["value"] = 10 ** 401
    report = build_report(document, FIXTURES)
    assert report["counts"]["accepted"] == 4
    assert report["rejected"]


def test_cifra_posterior_no_se_atribuye_al_anuncio(document):
    event = document["events"][0]
    document["events"] = [event]
    event["released"][0]["available_at"] = "2024-09-11T08:31:00-04:00"
    report = build_report(document, FIXTURES)
    assert not report["accepted"]
    assert report["rejected"]


@pytest.mark.parametrize("field", ["expected_missing_reason", "known_before_missing_reason"])
def test_falta_de_datos_debe_quedar_explicita(document, field):
    document["events"] = [document["events"][0]]
    del document["events"][0][field]
    report = build_report(document, FIXTURES)
    assert not report["accepted"]
    assert report["rejected"]


def test_snapshot_corrupto_no_se_acepta(document):
    document["events"] = [document["events"][0]]
    document["events"][0]["provenance"]["snapshot_sha256"] = "0" * 64
    report = build_report(document, FIXTURES)
    assert not report["accepted"]
    assert report["rejected"]


def test_snapshot_no_puede_salir_de_la_carpeta_de_fixtures(document, tmp_path):
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    snapshot = b"Fuente fuera de la carpeta autorizada"
    (tmp_path / "fuera.txt").write_bytes(snapshot)
    document["events"] = [document["events"][0]]
    document["events"][0]["provenance"]["snapshot_path"] = "../fuera.txt"
    document["events"][0]["provenance"]["snapshot_sha256"] = hashlib.sha256(snapshot).hexdigest()
    report = build_report(document, fixture_root)
    assert not report["accepted"]
    assert report["rejected"]


def test_id_reutilizado_para_otro_anuncio_se_rechaza(document):
    document["events"][1]["event_id"] = document["events"][0]["event_id"]
    report = build_report(document, FIXTURES)
    assert report["counts"]["accepted"] == 4
    assert report["rejected"]


def test_mismo_evento_no_puede_cambiar_grupo(document):
    previous = build_report(document, FIXTURES)
    document["events"] = [document["events"][0]]
    document["events"][0]["correlation_group"] += "-otro"
    report = build_report(document, FIXTURES, existing=previous)
    assert not report["accepted"]
    assert report["rejected"]


@pytest.mark.parametrize("document", [{}, {"schema_version": 1, "events": {}}, {"schema_version": True, "events": []}])
def test_documento_invalido_aborta_con_error_explicito(document):
    with pytest.raises(ValidationError):
        build_report(document, FIXTURES)


def test_informe_previo_alterado_aborta(document):
    previous = build_report(document, FIXTURES)
    previous["staged"][0]["evaluation_ready"] = True
    with pytest.raises(ValidationError):
        build_report(document, FIXTURES, existing=previous)


def test_version_booleana_del_informe_previo_es_invalida(document):
    previous = build_report(document, FIXTURES)
    previous["schema_version"] = True
    with pytest.raises(ValidationError):
        build_report(document, FIXTURES, existing=previous)


def test_tipo_invalido_en_informe_previo_da_error_de_contrato(document):
    previous = build_report(document, FIXTURES)
    previous["staged"][0]["symbol"] = []
    with pytest.raises(ValidationError):
        build_report(document, FIXTURES, existing=previous)


def test_informe_previo_con_ids_contradictorios_aborta(document):
    first = deepcopy(document)
    first["events"] = [first["events"][0]]
    second = deepcopy(document)
    second["events"] = [second["events"][1]]
    second["events"][0]["event_id"] = first["events"][0]["event_id"]
    previous = build_report(first, FIXTURES)
    previous["staged"] += build_report(second, FIXTURES)["staged"]
    with pytest.raises(ValidationError):
        build_report(document, FIXTURES, existing=previous)


def test_informe_previo_no_puede_dividir_un_evento_en_dos_grupos(document):
    first = deepcopy(document)
    first["events"] = [first["events"][0]]
    first["events"][0]["instruments"] = first["events"][0]["instruments"][:1]
    second = deepcopy(document)
    second["events"] = [second["events"][0]]
    second["events"][0]["instruments"] = second["events"][0]["instruments"][1:2]
    second["events"][0]["correlation_group"] += "-otro"
    previous = build_report(first, FIXTURES)
    previous["staged"] += build_report(second, FIXTURES)["staged"]
    with pytest.raises(ValidationError):
        build_report(document, FIXTURES, existing=previous)


def test_agregar_instrumentos_conserva_el_acontecimiento(document):
    document["events"] = [document["events"][0]]
    initial = deepcopy(document)
    initial["events"][0]["instruments"] = initial["events"][0]["instruments"][:1]
    previous = build_report(initial, FIXTURES)
    report = build_report(document, FIXTURES, existing=previous)
    assert report["counts"]["accepted"] == 3
    assert report["counts"]["rejected"] == 1
    assert report["counts"]["staged"] == 4
    assert report["counts"]["correlation_groups"] == 1


def test_ampliar_instrumentos_no_permite_reescribir_el_anuncio(document):
    document["events"] = [document["events"][0]]
    initial = deepcopy(document)
    initial["events"][0]["instruments"] = initial["events"][0]["instruments"][:1]
    previous = build_report(initial, FIXTURES)
    document["events"][0]["released"][0]["value"] = 9.9
    report = build_report(document, FIXTURES, existing=previous)
    assert not report["accepted"]
    assert report["rejected"]
    assert report["staged"] == previous["staged"]


def test_cli_offline_emite_json_y_no_crea_archivos(tmp_path):
    # El proceso hijo bloquea red y SQLite incluso si el módulo regresara.
    script = """
import runpy
import socket
import sqlite3

def forbidden(*args, **kwargs):
    raise AssertionError('El piloto intentó usar red o SQLite')

socket.socket.connect = forbidden
socket.create_connection = forbidden
sqlite3.connect = forbidden
runpy.run_module('contenido.cosechador_macro', run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script, "--input", str(FIXTURES / "events.json")],
        cwd=tmp_path,
        env={"PYTHONPATH": str(ENGINE)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"]["accepted"] == 8
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("numeric_literal", "exit_code", "error_field"),
    [("NaN", 2, "error"), ("Infinity", 2, "error"),
     ("-Infinity", 2, "error"), ("1e999", 0, "rejected")],
)
def test_cli_rechaza_numeros_no_finitos_con_error_json(
    document, tmp_path, numeric_literal, exit_code, error_field,
):
    copytree(FIXTURES / "sources", tmp_path / "sources")
    document["events"][0]["provenance"]["extra"] = "NUMERIC_LITERAL"
    fixture = tmp_path / "invalido.json"
    fixture.write_text(json.dumps(document).replace('"NUMERIC_LITERAL"', numeric_literal),
                       encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-B", "-m", "contenido.cosechador_macro", "--input", str(fixture)],
        cwd=tmp_path,
        env={"PYTHONPATH": str(ENGINE)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == exit_code
    assert json.loads(result.stdout)[error_field]
    assert "Traceback" not in result.stderr
