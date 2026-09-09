# Revisión de la Fase 1 (Ensemble de Sentimiento) + Plan Alternativo

*Rubicón Lab · El Enjambre · 9 de septiembre de 2026*

> **Para Giorgio, en simple.** Me pediste analizar el plan "Fase 1: Ensemble de
> Sentimiento" sin cerrarme, cooperando y contraargumentando donde hiciera falta.
> Antes de opinar, **revisé el código de verdad** (no de memoria). Este documento
> tiene tres partes: (1) por qué NO implementaría ese plan tal como llegó, con el
> porqué de cada cosa; (2) lo que SÍ rescato de él; y (3) el plan como lo haría
> yo, paso a paso. Se puede leer sin saber una línea de código.

---

## PARTE 0 — El resumen de una página

El plan está **bien investigado en forma**, pero se apoya en una **premisa falsa
para tu proyecto**: dice que el enjambre usa FinBERT como motor de sentimiento, y
**no es así** (lo verifiqué en el código). Además propone una vía que **no cabe en
tu servidor** (Render 2 GB), **mide el éxito de forma equivocada**, y trae una
pieza (el diccionario LMcD) **mal armada**.

No lo tiro a la basura: tiene una intuición buena que sí rescato. Pero antes de
construir nada, propongo un **diagnóstico de un día, casi gratis**, que puede
ahorrarnos 1-2 semanas de trabajo inútil.

**Veredicto en una frase:** *el plan ataca un problema que no tienes (FinBERT),
por una vía que no entra en tu servidor (torch en Render), midiendo el éxito como
no se debe (el ensemble solo, no el enjambre).*

---

## PARTE 1 — Por qué NO lo implementaría tal como llegó

### 1.1 La premisa de raíz es falsa: FinBERT NO es tu motor de sentimiento ⛔

El plan abre diciendo: *"El enjambre utiliza FinBERT como su principal motor de
análisis de sentimiento."* **En tu proyecto eso no es cierto.** Evidencia del
código:

- FinBERT existe, pero en un archivo (`engine/nlp_scorer.py`) **deliberadamente
  desconectado**. Su propio comentario de cabecera dice, textual:
  > *"AISLADO A PROPÓSITO: este módulo NO está enchufado al motor en producción.
  > FinBERT arrastra torch + transformers (varios GB en RAM), y el motor corre en
  > Render con memoria muy ajustada: cargarlo ahí lo reventaría (OOM). Además, en
  > El Enjambre la interpretación de la noticia la hacen los LÍDERES LLM por
  > arquetipo — ese es el diferenciador del producto."*
- Tu motor de sentimiento real son **los líderes LLM** (los cerebros de Claude
  por arquetipo) + un **diccionario léxico bilingüe** de respaldo
  (`engine/brains/fallback.py`).
- `torch` y `transformers` **ni siquiera están instalados** en producción
  (lo confirmé en `engine/requirements.txt`).

**Por qué importa (el porqué):** todo el plan está escrito como *"vamos a arreglar
las limitaciones de FinBERT combinándolo con otros modelos"*. Pero tú no tienes
ese problema, porque no usas FinBERT. Entonces el plan **no arregla un bug: es un
cambio de rumbo** — meter una torre nueva de 4 modelos que **compite** con lo que
ya es tu diferenciador (los líderes LLM). Eso es una decisión estratégica grande
disfrazada de "mejora de bajo riesgo".

> **Lectura honesta:** el plan parece escrito mirando "cómo mejorar sentimiento
> financiero" en general, sin mirar tu código. Bien investigado, pero desalineado
> con tu realidad.

### 1.2 No cabe en Render (el problema más grave de todos) ⛔

El plan quiere cargar **FinBERT y RoBERTa** (dos modelos transformer, ~500 MB cada
uno + torch) **encima** de tu simulación de 10.150 agentes, en **Render Standard
de 2 GB**.

