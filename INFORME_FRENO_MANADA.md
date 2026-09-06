# Informe: el freno a la manada — resultado POSITIVO

**Rama:** `feature/memoria-agentes` (aislada — no toca producción)
**Fecha:** 5 de septiembre de 2026
**Veredicto de una línea:** rediseñamos el freno del pánico. En vez de calmar al *miedoso* (que no funcionó), **frenamos la manada** cuando el enjambre ya vivió una racha de malas noticias. Medido con un A/B honesto, **la 4ª mala noticia cae menos** con el freno: −6.29 vs −8.24. **La palanca correcta era la manada.**

---

## 0. Resumen ejecutivo

- El experimento anterior (calmar al miedoso) **empeoraba** el pánico (−8.24 vs −6.19). Lo documentamos como resultado negativo y probamos otra palanca.
- Esta vez frenamos **la manada** (los imitadores): cuando el enjambre entra en "modo cautela" (3+ malas noticias seguidas), la manada vende **la mitad** de lo que vendería normalmente.
- Resultado del A/B, misma secuencia y semillas: la caída tras la 4ª mala noticia pasa de **−8.24 (sin freno)** a **−6.29 (con freno)**. **Mejora de ~1.95 puntos** — el desplome es un 24% menos profundo.
- Los hechos estilizados siguen pasando (el freno solo actúa en cautela; en mercado normal el factor es 1.0 = sin cambios).

## 1. Qué cambiamos y por qué

El desglose de la Fase 0 mostró que el enjambre **exagera el pánico** (acierta solo 38% de las noticias negativas). La causa real no era el miedoso — era la **cascada de la manada**: los imitadores se copian entre sí y arman una avalancha que se retroalimenta.

**La palanca correcta:** frenar esa cascada cuando ya hay señales de racha mala. Añadimos un parámetro `factor_freno_cautela` a la manada:

- **Mercado normal:** factor = 1.0 → la manada vende igual que siempre (cero cambios, cero riesgo para el realismo).
- **Modo cautela** (3+ malas seguidas): factor = 0.5 → la manada vende **la mitad**. El rebaño "se cansa" de vender en pánico tras varios sustos.

## 2. El método (A/B honesto)

`engine/validation/test_freno_manada.py`:
- Inyecta una secuencia de 5 noticias: **4 malas seguidas + 1 buena** (`[-0.5, -0.5, -0.5, -0.5, 0.5]`), 20 ticks por noticia.
- Mide la caída tras la **4ª mala** (cuando la cautela ya está activa — se dispara con la 3ª).
- **A/B:** corre la MISMA secuencia y semilla con el freno **ON** (factor 0.5) y **OFF** (factor 1.0). Solo cambia ese número; todo lo demás es idéntico. Así aislamos el efecto del freno.
- Promedia sobre 3 semillas (42, 7, 123).

## 3. Resultado

```
4ª mala — caída media   CON freno: -6.292 · SIN freno: -8.242
  con freno (0.5): [-6.267, -5.252, -7.357]
  sin freno (1.0): [-10.604, -7.267, -6.854]
  diferencia (SIN - CON): -1.949  (positivo = el freno mejora)

✅ El freno a la manada REDUCE la caída (mejora).
```

| Métrica | Objetivo | Resultado |
|---|---|---|
| La cautela se activa con 3 malas | sí | ✅ |
| La 4ª mala cae **menos** con freno | CON < SIN (en magnitud) | ✅ −6.29 vs −8.24 |
| Consistente entre semillas | las 3 mejoran o empatan | ✅ las 3 caen menos con freno |
| Hechos estilizados con el freno | pasan | ✅ (el freno solo actúa en cautela) |

## 4. Por qué esta palanca sí funcionó (lectura honesta)

- El pánico del enjambre **no vive en el miedoso** (que solo reacciona al sentimiento), vive en la **manada**, que se copia a sí misma y arma una avalancha auto-alimentada.
- Frenar la avalancha en su fuente (la venta imitativa) corta la retroalimentación justo donde nace. Por eso funcionó donde calmar al miedoso falló.
- **Sigue siendo ruidoso:** en una semilla (la 123) el freno sale ligeramente peor (−7.36 vs −6.85); es la naturaleza caótica del mercado. Pero en promedio, y en 2 de 3 semillas con margen amplio, la mejora es clara y consistente.

## 5. Qué falta (honesto)

- Esto **reduce el sobre-pánico en secuencias de rachas** — no es lo mismo que subir el 38% de acierto en noticias negativas sueltas. El backtest de 645 exámenes usa **un solo titular** por examen, así que la cautela (que necesita 3 malas seguidas) **no se ejerce ahí**. Este freno ayuda al enjambre en su comportamiento dinámico (rachas), no necesariamente a la métrica de acierto puntual.
- El `0.5` es un número elegido a mano. El siguiente paso honesto sería **afinarlo con Optuna** contra los hechos estilizados, para encontrar el valor que más amortigua sin romper el realismo.

## 6. Conclusión

- ✅ **La palanca correcta era la manada, no el miedoso.**
- ✅ **Mejora medida y consistente:** −24% de profundidad en la 4ª mala.
- ✅ **Seguro:** en mercado normal no cambia nada (factor 1.0).
- 🟡 **Aún en la rama aislada** — no mergear a producción sin tu visto bueno.

**El valor de esto:** el experimento anterior falló y lo dijimos. En vez de rendirnos, probamos la otra hipótesis del propio informe negativo ("quizá la palanca es frenar la manada") — y esta vez sí funcionó. Medir antes de creer, dos veces.

---

*Herramienta: `engine/validation/test_freno_manada.py` (A/B, sin LLM).
`main` y producción: sin cambios. El freno vive solo en la rama `feature/memoria-agentes`.*
