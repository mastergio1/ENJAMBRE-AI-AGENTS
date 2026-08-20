# El Pulso — Contexto profundo del producto

> Documento maestro de El Pulso, al día de agosto de 2026. Reúne qué es, cómo se
> arma cada edición, cómo se cobra y cómo vive en producción. Escrito para
> Giorgio (explicaciones en simple) con los detalles técnicos por si se los pasas
> a un desarrollador. Complementa: `contenido.md`, `la-redaccion.md`,
> `edicion-fin-de-semana.md`, `premium.md`, `despliegue.md`.

---

## 1. Qué es El Pulso

**El Pulso es el diario de mercado de Rubicón Lab.** Cada mañana temprano llega a
tu correo un resumen del mercado contado en simple: qué pasó, por qué, y qué
observa El Enjambre (nuestra herramienta de 10.000 inversionistas simulados con
IA que reaccionan a las noticias del día).

- **Posicionamiento:** informar y educar sobre el mercado, con contexto y voz —
  nunca dar consejos. Es un diario, no un asesor.
- **Restricción #1 (CMF Chile):** **jamás** lenguaje de recomendación de
  inversión. No se dice qué comprar ni vender. Hay un filtro en código que lo
  hace cumplir (sección 10).
- **Marca hermana:** El Enjambre (el simulador 3D). El Pulso trae la gente por la
  puerta del diario; El Enjambre es el gancho visual y la herramienta.
- **Modelo de negocio:** gratis para todos, con una capa **Premium** de pago
  (USD 6,99/mes) que abre el análisis a fondo del domingo y más simulaciones.

---

## 2. La arquitectura en una imagen

```
                 ┌─────────────────────────── El Pulso ───────────────────────────┐
  Fuentes        │  RECOLECCIÓN        SELECCIÓN      SIMULACIÓN      REDACCIÓN     │   Salida
  ───────        │  ───────────        ─────────      ──────────      ─────────     │   ──────
  Alpaca (news) ─┼─► titulares  ┐                                                   │
  Yahoo (movers)─┼─► + reportero├─► el portero ─► el enjambre  ─► La Redacción ─► el │─► correo de
  Búsqueda web ──┼─►   IA        │   (impacto)    (3 destacadas)   + redactor IA    │   revisión
                 │                                                    boletín HTML   │      │
                 └───────────────────────────────────────────────────────────────  ┘      ▼
                                                                              Giorgio aprueba
                                                                                     │
                                                                                     ▼
                                                                          suscriptores (Resend)
```

**Dónde vive cada cosa:**

| Pieza | Plataforma | Qué hace |
|---|---|---|
| **Motor** | Render (`enjambre-motor`, FastAPI, Docker) | Arma las ediciones, simula el enjambre, maneja suscriptores/Premium/límites. Se despliega solo desde `main`. |
| **Landing + Enjambre** | Vercel | La landing (`www.diarioelpulso.com`) y El Enjambre (`enjambre-ai-agents.vercel.app`) — dos proyectos separados. |
| **Dominio** | Cloudflare (registrador + DNS) | `www.diarioelpulso.com` (y el raíz redirige a www). |
| **Correo** | Resend | Envía El Pulso, el correo de revisión y los de confirmación. |
| **Pagos** | Polar (Merchant of Record) | Cobra el Premium (sirve para Chile, a diferencia de Stripe). |
| **Datos IA** | Anthropic (`claude-sonnet-5`, `claude-haiku-4-5`) | Los cerebros del enjambre, el portero, el redactor y el reportero. |
| **Base de datos** | SQLite en el disco de Render | Simulaciones, titulares, suscriptores, gasto. |
| **Cron** | GitHub Actions | Dispara el ritual diario a las 10:00 UTC. |

---

## 3. El ritual de la madrugada

Un cron de **GitHub Actions** (`.github/workflows/ritual-diario.yml`) dispara el
motor todos los días a las **10:00 UTC ≈ 6:00 AM Chile** (6:00 en invierno, 7:00
en verano). El workflow solo *llama* al motor (`POST /api/pipeline`); el ritual
corre **en segundo plano dentro del motor** y tarda ~3-4 minutos.

Secuencia (ver `contenido/pipeline.py` → `ritual_matutino`):

1. **Recolección + selección + simulación** (entre semana) → las 3 destacadas.
2. **La Redacción** arma el brief del día (lo que pasó / qué observa).
3. **El redactor IA** le pone voz.
4. **El boletín** arma el HTML.
5. Se **guarda como 'pendiente'** y se le manda a Giorgio el **correo de
   revisión** ("📋 Revisar El Pulso"), ~6:40 AM.
6. **Giorgio aprueba** (desde el correo o el panel) → *ahí* sale a los
   suscriptores. Nada se envía sin su visto bueno (humano en el lazo).

