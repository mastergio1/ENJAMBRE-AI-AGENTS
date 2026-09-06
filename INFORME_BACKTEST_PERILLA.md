# Backtests de la perilla P2 — cuentas exactas y qué pasó

**Fecha:** 6 de septiembre de 2026
**Qué es esto:** el detalle de los backtests que corrimos moviendo la perilla `peso_tono_invertidores` (la que decide cuánto pesan los líderes "invertidores" en el clima del mercado). Con el LLM real en Render, sobre exámenes históricos respaldados.

> **Aclaración honesta:** medimos **0.0, 0.3 y 1.0** (la base actual). **0.1 no se corrió** — al final del archivo explico por qué y cómo pedirlo si lo quieres (es barato).

---

## 1. Qué son los "respaldados" y cuántos exámenes

Un **examen respaldado** es un caso histórico donde el enjambre ya opinó *y además sabemos qué hizo el mercado de verdad después*. Eso permite corregir el examen: comparar la dirección que predijo el enjambre contra la dirección real.

- **Casos respaldados totales (todos los mercados):** **645**
- **Categorizados (con reacción real conocida):** 609
- **Del mercado ÍNDICE (donde hicimos el barrido completo):** **163 exámenes**
  - **81 negativas** (el mercado cayó ≥1%)
  - **69 positivas** (el mercado subió ≥1%)
  - **13 neutras** (se movió menos de 1%)
- **Del mercado CRIPTO (medición chica, solo como sonda):** **20 exámenes** (18 negativas, 2 positivas)

La categoría (negativa/positiva/neutra) la define **lo que hizo el mercado real**, no el tono de la noticia. Por eso sirve para calificar el acierto.

---

## 2. ÍNDICE — el barrido completo (163 exámenes)

Este es el resultado que manda, porque es la muestra completa y la misma para las tres posiciones (mismos casos, mismas semillas → aísla el efecto de la perilla).

| Perilla | Negativas (81) | Positivas (69) | Neutras (13) | Global (163) |
|---|---|---|---|---|
| **1.0** — actual (P2 apagado) | **44/81 = 54.3%** | **50/69 = 72.5%** | 8/13 = 61.5% | **102/163 = 62.6%** |
| **0.3** — P2 suave | 44/81 = 54.3% | 48/69 = 69.6% | 7/13 = 53.8% | 99/163 = 60.7% |
| **0.0** — P2 pleno | 45/81 = 55.6% | 46/69 = 66.7% | 6/13 = 46.2% | 97/163 = 59.5% |

**Lo que pasó, en una frase:** mover la perilla hacia P2 **no gana casi nada en negativas** (0.3 da los mismos 44 aciertos que la base; 0.0 sube 1 solo) y **sí resta en positivas y en el global**. No hay punto dulce.

---

## 3. Cómo cada barrido se armó por tandas (y cómo se desinfló la ilusión)

Cada backtest se corrió en **tandas de 40 exámenes** (para no reventar la memoria del servidor), acumulando hasta los 163. Aquí se ve por qué **no hay que creerle a las muestras chicas**: mira la columna de negativas de la perilla 0.3, cómo baja del 62.5% inicial al 54.3% final.

### Perilla 0.3 (acumulado)
| Exámenes | Negativas | Positivas | Global |
|---|---|---|---|
| 40 | 15/24 = **62.5%** ← la ilusión | 9/13 = 69.2% | 65.0% |
| 80 | 25/46 = 54.3% | 17/25 = 68.0% | 57.5% |
| 120 | 34/62 = 54.8% | 30/47 = 63.8% | 57.5% |
| 160 | 42/79 = 53.2% | 47/68 = 69.1% | 60.0% |
| **163** | **44/81 = 54.3%** ← la verdad | **48/69 = 69.6%** | **60.7%** |

