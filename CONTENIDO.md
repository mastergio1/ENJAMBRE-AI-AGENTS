# CONTENIDO.md — La Capa de Contenido de "El Enjambre"

> **Extensión oficial de `CLAUDE.md`. Leer ambos antes de escribir código.**
> `CLAUDE.md` define el simulador (etapas 0-5). Este archivo define la capa
> que lo convierte en un producto de visita diaria: el muro de noticias,
> la newsletter, el archivo histórico, los duelos y el widget embebible.
> Si algo aquí contradice a `CLAUDE.md`, gana `CLAUDE.md` y se pregunta.
>
> Estado de partida: etapas 0-4 completadas (27 tests verdes, commit `0f8527d`).
> Esta capa corresponde a las **etapas 6-10** del proyecto.

---

## 1. VISIÓN DE ESTA CAPA

El simulador es el espectáculo; el contenido es la razón para volver.
Hoy la web es una demo que se visita una vez. Con esta capa se convierte en
un sitio que se revisa cada mañana con el café: titulares del día, cada uno
con su enjambre reaccionando, un correo diario que llega solo, y un archivo
que acumula credibilidad con el tiempo.

**Principio económico rector:** las simulaciones del día se corren UNA vez
de madrugada y se sirven mil veces desde caché. El costo marginal de cada
visitante es cero. Todo el diseño técnico se subordina a este principio.

**Principio regulatorio rector (CMF Chile, NO NEGOCIABLE):** todo lo que
esta capa publica es *simulación educativa de comportamiento de masas*.
Prohibido en cualquier texto generado o fijo: "recomendamos", "deberías
comprar/vender", "el precio subirá/bajará", "predicción", "señal de
inversión", "oportunidad de compra". Vocabulario permitido: "el enjambre
simulado reaccionó", "los agentes simulados", "en esta simulación
educativa", "comportamiento simulado de masas". Cada pieza pública
(página, correo, widget, imagen social) lleva el disclaimer fijo:
*"Simulación educativa de comportamiento de masas con agentes de IA.
No constituye asesoría ni recomendación de inversión."* Debe existir un
test automático que verifique la presencia del disclaimer en cada plantilla.

## 2. REGLAS DE TRABAJO ADICIONALES

Heredan todas las de `CLAUDE.md` (una sesión una misión, verificar todo,
commits como puntos de guardado, español, simplicidad). Se agregan:

1. **Presupuesto de la capa de contenido:** máximo 3 simulaciones completas
   por día en el pipeline automático (~300-360 llamadas LLM/día ≈ centavos).
   El portero (sección 7) protege este presupuesto. Si un diseño necesita
   más, se rediseña.
2. **Nada se publica sin pasar por el filtro de vocabulario** (sección 1).
   El filtro es código (lista de términos prohibidos + test), no una
   promesa.
3. **Persistencia primero:** desde el primer commit de esta capa, TODA
   simulación (manual o automática) se guarda. El archivo histórico se
   construye solo si la persistencia existe desde el día uno.
4. **Degradación elegante:** si Alpaca no responde, el muro muestra las
   simulaciones de ayer con fecha visible. Si el motor está caído, la web
   sirve el último estado estático. Nunca una página en blanco.

## 3. ARQUITECTURA DE LA CAPA

```
enjambre/
├── engine/
│   ├── contenido/                  ← NUEVO paquete
│   │   ├── fuentes/
│   │   │   ├── alpaca.py           ← cliente Alpaca News API (WebSocket + REST)
│   │   │   └── telegram.py         ← oyente del canal Telegram de Giorgio (fase 2)
│   │   ├── portero.py              ← clasificador: ¿este titular amerita simulación?
│   │   ├── pipeline.py             ← el ritual de la madrugada (sección 6)
│   │   ├── persistencia.py         ← guarda/lee simulaciones (SQLite)
│   │   ├── boletin.py              ← genera y envía la newsletter
│   │   └── captura.py              ← render del "momento dramático" (imagen del enjambre)
│   ├── server.py                   ← se extiende con endpoints de contenido (sección 3.2)
│   └── datos/enjambre.db           ← SQLite (gitignored; en Render: disco persistente)
├── web/
│   └── src/
│       ├── muro/                   ← NUEVO: muro de noticias (sección 4)
│       ├── archivo/                ← NUEVO: hemeroteca (sección 5)
│       ├── duelo/                  ← NUEVO: comparador lado a lado (sección 8)
│       └── widget/                 ← NUEVO: build separado embebible (sección 9)
└── docs/contenido.md               ← guía de operación para Giorgio
```

