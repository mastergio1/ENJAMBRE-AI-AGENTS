# El Enjambre — Contexto profundo (código y todo)

> Documento de referencia técnica de El Enjambre al día de agosto de 2026.
> Descripción fiel de cómo funciona, dónde está cada cosa en el código y qué
> queda. Complementa: `arquitectura-y-producto.md`, `ficha-tecnica.md`,
> `el-pulso.md`, la biblia `CLAUDE.md`.

---

## 1. Qué es

El Enjambre es un **simulador de escenarios de mercado**: le sueltas un titular
(ej. *"la Fed sube las tasas 50 puntos base"*) y **10.000 inversionistas
simulados** reaccionan en una escena 3D — el pánico se contagia, las manadas se
forman, el precio emerge del cruce de órdenes. Al final se genera un reporte:
dirección esperada, volatilidad y desglose de reacciones por tipo de agente.

- **Motor:** Python 3.11 + **Mesa** (agent-based modeling) + FastAPI + WebSocket.
- **Frontend:** Vite + **Three.js** (instanced rendering) + GSAP + Tailwind.
- **IA:** Anthropic — `claude-sonnet-5` (los cerebros de los líderes),
  `claude-haiku-4-5` (el portero de El Pulso).
- **Restricción #1:** herramienta educativa/simulación. **Nunca** asesoría de
  inversión (marco CMF Chile).

---

## 2. El flujo de una simulación

```
titular
  │
  ▼
1000 líderes LLM lo leen  (comparten ~110 "cerebros" → ~110 llamadas API)
  │  cada líder emite señal ∈ [-1,+1] + confianza + una frase
  ▼
la señal se propaga por la RED DE INFLUENCIA a los 9000 agentes de reglas
  │  con retardo de 1-4 ticks y atenuación 0.7 por salto  → la "ola"
  ▼
el MODELO corre N ticks: cada agente decide y pone órdenes límite
  │
  ▼
el LIBRO DE ÓRDENES cruza oferta/demanda → el precio EMERGE (VWAP del tick)
  │
  ▼
cada tick se transmite por WebSocket (frame binario) al frontend
  │
  ▼
Three.js anima el enjambre 3D  →  al terminar, se genera el REPORTE
```

**Horizonte de una simulación** (`server.py`):
- `TICKS_CALENTAMIENTO = 60` — el mercado encuentra su ritmo (no se transmite).
- `TICKS_PREVIOS = 10` — calma visible antes de la noticia.
- Se aplica el titular.
- `TICKS_POSTERIORES = 140` — la reacción completa (caída → sobre-reacción → rebote).

---

## 3. Arquitectura del motor (dónde está cada cosa)

```
engine/
├── model.py                 # MercadoEnjambre(mesa.Model): el modelo central
├── market/
│   └── order_book.py        # el libro de órdenes (órdenes límite, VWAP)
├── agents/
│   ├── base.py              # AgenteBase: efectivo + acciones, colocar_orden…
│   ├── reglas.py            # los 12 tipos de agentes de reglas
│   └── lider.py             # LiderOpinion (tipo 13): lee la noticia, propaga
├── brains/
│   ├── arquetipos.py        # los 8 arquetipos de líder (perfiles + prompts)
│   ├── cerebro.py           # la llamada real a Anthropic (async)
│   ├── reparto.py           # 1000 líderes ↔ ~110 cerebros (presupuesto)
│   ├── fallback.py          # respaldo léxico si la API falla
│   └── mercado.py           # clasifica el TIPO de mercado del titular
├── network/
│   └── red.py               # la red de influencia scale-free
├── config/
│   └── agentes.json         # la mezcla de 10.000 agentes (la fuente de verdad)
├── server.py                # FastAPI + WebSocket /ws + endpoints
└── llm_texto.py             # extrae texto de las respuestas (salta 'thinking')
```

---

## 4. El libro de órdenes (`market/order_book.py`)

Todas las órdenes son **órdenes límite**. Un agente con urgencia "cruza" el libro
poniendo un precio agresivo (paga más / recibe menos); lo que no encuentra
contraparte queda reposando y **da liquidez**. Las órdenes viejas expiran.

