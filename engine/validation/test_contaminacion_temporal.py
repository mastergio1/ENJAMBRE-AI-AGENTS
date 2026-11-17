"""Tests del experimento de contaminación temporal (Fase 0). Puro, sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import contaminacion_temporal as ct


def _fila(anio, senal, pct, mercado="indice"):
    return {"fecha": f"{anio}-06-01", "anio": anio, "mercado": mercado,
            "direccion_pct": pct, "senal": senal, "pct_corr": pct}


def test_acc_senal_cuenta_bien_la_direccion():
    # 3 aciertos (mismo signo) y 1 fallo → 75%
    filas = [_fila(2020, 0.5, 2.0), _fila(2020, -0.5, -2.0),
             _fila(2020, 0.5, 1.0), _fila(2020, 0.5, -1.0)]
    acc, n = ct.acc_senal(filas)
    assert n == 4 and acc == 75.0


def test_acc_senal_filtra_por_zona_y_corte():
    filas = [_fila(2020, 0.4, 2.0),    # cuenta (|pct|≥0.3, |señal|≥0.3)
             _fila(2020, 0.1, 2.0),    # |señal|<0.3 → fuera con corte 0.3
             _fila(2020, 0.4, 0.1)]    # |pct|<0.3 → no direccionable
    assert ct.acc_senal(filas, corte_senal=0.3)[1] == 1
    assert ct.acc_senal(filas, corte_senal=0.0)[1] == 2  # el de |pct|<0.3 sigue fuera


def test_particionar_por_era():
    filas = [_fila(2019, 0.5, 1), _fila(2024, 0.5, 1), _fila(2026, 0.5, 1)]
    eras = ct.particionar_por_era(filas)
    assert len(eras["viejas"]) == 1 and len(eras["medio"]) == 1 and len(eras["recientes"]) == 1


def test_resumen_detecta_contaminacion_sintetica():
    # viejas: todas aciertan (memoria perfecta); recientes: azar (50%)
    viejas = [_fila(2019, 0.5, 2.0) for _ in range(10)]          # 100% acierto
    recientes = ([_fila(2026, 0.5, 2.0) for _ in range(5)] +      # aciertan
                 [_fila(2026, 0.5, -2.0) for _ in range(5)])      # fallan → 50%
    res = ct.resumen_contaminacion(viejas + recientes, "indice")
    assert res["viejas"]["acierto_senal"] == 100.0
    assert res["recientes"]["acierto_senal"] == 50.0


def test_recolectar_con_fecha_usa_fetch_inyectado(tmp_path):
    # un caso histórico de índice; fetch mockeado devuelve barras que suben
    caso = {"origen": "historico", "simbolos": "^GSPC", "mercado": "indice",
            "direccion_pct": 1.0, "senales_arquetipo": {"macro_trader": {"senal_media": 0.5, "n": 1}},
            "reaccion_real": {"simbolo": "^GSPC", "fecha_base": "2020-03-02", "ruedas": 2}}
    ruta = tmp_path / "cal.json"
    ruta.write_text('{"casos": [%s]}' % __import__("json").dumps(caso))

    def fake_fetch(sim, fb):
        # barras: día base y dos ruedas después subiendo
        return [("2020-03-02", 100.0), ("2020-03-03", 101.0),
                ("2020-03-04", 102.0), ("2020-03-05", 103.0)]

    filas = ct.recolectar_con_fecha(str(ruta), fetch=fake_fetch, pausa=0)
    assert len(filas) == 1
    assert filas[0]["anio"] == 2020 and filas[0]["mercado"] == "indice"
    assert filas[0]["pct_corr"] > 0  # subió después del titular
