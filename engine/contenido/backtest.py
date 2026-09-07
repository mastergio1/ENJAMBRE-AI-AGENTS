"""Backtesting histórico — la calibración no espera al futuro.

Le pasa al enjambre exámenes del pasado cuya respuesta real ya se conoce:
titulares de eventos reales (backtest_eventos.json) se simulan hoy y se
comparan con cuánto se movió el símbolo EN ESOS DÍAS históricos (Alpaca).

Reglas de diseño:
- **Tandas pequeñas** (presupuesto LLM ~100 llamadas por simulación):
  cada corrida procesa `tamano` eventos y se detiene. Tope duro TANDA_MAXIMA.
- Los casos quedan con fuente='backtest' y NUNCA destacada: no aparecen
  en el muro ni en la hemeroteca (el archivo es el registro EN VIVO);
  solo alimentan la libreta de calificaciones y la caja fuerte.
- Reproducible: la semilla de cada evento sale de su fecha — repetir una
  tanda no gasta (la caché de cerebros responde gratis).
- Si Alpaca no entrega datos para un evento, queda pendiente y la
  próxima tanda lo reintenta. Nunca lanza.
"""

import gc
import json
import os
from pathlib import Path

from contenido import persistencia

RUTA_EVENTOS = Path(__file__).parent / "backtest_eventos.json"
TANDA_DEFECTO = 5
TANDA_MAXIMA = 40   # freno duro por corrida. Con Starter (no se duerme) + disco
                    # persistente, tandas grandes son seguras; y cada examen se
                    # respalda al instante, así que si Render corta una tanda
                    # larga, la siguiente continúa sin perder nada.
RUEDAS = 2          # misma ventana de medición que el corrector en vivo


def cargar_eventos() -> list[dict]:
    """El banco de exámenes: los curados a mano (backtest_eventos.json) MÁS
    los que el cosechador fue sumando en GitHub (datos/cosecha.json). Se
    fusiona por `id` (lo local manda si hay choque) para que el catálogo
    crezca solo sin depender del disco efímero ni de un redeploy."""
    with open(RUTA_EVENTOS, encoding="utf-8") as archivo:
        locales = json.load(archivo)["eventos"]
    por_id = {}
    try:
        from contenido import respaldo
        for evento in respaldo.cosecha_remota():
            if evento.get("id") and evento.get("titular") and evento.get("simbolo"):
                por_id[evento["id"]] = evento
    except Exception:
        pass  # sin red o sin cosecha: el banco es solo lo local
    for evento in locales:  # lo curado a mano tiene prioridad sobre lo cosechado
        por_id[evento["id"]] = evento
    return sorted(por_id.values(), key=lambda e: e.get("fecha") or "")


def _variacion_historica(simbolo: str, fecha: str, ruedas: int = RUEDAS) -> dict | None:
    """Yahoo primero (histórico largo y completo: acciones, ETFs, cripto),
    Alpaca de respaldo. Stooq quedó fuera: su API de descarga dejó de
    responder (404), lo que estancaba el backtest en ~30 exámenes."""
    from contenido.fuentes import alpaca, yahoo

    return (yahoo.variacion_real(simbolo, fecha, ruedas)
            or alpaca.variacion_real(simbolo, fecha, ruedas))


def _seed(evento: dict) -> int:
    """Semilla determinística por evento: la fecha como número (AAAAMMDD)."""
    return int(evento["fecha"].replace("-", ""))


def _sim_id(evento: dict) -> str:
    return persistencia.id_simulacion(evento["titular"], _seed(evento))


# para eventos sin campo "mercado" (curados viejos), se infiere del símbolo
_SIMBOLOS_MERCADO = {
    "oro": {"GLD", "IAU", "GDX", "NEM", "GOLD"},
    "cripto": {"GBTC", "COIN", "MARA", "RIOT", "MSTR", "ETHE", "BITO", "BTC-USD"},
    "petroleo": {"USO", "XLE", "OXY", "SLB"},
    "indice": {"SPY", "QQQ", "DIA", "IWM"},
}


