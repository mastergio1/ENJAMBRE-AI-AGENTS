"""El Pulso del Enjambre — la newsletter (CONTENIDO.md sección 6).

Arma el correo diario desde plantilla (HTML de correo: tablas + estilos
inline, ancho 600px) y lo envía por Resend. Todos los textos variables pasan
por el filtro de vocabulario CMF antes de salir. Degradación elegante: sin
RESEND_API_KEY, genera el HTML pero no envía.

Paleta CLARA (boceto aprobado por Giorgio, 5-ago-2026): fondo blanco cálido,
texto tinta, dorado de protagonista, teal de reparto, verde/rojo en los
movimientos. El enjambre 3D vive en oscuro; el diario se lee en claro.
"""

import html
import os

import httpx

from contenido import persistencia
from contenido.vocabulario import DISCLAIMER, es_publicable

_esc = html.escape

URL_RESEND = "https://api.resend.com/emails"
REMITENTE = os.environ.get("PULSO_REMITENTE", "El Enjambre <pulso@rubiconlab.cl>")
BASE_WEB = os.environ.get("ENJAMBRE_WEB_URL", "https://enjambre-ai-agents.vercel.app")
BASE_API = os.environ.get("ENJAMBRE_API_URL", "https://enjambre-motor.onrender.com")

# --- paleta CLARA del correo (boceto aprobado) ---
PAPEL = "#faf8f4"          # fondo de página, blanco cálido
BLANCO = "#ffffff"         # tarjeta del correo
TEXTO = "#1e1b17"          # texto principal (el ink de marca, ahora como texto)
TEXTO_2 = "#3c382f"        # cuerpo
MUTE = "#6f6a5f"           # secundario
ORO = "#b0831a"            # dorado protagonista (marca, botón)
TEAL = "#2f7a6f"           # teal de reparto (enlaces)
SUBE = "#2f8f66"           # verde — sube
BAJA = "#c0504d"           # rojo-arcilla — baja
LINEA = "#eae5db"          # hairline


def _flecha(direccion_pct: float) -> str:
    if direccion_pct > 1.0:
        return "▲"
    if direccion_pct < -1.0:
        return "▼"
    return "◆"


def COLOR_DIR(pct: float) -> str:
    return SUBE if pct > 0.15 else BAJA if pct < -0.15 else TEAL


def _limpiar(texto: str) -> str:
    """Un texto variable solo sale si pasa el filtro CMF; si no, se neutraliza.

    Además ESCAPA el HTML: los titulares llegan de fuentes externas (Alpaca) y
    las frases las escribe la IA leyendo un titular que puede venir del público.
    Sin escapar, un `<` en un titular rompe el correo — y un titular hostil podría
    colar marcado (un enlace falso) en el Pulso que reciben los suscriptores.
    Todos los usos de esta función son contexto HTML.
    """
    return _esc(texto) if es_publicable(texto) else "—"


def _url_segura(url: str) -> str:
    """Solo http(s) llega al correo: cierra la puerta a `javascript:` y `data:`."""
    limpia = (url or "").strip()
    return _esc(limpia) if limpia.lower().startswith(("http://", "https://")) else ""


def _voz(frase: dict) -> str:
    from brains.arquetipos import POR_ID
    nombre = POR_ID.get(frase.get("arquetipo", ""), {}).get("nombre", frase.get("arquetipo", ""))
    return f"«{_limpiar(frase.get('frase', ''))}» — {nombre}"


def _parrafos(texto: str, color: str = TEXTO_2, size: int = 15) -> str:
    """Convierte el texto con voz (párrafos separados por línea en blanco) en
    <p> escapados. El texto ya viene filtrado por CMF desde redaccion_ia."""
    if not texto:
        return ""
    return "".join(
        f'<p style="margin:0 0 12px;color:{color};font-size:{size}px;line-height:1.55;">{_esc(p.strip())}</p>'
        for p in texto.split("\n\n") if p.strip()
    )


