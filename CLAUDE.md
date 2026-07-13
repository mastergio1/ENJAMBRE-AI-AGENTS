# CLAUDE.md — Proyecto "El Enjambre"

> **Lee este archivo completo antes de escribir cualquier línea de código.**
> Es la biblia del proyecto. Si una decisión técnica contradice algo escrito aquí, pregunta antes de proceder.

---

## 1. VISIÓN

**El Enjambre** es un simulador de escenarios del mercado bursátil: el usuario ingresa una noticia (ej. *"la Fed sube las tasas 50 puntos base"*) y observa en una escena 3D cómo 5.000 inversionistas simulados reaccionan — el pánico se contagia, las manadas se forman, el precio emerge. Al final recibe un reporte: dirección esperada, volatilidad y desglose de reacciones por tipo de inversionista.

- **Posicionamiento:** "el focus group sintético del mercado". Herramienta de simulación y educación. **NUNCA asesoría financiera** (restricción regulatoria CMF Chile — no usar lenguaje de recomendación de inversión en ninguna parte del producto).
- **Cliente:** B2B — fintechs, educación financiera, medios económicos, gestores de activos.
- **Diferenciador:** la visualización 3D del enjambre en tiempo real. Nadie más la tiene.
- **Dueño del proyecto:** Giorgio (Rubicón Lab). No es programador: es director. Explícale siempre qué hiciste en lenguaje simple, sin jerga, con analogías.

## 2. REGLAS DE TRABAJO (no negociables)

1. **Una sesión, una misión.** No avances a otra etapa sin instrucción explícita.
2. **Verifica todo.** Después de cada implementación: ejecuta, muestra el resultado, explica en simple. Nunca digas "listo" sin evidencia.
3. **Commits como puntos de guardado.** Después de cada avance funcional, commit con mensaje descriptivo en español.
4. **Español primero.** Comentarios de código, mensajes de commit y explicaciones en español. Nombres de variables/funciones en inglés (convención estándar).
5. **Simplicidad ante todo.** Prefiere la solución simple que funciona hoy sobre la arquitectura perfecta de mañana. Nada de microservicios, nada de sobre-ingeniería.
6. **Performance 3D:** reutilizar geometrías y materiales (nunca crear objetos dentro de loops), vectores mutables con refs (`vec.lerp`, no `new Vector3` por frame), `pixelRatio` limitado a `Math.min(devicePixelRatio, 2)`. Objetivo: 60fps en móvil de gama media.
7. **Presupuesto LLM:** máximo ~100-120 llamadas API por simulación. Si un diseño requiere más, rediseña.

## 3. ARQUITECTURA

```
enjambre/
├── CLAUDE.md              ← este archivo
├── engine/                ← motor de simulación (Python 3.11+, Mesa)
│   ├── config/
│   │   └── agentes.json   ← la mezcla de agentes (sección 4)
│   ├── market/            ← libro de órdenes, formación de precio
│   ├── agents/            ← clases de agentes por tipo
│   ├── brains/            ← líderes de opinión LLM (sección 5)
│   ├── network/           ← red de influencia (sección 6)
│   ├── validation/        ← tests de hechos estilizados (sección 7)
│   └── server.py          ← FastAPI + WebSocket → frontend
├── web/                   ← frontend (Vite + Three.js + GSAP)
│   ├── src/swarm/         ← enjambre de partículas (instanced)
│   ├── src/ui/            ← input de noticia, panel de resultados
│   └── src/report/        ← reporte exportable
└── docs/
```

**Flujo de una simulación:**
1. Usuario escribe titular → 2. Los 100 líderes LLM lo interpretan (paralelo, 1 llamada c/u) → 3. Cada líder emite señal ∈ [-1, +1] con justificación de una frase → 4. La señal se propaga por la red de influencia a los 4.900 agentes de reglas → 5. El motor corre N ticks; los agentes ponen órdenes; el precio emerge del libro de órdenes → 6. Cada tick se transmite por WebSocket al frontend → 7. Three.js anima el enjambre → 8. Al terminar, se genera el reporte.

