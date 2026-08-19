"""Tests del blindaje (Fase 1 + 2): identidad, rate-limit, cabeceras,
validación de ids, path traversal y escape XSS del frontend."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import limites, persistencia, seguridad


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    seguridad.reiniciar()
    limites.reiniciar()


# ---------- identidad real del cliente (anti-spoofing) ----------

def test_ip_cliente_toma_el_ultimo_salto_de_xff():
    # el cliente falsifica 1.1.1.1; Render agrega su IP real al final
    headers = {"x-forwarded-for": "1.1.1.1, 203.0.113.9"}
    assert seguridad.ip_cliente(headers, "10.0.0.1") == "203.0.113.9"


def test_ip_cliente_usa_fallback_sin_proxy():
    assert seguridad.ip_cliente({}, "192.168.1.5") == "192.168.1.5"
    assert seguridad.ip_cliente({}, None) == "desconocida"


# ---------- validación de identificadores ----------

def test_sim_id_valido_solo_hex16():
    assert seguridad.sim_id_valido("6181e77222d4a245")
    assert not seguridad.sim_id_valido("../../../../etc/passwd")
    assert not seguridad.sim_id_valido("6181e77222d4a24")   # 15
    assert not seguridad.sim_id_valido("6181E77222D4A245")  # mayúsculas
    assert not seguridad.sim_id_valido(None)


def test_ruta_frames_rechaza_traversal():
    with pytest.raises(ValueError):
        persistencia.ruta_frames("../../../../etc/passwd")
    # un id válido sí produce ruta dentro de frames/
    ruta = persistencia.ruta_frames("6181e77222d4a245")
    assert ruta.name == "6181e77222d4a245.bin"


# ---------- rate-limit HTTP ----------

def test_permitir_http_corta_al_pasar_el_limite():
    ip = "9.9.9.9"
    permitidas = sum(1 for _ in range(200) if seguridad.permitir_http(ip, "/api/muro"))
    assert permitidas == seguridad.LIMITE_GENERAL[0]
    # otra IP sigue teniendo su propio cupo
    assert seguridad.permitir_http("8.8.8.8", "/api/muro")


def test_replay_tiene_su_propio_limite_mas_estricto():
    ip = "7.7.7.7"
    replay_ok = sum(1 for _ in range(100) if seguridad.permitir_http(ip, "/api/simulacion/x/replay"))
    assert replay_ok == seguridad.LIMITE_PESADO[0]


def test_endpoint_muro_responde_429_bajo_flood():
    cliente = TestClient(server.app)
    codigos = {cliente.get("/api/muro").status_code for _ in range(seguridad.LIMITE_GENERAL[0] + 10)}
    assert 429 in codigos


# ---------- cabeceras de seguridad ----------

def test_cabeceras_de_seguridad_presentes():
    cliente = TestClient(server.app)
    respuesta = cliente.get("/api/muro")
    assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
    assert respuesta.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'none'" in respuesta.headers["Content-Security-Policy"]


# ---------- path traversal en el endpoint de replay ----------

def test_replay_rechaza_sim_id_malicioso():
    cliente = TestClient(server.app)
    assert cliente.get("/api/simulacion/..%2f..%2fsecreto/replay").status_code == 404
    assert cliente.get("/api/simulacion/no-hex/replay").status_code == 404
    assert cliente.get("/api/simulacion/no-hex").status_code == 404


# ---------- caché HTTP en los endpoints servibles ----------

def test_endpoints_publicos_declaran_cache():
    cliente = TestClient(server.app)
    assert "max-age" in cliente.get("/api/muro").headers.get("Cache-Control", "")


# ---------- XSS: el frontend escapa el contenido no confiable ----------

def test_el_muro_escapa_datos_antes_de_innerhtml():
    """Guard de código: titular/frase deben ir escapados, nunca crudos."""
    muro = (Path(__file__).parent.parent.parent / "web" / "src" / "muro" / "muro.js").read_text(encoding="utf-8")
    assert "function esc(" in muro
    # el titular jamás se interpola crudo en el HTML
    assert "${tarjeta.titular}" not in muro
    assert "${esc(tarjeta.titular)}" in muro
    assert "${esc(r.frase.frase)}" in muro

    panel = (Path(__file__).parent.parent.parent / "web" / "src" / "ui" / "panel.js").read_text(encoding="utf-8")
    assert "${esc(f.frase)}" in panel
    assert re.search(r"\$\{f\.frase\}", panel) is None  # nunca crudo
    # el tooltip del líder también escapa la frase del LLM (defensa en profundidad)
    assert "${esc(lider.frase)}" in panel
    assert re.search(r"\$\{lider\.frase\}", panel) is None
    assert re.search(r"\$\{lider\.nombre\}", panel) is None
    # el ticker pasa por la lista blanca antes del HTML y del widget externo
    assert "tickerSeguro(" in panel
    assert re.search(r"\$\{extras\.simbolos\}", panel) is None  # nunca crudo


# ---------- el token de admin se compara en tiempo constante ----------

def test_token_admin_usa_comparacion_constante():
    """Los endpoints protegidos comparan el token con hmac.compare_digest
    (no con !=), para no filtrar el token por timing."""
    servidor = (Path(__file__).parent.parent / "server.py").read_text(encoding="utf-8")
    assert "hmac.compare_digest" in servidor
    # ya no debe quedar la comparación directa del token
    assert "!= esperado" not in servidor


def test_endpoint_protegido_rechaza_token_incorrecto(monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    import server
    cliente = TestClient(server.app)
    # sin token → 403
    assert cliente.post("/api/pipeline").status_code == 403
    # token equivocado → 403
    assert cliente.post("/api/pipeline", headers={"X-Pipeline-Token": "malo"}).status_code == 403
    # el diagnóstico también es solo-admin
    assert cliente.get("/api/diagnostico").status_code == 403


def test_diagnostico_reporta_clave_faltante(monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto-de-prueba")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import server
    cliente = TestClient(server.app)
    datos = cliente.get("/api/diagnostico", headers={"X-Pipeline-Token": "secreto-de-prueba"}).json()
    assert datos["clave_presente"] is False
    assert "FALTA" in datos["veredicto"]


# ---------- el tope global por defecto (la muralla de la billetera) ----------

def test_tope_diario_por_defecto(monkeypatch):
    # el default es 30 (la muralla de la billetera); en producción se fija con
    # ENJAMBRE_MAX_SIM_DIA según el presupuesto.
    monkeypatch.delenv("ENJAMBRE_MAX_SIM_DIA", raising=False)
    assert limites.tope_global_dia() == 30


# ---------- candado de pruebas privadas ----------

def test_acceso_abierto_sin_clave(monkeypatch):
    """Sin ENJAMBRE_ACCESO, cualquiera pasa (comportamiento normal)."""
    monkeypatch.delenv("ENJAMBRE_ACCESO", raising=False)
    assert not seguridad.acceso_privado_activo()
    assert seguridad.acceso_ok(None)
    assert seguridad.acceso_ok("lo-que-sea")


def test_acceso_privado_exige_la_clave(monkeypatch):
    """Con ENJAMBRE_ACCESO puesta, solo la clave correcta pasa."""
    monkeypatch.setenv("ENJAMBRE_ACCESO", "clave-secreta-de-pruebas")
    assert seguridad.acceso_privado_activo()
    assert seguridad.acceso_ok("clave-secreta-de-pruebas")
    assert not seguridad.acceso_ok("")
    assert not seguridad.acceso_ok(None)
    assert not seguridad.acceso_ok("clave-equivocada")


def test_ws_simular_rechaza_sin_clave_en_modo_privado(monkeypatch):
    """El WebSocket de simulación no gasta IA sin la clave correcta."""
    monkeypatch.setenv("ENJAMBRE_ACCESO", "abre-sesamo")
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_json({"tipo": "simular", "titular": "La Fed sube las tasas"})
        respuesta = ws.receive_json()
        assert respuesta["tipo"] == "privado"


def test_simular_titular_respeta_el_candado(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_ACCESO", "abre-sesamo")
    cliente = TestClient(server.app)
    r = cliente.post("/api/simular-titular", json={"id": "a" * 16})
    assert r.json()["estado"] == "privado"
    # con la clave correcta, el candado deja pasar (y sigue el flujo normal)
    r2 = cliente.post("/api/simular-titular", json={"id": "no-hex", "acceso": "abre-sesamo"})
    assert r2.status_code == 404  # ya pasó el candado; falla por id inválido


# ---------- la puerta de correo (gancho de crecimiento público) ----------

def test_correo_valido():
    assert seguridad.correo_valido("giorgio@rubicon.cl")
    assert not seguridad.correo_valido("no-es-correo")
    assert not seguridad.correo_valido("")
    assert not seguridad.correo_valido(None)
    assert not seguridad.correo_valido("a@b." + "x" * 300)  # muy largo


def test_puerta_publica_sin_bandera_queda_abierta(monkeypatch):
    """Sin ENJAMBRE_PUERTA_CORREO, público abierto (comportamiento de siempre)."""
    monkeypatch.delenv("ENJAMBRE_ACCESO", raising=False)
    monkeypatch.delenv("ENJAMBRE_PUERTA_CORREO", raising=False)
    ok, correo = server._puerta_simulacion({"titular": "x"})
    assert ok and correo is None


def test_puerta_correo_desactivada_es_permanente(monkeypatch):
    """Decisión de Giorgio: El Enjambre es GRATIS y abierto. La puerta de correo
    queda desactivada aunque alguien ponga la bandera; nunca bloquea. Si la
    persona deja un correo válido, igual se captura como lead (sin bloquear)."""
    monkeypatch.delenv("ENJAMBRE_ACCESO", raising=False)
    monkeypatch.setenv("ENJAMBRE_PUERTA_CORREO", "1")  # la bandera ya no tiene efecto
    ok, correo = server._puerta_simulacion({"titular": "x"})              # sin correo: abierto
    assert ok and correo is None
    ok, correo = server._puerta_simulacion({"titular": "x", "email": "Lector@Medio.CL"})
    assert ok and correo == "lector@medio.cl"                            # lead capturado (minúsculas)


def test_puerta_privada_exige_clave_no_correo(monkeypatch):
    monkeypatch.setenv("ENJAMBRE_ACCESO", "abre-sesamo")
    assert server._puerta_simulacion({"email": "x@y.cl"}) == (False, None)  # el correo no basta
    ok, _ = server._puerta_simulacion({"acceso": "abre-sesamo"})
    assert ok


def test_ws_no_pide_correo_en_publico(monkeypatch):
    """Aunque esté la bandera vieja, el WS NO exige correo: la simulación arranca.
    (El Enjambre es abierto; suscribirse a El Pulso es siempre opcional.)"""
    monkeypatch.delenv("ENJAMBRE_ACCESO", raising=False)
    monkeypatch.setenv("ENJAMBRE_PUERTA_CORREO", "1")
    cliente = TestClient(server.app)
    with cliente.websocket_connect("/ws") as ws:
        ws.send_json({"tipo": "simular", "titular": "La Fed sube las tasas"})  # sin correo
        respuesta = ws.receive_json()
        assert respuesta["tipo"] != "correo"  # no bloquea; arranca la simulación


# ---------- tope de cuerpo por petición (memoria del motor) ----------

def test_cuerpo_gigante_se_rechaza_con_413():
    """Un POST enorme se corta en la puerta: sin este freno se carga entero en
    memoria antes de validarse y el motor (512 MB en Render) reinicia."""
    cliente = TestClient(server.app)
    grande = "x" * (server.MAX_CUERPO + 1)
    respuesta = cliente.post("/api/contacto",
                             json={"nombre": "Ana", "email": "ana@medio.cl", "mensaje": grande})
    assert respuesta.status_code == 413
    # y el webhook (fuera de /api/) también queda cubierto
    assert cliente.post("/pulso/webhook/resend", content=grande).status_code == 413


def test_cuerpo_normal_sigue_pasando():
    """El freno no puede estorbar al uso legítimo (el más grande es el editor
    del panel: unos pocos KB)."""
    cliente = TestClient(server.app)
    respuesta = cliente.post("/api/contacto", json={
        "nombre": "Ana", "email": "ana@medio.cl",
        "organizacion": "Medio X", "mensaje": "y" * 4000})
    assert respuesta.status_code == 200


# ---------- avisos a Telegram (van con parse_mode=HTML) ----------

def test_aviso_telegram_escapa_lo_que_viene_de_afuera():
    """Un "<" en un formulario o en un titular hacía que Telegram rechazara el
    mensaje entero (400) y el aviso se perdiera en silencio."""
    from contenido import notificar
    assert notificar.escapar("<b>Ana</b>") == "&lt;b&gt;Ana&lt;/b&gt;"
    resumen = notificar.resumen_ejecucion(
        "demo", [{"impacto": 8, "titular": "<script>alert(1)</script> Fed sube"}], None)
    assert "<script>" not in resumen
    assert "&lt;script&gt;" in resumen
    assert "<b>El Pulso" in resumen  # el marcado propio del aviso se conserva


# ---------- filtro CMF a las voces de los líderes (borde de cumplimiento) ----------

def test_sanear_frases_neutraliza_lo_no_publicable():
    """Una frase de líder con vocabulario prohibido se neutraliza; una limpia
    se conserva. La neutra, a su vez, sí pasa el filtro."""
    from contenido import vocabulario
    r = [{"arquetipo": "fomo", "frase": "Compra ahora, esto va a subir"},
         {"arquetipo": "doomer", "frase": "Cautela ante el dato de empleo"}]
    vocabulario.sanear_frases(r)
    assert r[0]["frase"] == vocabulario.FRASE_NEUTRAL
    assert r[1]["frase"] == "Cautela ante el dato de empleo"
    assert vocabulario.es_publicable(vocabulario.FRASE_NEUTRAL)


def test_las_frases_de_lideres_se_sanean_en_los_tres_flujos():
    """Guard de código: las tres rutas que muestran frases de líderes (web,
    observatorio en vivo y pipeline de la madrugada) pasan por sanear_frases
    antes de repartirlas a la web, la base y el muro."""
    srv = (Path(__file__).parent.parent / "server.py").read_text(encoding="utf-8")
    assert srv.count("sanear_frases(") >= 2  # simulación transmitida + observatorio
    pipe = (Path(__file__).parent.parent / "contenido" / "pipeline.py").read_text(encoding="utf-8")
    assert "sanear_frases(" in pipe


# ---------- el tope diario vive en disco (sobrevive a los reinicios) ----------

def test_tope_diario_persiste_en_disco(monkeypatch):
    """El cupo global no depende de una variable en memoria que Render reinicia:
    vive en la base, así que un reinicio del proceso no lo levanta a cero."""
    from datetime import date
    monkeypatch.setenv("ENJAMBRE_MAX_SIM_DIA", "2")
    limites.reiniciar()
    assert limites.permitir("a")[0]
    assert limites.permitir("b")[0]
    # el gasto quedó en disco (una conexión nueva lo ve): el cupo está agotado
    conexion = persistencia.conectar()
    assert persistencia.gasto_dia(conexion, date.today().isoformat()) == 2
    conexion.close()
    ok, motivo = limites.permitir("c")
    assert not ok and motivo == limites.MENSAJE_GLOBAL