def asunto_del_dia(destacada: dict) -> str:
    palabras = destacada["titular"].split()
    resumen = " ".join(palabras[:6]) + ("…" if len(palabras) > 6 else "")
    return f"🐝 El Pulso — {resumen}"


def asunto_finde(analisis: dict | None) -> str:
    """El asunto de la edición de fin de semana: la sección + el protagonista."""
    analisis = analisis or {}
    titulo = analisis.get("titulo", "Fin de semana")
    nombre = analisis.get("nombre", "")
    return f"🐝 El Pulso — {titulo}: {nombre}".rstrip(": ")


def _fila_mercado(m: dict) -> str:
    url = _url_segura(m.get("url", ""))
    fuente = (f'<a href="{url}" style="color:{TEAL};font-size:12px;text-decoration:none;">·&nbsp;fuente</a>'
              if url else "")
    if m.get("tipo") == "evento":
        marca = f'<span style="color:{ORO};font-weight:bold;">◆</span>'
        cuerpo = _esc(m["titular"])
    else:  # movimiento de precio
        marca = f'<span style="color:{COLOR_DIR(m["variacion_pct"])};font-weight:bold;">{_flecha(m["variacion_pct"])}</span>'
        cuerpo = _esc(m["frase"])
    return f"""<tr><td style="padding:6px 0;color:{TEXTO_2};font-size:14px;line-height:1.45;border-top:1px solid {LINEA};">
        {marca} {cuerpo} {fuente}</td></tr>"""


def _bloque_mercado(brief: dict | None) -> str:
    """'Lo que pasó' — movimientos verificados + eventos, con su fuente.
    (En modo con voz, esto lo cuenta el editorial; se usa en el fallback.)"""
    if not brief or not brief.get("mercado"):
        return ""
    filas = "".join(_fila_mercado(m) for m in brief["mercado"][:5])
    return f"""
  <tr><td style="padding:18px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">Lo que pasó</div>
  </td></tr>
  <tr><td style="padding:4px 32px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{filas}</table></td></tr>"""


def _pildora(pct) -> str:
    """Una píldora verde/roja con la variación, o '—' si no hay dato."""
    if pct is None:
        return f'<span style="color:{MUTE};font-size:12px;">—</span>'
    if pct > 0.05:
        color, bg, flecha = SUBE, "rgba(47,143,102,0.14)", "▲"
    elif pct < -0.05:
        color, bg, flecha = BAJA, "rgba(192,80,77,0.13)", "▼"
    else:
        color, bg, flecha = MUTE, "rgba(60,56,47,0.06)", "•"
    return (f'<span style="display:inline-block;padding:3px 9px;border-radius:12px;'
            f'background:{bg};color:{color};font-size:12px;font-weight:bold;">'
            f'{flecha} {abs(pct)}%</span>')


def _tabla_mercado(brief: dict | None) -> str:
    """'La foto del día': el telón de fondo (índices, petróleo, oro) con sus
    columnas Día / Mes / Año."""
    foto = (brief or {}).get("foto")
    if not foto:
        return ""
    th = (f'font-size:10px;letter-spacing:1px;color:{MUTE};text-transform:uppercase;'
          'font-weight:600;padding:0 0 8px;')
    filas = ""
    for f in foto:
        filas += f"""<tr>
          <td style="padding:7px 0;border-top:1px solid {LINEA};color:{TEXTO};font-size:14px;font-weight:600;">{_esc(f["nombre"])}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{_pildora(f.get("variacion_pct"))}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{_pildora(f.get("var_mes_pct"))}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{_pildora(f.get("var_ano_pct"))}</td>
        </tr>"""
    return f"""
  <tr><td style="padding:18px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">La foto del día</div>
  </td></tr>
  <tr><td style="padding:6px 32px 4px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr><th align="left" style="{th}">Mercado</th><th align="right" style="{th}">Día</th><th align="right" style="{th}">Mes</th><th align="right" style="{th}">Año</th></tr>
      {filas}
    </table>
  </td></tr>"""


