# THE LAST EXPERIMENT — Informe de desarrollo (pre-T0)

*Rubicón Lab · rama `research/last-experiment` · HEAD de partida `fc795b8`. Qué está
hecho, qué falta, viabilidad, potencia y bloqueos. Honesto: la prioridad es la verdad,
no salvar el proyecto.*

## 1. Estado: implementación COMPLETA, NO congelada, NO activada

Se implementaron las tareas **L0–L10** de la Parte I en un módulo aislado
`engine/research/last_experiment/` (2.586 líneas) con **594 líneas de tests** (61 tests,
todos en verde) + el fix F12 en `calibration/riesgo_abm.py` con su test. No se tocó el
frontend ni el motor (solo se REUTILIZARON sus primitivos). No se gastó dinero, no se
contrató nada, no se activó el sellado.

| Tarea | Módulo | Estado | Evidencia |
|---|---|---|---|
| L0 | — | ✅ | HEAD `fc795b8`; 78 tests previos verdes |
| L1 | `config.py` | ✅ | `event_id` determinista `SPY:fecha:2D:v1`; validación |
| L2 | `calendar.py` | ✅ | festivos, media sesión, DST, Viernes Santo; 10 tests |
| L3 | `evidence.py` | ✅ | snapshot PIT, rechazo naive/futuro, paquete determinista |
| L4 | `models.py`,`features.py`,`llm.py` | ✅ | P0–P4, logística L2, Platt, selección de C |
| L5 | `abm.py` | ✅ | adaptador real del motor, 3 semillas, 6 features; P5⊇P4 |
| L6 | `ledger.py`,`resolver.py`,`runner.py` | ✅ | sellado append-only, triggers, hash-chain, maduración |
| L7 | `evaluate.py` | ✅ | Brier pareado, moving-block bootstrap, gate doble |
| L8 | `economics.py` | ✅ | paper trading, costes base/estrés, gate económico |
| L9 | `cli.py freeze` + manifest | ✅ | congela T0/T1/B*/hashes; validación de freeze |
| L10 | `cli.py`, workflow, docs | ✅ | 7 comandos, dry-run end-to-end, workflow desactivado |

## 2. Verificación reproducible

```bash
cd engine
python -m pytest validation/test_last_experiment_*.py validation/test_riesgo_abm.py -q
python -m research.last_experiment.cli dry-run --fixture synthetic
```

- **Dry-run end-to-end:** entrena, sella 6 probabilidades × evento, resuelve con precios
  ficticios, evalúa (Brier pareado + bootstrap) y corre paper trading. Cadena de hashes
  verificada (`cadena_ok: True`). Con el ABM SINTÉTICO (sin información real), el gate da
  correctamente **False** — la cañería no "inventa" ventaja.
- **ABM real medido:** `abm.features` corre contra el motor real (10.150 agentes):
  **6,6 s por semilla, ~20 s las 3 semillas**. El deadline del contrato es 10 min →
  holgado. Features extraídas del código, no de gráficos.

## 3. Potencia (I.6) — ADVERTENCIA

Estimada sobre el fixture sintético (la σ REAL debe medirse en el panel histórico antes
de T0). `n ≈ (1.96+0.84)² σ² / (Δ−0.005)²`:

| σ(d_t) observada | n para Δ=0.010 | n para Δ=0.020 |
|---|---:|---:|
| 0.015 | 75 | 9 |
| 0.068 | 1.440 | 160 |
| 0.078 | 1.914 | 213 |

**Lectura honesta:** si el efecto real del ABM es pequeño (Δ≈0.01) y la varianza de `d_t`
es media/alta, **100 pares NO bastan** para detectarlo: el resultado saldría *inconcluso*,
que por la regla empresarial = **cierre**. Hay que medir σ en el panel real y, si la
potencia es baja, avisar a Giorgio ANTES de activar (I.6).

## 4. Correcciones de auditoría

- **F01–F04:** verificadas (tests de regresión previos en verde).
- **F05:** `SealedForecast.p_up` sella la probabilidad calibrada de P0–P5.
- **F06/F07:** `evaluate.py` nuevo usa p selladas, pares verdaderos y agrupación por
  sesión/evento explícito; NO usa `evaluar_prospectivo.py` (prevalencia del test) para el
  gate.
- **F08/F13:** etiqueta madura solo tras cierre de salida + barra FINAL (`resolver.py`).
- **F09:** identidad de evento determinista; el nuevo ledger está AISLADO del de
  producción (no se contamina con acciones ni versiones antiguas).
- **F12:** `riesgo_abm.spearman` → scipy + `None` para constante (bug de empates
  corregido, con test).
- **F10/F14:** NO se repite el barrido de población ni se amplía el alcance.

## 5. Bloqueos para llegar a T0 (requieren decisión/credenciales de Giorgio)

1. **Proveedor de precios point-in-time de SPY** con barra final certificada
   (Alpaca/Yahoo con contrato válido). Es el bloqueo principal: sin él no hay entrada/
   salida reales ni resolución. Interfaz lista (`resolver.ProveedorPrecios`); falta el
   adaptador real + validación de licencia/calidad.
2. **Panel histórico de desarrollo** (no el banco de shocks) para entrenar P0–P5 y fijar
   B*. Pendiente de construir con el proveedor PIT.
3. **Clave Anthropic** para P2/P3 en vivo y presupuesto de API dentro de los USD 300.
4. **Fuentes macro con vintage** (FRED/BLS/BEA) para sorpresas (opcional; omitir si no se
   certifica).
5. **Aprobación y presupuesto congelado** → `freeze` → activación.

## 6. Qué NO se hizo (a propósito)

No se activó el sellado en vivo, no se gastó dinero, no se construyó el panel real (falta
proveedor PIT aprobado), no se usó el banco de shocks como evidencia, no se tocó
producción, no se crearon nuevas hipótesis ni se movieron los gates. Todo eso espera la
decisión del fundador.

## 7. Veredicto previo (contexto, no resultado)

Toda la evidencia histórica (7 análisis) apunta a que el ABM no aporta ventaja sobre una
sola lectura LLM. Este experimento es la prueba prospectiva limpia para confirmarlo o
refutarlo. Está construido para **descubrir la verdad**, no para rescatar el proyecto.
