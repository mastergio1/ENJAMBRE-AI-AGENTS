# Plan del consejo — calibración hacia el 70 %

Fecha: 3 de septiembre de 2026  
Rama: `calibracion/impacto-no-lineal` (no toca `main`)  
Para: Giorgio, Rubicón Lab  
Costo de lo implementado hoy: **US$0** (sin API)

Cuatro roles miraron el mismo problema. Este archivo unifica lo que
encontraron y el plan que se está ejecutando. Lenguaje llano a propósito.

---

## 1. El diagnóstico, en una frase

**El parlante ya grita fuerte. El micrófono no distingue un susurro de un grito.**

- El **parlante** es el libro de órdenes (10.000 agentes). En un crash
  numérico ya mueve ~11 %. Subirle el volumen (hipótesis v1a) no lo hace
  gritar más: infla los días chicos y los extremos se quedan iguales.
- El **micrófono** son los ~110 cerebros que leen el titular. Ahí están
  los fallos de verdad: Fed en pausa (se esperaba, el enjambre se desplomó),
  Nvidia (mal el signo), aranceles 2025 (casi bien).

v1a se midió y **no pasa**. No se activa v1b (es v1a con más perillas).

---

## 2. Qué trajo cada agente

### Investigación (herramientas, X, papers)

No existe un calibrador “enchufar y listo” para un ABM + LLM como El Enjambre.

| Herramienta | ¿Sirve? | Por qué |
|---|---|---|
| PyABC / SBI / ABC | **No** | Quieren 10⁴–10⁵ simulaciones. Cada sim son 10.000 agentes. Impagable. |
| MSM / method of simulated moments | **No ahora** | Misma razón: demasiadas corridas. |
| DSPy / GEPA (optimizar prompts) | **Más adelante** | Ataca el micrófono. Gasta API. Después de tener medición honesta. |
| FinBERT u otro clasificador de noticias | **Diagnóstico** | Para etiquetar sorpresa vs. “ya estaba en el precio”. No mueve el precio. |
| TradingAgents y similares | **Otro producto** | Agentes que *operan*. El Enjambre *simula masas*. |
| Event-study CAR (abnormal returns) | **Sí, como meta** | Medir el enjambre contra el movimiento *anormal* del evento, no contra el ruido del día. |
| EDSL / paneles sintéticos | **Idea** | Caro. No prioridad. |

Nada de esto se instala hoy. El atajo útil y gratis es **taxonomía léxica**
(tipo de noticia + ¿era sorpresa?) y **dejar de mentirnos con la Loss**.

### Cuantitativo (finanzas)

Nueve palancas. El programador vetó las que rompen el precio emergente.

1. **Zona muerta / James-Stein en el consenso ambiente** — anti-v1a. Los
   líderes siguen hablando; el “tono de la prensa” no inunda el mercado
   cuando el titular es tibio. **Esto sí se implementa (apagado por defecto).**
2. **Taxonomía de noticias** (macro / resultados / geopolítica ×
   priced-in / sorpresa / ambiguo). Sin taxonomía, 12 casos mezclados
   no enseñan nada. **Léxico, hoy.**
3. **Loss simétrica** — si el enjambre hace 4× de más, eso es error, no
   un 10. **Hoy.**
4. **CAR / retorno anormal** — meta de medición, no de esta sesión.
5. **Campo “sorpresa” en el prompt de los cerebros** — una línea.
   Gasta API. Siguiente sesión con exámenes.
6. **MoE (un cerebro distinto según tipo de noticia)** — después de
   tener datos por casilla.
7. **β de valoración solo en resultados de acciones** — después.
8. **Tamaño de orden convexo en líderes** — toca la mezcla. Peligroso.
9. **Kyle-λ (fijar impacto ∝ volumen)** — **VETO**. El precio tiene que
   seguir saliendo del libro. Si lo fijamos a mano, se rompen los 5
   hechos estilizados.

### Ciencia de datos

- **n = 12 es teatro.** 8 aciertos de 12 = 67 %, pero el intervalo de
  Wilson es **[39 %, 86 %]**. Cabe tanto “somos un dado” como “ya está”.
  Para afirmar 70 % con la boca chica hacen falta ~**80 casos hold-out**
  con IA real (no el respaldo léxico).
- La Loss **premiaba el exceso**: si el enjambre se pasaba 5×, el ratio
  se capeaba a 1.5 y el error de fuerza quedaba en 0 (perfecto). Mentira.
- `listo_produccion` no puede prenderse con 12 casos bonitos.
- Soft-threshold (zona muerta) es el experimento **anti-v1a**.
- Platt / calibración de probabilidades: recién con n ≥ 50.
- No entrenar XGBoost sobre 12 filas.

### Programador (factibilidad)

