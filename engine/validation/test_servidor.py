"""Tests del servidor WebSocket (Etapa 4): el flujo end-to-end.

Corren sin API key (fallback) y con ritmo 0 (sin pausas entre ticks).
"""

import json
import struct

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    from contenido import limites, seguridad

    limites.reiniciar()
    seguridad.reiniciar()


def test_salud():
    cliente = TestClient(server.app)
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_suscriptores_protegido_sin_secreto_en_codigo(monkeypatch):
    """P0 (auditoría 4.1): el endpoint de suscriptores ya NO lleva clave
    hardcodeada. Exige el token de admin del entorno; sin token, falla cerrado."""
    cliente = TestClient(server.app)
    # la vieja clave hardcodeada ya no abre nada
    assert cliente.get("/api/pulso/suscriptores?clave=revisar-pulso-2026").status_code == 404
    # sin token configurado: nadie pasa (falla cerrado)
    monkeypatch.delenv("ENJAMBRE_PIPELINE_TOKEN", raising=False)
    assert cliente.get("/api/pulso/suscriptores").status_code == 404
    # con el token del entorno: pasa SOLO por cabecera (auditoría v4: se quitó
    # ?clave= para no exponer el token en la URL)
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba-123")
    r_cab = cliente.get("/api/pulso/suscriptores",
                        headers={"X-Pipeline-Token": "secreto-de-prueba-123"})
    assert r_cab.status_code == 200 and "registrados" in r_cab.json()
    # el token en la URL (?clave=) YA NO autentica, ni con el valor correcto
    assert cliente.get("/api/pulso/suscriptores?clave=secreto-de-prueba-123").status_code == 404
    assert cliente.get("/api/pulso/suscriptores?clave=otra-cosa").status_code == 404


def test_cuerpo_chunked_grande_se_rechaza(monkeypatch):
    """Auditoría 4.3: una subida sin Content-Length (chunked) también se corta al
    superar el tope — antes solo se cubría el caso con Content-Length."""
    monkeypatch.setattr(server, "MAX_CUERPO", 2000)
    cliente = TestClient(server.app)

    def cuerpo_enorme():
        for _ in range(50):
            yield b"x" * 1000  # 50 KB en trozos, sin Content-Length

    # httpx envía un generador como chunked (sin Content-Length)
    r = cliente.post("/api/suscribir", content=cuerpo_enorme())
    assert r.status_code == 413


def test_cuerpo_chunked_valido_llega_al_handler(monkeypatch):
    """La re-inyección del cuerpo no rompe una petición chunked legítima."""
    import json as _json
    cliente = TestClient(server.app)

    def cuerpo_ok():
        yield _json.dumps({"email": "persona@ejemplo.com", "origen": "web"}).encode()

    r = cliente.post("/api/suscribir", content=cuerpo_ok(),
                     headers={"content-type": "application/json"})
    assert r.status_code == 200
    assert r.json()["estado"] in ("suscrito", "ya_suscrito")