**Stack fijo:** Python + Mesa + FastAPI (motor) · API de Anthropic, modelo `claude-sonnet-5` (cerebros) + `claude-haiku-4-5` (portero) · Vite + Three.js + GSAP + Tailwind (frontend) · GitHub (`mastergio1`) + Vercel (deploy frontend).

## 4. LA MEZCLA — 5.000 AGENTES

**Principio de diseño:** la *cantidad* de agentes representa personas; el *capital* representa poder de mercado. Los institucionales son pocos pero con capital ~50x, de modo que generen ~65-70% del volumen (calibrar). El retail domina en número (89%) pero pesa ~30-35% del volumen.

| # | Tipo | Cant. | Capital rel. | Rol |
|---|------|------:|:---:|-----|
| 1 | Fundamentalista / value institucional | 200 | 50x | Ancla el precio al valor "justo" |
| 2 | Quant / momentum institucional | 120 | 40x | Sigue tendencias con disciplina |
| 3 | Fondo pasivo / index | 80 | 60x | Compra constante, insensible a noticias |
| 4 | Market maker | 5 | 100x | Liquidez: cotiza compra y venta siempre |
| 5 | Ejecutor TWAP/VWAP | 15 | 30x | Ejecuta órdenes grandes en rebanadas |
| 6 | Arbitrajista | 30 | 20x | Corrige ineficiencias rápido |
| 7 | Noise trader retail | 2.000 | 1x | Ruido browniano de fondo |
| 8 | Manada / imitador | 900 | 1x | Copia lo que hace su red |
| 9 | FOMO / momentum retail | 600 | 1x | Persigue subidas, entra tarde |
| 10 | Miedoso / aversión a pérdida | 500 | 1x | Vende rápido ante caídas |
| 11 | Contrarian retail | 250 | 1.5x | Va contra la corriente |
| 12 | Buy & hold pasivo | 200 | 2x | Casi nunca opera |
| 13 | **Líder de opinión (LLM)** | **100** | 5x | Lee la noticia; su señal se propaga |

### Parámetros de comportamiento por tipo (agentes de reglas)

Cada agente se instancia con estos parámetros base ± ruido gaussiano (σ = 15% del valor) para que no haya dos idénticos:

**1. Fundamentalista/value (200):** Estima valor fundamental V con ruido idiosincrático. Compra si precio < 0.95·V, vende si > 1.05·V. Sensibilidad a noticias: solo vía actualización de V (lenta, ponderada 0.3). Paciencia alta: opera cada 10-20 ticks. *Es el freno del sistema: sin ellos el precio se va a la luna o al subsuelo.*

**2. Quant/momentum institucional (120):** Señal = media móvil corta vs. larga (ventanas 5/20 ticks). Entra con tendencia confirmada, sale con stop-loss disciplinado (-3%). Ignora la noticia directamente; reacciona al precio que la noticia provoca. Sin emociones: ejecución mecánica.

**3. Fondo pasivo (80):** Compra un monto fijo pequeño cada K ticks pase lo que pase. Sensibilidad a noticias: 0. *Representa el flujo 401k/AFP que estabiliza.*

**4. Market maker (5):** Cotiza bid/ask alrededor del último precio con spread proporcional a la volatilidad reciente. Si su inventario se desequilibra, sesga las cotizaciones para volver a neutral. En pánico extremo (volatilidad > umbral) amplía el spread ×3 — *esto reproduce la evaporación de liquidez de los crashes reales.*

**5. Ejecutor TWAP/VWAP (15):** Recibe una orden grande al inicio (aleatoria: comprar o vender X) y la ejecuta en rebanadas iguales durante toda la sesión. Presión de fondo direccional.

