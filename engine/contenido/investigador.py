"""El reportero IA de El Pulso: investiga y VERIFICA por qué se movió una acción,
con búsqueda web real, ANTES de que la historia entre a la edición del día.

Convierte un movimiento crudo ("MRNA +170%") en un titular con contexto
verificado ("Moderna sube 170% tras un avance en su vacuna contra el cáncer").
Así el enjambre reacciona a lo que DE VERDAD movió al mercado —no solo a lo que
un feed de titulares decidió publicar— y con el porqué comprobado.

Reglas:
- Si NO puede verificar el motivo, lo dice (no lo inventa). Marco CMF: informar,
  no adivinar; jamás consejo de inversión.
- Degradación elegante: sin ANTHROPIC_API_KEY o si la búsqueda falla, usa un
  titular llano con el dato duro (el movimiento igual entra a la selección).
- Acota costo y tiempo: investiga solo los MAX_MOVERS mayores, en paralelo.
"""

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor

from contenido import vocabulario

MODELO = "claude-sonnet-5"
TIMEOUT = 40
MAX_MOVERS = 6          # cuántos movimientos investiga (techo de costo/tiempo)
HILOS = 6
# búsqueda web del lado del servidor de Anthropic (Sonnet-5). Si el nombre de la
# herramienta cambiara, la llamada falla y se cae al titular llano (sin romperse).
HERRAMIENTAS_WEB = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}]

PROMPT = (
    "Eres un reportero de mercado riguroso. Te doy una acción que se movió fuerte HOY. "
    "Busca en la web el motivo REAL y verifícalo con al menos una fuente creíble "
    "(un medio financiero, un comunicado, la propia empresa). Responde SOLO con un JSON:\n"
    '{"verificado": true|false, "titular": "…", "razon": "…", "fuente": "…"}\n'
    "- titular: en español, una línea noticiosa con el nombre, el ticker, el % y el "
    "PORQUÉ verificado. Ej: \"Moderna (MRNA) sube 170% tras un avance en su vacuna contra el cáncer\".\n"
    "- razon: una frase con el motivo confirmado.\n"
    "- fuente: el medio o URL donde lo confirmaste.\n"
    "- Si NO hallas un motivo claro y verificable, pon verificado=false y en titular "
    "SOLO el dato duro, sin inventar causa.\n"
    "NUNCA inventes el motivo. NUNCA des consejo de inversión (ni 'compra', ni 'vende', "
    "ni 'oportunidad'). Solo informas qué pasó y por qué."
)


def _extraer_json(texto: str) -> dict | None:
    if not texto:
        return None
    m = re.search(r"\{.*\}", texto, re.DOTALL)
    try:
        return json.loads(m.group(0)) if m else None
    except (ValueError, TypeError):
        return None


def _direccion(pct: float) -> str:
    return "sube" if pct >= 0 else "cae"


def _titular_llano(m: dict) -> dict:
    """El respaldo sin IA: el dato duro como titular (el movimiento igual entra)."""
    return {
        "titular": f"{m['nombre']} ({m['ticker']}) {_direccion(m['var_pct'])} "
                   f"{abs(m['var_pct'])}% en el día",
        "fuente": "movimiento de mercado", "simbolos": m["ticker"],
        "verificado": False, "razon": "",
    }


def _investigar_uno(m: dict) -> dict:
    """Investiga UN movimiento con búsqueda web. Nunca lanza: ante cualquier
    problema, devuelve el titular llano (degradación)."""
    llano = _titular_llano(m)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return llano
    dato = (f"{m['nombre']} ({m['ticker']}) {_direccion(m['var_pct'])} "
            f"{abs(m['var_pct'])}% hoy. ¿Por qué se movió?")
    try:
        import anthropic
        from llm_texto import texto_de

        cliente = anthropic.Anthropic(timeout=TIMEOUT)
        respuesta = cliente.messages.create(
            model=MODELO, max_tokens=1200, system=PROMPT,
            tools=HERRAMIENTAS_WEB,
            messages=[{"role": "user", "content": dato}],
        )
        datos = _extraer_json(texto_de(respuesta))
        titular = str((datos or {}).get("titular", "")).strip()
        # el titular DEBE pasar el filtro CMF; si no, al respaldo llano
        if not titular or not vocabulario.es_publicable(titular):
            return llano
        return {
            "titular": titular[:200],
            "fuente": str(datos.get("fuente", "") or "investigación")[:120],
            "simbolos": m["ticker"],
            "verificado": bool(datos.get("verificado")),
            "razon": str(datos.get("razon", "") or "")[:300],
        }
    except Exception:
        return llano


def investigar_movers(movers: list[dict], maximo: int = MAX_MOVERS) -> list[dict]:
    """Investiga los `maximo` mayores movimientos y los devuelve como candidatos
    listos para el portero: [{titular, fuente, simbolos, razon, verificado}, …].
    En paralelo. [] si no hay movimientos."""
    top = sorted(movers, key=lambda m: abs(m.get("var_pct", 0)), reverse=True)[:maximo]
    if not top:
        return []
    with ThreadPoolExecutor(max_workers=min(HILOS, len(top))) as ejecutor:
        resultados = list(ejecutor.map(_investigar_uno, top))
    return [r for r in resultados if r and r.get("titular")]