### 3.1 El modelo de datos (SQLite — simple a propósito)

Una sola base, tres tablas. SQLite basta hasta decenas de miles de
simulaciones; migrar a Postgres es decisión futura, no de hoy.

```sql
-- Toda simulación que alguna vez corrió
CREATE TABLE simulaciones (
  id            TEXT PRIMARY KEY,   -- sha256(titular|seed) — igual que la caché de cerebros
  titular       TEXT NOT NULL,
  fuente        TEXT,               -- 'alpaca' | 'telegram' | 'manual' | 'duelo'
  fecha         TEXT NOT NULL,      -- ISO 8601 UTC
  seed          INTEGER NOT NULL,
  resumen_json  TEXT NOT NULL,      -- reporte final: dirección, volatilidad, % por tipo
  lideres_json  TEXT NOT NULL,      -- las 100 señales + frases (el oro editorial)
  serie_precios TEXT NOT NULL,      -- los 150 puntos de precio (para el gráfico 2D)
  frames_ref    TEXT,               -- ruta al archivo binario de frames (replay 3D)
  destacada     INTEGER DEFAULT 0   -- 1 si el pipeline la eligió para el día
);

-- Los titulares evaluados (incluso los rechazados por el portero — sirven de log)
CREATE TABLE titulares (
  id         TEXT PRIMARY KEY,
  titular    TEXT NOT NULL,
  fuente     TEXT NOT NULL,
  fecha      TEXT NOT NULL,
  simbolos   TEXT,                  -- tickers que Alpaca asocia a la noticia
  veredicto  TEXT NOT NULL,         -- 'simular' | 'descartar'
  motivo     TEXT,                  -- una frase del portero
  sim_id     TEXT REFERENCES simulaciones(id)
);

-- Suscriptores del boletín
CREATE TABLE suscriptores (
  email      TEXT PRIMARY KEY,
  fecha_alta TEXT NOT NULL,
  origen     TEXT,                  -- 'web' | 'widget' | 'manual'
  activo     INTEGER DEFAULT 1,
  token_baja TEXT NOT NULL          -- para el link de desuscripción de un clic
);
```

**Regla del replay:** los frames binarios de las 3 simulaciones destacadas
del día se conservan siempre (son el replay 3D del archivo). Para el resto,
solo `serie_precios` + `resumen_json` (el gráfico 2D basta). Esto mantiene
el disco bajo control: ~750 KB por simulación destacada, ~2 MB/día.

### 3.2 Endpoints nuevos en `server.py`

```
GET  /api/muro                  → titulares del día con estado (simulado/pendiente)
GET  /api/simulacion/{id}       → resumen + líderes + serie de precios
GET  /api/simulacion/{id}/replay→ frames binarios (para re-ver el enjambre en 3D)
POST /api/simular-titular       → simulación on-demand desde el muro (rate limit: 5/hora/IP)
GET  /api/archivo?mes=2026-07   → listado paginado de simulaciones pasadas
POST /api/suscribir             → alta a la newsletter (email + double opt-in)
GET  /api/baja/{token}          → desuscripción de un clic
GET  /api/duelo/{id_a}/{id_b}   → los dos resúmenes para el comparador
```

## 4. COMPONENTE 1 — EL MURO DE NOTICIAS *(la prioridad)*

**Qué es:** la nueva portada de la web. El feed de titulares bursátiles del
día; cada titular es una tarjeta con su estado.

**Anatomía de una tarjeta:**
- Titular + hora + fuente (Benzinga vía Alpaca) + tickers asociados.
- **Estado A — ya simulada** (las destacadas del pipeline): miniatura del
  momento dramático, dirección con flecha editorial (▲ ▼ ◆ neutral),
  "nivel de agitación" (bajo/medio/alto — traducción de la volatilidad),
  y la frase más jugosa de un líder con su arquetipo:
  *«El Doomer: "esto huele a 2008"»*. Clic → vista completa con replay 3D.