> El fin de semana el ritual cambia de marcha (sección 5) y no simula el enjambre
> (lectura pausada, un solo llamado LLM).

---

## 4. Cómo se arma una edición diaria (el corazón)

### 4.1 Recolección — de dónde salen las historias

Dos fuentes, combinadas (`pipeline.py` → `preparar_dia`):

1. **Alpaca (titulares de prensa):** `fuentes/alpaca.py` — las noticias del día
   (con degradación a demo si no hay clave).
2. **Los movimientos reales del día + el reportero IA** *(nuevo, ago-2026)*:
   - `fuentes/yahoo.py` → `movers_del_dia`: los mayores gainers/losers del día
     (screener de Yahoo). Es **lo que de verdad movió al mercado**, no solo lo
     que un feed tituló. *(Esto arregla el caso "se perdió Moderna +177%".)*
   - `contenido/investigador.py` (el **reportero IA**): con **búsqueda web real**
     (`claude-sonnet-5` + herramienta `web_search`), investiga y **verifica** por
     qué se movió cada acción y arma un titular con el porqué comprobado. Si no lo
     puede verificar, **no inventa** (marco CMF); degrada al dato duro sin causa.
     Acota costo/tiempo: los 6 mayores, en paralelo.

Los movers investigados entran al pool **al frente**, junto a los titulares de
Alpaca.

### 4.2 Selección — el portero

`contenido/portero.py` → `procesar_dia`: evalúa cada candidato y le pone un
**impacto 1-10** (con `claude-haiku-4-5`, o un heurístico léxico sin clave).
Descarta duplicados y ruido, y elige los **3 de mayor impacto**. Todo veredicto
queda registrado en la tabla `titulares` (el log del portero, visible en el muro).

### 4.3 Simulación — el enjambre

Cada una de las 3 destacadas se simula con el motor del Enjambre (Mesa/ABM):
10.000 agentes reaccionan, 1.000 líderes de opinión LLM leen el titular
(comparten ~110 "cerebros" por presupuesto), el precio emerge del libro de
órdenes. Se guardan **con frames** para el replay 3D del muro. Presupuesto:
~$0,12 por simulación.

### 4.4 Redacción — La Redacción + el redactor IA

- **La Redacción** (`contenido/redaccion.py`): un flujo reportero/verificador/
  editor que arma el **brief**: "lo que pasó" (movimientos verificados con fuente,
  vía Barchart/Yahoo con degradación a demo) + "la foto del día" (índices,
  petróleo, oro) + "qué observa el enjambre hoy" (atención, **nunca** predicción).
  Detalle en `la-redaccion.md`.
- **El redactor IA** (`contenido/redaccion_ia.py`): le pone **voz** al brief con
  el prompt maestro (`prompt-maestro-pulso.md`), usando `claude-sonnet-5`. Si
  falla, el correo usa su plantilla (degradación elegante).

### 4.5 El boletín — el HTML

`contenido/boletin.py` arma el correo (tablas + estilos inline, 600px, paleta
clara editorial). Todos los textos variables pasan por el **filtro CMF** antes de
salir, y se **escapan** (los titulares vienen de fuentes externas).

---

## 5. Las tres marchas de la semana

| Día | Edición | Qué trae | Se cobra |
|---|---|---|---|
| **Lun-Vie** | **Diaria** | Las 3 historias del día (movers investigados + noticias) con el enjambre + gráficos reales. | Gratis |
| **Sábado** | **Resumen de la semana** | Los grandes temas con punto de vista (qué pasó, por qué, qué observar). Nunca predicción. | Gratis |
| **Domingo** | **Deep-dive (Premium)** | Una empresa de mediana capitalización a fondo: qué hace, sus números (ingresos, márgenes, EBITDA, deuda), el gráfico real y el **debate de los 8 perfiles IA**. | **Premium** |

- Código: `contenido/resumen_semanal.py` (sábado), `analisis_semanal.py` (domingo),
  y los bloques en `boletin.py`. Detalle en `edicion-fin-de-semana.md`.
- El **domingo se parte en dos** en el envío (sección 6.2).

---

## 6. Premium — la capa de pago

*(Referencia completa del cobro en `premium.md`.)*

### 6.1 El circuito

`www.diarioelpulso.com` → botón "Hazte Premium" → **checkout de Polar**
(`buy.polar.sh/…`, USD 6,99/mes, 5 días de prueba) → Polar avisa por webhook →
el motor **prende la llave Premium solo** → recibe el domingo completo + más
enjambre.

### 6.2 El correo del domingo, partido

Un mismo envío se divide (`boletin.py` + `pipeline.py` → `teaser_para`):
- **Premium** → el análisis **completo**.
- **Gratis** → un **teaser** con el gancho y el botón de pago; revela el sector
  pero **nunca** el nombre, los números ni el debate.

