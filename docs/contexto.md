# CONTEXTO DEL PROYECTO — El Enjambre

> Documento de traspaso: todo lo que otro entorno (u otra sesión de IA)
> necesita para continuar el trabajo sin releer la historia completa.
> Complementa a `CLAUDE.md` (biblia del simulador) y a `CONTENIDO.md`
> (biblia de la capa de contenido). Cuenta **lo construido, cómo quedó y
> por qué**.
>
> Actualizado: 14 de julio de 2026 · rama `claude/m-d-file-6z1e63` (espejo
> en `main`, que es la que despliega) · tras el DEPLOY REAL, el arreglo de
> los cerebros IA y la comparación con el mercado real (TradingView).

---

## 1. Estado en una línea

**El producto está EN PRODUCCIÓN y en fase de pruebas reales.** Motor vivo
en Render, web viva en Vercel, ambos con auto-deploy desde `main`. Los 100
líderes leen con IA real (claude-sonnet-5), el muro publica las noticias
del día, y el reporte compara la reacción del enjambre con el gráfico real
del símbolo. 115 tests verdes.

| Pieza | URL |
|---|---|
| Web (Vercel) | https://enjambre-ai-agents.vercel.app |
| Motor (Render, plan free — duerme y tarda ~50 s en despertar) | https://enjambre-motor.onrender.com |

| Etapa | Qué |
|---|---|
| 0-1 | Motor + 5.000 agentes + hechos estilizados |
| 2 | Cerebros LLM + red de influencia |
| 3 | Enjambre 3D (instanced) |
| 4 | Integración WebSocket + deploy listo |
| 6 | Persistencia SQLite + Alpaca + portero |
| 7 | El muro (portada) |
| 8 | El Pulso (newsletter) |
| — | La Redacción (análisis de mercado dinámico en el Pulso) |
| 9 | El archivo (hemeroteca) |
| 10 | El duelo + el widget |
| 5 | Reporte exportable — recogido dentro de la capa de contenido |
| — | **Marca Rubicón Lab** (paleta, firma, rediseño del enjambre) |
| — | **Blindaje de seguridad** + **auditoría previa al despliegue** |
| — | **DEPLOY REAL** (Render + Vercel, julio 2026) + guía "¿Cómo funciona?" |
| — | **Cerebros IA funcionando** (arreglo `temperature`) + comparación TradingView |

## 2. Mapa del código

```
engine/                        Python 3.11 · Mesa 3 · FastAPI (venv en engine/.venv)
├── config/agentes.json        la mezcla: 13 tipos, 5.000 agentes, 8 arquetipos
├── market/order_book.py       libro de órdenes (SOLO órdenes límite, §3.1)
├── agents/                    base + los 12 tipos de reglas + el líder LLM
├── brains/                    arquetipos, cerebro (API async + caché), fallback léxico
├── network/red.py             grafo scale-free (líderes→seguidores + pares retail)
├── model.py                   MercadoEnjambre (el modelo central Mesa)
├── server.py                  FastAPI: WS /ws + todos los endpoints REST
├── contenido/                 ← LA CAPA DE CONTENIDO (etapas 6-10)
│   ├── persistencia.py        SQLite: simulaciones, titulares, suscriptores, briefs
│   ├── portero.py             clasificador 2 pisos (léxico + Haiku) del día
│   ├── limites.py             tope on-demand 5/día global, 3/hora IP
│   ├── seguridad.py           IP real, rate-limit HTTP, validación, cabeceras
│   ├── pipeline.py            el ritual de la madrugada (8 pasos)
│   ├── boletin.py             El Pulso: HTML del correo + envío Resend
│   ├── captura.py             imagen del "momento dramático" (Pillow)
│   ├── redaccion.py           La Redacción: análisis de mercado (3 roles)
│   ├── notificar.py           aviso a Giorgio por Telegram
│   ├── disparar_pulso.py      el cron golpea el endpoint protegido
│   ├── vocabulario.py         filtro CMF (prohibidos ES+EN + disclaimer)
│   └── fuentes/               alpaca.py (noticias) · barchart.py (datos de mercado)
├── validation/                115 tests
├── requirements.txt           deps de PRODUCCIÓN, versiones fijas (==)
├── requirements-dev.txt       pytest/httpx (NO van en la imagen)
├── Dockerfile                 imagen no-root (uid 10001)
└── .dockerignore              fuera .venv, datos, caché, secretos, dev-deps, tests

web/                           Vite · Three.js · Tailwind 4 · GSAP
├── src/swarm/enjambre.js      enjambre 3D instanced (paleta de marca, §3.6)
├── src/muro/muro.js           portada: tarjetas, replay, on-demand, suscripción, FIRMA
├── src/archivo/archivo.js     hemeroteca + modo "armar duelo"
├── src/duelo/duelo.js         dos enjambres sincronizados + Reel (MediaRecorder)
├── src/widget/widget.js       iframe embebible (build separado widget.html)
├── src/ui/                    panel (reporte, voces, epílogo, tooltip) + conexión WS
├── src/style.css              tokens de marca + firma .rl-* + divisor "cruce"
└── src/main.js                wiring + enrutamiento (?sim, /archivo, /duelo/...)

render.yaml + engine/Dockerfile   deploy motor (web + cron) en Render
web/vercel.json                   deploy web + CSP + rewrites SPA
docs/                             despliegue · contenido · seguridad · la-redaccion ·
                                  auditoria-pre-deploy · contexto
```