- **Estado B — no simulada:** botón "Ver reacción del enjambre" →
  `POST /api/simular-titular` → la tarjeta muestra el enjambre en vivo
  mientras corre (~10-15 s, el espectáculo ES la espera) → queda cacheada
  para todos los visitantes siguientes.
- **Estado C — descartada por el portero:** no aparece. El muro solo
  muestra lo que amerita.

**Diseño:** estética Rubicón (tinta, dorado, Cormorant/Jost). El muro es
una columna editorial tipo periódico, no una grilla de dashboard. La
simulación destacada del día ocupa el lugar del "titular de portada" con
el enjambre animándose en loop suave detrás (reutiliza el canvas existente
en modo replay, respetando `prefers-reduced-motion`).

**Orden del muro:** destacadas primero, luego cronológico descendente.
Máximo 12 tarjetas visibles; el resto pagina.

**Hecho cuando:** un visitante llega a la web a las 9:00, ve los titulares
de la mañana, la destacada del día ya viene simulada, toca otra y la ve
correr en vivo — y todo eso sin costo LLM extra para las visitas siguientes.

## 5. COMPONENTE 2 — EL ARCHIVO ("El Enjambre dijo")

**Qué es:** la hemeroteca. Toda simulación destacada queda para siempre,
navegable por mes, buscable por texto del titular y filtrable por ticker.

**La página de una simulación archivada contiene:**
1. El titular original, fecha y fuente.
2. El replay 3D (si es destacada) o el gráfico 2D de la sesión.
3. El reporte: dirección simulada, agitación, desglose por los 12 tipos.
4. Las 8 voces: la señal media y la mejor frase de cada arquetipo.
5. **La sección "¿Y qué pasó después?"** — al inicio, manual: un campo de
   texto que Giorgio completa cuando quiere ("el S&P cerró -1,2% ese día").
   Automatizarla con datos de mercado reales es una mejora futura, NO parte
   de esta etapa. Cuando existe, se muestra lado a lado con la simulación
   SIEMPRE bajo el rótulo "comparación educativa" — nunca "acierto" ni
   "predicción" (vocabulario CMF).

**Por qué importa:** es el activo compuesto del proyecto. Cada día suma
una página indexable (SEO en español sobre titulares financieros — casi
sin competencia), y en 6 meses es la prueba de seriedad ante cualquier
cliente B2B.

**Hecho cuando:** existe `/archivo`, cada simulación destacada tiene URL
propia y compartible, y el buscador encuentra "Fed" en simulaciones de
hace un mes.

## 6. COMPONENTE 3 — "EL PULSO DEL ENJAMBRE" (la newsletter)

**Qué es:** un correo diario (L-V, 8:00 AM Chile) generado y enviado sin
intervención humana. Es la máquina de leads B2B disfrazada de contenido:
cada suscriptor es un prospecto que ya entendió el producto.

### 6.1 El ritual de la madrugada (`pipeline.py`, corre 6:30 AM Chile)

```
1. RECOLECTAR   titulares de las últimas 18 h (Alpaca News REST).
2. FILTRAR      el portero evalúa cada uno (sección 7) → top 3 del día.
3. SIMULAR      las 3 destacadas, seeds fijas del día (reproducibilidad),
                guardando todo vía persistencia.py.
4. CAPTURAR     captura.py renderiza el momento dramático de cada una
                (tick de máxima agitación) → PNG 1200×630 con marca de
                agua "El Enjambre · Rubicón Lab" (sirve también de
                Open Graph image de la página).
5. REDACTAR     boletin.py arma el correo desde plantilla (sección 6.2).
                Los textos variables pasan por el filtro de vocabulario.
6. ENVIAR       a suscriptores activos.
7. PUBLICAR     marca las 3 como destacadas → aparecen en muro y archivo.
8. AVISAR       resumen de ejecución al Telegram de Giorgio: qué se
                simuló, cuántos correos salieron, errores si hubo.
```

Implementación del cron: worker de Render con schedule (o GitHub Action
programada que llama a un endpoint protegido con token — decidir por costo;
documentar la elección en `docs/contenido.md`).

### 6.2 La plantilla del correo

Asunto: `🐝 El Pulso — [titular estrella en 6 palabras]`

