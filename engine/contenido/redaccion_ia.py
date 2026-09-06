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
from datetime import datetime, timezone

from brains.arquetipos import ARQUETIPOS, POR_ID
from contenido.vocabulario import es_publicable
from llm_texto import texto_de

# los lectores viven en Chile/LatAm; el saludo se calcula en hora local de
# Chile (zoneinfo maneja el horario de verano solo). Si no está la zona
# (entornos mínimos), cae a UTC sin romperse.
ZONA_LECTOR = "America/Santiago"
_DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
_MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _ahora_local(ahora: datetime | None = None) -> datetime:
    base = ahora or datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        return base.astimezone(ZoneInfo(ZONA_LECTOR))
    except Exception:
        return base  # sin tzdata: el UTC sirve igual para el momento del día


def _momento(hora: int) -> str:
    if hora < 6:
        return "madrugada"
    if hora < 12:
        return "mañana"
    if hora < 20:
        return "tarde"
    return "noche"


def contexto_temporal(ahora: datetime | None = None) -> dict:
    """Qué día es, la fecha y el momento — para que el redactor NO los invente."""
    t = _ahora_local(ahora)
    return {
        "dia_semana": _DIAS[t.weekday()],
        "weekday": t.weekday(),                 # 0=lunes … 5=sábado, 6=domingo
        "fecha": f"{t.day} de {_MESES[t.month - 1]} de {t.year}",
        "momento": _momento(t.hour),
        "es_finde": t.weekday() >= 5,
    }

MODELO = "claude-sonnet-5"   # calidad de escritura; sin temperature (Sonnet-5 la rechaza)
MAX_TOKENS = 8000            # análisis extenso (deep-dive con debate + números):
                             # holgura para que el JSON NUNCA se corte a medias
TIMEOUT_SEGUNDOS = 90.0      # corre en el ritual de fondo, no en un request web

# ---------- EL PROMPT MAESTRO (rediseño estilo diario, 14-ago-2026) ----------

PROMPT_MAESTRO = """\
Eres el redactor jefe de EL PULSO, un DIARIO DE MERCADO (by Rubicón Lab) que la
gente lee en su correo cada mañana. Tu trabajo NO es reenviar titulares: es
tomar los HECHOS YA VERIFICADOS que te entrego y convertir cada uno en una
HISTORIA con análisis de verdad. Piensa en un boletín como "Morning Brew" o
"Moby": ameno, agudo, con opinión sobre los hechos, que enseña mientras entretiene.

PARA QUIÉN ESCRIBES
Lectores curiosos: retail que quiere entender el mercado sin ser experto, y
gente de finanzas que agradece que no la aburran. Español neutro (Chile/LatAm).
Si usas un término técnico, lo explicas en la misma frase con una analogía.

CÓMO ESCRIBES (tu voz)
- Cálido y filoso, como un amigo brillante que sabe de mercados y te lo cuenta
  en el café. Cercano, nunca solemne.
- Con humor seco e ironía sobre LOS HECHOS (jamás sobre el lector).
- Frases cortas, ritmo. Analogías cotidianas para lo complejo.
- EXTENSO donde importa: cada historia son 3 a 5 párrafos de análisis real, no
  un resumen. Desarrolla la idea; no te quedes en el titular.

LA ESTRUCTURA DE CADA HISTORIA (síguela)
1. QUÉ PASÓ — el hecho con su cifra (la que te doy).
2. POR QUÉ IMPORTA — la tesis: qué significa de verdad, más allá del dato.
3. LA CONEXIÓN — el hilo con lo macro (tasas, petróleo, la Fed, la industria) o
   con la narrativa del momento. Aquí está el valor: conectas puntos.
4. Cierras con un "bottom_line": una frase que remata la idea.

CÓMO ELIGES LAS HISTORIAS (curaduría por ATENCIÓN, no por tamaño)
De los candidatos que te doy, elige las 3-4 que MÁS llamen la atención. Criterios:
- Una movida fuerte (un porcentaje grande, sobre todo en algo chico).
- Un catalizador o aprobación (FDA, un regulador, un contrato, un acuerdo).
- La narrativa que domina el mercado esta semana/mes.
NO te limites a las empresas gigantes: una small-cap que se disparó por una
aprobación, una cripto o una materia prima valen MÁS que otra mega-cap más.
Busca variedad de activos.

EL GRÁFICO DE CADA HISTORIA
Cada historia lleva un gráfico de precio real. Para eso, en "grafico" pon el
TICKER que te doy junto a ese activo (cópialo textual, NO inventes tickers) y su
nombre. Elige "periodo": "dia" si la movida fue de hoy/una aprobación reciente,
"semana" por defecto, "mes" si es una narrativa de fondo. "moneda" suele ser "$".
Si una historia no tiene un ticker claro entre los datos, deja "grafico": null.

LO QUE NUNCA HACES — REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena) — ESTA ES TU LÍNEA Y TU DEFENSA:
- NUNCA recomiendas comprar, vender ni mantener. Prohibidas: "conviene",
  "es buen momento", "oportunidad de compra", "deberías", "apunta a",
  "podría subir/bajar", "esperamos que", "precio objetivo".
- NUNCA predices el futuro. Cuentas lo que YA pasó. Cuando mires hacia adelante,
  es "qué observar / qué está en juego", nunca "qué va a pasar".
- Análisis profundo SÍ; recomendación de inversión JAMÁS. Puedes explicar por
  qué algo importa sin decirle a nadie qué hacer con su plata.
B. Integridad de datos:
- Los NÚMEROS, TICKERS, FECHAS y CITAS vienen dados. Cópialos TEXTUALES.
- Si un dato no está en lo que te di, NO lo mencionas. No rellenas huecos.
- Los titulares de prensa se citan como CONTEXTO, nunca como causa confirmada.
- No inventas fuentes, enlaces ni cifras.

EL DÍA DE HOY (te lo doy yo — NO lo inventes)
Te digo el día, la fecha y el momento. Saluda acorde ("Buenos días" en la mañana,
etc.), menciona la fecha que te doy, nunca inventes otra. Si es fin de semana o
feriado sin sesión, escribe una edición de repaso, sin inventar movimientos.

NO menciones "el enjambre" ni simulaciones en las historias: El Pulso es un diario
de mercado serio. (El Enjambre se promociona aparte, al pie del correo.)

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "buenos_dias": "2-3 párrafos de apertura que amarran el día, separados por \\n\\n.",
  "historias": [
    {
      "kicker": "etiqueta corta de categoría, ej: 'Tecnología · catalizador',
                 'Small-cap · movida del día', 'Narrativa del mes · cripto',
                 'Macro · materias primas'",
      "emoji": "un emoji que resuma la historia",
      "titular": "titular con gancho, reescrito en tu voz",
      "dek": "una bajada de una línea (subtítulo)",
      "cuerpo": "3 a 5 párrafos separados por \\n\\n: qué pasó + por qué importa + la conexión",
      "bottom_line": "una frase de cierre (sin escribir 'En una línea:', solo la frase)",
      "grafico": {"ticker": "AAPL", "nombre": "Apple Inc.", "periodo": "semana", "moneda": "$"}
    }
  ]
}
Devuelve 3-4 historias. Escribe SIEMPRE en español. Prioriza calidad y profundidad
sobre cantidad, pero cada historia elegida va DESARROLLADA, no en dos frases."""


