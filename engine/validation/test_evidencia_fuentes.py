"""Tests de los adaptadores de evidencia (Fase 1). Sin red (fetch mockeado)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from evidence import fuentes, recoleccion, contrato


def _barras_subiendo(dias=30, inicio=100.0, paso=1.0):
    # genera barras diarias hasta 2026-09-10 (antes de un as_of 2026-09-11)
    from datetime import date, timedelta
    base = date(2026, 9, 10)
    out = []
    for i in range(dias):
        d = base - timedelta(days=dias - 1 - i)
        out.append((d.isoformat(), inicio + paso * i))
    return out


AS_OF = "2026-09-11T08:30:00+00:00"


def test_contexto_precio_solo_usa_barras_previas():
    # incluye una barra DEL día del as_of y una POSTERIOR; deben ignorarse
    barras = _barras_subiendo() + [("2026-09-11", 999.0), ("2026-09-12", 1000.0)]
    hechos, fuente = fuentes.contexto_precio("SPY", AS_OF, fetch=lambda s, f: barras)
    assert hechos and fuente
    # la fuente no puede ser del día del evento ni posterior
    assert fuente["published_at"][:10] < "2026-09-11"
    # con tendencia alcista, el retorno previo de 5 sesiones es positivo
    ret5 = next(h for h in hechos if h["clave"] == "ret_5")
    assert ret5["valor"] > 0


def test_contexto_precio_sin_datos():
    assert fuentes.contexto_precio("SPY", AS_OF, fetch=lambda s, f: None) == (None, None)
    assert fuentes.contexto_precio("SPY", AS_OF, fetch=lambda s, f: [("2026-09-01", 100.0)]) == (None, None)


def test_evidencia_para_es_valida_y_point_in_time():
    barras = _barras_subiendo()
    e = recoleccion.evidencia_para("SPY", "CPI sorprende", AS_OF,
                                   fetch_precio=lambda s, f: barras)
    # pasa el contrato (ninguna fuente del futuro) y trae el contexto
    assert e["evidence_version"] == "v1" and e["evidence_hash"]
    assert e["sources"] and e["facts"]
    texto = contrato.formatear_para_cerebro(e)
    assert "retorno previo" in texto


def test_evidencia_para_blindada_sin_datos():
    # sin barras: evidencia mínima (solo titular), sin romper
    e = recoleccion.evidencia_para("SPY", "x", AS_OF, fetch_precio=lambda s, f: None)
    assert e["facts"] == [] and e["sources"] == []
    assert contrato.formatear_para_cerebro(e) == "Titular: x"
