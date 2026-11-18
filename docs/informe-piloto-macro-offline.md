# Inspección y piloto macroeconómico offline

Rubicón Lab · El Enjambre · 18 de noviembre de 2026

La inspección parte del commit `0af8a2f` de `claude/m-d-file-6z1e63`. El trabajo se prepara en `codex/piloto-macro-offline` para revisión antes de integrar. La misión de esta sesión es construir candidatos históricos trazables a partir de acontecimientos oficiales y comprobar su importación offline.

El principal hallazgo es que el cosechador actual elige días por la magnitud del movimiento posterior. Después busca una noticia asociada al símbolo. Por tanto, ampliar la cobertura de titulares por ticker resolvería solamente una parte del problema. La nueva vía debe seleccionar acontecimientos mediante un calendario definido de antemano y conservar los casos aunque su reacción posterior sea pequeña.

El piloto contiene dos acontecimientos y cuatro instrumentos por acontecimiento, ocho candidatos en dos grupos de correlación. La aceptación de sus metadatos significa que se puede reconstruir su procedencia y asociación económica. La elegibilidad para evaluar predicciones sigue bloqueada por precios intradía, contexto previo y protocolo de evaluación pendientes.

## Arquitectura inspeccionada

| Componente | Ruta | Contrato y comportamiento observado |
|---|---|---|
| Entrada de cosecha | `engine/server.py`, `api_cosechar` | Endpoint administrativo `/api/cosechar`. Inicia una tarea que puede guardar el catálogo remoto |
| Selección histórica | `engine/contenido/cosechador.py`, `dias_de_movimiento` | Descarga cierres diarios Yahoo, filtra por umbral absoluto de retorno y prioriza magnitudes grandes |
| Noticias | `engine/contenido/cosechador.py`, `_titular_de` | Consulta Alpaca/Benzinga con `symbols=simbolo`, descarta titulares genéricos y elige uno por proximidad temporal |
| Catálogo local | `engine/contenido/backtest_eventos.json` | Objeto JSON con lista `eventos` |
| Catálogo remoto | `engine/contenido/respaldo.py`, `cosecha_remota` | Lee `datos/cosecha.json` de la rama predeterminada `respaldo-datos` |
| Importación efectiva | `engine/contenido/backtest.py`, `cargar_eventos` | Fusiona catálogos por `id`. Los eventos locales prevalecen sobre los remotos |
| Ejecución histórica | `engine/contenido/backtest.py`, `correr_tanda` | Consulta precios y luego ejecuta el pipeline de simulación. Guarda fuente `backtest` y respalda cada caso |
| Persistencia | `engine/contenido/persistencia.py` | SQLite, tabla `simulaciones`, JSON de resumen, líderes y precios. `conectar` puede crear esquema y ejecutar migraciones |
| Precios | `engine/contenido/fuentes/yahoo.py`, `variacion_real`, y respaldo Alpaca | Retorno desde el cierre anterior a la fecha hasta el cierre de la segunda rueda, con horizonte predeterminado de dos ruedas |
| Export principal | `engine/contenido/respaldo.py`, `exportar_casos` | Casos planos con `sim_id`, `origen`, `fecha`, `titular`, símbolos, señales por arquetipo y `reaccion_real` |
| Export HTTP | `engine/server.py`, `api_calibracion_export` | `/api/calibracion/export` devuelve `n` y lista `casos`, protegido con token |
| Export alternativo | `engine/contenido/exportar_libreta.py` | Lista de señales, confianza, retorno real, categoría y fuente. Es otro contrato de salida |
| Guía operativa existente | `docs/runbook-ampliar-datos-indice.md` | Recomienda cosechar nueve ETFs desde 2016, ejecutar tandas LLM y descargar resultados |
| Pruebas pertinentes | `engine/validation/test_cosechador.py`, `test_backtest.py`, `test_respaldo.py` | Cubren selección actual, deduplicación, ejecución inyectable y exportación |
| Evaluación predictiva temporal | `engine/calibration/walk_forward.py` | Walk-forward, métricas fuera de muestra y variantes de promoción |
| Particiones | `engine/calibration/verificador.py` | Partición por hash y alternativa temporal con purga opcional |
| Métricas de probabilidad | `engine/contenido/calibracion.py` | Brier, log-loss y error de calibración ECE, usados por walk-forward |
| Incertidumbre | `engine/calibration/intervalos.py` | Bootstrap agrupado actualmente por activo |
| Predicciones prospectivas | `engine/contenido/pipeline.py`, `engine/contenido/persistencia.py` | Enganche al pipeline y tabla `predicciones`, con registro y resolución separados |
| Resolución prospectiva | `engine/contenido/resolver_predicciones.py` | Resuelve predicciones mediante precios y contrato diario |
| Benchmark computacional | `engine/calibration/benchmark_motor.py` | Medición de rendimiento computacional del motor |

