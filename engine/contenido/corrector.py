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
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from statistics import mean

from contenido import persistencia, vocabulario
from contenido.simbolo import apto_calibracion, es_ruido, simbolo_del_hecho

DIAS_ESPERA = 1    # edad mínima de una destacada antes de intentar corregirla
RUEDAS = 2         # ventana de medición: días de mercado tras la noticia
UMBRAL_PLANO = 0.3  # bajo este |%|, la dirección se considera plana
MIN_CASOS_PRODUCCION = 80  # menos que esto, listo_produccion es siempre False

_SIMBOLOS_INDICE = {"SPY", "QQQ", "DIA", "IWM"}
_SIMBOLOS_CRIPTO = {"BTC-USD", "GBTC", "BITO", "COIN", "MSTR", "MARA", "RIOT", "ETHE"}
_SIMBOLOS_PETROLEO = {"USO", "XLE", "OXY", "SLB"}
_SIMBOLOS_ORO = {"GLD", "IAU", "GDX", "NEM", "GOLD"}


def mercado_de(simbolo: str = "", titular: str = "") -> str:
    """Mercado grosero para partir la libreta (índice ≠ cripto)."""
    s = (simbolo or "").upper().split(",")[0].strip()
    t = (titular or "").lower()
    if s in _SIMBOLOS_CRIPTO or any(k in t for k in ("bitcoin", "crypto", "ethereum", "dogecoin")):
        return "cripto"
    if s in _SIMBOLOS_INDICE:
        return "indice"
    if s in _SIMBOLOS_PETROLEO:
        return "petroleo"
    if s in _SIMBOLOS_ORO:
        return "oro"
    return "accion"



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
            simbolo = simbolo_del_hecho(sim.get("titular") or "", sim["simbolos"] or "")
            if not simbolo:
                esperando += 1  # sopa sin ancla: no puntuar el primer ticker al azar
                continue
            if es_ruido(sim.get("titular") or ""):
                esperando += 1  # ruido Benzinga: no es un examen
                continue
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


def wilson_intervalo(aciertos: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    """Intervalo de Wilson 95 % para una proporción. Honesto con n chico.

    8/12 = 67 % se siente casi 70; Wilson da ~[39 %, 86 %]. Sin esto
    la libreta miente.
    """
    if n <= 0:
        return (None, None)
    p = aciertos / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centro = (p + z2 / (2.0 * n)) / denom
    margen = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n) / denom
    return (round(max(0.0, centro - margen), 3), round(min(1.0, centro + margen), 3))


def ratio_fuerza_bruto(sim_pct: float, real_pct: float) -> float | None:
    """|sim| / |real| sin capear. >1 = el enjambre exageró. None si el real no se movió."""
    if abs(real_pct) < UMBRAL_PLANO:
        return None
    return abs(sim_pct) / abs(real_pct)


def ratio_fuerza(sim_pct: float, real_pct: float, tope: float | None = None) -> float | None:
    """Fuerza simétrica ∈ (0, 1]: 1 si las magnitudes coinciden.

    Equivale a exp(-|log(|sim|/|real|)|) = min(s/r, r/s).
    Vale 0.5 si el enjambre hizo el doble O la mitad. El `tope` se ignora
    (quedó de cuando se capeaba a 1.5 y el exceso se contaba perfecto).
    """
    bruto = ratio_fuerza_bruto(sim_pct, real_pct)
    if bruto is None:
        return None
    if bruto <= 0.0:
        return 0.0
    return bruto if bruto <= 1.0 else 1.0 / bruto


def clasificar_error(sim_pct: float, real_pct: float) -> str:
    """Una etiqueta por caso: acierto / signo / exagera / se_queda_corto / plano."""
    s, r = _signo(sim_pct), _signo(real_pct)
    if s == 0 and r == 0:
        return "ambos_planos"
    if s == 0 or r == 0:
        return "plano"
    if s != r:
        return "signo"
    bruto = abs(sim_pct) / max(abs(real_pct), 1e-9)
    if bruto > 1.5:
        return "exagera"
    if bruto < 0.5:
        return "se_queda_corto"
    return "acierto"


def error_trayectoria(sim_pct: float, real_pct: float) -> float:
    """Error de extremo a extremo, normalizado a [0, 1]."""
    denom = max(abs(real_pct), 1.0)
    return min(1.0, abs(sim_pct - real_pct) / denom)


