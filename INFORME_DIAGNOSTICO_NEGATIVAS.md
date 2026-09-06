# Diagnóstico: por qué el enjambre falla las negativas (y por qué el sesgo optimista va al revés)

**Fecha:** 6 de septiembre de 2026
**Datos:** los 645 casos reales del respaldo (`respaldo.casos_remotos()`), esquema correcto.
**Veredicto de una línea:** el enjambre NO es demasiado pesimista con las malas noticias — es demasiado **optimista**. Ante noticias malas donde el mercado real cayó el 96% de las veces, el enjambre predijo que **subiría el 59%** de las veces. El Sprint 2.2 (añadir sesgo optimista) empeoraría el problema; la palanca correcta es la **contraria**.

---

## 0. Qué medimos

Sobre los 645 exámenes ya rendidos, comparamos para cada caso la dirección que predijo el enjambre (`direccion_pct`) contra lo que hizo el mercado de verdad (`reaccion_real.pct_real`), separando por el tono de la noticia (`categoria`).

## 1. El dato que lo cambia todo

### Noticias NEGATIVAS (264 casos)
| | Subió | Bajó |
|---|---|---|
| **Realidad** | 4% | **96%** |
| **Enjambre predijo** | **59%** | 41% |

- **Acierto actual del enjambre: 38.3%**
- Si el enjambre simplemente dijera "baja" ante toda mala noticia: **95.8%**.

### Noticias POSITIVAS (329 casos)
| | Subió | Bajó |
|---|---|---|
| **Realidad** | 98% | 2% |
| **Enjambre predijo** | 81% | 19% |

- **Acierto actual: 79.6%**
- Techo simple ("sube" siempre): 98.2%.

## 2. La lectura honesta

El enjambre tiene un **sesgo alcista sistemático**: predice "sube" mucho más de lo que la realidad justifica.
- En **positivas** ese sesgo *coincide* con la realidad (casi todo sube), así que el acierto se ve decente (79.6%).
- En **negativas** el sesgo choca de frente con la realidad: el mercado cae el 96% de las veces, pero el enjambre vota "sube" el 59%. Por eso el acierto se desploma al 38%.

**El problema del 38% no es pesimismo — es exceso de optimismo.** El enjambre se "traga" las malas noticias: la presión compradora de fondo (fondos pasivos, buy & hold, indexados que compran pase lo que pase) **ahoga** la señal negativa de los líderes, y el precio termina subiendo aunque la noticia sea mala.

## 3. Por qué el Sprint 2.2 va exactamente al revés

El Sprint 2.2 propone añadir **sesgo OPTIMISTA** a los líderes ante noticias negativas (que interpreten que "ya está descontado" y suban). Pero el enjambre **ya** es demasiado optimista con las malas noticias (predice subir el 59% cuando solo sube el 4%). Añadir más optimismo empujaría ese 59% aún más arriba → el acierto en negativas **caería por debajo del 38%**, no subiría.

El margen para "el mercado sube con mala noticia" es minúsculo: de 264 negativas, solo **11 (4%) subieron de verdad**. Un sesgo optimista pelearía por acertar esos 11 mientras arruina los 253 que cayeron. Trade-off pésimo.

## 4. La palanca correcta (la opuesta)

Hacer que el enjambre **tome en serio las malas noticias**: que una señal negativa de los líderes se traduzca de forma fiable en un precio a la baja, en vez de ser ahogada por la compra de fondo.

- **Techo del margen:** de 38% hacia ~90%+ en negativas (el mercado cae el 96% de las veces ante mala noticia). **Es la palanca más grande de todo el proyecto.**
- **Dos sospechosos de la causa raíz** (a investigar):
  1. **Presión compradora de fondo demasiado fuerte** (FondoPasivo + BuyAndHold + arbitraje) que domina sobre la señal de la noticia. → El enjambre "deriva hacia arriba" pase lo que pase.
  2. **Señal de los líderes demasiado débil o diluida** por los arquetipos optimistas (Optimista, Contrarian, Value) que emiten señales no-negativas incluso con malas noticias.

## 5. Lo que NO puedo hacer en esta sesión (y cómo medirlo de verdad)

El 38% se mide con la **ruta LLM** (los cerebros leen el titular real). En esta sesión **no hay API key**, así que no puedo re-rendir los 645 exámenes para medir el efecto de un cambio. Cualquier A/B con "sentimiento aleatorio por categoría" (como proponía el PASO 4) mide algo desconectado del 38% real y daría un número engañoso — por eso no lo corrí.

**La medición real** tiene que correr en CI con la API key (`backtest.yml` / `engine/contenido/backtest.py`). El flujo honesto:
1. Implementar la palanca correcta (reforzar el peso de la mala noticia en la formación del precio, o atenuar la compra de fondo ante señal negativa fuerte).
2. Validar hechos estilizados aquí (gratis).
3. Medir el acierto real en CI con el LLM.

## 6. Recomendación

- ❌ **Descartar el Sprint 2.2** (sesgo optimista): la evidencia muestra que va al revés.
- ✅ **Abrir el Sprint 2.2-invertido:** investigar y corregir el **sesgo alcista sistemático** del enjambre ante malas noticias. Es el mayor potencial de mejora (38% → ~90%+), y ataca la causa raíz real, no un síntoma.

**El valor de este diagnóstico:** en vez de construir el sesgo optimista y quemar una corrida de CI con LLM para descubrir que empeora, lo miramos en los datos que ya teníamos (gratis) y descubrimos que la intuición del sprint estaba invertida. Un día de trabajo ahorrado y, mejor aún, la palanca correcta identificada con evidencia.

---

*Análisis sobre `respaldo.casos_remotos()` (645 casos). Sin LLM, sin coste.
Motor y producción: sin cambios por este diagnóstico.*
