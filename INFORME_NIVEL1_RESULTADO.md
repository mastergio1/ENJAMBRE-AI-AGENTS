# Informe: Nivel 1 (memoria) — validación en secuencias (resultado NEGATIVO)

**Rama:** `feature/memoria-agentes` (aislada — no toca producción)
**Fecha:** 5 de septiembre de 2026
**Veredicto de una línea:** el feature de memoria **es seguro** (no rompe los hechos estilizados) pero **NO cumple su propósito**: medido con un A/B honesto, **no amortigua el pánico — lo empeora**. No debe mergearse como "arreglo del pánico".

---

## 0. Resumen ejecutivo

- Construimos la memoria de agentes (Nivel 1) para que, ante una racha de 3+ malas noticias, el enjambre amortiguara su sobre-reacción al pánico (×0.7).
- La medición honesta (A/B: memoria ON vs OFF, misma secuencia y semillas) muestra lo **contrario**: con memoria, la caída tras la 4ª mala noticia es **más profunda** (−8.24) que sin ella (−6.19).
- El feature **no daña** el realismo (los 4 hechos estilizados siguen pasando), pero **no logra su objetivo**. Es un **resultado negativo bien medido**: valioso porque evita adoptar algo que no funciona.

## 1. Qué se quiso medir

El desglose de la Fase 0 mostró que el enjambre exagera el pánico (acierta solo 38% de las negativas). El Nivel 1 buscaba corregir eso: tras varias malas noticias seguidas, "desensibilizar" a los agentes emocionales (amortiguar ×0.7 su reacción a una nueva mala).

**Por qué el backtest no servía:** cada examen del backtest usa **un solo titular** (`aplicar_titular`), y la memoria/cautela necesita **3 malas seguidas** para activarse. El backtest jamás ejerce el feature. Por eso se construyó una validación **de secuencias**.

## 2. El método (A/B honesto)

`engine/validation/test_memoria_secuencias.py`:
- Inyecta una secuencia de 5 noticias: **4 malas seguidas + 1 buena** (`[-0.5, -0.5, -0.5, -0.5, 0.5]`), 20 ticks por noticia.
- Mide la caída de precio tras la **4ª mala** (cuando la cautela ya está activa — se dispara con la 3ª).
- **A/B:** corre la MISMA secuencia y semilla con la memoria **ON** y con la memoria **OFF** (desactivando solo `ajustar_por_contexto`), para **aislar** el efecto de la memoria de la acumulación del sentimiento.
- Promedia sobre 3 semillas (42, 7, 123).

> Por qué el test original del borrador no servía: comparaba "la 4ª caída vs la 3ª" en una sola corrida, lo que mezcla el efecto de la memoria con el decaimiento/acumulación del sentimiento del propio modelo. El A/B lo aísla.

## 3. Resultado

```
La cautela se activa con 3 malas (y no antes).           ✅

4ª mala — caída media   ON: -8.242 · OFF: -6.193
  por semilla ON : [-10.604, -7.267, -6.854]
  por semilla OFF: [ -6.024, -6.451, -6.104]
```

| Métrica | Objetivo | Resultado |
|---|---|---|
| La cautela se activa con 3 malas | sí | ✅ |
| La 4ª mala cae **menos** con memoria | ON < OFF (en magnitud) | ❌ ON cae **más** (−8.24 vs −6.19) |
| Hechos estilizados con memoria | pasan | ✅ (9 tests, validado aparte) |

## 4. Por qué falló (lectura honesta)

1. **Amortiguar al miedoso no basta.** Se bajó la reacción del miedoso (y del noise sensible) al sentimiento negativo, pero:
   - el **sentimiento acumulado** del modelo satura en −1 y persiste (decae lento), así que la presión bajista sigue;
   - la **manada** arma su cascada mirando a los **vecinos** (no al sentimiento), así que el desplome ocurre igual — solo que con otro *timing* que, en la ventana de 20 ticks, salió más profundo.
2. **La medición es intrínsecamente ruidosa.** En cuanto la memoria cambia UNA decisión, toda la trayectoria del mercado diverge (órdenes distintas, consumo de azar distinto). Con 3 semillas la varianza es grande (ON de −6.9 a −10.6). Aun así, la señal es clara: la memoria **no** amortigua; ni empata al OFF.

## 5. Conclusión y opciones

- ✅ **Seguro:** no rompe los hechos estilizados.
- ❌ **No cumple su propósito:** no amortigua el pánico (lo empeora, en esta medición).
- 🚫 **No mergear** como "arreglo del pánico/38%": sería vender algo que no funciona.

**Caminos honestos:**
1. **Rediseñar el mecanismo.** La palanca correcta quizá no es la percepción del miedoso, sino frenar la **cascada de la manada** en cautela, o atenuar el **sentimiento acumulado**. Se puede probar con el mismo A/B (gratis).
2. **Archivar el Nivel 1** como experimento documentado (resultado negativo). Válido y honesto.
3. **Investigar más** con más semillas y una medición aún más limpia (p. ej. medir el desplome acumulado de toda la secuencia, no solo la 4ª caída).

**El valor de esto:** medimos antes de creer. Construimos el feature, lo probamos con rigor, y demostró que **no hace lo que prometía**. Eso ahorra gastar saldo y evita un merge que habría prometido algo falso.

---

*Herramienta: `engine/validation/test_memoria_secuencias.py` (A/B, sin LLM).
Hechos estilizados: `test_hechos_estilizados.py` (9 passed). `main` y producción:
sin cambios. El feature vive solo en la rama `feature/memoria-agentes`.*
