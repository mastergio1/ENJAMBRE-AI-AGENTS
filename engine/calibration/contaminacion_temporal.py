"""Fase 0 — Contaminación temporal por memoria del LLM.

Pregunta honesta: ¿cuánto del acierto de la señal en ÍNDICE es señal real y
cuánto es que el modelo RECUERDA el desenlace de noticias viejas (en su corte de
conocimiento)? Las noticias RECIENTES el modelo casi no pudo memorizarlas; las
VIEJAS sí. Si el acierto NO decae en las recientes, la señal es real. Si las
viejas aciertan mucho más, parte era memoria.

No usa IA nueva: reutiliza las señales ya guardadas (`senales_arquetipo`) y
re-mide el resultado SIN FUGA con Yahoo (`remedir_sin_fuga`). La recolección vive
en `recolectar_con_fecha`; el análisis (particionar por era, acierto por bloque)
es puro y testeable sin red.

Uso:
    python3 engine/calibration/contaminacion_temporal.py ruta/al/calibracion.json
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration.remedir_sin_fuga import obtener_barras, pct_sin_fuga, _pond, _sg
from contenido.backtest import _mercado_de_caso


def recolectar_con_fecha(ruta, fetch=obtener_barras, pausa=0.02, cache=None):
    """Filas históricas re-medidas SIN FUGA, conservando la fecha del titular.

    Cada fila: {fecha, anio, mercado, direccion_pct, senal, pct_corr}. `fetch` es
    aislable en tests; `cache` (ruta) evita re-consultar Yahoo si ya existe."""
    if cache and Path(cache).exists():
        return json.load(open(cache))
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
        filas.append({"fecha": fb, "anio": int(fb[:4]), "mercado": m,
                      "direccion_pct": c.get("direccion_pct"),
                      "senal": _pond(c.get("senales_arquetipo") or {}),
                      "pct_corr": pc})
        if pausa:
            time.sleep(pausa)
    if cache:
        try:
            json.dump(filas, open(cache, "w"))
        except OSError:
            pass
    return filas


def acc_senal(filas, zona=0.3, corte_senal=0.0):
    """(acierto%, n) de la DIRECCIÓN de la señal sin fuga, sobre casos
    direccionables (|movimiento| ≥ zona) con |señal| ≥ corte_senal."""
    dire = [f for f in filas if f.get("pct_corr") is not None
            and abs(f["pct_corr"]) >= zona and abs(f["senal"]) >= corte_senal]
    if not dire:
        return (None, 0)
    ok = sum(1 for f in dire if _sg(f["senal"]) == _sg(f["pct_corr"]))
    return (round(100 * ok / len(dire), 1), len(dire))


def particionar_por_era(filas, viejas_hasta=2023, recientes_desde=2025):
    """Separa en viejas (año ≤ viejas_hasta), medio y recientes (≥ recientes_desde)."""
    return {
        "viejas": [f for f in filas if f["anio"] <= viejas_hasta],
        "medio": [f for f in filas if viejas_hasta < f["anio"] < recientes_desde],
        "recientes": [f for f in filas if f["anio"] >= recientes_desde],
    }


def resumen_contaminacion(filas, mercado=None, corte_senal=0.3):
    """Acierto de la señal por era (viejas/medio/recientes). Si las viejas
    aciertan MUCHO más que las recientes, hay señal de contaminación por memoria."""
    sub = filas if mercado is None else [f for f in filas if f["mercado"] == mercado]
    eras = particionar_por_era(sub)
    out = {"mercado": mercado or "TODOS", "n": len(sub)}
    for era, fs in eras.items():
        a_all, n_all = acc_senal(fs)
        a_str, n_str = acc_senal(fs, corte_senal=corte_senal)
        out[era] = {"n": len(fs), "acierto_senal": a_all, "n_dir": n_all,
                    "acierto_fuerte": a_str, "n_fuerte": n_str}
    return out


def imprimir(res):
    print(f"\n=== {res['mercado']} (n={res['n']}) — acierto de la SEÑAL por era ===")
    print(f"{'era':12}{'n':>6}{'señal %':>10}{'n_dir':>7}{'|señal|≥0.3 %':>16}{'n':>6}")
    for era in ("viejas", "medio", "recientes"):
        d = res[era]
        print(f"{era:12}{d['n']:>6}{str(d['acierto_senal']):>10}{d['n_dir']:>7}"
              f"{str(d['acierto_fuerte']):>16}{d['n_fuerte']:>6}")


def main(ruta):
    cache = ruta + ".con_fecha.json"
    filas = recolectar_con_fecha(ruta, cache=cache)
    print(f"filas históricas re-medidas sin fuga (con fecha): {len(filas)}")
    imprimir(resumen_contaminacion(filas))              # todos los mercados
    imprimir(resumen_contaminacion(filas, "indice"))    # donde vive la señal


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "calibracion.json")