## 3. Decisiones técnicas y POR QUÉ (lo caro de re-aprender)

### 3.1 El mercado — solo órdenes límite (Chiarella-Iori)
Los primeros libros explotaban (+8.000%/tick, precios negativos). Diseño
final: **toda orden es límite con "urgencia"** (`precio*(1±urgencia)`,
urgencia exponencial `min(expovariate(125),0.06)`); lo no cruzado reposa y
**expira a los 4 ticks**. Precio de cierre = **última transacción** (VWAP y
punto medio fallan). El precio de referencia de los agentes es el cierre
del tick anterior, no `libro.ultimo_precio`. El **arbitrajista** (SMA-3,
umbral 0.006) borra tendencias predecibles: si se debilita, el test 3 cae.

### 3.2 Los cerebros y la noticia
- `model.aplicar_titular()`: sync usa `asyncio.run`; el servidor usa
  `analizar_titular_async` — **nunca la sync dentro de un event loop**.
- Modelos: `claude-sonnet-5` (líderes) + `claude-haiku-4-5-20251001` (portero).
- **⚠️ LECCIÓN CARA:** `claude-sonnet-5` eliminó los parámetros de sampling
  (`temperature`/`top_p`/`top_k`) — enviarlos devuelve **400** y TODOS los
  líderes caen silenciosamente al fallback. No volver a agregarlos. El
  síntoma era: clave válida pero HUD siempre "· respaldo" y frases enlatadas.
  `_reportar_primera_falla()` deja la causa real en el log de Render;
  `GET /api/diagnostico` (solo-admin) prueba la clave con una llamada mínima.
- **El caché solo guarda voces de la API, nunca fallback**: una falla
  pasajera no congela frases enlatadas para ese (titular, arquetipo, semilla).
- La semilla de los líderes es aleatoria por corrida (`_semilla_lider`):
  dos corridas del mismo titular dan voces distintas.
- El tono ambiente sale del **léxico crudo del titular**, no del promedio.
- Léxico **bilingüe** (ES+EN): los cables de Alpaca llegan en inglés.
- Fallback obligatorio por arquetipo (3 variantes de frase por ramo, se
  sortean por semilla); caché en `brains/cache/` (efímero en Render free).

### 3.3 El contrato motor ↔ frontend (WebSocket)
Cliente: `{"tipo":"simular","titular","seed","ritmo","titular_id?"}`.
Servidor: texto `inicio` (100 líderes) → 150 frames binarios (`f32 precio ·
u32 tick · i8×5000`) → texto `fin` con reporte y `sim_id`. **El orden de
agentes es el contrato**: orden de creación (= agentes.json, líderes al
final), debe coincidir con `web/src/swarm/datos.js`. El replay reusa el
mismo formato de frame (`TAMANO_FRAME = 8+5000`), lo usan muro, archivo,
duelo y widget. Hay además un **modo observatorio** (`{"tipo":"observatorio"}`
/ `noticia` / `detener`): el enjambre late indefinidamente y recibe noticias
encima; máx 2 sesiones, auto-cierre ~8 min.

