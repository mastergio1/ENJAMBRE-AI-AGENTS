# El Enjambre — Plan de implementación v4

**Rubicón Lab | 23 de noviembre de 2026 | Propuesta de auditoría y ejecución**

## 0. Resumen ejecutivo

**Meta:** establecer si las señales generadas por El Enjambre, en determinados instrumentos, tipos de acontecimientos y horizontes, mejoran resultados futuros frente a métodos simples y frente a los mismos LLM sin simulación. No se pretende prometer que el sistema «predice todo»: cada afirmación debe quedar restringida a la población y el contrato realmente evaluados.

**Diagnóstico:** la ablación histórica reporta para índices aproximadamente 62,8 % (clase mayoritaria), 65,1 % (consenso LLM, A3) y 53,5 % (dirección del precio simulado ABM, A4) en una muestra pequeña presentada como fuera de muestra. El contraste más reciente detecta deficiencias adicionales: `ablacion.py` estima A0 con etiquetas del conjunto evaluado; `holdout.py::particionar` incorpora datos nuevos posteriores al holdout al desarrollo; la inferencia por bootstrap elige el intervalo más ancho entre agrupaciones distintas sin una garantía general de cobertura; y la selección histórica contiene sesgos. Por tanto, esos porcentajes son **indicativos, no una prueba predictiva definitiva**.

La versión revisada de `main` es `fe3415992eb4996bca6eb6808c6367f817bc3c16`; la rama predeterminada `claude/m-d-file-6z1e63` incorpora una bitácora posterior; los PR #34 y #35 siguen abiertos en borrador, encadenados. La bitácora **reporta** 468 tests verdes; esa suite completa no se ejecutó independientemente durante esta revisión. El motor de 10.150 agentes, aproximadamente 110 cerebros compartidos, visualización y registro prospectivo inicial ya existen. El trabajo pasa a preservar evidencia, comparar alternativas y validar predicción real.

**Principio:** no optimizar sobre el examen. El resultado negativo (ausencia de mejora) también es un hallazgo válido.

## 1. Las tres hipótesis científicas

- **H1 — consenso:** los LLM extraen una señal útil de noticias, pero el precio simulado del ABM añade ruido a su signo.
- **H2 — microseñales del ABM:** aunque el signo final del precio simulado falle, las variables de la interacción colectiva (dispersión, desequilibrio de órdenes, contagio, volatilidad, velocidad de consenso) podrían añadir información a A3.
- **H3 — artefacto:** la aparente señal histórica resulta de tendencia alcista, selección retrospectiva, memoria del LLM, disponibilidad temporal defectuosa o dependencia entre casos.

La investigación debe poder rechazar las tres. No inferir valor predictivo de la existencia de 10.150 agentes.

## 2. Reglas transversales antes de cualquier sprint

1. **Seguridad:** rotar `ENJAMBRE_PIPELINE_TOKEN` si fue expuesto; actualizar Render/GitHub; eliminar `?clave=` de `/api/predicciones/resumen` y exigir `X-Pipeline-Token` u otro mecanismo seguro; no imprimir ni exponer credenciales. No pedir ni pegar claves en el chat.
2. **Rama canónica:** decidir si la fuente de verdad para desarrollo y despliegue es `main` o la rama actualmente predeterminada; alinear Actions y base de PR. No fusionar PR #34/#35 hasta rebase/revisión de conflictos contra las modificaciones recientes.
3. **CI:** por cada PR ejecutar pytest sin red y con SQLite temporal, lint, build frontend, chequeos de schema, comprobación de secretos y contratos temporales; no escribir en Render ni en bases de producción.
4. **Identidad:** `event_id` para anuncio, `event_group_id` para dependencia estadística, `observation_id` para anuncio × activo × contrato/horizonte y `simulation_id` para cada ejecución; los reintentos no reemplazan ejecuciones distintas.
5. **Procedencia:** conservar input point-in-time, versión de datos, modelo, prompt, configuración, caché, código, regla de etiqueta, timestamp UTC y estado de cada intento.
6. **Separación:** exploración histórica, desarrollo, holdout confirmatorio y predicciones prospectivas son cohortes distintas. No presentar resultados del desarrollo como confirmación independiente.
7. **Cobertura:** cada intento planificado debe producir predicción sellada, abstención explícita o error persistido; los fallos no desaparecen del denominador.

