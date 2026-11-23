# Análisis en frío — Auditoría v3 (23-11-2026)

*Rubicón Lab · El Enjambre · 2026-11-23. Evaluación independiente de la "Auditoría
técnica y científica + Plan de Evolución v3", verificada contra el código y los
datos reales.*

## Veredicto: la más rigurosa de las seis, y acierta

A diferencia de las anteriores, esta auditoría **encontró problemas reales nuevos
—incluidos cuatro en el código del registro prospectivo que yo mismo escribí y
desplegué el 18-11.** Verifiqué cada afirmación P0/P1 contra el repo y los datos:
**todas se confirman.** No hay cifras infladas ni citas inventadas. Es una
auditoría para tomarse en serio y agradecer.

**Contexto nuevo:** existe otro agente (**Codex**) trabajando en el repo — los PR
#34 y #35 (`codex/piloto-macro-offline`, `codex/integridad-evaluacion-macro`) son
reales y están abiertos. La auditoría trae incluso una lista de tareas para Codex
(§7). Hay que **coordinar carriles** para no chocar.

## Lo primero, para tu tranquilidad: el 63%/80% NO se toca

El hallazgo más serio (P0-01) es que `walk_forward.py` ordena el backtest por
`c["fecha"]`, que es **la hora en que se corrió la simulación** (todos el
2026-08-03), no la fecha real de la noticia. Lo verifiqué en los datos: en **496
de 619 casos** esas dos fechas difieren hasta de año. El "backtest temporal" del
calibrador, entonces, no es temporal de verdad.

**PERO** mis hallazgos (contaminación, intervalos, acierto por arquetipo) usan
`reaccion_real.fecha_base` —la fecha real de la noticia—, no `c["fecha"]`. Así que
**el 62.7% de índice y el 77-80% de convicción fuerte siguen siendo válidos** con
sus salvedades conocidas. El bug afecta al **calibrador de probabilidad**, que no
está publicado en el producto. Hay que arreglarlo antes de confiar en él, pero no
contamina lo que ya reportamos.

## Verificación de los hallazgos P0 (críticos)

| # | Hallazgo | Veredicto | ¿Afecta 63%/80%? |
|---|---|---|---|
| P0-01 | `walk_forward` ordena por fecha de procesamiento, no de la noticia | ✅ **Confirmado** (496/619 difieren de año) | ❌ No (mis tools usan `fecha_base`; afecta solo el calibrador, no publicado) |
| P0-02 | Cosechador: sesgo de selección por movimiento | ✅ Ya conocido (la fuga que documentamos) | Documentado |
| P0-03 | Registro prospectivo: `try/except pass` silencioso + solo el primer ticker | ✅ **Confirmado (mi código)** | — |
| P0-04 | Resolver no maneja fin de semana (`as_of` sábado → nunca resuelve) | ✅ **Confirmado (mi código)** | — |

## Verificación de los hallazgos P1

| # | Hallazgo | Veredicto |
|---|---|---|
| P1-05 | `id_simulacion(titular,seed)` sin ticker/horizonte + `INSERT OR REPLACE` → colisión posible SPY/QQQ | ✅ Correcto. **Lo aborda Codex en PR #35.** |
| P1-06 | Holdout/CLI: `promover()` en el `__main__` confunde diagnóstico con evidencia | ✅ Correcto (ya anotado en plan v2) |
| P1-07 | `intervalos` agrupa por activo; 4 ETFs no son independientes; fallback a bootstrap por fila | ✅ Correcto (plan v2 ya pedía multiway) |
| P1-08 | No se ha aislado el aporte propio del ENJAMBRE (ablación A0–A5) | ✅ **Excelente** — más afilado que mi A/B/C/D |
| P1-09 | `resumen_predicciones` usa `limite=500` → cobertura sobre muestra truncada | ✅ **Confirmado (mi código)** |
| P1-10 | `resolver_prediccion` lee-y-actualiza sin `WHERE resuelto=0` atómico | ✅ **Confirmado (mi código)** |
| P2-11 | Ops: BackgroundTasks en proceso, cron 20:30 UTC = 15:30 ET (antes del cierre), falta CI con pytest en cada PR | ✅ Correcto |

## Los 4 bugs de MI código (los reconozco y propongo arreglar)

Son reales y son míos. Ninguno rompe el producto hoy, pero debilitan el registro
prospectivo —justo la pieza que debe ser impecable porque su valor es la
integridad de los datos:

1. **P0-03 — falla silenciosa:** si el registro de una predicción falla, el
   `except: pass` lo esconde y nadie se entera. Un registro cuyo valor es la
   completitud no puede fallar en silencio. **Arreglo:** registrar el intento,
   contar `intentos/registradas/fallidas`, y alertar; además registrar TODOS los
   tickers de la noticia, no solo el primero.
2. **P0-04 — fin de semana:** si la noticia cae sábado/domingo, el resolvedor
   busca una barra de ESE día, no la encuentra y nunca resuelve. **Arreglo:**
   resolver desde la primera sesión hábil posterior, con calendario.
3. **P1-09 — cobertura truncada:** el tablero cuenta sobre máximo 500 filas; con
   más predicciones, los denominadores quedan mal. **Arreglo:** contar con SQL
   sobre el universo completo (`COUNT(*)`), no sobre una lista truncada.
4. **P1-10 — resolución no atómica:** dos procesos podrían resolver la misma
   predicción. **Arreglo:** `UPDATE ... WHERE resuelto=0` atómico.

Los cuatro son de bajo riesgo hoy (el ritual corre en un solo proceso, de lunes a
viernes) pero son correctos y rápidos de arreglar. Son **mi carril**.

## El plan: v3 reemplaza a v2

El Plan v3 es un **superconjunto más riguroso** del v2: conserva la estructura
(ciencia + ingeniería, prospectivo primero) y añade lo que faltaba — esquema de
identidad temporal (`available_at`, `as_of`…), cosecha por **calendario** (no por
movimiento), la ablación **A0–A5** para aislar el aporte del enjambre, holdout con
manifiesto y hash, CI con pytest en cada PR, y la coordinación con Codex. **Lo
adopto como el plan vigente.**

## Reparto de carriles (importante, hay dos agentes)

| Carril | Quién | Qué |
|---|---|---|
| Registro prospectivo (bugs P0-03,04; P1-09,10) | **Yo** | Es código mío; lo arreglo |
| Ciencia / análisis / ablación A0–A5 | **Yo** | Mi terreno hasta ahora |
| Identidad y esquema macro (P0-01, P1-05) | **Codex** | PR #34/#35 ya lo abordan |
| CI, rama canónica, política de merge | **A definir contigo** | Decisión de gobierno |

**Riesgo a evitar:** que Codex y yo toquemos los mismos archivos
(`persistencia.py`, `walk_forward.py`) a la vez. Antes de que yo arregle P0-01 o
la identidad, hay que ver qué trae el PR #35 para no pisarnos.

## Mi recomendación

1. **Arreglar YA los 4 bugs del registro prospectivo** (mi carril, rápido, no
   choca con Codex).
2. **Adoptar el Plan v3** como vigente (actualizo `plan-evolucion-enjambre.md`).
3. **Definir el gobierno:** rama canónica, política de merge, y si reviso/cierro
   los PR de Codex o los deja él. Eso lo decides tú.
4. **P0-01 (fecha del walk_forward)** y la identidad: coordinar con lo que trae
   Codex antes de tocarlo, para no duplicar.