| Pedido | ¿Se puede en esta rama? | Riesgo |
|---|---|---|
| Medición honesta (Wilson, Loss simétrica, n mínimo) | **Sí, hoy** | Ninguno: no cambia el mercado |
| Taxonomía léxica de titulares | **Sí, hoy** | Ninguno |
| Zona muerta `umbral_consenso` (v1c) | **Sí, hoy, apagada** | Baseline = 0 = identidad |
| 1–2 perillas por hipótesis | **Ya está** | v1a demostró que hay que respetarlo |
| Kyle-λ, XGBoost, PyABC, v1b | **No** | Rompe precio / no aísla / caro |
| 80 exámenes LLM hold-out | **Sí, pero ~US$10 y ~110 llamadas c/u** | Presupuesto. No en esta sesión. |
| Sorpresa en el prompt | **Sí, 1 línea** | Gasta API. Siguiente. |
| Fusionar a `main` | **No hasta evidencia** | Producción se queda en identidad |

---

## 3. Plan paso a paso (el camino al 70 %)

Regla de oro, igual que siempre: **1 hipótesis por sesión, 1–2 perillas,
nunca romper los 5 hechos estilizados, fallback si la API falla.**

### Paso 0 — ya hecho (esta sesión)

1. Loss simétrica: pasarse de largo **cuesta**, igual que quedarse corto.
2. Intervalo de Wilson en la libreta: se ve la incertidumbre, no solo el %.
3. `listo_produccion` exige **≥ 80 casos** con las métricas en verde.
4. Taxonomía léxica (tipo + régimen priced-in/sorpresa).
5. Hipótesis **v1c**: `umbral_consenso = 0.25`. En baseline vale **0**
   (el enjambre de hoy no cambia). No se activa en producción.
6. Producción = `conjunto_activo: baseline`. `main` intocado.

### Paso 1 — medir v1c sin gastar API (barato)

Correr el banco numérico **solo como red de seguridad**:

```text
python -m contenido.experimento --set baseline --vs hipotesis_v1c --n 1
```

v1c **no debería inflar días chicos** (a diferencia de v1a), porque no
toca `impacto_base`. Los líderes siguen oyendo el shock completo; solo
el ambiente de fondo se silencia si es tibio.

Si los extremos se caen o los hechos estilizados se rompen → se descarta
v1c igual que v1a. Sin drama: la rama está aparte.

### Paso 2 — taxonomía sobre lo ya simulado

Sin API. Agarrar la libreta / backtest que ya existe y partir los errores
en casillas: *¿fallamos el signo en resultados? ¿exageramos macros
priced-in?*. Eso dice **dónde** poner el siguiente golpe, no un promedio
que esconde Nvidia y la Fed en el mismo número.

### Paso 3 — una línea en el prompt (sí gasta API)

Cuando Giorgio autorice la tanda:

> “Di si esta noticia era una **sorpresa** o **ya estaba en el precio**.
> Si ya estaba en el precio, tu señal debe ser cercana a 0.”

Eso ataca Fed-en-pausa y “as expected” sin tocar el libro. Hipótesis
aparte, una sesión, contra baseline. Presupuesto: ~US$0.12 × N titulares.

### Paso 4 — hold-out de verdad (el 70 % honesto)

- **No** reusar los 12 casos con los que se inventó la hipótesis.
- ~40 noticias de entrenamiento / ajuste (el 70 % normales + 30 % extremas).
- ~80 hold-out que el enjambre no vio.
- Solo cuentan cerebros IA (no el respaldo léxico).
- Meta: dirección ≥ 70 % **y** el piso de Wilson no da vergüenza,
  fuerza simétrica ≥ 0.70, ≥ 40 % dentro de ±30 %, hechos estilizados OK.

Hasta no tener esos 80, **nadie declara victoria**. Un 8/12 no es calibración.

### Paso 5 — solo si el paso 4 se estanca

- GEPA/DSPy sobre los 8 prompts de arquetipo (caro, micrófono).
- MoE suave: más peso a Quant en resultados, más Doomer en crashes.
- CAR como meta (retorno anormal, no el close-to-close crudo).

No antes. No en paralelo con tres perillas a la vez.

---

## 4. Cómo se usa, sin romper nada

Por defecto **no cambia el producto**. El JSON sigue en `baseline`.

```text
# identidad (hoy)
ENJAMBRE_PERILLAS=baseline

# experimento anti-v1a (solo en esta rama, a propósito)
ENJAMBRE_PERILLAS=hipotesis_v1c
```

Activar v1c en producción exigiría cambiar `conjunto_activo` **y**
evidencia del paso 1–4. Hoy no se cambia.

---

## 5. Qué está prohibido (para no repetir v1a)

- Fusionar a `main` o a `claude/m-d-file-6z1e63`.
- Activar `hipotesis_v1b` (cocina entera).
- Subir `impacto_base` otra vez.
- Declarar “listo” con n < 80.
- Poner Kyle-λ, un precio `k × señal`, PyABC o un XGBoost de 12 filas.
- Gastar la API en v1a/v1b.

---

## 6. Analogía para no perder el norte

Calibrar el Enjambre no es subir el volumen del altavoz. Es enseñarle
al oído a distinguir:

- “la Fed hizo lo que todos esperaban” → el mercado bosteza;
- “Nvidia voló las estimaciones” → el mercado se despierta;
- “aranceles por sorpresa” → el mercado se asusta.

v1a subió el volumen. v1c tapa el oído cuando el ruido es bajo.
El 70 % de dirección se gana leyendo el titular, no empujando el libro.

*Rubicón Lab · consejo de calibración · 3 sep 2026*
