"""Tests del evaluador prospectivo (Fase 6). Sin red."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from calibration import evaluar_prospectivo as ep


def _r(mercado, direccion, pct_real, fecha, fiable=0, abstenido=0, prob=None):
    return {"mercado": mercado, "direccion": direccion, "pct_real": pct_real,
            "fecha": fecha, "fiable": fiable, "abstenido": abstenido, "probabilidad": prob}


def test_puntuables_excluye_abstenidas_y_no_resueltas():
    regs = [_r("indice", "alza", 2.0, "2026-01-01"),
            _r("indice", "baja", -1.0, "2026-01-02", abstenido=1),   # abstenida
            _r("indice", "neutra", 1.0, "2026-01-03"),               # sin dirección
            _r("indice", "alza", None, "2026-01-04")]                # sin resolver
    assert len(ep._puntuables(regs)) == 1


def test_acierto_y_cobertura():
    regs = [_r("indice", "alza", 2.0, "2026-01-01"),     # acierta
            _r("indice", "baja", -1.0, "2026-01-02"),     # acierta
            _r("indice", "alza", -1.0, "2026-01-03"),     # falla
            _r("indice", "alza", 1.0, "2026-01-04", abstenido=1)]  # abstenida
    r = ep.evaluar(regs, "indice")
    assert r["n_resueltas"] == 4 and r["cobertura_pct"] == 75.0
    assert r["acierto_todos"]["punto"] == 66.7  # 2 de 3


def test_solo_fiables():
    regs = [_r("indice", "alza", 2.0, "2026-01-01", fiable=1),
            _r("indice", "baja", 1.0, "2026-01-02", fiable=0)]  # no fiable, falla
    assert ep.evaluar(regs, "indice")["acierto_fiables"]["punto"] == 100.0


def test_brier_skill():
    regs = [_r("indice", "alza", 2.0, "2026-01-01", prob=0.9),
            _r("indice", "baja", -2.0, "2026-01-02", prob=0.1)]
    b = ep.evaluar(regs, "indice")["brier"]
    assert b["skill"] > 0  # probabilidades bien puestas baten la tasa base