# ---------- armado del mensaje del día (los hechos verificados) ----------

def _mensaje_del_dia(brief: dict, enjambre: dict | None = None, cuando: dict | None = None) -> str:
    """Serializa los hechos verificados para el redactor: los CANDIDATOS del día
    (movidas con su ticker + cifra + cita) para que elija y desarrolle 3-4.
    Solo hechos verificados; el redactor no ve nada que pueda inventar."""
    cuando = cuando or contexto_temporal()
    finde = " (FIN DE SEMANA: sin sesión de mercado)" if cuando.get("es_finde") else ""
    lineas = [
        f'HOY es {cuando["dia_semana"]} {cuando["fecha"]}, es de {cuando["momento"]}{finde}.',
        "Saluda según el momento y usa esta fecha; NO inventes otra.\n",
    ]

    foto = brief.get("foto") or []
    if foto:
        lineas.append("EL TELÓN DE FONDO (índices y materias primas, para contexto):")
        for f in foto:
            lineas.append(f'- {f.get("nombre","")}: día {f.get("variacion_pct")}%, '
                          f'mes {f.get("var_mes_pct")}%, año {f.get("var_ano_pct")}%')
        lineas.append("")

    mercado = brief.get("mercado") or []
    movers = [m for m in mercado if m.get("tipo") != "evento"]
    eventos = [m for m in mercado if m.get("tipo") == "evento"]

    if movers:
        lineas.append("CANDIDATOS A HISTORIA — movidas verificadas (elige las que MÁS "
                      "llamen la atención; usa el [TICKER] para el gráfico de cada una):")
        for m in movers:
            tk = m.get("simbolo", "") or "?"
            linea = f'- [{tk}] {m.get("nombre","")}: {m.get("variacion_pct")}%'
            if m.get("cita_titular"):
                linea += f' — en la prensa: «{m["cita_titular"]}»'
            if m.get("fuente"):
                linea += f' (fuente: {m["fuente"]})'
            lineas.append(linea)
        lineas.append("")

    if eventos:
        lineas.append("EVENTOS DEL DÍA (noticias sin un movimiento de precio directo — "
                      "úsalas como historia o como contexto):")
        for e in eventos:
            lineas.append(f'- «{e.get("titular","")}»'
                          + (f' (fuente: {e["fuente"]})' if e.get("fuente") else ""))
        lineas.append("")

    observa = brief.get("observa") or []
    if observa:
        lineas.append("OTROS TITULARES EN EL RADAR (contexto extra, no obligatorio):")
        lineas += [f"- {t}" for t in observa]

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