## 3. Fases y criterios de aceptación

### Fase 00 — Control de acceso y prueba reproducible (P0)

**Construir:** remover autenticación por query string; rotar token; elegir rama canónica; activar CI en cada PR; inmovilizar commit de referencia, seeds y hashes. Capturar métricas/reportes actuales como baseline histórico *exploratorio*.

**Pruebas:** endpoint rechaza query token y acepta header; no secretos en URLs ni logs; suite y build en limpio; PR con tests fallidos bloqueado; cambios no escriben en producción.

**Cierre:** operación administrativa segura y baseline reproducible. La cifra de 468 tests verdes es un reporte que debe comprobarse en CI.

### Fase 01 — Integridad prospectiva y relojes (P0; continua en paralelo)

**Construir:** reconciliador `eventos planificados → intentos → predicciones selladas → resultados pendientes/resueltos`; fallos observables y persistidos, no solo mensajes de log; guardar input y hash. Fijar contrato temporal por objetivo: `release_at`, `available_at`, `as_of`, `prediction_recorded_at`, `ready_at`, `entry_at`, `exit_at`, `outcome_available_at`. Versionar calendario NYSE, horario estacional, horario extendido y proveedor de precios. No cambiar silenciosamente el contrato del resolvedor histórico ni reescribir etiquetas antiguas.

**Hallazgo actual:** el resolvedor actualizado resuelve fines de semana usando la primera sesión posterior a la *fecha* de la señal, pero sigue descartando la **hora**, por lo que una publicación a las 08:00 y otra a las 15:00 reciben el mismo anclaje. Es apto como corrección puntual, no como etiqueta de ejecución temporalmente precisa.

**Pruebas:** viernes tarde, sábado, domingo, feriado, cierre adelantado, CPI antes de apertura, FOMC durante sesión, ejecución tardía, crash/retry, doble resolución, duplicados multi-ETF, fallos de datos; cada caso conserva el denominador y su motivo.

**Cierre:** 100 % de intentos reconciliables y etiquetas reproducibles con timestamps. Cero escrituras prospectivas silenciosamente perdidas.

### Fase 02 — Integración macro, identidad y dataset de eventos (P0)

**Construir:** revisar y actualizar PR #34 y #35 contra rama canónica reciente; ejecutar migración en copia temporal; persistencia de eventos/observaciones/simulaciones/resultados separados. Cosecha de macro por calendario anunciado de antemano (CPI, FOMC, empleo) sin escoger días mirando el retorno; conservar períodos sin movimientos, fallas y fuentes fechadas. Para nuevos horizontes, no deduplicar por `simulation_id`.

**Pruebas:** dos anuncios × cuatro ETFs = ocho observaciones, dos grupos de dependencia; resultados separados por ETF, horizontes separados, retry idempotente, export/import round trip, no migración silenciosa de legado.

**Cierre:** dataset verificable, sin pérdida de multiplicidad y con fuente primaria y `available_at` para cada observación.

### Fase 03 — Holdout y estadística válidos (P0)

**Construir:** reparar A0 para entrenar la regla mayoritaria exclusivamente con etiquetas anteriores al test. Revisar `holdout.py`: nuevas observaciones posteriores al corte original no pueden alimentar entrenamiento de un examen anterior; formar cohortes prospectivas futuras independientes y protegidas. Mantener snapshots/versiones sellados; registrar quién accedió a etiquetas finales y cuándo; si ya se inspeccionó un holdout, tratarlo como desarrollo para futuras optimizaciones.

