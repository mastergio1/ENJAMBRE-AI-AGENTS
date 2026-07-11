"""Disparador del ritual de la madrugada (lo corre el cron de Render).

El cron y la web son contenedores separados que NO comparten disco, así
que el cron no simula: solo golpea el endpoint protegido del servicio web,
y el ritual corre DENTRO del proceso web (misma base que sirve el muro).

Uso (cron): python -m contenido.disparar_pulso
Variables: ENJAMBRE_API_URL, ENJAMBRE_PIPELINE_TOKEN.
"""

import os
import sys

import httpx


def main() -> int:
    base = os.environ.get("ENJAMBRE_API_URL", "").rstrip("/")
    token = os.environ.get("ENJAMBRE_PIPELINE_TOKEN", "")
    if not base or not token:
        print("faltan ENJAMBRE_API_URL o ENJAMBRE_PIPELINE_TOKEN", file=sys.stderr)
        return 1
    try:
        respuesta = httpx.post(
            f"{base}/api/pipeline",
            headers={"X-Pipeline-Token": token},
            timeout=30,
        )
        print(f"disparo del pipeline → HTTP {respuesta.status_code}: {respuesta.text[:120]}")
        return 0 if respuesta.status_code < 300 else 1
    except Exception as error:
        print(f"no se pudo disparar el pipeline: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
