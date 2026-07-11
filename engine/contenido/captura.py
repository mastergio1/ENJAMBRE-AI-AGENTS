"""Captura del "momento dramático" de una simulación (CONTENIDO.md paso 4).

Genera un PNG 1200×630 editorial (Rubicón Lab: tinta + dorado) con el
titular, la dirección, el nivel de agitación, la curva de precio con el
tick de máxima agitación marcado, el disclaimer y la marca de agua.
Sirve de portada del correo y de Open Graph image de la página.

Se dibuja en 2D con Pillow — sin GL headless, funciona en el plan free.
Un render 3D real del enjambre es una mejora futura, no de hoy.
"""

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from contenido.vocabulario import DISCLAIMER

TINTA = (11, 14, 20)
DORADO = (201, 162, 39)
MARFIL = (244, 239, 230)
MARFIL_SUAVE = (244, 239, 230, 150)
COMPRA = (79, 174, 127)
VENTA = (196, 71, 42)
NEUTRO = (110, 98, 80)

ANCHO, ALTO = 1200, 630
MARGEN = 70


def _fuente(tamano: int, negrita: bool = False):
    """Busca una fuente del sistema; si no hay, la de Pillow (siempre existe)."""
    candidatas = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if negrita
        else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
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


def _envolver(texto: str, fuente, dibujo, ancho_max: int) -> list[str]:
    palabras = texto.split()
    lineas, actual = [], ""
    for palabra in palabras:
        prueba = f"{actual} {palabra}".strip()
        if dibujo.textlength(prueba, font=fuente) <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas[:3]


def _color_direccion(direccion_pct: float):
    if direccion_pct > 1.0:
        return COMPRA
    if direccion_pct < -1.0:
        return VENTA
    return DORADO


def generar_png(titular: str, resumen: dict, serie_precios: list[float]) -> bytes:
    """Devuelve el PNG del momento dramático como bytes."""
    imagen = Image.new("RGB", (ANCHO, ALTO), TINTA)
    dibujo = ImageDraw.Draw(imagen)

    # marco dorado sutil
    dibujo.rectangle([12, 12, ANCHO - 12, ALTO - 12], outline=DORADO, width=1)

    # cabecera: marca
    dibujo.text((MARGEN, 46), "EL ENJAMBRE", font=_fuente(26, negrita=True), fill=DORADO)
    dibujo.text((MARGEN, 82), "el focus group sintético del mercado",
                font=_fuente(16), fill=MARFIL_SUAVE[:3])

    # titular (hasta 3 líneas)
    fuente_titular = _fuente(40, negrita=True)
    lineas = _envolver(titular, fuente_titular, dibujo, ANCHO - 2 * MARGEN)
    y = 150
    for linea in lineas:
        dibujo.text((MARGEN, y), linea, font=fuente_titular, fill=MARFIL)
        y += 52

    # cifras: dirección y agitación
    direccion = resumen.get("direccion_pct", 0) or 0
    agitacion = resumen.get("agitacion") or _nivel(resumen.get("volatilidad_pct", 0))
    y_cifras = 360
    flecha = "▲" if direccion > 1 else "▼" if direccion < -1 else "◆"
    texto_dir = f"{flecha} {'+' if direccion > 0 else ''}{direccion}%"
    dibujo.text((MARGEN, y_cifras), texto_dir, font=_fuente(46, negrita=True),
                fill=_color_direccion(direccion))
    dibujo.text((MARGEN, y_cifras + 62), f"agitación {agitacion}",
                font=_fuente(18), fill=MARFIL_SUAVE[:3])

    # curva de precio con el tick más dramático marcado
    _dibujar_curva(dibujo, serie_precios, x0=560, y0=340, ancho=560, alto=180)

    # disclaimer CMF + marca de agua
    dibujo.text((MARGEN, ALTO - 76), DISCLAIMER, font=_fuente(13), fill=MARFIL_SUAVE[:3])
    marca = "El Enjambre · Rubicón Lab"
    fuente_marca = _fuente(15)
    ancho_marca = dibujo.textlength(marca, font=fuente_marca)
    dibujo.text((ANCHO - MARGEN - ancho_marca, ALTO - 44), marca, font=fuente_marca, fill=DORADO)

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()


def _nivel(volatilidad_pct: float) -> str:
    if volatilidad_pct < 1.0:
        return "bajo"
    if volatilidad_pct < 2.0:
        return "medio"
    return "alto"


def _dibujar_curva(dibujo, serie, x0, y0, ancho, alto) -> None:
    if not serie or len(serie) < 2:
        return
    minimo, maximo = min(serie), max(serie)
    rango = max(maximo - minimo, 0.5)
    puntos = []
    for i, valor in enumerate(serie):
        x = x0 + (i / (len(serie) - 1)) * ancho
        y = y0 + alto - ((valor - minimo) / rango) * alto
        puntos.append((x, y))
    # línea base tenue
    dibujo.line([(x0, y0 + alto), (x0 + ancho, y0 + alto)], fill=(60, 55, 45), width=1)
    dibujo.line(puntos, fill=DORADO, width=3, joint="curve")
    # marca el tick de máxima caída (el momento dramático)
    idx = serie.index(minimo)
    px, py = puntos[idx]
    dibujo.ellipse([px - 6, py - 6, px + 6, py + 6], fill=VENTA)


def guardar_png(ruta: Path, contenido: bytes) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)
