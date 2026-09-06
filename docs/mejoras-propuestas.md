# El Enjambre — Mejoras propuestas

> Lista de mejoras concretas surgidas de una revisión a fondo del código,
> con la evidencia de cada una y el arreglo sugerido.
> Fecha: **14 de agosto de 2026** · rama `claude/project-context-nxjjst`
>
> Complementa a `docs/analisis-codigo.md` (revisión del 3 de agosto, que dejó
> varios puntos abiertos que aquí se retoman) y a `docs/contexto.md` §5
> (los pendientes ya conocidos).
>
> **Este documento no toca código: lo describe.** Cada punto trae dónde está
> el problema, por qué importa y qué se haría, para que la decisión de en qué
> invertir el tiempo sea informada y no a ciegas.

---

## Cómo leer este documento

Las mejoras van en cuatro grupos, de lo más urgente a lo menos:

| Grupo | Qué agrupa |
|---|---|
| **A** | Antes de abrir al público — cierran riesgo real (regulatorio, de plata o de abuso) |
| **B** | Fallas que ocurren en silencio — el sistema se equivoca y nadie se entera |
| **C** | Deuda que cobra intereses — no rompe nada hoy, pero encarece cada día de trabajo |
| **D** | Riesgo del día del lanzamiento |

Cada punto trae un semáforo: 🔴 alto · 🟠 medio · 🟡 bajo, y una estimación de
esfuerzo en horas de trabajo (aproximada, para comparar entre sí).

---

# GRUPO A — Antes de abrir al público

## A1. El filtro CMF no toca las frases que ve el público 🔴

**Esfuerzo: ~30 min** · *El punto más serio de la lista, y es regulatorio, no técnico.*

### Qué pasa

El proyecto tiene una regla no negociable: nada de lenguaje de recomendación de
inversión (restricción CMF Chile). Esa regla vive en código, en la función
`es_publicable()` de `engine/contenido/vocabulario.py`, y hoy se aplica en:

- el epílogo del archivo (`server.py:1520`)
- el correo de El Pulso (`boletin.py:62`)
- La Redacción, en sus tres roles (`redaccion.py`, `redaccion_ia.py`)
- el corrector automático (`corrector.py:70`)

**No se aplica a las frases de los líderes de opinión**, que son justamente lo
que más gente ve:

| Dónde aparece la frase sin filtrar | Referencia |
|---|---|
| El mensaje `inicio` que va al navegador en cada simulación | `server.py:454` |
| El mismo mensaje en el modo observatorio | `server.py:380` |
| Lo que se guarda en la base y luego sirve al muro y al archivo | `server.py:521` |
| La "frase jugosa" de cada tarjeta del muro | `server.py:611` (`_resumen_tarjeta`) |
| El widget embebido en el sitio de un medio | mismo dato, vía `/api/muro` |

### Por qué importa

La cadena es corta y directa: **un visitante escribe un titular → la IA lo lee →
su frase se muestra en pantalla sin pasar por el filtro.** Si alguien empuja al
modelo a escribir "compra ahora" o "esto va a subir", eso aparece tal cual.

Y el caso peor no es en tu web: es en el **widget**, donde esa frase sale dentro
del sitio de un medio, con la firma de Rubicón Lab al lado. Ahí el texto ya no se
lee como una simulación: se lee como una recomendación publicada por un tercero.

Esto ya estaba anotado como pendiente en `docs/analisis-codigo.md` §2 del 3 de
agosto, con estas palabras: *"El filtro `es_publicable` se aplica al epílogo y al
brief, pero no a las frases del LLM. Probabilidad baja, pero es un borde de
cumplimiento CMF a cerrar antes de abrir al público."* Sigue abierto.

### Arreglo propuesto

Una sola función en el borde, que haga lo mismo que ya hace el correo: si la
frase no pasa el filtro, se neutraliza (el correo la reemplaza por "—"; en la web
podría ser una frase genérica del arquetipo, para no dejar un hueco visual).

