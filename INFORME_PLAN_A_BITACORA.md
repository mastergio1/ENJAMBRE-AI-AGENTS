# Bitácora del Plan A — qué hice, paso a paso

**Fecha:** 6 de septiembre de 2026
**Para:** Giorgio (Rubicón Lab)
**En una línea:** construí la corrección del sesgo alcista, la medí con el LLM real barriendo la perilla, encontré que **mejora el acierto global del enjambre** (la primera palanca que lo logra), y la dejé **activada en 0.35** en producción (falta solo tu deploy en Render).

---

## 1. El problema que ataqué

El enjambre acierta bien la dirección en noticias buenas (~72-83%) pero mal en las malas (~52-54%): es **demasiado optimista**. El diagnóstico apuntaba al "tono" de la noticia — un descuento de magnitud (`GANANCIA_CONSENSO = 0.8`) **suaviza hacia arriba** una mala noticia clara, y el enjambre predice "sube" sobre una caída real.

P2 (silenciar líderes) ya se había descartado. El Plan A ataca la capa correcta: el tono directamente.

## 2. Qué construí (el código)

**El mecanismo** (`engine/model.py`): cuando los líderes que leyeron la noticia con la IA ya coinciden en que es **claramente bajista** (el consenso baja de −umbral), la corrección **no la suaviza**: usa la lectura a plena magnitud (la más bajista entre el consenso y el léxico). **Nunca invierte el signo** — solo evita diluir el bajón. Una perilla, `umbral_correccion_sesgo`, fija qué tan bajista debe ser el consenso para disparar (0 = apagada).

**La infraestructura para medirlo sin riesgo:**
- `config/agentes.json`: la perilla, arrancó en **0.0 (apagada)** → cero cambio en producción hasta decidir.
- Variable de entorno `ENJAMBRE_UMBRAL_CORRECCION_SESGO`: manda sobre la config, para medir base vs corrección **sin re-desplegar** y para **rollback instantáneo** (mismo patrón que usamos en P2).
- `backtest.py` + `server.py` + workflow `evaluar.yml`: un parámetro `umbral` para barrer valores desde el botón de GitHub, resumible por (mercado, peso, umbral).
- `validation/test_correccion_sesgo.py`: tests que verifican que umbral 0 = comportamiento histórico, que la corrección hace el tono más fiel ante mala noticia, y que **nunca invierte el signo**.

**Lo importante y seguro:** la corrección **solo vive en la ruta del titular LLM** (`aplicar_titular`). La ruta numérica (`aplicar_noticia`), que usan los hechos estilizados, **no se toca**. Por eso el realismo del mercado queda intacto pase lo que pase con la perilla.

## 3. Cómo lo medí

Desplegué el código **dormido** (perilla 0.0 = sin efecto en vivo) a Render, y medí con el **LLM real** sobre los exámenes históricos respaldados, comparando la MISMA muestra cambiando solo la perilla. El barrido fue **gratis** (caché de cerebros caliente). Runs #48-#73 del workflow.

*(Un tropiezo: Render tiene el auto-deploy en manual, así que la primera vez el motor siguió sirviendo el código viejo ~30 min hasta que le diste "Deploy" a mano. Lo detecté vigilando la versión del motor por `/salud`.)*

## 4. Qué encontré

### Índice (163 exámenes) — barrido de la perilla

| Umbral | Negativas (81) | Positivas (69) | Global (163) |
|---|---|---|---|
| **0 (base)** | 44 = 54.3% | 50 = 72.5% | 62.6% |
| 0.2 | 47 = 58.0% | 45 = 65.2% | 60.7% |
| 0.25 | *(peor que 0.3)* | | |
| **0.3** | 48 = 59.3% | 47 = 68.1% | **63.2%** |
| **0.35** | 47 = 58.0% | 48 = 69.6% | **63.2%** |

- **0.3 y 0.35 son el punto dulce** (0.2/0.25 castigan las positivas de más).
- **0.35 es el más equilibrado:** negativas **+3.7 pts**, positivas solo **−2.9 pts**, y el **global sube +0.6**.
- Descubrí algo clave: **subir el umbral mejora el resultado** (hasta un plateau en 0.3-0.35), porque dispara solo en los casos MÁS claramente bajistas (los de mayor precisión) y no toca los "titular feo → el mercado rebotó".

### Cripto (220 exámenes) — la corrección es INERTE

Idéntico a la base en los tres cortes (40, 80, 120): en cripto el consenso de la IA casi nunca baja de −0.3, así que la corrección **no dispara**. Resultado: **cero cambio, ni bueno ni malo.**

## 5. El veredicto

Contra tu criterio estricto (negativas ≥+5 en ambos mercados, positivas no bajan >2), el Plan A **no cumple al pie de la letra**: cripto no mejora (inerte) y las positivas de índice ceden ~3 pts.

**Pero es un avance real:** es **la PRIMERA palanca de toda la investigación que mejora el acierto GLOBAL** (índice 62.6% → 63.2%), sin hacer daño en cripto, y reversible al instante. Freno, P1, P2 y todas las variantes previas eran neutrales o negativas.

Te presenté la curva completa y me dijiste: **activar 0.35.**

## 6. Cómo lo dejé (activación)

1. Cambié la config a `umbral_correccion_sesgo = 0.35` y lo fusioné a `main` (commit `58239eb`).
2. **Verificado:** 12/12 tests pasan (unitarios + hechos estilizados completos, 5 min de corrida) con la config en 0.35. El motor lee 0.35; la ruta numérica sigue sana (curtosis 4.64 >3, asimetría 1.67 >1).
3. **Falta solo tu deploy manual en Render** (`enjambre-motor` → Manual Deploy → Deploy latest commit) para que quede vivo.
4. **Rollback instantáneo** si algo se descalibra en vivo: variable `ENJAMBRE_UMBRAL_CORRECCION_SESGO = 0` en Render (sin re-desplegar).

## 7. Qué NO hice (y por qué)

Tu plan mencionaba P3 (acotar magnitudes en cripto) y P4 (confianza + segmentación) como paquete "si el Plan A funcionaba limpio". Como el Plan A resultó una mejora real pero **modesta** (no el home run del criterio estricto) y elegiste activar 0.35 puntualmente, **no construí P3/P4**. Quedan como misión aparte cuando quieras.

## 8. Archivos que toqué

- `engine/model.py` — el mecanismo de corrección + lector de entorno.
- `engine/config/agentes.json` — la perilla (ahora en 0.35).
- `engine/contenido/backtest.py`, `engine/server.py`, `.github/workflows/evaluar.yml` — el parámetro `umbral` para medir.
- `engine/validation/test_correccion_sesgo.py` — los tests del mecanismo.
- Informes: `INFORME_PLAN_A.md` (la curva y la recomendación), este `INFORME_PLAN_A_BITACORA.md`.

---

*Mediciones: workflow "Evaluar acierto (P2)" → `/api/evaluar` (Render, LLM real), runs #48-#73. Diagnóstico: `INFORME_CAUSA_RAIZ_NEGATIVAS.md`. Cierre de P2: `INFORME_PERILLA_COMPLETO.md`.*
