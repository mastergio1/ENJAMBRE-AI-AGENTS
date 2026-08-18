# El Enjambre · El Pulso — Contexto Completo del Proyecto

> Documento de contexto **profundo** y consolidado. Sirve para que cualquier
> persona (o IA) entienda el proyecto entero: qué es, cómo funciona por dentro,
> cómo está desplegado, qué se ha resuelto, qué falta y hacia dónde va.
>
> La biblia de decisiones de producto sigue siendo `CLAUDE.md` (raíz). Este
> archivo lo complementa con el **estado operativo real** y las **lecciones**
> que no están en la biblia.
>
> _Rubicón Lab · Dueño: Giorgio (director, no programador) · Última gran
> actualización: agosto 2026._

---

## 0. Resumen ejecutivo (una página)

**El Enjambre** es un simulador 3D del mercado: el usuario escribe un titular
(ej. *"la Fed sube las tasas 50 pb"*) y ve, en una escena 3D, cómo **10.000
inversionistas simulados con IA** reaccionan — el pánico se contagia, se forman
manadas, emerge un precio. Es *"el focus group sintético del mercado"*:
herramienta de **simulación y educación**, nunca asesoría financiera.

Sobre ese motor se construyó **El Pulso**, un **diario de mercado por correo**
(newsletter) que sale solo cada día, con noticias, análisis y gráficos reales.
El Pulso es el producto que la gente **se suscribe** y consume a diario; El
Enjambre es el **gancho visual** único y el laboratorio detrás.

- **Cliente:** B2B (fintechs, educación financiera, medios económicos, gestores)
  y retail curioso como top-of-funnel.
- **Diferenciador:** la visualización 3D del enjambre en tiempo real. Nadie más
  la tiene.
- **Restricción legal transversal (CMF Chile):** informar, **nunca aconsejar**.
  Sin recomendaciones, sin predicciones, sin precios objetivo. Esto atraviesa
  TODO — motor, correos, redes sociales.
- **Estado:** en producción y funcionando de lunes a domingo. En **calibración**
  (posicionamiento honesto y también legalmente conveniente).

---

## 1. Los dos productos

### 1.1 El Enjambre (la herramienta / el motor)
Simulador de agentes: 10.000 inversionistas simulados reaccionan a un titular.
El resultado emerge de sus decisiones (no está hardcodeado). Se renderiza en 3D
en la web. Web pública: `https://enjambre-ai-agents.vercel.app`.

### 1.2 El Pulso (el diario / la newsletter)
Diario de mercado por correo, con su propio dominio `diarioelpulso.com`. Sale
solo cada mañana (6:00 Chile) como **borrador pendiente de aprobación**; Giorgio
revisa y aprueba; recién ahí sale a los suscriptores. **Calendario:**

| Día | Edición |
|---|---|
| **Lunes–Viernes** | Los titulares del día + lo que mueve el mercado (noticias + gráficos + análisis) |
| **Sábado** | Resumen de la semana (los grandes temas con punto de vista + "qué observar") |
| **Domingo** | Deep-dive de una empresa mediana/grande o un sector (de un universo de 500, elegido por atención) |

---

## 2. La restricción CMF (la más importante)

La Comisión para el Mercado Financiero (Chile) prohíbe dar asesoría de inversión
sin licencia. Por eso **todo el producto informa, no aconseja**:

- **Prohibido siempre:** "compra/vende/mantén", "conviene", "es buen momento",
  "oportunidad de compra", "deberías", "precio objetivo", "va a subir/bajar",
  "le vemos potencial".
- **Prohibido:** predecir el futuro. Se cuenta lo que **ya pasó** y su **porqué**.
  Mirar adelante siempre es **"qué observar / qué está en juego"**, nunca "qué va
  a pasar".
- **Cómo se implementa:** un filtro de vocabulario en código (`contenido/
  vocabulario.py`, funciones `es_publicable`, `verificar_pieza`, más `DISCLAIMER`)
  por el que pasa **cada texto** antes de publicarse. Si un texto cruza la línea,
  se descarta (o se cae ese párrafo). Hay tests que protegen esto.
- **En el deep-dive del domingo** el "potencial" no lo pone el medio: lo ponen en
  tensión los **arquetipos** de inversionistas, como miradas contrastantes.
- **En redes sociales aplica igual:** todo va como "experimento educativo, en
  calibración". Nunca "entonces compra X".