def _grafico_valido(g) -> dict | None:
    """Valida la especificación del gráfico: un ticker limpio (sin inyección) y
    los campos de presentación. None si no hay ticker usable."""
    if not isinstance(g, dict):
        return None
    t = str(g.get("ticker", "")).strip()
    if not t or len(t) > 15 or not all(c.isalnum() or c in ".=^-" for c in t):
        return None
    periodo = str(g.get("periodo", "semana")).strip().lower()
    if periodo not in ("semana", "mes", "ano", "dia"):
        periodo = "semana"
    return {"ticker": t, "nombre": str(g.get("nombre", "") or t)[:60],
            "periodo": periodo, "moneda": (str(g.get("moneda", "$")).strip()[:2] or "$")}


def _texto_cmf(t) -> str:
    """Un texto de una línea: se conserva solo si pasa el filtro CMF."""
    t = str(t or "").strip()
    return t if t and es_publicable(t) else ""


def _sanear_historia(h: dict) -> dict | None:
    """Una historia con su estructura nueva; None si no tiene lo mínimo
    (titular + cuerpo publicables)."""
    if not isinstance(h, dict):
        return None
    titular = str(h.get("titular", "")).strip()
    cuerpo = _cmf(h.get("cuerpo", ""))
    if not cuerpo or not titular or not es_publicable(titular):
        return None
    return {
        "kicker": _texto_cmf(h.get("kicker"))[:60],
        "emoji": str(h.get("emoji", "") or "").strip()[:4],
        "titular": titular[:160],
        "dek": _texto_cmf(h.get("dek"))[:200],
        "cuerpo": cuerpo,
        "bottom_line": _texto_cmf(h.get("bottom_line"))[:280],
        "grafico": _grafico_valido(h.get("grafico")),
    }


def _validar(datos: dict) -> dict | None:
    """Valida la forma del JSON y pasa TODO por el filtro CMF."""
    if not isinstance(datos, dict):
        return None
    buenos = _cmf(datos.get("buenos_dias", ""))
    historias = [s for s in (_sanear_historia(h) for h in (datos.get("historias") or [])
                             if isinstance(h, dict)) if s]
    if not historias and not buenos:
        return None  # sin historias ni apertura, no hay diario que valga
    return {"buenos_dias": buenos, "historias": historias[:4]}


def _extraer_json(texto: str) -> dict | None:
    encontrado = re.search(r"\{.*\}", texto, re.DOTALL)
    if not encontrado:
        return None
    try:
        return json.loads(encontrado.group())
    except json.JSONDecodeError:
        return None


# ---------- punto de entrada ----------

def redactar(brief: dict, enjambre: dict | None = None, cuando: dict | None = None) -> dict | None:
    """Reescribe el brief del día como diario: {buenos_dias, historias[]}. None
    si no se puede (sin clave, API caída, JSON roto, todo filtrado por CMF) — el
    boletín cae a su respaldo. `enjambre` se mantiene por compatibilidad de firma
    pero ya no se usa (las historias son de las noticias, no del enjambre).
    `cuando` se calcula solo si no se pasa. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    if not brief or not (brief.get("mercado") or brief.get("observa")):
        return None  # sin hechos, no hay nada que redactar
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_MAESTRO,
            messages=[{"role": "user", "content": _mensaje_del_dia(brief, cuando=cuando)}],
        )
        datos = _extraer_json(texto_de(respuesta))
        return _validar(datos) if datos else None
    except Exception:
        return None  # cualquier falla → fallback a plantilla


# ══════════════════════════════════════════════════════════════════════════
#  LA EDICIÓN DE LA TARDE — 'el cierre del mercado' (Premium) CON VOZ
# ══════════════════════════════════════════════════════════════════════════
# El investigador (investigador.py) ya cazó y VERIFICÓ los mayores movimientos
# del día con su porqué. Aquí les ponemos ENCIMA la voz Moby: en vez de una lista
# plana ("FRVO sube 28%"), los 3 protagonistas se vuelven mini-historias con
# tono cálido-filoso, igual que la edición de la mañana. Voz sobre hechos ya
# verificados: los números, tickers y el motivo vienen dados; la IA no los toca.

PROMPT_CIERRE = """\
Eres el redactor jefe de EL PULSO (by Rubicón Lab). Esta es la EDICIÓN DE LA
TARDE: 'el cierre del mercado', el premio de los suscriptores Premium. Cerró la
bolsa de EE.UU. y te entrego los MAYORES movimientos del día, YA investigados y
VERIFICADOS por nuestro reportero (cada uno con su cifra y su motivo confirmado).
Tu trabajo: convertir los 3 que MÁS llamen la atención en mini-historias con
voz, no en una lista plana de porcentajes.

TU VOZ (la de siempre, la "Moby")
- Cálido y filoso, como un amigo brillante que sabe de mercados y te lo cuenta en
  el café al cierre del día. Cercano, nunca solemne.
- Humor seco e ironía sobre LOS HECHOS (jamás sobre el lector).
- Frases cortas, ritmo. Analogías cotidianas para lo complejo. Si usas un término
  técnico, lo explicas en la misma frase.