def _bloque_observa(brief: dict | None) -> str:
    """'Qué observa el enjambre hoy' — atención, NUNCA predicción."""
    if not brief or not brief.get("observa"):
        return ""
    filas = "".join(
        f"""<p style="margin:4px 0;color:{MUTE};font-size:14px;">· {_esc(t)}</p>"""
        for t in brief["observa"][:3]
    )
    return f"""
  <tr><td style="padding:14px 32px 4px;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">Qué observa el enjambre hoy</div>
    {filas}</td></tr>"""


def _grafico_img(g: dict | None) -> str:
    """El <img> del gráfico de precio REAL de un activo, si la historia trae uno.
    Apunta al endpoint /api/grafico, que lo dibuja desde Yahoo. Si el ticker es
    inválido, no se pone gráfico (nunca rompe el correo)."""
    if not isinstance(g, dict) or not g.get("ticker"):
        return ""
    from urllib.parse import quote
    ticker = str(g.get("ticker", "")).strip()
    if not ticker or len(ticker) > 15 or not all(c.isalnum() or c in ".=^-" for c in ticker):
        return ""
    periodo = str(g.get("periodo", "semana")).strip() or "semana"
    nombre = str(g.get("nombre", "") or ticker)[:40]
    moneda = str(g.get("moneda", "$") or "$")[:2]
    url = (f"{BASE_API}/api/grafico/{quote(ticker, safe='.=^-')}"
           f"?n={quote(nombre)}&p={quote(periodo)}&m={quote(moneda)}")
    return f"""
  <tr><td style="padding:8px 32px 2px;">
    <img src="{url}" width="536" alt="Gráfico de {_esc(nombre)}"
      style="width:100%;max-width:536px;display:block;border:1px solid {LINEA};border-radius:8px;">
  </td></tr>"""


def _sin_prefijo_linea(texto: str) -> str:
    """Quita un 'En una línea:' inicial si el redactor lo incluyó (lo pone la plantilla)."""
    t = texto.strip()
    bajo = t.lower()
    for p in ("en una línea:", "en una linea:", "en resumen:", "bottom line:"):
        if bajo.startswith(p):
            return t[len(p):].strip()
    return t


def _bloque_historia(h: dict) -> str:
    """Una historia del día: etiqueta, titular, bajada, gráfico real, análisis
    y el 'en una línea' de cierre. Todo escapado (los titulares y el texto de la
    IA no pueden inyectar HTML) y filtrado por CMF vía _limpiar."""
    if not isinstance(h, dict):
        return ""
    kicker = _limpiar(str(h.get("kicker", "") or ""))
    emoji = _esc(str(h.get("emoji", "") or ""))
    titular = _limpiar(str(h.get("titular", "") or ""))
    dek = _limpiar(str(h.get("dek", "") or ""))
    cuerpo = _parrafos(str(h.get("cuerpo", "") or ""))
    bl = _limpiar(_sin_prefijo_linea(str(h.get("bottom_line", "") or "")))
    if not titular or not cuerpo:
        return ""
    kicker_html = (f'<div style="font-size:11px;letter-spacing:1.5px;color:{TEAL};'
                   f'text-transform:uppercase;font-weight:700;margin-bottom:4px;">{kicker}</div>'
                   if kicker and kicker != "—" else "")
    dek_html = (f'<div style="font-family:Georgia,serif;font-style:italic;color:{MUTE};'
                f'font-size:14px;margin:3px 0 10px;">{dek}</div>' if dek and dek != "—" else "")
    bl_html = (f'<div style="margin:15px 0 2px;padding:12px 16px;background:{PAPEL};'
               f'border-left:3px solid {ORO};border-radius:6px;color:{TEXTO_2};font-size:14px;">'
               f'<b style="color:{TEXTO};">En una línea:</b> {bl}</div>' if bl and bl != "—" else "")
    return f"""
  <tr><td style="padding:22px 32px 2px;border-top:1px solid {LINEA};">
    {kicker_html}
    <div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:{TEXTO};line-height:1.25;">{emoji} {titular}</div>
    {dek_html}
  </td></tr>
  {_grafico_img(h.get("grafico"))}
  <tr><td style="padding:8px 32px 2px;">
    {cuerpo}
    {bl_html}
  </td></tr>"""


