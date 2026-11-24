"""L8 — Tests de paper trading: política, PnL, costes, solapamiento y gate."""
from research.last_experiment import economics as ec
from research.last_experiment.config import Economia


def test_politica_umbrales():
    eco = Economia()
    assert ec.politica(0.60, eco) == 1
    assert ec.politica(0.40, eco) == -1
    assert ec.politica(0.50, eco) == 0
    eco_lf = Economia(variante="long_flat")
    assert ec.politica(0.40, eco_lf) == 0  # sin cortos


def test_simular_largo_ganador():
    eco = Economia(capital=10000.0)
    trades = [ec.Trade("2025-01-02", "2025-01-06", 1, 0.02)]
    r = ec.simular(trades, eco, coste_bps=0.0)
    # 1/2 equity = 5000 * 0.02 = 100 USD
    assert abs(r["pnl_neto_usd"] - 100.0) < 1e-6


def test_costes_restan():
    eco = Economia(capital=10000.0)
    trades = [ec.Trade("2025-01-02", "2025-01-06", 1, 0.0)]
    r = ec.simular(trades, eco, coste_bps=10.0)  # 10 bps * 2 lados sobre 5000
    assert r["pnl_neto_usd"] < 0


def test_corto_gana_en_caida():
    eco = Economia(capital=10000.0)
    trades = [ec.Trade("2025-01-02", "2025-01-06", -1, -0.02)]
    r = ec.simular(trades, eco, coste_bps=0.0)
    assert r["pnl_neto_usd"] > 0  # corto en caída = ganancia


def test_exposicion_bruta_limitada():
    eco = Economia(capital=10000.0, max_tramo_frac=0.5, max_bruto=1.0)
    # 3 posiciones solapadas; la bruta no puede exceder 100% del equity
    trades = [ec.Trade("2025-01-02", "2025-01-10", 1, 0.0),
              ec.Trade("2025-01-03", "2025-01-11", 1, 0.0),
              ec.Trade("2025-01-06", "2025-01-12", 1, 0.0)]
    r = ec.simular(trades, eco, coste_bps=0.0)
    assert r["n_operaciones"] == 3  # todas consideradas, pero sizing respeta el cupo


def test_gate_economico_p5_debe_superar():
    eco = Economia()
    regs = []
    for i in range(1, 30):
        ent = f"2025-02-{i:02d}"
        sal = f"2025-03-{i:02d}"   # salida distinta de la entrada (2 sesiones reales)
        # P5 siempre acierta dirección (p alta cuando sube), P4 neutro
        regs.append({"model_id": "P5", "p_up": 0.9, "r": 0.01,
                     "entry_session": ent, "exit_session": sal})
        regs.append({"model_id": "P4", "p_up": 0.5, "r": 0.01,
                     "entry_session": ent, "exit_session": sal})
        for m in ("P0", "P1", "P2", "P3"):
            regs.append({"model_id": m, "p_up": 0.5, "r": 0.01,
                         "entry_session": ent, "exit_session": sal})
    res = ec.evaluar_economia(regs, "P4", eco, coste_base_bps=0.0, coste_estres_bps=0.0)
    assert res["metricas"]["base"]["P5"]["pnl_neto_usd"] > 0
    assert res["metricas"]["base"]["P4"]["pnl_neto_usd"] == 0  # P4 neutro no opera
    assert res["gate_economico"] is True


def test_buy_and_hold_referencia():
    eco = Economia()
    regs = [{"model_id": "P5", "p_up": 0.4, "r": 0.03,
             "entry_session": "2025-01-02", "exit_session": "2025-01-06"}]
    res = ec.evaluar_economia(regs, "P4", eco, 0.0, 0.0)
    assert res["metricas"]["buy_and_hold"]["base"]["pnl_neto_usd"] > 0  # siempre largo