### 6.3 El cobro con Polar (webhook)

`contenido/pagos.py` verifica la firma **Standard Webhooks** de Polar y traduce el
evento a la llave: activa con `subscription.created/active/updated/…`; en
`canceled` deja vencer el mes pagado; en `revoked` corta ya. Endpoint:
`POST /pulso/webhook/polar` (fuera de `/api/` para no toparse con el rate-limit).
Falla cerrado sin `POLAR_WEBHOOK_SECRET`.

### 6.4 El freemium de El Enjambre

`contenido/limites.py`:
- **Gratis:** 1 simulación al día, contada por **dispositivo** (huella del
  navegador) — así una oficina o el 4G (CGNAT) no comparten un solo cupo.
- **Premium:** 40 simulaciones al **mes**, en **disco** (sobrevive a reinicios).
- **Muralla global:** `ENJAMBRE_MAX_SIM_DIA=30` — el tope de gasto, sobre todos.

**Economía:** 40 × $0,12 = $4,80 máx/mes por Premium contra $6,99 que paga →
siempre queda margen.

### 6.5 El desbloqueo con enlace mágico *(seguro)*

Para subir a 40/mes, el Premium **no escribe su correo desnudo** (se podía
suplantar y filtraba quién paga). En su lugar:
1. Escribe su correo → el motor le manda un **enlace** al buzón
   (`POST /api/pulso/desbloqueo`, respuesta **siempre neutra**).
2. Hace clic → el navegador guarda un **token firmado**
   (`GET /api/pulso/enjambre/verificar`).
3. Cada simulación manda el token; solo desbloquea quien tiene acceso real al
   buzón — el que pagó. (`token_enjambre` en la base; `web/src/ui/premium.js`.)

---

## 7. La landing (`www.diarioelpulso.com`)

`web/pulso/` — página autónoma (HTML + CSS inline), desplegada en Vercel:
- **Hero** con enjambre animado, **qué llega al correo**, el giro del fin de
  semana, la **tarjeta de planes** (Gratis vs Premium), y un **formulario de alta
  gratis** conectado a `POST /api/suscribir` (doble opt-in).
- Botón **"Hazte Premium"** → checkout de Polar. Página **/gracias** tras pagar.
- Franja de cross-promo a **El Enjambre**.
- Su dominio debe estar en `ENJAMBRE_ORIGENES` (CORS) del motor — ya lo está.

---

## 8. Suscriptores (double opt-in)

Tabla `suscriptores` (`contenido/persistencia.py`). Estados:
- **Pendiente:** `activo=0` con `token_confirma` — se dio de alta, falta confirmar.
- **Activo:** `activo=1` — confirmó; recibe El Pulso.
- **Baja:** `activo=0` sin token — se desuscribió (un clic).
- **Premium:** `premium=1` (+ `premium_hasta`) — de pago. Un pagador se da de alta
  **directo** (`alta_directa`, sin doble opt-in: ya consintió al pagar).

Flujo: `POST /api/suscribir` → correo de confirmación → `GET /api/confirmar/{token}`
→ activo. Baja: `GET /api/baja/{token}`. Antibombardeo: no se reenvía la
confirmación a la misma dirección más seguido que 10 min.

---

## 9. El centro de mando (panel)

`GET /panel` (protegido por `ENJAMBRE_PIPELINE_TOKEN`) — el tablero de Giorgio:
- La **edición del día** como máquina de estados: `pendiente → aprobada → enviada`
  (o `descartada`). Nada sale sin pasar a 'enviada'.
- **Aprobar / descartar / reenviar** a todos.
- **Editar** el texto (regenera el preview WYSIWYG).
- **Estadísticas:** suscriptores (total/activos/pendientes, curva de crecimiento,
  orígenes), ediciones (enviadas/descartadas) y correo (aperturas/clics por
  edición, vía el webhook de Resend firmado con Svix).

También llega el correo de **revisión** al propio buzón de Giorgio → funciona
desde el celular sin abrir el panel.

---

## 10. El marco CMF (la restricción legal)

