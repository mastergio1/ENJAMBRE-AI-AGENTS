# Plan combinado de calibración y señal — Propuestas 1 + 2

*Rubicón Lab · El Enjambre · armado 2026-11-16. Síntesis de las dos propuestas
nuevas, verificadas contra el código. No descarta nada valioso de ninguna.*

> **Para Giorgio, en simple.** Las dos propuestas encontraron fallos reales. Este
> plan junta TODO lo valioso de ambas, en orden de "lo seguro y barato primero,
> lo grande e incierto al final". Es trabajo de MODELO (no se ve en el demo), así
> que la mayor parte es para DESPUÉS del evento del 21.

---

## La regla de oro que manda sobre todo (aprendida esta semana)

La etiqueta "negativa/positiva" de los datos **se calcula del precio que ya se
movió** (`cosechador.py`), no del titular. Es **circular**. Por eso:

> **Ninguna palanca que haga el tono "más bajista" se acepta por subir el
> "acierto en negativas". Se acepta solo si mejora la predicción REAL fuera de
> muestra** (Brier/dirección en walk-forward sobre la señal→probabilidad).

Esto no es teórico: el A/B del doomer en "acción" mostró "+10 pts" que, con base
limpia sobre los mismos casos, **se evaporaron** (42.9% base vs 39.3% con doomer).
Toda la Fase 3 de abajo existe bajo esta ley.

---

## FASE 0 — Instrumentación honesta + contrato de métricas
*(De P1§1 y P2 Fase 0. Riesgo nulo. Habilita todo lo demás. No se toca una sola
palanca sin esto.)*

1. **Reporte por segmento** (`engine/validation/evaluar_por_segmento.py`, nuevo):
   - mercado × signo_real × |consenso| → hit rate
   - arquetipo → hit rate individual
   - arquetipo → correlación(confianza_reportada, acierto)
   - fallback vs api → hit rate y distribución de señal
2. **Rastro por predicción** (persistir en JSON/SQLite por caso):
   `{titular, consenso_crudo, ajustes_en_orden, directo_lexico, tono_final,
   prob_calibrada, fuente, signo_real, hit, motivo_lateral}`.
3. **Dataset congelado y versionado** + semilla reproducible (`ENJAMBRE_EXAMEN_SEED`).
4. **Alinear `calibrar_libreta` a partición temporal** (hoy usa shuffle aleatorio
   → fuga temporal; `walk_forward.py` y `ablacion_arquetipos.py` ya son temporales).
5. **El juez oficial:** para cualquier palanca de tono/señal, la métrica que
   decide es el Brier/dirección **out-of-sample en walk-forward**, no el hit-rate
   de la categoría circular.

*Parte ya existe:* `ablacion_arquetipos.py` (por arquetipo), `walk_forward.py`
(ventana expansiva), `calibrar_respaldo.py` (temporal).

---

## FASE 1 — Correctitud y trazabilidad (bajo riesgo, no cambia el comportamiento)
*(De P1. Son arreglos de definición/claridad, no de acierto. Van primero.)*

1. **Arreglar la definición de "confianza"** (P1a, confirmado): hoy
   `_ultimo_consenso` se guarda **antes** de `GANANCIA_CONSENSO`, Plan A y
   `_aplicar_perfil`; la "confianza" del reporte = magnitud de la lectura CRUDA,
   no del tono aplicado. Persistir el estado final (`_tono_final`,
   `_confianza_final`, `_fuente_tono`) y dejar de reportar un valor intermedio
   como si fuera el final (o renombrarlo a "fuerza de lectura cruda").
2. **Dos salidas explícitas y trazables:** `prob_calibrada` (para predicción) vs
   `tono`/`confianza_final` (para el enjambre). Hoy están entrelazadas en el
   nombre; separarlas limpio.

---

## FASE 2 — Palancas de bajo riesgo, robustas al artefacto (gratis o casi)
*(De P2 H3/H4/H5 + infra. Todo detrás de flag `ENJAMBRE_*`, default = hoy.)*

1. **H5 — Calibrar la confianza del LLM por arquetipo.** Aprender
   `confianza_cruda → peso_calibrado` por arquetipo (isotónica/escalado) con
   train, medir con test (walk-forward). Gratis, determinista. Robusta al
   artefacto (no empuja el signo, re-pesa por fiabilidad).
2. **H4 — Consenso robusto** (media recortada al 10% / mediana ponderada),
   `ENJAMBRE_CONSENSO_ROBUSTO ∈ {media, recortada10, mediana}`. Neutraliza a un
   arquetipo sistemáticamente contrario sin apagarlo.
3. **3.1.bis — Hash del prompt en la clave de caché** (`_clave_cache(... hash_prompt)`).
   Infra clara: desbloquea iterar prompts sin `ENJAMBRE_IGNORAR_CACHE` global.
4. **H3 — Plan A suave + léxico como feature.** Reemplazar el corte duro en
   `-umbral` por mezcla continua `tono = α·(consenso·gain) + (1-α)·directo` (α por
   mercado, default 1.0 = hoy). El léxico (`directo`) pasa de rescate a feature.
   *Riesgo medio:* el léxico puede sesgar → validar con el juez limpio.
5. **MINIMO_IA_CONSENSO gradual** (P1c): medir degradación suave vs el corte duro
   0.5 (cobertura, Brier, distribución de laterales) + política explícita de
   fallback/abstención.

---

## FASE 3 — Palancas sospechosas de "ganarle a la métrica" (base limpia OBLIGATORIA)
*(De P2 H1/H2/H7. Van APARTE porque pueden inflar la métrica circular — como el
doomer. Solo se aceptan si mejoran la predicción limpia out-of-sample.)*