- **El precio del tick es el VWAP** — el promedio ponderado de donde realmente se
  operó. Así el precio **emerge** del cruce, sin mecanismos artificiales.
- `LibroOrdenes`: `orden_limite()`, `mejor_compra()`, `mejor_venta()`,
  `vwap_tick()`, `reiniciar_tick()`, `cancelar_ordenes()`, `_ejecutar()`.
- `OrdenLimite` (dataclass): agente_id, lado, precio, cantidad, tick.
- Cada ejecución notifica al agente (`aplicar_ejecucion`) y al modelo (para la
  visual de compra/venta).

---

## 5. Los agentes

### 5.1 La base (`agents/base.py`)

`AgenteBase(mesa.Agent)`: arranca **50% efectivo / 50% acciones**. Métodos:
`colocar_orden(lado, precio_limite, cantidad)`, `comprar_mercado`,
`vender_mercado`, `aplicar_ejecucion`, `ruido(valor, σ=0.15)`. Cada agente
recuerda su `ultima_accion` y `tick_ultima_accion` (los vecinos lo miran) y su
lugar en la red: `pares` (vecinos horizontales) y `lideres_seguidos`.

### 5.2 La mezcla de 10.000 (`config/agentes.json`)

`total_agentes: 10000`, ruido gaussiano σ=0.15 sobre los parámetros base (no hay
dos iguales). **El orden importa**: los tipos 1-12 primero, los 1000 líderes al
final — el frame binario del WebSocket manda un sentimiento por agente en ESE
orden, y el frontend mapea por índice.

| # | Tipo (clase en `agents/reglas.py`) | Cant. | Capital rel. | Rol |
|---|---|--:|:--:|---|
| 1 | `Fundamentalista` | 370 | 50x | Ancla el precio al valor justo (el freno) |
| 2 | `QuantMomentum` | 220 | 40x | Sigue tendencias (media móvil 5/20), stop-loss |
| 3 | `FondoPasivo` | 150 | 60x | Compra fija cada K ticks, insensible |
| 4 | `MarketMaker` | 9 | 100x | Cotiza bid/ask; en pánico amplía el spread ×3 |
| 5 | `EjecutorTWAP` | 28 | 30x | Ejecuta una orden grande en rebanadas |
| 6 | `Arbitrajista` | 55 | 20x | Corrige desvíos > 2% cada tick |
| 7 | `NoiseTrader` | 3.670 | 1x | Ruido browniano de fondo |
| 8 | `Manada` | 1.650 | 1x | Copia a su red (umbral 40-80%, cascadas) |
| 9 | `FomoRetail` | 1.100 | 1x | Persigue subidas, entra tarde, vende en pánico |
| 10 | `Miedoso` | 920 | 1x | Aversión a pérdida 2.5:1, vende rápido |
| 11 | `Contrarian` | 460 | 1.5x | Va contra la corriente en extremos |
| 12 | `BuyAndHold` | 368 | 2x | Casi nunca opera (capital dormido) |
| 13 | `LiderOpinion` | 1.000 | 5x | Lee la noticia; su señal se propaga |

*(Principio: la cantidad = personas; el capital = poder de mercado. Los
institucionales son pocos pero pesan; el retail domina en número.)*

### 5.3 El líder de opinión (`agents/lider.py`)

`LiderOpinion`: guarda `senal ∈ [-1,+1]`, `confianza ∈ [0,1]`, `arquetipo` y su
`frase`. Es el único que "lee" la noticia real (vía el LLM). En su `step()` opera
según su señal; su señal se propaga a sus seguidores por la red.

---

## 6. Los cerebros (LLM) — `brains/`

### 6.1 Los 8 arquetipos (`brains/arquetipos.py`)

