# Investigación a fondo: la causa raíz del 38% en negativas (y propuestas realistas)

**Fecha:** 6 de septiembre de 2026
**Método:** análisis de los 645 casos reales + experimentos sobre el motor (sin LLM, sin coste).
**Veredicto de una línea:** el enjambre predice "sube" de más. La formación de precio está **sana**; el sesgo vive **arriba, en cómo los líderes agregan la noticia**: los arquetipos contrarian/optimista **cancelan** la señal bajista, y encima muchos crashes siguen a titulares que de verdad parecían neutros. Hay una parte **arreglable** y una parte **irreducible** — y las separo abajo con números.

---

## 0. Corrección honesta de mi diagnóstico anterior

En `INFORME_DIAGNOSTICO_NEGATIVAS.md` dije que el techo en negativas era ~96% ("si siempre dijera baja"). **Eso estaba mal como techo alcanzable:** la etiqueta `categoria` se define por el **resultado real del mercado** (`_categoria(pct_real)`: ≤−1% = negativa), no por el tono de la noticia. Ese "96%" usa el resultado que en producción **no conoces de antemano** — es trampa de retrovisor. El techo real está limitado por cuánta dirección trae el titular, que es mucho menos. Lo corrijo aquí.

## 1. El síntoma, con números duros (264 negativas)

| | valor |
|---|---|
| `direccion_pct` del enjambre (predicción) | media **+5.2%** · mediana +2.7% |
| `pct_real` del mercado (realidad) | media **−9.1%** · mediana −7.8% |
| De las que predijo SUBIR (156), magnitud media | **+16.7%** |
| Acierto de dirección | **38.3%** |

El enjambre no falla "por poco": predice subidas **grandes** (+16.7% de media) donde el mercado se desplomó. Es un sesgo alcista fuerte, no una deriva tibia.

## 2. Dónde NO está el problema (verificado con experimentos)

Antes de acusar a nadie, probé el motor:

- **Deriva base sin noticia (5 semillas): −1.93.** No hay deriva alcista estructural. → **Mi sospecha inicial (la compra de fondo que empuja el precio arriba) era FALSA.** Bien haberla medido.
- **Curva de respuesta mecánica** (meter un sentimiento y ver el precio):

  | sentimiento | −0.6 | −0.4 | −0.2 | +0.1 | +0.4 | +0.6 |
  |---|---|---|---|---|---|---|
  | precio | −6.4 | −5.1 | −2.4 | +0.5 | +1.6 | +7.0 |

  Monótona y con el signo correcto: negativo → baja, positivo → sube. **La formación de precio está sana. No tocar.**

## 3. Dónde SÍ está el problema (la interpretación de los líderes)

Como el motor es fiel, el +5% de subida en los crashes significa que el **tono de los líderes** (`self.sentimiento`) salió **positivo** en esos casos. Dos causas, ambas verificadas:

### 3a. Los arquetipos se cancelan (dilución estructural)
Las transformaciones por arquetipo (`brains/fallback.py`, y el mismo espíritu en el LLM) hacen que ante una mala noticia (s=−0.6):
- **Quant** (`−0.5·s`) → **+0.30** (invierte)
- **Contrarian** (`−0.7·s`) → **+0.42** (invierte)
- **Optimista** (si s<−0.5) → **+0.40** (piso positivo)
- Doomer −0.71, FOMO −0.96, Institucional −0.24…

Ponderando por cantidad × confianza, el consenso de una **mala noticia fuerte (−0.6)** sale en solo **≈ −0.16** (× `GANANCIA_CONSENSO 0.8`). Los optimistas y contrarians **borran** a los doomers. Una noticia −0.6 llega al mercado como −0.16: casi neutral. *(La diversidad de arquetipos es un rasgo del producto —da las frases del hover—, pero su NETO como "tono de mercado" quedó demasiado optimista.)*

### 3b. Muchos crashes siguen a titulares que parecían neutros (irreducible)
Mirando los peores casos: *"Bitcoin Trades Above $52K"* (subió el titular, cayó 24% después), *"Whale Activity In Today's Session"* (neutro), *"miner relocation"* (operativo). El líder los leyó bien; el mercado cayó **por sorpresa**, por razones que no estaban en el titular. Eso **ningún arreglo del motor** lo predice.

**Cuánto es irreducible, medido:** el diccionario léxico se queda **mudo (sin palabra direccional) en el 69% de las negativas.** Es decir, 2 de cada 3 titulares que precedieron caídas **no traen una palabra claramente bajista**. Ahí el techo es bajo para cualquiera.

