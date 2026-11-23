# Hallazgo CLAVE — ¿El enjambre le gana a un baseline tonto? (Fase 3/4 preview)

*Rubicón Lab · El Enjambre · 2026-11-23. La pregunta central de la auditoría: un
63% no dice nada si un modelo tonto también acierta 63%. Primera comparación
honesta, fuera de muestra, con el mismo resultado SIN FUGA. Herramienta:
`engine/calibration/baselines.py` (con tests). Sin IA nueva.*

## El experimento

165 casos de índice, split temporal 70/30 (train 115, test 50). En el test (38
casos direccionables) comparamos cuatro reglas contra el movimiento real:

| Regla | Acierto (test, fuera de muestra) |
|---|---:|
| **Mayoría** (predecir siempre "sube", lo más común) | **60.5 %** |
| **Momentum** (el movimiento previo continúa) | **63.2 %** |
| **Señal del enjambre** (dirección de los líderes) | **65.8 %** |
| **Precio simulado** (dirección del ABM de 10.150 agentes) | **55.3 %** |

*(n = 38 casos direccionables en el test.)*

## Qué significa, sin adornos

Esto es lo más importante que hemos medido, y es **honestamente incómodo**:

1. **La mayor parte del "63%" es simplemente que los índices suben más de lo que
   bajan.** Un modelo que predice "sube" siempre, sin leer nada, acierta **60.5%**.
   Eso NO es inteligencia del enjambre: es la tasa base del mercado.

2. **La señal del enjambre (65.8%) SÍ le gana a la mayoría, pero por poco:** +5.3
   puntos. Y a un momentum tonto (63.2%) le gana por solo +2.6 puntos. **Sobre 38
   casos, esa diferencia está dentro del ruido** — no es estadísticamente
   convincente todavía.

3. **El precio simulado del ABM (55.3%) es PEOR que la mayoría tonta.** Los 10.150
   agentes produciendo un precio no aportan dirección predictiva; si hay algo de
   valor, está en la **señal de los líderes LLM**, no en la simulación del
   mercado. (Confirma la sospecha P1-08 de la auditoría.)

## El veredicto honesto que esto obliga

> **La ventaja predictiva real del enjambre sobre un baseline razonable es pequeña
> y aún no está demostrada.** El grueso del acierto en índices es la tasa base
> ("los índices suben"). La señal LLM añade unos pocos puntos sobre un momentum
> simple, pero en esta muestra eso cabe dentro del margen de error.

Esto **no mata el proyecto**, pero **reescribe la historia honesta**:

- ❌ **No podemos decir** "El Enjambre predice el mercado al 63%". Sería engañoso:
  un modelo tonto hace 60.5%.
- ✅ **Sí podemos decir** "mide una señal direccional en índices que supera
  ligeramente a baselines simples, pendiente de confirmar con más datos."
- 🎯 **Refuerza dos prioridades:** (a) el **registro prospectivo** (ya corriendo),
  para ver con datos frescos si ese pequeño margen es real o ruido; y (b) la
  **capa de evidencia (Fase 1)** — si el titular pelado solo da +3 pts sobre
  momentum, la palanca es darle al enjambre MEJOR información, no más agentes.

## Salvedades

- n=38 en el test: los márgenes son pequeños y los intervalos de confianza se
  solapan. La lectura correcta es "no se demuestra ventaja fuerte", no "no hay
  ventaja". Hace falta más muestra (prospectiva) para concluir.
- La comparación es direccional; una ventaja podría existir en calidad de
  probabilidad (Brier) o en el subconjunto de alta convicción. Pero para el número
  que se comunica —acierto direccional— el enjambre apenas supera lo tonto.
- El momentum y la mayoría son baselines razonables, no deliberadamente débiles
  (como pide la auditoría). Si acaso, faltan baselines aún más fuertes
  (clasificador de sentimiento), que probablemente estrecharían más la brecha.
