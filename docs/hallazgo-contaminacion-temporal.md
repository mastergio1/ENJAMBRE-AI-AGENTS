# Hallazgo — Contaminación temporal por memoria del LLM (Fase 0)

*Rubicón Lab · El Enjambre · 2026-11-17. Primer experimento de la Fase 0, en
respuesta a la auditoría predictiva (Problema 4). Mide cuánto del acierto de la
señal en ÍNDICE es señal real y cuánto podría ser que el modelo RECUERDE el
desenlace de noticias viejas. Sin IA nueva: reutiliza las señales ya guardadas
(617 casos históricos, 2017→2026) y re-mide el resultado SIN FUGA con Yahoo.
Herramienta: `engine/calibration/contaminacion_temporal.py` (con tests).*

## La idea

El modelo (claude-sonnet-5) tiene un corte de conocimiento. Las noticias
**viejas** (antes del corte) pudo haberlas memorizado, incluido su desenlace; las
**recientes** casi no. Si el acierto NO decae en las recientes, la señal es real.
Si las viejas aciertan mucho más que las recientes, parte del acierto era memoria.

## El resultado (616 casos re-medidos sin fuga)

### Solo ÍNDICE (donde vive la señal), acierto de la dirección de la señal

| Era | n casos | Acierto señal (todos) | Acierto con |señal|≥0.3 |
|---|---:|---:|---:|
| **Viejas (≤2023)** | 124 | **63.1 %** (n=111) | 82.6 % (n=23) |
| 2024 | 15 | 66.7 % (n=9) | 75.0 % (n=4) |
| **Recientes (≥2025)** | 24 | **61.9 %** (n=21) | 66.7 % (n=3) |

### Todos los mercados (contexto)

| Era | Acierto señal (todos) |
|---|---:|
| Viejas (≤2023) | 52.6 % (n=270) |
| 2024 | 57.4 % (n=54) |
| Recientes (≥2025) | 47.0 % (n=253) |

## Qué significa, sin adornos

**La buena noticia (y es importante): la señal base de ÍNDICE NO se cae con las
noticias recientes.** 63.1 % en viejas vs 61.9 % en recientes son prácticamente
iguales. Es decir: **el ~62 % de acierto direccional en índice parece señal real,
no principalmente memoria.** El miedo de la auditoría —que el 63 % fuera un
espejismo de memoria— **no se confirma para la señal base.** Esto sostiene la
afirmación central del proyecto: en índices, el texto de la noticia lleva
información direccional.

**La noticia que obliga a humildad: el "80 % con convicción" está sub-potenciado.**
Cuando exigimos las tres condiciones a la vez (índice + señal fuerte + noticias
recientes), nos quedamos con **n=3**. Estadísticamente eso no demuestra nada. El
82.6 % de las viejas se apoya en n=23; las recientes, en n=3. **El 80 % es real
en los datos con que lo medimos, pero todavía no está establecido con solidez.**
Necesita más datos para creerlo.

**El agregado de todos los mercados en recientes cae a 47 % (azar).** Consistente
con lo que ya sabíamos: fuera de índice (cripto, acción, oro, petróleo) la
dirección no está en el texto. No es contaminación; es que ahí no hay señal.

## Advertencias honestas sobre este experimento

1. **No conozco el corte de conocimiento exacto de claude-sonnet-5.** "Recientes
   ≥2025" podría incluir aún noticias memorizables. El único año verdaderamente
   fuera de muestra (2026) tiene n=1. Así que esto es **sugerente, no
   concluyente**.
2. **Muestras pequeñas** en todos los números con compuerta (|señal|≥0.3).
3. Es un análisis sobre señales generadas **sin** fechar el prompt. Fechar el
   prompt (que el modelo razone "como si fuera" la fecha) reduciría aún más el
   riesgo de pistas de memoria, pero no lo elimina (los pesos ya contienen el
   futuro). La prueba limpia de verdad es correr sobre noticias **posteriores al
   corte**.

## Veredicto provisional sobre las "dos verdades"

Entre "Predictor" (Verdad A) y "Simulador" (Verdad B), esto se inclina hacia
**A para la señal base de índice** (~62 %, aguanta en lo reciente) — pero de forma
**moderada**, no espectacular. El premio del gating (el salto a 80 % con señal
fuerte) **aún no es confiable** por falta de datos.

