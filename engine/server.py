"""Servidor de El Enjambre — FastAPI + WebSocket.

Flujo: el navegador se conecta a /ws y envía un titular. El servidor
corre el mercado real (5.000 agentes), hace que los 100 líderes lean la
noticia (LLM con fallback) y transmite cada tick al frontend:

- mensaje de texto "inicio": las respuestas de los líderes
- un frame binario por tick: [precio f32][tick u32][sentimiento i8 × N_agentes]
  (N_agentes es dinámico: len(agentes_ordenados) — hoy 10.000)
- mensaje de texto "fin": el reporte de la simulación

El sentimiento por agente viaja como un byte (-127..127): la escena 3D
solo necesita saber cuánto pánico o codicia siente cada partícula.
"""

import asyncio
import base64
import contextlib as _contextlib
import hashlib
import hmac
import json
import struct
from collections import defaultdict

import os

from fastapi import BackgroundTasks, FastAPI, Header, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agents.lider import LiderOpinion
from brains.arquetipos import POR_ID
from brains.cerebro import analizar_titular_async
from contenido import limites, persistencia, portero, seguridad
from contenido.vocabulario import DISCLAIMER
from model import MercadoEnjambre

TICKS_CALENTAMIENTO = 60  # el mercado encuentra su ritmo (no se transmite)
TICKS_PREVIOS = 10        # calma visible antes de la noticia
TICKS_POSTERIORES = 140   # la reacción completa
RITMO_DEFECTO = 0.08      # segundos entre ticks transmitidos
RITMO_MINIMO = 0.02       # piso: nadie pide ticks sin pausa (protege la CPU)
MAX_TITULAR = 1200        # caracteres: cabe un tweet presidencial completo
MAX_MENSAJE_WS = 4000     # bytes de texto por mensaje del cliente
MAX_SIM_CONCURRENTES = 2  # simulaciones pesadas en vuelo a la vez
MENSAJE_PRIVADO = (
    "El Enjambre está en pruebas privadas. Puedes explorar el muro y el "
    "archivo; para soltar tus propios titulares, escríbenos desde "
    "«El Enjambre para tu organización»."
)
MENSAJE_CORREO = (
    "Deja tu correo para soltar tu propio titular al enjambre. De paso te "
    "suscribes gratis a El Pulso, el diario diario del enjambre. Un solo dato, "
    "sin contraseñas."
)


def _puerta_correo_activa() -> bool:
    """Decisión de Giorgio: El Enjambre es una herramienta GRATIS y abierta, sin
    suscripción obligatoria para usarla. La puerta de correo queda DESACTIVADA de
    forma permanente — suscribirse a El Pulso es siempre opcional. (Si alguien
    deja su correo al soltar un titular, se captura como lead sin bloquear nada.)"""
    return False


def _puerta_simulacion(mensaje: dict) -> tuple[bool, str | None]:
    """¿Puede esta persona soltar un titular? Devuelve (permitido, correo).

    - En pruebas privadas: solo la clave del equipo abre.
    - En público CON puerta de correo (ENJAMBRE_PUERTA_CORREO=1): un CORREO
      válido abre y queda suscrito gratis (cada simulación deja un lead).
    - En público sin la puerta: abierto (comportamiento de siempre). En todos
      los casos, si la persona dejó un correo válido, se captura igual.
    """
    email = str(mensaje.get("email", "")).strip().lower()
    correo = email if seguridad.correo_valido(email) else None
    if seguridad.acceso_privado_activo():
        return (True, correo) if seguridad.acceso_ok(mensaje.get("acceso")) else (False, None)
    if _puerta_correo_activa():
        return (True, correo) if correo else (False, None)
    return True, correo


def _suscribir_silencioso(email: str) -> None:
    """Captura el lead SIN bloquear la simulación: alta + correo de confirmación
    (double opt-in). Corre en su propio hilo; cualquier falla se traga para no
    apagar el momento mágico de ver al enjambre."""
    try:
        conexion = persistencia.conectar()
        try:
            alta = persistencia.agregar_suscriptor(conexion, email, origen="web")
        finally:
            conexion.close()
        if not alta.get("ya_activo") and alta.get("reenviar", True):
            from contenido import boletin
            boletin.enviar_confirmacion(email, alta["token_confirma"])
    except Exception:
        pass


def _semilla_lider(semilla_sim: int, unique_id: int) -> int:
    """Semilla de cerebro por líder Y por corrida: mezcla la semilla de la
    simulación con el id del líder. Así dos corridas del mismo titular no
    repiten frases (ni de la IA —caché aparte— ni del respaldo)."""
    return semilla_sim * 1_000_003 + unique_id

# orígenes permitidos: la web de producción + localhost de desarrollo.
# Configurable por entorno (ENJAMBRE_ORIGENES, separado por comas).
_origenes_env = os.environ.get("ENJAMBRE_ORIGENES", "").strip()
ORIGENES = [o.strip() for o in _origenes_env.split(",") if o.strip()] or [
    "http://localhost:5173",
    "http://localhost:4173",
]
# lista blanca del widget: los medios donde se puede embeber (sección 9).
# Un dominio fuera de lista no obtiene los datos (CORS) → el widget muestra
# la versión con CTA "Consigue el widget para tu medio".
_widget_env = os.environ.get("ENJAMBRE_WIDGET_DOMINIOS", "").strip()
DOMINIOS_WIDGET = [d.strip() for d in _widget_env.split(",") if d.strip()]
ORIGENES = ORIGENES + DOMINIOS_WIDGET

