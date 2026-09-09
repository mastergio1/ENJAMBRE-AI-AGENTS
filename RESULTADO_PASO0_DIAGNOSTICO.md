# Resultado del Paso 0 — Diagnóstico barato del sentimiento

*Rubicón Lab · El Enjambre · 9 de septiembre de 2026*

> **Para Giorgio, en simple.** Antes de construir el ensemble de sentimiento de la
> Fase 1, hice el diagnóstico de un día que prometí: **sin gastar saldo de IA**,
> sobre los 648 casos reales que ya tenemos. La pregunta era una sola: *¿el cuello
> de botella de las malas noticias es la MEDICIÓN del sentimiento, o es otra cosa?*
> La respuesta es clara, y **cambia la recomendación** (para mejor).

---

## 1. Qué hice (el método, sin jerga)

Para cada mala noticia histórica comparé dos cosas:

- **(A)** ¿El **léxico** (el lector barato y gratis del motor) detecta que la
  noticia es negativa? — puro cálculo, cero IA.
- **(B)** ¿El **enjambre completo** (con los líderes LLM) acierta la dirección? —
  esto ya lo medimos con el doomer.

**La lógica:** si el enjambre, que usa lectores LLM mucho más potentes que
cualquier FinBERT/VADER, **no le gana** al léxico crudo… entonces meter un
ensemble de modelos *más débiles que el LLM* no va a subir el techo. El problema
estaría en otro lado.

---

## 2. Los números (609 casos con nota real)

### Negativas (malas noticias) — 264 casos

| | Léxico detecta la dirección | Enjambre completo acierta |
|---|---|---|
| **Global** | **37.5%** (99/264) | — |
| Índice | **38%** (31/81) | **38%** ← igualito |
| Cripto | **55%** (49/89) | **52%** ← casi igual |
| Acción | **18%** (14/76) | **20%** ← casi igual |

**El hallazgo que salta a la vista:** mercado por mercado, **lo que detecta el
léxico crudo ≈ lo que acierta el enjambre completo.** La brecha es de 0 a 3
puntos. Es un calce sorprendentemente ajustado en los tres mercados.

### Positivas (buenas noticias) — 329 casos

| | Léxico detecta | Enjambre acierta |
|---|---|---|
| Global | **23%** (77/329) | **~85%** |

Aquí pasa lo **contrario**: el léxico es malísimo (23%) pero el enjambre es
buenísimo (85%). Enorme diferencia.

---

## 3. Qué significa todo esto (la interpretación honesta)

### 3.1 En negativas: mejor lector NO da mejor resultado

El enjambre usa **líderes LLM** — lectores muchísimo mejores que el léxico, y
mejores que cualquier ensemble de FinBERT/VADER. Y sin embargo, en malas noticias,
**el enjambre acierta casi lo mismo que el léxico crudo** (38/38, 52/55, 20/18).

> **Conclusión dura:** el techo NO es la calidad de lectura del sentimiento. Si el
> LLM (el mejor lector disponible) ya está pegado al techo del léxico, un ensemble
> de modelos *más débiles* no tiene forma de subirlo. **El ensemble de la Fase 1
> ataca la capa equivocada.**

### 3.2 En positivas: el enjambre gana por SESGO, no por leer

El enjambre acierta el 85% de las buenas noticias, pero **no porque las lea bien**
(el léxico solo ve el 23%). Las acierta porque **el enjambre por construcción
tiende a decir "sube"** — la mayoría de sus agentes tienen un sesgo alcista de
fábrica. Cuando la noticia de verdad es buena, ese optimismo "acierta". Cuando es
mala, ese mismo optimismo **hace fallar**.

> Esto confirma toda la historia del proyecto: el problema de las negativas es el
> **sesgo alcista estructural en la AGREGACIÓN**, no la medición del sentimiento.

### 3.3 De las 165 negativas que el léxico falla, ¿qué son?

- **143 son "mudas"** (el léxico no vio nada, puntaje 0). Aquí hay **algo** de
  brecha de vocabulario — pero ojo: los líderes LLM SÍ leen estos titulares, y el
  enjambre igual falla. O sea, la mayoría no se arreglan leyendo mejor: fallan
  porque la negatividad no alcanza a vencer el sesgo alcista, o porque la dirección
  simplemente **no está en las palabras**.
