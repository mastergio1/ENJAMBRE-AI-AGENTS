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
import json
import struct
from collections import defaultdict

import os

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
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
MAX_MENSAJE_WS = 4000     # bytes de texto por mensaje del cliente
MAX_SIM_CONCURRENTES = 2  # simulaciones pesadas en vuelo a la vez

# orígenes permitidos: la web de producción + localhost de desarrollo.
# Configurable por entorno (ENJAMBRE_ORIGENES, separado por comas).
_origenes_env = os.environ.get("ENJAMBRE_ORIGENES", "").strip()
ORIGENES = [o.strip() for o in _origenes_env.split(",") if o.strip()] or [
    "http://localhost:5173",
    "http://localhost:4173",
]

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


@app.get("/salud")
def salud() -> dict:
    return {"estado": "ok", "proyecto": "El Enjambre", "etapa": 7}


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
            if not isinstance(mensaje, dict) or mensaje.get("tipo") != "simular":
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


# ---------- la simulación transmitida ----------

async def _correr_simulacion(ws: WebSocket, mensaje: dict) -> None:
    titular = str(mensaje.get("titular", ""))[:300].strip() or "Sin novedades en los mercados"
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

    # los 100 líderes leen el titular (en paralelo si hay API; si no, fallback)
    consultas = [(lider.unique_id, lider.arquetipo) for lider in lideres]
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


@app.get("/api/simulacion/{sim_id}")
def simulacion(sim_id: str, respuesta: Response) -> dict:
    if not seguridad.sim_id_valido(sim_id):
        return Response(status_code=404)  # type: ignore[return-value]
    conexion = persistencia.conectar()
    try:
        datos = persistencia.obtener_simulacion(conexion, sim_id)
    finally:
        conexion.close()
    if datos is None:
        return Response(status_code=404)  # type: ignore[return-value]
    respuesta.headers["Cache-Control"] = "public, max-age=300"
    return {
        "id": datos["id"],
        "titular": datos["titular"],
        "fuente": datos["fuente"],
        "fecha": datos["fecha"],
        "destacada": bool(datos["destacada"]),
        "resumen": datos["resumen"],
        "tarjeta": _resumen_tarjeta(datos["resumen"]),
        "lideres": datos["lideres"],
        "serie_precios": datos["serie_precios"],
        "tiene_replay": persistencia.leer_frames(sim_id) is not None,
    }


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
