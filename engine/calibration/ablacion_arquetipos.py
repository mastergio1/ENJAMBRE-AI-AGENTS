"""Ablación por arquetipo: ¿quién descalibra / desorienta el consenso?

Lee un export de casos (el que produce `GET /api/calibracion/export` o la rama
respaldo-datos: una lista de casos, cada uno con `senales_arquetipo`) y mide,
con partición TEMPORAL (2/3 entrena, 1/3 prueba por fecha):

  1. Arquetipo suelto: su señal media como predictor (acierto direccional y
     Brier calibrado con Platt).
  2. Consenso = promedio simple de los 8 arquetipos base.
  3. Leave-one-out: consenso SIN cada arquetipo. Δbrier<0 al quitarlo ⇒ ese
     arquetipo estaba DESORIENTANDO al consenso.
  4. Variantes del consenso (sin contrarians / solo los direccionales).
  5. Desglose por clase de titular (negativa/positiva/neutra).

NO toca el motor ni gasta IA: solo lee números ya calculados. Es un DIAGNÓSTICO
del contenido direccional de cada voz (promedio simple), no un cambio de config:
el motor pondera por seguidores y confianza y el consenso mueve el enjambre, no
solo una probabilidad. Sirve para decidir dónde intervenir, con medición.

Uso:
    python3 engine/calibration/ablacion_arquetipos.py ruta/al/calibracion.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido import calibracion as cal

BASE = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente"]
# arquetipos OPCIONALES (no están en todos los casos: se activaron después). Se
# evalúan sueltos sobre el subconjunto donde aparecen (auditoría: medir la utilidad
# del doomer_selectivo, no asumirla).
OPCIONALES = ["doomer_selectivo"]
# Los que, por el diagnóstico, aportan dirección vs. los que la restan.
DIRECCIONALES = ["institucional_frio", "fomo_evangelista", "doomer", "influencer_optimista"]
CONTRARIANS = ["quant_esceptico", "contrarian_sabio"]


def cargar(ruta: str) -> list[dict]:
    """Casos usables: con pct_real != 0 y los 8 arquetipos base presentes,
    ordenados por fecha (para la partición temporal)."""
    datos = json.load(open(ruta))
    casos = datos.get("casos", datos) if isinstance(datos, dict) else datos
    out = []
    for c in casos:
        r = c["reaccion_real"]
        pct = r.get("pct_real")
        if pct is None or pct == 0:
            continue
        sa = c.get("senales_arquetipo") or {}
        if not all(a in sa for a in BASE):
            continue
        caso = {
            "fecha": c.get("fecha") or "",
            "y": 1 if pct > 0 else 0,
            "cat": r.get("categoria", "?"),
            "senal": {a: sa[a]["senal_media"] for a in BASE},
        }
        # arquetipos opcionales: se guardan solo si el caso los trae
        for a in OPCIONALES:
            if a in sa:
                caso["senal"][a] = sa[a]["senal_media"]
        out.append(caso)
    out.sort(key=lambda x: x["fecha"])
    return out


def prob(s: float) -> float:
    return cal.senal_a_prob_cruda({"senal_media_lideres": s})


def acierto_direccional(senales, ys):
    """% de casos donde el signo de la señal coincide con el real (0 = medio punto)."""
    if not senales:
        return None
    ok = 0.0
    for s, y in zip(senales, ys):
        if s == 0:
            ok += 0.5
        elif (s > 0) == (y == 1):
            ok += 1
    return round(100 * ok / len(senales), 1)


def brier_calibrado(scores, ys, frac=2 / 3):
    """Platt con partición temporal. Devuelve (brier_cal, brier_base, n_prueba)."""
    corte = int(len(scores) * frac)
    s_tr, y_tr = scores[:corte], ys[:corte]
    s_te, y_te = scores[corte:], ys[corte:]
    if len(s_tr) < 30 or len(s_te) < 15:
        return None, None, len(s_te)
    try:
        c = cal.ajustar_calibrador(s_tr, y_tr, metodo="platt")
        bc = round(cal.brier(c.predict(s_te), y_te), 4)
    except Exception:
        bc = None
    base = cal.tasa_base(y_tr)
    bb = round(cal.brier([base] * len(y_te), y_te), 4)
    return bc, bb, len(s_te)


def consenso(caso, excluir=()):
    # el consenso/leave-one-out viven SOBRE LOS 8 BASE (presentes en todos los
    # casos), para que sea comparable entre casos; los opcionales se evalúan aparte.
    ss = [caso["senal"][a] for a in BASE if a not in excluir and a in caso["senal"]]
    return sum(ss) / len(ss) if ss else 0.0


def analizar(ruta: str) -> dict:
    casos = cargar(ruta)
    ys = [c["y"] for c in casos]
    rep = {"n": len(casos), "tasa_base": round(sum(ys) / len(ys), 3)}

    rep["arquetipo_suelto"] = {}
    for a in BASE:
        bc, bb, nte = brier_calibrado([prob(c["senal"][a]) for c in casos], ys)
        rep["arquetipo_suelto"][a] = {
            "acierto": acierto_direccional([c["senal"][a] for c in casos], ys),
            "brier_cal": bc, "brier_base": bb, "n_test": nte}

    # arquetipos opcionales (p.ej. doomer_selectivo): sobre su subconjunto presente
    rep["arquetipo_opcional"] = {}
    for a in OPCIONALES:
        sub = [c for c in casos if a in c["senal"]]
        if len(sub) < 30:
            rep["arquetipo_opcional"][a] = {"n": len(sub), "nota": "muestra insuficiente"}
            continue
        ys_sub = [c["y"] for c in sub]
        bc, bb, nte = brier_calibrado([prob(c["senal"][a]) for c in sub], ys_sub)
        rep["arquetipo_opcional"][a] = {
            "n": len(sub),
            "acierto": acierto_direccional([c["senal"][a] for c in sub], ys_sub),
            "brier_cal": bc, "brier_base": bb, "n_test": nte}

    bc_c, bb_c, nte = brier_calibrado([prob(consenso(c)) for c in casos], ys)
    rep["consenso"] = {"acierto": acierto_direccional([consenso(c) for c in casos], ys),
                       "brier_cal": bc_c, "brier_base": bb_c, "n_test": nte}

    rep["leave_one_out"] = {}
    for a in BASE:
        bc, _, _ = brier_calibrado([prob(consenso(c, (a,))) for c in casos], ys)
        rep["leave_one_out"][a] = {
            "acierto": acierto_direccional([consenso(c, (a,)) for c in casos], ys),
            "brier_cal": bc,
            "delta": round(bc - bc_c, 4) if (bc and bc_c) else None}

    rep["variantes"] = {}
    for nombre, excl in [("sin_contrarians", CONTRARIANS),
                         ("solo_direccionales", [a for a in BASE if a not in DIRECCIONALES])]:
        bc, _, _ = brier_calibrado([prob(consenso(c, tuple(excl))) for c in casos], ys)
        rep["variantes"][nombre] = {
            "acierto": acierto_direccional([consenso(c, tuple(excl)) for c in casos], ys),
            "brier_cal": bc,
            "delta": round(bc - bc_c, 4) if (bc and bc_c) else None}

    rep["por_clase"] = {}
    for clase in ("negativa", "positiva", "neutra"):
        sub = [c for c in casos if c["cat"] == clase]
        if len(sub) < 10:
            continue
        ys_s = [c["y"] for c in sub]
        rep["por_clase"][clase] = {
            "n": len(sub), "tasa_subio": round(sum(ys_s) / len(ys_s), 2),
            "consenso_acierto": acierto_direccional([consenso(c) for c in sub], ys_s),
            "arquetipos": {a: acierto_direccional([c["senal"][a] for c in sub], ys_s)
                           for a in BASE}}
    return rep


def imprimir(rep: dict) -> None:
    print(f"casos usables: {rep['n']}   tasa base subió: {rep['tasa_base']}\n")
    print("=== ARQUETIPO SUELTO ===")
    print(f"{'arquetipo':22}{'acierto%':>9}{'brier_cal':>11}{'brier_base':>12}")
    for a, v in rep["arquetipo_suelto"].items():
        print(f"{a:22}{v['acierto']:>9}{str(v['brier_cal']):>11}{str(v['brier_base']):>12}")
    if rep.get("arquetipo_opcional"):
        print("\n=== ARQUETIPOS OPCIONALES (sobre su subconjunto presente) ===")
        for a, v in rep["arquetipo_opcional"].items():
            if "acierto" in v:
                print(f"{a:22} n={v['n']}  acierto={v['acierto']}%  brier_cal={v['brier_cal']}  base={v['brier_base']}")
            else:
                print(f"{a:22} n={v['n']}  ({v.get('nota')})")
    c = rep["consenso"]
    print(f"\n=== CONSENSO (8) ===\nacierto={c['acierto']}%  brier_cal={c['brier_cal']}  "
          f"base={c['brier_base']}  n_test={c['n_test']}")
    print("\n=== LEAVE-ONE-OUT (Δbrier<0 al quitar ⇒ desorientaba) ===")
    print(f"{'quito':22}{'acierto%':>9}{'brier_cal':>11}{'Δbrier':>9}")
    for a, v in rep["leave_one_out"].items():
        print(f"{a:22}{v['acierto']:>9}{str(v['brier_cal']):>11}{str(v['delta']):>9}")
    print("\n=== VARIANTES DEL CONSENSO ===")
    for n, v in rep["variantes"].items():
        print(f"{n:22}{v['acierto']:>9}{str(v['brier_cal']):>11}{str(v['delta']):>9}")
    print("\n=== POR CLASE DE TITULAR (acierto direccional) ===")
    for clase, v in rep["por_clase"].items():
        print(f"  {clase} (n={v['n']}, tasa subió={v['tasa_subio']}): consenso={v['consenso_acierto']}%")
        for a, acc in v["arquetipos"].items():
            print(f"      {a:22}{acc}%")


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"
    imprimir(analizar(ruta))
