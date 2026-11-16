# Plan combinado de calibración y señal — Propuestas 1 + 2 + 3 (v2, priorizado)

*Rubicón Lab · El Enjambre · v2 2026-11-16. Síntesis de las TRES propuestas,
verificada y en parte MEDIDA contra el código/datos. Re-priorizado por evidencia.*

> **Para Giorgio, en simple.** Las tres encontraron fallos reales. La 3ª encontró
> la palanca que las otras rozaron, y la **medí: es real y casi gratis**. Por eso
> cambia el orden. Lo de arriba es lo que más sube el acierto con menos riesgo.

---

## La verdad que gobierna todo (Propuesta 3, MEDIDA)

**El acierto NO lo mueve la calibración (Platt/isotónica). Lo mueve el signo de
`direccion_pct`, que sale del PRECIO simulado de UNA corrida ruidosa — no de la
señal de los líderes.** Por eso toda la calibración mejora el Brier (honestidad)
pero no el % de aciertos.

Y lo medí sobre los 678 casos — **el signo de la SEÑAL acierta más que el del
precio:**

| Mercado | Precio simulado (hoy) | Señal de líderes | Δ |
|---|--:|--:|--:|
| TODOS (678) | 60.3% | **64.6%** | +4.3 |
| índice (170) | 54.7% | **64.7%** | +10.0 |
| cripto (221) | 67.9% | **70.6%** | +2.7 |
| petróleo (26) | 46.2% | **57.7%** | +11.5 |
| acción (239) | 60.3% | 61.5% | +1.2 |
| oro (22) | 45.5% | 45.5% | = |

→ **Publicar la dirección desde la señal es la intervención #1: medida, gratis,
sin dañar ningún mercado.**

## La otra ley (del artefacto, ya vivida)

La etiqueta "negativa/positiva" y los días del examen **salen del movimiento real
ya ocurrido** (`cosechador.py`, umbrales índice 2.5% / acción·cripto 6.0%). El
examen es **más fácil que el uso en vivo** (el titular ya describe la caída).
Por eso: **ninguna palanca de tono se acepta por subir el "acierto en negativas";
solo si mejora la predicción limpia out-of-sample.** (El falso "+10pts" del doomer
se evaporó así.)

---

## YA HECHO HOY (no repetir)
- **Fase 0 instrumentación:** `calibration/evaluar_por_segmento.py` (reporte por
  mercado×signo×|consenso|, por arquetipo, por fuente) + `docs/baseline-calibracion-fase0.md`.
- **Fuga temporal de `calibrar_libreta` eliminada** (ahora parte por fecha;
  `exportar_libreta` incluye `fecha`).
- **Medido y DESCARTADO** (no ayuda out-of-sample): consenso robusto mediana/
  recortada (P2 H4) y re-pesar por fiabilidad (P2 H5). La señal ponderada 0.3 que
  ya está en producción sigue siendo el mejor estimador.
- Hallazgo: **la confianza auto-reportada del LLM NO correlaciona con el acierto**
  (justifica no confiar en ella cruda).

---

## PRIORIDAD 1 — Dirección desde la señal, no desde el precio *(P3, MEDIDA, gratis)*
1. **Métrica (seguro, offline):** que `backtest.evaluar` mida el acierto sobre el
   signo de `senal_media_ponderada` (y, como control, la mediana de varias
   semillas del precio), no sobre una sola corrida del libro.
2. **Producto (toca el demo):** el reporte publica la **dirección** desde la señal;
   el **precio simulado se queda para el demo y la magnitud**. Decisión respecto al
   evento (reinicia Render).
- *Esperado:* +4.3 global, +10 índice, +11.5 petróleo (medido). Sin tocar pesos ni
  prompts. Es la mejor relación mejora/riesgo.

## PRIORIDAD 2 — Arreglar el examen *(P3 #1 + #5 + #promover)*
*(Sin esto, los números absolutos engañan.)*
1. **Contrato de acierto único:** misma zona muerta (0.3%, la de `corrector.libreta`)
   en `evaluar`, libreta y muro; "lateral" no es error → se reporta **cobertura**
   aparte (hoy: evaluar sin zona muerta, libreta 0.3%, muro otro umbral).
2. **Arreglar la etiqueta del cosechador:** la ventana de `pct_real` debe empezar
   en el cierre **posterior** al timestamp del titular; añadir días **no elegidos**
   por "ya se movió fuerte". Si no, se optimiza un examen más fácil que el vivo.
3. **Holdout honesto:** walk-forward siempre; un holdout que **no participe** en
   elegir el mejor de los 6 calibradores (hoy `promover` elige sobre el mismo OOS).

