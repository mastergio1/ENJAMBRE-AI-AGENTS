# CONTEXTO DEL PROYECTO — El Enjambre

> Documento de traspaso: todo lo que otro entorno (u otra sesión de IA)
> necesita para continuar el trabajo sin releer la historia completa.
> Complementa a `CLAUDE.md` (biblia del simulador) y a `CONTENIDO.md`
> (biblia de la capa de contenido). Cuenta **lo construido, cómo quedó y
> por qué**.
>
> Actualizado: 15 de julio de 2026 · rama `claude/m-d-file-6z1e63` (espejo
> en `main`, que es la que despliega) · tras el deploy real, la
> calibración en marcha (backtest + corrector) y los Sprints 1-3 de UX.

---

## 1. Estado en una línea

**EN PRODUCCIÓN, en fase de pruebas reales, con la calibración en marcha.**
Motor en Render y web en Vercel (auto-deploy desde `main`). Los 100 líderes
leen con IA real (claude-sonnet-5) *cuando hay saldo de Anthropic* — hoy el
saldo está agotado y el enjambre corre con el respaldo léxico (por diseño,
nunca se cae). La calibración acumula: **12 exámenes históricos rendidos
(8/12 direcciones acertadas)** guardados en la caja fuerte de GitHub.

| Pieza | URL |
|---|---|
| Web (Vercel) | https://enjambre-ai-agents.vercel.app |
| Motor (Render free — duerme, ~50 s de bostezo) | https://enjambre-motor.onrender.com |
| Caja fuerte de calibración | rama `respaldo-datos` → `datos/calibracion.json` |

| Hito | Estado |
|---|---|
| Etapas 0-10 del roadmap (motor, cerebros, 3D, contenido) | ✅ completas |
| Marca Rubicón Lab + blindaje de seguridad + auditoría | ✅ |
| DEPLOY REAL (Render + Vercel) | ✅ julio 2026 |
| Cerebros IA funcionando (arreglo `temperature`) | ✅ |
| Comparación con el mercado real (TradingView en el reporte) | ✅ |
| Corrector automático + libreta de calificaciones | ✅ |
| Caja fuerte GitHub (rama `respaldo-datos`) | ✅ |
| Despertador diario (GitHub Actions, 6:00 Chile L-V) | ✅ |
| Backtest histórico (55 exámenes 2001-2025, por tandas) | ✅ 12/55 rendidos |
| Blindaje sin-saldo (la calibración nunca mide al respaldo) | ✅ |
| Sprints 1-3 de UX (nav, tour, cámara, escena nítida, B2B) | ✅ |

## 2. Mapa del código

