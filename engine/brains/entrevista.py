"""Entrevistar a un líder — conversación EN PERSONAJE (Fase 2, efecto-wow del demo).

Clic en un líder → le preguntas "¿por qué reaccionaste así?" y responde en su
voz (su arquetipo), de forma educativa. Extiende el hover que ya existe.

CMF (obligatorio): es la opinión de un PERSONAJE de una simulación educativa,
NUNCA asesoría financiera. El personaje jamás le dice al usuario que compre,
venda o mantenga. Modelo barato (haiku) porque es a demanda y fuera del
presupuesto de la simulación. NUNCA se cae: si la API falla, responde un
fallback en personaje.
"""
import asyncio
import os

from brains.arquetipos import POR_ID
from llm_texto import texto_de

MODELO = "claude-haiku-4-5-20251001"   # barato: 1 llamada por pregunta, a demanda
TIMEOUT_SEGUNDOS = 15.0
MAX_PREGUNTA = 300        # recorta la pregunta del usuario (anti-abuso/costo)
MAX_RESPUESTA = 600       # recorta la respuesta y los turnos del historial
MAX_TURNOS = 6            # cuánto historial se reenvía (acota el costo por turno)

INSTRUCCION = (
    "Eres este personaje dentro de 'El Enjambre', una simulación educativa de "
    "mercado. Un usuario te pregunta por tu reacción a la noticia. Responde EN "
    "PERSONAJE, en primera persona, en español, breve (2 a 4 frases), fiel a tu "
    "estilo y sesgos. Explica tu RAZONAMIENTO como el personaje que eres.\n"
    "REGLAS CMF (obligatorias e inquebrantables): esto es simulación y educación, "
    "NO asesoría financiera. NUNCA le digas al usuario que compre, venda o "
    "mantenga nada, ni le des recomendaciones de inversión personales. Habla solo "
    "de TU opinión como personaje de ficción, nunca de lo que el usuario debería "
    "hacer. No inventes precios ni datos concretos. Si te piden consejo de "
    "inversión, recuérdales con tu voz que eres un personaje de una simulación."
)


def _contexto(titular: str, senal, frase_original: str) -> str:
    partes = [f"La noticia que leíste: {titular}"]
    if frase_original:
        partes.append(f'Tu reacción inicial fue: "{frase_original}"')
    if isinstance(senal, (int, float)):
        inclinacion = ("comprar" if senal > 0.1 else
                       "vender" if senal < -0.1 else "mantenerte neutral")
        partes.append(f"Tu señal fue {senal:+.2f} (te inclinaste a {inclinacion}).")
    return "\n".join(partes)


def _fallback(arquetipo_id: str) -> str:
    nombre = POR_ID.get(arquetipo_id, {}).get("nombre", "el líder")
    return (f"(Ahora mismo no puedo extenderme, pero como {nombre} te diría: mi "
            "reacción nace de mi forma de leer el mercado. Recuerda que soy un "
            "personaje de una simulación educativa, no un asesor.)")


def _mensajes(pregunta: str, historial) -> list[dict]:
    mensajes = []
    for turno in (historial or [])[-MAX_TURNOS:]:
        rol = turno.get("rol")
        texto = (turno.get("texto") or "").strip()
        if rol in ("user", "assistant") and texto:
            mensajes.append({"role": rol, "content": texto[:MAX_RESPUESTA]})
    mensajes.append({"role": "user", "content": (pregunta or "").strip()[:MAX_PREGUNTA]})
    return mensajes


async def entrevistar_async(arquetipo_id: str, titular: str, pregunta: str,
                            senal=None, frase_original: str = "",
                            historial=None) -> dict:
    """Devuelve {"respuesta": str, "fuente": "api"|"fallback", "arquetipo": id}."""
    base = {"arquetipo": arquetipo_id}
    if arquetipo_id not in POR_ID or not (pregunta or "").strip():
        return {**base, "respuesta": _fallback(arquetipo_id), "fuente": "fallback"}
    system = (f"{POR_ID[arquetipo_id]['prompt']}\n\n{INSTRUCCION}\n\n"
              f"{_contexto(titular, senal, frase_original)}")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {**base, "respuesta": _fallback(arquetipo_id), "fuente": "fallback"}
    try:
        import anthropic
        cliente = anthropic.AsyncAnthropic()
        respuesta = await asyncio.wait_for(
            cliente.messages.create(model=MODELO, max_tokens=300, system=system,
                                    messages=_mensajes(pregunta, historial)),
            timeout=TIMEOUT_SEGUNDOS,
        )
        texto = (texto_de(respuesta) or "").strip()[:MAX_RESPUESTA]
        if texto:
            return {**base, "respuesta": texto, "fuente": "api"}
    except Exception:
        pass
    return {**base, "respuesta": _fallback(arquetipo_id), "fuente": "fallback"}


def entrevistar(arquetipo_id: str, titular: str, pregunta: str, senal=None,
                frase_original: str = "", historial=None) -> dict:
    return asyncio.run(entrevistar_async(arquetipo_id, titular, pregunta,
                                         senal, frase_original, historial))
