"""Reparto de cerebros — 1000 líderes, ~110 llamadas a la IA.

La biblia (CLAUDE.md §2.7) fija un presupuesto de ~100-120 llamadas a la
API por simulación. Con 1000 líderes de opinión, una llamada por líder lo
rompería 10x. La solución: los 1000 líderes comparten ~110 "cerebros".

Cada cerebro es UNA llamada al LLM (con el prompt de su arquetipo). Los
líderes de un mismo arquetipo se reparten sus cerebros en ronda: así hay
~110 frases distintas (variedad de sobra para el hover del demo) al costo
de siempre. La diversidad de opinión vive en los 8 arquetipos + el muestreo
del modelo, no en repetir 1000 veces la misma personalidad.

Si hay 110 líderes o menos (p. ej. la configuración vieja de 100), cada
líder es su propio cerebro y el comportamiento es idéntico al de antes.
"""

CEREBROS_OBJETIVO = 110  # dentro del presupuesto de la biblia (~100-120)


def _cerebros_por_arquetipo(conteo: dict[str, int], objetivo: int) -> dict[str, int]:
    """Reparte `objetivo` cerebros entre arquetipos, proporcional a su tamaño.

    Cada arquetipo recibe al menos 1 cerebro y nunca más cerebros que
    líderes. La suma se acerca a `objetivo` sin pasarse (salvo por el
    mínimo de 1 por arquetipo)."""
    total = sum(conteo.values())
    if total == 0:
        return {}
    if total <= objetivo:
        return dict(conteo)  # cada líder es su propio cerebro (como antes)
    cerebros = {}
    for arq, n in conteo.items():
        cerebros[arq] = max(1, min(n, round(n * objetivo / total)))
    return cerebros


def planificar(lideres: list, semilla_fn, objetivo: int = CEREBROS_OBJETIVO):
    """Devuelve (consultas, asignacion) para consultar la IA una vez por cerebro.

    - `lideres`: los agentes líder, cada uno con `.arquetipo` y `.unique_id`.
    - `semilla_fn(unique_id) -> int`: semilla base por líder (para el caché).
    - `consultas`: lista de (semilla, arquetipo_id), UNA por cerebro (~110).
    - `asignacion`: lista paralela a `lideres` con el índice del cerebro que
      le toca a cada líder (en el mismo orden que `lideres`).

    Uso: respuestas = analizar_titular(titular, consultas); luego cada líder i
    toma respuestas[asignacion[i]].
    """
    # orden de aparición de cada arquetipo y sus líderes
    por_arquetipo: dict[str, list[int]] = {}
    for i, lider in enumerate(lideres):
        por_arquetipo.setdefault(lider.arquetipo, []).append(i)

    conteo = {arq: len(idxs) for arq, idxs in por_arquetipo.items()}
    n_cerebros = _cerebros_por_arquetipo(conteo, objetivo)

    consultas: list[tuple[int, str]] = []
    asignacion: list[int] = [0] * len(lideres)
    for arq, idxs in por_arquetipo.items():
        k = n_cerebros[arq]
        base = len(consultas)  # índice global donde empiezan los cerebros de este arquetipo
        # una semilla distinta por cerebro (para el caché y variedad intra-arquetipo);
        # se ancla en el primer líder que usará ese cerebro → reproducible
        for c in range(k):
            semilla = semilla_fn(lideres[idxs[c]].unique_id)
            consultas.append((semilla, arq))
        # los líderes del arquetipo se reparten sus k cerebros en ronda
        for pos, i in enumerate(idxs):
            asignacion[i] = base + (pos % k)
    return consultas, asignacion


def expandir(respuestas_cerebros: list[dict], asignacion: list[int]) -> list[dict]:
    """Expande las ~110 respuestas de la IA a una por líder (según `asignacion`)."""
    return [respuestas_cerebros[asignacion[i]] for i in range(len(asignacion))]
