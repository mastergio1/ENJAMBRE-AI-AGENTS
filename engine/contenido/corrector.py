"""El corrector automático — paso 2 de la ruta de calibración.

Uno o dos días de mercado después de cada destacada, consulta cuánto se
movió su símbolo EN EL MERCADO REAL (Alpaca, barras diarias) y lo guarda:

- estructurado en `simulaciones.reaccion_real` (la materia prima de la
  libreta de calificaciones), y
- como epílogo "¿y qué pasó después?" SOLO si Giorgio no escribió uno a
  mano (lo manual siempre manda).

Línea CMF: el texto cuenta el pasado y se declara comparación educativa;
pasa por vocabulario.es_publicable antes de guardarse. Si Alpaca no
responde o la ventana aún no se completa, la simulación queda pendiente
y se reintenta en la próxima corrida — el corrector nunca lanza.
"""

import json
from datetime import datetime, timedelta, timezone
from statistics import mean

from contenido import persistencia, vocabulario

DIAS_ESPERA = 1    # edad mínima de una destacada antes de intentar corregirla
RUEDAS = 2         # ventana de medición: días de mercado tras la noticia
UMBRAL_PLANO = 0.3  # bajo este |%|, la dirección se considera plana


def cerebros_ia(lideres: list[dict]) -> bool:
    """¿La mayoría de los líderes habló con IA real (no con el respaldo)?

    Sin saldo de API el enjambre sigue funcionando con el cerebro léxico,
    pero la calibración solo debe medir al titular, no al suplente.
    Si los líderes no traen `fuente` (registros antiguos), se asume IA."""
    fuentes = [l.get("fuente") for l in (lideres or []) if l.get("fuente")]
    if not fuentes:
        return True
    ia = sum(1 for f in fuentes if f in ("api", "cache"))
    return ia > len(fuentes) / 2


def corregir_pendientes(conexion=None, obtener_variacion=None, limite: int = 10,
                        dias_espera: int = DIAS_ESPERA, ruedas: int = RUEDAS) -> dict:
    """Corrige las destacadas pendientes. Devuelve {corregidas, esperando}."""
    from contenido.fuentes import alpaca

    obtener_variacion = obtener_variacion or alpaca.variacion_real
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        antes_de = (datetime.now(timezone.utc) - timedelta(days=dias_espera)).isoformat(
            timespec="seconds"
        )
        pendientes = persistencia.destacadas_sin_correccion(conexion, antes_de, limite)
        corregidas, esperando = [], 0
        for sim in pendientes:
            simbolo = (sim["simbolos"] or "").split(",")[0].strip().upper()
            variacion = obtener_variacion(simbolo, sim["fecha"], ruedas) if simbolo else None
            if variacion is None:
                esperando += 1  # sin datos todavía: la próxima corrida reintenta
                continue
            # la etiqueta ia/respaldo viaja con la nota: la libreta solo
            # califica al titular (IA real), nunca al suplente léxico
            lideres = json.loads(sim.get("lideres_json") or "[]")
            variacion = {**variacion,
                         "cerebros": "ia" if cerebros_ia(lideres) else "respaldo"}
            persistencia.guardar_reaccion_real(conexion, sim["id"], variacion)
            if not (sim["epilogo"] or "").strip():
                resumen = json.loads(sim["resumen_json"])
                texto = _texto_epilogo(resumen.get("direccion_pct", 0), variacion)
                if vocabulario.es_publicable(texto):
                    persistencia.guardar_epilogo(conexion, sim["id"], texto)
            corregidas.append({"sim_id": sim["id"], "simbolo": simbolo,
                               "pct_real": variacion["pct_real"]})
        resultado = {"corregidas": corregidas, "esperando": esperando}
        if corregidas:
            # caja fuerte: el acumulado se respalda en GitHub (rama aparte);
            # si falla, el corrector no se cae — reintenta con la próxima
            try:
                from contenido import respaldo
                resultado["respaldo"] = respaldo.respaldar(conexion)
            except Exception:
                resultado["respaldo"] = None
        return resultado
    finally:
        if propia:
            conexion.close()


def _texto_epilogo(direccion_pct: float, variacion: dict) -> str:
    """El '¿y qué pasó después?' automático, en pasado y tono educativo."""
    pct_sim = float(direccion_pct or 0)
    rumbo = ("una subida" if pct_sim > UMBRAL_PLANO
             else "una caída" if pct_sim < -UMBRAL_PLANO
             else "una reacción plana")
    return (
        f"El enjambre simuló {rumbo} de {pct_sim:+.1f}%. En el mercado real, "
        f"{variacion['simbolo']} cerró en {variacion['cierre_final']} "
        f"el {variacion['fecha_final']} (venía de {variacion['cierre_base']} "
        f"el {variacion['fecha_base']}): {variacion['pct_real']:+.1f}% en "
        f"{variacion['ruedas']} días de mercado. Registro del corrector "
        "automático con fines educativos: la simulación modela comportamiento "
        "de masas, no el precio futuro."
    )


def _signo(x: float) -> int:
    return 0 if abs(x) < UMBRAL_PLANO else (1 if x > 0 else -1)


def _resumir(casos: list[tuple[float, float]]) -> dict:
    """Las métricas de un conjunto de casos (sim_pct, real_pct)."""
    evaluables = [(s, r) for s, r in casos if _signo(s) or _signo(r)]
    aciertos = sum(1 for s, r in evaluables if _signo(s) == _signo(r))
    return {
        "casos": len(casos),
        "evaluables": len(evaluables),  # al menos un lado se movió
        "aciertos_direccion": aciertos,
        "tasa_acierto": round(aciertos / len(evaluables), 2) if evaluables else None,
        "magnitud_media_sim": round(mean(abs(s) for s, _ in casos), 2) if casos else None,
        "magnitud_media_real": round(mean(abs(r) for _, r in casos), 2) if casos else None,
    }


def libreta(conexion=None) -> dict:
    """La libreta de calificaciones: enjambre vs mercado real, acumulado.

    Es la brújula de la calibración (¿acierta la dirección? ¿exagera?),
    no una métrica de marketing. Separa lo EN VIVO (destacadas corregidas
    día a día) de lo HISTÓRICO (backtest): peras con peras.
    """
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        filas = conexion.execute(
            "SELECT resumen_json, reaccion_real, fuente FROM simulaciones "
            "WHERE reaccion_real IS NOT NULL AND (destacada = 1 OR fuente = 'backtest')"
        ).fetchall()
    finally:
        if propia:
            conexion.close()

    vivo, historico, excluidos = [], [], 0
    for fila in filas:
        reaccion = json.loads(fila["reaccion_real"])
        if reaccion.get("cerebros") == "respaldo":
            excluidos += 1  # simulado sin IA (sin saldo): no califica al titular
            continue
        sim = float(json.loads(fila["resumen_json"]).get("direccion_pct") or 0)
        real = float(reaccion.get("pct_real") or 0)
        (historico if fila["fuente"] == "backtest" else vivo).append((sim, real))

    return {
        **_resumir(vivo + historico),
        "en_vivo": _resumir(vivo),
        "historico": _resumir(historico),
        "excluidos_respaldo": excluidos,
        "nota": "con menos de 30 casos, la tasa es anecdótica — seguir acumulando",
    }