def _bloque_debate(debate: list[dict]) -> str:
    """El debate de arquetipos: miradas contrastantes de nuestros inversionistas
    IA sobre el protagonista. Cada una es nombre del perfil + su frase (escapada
    y filtrada por CMF). Este contraste ES el análisis del fin de semana."""
    if not debate:
        return ""
    tarjetas = ""
    for d in debate:
        if not isinstance(d, dict):
            continue
        nombre = _limpiar(str(d.get("nombre", "") or ""))
        mirada = _limpiar(str(d.get("mirada", "") or ""))
        if not mirada or mirada == "—":
            continue
        tarjetas += f"""
      <tr><td style="padding:10px 0;border-top:1px solid {LINEA};">
        <div style="font-size:11px;letter-spacing:1px;color:{TEAL};text-transform:uppercase;font-weight:700;margin-bottom:3px;">{nombre}</div>
        <div style="color:{TEXTO_2};font-size:14px;line-height:1.5;">{mirada}</div>
      </td></tr>"""
    if not tarjetas:
        return ""
    return f"""
  <tr><td style="padding:18px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;">🐝 Lo que ven nuestros inversionistas IA</div>
    <div style="color:{MUTE};font-size:12px;font-style:italic;margin:4px 0 2px;">Miradas distintas del mismo caso — no un veredicto único.</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{tarjetas}</table>
  </td></tr>"""


def _pildora_pct_texto(fmt: str) -> str:
    """Una píldora verde/roja a partir de un porcentaje YA formateado por Yahoo
    (ej. '35.50%', '-4.20%'). El color sale del signo; no reinterpreta el número."""
    t = str(fmt or "").strip()
    negativo = t.startswith("-")
    color, bg = (BAJA, "rgba(192,80,77,0.13)") if negativo else (SUBE, "rgba(47,143,102,0.14)")
    flecha = "▼" if negativo else "▲"
    return (f'<span style="display:inline-block;padding:2px 8px;border-radius:12px;'
            f'background:{bg};color:{color};font-size:12px;font-weight:bold;">{flecha} {_esc(t)}</span>')


# fundamentales que se muestran, en orden, y cuáles llevan píldora de color (%)
_FUND_FILAS = [
    ("market_cap", "Capitalización", False),
    ("ingresos", "Ingresos (12m)", False),
    ("crecimiento_ingresos", "Crecimiento ingresos", True),
    ("margen_bruto", "Margen bruto", False),
    ("margen_operativo", "Margen operativo", False),
    ("ebitda", "EBITDA", False),
    ("deuda", "Deuda total", False),
    ("caja", "Caja", False),
]


