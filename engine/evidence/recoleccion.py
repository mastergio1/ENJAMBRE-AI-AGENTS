"""Recolección de evidencia (Fase 1): ensambla el objeto de evidencia a partir de
los adaptadores de fuentes disponibles, respetando el contrato point-in-time.

Hoy conecta una fuente real: el contexto de precio previo (Yahoo). Las demás
(macro, consenso, noticias) se enchufan con la misma interfaz cuando estén sus
llaves/datos. Se usa en MODO SOMBRA: produce y guarda la evidencia sin alterar las
predicciones del enjambre."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from evidence import contrato
from evidence.fuentes import contexto_precio


def evidencia_para(simbolo, titular, as_of, *, event_id=None, mercado=None,
                   fetch_precio=None):
    """Construye el objeto de evidencia point-in-time para (simbolo, titular, as_of).

    BLINDADO: si una fuente falla, sigue con lo que haya; nunca lanza. Devuelve el
    objeto de evidencia validado (con su hash) — o uno mínimo (solo titular) si no
    hubo contexto. `fetch_precio` es inyectable para tests."""
    hechos, fuentes = [], []
    try:
        kw = {"fetch": fetch_precio} if fetch_precio else {}
        h, f = contexto_precio(simbolo, as_of, **kw)
        if h:
            hechos.extend(h)
        if f:
            fuentes.append(f)
    except Exception as e:
        print(f"[evidencia] contexto_precio falló para {simbolo}: {e!r}", flush=True)

    return contrato.construir_evidencia(
        event_id=event_id or f"{simbolo}:{as_of[:10]}",
        activo=simbolo, as_of=as_of, titular=titular, entity=None,
        hechos=hechos, fuentes=fuentes)
