# CONTEXTO DEL PROYECTO — El Enjambre

> Documento de traspaso: todo lo que otro entorno (u otra sesión de IA)
> necesita para continuar el trabajo sin releer la historia completa.
> Complementa a `CLAUDE.md` (biblia del simulador) y a `CONTENIDO.md`
> (biblia de la capa de contenido). Cuenta **lo construido, cómo quedó y
> por qué**.
>
> Actualizado: julio 2026 · rama `claude/m-d-file-6z1e63` · commit de la Etapa 10.

---

## 1. Estado en una línea

**El producto está funcionalmente completo: etapas 0-4 (simulador) + 6-10
(capa de contenido) + blindaje de seguridad. 97 tests verdes.** Lo único
pendiente es del lado de Giorgio: el deploy (Render + Vercel) y las claves
externas (Alpaca, Barchart, Resend).

| Etapa | Qué |
|---|---|
| 0-1 | Motor + 5.000 agentes + hechos estilizados |
| 2 | Cerebros LLM + red de influencia |
| 3 | Enjambre 3D (instanced) |
| 4 | Integración WebSocket + deploy listo |
| — | Blindaje de seguridad (rate-limit, XSS, path traversal, DoS) |
| 6 | Persistencia SQLite + Alpaca + portero |
| 7 | El muro (portada) |
| 8 | El Pulso (newsletter) |
| — | La Redacción (análisis de mercado dinámico en el Pulso) |
| 9 | El archivo (hemeroteca) |
| 10 | El duelo + el widget |
| 5 | Reporte exportable — recogido dentro de la capa de contenido |

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
└── validation/                97 tests

web/                           Vite · Three.js · Tailwind 4 · GSAP
├── src/swarm/                 enjambre 3D instanced + datos/escenario espejo
├── src/muro/muro.js           portada: tarjetas, replay, on-demand, suscripción
├── src/archivo/archivo.js     hemeroteca + modo "armar duelo"
├── src/duelo/duelo.js         dos enjambres sincronizados + Reel (MediaRecorder)
├── src/widget/widget.js       iframe embebible (build separado widget.html)
├── src/ui/                    panel (reporte, voces, epílogo) + conexión WS
└── src/main.js                wiring + enrutamiento (?sim, /archivo, /duelo/...)

render.yaml + engine/Dockerfile   deploy motor (web + cron) en Render
web/vercel.json                   deploy web + CSP + rewrites SPA
docs/                             despliegue · contenido · seguridad · la-redaccion · contexto
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
- El tono ambiente sale del **léxico crudo del titular**, no del promedio.
- Léxico **bilingüe** (ES+EN): los cables de Alpaca llegan en inglés.
- Fallback obligatorio por arquetipo; caché en `brains/cache/`.

### 3.3 El contrato motor ↔ frontend (WebSocket)
Cliente: `{"tipo":"simular","titular","seed","ritmo","titular_id?"}`.
Servidor: texto `inicio` (100 líderes) → 150 frames binarios (`f32 precio ·
u32 tick · i8×5000`) → texto `fin` con reporte y `sim_id`. **El orden de
agentes es el contrato**: orden de creación (= agentes.json, líderes al
final), debe coincidir con `web/src/swarm/datos.js`. El replay reusa el
mismo formato de frame (`TAMANO_FRAME = 8+5000`), lo usan muro, archivo,
duelo y widget.

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

### 3.5 Seguridad (ver docs/seguridad.md)
Rate-limit HTTP por IP (IP real = último salto de X-Forwarded-For);
XSS neutralizado con `esc()` antes de todo `innerHTML` + CSP en
`vercel.json`; `sim_id` validado `^[0-9a-f]{16}$`; semáforo de 2
simulaciones concurrentes; WebSocket robusto ante basura; CORS restringido.
Tope on-demand **5/día** (la muralla de la billetera LLM).

## 4. Cómo correr y verificar

```bash
cd engine && source .venv/bin/activate
python -m pytest validation/ -q         # 97 tests (~3-4 min)
python simular.py 42                     # métricas de hechos estilizados
python -m contenido.pipeline            # el ritual (sin enviar correos)
python probar_portero.py                # log de veredictos del día
uvicorn server:app --port 8000          # motor
cd web && npm install && npm run dev     # web → localhost:5173
```

Números sanos: curtosis 4-9 · AC|r| lag1 0.15-0.45 · AC retornos |media|
< 0.1 · asimetría 1.2-3 · shock -0.9 → mínimo -7% a -18% con rebote ·
institucionales ~65-70% del volumen. E2E con navegador:
`npm run build && npx vite preview --port 4173` + Playwright
(`executablePath /opt/pw-browsers/chromium`, flags swiftshader).

## 5. Pendientes — todos del lado de Giorgio

1. **Deploy** (~10 min, `docs/despliegue.md`): Render (Blueprint lee
   `render.yaml`: web + cron) + Vercel (root `web`, `VITE_WS_URL`). Cerrar
   CORS con `ENJAMBRE_ORIGENES`.
2. **Claves** (todo con degradación a demo hasta que lleguen):
   - Alpaca (`ALPACA_API_KEY_ID/SECRET`) → titulares reales.
   - Barchart (`BARCHART_API_KEY`) → datos de mercado reales de La Redacción.
   - Resend (`RESEND_API_KEY`) + dominio verificado → el correo llega.
   - `ENJAMBRE_PIPELINE_TOKEN` (mismo valor en web y cron), opcional
     Telegram, opcional `ENJAMBRE_WIDGET_DOMINIOS` para embebido en medios.
3. **Verificar en dispositivo real**: el Reel del duelo (MediaRecorder no
   se certifica headless) y los 100 cerebros con API real (latencia < 15 s).
4. **Recomendado**: Cloudflare gratis delante de todo (DDoS volumétrico).

## 6. Deuda técnica consciente
- Rate-limit y tope en memoria de una instancia (Redis al escalar).
- Render free = disco efímero: el pipeline regenera el día; para archivo
  histórico persistente, subir de plan + disco en `/app/datos`.
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