**6. Arbitrajista (30):** Si el precio se desvía > 2% de una referencia de corto plazo sin volumen que lo justifique, opera en contra. Rápido: cada tick. Capital medio.

**7. Noise trader (2.000):** Cada tick, con probabilidad p≈0.05, compra o vende al azar (50/50) un monto pequeño. Sensibilidad a noticias: solo el 20% de ellos desplaza su probabilidad ±10% según el sentimiento global. *Son la textura del mercado; sin ellos no hay hechos estilizados.*

**8. Manada/imitador (900):** Observa a sus vecinos de red (incluye 1-2 líderes de opinión). Si > 60% de su red compró en los últimos 3 ticks, compra; ídem venta. Umbral de activación con distribución variada (40%-80%) — *crucial: umbrales heterogéneos crean cascadas graduales tipo ola, no saltos binarios.*

**9. FOMO/momentum retail (600):** Se activa cuando el precio sube > 2% en 5 ticks Y su red social habla de ello (≥ 2 vecinos compraron). Compra tarde, con monto agresivo (hasta 40% de su capital). Vende en pánico si cae > 4% desde su entrada. *Sesgo de recencia extremo: solo mira los últimos 5 ticks.*

**10. Miedoso/aversión a pérdida (500):** Asimetría 2.5:1 (el dolor de perder pesa 2.5× el placer de ganar — coeficiente de Kahneman-Tversky). Ante sentimiento negativo > umbral, vende el 50-100% de su posición inmediatamente. Recompra lento y tarde (necesita 10+ ticks de calma). *Motor del sobreajuste a la baja.*

**11. Contrarian retail (250):** Mide el sentimiento agregado de los últimos 5 ticks. Si el 70%+ del mercado vendió, compra ("sangre en las calles"); si hay euforia compradora, vende. Capital algo mayor (sobrevivieron a varios ciclos). Paciente: opera cada 5-10 ticks.

**12. Buy & hold (200):** Solo opera si el precio cae > 15% (compra "la oportunidad de la década") o ante necesidad aleatoria de liquidez (p≈0.001/tick). El resto del tiempo: nada. *Representa el capital dormido.*

## 5. LOS 100 LÍDERES DE OPINIÓN (LLM) — ANÁLISIS DE PERSONALIDADES

Son los únicos agentes que leen la noticia real. Cada uno hace **una llamada** a la API con su prompt de personalidad + el titular, y responde SOLO con JSON:

```json
{ "senal": 0.65, "confianza": 0.8, "frase": "Tasas más altas castigan growth; roto a defensivas." }
```

`senal` ∈ [-1, +1] (venta total → compra fuerte) · `confianza` ∈ [0, 1] (modula cuánto arrastra a sus seguidores) · `frase` = una línea en su voz (se muestra en la UI al hacer hover sobre el líder — momento mágico del demo).

### Los 8 arquetipos

**A. El Institucional Frío — 15 líderes · seguidores: pocos pero de capital alto**
*Perfil:* CIO de fondo, 25 años de experiencia. Analiza impacto en flujos de caja y tasas de descuento. Desconfía de las narrativas; confía en los números.
*Sesgo dominante:* exceso de confianza en modelos; lento para reconocer cambios de régimen.
*Reacción típica:* señales moderadas (rara vez |señal| > 0.5), confianza alta. Ante noticia ambigua: señal ≈ 0, frase escéptica.
*Prompt base:* "Eres un director de inversiones institucional con décadas de experiencia. Evalúas noticias por su impacto en fundamentales: flujos de caja, tasas de descuento, márgenes. Ignoras el ruido mediático. Eres medido: casi nunca tomas posiciones extremas."

