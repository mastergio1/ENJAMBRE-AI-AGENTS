"""Red de influencia de El Enjambre (CLAUDE.md sección 6).

Grafo dirigido tipo scale-free: pocos nodos muy conectados (los líderes),
muchos poco conectados. Los líderes tienen 20-150 seguidores según su
arquetipo; los agentes retail (manada, FOMO, miedoso) tienen además 3-8
vecinos "pares" entre sí — el rumor también viaja horizontalmente.
Los institucionales NO están en la red: reaccionan a precio y
fundamentales, no a rumores.
"""

from agents.lider import LiderOpinion
from agents.reglas import (
    BuyAndHold,
    Contrarian,
    FomoRetail,
    Manada,
    Miedoso,
    NoiseTrader,
)
from brains.arquetipos import POR_ID

CLASES_SOCIALES = {
    "noise_trader": NoiseTrader,
    "manada": Manada,
    "fomo": FomoRetail,
    "miedoso": Miedoso,
    "contrarian": Contrarian,
    "buy_and_hold": BuyAndHold,
}

# tipos que además tienen pares horizontales (tipos 8-10 de la mezcla)
CON_PARES = (Manada, FomoRetail, Miedoso)


def construir_red(model) -> None:
    """Conecta líderes con seguidores y teje los pares retail.

    Deja en cada agente:
      - agente.pares: vecinos horizontales (solo tipos 8-10)
      - agente.lideres_seguidos: los líderes cuya señal recibe
      - agente.vecinos: pares + líderes (su "red" observable)
      - lider.seguidores: a quiénes arrastra
    """
    rng = model.random
    lideres = [a for a in model.agents if isinstance(a, LiderOpinion)]
    por_tipo = {
        tipo_id: [a for a in model.agents if isinstance(a, clase)]
        for tipo_id, clase in CLASES_SOCIALES.items()
    }

    # --- líderes → seguidores (conexión preferencial: los populares
    #     se vuelven más populares → distribución scale-free) ---
    popularidad: dict[int, int] = {}
    for lider in lideres:
        arquetipo = POR_ID[lider.arquetipo]
        minimo, maximo = arquetipo["seguidores"]
        cuantos = rng.randint(minimo, maximo)
        candidatos = [a for t in arquetipo["sigue"] for a in por_tipo[t]]
        elegidos = _muestra_preferencial(rng, candidatos, cuantos, popularidad)
        for seguidor in elegidos:
            lider.seguidores.append(seguidor)
            seguidor.lideres_seguidos.append(lider)
            popularidad[seguidor.unique_id] = popularidad.get(seguidor.unique_id, 0) + 1

    # --- la manada y el FOMO necesitan 1-2 líderes en su red sí o sí ---
    for tipo_id in ("manada", "fomo"):
        for agente in por_tipo[tipo_id]:
            while len(agente.lideres_seguidos) < rng.randint(1, 2):
                lider = rng.choice(lideres)
                if lider in agente.lideres_seguidos:
                    continue
                lider.seguidores.append(agente)
                agente.lideres_seguidos.append(lider)

    # --- pares horizontales entre retail (tipos 8-10), conexión
    #     preferencial: quien ya tiene vecinos atrae más vecinos ---
    sociales = [a for a in model.agents if isinstance(a, CON_PARES)]
    for agente in sociales:
        deseados = rng.randint(3, 8)
        while len(agente.pares) < deseados:
            par = _eleccion_preferencial(rng, sociales, agente)
            if par not in agente.pares:
                agente.pares.append(par)
                par.pares.append(agente)  # el rumor viaja en ambos sentidos

    # --- la red observable de cada agente ---
    for agente in model.agents:
        agente.vecinos = list(agente.pares) + list(agente.lideres_seguidos)


def _muestra_preferencial(rng, candidatos, cuantos, popularidad) -> list:
    """Muestra sin reemplazo, con peso 1 + popularidad actual del candidato."""
    if cuantos >= len(candidatos):
        return list(candidatos)
    pesos = [1 + popularidad.get(c.unique_id, 0) for c in candidatos]
    elegidos: list = []
    indices = list(range(len(candidatos)))
    for _ in range(cuantos):
        total = sum(pesos[i] for i in indices)
        objetivo = rng.random() * total
        acumulado = 0.0
        for pos, i in enumerate(indices):
            acumulado += pesos[i]
            if acumulado >= objetivo:
                elegidos.append(candidatos[i])
                indices.pop(pos)
                break
    return elegidos


def _eleccion_preferencial(rng, poblacion, excluido):
    """Elige un agente con peso 1 + grado actual, excluyéndose a sí mismo."""
    while True:
        # dos intentos sesgados: uno uniforme y uno por popularidad
        candidato = rng.choice(poblacion)
        if candidato is excluido:
            continue
        # aceptación proporcional al grado (con piso para los nuevos)
        if rng.random() < (1 + len(candidato.pares)) / 9:
            return candidato
