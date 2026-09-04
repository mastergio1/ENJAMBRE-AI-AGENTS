# Laboratorio de calibración (rama `feature/calibracion-70-porciento`)

Banco de pruebas **offline y aislado**. No toca el motor en producción, ni los
agentes reales, ni el frontend. Todo aquí es reversible con `git branch -D`.

## Qué hay

| Archivo | Qué hace |
|---|---|
| `data_loader.py` | Descarga SPY (yfinance) y guarda log-retornos de 5 min en `data/`. |
| `optimizer.py` | Modelo de agente de juguete (alpha/beta/gamma) + Optuna, maximizando R² contra el benchmark. |
| `../nlp_scorer.py` | FinBERT (torch) para puntuar titulares. **Offline**, no enchufado al motor. |

## Cómo correrlo

```bash
pip install optuna scikit-learn yfinance    # ligeras
# (nlp_scorer además necesita: pip install torch transformers  → varios GB)
python engine/calibration/data_loader.py    # baja el benchmark
python engine/calibration/optimizer.py      # calibra
cat engine/config_calibrada.json            # resultado
```

## Lo honesto (léelo antes de creerle a un número)

Esto se construyó tal como se pidió, pero como ingeniero te debo la verdad de
qué mide y qué no. **No es una excusa; es lo que evita venderte humo.**

1. **El modelo de juguete NO es el motor real.** `optimizer.py` corre un agente
   reducido de 3 parámetros. El Enjambre real es Mesa + libro de órdenes + 12
   tipos de agentes + líderes LLM (ver `CLAUDE.md` §3-§5). Calibrar el juguete
   **no calibra el motor**.

2. **El R² de aquí es curve-fitting, no correlación con el mercado.** Las
   "noticias" que mueven la simulación son **ruido aleatorio**, no lo que de
   verdad movió a SPY. Ajustar 3 parámetros para que salida-de-ruido se parezca
   a la ruta de SPY no valida nada. **Evidencia:** una corrida de 20 trials dio
   **R² = -38.9** (peor que predecir el promedio). El objetivo "70%" no aparece
   porque no puede: no hay señal, solo ruido.

3. **Mostrar "Correlación vs SPY: 72%" en la web sería un dato inventado.** El
   panel del bundle trae `0.72` hardcodeado. No lo implementé enchufado a la UI:
   poner una correlación falsa frente a usuarios de un producto financiero
   (marco CMF: informar, nunca engañar) no es algo que deba construir. Si quieres
   un panel, lo hago mostrando **estado interno real** (sentimiento agregado,
   precio sintético, driver), sin cifras fabricadas.

4. **FinBERT/torch NO va al motor.** `torch` + `transformers` son varios GB en
   RAM; el motor corre en Render con memoria ajustada → lo reventaría (OOM).
   Además, la interpretación de noticias por arquetipo (líderes LLM) es EL
   diferenciador del producto; reemplazarla por FinBERT es un cambio de rumbo,
   no una mejora. Por eso `nlp_scorer.py` queda como herramienta offline.

5. **`yfinance` es frágil aquí.** Usa su propio cliente HTTP que no pasa por el
   proxy del entorno → falla con SSLError. El motor ya trae un lector de Yahoo
   robusto (`engine/contenido/fuentes/yahoo.py`, vía httpx). El camino sólido es
   reusar ESE, no yfinance.

## El camino correcto para "más realismo"

El proyecto YA tiene el marco correcto: `engine/validation/` valida **hechos
estilizados** (colas gordas, clustering de volatilidad, asimetría de pánico —
`CLAUDE.md` §7). Calibrar de verdad = tunear los parámetros del **motor real**
para que reproduzca esos hechos, no para clavar la ruta de un índice. Si quieres,
el siguiente paso honesto es montar Optuna sobre esa validación real. Eso sí
mueve la aguja.
