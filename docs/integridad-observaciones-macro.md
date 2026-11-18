# Identidad de las observaciones macro y revisión del piloto

El mismo comunicado aplicado a cuatro ETF produjo cuatro observaciones y un solo identificador de simulación heredado. Una simulación compartida tiene sentido si los cuatro instrumentos reciben la misma señal. El problema aparece al guardar el retorno de cada instrumento en la misma fila. La propuesta conserva una fila lógica por observación y reserva un identificador distinto para cada ejecución efectiva del motor.

## Qué se revisó

El 18 de noviembre de 2026 se verificó en GitHub el [PR 34](https://github.com/mastergio1/ENJAMBRE-AI-AGENTS/pull/34). Estaba abierto en borrador y sin fusionar. La base `claude/m-d-file-6z1e63` apuntaba a `0af8a2f4e3204710ec700353de23a37575c4e5a6`. La rama `codex/piloto-macro-offline` tenía un commit propio, `8d8053e9299af81a5c5b65f187212e657b901c80`, y cero commits de retraso. La revisión cubrió las 1.543 líneas añadidas en los siete archivos del diff: módulo, pruebas, fixture JSON, extractos CPI/FOMC, resumen JSON e informe. Los hashes de los extractos y las ocho identidades concordaban. Se reprodujo el resumen del piloto frente a la salida completa.

El trabajo de esta sesión parte del commit del piloto, en `codex/integridad-evaluacion-macro`. Los números de línea del diagnóstico siguiente corresponden al **commit revisado 8d8053e**, para que las referencias sigan siendo verificables.

| Riesgo observado | Ruta y línea en el piloto | Consecuencia |
|---|---|---|
| Semilla por fecha e identidad por titular y semilla | `engine/contenido/backtest.py:65`, `:70`, `engine/contenido/persistencia.py:178` | Una prueba con cuatro símbolos y el mismo titular produce la misma clave cuatro veces. Añadir otro horizonte tampoco cambia esa clave. Es una colisión por construcción. |
| Una fila reemplazable y un resultado por simulación | `engine/contenido/persistencia.py:20`, `:191`, `:203`, `:430`, `engine/contenido/backtest.py:109` | El guardado confirma la fila antes de adjuntar la reacción. Otro resultado puede sustituir al anterior, o la comprobación de pendientes puede dar por resuelta otra observación. |
| Proyección histórica admitida antes de validar categoría | `engine/contenido/cosechador_macro.py:245`, `engine/contenido/backtest.py:46`, `:163`, `:169`, `:175` | La ruta original, probada con funciones simuladas, llamó al simulador y al guardado antes de fallar por falta de `categoria`. |
| Export breve y fusión con pérdida de multiplicidad | `engine/contenido/exportar_libreta.py:21`, `engine/contenido/respaldo.py:161`, `:191` | El export breve carece de identidad por instrumento y horizonte. El respaldo sustituye por `sim_id`. La fecha exportada es la de guardado. Una reconstrucción histórica y una predicción prospectiva necesitan procedencias independientes. |
| Variantes elegidas por su propio resultado de validación | `engine/calibration/walk_forward.py:52`, `:80`, `:126`, `:156`, `:240` | El cargador pierde los grupos. Los cortes usan filas y la CLI elige entre seis configuraciones usando el mismo conjunto en el que compara al ganador. |
| Incertidumbre y reserva final | `engine/calibration/intervalos.py:26`, `:40`, `engine/calibration/verificador.py:51`, `engine/calibration/walk_forward.py:170` | El bootstrap por símbolo separa cuatro ETF de un mismo anuncio. La promoción anidada vuelve a calcular la cola del conjunto por porcentaje cuando se añaden filas. |

## Contrato de identidad

| Campo | Significado y regla |
|---|---|
| `event_id` | Identificador editorial permanente del comunicado original. En el piloto, URL primaria canónica e instante UTC deben corresponder a un único ID en el acumulado. Un cambio de ticker, despliegue o semilla no crea un acontecimiento. |
| `event_group_id` | Unidad de dependencia estadística. Todos los instrumentos, horizontes y repeticiones de un acontecimiento comparten grupo. Varios comunicados simultáneos pueden recibir el mismo grupo mediante una regla editorial previa. Se conserva el alias histórico `correlation_group`. |
| `observation_id` | Clave única de `[event_id, symbol, horizon]`, serializada como JSON compacto UTF-8 y resumida mediante SHA-256 con prefijo `macro-`. Es idéntica al `case_id` del piloto. El horizonte identifica una convención de medición versionada. Cambiar símbolo u horizonte crea otra observación. La versión v2 todavía solo admite la ventana descriptiva del piloto. |
| `simulation_id` | Identificador de **una ejecución efectivamente iniciada**. Se exporta como `null` durante la preparación offline. Para integración se propone asignar un UUID por ejecución, conservar un identificador de petición para reintentos y registrar semilla, versión de código, modelo, inputs, origen y hora. Un reintento de la misma petición recupera la ejecución asociada. Una repetición experimental deliberada recibe un UUID nuevo. |

**Compatibilidad.** El fixture de anuncios sigue en v1. La CLI emite informes completos v2 y puede reimportar un informe completo v1 en memoria. Valida las filas, los campos derivados, la identidad canónica y la concordancia entre los aceptados y el acumulado. Entrega el mismo ID v1 para cada observación original. Un resumen de revisión `offline_summary` no contiene el inventario completo. Si falta una correspondencia fiable en los exports históricos, se conserva el `sim_id` original con su procedencia y el registro queda pendiente para análisis agrupado. Ni el símbolo ni la fecha de simulación bastan para asignarle un grupo.

**Primer cambio implementado.** Los informes de preparación validan la identidad al reimportarse. Las entradas históricas del backtest y del walk-forward rechazan lotes identificados como macro o agrupados antes de simular, guardar una simulación o construir etiquetas para un ajuste. El camino de planificación temporal acepta exclusivamente informes de preparación revalidados, exporta los cuatro identificadores y devuelve la razón de cada exclusión. Los nombres `train`, `development` y `evaluation` expresan el período que correspondería al grupo en la vista previa. Los ocho casos del piloto conservan `evaluation_ready=false` y `simulation_id=null`.

**Alcance.** El registro de equivalencias de IDs es el acumulado suministrado en `--existing`. Para deduplicar entre trabajos independientes habrá que compartir un inventario de fuentes y equivalencias, incluidas URLs alternativas de una publicación. Un hash del extracto comprueba integridad de bytes. La hora de publicación y las cifras de los fixtures se revisaron contra esos extractos. Antes de construir entradas para el motor habrá que proyectar explícitamente los campos disponibles a la hora de la predicción.

**Integración propuesta, pendiente de aprobación.** Una tabla de ejecuciones inmutables, otra de observaciones y una relación `(observation_id, simulation_id)` permiten vincular una ejecución común a varios instrumentos y conservar repeticiones. Los desenlaces pertenecen a `observation_id` con versión de proveedor y de etiqueta. El origen histórico o prospectivo debe concordar en ambos extremos de cada vínculo. Claves únicas y transacciones deben hacer idempotentes los reintentos concurrentes. Una discrepancia para la misma observación abre una revisión en lugar de reemplazar el valor. El export nuevo debe mantener identidad, ventana, origen y vínculos, con verificación de ida y vuelta. Los consumidores del export plano pueden continuar en su versión actual. La migración requerirá un ensayo sobre copia aislada, inventario de correspondencias ambiguas y conciliación de conteos antes de autorizar una escritura real.

El [protocolo de evaluación](protocolo-evaluacion-macro.md) especifica los objetivos a cinco minutos y a una o dos sesiones, sus baselines, la agrupación, el embargo y el diseño del manifiesto. La congelación de una membresía real, la lectura de desenlaces finales, cualquier cambio en la CLI de promoción para datos reales y la integración operativa se reservan para decisiones posteriores.

## Comprobaciones y reproducción

Se consultó la ficha del PR 34 en GitHub, se actualizaron referencias con `git fetch origin` y se revisaron los archivos del diff completo. Los siguientes comandos permiten identificar exactamente las revisiones y comprobar la diferencia.

```bash
git rev-list --left-right --count origin/claude/m-d-file-6z1e63...origin/codex/piloto-macro-offline
git diff --stat 0af8a2f...8d8053e
git diff --check 0af8a2f...8d8053e
git diff 0af8a2f...8d8053e
git diff 8d8053e...origin/codex/integridad-evaluacion-macro
```

Las pruebas se ejecutaron en Python 3.12 con las dependencias fijadas por el proyecto. La primera corrida usó el checkout intacto del piloto, la segunda el árbol de trabajo separado. El lanzador temporal `/workspace/work/validate_offline.py` llamó a pytest desde el directorio `engine/`, con SQLite temporal, credenciales retiradas y supervisión de red, archivos protegidos y procesos Python hijos. Añadió `-p no:cacheprovider` y `--deselect=validation/test_verificador.py::test_baseline_carga_y_tiene_claves`. Esa única prueba abre el archivo real de referencia. Los tests de promoción, purga, métricas y resolución que sí se ejecutaron usan datos sintéticos.

La selección exacta de archivos y las dos invocaciones se expresan aquí con una variable de Bash para facilitar su repetición.

```bash
suites=(
  validation/test_cosechador_macro.py
  validation/test_cosechador.py
  validation/test_backtest.py
  validation/test_benchmark_motor.py
  validation/test_walk_forward.py
  validation/test_verificador.py
  validation/test_predicciones.py
  validation/test_resolver_predicciones.py
  validation/test_pipeline_prediccion.py
  validation/test_intervalos.py
  validation/test_contaminacion_temporal.py
  validation/test_remedir_sin_fuga.py
  validation/test_respaldo.py
)
/workspace/work/venv/bin/python /workspace/work/validate_offline.py \
  --repo /workspace/work/ENJAMBRE-AI-AGENTS --guard-log /workspace/work/pilot-baseline-guard.jsonl \
  -q "${suites[@]}"
/workspace/work/venv/bin/python /workspace/work/validate_offline.py \
  --repo /workspace/work/integridad --guard-log /workspace/work/integridad-suite-guard.jsonl \
  -q "${suites[@]}" validation/test_particiones_macro.py
```

Para repetir la misma selección desde `engine/` en otro entorno aislado de servicios y secretos, con las dependencias de `requirements-dev.txt` instaladas y las variables de la lista anterior definidas, el comando de pytest es el siguiente.

```bash
python -m pytest -q -p no:cacheprovider \
  --deselect=validation/test_verificador.py::test_baseline_carga_y_tiene_claves \
  "${suites[@]}" validation/test_particiones_macro.py
```

En el piloto original pasaron **127 pruebas en 55,46 segundos**. En la rama de integridad pasaron **201 en 56,50 segundos**. Ambas corridas excluyeron la misma prueba de lectura del baseline real y emitieron los mismos cuatro avisos preexistentes, tres de `datetime.utcfromtimestamp` en `fuentes/yahoo.py:299` y uno de Starlette sobre `httpx`. En cada corrida la guardia supervisó seis procesos Python, con cero intentos registrados de conexión de red o lectura de archivos protegidos. Los logs de la sesión fueron `/workspace/work/pilot-baseline-tests.log` y `/workspace/work/integridad-suite.log`.

Además se probaron los puntos de entrada reales en tres invocaciones sucesivas. Se usaron los dos fixtures ya existentes y se eligieron fechas ilustrativas que sitúan ambos anuncios en entrenamiento. Los cortes y el embargo de este ejemplo sirven para probar el recorrido de archivos. El experimento futuro requiere definir sus propios períodos.

```bash
cd engine
/workspace/work/venv/bin/python -B -m contenido.cosechador_macro \
  --input validation/fixtures/macro/events.json > /workspace/work/integridad-report.json
/workspace/work/venv/bin/python -B -m contenido.cosechador_macro \
  --input validation/fixtures/macro/events.json --existing /workspace/work/integridad-report.json \
  > /workspace/work/integridad-retry.json
/workspace/work/venv/bin/python -B -m calibration.particiones_macro \
  --report /workspace/work/integridad-retry.json --fixture-root validation/fixtures/macro \
  --train-from 2024-01-01T00:00:00Z --development-from 2025-01-01T00:00:00Z \
  --evaluation-from 2026-01-01T00:00:00Z --evaluation-until 2027-01-01T00:00:00Z \
  --embargo-seconds 300 > /workspace/work/integridad-preview.json
```

La importación inicial aceptó 8 casos en 2 grupos. La repetición rechazó los 8 duplicados y conservó íntegro el acumulado. La vista temporal devolvió las 8 observaciones con sus grupos y 0 aptas para puntuación. Las pruebas específicas ejercitan además cruces de período, ventanas cuyo precio final toca exactamente el corte, embargo en segundos, retornos sintéticos del flujo histórico y rechazo previo a precios, simulación o guardado.
