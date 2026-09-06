# El Pulso Premium — Mapa del sistema de cobro

> Documento de referencia (agosto 2026). Cómo funciona la suscripción Premium
> de El Pulso de punta a punta: el cobro, la activación, el contenido y los
> límites del enjambre. Escrito para Giorgio (no-técnico) — con los detalles
> técnicos por si algún día se los pasas a un desarrollador.

---

## 1. El circuito en una frase

Alguien entra a **www.diarioelpulso.com** → se suscribe gratis **o** paga Premium en **Polar** → Polar le avisa al motor → el motor **prende su llave Premium solo** → recibe el análisis del domingo completo y desbloquea **40 simulaciones/mes** en El Enjambre.

```
Landing (Vercel)  →  Pago en Polar  →  Webhook al motor (Render)  →  Llave Premium encendida
www.diarioelpulso.com    buy.polar.sh       /pulso/webhook/polar         (base de datos SQLite)
```

---

## 2. Las piezas y dónde viven

| Pieza | Dónde | Qué hace |
|---|---|---|
| **Landing** | Vercel · proyecto `diario-el-pulso` · carpeta `web/pulso/` | La cara pública: presenta El Pulso, alta gratis y botón "Hazte Premium". |
| **Dominio** | Cloudflare (registrador + DNS) | `www.diarioelpulso.com` (y `diarioelpulso.com` redirige a `www`). |
| **Motor** | Render · servicio `enjambre-motor` (FastAPI) | Recibe el pago (webhook), maneja los suscriptores y los límites. |
| **Pagos** | Polar · organización `diarioelpulso` | Cobra la suscripción (Merchant of Record; sirve para Chile). |
| **Correo** | Resend (dominio del remitente) | Envía El Pulso y el correo de revisión. |
| **Base de datos** | SQLite en el disco de Render | Suscriptores, estado Premium, uso mensual. |

---

## 3. El producto en Polar

- **Nombre:** El Pulso Premium
- **Precio:** USD 6,99 / mes (suscripción recurrente)
- **Prueba gratis:** 5 días
- **Enlace de pago (checkout):**
  `https://buy.polar.sh/polar_cl_hy8qjPfruFrefdpCyLWJB043I99rOwHIcqE270kLphF`
  (es público; vive en el botón "Hazte Premium" de la landing, variable `CHECKOUT_URL` en `web/pulso/index.html`)
- **Panel de Polar:** https://polar.sh/dashboard/diarioelpulso

### El webhook (el "aviso automático")

- **A dónde apunta:** `https://enjambre-motor.onrender.com/pulso/webhook/polar`
- **Eventos:** `subscription.created`, `.active`, `.updated`, `.canceled`, `.revoked`
- **Seguridad:** firma **Standard Webhooks** (HMAC). El motor la verifica con el
  secreto antes de creer nada. Sin secreto configurado, **no activa nada** (falla cerrado).

---

## 4. Cómo se prende y se apaga el Premium (automático)

Todo lo hace `engine/contenido/pagos.py` cuando llega el webhook:

- **Paga / renueva / reactiva** (`created`, `active`, `updated`, `cycled`, `resumed`, `uncanceled`)
  → **Premium ON** hasta el fin del período. Si el pagador no era suscriptor, se le da de alta activo (ya dio consentimiento al pagar).
- **Cancela** (`canceled`) → se le deja Premium **hasta que venza** el mes ya pagado (no se corta de golpe).
- **Se revoca** (`revoked`: reembolso, impago definitivo) → **Premium OFF de inmediato**.

En la base de datos (tabla `suscriptores`): `premium` (1/0) y `premium_hasta` (fecha de vencimiento).

---

## 5. El correo del domingo: gratis vs. Premium

El deep-dive del domingo es el gran beneficio Premium. Un mismo envío se parte en dos (`engine/contenido/boletin.py` + `pipeline.py`):

- **Premium** → el análisis **completo** (empresa, números, debate de los 8 perfiles, gráfico, "qué observar").
- **Gratis** → un **teaser** con el gancho y el botón de pago. Revela el **sector** pero **nunca** el nombre, los números ni el debate.

El **sábado** (resumen de la semana) y el **diario de lunes a viernes** son **iguales para todos** (no se cobran).

---

## 6. El Enjambre: freemium (1/día vs. 40/mes)

`engine/contenido/limites.py` controla cuántas simulaciones puede disparar cada quien:

