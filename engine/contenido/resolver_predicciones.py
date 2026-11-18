"""Resolvedor del registro prospectivo (Fase 7-mínima).

Para cada predicción aún sin resultado, intenta medir el movimiento REAL sin fuga
(desde el cierre posterior al `as_of` hacia adelante `horizonte` ruedas, con Yahoo)
y la resuelve. Si todavía no hay suficientes ruedas (la predicción no ha madurado),
la deja pendiente. Pensado para correr como job periódico (cron/Action).

Uso:
    python3 engine/contenido/resolver_predicciones.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from contenido import persistencia
from calibration.remedir_sin_fuga import obtener_barras, pct_sin_fuga

EVALUADOR_VER = "v1"


def resolver_pendientes(conexion, fetch=obtener_barras, zona: float = 0.3) -> dict:
    """Resuelve las predicciones maduras. Devuelve {resueltas, pendientes, sin_datos}.

    `fetch(simbolo, fecha) -> [(fecha_iso, cierre)]` es inyectable para tests."""
    pendientes = persistencia.predicciones_por_resolver(conexion)
    resueltas = sin_datos = aun_verdes = 0
    for pred in pendientes:
        fecha_base = pred["as_of_iso"][:10]  # YYYY-MM-DD
        barras = fetch(pred["simbolo"], fecha_base)
        if not barras:
            sin_datos += 1
            continue
        pct = pct_sin_fuga(barras, fecha_base, pred["horizonte"])
        if pct is None:
            aun_verdes += 1  # todavía no hay suficientes ruedas (no ha madurado)
            continue
        if persistencia.resolver_prediccion(conexion, pred["id"], pct,
                                             zona=zona, evaluador_ver=EVALUADOR_VER):
            resueltas += 1
    return {"resueltas": resueltas, "sin_datos": sin_datos, "aun_verdes": aun_verdes,
            "total_pendientes": len(pendientes)}


def main():
    conexion = persistencia.conectar()
    res = resolver_pendientes(conexion)
    print(f"resueltas: {res['resueltas']} | aún verdes: {res['aun_verdes']} | "
          f"sin datos: {res['sin_datos']} | total pendientes: {res['total_pendientes']}")
    print("tablero:", persistencia.resumen_predicciones(conexion))
    print("tablero índice:", persistencia.resumen_predicciones(conexion, "indice"))


if __name__ == "__main__":
    main()
