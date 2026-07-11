# CONTEXTO DEL PROYECTO — El Enjambre

> Documento de traspaso: todo lo que otro entorno (u otra sesión de IA)
> necesita para continuar el trabajo sin releer la historia completa.
> Complementa a `CLAUDE.md` (la biblia del simulador) y a `CONTENIDO.md`
> (la biblia de la capa de contenido). Este archivo cuenta **lo que ya se
> construyó, cómo quedó y por qué**.
>
> Actualizado: julio 2026 · rama `claude/m-d-file-6z1e63` · commit `cbf40af`

---

## 1. Estado en una línea

**Etapas 0-4 (simulador) + 6-8 (capa de contenido) completadas y
verificadas. 71 tests verdes.** Más un blindaje de seguridad completo.
Falta: ejecutar el deploy (requiere las cuentas de Giorgio), las claves
de Alpaca (estaba en mantenimiento), y las Etapas 9-10.

| Etapa | Qué | Estado | Commit |
|---|---|---|---|
| 0 | Setup repo + entornos | ✅ | `8f8b017` |
| 1 | Motor + 5.000 agentes + hechos estilizados | ✅ | `cdab026` |
| 2 | Cerebros LLM + red de influencia | ✅ | `a39911f` |
| 3 | Enjambre 3D (instanced) | ✅ | `2aeee97` |
| 4 | Integración WebSocket + deploy listo | ✅ integración / ⏳ deploy | `0f8527d` |
| 6 | Persistencia SQLite + Alpaca + portero | ✅ | `582a74d` |
| 7 | El muro (nueva portada) | ✅ | `30a1954` |
| — | Blindaje de seguridad | ✅ | `e6a906d` |
| 8 | El Pulso (newsletter) | ✅ | `cbf40af` |
| 5 | Reporte exportable | ⏳ (se recoge dentro de contenido) | — |
| 9 | El archivo (hemeroteca) | ⏳ | — |
| 10 | Duelo + widget | ⏳ | — |

## 2. Mapa del código

```
engine/                        Python 3.11 + Mesa 3 + FastAPI (venv en engine/.venv)
├── config/agentes.json        la mezcla: 13 tipos, 5.000 agentes, 8 arquetipos
├── market/order_book.py       libro de órdenes (SOLO órdenes límite, ver §3.1)
├── agents/base.py             AgenteBase: cartera, órdenes con urgencia, red social
├── agents/reglas.py           los 12 tipos de reglas (CLAUDE.md sección 4)
├── agents/lider.py            LiderOpinion: señal/confianza/frase
├── brains/arquetipos.py       8 personalidades: prompt LLM + a quién arrastran
├── brains/cerebro.py          API Anthropic async (100 llamadas paralelas) + caché
├── brains/fallback.py         léxico ES+EN por arquetipo — la simulación nunca cae
├── network/red.py             grafo scale-free: líderes→seguidores + pares retail
├── model.py                   MercadoEnjambre: el modelo central (Mesa)
├── server.py                  FastAPI: WS /ws + endpoints REST del muro y El Pulso
├── contenido/                 ← LA CAPA DE CONTENIDO (etapas 6-8)
│   ├── persistencia.py        SQLite: simulaciones, titulares, suscriptores
│   ├── portero.py             clasificador de 2 pisos (léxico + Haiku)
│   ├── limites.py             tope on-demand: 5/día global, 3/hora IP
│   ├── seguridad.py           IP real, rate-limit HTTP, validación, cabeceras
│   ├── pipeline.py            el ritual de la madrugada (8 pasos)
│   ├── boletin.py             El Pulso: HTML del correo + envío Resend
│   ├── captura.py             imagen del "momento dramático" (Pillow)
│   ├── notificar.py           aviso a Giorgio por Telegram
│   ├── disparar_pulso.py      el cron golpea el endpoint protegido
│   ├── vocabulario.py         filtro CMF (términos prohibidos + disclaimer)
│   └── fuentes/alpaca.py      cliente Alpaca News (degrada a demo)
├── simular.py                 CLI de calibración (métricas de hechos estilizados)
├── demo_titular.py            demo de consola
├── probar_portero.py          log de veredictos del portero
└── validation/                71 tests

web/                           Vite + Three.js + Tailwind 4
├── src/swarm/                 enjambre 3D instanced + datos/escenario espejo
├── src/muro/muro.js           la portada: tarjetas, replay, on-demand, suscripción
├── src/ui/panel.js            input, HUD, reporte, avisos (con escape XSS)
├── src/ui/conexion.js         cliente WebSocket + urlApi()
└── src/main.js                wiring, gobernador fps, prefers-reduced-motion

render.yaml + engine/Dockerfile   deploy motor (web + cron) en Render
web/vercel.json                   deploy web + CSP anti-XSS
docs/                             despliegue.md · contenido.md · seguridad.md · contexto.md
```

