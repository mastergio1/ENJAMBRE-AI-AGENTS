"""L7 / I.9 — Tests del evaluador: pérdidas constantes, sin señal, predicciones
perfectas, empates, ausencia de modelo, labels 0, cobertura, inversión del signo del
delta y bootstrap por bloques."""
from research.last_experiment import evaluate as ev


def _regs(pares):
    """pares: lista de (session, p4, p5, y). Construye filas P4 y P5."""
    out = []
    for s, p4, p5, y in pares:
        out.append({"model_id": "P4", "p_up": p4, "y": y, "session_id": s})
        out.append({"model_id": "P5", "p_up": p5, "y": y, "session_id": s})
    return out


def test_bootstrap_constante():
    d = [0.01] * 50
    r = ev.moving_block_bootstrap(d, block=5, resamples=2000, seed=1)
    assert abs(r["media"] - 0.01) < 1e-9
    assert abs(r["lo"] - 0.01) < 1e-9 and abs(r["hi"] - 0.01) < 1e-9


def test_predicciones_perfectas_p5_supera():
    # P5 perfecto (p=y), P4 siempre 0.5 -> Δ grande y positivo
    pares = [(f"2025-01-{i:02d}", 0.5, float(i % 2), float(i % 2)) for i in range(1, 60)]
    r = ev.evaluar(_regs(pares), b_star="P4", min_sesiones=10, min_cobertura=0.9,
                   resamples=2000)
    ic = r["resultados"]["P4"]["ic"]
    assert ic["media"] > 0.2
    assert ic["lo"] > 0.005
    assert r["resultados"]["P4"]["veredicto"] == "supera"
    assert r["gate_estadistico"] is True


def test_inversion_signo_delta_inferior():
    # P5 peor que P4 -> Δ negativo -> inferior
    pares = [(f"2025-02-{i:02d}", float(i % 2), 0.5, float(i % 2)) for i in range(1, 60)]
    r = ev.evaluar(_regs(pares), b_star="P4", min_sesiones=10, resamples=2000)
    ic = r["resultados"]["P4"]["ic"]
    assert ic["media"] < 0
    assert r["resultados"]["P4"]["veredicto"] == "inferior"
    assert r["gate_estadistico"] is False


def test_sin_senal_no_supera():
    pares = [(f"2025-03-{i:02d}", 0.5, 0.5, float(i % 2)) for i in range(1, 40)]
    r = ev.evaluar(_regs(pares), b_star="P4", min_sesiones=10, resamples=1000)
    assert r["resultados"]["P4"]["ic"]["media"] == 0.0
    assert r["gate_estadistico"] is False


def test_labels_todas_cero():
    pares = [(f"2025-04-{i:02d}", 0.6, 0.4, 0.0) for i in range(1, 30)]
    r = ev.evaluar(_regs(pares), b_star="P4", min_sesiones=5, resamples=500)
    # P5 (0.4) más cerca de 0 que P4 (0.6) -> Δ>0
    assert r["resultados"]["P4"]["ic"]["media"] > 0


def test_ausencia_de_modelo_baja_cobertura():
    pares = [(f"2025-05-{i:02d}", 0.6, 0.6, 1.0) for i in range(1, 21)]
    regs = _regs(pares)
    # quitar P5 de 5 sesiones
    regs = [r for r in regs if not (r["model_id"] == "P5"
            and r["session_id"] in {f"2025-05-{i:02d}" for i in range(1, 6)})]
    r = ev.evaluar(regs, b_star="P4", min_sesiones=5, resamples=500)
    cob = r["resultados"]["P4"]["conteos"]["cobertura"]
    assert cob is not None and cob < 1.0
    assert r["resultados"]["P4"]["conteos"]["fallos_por_modelo"]["P5"] == 5


def test_etiqueta_no_madura_no_puntua():
    pares = [(f"2025-06-{i:02d}", 0.6, 0.4, 1.0) for i in range(1, 10)]
    regs = _regs(pares)
    # una sesión sin y (no madura)
    regs.append({"model_id": "P4", "p_up": 0.6, "y": None, "session_id": "2025-06-30"})
    regs.append({"model_id": "P5", "p_up": 0.4, "y": None, "session_id": "2025-06-30"})
    r = ev.evaluar(regs, b_star="P4", min_sesiones=5, resamples=500)
    assert r["resultados"]["P4"]["conteos"]["n_mature"] == 9  # la no madura no cuenta


def test_gate_requiere_muestra_minima():
    pares = [(f"2025-07-{i:02d}", 0.5, 0.0, 0.0) for i in range(1, 10)]  # P5 perfecto
    r = ev.evaluar(_regs(pares), b_star="P4", min_sesiones=100, resamples=500)
    assert r["muestra_suficiente"] is False
    assert r["gate_estadistico"] is False  # aunque supere, n<100


def test_gate_doble_exige_b_star_distinto():
    # P5 supera a P4 pero NO a B*=P3 -> gate False (intersección)
    regs = []
    for i in range(1, 60):
        s = f"2025-08-{i % 28 + 1:02d}-{i}"
        y = float(i % 2)
        regs.append({"model_id": "P4", "p_up": 0.5, "y": y, "session_id": s})
        regs.append({"model_id": "P3", "p_up": y, "y": y, "session_id": s})  # P3 perfecto
        regs.append({"model_id": "P5", "p_up": (y * 0.9 + 0.05), "y": y, "session_id": s})
    r = ev.evaluar(regs, b_star="P3", min_sesiones=10, resamples=1000)
    # supera a P4 pero P3 es mejor que P5 -> no supera a B*
    assert r["resultados"]["P4"]["veredicto"] == "supera"
    assert r["resultados"]["P3"]["veredicto"] != "supera"
    assert r["gate_estadistico"] is False
