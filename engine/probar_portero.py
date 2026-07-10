"""Corre el portero sobre los titulares del día y muestra el log de veredictos.

Uso: python probar_portero.py
Con claves de Alpaca en el entorno usa titulares reales de las últimas 18 h;
sin claves usa el día de demostración. Todo veredicto queda en la base.
"""

from contenido import persistencia, portero
from contenido.fuentes import alpaca

if __name__ == "__main__":
    titulares, origen = alpaca.obtener_titulares(horas=18, limite=50)
    print(f"fuente de titulares: {origen} ({len(titulares)} recibidos)\n")

    conexion = persistencia.conectar()
    resultado = portero.procesar_dia(conexion, titulares, maximo=3)
    conexion.close()

    print(f"{'imp':>3}  {'veredicto':9}  titular")
    print("-" * 100)
    for entrada in sorted(resultado["log"], key=lambda e: -e["impacto"]):
        print(f"{entrada['impacto']:>3}  {entrada['veredicto']:9}  {entrada['titular'][:70]}")
        print(f"{'':>16}└ {entrada['motivo'][:80]}")

    print(f"\nELEGIDOS DEL DÍA ({len(resultado['elegidos'])}):")
    for elegido in resultado["elegidos"]:
        print(f"  ★ [{elegido['impacto']}/10] {elegido['titular']}")