CADA MINI-HISTORIA (2 a 3 párrafos, desarrollada)
1. QUÉ PASÓ — el movimiento con su cifra (la que te doy) y el motivo verificado.
2. POR QUÉ IMPORTA — la tesis: qué significa de verdad, más allá del salto de precio.
3. LA CONEXIÓN — el hilo con lo macro (tasas, la Fed, el sector, la narrativa del
   momento). Aquí está el valor: conectas puntos.
Cierra con un "bottom_line": una frase que remata.

REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena): NUNCA recomiendas comprar, vender ni mantener.
   Prohibidas: "conviene", "oportunidad", "deberías", "podría subir/bajar",
   "precio objetivo", "es buen momento". NUNCA predices el futuro: cuentas lo que
   YA pasó; hacia adelante es "qué observar", nunca "qué va a pasar".
B. Integridad: los NÚMEROS, TICKERS y el MOTIVO vienen dados. Cópialos TEXTUALES.
   Si algo no está en lo que te di, NO lo inventas. Si un movimiento vino marcado
   como SIN motivo verificado, cuéntalo así ("subió con fuerza; el mercado aún no
   fija una causa clara") — jamás inventes la razón.

EL GRÁFICO: en "grafico" pon el TICKER que te doy junto a ese activo (textual, NO
inventes) y su nombre. "periodo": "dia". "moneda": "$".

NO menciones "el enjambre" ni simulaciones: El Pulso es un diario de mercado serio.

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "buenas_tardes": "1-2 párrafos de apertura que amarran el cierre del día, separados por \\n\\n.",
  "historias": [
    {
      "kicker": "etiqueta corta, ej: 'Energía · movida del día', 'Small-cap · catalizador'",
      "emoji": "un emoji que resuma la historia",
      "titular": "titular con gancho, en tu voz",
      "dek": "una bajada de una línea",
      "cuerpo": "2 a 3 párrafos separados por \\n\\n: qué pasó + por qué importa + la conexión",
      "bottom_line": "una frase de cierre (sin escribir 'En una línea:', solo la frase)",
      "grafico": {"ticker": "FRVO", "nombre": "Fervo Energy", "periodo": "dia", "moneda": "$"}
    }
  ]
}
Devuelve las 3 historias más llamativas. Escribe SIEMPRE en español. Cada una
DESARROLLADA, no en dos frases."""


def _mensaje_cierre(datos: dict, cuando: dict | None = None) -> str:
    """Serializa los movimientos YA verificados para el redactor del cierre."""
    cuando = cuando or contexto_temporal()
    movers = [m for m in (datos.get("movers") or []) if isinstance(m, dict)]
    lineas = [
        f'HOY es {cuando["dia_semana"]} {cuando["fecha"]}. Es la EDICIÓN DE LA '
        f'TARDE, tras el cierre del mercado de EE.UU. Saluda con "Buenas tardes" '
        f'y usa esta fecha; NO inventes otra.\n',
        "LOS PROTAGONISTAS DEL CIERRE — movimientos verificados (elige los 3 que "
        "MÁS llamen la atención y desarróllalos; usa el [TICKER] para el gráfico):",
    ]
    for m in movers:
        tk = str(m.get("simbolos", "") or "?").split(",")[0].strip() or "?"
        pct = m.get("var_pct")
        signo = "sube" if (pct or 0) >= 0 else "cae"
        linea = f'- [{tk}] {m.get("titular","")}'
        if pct is not None:
            linea += f' — dato: {signo} {abs(pct)}%'
        razon = str(m.get("razon", "") or "").strip()
        if m.get("verificado") and razon:
            linea += f'. Motivo verificado: «{razon}»'
        else:
            linea += ". SIN motivo verificado (no inventes la causa)."
        if m.get("fuente"):
            linea += f' (fuente: {m["fuente"]})'
        lineas.append(linea)
    return "\n".join(lineas)


def _validar_cierre(datos: dict, fuente_movers: list[dict]) -> dict | None:
    """Valida la forma del JSON del cierre y pasa TODO por el filtro CMF. Ata a
    cada historia el % real del movimiento (la píldora) casando su ticker con el
    del movimiento de origen. None si no quedó ni apertura ni historia."""
    if not isinstance(datos, dict):
        return None
    apertura = _cmf(datos.get("buenas_tardes", ""))
    historias = [s for s in (_sanear_historia(h) for h in (datos.get("historias") or [])
                             if isinstance(h, dict)) if s]
    if not historias and not apertura:
        return None
    # píldora del %: casa el ticker del gráfico con el movimiento de origen
    por_ticker = {}
    for m in fuente_movers:
        tk = str(m.get("simbolos", "") or "").split(",")[0].strip().upper()
        if tk:
            por_ticker[tk] = m
    for h in historias:
        g = h.get("grafico") or {}
        origen = por_ticker.get(str(g.get("ticker", "")).strip().upper())
        if origen:
            h["var_pct"] = origen.get("var_pct")
            h["sesion"] = origen.get("sesion")
    return {"buenas_tardes": apertura, "historias": historias[:3]}


def redactar_cierre(datos: dict, cuando: dict | None = None) -> dict | None:
    """Le pone VOZ Moby al cierre del día: toma los movimientos verificados por el
    investigador y devuelve {buenas_tardes, historias[]}. None si no se puede
    (sin clave, API caída, JSON roto, todo filtrado por CMF) — el boletín cae a la
    lista llana de siempre. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    movers = [m for m in (datos.get("movers") or []) if isinstance(m, dict)]
    if not movers:
        return None
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_CIERRE,
            messages=[{"role": "user", "content": _mensaje_cierre(datos, cuando=cuando)}],
        )
        parseado = _extraer_json(texto_de(respuesta))
        return _validar_cierre(parseado, movers) if parseado else None
    except Exception:
        return None  # cualquier falla → fallback a la lista llana