| Nivel | Cupo | Cómo se cuenta |
|---|---|---|
| **Gratis** | **1 al día** | por IP (en memoria) |
| **Premium** | **40 al mes** | por correo (en disco, tabla `gasto_premium`) |
| **Muralla global** | **30 al día** (todos juntos) | en disco (tabla `gasto_diario`) — el tope de gasto |

**Economía:** 40 sim × $0,12 = **$4,80 máx/mes** por Premium, contra los **$6,99** que paga → siempre queda margen.

**Cómo desbloquea el Premium sus 40:** en El Enjambre, abajo a la izquierda, el chip **"🔓 ¿Eres Premium?"** — escribe su correo, el motor verifica (`GET /api/pulso/premium`) y le sube el cupo. Se guarda en su navegador. Si cancela, vuelve solo a 1/día.

---

## 7. Variables de entorno (en Render)

> Nunca se guardan en el código ni se comparten por chat. Aquí van solo los **nombres**.

**Del cobro Premium:**
- `POLAR_WEBHOOK_SECRET` — el secreto del webhook de Polar (obligatorio para que el pago prenda el Premium).

**De los límites (opcionales; ya tienen buen valor por defecto):**
- `ENJAMBRE_MAX_SIM_DIA` = `30` (muralla global de la billetera)
- `ENJAMBRE_SIM_DIA_GRATIS` = `1` (cupo gratis diario)
- `ENJAMBRE_SIM_MES_PREMIUM` = `40` (cupo Premium mensual)

**De la web / correo (ya existían):**
- `ENJAMBRE_ORIGENES` — dominios permitidos (CORS). Incluye `https://www.diarioelpulso.com`.
- `RESEND_API_KEY`, `PULSO_ADMIN_EMAIL` — el envío y el correo de revisión.
- `ANTHROPIC_API_KEY` — los cerebros IA.
- `ENJAMBRE_PIPELINE_TOKEN` — protege el disparo del ritual diario.

---

## 8. Cómo dar Premium "a mano" (sin cobrar)

Para regalar Premium a alguien (un amigo, un caso especial, una prueba), la forma **más simple y segura** es un **código de 100% de descuento** en Polar:

1. En Polar → **Descuentos** → crea un código al **100%**.
2. La persona entra a `www.diarioelpulso.com` → **Hazte Premium** → aplica el código en la página de pago de Polar.
3. Paga **$0**, y el webhook le **prende el Premium igual** (pasa por el mismo circuito).

> No hay (todavía) un botón de administrador para prender el Premium directo en la base de datos. Si lo necesitas seguido, se puede construir un pequeño panel protegido — pídemelo.

---

## 9. Cómo probar el circuito completo (sin gastar plata)

1. En Polar → **Descuentos** → crea un código de **100% descuento** (uno de un solo uso para pruebas).
2. `www.diarioelpulso.com` → **Hazte Premium** → aplica el código → completa el "pago".
3. Verifica: llegas a **/gracias**; y en El Enjambre el chip **"🔓 ¿Eres Premium?"** te desbloquea los **40/mes** con ese correo.

---

## 10. El ritual diario (recordatorio)

- **10:00 UTC (≈6:40 AM Chile):** el motor arma la edición y te manda **"📋 Revisar El Pulso"**.
- **Tú apruebas** → recién ahí sale a los suscriptores (siempre con tu visto bueno).
- Lun-vie: diaria · Sáb: resumen · Dom: deep-dive Premium.

---

## 11. Archivos clave (para un desarrollador)

- `engine/contenido/pagos.py` — verifica el webhook de Polar y prende/apaga Premium.
- `engine/contenido/persistencia.py` — `set_premium`, `es_premium`, `contar_premium`, `alta_directa`, `gasto_premium_mes`.
- `engine/contenido/limites.py` — freemium (1/día · 40/mes · muralla global).
- `engine/contenido/boletin.py` — el correo partido (teaser/completo), `teaser_para`, `enviar_a_suscriptores`.
- `engine/server.py` — `POST /pulso/webhook/polar`, `GET /api/pulso/premium`, `POST /api/suscribir`.
- `web/pulso/` — la landing (`index.html`, `gracias.html`, `vercel.json`).
- `web/src/ui/premium.js` — el chip de desbloqueo Premium en El Enjambre.

> ⚠️ Esta integración corre contra el entorno **de producción** de Polar: los pagos son reales.

---
*Rubicón Lab · El Pulso · Documento de referencia · Premium v1*
