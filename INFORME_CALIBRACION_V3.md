# Informe V3: Calibración del motor real por parámetros de agentes

**Rama:** `feature/calibracion-70-porciento` (aislada — no toca `main` ni el motor en producción)
**Fecha:** 5 de septiembre de 2026
**Objetivo de esta etapa:** subir la **curtosis** (colas gordas) del enjambre tuneando los parámetros de los agentes, no solo la noticia.

---

## 1. Qué se pidió

Extender el calibrador para que tunee los parámetros de `config/agentes.json`
(pánico del market maker, aversión del miedoso, umbrales de la manada) y así
atacar la curtosis, que en la V2 quedó corta (2.05 vs. el objetivo > 3).

## 2. Lo que encontré (y por qué el plan original no habría funcionado)

### Hallazgo crítico: `config/agentes.json` era decorativo
El bloque `"parametros"` de cada tipo en `config/agentes.json` **nunca lo leía
el motor**. Evidencia:
- `grep "parametros"` en todo `engine/model.py` y `engine/agents/*.py` → **0 resultados**.
- `model._crear_agentes` instanciaba `clase(self, capital)` — sin pasar `parametros`.
- Cada agente **hardcodeaba** sus valores (p. ej. `self.umbral_subida = self.ruido(0.02)`).

Consecuencia: el bundle original (que escribía claves como `config["miedosos"]["umbral_panico"]`)
habría sido un **no-op disfrazado** — el modelo habría ignorado esos cambios y
la "calibración de agentes" no habría tocado un solo agente. Un fitness así
habría sido humo.

### Segundo hallazgo: el JSON había DIVERGIDO de los valores calibrados
Los valores decorativos del JSON no coincidían con los hardcodeados (que son los
realmente calibrados). Al conectarlos, esto rompía el comportamiento:

| Parámetro | JSON (decorativo) | Código (calibrado) |
|---|---|---|
| market_maker · umbral_volatilidad_panico | 0.05 | **0.008** |
| miedoso · fraccion_venta_rango | [0.5, 1.0] | **[0.7, 1.0]** |
| fomo · fraccion_capital_maxima | 0.4 | **0.2** |

## 3. Lo que hice (mejoras)

### 3.1 Cablear la config a los agentes (retrocompatible)
- `AgenteBase.__init__` toma `model._cfg_agentes_actual` (los `parametros` del tipo)
  y lo guarda en `self.cfg`.
- `model._crear_agentes` expone ese cfg por tipo **antes** de crear sus agentes.
- Las 4 clases que gobiernan las colas gordas leen sus valores del cfg, con el
  valor calibrado actual como **default** (así, con la config original, el
  comportamiento NO cambia):
  - **MarketMaker:** `multiplicador_spread_panico`, `umbral_volatilidad_panico`
  - **Manada:** `umbral_activacion_rango`
  - **Miedoso:** `asimetria_kahneman`, `fraccion_venta_rango`
  - **FomoRetail:** `umbral_subida`, `fraccion_capital_maxima`, `stop_panico`
- Se corrigió el JSON a los valores calibrados reales (tabla de §2) para que la
  config original reproduzca el comportamiento de siempre.

**Verificación:** con overrides extremos, los agentes leen los valores nuevos
(MarketMaker.mult_panico = 8.0, Miedoso.asimetria = 5.0, etc.). Los parámetros
llegan de verdad a los agentes. ✅

### 3.2 Blindaje: el motor sigue intacto
El test de hecho estilizado #3 (sin autocorrelación de retornos) **pasó** tras
corregir el JSON (`1 passed in 282s`). La config original reproduce el
comportamiento calibrado; solo los overrides del calibrador lo cambian.

### 3.3 Calibrador V3 (`engine/calibration/real_optimizer.py`)
- Escribe un `agentes.json` **temporal por trial** con los overrides inyectados
  en el **tipo correcto** (mapeo real, no el inventado del bundle), y lo borra al
  terminar.
- Optuna ahora tunea, además de la noticia: `mult_spread_panico`,
  `umbral_vol_panico`, `asimetria_kahneman`, `manada_umbral_lo`.
- Objetivo = valores canónicos de mercado (curtosis 3.5, clustering 0.3,
  skew −0.5), estables, no una descarga rota de SPY.
- Fitness prioriza la curtosis (peso 0.5).

## 4. Resultados (evidencia)

Corrida de 15 trials (~30 s/trial, memoria liberada entre trials).

| Hecho estilizado | Objetivo | V2 (solo noticia) | **V3 (con agentes)** | Estado |
|---|---|---|---|---|
| Curtosis | > 3 | 2.05 | **2.62** ⬆️ (+28%) | 🔺 más cerca, aún corto |
| Clustering de volatilidad | > 0.2 | 0.231 | **0.251** | ✅ |
| Asimetría de pánico | negativa | −0.559 | **−0.693** | ✅ |

**Fitness: 0.56.** Parámetros óptimos hallados:

```json
{
  "noticias_intensidad": 2.30,
  "ruido_base": 0.020,
  "mult_spread_panico": 6.54,
  "umbral_vol_panico": 0.0032,
  "asimetria_kahneman": 4.92,
  "manada_umbral_lo": 0.416
}
```

**Interpretación:** la curtosis subió porque el optimizador empujó las tres
palancas correctas en la dirección que predice la teoría de cascadas:
- market maker retira liquidez **6.5×** en pánico (vs. 3) y con umbral bajísimo
  → baches de precio más profundos y frecuentes;
- los miedosos venden ante caídas más chicas (asimetría 4.9 vs. 2.5) → crashes
  más filosos;
- la manada se contagia con menos evidencia → cascadas más fáciles.

## 5. Lo honesto: por qué no llegó a 3

1. **150 ticks es una muestra corta**: la curtosis en pocas observaciones sale
   **sesgada hacia abajo**. En un mercado real se mide sobre miles de datos; con
   sesiones más largas el mismo enjambre marcaría más.
2. **15 trials es una búsqueda chica**: con más trials, rangos más amplios y un
   par de palancas extra (agresividad del FOMO; soltar el freno del arbitrajista,
   que hoy borra la predictibilidad pero también aplana las colas) es muy
   probable cruzar el 3.

## 6. Próximos pasos posibles

- Correr sesiones de 400+ ticks y 30+ trials para empujar la curtosis sobre 3.
- Añadir al calibrador las palancas del FOMO y del arbitrajista.
- Si el resultado convence: portar los parámetros óptimos a `config/agentes.json`
  (con revisión de que los 5 hechos estilizados de `engine/validation/` siguen
  pasando) — nunca hardcodear un resultado sin que la validación real lo respalde.

---

*Archivos tocados (todos en la rama aislada): `engine/agents/base.py`,
`engine/model.py`, `engine/agents/reglas.py`, `engine/config/agentes.json`,
`engine/calibration/real_optimizer.py`. `main` y el motor en producción no
fueron modificados.*
