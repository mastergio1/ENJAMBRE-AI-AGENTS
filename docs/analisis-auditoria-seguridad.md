# Análisis en frío — Propuesta 2 (auditoría de seguridad e ingeniería)

*Rubicón Lab · 2026-11-17. Verificación de la auditoría técnica contra el código
real, sin sesgo. A diferencia de la Propuesta 1 (que se apoyó en comentarios
obsoletos), esta auditoría hizo análisis estático de verdad y casi todo lo que
afirma es CORRECTO y verificable.*

---

## Resumen de una línea

Es la mejor de las propuestas recibidas: honesta, humilde (distingue hallazgos
estáticos de lo que requiere ejecución, y NO promete capacidad predictiva), y sus
hallazgos se confirman en el código. Tiene **un P0 real de seguridad que hay que
arreglar ya**, varios P1 de ingeniería y ciencia válidos, y un plan de
profesionalización correcto — pero que es **trabajo de semanas, no de 4 días**. El
reto es separar "lo que se arregla antes del sábado" de "la hoja de ruta post-evento".

---

## Verificación punto por punto

### 4.1 · P0 — Credencial escrita en el código · **CONFIRMADO (real, arréglalo ya)**
`engine/server.py:1548`:
```python
if clave != "revisar-pulso-2026":
    return Response(status_code=404)
```
Es exactamente lo que dice la auditoría: una clave **hardcodeada** en la URL que
protege `/api/pulso/suscriptores`. Ese endpoint revela conteos de suscriptores y,
con `?email=`, si un correo concreto está suscrito/pendiente/baja (fuga de
privacidad: permite comprobar si cualquier correo está en la lista).
**Agravante propio de hoy:** esa clave ya viaja en `docs/codigo-fuente-enjambre.md`,
el volcado que generamos y compartimos con revisores externos → el "secreto" ya
está efectivamente público.
**Severidad honesta:** es de solo lectura (no controla dinero ni borra datos), así
que no es catastrófico, pero es un secreto incrustado + fuga de privacidad en un
servicio EN VIVO. La auditoría tiene toda la razón.
**Arreglo (1 línea, patrón que YA existe):** usar `_token_admin_ok(clave)` —
que lee `ENJAMBRE_PIPELINE_TOKEN` del entorno, falla cerrado y compara en tiempo
constante. El mismo token que ya protege los demás endpoints de admin.
→ **ACCIÓN INMEDIATA.**

### 4.2 · P1 — Cuotas vulnerables a concurrencia · **CONFIRMADO (mitigado)**
`engine/contenido/limites.py`: el chequeo del tope global (`gasto_dia >= tope`,
línea 85) y el incremento (`sumar_gasto_dia`, líneas 99/113) son operaciones
SEPARADAS → dos peticiones simultáneas pueden pasar el chequeo antes de incrementar
(TOCTOU). Y `_uso` (línea 48) es un contador en memoria (rate-limit por IP) que se
reinicia al reiniciar el proceso y no se comparte entre instancias.
**Mitigación real:** el motor corre en UNA instancia con slots limitados de
simulación, así que la concurrencia verdadera es baja. El riesgo existe pero el
daño práctico hoy es acotado. → **Válido; arreglo post-evento (reserva atómica).**

### 4.3 · P1 — Límite de cuerpo HTTP tras leerlo entero · **PLAUSIBLE (a verificar)**
No lo confirmé a fondo. Hay middleware de seguridad (`contenido/seguridad.py`) con
límites; falta comprobar si el límite se aplica durante el streaming o después de
materializar el body. → **A revisar; no es bloqueante para el evento.**

### 4.4 · P1 — Tareas críticas con BackgroundTasks · **CONFIRMADO (por diseño)**
El servidor usa `BackgroundTasks` para pipeline/backtest/cosecha. Si el proceso se
reinicia, una tarea en curso se pierde (no es una cola durable). Cierto. Para el
PRODUCTO en vivo del evento no es crítico (esas tareas son del ritual del Pulso, no
de la demo). → **Válido; cola durable es trabajo post-evento.**

### 4.5 · P1 — Baseline del walk-forward usa etiquetas OOS · **CONFIRMADO**
`engine/calibration/walk_forward.py:92`: `base = cal.tasa_base(ys_oos)` — la tasa
base se calcula con las etiquetas del propio tramo fuera de muestra. Es una fuga
sutil en el BASELINE (no en el modelo): el "azar" contra el que compites conoce el
balance de clases del futuro. Lo correcto es calcular la base solo con el train
disponible hasta ese corte. Baja importancia práctica, pero la crítica es correcta
y barata de arreglar. → **Válido; arreglo chico.**

