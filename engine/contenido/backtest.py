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

import json
from pathlib import Path

from contenido import persistencia

RUTA_EVENTOS = Path(__file__).parent / "backtest_eventos.json"
TANDA_DEFECTO = 5
TANDA_MAXIMA = 10   # freno duro de presupuesto por corrida
RUEDAS = 2          # misma ventana de medición que el corrector en vivo


def cargar_eventos() -> list[dict]:
    with open(RUTA_EVENTOS, encoding="utf-8") as archivo:
        return json.load(archivo)["eventos"]


def _variacion_historica(simbolo: str, fecha: str, ruedas: int = RUEDAS) -> dict | None:
    """Alpaca primero (cubre ~2016→hoy); Stooq de plan B para lo antiguo."""
    from contenido.fuentes import alpaca, stooq

    return (alpaca.variacion_real(simbolo, fecha, ruedas)
            or stooq.variacion_real(simbolo, fecha, ruedas))


def _seed(evento: dict) -> int:
    """Semilla determinística por evento: la fecha como número (AAAAMMDD)."""
    return int(evento["fecha"].replace("-", ""))


def _sim_id(evento: dict) -> str:
    return persistencia.id_simulacion(evento["titular"], _seed(evento))


def estado(conexion=None) -> dict:
    """Cuántos exámenes están rendidos (con nota real) y cuántos faltan.

    Cuenta lo local Y lo ya respaldado en GitHub: el disco de Render se
    borra con cada deploy, pero un examen en la caja fuerte no se repite
    (repetirlo costaría ~100 llamadas LLM cada vez)."""
    from contenido import respaldo

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        eventos = cargar_eventos()
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
                 simular=None, obtener_variacion=None) -> dict:
    """Rinde una tanda de exámenes históricos. Devuelve el detalle.

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

        pendientes = estado(conexion)["_lista_pendiente"]
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

        resultado = {"hechas": hechas, "sin_datos": sin_datos, "sin_ia": sin_ia,
                     "pendientes": len(pendientes) - len(hechas)}
        if hechas:
            resultado["respaldo"] = ultimo_respaldo
        return resultado
    finally:
        if propia:
            conexion.close()
