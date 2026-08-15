"""Tests de la Etapa 8: El Pulso — captura, boletín, double opt-in, ritual."""

import struct

import pytest
from fastapi.testclient import TestClient

import brains.cerebro as cerebro
import server
from contenido import boletin, captura, limites, persistencia, pipeline, seguridad
from contenido.vocabulario import DISCLAIMER, verificar_pieza


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(cerebro, "RUTA_CACHE", tmp_path / "cache.json")
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))
    limites.reiniciar()
    seguridad.reiniciar()


@pytest.fixture()
def dia():
    return pipeline.preparar_dia(semilla_base=42)


# ---------- captura del momento dramático ----------

def test_captura_genera_png_valido():
    serie = [100.0 + (i % 7) - 3 for i in range(151)]
    png = captura.generar_png(
        "Quiebra un banco", {"direccion_pct": -8.4, "volatilidad_pct": 1.6}, serie)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"  # firma PNG
    assert len(png) > 5000


def test_endpoint_imagen(dia):
    cliente = TestClient(server.app)
    sim_id = dia["publicadas"][0]["sim_id"]
    respuesta = cliente.get(f"/api/simulacion/{sim_id}/imagen")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "image/png"
    assert respuesta.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert "max-age" in respuesta.headers.get("Cache-Control", "")
    # sim_id inválido → 404 (misma defensa que el resto)
    assert cliente.get("/api/simulacion/no-hex/imagen").status_code == 404


# ---------- el correo ----------

def test_html_del_pulso_lleva_disclaimer_y_vocabulario_limpio(dia):
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    html = boletin.construir_html(destacadas, "sábado 11 de julio", token_baja="ABC")
    # el disclaimer CMF está presente (test obligatorio de CONTENIDO.md)
    assert DISCLAIMER in html
    # y no hay vocabulario prohibido en toda la pieza
    assert verificar_pieza(html) == []
    # el link de baja usa el token del suscriptor
    assert "/api/baja/ABC" in html
    # el rediseño: cabecera de El Pulso y El Enjambre invitado al pie
    assert "El Pulso" in html and "Probar El Enjambre" in html


def test_correo_de_confirmacion_lleva_disclaimer():
    # sin RESEND no envía, pero el HTML se arma igual: lo probamos directo
    from contenido import boletin as b
    # reconstruye el cuerpo llamando a enviar con un doble que capture el html
    capturado = {}

    def falso_enviar(destinatario, asunto, html):
        capturado["html"] = html
        capturado["asunto"] = asunto
        return True

    b.enviar = falso_enviar  # monkeypatch simple
    assert b.enviar_confirmacion("x@y.cl", "tok123")
    assert DISCLAIMER in capturado["html"]
    assert "/api/confirmar/tok123" in capturado["html"]
    assert "Confirma" in capturado["asunto"]


# ---------- suscripción por la API (double opt-in) ----------

def test_flujo_suscripcion_completo():
    cliente = TestClient(server.app)

    # alta con correo inválido → 400
    assert cliente.post("/api/suscribir", json={"email": "no-es-correo"}).status_code == 400

    # alta válida → pendiente
    respuesta = cliente.post("/api/suscribir", json={"email": "giorgio@rubicon.cl"}).json()
    assert respuesta["estado"] == "pendiente"

    # aún no está activo
    conexion = persistencia.conectar()
    assert persistencia.suscriptores_activos(conexion) == []
    token = conexion.execute("SELECT token_confirma FROM suscriptores").fetchone()[0]
    baja = conexion.execute("SELECT token_baja FROM suscriptores").fetchone()[0]
    conexion.close()

    # confirmar por el link → página HTML de éxito
    conf = cliente.get(f"/api/confirmar/{token}")
    assert conf.status_code == 200
    assert "confirmada" in conf.text.lower()

    conexion = persistencia.conectar()
    assert len(persistencia.suscriptores_activos(conexion)) == 1
    conexion.close()

    # baja de un clic
    assert cliente.get(f"/api/baja/{baja}").status_code == 200
    conexion = persistencia.conectar()
    assert persistencia.suscriptores_activos(conexion) == []
    conexion.close()