Cada líder pertenece a uno de 8 arquetipos, cada uno con su **prompt de
personalidad** y su sesgo (ver CLAUDE.md §5):
**A** Institucional Frío · **B** Quant Escéptico · **C** FOMO Evangelista ·
**D** Doomer · **E** Contrarian Sabio · **F** Macro Trader ·
**G** Influencer Retail Optimista · **H** Value Paciente.
`POR_ID` mapea id → {nombre, perfil}.

Cada cerebro responde SOLO con JSON:
`{"senal": 0.65, "confianza": 0.8, "frase": "…"}`.

### 6.2 El reparto (`brains/reparto.py`) — el truco del presupuesto

1.000 líderes con una llamada cada uno romperían el presupuesto (~100-120
llamadas/simulación) 10×. Solución: **los 1.000 líderes comparten ~110 cerebros**
(uno por arquetipo × varios). Cada cerebro es UNA llamada al LLM; los líderes de
un mismo arquetipo la comparten **en ronda**. Así hay ~110 frases distintas
(variedad de sobra para el hover) al costo de siempre (~$0,12/simulación).
`planificar(lideres, …)` reparte; `expandir(respuestas, asignacion)` las
distribuye a los 1.000.

### 6.3 La llamada real (`brains/cerebro.py`)

`analizar_titular(titular, consultas)`: llama a Anthropic **en paralelo**
(asyncio, `AsyncAnthropic`), modelo `claude-sonnet-5`. **NO envía `temperature`**
(Sonnet-5 la rechaza con HTTP 400 y todos caerían al respaldo en silencio — ver
`contexto.md`). La variabilidad viene del muestreo del modelo + la semilla por
corrida. Valida el JSON, recorta la señal a [-1,+1].

### 6.4 El respaldo léxico (`brains/fallback.py`)

Si la API falla o no hay clave, cada líder usa una **señal precomputada por
arquetipo** según el sentimiento léxico del titular (diccionario simple). **La
simulación NUNCA se cae por la API.**

### 6.5 El tipo de mercado (`brains/mercado.py`)

`clasificar(titular)` + `perfil_de(...)`: el enjambre razona el TIPO de mercado
(macro, corporativo, etc.) y aplica su personalidad al tono del titular.

---

## 7. La red de influencia (`network/red.py`)

Grafo dirigido **scale-free** (attachment preferencial): pocos nodos muy
conectados (los líderes), muchos poco conectados — como las redes sociales reales.

- Cada líder tiene **20-150 seguidores** según arquetipo (los FOMO Evangelistas y
  los Influencers Optimistas son los más seguidos).
- Los agentes retail (manada, FOMO, miedoso) tienen además **3-8 vecinos "pares"**
  — el rumor viaja horizontal.
- Los **institucionales NO están en la red**: reaccionan a precio y fundamentales,
  no a rumores.
- **Propagación con retardo:** la señal de un líder llega a sus seguidores con
  delay de **1-4 ticks** y **atenuación 0.7** por salto. *Esto crea la ola visual
  — el efecto más importante del producto.*
- `construir_red(model)`, `_muestra_preferencial(...)`, `_eleccion_preferencial(...)`.

---

## 8. El modelo (`model.py`)

`MercadoEnjambre(mesa.Model)`:
- `__init__`: carga la mezcla desde `config/agentes.json`, crea los agentes
  (`_crear_agentes`), teje la red.
- `aplicar_titular(titular, respuestas, perfil)`: convierte el titular en un tono,
  aplica el perfil del mercado, siembra las señales en los líderes.
- `_propagar_desde_lideres()` + `_entregar_senales()`: la propagación con retardo.
- `step()`: un tick — reinicia el libro, cada agente decide y opera, el precio
  emerge, se registran retornos/flujo.
- `correr(ticks)`, `retorno_acumulado(n)`, `volatilidad_reciente(n)`,
  `fraccion_compras(n)`.
- Expone `historial_precios`, `retornos`, `agentes_ordenados` (el orden canónico).

---

## 9. El servidor y el protocolo WebSocket (`server.py`)

### 9.1 El canal `/ws`

