"""Calibración agregada sobre la libreta de respaldo (datos/calibracion.json).

Toma los casos reales (reacción del enjambre vs movimiento real) y mide si la
probabilidad del enjambre, calibrada (Platt / Isotónica), supera a líneas base
triviales — con SPLIT TEMPORAL (entrena con los antiguos, prueba con los
recientes) para no filtrar futuro. Desglosa además por mercado.

No llama a la IA. Pura matemática sobre casos ya medidos.

Uso:  python -m calibration.calibrar_respaldo <ruta_calibracion.json>
(el archivo vive en la rama respaldo-datos: datos/calibracion.json)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brains.mercado import clasificar_lexico
from contenido import calibracion as cal


def _cargar_casos(ruta: str) -> list[dict]:
    obj = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return obj["casos"] if isinstance(obj, dict) else obj


def _filas(casos, mercado=None):
    """(fecha, direccion_pct, resultado_binario) de los casos con IA real."""
    out = []
    for c in casos:
        rr = c.get("reaccion_real") or {}
        if rr.get("cerebros") != "ia":
            continue
        pr, d = rr.get("pct_real"), c.get("direccion_pct")
        if pr is None or d is None or float(pr) == 0:
            continue
        if mercado is not None and clasificar_lexico(c.get("titular", "")) != mercado:
            continue
        out.append((c.get("fecha", ""), float(d), 1 if float(pr) > 0 else 0))
    return out


def _prob(d):
    return cal.senal_a_prob_cruda({"direccion_pct": d}, modo="direccion")


def evaluar(filas, frac_prueba=0.3):
    if len(filas) < 20:
        return {"n": len(filas), "error": "muy pocos casos para concluir"}
    filas = sorted(filas, key=lambda x: x[0])          # split TEMPORAL
    corte = int(len(filas) * (1 - frac_prueba))
    tr, te = filas[:corte], filas[corte:]
    s_tr = [_prob(d) for _, d, _ in tr]; y_tr = [y for _, _, y in tr]
    s_te = [_prob(d) for _, d, _ in te]; y_te = [y for _, _, y in te]
    platt = cal.ajustar_calibrador(s_tr, y_tr, "platt")
    iso = cal.ajustar_calibrador(s_tr, y_tr, "isotonic")
    base = cal.brier([cal.tasa_base(y_te)] * len(te), y_te)
    b_platt = cal.brier(platt.predict(s_te), y_te)
    b_iso = cal.brier(iso.predict(s_te), y_te)
    return {
        "n": len(filas), "entrena": len(tr), "prueba": len(te),
        "tasa_subidas": round(cal.tasa_base([y for _, _, y in filas]), 3),
        "brier_base_rate": round(base, 4),
        "brier_crudo": round(cal.brier(s_te, y_te), 4),
        "brier_platt": round(b_platt, 4),
        "brier_isotonic": round(b_iso, 4),
        "skill_mejor_vs_base": round(cal.skill_score(min(b_platt, b_iso), base), 3),
    }


def main(ruta):
    casos = _cargar_casos(ruta)
    print("=== AGREGADO (todos los mercados) ===")
    print(json.dumps(evaluar(_filas(casos)), ensure_ascii=False, indent=1))
    for m in ("indice", "cripto", "accion"):
        print(f"=== {m.upper()} ===")
        print(json.dumps(evaluar(_filas(casos, mercado=m)), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "datos/calibracion.json")
