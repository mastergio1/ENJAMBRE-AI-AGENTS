# P1 — Respaldo léxico ampliado + monitor + rollback: informe completo

**Fecha:** 6 de septiembre de 2026
**Estado:** ✅ **mergeado a producción** (`main` → commit `dcf4e17`). Deploy en Render en curso al momento de escribir; verificación de `/salud` abajo.
**Rama:** `p1-lexico-ampliado` (mergeada con `--no-ff`).
**Suite:** 256 passed, 2 skipped, 0 fallas.

---

## 0. Qué es P1, en una frase

El **respaldo léxico** es el "plan B" del enjambre: cuando la API de los cerebros LLM se cae o se queda sin saldo, un diccionario simple lee el titular para que la simulación no quede ciega. Ese plan B estaba **flojo y con un bug**. P1 lo amplía, lo arregla, y le pone **monitorización** y **freno de emergencia**.

## 1. Qué hice mejor que el plan original

El plan que me pasaste tenía dos vicios; los corregí:

1. **Medía un diccionario de juguete**, no el real (`["sube","cae",…]` a mano). Mi test mide la **función real** del motor sobre los 645 casos.
2. **Solo miraba negativas.** Agregar jerga bajista a ciegas puede **dañar las positivas**. Yo mido negativas, positivas Y falsos positivos.

Y añadí lo que el plan no pedía: **arreglar el bug de substring** (un problema real y silencioso).

## 2. Los dos bugs que encontré y arreglé

Al medir la línea base salió un **39.7% de falsos positivos** (noticias buenas leídas como malas). Culpables:

- **Substring:** `"war"` matcheaba *"So**ftware**"*, *"**War**ner Bros"*, *"**War**ns"*. → **Arreglado** con matcheo por **límite de palabra** (`\bwar\b`).
- **Ambigüedad:** `"tariff"` marcaba bajista *"US-China **Slash Tariffs**"* — ¡pero recortar aranceles subió el mercado $700B! → **Arreglado** con **frases** ("slash tariffs" = alcista) evaluadas primero.

## 3. Qué cambié en el diccionario

- **Matcheo por límite de palabra** (regex `\b…\b`) en vez de substring.
- **Frases nuevas**: aranceles (slash/cut tariffs), guías (profit warning, cuts/raises guidance), mercado (bear/bull market, record low/high, beats/misses estimates).
- **Jerga bajista** con formas verbales: tumbles, plunge, slump, slide, sell-off, freeze, warn/warning, downgrade, plummet, tank, rout, bloodbath, bearish, nosedive, crater, diving, freefall…
- **Jerga alcista**: surge, soar, rally, jump, climb, rebound, recovery, upbeat, bullish, boom, gains, tops, highs, rises…

## 4. Resultados (medidos con la función real, 645 casos)

| Métrica | Antes | Después | |
|---|---|---|---|
| **Mudo** (sin señal) | 74.5% | **60.5%** | ✅ +cobertura |
| Acierto **positivas** (opina) | 54.4% | **62.8%** | ✅ |
| **Falsos positivos** | 39.7% | **31.9%** | ✅ |
| Negativas bien clasificadas (absoluto) | 69 | **88** | ✅ +19 |
| Acierto **negativas** (tasa, opina) | 83.1% | 72.7% | ⚠️ espejismo* |

*La tasa de negativas "baja" porque, al cubrir más, aflora lo **irreducible**: titulares alcistas ("Bitcoin sobre $52K") que precedieron caídas. En **absoluto acierta más** negativas (88 vs 69). Probé una variante solo-bajista (negativas 86%) pero hundía positivas a 45% y falsos positivos a 49% — peor balance. Elegí la **completa** por mejor balance global.

## 5. Condición 1 (tuya) — Monitor de polaridad en vivo ✅

`monitorear_polaridad()` en `aplicar_titular`: cada simulación real registra en el log `enjambre.lexico` la distribución **alcista/bajista/neutral y media** del **respaldo** vs la **API**, **solo cuando el respaldo se activó** (API caída). Si el nuevo léxico sesgara distinto que la API, se ve en los logs al instante.

```
polaridad respaldo={'n':40,'alcista':8,'bajista':25,'neutral':7,'media':-0.31}
              api={'n':60,'alcista':12,'bajista':38,'neutral':10,'media':-0.29}
```
Si la `media` del respaldo se despega de la de la API → hay sesgo, a revisar. Es **pasivo** (no cambia decisiones) y **a prueba de fallos** (nunca tumba una simulación).

## 6. Condición 2 (tuya) — Flag de rollback por umbral ✅

Variable de entorno **`ENJAMBRE_LEXICO_UMBRAL`**, leída *por llamada*:
- `0.0` (defecto) → comportamiento normal.
- Subirla (ej. `0.5`) → el léxico **prefiere "mudo"** y solo opina cuando está muy seguro (menos riesgo de falso positivo).
- `1.1` → respaldo léxico **apagado** por completo.

En Render se cambia la variable y toma efecto al reiniciar: **rollback en segundos, sin re-desplegar ni tocar código.** Cubierto con test.

## 7. Lo honesto sobre el alcance (sin humo)

- **No bajé el mudo a <50%** (quedó en 60.5%). Empujar más obliga a palabras genéricas que reintroducen falsos positivos. 60.5% es el punto honesto.
- **Esto NO cambia el 38% en negativas.** Ese número sale de la ruta **LLM** (`cerebros:'ia'`), no del respaldo. P1 mejora la **robustez cuando la API se cae** — hoy, sin saldo, el enjambre leía *"Bitcoin tumbles… freezes withdrawals"* como **neutral**; ahora lo lee bajista.
- **Riesgo:** bajo. El respaldo solo actúa con la API caída. 256 tests pasan; monitor pasivo; rollback en segundos.

## 8. Verificación de despliegue

- Merge a `main`: commit `dcf4e17` (con `9ed986f`… la historia previa preservada como ancestro).
- Render despliega desde `main`; verificar en `https://enjambre-motor.onrender.com/salud` que `version` empiece por `dcf4e17`.
  - *Al momento de escribir, Render aún servía un commit anterior (deploy en construcción). Reverificar hasta que `/salud` muestre `dcf4e17`.*

## 9. Qué sigue

- **P3** (acotar magnitudes absurdas de cripto, +54%/+71%) — medible aquí, mecánico.
- **P2** (separar "clima del mercado" de "apuesta del líder") — la palanca real del 38%, se mide en **CI con LLM**.
- **P4** (reencuadre / segmentar / confianza) — decisión de producto.

---

*Archivos: `engine/brains/fallback.py` (diccionario + matcheo + flag), `engine/model.py` (monitor), `engine/validation/test_lexico_cobertura.py` (medición + tests). Rama `p1-lexico-ampliado` → `main` `dcf4e17`.*