**B. El Quant Escéptico — 10 líderes · seguidores: momentum institucional**
*Perfil:* PhD en física convertido a finanzas. Cree que las noticias ya están en el precio. Busca sobre-reacciones para apostar a la reversión.
*Sesgo dominante:* desprecio por el análisis cualitativo; punto ciego ante cambios estructurales genuinos.
*Reacción típica:* señal CONTRARIA a la intuición popular cuando percibe sobre-reacción. Confianza media.
*Prompt base:* "Eres un quant escéptico. Tu tesis: el mercado sobre-reacciona a titulares y luego revierte. Evalúa si esta noticia genuinamente cambia fundamentales o es ruido que la masa exagerará. Si es ruido, tu señal apuesta a la reversión."

**C. El FOMO Evangelista — 15 líderes · seguidores: FOMO retail y manada**
*Perfil:* Influencer financiero de 28 años, 500k seguidores. Todo es "la oportunidad de la década" o "el colapso inminente". Vive de la emoción.
*Sesgo dominante:* recencia extrema + narrativa sobre datos + necesidad de contenido viral.
*Reacción típica:* señales extremas (|señal| > 0.7 casi siempre), confianza altísima, frases con hipérbole.
*Prompt base:* "Eres un influencer financiero viral. Amplificas todo: las buenas noticias son EL momento de entrar, las malas son EL colapso. Tus señales son extremas y tu confianza total. Tu frase debe sonar a tweet viral."

**D. El Doomer — 15 líderes · seguidores: miedosos**
*Perfil:* Analista que predijo 2008 (y otras 14 crisis que no ocurrieron). Toda noticia esconde un riesgo sistémico. Colecciona oro y desconfianza.
*Sesgo dominante:* sesgo de negatividad + aversión a pérdida proyectada + memoria selectiva de crisis.
*Reacción típica:* señal negativa incluso ante noticias neutras (rango típico [-1, 0.1]). Ante noticias malas: -0.9 con confianza alta.
*Prompt base:* "Eres un analista permanentemente bajista que vivió el 2008. En toda noticia buscas el riesgo oculto, el contagio posible, la fragilidad sistémica. Las buenas noticias te parecen trampas alcistas. Tu señal rara vez supera +0.1."

**E. El Contrarian Sabio — 10 líderes · seguidores: contrarians**
*Perfil:* Veterano estilo Buffett/Marks. "Sé codicioso cuando otros temen." Piensa en años, no en días.
*Sesgo dominante:* puede ser temprano por años (que en trading equivale a estar equivocado).
*Reacción típica:* pregunta interna: "¿qué hará la masa con esto?" y va al revés, con paciencia. Señales moderadas-fuertes solo en extremos de sentimiento.
*Prompt base:* "Eres un inversionista contrarian veterano. Ante cada noticia estimas primero la reacción emocional de la masa, y luego evalúas si esa reacción creará una oportunidad en sentido opuesto. El pánico ajeno es tu compra; la euforia ajena, tu venta."

**F. El Macro Trader — 10 líderes · seguidores: mixtos (quant + manada)**
*Perfil:* Ex-banco central, ahora hedge fund global. Lee todo en clave de tasas, dólar, geopolítica y liquidez. Para él, las acciones son un derivado de la macro.
*Sesgo dominante:* sobre-interpreta señales de política monetaria; ve a la Fed en todas partes.
*Reacción típica:* MUY sensible a noticias de bancos centrales, inflación, empleo (|señal| alta); casi indiferente a noticias corporativas individuales (señal ≈ 0).
*Prompt base:* "Eres un macro trader global. Traduces toda noticia a: ¿qué implica para tasas, dólar y liquidez global? Noticias de bancos centrales e inflación te mueven fuerte; noticias de empresas individuales apenas te importan."

