# P2 + sistema de medición: informe completo

**Fecha:** 6 de septiembre de 2026
**Estado:** P2 en producción (neutro por defecto) · sistema de medición funcionando con LLM real · **primera señal POSITIVA** medida.
**Veredicto de una línea:** después de resolver tres tropiezos (memoria, un bug de datos y la fragilidad del workflow), medimos P2 con el LLM real sobre 20 exámenes de cripto: el acierto en negativas subió de **61% a 72%** al activar P2. Muestra chica (no concluyente aún); el siguiente paso es confirmarlo en **índice**.

---

## 1. Qué es P2 (recordatorio)

El diagnóstico de causa raíz mostró que el enjambre **predice "sube" de más** ante malas noticias (predecía +5% donde el mercado caía −9%). La causa: los arquetipos **contrarian, quant y optimista** invierten la señal negativa y **cancelan** el "clima" del mercado, así que una mala noticia llega diluida y el enjambre no la toma en serio.

**P2** separa el **tono de mercado** (el clima que sienten todos) de la **apuesta individual** de cada líder. Los invertidores siguen operando y hablando (su frase del hover intacta), pero **ya no fijan el ánimo del mercado**. Se controla con la perilla `peso_tono_invertidores` (1.0 = comportamiento histórico · 0.0 = fuera del tono), también por variable de entorno `ENJAMBRE_PESO_TONO_INVERSORES` para medir/rollback sin re-desplegar.

**Corrección al plan original:** el plan editaba `aplicar_noticia` (la ruta numérica, que ya usa tono directo) — habría tenido efecto CERO. El 38% viene de la ruta LLM (`_tono_de_titular`), que es donde se implementó.

---

## 2. El sistema de medición (por qué hubo que construirlo)

Medir el efecto real en el 38% exige el LLM leyendo titulares reales — que **no corre en la sesión de desarrollo** (sin API key), solo en Render. Y el backtest normal **salta los exámenes ya respaldados** (no re-rinde). Así que construimos:

- **Caché de cerebros al disco persistente** — antes se borraba en cada deploy; ahora se calienta una vez y sobrevive. Esto hace que barrer valores de P2 sea **casi gratis** tras la primera pasada.
- **Endpoint `/api/evaluar`** — re-simula los casos ya respaldados bajo el entorno actual y mide el acierto por categoría, **sin tocar el respaldo histórico**. Acepta `peso` para fijar P2 solo durante la medición.
- **Workflow "Evaluar acierto (P2)"** — un clic en GitHub Actions: eliges `peso`, `mercado`, `tamano` y ves el resultado en el log.

---

## 3. Los tres tropiezos (y qué se arregló)

### Tropiezo 1 — Memoria (Render 512 MB)
La primera corrida **desbordó los 512 MB** del plan Starter (la simulación de 10.000 agentes es pesada) → Render reinició el motor a mitad → el workflow abortó.
**Arreglo:** subiste Render a **Standard (2 GB)**. Confirmado leyendo el contenedor: `ram_mb: 2048`. También agregué ese dato a `/api/estado` para poder verificar el plan desde afuera.

### Tropiezo 2 — Bug de datos (evaluados = 0)
Las siguientes corridas terminaban con **0 exámenes medidos**. El diagnóstico que instrumenté lo reveló: los datos llegaban (645 casos, 1714 eventos) pero **el cruce evento↔caso por `sim_id` daba 0 en Render**. Causa: `_leer_remoto` lee **distinto según haya token** — en Render (con `GITHUB_RESPALDO_TOKEN`) usa la API de GitHub; local (sin token) usa el raw; sirven versiones distintas del archivo y el cruce se rompía.
**Arreglo:** rediseñé `evaluar` para medir **directo sobre los casos respaldados** (que ya traen titular + resultado real), con semilla determinística por caso (`int(sim_id[:8],16)`). Sin cruce frágil. Encuentra 220 cripto / 609 en total.

### Tropiezo 3 — Workflow frágil
El workflow abortaba (exit 22) si el motor tardaba un segundo en responder mientras estaba ocupado calculando (justo lo que pasa con la caché fría).
**Arreglo:** `curl -s` tolerante (un hipo ya no lo tumba), sondeo de 20 min, y **siempre** muestra el último resultado guardado. Nunca falla por un hipo de red.

---

## 4. El primer resultado (con LLM real)

Sobre los **mismos 20 exámenes de cripto** (18 negativas, 2 positivas), semillas idénticas, `con_ia: 20` (todos usaron el LLM real):

| | Negativas | Global |
|---|---|---|
| **peso 1.0** (actual) | 11/18 = **61.1%** | 60% |
| **peso 0.0** (P2) | 13/18 = **72.2%** | **70%** |
| **Diferencia** | **+11 pts** (2 aciertos más) | **+10 pts** |

**P2 acertó 2 negativas más y no perdió positivas.** Primera evidencia real de que la palanca va en la dirección correcta.

---

## 5. La honestidad (qué NO afirmamos aún)

- **No es concluyente:** 18 negativas es muestra chica; un +2 puede tener algo de suerte.
- **No comparable al 38% directo:** ese 38% era todas las negativas (todos los mercados) con semillas originales; este 61%/72% es cripto con semillas nuevas. Lo válido es la comparación **1.0 vs 0.0 sobre la misma muestra** (que aísla P2 limpio).
- **Cripto acierta bien de por sí** (~68%); falta el mercado donde el sesgo alcista era peor: **índice (55%)**.
- **Nada apunta en contra:** la dirección y la consistencia con la hipótesis son buenas.

---

## 6. Lo que sigue: **Opción B — probar en índice**

**Por qué índice:** es el mercado donde el enjambre más se equivocaba por optimismo, así que es donde P2 **debería** ayudar más. Si también mejora ahí, la evidencia se vuelve fuerte y escalamos a la muestra completa.

**Plan inmediato:**
1. Correr `peso: 1.0`, `mercado: indice`, `tamano: 40` → línea base de índice (calienta ~40 exámenes, ~$5 una vez).
2. Correr `peso: 0.0`, `mercado: indice`, `tamano: 40` → P2 sobre los mismos (caché caliente → rápido/gratis).
3. Comparar el acierto en negativas de índice.

**Criterio:**
- Si P2 sube negativas también en índice → señal fuerte → escalar a los 609 y decidir el valor final (0.0 o intermedio) para producción.
- Si no ayuda en índice → aprendimos barato que el efecto es solo de cripto; se evalúa si vale, o se afina la perilla (0.3/0.5).

**Estado de producción:** P2 vive en `main` con la perilla en **1.0 por defecto** — cero cambio de comportamiento hasta que los números justifiquen fijar otro valor. El cambio real lo decides tú con la evidencia.

---

*Piezas: `engine/model.py` (P2 + monitor), `engine/contenido/backtest.py` (evaluar),
`engine/server.py` (endpoints + ram_mb), `engine/brains/cerebro.py` (caché persistente),
`.github/workflows/evaluar.yml` (workflow tolerante). Guía: `docs/medir-p2.md`.*