app = FastAPI(title="El Enjambre", version="0.7.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_origin_regex=r"https://.*\.vercel\.app",  # previews de Vercel
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# semáforo global: ninguna avalancha de conexiones dispara más de N
# simulaciones pesadas al mismo tiempo (protege CPU y memoria)
import asyncio as _asyncio  # noqa: E402

_semaforo_sim = _asyncio.Semaphore(MAX_SIM_CONCURRENTES)

MAX_OBSERVATORIOS = 2       # sesiones "en vivo" simultáneas (protege CPU)
MAX_TICKS_OBS = 6000        # tope de latidos por sesión (~8 min); luego se cierra
_semaforo_obs = _asyncio.Semaphore(MAX_OBSERVATORIOS)


_contador_peticiones = 0
_CADA_LIMPIEZA = 500  # cada tantas requests se purga el estado vencido

# Tope de cuerpo por petición. El más grande legítimo es el editor del panel
# (el texto completo de una edición del Pulso: unos pocos KB), así que 256 KB
# sobra. Sin este freno, un POST de cientos de MB se carga entero en memoria
# antes de que pydantic lo valide → el motor (512 MB en Render) se queda sin
# memoria y reinicia. Nota: cubre el caso con Content-Length (el normal); una
# subida "chunked" sin ese encabezado sigue acotada por los frenos de más abajo.
MAX_CUERPO = 256_000


@app.middleware("http")
async def blindaje(request: Request, call_next):
    """Rate-limit por IP en /api/*, tope de cuerpo y cabeceras de seguridad."""
    global _contador_peticiones
    ruta = request.url.path
    if request.method in ("POST", "PUT", "PATCH"):
        declarado = request.headers.get("content-length", "")
        if declarado.isdigit() and int(declarado) > MAX_CUERPO:
            return JSONResponse({"error": "cuerpo demasiado grande"}, status_code=413)
    if ruta.startswith("/api/"):
        ip = seguridad.ip_cliente(request.headers, request.client.host if request.client else None)
        if not seguridad.permitir_http(ip, ruta):
            return JSONResponse({"error": "Demasiadas solicitudes. Espera un momento."}, status_code=429)
    # limpieza periódica: evita que el estado en memoria (ventanas de rate-limit
    # e IPs de límites) crezca sin fin al acumular visitantes distintos.
    _contador_peticiones += 1
    if _contador_peticiones % _CADA_LIMPIEZA == 0:
        seguridad.limpiar()
        limites.limpiar()
    respuesta = await call_next(request)
    for clave, valor in seguridad.CABECERAS_SEGURIDAD.items():
        respuesta.headers.setdefault(clave, valor)
    return respuesta

NOMBRES_TIPO = {
    "Fundamentalista": "Fundamentalistas",
    "QuantMomentum": "Quants institucionales",
    "FondoPasivo": "Fondos pasivos",
    "MarketMaker": "Market makers",
    "EjecutorTWAP": "Ejecutores TWAP",
    "Arbitrajista": "Arbitrajistas",
    "NoiseTrader": "Noise traders",
    "Manada": "Manada",
    "FomoRetail": "FOMO retail",
    "Miedoso": "Miedosos",
    "Contrarian": "Contrarians",
    "BuyAndHold": "Buy & hold",
    "LiderOpinion": "Líderes de opinión",
}


def _token_admin_ok(recibido: str) -> bool:
    """Compara el token de admin en tiempo constante (evita timing attacks).

    Falla cerrado: si no hay ENJAMBRE_PIPELINE_TOKEN configurado, nadie pasa.
    """
    esperado = os.environ.get("ENJAMBRE_PIPELINE_TOKEN", "")
    if not esperado:
        return False
    return hmac.compare_digest(recibido or "", esperado)


@app.get("/salud")
def salud() -> dict:
    # `version` = el commit que Render tiene vivo (lo inyecta solo). Sirve para
    # confirmar de un vistazo QUÉ código está corriendo tras un despliegue.
    return {"estado": "ok", "proyecto": "El Enjambre", "etapa": 10,
            "redaccion": True,
            "version": (os.environ.get("RENDER_GIT_COMMIT") or "local")[:12]}


@app.get("/api/estado")
def api_estado(respuesta: Response) -> dict:
    """Estado operativo público (no revela secretos): si el enjambre está en
    pruebas privadas y si hay clave de IA. Sirve para monitoreo y para
    confirmar de un vistazo que el candado quedó activo."""
    respuesta.headers["Cache-Control"] = "no-store"
    return {
        "privado": seguridad.acceso_privado_activo(),
        "ia_configurada": bool(os.environ.get("ANTHROPIC_API_KEY")),
    }


def _responder(ws: WebSocket, **campos) -> str:
    return json.dumps(campos, ensure_ascii=False)


@app.websocket("/ws")
async def canal(ws: WebSocket) -> None:
    await ws.accept()
    ip = seguridad.ip_cliente(ws.headers, ws.client.host if ws.client else None)
    try:
        while True:
            texto = await ws.receive_text()
            # entrada malformada nunca tumba la conexión: se responde y sigue
            if len(texto) > MAX_MENSAJE_WS:
                await ws.send_text(_responder(ws, tipo="error", mensaje="mensaje demasiado grande"))
                continue
            try:
                mensaje = json.loads(texto)
            except (ValueError, TypeError):
                await ws.send_text(_responder(ws, tipo="error", mensaje="formato inválido"))
                continue
            if not isinstance(mensaje, dict):
                continue
            tipo = mensaje.get("tipo")

            # modo observatorio: el enjambre sigue vivo y recibe noticias encima
            if tipo == "observatorio":
                # el observatorio también lee titulares con IA: misma puerta
                permitido_obs, correo_obs = _puerta_simulacion(mensaje)
                if not permitido_obs:
                    mensaje_puerta = MENSAJE_PRIVADO if seguridad.acceso_privado_activo() else MENSAJE_CORREO
                    tipo_puerta = "privado" if seguridad.acceso_privado_activo() else "correo"
                    await ws.send_text(_responder(ws, tipo=tipo_puerta, mensaje=mensaje_puerta))
                    continue
                if correo_obs:
                    _asyncio.create_task(_asyncio.to_thread(_suscribir_silencioso, correo_obs))
                try:
                    await _asyncio.wait_for(_semaforo_obs.acquire(), timeout=0.01)
                except _asyncio.TimeoutError:
                    await ws.send_text(_responder(
                        ws, tipo="ocupado",
                        mensaje="El observatorio está lleno ahora mismo. Intenta en unos minutos."))
                    continue
                try:
                    await _correr_observatorio(ws, mensaje, ip)
                finally:
                    _semaforo_obs.release()
                continue

            if tipo != "simular":
                continue

            # la puerta: en privado abre la clave (equipo); en público, un correo
            # válido abre Y queda suscrito gratis (cada simulación deja un lead).
            permitido_puerta, correo = _puerta_simulacion(mensaje)
            if not permitido_puerta:
                mensaje_puerta = MENSAJE_PRIVADO if seguridad.acceso_privado_activo() else MENSAJE_CORREO
                tipo_puerta = "privado" if seguridad.acceso_privado_activo() else "correo"
                await ws.send_text(_responder(ws, tipo=tipo_puerta, mensaje=mensaje_puerta))
                continue

            # tope de simulaciones pesadas simultáneas (antes de gastar cupo)
            try:
                await _asyncio.wait_for(_semaforo_sim.acquire(), timeout=0.01)
            except _asyncio.TimeoutError:
                await ws.send_text(_responder(
                    ws, tipo="ocupado",
                    mensaje="El enjambre está ocupado con otra simulación. Intenta en unos segundos."))
                continue
            try:
                # toda simulación pública gasta ~100 llamadas LLM:
                # frenos por IP y global (tope diario)
                permitido, motivo = limites.permitir(ip)
                if not permitido:
                    await ws.send_text(_responder(ws, tipo="limite", mensaje=motivo))
                    continue
                # captura del lead EN PARALELO: no bloquea el momento mágico
                if correo:
                    _asyncio.create_task(_asyncio.to_thread(_suscribir_silencioso, correo))
                await _correr_simulacion(ws, mensaje)
            finally:
                _semaforo_sim.release()
    except WebSocketDisconnect:
        pass
    except Exception:
        # cualquier fallo inesperado cierra ESTA conexión, no el servidor
        try:
            await ws.close()
        except Exception:
            pass


# ---------- el modo observatorio (el enjambre sigue vivo) ----------

async def _leer_titular_en_vivo(modelo, lideres, titular, candado, semilla) -> list[dict]:
    """Los líderes leen una noticia y se inyecta al modelo EN VIVO (sin
    frenar el latido). El candado evita chocar con el step en curso."""
    from brains import reparto
    from brains.mercado import clasificar_async, perfil_de

    # 1000 líderes comparten ~110 cerebros (presupuesto de la biblia)
    consultas, asignacion = reparto.planificar(
        lideres, lambda uid: _semilla_lider(semilla, uid))
    respuestas_cerebros, tipo = await asyncio.gather(  # lento: sin candado
        analizar_titular_async(titular, consultas),
        clasificar_async(titular),
    )
    respuestas = reparto.expandir(respuestas_cerebros, asignacion)
    async with candado:
        await asyncio.to_thread(modelo.aplicar_titular, titular, respuestas, perfil_de(tipo))
    return respuestas


async def _correr_observatorio(ws: WebSocket, mensaje: dict, ip: str) -> None:
    """El enjambre late indefinidamente; el usuario suelta noticias encima.
    El costo LLM ocurre SOLO al leer un titular (bajo el tope diario); los
    latidos son casi gratis."""
    try:
        semilla = int(mensaje.get("seed", 42)) % 2_147_483_647
    except (TypeError, ValueError):
        semilla = 42
    ritmo = 0.08
    try:
        ritmo = max(0.04, float(mensaje.get("ritmo", 0.08)))
    except (TypeError, ValueError):
        pass

    modelo = await asyncio.to_thread(_crear_mercado, semilla)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]
    candado = _asyncio.Lock()
    detener = _asyncio.Event()

    await ws.send_text(_responder(ws, tipo="observatorio-inicio",
                                  precio=modelo.historial_precios[-1]))

    async def latir() -> None:
        latidos = 0
        while not detener.is_set() and latidos < MAX_TICKS_OBS:
            async with candado:
                await asyncio.to_thread(modelo.step)
            await ws.send_bytes(_paquete_tick(modelo))
            await asyncio.sleep(ritmo)
            latidos += 1
        detener.set()

    async def _inyectar(titular: str) -> None:
        # cada noticia gasta ~100 llamadas LLM → bajo el tope diario
        permitido, motivo = limites.permitir(ip)
        if not permitido:
            await ws.send_text(_responder(ws, tipo="limite", mensaje=motivo))
            return
        respuestas = await _leer_titular_en_vivo(modelo, lideres, titular, candado, semilla)
        await ws.send_text(json.dumps({
            "tipo": "inicio", "titular": titular,
            "lideres": [{"arquetipo": l.arquetipo, **{k: r[k] for k in ("senal", "confianza", "frase", "fuente")}}
                        for l, r in zip(lideres, respuestas)],
        }, ensure_ascii=False))

    async def escuchar() -> None:
        # noticia inicial (opcional): la que traía el mensaje de arranque
        inicial = str(mensaje.get("titular", "")).strip()[:MAX_TITULAR]
        if inicial:
            await _inyectar(inicial)
        while not detener.is_set():
            texto = await ws.receive_text()
            if len(texto) > MAX_MENSAJE_WS:
                continue
            try:
                dato = json.loads(texto)
            except (ValueError, TypeError):
                continue
            tipo = dato.get("tipo") if isinstance(dato, dict) else None
            if tipo == "detener":
                detener.set()
            elif tipo == "noticia":
                titular = str(dato.get("titular", "")).strip()[:MAX_TITULAR]
                if titular:
                    await _inyectar(titular)

    try:
        await _asyncio.gather(latir(), escuchar())
    except WebSocketDisconnect:
        detener.set()
    finally:
        detener.set()
        with _contextlib.suppress(Exception):
            await ws.send_text(_responder(ws, tipo="observatorio-fin"))


