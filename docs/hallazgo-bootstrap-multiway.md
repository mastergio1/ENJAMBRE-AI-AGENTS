# Hallazgo — Bootstrap multiway: el 80% es menos seguro de lo que parecía

*Rubicón Lab · El Enjambre · 2026-11-23. Fase 0.5. El bootstrap por activo
(intervalos.py) no captura que 4 ETFs reaccionando a la misma noticia no son 4
experimentos independientes. Esta herramienta
(`engine/calibration/intervalos_multiway.py`, con tests) recalcula el intervalo
agrupando por activo, por evento (fecha) y por período (año). Sin IA.*

## Resultado (índice, sin fuga)

### Señal base (todos los casos direccionables, n=142)
| Agrupado por | Acierto | IC 95% | nº grupos |
|---|---:|:---:|---:|
| activo | 62.7 % | [52.5–70.4] | 4 |
| evento (fecha) | 62.7 % | [54.9–70.8] | 89 |
| período (año) | 62.7 % | [57.0–69.4] | 9 |

**Robusto:** el intervalo es parecido bajo las tres agrupaciones y siempre excluye
el 50 %. La señal base ~62.7 % se sostiene. Sensibilidad a excluir un instrumento:
56–67 % (sin SPY cae a 56 %, pero sigue > azar).

### Señal fuerte — el "80 % con convicción" (n=31)
| Agrupado por | Acierto | IC 95% | nº grupos |
|---|---:|:---:|---:|
| activo | 77.4 % | **[69.6–81.0]** | 4 |
| evento (fecha) | 77.4 % | **[59.3–91.7]** | 25 |
| período (año) | 77.4 % | **[54.5–92.3]** | 9 |

**Mucho menos seguro:** al contar la dependencia por evento o por período, el
intervalo **se ensancha enormemente** — el límite inferior cae de 69.6 % a
**54.5 %**. El "80 %" podría estar, en verdad, apenas por encima del azar.

## Qué significa

1. **La señal base de índice (~62 %) es un hallazgo sólido** — aguanta distintas
   formas de medir la incertidumbre.
2. **El "80 % con convicción" NO está establecido.** Su verdadera incertidumbre es
   grande (IC hasta [54.5–92.3] por período). No se puede comunicar como un número
   firme; es "prometedor pero sin confirmar", con n=31 y fuerte dependencia.
3. Esto confirma, con rigor estadístico, lo que ya sospechábamos: **la evidencia es
   estrecha.** La herramienta honesta a usar de aquí en adelante es la agrupación
   por evento/período (la más ancha), no por activo (la más optimista).

## Para comunicar

Nunca "80 % con convicción" a secas. Lo correcto: *"en la muestra, la señal fuerte
en índice acertó ~77 %, pero con un intervalo muy amplio (del orden de 55–92 %
según cómo se cuente la dependencia) sobre solo 31 casos — prometedor, pendiente de
confirmar con más datos prospectivos."*