**Construir inferencia:** diferencias de pérdida **pareadas** A3 frente a A4 por mismos eventos; una unidad principal `event_group_id`, y análisis temporal por bloques como sensibilidad. No llamar «bootstrap multiway» al máximo de tres intervalos unidimensionales; especificar un procedimiento de inferencia antes de mirar resultados, y simulaciones de potencia según el efecto mínimo relevante. Los cuatro ETFs de un mismo anuncio no son cuatro eventos independientes.

**Pruebas:** A0 no cambia si se invierten etiquetas solo del test; nuevas filas futuras no aparecen en train anterior; grupos indivisibles; embargo por tiempo y disponibilidad de etiqueta; intervalos reproducibles y cobertura simulada bajo diseños conocidos.

**Cierre:** un evaluador independiente obtiene el mismo resultado sin mirar el conjunto final durante selección.

### Fase 04 — Ablación justa A0–A5 (P1)

**Comparadores:** A0 base histórica/momentum; A1 léxico; A2 un LLM neutral; A3 consenso ~110 LLM sin ABM; A4 ABM completo; A5 ABM + evidencia point-in-time. Cada comparación usa el mismo conjunto, horizonte, reloj de predicción, proveedor de precios y denominador; registrar abstenciones y costo de inferencia. Los resultados ya vistos son **exploratorios**.

**A2:** antes de hacer llamadas, cambiar caché para incluir `model_id`, `prompt_hash`, versión del parser, input y política as-of; guardar fallos por evento en lugar de omitirlos. Si se ejecuta un modelo de 2026 sobre titulares anteriores a su cutoff, etiquetar el experimento como diagnóstico de reconstrucción, nunca evidencia prospectiva limpia. La clave debe cargarse en entorno de ejecución seguro, no en chat.

**Cierre:** reporte A0–A5 comparable en una nueva cohorte válida, diferencias pareadas, intervalo y costo por predicción; decidir si A4 añade valor o solo visualización.

### Fase 05 — Extraer características predictivas del ABM (P1, experimento con criterio de parada)

Si A4 no mejora A3, **no** aumentar agentes ni tunear sus parámetros al azar. Exportar por simulación, sin usar resultados reales como inputs: `consensus_dispersion`, `order_imbalance`, `herding_index`, `volatility_simulated`, `price_path_shape`, `leader_follower_disagreement`, `liquidity_pressure`, cambios temporales del consenso y persistencia. Definirlas por contrato y correr A3 frente a A3 + features ABM con un clasificador muy simple regularizado entrenado solo en desarrollo. Añadir control con rasgos simulados permutados y comparación de costo/latencia.

**Cierre:** si no hay mejora estable de Brier respecto a A3, congelar esta línea como investigación negativa; no promocionar features por correlaciones de desarrollo.

### Fase 06 — Evidencia económica + calibración (P1)

Ya existe `engine/evidence/` en modo sombra y un adaptador de contexto de precios anteriores. Ampliarlo con calendario oficial, cifras macro, consenso previo con vintage, revisiones históricas, fuentes archivadas y expectativa/resultado. Verificar `published_at` **y** disponibilidad efectiva (`available_at`); no asumir que una URL encontrada en 2026 acredita su disponibilidad íntegra en 2024. Probar B (solo titular) vs D (evidencia) con respuestas LLM congeladas y mismo presupuesto.

Entrenar calibrador probabilístico sobre entrenamiento, seleccionar solo con desarrollo, evaluar Brier/log-loss y curva riesgo-cobertura; no traducir fuerza de consenso directamente a probabilidad. Abstención requiere razón y siempre se reporta cobertura.

**Cierre:** mejora en datos no utilizados para el diseño, sin filtraciones temporales ni degradación relevante de cobertura/costo.

### Fase 07 — Experimento prospectivo confirmatorio (P0 científico)

**Pregunta primaria propuesta:** ¿El mejor sistema seleccionado en desarrollo reduce la pérdida Brier de la probabilidad de subida de SPY frente al mejor baseline predefinido en eventos macro estadounidenses seleccionados por calendario, con entrada posterior a la señal y horizonte fijo de una sesión elegible?

