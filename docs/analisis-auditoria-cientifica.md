# Análisis en frío de la Auditoría Científica + plan de acción

*Rubicón Lab · El Enjambre · 2026-11-24. Análisis de `docs/auditoria-cientifica.md`
(la auditoría más rigurosa recibida) contrastado contra el código REAL, y qué
hacemos. Propósito del proyecto: **comprobar o descartar científicamente** que el
enjambre aporta ventaja predictiva. El resultado negativo también es un hallazgo.*

## 1. Veredicto: la auditoría es correcta

Verifiqué sus cuatro hallazgos P0 "reproducidos" contra el código. **Los cuatro son
ciertos** (y dos muestran que mis correcciones v4 quedaron incompletas):

| ID | Afirmación | ¿Cierto? | Estado v4 |
|---|---|---|---|
| F01 | `walk_forward.cargar` usa `pct_real` (etiqueta contaminada) | ✅ | no tocado en v4 |
| F02 | A0 cuenta etiquetas del MISMO día (no maduradas) | ✅ | v4 arregló orden, no maduración |
| F03 | `construir_evidencia` no valida `event_timestamp` vs `as_of` | ✅ | no tocado en v4 |
| F04 | `particionar` ignora el embargo del manifiesto | ✅ | v4 tapó futuras, no el embargo |

La auditoría también encuadra bien la ciencia: las **cuatro hipótesis** (lenguaje →
señal; ensemble > 1 cerebro; ABM incremental; valor neto tras costes) son
independientes, y la prueba decisiva es **prospectiva**, no un backtest.

## 2. Lo que YA corregí (Fase 0 — integridad, sin clave; con tests)

- **F01** — `walk_forward.cargar` ahora prefiere `pct_corr` (sin fuga) y **rehúsa**
  `pct_real` no certificada por defecto (opt-in explícito para legacy). +test.
- **F02** — `_items_a0` madura etiquetas: los casos del **mismo día** se predicen con
  la historia previa y esta se actualiza al **cerrar el día** (no se informan entre
  sí). +test.
- **F03** — `construir_evidencia` **rechaza** un `event_timestamp` posterior al
  `as_of` (un hecho observado no viene del futuro; un evento programado va como
  `scheduled_at`). +test.
- **F04** — `particionar` aplica el **mismo embargo** que `construir_manifiesto`; el
  tamaño de desarrollo coincide con lo declarado. +test.

Quedan como P0 más grandes (necesitan datos/calendario, no la clave): **F05**
(cosecha sesgada por el movimiento → construir un banco cronológico de flujo) y
**F06** (horizonte intradía con calendario por bolsa).

## 3. El programa de investigación que adoptamos

La auditoría define un **torneo de modelos** M0–M13 cuya comparación primaria es:

> **M13 (contexto + consenso + features del ABM) vs M13-null (idéntico, SIN features
> del ABM).** Mismos eventos, misma información, mismo presupuesto. Diferencia
> **pareada** por evento (Brier), con holdout sellado y, al final, **cohorte
> prospectiva**.

Comparaciones críticas secundarias: **M4** (un LLM solo) vs **A3** (consenso de 110)
— ¿la diversidad compra algo? — y **M7 (A4, ABM) vs A3** — ¿el precio simulado supera
al consenso? (hoy, históricamente, NO: lo resta).

### Qué necesita cada cosa
- **Sin clave, ya hecho:** Fase 0 integridad (F01–F04), inferencia pareada, A0 honesto.
- **Necesita la clave (`ANTHROPIC_API_KEY`):** A2/M4 (un LLM), M5/M6 (ensembles),
  features del ABM con respuestas congeladas, evidencia B-vs-D.
- **Necesita datos excluidos del volcado** (SQLite/JSON): recalcular tasas, banco
  cronológico de flujo (F05), microestructura.
- **Necesita tiempo:** la cohorte **prospectiva** sellada (la única prueba limpia).

## 4. Mi opinión fuerte (dónde acelerar y dónde frenar)

- **Acelerar:** integridad (hecho), el torneo M4/M6/M13-vs-M13-null, y sobre todo
  **acumular casos prospectivos** (el ritual auto-sanador ya lo sostiene).
- **Frenar (regla 5 de la biblia — simplicidad):** NO construir todavía el paquete
  `predictor/` completo, los 12 especialistas, Monte Carlo masivo ni barridos de
  50k–100k agentes. Eso se construye **si** aparece señal que lo justifique. El barrido
  de población (N) y el metamodelo son la fase media, no la primera.
- **La ventaja competitiva, si existe, probablemente NO está en "más agentes".** La
  propia auditoría lo dice: puede estar en los datos point-in-time, la memoria de
  eventos, la calibración y la especialización — no en el tamaño del enjambre.

## 5. Siguiente paso concreto

Con la Fase 0 cerrada, el próximo movimiento de mayor valor que **no** necesita tu
clave es preparar el **banco cronológico de flujo (F05)**: un dataset de eventos
seleccionados por reglas *ex ante* (no por el movimiento posterior), que es el
universo honesto para medir predicción. En cuanto cargues `ANTHROPIC_API_KEY`
(+ rotar el token), corremos **M4 vs A3** y luego **M13 vs M13-null**.