def _vacio() -> dict:
    return {
        "casos": 0, "evaluables": 0, "aciertos_direccion": 0,
        "tasa_acierto": None, "ratio_fuerza_medio": None,
        "ratio_fuerza_bruto": None, "pct_dentro_30": None,
        "error_trayectoria": None, "loss": None,
        "listo_produccion": False, "pasa_metricas": False,
        "n_minimo_produccion": MIN_CASOS_PRODUCCION,
        "wilson_lo": None, "wilson_hi": None,
        "desglose_errores": {},
        "magnitud_media_sim": None, "magnitud_media_real": None,
    }


def evaluar_casos(casos: list[tuple[float, float]],
                  error_estilizados: float | None = None,
                  titulares: list[str] | None = None) -> dict:
    """Loss oficial de calibración sobre pares (sim_pct, real_pct).

    Loss = 0.40·E_dir + 0.35·(1-R_fuerza_simétrica) + 0.15·E_estilizados + 0.10·E_trayectoria
    R_fuerza es simétrica: pasarse de largo cuesta igual que quedarse corto.
    Si no hay hechos estilizados, se reparte ese 0.15 entre dirección y fuerza.

    listo_produccion exige además n ≥ 80. pasa_metricas ignora n (para tests).
    """
    if not casos:
        return _vacio()
    evaluables = [(s, r) for s, r in casos if _signo(s) or _signo(r)]
    aciertos = sum(1 for s, r in evaluables if _signo(s) == _signo(r))
    e_dir = 1.0 - (aciertos / len(evaluables)) if evaluables else 1.0
    ratios = [x for x in (ratio_fuerza(s, r) for s, r in casos) if x is not None]
    brutos = [x for x in (ratio_fuerza_bruto(s, r) for s, r in casos) if x is not None]
    r_fuerza = mean(ratios) if ratios else 0.0
    r_bruto = mean(brutos) if brutos else 0.0
    tray = [error_trayectoria(s, r) for s, r in casos]
    e_tray = mean(tray) if tray else 1.0
    denom_dentro = sum(1 for _, r in casos if abs(r) >= UMBRAL_PLANO)
    dentro = sum(1 for s, r in casos
                 if abs(r) >= UMBRAL_PLANO and abs(s - r) / abs(r) <= 0.30)
    pct_dentro = (dentro / denom_dentro) if denom_dentro else None

    if error_estilizados is None:
        w_dir, w_fza, w_est, w_tray = 0.48, 0.42, 0.0, 0.10
        e_est = 0.0
    else:
        w_dir, w_fza, w_est, w_tray = 0.40, 0.35, 0.15, 0.10
        e_est = max(0.0, min(1.0, error_estilizados))
    # r_fuerza ya ∈ (0, 1]; no hace falta min(1, ·) — eso es lo que
    # antes convertía un exceso capeado a 1.5 en error 0.
    loss = (w_dir * e_dir
            + w_fza * (1.0 - r_fuerza)
            + w_est * e_est
            + w_tray * e_tray)
    tasa = round(aciertos / len(evaluables), 2) if evaluables else None
    wilson_lo, wilson_hi = wilson_intervalo(aciertos, len(evaluables))
    pasa = bool(
        tasa is not None and tasa >= 0.70
        and r_fuerza >= 0.70
        and (pct_dentro or 0) >= 0.40
    )
    desglose = dict(Counter(clasificar_error(s, r) for s, r in casos))
    out = {
        "casos": len(casos),
        "evaluables": len(evaluables),
        "aciertos_direccion": aciertos,
        "tasa_acierto": tasa,
        "wilson_lo": wilson_lo,
        "wilson_hi": wilson_hi,
        "ratio_fuerza_medio": round(r_fuerza, 3) if ratios else None,
        "ratio_fuerza_bruto": round(r_bruto, 3) if brutos else None,
        "pct_dentro_30": round(pct_dentro, 3) if pct_dentro is not None else None,
        "error_trayectoria": round(e_tray, 3),
        "error_estilizados": error_estilizados,
        "loss": round(loss, 4),
        "pasa_metricas": pasa,
        "listo_produccion": bool(pasa and len(evaluables) >= MIN_CASOS_PRODUCCION),
        "n_minimo_produccion": MIN_CASOS_PRODUCCION,
        "desglose_errores": desglose,
        "magnitud_media_sim": round(mean(abs(s) for s, _ in casos), 2),
        "magnitud_media_real": round(mean(abs(r) for _, r in casos), 2),
    }
    if titulares and len(titulares) == len(casos):
        from brains.fallback import clasificar_titular
        cajas = Counter()
        for (s, r), tit in zip(casos, titulares):
            t = clasificar_titular(tit or "")
            cajas[f"{t['tipo']}|{t['regimen']}|{clasificar_error(s, r)}"] += 1
        out["desglose_taxonomia"] = dict(cajas)
    return out


