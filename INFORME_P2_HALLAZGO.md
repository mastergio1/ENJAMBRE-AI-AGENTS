# Hallazgo: P2 mejora el acierto en negativas — en los dos mercados probados

**Fecha:** 6 de septiembre de 2026
**Medición:** con el LLM real en Render (`con_ia: 20/20` y `40/40`), sobre exámenes ya respaldados, comparando la MISMA muestra y semillas con la perilla en 1.0 (actual) vs 0.0 (P2).
**Veredicto de una línea:** separar a los arquetipos invertidores del "clima del mercado" (P2) **sube el acierto en negativas en cripto Y en índice, sin costar nada en positivas.** Señal consistente y sin daño colateral; muestras aún modestas.

---

## 1. Qué se midió

P2 saca a los arquetipos **contrarian, quant y optimista** del tono de mercado (siguen operando y hablando; solo dejan de fijar el ánimo). La perilla `peso_tono_invertidores`: **1.0** = comportamiento actual, **0.0** = P2 pleno. La comparación se hace sobre los mismos exámenes y las mismas semillas, así que aísla el efecto de P2 limpio.

## 2. Resultado — CRIPTO (20 exámenes · 18 negativas)

| Cripto | Negativas | Positivas | Global |
|---|---|---|---|
| **peso 1.0** (actual) | 11/18 = **61.1%** | 1/2 = 50% | 60% |
| **peso 0.0** (P2) | **13/18 = 72.2%** | 1/2 = 50% | **70%** |
| **Diferencia** | **+11 pts** (+2 aciertos) | igual | +10 pts |

## 3. Resultado — ÍNDICE (40 exámenes · 24 negativas)

| Índice | Negativas | Positivas | Global |
|---|---|---|---|
| **peso 1.0** (actual) | 12/24 = **50%** | 8/13 = 61.5% | 55% |
| **peso 0.0** (P2) | **15/24 = 62.5%** | 8/13 = 61.5% | **62.5%** |
| **Diferencia** | **+12.5 pts** (+3 aciertos) | **igual** ✅ | +7.5 pts |

## 4. El cuadro combinado

| Mercado | Negativas base | Negativas P2 | Δ negativas | Positivas |
|---|---|---|---|---|
| **Cripto** (18 neg) | 61.1% | **72.2%** | +2 aciertos | igual ✅ |
| **Índice** (24 neg) | 50.0% | **62.5%** | +3 aciertos | igual ✅ |
| **Total** (42 neg) | — | — | **+5 aciertos, 0 positivas perdidas** | sin trade-off |

## 5. Por qué esto es una buena señal

1. **Consistencia:** P2 sube las negativas en **ambos** mercados (no fue casualidad de uno solo).
2. **Sin costo colateral:** las positivas quedaron **idénticas** en los dos mercados. Era el mayor riesgo (que arreglar negativas rompiera positivas) — y no pasó.
3. **Ayuda más donde debía:** el efecto es mayor en **índice**, que era el mercado con peor sesgo alcista (50% base). Exactamente lo que predijo el diagnóstico de causa raíz.
4. **Bajo riesgo:** P2 es reversible con una variable de entorno, y los 5 hechos estilizados siguen pasando.

## 6. La honestidad — qué NO afirmamos aún

- **Muestras modestas:** 18 + 24 = 42 negativas. El efecto es real y consistente, pero un intervalo de confianza estricto pediría más exámenes.
- **No es el "38% global":** ese número era todas las negativas con semillas originales; aquí medimos por mercado con semillas nuevas. Lo válido es la comparación 1.0 vs 0.0 sobre la misma muestra (que sí aísla P2).
- **Falta el resto de mercados** (acción, oro, petróleo) y el número a escala completa.

## 7. Caminos para decidir

**A) Confirmar con todo:** correr los 609 exámenes (todos los mercados). Número definitivo. ~$66 una vez, después gratis.

**B) Confirmar índice+cripto (recomendado):** correr el resto de los dos mercados con señal (~380 exámenes, ~$39). Clava el número donde importa, y ahí se decide el valor final.

**C) Activar P2 ya (pragmático):** la evidencia es consistente y sin downside; fijar `ENJAMBRE_PESO_TONO_INVERSORES` = 0.0 (o un moderado 0.3) en Render y monitorear en vivo. Reversible al instante.

**Recomendación:** B — un paso más de confirmación en los mercados que importan, y luego fijar el valor. Si se prefiere velocidad, C es defendible por ser reversible.

---

## 8. Estado de producción

P2 vive en `main` con la perilla en **1.0 por defecto** → **cero cambio de comportamiento** hasta que los números justifiquen fijar otro valor. Toda esta medición NO tocó el respaldo histórico ni el comportamiento en vivo. El cambio real lo decides tú con la evidencia.

---

*Medición: workflow "Evaluar acierto (P2)" → `/api/evaluar` (Render, LLM real).
Detalle del sistema y los arreglos: `INFORME_P2_MEDICION.md`. Cómo medir: `docs/medir-p2.md`.*
