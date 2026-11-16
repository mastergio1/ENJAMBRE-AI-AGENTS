# Análisis en frío — Propuesta "Gating + tono" (contra el código real)

*Rubicón Lab · 2026-11-16. Verificación punto por punto de la propuesta contra el
código actual del motor, sin sesgo. Etiquetas: **YA HECHO** · **CORRECTO** ·
**IMPRECISO** · **PREMISA OBSOLETA** · **VALE LA PENA**.*

---

## Resumen de una línea

La propuesta leyó el código de verdad (las constantes que cita son exactas) y su
**punto 1 (gating) y punto 2 (acople señal↔tono) son observaciones correctas y
valiosas**. Pero su **diagnóstico de arranque — "positivas ~80% / negativas ~53%,
sesgo alcista"— sale de comentarios del código que describen la métrica VIEJA con
fuga**. Esa métrica ya la demolimos: medido sin fuga el acierto agregado es ~50% y
solo índice conserva señal (~63%). Varios puntos (3, 4, 5) apuntan a "arreglar el
sesgo en negativas", un blanco que **se disuelve** cuando mides sin fuga.

---

## El problema de fondo (afecta a casi toda la propuesta)

La tabla de diagnóstico de la propuesta:

| Régimen | "Acierto" que cita | Realidad |
|---|---|---|
| Positivas | ~80% | artefacto de la métrica circular |
| Negativas | ~53% | artefacto de la métrica circular |

De dónde sale ese 80/53: de los comentarios de `engine/model.py:118-119`, que citan
`INFORME_CAUSA_RAIZ_NEGATIVAS.md`. Ese informe usó la métrica **con dos fugas** que
ya identificamos y corregimos:

1. **La categoría es circular.** `categoria` ("negativa"/"positiva") se calcula
   DEL RESULTADO del precio (`cosechador._categoria(pct_ventana)`), no del titular.
   Entonces "acierto en negativas" mide qué tan seguido el signo del precio simulado
   coincide con el signo del precio real… en los días que ya se definieron por su
   precio. Hacer el tono más bajista "mejora negativas" por construcción.
2. **Fuga de selección + ventana.** El cosechador elige días de salto grande y la
   ventana de resultado empezaba ANTES del titular → incluía el mismo salto que
   seleccionó el día.

Medido **sin fuga** (`engine/calibration/remedir_sin_fuga.py`, 616 casos, Yahoo):

```
mercado       n | CON fuga precio/señal | SIN fuga precio/señal
TODOS       616 |   60.8 / 64.4   |   49.4 / 50.6
indice      163 |   55.2 / 63.8   |   56.7 / 63.1
cripto      220 |   68.8 / 71.6   |   50.7 / 48.8
accion      188 |   60.1 / 60.1   |   44.2 / 44.2
```

**No existe un "80% en positivas" cuando mides sin fuga.** El techo honesto es:
índice ~63%, el resto ~azar (la dirección no está en el texto). Por eso toda mejora
que se mida contra el 80/53 está midiendo humo.

---

## Punto por punto

### Punto 1 — Gating por fuerza de señal · **CORRECTO + YA MEDIDO**
La propuesta acierta: cuando |señal| es alta, el acierto sube. **Ya lo medí** (sin
fuga), y el resultado es el mejor dato de toda la etapa:

```
|señal|≥    acierto% (TODOS)   acierto% (ÍNDICE)   cobertura(índice)
0.0            50.6               63.1               100%
0.2            50.3               61.2                60%
0.3            62.8               80.0                21%
```

En índice, con señal fuerte (|señal|≥0.3) el acierto es **80%** sobre ~1 de cada 5
casos. Eso es un titular honesto y vendible.
**Falta lo que la propuesta pide bien:** el reporte en producción ya expone
`fuerza_consenso` y `senal_media_ponderada` (`server.py:646-658`), pero **no aplica
la decisión de gating** (marcar "dirección débil/ambigua" bajo umbral) ni una
`confianza_calibrada`. Eso sí vale la pena y es barato. → **VALE LA PENA (alto ROI).**

### Punto 2 — Acoplar la señal de predicción con el tono · **CORRECTO (observación fina)**
Es verdad y está bien visto: hoy hay **dos ponderaciones distintas**.
- **Tono** (`model._tono_de_titular`): pondera por `confianza` y baja a
  `ARQUETIPOS_INVERSORES` por `peso_tono_invertidores`.
- **Predicción** (`senal_prediccion.senal_media_ponderada`): baja a 2 contrarians a
  0.3, **sin** ponderar por confianza.

Están desacopladas, como dice. **PERO ojo con una imprecisión suya:** afirma que
"el optimista sigue entrando completo [en el tono]". Falso: `influencer_optimista`
**ya está** en `ARQUETIPOS_INVERSORES` (`model.py:95-97`), así que el tono ya lo
castiga. En la PREDICCIÓN el optimista NO se baja **a propósito** (la ablación lo
halló útil). Acoplar las dos ponderaciones es razonable de probar, pero es un ajuste
de magnitud/clima, no de dirección → impacto esperado modesto sin fuga.
→ **CORRECTO, pero VALE LA PENA solo como experimento medido, no como certeza.**

