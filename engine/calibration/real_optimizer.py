"""
CALIBRADOR DEL MOTOR REAL (Basado en Hechos Estilizados)
- Optimiza contra Curtosis, Clustering de Volatilidad y Asimetría
- Usa el modelo MercadoEnjambre real (engine/model.py)
- Headless: sin WebSockets, sin frontend

NOTA (correcciones vs. el bundle original, para que enchufe con la API real):
  1. RUTA_CONFIG se importa de `model`, no de `config.agentes` (no existe).
  2. El precio del tick es `modelo.historial_precios[-1]` (no hay `precio_actual`
     ni `obtener_precio()`); el inicial es `historial_precios[0]`.
  3. `io.StringIO` en vez de `pd.compat.StringIO` (removido en pandas moderno).
"""

import gc
import io
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict

import numpy as np
import optuna
import pandas as pd

logging.basicConfig(level=logging.WARNING)

# ==============================================
# 1. IMPORTAR EL MODELO REAL
# ==============================================
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model import MercadoEnjambre, RUTA_CONFIG  # noqa: E402  (RUTA_CONFIG vive aquí)

print("✅ Modelo real importado: MercadoEnjambre")
print(f"   Config agentes: {RUTA_CONFIG}")

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ==============================================
# TARGETS CANÓNICOS DE UN MERCADO REAL (hechos estilizados)
# ==============================================
# Por qué NO usamos una descarga de SPY: el endpoint /v7/finance/download de
# Yahoo está deprecado (401), y el respaldo Cauchy tiene momentos INDEFINIDOS
# (kurtosis/skew de una muestra dan valores absurdos e inestables: ~145 / ~+11).
# Los hechos estilizados son propiedades UNIVERSALES y estables de los mercados;
# se calibra contra esos valores canónicos, no contra la ruta puntual de un
# índice. Son los mismos criterios que valida engine/validation/ (CLAUDE.md §7):
#   - curtosis > 3            → colas gordas (los extremos pasan más que en Gauss)
#   - AC de |retornos| > 0    → clustering de volatilidad (la turbulencia viene en rachas)
#   - asimetría negativa      → las caídas son más violentas que las subidas (pánico)
TARGET_STATS = {"kurtosis": 5.0, "vol_clustering": 0.25, "skew": -0.30}


# ==============================================
# 2. LECTOR ROBUSTO DE SPY (httpx, sin yfinance)
# ==============================================
def download_spy_benchmark_robust(days=60):
    """Descarga SPY usando httpx (respeta el proxy, a diferencia de yfinance).
    OJO: el endpoint /v7/finance/download de Yahoo está deprecado; si falla,
    cae a un benchmark sintético de cola gorda para probar el flujo."""
    import httpx

    end = datetime.now()
    start = end - timedelta(days=days)
    url = (f"https://query1.finance.yahoo.com/v7/finance/download/SPY"
           f"?period1={int(start.timestamp())}&period2={int(end.timestamp())}"
           f"&interval=5m&events=history")

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))

            if df.empty:
                raise RuntimeError("Datos vacíos")

            df["log_return_cum"] = np.log(df["Close"] / df["Close"].iloc[0])
            df = df.dropna()
            df_bench = df[["Close", "log_return_cum"]].iloc[:200]

            output_path = os.path.join(_DATA_DIR, "real_benchmark_robust.csv")
            os.makedirs(_DATA_DIR, exist_ok=True)
            df_bench.to_csv(output_path, index=False)

            print(f"✅ Benchmark robusto guardado: {output_path} ({len(df_bench)} filas)")
            return df_bench["log_return_cum"].values

    except Exception as e:
        print(f"⚠️ Falló descarga robusta: {e}")
        print("📊 Usando benchmark sintético (Cauchy) para probar el flujo…")
        return np.random.standard_cauchy(200).cumsum() * 0.01


# ==============================================
# 3. CÁLCULO DE HECHOS ESTILIZADOS
# ==============================================
def calcular_hechos_estilizados(series: np.ndarray) -> Dict[str, float]:
    """Curtosis (>3 = colas gordas), clustering de volatilidad (AC de |ret|),
    asimetría (negativa = efecto pánico)."""
    if len(series) < 10:
        return {"kurtosis": 0.0, "vol_clustering": 0.0, "skew": 0.0}

    retornos = np.diff(series)
    if len(retornos) < 2:
        return {"kurtosis": 0.0, "vol_clustering": 0.0, "skew": 0.0}

    kurt = pd.Series(retornos).kurtosis()

    abs_ret = np.abs(retornos)
    if len(abs_ret) > 1 and np.std(abs_ret) > 0:
        vol_clust = np.corrcoef(abs_ret[:-1], abs_ret[1:])[0, 1]
    else:
        vol_clust = 0.0

    skew = pd.Series(retornos).skew()

    return {
        "kurtosis": float(kurt) if not np.isnan(kurt) else 0.0,
        "vol_clustering": float(vol_clust) if not np.isnan(vol_clust) else 0.0,
        "skew": float(skew) if not np.isnan(skew) else 0.0,
    }


