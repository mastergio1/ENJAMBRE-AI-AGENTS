# Bitácora de la sesión: la caza del acierto en negativas

**Fecha:** 6 de septiembre de 2026
**Para:** Giorgio (Rubicón Lab)
**En una línea:** entramos a mejorar el punto flaco del enjambre —acierta poco cuando la noticia es mala— y salimos con **dos mejoras reales en producción**, **una idea grande descartada con honestidad**, y **una máquina de medir** que deja barato probar lo que venga.

---

## 0. El problema que vinimos a resolver

El enjambre acierta bien la **dirección** del mercado cuando la noticia es buena, pero **falla en las malas**: muchas veces predice que el precio sube cuando en realidad cayó. Es demasiado optimista. Toda la sesión giró alrededor de subir ese acierto en negativas **sin romper lo que ya funciona**.

Un mapa de lo que hicimos, en orden:

1. Freno de la manada (arreglado y afinado) → **producción**
2. Limpieza de código muerto de memoria → **producción**
3. Dos "sprints" que me pasaste → **evaluados y descartados con razón**
4. Diagnóstico de causa raíz → **entender el porqué**
5. P1: mejorar el diccionario de tono → **producción**
6. P2: separar el "clima" de la "apuesta" → **medido a fondo y archivado**
7. La infraestructura de medición (motor + memoria + bugs) → **construida**

---

## 1. El freno de la manada — y afinarlo con Optuna

**Qué encontramos:** en una racha de malas noticias, los imitadores (la "manada") se copian entre sí y arman una bola de nieve: la 4ª mala noticia golpeaba **más fuerte** que la 1ª. Eso es sobre-pánico irreal.

**Qué hicimos:** un "freno" que reduce cuánto vende la manada cuando entra en *modo cautela* (tras 3 malas seguidas). La pregunta era: ¿qué tan fuerte apretar el freno?

**Cómo lo hicimos:** usamos **Optuna** —un buscador automático que prueba muchos valores— con un objetivo honesto anclado al propio modelo: *que la 4ª mala pegue igual que la 1ª* (ni más = sobre-pánico, ni menos = ignorar la noticia). El buscador tiró un "ganador" ruidoso (0.147), pero al mirarlo de cerca era azar. Elegí un valor **moderado y estable: 0.5**, y lo validé contra los 5 hechos estilizados (las "huellas digitales" de un mercado real) para confirmar que no rompía nada.

**Resultado:** freno en 0.5, hechos estilizados pasando. **Mergeado a producción.**
*(Detalle: `INFORME_FRENO_MANADA.md`, `INFORME_OPTUNA_FRENO.md`.)*

---

## 2. Limpiar el peso muerto de la memoria

**Qué encontramos:** los agentes tenían una "memoria de percepción" (`ajustar_por_contexto`) que en su día se probó para amortiguar el pánico y **no funcionó**. Quedó ahí ocupando espacio, sin hacer nada útil.

**Cómo lo hicimos:** quité el código muerto (`ajustar_por_contexto`, `contador_buenas`) pero **conservé lo que sí sostiene el freno**: la memoria que detecta la racha mala y enciende el *modo cautela*. Cirugía fina, con un test que confirma que la cautela sigue activándose con 3 malas y no antes.

**Resultado:** menos código, mismo comportamiento, nada roto. **Mergeado a producción.**

---

## 3. Los dos "sprints" que me pasaste — la parte incómoda pero honesta

Me pasaste dos paquetes de mejoras listos ("Sprint 2.1" y "2.2"). Los revisé antes de ejecutarlos y **encontré que estaban desconectados del sistema real**:

- Llamaban a funciones que no existen (`obtener_casos`, cuando lo real es `respaldo.casos_remotos()`).
- Usaban un formato de datos plano que no es el nuestro (el real es anidado).
- Optimizaban con un sentimiento **al azar**, sin conexión con la métrica real.
- Editaban la función equivocada (la ruta numérica en vez de la del LLM, que es la que causa el 38%).

**Qué hicimos:** te lo dije tal cual, sin maquillar. Preferiste "mejor no hacerlo" en el 2.1. Fue la decisión correcta: ejecutarlos habría dado números falsos con apariencia de progreso.

**La lección:** un paquete que "se ve completo" puede estar apuntando al aire. Vale más media hora de revisión que un mes creyendo una mentira.

---

## 4. El diagnóstico de causa raíz