- Tu propio equipo **ya tomó esta decisión** y amuralló FinBERT justo por esto.
- El plan afirma *"Riesgo: Bajo (no modifica el núcleo)"* — **falso.** Agregar
  torch a Render **sí** es un cambio de infraestructura, con riesgo real de que el
  motor **se caiga por falta de memoria (OOM)**.

**El porqué:** meter varios GB de modelos en un servidor de 2 GB que ya está lleno
con el enjambre es pedirle que reviente. Las salidas serían: pagar un Render más
grande (costo mensual permanente), o montar un microservicio aparte (que
contradice la regla de CLAUDE.md §5: "nada de microservicios, nada de
sobre-ingeniería"). Ninguna es "bajo riesgo".

### 1.3 Dos de los cuatro modelos están medio ciegos en español ⚠️

VADER y LMcD son **diccionarios solo en inglés**. Tus titulares son **bilingües**
(el producto habla español; los cables de Alpaca/Barchart llegan en inglés).

- En una noticia en español, VADER y LMcD quedan **medio ciegos**.
- Tu léxico actual **ya es bilingüe y está afinado para finanzas** (maneja frases
  compuestas, desambigua "sube las tasas" como malo para acciones, etc.). Para tu
  caso concreto es **mejor** que un VADER genérico.

**El porqué:** estás por sumar dos "opinadores" que no entienden la mitad de tus
titulares, cuando ya tienes uno bilingüe hecho a medida. Es sumar ruido, no señal.

### 1.4 El diccionario LMcD del plan está roto ⛔

El plan **pega miles de palabras a mano** dentro del código Python. Y peor: esas
listas están **mal generadas** — la lista "negativa" incluye montones de palabras
neutras y de relleno (`and`, `the`, `is`, `account`, `customer`…).

- El Loughran-McDonald **real** es un CSV curado (~2.345 negativas, ~347
  positivas), con categorías específicas.
- Cargar una lista inventada así **envenenaría** el sentimiento en vez de
  mejorarlo (contaría como "negativas" palabras que no lo son).

**El porqué:** una pieza mal armada del ensemble no es neutra — arrastra a todo el
conjunto hacia el error. Y encima, miles de palabras incrustadas en el código son
un dolor de cabeza de mantener.

### 1.5 La métrica de Optuna mide lo equivocado ⚠️

El script optimiza qué tan bien **el ensemble por sí solo** predice la dirección,
**aislado del enjambre**. Pero en producción el sentimiento **entra al enjambre**,
y es la simulación la que produce la dirección.

- Optimizar el atajo (sentimiento → dirección directa) **no es lo mismo** que
  optimizar tu tubería real (sentimiento → enjambre → dirección).
- **Trampa filosófica escondida:** si un ensemble de 4 modelos predice la
  dirección al 70% **por sí solo**, entonces tu **enjambre 3D sobra** — la
  predicción vendría del ensemble, no del enjambre. Eso choca de frente con la
  esencia del producto: "el focus group sintético del mercado".

**El porqué:** estarías afinando un número que no es el que de verdad te importa, y
en el extremo, construyendo algo que hace innecesario a tu propio diferenciador.

### 1.6 "Confianza = 1 − desviación" es ingenuo ⚠️

La fórmula de confianza del plan dice: si los modelos coinciden, hay alta
confianza. Pero **coincidir no es lo mismo que acertar**.

- Si los 4 modelos se equivocan **juntos** (comparten el mismo punto ciego, p. ej.
  todos son optimistas, o ninguno entiende el sarcasmo), coinciden y te dan **alta
  confianza en una respuesta equivocada**.
- Esa fórmula **amplifica el error sistemático** justo cuando más duele.

### 1.7 Las cifras y la meta son optimistas ⚠️

- El propio plan cita un estudio con **"60.14% en el S&P 500"** — que está **por
  debajo** de tu meta de 70%.
- El **"100% en 60 titulares"** es un resultado de juguete (sobreajuste: 60
  titulares no prueban nada).
- Las cifras de FinBERT mezclan tareas y datasets distintos (72% aquí, 84.77%
  allá, 50% más allá).
- La meta de **70% de acierto direccional** en titulares es **más alta de lo que
  logra la mayoría de la literatura seria** (55–62%). Prometerla es arriesgado.
- El plan promete "+5 a +10 puntos en negativas" **sin base**. Nuestra experiencia
  con el doomer mostró que una intervención puede ser **totalmente inerte** según
  el mercado (ayudó al índice, cero en cripto y acción). No hay garantía de
  mejora.

---

## PARTE 2 — Lo que SÍ rescato del plan

No todo es para descartar. Estas cosas son buenas y las conservo:

| Idea del plan | ¿Por qué la conservo? |
|---|---|
| **Combinar varias fuentes de sentimiento** | La intuición central es correcta: una sola fuente tiene un solo sesgo; combinar reduce el error sistemático. Es teoría de ensembles sólida. |
| **Estructura de código limpia** (clase base + un wrapper por modelo + ensemble) | Buena higiene de ingeniería; la reuso tal cual. |
| **Usar Optuna para afinar pesos** | Razonable — de hecho ya tienes calibración estilo Optuna en `engine/calibration/`. Solo cambio *contra qué* se optimiza. |
| **La idea de "confianza por desacuerdo"** | Sirve — solo hay que hacerla bien (no con desviación pelada). |
| **Preprocesar/limpiar el texto** | Correcto y barato. |

**En una frase:** la *idea* (combinar fuentes baratas y bilingües, afinar con
Optuna, medir confianza por desacuerdo) es buena. Lo que cambio es el *cómo*: qué
modelos, dónde corren, y contra qué se mide el éxito.

---

## PARTE 3 — El plan como lo haría yo

### Principio rector

Antes de construir una torre nueva, **responder una pregunta que el plan nunca se
hace**: *¿el cuello de botella es de verdad la medición de sentimiento?* Nosotros
ya **medimos** (con el doomer) que el problema de negativas vive en cómo se
**agregan** las señales de los líderes, y que es **específico por mercado**. Nada
en el plan conecta el ensemble con ese mecanismo que ya comprobamos. Así que
primero diagnostico, después construyo (si hace falta).

### PASO 0 — Diagnóstico barato, ANTES de construir nada

**Duración:** ~1 día · **Costo:** casi gratis (usa el backtest y los 645 casos que
ya tenemos) · **Riesgo:** nulo.

Tomo los casos negativos que el enjambre **falla** y, para cada uno, anoto tres
cosas: el puntaje del léxico, el tono agregado de los líderes, y la dirección
real. Con eso respondo **una sola pregunta**:

> Cuando el enjambre falla una mala noticia, ¿es porque el **número de
> sentimiento** estaba mal, o porque estaba **bien** pero la agregación/simulación
> lo dio vuelta?

**Dos desenlaces posibles:**

- **Si la mayoría de fallos tienen el sentimiento CORRECTO** pero la dirección
  final equivocada → **el ensemble NO ayuda.** El arreglo está en la agregación
  (como el doomer). Nos ahorramos 1-2 semanas de trabajo inútil. ✋
- **Si la mayoría tienen el sentimiento EQUIVOCADO** → la premisa del ensemble se
  sostiene, y avanzamos al Paso 1 (pero con la versión de abajo). ✅

**Por qué este paso primero:** es el mismo rigor que usamos con el doomer —
*medir antes de decidir*. Barato, rápido, y nos dice si la Fase 1 siquiera ataca
el problema correcto.

### PASO 1 — Un ensemble que SÍ cabe en Render (solo si el Paso 0 lo justifica)

1. **Fuera los transformers de producción** (FinBERT, RoBERTa). Revientan la
   memoria de Render, y tus **líderes LLM ya son** el lector calidad-transformer.
   Se quedan solo como **referencia offline** — que es justo lo que ya es
   `engine/nlp_scorer.py`.
2. **Ensemble de miembros baratos y bilingües** que sí entran en RAM:
   - Tu **léxico actual** (ya bueno, ya bilingüe).
   - Un **LMcD de verdad**, cargado del **CSV oficial**, junto con un **léxico
     financiero en español** (no una lista inventada a mano).
   - Opcionalmente, el **propio tono de los líderes** como un miembro más del
     ensemble.
3. **Afinar los pesos contra el acierto de punta a punta del ENJAMBRE** (el
   backtest que ya corremos), **no** contra un atajo aislado. Y hacerlo en el
   mercado donde medimos déficit real y no es inerte (índice-like).
4. **Reformular la meta:** en vez de "70% absoluto", perseguir *"superar la base
   actual por un margen medible en negativas, mercado por mercado"* — que es lo que
   sí podemos verificar.
5. **Confianza por desacuerdo, bien hecha:** usar el desacuerdo entre modelos como
   señal de duda, pero **penalizando el punto ciego común** (no premiar la
   coincidencia ciega).

### PASO 2 — La alternativa aún más simple (respeta el producto)

Si el Paso 0 muestra que el sentimiento **ya está bien medido**, entonces ni
siquiera armamos el ensemble. En su lugar:

- **Mejorar el léxico** en las brechas de cobertura que ya podemos medir con
  `engine/validation/test_lexico_cobertura.py`.
- **Seguir invirtiendo en el camino de los líderes LLM**, que es el diferenciador
  del producto (y donde el doomer ya dio fruto en índice).

Esto es lo que más respeta la regla de CLAUDE.md: *"prefiere la solución simple
que funciona hoy sobre la arquitectura perfecta de mañana."*

---

## PARTE 4 — Comparación rápida: plan original vs. mi plan

| Tema | Plan original | Mi plan |
|---|---|---|
| **Premisa** | "Arreglar FinBERT" (que no usas) | Diagnosticar si el sentimiento es el cuello de botella |
| **Primer paso** | Construir 4 modelos ya | Medir 1 día antes de construir |
| **Modelos** | FinBERT + RoBERTa (transformers pesados) | Léxicos baratos y bilingües (+ tono de líderes) |
| **¿Cabe en Render?** | No (riesgo de OOM) | Sí |
| **Idioma** | 2 de 4 solo en inglés | Todos bilingües |
| **LMcD** | Lista inventada a mano (rota) | CSV oficial + léxico español |
| **Qué se optimiza** | El ensemble solo (atajo) | El enjambre completo (real) |
| **Meta** | 70% absoluto (optimista) | Superar la base, medible por mercado |
| **Riesgo** | "Bajo" (en realidad, alto) | Bajo de verdad |
| **Diferenciador del producto** | Lo compite/lo hace sobrar | Lo respeta y lo refuerza |

---

## PARTE 5 — La decisión que te toca a ti

1. **¿Hago el Paso 0 (diagnóstico barato) ahora?** Casi no gasta saldo y nos dice
   si la Fase 1 vale la pena. Es lo que recomiendo.
2. **¿O prefieres pensarlo con calma** con este documento en mano y decidir
   después?

No hay apuro ni riesgo en esperar. Nada está roto hoy. Pero si vamos a invertir
1-2 semanas en un ensemble, primero gastemos 1 día en asegurarnos de que ataca el
problema correcto — igual que hicimos con el doomer.

---

## Anexo — Archivos del código que consulté para esta revisión

- `engine/nlp_scorer.py` — FinBERT offline, desconectado a propósito (la prueba de
  que no es el motor de producción).
- `engine/brains/fallback.py` — el léxico bilingüe real + las transformaciones por
  arquetipo (incluido el `doomer_selectivo` que ya medimos).
- `engine/requirements.txt` — sin torch ni transformers (confirma que no están en
  producción).
- `engine/contenido/vocabulario.py` — el filtro CMF (contexto de que los titulares
  son bilingües).
- `INFORME_CALIBRACION.md` y `engine/calibration/README.md` — donde el equipo ya
  documentó por qué FinBERT/torch no van al motor.

---

*Fin de la revisión. Cualquier duda, pregunta sin miedo.*
