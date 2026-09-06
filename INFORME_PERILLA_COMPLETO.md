# Todos los tests de la perilla P2 — resultados completos y mi opinión

**Fecha:** 6 de septiembre de 2026
**Para:** Giorgio (Rubicón Lab)
**Qué es esto:** el registro completo de TODOS los backtests que corrimos moviendo la perilla `peso_tono_invertidores` (P2), con el LLM real en Render, sobre los exámenes históricos respaldados. Incluye índice (4 posiciones de la perilla) y cripto (2 posiciones), el desglose por tanda, y mi opinión honesta al final.

---

## 1. Recordatorio de qué es la perilla (P2)

Tres tipos de líder —el **contrarian sabio**, el **quant escéptico** y el **optimista**— invierten la señal ante malas noticias (ven la caída como oportunidad). Eso está bien para su apuesta personal, pero al promediarlos **diluyen el ánimo colectivo** y el mercado no reacciona a la mala noticia. P2 los saca del "clima" (sin quitarles su apuesta). La perilla:

- **1.0** = como está hoy (P2 apagado, comportamiento histórico).
- **0.1** = un toque de P2.
- **0.3** = P2 medio.
- **0.0** = P2 pleno (invertidores fuera del clima del todo).

Todos los tests comparan la MISMA muestra y las MISMAS semillas cambiando solo la perilla, así que aíslan su efecto limpio.

---

## 2. Cuántos exámenes hay (respaldados)

- **645** casos respaldados en total · **609** categorizados (sabemos qué hizo el mercado real).
- **Índice: 163** (81 negativas, 69 positivas, 13 neutras) — barrido completo de 4 posiciones.
- **Cripto: 220** (89 negativas, 131 positivas, 0 neutras) — barrido de 2 posiciones (base y 0.1).
- (El resto: acción 188, petróleo 25, oro 13 — no se tocaron.)

---

## 3. ÍNDICE — barrido completo (163 exámenes)

| Perilla | Negativas (81) | Positivas (69) | Neutras (13) | Global (163) |
|---|---|---|---|---|
| **1.0** — actual | 44/81 = 54.3% | 50/69 = **72.5%** | 8/13 = 61.5% | 102/163 = 62.6% |
| **0.1** ⭐ | **47/81 = 58.0%** | 49/69 = 71.0% | 8/13 = 61.5% | **104/163 = 63.8%** |
| **0.3** | 44/81 = 54.3% | 48/69 = 69.6% | 7/13 = 53.8% | 99/163 = 60.7% |
| **0.0** | 45/81 = 55.6% | 46/69 = 66.7% | 6/13 = 46.2% | 97/163 = 59.5% |

**En índice, 0.1 fue el mejor:** negativas +3 aciertos, global +2, pagando solo −1 en positivas. **0.3 y 0.0 son peores que la base.** La curva no es monótona: un toque ayuda, más hace daño.

---

## 4. CRIPTO — barrido (220 exámenes)

| Perilla | Negativas (89) | Positivas (131) | Global (220) |
|---|---|---|---|
| **1.0** — actual | 46/89 = 51.7% | 109/131 = **83.2%** | 155/220 = **70.5%** |
| **0.1** | 47/89 = 52.8% | 105/131 = 80.2% | 152/220 = 69.1% |

**En cripto, 0.1 fue peor:** gana 1 negativa pero pierde **4 positivas** → global −3 aciertos. El intercambio es desfavorable.

*(Nota: en cripto el enjambre ya es muy bueno en positivas —83%— y flojo en negativas —52%—: el mismo sesgo alcista, más marcado. Y P2 justo castiga lo que hace bien.)*

---

## 5. El veredicto combinado — los dos mercados juntos (383 exámenes)

Aquí está la verdad, sumando índice + cripto (170 negativas, 200 positivas, 13 neutras):

| Perilla | Negativas (170) | Positivas (200) | Global (383) |
|---|---|---|---|
| **1.0** — actual | 90/170 = 52.9% | 159/200 = **79.5%** | 257/383 = **67.1%** |
| **0.1** | 94/170 = **55.3%** | 154/200 = 77.0% | 256/383 = 66.8% |

**P2 a 0.1 es un intercambio casi uno-a-uno:** sube las negativas ~2.4 puntos (+4 aciertos) pero baja las positivas ~2.5 puntos (−5 aciertos). El global queda **igual o un pelo peor** (−0.3 pts). **No hay almuerzo gratis.**

---

## 6. Cómo se desinfló la ilusión (por qué no basta la muestra chica)

Cada backtest se corrió en tandas de 40, acumulando. Mira cómo el mismo número miente al principio y dice la verdad al final:

**Índice 0.1 — negativas por tanda:** 40→58.3% · 80→58.7% · 120→54.8% · 160→57.0% · **163→58.0%**
**Cripto 0.1 — el intercambio por tanda (neg vs pos, comparado con base):**
| Casos | 0.1 negativas | 0.1 positivas | vs base |
|---|---|---|---|
| 40 | 70.4% | 76.9% | neg +1, pos = |
| 80 | 62.5% | 82.5% | neg +1, pos = |
| 120 | 56.6% | 82.1% | neg +1, pos = |
| 160 | 57.8% | 80.9% | neg +1, **pos −2** |
| 200 | 56.1% | 81.4% | neg +1, **pos −3** |
| **220** | **52.8%** | **80.2%** | **neg +1, pos −4** |

En cripto, hasta el caso 120 se veía "gratis" (ganaba negativas sin costar positivas). El costo en positivas apareció en la segunda mitad. **Exactamente el mismo espejismo que ya nos engañó dos veces** (la sonda de 18 casos y los primeros 40 del índice).

---

## 7. Historial de todas las mediciones de P2 (para que quede el rastro)

| # | Qué se midió | Muestra | Qué mostró | Qué resultó ser |
|---|---|---|---|---|
| 1 | Cripto sonda 0.0 vs 1.0 | 20 (18 neg) | +11 pts negativas | **espejismo** de muestra chica |
| 2 | Índice 0.0 vs 1.0 (primeros 40) | 40 | +12 pts negativas | **espejismo** |
| 3 | Índice 0.0 completo | 163 | net −3 pts global | P2 pleno = malo |
| 4 | Índice 0.3 completo | 163 | net −2 pts global | P2 medio = malo |
| 5 | Índice 0.1 completo | 163 | net +2 (dentro del ruido) | prometía, pero débil |
| 6 | Cripto 1.0 base completo | 220 | referencia 70.5% | — |
| 7 | Cripto 0.1 completo | 220 | net −3 pts global | mata la promesa del 0.1 |

---

## 8. Estado de producción

- `main`: P2 presente, perilla en **1.0** → cero cambio de comportamiento. **Nada que revertir** (la variable `ENJAMBRE_PESO_TONO_INVERSORES` nunca se fijó).
- El respaldo histórico y el comportamiento en vivo **nunca se tocaron** en todo el experimento.
- Presupuesto: se gastó ~$24 en calentar la caché de los 220 cripto (dentro de tu presupuesto de $48.66; los barridos de perilla fueron gratis).

---

## 9. Mi opinión (honesta)

**P2 no sirve para producción. La perilla se queda en 1.0. Lo archivo.**

Por qué, sin rodeos:

1. **No hay punto dulce.** Probamos cuatro valores (1.0, 0.1, 0.3, 0.0) en índice y dos (1.0, 0.1) en cripto. El único que parecía ayudar (0.1) resultó ser un **intercambio uno-a-uno**: cada negativa que gana la paga con una positiva que pierde. El global no mejora.

2. **La señal más grande fue ruido, dos veces.** Nos entusiasmó +11 puntos en 18 casos y +12 en 40 casos. Ambas se evaporaron al llegar a la muestra completa. Aprendimos la lección a tiempo: **nunca decidir con muestras chicas.**

3. **P2 castiga donde el enjambre ya es bueno.** En cripto acierta el 83% de las positivas; silenciar a los optimistas del clima justo rompe eso. Es como bajarle el volumen a lo que suena bien para intentar arreglar lo que suena mal, y no arregla nada.

4. **Pero el diagnóstico sigue siendo correcto.** El enjambre es demasiado optimista en negativas (~53% de acierto en las malas noticias, contra ~80% en las buenas). P2 apuntaba a la capa correcta —el tono del mercado— pero eligió la palanca equivocada (silenciar líderes). El problema real está en **cómo se forma el consenso y cómo el léxico lee las malas noticias**, no en quién participa del clima.

**Mi recomendación para el próximo paso** (otra misión, cuando quieras): en vez de *quitar* voces del clima, **corregir el sesgo alcista directamente** — que cuando el consenso de los líderes apunta claramente a la baja, el tono no se "suavice" hacia arriba. Eso ataca la causa (el optimismo estructural) sin sacrificar el acierto en positivas. Y se mide con la misma máquina que ya quedó lista, caliente y **gratis de correr** para índice y cripto.

Lo bueno de esta sesión: gastamos ~$24 y varias horas, pero **compramos certeza**. Ahora sabemos que P2 no es el camino, con datos de dos mercados y 383 exámenes — no con una corazonada. Eso vale más que activar algo que se veía bien y descubrir el bajón en producción.

---

*Mediciones: workflow "Evaluar acierto (P2)" → `/api/evaluar` (Render, LLM real), runs #17–#47.
Informes relacionados: `INFORME_P2_CIERRE.md`, `INFORME_BACKTEST_PERILLA.md`, `INFORME_CAUSA_RAIZ_NEGATIVAS.md`. Bitácora de la sesión: `INFORME_SESION_COMPLETA.md`.*