## 3. Decisiones técnicas y POR QUÉ (lo caro de re-aprender)

### 3.1 El mercado — solo órdenes límite (diseño Chiarella-Iori)
Los primeros libros de órdenes explotaban (+8.000%/tick, precios
negativos). Diseño final: **toda orden es límite con "urgencia"**
(`precio*(1±urgencia)`, urgencia exponencial `min(expovariate(125),
0.06)`); lo no cruzado reposa y **expira a los 4 ticks**. Precio de cierre
= **última transacción** (VWAP y punto medio bid/ask fallan). El precio de
referencia de los agentes es el cierre del tick anterior, no
`libro.ultimo_precio`. El **arbitrajista** (SMA-3, umbral 0.006) es el
"policía" que borra tendencias predecibles: si se debilita, el test 3 cae.

### 3.2 Los cerebros y la noticia
- `model.aplicar_titular()`: sync usa `asyncio.run`; el servidor usa
  `analizar_titular_async` — **nunca la sync dentro de un event loop**.
- El tono ambiente (`model.sentimiento`) sale del **léxico crudo del
  titular**, no del promedio de líderes.
- Léxico **bilingüe** (ES+EN): los cables de Alpaca llegan en inglés.
  Contexto de tasas: "sube"/"raises" son negativas si hay "tasa"/"rate".
- Fallback obligatorio por arquetipo; caché en `brains/cache/` (gitignored).

### 3.3 La red de influencia
Grafo scale-free con conexión preferencial; retardo 1-4 ticks, atenuación
0.7 por salto, máx 2 saltos (cola en `model.cola_senales`). Institucionales
(tipos 1-6, 12) fuera de la red (`vecinos == []`). La manada mira las
**acciones reales** de sus vecinos, no el flujo global.

### 3.4 El contrato motor ↔ frontend (WebSocket)
Cliente manda `{"tipo":"simular","titular","seed","ritmo","titular_id?"}`.
Servidor: texto `inicio` (100 líderes) → 150 frames binarios (`f32 precio
· u32 tick · i8×5000`) → texto `fin` con reporte y `sim_id`. **El orden de
agentes es el contrato**: orden de creación (= orden de agentes.json,
líderes al final), y debe coincidir con `web/src/swarm/datos.js`. Si se
cambia la mezcla, cambiar AMBOS lados.

### 3.5 La capa de contenido (etapas 6-8)
- **Persistencia primero**: TODA simulación se guarda. `id =
  sha256(titular|seed)[:16]` (igual que la caché de cerebros).
- **SQLite en WAL + busy_timeout**, esquema creado una sola vez por
  proceso (no por request) — evita `database is locked` y es rápido.
- **El portero** (2 pisos): léxico gratis (duplicados >0.85, promocional,
  sin mercado) + Haiku en lote de 20 (heurístico bilingüe si no hay API).
  Los tickers de la fuente cuentan como señal de mercado. Todo veredicto
  se registra en la tabla `titulares`.
- **El muro**: destacadas (pipeline) con replay 3D desde caché; pendientes
  con on-demand en vivo que queda cacheado (Estado B→A). Degrada elegante
  si el motor duerme.