Aplicarla en los cuatro puntos de la tabla. Como todos parten del mismo diccionario
(`respuestas`), lo más limpio es filtrar **una vez, apenas vuelven los cerebros**,
antes de que la frase se reparta a la web, a la base y al reporte.

Test que lo fija: una frase de líder con vocabulario prohibido no debe aparecer
en el mensaje `inicio`, ni en la tarjeta del muro, ni en lo guardado.

---

## A2. El tope diario de gasto se reinicia con cada despliegue 🟠

**Esfuerzo: ~1 h**

### Qué pasa

El contador de simulaciones del día vive en una variable en memoria:
`_consumidas_hoy` (`engine/contenido/limites.py:27`). Render reinicia el proceso
cada vez que hay un despliegue, y también cuando la memoria se aprieta. En cada
reinicio, el contador **vuelve a cero**.

### Por qué importa

El tope diario es lo que impide que una avalancha de visitas se convierta en una
cuenta grande de Anthropic. Con el contador en memoria, ese tope no es un techo
firme: es un techo que se levanta solo cada vez que el motor reinicia. Un día con
varios despliegues (o con reinicios por memoria, que ya han ocurrido) puede
gastar varias veces el tope configurado.

Está documentado como deuda consciente en `docs/contexto.md` §6, con el argumento
de que el disco era efímero de todos modos. **Ese argumento ya no aplica: el
servidor pasó al plan con disco propio.** La base SQLite ahora sobrevive a los
reinicios, así que el contador puede vivir ahí.

### Arreglo propuesto

Mover el contador a una tabla de la base (una fila por día: fecha y cuántas van).
Son unas 20 líneas en `limites.py` más una tabla en `persistencia.py`. El
rate-limit por IP puede quedarse en memoria sin problema — ese es de minutos y su
reinicio no cuesta plata.

---

## A3. La lista de blindaje que ya está decidida, sin ejecutar 🔴

**Esfuerzo: ~1 h en total, casi todo en el panel de Render**

Estos puntos ya están acordados en `docs/contexto.md` §5. No son hallazgos
nuevos: son tareas pendientes que siguen pendientes, y todas son bloqueantes para
abrir al público.

| Qué | Estado hoy | Debe quedar |
|---|---|---|
| Tope global diario (`ENJAMBRE_MAX_SIM_DIA`) | **500** (subido para calibrar) | **5** |
| Tope por IP por hora (`ENJAMBRE_MAX_SIM_IP_HORA`) | **100** | **3** |
| Llaves de Alpaca | expuestas en un chat | regeneradas |
| `ENJAMBRE_PIPELINE_TOKEN` (la llave del panel y de los endpoints de admin) | apareció parcial en capturas | rotado |
| CSP del widget | pendiente | puesta |
| `ENJAMBRE_ORIGENES` | sin el dominio definitivo | con el dominio |

**Ojo con el orden:** rotar `ENJAMBRE_PIPELINE_TOKEN` deja el Centro de Mando
pidiendo la clave de nuevo (es la misma). Hay que rotarlo y anotar la nueva, no
al revés.

---

## A4. El comodín de CORS saltea la lista blanca del widget 🟡

**Esfuerzo: ~15 min (es una decisión, no un desarrollo)**

### Qué pasa

En `engine/server.py:126` la API acepta peticiones desde cualquier origen que
calce con `https://.*\.vercel\.app`. Se puso para que funcionen los previews de
Vercel, y cumple ese fin.

### Por qué importa

**No es un hueco de seguridad.** Los datos que sirve son públicos de todos modos,
y los endpoints de administración exigen una cabecera que el navegador no deja
enviar desde otro origen, así que quedan fuera de alcance. Verificado además que
la versión de Starlette que corre (1.6) compara con `fullmatch`, así que no se
puede burlar con un dominio tipo `algo.vercel.app.sitio-malicioso.com`.

Lo que sí toca es **el modelo de negocio del widget**: la sección 9 de
`CONTENIDO.md` define una lista blanca de medios autorizados a embeberlo. Ese
comodín la deja sin efecto para cualquiera que publique su sitio en Vercel.

### Arreglo propuesto

Es una decisión tuya, con dos caminos:

1. **Acotar** — reemplazar el comodín por los dominios de preview que realmente
   uses. Cuesta que cada preview nuevo de Vercel haya que agregarlo a mano.
2. **Asumirlo** — dejarlo, entendiendo que la lista blanca del widget es una
   convención comercial, no una barrera técnica.

Lo que no conviene es dejarlo sin decidir, creyendo que la lista blanca protege
algo que no protege.

---

# GRUPO B — Fallas que ocurren en silencio

## B5. Editas El Pulso, dice "guardado", y apruebas la versión vieja 🟠

**Esfuerzo: ~15 min** · *La mejor relación daño/tamaño de toda la lista.*

### Qué pasa

En `engine/server.py:1248` (`panel_editar`), cuando editas el texto del Pulso
desde el Centro de Mando, pasan dos cosas: se guarda tu texto, y se vuelve a
generar la vista previa del correo con ese texto.

La segunda está envuelta en un `try/except Exception: pass` (líneas 1260-1273) y
**la función devuelve `{"ok": True}` de todas formas**.

### Por qué importa

Si la regeneración falla —por ejemplo porque ese día no hay destacadas, que es
justo la condición que el código chequea— la secuencia es esta:

1. Editas el texto en el panel.
2. El panel te dice que quedó guardado. ✅
3. Miras la vista previa: **es la vieja**, sin tus cambios.
4. Aprietas "Aprobar y enviar".
5. Sale el correo a todos los suscriptores **sin tus ediciones**.

Nadie se entera en ningún momento. El texto sí se guardó en la base; lo que salió
por correo fue otra cosa.

### Arreglo propuesto

Que la respuesta diga la verdad: si el preview no se pudo regenerar, devolver
`{"ok": true, "preview_actualizado": false, "motivo": "…"}` y que el panel muestre
un aviso claro ("se guardó tu texto, pero la vista previa quedó desactualizada").
Son unas pocas líneas en el servidor y un aviso en `panel.html`.

---

## B6. Si el ritual de la madrugada falla, silencio absoluto 🟠

**Esfuerzo: ~30 min**

### Qué pasa

`_correr_ritual()` (`engine/server.py:1289`) envuelve el ritual completo —elegir
los titulares del día, simularlos, armar el Pulso— en un `try/except Exception:
pass`. El comentario explica la intención, que es correcta: *"cualquier fallo se
traga (no debe tumbar el servidor)"*.

El problema no es que no tumbe el servidor. Es que **tampoco deja rastro**: ni un
`print`, ni un aviso. Nada.

### Por qué importa

El ritual es lo que hace que el muro amanezca lleno y que salga El Pulso. Si se
cae, el resultado visible es un muro vacío y ningún correo — indistinguible de
"hoy no había noticias interesantes". Y en el log de Render no hay ninguna pista
de por qué.

Lo mismo aplica al botón **"Generar edición de hoy"** del Centro de Mando: lanza
la misma función, te responde *"Generando la edición de hoy… (~1-2 min). Recarga
en un momento"*, y si falla, recargas para siempre sin que aparezca nada.

### Arreglo propuesto

No cambiar el comportamiento —que siga sin tumbar el servidor— pero dejar rastro:

1. Un `print` con la causa (`traceback`), que en Render queda en el log.
2. Un aviso por Telegram con `notificar.avisar()`, que ya existe y desde la
   auditoría de hoy escapa bien el texto.

Con eso la operación pasa de adivinar a saber. Es el mismo patrón que ya usa el
backtest, que sí imprime su resultado (`server.py:_correr_backtest`).

**Nota:** hay otros dos `except Exception: pass` en el servidor que **están
bien** y no hay que tocar: el de `_suscribir_silencioso` (`server.py:98`, para no
apagar el momento mágico de la simulación por un fallo del correo) y el del
cierre del WebSocket (`server.py:314`). La diferencia es que esos fallan en algo
accesorio; el ritual falla en el producto entero.

---

# GRUPO C — Deuda que cobra intereses

## C7. Veinte minutos para saber si rompiste algo 🟡

**Esfuerzo: ~2 h**