```
[Cabecera: wordmark El Enjambre, fecha en Cormorant itálica]

LA REACCIÓN DEL DÍA
[Imagen del momento dramático — clic lleva a la simulación]
[Titular] · Fuente · [▲▼◆] · Agitación: [nivel]
En esta simulación, el [X]% de los agentes retail entró en modo
venta en los primeros 40 ticks. [1 frase generada, filtrada]

LAS VOCES
«[frase]» — El Doomer          «[frase]» — El Institucional
[las 2 más contrastantes del día, elegidas por distancia entre señales]

TAMBIÉN REACCIONÓ A
· [Titular 2] → [▲▼◆] · [link]
· [Titular 3] → [▲▼◆] · [link]

[CTA] Ver el enjambre en vivo →
[Disclaimer CMF completo · Desuscribirse en un clic]
```

HTML de correo: tablas y estilos inline (los clientes de correo no soportan
CSS moderno), oscuro con acento dorado, ancho 600 px, probado en Gmail
móvil primero.

### 6.3 Envío

Empezar con **Resend** (API simple, tier gratuito 3.000 correos/mes,
dominio verificado con SPF/DKIM — sin esto el correo cae a spam y el
proyecto entero pierde). Double opt-in obligatorio: alta → correo de
confirmación → activo. La lista vive en `suscriptores` (SQLite), no en
un servicio externo: los leads son del negocio.

**Hecho cuando:** Giorgio se suscribe con su correo personal, recibe el
Pulso a las 8:00 sin haber tocado nada, el correo se ve bien en su
teléfono, y el link de baja funciona a la primera.

## 7. EL PORTERO (`portero.py`)

El guardián del presupuesto. Decide qué titulares ameritan simulación.

**Diseño en dos pisos:**
1. **Piso léxico (gratis, elimina ~80%):** descarta duplicados
   (similitud > 0.85 con titulares de las últimas 48 h), noticias sin
   contenido de mercado (listas "top 5 acciones", contenido promocional),
   y todo lo que no menciona ni empresa, ni sector, ni macro.
2. **Piso Haiku (centavos, decide el resto):** una llamada a
   `claude-haiku-4-5` con lote de hasta 20 titulares, que devuelve JSON:
   `{"titular_id": ..., "veredicto": "simular"|"descartar",
   "impacto": 1-10, "motivo": "una frase"}`.
   Se simulan los 3 de mayor impacto del día. Empates: el más reciente.

**Criterio de impacto (en el prompt del portero):** afecta a un índice o
sector completo > empresa mega-cap > empresa puntual; macro (tasas,
inflación, empleo, geopolítica) puntúa alto; rumores y opiniones puntúan
bajo salvo que vengan de fuente institucional.

Todo veredicto (incluso descartes) se registra en `titulares` — ese log
es el material para calibrar el portero después.

**Hecho cuando:** en un día normal el portero recibe ~100+ titulares,
gasta 1-2 llamadas Haiku en lotes, y las 3 elegidas son razonables a ojos
de Giorgio revisando el log.

## 8. COMPONENTE 4 — EL DUELO DE ESCENARIOS

**Qué es:** dos titulares lado a lado, dos enjambres reaccionando en
paralelo, mismo seed. *"¿Qué asusta más al mercado simulado: inflación o
desempleo?"*

**Especificación:**
- Ruta `/duelo/{id_a}-vs-{id_b}` con URL compartible.
- En desktop: dos canvas lado a lado, sincronizados tick a tick, con los
  dos gráficos de precio superpuestos abajo. En móvil: apilados, con un
  selector para alternar (dos canvas 3D simultáneos en móvil rompen el
  presupuesto de fps — el gobernador existente manda).
- El constructor de duelos es interno al inicio (Giorgio elige dos
  simulaciones del archivo); abrirlo al público es fase futura.
- **Botón "exportar Reel":** graba 12 segundos verticales (9:16) de los
  dos enjambres + titulares sobreimpresos + marca de agua. Material listo
  para que Mailyn y Sonalys publiquen. (Implementación: captura de canvas
  a WebM con MediaRecorder; conversión a MP4 es tarea del equipo social,
  no del servidor.)

**Hecho cuando:** existe un duelo publicado con URL propia, y el export
genera un video vertical que se ve digno en un teléfono.

## 9. COMPONENTE 5 — EL WIDGET EMBEBIBLE

