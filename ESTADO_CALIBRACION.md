# Estado de la Calibración — El Enjambre

*Rubicón Lab · El Enjambre · Actualizado el 9 de septiembre de 2026*

> **Para Giorgio, en simple.** Este documento cuenta, sin jerga y a detalle, todo
> lo que medimos para afinar el enjambre, qué decidimos cambiar, qué dejamos
> igual, y en qué punto está la calibración hoy. Es el "estado de cuenta" del
> proyecto: lo puedes leer de arriba a abajo sin saber de código.

---

## 0. La idea en una frase

El enjambre lee una noticia y predice hacia dónde se moverá el mercado. Estábamos
afinando **una sola cosa**: que acierte mejor cuando la noticia es **mala**
(históricamente el enjambre era demasiado optimista y no "veía" bien las malas
noticias). Para eso creamos un panelista nuevo y lo medimos mercado por mercado.

---

## 1. El personaje nuevo: el "Analista de Riesgo Selectivo"

Piensa en el enjambre como un panel de 9 tipos de opinadores (institucionales,
influencers, contrarians, etc.). Notamos que le faltaba **una voz pesimista con
criterio**, así que agregamos un panelista número 9:

- **El Analista de Riesgo Selectivo** (en el código: `doomer_selectivo`).
- **No es un pesimista de manual.** En el 70% de las noticias se queda neutral,
  como cualquiera. Pero cuando ve un **deterioro claro** (una noticia
  genuinamente mala), la lee **a toda su magnitud, sin suavizarla**.
- **Para qué sirve:** evita que las caídas reales se "diluyan" en el optimismo
  del resto del panel.

**El botón que lo controla:** un número llamado `peso_doomer` que va de 0 a 1.
- `0` = el analista está **apagado** (no influye).
- `1.0` = el analista está **a pleno** (máxima influencia).
- `0.5` = a media máquina.

La pregunta de toda esta calibración fue: **¿en qué mercados conviene encenderlo,
y a qué intensidad?**

---

## 2. Cómo medimos (para que confíes en los números)

- **Con exámenes reales, no inventados.** Tenemos un archivo histórico de
  titulares reales de cada mercado, con lo que pasó después. Le damos al enjambre
  cada titular y comparamos su predicción contra la realidad. A eso le llamamos
  "acierto direccional" (¿le achuntó a la dirección?).
- **Muestras COMPLETAS, no atajos.** Medimos TODOS los casos de cada mercado, no
  una muestra chica. Esto importó muchísimo (ver el caso de cripto abajo).
- **Con IA real, no con el respaldo de emergencia.** El enjambre tiene un "plan B"
  de diccionario simple por si se cae la IA. Ese plan B ensucia la medición, así
  que vigilamos que **cada examen se rindiera con IA real** (`con_ia`) y que
  **ninguno cayera al plan B** (`sin_ia = 0`). Todas las mediciones de abajo son
  100% limpias.
- **Comparación justa:** los mismos exámenes se rinden con el analista apagado y
  encendido, para comparar peras con peras.

---

## 3. Resultados por mercado (el corazón del informe)

### 3.1 ÍNDICE — el analista SÍ ayuda ✅

Mercado de índices bursátiles (S&P, IPSA, etc.). Medimos 3 intensidades sobre la
muestra completa:

| Intensidad | Acierto en malas noticias | Acierto en buenas noticias | Global |
|---|---|---|---|
| **Apagado (0)** | 37.97 % | 76.47 % | 55.0 % |
| **Medio (0.5)** | 43.04 % | 73.53 % | 57.5 % |
| **Pleno (1.0)** | **45.57 %** | 73.53 % | **58.1 %** |

**Lo que dice:** encender el analista a pleno mejora el acierto en malas noticias
**+7.6 puntos** (de 38% a 46%), a cambio de un costo chico en buenas noticias
(−2.9). El balance neto es claramente positivo (+3.1 global). **Vale la pena.**

