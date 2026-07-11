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


if __name__ == "__main__":
    resultado = preparar_dia()
    print(f"fuente: {resultado['origen']}")
    for publicada in resultado.get("publicadas", []):
        print(f"  ★ [{publicada['impacto']}/10] {publicada['titular']}  → sim {publicada['sim_id']}")
    if not resultado.get("publicadas"):
        print(f"  ({resultado.get('motivo', 'sin titulares elegibles')})")