> Regla mental: análisis profundo **sí**; recomendación de inversión **jamás**.

---

## 3. Arquitectura y stack

```
enjambre/
├── CLAUDE.md                  ← biblia de producto
├── docs/                      ← documentación (este archivo entre otros)
├── engine/                    ← motor + API + capa de contenido (Python 3.11)
│   ├── server.py              ← FastAPI + WebSocket + todos los endpoints
│   ├── model.py               ← el modelo Mesa (MercadoEnjambre)
│   ├── llm_texto.py           ← extrae texto de respuestas Anthropic (ver §7)
│   ├── agents/                ← clases de agentes por tipo (lider.py, etc.)
│   ├── brains/                ← cerebros LLM: arquetipos, cerebro, reparto, mercado
│   ├── market/                ← libro de órdenes, formación de precio
│   ├── network/               ← red de influencia (scale-free)
│   ├── validation/            ← tests (hechos estilizados + toda la suite)
│   └── contenido/             ← EL PULSO y toda la capa de contenido
│       ├── config/
│       │   ├── agentes.json           ← la mezcla de agentes
│       │   └── universo_semanal.json  ← las 500 empresas del deep-dive
│       ├── pipeline.py        ← el ritual diario (orquesta todo)
│       ├── portero.py         ← elige los titulares del día (LLM haiku)
│       ├── redaccion.py       ← La Redacción: hechos verificados con su cita
│       ├── redaccion_ia.py    ← los 3 redactores (diario, sábado, domingo)
│       ├── analisis_semanal.py← selección del deep-dive del domingo
│       ├── resumen_semanal.py ← el resumen de la semana (sábado)
│       ├── boletin.py         ← arma y envía el HTML del correo (Resend)
│       ├── graficos.py        ← gráficos de precio reales (PNG, PIL)
│       ├── persistencia.py    ← SQLite (simulaciones, ediciones, suscriptores)
│       ├── corrector.py       ← compara "lo que dijo el enjambre" vs realidad
│       └── fuentes/           ← yahoo.py, alpaca.py, barchart.py
├── engine/panel.html          ← el Centro de Mando (dashboard)
└── web/                       ← frontend (Vite + Three.js + GSAP + Tailwind)
    └── src/                   ← swarm 3D, muro, archivo, duelo, widget, UI
```

**Stack fijo:**
- **Motor:** Python 3.11 · FastAPI + WebSocket · Mesa 3 (agentes) · SQLite · httpx · Pillow.
- **IA:** API de Anthropic — `claude-sonnet-5` (redactores y cerebros) y
  `claude-haiku-4-5` (portero de titulares).
- **Frontend:** Vite + Three.js (vanilla, instanced) + GSAP + Tailwind.
- **Infra:** GitHub (`mastergio1/enjambre-ai-agents`) · Render (motor, Docker) ·
  Vercel (web) · Resend (correo) · GitHub Actions (cron diario).

---

## 4. El motor de simulación

### 4.1 La mezcla — 10.000 agentes
La *cantidad* representa personas; el *capital* representa poder de mercado. Los
institucionales son pocos pero con capital ~50x (generan ~65-70% del volumen);
el retail domina en número (~89%) pero pesa ~30-35% del volumen. Tipos (resumen;
detalle y parámetros en `CLAUDE.md` §4 y `config/agentes.json`):

- **Institucionales (reaccionan a precio/fundamentales, NO a rumores):**
  fundamentalista/value, quant/momentum, fondo pasivo, market maker, ejecutor
  TWAP/VWAP, arbitrajista.
- **Retail (en la red social, se contagian):** noise trader, manada/imitador,
  FOMO/momentum, miedoso/aversión a pérdida, contrarian, buy & hold.
- **Líderes de opinión (LLM): 1.000.** Son los únicos que **leen la noticia
  real**. Su señal ∈ [-1,+1] se propaga por la red.

### 4.2 Los 1.000 líderes y el presupuesto LLM
Los 1.000 líderes **no** llaman a la API uno por uno. Comparten **~110 "cerebros"**
repartidos por arquetipo (`brains/reparto.py`): cada cerebro es UNA llamada, y los
líderes del mismo arquetipo la comparten en ronda. Así el costo por simulación se
mantiene en el techo (~$0.12) pase lo que pase. Presupuesto: **máx ~100-120
llamadas por simulación.**

