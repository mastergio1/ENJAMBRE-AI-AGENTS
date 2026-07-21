# FICHA TÉCNICA — El Enjambre

> Documento de referencia del producto: qué es, para qué sirve, casos de
> uso y arquitectura a nivel de código. Cifras verificadas contra el código
> fuente (no de memoria). Rubicón Lab · 15 de julio de 2026.

---

## 1. Qué es

**El Enjambre** es un simulador de comportamiento de masas del mercado
bursátil basado en agentes (*agent-based model*, ABM). El usuario ingresa
un titular real de mercado (ej. *"la Fed sube las tasas 50 puntos base"*) y
observa en una escena 3D en tiempo real cómo **5.000 inversionistas
simulados** reaccionan: el pánico se contagia, las manadas se forman, el
precio emerge del cruce de órdenes. Al final entrega un reporte: dirección
esperada, volatilidad, mínimo y desglose de reacciones por tipo de agente.

- **Posicionamiento:** "el focus group sintético del mercado". Herramienta
  de **simulación y educación**, NO de asesoría financiera (restricción
  regulatoria CMF Chile — sin lenguaje de recomendación de inversión).
- **Diferenciador:** la visualización 3D del enjambre en tiempo real y la
  interpretación de la noticia por 100 líderes de opinión con IA.
- **Alcance:** mercado bursátil mundial, con foco en la bolsa de EE.UU.

## 2. Para qué sirve — casos de uso (B2B)

| Cliente | Uso |
|---|---|
| **Fintech / neobrokers** | Widget embebible que muestra "cómo reaccionaría la masa" a la noticia del día — engagement educativo, no señal de trading. |
| **Educación financiera** | Herramienta de aula: sesgos conductuales (Kahneman-Tversky, FOMO, aversión a pérdida) hechos visibles. Escenarios a medida. |
| **Medios económicos** | El "¿y el mercado qué siente?" ilustrado; el duelo de dos escenarios como pieza de contenido; El Pulso como newsletter. |
| **Gestores de activos** | Focus group sintético: estresar una tesis narrativa contra la reacción probable de la masa retail vs. institucional. |

**Casos de uso técnicos del sistema:**
1. **Simulación on-demand:** un titular → reacción en vivo (WebSocket, ~25 s).
2. **Muro diario:** las 3 noticias destacadas del día, ya simuladas.
3. **Hemeroteca ("El Enjambre dijo"):** archivo navegable con URL por caso.
4. **Duelo:** dos escenarios enfrentados, exportable a Reel vertical 9:16.
5. **El Pulso:** newsletter diaria automática (ritual de madrugada).
6. **Calibración:** backtesting histórico + corrección contra mercado real.

## 3. La mezcla de agentes — 5.000 en total

**`total_agentes: 5000`** (`engine/config/agentes.json`). Principio de
diseño: la **cantidad** representa personas; el **capital relativo**
representa poder de mercado. Los institucionales son pocos pero con capital
~50-100×, de modo que generan ~65-70% del volumen; el retail domina en
número (~89%) pero pesa ~30-35% del volumen.

| # | Tipo | Cant. | Capital | En red social | Rol |
|---|------|------:|:---:|:---:|-----|
| 1 | Fundamentalista / value institucional | 200 | 50× | no | Ancla el precio al valor justo |
| 2 | Quant / momentum institucional | 120 | 40× | no | Sigue tendencias (SMA 5/20, stop -3%) |
| 3 | Fondo pasivo / index | 80 | 60× | no | Compra constante, insensible a noticias |
| 4 | Market maker | 5 | 100× | no | Liquidez; amplía spread ×3 en pánico |
| 5 | Ejecutor TWAP/VWAP | 15 | 30× | no | Ejecuta órdenes grandes en rebanadas |
| 6 | Arbitrajista | 30 | 20× | no | Corrige desviaciones > 2% |
| 7 | Noise trader retail | 2.000 | 1× | sí | Ruido browniano (p≈0.05/tick) |
| 8 | Manada / imitador | 900 | 1× | sí | Copia a su red (umbral 40-80%) |
| 9 | FOMO / momentum retail | 600 | 1× | sí | Persigue subidas, entra tarde |
| 10 | Miedoso / aversión a pérdida | 500 | 1× | sí | Vende rápido (asimetría 2.5:1) |
| 11 | Contrarian retail | 250 | 1.5× | sí | Va contra el consenso (>70%) |
| 12 | Buy & hold pasivo | 200 | 2× | no | Casi nunca opera |
| 13 | **Líder de opinión (LLM)** | **100** | 5× | sí | Lee la noticia; su señal se propaga |