### Qué pasa

La batería completa son 187 pruebas y tarda **20 minutos y medio**. La razón es
legítima: varias levantan el mercado completo —10.000 agentes, 150 latidos— porque
es la única forma honesta de comprobar los hechos estilizados.

### Por qué importa

Cuando verificar cuesta 20 minutos, se verifica menos. Y verificar menos es
exactamente lo contrario de lo que uno quiere de una batería de pruebas: el valor
de un examen no está en que exista, está en que se rinda seguido.

### Arreglo propuesto

Marcar las pruebas lentas con una etiqueta de pytest (`@pytest.mark.lento`) para
tener dos modos:

- **Tanda rápida** (~1 min): todo menos las que levantan mercados. Es la que se
  corre mientras se trabaja, a cada rato.
- **Tanda completa** (20 min): antes de cada despliegue y en el flujo de GitHub.

No se pierde ninguna cobertura: se elige cuándo pagar los 20 minutos. Se paga solo
en la primera semana de uso.

---

## C8. Una sola prueba del frontend 🟡

**Esfuerzo: ~3 h**

### Qué pasa

Las pruebas del frontend hoy son **cero**. El `package.json` de `web/` solo sabe
`dev`, `build` y `preview` — no hay corredor de pruebas instalado. Las 187 son
todas de Python: el enjambre 3D, la escena, el hover sobre un líder, el reporte,
nada de eso está cubierto.

### Por qué importa

No propongo una suite completa del frontend: sería sobre-ingeniería y va contra la
regla 5 del proyecto ("prefiere la solución simple que funciona hoy"). Propongo
**una sola prueba**, la que atrapa la falla que ya ocurrió de verdad:

`docs/contexto.md` §3.7 documenta que en 4G débil una hoja de estilos colgada
dejaba **toda la pantalla en negro**. Se arregló, pero nada impide que vuelva —
ninguna prueba lo vigila.

### Arreglo propuesto

Una prueba con Playwright (Chromium ya viene instalado en el entorno, no hay nada
que descargar): abrir la página construida, esperar, y verificar que el lienzo del
enjambre dibujó algo distinto de negro. Una sola aserción, que cubre la peor falla
posible del producto: que el visitante llegue y no vea nada.

---

# GRUPO D — Riesgo del día del lanzamiento

## D. Dos simulaciones a la vez en medio procesador 🟠

**Esfuerzo: 1 min (cambiar un número) + criterio**

`MAX_SIM_CONCURRENTES = 2` (`engine/server.py:46`) define cuántas simulaciones
pesadas corren al mismo tiempo. El servidor tiene 0,5 de procesador y 512 MB.

El análisis del 3 de agosto (`docs/analisis-codigo.md` §1) ya lo había marcado:
*"Correr 2 simulaciones de 10.000 agentes en 0,5 CPU / 512 MB está al borde — ya
vimos reinicios por memoria con UNA sola. En el plan actual, 1 sería más
seguro."* Sigue en 2.

**Por qué importa:** ese número es el que decide, el día que lleguen visitas de
verdad, entre *"El enjambre está ocupado, intenta en unos segundos"* (elegante) y
*el motor reinicia a mitad de la simulación de alguien* (pésimo). Bajarlo a 1
hace que más gente vea el mensaje de ocupado, pero nadie vea el motor caerse.

La alternativa, si se prefiere mantener 2, es subir el plan del servidor. Es una
decisión de plata contra experiencia, y conviene tomarla **antes** del lanzamiento
y no durante.

---

# Resumen y orden sugerido

| # | Mejora | Riesgo | Esfuerzo | Tipo |
|---|---|:---:|:---:|---|
| **A1** | Filtro CMF a las frases de los líderes | 🔴 | 30 min | código |
| **B5** | El panel miente cuando el preview falla | 🟠 | 15 min | código |
| **B6** | El ritual falla en silencio | 🟠 | 30 min | código |
| **A2** | Tope diario a disco (deja de reiniciarse) | 🟠 | 1 h | código |
| **A3** | Blindaje: topes, llaves, CSP, dominio | 🔴 | 1 h | operación |
| **D** | Bajar simulaciones simultáneas a 1 | 🟠 | 1 min | decisión |
| **A4** | Decidir el comodín de CORS | 🟡 | 15 min | decisión |
| **C7** | Tanda rápida de pruebas | 🟡 | 2 h | código |
| **C8** | Una prueba del frontend | 🟡 | 3 h | código |

