# Plan de evolución de El Enjambre — v3

> **⚠️ SUPERSEDED por el PLAN v4 (`docs/plan-v4-implementacion.md`), 23-nov-2026.**
> La auditoría v4 es más rigurosa y es ahora el plan RECTOR. Ya se ejecutó su lote
> de rigor+seguridad (sin clave): A0 train-only, inferencia pareada A3-vs-A4 por
> evento (reemplaza el atajo "multiway"), guardia anti-fuga en el holdout, caché A2
> versionado y token fuera de la URL (se quitó `?clave=`). Pendiente de la clave y de
> datos prospectivos: A2 real, features del ABM (H2), evidencia B-vs-D y el
> experimento prospectivo confirmatorio (v4 Fase 07). Lo de abajo (v3) se conserva
> como contexto histórico.

*Rubicón Lab · El Enjambre · v3, 2026-11-23. Reorganiza la ejecución del plan para
eliminar dependencias circulares, priorizar evidencia prospectiva y coordinar DOS
agentes (Claude y Codex). Incorpora la auditoría integral del 23-11
(`docs/analisis-auditoria-v3.md`). Supersede a v2.*

---

## La estrella polar

> **No queremos que El Enjambre parezca más inteligente. Queremos demostrar, con
> resultados fuera de muestra, que aporta valor frente a un modelo simple.**

**La métrica de éxito NO es "¿cuántos agentes?" ni "¿qué % histórico más alto?".
Es:** ¿cuál es la reducción de error frente al mejor baseline aplicable, sobre
predicciones selladas antes del desenlace, en un universo predefinido, con qué
incertidumbre, cobertura, latencia y coste — y qué parte proviene realmente del
mecanismo multiagente?

### La regla de oro

> Ninguna cifra sin denominador. Ninguna predicción sin timestamp. Ninguna
> promoción sin holdout. Ninguna mejora sin comparación. Ningún consenso sin medir
> su independencia. Ningún "test verde" prueba por sí solo capacidad predictiva.

### Las dos tesis (las decide la evidencia)

- **A — Predictor:** la señal sobrevive a datos temporalmente válidos, más
  instrumentos y comparación fuera de muestra → capacidad predictiva **acotada**
  (por mercado × evento × horizonte × régimen), nunca "predice todo".
- **B — Simulador / focus group sintético:** si la ventaja se debilita al
  controlar memoria, selección y correlación → sigue siendo un gran producto, pero
  la comunicación no vende predicción no demostrada.

---

## Reparto de carriles (hay dos agentes)

