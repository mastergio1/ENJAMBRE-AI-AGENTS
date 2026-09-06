# Plan A — corrección del sesgo alcista: resultados y recomendación

**Fecha:** 6 de septiembre de 2026
**Para:** Giorgio (Rubicón Lab)
**En una línea:** El Plan A es **la primera palanca que mejora el acierto GLOBAL** del enjambre (índice +0.6 pts) sin hacer daño en cripto. No cumple al pie de la letra tu criterio estricto, pero es una ganancia real y reversible. La decisión de activarlo es tuya.

---

## 1. Qué hace el Plan A (en simple)

El enjambre acierta ~72-83% en noticias buenas pero solo ~52-54% en malas: es **demasiado optimista**. La causa: el "tono" de la noticia se **suaviza hacia arriba** (un descuento de magnitud, `GANANCIA_CONSENSO`, encoge una mala noticia clara).

La corrección: **cuando los líderes que leyeron la noticia con la IA ya coinciden en que es claramente bajista** (consenso por debajo de −umbral), **no la suavizamos** — usamos la lectura a plena magnitud (la más bajista entre el consenso y el léxico). Nunca invierte el signo: solo evita diluir el bajón. Una perilla, `umbral_correccion_sesgo`, fija qué tan bajista debe ser el consenso para disparar (0 = apagada).

*(A diferencia de P2, que silenciaba líderes y no servía, esto corrige el tono directamente — la capa correcta según el diagnóstico de causa raíz.)*

## 2. Barrido completo en ÍNDICE (163 exámenes)

| Umbral | Negativas (81) | Positivas (69) | Global (163) |
|---|---|---|---|
| **0 (base)** | 44 = 54.3% | 50 = **72.5%** | 102 = 62.6% |
| 0.2 | 47 = 58.0% | 45 = 65.2% | 99 = 60.7% |
| 0.25 | *(peor que 0.3 — parcial: a 80 casos ya cede una positiva de más)* | | |
| **0.3** | **48 = 59.3%** | 47 = 68.1% | **103 = 63.2%** |
| **0.35** | 47 = 58.0% | 48 = **69.6%** | **103 = 63.2%** |

**Lo que aprendimos de la curva:**
- **Subir el umbral MEJORA el resultado** (hasta un plateau en 0.3-0.35). Contra-intuitivo pero lógico: un umbral alto dispara solo en los casos MÁS claramente bajistas (los de mayor precisión), sin tocar los casos de "titular feo → el mercado rebotó" donde el optimismo del enjambre acertaba.
- **0.2 y 0.25 son malos** (castigan positivas de más). **0.3 y 0.35 son el punto dulce** (ambos +0.6 pts de global).
- **0.3 vs 0.35:** 0.3 gana más en negativas (+4.9 pts) pero cede más en positivas (−4.3). 0.35 es el más equilibrado: negativas +3.7 pts y positivas solo −2.9.

## 3. CRIPTO (220 exámenes) — la corrección es INERTE

| Cripto (checkpoints) | Negativas | Positivas |
|---|---|---|
| base vs 0.3 @ 40 | 18/27 = idéntico | 10/13 = idéntico |
| base vs 0.3 @ 80 | 24/40 = idéntico | 33/40 = idéntico |
| base vs 0.3 @ 120 | 29/53 = idéntico | 55/67 = idéntico |

**En cripto la corrección NO dispara** (el consenso de la IA en cripto casi nunca baja de −0.3). Resultado: **cero cambio, ni bueno ni malo.** Cripto se queda como está (neg 51.7%, pos 83.2%, global 70.5%).

## 4. Contra tu criterio de éxito

Tu criterio: negativas ≥ +5 pts **en ambos mercados**, positivas no bajan > 2 pts, hechos estilizados pasan.

| Criterio | 0.3 | 0.35 |
|---|---|---|
| Negativas ≥ +5 pts (índice) | +4.9 ⚠️ casi | +3.7 ❌ |
| Negativas ≥ +5 pts (cripto) | 0 (inerte) ❌ | 0 (inerte) ❌ |
| Positivas no bajan > 2 (índice) | −4.3 ❌ | −2.9 ⚠️ casi |
| Positivas no bajan > 2 (cripto) | 0 ✅ | 0 ✅ |
| Hechos estilizados pasan | ✅ | ✅ |
| **Global (índice)** | **+0.6 ✅** | **+0.6 ✅** |

Al pie de la letra, **no cumple** (cripto no mejora en negativas; las positivas de índice bajan algo más de lo permitido). Pero:

## 5. Por qué esto igual es un avance real

1. **Es la PRIMERA palanca que mejora el acierto GLOBAL.** Freno, P1, P2 y todas las variantes previas eran neutrales o negativas. Esta suma (índice 62.6% → 63.2%).
2. **No hace daño donde no debe.** En cripto es inerte; en índice el global sube pese al ajuste de positivas.
3. **Ataca la capa correcta.** Confirma que el problema es el sesgo del tono, no los agentes. La corrección hace justo lo que el diagnóstico pedía.
4. **Reversible al instante.** Es una variable de entorno; si en vivo algo se descalibra, se apaga sin re-desplegar.
5. **Los hechos estilizados no se tocan** (la corrección solo vive en la ruta del titular LLM; el realismo del mercado queda intacto).

## 6. Los "peros" honestos

- **La ganancia es modesta:** +1 acierto neto sobre 163 en índice. Real, pero pequeño; dentro de un intervalo de confianza estricto es apenas distinguible de cero.
- **Cripto no se beneficia:** el mercado con peor sesgo alcista (pos 83% / neg 52%) queda igual, porque su consenso no llega a ser lo bastante bajista para disparar. Un umbral más bajo lo tocaría, pero ya vimos que umbral bajo (0.2) castiga las positivas de índice.
- **Las positivas de índice ceden** ~3-4 aciertos: son casos de sobre-reacción (titular malo, mercado arriba) que ningún tono más pesimista puede distinguir de una caída real.

## 7. Estado de producción

- Plan A está en `main` y desplegado en Render, **con la perilla en 0.0 (DESACTIVADA)** → cero cambio de comportamiento en vivo hoy.
- Activar = fijar `ENJAMBRE_UMBRAL_CORRECCION_SESGO` (0.3 o 0.35) en Render, o `umbral_correccion_sesgo` en la config. Reversible poniéndolo en 0.
- 8/8 tests unitarios verdes; hechos estilizados pasan con la corrección activa.

## 8. Mi recomendación (honesta)

**Activaría 0.35 en producción, con monitoreo.** Razones:
- Es el más equilibrado: mejora negativas ~4 pts, apenas roza las positivas (−2.9, casi dentro de tu límite), y **el global sube**.
- Cero riesgo en cripto (inerte).
- Reversible al instante.
- Es un avance real, y "esperar la palanca perfecta que quizás no existe" tiene su propio costo.

**Pero es defendible NO activarlo** y pasar a la Fase 2 (Plan B) si prefieres ceñirte al criterio estricto: la ganancia global es de 1 acierto sobre 163 (dentro del ruido), y cripto no mejora. En ese caso el código queda dormido en producción por si un rediseño futuro lo aprovecha.

**La decisión es tuya:** activar 0.35 (o 0.3), o guardar el Plan A y pasar a Fase 2.

---

*Mediciones: workflow "Evaluar acierto (P2)" → `/api/evaluar` (Render, LLM real), runs #48-#73, barrido de umbral sobre caché caliente. Diagnóstico: `INFORME_CAUSA_RAIZ_NEGATIVAS.md`. Cierre de P2: `INFORME_PERILLA_COMPLETO.md`.*
