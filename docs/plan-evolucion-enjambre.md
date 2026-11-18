# Plan de evolución de El Enjambre — v2

*Rubicón Lab · El Enjambre · v2, 2026-11-18. Hoja de ruta para llevar el motor de
"experimento convincente" a sistema predictivo **demostrable**. v2 integra los
refinamientos de la auditoría integral (18-11): contrato de evaluación, holdout
congelado con manifiesto, bootstrap multiway, registro prospectivo desde ya,
baselines fuertes, abstención y guía de comunicación. Compañero:
`docs/resumen-avances-enjambre.md` y `docs/analisis-auditoria-integral.md`.*

---

## La estrella polar

> **No queremos que El Enjambre parezca más inteligente. Queremos demostrar, con
> resultados fuera de muestra, que aporta valor frente a un modelo simple.**

### La regla de oro (de la auditoría integral)

> Ninguna cifra sin denominador. Ninguna predicción sin timestamp. Ninguna
> promoción sin holdout. Ninguna mejora sin comparación. Ningún consenso sin medir
> su independencia.

### Tres reglas de disciplina

1. **Medir antes de cambiar** (hipótesis, métrica, comparación, criterio de promoción).
2. **Una variable a la vez.**
3. **Holdout congelado** — no se usa para ajustar nada; cada evaluación se registra.

### Las dos tesis (las decide la evidencia, no la intuición)

- **Verdad A — Predictor:** si la señal sobrevive a datos temporalmente válidos,
  más instrumentos y comparaciones fuera de muestra → capacidad predictiva acotada
  y demostrable.
- **Verdad B — Simulador / focus group sintético:** si la ventaja se debilita al
  controlar memoria, selección y correlación → el producto sigue siendo valioso
  (simulación, visualización, educación), pero la comunicación comercial no vende
  predicción no demostrada.

---

## Dónde estamos (18-11-2026)

- **Fase 0:** esencialmente completa en lo medible sin IA. Hecho y verificado:
  contaminación (la señal de índice NO es memoria), intervalos de confianza, aporte
  por arquetipo, arreglo del baseline (`calibrar_respaldo.py` y `walk_forward.py`),
  P5. Pendiente: **ampliar muestra** y **cerrar controles formales** (contrato de
  etiqueta, holdout con manifiesto, bancos).
- **Fase 2:** probada y **redirigida** — reponderar por acierto histórico NO mejora
  la dirección (0/37 cambios de signo). Queda como pregunta de calibración.
- **Resto:** pendiente.

Números actuales (en muestra, ~4 instrumentos de índice correlacionados): todos
50.6% [45–56] (azar); índice 63.1% [52.5–71.4]; índice fuerte 80.0% [69.6–85.7].
**Límite honesto:** pocos instrumentos; confirmación real = más datos + prospectivo.

---

## Dos vías

- **CIENCIA** (Fases 0,1,2,3,4,7): ¿aporta valor predictivo fuera de muestra?
- **INGENIERÍA** (Fases 5,6,8): robustez, escala, mantenibilidad. En paralelo, pero
  no se escala a ciegas un sistema cuya ventaja aún se evalúa.

---

# VÍA CIENCIA

## FASE 0 — Verdad estadística y línea base *(cerrar)*

**Objetivo:** línea base honesta por mercado, instrumento, tipo de noticia y
horizonte, con incertidumbre explícita y holdout congelado.

- **0.1 Ampliar datos de índice** — `docs/runbook-ampliar-datos-indice.md`
  (cosechar + backtest + exportar por botón). Buscar más instrumentos y períodos,
  no solo más noticias de los mismos 4 ETF.
- **0.2 Contrato de evaluación (NUEVO, hacer ANTES de medir):** fijar momento de
  publicación, precio de referencia, horizonte exacto, regla subida/bajada/neutral,
  trato de movimientos pequeños, sesiones cerradas, eventos solapados, ventana de
  reacción. Una predicción no es reproducible si su etiqueta/horizonte cambian
  después de ver el resultado.
