"""L10 — Tests de integración: dry-run end-to-end y bloqueo de activación."""
from research.last_experiment import cli
from research.last_experiment.evidence import FuenteEvidencia
from research.last_experiment import llm


def test_dry_run_end_to_end(capsys):
    rc = cli.main(["dry-run", "--n", "120", "--seed", "3"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Brier por modelo" in out
    assert "gate estadístico" in out
    assert "gate económico" in out
    assert "cadena_ok: True" in out


def test_seal_bloqueado_sin_aprobacion(capsys):
    rc = cli.main(["seal", "--manifest", "/no/existe.json"])
    out = capsys.readouterr().out
    assert rc == 2
    assert "BLOQUEADO" in out


def test_resolve_y_finalize_bloqueados(capsys):
    assert cli.main(["resolve", "--manifest", "/no/existe.json"]) == 2
    assert cli.main(["finalize", "--manifest", "/no/existe.json"]) == 2


def test_train_fixture_produce_bstar(tmp_path, capsys):
    out_file = tmp_path / "bundle.json"
    rc = cli.main(["train", "--fixture", "synthetic", "--n", "140",
                   "--out", str(out_file)])
    out = capsys.readouterr().out
    assert rc == 0 and out_file.exists()
    assert "B* preseleccionado" in out
    assert "potencia" in out


def test_llm_fallback_schema_valido():
    # sin `obtener` (sin API) -> fallback léxico, schema válido
    paq = {"token": "MACRO", "hash": "h",
           "items": [{"source_id": "a", "texto": "CPI sube fuerte y rally", "categoria": "CPI"}]}
    r = llm.leer(paq)
    assert r["fuente"] == "fallback"
    assert set(r["archetypes"].keys()) == set(llm.ARQUETIPOS)
    assert -1.0 <= r["score"] <= 1.0


def test_llm_valida_schema_estricto():
    import pytest
    with pytest.raises(ValueError):
        llm.validar_json({"score": 0.5})  # faltan archetypes/uncertainty
    ok = llm.validar_json({"score": 2.0, "uncertainty": 0.5,
                           "archetypes": {a: 0.0 for a in llm.ARQUETIPOS}})
    assert ok["score"] == 1.0  # recortado a [-1,1]
