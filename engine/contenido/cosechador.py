"""El cosechador — genera exámenes REALES automáticamente.

Idea: para calibrar de verdad no basta con inventar titulares. Cada examen
necesita una noticia REAL, de una fecha REAL, con un resultado REAL. Este
módulo lo consigue solo:

1. Busca los **días de mayor movimiento** de cada símbolo (Yahoo Finance):
   esos son los días en que "pasó algo".
2. Le pega el **titular real** de ese día (Alpaca News / Benzinga).
3. Solo conserva el evento si EXISTE un titular real. Si no hay noticia,
   descarta el día — **nunca inventa** una (regla de oro del proyecto).

Así el banco de exámenes escala hacia los 100 por mercado sin curado
manual, y sin ensuciar la calibración con noticias falsas.

El resultado son "eventos candidatos" con el mismo formato que
backtest_eventos.json, listos para revisar y fusionar al banco.
"""

from datetime import datetime, timedelta, timezone

import httpx

URL_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"

# Umbral de "día de movimiento" por mercado: un día importa si el símbolo se
# movió más que esto (en %). Calibrado a la volatilidad típica de cada uno:
# el oro se mueve poco, la cripto mucho — un 3% no significa lo mismo en cada
# uno. Así cosechamos eventos comparables en "sorpresa", no en tamaño bruto.
UMBRAL_POR_MERCADO = {
    "indice": 2.5,
    "accion": 6.0,
    "petroleo": 4.0,
    "oro": 2.5,
    "cripto": 7.0,
}
UMBRAL_DEFECTO = 4.0

# Distancia mínima (en días de mercado) entre dos eventos del mismo símbolo:
# evita cosechar tres días seguidos del mismo desplome como si fueran tres
# noticias distintas.
SEPARACION_MINIMA = 5

# Cuánto se mide la reacción (misma ventana que el corrector en vivo).
RUEDAS = 2

# La lista de caza por mercado. Símbolos con histórico largo en Yahoo Y
# cobertura de noticias en Benzinga/Alpaca (2015+). Para acciones: variadas
# —grandes y medianas, de sectores distintos— tal como pidió el proyecto,
# no solo las gigantes. Se puede ampliar sin tocar el resto del código.
WATCHLIST_DEFECTO: dict[str, str] = {
    # índices
    "SPY": "indice", "QQQ": "indice", "DIA": "indice", "IWM": "indice",
    # oro y mineras de oro
    "GLD": "oro", "IAU": "oro", "GDX": "oro", "NEM": "oro", "GOLD": "oro",
    # cripto (proxies bursátiles: ETFs, exchange y mineras)
    "GBTC": "cripto", "COIN": "cripto", "MARA": "cripto", "RIOT": "cripto",
    "MSTR": "cripto", "ETHE": "cripto", "BITO": "cripto",
    # petróleo y energía
    "USO": "petroleo", "XLE": "petroleo", "OXY": "petroleo", "SLB": "petroleo",
    # acciones — grandes
    "AAPL": "accion", "MSFT": "accion", "NVDA": "accion", "AMZN": "accion",
    "GOOGL": "accion", "META": "accion", "TSLA": "accion", "NFLX": "accion",
    "JPM": "accion", "XOM": "accion", "WMT": "accion", "DIS": "accion",
    # acciones — medianas y variadas (sectores distintos)
    "AMD": "accion", "INTC": "accion", "MU": "accion", "QCOM": "accion",
    "BA": "accion", "GE": "accion", "CAT": "accion", "F": "accion",
    "GM": "accion", "T": "accion", "PFE": "accion", "MRNA": "accion",
    "KO": "accion", "PEP": "accion", "TGT": "accion", "NKE": "accion",
    "SBUX": "accion", "MCD": "accion", "HD": "accion", "CRM": "accion",
    "PYPL": "accion", "SQ": "accion", "SHOP": "accion", "ROKU": "accion",
    "UBER": "accion", "ABNB": "accion", "SNAP": "accion", "PLTR": "accion",
    "GME": "accion", "AMC": "accion", "RIVN": "accion", "LCID": "accion",
    "SOFI": "accion", "HOOD": "accion", "DKNG": "accion", "RBLX": "accion",
    "MRVL": "accion", "CVNA": "accion",
}


