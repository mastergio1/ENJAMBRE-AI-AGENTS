"""L10 — CLI del experimento: validate-data, train, dry-run, freeze, seal, resolve,
finalize.

`seal`, `resolve` y `finalize` ACTIVAN el experimento (sellado en vivo, resolución con
datos reales, veredicto). Están BLOQUEADOS salvo que se pase `--aprobado-por-fundador`
Y exista un manifest congelado; sin eso, el comando se niega y explica por qué (I.3.1:
"detén la activación hasta aprobación del fundador"). `train`/`dry-run` son de
desarrollo y no tocan producción ni gastan dinero.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

from . import evaluate as ev
from . import economics as ec
from . import resolver as rs
from .config import MODELOS, Manifiesto, hash_canonico
from .models import (ModeloLogistico, ModeloP0, ModeloPlatt, brier, cargar_modelo,
                     fila_features)


# ------------------------------------------------- fixture sintético (dry-run)
def generar_fixture(n: int = 160, seed: int = 7) -> tuple[list[dict], list[dict]]:
    """Genera `n` eventos sintéticos con señal LLM real + ruido y features ABM
    sintéticas (NO corre el motor; el dry-run prueba la CAÑERÍA, no el ABM real).
    Devuelve (registros_con_y, eventos_para_sellar)."""
    from .config import ABMCfg, ARQUETIPOS
    rng = random.Random(seed); np.random.seed(seed)
    regs = []
    base = 100.0
    fecha0 = __import__("datetime").date(2025, 1, 2)
    from . import calendar as cal
    emi = fecha0
    for i in range(n):
        while not cal.es_sesion(emi):
            emi += __import__("datetime").timedelta(days=1)
        r5 = rng.gauss(0, 0.02); sc = rng.gauss(0, 1.0)
        logit = 7.0 * r5 + 0.9 * sc
        pstar = 1 / (1 + np.exp(-logit))
        y = 1.0 if rng.random() < pstar else 0.0
        r_real = (0.01 if y else -0.01) * (1 + abs(rng.gauss(0, 1)))
        arqs = {a: max(-1, min(1, sc + rng.gauss(0, 0.3))) for a in ARQUETIPOS}
        abm = {k: rng.gauss(0, 1) for k in ABMCfg().features}
        # el ABM sintético NO añade información real (coherente con el hallazgo)
        regs.append({
            "emision": emi.isoformat(),
            "features_mercado": {"ret_1": rng.gauss(0, 0.01), "ret_5": r5,
                                 "ret_20": rng.gauss(0, 0.03),
                                 "vol_20": abs(rng.gauss(0.01, 0.003)),
                                 "momentum_5_20": rng.gauss(0, 0.01)},
            "features_macro": {"sorpresa": rng.gauss(0, 1), "sorpresa_falta": 0.0,
                               "sorpresa_std": rng.gauss(0, 1), "sorpresa_std_falta": 0.0},
            "llm": {"score_titular": sc + rng.gauss(0, 0.2), "score_contextual": sc,
                    "archetypes": arqs, "uncertainty": 0.5},
            "abm": abm, "y": y, "r": r_real,
        })
        emi += __import__("datetime").timedelta(days=1)
    return regs, regs


# ------------------------------------------------------------- entrenamiento
def entrenar_bundle(regs: list[dict], grid=(0.01, 0.1, 1.0)) -> tuple[dict, dict]:
    """Entrena P0–P5 sobre `regs` (con 'y'). Devuelve (bundle, meta con B* y potencia).
    División temporal: primeras 70% desarrollo-train, 30% validación OOS."""
    y = [r["y"] for r in regs]
    n = len(regs)
    corte = int(n * 0.7)
    tr, va = regs[:corte], regs[corte:]
    ytr = [r["y"] for r in tr]
    bundle = {
        "P0": ModeloP0.entrenar(ytr),
        "P1": ModeloLogistico.entrenar("P1", tr, ytr, "P1", grid),
        "P2": ModeloPlatt.entrenar("P2", [r["llm"]["score_titular"] for r in tr], ytr, "score_titular"),
        "P3": ModeloPlatt.entrenar("P3", [r["llm"]["score_contextual"] for r in tr], ytr, "score_contextual"),
        "P4": ModeloLogistico.entrenar("P4", tr, ytr, "P4", grid),
        "P5": ModeloLogistico.entrenar("P5", tr, ytr, "P5", grid),
    }
    # B*: menor Brier OOS entre P0–P4 (preseleccionado antes de T0)
    brier_oos = {}
    for mid in ("P0", "P1", "P2", "P3", "P4"):
        pv = [bundle[mid].proba_una(r) for r in va]
        brier_oos[mid] = brier(pv, [r["y"] for r in va]) if va else None
    b_star = min((m for m in brier_oos if brier_oos[m] is not None),
                 key=lambda m: brier_oos[m]) if va else "P4"
    # potencia: sigma de d_t = loss_P4 - loss_P5 en validación OOS
    dts = []
    for r in va:
        p4 = bundle["P4"].proba_una(r); p5 = bundle["P5"].proba_una(r)
        dts.append((p4 - r["y"]) ** 2 - (p5 - r["y"]) ** 2)
    sigma = float(np.std(dts)) if len(dts) > 1 else None
    potencia = _reporte_potencia(sigma)
    meta = {"b_star": b_star, "brier_oos": brier_oos, "sigma_d": sigma,
            "potencia": potencia, "n_train": len(tr), "n_val": len(va)}
    return bundle, meta


def _reporte_potencia(sigma: float | None) -> dict:
    """n ≈ (1.96+0.84)^2 σ²/(Δ_real−0.005)² para Δ_real 0.010 y 0.020 (I.6)."""
    if not sigma or sigma <= 0:
        return {"sigma": sigma, "nota": "sin sigma estimable"}
    z = (1.96 + 0.84) ** 2
    out = {"sigma": round(sigma, 5)}
    for delta in (0.010, 0.020):
        denom = (delta - 0.005) ** 2
        out[f"n_para_delta_{delta}"] = int(np.ceil(z * sigma ** 2 / denom))
    return out


def bundle_a_dict(bundle: dict) -> dict:
    return {mid: m.a_dict() for mid, m in bundle.items()}


def bundle_desde_dict(d: dict) -> dict:
    return {mid: cargar_modelo(md) for mid, md in d.items()}


# ----------------------------------------------------------------- comandos
def cmd_validate_data(args) -> int:
    man = Manifiesto.cargar(args.config)
    problemas = man.validar()
    print("== validate-data ==")
    print(f"manifiesto: {args.config}")
    print(f"experiment_id: {man.experiment_id}  symbol: {man.symbol}")
    if problemas:
        print("PROBLEMAS de configuración:")
        for p in problemas:
            print("  -", p)
    else:
        print("configuración base: OK")
    # disponibilidad de datos de desarrollo
    dev = args.dev or man.a_dict().get("dev_panel")
    if dev and Path(dev).exists():
        regs = json.loads(Path(dev).read_text())
        print(f"panel de desarrollo: {dev} ({len(regs)} filas)")
    else:
        print("panel de desarrollo: NO DISPONIBLE (bloqueo).")
        print("  → Requiere construir panel histórico PIT de SPY con proveedor de")
        print("    precios aprobado (Alpaca/Yahoo con contrato) + FRED/BLS/BEA para")
        print("    macro. No incluido: necesita claves y aprobación (ver RUNBOOK).")
    from . import abm
    print(f"motor ABM disponible (mesa+model): {abm.disponible()}")
    return 0 if not problemas else 1


def cmd_train(args) -> int:
    if args.fixture == "synthetic":
        regs, _ = generar_fixture(args.n, args.seed)
        print(f"[train] usando fixture sintético ({len(regs)} filas) — SOLO desarrollo")
    else:
        regs = json.loads(Path(args.dev).read_text())
        print(f"[train] panel de desarrollo {args.dev} ({len(regs)} filas)")
    bundle, meta = entrenar_bundle(regs)
    salida = Path(args.out)
    salida.parent.mkdir(parents=True, exist_ok=True)
    artefacto = {"bundle": bundle_a_dict(bundle), "meta": meta,
                 "artifact_hash": hash_canonico(bundle_a_dict(bundle))}
    salida.write_text(json.dumps(artefacto, indent=2, ensure_ascii=False))
    print(f"[train] artefacto → {salida}")
    print(f"[train] B* preseleccionado: {meta['b_star']}  (Brier OOS {meta['brier_oos']})")
    print(f"[train] potencia: {meta['potencia']}")
    return 0


def cmd_dry_run(args) -> int:
    """End-to-end sintético: entrena, sella 6 probabilidades por evento, resuelve con
    precios ficticios, evalúa (Brier pareado + bootstrap) y corre paper trading."""
    import tempfile
    from .ledger import Ledger
    from .evidence import construir_snapshot, FuenteEvidencia
    import datetime as dt

    regs, _ = generar_fixture(args.n, args.seed)
    corte = int(len(regs) * 0.6)
    tr, te = regs[:corte], regs[corte:]
    bundle, meta = entrenar_bundle(tr)
    b_star = meta["b_star"]
    print(f"== dry-run (fixture sintético, n={len(regs)}) ==")
    print(f"entrenado con {len(tr)}; sellando {len(te)}; B*={b_star}")

    tmp = Path(tempfile.mkdtemp()) / "dry.sqlite"
    led = Ledger(tmp)
    man = Manifiesto(experiment_id="DRYRUN", b_star=b_star)
    precios = {}
    from . import calendar as cal
    for r in te:
        emi = r["emision"]
        contrato = rs.contrato_desde_emision("SPY", emi, 2)
        # precios ficticios coherentes con r (entrada 100 → salida 100*(1+r))
        precios[("SPY", contrato["entrada_sesion"])] = 100.0
        precios[("SPY", contrato["salida_sesion"])] = 100.0 * (1 + r["r"])
        # sellar los 6 modelos directamente (cañería; sin motor real)
        reg5 = r
        for mid in MODELOS:
            cual = "P5" if mid == "P5" else ("P4" if mid == "P4" else "P1")
            p = bundle[mid].proba_una(reg5)
            _sellar_directo(led, man, mid, contrato, p, bundle[mid].model_hash())
    # resolver
    prov = rs.FixturePrecios(precios)
    ahora = dt.datetime(2030, 1, 1, tzinfo=dt.timezone.utc)
    for r in te:
        contrato = rs.contrato_desde_emision("SPY", r["emision"], 2)
        try:
            o = rs.resolver_evento(contrato, prov, ahora)
            led.resolver(o)
        except Exception as e:  # noqa: BLE001
            print("  resolver:", e)
    registros = led.registros_evaluables("DRYRUN")
    print(f"registros evaluables: {len(registros)}  cadena_ok: {led.verificar_cadena()}")
    resu = ev.evaluar(registros, b_star, min_sesiones=10)
    print("Brier por modelo:", {k: round(v, 4) for k, v in resu["brier_por_modelo"].items()})
    for cmp, rr in resu["resultados"].items():
        ic = rr["ic"]
        if ic["media"] is None:
            print(f"  P5 vs {cmp}: sin pares → {rr['veredicto']}")
            continue
        print(f"  P5 vs {cmp}: Δ={ic['media']:.4f} IC95 [{ic['lo']:.4f},{ic['hi']:.4f}] "
              f"→ {rr['veredicto']} (n={ic['n']})")
    print(f"gate estadístico: {resu['gate_estadistico']} "
          f"(n_paired={resu['n_paired']}, cobertura={resu['cobertura']})")
    eco = ec.evaluar_economia(registros, b_star, man.economia)
    print(f"paper trading base P4={eco['metricas']['base']['P4']['pnl_neto_usd']} "
          f"P5={eco['metricas']['base']['P5']['pnl_neto_usd']} "
          f"buy&hold={eco['metricas']['buy_and_hold']['base']['pnl_neto_usd']}")
    print(f"gate económico: {eco['gate_economico']}")
    led.cerrar()
    print("\nNOTA: dry-run prueba la CAÑERÍA con datos sintéticos. NO es evidencia")
    print("predictiva. El ABM sintético no aporta información por diseño.")
    return 0


def _sellar_directo(led, man, model_id, contrato, p, model_hash):
    from .ledger import SealedForecast
    import datetime as dt
    led.registrar_experimento(man.experiment_id, "dry", "dry")
    led.registrar_evento(man.experiment_id, contrato["event_id"], "SPY",
                         contrato["cutoff_utc"], contrato["deadline_utc"],
                         contrato["entrada_sesion"], contrato["salida_sesion"], "h", "v1")
    emi = dt.datetime.fromisoformat(contrato["cutoff_utc"])
    f = SealedForecast(
        experiment_id=man.experiment_id, event_id=contrato["event_id"], model_id=model_id,
        symbol="SPY", issued_at=emi.isoformat(), cutoff_at=contrato["cutoff_utc"],
        deadline_at=contrato["deadline_utc"], p_up=float(p),
        abstained=(man.economia.umbral_corto < p < man.economia.umbral_largo),
        model_hash=model_hash, evidence_hash="h", config_hash="c", feature_hash="f",
        code_commit="dry", latency_ms=1, cost_usd=0.0)
    led.sellar(f)


def cmd_freeze(args) -> int:
    man = Manifiesto.cargar(args.config)
    if not man.t0:
        print("[freeze] ERROR: fija T0 en el manifiesto antes de congelar.")
        return 1
    man.t1 = man.derivar_t1()
    if args.artifact and Path(args.artifact).exists():
        art = json.loads(Path(args.artifact).read_text())
        man.b_star = art["meta"]["b_star"]
        man.hash_artefactos = art.get("artifact_hash")
    man.hash_codigo = _hash_codigo()
    man.hash_calendario = _hash_calendario()
    man.hash_prompts = _hash_prompts()
    man.hash_datos = args.hash_datos or man.hash_datos or "PENDIENTE_PANEL_PIT"
    man.code_commit = args.commit or man.code_commit or "PENDIENTE"
    problemas = man.validar(exigir_freeze=True)
    if problemas:
        print("[freeze] NO congelable todavía:")
        for p in problemas:
            print("  -", p)
        return 1
    Path(args.out).write_text(json.dumps(man.a_dict(), indent=2, ensure_ascii=False, default=str))
    print(f"[freeze] manifiesto congelado → {args.out}")
    print(f"  T0={man.t0} T1={man.t1} B*={man.b_star} config_hash={man.hash_config()[:12]}")
    return 0


def _bloqueo_activacion(cmd: str, args) -> int:
    print(f"== {cmd} ==")
    if not getattr(args, "aprobado_por_fundador", False):
        print("BLOQUEADO: la activación requiere aprobación EXPLÍCITA del fundador.")
        print("  Este comando sella/resuelve en vivo o emite el veredicto. El protocolo")
        print("  (I.1/I.3.1) prohíbe activarlo sin aprobación, presupuesto congelado y")
        print("  proveedor de datos PIT aprobado. Pasa --aprobado-por-fundador solo")
        print("  cuando Giorgio lo autorice por escrito. Ver docs/last-experiment/RUNBOOK.md.")
        return 2
    man_ruta = Path(args.manifest)
    if not man_ruta.exists():
        print("ERROR: falta el manifiesto congelado (ejecuta freeze primero).")
        return 1
    man = Manifiesto.cargar(man_ruta)
    problemas = man.validar(exigir_freeze=True)
    if problemas:
        print("ERROR: manifiesto no está correctamente congelado:", problemas)
        return 1
    print("Aprobación recibida y manifiesto congelado válido.")
    print("  (La ejecución en vivo requiere el proveedor de precios PIT y el scheduler")
    print("   durables; ver RUNBOOK. Este esqueleto no contacta servicios por sí mismo.)")
    return 0


def cmd_seal(args):
    return _bloqueo_activacion("seal", args)


def cmd_resolve(args):
    return _bloqueo_activacion("resolve", args)


def cmd_finalize(args):
    return _bloqueo_activacion("finalize", args)


# ------------------------------------------------------------------- hashes
def _raiz() -> Path:
    return Path(__file__).resolve().parent


def _hash_codigo() -> str:
    hs = {}
    for f in sorted(_raiz().glob("*.py")):
        hs[f.name] = hash_canonico(f.read_text(encoding="utf-8"))
    return hash_canonico(hs)


def _hash_calendario() -> str:
    from . import calendar as cal
    import datetime as dt
    muestras = {}
    for anio in range(2025, 2028):
        muestras[str(anio)] = sorted(d.isoformat() for d in cal.festivos(anio))
    return hash_canonico(muestras)


def _hash_prompts() -> str:
    from . import llm
    return hash_canonico({"sistema": llm.SISTEMA, "instruccion": llm.INSTRUCCION,
                          "parser": llm.PARSER_V, "modelo": llm.MODELO})


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="research.last_experiment.cli",
                                description="THE LAST EXPERIMENT — CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("validate-data"); s.add_argument("--config", required=True)
    s.add_argument("--dev", default=None); s.set_defaults(func=cmd_validate_data)

    s = sub.add_parser("train")
    s.add_argument("--config", default=None); s.add_argument("--dev", default=None)
    s.add_argument("--fixture", default=None); s.add_argument("--n", type=int, default=160)
    s.add_argument("--seed", type=int, default=7)
    s.add_argument("--out", default="artifacts/bundle.json"); s.set_defaults(func=cmd_train)

    s = sub.add_parser("dry-run")
    s.add_argument("--fixture", default="synthetic"); s.add_argument("--n", type=int, default=160)
    s.add_argument("--seed", type=int, default=7); s.set_defaults(func=cmd_dry_run)

    s = sub.add_parser("freeze")
    s.add_argument("--config", required=True); s.add_argument("--out", default="../docs/last-experiment/manifest.json")
    s.add_argument("--artifact", default=None); s.add_argument("--hash-datos", default=None)
    s.add_argument("--commit", default=None); s.set_defaults(func=cmd_freeze)

    for nombre, fn in (("seal", cmd_seal), ("resolve", cmd_resolve), ("finalize", cmd_finalize)):
        s = sub.add_parser(nombre)
        s.add_argument("--manifest", required=True)
        s.add_argument("--aprobado-por-fundador", action="store_true", dest="aprobado_por_fundador")
        s.set_defaults(func=fn)
    return p


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
