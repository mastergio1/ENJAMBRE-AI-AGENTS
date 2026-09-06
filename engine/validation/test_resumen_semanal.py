"""Tests del RESUMEN DE LA SEMANA de El Pulso (edición del sábado).

Reglas de oro que protegen:
- los temas salen de las noticias que importaron (destacadas de la semana);
- los números semanales vienen de Yahoo (el número manda);
- punto de vista sobre lo que YA pasó SÍ, predicción JAMÁS (CMF);
- nada se publica sin pasar el filtro CMF ni sin escapar el HTML.
"""

from datetime import datetime, timedelta

from contenido import boletin, redaccion_ia, resumen_semanal
from contenido.vocabulario import DISCLAIMER, verificar_pieza

CUANDO = {"dia_semana": "sábado", "weekday": 5, "fecha": "15 de agosto de 2026",
          "momento": "mañana", "es_finde": True}


# ---------- los temas: ventana de la semana + dedup ----------

def test_titulares_de_la_semana_filtra_ventana_y_dedup(monkeypatch):
    filas = [
        {"titular": "Tema A", "fecha": "2026-08-14T10:00:00"},
        {"titular": "tema a", "fecha": "2026-08-13T10:00:00"},   # duplicado (case)
        {"titular": "Muy viejo", "fecha": "2026-08-01T10:00:00"},  # fuera de la ventana
        {"titular": "Tema B", "fecha": "2026-08-12T10:00:00"},
    ]
    monkeypatch.setattr(resumen_semanal.persistencia, "listar_simulaciones",
                        lambda *a, **k: filas)
    out = resumen_semanal.titulares_de_la_semana(conexion=object(), cuando=CUANDO)
    assert [t["titular"] for t in out] == ["Tema A", "Tema B"]


# ---------- la foto semanal: el número manda ----------

def _fetch_fake(mapa):
    def fetch(simbolo, rango="5d", intervalo="1d"):
        precios = mapa.get(simbolo)
        if not precios:
            return None
        base = datetime(2026, 8, 11)
        fechas = [base + timedelta(days=i) for i in range(len(precios))]
        return fechas, [float(p) for p in precios]
    return fetch


def test_foto_semana_calcula_variacion_semanal():
    fetch = _fetch_fake({"^GSPC": [100, 101, 102, 103, 104], "CL=F": [80, 78, 77, 76, 75]})
    foto = resumen_semanal.foto_semana(fetch=fetch)
    por_simbolo = {f["simbolo"]: f for f in foto}
    assert por_simbolo["^GSPC"]["var_semana_pct"] == 4.0
    assert por_simbolo["CL=F"]["var_semana_pct"] == -6.25
    assert por_simbolo["^GSPC"]["nombre"] == "S&P 500"


def test_preparar_resumen_none_sin_temas(monkeypatch):
    monkeypatch.setattr(resumen_semanal.persistencia, "listar_simulaciones", lambda *a, **k: [])
    assert resumen_semanal.preparar_resumen(conexion=object(), cuando=CUANDO,
                                            fetch=_fetch_fake({})) is None


# ---------- el filtro CMF sobre el resumen redactado ----------

def test_validar_resumen_filtra_prediccion_y_recomendacion():
    datos = {
        "intro": "Semana de nervios.\n\nEl precio subirá con fuerza la próxima semana.",  # 2º cae (predicción)
        "temas": [
            {"kicker": "Macro", "emoji": "🏦", "titular": "La Fed marcó el tono",
             "analisis": "Subió el tono.\n\nEl mercado lo leyó como cautela.",
             "que_observar": "Habrá que ver la próxima acta.", "grafico": None},
            {"titular": "Deberías comprar ya", "analisis": "x"},   # titular prohibido → cae
        ],
        "cierre": "Una semana para respirar.",
    }
    val = redaccion_ia._validar_resumen(datos)
    assert val is not None
    assert "subirá con fuerza" not in val["intro"]     # la predicción cayó
    assert "Semana de nervios" in val["intro"]
    assert len(val["temas"]) == 1                       # el tema prohibido cayó
    assert val["temas"][0]["titular"] == "La Fed marcó el tono"


# ---------- el correo del sábado ----------

def _brief_resumen():
    hechos = {"titulo": "El Pulso de la semana",
              "titulares": [{"titular": "x", "fecha": "2026-08-12"}],
              "foto": [{"simbolo": "^GSPC", "nombre": "S&P 500", "var_semana_pct": 1.8},
                       {"simbolo": "CL=F", "nombre": "Petróleo WTI", "var_semana_pct": -3.2}]}
    red = {"intro": "Semana de nervios.\n\nLa Fed en el centro.",
           "temas": [
               {"kicker": "Macro · la Fed", "emoji": "🏦", "titular": "La Fed volvió a ser el personaje",
                "analisis": "Subió el tono.\n\nEl mercado lo leyó como cautela.",
                "que_observar": "Habrá que ver la próxima acta.",
                "grafico": {"ticker": "^GSPC", "nombre": "S&P 500", "periodo": "semana", "moneda": "$"}},
               {"kicker": "Geopolítica · petróleo", "emoji": "🛢️", "titular": "El crudo cedió",
                "analisis": "Bajó la tensión.\n\nMenos prima de riesgo.",
                "que_observar": "Atento a la OPEP.", "grafico": None},
           ],
           "cierre": "Una semana para respirar."}
    return {"resumen": hechos, "resumen_redactado": red}


def test_correo_resumen_es_cmf_limpio():
    html = boletin.construir_html([], "sábado 15 de agosto", brief=_brief_resumen())
    assert "El Pulso de la semana" in html
    assert "La semana en números" in html
    assert "La Fed volvió a ser el personaje" in html and "El crudo cedió" in html
    assert "Qué observar" in html
    assert "También de Rubicón Lab" in html          # el pie del Enjambre, como siempre
    assert DISCLAIMER in html
    assert verificar_pieza(html) == []


def test_correo_resumen_escapa_html_hostil():
    brief = _brief_resumen()
    brief["resumen_redactado"]["temas"][0]["analisis"] = "<script>alert(1)</script> ojo"
    html = boletin.construir_html([], "sábado 15 de agosto", brief=brief)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_asunto_resumen():
    assert "semana" in boletin.asunto_resumen().lower()
