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
    from brains import reparto
    from brains.cerebro import analizar_titular
    from model import MercadoEnjambre

    from brains.mercado import clasificar, perfil_de

    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=server.TICKS_CALENTAMIENTO + server.TICKS_POSTERIORES)
    modelo.correr(server.TICKS_CALENTAMIENTO)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]
    # 1000 líderes comparten ~110 cerebros (presupuesto de la biblia)
    consultas, asignacion = reparto.planificar(lideres, lambda uid: uid)
    from contenido import vocabulario
    # filtro CMF a las voces de los líderes antes de que se guarden y se sirvan
    respuestas = reparto.expandir(
        vocabulario.sanear_frases(analizar_titular(titular, consultas)), asignacion)
    # el enjambre razona el TIPO de mercado y aplica su personalidad
    perfil = perfil_de(clasificar(titular))

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
    modelo.aplicar_titular(titular, respuestas=respuestas, perfil=perfil)
    for _ in range(server.TICKS_POSTERIORES):
        avanzar()

    reporte = server._generar_reporte(modelo, precio_previo, respuestas, lideres, contador)
    reporte["mercado"] = perfil["tipo"]            # el tipo detectado (calibración/UI)
    reporte["mercado_etiqueta"] = perfil["etiqueta"]
    lideres_datos = [
        # `fuente` viaja con cada líder: la calibración necesita saber si la
        # voz fue IA real o el respaldo léxico (sin saldo, el suplente juega)
        {"arquetipo": lider.arquetipo, "fuente": r.get("fuente", "fallback"),
         **{k: r[k] for k in ("senal", "confianza", "frase")}}
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
                    enviar: bool = True, cuando: dict | None = None) -> dict:
    """El ritual completo (CONTENIDO.md sección 6.1): prepara el día
    (pasos 1-3, 7) y luego redacta y envía El Pulso (pasos 5-6) y avisa a
    Giorgio (paso 8). El paso 4 (imagen) se sirve on-the-fly desde el
    endpoint /api/simulacion/{id}/imagen — no hace falta pre-renderizar.

    `enviar=False` arma todo pero no manda correos (para pruebas/preview).
    """
    from datetime import datetime, timezone

    from contenido import boletin, notificar, redaccion, redaccion_ia

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        # ¿qué día es? (hora local del lector). El fin de semana El Pulso cambia
        # de marcha: SÁBADO = resumen de la semana; DOMINGO = deep-dive de una
        # mid/small-cap o sector. `cuando` se puede inyectar (tests).
        cuando = cuando or redaccion_ia.contexto_temporal()
        dia = cuando.get("weekday")
        es_finde = cuando.get("es_finde", dia in (5, 6) if dia is not None else False)
        es_sabado = dia == 5
        # sin weekday (cuando antiguo inyectado) pero es finde → se trata como domingo
        es_domingo = dia == 6 or (es_finde and dia is None)

        if es_finde:
            # sin simulaciones nuevas ni gasto de enjambre: el fin de semana es
            # lectura pausada. Un solo llamado LLM (el redactor del finde).
            preparado = {"origen": "fin de semana", "publicadas": [], "log": []}
        else:
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
        destacadas = [] if es_finde else _destacadas_de_hoy(conexion)

        # La Redacción: el análisis de mercado del día, DINÁMICO. El universo
        # sale de los titulares que el portero evaluó hoy (sus tickers), así
        # el brief cambia cada día. "Qué observa hoy" = las destacadas.
        radar = [d["titular"] for d in destacadas]
        evaluadas = preparado.get("log", [])
        brief = redaccion.preparar_brief(evaluadas=evaluadas, radar=radar)

        if es_sabado:
            # ── SÁBADO: RESUMEN DE LA SEMANA. Los grandes temas con punto de vista
            # (qué pasó, por qué, geopolítica/macro → mercado, qué observar). NUNCA
            # predicción (marco CMF). Degrada a None sin romperse.
            try:
                from contenido import resumen_semanal
                resumen = resumen_semanal.preparar_resumen(conexion, cuando=cuando)
                brief["resumen"] = resumen
                brief["resumen_redactado"] = (
                    redaccion_ia.redactar_resumen(resumen, cuando=cuando) if resumen else None)
            except Exception:
                brief["resumen"] = None
                brief["resumen_redactado"] = None
        elif es_domingo:
            # ── DOMINGO: DEEP-DIVE de una empresa mediana/pequeña o un sector en
            # rotación. Contexto + números verificados + debate de arquetipos +
            # gráfico real. NUNCA consejo de inversión (marco CMF).
            try:
                from contenido import analisis_semanal
                analisis = analisis_semanal.preparar_analisis(cuando=cuando)
                brief["analisis"] = analisis
                brief["analisis_redactado"] = (
                    redaccion_ia.redactar_analisis(analisis, cuando=cuando) if analisis else None)
            except Exception:
                brief["analisis"] = None
                brief["analisis_redactado"] = None
        else:
            # el redactor de IA le pone VOZ al brief (prompt maestro aprobado).
            # Si no hay clave/IA o algo falla, redactar() devuelve None y el correo
            # usa su plantilla.
            try:
                enjambre = None
                if destacadas:
                    d0 = destacadas[0]
                    enjambre = {"titular": d0["titular"],
                                "direccion_pct": d0["resumen"].get("direccion_pct"),
                                "volatilidad": d0["resumen"].get("agitacion")}
                brief["redactado"] = redaccion_ia.redactar(brief, enjambre)
            except Exception:
                brief["redactado"] = None

        # ── CENTRO DE MANDO: se GENERA y se GUARDA como 'pendiente'; NO se envía
        # a los suscriptores hasta el visto bueno de Giorgio. Se le manda un
        # correo de REVISIÓN (a su propio correo → funciona aun sin dominio).
        import secrets

        fecha_iso = persistencia.ahora_iso()[:10]
        fecha_es = _fecha_es(datetime.now(timezone.utc))
        # hay edición si hay destacadas (entre semana), resumen (sábado) o
        # deep-dive (domingo)
        sabado_listo = es_sabado and isinstance(brief.get("resumen_redactado"), dict)
        domingo_listo = es_domingo and isinstance(brief.get("analisis_redactado"), dict)
        finde_listo = sabado_listo or domingo_listo
        html_preview = None
        token = None
        if destacadas or finde_listo:
            html_preview = boletin.construir_html(
                destacadas, fecha_es, token_baja=persistencia.TOKEN_BAJA_SENTINEL, brief=brief)
            if sabado_listo:
                asunto = boletin.asunto_resumen(brief.get("resumen"))
            elif domingo_listo:
                asunto = boletin.asunto_finde(brief["analisis"])
            else:
                asunto = boletin.asunto_del_dia(destacadas[0])
            token = secrets.token_urlsafe(24)
            persistencia.guardar_edicion(conexion, fecha_iso, brief, html_preview,
                                         asunto, token, persistencia.ahora_iso())
            n_susc = len(persistencia.suscriptores_activos(conexion))
            if enviar:  # 'enviar' ahora = mandar el correo de REVISIÓN (no a suscriptores)
                boletin.enviar_revision(fecha_es, html_preview, token, n_susc)
        else:
            persistencia.guardar_brief(conexion, fecha_iso, brief)  # sin edición: solo el brief

        # paso 8: avisar a Giorgio que la edición espera su revisión
        notificar.avisar(notificar.resumen_ejecucion(preparado["origen"], preparado["publicadas"], None))

        edicion = ("resumen" if sabado_listo else "finde" if domingo_listo
                   else "diaria" if destacadas else "ninguna")
        return {**preparado, "destacadas": len(destacadas),
                "estado": "pendiente" if (destacadas or finde_listo) else "sin_edicion",
                "edicion": edicion,
                "brief": brief, "html_preview": html_preview, "token": token,
                "correccion": correccion}
    finally:
        if propia:
            conexion.close()