# ---------- la simulación transmitida ----------

async def _correr_simulacion(ws: WebSocket, mensaje: dict) -> None:
    titular = str(mensaje.get("titular", ""))[:MAX_TITULAR].strip() or "Sin novedades en los mercados"
    try:
        semilla = int(mensaje.get("seed", 42)) % 2_147_483_647
    except (TypeError, ValueError):
        semilla = 42
    try:
        ritmo = max(RITMO_MINIMO, float(mensaje.get("ritmo", RITMO_DEFECTO)))
    except (TypeError, ValueError):
        ritmo = RITMO_DEFECTO

    # crear y calentar el mercado sin bloquear el loop del servidor
    modelo = await asyncio.to_thread(_crear_mercado, semilla)
    lideres = [a for a in modelo.agentes_ordenados if isinstance(a, LiderOpinion)]

    # los 1000 líderes leen el titular (compartiendo ~110 cerebros de IA, según
    # el presupuesto de la biblia) Y se clasifica el tipo de mercado, en paralelo
    # (la clasificación es 1 llamada barata a Haiku, sin latencia extra)
    from brains import reparto
    from brains.mercado import clasificar_async, perfil_de

    consultas, asignacion = reparto.planificar(
        lideres, lambda uid: _semilla_lider(semilla, uid))
    respuestas_cerebros, tipo_mercado = await asyncio.gather(
        analizar_titular_async(titular, consultas),
        clasificar_async(titular),
    )
    respuestas = reparto.expandir(respuestas_cerebros, asignacion)
    perfil = perfil_de(tipo_mercado)

    await ws.send_text(json.dumps({
        "tipo": "inicio",
        "titular": titular,
        "precio": modelo.historial_precios[-1],
        "mercado": perfil["tipo"],
        "mercado_etiqueta": perfil["etiqueta"],
        "lideres": [
            {"arquetipo": lider.arquetipo, **{k: r[k] for k in ("senal", "confianza", "frase", "fuente")}}
            for lider, r in zip(lideres, respuestas)
        ],
    }, ensure_ascii=False))

    contador_acciones: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    async def transmitir_tick() -> None:
        await asyncio.to_thread(modelo.step)
        _contar_acciones(modelo, contador_acciones)
        await ws.send_bytes(_paquete_tick(modelo))
        if ritmo:
            await asyncio.sleep(ritmo)

    for _ in range(TICKS_PREVIOS):
        await transmitir_tick()

    precio_previo = modelo.historial_precios[-1]
    contador_acciones.clear()
    modelo.aplicar_titular(titular, respuestas=respuestas, perfil=perfil)

    for _ in range(TICKS_POSTERIORES):
        await transmitir_tick()

    reporte = _generar_reporte(modelo, precio_previo, respuestas, lideres, contador_acciones)
    reporte["mercado"] = perfil["tipo"]
    reporte["mercado_etiqueta"] = perfil["etiqueta"]

    # persistencia primero (CONTENIDO.md): TODA simulación se guarda
    sim_id = None
    try:
        sim_id = await asyncio.to_thread(
            _guardar_simulacion, titular, semilla, reporte, respuestas, lideres, modelo,
        )
        # si vino desde una tarjeta del muro, la tarjeta pasa a Estado A
        titular_id = mensaje.get("titular_id")
        if sim_id and seguridad.sim_id_valido(str(titular_id) if titular_id else None):
            await asyncio.to_thread(_vincular_titular, str(titular_id), sim_id)
    except Exception:
        pass  # la persistencia nunca tumba la simulación en curso

    await ws.send_text(json.dumps({
        "tipo": "fin",
        "sim_id": sim_id,
        "reporte": reporte,
    }, ensure_ascii=False))


def _vincular_titular(titular_id: str, sim_id: str) -> None:
    conexion = persistencia.conectar()
    try:
        persistencia.vincular_simulacion(conexion, titular_id, sim_id)
    finally:
        conexion.close()


def _guardar_simulacion(titular, semilla, reporte, respuestas, lideres, modelo) -> str:
    conexion = persistencia.conectar()
    try:
        return persistencia.guardar_simulacion(
            conexion,
            titular=titular,
            fuente="manual",
            seed=semilla,
            resumen=reporte,
            lideres=[
                {"arquetipo": lider.arquetipo,
                 **{k: r[k] for k in ("senal", "confianza", "frase")}}
                for lider, r in zip(lideres, respuestas)
            ],
            serie_precios=modelo.historial_precios[-(TICKS_PREVIOS + TICKS_POSTERIORES + 1):],
        )
    finally:
        conexion.close()


def _crear_mercado(semilla: int) -> MercadoEnjambre:
    modelo = MercadoEnjambre(seed=semilla, ticks_horizonte=TICKS_CALENTAMIENTO + TICKS_POSTERIORES)
    modelo.correr(TICKS_CALENTAMIENTO)
    return modelo


# ---------- el paquete binario por tick ----------

def _paquete_tick(modelo: MercadoEnjambre) -> bytes:
    cabecera = struct.pack("<fI", modelo.historial_precios[-1], modelo.tick)
    cuerpo = bytearray(len(modelo.agentes_ordenados))
    for i, agente in enumerate(modelo.agentes_ordenados):
        if isinstance(agente, LiderOpinion):
            s = agente.senal
        else:
            # sentimiento visible = rumor recibido + eco de su última acción
            hace = modelo.tick - agente.tick_ultima_accion
            impulso = 0.0
            if agente.ultima_accion and hace <= 5:
                signo = 0.5 if agente.ultima_accion == "compra" else -0.5
                impulso = signo * (1 - hace / 6)
            s = max(-1.0, min(1.0, agente.senal_social + impulso))
        cuerpo[i] = int(s * 127) & 0xFF
    return cabecera + bytes(cuerpo)


def _contar_acciones(modelo: MercadoEnjambre, contador: dict) -> None:
    for agente in modelo.agentes_ordenados:
        if agente.tick_ultima_accion == modelo.tick and agente.ultima_accion:
            lado = 0 if agente.ultima_accion == "compra" else 1
            contador[type(agente).__name__][lado] += 1


# ---------- el reporte final ----------