`@app.websocket("/ws")` → `canal(ws)`. Recibe mensajes JSON del navegador:
- `tipo: "simular"` — una simulación de un titular (la clásica).
- `tipo: "observatorio"` — sesión continua donde el enjambre sigue vivo y el
  usuario suelta noticias encima (`MAX_TICKS_OBS = 6000` ≈ 8 min).
- La "puerta" (`_puerta_simulacion`): en pruebas privadas abre una clave; en
  público, un correo válido abre y de paso suscribe gratis.
- Frenos: semáforo de simulaciones simultáneas + los límites de `limites.py`
  (freemium: 1/día gratis, 40/mes Premium — ver `el-pulso.md` §6).

### 9.2 El frame binario del tick (`_paquete_tick`)

Cada tick se manda como **bytes** (no JSON, por velocidad):
```
cabecera:  struct "<fI"  → float precio (4 bytes) + uint32 tick (4 bytes)
cuerpo:    1 byte por agente, en el orden canónico (tipos 1-12, luego líderes)
           valor = int(sentimiento * 127)   → sentimiento ∈ [-1,+1]
```
El sentimiento visible de un agente de reglas = rumor recibido + eco de su última
acción (compra/venta) que decae en ~5 ticks. El de un líder = su `senal`.

### 9.3 El reporte final (`_generar_reporte`)

Al terminar: dirección (retorno acumulado), volatilidad, y frases
representativas (el más bajista, el mediano, el más alcista de los líderes). Más
el tipo de mercado detectado. Es lo que se guarda y se muestra en el panel/muro.

---

## 10. La validación — hechos estilizados (`validation/hechos_estilizados.py`)

La simulación es creíble solo si reproduce las "huellas digitales" de un mercado
real. Tests que deben pasar (`test_hechos_estilizados.py`):
1. **Colas gordas** — curtosis de retornos > 3.
2. **Clustering de volatilidad** — autocorrelación de |retornos| positiva, decae lento.
3. **Sin autocorrelación de retornos** — el signo no predice el siguiente.
4. **Asimetría de pánico** — las caídas son más rápidas que las subidas.
5. **Respuesta a shock** — ante una noticia muy negativa: caer → sobre-reaccionar → rebotar.

Si un test falla, se ajustan proporciones/parámetros de la mezcla, **no** se
hardcodea el resultado.

---

## 11. El frontend 3D (`web/src/`)

```
web/src/
├── main.js                  # arranque: escena Three.js, loop, monta la UI
├── swarm/
│   ├── enjambre.js          # el enjambre 3D: instanced rendering, 3 draw calls
│   ├── datos.js             # la mezcla de 10.000 (espejo de agentes.json)
│   └── escenario.js         # analizador léxico (para el modo demo sin motor)
├── muro/ muro.js            # EL MURO: la portada (3 destacadas del día + on-demand)
├── archivo/ archivo.js      # la hemeroteca ("El Enjambre dijo")
├── duelo/ duelo.js          # el duelo: dos escenarios enfrentados
├── widget/ widget.js        # el widget embebible (iframe para medios)
├── report/                  # el reporte exportable
└── ui/
    ├── conexion.js          # el WebSocket con el motor (+ token Premium, cid)
    ├── premium.js           # el chip del enlace mágico (desbloqueo 40/mes)
    ├── correo.js            # la puerta de correo
    ├── panel.js             # el panel/reporte + gráfico estático
    ├── navegacion.js, guia.js, tour.js
```

- **Instanced rendering:** el enjambre se dibuja en **3 draw calls** (partículas +
  líderes + halos). Geometrías y materiales se crean **una vez**; nada de objetos
  nuevos dentro del loop (regla de rendimiento de CLAUDE.md §6).
- **Mapeo visual:** color = sentimiento (verde compra → rojo venta, paleta
  editorial) · posición/movimiento = decisión y cluster · tamaño = capital. Los
  1.000 líderes se dibujan más grandes, con halo; el hover muestra su `frase`
  (el momento mágico del demo).
- **Rendimiento:** objetivo 60fps en móvil de gama media; si baja de 45 reduce
  partículas; respeta `prefers-reduced-motion` (modo estático 2D).
