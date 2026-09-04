"""Laboratorio de calibración offline (Optuna) — modelo de agente de juguete.

⚠️ QUÉ ES Y QUÉ NO ES (léelo antes de creerle a un número):
- Corre un modelo de agente REDUCIDO (HeadlessAgent: alpha/beta/gamma), NO el
  motor real de El Enjambre (Mesa + libro de órdenes + 12 tipos + líderes LLM).
  Calibrar este juguete NO calibra el motor real.
- El "benchmark" es la ruta concreta de SPY, pero las noticias que alimentan la
  simulación son RUIDO sintético (aleatorio). Ajustar 3 parámetros para que una
  salida movida por ruido se parezca a la ruta de SPY es CURVE-FITTING: un R²
  alto aquí NO significa que el simulador prediga el mercado. Es un banco de
  pruebas del andamiaje, no una validación de realismo.
- La validación de realismo del proyecto vive en engine/validation/ (hechos
  estilizados: colas gordas, clustering de volatilidad, etc.), que es el camino
  correcto para calibrar el motor real (ver README de esta carpeta).

Sirve para: probar el flujo Optuna, medir tiempos, y como esqueleto para migrar
luego a una calibración honesta contra los hechos estilizados.
"""

import json
import os
import sys
from typing import List

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NUM_AGENTS = 2000   # 2000 para pruebas rápidas; 10000 para la corrida "final"
NUM_STEPS = 200     # pasos de simulación (1 paso ≈ 1 minuto)

_BENCHMARK = os.path.join(os.path.dirname(__file__), "data", "real_benchmark.csv")


class HeadlessAgent:
    """Agente de juguete para correr offline, sin servidor ni websockets."""

    def __init__(self, alpha: float, beta: float, gamma: float):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.memory_trace = 0.0
        self.position = 0.0
        self.neighbors: list = []

    def step(self, news_impact: float = 0.0) -> float:
        self.memory_trace *= self.gamma
        self.memory_trace += news_impact * self.alpha
        if self.neighbors:
            avg_neigh = np.mean([n.memory_trace for n in self.neighbors])
        else:
            avg_neigh = 0.0
        final_decision = (self.memory_trace * (1 - self.beta)) + (avg_neigh * self.beta)
        self.position += final_decision * 0.01
        self.position = float(np.clip(self.position, -1.0, 1.0))
        return self.position


def run_headless_simulation(alpha: float, beta: float, gamma: float) -> List[float]:
    """Simulación sin frontend. Devuelve log-retornos acumulados sintéticos."""
    agents = [HeadlessAgent(alpha, beta, gamma) for _ in range(NUM_AGENTS)]

    # red de influencia de juguete: 5 vecinos aleatorios por agente
    for agent in agents:
        agent.neighbors = list(np.random.choice(agents, size=5, replace=False))

    # flujo de noticias SINTÉTICO (ruido + shocks) — semilla fija para repetir
    np.random.seed(42)
    news_stream = []
    for _ in range(NUM_STEPS):
        if np.random.rand() < 0.2:
            news_stream.append(np.random.normal(0, 0.5))    # shock fuerte
        else:
            news_stream.append(np.random.normal(0, 0.05))   # ruido normal

    price_evolution = [0.0]
    for step_idx in range(NUM_STEPS):
        impacto = news_stream[step_idx]
        for agent in agents:
            agent.step(news_impact=impacto)
        avg_position = np.mean([a.position for a in agents])
        price_evolution.append(price_evolution[-1] + (avg_position * 0.02))

    return price_evolution[1:]


def load_real_benchmark() -> np.ndarray:
    """Carga el SPY real descargado por data_loader.py."""
    if not os.path.exists(_BENCHMARK):
        raise FileNotFoundError(
            f"Ejecuta primero data_loader.py. No se encuentra {_BENCHMARK}")
    import pandas as pd

    df = pd.read_csv(_BENCHMARK)
    real = df["log_return_cum"].values[:NUM_STEPS]
    if len(real) < NUM_STEPS:
        real = np.pad(real, (0, NUM_STEPS - len(real)), constant_values=real[-1])
    return real[:NUM_STEPS]


def objective(trial):
    from sklearn.metrics import r2_score

    alpha = trial.suggest_float("alpha", 0.2, 0.9)
    beta = trial.suggest_float("beta", 0.1, 0.8)
    gamma = trial.suggest_float("gamma", 0.7, 0.99)

    sim = run_headless_simulation(alpha, beta, gamma)
    real = load_real_benchmark()

    n = min(len(sim), len(real))
    sim, real = np.asarray(sim[:n]), np.asarray(real[:n])
    try:
        return float(r2_score(real, sim))
    except Exception:
        return -10.0


def run_calibration(n_trials: int = 100):
    import optuna

    print("=== CALIBRACIÓN OFFLINE (Optuna) — modelo de juguete ===")
    print(f"Agentes: {NUM_AGENTS} | Pasos: {NUM_STEPS} | Trials: {n_trials}")

    study = optuna.create_study(direction="maximize",
                                sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials)

    salida = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "config_calibrada.json")
    with open(salida, "w") as f:
        json.dump({
            "best_params": study.best_params,
            "best_r2": study.best_value,
            "n_agents": NUM_AGENTS,
            "n_steps": NUM_STEPS,
            "aviso": "R² de un modelo de juguete vs ruido sintético; NO es "
                     "correlación real con el mercado. Ver README.",
        }, f, indent=4)

    print("\n" + "=" * 50)
    print("✅ CALIBRACIÓN (juguete) COMPLETADA")
    print(f"Mejor R²: {study.best_value:.4f}  (curve-fit, no realismo — ver README)")
    print(f"Parámetros: {study.best_params}")
    print(f"Guardado en: {salida}")
    print("=" * 50)
    return study.best_params, study.best_value


if __name__ == "__main__":
    if not os.path.exists(_BENCHMARK):
        print("⚠️ Sin benchmark. Ejecutando data_loader.py…")
        from calibration import data_loader
        data_loader.download_spy_benchmark()
    run_calibration()
