# Guía de operación — capa de contenido

> Para Giorgio. Qué existe de la capa de contenido, cómo se opera y qué
> falta. Se actualiza al cierre de cada etapa (6-10 de `CONTENIDO.md`).

## Qué existe hoy (Etapas 6 y 7 completadas)

| Pieza | Qué hace |
|---|---|
| **La memoria** (`contenido/persistencia.py`) | Toda simulación que corre el motor queda guardada para siempre en la base (`engine/datos/enjambre.db`): titular, reporte, las 100 voces y la curva de precios. Es el cimiento del archivo histórico. |
| **El portero** (`contenido/portero.py`) | Filtra los titulares del día en dos pisos: primero descarta gratis lo obvio (duplicados, publicidad, listas), luego puntúa el impacto 1-10 (con Haiku si hay clave de API; con reglas si no) y elige los 3 del día. Todo veredicto queda registrado. |
| **La fuente** (`contenido/fuentes/alpaca.py`) | Trae los titulares reales de las últimas 18 h desde Alpaca. Sin claves, usa un día de demostración — nada se cae. |
| **El filtro CMF** (`contenido/vocabulario.py`) | La lista de términos prohibidos y el disclaimer oficial, como código con tests. Nada se publica sin pasar por aquí. Ya pescó y corrigió dos frases del propio producto. |
| **El muro** (`web/src/muro/` + endpoints `/api/*`) | La nueva portada: tarjetas del día con las 3 destacadas ya simuladas (replay 3D en loop detrás), botón "Ver reacción del enjambre" para las pendientes (corre en vivo y queda cacheada para todos), y las descartadas no aparecen. |
| **Los frenos** (`contenido/limites.py`) | 5 simulaciones/hora por visitante y tope global diario (`ENJAMBRE_MAX_SIM_DIA`, defecto 20). Al agotarse, el muro invita a suscribirse al Pulso. |
| **El ritual (parcial)** (`contenido/pipeline.py`) | Los pasos 1-3 y 7 de la madrugada: recolectar → portero → simular las 3 con seeds del día → publicar como destacadas con su replay. Correr a mano: `python -m contenido.pipeline`. Los pasos de correo llegan en la Etapa 8. |

## Cómo revisar el log de veredictos del portero

```bash
cd engine && source .venv/bin/activate
python probar_portero.py
```

Muestra cada titular con su impacto, veredicto y motivo, y los 3 elegidos.
Con claves de Alpaca procesa los titulares reales del día.

## Las claves que activan lo real (van en el entorno, JAMÁS en el repo)

| Variable | Para qué | Dónde conseguirla |
|---|---|---|
| `ALPACA_API_KEY_ID` y `ALPACA_API_SECRET_KEY` | titulares reales | cuenta gratis en alpaca.markets |
| `ANTHROPIC_API_KEY` | cerebros LLM + portero Haiku | console.anthropic.com |

En local: archivo `engine/.env` (ver `.env.example`). En Render: panel →
Environment. **Importante para Render:** agregar un disco persistente
montado en `/app/datos` para que la base sobreviva a los reinicios.

## Qué sigue (en orden)

- **Etapa 8 — El Pulso:** completar el pipeline (captura del momento
  dramático, plantilla de correo, Resend, double opt-in, aviso a Telegram)
  + el cron (ahí se decide worker de Render vs GitHub Action; se necesita
  cuenta de Resend + dominio verificado).
- **Etapa 9 — El archivo** · **Etapa 10 — Duelo + widget.**
