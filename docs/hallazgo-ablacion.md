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

---

## Actualización (auditoría v4, 23-nov-2026) — método correcto, veredicto más firme

La auditoría v4 señaló, con razón, dos defectos de rigor que ya se corrigieron en
`ablacion.py` (con tests):

1. **A0 ya no mira el examen.** Antes la clase mayoritaria se calculaba sobre TODO
   el conjunto (miraba las etiquetas que debía predecir). Ahora es *train-only*
   (expanding window): cada caso usa solo la mayoría de los casos **anteriores**.
   Resultado honesto en índice: **64.5 %** (casi igual que antes, porque los índices
   suben de forma persistente) — **sigue igualando al consenso A3 (62.7 %)**.

2. **Inferencia PAREADA por evento** (reemplaza el atajo "el más ancho de tres").
   La unidad de dependencia correcta es el ANUNCIO (misma fecha), no el caso suelto.
   Diferencia pareada d = acierto_A4 − acierto_A3, con cluster bootstrap por evento:

   | Mercado | media(A4−A3) | IC 95 % | veredicto |
   |---|---:|:---:|---|
   | **ÍNDICE** | **−0.063** | **[−0.124, −0.007]** | **significativo: el ABM RESTA** |
   | TODOS | −0.012 | [−0.045, 0.021] | no concluyente (cruza 0) |

**Conclusión reforzada:** en índice, el IC pareado **excluye el cero** → ahora es
defendible estadísticamente que el ABM **empeora** la dirección frente al consenso,
no solo de forma puntual. Y como A0 honesto (64.5 %) iguala a A3 (62.7 %), la señal
del consenso **no supera con claridad** el piso "los índices suben". El veredicto
definitivo sigue dependiendo del experimento **prospectivo** pre-registrado (v4
Fase 07), no de este histórico.
