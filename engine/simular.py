"""Corre una sesión de mercado y reporta los hechos estilizados.

Uso: python simular.py [seed]
Herramienta de calibración de la Etapa 1 — no es parte del producto.
"""

import sys
import time

from model import MercadoEnjambre
from validation.hechos_estilizados import asimetria_panico, autocorrelacion, curtosis


def sesion_con_noticias(seed: int, ticks: int = 600) -> MercadoEnjambre:
    """Una sesión con flujo de noticias aleatorias (como un día real)."""
    modelo = MercadoEnjambre(seed=seed, ticks_horizonte=ticks)
    for _ in range(ticks):
        if modelo.random.random() < 0.02:  # llega una noticia al mercado
            modelo.aplicar_noticia(modelo.random.gauss(0, 0.45))
        modelo.step()
    return modelo


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    inicio = time.time()
    modelo = sesion_con_noticias(seed)
    duracion = time.time() - inicio

    r = modelo.retornos
    absolutos = [abs(x) for x in r]
    print(f"seed={seed} · {len(r)} ticks en {duracion:.1f}s")
    print(f"precio final: {modelo.historial_precios[-1]:.2f} (partió en 100)")
    print(f"1. curtosis:            {curtosis(r):.2f}  (real si > 3)")
    print(f"2. AC |r| rezago 1:     {autocorrelacion(absolutos, 1):.3f}  (real si > 0 y decae)")
    print(f"   AC |r| rezago 5:     {autocorrelacion(absolutos, 5):.3f}")
    print(f"   AC |r| rezago 10:    {autocorrelacion(absolutos, 10):.3f}")
    print(f"3. AC retornos rez. 1:  {autocorrelacion(r, 1):.3f}  (real si ≈ 0)")
    print(f"4. asimetría de pánico: {asimetria_panico(r):.2f}  (real si > 1)")

    total = sum(modelo.flujo_compras) + sum(modelo.flujo_ventas)
    print(f"volumen total sesión:   {total:,.0f} acciones")
