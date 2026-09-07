# Intervención 1 (voz doomer) — resultado, hallazgo estructural y recomendación

**Fecha:** 7 de septiembre de 2026
**Para:** Giorgio (Rubicón Lab)
**En una línea:** la voz doomer **falla de forma contundente y reveladora**: hacer el tono más bajista **destruye** el acierto en negativas (lo contrario del objetivo). El porqué es el hallazgo más valioso de toda la investigación: **el problema de las negativas es en parte intrínseco al realismo del modelo.**

---

## 1. Qué se probó

Una voz "doomer pura" (fiel, que NO invierte) mezclada en el consenso con peso `peso_doomer`, para contrarrestar el sesgo alcista de los invertidores. Medido con el LLM real sobre los 163 exámenes de índice, sobre la producción actual (Plan A a 0.35).

## 2. Resultado (índice, 163 exámenes)

| Config | Negativas (81) | Positivas (69) | Global |
|---|---|---|---|
| base cruda (sin nada) | 44 = 54.3% | 50 = 72.5% | 62.6% |
| **Plan A 0.35** (producción) | **47 = 58.0%** | 48 = 69.6% | **63.2%** |
| **Plan A + doomer 0.2** | **42 = 51.9%** | 52 = 75.4% | 62.0% |

**El doomer:**
- **Negativas: −6.2 pts** (58.0% → 51.9%) — peor incluso que la base cruda. **Catastrófico.**
- Positivas: +5.8 pts (69.6% → 75.4%).
- Global: −1.2 pts.

El criterio pedía negativas **≥ +5 pts**. El doomer las manda a **−6 pts**. **Falla, y en la dirección contraria.**

## 3. El hallazgo estructural (lo importante)

El doomer hace justo lo opuesto de lo esperado: **intercambia negativas por positivas.** ¿Por qué añadir una voz bajista empeora el acierto en malas noticias?

**Por las dinámicas de rebote del propio mercado.** El modelo está DISEÑADO para sobre-reaccionar y rebotar — es el **hecho estilizado #5** de CLAUDE.md, obligatorio para el realismo: *"ante una noticia fuertemente negativa, el precio debe caer → sobre-reaccionar → rebotar parcialmente."*

Cuando el doomer empuja el tono **demasiado** bajista, el enjambre **cae fuerte y rebota más allá del punto de partida** → termina en positivo sobre una caída real → **falla la negativa.** Cuanto más bajista el tono, más rebotes de estos, más falsos positivos en negativas.

**La consecuencia es profunda:** hay una **tensión intrínseca** entre dos cosas que ambas queremos:
- El **realismo** (sobre-reacción y rebote, hecho estilizado #5).
- El **acierto de dirección en negativas** (que no rebote hasta cruzar a positivo).

**No se pueden maximizar las dos a la vez.** El ~54-58% de acierto en negativas no es (solo) un bug a corregir con más pesimismo: es en buena parte el **precio del realismo** que el modelo tiene por diseño. Empujar el tono más bajista pelea contra ese realismo y **pierde**.

Por eso el Plan A funcionó (modesto) y el doomer no: el Plan A es **quirúrgico y acotado** (solo dispara cuando el consenso ya es claramente bajista, y toma el mínimo — un empujón puntual). El doomer mezcla 20% de bajismo en **todas** las noticias, encima del Plan A → **doble empujón** → sobre-corrección → rebotes → negativas destruidas.

## 4. Recomendación honesta

**Archivar la Intervención 1.** No sirve en ningún peso; el mecanismo empeora lo que quiere arreglar.

**NO recomiendo pasar a la Intervención 2 tal como está escrita.** La Intervención 2 propone ponderar al doomer **AÚN MÁS** en mercados bajistas — es decir, **más** del mismo empujón bajista justo donde ya vimos que la sobre-corrección hace daño. Muy probablemente **falle igual o peor.** El diagnóstico de esta intervención dice que "más tono bajista" no es el camino.

**Lo que sí propondría** (otra misión, cuando quieras): dejar de pelear con el tono y aceptar que:
- **El Plan A (0.35) ya es el mejor lever de tono** que vamos a sacar — modesto pero real (+0.6 global), y se queda activo.
- El techo de negativas es en parte **estructural** (el realismo del rebote). Subirlo de verdad requeriría tocar las **dinámicas de mercado** (la magnitud/timing del rebote en cripto/índice) — un cambio de calibración profundo, con el riesgo de romper el hecho estilizado #5. Es un proyecto grande, no una perilla.
- O bien **replantear la métrica**: quizá el valor del producto no está en clavar la dirección de cada caída (imposible sin perder realismo), sino en el **rango y la volatilidad** que el enjambre sí estima bien.

## 5. Estado de producción

- La voz doomer quedó **dormida** (`peso_doomer = 0.0` en `main` y Render) → **cero efecto en vivo.** Producción sigue con **Plan A 0.35 + P3 + P4**, que es la mejor configuración medida.
- No hay nada que revertir. El código del doomer queda inerte y reversible (env `ENJAMBRE_PESO_DOOMER`), por si un rediseño futuro lo aprovecha de otra forma.

## 6. El mapa completo de intentos sobre las negativas

| Intento | Idea | Resultado |
|---|---|---|
| Freno manada | frenar cascadas de pánico | neutral en dirección |
| P1 (léxico) | oír mejor las malas noticias | mejoró la lectura, no el acierto final |
| P2 (silenciar invertidores) | quitar voces que diluyen | net-negativo, archivado |
| **Plan A (0.35)** | corregir el tono, quirúrgico | **+0.6 global · ACTIVO** |
| **Intervención 1 (doomer)** | añadir voz bajista incondicional | **negativas −6 · archivada** |

El patrón es claro: **los levers de tono ya dieron lo que podían dar (Plan A).** El resto del problema de negativas vive en la capa de dinámicas de mercado, no en el tono.

---

*Mediciones: workflow "Evaluar acierto (P2)" → `/api/evaluar` (Render, LLM real), runs #74-#80. Plan A: `INFORME_PLAN_A.md`. Diagnóstico: `INFORME_CAUSA_RAIZ_NEGATIVAS.md`.*