def _historia_diaria(simbolo: str, desde: str, hasta: str) -> list[tuple[str, float]]:
    """(fecha_iso, cierre) de cada rueda entre `desde` y `hasta`. [] si falla."""
    try:
        p1 = int(datetime.fromisoformat(desde).replace(tzinfo=timezone.utc).timestamp())
        p2 = int(datetime.fromisoformat(hasta).replace(tzinfo=timezone.utc).timestamp())
        respuesta = httpx.get(
            URL_YAHOO.format(simbolo=simbolo),
            params={"period1": p1, "period2": p2, "interval": "1d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20,
        )
        respuesta.raise_for_status()
        resultado = respuesta.json()["chart"]["result"][0]
        marcas = resultado["timestamp"]
        cierres = resultado["indicators"]["quote"][0]["close"]
    except Exception:
        return []
    barras = []
    for ts, cierre in zip(marcas, cierres):
        if cierre is None:
            continue
        dia = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        barras.append((dia, float(cierre)))
    return barras


def _categoria(pct: float) -> str:
    if pct <= -1.0:
        return "negativa"
    if pct >= 1.0:
        return "positiva"
    return "neutra"


def dias_de_movimiento(simbolo: str, mercado: str, desde: str, hasta: str,
                       ruedas: int = RUEDAS) -> list[dict]:
    """Los días en que `simbolo` se movió fuerte, con la reacción medida en la
    misma ventana que usa el corrector (cierre previo → `ruedas` ruedas después).

    Devuelve candidatos SIN titular todavía: {fecha, simbolo, mercado,
    categoria, pct_ventana}. El titular real se busca aparte (puede no existir).
    """
    umbral = UMBRAL_POR_MERCADO.get(mercado, UMBRAL_DEFECTO)
    barras = _historia_diaria(simbolo, desde, hasta)
    if len(barras) < ruedas + 2:
        return []

    candidatos = []
    for i in range(1, len(barras) - ruedas):
        fecha_prev, cierre_prev = barras[i - 1]
        fecha, _ = barras[i]
        _, cierre_final = barras[i + ruedas - 1]
        if not cierre_prev:
            continue
        # el movimiento del propio día decide si "pasó algo"
        cambio_dia = (barras[i][1] - cierre_prev) / cierre_prev * 100
        if abs(cambio_dia) < umbral:
            continue
        # pero la NOTA se mide en la ventana del corrector (base → ruedas después)
        pct_ventana = round((cierre_final - cierre_prev) / cierre_prev * 100, 2)
        candidatos.append({
            "fecha": fecha,
            "simbolo": simbolo,
            "mercado": mercado,
            "categoria": _categoria(pct_ventana),
            "pct_ventana": pct_ventana,
            "_cambio_dia": round(cambio_dia, 2),
        })

    # espaciar: si dos candidatos caen a menos de SEPARACION_MINIMA ruedas,
    # quedarse con el de mayor movimiento (una noticia, no la misma racha)
    candidatos.sort(key=lambda c: abs(c["_cambio_dia"]), reverse=True)
    elegidos: list[dict] = []
    for cand in candidatos:
        f = datetime.fromisoformat(cand["fecha"])
        if all(abs((f - datetime.fromisoformat(e["fecha"])).days) >= SEPARACION_MINIMA
               for e in elegidos if e["simbolo"] == cand["simbolo"]):
            elegidos.append(cand)
    elegidos.sort(key=lambda c: c["fecha"])
    return elegidos


def _titular_de(simbolo: str, fecha: str) -> dict | None:
    """El titular real de Benzinga para `simbolo` alrededor de `fecha` (Alpaca).

    Busca en la ventana [fecha-1día, fecha] y devuelve el titular cuyo momento
    esté más cerca de la fecha del movimiento. None si no hay claves, red o
    ninguna noticia — en ese caso el día se descarta (no se inventa titular).
    """
    import os

    if not (os.environ.get("ALPACA_API_KEY_ID") and os.environ.get("ALPACA_API_SECRET_KEY")):
        return None
    inicio = (datetime.fromisoformat(fecha) - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    fin = (datetime.fromisoformat(fecha) + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    try:
        respuesta = httpx.get(
            "https://data.alpaca.markets/v1beta1/news",
            params={"symbols": simbolo, "start": inicio, "end": fin,
                    "limit": 50, "sort": "desc"},
            headers={
                "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY_ID"],
                "APCA-API-SECRET-KEY": os.environ["ALPACA_API_SECRET_KEY"],
            },
            timeout=15,
        )
        respuesta.raise_for_status()
        noticias = [n for n in respuesta.json().get("news", []) if n.get("headline")]
    except Exception:
        return None
    if not noticias:
        return None
    # el titular cuyo momento cae más cerca del cierre del día del movimiento
    ancla = datetime.fromisoformat(fecha).replace(tzinfo=timezone.utc)

    def distancia(n):
        try:
            t = datetime.fromisoformat(n["created_at"].replace("Z", "+00:00"))
            return abs((t - ancla).total_seconds())
        except Exception:
            return float("inf")

    mejor = min(noticias, key=distancia)
    return {"titular": mejor["headline"].strip(),
            "fuente_noticia": mejor.get("source", "benzinga"),
            "url": mejor.get("url", "")}


def _id_evento(simbolo: str, fecha: str, mercado: str) -> str:
    return f"{fecha}-{mercado[:3]}-cosecha-{simbolo.lower()}"


def cosechar(watchlist: dict[str, str], desde: str, hasta: str,
             ids_existentes: set[str] | None = None,
             tope_por_simbolo: int = 8) -> dict:
    """Cosecha eventos reales para una lista de símbolos.

    watchlist: {simbolo: mercado}. desde/hasta: rango ISO (AAAA-MM-DD).
    ids_existentes: ids del banco actual, para no repetir.
    Devuelve {"eventos": [...], "sin_titular": [...], "resumen": {...}}.
    """
    ids_existentes = ids_existentes or set()
    eventos, sin_titular = [], []
    por_mercado: dict[str, int] = {}
    for simbolo, mercado in watchlist.items():
        candidatos = dias_de_movimiento(simbolo, mercado, desde, hasta)
        # los de mayor movimiento primero, hasta el tope por símbolo
        candidatos.sort(key=lambda c: abs(c["_cambio_dia"]), reverse=True)
        tomados = 0
        for cand in candidatos:
            if tomados >= tope_por_simbolo:
                break
            id_evento = _id_evento(simbolo, cand["fecha"], mercado)
            if id_evento in ids_existentes:
                continue
            titular = _titular_de(simbolo, cand["fecha"])
            if titular is None:
                sin_titular.append({"simbolo": simbolo, "fecha": cand["fecha"]})
                continue
            eventos.append({
                "id": id_evento,
                "fecha": cand["fecha"],
                "simbolo": simbolo,
                "categoria": cand["categoria"],
                "mercado": mercado,
                "titular": titular["titular"],
            })
            ids_existentes.add(id_evento)
            por_mercado[mercado] = por_mercado.get(mercado, 0) + 1
            tomados += 1
    eventos.sort(key=lambda e: e["fecha"])
    return {"eventos": eventos, "sin_titular": sin_titular,
            "resumen": {"cosechados": len(eventos), "sin_titular": len(sin_titular),
                        "por_mercado": por_mercado}}


def cosechar_y_guardar(mercados: list[str] | None = None,
                       desde: str = "2016-01-01", hasta: str | None = None,
                       tope_por_simbolo: int = 8) -> dict:
    """Cosecha eventos reales y los sube a GitHub (datos/cosecha.json).

    `mercados`: filtra la watchlist (ej. ["oro", "cripto"]); None = todos.
    El banco de exámenes los recoge solo en la próxima tanda (cargar_eventos
    fusiona lo local con lo cosechado). NUNCA lanza hacia el pipeline.
    """
    from contenido import backtest, respaldo

    if hasta is None:
        hasta = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    watchlist = WATCHLIST_DEFECTO
    if mercados:
        objetivo = {m.lower() for m in mercados}
        watchlist = {s: m for s, m in WATCHLIST_DEFECTO.items() if m in objetivo}

    ids_existentes = {e["id"] for e in backtest.cargar_eventos()}
    resultado = cosechar(watchlist, desde, hasta, ids_existentes, tope_por_simbolo)
    if resultado["eventos"]:
        resultado["respaldo"] = respaldo.subir_cosecha(resultado["eventos"])
    return resultado
