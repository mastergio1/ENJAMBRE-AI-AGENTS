"""L3 — Tests del snapshot PIT y paquete de titulares determinista."""
import datetime as dt

import pytest

from research.last_experiment.evidence import (EvidenciaInvalida, FuenteEvidencia,
                                               construir_snapshot, paquete_titulares)

UTC = dt.timezone.utc


def _f(sid, pub, tipo="titular", texto="CPI sube fuerte", cat="CPI"):
    return FuenteEvidencia(source_id=sid, tipo=tipo,
                           contenido={"texto": texto, "categoria": cat},
                           published_at=pub, observed_at=pub, available_at=pub)


def test_rechaza_fecha_naive():
    with pytest.raises(EvidenciaInvalida):
        _f("a", dt.datetime(2026, 1, 5, 12, 0))  # naive


def test_rechaza_fuente_posterior_al_cutoff():
    cutoff = dt.datetime(2026, 1, 5, 20, 30, tzinfo=UTC)
    futura = _f("a", cutoff + dt.timedelta(minutes=1))
    with pytest.raises(EvidenciaInvalida):
        construir_snapshot("SPY:2026-01-05:2D:v1", "SPY", cutoff, [futura])


def test_snapshot_valido_y_hash_estable():
    cutoff = dt.datetime(2026, 1, 5, 20, 30, tzinfo=UTC)
    f = _f("a", cutoff - dt.timedelta(hours=2))
    s1 = construir_snapshot("E", "SPY", cutoff, [f])
    s2 = construir_snapshot("E", "SPY", cutoff, [f])
    assert s1.evidence_hash == s2.evidence_hash
    assert "a" in s1.evidence_ids()


def test_paquete_dedup_y_orden():
    cutoff = dt.datetime(2026, 1, 5, 20, 30, tzinfo=UTC)
    p1 = cutoff - dt.timedelta(hours=3)
    p2 = cutoff - dt.timedelta(hours=1)
    f_dup = _f("a", p1)
    f_mismo_contenido = _f("b", p1)  # distinto id, mismo contenido/hora -> mismo hash
    f_tarde = _f("c", p2, texto="NFP débil", cat="empleo")
    paq = paquete_titulares([f_tarde, f_dup, f_dup, f_mismo_contenido])
    # dedup por content_hash: a y b comparten contenido+hora => uno cae
    ids = [it["source_id"] for it in paq["items"]]
    assert len(ids) == len(set(ids))
    # orden por published_at: el de p1 antes que el de p2
    assert paq["items"][0]["published_at"] <= paq["items"][-1]["published_at"]


def test_paquete_sin_titulares_token():
    paq = paquete_titulares([])
    assert paq["token"] == "NO_MACRO_EVENT"
    assert paq["items"] == []


def test_paquete_max_5():
    cutoff = dt.datetime(2026, 1, 5, 20, 30, tzinfo=UTC)
    fuentes = [_f(f"s{i}", cutoff - dt.timedelta(hours=i + 1), texto=f"nota {i}")
               for i in range(9)]
    paq = paquete_titulares(fuentes, max_titulares=5)
    assert len(paq["items"]) == 5
