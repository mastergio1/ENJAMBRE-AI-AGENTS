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
import random
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
    ("A2_un_llm", "un solo LLM neutral (sin arquetipos ni ABM)"),
    ("A3_consenso", "consenso LLM, sin ABM (senal)"),
    ("A4_abm", "ABM completo 10.150 agentes (direccion_pct)"),
]


def _signo_mayoria(filas):
    """Dirección mayoritaria entre TODOS los resultados dados (atajo que SÍ mira
    las etiquetas del conjunto). Se conserva como utilidad, pero para puntuar A0
    NO se usa (miraría el examen): ver `_items_a0`, que solo usa el pasado."""
    dire = [f for f in filas if f.get("pct_corr") is not None and abs(f["pct_corr"]) >= ZONA]
    subas = sum(1 for f in dire if f["pct_corr"] > 0)
    return 1 if subas >= (len(dire) - subas) else -1


def _items_a0(filas, zona=ZONA):
    """A0 HONESTO con MADURACIÓN DE ETIQUETAS (auditoría científica F02).

    Para cada caso, la clase mayoritaria de los eventos ESTRICTAMENTE ANTERIORES por
    fecha. Clave: los casos del MISMO día (p. ej. 3 ETFs del mismo anuncio) NO se
    informan entre sí — su etiqueta no está disponible hasta días después, así que se
    predicen TODOS con la historia previa al día y la historia se actualiza recién al
    cerrar el día. Antes (v4) la historia se actualizaba caso a caso y los ETFs del
    mismo día se contaban como ya resueltos: fuga sutil. Se abstiene mientras no haya
    historia madura (empate 0-0); esas abstenciones reducen el denominador a propósito."""
    dire = [f for f in filas if f.get("pct_corr") is not None and abs(f["pct_corr"]) >= zona]
    dire = sorted(dire, key=lambda f: str(f.get("fecha", ""))[:10])
    out = []
    subas = bajas = 0
    i, n = 0, len(dire)
    while i < n:
        dia = str(dire[i].get("fecha", ""))[:10]
        j = i
        # 1) PREDECIR todos los casos del día con la historia previa (madura)
        pred = 1 if subas > bajas else (-1 if bajas > subas else 0)
        while j < n and str(dire[j].get("fecha", ""))[:10] == dia:
            f = dire[j]
            if pred != 0:
                ok = 1 if _sg(pred) == _sg(f["pct_corr"]) else 0
                out.append((ok, {"simbolo": f.get("simbolo"), "fecha": dia,
                                 "anio": str(f.get("anio") or dia[:4])}))
            j += 1
        # 2) CERRAR el día: recién ahora sus etiquetas entran en la historia
        for k in range(i, j):
            if dire[k]["pct_corr"] > 0:
                subas += 1
            else:
                bajas += 1
        i = j
    return out


def pred_de(fila, escalon, signo_mayoria):
    if escalon == "A0_mayoria":
        return signo_mayoria
    if escalon == "A1_lexico":
        return fila.get("lexico")
    if escalon == "A2_un_llm":
        return fila.get("a2")
    if escalon == "A3_consenso":
        return fila.get("senal")
    if escalon == "A4_abm":
        return fila.get("direccion_pct")
    return None


def cargar(ruta_con_fecha, ruta_raw=None, ruta_a2=None):
    """Carga las filas sin fuga. Si se da el export crudo, añade `titular` y
    `lexico` (A1) emparejando por (reaccion_real.fecha_base, ….simbolo). Si se da
    `ruta_a2` (un {titular: senal} que produce `un_llm.py`), añade `a2` (A2)."""
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
    if ruta_a2:
        a2 = json.loads(Path(ruta_a2).read_text())
        if isinstance(a2, dict) and "senales" in a2:  # caché versionado de un_llm.py
            a2 = a2["senales"]
        for f in filas:
            if f.get("titular") in a2:
                f["a2"] = a2[f["titular"]]
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
    res = {}
    for esc, _desc in ESCALONES:
        # A0 se puntúa SOLO con el pasado (train-only); el resto son reglas fijas
        # (su acierto es el mismo dentro y fuera de muestra), así que no filtran.
        items = _items_a0(sub, zona) if esc == "A0_mayoria" else _items(sub, esc, None, zona)
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