def _tabla_fundamentales(fund: dict | None) -> str:
    """'Los números' del protagonista: la ficha de fundamentales VERIFICADOS
    (datos de mercado), como la tabla de un analista. Solo cifras que existen;
    se dibuja desde los datos, no desde el texto de la IA. '' si no hay ficha."""
    if not isinstance(fund, dict) or not fund:
        return ""
    filas = ""
    for clave, etiqueta, es_pct in _FUND_FILAS:
        valor = fund.get(clave)
        if not valor:
            continue
        celda = _pildora_pct_texto(valor) if es_pct else f'<b style="color:{TEXTO};font-size:14px;">{_esc(str(valor))}</b>'
        filas += f"""<tr>
          <td style="padding:7px 0;border-top:1px solid {LINEA};color:{TEXTO_2};font-size:13px;">{etiqueta}</td>
          <td align="right" style="padding:7px 0;border-top:1px solid {LINEA};">{celda}</td>
        </tr>"""
    if not filas:
        return ""
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:{PAPEL};border:1px solid {LINEA};border-radius:8px;padding:2px 14px;margin:2px 0 6px;">{filas}
      <tr><td colspan="2" style="padding:6px 0 2px;color:{MUTE};font-size:11px;font-style:italic;">Datos de mercado (Yahoo Finance), últimos disponibles.</td></tr>
    </table>"""


def _bloque_numeros(hechos: dict, red: dict) -> str:
    """'Los números': la ficha de fundamentales (tabla desde datos) + la lectura
    financiera en simple que escribió la IA. '' si no hay ni ficha ni prosa."""
    tabla = _tabla_fundamentales(hechos.get("fundamentales"))
    prosa = _parrafos(str(red.get("numeros", "") or ""))
    if not tabla and not prosa:
        return ""
    return f"""
  <tr><td style="padding:14px 32px 2px;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;margin-bottom:6px;">Los números</div>
    {tabla}
    {prosa}
  </td></tr>"""


def _bloque_analisis(brief: dict | None) -> str:
    """La EDICIÓN DE FIN DE SEMANA: el deep-dive de una mid-cap o un sector.
    Contexto primero (qué es), la lectura (por qué está en la mira), el gráfico
    real, los números (fundamentales), el debate de arquetipos y qué observar.
    Todo escapado + filtrado CMF. '' si no hay análisis redactado."""
    brief = brief or {}
    red = brief.get("analisis_redactado")
    hechos = brief.get("analisis") or {}
    if not isinstance(red, dict) or not red.get("contexto") or not red.get("titular"):
        return ""

    titulo = _limpiar(str(hechos.get("titulo", "Edición de fin de semana")))
    encuadre = _limpiar(str(hechos.get("encuadre", "")))
    nombre = _limpiar(str(hechos.get("nombre", "")))
    ticker = _esc(str(hechos.get("ticker", "") or ""))
    sector = _limpiar(str(hechos.get("sector", "") or ""))
    titular = _limpiar(str(red.get("titular", "")))
    dek = _limpiar(str(red.get("dek", "") or ""))
    contexto = _parrafos(str(red.get("contexto", "") or ""))
    lectura = _parrafos(str(red.get("lectura", "") or ""))
    que_observar = _parrafos(str(red.get("que_observar", "") or ""), color=TEXTO_2)
    pildora = _pildora(hechos.get("var_semana_pct"))

    dek_html = (f'<div style="font-family:Georgia,serif;font-style:italic;color:{MUTE};'
                f'font-size:15px;margin:4px 0 8px;">{dek}</div>' if dek and dek != "—" else "")
    sector_html = (f'<span style="color:{MUTE};font-size:12px;">· {sector}</span>'
                   if sector and sector != "—" else "")
    lectura_html = (f"""
  <tr><td style="padding:6px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;margin-bottom:4px;">Por qué está en la mira</div>
    {lectura}
  </td></tr>""" if lectura else "")
    observar_html = (f"""
  <tr><td style="padding:8px 32px 6px;">
    <div style="margin:6px 0 2px;padding:12px 16px;background:{PAPEL};border-left:3px solid {ORO};border-radius:6px;">
      <div style="font-size:11px;letter-spacing:1px;color:{ORO};text-transform:uppercase;font-weight:700;margin-bottom:4px;">Qué observar</div>
      <div style="color:{TEXTO_2};font-size:14px;line-height:1.55;">{que_observar}</div>
    </div>
  </td></tr>""" if que_observar else "")

    return f"""
  <tr><td style="padding:22px 32px 4px;text-align:center;border-top:1px solid {LINEA};">
    <div style="font-size:11px;letter-spacing:3px;color:{ORO};text-transform:uppercase;font-weight:700;">◆ Edición de fin de semana</div>
    <div style="font-size:11px;letter-spacing:1px;color:{TEAL};text-transform:uppercase;font-weight:700;margin-top:6px;">{titulo} · {encuadre}</div>
  </td></tr>
  <tr><td style="padding:4px 32px 2px;">
    <div style="font-family:Georgia,serif;font-size:24px;font-weight:bold;color:{TEXTO};line-height:1.25;">{titular}</div>
    {dek_html}
    <div style="margin:6px 0 2px;">{pildora} <b style="color:{TEXTO};font-size:14px;">{nombre}</b>
      <span style="color:{MUTE};font-size:12px;">{ticker}</span> {sector_html}
      <span style="color:{MUTE};font-size:12px;">· en la semana</span></div>
  </td></tr>
  <tr><td style="padding:10px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;margin-bottom:4px;">Qué es</div>
    {contexto}
  </td></tr>
  {lectura_html}
  {_grafico_img(hechos.get("grafico"))}
  {_bloque_numeros(hechos, red)}
  {_bloque_debate(red.get("debate"))}
  {observar_html}
  <tr><td style="padding:2px 32px 8px;">
    <div style="color:{MUTE};font-size:12px;font-style:italic;line-height:1.5;">No es asesoría de inversión: es lo que nuestros inversionistas IA están viendo y analizando.</div>
  </td></tr>"""


def _footer_enjambre() -> str:
    """El Enjambre al pie, como herramienta HERMANA (no como autor de El Pulso):
    una invitación a probarlo + su descripción. Nada de 'esto lo escribe el
    enjambre' — El Pulso es el diario serio; El Enjambre, otra herramienta nuestra."""
    return f"""
  <tr><td style="padding:10px 32px 24px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#171019;border-radius:12px;">
      <tr><td style="padding:20px 22px;">
        <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#e3c565;font-weight:700;">🐝 También de Rubicón Lab</div>
        <div style="font-family:Georgia,serif;font-size:18px;color:#ffffff;font-weight:bold;margin:6px 0;">Mira al mercado entrar en pánico, en cámara lenta</div>
        <div style="color:#c7bfb2;font-size:13px;line-height:1.55;margin-bottom:14px;">El Enjambre es nuestra herramienta educativa: le sueltas un titular y 10.000 inversionistas simulados con IA reaccionan en vivo, en 3D. Ves formarse la manada, el miedo y la euforia — el comportamiento de las masas del mercado, hecho visible.</div>
        <a href="{BASE_WEB}" style="display:inline-block;background:#e3c565;color:#1b1410;text-decoration:none;font-weight:bold;font-size:12px;letter-spacing:.5px;padding:11px 20px;border-radius:7px;">Probar El Enjambre →</a>
      </td></tr>
    </table>
  </td></tr>"""


