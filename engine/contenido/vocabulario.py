"""Filtro de vocabulario CMF (CONTENIDO.md sección 1 — NO NEGOCIABLE).

Todo texto que esta capa publica es simulación educativa de comportamiento
de masas. Este módulo es el filtro en código: la lista de términos
prohibidos, el disclaimer oficial y las funciones de verificación.
Nada se publica sin pasar por aquí.
"""

import unicodedata

DISCLAIMER = (
    "Herramienta educativa y recreativa en proceso de creación y mejora. "
    "Simula el comportamiento de masas con agentes de IA; "
    "no constituye asesoría ni recomendación de inversión."
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


# frase con la que se reemplaza la voz de un líder que no pasa el filtro:
# neutra, CMF-limpia y en la voz genérica del analista (no deja hueco visual).
FRASE_NEUTRAL = "Prefiere no comentar este titular."


def frase_segura(texto: str) -> str:
    """La voz de un líder solo se muestra si pasa el filtro CMF; si no —p. ej.
    alguien empujó al modelo a un «compra ahora»— se neutraliza. Las frases de
    los líderes son lo que más gente ve (web, muro, widget), así que este es el
    borde de cumplimiento más importante de cerrar."""
    return texto if es_publicable(texto) else FRASE_NEUTRAL


def sanear_frases(respuestas: list[dict]) -> list[dict]:
    """Neutraliza IN SITU las frases no publicables de las respuestas de los
    cerebros, apenas vuelven de la IA y ANTES de repartirlas a la web, la base
    y el muro. Devuelve la misma lista (para encadenar con reparto.expandir)."""
    for r in respuestas:
        if isinstance(r, dict) and "frase" in r:
            r["frase"] = frase_segura(str(r.get("frase", "")))
    return respuestas


def verificar_pieza(texto: str) -> list[str]:
    """Verificación completa de una pieza pública (página, correo, widget).

    Devuelve la lista de problemas encontrados (vacía = la pieza pasa):
    términos prohibidos presentes y/o disclaimer ausente.
    """
    problemas = [f"término prohibido: «{t}»" for t in encontrar_prohibidas(texto)]
    if _normalizar(DISCLAIMER) not in _normalizar(texto):
        problemas.append("falta el disclaimer oficial")
    return problemas
