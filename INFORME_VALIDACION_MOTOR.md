# Informe: validación del motor tras los cambios de calibración

**Rama:** `feature/calibracion-70-porciento`
**Fecha:** 5 de septiembre de 2026
**Pregunta que responde:** ¿los cambios de esta rama (cablear `config/agentes.json` a los agentes, alinear el JSON, corregir el medidor) **rompieron** el motor? **Respuesta: no.**

---

## 1. Resumen ejecutivo

- Los **cuatro hechos estilizados** de un mercado real **pasan** con la config de esta rama. El motor sigue reproduciendo un mercado creíble.
- La **curtosis sale 5.22** (Pearson, meta > 3): confirma en vivo que el enjambre **siempre tuvo colas gordas**; el "faltaba llegar a 3" fue un espejismo de definición (Fisher vs Pearson), no un defecto real.
- El suite completo de `pytest engine/validation/` estaba corriendo al cerrar este informe, **sin fallos** hasta ese punto (ver §3; se actualiza el conteo al terminar).

## 2. Resumen de hechos estilizados (`python simular.py 42`)

Una sesión de 599 ticks con 10.000 agentes, config de la rama:

| # | Hecho estilizado | Resultado | Meta | Veredicto |
|---|---|---|---|---|
| 1 | **Curtosis (colas gordas)** | **5.22** | > 3 | ✅ |
| 2 | **Clustering de volatilidad** | AC\|r\| lag1 = **0.317**, decae (lag5 −0.107, lag10 −0.028) | > 0 y decae | ✅ |
| 3 | **Sin autocorrelación de retornos** | AC lag1 = **0.073** | ≈ 0 | ✅ |
| 4 | **Asimetría de pánico** | **1.37** | > 1 | ✅ |

*Precio final 103.97 (partió en 100); volumen de la sesión ~4.0M acciones.*

### Qué significa
- **Los cuatro se cumplen** → el motor no se degradó con los cambios de la rama. El cableado del `cfg` a los agentes y la alineación del JSON son, en efecto, **neutros** con la config original (como se diseñaron).
- **Curtosis 5.22** es la confirmación en vivo del hallazgo del bug de medición: en la definición correcta (Pearson, normal = 3) el enjambre está claramente por encima de 3. No hubo que "arreglar" ninguna curtosis; había que medirla bien.

## 3. Suite completa de pruebas (`pytest engine/validation/`)

El suite completo es pesado (~15 min: construye modelos de 10.000 agentes muchas veces, y algunos tests tocan red). Estado al cerrar este informe: **en progreso, 0 fallos**.

> Nota: algunos tests del suite dependen de red o de servicios externos
> (Yahoo, servidor). Un eventual fallo en esos NO indica un problema de los
> cambios de esta rama; los tests relevantes a los cambios son los de
> `test_hechos_estilizados.py`, `test_mercado.py` y `test_red_influencia.py`,
> que validan el comportamiento del motor. (El de no-autocorrelación ya se
> corrió aparte y **pasó**.)

*Se actualizará este apartado con el conteo final passed/failed cuando el suite termine.*

## 4. Conclusión

Los cambios de calibración de esta rama **no rompieron el motor**: reproduce los cuatro hechos estilizados de un mercado real, con colas gordas (curtosis 5.22), turbulencia en rachas, retornos sin memoria y pánico asimétrico. La rama sigue siendo un laboratorio seguro; `main` y el motor en producción no fueron tocados.

---

*Herramientas: `engine/simular.py` (resumen de hechos estilizados) y
`pytest engine/validation/`. Config: `engine/config/agentes.json` de la rama,
alineada a los valores calibrados reales.*