def construir_html(destacadas: list[dict], fecha: str, token_baja: str = "TOKEN",
                   brief: dict | None = None) -> str:
    """El HTML del correo (rediseño estilo diario): las NOTICIAS con análisis y
    gráficos reales son el cuerpo; El Enjambre baja al pie como herramienta
    hermana. `destacadas` ya no arma el cuerpo (el correo es noticioso), pero se
    mantiene la firma por compatibilidad. brief["redactado"] trae las historias."""
    brief = brief or {}
    red = brief.get("redactado") or {}
    url_baja = f"{BASE_API}/api/baja/{token_baja}"

    # EDICIÓN DE FIN DE SEMANA: si hay un deep-dive redactado, ES el correo
    # (reemplaza las noticias del día; el fin de semana no hay sesión).
    analisis_html = _bloque_analisis(brief)
    es_finde = bool(analisis_html)

    historias = [] if es_finde else [h for h in (red.get("historias") or []) if isinstance(h, dict)]
    historias_html = "".join(_bloque_historia(h) for h in historias)

    buenos_html = ""
    if not es_finde and red.get("buenos_dias"):
        buenos_html = f"""
  <tr><td style="padding:22px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:700;">☀️ Buenos días</div>
    {_parrafos(red["buenos_dias"])}
  </td></tr>"""

    # la foto del día (índices, petróleo, oro) va entre semana; el fin de semana
    # el deep-dive se lee solo, sin la tabla del telón (cierres del viernes).
    tabla_html = "" if es_finde else _tabla_mercado(brief)

    # respaldo: si la IA no escribió historias, al menos 'lo que pasó' crudo
    # (mejor un digest simple que un correo vacío). No aplica al fin de semana.
    cuerpo_respaldo = _bloque_mercado(brief) if (not historias and not es_finde) else ""

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{PAPEL};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{PAPEL};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0"
  style="max-width:600px;width:100%;background:{BLANCO};border:1px solid {LINEA};border-radius:8px;">

  <tr><td style="padding:30px 32px 20px;text-align:center;border-bottom:1px solid {LINEA};">
    <div style="font-family:Georgia,serif;font-size:34px;font-weight:bold;color:{ORO};line-height:1;">El Pulso 🐝</div>
    <div style="font-size:10px;letter-spacing:3px;color:{TEAL};text-transform:uppercase;font-weight:bold;margin-top:10px;">Diario de mercado</div>
    <div style="font-family:Georgia,serif;font-style:italic;font-size:16px;color:{MUTE};margin-top:4px;">{fecha}</div>
    <div style="font-size:11px;color:{MUTE};margin-top:6px;">by <b style="color:{TEXTO_2};">Rubicón Lab</b></div>
  </td></tr>
  {tabla_html}
  {buenos_html}
  {analisis_html}
  {historias_html}
  {cuerpo_respaldo}
  {_footer_enjambre()}

  <tr><td style="padding:8px 32px 28px;border-top:1px solid {LINEA};text-align:center;">
    <div style="color:{MUTE};font-size:11px;line-height:1.5;">{DISCLAIMER}</div>
    <div style="margin-top:10px;">
      <a href="{url_baja}" style="color:{TEAL};font-size:11px;">Desuscribirse en un clic</a>
    </div>
  </td></tr>