`contenido/vocabulario.py` es el filtro en código:
- `PROHIBIDAS`: lista de términos de recomendación ("recomendamos", "deberías
  comprar", "recomendación de compra/venta", etc.).
- `es_publicable(texto)` / `verificar_pieza(texto)`: nada sale si contiene esos
  términos o si falta el disclaimer.
- `DISCLAIMER`: el aviso oficial ("no constituye asesoría ni recomendación").

**Todo texto variable** (titulares, voces del enjambre, brief, reportero) pasa por
este filtro antes de mostrarse o enviarse. El reportero IA, además, tiene la
instrucción de **no dar consejo y no inventar**. En El Enjambre, el aviso legal
(`.beta-badge`) tiene prioridad visual: ningún elemento comercial lo tapa.

---

## 11. Variables de entorno (en Render) — solo nombres

**Cobro/Premium:** `POLAR_WEBHOOK_SECRET`.
**Límites:** `ENJAMBRE_MAX_SIM_DIA` (30), `ENJAMBRE_SIM_DIA_GRATIS` (1),
`ENJAMBRE_SIM_MES_PREMIUM` (40).
**Web/correo:** `ENJAMBRE_ORIGENES` (CORS, incluye www.diarioelpulso.com),
`RESEND_API_KEY`, `PULSO_ADMIN_EMAIL`, `PULSO_REMITENTE`.
**IA:** `ANTHROPIC_API_KEY`.
**Datos:** `ALPACA_API_KEY_ID`/`ALPACA_API_SECRET` (titulares),
`BARCHART_API_KEY` (cotizaciones; degrada a Yahoo/demo).
**Operación:** `ENJAMBRE_PIPELINE_TOKEN` (protege el ritual y el panel),
`RESEND_WEBHOOK_SECRET` (aperturas/clics), `ENJAMBRE_WEB_URL`, `ENJAMBRE_API_URL`,
`ENJAMBRE_DB`.

---

## 12. Operaciones (cómo hacer cosas a mano)

- **Regenerar la edición de hoy:** GitHub → Actions → "El ritual del día" → "Run
  workflow". *Ojo:* es idempotente — si ya hay 3 destacadas del día, no la rehace.
  Para forzar una nueva hay que limpiar las destacadas del día (pendiente: un
  botón de "regenerar" en el panel).
- **Dar Premium a mano:** lo más simple es un **código de 100% descuento** en
  Polar; la persona "paga" $0 y el webhook le prende el Premium por el circuito
  normal. (No hay aún un botón de admin que lo prenda directo en la base.)
- **Probar el pago sin gastar:** código de 100% en Polar → "Hazte Premium" → ver
  /gracias → el chip del enjambre desbloquea 40/mes.
- **Ver quién abrió/clicó:** el panel de estadísticas (requiere el webhook de
  Resend configurado).

---

## 13. Archivos clave

```
engine/
├── server.py                       # FastAPI: WebSocket del enjambre + endpoints del Pulso
├── llm_texto.py                    # extrae el texto de las respuestas de Claude (salta 'thinking')
└── contenido/
    ├── pipeline.py                 # el ritual: recolecta→elige→simula→redacta→revisa→envía
    ├── portero.py                  # selección por impacto (1-10)
    ├── investigador.py             # ⭐ el reportero IA: movers + búsqueda web + verificación
    ├── redaccion.py                # La Redacción: el brief (lo que pasó / qué observa)
    ├── redaccion_ia.py             # el redactor: le pone voz (diaria, sábado, domingo)
    ├── resumen_semanal.py          # el sábado
    ├── analisis_semanal.py         # el domingo (deep-dive Premium)
    ├── boletin.py                  # el HTML del correo (+ teaser Premium, correo de revisión)
    ├── pagos.py                    # ⭐ Polar: verifica el webhook y prende/apaga Premium
    ├── limites.py                  # ⭐ freemium: 1/día gratis, 40/mes Premium, muralla global
    ├── persistencia.py             # SQLite: simulaciones, titulares, suscriptores, gasto
    ├── vocabulario.py              # el filtro CMF
    └── fuentes/
        ├── alpaca.py               # titulares de prensa
        ├── yahoo.py                # ⭐ movers del día + cotizaciones + fundamentales + gráficos
        └── barchart.py             # cotizaciones (con degradación)
web/
├── pulso/                          # la landing (index.html, gracias.html, vercel.json)
└── src/ui/premium.js               # ⭐ el chip del enlace mágico en El Enjambre
docs/                               # esta carpeta (contexto, arquitectura, premium, etc.)
```

*(⭐ = agregado o rehecho en agosto de 2026.)*

---

## 14. Estado y pendientes (ago-2026)

**En vivo y funcionando:**
- El Pulso diario + fin de semana, con tu aprobación.
- El reportero IA cazando los movimientos reales del día (Moderna +177% cazada en
  la prueba en vivo).
- Premium completo: cobro con Polar, correo partido, freemium 1/40, enlace mágico.
- Landing en `www.diarioelpulso.com`.

**Pendientes anotados (no bloqueantes):**
- Confirmar en producción que la búsqueda web del reportero investiga bien
  (primera salida real: la próxima edición automática).
- Un botón de "regenerar edición" en el panel (hoy el ritual es idempotente).
- Un botón de admin para dar Premium sin pasar por un código de descuento.
- Reservar un cupo del top-3 diario para el mayor movimiento verificado.
- Marketing: llevar tráfico a `www.diarioelpulso.com`.

---
*Rubicón Lab · El Pulso · Contexto profundo · agosto 2026*