## PRIORIDAD 3 — Correctitud y trazabilidad *(P1 + P3)*
1. **Confianza bien definida:** `_ultimo_consenso` se guarda **antes** de
   `GANANCIA_CONSENSO`/Plan A/perfil; la "confianza" del reporte = lectura cruda,
   no el tono aplicado. Persistir `_tono_final`/`_confianza_final`/`_fuente_tono`
   y rastro por predicción (crudo → ajustes → final → fuente → motivo lateral).
2. **Dos salidas explícitas:** `prob_calibrada` (predicción) vs `tono/confianza_final`
   (enjambre). Hoy están entrelazadas en el nombre.

## PRIORIDAD 4 — Palancas de tono *(P2, SOSPECHOSAS — base limpia OBLIGATORIA)*
*(Bajan de prioridad: si la dirección ya sale de la señal (Prioridad 1), el tono
del precio pesa menos para el acierto y más para el demo/magnitud. Además pueden
engañar a la métrica circular.)*
1. **Separar magnitud y dirección** (P3 #4): la perilla de tamaño
   (`GANANCIA_CONSENSO`, topes P3, volatilidad) **no** vuelve a entrar en la
   función que decide el signo.
2. **`GANANCIA_CONSENSO` por signo/mercado** y **`peso_tono_invertidores` por
   mercado** (P2 H1/H2) — solo si mejoran la predicción limpia.
3. **Plan A suave** (mezcla continua en vez de corte duro) + **léxico como feature**
   (α·consenso + (1−α)·directo) (P2 H3).
4. **`MINIMO_IA_CONSENSO` gradual** vs el corte seco 0.5 (P1/P2).
5. **Gating por ambigüedad** (P2 H7): si |señal/tono| < θ → lateral; publicar
   cobertura aparte.

## PRIORIDAD 5 — Subir el techo *(P2, más caro, al final)*
1. **Hash del prompt en la clave de caché** (P2 3.1.bis) — infra; desbloquea iterar prompts.
2. **Few-shot en los prompts de los arquetipos fieles** (P2 H6/3.1) con casos
   negativos reales (el `doomer_selectivo` ya validó que el prompt es palanca).
3. **Relevancia arquetipo × mercado** (P2 3.2): bajar el peso de las voces inertes
   en el mercado donde aciertan ~50%.
4. **Meta-modelo ligero de dirección** (P2 H8): logística `[consenso, directo,
   std, confianza_media, n_disonantes, one_hot(mercado), …] → P(up)`. *NO existe
   hoy (corrección a P2: `real_optimizer` optimiza hechos estilizados, no dirección).*
5. **Self-consistency** opt-in (3 muestras por arquetipo fiel) — rompe el
   presupuesto ×3; último.

---

## Descartado por medición (no se implementa)
- **Consenso robusto** (mediana/recortada, P2 H4): empeora el Brier OOS.
- **Re-pesar por fiabilidad histórica** (P2 H5): empata, no supera a la señal
  ponderada actual.

## Lo que NO hacer *(de las tres + lo medido)*
- No añadir más arquetipos "correctores" incondicionales.
- No subir `GANANCIA_CONSENSO` global a 1.0 (sobre-reacciona en magnitud).
- No tocar los prompts de los invertidores (su trabajo es invertir).
- No usar `simular.py` como métrica de dirección (mide hechos estilizados).
- No tocar pesos de arquetipos ni prompts **hasta** medir la Prioridad 1 (P3).
- No aceptar ninguna mejora de "negativas" sin base limpia out-of-sample.

## Reglas transversales
- Flag `ENJAMBRE_*` para todo lo nuevo, default = hoy; rollback sin redeploy.
- Una palanca por PR; walk-forward siempre; dataset congelado.
- Métrica compuesta para mirar (hit_neg/hit_pos/por mercado + cobertura); **el juez
  que decide es el acierto/Brier limpio out-of-sample.**
- CMF intacto (educativo, no asesoría).

## Orden, riesgo y expectativa
| # | Qué | Riesgo | Expectativa |
|---|---|---|---|
| 1 | Dirección desde la señal | Bajo (métrica) / Medio (producto) | **+4.3 global, +10 índice (medido)** |
| 2 | Arreglar el examen (zona muerta, cosechador, holdout) | Bajo | Números creíbles; sin esto todo engaña |
| 3 | Confianza bien definida + trazabilidad | Bajo | Correctitud |
| 4 | Palancas de tono (con base limpia) | Medio | Incierto; puede ser espejismo |
| 5 | Techo (prompts, meta-modelo, …) | Medio-alto | Sube el techo; lo más caro |

**Momento:** La Prioridad 1 (métrica) y la 2 son casi todo offline y se pueden
hacer ya. El cambio de la dirección PUBLICADA y las palancas de tono tocan el demo
(reinician Render) → recomendación: **después del evento del 21**. El techo
estructural sigue: para cripto/acción la dirección muchas veces no está en el texto.

---
*Fin del plan v2. Cada fase se mide y se decide con evidencia.*
