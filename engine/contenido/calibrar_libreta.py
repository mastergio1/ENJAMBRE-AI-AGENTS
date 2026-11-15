"""Tubería de calibración: desde la libreta exportada al veredicto Brier.

Uso (cuando ya tengas libreta_export.json de Render):

    python -m contenido.calibrar_libreta libreta_export.json

Qué hace, en simple:
1. Lee los casos (señal del enjambre + resultado real).
2. Convierte cada caso en (probabilidad cruda del enjambre, ¿subió? sí/no).
3. Parte en entrenamiento/prueba, ajusta los calibradores SOLO con entrenamiento.
4. Mide el Brier en prueba: enjambre crudo vs calibrado vs líneas base triviales.
5. Imprime un veredicto honesto, sin maquillaje.

No llama a la IA ni toca la red. Pura matemática sobre datos ya medidos.
"""

import json
import random
import sys

from contenido import calibracion as cal


def _resultado_binario(pct_real) -> int | None:
    """¿Subió? 1 = sí, 0 = no. Los exactamente-cero (rarísimos) se descartan."""
    if pct_real is None:
        return None
    v = float(pct_real)
    if v == 0:
        return None
    return 1 if v > 0 else 0


def preparar(casos: list[dict], modo: str = "senal_media"):
    """Convierte casos crudos en pares (prob_cruda, resultado_binario), filtrando
    los que no tienen señal o resultado usable."""
    scores, ys = [], []
    for c in casos:
        y = _resultado_binario(c.get("pct_real"))
        if y is None:
            continue
        # el reporte que espera el mapeo usa estas mismas claves
        try:
            p = cal.senal_a_prob_cruda(c, modo=modo)
        except Exception:
            continue
        scores.append(p)
        ys.append(y)
    return scores, ys


def calibrar(casos: list[dict], modo: str = "senal_media",
             frac_prueba: float = 0.3, seed: int = 42) -> dict:
    scores, ys = preparar(casos, modo=modo)
    n = len(ys)
    if n < 10:
        return {"error": f"muy pocos casos usables ({n}); se necesitan >= 10 para algo informativo"}

    # barajado determinístico y split
    idx = list(range(n))
    random.Random(seed).shuffle(idx)
    corte = int(n * (1 - frac_prueba))
    tr = idx[:corte]
    te = idx[corte:]
    s_tr = [scores[i] for i in tr]; y_tr = [ys[i] for i in tr]
    s_te = [scores[i] for i in te]; y_te = [ys[i] for i in te]

    salida = {"modo": modo, "n_total": n, "n_entrena": len(tr), "n_prueba": len(te),
              "tasa_subidas": round(cal.tasa_base(ys), 4)}

    for metodo in ("platt", "isotonic"):
        c = cal.ajustar_calibrador(s_tr, y_tr, metodo=metodo)
        rep = cal.evaluar_calibracion(s_te, y_te, calibrador=c)
        salida[metodo] = rep
        salida[f"{metodo}_confiabilidad"] = cal.curva_confiabilidad(c.predict(s_te), y_te)
    return salida


def _imprimir(rep: dict) -> None:
    if "error" in rep:
        print("No se pudo calibrar:", rep["error"])
        return
    print(f"Casos usables: {rep['n_total']}  (entrena {rep['n_entrena']} / prueba {rep['n_prueba']})")
    print(f"Tasa de subidas en los datos: {rep['tasa_subidas']:.1%}")
    print()
    print("Brier en prueba (MENOR = mejor):")
    base = rep["platt"]
    print(f"  Línea base 50% constante : {base['brier_constante_050']}")
    print(f"  Línea base tasa de subida: {base['brier_tasa_base']}")
    print(f"  Enjambre CRUDO           : {base['brier_cruda']}")
    for metodo in ("platt", "isotonic"):
        m = rep[metodo]
        print(f"  Enjambre + {metodo:<9} : {m.get('brier_calibrada')}  "
              f"(skill vs base: {m.get('skill_vs_base')})")
    print()
    print("Veredicto honesto:")
    mejor = min(("platt", "isotonic"), key=lambda k: rep[k].get("brier_calibrada", 9))
    m = rep[mejor]
    if m.get("brier_calibrada", 9) < base["brier_tasa_base"] and m.get("skill_vs_base", 0) > 0:
        print(f"  El enjambre calibrado ({mejor}) SUPERA a la línea base trivial. Hay señal.")
    else:
        print(f"  El enjambre NO supera claramente la línea base. Fracaso informativo "
              f"(esperado fuera de macro).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python -m contenido.calibrar_libreta <libreta_export.json> [modo]")
        sys.exit(2)
    ruta = sys.argv[1]
    modo = sys.argv[2] if len(sys.argv) > 2 else "senal_media"
    with open(ruta, encoding="utf-8") as f:
        casos = json.load(f)
    _imprimir(calibrar(casos, modo=modo))