</table></td></tr></table></body></html>"""


def _tag_edicion(fecha: str | None) -> list[dict] | None:
    """El tag que Resend devuelve en el webhook, para atribuir aperturas/clics a
    su edición. Resend solo admite letras/números/_/-; la fecha AAAA-MM-DD cumple."""
    if not fecha:
        return None
    limpio = "".join(c for c in fecha if c.isalnum() or c in "-_")[:60]
    return [{"name": "edicion", "value": limpio}] if limpio else None


def enviar(destinatario: str, asunto: str, html: str, fecha_edicion: str | None = None) -> bool:
    """Envía un correo por Resend. False si no hay clave o falla (no lanza).
    `fecha_edicion` etiqueta el correo para poder medir su apertura por edición."""
    clave = os.environ.get("RESEND_API_KEY")
    if not clave:
        return False
    cuerpo = {"from": REMITENTE, "to": [destinatario], "subject": asunto, "html": html}
    tags = _tag_edicion(fecha_edicion)
    if tags:
        cuerpo["tags"] = tags
    try:
        respuesta = httpx.post(
            URL_RESEND,
            headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"},
            json=cuerpo,
            timeout=20,
        )
        return respuesta.status_code < 300
    except Exception:
        return False


def enviar_confirmacion(email: str, token_confirma: str) -> bool:
    """El correo del double opt-in: un clic para confirmar la suscripción."""
    url = f"{BASE_API}/api/confirmar/{token_confirma}"
    html = f"""<!doctype html><html><body style="margin:0;background:{PAPEL};">
<table role="presentation" width="100%" style="background:{PAPEL};"><tr><td align="center" style="padding:32px;">
<table role="presentation" width="600" style="max-width:600px;background:{BLANCO};border:1px solid {LINEA};border-radius:8px;">
  <tr><td style="padding:34px;text-align:center;">
    <div style="font-family:Georgia,serif;font-size:30px;color:{ORO};font-weight:bold;">El Enjambre 🐝</div>
    <p style="color:{TEXTO_2};font-size:16px;line-height:1.5;">Confirma tu suscripción a <b>El Pulso</b>,
      el diario de mercado donde el enjambre simulado reacciona a los titulares del día.</p>
    <a href="{url}" style="display:inline-block;background:{ORO};color:#ffffff;text-decoration:none;
      font-weight:bold;padding:13px 28px;border-radius:4px;text-transform:uppercase;letter-spacing:1px;">Confirmar suscripción</a>
    <p style="color:{MUTE};font-size:12px;margin-top:18px;">
      Si no fuiste tú, ignora este correo y no recibirás nada más.</p>
    <p style="color:{MUTE};font-size:11px;">{DISCLAIMER}</p>
  </td></tr>
