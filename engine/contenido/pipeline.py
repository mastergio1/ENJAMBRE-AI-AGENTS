"""El ritual de la madrugada — versión Etapa 7 (pasos 1, 2, 3 y 7).

Recolecta los titulares, el portero elige el top 3 del día, se simulan
con seeds fijas (reproducibilidad), se guardan CON frames (el replay 3D
del muro) y quedan marcadas como destacadas.

Los pasos 4-6 y 8 (captura, boletín, envío, aviso a Telegram) llegan en
la Etapa 8. Uso manual: python -m contenido.pipeline
"""

from datetime import date, datetime, timezone

from contenido import persistencia, portero
from contenido.fuentes import alpaca

MAXIMO_DIARIO = 3  # presupuesto de CONTENIDO.md — no negociable


def simular_titular_completo(titular: str, seed: int, con_frames: bool = False):
    """Corre una simulación completa fuera del WebSocket (para el pipeline).

    Devuelve (reporte, lideres_datos, serie_precios, frames).
    """
    # imports tardíos: el pipeline se importa sin levantar FastAPI
    from collections import defaultdict

    import server
    from agents.lider import LiderOpinion
    from brains.cerebro import analizar_titular
    from model import MercadoEnjambre

    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=server.TICKS_CALENTAMIENTO + server.TICKS_POSTERIORES)
    modelo.correr(server.TICKS_CALENTAMIENTO)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]
    respuestas = analizar_titular(titular, [(l.unique_id, l.arquetipo) for l in lideres])

    contador = defaultdict(lambda: [0, 0])
    frames: list[bytes] = []

    def avanzar():
        modelo.step()
        server._contar_acciones(modelo, contador)
        if con_frames:
            frames.append(server._paquete_tick(modelo))

    for _ in range(server.TICKS_PREVIOS):
        avanzar()
    precio_previo = modelo.historial_precios[-1]
    contador.clear()
    modelo.aplicar_titular(titular, respuestas=respuestas)
    for _ in range(server.TICKS_POSTERIORES):
        avanzar()

    reporte = server._generar_reporte(modelo, precio_previo, respuestas, lideres, contador)
    lideres_datos = [
        {"arquetipo": lider.arquetipo, **{k: r[k] for k in ("senal", "confianza", "frase")}}
        for lider, r in zip(lideres, respuestas)
    ]
    serie = modelo.historial_precios[-(server.TICKS_PREVIOS + server.TICKS_POSTERIORES + 1):]
    return reporte, lideres_datos, serie, frames


def preparar_dia(conexion=None, maximo: int = MAXIMO_DIARIO, semilla_base: int | None = None) -> dict:
    """Pasos 1-3 y 7 del ritual: recolectar, filtrar, simular, publicar.

    Idempotente: si hoy ya hay `maximo` destacadas, no gasta de nuevo.
    """
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        hoy = datetime.now(timezone.utc).strftime("%Y-%m")
        destacadas_hoy = [
            s for s in persistencia.listar_simulaciones(conexion, solo_destacadas=True, limite=10)
            if s["fecha"][:10] == persistencia.ahora_iso()[:10]
        ]
        if len(destacadas_hoy) >= maximo:
            return {"origen": "sin cambios", "publicadas": [], "motivo": "el día ya estaba preparado"}

        # 1. RECOLECTAR (con degradación elegante a demo)
        titulares, origen = alpaca.obtener_titulares(horas=18, limite=50)
        # 2. FILTRAR
        resultado = portero.procesar_dia(conexion, titulares, maximo=maximo)
        # 3. SIMULAR con seeds fijas del día + 7. PUBLICAR como destacadas
        semilla_base = semilla_base if semilla_base is not None else int(date.today().strftime("%Y%m%d"))
        publicadas = []
        for indice, elegido in enumerate(resultado["elegidos"][: maximo - len(destacadas_hoy)]):
            seed = semilla_base + indice
            reporte, lideres_datos, serie, frames = simular_titular_completo(
                elegido["titular"], seed, con_frames=True
            )
            sim_id = persistencia.guardar_simulacion(
                conexion,
                titular=elegido["titular"],
                fuente=elegido.get("fuente", "alpaca"),
                seed=seed,
                resumen=reporte,
                lideres=lideres_datos,
                serie_precios=serie,
                frames_ref=persistencia.guardar_frames(
                    persistencia.id_simulacion(elegido["titular"], seed), frames
                ),
                destacada=True,
            )
            persistencia.vincular_simulacion(conexion, persistencia.id_titular(elegido["titular"]), sim_id)
            publicadas.append({"sim_id": sim_id, "titular": elegido["titular"], "impacto": elegido["impacto"]})

        return {"origen": origen, "publicadas": publicadas, "log": resultado["log"]}
    finally:
        if propia:
            conexion.close()


