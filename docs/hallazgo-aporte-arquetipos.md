# Hallazgo — Qué arquetipos de verdad predicen (Fase 2, groundwork)

*Rubicón Lab · El Enjambre · 2026-11-17. Mide el acierto direccional de CADA una
de las 9 voces por separado, sin fuga, sobre los 617 casos históricos (597 con
resultado sin fuga re-medido). Es la materia prima de la "confianza efectiva por
arquetipo" (Fase 2). Herramienta: `engine/calibration/acierto_por_arquetipo.py`
(con tests). Sin IA nueva: reutiliza las señales guardadas.*

## Resultado — ÍNDICE, acierto direccional de la señal (sin fuga)

| Arquetipo | Acierto (todas) | n | Acierto \|señal\|≥0.3 | n |
|---|---:|---:|---:|---:|
| **macro_trader** | **64.2 %** | 106 | 63.4 % | 41 |
| **influencer_optimista** | **64.5 %** | 141 | 65.2 % | 138 |
| **fomo_evangelista** | **63.3 %** | 139 | 63.3 % | 139 |
| **institucional_frio** | **61.3 %** | 124 | **78.6 %** | 28 |
| contrarian_sabio | 57.6 % | 125 | 48.4 % | 62 |
| quant_esceptico | 53.5 % | 129 | 41.2 % | 34 |
| **doomer** | **35.5 %** | 141 | 41.5 % | 94 |
| value_paciente | 63.6 % | 11 | (n=1) | 1 |
| doomer_selectivo | — | 0 | — | 0 |

## Lo que revela (accionable)

1. **El doomer perpetuo HACE DAÑO a la dirección: 35.5 %** — peor que una moneda.
   Es lógico: siempre dice "baja", así que acierta solo cuando el mercado cae. Es
   un lastre direccional. **Candidato #1 a bajarle el peso en el consenso** (o
   usarlo solo como voz de "riesgo de cola", no de dirección).

2. **Los contrarians (quant_esceptico 53.5 %, contrarian_sabio 57.6 %) son flojos
   en dirección** — y en señal fuerte caen por debajo del azar (41 % y 48 %). Esto
   **valida con datos** la decisión que ya tomamos de bajarles el peso en
   `senal_media_ponderada`. No era arbitrario: apuestan a la reversión, no a la
   dirección.

3. **Los mejores predictores direccionales de índice son macro_trader (64 %),
   influencer_optimista (64.5 %), fomo (63 %) e institucional_frio (61 %, y 78.6 %
   cuando tiene convicción fuerte).** Que el **macro_trader** brille en índice es
   una señal de coherencia: las noticias macro mueven los índices, y es la voz que
   lee en clave macro.

4. **value_paciente casi no opina** (n=11, por diseño "80 % ruido") y
   **doomer_selectivo no estaba activo** cuando se cosecharon estos casos (es el 9º
   arquetipo, añadido después) → no hay datos suyos aquí todavía.

## Por qué importa para la Fase 2

Esto es exactamente la base de la **confianza efectiva** (declarada + histórica):
hoy el consenso pondera por la confianza que *declara* cada LLM, no por su acierto
*real*. Estos números dicen que una ponderación por acierto histórico **subiría**
a macro_trader/institucional y **bajaría** al doomer — lo que casi seguro mejora
el agregado. La hipótesis a probar en la Fase 2: reponderar por acierto histórico
mejora el Brier y el acierto direccional fuera de muestra.

## Salvedades honestas

- Mismas de la Fase 0: en muestra, ~4 instrumentos de índice, posible
  contaminación por memoria (aunque el orden RELATIVO entre arquetipos —doomer
  malo, macro bueno— es robusto frente a eso).
- `doomer_selectivo` necesita datos propios (una cosecha nueva con él activo).
- El acierto direccional crudo no es lo único que importa: un arquetipo "malo"
  en dirección puede aportar en magnitud o en calibración. Por eso es *insumo*
  de la Fase 2, no una sentencia para eliminar voces.