def test_suscribir_silencioso_captura_el_lead():
    """La puerta de correo: soltar un titular con correo deja el lead suscrito
    (sin RESEND no envía, pero el alta queda)."""
    server._suscribir_silencioso("nuevo@lector.cl")
    conexion = persistencia.conectar()
    total = conexion.execute(
        "SELECT COUNT(*) FROM suscriptores WHERE email = 'nuevo@lector.cl'").fetchone()[0]
    conexion.close()
    assert total == 1


def test_suscribir_dos_veces_no_duplica():
    cliente = TestClient(server.app)
    cliente.post("/api/suscribir", json={"email": "a@b.cl"})
    cliente.post("/api/suscribir", json={"email": "a@b.cl"})
    conexion = persistencia.conectar()
    total = conexion.execute("SELECT COUNT(*) FROM suscriptores").fetchone()[0]
    conexion.close()
    assert total == 1


def test_no_reenvia_confirmacion_a_pendiente_reciente():
    """Antibombardeo (auditoría C): un segundo intento inmediato para el mismo
    correo pendiente no reenvía ni rota el token."""
    conexion = persistencia.conectar()
    a1 = persistencia.agregar_suscriptor(conexion, "victima@correo.cl")
    a2 = persistencia.agregar_suscriptor(conexion, "victima@correo.cl")
    conexion.close()
    assert a1["reenviar"] is True
    assert a2["reenviar"] is False              # no se reenvía el correo
    assert a2["token_confirma"] == a1["token_confirma"]  # ni se rota el token


# ---------- el ritual completo ----------

def test_ritual_matutino_arma_todo_sin_enviar(monkeypatch):
    avisos = []
    from contenido import notificar
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: avisos.append(mensaje) or True)

    # se fuerza un día de semana (el ritual del fin de semana es otra edición)
    entre_semana = {"dia_semana": "lunes", "fecha": "4 de agosto de 2026",
                    "momento": "mañana", "es_finde": False}
    resultado = pipeline.ritual_matutino(semilla_base=99, enviar=False, cuando=entre_semana)
    assert len(resultado["publicadas"]) == 3
    assert resultado["destacadas"] == 3
    assert resultado["estado"] == "pendiente"   # generada, esperando el visto bueno
    assert resultado["token"]                   # token para los enlaces del correo de revisión
    assert DISCLAIMER in resultado["html_preview"]
    assert avisos and "El Pulso" in avisos[0]   # paso 8: avisó a Giorgio


def test_ritual_de_domingo_arma_el_deep_dive(monkeypatch):
    """El domingo el ritual NO simula noticias: arma el deep-dive de una
    mid/small-cap o sector y lo deja pendiente de revisión."""
    from contenido import analisis_semanal, notificar, redaccion_ia
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: True)

    hechos = {
        "modo": "accion", "titulo": "Acción seleccionada", "encuadre": "mediana capitalización",
        "ticker": "ROKU", "nombre": "Roku", "sector": "Streaming", "contexto": "…",
        "var_semana_pct": 8.4, "var_mes_pct": 12.0, "fecha_inicio": "1 ago", "fecha_fin": "31 ago",
        "grafico": {"ticker": "ROKU", "nombre": "Roku", "periodo": "mes", "moneda": "$"},
    }
    redactado = {
        "titular": "Roku vuelve a la conversación", "dek": "Semana movida",
        "contexto": "Roku hace el sistema de sus televisores.\n\nGana con publicidad.",
        "lectura": "Avanzó tras un anuncio.",
        "debate": [{"arquetipo": "doomer", "nombre": "El Doomer",
                    "mirada": "La publicidad es lo primero que se recorta."}],
        "que_observar": "Habrá que ver si sostiene el ritmo.",
    }
    monkeypatch.setattr(analisis_semanal, "preparar_analisis", lambda **k: hechos)
    monkeypatch.setattr(redaccion_ia, "redactar_analisis", lambda *a, **k: redactado)

    domingo = {"dia_semana": "domingo", "weekday": 6, "fecha": "16 de agosto de 2026",
               "momento": "mañana", "es_finde": True}
    resultado = pipeline.ritual_matutino(enviar=False, cuando=domingo)

    assert resultado["edicion"] == "finde"
    assert resultado["estado"] == "pendiente"
    assert resultado["publicadas"] == []                 # el finde no simula el enjambre
    html = resultado["html_preview"]
    assert "Edición de fin de semana" in html
    assert "Qué es" in html and "Lo que ven nuestros inversionistas IA" in html
    assert DISCLAIMER in html