# ══════════════════════════════════════════════════════════════════════════
#  LA EDICIÓN DE FIN DE SEMANA — el deep-dive de una mid-cap o un sector
# ══════════════════════════════════════════════════════════════════════════
# Formato distinto al diario: CONTEXTO primero (qué ES), luego el DEBATE de
# arquetipos (miradas contrastantes = "lo que nuestros inversionistas IA están
# viendo o analizando"). NUNCA consejo de inversión. Ver analisis_semanal.py.

# roster compacto de arquetipos para el prompt (id → nombre + una línea de perfil)
def _roster_arquetipos() -> str:
    lineas = []
    for a in ARQUETIPOS:
        # una línea de esencia por arquetipo (la primera frase de su prompt)
        esencia = a["prompt"].split(".")[0].strip()
        lineas.append(f'- {a["id"]} ({a["nombre"]}): {esencia}.')
    return "\n".join(lineas)


PROMPT_ANALISIS = """\
Eres el redactor jefe de EL PULSO (by Rubicón Lab). Es FIN DE SEMANA: el mercado
está cerrado y toca la lectura pausada. Hoy NO cuentas las noticias del día:
haces UN análisis a fondo de un solo protagonista —una empresa de mediana
capitalización o un sector— que te entrego ya elegido, con su contexto y su
cifra verificada.

EL ENCUADRE QUE MANDA (léelo dos veces)
Esto NO es consejo de inversión. Es "lo que nuestros inversionistas IA están
VIENDO y ANALIZANDO". Tú no le dices a nadie qué hacer con su plata: describes
qué es el protagonista, por qué llamó la atención, y cómo lo miran perfiles de
inversionista MUY distintos entre sí. El valor está en el CONTRASTE de miradas,
no en una conclusión única.

CÓMO ESCRIBES (tu voz)
- Cálido, agudo, cercano; con humor seco sobre los hechos, nunca sobre el lector.
- Español neutro (Chile/LatAm). Si usas un término técnico, lo explicas ahí mismo
  con una analogía cotidiana.
- Extenso donde importa: párrafos de análisis real, no un resumen.

LA ESTRUCTURA (síguela en este orden — es un análisis de analista, no un tuit)
1. CONTEXTO PRIMERO — QUÉ ES el protagonista. Antes de opinar nada, explícale al
   lector a qué se dedica la empresa/sector, cómo gana dinero, qué lo hace
   particular. Apóyate en el contexto factual que te doy; no inventes datos.
   Desarróllalo: 2-3 párrafos.
2. LA LECTURA — POR QUÉ está en la mira esta semana: la movida de precio (la
   cifra que te doy) y la narrativa alrededor. Qué historia se está contando.
3. LOS NÚMEROS — la lectura financiera, como la haría un analista. Con los DATOS
   VERIFICADOS que te doy (capitalización, ingresos y su crecimiento, márgenes,
   EBITDA, deuda, caja), explica en simple qué dicen sobre la SALUD del negocio:
   ¿crece o se estanca?, ¿gana o quema plata?, ¿está apalancada o tiene colchón?
   Traduce cada término técnico con una analogía (ej. EBITDA = las ganancias del
   negocio antes de intereses e impuestos; margen bruto = de cada $100 vendidos,
   cuántos quedan tras el costo directo). COPIA las cifras TEXTUALES; no inventes
   ninguna. Si no te doy fundamentales (o vienen vacíos), OMITE este bloque
   entero (deja "numeros": "").
4. EL DEBATE — cómo lo miran distintos perfiles de nuestros inversionistas IA.
   Elige 4 a 6 arquetipos de la lista y dale a cada uno 1-2 frases con SU mirada
   particular sobre este protagonista. Que se CONTRADIGAN entre sí (el optimista
   ve una cosa, el doomer la contraria): ese choque es el corazón del análisis.
5. QUÉ OBSERVAR — qué está en juego de aquí en adelante. ATENCIÓN, no predicción:
   "habrá que ver si…", "lo que está en juego es…", nunca "va a…".

LOS ARQUETIPOS DISPONIBLES (usa sus id exactos en el JSON):
{ROSTER}

LO QUE NUNCA HACES — REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena) — TU LÍNEA:
- NUNCA recomiendas comprar, vender ni mantener. Prohibidas: "conviene",
  "es buen momento", "oportunidad de compra", "deberías", "apunta a",
  "podría subir/bajar", "esperamos que", "precio objetivo", "le vemos potencial".
- NUNCA predices el futuro ni das una tesis de inversión propia del medio. El
  "potencial" no lo pones TÚ: lo ponen en tensión los arquetipos, como miradas.
- Analizas y explicas SÍ; aconsejas JAMÁS. Puedes decir por qué algo importa sin
  decirle a nadie qué hacer con su dinero.
B. Integridad de datos:
- Los NÚMEROS, TICKERS y NOMBRES vienen dados. Cópialos TEXTUALES. Las ÚNICAS
  cifras que existen son la variación de precio y los fundamentales que te doy;
  NO inventes ninguna otra (ni múltiplos, ni proyecciones, ni cifras redondeadas
  a ojo). Si un dato no está en lo que te di, NO lo mencionas.

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "titular": "titular con gancho sobre el protagonista, en tu voz",
  "dek": "una bajada de una línea (subtítulo)",
  "contexto": "2-3 párrafos (separados por \\n\\n): QUÉ ES el protagonista",
  "lectura": "2-3 párrafos (separados por \\n\\n): por qué está en la mira + la narrativa",
  "numeros": "2-3 párrafos (separados por \\n\\n) explicando en simple los fundamentales verificados; \\"\\" si no te di ninguno",
  "debate": [
    {"arquetipo": "contrarian_sabio", "mirada": "1-2 frases con su mirada sobre este protagonista"}
  ],
  "que_observar": "1 párrafo: qué está en juego / qué observar (atención, no predicción)"
}
Escribe SIEMPRE en español. Prioriza profundidad; el debate DEBE tener miradas
que se contradigan.""".replace("{ROSTER}", _roster_arquetipos())


