# Calibración v1 — rama `calibracion/impacto-no-lineal`

Plan original: *Mejoras de Calibración — El Enjambre* (31 ago 2026, Rubicón Lab).
Consejo unificado: [plan-calibracion-consejo.md](plan-calibracion-consejo.md).
Esta rama no toca `main` ni `claude/m-d-file-6z1e63`.

## Estado

| Hipótesis | Qué es | Veredicto |
|---|---|---|
| baseline | identidad (el enjambre de hoy) | producción |
| v1a | `impacto_base=2` + `umbral_panico=0.45` | **no pasa** (infla días chicos ×2) |
| v1b | v1a + cocina | **no medir** |
| v1c | `umbral_consenso=0.25` (zona muerta ambiente) | implementada, **apagada** |

## Qué hay ahora que no había

- Loss **simétrica**: pasarse 4× ya no cuenta como fuerza perfecta.
- Intervalo de Wilson en la libreta. 8/12 no es 70 %.
- `listo_produccion` exige **≥ 80 casos** hold-out.
- Taxonomía léxica del titular (tipo × priced-in/sorpresa × tipo de error).
- `zona_muerta` sobre el tono ambiente. Los líderes siguen hablando.

## Cómo se usa (sin romper nada)

Por defecto **no cambia nada**. El conjunto activo es `baseline`.

```bash
cd engine
python -m contenido.experimento --set baseline --vs hipotesis_v1c --n 1
```

Sin `ENJAMBRE_PERILLAS`, el enjambre se comporta como hoy.

## Criterio de “esta hipótesis sirve”

En un hold-out (libreta, ≥ 80 casos con IA real):

- acierto de dirección ≥ 70 % (y el piso de Wilson no da vergüenza)
- ratio de fuerza **simétrico** ≥ 0.70
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
- `conjunto_activo` (sigue `baseline`)

*Rubicón Lab · rama de calibración · 3 de septiembre de 2026*
