"""Tests del holdout congelado (Fase 0.4). Sin red."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import holdout as ho


def _casos(n=10):
    # ids 0..n-1, fechas crecientes, etiqueta alterna
    return [{"id": i, "y": i % 2, "fecha": f"2026-01-{i+1:02d}"} for i in range(n)]


def test_construir_separa_los_mas_recientes():
    m = ho.construir_manifiesto(_casos(10), pct_holdout=20)
    assert m["n_holdout"] == 2 and m["n_desarrollo"] == 8
    assert m["holdout_ids"] == ["8", "9"]  # los 2 más recientes
    assert m["esquema"] == "holdout-v1" and len(m["hash"]) == 64


def test_no_parte_un_dia_entre_train_y_test():
    # dos casos comparten la fecha de corte → ambos van al holdout
    casos = _casos(8) + [{"id": 99, "y": 1, "fecha": "2026-01-07"}]  # mismo día que id 6
    m = ho.construir_manifiesto(casos, pct_holdout=25)
    # el corte cae en 2026-01-07; los dos casos de ese día quedan en el holdout
    ids = set(m["holdout_ids"])
    assert "6" in ids and "99" in ids


def test_verificar_ok_si_intacto():
    casos = _casos(10)
    m = ho.construir_manifiesto(casos, pct_holdout=20)
    r = ho.verificar_manifiesto(m, casos)
    assert r["ok"] and r["hash_coincide"] and r["faltantes"] == []


def test_verificar_detecta_etiqueta_revisada():
    casos = _casos(10)
    m = ho.construir_manifiesto(casos, pct_holdout=20)
    # alguien "revisa" la etiqueta de un caso del holdout (id 8)
    for c in casos:
        if c["id"] == 8:
            c["y"] = 1 - c["y"]
    r = ho.verificar_manifiesto(m, casos)
    assert not r["ok"] and not r["hash_coincide"]


def test_verificar_detecta_caso_faltante():
    casos = _casos(10)
    m = ho.construir_manifiesto(casos, pct_holdout=20)
    casos = [c for c in casos if c["id"] != 9]  # se borró un caso del holdout
    r = ho.verificar_manifiesto(m, casos)
    assert not r["ok"] and r["faltantes"] == ["9"]


def test_anadir_datos_no_cambia_membresia():
    casos = _casos(10)
    m = ho.construir_manifiesto(casos, pct_holdout=20)
    # llegan casos nuevos MÁS recientes; el manifiesto NO se recalcula
    nuevos = casos + [{"id": 50, "y": 1, "fecha": "2026-02-01"}]
    r = ho.verificar_manifiesto(m, nuevos)
    assert r["ok"]  # el holdout congelado (ids 8,9) sigue intacto
    dev, hold = ho.particionar(nuevos, m)
    assert {str(c["id"]) for c in hold} == {"8", "9"}  # el nuevo NO entra al holdout


def test_embargo_purga_cercanos_al_corte():
    casos = _casos(10)
    sin = ho.construir_manifiesto(casos, pct_holdout=20, embargo_dias=0)
    con = ho.construir_manifiesto(casos, pct_holdout=20, embargo_dias=3)
    # el embargo quita del desarrollo los casos dentro de 3 días antes del corte
    assert con["n_desarrollo"] < sin["n_desarrollo"]
    assert con["n_holdout"] == sin["n_holdout"]  # el holdout no cambia
