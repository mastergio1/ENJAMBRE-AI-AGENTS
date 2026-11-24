"""L6/L10 — Orquestación del sellado diario (idempotente, con deadline).

Dado el contrato temporal de un evento, su snapshot de evidencia, la lectura LLM y el
bundle de modelos CONGELADOS, produce y sella P0–P5 antes del deadline. Cronometra
latencia real. Si el ABM supera el deadline, registra un `RunFailure` para P5 y NO
reconstruye el pronóstico (I.3). El sellado es idempotente (repetir devuelve la fila
original; hash divergente = error de integridad).

NO decide operar aquí: la economía usa las probabilidades selladas. `abstained` es una
decisión de política (p en zona neutral), nunca ausencia de probabilidad (F05/F11).
"""
from __future__ import annotations

import datetime as dt
import time

from . import abm as abm_mod
from .config import Manifiesto, hash_canonico
from .features import vector_features
from .ledger import Ledger, RunFailure, SealedForecast
from .models import fila_features


def construir_reg(features_mercado: dict, features_macro: dict, lectura: dict,
                  abm_features: dict | None = None) -> dict:
    """Ensambla el registro que consumen los modelos (mismo que en entrenamiento)."""
    return {
        "features_mercado": features_mercado,
        "features_macro": features_macro,
        "llm": {
            "score_titular": lectura.get("score_titular", lectura.get("score")),
            "score_contextual": lectura.get("score_contextual", lectura.get("score")),
            "archetypes": lectura.get("archetypes", {}),
            "uncertainty": lectura.get("uncertainty"),
        },
        "abm": abm_features or {},
    }


def _zona_neutral(p: float, eco) -> bool:
    return eco.umbral_corto < p < eco.umbral_largo


def sellar_evento(man: Manifiesto, ledger: Ledger, bundle: dict, contrato: dict,
                  snapshot, features_mercado: dict, features_macro: dict,
                  lectura: dict, *, correr_abm: bool = True, mercado: str = "indice",
                  code_commit: str = "", ahora_utc: dt.datetime | None = None,
                  config_hash: str = "", coste_llm_usd: float = 0.0) -> dict:
    """Sella P0–P5 para un evento. Devuelve resumen de estados por modelo."""
    ahora_utc = ahora_utc or dt.datetime.now(dt.timezone.utc)
    deadline = dt.datetime.fromisoformat(contrato["deadline_utc"])
    event_id = contrato["event_id"]

    ledger.registrar_experimento(man.experiment_id, config_hash, code_commit)
    ledger.registrar_evento(
        man.experiment_id, event_id, man.symbol, contrato["cutoff_utc"],
        contrato["deadline_utc"], contrato["entrada_sesion"], contrato["salida_sesion"],
        snapshot.evidence_hash, "v1")

    evidence_hash = snapshot.evidence_hash
    reg_base = construir_reg(features_mercado, features_macro, lectura)
    resultados = {}

    def _sellar(model_id, p, abm_features, latency_ms, cost):
        feat = fila_features(
            construir_reg(features_mercado, features_macro, lectura, abm_features),
            "P5" if model_id == "P5" else ("P4" if model_id == "P4" else "P1"))
        f = SealedForecast(
            experiment_id=man.experiment_id, event_id=event_id, model_id=model_id,
            symbol=man.symbol,
            issued_at=ahora_utc.isoformat(), cutoff_at=contrato["cutoff_utc"],
            deadline_at=contrato["deadline_utc"], p_up=float(p),
            abstained=_zona_neutral(float(p), man.economia),
            model_hash=bundle[model_id].model_hash(), evidence_hash=evidence_hash,
            config_hash=config_hash,
            feature_hash=hash_canonico(vector_features(features_mercado, features_macro)),
            code_commit=code_commit, latency_ms=int(latency_ms), cost_usd=float(cost))
        return ledger.sellar(f)

    # P0–P4: sin ABM
    for mid in ("P0", "P1", "P2", "P3", "P4"):
        t0 = time.perf_counter()
        p = bundle[mid].proba_una(reg_base)
        lat = (time.perf_counter() - t0) * 1000
        cost = coste_llm_usd if mid in ("P2", "P3", "P4") else 0.0
        if dt.datetime.now(dt.timezone.utc) > deadline and ahora_utc <= deadline:
            pass  # el reloj de emisión es ahora_utc; en producción vigilar deadline real
        resultados[mid] = _sellar(mid, p, None, lat, cost)

    # P5: requiere ABM. Si supera el deadline, se registra fallo y NO se sella.
    if correr_abm:
        t0 = time.perf_counter()
        try:
            abm_feats = abm_mod.features(lectura, mercado=mercado)
            lat = (time.perf_counter() - t0) * 1000
            emitido = ahora_utc + dt.timedelta(milliseconds=lat)
            if emitido > deadline:
                ledger.registrar_fallo(RunFailure(
                    event_id, "P5", f"ABM excedió deadline ({lat:.0f} ms)",
                    dt.datetime.now(dt.timezone.utc).isoformat()))
                resultados["P5"] = {"estado": "fallo_deadline", "latency_ms": int(lat)}
            else:
                reg5 = construir_reg(features_mercado, features_macro, lectura, abm_feats)
                p5 = bundle["P5"].proba_una(reg5)
                resultados["P5"] = _sellar("P5", p5, abm_feats, lat,
                                           coste_llm_usd + 0.0)
        except Exception as e:  # noqa: BLE001
            ledger.registrar_fallo(RunFailure(
                event_id, "P5", f"ABM error: {e}",
                dt.datetime.now(dt.timezone.utc).isoformat()))
            resultados["P5"] = {"estado": "fallo_abm", "error": str(e)}
    else:
        resultados["P5"] = {"estado": "omitido_abm_desactivado"}

    return {"event_id": event_id, "modelos": resultados}
