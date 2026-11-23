"""Fase 3 · A2 — un solo LLM NEUTRAL por titular (sin arquetipos ni ABM).

Mide el escalón A2 de la ablación: ¿~110 cerebros con 8 personalidades le ganan a
UNA sola lectura neutral del titular? Si A2 ≈ A3, el reparto de arquetipos no
compra acierto direccional y es gasto evitable.

Produce un JSON {titular: senal} que `ablacion.py --a2` consume. NO decide nada por
sí solo; solo aporta el número de A2 a la escalera.

Necesita la clave de Anthropic (variable de entorno `ANTHROPIC_API_KEY`); en la
nube, el entorno la inyecta y una sesión nueva la toma. Respeta la regla cara de la
biblia (§5): a `claude-sonnet-5` NO se le manda `temperature`/`top_p`/`top_k`.
Cachea por titular: repetir una corrida no cuesta. La llamada a la API es
inyectable (`obtener`) para poder testear el resto sin red.

Uso:
    python3 engine/calibration/un_llm.py cal.con_fecha.json cal.json [salida_a2.json]
"""
import asyncio
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from brains.cerebro import MODELO, _validar_respuesta

CONCURRENCIA = 8
MAX_TOKENS = 200

# Prompt NEUTRAL: un analista sobrio, sin personalidad de arquetipo. Es el
# contraste justo contra el enjambre (que suma 8 sesgos deliberados).
SISTEMA = (
    "Eres un analista de mercados financieros sobrio, neutral y sin sesgo. "
    "Lees un titular y estimas su impacto direccional de CORTO PLAZO sobre el "
    "instrumento o mercado al que se refiere. No das consejo de inversión; solo "
    "estimas la reacción esperada del precio. Responde SOLO con JSON válido."
)
INSTRUCCION = (
    'Responde EXACTAMENTE así, sin texto extra:\n'
    '{"senal": <número en [-1,1], negativo=baja esperada, positivo=sube>, '
    '"confianza": <número en [0,1]>, "frase": "<una línea en tu voz>"}'
)


def construir_mensajes(titular: str) -> list[dict]:
    return [{"role": "user", "content": f"Titular: {titular}\n\n{INSTRUCCION}"}]


async def _llamar_api(cliente, titular: str) -> str:
    """Una llamada real a la API. Sin temperature (claude-sonnet-5 la rechaza)."""
    resp = await asyncio.wait_for(
        cliente.messages.create(
            model=MODELO, max_tokens=MAX_TOKENS, system=SISTEMA,
            messages=construir_mensajes(titular),
        ),
        timeout=30,
    )
    return resp.content[0].text


async def senales_async(titulares, obtener, concurrencia=CONCURRENCIA, cache=None):
    """{titular: senal} para cada titular nuevo (los de `cache` no se repiten).

    `obtener(titular) -> texto` es async: la API real o un doble en tests."""
    cache = dict(cache or {})
    pendientes = [t for t in dict.fromkeys(titulares) if t not in cache]
    sem = asyncio.Semaphore(concurrencia)

    async def una(t):
        async with sem:
            try:
                d = _validar_respuesta(await obtener(t))
                if d is not None:
                    cache[t] = round(max(-1.0, min(1.0, float(d["senal"]))), 4)
            except Exception:
                pass  # un titular que falla no cae la corrida; queda sin A2

    await asyncio.gather(*(una(t) for t in pendientes))
    return cache


PARSER_V = "a2-parser-1"  # súbelo si cambia cómo se parsea/recorta la respuesta


def _version_a2() -> str:
    """Huella del contrato de A2: modelo + prompt + parser. Si cambia cualquiera, el
    caché viejo NO se reutiliza (auditoría v4: no mezclar respuestas de contratos
    distintos)."""
    crudo = f"{MODELO}|{SISTEMA}|{INSTRUCCION}|{PARSER_V}"
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()[:16]


def _previo_valido(guardado, version) -> dict:
    """Las señales reutilizables del caché: solo si la versión del contrato coincide.
    Un formato viejo {titular: senal} o una versión distinta → {} (no se mezcla)."""
    if isinstance(guardado, dict) and guardado.get("_version") == version:
        return dict(guardado.get("senales", {}))
    return {}


def senales(titulares, ruta_cache):
    """Envoltura síncrona: carga el caché VERSIONADO, consulta lo que falte con la
    API real, lo guarda y devuelve {titular: senal}. Si la versión del contrato
    (modelo/prompt/parser) no coincide con la guardada, el caché viejo se ignora."""
    import anthropic
    ruta = Path(ruta_cache)
    version = _version_a2()
    previo = _previo_valido(json.loads(ruta.read_text()), version) if ruta.exists() else {}
    cliente = anthropic.AsyncAnthropic()
    nuevo = asyncio.run(senales_async(
        titulares, lambda t: _llamar_api(cliente, t), cache=previo))
    ruta.write_text(json.dumps(
        {"_version": version, "modelo": MODELO, "senales": nuevo},
        ensure_ascii=False, indent=1))
    return nuevo


def titulares_de(filas) -> list[str]:
    """Titulares únicos de las filas ya cargadas por ablacion.cargar(…, ruta_raw)."""
    return list(dict.fromkeys(f["titular"] for f in filas if f.get("titular")))


def main(con_fecha, raw, salida="a2_senales.json"):
    from calibration import ablacion
    filas = ablacion.cargar(con_fecha, raw)
    titulares = titulares_de(filas)
    print(f"{len(titulares)} titulares únicos → consultando A2 (1 LLM neutral)…")
    mapa = senales(titulares, salida)
    print(f"A2 listo: {len(mapa)} señales en {salida}")
    print(f"Ahora: python3 engine/calibration/ablacion.py {con_fecha} {raw} --a2 {salida}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "a2_senales.json")
