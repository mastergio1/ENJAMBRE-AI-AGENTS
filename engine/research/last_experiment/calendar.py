"""L2 — Calendario NYSE y tiempos UTC (sin dependencias externas).

Implementa el contrato temporal exacto (Parte I.3) sin `pandas_market_calendars`:
sesiones regulares, festivos oficiales, medias sesiones, DST (vía zoneinfo),
cutoff = cierre − 30 min, deadline = cutoff + 10 min, todo en UTC *aware*.

El calendario es la FUENTE DE VERDAD de qué es una sesión válida, cuándo madura una
etiqueta y qué datos están disponibles al cutoff. Nunca sumar días naturales: se
cuentan sesiones bursátiles por identificador de sesión (la fecha local de NYSE).

Reglas de disponibilidad (F08/F13): una barra/etiqueta solo está disponible cuando su
sesión ha cerrado definitivamente (barra marcada final), no por número de barras ni
por días naturales transcurridos.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

# Minutos antes del cierre para el cutoff de información (I.3) y margen de emisión.
CUTOFF_ANTES_CIERRE_MIN = 30
DEADLINE_DESPUES_CUTOFF_MIN = 10

CIERRE_NORMAL = dt.time(16, 0)      # 16:00 ET
CIERRE_MEDIA_SESION = dt.time(13, 0)  # 13:00 ET (half day)
APERTURA = dt.time(9, 30)


def _pascua(anio: int) -> dt.date:
    """Domingo de Pascua (algoritmo anónimo gregoriano). Para Viernes Santo."""
    a = anio % 19
    b, c = divmod(anio, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    mes = (h + el - 7 * m + 114) // 31
    dia = ((h + el - 7 * m + 114) % 31) + 1
    return dt.date(anio, mes, dia)


def _nth_weekday(anio: int, mes: int, weekday: int, n: int) -> dt.date:
    """n-ésimo `weekday` (0=lunes) del mes. n negativo = desde el final."""
    if n > 0:
        d = dt.date(anio, mes, 1)
        offset = (weekday - d.weekday()) % 7
        return d + dt.timedelta(days=offset + 7 * (n - 1))
    # último
    if mes == 12:
        ult = dt.date(anio, 12, 31)
    else:
        ult = dt.date(anio, mes + 1, 1) - dt.timedelta(days=1)
    offset = (ult.weekday() - weekday) % 7
    return ult - dt.timedelta(days=offset)


def _observado(d: dt.date) -> dt.date:
    """Regla NYSE: festivo en sábado → viernes previo; en domingo → lunes siguiente."""
    if d.weekday() == 5:  # sábado
        return d - dt.timedelta(days=1)
    if d.weekday() == 6:  # domingo
        return d + dt.timedelta(days=1)
    return d


def festivos(anio: int) -> set[dt.date]:
    """Festivos de cierre total de NYSE para el año (con regla de observancia)."""
    fs: set[dt.date] = set()
    fs.add(_observado(dt.date(anio, 1, 1)))          # Año Nuevo
    fs.add(_nth_weekday(anio, 1, 0, 3))              # MLK (3er lunes enero)
    fs.add(_nth_weekday(anio, 2, 0, 3))              # Washington (3er lunes febrero)
    fs.add(_pascua(anio) - dt.timedelta(days=2))     # Viernes Santo
    fs.add(_nth_weekday(anio, 5, 0, -1))             # Memorial (último lunes mayo)
    if anio >= 2022:
        fs.add(_observado(dt.date(anio, 6, 19)))     # Juneteenth (desde 2022)
    fs.add(_observado(dt.date(anio, 7, 4)))          # Independencia
    fs.add(_nth_weekday(anio, 9, 0, 1))              # Trabajo (1er lunes septiembre)
    fs.add(_nth_weekday(anio, 11, 3, 4))             # Acción de Gracias (4º jueves)
    fs.add(_observado(dt.date(anio, 12, 25)))        # Navidad
    return fs


def medias_sesiones(anio: int) -> set[dt.date]:
    """Medias sesiones NYSE (cierre 13:00 ET): día después de Acción de Gracias,
    víspera de Navidad (24-dic) si cae en día hábil, y 3-jul si cae en día hábil y
    el 4 es festivo laborable."""
    ms: set[dt.date] = set()
    tg = _nth_weekday(anio, 11, 3, 4)
    ms.add(tg + dt.timedelta(days=1))                # viernes post Thanksgiving
    nochebuena = dt.date(anio, 12, 24)
    if nochebuena.weekday() < 5:
        ms.add(nochebuena)
    jul3 = dt.date(anio, 7, 3)
    if jul3.weekday() < 5:
        ms.add(jul3)
    # quitar cualquiera que sea festivo total
    return {d for d in ms if d not in festivos(anio) and d.weekday() < 5}


def es_sesion(d: dt.date) -> bool:
    """¿`d` es una sesión bursátil programada de NYSE?"""
    if d.weekday() >= 5:
        return False
    return d not in festivos(d.year)


def es_media_sesion(d: dt.date) -> bool:
    return es_sesion(d) and d in medias_sesiones(d.year)


def hora_cierre(d: dt.date) -> dt.time:
    return CIERRE_MEDIA_SESION if es_media_sesion(d) else CIERRE_NORMAL


def _ny_a_utc(d: dt.date, t: dt.time) -> dt.datetime:
    """Combina fecha+hora en America/New_York (resuelve DST) y pasa a UTC aware."""
    local = dt.datetime.combine(d, t, tzinfo=NY)
    return local.astimezone(UTC)


@dataclass(frozen=True)
class Sesion:
    """Una sesión bursátil con sus tiempos clave en UTC aware."""
    fecha: dt.date          # identificador de sesión (fecha local NYSE)
    media: bool
    apertura_utc: dt.datetime
    cierre_utc: dt.datetime
    cutoff_utc: dt.datetime
    deadline_utc: dt.datetime

    @property
    def id(self) -> str:
        return self.fecha.isoformat()


def sesion(d: dt.date) -> Sesion:
    """Construye la Sesion de `d`. Lanza ValueError si `d` no es sesión."""
    if not es_sesion(d):
        raise ValueError(f"{d} no es una sesión bursátil de NYSE")
    media = es_media_sesion(d)
    cierre_t = hora_cierre(d)
    cierre = _ny_a_utc(d, cierre_t)
    cutoff = cierre - dt.timedelta(minutes=CUTOFF_ANTES_CIERRE_MIN)
    deadline = cutoff + dt.timedelta(minutes=DEADLINE_DESPUES_CUTOFF_MIN)
    return Sesion(
        fecha=d, media=media,
        apertura_utc=_ny_a_utc(d, APERTURA),
        cierre_utc=cierre, cutoff_utc=cutoff, deadline_utc=deadline,
    )


def siguiente_sesion(d: dt.date) -> dt.date:
    """Primera sesión bursátil estrictamente posterior a `d`."""
    x = d + dt.timedelta(days=1)
    while not es_sesion(x):
        x += dt.timedelta(days=1)
    return x


def sesion_anterior(d: dt.date) -> dt.date:
    x = d - dt.timedelta(days=1)
    while not es_sesion(x):
        x -= dt.timedelta(days=1)
    return x


def avanzar_sesiones(d: dt.date, n: int) -> dt.date:
    """Avanza `n` sesiones bursátiles desde `d` (n>0 hacia el futuro)."""
    x = d
    paso = 1 if n >= 0 else -1
    for _ in range(abs(n)):
        x = siguiente_sesion(x) if paso > 0 else sesion_anterior(x)
    return x


def sesiones_entre(desde: dt.date, hasta: dt.date) -> list[dt.date]:
    """Sesiones bursátiles en [desde, hasta) — cohorte por cutoff dentro de [T0,T1)."""
    out: list[dt.date] = []
    x = desde
    while x < hasta:
        if es_sesion(x):
            out.append(x)
        x += dt.timedelta(days=1)
    return out


def contrato_evento(emision: dt.date, horizonte_sesiones: int = 2) -> dict:
    """Contrato temporal de un evento emitido en la sesión `emision` (I.3).

    - entrada: cierre de la 1ª sesión estrictamente posterior a la emisión.
    - salida: cierre `horizonte_sesiones` sesiones después de la entrada.
    - label_available_at: posterior al cierre de salida (barra final).
    """
    s_em = sesion(emision)
    entrada = siguiente_sesion(emision)
    salida = avanzar_sesiones(entrada, horizonte_sesiones)
    s_sal = sesion(salida)
    return {
        "emision": emision.isoformat(),
        "cutoff_utc": s_em.cutoff_utc.isoformat(),
        "deadline_utc": s_em.deadline_utc.isoformat(),
        "entrada_sesion": entrada.isoformat(),
        "salida_sesion": salida.isoformat(),
        "entrada_cierre_utc": sesion(entrada).cierre_utc.isoformat(),
        "salida_cierre_utc": s_sal.cierre_utc.isoformat(),
        # la etiqueta NO está disponible hasta después del cierre de salida
        "label_available_after_utc": s_sal.cierre_utc.isoformat(),
    }


def label_madura(contrato: dict, ahora_utc: dt.datetime) -> bool:
    """¿La etiqueta del evento ya maduró (cerró la sesión de salida)? (F08/F13)."""
    if ahora_utc.tzinfo is None:
        raise ValueError("ahora_utc debe ser aware (UTC)")
    cierre_salida = dt.datetime.fromisoformat(contrato["label_available_after_utc"])
    return ahora_utc > cierre_salida


def disponible_al_cutoff(published_at_utc: dt.datetime, cutoff_utc: dt.datetime) -> bool:
    """¿Un dato con `published_at` está disponible al cutoff? (prevención de fuga)."""
    if published_at_utc.tzinfo is None or cutoff_utc.tzinfo is None:
        raise ValueError("timestamps deben ser aware (UTC)")
    return published_at_utc <= cutoff_utc