```
engine/                        Python 3.11 · Mesa 3 · FastAPI (venv en engine/.venv)
├── config/agentes.json        la mezcla: 13 tipos, 5.000 agentes, 8 arquetipos
├── market/order_book.py       libro de órdenes (SOLO órdenes límite, §3.1)
├── agents/                    base + los 12 tipos de reglas + el líder LLM
├── brains/                    arquetipos, cerebro (API async + caché), fallback léxico
├── network/red.py             grafo scale-free (líderes→seguidores + pares retail)
├── model.py                   MercadoEnjambre (el modelo central Mesa)
├── server.py                  FastAPI: WS /ws + REST (incl. admin: diagnostico,
│                              pipeline, corrector, libreta, backtest, contactos)
├── contenido/
│   ├── persistencia.py        SQLite: simulaciones, titulares, suscriptores,
│   │                          briefs, contactos (B2B) · reaccion_real (calibración)
│   ├── portero.py             clasificador 2 pisos (léxico + Haiku) del día
│   ├── limites.py             topes on-demand (⚠️ abiertos en fase de pruebas)
│   ├── seguridad.py           IP real, rate-limit, validación, cabeceras
│   ├── pipeline.py            ritual de la madrugada (+ corrector integrado)
│   ├── corrector.py           califica destacadas vs mercado real + libreta
│   ├── backtest.py            exámenes históricos por tandas (freno de gasto)
│   ├── backtest_eventos.json  55 eventos 2001-2025 (24 neg / 21 pos / 10 neutras)
│   ├── respaldo.py            caja fuerte GitHub (fusiona, nunca pierde)
│   ├── boletin.py · captura.py · redaccion.py · notificar.py · disparar_pulso.py
│   ├── vocabulario.py         filtro CMF (prohibidos ES+EN + disclaimer)
│   └── fuentes/               alpaca.py (noticias + barras) · stooq.py (histórico
│                              pre-2016, sin clave) · barchart.py
├── validation/                138 tests
└── Dockerfile · requirements  imagen no-root, deps fijas

web/                           Vite · Three.js · Tailwind 4 · GSAP
├── src/swarm/enjambre.js      enjambre instanced (NEUTRO/COMPRA/VENTA/LIDER)
├── src/muro/muro.js           portada: tarjetas, replay, Pulso, ORGANIZACIONES
│                              (form B2B), pie, firma Rubicón
├── src/archivo/ · src/duelo/ · src/widget/
├── src/ui/panel.js            reporte (acciones post-sim, TradingView), tooltip
│                              táctil con señal/convicción, HUD, avisos
├── src/ui/navegacion.js       barra fija (Inicio·Muro·Archivo·Duelo·El Pulso)
├── src/ui/tour.js             tour de bienvenida 5 pasos (1ª visita)
├── src/ui/guia.js             "¿Cómo funciona?" (botón ?, ya no auto-abre)
├── src/ui/conexion.js         WS con paciencia (cold start ~50 s de Render)
└── src/main.js                wiring, OrbitControls + parallax, bloom/estela
                               afinados, señal de vida anti-pantalla-negra

.github/workflows/ritual-diario.yml   despertador: 10:00 UTC L-V + botón manual
.github/workflows/backtest.yml        tanda de backtest a demanda (botón/API)
render.yaml · web/vercel.json · docs/
```

## 3. Decisiones técnicas y POR QUÉ (lo caro de re-aprender)

### 3.1 El mercado — solo órdenes límite (Chiarella-Iori)
Toda orden es límite con "urgencia" (`precio*(1±urgencia)`, exponencial
`min(expovariate(125),0.06)`); lo no cruzado reposa y expira a los 4 ticks.
Cierre = última transacción. Referencia de agentes = cierre del tick
anterior. El arbitrajista (SMA-3, umbral 0.006) borra tendencias
predecibles: si se debilita, cae el test de no-autocorrelación.

### 3.2 Los cerebros y la noticia
- Modelos: `claude-sonnet-5` (líderes) + `claude-haiku-4-5-20251001` (portero).
- **⚠️ LECCIÓN CARA:** `claude-sonnet-5` NO acepta `temperature`/`top_p`/
  `top_k` (400 y todos caen al respaldo silenciosamente). No re-agregarlos.
  Diagnóstico: `GET /api/diagnostico` (admin) prueba la clave en un comando;
  `_reportar_primera_falla()` deja la causa en el log de Render.
- El caché solo guarda voces de la API (nunca fallback). Semilla aleatoria
  por corrida → voces distintas. Fallback bilingüe con 3 variantes por ramo.
- **`fuente` (api/cache/fallback) viaja con cada líder guardado** — es lo
  que permite el blindaje sin-saldo (§3.9).

### 3.3 Contrato motor ↔ frontend
WS: texto `inicio` (líderes) → frames binarios (f32 precio · u32 tick ·
i8×5000, orden de creación = contrato con datos.js) → texto `fin`.
Replay reutiliza el formato (muro, archivo, duelo, widget). Observatorio:
sesión continua con noticias encima (máx 2, autocierre ~8 min).

### 3.4 La capa de contenido
Persistencia primero (toda simulación se guarda; id = sha256(titular|seed)
[:16]) · SQLite WAL · portero de 2 pisos elige las 3 del día · muro con
replay cacheado y on-demand · Pulso con double opt-in y humano en el lazo ·
La Redacción (3 roles, el número manda, CMF) · duelo (2 escenas, Reel) ·
widget (build aparte, lista blanca CORS).

