# Hallazgo — Un solo LLM iguala al consenso de 110 cerebros (A2 ≈ A3)

*Rubicón Lab · El Enjambre · 2026-11-24. Fase 1 del plan maestro v5, comparación
secundaria crítica **M4 (A2) vs A3**. A2 se corrió con la clave del motor en Render
(Plan B: `POST /api/experimento/a2`), 641 señales sobre 664 titulares únicos.
Herramienta: `engine/calibration/a2_vs_a3.py` (de otra sesión) + `ablacion.py`.*

## La pregunta

¿Los ~110 cerebros LLM (9 arquetipos, el "reparto") aciertan la DIRECCIÓN mejor que
**un solo LLM neutral** leyendo el mismo titular? Si empatan, la diversidad de 110
no compra acierto y es gasto evitable (para la predicción).

## Resultado (cobertura COMÚN, pareado por evento)

| Mercado | A2 (1 LLM) | A3 (110) | pareado A2−A3 | IC 95% | veredicto |
|---|---:|---:|---:|:---:|---|
| **ÍNDICE** | 65.5 % | 66.4 % | −0.009 | [−0.061, 0.042] | **no distinguible** |
| TODOS | 53.8 % | 51.5 % | +0.023 | [−0.002, 0.051] | no distinguible (A2 algo arriba) |
| Acción | 50.7 % | 44.9 % | +0.058 | [−0.014, 0.128] | no distinguible (A2 arriba) |
| Cripto | 47.9 % | 48.4 % | −0.005 | [−0.028, 0.017] | no distinguible |

**Acuerdo de signo A2↔A3: ~92 % · correlación de señales: ~0.86.**

## Qué significa

1. **Un solo LLM neutral iguala al consenso de los 110 cerebros.** En índice la
   diferencia es −0.9 pts (el IC cruza 0); en el resto, el LLM solo es incluso un
   pelo mejor. **La diversidad de 110 cerebros NO mejora la dirección.** Leen la misma
   noticia y en el 92 % de los casos dicen lo mismo.
2. Es la **4ª evidencia consistente**: el ABM resta (A4<A3), el consenso apenas iguala
   "los índices suben" (A3≈A0), las features del ABM no bajan el Brier (M13≈M13-null),
   y ahora **un LLM ≈ el ensemble**. La señal predictiva, la poca que hay, la captura
   **una sola lectura LLM del titular**.

## Implicación de COSTO (lo que te ahorra)

- Las ~110 llamadas LLM por simulación **compran variedad de frases y los 9 arquetipos**
  — eso es valor de **producto y visualización** (las voces del hover, el enjambre), y
  se conserva.
- Pero para la **predicción de dirección**, **basta 1 llamada**. El reparto de 110
  cerebros es redundante para el número que predice. Un predictor mínimo usaría 1 LLM.

## Matiz (honestidad)

Exploratorio: banco histórico de shocks (sesgado por selección), n chico, IC que
cruzan 0. No es veredicto definitivo — eso es prospectivo. Pero la dirección es clara
y repetida. A2 se cacheó (`docs/datos-investigacion/a2_senales.json`) para repetir sin
costo. 23 titulares no dieron señal (fallo de parseo/API), sin efecto material.