- **0.3 Tres bancos:** ordinario / extraordinario / difícil. Reportar cada uno por
  separado y el agregado transparente.
- **0.4 Holdout congelado (formalizar):** partición temporal, congelar con **hash +
  manifiesto**, no usarlo para ajustar nada, **registrar cada evaluación**, una sola
  evaluación de promoción.
- **0.5 Intervalos — bootstrap multiway:** agrupar por **evento × instrumento ×
  período** (no solo por activo), para no tratar 4 ETF correlacionados ni 10
  noticias de un mismo evento como independientes. Documentar la unidad de remuestreo.
- **0.6 Instrumentación por simulación:** % API fresca / caché / fallback, errores,
  JSON inválidos, timeouts, latencia p50/p95/p99, modelo+versión, hash de prompt,
  nº de cerebros únicos y % de respuestas compartidas — **cruzable con cada resultado.**
- **0.7 Limpieza menor:** que el CLI de `walk_forward.py` imprima `promover_anidado`
  como veredicto autoritativo (hoy imprime `promover()`, que es diagnóstico).

**Gate:** no afirmar ventaja consolidada hasta tener etiqueta/horizonte estables,
baseline solo-train, holdout protegido, métricas por segmento, incertidumbre con
dependencia bien tratada y datos no dominados por pocos instrumentos.

## FASE 7-mínima — Registro prospectivo *(EMPEZAR YA, en paralelo)*

> **La joya de la auditoría integral.** Los datos prospectivos (predicción
> registrada ANTES de conocer el resultado) son inmunes a contaminación y selección.
> Empezar a acumularlos hoy es casi gratis y resuelve de raíz la duda "predictor vs
> simulador". Por eso sube a prioridad inmediata, antes que refinar el bootstrap.

**Objetivo:** registro inmutable de cada predicción con todo su contexto, que se
resuelve solo cuando llega el resultado futuro.

Cada registro: id, evento, activo, fecha de noticia, `as_of_timestamp`, horizonte,
dirección, probabilidad, consenso, convicción, decisión de abstención, modelo LLM,
versión de prompt/código/agregador/evidencia, fuente de cada respuesta
(API/caché/fallback), resultado futuro + timestamp de resolución, versión del
evaluador.

**Entregable:** primera cohorte prospectiva + panel mínimo (acierto, cobertura,
Brier). **Gate:** poder responder, cualquier día, "qué predijo, con qué info, qué
versión, cuántos casos cubrió y cómo le fue vs baseline".

## FASE 1 — Capa de evidencia temporalmente válida *(prioridad científica #1)*

> La palanca real: el lastre está en los INSUMOS, no en los pesos (lo demostró el
> resultado negativo de la confianza efectiva).

**Objetivo:** dejar de entregar un titular desnudo; entregar un paquete estructurado
que represente lo que se sabía en el momento del evento.

- Módulo central `engine/evidence/` (no que cada agente busque por su cuenta):
  identifica activo/entidad/tipo de evento, recupera info disponible a la fecha de
  corte, extrae hechos y expectativas, marca qué es nuevo, estima qué estaba
  descontado, contrasta fuentes, detecta contradicciones, marca incertidumbre, y
  produce un **objeto estructurado versionado** (esquema JSON con `as_of_timestamp`,
  `facts`, `expectations`, `priced_in_assessment`, `sources`, `contradictions`,
  `uncertainties`, `evidence_version`).
- **Reglas temporales estrictas:** no incorporar nada posterior al `as_of`;
  distinguir fecha de publicación/hecho/recuperación; snapshots de fuentes; rechazar
  fuentes sin timestamp; el LLM no inventa hechos ausentes.
- **Separar** hecho / expectativa previa / resultado / diferencia vs expectativa /
  interpretación / inferencia / info faltante.
- **Modo sombra primero:** producir la evidencia sin alterar las predicciones.

