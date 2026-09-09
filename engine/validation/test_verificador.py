"""Tests del verificador (arnés): partición held-out estable y comparación
contra el baseline. Todo local, sin IA."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from calibration import verificador  # noqa: E402


def test_holdout_es_determinista():
    """El mismo sim_id cae SIEMPRE del mismo lado (no depende de random)."""
    ids = ["abc123", "def456", "ghi789", "0f0f0f0f"]
    primera = [verificador.es_holdout(i) for i in ids]
    for _ in range(5):
        assert [verificador.es_holdout(i) for i in ids] == primera


def test_holdout_separa_casos():
    """No todos los ids caen del mismo lado (la partición realmente divide)."""
    ids = [f"caso-{i:04d}" for i in range(500)]
    holdout = [i for i in ids if verificador.es_holdout(i)]
    visible = [i for i in ids if not verificador.es_holdout(i)]
    assert holdout and visible                       # ambos lados no vacíos
    # proporción cercana al 30% (con 500 ids, margen amplio por azar del hash)
    frac = len(holdout) / len(ids)
    assert 0.20 < frac < 0.40


def test_particionar_no_pierde_casos():
    casos = [{"sim_id": f"s{i}"} for i in range(200)]
    visible, holdout = verificador.particionar(casos)
    assert len(visible) + len(holdout) == len(casos)  # ninguno se pierde
    assert not (set(id(c) for c in visible) & set(id(c) for c in holdout))


def test_baseline_carga_y_tiene_claves():
    base = verificador.cargar_baseline()
    assert base, "el baseline congelado debe existir"
    assert "acierto" in base and "dataset" in base
    assert isinstance(base["acierto"]["indice_negativa"], (int, float))


def test_comparar_promueve_mejora_limpia():
    """Una mejora sin degradar ningún régimen ES promovible."""
    base = {"acierto": {"indice_negativa": 0.38, "indice_positiva": 0.76}}
    nuevas = {"indice_negativa": 0.46, "indice_positiva": 0.76}  # sube neg, mantiene pos
    r = verificador.comparar(nuevas, base)
    assert r["promovible"] is True
    assert "indice_negativa" in r["mejoras"]


def test_comparar_bloquea_si_degrada_un_regimen():
    """Una mejora que ROMPE un régimen NO se promueve (criterio §5)."""
    base = {"acierto": {"indice_negativa": 0.38, "indice_positiva": 0.76}}
    nuevas = {"indice_negativa": 0.46, "indice_positiva": 0.60}  # sube neg pero hunde pos
    r = verificador.comparar(nuevas, base)
    assert r["promovible"] is False
    assert "indice_positiva" in r["degradaciones"]