- **En vivo vs. demo:** con motor, el frame binario del WebSocket trae el
  sentimiento real por agente; sin motor, `escenario.js` (un espejo léxico
  simplificado de `fallback.py`) genera un escenario falso en el navegador.

### 11.1 El muro (la portada)

`muro/muro.js` es la nueva portada: las **3 destacadas del día** ya simuladas con
replay 3D, la **simulación on-demand** (escribe tu titular) con los frenos del
freemium, y degradación elegante si el motor duerme (Render free tarda ~50 s en
despertar; la UI dice "despertando el motor…" en vez de caer al demo).

---

## 12. Persistencia (`contenido/persistencia.py`)

- **Toda simulación se guarda** en SQLite (regla desde el primer commit de la capa
  de contenido). Tabla `simulaciones`: titular, seed, reporte, líderes (voces),
  serie de precios, ref a los frames, `destacada`.
- Las **destacadas** conservan sus **frames binarios** en disco (`frames/{id}.bin`)
  para el replay 3D del muro y del archivo.
- Reproducibilidad: el id de una simulación es `sha256(titular|seed)`; las seeds
  del día son fijas → el mismo titular da el mismo replay.

---

## 13. Dónde vive (despliegue)

- **Motor:** Render (`enjambre-motor`, Docker, FastAPI/uvicorn). WebSocket `/ws`.
  Se despliega solo desde `main`. Plan free → duerme con la inactividad.
- **Frontend:** Vercel (proyecto `enjambre-ai-agents` → `enjambre-ai-agents.vercel.app`).
  Build Vite. CSP estricta en `vercel.json`.
- **Datos:** SQLite en el disco persistente de Render (`ENJAMBRE_DB`).
- Variables clave: `ANTHROPIC_API_KEY` (cerebros), `ENJAMBRE_ORIGENES` (CORS),
  `ENJAMBRE_MAX_SIM_DIA`/`ENJAMBRE_SIM_DIA_GRATIS`/`ENJAMBRE_SIM_MES_PREMIUM`
  (límites), `ENJAMBRE_ACCESO` (clave de pruebas privadas).

---

## 14. Módulos de contenido que se apoyan en el Enjambre

- `contenido/pipeline.py` — corre simulaciones fuera del WebSocket para el ritual
  diario de El Pulso (las 3 destacadas).
- `contenido/captura.py` — captura el "momento dramático" (PNG) de una simulación.
- `contenido/corrector.py` — el corrector automático: compara la reacción del
  enjambre con el movimiento real del símbolo (calibración).
- `contenido/backtest.py` — pruebas de calibración sobre históricos.
- `contenido/duelo` (en server) — dos enjambres sincronizados enfrentados.

---

## 15. Estado y qué queda (ago-2026)

**Hecho y en vivo (Etapas 0-10 de CLAUDE.md):**
- Motor completo: mezcla de 10.000, libro de órdenes, red de influencia, cerebros
  LLM con reparto y respaldo, validación de hechos estilizados.
- WebSocket en vivo → enjambre 3D renderizando la simulación real.
- El muro (portada), el archivo (hemeroteca), el duelo, el widget embebible.
- Integración con El Pulso: destacadas del día, freemium (1/día gratis, 40/mes
  Premium con enlace mágico).

**Lo que queda / pendientes conocidos:**
- El docstring de `model.py` dice "5.000 agentes" (histórico); la mezcla real es
  **10.000** (`agentes.json`) — comentario desactualizado, no afecta al código.
- Afinar continuamente la calibración vía el corrector (que los hechos estilizados
  y la reacción del enjambre se acerquen al mercado real).
- El reporte exportable (Etapa 5) quedó recogido dentro de la capa de contenido.
- Rendimiento en móvil de gama baja: seguir vigilando el degradado automático.
- (Ligado a El Pulso) reservar cupo del top-3 diario para el mayor movimiento
  verificado; botón de "regenerar edición" en el panel.

---
*Rubicón Lab · El Enjambre · Contexto profundo (código) · agosto 2026*
