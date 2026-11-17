# Análisis en frío — Auditoría predictiva (Propuesta 4)

*Rubicón Lab · El Enjambre · 2026-11-17. Análisis independiente de la "Auditoría
técnica de El Enjambre" (arquitectura y predicción), contrastada línea por línea
contra el código ACTUAL del repositorio (rama desplegada, HEAD con el badge de
convicción). Sin sesgo a favor ni en contra: se verifica cada afirmación.*

## Resumen ejecutivo

Es la **mejor de las cuatro auditorías** recibidas. A diferencia de las
anteriores:

1. **Sus afirmaciones sobre el código son exactas.** Verifiqué las 5 principales
   una por una; las 5 describen correctamente el código actual (no una versión
   vieja).
2. **Sus fuentes son reales.** Verifiqué la que parecía inventada (arxiv
   2606.11816, "WorldReasoner", Cambridge 2026): **existe**, es de este año y
   trata exactamente del problema que la auditoría señala como más grave. Las
   otras tres (Gneiting-Raftery 2007, Hewamalage 2022, López de Prado) son obras
   reales y pertinentes.
3. **No contradice lo que construimos; lo extiende.** Converge con todo lo ya
   hecho: señal > precio, gating por convicción, medición honesta, rigor de
   calibración.

**Pero** (y esto es lo central para la decisión): **nada de esto es para el
sábado.** Es una hoja de ruta de investigación de ~6 semanas, post-evento. El
demo del sábado no necesita ninguna de estas mejoras.

Y hay **un hallazgo nuevo que sí importa de verdad** (Problema 4): la posible
contaminación temporal por memoria del LLM. Es el único punto que podría afectar
nuestra cifra honesta de "~63% en índice", y conviene probarlo antes de apoyarnos
demasiado en ese número frente a inversionistas sofisticados.

---

## Veredicto por afirmación (verificado contra el código)

| # | Afirmación de la auditoría | Veredicto | Estado |
|---|---|---|---|
| P1 | 1.000 líderes comparten ~110 cerebros → diversidad visual, no cognitiva | **CORRECTO** | Diseño intencional (presupuesto), no bug |
| P2 | La confianza declarada pondera consenso e influencia → amplifica el error convencido | **CORRECTO y preciso** | Idea fuerte, salvageable |
| P3 | El cosechador selecciona días de mayor movimiento → sesgo de selección | **CORRECTO** | **Ya lo encontramos y documentamos (es LA FUGA)** |
| P4 | `cerebro.py` manda "Titular de hoy" sin fecha → el LLM puede recordar el desenlace | **CORRECTO y NUEVO** | **Lo más importante. No lo habíamos tratado.** |
| P5 | `evaluar()` usa `tasa_base(y_te)` (etiquetas del test) para el baseline | **CORRECTO y preciso** | Real pero menor y *conservador*; fix trivial |

### P1 — Cerebros compartidos (CORRECTO, pero es diseño, no defecto)

`engine/brains/reparto.py` efectivamente reparte ~110 cerebros entre los líderes
(ahora 1.150, no 1.000 como dice la auditoría — dato menor desactualizado). La
observación "mil líderes ≠ mil opiniones independientes" es **verdadera**, y el
propio código lo dice en su docstring: *"La diversidad de opinión vive en los
arquetipos + el muestreo del modelo, no en repetir 1.000 veces la misma
personalidad."*

Es una **decisión de presupuesto consciente** (CLAUDE.md §2.7: ~100-120 llamadas
por simulación). La sugerencia de experimentar con 110/220/400 cerebros es
razonable **pero cuesta dinero**: cada cerebro extra es una llamada LLM más por
simulación. Salvageable como experimento medido post-evento, con tope de costo.

### P2 — La confianza amplifica errores (CORRECTO — idea fuerte)

Verificado en `engine/model.py`:
- Consenso = Σ(señal·confianza) / Σ(confianza) (líneas 457-463).
- Influencia sobre seguidores = señal·confianza·0.7·sensibilidad (línea 508).
- Apuesta individual = |señal|·confianza·0.4·capital (`agents/lider.py:36`).

La confianza declarada por un LLM **no es** su probabilidad empírica de acertar.
Ponderar por ella puede dar más peso al error más convencido. La solución
propuesta —confianza efectiva = α·declarada + (1-α)·histórica, por
arquetipo/mercado/tipo de noticia— es **metodológicamente sólida** y encaja con
la "memoria de errores por arquetipo" que la misma auditoría propone después.
**Salvageable, prioridad alta post-evento.**

### P3 — Sesgo de selección del cosechador (CORRECTO — pero ya lo sabíamos)

`engine/contenido/cosechador.py:181` ordena por `abs(cambio_dia)` descendente y
filtra por umbral: selecciona **días de gran movimiento**. Esto es exactamente
**la fuga de selección que ya identificamos, medimos y documentamos** en sesiones
previas:
- `engine/calibration/remedir_sin_fuga.py` (re-medición SIN fuga).
- `docs/baseline-calibracion-fase0.md` y `docs/analisis-propuesta-gating-tono.md`.
- Resultado honesto ya conocido: agregado ~50% (azar), **índice ~63%** (señal
  real), el resto sin dirección en el texto.

Lo **nuevo y salvageable** de esta auditoría: separar en **3 bancos** (ordinario
/ extraordinario / difícil) y reportar el acierto de cada uno, en vez de una
cifra global dominada por extremos. Buena idea, post-evento.

### P4 — Contaminación temporal por memoria del LLM (CORRECTO, NUEVO, IMPORTANTE)