# ==============================================
# 4. SIMULADOR HEADLESS DEL MOTOR REAL
# ==============================================
def run_headless_real_simulation(params: Dict[str, float], steps: int = 200) -> np.ndarray:
    """Ejecuta el modelo MercadoEnjambre real sin WebSockets."""
    try:
        modelo = MercadoEnjambre(
            seed=int(params.get("seed", 42)),
            precio_inicial=100.0,
            ticks_horizonte=steps,
            ruta_config=RUTA_CONFIG,
        )

        np.random.seed(int(params.get("seed", 42)) + 1)
        intensidad = params.get("noticias_intensidad", 0.5)
        ruido = params.get("ruido_base", 0.01)

        noticias = []
        for _ in range(steps):
            if np.random.rand() < 0.15:                       # 15% shock grande
                noticias.append(np.random.standard_t(df=3) * intensidad * 0.5)
            else:
                noticias.append(np.random.normal(0, ruido))   # 85% ruido de fondo

        precios = [modelo.historial_precios[0]]               # (fix #2) = 100.0
        for i in range(steps):
            modelo.aplicar_noticia(sentimiento=noticias[i])
            modelo.step()
            precios.append(modelo.historial_precios[-1])       # (fix #3)

        precios = np.array(precios)
        serie = np.log(precios / precios[0])                   # log-retornos acum.
        # liberar el modelo (10.000 agentes con refs cíclicas) para no acumular
        # basura entre trials → sin esto, Render/entornos con poca RAM hacen OOM
        # (mismo aprendizaje del backtest del proyecto).
        del modelo
        gc.collect()
        return serie

    except Exception as e:
        print(f"❌ Error en simulación headless: {e}")
        import traceback
        traceback.print_exc()
        return np.random.randn(steps).cumsum() * 0.01


# ==============================================
# 5. CACHE DEL BENCHMARK REAL
# ==============================================
_real_benchmark_cache = None


def load_real_benchmark():
    global _real_benchmark_cache
    if _real_benchmark_cache is not None:
        return _real_benchmark_cache

    path = os.path.join(_DATA_DIR, "real_benchmark_robust.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        _real_benchmark_cache = df["log_return_cum"].values
        return _real_benchmark_cache

    _real_benchmark_cache = download_spy_benchmark_robust()
    return _real_benchmark_cache


# ==============================================
# 6. FUNCIÓN OBJETIVO DE OPTUNA
# ==============================================
def objective(trial):
    params = {
        "noticias_intensidad": trial.suggest_float("noticias_intensidad", 0.1, 2.0),
        "ruido_base": trial.suggest_float("ruido_base", 0.001, 0.05),
        "seed": trial.suggest_int("seed", 1, 1000),
    }

    sim_series = run_headless_real_simulation(params, steps=150)
    sim_stats = calcular_hechos_estilizados(sim_series)

    # objetivo = valores canónicos de mercado (estables), no una descarga rota
    real_stats = TARGET_STATS

    def safe_score(real_val, sim_val):
        if abs(real_val) < 0.01:
            return 1.0 if abs(sim_val) < 0.01 else 0.0
        error = abs(real_val - sim_val) / abs(real_val)
        return max(0.0, 1.0 - min(error, 1.0))

    score_kurt = safe_score(real_stats["kurtosis"], sim_stats["kurtosis"])
    score_clust = safe_score(real_stats["vol_clustering"], sim_stats["vol_clustering"])
    score_skew = safe_score(real_stats["skew"], sim_stats["skew"])

    fitness = (0.4 * score_kurt) + (0.4 * score_clust) + (0.2 * score_skew)

    trial.set_user_attr("sim_stats", sim_stats)
    trial.set_user_attr("real_stats", real_stats)
    trial.set_user_attr("fitness", fitness)
    trial.set_user_attr("params", params)
    return fitness


# ==============================================
# 7. EJECUCIÓN PRINCIPAL
# ==============================================
def run_real_calibration(n_trials: int = 30):
    print("\n" + "=" * 60)
    print("🧠 CALIBRACIÓN DEL MOTOR REAL (Hechos Estilizados)")
    print("   Modelo: MercadoEnjambre (engine/model.py)")
    print("=" * 60)

    real_stats = TARGET_STATS

    print("\n📊 Targets canónicos de mercado (objetivo de la calibración):")
    print(f"   Curtosis: {real_stats['kurtosis']:.3f}  → colas gordas (> 3)")
    print(f"   Clustering volatilidad: {real_stats['vol_clustering']:.3f}  → rachas (> 0.2)")
    print(f"   Asimetría: {real_stats['skew']:.3f}  → negativa = efecto pánico")

    study = optuna.create_study(direction="maximize",
                                sampler=optuna.samplers.TPESampler(seed=42))

    print(f"\n🚀 Iniciando optimización ({n_trials} trials)…")
    study.optimize(objective, n_trials=n_trials)

    best = study.best_params
    best_fitness = study.best_value
    best_stats = study.best_trial.user_attrs.get("sim_stats", {})

    print("\n" + "=" * 60)
    print("✅ CALIBRACIÓN COMPLETADA")
    print(f"Fitness máximo: {best_fitness:.4f}  (1.0 = réplica perfecta del benchmark)")
    print(f"\n📌 Parámetros óptimos:\n{json.dumps(best, indent=2)}")
    print("\n📊 Estadísticas del enjambre calibrado:")
    print(f"   Curtosis: {best_stats.get('kurtosis', 0):.3f}")
    print(f"   Clustering: {best_stats.get('vol_clustering', 0):.3f}")
    print(f"   Asimetría: {best_stats.get('skew', 0):.3f}")
    print("=" * 60)

    config = {
        "best_params": best,
        "best_fitness": best_fitness,
        "real_stats": real_stats,
        "sim_stats": best_stats,
        "n_trials": n_trials,
        "date": datetime.now().isoformat(),
        "modelo": "MercadoEnjambre",
        "ruta_config": str(RUTA_CONFIG),
    }
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "config_calibrada_real.json")
    with open(output_path, "w") as f:
        json.dump(config, f, indent=4)
    print(f"\n💾 Configuración guardada: {output_path}")
    return best, best_fitness


if __name__ == "__main__":
    run_real_calibration()
