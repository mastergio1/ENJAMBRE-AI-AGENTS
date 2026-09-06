# P3 + P4 — qué hice, hallazgos y cómo quedó

**Fecha:** 6 de septiembre de 2026
**Para:** Giorgio (Rubicón Lab)
**En una línea:** implementé dos mejoras incrementales sobre el Plan A — **acotar las magnitudes exageradas de cripto** (P3) y **mostrar la confianza del enjambre** en cada lectura (P4) — sin tocar el comportamiento ni el acierto. Ambas están **fusionadas a `main`**; falta solo tu deploy en Render + Vercel.

---

## 1. P3 — Acotar magnitudes absurdas en cripto

### El problema
En cripto (y acciones individuales) el enjambre a veces emerge con movimientos **irreales** — ±40-50% en una sesión — por su alta volatilidad de masas. El número asusta y resta credibilidad, aunque la **dirección** sea correcta.

### Qué hice
- En `engine/model.py`: un diccionario `FACTORES_LIQUIDEZ` con un **tope de magnitud por tipo de mercado** (cripto **±30%**, acción **±40%**; índice sin tope, es la base de calibración) y una función `acotar_magnitud()`.
- En `engine/server.py` (`_generar_reporte`): el tope se aplica a `direccion_pct`, `minimo_pct` y `maximo_pct`.

### Hallazgo importante (adaptación honesta)
Tu plan pedía el diccionario **por símbolo** (BTC, ETH…). Pero al revisar el código descubrí que **el flujo en vivo NO conoce el símbolo puntual**: el usuario escribe un titular, y el enjambre lo clasifica por **tipo de mercado** (índice/acción/cripto) con una llamada barata a la IA — nunca resuelve "esto es BTC". Así que un diccionario por símbolo casi nunca dispararía en vivo.

Lo adapté a **tope por tipo de mercado**, que es lo que sí se conoce en el reporte y logra el objetivo. (Mismo criterio que ya usa el motor para su personalidad de mercado: sensibilidad y volatilidad son por tipo, no por símbolo.)

### Por qué NO cambia el acierto
El tope es un **recorte (clamp)**, que **no puede voltear un signo**: un +45% topa a +30% (sigue positivo), un −52% a −30% (sigue negativo). Como el acierto de dirección mira solo el **signo**, es **idéntico por construcción matemática** — no hizo falta re-medir con el LLM para probarlo.

### Verificación
End-to-end: un titular de "Bitcoin crashes 40%…" emergió más grande y quedó topado a **−30%**, conservando el signo. Criterio cumplido ("no más de ±30% para la mayoría").

---

## 2. P4 — Confianza y segmentación

### Qué hice
- **Confianza:** el modelo ahora guarda la **fuerza del consenso** de la última noticia (`_ultimo_consenso`, en `_tono_de_titular`). El reporte expone `confianza = abs(consenso)` ∈ [0, 1]. El panel (`web/src/ui/panel.js`) la muestra como stat **"confianza %"**.
  - Interpretación: confianza alta = los líderes leyeron la noticia con convicción (consenso decidido); baja = noticia ambigua. En la prueba dio **0.87** para un titular claramente malo.
- **Segmentación por mercado:** **ya existía** — el reporte trae `mercado`/`mercado_etiqueta` y el panel muestra **"Mercado detectado · Cripto"**. Lo confirmé; no hubo que reconstruirlo.

### Hallazgo
La mitad de P4 ya estaba hecha (la segmentación). Lo genuinamente nuevo es la **confianza global**, que antes solo existía por líder ("convicción X%") y ahora también como número de conjunto.

---

## 3. Lo que NO se toca (y por qué es seguro)

- Ni P3 ni P4 tocan la **ruta numérica** (`aplicar_noticia`) que usan los hechos estilizados, ni el **tono** del mercado. Por eso el realismo del mercado y el **Plan A** quedan intactos.
- P3 solo cambia la **magnitud reportada** (no la simulación ni la dirección).
- P4 es **informativo** (lee el consenso ya calculado; no cambia ninguna decisión).

## 4. Tests

- `engine/validation/test_p3_p4.py` (7 tests): el tope conserva el signo y respeta cada mercado; el consenso se guarda; la confianza ∈ [0,1].
- Suite de servidor/contenido/backtest/evaluar (33 tests): en verde con el reporte cambiado.
- **Total: 40 tests verdes** + verificación end-to-end.

## 5. Estado de producción

- **Fusionado a `main`** (commit `dbf1669`), sobre el Plan A ya activo (umbral 0.35).
- **Falta tu deploy** para que quede vivo:
  1. **Render** (`enjambre-motor` → Manual Deploy → Deploy latest commit): activa el tope y la confianza en el reporte.
  2. **Vercel** (deploy de `web/`): hace **visible** la confianza en el panel. Si Vercel tiene auto-deploy desde `main`, se actualiza solo con el push.

## 6. Archivos que toqué

- `engine/model.py` — `FACTORES_LIQUIDEZ` + `acotar_magnitud()` (P3); guardado de `_ultimo_consenso` (P4).
- `engine/server.py` — `_generar_reporte` aplica el tope y expone `confianza`.
- `web/src/ui/panel.js` — muestra la confianza como stat.
- `engine/validation/test_p3_p4.py` — tests nuevos.

---

## Resumen de las tres mejoras de esta sesión

| Mejora | Qué hace | Efecto en el acierto | Estado |
|---|---|---|---|
| **Plan A** (umbral 0.35) | corrige el sesgo alcista del tono | índice **+0.6 pts global**; cripto inerte | ✅ activo (desplegado) |
| **P3** (topes) | acota magnitudes de cripto/acción | **ninguno** (solo el tamaño) | ✅ en `main`, falta deploy |
| **P4** (confianza) | muestra la fuerza del consenso | **ninguno** (informativo) | ✅ en `main`, falta deploy |

---

*Detalle del Plan A: `INFORME_PLAN_A.md` y `INFORME_PLAN_A_BITACORA.md`. Diagnóstico: `INFORME_CAUSA_RAIZ_NEGATIVAS.md`.*
