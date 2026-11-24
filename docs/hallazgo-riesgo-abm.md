# Hallazgo — El ABM tampoco predice el riesgo (primer pase). Fase 4.

*Rubicón Lab · El Enjambre · 2026-11-24. Fase 4 del plan maestro v5, hipótesis H14 de
la auditoría: ¿el enjambre predice la MAGNITUD del movimiento (riesgo/volatilidad)
aunque no acierte la dirección? Herramienta: `engine/calibration/riesgo_abm.py` (con
tests). Primer pase SIN re-correr simulaciones: usa las salidas de riesgo que el
dataset ya tiene. Objetivo: `|pct_corr|` (magnitud real, sin fuga). Exploratorio. Sin IA.*

## Resultado

### ÍNDICE (165 casos)
Correlación de rango (Spearman) con la magnitud real — **todas ≈ 0 o negativas**:

| Feature del ABM | Spearman |
|---|---:|
| volatilidad simulada | −0.118 |
| magnitud simulada `|dir|` | −0.004 |
| dispersión del consenso | −0.076 |
| `|consenso|` (baseline) | −0.143 |

Error fuera de muestra al predecir la magnitud (MAE, menor = mejor):

| Modelo | MAE |
|---|---:|
| constante (media) | 1.222 |
| solo `|consenso|` | 1.200 |
| **+ features ABM** | **1.283** ← peor |

**En índice el ABM NO predice el riesgo:** sus salidas no rankean la magnitud real, y
añadirlas EMPEORA la predicción frente a un baseline trivial.

### TODOS los mercados (618 casos)
Pista **muy débil**: `+ features ABM` baja el MAE a 2.588 (vs 2.705 del constante,
~4 % mejor), empujado por `|dir_abm|` (Spearman +0.195). Pero todas las correlaciones
son < 0.2: no es un predictor de riesgo usable.

## Qué significa

1. **La hipótesis que podía rescatar al ABM (predecir riesgo, no dirección) no se
   sostiene en este primer pase.** En índice es nula/negativa; en todos los mercados,
   apenas un hint que no alcanza para un producto.
2. Es la 6ª evidencia consistente: el ABM, con lo que hoy produce, no aporta valor
   predictivo medible — ni en dirección ni en magnitud.

## Segundo pase — features RICAS de microestructura (re-corriendo sims). H14 CERRADA.

Se re-corrieron las 142 simulaciones de índice extrayendo la microestructura del tramo
posterior a la noticia. Correlación de rango (Spearman) con la magnitud real:

| Feature rica del ABM | Spearman |
|---|---:|
| volatilidad simulada | +0.024 |
| desequilibrio de órdenes | −0.039 |
| sobre-reacción (overshoot) | −0.079 |
| reversión | −0.003 |
| rango | −0.023 |
| dispersión del consenso | −0.003 |

**Todas ≈ 0.** Y al predecir la magnitud fuera de muestra, añadir las features ricas
EMPEORA: MAE 1.241 vs 1.172 del baseline trivial (la media).

**H14 cerrada en NEGATIVO:** ni las salidas escalares ni las features ricas de
microestructura del ABM predicen cuánto se mueve el mercado. El enjambre **tampoco
predice el riesgo**.

## Veredicto de la Fase 4

La hipótesis que podía rescatar al ABM (predecir riesgo/volatilidad aunque no la
dirección) **no se sostiene**. Es la 6ª evidencia consistente: el motor de agentes no
aporta valor predictivo medible — ni dirección ni magnitud. Su valor es de **producto
y visualización**. Caveat de siempre: exploratorio (banco histórico, 1 semilla, n=142);
el veredicto último es prospectivo, pero la señal (su ausencia) es clara y repetida.
