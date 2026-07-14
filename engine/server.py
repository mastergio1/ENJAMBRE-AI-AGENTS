"""Servidor de El Enjambre — FastAPI + WebSocket.

Flujo: el navegador se conecta a /ws y envía un titular. El servidor
corre el mercado real (5.000 agentes), hace que los 100 líderes lean la
noticia (LLM con fallback) y transmite cada tick al frontend:

- mensaje de texto "inicio": las respuestas de los líderes
- un frame binario por tick: [precio f32][tick u32][sentimiento i8 × 5000]
- mensaje de texto "fin": el reporte de la simulación

El sentimiento por agente viaja como un byte (-127..127): la escena 3D
solo necesita saber cuánto pánico o codicia siente cada partícula.
"""

import asyncio
import contextlib as _contextlib
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


@app.middleware("http")
async def blindaje(request: Request, call_next):
    """Rate-limit por IP en /api/* y cabeceras de seguridad en todo."""
    ruta = request.url.path
    if ruta.startswith("/api/"):
        ip = seguridad.ip_cliente(request.headers, request.client.host if request.client else None)
        if not seguridad.permitir_http(ip, ruta):
            return JSONResponse({"error": "Demasiadas solicitudes. Espera un momento."}, status_code=429)
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
    return {"estado": "ok", "proyecto": "El Enjambre", "etapa": 10, "redaccion": True}


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
    consultas = [(_semilla_lider(semilla, lider.unique_id), lider.arquetipo) for lider in lideres]
    respuestas = await analizar_titular_async(titular, consultas)  # lento: sin candado
    async with candado:
        await asyncio.to_thread(modelo.aplicar_titular, titular, respuestas)
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

    # los 100 líderes leen el titular (en paralelo si hay API; si no, fallback);
    # la semilla de la corrida entra a la mezcla: cada corrida, voces frescas
    consultas = [(_semilla_lider(semilla, lider.unique_id), lider.arquetipo) for lider in lideres]
    respuestas = await analizar_titular_async(titular, consultas)

    await ws.send_text(json.dumps({
        "tipo": "inicio",
        "titular": titular,
        "precio": modelo.historial_precios[-1],
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
    modelo.aplicar_titular(titular, respuestas=respuestas)

    for _ in range(TICKS_POSTERIORES):
        await transmitir_tick()

    reporte = _generar_reporte(modelo, precio_previo, respuestas, lideres, contador_acciones)

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


@app.post("/api/simular-titular")
def simular_titular(peticion: PeticionSimular) -> dict:
    """Chequeo previo de la simulación on-demand desde una tarjeta.

    No consume el cupo (eso pasa al correr de verdad por el WebSocket);
    responde si hay presupuesto y devuelve el titular a simular.
    """
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
    return os.environ.get("ENJAMBRE_WEB_URL", "https://enjambre.vercel.app")


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
