"""Exporta la libreta cruda (señal del enjambre + resultado real) para calibrar.

Correr EN RENDER, desde la carpeta engine/:

    python -m contenido.exportar_libreta > libreta_export.json

Devuelve una lista JSON con una fila por caso ya corregido (con resultado real),
sin IA de respaldo. Cada fila: la señal continua del enjambre y cuánto se movió
el símbolo de verdad. Es lo único que la calibración necesita, y NO contiene datos
de Kalshi/Polymarket — es nuestra propia libreta (movimientos vía Alpaca).

Seguro: solo LEE la base; no escribe nada. No imprime emails ni secretos.
"""

import json
import sys

from contenido import persistencia


def exportar(conexion=None) -> list[dict]:
    propia = conexion is None
    conexion = conexion or persistencia.conectar()
    try:
        filas = conexion.execute(
            "SELECT resumen_json, reaccion_real, fuente FROM simulaciones "
            "WHERE reaccion_real IS NOT NULL AND (destacada = 1 OR fuente = 'backtest')"
        ).fetchall()
    finally:
        if propia:
            conexion.close()

    casos = []
    for fila in filas:
        reaccion = json.loads(fila["reaccion_real"])
        if reaccion.get("cerebros") == "respaldo":
            continue  # simulado sin IA real: no califica
        resumen = json.loads(fila["resumen_json"])
        casos.append({
            "direccion_pct": resumen.get("direccion_pct"),
            "senal_media_lideres": resumen.get("senal_media_lideres"),
            "senal_media_ponderada": resumen.get("senal_media_ponderada"),
            "confianza": resumen.get("confianza"),
            "pct_real": reaccion.get("pct_real"),
            "categoria": reaccion.get("categoria"),
            "fuente": fila["fuente"],
        })
    return casos


if __name__ == "__main__":
    casos = exportar()
    json.dump(casos, sys.stdout, ensure_ascii=False)
    print(f"\n# {len(casos)} casos exportados", file=sys.stderr)
