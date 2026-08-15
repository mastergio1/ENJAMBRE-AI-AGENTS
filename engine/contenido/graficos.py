"""Gráficos de precio REAL para El Pulso (rediseño estilo Moby).

Dibuja un PNG autocontenido —fondo claro, la línea de precio, el nombre del
activo, su variación del período y el precio inicial/final— para incrustar en
el correo. Los datos vienen de Yahoo (contenido/fuentes/yahoo.py); este módulo
solo pinta. Se dibuja en 2D con Pillow (sin GL headless), como captura.py.

Regla de integridad: los números vienen dados (serie real). Este módulo no
inventa nada; si la serie es pobre (< 2 puntos), devuelve None y el correo
simplemente omite el gráfico.
"""

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# paleta CLARA del correo (misma que boletin.py) en RGB
PAPEL = (244, 239, 228)      # #f4efe4 — fondo de la tarjeta del gráfico
BORDE = (231, 222, 208)      # #e7ded0 — hairline
TINTA = (28, 24, 19)         # #1c1813 — texto principal
CUERPO = (58, 53, 44)        # #3a352c
MUTE = (138, 129, 115)       # #8a8173 — secundario
SUBE = (47, 143, 102)        # #2f8f66 — verde
BAJA = (192, 80, 77)         # #c0504d — rojo

# 2x para retina; en el correo se muestra a la mitad (~536 px de ancho)
ANCHO, ALTO = 1072, 480
MARGEN = 44
PAD_LINEA_SUP = 150          # dónde empieza el área de la línea
PAD_LINEA_INF = 100          # margen inferior del área de la línea


def _fuente(tamano: int, negrita: bool = False):
    candidatas = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrita
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for ruta in candidatas:
        if Path(ruta).exists():
            try:
                return ImageFont.truetype(ruta, tamano)
            except OSError:
                continue
    return ImageFont.load_default()


def _limpiar_serie(serie: list) -> list[float]:
    """Descarta huecos (None) que Yahoo deja en días sin cierre."""
    return [float(v) for v in (serie or []) if isinstance(v, (int, float))]


def _fmt_precio(v: float) -> str:
    """1234.5 → '1.234,5' no: mantenemos punto decimal simple estilo mercado US."""
    if v >= 1000:
        return f"{v:,.0f}".replace(",", " ")
    if v >= 1:
        return f"{v:,.2f}"
    return f"{v:.4f}"           # cripto/penny stocks


def generar_grafico(
    nombre: str, ticker: str, serie: list[float], *,
    etiqueta_periodo: str = "última semana",
    fecha_inicio: str = "", fecha_fin: str = "hoy",
    moneda: str = "$",
) -> bytes | None:
    """PNG del gráfico de un activo. None si la serie no alcanza (< 2 puntos)."""
    cierres = _limpiar_serie(serie)
    if len(cierres) < 2:
        return None

    inicio, fin = cierres[0], cierres[-1]
    sube = fin >= inicio
    color = SUBE if sube else BAJA
    delta = fin - inicio
    pct = (delta / inicio * 100) if inicio else 0.0
    signo = "+" if delta >= 0 else "−"
    cambio_txt = (f"{signo}{moneda}{_fmt_precio(abs(delta))} "
                  f"({signo}{abs(pct):.1f}%) · {etiqueta_periodo}")

    imagen = Image.new("RGB", (ANCHO, ALTO), PAPEL)
    d = ImageDraw.Draw(imagen)
    d.rounded_rectangle([2, 2, ANCHO - 2, ALTO - 2], radius=20, outline=BORDE, width=2)

    # ── cabecera: nombre · ticker  (izq)   ·   variación (der) ──
    f_nom = _fuente(30, negrita=True)
    d.text((MARGEN, 40), f"{nombre} · {ticker}", font=f_nom, fill=TINTA)
    f_chg = _fuente(27, negrita=True)
    anc = d.textlength(cambio_txt, font=f_chg)
    d.text((ANCHO - MARGEN - anc, 44), cambio_txt, font=f_chg, fill=color)

    # ── la línea de precio ──
    x0, x1 = MARGEN, ANCHO - MARGEN
    y0, y1 = PAD_LINEA_SUP, ALTO - PAD_LINEA_INF
    lo, hi = min(cierres), max(cierres)
    rango = max(hi - lo, 1e-9)
    n = len(cierres)
    pts = []
    for i, v in enumerate(cierres):
        x = x0 + (i / (n - 1)) * (x1 - x0)
        y = y1 - ((v - lo) / rango) * (y1 - y0)
        pts.append((x, y))

    # área tenue bajo la línea (relleno del color, muy suave)
    poligono = pts + [(x1, y1), (x0, y1)]
    capa = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    ImageDraw.Draw(capa).polygon(poligono, fill=color + (28,))
    imagen.paste(Image.alpha_composite(imagen.convert("RGBA"), capa).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(imagen)

    d.line(pts, fill=color, width=5, joint="curve")
    ex, ey = pts[-1]
    d.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=color)

    # ── pie: precio inicial (izq)  ·  precio final (der, resaltado) ──
    f_eje = _fuente(21)
    izq = f"{moneda}{_fmt_precio(inicio)}" + (f" · {fecha_inicio}" if fecha_inicio else "")
    d.text((MARGEN, ALTO - 58), izq, font=f_eje, fill=MUTE)
    f_fin = _fuente(22, negrita=True)
    der = f"{moneda}{_fmt_precio(fin)} · {fecha_fin}"
    anc_der = d.textlength(der, font=f_fin)
    d.text((ANCHO - MARGEN - anc_der, ALTO - 59), der, font=f_fin, fill=color)

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()
