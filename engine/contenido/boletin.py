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
    """'La foto del día' — movimientos verificados + eventos, con su fuente."""
    if not brief or not brief.get("mercado"):
        return ""
    filas = "".join(_fila_mercado(m) for m in brief["mercado"][:5])
    return f"""
  <tr><td style="padding:18px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">La foto del día</div>
  </td></tr>
  <tr><td style="padding:4px 32px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{filas}</table></td></tr>"""


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
  {_bloque_mercado(brief)}

  <tr><td style="padding:22px 32px 4px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">La reacción del día</div>
  </td></tr>

  <tr><td style="padding:8px 32px;">
    <a href="{url_sim}"><img src="{url_img}" width="536" alt="El enjambre reaccionando"
      style="width:100%;max-width:536px;display:block;border:1px solid {LINEA};border-radius:6px;"></a>
  </td></tr>

  <tr><td style="padding:8px 32px;">
    <div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:{TEXTO};line-height:1.25;">
      {_limpiar(principal['titular'])}</div>
    <div style="padding:8px 0;color:{MUTE};font-size:14px;">
      <span style="color:{COLOR_DIR(direccion)};font-weight:bold;">{_flecha(direccion)} {signo}{direccion}%</span> &nbsp;·&nbsp; agitación {agitacion}</div>
    <div style="color:{TEXTO_2};font-size:15px;line-height:1.5;">
      En esta simulación educativa, el enjambre de agentes reaccionó al titular con el
      comportamiento de masas que ves arriba.</div>
  </td></tr>

  <tr><td style="padding:12px 32px;">
    <div style="font-size:11px;letter-spacing:2px;color:{MUTE};text-transform:uppercase;font-weight:600;">Las voces</div>
    {voces_html}
  </td></tr>

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