### 4.3 Los 8 arquetipos de líderes
`brains/arquetipos.py`: Institucional Frío, Quant Escéptico, FOMO Evangelista,
Doomer, Contrarian Sabio, Macro Trader, Influencer Optimista, Value Paciente.
Cada uno tiene su prompt de personalidad y su fallback léxico. La diversidad vive
en los 8 arquetipos + el muestreo del modelo (no en repetir llamadas).

### 4.4 La red de influencia
Grafo dirigido **scale-free (Barabási–Albert)**: pocos nodos muy conectados (los
líderes), muchos poco conectados. Propagación **con retardo** (1-4 ticks) y
atenuación 0.7 por salto → esto crea **la ola visual**, el efecto más importante
del producto.

### 4.5 Validación (hechos estilizados)
Tests en `validation/` que deben pasar antes de cualquier demo: colas gordas
(curtosis > 3), clustering de volatilidad, sin autocorrelación de retornos,
asimetría de pánico (las caídas más rápidas que las subidas), respuesta a shock
(caer → sobre-reaccionar → rebotar). Si un test falla, se ajustan proporciones,
**no** se hardcodea el resultado.

---

## 5. La capa LLM y sus lecciones (CRÍTICO)

Tres reglas aprendidas a la mala. Si trabajas en los redactores/cerebros, léelas:

1. **NO enviar `temperature` / `top_p` / `top_k`.** `claude-sonnet-5` los rechaza
   con HTTP 400 y *todos* los líderes/redactores caen al respaldo en silencio. La
   variabilidad viene del muestreo del modelo + la semilla, no de un parámetro.

2. **Leer el texto de la respuesta con `llm_texto.texto_de(respuesta)`, NUNCA
   `respuesta.content[0].text`.** Los modelos nuevos (sonnet-5) **razonan antes
   de responder**: el primer bloque de `content` puede ser un `ThinkingBlock` (sin
   `.text`). Tomar `content[0].text` a ciegas revienta con `AttributeError`, la
   excepción se traga en un `try/except`, y el resultado queda vacío. **Este fue
   el bug que dejó a El Pulso sin correo de fin de semana** (el diario "sobrevivía"
   cayendo a su plantilla; el fin de semana no tiene ese respaldo, así que no
   salía nada). `llm_texto.texto_de` junta solo los bloques de tipo texto.

3. **Fallback obligatorio.** Si la API falla o el JSON no parsea, cada redactor
   devuelve `None` y el boletín cae a su plantilla. **La simulación/el correo
   NUNCA se caen por la API.** Ojo: las ediciones de **fin de semana no tienen
   fallback de plantilla** (dependen del deep-dive/resumen), por eso ahí un fallo
   silencioso = no hay correo. Vigilar.

4. **`MAX_TOKENS = 8000`** en los redactores. El razonamiento (thinking) consume
   tokens; con 4000 el análisis del domingo se cortaba a medias y el JSON no
   parseaba. Se subió a 8000 para dar holgura.

---

## 6. El Pulso en detalle — el ritual diario

Orquestado por `pipeline.py::ritual_matutino`. Cada mañana (disparado por el cron):

1. **Recolectar** titulares (Alpaca; degradación elegante a demo).
2. **El Portero** (`portero.py`, LLM `claude-haiku-4-5`, "de dos pisos") elige el
   top del día y evalúa impacto/símbolos. Filtra publicidad y listas.
3. **Simular** (solo entre semana) las destacadas con seeds fijas
   (reproducibilidad), guardando frames para el replay 3D del muro.
4. **La Redacción** (`redaccion.py`): arma los **hechos verificados** — el número
   manda (viene de Yahoo, no de un texto), cada hecho con su cita/fuente. Roles:
   Reportero (trae los hechos con cita), Verificador (descarta ruido), Editor
   (pone voz + filtro CMF).
5. **El redactor de IA** (`redaccion_ia.py`) le pone **voz** según el día:
   - **`redactar`** (lun-vie): 3-4 historias con análisis (qué pasó → por qué
     importa → conexión macro → bottom line) + gráfico real por historia.
   - **`redactar_resumen`** (sábado): intro + 3-5 temas de la semana (qué pasó,
     por qué, conexión geopolítica/macro, qué observar) + "la semana en números".
   - **`redactar_analisis`** (domingo): el deep-dive — contexto (qué es la
     empresa) → por qué está en la mira → gráfico → **los números** (fundamentales
     verificados de Yahoo) → **debate de arquetipos** → qué observar.
