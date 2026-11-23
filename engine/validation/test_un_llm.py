"""Tests de A2 (un LLM neutral). Sin red: la llamada a la API va inyectada."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import un_llm


def _correr(titulares, respuestas, cache=None):
    async def obtener(t):
        return respuestas[t]
    return asyncio.run(un_llm.senales_async(titulares, obtener, cache=cache))


def test_parsea_y_recorta_la_senal():
    r = {"T1": '{"senal": 0.7, "confianza": 0.8, "frase": "sube"}',
         "T2": '{"senal": 2.5, "confianza": 0.9, "frase": "tope"}'}  # fuera de rango
    out = _correr(["T1", "T2"], r)
    assert out["T1"] == 0.7
    assert out["T2"] == 1.0  # recortada a [-1,1]


def test_no_repite_lo_cacheado():
    llamados = []
    async def obtener(t):
        llamados.append(t)
        return '{"senal": -0.3, "confianza": 0.5, "frase": "x"}'
    out = asyncio.run(un_llm.senales_async(
        ["A", "B"], obtener, cache={"A": 0.9}))
    assert out["A"] == 0.9 and out["B"] == -0.3
    assert llamados == ["B"]  # A no se volvió a consultar


def test_titular_que_falla_no_cae_la_corrida():
    r = {"OK": '{"senal": 0.4, "confianza": 0.6, "frase": "ok"}',
         "MAL": "esto no es json"}
    out = _correr(["OK", "MAL"], r)
    assert out["OK"] == 0.4 and "MAL" not in out  # el malo se omite, el bueno queda


def test_titulares_unicos_en_orden():
    filas = [{"titular": "X"}, {"titular": "Y"}, {"titular": "X"}, {"sin": 1}]
    assert un_llm.titulares_de(filas) == ["X", "Y"]


def test_a2_entra_en_la_escalera(tmp_path):
    from calibration import ablacion
    cf = tmp_path / "cf.json"
    cf.write_text(json.dumps([
        {"pct_corr": 2.0, "senal": 0.5, "direccion_pct": 0.5, "simbolo": "SPY",
         "fecha": "2020-01-01", "anio": 2020, "mercado": "indice"},
        {"pct_corr": -2.0, "senal": -0.5, "direccion_pct": -0.5, "simbolo": "QQQ",
         "fecha": "2020-01-02", "anio": 2020, "mercado": "indice"},
    ]))
    # a2 se adjunta por titular; sin raw, inyectamos titular a mano
    filas = ablacion.cargar(str(cf))
    filas[0]["titular"] = "t1"; filas[1]["titular"] = "t2"
    filas[0]["a2"] = 0.9; filas[1]["a2"] = 0.9  # A2 acierta la 1ª, falla la 2ª
    res = ablacion.evaluar(filas, n_boot=200)
    assert res["A2_un_llm"]["punto"] == 50.0
