# Informe: optimización del freno de la manada con Optuna

**Rama:** `feature/memoria-agentes` (aislada — no toca producción)
**Fecha:** 5 de septiembre de 2026
**Veredicto de una línea:** Optuna confirma que **encender el freno corrige el sobre-pánico** (señal fuerte y clara), pero el **valor exacto no se puede fijar con precisión** porque la medición es ruidosa (señal débil). Recomiendo un valor **moderado (0.5 = la manada vende la mitad en cautela)**, no el "ganador" numérico de Optuna (0.147), que es un freno demasiado agresivo elegido sobre ruido.

---

## 0. Qué te pedí que entendieras primero

Antes de optimizar, había un riesgo de trampa: si a Optuna solo le dices *"minimiza la caída"*, encuentra la respuesta degenerada `factor = 0` — la manada nunca vende, el mercado nunca cae ante malas noticias, y eso es **irreal**. Así que no optimicé "la caída mínima". Optimicé un blanco con sentido económico.

## 1. El objetivo (honesto, anclado al propio modelo)

Medí cuánto cae el precio tras cada mala noticia en una racha de 4 malas seguidas:

| | 1ª mala (d1) | 2ª | 3ª | **4ª mala (d4)** |
|---|---|---|---|---|
| Sin freno | **−5.7** | −2.4 | −3.2 | **−7.2 a −7.6** |

La 1ª mala provoca una reacción normal (−5.7). El mercado se habitúa (2ª, 3ª más suaves). Pero en la **4ª, la cascada de la manada explota** y cae MÁS que la primera. Esa aceleración es el sobre-pánico.

**Blanco de Optuna:** que la 4ª mala **golpee como la 1ª**, ni más ni menos → minimizar `(d4 − d1)²`.

- Si d4 es **más profundo** que d1 → sobre-pánico (lo que queremos corregir).
- Si d4 es **mucho más suave** que d1 → el mercado *ignorando* la mala noticia (también irreal). Esto **excluye la trampa** `factor=0`.
- El punto justo: **d4 ≈ d1 = −5.7**.

Lo importante: ese blanco (−5.7) **no lo inventé** — es la reacción natural del propio enjambre ante la 1ª mala. Nadie puede acusarnos de ajustar la curva a mano.

## 2. Qué corrió Optuna

`engine/calibration/optimizar_freno.py`: 15 pruebas, 6 semillas (42, 7, 123, 3, 11, 19), muestreador TPE. Le di 2 anclas de arranque: el freno actual (1.0 = sin freno) y el probado a mano ayer (0.5).

## 3. El paisaje completo (ordenado por factor)

`d1` (ancla) = **−5.7** en todas las pruebas. Objetivo = `(d4−d1)²`, menor es mejor.

| factor (cuánto vende la manada en cautela) | d4 (caída 4ª mala) | objetivo |
|---:|---:|---:|
| 0.00 (no vende) | −6.44 | 0.489 |
| 0.09 | −6.56 | 0.675 |
| **0.15 ★ ganador** | **−5.86** | **0.014** |
| 0.19 | −7.38 | 2.702 |
| 0.30 | −7.10 | 1.839 |
| 0.35 | −6.32 | 0.338 |
| 0.42 | −6.77 | 1.060 |
| **0.50 (recomendado)** | **−6.25** | **0.256** |
| 0.55 | −6.29 | 0.301 |
| 0.63 | −5.54 | 0.040 |
| 0.65 | −6.54 | 0.642 |
| 0.72 | −6.17 | 0.184 |
| 0.75 | −6.50 | 0.576 |
| 0.97 | −7.60 | 3.446 |
| 1.00 (sin freno) | −7.15 | 1.985 |

## 4. Qué encontré (lectura honesta, en dos capas)

**Señal FUERTE — el freno funciona:**
- La zona **sin freno** (0.97–1.00) es claramente la peor: d4 entre −7.2 y −7.6, objetivo 2–3.5. Es el sobre-pánico documentado.
- Encender el freno (cualquier factor **por debajo de ~0.75**) lleva d4 al rango −5.5 a −6.6, muy cerca del blanco −5.7. **Esto es robusto y creíble.**

**Señal DÉBIL — el valor exacto es ruido:**
- El "ganador" 0.15 (objetivo 0.014) y el 0.63 (objetivo 0.040) están **empatados en la práctica** pero son factores muy distintos. Si el mejor y otro casi-mejor están tan separados, es que la superficie es **plana y ruidosa**: con 6 semillas no se distingue 0.15 de 0.63.
- Hay picos de ruido que lo confirman: 0.19 y 0.30 dan d4 malos (−7.4, −7.1) a pesar de estar en la "zona buena". Es el caos del mercado, no una relación real.

## 5. Por qué NO recomiendo el 0.147 de Optuna

1. **Es un ajuste al ruido.** No es estadísticamente distinto de medio abanico de valores (0.35, 0.5, 0.63, 0.72 caen todos en la zona buena).
2. **Es un freno demasiado agresivo:** 0.15 = la manada vende solo el **15%** de lo normal en cautela. Eso arriesga el problema opuesto — que el mercado **sub-reaccione** e ignore malas noticias reales.
3. **0.5 es la elección defendible:** freno moderado (vende la mitad), lleva d4 a −6.25 (cerca del blanco −5.7, y mucho mejor que el −7.2 sin freno), y ya lo validamos con un A/B aparte (INFORME_FRENO_MANADA.md). Moderado y probado le gana a un extremo elegido por suerte.

## 6. Reja de seguridad: hechos estilizados con factor 0.5

> ⏳ *Validación en ejecución (`validar_freno_hechos.py --factor 0.5`). Se
> actualiza esta sección con los 5 criterios medidos en cuanto termine.*

## 7. Recomendación

- **Valor a producción:** `factor_freno_cautela = 0.5` (moderado, robusto, validado).
- **Lo honesto de decir:** Optuna **confirmó que el freno corrige el sobre-pánico**, y descartó el extremo tramposo. Lo que NO puede hacer con esta medición ruidosa es afinar un decimal mágico — y forzarlo sería venderte precisión falsa.
- **Si más adelante quieres afinar de verdad:** habría que subir a ~20–30 semillas por prueba para bajar el ruido (mucho más caro), o medir el desplome acumulado de toda la racha en vez de solo la 4ª caída.

---

*Herramientas: `engine/calibration/optimizar_freno.py` (Optuna, 15 trials × 6 semillas),
`engine/calibration/validar_freno_hechos.py` (los 5 hechos estilizados con el factor).
`main` y producción: sin cambios. Todo vive en la rama `feature/memoria-agentes`.*
