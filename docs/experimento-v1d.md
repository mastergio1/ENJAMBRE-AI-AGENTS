# Experimento v1d — el oído nuevo, medido

Fecha: 3–4 de septiembre de 2026  
Rama: `calibracion/impacto-no-lineal`  
Costo: ~US$3 (24 simulaciones, cerebros Claude reales)  
Producción: **baseline, no se tocó**

Hipótesis: tres reglas en el prompt (priced-in ≈ 0, earnings = beat/miss
de ESA empresa, no sopa de tickers) callan a la Fed-en-pausa y dejan
gritar a Lehman.

**Veredicto: no pasa.** No se enciende v1e. No se fusiona.

Todos los 12 baseline salieron con 1000/1000 voces IA.
v1d: media 810/1000 (el prompt más largo hizo timeout; parte cayó
al diccionario). Eso ya es una palanca sucia.

## Tabla (porcentaje que movió el enjambre)

| Titular | Qué debería pasar | Hoy | v1d | ¿Mejor? |
|---|---|---:|---:|---|
| Fed holds, as widely expected | casi 0 | −4.4 | **+3.4** | No. Dejó de caer e **inventó** una subida |
| Fed pauses, more hikes ahead | casi 0 / levemente − | −1.1 | **+7.5** | No. Más fuerte, signo al revés |
| CPI in line, Fed unchanged | casi 0 | +6.0 | +6.3 | No |
| Fed holds, inflation transitory | casi 0 | +6.9 | −2.4 | A medias: más chico, signo al revés |
| Tarifas que aturden | fuerte − | −2.6 | −3.9 | Sí, un poco más crash |
| Lehman quiebra | fuerte − | −8.0 | −9.9 | Sí, sigue gritando |
| S&P −12 % pese al recorte a 0 | fuerte − | −5.4 | −8.9 | Sí |
| Amazon pérdida trimestral | − | −2.8 | **−16.2** | Signo ok, magnitud 3× peor |
| Meta crater −20 % | ~−20 | −5.8 | −22.1 | Magnitud más parecida al titular |
| Target sube guidance | + chico, no +50 | **+42** | **+53** | No. Peor |
| Eli Lilly (sopa) | no +42 | +42 | +12 | Sí, bajó el grito |
| NVIDIA CEO / cobre | ruido, chico | +31 | +40 | No |

## Por grupo (|movimiento| medio)

| Grupo | Hoy | v1d |
|---|---:|---:|
| Fed / CPI ya en el precio | 4.6 % | **4.9 %** (no calló) |
| Crashes | 5.3 % | 7.6 % (no se apagó, bien) |
| Resultados | 16.9 % | **30.3 %** (gritó más) |
| Ruido / sopa | 36.8 % | 26.1 % (Lilly salvó el promedio) |

## Criterios de paso, uno por uno

1. Fed-en-pausa se calla, sin inventar signo → **falló**
2. Lehman / aranceles siguen fuertes → **cumplió**
3. Target / Lilly no salen +50 % → Target **empeoró**; Lilly mejoró. **No basta**

Una palanca que calla un Lilly y enciende un Target +53 % no va a producción.

## Qué se aprende (para no repetir v1a)

El prompt **no disciplina la magnitud**. A veces cambia el signo.
Los crashes no se apagaron (eso importa: no es un mute total).
El cuello sigue siendo: “ya estaba en el precio” no se traduce a
una señal cerca de 0.

Siguiente golpe al oído, no al volumen: un campo numérico `sorpresa`
(0–1) en el JSON del cerebro, que **multiplica** la señal después.
El modelo no tiene que “hablar bajito”; el motor le baja el volumen
si dice que no hay sorpresa. Eso no se enciende hasta diseñarlo
como v1f, una palanca, medido igual que esto.

*Rubicón Lab · v1d medida · 4 sep 2026*