### 3.5 Seguridad
Rate-limit por IP real (último salto XFF) · XSS: esc() antes de TODO
innerHTML (guards en tests, incl. ticker con lista blanca `tickerSeguro`) ·
sim_id `^[0-9a-f]{16}$` · SQL parametrizado · hmac.compare_digest para el
token admin · contenedor no-root · deps fijas. Pendientes del deploy:
CSP del widget, dominio definitivo en ENJAMBRE_ORIGENES.

### 3.6 La marca
Fondo tinta cálida #1b1916 · teal #6fa89e único acento UI · enjambre:
grafito #5c574f / viridiano #4f9e86 / rosa-arcilla #c47b7b / líderes
DORADOS #e3c565 · Cormorant Garamond + Jost · firma .rl-* al pie del muro
(`URL_ESTUDIO` aún marcador).

### 3.7 El deploy real y sus lecciones
- Render (Blueprint, solo servicio web; cron del Pulso pendiente de Resend)
  + Vercel (root `web`, `VITE_WS_URL`). Auto-deploy desde `main`.
- **El disco free de Render es efímero: CADA deploy lo borra.** De ahí: la
  caja fuerte (§3.8), el anti-repetición del backtest, y que el muro
  amanezca vacío tras un día de muchos pushes (el despertador lo rellena
  a las 6:00; también a mano: workflow "El ritual del día" → Run workflow).
- **⚠️ MODO PRUEBAS:** `ENJAMBRE_MAX_SIM_DIA=500`, `IP_HORA=100` en
  render.yaml. **Volver a 5 y 3 antes del lanzamiento público.**
- Frontend anti-pantalla-negra: Google Fonts asíncronas (en 4G débil una
  hoja colgada dejaba TODO negro) + señal de vida inline en index.html.
- iOS: maximum-scale=1 + campos ≥16px (el zoom automático descuadraba todo).

### 3.8 La calibración (el corazón del roadmap actual)
- **Corrector automático** (`corrector.py`): ≥1 día después de cada
  destacada mide el movimiento real (2 ruedas; base = cierre previo) con
  Alpaca; guarda `reaccion_real` y redacta el epílogo CMF-limpio si no hay
  uno manual. Corre en el ritual y con POST /api/corrector (token).
- **Backtest** (`backtest.py` + 55 eventos 2001-2025): tandas pequeñas
  (freno TANDA_MAXIMA=10, ~$0.10-0.20 por examen), precio real ANTES de
  simular (sin dato = no gasta), recientes primero, Alpaca→Stooq (pre-2016),
  y NO repite lo ya respaldado en GitHub (anti doble-gasto tras borrones).
  Workflow manual "Backtest histórico (tanda)". Claude puede dispararlo.
- **Libreta** (`corrector.libreta()` / GET /api/libreta): casos, aciertos
  de dirección (umbral plano 0.3%), magnitudes medias, separando EN VIVO
  vs HISTÓRICO, y excluyendo lo simulado con respaldo.
- **Caja fuerte** (`respaldo.py`): tras cada examen/corrección sube el JSON
  fusionado a la rama `respaldo-datos` (NUNCA main: redeployaría el motor).
  Lectura pública sin token; escritura con GITHUB_RESPALDO_TOKEN
  (fine-grained, Contents RW solo este repo, ya configurado en Render).
- **Primeros hallazgos (12 casos, anecdótico aún):** 8/12 direcciones;
  clava macro dramática (aranceles 2025: -12.4% vs -10.4% real) pero
  SUBESTIMA euforias corporativas (Nvidia +16.8% real vs -0.1% sim) y
  EXAGERA macro tibia (Fed en pausa: -7.4% sim vs +1.4% real). Diales
  candidatos: FOMO ante earnings, sensibilidad léxica a matices Fed.
- **Ronda 1 de ajuste de diales:** con ~30-50 casos (los 55 históricos +
  los vivos diarios). Regla de CLAUDE.md §7: ajustar parámetros de
  conducta, jamás hardcodear; los hechos estilizados no se rompen.

