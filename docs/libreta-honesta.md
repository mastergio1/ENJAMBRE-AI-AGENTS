# Libreta honesta — 632 exámenes con IA

Fecha: 3 de septiembre de 2026  
Fuente: `datos/calibracion.json` (rama `respaldo-datos`, generado 2-sep)  
Costo de este informe: **US$0** (no se re-rindieron exámenes; se releyó lo ya pagado)  
Rama: `calibracion/impacto-no-lineal`

Antes hablábamos de “12 casos” y de un 62 %. Eso era una muestra chica.
En la caja fuerte hay **632 casos con cerebros IA reales**. Con n=632
el intervalo de Wilson ya es estrecho: ya no cabe esconderse.

## Veredicto

**No está listo. No es 70 %.**

| Meta | Hoy (IA, n=632) | ¿Pasa? |
|---|---|---|
| Dirección ≥ 70 % | **60 %**  (Wilson 95 %: **56–64 %**) | No. El techo del intervalo es 64 %. |
| Fuerza simétrica ≥ 0.70 | **0.46** | No. |
| Dentro de ±30 % del real | **13 %** | No. |
| n ≥ 80 | 632 | Sí. |
| `listo_produccion` | **False** | — |

El enjambre **se pasa de largo**: hace de media **3.1×** el movimiento real
(sim 17 % vs real 11 %). Antes la Loss premiaba eso. Ahora lo cuenta como error.

Desglose de errores: **239 signo mal**, 173 exagera, 142 acierto, 65 se queda corto, 13 plano.

## Por mercado (el producto es índice + acción)

| Mercado | n | Dirección | Wilson | Fuerza | Sim vs real |
|---|---:|---:|---|---:|---|
| cripto | 233 | 67 % | 61–73 % | 0.47 | 24 % vs 16 % |
| acción | 221 | 59 % | 52–65 % | 0.47 | 19 % vs 12 % |
| **índice (SPY/QQQ/…)** | **155** | **54 %** | **46–61 %** | 0.45 | 7 % vs 4 % |
| índice + acción | 376 | 57 % | 52–62 % | 0.46 | 14 % vs 8 % |

En el S&P el enjambre está **cerca de una moneda**. El 67 % de cripto no
salva el producto: ahí el mercado real también es un volcán, y aun así
el enjambre grita 3×.

## En vivo (lo que ve el muro, n=23)

Dirección 52 % (Wilson 33–71 %, inútil). Sim **26 %** vs real **5 %**.
Ejemplos: Target guidance +58 % simulado vs +3.8 % real; Medline +40 %
simulado vs −18 % real (signo mal y 2× de más). El enjambre **grita**
en las noticias del día.

## Casillas (taxonomía léxica)

La red de pesca léxica deja **452/632 en “otro / ambiguo”**: los cables
de Benzinga no parecen un titular de manual. Aun así, donde sí etiqueta:

- **Macro “ya estaba en el precio”** (n=3): acierta el signo, **exagera 5×**.
  Es el fallo tipo Fed-en-pausa.
- **Resultados** (n=38+5): mejor dirección (~66–80 %), n chico.
- **Geopolítica** (n=57): 56 %, casi moneda.

## Qué no es este número

No es un examen nuevo. Es la nota de lo que **ya se rindió** con el
enjambre de producción (baseline). v1c no está activada. Re-rendir
esos 632 con otra hipótesis costaría ~US$75 y no se hace hasta que
una hipótesis gane barato.

*Rubicón Lab · libreta honesta · 3 sep 2026*
