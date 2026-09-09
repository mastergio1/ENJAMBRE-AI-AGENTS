# Paso A — Arreglado el "arrastre" del precio

**Fecha:** 2026-09-09 · **Rama:** `claude/m-d-file-6z1e63` · **Commit:** `f452a14`
**Costo en crédito de IA:** $0 (todo con agentes de reglas, sin llamadas a la API)

---

## Qué es esto en simple

El **arrastre** es la "inercia" del precio: cuánto un latido del mercado empuja
al siguiente en la misma dirección. Un mercado de verdad casi no tiene inercia —
si subió este segundo, eso NO te dice si sube el próximo (si lo dijera, todos
ganarían plata fácil, y eso no existe). Nuestro simulador tenía **demasiada
inercia**: media 0.14 cuando lo real es por debajo de 0.10. Era una "deuda"
que veníamos arrastrando (el test la tenía marcada como pendiente).

**Ya está pagada.** Ahora la inercia es **0.02** de media — dentro de lo real —
y sin romper ninguna otra huella del mercado.

---

## El hallazgo importante (y algo incómodo)

Buscando el arreglo descubrí que **varios controles del panel no estaban
enchufados**. En el archivo de configuración (`agentes.json`) había perillas —
la ventana del quant, el umbral del arbitrajista, la memoria de la manada —
pero el código de esos agentes **ignoraba el archivo y usaba valores fijos por
dentro**. O sea: girabas la perilla y no pasaba nada. Perdí tres mediciones
girando perillas muertas hasta darme cuenta (salían idénticas al byte).

Lo dejé honesto: **enchufé el quant y el arbitrajista a su configuración**, así
el panel ya no miente. (Los otros parámetros muertos los dejé anotados; se
enchufan cuando haga falta.)

---

## Cómo se arregló

El **arbitrajista** es el agente cuyo trabajo es, justamente, deshacer la
inercia: cada latido corrige los empujones sin fundamento. Estaba **desnutrido**
—actuaba poco y corregía poco— así que la inercia sobrevivía. Le di fuerza:

| Agente | Antes | Ahora | Por qué |
|---|---|---|---|
| Arbitrajista — umbral | 0.006 | **0.004** | corrige antes |
| Arbitrajista — con qué frecuencia actúa | 80% de latidos | **90%** | más presente |
| Arbitrajista — cuánto corrige | hasta 0.25 | **hasta 0.4** | corrige más fuerte |
| Quant — ventana corta | 5 latidos | **8 latidos** | no persigue ruido tan corto |
| FOMO — umbral de entrada | 0.02 | **0.03** | entra menos por nada |
| FOMO — capital que mete | 20% | **15%** | empuja menos la ola |

Nada de esto toca la **ola visual** (el efecto estrella del producto): esa vive
en la red de influencia, y no la moví.

---

## El número, antes y después (12 semillas)

| | Arrastre media | Arrastre máx | Veredicto |
|---|---|---|---|
| Antes | ~0.14 | — | ❌ deuda |
| **Ahora** | **0.021** | **0.131** | ✅ pasa (objetivo <0.10 y <0.20) |

**Las otras huellas del mercado, intactas:**
- Colas gordas (curtosis): 5.1 — los extremos siguen ocurriendo más que en una campana ✅
- Racha de turbulencia (clustering): 0.30 — la volatilidad sigue viniendo a rachas ✅
- Asimetría de pánico: 1.44 — las caídas siguen siendo más violentas que las subidas ✅

**Batería completa de hechos estilizados: 9/9 pasan.** Quité el marcador de
"deuda" del test: ahora es un aprobado limpio.

---

## Qué NO hice (y por qué)

- **No relajé el examen para hacerlo pasar.** Eso hubiera sido trampa (el
  CLAUDE.md §7 lo prohíbe: se ajusta la mezcla, no el umbral). Se arregló de
  verdad.
- **No toqué la ola visual.** Bajar la inercia por ahí habría aplanado el
  efecto estrella; ni lo consideré.
- **No cambié las proporciones de la mezcla** (cuántos agentes de cada tipo).
  Solo afiné comportamientos.

---

## Dónde quedamos

- **Paso A (este): hecho y guardado.** ✅
- **Paso B — desplegar:** cuando tú digas, esto pasa a `main` y se sube a
  Render (acción tuya, sin crédito de IA).
- **Paso C — re-medir el sistema completo con IA:** requiere recarga (~$20-30).
  Te aviso cuando toque ese paso.
