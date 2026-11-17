"""Re-mide el acierto con ventana SIN FUGA (Prioridad 2b del plan combinado v2).

El examen del cosechador elige días que YA se movieron fuerte y mide `pct_real`
desde el cierre ANTERIOR al titular — así la ventana incluye el mismo movimiento
que hizo seleccionar el día, y el titular ya lo describe (fuga). Esta herramienta
re-mide el resultado desde el cierre DEL DÍA del titular hacia adelante (el
movimiento POSTERIOR a la noticia), con Yahoo (gratis, sin IA), y compara el
acierto tomando la dirección del PRECIO simulado vs. de la SEÑAL de líderes.

Hallazgo (2026-11-16, 616 casos): sin fuga el acierto cae a ~50% en el agregado;
solo ÍNDICE conserva señal real (~63% la señal vs 50% de azar). Ver
docs/baseline-calibracion-fase0.md.

Uso:
    python3 engine/calibration/remedir_sin_fuga.py ruta/al/calibracion.json
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido.backtest import _mercado_de_caso

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
BASE = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente"]
# incluye doomer_selectivo (9º) para medir la MISMA señal que usa producción.
VOCES = BASE + ["doomer_selectivo"]
CONTRARIANS = {"quant_esceptico", "contrarian_sabio"}


def _pond(sa, w=0.3):
    num = sum(sa[a]["senal_media"] * sa[a]["n"] * (w if a in CONTRARIANS else 1) for a in VOCES if a in sa)
    den = sum(sa[a]["n"] * (w if a in CONTRARIANS else 1) for a in VOCES if a in sa)
    return num / den if den else 0.0


def _sg(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def obtener_barras(simbolo, fecha):
    """(fecha_iso, cierre) diarias alrededor de `fecha`. Aislable en tests."""
    try:
        b = datetime.fromisoformat(fecha)
        p1 = int(b.timestamp()) - 12 * 86400
        p2 = int(b.timestamp()) + 20 * 86400
        r = httpx.get(URL.format(simbolo=simbolo),
                      params={"period1": p1, "period2": p2, "interval": "1d"},
                      headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        r.raise_for_status()
        res = r.json()["chart"]["result"][0]
        out = []
        for ts, cl in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]):
            if cl is not None:
                dia = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")
                out.append((dia, float(cl)))
        return out
    except Exception:
        return None


def pct_sin_fuga(barras, fecha_base, ruedas):
    """Movimiento DESPUÉS del día del titular: base = cierre del día del titular
    (la rueda siguiente a fecha_base, que es el cierre anterior), final = `ruedas`
    ruedas después. None si no hay barras suficientes."""
    if not barras:
        return None
    idx = next((k for k, (dia, _) in enumerate(barras) if dia == fecha_base), None)
    if idx is None or idx + 1 + ruedas >= len(barras):
        return None
    base = barras[idx + 1][1]
    final = barras[idx + 1 + ruedas][1]
    if not base:
        return None
    return (final - base) / base * 100


def recolectar(ruta, fetch=obtener_barras, pausa=0.05):
    datos = json.load(open(ruta))
    casos = [c for c in datos.get("casos", datos) if c.get("origen") == "historico"]
    filas = []
    for c in casos:
        rr = c["reaccion_real"]
        sim = rr.get("simbolo") or (c.get("simbolos") or "").split(",")[0]
        fb, rue = rr.get("fecha_base"), rr.get("ruedas", 2)
        if not sim or not fb:
            continue
        pc = pct_sin_fuga(fetch(sim, fb), fb, rue)
        if pc is None:
            continue
        m = _mercado_de_caso({"simbolos": c.get("simbolos"), "mercado": c.get("mercado")})
        filas.append({"mercado": m, "direccion_pct": c.get("direccion_pct"),
                      "senal": _pond(c.get("senales_arquetipo") or {}),
                      "pct_orig": rr.get("pct_real"), "pct_corr": pc})
        if pausa:
            time.sleep(pausa)
    return filas


def _acc(filas, por_senal, usar_corr, zona=0.3):
    campo = "pct_corr" if usar_corr else "pct_orig"
    dire = [f for f in filas if f[campo] is not None and abs(f[campo]) >= zona]
    if not dire:
        return (None, 0)
    ok = sum(1 for f in dire
             if _sg(f["senal"] if por_senal else f["direccion_pct"]) == _sg(f[campo]))
    return (round(100 * ok / len(dire), 1), len(dire))


def resumen(filas):
    out = {}
    for m in ("TODOS", "indice", "accion", "cripto", "oro", "petroleo"):
        sub = filas if m == "TODOS" else [f for f in filas if f["mercado"] == m]
        if not sub:
            continue
        out[m] = {
            "n": len(sub),
            "con_fuga": {"precio": _acc(sub, False, False)[0], "senal": _acc(sub, True, False)[0]},
            "sin_fuga": {"precio": _acc(sub, False, True)[0], "senal": _acc(sub, True, True)[0]},
        }
    return out


def gating_por_senal(filas, cortes=(0.0, 0.1, 0.2, 0.3, 0.5), zona=0.3):
    """¿Acierta más la SEÑAL cuando es más fuerte? (gating/confianza). Para cada
    corte |señal| ≥ c mide, SIN fuga, el acierto de la señal y la COBERTURA
    (fracción de casos direccionables que superan el corte). Si el acierto sube
    con el corte, |señal| informa confianza; si es plano, es adorno."""
    dire = [f for f in filas if f["pct_corr"] is not None and abs(f["pct_corr"]) >= zona]
    base = len(dire)
    out = []
    for c in cortes:
        sub = [f for f in dire if abs(f["senal"]) >= c]
        if not sub:
            out.append({"corte": c, "acierto": None, "n": 0, "cobertura": 0.0})
            continue
        ok = sum(1 for f in sub if _sg(f["senal"]) == _sg(f["pct_corr"]))
        out.append({"corte": c, "acierto": round(100 * ok / len(sub), 1),
                    "n": len(sub), "cobertura": round(100 * len(sub) / base, 1) if base else 0.0})
    return out


def imprimir(res):
    print(f"{'mercado':10}{'n':>5} | CON fuga precio/señal | SIN fuga precio/señal")
    for m, d in res.items():
        cf, sf = d["con_fuga"], d["sin_fuga"]
        print(f"{m:10}{d['n']:>5} |   {cf['precio']} / {cf['senal']}   |   {sf['precio']} / {sf['senal']}")


def imprimir_gating(g):
    print(f"\n{'|señal|≥':10}{'acierto%':>10}{'n':>7}{'cobertura%':>12}")
    for r in g:
        print(f"{r['corte']:<10}{str(r['acierto']):>10}{r['n']:>7}{str(r['cobertura']):>12}")


if __name__ == "__main__":
    import json as _json
    ruta = sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"
    print("re-midiendo históricos con Yahoo (sin fuga)…", flush=True)
    filas = recolectar(ruta)
    try:  # cachear las filas re-medidas para no re-consultar Yahoo
        _json.dump(filas, open(ruta + ".sinfuga.json", "w"))
    except Exception:
        pass
    imprimir(resumen(filas))
    print("\n=== GATING: ¿acierta más la señal cuando es más fuerte? (TODOS, sin fuga) ===")
    imprimir_gating(gating_por_senal(filas))
    print("\n=== GATING solo ÍNDICE (donde hay señal real) ===")
    imprimir_gating(gating_por_senal([f for f in filas if f["mercado"] == "indice"]))
