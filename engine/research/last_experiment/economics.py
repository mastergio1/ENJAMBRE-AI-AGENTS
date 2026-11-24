"""L8 — Evaluación económica sin dinero real (paper trading). (I.9.1)

Una prueba de Brier no demuestra rentabilidad. Esta simulación contable aplica una
política SIMPLE y congelada idéntica a todos los modelos: `p>=0.55` largo, `p<=0.45`
corto (o long/flat si no se modela el corto), caso contrario efectivo. Cartera
ficticia de USD 10.000 (parámetro de test, NUNCA capital del usuario), tamaño máximo
por tramo 1/2 de equity, exposición bruta <= 100%, hasta dos posiciones de 2 sesiones
simultáneas, mark-to-market diario, sin apalancamiento. Costes: base 5 bps/lado,
estrés 10 bps/lado. El coste incremental del ABM/API se imputa a P5, amortizado por
sesión. NO se realizan operaciones reales.

Gate económico: P5 PnL neto >0 y > P4 y > B* a exposición comparable, en base y estrés;
drawdown de P5 no peor que P4 por más de 2 pp. Sharpe se reporta sin interpretarlo como
robusto en muestra pequeña.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .config import Economia


def politica(p: float, eco: Economia) -> int:
    """Dirección de la operación: +1 largo, -1 corto, 0 efectivo."""
    if p >= eco.umbral_largo:
        return 1
    if p <= eco.umbral_corto:
        return -1 if eco.variante == "long_short" else 0
    return 0


@dataclass
class Trade:
    entry_session: str
    exit_session: str
    direction: int        # +1/-1/0
    r: float              # retorno total del instrumento (decimal) entrada->salida
    marks: list | None = None  # retornos por sesión intermedios para MtM (opcional)


def _orden_sesiones(trades: list[Trade]) -> list[str]:
    s = set()
    for t in trades:
        s.add(t.entry_session); s.add(t.exit_session)
    return sorted(s)


def simular(trades: list[Trade], eco: Economia, coste_bps: float,
            coste_extra_total: float = 0.0) -> dict:
    """Simula la cartera. Cada señal abre, en su sesión de entrada, una posición de
    tamaño = max_tramo_frac * equity_actual, respetando exposición bruta <= max_bruto.
    Realiza PnL a la salida; costes a la apertura y al cierre (2 lados). Mark-to-market
    por sesión si hay `marks`. Devuelve métricas; PnL en USD sobre `capital`."""
    cap0 = eco.capital
    equity = cap0
    # eventos cronológicos: apertura en entry, cierre en exit
    eventos = []
    for i, t in enumerate(trades):
        eventos.append((t.entry_session, "open", i))
        eventos.append((t.exit_session, "close", i))
    # orden: por sesión; en una misma sesión, cerrar antes de abrir (liquidar primero)
    orden = {"close": 0, "open": 1}
    eventos.sort(key=lambda e: (e[0], orden[e[1]]))

    abiertas: dict[int, dict] = {}
    pnl_realizado = 0.0
    turnover = 0.0
    serie_equity = [cap0]
    costo_frac = coste_bps / 10000.0

    for sesion, tipo, i in eventos:
        t = trades[i]
        if tipo == "open":
            if t.direction == 0:
                continue
            bruto = sum(p["notional"] for p in abiertas.values())
            cupo = max(0.0, eco.max_bruto * equity - bruto)
            notional = min(eco.max_tramo_frac * equity, cupo)
            if notional <= 0:
                continue
            costo = notional * costo_frac
            pnl_realizado -= costo
            turnover += notional
            abiertas[i] = {"notional": notional, "dir": t.direction, "r": t.r}
        else:  # close
            pos = abiertas.pop(i, None)
            if pos is None:
                continue
            bruto_pnl = pos["dir"] * pos["r"] * pos["notional"]
            costo = pos["notional"] * costo_frac
            pnl_realizado += bruto_pnl - costo
            turnover += pos["notional"]
            equity = cap0 + pnl_realizado
            serie_equity.append(equity)

    # coste incremental (ABM/API) imputado al final
    pnl_realizado -= coste_extra_total
    equity_final = cap0 + pnl_realizado

    # drawdown sobre la serie de equity realizada
    pico = -math.inf; dd = 0.0
    for e in serie_equity + [equity_final]:
        pico = max(pico, e)
        dd = max(dd, (pico - e) / pico if pico > 0 else 0.0)

    # retornos por operación cerrada para Sharpe (diagnóstico)
    rets = []
    for t in trades:
        if t.direction != 0:
            rets.append(t.direction * t.r - 2 * costo_frac)
    sharpe = None
    if len(rets) >= 2:
        mu = sum(rets) / len(rets)
        sd = math.sqrt(sum((x - mu) ** 2 for x in rets) / (len(rets) - 1))
        sharpe = (mu / sd * math.sqrt(len(rets))) if sd > 1e-12 else None

    return {
        "pnl_neto_usd": round(pnl_realizado, 2),
        "retorno_pct": round(100 * pnl_realizado / cap0, 4),
        "max_drawdown_pct": round(100 * dd, 4),
        "turnover_usd": round(turnover, 2),
        "n_operaciones": sum(1 for t in trades if t.direction != 0),
        "exposicion_media": round(turnover / (2 * cap0), 4) if cap0 else None,
        "sharpe": round(sharpe, 3) if sharpe is not None else None,
        "coste_incremental_usd": round(coste_extra_total, 4),
    }


def trades_de_modelo(registros: list[dict], model_id: str, eco: Economia) -> list[Trade]:
    """Construye trades para un modelo desde filas resueltas {p_up, r, entry_session,
    exit_session}."""
    out = []
    for r in registros:
        if r["model_id"] != model_id:
            continue
        if r.get("r") is None:
            continue
        out.append(Trade(
            entry_session=r.get("entry_session") or r.get("emision"),
            exit_session=r.get("exit_session") or r.get("emision"),
            direction=politica(float(r["p_up"]), eco),
            r=float(r["r"]), marks=r.get("marks")))
    return out


def buy_and_hold(registros: list[dict], eco: Economia, coste_bps: float) -> dict:
    """Referencia descriptiva buy&hold SPY (siempre largo, mismas entradas/salidas)."""
    vistos = {}
    for r in registros:
        s = r.get("entry_session") or r.get("emision")
        if s not in vistos and r.get("r") is not None:
            vistos[s] = Trade(s, r.get("exit_session") or s, 1, float(r["r"]))
    return simular(list(vistos.values()), eco, coste_bps)


def evaluar_economia(registros: list[dict], b_star: str, eco: Economia,
                     coste_base_bps: float = 5.0, coste_estres_bps: float = 10.0,
                     coste_extra_p5_usd: float = 0.0) -> dict:
    """Simula P0–P5 + buy&hold en base y estrés, y aplica el gate económico."""
    modelos = ["P0", "P1", "P2", "P3", "P4", "P5"]
    out = {"base": {}, "estres": {}, "buy_and_hold": {}}
    for etq, bps in (("base", coste_base_bps), ("estres", coste_estres_bps)):
        for m in modelos:
            extra = coste_extra_p5_usd if m == "P5" else 0.0
            out[etq][m] = simular(trades_de_modelo(registros, m, eco), eco, bps, extra)
        out["buy_and_hold"][etq] = buy_and_hold(registros, eco, bps)

    comparadores = ["P4"] + ([b_star] if b_star and b_star != "P4" else [])

    def gate(etq):
        p5 = out[etq]["P5"]
        if p5["pnl_neto_usd"] <= 0:
            return False
        for c in comparadores:
            if p5["pnl_neto_usd"] <= out[etq][c]["pnl_neto_usd"]:
                return False
            # drawdown de P5 no peor que el comparador por más de 2 pp
            if p5["max_drawdown_pct"] > out[etq][c]["max_drawdown_pct"] + eco.tolerancia_drawdown_pp:
                return False
        return True

    gate_base = gate("base")
    gate_estres = gate("estres")
    return {
        "metricas": out,
        "comparadores": comparadores,
        "gate_economico": bool(gate_base and gate_estres),
        "gate_base": gate_base, "gate_estres": gate_estres,
    }