En una frase para un inversionista técnico: *"En índices medimos una ventaja
direccional real pero modesta, del orden del 60 %, que se sostiene en noticias
recientes; el 80 % con alta convicción es prometedor pero todavía no lo damos por
demostrado — estamos juntando más datos para confirmarlo."* Esa honestidad vale
más que un número inflado.

## Próximo paso (necesita la IA / Render)

Para cerrar esto hacen falta **más casos de índice recientes y post-corte**:
1. Correr el cosechador/benchmark sobre noticias de índice de los últimos meses
   (posteriores al corte del modelo), con el prompt **fechado**.
2. Re-correr `contaminacion_temporal.py` con esos datos.
3. Si el ~62 % base y el premio de convicción se sostienen con n grande →
   señal confirmada. Si caen → era memoria, y la historia pasa a "simulador".

Eso requiere llamadas a la IA (corre en Render, no desde la sesión de análisis).
Es la primera tarea a ejecutar con presupuesto de IA.

---

## Actualización — Intervalos de confianza y bancos por magnitud

*Segunda pieza de la Fase 0. Herramienta: `engine/calibration/intervalos.py`
(con tests). Pone barras de error (bootstrap 95% AGRUPADO POR ACTIVO, para no
tratar varias noticias del mismo símbolo como independientes) sobre los mismos
616 casos.*

### Acierto de la señal con IC del 95%

| Corte | Acierto | IC 95% | n casos | nº activos |
|---|---:|:---:|---:|---:|
| TODOS los mercados | 50.6 % | **[45.3 – 56.0]** | 577 | 71 |
| ÍNDICE | 63.1 % | **[52.5 – 71.4]** | 141 | 4 |
| ÍNDICE, |señal|≥0.3 | 80.0 % | **[69.6 – 85.7]** | 30 | 4 |

### Acierto por banco de magnitud del movimiento (ÍNDICE)

| Movimiento posterior | Acierto | IC 95% | n |
|---|---:|:---:|---:|
| Chico (<1%) | 57.1 % | [54.5 – 59.1] | 42 |
| Medio (1–3%) | 64.9 % | [50.0 – 76.2] | 74 |
| Grande (>3%) | 68.0 % | [50.0 – 81.6] | 25 |

### Qué nos dicen las barras de error (honestidad fina)

1. **El agregado de todos los mercados es azar, confirmado:** 50.6 % con IC
   [45.3–56.0] — cruza el 50 %. No hay señal fuera de índice. (Ya lo sabíamos;
   ahora con barra de error.)

2. **Corrección honesta a lo que dije ayer:** el "80 % con convicción" **NO es
   n=3**. Ese n=3 era solo del corte RECIENTE. Sobre TODO el histórico, la señal
   fuerte en índice es **n=30 con IC [69.6–85.7]**, que **excluye el 50 %**. O
   sea: en los datos que tenemos, el 80 % es un resultado estadísticamente real,
   más sólido de lo que te dije. Me pasé de pesimista; te lo corrijo.

3. **Pero el límite honesto son los activos, no los casos:** índice se apoya en
   **solo 4 instrumentos** distintos (4 "activos"). El bootstrap agrupado por
   activo ya lo refleja —por eso el IC de índice es ancho—, pero con 4 grupos la
   medición sigue siendo frágil. Nuestra evidencia de índice es "real pero
   estrecha": pocos instrumentos, muchas noticias sobre ellos.

4. **El sesgo de selección existe pero es moderado:** el acierto sube con el
   tamaño del movimiento (chico 57 % → grande 68 %), así que parte del acierto
   vive en los extremos (que el cosechador eligió). PERO incluso en movimientos
   chicos el acierto es 57 % (IC [54.5–59.1], excluye 50 %): hay señal también en
   lo ordinario, no solo en los días dramáticos.

### Veredicto refinado

La señal direccional de índice es **real** (base ~63 %, fuerte ~80 %, ambas
excluyen el azar en muestra), **no se cae en noticias recientes** (sección
anterior), y **no vive solo en los extremos** (banco chico 57 %). La debilidad
honesta: descansa en **~4 instrumentos**, y la confirmación definitiva contra
memoria necesita más casos recientes. Historia defendible hoy: *"en índices
medimos una ventaja direccional real, del 60 % de base y ~80 % cuando el enjambre
está muy convencido, con la salvedad de que hasta ahora se apoya en pocos
instrumentos y la seguimos ampliando."*
