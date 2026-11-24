# Hallazgo — Más agentes NO mejoran la predicción (la empeoran). Fase 2.

*Rubicón Lab · El Enjambre · 2026-11-24. Fase 2 del plan maestro v5 (barrido de
población). Herramienta: `engine/calibration/barrido_poblacion.py` (con tests). Mide
el acierto direccional del ABM a distintos tamaños, con **capital agregado
constante** (control de la auditoría) y **señales de líder congeladas** (sin IA), en
índice (142 casos). Exploratorio (banco histórico). Sin IA.*

## Resultado (3 semillas — CONFIRMADO)

| Enjambre | Agentes | Semilla 1 | Semilla 2 | Semilla 3 | Media | Dispersión | Velocidad |
|---|---:|---:|---:|---:|---:|---|---:|
| Completo | 10.150 | 58.5 % | 57.0 % | 61.3 % | **58.9 %** | estrecha (57–61) | 6.6 s |
| 1/10 | 1.016 | 61.3 % | 39.4 % | 55.3 % | 52.0 % | **enorme (39–61)** | 0.37 s |
| 1/20 | 510 | 62.7 % | 54.9 % | 59.9 % | 59.2 % | ancha (55–63) | 0.16 s |

> ⚠️ **Corrección (integridad):** la primera versión de este hallazgo (semilla única)
> decía "a menos agentes, más acierto; el chico empata al consenso". **Era suerte de
> semilla.** Con 3 semillas, esa conclusión NO se sostiene.

## Qué significa (corregido)

1. **El tamaño NO mejora el acierto medio.** Todos los tamaños rondan ~53–59 %, y
   **todos por debajo del consenso A3 (62.7 %)**. Más agentes no crean señal direccional.
2. **El enjambre chico es MUCHO más ruidoso** corrida a corrida (a 1.016 agentes el
   acierto osciló 39 %↔61 % solo cambiando la semilla). El enjambre grande es **estable**
   (~57–61 %). Es esperable: más agentes = más promediado = menos varianza Monte Carlo.
3. Por tanto, el valor del enjambre grande es **ESTABILIDAD** (reproducibilidad), **no**
   acierto. Para predecir dirección, ningún tamaño le gana al consenso.
4. Sigue siendo consistente con las evidencias previas: el valor predictivo vive en el
   **consenso LLM**, no en el tamaño del ABM. "Más agentes = más impresionante" es
   cierto para el PRODUCTO/visual.

## Caveats (honestidad)

- 3 semillas es poco para estimar bien la varianza; la dirección (sin ganancia media,
  mucho ruido a N chico) es clara, pero los números exactos son indicativos.
- Exploratorio: banco histórico de shocks, n=142. Veredicto definitivo = prospectivo.
- Esto mide DIRECCIÓN. No prueba nada sobre si el ABM predice **riesgo/volatilidad**
  (Fase 4/H14), que es la pista que podría rescatar al motor.

## Implicación para el producto

El enjambre de 10.150 agentes es una **decisión de producto y visualización** (más
espectacular), **no** de predicción. Si algún día se arma un "producto predictor",
usaría el consenso (o 1 LLM) y, a lo sumo, un enjambre pequeño — barato y más fiel.