def _mercado_de(evento: dict) -> str:
    """El mercado de un evento: su campo `mercado`, o inferido del símbolo."""
    if evento.get("mercado"):
        return evento["mercado"]
    simbolo = (evento.get("simbolo") or "").upper()
    for mercado, simbolos in _SIMBOLOS_MERCADO.items():
        if simbolo in simbolos:
            return mercado
    return "accion"


def estado(conexion=None, mercado: str | None = None) -> dict:
    """Cuántos exámenes están rendidos (con nota real) y cuántos faltan.

    Con `mercado` (oro/cripto/petroleo/indice/accion) cuenta y rinde SOLO
    ese mercado — clave para calibrar de forma balanceada (100+/mercado) en
    vez de que las acciones, que son mayoría, se lleven todas las tandas.

    Cuenta lo local Y lo ya respaldado en GitHub: el disco de Render se
    borra con cada deploy, pero un examen en la caja fuerte no se repite
    (repetirlo costaría ~100 llamadas LLM cada vez)."""
    from contenido import respaldo

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        eventos = cargar_eventos()
        if mercado:
            eventos = [e for e in eventos if _mercado_de(e) == mercado]
        respaldados = {c.get("sim_id") for c in respaldo.casos_remotos()}
        pendientes = []
        for evento in eventos:
            if _sim_id(evento) in respaldados:
                continue  # la caja fuerte ya lo tiene
            fila = conexion.execute(
                "SELECT reaccion_real FROM simulaciones WHERE id = ?", (_sim_id(evento),)
            ).fetchone()
            if not (fila and fila["reaccion_real"]):
                pendientes.append(evento)
        return {"total": len(eventos), "hechos": len(eventos) - len(pendientes),
                "pendientes": len(pendientes), "_lista_pendiente": pendientes}
    finally:
        if propia:
            conexion.close()


def correr_tanda(conexion=None, tamano: int = TANDA_DEFECTO,
                 simular=None, obtener_variacion=None, mercado: str | None = None) -> dict:
    """Rinde una tanda de exámenes históricos. Devuelve el detalle.

    Con `mercado` rinde SOLO ese mercado (calibración balanceada).
    `simular` y `obtener_variacion` son inyectables para los tests;
    en producción usan el pipeline real y las barras de Alpaca.
    """
    if simular is None:
        from contenido import pipeline
        simular = lambda titular, seed: pipeline.simular_titular_completo(  # noqa: E731
            titular, seed, con_frames=False
        )
    if obtener_variacion is None:
        obtener_variacion = _variacion_historica

    tamano = max(1, min(int(tamano), TANDA_MAXIMA))
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        from contenido.corrector import cerebros_ia

        pendientes = estado(conexion, mercado=mercado)["_lista_pendiente"]
        # los recientes primero: sus datos (Alpaca) son los más confiables,
        # y así el avance no se atasca si la fuente antigua no responde
        pendientes.sort(key=lambda e: e["fecha"], reverse=True)
        hechas, sin_datos, sin_ia = [], [], []
        for evento in pendientes[:tamano]:
            # el precio real se consulta ANTES de simular: si no hay dato,
            # el examen se salta sin gastar ni una llamada LLM
            variacion = obtener_variacion(evento["simbolo"], evento["fecha"], RUEDAS)
            if variacion is None:
                sin_datos.append(evento["id"])  # la próxima tanda reintenta
                continue
            reporte, lideres, serie, _ = simular(evento["titular"], _seed(evento))
            if not cerebros_ia(lideres):
                # sin saldo de API los líderes usaron el respaldo léxico: el
                # examen NO se guarda — se rendirá de verdad cuando vuelva la IA
                sin_ia.append(evento["id"])
                break  # sin saldo no tiene sentido seguir gastando la tanda
            sim_id = persistencia.guardar_simulacion(
                conexion, titular=evento["titular"], fuente="backtest",
                seed=_seed(evento), resumen=reporte, lideres=lideres,
                serie_precios=serie, destacada=False,
            )
            persistencia.guardar_reaccion_real(
                conexion, sim_id, {**variacion, "categoria": evento["categoria"],
                                   "cerebros": "ia"}
            )
            hechas.append({"id": evento["id"], "sim_id": sim_id,
                           "sim_pct": reporte.get("direccion_pct"),
                           "real_pct": variacion["pct_real"]})
            # a la caja fuerte DESPUÉS DE CADA EXAMEN (no al final): si un
            # deploy reinicia el motor a mitad de tanda, lo rendido no se pierde
            try:
                from contenido import respaldo
                ultimo_respaldo = respaldo.respaldar(conexion)
            except Exception:
                ultimo_respaldo = None

            # liberar la memoria del modelo de 10.000 agentes ANTES del próximo
            # examen: los agentes y el modelo se referencian en ciclo, así que
            # sin un gc.collect() explícito la basura se acumula y en el plan
            # Starter (512 MB) puede desbordar y reiniciar el motor.
            del reporte, lideres, serie
            gc.collect()

        resultado = {"hechas": hechas, "sin_datos": sin_datos, "sin_ia": sin_ia,
                     "pendientes": len(pendientes) - len(hechas)}
        if hechas:
            resultado["respaldo"] = ultimo_respaldo
        return resultado
    finally:
        if propia:
            conexion.close()