def test_flujo_completo_por_websocket():
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({
            "tipo": "simular",
            "titular": "Quiebra el segundo banco más grande del país; pánico en los mercados",
            "seed": 42,
            "ritmo": 0,
        }))

        # 1) inicio: los 1150 líderes con señal, confianza y frase
        inicio = json.loads(ws.receive_text())
        assert inicio["tipo"] == "inicio"
        assert len(inicio["lideres"]) == 1150
        for lider in inicio["lideres"]:
            assert -1.0 <= lider["senal"] <= 1.0
            assert lider["frase"]

        # 2) un frame binario por tick: cabecera (precio, tick) + un byte por agente
        total_ticks = server.TICKS_PREVIOS + server.TICKS_POSTERIORES
        precios = []
        for _ in range(total_ticks):
            frame = ws.receive_bytes()
            precio, tick = struct.unpack("<fI", frame[:8])
            assert len(frame) == 8 + 10150
            precios.append(precio)

        # el titular negativo golpea el precio durante la reacción
        assert min(precios) < precios[server.TICKS_PREVIOS - 1] * 0.97

        # los sentimientos del último frame son bytes con signo válidos
        sentimientos = [b - 256 if b > 127 else b for b in frame[8:]]
        assert all(-127 <= s <= 127 for s in sentimientos)

        # 3) fin: el reporte
        fin = json.loads(ws.receive_text())
        assert fin["tipo"] == "fin"
        reporte = fin["reporte"]
        assert reporte["direccion_pct"] < 2  # una quiebra no dispara el precio
        assert reporte["volatilidad_pct"] > 0
        # Ventana A: el reporte expone la dirección de la señal y la del titular
        assert reporte["direccion_senal"] in ("alza", "baja", "neutra")
        assert reporte["direccion_titular"] in ("alza", "baja", "neutra")
        assert reporte["conviccion"]["nivel"] in ("fuerte", "moderada", "debil")
        # si la convicción es fiable, el titular sigue a la señal; si no, al precio
        if reporte["conviccion"]["fiable_direccion"]:
            assert reporte["direccion_titular"] == reporte["direccion_senal"]
        assert len(reporte["frases"]) == 3
        assert reporte["desglose"]  # hay actividad por tipo

        from contenido.vocabulario import DISCLAIMER
        assert reporte["descargo"] == DISCLAIMER

        # 4) persistencia primero: la simulación quedó guardada
        from contenido import persistencia
        conexion = persistencia.conectar()
        guardada = persistencia.obtener_simulacion(conexion, fin["sim_id"])
        conexion.close()
        assert guardada is not None
        assert guardada["titular"].startswith("Quiebra el segundo banco")
        assert len(guardada["lideres"]) == 1150
        assert len(guardada["serie_precios"]) >= total_ticks


# ---- Lectura honesta de la tarjeta (Opción 1: separar visual del ABM de la
# lectura del consenso; ver docs/hallazgo-ablacion.md) ----

def test_lectura_tarjeta_solo_si_fiable():
    # fiable → la tarjeta expone la LECTURA (dirección del consenso), aunque el
    # precio simulado (direccion_pct) vaya en otro sentido: se muestran aparte.
    rep = {"direccion_pct": -2.5, "volatilidad_pct": 1.0,
           "conviccion": {"fiable_direccion": True},
           "direccion_titular": "alza", "frases": []}
    t = server._resumen_tarjeta(rep)
    assert t["lectura"] == {"direccion": "alza", "flecha": "▲"}
    assert t["direccion"] == "▼"  # el movimiento simulado NO se toca


def test_sin_lectura_cuando_no_es_fiable():
    rep = {"direccion_pct": 3.0, "volatilidad_pct": 1.0,
           "conviccion": {"fiable_direccion": False},
           "direccion_titular": "alza", "frases": []}
    assert server._resumen_tarjeta(rep)["lectura"] is None


def test_sin_lectura_en_reporte_viejo_sin_conviccion():
    # destacadas históricas (antes de Ventana A) no traen `conviccion` → sin lectura
    rep = {"direccion_pct": 2.0, "volatilidad_pct": 1.0, "frases": []}
    assert server._resumen_tarjeta(rep)["lectura"] is None


def test_tablero_predicciones_solo_por_cabecera(monkeypatch):
    """Auditoría v4: /api/predicciones/resumen exige X-Pipeline-Token por CABECERA;
    el token en la URL (?clave=) ya no autentica (no exponerlo en logs/historial)."""
    cliente = TestClient(server.app)
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "tok-123")
    assert cliente.get("/api/predicciones/resumen").status_code == 403
    assert cliente.get("/api/predicciones/resumen?clave=tok-123").status_code == 403
    r = cliente.get("/api/predicciones/resumen", headers={"X-Pipeline-Token": "tok-123"})
    assert r.status_code == 200 and "global" in r.json()


def test_experimento_a2_protegido_y_estado(monkeypatch):
    """Plan B: los endpoints de A2 exigen token; el GET devuelve un estado."""
    cliente = TestClient(server.app)
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "tok-a2")
    # sin token → 403 en ambos
    assert cliente.get("/api/experimento/a2").status_code == 403
    assert cliente.post("/api/experimento/a2").status_code == 403
    # con token: el GET trae un estado (ninguno/corriendo/listo/error)
    r = cliente.get("/api/experimento/a2", headers={"X-Pipeline-Token": "tok-a2"})
    assert r.status_code == 200 and "estado" in r.json()
