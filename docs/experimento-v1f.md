# Experimento v1f — senal × sorpresa

Fecha: 4 de septiembre de 2026  
Rama: `calibracion/impacto-no-lineal`  
Costo: ~US$1.50 (12 simulaciones nuevas; baseline de caché)  
Producción: **baseline, no se tocó**

Hipótesis: el cerebro declara `sorpresa` ∈ [0, 1] y el **motor** hace
`senal × sorpresa`. v1d pedía hablar bajito y no lo hizo.

**Veredicto de producto: no pasa (aún).**  
**Veredicto de oído: sí mejoró.** No se fusiona.

IA real: 996/1000 voces. El campo `sorpresa` salió en los 108 cerebros
de cada titular.

## Lo que oyeron los cerebros (después de recortar)

| Titular | sorpresa media | senal media | Lectura |
|---|---:|---:|---|
| Fed as expected | **0.09** | +0.02 | Casi 0. El oído calló |
| Fed pause + more hikes | 0.20 | −0.02 | Casi 0 |
| CPI in line | **0.07** | +0.02 | Casi 0 |
| Fed transitory | **0.08** | +0.02 | Casi 0 |
| Tarifas stun | 0.76 | −0.24 | Sigue siendo crash |
| Lehman | **0.92** | −0.58 | Sigue gritando |
| S&P −12 % | 0.78 | −0.24 | Crash |
| Amazon pérdida | 0.66 | −0.18 | Miss |
| Meta crater | 0.59 | −0.15 | Miss |
| Target guidance | 0.58 | +0.27 | Beat, no luna |
| Lilly sopa | 0.27 | +0.10 | Bajó el drama |
| NVIDIA CEO / cobre | 0.18 | +0.05 | Ruido, bajito |

Eso es el micrófono que queríamos. v1d no lo logró.

## Lo que hizo el precio (el parlante)

| Titular | Hoy | v1f | ¿El producto mejoró? |
|---|---:|---:|---|
| Fed as expected | −4.4 | −2.7 | Un poco más chico; no es 0 |
| Fed pause | −1.1 | **+6.3** | No. Inventó una subida |
| CPI in line | +6.0 | +4.5 | Sigue ruidoso |
| Fed transitory | +6.9 | +2.0 | Mejor, no listo |
| Tarifas | −2.6 | −1.2 | Se **apagó** de más |
| Lehman | −8.0 | −5.9 | Un poco más flojo |
| S&P −12 % | −5.4 | −3.9 | Más flojo |
| Amazon | −2.8 | −2.2 | — |
| Meta crater | −5.8 | **+0.3** | Signo al revés |
| Target | +42 | +36 | Sigue siendo un grito |
| Lilly | +42 | +24 | Bajó; sigue grande |
| NVIDIA | +31 | +19 | Bajó; sigue grande |

Fed/CPI |mov|: 4.6 % → 3.9 %. No es ~0.  
Crashes: 5.3 % → 3.6 % (se apagaron un poco: no queremos eso).  
Target sigue en +36 %.

## Qué se aprende

1. Pedir un **número** y recortar en el motor **sí** hace que Fed-en-pausa
   tenga senal ≈ 0. El prompt solo (v1d) no.
2. Con senal ≈ 0 el **enjambre igual se mueve ±6 %**: ruido del libro y
   de los arquetipos que se cancelan mal. El silencio del oído deja oír
   el parlante vacío.
3. senal +0.27 (Target) todavía se vuelve **+36 %** en el precio.
   El cuello ahora es el parlante, no el oído.

No se enciende en producción. Siguiente palanca, si se sigue:
zona muerta (v1c) **encima** de v1f, para que un consenso ~0 no inyecte
ruido al ambiente — ahora sí hay evidencia de que el oído calla.

*Rubicón Lab · v1f medida · 4 sep 2026*
