"""L6 — Tests del ledger sellado: idempotencia, inmutabilidad, hash-chain."""
import datetime as dt

import pytest

from research.last_experiment.ledger import (IntegrityError, Ledger, Outcome,
                                             SealedForecast)

UTC = dt.timezone.utc


def _sf(model_id="P4", p=0.6, event_id="SPY:2026-01-05:2D:v1"):
    cutoff = dt.datetime(2026, 1, 5, 20, 30, tzinfo=UTC)
    return SealedForecast(
        experiment_id="EXP", event_id=event_id, model_id=model_id, symbol="SPY",
        issued_at=cutoff.isoformat(), cutoff_at=cutoff.isoformat(),
        deadline_at=(cutoff + dt.timedelta(minutes=10)).isoformat(),
        p_up=p, abstained=False, model_hash="mh", evidence_hash="eh",
        config_hash="ch", feature_hash="fh", code_commit="abc", latency_ms=5,
        cost_usd=0.01)


def _led(tmp_path):
    led = Ledger(tmp_path / "le.sqlite")
    led.registrar_experimento("EXP", "mh", "abc")
    led.registrar_evento("EXP", "SPY:2026-01-05:2D:v1", "SPY",
                         "2026-01-05T20:30:00+00:00", "2026-01-05T20:40:00+00:00",
                         "2026-01-06", "2026-01-08", "eh", "v1")
    return led


def test_sellar_y_idempotencia(tmp_path):
    led = _led(tmp_path)
    r1 = led.sellar(_sf())
    assert r1["estado"] == "sellado"
    r2 = led.sellar(_sf())  # idéntico
    assert r2["estado"] == "idempotente"


def test_sellado_divergente_falla(tmp_path):
    led = _led(tmp_path)
    led.sellar(_sf(p=0.6))
    with pytest.raises(IntegrityError):
        led.sellar(_sf(p=0.7))  # misma clave, p distinta


def test_p_up_invalido_rechazado(tmp_path):
    led = _led(tmp_path)
    with pytest.raises(ValueError):
        led.sellar(_sf(p=1.5))


def test_trigger_bloquea_update_delete(tmp_path):
    led = _led(tmp_path)
    led.sellar(_sf())
    with pytest.raises(Exception):
        led.cx.execute("UPDATE le_forecast SET p_up=0.9")
    with pytest.raises(Exception):
        led.cx.execute("DELETE FROM le_forecast")


def test_hash_chain_verifica(tmp_path):
    led = _led(tmp_path)
    led.sellar(_sf("P0", 0.5))
    led.sellar(_sf("P4", 0.6))
    led.sellar(_sf("P5", 0.55))
    assert led.verificar_cadena()
    exp = led.exportar()
    assert exp["cadena_ok"] and len(exp["forecasts"]) == 3


def test_outcome_inmutable(tmp_path):
    led = _led(tmp_path)
    o = Outcome("SPY:2026-01-05:2D:v1", "2026-01-06", "2026-01-08", 100.0, 101.0,
                0.01, "2026-01-08T21:00:00+00:00", "dh", "2026-01-09T00:00:00+00:00")
    assert led.resolver(o)["y"] == 1
    assert led.resolver(o)["estado"] == "idempotente"
    with pytest.raises(Exception):
        led.cx.execute("UPDATE le_outcome SET return_decimal=-1")


def test_registros_evaluables_une_outcome(tmp_path):
    led = _led(tmp_path)
    led.sellar(_sf("P4", 0.6))
    led.sellar(_sf("P5", 0.55))
    led.resolver(Outcome("SPY:2026-01-05:2D:v1", "2026-01-06", "2026-01-08",
                         100.0, 101.0, 0.01, "2026-01-08T21:00:00+00:00", "dh",
                         "2026-01-09T00:00:00+00:00"))
    regs = led.registros_evaluables("EXP")
    assert len(regs) == 2
    assert all(r["y"] == 1 for r in regs)
    assert all(r["session_id"] == "2026-01-05" for r in regs)
