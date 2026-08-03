"""Tests de la Etapa 6: persistencia, portero y filtro de vocabulario CMF."""

from pathlib import Path

import pytest

from contenido import persistencia, portero, vocabulario
from contenido.fuentes import alpaca


@pytest.fixture()
def conexion(tmp_path):
    con = persistencia.conectar(tmp_path / "prueba.db")
    yield con
    con.close()


@pytest.fixture(autouse=True)
def sin_api(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)


# ---------- vocabulario CMF (sección 1 — no negociable) ----------

def test_filtro_detecta_terminos_prohibidos():
    assert not vocabulario.es_publicable("Recomendamos comprar esta acción")
    assert not vocabulario.es_publicable("Es una clara señal de inversión")
    assert not vocabulario.es_publicable("Nuestra predicción: el precio subirá")
    assert not vocabulario.es_publicable("gran OPORTUNIDAD DE COMPRA hoy")


def test_filtro_acepta_vocabulario_permitido():
    assert vocabulario.es_publicable("El enjambre simulado reaccionó con pánico")
    assert vocabulario.es_publicable("Los agentes simulados vendieron en cascada")
    assert vocabulario.es_publicable("En esta simulación educativa, la dirección fue -3%")


def test_verificar_pieza_exige_disclaimer():
    pieza_sin = "El enjambre simulado reaccionó."
    assert "falta el disclaimer oficial" in vocabulario.verificar_pieza(pieza_sin)
    pieza_completa = f"El enjambre simulado reaccionó. {vocabulario.DISCLAIMER}"
    assert vocabulario.verificar_pieza(pieza_completa) == []


def test_disclaimer_presente_en_las_piezas_publicas_existentes():
    """Cada pieza pública lleva el disclaimer fijo: la web ya es una."""
    panel = (Path(__file__).parent.parent.parent / "web" / "src" / "ui" / "panel.js").read_text(encoding="utf-8")
    assert vocabulario.DISCLAIMER in panel


def test_frases_fallback_de_los_lideres_son_publicables():
    """Las voces de los arquetipos (fallback) no usan vocabulario prohibido."""
    from brains.fallback import TRANSFORMACIONES

    for arquetipo, transformar in TRANSFORMACIONES.items():
        for sentimiento in (-0.9, 0.0, 0.9):
            _, _, variantes = transformar(sentimiento, "titular de prueba")
            for frase in variantes:  # cada ramo trae 3 variantes; todas publicables
                assert vocabulario.es_publicable(frase), f"{arquetipo}: «{frase}»"


# ---------- persistencia (regla: TODA simulación se guarda) ----------

def test_guardar_y_leer_simulacion(conexion):
    sim_id = persistencia.guardar_simulacion(
        conexion,
        titular="La Fed sube las tasas", fuente="manual", seed=42,
        resumen={"direccion_pct": -3.2}, lideres=[{"arquetipo": "doomer", "senal": -0.8}],
        serie_precios=[100.0, 99.1, 98.7],
    )
    assert sim_id == persistencia.id_simulacion("La Fed sube las tasas", 42)
    guardada = persistencia.obtener_simulacion(conexion, sim_id)
    assert guardada["resumen"]["direccion_pct"] == -3.2
    assert guardada["serie_precios"] == [100.0, 99.1, 98.7]
    assert guardada["destacada"] == 0


def test_misma_simulacion_no_se_duplica(conexion):
    for _ in range(2):
        persistencia.guardar_simulacion(
            conexion, titular="X", fuente="manual", seed=1,
            resumen={}, lideres=[], serie_precios=[100],
        )
    total = conexion.execute("SELECT COUNT(*) FROM simulaciones").fetchone()[0]
    assert total == 1


def test_listar_por_mes_y_destacadas(conexion):
    sim_id = persistencia.guardar_simulacion(
        conexion, titular="A", fuente="alpaca", seed=1,
        resumen={}, lideres=[], serie_precios=[100],
    )
    persistencia.marcar_destacada(conexion, sim_id)
    mes = persistencia.ahora_iso()[:7]
    assert persistencia.listar_simulaciones(conexion, mes=mes)
    assert persistencia.listar_simulaciones(conexion, solo_destacadas=True)[0]["id"] == sim_id
    assert persistencia.listar_simulaciones(conexion, mes="1999-01") == []


def test_suscriptores_double_opt_in(conexion):
    # alta: nace PENDIENTE (activo=0) hasta confirmar
    alta = persistencia.agregar_suscriptor(conexion, "Giorgio@Rubicon.cl", origen="web")
    assert alta["email"] == "giorgio@rubicon.cl"  # normalizado
    assert alta["ya_activo"] is False
    assert conexion.execute("SELECT activo FROM suscriptores").fetchone()[0] == 0
    assert persistencia.suscriptores_activos(conexion) == []

    # confirmar: ahora sí queda activo
    assert persistencia.confirmar_suscriptor(conexion, alta["token_confirma"]) == "giorgio@rubicon.cl"
    assert len(persistencia.suscriptores_activos(conexion)) == 1
    # el token de confirmación no sirve dos veces
    assert persistencia.confirmar_suscriptor(conexion, alta["token_confirma"]) is None

    # baja de un clic
    assert persistencia.dar_de_baja(conexion, alta["token_baja"]) is True
    assert persistencia.suscriptores_activos(conexion) == []
    assert persistencia.dar_de_baja(conexion, "token-falso") is False


# ---------- el portero ----------

def test_piso_lexico_descarta_lo_obvio():
    assert portero.evaluar_lexico("Top 5 stocks to watch this week", []) is not None
    assert portero.evaluar_lexico("How to invest in AI: a beginner's guide", []) is not None
    assert portero.evaluar_lexico("Celebrity chef opens new restaurant", []) is not None
    assert portero.evaluar_lexico("Join our free webinar: options trading", []) is not None


def test_piso_lexico_detecta_duplicados():
    previo = "Fed holds rates steady but signals two more hikes this year"
    casi_igual = "Fed holds rates steady, signals two more hikes this year"
    assert portero.evaluar_lexico(casi_igual, [previo]) == "duplicado de un titular reciente"


def test_piso_lexico_deja_pasar_lo_que_importa():
    assert portero.evaluar_lexico("US inflation comes in hotter than expected at 4.1%", []) is None
    assert portero.evaluar_lexico("Quiebra el segundo banco más grande del país", []) is None


def test_procesar_dia_elige_top3_y_registra_todo(conexion):
    candidatos = alpaca.titulares_demo()
    resultado = portero.procesar_dia(conexion, candidatos, maximo=3)

    assert len(resultado["elegidos"]) == 3
    assert all(e["impacto"] >= portero.UMBRAL_IMPACTO for e in resultado["elegidos"])
    # todo veredicto queda en el log de la base, incluso los descartes
    total = conexion.execute("SELECT COUNT(*) FROM titulares").fetchone()[0]
    assert total == len(candidatos)
    descartes = conexion.execute(
        "SELECT COUNT(*) FROM titulares WHERE veredicto = 'descartar'"
    ).fetchone()[0]
    assert descartes == len(candidatos) - 3
    # el duplicado del set de demo cayó en el piso léxico
    assert any("duplicado" in (e["motivo"] or "") for e in resultado["log"])


# ---------- fuente Alpaca ----------

def test_alpaca_sin_claves_degrada_elegante():
    assert alpaca.hay_credenciales() is False
    assert alpaca.titulares_recientes() == []
    titulares, origen = alpaca.obtener_titulares()
    assert origen == "demo"
    assert len(titulares) >= 20
    assert all(t["titular"] for t in titulares)