def aprobar_y_enviar(conexion=None, fecha: str | None = None) -> dict:
    """El visto bueno: envía la edición del día a los suscriptores (idéntica a lo
    revisado) y la marca 'enviada'. Idempotente: si ya se envió, no repite."""
    from contenido import boletin

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        fecha = fecha or persistencia.ahora_iso()[:10]
        ed = persistencia.obtener_edicion(conexion, fecha)
        if ed is None or not ed.get("html_preview"):
            return {"ok": False, "motivo": "no hay edición para ese día"}
        if ed["estado"] == "enviada":
            return {"ok": True, "ya_enviada": True,
                    "enviados": ed["enviados"], "suscriptores": ed["suscriptores"]}
        if ed["estado"] == "descartada":
            return {"ok": False, "motivo": "la edición fue descartada"}
        # el deep-dive del domingo es Premium: gratis → teaser; de pago → completo
        teaser_html, asunto_teaser = boletin.teaser_para(ed.get("brief"), fecha)
        conteo = boletin.enviar_a_suscriptores(
            conexion, ed["html_preview"], ed["asunto"] or "El Pulso", fecha_edicion=fecha,
            teaser_html=teaser_html, asunto_teaser=asunto_teaser)
        persistencia.marcar_enviada(conexion, fecha, conteo["enviados"],
                                    conteo["suscriptores"], persistencia.ahora_iso())
        return {"ok": True, **conteo}
    finally:
        if propia:
            conexion.close()


def reenviar_a_suscriptores(conexion=None, fecha: str | None = None) -> dict:
    """Reenvía la edición del día a TODOS los suscriptores activos, aunque YA se
    haya enviado (envío manual a pedido de Giorgio). A diferencia de
    aprobar_y_enviar, NO es idempotente: reenvía a propósito. Requiere que exista
    el preview y que la edición no esté descartada."""
    from contenido import boletin

    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        fecha = fecha or persistencia.ahora_iso()[:10]
        ed = persistencia.obtener_edicion(conexion, fecha)
        if ed is None or not ed.get("html_preview"):
            return {"ok": False, "motivo": "no hay edición para ese día"}
        if ed["estado"] == "descartada":
            return {"ok": False, "motivo": "la edición fue descartada"}
        # el deep-dive del domingo es Premium: gratis → teaser; de pago → completo
        teaser_html, asunto_teaser = boletin.teaser_para(ed.get("brief"), fecha)
        conteo = boletin.enviar_a_suscriptores(
            conexion, ed["html_preview"], ed["asunto"] or "El Pulso", fecha_edicion=fecha,
            teaser_html=teaser_html, asunto_teaser=asunto_teaser)
        persistencia.marcar_enviada(conexion, fecha, conteo["enviados"],
                                    conteo["suscriptores"], persistencia.ahora_iso())
        return {"ok": True, "reenviada": True, **conteo}
    finally:
        if propia:
            conexion.close()


def descartar_edicion(conexion=None, fecha: str | None = None) -> dict:
    """Descarta la edición del día (no se enviará)."""
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        fecha = fecha or persistencia.ahora_iso()[:10]
        ok = persistencia.set_estado_edicion(conexion, fecha, "descartada")
        return {"ok": ok}
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
