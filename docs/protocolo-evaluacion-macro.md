# Protocolo de evaluación macro

Este protocolo propone tres objetivos separados para El Enjambre. El signo del movimiento a cinco minutos del anuncio es un objetivo binario. El retorno a una y dos sesiones es una magnitud continua. Cada objetivo necesita precios, comparadores y métricas propios. Las decisiones se registrarán antes de calcular resultados.

La referencia de la auditoría es `8d8053e`. La CLI nueva `calibration.particiones_macro` prepara un reparto de metadatos locales. La congelación real del conjunto final y su evaluación son operaciones posteriores. Los dos acontecimientos del piloto son datos de desarrollo del importador.

## Evidencia del código y del historial

| Ruta en la referencia auditada | Hallazgo y consecuencia |
|---|---|
| `engine/calibration/walk_forward.py:52` | El cargador ordena por `fecha`, descarta retornos cero y reduce cada registro a fecha, etiqueta binaria, señales y dirección. Pierde grupos e intervalos. La fecha exportada puede corresponder a la simulación. |
| `engine/calibration/walk_forward.py:80` | Las ventanas y el embargo se expresan en filas. La tasa base de cada pliegue usa solamente entrenamiento en la línea 98. |
| `engine/calibration/walk_forward.py:126` | `promover` elige entre seis configuraciones y mide su ganancia en las mismas predicciones usadas para elegir. Ese resultado pertenece a selección dentro del desarrollo. |
| `engine/calibration/walk_forward.py:156` | `promover_anidado` separa selección y evaluación final, pero vuelve a calcular un corte porcentual en las líneas 170–177. Carece de manifiesto persistido y registro de accesos. El reajuste de la línea 217 incorpora el conjunto final después de evaluar. |
| `engine/calibration/walk_forward.py:236` | La entrada CLI llama a `promover(casos)` en la línea 240. |
| `engine/calibration/verificador.py:28` y `:51` | Coexisten reparto por hash heredado y reparto temporal con purga por grupo opcional. El embargo cuenta filas. |
| `engine/calibration/intervalos.py:26` | Agrupa por símbolo. En la línea 53 pasa a remuestreo por fila con menos de dos grupos. Un anuncio macro requiere conservar juntos sus instrumentos. |
| `engine/contenido/resolver_predicciones.py:28` | Reduce `as_of_iso` a fecha y llama a `pct_sin_fuga`. |
| `engine/calibration/remedir_sin_fuga.py:67` | Toma el cierre de la rueda siguiente a la fecha encontrada como base. Con horizonte dos termina tres posiciones después de esa fecha. Una fecha sin barra devuelve `None`. Ese contrato no conserva la hora de salida de la señal. |
| `engine/contenido/persistencia.py:948` y `:978` | Registra predicciones mediante `INSERT OR IGNORE` y resuelve dirección con zona neutral de 0,3%. Los resultados neutrales y las abstenciones quedan sin puntuar en ese acierto. |
| `engine/contenido/calibracion.py:94` | Implementa métricas probabilísticas. Evaluar magnitud de retorno exige un contrato continuo y pérdidas apropiadas. |

`git blame` atribuye el bloque CLI a `54d6289`. El diff de `0884e8a` añadió 70 líneas con `promover_anidado` y conservó la llamada anterior. Su mensaje declara que mantiene `promover` clásico. Esto acredita que quedó pendiente conectar la CLI con la nueva evaluación, tarea también registrada en `docs/plan-evolucion-enjambre.md:92`.

El historial registra además `1c6108e` para baseline calculado solo con entrenamiento, `d4aa164` para partición temporal con purga, `1b0cc0a` para embargo en filas, `4c8566f` para bootstrap por activo y `379d699` para el resolvedor prospectivo. La revisión utilizó código, diffs y atribución de líneas.

## Identidad, cohortes e información disponible

La observación se identifica con `observation_id`, derivado de `[event_id, symbol, horizon]`. El horizonte identifica un contrato temporal versionado. `event_group_id` es la unidad mínima de dependencia y permanece común entre instrumentos, horizontes y repeticiones del mismo acontecimiento. Comunicados simultáneos que forman un conjunto informativo, como FOMC y proyecciones económicas, comparten grupo mediante un catálogo de equivalencias fijado previamente. `simulation_id` identifica la ejecución y sus versiones. Una ejecución puede vincularse a varias observaciones.