**Qué hicimos:** antes de tocar nada más, medí de verdad *por qué* falla en negativas. Primero me equivoqué —dije que había un "techo del 96%"— y **me corregí**: ese número usaba información del futuro (la categoría de cada caso se define por lo que el mercado hizo *después*, no por el tono de la noticia). Sin trampa, el hallazgo real fue claro:

> **El enjambre no es pesimista de más; es optimista de más.** Ante un desplome real de −9%, el enjambre predecía en promedio **+5%**. Está mirando el vaso medio lleno cuando el mercado se está cayendo.

Eso apuntó a la capa correcta: el **tono de mercado** (el ánimo que emerge de los líderes), no las reglas de los agentes.
*(Detalle: `INFORME_DIAGNOSTICO_NEGATIVAS.md`, `INFORME_CAUSA_RAIZ_NEGATIVAS.md`.)*

---

## 5. P1 — arreglar el "oído" del enjambre (el diccionario de tono)

**Qué encontramos:** cuando el LLM no alcanza, el enjambre lee el titular con un diccionario de palabras (el "respaldo léxico"). Ese diccionario estaba **medio sordo**: no reconocía variantes de palabras y se quedaba **mudo** (tono 0) en el 74.5% de los titulares. Un mercado que no oye la mitad de las malas noticias, obvio que no reacciona.

**Cómo lo hicimos:**
- Reconocimiento por **palabra completa** (regex con límites `\b`), para no confundir pedazos de palabras.
- Amplié el diccionario con **formas conjugadas e inflexiones** ("cae", "cayó", "caída"…).
- Le puse dos condiciones que me pediste, y las cumplí:
  1. **Monitoreo en vivo:** un registro que compara la polaridad del respaldo contra la del LLM real, para ver si algo se descalibra.
  2. **Rollback rápido:** una variable de entorno (un umbral) que apaga o revierte el cambio al instante, sin tocar código.

**Resultado (medido):**
| | Antes | Después |
|---|---|---|
| Titulares "mudos" | 74.5% | **60.5%** |
| Bien clasificados como positivos | 54.4% | **62.8%** |
| Falsos positivos | 39.7% | **31.9%** |

El enjambre ahora **oye mejor**. **Mergeado a producción** con su monitoreo y su interruptor de emergencia.
*(Detalle: `INFORME_P1_LEXICO.md`, `INFORME_P1_COMPLETO.md`.)*

---

## 6. P2 — la idea grande: separar el "clima" de la "apuesta"

**La teoría (buena):** tres tipos de líder —el contrarian sabio, el quant escéptico y el optimista— **invierten** la señal ante malas noticias (ven la caída como oportunidad de compra). Eso está bien para *su apuesta personal*, pero al promediarlos, **diluyen el ánimo colectivo** y el mercado no reacciona a la mala noticia. La idea de P2: que esos tres **sigan apostando y hablando**, pero **dejen de fijar el clima**. Una perilla (`peso_tono_invertidores`) controla cuánto pesan en el clima: 1.0 = como siempre, 0.0 = fuera del clima.

**Cómo lo medimos (esto fue lo importante):** con el **LLM real** en Render, sobre los exámenes históricos respaldados, comparando la **misma muestra y semillas** con la perilla en distintas posiciones. Así el experimento aísla el efecto de P2 limpio.

### El giro honesto de esta historia

**Primera medición (muestras chicas, 18–24 negativas):** P2 subía las negativas **+11 y +12 puntos**, sin costar nada en positivas. Se veía **excelente**. Escribí un informe entusiasta (`INFORME_P2_HALLAZGO.md`).

**Segunda medición (muestra completa, 163 exámenes del índice):** la ventaja **se desinfló hasta desaparecer.** Aquí está el cuadro final con la perilla en tres posiciones:

| Perilla | Negativas (81) | Positivas (69) | Global |
|---|---|---|---|
| **1.0** — actual | **44/81 = 54.3%** | **50/69 = 72.5%** | **62.6%** |
| **0.3** — suave | 44/81 = 54.3% | 48/69 = 69.6% | 60.7% |
| **0.0** — pleno | 45/81 = 55.6% | 46/69 = 66.7% | 59.5% |

En 0.3 las negativas dan **exactamente los mismos 44 aciertos** que ahora —ni uno más— y las positivas **pierden ~3 puntos**. P2 resultó ser una palanca que **solo tiene lado malo** a escala completa.

**Cómo se desinfló, tanda por tanda (perilla 0.3):**
| Casos | Negativas |
|---|---|
| 40 | 62.5% ← la ilusión |
| 80 | 54.3% |
| 120 | 54.8% |
| 163 | **54.3%** ← la verdad |

