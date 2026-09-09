# Paso B (barato) — Auditoría del "panel de control": perillas muertas

**Fecha:** 2026-09-09 · **Rama:** `claude/m-d-file-6z1e63`
**Costo en crédito de IA:** $0 (solo lectura de código + agentes de reglas)

---

## De dónde salió esto

Arreglando el arrastre (Paso A) perdí **tres mediciones** girando perillas que
no hacían nada. Eso destapó un problema de fondo: el archivo de configuración
(`agentes.json`) tiene muchas perillas que **el código ignora**. Giras la
perilla, y no pasa nada.

Antes de que gastes crédito calibrando (Paso C), el panel tiene que ser real.
Si la mitad de las perillas están muertas, tiras plata midiendo cambios que no
existen. Así que hice el barrido completo: perilla por perilla, ¿la lee el
código o no?

---

## El diagnóstico (antes)

De ~30 perillas del config, **17 estaban muertas** — leídas por cero archivos
de código. El agente usaba un valor fijo escrito por dentro e ignoraba el panel.

La buena noticia: casi todos los valores muertos **coincidían** con lo que el
código hacía por dentro, así que el panel no engañaba en los números… salvo
**una excepción real**:

> **La mentira:** el *noise trader* (el ruido de fondo del mercado) decía
> `probabilidad_operar: 0.05` en el panel, pero el código corría a **0.12** —
> 2,4 veces más ruido del que el panel declaraba. El 0.12 es el valor calibrado
> que sostiene las huellas del mercado (sin ruido no hay hechos estilizados),
> así que la verdad es 0.12; **corregí el panel para que lo diga.**

---

## Qué hice (el arreglo)

**Enchufé las 17 perillas al código**, con el valor por defecto = el que el
código ya usaba. Traducción: **no cambia ningún comportamiento** (lo confirmé
con la batería de hechos estilizados: sigue 9/9), pero de ahora en adelante
girar cualquiera de estas perillas **sí hace algo**.

Perillas que pasaron de muertas a vivas, por agente:

| Agente | Perillas enchufadas |
|---|---|
| Fundamentalista | umbral_compra, umbral_venta, ponderación de noticia, ticks entre operaciones |
| Fondo pasivo | ticks entre compras |
| Noise trader | probabilidad de operar *(mentira corregida 0.05→0.12)*, fracción sensible a noticias, desplazamiento por sentimiento |
| Manada | ventana de observación |
| FOMO | ventana de ticks, vecinos mínimos activos |
| Miedoso | ticks de calma para recomprar |
| Contrarian | umbral de consenso, ventana de sentimiento, ticks entre operaciones |
| Buy & hold | umbral de caída-oportunidad, probabilidad de liquidez |

Única perilla que dejé como constante a propósito: `sensibilidad_noticias` del
fondo pasivo — es **0 por diseño** (el flujo 401k/AFP no reacciona a titulares)
y no hay código de noticia al que enchufarla. Queda anotada.

---

## Por qué esto importa (en simple)

Es como un tablero de auto donde la mitad de las perillas del clima no estaban
conectadas al aire acondicionado. El auto andaba bien —los valores de fábrica
coincidían— pero si querías ajustar algo, girabas en el vacío. **Ahora todas
están conectadas.** Cuando quieras calibrar cripto, oro o lo que sea (Paso C,
con IA), cada ajuste que hagas va a tener efecto real y medible. Nada de plata
tirada en perillas fantasma.

---

## Verificación

- Sintaxis del código: OK.
- Las 17 perillas: ahora leídas por el código (confirmado con búsqueda).
- Batería de hechos estilizados: **9/9 pasan** (arrastre incluido) — cero
  regresión, como se esperaba (los defaults son los valores de siempre).

---

## ¿Y las mediciones del doomer (peso 1.0, 0.5…) quedaron mal?

**No. Esa perilla SÍ estaba viva.** Es de otra familia: la del doomer
(`peso_doomer`, `peso_doomer_por_mercado`, `umbral_correccion_sesgo`) vive en
`model.py` (el cerebro del tono), no en `reglas.py` (los agentes). Las 17
muertas eran solo las de comportamiento de los agentes.

**La prueba:** una perilla muerta da resultados **idénticos** cuando la cambias
(lo vimos 3 veces con el arrastre: salida idéntica al byte). Las mediciones del
doomer dieron resultados **distintos** entre peso 0 y 1.0 (índice se movió +7.6
puntos; cripto quedó en 0.0). Si estuviera muerta, habrían sido idénticas. Se
movieron → estaba viva.

**Punto fino de método:** las 17 perillas muertas estaban fijas en el **mismo
valor en ambos lados** de cada comparación del doomer. Un A/B donde una variable
está trabada igual en los dos lados sigue siendo válido: aislabas el doomer, y
todo lo demás era constante. **Las conclusiones del doomer se sostienen.**

## Una perilla muerta más (a nivel global)

`ruido_parametros_sigma` (0.15) — el "±15%" que hace único a cada agente —
también estaba hardcodeada en `base.py`. Enchufada igual (default 0.15, sin
cambio de comportamiento). Ahora la heterogeneidad del enjambre es calibrable
desde el panel.

## Dónde quedamos

- **Paso A — arrastre:** hecho. ✅
- **Paso B — panel honesto (este):** hecho. ✅ Auditoría cruzada completa: de
  todo el config, la única clave sin leer es `sensibilidad_noticias` (constante
  0 por diseño). Todo lo demás, vivo.
- **Paso C — calibrar con IA:** ahora el panel está listo para eso. Requiere
  recarga (~$20-30). Te aviso cuando toque.