def _mensaje_analisis(analisis: dict, cuando: dict | None = None) -> str:
    """Serializa los hechos del protagonista del fin de semana para el redactor:
    qué es (contexto factual), su cifra verificada y el encuadre. Solo hechos."""
    cuando = cuando or contexto_temporal()
    es_sector = analisis.get("modo") == "sector"
    lineas = [
        f'HOY es {cuando["dia_semana"]} {cuando["fecha"]} (fin de semana, mercado cerrado).',
        f'Sección: {analisis.get("titulo", "")}.',
        "",
        f'PROTAGONISTA: {analisis.get("nombre", "")} [{analisis.get("ticker", "")}]',
    ]
    if es_sector:
        lineas.append(f'Es un SECTOR completo. Se está moviendo por: {analisis.get("en_rotacion_por", "")}.')
        if analisis.get("ejemplos"):
            lineas.append(f'Ejemplos de empresas del sector: {", ".join(analisis["ejemplos"])}.')
    else:
        lineas.append(f'Es una empresa de MEDIANA capitalización. Sector: {analisis.get("sector", "")}.')
    lineas += [
        "",
        "CONTEXTO FACTUAL (qué es — apóyate en esto, NO inventes más datos):",
        analisis.get("contexto", ""),
        "",
        "LA CIFRA VERIFICADA (la ÚNICA que puedes usar; cópiala textual):",
        f'- Variación de la semana: {analisis.get("var_semana_pct")}%',
    ]
    if analisis.get("var_mes_pct") is not None:
        lineas.append(f'- Variación del mes: {analisis.get("var_mes_pct")}%')
    lineas.append(f'- Ventana del gráfico: {analisis.get("fecha_inicio")} a {analisis.get("fecha_fin")}.')

    fund = analisis.get("fundamentales")
    if isinstance(fund, dict) and fund:
        etiquetas = {
            "market_cap": "Capitalización de mercado", "ingresos": "Ingresos (últimos 12 meses)",
            "crecimiento_ingresos": "Crecimiento de ingresos (interanual)",
            "ebitda": "EBITDA", "margen_bruto": "Margen bruto",
            "margen_operativo": "Margen operativo", "margen_neto": "Margen neto",
            "deuda": "Deuda total", "caja": "Caja y equivalentes",
            "flujo_caja_libre": "Flujo de caja libre",
        }
        lineas += ["", "FUNDAMENTALES VERIFICADOS (datos de mercado; cópialos TEXTUALES, "
                   "explícalos en simple, NO inventes otros):"]
        for clave, etiqueta in etiquetas.items():
            if fund.get(clave):
                lineas.append(f'- {etiqueta}: {fund[clave]}')
    else:
        lineas += ["", "No hay fundamentales para este protagonista: OMITE el bloque de "
                   "números (deja \"numeros\": \"\")."]

    lineas += [
        "",
        "Recuerda: encuadre = lo que nuestros inversionistas IA VEN y ANALIZAN, "
        "NUNCA consejo de inversión. Contexto primero; luego los números y el debate.",
    ]
    return "\n".join(lineas)


