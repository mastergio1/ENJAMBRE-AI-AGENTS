# Guía de operación — capa de contenido

> Para Giorgio. Qué existe de la capa de contenido, cómo se opera y qué
> falta. Se actualiza al cierre de cada etapa (6-10 de `CONTENIDO.md`).

## Qué existe hoy (Etapas 6, 7, 8 y 9 completadas)

| Pieza | Qué hace |
|---|---|
| **La memoria** (`contenido/persistencia.py`) | Toda simulación que corre el motor queda guardada para siempre en la base (`engine/datos/enjambre.db`): titular, reporte, las 100 voces y la curva de precios. Es el cimiento del archivo histórico. |
| **El portero** (`contenido/portero.py`) | Filtra los titulares del día en dos pisos: primero descarta gratis lo obvio (duplicados, publicidad, listas), luego puntúa el impacto 1-10 (con Haiku si hay clave de API; con reglas si no) y elige los 3 del día. Todo veredicto queda registrado. |
| **La fuente** (`contenido/fuentes/alpaca.py`) | Trae los titulares reales de las últimas 18 h desde Alpaca. Sin claves, usa un día de demostración — nada se cae. |
| **El filtro CMF** (`contenido/vocabulario.py`) | La lista de términos prohibidos y el disclaimer oficial, como código con tests. Nada se publica sin pasar por aquí. Ya pescó y corrigió dos frases del propio producto. |
| **El muro** (`web/src/muro/` + endpoints `/api/*`) | La nueva portada: tarjetas del día con las 3 destacadas ya simuladas (replay 3D en loop detrás), botón "Ver reacción del enjambre" para las pendientes (corre en vivo y queda cacheada para todos), y las descartadas no aparecen. |
| **Los frenos** (`contenido/limites.py`) | 5 simulaciones/hora por visitante y tope global diario (`ENJAMBRE_MAX_SIM_DIA`, defecto 20). Al agotarse, el muro invita a suscribirse al Pulso. |
| **El ritual completo** (`contenido/pipeline.py`) | Los 8 pasos de la madrugada: recolectar → portero → simular las 3 → capturar imagen → redactar correo → enviar → publicar → avisar a Giorgio. `python -m contenido.pipeline` arma todo; `--enviar` manda los correos. |
| **El Pulso** (`contenido/boletin.py`) | El correo diario (HTML de tablas inline, oscuro con dorado) por Resend. Todos los textos variables pasan por el filtro CMF; lleva el disclaimer y el link de baja de un clic. Sin `RESEND_API_KEY`, arma el HTML pero no envía. |
| **La imagen** (`contenido/captura.py`) | El "momento dramático" 1200×630 (Pillow): titular, dirección, agitación, la curva con el tick de máxima caída marcado, disclaimer y marca de agua. Sirve de portada del correo y de Open Graph. Endpoint: `/api/simulacion/{id}/imagen`. |
| **Suscripción double opt-in** | Formulario en el muro → `/api/suscribir` (nace pendiente) → correo de confirmación → `/api/confirmar/{token}` (activo) → `/api/baja/{token}` (un clic). La lista vive en SQLite: los leads son del negocio. |
| **El cron** (`contenido/disparar_pulso.py`) | El cron de Render (6:30 AM Chile, L-V) golpea `/api/pipeline` (protegido por token) y el ritual corre dentro del proceso web, sobre la misma base que sirve el muro. |
| **El archivo** (`web/src/archivo/` + `/api/archivo`) | La hemeroteca "El Enjambre dijo": destacadas navegables por mes, buscables por titular y filtrables por ticker. Cada una con URL propia (`?sim=<id>`), su reporte con las **8 voces** por arquetipo, y el campo **"¿y qué pasó después?"** (epílogo). |

### Cómo escribir el "¿y qué pasó después?" de una simulación

Es manual y protegido (solo tú). Con el token de admin (`ENJAMBRE_PIPELINE_TOKEN`):

```bash
curl -X POST https://<motor>/api/epilogo/<sim_id> \
  -H "X-Pipeline-Token: <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{"texto":"El IPSA cerró -1,2% ese día."}'
```

Aparece en la página de la simulación bajo "Comparación educativa" — nunca
como "acierto" ni "predicción". El filtro CMF rechaza vocabulario prohibido.

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

## Para encender El Pulso (Etapa 8) en producción

1. Cuenta en **resend.com** + verificar un **dominio** (SPF/DKIM) — sin
   dominio propio el correo cae a spam. Pegar `RESEND_API_KEY` y ajustar
   `PULSO_REMITENTE` en Render.
2. El cron `enjambre-pulso` ya está en `render.yaml` (6:30 AM Chile, L-V).
   Copiar el `ENJAMBRE_PIPELINE_TOKEN` que Render genera en el servicio web
   y pegarlo igual en el cron.
3. (Opcional) Bot de Telegram: `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`
   para recibir el resumen de cada corrida.

Probar sin enviar: `python -m contenido.pipeline` (arma el correo y lo deja
en `html_preview`). Con `--enviar` manda de verdad.

## Qué sigue (en orden)

- **Etapa 10 — Duelo + widget** (el comparador con export vertical + el
  build embebible para medios).
