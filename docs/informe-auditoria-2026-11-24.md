# El Enjambre — Informe de auditoría científica (24-nov-2026)

*Rubicón Lab. Todo el trabajo del día con su EVIDENCIA (números medidos), el código
que lo produce y el test que lo valida. Para auditoría externa. Acompaña al volcado de
código `docs/codigo-fuente-enjambre.md` (207 archivos, 32.385 líneas).*

## 0. Alcance y honestidad

- **Propósito:** comprobar o descartar científicamente que El Enjambre aporta ventaja
  predictiva. El resultado negativo es un hallazgo válido.
- **Todo lo de este informe es EXPLORATORIO:** corre sobre el banco histórico de shocks
  (sesgado por selección, posible memoria del LLM), n chico. El veredicto DEFINITIVO es
  prospectivo (Fase 6, pendiente de tiempo). Aun así, la evidencia es consistente.
- **Datos de reproducción:** `docs/datos-investigacion/` (dataset sin fuga + señales A2
  + features de riesgo). Cada herramienta corre offline, sin IA salvo donde se indica.

## 1. Fase 0 — Integridad (correcciones P0 de la auditoría científica)

Cuatro defectos reproducidos y corregidos, cada uno con test de regresión:

| ID | Defecto | Corrección | Código · test |
|---|---|---|---|
| F01 | `walk_forward.cargar` usaba `pct_real` (etiqueta contaminada) | rehúsa `pct_real` no certificada; usa `pct_corr` | `calibration/walk_forward.py` · `test_walk_forward.py` |
| F02 | A0 contaba etiquetas del MISMO día (no maduradas) | madura por fecha; los casos del día no se informan | `calibration/ablacion.py::_items_a0` · `test_ablacion.py` |
| F03 | la evidencia aceptaba `event_timestamp` futuro | rechaza evento posterior al `as_of` | `evidence/contrato.py` · `test_evidencia.py` |
| F04 | `particionar` ignoraba el embargo del holdout | aplica el mismo embargo que el manifiesto | `calibration/holdout.py` · `test_holdout.py` |

Seguridad: se quitó `?clave=` (token en la URL) de dos endpoints; el tablero vive en
`/panel` con cabecera. `server.py` · `test_servidor.py`.

## 2. El torneo de modelos — hallazgos con evidencia

### 2.1 Ablación A0–A5 (dirección, índice, sin fuga)
`calibration/ablacion.py` (tests `test_ablacion.py`). Acierto direccional:

| Escalón | Qué | Acierto |
|---|---|---:|
| A0 | piso "los índices suben" (train-only) | 64.5 % |
| A1 | léxico del titular | 59.3 % |
| **A2** | **un LLM neutral** | **65.5 %** |
| A3 | consenso de 110 cerebros | 62.7 % |
| A4 | ABM completo (10.150 agentes) | 56.3 % |

**Gate pareado por evento A4−A3 = −0.063, IC95 [−0.124, −0.007] (excluye 0):** el ABM
**resta** frente al consenso, significativo. `ablacion.gate_pareado`.

### 2.2 M4 vs A3 — un LLM vs los 110 cerebros
`calibration/a2_vs_a3.py` + `un_llm.py` (A2 corrido con la clave del motor, 641 señales).

- Índice: **A2 65.5 % vs A3 66.4 %**, diferencia pareada por evento **−0.009, IC95
  [−0.061, 0.042]** → no distinguible. Acuerdo de signo **92 %**, correlación **0.86**.
- **Un solo LLM iguala al consenso de 110.** → `docs/hallazgo-a2-un-llm.md`

### 2.3 Metamodelo M13 vs M13-null
`calibration/metamodelo.py` (`test_metamodelo.py`). Logística con/sin features del ABM:

- Índice: Brier **0.2253 (con ABM) vs 0.2238 (sin)**, media(d) −0.0014, IC95
  [−0.0133, 0.0099] → **las features del ABM no bajan el error.** → `docs/hallazgo-metamodelo.md`

### 2.4 Bootstrap multiway (incertidumbre honesta)
`calibration/intervalos_multiway.py` (`test_intervalos_multiway.py`). La "señal fuerte"
(77.4 %) pasa de IC [69.6–81.0] por activo a **[54.5–92.3] por período**: el "80 % con
convicción" NO está establecido. → `docs/hallazgo-bootstrap-multiway.md`

### 2.5 Fase 2 — Barrido de población
`calibration/barrido_poblacion.py` (`test_barrido_poblacion.py`). Capital constante,
señales congeladas, índice, 3 semillas:

| Agentes | Acierto medio | Dispersión por semilla |
|---|---:|---|
| 10.150 | 58.9 % | estrecha (57–61) |
| 1.016 | 52.0 % | **enorme (39–61)** |
| 510 | 59.2 % | ancha (55–63) |