# ---------- evaluación (medir una config SIN re-respaldar) ----------

def _ruta_evaluacion() -> Path:
    """Dónde se guarda el resultado de la última evaluación. En Render, junto a
    la base en el disco persistente; en local, junto al banco de exámenes."""
    db = os.environ.get("ENJAMBRE_DB")
    base = Path(db).parent if db else RUTA_EVENTOS.parent
    return base / "evaluaciones.json"


def _signo(x) -> int:
    if x is None:
        return 0
    return 1 if x > 0 else (-1 if x < 0 else 0)


# tanda máxima por corrida de evaluación: correr más de ~40 simulaciones de
# 10.000 agentes seguidas desborda la RAM (el backtest histórico se limita
# igual). La evaluación es RESUMIBLE, así que varias corridas cubren todo.
TANDA_EVAL_MAX = 40


def _ruta_progreso() -> Path:
    db = os.environ.get("ENJAMBRE_DB")
    base = Path(db).parent if db else RUTA_EVENTOS.parent
    return base / "evaluaciones_progreso.json"


def _cargar_progreso() -> dict:
    try:
        ruta = _ruta_progreso()
        if ruta.exists():
            return json.loads(ruta.read_text(encoding="utf-8")) or {}
    except Exception:
        pass
    return {}


def _guardar_progreso(progreso: dict) -> None:
    try:
        ruta = _ruta_progreso()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(progreso, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


CATS_VALIDAS = ("negativa", "positiva", "neutra")


def _simbolo_de_caso(caso: dict) -> str:
    """El primer símbolo de un caso respaldado (guarda `simbolos`, lista o
    cadena separada por comas)."""
    s = caso.get("simbolos")
    if isinstance(s, list):
        s = s[0] if s else ""
    return ((s or "").split(",")[0]).strip().upper()


def _mercado_de_caso(caso: dict) -> str:
    """El mercado de un caso respaldado: su campo `mercado`, o inferido del
    símbolo (mismo criterio que `_mercado_de` para eventos)."""
    if caso.get("mercado"):
        return caso["mercado"]
    simbolo = _simbolo_de_caso(caso)
    for mercado, simbolos in _SIMBOLOS_MERCADO.items():
        if simbolo in simbolos:
            return mercado
    return "accion"


def evaluar(tamano: int | None = None, mercado: str | None = None,
            peso: float | None = None, umbral: float | None = None,
            doomer: float | None = None, reiniciar: bool = False,
            simular=None, guardar: bool = True) -> dict:
    """Re-simula los exámenes YA respaldados bajo el código/entorno ACTUAL y
    mide el acierto de DIRECCIÓN por categoría, comparándolo con el resultado
    real ya conocido. Sirve para medir el impacto de un cambio (ej. P2) SIN
    tocar el respaldo histórico.

    - `peso`: si se pasa, fija ENJAMBRE_PESO_TONO_INVERSORES SOLO durante esta
      evaluación (para barrer valores de P2 sin re-desplegar ni cambiarlo en
      Render). Si es None, usa el valor vigente del entorno.
    - NO persiste simulaciones ni re-respalda: es una medición pura.
    - Usa la caché de cerebros: barato si está caliente, gasta si está fría.
    - Solo cuenta los exámenes que de verdad usaron el LLM (con_ia); si el
      motor cayó al respaldo léxico (sin saldo), lo reporta y no contamina.
    """
    import time

    from model import (_peso_invertidores_env, _umbral_correccion_env,
                       _peso_doomer_env, _peso_doomer_env_forzado)

    # Intervención 1: fija ENJAMBRE_PESO_DOOMER SOLO durante esta evaluación.
    if doomer is not None:
        previo = os.environ.get("ENJAMBRE_PESO_DOOMER")
        os.environ["ENJAMBRE_PESO_DOOMER"] = str(doomer)
        try:
            return evaluar(tamano=tamano, mercado=mercado, peso=peso, umbral=umbral,
                           doomer=None, reiniciar=reiniciar, simular=simular,
                           guardar=guardar)
        finally:
            if previo is None:
                os.environ.pop("ENJAMBRE_PESO_DOOMER", None)
            else:
                os.environ["ENJAMBRE_PESO_DOOMER"] = previo

    # Plan A: fija ENJAMBRE_UMBRAL_CORRECCION_SESGO SOLO durante esta evaluación
    # (para medir base vs corrección sin re-desplegar). Mismo patrón que `peso`.
    if umbral is not None:
        previo = os.environ.get("ENJAMBRE_UMBRAL_CORRECCION_SESGO")
        os.environ["ENJAMBRE_UMBRAL_CORRECCION_SESGO"] = str(umbral)
        try:
            return evaluar(tamano=tamano, mercado=mercado, peso=peso, umbral=None,
                           reiniciar=reiniciar, simular=simular, guardar=guardar)
        finally:
            if previo is None:
                os.environ.pop("ENJAMBRE_UMBRAL_CORRECCION_SESGO", None)
            else:
                os.environ["ENJAMBRE_UMBRAL_CORRECCION_SESGO"] = previo

    if peso is not None:
        previo = os.environ.get("ENJAMBRE_PESO_TONO_INVERSORES")
        os.environ["ENJAMBRE_PESO_TONO_INVERSORES"] = str(peso)
        try:
            return evaluar(tamano=tamano, mercado=mercado, peso=None, umbral=None,
                           reiniciar=reiniciar, simular=simular, guardar=guardar)
        finally:
            if previo is None:
                os.environ.pop("ENJAMBRE_PESO_TONO_INVERSORES", None)
            else:
                os.environ["ENJAMBRE_PESO_TONO_INVERSORES"] = previo

    if simular is None:
        from contenido import pipeline
        simular = lambda t, s: pipeline.simular_titular_completo(  # noqa: E731
            t, s, con_frames=False)
    from contenido import respaldo
    from contenido.corrector import cerebros_ia

    try:
        casos = respaldo.casos_remotos()
    except Exception:
        casos = []
    # Evaluación DIRECTA sobre los casos ya respaldados (traen titular + el
    # resultado real). NO se cruza con el banco de eventos: ese cruce por sim_id
    # es frágil (el raw y la API de GitHub sirven versiones distintas del
    # archivo) y daba 0 en Render. La semilla sale del propio sim_id, así que es
    # determinística por caso: la 1ª pasada calienta la caché de cerebros y las
    # siguientes (otros valores de peso) reusan esa caché — el barrido es barato.
    evaluables = []
    for c in casos:
        rr = c.get("reaccion_real") or {}
        if rr.get("pct_real") is None or rr.get("categoria") not in CATS_VALIDAS:
            continue
        if mercado and _mercado_de_caso(c) != mercado:
            continue
        evaluables.append(c)
    evaluables.sort(key=lambda c: c.get("fecha") or "", reverse=True)
    n_categorizados = len(evaluables)

    # progreso ACUMULADO por (mercado, peso), guardado en disco: cada corrida
    # simula a lo sumo una tanda (para no desbordar la RAM) de casos NUEVOS y
    # SUMA el resultado. Varias corridas cubren todo el mercado; re-correr no
    # repite lo ya hecho. `reiniciar` borra el progreso de esa (mercado, peso).
    peso_actual = _peso_invertidores_env(1.0)
    umbral_actual = _umbral_correccion_env(0.0)
    # Si el env fija un peso, ese override manda en TODOS los mercados (medición);
    # si no, el tono usa la SEGMENTACIÓN por-mercado (índice 1.0, cripto 0.0, …).
    # Se rotula "seg" para que la clave de progreso NO choque con dm0.0 (que es
    # doomer forzado a 0 en todos lados) y para que el reporte no mienta.
    doomer_forzado = _peso_doomer_env_forzado()
    doomer_actual = doomer_forzado if doomer_forzado is not None else "seg"
    # el progreso se acumula por (mercado, peso, umbral, doomer): así cada
    # combinación se mide aparte. `dm0.0` = doomer forzado a 0 (base); `dmseg` =
    # segmentado por mercado (producción).
    clave = f"{mercado or 'todos'}|peso{peso_actual}|umb{umbral_actual}|dm{doomer_actual}"
    progreso = _cargar_progreso()
    if reiniciar:
        progreso[clave] = {}
    hechos = progreso.setdefault(clave, {})

    pendientes = [c for c in evaluables if c["sim_id"] not in hechos]
    por_tanda = min(int(tamano), TANDA_EVAL_MAX) if tamano else TANDA_EVAL_MAX

    con_ia = sin_ia = 0
    for c in pendientes[:por_tanda]:
        rr = c["reaccion_real"]
        real, cat = rr["pct_real"], rr["categoria"]
        seed = int(c["sim_id"][:8], 16)  # semilla determinística por caso
        reporte, lideres, serie, _ = simular(c["titular"], seed)
        if cerebros_ia(lideres):
            con_ia += 1
        else:
            sin_ia += 1
        ok = 1 if _signo(reporte.get("direccion_pct")) == _signo(real) else 0
        hechos[c["sim_id"]] = {"cat": cat, "ok": ok}
        del reporte, lideres, serie
        gc.collect()
    nuevos = min(len(pendientes), por_tanda)
    if guardar:
        _guardar_progreso(progreso)

    # acierto ACUMULADO sobre todo lo hecho para (mercado, peso)
    cats = {"negativa": [0, 0], "positiva": [0, 0], "neutra": [0, 0]}
    for r in hechos.values():
        if r.get("cat") in cats:
            cats[r["cat"]][1] += 1
            cats[r["cat"]][0] += r.get("ok", 0)

    def _acc(par):
        return {"aciertos": par[0], "total": par[1],
                "acierto": round(par[0] / par[1], 4) if par[1] else None}

    tot = sum(c[1] for c in cats.values())
    ok = sum(c[0] for c in cats.values())
    resultado = {
        "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "peso_tono_invertidores": peso_actual,
        "umbral_correccion_sesgo": umbral_actual,
        "peso_doomer": doomer_actual,
        "evaluados": tot, "con_ia": con_ia, "sin_ia": sin_ia,
        "acierto_global": round(ok / tot, 4) if tot else None,
        "negativa": _acc(cats["negativa"]), "positiva": _acc(cats["positiva"]),
        "neutra": _acc(cats["neutra"]),
        # progreso ACUMULADO: cuántos exámenes llevamos de este (mercado, peso)
        "progreso": {"hechos": tot, "total": n_categorizados,
                     "faltan": n_categorizados - tot,
                     "nuevos_esta_tanda": nuevos,
                     "completo": tot >= n_categorizados},
        # diagnóstico: para ver de dónde sale un 0
        "diag": {"casos_respaldados": len(casos),
                 "casos_categorizados": n_categorizados},
    }
    if guardar:
        _registrar_evaluacion(resultado)
    return resultado


def _registrar_evaluacion(resultado: dict) -> None:
    """Guarda el resultado (con un pequeño historial) para que el endpoint GET
    lo devuelva. Nunca lanza."""
    try:
        ruta = _ruta_evaluacion()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        historial = []
        if ruta.exists():
            historial = (json.loads(ruta.read_text(encoding="utf-8")) or {}).get("historial", [])
        historial.append(resultado)
        ruta.write_text(json.dumps({"ultima": resultado, "historial": historial[-20:]},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        pass


def ultima_evaluacion() -> dict | None:
    """El último resultado de evaluación guardado (para el endpoint GET)."""
    try:
        ruta = _ruta_evaluacion()
        if ruta.exists():
            return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None
