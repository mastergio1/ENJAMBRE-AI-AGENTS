# Guía paso a paso — del 57 % al MVP calibrado

Para: Giorgio  
Producto: El Enjambre (mercado sintético)  
Hoy: 3 de septiembre de 2026  
Producción: **no se toca** hasta el paso 6

Esto es lo que hay que hacer, en orden. Vos hacés los pasos de
**negocio y clave**. Yo hago el código y los exámenes.

---

## Foto de hoy (honesta)

El producto **ya corre**. Un usuario puede soltar un titular y ver
10.000 agentes. Eso no es el MVP de un mercado sintético creíble:
hoy, en índice+acción (275 casos limpios), acierta la dirección
**57 %** (una moneda) y grita **3 veces** de más. En vivo: 26 %
simulado vs 5 % real.

Sin calibrar, el lanzamiento enseña un juguete que se asusta solo.

---

## Paso 1 — Limpiar la nota  ✅ HECHO hoy

- El corrector ya no puntúa el primer ticker de una sopa.
  “Eli Lilly…” se compara con LLY, no con APP.
- Los cables de whales / most-searched / top-N no entran a la nota.
- Congelados **40** titulares de ajuste y **80** de hold-out.

No tocó producción. No gastó saldo. El 57 % sigue siendo 57 %.

---

## Paso 2 — Tu único trabajo ahora (10 minutos)

Los cerebros de producción leen con **Claude**. Desde acá no veo
esa clave. Sin ella no se puede examinar v1d (el oído nuevo).

Hacé **una** de estas dos cosas:

1. **Más rápido:** en el próximo mensaje de este chat, pegá la
   clave de Anthropic (empieza con `sk-ant-`). La uso para rendir
   y **no** la subo al repositorio ni a producción.
2. **Más prolijo:** Render → servicio `enjambre-motor` → Environment
   → confirmá que `ANTHROPIC_API_KEY` está y que hay saldo.
   Eso alimenta el producto en vivo. **No alcanza** para los
   exámenes de esta rama: para eso hace falta la opción 1
   o decirme “está en Render, corré los exámenes allá”
   (lo armamos en un disparo protegido por token).

Cuando esté, escribime: **“clave lista, corré el paso 3”**.

No cambies `main`. No subas volumen. No fusiones nada.

---

## Paso 3 — Examen chico del oído ✅ HECHO 4-sep. **No pasa.**

Ver [experimento-v1d.md](experimento-v1d.md). 12 vs 12, cerebros Claude.

Fed-en-pausa no se calló (4.6 % → 4.9 %) e inventó signos.
Lehman siguió gritando (bien). Target pasó de +42 % a +53 %.
No se enciende v1e. No se fusiona. Siguiente: campo `sorpresa` (paso 3b),
no el paquete del paso 4.

---

## Paso 4 — SALTADO (el 3 no pasó)

v1e (oído + zona muerta) no se mide. Si se juntan dos palancas
después de que una perdió, no se sabe nada.


---

## Paso 5 — El 70 % de verdad (yo, ~US$10–15)

Los **80 hold-out** congelados hoy. El enjambre no los usó para
inventar la hipótesis. Solo índice + acción. Solo cerebros IA.

Se declara listo **solo si** en esos 80:

| Meta | Número |
|---|---|
| Dirección | ≥ 70 % y el piso de Wilson ≥ ~60 % |
| Fuerza | ≥ 0.70 (ni la mitad ni el triple) |
| Dentro de ±30 % del real | ≥ 40 % |
| Hechos estilizados | siguen pasando |
| El muro en vivo | ya no hace 26 % vs 5 % |

Un 8/12 no lanza la startup.

---

## Paso 6 — Lanzar o no

- Si el paso 5 pasa: se fusiona a `main`, se enciende en Render,
  el MVP se puede mostrar. Calibrado.
- Si no pasa: el producto sigue en baseline (el de hoy). Se diseña
  la siguiente palanca de oído (campo `sorpresa` en el JSON).
  **No se lanza** un mercado sintético que es una moneda.

---

## Lo que no vas a hacer, aunque apure

- Fusionar a `main` “para ver cómo se siente”
- Subir el volumen (ya se midió: infla días chicos)
- Meter más FOMO / más influencers
- Fijar el precio a mano (se rompe el mercado emergente)
- Declarar 70 % con menos de 80 hold-out

---

## Qué me escribís, según el momento

| Vos escribís | Yo hago |
|---|---|
| `clave lista, corré el paso 3` | Examen v1d, te traigo el veredicto |
| `paso 3 pasó, seguí` | Paso 4, después 5 |
| `no toques producción` | No toco `main` (ya es la regla) |

Hoy el siguiente movimiento es el **paso 2**. Sin clave no hay
calibración nueva. El código del oído ya está, apagado.

*Rubicón Lab · guía operativa · 3 sep 2026*
