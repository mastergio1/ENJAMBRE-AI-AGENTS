"""
Recopila noticias reales y movimientos del SPY para validación (laboratorio).

Correcciones vs. el bundle original (para que de verdad funcione):
  1. El movimiento del SPY se baja por el endpoint v8/finance/chart de Yahoo
     (el que SÍ responde y usa el propio motor en engine/contenido/fuentes/
     yahoo.py). El v7/finance/download del bundle está DEPRECADO (HTTP 401) y
     devolvía 0.0 siempre → dataset inútil.
  2. io.StringIO en vez de pd.compat.StringIO (removido en pandas moderno).
  3. NewsAPI degrada con un mensaje claro si falta NEWS_API_KEY (nunca se
     hardcodea una clave).

⚠️ Límites honestos de NewsAPI (plan free): ~1 mes hacia atrás (no 60 días),
100 req/día, sin uso comercial. Y correlacionar noticias en ESPAÑOL con
movimientos intradía del SPY (un ETF de EE.UU.) es señal débil: para validar el
enjambre conviene noticias en inglés y de mercado. Además el intradía de 5m solo
existe para ~60 días y en horario de mercado (noche/fin de semana → sin dato).
"""

import io
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

import httpx
import pandas as pd

# ==============================================
# CONFIGURACIÓN
# ==============================================
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")   # regístrate gratis en newsapi.org
TICKER = "SPY"
INTERVALO_MINUTOS = 30          # movimiento en los 30 min tras la noticia
DIAS_ATRAS = 30                 # NewsAPI free solo cubre ~1 mes
_URL_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}"
_SALIDA = os.path.join(os.path.dirname(__file__), "data", "noticias_reales.csv")


# ==============================================
# 1. NOTICIAS (NewsAPI)
# ==============================================
def obtener_noticias(dias: int = DIAS_ATRAS) -> List[Dict]:
    if not NEWS_API_KEY:
        print("⚠️ Falta NEWS_API_KEY (regístrate gratis en newsapi.org y expórtala "
              "en el entorno). Sin clave no se pueden bajar noticias.")
        return []

    fecha_desde = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
    try:
        with httpx.Client(timeout=30.0) as client:
            respuesta = client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "stock market OR S&P 500 OR SPY OR Federal Reserve",
                    "from": fecha_desde,
                    "sortBy": "publishedAt",
                    "language": "en",     # inglés: señal más fuerte para el SPY
                    "pageSize": 100,
                    "apiKey": NEWS_API_KEY,
                },
            )
            respuesta.raise_for_status()
            data = respuesta.json()
        if data.get("status") != "ok":
            print(f"⚠️ Error en NewsAPI: {data.get('message', '')}")
            return []
        noticias = [
            {
                "titular": a["title"],
                "fecha": a["publishedAt"],
                "fuente": a.get("source", {}).get("name", "desconocida"),
                "descripcion": a.get("description", ""),
            }
            for a in data.get("articles", [])
            if a.get("title") and a.get("publishedAt")
        ]
        print(f"✅ Obtenidas {len(noticias)} noticias desde {fecha_desde}")
        return noticias
    except Exception as e:
        print(f"❌ Error obteniendo noticias: {e}")
        return []


# ==============================================
# 2. MOVIMIENTO DEL SPY (v8/finance/chart — el que SÍ responde)
# ==============================================
def obtener_movimiento_spy(fecha: str) -> float:
    """Retorno del SPY en los INTERVALO_MINUTOS posteriores a la noticia.
    0.0 si no hay dato intradía (noche/fin de semana, o fuera de los ~60 días)."""
    try:
        dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
        p1 = int(dt.timestamp())
        p2 = int((dt + timedelta(minutes=INTERVALO_MINUTOS + 5)).timestamp())
        with httpx.Client(timeout=30.0) as client:
            respuesta = client.get(
                _URL_CHART.format(simbolo=TICKER),
                params={"period1": p1, "period2": p2, "interval": "5m"},
                headers={"User-Agent": "Mozilla/5.0"},
            )
        if respuesta.status_code != 200:
            return 0.0
        r = respuesta.json()["chart"]["result"][0]
        cierres = [c for c in r["indicators"]["quote"][0]["close"] if c is not None]
        if len(cierres) < 2:
            return 0.0
        return float((cierres[-1] - cierres[0]) / cierres[0])
    except Exception:
        return 0.0


# ==============================================
# 3. RECOPILAR
# ==============================================
def recopilar_datos_completos():
    noticias = obtener_noticias()
    if not noticias:
        print("❌ No se obtuvieron noticias (¿falta la API key?).")
        return None

    datos = []
    for i, n in enumerate(noticias):
        print(f"Procesando {i + 1}/{len(noticias)}: {n['titular'][:50]}…")
        datos.append({
            "titular": n["titular"],
            "fecha": n["fecha"],
            "fuente": n["fuente"],
            "retorno_spy_30min": obtener_movimiento_spy(n["fecha"]),
        })
        time.sleep(0.1)   # cortesía con la API

    df = pd.DataFrame(datos)
    os.makedirs(os.path.dirname(_SALIDA), exist_ok=True)
    df.to_csv(_SALIDA, index=False)

    con_dato = df[df["retorno_spy_30min"] != 0.0]
    print(f"\n✅ Datos guardados en: {_SALIDA}")
    print(f"   Total noticias: {len(df)} | con movimiento intradía: {len(con_dato)}")
    if len(con_dato):
        print(f"   Retorno promedio: {con_dato['retorno_spy_30min'].mean():.4f}")
        print(f"   Rango: {con_dato['retorno_spy_30min'].min():.4f} a "
              f"{con_dato['retorno_spy_30min'].max():.4f}")
    return df


if __name__ == "__main__":
    recopilar_datos_completos()