def test_ritual_de_sabado_arma_el_resumen(monkeypatch):
    """El sábado el ritual arma el RESUMEN DE LA SEMANA (no el deep-dive) y lo
    deja pendiente de revisión."""
    from contenido import notificar, redaccion_ia, resumen_semanal
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: True)

    hechos = {"titulo": "El Pulso de la semana",
              "titulares": [{"titular": "La Fed sube el tono", "fecha": "2026-08-14"}],
              "foto": [{"simbolo": "^GSPC", "nombre": "S&P 500", "var_semana_pct": 1.8}]}
    redactado = {"intro": "Semana de nervios.",
                 "temas": [{"kicker": "Macro", "emoji": "🏦", "titular": "La Fed marcó el tono",
                            "analisis": "Subió el tono.\n\nCautela.",
                            "que_observar": "Habrá que ver la próxima acta.", "grafico": None}],
                 "cierre": "Una semana para respirar."}
    monkeypatch.setattr(resumen_semanal, "preparar_resumen", lambda *a, **k: hechos)
    monkeypatch.setattr(redaccion_ia, "redactar_resumen", lambda *a, **k: redactado)

    sabado = {"dia_semana": "sábado", "weekday": 5, "fecha": "15 de agosto de 2026",
              "momento": "mañana", "es_finde": True}
    resultado = pipeline.ritual_matutino(enviar=False, cuando=sabado)

    assert resultado["edicion"] == "resumen"
    assert resultado["estado"] == "pendiente"
    assert resultado["publicadas"] == []
    html = resultado["html_preview"]
    assert "El Pulso de la semana" in html and "La semana en números" in html
    assert "La Fed marcó el tono" in html
    assert DISCLAIMER in html


def test_endpoint_pipeline_exige_token(monkeypatch):
    cliente = TestClient(server.app)
    # sin token configurado → 403
    monkeypatch.delenv("ENJAMBRE_PIPELINE_TOKEN", raising=False)
    assert cliente.post("/api/pipeline").status_code == 403

    # con token configurado pero header incorrecto → 403
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    assert cliente.post("/api/pipeline", headers={"X-Pipeline-Token": "malo"}).status_code == 403

    # header correcto → 200 e inicia en segundo plano (el ritual se neutraliza
    # para probar solo la puerta de autorización, no correr 3 simulaciones)
    corridas = []
    monkeypatch.setattr(pipeline, "ritual_matutino", lambda **k: corridas.append(k))
    respuesta = cliente.post("/api/pipeline", headers={"X-Pipeline-Token": "secreto"})
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "iniciado"
    assert corridas  # el ritual se disparó en segundo plano


def test_html_usa_la_voz_de_ia_cuando_existe(dia):
    """Con 'redactado' (voz del redactor de IA), el correo lo usa: historias con
    análisis, gráfico real y 'en una línea'; sigue pasando el filtro CMF."""
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    brief = {"mercado": [], "observa": [], "redactado": {
        "buenos_dias": "Wall Street amaneció en verde y el Nasdaq sacó pecho.",
        "historias": [
            {"kicker": "Tecnología · catalizador", "emoji": "🍎",
             "titular": "Apple busca acuerdo con Epic", "dek": "El que peleaba, negocia.",
             "cuerpo": "Años de pelea.\n\nHoy ofrece café.\n\nEso dice mucho.",
             "bottom_line": "Apple no cambia de libreto por gusto.",
             "grafico": {"ticker": "AAPL", "nombre": "Apple Inc.", "periodo": "semana", "moneda": "$"}},
            {"kicker": "Small-cap · movida", "emoji": "🟢", "titular": "Nvidia subió",
             "dek": "", "cuerpo": "Los chips mandan.", "bottom_line": "", "grafico": None},
        ],
    }}
    html = boletin.construir_html(destacadas, "miércoles 5 de agosto", brief=brief)
    assert "Buenos días" in html
    assert "Apple busca acuerdo con Epic" in html and "Nvidia subió" in html
    assert "/api/grafico/AAPL" in html          # el gráfico real de la historia
    assert "En una línea:" in html               # el bottom line
    assert DISCLAIMER in html
    assert verificar_pieza(html) == []


