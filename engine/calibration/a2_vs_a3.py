"""M4 vs A3 — comparación TITULAR POR TITULAR entre un LLM neutral (A2) y el consenso
de ~110 cerebros (A3).

La tabla de `ablacion.py` da un acierto global por escalón, cada uno sobre SU propia
cobertura. Aquí se mira el mismo examen para los dos, caso a caso:

  1. Cobertura COMÚN: solo casos direccionables (|pct_corr| ≥ ZONA) donde AMBOS opinan.
     Se informa cuántos casos pierde cada uno (no comparar a coberturas distintas).
  2. Acierto de A2 y A3 sobre esa misma cobertura, con su IC honesto (multiway).
  3. Diferencia PAREADA A2−A3 por evento (cluster bootstrap: la unidad es el anuncio).
  4. Discordancias: en cuántos casos acierta solo A2 vs solo A3 (McNemar exacto, solo
     indicativo porque asume independencia; manda el bootstrap por evento).
  5. Acuerdo de signo y correlación entre las dos señales.
  6. Tabla por titular (markdown) con las dos señales, lo que pasó y quién acertó.

Es EXPLORATORIO (banco histórico sesgado por selección, n chico): no da veredicto
definitivo. Si el IC pareado cruza 0, el veredicto honesto es "no distinguible".

Uso:
    python3 engine/calibration/a2_vs_a3.py cal.con_fecha.json cal.json a2_senales.json [tabla.md]
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import ablacion
from calibration.remedir_sin_fuga import _sg

ZONA = ablacion.ZONA


def _opina(x):
    return x not in (0, None)


def cobertura(filas, mercado=None, zona=ZONA):
    """Cuántos casos direccionables hay y en cuántos opina cada escalón / ambos."""
    sub = [f for f in filas if mercado is None or f.get("mercado") == mercado]
    dire = [f for f in sub if f.get("pct_corr") is not None and abs(f["pct_corr"]) >= zona]
    return {
        "direccionables": len(dire),
        "con_a2": sum(1 for f in dire if _opina(f.get("a2"))),
        "con_a3": sum(1 for f in dire if _opina(f.get("senal"))),
        "ambos": sum(1 for f in dire if _opina(f.get("a2")) and _opina(f.get("senal"))),
    }


def pares(filas, mercado=None, zona=ZONA):
    """Filas de la cobertura común, con el acierto de cada uno ya calculado."""
    out = []
    for f in filas:
        if mercado is not None and f.get("mercado") != mercado:
            continue
        pc = f.get("pct_corr")
        if pc is None or abs(pc) < zona:
            continue
        a2, a3 = f.get("a2"), f.get("senal")
        if not (_opina(a2) and _opina(a3)):
            continue
        out.append({**f, "ok_a2": int(_sg(a2) == _sg(pc)), "ok_a3": int(_sg(a3) == _sg(pc))})
    return out


def mcnemar_exacto(b, c):
    """p bilateral exacto de McNemar (binomial con p=0.5 sobre las discordancias)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    cola = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * cola)


def _pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return round(sxy / (sx * sy), 3) if sx and sy else None


def comparar(filas, mercado=None, zona=ZONA, **kw):
    """Todo lo de M4 vs A3 sobre la cobertura común de un mercado (o de todos)."""
    ps = pares(filas, mercado, zona)
    items = lambda clave: [(p[clave], {"simbolo": p.get("simbolo"),
                                       "fecha": str(p.get("fecha", ""))[:10],
                                       "anio": str(p.get("anio") or str(p.get("fecha", ""))[:4])})
                           for p in ps]
    solo_a2 = sum(1 for p in ps if p["ok_a2"] and not p["ok_a3"])
    solo_a3 = sum(1 for p in ps if p["ok_a3"] and not p["ok_a2"])
    return {
        "cobertura": cobertura(filas, mercado, zona),
        "A2": ablacion._ci_honesto(items("ok_a2"), **kw),
        "A3": ablacion._ci_honesto(items("ok_a3"), **kw),
        "pareado": ablacion.pareado(filas, "A2_un_llm", "A3_consenso",
                                    mercado=mercado, zona=zona),
        "ambos_aciertan": sum(1 for p in ps if p["ok_a2"] and p["ok_a3"]),
        "ambos_fallan": sum(1 for p in ps if not p["ok_a2"] and not p["ok_a3"]),
        "solo_a2": solo_a2, "solo_a3": solo_a3,
        "mcnemar_p": round(mcnemar_exacto(solo_a2, solo_a3), 4),
        "acuerdo_signo": (round(100 * sum(1 for p in ps if _sg(p["a2"]) == _sg(p["senal"]))
                                / len(ps), 1) if ps else None),
        "correlacion": _pearson([p["a2"] for p in ps], [p["senal"] for p in ps]),
    }


