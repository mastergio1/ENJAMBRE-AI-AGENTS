"""Tests de la comparación M4 (A2) vs A3, titular por titular. Sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import a2_vs_a3 as m
from calibration import ablacion


def _f(fecha, a2, a3, pc, mercado="indice", sim="SPY", tit=None):
    return {"fecha": fecha, "anio": int(fecha[:4]), "mercado": mercado, "simbolo": sim,
            "a2": a2, "senal": a3, "pct_corr": pc, "titular": tit or f"T {fecha} {sim}",
            "direccion_pct": 0.0}


def test_cobertura_comun_excluye_abstenciones_y_zona_muerta():
    filas = [_f("2025-01-01", 0.5, 0.4, 1.0),
             _f("2025-01-02", None, 0.4, 1.0),   # A2 sin dato
             _f("2025-01-03", 0.5, 0.0, 1.0),    # A3 se abstiene
             _f("2025-01-04", 0.5, 0.4, 0.1)]    # zona muerta
    c = m.cobertura(filas)
    assert c == {"direccionables": 3, "con_a2": 2, "con_a3": 2, "ambos": 1}
    assert len(m.pares(filas)) == 1


def test_discordancias_y_mcnemar():
    filas = [_f("2025-01-01", 0.5, -0.4, 1.0),   # solo A2
             _f("2025-01-02", 0.5, -0.4, 1.0),   # solo A2
             _f("2025-01-03", -0.5, 0.4, 1.0),   # solo A3
             _f("2025-01-04", 0.5, 0.4, 1.0),    # ambos ✓
             _f("2025-01-05", 0.5, 0.4, -1.0)]   # ambos ✗
    r = m.comparar(filas)
    assert (r["solo_a2"], r["solo_a3"], r["ambos_aciertan"], r["ambos_fallan"]) == (2, 1, 1, 1)
    assert r["acuerdo_signo"] == 40.0
    assert m.mcnemar_exacto(2, 1) == 1.0
    assert m.mcnemar_exacto(0, 10) < 0.01


def test_empate_es_no_distinguible():
    filas = [_f(f"2025-01-{d:02d}", 0.5, 0.5, 1.0 if d % 2 else -1.0) for d in range(1, 21)]
    r = m.comparar(filas)
    assert r["pareado"]["media"] == 0
    assert "no distinguible" in m.veredicto(r)


def test_a2_claramente_mejor_lo_detecta():
    filas = [_f(f"2025-{mo:02d}-{d:02d}", 0.5, -0.5, 1.0)
             for mo in range(1, 4) for d in range(1, 21)]
    r = m.comparar(filas)
    assert r["pareado"]["media"] == 1.0 and r["pareado"]["excluye_cero"]
    assert m.veredicto(r).startswith("A2 > A3")


def test_pareado_agrupa_por_evento():
    # 4 ETFs del mismo día cuentan como UN evento
    filas = [_f("2025-01-01", 0.5, -0.5, 1.0, sim=s) for s in ("SPY", "QQQ", "DIA", "IWM")]
    p = ablacion.pareado(filas, "A2_un_llm", "A3_consenso")
    assert p["n"] == 4 and p["n_eventos"] == 1


def test_gate_pareado_sigue_igual_tras_generalizar():
    filas = [{**_f(f"2025-01-{d:02d}", None, 0.5, 1.0), "direccion_pct": -1.0}
             for d in range(1, 11)]
    g = ablacion.gate_pareado(filas)
    assert g["media"] == -1.0 and g["n_eventos"] == 10 and g["excluye_cero"]


def test_tabla_titulares_pone_discordancias_primero_y_escapa_barras():
    filas = [_f("2025-01-01", 0.5, 0.4, 1.0, tit="ambos aciertan"),
             _f("2025-01-02", 0.5, -0.4, 1.0, tit="A2 gana | con barra")]
    t = m.tabla_titulares(filas).splitlines()
    assert len(t) == 4
    assert "solo A2 ✓" in t[2] and "A2 gana / con barra" in t[2]
    assert "ambos ✓" in t[3]