def test_tabla_mercado_dia_mes_ano(dia):
    """La 'foto del día' se pinta como tabla Día/Mes/Año; los datos faltantes
    (mes/año None) muestran '—' y todo pasa el filtro CMF."""
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    brief = {"foto": [
        {"nombre": "S&P 500", "variacion_pct": 1.8, "var_mes_pct": 2.67, "var_ano_pct": 22.8},
        {"nombre": "Oro", "variacion_pct": -0.9, "var_mes_pct": 3.28, "var_ano_pct": None},
    ]}
    html = boletin.construir_html(destacadas, "miércoles 5 de agosto", brief=brief)
    assert "La foto del día" in html
    assert "S&amp;P 500" in html          # nombre escapado
    assert "1.8%" in html and "22.8%" in html
    assert "—" in html                     # el año de Oro venía None
    assert verificar_pieza(html) == []


def test_html_respaldo_sin_redactado(dia):
    """Sin 'redactado' ni brief, el correo se arma igual (no se cae): cabecera de
    El Pulso, El Enjambre al pie y el disclaimer."""
    destacadas = pipeline._destacadas_de_hoy(persistencia.conectar())
    html = boletin.construir_html(destacadas, "miércoles 5 de agosto")  # sin brief
    assert html.startswith("<!doctype")
    assert "El Pulso" in html and "Probar El Enjambre" in html
    assert DISCLAIMER in html


def test_yahoo_calcula_dia_mes_ano():
    """El cálculo Día/Mes/Año de Yahoo, sin red (serie inyectada)."""
    from contenido.fuentes import yahoo
    serie = [100 + i * 0.1 for i in range(260)]   # sube de 100 a ~125.9 en el año
    v = yahoo._variaciones(serie)
    assert v["variacion_pct"] is not None          # día
    assert v["var_mes_pct"] is not None            # mes (>=22 datos)
    assert v["var_ano_pct"] > 0                    # subió en el año
    assert yahoo._variaciones([100.0]) is None     # serie muy corta → None


def test_ritual_genera_pendiente_y_aprobar_envia(monkeypatch):
    """El ritual GENERA la edición (pendiente); nada sale a los suscriptores
    hasta que Giorgio la aprueba. Aprobar la envía a los confirmados."""
    # un suscriptor confirmado
    conexion = persistencia.conectar()
    alta = persistencia.agregar_suscriptor(conexion, "lector@medio.cl")
    persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    conexion.close()

    enviados = []
    monkeypatch.setattr(boletin, "enviar", lambda *a, **k: enviados.append(a) or True)
    monkeypatch.setattr(boletin, "PULSO_ADMIN_EMAIL", "")  # sin correo de revisión en el test
    from contenido import notificar
    monkeypatch.setattr(notificar, "avisar", lambda mensaje: True)

    # 1) el ritual arma la edición pero NO la envía a los suscriptores (queda pendiente)
    entre_semana = {"dia_semana": "lunes", "fecha": "4 de agosto de 2026",
                    "momento": "mañana", "es_finde": False}
    resultado = pipeline.ritual_matutino(semilla_base=7, enviar=True, cuando=entre_semana)
    assert resultado["estado"] == "pendiente"
    assert enviados == []                       # nada salió a los suscriptores todavía

    # 2) el visto bueno la envía a los suscriptores confirmados
    envio = pipeline.aprobar_y_enviar()
    assert envio["ok"] and envio["suscriptores"] == 1 and envio["enviados"] == 1
    assert enviados[0][0] == "lector@medio.cl"  # el correo salió al confirmado


# ---------- el correo no deja pasar marcado ajeno ----------