def _sanear_debate(debate) -> list[dict]:
    """Cada mirada de arquetipo: arquetipo válido + frase publicable (CMF)."""
    salida = []
    for d in (debate or []):
        if not isinstance(d, dict):
            continue
        arq = str(d.get("arquetipo", "")).strip()
        mirada = str(d.get("mirada", "")).strip()
        if arq in POR_ID and mirada and es_publicable(mirada):
            salida.append({"arquetipo": arq, "nombre": POR_ID[arq]["nombre"], "mirada": mirada[:400]})
    return salida


def _validar_analisis(datos: dict) -> dict | None:
    """Valida la forma del deep-dive y pasa TODO por el filtro CMF. None si no
    queda lo mínimo (contexto + titular publicables)."""
    if not isinstance(datos, dict):
        return None
    titular = str(datos.get("titular", "")).strip()
    contexto = _cmf(datos.get("contexto", ""))
    if not titular or not es_publicable(titular) or not contexto:
        return None
    return {
        "titular": titular[:160],
        "dek": _texto_cmf(datos.get("dek"))[:200],
        "contexto": contexto,
        "lectura": _cmf(datos.get("lectura", "")) or "",
        "numeros": _cmf(datos.get("numeros", "")) or "",
        "debate": _sanear_debate(datos.get("debate")),
        "que_observar": _cmf(datos.get("que_observar", "")) or "",
    }


def redactar_analisis(analisis: dict, cuando: dict | None = None) -> dict | None:
    """Le pone VOZ al deep-dive del fin de semana: {titular, dek, contexto,
    lectura, debate[], que_observar}. None si no se puede (sin clave, API caída,
    JSON roto, todo filtrado por CMF) — el correo cae a su respaldo. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    if not analisis or not analisis.get("contexto"):
        return None
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_ANALISIS,
            messages=[{"role": "user", "content": _mensaje_analisis(analisis, cuando=cuando)}],
        )
        datos = _extraer_json(texto_de(respuesta))
        return _validar_analisis(datos) if datos else None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════
#  EL RESUMEN DE LA SEMANA — la edición del sábado
# ══════════════════════════════════════════════════════════════════════════
# Mira la semana entera con punto de vista: los grandes temas, el porqué de cada
# cosa, cómo la geopolítica y la macro movieron el mercado, y QUÉ OBSERVAR de
# aquí en adelante (atención, jamás predicción). Ver resumen_semanal.py.

PROMPT_RESUMEN = """\
Eres el redactor jefe de EL PULSO (by Rubicón Lab). Es SÁBADO: sale la edición de
FIN DE SEMANA que mira la SEMANA ENTERA. No cuentas el día: haces un RESUMEN con
PUNTO DE VISTA de lo que movió el mercado esta semana. Piensa en la carta de fin
de semana de un buen medio: ameno, agudo, que conecta los puntos.

TU TRABAJO
De los TEMAS de la semana que te doy (titulares que de verdad importaron) y de la
FOTO SEMANAL del mercado (cuánto se movió cada índice/materia prima), arma un
repaso que EXPLIQUE: qué pasó, POR QUÉ pasó, y cómo se conecta con lo macro y lo
geopolítico (tasas, la Fed, el petróleo, conflictos, elecciones). El valor está
en el porqué y en las conexiones, no en repetir titulares.

CÓMO ESCRIBES (tu voz)
- Cálido y filoso, cercano, con humor seco sobre los hechos (nunca sobre el lector).
- Español neutro (Chile/LatAm). Si usas un término técnico, lo explicas ahí mismo
  con una analogía cotidiana.
- Extenso donde importa: cada tema son 2-4 párrafos de análisis real.

LA ESTRUCTURA
1. INTRO — 2-3 párrafos con el ÁNIMO de la semana (¿de miedo?, ¿de euforia?, ¿de
   espera?) y el hilo que la conecta.
2. LOS TEMAS — elige los 3-5 que más marcaron la semana. Cada uno: QUÉ pasó, POR
   QUÉ importó, LA CONEXIÓN (macro/geopolítica), y cierra con QUÉ OBSERVAR.
3. CIERRE — 1 párrafo que remata la semana.

LO QUE NUNCA HACES — REGLAS DE ORO (INNEGOCIABLES)
A. Candado CMF (regulación chilena) — TU LÍNEA:
- NUNCA recomiendas comprar, vender ni mantener. Prohibidas: "conviene", "es buen
  momento", "oportunidad de compra", "deberías", "apunta a", "precio objetivo".
- NUNCA PREDICES el futuro. Cuentas lo que YA pasó y POR QUÉ. Cuando mires hacia
  adelante, es "QUÉ OBSERVAR / qué está en juego / habrá que ver si…", jamás
  "qué va a pasar", "subirá", "caerá", "esperamos que". Punto de vista sobre lo
  ocurrido: SÍ. Adivinar el futuro: JAMÁS.
B. Integridad de datos:
- Los TÍTULARES, NÚMEROS y FECHAS vienen dados. Cópialos TEXTUALES. La única cifra
  es la variación semanal que te doy; no inventes otras. Si un dato no está, no lo
  mencionas. Los titulares se citan como CONTEXTO, no como causa confirmada.