## Diagnóstico del contrato actual

El evento cosechado conserva seis campos, `id`, `fecha`, `simbolo`, `categoria`, `mercado` y `titular`. La categoría deriva del retorno posterior. El recuperador obtiene fuente y URL, pero el constructor del evento descarta ambos. Tampoco conserva el timestamp de la noticia. Esto impide reconstruir qué información estaba disponible en el instante de un anuncio.

La dependencia de ticker viene del filtro de símbolos de Alpaca/Benzinga. El código inspeccionado carece de una comprobación de mención literal del ticker dentro del titular. El cuello de botella corresponde a cobertura y etiquetado del proveedor.

La búsqueda abarca desde el día anterior hasta el final del día seleccionado. La proximidad se calcula frente a medianoche UTC, aunque el comentario menciona el cierre. Una reconstrucción intradía requiere conservar y validar el momento exacto de disponibilidad.

La selección por grandes movimientos está presente en `cosechador.py`, tanto al formar los candidatos como al aplicar el tope por instrumento. La separación declarada como cinco ruedas se implementa mediante diferencia de días calendario. Los tests actuales comprueban el comportamiento de selección por magnitud.

La importación remota en `backtest.cargar_eventos` verifica únicamente que existan `id`, `titular` y `simbolo`. El resto del contrato se presupone. El catálogo remoto se fusiona por `id` y prevalece lo nuevo al guardarlo. Al leerlo junto con el catálogo local, prevalece lo local. La opción `reemplazar=True` sustituye el catálogo remoto guardado.

La identidad del catálogo y la identidad de una simulación difieren. El ID de cosecha contiene fecha, mercado y símbolo. El ID persistido de simulación es un hash de titular y semilla, y la semilla histórica deriva de la fecha. Dos instrumentos asociados al mismo comunicado y fecha pueden compartir `sim_id`. La persistencia usa `INSERT OR REPLACE`, y el respaldo deduplica por `sim_id`. Integrar varios instrumentos necesita una identidad de observación separada y explícita.

El campo `fecha` de las simulaciones y del export corresponde al momento de ejecución. La fecha del acontecimiento debe recuperarse de otra procedencia. El export principal incluye históricos y destacadas en vivo con un campo `origen` que permite distinguirlos. Esa distinción debe conservarse durante cualquier análisis posterior.

El retorno entre cierres diarios contiene información de muchas horas y otros acontecimientos. Una ventana alrededor de un comunicado requiere precios con timestamps y convenciones explícitas. La asociación temporal observada tampoco establece por sí sola impacto causal.

## Piloto implementado

La nueva entrada está en `engine/contenido/cosechador_macro.py`. Utiliza JSON y biblioteca estándar, genera su informe por la salida estándar y funciona sobre archivos locales. Los fixtures están en `engine/validation/fixtures/macro/events.json`, acompañados por extractos de fuentes oficiales en `sources/`.

Cada acontecimiento conserva identificador, grupo de correlación, tipo, fuente primaria, timestamp con offset, zona IANA, momento de disponibilidad, datos del anuncio, exposición por instrumento, ventana de medición, versión del extractor, hash del extracto y estado de validación. Los datos conocidos previamente tienen su propio bloque y su momento de disponibilidad.

