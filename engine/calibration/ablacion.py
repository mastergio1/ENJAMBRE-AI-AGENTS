"""Fase 3 — Ablación A0–A5: aislar cuánto aporta CADA capa del enjambre.

La pregunta de fondo del proyecto: el enjambre de 10.150 agentes, ¿agrega poder
PREDICTIVO sobre atajos mucho más simples, o el acierto que vemos ya está en el
consenso de los líderes LLM (y la simulación solo lo adorna)? Esta herramienta lo
mide sobre el dataset SIN FUGA (`pct_corr`), escalón por escalón:

  A0  piso tonto     — clase mayoritaria (el predictor constante óptimo)
  A1  léxico simple  — sentimiento de palabras del titular (sin IA, diccionario)
  A3  consenso LLM   — señal agregada de los ~110 cerebros, SIN ABM  (campo `senal`)
  A4  ABM completo   — lo que simuló el enjambre de 10.150 agentes (`direccion_pct`)

A2 (un solo LLM leyendo el titular) y A5 (ABM + evidencia `as_of`) necesitan correr
IA/motor y se miden aparte; aquí se dejan como escalones declarados, no calculados.

El **gate** del plan: cuantificar A4 − A3. Si A4 ≤ A3, el ABM NO añade predicción
direccional incremental (es gran producto y visualización, no un mejor predictor).

Cada escalón trae su intervalo de confianza HONESTO (bootstrap multiway: el más
ancho entre agrupar por activo, por evento y por período — §Fase 0.5). Sin red:
solo lee números ya calculados (+ el diccionario léxico local para A1).

Uso:
    python3 engine/calibration/ablacion.py cal.json.con_fecha.json [cal.json]
(el 2º argumento, el export crudo, habilita A1 trayendo el titular de cada caso)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import intervalos_multiway as mw
from calibration.remedir_sin_fuga import _sg

ZONA = 0.3  # zona muerta: solo casos con movimiento real |pct_corr| ≥ 0.3%

# Escalones calculables offline. pred_fn(fila) → número cuyo SIGNO es la predicción
# (0 / None = el escalón se abstiene en ese caso).
ESCALONES = [
    ("A0_mayoria", "piso tonto (clase mayoritaria)"),
    ("A1_lexico", "léxico del titular (sin IA)"),
    ("A3_consenso", "consenso LLM, sin ABM (senal)"),
    ("A4_abm", "ABM completo 10.150 agentes (direccion_pct)"),
]


def _signo_mayoria(filas):
    """Dirección mayoritaria entre los resultados reales direccionables (el
    predictor constante óptimo: el piso a batir). No mira features, solo el
    balance subas/bajas, así que es la misma dentro y fuera de muestra."""
    dire = [f for f in filas if f.get("pct_corr") is not None and abs(f["pct_corr"]) >= ZONA]
    subas = sum(1 for f in dire if f["pct_corr"] > 0)
    return 1 if subas >= (len(dire) - subas) else -1


def pred_de(fila, escalon, signo_mayoria):
    if escalon == "A0_mayoria":
        return signo_mayoria
    if escalon == "A1_lexico":
        return fila.get("lexico")
    if escalon == "A3_consenso":
        return fila.get("senal")
    if escalon == "A4_abm":
        return fila.get("direccion_pct")
    return None


def cargar(ruta_con_fecha, ruta_raw=None):
    """Carga las filas sin fuga. Si se da el export crudo, añade `lexico` (A1)
    emparejando por (reaccion_real.fecha_base, reaccion_real.simbolo)."""
    filas = json.loads(Path(ruta_con_fecha).read_text())
    if ruta_raw:
        from brains.fallback import sentimiento_lexico
        crudo = json.loads(Path(ruta_raw).read_text())
        casos = crudo.get("casos", crudo) if isinstance(crudo, dict) else crudo
        titular_por = {}
        for c in casos:
            rr = c.get("reaccion_real") or {}
            k = (rr.get("fecha_base"), rr.get("simbolo"))
            if k[0] and k[1]:
                titular_por.setdefault(k, c.get("titular", ""))
        for f in filas:
            tit = titular_por.get((f.get("fecha"), f.get("simbolo")))
            if tit:
                f["titular"] = tit
                f["lexico"] = sentimiento_lexico(tit)
    return filas


def _items(filas, escalon, signo_mayoria, zona=ZONA):
    """[(acierto, claves)] para los casos direccionables donde el escalón opina."""
    out = []
    for f in filas:
        pc = f.get("pct_corr")
        if pc is None or abs(pc) < zona:
            continue
        pred = pred_de(f, escalon, signo_mayoria)
        if pred in (0, None):
            continue  # el escalón se abstiene
        ok = 1 if _sg(pred) == _sg(pc) else 0
        fecha = str(f.get("fecha", ""))[:10]
        out.append((ok, {"simbolo": f.get("simbolo"), "fecha": fecha,
                         "anio": str(f.get("anio") or fecha[:4])}))
    return out


def _ci_honesto(items, **kw):
    """El IC 95% más ANCHO entre agrupar por activo, evento y período (el honesto)."""
    if not items:
        return {"punto": None, "lo": None, "hi": None, "n": 0}
    por = {c: mw._ci_por_clave(items, c, **kw) for c in ("simbolo", "fecha", "anio")}
    ancho = max(por.values(), key=lambda d: (d["hi"] - d["lo"]))
    clave = next(k for k, v in por.items() if v is ancho)
    return {"punto": ancho["punto"], "lo": ancho["lo"], "hi": ancho["hi"],
            "n": ancho["n"], "agrupado": clave}


def evaluar(filas, mercado=None, zona=ZONA, **kw):
    """Acierto e IC honesto de cada escalón (opcionalmente filtrando por mercado)."""
    sub = [f for f in filas if mercado is None or f.get("mercado") == mercado]
    sm = _signo_mayoria(sub)
    res = {}
    for esc, _desc in ESCALONES:
        items = _items(sub, esc, sm, zona)
        res[esc] = _ci_honesto(items, **kw)
    return res


def gate_abm(filas, mercado=None, zona=ZONA):
    """El gate del plan: A4 − A3. Devuelve la diferencia y cuántas veces el ABM
    cambió el signo del consenso (y con qué resultado neto)."""
    sub = [f for f in filas if mercado is None or f.get("mercado") == mercado]
    sm = _signo_mayoria(sub)
    a3 = _items(sub, "A3_consenso", sm, zona)
    a4 = _items(sub, "A4_abm", sm, zona)
    acc3 = 100 * sum(a for a, _ in a3) / len(a3) if a3 else None
    acc4 = 100 * sum(a for a, _ in a4) / len(a4) if a4 else None
    dire = [f for f in sub if f.get("pct_corr") is not None and abs(f["pct_corr"]) >= zona]
    cambia = [f for f in dire if _sg(f.get("senal")) != _sg(f.get("direccion_pct"))]
    # de los que el ABM invirtió, ¿cuántos acertó el ABM vs los habría acertado A3?
    gana_abm = sum(1 for f in cambia
                   if _sg(f["direccion_pct"]) == _sg(f["pct_corr"]) and f["direccion_pct"])
    return {
        "A3": round(acc3, 1) if acc3 is not None else None,
        "A4": round(acc4, 1) if acc4 is not None else None,
        "delta_A4_menos_A3": (round(acc4 - acc3, 1)
                              if acc3 is not None and acc4 is not None else None),
        "n": len(a4), "abm_cambia_signo": len(cambia),
        "abm_acierta_al_cambiar": gana_abm,
        "abm_falla_al_cambiar": len(cambia) - gana_abm,
    }


def imprimir(filas, mercados=("indice", None)):
    for m in mercados:
        etq = (m or "TODOS").upper()
        res = evaluar(filas, mercado=m)
        print(f"\n=== Ablación A0–A5 · {etq} — acierto direccional (sin fuga) ===")
        print(f"{'escalón':14}{'descripción':42}{'acierto%':>9}{'IC 95% honesto':>18}{'n':>6}")
        for esc, desc in ESCALONES:
            d = res[esc]
            if d["punto"] is None:
                print(f"{esc:14}{desc:42}{'(sin datos)':>9}")
                continue
            ic = f"[{d['lo']}-{d['hi']}]({d['agrupado'][:3]})"
            print(f"{esc:14}{desc:42}{d['punto']:>9}{ic:>18}{d['n']:>6}")
        g = gate_abm(filas, mercado=m)
        print(f"  GATE A4−A3 = {g['delta_A4_menos_A3']} pts  "
              f"(ABM cambió el signo {g['abm_cambia_signo']} veces: "
              f"acertó {g['abm_acierta_al_cambiar']}, falló {g['abm_falla_al_cambiar']})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    raw = sys.argv[2] if len(sys.argv) > 2 else None
    imprimir(cargar(sys.argv[1], raw))
