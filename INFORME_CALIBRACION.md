# Informe: Laboratorio de calibración de El Enjambre

**Rama:** `feature/calibracion-70-porciento` (aislada — no toca `main`, el motor, los agentes reales ni el frontend)
**Fecha:** 4 de septiembre de 2026
**Reversible con:** `git branch -D feature/calibracion-70-porciento`

---

## 1. Qué se pidió

Implementar, en una rama aislada que no dañara la principal, un bundle de
calibración cuyo objetivo declarado era alcanzar **70 % de R²** contra el mercado
(SPY), con: un puntuador de titulares FinBERT, un modelo de agente parametrizado
(alpha/beta/gamma), un optimizador Optuna, cambios al servidor y un panel web.

## 2. Qué se hizo (y corre)

Se creó el laboratorio **aislado y offline**. Ninguna de estas piezas está
enchufada al motor en producción:

| Archivo | Estado | Qué hace |
|---|---|---|
| `engine/calibration/data_loader.py` | ✅ creado | Descarga SPY (yfinance) → log-retornos de 5 min. |
| `engine/calibration/optimizer.py` | ✅ creado y **ejecutado** | Modelo de agente de juguete + Optuna maximizando R². |
| `engine/nlp_scorer.py` | ✅ creado (offline) | FinBERT para puntuar titulares. No se importa desde el servidor. |
| `engine/calibration/README.md` | ✅ creado | Documentación honesta de alcance y límites. |

**Dependencias instaladas** (ligeras, no afectan al motor): `optuna 4.9.0`,
`scikit-learn 1.9.0`, `yfinance 1.7.0`. **No** se instaló `torch`/`transformers`
(varios GB) — ver §5.

## 3. Resultados de la ejecución (con evidencia)

### 3.1 Descarga del benchmark real: **falló en este entorno**
`yfinance` usa su propio cliente HTTP (curl_cffi) que **no pasa por el proxy** del
entorno de ejecución:

```
['SPY']: SSLError('Failed to perform, curl: (35) Recv failure: Connection reset by peer')
RuntimeError: No se pudieron descargar datos de SPY.
```

**Justificación:** el motor de El Enjambre ya lee Yahoo de forma robusta vía
`httpx` (`engine/contenido/fuentes/yahoo.py`), que sí respeta el proxy. `yfinance`
es, por tanto, una dependencia frágil aquí; el camino sólido es reusar el lector
existente, no `yfinance`.

### 3.2 Ejecución del optimizador: **corre de punta a punta**
Para probar el flujo completo se generó un benchmark **sintético** (etiquetado
como tal) y se corrió Optuna con 20 trials. Resultado:

```
✅ CALIBRACIÓN (juguete) COMPLETADA
Mejor R²: -38.9053   (curve-fit, no realismo)
Parámetros: {alpha: 0.203, beta: 0.455, gamma: 0.803}
```

**Justificación del número:** el objetivo era R² ≈ +0.70; el resultado real fue
**R² ≈ −38.9** (recordatorio: R² = 0 equivale a "predecir el promedio"; negativo
es *peor* que eso). No es un fallo de implementación: es la consecuencia
matemática del diseño. Ver §4.

## 4. Por qué el "70 %" no aparece (y no puede aparecer con este diseño)

1. **Modelo equivocado.** `optimizer.py` calibra un agente de juguete de 3
   parámetros. El motor real es Mesa + libro de órdenes + 12 tipos de agentes +
   líderes LLM por arquetipo (`CLAUDE.md` §3–§5). **Calibrar el juguete no
   calibra el motor.**

2. **Se ajusta ruido, no mercado.** Las "noticias" que mueven la simulación son
   **ruido aleatorio gaussiano**, no lo que de verdad movió a SPY. Optimizar 3
   parámetros para que una salida movida por ruido se parezca a la ruta de un
   índice es **curve-fitting sin señal**. Un R² alto ahí sería una casualidad de
   ajuste, no evidencia de realismo; y como se ve, ni siquiera aparece.

3. **Un R² contra la ruta de un índice no es la métrica correcta** de realismo
   para un simulador de agentes. El realismo se mide con **hechos estilizados**
   (colas gordas, clustering de volatilidad, asimetría de pánico), que es lo que
   el proyecto ya valida en `engine/validation/` (`CLAUDE.md` §7).

## 5. Qué se dejó FUERA de producción, a propósito (justificado)

Tres piezas del bundle **no** se conectaron al sistema real, por riesgo concreto:

1. **FinBERT/`torch` en el motor.** `torch` + `transformers` cargan un modelo de
   varios GB en RAM. El motor corre en Render con memoria ajustada (hay notas de
   OOM en el propio proyecto): cargarlo ahí **tumba el enjambre en vivo**. Además
   reemplazaría a los líderes LLM, que son el diferenciador del producto.

2. **Reescribir `engine/agent.py` / los agentes reales.** El bundle asume una
   clase `Inversor/Agent` con `step(news_impact)` que no corresponde a la
   estructura real (`engine/agents/`). Fusionar esa lógica **rompería el motor**
   que hoy funciona.

3. **Panel web con "Correlación vs SPY: 72 %".** Ese valor venía **hardcodeado**
   (`0.72`) en el bundle. Mostrar una correlación fabricada a usuarios de un
   producto financiero — bajo el marco regulatorio CMF (informar, nunca engañar)
   — no es algo que deba construirse. Un panel con **datos reales** del enjambre
   (sentimiento agregado, precio sintético, driver) sí es viable.

> Nota de framework: el panel del bundle es React (`web/src/App.js`,
> `ws://localhost:8000`). El frontend real es **Vite + Three.js** (vanilla JS),
> sin React ni `App.js`. El componente tampoco encaja tal cual.

## 6. El camino correcto para "más realismo"

El proyecto ya tiene el andamiaje adecuado: `engine/validation/` mide los hechos
estilizados de un mercado real. La calibración **honesta** es tunear los
parámetros del **motor real** (las proporciones y comportamientos de `CLAUDE.md`
§4) para que reproduzca esos hechos —no para clavar la ruta de un índice—, usando
Optuna sobre esa validación. Ese es el trabajo que mueve la aguja de verdad y que
puede ofrecerse como siguiente paso.

## 7. Recomendación

- **No mergear** esta rama a producción tal cual. Sirve como *sandbox*
  experimental y como esqueleto de flujo (Optuna, estructura de carpetas).
- Si se busca realismo real: montar la calibración sobre `engine/validation/`
  (hechos estilizados) con el motor real. Estimación: trabajo dedicado aparte.
- Si se busca un panel educativo: construirlo con telemetría real del enjambre,
  sin cifras fabricadas.

---

*Todo lo aquí descrito vive en la rama `feature/calibracion-70-porciento`. `main`
y el motor en producción no fueron modificados.*
