"""Fase 0.4 — Holdout congelado con manifiesto y hash.

El "juez" protegido: un conjunto final de evaluación que se separa por TIEMPO
(los casos más nuevos), se CONGELA con un hash SHA-256 de su membresía y sus
etiquetas, y nunca se usa para ajustar nada. Reglas (de la auditoría v3):

- Partición temporal por evento; el holdout son los casos más recientes.
- Añadir datos nuevos NO cambia la membresía congelada (se vuelve a verificar
  contra el manifiesto, no se re-parte).
- Si una etiqueta se revisa o un caso desaparece, el hash deja de coincidir →
  salta la auditoría.
- Embargo temporal: se purgan del desarrollo los casos demasiado cercanos al
  corte (para no filtrar etiquetas que se solapan con el holdout).

Puro y testeable (sin red).
"""
import hashlib
import json
from datetime import datetime, timezone

ESQUEMA = "holdout-v1"


class HoldoutInvalido(ValueError):
    pass


def _hash(pares) -> str:
    """Hash estable de los pares (id, etiqueta) ya ordenados."""
    crudo = json.dumps(pares, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()


def _dias(fa, fb):
    return abs((datetime.fromisoformat(fa[:10]) - datetime.fromisoformat(fb[:10])).days)


def construir_manifiesto(casos, *, pct_holdout=20, clave_id="id", clave_y="y",
                         clave_fecha="fecha", embargo_dias=0):
    """Separa el holdout (los `pct_holdout`% más recientes) y lo CONGELA.

    Devuelve el manifiesto con la lista de ids del holdout y su hash. La partición
    es temporal; los casos que comparten la fecha de corte caen enteros en el
    holdout (no se parte un día). El embargo purga del desarrollo los casos dentro
    de `embargo_dias` antes del corte."""
    if not casos:
        raise HoldoutInvalido("no hay casos")
    ordenados = sorted(casos, key=lambda c: c[clave_fecha])
    n_hold = max(1, round(len(ordenados) * pct_holdout / 100))
    corte_idx = len(ordenados) - n_hold
    fecha_corte = ordenados[corte_idx][clave_fecha][:10]
    holdout = [c for c in ordenados if c[clave_fecha][:10] >= fecha_corte]
    desarrollo = [c for c in ordenados if c[clave_fecha][:10] < fecha_corte]
    if embargo_dias:
        desarrollo = [c for c in desarrollo
                      if _dias(c[clave_fecha], fecha_corte) > embargo_dias]
    pares = sorted((str(c[clave_id]), c[clave_y]) for c in holdout)
    return {
        "esquema": ESQUEMA,
        "creado_iso": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pct_holdout": pct_holdout, "fecha_corte": fecha_corte,
        "embargo_dias": embargo_dias,
        "n_total": len(casos), "n_desarrollo": len(desarrollo), "n_holdout": len(holdout),
        "holdout_ids": [p[0] for p in pares],
        "hash": _hash(pares),
    }


def verificar_manifiesto(manifiesto, casos, *, clave_id="id", clave_y="y"):
    """Comprueba que el holdout congelado sigue intacto en `casos`.

    Devuelve {ok, hash_coincide, faltantes, revisados}. `ok` es True solo si cada
    id del holdout sigue presente con la MISMA etiqueta (mismo hash). Detecta
    casos que desaparecieron o cuya etiqueta se revisó."""
    por_id = {str(c[clave_id]): c[clave_y] for c in casos}
    ids = manifiesto["holdout_ids"]
    faltantes = [i for i in ids if i not in por_id]
    presentes = sorted((i, por_id[i]) for i in ids if i in por_id)
    hash_actual = _hash(presentes)
    coincide = (hash_actual == manifiesto["hash"]) and not faltantes
    return {"ok": coincide, "hash_coincide": hash_actual == manifiesto["hash"],
            "faltantes": faltantes, "n_holdout": len(ids),
            "n_presentes": len(presentes)}


def particionar(casos, manifiesto, *, clave_id="id", clave_fecha="fecha"):
    """Devuelve (desarrollo, holdout) usando la membresía CONGELADA del manifiesto.

    El holdout son exactamente los ids del manifiesto. El desarrollo EXCLUYE las
    filas posteriores al corte que NO están en el holdout (llegaron después de
    congelarlo): entrenar un examen con datos más nuevos que su propio test es fuga
    temporal (auditoría v4). Esas filas quedan fuera de ambos (cohorte futura), no
    en desarrollo."""
    ids_hold = set(manifiesto["holdout_ids"])
    corte = manifiesto.get("fecha_corte")
    holdout = [c for c in casos if str(c[clave_id]) in ids_hold]
    desarrollo = []
    for c in casos:
        if str(c[clave_id]) in ids_hold:
            continue
        if corte and str(c.get(clave_fecha, ""))[:10] >= corte:
            continue  # posterior al corte y NO en el holdout → cohorte futura, fuera
        desarrollo.append(c)
    return desarrollo, holdout
