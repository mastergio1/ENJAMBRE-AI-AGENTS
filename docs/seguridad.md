# Seguridad y blindaje — El Enjambre

> Resumen de las murallas que protegen la web pública contra caídas por
> tráfico, abuso de presupuesto, XSS y otros. Auditoría + blindaje de la
> sesión de julio 2026 (Fases 1 y 2). Cada muralla tiene su test.

## Lo que se blindó

| # | Riesgo | Muralla | Dónde |
|---|--------|---------|-------|
| 1 | Flood a los endpoints HTTP tumba el sitio | Rate-limit por IP en `/api/*` (120/min; `/replay` 30/min) → HTTP 429 | `contenido/seguridad.py`, middleware en `server.py` |
| 2 | `database is locked` bajo carga | SQLite en modo WAL + `busy_timeout`; esquema creado una sola vez, no por request | `contenido/persistencia.py` |
| 3 | Rate-limit burlado tras el proxy | La IP real se lee del **último salto** de `X-Forwarded-For` (anti-spoofing) | `seguridad.ip_cliente` |
| 4 | XSS almacenado vía titulares/frases | Todo texto de datos (Alpaca/LLM) se **escapa** antes de ir a `innerHTML`; ids se filtran a hex | `web/src/muro/muro.js`, `web/src/ui/panel.js` |
| 4b | XSS — segunda muralla | **CSP estricta** en la página (`script-src 'self'`, `object-src 'none'`, sin `unsafe-eval`) | `web/vercel.json` |
| 5 | Path traversal en `/replay` | `sim_id` validado como `^[0-9a-f]{16}$` + la ruta jamás sale de `frames/` | `seguridad.sim_id_valido`, `persistencia.ruta_frames` |
| 6 | Avalancha de simulaciones agota CPU/RAM | Semáforo global (máx 2 simultáneas) + tope diario **5** + `ritmo` mínimo | `server.py`, `contenido/limites.py` |
| 7 | Entrada malformada tumba la conexión | El WebSocket valida tamaño y JSON, responde error y sigue; ningún fallo tumba el servidor | `server.py` canal `/ws` |
| 8 | CORS abierto a cualquiera | Orígenes restringidos a la web de producción + `*.vercel.app` (configurable con `ENJAMBRE_ORIGENES`) | `server.py` |
| 9 | Cabeceras faltantes | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, CSP en la API; HSTS + CSP en la web | `seguridad.CABECERAS_SEGURIDAD`, `vercel.json` |
| 10 | Fuga de memoria del limitador | Poda de ventanas vencidas (`seguridad.limpiar`) | `contenido/seguridad.py` |

## El presupuesto (decisión de Giorgio)

`ENJAMBRE_MAX_SIM_DIA = 5` — máximo **5 simulaciones on-demand nuevas por
día** en todo el sitio. El on-demand es un lujo, no un regalo: es la
muralla de la billetera LLM. Las destacadas del día (pipeline) y re-ver
simulaciones ya guardadas NO cuentan contra este tope (salen de caché,
costo cero). Al agotarse, el muro invita a suscribirse al Pulso.

Se ajusta sin tocar código: variable de entorno en el panel de Render.

## Verificado en vivo

- Flood de 135 requests a `/api/muro` → 120 servidas, 15 cortadas con 429.
- `GET /api/simulacion/..%2f..%2fsecreto/replay` → 404.
- Titular con `<img onerror>` inyectado en la base → se muestra como
  texto, no ejecuta código, no crea el nodo (Playwright).
- 62 tests verdes, 12 de ellos específicos del blindaje.

## Lo que queda para cuando escale (no urgente)

- El rate-limit y el tope viven en memoria de una instancia. Si algún día
  hay más de una instancia, mover a Redis o al proxy (Cloudflare).
- Poner Cloudflare (gratis) delante de Vercel + Render suma protección
  DDoS volumétrica y caché de borde — la defensa que ninguna app puede
  darse a sí misma.
- Persistencia del disco en Render: el plan free es efímero (el pipeline
  regenera el día). Para archivo histórico real, subir de plan y montar
  disco en `/app/datos` (ver `docs/despliegue.md`).
