"""Los cerebros LLM de los 100 líderes de opinión.

Cada líder hace UNA llamada a la API de Anthropic con su prompt de
personalidad + el titular, en paralelo (las 100 en < 15 segundos).
Orden de resolución por líder: caché → API → fallback léxico.
La simulación NUNCA se cae por la API.
"""

import asyncio
import hashlib
import json
import os
import re
from pathlib import Path

from brains.arquetipos import INSTRUCCION_JSON, POR_ID
from brains.fallback import respuesta_fallback

MODELO = "claude-sonnet-5"
# Nota: claude-sonnet-5 ya no acepta `temperature` (devuelve 400 si se envía).
# La variabilidad intra-arquetipo viene del propio modelo y de la semilla del caché.
MAX_CONCURRENTES = 25   # llamadas simultáneas
TIMEOUT_SEGUNDOS = 12.0
RUTA_CACHE = Path(__file__).parent / "cache" / "respuestas.json"


# ---------- caché (repetir demos no cuesta nada) ----------

def _clave_cache(titular: str, arquetipo_id: str, semilla: int) -> str:
    crudo = f"{titular}|{arquetipo_id}|{semilla}"
    return hashlib.sha256(crudo.encode()).hexdigest()[:16]


def _cargar_cache() -> dict:
    if RUTA_CACHE.exists():
        try:
            return json.loads(RUTA_CACHE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _guardar_cache(cache: dict) -> None:
    RUTA_CACHE.parent.mkdir(parents=True, exist_ok=True)
    RUTA_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------- validación del JSON del LLM ----------

def _validar_respuesta(texto: str) -> dict | None:
    """Extrae y valida el JSON de la respuesta. None si no cumple el schema."""
    encontrado = re.search(r"\{.*\}", texto, re.DOTALL)
    if not encontrado:
        return None
    try:
        datos = json.loads(encontrado.group())
    except json.JSONDecodeError:
        return None
    if not isinstance(datos.get("senal"), (int, float)):
        return None
    if not isinstance(datos.get("confianza"), (int, float)):
        return None
    if not isinstance(datos.get("frase"), str) or not datos["frase"].strip():
        return None
    return {
        "senal": max(-1.0, min(1.0, float(datos["senal"]))),
        "confianza": max(0.0, min(1.0, float(datos["confianza"]))),
        "frase": datos["frase"].strip()[:160],
    }


# ---------- llamadas a la API ----------

_primera_falla_reportada = False


def _reportar_primera_falla(error: Exception) -> None:
    """Deja UNA línea en el log con la causa real de la primera falla de API
    del proceso (clave inválida, sin saldo, timeout…). Sin esto, el fallback
    silencioso hace imposible diagnosticar en producción."""
    global _primera_falla_reportada
    if not _primera_falla_reportada:
        _primera_falla_reportada = True
        print(f"⚠️ cerebro: la API de Anthropic falló ({type(error).__name__}): {error} "
              "— los líderes usan el fallback léxico", flush=True)


async def _consultar_lider(cliente, semaforo, titular: str, arquetipo_id: str, semilla: int) -> dict:
    """Una llamada por líder. Cualquier falla degrada al fallback léxico."""
    prompt = POR_ID[arquetipo_id]["prompt"]
    async with semaforo:
        try:
            respuesta = await asyncio.wait_for(
                cliente.messages.create(
                    model=MODELO,
                    max_tokens=200,
                    system=f"{prompt}\n\n{INSTRUCCION_JSON}",
                    messages=[{"role": "user", "content": f"Titular de hoy: {titular}"}],
                ),
                timeout=TIMEOUT_SEGUNDOS,
            )
            datos = _validar_respuesta(respuesta.content[0].text)
            if datos is not None:
                datos["fuente"] = "api"
                return datos
        except Exception as error:
            # timeout, red, límite de tasa, JSON roto: hay fallback, pero la
            # PRIMERA causa queda en el log para poder diagnosticar
            _reportar_primera_falla(error)
    return respuesta_fallback(titular, arquetipo_id, semilla)


async def analizar_titular_async(titular: str, lideres: list[tuple[int, str]]) -> list[dict]:
    """lideres: lista de (semilla, arquetipo_id). Devuelve una respuesta por líder."""
    cache = _cargar_cache()
    respuestas: dict[int, dict] = {}
    pendientes: list[tuple[int, int, str]] = []  # (posición, semilla, arquetipo)

    for posicion, (semilla, arquetipo_id) in enumerate(lideres):
        clave = _clave_cache(titular, arquetipo_id, semilla)
        if clave in cache:
            respuestas[posicion] = {**cache[clave], "fuente": "cache"}
        else:
            pendientes.append((posicion, semilla, arquetipo_id))

    if pendientes:
        if os.environ.get("ANTHROPIC_API_KEY"):
            import anthropic

            cliente = anthropic.AsyncAnthropic()
            semaforo = asyncio.Semaphore(MAX_CONCURRENTES)
            tareas = [
                _consultar_lider(cliente, semaforo, titular, arq, sem)
                for (_, sem, arq) in pendientes
            ]
            resultados = await asyncio.gather(*tareas)
        else:
            # sin clave de API: todos los líderes usan el fallback léxico
            resultados = [
                respuesta_fallback(titular, arq, sem) for (_, sem, arq) in pendientes
            ]
        for (posicion, semilla, arquetipo_id), resultado in zip(pendientes, resultados):
            respuestas[posicion] = resultado
            clave = _clave_cache(titular, arquetipo_id, semilla)
            cache[clave] = {k: v for k, v in resultado.items() if k != "fuente"}
        _guardar_cache(cache)

    return [respuestas[i] for i in range(len(lideres))]


def analizar_titular(titular: str, lideres: list[tuple[int, str]]) -> list[dict]:
    """Punto de entrada síncrono: los 100 líderes leen el titular.

    lideres: lista de (semilla, arquetipo_id), una entrada por líder.
    Devuelve, en el mismo orden, dicts {senal, confianza, frase, fuente}.
    """
    return asyncio.run(analizar_titular_async(titular, lideres))