def pareado(filas, esc_a, esc_b, mercado=None, zona=ZONA, n_boot=3000, seed=42):
    """Diferencia PAREADA acierto(esc_a) − acierto(esc_b) por EVENTO (cluster bootstrap).

    La unidad de dependencia no es el caso suelto sino el ANUNCIO (misma fecha): 4
    ETFs del mismo día no son 4 experimentos. Solo cuenta los casos donde AMBOS
    escalones opinan (misma cobertura: nada de comparar a coberturas distintas).
    d = acierto_a − acierto_b ∈ {-1,0,1}; se agrupan por fecha y se re-muestrean los
    GRUPOS para el IC de la media de d. IC que EXCLUYE 0 ⇒ diferencia significativa."""
    sub = [f for f in filas if mercado is None or f.get("mercado") == mercado]
    por_evento = {}
    for f in sub:
        pc = f.get("pct_corr")
        if pc is None or abs(pc) < zona:
            continue
        pa, pb = pred_de(f, esc_a, None), pred_de(f, esc_b, None)
        if pa in (0, None) or pb in (0, None):
            continue
        a = 1 if _sg(pa) == _sg(pc) else 0
        b = 1 if _sg(pb) == _sg(pc) else 0
        por_evento.setdefault(str(f.get("fecha", ""))[:10], []).append(a - b)
    grupos = list(por_evento.values())
    todos = [d for g in grupos for d in g]
    if not todos:
        return {"media": None, "lo": None, "hi": None, "n": 0, "n_eventos": 0}
    media = sum(todos) / len(todos)
    rng = random.Random(seed)
    muestras = []
    for _ in range(n_boot):
        pool = []
        for _ in range(len(grupos)):
            pool.extend(rng.choice(grupos))
        if pool:
            muestras.append(sum(pool) / len(pool))
    muestras.sort()
    lo = muestras[int(0.025 * len(muestras))]
    hi = muestras[int(0.975 * len(muestras)) - 1]
    return {"media": round(media, 3), "lo": round(lo, 3), "hi": round(hi, 3),
            "n": len(todos), "n_eventos": len(grupos),
            "excluye_cero": hi < 0 or lo > 0}


def gate_pareado(filas, mercado=None, zona=ZONA, n_boot=3000, seed=42):
    """El gate CORRECTO (auditoría v4): diferencia PAREADA A4 − A3 por EVENTO.
    media<0 ⇒ el ABM resta. Sustituye al atajo 'el intervalo más ancho de tres' para
    la comparación A3-vs-A4. (Caso particular de `pareado`.)"""
    return pareado(filas, "A4_abm", "A3_consenso", mercado=mercado, zona=zona,
                   n_boot=n_boot, seed=seed)


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
        print(f"  GATE A4−A3 (puntual) = {g['delta_A4_menos_A3']} pts  "
              f"(ABM cambió el signo {g['abm_cambia_signo']} veces: "
              f"acertó {g['abm_acierta_al_cambiar']}, falló {g['abm_falla_al_cambiar']})")
        p = gate_pareado(filas, mercado=m)
        if p["media"] is not None:
            print(f"  GATE pareado por evento: media(A4−A3) = {p['media']} "
                  f"IC95 [{p['lo']}, {p['hi']}] · {p['n']} casos en {p['n_eventos']} eventos"
                  f" · {'significativo' if p['excluye_cero'] else 'no concluyente (IC cruza 0)'}")
        if any(f.get("a2") is not None for f in filas):
            q = pareado(filas, "A2_un_llm", "A3_consenso", mercado=m)
            if q["media"] is not None:
                print(f"  M4 pareado por evento: media(A2−A3) = {q['media']} "
                      f"IC95 [{q['lo']}, {q['hi']}] · {q['n']} casos en {q['n_eventos']} eventos"
                      f" · {'significativo' if q['excluye_cero'] else 'no distinguible (IC cruza 0)'}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    a2 = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--a2=")), None)
    if a2 is None and "--a2" in sys.argv:  # forma "--a2 ruta"
        i = sys.argv.index("--a2")
        a2 = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
        args = [a for a in args if a != a2]
    if not args:
        print(__doc__)
        sys.exit(1)
    raw = args[1] if len(args) > 1 else None
    imprimir(cargar(args[0], raw, a2))
