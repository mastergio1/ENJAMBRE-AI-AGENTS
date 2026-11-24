# Hallazgo — Predictor calibrado: ventaja marginal solo en índice. Fase 5.

*Rubicón Lab · El Enjambre · 2026-11-24. Fase 5 del plan maestro v5 (predictor
probabilístico calibrado + abstención). Herramienta:
`engine/calibration/predictor_calibrado.py` (con tests). Toma el consenso A3,
lo calibra con Platt (entrenando solo con el pasado) y evalúa fuera de muestra.
Exploratorio (banco histórico). Sin IA.*

## Resultado

### ÍNDICE (test n=43)
| Métrica | Valor | Lectura |
|---|---:|---|
| Brier | 0.2238 | menor = mejor |
| Brier skill vs tasa base | **+0.045** | apenas mejor que la tasa base |
| ECE (calibración) | 0.087 | aceptable (0 = perfecto) |

**Abstención (acierto según cuánto se exige de confianza):**
| Cobertura | 100 % | 75 % | 50 % | 25 % |
|---|---:|---:|---:|---:|
| Acierto | 65.1 % | 68.8 % | 61.9 % | **70.0 %** |

En índice, exigir confianza **sí** mejora algo (70 % tomando solo el 25 % más
seguro, vs 65 % en cobertura total), pero es **frágil** (test n=43, y la curva no es
del todo monótona).

### TODOS los mercados (test n=174)
- Brier skill **−0.01** (NO mejor que la tasa base).
- Abstención **empeora** (100 %→47 %, 25 %→35 %): la "confianza" no predice acierto.

## Qué significa

1. **Hay una ventaja, pero marginal y solo en índice.** Calibrado, el consenso da un
   Brier skill +0.045 y una abstención selectiva que llega a ~70 % — un predictor
   mínimo *podría* operar solo cuando está muy convencido, a costa de actuar 1 de cada
   4 veces. Pero la muestra es chica y el resultado, inestable.
2. **Fuera de índice no hay nada que calibrar:** sin habilidad, y la confianza es
   anti-informativa.
3. Consistente con todo: el valor vive en índice, en una sola lectura de la noticia,
   y es frágil. La calibración y la abstención son las herramientas correctas para un
   producto honesto (reportar siempre cobertura), pero no crean señal donde no la hay.

## Caveat

Exploratorio, test n=43 (índice). El veredicto definitivo es **prospectivo** (Fase 6):
congelar este predictor y medirlo en casos nuevos sellados. La Fase 5 deja la
maquinaria (probabilidad calibrada + curva riesgo-cobertura) lista para ese examen.