6. **Gráficos reales** (`graficos.py`): PNG estilo editorial desde datos de Yahoo,
   servidos por `GET /api/grafico/{ticker}`.
7. **El boletín** (`boletin.py`): arma el HTML (paleta clara, editorial) y —tras
   aprobación— lo envía por **Resend**. El Enjambre baja al **pie** como
   herramienta hermana (NO como autor del Pulso: eso le quitaría seriedad).
8. **Se guarda como PENDIENTE** y se manda a Giorgio un **correo de revisión**
   (con botones Aprobar/Descartar). Nada sale a suscriptores sin su visto bueno.
9. **El Corrector** (`corrector.py`) guarda, días después, cuánto se movió de
   verdad el símbolo de las destacadas → alimenta la calibración y el campo
   *"¿y qué pasó después?"* del archivo (materia prima para el contenido
   "Enjambre vs. realidad").

### 6.1 El deep-dive del domingo (universo de 500)
- `config/universo_semanal.json`: **500 empresas** curadas + generadas, cada una
  con nombre, sector (en español) y contexto (descripción de negocio; las
  auto-generadas traen el resumen real de Yahoo como semilla, que la IA reescribe
  en español al elegirlas).
- Se elige por **ATENCIÓN**: la que más se movió esa semana, **dentro de la franja
  ~$1B–$50B** (`analisis_semanal.py`, `CAP_MIN`/`CAP_MAX`). La capitalización se
  **verifica en vivo** con Yahoo; si el mayor movedor supera $50B, se baja al
  siguiente en banda.
- **Descarga en paralelo** (`ThreadPoolExecutor`): rankear 500 empresas en serie
  tardaba ~6 min (y el ritual del domingo no terminaba); en paralelo baja a ~27 s.
  Lección: cualquier operación por-empresa sobre el universo grande debe ir en
  paralelo/acotada.
- Como el mercado **rota** por temas (memoria, IA, quantum, nuclear, defensa…),
  y el selector elige por atención, el deep-dive **cae solo en el tema caliente**
  de la semana. El universo está etiquetado con un campo `tema` para eso.

---

## 7. El Centro de Mando (panel) y el human-in-the-loop

- **URL:** `https://enjambre-motor.onrender.com/panel`. El acceso se controla con
  una **clave** que se pide dentro de la página: es el `ENJAMBRE_PIPELINE_TOKEN`
  (env var de Render).
- **Flujo de revisión (human-in-the-loop):** cada edición nace `pendiente`.
  Giorgio la revisa desde el **link del correo de revisión** (`/pulso/revisar/
  {token}`) o desde el panel, y decide **Aprobar** (envía a suscriptores) o
  **Descartar**. Estados: `pendiente → aprobada/enviada → descartada`.
- **Reenvío manual:** si una edición ya se envió y entran suscriptores nuevos, en
  `/pulso/revisar/{token}` aparece **"📤 Reenviar a todos"**
  (`pipeline.reenviar_a_suscriptores`, NO idempotente, reenvía a propósito).

---

## 8. Suscriptores y entregabilidad (lecciones caras)

- **Double opt-in:** al suscribirse, el correo nace **inactivo** hasta que la
  persona hace clic en **"Confirmar suscripción"**. Solo los **activos** reciben
  el newsletter. Estados por correo: activo / sin confirmar (pendiente) / baja.
- **Distinción clave:** el **correo de revisión** va al `PULSO_ADMIN_EMAIL` de
  Giorgio (llega siempre, sin importar suscripción). El **newsletter** va solo a
  suscriptores **confirmados**. Confundir esto lleva a "aprobé pero no me llegó".
- **Caso real:** el propio correo de Giorgio quedó marcado como **baja** (se hizo
  clic sin querer en desuscribirse en una prueba) → recibía la revisión pero no el
  newsletter. Solución: re-suscribirse por el formulario + confirmar.
- **Entregabilidad:** los newsletters (con imágenes y link de baja) suelen caer en
  **Promociones/Spam** de Gmail. Antes de meterle tráfico de marketing, hay que
  dejar el flujo suscribirse→confirmar→recibir 100% sólido (SPF/DKIM/DMARC de
  `diarioelpulso.com` bien puestos en Resend), o el embudo tiene fuga en la puerta.