def test_el_correo_escapa_texto_hostil_del_redactado():
    """El texto del redactor de IA (titular, cuerpo, bottom_line) sale de un
    titular que puede venir del público: no puede inyectar HTML en el correo
    que reciben los suscriptores."""
    brief = {"mercado": [], "redactado": {
        "buenos_dias": "Un día normal.",
        "historias": [{
            "kicker": "Test", "emoji": "🧪",
            "titular": '<img src=x onerror=alert(1)> Titular hostil',
            "dek": "", "cuerpo": '</p><a href="http://sitio-falso.cl">entra aquí</a>\n\nOtro párrafo.',
            "bottom_line": "<script>alert(1)</script> cierre",
            "grafico": None,
        }]}}
    html = boletin.construir_html([], "lunes 4 de agosto", token_baja="ABC", brief=brief)
    assert "<img src=x" not in html
    assert "&lt;img src=x" in html                        # se ve como texto, no se ejecuta
    assert '<a href="http://sitio-falso.cl"' not in html  # sin enlaces colados
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html


def test_el_correo_solo_acepta_enlaces_http():
    """La fuente de un dato de mercado es un enlace externo: solo http(s)."""
    assert boletin._url_segura("https://ejemplo.cl/nota") == "https://ejemplo.cl/nota"
    assert boletin._url_segura("javascript:alert(1)") == ""
    assert boletin._url_segura("") == ""
    fila = boletin._fila_mercado({"tipo": "evento", "titular": "Dato", "url": "javascript:alert(1)"})
    assert "javascript:" not in fila


# ---------- B5: el panel no miente cuando el preview no se regenera ----------

def test_editar_avisa_si_el_preview_no_se_regenera(monkeypatch):
    """Si al editar no hay destacadas para re-armar el correo, la respuesta debe
    DECIRLO (preview_actualizado=False), no un ok:true a secas — si no, se
    aprueba y sale el correo sin las ediciones."""
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    hoy = persistencia.ahora_iso()[:10]
    conexion = persistencia.conectar()
    # una edición guardada, pero SIN simulaciones destacadas para hoy
    persistencia.guardar_edicion(conexion, hoy, {"redactado": {}}, "<html>viejo</html>",
                                 "Asunto", "t" * 24, persistencia.ahora_iso())
    conexion.close()
    cliente = TestClient(server.app)
    res = cliente.post(f"/api/panel/edicion/{hoy}/editar",
                       headers={"X-Pipeline-Token": "secreto"},
                       json={"redactado": {"buenos_dias": "Hola"}}).json()
    assert res["ok"] is True
    assert res["preview_actualizado"] is False        # no mintió
    assert "vista previa" in res["motivo"].lower()


def test_panel_edicion_finde_marca_deep_dive_y_regenera_preview(monkeypatch):
    """La edición de FIN DE SEMANA se marca como 'finde' en el panel y su vista
    previa SÍ se regenera sin destacadas (el deep-dive no las necesita)."""
    monkeypatch.setenv("ENJAMBRE_PIPELINE_TOKEN", "secreto")
    hoy = persistencia.ahora_iso()[:10]
    brief = {
        "analisis": {"modo": "accion", "titulo": "Acción seleccionada",
                     "encuadre": "mediana capitalización", "ticker": "ROKU", "nombre": "Roku",
                     "sector": "Streaming", "var_semana_pct": 8.4,
                     "grafico": {"ticker": "ROKU", "nombre": "Roku", "periodo": "mes", "moneda": "$"}},
        "analisis_redactado": {"titular": "Roku vuelve a la conversación", "dek": "",
                               "contexto": "Roku hace el sistema de sus televisores.", "lectura": "",
                               "debate": [{"arquetipo": "doomer", "nombre": "El Doomer",
                                           "mirada": "La publicidad es lo primero que se recorta."}],
                               "que_observar": "Habrá que ver si sostiene el ritmo."},
    }
    conexion = persistencia.conectar()
    persistencia.guardar_edicion(conexion, hoy, brief, "<html>viejo</html>",
                                 "Asunto", "t" * 24, persistencia.ahora_iso())
    conexion.close()
    cliente = TestClient(server.app)

    ed = cliente.get(f"/api/panel/edicion/{hoy}", headers={"X-Pipeline-Token": "secreto"}).json()
    assert ed["finde"] is True
    assert ed["analisis"]["nombre"] == "Roku"

    res = cliente.post(f"/api/panel/edicion/{hoy}/editar",
                       headers={"X-Pipeline-Token": "secreto"},
                       json={"redactado": {}}).json()
    assert res["ok"] is True and res["preview_actualizado"] is True  # se regeneró el deep-dive
