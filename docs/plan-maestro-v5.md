# El Enjambre — Plan maestro v5 (científico)

> **RECTOR desde 2026-11-24.** Supersede a v4/v3. Síntesis ejecutable de
> `docs/auditoria-cientifica.md`, adaptada a nuestra realidad (qué necesita clave,
> datos o tiempo) y a la regla 5 de la biblia (simplicidad: no construir la catedral
> antes de probar la tesis).

## Estrella polar

**Comprobar o descartar, sin autoengaño, que El Enjambre aporta ventaja predictiva
incremental, robusta y económicamente útil.** El resultado negativo es un hallazgo
válido. No se presupone que 10.150 agentes, el ABM ni ningún arquetipo deban
mantenerse: cada pieza se juzga con evidencia.

## Las 4 hipótesis (independientes)

1. **H1** — el lenguaje de una noticia contiene señal sobre el retorno futuro.
2. **H2** — un conjunto de cerebros heterogéneos supera a UN solo cerebro (igual info).
3. **H3** — la simulación ABM aporta señal incremental sobre el consenso + contexto.
4. **H4** — la señal sobrevive a costes, latencia y riesgo (valor neto).

Probar una no prueba las otras.

## El torneo de modelos (la comparación)

| ID | Modelo | Pregunta |
|---|---|---|
| M0 | tasa base / siempre alcista / 50-50 | ¿hay señal sobre deriva y azar? |
| M1 | momentum/reversión/volatilidad | ¿supera reglas simples? |
| M2 | léxico del titular | ¿el LLM supera el diccionario? |
| M3 | logística de features financieras | ¿texto/ABM añaden a lo numérico? |
| **M4** | **un LLM neutral, titular-only** | **¿los 110 cerebros mejoran sobre 1?** |
| M5 | un LLM con evidencia contextual | ¿ensemble supera un cerebro bien informado? |
| M6 | ensemble de cerebros independientes | ¿la diversidad agrega señal? |
| M7 | ABM legacy (= A4) | ¿el precio simulado supera al consenso? |
| **M13** | **contexto + consenso + features ABM** | **la comparación primaria…** |
| **M13-null** | **idéntico, SIN features ABM** | **…¿el ABM aporta algo?** |

**Comparación primaria:** M13 vs M13-null (mismos eventos, misma info, mismo
presupuesto, diferencia **pareada por evento**, holdout sellado, y al final cohorte
**prospectiva**). Secundarias críticas: **M4 vs A3** (consenso) y **M7 vs A3**.

## Fases (gates, no fechas)

| Fase | Qué | Estado |
|---|---|---|
| **0 · Integridad** | contrato temporal, etiquetas maduras, embargo, evidencia PIT | **F01–F04 ✅ hechas** · F05/F06 pendientes |
| 1 · Origen de la señal | A0–A4 + M0–M7 sobre los mismos eventos | parcial (ablación ✅; M4 necesita clave) |
| 2 · Escala y semillas | barrido N/B con capital constante, frontera de Pareto | pendiente |
| 3 · Inteligencia colectiva | correlación de errores, topologías, deliberación, arquetipos | pendiente |
| 4 · Condicionar al mercado | evidencia real previa, memoria, microestructura | evidencia en sombra ✅; resto pendiente |
| 5 · Predictor calibrado | metamodelo M13/M13-null, calibración, abstención | pendiente |
| 6 · Prospectivo | registro sellado + paper trading neto | registro ✅ (ritual confiable ✅); acumulando |
| 7 · Operación | drift, revalidación, champion/challenger | pendiente |

### Fase 0 — Integridad (bloqueante) — lo hecho y lo que falta
- ✅ **F01** walk_forward rehúsa `pct_real` no certificada.
- ✅ **F02** A0 madura etiquetas (casos del mismo día no se informan).
- ✅ **F03** evidencia rechaza `event_timestamp` futuro.
- ✅ **F04** `particionar` aplica el embargo del manifiesto.
- ⏳ **F05** banco cronológico de flujo (eventos elegidos por reglas *ex ante*, no por
  el movimiento) — **necesita recolección nueva** (no se puede reconstruir desde el
  banco de shocks ya sesgado).
- ⏳ **F06** horizonte intradía con calendario por bolsa.

## Qué necesita cada avance

- **Sin clave, ya (en esta sesión):** Fase 0 (hecho); **M13 vs M13-null EXPLORATORIO**
  sobre los datos históricos existentes (consenso + features ABM `direccion_pct`/
  `volatilidad_pct` vs solo consenso), claramente etiquetado como exploratorio.
- **Necesita `ANTHROPIC_API_KEY`:** M4/A2 (un LLM), M5/M6 (ensembles), features del ABM
  con respuestas congeladas, evidencia B-vs-D.
- **Necesita datos excluidos del volcado (SQLite/JSON) + recolección:** F05 banco de
  flujo, recalcular tasas, microestructura.
- **Necesita tiempo:** la **cohorte prospectiva** sellada — la única prueba limpia.

## Reglas de oro (no negociables)

1. No optimizar sobre el examen. No cambiar hipótesis/métrica/muestra tras ver el
   resultado. Si falta potencia → **inconcluso**, nunca "probado".
2. Diferencia **pareada por evento** (`canonical_event_id`); 4 ETFs de un anuncio NO
   son 4 experimentos. Reportar siempre cobertura y denominador.
3. Separar **simulación (visual)** de **pronóstico (ciencia)** de **decisión**.
4. Registro **append-only**: una predicción no se reescribe al ver su resultado.
5. **Simplicidad primero:** no construir predictor completo, 12 especialistas, Monte
   Carlo masivo ni 50–100k agentes hasta que la evidencia lo justifique.

## Matriz de decisión (resumen)

- M13 > M13-null (confirmado y prospectivo) → desarrollar predictor híbrido.
- Consenso > ABM → la dirección vive en los cerebros; ABM queda como simulador/riesgo.
- Un LLM ≈ ensemble → la diversidad no paga; abaratar.
- 500 ≈ 10.150 agentes → compactar el predictor (la visual puede conservar N).
- ABM predice **riesgo** pero no dirección → módulo de riesgo, no alpha direccional.
- Nadie supera baselines con potencia → **descartar la tesis predictiva**, conservar
  el simulador como producto de escenarios/educación.

*El valor científico se construye con experimentos honestos, no con el número de
agentes ni defendiendo una arquitectura preferida.*
