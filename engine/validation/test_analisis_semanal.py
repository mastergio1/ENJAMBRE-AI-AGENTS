"""Tests de la EDICIÓN DE FIN DE SEMANA de El Pulso (deep-dive mid-cap/sector).

Reglas de oro que protegen:
- el número manda (la variación viene de Yahoo, no de un texto);
- contexto primero + debate de arquetipos (miradas contrastantes);
- NUNCA consejo de inversión: "lo que nuestros inversionistas IA ven/analizan";
- nada se publica sin pasar el filtro CMF y sin escapar el HTML.
"""

from datetime import datetime, timedelta

from contenido import analisis_semanal, boletin, redaccion_ia
from contenido.vocabulario import DISCLAIMER, verificar_pieza


# ---------- helpers ----------

def _serie(precios, dias=None):
    base = datetime(2026, 8, 1)
    fechas = [base + timedelta(days=i) for i in range(len(precios))]
    return fechas, [float(p) for p in precios]


def _fetch_fake(mapa):
    """Devuelve un fetch(simbolo, rango, intervalo) que lee de un mapa
    símbolo→lista de precios (o None para simular que Yahoo no responde)."""
    def fetch(simbolo, rango="1mo", intervalo="1d"):
        precios = mapa.get(simbolo)
        return _serie(precios) if precios else None
    return fetch


def _sin_fundamentales(_ticker):
    """fetch_fund que no trae ficha (Yahoo caído): el deep-dive sale sin números."""
    return None


# ---------- el universo curado ----------

def test_universo_carga_y_tiene_contexto():
    u = analisis_semanal.cargar_universo()
    assert u.get("acciones") and u.get("sectores")
    for a in u["acciones"]:
        assert a["ticker"] and a["nombre"] and a["contexto"]
        assert a["banda"] in ("1-15B", "15-30B")  # mediana capitalización
    for s in u["sectores"]:
        assert s["nombre"] and s["etf"] and s["contexto"]


# ---------- la rotación de modo ----------

def test_modo_alterna_por_semana():
    assert analisis_semanal.elegir_modo(semana_iso=2) == "accion"
    assert analisis_semanal.elegir_modo(semana_iso=3) == "sector"


# ---------- la selección por ATENCIÓN (el número manda) ----------

def test_selecciona_la_accion_de_mayor_movida():
    universo = {"acciones": [
        {"ticker": "AAA", "nombre": "Alfa", "banda": "1-15B", "sector": "X", "contexto": "..."},
        {"ticker": "BBB", "nombre": "Beta", "banda": "15-30B", "sector": "Y", "contexto": "..."},
    ]}
    # AAA sube ~2% en el mes; BBB se dispara ~30% → BBB es la de mayor atención
    fetch = _fetch_fake({
        "AAA": [100, 100.5, 101, 101.5, 102, 102],
        "BBB": [100, 105, 110, 120, 128, 130],
    })
    sel = analisis_semanal.seleccionar_accion(universo, fetch=fetch, fetch_fund=_sin_fundamentales)
    assert sel["ticker"] == "BBB"
    assert sel["modo"] == "accion"
    assert sel["encuadre"] == "mediana capitalización"
    assert isinstance(sel["var_semana_pct"], (int, float))
    assert sel["grafico"]["ticker"] == "BBB"
    assert sel["fundamentales"] is None  # Yahoo no dio ficha → sin números, sin romperse


