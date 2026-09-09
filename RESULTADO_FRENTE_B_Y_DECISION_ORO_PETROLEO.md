# Frente B (cripto/acción) + Decisión sobre oro/petróleo

*Rubicón Lab · El Enjambre · 9 de septiembre de 2026*

> **Para Giorgio, en simple.** Dos cosas: (1) el resultado del Frente B —por qué el
> doomer fue inerte en cripto y acción, hecho **gratis** sobre los casos reales; y
> (2) mi recomendación honesta sobre si gastar ~$4-5 en medir oro y petróleo.

---

## PARTE A — Frente B: por qué el doomer es inerte en cripto y acción (gratis)

### Qué miré

Para las malas noticias que el enjambre **falla** en cada mercado (usando su
predicción ya guardada, sin re-simular), revisé una cosa: *¿el doomer siquiera se
dispararía ahí?* El doomer solo actúa ante negatividad **clara** en el texto
(puntaje ≤ −0.35).

### Los números

| | Cripto (41 fallos) | Acción (61 fallos) |
|---|---|---|
| **Doomer NO se activa** (no ve negatividad) | **78%** (32) | **89%** (54) |
| Doomer se dispara pero igual falla | 15% (6) | 7% (4) |
| Negativo leve (no alcanza el umbral) | 7% (3) | 5% (3) |

### La causa, en los propios titulares

Ejemplos reales de malas noticias que el enjambre falla:

| Titular | Palabras | Resultado real |
|---|---|---|
| "…Are Among Top 8 Mid-Cap **Gainers**…" | positivas | **−16.9%** |
| "Why Experts Are **Bullish** On Platinum…" | positivas | **−7.5%** |
| "Google's **Jaw-Dropping** Capex – AI Story Has More Gas" | positivas | **−4.5%** |
| "NVIDIA CEO Says AI's Future Isn't Just Copper" | neutrales | **−9.9%** |
| "Okta, Moderna and MicroStrategy Among Top 10 **Gainers**" | positivas | **−9.3%** |

**El hallazgo honesto:** en cripto y acción, el **80-90% de las malas noticias
tienen titulares neutrales o hasta positivos** ("gainers", "bullish",
"jaw-dropping"), pero el activo **igual cayó**. La dirección **NO está en las
palabras** — es reversión a la media, toma de ganancias tras una subida, rotación
de sector. Cosas que el titular no anuncia.

### Por qué esto explica TODO

1. **Por qué el doomer es inerte en cripto/acción:** solo se dispara ante
   negatividad clara, pero estos fallos **no tienen** negatividad en el texto —
   muchas veces tienen lo contrario. El doomer no tiene de qué agarrarse.
2. **Por qué un ensemble tampoco ayudaría:** misma razón — la señal **no está en
   el texto**. Ningún lector (léxico, LLM, FinBERT, ensemble) puede leer lo que no
   está escrito.
3. **Por qué índice SÍ funcionó:** sus titulares (Fed, tasas, inflación, recesión)
   **llevan la dirección en las palabras**. Por eso una corrección de sesgo sobre
   negatividad clara (el doomer) rinde ahí.

### El dato más brutal: acción está PEOR que una moneda al aire

Acción acierta solo el **20%** de las negativas — menos que el 50% del azar. Eso no
es "no puede saber": es que el enjambre está siendo **engañado por el marketing
positivo** de acciones que venían subiendo y luego se dan vuelta. Lee "gainers /
bullish / jaw-dropping", predice subida, **se come el hype y se quema**. Es un
sesgo alcista que, en nombres individuales con framing positivo, resulta
**anti-correlacionado** con lo que pasa después.

### Conclusión del Frente B

En cripto y acción, el techo desde el titular solo es **cercano a una moneda al
aire** (~50-55%), porque para la mayoría de sus malas noticias la dirección no está
escrita. **Ni el doomer ni un ensemble mueven eso.** El único mercado donde el
titular manda la dirección es índice — y ahí ya ganamos.

*(Nota: acción a 20% sugiere un patrón real —"el hype precede la caída" en nombres
individuales— pero explotarlo sería una señal de mercado especulativa y roza el
terreno de "predicción/consejo" que el filtro CMF prohíbe en el producto. Anotado
como curiosidad, no como acción inmediata.)*

---

## PARTE B — Decisión sobre oro y petróleo: NO gastar ahora

### Costo y tamaño

- Oro y petróleo **nunca** se calentaron en memoria → serían llamadas LLM reales.
- Son **13 casos de oro + 25 de petróleo** ≈ **$4-5** (la base gasta; el doomer=1
  después reusa memoria).

### Por qué NO lo recomiendo (aunque hay saldo)

1. **Oro es refugio: el doomer podría EMPEORARLO.** Una mala noticia (guerra,
   crisis) muchas veces **sube** el oro. El doomer, que lee la negatividad al pie
   de la letra, empujaría la predicción **hacia abajo** — justo al revés. Riesgo
   real de daño, no de mejora.
2. **Muestras diminutas:** oro tiene **7 negativas**, petróleo **11**. Con eso, un
   par de casos mueven el porcentaje entero. La respuesta sería **ruidosa**.
3. **Bajo prior de éxito:** el mapa ya es claro — el doomer funciona donde el
   titular lleva la dirección (índice), y eso no aplica a oro ni probablemente a
   petróleo.

**Recomendación:** guardar los $7.34. Gastar ~$4-5 en una medición que casi seguro
dirá "inerte o peor", sobre muestras demasiado chicas para confiar, no vale la
pena. Si algún día quieres cerrar el círculo por completeza, es barato y ahí está;
pero no lo pondría como prioridad.

### Parámetros correctos (por si decides hacerlo igual)

El plan original tenía la perilla equivocada. Lo correcto (como hicimos con
acción), por cada mercado:

- Base: `doomer=0`, `peso=-1`, `umbral=-1`, `mercado=oro` (o `petroleo`),
  `tamano=0`, `reiniciar=true`.
- Doomer encendido: igual pero `doomer=1`, `reiniciar=false`.

*(NO usar `peso` para prender/apagar el doomer: `peso` es el tono de invertidores,
otra cosa.)*

---

## Resumen de toda la investigación (el mapa completo)

| Mercado | ¿Titular lleva la dirección? | Doomer | Estado |
|---|---|---|---|
| **Índice** | Sí (Fed, tasas, inflación) | ✅ Ayuda +7.6 pts | Activo |
| **Cripto** | No (80% sin señal en el texto) | Inerte | Apagado |
| **Acción** | No (89% sin señal; hype→caída) | Inerte | Apagado |
| **Oro** | No (refugio: dirección invertida) | Prob. inerte o dañino | Apagado (no medir) |
| **Petróleo** | Mixto, muestra chica | Prob. inerte | Apagado (no medir) |

**La gran lección:** el sesgo alcista del enjambre solo se puede corregir con el
titular donde el titular **contiene** la dirección — y eso es, esencialmente, solo
índice (noticias macro). En nombres individuales y cripto, la dirección de corto
plazo no está en el texto, y **ningún lector de sentimiento la va a inventar.**

---

*Fin del documento.*
