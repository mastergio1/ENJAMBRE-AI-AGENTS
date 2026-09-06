"""El RESUMEN DE LA SEMANA de El Pulso — la edición del sábado.

Entre semana El Pulso cuenta el día; el sábado mira la semana entera con punto de
vista: los grandes temas, el porqué de cada cosa, cómo la geopolítica y la macro
movieron el mercado, y —siempre bajo el candado CMF— QUÉ OBSERVAR de aquí en
adelante (atención, jamás una predicción).

Este módulo solo junta los HECHOS (el número manda: los movimientos semanales
vienen de Yahoo; los temas, de los titulares que el motor destacó esta semana).
La voz la pone redaccion_ia.redactar_resumen; el correo lo dibuja boletin.
Degradación elegante: sin titulares de la semana devuelve None y el sábado cae a
lo que haya. NUNCA lanza.
"""

from datetime import datetime, timedelta, timezone

from contenido import persistencia
from contenido.fuentes import yahoo

# el telón de fondo del resumen: índices y materias primas SIEMPRE relevantes.
TELON = ["^GSPC", "^IXIC", "^DJI", "CL=F", "GC=F"]
DIAS_SEMANA = 7        # ventana de "la semana"
MAX_TITULARES = 12     # cuántos temas de la semana se le pasan al redactor


def titulares_de_la_semana(conexion, cuando: dict | None = None,
                           dias: int = DIAS_SEMANA, maximo: int = MAX_TITULARES) -> list[dict]:
    """Los titulares que el motor DESTACÓ en los últimos `dias` días: la columna
    vertebral del resumen (las noticias que de verdad importaron). Deduplicados,
    más recientes primero."""
    hoy = (persistencia.ahora_iso() if cuando is None else _iso_de(cuando))[:10]
    limite = _fecha_menos(hoy, dias)
    vistos, salida = set(), []
    for fila in persistencia.listar_simulaciones(conexion, solo_destacadas=True, limite=60):
        fecha = fila["fecha"][:10]
        if fecha < limite or fecha > hoy:
            continue
        clave = fila["titular"].strip().lower()
        if clave in vistos:
            continue
        vistos.add(clave)
        salida.append({"titular": fila["titular"], "fecha": fecha})
        if len(salida) >= maximo:
            break
    return salida


def foto_semana(fetch=yahoo.serie_reciente) -> list[dict]:
    """'La semana en números': el movimiento SEMANAL (~5 ruedas) de los índices y
    materias primas del telón. Solo los que Yahoo responde; nunca lanza."""
    foto = []
    for simbolo in TELON:
        serie = fetch(simbolo, rango="5d", intervalo="1d")
        if not serie:
            continue
        _fechas, cierres = serie
        if len(cierres) < 2 or not cierres[0]:
            continue
        var = round((cierres[-1] - cierres[0]) / cierres[0] * 100, 2)
        foto.append({"simbolo": simbolo, "nombre": yahoo.NOMBRES.get(simbolo, simbolo),
                     "var_semana_pct": var})
    return foto


def preparar_resumen(conexion=None, cuando: dict | None = None,
                     fetch=yahoo.serie_reciente) -> dict | None:
    """Arma los HECHOS del resumen del sábado: los temas de la semana (titulares
    destacados) + la foto semanal del mercado. None si no hubo temas (nada que
    resumir → el sábado cae a lo que haya)."""
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        titulares = titulares_de_la_semana(conexion, cuando)
    finally:
        if propia:
            conexion.close()
    if not titulares:
        return None
    return {"titulo": "El Pulso de la semana", "titulares": titulares, "foto": foto_semana(fetch)}


# ---------- utilidades de fecha ----------

def _iso_de(cuando: dict) -> str:
    """Convierte el 'cuando' inyectado (con fecha 'D de mes de AAAA') a AAAA-MM-DD.
    Si no se puede, cae a hoy (el resumen no se cae por esto)."""
    from contenido.redaccion_ia import _MESES
    try:
        partes = cuando.get("fecha", "").split(" de ")
        dia, mes, ano = int(partes[0]), _MESES.index(partes[1]) + 1, int(partes[2])
        return f"{ano:04d}-{mes:02d}-{dia:02d}"
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _fecha_menos(iso: str, dias: int) -> str:
    try:
        return (datetime.fromisoformat(iso) - timedelta(days=dias)).strftime("%Y-%m-%d")
    except Exception:
        return "0000-00-00"