def veredicto(res):
    """Lectura honesta en una línea (reglas del plan v5)."""
    p = res["pareado"]
    if p["media"] is None:
        return "sin datos comunes"
    if not p["excluye_cero"]:
        return "no distinguible con estos datos (el IC pareado cruza 0)"
    return ("A2 > A3: el consenso pierde señal al promediar — investigar"
            if p["media"] > 0 else "A3 > A2: la diversidad de cerebros aporta")


def _estado(p):
    if p["ok_a2"] and p["ok_a3"]:
        return "ambos ✓"
    if p["ok_a2"]:
        return "solo A2 ✓"
    if p["ok_a3"]:
        return "solo A3 ✓"
    return "ambos ✗"


def tabla_titulares(filas, zona=ZONA):
    """Markdown: una fila por (titular, activo) de la cobertura común, ordenada por
    mercado y fecha. Las discordancias primero dentro de cada mercado."""
    ps = pares(filas, None, zona)
    orden = {"solo A2 ✓": 0, "solo A3 ✓": 1, "ambos ✗": 2, "ambos ✓": 3}
    ps.sort(key=lambda p: (str(p.get("mercado")), orden[_estado(p)], str(p.get("fecha"))))
    lineas = ["| mercado | fecha | activo | titular | A3 (consenso) | A2 (1 LLM) | real % | quién acierta |",
              "|---|---|---|---|---:|---:|---:|---|"]
    for p in ps:
        tit = (p.get("titular") or "").replace("|", "/")
        if len(tit) > 110:
            tit = tit[:107] + "…"
        lineas.append(
            f"| {p.get('mercado')} | {str(p.get('fecha'))[:10]} | {p.get('simbolo')} | {tit} "
            f"| {p['senal']:+.2f} | {p['a2']:+.2f} | {p['pct_corr']:+.2f} | {_estado(p)} |")
    return "\n".join(lineas)


def imprimir(filas, mercados=("indice", None, "accion", "cripto", "oro", "petroleo")):
    for m in mercados:
        r = comparar(filas, mercado=m)
        c = r["cobertura"]
        if not c["ambos"]:
            continue
        print(f"\n=== M4 (A2, 1 LLM) vs A3 (consenso) · {(m or 'TODOS').upper()} ===")
        print(f"  cobertura: {c['direccionables']} direccionables · A2 opina {c['con_a2']} · "
              f"A3 opina {c['con_a3']} · ambos {c['ambos']}")
        for k in ("A2", "A3"):
            d = r[k]
            print(f"  {k}: {d['punto']}%  IC95 honesto [{d['lo']}-{d['hi']}] "
                  f"({d['agrupado']}) · n={d['n']}")
        p = r["pareado"]
        print(f"  pareado A2−A3 por evento: {p['media']}  IC95 [{p['lo']}, {p['hi']}] · "
              f"{p['n']} casos en {p['n_eventos']} eventos")
        print(f"  discordancias: solo A2 acierta {r['solo_a2']} · solo A3 acierta {r['solo_a3']} "
              f"(McNemar p={r['mcnemar_p']}, indicativo) · ambos ✓ {r['ambos_aciertan']} · "
              f"ambos ✗ {r['ambos_fallan']}")
        print(f"  acuerdo de signo {r['acuerdo_signo']}% · correlación de señales {r['correlacion']}")
        print(f"  → {veredicto(r)}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    filas = ablacion.cargar(sys.argv[1], sys.argv[2], sys.argv[3])
    imprimir(filas)
    if len(sys.argv) > 4:
        Path(sys.argv[4]).write_text(tabla_titulares(filas) + "\n")
        print(f"\nTabla titular por titular → {sys.argv[4]}")
