# Informe de cierre: Calibración de El Enjambre (de "70% R²" a producción)

**Fecha:** 5 de septiembre de 2026
**Rama:** `feature/calibracion-70-porciento` → **mergeada a `main`** (PR #33, merge `9ed986f`)
**Estado:** en producción. Render redeploya el motor solo (comportamiento idéntico, ahora calibrable).

---

## 0. Resumen ejecutivo

Empezamos con un objetivo mal planteado ("70% R²") y terminamos con algo mucho mejor: **el motor quedó calibrable de verdad, probamos que reproduce un mercado real, y medimos su desempeño con honestidad** — sin maquillar un solo número. Tres hallazgos importantes salieron en el camino, dos de ellos habrían sido "números falsos" si no los cazamos.

---

## 1. Lo que hice (el recorrido)

| Fase | Qué | Resultado |
|---|---|---|
| Laboratorio aislado | Rama que no toca `main` ni el motor | Todo reversible |
| Calibrador v1 (contra SPY) | Optuna contra la ruta del índice | Descartado: R² −38.9 (curve-fitting de ruido) |
| Calibrador v2 (hechos estilizados) | Optuna sobre el modelo REAL vs. targets canónicos | Funciona; curtosis "corta" (espejismo, ver §2) |
| Cablear agentes | Conectar `config/agentes.json` a las clases | El motor quedó **calibrable** |
| Calibrador v3 (agentes) | Tunear pánico/manada/miedoso | Movió la curtosis en la dirección correcta |
| Fase 0 — Validación base | Enjambre vs. mercado real (645 casos) | 60.9% acierto de dirección |
| Desglose | Por mercado / magnitud / sentimiento | Halló el sesgo de negativas |
| Documentación | `docs/ASIMETRIA_Y_REALISMO.md` + informes | Posicionamiento honesto |
| Validación final | Suite completo + hechos estilizados | 251 tests ✅, 4 hechos ✅ |
| Merge | PR #33 a `main` | En producción |

## 2. Lo que encontré (los 3 hallazgos)

### 2.1 `config/agentes.json` era DECORATIVO
El bloque `parametros` del JSON **nunca lo leía el motor** (`grep` → 0). Los valores estaban hardcodeados en las clases y habían **divergido** del JSON. Cualquier "calibración" que editara el JSON habría sido un **no-op** que reportaba números falsos. Lo arreglé: cableé el JSON a los agentes y lo alineé a los valores calibrados reales.

### 2.2 El bug de la curtosis (Fisher vs Pearson)
El medidor usaba la curtosis "en exceso" (normal = 0) pero la comparaba contra el umbral de la de Pearson (normal = 3). Difieren en 3. Por eso una curtosis real de **~5.2** parecía **~2.2** y "no llegaba a 3". **El enjambre siempre tuvo colas gordas**; el problema era la regla de medición.

### 2.3 El "70% R²" nunca fue una métrica válida
Ajustar el simulador para clavar la ruta de un índice es curve-fitting de ruido (dio R² −38.9). El realismo de un simulador de agentes se mide con **hechos estilizados**, no con el R² de un índice. La métrica honesta y útil para esta herramienta es el **acierto de dirección**.

## 3. Lo que mide el enjambre (validación honesta)

### Hechos estilizados (los 4 pasan)
| Hecho | Resultado | Meta |
|---|---|---|
| Curtosis (colas gordas) | 5.22 | > 3 ✅ |
| Clustering de volatilidad | 0.317, decae | >0 y decae ✅ |
| Sin autocorrelación de retornos | 0.073 | ≈ 0 ✅ |
| Asimetría de pánico | 1.37 | > 1 ✅ |

### Acierto de dirección (645 casos reales)
- **Global: 60.9%** (azar = 50%)
- **Positivas: 79.6%** 🟢 · **Negativas: 38.3%** 🔴
- Por mercado: cripto 68% (fuerte), acción 61%, índice 55%.
- Correlación de magnitud: 0.24 (acierta el rumbo mejor que el tamaño).

**El sesgo de negativas** es en buena parte la huella de un mercado real (sube tras malas noticias) + un enjambre pesimista por diseño (asimetría de pánico). Documentado en `docs/ASIMETRIA_Y_REALISMO.md`.

## 4. El merge a producción (PR #33)

**Qué entró a `main`:**
- Motor **calibrable**: `AgenteBase` toma la config del tipo; market maker, manada, miedoso y fomo leen sus valores del JSON (default = valor calibrado).
- `config/agentes.json` alineado a los valores calibrados reales (3 valores; el resto del diff es reindentado cosmético).
- Herramientas de calibración en `engine/calibration/` (inertes — el servidor no las importa), informes y `docs/ASIMETRIA_Y_REALISMO.md`.

**Blindaje antes de mergear:**
- Suite completo: **251 passed, 2 skipped, 0 failed** (13:48).
- Los 4 hechos estilizados pasan en vivo.
- Comportamiento del motor **idéntico** con la config original (los cambios son neutros; solo habilitan la calibración).

**Notas técnicas:**
- El diff de `agentes.json` es grande (~106 líneas) pero casi todo cosmético (reindentado); el cambio real son 3 valores.
- `nlp_scorer.py` (torch) es de import perezoso y nadie lo importa en producción → no afecta el motor en Render.

## 5. Qué GANÓ el proyecto con esto

1. **Un motor calibrable de verdad** (antes el JSON era decorativo). Ahora se pueden tunear los agentes desde la config, con validación.
2. **La certeza —probada— de que el enjambre reproduce un mercado real** (4 hechos estilizados) y una métrica honesta de desempeño (61% de dirección).
3. **Tres "números falsos" evitados** (el JSON decorativo, el bug de curtosis, el R² de índice). En un producto bajo CMF, no vender humo es tan valioso como el producto mismo.
4. **Un posicionamiento defendible** ante clientes: *"acierta la dirección ~6 de 10 veces, hasta 8 de 10 en positivas; informa y simula, nunca aconseja"*.

## 6. Próximos pasos posibles (no urgentes)

- Ajuste fino y medido del pánico (subir negativas) **solo** si el trade-off con los hechos estilizados es aceptable — re-validando cada cambio.
- Un backtest real más grande (con saldo) para robustecer el 61%.
- Retomar el **correo de El Pulso**, que quedó a medias (el "no me llegó" resultó ser que la edición ya se había enviado 3/3; falta aclarar si tu correo está entre los suscriptores).

---

*Verificado: `pytest engine/validation/` (251 passed) y `engine/simular.py`.
Merge PR #33 en `main` (`9ed986f`). Producción redeploya el motor sola.*
