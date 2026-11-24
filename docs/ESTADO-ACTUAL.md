# ESTADO ACTUAL Y CONTINUIDAD — léeme primero

> **Para Claude en una sesión nueva.** Este archivo es el punto de continuidad: dónde
> vamos, cómo trabajamos y qué sigue. Una sesión nueva NO recuerda el chat anterior,
> pero todo el estado vive aquí y en los docs que se citan. Actualiza este archivo
> cuando cierres un avance importante. Fecha de corte: 2026-11-24.

## 1. La misión (el porqué de todo)

**Comprobar o descartar científicamente** que El Enjambre tiene ventaja predictiva
real en el mercado — no que lo parezca. El resultado negativo también es un hallazgo
válido. Dueño: **Giorgio** (Rubicón Lab), no programador: explícale en **español
simple, con analogías, y opinión fuerte y sincera** (él la pide). El presupuesto NO
es un bloqueo ("si hay que gastar en IA, hazlo").

## 2. Cómo trabajamos (reglas de esta etapa)

- **Plan rector:** `docs/plan-maestro-v5.md` (sintetiza `docs/auditoria-cientifica.md`).
  Supersede v4/v3. Ahí están el torneo M0–M13 y las fases 0–7.
- **Nada se declara "listo" sin evidencia:** cada cambio con tests; se corren y se
  muestran. No inventar resultados; si falta la clave o datos, decirlo.
- **Rama de trabajo:** `claude/m-d-file-6z1e63`. Commits en español. Trailers al final
  de cada commit:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` y
  `Claude-Session: https://claude.ai/code/session_01PS8KRMqGmbUdb1etMtuQe2`.
- **Desplegar (cuando la suite completa esté verde):** `git checkout main && git merge
  --ff-only claude/m-d-file-6z1e63 && git push origin main` → Render reconstruye el
  motor SOLO si cambió `engine/`; Vercel el frontend si cambió `web/`. Verificar el
  motor con `GET https://enjambre-motor.onrender.com/salud` (campo `version` = sha
  corto). Volver a la rama. La suite completa tarda ~24 min (corre simulaciones).
- **Seguridad (no negociable):** nunca mandar el email de Giorgio a servicios externos;
  `ANTHROPIC_API_KEY` solo en entornos, nunca en chat/código/GitHub;
  `ENJAMBRE_PIPELINE_TOKEN` solo en Render + secreto de GitHub; sin identificadores de
  modelo en commits/PR/código. No crear PR salvo que lo pida.
- **Simplicidad (regla 5 de la biblia):** no construir la catedral (predictor completo,
  12 especialistas, Monte Carlo masivo, 50–100k agentes) antes de probar la tesis.

## 3. Dónde vamos — hecho vs pendiente

### Hecho (en la rama / producción)
- **Fase 0 integridad (auditoría científica F01–F04):** walk_forward rehúsa `pct_real`
  no certificada; A0 madura etiquetas (casos del mismo día no se informan); evidencia
  rechaza `event_timestamp` futuro; `particionar` aplica el embargo. Con tests.
- **Ablación A0–A5** (`engine/calibration/ablacion.py`) + **gate pareado por evento**.
- **Metamodelo M13 vs M13-null** (`engine/calibration/metamodelo.py`).
- **Holdout congelado** (hash) y **bootstrap multiway** (con su caveat honesto).
- **Capa de evidencia** point-in-time en modo sombra (`engine/evidence/`).
- **Honestidad de producto:** la web separa "movimiento simulado" (ABM, visual) de
  "lectura" (consenso, solo si es fiable) en muro, archivo, panel y duelo.
- **Ritual auto-sanador** (`.github/workflows/ritual-diario.yml`): verifica + reintenta.
- **A2 listo para correr** (`engine/calibration/un_llm.py`) — ver §5.
- **Comparación titular por titular A2 vs A3 lista** (`engine/calibration/a2_vs_a3.py`,
  con tests): misma cobertura, pareado por evento, discordancias, tabla caso a caso.
  Probada con un A2 falso (solo cañería); falta correrla con el A2 real.

### Pendiente
- ✅ **M4 vs A3 HECHO** (vía Plan B, endpoint en Render): **un LLM iguala al consenso
  de 110** (índice 65.5% vs 66.4%, pareado no distinguible). → `docs/hallazgo-a2-un-llm.md`.
- **Rotar `ENJAMBRE_PIPELINE_TOKEN`** (se expuso en el chat): Render + secreto GitHub.
- **F05** banco cronológico de flujo (eventos por reglas ex-ante, sin sesgo de
  selección) — necesita recolección nueva.