Antes de recoger/desvelar desenlaces, congelar: universo (por ejemplo, CPI, FOMC y NFP), instrumento primario SPY, horario y reglas de ejecución, fuentes, horizonte exacto, versión del predictor, modelo, calibrador, baseline, pérdida primaria, pérdida secundaria, mínimo efecto de interés, procedimiento de incertidumbre, política de faltantes, potencia y criterio de parada. SPY es unidad primaria; QQQ/DIA/IWM son panel secundario correlacionado.

**Métrica:** ganancia Brier pareada por evento (`Brier_baseline - Brier_modelo`), IC 95 % con dependencia apropiada, cobertura, fallo/abstención, latencia y coste. Para retorno continuo adicional: MAE/RMSE/MSE y costos de ejecución si se promete utilidad de trading. Contrastar contra baseline entrenado, momentum, LLM aislado y A3. Hacer el test final **una vez**, dejando constancia del acceso. Corregir por objetivos secundarios múltiples.

**Cierre:** afirmar la ventaja solo si supera el margen mínimo y el protocolo de incertidumbre definido; de lo contrario: «no demostrada», preservar el producto de simulación. Si la muestra no tiene potencia, informar «inconcluso», nunca «probado».

### Fase 08 — Operación, producto y plataforma Rubicón Lab (condicionada)

Separar API y trabajadores; cola durable, leases, retries, idempotencia, métricas y presupuesto por experimento. Optimizar llamadas LLM después de A2; si uno rinde como 110, reconsiderar economía de costos. Para Rubicón Lab extraer interfaces reutilizables (`Population`, `AgentPolicy`, `InteractionNetwork`, `Environment`, `Intervention`, `Outcome`, `Evaluator`, `DataProvider`) sin asumir que un predictor financiero transfiera su precisión a publicidad. Mantener un producto de simulación valioso aun ante resultado predictivo negativo.

**Cierre:** infraestructura recuperable y un segundo prototipo vertical con validación independiente de datos reales.

## 4. Secuencia de entregas: qué haría primero

| Entrega | Cambio | Tests imprescindibles | Resultado permitido |
|---|---|---|---|
| **S0 — Seguridad/CI** | Token URL → solo header; rotación; rama canónica; CI | Auth negativo/positivo, secretos, pytest, build | Puede desplegarse tras revisión |
| **S1 — Reparar evaluación** | A0 train-only; holdout sin datos futuros; definir grupos y contratos de prueba | Inversión de etiquetas test no afecta A0; nuevos futuros no entran en train | Sin acceso a holdout real |
| **S2 — Registro y reloj** | Reconciliador; fallos persistentes; timestamp exacto y calendario | 12 casos temporales/multiasset, crash/retry | En paralelo, sin modificar motor |
| **S3 — PR macro** | Rebase/revisión #34 → #35 y esquema idempotente | 8 observaciones, dos eventos, roundtrip, no sobrescritura | Integración tras review |
| **S4 — A2 diagnóstico** | Runner cache versionada, cohortes sin leakage y costo | Cache cambia si modelo/prompt cambia; fail explícito | Exploratorio, no confirmación |
| **S5 — ABM features** | A3 vs A3+features con ablation | Pares, semillas, test de permutación, costo | Promover solo si mejora |
| **S6 — Evidencia** | Fuentes PIT y B vs D | Timestamps, snapshots, revisiones, DST | Shadow → si supera gates |
| **S7 — Confirmación** | Experimento pre-registrado sobre nuevos eventos | Blindaje, independencia, cobertura y CI | Una evaluación final |

La ejecución prospectiva debe seguir corriendo a la vez que S0–S6, con monitoreo de fiabilidad. No establecer tiempos de calendario artificiales: el avance ocurre al cumplir gates, no al declarar una fecha.

## 5. Decisiones ante los resultados

