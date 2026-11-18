# Hallazgo — La confianza efectiva NO mejora la dirección (Fase 2)

*Rubicón Lab · El Enjambre · 2026-11-18. Prueba fuera de muestra de la idea
estrella de la auditoría para la Fase 2: reponderar el consenso por el acierto
HISTÓRICO de cada arquetipo en vez de por la confianza que DECLARA el LLM.
Herramienta: `engine/calibration/confianza_efectiva.py` (con tests). Sin IA nueva.
Resultado negativo, y es valioso: nos ahorra invertir donde no mueve la aguja.*

## El experimento (honesto, fuera de muestra)

163 casos de índice con señal, ordenados por fecha. Split temporal 70/30:
train = 114 casos (hasta 2022-11), test = 49 casos (desde 2022-11). Los pesos por
arquetipo se estiman SOLO en train (acierto histórico) y se evalúan en test.

Pesos efectivos aprendidos en train (premian solo a los que superan el azar):

| Arquetipo | Acierto train | Peso efectivo |
|---|---:|---:|
| influencer_optimista | 66.3 % | 0.163 |
| macro_trader | 64.4 % | 0.144 |
| fomo_evangelista | 62.7 % | 0.127 |
| institucional_frio | 60.2 % | 0.102 |
| contrarian_sabio | 55.6 % | 0.056 |
| quant_esceptico | 55.4 % | 0.054 |
| **doomer** | **33.7 %** | **0.000** |
| value_paciente | 50.0 % | 0.000 |

## El resultado — TEST (fuera de muestra, índice, n=37 direccionables)

| Esquema de agregación | Acierto direccional |
|---|---:|
| Promedio simple (flat) | **64.9 %** |
| Ponderada ACTUAL (producción) | **64.9 %** |
| Efectiva (peso por acierto histórico) | **64.9 %** |

**Idénticos.** Y al investigar por qué: en los 37 casos de test los arquetipos
discrepan de signo entre sí en **37/37**, pero **ningún esquema de peso cambia el
signo del agregado (0/37)** — ni quitando al doomer, ni elevando los pesos al
cuadrado.

## Qué significa (y por qué redirige el plan)

**Para la DIRECCIÓN, la forma de agregar es irrelevante.** El signo del consenso
lo fija la mayoría de voces; el doomer y los contrarians son minoría, así que
bajarles el peso (o anularlos) no voltea el resultado. El acierto se queda en
~64-65 % hagas lo que hagas. Reponderar por acierto histórico —la idea estrella de
la Fase 2— **no mejora la dirección.**

Esto **ahorra** semanas de trabajo en una palanca que no servía, y **redirige**
el esfuerzo:

- ❌ **Fase 2 (confianza efectiva para dirección): descartada.** No invertir ahí.
- ✅ **El lastre está en los INSUMOS, no en los pesos.** La palanca real es la
  **Fase 1 (capa de evidencia)**: darle a los agentes contexto, fecha, expectativa
  previa y qué ya estaba descontado. Si mejoramos lo que LEEN, mejora la
  dirección; reordenar cómo los sumamos, no.
- ✅ **Más instrumentos/datos** (la salvedad de los ~4 activos sigue siendo el
  límite honesto de todo).

## Salvedades honestas

- Es sobre **DIRECCIÓN**. La confianza efectiva **todavía podría ayudar a la
  CALIBRACIÓN** (calidad de la probabilidad / Brier) — o sea, a decir *cuán*
  seguros estamos, no a acertar más veces. Eso no se midió aquí y queda como
  pregunta abierta menor. Pero para el número que importa (acierto direccional),
  es un no.
- n=37 en test es chico; el resultado es robusto porque es **0/37 cambios de
  signo** (no es cuestión de potencia estadística, es estructural: la mayoría
  manda).
- El gating de convicción (Ventana A) ya cumple mejor el rol de "cuándo confiar"
  que lo que haría una reponderación.
