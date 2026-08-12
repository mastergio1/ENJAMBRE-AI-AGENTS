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
    """Un texto variable solo sale si pasa el filtro CMF; si no, se neutraliza."""
    return texto if es_publicable(texto) else "—"


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


def _fila_mercado(m: dict) -> str:
    fuente = (f'<a href="{_esc(m["url"])}" style="color:{TEAL};font-size:12px;text-decoration:none;">·&nbsp;fuente</a>'
              if m.get("url") else "")
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


def construir_html(destacadas: list[dict], fecha: str, token_baja: str = "TOKEN",
                   brief: dict | None = None) -> str:
    """El HTML del correo (paleta clara). destacadas: [{titular, sim_id, resumen, lideres}].
    brief (opcional): el análisis de mercado de La Redacción."""
    if not destacadas:
        raise ValueError("no hay simulaciones destacadas para el Pulso")

    principal = destacadas[0]
    resumen = principal["resumen"]
    direccion = resumen.get("direccion_pct", 0) or 0
    agitacion = resumen.get("agitacion") or "medio"

    frases = sorted(principal.get("lideres_frases", []), key=lambda f: f.get("senal", 0))
    voces = [frases[0], frases[-1]] if len(frases) >= 2 else []

    url_sim = f"{BASE_WEB}/?sim={principal['sim_id']}"
    url_img = f"{BASE_API}/api/simulacion/{principal['sim_id']}/imagen"
    url_baja = f"{BASE_API}/api/baja/{token_baja}"

    otras = "".join(
        f"""<tr><td style="padding:6px 0;color:{TEXTO_2};font-size:14px;border-top:1px solid {LINEA};">
        · {_limpiar(d['titular'])} &nbsp;<span style="color:{COLOR_DIR(d['resumen'].get('direccion_pct', 0) or 0)};font-weight:bold;">{_flecha(d['resumen'].get('direccion_pct', 0) or 0)}</span>
        &nbsp;<a href="{BASE_WEB}/?sim={d['sim_id']}" style="color:{TEAL};text-decoration:none;">ver</a>
        </td></tr>"""
        for d in destacadas[1:3]
    )

    voces_html = "".join(
        f"""<p style="margin:8px 0;color:{TEXTO_2};font-size:15px;font-style:italic;line-height:1.4;">
        {_voz(v)}</p>"""
        for v in voces
    )
    signo = '+' if direccion > 0 else ''

    # --- la VOZ del redactor de IA (si la hay); si no, la plantilla ---
    red = (brief or {}).get("redactado") or {}

    buenos_html = ""
    if red.get("buenos_dias"):
        buenos_html = f"""
  <tr><td style="padding:22px 32px 2px;">
    <div style="font-family:Georgia,serif;font-size:24px;font-weight:bold;color:{TEXTO};">☀️ Buenos días</div>
    {_parrafos(red["buenos_dias"])}
  </td></tr>"""

    estrella = red.get("historia_estrella")
    if estrella:
        reaccion_titular = f'{_esc(estrella.get("emoji", ""))} {_esc(estrella["titular"])}'.strip()
        reaccion_cuerpo = _parrafos(estrella["cuerpo"])
    else:
        reaccion_titular = _limpiar(principal['titular'])
        reaccion_cuerpo = (f'<div style="color:{TEXTO_2};font-size:15px;line-height:1.5;">'
                           'En esta simulación educativa, el enjambre de agentes reaccionó al titular '
                           'con el comportamiento de masas que ves arriba.</div>')

    historias_html = "".join(
        f"""<tr><td style="padding:18px 32px 2px;border-top:1px solid {LINEA};">
        <div style="font-family:Georgia,serif;font-size:20px;font-weight:bold;color:{TEXTO};line-height:1.2;">{_esc(h.get("emoji", ""))} {_esc(h["titular"])}</div>
        {_parrafos(h["cuerpo"])}</td></tr>"""
        for h in (red.get("historias") or [])
    )

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{PAPEL};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{PAPEL};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0"
  style="max-width:600px;width:100%;background:{BLANCO};border:1px solid {LINEA};border-radius:8px;">

  <tr><td style="padding:30px 32px 20px;text-align:center;border-bottom:1px solid {LINEA};">
    <div style="font-family:Georgia,serif;font-size:34px;font-weight:bold;color:{ORO};line-height:1;">El Enjambre 🐝</div>
    <div style="font-size:10px;letter-spacing:3px;color:{TEAL};text-transform:uppercase;font-weight:bold;margin-top:10px;">El Pulso · Diario de mercado</div>
    <div style="font-family:Georgia,serif;font-style:italic;font-size:16px;color:{MUTE};margin-top:4px;">{fecha}</div>
    <div style="font-size:11px;color:{MUTE};margin-top:6px;">by <b style="color:{TEXTO_2};">Rubicón Lab</b></div>
  </td></tr>
  {_tabla_mercado(brief)}
  {_bloque_mercado(brief) if not red else ""}
  {buenos_html}

  <tr><td style="padding:22px 32px 4px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">La reacción del día</div>
  </td></tr>

  <tr><td style="padding:8px 32px;">
    <a href="{url_sim}"><img src="{url_img}" width="536" alt="El enjambre reaccionando"
      style="width:100%;max-width:536px;display:block;border:1px solid {LINEA};border-radius:6px;"></a>
  </td></tr>

  <tr><td style="padding:8px 32px;">
    <div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:{TEXTO};line-height:1.25;">
      {reaccion_titular}</div>
    <div style="padding:8px 0;color:{MUTE};font-size:14px;">
      <span style="color:{COLOR_DIR(direccion)};font-weight:bold;">{_flecha(direccion)} {signo}{direccion}%</span> &nbsp;·&nbsp; agitación {agitacion}</div>
    {reaccion_cuerpo}
  </td></tr>

  <tr><td style="padding:12px 32px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">Las voces</div>
    {voces_html}
  </td></tr>
  {historias_html}

  {f'''<tr><td style="padding:8px 32px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">También reaccionó a</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{otras}</table>
  </td></tr>''' if otras else ''}
  {_bloque_observa(brief)}

  <tr><td style="padding:22px 32px;text-align:center;">
    <a href="{url_sim}" style="display:inline-block;background:{ORO};color:#ffffff;
      text-decoration:none;font-weight:bold;font-size:13px;letter-spacing:1px;
      text-transform:uppercase;padding:13px 28px;border-radius:4px;">Ver el enjambre en vivo →</a>
  </td></tr>

  <tr><td style="padding:16px 32px 28px;border-top:1px solid {LINEA};text-align:center;">
    <div style="color:{MUTE};font-size:11px;line-height:1.5;">{DISCLAIMER}</div>
    <div style="margin-top:10px;">
      <a href="{url_baja}" style="color:{TEAL};font-size:11px;">Desuscribirse en un clic</a>
    </div>
  </td></tr>

</table></td></tr></table></body></html>"""


def enviar(destinatario: str, asunto: str, html: str) -> bool:
    """Envía un correo por Resend. False si no hay clave o falla (no lanza)."""
    clave = os.environ.get("RESEND_API_KEY")
    if not clave:
        return False
    try:
        respuesta = httpx.post(
            URL_RESEND,
            headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"},
            json={"from": REMITENTE, "to": [destinatario], "subject": asunto, "html": html},
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


def enviar_a_suscriptores(conexion, preview_html: str, asunto: str) -> dict:
    """Envía la edición YA APROBADA a los suscriptores activos, reemplazando el
    marcador del token de baja por el de cada uno (WYSIWYG con lo revisado)."""
    activos = persistencia.suscriptores_activos(conexion)
    enviados = 0
    for s in activos:
        html = preview_html.replace(persistencia.TOKEN_BAJA_SENTINEL, s["token_baja"])
        if enviar(s["email"], asunto, html):
            enviados += 1
    return {"suscriptores": len(activos), "enviados": enviados, "fallidos": len(activos) - enviados}