| Carril | Quién | Estado |
|---|---|---|
| Registro prospectivo (Fase 7) + ciencia/análisis/ablación | **Claude** | En curso |
| Identidad y persistencia macro (PR #34/#35), cosecha por calendario | **Codex** | PRs abiertos |
| Gobierno (rama canónica, CI, política de merge) | **Giorgio decide** | Pendiente |
| Revisión de los PR de Codex | **Claude** | Acordado |

**Regla de no-colisión:** antes de tocar `walk_forward.py`, `backtest.py`,
`persistencia.py` (identidad), coordinar con lo que trae Codex. Los bugs del
registro (ya resueltos) no tocaban esos archivos.

---

## Estado al 23-11-2026

- ✅ **Fase 7 (registro prospectivo): desplegada** (v`60daa77`) y **endurecida**:
  arreglados los 4 bugs de la auditoría v3 (falla silenciosa + todos los tickers;
  fin de semana; cobertura por SQL completo; resolución atómica). 19 tests.
- ✅ **Fase 0 (ciencia): medida.** Índice 62.7% [52.5–70.4]; convicción fuerte
  77-80% [69.6–81.0]; sin contaminación; reponderar no mejora la dirección.
- ⏳ **Codex:** PR #34 (piloto macro offline) y #35 (integridad de evaluación) —
  buena base, aún en draft.
- ⚠️ **Deuda confirmada:** P0-01 (walk_forward ordena por fecha de procesamiento,
  no de la noticia) — no afecta el 63%/80% (usan `fecha_base`), pero debe
  arreglarse antes de confiar en el calibrador.

---

# VÍA CIENCIA

## Fase 0A — Gobierno del código y prueba reproducible *(Giorgio + Claude)*
Elegir rama canónica y política de merge; congelar `baseline_model_B` por commit +
hashes de prompts/config; **CI en cada PR** (pytest sin red ni credenciales, lint,
build web, validación de esquemas); migraciones solo en DB temporal.
**Gate:** un PR no pasa sin tests; no se toca producción, holdout ni el predictor.

## Fase 7 — Registro prospectivo auditable *(Claude · en curso)*
✅ Base + enganche + resolución + tablero desplegados; 4 bugs de integridad
resueltos. **Falta:** separar `prospective` vs `historical_reconstruction`;
reconciliador diario intentos→registro→resolución; contrato de resolución por
calendario versionado; registrar la probabilidad/crudo y la versión del calibrador.
**Gate:** reconciliación 100% de intentos (resultado guardado o fallo explícito,
nunca silencio). **No** se exige tasa de acierto mínima en esta fase.

## Fase 0B — Identidad y persistencia macro *(Codex · PR #34→#35)*
Esquema `events / observations / simulations / simulation_observations / outcomes /
predictions / audit_log`; ID de reintento ≠ run ID; sin `INSERT OR REPLACE`
silencioso; migración en copia aislada. **Claude revisa los PR.**
**Gate:** ninguna pérdida ni reemplazo silencioso; identidad determinista; suite verde.

## Fase 0C — Contrato de objetivo, datos y relojes
Acordar por objetivo `published_at`, `available_at`, `as_of`, `signal_due_at`,
`entry_at`, `exit_at`, `label_available_at`; calendario de mercado (IANA/DST),
precios ajustados/no, neutro. Priorizar 1-2 contratos **operables** (p. ej. próxima
apertura a 1-2 sesiones). **Gate:** cualquier evaluador reproduce la etiqueta; no
ingiere datos posteriores al `as_of`. *(Borrador: Codex `protocolo-evaluacion-macro.md`.)*

## Fase 0D — Dataset por calendario + holdout blindado
Cosechar **todos** los eventos del calendario (CPI, FOMC, empleo, earnings), sin
filtrar por retorno; registrar causa de exclusión; banco antiguo = estrés.
Manifiesto JSON con hash SHA-256 (grupo, contrato, proveedor, ventana, esquema);
splits por `event_group_id` con purga y embargo en tiempo; modo `shadow`.
**Gate:** `holdout_manifest.sha256` reproducible y congelado; unidad de
independencia justificada.

## Fase 0E — Incertidumbre, informes y CLI
Comparaciones pareadas; re-muestreo por **evento/bloque** (no por fila cuando la
dependencia es insuficiente — eso se reporta como incertidumbre, no como IC
estrecho); análisis por instrumento/régimen/fecha; baselines solo-train; CLI que
separe diagnóstico de promoción anidada; corrección por múltiples hipótesis.
**Gate:** reporte verificable por código y manifiesto, sin elegir resultados
después de ver el test.

## Fase 1 — Evidencia point-in-time *(modo sombra)*
Módulo `engine/evidence/`: noticia, macro, consenso previo, expectativas, qué pudo
estar descontado, contradicciones, URLs, snapshots, `available_at`, `evidence_hash`.
Retrieval centralizado; nunca features del futuro. Comparar **B (solo titular)** vs
**D (evidencia)** con mismos cerebros y población.
**Gate:** mejora fuera de muestra, no solo mejor narrativa. No promover todavía.

## Fase 2 — Probabilidad calibrada, abstención y cobertura
Calibradores solo con train; separar dirección / probabilidad / fuerza / cobertura;
política `predict/abstain` con razón; curvas riesgo–cobertura; ECE/Brier/log-loss
estratificados. *(La reponderación histórica por arquetipo ya se probó sin mejorar
el signo: no repetir sin nueva hipótesis.)*
**Gate:** mejora probabilística OOS y cobertura transparente; nunca pasar de 50% a
80% reportando un subconjunto sin decir cuánto se abstiene.

## Fase 3 — Aislar el valor de la simulación *(ablación A0–A5)*
- **A0** prior/clase mayoritaria + momentum + precio sin noticias
- **A1** léxico/sentimiento simple del titular
- **A2** UN solo LLM con el titular, sin agentes
- **A3** 110 cerebros LLM agregados, **sin ABM**
- **A4** ABM completo (10.150 agentes)
- **A5** ABM + evidencia `as_of`

Mismos eventos, horizontes y respuestas LLM congeladas. **Gate:** cuantificar
cuánto mejora A4 sobre A3 (o demostrar que no). Si A3 ≈ A4, el enjambre es buen
producto pero **no** se le atribuye predicción incremental.

## Fase 4 — A/B/C/D con promoción pre-registrada
A=baselines fuertes + LLM aislado; B=Enjambre congelado; C=+mejoras validadas;
D=C+evidencia. Pareado por `event_group_id`; pre-registrar métrica primaria, efecto
mínimo, cobertura mínima, potencia y corrección múltiple; **test final una vez**.
**Gate:** afirmar con alcance explícito ("mejora Brier vs baseline X sobre n
eventos de Y período, IC y cobertura") **o** "no verificado". **El mejor resultado
puede ser negativo, y eso también es un resultado.**

---

# VÍA INGENIERÍA *(según necesidad)*

## Fase 5 — Infraestructura durable
Separar HTTP de cómputo; job durable `pending/running/retry/succeeded/failed`; cola
+ worker; lock/lease; idempotencia; presupuesto LLM por simulación; reconciliador.
**Gate:** crash/restart no pierde ni duplica; prueba de carga con límite explícito.

## Fase 6 — Microestructura *(opcional, objetivo separado)*
Spread, profundidad, slippage, impacto — solo si se vende simulación de ejecución o
una A/B demuestra beneficio predictivo. **Gate:** realismo **y** utilidad
independiente; no confundir realismo con alfa.

## Fase 8 — Modularización multivertical
Contratos `Population / AgentPolicy / InteractionNetwork / Environment /
Intervention / Outcome / Evaluator / DataProvider`; núcleo genérico + adaptador
financiero. **Gate:** vertical financiera intacta + piloto de otra vertical sin
duplicar infraestructura. *(Un modelo útil en índices no predice consumidores
automáticamente.)*

---

## Orden de trabajo

```
AHORA
 ├─ Claude: Fase 7 endurecida ✅  → reconciliador + contrato de resolución
 ├─ Codex:  cerrar PR #34 → #35 (identidad macro)   [Claude revisa]
 ├─ Giorgio+Claude: Fase 0A (CI, rama canónica, baseline B congelado)
 │
 ├─ Fase 0C contrato de etiqueta → 0D calendario+holdout → 0E incertidumbre
 │       └─ Fase 1 evidencia (sombra) → Fase 2 probabilidad/abstención
 │               └─ Fase 3 ablación A0–A5 → Fase 4 A/B/C/D → veredicto
 └─ En paralelo: Fase 5 infra (según demanda) · Después: 6, 8
```

## Cómo comunicar las cifras
**Correcto:** *"En la muestra evaluada, X% en índices, IC Y–Z, bajo el horizonte y
etiqueta especificados; concentrado en ciertos instrumentos y pendiente de más
muestra."* **Evitar:** "acierta el 80%", "10.150 agentes predicen el mercado", "la
IA supera al mercado". El 80% es un subconjunto con n=30: siempre con cobertura,
instrumento, período, horizonte e intervalo.

## La pregunta que guía el próximo ciclo
> Si entregamos a los mismos agentes información más completa, verificable y
> temporalmente correcta, ¿mejora su capacidad de anticipar al mercado?
