"""Tests del reportero IA: investiga y verifica el porqué de los movimientos."""

import pytest

from contenido import investigador

MOVER = {"ticker": "MRNA", "nombre": "Moderna", "var_pct": 170.0, "precio": 120.0}


@pytest.fixture(autouse=True)
def _sin_clave(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


# --- respuesta de Anthropic falsa (con bloque de texto, como la real) ---

class _Bloque:
    def __init__(self, texto):
        self.type = "text"
        self.text = texto


class _Resp:
    def __init__(self, texto):
        self.content = [_Bloque(texto)]


def _fabricar_anthropic(json_text):
    class _Msgs:
        def create(self, **k):
            return _Resp(json_text)

    class _Cli:
        def __init__(self, *a, **k):
            self.messages = _Msgs()

    return _Cli


def test_sin_api_usa_titular_llano():
    """Sin clave de IA, el movimiento igual entra: titular con el dato duro."""
    cands = investigador.investigar_movers([MOVER])
    assert len(cands) == 1
    c = cands[0]
    assert c["verificado"] is False
    assert "MRNA" in c["titular"] and "170" in c["titular"]
    assert c["simbolos"] == "MRNA"


def test_con_ia_investiga_y_verifica(monkeypatch):
    """Con IA + búsqueda web (mockeada): titular con el porqué verificado."""
    anthropic = pytest.importorskip("anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    jt = ('{"verificado": true, "titular": "Moderna (MRNA) sube 170% tras un avance '
          'en su vacuna contra el cáncer", "razon": "resultados clínicos positivos", '
          '"fuente": "Reuters"}')
    monkeypatch.setattr(anthropic, "Anthropic", _fabricar_anthropic(jt))

    cands = investigador.investigar_movers([MOVER])
    assert cands[0]["verificado"] is True
    assert "vacuna contra el cáncer" in cands[0]["titular"]
    assert cands[0]["fuente"] == "Reuters"


def test_titular_no_publicable_cae_a_llano(monkeypatch):
    """Si la IA devuelve lenguaje de recomendación (CMF), se descarta y se usa el
    titular llano — nunca sale una pieza que rompa el marco regulatorio."""
    anthropic = pytest.importorskip("anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    jt = '{"verificado": true, "titular": "Recomendamos comprar MRNA ya", "razon": "x", "fuente": "y"}'
    monkeypatch.setattr(anthropic, "Anthropic", _fabricar_anthropic(jt))

    cands = investigador.investigar_movers([MOVER])
    assert cands[0]["verificado"] is False           # cayó al respaldo
    assert "MRNA" in cands[0]["titular"] and "170" in cands[0]["titular"]


def test_sin_movimientos_no_investiga():
    assert investigador.investigar_movers([]) == []