### 4.6 / 4.7 / 4.9 · P1 — Selección sobre OOS, sin purga/embargo, holdout por hash · **CONFIRMADO y ALINEADO con lo nuestro**
`engine/calibration/verificador.py:34`: `es_holdout` reparte por `sha256(sim_id) %
100 < 30` — holdout por HASH, no temporal ni agrupado por evento/activo. La
auditoría acierta: puede separar casos del mismo acontecimiento entre train y
holdout (fuga por correlación). **Esto es exactamente el problema de fuga que ya
detectamos y medimos por nuestra cuenta** (remedir_sin_fuga, baseline-calibracion-
fase0.md). La auditoría lo generaliza bien (purga, embargo, agrupación por evento).
→ **Válido y coincide con nuestro hallazgo independiente.**

### 4.8 · P1 — Fechas sintéticas no cronológicas en el test · **CONFIRMADO (menor)**
`engine/validation/test_walk_forward.py:24`: `f"2026-08-{i % 28 + 1:02d}..."` — el
día cicla con `i % 28`, así que las fechas no son estrictamente crecientes. El test
puede pasar sin comprobar bien el orden temporal. Arreglo trivial (fechas
monótonas + un test con datos desordenados). → **Válido; menor.**

### 4.10 · P1 — Brier solo no basta · **YA MAYORMENTE HECHO**
`contenido/calibracion.py` ya trae Brier, Brier Skill Score vs base, curva de
confiabilidad por tramos y skill_score. Falta lo que pide de más: ECE/MCE,
intervalos de confianza y no publicar subgrupos con N chico. → **Arnés hecho;
faltan los adornos estadísticos. Válido.**

### 4.11 · P2 — Microestructura del mercado · **CORRECTO (ambicioso)**
El libro de órdenes es simple. Las mejoras (prioridad precio-tiempo, spread
explícito, profundidad, slippage) son correctas para realismo, pero NO cambian el
acierto direccional ni son necesarias para la demo. → **Hoja de ruta, no evento.**

### 4.14 · P2 — Caché LLM sin versión de modelo/prompt · **CONFIRMADO**
`engine/brains/cerebro.py:48`: la clave de caché es `titular|arquetipo|semilla`, sin
modelo, prompt ni esquema. Cambiar el prompt o el modelo puede devolver respuestas
viejas. Cierto y vale la pena (reproducibilidad). Arreglo chico: añadir modelo+
versión de prompt a la clave. → **Válido; barato.**

### 4.18 · P3 — Conteos desalineados doc vs config · **CONFIRMADO (parcial)**
`config/agentes.json` dice `total_agentes: 10150` (9.000 + 1.150 líderes). CLAUDE.md
mezcla 10.000/1.000 en el cuerpo pero la nota del doomer ya dice 10.150. El config es
la fuente de verdad. Arreglo: un test que verifique que los conteos no se desalinean.
→ **Válido; menor.**

### El resto (4.12 rendimiento, 4.13 CPU/memoria, 4.15 observabilidad, 4.16 modularizar server.py de 2015 líneas, 4.17 SQLite→Postgres)
Todo correcto como ingeniería de producción y bien argumentado. Es la hoja de ruta
de **profesionalización por etapas** (semanas/meses). Nada de esto es para 4 días
antes del pitch, y la propia auditoría lo ordena así (seguridad → fiabilidad →
ciencia → rendimiento → LLM → modularización).

---

## Veredicto

**Oro inmediato (antes del evento):**
1. **Arreglar el P0** (credencial hardcodeada → `_token_admin_ok`). 1 línea, patrón
   ya existente. Urgente porque el valor ya está en el volcado compartido.
2. (Opcional, baratos) el fix del baseline-sobre-train (4.5), la clave de caché con
   versión (4.14), el test de conteos (4.18), fechas monótonas en el test (4.8).

**Hoja de ruta post-evento (correcta, pero NO para esta semana):**
- Reserva atómica de cuotas (4.2), cola durable + workers (4.4), límites de carga
  (4.13), observabilidad (4.15), modularizar server.py (4.16), Postgres cuando
  escale (4.17), microestructura (4.11), nested walk-forward + purga/embargo (4.6/
  4.7/4.9) — esto último ya alineado con nuestro trabajo de fuga.

**Coincidencia clave:** su crítica científica central (holdout por hash, fuga por
correlación de eventos, baseline optimista) **es el mismo problema que ya
encontramos y medimos**. Eso valida de forma independiente nuestro giro al "techo
honesto + gating por índice". No nos contradice: nos respalda.

**Qué NO hacer:** no arrancar la reescritura/profesionalización ahora. La auditoría
misma lo dice en su dictamen: "no reconstruir; profesionalizar por etapas". Primero
el evento; después, esta hoja de ruta en orden.
