# Calibración v1 — rama `calibracion/impacto-no-lineal`

Plan original: *Mejoras de Calibración — El Enjambre* (31 ago 2026, Rubicón Lab).
Esta rama implementa la **Fase 1** sin tocar `main` ni la rama de trabajo actual
(`claude/m-d-file-6z1e63`).

## Qué es factible (y qué no)

| Pedido del plan | Veredicto | Por qué |
|---|---|---|
| Función de impacto no lineal | **Sí, adaptada** | El precio **no** se calcula con `k × señal`. Sale del libro de órdenes. La función amplifica la *señal* (tono + contagio + tamaño de orden del líder). Si fijáramos el % a mano, se romperían los 5 hechos estilizados. |
| 6 perillas en JSON, versionadas | **Sí** | `engine/config/perillas_calibracion.json`. Conjunto `baseline` = comportamiento actual (identidad). |
| Perfiles por mercado | **Sí** | Ya existían (`brains/mercado.py`). La hipótesis v1b añade overrides por tipo. Oro/petróleo siguen en pausa. |
| Loss oficial + ratio de fuerza | **Sí** | `corrector.evaluar_casos` / libreta. |
| Script de experimentos | **Sí, barato** | Shocks numéricos, **sin gastar la API**. La Loss vs mercado real sigue saliendo del backtest. |
| ≥ 70 % dirección y ratio ≥ 0.70 | **Meta, no garantía** | Hoy la dirección ronda 55-62 %. El cuello de botella real es **magnitud**. Esta fase ataca magnitud. El 70 % de dirección depende más de los cerebros (leer bien el titular) que de las perillas. |
| Grid search / Bayesian / XGBoost | **No en esta rama** | Fase 3. Caro y prematuro hasta tener baseline + una hipótesis medida. |
| 25-30 exámenes LLM de baseline | **No desde aquí** | Cada examen ~US$0.12 y ~110 llamadas. Se dispara con el workflow de calibración cuando Giorgio lo pida. |
| Más cerebros FOMO/Influencer | **Sí, opt-in** | En `hipotesis_v1b` pesan 1.35×. El techo sigue en ~110 llamadas. |
| Ruido por líder | **Sí, opt-in** | σ = 0.10 en la hipótesis. En baseline está apagado (tests reproducibles). |

## Cómo se usa (sin romper nada)

Por defecto **no cambia nada**. El conjunto activo es `baseline`.

```bash
cd engine
python -m contenido.experimento --set baseline --vs hipotesis_v1a --n 3
```

**v1a se midió el 3-sep-2026 y NO pasó** (ver [experimento-v1a.md](experimento-v1a.md)):
infla días normales ×2 y casi no mueve extremos. No activar `hipotesis_v1b`.
Sin `ENJAMBRE_PERILLAS`, el enjambre se comporta como hoy.

## Criterio de “esta hipótesis sirve”

En un hold-out (libreta, ≥ 80 casos con IA real):

- acierto de dirección ≥ 70 %
- ratio de fuerza medio ≥ 0.70
- ≥ 40 % de los casos dentro de ±30 % del movimiento real
- hechos estilizados siguen pasando (`pytest` tanda lenta)
- si mejora la fuerza pero rompe los hechos → se descarta

## Qué no se tocó

- `main`
- la rama de trabajo `claude/m-d-file-6z1e63`
- la mezcla de 10.000 agentes
- el libro de órdenes
- el presupuesto de ~110 cerebros
- oro/petróleo (siguen en pausa)

*Rubicón Lab · rama de calibración · 1 de septiembre de 2026*