def test_band_gate_excluye_los_muy_grandes_y_adjunta_fundamentales():
    """La franja manda: el mayor movedor puede quedar FUERA si su capitalización
    real supera ~20B; se elige el siguiente EN banda y se le adjunta su ficha."""
    universo = {"acciones": [
        {"ticker": "BIG", "nombre": "Gigante", "banda": "15-30B", "sector": "X", "contexto": "c"},
        {"ticker": "MID", "nombre": "Media", "banda": "1-15B", "sector": "Y", "contexto": "c"},
    ]}
    fetch = _fetch_fake({
        "BIG": [100, 120, 140, 160, 180, 200],   # movida enorme, pero es gigante
        "MID": [50, 51, 52, 53, 54, 55],          # movida menor, pero en banda
    })
    fichas = {
        "BIG": {"market_cap_num": 25_000_000_000, "ingresos": "40B"},
        "MID": {"market_cap_num": 8_000_000_000, "ingresos": "2B", "ebitda": "300M"},
    }
    sel = analisis_semanal.seleccionar_accion(universo, fetch=fetch, fetch_fund=lambda t: fichas.get(t))
    assert sel["ticker"] == "MID"                 # BIG excluido por capitalización
    assert sel["fundamentales"]["ebitda"] == "300M"


def test_selecciona_el_sector_de_mayor_movida():
    universo = {"sectores": [
        {"nombre": "Energía", "etf": "XLE", "contexto": "...", "ejemplos": ["XOM"]},
        {"nombre": "Bancos", "etf": "KRE", "contexto": "...", "ejemplos": ["FITB"]},
    ]}
    fetch = _fetch_fake({
        "XLE": [50, 50.2, 50.1, 50.3, 50.4, 50.5],
        "KRE": [50, 47, 45, 43, 42, 41],  # cae fuerte → rotación
    })
    sel = analisis_semanal.seleccionar_sector(universo, fetch=fetch)
    assert sel["ticker"] == "KRE"
    assert sel["modo"] == "sector"
    assert sel["nombre"] == "Bancos"


def test_preparar_cae_al_otro_modo_si_el_elegido_no_tiene_datos():
    universo = {
        "acciones": [{"ticker": "AAA", "nombre": "Alfa", "banda": "1-15B", "sector": "X", "contexto": "c"}],
        "sectores": [{"nombre": "Energía", "etf": "XLE", "contexto": "c"}],
    }
    # se fuerza 'sector' pero XLE no trae datos → cae a 'accion' (AAA sí trae)
    fetch = _fetch_fake({"AAA": [10, 11, 12, 13, 14, 15]})
    sel = analisis_semanal.preparar_analisis(universo, modo="sector", fetch=fetch,
                                             fetch_fund=_sin_fundamentales)
    assert sel is not None and sel["modo"] == "accion"


def test_preparar_none_si_no_hay_datos():
    universo = {"acciones": [{"ticker": "AAA", "nombre": "Alfa", "banda": "1-15B",
                              "sector": "X", "contexto": "c"}], "sectores": []}
    fetch = _fetch_fake({})  # Yahoo no responde para nada
    assert analisis_semanal.preparar_analisis(universo, modo="accion", fetch=fetch,
                                              fetch_fund=_sin_fundamentales) is None


# ---------- el filtro CMF sobre el deep-dive redactado ----------

def test_validar_analisis_filtra_debate_no_publicable():
    datos = {
        "titular": "Roku, la plataforma que vive de la publicidad",
        "dek": "Una mirada de fin de semana",
        "contexto": "Roku fabrica el sistema de sus televisores.\n\nGana con publicidad.",
        "lectura": "Subió fuerte esta semana.",
        "debate": [
            {"arquetipo": "doomer", "mirada": "deberías vender todo ya"},   # prohibido → fuera
            {"arquetipo": "inexistente", "mirada": "hola"},                 # arquetipo inválido → fuera
            {"arquetipo": "contrarian_sabio", "mirada": "El pánico ajeno se observa con calma."},
        ],
        "que_observar": "Habrá que ver la próxima temporada de resultados.",
    }
    val = redaccion_ia._validar_analisis(datos)
    assert val is not None
    ids = [d["arquetipo"] for d in val["debate"]]
    assert ids == ["contrarian_sabio"]
    assert val["debate"][0]["nombre"]  # trae el nombre legible del arquetipo