**Reparto:** 4.900 agentes de reglas (tipos 1-12) + **100 líderes LLM**
(tipo 13) = **5.000**. Cada agente se instancia con sus parámetros base
± ruido gaussiano (σ = 15%) para que no haya dos idénticos.

En la **capa visual** el motor simula 5.000 agentes, pero el frontend puede
renderizar hasta **10 partículas por agente (50.000)** vía *instanced
rendering* (1 draw call) si el dispositivo lo permite; degrada elegante y
un gobernador de fps recorta partículas bajo 45 fps.

## 4. Los 100 líderes de opinión (LLM) — 8 arquetipos

Son los **únicos** agentes que leen la noticia real. Cada uno hace **una
llamada** a la API de Anthropic con su prompt de personalidad + el titular,
y responde solo con JSON: `{ "senal": 0.65, "confianza": 0.8, "frase": "…" }`
(señal ∈ [-1,+1], confianza ∈ [0,1], frase = una línea en su voz).

| Arquetipo | Cant. | Seguidores | Sesgo dominante |
|---|---:|:---:|---|
| A. Institucional Frío | 15 | 20-60 | Exceso de confianza en modelos |
| B. Quant Escéptico | 10 | 20-50 | Apuesta a la reversión de sobre-reacciones |
| C. FOMO Evangelista | 15 | 80-150 | Recencia extrema, hipérbole viral |
| D. Doomer | 15 | 40-100 | Sesgo de negatividad (todo es 2008) |
| E. Contrarian Sabio | 10 | 20-60 | Va contra la masa, puede ser temprano |
| F. Macro Trader | 10 | 30-80 | Sobre-interpreta señales de la Fed |
| G. Influencer Optimista | 15 | 80-150 | Optimismo estructural ("siempre sube") |
| H. Value Paciente | 10 | 20-50 | Anclaje a tesis; ignora el ruido |

**Implementación (`engine/brains/`):**
- Llamadas en **paralelo** (asyncio, `MAX_CONCURRENTES = 25`): las 100 se
  resuelven en < 15 s.
- Modelos: `claude-sonnet-5` (líderes) + `claude-haiku-4-5-20251001`
  (portero que clasifica las noticias del día).
- **Sin `temperature`** (Sonnet 5 lo rechaza con HTTP 400); la variabilidad
  viene del prompt y de la semilla por corrida.
- **Fallback léxico obligatorio:** si la API falla o el JSON no parsea, el
  líder usa una señal precomputada por arquetipo según el sentimiento del
  titular (diccionario bilingüe ES+EN). La simulación NUNCA se cae por la
  API. El campo `fuente` (api/cache/fallback) viaja con cada respuesta.
- Caché por (titular, arquetipo, semilla): repetir demos no cuesta.

## 5. La red de influencia (`engine/network/red.py`)

- Grafo dirigido **scale-free (Barabási–Albert):** pocos nodos muy
  conectados (líderes), muchos poco conectados (como una red social real).
- Cada líder tiene 20-150 seguidores según arquetipo; los retail (tipos
  8-10) tienen además 3-8 vecinos "pares" (el rumor viaja horizontal).
- **Propagación con retardo:** la señal de un líder llega a sus seguidores
  con delay de 1-4 ticks y atenuación 0.7 por salto. *Esto crea la "ola"
  visual — el efecto más importante del producto.*
- Los institucionales (tipos 1-3) NO están en la red: reaccionan a precio
  y fundamentales, no a rumores.

## 6. El motor de mercado (`engine/market/order_book.py`)

Microestructura tipo **Chiarella-Iori**: el precio **emerge** del libro de
órdenes, no se impone.
- Toda orden es **límite** con "urgencia" (`precio*(1±urgencia)`, urgencia
  exponencial `min(expovariate(125), 0.06)`); lo no cruzado reposa y
  **expira a los 4 ticks**.
