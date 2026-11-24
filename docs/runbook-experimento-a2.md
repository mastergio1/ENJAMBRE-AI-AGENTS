# Runbook — Experimento A2 / M4 vs A3 (para una sesión NUEVA con la clave)

> Para Claude en una **sesión nueva** (donde `ANTHROPIC_API_KEY` ya está en el
> entorno). Pregunta: **¿un solo LLM neutral (A2/M4) iguala al consenso de ~110
> cerebros (A3)?** Si empata, el reparto de 110 cerebros no compra acierto
> direccional y es gasto evitable. Plan rector: `docs/plan-maestro-v5.md`.

> Todos los comandos se corren desde la RAÍZ del repositorio.

## 0. Pre-chequeo

```bash
python3.13 -c "import os;print('clave:', 'OK' if os.environ.get('ANTHROPIC_API_KEY') else 'FALTA — abrir sesión nueva')"
```
Si dice FALTA, parar: la clave se agrega como variable de entorno del entorno de
nube (no en Render) y la toma una sesión nueva. No inventar resultados.

> **Lección (2026-11-24):** la clave puede estar guardada en el entorno y aun así
> decir FALTA — pasa si la sesión se abrió ANTES de guardarla (las variables se
> inyectan solo al arrancar una sesión). Solución: abrir una sesión NUEVA. No
> buscar la clave en otros procesos ni pedirla por chat.

## 1. Correr A2 (un LLM neutral por titular, cacheado)

Los datos ya están en el repo (`docs/datos-investigacion/`). Esto hace ~1 llamada
LLM por titular único (claude-sonnet-5, sin `temperature`), cacheada por titular:

```bash
python3.13 engine/calibration/un_llm.py \
  docs/datos-investigacion/calibracion.con_fecha.json \
  docs/datos-investigacion/calibracion.json \
  docs/datos-investigacion/a2_senales.json
```

## 2. Ver A2 dentro de la escalera (M4 vs A3) y el metamodelo

```bash
python3.13 engine/calibration/ablacion.py \
  docs/datos-investigacion/calibracion.con_fecha.json \
  docs/datos-investigacion/calibracion.json \
  --a2 docs/datos-investigacion/a2_senales.json
```

En la tabla, comparar **A2_un_llm** (M4) contra **A3_consenso**:
- Si A2 ≈ A3 (dentro del IC) → **la diversidad de 110 cerebros no paga**: un LLM
  basta para la dirección. Decisión: abaratar (reducir el reparto).
- Si A3 > A2 (sin solape de IC) → la diversidad aporta; conservar el reparto.
- Si A2 > A3 → el consenso está perdiendo señal al promediar; investigar.

## 2b. Comparar titular por titular (A2 vs A3, misma cobertura)

```bash
python3.13 engine/calibration/a2_vs_a3.py \
  docs/datos-investigacion/calibracion.con_fecha.json \
  docs/datos-investigacion/calibracion.json \
  docs/datos-investigacion/a2_senales.json \
  docs/datos-investigacion/a2_vs_a3_titulares.md
```

Por mercado (índice primero) imprime: cobertura común, acierto de A2 y A3 sobre
los MISMOS casos con IC honesto, diferencia pareada A2−A3 por evento (la prueba
principal), discordancias (solo A2 acierta vs solo A3 acierta, McNemar indicativo),
acuerdo de signo y correlación de señales, y una línea de veredicto. El `.md` es la
tabla caso a caso (discordancias primero) para leer DÓNDE difieren.

## 3. Interpretar con honestidad (reglas del plan v5)

- Es **exploratorio** (banco histórico de shocks, sesgado por selección; n chico). No
  declarar veredicto definitivo: eso es prospectivo.
- Reportar el acierto de A2 y A3 con su **IC** y su **n**; no comparar a coberturas
  distintas.
- Si los IC se solapan, el veredicto honesto es **"no distinguible con estos datos"**,
  no "iguales" ni "uno gana".

## 4. Guardar (en la rama `claude/m-d-file-6z1e63`, no en main)

- Commitear `docs/datos-investigacion/a2_senales.json` (el caché, para repetir sin
  costo), `docs/datos-investigacion/a2_vs_a3_titulares.md` (la tabla caso a caso) y
  un `docs/hallazgo-a2-un-llm.md` con la tabla, la comparación pareada, ejemplos de
  discordancias y la interpretación honesta.
- Empujar a la rama. NO desplegar (es análisis offline, no toca producción).
- Avisar a Giorgio en simple: qué salió y qué implica para el costo de IA.

## 5. Siguiente (si queda tiempo / otra sesión)

- **M13 vs M13-null con A2 incluido** ya corre (`calibration/metamodelo.py`); el
  siguiente salto real es extraer **features ricas del ABM** (order imbalance, manada,
  dispersión…) re-corriendo simulaciones — eso necesita diseño aparte.
- **F05**: banco cronológico de flujo (eventos por reglas ex-ante) — recolección nueva.
