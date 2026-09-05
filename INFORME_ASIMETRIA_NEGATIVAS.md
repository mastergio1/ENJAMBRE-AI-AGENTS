# Informe: el intento de "subir el acierto en noticias negativas (38% → 60%)"

**Rama:** `feature/calibracion-70-porciento` (aislada)
**Fecha:** 5 de septiembre de 2026
**Veredicto de una línea:** el script propuesto **no se puede ejecutar** (se rompe de entrada) y, aunque se arreglara, sería un **no-op** que reportaría un número falso; además la estrategia de fondo es **sobreajuste**, no calibración. Me detuve a propósito antes de gastar saldo o ensuciar el motor.

---

## 1. El objetivo (legítimo) y de dónde viene

El desglose de la Fase 0 encontró que el enjambre acierta la dirección:
- **Positivas: 79.6%** 🟢
- **Negativas: 38.3%** 🔴 (peor que el azar)

La idea del bundle: añadir un `factor_panico_negativo` y calibrarlo con Optuna para subir el 38% al 60%. El **objetivo** (que el enjambre no exagere tanto el pánico) es válido. El **método** propuesto, no.

## 2. Por qué el script NO funciona (bugs verificados)

Revisé cada supuesto contra el código real. Evidencia:

| # | Problema | Evidencia |
|---|---|---|
| 1 | `from ...validacion_base import obtener_casos, calcular_metricas` → **ImportError** | Esas funciones no existen; la herramienta tiene `validar`, `_cargar_pares`, `_puntuar`. |
| 2 | `factor_panico_negativo` es un **parámetro fantasma** | `grep` en todo `engine/` → **0 resultados**. Ningún agente lo lee. |
| 3 | Escribe en `config["miedosos"]["parametros"]`, una clave que el motor **ignora** | El JSON es `{descripcion, total_agentes, ruido_parametros_sigma, tipos:[...]}`. No hay clave `miedosos`. |
| 4 | `from engine.model import …` **falla** | `model.py` hace `from agents.base import…` (asume `engine/` en el path, no la raíz). |

Consecuencia: aunque parchara el import, el "factor" se escribiría en un lugar que nadie lee → **el enjambre no cambiaría** y Optuna reportaría diferencias que en realidad son solo **ruido aleatorio** entre corridas. Un fitness inventado. Es exactamente el mismo error que ya cazamos dos veces en esta rama (el JSON decorativo).

> Nota sobre el `obtener_casos()` que el mensaje sugería añadir: descargaba
> `backtest_eventos.json` (los 100 titulares SIN el movimiento real ni la
> categoría medida), no los 645 casos con `pct_real`. No sirve para medir
> acierto. Y usaba `requests`, que no está instalado (el proyecto usa `httpx`).

## 3. El problema de fondo (más importante que los bugs)

Aunque arreglara los 4 bugs, la estrategia **no es honesta**, por dos razones:

### 3.1 No simula el producto real
El bundle re-simula con un **sentimiento aleatorio** por categoría (`random.uniform(-0.8,-0.3)` para negativas), **no** con los líderes LLM leyendo el titular real. Es un modelo distinto y más pobre; calibrarlo no calibra tu producto.

### 3.2 El 38% es, en buena parte, IRREDUCIBLE
El dato incómodo: **el mercado real sube seguido tras una mala noticia** — porque ya estaba en el precio, o rebota (sobreventa). Eso no es un defecto del enjambre; es cómo funciona el mercado.

Para "subir" el acierto en negativas, el optimizador tendría que hacer que el enjambre **prediga SUBIDA ante titulares negativos** — o sea, volverlo **contrarian**. Eso:
- es absurdo como comportamiento (un enjambre que se pone feliz con malas noticias),
- rompería la **asimetría de pánico** que hace pasar los hechos estilizados (`CLAUDE.md` §7),
- y muy probablemente **bajaría el 80% de las positivas**.

Sería **sobreajustar** a 645 casos particulares, no hacer el enjambre más realista.

### 3.3 Medirlo de verdad cuesta dinero
El backtest real (líderes LLM leyendo titulares) cuesta ~$0.12 por evento. 20 trials × 100 eventos = **2.000 simulaciones ≈ ~$240** de saldo Anthropic por una sola corrida de calibración que persigue un objetivo sobreajustado.

## 4. Mi punto de vista (honesto)

**El 38% no es un bug que una perilla arregle; es un diagnóstico correcto con dos causas mezcladas:**

1. **El enjambre exagera el pánico** — esto SÍ es real y ya lo detectamos. Es el efecto secundario de su mayor virtud (la asimetría que le da colas gordas y crashes creíbles).
2. **Las malas noticias muchas veces no tumban al mercado** — esto es irreducible; ningún parámetro lo arregla sin convertir el enjambre en un contrarian irreal.

Perseguir "38% → 60%" con un knob que fabrique subidas ante malas noticias sería **maquillar el número a costa del realismo**. Es justo lo contrario de lo que veníamos haciendo bien: honestidad sobre humo.

**Lo que yo recomiendo, en orden:**

1. **Quedarnos con el hallazgo como diagnóstico** (ya documentado): "el enjambre entiende la euforia, exagera el pánico". Es una verdad útil y vendible con matices, no algo que esconder.
2. **Si quieres experimentar el trade-off de verdad** (gratis y aquí mismo): bajo `asimetria_kahneman` del miedoso en la rama y **re-corro los hechos estilizados** (`engine/validation/`, sin LLM). Te muestro con números cuánto se degrada la curtosis/asimetría al suavizar el pánico. Así ves el precio real de "mejorar" las negativas.
3. **Solo si ese trade-off se ve aceptable**, recién ahí valdría gastar un backtest real chico para confirmar el efecto en negativas — con los ojos abiertos, no a ciegas.

Lo que **no** recomiendo: correr el script tal cual (se cae), ni una versión "parchada" que tunee un parámetro fantasma (mentiría), ni sobreajustar el enjambre para que acierte malas noticias volviéndolo contrarian.

## 5. Para el cliente / marco CMF

La afirmación honesta sigue siendo fuerte: *"el enjambre acierta la dirección ~6 de cada 10 veces, y hasta 8 de 10 con noticias positivas"*. Añadir *"con noticias negativas es más cauto porque tiende a anticipar el pánico"* es honesto y hasta suena sofisticado. Fabricar un 60% falso sería el camino contrario — y en un producto bajo CMF, el peor.

---

*No se ejecutó el script propuesto (se rompe en imports y tunearía un parámetro
fantasma). No se gastó saldo de IA. `main` y el motor en producción: sin cambios.*