def test_validar_analisis_none_si_titular_prohibido():
    datos = {"titular": "deberías comprar Roku ahora", "contexto": "algo"}
    assert redaccion_ia._validar_analisis(datos) is None


# ---------- el correo de fin de semana ----------

def _brief_finde():
    hechos = {
        "modo": "accion", "titulo": "Acción seleccionada", "encuadre": "mediana capitalización",
        "ticker": "ROKU", "nombre": "Roku", "sector": "Streaming",
        "contexto": "...", "var_semana_pct": 8.4, "var_mes_pct": 12.0,
        "fecha_inicio": "1 ago", "fecha_fin": "31 ago",
        "fundamentales": {"market_cap": "9.5B", "ingresos": "4.2B",
                          "crecimiento_ingresos": "18.00%", "margen_bruto": "45.00%",
                          "ebitda": "300M", "deuda": "500M", "caja": "2.1B"},
        "grafico": {"ticker": "ROKU", "nombre": "Roku", "periodo": "mes", "moneda": "$"},
    }
    red = {
        "titular": "Roku vuelve a la conversación",
        "dek": "La plataforma de TV conectada tuvo una semana movida",
        "contexto": "Roku hace el sistema operativo de televisores.\n\nGana con publicidad.",
        "lectura": "Esta semana avanzó con fuerza tras un anuncio.",
        "numeros": "Crece 18% al año.\n\nEBITDA positivo y más caja que deuda: un colchón cómodo.",
        "debate": [
            {"arquetipo": "fomo_evangelista", "nombre": "El FOMO Evangelista",
             "mirada": "¡La TV conectada es el futuro y aquí está pasando!"},
            {"arquetipo": "doomer", "nombre": "El Doomer",
             "mirada": "La publicidad es lo primero que se recorta en una crisis."},
        ],
        "que_observar": "Habrá que ver si la publicidad digital sostiene el ritmo.",
    }
    return {"analisis": hechos, "analisis_redactado": red}


def test_correo_finde_es_deep_dive_cmf_limpio():
    html = boletin.construir_html([], "sábado 16 de agosto", brief=_brief_finde())
    # la edición de fin de semana y su encuadre
    assert "Edición de fin de semana" in html
    assert "Qué es" in html                       # contexto primero
    assert "Lo que ven nuestros inversionistas IA" in html   # el debate
    assert "no es asesoría de inversión" in html.lower()
    assert "El FOMO Evangelista" in html and "El Doomer" in html
    assert "/api/grafico/ROKU" in html            # gráfico real del protagonista
    # 'Los números': la ficha de fundamentales (datos de mercado) + la lectura
    assert "Los números" in html
    assert "EBITDA" in html and "300M" in html and "4.2B" in html
    assert "Crecimiento ingresos" in html and "18.00%" in html
    assert "Yahoo Finance" in html                # la ficha va atribuida a su fuente
    # El Enjambre al pie + disclaimer, como siempre
    assert "También de Rubicón Lab" in html
    assert DISCLAIMER in html
    assert verificar_pieza(html) == []            # sin vocabulario prohibido


def test_correo_finde_escapa_html_hostil():
    brief = _brief_finde()
    brief["analisis_redactado"]["debate"][0]["mirada"] = "<script>alert(1)</script> mira esto"
    html = boletin.construir_html([], "sábado 16 de agosto", brief=brief)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_correo_finde_omite_las_historias_diarias():
    brief = _brief_finde()
    # aunque llegue una historia diaria, el fin de semana NO la muestra
    brief["redactado"] = {"historias": [{"titular": "Historia diaria colada",
                                         "cuerpo": "no debería salir"}]}
    html = boletin.construir_html([], "sábado 16 de agosto", brief=brief)
    assert "Historia diaria colada" not in html


def test_asunto_finde():
    asunto = boletin.asunto_finde({"titulo": "Sector en rotación", "nombre": "Energía"})
    assert "Sector en rotación" in asunto and "Energía" in asunto
