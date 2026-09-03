# Experimento v1c — zona muerta vs baseline

Fecha: 3 de septiembre de 2026  
Rama: `calibracion/impacto-no-lineal`  
Costo: **US$0** (shocks numéricos, sin API)  
Motor: 10.000 agentes, 40 ticks de calentamiento + 120 de reacción  
Semillas: 42, 7 (12 vs 12 corridas)

**Hipótesis flaca (1 perilla):** `umbral_consenso = 0.25`.  
`impacto_base` sigue en 1. Los líderes oyen el shock completo; el tono
ambiente (lo que sienten todos) se apaga si es más chico que 0.25.

## Veredicto: hace lo que prometió en días chicos. No va a producción.

v1c es lo **contrario** de v1a: en vez de subir el volumen, tapa el
susurro. Los días normales se achican. Los extremos casi se mantienen.
Un shock tibio positivo (+0.20) puede **cambiar de signo** porque el
ambiente queda en cero y el libro hace ruido.

| Pregunta | Resultado |
|---|---|
| ¿Se inflan los días chicos? (el pecado de v1a) | **No.** 4.1 % → 1.2 % (×0.31) |
| ¿Los extremos siguen siendo extremos? | **Casi.** 9.9 % → 8.5 % (×0.86) |
| ¿La dirección se mantiene? | **No del todo.** 12/12 → 10/12. Fallan los +0.20 |

## Tabla (media de 2 semillas)

| Shock | Tipo | Hoy (baseline) | v1c | ¿Qué pasó? |
|------:|------|---------------:|----:|---|
| +0.20 | día normal | +1.5 % | **−0.3 %** | ambiente apagado; el signo se va |
| −0.25 | día normal | −4.1 % | −1.4 % | más chico, signo ok |
| −0.35 | día normal | −4.7 % | −1.4 % | más chico, signo ok |
| +0.40 | día normal | +6.0 % | +1.8 % | más chico, signo ok |
| +0.85 | extremo | +8.7 % | +9.6 % | se mantiene |
| −0.90 | extremo | −11.0 % | −7.3 % | un poco más flojo (semilla 7: −13.6 → −6.9) |

## Lectura en simple

Analogía: v1a subió el volumen de todo el altavoz. v1c pone un ruido
de fondo mínimo: si la prensa habla bajito, el mercado no se entera;
si grita, sí. Eso es lo que queríamos para “Fed en pausa, como se
esperaba”. El costo: un empujón suave ya no mueve al rebaño entero, y
a veces el libro decide solo (de ahí el +0.20 que se pone rojo).

Esto **no** prueba el 70 % contra el mercado real. Prueba que la perilla
no rompe el parlante. El 70 % vive en los cerebros (ver
[libreta-honesta.md](libreta-honesta.md): hoy 60 %, techo Wilson 64 %).

## Qué no hacemos

- No fusionar a `main`.
- No poner `conjunto_activo = hipotesis_v1c`.
- No gastar ~US$75 re-rindiendo 632 noticias con v1c: primero una
  tanda chica (8–12 titulares, priced-in vs sorpresa) cuando la clave
  de Claude esté en este entorno.
- No bajar el umbral a 0.15 en la misma sesión. Una hipótesis por vez.

Archivos crudos (locales, no van a git):
`engine/config/experimentos/baseline_20260903T213441Z.json` y
`hipotesis_v1c_20260903T213552Z.json`.

*Rubicón Lab · experimento v1c · 3 sep 2026*
