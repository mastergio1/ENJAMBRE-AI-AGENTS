"""Fase 2 (groundwork) — Acierto direccional de CADA arquetipo, sin fuga.

¿Qué voces de verdad predicen y cuáles son adorno (o estorban)? Para cada
arquetipo mide cuántas veces la DIRECCIÓN de su señal coincidió con el movimiento
POSTERIOR a la noticia (leak-free), sobre los casos históricos guardados. Es la
materia prima de la "confianza histórica por arquetipo" (confianza efectiva de la
Fase 2) y del "qué arquetipos aportan" (Fase 3).

No usa IA nueva: reutiliza `senales_arquetipo` ya guardado y un mapa de resultados
sin fuga (de `contaminacion_temporal`/`remedir_sin_fuga`). Núcleo puro y testeable.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration.remedir_sin_fuga import _sg
from contenido.backtest import _mercado_de_caso

ARQS = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente",
        "doomer_selectivo"]


def mapa_resultados(filas):
    """(simbolo, fecha) -> pct_corr, desde las filas re-medidas sin fuga."""
    return {(f["simbolo"], f["fecha"]): f["pct_corr"] for f in filas
            if f.get("simbolo") and f.get("pct_corr") is not None}


def acierto_por_arquetipo(casos, pcmap, mercado=None, arqs=ARQS, zona=0.3, corte=0.0):
    """Para cada arquetipo: {acierto%, n} de la dirección de su señal vs el
    movimiento sin fuga, sobre casos direccionables (|mov| ≥ zona) donde el
    arquetipo emitió |señal| ≥ corte (y ≠ 0). `mercado` filtra (p.ej. 'indice')."""
    tot = {a: [0, 0] for a in arqs}
    for c in casos:
        rr = c.get("reaccion_real") or {}
        sim = rr.get("simbolo") or (c.get("simbolos") or "").split(",")[0]
        pc = pcmap.get((sim, rr.get("fecha_base")))
        if pc is None or abs(pc) < zona:
            continue
        if mercado and _mercado_de_caso({"simbolos": c.get("simbolos"),
                                         "mercado": c.get("mercado")}) != mercado:
            continue
        sa = c.get("senales_arquetipo") or {}
        for a in arqs:
            s = (sa.get(a) or {}).get("senal_media", 0)
            if a in sa and s != 0 and abs(s) >= corte:
                tot[a][1] += 1
                if _sg(s) == _sg(pc):
                    tot[a][0] += 1
    out = {}
    for a in arqs:
        ok, n = tot[a]
        out[a] = {"acierto": round(100 * ok / n, 1) if n else None, "n": n}
    return out


def imprimir(res_todas, res_fuerte):
    print(f"\n{'arquetipo':22}{'acierto%':>10}{'n':>6}   {'|señal|≥0.3':>12}{'n':>6}")
    for a in ARQS:
        r, rf = res_todas[a], res_fuerte[a]
        print(f"{a:22}{str(r['acierto']):>10}{r['n']:>6}   {str(rf['acierto']):>12}{rf['n']:>6}")


def main(calibracion, sinfuga):
    cal = json.load(open(calibracion))
    casos = [c for c in cal.get("casos", cal) if c.get("origen") == "historico"]
    pcmap = mapa_resultados(json.load(open(sinfuga)))
    print(f"casos históricos: {len(casos)} | resultados sin fuga: {len(pcmap)}")
    print("\n=== APORTE POR ARQUETIPO — ÍNDICE (acierto direccional, sin fuga) ===")
    imprimir(acierto_por_arquetipo(casos, pcmap, "indice", corte=0.0),
             acierto_por_arquetipo(casos, pcmap, "indice", corte=0.3))


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"
    b = sys.argv[2] if len(sys.argv) > 2 else "calibracion.json.con_fecha.json"
    main(a, b)