- **22 están "al revés"** (el léxico las leyó como positivas). Son casos donde la
  dirección va **contra** el sentimiento del titular: oro como refugio ("guerra"
  sube el oro… o lo baja, según el día), "compra la caída" que salió mal,
  posicionamiento macro. **Ningún** modelo de sentimiento arregla estos.

---

## 4. El veredicto (fuerte y sincero)

**El cuello de botella NO es la medición del sentimiento. Es el sesgo alcista
estructural del enjambre en la agregación.** Tres pruebas que apuntan a lo mismo:

1. **Mejor lector no gana:** el LLM no le gana al léxico crudo en negativas → la
   calidad de lectura no es el techo.
2. **Las positivas se ganan por defecto:** el enjambre acierta buenas noticias por
   su optimismo de fábrica, no por leer → la máquina se inclina alcista por
   construcción.
3. **El doomer YA funcionó:** una intervención de *agregación* (corregir el sesgo)
   mejoró índice +7.6 pts. Ese es el lever que sí mueve la aguja.

> **Por lo tanto: NO construir el ensemble de la Fase 1.** Un ensemble de
> FinBERT/VADER (más débiles que el LLM que ya tienes) tiene ~cero probabilidad de
> subir el techo, no cabe en Render, y ataca la capa equivocada. El Paso 0 nos
> ahorró 1-2 semanas de trabajo que habría dado casi nada — igual que sospechábamos,
> ahora con datos.

**Nota de honestidad:** en mi revisión inicial supuse que el sentimiento "se
detectaba pero se perdía río abajo". El diagnóstico afinó (y corrigió en parte) esa
idea: en realidad el enjambre está **topado cerca del límite de lo que el texto
permite leer**, y su sesgo alcista es lo que hunde las negativas. Distinto matiz,
misma conclusión: el ensemble no es el camino.

---

## 5. Lo que el diagnóstico SÍ recomienda hacer

En vez del ensemble, dos frentes — ambos baratos y alineados con lo que ya
funciona:

1. **Seguir con la corrección de sesgo por mercado (estilo doomer)** — es el único
   lever que demostró mover negativas. Lo que queda por explorar ahí: **medir oro y
   petróleo** (sin medir aún), y buscar para **acción** una corrección distinta
   (el doomer fue inerte en acción, pero su problema — 18-20% — es el peor de
   todos, así que merece su propia intervención de agregación, no de sentimiento).

2. **Mejora barata del léxico** (opcional, secundaria): rellenar el vocabulario de
   las 143 "mudas" (frases como *"under pressure"*, *"sell stocks"*, *"yields
   surge"*, *"breaking down"*). Ayuda al camino de respaldo (`sin_ia`) y le da un
   mejor punto de partida a los líderes. Pero es incremental: no toca los casos
   donde la dirección no está en las palabras.

**Lo que NO haría:** meter transformers pesados (FinBERT/RoBERTa) a Render, ni
armar el ensemble de 4 modelos. Los datos dicen que no rendiría.

---

## 6. Caveat metodológico (para ser justos)

Este diagnóstico usa el **léxico como proxy barato** del "lector de sentimiento" y
lo compara contra el acierto agregado del enjambre (de las corridas del doomer). El
calce tan ajustado en **tres mercados** es una señal fuerte, pero no es una traza
caso-por-caso del tono real de los líderes LLM. Una versión 100% rigurosa
registraría, por cada caso fallado, el tono exacto del LLM — pero eso **sí gasta
saldo**, y la evidencia agregada (más el hecho de que el LLM no le gana al léxico)
ya es bastante concluyente para tomar la decisión sin gastar.

---

## Anexo — Datos y script

- Casos: `datos/calibracion.json` (rama `respaldo-datos`), 648 casos, 609 con nota
  real (264 negativas, 329 positivas, resto neutras).
- Léxico: `engine/brains/fallback.py` → `sentimiento_lexico()` (cero IA).
- Acierto del enjambre por mercado: de las mediciones del doomer (base 0),
  documentadas en `ESTADO_CALIBRACION.md` e `INFORME_DOOMER_SELECTIVO_FINAL.md`.
- El diagnóstico corre local y gratis; se puede repetir cuando el banco de casos
  crezca.

---

*Fin del resultado del Paso 0.*