**Qué es:** el producto para medios. Un iframe del enjambre reaccionando
al titular del día, que un medio económico incrusta en sus artículos.

**Especificación:**
- Build separado (`web/src/widget/` → `widget.js`, < 200 KB gzip):
  versión mínima del canvas + titular + firma "El Enjambre by Rubicón Lab"
  + link a la web + disclaimer CMF SIEMPRE visible (no negociable ni
  configurable por el cliente).
- Solo lee simulaciones cacheadas (`GET /api/simulacion/{id}` + replay).
  El widget JAMÁS dispara simulaciones nuevas — un iframe en un sitio de
  alto tráfico no puede tocar el presupuesto LLM.
- Parámetros: `?sim=<id>` (fija) o `?modo=hoy` (la destacada del día).
- Anti-abuso: lista blanca de dominios permitidos (header `Referer`)
  administrable por variable de entorno. Dominios fuera de lista ven la
  versión con CTA grande "Consigue el widget para tu medio".
- El widget es también el caballo de Troya del pitch: se le manda a un
  periodista un link de prueba funcionando en 30 segundos.

**Hecho cuando:** un HTML de prueba de 5 líneas en cualquier dominio de
la lista blanca muestra el enjambre del día funcionando a 60 fps.

## 10. HOJA DE RUTA DE LA CAPA — ETAPAS 6 A 10

> Mismo formato que `CLAUDE.md`: una sesión una misión, cada etapa con su
> "hecho cuando". El orden importa: la persistencia va primero porque el
> archivo solo existe si se guarda desde el día uno.

**Etapa 6 · Persistencia + fuentes (semana 1)**
SQLite + `persistencia.py` + guardar toda simulación desde ya + cliente
Alpaca News + el portero con su log.
*Prompt sugerido:* «Lee CLAUDE.md y CONTENIDO.md. Etapa 6: implementa la
persistencia SQLite con las 3 tablas de la sección 3.1, engancha el guardado
en server.py para toda simulación, y crea el cliente de Alpaca News con el
portero de dos pisos. Pruébalo con titulares reales del día y muéstrame el
log de veredictos.»
*Hecho cuando:* toda simulación queda en la base, y el portero procesa un
día real de titulares con veredictos razonables.

**Etapa 7 · El muro (semanas 2-3)**
La nueva portada: tarjetas, estados A/B/C, simulación on-demand con rate
limit, replay desde caché.
*Hecho cuando:* el criterio de la sección 4.

**Etapa 8 · El Pulso (semana 4)**
`pipeline.py` completo (los 8 pasos), `captura.py`, plantilla de correo,
Resend con dominio verificado, double opt-in, formulario de alta en la web.
*Hecho cuando:* el criterio de la sección 6.3.

**Etapa 9 · El archivo (semana 5)**
`/archivo` navegable + página por simulación + buscador + campo manual
"¿y qué pasó después?".
*Hecho cuando:* el criterio de la sección 5.

**Etapa 10 · Duelo + widget (semanas 6-7)**
El comparador con export vertical, y el build embebible con lista blanca.
*Hecho cuando:* los criterios de las secciones 8 y 9.

## 11. COSTOS DE OPERACIÓN DE LA CAPA

| Ítem | Detalle | USD/mes |
|---|---|---|
| Simulaciones diarias | 3/día × ~110 llamadas Sonnet ≈ 7.000/mes | ~5-15 |
| El portero | 1-2 llamadas Haiku/día en lote | < 1 |
| Resend (correo) | gratis hasta 3.000 correos/mes; luego ~20 | 0-20 |
| Disco persistente Render | ~2 MB/día de frames destacados | 0-7 |
| Alpaca News API | tier gratuito | 0 |
| **Total capa de contenido** | | **~5-45** |

## 12. MÉTRICAS DE ÉXITO (revisar mensualmente con Giorgio)

- Suscriptores del Pulso y su tasa de apertura (meta inicial: 100
  suscriptores, apertura > 40%).
- Visitas recurrentes al muro (mismo visitante ≥ 3 días/semana).
- Simulaciones on-demand disparadas por visitantes (apetito real).
- Duelos compartidos y reproducciones de los Reels.
- Medios con el widget instalado (la métrica B2B que paga las demás).

---
*Rubicón Lab · El Enjambre · CONTENIDO.md v1 · Julio 2026*
