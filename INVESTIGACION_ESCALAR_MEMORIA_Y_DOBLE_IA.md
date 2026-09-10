# Escalar El Enjambre: memoria para los agentes + doble IA (Claude + ChatGPT)

*Investigación a fondo. Costos en dinero, tiempo y complejidad. Para Giorgio.*
*Fecha: 2026-09-10. Basado en el código real del motor, no en supuestos.*

---

## Resumen ejecutivo (léelo aunque no leas nada más)

1. **El servidor casero NO resuelve ninguna de las dos ideas.** Memoria y doble-IA
   son problemas de **software y de API**, no de **cómputo**. Un servidor casero
   solo sirve para correr un **modelo de IA local** y ahorrar en API. Pero:
   - Tu gasto de IA es de **~$35 total**, no de miles. El cómputo NO es tu cuello
     de botella.
   - Un modelo local lo bastante bueno para igualar a `claude-sonnet-5` en el
     razonamiento por arquetipo (el diferenciador del producto) necesita una
     tarjeta gráfica de **$1.500–3.500**, electricidad 24/7, y mantenimiento — a
     cambio de **peor calidad** y **menos confiabilidad**. Mala inversión.
   - Para un producto B2B que quieres **vender**, un servidor en tu casa (con tu
     internet y tu luz) es un **punto único de falla**. La nube es lo correcto.

2. **Memoria (darle contexto histórico a los líderes): vale la pena explorarla,
   PERO barata y en software** — no en hardware. Y ojo con la expectativa:
   probablemente mejore más la **riqueza/realismo** de las opiniones que el
   **acierto** (que tiene techo estructural, como ya medimos).

3. **Doble IA (Claude + ChatGPT): es una jugada de DIVERSIDAD/realismo, no de
   acierto.** Dos modelos chocan contra el mismo techo de "la dirección no está en
   el texto". Suma variedad de voces (bueno para el focus-group), pero también
   suma complejidad y costo. Opcional, no prioritario.

---

## Contexto: cómo funciona hoy el motor (para entender los costos)

- 10.150 agentes: 9.000 de reglas + 1.150 líderes LLM que comparten **~110
  "cerebros"** (110 llamadas reales a la API por simulación).
- Solo los líderes leen la noticia. Cada uno: `claude-sonnet-5`, prompt de
  arquetipo (~65 tokens) + instrucción JSON (~85 tokens) + el titular (~20
  tokens) = **~170 tokens de entrada por llamada**. Corto.
- Costo por simulación: **~$0.12** (con caché por titular+arquetipo+semilla).
- **Ya tenemos el material para memoria:** un banco de **652 casos** con titular,
  fecha, símbolo, categoría y **el resultado real** de cada uno (en SQLite).
- **Render tiene RAM ajustada** (hoy vimos reinicios por memoria con los sims de
  10.150 agentes). Cargar modelos pesados ahí (torch/FinBERT) lo revienta — ya
  está aislado por eso (`nlp_scorer.py`).

---

## IDEA 1 — Memoria para los agentes (contexto histórico al leer la noticia)

### Qué es, en concreto
Hoy un líder lee "la Fed sube 50 puntos" **en frío**. Con memoria, antes de
opinar recibiría contexto: *"eventos parecidos del pasado y qué pasó después"*
(ej. subidas de tasa previas y la reacción real del mercado). Técnicamente es
**RAG** (retrieval-augmented generation): buscar los casos más parecidos y
metérselos al prompt.

### Cómo se hace BIEN (sin servidor, sin reventar Render)
1. **Precomputar embeddings** (un "número-huella" por titular) de los 652 casos —
   una sola vez, offline o con una API de embeddings barata.
2. **Guardar esos vectores en SQLite** (ya lo tenemos).
3. En cada simulación: embeber el titular nuevo y buscar los 3–5 casos más
   parecidos con una multiplicación de vectores en `numpy` (milisegundos, sin
   torch, sin GPU). **Corre en el Render actual sin problema.**
4. Inyectar esos casos + su resultado real en el prompt del líder.

