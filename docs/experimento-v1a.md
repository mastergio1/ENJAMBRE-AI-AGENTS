# Experimento v1a — baseline vs 2 perillas

Fecha: 3 de septiembre de 2026  
Rama: `calibracion/impacto-no-lineal`  
Costo: **US$0** (shocks numéricos, sin API)  
Motor: 10.000 agentes, 40 ticks de calentamiento + 120 de reacción  
Semillas: 42, 7, 19 (18 corridas por set)

**Hipótesis flaca:** solo `impacto_base = 2.0` y `umbral_panico = 0.45`.  
Todo lo demás idéntico al enjambre de hoy.

## Veredicto: no pasa. No ir al paso 2.

v1a hace lo **contrario** de lo que necesitamos: infla los días chicos y casi no mueve los extremos.

| Pregunta | Resultado |
|---|---|
| ¿Subió la magnitud en shocks grandes? | **No.** 10.7 % → 11.0 % (×1.03) |
| ¿Los días chicos se quedaron chicos? | **No.** 3.9 % → 8.0 % (×2.05) |
| ¿La dirección se mantuvo? | **Sí.** 89 % → 100 % |

Analogía: subimos el volumen de todo el altavoz. Los susurros se vuelven gritos. Los gritos ya estaban al tope del parlante y no suenan más fuerte.

## Tabla (media de |movimiento| en 3 semillas)

| Shock | Tipo | Hoy (baseline) | v1a | Ratio |
|------:|------|---------------:|----:|------:|
| +0.20 | día normal | 1.8 % | 7.3 % | **×4.1** |
| −0.25 | día normal | 3.1 % | 5.3 % | ×1.7 |
| −0.35 | día normal | 3.4 % | 7.1 % | ×2.1 |
| +0.40 | día normal | 7.3 % | 12.3 % | ×1.7 |
| +0.85 | extremo | 10.6 % | 11.3 % | ×1.06 |
| −0.90 | extremo | 10.8 % | 10.7 % | ×0.99 |

Dirección: 16/18 aciertos hoy, 18/18 con v1a. Eso es lo único que mejoró — y no justifica días normales al doble.

## Por qué pasa esto (en simple)

1. Multiplicar ×2 **todas** las señales hace que una noticia tibia se sienta como una fuerte. Es exactamente el fallo de “Fed en pausa” (−7.4 % simulado vs +1.4 % real).
2. Un crash numérico **ya** mueve ~11 % en el libro de órdenes. Los fundamentalistas frenan. Empujar más no agrega recorrido: a veces hasta revierte (semilla 7, shock −0.90: −13.6 % → −8.9 %).
3. El 3–5 % vs 8–12 % del plan **no** es “el libro no puede moverse”. En shocks numéricos puros, el enjambre **sí** llega a 8–14 %. El corto contra el mercado real está más arriba: en cómo los cerebros **leen** el titular (consenso suave, Nvidia mal leída, etc.).

## Qué no hacemos ahora

- No fusionar a `main`.
- No activar `hipotesis_v1b` (es v1a + más perillas: peor para aislar).
- No gastar ~US$1.50 en 12 noticias reales con esta hipótesis: ya sabemos que infla días chicos.

## Si hay un paso 2 distinto (no autorizado aún)

Una hipótesis más honesta sería **no** tocar `impacto_base` y solo encender pánico cuando `|señal| ≥ umbral`, para dejar los días chicos en paz. Aun así, este experimento sugiere que el techo del libro ya está cerca en los extremos: el siguiente golpe de verdad probablemente no es una perilla, sino los cerebros.

Archivos crudos (locales, no van a git): `engine/config/experimentos/baseline_20260903T123938Z.json` y `hipotesis_v1a_20260903T124144Z.json`.

*Rubicón Lab · experimento v1a · 3 sep 2026*
