# Guía de operación — capa de contenido

> Para Giorgio. Qué existe de la capa de contenido, cómo se opera y qué
> falta. Se actualiza al cierre de cada etapa (6-10 de `CONTENIDO.md`).

## Qué existe hoy (Etapa 6 completada)

| Pieza | Qué hace |
|---|---|
| **La memoria** (`contenido/persistencia.py`) | Toda simulación que corre el motor queda guardada para siempre en la base (`engine/datos/enjambre.db`): titular, reporte, las 100 voces y la curva de precios. Es el cimiento del archivo histórico. |
| **El portero** (`contenido/portero.py`) | Filtra los titulares del día en dos pisos: primero descarta gratis lo obvio (duplicados, publicidad, listas), luego puntúa el impacto 1-10 (con Haiku si hay clave de API; con reglas si no) y elige los 3 del día. Todo veredicto queda registrado. |
| **La fuente** (`contenido/fuentes/alpaca.py`) | Trae los titulares reales de las últimas 18 h desde Alpaca. Sin claves, usa un día de demostración — nada se cae. |
| **El filtro CMF** (`contenido/vocabulario.py`) | La lista de términos prohibidos y el disclaimer oficial, como código con tests. Nada se publica sin pasar por aquí. Ya pescó y corrigió dos frases del propio producto. |

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

- **Etapa 7 — El muro:** la nueva portada con los titulares del día.
- **Etapa 8 — El Pulso:** el pipeline de madrugada + la newsletter (ahí se
  decide cron de Render vs GitHub Action, y se necesita cuenta de Resend
  + dominio verificado).
- **Etapa 9 — El archivo** · **Etapa 10 — Duelo + widget.**
