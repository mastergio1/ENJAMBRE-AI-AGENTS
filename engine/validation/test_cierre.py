"""Tests de la edición de la TARDE — 'el cierre del mercado' (Premium)."""

import pytest

import server  # noqa: F401 (asegura que la app importa con los cambios)
from contenido import boletin, persistencia, pipeline

CIERRE = {
    "titulo": "El cierre del mercado",
    "movers": [
        {"titular": "Moderna (MRNA) sube 40% tras un avance en su vacuna contra el cáncer",
         "razon": "resultados clínicos positivos", "simbolos": "MRNA",
         "var_pct": 40.0, "verificado": True, "sesion": "sesión"},
        {"titular": "OneSpaWorld (OSW) cae 10% tras una guía débil",
         "razon": "recortó su previsión", "simbolos": "OSW",
         "var_pct": -10.0, "verificado": True, "sesion": "sesión"},
    ],
}


@pytest.fixture(autouse=True)
def entorno(monkeypatch, tmp_path):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.setenv("ENJAMBRE_DB", str(tmp_path / "enjambre.db"))


def test_bloque_cierre_renderiza():
    html = boletin.construir_html([], "lunes 1 de septiembre · cierre", brief={"cierre": CIERRE})
    assert "Edición de la tarde" in html
    assert "Moderna" in html and "vacuna contra el cáncer" in html
    assert "OneSpaWorld" in html
    assert "No es asesoría de inversión" in html


def test_bloque_cierre_con_voz_renderiza_minihistorias():
    """Con voz Moby, el cierre son mini-historias (apertura + párrafos), no la
    lista llana."""
    cierre_con_voz = dict(CIERRE)
    cierre_con_voz["redactado"] = {
        "buenas_tardes": "El mercado cerró y, como siempre, los protagonistas no "
                         "fueron los de siempre.",
        "historias": [{
            "kicker": "Salud · catalizador",
            "emoji": "🧬",
            "titular": "Moderna se disparó y recordó por qué la biotecnología no aburre",
            "dek": "Un avance clínico encendió la acción",
            "cuerpo": "Moderna subió con fuerza tras un avance en su vacuna contra el "
                      "cáncer.\n\nEl dato importa porque cambia la conversación sobre "
                      "sus ingresos futuros.",
            "bottom_line": "La biotecnología volvió al centro de la mesa.",
            "grafico": {"ticker": "MRNA", "nombre": "Moderna", "periodo": "dia", "moneda": "$"},
            "var_pct": 40.0, "sesion": "sesión",
        }],
    }
    html = boletin.construir_html([], "lunes 1 de septiembre · cierre",
                                  brief={"cierre": cierre_con_voz})
    assert "Edición de la tarde" in html
    assert "Buenas tardes" in html
    assert "la biotecnología no aburre" in html          # titular con voz
    assert "cambia la conversación" in html              # cuerpo desarrollado
    assert "No es asesoría de inversión" in html


def test_validar_cierre_ata_pildora_por_ticker():
    """El validador casa el % real del movimiento con la historia por su ticker."""
    from contenido import redaccion_ia
    parseado = {
        "buenas_tardes": "Buenas tardes.",
        "historias": [{
            "titular": "Moderna vivió su mejor día en meses",
            "cuerpo": "Subió tras un avance clínico.\n\nEl mercado lo celebró.",
            "grafico": {"ticker": "MRNA", "nombre": "Moderna", "periodo": "dia", "moneda": "$"},
        }],
    }
    salida = redaccion_ia._validar_cierre(parseado, CIERRE["movers"])
    assert salida is not None
    assert salida["historias"][0]["var_pct"] == 40.0     # atado desde el mover MRNA
    assert salida["historias"][0]["sesion"] == "sesión"


def test_envio_reporta_fallos_con_motivo(monkeypatch):
    """Un envío que falla ya no es un '3 de 6' a ciegas: enviar_a_suscriptores
    devuelve QUÉ direcciones cayeron y por qué."""
    conexion = persistencia.conectar()
    for correo in ("bueno@lector.cl", "malo@lector.cl"):
        alta = persistencia.agregar_suscriptor(conexion, correo)
        persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])

    def fake_enviar(dest, asunto, html, **k):
        if dest == "malo@lector.cl":
            return False, "HTTP 422: dirección inválida"
        return True, ""
    monkeypatch.setattr(boletin, "_enviar_resend", fake_enviar)

    conteo = boletin.enviar_a_suscriptores(conexion, "<html>x</html>", "Asunto")
    conexion.close()
    assert conteo["enviados"] == 1 and conteo["fallidos"] == 1
    assert conteo["fallos"] == [{"email": "malo@lector.cl", "motivo": "HTTP 422: dirección inválida"}]


def test_ritual_tarde_arma_pendiente(monkeypatch):
    from contenido import cierre, notificar
    monkeypatch.setattr(notificar, "avisar", lambda m: True)
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: CIERRE)

    res = pipeline.ritual_matutino(enviar=False, momento="tarde")
    assert res["edicion"] == "cierre" and res["estado"] == "pendiente"
    assert res["clave"].endswith("-t")           # clave propia de la tarde
    assert "El cierre del mercado" in res["html_preview"]


def test_ritual_tarde_sin_movers_no_edicion(monkeypatch):
    from contenido import cierre
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: None)
    res = pipeline.ritual_matutino(enviar=False, momento="tarde")
    assert res["estado"] == "sin_edicion" and res["edicion"] == "cierre"


def test_cierre_sale_solo_a_premium(monkeypatch):
    conexion = persistencia.conectar()
    for correo in ("gratis@lector.cl", "pago@lector.cl"):
        alta = persistencia.agregar_suscriptor(conexion, correo)
        persistencia.confirmar_suscriptor(conexion, alta["token_confirma"])
    persistencia.set_premium(conexion, "pago@lector.cl", True)

    from contenido import cierre, notificar
    monkeypatch.setattr(notificar, "avisar", lambda m: True)
    monkeypatch.setattr(cierre, "preparar_cierre", lambda **k: CIERRE)
    res = pipeline.ritual_matutino(conexion, enviar=False, momento="tarde")
    clave = res["clave"]
    conexion.close()

    enviados = []
    monkeypatch.setattr(boletin, "_enviar_resend",
                        lambda dest, asunto, html, **k: (enviados.append(dest) or True, ""))
    r = pipeline.aprobar_y_enviar(fecha=clave)
    assert r["ok"] and r["enviados"] == 1
    assert enviados == ["pago@lector.cl"]         # el gratuito NO recibe la tarde
