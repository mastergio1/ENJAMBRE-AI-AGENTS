"""Fase C: limpia la libreta y arma el banco de hold-out (US$0).

Lee datos/calibracion.json (ya pagado), saca ruido y sopas mal puntuadas,
parte índice+acción, congela 40 de ajuste + 80 de hold-out.

    python -m contenido.banco_calibracion

No gasta API. No toca producción.
"""

from __future__ import annotations

import json
from pathlib import Path

from brains.fallback import clasificar_titular
from contenido.corrector import evaluar_casos, mercado_de
from contenido.simbolo import apto_calibracion, es_ruido, es_sopa, simbolo_del_hecho

RUTA_CAJA = Path(__file__).resolve().parent.parent.parent / "datos" / "calibracion.json"
RUTA_BANCO = Path(__file__).resolve().parent / "fuentes" / "banco_holdout.json"

# titulares con los que se DISEÑÓ v1d: no pueden ser hold-out
_V1D = {
    "fed holds rates and flags a march increase, as widely expected",
    "fed pauses rate hikes but signals two more increases may lie ahead",
    "consumer prices come in line with expectations; fed keeps rates unchanged",
    "fed holds rates steady and repeats view that inflation pressures are transitory",
    "sweeping new us tariffs stun markets; stocks sink on trade war fears",
    "lehman brothers files for bankruptcy; global financial system reels",
    "s&p 500 plunges 12% despite fed emergency rate cut to zero",
    "amazon posts first quarterly loss since 2015 on weak outlook; shares tumble",
    "meta shares crater 20% on weak forecast and soaring metaverse spending",
    "target raises fy2026 gaap eps guidance from $8.50 to $9.90-$10.90 vs $8.39 est",
    "eli lilly could swing over $76 billion in value after earnings",
    "nvidia ceo says ai's future isn't just copper",
}


def _cargar() -> list[dict]:
    if not RUTA_CAJA.exists():
        return []
    return json.loads(RUTA_CAJA.read_text(encoding="utf-8")).get("casos") or []


def _fila(c: dict) -> dict:
    reaccion = c.get("reaccion_real") or {}
    titular = c.get("titular") or ""
    simbolos = c.get("simbolos") or ""
    scored = reaccion.get("simbolo") or ""
    tax = clasificar_titular(titular)
    return {
        "sim_id": c.get("sim_id"),
        "origen": c.get("origen"),
        "fecha": c.get("fecha"),
        "titular": titular,
        "simbolos": simbolos,
        "simbolo_hecho": simbolo_del_hecho(titular, simbolos) or scored,
        "simbolo_puntuado": scored,
        "sim_pct": float(c.get("direccion_pct") or 0),
        "real_pct": float(reaccion.get("pct_real") or 0),
        "cerebros": reaccion.get("cerebros") or "",
        "mercado": mercado_de(scored, titular),
        "tipo": tax["tipo"],
        "regimen": tax["regimen"],
        "ruido": es_ruido(titular),
        "sopa": es_sopa(simbolos),
        "apto": apto_calibracion(titular, simbolos, scored),
        "es_v1d": titular.lower() in _V1D,
    }


def limpiar(casos: list[dict] | None = None) -> dict:
    filas = [_fila(c) for c in (casos if casos is not None else _cargar())]
    ia = [f for f in filas if f["cerebros"] == "ia"]
    aptos = [f for f in ia if f["apto"]]
    foco = [f for f in aptos if f["mercado"] in ("indice", "accion")]
    candidatos = [f for f in foco if not f["es_v1d"]]
    candidatos.sort(key=lambda f: f["sim_id"] or "")
    ajuste = candidatos[:40]
    holdout = candidatos[40:120]
    ids_usados = {f["sim_id"] for f in ajuste + holdout}

    def pares(xs):
        return [(x["sim_pct"], x["real_pct"]) for x in xs]

    def tits(xs):
        return [x["titular"] for x in xs]

    nota_ia = evaluar_casos(pares(ia), titulares=tits(ia))
    nota_foco_antes = evaluar_casos(
        pares([f for f in ia if f["mercado"] in ("indice", "accion")]),
        titulares=tits([f for f in ia if f["mercado"] in ("indice", "accion")]),
    )
    nota_foco = evaluar_casos(pares(foco), titulares=tits(foco))
    return {
        "n_total": len(filas),
        "n_ia": len(ia),
        "n_ruido": sum(1 for f in ia if f["ruido"]),
        "n_sopa": sum(1 for f in ia if f["sopa"]),
        "n_aptos": len(aptos),
        "n_foco": len(foco),
        "n_ajuste": len(ajuste),
        "n_holdout": len(holdout),
        "n_pool": sum(1 for f in candidatos if f["sim_id"] not in ids_usados),
        "nota_ia_cruda": {
            "casos": nota_ia["casos"], "tasa": nota_ia["tasa_acierto"],
            "wilson": [nota_ia["wilson_lo"], nota_ia["wilson_hi"]],
            "fuerza": nota_ia["ratio_fuerza_medio"],
            "bruto": nota_ia["ratio_fuerza_bruto"],
        },
        "nota_foco_antes": {
            "casos": nota_foco_antes["casos"], "tasa": nota_foco_antes["tasa_acierto"],
            "wilson": [nota_foco_antes["wilson_lo"], nota_foco_antes["wilson_hi"]],
            "fuerza": nota_foco_antes["ratio_fuerza_medio"],
        },
        "nota_foco_limpia": {
            "casos": nota_foco["casos"], "tasa": nota_foco["tasa_acierto"],
            "wilson": [nota_foco["wilson_lo"], nota_foco["wilson_hi"]],
            "fuerza": nota_foco["ratio_fuerza_medio"],
            "bruto": nota_foco["ratio_fuerza_bruto"],
            "listo_produccion": nota_foco["listo_produccion"],
        },
        "ajuste": ajuste,
        "holdout": holdout,
    }


def guardar(informe: dict | None = None) -> Path:
    inf = informe or limpiar()
    RUTA_BANCO.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "nota": (
            "Banco congelado Fase C. ajuste = para diseñar/chequear hipótesis. "
            "holdout = NO se toca hasta declarar el 70 %. Re-simular con la "
            "hipótesis ganadora; el pct_real ya está. No son la nota de v1d."
        ),
        "n_ajuste": inf["n_ajuste"],
        "n_holdout": inf["n_holdout"],
        "nota_foco_limpia": inf["nota_foco_limpia"],
        "ajuste": inf["ajuste"],
        "holdout": inf["holdout"],
    }
    RUTA_BANCO.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return RUTA_BANCO


def main() -> int:
    inf = limpiar()
    ruta = guardar(inf)
    print(json.dumps({
        "archivo": str(ruta),
        **{k: inf[k] for k in inf if k not in ("ajuste", "holdout")},
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