### 3.9 Blindaje sin-saldo (estado ACTUAL: sin saldo de Anthropic)
Sin saldo, el enjambre funciona con el respaldo léxico (HUD "· respaldo").
Para que eso jamás contamine la calibración:
- el corrector etiqueta cada nota con `cerebros: ia|respaldo` y la libreta
  EXCLUYE lo de respaldo;
- el backtest NO guarda exámenes rendidos sin IA y detiene la tanda
  (`sin_ia` en el resultado y en el log de Render).
Al recargar saldo todo se reanuda solo; los exámenes saltados se rinden
de verdad en la siguiente tanda.

### 3.10 UX (Sprints 1-3, completos)
Barra de navegación sobre los overlays (z=48) · tour de bienvenida 5 pasos
(reemplaza el auto-open de la guía; localStorage) · OrbitControls acotado
conviviendo con el parallax (dblclick devuelve el mando) · escena
despejada: bloom 0.5/0.3/umbral 0.72, estela 0.55→0.90 solo en pánico,
fog 0.014 (la "niebla" que reportó Giorgio eran los tres apilados) ·
tooltip táctil con señal y convicción · acciones post-reporte (otro
titular / armar duelo / copiar enlace) · pie del muro · sección B2B
"El Enjambre para tu organización" → POST /api/contacto (tabla contactos,
aviso Telegram opcional, GET /api/contactos con token) · focus-visible.

## 4. Cómo correr y verificar

```bash
cd engine && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest validation/ -q          # 138 tests (~5 min)
python simular.py 42                      # hechos estilizados
uvicorn server:app --port 8000            # motor
cd web && npm install && npm run dev      # web → localhost:5173
```

Números sanos: curtosis 4-9 · AC|r| lag1 0.15-0.45 · asimetría 1.2-3 ·
shock -0.9 → mínimo -7% a -18% con rebote. E2E: `npm run build && npx vite
preview` + Playwright (`/opt/pw-browsers/chromium-*/chrome-linux/chrome`).

Operación remota (Claude puede hacerlo vía GitHub):
- Llenar el muro: workflow "El ritual del día" → Run workflow.
- Tanda de backtest: workflow "Backtest histórico (tanda)".
- Ver avance: `datos/calibracion.json` en la rama `respaldo-datos`.

## 5. Pendientes

**Ahora mismo:**
1. **Recargar saldo de Anthropic** → vuelven las voces IA y se reanudan
   las tandas (~43 exámenes restantes ≈ $5-9 USD).

**Antes del lanzamiento público (no negociables):**
2. Topes a 5/día y 3/hora/IP en render.yaml.
3. Regenerar claves de Alpaca (expuestas en un chat) y rotar
   ENJAMBRE_PIPELINE_TOKEN (parcial en capturas).
4. Puntos de auditoría en vivo: CSP del widget · dominio en
   ENJAMBRE_ORIGENES.

**Para completar el producto:**
5. Resend (clave + dominio) → El Pulso; re-agregar el cron a render.yaml.
6. Barchart (clave) → datos reales de La Redacción.
7. Disco persistente de Render ($7/mes) — agosto, con la calibración seria.
8. Informe de calibración #1 + ajuste de diales (con ~30-50 casos).
9. Decisión de marca: destino de la firma (URL_ESTUDIO).
10. Verificar el Reel del duelo en dispositivo real; Cloudflare delante.

## 6. Deuda técnica consciente
- Rate-limit/topes en memoria de 1 instancia (Redis al escalar).
- Disco efímero: hemeroteca y suscriptores se pierden por deploy hasta el
  disco persistente (la calibración NO: caja fuerte).
- Órdenes en reposo no reservan efectivo (acotado por expiración).
- El mensaje de un commit perdió la palabra "fuente" (backticks en shell);
  sin efecto en el código.

## 7. Convenciones
Español en comentarios/commits/explicaciones; nombres de dominio del motor
en español (`comprar_mercado`). Commits como puntos de guardado. Nunca
"listo" sin evidencia. Explicar a Giorgio en simple, con analogías.
**Nada de lenguaje de recomendación de inversión** (filtro CMF con tests).
La calibración solo mide IA real, nunca al respaldo.

---
*Rubicón Lab · El Enjambre · contexto.md · 15 de julio de 2026*
