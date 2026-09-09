"""Verificador — el arnés que congela el baseline y separa visible / held-out.

Primer paso (barato) de la metodología tipo "sala de hipótesis": ningún cambio
entra a producción sin superar el BASELINE en casos HELD-OUT (reservados, que no
se usaron para afinar). Este módulo NO genera hipótesis ni corre agentes LLM —
solo provee el arnés, y es 100% local y gratis (no llama a la IA):

- `es_holdout(sim_id)`: partición DETERMINÍSTICA y estable (hash del sim_id). El
  mismo caso cae siempre del mismo lado, y un caso nuevo del cosechador se
  auto-clasifica con la misma regla (no hay que re-partir a mano).
- `particionar(casos)`: separa una lista de casos en (visible, held_out).
- `cargar_baseline()` / `guardar_baseline()`: la foto congelada de las métricas.
- `comparar(nuevas)`: aplica los criterios de promoción (superar el baseline y no
  degradar NINGÚN régimen por encima de un umbral fijado de antemano).

Regla de oro: el verificador recibe NÚMEROS (métricas), nunca la justificación en
prosa de un cambio — así la narrativa no contamina el juicio.
"""
import hashlib
import json
from pathlib import Path

# ~30% de los casos se reservan para validar (no se afinan sobre ellos).
PORCENTAJE_HOLDOUT = 30
RUTA_BASELINE = Path(__file__).parent / "baseline.json"


def es_holdout(sim_id: str, pct: int = PORCENTAJE_HOLDOUT) -> bool:
    """True si el caso pertenece al conjunto HELD-OUT (reservado para validar).

    Determinístico y estable: NO usa `random` (que cambiaría en cada corrida);
    usa un hash del sim_id, así el reparto es reproducible y un caso nuevo cae
    solo en su lado sin re-partir nada."""
    h = int(hashlib.sha256(str(sim_id).encode()).hexdigest(), 16)
    return (h % 100) < pct


def particionar(casos: list[dict]) -> tuple[list, list]:
    """Separa casos (cada uno con 'sim_id') en (visible, held_out)."""
    visible, holdout = [], []
    for c in casos:
        (holdout if es_holdout(c.get("sim_id", "")) else visible).append(c)
    return visible, holdout


def cargar_baseline() -> dict:
    """La foto congelada de las métricas del motor (o {} si no existe)."""
    try:
        return json.loads(RUTA_BASELINE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def guardar_baseline(metricas: dict) -> None:
    """Congela una foto de métricas. Usar con criterio: el baseline es el punto
    de comparación, no se pisa a la ligera."""
    RUTA_BASELINE.write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")


def comparar(nuevas: dict, baseline: dict | None = None,
             umbral_degradacion: float = 0.02) -> dict:
    """Compara métricas de acierto NUEVAS contra el baseline congelado.

    `nuevas` es un dict {clave: acierto 0..1} con claves tipo "indice_negativa".
    Criterios de promoción (documento §5): una mejora que rompe un régimen NO se
    promueve. Devuelve:
      - mejoras: métricas que subieron
      - degradaciones: las que bajaron más que `umbral_degradacion`
      - promovible: True solo si hay mejora neta y NINGUNA degradación de régimen
    """
    base = baseline if baseline is not None else cargar_baseline()
    ref = base.get("acierto", {}) if isinstance(base, dict) else {}
    mejoras, degradaciones = {}, {}
    for k, v in nuevas.items():
        if k not in ref or not isinstance(ref[k], (int, float)):
            continue
        d = v - ref[k]
        if d > 0:
            mejoras[k] = round(d, 4)
        elif d < -umbral_degradacion:
            degradaciones[k] = round(d, 4)
    return {
        "mejoras": mejoras,
        "degradaciones": degradaciones,
        "promovible": bool(mejoras) and not degradaciones,
    }
