"""Instrumentación por segmento (Fase 0 del plan combinado) — dónde se pierde el
acierto. Lee el export de casos (`/api/calibracion/export` o la rama respaldo) y
produce un diagnóstico, SIN tocar el motor ni gastar IA.

Reportes:
  1. mercado × signo_real × |consenso| (bucket) → hit rate del enjambre.
  2. arquetipo → hit rate individual (¿qué voces contribuyen al error?).
  3. arquetipo → correlación(confianza_reportada, acierto) (¿la confianza informa?).
  4. fuente (api/cache vs respaldo léxico) → hit rate y nº de casos.

"Hit" del enjambre = signo(direccion_pct) coincide con signo(pct_real) (el mismo
criterio que usa el backtest). OJO: la categoría de los datos es circular (se
calcula del resultado), así que este reporte es para VER dónde falla, no para
decidir despliegues — eso lo decide el walk-forward sobre la predicción.

Uso:
    python3 engine/calibration/evaluar_por_segmento.py ruta/al/calibracion.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido.backtest import _mercado_de_caso

BASE = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente"]
# incluye doomer_selectivo (9º) para medir la MISMA señal que usa producción, no
# una de 8 que lo ignora (auditoría ampliada). Se suma solo cuando está presente.
VOCES = BASE + ["doomer_selectivo"]
CONTRARIANS = {"quant_esceptico", "contrarian_sabio"}


def _senal_ponderada(sa, peso_contr=0.3) -> float:
    """senal_media_ponderada reconstruida desde senales_arquetipo (contrarians×0.3)."""
    num = den = 0.0
    for a in VOCES:
        if a in sa:
            w = sa[a]["n"] * (peso_contr if a in CONTRARIANS else 1.0)
            num += sa[a]["senal_media"] * w
            den += w
    return num / den if den else 0.0


def cargar(ruta: str) -> list[dict]:
    datos = json.load(open(ruta))
    casos = datos.get("casos", datos) if isinstance(datos, dict) else datos
    out = []
    for c in casos:
        r = c.get("reaccion_real") or {}
        pct = r.get("pct_real")
        if pct is None or pct == 0 or c.get("direccion_pct") is None:
            continue
        out.append(c)
    return out


def _signo(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _consenso(caso) -> float:
    """Reconstruye la magnitud del consenso desde senales_arquetipo (el export no
    trae `confianza`): media ponderada por confianza×n sobre los 8 arquetipos."""
    sa = caso.get("senales_arquetipo") or {}
    num = den = 0.0
    for a in VOCES:
        if a in sa:
            w = sa[a]["confianza_media"] * sa[a]["n"]
            num += sa[a]["senal_media"] * w
            den += w
    return num / den if den else 0.0


def _hit(caso) -> bool:
    return _signo(caso["direccion_pct"]) == _signo(caso["reaccion_real"]["pct_real"])


def _tasa(items, pred):
    sub = [x for x in items if pred(x)]
    if not sub:
        return (None, 0)
    return (round(100 * sum(1 for x in sub if _hit(x)) / len(sub), 1), len(sub))


def por_mercado_signo_consenso(casos):
    """mercado × signo_real × bucket de |consenso| (confianza) → hit rate."""
    out = {}
    cubos = [(0.0, 0.15), (0.15, 0.35), (0.35, 0.6), (0.6, 1.01)]
    for m in ("indice", "accion", "cripto", "oro", "petroleo"):
        dm = _mercado_de_caso
        base = [c for c in casos if dm({"simbolos": c.get("simbolos"), "mercado": c.get("mercado")}) == m]
        if not base:
            continue
        fila = {"n": len(base)}
        for etq, signo in (("real_sube", 1), ("real_baja", -1)):
            sub = [c for c in base if _signo(c["reaccion_real"]["pct_real"]) == signo]
            acc, n = _tasa(sub, lambda x: True)
            fila[etq] = {"hit": acc, "n": n}
            fila[etq]["por_consenso"] = {
                f"{lo:.2f}-{hi:.2f}": _tasa(sub, lambda x, lo=lo, hi=hi: lo <= abs(_consenso(x)) < hi)
                for lo, hi in cubos
            }
        out[m] = fila
    return out


def por_arquetipo(casos):
    """arquetipo → hit direccional de su señal + correlación(confianza, acierto)."""
    out = {}
    for a in BASE:
        pares = [(c["senales_arquetipo"][a], _hit(c), _signo(c["reaccion_real"]["pct_real"]))
                 for c in casos if (c.get("senales_arquetipo") or {}).get(a)]
        if not pares:
            continue
        # hit direccional del arquetipo: signo(su senal_media) vs signo(real)
        aciertos = sum(1 for sa, _h, sr in pares if _signo(sa["senal_media"]) == sr)
        # correlación confianza vs acierto-del-enjambre (proxy simple)
        confs = [sa["confianza_media"] for sa, _h, _sr in pares]
        hits = [1 if _h else 0 for _sa, _h, _sr in pares]
        out[a] = {
            "acierto_direccional": round(100 * aciertos / len(pares), 1),
            "n": len(pares),
            "corr_confianza_hit": _corr(confs, hits),
        }
    return out


def por_fuente(casos):
    """api/cache vs respaldo léxico → hit rate y nº de casos."""
    out = {}
    for etq, pred in (("ia_real", lambda c: (c["reaccion_real"].get("cerebros") or "") != "respaldo"),
                      ("respaldo_lexico", lambda c: (c["reaccion_real"].get("cerebros") or "") == "respaldo")):
        acc, n = _tasa(casos, pred)
        out[etq] = {"hit": acc, "n": n}
    return out


def _corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return round(num / (dx * dy), 3)


def direccion_senal_vs_precio(casos, zona_muerta=0.3):
    """Prioridad 1+2 (plan v2): compara el acierto direccional tomando la dirección
    del PRECIO simulado vs. de la SEÑAL de los líderes (senal_media_ponderada),
    global y por mercado. Con ZONA MUERTA (Prioridad 2): los resultados planos
    (|pct_real| < zona_muerta %) NO cuentan como error — salen del denominador y
    se reporta la COBERTURA (fracción de casos direccionables)."""
    out = {}

    def acc(sub, por_senal):
        dire = [c for c in sub if abs(c["reaccion_real"]["pct_real"]) >= zona_muerta]
        if not dire:
            return (None, 0)
        ok = sum(1 for c in dire
                 if _signo(_senal_ponderada(c.get("senales_arquetipo") or {}) if por_senal else c["direccion_pct"])
                 == _signo(c["reaccion_real"]["pct_real"]))
        return (round(100 * ok / len(dire), 1), len(dire))

    for m in ("TODOS", "indice", "accion", "cripto", "oro", "petroleo"):
        sub = casos if m == "TODOS" else [
            c for c in casos
            if _mercado_de_caso({"simbolos": c.get("simbolos"), "mercado": c.get("mercado")}) == m]
        if not sub:
            continue
        pre, n_dir = acc(sub, False)
        sen, _ = acc(sub, True)
        out[m] = {"n": len(sub), "n_direccionable": n_dir,
                  "cobertura": round(100 * n_dir / len(sub), 1) if sub else None,
                  "precio": pre, "senal": sen,
                  "delta": round(sen - pre, 1) if (sen is not None and pre is not None) else None}
    return out


def reporte(ruta: str) -> dict:
    casos = cargar(ruta)
    return {
        "n": len(casos),
        "hit_global": _tasa(casos, lambda x: True)[0],
        "direccion_senal_vs_precio": direccion_senal_vs_precio(casos),
        "por_mercado": por_mercado_signo_consenso(casos),
        "por_arquetipo": por_arquetipo(casos),
        "por_fuente": por_fuente(casos),
    }


def imprimir(rep: dict) -> None:
    print(f"casos usables: {rep['n']}   hit global: {rep['hit_global']}%\n")
    print("=== PRIORIDAD 1+2 · dirección PRECIO vs SEÑAL (zona muerta 0.3%) ===")
    print(f"{'mercado':10}{'n':>5}{'cobert%':>9}{'precio%':>9}{'senal%':>9}{'Δ':>7}")
    for m, d in rep["direccion_senal_vs_precio"].items():
        print(f"{m:10}{d['n']:>5}{str(d['cobertura']):>9}{str(d['precio']):>9}{str(d['senal']):>9}{str(d['delta']):>7}")
    print()
    print("=== MERCADO × SIGNO REAL × |consenso| → hit% (n) ===")
    for m, f in rep["por_mercado"].items():
        print(f"  {m} (n={f['n']})")
        for etq in ("real_sube", "real_baja"):
            d = f[etq]
            print(f"    {etq}: hit {d['hit']}% (n={d['n']})  por |consenso|: " +
                  "  ".join(f"{k}:{v[0]}%({v[1]})" for k, v in d["por_consenso"].items()))
    print("\n=== ARQUETIPO → acierto direccional · corr(confianza,hit) ===")
    for a, d in rep["por_arquetipo"].items():
        print(f"  {a:22} {d['acierto_direccional']}% (n={d['n']})  corr={d['corr_confianza_hit']}")
    print("\n=== FUENTE → hit% (n) ===")
    for etq, d in rep["por_fuente"].items():
        print(f"  {etq:18} {d['hit']}% (n={d['n']})")


if __name__ == "__main__":
    imprimir(reporte(sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"))
