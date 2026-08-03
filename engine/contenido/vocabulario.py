"""Filtro de vocabulario CMF (CONTENIDO.md sección 1 — NO NEGOCIABLE).

Todo texto que esta capa publica es simulación educativa de comportamiento
de masas. Este módulo es el filtro en código: la lista de términos
prohibidos, el disclaimer oficial y las funciones de verificación.
Nada se publica sin pasar por aquí.
"""

import unicodedata

DISCLAIMER = (
    "Simulación educativa de comportamiento de masas con agentes de IA. "
    "No constituye asesoría ni recomendación de inversión."
)

# términos prohibidos por el principio regulatorio (más variantes obvias);
# se comparan sin tildes y en minúsculas
PROHIBIDAS = [
    "recomendamos",
    "te recomiendo",
    "recomendacion de compra",
    "recomendacion de venta",
    "deberias comprar",
    "deberias vender",
    "deberia comprar",
    "deberia vender",
    "debes comprar",
    "debes vender",
    "hay que comprar",
    "hay que vender",
    "compra ahora",
    "vende ahora",
    "el precio subira",
    "el precio bajara",
    "va a subir",
    "va a bajar",
    "prediccion",
    "predecimos",
    "senal de inversion",
    "senal de compra",
    "senal de venta",
    "oportunidad de compra",
    "oportunidad de venta",
    "consejo de inversion",
    "asesoria personalizada",
    "vendan todo",
    "compren todo",
    # inglés: los titulares y datos llegan en inglés (Alpaca/Barchart)
    "should you buy",
    "should you sell",
    "should i buy",
    "should i sell",
    "buy now",
    "sell now",
    "strong buy",
    "table pounding buy",
    "price target",
    "buy alert",
    "will surge",
    "will crash",
    "guaranteed return",
    "must buy",
]


def _normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para que 'Predicción' no se escape."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.lower()


def encontrar_prohibidas(texto: str) -> list[str]:
    """Devuelve los términos prohibidos presentes en el texto (vacía = limpio)."""
    normalizado = _normalizar(texto)
    return [termino for termino in PROHIBIDAS if termino in normalizado]


def es_publicable(texto: str) -> bool:
    """True si el texto no contiene vocabulario prohibido."""
    return not encontrar_prohibidas(texto)


def verificar_pieza(texto: str) -> list[str]:
    """Verificación completa de una pieza pública (página, correo, widget).

    Devuelve la lista de problemas encontrados (vacía = la pieza pasa):
    términos prohibidos presentes y/o disclaimer ausente.
    """
    problemas = [f"término prohibido: «{t}»" for t in encontrar_prohibidas(texto)]
    if _normalizar(DISCLAIMER) not in _normalizar(texto):
        problemas.append("falta el disclaimer oficial")
    return problemas
