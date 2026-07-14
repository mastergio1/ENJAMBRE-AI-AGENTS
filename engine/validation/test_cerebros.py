"""Tests de los cerebros LLM (CLAUDE.md sección 5).

Corren SIN clave de API: prueban el fallback léxico, la validación del
JSON, la caché y el criterio de la Etapa 2 — que un titular real cambie
el comportamiento del enjambre. La ruta con API real usa el mismo código
con la única diferencia de la fuente de la respuesta.
"""

import statistics

import pytest

import brains.cerebro as cerebro
from brains.arquetipos import ARQUETIPOS
from brains.cerebro import _validar_respuesta, analizar_titular
from model import MercadoEnjambre

TITULAR_NEGATIVO = "Quiebra el segundo banco más grande del país; pánico en los mercados"
TITULAR_POSITIVO = "La bolsa alcanza un máximo histórico tras ganancias récord"


@pytest.fixture(autouse=True)
def entorno_sin_api(monkeypatch, tmp_path):
    """Sin clave de API y con caché desechable: los tests nunca llaman afuera."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")


def _cien_lideres() -> list[tuple[int, str]]:
    consultas = []
    indice = 0
    for arquetipo in ARQUETIPOS:
        for _ in range(arquetipo["cantidad"]):
            consultas.append((indice, arquetipo["id"]))
            indice += 1
    return consultas


def test_fallback_responde_por_los_100_lideres():
    respuestas = analizar_titular(TITULAR_NEGATIVO, _cien_lideres())
    assert len(respuestas) == 100
    for r in respuestas:
        assert -1.0 <= r["senal"] <= 1.0
        assert 0.0 <= r["confianza"] <= 1.0
        assert r["frase"]
        assert r["fuente"] == "fallback"


def test_los_arquetipos_tienen_personalidad():
    """Ante la misma noticia negativa, cada arquetipo reacciona a su manera."""
    respuestas = analizar_titular(TITULAR_NEGATIVO, _cien_lideres())
    por_arquetipo: dict[str, list[float]] = {}
    for (_, arq), r in zip(_cien_lideres(), respuestas):
        por_arquetipo.setdefault(arq, []).append(r["senal"])
    medias = {a: statistics.mean(s) for a, s in por_arquetipo.items()}

    assert medias["doomer"] < -0.5                    # ve el colapso confirmado
    assert medias["fomo_evangelista"] < -0.5          # amplifica el pánico
    assert medias["influencer_optimista"] > 0.1       # "las caídas son descuentos"
    assert medias["contrarian_sabio"] > 0.2           # compra la sangre
    assert abs(medias["institucional_frio"]) < 0.55   # nunca extremo


def test_cache_guarda_la_api_pero_no_el_fallback():
    """El fallback NO se cachea: una falla pasajera de la API no debe congelar
    frases enlatadas para siempre. La voz real de la IA sí se cachea."""
    import json

    from brains.cerebro import _clave_cache

    # sin API, la segunda corrida vuelve a intentar (fuente = fallback, no cache)…
    primera = analizar_titular(TITULAR_NEGATIVO, _cien_lideres())
    segunda = analizar_titular(TITULAR_NEGATIVO, _cien_lideres())
    assert all(r["fuente"] == "fallback" for r in segunda)
    # …pero el fallback es determinístico por semilla: mismos valores
    assert [r["senal"] for r in primera] == [r["senal"] for r in segunda]

    # una respuesta de API pre-sembrada en el caché sí se reutiliza
    clave = _clave_cache(TITULAR_NEGATIVO, "doomer", 0)
    cerebro.RUTA_CACHE.parent.mkdir(parents=True, exist_ok=True)
    cerebro.RUTA_CACHE.write_text(
        json.dumps({clave: {"senal": -0.8, "confianza": 0.9, "frase": "voz real"}}),
        encoding="utf-8",
    )
    respuesta = analizar_titular(TITULAR_NEGATIVO, [(0, "doomer")])[0]
    assert respuesta["fuente"] == "cache"
    assert respuesta["frase"] == "voz real"


def test_validacion_del_json_del_llm():
    assert _validar_respuesta('{"senal": 0.5, "confianza": 0.8, "frase": "ok"}') is not None
    # señal fuera de rango se recorta a [-1, 1]
    assert _validar_respuesta('{"senal": 7, "confianza": 0.8, "frase": "x"}')["senal"] == 1.0
    # JSON roto, campos faltantes o tipos malos → None (dispara el fallback)
    assert _validar_respuesta("no soy json") is None
    assert _validar_respuesta('{"senal": "alta", "confianza": 1, "frase": "x"}') is None
    assert _validar_respuesta('{"senal": 0.2, "confianza": 0.5}') is None
    # el JSON envuelto en texto se extrae igual
    envuelto = 'Claro: {"senal": -0.3, "confianza": 0.6, "frase": "ok"} listo'
    assert _validar_respuesta(envuelto)["senal"] == -0.3


def test_etapa2_un_titular_cambia_el_enjambre():
    """El criterio de la Etapa 2: el mismo mercado, con la misma semilla,
    se comporta distinto según el titular que lee."""

    def precio_final(titular: str, seed: int) -> float:
        m = MercadoEnjambre(seed=seed, ticks_horizonte=200)
        m.correr(80)
        base = m.historial_precios[-1]
        m.aplicar_titular(titular)
        m.correr(60)
        return m.historial_precios[-1] / base

    semillas = [1, 2]
    negativos = [precio_final(TITULAR_NEGATIVO, s) for s in semillas]
    positivos = [precio_final(TITULAR_POSITIVO, s) for s in semillas]
    assert statistics.mean(negativos) < statistics.mean(positivos)
    assert statistics.mean(negativos) < 1.0  # la quiebra bancaria golpea
