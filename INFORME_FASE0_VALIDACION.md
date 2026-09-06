# Informe Fase 0: Validación Base — ¿el enjambre reacciona como el mercado real?

**Rama:** `feature/calibracion-70-porciento` (aislada — `main` y el motor en producción NO fueron modificados)
**Fecha:** 5 de septiembre de 2026
**Conclusión de una línea:** el enjambre acierta la **dirección** del mercado ~**61%** de las veces (azar = 50%); es un *focus group sintético* con señal real, no un oráculo.

---

## 0. Resumen ejecutivo

- Tu enjambre **tiene señal direccional genuina**: acierta hacia dónde se movió el mercado en **60.9%** de 645 eventos reales (el azar sería 50%).
- Estima el **tamaño** del golpe flojo: correlación 0.24 (R² ≈ 0.06).
- El objetivo "70% R²" nunca fue realista para esto; la métrica honesta y útil es el **61% de acierto de dirección**.
- Todo esto salió de **datos reales YA existentes**, sin gastar saldo de IA ni depender de NewsAPI.

## 1. Qué se pidió

Ejecutar la "Fase 0: Validación Base" — comprobar si el enjambre reacciona a noticias reales como reaccionó el mercado de verdad.

## 2. Lo que encontré (hallazgos)

### 2.1 No hacía falta NewsAPI: el proyecto ya tenía todo
El plan inicial (recopilar noticias con NewsAPI + movimientos del SPY) tenía tres problemas: necesita una API key, su plan free solo cubre ~1 mes, y correlacionar una noticia suelta con el SPY a 30 min es **señal débil** (los mercados son eficientes; casi todo ya está en el precio).

En cambio, el proyecto **ya incluye** un sistema de backtesting:
- `engine/contenido/backtest_eventos.json`: **100 eventos curados** (2001-2025), con titular, fecha y símbolo líquido. Mezcla ~40% negativos / ~40% positivos / ~20% neutros.
- `engine/contenido/backtest.py`: corre el enjambre sobre cada evento y baja el movimiento **real** del mercado (Yahoo/Alpaca) para compararlo.

### 2.2 El backtest guardaba los pares, pero NO calculaba la métrica
`backtest.py` almacena, por evento, `direccion_pct` (lo que simuló el enjambre) y `reaccion_real.pct_real` (lo que pasó de verdad) — pero **nunca computaba un puntaje agregado** (acierto de dirección, correlación). Ese era el trabajo pendiente de la Fase 0.

### 2.3 Correrlo en vivo exigía saldo de IA… pero no hizo falta
El backtest **se niega a guardar** un examen si los líderes cayeron al respaldo léxico (sin `ANTHROPIC_API_KEY`), para no contaminar la calibración. En esta sesión no hay key, así que no se podía rendir exámenes nuevos.
**Pero** el motor en producción **ya rindió 645 exámenes**, respaldados en GitHub con **lectura pública** (`respaldo.casos_remotos()`, sin token). Así se pudo validar **con datos reales, sin key y sin costo**.

## 3. Lo que hice (la herramienta de Fase 0)

`engine/calibration/validacion_base.py`:
- Trae los 645 casos ya rendidos (respaldo público de GitHub).
- Por cada caso empareja `direccion_pct` (enjambre) vs `reaccion_real.pct_real` (mercado).
- Calcula: **acierto de dirección** (¿coincide el signo?), **correlación de magnitud** (Pearson) y R².
- Desglosa por origen (histórico vs. en vivo). **No** corre simulaciones nuevas → no gasta LLM.

## 4. Resultados (evidencia — 645 exámenes reales)

| Métrica | Resultado | Lectura |
|---|---|---|
| **Acierto de dirección** | **60.9%** | El enjambre acierta el rumbo ~6 de cada 10 veces (azar = 50%) |
| Acierto en movimientos notables (≥0.5%, n=631) | 61.3% | Se mantiene cuando el mercado sí se movió |
| **Correlación de magnitud (Pearson)** | **0.240** | Modesta: acierta la dirección mejor que el tamaño |
| R² (magnitud) | 0.058 | Explica ~6% de la varianza del tamaño del golpe |

**Desglose por origen:**

| Origen | n | Acierto dirección | Correlación |
|---|---|---|---|
| Histórico (backtest curado) | 609 | 60.9% | 0.250 |
| En vivo (destacadas recientes) | 36 | 61.1% | 0.128 |

## 5. Interpretación honesta

- **La dirección es el fuerte del enjambre.** 61% vs. 50% de azar es una señal real y consistente (se sostiene en 645 casos, en histórico y en vivo, y en los movimientos notables). Para un simulador de agentes, capturar el rumbo 6 de 10 veces es un resultado sólido.
- **La magnitud es el flanco débil.** Con R² ≈ 0.06, el enjambre no predice con precisión *cuánto* se moverá el precio. Eso es esperable y coherente con el posicionamiento del producto: un **focus group sintético** que muestra hacia dónde empuja una noticia, **no** un oráculo de precios.
- **Sobre el "70% R²":** era un objetivo mal planteado (R² de magnitud). El número real es ~0.06. Pero la métrica que de verdad importa para esta herramienta —acertar la dirección— está en **61%**, y eso es lo defendible ante un cliente.
- **Marco CMF:** este resultado refuerza el posicionamiento correcto — informar y simular, **nunca** asesorar. "El enjambre acierta la dirección 6 de 10 veces" es una afirmación honesta; "predice el precio" no lo sería.

## 6. Próximos pasos posibles

- Desglosar el acierto por **mercado** (oro / cripto / índice / acción) para ver dónde el enjambre es más fuerte y dónde flojea.
- Medir el acierto por **magnitud del evento** (¿acierta mejor en shocks grandes que en ruido?).
- Si se quiere subir la correlación de magnitud, ese sí sería un objetivo de calibración legítimo (a diferencia del "70% R²"), tuneando parámetros de agentes contra este set — con el cuidado de no sobreajustar.

---

*Herramienta y datos: `engine/calibration/validacion_base.py` (Fase 0), que lee el
respaldo público de exámenes del motor. `main` y el motor en producción: sin cambios.*