> **No hace falta torch/FinBERT en Render** (eso sí lo reventaría). Los embeddings
> se precomputan aparte; en vivo solo se hace una resta de vectores. Cero hardware
> nuevo.

### Costos

| Dimensión | Costo | Detalle |
|---|---|---|
| **Dinero (setup)** | **~$1–3** | Embeber 652 casos una vez, vía API de embeddings. |
| **Dinero (por simulación)** | **+30–50%** (≈ $0.12 → **$0.16–0.18**) | El contexto agranda el prompt (~170 → ~400 tokens de entrada). La salida no cambia, y la salida es lo caro, por eso el alza es moderada. |
| **Tiempo (desarrollo)** | **1–2 sesiones enfocadas** | Pipeline de embeddings, búsqueda + inyección, manejo de caché, re-validación. |
| **Complejidad** | **MEDIA** | Es una pieza nueva pero acotada. Ya tenemos los datos y el SQLite. |
| **Hardware** | **$0** | Ninguno. |

### La trampa que hay que cuidar (importante)
**Sesgo de anticipación (lookahead):** al simular un evento de 2001, la memoria
debe traer SOLO casos **anteriores** a esa fecha. Si le cuela el futuro, el
"acierto" sube falsamente y sería otra medición en vano. Es un detalle sutil pero
crítico para que los backtests valgan.

### ¿Mejora el acierto? (la pregunta honesta)
- **Probablemente un poco, no un salto.** El techo del acierto no es por falta de
  contexto: es que **la dirección tras una noticia es casi aleatoria caso a caso**
  (el mercado ya la tenía descontada). Reacciona a la **sorpresa vs. lo esperado**,
  no al evento crudo — y "la última vez que la Fed subió, cayó" es justo el patrón
  ingenuo que NO generaliza.
- **Donde SÍ ayudaría:** casos donde el contexto cambia la interpretación (ej. una
  caída del 20% que "en realidad no es tanto" dado el contexto — tu propio
  ejemplo). Ahí la memoria puede afinar la señal.
- **El beneficio más probable es de REALISMO:** las frases de los líderes quedarían
  más ricas y contextuales ("esto rima con 2018, cuando..."). Eso mejora el
  **momento mágico del demo**, que es donde vive el valor del producto.

### Veredicto Idea 1
**Vale la pena, como experimento de software barato**, con expectativa puesta en
**realismo** más que en acierto. Sin servidor. Riesgo bajo, upside moderado.

---

## IDEA 2 — Dos modelos en un entorno (Claude + ChatGPT juntos)

### Qué podría significar (3 sabores)
- **A. Diversidad de cerebros:** unos líderes usan Claude, otros GPT → más
  variedad de "personalidades".
- **B. Ensamble/votación:** ambos opinan y se combinan → busca robustez.
- **C. Pipeline de roles:** uno interpreta, el otro verifica/critica.

### Costos

| Dimensión | Costo | Detalle |
|---|---|---|
| **Dinero (por simulación)** | **+0% a +100%** | Si REPARTES líderes (mitad y mitad): costo similar. Si ambos opinan por caso (ensamble): ~2× la parte LLM (≈ $0.12 → ~$0.24). GPT-4-class cuesta parecido a Sonnet. |
| **Tiempo (desarrollo)** | **2–3 sesiones** | Abstraer la "interfaz de cerebro", 2 SDKs, 2 llaves, 2 fallbacks, 2 formas de parsear JSON, 2 límites de tasa, 2 cachés. |
| **Complejidad** | **MEDIA-ALTA** | Hoy el código tiene UN camino limpio (Anthropic). Meter OpenAI duplica los modos de falla. (Y cada modelo tiene sus mañas: Sonnet rechaza `temperature`; GPT tiene otras.) |
| **Hardware** | **$0** | Ambos son APIs en la nube. |

### ¿Mejora el acierto?
- **Marginal.** Dos modelos chocan contra el mismo techo. Si la dirección no está
  en el texto, dos IAs coincidirán en lo mismo o discreparán al azar.
- **Donde SÍ suma: diversidad de voces.** Dos familias de modelos dan
  personalidades genuinamente distintas a los líderes → focus-group más rico.

