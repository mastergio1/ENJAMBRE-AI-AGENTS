# Auditoría de seguridad previa al despliegue

> Revisión por capas del motor (FastAPI/WebSocket), datos (SQLite), frontend
> (XSS/CSP), configuración de despliegue, secretos y controles de costo/DoS.
> Fecha: julio 2026. Para Giorgio.

## Veredicto

El sistema está **bien blindado**. No hay agujeros críticos (ni ejecución
remota, ni inyección SQL, ni fuga de secretos). Los hallazgos se dividen en
dos: los de **código** (ya corregidos) y los de **configuración de
despliegue** (se resuelven al conectar Vercel y Render).

## ✅ Corregido en el código

| # | Nivel | Hallazgo | Corrección |
|---|---|---|---|
| XSS | Medio (ya mitigado por CSP) | El tooltip del líder pintaba `lider.frase` (texto del LLM, influenciable por el titular) vía `innerHTML` sin escapar. | Se escapa con `esc()`. Test extendido al tooltip. |
| Timing | Bajo | Los 4 endpoints protegidos comparaban el token de admin con `!=` (no constante). | `hmac.compare_digest` vía helper que falla cerrado. Tests: token malo → 403. |
| Cadena de suministro (B) | Medio | `requirements.txt` con `>=`: builds no reproducibles. | Versiones fijas (`==`). Dev-deps (pytest/httpx) movidas a `requirements-dev.txt` (fuera de la imagen de producción). |
| Abuso de correo (C) | Medio | `/api/suscribir` reenviaba la confirmación en cada intento → posible bombardeo de un tercero. | Ventana antirreenvío de 10 min por dirección; la respuesta no revela si el correo ya existía. |
| Contenedor (E) | Bajo | La imagen corría como `root` y sin `.dockerignore`. | Usuario no-root (uid 10001) + `.dockerignore`. |

## 🔧 Pendiente para el momento del despliegue

| # | Nivel | Hallazgo | Acción |
|---|---|---|---|
| A | Alto (funcional) | La CSP de Vercel aplica `frame-ancestors 'none'` a **todo**, incluido `widget.html` → el widget no se podrá incrustar en ningún medio. No es un riesgo, es una traba de más. | Exceptuar `widget.html` en `vercel.json` (requiere probar cómo Vercel fusiona cabeceras duplicadas; hacerlo y verificarlo en el deploy). |
| D | Medio | Se toma la IP del **último salto** de `X-Forwarded-For`. Hay que confirmar en la doc de Render que ese salto es la IP real del cliente y no una IP compartida del borde. | Verificar con una prueba real en el primer deploy. Si fuera IP compartida, ajustar `seguridad.ip_cliente`. |
| G | Bajo | El CORS permite cualquier `*.vercel.app`. La API no usa cookies (data pública o token en header), así que el riesgo es bajo. | Fijar el dominio real en `ENJAMBRE_ORIGENES` y, si se quiere, quitar el comodín del regex. |
| F | Bajo | Los límites (rate-limit y tope diario) viven en la RAM de una instancia. En plan free (1 instancia) es correcto; con varias instancias se vuelven evadibles y el tope diario se reinicia al reiniciar el proceso. | Documentar el supuesto de 1 instancia. Opcional: programar `seguridad.limpiar()` y/o mover el estado a un almacén compartido si se escala. |
| H | Bajo | No hay tope de **conexiones WebSocket** simultáneas por IP (sí de trabajo pesado). | Render impone un límite de plataforma; opcional: cap por IP. |

## 🛡️ Controles ya presentes (bien hechos)

- **SQL 100% parametrizado** — sin inyección; los únicos `f-string` en consultas
  arman nombres de columna fijos, nunca datos del usuario.
- **Path traversal** en replays/imágenes: `sim_id` validado como hex de 16 +
  verificación de que la ruta no sale de su carpeta (doble muralla).
- **Anti-abuso / anti-DoS**: rate-limit deslizante por IP en `/api/*` (con clase
  más estricta para `/replay`), límite de simulaciones por IP (3/hora) + tope
  diario global (5), semáforos de concurrencia (2 simulaciones, 2
  observatorios), auto-cierre del observatorio (~8 min / 6000 ticks).
- **Secretos**: nada versionado; `render.yaml` con `sync:false` y token de
  pipeline autogenerado; `.env` en `.gitignore`; imagen sin `.env`.
- **Cabeceras**: `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`,
  CSP (`default-src 'none'` en la API; `script-src 'self'` sin `unsafe-inline`
  en la web), HSTS.
- **Suscripción** double opt-in con tokens de alta entropía
  (`secrets.token_urlsafe`), baja de un clic.
- **Validación de entradas**: titular `[:300]`, email (regex + longitud), seed y
  ritmo con guardas y pisos anti-flood, `sim_id` hex16, fecha `AAAA-MM-DD`.
- **Filtro CMF** (`vocabulario.py`) sobre todo texto publicable.
- **WebSocket** robusto: límite de tamaño de mensaje, JSON malformado no tumba
  la conexión, un fallo aísla solo esa conexión.
- **Frontend**: escapado del contenido no confiable antes de `innerHTML` en
  muro, archivo, duelo, widget, reporte y tooltip.

## Cómo se verificó

Suite de tests de la capa de seguridad y de contenido en verde tras los
cambios (incluye guardas de código para el escapado y el token constante, y
pruebas funcionales de 403 y del antirreenvío).