def _resumir(casos: list[tuple[float, float]],
             titulares: list[str] | None = None) -> dict:
    """Las métricas de un conjunto de casos (sim_pct, real_pct)."""
    extra = evaluar_casos(casos, titulares=titulares)
    return {
        "casos": extra["casos"],
        "evaluables": extra["evaluables"],
        "aciertos_direccion": extra["aciertos_direccion"],
        "tasa_acierto": extra["tasa_acierto"],
        "wilson_lo": extra.get("wilson_lo"),
        "wilson_hi": extra.get("wilson_hi"),
        "magnitud_media_sim": extra.get("magnitud_media_sim"),
        "magnitud_media_real": extra.get("magnitud_media_real"),
        "ratio_fuerza_medio": extra["ratio_fuerza_medio"],
        "ratio_fuerza_bruto": extra.get("ratio_fuerza_bruto"),
        "pct_dentro_30": extra["pct_dentro_30"],
        "error_trayectoria": extra["error_trayectoria"],
        "loss": extra["loss"],
        "pasa_metricas": extra.get("pasa_metricas"),
        "listo_produccion": extra["listo_produccion"],
        "n_minimo_produccion": extra.get("n_minimo_produccion", MIN_CASOS_PRODUCCION),
        "desglose_errores": extra.get("desglose_errores") or {},
        "desglose_taxonomia": extra.get("desglose_taxonomia"),
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
            "SELECT s.titular, s.resumen_json, s.reaccion_real, s.fuente, "
            "COALESCE(t.simbolos, '') AS simbolos "
            "FROM simulaciones s LEFT JOIN titulares t ON t.sim_id = s.id "
            "WHERE s.reaccion_real IS NOT NULL AND (s.destacada = 1 OR s.fuente = 'backtest')"
        ).fetchall()
    finally:
        if propia:
            conexion.close()

    vivo, historico, excluidos, excluidos_ruido = [], [], 0, 0
    vivo_tits, hist_tits = [], []
    por_mercado: dict[str, list] = {}
    por_mercado_tits: dict[str, list] = {}
    for fila in filas:
        reaccion = json.loads(fila["reaccion_real"])
        if reaccion.get("cerebros") == "respaldo":
            excluidos += 1  # simulado sin IA (sin saldo): no califica al titular
            continue
        tit = fila["titular"] or ""
        sims = fila["simbolos"] or ""
        scored = reaccion.get("simbolo") or ""
        if not apto_calibracion(tit, sims, scored):
            excluidos_ruido += 1  # ruido / sopa mal puntuada
            continue
        sim = float(json.loads(fila["resumen_json"]).get("direccion_pct") or 0)
        real = float(reaccion.get("pct_real") or 0)
        mkt = mercado_de(scored or "", tit)
        por_mercado.setdefault(mkt, []).append((sim, real))
        por_mercado_tits.setdefault(mkt, []).append(tit)
        if fila["fuente"] == "backtest":
            historico.append((sim, real))
            hist_tits.append(tit)
        else:
            vivo.append((sim, real))
            vivo_tits.append(tit)

    n_eval = len(vivo) + len(historico)
    foco_casos = (por_mercado.get("indice") or []) + (por_mercado.get("accion") or [])
    foco_tits = (por_mercado_tits.get("indice") or []) + (por_mercado_tits.get("accion") or [])
    total = _resumir(vivo + historico, titulares=vivo_tits + hist_tits)
    foco = _resumir(foco_casos, titulares=foco_tits) if foco_casos else _vacio()
    # el producto es índice + acción: cripto no puede declarar victoria
    total["listo_produccion"] = bool(foco.get("listo_produccion"))
    total["pasa_metricas"] = bool(foco.get("pasa_metricas"))
    return {
        **total,
        "en_vivo": _resumir(vivo, titulares=vivo_tits),
        "historico": _resumir(historico, titulares=hist_tits),
        "foco_producto": foco,
        "por_mercado": {k: _resumir(v, titulares=por_mercado_tits[k])
                        for k, v in por_mercado.items()},
        "excluidos_respaldo": excluidos,
        "excluidos_ruido": excluidos_ruido,
        "nota": (
            f"con menos de {MIN_CASOS_PRODUCCION} casos hold-out (índice+acción) la tasa es hipótesis, "
            "no calibración — el intervalo de Wilson muestra la incertidumbre"
            if len(foco_casos) < MIN_CASOS_PRODUCCION
            else "hold-out de índice+acción suficiente para hablar de calibración, no de marketing"
        ),
    }