def _generar_reporte(modelo, precio_previo, respuestas, lideres, contador) -> dict:
    precios = modelo.historial_precios[-(TICKS_POSTERIORES + 1):]
    retornos = modelo.retornos[-TICKS_POSTERIORES:]
    media = sum(retornos) / len(retornos)
    volatilidad = (sum((r - media) ** 2 for r in retornos) / len(retornos)) ** 0.5

    extremos = sorted(zip(lideres, respuestas), key=lambda par: par[1]["senal"])
    frases = [
        {"arquetipo": lider.arquetipo, "frase": r["frase"], "senal": r["senal"]}
        for lider, r in (extremos[0], extremos[len(extremos) // 2], extremos[-1])
    ]

    return {
        "direccion_pct": round((precios[-1] / precio_previo - 1) * 100, 2),
        "minimo_pct": round((min(precios) / precio_previo - 1) * 100, 2),
        "maximo_pct": round((max(precios) / precio_previo - 1) * 100, 2),
        "volatilidad_pct": round(volatilidad * 100, 2),
        "senal_media_lideres": round(sum(r["senal"] for r in respuestas) / len(respuestas), 2),
        "desglose": {
            NOMBRES_TIPO.get(clase, clase): {"compras": c, "ventas": v}
            for clase, (c, v) in sorted(contador.items(), key=lambda kv: -sum(kv[1]))
        },
        "frases": frases,
        "descargo": DISCLAIMER,
    }


# ---------- los endpoints del muro (CONTENIDO.md sección 3.2) ----------

def _nivel_agitacion(volatilidad_pct: float) -> str:
    """Traducción editorial de la volatilidad."""
    if volatilidad_pct < 1.0:
        return "bajo"
    if volatilidad_pct < 2.0:
        return "medio"
    return "alto"


def _direccion_editorial(direccion_pct: float) -> str:
    if direccion_pct > 1.0:
        return "▲"
    if direccion_pct < -1.0:
        return "▼"
    return "◆"


def _resumen_tarjeta(resumen: dict) -> dict:
    """Lo que la tarjeta del muro necesita del reporte completo."""
    frases = resumen.get("frases", [])
    jugosa = max(frases, key=lambda f: abs(f.get("senal", 0)), default=None)
    if jugosa is not None:
        arquetipo = POR_ID.get(jugosa["arquetipo"], {})
        jugosa = {"arquetipo": arquetipo.get("nombre", jugosa["arquetipo"]), "frase": jugosa["frase"]}
    return {
        "direccion_pct": resumen.get("direccion_pct"),
        "direccion": _direccion_editorial(resumen.get("direccion_pct", 0)),
        "agitacion": _nivel_agitacion(resumen.get("volatilidad_pct", 0)),
        "frase": jugosa,
    }


@app.get("/api/muro")
def muro(respuesta: Response) -> dict:
    """Las tarjetas del día: destacadas primero, luego cronológico."""
    respuesta.headers["Cache-Control"] = "public, max-age=60"
    conexion = persistencia.conectar()
    try:
        filas = persistencia.titulares_del_muro(conexion, portero.UMBRAL_IMPACTO, limite=30)
    finally:
        conexion.close()
    tarjetas = []
    for fila in filas:
        tarjeta = {
            "id": fila["id"],
            "titular": fila["titular"],
            "fuente": fila["fuente"],
            "simbolos": fila["simbolos"],
            "fecha": fila["fecha"],
            "estado": "simulada" if fila["sim_id"] else "pendiente",
            "sim_id": fila["sim_id"],
            "destacada": bool(fila["sim_destacada"]),
        }
        if fila["resumen_json"]:
            tarjeta["resumen"] = _resumen_tarjeta(json.loads(fila["resumen_json"]))
        tarjetas.append(tarjeta)
    return {"tarjetas": tarjetas, "descargo": DISCLAIMER}


def _payload_simulacion(sim_id: str) -> dict | None:
    """Los datos de una simulación para la UI (o None si no existe)."""
    conexion = persistencia.conectar()
    try:
        datos = persistencia.obtener_simulacion(conexion, sim_id)
        simbolos = ""
        if datos is not None:
            # el ticker viene del titular del muro (si esta sim nació de uno):
            # la UI lo usa para la comparación educativa con el gráfico real
            fila = conexion.execute(
                "SELECT simbolos FROM titulares WHERE sim_id = ?", (sim_id,)
            ).fetchone()
            simbolos = (fila["simbolos"] or "") if fila else ""
    finally:
        conexion.close()
    if datos is None:
        return None
    return {
        "id": datos["id"],
        "titular": datos["titular"],
        "fuente": datos["fuente"],
        "fecha": datos["fecha"],
        "destacada": bool(datos["destacada"]),
        "resumen": datos["resumen"],
        "tarjeta": _resumen_tarjeta(datos["resumen"]),
        "lideres": datos["lideres"],
        "voces": _voces_por_arquetipo(datos["lideres"]),
        "serie_precios": datos["serie_precios"],
        "epilogo": datos.get("epilogo"),
        "simbolos": simbolos,
        "reaccion_real": datos.get("reaccion_real"),
        "tiene_replay": persistencia.leer_frames(sim_id) is not None,
    }


@app.get("/api/simulacion/{sim_id}")
def simulacion(sim_id: str, respuesta: Response) -> dict:
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)  # type: ignore[return-value]
    datos = _payload_simulacion(sim_id)
    if datos is None:
        return Response(status_code=404)  # type: ignore[return-value]
    respuesta.headers["Cache-Control"] = "public, max-age=300"
    return datos


@app.get("/api/duelo/{id_a}/{id_b}")
def duelo(id_a: str, id_b: str, respuesta: Response) -> dict:
    """Los dos resúmenes de un duelo de escenarios (CONTENIDO.md sección 8)."""
    if not (seguridad.sim_id_valido(id_a) and seguridad.sim_id_valido(id_b)):
        return Response(status_code=404)  # type: ignore[return-value]
    a, b = _payload_simulacion(id_a), _payload_simulacion(id_b)
    if a is None or b is None:
        return Response(status_code=404)  # type: ignore[return-value]
    respuesta.headers["Cache-Control"] = "public, max-age=300"
    return {"a": a, "b": b, "descargo": DISCLAIMER}


def _voces_por_arquetipo(lideres: list[dict]) -> list[dict]:
    """Las 8 voces del reporte: por arquetipo, señal media + la mejor frase."""
    grupos: dict[str, list[dict]] = defaultdict(list)
    for lider in lideres:
        grupos[lider["arquetipo"]].append(lider)
    voces = []
    for arquetipo, miembros in grupos.items():
        senal_media = sum(m["senal"] for m in miembros) / len(miembros)
        mejor = max(miembros, key=lambda m: abs(m["senal"]))
        voces.append({
            "arquetipo": arquetipo,
            "nombre": POR_ID.get(arquetipo, {}).get("nombre", arquetipo),
            "senal_media": round(senal_media, 2),
            "frase": mejor["frase"],
        })
    return sorted(voces, key=lambda v: v["senal_media"])


@app.get("/api/simulacion/{sim_id}/imagen")
def imagen(sim_id: str) -> Response:
    """El 'momento dramático' como PNG 1200×630 (correo + Open Graph)."""
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)
    conexion = persistencia.conectar()
    try:
        datos = persistencia.obtener_simulacion(conexion, sim_id)
    finally:
        conexion.close()
    if datos is None:
        return Response(status_code=404)
    from contenido import captura

    resumen = {**datos["resumen"], "agitacion": _nivel_agitacion(datos["resumen"].get("volatilidad_pct", 0))}
    png = captura.generar_png(datos["titular"], resumen, datos["serie_precios"])
    return Response(
        content=png,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400, immutable"},
    )


@app.get("/api/simulacion/{sim_id}/replay")
def replay(sim_id: str) -> Response:
    """Los frames binarios del replay 3D (solo destacadas los conservan).

    El sim_id se valida como hash hex de 16 (nada de path traversal); el
    replay es inmutable, así que se puede cachear con fuerza.
    """
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)
    frames = persistencia.leer_frames(sim_id)
    if frames is None:
        return Response(status_code=404)
    return Response(
        content=frames,
        media_type="application/octet-stream",
        headers={"Cache-Control": "public, max-age=86400, immutable"},
    )


class PeticionSimular(BaseModel):
    id: str  # el id del titular en el muro
    acceso: str = ""  # clave de pruebas privadas (si el modo está activo)


