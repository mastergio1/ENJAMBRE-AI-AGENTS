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


# ---------- el tope diario ahora es 5 ----------

def test_tope_diario_por_defecto_es_cinco(monkeypatch):
    monkeypatch.delenv("ENJAMBRE_MAX_SIM_DIA", raising=False)
    assert limites.tope_global_dia() == 5
