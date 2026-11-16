"""Tests del cerebro de entrevista (Fase 2) — todo lo que no necesita IA en vivo."""

from brains import entrevista as e


def test_contexto_incluye_titular_senal_y_frase():
    c = e._contexto("La Fed sube tasas", 0.6, "Castiga a growth")
    assert "La Fed sube tasas" in c
    assert "Castiga a growth" in c
    assert "comprar" in c  # senal > 0.1
    assert e._contexto("x", -0.5, "")  # vender
    assert "neutral" in e._contexto("x", 0.0, "")


def test_contexto_tolera_senal_ausente():
    c = e._contexto("Noticia", None, "")
    assert "Noticia" in c and "señal" not in c.lower()


def test_fallback_es_en_personaje_y_cmf():
    f = e._fallback("doomer")
    assert "El Doomer" in f
    assert "simulación" in f.lower()  # recordatorio CMF


def test_fallback_arquetipo_desconocido_no_rompe():
    assert "líder" in e._fallback("no_existe")


def test_mensajes_recorta_historial_y_pregunta():
    historial = [{"rol": "user", "texto": "hola"},
                 {"rol": "assistant", "texto": "qué tal"},
                 {"rol": "otro", "texto": "ignorar"}]  # rol inválido se descarta
    m = e._mensajes("x" * 500, historial)
    assert m[-1]["role"] == "user"
    assert len(m[-1]["content"]) == e.MAX_PREGUNTA  # recortada
    roles = [x["role"] for x in m]
    assert "otro" not in roles  # rol inválido descartado
    assert roles.count("user") >= 1


def test_mensajes_limita_turnos():
    historial = [{"rol": "user", "texto": f"t{i}"} for i in range(20)]
    m = e._mensajes("final", historial)
    # a lo sumo MAX_TURNOS del historial + la pregunta final
    assert len(m) <= e.MAX_TURNOS + 1


def test_entrevistar_sin_api_degrada_a_fallback(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = e.entrevistar("fomo_evangelista", "Bitcoin rompe máximos", "¿por qué?")
    assert r["fuente"] == "fallback"
    assert r["arquetipo"] == "fomo_evangelista"
    assert r["respuesta"]


def test_entrevistar_pregunta_vacia_es_fallback(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    r = e.entrevistar("doomer", "Noticia", "   ")
    assert r["fuente"] == "fallback"
