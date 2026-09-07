# Informe FINAL — Analista de Riesgo Selectivo: 0 vs 0.5 vs 1.0 (muestras completas)

*Rubicón Lab · El Enjambre · 7 de septiembre de 2026*

> Para Giorgio, en simple: medimos al nuevo panelista (el **Analista de Riesgo
> Selectivo**) en tres intensidades —apagado (0), medio (0.5) y pleno (1.0)—
> sobre **todos** los exámenes históricos de cada mercado (índice completo,
> cripto completo, 220 casos), con la IA real. Este informe reemplaza al parcial
> anterior: con la muestra completa, la lectura de **cripto cambió**.

---

## 1. Resultados con muestra completa (acierto direccional)

### Índice (160 casos, mismos casos en los tres)

| Nivel | Negativas | Positivas | Global |
|---|---|---|---|
| **Base (0)** | 37.97 % (30/79) | 76.47 % (52/68) | 55.0 % |
| **0.5** | 43.04 % (34/79) | 73.53 % (50/68) | 57.5 % |
| **1.0** | **45.57 % (36/79)** | 73.53 % (50/68) | **58.1 %** |
| *Cambio 1.0 vs base* | **+7.6 pts** ✅ | −2.9 pts ⚠️ | +3.1 |

### Cripto (220 casos COMPLETOS, mismos casos en los tres)

| Nivel | Negativas | Positivas | Global |
|---|---|---|---|
| **Base (0)** | 51.69 % (46/89) | 86.26 % (113/131) | 72.3 % |
| **0.5** | 52.81 % (47/89) | 83.97 % (110/131) | 71.4 % |
| **1.0** | 51.69 % (46/89) | 85.50 % (112/131) | 71.8 % |
| *Cambio 1.0 vs base* | **0.0 pts** ✗ | −0.8 pts | −0.5 |

---

## 2. El hallazgo clave (y por qué la muestra completa importó)

**El Analista Selectivo ayuda en ÍNDICE, pero NO en cripto.** En cripto, con la
muestra completa (220), el doomer a pleno da **exactamente el mismo acierto en
negativas que la base** (46 de 89, idéntico) — cero mejora. El "+2.2" que
habíamos visto antes con 100 casos era un **espejismo de muestra chica**: al
completar los 220, el beneficio se evaporó. *(Coherente con el diseño: los
titulares de cripto muchas veces no gatillan el criterio de "deterioro claro",
así que el panelista se queda neutral y no cambia nada; y donde la noticia es
claramente mala, el Plan A ya toma la lectura fiel por su cuenta.)*

**En índice sí es un triunfo real:** +7.6 pts en negativas (de 38 % a 46 %), a
cambio de −2.9 en positivas. Neto claramente positivo (+3.1 global).

### ¿0.5 o 1.0?
En índice, **1.0 le gana a 0.5** (mismo costo en positivas −2.9, pero más
ganancia en negativas: +7.6 vs +5.1). En cripto ambos son ≈ neutros. **No hay
punto dulce en 0.5**: si se activa, conviene 1.0.

---

## 3. Veredicto honesto

El Analista Selectivo es una mejora **real pero ANGOSTA**: sirve para las malas
noticias de **índices bursátiles**, y no aporta nada en **cripto**. No es un
arreglo universal del sesgo alcista; es específico de índice.

- **Índice:** activarlo a 1.0 mejora el acierto en negativas de forma sólida
  (+7.6), con un costo pequeño en positivas (−2.9). Vale la pena.
- **Cripto:** activarlo no ayuda (0.0 en negativas) y roza las positivas hacia
  abajo. No vale la pena.

---

## 4. Recomendación (la mejor, no la barata)

**Activación segmentada por mercado: doomer ON en índice (1.0), OFF en cripto.**
Así se captura el triunfo real de índice sin arrastrar el costo inútil en
cripto. Es exactamente lo que la data pide.

Pasos:
1. **Hacer `peso_doomer` por-mercado** (como ya existe `FACTORES_LIQUIDEZ` por
   mercado): índice → 1.0, cripto → 0.0 (y evaluar los otros mercados —oro,
   petróleo, acción— con la misma vara antes de encenderlos). Cambio de código
   chico y limpio.
2. Dejar el flag global de rollback (`ENJAMBRE_PESO_DOOMER=0`) por si acaso.

**Alternativa simple** (si se prefiere no segmentar ahora): activar 1.0 global.
El neto entre los dos mercados es ~break-even (índice +3.1, cripto −0.5), así
que se gana en índice sin romper cripto — pero es subóptimo frente a segmentar.

**Si se prefiere no activar todavía:** el arquetipo queda dormido en producción
(como está hoy), sin costo, listo para encender cuando se decida.

---

## 5. Nota sobre el tiempo de medición (por qué tardó)

La lentitud NO fue el motor haciendo más trabajo por el doomer: medimos que una
simulación tarda ~5-6 s por caso **con cualquier `peso_doomer`**. La demora es
**infraestructura** — la latencia variable de la API de IA para los cerebros en
frío y el rendimiento variable de Render (plan Standard 2 GB con el modelo de
10.150 agentes). Algunas tandas corrieron en ~7 min y otras en ~20; el resultado
es el mismo, solo cambia el reloj.

*Costo LLM total de toda la medición (0/0.5/1.0 × índice/cripto completos):
dentro de lo autorizado; el grueso fue calentar los cerebros nuevos una vez.*