El informe v2 conserva `case_id` como alias de `observation_id` y `correlation_group` como alias de `event_group_id`. La correspondencia se verifica al importar. El manifiesto utiliza los nombres v2. En el piloto, `origin="historical_reconstruction"` se corresponde con `cohort="historical_reconstruction"`. El futuro origen `prospective` exige evidencia de registro anterior al desenlace. Los campos heredados `origen="historico"` y `origen="en_vivo"` conservan su procedencia, y una etiqueta `en_vivo` por sí sola queda pendiente de verificar cronología y trazabilidad antes de asignarla a una cohorte prospectiva.

Una observación apta para evaluación deberá conservar `release_at`, `available_at`, `as_of`, inicio y final de generación, `prediction_recorded_at`, `execution_latency_ms`, `entry_at`, `exit_at` y `outcome_available_at`. También deberá conservar zona IANA, calendario de sesiones versionado, proveedor, versión de precios y hashes de inputs, modelo, prompt, configuración y código.

`release_at` es la hora oficial del anuncio. `available_at` acredita cuándo quedó disponible el contenido usado. Cada input cumple `input.available_at <= as_of`, y la salida queda registrada después de reunir esa información. Un precio utilizado como etiqueta futura permanece fuera de los inputs previos. Una reconstrucción histórica registra fecha real de generación y corte hipotético de información. Usar un LLM actual conserva el riesgo de contaminación temporal y limita la inferencia predictiva.

El calendario de inclusión contiene todos los anuncios de tipos y fechas fijados, incluidos movimientos pequeños y datos ausentes. Cada exclusión conserva motivo y evidencia. El diseño por calendario evita seleccionar acontecimientos según movimiento posterior o acierto. Las cohortes histórica y prospectiva tienen manifiestos y conclusiones separados.

## Precios y cronología de la señal

La ventana `event_minus_1m_to_plus_5m` implementada en el piloto es descriptiva y empieza antes de la información publicada. Los siguientes contratos predictivos requieren implementación posterior.

Para comparar variantes se fija un corte común de información `as_of` y un plazo de generación registrado en el protocolo. La hora límite para guardar la señal es `signal_due_at = as_of + plazo_de_generación`. La primera entrada elegible sucede después de `ready_at = signal_due_at + execution_latency_ms`, igual para todos los comparadores. En prospectivo se exige `available_at <= as_of <= prediction_recorded_at <= signal_due_at` contra el registro inmutable. Una variante tardía queda registrada como fallo y conserva la misma etiqueta que los demás comparadores. En retrospectivo se guarda por separado la hora real del cálculo moderno y su latencia medida. El reloj de reproducción aplica esa latencia al instante histórico de inicio fijado para el experimento. Ese reloj sirve para comprobar si cabría dentro del plazo y siempre se marca como hipotético.

El proveedor debe documentar timestamps, zona, sesión, correcciones, splits, dividendos, ajuste y semántica de barras. Los precios son positivos y finitos. Cada barra se normaliza a `[bar_start, bar_end)`. Una barra completa solo puede ser input después de `bar_end` y de su disponibilidad efectiva. Su máximo, mínimo y cierre aún en formación contienen información posterior.

La modalidad de precio se fija para todo el contrato. Con cotizaciones se conserva bid, ask, timestamp y límite de antigüedad. El punto medio permite evaluar dirección o retorno de referencia. Afirmar ejecución monetaria requiere además spread, lado, profundidad y costos. Los OHLC son aproximaciones de precio observado cuya ejecución efectiva debe validarse por separado. Las ausencias de precios permanecen como tales, con impacto visible en cobertura.

### Signo a cinco minutos del anuncio

`release_plus_5m_v1` vence exactamente en `deadline = release_at + 300 segundos`. La demora de información o generación reduce el tiempo disponible y mantiene el vencimiento fijo.

