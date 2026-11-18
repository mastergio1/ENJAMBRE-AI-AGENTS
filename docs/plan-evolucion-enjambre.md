# Plan de evolución de El Enjambre

*Rubicón Lab · El Enjambre · 2026-11-17. Hoja de ruta completa para evolucionar
el motor de un "experimento convincente" a un sistema predictivo **demostrable**.
Integra los hallazgos salvageables de las cuatro auditorías externas, nuestro
propio roadmap diferido (infraestructura, microestructura, modularización) y la
disciplina metodológica que lo hace ciencia y no teatro.*

---

## La estrella polar

> **No queremos que el Enjambre parezca más inteligente. Queremos demostrar, con
> resultados fuera de muestra, que realmente acierta más que un modelo simple.**

Todo en este plan se subordina a eso. Y hay una verdad incómoda que define la
prioridad: **hoy no sabemos con certeza cuánto de nuestro "~63% en índice" es
señal real y cuánto es memoria del modelo.** Hasta resolver eso (Fase 0), toda
mejora se construye sobre arena.

### Tres reglas de disciplina (no negociables)

1. **Medir antes de cambiar.** Ninguna mejora se promueve sin número.
2. **Una variable a la vez.** Si cambiamos cinco cosas y mejora, no sabemos cuál
   funcionó. Si empeora, tampoco.
3. **Holdout congelado.** Un conjunto de datos final que NUNCA se usa para
   ajustar nada. Es el juez. Si una mejora gana ahí, es real. Si solo gana en los
   datos con los que la afinamos, es autoengaño.

### Dos posibles verdades sobre el Enjambre (Fase 0 nos dice cuál)

- **Verdad A — "Predictor":** si la señal del enjambre aguanta en noticias que el
  modelo no pudo conocer, tenemos un sistema con valor predictivo real. El plan
  completo aplica.
- **Verdad B — "Simulador":** si el acierto se desploma sin la memoria del
  modelo, el valor defendible del Enjambre es ser **el focus group sintético**
  (simulación, visualización, educación — el posicionamiento de CLAUDE.md, que
  nunca fue "asesoría financiera"). Eso **también es un gran producto**, pero la
  historia y el pitch cambian.

**No sabremos cuál es la verdad hasta la Fase 0. Por eso es lo primero.**

---

## Dos vías en paralelo

- **Vía CIENCIA** (Fases 0→4 + 7): ¿el Enjambre aporta valor predictivo? Es la
  prioridad absoluta.
- **Vía INGENIERÍA** (Fases 5, 6, 8): robustez, escala y mantenibilidad. Puede
  avanzar en paralelo porque no depende de los resultados de la ciencia, pero no
  tiene sentido escalar algo cuyo valor aún no demostramos.

---

# VÍA CIENCIA

## FASE 0 — La verdad estadística *(fundacional · bloqueante)*

**Objetivo:** tener un número honesto en el que podamos confiar, por mercado, con
barras de error, congelado como punto de partida.

**Por qué importa:** es el cimiento. Sin esto, cada mejora posterior se mide
contra una referencia dudosa.

**Qué se hace:**
1. **Resolver la contaminación temporal (P4) — EL PRIMER EXPERIMENTO.**
   - Pasar la **fecha histórica** a los cerebros y restringir el contexto a "lo
     que se sabía en ese momento".
   - Correr el benchmark sobre **noticias recientes que el modelo no pudo
     conocer** (posteriores a su corte de conocimiento).
   - Comparar ese acierto con el histórico. La diferencia = cuánto venía de
     memoria.
2. Arreglo trivial del baseline (`calibrar_respaldo.py`: `y_te` → `y_tr`).
3. **Congelar un holdout final** que no se toca para ajustar nada.
4. **Tres bancos separados** (P3): ordinario / extraordinario / difícil, cada uno
   con su acierto, en vez de una cifra global dominada por extremos.
5. **Instrumentación por simulación:** % IA / % caché / % fallback / errores API /
   latencia p50-p95. Distingue "mal modelo" de "degradación técnica".
6. **Intervalos de confianza** por bootstrap agrupado por evento (no tratar diez
   noticias de la misma empresa como diez observaciones independientes).

**Entregable:** un informe de baseline honesto y congelado.
**Gate:** un número por mercado en el que confiamos, con incertidumbre explícita.
**Esfuerzo honesto:** 1-2 semanas de trabajo enfocado. **Alto valor de
información** (el experimento P4 puede redefinir la tesis entera del proyecto).

---

## FASE 1 — Mejores insumos: evidencia y validez temporal

**Objetivo:** que los agentes analicen con contexto, no un titular desnudo.

**Por qué importa:** el paper WorldReasoner (2026) concluye que recuperar
evidencia temporalmente válida es **uno de los factores más determinantes** de la
precisión. Un titular sin contexto es la mitad de la historia.

