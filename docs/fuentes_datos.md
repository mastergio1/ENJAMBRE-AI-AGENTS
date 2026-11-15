# Fuentes de datos — veredicto de licencia (Fase 0)

*Rubicón Lab · El Enjambre · 2026-11-15*
*Chequeo de términos de uso y API de Polymarket y Kalshi para el plan de validación
contra mercados de predicción. Lectura de texto, NO asesoría legal.*

> **Veredicto rápido:** 🟡 **ÁMBAR, no verde.** Técnicamente ambos tienen API de
> lectura pública y gratuita para mercados resueltos e histórico de precios. Pero
> **legalmente hay un freno real en Polymarket** (una cláusula que restringe a
> "empresas de tecnología financiera" usar sus datos sin acuerdo escrito) y en
> **Kalshi no se pudo leer el documento legal clave** (Developer Agreement + ToS
> devolvieron error de tasa). Antes de construir el producto comercial, esto
> necesita revisión legal. Para la validación interna, hay un camino alternativo
> que reduce la dependencia (ver §4).

---

## 1. Polymarket

**Fuentes leídas:** docs.polymarket.com (varias páginas), polymarket.com/tos,
polymarket.com/legal. (polymarket.com/terms-of-use → 404.) ToS vigente 11-ago-2026.

| Pregunta | Veredicto | Detalle |
|---|---|---|
| ¿API de mercados resueltos + histórico? | ✅ Sí | Gamma API (`closed=true`), Data API `prices-history`. Lectura **sin API key**. Ojo: granularidad fina solo últimos 30 días; buckets de 3h/12h son permanentes (usar `interval=max`). |
| ¿Uso comercial de los datos? | 🔴 **Restringido** | ToS §5.1: licencia "personal, limited, non-commercial". §4.2: **prohíbe** usar los datos "directly or through an API ... in raw, derived, aggregated form" si eres "a non-retail, professional entity ... including **financial technology companies**" o "market data distributor", **salvo acuerdo escrito**. |
| ¿Almacenar/cachear? | 🟡 No claro | Sin cláusula explícita; §4.2 prohíbe scraping del "Site". Para dataset interno el riesgo principal es la cláusula de "entidad profesional/fintech". |
| ¿Redistribuir/mostrar precios? | 🔴 Restringido | §4.2 prohíbe "commercially exploit the Data to any Capital Market Client or market data distributor" sin acuerdo escrito. Mostrar un precio puntual en un newsletter: no claro. |
| Límites / costo | 🟡 No claro | Sin cifras para lectura pública; sin cargo documentado por lectura. |
| Geografía | 🟡 Trading bloqueado para EE.UU. (close-only); lectura de datos no claramente restringida. |

**El punto que más pesa:** la cláusula §4.2 nombra **explícitamente a las "financial
technology companies"**. El giro de Rubicón Lab incluye IA aplicada a análisis
financiero → **esa cláusula probablemente nos aplica, incluso para investigación
interna.** Para cualquier uso serio: pedir permiso escrito (builder@polymarket.com).

## 2. Kalshi

**Fuentes leídas:** docs.kalshi.com (varias). **No leídas (error 429):** kalshi.com/terms,
/regulatory, y el **Developer Agreement** (kalshi.com/developer-agreement) — que es
"probablemente donde están las reglas de datos". La doc dice: "By continuing to use
or access Kalshi's API, you are agreeing to be bound to our Developer Agreement."

| Pregunta | Veredicto | Detalle |
|---|---|---|
| ¿API de mercados resueltos + histórico? | ✅ Sí (técnicamente el más limpio) | `/historical/markets`, `/historical/markets/{ticker}/candlesticks`, `/historical/trades`, `/markets?status=settled`. Velas 1min/1h/1día. Lectura **sin auth**, **sin depósito**. |
| ¿Uso comercial? | 🟡 **No resuelto** | No se pudo leer el Developer Agreement/ToS. Sin cláusula que citar. |
| ¿Almacenar/cachear? | 🟡 No resuelto | Técnicamente posible; sin texto de licencia que lo permita. |
| ¿Redistribuir/mostrar precios? | 🟡 No resuelto | **El punto que más necesita leerse** antes del producto. |
| Límites / costo | ✅ Publicados | Tier Basic: ~200 tokens/s (~20 req/s), solo requiere registro. Sin tarifa mencionada. |
| Geografía | 🟡 No resuelto | Páginas regulatorias no leídas. (Kalshi es un exchange regulado por la CFTC en EE.UU.) |

**Kalshi es técnicamente más favorable** (API histórica limpia, candlesticks, sin
depósito), pero **su documento legal clave quedó sin leer** (429). Hay que reintentar
leer el Developer Agreement + terms + regulatory cuando se libere el límite.

## 3. Veredicto de la puerta

🟡 **ÁMBAR.** No se puede dar luz verde limpia:
- **Validación interna:** técnicamente viable en ambos; pero Polymarket §4.2 es un
  riesgo real para nosotros (fintech) y los términos de Kalshi están sin leer.
- **Producto "Enjambre vs Mercado" (republicar precios):** **requiere revisión legal
  y, en Polymarket, acuerdo escrito.** No avanzar a producto sin eso.

## 4. Camino alternativo honesto (reduce la dependencia de licencia)

Para la **validación** necesitamos tres cosas por pregunta: (a) la pregunta binaria,
(b) su **resolución**, (c) el **precio del mercado en T**. De esas:

- (a) y (b) son **hechos públicos** (¿subió la Fed? ¿el IPC superó X?) — se obtienen
  de fuentes oficiales **sin** ninguna de estas licencias.
- (c), el precio del mercado, es lo único realmente licenciado.

**Implicación:** podemos correr **casi toda la validación** (enjambre vs líneas base
triviales y vs la tasa base) usando **solo resoluciones públicas**, y usar
Polymarket/Kalshi **únicamente** para la comparación "¿le gana al precio del mercado?".
Eso deja el riesgo de licencia acotado a un solo paso, y nos permite avanzar el resto
mientras se resuelve el permiso.

## 5. Próximos pasos de licencia

1. Reintentar leer el **Developer Agreement + terms + regulatory de Kalshi** (cuando
   pase el 429) y buscar cláusulas de datos/redistribución/uso comercial.
2. Si vamos a producto con Polymarket: escribir a **builder@polymarket.com** por el
   permiso escrito que exige §4.2.
3. Confirmar con asesoría legal antes de **republicar** precios de cualquiera de los
   dos en El Pulso.

---

*Fin. Lectura de texto público, no asesoría legal. Páginas que fallaron:
polymarket.com/terms-of-use (404), kalshi.com/terms, /regulatory, /developer-agreement (429).*
