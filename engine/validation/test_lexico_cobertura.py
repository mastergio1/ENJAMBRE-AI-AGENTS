"""
Cobertura y acierto del respaldo léxico (`sentimiento_lexico`) sobre los 645
casos reales. Mide con la función REAL del motor (no un diccionario de juguete):

- % "mudo": titulares donde el léxico no encuentra ninguna palabra (señal 0).
- acierto de dirección cuando OPINA, separado por negativas y positivas.
- falsos positivos: positivas que el léxico marca como bajistas (el riesgo de
  agregar jerga bajista sin cuidado).

El respaldo solo se usa cuando la API de LLM no está disponible; por eso esto
mide ROBUSTEZ del plan B, no el 38% real (que usa el LLM). Sin coste, sin red
salvo la lectura del respaldo público.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from brains.fallback import sentimiento_lexico  # noqa: E402


def _signo(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def medir(casos: list[dict]) -> dict:
    total = mudo = 0
    op_neg = ok_neg = op_pos = ok_pos = fp_pos = 0
    for c in casos:
        rr = c.get("reaccion_real") or {}
        cat = rr.get("categoria")
        real = rr.get("pct_real")
        if cat not in ("negativa", "positiva") or real is None:
            continue
        total += 1
        s = sentimiento_lexico(c.get("titular", ""))
        if abs(s) < 1e-9:
            mudo += 1
            continue
        acierta = _signo(s) == _signo(real)
        if cat == "negativa":
            op_neg += 1
            ok_neg += acierta
        else:
            op_pos += 1
            ok_pos += acierta
            if s < 0:               # positiva leída como bajista = falso positivo
                fp_pos += 1
    return {
        "total": total, "mudo": mudo,
        "op_neg": op_neg, "ok_neg": ok_neg,
        "op_pos": op_pos, "ok_pos": ok_pos, "fp_pos": fp_pos,
    }


def _pct(a, b):
    return f"{100*a/b:.1f}%" if b else "s/d"


def imprimir(m: dict) -> None:
    t = m["total"]
    opina = t - m["mudo"]
    print(f"  casos con dirección real: {t}")
    print(f"  MUDO (señal 0):           {m['mudo']}  ({_pct(m['mudo'], t)})")
    print(f"  opina:                    {opina}  ({_pct(opina, t)})")
    print(f"  acierto NEGATIVAS (opina):{m['ok_neg']}/{m['op_neg']}  ({_pct(m['ok_neg'], m['op_neg'])})")
    print(f"  acierto POSITIVAS (opina):{m['ok_pos']}/{m['op_pos']}  ({_pct(m['ok_pos'], m['op_pos'])})")
    print(f"  FALSOS POSITIVOS (pos leída bajista): {m['fp_pos']}  ({_pct(m['fp_pos'], m['op_pos'])})")


def test_cobertura_y_precision():
    """El léxico ampliado: cubre más (menos mudo) manteniendo la precisión
    global y bajando los falsos positivos.

    Nota honesta sobre la métrica: subir la cobertura necesariamente aflora
    casos irreducibles (titulares alcistas que precedieron caídas), así que la
    TASA de acierto en negativas baja aunque el número absoluto de negativas
    bien clasificadas suba. Por eso NO exigimos una tasa alta de negativas
    (eso se optimiza trivialmente quedándose mudo). Exigimos: más cobertura,
    precisión global sana y menos falsos positivos que la línea base (39.7%).
    """
    from contenido.respaldo import casos_remotos
    m = medir(casos_remotos())
    assert m["total"] > 0, "no se leyeron casos del respaldo"
    opina = m["total"] - m["mudo"]
    # cobertura: el mudo baja del 65% (línea base medida: 74.5%)
    assert m["mudo"] / m["total"] < 0.65, f"mudo demasiado alto: {m['mudo']}/{m['total']}"
    # precisión global (cuando opina): ≥ 63%
    aciertos = m["ok_neg"] + m["ok_pos"]
    assert aciertos / max(1, opina) >= 0.63, "precisión global cayó"
    # falsos positivos en positivas: por debajo de la línea base (39.7%)
    assert m["fp_pos"] / max(1, m["op_pos"]) < 0.39, "demasiados falsos positivos"


if __name__ == "__main__":
    from contenido.respaldo import casos_remotos
    print("\n📚 Cobertura del respaldo léxico sobre los 645 casos")
    print("=" * 55)
    imprimir(medir(casos_remotos()))
    print("=" * 55)