**Experimento:** B (motor actual congelado) vs D (mismo motor + evidencia), mismos
eventos/horizonte/holdout. **Gate:** se promueve solo si mejora métricas fuera de
muestra, no por mejor narrativa.

## FASE 2 — Agregación, probabilidad y abstención *(selectiva)*

> Aprendizaje: la reponderación direccional por confianza efectiva quedó
> **descartada** (0/37 cambios de signo). Sobreviven las piezas que no son eso.

- **Separar 4 salidas:** consenso · dirección · **probabilidad calibrada** · cobertura.
- **Abstención:** el sistema puede decir "no predigo" (evidencia insuficiente,
  fuentes contradictorias, consenso dependiente de un cerebro, baja convicción,
  régimen fuera de distribución). Medir acierto condicionado, cobertura y **curva
  riesgo-cobertura** (nunca acierto selectivo sin cobertura).
- **Detector de consenso engañoso:** alerta cuando muchas voces derivan de pocos
  cerebros, hay duplicación de fuentes, o la noticia ya era conocida.
- **Confianza efectiva (pregunta residual):** evaluar si ayuda a la CALIBRACIÓN
  (Brier/Log Loss/ECE), no a la dirección.

**Gate:** ganar al agregador actual en el holdout en las métricas predefinidas, sin
reducir cobertura de forma engañosa.

## FASE 3 — Diversidad e independencia

**Objetivo:** medir cuánta información independiente aportan las voces y qué tamaño
de población es eficiente.

- Experimentar 110 / 220 / 400 cerebros (todo lo demás constante). Medir correlación
  de señales y respuestas, diversidad semántica, información marginal por
  cerebro/arquetipo, rendimiento y costo.
- **Distribución adaptativa** solo DESPUÉS de medir aporte.
- **Agentes detectores** (abogado del diablo, causalidad débil, info descontada,
  verificador de fuentes) en **modo sombra** primero: diagnostican sin influir;
  medir si sus alertas predicen errores antes de darles voz.

**Gate:** más diversidad solo si mejora fuera de muestra o reduce costo a igual
rendimiento.

## FASE 4 — Experimento A/B/C/D *(la prueba de valor)*

| | Sistema | Pregunta |
|---|---|---|
| **A** | Baseline(s) simple(s) | ¿El piso a superar? |
| **B** | Enjambre actual congelado | ¿Aporta sobre el baseline? |
| **C** | B + agregación/abstención/diversidad validadas | ¿La optimización añade? |
| **D** | C + capa de evidencia | ¿La evidencia añade? |

- **Baselines fuertes (no débiles a propósito):** tasa histórica, clase mayoritaria,
  momentum simple, sentimiento del titular básico, clasificador simple con variables
  a la fecha.
- Mismos eventos/timestamps/horizonte/etiquetas/holdout; predicciones registradas
  antes de revelar etiquetas; comparación pareada por evento; intervalos por clúster;
  métricas por mercado/instrumento/tipo.
- **Promoción pre-registrada:** métrica primaria, secundarias, margen mínimo
  relevante, tolerancia de degradación por segmento, método de incertidumbre,
  corrección por comparaciones múltiples. Si C no supera B, no se promueve C; si D no
  supera C, no se afirma que la evidencia mejoró la predicción (aunque mejore la
  trazabilidad).

**Entregable:** veredicto de valor predictivo por mercado y segmento, con límites.

---

# VÍA INGENIERÍA *(en paralelo, según demanda)*

## FASE 5 — Infraestructura durable
Sacar la simulación del request web: API crea un `simulation_job` durable → cola →
workers con lease → persistencia de progreso → reintentos/idempotencia/backpressure/
dead-letter. **Gate:** prueba de carga (concurrencia, cola, error, recuperación de
worker, sin duplicar jobs ni gasto). Fijar objetivo de carga y presupuesto antes.

