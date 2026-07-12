"""Tests de La Redacción: el análisis de mercado del Pulso.

Reglas de oro que estos tests protegen:
- el número manda (viene de la capa de datos, no de un texto)
- nada se publica sin fuente / sin pasar el filtro CMF
- se cuenta el pasado, nunca se predice el futuro
"""

import pytest

from contenido import boletin, persistencia, redaccion
from contenido.fuentes import barchart
from contenido.vocabulario import DISCLAIMER, es_publicable, verificar_pieza


@pytest.fixture(autouse=True)
def sin_claves(monkeypatch, tmp_path):
    monkeypatch.delenv("BARCHART_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


NOTICIAS = [
    {"titular": "Nvidia beats earnings expectations, revenue up 48%", "fuente": "demo",
     "url": "https://x/nvda", "simbolos": "NVDA", "fecha": "2026-07-10"},
    {"titular": "Oil jumps 6% as tensions escalate in the Strait of Hormuz", "fuente": "demo",
     "url": "https://x/oil", "simbolos": "USO,XOM", "fecha": "2026-07-10"},
    {"titular": "Top 5 stocks to watch this week", "fuente": "demo",
     "url": "", "simbolos": "", "fecha": "2026-07-10"},
    {"titular": "Should you buy the dip in tech stocks?", "fuente": "demo",
     "url": "", "simbolos": "QQQ", "fecha": "2026-07-10"},
]


# ---------- la capa de datos ----------

def test_barchart_degrada_a_demo():
    assert barchart.hay_credenciales() is False
    cotizaciones, origen = barchart.cotizaciones()
    assert origen == "demo"
    assert len(cotizaciones) >= 4
    for c in cotizaciones:
        assert isinstance(c["variacion_pct"], (int, float))
        assert c["nombre"]


# ---------- el reportero: nada sin fuente, no cita publicidad ----------

def test_reportero_casa_hechos_con_su_cita():
    cotizaciones = [
        {"simbolo": "NVDA", "nombre": "Nvidia", "variacion_pct": 3.4},
        {"simbolo": "CLZ25", "nombre": "Petróleo WTI", "variacion_pct": 2.1},
    ]
    hechos = redaccion.reportear(cotizaciones, NOTICIAS)
    assert hechos[0]["cita"]["titular"].startswith("Nvidia beats")
    assert "hormuz" in hechos[1]["cita"]["titular"].lower()


def test_reportero_no_usa_publicidad_como_cita():
    # el Nasdaq solo tiene titulares promocionales/advisory disponibles
    cotizaciones = [{"simbolo": "$IUXX", "nombre": "Nasdaq 100", "variacion_pct": -0.9}]
    hechos = redaccion.reportear(cotizaciones, NOTICIAS)
    assert hechos[0]["cita"] is None  # "Top 5" y "Should you buy" quedan fuera


# ---------- el verificador: el número manda, descarta el ruido ----------

def test_verificador_descarta_movimientos_insignificantes():
    hechos = [
        {"nombre": "Apple", "variacion_pct": 0.1, "cita": None},   # ruido
        {"nombre": "Nvidia", "variacion_pct": 3.4, "cita": None},  # noticia
    ]
    verificados = redaccion.verificar(hechos)
    assert len(verificados) == 1
    assert verificados[0]["nombre"] == "Nvidia"


# ---------- el editor: pasado, con fuente, CMF-limpio ----------

def test_editor_redacta_en_pasado_y_publicable():
    hecho = {"nombre": "Petróleo WTI", "variacion_pct": 2.1,
             "cita": {"titular": "Oil jumps 6% in the Strait of Hormuz", "fuente": "demo", "url": "u"}}
    linea = redaccion.editar(hecho)
    assert "avanzó 2.1%" in linea["frase"]
    assert "En la prensa" in linea["frase"]
    assert es_publicable(linea["frase"])


def test_editor_cae_la_causa_si_el_titular_no_es_publicable():
    hecho = {"nombre": "Nasdaq 100", "variacion_pct": -1.2,
             "cita": {"titular": "3 reasons you should buy now", "fuente": "x", "url": ""}}
    linea = redaccion.editar(hecho)
    # conserva la cifra verificada, pero descarta el 'por qué' prohibido
    assert linea is not None
    assert "En la prensa" not in linea["frase"]
    assert es_publicable(linea["frase"])


# ---------- el brief completo ----------

def test_brief_del_dia():
    brief = redaccion.preparar_brief(radar=["La Fed decide tasas hoy"])
    assert brief["origen_datos"] == "demo"
    assert brief["mercado"]
    for m in brief["mercado"]:
        assert es_publicable(m["frase"])
        assert isinstance(m["variacion_pct"], (int, float))  # el número, siempre
    assert brief["observa"] == ["La Fed decide tasas hoy"]


def test_brief_es_dinamico_segun_las_noticias_del_dia():
    """El corazón del requisito: el contenido cambia con lo que pasa cada día."""
    dia_a = [{"titular": "Amazon to acquire logistics startup for 4.2 billion",
              "fuente": "x", "url": "", "simbolos": "AMZN", "impacto": 8}]
    dia_b = [{"titular": "Major cyberattack disrupts operations at three US banks",
              "fuente": "x", "url": "", "simbolos": "JPM,BAC", "impacto": 9}]
    texto_a = " ".join(m["frase"] for m in redaccion.preparar_brief(evaluadas=dia_a)["mercado"])
    texto_b = " ".join(m["frase"] for m in redaccion.preparar_brief(evaluadas=dia_b)["mercado"])
    assert "Amazon" in texto_a and "Amazon" not in texto_b
    assert "cyberattack" in texto_b and "cyberattack" not in texto_a


def test_eventos_entran_como_hechos_con_fuente():
    evaluadas = [{"titular": "Amazon to acquire logistics startup for 4.2 billion",
                  "fuente": "reuters", "url": "https://x", "simbolos": "AMZN", "impacto": 8}]
    brief = redaccion.preparar_brief(evaluadas=evaluadas)
    eventos = [m for m in brief["mercado"] if m["tipo"] == "evento"]
    assert any("acquire" in e["titular"] for e in eventos)
    for e in eventos:
        assert es_publicable(e["frase"])  # nada prohibido, ni número inventado


def test_evento_no_duplica_una_cita_ya_usada():
    # el mismo titular que explica un movimiento no se repite como evento
    evaluadas = [{"titular": "Nvidia beats earnings expectations", "fuente": "x",
                  "url": "", "simbolos": "NVDA", "impacto": 8}]
    brief = redaccion.preparar_brief(evaluadas=evaluadas)
    titulares = [m.get("titular") for m in brief["mercado"] if m["tipo"] == "evento"]
    assert "Nvidia beats earnings expectations" not in titulares


def test_observa_es_atencion_no_prediccion():
    # un 'radar' con vocabulario de predicción se filtra
    brief = redaccion.preparar_brief(radar=["El precio subirá mañana", "La Fed decide hoy"])
    assert "El precio subirá mañana" not in brief["observa"]
    assert "La Fed decide hoy" in brief["observa"]


# ---------- el correo con el análisis de mercado ----------

def test_correo_con_brief_es_cmf_limpio_y_lleva_disclaimer():
    brief = redaccion.preparar_brief(radar=["La Fed decide hoy"])
    destacadas = [{
        "sim_id": "abc1230000000000", "titular": "Quiebra un banco",
        "resumen": {"direccion_pct": -3.0, "agitacion": "medio"},
        "lideres_frases": [{"arquetipo": "doomer", "senal": -0.8, "frase": "Lo advertí."},
                           {"arquetipo": "institucional_frio", "senal": 0.1, "frase": "Sin impacto."}],
    }]
    html = boletin.construir_html(destacadas, "domingo 12 de julio", brief=brief)
    assert "Lo que pasó en el mercado" in html
    assert "Qué observa el enjambre hoy" in html
    assert DISCLAIMER in html
    assert verificar_pieza(html) == []  # sin vocabulario prohibido, con disclaimer


# ---------- persistencia del brief ----------

def test_brief_se_guarda_y_se_lee():
    conexion = persistencia.conectar()
    brief = {"mercado": [{"nombre": "Oro", "variacion_pct": -0.9, "frase": "Oro retrocedió 0.9%."}],
             "observa": ["La Fed"], "origen_datos": "demo"}
    persistencia.guardar_brief(conexion, "2026-07-12", brief)
    leido = persistencia.obtener_brief(conexion, "2026-07-12")
    assert leido["mercado"][0]["nombre"] == "Oro"
    assert leido["aprobado"] is False
    assert persistencia.aprobar_brief(conexion, "2026-07-12") is True
    assert persistencia.obtener_brief(conexion, "2026-07-12")["aprobado"] is True
    conexion.close()
