"""El portero — guardián del presupuesto LLM (CONTENIDO.md sección 7).

Dos pisos:
1. Léxico (gratis): descarta duplicados, contenido promocional y todo lo
   que no tiene contenido de mercado. Elimina ~80% sin gastar un centavo.
2. Haiku (centavos): una llamada con lote de hasta 20 titulares que
   puntúa impacto 1-10. Sin API key, un heurístico léxico decide igual —
   el pipeline nunca se cae.

Todo veredicto (incluso descartes) queda en la tabla `titulares`:
ese log es el material para calibrar el portero después.
"""

import difflib
import json
import os
import re

from contenido import persistencia

MODELO_PORTERO = "claude-haiku-4-5-20251001"
LOTE_MAXIMO = 20
UMBRAL_DUPLICADO = 0.85
UMBRAL_IMPACTO = 5  # bajo esto, el heurístico descarta

# --- señales de que el titular SÍ habla de mercados (ES + EN: Alpaca llega en inglés) ---
SENALES_MERCADO = [
    # macro
    "fed", "banco central", "central bank", "tasas", "rates", "inflación", "inflation",
    "empleo", "jobs", "unemployment", "pib", "gdp", "dólar", "dollar", "recesión",
    "recession", "tariff", "arancel", "treasury", "bonos", "bonds", "liquidez",
    # mercado / empresa
    "acciones", "stocks", "shares", "bolsa", "market", "índice", "index", "s&p",
    "nasdaq", "dow", "ipsa", "earnings", "resultados", "ganancias", "revenue",
    "ingresos", "quiebra", "bankruptcy", "fusión", "merger", "adquisición",
    "acquisition", "ipo", "dividendo", "dividend", "ceo", "regulador", "sec",
    "banco", "bank", "cripto", "crypto", "bitcoin", "petróleo", "oil",
]

# --- patrones de contenido sin sustancia (listas, promoción, opinión blanda) ---
PATRONES_DESCARTE = [
    r"^\d+\s+(stocks|acciones|razones|reasons|things|ways)",
    r"\btop\s+\d+\b",
    r"(best|mejores)\s+(stocks|acciones|etfs?)",
    r"(should you|deberías)\b",
    r"(how to|cómo)\s+(invest|invertir|trade)",
    r"\b(webinar|sponsored|patrocinado|newsletter|podcast|giveaway)\b",
    r"(what to watch|qué mirar|cheat sheet|preview of the week)",
    r"\b(motley fool|zacks)\b",
]


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.lower().strip())


def _es_duplicado(titular: str, previos: list[str]) -> bool:
    objetivo = _normalizar(titular)
    for previo in previos:
        similitud = difflib.SequenceMatcher(None, objetivo, _normalizar(previo)).ratio()
        if similitud > UMBRAL_DUPLICADO:
            return True
    return False


# ---------- piso 1: léxico (gratis) ----------

def evaluar_lexico(titular: str, previos: list[str], simbolos: str = "") -> str | None:
    """Devuelve el motivo del descarte, o None si pasa al piso 2."""
    if _es_duplicado(titular, previos):
        return "duplicado de un titular reciente"
    texto = _normalizar(titular)
    for patron in PATRONES_DESCARTE:
        if re.search(patron, texto):
            return "contenido promocional o lista sin sustancia"
    # si la fuente asoció tickers, ES contenido de mercado por definición
    tiene_simbolos = bool(simbolos.strip())
    if not tiene_simbolos and not any(senal in texto for senal in SENALES_MERCADO):
        return "sin contenido de mercado reconocible"
    return None


# ---------- piso 2: Haiku (o heurístico si no hay API) ----------

PROMPT_PORTERO = """Eres el editor de un simulador educativo de mercados.
Evalúa el IMPACTO DE MERCADO de cada titular (1-10):
- afecta a un índice o sector completo > empresa mega-cap > empresa puntual
- macro (tasas, inflación, empleo, geopolítica) puntúa alto
- rumores y opiniones puntúan bajo, salvo fuente institucional
Responde SOLO un array JSON, un objeto por titular, mismo orden:
[{"veredicto": "simular"|"descartar", "impacto": 1-10, "motivo": "una frase en español"}]"""