**Qué se hace:** un módulo "especialista en evidencia" que, antes de que opinen
los agentes, extraiga: qué pasó, qué activo, cuándo, qué es información nueva, qué
se esperaba antes, qué ya estaba descontado, qué fuentes lo confirman, y qué parte
es hecho vs. interpretación. Todo con timestamps verificables.

**Entregable:** un contexto estructurado que acompaña cada noticia.
**Gate:** mejora el acierto fuera de muestra vs. Fase 0.
**Esfuerzo honesto:** 2-3 semanas. Sustancial, pero probablemente el mayor salto
de calidad después de la Fase 0.

---

## FASE 2 — Mejor agregación: de consenso a predicción

> **⚠️ Aprendizaje (2026-11-18): la "confianza efectiva" para la DIRECCIÓN quedó
> DESCARTADA tras medirla.** Reponderar el consenso por el acierto histórico de
> cada arquetipo da el MISMO acierto direccional que la ponderada actual (0/37
> casos cambian de signo fuera de muestra): la mayoría de voces fija el signo y
> bajar el peso de las malas no lo voltea. Ver
> `docs/hallazgo-confianza-efectiva.md`. Conclusión: **el lastre está en los
> INSUMOS (Fase 1), no en los pesos.** Por eso la Fase 1 (evidencia) pasa a ser la
> palanca #1. De esta fase solo sobreviven las piezas que NO son reponderación de
> dirección: la separación consenso↔predicción (ya iniciada con el gating), la
> abstención, el detector de consenso engañoso, y —como pregunta abierta menor— si
> la confianza efectiva ayuda a la CALIBRACIÓN (Brier), no a la dirección.

**Objetivo:** dejar de confundir "lo que piensa el enjambre" con "lo que creemos
que pasará".

**Por qué importa:** hoy el consenso se pondera por la **confianza declarada** del
LLM — que no es su probabilidad real de acertar. Podemos estar amplificando el
error más convencido.

**Qué se hace:**
1. **Confianza efectiva (P2):** `C_efectiva = α·C_declarada + (1-α)·C_histórica`,
   donde la histórica se mide por arquetipo / mercado / tipo de noticia / régimen.
2. **Memoria de errores por arquetipo:** cada arquetipo lleva un historial de
   cuándo acierta y cuándo se equivoca.
3. **Separar consenso de predicción:** un motor que transforma el consenso en una
   probabilidad usando evidencia, régimen de mercado e historial. (Ya empezamos
   esto con el gating de convicción / Ventana A — esto lo lleva más lejos.)
4. **Abstención:** cuando la evidencia es insuficiente, el sistema puede decir "no
   predigo" en vez de inventar. (Métrica de cobertura.)
5. **Detector de consenso engañoso:** avisa cuando la unanimidad es sospechosa
   (p. ej. todos repiten el mismo cerebro, o la noticia ya estaba descontada).

**Entregable:** un agregador alternativo que compite contra el actual.
**Gate:** gana en Brier **y** en acierto direccional en el holdout congelado.
**Esfuerzo honesto:** 2-3 semanas.

---

## FASE 3 — Diversidad e independencia *(el experimento de P1)*

**Objetivo:** medir cuánta diversidad REALMENTE aporta información.

**Por qué importa:** la intuición "más agentes = mejor" hay que probarla, no
asumirla. Mi predicción en frío: rendimientos decrecientes rápidos, porque son el
mismo modelo con el mismo prompt. Pero hay que medirlo.

**Qué se hace:**
1. Medir la **correlación real** entre cerebros (¿qué tan parecidas son sus
   respuestas?).
2. Experimentar **110 / 220 / 400 cerebros** (ahora sí, sin tope de costo).
3. **Distribución adaptativa:** más cerebros a los arquetipos que demuestran
   capacidad predictiva, menos a los que repiten; más diversidad ante noticias
   ambiguas.
4. **Agentes detectores de error** (experimentales): abogado del diablo, detector
   de causalidad, detector de información descontada, verificador de fuentes. **No
   se les da influencia automáticamente** — primero se mide si mejoran la
   predicción.

**Entregable:** una curva de "cuánta diversidad aporta información".
**Gate:** ¿más diversidad mejora el holdout? Si no, no se promueve.
**Esfuerzo honesto:** 1-2 semanas (es sobre todo medición).

---

## FASE 4 — El experimento A/B/C/D *(la prueba de valor)*

**Objetivo:** demostrar, de una vez, si el enjambre vale más que un modelo simple.

**Qué se hace:** comparar cuatro sistemas sobre exactamente los mismos eventos y
el mismo holdout temporal, por mercado, con intervalos de confianza:

| | Sistema | Pregunta que responde |
|---|---|---|
| **A** | Baseline simple (tasa histórica de subidas/bajadas) | El piso a superar |
| **B** | Enjambre actual | ¿El enjambre aporta sobre el azar informado? |
| **C** | Enjambre optimizado (Fases 2-3) | ¿La mejor agregación funciona? |
| **D** | C + evidencia (Fase 1) | ¿La evidencia adicional aporta? |

**Regla de promoción:** B>A, C>B, D>C — cada uno **fuera de muestra**. El que
empeora, no se promueve.

**Entregable:** el veredicto honesto sobre el valor del Enjambre.
**Gate:** este experimento ES el gate de todo el proyecto.
**Esfuerzo honesto:** 1 semana (una vez que las fases anteriores existen).

---

## FASE 7 — Producción, monitoreo y aprendizaje continuo

*(numerada 7 porque cierra la vía ciencia, pero se construye junto a la Fase 5)*

**Objetivo:** que las mejoras sobrevivan en vivo y el sistema demuestre cuándo
mejora y cuándo empeora.

**Qué se hace:** registrar cada predicción **antes** de conocer su resultado;
tablero de rendimiento por horizonte y mercado; vigilancia de degradación;
rollback automático de experimentos; versionado de modelos y prompts.

**Entregable:** un Enjambre que se audita a sí mismo en producción.
**Gate:** podemos decir, cualquier día, "esta semana acertamos X ± Y".
**Esfuerzo honesto:** 2 semanas.

---

# VÍA INGENIERÍA *(puede avanzar en paralelo)*

## FASE 5 — Infraestructura durable *(nuestra Fase 1 diferida)*

**Objetivo:** que el motor aguante carga real y los rituales diarios no se caigan.

**Por qué importa:** hoy la simulación corre dentro del request web. Eso funciona
para un demo, no para muchos usuarios simultáneos ni para los procesos de
madrugada (El Pulso, La Redacción).

**Qué se hace:** cola durable + workers (sacar la simulación del request);
reintentos, idempotencia, backpressure; separar el motor de simulación del
servidor web para escalarlos por separado.

**Entregable:** el motor soporta N simulaciones concurrentes sin degradar.
**Gate:** prueba de carga superada.
**Esfuerzo honesto:** 2-3 semanas.

## FASE 6 — Microestructura y realismo *(nuestra Fase 3 diferida)*

**Objetivo:** profundizar el realismo del mercado simulado.

**Qué se hace:** más realismo en el libro de órdenes (impacto, profundidad,
latencia); afinar los hechos estilizados; medir contra microestructura real.

**Entregable:** una simulación aún más creíble para un ojo técnico.
**Esfuerzo honesto:** 2-4 semanas (es un pozo tan profundo como se quiera).

## FASE 8 — Modularización *(nuestra Fase 5 diferida)*

**Objetivo:** que el sistema sea mantenible y reutilizable en otros dominios de
predicción (no solo mercados).

**Qué se hace:** separar en módulos limpios con interfaces claras (motor,
cerebros, evidencia, agregación, evaluación).

**Entregable:** una arquitectura que otro equipo podría extender.
**Esfuerzo honesto:** 1-2 semanas, mejor hacerlo después de que la ciencia
estabilice las interfaces.

---

## Orden recomendado

```
AHORA ─► FASE 0 (la verdad) ──────────────────────────► decide la tesis
                 │
                 ├─► FASE 1 (evidencia) ─► FASE 2 (agregación) ─► FASE 3 (diversidad)
                 │                                   │
                 │                                   ▼
                 │                            FASE 4 (A/B/C/D) ─► veredicto
                 │
                 └─► (en paralelo) FASE 5 (infra) ─► FASE 7 (monitoreo)
                                   FASE 6 (microestructura)
                                   FASE 8 (modularización, al final)
```

**Si tuviera que elegir UNA sola cosa para empezar:** la Fase 0, y dentro de ella,
el experimento de contaminación temporal (P4). Es barato, es rápido, y su
resultado decide si el Enjambre es un "predictor" o un "simulador" — y eso cambia
todo lo demás.

## Una nota honesta sobre el esfuerzo y el dinero

Este plan completo es **varios meses** de trabajo enfocado. La buena noticia: casi
todo lo ejecuto yo (Claude) dirigido por ti; tu gasto principal es el costo de las
llamadas LLM de los experimentos (que ahora, sin el tope del presupuesto de demo,
podemos subir deliberadamente para las fases de medición). No necesitas un equipo
de ingenieros para avanzar — necesitas decidir el orden y financiar los
experimentos. Eso lo puedes hacer con tu plata, a tu ritmo, sin depender del
sábado.

**Y lo más importante:** si la Fase 0 dice "Verdad B" (es más simulador que
predictor), **eso no es un fracaso** — es claridad. El focus group sintético del
mercado, con esta visualización, es algo que nadie más tiene. Prefiero que sepas
la verdad y construyas sobre roca, a venderte un 90% que se evapore frente al
primer inversionista que sepa de estadística.