### Punto 3 — Bajar umbral de Plan A (0.35 → 0.20) · **PREMISA OBSOLETA**
`umbral_correccion_sesgo = 0.35` ✓ (verificado). La corrección solo dispara con
consenso < −umbral y solo hace la lectura MÁS bajista (nunca invierte). Bajarlo es
trivial de medir (hay override por entorno). **Pero** su objetivo declarado —"subir
el acierto en negativas"— apunta a la métrica circular. Medido sin fuga, empujar el
tono más bajista no "mejora" nada real; solo juega con la categoría. → **No es daño,
pero el beneficio que promete es ilusorio.**

### Punto 4 — Consenso "fiel" separado del "completo" · **PARCIALMENTE YA HECHO**
La idea estructural (un consenso solo de voces no-invertidoras para tono+predicción,
y el completo para la UI) es limpia. **Pero ya existe en forma de pesos:** el tono
baja a los invertidores (`peso_tono_invertidores`) y la predicción baja a los
contrarians (0.3), mientras la UI muestra todas las voces. Reescribirlo como split
binario es refactor, no capacidad nueva, y de nuevo persigue el sesgo en negativas
(premisa obsoleta). → **YA HECHO en esencia; refactor opcional, bajo ROI.**

### Punto 5 — Corregir polaridad cuando léxico vs IA divergen · **CORRECTO (hay base)**
`monitorear_polaridad` existe y es **pasivo** (`model.py:185-198`, solo loguea), tal
como dice. Convertirlo en corrección (si discrepan en signo > X%, no confiar en el
consenso) es una idea sensata y sobre todo **defensiva** (evita volteretas en
titulares compuestos como "slash tariffs"). → **VALE LA PENA como robustez**, aunque
su efecto en el acierto honesto es incierto.

### Punto 6 — Saturación de magnitud por mercado (P3) · **YA HECHO (instrumentado)**
`server.py:638,651` ya guarda `recorte_aplicado` (si el tope de magnitud actuó) y la
magnitud cruda. Medir saturación por mercado es un query sobre datos que ya se
guardan. → **YA HECHO; solo falta el reporte, trivial. No cambia la dirección.**

### Punto 7 — Feature engineering + calibrador Platt/isotonic · **YA HECHO (el arnés)**
`engine/contenido/calibracion.py` ya trae Platt e Isotonic (`CalibradorPlatt`,
`CalibradorIsotonico`), Brier, log-loss, curva de confiabilidad y skill-score, con
mapeos para `senal_media`, `senal_ponderada` y `direccion`. `walk_forward.py` y
`verificador.py` son el hold-out. **Lo único nuevo y útil de este punto:** alimentar
el calibrador con **features adicionales** (|señal| + fuerza_consenso + dispersión +
coherencia IA/léxico + tipo de mercado) en vez de un solo score. Eso sí es trabajo
nuevo de valor para la CONFIANZA (no para la dirección). → **Arnés YA HECHO; el
multi-feature VALE LA PENA para confianza.**

### Punto 8 — Ablación de arquetipos · **YA HECHO (script) + medido**
`engine/calibration/ablacion_arquetipos.py` existe y ya corrió
(`docs/calibracion-por-arquetipo.md`): por eso bajamos contrarians a 0.3 y dejamos
al optimista. Re-correrlo en el régimen negativo vuelve a chocar con la métrica
circular. → **YA HECHO; re-correr solo útil si se mide sin fuga.**

### "Qué no tocar" · **CORRECTO y alineado**
No subir agentes/llamadas, no tocar la red (es para la ola visual y los hechos
estilizados), no buscar un oráculo. Todo coincide con nuestra postura. Su cifra
objetivo (">60-65% negativas, >75% con señal fuerte") coincide con lo que YA
tenemos honestamente en índice (80% con |señal|≥0.3).

---

## Veredicto: qué de esta propuesta es oro y qué es humo

**Oro (vale la pena, y es barato/honesto):**
1. **Gating en producción** (punto 1): aplicar la decisión "no afirmar dirección
   cuando |señal| es baja; marcar fuerte/débil" + `confianza_calibrada`. Ya tenemos
   la medición que lo justifica (80% índice con señal fuerte). **Máximo ROI.**
2. **Corrección de polaridad defensiva** (punto 5): robustez ante titulares
   compuestos. No sube el acierto pero evita papelones en la demo.
3. **Calibrador multi-feature para la CONFIANZA** (punto 7, parte nueva): mejora el
   número de confianza, no la dirección. Útil para el pitch honesto.

**Humo (basado en la métrica con fuga que ya corregimos):**
- Todo lo orientado a "arreglar el sesgo alcista en negativas" (puntos 3, 4, y el
  objetivo de 2): persigue una categoría circular. Sin fuga, ese problema casi no
  existe; lo que existe es el techo estructural (la dirección no está en el texto
  para cripto/acción).

**Ya hecho (no-op):** el optimista ya está castigado en el tono; Platt/isotonic ya
existen; la ablación ya corrió; la saturación (P3) ya se instrumenta.

**La conclusión no cambia:** el ángulo honesto y vendible es **índice + alta
confianza (gating)**. Esta propuesta, bien filtrada, refuerza exactamente eso.
