"""L1/L9 — Tests del manifiesto, identidad de eventos y validación de freeze."""
from research.last_experiment.config import Manifiesto, event_id, hash_canonico


def test_event_id_determinista():
    assert event_id("SPY", "2026-01-05", 2) == "SPY:2026-01-05:2D:v1"


def test_manifiesto_valido_base():
    m = Manifiesto(experiment_id="LE1")
    assert m.validar() == []


def test_capital_real_debe_ser_cero():
    m = Manifiesto(experiment_id="LE1", capital_real_usd=100.0)
    assert any("capital_real" in p for p in m.validar())


def test_symbol_debe_ser_spy():
    m = Manifiesto(experiment_id="LE1", symbol="QQQ")
    assert any("SPY" in p for p in m.validar())


def test_delta_min_congelado():
    m = Manifiesto(experiment_id="LE1", delta_min=0.01)
    assert any("delta_min" in p for p in m.validar())


def test_freeze_exige_t0_bstar_hashes():
    m = Manifiesto(experiment_id="LE1")
    problemas = m.validar(exigir_freeze=True)
    assert any("T0" in p for p in problemas)
    assert any("B*" in p for p in problemas)


def test_derivar_t1_seis_meses():
    m = Manifiesto(experiment_id="LE1", t0="2026-01-15")
    assert m.derivar_t1() == "2026-07-15"


def test_hash_config_estable():
    m1 = Manifiesto(experiment_id="LE1")
    m2 = Manifiesto(experiment_id="LE1")
    assert m1.hash_config() == m2.hash_config()
    m2.code_commit = "xyz"  # los hashes de congelación NO entran en hash_config
    assert m1.hash_config() == m2.hash_config()


def test_roundtrip_dict():
    m = Manifiesto(experiment_id="LE1", t0="2026-01-15", b_star="P4")
    m2 = Manifiesto.desde_dict(m.a_dict())
    assert m2.experiment_id == "LE1" and m2.b_star == "P4"
    assert m2.bootstrap.seed == 20261124