### 3c. El respaldo léxico está roto (bonus, y esto SÍ es medible aquí)
Cuando la API falla, todo cae al diccionario. Y el diccionario hoy:
- Lee *"Bitcoin tumbles below $23,000 after Celsius freezes withdrawals"* → **0.00** (neutral).
- *"Stocks Are Diving"* → 0.00. *"Futures Fall More than 5,000"* → 0.00.
- Se queda **mudo en el 75%** de todos los titulares.
- **Pero cuando opina, acierta el 70% (94% en negativas).** Alta precisión, baja cobertura.

### 3d. Magnitudes absurdas en cripto (problema aparte)
Casos como *"Whale Activity"* → **+54%**, *"miner relocation"* → **+71%**. Eso no es sentimiento: es el sim generando movimientos gigantes en símbolos cripto de baja liquidez. Es un problema de **volatilidad/magnitud**, distinto del de dirección.

## 4. Propuestas realistas (etiquetadas por lo que se puede medir)

### 🟢 P1 — Ampliar el diccionario léxico *(se hace y se MIDE en esta sesión)*
Añadir la jerga bajista/alcista que hoy falta (*tumbles, diving, slump, sell-off, freezes, warns, downgrade, guidance cut, below/sub…*). Es alta-precisión/baja-cobertura: bajar el "mudo" del 69% subiría la señal bajista del respaldo.
- **Riesgo:** bajo (solo afecta la ruta de respaldo).
- **Honestidad:** **NO cambia el 38%** (esos casos usaron el LLM `'ia'`). Mejora la **robustez cuando la API se cae** — hoy, sin saldo, el enjambre quedaría ciego ante crashes obvios. Se mide con el acierto del léxico sobre los 645, antes/después.

### 🟡 P2 — Separar "tono del mercado" de "apuesta del líder" *(la palanca real del 38%; se valida en CI con LLM)*
Hoy el tono de fondo (`_tono_de_titular`) es el promedio de las **señales** de los líderes — que ya incluyen las inversiones contrarian/optimista (su forma de **apostar**, no su lectura de la noticia). Eso mete el ruido contrarian dentro del "clima" que sienten todos. Propuesta: el **tono** se calcula de la lectura direccional de la noticia (antes de la inversión de arquetipo); las señales individuales siguen viajando por la red para las apuestas y las frases. Así una mala noticia genuina llega al mercado como mala, sin que el contrarian la cancele en el clima.
- **Riesgo:** medio (toca el corazón del producto; hay que cuidar la asimetría de pánico y no re-crear sobre-pánico — dialoga con el freno que ya pusimos).
- **Honestidad:** el efecto real en el 38% **solo se mide en CI con la API key** (`backtest.py`). Aquí se puede prototipar y validar hechos estilizados, pero el número final es de CI.

### 🟢 P3 — Acotar las magnitudes absurdas en cripto *(se hace y se mide aquí, mecánico)*
Investigar por qué símbolos de baja liquidez dan +50/+70% y acotar la volatilidad por liquidez del símbolo. Mejora realismo y la métrica de magnitud. No toca dirección.
- **Riesgo:** bajo-medio. **Medible** con los hechos estilizados y el rango de `direccion_pct`.

### 🔵 P4 — Reencuadre honesto del producto *(decisión tuya)*
Parte del 38% es irreducible (69% de las negativas no traen palabra bajista). Opciones: medir por **segmento** (ya sabemos cripto 68%, índice 55%), y/o entregar una **confianza** en vez de una dirección dura cuando el titular trae poca señal ("el enjambre no ve señal clara") — más honesto ante CMF y más útil que forzar un signo.

## 5. Recomendación de secuencia

1. **P1 ahora** (rápido, medible, mejora robustez real ante caídas de API). Te doy el antes/después.
2. **P3 después** (acota lo absurdo de cripto; mejora realismo medible).
3. **P2 como el proyecto grande** (la palanca del 38% de verdad): prototipar aquí, validar hechos estilizados aquí, y **medir el acierto real en CI con LLM**. Es el único camino honesto para tocar el 38%.
4. **P4 en paralelo** como decisión de producto (segmentar / confianza).

**Lo que NO recomiendo:** prometer "38% → 90%". El techo real es más bajo por la parte irreducible. Lo honesto es apuntar a mejoras medibles por tramo y no vender un número mágico.

---

*Experimentos y análisis sobre `respaldo.casos_remotos()` (645 casos) y el motor local.
Sin LLM, sin coste. Motor y producción: sin cambios por esta investigación.*
