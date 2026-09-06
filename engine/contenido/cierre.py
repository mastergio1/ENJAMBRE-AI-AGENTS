"""La edición de la TARDE de El Pulso — 'El cierre del mercado' (Premium).

Después del cierre de EE.UU., el reportero IA caza los mayores movimientos REALES
del día y explica por qué. Es el premio de ser Premium: la mañana es para todos
(pre-market + noticias); la tarde a fondo, para quien paga.

No simula el enjambre (evita duplicar las destacadas de la mañana y el costo): su
valor es "qué se movió de verdad y por qué", investigado y verificado.
"""

from contenido import investigador
from contenido.fuentes import yahoo

MAX_MOVERS_CIERRE = 5


def preparar_cierre(maximo: int = MAX_MOVERS_CIERRE) -> dict | None:
    """Arma el cierre del día: los mayores movimientos investigados. None si no
    hay movimientos (mercado cerrado sin datos / degradación) — entonces no hay
    edición de tarde y no se molesta a nadie."""
    movers = investigador.investigar_movers(yahoo.movers_del_dia(n=12), maximo=maximo)
    if not movers:
        return None
    # de más movido a menos (por si el orden se perdió)
    movers.sort(key=lambda m: abs(m.get("var_pct") or 0), reverse=True)
    return {"titulo": "El cierre del mercado", "movers": movers}