### 3.4 La capa de contenido
- **Persistencia primero**: TODA simulación se guarda. `id =
  sha256(titular|seed)[:16]`.
- **SQLite en WAL + busy_timeout**, esquema una sola vez por proceso.
- **El portero** (2 pisos) es la inteligencia del día: elige las 3
  destacadas Y define el universo de La Redacción (sus tickers).
- **El muro**: destacadas con replay desde caché; on-demand en vivo que
  queda cacheado (Estado B→A). Degrada elegante si el motor duerme.
- **El Pulso** (ritual de 8 pasos): imagen Pillow (2D, no GL headless),
  Resend, double opt-in, humano en el lazo (aprobar antes de enviar).
- **La Redacción**: 3 roles (reportero/verificador/editor). El número
  manda (viene de Barchart, no de un texto). **Selección dinámica**: el
  universo del día = telón fijo (índices/commodities) + tickers de las
  noticias relevantes del portero. Mezcla MOVIMIENTOS (con cifra) y
  EVENTOS (adquisiciones: el hecho es la noticia con fuente). Línea CMF:
  se cuenta el pasado, "qué observa hoy" es atención, nunca predicción.
- **El cron NO comparte disco con la web** en Render free: golpea
  `POST /api/pipeline` (token) y el ritual corre DENTRO del proceso web.
- **El duelo**: dos Enjambre en una escena, offset en X, replay
  sincronizado por un índice de cuadro compartido; en móvil, uno a la vez
  (dos escenas 3D rompen el fps). Reel = MediaRecorder a WebM 9:16.
- **El widget**: build Vite separado (`widget.html`), solo lee caché,
  jamás simula; lista blanca vía CORS (`ENJAMBRE_WIDGET_DOMINIOS`) — fuera
  de lista, CORS bloquea los datos → muestra el CTA.

### 3.5 Seguridad y auditoría previa al despliegue (ver docs/auditoria-pre-deploy.md)
Controles de base: rate-limit HTTP por IP (IP real = último salto de
X-Forwarded-For); XSS neutralizado con `esc()` antes de todo `innerHTML` +
CSP en `vercel.json`; `sim_id` validado `^[0-9a-f]{16}$`; SQL 100%
parametrizado; path traversal con doble muralla; semáforos (2 simulaciones,
2 observatorios); tope on-demand **5/día** (la muralla de la billetera LLM).

La **auditoría previa al deploy** cerró 5 puntos en código:
- Escapado del **tooltip del líder** (frase del LLM iba cruda a innerHTML).
- Token de admin comparado en **tiempo constante** (`hmac.compare_digest`).
- **Dependencias fijas** (`==`) + dev-deps fuera de la imagen.
- **Antirreenvío** del correo de confirmación (ventana 10 min por dirección).
- **Contenedor no-root** + `.dockerignore`.

Quedan 4 puntos para el **momento del deploy** (necesitan probar contra
Vercel/Render): **A** exceptuar `widget.html` de `frame-ancestors 'none'`
(si no, el widget no se puede incrustar) · **D** confirmar que la IP tras el
proxy de Render es la real · **G** fijar el dominio real en `ENJAMBRE_ORIGENES`
· **F/H** notas menores (límites en memoria de 1 instancia, tope de conexiones
WS). Detalle y niveles en `docs/auditoria-pre-deploy.md`.

### 3.6 La marca Rubicón Lab (paleta, firma, enjambre)
Se aplicó el manual de marca. **Aplicación "reverse"**: fondo tinta cálida,
el **teal** (`#6fa89e`, "el río") como único acento de la interfaz (reemplaza
el dorado anterior). Tipografías Cormorant Garamond + Jost (ya eran las de la
marca). Decisiones de color:
- **La fachada** (botones, sparkline, bordes, acentos de UI) = teal de marca.
- **El enjambre en acción** (decisión de Giorgio, versión "seria" para público
  B2B): reposo en grafito cálido `#5c574f`, compra en verde viridiano
  `#4f9e86`, venta en rosa-arcilla `#c47b7b`, y **los líderes conservan su
  DORADO** `#e3c565` como faros — el único acento cálido, distinto del teal de
  la interfaz, marca quién guía a la manada.
