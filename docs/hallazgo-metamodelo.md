# Hallazgo — M13 vs M13-null: las salidas del ABM no agregan valor (exploratorio)

*Rubicón Lab · El Enjambre · 2026-11-24. Fase 1/5 del plan maestro v5. Herramienta:
`engine/calibration/metamodelo.py` (con tests). La comparación PRIMARIA del plan,
corrida offline sobre el banco histórico. Sin IA.*

## Qué se probó

Un metamodelo (logística L2, ajuste y estandarización SOLO con el pasado, evaluación
en el futuro, diferencia **pareada por evento** con cluster bootstrap):

- **M13** = logística(consenso de líderes + `direccion_pct` ABM + `volatilidad_pct` ABM)
- **M13-null** = logística(consenso de líderes) — idéntico, sin las features del ABM

`d = (Brier_sinABM) − (Brier_conABM)`; media>0 favorece al ABM.

## Resultado

| Mercado | Brier M13 (con ABM) | Brier M13-null | media(d) | IC95 | veredicto |
|---|---:|---:|---:|:---:|---|
| **ÍNDICE** | 0.2253 | 0.2238 | **−0.0014** | [−0.0133, 0.0099] | no concluyente (ligeramente peor) |
| TODOS | 0.256 | 0.253 | −0.003 | [−0.0111, 0.0045] | no concluyente (ligeramente peor) |

**Las salidas del ABM no mejoran la predicción sobre el consenso; si acaso, la
empeoran un poco (dentro del ruido).** Tercera pieza independiente que apunta a lo
mismo (ablación A4<A3, gate pareado −0.063 significativo, y ahora el metamodelo): el
valor predictivo vive en el consenso LLM, no en el motor de agentes.

## Matiz importante (qué NO cierra esto)

- Solo se probaron las **dos salidas escalares** del ABM (`direccion_pct`,
  `volatilidad_pct`). Las features **ricas** que propone la auditoría (order-flow
  imbalance, índice de manada, dispersión del consenso, forma de la trayectoria,
  desacuerdo líder-seguidor, presión de liquidez, velocidad del consenso) **no están
  en los datos actuales**: requieren **re-correr simulaciones** exportando esas
  variables por corrida. Ese es un experimento futuro (H2 de la auditoría).
- Es **EXPLORATORIO**: banco histórico de shocks (sesgado por selección), n chico. El
  veredicto definitivo es **prospectivo**.

## Implicación

Antes de invertir en extraer features ricas del ABM, el orden correcto es: (1) cerrar
**M4 vs A3** (¿un LLM iguala a los 110? — necesita la clave), porque si el consenso ni
siquiera supera a un LLM solo, el ABM es secundario; y (2) construir el **banco
cronológico de flujo** (F05) para que todo esto se mida sin sesgo de selección.