La entrada es la primera cotización válida después de `ready_at` o el `open` de la primera barra cuyo `bar_start > ready_at`, según la modalidad fijada. Debe cumplir `entry_at < deadline`. La salida usa la cotización vigente al vencimiento con antigüedad máxima predefinida, o el `close` de la barra cuyo `bar_end == deadline`. Se conservan timestamps efectivos, límites de espera y calidad. La regla de salida utiliza exclusivamente operaciones anteriores o iguales al vencimiento.

Si falta tiempo o datos, se registra `late_information`, `late_signal`, `missing_entry_price` o `missing_exit_price`. El caso permanece en la cobertura del calendario. El CPI de las 08:30 ET exige sesión extendida hasta las 08:35. FOMC de las 14:00 ET vence a las 14:05 regulares. El calendario resuelve horario estacional, suspensiones, feriados y cierres anticipados.

La etiqueta es `Y_5m = 1` cuando `exit_price > entry_price`, y cero cuando es igual o inferior. La igualdad queda incluida en la clase de ausencia de subida. Se predice `p_up`, con objetivo `P(Y_5m=1)`.

### Retorno a una y dos sesiones

`next_regular_open_1session_v1` y `next_regular_open_2sessions_v1` predicen magnitud continua. Se elige la primera sesión regular para la que **`ready_at` sea estrictamente anterior al cutoff operativo del mercado**, que a su vez antecede o coincide con la apertura. Llegar al cutoff obliga a usar la sesión siguiente. La modalidad y el cutoff deben quedar definidos para cada mercado.

La entrada usa el precio de subasta de apertura si se acredita elegibilidad operativa, o la primera cotización válida después de la apertura dentro de un plazo fijo. Estas modalidades requieren contratos distintos. Los inputs y la señal quedan congelados antes del cutoff.

Una señal CPI preparada a tiempo puede entrar en la apertura regular del mismo día. Una señal FOMC de las 14:00 utiliza la próxima apertura elegible. El calendario avanza sobre sesiones de negociación. El horizonte uno termina en el cierre regular de la sesión de entrada. El horizonte dos termina en el cierre regular de la siguiente sesión e incluye el intervalo nocturno. El cierre de referencia y los cierres anticipados siguen la modalidad versionada. El cierre anterior puede ser contexto conocido, mientras el retorno predictivo comienza después de la señal.

Para `k` igual a uno o dos, el objetivo es `R_k = exit_price_k / entry_price - 1`, y la predicción es `yhat_R_k` en esa misma unidad fraccionaria. Un retorno de `0.01` equivale a `1%` y a `100 bp`. Los retornos cero se conservan. La evaluación continua utiliza todos los valores válidos sin umbral de neutralidad ni conversión a signo. Retorno de precio y retorno total con dividendos son contratos diferentes.

Si el motor solo entrega señal o probabilidad, queda pendiente aprender un mapeo a magnitud, `yhat_R_k = f_k(señal, contexto)`. Cada función se ajustará en entrenamiento y se seleccionará en desarrollo, por horizonte. La existencia de una señal direccional no acredita una predicción de magnitud calibrada. Esta etapa no implementa ese mapeo.

## Métricas y comparadores por objetivo

| Objetivo | Pérdida primaria y estimando | Baselines entrenados | Diagnósticos secundarios |
|---|---|---|---|
| Signo a cinco minutos | Ganancia pareada de Brier, `loss_base - loss_model`, promediada primero dentro del evento y después entre eventos | Tasa de subida suavizada del entrenamiento del mismo contrato. Diagnóstico adicional `p=0.5` | Brier de ambos, log-loss con recorte fijo, ECE con bins fijos, acierto binario y cobertura |
| Retorno a una sesión | Reducción pareada de **MSE**, con igual peso por evento, para `R_1` continuo | Media de `R_1` calculada solo con entrenamiento. Referencia adicional de retorno cero | RMSE, MAE, sesgo medio y gráfico de predicho frente a observado |
| Retorno a dos sesiones | Reducción pareada de **MSE**, con igual peso por evento, para `R_2` continuo | Media de `R_2` calculada solo con entrenamiento. Referencia adicional de retorno cero | RMSE, MAE, sesgo medio y gráfico de predicho frente a observado |