**G. El Influencer Retail Optimista — 15 líderes · seguidores: manada y noise**
*Perfil:* Creador de contenido "finanzas personales positivas". Todo es aprendizaje, largo plazo, "el mercado siempre sube". Nunca vende, solo "acumula".
*Sesgo dominante:* optimismo estructural + supervivencia (empezó en un bull market y nunca vivió uno bajista de verdad).
*Reacción típica:* señal ∈ [0, +0.6] casi siempre. Ante crashes: "oportunidad de comprar barato" (+0.4).
*Prompt base:* "Eres un creador de contenido de finanzas personales optimista. Tu filosofía: el mercado siempre sube en el largo plazo, las caídas son descuentos. Tu señal casi nunca es negativa; en el peor caso, es neutral con un mensaje de calma."

**H. El Value Paciente — 10 líderes · seguidores: buy & hold y fundamentalistas**
*Perfil:* Gestor boutique, cartera concentrada, rotación mínima. Las noticias diarias le parecen teatro; solo actúa si algo cambia el valor intrínseco de un negocio.
*Sesgo dominante:* anclaje a sus tesis de inversión; puede ignorar deterioro real por años.
*Reacción típica:* señal ≈ 0 en el 80% de las noticias (con frases desdeñosas sobre el cortoplacismo). Señal fuerte solo ante cambios estructurales (regulación, disrupción, quiebras).
*Prompt base:* "Eres un gestor value de cartera concentrada. El 80% de las noticias te parecen ruido irrelevante y tu señal es 0 con una frase desdeñosa sobre el cortoplacismo. Solo reaccionas ante noticias que cambian el valor intrínseco de largo plazo de los negocios."

### Reglas de implementación de los cerebros

- Llamadas en **paralelo** (asyncio) — las 100 deben resolverse en < 15 segundos.
- `temperature` ≈ 0.8 para variabilidad intra-arquetipo (dos Doomers no responden idéntico).
- **Fallback obligatorio:** si la API falla o el JSON no parsea, el líder usa una señal precomputada por arquetipo según el sentimiento léxico del titular (diccionario simple). La simulación NUNCA se cae por la API.
- Cachear respuestas por (titular, arquetipo, seed) para repetir demos sin costo.
- Validar el JSON con schema; recortar señal a [-1, +1].

## 6. RED DE INFLUENCIA

- Grafo dirigido tipo **scale-free (Barabási–Albert)**: pocos nodos muy conectados (los líderes), muchos poco conectados. Así se ven las redes sociales reales.
- Cada líder de opinión tiene entre 20 y 150 seguidores según arquetipo (los FOMO Evangelistas y los Influencers Optimistas son los más seguidos).
- Los agentes retail (tipos 8-10) tienen además 3-8 vecinos "pares" entre sí (el rumor también viaja horizontalmente).
- **Propagación con retardo:** la señal de un líder llega a sus seguidores con delay de 1-4 ticks (distribuido) y atenuación 0.7 por salto. *Esto crea la ola visual — el efecto más importante del producto. Sin retardo no hay ola, solo un salto feo.*
- Los institucionales (tipos 1-3) NO están en la red social: reaccionan a precio y fundamentales, no a rumores.

## 7. VALIDACIÓN — CRITERIOS DE REALISMO

La simulación es creíble solo si reproduce los **hechos estilizados** de mercados reales. Tests automáticos en `engine/validation/` que deben pasar antes de cualquier demo:

1. **Colas gordas:** curtosis de retornos > 3 (los extremos ocurren más que en una campana de Gauss).
2. **Clustering de volatilidad:** autocorrelación de |retornos| positiva y decayendo lento (la turbulencia viene en rachas).
3. **Sin autocorrelación de retornos:** el signo del retorno no predice el siguiente (no free lunch).
4. **Asimetría de pánico:** las caídas son más rápidas y violentas que las subidas.
5. **Respuesta a shock:** ante una noticia fuertemente negativa, el precio debe: caer → sobre-reaccionar → rebotar parcialmente (patrón documentado de sobre-reacción).

Si un test falla, ajustar proporciones/parámetros de la sección 4, **no** hardcodear el resultado.

## 8. EL FRONTEND — REGLAS DE ORO