- Precio de cierre = **última transacción** (VWAP y punto medio fallan).
- El precio de referencia de los agentes es el cierre del tick anterior.
- El **arbitrajista** (SMA-3, umbral 0.006) borra tendencias predecibles —
  es lo que hace pasar el test de no-autocorrelación de retornos.

**Ciclo de una simulación (`engine/server.py`):**
1. `TICKS_CALENTAMIENTO = 60` — el mercado halla su ritmo (no se transmite).
2. `TICKS_PREVIOS = 10` — calma visible antes de la noticia.
3. Se aplica el titular: los 100 líderes emiten señal → se propaga por la red.
4. `TICKS_POSTERIORES = 140` — la reacción completa.
5. Total transmitido: **150 frames** por WebSocket → reporte final.

## 7. Validación — hechos estilizados (`engine/validation/`)

La simulación es creíble solo si reproduce las "huellas digitales" de
mercados reales. Tests automáticos que deben pasar antes de cualquier demo:
1. **Colas gordas:** curtosis de retornos > 3 (sano: 4-9).
2. **Clustering de volatilidad:** autocorrelación de |retornos| positiva y
   decayendo lento (lag1 sano: 0.15-0.45).
3. **Sin autocorrelación de retornos:** el signo no predice el siguiente.
4. **Asimetría de pánico:** las caídas son más rápidas que las subidas
   (sano: 1.2-3).
5. **Respuesta a shock:** caída → sobre-reacción → rebote parcial.

Si un test falla, se ajustan proporciones/parámetros de §3, **nunca** se
hardcodea el resultado.

## 8. Arquitectura y stack

```
┌─ FRONTEND (Vercel) ──────────────┐        ┌─ MOTOR (Render) ──────────────┐
│ Vite · Three.js · Tailwind · GSAP│        │ Python 3.11 · Mesa 3 · FastAPI │
│ - enjambre 3D (instanced)        │◄──WS──►│ - MercadoEnjambre (ABM)        │
│ - muro, archivo, duelo, widget   │  bin   │ - order book (precio emergente)│
│ - reporte + TradingView          │ frames │ - 100 cerebros LLM (async)     │
└──────────────────────────────────┘        │ - red de influencia            │
                                             │ - SQLite (persistencia)        │
     ┌─ Anthropic API ─┐                     │ - portero, pipeline, corrector │
     │ sonnet-5 (líderes)│◄───────────────── │                                │
     │ haiku (portero)   │                   └────────────────────────────────┘
     └───────────────────┘                        │
                                        ┌─ Fuentes externas ─┐
                                        │ Alpaca (noticias+precios)│
                                        │ Stooq (histórico pre-2016)│
                                        │ Barchart · Resend · Telegram│
                                        └──────────────────────────┘
```

**Contrato motor ↔ frontend (WebSocket):**
- Cliente → `{"tipo":"simular","titular","seed"}`.
- Servidor → texto `inicio` (los 100 líderes con su frase) → **frames
  binarios** (`f32 precio · u32 tick · i8×5000 sentimientos`, tamaño de
  frame = **8 + 5000 = 5008 bytes**) → texto `fin` con reporte y `sim_id`.
- **El orden de agentes es el contrato:** orden de creación (= agentes.json,
  líderes al final), debe coincidir con `web/src/swarm/datos.js`.
- El replay reutiliza el mismo formato de frame (muro, archivo, duelo,
  widget). Modo **observatorio:** sesión continua que recibe noticias encima.

## 9. La capa de contenido (`engine/contenido/`)

- **Persistencia (SQLite, modo WAL):** TODA simulación se guarda; `id =
  sha256(titular|seed)[:16]`. Tablas: simulaciones, titulares, suscriptores,
  briefs, contactos (B2B). Columna `reaccion_real` para la calibración.
- **Portero (2 pisos):** filtro léxico + clasificador Haiku que elige las 3
  destacadas del día y define el universo de La Redacción.
- **Pipeline:** el ritual de la madrugada (recolectar → filtrar → simular →
  publicar → corrector → boletín), con humano en el lazo antes de enviar.
- **La Redacción:** análisis de mercado con 3 roles (reportero/verificador/
  editor); el número manda (viene de datos, no de un texto); filtro CMF.
