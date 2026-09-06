# Informe Fase 0 — Desglose: ¿dónde acierta y dónde falla el enjambre?

**Rama:** `feature/calibracion-70-porciento` (aislada — `main` y el motor en producción NO fueron modificados)
**Fecha:** 5 de septiembre de 2026
**Base:** 645 exámenes reales ya rendidos por el motor (respaldo público de GitHub, sin key ni costo).

---

## 0. Resumen ejecutivo

- **Línea base:** el enjambre acierta la dirección del mercado **60.9%** de las veces (azar = 50%).
- **Es fuerte en cripto (68%) y con buenas noticias (80%).**
- **Es débil en índices (55%) y, sobre todo, con malas noticias (38% — peor que el azar).**
- El culpable del punto débil es coherente con el diseño: la **asimetría de pánico** del enjambre lo hace sobre-reaccionar a titulares negativos que el mercado real muchas veces ignora.

## 1. Qué se hizo

Se extendió la herramienta de Fase 0 (`engine/calibration/validacion_base.py`, flag `--desglose`) para cortar los 645 exámenes por tres dimensiones: **mercado**, **magnitud del movimiento real** y **sentimiento de la noticia**. No corre simulaciones nuevas (no gasta LLM): puntúa lo ya rendido.

- **Mercado:** se infiere del símbolo medido (SPY/QQQ → índice, COIN/BTC/MSTR → cripto…), con el mismo mapa que `engine/contenido/backtest.py`.
- **Sentimiento:** del campo `categoria` de cada caso (positiva/negativa/neutra).
- **Magnitud:** del `pct_real` (grande >1%, medio 0.5-1%, ruido <0.5%).

## 2. Resultados (645 exámenes)

### 2.1 Por mercado
| Mercado | n | Acierto de dirección | Correlación |
|---|---:|---:|---:|
| **Cripto** | 220 | **68.2%** 🟢 | +0.286 |
| Acción | 221 | 60.6% | +0.105 |
| Índice | 165 | 55.2% 🟡 | +0.014 |
| Oro | 13 | 46.2% | +0.217 |
| Petróleo | 26 | 46.2% | −0.013 |

Más fuerte donde manda la **manada y la emoción** (cripto); más débil en **índices** (el SPY es eficiente y difícil de anticipar). Oro y petróleo tienen muestra chica (n bajo): tómalos con pinzas.

### 2.2 Por magnitud del movimiento real
| Magnitud | n | Acierto |
|---|---:|---:|
| Grande (>1%) | 617 | 61.4% |
| Medio (0.5-1%) | 14 | 57.1% |
| Ruido (<0.5%) | 14 | 42.9% |

Acierta en los movimientos que **importan**; el ruido (<0.5%) es impredecible por definición, así que caer a ~43% ahí es esperable y no preocupa.

### 2.3 Por sentimiento de la noticia — **el hallazgo clave**
| Sentimiento | n | Acierto |
|---|---:|---:|
| **Positiva** | 329 | **79.6%** 🟢 |
| Neutra | 16 | 50.0% |
| **Negativa** | 264 | **38.3%** 🔴 |

### 2.4 Por origen (control de sanidad)
| Origen | n | Acierto | Correlación |
|---|---:|---:|---:|
| En vivo | 36 | 61.1% | +0.128 |
| Histórico | 609 | 60.9% | +0.250 |

El resultado se sostiene en vivo y en histórico: no es un artefacto de un solo lote.

## 3. El hallazgo importante, explicado

El enjambre es **excelente con buenas noticias (80%)** pero **falla con las malas (38%, peor que una moneda)**. La causa es coherente con cómo está construido:

- El enjambre lleva **asimetría de pánico** por diseño (agentes miedosos, cascadas a la baja). Eso es lo que hace que **pasen los hechos estilizados** (las caídas reales son más violentas que las subidas — `CLAUDE.md` §7).
- Pero ese mismo motor lo hace **sobre-reaccionar** a cualquier titular negativo: el enjambre se derrumba, mientras el **mercado real a menudo ignora** la mala noticia (ya estaba en el precio, o rebota).
- Resultado: ante noticias negativas, el enjambre apunta abajo y el mercado no lo acompaña → falla la dirección el 62% de las veces.

El 60.9% global **esconde** esta asimetría: un enjambre que entiende la euforia pero **exagera el pánico**.

## 4. La palanca (si se quiere subir la línea base)

Moderar la reacción del enjambre a titulares **negativos** — sin romper la asimetría de pánico que necesita para los hechos estilizados. Es un equilibrio fino, y ahora **medible**: cualquier ajuste se vuelve a puntuar con `validacion_base.py --desglose` y se compara el acierto en negativas (hoy 38%) sin dañar el de positivas (80%) ni los hechos estilizados (`engine/validation/`).

> ⚠️ Cuidado de no sobreajustar: la meta no es "clavar" estos 645 casos, sino
> que el enjambre sea razonable en general. Cualquier cambio se valida también
> contra los 5 hechos estilizados antes de adoptarlo.

## 5. Lo honesto para el cliente / marco CMF

- Afirmación defendible: *"el enjambre acierta la dirección del mercado ~6 de cada 10 veces, y hasta 8 de 10 con noticias positivas"*.
- Afirmación que NO se debe hacer: que predice precios o que es asesoría. Es un **focus group sintético** — informa y simula, nunca aconseja.

---

*Herramienta: `engine/calibration/validacion_base.py --desglose`. Lee el respaldo
público de exámenes del motor. `main` y el motor en producción: sin cambios.*
