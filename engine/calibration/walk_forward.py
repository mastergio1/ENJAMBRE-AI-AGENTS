"""Fase 5 — validación WALK-FORWARD del calibrador + decisión de PROMOCIÓN.

El split 2/3 de la Fase 3 es un solo corte. Esto es más honesto: ventana
EXPANSIVA (entrena con el pasado, predice el siguiente bloque, avanza), que es
como funcionaría en vivo. Acumula TODAS las predicciones fuera de muestra y
mide el Brier, el skill vs. la tasa base y la curva de confiabilidad.

`promover` decide si un calibrador está listo para publicar `probabilidad_subida`:
solo si su Brier walk-forward le gana a la tasa base por un margen mínimo. Si
promueve, deja el calibrador ya ajustado con TODOS los datos (para que el motor
lo cargue) y un veredicto auditable. Es offline y no toca el producto: la
publicación en vivo (lenguaje CMF incluido) es una decisión aparte, humana.

Scores por modo (reconstruidos desde `senales_arquetipo`, que todos los casos
traen):
  - senal_media    : promedio simple de las voces (como el reporte histórico)
  - senal_ponderada: baja a 0.3 las voces contrarian (Intervención A)
  - direccion      : la dirección simulada en %

Uso:
    python3 engine/calibration/walk_forward.py ruta/al/calibracion.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido import calibracion as cal
from contenido.backtest import reject_grouped_input

# los 8 arquetipos clásicos que TODOS los casos traen (se exige su presencia).
BASE = ["institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
        "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente"]
# VOCES = las que SUMAN a la señal. Incluye doomer_selectivo (9º arquetipo): la
# señal de PRODUCCIÓN (senal_media_ponderada) lo incorpora, así que las
# herramientas offline deben medir la MISMA señal, no una de 8 que lo ignora
# (auditoría ampliada). Se suma solo cuando está presente (los casos viejos,
# cosechados antes de activarlo, simplemente no lo traen y no se descartan).
VOCES = BASE + ["doomer_selectivo"]
CONTRARIANS = {"quant_esceptico", "contrarian_sabio"}
MODOS = ("senal_media", "senal_ponderada", "direccion")
MARGEN_PROMOCION = 0.005  # el Brier WF debe ganarle a la base por al menos esto


def _senal(sa, peso_contr=1.0):
    num = sum(sa[a]["senal_media"] * sa[a]["n"] * (peso_contr if a in CONTRARIANS else 1.0)
              for a in VOCES if a in sa)
    den = sum(sa[a]["n"] * (peso_contr if a in CONTRARIANS else 1.0)
              for a in VOCES if a in sa)
    return num / den if den else 0.0


def cargar(ruta: str) -> list[dict]:
    with open(ruta, encoding="utf-8") as archivo:
        datos = json.load(archivo)
    reject_grouped_input(datos)
    casos = datos.get("casos", datos) if isinstance(datos, dict) else datos
    # Revisar el lote completo antes de leer la primera etiqueta de resultado.
    for caso in casos:
        reject_grouped_input(caso)
    out = []
    for c in casos:
        r = c["reaccion_real"]
        pct = r.get("pct_real")
        if pct is None or pct == 0:
            continue
        sa = c.get("senales_arquetipo") or {}
        if not all(a in sa for a in BASE):
            continue
        out.append({"fecha": c.get("fecha") or "", "y": 1 if pct > 0 else 0,
                    "sa": sa, "direccion_pct": c.get("direccion_pct") or 0.0})
    out.sort(key=lambda x: x["fecha"])
    return out


def _score(caso, modo):
    if modo == "senal_media":
        return cal.senal_a_prob_cruda({"senal_media_lideres": _senal(caso["sa"], 1.0)})
    if modo == "senal_ponderada":
        return cal.senal_a_prob_cruda({"senal_media_lideres": _senal(caso["sa"], 0.3)})
    if modo == "direccion":
        return cal.senal_a_prob_cruda({"direccion_pct": caso["direccion_pct"]}, modo="direccion")
    raise ValueError(f"modo desconocido: {modo}")


def walk_forward(casos, modo, min_entrena=200, paso=20, metodo="platt", embargo=0):
    """Ventana expansiva: entrena con [0:t], predice [t:t+paso], avanza. Acumula
    predicciones fuera de muestra y las evalúa en conjunto."""
    scores = [_score(c, modo) for c in casos]
    ys = [c["y"] for c in casos]
    preds_oos, ys_oos, preds_base = [], [], []
    t = min_entrena
    while t < len(scores):
        # EMBARGO (auditoría 4.7/C): el train excluye los `embargo` casos justo
        # antes del bloque de test, para que una ventana de resultado solapada no
        # filtre info del futuro inmediato al entrenamiento. 0 = sin embargo.
        corte_tr = max(1, t - max(0, embargo))
        s_tr, y_tr = scores[:corte_tr], ys[:corte_tr]
        fin = min(t + paso, len(scores))
        # Baseline HONESTO (auditoría 4.5): la tasa base de esta ventana se calcula
        # SOLO con el train disponible hasta el corte `t`, nunca con las etiquetas
        # OOS [t:fin] (que no se conocen al momento de predecir). Antes se usaba
        # cal.tasa_base(ys_oos) — el baseline "veía" el balance de clases del futuro.
        base_t = cal.tasa_base(y_tr)
        try:
            calib = cal.ajustar_calibrador(s_tr, y_tr, metodo=metodo)
            preds_oos.extend(calib.predict(scores[t:fin]))
        except Exception:
            preds_oos.extend(scores[t:fin])  # si falla, crudo (conservador)
        preds_base.extend([base_t] * (fin - t))
        ys_oos.extend(ys[t:fin])
        t = fin
    if not preds_oos:
        return {"error": "no hay suficientes datos para walk-forward"}
    base = round(sum(preds_base) / len(preds_base), 4)  # base media (solo-train)
    brier_modelo = cal.brier(preds_oos, ys_oos)
    brier_base = cal.brier(preds_base, ys_oos)
    return {
        "modo": modo, "metodo": metodo,
        "n_oos": len(preds_oos),
        "base": base,  # tasa base media (solo-train), para transparencia
        "brier": round(brier_modelo, 4),
        "brier_base": round(brier_base, 4),
        "skill": round(cal.skill_score(brier_modelo, brier_base), 4),
        "log_loss": round(cal.log_loss(preds_oos, ys_oos), 4),
        "ece": round(cal.ece(preds_oos, ys_oos, n_tramos=5), 4),
        "mce": round(cal.mce(preds_oos, ys_oos, n_tramos=5), 4),
        "confiabilidad": cal.curva_confiabilidad(preds_oos, ys_oos, n_tramos=5),
    }


def promover(casos, min_entrena=200, paso=20):
    """Corre walk-forward en los 3 modos × 2 métodos, elige el mejor por Brier
    OOS y decide si PROMOVER (ganarle a la base por MARGEN_PROMOCION)."""
    resultados = []
    for modo in MODOS:
        for metodo in ("platt", "isotonic"):
            r = walk_forward(casos, modo, min_entrena, paso, metodo)
            if "error" not in r:
                resultados.append(r)
    if not resultados:
        return {"promovido": False, "motivo": "sin resultados", "candidatos": []}
    resultados.sort(key=lambda r: r["brier"])
    mejor = resultados[0]
    gana = mejor["brier_base"] - mejor["brier"]
    promovido = gana >= MARGEN_PROMOCION
    salida = {"promovido": promovido,
              "margen_requerido": MARGEN_PROMOCION,
              "ganancia_vs_base": round(gana, 4),
              "mejor": mejor,
              "candidatos": resultados}
    if promovido:
        # ajusta el calibrador final con TODOS los datos (para que el motor lo cargue)
        scores = [_score(c, mejor["modo"]) for c in casos]
        ys = [c["y"] for c in casos]
        calib = cal.ajustar_calibrador(scores, ys, metodo=mejor["metodo"])
        salida["calibrador"] = {"modo": mejor["modo"], "metodo": mejor["metodo"],
                                "params": _serializar(calib)}
    return salida


def promover_anidado(casos, min_entrena=150, paso=20, pct_holdout=20, embargo=0):
    """Promoción con holdout final CONGELADO (auditoría 4.6 y 'congelar holdout').

    Evita el sesgo de selección múltiple: `promover` elige el mejor de 6 configs
    mirando el MISMO OOS que luego reporta (optimismo). Aquí:
      1. Se parte temporalmente: desarrollo (lo viejo) y holdout final (el pct%
         más reciente), con un `embargo` de separación. Los casos ya vienen
         ordenados por fecha desde `cargar`.
      2. La elección de (modo, método) se hace SOLO con el desarrollo (walk-forward
         interno). El holdout NO participa en la selección.
      3. El calibrador elegido se ajusta con TODO el desarrollo y se evalúa UNA vez
         sobre el holdout congelado. Ese número es el veredicto honesto.
      4. Promueve solo si le gana a la base (del desarrollo) EN EL HOLDOUT.
    """
    n = len(casos)
    n_hold = round(n * pct_holdout / 100)
    corte = n - n_hold
    if corte - embargo < min_entrena or n_hold < 20:
        return {"promovido": False, "motivo": "datos insuficientes para anidar",
                "n": n, "n_holdout": n_hold}
    desarrollo = casos[:corte - embargo] if embargo else casos[:corte]
    holdout = casos[corte:]

    # 1) selección SOLO en desarrollo (walk-forward interno)
    candidatos = []
    for modo in MODOS:
        for metodo in ("platt", "isotonic"):
            r = walk_forward(desarrollo, modo, min_entrena, paso, metodo, embargo=embargo)
            if "error" not in r:
                candidatos.append(r)
    if not candidatos:
        return {"promovido": False, "motivo": "sin candidatos", "candidatos": []}
    candidatos.sort(key=lambda r: r["brier"])
    elegido = candidatos[0]

    # 2) ajustar el elegido con TODO el desarrollo y evaluar UNA vez en el holdout
    s_dev = [_score(c, elegido["modo"]) for c in desarrollo]
    y_dev = [c["y"] for c in desarrollo]
    calib = cal.ajustar_calibrador(s_dev, y_dev, metodo=elegido["metodo"])
    s_hold = [_score(c, elegido["modo"]) for c in holdout]
    y_hold = [c["y"] for c in holdout]
    preds_hold = calib.predict(s_hold)
    base_dev = cal.tasa_base(y_dev)  # base HONESTA: solo-desarrollo, no ve el holdout
    brier_hold = cal.brier(preds_hold, y_hold)
    brier_base_hold = cal.brier([base_dev] * len(y_hold), y_hold)
    gana = brier_base_hold - brier_hold
    holdout_metricas = {
        "n": len(y_hold), "brier": round(brier_hold, 4),
        "brier_base": round(brier_base_hold, 4),
        "skill": round(cal.skill_score(brier_hold, brier_base_hold), 4),
        "log_loss": round(cal.log_loss(preds_hold, y_hold), 4),
        "ece": round(cal.ece(preds_hold, y_hold, n_tramos=5), 4),
    }
    promovido = gana >= MARGEN_PROMOCION
    salida = {"promovido": promovido, "margen_requerido": MARGEN_PROMOCION,
              "ganancia_vs_base_holdout": round(gana, 4),
              "elegido": {"modo": elegido["modo"], "metodo": elegido["metodo"]},
              "seleccion_desarrollo": elegido,  # su métrica de desarrollo (optimista)
              "holdout_final": holdout_metricas,  # el veredicto honesto
              "candidatos": candidatos}
    if promovido:
        # calibrador final con TODOS los datos (dev+holdout), ya validado
        scores = [_score(c, elegido["modo"]) for c in casos]
        ys = [c["y"] for c in casos]
        final = cal.ajustar_calibrador(scores, ys, metodo=elegido["metodo"])
        salida["calibrador"] = {"modo": elegido["modo"], "metodo": elegido["metodo"],
                                "params": _serializar(final)}
    return salida


def _serializar(calib) -> dict:
    """Parámetros del calibrador en JSON, para que el motor lo reconstruya."""
    if hasattr(calib, "a") and hasattr(calib, "b"):   # Platt
        return {"tipo": "platt", "a": calib.a, "b": calib.b,
                "mu": calib._mu, "sd": calib._sd}
    if hasattr(calib, "_xs"):                          # Isotonic
        return {"tipo": "isotonic", "xs": list(calib._xs), "ys": list(calib._ys)}
    return {}


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "calibracion.json"
    casos = cargar(ruta)
    print(f"casos: {len(casos)}\n")
    rep = promover(casos)
    print(f"{'modo':16}{'metodo':10}{'n_oos':>7}{'brier':>9}{'base':>9}{'skill':>9}")
    for r in rep["candidatos"]:
        print(f"{r['modo']:16}{r['metodo']:10}{r['n_oos']:>7}{r['brier']:>9}{r['brier_base']:>9}{r['skill']:>9}")
    print(f"\nMejor: {rep['mejor']['modo']}/{rep['mejor']['metodo']}  "
          f"gana a la base por {rep['ganancia_vs_base']} (requiere {rep['margen_requerido']})")
    print(f"PROMOVIDO: {rep['promovido']}")
