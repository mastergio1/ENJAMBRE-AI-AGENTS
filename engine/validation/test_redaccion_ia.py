"""Tests del redactor de IA de El Pulso — los candados sin llamar a la API.

Prueban que: sin clave hay fallback (None), el filtro CMF cae los párrafos
prohibidos pero conserva los limpios, y la validación arma bien la estructura.
Ninguno gasta una llamada a Anthropic.
"""

from datetime import datetime, timezone

from contenido import redaccion_ia


def test_contexto_temporal_sabado_de_manana():
    """El 8 de agosto de 2026 es sábado; 13:00 UTC ≈ mañana en Chile."""
    momento = datetime(2026, 8, 8, 13, 0, tzinfo=timezone.utc)
    ctx = redaccion_ia.contexto_temporal(momento)
    assert ctx["dia_semana"] == "sábado"
    assert ctx["es_finde"] is True
    assert "8 de agosto de 2026" in ctx["fecha"]
    assert ctx["momento"] in ("mañana", "madrugada")  # según horario de verano/invierno


def test_momentos_del_dia():
    assert redaccion_ia._momento(3) == "madrugada"
    assert redaccion_ia._momento(9) == "mañana"
    assert redaccion_ia._momento(15) == "tarde"
    assert redaccion_ia._momento(22) == "noche"


def test_mensaje_incluye_dia_fecha_y_momento():
    """El redactor recibe el día/fecha/momento como hecho — no los adivina."""
    brief = {"mercado": [{"nombre": "Nvidia", "variacion_pct": 3.4}]}
    cuando = {"dia_semana": "miércoles", "fecha": "5 de agosto de 2026",
              "momento": "mañana", "es_finde": False}
    msg = redaccion_ia._mensaje_del_dia(brief, None, cuando)
    assert "miércoles" in msg
    assert "5 de agosto de 2026" in msg
    assert "mañana" in msg


def test_mensaje_marca_fin_de_semana():
    brief = {"mercado": [{"nombre": "Nvidia", "variacion_pct": 3.4}]}
    cuando = {"dia_semana": "sábado", "fecha": "8 de agosto de 2026",
              "momento": "mañana", "es_finde": True}
    msg = redaccion_ia._mensaje_del_dia(brief, None, cuando)
    assert "FIN DE SEMANA" in msg


def test_sin_clave_cae_al_fallback(monkeypatch):
    """Sin ANTHROPIC_API_KEY, redactar() devuelve None (el boletín usa plantilla)."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    brief = {"mercado": [{"nombre": "Nvidia", "variacion_pct": 3.4}]}
    assert redaccion_ia.redactar(brief) is None


def test_sin_hechos_no_redacta(monkeypatch):
    """Con clave pero sin hechos ni enjambre, no hay nada que redactar → None."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-falsa")
    assert redaccion_ia.redactar({"mercado": []}) is None


def test_cmf_cae_parrafo_prohibido_conserva_limpio():
    """El filtro CMF descarta el párrafo con vocabulario prohibido y deja el limpio."""
    texto = ("Nvidia avanzó 3,4% y volvió a ser el engreído del salón.\n\n"
             "Es una oportunidad de compra clarísima para ti.")  # este cruza la CMF
    limpio = redaccion_ia._cmf(texto)
    assert limpio is not None
    assert "engreído del salón" in limpio
    assert "oportunidad de compra" not in limpio


def test_cmf_todo_prohibido_devuelve_none():
    assert redaccion_ia._cmf("Recomendamos comprar ahora sin pensarlo.") is None


def test_validar_sanea_y_arma_estructura():
    """Una respuesta de IA (simulada) se valida: conserva lo limpio, cae lo
    que cruza la CMF, y arma la forma final."""
    datos = {
        "buenos_dias": ("Wall Street amaneció en verde.\n\n"
                        "Deberias comprar ya mismo."),   # 2º párrafo cae
        "historia_estrella": {
            "emoji": "🩸",
            "titular": "Insulet vendió más y aun así la castigaron",
            "cuerpo": "Recortó su previsión.\n\nEl enjambre se hundió 6%.",
        },
        "historias": [
            {"emoji": "🟢", "titular": "Nvidia subió", "cuerpo": "Los chips mandan."},
            {"emoji": "⚠️", "titular": "Compra ahora esta acción", "cuerpo": "x"},  # titular prohibido → cae
        ],
    }
    salida = redaccion_ia._validar(datos)
    assert salida is not None
    assert "amaneció en verde" in salida["buenos_dias"]
    assert "comprar ya mismo" not in salida["buenos_dias"]
    assert salida["historia_estrella"]["titular"].startswith("Insulet")
    # solo la historia limpia sobrevive (la de "Compra ahora" se cae)
    assert len(salida["historias"]) == 1
    assert salida["historias"][0]["titular"] == "Nvidia subió"


def test_validar_sin_apertura_ni_estrella_es_none():
    """Si no queda ni apertura ni historia estrella, no hay diario → None."""
    datos = {"buenos_dias": "Recomendamos comprar.", "historia_estrella": None, "historias": []}
    assert redaccion_ia._validar(datos) is None


def test_extraer_json_desde_texto_envuelto():
    crudo = 'Claro, aquí tienes:\n{"buenos_dias": "Hola", "historias": []}\n¡Listo!'
    datos = redaccion_ia._extraer_json(crudo)
    assert datos is not None and datos["buenos_dias"] == "Hola"


def test_mensaje_del_dia_no_filtra_numeros():
    """El mensaje que ve la IA lleva los números tal cual (para copiarlos, no inventarlos)."""
    brief = {"mercado": [{"nombre": "Nvidia", "variacion_pct": 3.4}]}
    enjambre = {"titular": "Insulet recorta su previsión", "direccion_pct": -6.1}
    msg = redaccion_ia._mensaje_del_dia(brief, enjambre)
    assert "3.4%" in msg
    assert "-6.1%" in msg
    assert "Insulet recorta su previsión" in msg
