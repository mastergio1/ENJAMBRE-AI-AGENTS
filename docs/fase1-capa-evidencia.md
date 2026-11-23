# Fase 1 — Capa de evidencia point-in-time (cimiento)

*Rubicón Lab · El Enjambre · 2026-11-23. Primer incremento de la Fase 1, la palanca
que el hallazgo de baselines señaló como la real: si el titular pelado solo supera
al momentum por ~3 puntos, el camino es darle al enjambre MEJOR información, no más
agentes. Módulo `engine/evidence/` (con 11 tests). Sin IA, en modo sombra.*

## Qué se construyó (offline, testeado)

Un **contrato de evidencia** con su guardia de integridad temporal — el cimiento
sobre el que se apoya todo lo demás de la Fase 1:

- **Esquema** (`construir_evidencia`): objeto versionado con `event_id`, `asset`,
  `as_of_timestamp`, hechos, expectativas, información nueva, "¿ya estaba
  descontado?", fuentes (con su fecha), contradicciones, incertidumbres,
  información faltante y `evidence_hash`.
- **Guardia temporal (la regla sagrada):** NADA posterior al `as_of` puede entrar.
  Una fuente publicada después del evento, o una expectativa con vintage posterior,
  se **rechaza** — eso sería ver el futuro (la fuga que arruina un backtest).
  También se rechaza una fuente sin fecha fiable.
- **Hash estable:** mismo contenido → mismo `evidence_hash` (reproducibilidad).
- **Ensamblador de modo sombra:** produce la evidencia sin tocar todavía las
  predicciones del enjambre.
- **Formateador para el cerebro:** convierte la evidencia en el bloque de texto que
  leería el LLM. Es el puente del experimento **B (solo titular) vs D (titular +
  evidencia)**: el brazo B recibe solo el titular; el D, el titular + el contexto
  validado.

## Lo que falta (necesita Render/datos/IA)

Esto es el **contrato y la validación**, no la recuperación real. Lo siguiente:

1. **Adaptadores de recuperación** point-in-time: calendario macro (CPI/FOMC),
   consenso previo, precios/volatilidad anteriores, noticias oficiales — cada una
   con su `published_at`/`vintage`. Corren contra APIs (Alpaca/Barchart/macro) en
   Render. El contrato ya los obliga a respetar el `as_of`.
2. **Experimento B vs D:** correr los mismos cerebros con y sin el bloque de
   evidencia, sobre los mismos eventos, y medir si D le gana a B fuera de muestra.
   Necesita IA (Render).

## Gate de la fase (de la auditoría v3)

La capa de evidencia se promueve **solo si mejora métricas fuera de muestra**, no
por mejor narrativa ni explicaciones más convincentes. Hasta entonces, vive en modo
sombra: se produce y se audita, pero no cambia lo que ve el enjambre.
