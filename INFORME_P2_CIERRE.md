# Cierre de P2: la muestra completa lo refuta — la perilla se queda en 1.0

**Fecha:** 6 de septiembre de 2026
**Medición:** con el LLM real en Render, sobre los **163 exámenes de índice** (81 negativas, 69 positivas, 13 neutras), comparando la MISMA muestra y semillas con la perilla en tres posiciones: 1.0 (actual), 0.3 (P2 suave) y 0.0 (P2 pleno).
**Veredicto de una línea:** **P2 no sirve.** En la muestra completa no gana ni un solo acierto en negativas y sí resta en positivas, en cualquier nivel de la perilla. Se archiva. La perilla se queda en **1.0** (como ya está en producción).

---

## 1. La historia honesta de este experimento

Este informe **corrige** a `INFORME_P2_HALLAZGO.md`. Aquella medición, con muestras chicas (18 + 24 negativas), mostró a P2 subiendo el acierto en negativas +11 y +12 puntos, sin costo. Se veía excelente. **Era ruido de muestra pequeña.**

Al cerrar la muestra completa del índice (163 exámenes en vez de 40), la ventaja se desinfló hasta desaparecer. Es el ejemplo de libro de por qué no se decide con muestras chicas: el primer puñado de casos puede mentir con total convicción.

## 2. La foto completa — índice, 163 exámenes

| Perilla | Negativas (81) | Positivas (69) | Global (163) |
|---|---|---|---|
| **1.0** — actual (P2 apagado) | **44/81 = 54.3%** | **50/69 = 72.5%** | **102/163 = 62.6%** |
| **0.3** — P2 suave | 44/81 = 54.3% | 48/69 = 69.6% | 99/163 = 60.7% |
| **0.0** — P2 pleno | 45/81 = 55.6% | 46/69 = 66.7% | 97/163 = 59.5% |

**Lectura:**
- **Negativas:** mover la perilla no aporta nada. En 0.3 son **exactamente los mismos 44 aciertos** que la base. En 0.0 sube un solo caso (45). Cero mejora real.
- **Positivas:** cada paso hacia P2 **resta**: 72.5% → 69.6% → 66.7%.
- **Global:** baja monótonamente: 62.6% → 60.7% → 59.5%.

P2 es una palanca que **solo tiene lado malo** a escala completa.

## 3. Cómo se desinfló la ilusión (peso 0.3, acumulado por tanda)

| Casos acumulados | Negativas | Positivas |
|---|---|---|
| 40 | 15/24 = **62.5%** | 9/13 = 69.2% |
| 80 | 25/46 = 54.3% | 17/25 = 68.0% |
| 120 | 34/62 = 54.8% | 30/47 = 63.8% |
| 160 | 42/79 = 53.2% | 47/68 = 69.1% |
| **163 (final)** | **44/81 = 54.3%** | **48/69 = 69.6%** |

Los primeros 40 casos daban 62.5% en negativas (la "buena señal" del informe anterior). Conforme entraron los 163, se hundió a 54.3% — el número de la base. La ventaja nunca fue de P2; fue del azar de qué casos entraron primero.

## 4. Por qué el mecanismo no ayudaba (en simple)

P2 sacaba a tres tipos de líder (el contrarian, el quant escéptico y el optimista) de "poner el clima" del mercado, con la idea de que así el enjambre no diluyera las malas noticias. La teoría era buena. Pero en la práctica:

- Esos líderes **no eran** la causa de que el enjambre acierte poco en negativas. Quitarlos del clima no movió la aguja de las negativas.
- Sí aportaban al clima de las **positivas** (donde el enjambre ya iba bien, 72.5%). Silenciarlos ahí solo hizo perder aciertos buenos.

En resumen: apagamos algo que ayudaba en un lado sin arreglar nada en el otro.

## 5. Decisión

1. **P2 se archiva.** No se activa en ningún nivel.
2. **La perilla se queda en 1.0**, que es el valor por defecto en producción. **No hay que revertir nada** — P2 nunca cambió el comportamiento en vivo (la variable `ENJAMBRE_PESO_TONO_INVERSORES` nunca se fijó en Render). El código sigue ahí, inerte y reversible, por si un rediseño futuro lo aprovecha.
3. **No se gasta más saldo en P2.** La medición de cripto a escala completa (~$39) que estaba sobre la mesa ya no se justifica: el mecanismo quedó refutado en el mercado que más importaba.

## 6. Qué aprendimos que sí vale

- **El diagnóstico de causa raíz sigue en pie:** el enjambre es demasiado optimista en negativas (predice subidas donde el mercado cayó). P2 apuntaba a la capa correcta (el tono), pero la palanca elegida no era la que mueve esa capa.
- **La infraestructura de medición quedó construida y probada:** exámenes reales con LLM, resumible, tolerante a reinicios de memoria, con caché caliente que hace gratis las nuevas barridas de perilla. Cualquier próxima idea se mide igual, sin volver a pagar los cerebros.
- **La disciplina de muestra completa nos ahorró un error caro:** activar P2 con la señal de 40 casos habría metido una regresión (−3 pts en positivas) creyendo que mejorábamos.

## 7. Estado de producción

- `main`: P2 presente, perilla en **1.0** → cero cambio de comportamiento. Sin acción pendiente.
- El respaldo histórico y el comportamiento en vivo **nunca se tocaron** en todo el experimento.

---

*Medición: workflow "Evaluar acierto (P2)" → `/api/evaluar` (Render, LLM real), barrido de perilla sobre caché caliente.
Antecedentes: `INFORME_P2_HALLAZGO.md` (señal de muestra chica, aquí corregida), `INFORME_P2_MEDICION.md` (sistema y arreglos), `INFORME_CAUSA_RAIZ_NEGATIVAS.md` (diagnóstico). Cómo medir: `docs/medir-p2.md`.*