- **La firma "Creada por Rubicón Lab"** (§10 del manual) al pie del muro:
  snippet oficial scopeado `.rl-*`, hereda `currentColor` (sin teal), cae al
  isotipo `R|` en ≤520 px. Enlace en `URL_ESTUDIO` (`muro.js`) — hoy apunta a
  Instagram como marcador; **decisión abierta**: confirmar dominio o handle.
- Coherencia de marca también en la imagen del "momento dramático"
  (`captura.py`) y el correo El Pulso (`boletin.py`).
- Los colores del enjambre viven como constantes en `web/src/swarm/enjambre.js`
  (`NEUTRO/COMPRA/VENTA/LIDER`): cambiar la paleta es tocar esas 4 líneas.

### 3.7 El deploy real (julio 2026) y lo aprendido
- **Render** (Blueprint desde `render.yaml`, solo el servicio web por ahora;
  el cron del Pulso se agrega cuando Resend esté listo). **Vercel** (root
  `web`, framework Vite, `VITE_WS_URL=wss://enjambre-motor.onrender.com/ws`).
  Ambos auto-despliegan al empujar a `main`.
- **Cold start:** el plan free de Render duerme el motor; el frontend
  conecta "con paciencia" (`_conectarConPaciencia`, reintentos hasta 75 s)
  y avisa "despertando el motor…" en vez de caer al demo a los 3 s.
- **⚠️ MODO PRUEBAS ACTIVO:** los topes están abiertos en `render.yaml`
  (`ENJAMBRE_MAX_SIM_DIA=500`, `ENJAMBRE_MAX_SIM_IP_HORA=100`). **ANTES del
  lanzamiento público volver a 5 y 3** — cada simulación ≈ 100 llamadas LLM;
  esos topes son la muralla de la billetera.
- El pipeline se dispara a mano con
  `curl -X POST https://enjambre-motor.onrender.com/api/pipeline -H "X-Pipeline-Token: <token>"`
  (el token vive en el Environment de Render). Puebla el muro con las 3
  destacadas del día.
- La guía **"¿Cómo funciona?"** (`web/src/ui/guia.js`) se abre sola en la
  primera visita (localStorage) — explica el enjambre a un retail que entra
  sin contexto.

### 3.8 Comparación con el mercado real + la ruta de calibración
- **Lo construido:** las simulaciones que nacen de un titular del muro
  exponen su ticker en `/api/simulacion/<id>` (`simbolos`, viene de la tabla
  `titulares`), y el reporte muestra el mini-gráfico REAL del símbolo
  (widget oficial de TradingView) bajo el rótulo "Comparación educativa ·
  el mercado real". El ticker pasa por lista blanca (`tickerSeguro` en
  `panel.js`) antes de tocar HTML o la config del widget — con guard de test.
  Las simulaciones manuales no lo muestran (sin ticker asociado).
- **Línea CMF:** la nota junto al gráfico dice explícitamente que es un
  ejercicio educativo, no predicción ni validación. Mantener SIEMPRE.
- **La ruta de calibración acordada (el "entrenamiento" honesto):** el
  enjambre no predice precios; se calibra contra la realidad. Circuito:
  (1) cada destacada guarda su ticker → (2) capturar automáticamente el
  movimiento real 1-2 días después vía Alpaca y guardarlo como epílogo →
  (3) con 30-50 casos, libreta de calificaciones (% de aciertos de
  dirección, sesgos de sobre/sub-reacción) → (4) ajustar parámetros de
  conducta de la mezcla (§4 de CLAUDE.md), jamás hardcodear el resultado.
- **El corrector automático (paso 2) YA EXISTE** (`contenido/corrector.py`):
  corre dentro del ritual diario; espera ≥1 día, mide 2 ruedas con barras
  IEX de Alpaca (`variacion_real` en fuentes/alpaca.py: base = cierre previo
  a la noticia), guarda `reaccion_real` (JSON) y redacta el epílogo CMF-limpio
  solo si no hay uno manual. Sin datos aún → reintenta en la próxima corrida.
  La libreta (paso 3) también existe: `corrector.libreta()` / `GET /api/libreta`.