| Acontecimiento | Publicación local | Publicación UTC | Instrumentos propuestos |
|---|---|---|---|
| CPI estadounidense de agosto de 2024 | 11 de septiembre de 2024, 08:30, `America/New_York` | 12:30 UTC | SPY, QQQ, DIA, IWM |
| Decisión FOMC | 18 de septiembre de 2024, 14:00, `America/New_York` | 18:00 UTC | SPY, QQQ, DIA, IWM |

La fuente BLS registra CPI general mensual de 0,2%, interanual de 2,5%, subyacente mensual de 0,3% e interanual de 3,2%. La fuente Fed registra un recorte de 0,5 puntos porcentuales y rango objetivo de 4,75–5,00%. Los extractos conservan los fragmentos utilizados y su hash. [Comunicado BLS](https://www.bls.gov/news.release/archives/cpi_09112024.htm) · [Comunicado Fed](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a.htm)

Estos archivos publicados en 2024 se recuperaron mediante Firecrawl en 2026, con información de caché incluida en la procedencia. Acreditan el contenido observado del archivo oficial en la recuperación actual. Una auditoría de versiones históricas debe comprobar revisiones y disponibilidad contemporánea. La extracción reportó un consumo total de dos créditos Firecrawl.

`source_verified` expresa la revisión manual de estos dos fixtures contra sus extractos. El validador comprueba estructura, coherencia temporal e integridad SHA-256. La comprobación automática de cifras y horarios frente al texto fuente queda pendiente para futuros extractores. Cada dato añadido a `known_before` necesitará evidencia archivada de su disponibilidad anterior. Los dos acontecimientos fueron propuestos para este piloto y constituyen una muestra de desarrollo del importador.

El bloque `known_before` está vacío con una razón explícita. Las referencias retrospectivas incluidas en el propio comunicado se conocen en este fixture al publicarse el anuncio. El campo `expected` es nulo porque falta una fuente fechada de consenso de mercado anterior al anuncio. Completar ambos requiere datos verificables, y calcular una sorpresa respecto del consenso exige especificar su definición previamente.

Se propone como ventana descriptiva desde un minuto antes hasta cinco minutos después del anuncio. Es una decisión de diseño del piloto que deberá fijarse en el protocolo antes de consultar retornos. El CPI exige cobertura de sesión extendida, ya que se publica antes de la apertura regular. Los precios y su proveedor permanecen pendientes.

La ventana FOMC puede captar simultáneamente el comunicado y otras publicaciones de la reunión, incluidas proyecciones económicas. Cualquier interpretación del movimiento debe considerar ese conjunto de información. La deduplicación actual usa URL canónica, instante UTC, instrumento y horizonte, normalizando fragmentos, puerto HTTPS predeterminado y parámetros de seguimiento. Ampliar las fuentes requiere registrar equivalencias entre comunicados replicados en URLs distintas.

La expansión a cuatro ETFs conserva un mismo grupo por acontecimiento. Por tanto, los ocho candidatos representan dos acontecimientos para la agrupación. Las futuras particiones temporales y el bootstrap deberán respetar esos grupos, además de comprobar ventanas solapadas.

El resumen versionado de la ejecución está en `docs/piloto-macro-resultado.json`, identificado mediante `mode="offline_summary"`. Registra conteos, candidatos, aceptación o rechazo de metadatos, motivos y bloqueos de elegibilidad. Omite repeticiones de los acontecimientos completos, cuya fuente es el fixture `events.json`. La salida completa de la CLI se puede guardar en `/tmp/macro-report.json` y utilizar como entrada de `--existing` para comprobar una segunda importación. El resumen versionado sirve como evidencia de revisión y tiene un formato diferente del informe completo requerido por `--existing`.

La ejecución del piloto produce ocho candidatos, con dos grupos, y cero casos elegibles para evaluación mientras los requisitos metodológicos sigan pendientes.

## Pruebas y comandos de esta sesión

El entorno local usa Python 3.12.14 y un entorno virtual en `/workspace/work/venv`. La revisión se efectuó sobre una clonación local, con dependencias fijadas para esa ejecución.

La línea base de pruebas pertinentes terminó con **83 pruebas aprobadas en 53,96 segundos**. La guardia de red registró cero intentos de conexión durante esas pruebas. Aparecieron cuatro avisos de dependencias o deprecación, tres por `utcfromtimestamp` en `fuentes/yahoo.py` y uno de Starlette relacionado con `httpx`.

Se instalaron las versiones fijadas mediante los siguientes comandos desde la raíz del repositorio.

```bash
python -m venv /workspace/work/venv
/workspace/work/venv/bin/python -m pip install -r engine/requirements-dev.txt
```

La comprobación final reutilizó un lanzador temporal en `/workspace/work/run_offline_tests.py`. Retira credenciales del proceso, desactiva plugins externos de pytest, bloquea sockets y DNS y fija `ENJAMBRE_DB` en un directorio temporal. Ejecuta pytest desde `engine/` con esta selección.

```bash
/workspace/work/venv/bin/python /workspace/work/run_offline_tests.py -q \
  validation/test_cosechador.py validation/test_backtest.py \
  validation/test_benchmark_motor.py validation/test_walk_forward.py \
  validation/test_verificador.py validation/test_predicciones.py \
  validation/test_resolver_predicciones.py validation/test_pipeline_prediccion.py \
  validation/test_intervalos.py validation/test_contaminacion_temporal.py \
  validation/test_remedir_sin_fuga.py validation/test_respaldo.py \
  validation/test_cosechador_macro.py
```

La suite nueva tiene 45 pruebas. Incluye ejecución CLI con sockets y SQLite bloqueados, fechas con offset y horario estacional, campos obligatorios, fuga temporal, integridad de extractos, reimportaciones, alias de fuentes, inconsistencias del mismo acontecimiento y números no finitos. El lanzador y los logs son archivos temporales de esta sesión. En otro checkout, la selección se puede repetir desde `engine/` mediante `python -m pytest` con los mismos argumentos.

La CLI se ejecutó desde `engine/` con estos comandos.

```bash
/workspace/work/venv/bin/python -B -m contenido.cosechador_macro \
  --input validation/fixtures/macro/events.json > /workspace/work/macro-report.json
/workspace/work/venv/bin/python -B -m contenido.cosechador_macro \
  --input validation/fixtures/macro/events.json \
  --existing /workspace/work/macro-report.json > /workspace/work/macro-reimport.json
```

La primera ejecución aceptó ocho candidatos y rechazó cero. La segunda aceptó cero y rechazó ocho por duplicación, conservando los ocho casos preparados. Ambas mantuvieron dos grupos y cero casos elegibles. El resumen versionado se deriva de estos JSON y conserva los registros aceptados sin repetir el objeto `event` y su vista heredada, además de las razones de rechazo en la reimportación.

Se inspeccionaron archivos con `rg`, `sed` y lecturas de texto. `git ls-tree`, `git log` y scripts de extracción de metadatos permitieron comprobar la rama de respaldo. La revisión de particiones y sus pruebas usó código y casos sintéticos. La carga del baseline por una prueba existente comprobó su estructura. Los resultados del holdout quedaron fuera de la selección de decisiones de este piloto.

La corrida integrada aprobó 123 pruebas en 52,54 segundos, con los mismos cuatro avisos preexistentes y cero intentos de conexión. Después de endurecer el manejo de JSON y añadir regresiones, se repitió toda la suite nueva mediante `python /workspace/work/run_offline_tests.py -q validation/test_cosechador_macro.py`, con 45 aprobadas en 0,38 segundos y cero intentos de conexión. En conjunto quedaron verificadas 83 pruebas existentes y 45 nuevas. Los logs se conservaron durante esta sesión en `/workspace/work/final-tests.log` y `/workspace/work/final-macro-tests.log`.

`git diff --cached --check` pasó. El diff contiene siete archivos añadidos, correspondientes al módulo, pruebas, fixtures, extractos y los dos informes. La revisión y el commit se prepararon en la rama de trabajo.

## Estado del contexto previo

| Afirmación previa | Evidencia inspeccionada y alcance |
|---|---|
| Aproximadamente 10.150 inversionistas sintéticos | `engine/config/agentes.json` declara `total_agentes=10150`. `CLAUDE.md` documenta 1.150 líderes y nueve arquetipos |
| 617 casos históricos y aproximadamente 165 índices | El informe del 18 de noviembre documenta ese corte. El respaldo disponible corresponde a otro snapshot, detallado abajo |
| Cerca de 63% en índices y 50,6% agregado | La documentación registra 62,7% en índices, 77,4% en alta convicción y 50,6% agregado. Esta sesión no recalculó esos resultados |
| Sesgos de selección corregidos | Hay código para evaluación temporal y remedir retornos, pero el cosechador sigue seleccionando grandes movimientos posteriores |
| Baseline y walk-forward corregidos | Existe baseline calculado sobre entrenamiento y promoción anidada. La CLI actual continúa llamando a `promover`, que selecciona y reporta sobre el mismo conjunto fuera de muestra |
| Holdout congelado | Existe separación temporal y una función de promoción anidada. La partición por porcentaje se vuelve a calcular en cada ejecución. Falta un manifiesto persistido que permita acreditar un holdout congelado al ampliar datos |
| Brier, log-loss y calibración | Implementadas en `contenido/calibracion.py` y usadas en `calibration/walk_forward.py` |
| Registro prospectivo | Implementado con tabla propia, enganche en el pipeline y resolvedor. El despliegue real y el contenido de la base productiva quedan fuera de esta inspección de código |

La rama `respaldo-datos` inspeccionada apunta a `b44d454c509764ad195f104fb4bd7929fdd8a546`, fechado el 24 de septiembre de 2026. Su `datos/calibracion.json`, generado ese día, contiene 670 casos, de los cuales 609 tienen origen `historico` y 61 `en_vivo`. Hay 670 `sim_id` únicos. Entre los históricos, 168 corresponden a los ETFs de índice de la watchlist, distribuidos en SPY 73, QQQ 45, DIA 26, IWM 19, VTI 3 y VOO 2. El campo `mercado` está ausente en estos registros, por lo que el recuento de índice procede de sus símbolos.

En la misma rama, `datos/cosecha.json`, generado el 3 de agosto, contiene 1.614 eventos y 189 con mercado `indice`. El total se distribuye en 172 de oro, 189 de índices, 124 de petróleo, 904 de acciones y 225 de cripto. Las fechas de acontecimientos van del 11 de enero de 2016 al 29 de julio de 2026.

Estos conteos de metadatos proceden de un respaldo anterior al informe del 18 de noviembre. Las diferencias con 617/165 corresponden a cortes distintos y no permiten inferir el tamaño actual de la base productiva. La inspección contó identificadores, símbolos, orígenes y fechas sin evaluar desenlaces.

La evaluación tiene dos brechas relevantes para esta ampliación. `walk_forward.cargar` descarta la identidad de grupos, y el bootstrap en `intervalos.py` agrupa por activo. Ninguno garantiza actualmente mantener juntos los instrumentos del mismo anuncio. `verificador.particionar_temporal` ofrece purga opcional, y `promover_anidado` ofrece separación de desarrollo y holdout, pero el manifiesto persistido, el bootstrap por acontecimiento y el cambio de entrada CLI siguen pendientes. `docs/plan-evolucion-enjambre.md` ya reconoce parte de estas tareas.

| Componente de evaluación | Ruta y alcance |
|---|---|
| Benchmark computacional | `engine/calibration/benchmark_motor.py` mide rendimiento y reproducibilidad del motor sin IA |
| Evaluación temporal | `engine/calibration/walk_forward.py` implementa ventanas expansivas, baseline de entrenamiento y promoción anidada |
| Particiones | `engine/calibration/verificador.py` contiene reparto por hash heredado y partición temporal con purga opcional por grupo y embargo medido en filas |
| Ventanas históricas | `engine/calibration/remedir_sin_fuga.py` usa cierres diarios posteriores a la fecha base |
| Incertidumbre | `engine/calibration/intervalos.py` contiene bootstrap agrupado por activo |
| Métricas probabilísticas | `engine/contenido/calibracion.py` implementa Brier, log-loss y calibración |
| Comparación entre períodos | `engine/calibration/contaminacion_temporal.py` compara eras históricas. La fecha de entrenamiento del LLM requiere evidencia adicional |
| Registro prospectivo | `engine/contenido/persistencia.py`, `engine/contenido/pipeline.py` y `engine/contenido/resolver_predicciones.py` cubren registro, enganche y resolución |

El registro prospectivo conserva modelo, semilla y fuentes mediante `pipeline._registrar_prediccion_prospectiva`, pero faltan hashes de código y prompts para reproducibilidad completa. El tablero de `persistencia.resumen_predicciones` presenta acierto y cobertura sobre una consulta limitada a 500 filas. El resolvedor utiliza un contrato de precios diarios basado en la fecha de `as_of`, que debe especificarse antes de incorporar anuncios intradía. La existencia del código acredita su implementación, y la verificación del despliegue requiere evidencia operativa adicional.

La evidencia ya contrastada confirma la existencia del cosechador, exportación, respaldo remoto y runbook de ampliación. La watchlist incluye nueve ETFs de índices. El filtrado por movimientos posteriores sigue presente en el cosechador y exige tratar esta vía como una nueva muestra con criterios propios.

Las cifras de precisión documentadas describen evaluaciones previas. Esta sesión prepara y valida datos de entrada. Cualquier afirmación predictiva necesita un protocolo temporal reproducible, comparación incremental contra baselines y validación prospectiva. Un LLM actual puede haber incorporado información sobre acontecimientos históricos durante su entrenamiento.

## Plan técnico priorizado

1. Revisar el diff y aprobar el contrato del piloto. Fijar calendario de inclusión por tipo de anuncio y fechas, universo de instrumentos y ventana antes de consultar movimientos. Registrar revisiones del protocolo.
2. Incorporar fuentes previas verificables para contexto y consenso. Conservar timestamp, versión o vintage y procedencia por dato. Para cada variable, justificar si el consenso es necesario para la hipótesis que se evaluará.
3. Seleccionar proveedor de precios intradía, confirmar cobertura histórica de 2024 y sesión extendida para CPI, y documentar costo, licencia, ajustes, timestamps y convención de barras. Rechazar ventanas incompletas con motivos reproducibles.
4. Diseñar identidad de observación independiente del `sim_id` actual y preservar metadatos en importación y exportación. Resolver explícitamente el caso de un comunicado asociado a varios instrumentos.
5. Implementar evaluación agrupada por acontecimiento, orden temporal y control de solapamientos. Congelar decisiones antes de cualquier nueva evaluación y mantener la trazabilidad de la muestra.
6. Ampliar acontecimientos por calendario completo con el mismo extractor y criterios. Ejecutar pruebas de cobertura y duplicación. Evaluar incertidumbre por grupos y conservar la categoría de reconstrucción histórica.
7. Vincular las conclusiones históricas con un protocolo prospectivo cuyos registros antecedan al desenlace. Determinar el valor incremental del sistema con métricas y baselines definidos de antemano.

El próximo paso recomendado es revisar el contrato y aprobar la fuente y el presupuesto de precios intradía para completar estos dos acontecimientos. La integración de la rama, los cambios de contrato productivo, cualquier migración, despliegue o ejecución LLM requieren aprobación específica. El diff de esta sesión debe revisarse antes de integrar.