Verificado en `engine/brains/cerebro.py:153`:
```python
messages=[{"role": "user", "content": f"Titular de hoy: {titular}"}]
```
No se envía fecha histórica ni se restringe el contexto. Al evaluar noticias de
hace 1-2 años, el modelo (con su corte de conocimiento) **puede reconocer el
acontecimiento y "saber" lo que pasó después**. En ese caso mediríamos, en parte,
su **memoria histórica**, no su capacidad de interpretar la noticia en el momento.

**Esto es una fuga DISTINTA a la del cosechador** (aquella es de *timing* de
medición; ésta es de *memoria* del modelo) y **no la habíamos abordado**. Es el
mejor hallazgo de la auditoría, y está respaldado por un paper real y de este año
(WorldReasoner, arxiv 2606.11816), que trata precisamente la validez temporal en
forecasting de agentes LLM.

**Honestidad incómoda pero necesaria:** esta fuga podría afectar incluso nuestro
número "índice ~63%". Antes de apoyarnos fuerte en esa cifra frente a
inversionistas técnicos, conviene probar: (a) correr el benchmark solo sobre
noticias **recientes que el modelo no pudo conocer**, y/o (b) pasarle la fecha y
restringir contexto. Si el ~63% se sostiene en noticias "nuevas", la señal es
real. Si cae, parte venía de memoria.

### P5 — Baseline con `y_te` (CORRECTO — pero menor y conservador)

Verificado en `engine/calibration/calibrar_respaldo.py:59`:
```python
base = cal.brier([cal.tasa_base(y_te)] * len(te), y_te)
```
El baseline usa las etiquetas del conjunto de prueba. **Matiz que la auditoría no
menciona:** esto hace el baseline *más fuerte* (es el predictor constante óptimo
para ese test), así que **penaliza al modelo, no lo infla** — el sistema se ve
*peor*, no mejor. Además, `calibrar_respaldo.py` es un **script de diagnóstico
offline**, no la vía de producción. La producción (`walk_forward.py:98`) **ya usa
`tasa_base(y_tr)` honesto** (lo arreglamos en la auditoría 4.5), y la promoción
anidada (`promover_anidado`) también. Fix trivial (y_te → y_tr) por consistencia,
baja urgencia.

---

## Los 4 "riesgos" secundarios

| Riesgo | Veredicto | Nota |
|---|---|---|
| 45 llamadas simultáneas + timeout 12s → medir errores/latencia/fallback | **PARCIAL** | La `fuente` por líder (api/cache/fallback) ya se expone en inicio/fin; el backtest cuenta `con_ia`/`sin_ia`. Falta un **resumen con percentiles de latencia** por simulación. Salvageable formalizar. |
| Prompt = solo el titular | **Válido** | Se junta con P4 (añadir evidencia y fecha). |
| Clasificación léxica confunde activos/noticias | **Válido** | Un benchmark de clasificación sería útil, post-evento. |
| Reproducibilidad: la semilla no hace repetir al LLM | **PARCIAL** | Ya hay caché por (titular, arquetipo, semilla, **versión**) que hace los **demos** reproducibles. Para backtests, guardar snapshots completos sería mejora. |

---

## La arquitectura "de inteligencia colectiva" que propone

Las ideas de capas adicionales (especialista en evidencia, agentes detectores de
error, separar consenso de predicción, memoria de errores por arquetipo) son
**buenas direcciones de investigación**, coherentes con el proyecto. **No son
trabajo de 4 días.** La separación "consenso ≠ predicción" ya la empezamos con el
gating de convicción (Ventana A): el consenso es lo que piensa el enjambre; la
convicción + mercado decide cuándo esa lectura es fiable. Esta auditoría la
llevaría más lejos (un motor que transforme consenso en probabilidad con
evidencia e historial). Vale la pena, post-evento.

El experimento **A/B/C/D** (baseline simple vs. enjambre actual vs. optimizado
vs. con evidencia, sobre los mismos eventos y el mismo holdout temporal) es
**metodológicamente correcto** y es exactamente la forma honesta de demostrar que
el enjambre aporta valor. Es el experimento que yo haría primero, después del
sábado.

---

## Qué haría yo, y en qué orden (post-evento)

Prioridad por impacto en la honestidad de la cifra, no por facilidad:

1. **P4 — contaminación temporal (lo primero).** Es lo único que podría cambiar
   nuestra historia. Probar el benchmark en noticias recientes no conocidas por
   el modelo, y/o fechar el prompt. Barato de probar, alto valor de información.
2. **P5 — fix trivial** de `calibrar_respaldo.py` (y_te → y_tr). 2 minutos, por
   consistencia.
3. **Instrumentación por simulación** (resumen IA/caché/fallback/latencia). Barato
   y útil para distinguir "mal modelo" de "degradación técnica".
4. **P3 — tres bancos** (ordinario/extraordinario/difícil) para un acierto
   representativo, no dominado por extremos.
5. **P2 — confianza efectiva** (declarada + histórica por arquetipo). Idea fuerte,
   más trabajo.
6. **Experimento A/B/C/D** como marco para validar todo lo anterior fuera de
   muestra.

**Lo que NO haría:** subir el número de agentes a ciegas, cambiar todos los
prompts a la vez, o cambiar el modelo. Primero medir, después una variable a la
vez. (En esto la auditoría tiene toda la razón.)

## Impacto en el sábado: NINGUNO

El demo del sábado se sostiene en la visualización 3D + la historia honesta
("señal direccional en índice, ~63% en medición sin fuga, y lo seguimos
auditando"). Esa postura de honestidad intelectual —"acá está lo que medimos y
acá lo que aún estamos verificando"— es precisamente lo que impresiona a un
inversionista técnico. Esta auditoría no cambia el guion; si acaso, lo refuerza:
demuestra que el proyecto se somete a escrutinio externo en serio.