</table></td></tr></table></body></html>"""
    return enviar(email, "Confirma tu suscripción a El Pulso 🐝", html)


def enviar_pulso(conexion, destacadas: list[dict], fecha: str) -> dict:
    """Envía el Pulso a todos los suscriptores activos. Devuelve el conteo."""
    activos = persistencia.suscriptores_activos(conexion)
    asunto = asunto_del_dia(destacadas[0])
    enviados, fallidos = 0, 0
    for suscriptor in activos:
        html = construir_html(destacadas, fecha, token_baja=suscriptor["token_baja"])
        if enviar(suscriptor["email"], asunto, html):
            enviados += 1
        else:
            fallidos += 1
    return {"suscriptores": len(activos), "enviados": enviados, "fallidos": fallidos}


# ---------- El correo de REVISIÓN (humano en el lazo, desde el celular) ----------

PULSO_ADMIN_EMAIL = os.environ.get("PULSO_ADMIN_EMAIL", "")


def _banner_revision(fecha_es: str, token: str, suscriptores: int) -> str:
    """El banner que se inyecta arriba del preview en el correo de revisión."""
    url = f"{BASE_API}/pulso/revisar/{token}"
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#161009;">
  <tr><td align="center" style="padding:18px 16px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
      <tr><td style="text-align:center;">
        <div style="font:700 11px/1 system-ui,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#e3c565;">⏸ Pendiente de tu revisión</div>
        <div style="font-family:Georgia,serif;font-size:19px;color:#faf8f4;margin:6px 0 2px;">El Pulso — {_esc(fecha_es)}</div>
        <div style="color:#a8a291;font-size:13px;margin-bottom:12px;">Abajo va la edición tal como la recibirían tus {suscriptores} suscriptores. Revísala y decide.</div>
        <a href="{url}" style="display:inline-block;background:#e3c565;color:#161009;text-decoration:none;
          font-weight:bold;font-size:13px;letter-spacing:1px;text-transform:uppercase;padding:13px 30px;border-radius:6px;">Revisar y decidir →</a>
      </td></tr>
    </table>
  </td></tr>
</table>"""


def construir_revision(preview_html: str, fecha_es: str, token: str, suscriptores: int) -> str:
    """Inyecta el banner de revisión arriba del preview real (WYSIWYG)."""
    banner = _banner_revision(fecha_es, token, suscriptores)
    corte = preview_html.find(">", preview_html.find("<body"))
    if corte == -1:  # por si el preview no es un doc completo
        return banner + preview_html
    corte += 1
    return preview_html[:corte] + banner + preview_html[corte:]


def enviar_revision(fecha_es: str, preview_html: str, token: str, suscriptores: int,
                    admin_email: str | None = None) -> bool:
    """Envía a Giorgio el correo de revisión (preview + botón para decidir).
    Va a su propio correo → funciona aun sin dominio (modo prueba de Resend)."""
    destino = (admin_email or PULSO_ADMIN_EMAIL).strip()
    if not destino:
        return False
    html = construir_revision(preview_html, fecha_es, token, suscriptores)
    return enviar(destino, f"📋 Revisar El Pulso — {fecha_es}", html)


def enviar_a_suscriptores(conexion, preview_html: str, asunto: str,
                          fecha_edicion: str | None = None) -> dict:
    """Envía la edición YA APROBADA a los suscriptores activos, reemplazando el
    marcador del token de baja por el de cada uno (WYSIWYG con lo revisado).
    Cada correo va etiquetado con `fecha_edicion` para medir su apertura."""
    activos = persistencia.suscriptores_activos(conexion)
    enviados = 0
    for s in activos:
        html = preview_html.replace(persistencia.TOKEN_BAJA_SENTINEL, s["token_baja"])
        if enviar(s["email"], asunto, html, fecha_edicion=fecha_edicion):
            enviados += 1
    return {"suscriptores": len(activos), "enviados": enviados, "fallidos": len(activos) - enviados}
