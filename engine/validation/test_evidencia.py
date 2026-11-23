"""Tests del contrato de evidencia point-in-time (Fase 1). Sin red."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from evidence import contrato as ev


AS_OF = "2026-09-11T08:30:00+00:00"


def _fuente(pub, sid="s1"):
    return {"source_id": sid, "published_at": pub, "reliability": "alta"}


def test_fuente_del_futuro_rechazada():
    # publicada DESPUÉS del as_of → fuga de futuro
    with pytest.raises(ev.EvidenciaInvalida):
        ev.validar_fuente(_fuente("2026-09-12T10:00:00+00:00"), AS_OF)


def test_fuente_valida_pasa():
    ev.validar_fuente(_fuente("2026-09-10T10:00:00+00:00"), AS_OF)  # no lanza


def test_fuente_sin_timestamp_rechazada():
    with pytest.raises(ev.EvidenciaInvalida):
        ev.validar_fuente({"source_id": "s", "reliability": "alta"}, AS_OF)


def test_expectativa_sin_vintage_rechazada():
    with pytest.raises(ev.EvidenciaInvalida):
        ev.validar_expectativa({"valor": "CPI 3.1%"}, AS_OF)


def test_expectativa_del_futuro_rechazada():
    with pytest.raises(ev.EvidenciaInvalida):
        ev.validar_expectativa({"valor": "x", "vintage": "2026-09-20T00:00:00+00:00"}, AS_OF)


def test_construir_rechaza_fuente_futura():
    with pytest.raises(ev.EvidenciaInvalida):
        ev.construir_evidencia(event_id="e1", activo="SPY", as_of=AS_OF,
                               titular="CPI sorprende",
                               fuentes=[_fuente("2026-09-12T00:00:00+00:00")])


def test_construir_valido_tiene_todos_los_campos():
    e = ev.construir_evidencia(
        event_id="e1", activo="SPY", as_of=AS_OF, titular="CPI del mes",
        hechos=[{"texto": "CPI 3.2% vs 3.1% esperado"}],
        expectativas=[{"valor": "3.1%", "vintage": "2026-09-10T00:00:00+00:00"}],
        fuentes=[_fuente("2026-09-11T08:30:00+00:00")])
    for campo in ("event_id", "asset", "as_of_timestamp", "headline", "facts",
                  "expectations", "sources", "evidence_version", "evidence_hash"):
        assert campo in e
    assert e["evidence_version"] == "v1"


def test_hash_estable_y_sensible():
    base = dict(event_id="e1", activo="SPY", as_of=AS_OF, titular="CPI")
    a = ev.construir_evidencia(**base)
    b = ev.construir_evidencia(**base)
    assert a["evidence_hash"] == b["evidence_hash"]  # mismo input → mismo hash
    c = ev.construir_evidencia(**{**base, "titular": "otra noticia"})
    assert c["evidence_hash"] != a["evidence_hash"]  # input distinto → hash distinto
    # el hash no depende de sí mismo
    assert ev.hash_evidencia(a) == a["evidence_hash"]


def test_as_of_naive_se_asume_utc():
    # as_of sin zona no debe romper; se asume UTC
    e = ev.construir_evidencia(event_id="e", activo="SPY",
                               as_of="2026-09-11T08:30:00", titular="x")
    assert e["as_of_timestamp"].endswith("+00:00")


def test_formatear_para_cerebro_incluye_contexto():
    e = ev.construir_evidencia(
        event_id="e1", activo="SPY", as_of=AS_OF, titular="CPI del mes",
        hechos=[{"texto": "CPI 3.2% vs 3.1% esperado"}],
        expectativas=[{"valor": "3.1%", "vintage": "2026-09-10T00:00:00+00:00"}],
        info_faltante=[{"texto": "falta la guía futura"}])
    texto = ev.formatear_para_cerebro(e)
    assert "Titular: CPI del mes" in texto
    assert "CPI 3.2% vs 3.1% esperado" in texto
    assert "3.1%" in texto and "2026-09-10" in texto
    assert "falta la guía futura" in texto


def test_formatear_solo_titular_si_no_hay_contexto():
    e = ev.construir_evidencia(event_id="e", activo="SPY", as_of=AS_OF, titular="x")
    texto = ev.formatear_para_cerebro(e)
    assert texto == "Titular: x"  # brazo B: sin contexto, solo titular
