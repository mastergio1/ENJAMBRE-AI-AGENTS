# Instructivo — Ampliar los datos de índice (para confirmar el 62%/80%)

*Rubicón Lab · El Enjambre · 2026-11-18. Pasos simples, por botón, para juntar
más datos de índice y confirmar (con muestra ancha) la señal que medimos. Esto
gasta algo de presupuesto de IA (corre en Render). Cuando termines, me pasas el
archivo y yo re-corro todo el análisis.*

## Por qué

Nuestra evidencia de índice es real pero **estrecha**: se apoya en 4 instrumentos
(SPY, QQQ, DIA, IWM) y ~163 casos. Para poder decir el 62%/80% con seguridad
—y sobre todo con noticias recientes— necesitamos más casos. La buena noticia:
la máquina de cosechar y simular **ya existe**; es cuestión de apretar botones.

## Dónde

En GitHub: tu repositorio → pestaña **Actions** (arriba). Ahí verás la lista de
"workflows" (procesos). Cada uno se corre con el botón **"Run workflow"** (a la
derecha). Todos piden el "secreto" automáticamente; tú solo llenas los campos.

## Los 3 pasos, en orden

### Paso 1 — Cosechar más noticias de índice
1. Actions → **"Cosechar exámenes (noticias reales)"** → **Run workflow**.
2. Llena así:
   - **mercados:** `indice`
   - **desde:** `2016-01-01`
   - **tope:** `20`  *(máximo de eventos por instrumento; antes era 8)*
   - **reemplazar:** `false`  *(IMPORTANTE: false, para no borrar lo que ya hay)*
3. Run. Tarda unos minutos en segundo plano. Esto junta noticias de los 9 ETFs de
   índice (incluye VTI, VOO, MDY, RSP, EFA, que hoy no tienen casos) y fechas
   recientes.

### Paso 2 — Simular esas noticias con la IA (aquí se gasta el presupuesto)
1. Actions → **"Backtest histórico (tanda)"** → **Run workflow**.
2. Llena así:
   - **tanda:** `20`  *(máximo por corrida)*
   - **mercado:** `indice`
3. Run. Cada corrida rinde 20 exámenes (~1 minuto cada uno).
4. **Repite este paso varias veces** (5-10 corridas) hasta que ya no queden
   pendientes. Cada corrida cuesta ~20 simulaciones de IA. Puedes correrlas
   seguidas.

### Paso 3 — Descargar el resultado y pasármelo
1. Actions → **"Export calibración (artefacto)"** → **Run workflow** → Run.
2. Cuando termine, entra a esa corrida y abajo, en **"Artifacts"**, descarga
   **`calibracion-casos`** (es un .zip con el `calibracion.json`).
3. **Pásame ese archivo** por el chat.

## Qué hago yo cuando me lo pases

Re-corro los tres análisis sobre el dataset más grande:
1. `contaminacion_temporal` — ¿la señal de índice sigue sin caer en lo reciente,
   ahora con más casos?
2. `intervalos` — ¿el 62%/80% se mantiene y con intervalos de confianza más
   estrechos (más instrumentos)?
3. `acierto_por_arquetipo` — ¿el orden de las voces se confirma?

Y te doy el veredicto: **si aguanta con muestra ancha → señal confirmada, historia
sólida para inversionistas. Si se ablanda → ajustamos la historia con honestidad.**

## Cuánto cuesta (orden de magnitud)

Cada simulación usa ~110 llamadas de IA (el presupuesto de la biblia). Si juntamos
~150-200 casos nuevos de índice, son ~150-200 simulaciones → del orden de unos
pocos dólares a unas pocas decenas, según el tope que uses. Nada que te frene,
pero para que sepas qué estás gastando.

## Nota honesta sobre el límite

Los índices grandes de EE.UU. (SPY, QQQ, DIA, VTI, VOO) están **muy
correlacionados** entre sí — son casi el mismo mercado. Los que suman verdadera
independencia son **EFA (internacional), MDY (mediana capitalización) y RSP
(ponderación igual)**. Por eso el tope alto y cubrir esos ayuda más que repetir
los de siempre. Aun así, parte de la "estrechez" es intrínseca: los índices se
mueven juntos. La diversidad real también viene de **más fechas/eventos**, no solo
de más tickers — y eso el Paso 1 (tope 20, desde 2016) lo cubre.
