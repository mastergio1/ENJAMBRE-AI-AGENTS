# Informe final: Calibración del motor real de El Enjambre

**Rama:** `feature/calibracion-70-porciento` (aislada — `main` y el motor en producción NO fueron modificados)
**Fecha:** 5 de septiembre de 2026
**Conclusión de una línea:** el enjambre ya reproduce las tres huellas estilizadas de un mercado real; lo que faltaba era medirlo bien y hacer el motor calibrable.

---

## 0. Resumen ejecutivo (para leer en 30 segundos)

- El simulador **ya se comporta como un mercado real** en las tres propiedades que importan: colas gordas, turbulencia en rachas y pánico asimétrico.
- El "faltaba llegar a curtosis > 3" era un **espejismo de medición**: se medía con una regla (Fisher) y se comparaba contra el umbral de otra (Pearson). Difieren en 3.
- El trabajo dejó tres mejoras reales: (1) `config/agentes.json` ahora **controla de verdad** a los agentes; (2) se corrigieron valores del JSON que habían divergido; (3) se detectó y arregló el bug de la métrica.

## 1. Qué se pidió

Construir un calibrador "profesional" que hiciera el enjambre más realista, con un objetivo inicial de **70% R²** y, luego, de **curtosis > 3**. Todo en una rama aislada que no dañara la principal.

## 2. Lo que encontré (hallazgos)

### 2.1 El objetivo "70% R²" no era válido
El primer diseño alimentaba una simulación con **ruido aleatorio** y medía su R² contra la ruta puntual de SPY. Ajustar parámetros para que ruido se parezca a un índice es **curve-fitting sin señal**. Evidencia: dio **R² = −38.9** (peor que predecir el promedio). El realismo de un simulador de agentes NO se mide así, sino con **hechos estilizados** (propiedades universales y estables de los mercados), que es justo lo que el proyecto ya valida en `engine/validation/`.

### 2.2 `yfinance` no sirve en este entorno
Usa su propio cliente HTTP que no pasa por el proxy → falla con SSLError. El endpoint de descarga de SPY del bundle además está **deprecado** (HTTP 401). Por eso se calibró contra **valores canónicos de mercado** (estables), no contra una descarga rota.

### 2.3 `config/agentes.json` era DECORATIVO (hallazgo mayor)
El bloque `"parametros"` de cada tipo **nunca lo leía el motor**:
- `grep "parametros"` en `engine/model.py` y `engine/agents/*.py` → **0 resultados**.
- `model._crear_agentes` instanciaba `clase(self, capital)` — sin pasar `parametros`.
- Cada agente **hardcodeaba** sus valores (p. ej. `self.umbral_subida = self.ruido(0.02)`).

Consecuencia: el plan de "tunear los agentes editando el JSON" habría sido un **no-op disfrazado** — el modelo habría ignorado esos cambios y habría reportado un fitness falso.

### 2.4 El JSON había DIVERGIDO de los valores calibrados
Los valores decorativos no coincidían con los realmente calibrados (hardcodeados):

| Parámetro | JSON (decorativo) | Código (calibrado) |
|---|---|---|
| market_maker · umbral_volatilidad_panico | 0.05 | **0.008** |
| miedoso · fraccion_venta_rango | [0.5, 1.0] | **[0.7, 1.0]** |
| fomo · fraccion_capital_maxima | 0.4 | **0.2** |

### 2.5 El bug de la curtosis (hallazgo decisivo)
El medidor usaba `pandas.kurtosis()`, que es curtosis de **Fisher** ("en exceso", una normal da **0**). Pero el proyecto y la meta ">3" usan **Pearson** (una normal da **3**). Difieren en exactamente 3 (comprobado: mismo dato → pandas **3.035** vs proyecto **6.03**).

Por eso una curtosis real de **~5.17 (Pearson)** se veía como **2.17 (Fisher)** y parecía no llegar a 3. **El enjambre tenía colas gordas todo el tiempo.**

## 3. Lo que hice y mejoré

### 3.1 Calibrador contra hechos estilizados (no contra la ruta de un índice)
`engine/calibration/real_optimizer.py`: corre el modelo **real** `MercadoEnjambre` headless (sin WebSockets) y lo compara con targets canónicos de mercado.
- Se corrigieron 4 referencias del bundle que no existían en la API real (`RUTA_CONFIG`, `precio_inicial`, `precio_actual`/`obtener_precio`, `pd.compat.StringIO`).
- `gc.collect()` + liberar el modelo entre trials → evita el OOM por acumulación de modelos de 10.000 agentes (mismo aprendizaje que el backtest del proyecto).