**Por qué falló (en simple):** esos tres líderes **no eran la causa** de que el enjambre acierte poco en negativas; quitarlos del clima no movió la aguja. Pero sí aportaban al clima de las **positivas** (donde ya íbamos bien), así que silenciarlos solo hizo perder aciertos buenos. Apagamos algo que ayudaba de un lado sin arreglar nada del otro.

**Decisión:** P2 **se archiva**. La perilla se queda en **1.0** (que es el valor por defecto en producción → **no hay que revertir nada**, P2 nunca cambió el comportamiento en vivo). El código queda inerte y reversible por si un rediseño futuro lo aprovecha. **No se gastó más saldo:** tu presupuesto de $48.66 quedó intacto.
*(Detalle: `INFORME_P2_MEDICION.md`, `INFORME_P2_HALLAZGO.md` (corregido), `INFORME_P2_CIERRE.md`.)*

**La lección más cara evitada:** activar P2 con la señal de 40 casos habría metido una regresión (−3 pts en positivas) **creyendo que mejorábamos**. La disciplina de esperar la muestra completa nos salvó.

---

## 7. La máquina de medir (lo que quedó construido para siempre)

Para poder medir P2 con el LLM real sin arruinarnos ni caernos, hubo que construir bastante fontanería. Esto es reutilizable para cualquier idea futura:

- **Evaluación con exámenes reales:** el sistema toma los casos históricos respaldados y mide el acierto de dirección por categoría (negativa/positiva/neutra), con el LLM real.
- **Caché de cerebros en disco persistente:** las respuestas del LLM se guardan y **sobreviven a los redespliegues**. Por eso barrer la perilla (0.0, 0.3, 1.0) fue **gratis**: los cerebros ya estaban pagados y la perilla solo cambia cómo se promedian, no las llamadas.
- **Evaluación resumible y a prueba de memoria:** Python no le devuelve la RAM al sistema, así que miles de simulaciones de 10.000 agentes reventaban el servidor. Lo partí en **tandas de 40** que **guardan el progreso en disco**; si el motor se reinicia por memoria, **retoma donde iba**. Así completamos los 163 exámenes en varias tandas sin perder nada.
- **Botón desde GitHub:** un workflow ("Evaluar acierto (P2)") que dispara cada tanda con un clic, **tolerante** a los hipos de red y que siempre muestra el resultado guardado.

### Bugs y sustos que arreglamos en el camino
- **Render se quedó sin memoria (512MB) y se cayó** → subiste al plan de 2GB (confirmado). Aun así, una tanda grande lo tumbaba → lo resolví con las tandas resumibles.
- **Bug de "0 evaluados":** el cruce entre evento y caso fallaba en Render (GitHub entrega archivos distintos por dos rutas). Lo arreglé haciendo que la evaluación **recorra los casos directamente**.
- **El workflow abortaba con error 22** por un hipo de red pasajero → lo hice tolerante.
- **Una tanda de 0.3 no dejó registro** (el motor se reinició justo al dispararla) → la volví a disparar y retomó sin problema. Prueba de que el sistema **se auto-cura**.

---

## 8. Estado final de producción

| Cambio | Estado | Efecto en vivo |
|---|---|---|
| Freno de la manada (0.5) | ✅ en `main` | menos sobre-pánico en rachas |
| Limpieza de memoria | ✅ en `main` | igual comportamiento, menos código |
| P1 — diccionario de tono | ✅ en `main` | **oye mejor** las malas noticias (con monitoreo + rollback) |
| P2 — separar clima de apuesta | 🗄️ archivado, perilla en 1.0 | **ninguno** (inerte, reversible) |

El respaldo histórico y el comportamiento en vivo **nunca se tocaron** durante las mediciones.

---

## 9. Qué sigue (cuando quieras)

El acierto en negativas **sigue siendo el problema abierto** (~54%). P2 confirmó que la capa correcta es el **tono de mercado**, pero que silenciar líderes no es la palanca. El siguiente intento natural: **corregir el sesgo alcista directamente en el consenso/léxico** (que el enjambre no lea una caída del −9% como un +5%), y medirlo con la máquina que **ya está lista y es gratis de correr**.

Pero eso es otra misión. Esta quedó cerrada, con dos mejoras reales, una idea descartada con número honesto, y las herramientas para seguir sin gastar de más.

---

*Informes de detalle citados en cada sección. Cómo medir: `docs/medir-p2.md`, `docs/backtest-real.md`.*
