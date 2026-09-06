"""Extrae el TEXTO de una respuesta de la API de Anthropic, saltando el
razonamiento (thinking).

Los modelos nuevos (claude-sonnet-5, etc.) RAZONAN antes de responder: el
`content` de la respuesta puede empezar con uno o más ThinkingBlock (que NO
tienen `.text`), y recién después viene el bloque de texto. Tomar
`respuesta.content[0].text` a ciegas revienta con AttributeError cuando el primer
bloque es de razonamiento — y esa excepción, tragada por un try/except, dejaba a
El Pulso sin edición y sin correo.

Esta función junta SOLO los bloques de tipo texto, así funciona con o sin
razonamiento y con cualquier modelo. Nunca lanza.
"""


def texto_de(respuesta) -> str:
    """El texto de una respuesta de Anthropic, ignorando los bloques de
    razonamiento. '' si no hay texto (nunca lanza)."""
    partes = []
    for bloque in getattr(respuesta, "content", None) or []:
        if getattr(bloque, "type", None) == "text":
            trozo = getattr(bloque, "text", "")
            if trozo:
                partes.append(trozo)
    # respaldo defensivo: si por algún motivo no vino 'type' pero sí '.text'
    if not partes:
        for bloque in getattr(respuesta, "content", None) or []:
            trozo = getattr(bloque, "text", "")
            if trozo:
                partes.append(trozo)
    return "".join(partes)