- **El Pulso**: ritual de 8 pasos; imagen del momento dramático (Pillow,
  2D — no GL headless); correo por Resend con filtro CMF; double opt-in.
- **El cron NO comparte disco con la web** en Render free: por eso solo
  golpea `POST /api/pipeline` (token `ENJAMBRE_PIPELINE_TOKEN`) y el ritual
  corre DENTRO del proceso web, sobre la misma base que sirve el muro.

### 3.6 Seguridad (blindaje, commit `e6a906d`)
Ver `docs/seguridad.md`. Puntos clave: rate-limit HTTP por IP (la IP real
es el **último salto** de X-Forwarded-For, anti-spoofing); XSS neutralizado
con `esc()` antes de todo `innerHTML` + CSP estricta en `vercel.json`;
`sim_id` validado `^[0-9a-f]{16}$` (anti path-traversal); semáforo de 2
simulaciones concurrentes; WebSocket robusto ante entrada basura; CORS
restringido. El tope on-demand es **5/día** (decisión de Giorgio: es la
muralla de la billetera LLM).

## 4. Cómo correr y verificar

```bash
cd engine && source .venv/bin/activate
python -m pytest validation/ -q        # 71 tests (~2 min)
python simular.py 42                    # métricas de hechos estilizados
python demo_titular.py "..."            # demo de consola
python probar_portero.py               # log de veredictos del día
python -m contenido.pipeline           # el ritual (sin enviar correos)
python -m contenido.pipeline --enviar  # el ritual + envío real

# servidor + web en local
uvicorn server:app --port 8000            # terminal 1
cd web && npm install && npm run dev      # terminal 2 → localhost:5173
```

Números de referencia sanos: curtosis 4-9 · AC|r| lag1 0.15-0.45 ·
AC retornos |media| < 0.1 · asimetría 1.2-3 · shock -0.9 → mínimo -7% a
-18% con rebote parcial · institucionales ~65-70% del volumen.

Verificación e2e con navegador: `npm run build && npx vite preview
--port 4173` + Playwright (`executablePath /opt/pw-browsers/chromium`,
flags swiftshader en headless).

## 5. Pendientes y prerrequisitos de Giorgio

1. **Deploy** (~10 min, `docs/despliegue.md`): Render (Blueprint lee
   `render.yaml`: servicio web + cron) + Vercel (root `web`,
   `VITE_WS_URL`). Cerrar CORS con `ENJAMBRE_ORIGENES` al dominio final.
2. **Claves de Alpaca** (estaba en mantenimiento): al volver, pegar
   `ALPACA_API_KEY_ID` + `ALPACA_API_SECRET_KEY` → el muro pasa a
   titulares reales sin tocar código.
3. **El Pulso en producción**: cuenta de **Resend** + **dominio**
   verificado (SPF/DKIM), pegar `RESEND_API_KEY`; copiar el
   `ENJAMBRE_PIPELINE_TOKEN` generado del servicio web al cron.
4. **Recomendado**: Cloudflare gratis delante de todo (DDoS volumétrico).

## 6. Deuda técnica consciente
- Rate-limit y tope en memoria de una instancia (mover a Redis al escalar).
- Render free = disco efímero: el pipeline regenera el día; para archivo
  histórico persistente, subir de plan + disco en `/app/datos`.
- Órdenes límite en reposo no reservan efectivo (acotado por expiración y
  topes de cordura).
- Sin poda de simulaciones viejas (bounded por el tope diario).

## 7. Convenciones
Español en comentarios/commits/explicaciones. El motor usa **nombres en
español** (decisión temprana, consistente: `comprar_mercado`,
`senal_social`) — mantener consistencia antes que la regla inglés. Commits
como puntos de guardado por avance funcional. Nunca "listo" sin correr los
tests. Explicar a Giorgio en simple, con analogías. **Nada de lenguaje de
recomendación de inversión** en ninguna pieza pública (filtro CMF con test).