**Primera pasada recomendada: A1 + B5 + B6.** Son las tres que combinan daño real
con arreglo pequeño, las tres se pueden fijar con una prueba, y juntas son menos
de una hora y media de trabajo.

**Segunda: A2**, que cierra la última fuga de la billetera.

**A3, A4 y D no son código:** son decisiones tuyas y un rato en el panel de Render.

---

# Apéndice 1 — Qué se arregló hoy (14 de agosto)

Para que este documento se entienda solo, el contexto de la revisión que lo
originó. Cuatro hallazgos, ya corregidos y con pruebas que los fijan:

1. **El correo de El Pulso no escapaba los titulares ni las frases de la IA.** La
   función `_limpiar()` de `boletin.py` pasaba el filtro CMF pero devolvía el texto
   crudo a un contexto HTML. Los titulares vienen de Alpaca y las frases las
   escribe la IA leyendo un titular que puede venir del público: un titular hostil
   podía colar marcado —un enlace falso— en el correo que reciben los suscriptores.
2. **Sin tope de tamaño de cuerpo en los POST.** Un envío de cientos de MB se
   cargaba entero en memoria antes de validarse; el motor (512 MB) se quedaba sin
   memoria y reiniciaba.
3. **Los avisos a Telegram no escapaban lo que escribe el visitante.** Van con
   `parse_mode=HTML`: un `<` en el formulario B2B hacía que Telegram rechazara el
   mensaje con 400 y el aviso se perdiera — un lead perdido sin que nadie lo supiera.
4. **`panel.html`** cosía la fecha dentro de un `onclick` sin escapar (el único
   sumidero sin escape que quedaba en el panel).

También se corrigieron dos desfases de documentación: `CLAUDE.md` §5 decía que se
enviara `temperature ≈ 0.8` a los cerebros, cuando la lección aprendida (y el
código) dicen lo contrario — `claude-sonnet-5` lo rechaza con HTTP 400 y todos los
líderes caen al respaldo en silencio. Y el `README.md` seguía describiendo 5.000
agentes y la Etapa 4.

---

# Apéndice 2 — Qué prueban y qué no prueban las 187

Un dato que conviene tener presente al leer las propuestas de arriba: **la batería
estaba verde mientras los cuatro bugs de hoy existían.** Se comprobó devolviendo
el correo a su versión anterior y pasándole las pruebas nuevas: fallan de
inmediato. Los bugs no los encontró el examen — el examen no tenía la pregunta.

Lo que la batería **no** mira hoy:

| Punto ciego | Detalle |
|---|---|
| La IA real | 11 de los 21 archivos de prueba borran la clave de Anthropic antes de correr. Es a propósito (sin costo, sin red), pero significa que ninguna prueba comprueba que los cerebros reales funcionen: prueban el respaldo léxico. Para eso está `GET /api/diagnostico`. |
| Los servicios externos | Alpaca, Resend, Barchart, Telegram y la caja fuerte de GitHub se apagan en las pruebas. Que "El Pulso pase" significa *el correo se arma bien*, no *el correo llega*. |
| El frontend | Cero cobertura (ver C8). |
| Las huellas del mercado | Se comprueban con dos semillas (42 y 3). Pasan ahí; no es una garantía universal. |
| Si el enjambre acierta | Eso es la libreta de calibración, otra medición distinta. Verde en las pruebas ≠ enjambre certero. |

La batería es la revisión técnica del auto: confirma que los frenos, las luces y
los cinturones funcionan, y que nada que ayer andaba se echó a perder hoy. **No
opina sobre si el conductor va por el camino correcto.** El camino es la
calibración.

---
*Rubicón Lab · El Enjambre · Mejoras propuestas · 14 de agosto de 2026*