@app.post("/api/simular-titular")
def simular_titular(peticion: PeticionSimular) -> dict:
    """Chequeo previo de la simulación on-demand desde una tarjeta.

    No consume el cupo (eso pasa al correr de verdad por el WebSocket);
    responde si hay presupuesto y devuelve el titular a simular.
    """
    if not seguridad.acceso_ok(peticion.acceso):
        return {"estado": "privado", "mensaje": MENSAJE_PRIVADO}
    if not seguridad.sim_id_valido(peticion.id):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        titular = persistencia.obtener_titular(conexion, peticion.id)
    finally:
        conexion.close()
    if titular is None:
        return Response(status_code=404)  # type: ignore[return-value]
    if titular["sim_id"]:
        return {"estado": "simulada", "sim_id": titular["sim_id"]}
    permitido, motivo = limites.permitir("verificacion-previa", consumir=False)
    if not permitido and motivo == limites.MENSAJE_GLOBAL:
        return {"estado": "limite", "mensaje": motivo}
    return {"estado": "adelante", "titular": titular["titular"], "titular_id": titular["id"]}


# ---------- El Pulso: suscripción con double opt-in (CONTENIDO.md sección 6) ----------

import re as _re  # noqa: E402
import time as _time  # noqa: E402

from fastapi.responses import HTMLResponse  # noqa: E402

_EMAIL = _re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class PeticionSuscribir(BaseModel):
    email: str
    origen: str = "web"


