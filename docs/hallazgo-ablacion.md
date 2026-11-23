# Hallazgo — Ablación A0–A5: dónde vive (y dónde no) el poder predictivo

*Rubicón Lab · El Enjambre · 2026-11-23. Fase 3 del plan. Herramienta:
`engine/calibration/ablacion.py` (con tests). Mide, escalón por escalón sobre el
dataset SIN FUGA (`pct_corr`), cuánto acierta la DIRECCIÓN cada capa del sistema.
Sin IA ni motor: reusa números ya calculados (`senal` = consenso de líderes;
`direccion_pct` = lo que simuló el ABM) y el bootstrap multiway para el intervalo.*

## La escalera

| | Qué es | De dónde sale |
|---|---|---|
| **A0** | piso tonto: "índices suelen subir" (clase mayoritaria) | resultado real |
| **A1** | léxico del titular (diccionario, sin IA) | `sentimiento_lexico` |
| **A3** | **consenso de los ~110 cerebros LLM, SIN el ABM** | campo `senal` |
| **A4** | **el ABM completo de 10.150 agentes** | campo `direccion_pct` |

(A2 = un solo LLM, y A5 = ABM + evidencia, necesitan correr IA/motor; pendientes.)

## Resultado (acierto direccional, zona muerta 0.3%)

### ÍNDICE
| Escalón | En muestra | **Fuera de muestra** (corte temporal 70/30, n=43) |
|---|---:|---:|
| A0 piso "siempre sube" | 64.8 % | **62.8 %** |
| A1 léxico | 59.3 % (n=54) | — |
| **A3 consenso LLM** | 62.7 % | **65.1 %** |
| **A4 ABM completo** | 56.3 % | **53.5 %** |

**Gate del plan (A4 − A3): −6.3 pts en muestra, −11.6 fuera.** Cuando el ABM le
cambia el signo al consenso (21 veces), acierta 6 y **falla 15**.

### TODOS los mercados (índice + cripto + oro + petróleo + acción)
Todo ≈ 50 % (moneda al aire). A3 = 50.5 %, A4 = 49.3 %. Gate A4 − A3 = −1.2.

## Qué significa (sin adornos)

1. **El ABM NO mejora la predicción; la empeora.** Es el hallazgo central y aguanta
   dentro y fuera de muestra, en índice y en todos los mercados. La simulación de
   10.150 agentes, cuando se atreve a contradecir al consenso de los líderes,
   acierta ~1 de cada 3 veces. **El valor predictivo (el que hay) vive en el
   consenso LLM (A3), no en el enjambre de agentes (A4).**

2. **El poco acierto que existe está solo en ÍNDICE, y es frágil.** A3 ronda 63–65 %,
   apenas 0–2 puntos por encima del piso tonto "los índices suelen subir" (~63 %).
   Con n pequeño y los intervalos solapados, **no podemos afirmar que el consenso
   le gane de verdad al 'siempre sube'.** Es un indicio, no una prueba.

3. **Fuera de índice no hay señal.** Cripto, oro, petróleo y acciones individuales:
   moneda al aire en todas las capas.

## Implicación de PRODUCTO (importante)

Hoy el reporte muestra como "dirección esperada" el **`direccion_pct` del ABM
(A4)** — justo el peor predictor. **Recomendación:** comunicar la dirección del
**consenso de líderes (A3)**, no la del precio simulado; y encuadrar siempre como
"lectura de masas", nunca como predicción — más aún fuera de índice. El enjambre 3D
sigue siendo un producto y una visualización genuinos; lo que NO se sostiene es
venderlo como un predictor incremental por encima de "promediar lo que dicen los
líderes".

## Qué NO cierra esto

- **A2** (un solo LLM leyendo el titular): falta medir si ~110 cerebros le ganan a
  uno solo. Necesita una corrida de IA.
- **A5** (ABM + evidencia `as_of`): ya está la capa de evidencia desplegada; falta
  medir si cambia algo.
- El veredicto final espera **más casos prospectivos** (Fase 7): el registro limpio
  es la única forma de angostar estos intervalos.