### Veredicto Idea 2
**Jugada de realismo/variedad, no de acierto.** Opcional. Si se hace, empezar
**barato**: poner unos pocos líderes en GPT y comparar las voces, antes de
duplicar todo.

---

## EL SERVIDOR CASERO — análisis dedicado (porque es la decisión de plata grande)

### Cuándo un servidor casero SÍ tiene sentido
Solo si vas a correr un **modelo de IA local** (open-source) para **no pagar API**
a gran volumen. Es el único caso.

### Por qué HOY no aplica

| Factor | Realidad |
|---|---|
| **Tu cuello de botella** | No es el cómputo ni el costo de API ($35 total). Es el **techo de acierto** (estructural) y el **realismo** (software). |
| **Hardware para igualar a Sonnet** | GPU de 24GB+ ($700–900 usada; $1.600+ nueva), o 2 tarjetas para modelos de 70B. Rig realista: **$1.500–3.500**. |
| **Calidad** | Un modelo local sería **PEOR** que Sonnet en el razonamiento por arquetipo — el diferenciador del producto. |
| **Costos ocultos** | Electricidad 24/7 (~300–500W bajo carga), tu internet de casa, cortes de luz, actualizaciones, seguridad (abrir tu casa a internet). |
| **Confiabilidad para vender** | Un demo B2B que se cae porque se fue la luz en tu casa mata la venta. La nube da uptime. |

### Veredicto servidor casero
**No lo construyas para esto.** Resolvería un problema que no tienes (costo de
cómputo) creando tres que sí tendrías (peor calidad, fragilidad, mantenimiento).
Si algún día El Enjambre corre **miles de simulaciones al día** y la factura de
API se vuelve el costo dominante, ahí se reevalúa — pero ese día está lejos.

---

## Comparación de las 3 rutas

| Ruta | Dinero | Tiempo | Complejidad | ¿Sube acierto? | ¿Sube realismo? | Hardware |
|---|---|---|---|---|---|---|
| **Memoria (RAG, software)** | +$1–3 setup, +30–50%/sim | 1–2 sesiones | Media | Poco | **Sí** | $0 |
| **Doble IA (Claude+GPT)** | +0–100%/sim | 2–3 sesiones | Media-Alta | Marginal | Sí (variedad) | $0 |
| **Servidor casero** | **$1.500–3.500 + luz** | Semanas + mantención | **Alta** | No | No | Mucho |

---

## Mi recomendación honesta, priorizada

1. **NO compres servidor casero.** Ninguna de tus dos metas lo necesita.
2. **Si quieres explorar memoria:** hazla en **software**, barata, con embeddings
   precomputados + SQLite + numpy (sin torch, sin GPU). Mídela con el interruptor
   de caché fresca que ya construimos hoy, cuidando el sesgo de anticipación.
   Espera mejora de **realismo**, con acierto como bonus incierto.
3. **Doble IA: déjala para después**, y si la haces, arranca chica (unos líderes
   en GPT) como experimento de variedad de voces, no como plan de acierto.
4. **Recordatorio de fondo:** El Enjambre es un **simulador / focus-group**, no un
   predictor. Su valor de venta es la **visualización 3D**, las **voces por
   arquetipo** y el **realismo** — no adivinar la dirección. Escala hacia donde
   está el valor: hacer el enjambre más vivo, más contextual y más impresionante;
   no hacia predecir mejor algo que tiene techo natural.

---

## Orden sugerido si decides avanzar (todo en la nube, sin hardware)
1. **Prototipo de memoria barato** (1 sesión): embeddings de los 652 casos +
   retrieval con filtro de fecha + inyección en 1–2 arquetipos, medido con caché
   fresca en una muestra chica de índice. Ver si las frases mejoran y si el acierto
   se mueve. Costo estimado: **~$5–8** de IA.
2. Si el prototipo entusiasma → extenderlo a todos los arquetipos y re-medir.
3. Doble IA solo si, después de memoria, quieres aún más variedad de voces.

---
*Rubicón Lab · El Enjambre · Investigación de escalamiento · 2026-09-10*
