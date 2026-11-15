# Plan — validar El Enjambre contra mercados de predicción (Polymarket / Kalshi)

*Rubicón Lab · El Enjambre · noviembre 2026*
*Adaptado de la propuesta externa, aterrizado a la arquitectura y los hallazgos reales.*

> **Para Giorgio, en simple.** Vamos a medir —con la vara más honesta que existe,
> los mercados de predicción ya resueltos— qué tan buena es la probabilidad que
> da El Enjambre, y a mejorar donde haya señal. El costo ya no es el freno. Pero
> hay **dos frenos que NO son plata** y que respetamos sí o sí: que el modelo de
> IA "sepa" resultados pasados (contaminación) y que con pocas preguntas no se
> pueda concluir nada (muestra). Este plan está diseñado alrededor de eso.

---

## 0. Qué ya sabemos (para no pagar por re-descubrirlo)

Medido en sesiones anteriores, con IA real:

- **Índice (macro):** la dirección está en el titular. Ventaja real: malas
  noticias 38% → **~58%**. Es nuestro gol.
- **Cripto y acción:** el 80-89% de las malas noticias **no tienen la dirección en
  el texto**. Acción está en ~20% (peor que el azar: se come el hype).
- **Oro/petróleo:** muestras diminutas (7 y 11 casos), decidido no medir.
- **Arquitectura real:** 10.150 agentes (9.000 de reglas + 1.150 líderes LLM que
  comparten ~110 cerebros), no "5.000 con 5% LLM". El plan se adapta a esto.

**Implicación:** el esfuerzo se concentra donde hay señal (**macro/índice**), y el
resto se mide solo para **confirmar el techo con la vara nueva**, no para rescatarlo.

---

## 1. Para qué sirve esto (y para qué NO)

**Valor esperado real** (en orden de probabilidad):
1. **Mapear con una vara de oro** dónde el enjambre aporta información y dónde no.
2. Una **salida en probabilidad calibrada** (más honesta y vendible que "% de dirección").
3. Un **producto de contenido transparente**: "Enjambre vs Mercado" en El Pulso.

**Lo que NO es:** una apuesta a "ganarle al mercado". Es poco probable y **no es
nuestro relato** — seguimos siendo simulador/focus-group/educación, no oráculo.
Este trabajo lo refuerza con evidencia, no lo contradice.

---

## 2. Reglas no negociables

1. **Licencia primero.** Verificar términos de Polymarket/Kalshi (mercados
   resueltos, historial de precios, uso comercial, almacenamiento) **antes** de
   construir. Veredicto en `docs/fuentes_datos.md`. La **validación interna** suele
   permitirse; el **producto** que republica precios es donde muerde el uso comercial.
2. **Cero look-ahead.** El enjambre solo ve titulares/datos con fecha < T.
3. **Ciego al resultado.** El código que corre el enjambre nunca ve el campo de
   resolución. Reutilizar el patrón de tipos de corrida (arnés vs calibración real).
4. **Nada inventado.** Dato que falta = hueco reportado, no relleno.
5. **Criterios de éxito congelados antes de correr** (§6).
6. **No es asesoría.** Disclaimer CMF en todo output público.

---

## 3. Los dos frenos que no son plata (y cómo los manejamos)

### Contaminación del modelo (riesgo de validez #1)
El LLM (claude-sonnet-5) **puede saber el resultado** de eventos pasados ya
resueltos. Controles:
- **Variante solo-reglas** (sin líderes LLM) como comparación limpia.
- **Separar resultados** por eventos anteriores vs posteriores al corte de
  conocimiento del modelo; marcar modelo y versión en cada corrida.
- **Preferir eventos posteriores al corte** (verdaderamente no vistos) — son
  pocos, así que se recolectan **en vivo** desde ya (ver §7).

### Muestra / potencia estadística (riesgo de validez #2)
Con pocas preguntas no se concluye nada (la trampa de oro/petróleo). Controles:
- Intervalos de confianza por **bootstrap** siempre.
- Meta de **50-100 preguntas**, con un **sub-set macro/índice** lo más grande
  posible (ahí está la señal). No concluir con n bajo por categoría.

---

## 4. Fases

**Fase 0 · Puerta de licencia + enganche (1 día).** Leer términos de Polymarket y
Kalshi; escribir `docs/fuentes_datos.md` (fecha, enlace, veredicto). Identificar
endpoints de mercados resueltos + historial de precios. Si nada permite el uso,
parar y replantear. *(La auditoría de arquitectura ya está hecha — se omite.)*

**Fase 1 · Set de preguntas (2-3 días).** Binarias, resueltas sin ambigüedad, con
precio en T reconstruible y titulares fechados antes de T. Priorizar **macro/índice**
(Fed, inflación, umbrales de índices). Guardar id, texto, apertura, T, precio en T,
resultado, fuente, fecha de descarga → `data/preguntas.jsonl`. División 60/20/20,
**prueba sellada intacta** hasta el final.

