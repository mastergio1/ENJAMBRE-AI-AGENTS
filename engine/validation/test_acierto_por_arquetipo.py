"""Tests del acierto direccional por arquetipo (Fase 2 groundwork). Sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import acierto_por_arquetipo as apa


def _caso(simbolo, fecha, senales, mercado="indice"):
    return {"origen": "historico", "simbolos": simbolo, "mercado": mercado,
            "senales_arquetipo": {a: {"senal_media": s, "n": 1} for a, s in senales.items()},
            "reaccion_real": {"simbolo": simbolo, "fecha_base": fecha}}


def test_mapa_resultados():
    filas = [{"simbolo": "^GSPC", "fecha": "2020-01-01", "pct_corr": 2.0},
             {"simbolo": "^GSPC", "fecha": "2020-02-01", "pct_corr": None}]  # se omite
    m = apa.mapa_resultados(filas)
    assert m == {("^GSPC", "2020-01-01"): 2.0}


def test_arquetipo_que_acierta_y_otro_que_falla():
    # dos casos de índice; "bueno" siempre acierta, "malo" siempre falla
    casos = [_caso("^GSPC", "2020-01-01", {"macro_trader": 0.5, "doomer": -0.5}),
             _caso("^GSPC", "2020-02-01", {"macro_trader": -0.5, "doomer": -0.5})]
    pcmap = {("^GSPC", "2020-01-01"): 2.0,   # subió
             ("^GSPC", "2020-02-01"): -2.0}  # bajó
    res = apa.acierto_por_arquetipo(casos, pcmap, "indice",
                                    arqs=["macro_trader", "doomer"])
    assert res["macro_trader"]["acierto"] == 100.0 and res["macro_trader"]["n"] == 2
    assert res["doomer"]["acierto"] == 50.0 and res["doomer"]["n"] == 2  # acierta solo la baja


def test_filtra_por_zona_y_corte_y_cero():
    casos = [_caso("^GSPC", "2020-01-01", {"macro_trader": 0.1, "value_paciente": 0.0})]
    pcmap = {("^GSPC", "2020-01-01"): 2.0}
    # corte 0.3 excluye la señal 0.1; la señal 0.0 nunca cuenta
    res = apa.acierto_por_arquetipo(casos, pcmap, "indice",
                                    arqs=["macro_trader", "value_paciente"], corte=0.3)
    assert res["macro_trader"]["n"] == 0 and res["value_paciente"]["n"] == 0
    res2 = apa.acierto_por_arquetipo(casos, pcmap, "indice", arqs=["macro_trader"], corte=0.0)
    assert res2["macro_trader"]["n"] == 1


def test_mercado_no_directionable_se_omite():
    # movimiento por debajo de zona → no cuenta
    casos = [_caso("^GSPC", "2020-01-01", {"macro_trader": 0.5})]
    pcmap = {("^GSPC", "2020-01-01"): 0.1}
    res = apa.acierto_por_arquetipo(casos, pcmap, "indice", arqs=["macro_trader"])
    assert res["macro_trader"]["n"] == 0
