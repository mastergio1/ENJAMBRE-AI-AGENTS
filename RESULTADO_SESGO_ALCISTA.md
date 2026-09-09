# Diagnóstico del Sesgo Alcista Estructural del Enjambre

*Rubicón Lab · El Enjambre · 9 de septiembre de 2026*

> **Para Giorgio, en simple.** Este es, quizás, el hallazgo más importante de toda
> la investigación. Medí —**gratis**, sobre las 648 predicciones que ya tenemos
> guardadas— cuán alcista es el enjambre, si sus predicciones tienen alguna señal
> real, y si hay un arreglo de matemática pura (sin gastar saldo, sin re-simular).
> El resultado reencuadra **qué es** el enjambre. Se puede leer sin saber una línea
> de código.

---

## 0. Cómo lo medí (sin gastar nada)

Cada caso guardado trae dos números: **lo que el enjambre predijo** (`direccion_pct`,
su movimiento simulado) y **lo que de verdad pasó** (`pct_real`, el movimiento real
del mercado esos días). Comparé los 648 pares. Cero llamadas a la IA, cero
re-simular — pura aritmética sobre datos que ya pagaste.

---

## 1. El sesgo alcista es real y grande

| Medida | Enjambre | Realidad |
|---|---|---|
| **% de casos que predice "sube"** | **71%** | 56% |
| Media del movimiento | +11.6% | +3.1% |
| Mediana del movimiento | +7.9% | +2.3% |

**Lo que dice, en simple:**
- El enjambre dice "sube" en **7 de cada 10** noticias, cuando la realidad sube
  en ~5.6 de cada 10. Se inclina alcista **por construcción**.
- Sus movimientos predichos son mucho más grandes que los reales (mediana +7.9%
  vs +2.3% real). Grita subidas grandes.

> ⚠️ **Un matiz honesto sobre la magnitud:** el número de movimiento del enjambre
> (`direccion_pct`) sale de su libro de órdenes simulado, y **puede no estar en la
> misma escala** que el % real del mercado. Así que el "grita movimientos 3-4x más
> grandes" hay que tomarlo con pinza — parte puede ser un tema de escala, no solo
> de sesgo. Lo que **SÍ es sólido e independiente de la escala** es la inclinación
> de **dirección**: 71% "sube" vs 56% real. Eso es sesgo alcista de verdad.

---

## 2. El hallazgo demoledor: sus predicciones casi no correlacionan con la realidad

La "correlación" mide si predicho y real se mueven juntos (0 = puro ruido; 1 =
predicción perfecta):

| Mercado | Correlación predicho vs real |
|---|---|
| Global | **+0.24** (débil) |
| **Índice** | **+0.01** ← ¡prácticamente CERO! |
| Cripto | +0.29 (la mejor, aún débil) |
| Acción | +0.10 (casi nula) |

**Lo que dice, sin adornos:** como **predictor de cuánto se mueve el mercado**, el
enjambre es **casi ruido**. En índice, literalmente **no hay señal** (+0.01). 

Esto encaja perfecto con el Frente B (cripto/acción): la dirección de corto plazo
**no está en el titular**, así que el enjambre no puede predecirla — y los números
lo confirman con dureza. Lo que el doomer logró en índice fue empujar el **signo**
de las malas noticias un poco (38%→46%), no que el enjambre "lea" el mercado. Fue
capturar el único pedacito de señal que existía (la negatividad macro), no arreglar
la predicción.

---

## 3. La prueba clave: NO existe un arreglo gratis de "recentrado"

La idea tentadora era: *"el enjambre es muy alcista → restémosle el sesgo (movamos
el corte donde decidimos 'sube' vs 'baja') y mejorará."* **Lo probé barriendo TODOS
los umbrales posibles.** El resultado es contraintuitivo pero decisivo:

| Mercado | Acierto hoy (corte en 0) | Mejor umbral posible | Qué le pasa a las negativas |
|---|---|---|---|
| Índice | global 55% | 62% (corte −2.2) | **empeoran** (47%→43%) |
| Cripto | global 68% | 69% (corte −4.0) | **empeoran** (47%→42%) |
| Acción | global 61% | 63% (corte −4.0) | **empeoran** (24%→19%) |

**El resultado incómodo:** el umbral que **mejora el acierto global** lo hace
volviéndose **AÚN MÁS alcista** — porque como la realidad sube el 56% de las veces,
"apostar a que sube" gana de fábrica. Eso mejora el global pero **hunde las
negativas**. Y al revés: cualquier corte que mejore las negativas, hunde el global
y las positivas.

> **La conclusión dura:** **no puedes arreglar las negativas moviendo un número.**
> Cuando no hay señal (correlación ~0), lo mejor que puedes hacer con el global es
> apostar a la tendencia de fondo (que sube), y eso sacrifica las negativas. No hay
> almuerzo gratis. El único pedazo explotable —la negatividad macro de índice— el
> doomer ya lo tomó.