**Si A2 ≈ A3 y A4 es inferior:** la distribución de 110 cerebros no está justificando su coste para signo direccional; probar un producto predictor mínimo con A2/A3, mantener el ABM como simulación e investigar features con presupuesto limitado.

**Si A3 supera A2 pero A4 no supera A3:** la diversidad de arquetipos tiene valor; priorizar agregación/calibración y evidencia, no magnitud del precio simulado.

**Si A3+features ABM supera A3:** el motor multiagente aporta información indirecta. Validar esa diferencia de nuevo sobre un período realmente futuro, sin reutilizar el holdout exploratorio.

**Si nadie supera baselines en prospectivo:** resultado negativo de la tesis predictiva financiera; conservar la tecnología como simulador para escenarios, investigación y formación, y reutilizar la metodología de validación en otros verticales.

**Si aparece una mejora robusta y comercialmente útil:** construir API de predicción con señal probabilística, abstención, incertidumbre y latencia; evaluar datos y cumplimiento normativo antes de comercializar señales.

## 6. Prompt listo para Codex — primera entrega

> **EL ENJAMBRE — Sprint S0/S1: Seguridad y evaluación válida.** Trabaja sobre una rama aislada partiendo del head actual confirmado y verifica primero estado de GitHub y PR #34/#35; no presumas que están fusionados. **Tarea A:** eliminar autorización `?clave=` del tablero `/api/predicciones/resumen`, conservar header seguro, añadir pruebas negativas y evitar logs con credenciales. No intentes rotar secretos: dejar una checklist para el administrador. **Tarea B:** corregir en `engine/calibration/ablacion.py` la clase mayoritaria A0 para que se calcule solo con entrenamiento, nunca sobre las etiquetas de evaluación. **Tarea C:** corregir `engine/calibration/holdout.py` para que filas nuevas posteriores a un corte no entren al conjunto de desarrollo que evalúa un holdout anterior; incluir pruebas de no-leakage, timestamps, duplicados y grupos cuando corresponda. **Tarea D:** proponer CI Python/Web en PR sin llamadas de red ni secrets. Entrega diagnóstico con referencias, diseño mínimo, diffs, tests y PR draft. **No** ejecutar nuevos backtests, no consultar el holdout real, no modificar reglas de decisión de agentes, no escribir en producción, no fusionar y no ampliar alcance a A2/A5. Detente para revisión.

## 7. Evidencias de código revisadas

- `engine/calibration/ablacion.py`: `_signo_mayoria`, `_items`, `gate_abm` y salida A0–A5.
- `engine/calibration/holdout.py`: `construir_manifiesto`, `verificar_manifiesto`, `particionar`.
- `engine/calibration/intervalos_multiway.py`: intervalos unidimensionales separados y elección del más ancho.
- `engine/calibration/un_llm.py`: caché por texto de titular y llamadas LLM.
- `engine/evidence/{contrato,fuentes,recoleccion}.py`: contexto point-in-time actual, principalmente barras diarias previas.
- `engine/contenido/pipeline.py` y `persistencia.py`: registro prospectivo, múltiples símbolos, evidencia sombra e idempotencia actual.
- `engine/contenido/resolver_predicciones.py`: corrección para fecha sin barra, aún sin resolución intradía basada en hora exacta.
- `engine/server.py`: tablero administrativo y separación de lectura vs simulación.
- `docs/{hallazgo-ablacion,hallazgo-baselines,hallazgo-bootstrap-multiway,plan-evolucion-enjambre}.md`.
- GitHub: `main` `fe3415992e`, rama predeterminada posterior `ea4574a10a`, PR #34 `8d8053e9`, PR #35 `693842a7`.

**Límites de esta auditoría:** verificación de contenido y estado de GitHub; no se corrió la suite completa localmente, no se consultó producción privada ni se verificaron sus secretos o la base de predicciones reales. Los porcentajes y 468 tests son resultados reportados por el equipo, no certificados por esta revisión independiente.
