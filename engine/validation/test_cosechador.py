"""Tests del cosechador (contenido/cosechador.py).

Reglas: detecta días de gran movimiento reales, mide la ventana igual que el
corrector, NUNCA inventa titulares (si no hay noticia real, descarta el día),
no repite lo que ya está en el banco, y respeta el tope por símbolo.
"""

from contenido import cosechador


def _historia_falsa(*subidas):
    """Una serie de cierres a partir de variaciones diarias en %."""
    from datetime import date, timedelta

    precio = 100.0
    dia = date(2023, 1, 2)
    barras = [(dia.isoformat(), precio)]
    for pct in subidas:
        precio = round(precio * (1 + pct / 100), 4)
        dia += timedelta(days=1)
        barras.append((dia.isoformat(), precio))
    return barras


def test_detecta_solo_los_dias_de_gran_movimiento(monkeypatch):
    # días tranquilos (±0.5%) y un salto fuerte del 8% al cuarto día
    barras = _historia_falsa(0.5, -0.4, 0.3, 8.0, 0.2, -0.5)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    dias = cosechador.dias_de_movimiento("XYZ", "accion", "2023-01-01", "2023-02-01")
    assert len(dias) == 1
    assert dias[0]["categoria"] == "positiva"
    assert dias[0]["_cambio_dia"] >= 6.0


def test_umbral_depende_del_mercado(monkeypatch):
    # un 3% es ruido en cripto (umbral 7) pero noticia en oro (umbral 2.5)
    barras = _historia_falsa(0.2, 3.0, 0.1, -0.2)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    assert cosechador.dias_de_movimiento("BTC", "cripto", "2023-01-01", "2023-02-01") == []
    assert len(cosechador.dias_de_movimiento("GLD", "oro", "2023-01-01", "2023-02-01")) == 1


def test_nunca_inventa_titular(monkeypatch):
    """Si Alpaca no tiene noticia para ese día, el evento se descarta."""
    barras = _historia_falsa(0.2, -0.3, 9.0, 0.1, 0.2)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    monkeypatch.setattr(cosechador, "_titular_de", lambda s, f: None)  # sin noticia real
    r = cosechador.cosechar({"XYZ": "accion"}, "2023-01-01", "2023-02-01")
    assert r["eventos"] == []
    assert len(r["sin_titular"]) == 1  # quedó registrado como descartado, no inventado


def test_cosecha_arma_examen_completo_y_no_repite(monkeypatch):
    barras = _historia_falsa(0.2, -0.3, 9.0, 0.1, 0.2)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    monkeypatch.setattr(cosechador, "_titular_de",
                        lambda s, f: {"titular": f"{s} salta con fuerza", "fuente_noticia": "benzinga"})
    r = cosechador.cosechar({"XYZ": "accion"}, "2023-01-01", "2023-02-01")
    assert len(r["eventos"]) == 1
    ev = r["eventos"][0]
    assert ev["titular"] and ev["simbolo"] == "XYZ" and ev["mercado"] == "accion"
    assert ev["categoria"] in ("positiva", "negativa", "neutra")

    # con ese id ya en el banco, una segunda cosecha no lo repite
    r2 = cosechador.cosechar({"XYZ": "accion"}, "2023-01-01", "2023-02-01",
                             ids_existentes={ev["id"]})
    assert r2["eventos"] == []


def test_descarta_titulares_genericos(monkeypatch):
    """Un titular real pero sin señal ('40 Biggest Movers') no sirve de examen."""
    barras = _historia_falsa(0.2, -0.3, 9.0, 0.1, 0.2)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)

    def alpaca_falso(simbolo, fecha):
        # el más cercano en tiempo es genérico; hay otro real detrás
        return {"news": [
            {"headline": "40 Biggest Movers From Wednesday", "created_at": f"{fecha}T20:00:00Z"},
            {"headline": "Company XYZ wins major regulatory approval", "created_at": f"{fecha}T14:00:00Z"},
        ]}

    monkeypatch.setattr(cosechador.httpx, "get",
                        lambda *a, **k: type("R", (), {"raise_for_status": lambda s: None,
                                                        "json": lambda s: alpaca_falso(*[], **{})})())
    # prueba directa del filtro: el genérico no debe elegirse
    assert cosechador.PATRONES_GENERICOS.search("40 Biggest Movers From Wednesday")
    assert cosechador.PATRONES_GENERICOS.search("22 Stocks Moving In Monday's Pre-Market Session")
    assert not cosechador.PATRONES_GENERICOS.search("Bitcoin rallies after SEC approves spot ETF")


def test_proxy_de_cripto_no_cosecha_antes_del_pivote(monkeypatch):
    """MARA era una empresa de patentes antes de 2020: no cosechar cripto ahí."""
    capturado = {}

    def historia_espia(simbolo, desde, hasta, *a, **k):
        capturado["desde"] = desde
        return []

    monkeypatch.setattr(cosechador, "_historia_diaria", historia_espia)
    cosechador.dias_de_movimiento("MARA", "cripto", "2016-01-01", "2023-01-01")
    # el piso de MARA (2020-12-01) manda sobre el 2016 pedido
    assert capturado["desde"] == cosechador.SIMBOLO_DESDE["MARA"]


def test_respeta_el_tope_por_simbolo(monkeypatch):
    # cinco saltos fuertes bien separados; con tope 2 solo entran los dos mayores
    barras = _historia_falsa(9.0, 0.1, 0.1, 0.1, 0.1, 12.0, 0.1, 0.1, 0.1, 0.1,
                             7.0, 0.1, 0.1, 0.1, 0.1, 15.0, 0.1, 0.1, 0.1, 0.1, 8.0)
    monkeypatch.setattr(cosechador, "_historia_diaria", lambda *a, **k: barras)
    monkeypatch.setattr(cosechador, "_titular_de",
                        lambda s, f: {"titular": "hay noticia", "fuente_noticia": "x"})
    r = cosechador.cosechar({"XYZ": "accion"}, "2023-01-01", "2023-03-01", tope_por_simbolo=2)
    assert len(r["eventos"]) == 2
