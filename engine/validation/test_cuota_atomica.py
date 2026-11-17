"""Reserva ATÓMICA del cupo global (auditoría 4.2): bajo concurrencia, el gasto
registrado nunca supera el tope. Antes el chequeo y el incremento eran dos pasos
(carrera check-then-increment); ahora son una sola sentencia bajo el candado de
escritura de SQLite."""
import os
import sys
import threading

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from contenido import limites, persistencia


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    persistencia._inicializadas.clear()
    limites.reiniciar()
    yield
    limites.reiniciar()


def test_reservar_respeta_el_tope_secuencial():
    conexion = persistencia.conectar()
    try:
        # tope 3: las 3 primeras reservan, la 4ª no
        assert persistencia.reservar_gasto_dia(conexion, "2026-11-17", 3) is True
        assert persistencia.reservar_gasto_dia(conexion, "2026-11-17", 3) is True
        assert persistencia.reservar_gasto_dia(conexion, "2026-11-17", 3) is True
        assert persistencia.reservar_gasto_dia(conexion, "2026-11-17", 3) is False
        assert persistencia.gasto_dia(conexion, "2026-11-17") == 3
    finally:
        conexion.close()


def test_reservar_no_crea_fila_si_no_cabe_ni_el_primero():
    conexion = persistencia.conectar()
    try:
        assert persistencia.reservar_gasto_dia(conexion, "2026-11-17", 0) is False
        assert persistencia.gasto_dia(conexion, "2026-11-17") == 0  # sin fila sobre el tope
    finally:
        conexion.close()


def test_concurrencia_nunca_supera_el_presupuesto(monkeypatch):
    """20 peticiones simultáneas (dispositivos distintos) contra un tope global de
    5: exactamente 5 pasan, nunca 6. Cada hilo usa su propia conexión."""
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "5")
    monkeypatch.setenv("ENJAMBRE_SIM_DIA_GRATIS", "1")

    permitidos = []
    lock = threading.Lock()
    barrera = threading.Barrier(20)

    def intentar(i):
        barrera.wait()  # todos arrancan a la vez → máxima contención
        ok, _ = limites.permitir(ip=f"10.0.0.{i}", cliente_id=f"dev-{i}")
        if ok:
            with lock:
                permitidos.append(i)

    hilos = [threading.Thread(target=intentar, args=(i,)) for i in range(20)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    assert len(permitidos) == 5, f"pasaron {len(permitidos)}, debían ser 5"
    conexion = persistencia.conectar()
    try:
        from datetime import date
        assert persistencia.gasto_dia(conexion, date.today().isoformat()) == 5
    finally:
        conexion.close()
