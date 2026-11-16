"""Tests de la herramienta de ablación por arquetipo (con casos sintéticos)."""

import json

from calibration import ablacion_arquetipos as ab


def _caso(fecha, pct_real, senales, cat="?"):
    return {
        "fecha": fecha,
        "reaccion_real": {"pct_real": pct_real, "categoria": cat},
        "senales_arquetipo": {a: {"senal_media": s, "confianza_media": 0.7, "n": 10}
                              for a, s in senales.items()},
    }


def _archivo_sintetico(tmp_path, n=120, seed=3):
    """Un arquetipo ('fomo_evangelista') ordena bien (señal ~ dirección real);
    otro ('contrarian_sabio') va al revés. El resto, ruido centrado."""
    import random
    rng = random.Random(seed)
    casos = []
    for i in range(n):
        sube = rng.random() < 0.5
        pct = rng.uniform(0.1, 3) if sube else -rng.uniform(0.1, 3)
        base = 0.6 if sube else -0.6
        senales = {a: rng.uniform(-0.3, 0.3) for a in ab.BASE}
        senales["fomo_evangelista"] = base + rng.uniform(-0.1, 0.1)      # buen predictor
        senales["contrarian_sabio"] = -base + rng.uniform(-0.1, 0.1)     # va al revés
        casos.append(_caso(f"2026-08-{i % 28 + 1:02d}T00:00:00", pct, senales))
    ruta = tmp_path / "casos.json"
    ruta.write_text(json.dumps({"n": len(casos), "casos": casos}))
    return str(ruta)


def test_cargar_filtra_y_ordena(tmp_path):
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"casos": [
        _caso("2026-08-02T00:00:00", 1.0, {a: 0.1 for a in ab.BASE}),
        _caso("2026-08-01T00:00:00", -1.0, {a: 0.1 for a in ab.BASE}),
        _caso("2026-08-03T00:00:00", 0.0, {a: 0.1 for a in ab.BASE}),   # pct 0 → fuera
        {"fecha": "x", "reaccion_real": {"pct_real": 1.0}, "senales_arquetipo": {}},  # sin arquetipos → fuera
    ]}))
    casos = ab.cargar(str(ruta))
    assert len(casos) == 2
    assert casos[0]["fecha"] < casos[1]["fecha"]  # ordenado
    assert casos[0]["y"] == 0 and casos[1]["y"] == 1


def test_analizar_estructura_y_senal(tmp_path):
    rep = ab.analizar(_archivo_sintetico(tmp_path))
    assert rep["n"] > 60
    for k in ("arquetipo_suelto", "consenso", "leave_one_out", "variantes"):
        assert k in rep
    # el buen predictor acierta más que el contrarian invertido
    assert (rep["arquetipo_suelto"]["fomo_evangelista"]["acierto"]
            > rep["arquetipo_suelto"]["contrarian_sabio"]["acierto"])
    # quitar el contrarian invertido no debe EMPEORAR el Brier (Δ <= algo pequeño)
    assert rep["leave_one_out"]["contrarian_sabio"]["delta"] <= 0.02


def test_acierto_direccional_medio_punto_en_cero():
    assert ab.acierto_direccional([0.0], [1]) == 50.0
    assert ab.acierto_direccional([0.5], [1]) == 100.0
    assert ab.acierto_direccional([-0.5], [1]) == 0.0