**Fase 2 · Adaptador señal→probabilidad (3-4 días).** Mapear la salida del enjambre
a P(sí) ∈ [0,1] (empezar simple: proporción ponderada de postura positiva),
función reemplazable. Capa de **calibración** (Platt/isotónica) ajustada **solo con
entrenamiento**. Varias semillas para medir la varianza del propio enjambre. Tests:
el adaptador nunca ve la resolución; ningún titular > T entra; reproducibilidad por semilla.

**Fase 3 · Backtest ciego (3-4 días).** Reconstruir titulares hasta T, correr el
enjambre, guardar la probabilidad. Correr **con y sin** líderes LLM. Registrar todo
en la libreta → `resultados/backtest_v1.json`.

**Fase 4 · Métricas y criterios (2 días).**
- Métricas: **Brier score**, log loss, **curva de confiabilidad**, IC por bootstrap.
- Líneas base: (1) 50% constante, (2) tasa base histórica, (3) **precio del mercado
  en T** (la más exigente).
- Skill score = 1 − (Brier enjambre / Brier base).
- **Criterios congelados:** *éxito mínimo* = supera líneas 1 y 2 con IC que no cruza
  cero; *éxito fuerte* = iguala/mejora el precio del mercado, o aporta combinado con
  él; *fracaso informativo* = no supera la tasa base → se documenta y se diagnostica.

**Fase 5 · Diagnóstico y mejora (continuo).** Un cambio a la vez, evaluando en
validación (nunca en la sellada): ablaciones (% LLM vs reglas, nº agentes,
líderes, ponderación por tipo), por categoría (macro vs cripto, corto vs largo),
prompts de líderes versionados, y **combinación con el mercado** (el enjambre como
ajuste sobre el precio, no sustituto). Al final, **una sola corrida** de la prueba
sellada con la mejor configuración.

**Fase 6 · Producto "Enjambre vs Mercado" (tras validar).** Sección diaria en El
Pulso: probabilidad del enjambre vs la del mercado y, al resolverse, quién acertó.
**Publicar el historial completo** (aciertos y errores) — eso construye credibilidad.
Disclaimer CMF siempre. Si **no hay señal**: reposicionar como simulación/escenarios,
sin vender predicción. *(Este producto vale aunque el enjambre no le gane al mercado:
su valor es transparencia y educación.)*

---

## 5. Estructura de repo

```
docs/  fuentes_datos.md · criterios_inclusion.md · criterios_exito.md
data/  preguntas.jsonl
src/   adaptador_prediccion/ · backtest_mercados/ · metricas/
resultados/  backtest_v1.json
tests/
```

---

## 6. Criterios de éxito (congelar antes de correr)

- **Éxito mínimo:** Brier del enjambre < líneas base 1 y 2, IC que no cruza cero.
- **Éxito fuerte:** iguala/mejora el precio del mercado, o lo mejora combinado.
- **Fracaso informativo:** no supera la tasa base → documentar, diagnosticar, y
  (probablemente) reposicionar esa categoría como simulación.
- **Prior honesto:** esperamos éxito **solo en macro/índice**; en cripto/acción,
  fracaso informativo que confirma el techo con la vara nueva.

---

## 7. Orden recomendado y primer paso

Fase 0 → 1 → 2 → 3 → 4 → (si hay señal) 5 → 6, con la puerta de criterios en cada salto.

**Empezar HOY, gratis y sin riesgo:**
1. **Chequeo de licencia** de Polymarket/Kalshi (Fase 0) — es la puerta.
2. **Recolectar en vivo** preguntas macro que se resolverán en el futuro
   (posteriores al corte de conocimiento del modelo) — es la muestra más limpia
   contra la contaminación, y empieza a juntarse desde ya mientras se arma el resto.

---

## 8. Riesgos

| Riesgo | Mitigación |
|---|---|
| Licencia no permite uso | Fase 0 bloqueante; plan B con otra fuente |
| Contaminación del LLM | Variante solo-reglas; separar por corte; preferir eventos futuros |
| Pocas preguntas | Bootstrap; no concluir con n bajo; priorizar macro |
| Sobreajuste al mejorar | Prueba sellada intacta hasta el final |
| Resultado negativo | Previsto como válido: mapea el techo y reposiciona |
| Output que parezca asesoría | Disclaimer CMF fijo; revisión antes de publicar |

---

*Fin. El costo ya no es el freno; los frenos reales son contaminación y muestra, y
el plan está construido alrededor de ellos. El relato se mantiene: simulador y
educación, no oráculo.*