---

## 4. El reencuadre (la opinión fuerte y honesta)

**El enjambre no es un buen predictor de dirección, y ningún ajuste barato lo va a
volver uno — porque la información no está en el input.**

Pero —y esto es lo importante— **eso NO es un fracaso**, porque tu producto **no es
un predictor**. Es:

> *"El focus group sintético del mercado"* — un **simulador del comportamiento de
> masas**, educativo, con la **visualización 3D en vivo** como diferenciador. Y con
> el filtro CMF que **prohíbe** venderlo como predicción o consejo de inversión.

Entonces el verdadero problema del sesgo alcista **no es** "acierta poco la
dirección" (eso está topado por la falta de señal en el input, y no hay cómo
arreglarlo barato). El problema real es:

> **El enjambre se comporta de forma poco realista: se pone alcista y grita subidas
> grandes hasta cuando no debería, incluso ante malas noticias.**

Eso **sí importa** — pero por **REALISMO**, no por acierto. Y el realismo es
justamente lo que hace creíble a tu producto. Un "focus group" que ante una quiebra
dice "+12%" no es creíble; uno que reacciona con miedo, sí.

---

## 5. Lo que yo atacaría, y cómo (cuidando el saldo)

El sesgo vive en la **mezcla de agentes** (CLAUDE.md §4):
- Los **fondos pasivos** que "compran constante, insensibles a noticias".
- Los **FOMO** que persiguen subidas.
- Juntos crean una **corriente alcista de fondo** que empuja el precio arriba pase
  lo que pase.

**La corrección:** darle más peso/agresividad a los **miedosos / aversión a
pérdida** (§4 #10) y/o bajar el empuje comprador estructural, para que el enjambre
reaccione **creíblemente** a las malas noticias.

**Los dos frenos que hay que respetar:**
1. **Cambiar la mezcla cambia la simulación → hay que re-correr** (eso **sí gasta
   saldo**) para medir el efecto.
2. **No puede romper los "hechos estilizados"** (CLAUDE.md §7), en especial la
   **"asimetría de pánico"**: las caídas deben ser más rápidas y violentas que las
   subidas. Si al corregir el sesgo rompemos otro test de realismo, no sirve.

---

## 6. El siguiente paso — GRATIS, antes de gastar nada

Antes de tocar la mezcla o gastar un peso: **correr los tests de hechos estilizados
que ya existen** (`engine/validation/`). Si el enjambre rebota demasiado fácil, la
**asimetría de pánico** debería estar **fallando hoy** — y eso nos daría, gratis:
1. La confirmación de que el sesgo es un **bug de realismo medible** (no solo una
   corazonada).
2. Un **termómetro objetivo** para saber, más adelante, si una corrección de la
   mezcla lo mejora **sin** romper el resto.

---

## 7. Resumen del mapa completo (todo lo investigado)

| Hallazgo | Estado |
|---|---|
| Ensemble de sentimiento (Fase 1) | ❌ Descartado: ataca la capa equivocada, no cabe en Render |
| El cuello de botella es el sentimiento | ❌ Falso: el LLM ya lee bien; el problema es la agregación |
| Doomer en índice | ✅ Funciona (+7.6 pts negativas) — captura la negatividad macro |
| Doomer en cripto/acción | ❌ Inerte: la dirección no está en el titular (80-90% de los fallos) |
| Doomer en oro/petróleo | ⏸️ No medido: bajo prior, muestras diminutas, para oro podría dañar |
| **Sesgo alcista estructural** | 🔴 **Confirmado (71% vs 56%), sin señal de magnitud (~0), sin arreglo gratis de recentrado** |
| **Naturaleza del enjambre** | 🔵 **Es un SIMULADOR/focus-group, no un predictor. El foco debe ser REALISMO.** |

**La gran lección de toda la investigación:** dejamos de perseguir "acierto de
predicción" (que está topado porque la info no está en el input) y pasamos a
perseguir **realismo del comportamiento** — que es lo que de verdad vende el
producto, y donde el sesgo alcista sí es un bug atacable.

---

## Anexo — Datos y método

- Casos: `datos/calibracion.json` (rama `respaldo-datos`), 648 con predicción y
  resultado real.
- Campos usados: `direccion_pct` (predicción del enjambre) y
  `reaccion_real.pct_real` (movimiento real). Ambos ya guardados: cero IA.
- Caveat: `direccion_pct` es la captura histórica del backtest (puede diferir un
  poco de la re-simulación de `evaluar`, que usa otra semilla/config). El sesgo
  direccional y la baja correlación son robustos igual.

---

*Fin del diagnóstico del sesgo alcista.*