## FASE 6 — Microestructura y realismo *(baja por ahora)*
Profundidad del libro, impacto, slippage, liquidez, spread. Separar dos preguntas:
¿parece realista? (valor de simulación) vs ¿mejora la predicción? (otro experimento).
No invertir fuerte sin hipótesis concreta de valor.

## FASE 8 — Modularización *(al final)*
Módulos con interfaces explícitas y esquemas versionados (motor, agentes, cerebros,
evidencia, agregación, evaluación, datos, API, frontend). Después de estabilizar los
contratos, para no refactorizar en círculos.

---

## Orden de ejecución

```
AHORA
 ├─ 0.1 Ampliar datos de índice (runbook, acción de Giorgio)
 ├─ 0.2 Contrato de evaluación   0.4 Holdout congelado (hash+manifiesto)
 ├─ 7-mínima: registro prospectivo  ◀── empezar ya, resuelve la duda de raíz
 └─ 0.5 bootstrap multiway   0.6 instrumentación   0.7 limpieza CLI
        │
        └─ FASE 1 evidencia (rama experimental, modo sombra) ─ B vs D
               └─ FASE 2 probabilidad/abstención
                      └─ FASE 3 diversidad
                             └─ FASE 4 A/B/C/D ─ veredicto
En paralelo: FASE 5 infra (según demanda) · Después: 6 y 8
```

## Primeros sprints

- **Sprint 0 — Línea base auditable:** correr el runbook; conservar crudos; validar
  duplicados/solapamientos/timestamps; fijar etiqueta y horizonte (0.2); congelar
  holdout con hash; guardar versión B; bootstrap multiway; informe por instrumento y
  banco.
- **Sprint 1 — Registro prospectivo:** esquema inmutable; registrar cada salida antes
  del resultado; panel mínimo (acierto/cobertura/Brier); guardar API/caché/fallback.
- **Sprint 2 — Prototipo de evidencia (sombra):** JSON Schema; adaptador de fuentes;
  filtros temporales; hechos/expectativas; citas; contradicciones; validar; correr
  sin influir.
- **Sprint 3 — Experimento de evidencia:** B vs B+evidencia, mismo conjunto;
  comparación pareada; decidir por resultados, no por narrativa.

---

## Qué cuenta como "mejora" (y qué no)

**NO basta:** más agentes, más tokens, respuestas más largas, explicaciones más
convincentes, más realismo visual, más consenso, más confianza declarada.

**SÍ cuenta (fuera de muestra):** mejor acierto, mejor Brier/Log Loss, mejor
calibración (ECE/MCE), más cobertura a igual riesgo, menor costo a igual
rendimiento, menos degradación entre regímenes, menos errores técnicos, más
reproducibilidad.

## Cómo comunicar las cifras (para inversionistas)

**Correcto:** *"En la muestra histórica evaluada, el sistema obtuvo X% en índices,
IC Y–Z, bajo el horizonte y la etiqueta especificados; concentrado en ciertos
instrumentos y pendiente de confirmación con muestra más amplia."*

**Evitar:** "El Enjambre acierta el 80%" · "10.150 agentes predicen el mercado" ·
"la IA supera al mercado". El 80% es un subconjunto de 30 casos con convicción
fuerte: siempre con cobertura, instrumento, período, horizonte e intervalo.

## Ficha de experimento (plantilla)

`experiment_id, hypothesis, baseline_version(B), candidate_version(D), dataset_hash,
code_commit, prompt_hash, llm_model_version, evidence_version, universe, period,
horizon, label_definition, primary_metric, secondary_metrics, holdout_manifest_hash,
train/validation_window, embargo, bootstrap_unit, min_effect_size, coverage_floor,
segments, exclusions, promotion_rule, rollback_rule, result`.

## La pregunta que guía el próximo ciclo

> Si entregamos a los mismos agentes información más completa, verificable y
> temporalmente correcta, ¿mejora su capacidad de anticipar lo que hará el mercado?

Esa es la hipótesis que merece ahora el dinero, el tiempo y la ingeniería.
