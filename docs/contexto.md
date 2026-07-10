# CONTEXTO DEL PROYECTO — El Enjambre

> Documento de traspaso: todo lo que otro entorno (u otra sesión de IA)
> necesita para continuar el trabajo sin releer la historia completa.
> Complementa a `CLAUDE.md` (la biblia: visión y reglas) — este archivo
> cuenta **lo que ya se construyó, cómo quedó y por qué**.
>
> Actualizado: julio 2026 · rama `claude/m-d-file-6z1e63` · commit `0f8527d`

---

## 1. Estado en una línea

**Etapas 0-4 del roadmap completadas y verificadas (27 tests pasan).**
Falta: ejecutar el deploy real (10 min con cuentas de Giorgio, guía en
`docs/despliegue.md`) y la Etapa 5 (demo vendible: reporte exportable + pulido).

| Etapa | Estado | Evidencia |
|---|---|---|
| 0 — Setup repo + entornos | ✅ | commit `8f8b017` |
| 1 — Motor + mezcla de agentes | ✅ | 5 hechos estilizados pasan (commit `cdab026`) |
| 2 — Cerebros LLM + red de influencia | ✅ | titular negativo -3.5% vs positivo +5.9% media 6 semillas (`a39911f`) |
| 3 — Enjambre 3D | ✅ | 3 draw calls, gobernador de fps verificado en vivo (`2aeee97`) |
| 4 — Integración + deploy listo | ✅ integración / ⏳ deploy | e2e verificado con Chromium+uvicorn (`0f8527d`) |
| 5 — Demo vendible | ⏳ | 3 escenarios precargados ya existen; falta reporte exportable |

## 2. Mapa del código

```
engine/                        Python 3.11 + Mesa 3 + FastAPI (venv en engine/.venv)
├── config/agentes.json        la mezcla: 13 tipos, 5.000 agentes, 8 arquetipos
├── market/order_book.py       libro de órdenes (SOLO órdenes límite, ver §3.1)
├── agents/base.py             AgenteBase: cartera, órdenes con urgencia, red social
├── agents/reglas.py           los 12 tipos de reglas (sección 4 de CLAUDE.md)
├── agents/lider.py            LiderOpinion: señal/confianza/frase, opera con convicción
├── brains/arquetipos.py       8 personalidades: prompt LLM + a quién arrastran
├── brains/cerebro.py          API Anthropic async (100 llamadas paralelas) + caché
├── brains/fallback.py         léxico ES por arquetipo — la simulación NUNCA se cae
├── network/red.py             grafo scale-free: líderes→seguidores + pares retail
├── model.py                   MercadoEnjambre: el modelo central (Mesa)
├── server.py                  FastAPI + WS /ws: streaming binario por tick + reporte
├── simular.py                 CLI de calibración (métricas de hechos estilizados)
├── demo_titular.py            demo de consola: un titular mueve el enjambre
└── validation/                27 tests: setup, hechos estilizados, red, cerebros, servidor

web/                           Vite + Three.js + Tailwind 4 (npm i en web/)
├── src/swarm/datos.js         mezcla falsa espejo (mismo orden/cantidades que el motor)
├── src/swarm/escenario.js     léxico JS espejo del fallback (modo demo local)
├── src/swarm/enjambre.js      la escena: 3 InstancedMesh, órbitas, ola, colores
├── src/ui/panel.js            input, chips, HUD+sparkline, tooltip, reporte, gráfico 2D
├── src/ui/conexion.js         cliente WS del motor real (timeout 3 s → demo local)
└── src/main.js                wiring, gobernador fps, prefers-reduced-motion

render.yaml + engine/Dockerfile   deploy del motor (Render, plan free)
web/vercel.json                   deploy de la web (Vercel) — VITE_WS_URL en el panel
docs/despliegue.md                guía paso a paso para Giorgio
```

## 3. Decisiones técnicas y POR QUÉ (lo caro de re-aprender)

### 3.1 El mercado — diseño Chiarella-Iori (solo órdenes límite)

Historia: los primeros 3 intentos de libro de órdenes **explotaron**
(precios de +8.000% por tick, precios negativos). Causas y remedios, en orden:

1. "Liquidez residual" con impacto por orden → se componía cientos de veces
   por tick → **eliminada por completo**.
2. Diseño final: **toda orden es límite con "urgencia"** (cuánto está
   dispuesto a cruzar el libro: `precio*(1±urgencia)`). Lo no cruzado
   reposa dando liquidez y **expira a los 4 ticks** (`VIDA_ORDEN`).
