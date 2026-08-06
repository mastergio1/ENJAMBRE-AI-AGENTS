"""El redactor de IA de El Pulso — le pone VOZ a los hechos verificados.

La Redacción (redaccion.py) trae los hechos con su cifra y su fuente. Este
módulo toma esos hechos YA VERIFICADOS y los reescribe con la voz cálida y
con humor de El Pulso, usando el PROMPT MAESTRO (docs/prompt-maestro-pulso.md,
aprobado por Giorgio el 5 de agosto de 2026).

Dos candados que NO se cruzan:
  1. La IA solo pone voz sobre hechos verificados: los números vienen dados,
     no los toca. No puede inventar cifras.
  2. Cada texto que devuelve pasa por el filtro CMF (es_publicable) antes de
     usarse. Voz sí, asesoría/predicción no.

Degradación elegante: sin ANTHROPIC_API_KEY, o si la API/JSON fallan, devuelve
None y el boletín cae a su plantilla de siempre. El Pulso NUNCA se cae por esto.
"""

import json
import os
import re

from contenido.vocabulario import es_publicable

MODELO = "claude-sonnet-5"   # calidad de escritura; sin temperature (Sonnet-5 la rechaza)
MAX_TOKENS = 1500
TIMEOUT_SEGUNDOS = 25.0

# ---------- EL PROMPT MAESTRO (aprobado — docs/prompt-maestro-pulso.md) ----------

PROMPT_MAESTRO = """\
Eres el redactor de EL PULSO, el diario diario de El Enjambre (by Rubicón Lab):
un boletín de economía y mercado estadounidense —acciones y el S&P 500 sobre
todo— que la gente lee en su correo cada mañana. Tomas los HECHOS YA VERIFICADOS
que te entrego y los conviertes en un diario que dé gusto leer.

PARA QUIÉN ESCRIBES
Lectores curiosos: retail que quiere entender el mercado sin ser experto, y
gente de finanzas que agradece que no la aburran. Español neutro (Chile/LatAm),
sin modismos cerrados. Si usas un término técnico, lo explicas en la misma frase
con una analogía.

CÓMO ESCRIBES (tu voz)
- Cálido, como un amigo inteligente que sabe de mercados y te lo cuenta en el
  café. Cercano, nunca solemne.
- Con humor seco y una pizca de ironía sobre LOS HECHOS (nunca sobre el lector).
- Frases cortas. Ritmo. Un párrafo no supera 4-5 líneas.
- Analogías cotidianas para explicar lo complejo.
- Cero jerga sin traducir.

LO QUE NUNCA HACES — REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena):
- NUNCA recomiendas comprar, vender ni mantener. Prohibidas frases como
  "conviene", "es buen momento para", "oportunidad de compra", "deberías",
  "apunta a", "podría subir/bajar", "esperamos que".
- NUNCA predices el futuro. Solo cuentas lo que YA pasó, con su fuente.
- NUNCA das precios objetivo ni consejos de cartera.
- El Enjambre es una SIMULACIÓN EDUCATIVA de comportamiento de masas, no un
  oráculo. Su reacción es "cómo reaccionó una multitud sintética", jamás
  "lo que va a pasar".
B. Integridad de datos:
- Los NÚMEROS, TICKERS, FECHAS y CITAS vienen dados. Cópialos TEXTUALES. No los
  cambies, no agregues otros.
- Si un dato no está en lo que te di, NO lo mencionas. No rellenas huecos.
- Los titulares de prensa se citan como CONTEXTO, nunca como causa confirmada.
- No inventas fuentes ni enlaces.

EL SELLO DEL ENJAMBRE
La historia principal SIEMPRE cierra contando cómo reaccionó el enjambre a esa
noticia, con los datos de simulación que te paso. Lo narras como una escena y
recuerdas, con naturalidad, que son inversionistas simulados con IA.

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "buenos_dias": "2-3 párrafos que amarran el día (el editorial de apertura),
                  separados por \\n\\n. Sin inventar nada.",
  "historia_estrella": {
    "emoji": "un emoji que resuma el ánimo",
    "titular": "titular con gancho, en tu voz (reescrito)",
    "cuerpo": "3-4 párrafos separados por \\n\\n: qué pasó (con las cifras dadas)
               + contexto + CÓMO REACCIONÓ EL ENJAMBRE al cierre"
  },
  "historias": [{"emoji": "", "titular": "", "cuerpo": ""}]
}
Escribe SIEMPRE en español. Si los hechos vienen pobres, escribe menos: un buen
diario corto vale más que uno largo y relleno. Nunca inventes para llenar espacio."""