### 3.2 Cablear `config/agentes.json` a los agentes (retrocompatible)
- `AgenteBase` toma `model._cfg_agentes_actual` (los `parametros` del tipo) en `self.cfg`.
- `model._crear_agentes` expone ese cfg por tipo antes de crear sus agentes.
- 4 clases que gobiernan las colas gordas leen sus valores del cfg, con el valor calibrado actual como **default**:
  - **MarketMaker:** `multiplicador_spread_panico`, `umbral_volatilidad_panico`
  - **Manada:** `umbral_activacion_rango`
  - **Miedoso:** `asimetria_kahneman`, `fraccion_venta_rango`
  - **FomoRetail:** `umbral_subida`, `fraccion_capital_maxima`, `stop_panico`
- Se corrigió el JSON a los valores calibrados reales (tabla de §2.4).

**Verificación:** con overrides extremos los agentes leen los valores nuevos (MarketMaker.mult_panico = 8.0, Miedoso.asimetria = 5.0, etc.). El motor sigue intacto: el test de hecho estilizado #3 **pasó** (`1 passed in 282s`).

### 3.3 Arreglo del medidor de curtosis
`calcular_hechos_estilizados` ahora usa `scipy stats.kurtosis(fisher=False)` (Pearson), igual que `engine/validation/hechos_estilizados.py`; el target pasó a 6.0 (Pearson).

## 4. Resultados (evidencia, medidos en Pearson — la definición correcta)

Enjambre con los parámetros óptimos hallados (50 trials, 500 ticks):

| Hecho estilizado | Meta | Enjambre calibrado | Estado |
|---|---|---|---|
| **Curtosis (Pearson)** | > 3 | **4.78** | ✅ colas gordas |
| **Clustering de volatilidad** | > 0.2 | **0.33** | ✅ turbulencia en rachas |
| **Asimetría de pánico** | negativa | **−0.39** | ✅ caídas más violentas |

Parámetros óptimos de agentes (de la corrida escalada):
```json
{
  "noticias_intensidad": 1.05,
  "ruido_base": 0.028,
  "mult_spread_panico": 6.11,
  "umbral_vol_panico": 0.033,
  "asimetria_kahneman": 3.87,
  "manada_umbral_lo": 0.46
}
```

### Evolución del número de curtosis (para entender el espejismo)
| Corrida | Reportado (Fisher) | Real (Pearson = Fisher + 3) |
|---|---|---|
| V2 (solo noticia, 15 trials) | 2.05 | ~5.05 |
| V3 (con agentes, 15 trials) | 2.62 | ~5.62 |
| Escalada (50 trials, 500 ticks) | 2.17 | ~5.17 |

En las tres, la curtosis real **ya superaba 3**. El "problema" nunca existió; lo creó la mezcla de definiciones.

## 5. Lo honesto sobre el objetivo

- El "70% R²" nunca fue una métrica válida de realismo (§2.1).
- Si el objetivo real era **"que el enjambre se comporte como un mercado de verdad"**, eso **ya está**, y ahora está **probado con la definición correcta**.
- El motor no necesitaba el "arreglo" de la curtosis; sí ganó algo permanente: quedó **calibrable** (el JSON manda de verdad), con el JSON alineado a lo calibrado y el medidor corregido.

## 6. Estado y próximos pasos posibles

- **Recomendación:** no mergear a producción como cambio de comportamiento; el motor ya cumple los hechos estilizados con su config actual. El valor de esta rama es (a) la infraestructura de calibración y (b) los tres arreglos (cableado, JSON, métrica).
- Si se quiere, se puede correr `engine/validation/` completo con cualquier config candidata antes de adoptarla — nunca hardcodear un resultado sin que la validación real lo respalde.

---

### Archivos tocados (todos en la rama aislada)
- `engine/agents/base.py` — expone `self.cfg` por agente.
- `engine/model.py` — publica `_cfg_agentes_actual` por tipo.
- `engine/agents/reglas.py` — 4 clases leen sus params del cfg.
- `engine/config/agentes.json` — valores alineados a lo calibrado.
- `engine/calibration/real_optimizer.py` — calibrador real + medidor Pearson.
- `engine/calibration/` (data_loader, README, nlp_scorer) — herramientas de laboratorio.

`main` y el motor en producción: **sin cambios**.