### Perilla 1.0 — base (acumulado)
| Exámenes | Negativas | Positivas | Global |
|---|---|---|---|
| 40 | 12/24 = 50.0% | 8/13 = 61.5% | 55.0% |
| 80 | 26/46 = 56.5% | 15/25 = 60.0% | 57.5% |
| 120 | 34/62 = 54.8% | 32/47 = 68.1% | 60.0% |
| 160 | 42/79 = 53.2% | 49/68 = 72.1% | 61.9% |
| **163** | **44/81 = 54.3%** | **50/69 = 72.5%** | **62.6%** |

### Perilla 0.0 (acumulado)
| Exámenes | Negativas | Positivas | Global |
|---|---|---|---|
| 40 | 15/24 = 62.5% | 8/13 = 61.5% | 62.5% |
| 80 | 28/46 = 60.9% | 13/25 = 52.0% | 56.3% |
| 120 | 35/62 = 56.5% | 30/47 = 63.8% | 57.5% |
| 160 | 43/79 = 54.4% | 45/68 = 66.2% | 58.8% |
| **163** | **45/81 = 55.6%** | **46/69 = 66.7%** | **59.5%** |

**Detalle técnico:** en 0.0 y 0.3, las tandas 1–4 fueron de 40 exámenes y la 5ª de 3 (para cerrar los 163). Cada tanda tomó ~7 minutos. El barrido fue **gratis en saldo**: la caché de cerebros ya estaba pagada de la primera corrida, y la perilla solo cambia cómo se promedian las señales, no las llamadas al LLM.

---

## 4. CRIPTO — la sonda chica (20 exámenes) que nos engañó primero

Antes del barrido completo, una medición chica en cripto (18 negativas) fue la que **prendió la ilusión**:

| Perilla | Negativas (18) | Positivas (2) | Global (20) |
|---|---|---|---|
| **1.0** — base | 11/18 = 61.1% | 1/2 = 50% | 60% |
| **0.0** — P2 | **13/18 = 72.2%** | 1/2 = 50% | **70%** |

**+11 puntos en negativas** se veía espectacular. Pero eran 18 casos. Cuando repetimos la lógica a escala completa en índice (81 negativas), la ventaja se evaporó. **No gastamos más en cripto** justamente por eso: el mecanismo ya había quedado refutado donde importaba.

---

## 5. Qué pasó, en limpio

1. **Las muestras chicas mintieron:** cripto (18 neg) y los primeros 40 de índice daban +11/+12 puntos. Era ruido.
2. **La muestra completa (163) los desmintió:** la perilla no aporta aciertos reales en negativas y cuesta en positivas.
3. **Ningún nivel de la perilla sirve:** 0.0 y 0.3 son variantes del mismo error (uno más fuerte, otro más suave). El mejor valor es **1.0** — dejar todo como está.
4. **Decisión:** P2 archivado, perilla en **1.0** (que es el valor por defecto en producción → **nada que revertir**). Presupuesto de $48.66 intacto.

---

## 6. Sobre el 0.1 que mencionaste

No lo corrimos, y por una razón: la perilla es **casi lineal** entre 1.0 y 0.0. El 0.1 caería **entre el 0.0 y el 0.3**, y los dos ya son peores que la base. No hay motivo físico para esperar que justo en 0.1 aparezca un punto dulce que no está ni en 0.3 ni en 0.0.

Dicho eso: **correrlo es barato** (la caché está caliente, ~5 tandas de 7 min, cero saldo). Si quieres cerrar la duda del todo y verlo con tus ojos, dímelo y lo tiro. Mi apuesta honesta: dará ~54% en negativas (igual que la base) y algo menos en positivas — un punto más de la misma curva descendente.

---

*Mediciones: workflow "Evaluar acierto (P2)" → `/api/evaluar` (Render, LLM real), runs #17–#26.
Cierre y decisión: `INFORME_P2_CIERRE.md`. Bitácora de toda la sesión: `INFORME_SESION_COMPLETA.md`.*
