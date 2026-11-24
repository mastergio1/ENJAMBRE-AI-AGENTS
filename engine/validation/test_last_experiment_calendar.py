"""L2 — Tests del calendario NYSE y disponibilidad (contrato temporal I.3)."""
import datetime as dt

from research.last_experiment import calendar as cal


def test_viernes_es_sesion():
    assert cal.es_sesion(dt.date(2026, 1, 9))  # viernes normal


def test_fin_de_semana_no_es_sesion():
    assert not cal.es_sesion(dt.date(2026, 1, 10))  # sábado
    assert not cal.es_sesion(dt.date(2026, 1, 11))  # domingo


def test_festivo_no_es_sesion():
    assert not cal.es_sesion(dt.date(2026, 1, 1))   # Año Nuevo
    assert dt.date(2026, 4, 3) in cal.festivos(2026)  # Viernes Santo
    assert not cal.es_sesion(dt.date(2026, 11, 26))  # Thanksgiving


def test_media_sesion_cierra_antes():
    d = dt.date(2026, 11, 27)  # viernes post Thanksgiving
    assert cal.es_media_sesion(d)
    s = cal.sesion(d)
    # cierre 13:00 ET -> cutoff 12:30 ET = 17:30 UTC (EST)
    assert s.cutoff_utc.strftime("%H:%M") == "17:30"


def test_dst_cutoff_cambia_con_horario():
    # invierno (EST = UTC-5): 15:30 ET -> 20:30 UTC
    assert cal.sesion(dt.date(2026, 1, 5)).cutoff_utc.strftime("%H:%M") == "20:30"
    # verano (EDT = UTC-4): 15:30 ET -> 19:30 UTC
    assert cal.sesion(dt.date(2026, 7, 6)).cutoff_utc.strftime("%H:%M") == "19:30"


def test_cutoff_y_deadline_son_aware():
    s = cal.sesion(dt.date(2026, 3, 16))
    assert s.cutoff_utc.tzinfo is not None
    assert (s.deadline_utc - s.cutoff_utc) == dt.timedelta(minutes=10)


def test_contrato_evento_salta_festivos():
    # emisión jueves antes de un lunes festivo: entrada y salida saltan el festivo
    c = cal.contrato_evento(dt.date(2026, 1, 16))  # viernes
    assert c["entrada_sesion"] == "2026-01-20"  # 19 (MLK) es festivo
    assert c["salida_sesion"] == "2026-01-22"


def test_label_no_madura_antes_del_cierre():
    c = cal.contrato_evento(dt.date(2026, 1, 9))
    cierre = dt.datetime.fromisoformat(c["label_available_after_utc"])
    assert not cal.label_madura(c, cierre)                       # justo en el cierre: no
    assert cal.label_madura(c, cierre + dt.timedelta(hours=1))   # 1h después: sí


def test_publicacion_futura_no_disponible():
    s = cal.sesion(dt.date(2026, 2, 17))
    futuro = s.cutoff_utc + dt.timedelta(minutes=1)
    assert not cal.disponible_al_cutoff(futuro, s.cutoff_utc)
    assert cal.disponible_al_cutoff(s.cutoff_utc, s.cutoff_utc)


def test_avanzar_sesiones_cuenta_bursatiles():
    # 2 sesiones desde el viernes 2026-01-09 = martes 2026-01-13 (lunes 12 es sesión)
    assert cal.avanzar_sesiones(dt.date(2026, 1, 9), 2) == dt.date(2026, 1, 13)