Para `G` grupos entrenables, con panel fijo de instrumentos, `mean_Y_g` es la media de etiquetas binarias del grupo. El baseline binario propuesto es `p_base = (1 + sum(mean_Y_g)) / (2 + G)`. La decisión usa un umbral fijado en desarrollo, y `p == umbral` genera abstención. Las predicciones probabilísticas válidas participan en Brier aunque la política direccional se abstenga.

Para retorno continuo, `mean_R_g,k` es la media de retornos del grupo y horizonte. El baseline de media es `mu_k = sum(mean_R_g,k) / G`. Un baseline condicional por tipo de anuncio o instrumento debe fijar variables, regularización y respaldo mediante entrenamiento/desarrollo. Si MAE se estudia como comparación adicional, su comparador óptimo constante es la **mediana ponderada de los retornos de entrenamiento**, con peso total uno por acontecimiento. Cambiar la pérdida primaria a MAE constituye otra especificación registrada antes de evaluación.

MSE se calcula en retorno fraccionario al cuadrado. Su representación en `bp²` multiplica por `10^8`. RMSE y MAE en puntos básicos multiplican por `10^4`. El informe identifica la unidad junto a cada cifra. La calibración continua mediante sesgo, pendiente o intervalos predictivos es secundaria y opcional. Cualquier corrección de magnitud se aprende en entrenamiento/desarrollo y se congela antes de medir el conjunto final.

Cada baseline se ajusta al objetivo, horizonte, ancla, sesión y cohorte del modelo. En cada pliegue solo usa etiquetas disponibles en `train_cutoff`. Para la evaluación final se fija con entrenamiento y desarrollo permitidos antes de abrir los resultados finales. Los comparadores comparten precios y observaciones con el modelo.

Una predicción ausente activa el respaldo operacional predeclarado, por ejemplo la tasa base binaria o la media continua del entrenamiento. Se informa su frecuencia y contribución a la pérdida. También se informa la cobertura de las señales emitidas. Un diagnóstico restringido a emisiones exitosas se acompaña de la evaluación de la política completa y de sus fallos. La falta de precio se distingue de la abstención o del fallo de inferencia.

## Períodos, purga y embargo

Los límites UTC satisfacen `train_from < development_from < evaluation_from < evaluation_until`. Definen `[train_from, development_from)`, `[development_from, evaluation_from)` y `[evaluation_from, evaluation_until)`. Se fijan por calendario y presupuesto muestral usando metadatos. Los grupos completos se forman antes de asignar los períodos.

La CLI de preparación utiliza `event_group_id`. Toma el comienzo y fin de las ventanas descriptivas del grupo y mantiene todas sus observaciones juntas. Los extremos se consideran cerrados para detectar contactos con cortes. En entrenamiento y desarrollo exige que el fin sea estrictamente anterior al límite superior menos `embargo_seconds`. En evaluación exige fin estrictamente anterior a `evaluation_until` y aplica **cero embargo al final de esa última partición**, porque no hay un bloque posterior en la propuesta. Los grupos que cruzan cortes o quedan fuera del período se excluyen con motivo explícito.

El futuro evaluador predictivo añadirá dependencias de features y `outcome_available_at`. Purgará del entrenamiento grupos que compartan identidad o cuyos intervalos de información/resolución se solapen con validación. El contacto exacto cuenta como solapamiento. Cada etiqueta de entrenamiento debe estar disponible antes del corte, incluso cuando un intervalo de precio ya haya terminado.

El embargo es una duración de tiempo anterior a cada bloque de validación y evaluación final. Si se expresa en sesiones, el calendario produce límites UTC guardados. La selección de variantes usa pliegues expansivos de desarrollo con períodos fijos, purga y grupos íntegros. El candidato y la lista de alternativas probadas se congelan antes del acceso final.

Desde `engine/`, la interfaz siguiente ilustra una propuesta con fechas sintéticas.

```bash
python -m calibration.particiones_macro \
  --report /tmp/report-v2.json \
  --fixture-root validation/fixtures/macro \
  --train-from 2030-01-01T00:00:00Z \
  --development-from 2031-01-01T00:00:00Z \
  --evaluation-from 2032-01-01T00:00:00Z \
  --evaluation-until 2033-01-01T00:00:00Z \
  --embargo-seconds 86400
```

