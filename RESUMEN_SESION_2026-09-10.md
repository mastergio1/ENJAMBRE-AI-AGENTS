# Resumen de la sesión — 9–10 septiembre 2026

*Para Giorgio, en simple. Qué hicimos, qué salió, y cómo quedó todo.*

---

## Resumen en un párrafo

Arreglamos una deuda vieja de realismo del mercado (la "inercia" del precio),
descubrimos y reparamos que **medio panel de control estaba desconectado** (las
perillas no hacían nada), pusimos un guardián para que no vuelva a pasar,
sincronizamos la documentación, y desplegamos todo. Después, con saldo de IA,
fuimos a atacar el **acierto** del enjambre: comprobamos que en **acciones
individuales no hay nada que rascar** (piso estructural), pero encontramos un
**gol real en índice** — el arreglo del "influencer optimista" subió el acierto
leyendo malas noticias de **38% a ~54–59%**, medido con IA real y ya desplegado.
Gastamos ~$19 de saldo; quedan ~$16.

---

## Lo que hicimos, bloque por bloque

### 1. Arreglamos el "arrastre" del precio (gratis) ✅
El precio del simulador tenía demasiada **inercia**: un latido empujaba al
siguiente más de lo que pasa en un mercado real. Era una deuda marcada como
pendiente en los tests.

- **Causa encontrada:** el agente que existe para deshacer esa inercia (el
  arbitrajista) estaba desnutrido.
- **Arreglo:** lo reforzamos + afinamos al quant y al FOMO.
- **Resultado:** inercia media **0.14 → 0.02** (dentro de lo real), sin romper
  ninguna otra huella de mercado. Batería de realismo **9/9**.
- Informe: `RESULTADO_PASO_A_ARRASTRE.md`.

### 2. Hicimos el "panel de control" honesto (gratis) ✅
Descubrimos que **17 perillas** de la configuración estaban **muertas**: existían
en el archivo pero el código las ignoraba y usaba valores fijos por dentro.
Girarlas no hacía nada (me costó 3 mediciones a ciegas darme cuenta).

- **Arreglo:** enchufamos las 17 al código, con el valor por defecto = el que ya
  usaban → **cero cambio de comportamiento**, pero ahora cada perilla sí funciona.
- Corregimos la única mentira real (el ruido de fondo decía 0.05, corría a 0.12).
- **Guardián nuevo:** un test que **falla si alguien vuelve a dejar una perilla
  desconectada**. El problema no puede repetirse.
- Informe: `RESULTADO_PASO_B_AUDITORIA_CONFIG.md`.

### 3. Sincronizamos la biblia (`CLAUDE.md`) (gratis) ✅
El documento maestro tenía datos desactualizados. Le agregamos una "nota de
calibración" honesta con lo que de verdad hace el motor hoy.

### 4. Desplegamos todo ✅
Pasamos los cambios a `main` → Render los tomó. Verificamos que el motor corre el
código nuevo (`/salud` muestra la versión correcta). **El link público quedó
funcionando:** https://enjambre-ai-agents.vercel.app

### 5. Atacamos el acierto con IA (Paso C) — el trabajo con saldo

**Acción (mercado de acciones individuales):**
- ¿El "doomer" ayuda? → **No.** Lo empeora un poco. No lo activamos.
- ¿El arreglo del optimista ayuda? → **No significativo** (0.1974 → 0.2237). El
  fantasma inicial de 0.32 era suerte del muestreo chico.
- **Conclusión:** acción está en su **piso** (~0.22). Es idiosincrático: la
  dirección de una acción tras una noticia **no está en el texto**.

**Descubrimiento clave a mitad de camino:** la caché de la IA se guarda sin el
prompt, así que las mediciones devolvían respuestas **viejas**. Agregamos un
interruptor (`refrescar`) para forzar respuestas frescas solo durante una
medición. Sin esto, no se podía medir ningún cambio de prompt.

**Índice (mercado amplio) — EL GOL:**

| Índice, malas noticias | Antes | Ahora | Cambio |
|---|---|---|---|
| Aislado (solo optimista) | 0.38 | **0.544** | **+16 pts** (3 sigma) |
| Producción (optimista + doomer) | ~0.456 | **0.587** | **+13 pts** |

- El arreglo del optimista **subió el acierto leyendo caídas del mercado amplio**,
  de forma **grande y estadísticamente sólida**, y **ya desplegada**.
- Costo: las buenas noticias bajaron un poco (0.76→0.63) — tradeoff de ser menos
  alcista. Global de índice: 0.55 → 0.588.
- **Hallazgo bonus:** el doomer quedó **redundante** en índice (el optimista ya
  hace su trabajo). Se puede simplificar más adelante — medible gratis.
- Informe: `INFORME_TIRO_INDICE.md`.

---

## El gasto (saldo de IA)

| Concepto | Costo |
|---|---|
| Medición de acción (caché caliente) | ~$0.08 |
| Tiro a índice (respuestas frescas) | ~$19 |
| **Total gastado hoy** | **~$19** |
| **Saldo restante** | **~$16** |

---

## Cómo quedó todo (estado actual)

- ✅ **Motor desplegado y vivo**, corriendo el arrastre arreglado + panel honesto
  + guardián + interruptor de caché.
- ✅ **El producto en la web ya lee mejor las malas noticias del mercado amplio**
  (el arreglo del optimista está en producción).
- ✅ Realismo intacto (hechos estilizados 9/9).
- ✅ Todo commiteado y pusheado. Los **informes** de hoy quedaron en la rama de
  trabajo (son texto, no afectan el producto); el **código** está en `main`.

---

## Pendientes anotados (para más tarde, baratos)

En `OBSERVACIONES_PENDIENTES.md`:
1. **La manada queda en "0 compras" en los crashes** — un poco binario, revisar si
   pasa siempre (gratis).
2. **Lenguaje imperativo del influencer FOMO vs CMF** — "protejan su dinero YA"
   podría necesitar mirada legal.
3. **El doomer redundante en índice** — confirmar y quizás simplificar (gratis con
   la caché ya fresca).

---

## Mi recomendación honesta

**Parar aquí el gasto en acierto.** Extrajimos el gol grande disponible (índice).
Más allá es techo estructural: El Enjambre es un **simulador / focus-group**, no
un predictor — su valor está en el **realismo** y la **experiencia**, no en
adivinar la dirección. Hoy mejoramos ambas cosas y guardamos ~$16 para lo que de
verdad haga falta.

---
*Rubicón Lab · El Enjambre · Sesión 2026-09-10*