## 4. Cómo correr y verificar

```bash
cd engine && source .venv/bin/activate
pip install -r requirements-dev.txt      # deps de prod + pytest/httpx
python -m pytest validation/ -q          # 115 tests (~5 min)
python simular.py 42                      # métricas de hechos estilizados
python -m contenido.pipeline             # el ritual (sin enviar correos)
python probar_portero.py                 # log de veredictos del día
uvicorn server:app --port 8000           # motor
cd web && npm install && npm run dev      # web → localhost:5173
```

Números sanos: curtosis 4-9 · AC|r| lag1 0.15-0.45 · AC retornos |media|
< 0.1 · asimetría 1.2-3 · shock -0.9 → mínimo -7% a -18% con rebote ·
institucionales ~65-70% del volumen. E2E con navegador:
`npm run build && npx vite preview --port 4173` + Playwright
(`executablePath /opt/pw-browsers/chromium-*/chrome-linux/chrome`).

## 5. Pendientes

**Antes del lanzamiento público (no negociables):**
1. **Volver los topes a 5/día y 3/hora/IP** en `render.yaml` (hoy 500/100
   por la fase de pruebas). Es la muralla de la billetera LLM.
2. **Regenerar las claves de Alpaca** (se pegaron en un chat) y rotar el
   `ENJAMBRE_PIPELINE_TOKEN` (parcialmente visible en capturas).
3. Cerrar los puntos de auditoría que se prueban en vivo: **A** exceptuar
   `widget.html` de `frame-ancestors` · **D** confirmar IP real tras el
   proxy de Render · **G** dominio definitivo en `ENJAMBRE_ORIGENES`.

**Para completar el producto:**
4. **Resend** (clave + dominio verificado) → habilita El Pulso; entonces
   re-agregar el cron a `render.yaml` (bloque en `docs/despliegue.md`).
5. **Barchart** (clave) → datos reales de La Redacción (hoy demo).
6. ~~Epílogo automático~~ **CONSTRUIDO** (julio 2026): `contenido/corrector.py`
   corre dentro del ritual diario (y a demanda vía `POST /api/corrector`);
   guarda el movimiento real en `simulaciones.reaccion_real` y redacta el
   epílogo si no hay uno manual. La libreta: `GET /api/libreta` (admin).
   Primera ronda de ajuste de diales: inicios de agosto (con 30-50 casos).
7. **Mejoras UX propuestas tras el primer test** (lista de Giorgio):
   navbar + footer, tour de bienvenida, controles 3D táctiles, estados de
   carga, formulario educadores, CTA premium (cuidando CMF). Sin empezar.
8. **Decisión de marca abierta**: destino de la firma (`URL_ESTUDIO` en
   `muro.js`) — hoy marcador a Instagram.
9. **Verificar en dispositivo real**: el Reel del duelo (MediaRecorder).
10. **Recomendado**: Cloudflare gratis delante de todo (DDoS volumétrico).

## 6. Deuda técnica consciente
- Rate-limit y tope en memoria de una instancia (Redis al escalar);
  `seguridad.limpiar()` existe pero no se programa aún.
- Render free = disco efímero: el pipeline regenera el día; para archivo
  histórico persistente, subir de plan + disco en `/app/datos` (con permiso
  de escritura para el uid 10001 del contenedor no-root).
- Órdenes límite en reposo no reservan efectivo (acotado por expiración).
- La demo de Barchart es un snapshot fijo: los EVENTOS ya varían por día,
  los MOVIMIENTOS varían recién con la clave real.

## 7. Convenciones
Español en comentarios/commits/explicaciones. El motor usa **nombres en
español** (decisión temprana, consistente: `comprar_mercado`,
`senal_social`). Commits como puntos de guardado por avance funcional.
Nunca "listo" sin correr los tests. Explicar a Giorgio en simple, con
analogías. **Nada de lenguaje de recomendación de inversión** en ninguna
pieza pública (filtro CMF con test).
