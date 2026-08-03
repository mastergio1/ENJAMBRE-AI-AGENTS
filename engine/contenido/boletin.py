"""El Pulso del Enjambre — la newsletter (CONTENIDO.md sección 6).

Arma el correo diario desde plantilla (HTML de correo: tablas + estilos
inline, ancho 600px, tinta cálida con el teal como acento) y lo envía por Resend.
Todos los textos variables pasan por el filtro de vocabulario CMF antes
de salir. Degradación elegante: sin RESEND_API_KEY, genera el HTML pero
no envía (útil para pruebas y para revisar antes de conectar el dominio).
"""

import html
import os

import httpx

from contenido import persistencia
from contenido.vocabulario import DISCLAIMER, es_publicable

_esc = html.escape

URL_RESEND = "https://api.resend.com/emails"
REMITENTE = os.environ.get("PULSO_REMITENTE", "El Enjambre <pulso@rubiconlab.cl>")
BASE_WEB = os.environ.get("ENJAMBRE_WEB_URL", "https://enjambre.vercel.app")
BASE_API = os.environ.get("ENJAMBRE_API_URL", "https://enjambre-motor.onrender.com")

# paleta oficial del manual de marca (§05)
TINTA = "#1b1916"          # tinta cálida — fondo
TEAL = "#6fa89e"           # el río — acento
CREMA = "#f3eee8"          # crema — texto
CREMA_SUAVE = "#8a867e"    # suave — texto secundario


def _flecha(direccion_pct: float) -> str:
    if direccion_pct > 1.0:
        return "▲"
    if direccion_pct < -1.0:
        return "▼"
    return "◆"


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
    fuente = (f'<a href="{_esc(m["url"])}" style="color:{CREMA_SUAVE};font-size:12px;">·&nbsp;fuente</a>'
              if m.get("url") else "")
    if m.get("tipo") == "evento":
        marca = f'<span style="color:{TEAL};font-weight:bold;">◆</span>'
        cuerpo = _esc(m["titular"])
    else:  # movimiento de precio
        marca = f'<span style="color:{COLOR_DIR(m["variacion_pct"])};font-weight:bold;">{_flecha(m["variacion_pct"])}</span>'
        cuerpo = _esc(m["frase"])
    return f"""<tr><td style="padding:5px 0;color:{CREMA};font-size:14px;line-height:1.45;">
        {marca} {cuerpo} {fuente}</td></tr>"""


def _bloque_mercado(brief: dict | None) -> str:
    """'Lo que pasó en el mercado' — movimientos verificados + eventos del
    día, con su fuente (La Redacción). Dinámico: cambia con las noticias."""
    if not brief or not brief.get("mercado"):
        return ""
    filas = "".join(_fila_mercado(m) for m in brief["mercado"][:5])
    return f"""
  <tr><td style="padding:16px 32px 2px;">
    <div style="font-size:11px;letter-spacing:2px;color:{CREMA_SUAVE};text-transform:uppercase;">Lo que pasó en el mercado</div>
  </td></tr>
  <tr><td style="padding:4px 32px;"><table role="presentation" width="100%">{filas}</table></td></tr>"""


def _bloque_observa(brief: dict | None) -> str:
    """'Qué observa el enjambre hoy' — atención, NUNCA predicción."""
    if not brief or not brief.get("observa"):
        return ""
    filas = "".join(
        f"""<p style="margin:4px 0;color:{CREMA_SUAVE};font-size:14px;">· {_esc(t)}</p>"""
        for t in brief["observa"][:3]
    )
    return f"""
  <tr><td style="padding:14px 32px 4px;border-top:1px solid rgba(243,238,232,0.1);">
    <div style="font-size:11px;letter-spacing:2px;color:{CREMA_SUAVE};text-transform:uppercase;">Qué observa el enjambre hoy</div>
    {filas}</td></tr>"""


def COLOR_DIR(pct: float) -> str:
    return "#8fbfa6" if pct > 0.15 else "#d99a9a" if pct < -0.15 else TEAL


