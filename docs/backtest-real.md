# Cómo correr el backtest REAL (con los líderes LLM)

> El backtest hace que el enjambre "rinda exámenes": simula noticias del pasado
> con los cerebros LLM de verdad y compara su predicción con lo que hizo el
> mercado esos días. Es la ÚNICA forma honesta de medir el acierto real (el 38%
> en negativas y las mejoras que intentemos, como P2).

## El modelo mental

Tu **API key de Anthropic** es la gasolina y va en **UN solo lugar: Render** (el
motor). GitHub Actions es solo el botón de arranque: le dice al motor "rinde una
tanda", con un **token de seguridad** que NO es tu key. Tu clave **nunca** pasa
por GitHub ni por el chat.

```
[GitHub Actions: botón]  --token-->  [Render: el motor con tu API key]  --> LLM (gasta saldo)
```

## ⚠️ Seguridad (leer primero)

- La `ANTHROPIC_API_KEY` (`sk-ant-...`) va **solo** en el panel de Render.
- **Nunca** la pegues en el chat, en el código, ni en GitHub.
- Si se filtra por accidente: revócala en console.anthropic.com y crea otra.

---

## Paso 1 — Poner tu API key en Render (donde se gasta)

1. Entra a [render.com](https://render.com) → tu servicio **`enjambre-motor`**.
2. Pestaña **Environment** → **Add Environment Variable**.
3. Key: `ANTHROPIC_API_KEY` · Value: tu clave real `sk-ant-...`.
4. **Save Changes.** Render reinicia el motor solo (~1-2 min).

Verificación: el motor debe reportar que la IA está configurada. (Pídeme que lo
compruebe: leo el endpoint de estado y confirmo `ia_configurada: true` — sin ver
tu clave.)

## Paso 2 — El token de disparo (para que solo TÚ puedas correrlo)

Es un "candado" compartido entre GitHub y Render. Inventa un texto largo y
aleatorio (como una contraseña de 30+ caracteres) y ponlo en **los dos** lados,
idéntico:

1. **Render** → Environment → `ENJAMBRE_PIPELINE_TOKEN` = ese texto.
2. **GitHub** → repo → **Settings → Secrets and variables → Actions →
   New repository secret** → `ENJAMBRE_PIPELINE_TOKEN` = el **mismo** texto.

Si no coinciden, el motor rechaza el disparo (falla cerrado, por diseño).

## Paso 3 — Correr una tanda

1. GitHub → pestaña **Actions** → workflow **"Backtest histórico (tanda)"**.
2. **Run workflow** → parámetros:
   - `tanda`: cuántos exámenes rendir (máx 20).
   - `mercado` (opcional): `cripto` / `indice` / `oro` / `petroleo` / `accion`
     (vacío = todos).
3. El workflow despierta el motor y le pide la tanda. El motor hace las llamadas
   LLM (gasta tu saldo en Render), guarda cada examen al instante y lo respalda
   en GitHub. ~1 minuto por examen.

También se puede desde la **app móvil de GitHub** (Actions → Run workflow).

## Paso 4 — Costo y caché

- Cada simulación ≈ **~110 llamadas** a `claude-sonnet-5` (+ portero haiku).
  Costo estimado del proyecto: **~$0.12 por simulación** (CLAUDE.md §5).
  Una tanda de 20 ≈ **~$2.40**.
- **Caché:** los exámenes ya rendidos responden **gratis** (la caché de cerebros
  ya tiene la respuesta). Solo pagas por exámenes **nuevos**. Para rendir muchos,
  corre varias tandas.

## Paso 5 — Ver el acierto (después de rendir)

Los exámenes rendidos quedan en el respaldo público de GitHub. Para ver el
acierto por segmento:

```bash
python engine/calibration/validacion_base.py --desglose
```

Muestra el acierto por **mercado**, **magnitud** y **sentimiento**. **No necesita
API key** (solo lee resultados ya rendidos). Puedo correrlo yo en una sesión:
tras una tanda, avísame y te traigo los números frescos.

## Nota para medir una MEJORA de código (P2, etc.)

Para saber si un cambio de código (ej. P2: separar "clima" de "apuesta") mejora
el 38%, hay que rendir exámenes **con el código nuevo ya desplegado en Render**.
La agregación del tono se recalcula fresca (no se cachea), así que el efecto del
cambio se ve al rendir. Lo honesto: comparar el acierto ANTES vs DESPUÉS del
cambio sobre el mismo conjunto de exámenes.

---

## Resumen de las 3 variables

| Variable | Dónde | Para qué |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Render** | los cerebros LLM (aquí se gasta el saldo) |
| `ENJAMBRE_PIPELINE_TOKEN` | **Render** + **GitHub** (idéntico) | candado para disparar el backtest |
| (ya configuradas) | — | Alpaca/Barchart/Resend si aplica |

*Fuente: `.github/workflows/backtest.yml`, `engine/server.py` (`/api/backtest`),
`engine/brains/cerebro.py` (lee `ANTHROPIC_API_KEY`), `docs/despliegue.md`.*
