# Mejoras — atacar el micrófono (y lo que no)

Fecha: 3 de septiembre de 2026  
Rama: `calibracion/impacto-no-lineal`  
Producción: **baseline, no se toca**

El parlante ya grita. El 60 % de dirección y el 3× de más salen de
cómo los cerebros **leen**. Abajo: lo que quedó construido hoy, y lo
que conviene (o no) hacer después.

## Lo que quedó hecho hoy (apagado, identidad en baseline)

| Frente | Qué | Cómo se enciende |
|---|---|---|
| Prompt | Sorpresa vs “ya estaba en el precio”; earnings = beat/miss de ESA empresa; no sopa de tickers | `hipotesis_v1d` |
| Fallback | Si no hay API y el titular es priced-in, la señal léxica se achica a ±0.15 | mismo v1d |
| Caché | Versión `microfono_v1` para no reciclar voces viejas | automático con v1d |
| Zona muerta | El ambiente tibio no inunda el mercado | `hipotesis_v1c` (ya medida) |
| Paquete | v1c + v1d juntos | `hipotesis_v1e` — **no medir hasta tener v1d solo** |
| Taxonomía | Más pesca: guidance, EPS, “in line”, “pauses rate” | siempre (solo libreta) |
| Libreta | Parte por mercado. `listo_produccion` mira **índice+acción**, no cripto | siempre |

Tanda chica lista, **no corre sin la clave de Claude**:

```text
python -m contenido.tanda_microfono --dry
ENJAMBRE_PERILLAS=hipotesis_v1d python -m contenido.tanda_microfono --n 4
```

~US$0.12 × N. 4 titulares ≈ US$0.50. 12 ≈ US$1.50.

## Propuestas — qué atacar, en orden

### 1. Medir v1d (lo siguiente, ~US$1.50)

12 titulares curados: 4 Fed “as expected”, 3 crashes/aranceles, 3 resultados, 2 ruido.
**Una** hipótesis contra baseline. Si v1d no baja el grito en Fed-en-pausa
sin apagar Lehman, se descarta igual que v1a.

### 2. Limpiar la libreta (gratis)

- El corrector toma el **primer ticker** de una sopa (`APP,GILD,…` en una
  noticia de Eli Lilly). Hay que puntuar el símbolo del **hecho**, no el
  primero de la lista.
- Cripto (233/632) no puede mandar en la nota del producto. Ya partido.
- Filtrar “whale activity / most-searched / crypto update”: no son
  exámenes, son ruido. No calibran.

### 3. Si v1d gana: v1e (zona muerta + prompt)

Solo entonces se combinan. Si se combinan antes, no se sabe qué curó.

### 4. Hold-out de verdad (~US$10, ~80 titulares índice+acción)

Ahí se declara o no el 70 %. Wilson tiene que quedar con el piso
decente, no un 8/12.

### 5. Más adelante (no ahora)

| Idea | ¿Sí? | Por qué |
|---|---|---|
| GEPA/DSPy a los 8 prompts | Después del hold-out | Caro; ataca el micrófono de verdad |
| MoE: Quant más peso en earnings, Doomer en crashes | Después de casillas con n≥30 | Hoy n por casilla es chico |
| Bajar `ganancia_consenso` otra vez (0.8 → 0.5) | Solo si v1d no corta el 3× | Es volumen otra vez; v1a enseñó |
| Más cerebros FOMO | **No** | El enjambre ya grita 3× |
| Kyle-λ / fijar el % | **No** | Rompe el precio emergente |
| PyABC / 10⁵ sims | **No** | Impagable |
| FinBERT para etiquetar sorpresa | Diagnóstico | El léxico ya pesca; un modelo extra no mueve el precio |
| CAR (retorno anormal) | Meta de medición | Cuando la libreta esté limpia |
| Campo `sorpresa` que el LLM devuelva en el JSON | Evolución de v1d | Hoy va en el prompt; mañana puede ser un número |

## Lo que no prometemos

v1d **no** está medida con Claude desde acá: no hay llave en este entorno.
El código está, la tanda está, producción no cambió. Un 70 % se declara
con 80 hold-out de índice+acción, no con un prompt nuevo sin nota.

*Rubicón Lab · micrófono · 3 sep 2026*
