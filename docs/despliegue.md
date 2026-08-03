# Despliegue de El Enjambre — guía paso a paso

El producto tiene dos piezas: el **motor** (Python, simula el mercado) y la
**web** (la escena 3D). Se despliegan por separado y se conectan por WebSocket.

```
[Vercel: web estática]  ←── WebSocket ──→  [Render: motor Python]
```

## 1. El motor en Render (gratis)

1. Crear cuenta en [render.com](https://render.com) e iniciar sesión con GitHub.
2. **New → Blueprint** → elegir el repositorio `ENJAMBRE-AI-AGENTS`.
   Render lee `render.yaml` y configura todo solo.
3. En el panel del servicio → **Environment** → agregar la variable
   `ANTHROPIC_API_KEY` con la clave real (los 100 cerebros LLM).
   *Sin la clave el motor funciona igual, con el fallback léxico.*
4. Al terminar el deploy, Render entrega una URL tipo
   `https://enjambre-motor.onrender.com`. Verificar:
   `https://enjambre-motor.onrender.com/salud` debe responder `{"estado":"ok"}`.

> Nota del plan gratis: el servicio se duerme tras 15 minutos sin uso y la
> primera visita tarda ~1 minuto en despertarlo. Para demos con clientes,
> abrir el link 2 minutos antes (o subir al plan Starter).

## 2. La web en Vercel (gratis)

1. Crear cuenta en [vercel.com](https://vercel.com) con GitHub.
2. **Add New → Project** → elegir el repositorio → **Root Directory: `web`**.
3. En **Environment Variables** agregar:
   - `VITE_WS_URL` = `wss://enjambre-motor.onrender.com/ws`
     (la URL de Render del paso anterior, con `wss://` y `/ws` al final).
4. Deploy. Vercel entrega el link público, ej. `https://enjambre.vercel.app`.

## 3. Comprobación end-to-end

Abrir el link de Vercel, apretar el chip **"Quiebra bancaria"** y verificar:

- el HUD abajo a la izquierda dice **"motor real"** (si dice "demo local",
  revisar `VITE_WS_URL` y que el motor de Render esté despierto);
- el enjambre se tiñe de rojo en ola y el precio cae;
- al terminar (~15 segundos) aparece el **reporte** con dirección,
  volatilidad y desglose por tipo de inversionista.

## Correr todo en local (desarrollo)

```bash
# terminal 1 — motor
cd engine && source .venv/bin/activate && uvicorn server:app --port 8000

# terminal 2 — web (detecta el motor local sola)
cd web && npm run dev
```

## Presupuesto LLM

Cada simulación = 100 llamadas a `claude-sonnet-5` (una por líder), dentro
del presupuesto de CLAUDE.md (~100-120). Las respuestas se cachean por
(titular, arquetipo, semilla): repetir la misma demo no cuesta nada.
