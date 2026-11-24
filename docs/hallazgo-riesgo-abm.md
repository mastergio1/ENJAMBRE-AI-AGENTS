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

## Qué NO cierra (la versión completa de H14)

Este pase usa solo las **salidas escalares** del ABM (volatilidad y magnitud simuladas,
dispersión del consenso). Las features **ricas de microestructura** que propone la
auditoría —order-flow imbalance, índice de manada, forma de la trayectoria, expected
shortfall virtual, velocidad del consenso— **no están en los datos**: requieren
**re-correr simulaciones exportándolas** (factible por el motor, como el barrido de
población). Es el experimento pendiente para cerrar H14. El primer pase no es
alentador, pero esas features aún no se han probado.
