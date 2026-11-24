# THE LAST EXPERIMENT — Protocolo confirmatorio P0–P5 (SPY)

> **Estado:** especificación implementada, **NO congelada y NO activada**. Congelar
> (fijar T0, B*, hashes, presupuesto) y activar (sellar/resolver en vivo) requiere la
> **aprobación explícita de Giorgio**. Este documento fija las reglas ANTES de ver
> resultados prospectivos (regla de oro: no se cambian después).
>
> Rama aislada: `research/last-experiment`. No toca producción. Capital real = USD 0.

Fuente: `EL_ENJAMBRE_ULTIMO_EXPERIMENTO_Y_AUDITORIA.md`, Partes I–III. Implementación en
`engine/research/last_experiment/`. Tests en `engine/validation/test_last_experiment_*.py`.

## 1. La pregunta que decide el proyecto

1. ¿Una combinación de datos financieros + análisis contextual (LLM) contiene señal útil?
2. **¿La simulación ABM MEJORA esa combinación usando EXACTAMENTE la misma información?**

La (2) decide la continuidad de El Enjambre. **Si P5 (con ABM) no supera todos los
gates frente a P4 (sin ABM) y a B*, el producto predictivo se archiva** — incluso si el
resultado queda inconcluso.

## 2. El torneo (todos congelados antes de T0)

| ID | Modelo | Inputs | Implementación |
|---|---|---|---|
| P0 | Tasa base | retornos SPY ya maduros | constante beta-binomial(1,1) |
| P1 | Cuantitativo | precio/volatilidad PIT | logística L2 |
| P2 | LLM titular | texto hasta el cutoff | 1 llamada + Platt |
| P3 | LLM contextual | titular + evidencia certificada | 1 llamada + Platt |
| P4 | Híbrido sin ABM | P1 + señales de P3 (score + 9 arquetipos + media/desv) | logística L2 |
| P5 | Híbrido con ABM | **exactamente P4** + 6 features del motor | misma logística L2 |

**Control de información (clave):** P4 recibe TODAS las señales del LLM que alimentan al
ABM (score contextual, vector de 9 arquetipos, su media y dispersión). P5 solo añade el
resumen de la simulación. Así `P5 − P4` aísla el aporte del ENJAMBRE, no de información
extra. Verificado por test (`test_control_informacion_p5_superconjunto_p4`).

## 3. Contrato temporal exacto (I.3)

- **Cutoff:** 30 min antes del cierre de NYSE (15:30 ET rueda normal; 12:30 ET media
  sesión). Todos los timestamps en UTC *aware*. Calendario propio con festivos, medias
  sesiones y DST (`calendar.py`, tests L2).
- **Deadline de emisión:** cutoff + 10 min. Si el ABM se pasa, se registra fallo y **no**
  se reconstruye el pronóstico. (Latencia ABM medida: ~20 s las 3 semillas → holgado.)
- **Entrada:** cierre de la 1ª sesión estrictamente posterior a la emisión.
- **Salida:** cierre 2 sesiones después de la entrada. `r = exit/entry − 1` (decimal).
- **Etiqueta:** `y = 1` si `r > 0` ESTRICTO. Disponible solo tras el cierre de salida con
  barra FINAL (no provisional). Nunca se suma días naturales: se cuentan sesiones.
- `event_id` determinista: `SPY:YYYY-MM-DD:2D:v1`. Máximo una fila primaria por sesión.

## 4. Hipótesis y gates (decididos de antemano)

- Primaria: `d_t = (p4−y)² − (p5−y)²`. `delta_min = 0.005`. H0: E[d] ≤ 0.005.
- **Gate estadístico (intersección):** `lower95(Δ vs P4) > 0.005` **Y**
  `lower95(Δ vs B*) > 0.005`. B* = mejor no-ABM por Brier OOS de desarrollo,
  preseleccionado antes de T0.
- IC95 por **moving-block bootstrap** de sesiones consecutivas: bloques de 5 (sensibilidad
  10), 10.000 remuestreos, seed `20261124`. Una SPY por día. Las abstenciones SÍ entran en
  el Brier.
- **Gate económico:** paper trading USD 10.000 (ficticio), `p≥0.55` largo / `p≤0.45`
  corto, costes 5 bps (base) y 10 bps (estrés) por lado. P5 PnL neto >0, > P4 y > B* en
  base y estrés; drawdown de P5 no peor que P4 por más de 2 pp. Coste incremental del
  ABM imputado a P5.
- **Muestra:** ≥ 100 sesiones pareadas y cobertura ≥ 90%, o 6 meses, lo que ocurra
  primero. Sin optional stopping.

## 5. Regla de decisión (I.9.2)

| Resultado | Decisión |
|---|---|
| P5 supera TODOS los gates | candidato predictivo (sin capital real automático) |
| P4 funciona, P5 no mejora | **cerrar El Enjambre**; componentes reutilizables |
| Ambos fallan | cerrar |
| Muestra/operación insuficiente | inconcluso → **cerrar** por límite de recursos |
| Fuga temporal / integridad rota | experimento inválido → cerrar, documentar |

## 6. Integridad (correcciones de auditoría aplicadas)

- F01–F04 verificadas (tests de regresión en verde).
- **F05:** el ledger sella la probabilidad calibrada de P0–P5 (`SealedForecast.p_up`).
- **F06/F07:** evaluador nuevo (`evaluate.py`) con p selladas, diferencias pareadas
  verdaderas y agrupación por sesión/evento explícito (no por `fecha` vacía, no por la
  prevalencia del test). No se usa `calibration/evaluar_prospectivo.py` para el gate.
- **F08/F13:** la etiqueta solo madura tras el cierre de salida con barra FINAL.
- **F09:** identidad de evento determinista; duplicados ambiguos bloquean.
- **F12:** `riesgo_abm.spearman` corregido (scipy; `None` para constante).
- **F10/F14:** no se repite el barrido de población ni se amplía el alcance.

## 7. Qué NO autoriza este protocolo

No modificar producción, no contratar servicios, no gastar dinero, no enviar órdenes, no
arriesgar capital, no generar nuevas hipótesis ni mover los gates, no usar el banco de
shocks como evidencia confirmatoria. La activación la decide el fundador.
