# Análisis en frío — Propuesta 3 ("las 4 ventanas de mejora del acierto")

*Rubicón Lab · 2026-11-17. Verificación contra el código real y contra lo ya hecho.
Esta propuesta es seria y leyó bien el código (cita el hallazgo sin fuga, la
ablación, la cobertura léxica). Pero dos de sus cuatro ventanas YA están medidas o
implementadas, una se apoya en la métrica circular que ya corregimos, y hay una
tensión interna que no resuelve.*

---

## Resumen de una línea

Ventana A es real y es la buena — y **ya está medida y medio implementada** (el
gating que construí la cobra para los casos de alta convicción). Ventana C pide una
medición que **ya corrí**, y su resultado respalda ese mismo gating, no lo que ella
propone. Ventana B es una palanca real pero mejora el PRECIO (el peor predictor) y
choca con A. Ventana D es humo: se apoya en el "80/53" circular que acabamos de
corregir. Ganancia honesta realista: la de A (~+6-7 pts en índice), que el gating ya
expone.

---

## La tensión que la propuesta no resuelve (clave)

La propia propuesta demuestra que **la SEÑAL de líderes predice mejor que el PRECIO
simulado** (Ventana A). Pero sus Ventanas B, C y D **modifican el TONO**, que mueve
el PRECIO (`direccion_pct`), NO la señal (`senal_media_ponderada` se calcula aparte,
en senal_prediccion.py). Es decir: A dice "deja de usar el precio, usa la señal", y
B/C/D dicen "mejoremos el precio". Si vamos a reportar la señal (A), afinar el precio
con B/D rinde poco. La propuesta no nota este choque.

---

## Ventana por ventana

### Ventana A — usar la SEÑAL como dirección, no el precio · **REAL · YA MEDIDA + MEDIO IMPLEMENTADA**
Verificado: `backtest.py:445-477` ya separa `acierto_global` (precio) de
`acierto_senal_global` (señal) — **ese instrumento lo construí yo la semana pasada**.
Y `corrector.py:69,148` confirma que el PRODUCTO reporta `direccion_pct` (el precio)
como "la dirección". Así que el diagnóstico es correcto.
**El número honesto ya lo tengo** (remedir_sin_fuga, sin fuga): en ÍNDICE el precio
acierta 56.7% y la señal 63.1% → la señal gana ~6-7 pts (no 13; el "50 vs 63" de la
propuesta mezcla el agregado con índice). Y **el gating que ya implementé cobra
justamente eso**: marca "fiable" los casos de índice con señal fuerte, donde el
acierto histórico es 80%.
**Lo que FALTA de A (lo rescatable):** decidir si el producto, cuando la convicción
es alta, reporta la dirección de la SEÑAL como titular (hoy reporta el precio). Es
una decisión de producto/pitch, bounded, reversible. (La fórmula λ·precio +
(1-λ)·señal·10 de la propuesta mezcla unidades distintas de forma fea; más limpio es
reportar ambos y que el gating decida cuál creer — que es lo que ya hace `conviccion`.)
→ **La mejor ventana; ~70% hecha. Queda un paso de producto.**

### Ventana C — ponderar por |señal| en el tono · **LA MEDICIÓN YA ESTÁ HECHA**
La propuesta dice: "gating_por_senal existe pero nadie ha reportado su salida;
correrlo es la acción más rentable". **Ya lo corrí** (y lo dejé committeado). Salida
real, sin fuga:
```
|señal|≥   acierto% TODOS   acierto% ÍNDICE
0.0           50.6            63.1
0.2           50.3            61.2
0.3           62.8            80.0
```
No es monótono suave: es PLANO hasta 0.2 y SALTA en 0.3. La propia regla de decisión
de la propuesta dice: "si sube monótono → aplicar ponderación por |señal|; si es
plano → la dilución no es el problema". El dato dice: **el valor está en un UMBRAL
(≥0.3), no en un gradiente** → respalda el GATING que implementé (umbral), no la
ponderación continua α que ella propone. Además, aplicar α en el tono cambiaría el
PRECIO, no la señal. → **Medida; la respuesta es el gating, ya hecho.**

### Ventana B — peso_inv por mercado · **PALANCA REAL, PERO MEJORA EL PEOR LADO**
Verificado: `model.py:436` — `peso_tono_invertidores` es un escalar global, no por
mercado. Cierto. Segmentarlo (como `peso_doomer_por_mercado`) es un cambio limpio y
del mismo patrón ya validado. **Pero** mueve el TONO → el PRECIO, que es el predictor
peor (ver la tensión de arriba). Y la propia propuesta admite el riesgo: en cripto
sin doomer, bajar el peso puede dejar el consenso en "fieles" poco informativos.
→ **Real pero de bajo retorno dado que vamos a reportar la señal; medir-antes, no
prioridad a 4 días del evento.**

### Ventana D — GANANCIA_CONSENSO por signo · **HUMO (métrica circular)**
Verificado: `model.py:79` — `GANANCIA_CONSENSO = 0.8`, escalar único. Cierto. PERO su
justificación es textual: "el enjambre acierta ~80% en positivas pero ~53% en
negativas". **Ese es exactamente el '80/53' de la métrica CIRCULAR Y CON FUGA que
corregí ayer** (la `categoria` se calcula del resultado del precio → hacer el gain
asimétrico para "subir negativas" juega con una categoría circular). La propuesta es
sofisticada pero aquí recae en el comentario viejo (que ya marqué como obsoleto en el
código). Además GANANCIA_CONSENSO mueve el PRECIO, no la señal. → **Humo, misma raíz
que la Propuesta 1.**

### "Cosas que no hacer" · **CORRECTO**
No tocar MINIMO_IA_CONSENSO, no suavizar Plan A, re-medir peso_doomer cripto SIN FUGA
antes de cambiar, no calibrar por arquetipo con N chico (616 casos no alcanzan).
Todo sensato y alineado con nuestra postura.

---

## Veredicto

| Ventana | Estado real | Acción |
|---|---|---|
| **A — señal como dirección** | Instrumento y medición YA hechos; gating ya cobra el 80% de alta convicción | **Rescatable:** decidir si el producto reporta la señal como dirección cuando la convicción es alta (paso de producto/pitch) |
| **C — peso por |señal|** | Medición YA corrida; el valor es un umbral, no un gradiente | Ya respondida por el gating; la α continua rinde poco |
| **B — peso_inv por mercado** | Palanca real no construida | Mejora el PRECIO (peor predictor) y choca con A; medir-antes, baja prioridad |
| **D — gain por signo** | Palanca real no construida | **Humo:** se apoya en el 80/53 circular ya corregido |

**Ganancia honesta realista** (no los +15-25 de la propuesta, que doble-cuentan): la
de A, ~+6-7 pts en índice, y ya está expuesta por el gating (80% en la banda de alta
convicción). El resto es especulativo o humo.

**Coincidencia importante:** las dos propuestas de calibración (1 y 3) convergen en
que la SEÑAL > PRECIO y en el gating por fuerza de señal — exactamente lo que ya
implementé. Eso valida el camino. Lo único nuevo y rescatable de esta propuesta es el
paso de producto de la Ventana A: **que la demo, cuando el enjambre esté muy
convencido, muestre la dirección de la señal como el titular, no la del precio.**
