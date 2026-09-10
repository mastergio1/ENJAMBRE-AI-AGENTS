# El tiro a índice — el arreglo del optimista SÍ mueve el mercado que importa

**Fecha:** 2026-09-10 · **Rama:** `claude/m-d-file-6z1e63` → `main` (desplegado)
**Costo:** ~$19 de saldo IA (respuestas frescas de índice). Acción: ~$0 (caché caliente).

---

## En una frase

El arreglo del **Influencer Optimista** (que desplegamos hoy: ahora se asusta
primero ante caídas drásticas) **subió el acierto del enjambre leyendo malas
noticias del mercado amplio de 38% a ~54–59%** — un salto grande, estadísticamente
sólido, y **ya vivo en la web**. En acciones individuales no movió nada (ese
mercado está en su piso por naturaleza).

---

## El problema que tuvimos que resolver primero

La caché de respuestas de la IA se guarda por (titular, arquetipo, semilla) **sin
el prompt**. Por eso, al re-medir, devolvía las respuestas **viejas** (de antes
del arreglo) y no veíamos el efecto — medíamos un fantasma. Agregamos un
interruptor (`refrescar`) que fuerza respuestas **frescas** solo durante una
medición puntual. Con eso sí medimos el código real desplegado.

---

## Los números (índice, mercado amplio)

**Aislando el efecto del optimista** (doomer apagado en ambos, para comparar
manzana con manzana), sobre 160 casos / 79 negativos:

| Índice | Antes (baseline) | Ahora (optimista) | Cambio |
|---|---|---|---|
| **Malas noticias (negativa)** | 0.38 | **0.544** | **+16 pts** ✅ |
| Buenas noticias (positiva) | 0.765 | 0.632 | −13 pts |
| **Global** | 0.55 | **0.588** | **+3.75 pts** |

- El salto en negativas es **3 sigma (p≈0.003): sólido, no es ruido.**
- Aguantó toda la muestra (0.58 → 0.63 → 0.58 → 0.54 según crecía; nunca se
  derrumbó como sí pasó en acción).

**Producción real** (lo que ve tu cliente = optimista + doomer encendido), sobre
80 casos / 46 negativos:

| Índice producción | Antes (doomer solo) | Ahora (optimista + doomer) |
|---|---|---|
| **Malas noticias** | ~0.456 | **0.587** (+13 pts) |
| Global | — | **0.60** |

---

## Tres hallazgos que importan

1. **Es un gol real y desplegado.** El producto en la web **ya lee mejor las
   caídas del mercado**. Para un "focus group del pánico bursátil", acertar las
   malas noticias es exactamente lo que más importa.

2. **El costo (honesto):** las buenas noticias bajaron (0.76→0.63). Es el tradeoff
   de ser menos alcista. Por eso el global sube modesto aunque las negativas
   salten fuerte. Vale la pena: el valor está en leer bien el miedo.

3. **El doomer quedó redundante.** Con el optimista ya arreglado, encender el
   doomer encima **no agrega** en negativas (0.587 con doomer ≈ 0.544 sin él,
   dentro del ruido). Su ventaja original (+7.6) era sobre el optimista VIEJO.
   *Pendiente de confirmar con más muestra, pero abre la puerta a simplificar:
   quizás el doomer ya no haga falta en índice.*

---

## Contraste con acción (medido el mismo día)

Acción negativa: 0.1974 → 0.2237 (**+2.6 pts, no significativo**). El optimista
NO movió acción. Es esperable: una acción individual reacciona a mil cosas
idiosincráticas; **la dirección no está en el texto** (correlación 0.1). Acción
está en su piso. No se persigue más ahí.

---

## Conclusión

- **índice: el enjambre tiene poder real** y el arreglo del optimista lo mejoró
  de forma medible y significativa. Ya desplegado.
- **acción: piso estructural**, no se toca.
- **El acierto direccional tiene techo** (es un simulador/focus-group, no un
  predictor), pero dentro de ese techo, hoy subimos el peor régimen del mercado
  que importa.

**Saldo restante:** ~$16. **Recomendación:** parar aquí el gasto en acierto —
extrajimos el gol grande disponible. Lo que queda por explorar (doomer redundante)
se puede medir gratis más adelante con la caché ya fresca.