def construir_html(destacadas: list[dict], fecha: str, token_baja: str = "TOKEN",
                   brief: dict | None = None) -> str:
    """El HTML del correo. destacadas: [{titular, sim_id, resumen, lideres}].
    brief (opcional): el análisis de mercado de La Redacción."""
    if not destacadas:
        raise ValueError("no hay simulaciones destacadas para el Pulso")

    principal = destacadas[0]
    resumen = principal["resumen"]
    direccion = resumen.get("direccion_pct", 0) or 0
    agitacion = resumen.get("agitacion") or "medio"

    # las 2 voces más contrastantes (mayor distancia entre señales)
    frases = sorted(principal.get("lideres_frases", []), key=lambda f: f.get("senal", 0))
    voces = []
    if len(frases) >= 2:
        voces = [frases[0], frases[-1]]

    url_sim = f"{BASE_WEB}/?sim={principal['sim_id']}"
    url_img = f"{BASE_API}/api/simulacion/{principal['sim_id']}/imagen"
    url_baja = f"{BASE_API}/api/baja/{token_baja}"

    otras = "".join(
        f"""<tr><td style="padding:6px 0;color:{CREMA_SUAVE};font-size:14px;">
        · {_limpiar(d['titular'])} &nbsp;{_flecha(d['resumen'].get('direccion_pct', 0) or 0)}
        &nbsp;<a href="{BASE_WEB}/?sim={d['sim_id']}" style="color:{TEAL};text-decoration:none;">ver</a>
        </td></tr>"""
        for d in destacadas[1:3]
    )

    voces_html = "".join(
        f"""<p style="margin:8px 0;color:{CREMA};font-size:15px;font-style:italic;line-height:1.4;">
        {_voz(v)}</p>"""
        for v in voces
    )

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{TINTA};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{TINTA};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0"
  style="max-width:600px;width:100%;background:{TINTA};border:1px solid rgba(111,168,158,0.3);">

  <tr><td style="padding:28px 32px 8px;">
    <div style="font-family:Georgia,serif;font-size:26px;font-weight:bold;color:{TEAL};">El Enjambre</div>
    <div style="font-family:Georgia,serif;font-style:italic;font-size:15px;color:{CREMA_SUAVE};">{fecha}</div>
  </td></tr>
  {_bloque_mercado(brief)}

  <tr><td style="padding:16px 32px 4px;">
    <div style="font-size:11px;letter-spacing:2px;color:{CREMA_SUAVE};text-transform:uppercase;">La reacción del día</div>
  </td></tr>

  <tr><td style="padding:8px 32px;">
    <a href="{url_sim}"><img src="{url_img}" width="536" alt="El enjambre reaccionando"
      style="width:100%;max-width:536px;display:block;border:1px solid rgba(111,168,158,0.25);"></a>
  </td></tr>

  <tr><td style="padding:8px 32px;">
    <div style="font-family:Georgia,serif;font-size:21px;font-weight:bold;color:{CREMA};line-height:1.25;">
      {_limpiar(principal['titular'])}</div>
    <div style="padding:8px 0;color:{CREMA_SUAVE};font-size:14px;">
      {_flecha(direccion)} {'+' if direccion > 0 else ''}{direccion}% &nbsp;·&nbsp; agitación {agitacion}</div>
    <div style="color:{CREMA};font-size:15px;line-height:1.5;">
      En esta simulación educativa, el enjambre de agentes reaccionó al titular con el
      comportamiento de masas que ves arriba.</div>
  </td></tr>

  <tr><td style="padding:12px 32px;">
    <div style="font-size:11px;letter-spacing:2px;color:{CREMA_SUAVE};text-transform:uppercase;">Las voces</div>
    {voces_html}
  </td></tr>

  {f'''<tr><td style="padding:8px 32px;">
    <div style="font-size:11px;letter-spacing:2px;color:{CREMA_SUAVE};text-transform:uppercase;">También reaccionó a</div>
    <table role="presentation" width="100%">{otras}</table>
  </td></tr>''' if otras else ''}
  {_bloque_observa(brief)}

  <tr><td style="padding:20px 32px;">
    <a href="{url_sim}" style="display:inline-block;background:{TEAL};color:{TINTA};
      text-decoration:none;font-weight:bold;font-size:14px;letter-spacing:1px;
      text-transform:uppercase;padding:12px 24px;">Ver el enjambre en vivo →</a>
  </td></tr>

  <tr><td style="padding:16px 32px 28px;border-top:1px solid rgba(243,238,232,0.1);">
    <div style="color:{CREMA_SUAVE};font-size:11px;line-height:1.5;">{DISCLAIMER}</div>
    <div style="margin-top:10px;">
      <a href="{url_baja}" style="color:{CREMA_SUAVE};font-size:11px;">Desuscribirse en un clic</a>
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
    html = f"""<!doctype html><html><body style="margin:0;background:{TINTA};">
<table role="presentation" width="100%" style="background:{TINTA};"><tr><td align="center" style="padding:32px;">
<table role="presentation" width="600" style="max-width:600px;background:{TINTA};border:1px solid rgba(111,168,158,0.3);">
  <tr><td style="padding:32px;">
    <div style="font-family:Georgia,serif;font-size:26px;color:{TEAL};font-weight:bold;">El Enjambre</div>
    <p style="color:{CREMA};font-size:16px;line-height:1.5;">Confirma tu suscripción a <b>El Pulso</b>,
      el correo diario donde el enjambre simulado reacciona a los titulares del día.</p>
    <a href="{url}" style="display:inline-block;background:{TEAL};color:{TINTA};text-decoration:none;
      font-weight:bold;padding:12px 24px;text-transform:uppercase;letter-spacing:1px;">Confirmar suscripción</a>
    <p style="color:{CREMA_SUAVE};font-size:12px;margin-top:18px;">
      Si no fuiste tú, ignora este correo y no recibirás nada más.</p>
    <p style="color:{CREMA_SUAVE};font-size:11px;">{DISCLAIMER}</p>
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