def ritual_matutino(conexion=None, maximo: int = MAXIMO_DIARIO, semilla_base: int | None = None,
                    enviar: bool = True) -> dict:
    """El ritual completo (CONTENIDO.md sección 6.1): prepara el día
    (pasos 1-3, 7) y luego redacta y envía El Pulso (pasos 5-6) y avisa a
    Giorgio (paso 8). El paso 4 (imagen) se sirve on-the-fly desde el
    endpoint /api/simulacion/{id}/imagen — no hace falta pre-renderizar.

    `enviar=False` arma todo pero no manda correos (para pruebas/preview).
    """
    from datetime import datetime, timezone

    from contenido import boletin, notificar, redaccion

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        preparado = preparar_dia(conexion, maximo=maximo, semilla_base=semilla_base)

        # el corrector automático: guarda cuánto se movió de verdad el
        # símbolo de las destacadas de días anteriores (calibración).
        # El ritual jamás se cae por el corrector.
        try:
            from contenido import corrector
            correccion = corrector.corregir_pendientes(conexion)
        except Exception:
            correccion = None

        # reúne las destacadas de hoy con sus voces (para el correo)
        destacadas = _destacadas_de_hoy(conexion)

        # La Redacción: el análisis de mercado del día, DINÁMICO. El universo
        # sale de los titulares que el portero evaluó hoy (sus tickers), así
        # el brief cambia cada día. "Qué observa hoy" = las destacadas.
        radar = [d["titular"] for d in destacadas]
        evaluadas = preparado.get("log", [])
        brief = redaccion.preparar_brief(evaluadas=evaluadas, radar=radar)
        persistencia.guardar_brief(conexion, persistencia.ahora_iso()[:10], brief)

        envio = None
        html = None
        if destacadas:
            fecha = _fecha_es(datetime.now(timezone.utc))
            html = boletin.construir_html(destacadas, fecha, brief=brief)  # preview
            if enviar:
                envio = _enviar_con_brief(conexion, destacadas, fecha, brief)

        # paso 8: avisar a Giorgio
        notificar.avisar(notificar.resumen_ejecucion(preparado["origen"], preparado["publicadas"], envio))

        return {**preparado, "destacadas": len(destacadas), "envio": envio,
                "brief": brief, "html_preview": html, "correccion": correccion}
    finally:
        if propia:
            conexion.close()


def _enviar_con_brief(conexion, destacadas, fecha, brief) -> dict:
    """Como boletin.enviar_pulso pero incluyendo el análisis de mercado."""
    from contenido import boletin

    activos = persistencia.suscriptores_activos(conexion)
    asunto = boletin.asunto_del_dia(destacadas[0])
    enviados = 0
    for suscriptor in activos:
        html = boletin.construir_html(destacadas, fecha, token_baja=suscriptor["token_baja"], brief=brief)
        if boletin.enviar(suscriptor["email"], asunto, html):
            enviados += 1
    return {"suscriptores": len(activos), "enviados": enviados, "fallidos": len(activos) - enviados}


def _destacadas_de_hoy(conexion) -> list[dict]:
    """Las destacadas de hoy con resumen + voces, listas para el boletín."""
    hoy = persistencia.ahora_iso()[:10]
    resultado = []
    for fila in persistencia.listar_simulaciones(conexion, solo_destacadas=True, limite=10):
        if fila["fecha"][:10] != hoy:
            continue
        datos = persistencia.obtener_simulacion(conexion, fila["id"])
        if datos:
            resultado.append({
                "sim_id": datos["id"],
                "titular": datos["titular"],
                "resumen": {**datos["resumen"], "agitacion": _agitacion(datos["resumen"])},
                "lideres_frases": datos["lideres"],
            })
    return resultado


def _agitacion(resumen: dict) -> str:
    vol = resumen.get("volatilidad_pct", 0)
    return "bajo" if vol < 1.0 else "medio" if vol < 2.0 else "alto"


def _fecha_es(dt) -> str:
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month - 1]}"


if __name__ == "__main__":
    import sys

    enviar = "--enviar" in sys.argv
    resultado = ritual_matutino(enviar=enviar)
    print(f"fuente: {resultado['origen']}")
    for publicada in resultado.get("publicadas", []):
        print(f"  ★ [{publicada['impacto']}/10] {publicada['titular']}  → sim {publicada['sim_id']}")
    if resultado.get("envio"):
        e = resultado["envio"]
        print(f"correos: {e['enviados']}/{e['suscriptores']} enviados")
    elif resultado.get("destacadas"):
        print(f"boletín armado ({resultado['destacadas']} destacadas); envío desactivado (usa --enviar)")
    if not resultado.get("publicadas"):
        print(f"  ({resultado.get('motivo', 'sin titulares elegibles')})")