# ---------- armado del mensaje del día (los hechos verificados) ----------

def _mensaje_del_dia(brief: dict, enjambre: dict | None) -> str:
    """Serializa los hechos verificados para pasárselos al redactor.
    Solo hechos con cifra/fuente; el redactor no ve nada que pueda inventar."""
    lineas = ["Estos son los HECHOS VERIFICADOS de hoy. Escríbelos con tu voz,",
              "sin cambiar ningún número ni agregar datos que no estén aquí.\n"]

    mercado = brief.get("mercado") or []
    if mercado:
        lineas.append("MOVIMIENTOS Y EVENTOS DEL DÍA:")
        for m in mercado:
            if m.get("tipo") == "evento":
                lineas.append(f'- Evento: «{m.get("titular","")}»'
                              + (f' (fuente: {m["fuente"]})' if m.get("fuente") else ""))
            else:
                lineas.append(f'- {m.get("nombre","")}: {m.get("variacion_pct")}%'
                              + (f' — en la prensa: «{m["cita_titular"]}»' if m.get("cita_titular") else ""))

    observa = brief.get("observa") or []
    if observa:
        lineas.append("\nLO QUE EL ENJAMBRE MIRA HOY (atención, no predicción):")
        lineas += [f"- {t}" for t in observa]

    if enjambre:
        lineas.append("\nPARA LA HISTORIA ESTRELLA — así reaccionó el enjambre:")
        lineas.append(f'- Noticia: «{enjambre.get("titular","")}»')
        if enjambre.get("direccion_pct") is not None:
            lineas.append(f'- El precio simulado del enjambre se movió {enjambre["direccion_pct"]}%')
        if enjambre.get("volatilidad"):
            lineas.append(f'- Agitación de la manada: {enjambre["volatilidad"]}')
        if enjambre.get("arquetipos"):
            lineas.append(f'- Arquetipos que más reaccionaron: {enjambre["arquetipos"]}')

    return "\n".join(lineas)


# ---------- filtro CMF sobre lo que devuelve la IA ----------

def _cmf(texto: str) -> str | None:
    """Devuelve el texto si pasa el filtro CMF; None si no (para descartarlo).
    Se evalúa párrafo por párrafo: si un párrafo cruza la línea, se cae solo
    ese, no la historia entera."""
    if not isinstance(texto, str) or not texto.strip():
        return None
    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    limpios = [p for p in parrafos if es_publicable(p)]
    return "\n\n".join(limpios) if limpios else None


def _sanear_historia(h: dict) -> dict | None:
    cuerpo = _cmf(h.get("cuerpo", ""))
    titular = h.get("titular", "").strip()
    if not cuerpo or not titular or not es_publicable(titular):
        return None
    return {"emoji": (h.get("emoji") or "").strip()[:4],
            "titular": titular[:140], "cuerpo": cuerpo}


def _validar(datos: dict) -> dict | None:
    """Valida la forma del JSON y pasa TODO por el filtro CMF."""
    if not isinstance(datos, dict):
        return None
    buenos = _cmf(datos.get("buenos_dias", ""))
    estrella = datos.get("historia_estrella")
    estrella = _sanear_historia(estrella) if isinstance(estrella, dict) else None
    historias = [s for s in (_sanear_historia(h) for h in (datos.get("historias") or [])
                             if isinstance(h, dict)) if s]
    if not buenos and not estrella:
        return None  # sin apertura ni estrella, no hay diario que valga
    return {"buenos_dias": buenos, "historia_estrella": estrella, "historias": historias[:2]}


def _extraer_json(texto: str) -> dict | None:
    encontrado = re.search(r"\{.*\}", texto, re.DOTALL)
    if not encontrado:
        return None
    try:
        return json.loads(encontrado.group())
    except json.JSONDecodeError:
        return None


# ---------- punto de entrada ----------

def redactar(brief: dict, enjambre: dict | None = None) -> dict | None:
    """Reescribe el brief del día con la voz de El Pulso. Devuelve el dict
    {buenos_dias, historia_estrella, historias} o None si no se puede (sin
    clave, API caída, JSON roto, todo filtrado por CMF) — el boletín cae a
    su plantilla. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    if not brief or not (brief.get("mercado") or enjambre):
        return None  # sin hechos, no hay nada que redactar
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_MAESTRO,
            messages=[{"role": "user", "content": _mensaje_del_dia(brief, enjambre)}],
        )
        datos = _extraer_json(respuesta.content[0].text)
        return _validar(datos) if datos else None
    except Exception:
        return None  # cualquier falla → fallback a plantilla