3. Urgencia por defecto: **exponencial** `min(expovariate(125), 0.06)` —
   la cola larga hace que el ajuste de precio se complete en 1-2 ticks
   (sin ella quedaba momentum artificial, AC≈+0.7).
4. Precio de cierre del tick = **última transacción** (`ultimo_precio`).
   Se probó VWAP (suaviza → AC+ mecánico) y punto medio bid/ask (queda
   anclado a los MM → curtosis 1.7). La última transacción es el único
   que funciona.
5. El **precio de referencia de los agentes** es el cierre del tick
   anterior (`model.historial_precios[-1]`), NO `libro.ultimo_precio`
   (rebota demasiado intra-tick).

### 3.2 Calibración anti-predictibilidad (test 3, el más difícil)

La autocorrelación de retornos fue el hueso duro. Aprendizajes:

- **Cualquier presión direccional persistente + market maker que ajusta
  lento = deriva predecible.** Hasta el fondo pasivo la generaba.
- Remedio principal: el **arbitrajista** ahora desvanece desviaciones de
  MUY corto plazo (referencia SMA-3, umbral 0.006, cada tick, tamaño
  hasta 0.25 del capital). Es el "policía del precio". Si se toca, el
  test 3 se cae.
- MM con sesgo de inventario fuerte (0.12) y spread con tope 0.08.
- El rumor (`senal_social`) decae rápido: ×0.75 por tick.
- El test 3 se evalúa **en conjunto**: |media entre semillas| < 0.1 y
  ninguna trayectoria > 0.2 (una sola corrida de 600 ticks tiene
  varianza muestral alta — no es hardcodeo, es estadística).

### 3.3 Los cerebros y la noticia

- `model.aplicar_titular(titular)`: los líderes leen vía
  `brains.cerebro.analizar_titular` (sync usa `asyncio.run`; el servidor
  usa `analizar_titular_async` y pasa `respuestas=` precalculadas —
  **nunca llamar la versión sync dentro de un event loop**).
- **El tono ambiente (`model.sentimiento`) sale del léxico crudo del
  titular, NO del promedio de líderes** — los contrarians/optimistas
  neutralizaban el promedio y las quiebras no asustaban a los miedosos.
- Sesgo de negatividad en `recibir_noticia` (noticias malas ×1.4): motor
  de la asimetría de pánico (test 4).
- Las noticias graves dañan el valor fundamental V de los
  fundamentalistas (`0.3*sentimiento*0.02` por tick) — sin esto el
  mercado "olvida" el shock y rebota al 100% (test 5 falla).
- Léxico: ojo con contexto de tasas — "sube"/"alza" son negativas si el
  titular menciona tasas (chequeado sobre el titular ORIGINAL completo).
- Caché de respuestas: `engine/brains/cache/respuestas.json` (gitignored),
  clave sha256(titular|arquetipo|semilla_del_líder).

### 3.4 La red de influencia

- Líderes → seguidores con **conexión preferencial** (scale-free);
  cantidad por arquetipo en `brains/arquetipos.py` (`seguidores`).
- Manada y FOMO tienen garantizados 1-2 líderes en su red.
- Propagación: cola en `model.cola_senales` — retardo 1-4 ticks,
  atenuación 0.7 por salto, máximo 2 saltos (líder→seguidor→pares).
- Tipos 1-6 y 12 institucionales/no-sociales: `vecinos == []` (test lo
  verifica). La manada observa las **acciones reales** de sus vecinos
  (`ultima_accion` + `tick_ultima_accion`), no el flujo global.

### 3.5 El contrato motor ↔ frontend (WebSocket)

- Cliente manda: `{"tipo":"simular","titular":"...","seed":42,"ritmo":0.08}`
  (`ritmo:0` = sin pausas, lo usan los tests).
- Servidor responde: texto `inicio` (100 líderes con señal/confianza/
  frase/fuente) → **150 frames binarios** (10 de calma + 140 de
  reacción) → texto `fin` con el reporte.
- Frame binario little-endian: `f32 precio · u32 tick · i8×5000`
  (sentimiento por agente, -127..127).
- **El orden de agentes es el contrato**: orden de creación del motor
  (= orden de tipos en `config/agentes.json`, líderes al final) y debe
  coincidir con `web/src/swarm/datos.js` (mismos tipos, mismas
  cantidades, mismo orden). Si se cambia la mezcla, cambiar AMBOS lados.
