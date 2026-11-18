# Análisis en frío — Auditoría integral (18-11-2026)

*Rubicón Lab · El Enjambre · 2026-11-18. Evaluación independiente de la "Auditoría
integral, hallazgos y plan de implementación", verificada contra el código actual.*

## Veredicto: la mejor auditoría recibida, y es una validación cruzada

Es rigurosa y honesta: separa explícitamente "verificado en código / reportado /
hipótesis / propuesta", algo que ninguna anterior hizo. **No encontró bugs nuevos.**
Lo que hace es **confirmar de forma independiente** nuestros propios hallazgos
(contaminación, intervalos, aporte por arquetipo, el resultado negativo de la
confianza efectiva) y **refinar el plan** con disciplina metodológica. Que un
auditor externo llegue a las mismas conclusiones que nosotros es una señal fuerte
de que vamos bien encaminados.

## Verificación de sus afirmaciones de código (contra el repo de hoy)

| Punto de la auditoría | Estado real verificado |
|---|---|
| `calibrar_respaldo.py` usaba `y_te` (baseline ve el futuro) — "pendiente de comprobar" | ✅ **Ya corregido** (usa `y_tr`, línea 62). La auditoría vio el volcado del 17; se arregló el 18. |
| `walk_forward.py` baseline solo-train | ✅ Confirmado (`tasa_base(y_tr)`). |
| `promover()` produce optimismo de selección; producción debe usar anidado | ✅ `promover()` está solo en el `__main__` (CLI diagnóstico), no es ruta de producción. `promover_anidado` existe. *(Mejora menor pendiente: que el CLI imprima el veredicto anidado como autoritativo.)* |
| Cosechador con sesgo de selección | ✅ Ya medido/corregido (fuga) + re-medición sin fuga. Falta formalizar los 3 bancos. |
| Reparto comparte cerebros → no son opiniones independientes | ✅ Correcto y por diseño (presupuesto). |
| Confianza declarada no calibrada | ✅ Correcto; ya probamos que reponderar no mejora la dirección. |

**Conclusión:** sus observaciones de código o ya están resueltas o son de diseño
conocido. Su valor no está en encontrar fallos, sino en **subir el estándar del
plan**.

## Qué adoptamos de esta auditoría (refinamientos genuinamente valiosos)

1. **Contrato de evaluación (nuevo en Fase 0):** fijar ANTES de medir el horizonte
   exacto, la regla de subida/bajada/neutral, el precio de referencia, el trato de
   movimientos pequeños, sesiones cerradas y eventos solapados. Sin esto, cualquier
   cifra es frágil. **Alto valor.**
2. **Holdout congelado con hash + manifiesto + registro de cada evaluación.**
   Formaliza lo que teníamos como intención.
3. **Bootstrap multiway (evento × instrumento × período),** no solo por activo.
   Refina `intervalos.py`.
4. **Registro prospectivo YA (Fase 7 mínima en paralelo):** guardar cada predicción
   ANTES de conocer el resultado. **Es la joya del documento:** los datos
   prospectivos son inmunes a contaminación y selección, y empezar a acumularlos
   hoy es gratis y resuelve de raíz la duda del predictor. **Máxima prioridad nueva.**
5. **Baselines más fuertes en el A/B/C/D:** no solo la tasa base, también clase
   mayoritaria, momentum simple y un clasificador de sentimiento básico. Un baseline
   débil nos haría ver mejor de lo que somos.
6. **Fase 2 reenfocada:** la confianza efectiva como pregunta de CALIBRACIÓN (Brier),
   no de dirección; + abstención con curva riesgo-cobertura; + detector de consenso
   engañoso.
7. **Fase 1 (evidencia) con esquema JSON explícito y modo sombra** (producir la
   evidencia sin alterar las predicciones hasta medir que ayuda).
8. **Guía de comunicación:** cómo decir las cifras con honestidad (nunca "80%" sin
   cobertura, n, instrumento, período e intervalo). Clave para hablar con
   inversionistas.
9. **Artefactos operativos:** ficha de experimento, checklist, "regla de oro"
   (ninguna cifra sin denominador; ninguna predicción sin timestamp; ninguna
   promoción sin holdout; ninguna mejora sin comparación; ningún consenso sin medir
   su independencia).

Todo esto se integró en `plan-evolucion-enjambre.md` (v2).

## Lo único en que matizo a la auditoría

- La agrupación del bootstrap: la auditoría pide multiway; es correcto, pero con
  solo ~4 instrumentos de índice muy correlacionados, **ningún esquema de bootstrap
  arregla la falta de instrumentos independientes.** La solución real no es
  estadística sino de datos: más instrumentos y, sobre todo, **registro prospectivo**.
  Por eso priorizo la Fase 7 mínima por encima de refinar el bootstrap.