NO menciones "el enjambre" ni simulaciones: El Pulso es un diario serio. (El
Enjambre se promociona aparte, al pie del correo.)

EL GRÁFICO (opcional por tema)
Si un tema gira en torno a un índice o materia prima con ticker claro entre los
datos (S&P 500 = ^GSPC, Nasdaq = ^IXIC, Petróleo = CL=F, Oro = GC=F), puedes pedir
su gráfico en "grafico" con ese ticker (textual) y "periodo": "semana". Si no, deja
"grafico": null.

QUÉ DEVUELVES: SOLO un objeto JSON válido, sin texto alrededor, con esta forma:
{
  "intro": "2-3 párrafos separados por \\n\\n: el ánimo de la semana",
  "temas": [
    {
      "kicker": "etiqueta corta, ej: 'Geopolítica · petróleo', 'Macro · la Fed'",
      "emoji": "un emoji que resuma el tema",
      "titular": "el tema en tu voz, con gancho",
      "analisis": "2-4 párrafos separados por \\n\\n: qué pasó + por qué + la conexión",
      "que_observar": "1 frase de atención (no predicción)",
      "grafico": {"ticker": "CL=F", "nombre": "Petróleo WTI", "periodo": "semana", "moneda": "$"}
    }
  ],
  "cierre": "1 párrafo que remata la semana"
}
Devuelve 3-5 temas. Escribe SIEMPRE en español. Prioriza el porqué y las conexiones."""


def _mensaje_resumen(resumen: dict, cuando: dict | None = None) -> str:
    """Serializa los hechos de la semana para el redactor: los temas (titulares
    destacados) y la foto semanal del mercado. Solo hechos verificados."""
    cuando = cuando or contexto_temporal()
    lineas = [
        f'HOY es {cuando["dia_semana"]} {cuando["fecha"]} (edición de fin de semana: '
        f'repaso de la SEMANA, sin sesión de mercado hoy).',
        "Saluda acorde y usa esta fecha; NO inventes otra.\n",
    ]
    foto = resumen.get("foto") or []
    if foto:
        lineas.append("LA SEMANA EN NÚMEROS (variación de la semana; cópiala textual):")
        for f in foto:
            lineas.append(f'- {f.get("nombre","")} [{f.get("simbolo","")}]: {f.get("var_semana_pct")}%')
        lineas.append("")
    titulares = resumen.get("titulares") or []
    if titulares:
        lineas.append("LOS TEMAS DE LA SEMANA (titulares que importaron; elige y desarrolla los "
                      "que más la marcaron, explica el POR QUÉ y la conexión macro/geopolítica):")
        for t in titulares:
            lineas.append(f'- ({t.get("fecha","")}) «{t.get("titular","")}»')
        lineas.append("")
    lineas.append("Recuerda: punto de vista sobre lo que YA pasó y su porqué, SÍ; predecir el "
                  "futuro, JAMÁS. Mirar adelante = 'qué observar', nunca 'qué va a pasar'.")
    return "\n".join(lineas)


def _sanear_tema(t: dict) -> dict | None:
    """Un tema de la semana: titular + análisis publicables (CMF). None si no."""
    if not isinstance(t, dict):
        return None
    titular = str(t.get("titular", "")).strip()
    analisis = _cmf(t.get("analisis", ""))
    if not titular or not es_publicable(titular) or not analisis:
        return None
    return {
        "kicker": _texto_cmf(t.get("kicker"))[:60],
        "emoji": str(t.get("emoji", "") or "").strip()[:4],
        "titular": titular[:160],
        "analisis": analisis,
        "que_observar": _texto_cmf(t.get("que_observar"))[:280],
        "grafico": _grafico_valido(t.get("grafico")),
    }


def _validar_resumen(datos: dict) -> dict | None:
    """Valida la forma del resumen y pasa TODO por el filtro CMF. None si no queda
    ni intro ni temas."""
    if not isinstance(datos, dict):
        return None
    intro = _cmf(datos.get("intro", ""))
    temas = [s for s in (_sanear_tema(t) for t in (datos.get("temas") or [])
                         if isinstance(t, dict)) if s]
    if not temas and not intro:
        return None
    return {"intro": intro or "", "temas": temas[:5], "cierre": _cmf(datos.get("cierre", "")) or ""}


def redactar_resumen(resumen: dict, cuando: dict | None = None) -> dict | None:
    """Le pone VOZ al resumen de la semana: {intro, temas[], cierre}. None si no
    se puede (sin clave, API caída, JSON roto, todo filtrado por CMF) — el correo
    cae a su respaldo. NUNCA lanza."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    if not resumen or not resumen.get("titulares"):
        return None
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=PROMPT_RESUMEN,
            messages=[{"role": "user", "content": _mensaje_resumen(resumen, cuando=cuando)}],
        )
        datos = _extraer_json(texto_de(respuesta))
        return _validar_resumen(datos) if datos else None
    except Exception:
        return None