1. **H1 — `GANANCIA_CONSENSO` por signo y por mercado** (`gain_pos`/`gain_neg`).
   Grid sobre `neg`, dejando `pos` fijo. **Aceptar solo con base limpia.**
2. **H2 — `peso_tono_invertidores` por mercado** (mismo patrón que `peso_doomer`).
   **Aceptar solo con base limpia.**
3. **H7 — Gating por ambigüedad:** si `|tono| < θ(mercado)` → 0 y no propagar.
   θ sale del histograma hit-rate vs |consenso| (donde cae a ~50%). Depende de si
   el examen acepta "neutro" → flag `ENJAMBRE_GATING_AMBIGUO`.

---

## FASE 4 — Calidad de señal (sube el techo, más costoso, al final)
*(De P2 H6/H8/3.2/3.3/3.4. Lo grande e incierto.)*

1. **H6/3.1 — Few-shot en los prompts de los arquetipos fieles** (institucional,
   macro, value, doomer_selectivo) con casos negativos reales. Requiere 3.1.bis
   primero. El `doomer_selectivo` ya validó que el prompt es palanca (+7.6 pts
   índice). No tocar los prompts de los invertidores (su trabajo es invertir).
2. **3.2 — Relevancia arquetipo × mercado:** bajar el peso de un arquetipo en el
   mercado donde su hit-rate ≈ 50% (p. ej. voces inertes en cripto). No apagarlos.
3. **H8/2.2 — Meta-modelo ligero de dirección** (logística; GBM solo si mejora en
   test): features `[consenso_crudo, directo, std_señales, confianza_media,
   n_disonantes, one_hot(mercado), log(1+n_api)]` → P(up). *Corrección a P2: NO
   existe hoy (`real_optimizer.py` optimiza hechos estilizados, no dirección);
   sería nuevo.* Umbral para producción: AUC > 0.65 en test; si no, queda como
   capa de ranking.
4. **3.3 — `prior_direccional` por mercado** en `perfil_de` como feature/offset
   del meta-modelo.
5. **3.4 — Self-consistency** (3 muestras por arquetipo fiel, voto mayoritario),
   `ENJAMBRE_SELF_CONSISTENCY=1`. Rompe el presupuesto ×3 → solo para el top-N
   arquetipos por contribución al error. Último, opcional.

---

## Reglas transversales (de ambas propuestas + lo aprendido)

- **Flag para todo lo nuevo**, default = comportamiento actual; rollback sin redeploy.
- **Una palanca por PR** (si se apilan y no sube, no se sabe cuál falló).
- **Walk-forward siempre**; dataset congelado; nunca calibrar y medir con el mismo set.
- **Métrica compuesta** (hit_neg, hit_pos, por mercado) PARA MIRAR, pero **el juez
  que decide es el Brier/dirección limpio out-of-sample** (la ley de arriba).
- **CMF intacto:** nada cambia el marco "educativo, no asesoría".

## Lo que NO hacer (de P2 + lo medido)

- No añadir más arquetipos "correctores" incondicionales (ya falló; el selectivo
  funcionó por ser selectivo).
- No subir `GANANCIA_CONSENSO` global a 1.0 (sobre-reacciona; el problema es
  asimétrico, no de escala).
- No tocar los prompts de los invertidores.
- No usar `simular.py` como métrica de dirección (mide hechos estilizados).
- **No aceptar NINGUNA mejora de "negativas" sin base limpia** (el artefacto del doomer).

## Correcciones a las propuestas (para que el plan no herede errores)

- **P2 dice que el meta-modelo de dirección "ya existe en `real_optimizer.py`":**
  falso. Ese optimiza hechos estilizados, no P(up). El meta-modelo es nuevo.
- **P2 usa "~163 casos" y "negativas ~53%":** desactualizado. Hoy hay **678 casos**
  (índice 163 · cripto 220 · acción 189 · oro 20 · petróleo 25); los números por
  mercado son otros.
- **P1 pide walk-forward como si faltara:** ya existe (`walk_forward.py`); lo que
  falta es que el reporte de Fase 0 lo use y alinear `calibrar_libreta`.

---

## Orden recomendado y expectativa honesta

| Fase | Qué | Riesgo | Expectativa |
|---|---|---|---|
| 0 | Instrumentación + juez limpio | Nulo | Habilita todo; sin esto es a ciegas |
| 1 | Confianza bien definida + trazabilidad | Bajo | Correctitud, no acierto |
| 2 | Confianza calibrada, consenso robusto, caché por prompt, Plan A suave | Bajo | Mejora real y segura, modesta |
| 3 | gain_neg / peso_inv / gating **con base limpia** | Medio | Puede ser real o espejismo — la base limpia lo dirá |
| 4 | Few-shot, relevancia×mercado, meta-modelo, self-consistency | Medio-alto | Sube el techo; lo más incierto |

**Expectativa realista:** las Fases 0–2 dan mejoras modestas pero reales y sin
riesgo. La Fase 3 es donde P2 espera el grueso, pero es justo donde el artefacto
engaña — puede que rinda poco una vez medido limpio (como el doomer). La Fase 4
es la que de verdad podría subir el techo, y es la más cara e incierta. El tope
estructural sigue: para cripto/acción la dirección muchas veces **no está en el
texto**.

**Momento:** es trabajo de modelo, invisible en el demo. Recomiendo arrancar
**después del evento del 21**; antes, foco en demo + pitch.

---
*Fin del plan. Es una hoja de ruta; cada fase se mide y se decide con evidencia.*
