# Hallazgo — Los arquetipos SON diversos, pero en estilo, no en información. Fase 3.

*Rubicón Lab · El Enjambre · 2026-11-24. Fase 3 del plan maestro v5 (inteligencia
colectiva, T31: correlación de errores). Herramienta:
`engine/calibration/correlacion_cerebros.py` (con tests). Mide la diversidad REAL de
las 9 voces sobre el histórico. Sin IA.*

## Nota metodológica (buena ciencia: corregí un artefacto propio)

La primera versión midió la correlación del **error** `señal − y`. Dio ρ=0.89 (las
voces "se equivocan juntas"). **Era un artefacto:** todas las voces del mismo caso
comparten el mismo `y` (el resultado), lo que infla la correlación artificialmente —
hasta voces puramente al azar parecerían de acuerdo. La medida correcta es la
correlación de las **señales entre sí** (redundancia de información), que no tiene ese
sesgo. Un test (`test_voces_independientes…`) expuso el problema y se corrigió.

## Resultado (correlación de señales)

| Mercado | ρ media | Opiniones EFECTIVAS (de 9) |
|---|---:|---:|
| **ÍNDICE** | 0.065 | **5.91** |
| TODOS | 0.096 | 5.09 |

`N_efectivo = N / (1 + (N−1)·ρ)`. Con ρ≈0.07, las 9 voces equivalen a ~6 opiniones
independientes. **Los arquetipos SÍ son diversos** (dicen cosas bastante distintas).

## La paradoja (y su resolución honesta)

Si hay ~6 voces diversas, ¿por qué **un solo LLM iguala al consenso** (hallazgo A2≈A3)?

Porque la diversidad de los arquetipos es de **estilo/personalidad**, no de
**información**: los 9 leen **la misma noticia**. El optimista, el doomer, el quant…
reaccionan distinto al MISMO titular. Sus señales varían alrededor de una "lectura
central", y al promediarlas (el consenso) esa variación de personalidad se cancela y
**se recupera la lectura central** — que es exactamente lo que da un LLM neutral
leyendo el titular directo. Diversidad de voces, misma fuente de información.

## Qué significa

1. **El ensemble no falla por falta de diversidad** (la hay), sino porque la diversidad
   no aporta INFORMACIÓN nueva: una sola noticia → una sola señal de fondo.
2. Esto responde H3 de la auditoría con el mecanismo: para ganar con un ensemble harían
   falta voces con **fuentes de información DISTINTAS** (macro, fundamentales,
   microestructura, posicionamiento…), no 9 personalidades sobre el mismo titular. Es
   justo lo que propone la auditoría (§8.2, "especialistas") y queda como hipótesis a
   probar (necesita datos nuevos + la clave).
3. Confirma el valor de producto de los arquetipos (9 voces distintas para el hover y
   el enjambre) separado de su (nulo) valor predictivo incremental.

## Caveat

Exploratorio (banco histórico, índice n=142). Mide diversidad de señales, no prueba
causalidad. El N efectivo es una guía (fórmula de varianza con ρ media), no un test.
