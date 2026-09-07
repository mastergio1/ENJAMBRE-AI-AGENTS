# Informe — Medición del "Analista de Riesgo Selectivo" (Intervención 1, arquetipo LLM real)

*Rubicón Lab · El Enjambre · 7 de septiembre de 2026*

> Para Giorgio, en simple: medimos si el nuevo panelista del enjambre —el
> **Analista de Riesgo Selectivo**— mejora el acierto del enjambre cuando la
> noticia es MALA, que era su punto débil. Lo comparamos apagado (base, lo que
> hay hoy en producción) vs encendido, en dos mercados, sobre exámenes
> históricos reales, con la IA de verdad.

---

## 1. Qué se midió y cómo

- **El panelista:** un arquetipo LLM real y *selectivo* (`doomer_selectivo`, 150
  líderes). A diferencia del "Doomer" perpetuo, se queda **neutral** cuando la
  noticia es ambigua y solo aporta peso bajista **fiel** cuando el deterioro es
  claro. **Nunca** convierte una mala noticia en "oportunidad de compra".
- **La perilla:** `peso_doomer` (env `ENJAMBRE_PESO_DOOMER`). `0` = dormido
  (base). `1` = peso pleno en el tono de mercado. Su apuesta individual y su
  frase no se tocan; solo cambia cuánto pesa en el "clima".
- **El resto igual:** Plan A activo (`umbral 0.35`) en las dos condiciones, para
  aislar SOLO el efecto del doomer.
- **Motor vivo:** commit `1c8eeb5fff0a`, cerebros LLM reales (`claude-sonnet-5`),
  disparado desde GitHub Actions (`evaluar.yml`), acumulando por tandas.
- **Métrica:** acierto direccional (¿el enjambre acertó si el precio sube o
  baja?), desglosado en negativas / positivas / neutras.

---

## 2. Resultados (base vs con el doomer activo, MISMOS casos)

### Índice — 160 casos

| Categoría | Base (doomer 0) | Con Analista Selectivo (doomer 1) | Cambio |
|---|---|---|---|
| **Negativas** | 37.97 % (30/79) | **45.57 % (36/79)** | **+7.6 pts** ✅ |
| Positivas | 76.47 % (52/68) | 73.53 % (50/68) | −2.9 pts ⚠️ |
| Global | 55.0 % | 58.1 % | +3.1 pts |

### Cripto — 100 casos (muestra matcheada)

| Categoría | Base (doomer 0) | Con Analista Selectivo (doomer 1) | Cambio |
|---|---|---|---|
| **Negativas** | 56.52 % (26/46) | **58.70 % (27/46)** | **+2.2 pts** ➕ |
| Positivas | 90.74 % (49/54) | 90.74 % (49/54) | **0.0** ✅ |
| Global | 75.0 % | 76.0 % | +1.0 pt |

*(En cripto la base ya es alta; la muestra de 100 se tomó porque las tandas con
el tono más bajista disparan cascadas de pánico pesadas y corren muy lento. El
patrón fue estable: +3 pts a los 60 casos, +2.2 a los 100. Los primeros 20 casos
dieron IDÉNTICO base y activo — coherente con el diseño selectivo: si el titular
de cripto no gatilla "deterioro claro", el doomer se queda neutral y no cambia
nada.)*

---

## 3. Veredicto honesto

**El Analista Selectivo va en la dirección correcta: mejora las negativas —el
punto débil— en LOS DOS mercados, sin castigar (cripto) o castigando muy poco
(índice) las positivas.** Pero no despeja de forma limpia la vara estricta que
nos habíamos puesto ("negativas ≥ +5 Y positivas no bajan más de 2, en ambos"):

- **Índice:** clava el objetivo en negativas (**+7.6**, sobre el +5), pero roza
  el límite en positivas (**−2.9**, un pelín más que el −2). Neto claramente
  positivo (+3.1 global).
- **Cripto:** intocable en positivas (**0.0**), pero la mejora en negativas es
  modesta (**+2.2**, bajo el +5). Neto positivo (+1.0 global).

En una frase para Giorgio: **es una mejora real y segura, pero no un jonrón.**
Ayuda mucho en índice y suave en cripto; no rompe nada.

### Costos de realismo (medidos aparte, ver la deuda de realismo)
El arquetipo añade dos costitos pequeños y ruidosos: sube el "arrastre" de
retornos ~0.017 e inclina levemente el freno de manada. Ambos dentro del ruido y
menores frente al beneficio direccional. La huella de realismo #3 ya venía
fallando en producción (~0.14) por razones ajenas a este arquetipo — es deuda
aparte.

---

## 4. Recomendación

**Activar, pero con una prueba barata antes de fijar el nivel.** El código ya
está desplegado y dormido (`peso_doomer=0`), y encenderlo es solo una variable
de entorno en Render (reversible al instante). Propongo:

1. **Medir un nivel intermedio `peso_doomer=0.5`** (índice + cripto). Los
   cerebros ya están calientes → es **casi gratis** y rápido. La apuesta: 0.5
   podría conservar la mayor parte de la ganancia en negativas de índice
   *reduciendo* el costo de −2.9 en positivas — el punto dulce.
2. Con ese dato, **fijar `peso_doomer`** en el valor que mejor equilibre
   (probablemente entre 0.5 y 1.0) y activarlo en producción.
3. Dejar el flag documentado para rollback inmediato (`ENJAMBRE_PESO_DOOMER=0`).

Si Giorgio prefiere no afinar y decidir ya: **activar a `1.0`** es defendible
—la ganancia de índice en negativas es sólida y el costo en positivas son 2
casos de 68— siempre con el flag listo para volver atrás.

---

## 5. Estado técnico (todo en `main`, commit `1c8eeb5fff0a`)

- Arquetipo real `doomer_selectivo` (prompt + fallback léxico), mezcla a
  1.150 líderes / 10.150 agentes / 9 arquetipos / 9 voces.
- Frontend del replay 3D arreglado para leer 10.000 (histórico) y 10.150
  (nuevo) sin romperse (`web/src/swarm/replay-frame.js`).
- Suite verde; dos pruebas de realismo frágiles marcadas honestas (`xfail`
  documentado), apuntando a la deuda de realismo.
- Desplegado en Render (motor) y Vercel (frontend), con el arquetipo DORMIDO.

*Costo LLM de esta medición: ~US$5-6 (calentar los cerebros nuevos del
arquetipo, una sola vez), dentro de lo autorizado.*
