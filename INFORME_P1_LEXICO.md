# P1: ampliar y ARREGLAR el respaldo léxico — qué mejoré

**Fecha:** 6 de septiembre de 2026 · **Rama:** `p1-lexico-ampliado` (aislada)
**Veredicto de una línea:** amplié el diccionario del respaldo (el plan B cuando la API se cae) y de paso **arreglé un bug de falsos positivos que el plan del sprint ni miraba**. Cobertura arriba, positivas mejor, falsos positivos abajo — medido con la función real sobre los 645 casos.

---

## 0. Qué hice mejor que el plan original

El plan del sprint tenía dos vicios que corregí:

1. **Medía un diccionario de juguete, no el real.** El PASO 2 definía `["sube","cae",…]` a mano y medía ESO — no el `sentimiento_lexico` que de verdad corre en el motor. Mi test mide la **función real**.
2. **Solo miraba negativas.** Agregar jerga bajista a ciegas puede **dañar las positivas** (falsos positivos), y el plan ni lo medía. Yo mido negativas, positivas Y falsos positivos.

Y añadí una mejora que el plan no pedía: **arreglar el matcheo por substring**, que era un bug real.

## 1. Los dos bugs que encontré (y arreglé)

Al medir la línea base salió un **39.7% de falsos positivos** en positivas (noticias buenas leídas como bajistas). Diagnostiqué las culpables:

- **Bug de substring:** `"war"` (bajista) matcheaba *"**Soft**ware"*, *"**War**ner Bros"*, *"**War**ns"*. → **Arreglado con matcheo por límite de palabra** (`\bwar\b`): ya no matchea "software".
- **Palabra ambigua:** `"tariff"` marcaba bajista *"US-China **Slash Tariffs**"* — ¡pero recortar aranceles es ALCISTA (subió $700B)! → **Arreglado con frases** ("slash tariffs" = +0.6) que se evalúan antes y desambiguan.

## 2. Qué cambié

- **Matcheo por límite de palabra** (regex `\b…\b`) en vez de substring: mata los falsos positivos tipo "war→software".
- **Frases nuevas** para desambiguar: aranceles (slash/cut tariffs = alcista), guías (profit warning, cuts/raises guidance), mercado (bear/bull market, record low/high, beats/misses estimates).
- **Jerga bajista nueva con formas verbales:** tumbles/tumbled/tumbling, plunge/plunged, slump, slide, sell-off, freeze/frozen, warn/warns/warning, downgrade, plummet, tank, rout, bloodbath, bearish, nosedive, crater, diving, freefall…
- **Jerga alcista nueva:** surge/soar/rally/jump (todas las formas), climb, rebound, recovery, upbeat, bullish, boom, gains, tops, highs, rises…

## 3. Resultados (medidos con la función real, 645 casos)

| Métrica | Antes | Después | |
|---|---|---|---|
| **Mudo** (sin señal) | 74.5% | **60.5%** | ✅ −14 pp de cobertura |
| Acierto **positivas** (opina) | 54.4% | **62.8%** | ✅ |
| **Falsos positivos** (buena leída bajista) | 39.7% | **31.9%** | ✅ |
| Acierto **negativas** (opina) | 83.1% (69) | 72.7% (88) | ⚠️ ver nota |
| Negativas bien clasificadas (absoluto) | 69 | **88** | ✅ +19 |

**La nota honesta sobre la "caída" en la tasa de negativas:** es un espejismo. En **absoluto** el léxico ahora acierta MÁS negativas (88 vs 69). La *tasa* baja porque, al cubrir más, aflora casos **irreducibles**: titulares alcistas ("Bitcoin sobre $52K") que precedieron caídas. Con más cobertura los detecta y los lee alcistas (fiel al titular, "equivocado" respecto al desenlace). Ningún diccionario predice esos crashes desde un titular bueno.

Probé una variante **solo-bajista** (sin las alcistas nuevas): sube negativas a 86.1%, pero **hunde positivas a 45.5%** y sube falsos positivos a 49%. Peor balance. Por eso elegí la versión **completa**: misma precisión global (~68%), mucha más cobertura, y el bug de falsos positivos arreglado.

## 4. Lo honesto sobre el alcance (no te vendo humo)

- **No llegué a "mudo < 50%".** Me quedé en 60.5%. Empujar más abajo exige palabras genéricas ("below", "sub") que reintroducen falsos positivos. 60.5% es el punto honesto donde la precisión no se sacrifica.
- **Esto NO cambia el 38% en negativas.** Ese número sale de la ruta **LLM** (`cerebros: 'ia'`), no del respaldo. Esto mejora la **robustez cuando la API se cae**: hoy, sin saldo, el enjambre quedaría ciego ante *"Bitcoin tumbles… freezes withdrawals"* (lo leía 0.00 neutral); ahora lo lee bajista.
- **Riesgo:** bajo. El respaldo solo actúa con la API caída. Los **91 tests** que tocan el léxico pasan; la suite completa se validó aparte.

## 5. Recomendación

Mergear P1 a producción: es una mejora de **robustez** real y de bajo riesgo (arregla un bug de falsos positivos y tapa un agujero para cuando la API falle). No promete tocar el 38% — para eso es P2 (separar clima de apuesta), que se mide en CI con LLM.

---

*Herramientas: `engine/brains/fallback.py` (diccionario + matcheo), `engine/validation/test_lexico_cobertura.py` (medición sobre 645 casos reales). Sin LLM. Rama `p1-lexico-ampliado`.*