**¿0.5 o 1.0?** El 1.0 gana: cuesta lo mismo en buenas noticias pero rinde más en
malas. No hay "punto dulce" intermedio.

---

### 3.2 CRIPTO — el analista NO ayuda (inerte) ✗

Mercado de criptomonedas. Muestra completa: 220 casos.

| Intensidad | Acierto en malas noticias | Acierto en buenas noticias | Global |
|---|---|---|---|
| **Apagado (0)** | 51.69 % | 86.26 % | 72.3 % |
| **Medio (0.5)** | 52.81 % | 83.97 % | 71.4 % |
| **Pleno (1.0)** | 51.69 % | 85.50 % | 71.8 % |

**Lo que dice:** encender el analista da **exactamente el mismo acierto en malas
noticias que apagado** (46 de 89, idéntico). Cero mejora, y roza para abajo las
buenas noticias. **No vale la pena.**

> ⚠️ **Lección importante:** antes, con una muestra CHICA (100 casos), cripto
> parecía mejorar (+2.2). Al completar los 220 casos, esa mejora **se evaporó**:
> era un espejismo de muestra pequeña. Por eso ahora medimos siempre completo.

---

### 3.3 ACCIÓN — el analista NO ayuda (inerte, medido en septiembre) ✗

Mercado de acciones individuales. Muestra completa: 188 casos.

| Intensidad | Acierto en malas noticias | Acierto en buenas noticias | Global |
|---|---|---|---|
| **Apagado (0)** | 19.74 % (15/76) | 85.71 % (96/112) | 59.0 % |
| **Pleno (1.0)** | 19.74 % (15/76) | 85.71 % (96/112) | 59.0 % |

**Lo que dice:** el analista es **completamente inerte** en acción. No cambia ni
un solo acierto — malas, buenas y global **idénticas al 100%** entre apagado y
encendido. **No vale la pena.**

> 🔍 **Honestidad del proceso:** yo tenía la corazonada de que acción SÍ se
> beneficiaría, porque tiene el **peor** acierto en malas noticias de los tres
> mercados (apenas 19.7%, o sea 1 de cada 5). Pensé que ahí habría más margen.
> **Me equivoqué, y los números lo demostraron.** "Tener margen para mejorar" no
> es lo mismo que "este analista puede mejorarlo". El problema de acción es otro
> —algo estructural del mercado de acciones individuales— que este panelista no
> toca. Preferí medirlo completo antes que adivinar: ahora hay certeza, no
> suposición.

---

## 4. La foto completa: ¿qué cambió y qué no?

### 4.1 Tabla de decisiones por mercado

| Mercado | Analista | ¿Cambió algo? | Evidencia |
|---|---|---|---|
| **Índice** | ✅ **ENCENDIDO (1.0)** | **SÍ se cambió y desplegó** | +7.6 pts en malas noticias |
| **Cripto** | Apagado (0.0) | No (se dejó apagado) | Inerte (0.0 de mejora) |
| **Acción** | Apagado (0.0) | No (ya estaba apagado; confirmado) | Inerte (0.0 de mejora) |
| **Oro** | Apagado (0.0) | No (sin medir aún) | Default conservador |
| **Petróleo** | Apagado (0.0) | No (sin medir aún) | Default conservador |

### 4.2 El único cambio real que se hizo en producción

**Se activó el Analista de Riesgo SOLO en índice (a intensidad 1.0).** Todo lo
demás quedó apagado. A esto le llamamos **"segmentación por mercado"**: el mismo
botón (`peso_doomer`) tiene un valor distinto según el mercado que se está
simulando, en vez de un valor único para todos.

- **Antes:** el analista no existía / estaba dormido para todos.
- **Ahora:** encendido en índice, apagado en el resto.

### 4.3 El gran aprendizaje de esta calibración

El analista **no es un arreglo universal** del optimismo del enjambre. Es una
**mejora angosta pero real**: sirve específicamente para las malas noticias de
**índices bursátiles**, y no aporta en cripto ni en acción. Encenderlo a lo
bruto en todos los mercados habría sido un error (habríamos pagado un costo en
buenas noticias sin ganar nada en las malas de cripto/acción). La segmentación
es lo que la data pidió.