- **F06** horizonte intradía con calendario por bolsa.
- **A5 / evidencia B-vs-D** y **features ricas del ABM** (order imbalance, manada,
  dispersión…) — necesitan re-correr simulaciones y la clave.
- **Cohorte prospectiva** sellada — la única prueba limpia (necesita tiempo; el ritual
  ya la alimenta).

## 4. Hallazgos clave (honestos, hasta hoy)

1. **El ABM NO mejora la predicción de dirección; la resta.** Tres evidencias
   independientes: ablación (A4 56% < A3 63% en índice), gate pareado (media A4−A3
   = −0.063, IC95 [−0.124,−0.007], **significativo**), y metamodelo (features ABM no
   bajan el Brier). → `docs/hallazgo-ablacion.md`, `docs/hallazgo-metamodelo.md`.
2. **El valor predictivo (el poco que hay) vive en el consenso LLM (A3), solo en
   índices, y es frágil:** ~62–65% apenas iguala el piso "los índices suben" (A0 honesto
   64.5%). Fuera de índice, ~azar.
3. **El "80% con convicción" NO está establecido** (IC real [54.5–92.3] por período).
   → `docs/hallazgo-bootstrap-multiway.md`.
4. **Un solo LLM iguala al consenso de 110 cerebros** (A2≈A3): la diversidad no
   compra acierto; basta 1 llamada para la dirección (las 110 son valor de producto/
   visualización). → `docs/hallazgo-a2-un-llm.md`.
5. Conclusión de producto: El Enjambre es una **visualización / focus group sintético**
   genuino; NO se vende como predictor. El veredicto definitivo es prospectivo.

## 5. Próximo paso inmediato (sesión nueva con la clave)

Pega en la sesión nueva: *"Ya cargué ANTHROPIC_API_KEY. Corre el experimento A2/M4
siguiendo docs/runbook-experimento-a2.md (incluido el paso 2b titular por titular),
con honestidad, y guárdalo en la rama claude/m-d-file-6z1e63."*

> **Ojo (2026-11-24):** la sesión de ese día NO tenía la clave aunque ya estaba
> guardada en el entorno — se había abierto antes de guardarla. Hay que abrir una
> sesión NUEVA después de guardar la clave.
Los datos ya están en `docs/datos-investigacion/`. El runbook tiene los comandos
exactos y cómo interpretar (A2≈A3 ⇒ la diversidad de 110 cerebros no paga).

## 6. Mapa rápido de documentos

| Doc | Qué |
|---|---|
| `docs/plan-maestro-v5.md` | **el plan rector** (torneo, fases, reglas) |
| `docs/auditoria-cientifica.md` | la auditoría externa que adoptamos |
| `docs/analisis-auditoria-cientifica.md` | análisis en frío + qué se corrigió |
| `docs/runbook-experimento-a2.md` | cómo correr M4 vs A3 (próximo paso) |
| `docs/hallazgo-*.md` | los hallazgos medidos |
| `docs/resumen-sesion-2026-11-23.md` | bitácora de la sesión previa |
| `docs/codigo-fuente-enjambre.md` | volcado del código para auditoría externa |

## 7. Progreso del torneo (fases 2–6) — 2026-11-24

- **Fase 2 (escala):** más agentes NO mejoran el acierto; solo dan estabilidad. `docs/hallazgo-barrido-poblacion.md`
- **Fase 3 (diversidad):** 9 arquetipos diversos en estilo, no en información. `docs/hallazgo-diversidad-arquetipos.md`
- **Fase 4 (riesgo, H14):** CERRADA negativa — el ABM tampoco predice la magnitud, ni con features ricas. `docs/hallazgo-riesgo-abm.md`
- **Fase 5 (calibrado):** ventaja marginal y frágil solo en índice; abstención útil solo ahí. `docs/hallazgo-predictor-calibrado.md`
- **Fase 6 (prospectivo):** maquinaria TERMINADA (pre-registro `docs/preregistro-fase6.md` + evaluador `evaluar_prospectivo.py`). Falta solo TIEMPO y activar el sellado diario de ÍNDICE (hoy la cohorte es de acciones). Estado: 15 selladas, 6 resueltas (sin valor, n chico).
- **Veredicto acumulado (histórico):** 7 evidencias consistentes de que el ABM/ensemble no aporta valor predictivo sobre 1 LLM. El valor es de producto/visualización. La prueba definitiva es la Fase 6 prospectiva (necesita tiempo).