La CLI revalida informes completos v1/v2 y fixtures. Su salida `offline_partition_preview` propone pertenencia temporal de metadatos. El estado de elegibilidad y los precios pendientes siguen vigentes. La preparación conserva las ventanas descriptivas implementadas, mientras los tres contratos predictivos anteriores requieren implementación futura.

## Manifiesto congelado y evaluación registrada

La congelación debe proteger identidad del experimento y versión de esquema dentro del contenido resumido. El siguiente esquema describe campos sin miembros reales ni hashes calculados.

```json
{
  "manifest_sha256": "SHA-256 de los bytes canónicos de payload",
  "payload": {
    "schema_version": 1,
    "experiment_id": "identificador único e inmutable",
    "protocol_sha256": "hash del protocolo aprobado",
    "cohort": "historical_reconstruction o prospective",
    "created_at": "timestamp UTC de congelación",
    "frozen_by": "responsable de la operación explícita",
    "source_revision": "commit exacto",
    "catalog_sha256": "hash del catálogo de metadatos",
    "contracts_sha256": "hash de objetivos, anclas, unidades y precios",
    "universe_sha256": "hash de calendario y panel de instrumentos",
    "periods": "límites UTC, folds y embargo",
    "purge_policy": "intervalos y disponibilidad de etiquetas",
    "members": [
      {
        "observation_id": "ID sintético del esquema",
        "event_id": "ID sintético del esquema",
        "event_group_id": "ID sintético del esquema",
        "origin": "historical_reconstruction",
        "partition": "train, development o evaluation",
        "metadata_sha256": "hash del registro y sus intervalos"
      }
    ],
    "exclusions": "IDs y motivos ordenados",
    "evaluation_plan_sha256": "comparadores, métricas e inferencia"
  }
}
```

La serialización canónica usa UTF-8, claves ordenadas y separadores JSON compactos. Normaliza cadenas a NFC y timestamps a UTC con precisión fija. Los decimales usan cadenas canónicas. Rechaza claves duplicadas y números no finitos. Ordena miembros por `observation_id`, grupos por `event_group_id` y exclusiones por ID y motivo. El hash cubre `payload` completo, incluidos `schema_version` y `experiment_id`, y excluye únicamente el campo exterior que almacena el hash. Señales y desenlaces finales se conservan en artefactos de acceso separado.

1. **Preparar.** Revalidar metadatos, grupos y cobertura del calendario, y producir una propuesta sin consultar desenlaces. Resolver todos los parámetros del contrato antes de solicitar congelar una propuesta concreta.
2. **Congelar explícitamente.** Crear un archivo nuevo mediante escritura exclusiva que falle si el identificador ya existe. Guardar payload canónico, hash, commit, responsable y aprobación del protocolo. Preparar o evaluar nunca sustituye esta operación.
3. **Verificar.** Recalcular hashes y comprobar catálogo, grupos, snapshots, períodos y contratos contra la referencia congelada. Cualquier discrepancia aborta e identifica el elemento alterado. La verificación conserva el manifiesto original y no lo regenera.
4. **Seleccionar en desarrollo.** Registrar variantes, parámetros y semillas en los folds autorizados. Congelar el candidato elegido y su hash antes del primer acceso a etiquetas finales.
5. **Evaluar una vez.** Crear un registro exclusivo que vincule manifiesto, candidato, baselines, predicciones, código y precios. Registrar inicio antes de abrir etiquetas y resultado o fallo después. Un reintento solo completa la misma evaluación con hashes idénticos y conserva constancia del acceso previo.
6. **Cerrar.** Guardar el hash del informe y el estado consumido del conjunto final. Cambiar variante, horizonte o criterio exige otro experimento con evaluación todavía ajena a esas decisiones.

Agregar datos genera un catálogo y una cohorte posteriores sin reasignar membresía congelada. Una corrección de timestamp, grupo o etiqueta produce una enmienda que conserva la evidencia original y declara qué resultados invalida. Los resultados ya abiertos no recuperan condición de evidencia intacta mediante un cambio de nombre o hash. El registro versionado de solo adición aporta una referencia confiable para detectar reescrituras. Un registro prospectivo anexa recibos de predicciones y resoluciones al calendario y las reglas fijadas previamente.

## Estimando, bootstrap y multiplicidad