---

## 5. Los seguros y frenos (por si algo sale mal)

Toda la calibración quedó con **botones de reversa** por si acaso:

- **Apagar todo de golpe:** poner `ENJAMBRE_PESO_DOOMER=0` (una variable de
  entorno global). Manda sobre la segmentación en todos los mercados. Sirve para
  medir o para revertir sin tocar código.
- **Apagar solo índice:** poner `peso_doomer_por_mercado.indice` en 0.0.
- **La configuración vive en:** `engine/config/agentes.json` (el archivo de la
  "mezcla de agentes").

---

## 6. Estado de la calibración HOY

| Tema | Estado |
|---|---|
| Analista de Riesgo en índice | ✅ Medido, activado y desplegado |
| Analista de Riesgo en cripto | ✅ Medido, correctamente apagado |
| Analista de Riesgo en acción | ✅ Medido (sept), correctamente apagado |
| Analista de Riesgo en oro | ⬜ Sin medir (apagado por defecto seguro) |
| Analista de Riesgo en petróleo | ⬜ Sin medir (apagado por defecto seguro) |
| Segmentación por mercado (código) | ✅ Implementada y en producción |
| Botones de reversa | ✅ Funcionando |
| Informes escritos | ✅ Al día |

**En una frase:** la calibración del Analista de Riesgo está **cerrada para los
tres mercados principales** (índice, cripto, acción). El único que aportó fue
índice, y ya está funcionando en vivo. Todo lo demás quedó apagado con evidencia.

---

## 7. Lo que queda pendiente (para cuando decidas)

1. **Medir oro y petróleo** con la misma vara (base 0 vs 1.0, muestra completa).
   Son los dos mercados que faltan. Costo bajo si sus cerebros ya están tibios;
   se hace en una sesión corta cuando quieras.
2. **Deuda de realismo (tema aparte, no es del analista):** bajar el "arrastre"
   de la simulación (que el precio de un tick no prediga tanto el siguiente) por
   debajo de 0.10. Es un ajuste de otro tipo, de los "hechos estilizados" del
   mercado. Pendiente en la lista, sin urgencia.

---

## 8. Notas técnicas (por si un programador lee esto después)

- **Costo de medir:** una simulación tarda ~5-6 s por caso **con cualquier valor
  de `peso_doomer`** — el analista NO hace más lento el motor. Las demoras (unas
  tandas de ~7 min, otras de ~20) son de **infraestructura**: latencia variable
  de la API de IA al calentar cerebros en frío, y rendimiento variable de Render
  (plan Standard 2 GB con el modelo de 10.150 agentes).
- **Truco de costo:** los "cerebros" (las llamadas a la IA) se cachean en disco
  por (titular, arquetipo, semilla), **independiente** del valor de `peso_doomer`.
  Por eso medir la base (0) calienta la memoria y luego medir el 1.0 es **casi
  gratis** (reusa la caché; solo se recalcula la mezcla del tono, que es pura
  matemática).
- **Limpieza de muestra:** cada tanda reporta `con_ia` y `sin_ia`. Una tanda
  válida tiene `sin_ia = 0` (todos con IA real). Si se corre sin saldo de IA, los
  casos caen al respaldo léxico y **contaminan** la muestra — por eso nunca se
  mide sin saldo.
- **Archivos relacionados:**
  - `INFORME_DOOMER_SELECTIVO_FINAL.md` — el informe detallado de las mediciones
    0/0.5/1.0 con las tablas por mercado.
  - `engine/config/agentes.json` — la configuración `peso_doomer_por_mercado`.
  - `engine/model.py` — dónde el motor lee el peso por mercado.
  - `engine/contenido/backtest.py` — el motor de los exámenes (`evaluar`).

---

*Fin del estado de calibración. Cualquier duda, pregunta sin miedo — este
documento se puede leer sin saber una línea de código.*