- Sentimiento transmitido por agente de reglas =
  `senal_social + eco de última acción (±0.5 decayendo 5 ticks)`.

### 3.6 El frontend

- 3 draw calls: InstancedMesh de 4.900 reglas + 100 líderes + 100 halos.
- Orden de dibujo **barajado** para que el gobernador de fps (recorta
  bajo 45, restaura sobre 57, mínimo 1.200) quite una muestra pareja y
  no un tipo entero.
- Modo remoto (`enjambre.modoRemoto`): el motor dicta sentimiento y
  precio; los decaimientos locales se apagan.
- `VITE_WS_URL` (build-time) o `ws://localhost:8000/ws` en localhost;
  sin motor → demo local con el léxico JS espejo. HUD muestra el modo.
- `prefers-reduced-motion`: simulación offline de 25 s + un solo render
  + gráfico 2D del precio (una serie, dorado 2px, etiquetas en tinta).
- Paleta: tinta `#0b0e14` · dorado `#c9a227`/`#e3c565` · neutro
  `#57534a` · compra `#4fae7f` · venta `#c4472a` · marfil `#f4efe6`.

## 4. Cómo correr y verificar todo

```bash
# motor + tests (27, ~35 s)
cd engine && source .venv/bin/activate
python -m pytest validation/ -q
python simular.py 42          # métricas de hechos estilizados
python demo_titular.py "..."  # demo de consola

# servidor + web en local
uvicorn server:app --port 8000     # terminal 1
cd web && npm install && npm run dev  # terminal 2 → localhost:5173

# e2e con navegador (patrón usado en las verificaciones):
# npm run build && npx vite preview --port 4173 + Playwright con
# executablePath /opt/pw-browsers/chromium (flags swiftshader en headless)
```

Números de referencia sanos (si una recalibración los mueve mucho, sospechar):
curtosis 4-9 · AC|r| lag1 0.15-0.45 · AC retornos |media| < 0.1 ·
asimetría 1.2-3 · shock -0.9 → mínimo -7% a -18% con rebote parcial ·
volumen institucional ≈ 65-70% · sesión de 600 ticks ≈ 6-9 s.

## 5. Pendientes y siguientes pasos

1. **Deploy real** (Giorgio, ~10 min): Render (motor, blueprint
   `render.yaml`, pegar `ANTHROPIC_API_KEY`) + Vercel (web, root `web`,
   `VITE_WS_URL=wss://<motor>.onrender.com/ws`). Guía completa en
   `docs/despliegue.md`. Nadie ha probado aún los 100 cerebros con API
   real (sin clave en el entorno de desarrollo) — primer titular con
   clave: verificar latencia < 15 s y calidad de frases.
2. **Etapa 5 — demo vendible**: reporte exportable (PDF/imagen), pulido
   de los 3 escenarios, quizá comparador de escenarios.
3. **Ideas aprobadas para después** (conversadas con Giorgio):
   - Noticias en vivo: Alpaca News API (gratis, WebSocket, contenido
     Benzinga) para titulares globales; **canal de Telegram existente**
     de Giorgio como fuente de baja latencia (oyente Python → filtro →
     `aplicar_titular`).
   - **El portero**: clasificador barato (Haiku o léxico) que decide si
     un titular amerita simulación — protege el presupuesto de ~100-120
     llamadas por simulación.
4. Deuda técnica consciente (aceptada por simplicidad):
   - Órdenes límite en reposo no reservan efectivo (posible sobregiro
     leve; acotado por expiración de 4 ticks y topes de cordura).
   - El warmup del servidor (60 ticks) corre por conexión (~1-2 s);
     si algún día molesta, pre-calentar un pool de modelos.
   - `web/package.json` incluye Playwright como devDependency (se usa
     para verificación e2e; no viaja al build).

## 6. Convenciones de trabajo (resumen operativo)

Español en comentarios/commits/explicaciones; código en inglés… salvo que
este proyecto usa **nombres en español** en el motor (decisión temprana,
consistente en todo el código: `comprar_mercado`, `senal_social`, etc.) —
mantener la consistencia antes que la regla. Commits como puntos de
guardado por avance funcional. Nunca decir "listo" sin correr los tests.
Explicarle a Giorgio en simple, con analogías. Nada de lenguaje de
recomendación de inversión en ninguna parte del producto (CMF Chile).
