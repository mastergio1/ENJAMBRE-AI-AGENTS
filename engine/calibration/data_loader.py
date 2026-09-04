"""Descarga el benchmark real (SPY) para la calibración offline.

Guarda en data/real_benchmark.csv el retorno logarítmico acumulado de SPY en
ventanas de 5 minutos. Herramienta de laboratorio: no la usa el motor.
"""

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

_SALIDA = os.path.join(os.path.dirname(__file__), "data", "real_benchmark.csv")


def download_spy_benchmark(days: int = 90, interval: str = "1m",
                           output_file: str = _SALIDA) -> pd.DataFrame:
    """Descarga SPY y calcula el log-retorno acumulado en ventanas de 5 min."""
    import yfinance as yf

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"Descargando SPY desde {start_date:%Y-%m-%d} hasta {end_date:%Y-%m-%d}…")
    df = yf.download("SPY", start=start_date, end=end_date,
                     interval=interval, progress=False)

    if df is None or df.empty:
        raise RuntimeError("No se pudieron descargar datos de SPY (¿límite de "
                           "Yahoo para intradía, o sin red?).")

    close = df["Close"]
    if hasattr(close, "columns"):          # yfinance a veces devuelve MultiIndex
        close = close.iloc[:, 0]
    df_resampled = close.resample("5min").last().dropna()

    log_returns = np.log(df_resampled / df_resampled.iloc[0])
    df_benchmark = pd.DataFrame({
        "timestamp": df_resampled.index,
        "close": df_resampled.values,
        "log_return_cum": log_returns.values,
    })

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_benchmark.to_csv(output_file, index=False)
    print(f"Guardado en {output_file}. Registros: {len(df_benchmark)}")
    return df_benchmark


if __name__ == "__main__":
    download_spy_benchmark()