- **Límites:** topes on-demand por IP/hora y global/día (la muralla de la
  billetera LLM: cada simulación ≈ 100 llamadas API).

## 10. La calibración (backtest + corrector)

El enjambre no predice precios; se **calibra** contra la realidad.
- **Corrector** (`corrector.py`): 1-2 días después de cada destacada mide el
  movimiento real del símbolo (Alpaca, base = cierre previo a la noticia,
  ventana 2 ruedas) y lo guarda; redacta el epílogo educativo.
- **Backtest** (`backtest.py` + 55 eventos 2001-2025): pasa al enjambre
  exámenes históricos por **tandas pequeñas** (freno de presupuesto, máx 10
  por corrida) y compara con el precio real de esa fecha (Alpaca → Stooq
  para lo pre-2016). No repite lo ya rendido (consulta la caja fuerte).
- **Libreta** (`GET /api/libreta`): % de aciertos de dirección, magnitudes
  medias, separando EN VIVO vs HISTÓRICO, y excluyendo lo simulado sin IA.
- **Caja fuerte:** cada caso se respalda como JSON en la rama
  `respaldo-datos` de GitHub (inmune a los borrones del disco de Render).

## 11. Seguridad

Rate-limit por IP real (último salto de X-Forwarded-For) · XSS neutralizado
con `esc()` antes de todo `innerHTML` + CSP · `sim_id` validado
`^[0-9a-f]{16}$` · SQL 100% parametrizado · path traversal con doble
muralla · `hmac.compare_digest` para el token admin · contenedor Docker
no-root (uid 10001) · dependencias con versión fija · filtro CMF con tests
sobre todo texto publicable.

## 12. Números clave (referencia rápida)

| Parámetro | Valor | Dónde |
|---|---|---|
| Agentes totales | **5.000** | `agentes.json: total_agentes` |
| — de reglas (12 tipos) | 4.900 | tipos 1-12 |
| — líderes LLM | 100 | tipo 13 (8 arquetipos) |
| Partículas visuales máx. | 50.000 | 10 por agente (instanced) |
| Ruido por agente (σ) | 15% | `ruido_parametros_sigma` |
| Ticks de calentamiento | 60 | `TICKS_CALENTAMIENTO` |
| Ticks previos + posteriores | 10 + 140 | frames transmitidos: 150 |
| Tamaño de frame | 5.008 bytes | 8 + 5000 (i8/agente) |
| Llamadas LLM por simulación | ~100 | 1 por líder (paralelo, máx 25) |
| Presupuesto LLM objetivo | ≤ 100-120/sim | CLAUDE.md §2 |
| Objetivo de rendimiento | 60 fps móvil | recorta bajo 45 fps |
| Tests automatizados | 138 | `engine/validation/` |

## 13. Cómo correr (desarrollo)

```bash
# Motor (Python)
cd engine && python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest validation/ -q          # 138 tests (~5 min)
python simular.py 42                       # métricas de hechos estilizados
uvicorn server:app --port 8000             # levanta el motor + WebSocket

# Frontend (Node)
cd web && npm install && npm run dev       # → localhost:5173
npm run build && npx vite preview          # build de producción
```

**Variables de entorno del motor:** `ANTHROPIC_API_KEY` (cerebros),
`ALPACA_API_KEY_ID/SECRET` (noticias + precios), `ENJAMBRE_PIPELINE_TOKEN`
(admin), `GITHUB_RESPALDO_TOKEN` (caja fuerte), `RESEND_API_KEY` (Pulso),
`BARCHART_API_KEY` (La Redacción), `ENJAMBRE_MAX_SIM_DIA/IP_HORA` (topes).

## 14. Repositorio y despliegue

- **Código:** https://github.com/mastergio1/ENJAMBRE-AI-AGENTS
- **Web:** https://enjambre-ai-agents.vercel.app (Vercel, auto-deploy `main`)
- **Motor:** https://enjambre-motor.onrender.com (Render, Docker blueprint)
- **Documentación:** `CLAUDE.md` (biblia del simulador), `CONTENIDO.md`
  (capa de contenido), `docs/contexto.md` (estado y traspaso), `docs/`
  (despliegue, seguridad, auditoría, La Redacción, esta ficha).

---
*Rubicón Lab · El Enjambre · ficha-tecnica.md · 15 de julio de 2026*