---

## 9. Infraestructura, despliegue y "gotchas"

- **Motor:** Render (servicio `enjambre-motor`, Docker, plan Starter → no
  duerme). `render.yaml` es el blueprint (topes, env vars). **Auto-deploy desde
  `main` funciona** (el motor toma cada merge solo). URL:
  `https://enjambre-motor.onrender.com`.
- **Web:** Vercel, auto-deploy desde `main`.
  `https://enjambre-ai-agents.vercel.app`.
- **Correo:** Resend, remitente `El Pulso <hola@diarioelpulso.com>` (dominio
  propio verificado). `RESEND_WEBHOOK_SECRET` para aperturas/clics del panel.
- **Cron:** GitHub Actions (`.github/workflows/ritual-diario.yml`), 10:00 UTC =
  6:00 Chile, **lunes a domingo** (`1-5` diaria, `6` sábado, `0` domingo). Dispara
  `POST /api/pipeline` con `X-Pipeline-Token`. El motor corre el ritual en segundo
  plano y responde `{"estado":"iniciado"}` de inmediato (el Action solo confirma
  que arrancó; la edición tarda unos minutos).
- **La versión que corre el motor** = `RENDER_GIT_COMMIT`, visible en `GET /salud`
  → `"version"`. Sirve para saber si un merge ya se desplegó.
- **⚠️ Gotcha — la rama por defecto:** el repositorio tiene como rama por defecto
  una rama de trabajo (`claude/…`), no `main`. Esto confunde: los PRs se mergean a
  `main`, Render/Vercel despliegan `main`, pero el cron y algunas cosas miran la
  rama por defecto. **Recomendado: poner `main` como rama por defecto** en GitHub.
- **Topes de producción** (`render.yaml`, sitio público): `ENJAMBRE_MAX_SIM_DIA=5`,
  `ENJAMBRE_MAX_SIM_IP_HORA=3` (la muralla de la billetera con la URL abierta).
- **Claves en Render (env vars, `sync:false`, se pegan a mano):**
  `ANTHROPIC_API_KEY`, `ALPACA_API_KEY_ID/SECRET`, `RESEND_API_KEY`,
  `PULSO_ADMIN_EMAIL`, `RESEND_WEBHOOK_SECRET`, `BARCHART_API_KEY` (opcional),
  `ENJAMBRE_PIPELINE_TOKEN` (generado), `GITHUB_RESPALDO_TOKEN` (respaldo de
  calibración a la rama `respaldo-datos`).

### 9.1 Endpoints temporales de diagnóstico (POR LIMPIAR)
Se agregaron para depurar sin ver los logs de Render. Son de solo lectura y
protegidos con una clave fija (`revisar-pulso-2026`, no secreta). **Conviene
quitarlos** cuando ya no se necesiten:
- `GET /api/pulso/suscriptores?clave=…[&email=…]` — conteo de suscriptores y
  estado de un correo.
- (Ya retirado) `GET /api/pulso/diagnostico` — corría el ritual y reportaba el
  punto de falla.

El **`POST /pulso/reenviar/{token}`** y su botón SÍ son permanentes (feature real).

---

## 10. Estado actual (agosto 2026)

**Funcionando en producción, de lunes a domingo:**
- ✅ El motor transmite la simulación real por WebSocket; el enjambre 3D la
  renderiza en vivo. Toda simulación queda en SQLite.
- ✅ El Pulso sale solo cada día (3 formatos: diario, resumen sábado, deep-dive
  domingo), como borrador pendiente de aprobación.
- ✅ Correo de revisión → Giorgio aprueba → sale a suscriptores. Botón de reenvío.
- ✅ Universo de 500 empresas (verificadas $1–50B), selección por atención en
  paralelo (~27 s).
- ✅ Gráficos de precio reales, fundamentales verificados (Yahoo), filtro CMF con
  tests, disclaimer en todo.
- ✅ El archivo/hemeroteca ("El Enjambre dijo"), el duelo (dos escenarios), el
  widget embebible.
- ✅ **Bug del ThinkingBlock resuelto** (era la causa de que no saliera el correo
  de fin de semana).

**Suite de tests:** ~220 pruebas, verde.