- Estética Rubicón Lab: editorial, elegante, fondo tinta profunda, dorado como acento. Tipografías: Cormorant Garamond (display) + Jost (UI).
- **Instanced rendering** para las partículas (1 draw call). El motor simula 5.000 agentes; la capa visual puede renderizar 10 partículas por agente (50.000) si el dispositivo lo permite — detectar capacidad y degradar elegante.
- Mapeo visual: **color** = sentimiento (verde compra → rojo venta, con la paleta editorial, no colores puros saturados) · **posición/movimiento** = decisión y cluster de tipo · **tamaño** = capital.
- Los 100 líderes se renderizan distintos (más grandes, con halo). Hover sobre un líder muestra su `frase`. *Este es el momento mágico del demo.*
- 60fps en móvil gama media. Si baja de 45fps, reducir partículas automáticamente.
- Accesibilidad: respetar `prefers-reduced-motion` (modo estático con gráfico 2D).

## 9. ROADMAP (referencia rápida)

| Etapa | Qué | Hecho cuando |
|---|---|---|
| 0 | Setup repo + entornos | Claude Code trabaja dentro del repo |
| 1 | Motor + mezcla de agentes | Tests de hechos estilizados pasan |
| 2 | Cerebros LLM + red de influencia | Un titular real cambia el comportamiento del enjambre |
| 3 | Enjambre 3D (datos falsos) | Hipnótico y 60fps en móvil |
| 4 | Integración total + deploy | Un link público funciona end-to-end |
| 5 | Demo vendible | 3 escenarios precargados + reporte exportable |

**Estado actual: Etapas 0-4 + 6-10 completadas (la capa de contenido está completa)** — el motor transmite la simulación real por WebSocket y el enjambre 3D la renderiza en vivo; toda simulación queda en SQLite; el portero de dos pisos elige los titulares del día (Alpaca con degradación a demo); el filtro CMF es código con tests; y **el muro es la nueva portada**: las 3 destacadas del día ya simuladas con replay 3D, simulación on-demand con frenos de presupuesto (5/hora/IP + tope global diario), y degradación elegante si el motor duerme; **El Pulso** es la newsletter diaria (ritual de madrugada completo, correo por Resend, imagen del momento dramático, suscripción double opt-in, cron que dispara un endpoint protegido). La web está blindada (rate-limit, XSS, path traversal, DoS). **El archivo** ("El Enjambre dijo") es la hemeroteca: destacadas navegables por mes, buscables por titular y ticker, cada una con URL propia, sus 8 voces por arquetipo y el campo "¿y qué pasó después?". **La Redacción** añade al Pulso un análisis de mercado global investigado (reportero/verificador/editor): "lo que pasó" con hechos verificados y cita, "qué observa hoy" como atención (nunca predicción), datos de Barchart con degradación a demo, y brief con visto bueno humano — todo bajo el filtro CMF (docs/la-redaccion.md). **El duelo** enfrenta dos escenarios (dos enjambres sincronizados + curvas superpuestas + export a Reel vertical, URL /duelo/A-vs-B) y **el widget** es un iframe embebible del enjambre del día (build separado, firma + disclaimer CMF, lista blanca de dominios). Deploy documentado en docs/despliegue.md; falta ejecutarlo con las cuentas de Giorgio (Alpaca, Barchart, Resend). La capa de contenido (etapas 6-10) está completa; la Etapa 5 (reporte exportable) quedó recogida dentro de ella.

## 10. GLOSARIO PARA GIORGIO

Cuando expliques avances, usa estas equivalencias: agente = inversionista simulado · tick = un "latido" del mercado (una ronda de decisiones) · libro de órdenes = la lista donde se cruzan compras y ventas · señal = la opinión de un líder convertida en número · hechos estilizados = las huellas digitales de un mercado real · instanced rendering = truco para dibujar miles de partículas como si fueran una.

---
*Rubicón Lab · El Enjambre · CLAUDE.md v1 · Julio 2026*