def _evaluar_lote_llm(titulares: list[str]) -> list[dict] | None:
    """Una llamada Haiku por lote. None si no hay API o algo falla."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic

        cliente = anthropic.Anthropic()
        lista = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(titulares))
        respuesta = cliente.messages.create(
            model=MODELO_PORTERO,
            max_tokens=1500,
            system=PROMPT_PORTERO,
            messages=[{"role": "user", "content": lista}],
        )
        encontrado = re.search(r"\[.*\]", respuesta.content[0].text, re.DOTALL)
        datos = json.loads(encontrado.group())
        if len(datos) != len(titulares):
            return None
        return [
            {
                "veredicto": "simular" if d.get("veredicto") == "simular" else "descartar",
                "impacto": max(1, min(10, int(d.get("impacto", 1)))),
                "motivo": str(d.get("motivo", ""))[:200],
            }
            for d in datos
        ]
    except Exception:
        return None  # el heurístico decide; el pipeline no se cae


# vocabulario del heurístico (ES + EN): mismo criterio que el prompt Haiku
_MACRO_FUERTE = [
    "fed", "central bank", "banco central", "rates", "tasas", "inflación",
    "inflation", "unemployment", "desempleo", "jobs report", "empleo",
    "tariff", "arancel", "treasury", "gdp", "pib", "ecb", "recession", "recesión",
]
_EVENTO_FUERTE = [
    "collapse", "colapso", "quiebra", "bankruptcy", "default", "crash",
    "desploma", "crisis", "fdic", "bailout", "rescate", "cyberattack",
    "ciberataque", "all-time high", "máximo histórico", "surge", "spike",
    "plunge", "jumps", "record", "récord", "resigns", "renuncia", "recall",
    "investigation", "investigación", "fraud", "fraude", "war", "guerra",
    "acquire", "adquisición", "merger", "fusión", "fda approval", "beats",
    "misses", "escalate",
]


def _evaluar_heuristico(titular: str, simbolos: str = "") -> dict:
    """Plan B sin API: puntúa con el mismo criterio del prompt del portero."""
    texto = _normalizar(titular)
    impacto = 2
    if any(p in texto for p in _MACRO_FUERTE):
        impacto += 3  # macro puntúa alto
    aciertos = sum(1 for p in _EVENTO_FUERTE if p in texto)
    impacto += min(2 * aciertos, 4)
    if len([s for s in simbolos.split(",") if s]) >= 2:
        impacto += 1  # varios tickers: afecta más que a una empresa puntual
    impacto = max(1, min(10, impacto))
    veredicto = "simular" if impacto >= UMBRAL_IMPACTO else "descartar"
    return {"veredicto": veredicto, "impacto": impacto,
            "motivo": f"heurístico léxico (impacto {impacto}/10, sin API)"}


def evaluar_lote(candidatos: list[dict]) -> list[dict]:
    """Evalúa hasta LOTE_MAXIMO candidatos por llamada; degrada a heurístico."""
    resultados: list[dict] = []
    for inicio in range(0, len(candidatos), LOTE_MAXIMO):
        lote = candidatos[inicio:inicio + LOTE_MAXIMO]
        evaluados = _evaluar_lote_llm([c["titular"] for c in lote])
        if evaluados is None:
            evaluados = [_evaluar_heuristico(c["titular"], c.get("simbolos", "")) for c in lote]
        resultados.extend(evaluados)
    return resultados


# ---------- el proceso completo de un día ----------

def procesar_dia(conexion, candidatos: list[dict], maximo: int = 3) -> dict:
    """Evalúa los titulares del día y elige los `maximo` de mayor impacto.

    candidatos: [{"titular": ..., "fuente": ..., "simbolos": ...}, ...]
    Registra TODO veredicto en la tabla `titulares`. Devuelve
    {"elegidos": [...], "log": [...]} con los motivos de cada decisión.
    """
    previos = [t["titular"] for t in persistencia.titulares_recientes(conexion, horas=48)]
    log: list[dict] = []
    al_piso_dos: list[dict] = []

    for candidato in candidatos:
        titular = candidato["titular"].strip()
        motivo_lexico = evaluar_lexico(titular, previos, candidato.get("simbolos", ""))
        if motivo_lexico is not None:
            log.append({**candidato, "veredicto": "descartar", "impacto": 0,
                        "motivo": f"piso léxico: {motivo_lexico}"})
        else:
            al_piso_dos.append(candidato)
        previos.append(titular)  # los del propio lote también cuentan como "vistos"

    evaluaciones = evaluar_lote(al_piso_dos)
    for candidato, evaluacion in zip(al_piso_dos, evaluaciones):
        log.append({**candidato, **evaluacion})

    # los `maximo` de mayor impacto entre los que dijeron "simular";
    # en empate gana el más reciente (los candidatos llegan ordenados así)
    simulables = [e for e in log if e["veredicto"] == "simular"]
    simulables.sort(key=lambda e: -e["impacto"])
    elegidos = simulables[:maximo]
    ids_elegidos = {id(e) for e in elegidos}

    for entrada in log:
        veredicto_final = "simular" if id(entrada) in ids_elegidos else "descartar"
        if entrada["veredicto"] == "simular" and veredicto_final == "descartar":
            entrada["motivo"] += " (simulable, pero fuera del top del día)"
        entrada["veredicto"] = veredicto_final
        persistencia.registrar_titular(
            conexion,
            titular=entrada["titular"],
            fuente=entrada.get("fuente", "desconocida"),
            simbolos=entrada.get("simbolos", ""),
            veredicto=entrada["veredicto"],
            motivo=entrada["motivo"],
            impacto=entrada["impacto"],
        )

    return {"elegidos": elegidos, "log": log}