**Pendiente / a vigilar:**
- Poner `main` como rama por defecto en GitHub.
- Quitar los endpoints temporales de diagnóstico.
- Afinar entregabilidad de Resend / dominio (SPF/DKIM/DMARC) antes de traccionar.
- La cuenta de Barchart es opcional (hoy todo funciona con Yahoo gratis).

---

## 11. Estrategia de crecimiento (GTM / redes sociales)

Objetivo: popularizar El Pulso (suscripciones) usando El Enjambre como gancho.

- **Marca de la cuenta:** "El Pulso · Diario de mercado" (coherente con el dominio
  `diarioelpulso.com`). El enjambre es el visual estrella dentro.
- **Canal #1: TikTok** (mejor alcance desde cero para video hipnótico), con
  **cross-post a Instagram Reels** (mismo video vertical). LinkedIn/X para el
  ángulo B2B. No dispersarse: uno bien hecho + reciclar.
- **El activo viral es el ENJAMBRE**, no las noticias (las noticias son commodity;
  el 3D es el moat). Liderar con "mira a 10.000 IA entrar en pánico".
- **Tres series de contenido:**
  1. *El Pulso del día* (diario, sale del correo; tono juguetón, "chismoso").
  2. *El Enjambre vs. la realidad* (formato estrella): el enjambre reacciona a un
     titular → se revela qué hizo el mercado de verdad → puntaje honesto. La
     herramienta **ya guarda** ese dato (campo "¿y qué pasó después?").
  3. *Construyendo el Enjambre* (build-in-public; "en calibración" como historia).
- **CMF también en redes:** siempre "experimento educativo, en calibración, no es
  asesoría ni predicción". Nunca "entonces compra X".
- **Automatización:** publicar solo no es trivial en TikTok/IG, pero programadores
  como **Metricool** (plan gratis) auto-publican por lote. La parte automatizable
  de verdad es **generar el borrador del post diario desde la edición de El
  Pulso** (que el motor lo escupa junto al correo). Video/voz: humano.
- **Diseño de las piezas:** se hacen en **Diseño Claude** (plantilla "En blanco",
  sistema "Broadsheet", 9:16), con prompts on-brand (paleta tinta #1b1410, dorado
  #e3c565, teal #2f7a6f, crema #f4efe4; Cormorant Garamond + Jost).

---

## 12. Cómo trabajar en este proyecto (reglas de oro)

Del `CLAUDE.md`, no negociables:
1. **Una sesión, una misión.** No avanzar de etapa sin instrucción explícita.
2. **Verificar todo.** Después de implementar: ejecutar, mostrar resultado,
   explicar en simple. Nunca decir "listo" sin evidencia.
3. **Commits como puntos de guardado**, mensaje descriptivo en español.
4. **Español primero** (comentarios, commits, explicaciones). Variables/funciones
   en inglés.
5. **Simplicidad ante todo.** La solución simple que funciona hoy > la
   arquitectura perfecta de mañana.
6. **Performance 3D:** reutilizar geometrías/materiales, vectores mutables con
   refs, `pixelRatio` limitado a `min(devicePixelRatio, 2)`. Objetivo 60fps en
   móvil de gama media.
7. **Presupuesto LLM:** máx ~100-120 llamadas por simulación.
8. **Explicarle a Giorgio en simple**, sin jerga, con analogías. Es director, no
   programador.

---

## 13. Glosario para Giorgio

- **agente** = inversionista simulado
- **tick** = un "latido" del mercado (una ronda de decisiones)
- **libro de órdenes** = la lista donde se cruzan compras y ventas
- **señal** = la opinión de un líder convertida en número (-1 a +1)
- **hechos estilizados** = las huellas digitales de un mercado real
- **instanced rendering** = truco para dibujar miles de partículas como una
- **double opt-in** = confirmar la suscripción con un clic (protege la reputación)
- **deep-dive** = el análisis a fondo del domingo
- **fundamentales** = ingresos, márgenes, EBITDA, deuda... la salud del negocio
- **rotación** = cuando el mercado mueve su atención de un tema a otro (IA, nuclear…)
- **ThinkingBlock** = el "razonamiento" que el modelo hace antes de responder
- **cron** = el robot que dispara el ritual a la misma hora cada día

---

*Rubicón Lab · El Enjambre · El Pulso · Documento de contexto profundo · agosto 2026*