Cada contrato tiene un estimando propio. Para signo a cinco minutos es la reducción media de Brier. Para retorno a una y dos sesiones es la reducción media de MSE del retorno continuo. En los tres casos se calcula primero la diferencia pareada de pérdidas sobre el panel del `event_group_id` y después se promedia entre grupos con igual peso. La interpretación corresponde a un nuevo acontecimiento del calendario definido y al universo de instrumentos fijado.

La propuesta primaria exige el panel completo y conserva los grupos incompletos en cobertura y diagnóstico de disponibilidad. Esa regla se fija antes de consultar precios. Si se elige un estimando sobre instrumentos disponibles, se registra otra especificación y cómo cambia el panel. Los cuatro ETF de un anuncio siguen aportando un único grupo.

El bootstrap es pareado y conserva todas las observaciones del mismo `event_group_id`. Modelo y baseline mantienen etiquetas, anclas y precios comunes. Las predicciones fuera de muestra ya registradas quedan fijas durante las réplicas. El intervalo estima incertidumbre de la comparación de esos sistemas entrenados. Incluir variabilidad del entrenamiento exige repetir el procedimiento anidado completo dentro de cada réplica.

Para dependencia temporal adicional se propone remuestreo por bloques de meses consecutivos. Cada grupo pertenece íntegro al mes de su primer anuncio en la zona de mercado. Se extraen bloques contiguos de longitud `L` con reemplazo hasta completar el número de meses observado, conservando meses vacíos y todos los instrumentos de cada evento. Se recalcula en cada réplica el promedio por acontecimiento de la diferencia de Brier o MSE correspondiente. `L`, semilla, número de réplicas y método de intervalo se fijan con desarrollo y constan en el manifiesto.

El bootstrap simple por evento es una sensibilidad bajo independencia entre anuncios. La elección del método precede al acceso final. Con pocos eventos o bloques se declara resultado descriptivo y se reportan conteos efectivos. Las observaciones correlacionadas por instrumento no añaden grupos independientes.

Se publican casos, grupos, instrumentos, períodos, cobertura y diferencia pareada con su intervalo y unidades. Para afirmar éxito en cualquiera de los tres objetivos se predeclara uno como primario o un control de multiplicidad, como Holm sobre tres contrastes válidos preespecificados. Sus estadísticas siguen siendo distintas, Brier para signo y MSE para magnitud. Comparar varios baselines, pérdidas o variantes añade hipótesis que deben identificarse como confirmatorias o exploratorias antes de la evaluación.

## Plan de conexión y verificación

La etapa actual conserva la preparación de metadatos como operación local. Las futuras pruebas sintéticas deben cubrir grupos en fronteras, intervalos que se tocan, embargo temporal, sesiones cerradas y cutoff, igualdad de retornos, señal tardía, barras incompletas, baselines solo-entrenamiento, cambios de hashes y reintentos de evaluación.

La CLI de evaluación deberá exponer selección de desarrollo y evaluación final como operaciones explícitas. Ambas exigirán pertenencia por IDs del manifiesto. La final exigirá candidato congelado y registro de acceso. Usar `promover_anidado` aporta separación interna, pero aún requiere persistencia del reparto, intervalos y grupos. El nuevo cargador mantendrá `observation_id`, `event_group_id`, cohorte, contrato y disponibilidad de resultados, incluidos retornos cero.

La predicción de magnitud tendrá un camino de entrenamiento y selección propio. Brier y calibración probabilística corresponden al objetivo binario. El reajuste posterior con datos ya evaluados generará un artefacto identificado como entrenamiento posterior a evaluación, cuya siguiente validación utilizará otra cohorte.

Los comandos de auditoría incluyeron `git log` sobre los cuatro módulos, `git diff 0884e8a^ 0884e8a -- engine/calibration/walk_forward.py`, `git blame -L 236,246 -- engine/calibration/walk_forward.py` y `git diff 1c6108e^ 1c6108e -- engine/calibration/walk_forward.py`. La revisión usó código y datos sintéticos. El siguiente resultado revisable es una propuesta con los parámetros de precios, latencia, fechas, pérdidas e inferencia completos, seguida de la implementación y prueba de congelación explícita.