def _pagina(titulo: str, mensaje: str) -> HTMLResponse:
    """Una página mínima con la estética Rubicón para confirmar/baja."""
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{titulo}</title>
<style>body{{margin:0;height:100vh;display:flex;flex-direction:column;align-items:center;
justify-content:center;background:#0b0e14;color:#f4efe6;font-family:system-ui,sans-serif;text-align:center;padding:24px;}}
h1{{color:#c9a227;font-family:Georgia,serif;font-weight:600;}} a{{color:#c9a227;}}
p{{max-width:420px;line-height:1.5;color:#a8a291;}}</style></head>
<body><h1>{titulo}</h1><p>{mensaje}</p><a href="{boletin_base_web()}">Ir a El Enjambre →</a></body></html>"""
    # estas páginas sí llevan estilo inline: CSP propia que lo permite
    return HTMLResponse(content=html, headers={
        "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'",
    })


def boletin_base_web() -> str:
    return os.environ.get("ENJAMBRE_WEB_URL", "https://enjambre-ai-agents.vercel.app")


@app.post("/api/suscribir")
def suscribir(peticion: PeticionSuscribir) -> dict:
    """Alta pendiente + correo de confirmación (double opt-in)."""
    email = peticion.email.strip().lower()
    if not _EMAIL.match(email) or len(email) > 200:
        return JSONResponse({"error": "correo inválido"}, status_code=400)
    origen = peticion.origen if peticion.origen in ("web", "widget", "manual") else "web"

    conexion = persistencia.conectar()
    try:
        alta = persistencia.agregar_suscriptor(conexion, email, origen=origen)
    finally:
        conexion.close()

    if alta["ya_activo"]:
        return {"estado": "ya_suscrito", "mensaje": "Ya estabas suscrito al Pulso. ¡Gracias!"}

    # solo se envía si no hubo una confirmación reciente (antibombardeo, auditoría C).
    # La respuesta es idéntica en ambos casos: no revela si el correo ya existía.
    if alta.get("reenviar", True):
        from contenido import boletin

        boletin.enviar_confirmacion(email, alta["token_confirma"])  # sin Resend, no envía (dev)
    return {"estado": "pendiente",
            "mensaje": "Te enviamos un correo para confirmar tu suscripción. Revisa tu bandeja."}


class PeticionContacto(BaseModel):
    nombre: str
    email: str
    organizacion: str = ""
    mensaje: str = ""


@app.post("/api/contacto")
def api_contacto(peticion: PeticionContacto) -> dict:
    """El canal B2B: educadores, medios y fintechs que quieren conversar.

    Guarda el lead y avisa a Giorgio por Telegram (si está configurado).
    Sin promesas de inversión: es una solicitud de contacto, nada más."""
    nombre = peticion.nombre.strip()
    email = peticion.email.strip().lower()
    if not nombre or len(nombre) > 120:
        return JSONResponse({"error": "cuéntanos tu nombre"}, status_code=400)
    if not _EMAIL.match(email) or len(email) > 200:
        return JSONResponse({"error": "correo inválido"}, status_code=400)
    conexion = persistencia.conectar()
    try:
        persistencia.agregar_contacto(
            conexion, nombre=nombre, email=email,
            organizacion=peticion.organizacion, mensaje=peticion.mensaje,
        )
    finally:
        conexion.close()
    try:
        from contenido import notificar
        # todo lo que escribió el visitante se escapa: el aviso va con
        # parse_mode=HTML y un "<" suelto haría que Telegram lo rechace
        # (Giorgio perdería el lead sin enterarse).
        notificar.avisar(
            f"🤝 <b>Nuevo contacto B2B</b>\n{notificar.escapar(nombre)}"
            + (f" · {notificar.escapar(peticion.organizacion.strip()[:80])}"
               if peticion.organizacion.strip() else "")
            + f"\n{notificar.escapar(email)}\n{notificar.escapar(peticion.mensaje.strip()[:200])}"
        )
    except Exception:
        pass  # el lead ya quedó guardado; el aviso es cortesía
    return {"estado": "recibido",
            "mensaje": "¡Gracias! Te escribiremos pronto para coordinar."}


@app.get("/api/contactos")
def api_contactos(x_pipeline_token: str = Header(default="")) -> dict:
    """Los leads B2B, para Giorgio (protegido)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        return {"contactos": persistencia.listar_contactos(conexion)}
    finally:
        conexion.close()


@app.get("/api/confirmar/{token}")
def confirmar(token: str) -> HTMLResponse:
    conexion = persistencia.conectar()
    try:
        email = persistencia.confirmar_suscriptor(conexion, token)
    finally:
        conexion.close()
    if email is None:
        return _pagina("Enlace no válido", "Este enlace de confirmación ya se usó o expiró.")
    return _pagina("¡Suscripción confirmada! 🐝",
                   "Desde mañana recibirás El Pulso cada mañana. Bienvenido al enjambre.")


@app.get("/api/baja/{token}")
def baja(token: str) -> HTMLResponse:
    conexion = persistencia.conectar()
    try:
        exito = persistencia.dar_de_baja(conexion, token)
    finally:
        conexion.close()
    if not exito:
        return _pagina("Enlace no válido", "No encontramos esa suscripción.")
    return _pagina("Te desuscribiste", "Ya no recibirás El Pulso. Puedes volver cuando quieras.")


# ---------- El Pulso: revisión y aprobación desde el correo (humano en el lazo) ----------
# El token de la edición (en el correo de revisión) es la llave: quien lo tiene,
# decide. Aprobar/Descartar son POST (un clic desde la página de revisión), así
# ningún prefetch del cliente de correo dispara un envío por accidente.

def _pagina_pulso(titulo: str, cuerpo: str, status: int = 200) -> HTMLResponse:
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{titulo}</title>
<style>
 body{{margin:0;background:#141019;color:#f3eee8;font-family:system-ui,-apple-system,sans-serif;}}
 .barra{{position:sticky;top:0;z-index:2;background:#1b1522;border-bottom:1px solid #2e2636;padding:16px 18px;text-align:center;}}
 .barra h1{{margin:0 0 4px;font-family:Georgia,serif;font-weight:600;font-size:1.15rem;color:#e3c565;}}
 .barra p{{margin:0;color:#a8a291;font-size:.85rem;}}
 .acc{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:14px;}}
 .btn{{border:0;cursor:pointer;font:700 13px/1 system-ui;letter-spacing:.04em;text-transform:uppercase;padding:14px 24px;border-radius:8px;}}
 .ok{{background:#2f8f66;color:#fff;}} .no{{background:transparent;color:#c0847d;border:1px solid #7a4b47;}}
 .marco{{width:100%;border:0;background:#faf8f4;display:block;min-height:74vh;}}
 .aviso{{max-width:520px;margin:64px auto;padding:0 24px;text-align:center;line-height:1.6;}}
 .aviso h1{{font-family:Georgia,serif;}}
</style></head><body>{cuerpo}</body></html>"""
    return HTMLResponse(content=html, status_code=status, headers={
        "Content-Security-Policy": "default-src 'none'; frame-src 'self'; img-src 'self' data:; style-src 'unsafe-inline'; form-action 'self'",
        "Referrer-Policy": "no-referrer", "X-Content-Type-Options": "nosniff"})


@app.get("/pulso/preview/{token}")
def pulso_preview(token: str) -> Response:
    """El HTML crudo de la edición (lo carga el iframe de la página de revisión)."""
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
    finally:
        conexion.close()
    if not ed or not ed.get("html_preview"):
        return Response(status_code=404)
    return HTMLResponse(content=ed["html_preview"], headers={
        "Content-Security-Policy": "default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'",
        "X-Frame-Options": "SAMEORIGIN"})


@app.get("/pulso/revisar/{token}")
def pulso_revisar(token: str) -> HTMLResponse:
    """La sala de revisión: el preview real + botones Aprobar / Descartar."""
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
        n_susc = len(persistencia.suscriptores_activos(conexion)) if ed else 0
    finally:
        conexion.close()
    if not ed:
        return _pagina_pulso("Enlace no válido",
            '<div class="aviso"><h1>Enlace no válido</h1><p>No encontramos esa edición.</p></div>', status=404)
    estado = ed["estado"]
    if estado == "enviada":
        cabecera = f'<h1>Ya enviada ✓</h1><p>Salió a {ed["enviados"]} de {ed["suscriptores"]} suscriptores.</p>'
        acciones = ""
    elif estado == "descartada":
        cabecera = '<h1>Descartada</h1><p>Esta edición no se enviará.</p>'
        acciones = ""
    else:
        cabecera = (f'<h1>El Pulso — pendiente de tu revisión</h1>'
                    f'<p>Se enviaría a {n_susc} suscriptor(es). Revisa abajo y decide.</p>')
        acciones = (f'<div class="acc">'
                    f'<form method="post" action="/pulso/aprobar/{token}" style="margin:0;"><button class="btn ok" type="submit">✅ Aprobar y enviar</button></form>'
                    f'<form method="post" action="/pulso/descartar/{token}" style="margin:0;"><button class="btn no" type="submit">🗑 Descartar</button></form></div>')
    cuerpo = (f'<div class="barra">{cabecera}{acciones}</div>'
              f'<iframe class="marco" src="/pulso/preview/{token}" title="Vista previa de la edición"></iframe>')
    return _pagina_pulso("Revisar El Pulso", cuerpo)


@app.post("/pulso/aprobar/{token}")
def pulso_aprobar(token: str) -> HTMLResponse:
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
        if not ed:
            return _pagina_pulso("Enlace no válido", '<div class="aviso"><h1>Enlace no válido</h1></div>', status=404)
        from contenido import pipeline
        res = pipeline.aprobar_y_enviar(conexion, ed["fecha"])
    finally:
        conexion.close()
    if res.get("ok") and res.get("ya_enviada"):
        msg = f'Esta edición ya se había enviado ({res.get("enviados", 0)} correos).'
    elif res.get("ok"):
        msg = f'Enviada a {res.get("enviados", 0)} de {res.get("suscriptores", 0)} suscriptores. 🎉'
    else:
        msg = res.get("motivo", "No se pudo enviar.")
    return _pagina_pulso("Aprobada",
        f'<div class="aviso"><h1 style="color:#2f8f66;">✅ Listo</h1><p>{msg}</p></div>')


@app.post("/pulso/descartar/{token}")
def pulso_descartar(token: str) -> HTMLResponse:
    conexion = persistencia.conectar()
    try:
        ed = persistencia.edicion_por_token(conexion, token)
        if not ed:
            return _pagina_pulso("Enlace no válido", '<div class="aviso"><h1>Enlace no válido</h1></div>', status=404)
        from contenido import pipeline
        pipeline.descartar_edicion(conexion, ed["fecha"])
    finally:
        conexion.close()
    return _pagina_pulso("Descartada",
        '<div class="aviso"><h1 style="color:#c0847d;">🗑 Descartada</h1>'
        '<p>Esta edición no se enviará. Mañana habrá una nueva.</p></div>')


# ---------- Webhook de Resend: aperturas y clics (firmado por Svix) ----------
# Resend firma cada evento con Svix (HMAC-SHA256). Sin el secreto configurado,
# el endpoint RECHAZA todo (falla cerrado): jamás ingerimos eventos sin firmar.

def _verificar_svix(cuerpo: bytes, cabeceras) -> bool:
    """Valida la firma Svix de un webhook de Resend. Constante en el tiempo."""
    secreto = os.environ.get("RESEND_WEBHOOK_SECRET", "").strip()
    if not secreto:
        return False
    svix_id = cabeceras.get("svix-id", "")
    svix_ts = cabeceras.get("svix-timestamp", "")
    firmas = cabeceras.get("svix-signature", "")
    if not (svix_id and svix_ts and firmas):
        return False
    # antirreplay: rechaza timestamps muy viejos o del futuro (tolerancia amplia
    # para el reloj de Render). El timestamp es parte de lo firmado igualmente.
    try:
        desfase = abs(int(_time.time()) - int(svix_ts))
        if desfase > 3600:
            return False
    except (ValueError, TypeError):
        return False
    clave = secreto.split("_", 1)[1] if secreto.startswith("whsec_") else secreto
    try:
        clave_bytes = base64.b64decode(clave)
    except Exception:
        return False
    firmado = f"{svix_id}.{svix_ts}.".encode() + cuerpo
    esperada = base64.b64encode(hmac.new(clave_bytes, firmado, hashlib.sha256).digest()).decode()
    # el header trae "v1,<firma> v1,<firma2>…"; comparación constante contra cada una
    for parte in firmas.split():
        _, _, valor = parte.partition(",")
        if valor and hmac.compare_digest(valor, esperada):
            return True
    return False


def _tag_edicion_evento(data: dict) -> str | None:
    """Saca la fecha de edición del tag del evento (Resend la devuelve como
    objeto {edicion: fecha} o como lista [{name,value}])."""
    tags = data.get("tags")
    if isinstance(tags, dict):
        return tags.get("edicion")
    if isinstance(tags, list):
        for t in tags:
            if isinstance(t, dict) and t.get("name") == "edicion":
                return t.get("value")
    return None


@app.post("/pulso/webhook/resend")
async def webhook_resend(request: Request) -> Response:
    """Recibe eventos de Resend (apertura, clic…) y los registra por edición.
    Firma Svix obligatoria: sin ella, 401."""
    cuerpo = await request.body()
    if len(cuerpo) > 64_000:  # un evento legítimo es pequeño; corta abusos
        return JSONResponse({"error": "cuerpo demasiado grande"}, status_code=413)
    if not _verificar_svix(cuerpo, request.headers):
        return JSONResponse({"error": "firma no válida"}, status_code=401)
    try:
        evento = json.loads(cuerpo)
    except (ValueError, TypeError):
        return JSONResponse({"error": "json no válido"}, status_code=400)
    tipo = (evento.get("type") or "").removeprefix("email.")
    data = evento.get("data") or {}
    destinatarios = data.get("to") or []
    email = destinatarios[0] if isinstance(destinatarios, list) and destinatarios else ""
    fecha_ed = _tag_edicion_evento(data)
    ts = evento.get("created_at")
    if email and tipo:
        conexion = persistencia.conectar()
        try:
            persistencia.registrar_evento_correo(conexion, fecha_ed, email, tipo, ts)
        finally:
            conexion.close()
    return JSONResponse({"ok": True})  # 200 siempre que la firma sea válida


# ---------- Centro de Mando de El Pulso (dashboard, protegido por token) ----------

class PeticionEditar(BaseModel):
    redactado: dict = {}


def _fecha_valida(fecha: str) -> bool:
    return bool(_re.match(r"^\d{4}-\d{2}-\d{2}$", fecha))


@app.get("/panel")
def panel_html() -> Response:
    """Sirve el Centro de Mando desde la propia API (mismo origen → sin CORS).
    El acceso lo controla la clave que se pide dentro de la página."""
    from pathlib import Path
    ruta = Path(__file__).parent / "panel.html"
    if not ruta.exists():
        return Response(status_code=404)
    return HTMLResponse(content=ruta.read_text(encoding="utf-8"), headers={
        "Content-Security-Policy": ("default-src 'none'; script-src 'unsafe-inline'; "
                                    "style-src 'unsafe-inline'; connect-src 'self'; "
                                    "frame-src 'self'; img-src 'self' data:; font-src 'self'"),
        "X-Content-Type-Options": "nosniff"})


@app.get("/api/panel/estado")
def panel_estado(x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    conexion = persistencia.conectar()
    try:
        hoy = persistencia.ahora_iso()[:10]
        ed = persistencia.obtener_edicion(conexion, hoy)
        n_susc = len(persistencia.suscriptores_activos(conexion))
    finally:
        conexion.close()
    return {
        "hoy": hoy,
        "suscriptores": n_susc,
        "ia_configurada": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "resend_configurado": bool(os.environ.get("RESEND_API_KEY")),
        "admin_email_configurado": bool(os.environ.get("PULSO_ADMIN_EMAIL")),
        "edicion_hoy": None if ed is None else {
            "estado": ed["estado"], "asunto": ed["asunto"],
            "enviados": ed["enviados"], "suscriptores": ed["suscriptores"]},
        "version": (os.environ.get("RENDER_GIT_COMMIT") or "local")[:12],
    }


@app.get("/api/panel/ediciones")
def panel_ediciones(x_pipeline_token: str = Header(default=""), limite: int = 30) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    conexion = persistencia.conectar()
    try:
        eds = persistencia.listar_ediciones(conexion, min(max(1, limite), 90))
    finally:
        conexion.close()
    return {"ediciones": eds}


@app.get("/api/panel/estadisticas")
def panel_estadisticas(x_pipeline_token: str = Header(default=""), dias: int = 30) -> dict:
    """Estadísticas del centro de mando: crecimiento de suscriptores, ediciones
    y aperturas/clics (estas últimas si el webhook de Resend está configurado)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        datos = persistencia.estadisticas(conexion, dias=dias)
    finally:
        conexion.close()
    datos["webhook_configurado"] = bool(os.environ.get("RESEND_WEBHOOK_SECRET"))
    return datos


@app.get("/api/panel/edicion/{fecha}")
def panel_edicion(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _fecha_valida(fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        ed = persistencia.obtener_edicion(conexion, fecha)
    finally:
        conexion.close()
    if ed is None:
        return Response(status_code=404)  # type: ignore[return-value]
    brief = ed["brief"] or {}
    return {
        "fecha": ed["fecha"], "estado": ed["estado"], "asunto": ed["asunto"],
        "token": ed["token"], "enviados": ed["enviados"], "suscriptores": ed["suscriptores"],
        "generada_iso": ed["generada_iso"], "enviada_iso": ed["enviada_iso"],
        "redactado": brief.get("redactado") or {}, "foto": brief.get("foto") or [],
    }


@app.post("/api/panel/edicion/{fecha}/aprobar")
def panel_aprobar(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _fecha_valida(fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    from contenido import pipeline
    return pipeline.aprobar_y_enviar(fecha=fecha)


@app.post("/api/panel/edicion/{fecha}/descartar")
def panel_descartar(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _fecha_valida(fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    from contenido import pipeline
    return pipeline.descartar_edicion(fecha=fecha)


@app.post("/api/panel/edicion/{fecha}/editar")
def panel_editar(fecha: str, peticion: PeticionEditar, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _fecha_valida(fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        ed = persistencia.obtener_edicion(conexion, fecha)
        if ed is None:
            return {"ok": False, "motivo": "no existe la edición"}
        if ed["estado"] == "enviada":
            return {"ok": False, "motivo": "la edición ya se envió; no se puede editar"}
        persistencia.actualizar_redactado(conexion, fecha, peticion.redactado)
        # re-renderiza el preview con el texto editado (usa las destacadas de hoy)
        try:
            from datetime import datetime as _dt, timezone as _tz
            from contenido import pipeline, boletin
            brief = persistencia.obtener_edicion(conexion, fecha)["brief"]
            destacadas = pipeline._destacadas_de_hoy(conexion)
            if destacadas:
                html = boletin.construir_html(
                    destacadas, pipeline._fecha_es(_dt.now(_tz.utc)),
                    token_baja=persistencia.TOKEN_BAJA_SENTINEL, brief=brief)
                persistencia.actualizar_preview(conexion, fecha, html)
        except Exception:
            pass
        return {"ok": True}
    finally:
        conexion.close()


@app.post("/api/panel/generar")
def panel_generar(tareas: BackgroundTasks, x_pipeline_token: str = Header(default="")) -> dict:
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    tareas.add_task(_correr_ritual)
    return {"ok": True, "mensaje": "Generando la edición de hoy… (~1-2 min). Recarga en un momento."}


# ---------- disparador del ritual de la madrugada (protegido por token) ----------

def _correr_ritual() -> None:
    """Corre el ritual completo en el MISMO proceso web → misma base que
    sirve el muro. Cualquier fallo se traga (no debe tumbar el servidor)."""
    try:
        from contenido import pipeline
        pipeline.ritual_matutino(enviar=True)
    except Exception:
        pass


@app.get("/api/diagnostico")
def api_diagnostico(x_pipeline_token: str = Header(default="")) -> dict:
    """Diagnóstico de la clave de Anthropic en UN comando (protegido).

    Hace una llamada mínima a la API y devuelve el veredicto con la causa
    exacta si falla (clave inválida, sin saldo, timeout…). Evita pescar
    errores en los logs cuando los líderes caen al respaldo."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    clave = os.environ.get("ANTHROPIC_API_KEY", "")
    resultado = {
        "clave_presente": bool(clave),
        "formato_sk_ant": clave.startswith("sk-ant-"),
        "largo_clave": len(clave),
    }
    if not clave:
        resultado["veredicto"] = "FALTA la variable ANTHROPIC_API_KEY"
        return resultado
    if clave != clave.strip():
        resultado["veredicto"] = "la clave tiene espacios al inicio o final: bórralos y guarda"
        return resultado
    try:
        import anthropic

        cliente = anthropic.Anthropic(timeout=20)
        r = cliente.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=10,
            messages=[{"role": "user", "content": "Di solo: hola"}],
        )
        resultado["veredicto"] = "OK: la IA respondió — los cerebros reales funcionan"
        resultado["respuesta"] = r.content[0].text[:40]
    except Exception as error:
        resultado["veredicto"] = f"FALLA {type(error).__name__}: {str(error)[:300]}"
    return resultado


@app.post("/api/pipeline")
def disparar_pipeline(tareas: BackgroundTasks, x_pipeline_token: str = Header(default="")) -> dict:
    """Lo llama el cron de Render (o Giorgio a mano) para preparar el día.

    Protegido por token (ENJAMBRE_PIPELINE_TOKEN). Corre en segundo plano
    y responde al instante: el ritual toma minutos.
    """
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    tareas.add_task(_correr_ritual)
    return {"estado": "iniciado"}


@app.post("/api/corrector")
def api_corrector(x_pipeline_token: str = Header(default="")) -> dict:
    """Corre el corrector automático a demanda (protegido).

    Normalmente corre solo dentro del ritual diario; este endpoint sirve
    para corregir sin esperar la madrugada."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import corrector

    return corrector.corregir_pendientes()


@app.get("/api/libreta")
def api_libreta(x_pipeline_token: str = Header(default="")) -> dict:
    """La libreta de calificaciones (enjambre vs mercado real). Protegida:
    es la brújula interna de la calibración, no material publicable."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import corrector

    return corrector.libreta()


def _correr_backtest(tanda: int, mercado: str | None = None) -> None:
    from contenido import backtest

    resultado = backtest.correr_tanda(tamano=tanda, mercado=mercado)
    print(f"backtest: {len(resultado['hechas'])} exámenes rendidos, "
          f"{resultado['pendientes']} pendientes, sin datos: {resultado['sin_datos']}, "
          f"sin IA (¿saldo?): {resultado.get('sin_ia')}, "
          f"respaldo: {resultado.get('respaldo')}",
          flush=True)


@app.post("/api/backtest")
def api_backtest(tareas: BackgroundTasks, tanda: int = 5, mercado: str = "",
                 x_pipeline_token: str = Header(default="")) -> dict:
    """Rinde una tanda de exámenes históricos (protegido, freno de
    presupuesto). Corre en segundo plano — cada simulación toma ~1 minuto.
    Con `mercado` (oro/cripto/petroleo/indice/accion) rinde solo ese mercado
    (calibración balanceada, 100+/mercado)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import backtest

    merc = mercado.strip() or None
    avance = backtest.estado(mercado=merc)
    tareas.add_task(_correr_backtest, tanda, merc)
    return {"estado": "iniciado", "mercado": merc or "todos",
            "tanda": max(1, min(int(tanda), backtest.TANDA_MAXIMA)),
            "hechos": avance["hechos"], "pendientes": avance["pendientes"]}


@app.get("/api/backtest")
def api_backtest_estado(mercado: str = "", x_pipeline_token: str = Header(default="")) -> dict:
    """El avance del backtest: cuántos exámenes rendidos y cuántos faltan.
    Con `mercado` filtra a ese mercado."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import backtest

    avance = backtest.estado(mercado=mercado.strip() or None)
    return {k: v for k, v in avance.items() if not k.startswith("_")}


@app.post("/api/backtest/reiniciar")
def api_backtest_reiniciar(x_pipeline_token: str = Header(default="")) -> dict:
    """Borra los exámenes de calibración de la base LOCAL (fuente='backtest'),
    para re-validar tras cambiar los diales. El disco persistente del plan
    Starter guarda los casos entre deploys, así que sin esto el motor cree que
    ya están todos rendidos y no re-rinde. NO toca las destacadas en vivo.
    También conviene reiniciar la caja fuerte de GitHub aparte."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    from contenido import persistencia

    conexion = persistencia.conectar()
    try:
        antes = conexion.execute(
            "SELECT COUNT(*) FROM simulaciones WHERE fuente = 'backtest'").fetchone()[0]
        conexion.execute("DELETE FROM simulaciones WHERE fuente = 'backtest'")
        conexion.commit()
    finally:
        conexion.close()
    return {"reiniciado": True, "examenes_borrados": antes}


def _correr_cosecha(mercados, desde, hasta, tope, reemplazar) -> None:
    from contenido import cosechador

    resultado = cosechador.cosechar_y_guardar(mercados=mercados, desde=desde,
                                              hasta=hasta, tope_por_simbolo=tope,
                                              reemplazar=reemplazar)
    print(f"cosecha: {resultado['resumen']} · respaldo: {resultado.get('respaldo')}",
          flush=True)


@app.post("/api/cosechar")
def api_cosechar(tareas: BackgroundTasks, mercados: str = "", desde: str = "2016-01-01",
                 hasta: str = "", tope: int = 8, reemplazar: bool = False,
                 x_pipeline_token: str = Header(default="")) -> dict:
    """El cosechador: busca días de gran movimiento reales (Yahoo) y les pega
    su titular real (Benzinga/Alpaca), sumando exámenes al banco sin curado
    manual. Protegido. Corre en segundo plano. `mercados` separado por comas
    (ej. "oro,cripto"); vacío = todos. `reemplazar=true` purga la cosecha
    anterior (para limpiar una de baja calidad). Solo suma eventos NUEVOS."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)  # type: ignore[return-value]
    lista = [m.strip() for m in mercados.split(",") if m.strip()] or None
    tope = max(1, min(int(tope), 20))
    tareas.add_task(_correr_cosecha, lista, desde, hasta or None, tope, reemplazar)
    return {"estado": "cosechando", "mercados": lista or "todos", "desde": desde,
            "reemplazar": reemplazar,
            "nota": "corre en segundo plano; los nuevos exámenes aparecen en la próxima tanda"}


# ---------- El Archivo / hemeroteca (Etapa 9) ----------

@app.get("/api/archivo")
def api_archivo(respuesta: Response, mes: str = "", q: str = "", ticker: str = "", pagina: int = 0) -> dict:
    """La hemeroteca: destacadas navegables por mes, buscables por titular
    y filtrables por ticker. Paginado."""
    respuesta.headers["Cache-Control"] = "public, max-age=120"
    mes = mes.strip()[:7] or None
    texto = q.strip()[:80] or None
    tick = ticker.strip()[:12] or None
    try:
        pagina = max(0, int(pagina))
    except (TypeError, ValueError):
        pagina = 0

    conexion = persistencia.conectar()
    try:
        datos = persistencia.archivo(conexion, mes=mes, texto=texto, ticker=tick, pagina=pagina)
        meses = persistencia.meses_disponibles(conexion)
    finally:
        conexion.close()

    items = []
    for fila in datos["items"]:
        resumen = json.loads(fila["resumen_json"]) if fila["resumen_json"] else {}
        items.append({
            "id": fila["id"],
            "titular": fila["titular"],
            "fuente": fila["fuente"],
            "fecha": fila["fecha"],
            "simbolos": fila["simbolos"],
            "tarjeta": _resumen_tarjeta(resumen),
            "tiene_epilogo": bool(fila["tiene_epilogo"]),
        })
    return {"total": datos["total"], "pagina": datos["pagina"], "por_pagina": datos["por_pagina"],
            "meses": meses, "items": items, "descargo": DISCLAIMER}


class PeticionEpilogo(BaseModel):
    texto: str


@app.post("/api/epilogo/{sim_id}")
def api_epilogo(sim_id: str, peticion: PeticionEpilogo, x_pipeline_token: str = Header(default="")) -> dict:
    """'¿Y qué pasó después?' — solo Giorgio (protegido por el token de admin).

    Se muestra SIEMPRE bajo 'comparación educativa', nunca como acierto ni
    predicción (vocabulario CMF)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)  # type: ignore[return-value]
    from contenido.vocabulario import es_publicable

    texto = peticion.texto.strip()[:600]
    if texto and not es_publicable(texto):
        return JSONResponse({"error": "el texto usa vocabulario no permitido (CMF)"}, status_code=400)
    conexion = persistencia.conectar()
    try:
        ok = persistencia.guardar_epilogo(conexion, sim_id, texto)
    finally:
        conexion.close()
    if not ok:
        return Response(status_code=404)  # type: ignore[return-value]
    return {"estado": "guardado", "epilogo": texto or None}


# ---------- El brief de La Redacción (humano en el lazo) ----------

@app.get("/api/brief/{fecha}")
def api_brief(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    """El análisis de mercado de un día, para que Giorgio lo revise antes de
    enviarlo. Protegido (es material sin publicar aún)."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _re.match(r"^\d{4}-\d{2}-\d{2}$", fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        brief = persistencia.obtener_brief(conexion, fecha)
    finally:
        conexion.close()
    if brief is None:
        return Response(status_code=404)  # type: ignore[return-value]
    return brief


@app.post("/api/brief/{fecha}/aprobar")
def api_aprobar_brief(fecha: str, x_pipeline_token: str = Header(default="")) -> dict:
    """El visto bueno de Giorgio: marca el brief como aprobado."""
    if not _token_admin_ok(x_pipeline_token):
        return JSONResponse({"error": "no autorizado"}, status_code=403)
    if not _re.match(r"^\d{4}-\d{2}-\d{2}$", fecha):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        ok = persistencia.aprobar_brief(conexion, fecha)
    finally:
        conexion.close()
    if not ok:
        return Response(status_code=404)  # type: ignore[return-value]
    return {"estado": "aprobado", "fecha": fecha}