**Más agentes no mejoran el acierto; el enjambre chico es mucho más ruidoso.** El valor
del enjambre grande es ESTABILIDAD, no acierto. *(La conclusión provisional de 1 semilla
—"el chico gana"— era suerte de semilla; corregida con 3.)* → `docs/hallazgo-barrido-poblacion.md`

### 2.6 Fase 3 — Diversidad de arquetipos
`calibration/correlacion_cerebros.py` (`test_correlacion_cerebros.py`). Correlación de
**señales** (no del error, que tiene un artefacto por el `y` compartido — corregido):

- Índice: ρ = 0.065 → **~5.9 opiniones efectivas de 9.** Los arquetipos SON diversos,
  pero en ESTILO sobre la misma noticia; su promedio recupera la lectura central = la
  de 1 LLM. → `docs/hallazgo-diversidad-arquetipos.md`

### 2.7 Fase 4 — ¿Predice el RIESGO? (H14) — CERRADA negativa
`calibration/riesgo_abm.py` (`test_riesgo_abm.py`). Objetivo: magnitud real `|pct_corr|`.

- Salidas escalares (índice): Spearman ≈ 0; añadirlas EMPEORA el MAE (1.283 vs 1.222).
- **Features ricas de microestructura** (re-corriendo 142 sims: vol simulada,
  desequilibrio de órdenes, overshoot, reversión, rango, dispersión): **todas Spearman
  ≈ 0 (−0.08 a +0.02)**; MAE 1.241 vs 1.172. **El ABM tampoco predice el riesgo.**
  → `docs/hallazgo-riesgo-abm.md`

### 2.8 Fase 5 — Predictor calibrado + abstención
`calibration/predictor_calibrado.py` (`test_predictor_calibrado.py`).

- Índice: Brier skill **+0.045**, ECE 0.087; abstención sube el acierto a **70 %** en el
  25 % más confiado (vs 65 % total), pero frágil (test n=43).
- Todos los mercados: sin habilidad; la abstención empeora. → `docs/hallazgo-predictor-calibrado.md`

### 2.9 Fase 6 — Prospectivo (maquinaria terminada; resultado = tiempo)
`calibration/evaluar_prospectivo.py` (`test_evaluar_prospectivo.py`) +
`docs/preregistro-fase6.md` (protocolo congelado). Registro inmutable en producción:
15 selladas, 6 resueltas, **todas de acciones (0 índice)** → la cohorte aún no prueba la
hipótesis; falta activar el sellado diario de índice + tiempo.

## 3. Veredicto consolidado (7 evidencias, todas medidas)

1. El ABM resta vs el consenso (significativo). 2. El consenso apenas supera "los
índices suben". 3. Las features del ABM no bajan el Brier. 4. Un LLM iguala a los 110.
5. Más agentes no ayudan (solo estabilidad). 6. Los arquetipos son diversos en estilo,
no en información. 7. El ABM no predice el riesgo (ni con features ricas).

> **El valor predictivo (débil, solo índice, ~65 %, frágil) lo captura UNA sola lectura
> de IA del titular. Los 110 cerebros y los 10.150 agentes aportan valor de PRODUCTO y
> VISUALIZACIÓN, no de predicción — ni de dirección ni de riesgo.** Veredicto definitivo:
> prospectivo (Fase 6), pendiente de tiempo.

## 4. Mapa código ↔ hallazgo (para el auditor)

Cada módulo en `engine/calibration/` tiene su test en `engine/validation/`:
`ablacion` (+gate_pareado), `a2_vs_a3`, `un_llm` (A2), `metamodelo`, `intervalos_multiway`,
`holdout`, `walk_forward`, `barrido_poblacion`, `correlacion_cerebros`, `riesgo_abm`,
`predictor_calibrado`, `evaluar_prospectivo`. El endpoint Plan B (A2 vía Render):
`server.py::/api/experimento/a2`. Datos: `docs/datos-investigacion/`. Hallazgos narrados:
`docs/hallazgo-*.md`, `docs/plan-maestro-v5.md`, `docs/auditoria-cientifica.md`.

## 5. Reproducir (desde la raíz del repo)

```bash
D=docs/datos-investigacion
python3 engine/calibration/ablacion.py $D/calibracion.con_fecha.json $D/calibracion.json --a2 $D/a2_senales.json
python3 engine/calibration/a2_vs_a3.py $D/calibracion.con_fecha.json $D/calibracion.json $D/a2_senales.json
python3 engine/calibration/metamodelo.py $D/calibracion.con_fecha.json $D/calibracion.json
python3 engine/calibration/correlacion_cerebros.py $D/calibracion.con_fecha.json $D/calibracion.json
python3 engine/calibration/riesgo_abm.py $D/calibracion.con_fecha.json $D/calibracion.json
python3 engine/calibration/predictor_calibrado.py $D/calibracion.con_fecha.json
# barrido de población (lento, re-corre sims): engine/calibration/barrido_poblacion.py
# tests: cd engine && python3 -m pytest validation/ -q
```
