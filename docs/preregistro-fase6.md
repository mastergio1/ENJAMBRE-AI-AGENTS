# Pre-registro — Experimento prospectivo confirmatorio (Fase 6)

> **Congelado el 2026-11-24, ANTES de ver resultados prospectivos.** Este documento
> fija las reglas de la única prueba limpia del proyecto: predicciones selladas antes
> de conocer el desenlace, resueltas sin fuga cuando maduran. No se cambia la
> hipótesis, la métrica ni la muestra después de mirar los resultados (regla de oro).

## 1. Por qué este experimento

Toda la evidencia **histórica** (7 análisis, `docs/hallazgo-*.md`) apunta a que el
enjambre NO aporta valor predictivo sobre una sola lectura de IA del titular, y que la
señal que existe es débil y solo en índices. El histórico está sesgado (selección por
movimiento, posible memoria del LLM). **La prueba decisiva es prospectiva.** Este
pre-registro la define para que su resultado sea creíble, salga como salga. **El
resultado negativo es un hallazgo válido.**

## 2. Hipótesis primaria

> En **eventos macro de EE. UU.** con instrumento primario **SPY** (réplica QQQ, DIA,
> IWM), el **predictor calibrado del consenso** (`predictor_calibrado.py`, versión
> congelada) reduce la **pérdida de Brier** de la probabilidad de subida frente al
> **mejor baseline predefinido**, en predicciones **selladas antes del desenlace**.

Hipótesis nula: no reduce el Brier (o lo aumenta).

## 3. Lo que queda CONGELADO (no se toca tras ver datos)

| Elemento | Valor congelado |
|---|---|
| Instrumento primario | SPY (secundarios correlacionados: QQQ, DIA, IWM) |
| Universo | eventos de índice sellados por el ritual (ver §6: falta activar índice) |
| Horizonte | **2 sesiones** de bolsa desde la primera rueda ejecutable tras el sellado |
| Entrada / salida | cierre de la 1ª rueda posterior a `as_of` → cierre +2 ruedas |
| Predictor | consenso calibrado (Platt sobre `senal`), congelado; dirección y `probabilidad` |
| Política de decisión | abstención por gating: se puntúa aparte "todas" vs "solo fiables" |
| Baseline(s) | clase mayoritaria train-only ("los índices suben"), momentum, y A2 (1 LLM) |
| Métrica primaria | **ganancia de Brier pareada por evento** (modelo − baseline) |
| Métrica secundaria | acierto direccional a **igual cobertura**; ECE; curva riesgo-cobertura |
| Dependencia | unidad = evento canónico (mismo día); cluster bootstrap por evento |
| Efecto mínimo relevante | `delta_min` = 0.005 de Brier (continuidad con el margen del walk-forward) |
| Comparaciones múltiples | jerárquico: SPY primario; el resto, secundario (Holm/FDR) |
| Regla de parada | evaluar cuando haya **≥ 100 eventos de índice resueltos**, o a los **6 meses**, lo que ocurra primero. Sin optional stopping intermedio. |

## 4. Veredicto (decidido de antemano)

- **Superioridad** solo si la ganancia de Brier supera `delta_min` y su IC (dependencia
  por evento) lo respalda.
- **Inferioridad / equivalencia** según el IC.
- **Inconcluso** si el IC es ancho (falta potencia): se informa "inconcluso", nunca
  "probado". Ausencia de evidencia ≠ evidencia de ausencia.
- Si se confirma superioridad, recién ahí tiene sentido hablar de un producto predictor
  (con paper trading neto antes de cualquier capital real; ver auditoría §11.6).

## 5. Estado actual de la cohorte (2026-11-24, informativo, NO evaluable)

- 15 predicciones selladas · 6 resueltas · acierto 33 % (n=6, **sin valor estadístico**).
- **Todas son de ACCIONES individuales; 0 de índice.** Cobertura de evidencia 40 %.

## 6. Acción pendiente CRÍTICA para que este experimento sea válido

El ritual diario sella las **destacadas** (movers de noticias), que son casi siempre
**acciones individuales** — justo el mercado donde el histórico da ~azar. **Para probar
la hipótesis primaria (índice) hay que sellar también una predicción diaria de ÍNDICE**
(SPY/QQQ/DIA/IWM) basada en el titular macro del día. Sin eso, la cohorte prospectiva
nunca tendrá eventos de índice y la hipótesis primaria queda sin datos. *(Diseño:
añadir al ritual un sellado diario de índice; decisión de producto de Giorgio.)*

## 7. Qué queda "terminado" de la Fase 6

- ✅ Registro prospectivo inmutable (`predicciones`) + resolución sin fuga.
- ✅ Ritual auto-sanador que lo alimenta a diario.
- ✅ Predictor calibrado + curva riesgo-cobertura (Fase 5).
- ✅ Evaluador prospectivo (`evaluar_prospectivo.py`) listo para correr al madurar.
- ✅ Este pre-registro congelado.
- ⏳ Falta solo: **tiempo** (que maduren ≥100 eventos) y **activar el sellado de índice**.
