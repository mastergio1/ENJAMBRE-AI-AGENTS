# Plan paso a paso — próximos pasos de El Enjambre

*Rubicón Lab · El Enjambre · Armado el 2026-09-27, para ejecutar cuando entre capital*

> **Para Giorgio, en simple.** Este es el orden que vamos a seguir. La idea guía:
> **lo gratis primero, luego lo barato y seguro, y al final lo grande e incierto.**
> El dinero es el recurso escaso; mi tiempo de desarrollo es gratis para ti, así
> que las cosas que solo cuestan trabajo no se saltan la fila.

---

## Orden recomendado (resumen)

| Fase | Qué | ¿Cuesta plata? | Por qué en este orden |
|---|---|---|---|
| **0** | Cerrar cabos sueltos (las 2 observaciones) | $0 | Limpiar antes de gastar |
| **1** | **Calibrar oro y petróleo** | ~$10 | Barato, finito, cierra el libro; medir va antes que construir |
| **2** | Features de MiroFish baratas | ~$0 build | Se hacen con mi tiempo, no con tu saldo |
| **3** | Experimento de **memoria** | medio (con tope) | Lo más grande e incierto: al final y con freno |

---

## FASE 0 — Gratis, ya (no espera capital)

**Objetivo:** dejar todo prolijo antes de gastar un peso.

1. **Manada — redacción del reporte.** Cambiar solo el texto "0 compras" por algo
   como *"la manada vendió en cascada; recompra casi nula, típico del pánico"*.
   (Ya medido: no es bug, es realista; el problema era solo de óptica.)
   → *Necesita tu OK.*
2. **FOMO — suavizar frases vs. CMF.** Ajustar frases de respaldo **y** la
   instrucción del arquetipo: de "TÚ compra/vende YA" a "YO, el personaje, opino".
   Mantener el tono viral y los emojis. → *Necesita tu OK.*
3. **Verificar tests en verde** (hechos estilizados 9/9, `test_config_enchufado`,
   seguridad) tras los cambios.

- **Costo IA:** $0. **Hecho cuando:** cambios commiteados y tests verdes.

---

## FASE 1 — Primer capital (~$10): cerrar la calibración

**Objetivo:** medir el "Analista de Riesgo" (peso_doomer) en los 2 mercados que
faltan y dejar la calibración cerrada al 100%.

1. **Giorgio recarga saldo** en Anthropic (a fin de mes).
2. **Verificar saldo** y que la medición corra **100% con IA** (`sin_ia = 0`);
   si cae al respaldo léxico, se contamina — no se mide sin saldo.
3. **Medir ORO:** base (`peso_doomer=0`) → calienta la caché → pleno (`1.0`) casi
   gratis (reusa caché). Muestra **completa**.
   - ⚠️ **Ojo especial:** el oro es **refugio** — puede SUBIR con malas noticias.
     Es posible que el doomer lo **empeore**, o que el oro pida lógica propia.
     Medir **sin prejuicio**; que los números manden (ya me equivoqué con acción).
4. **Medir PETRÓLEO:** mismo procedimiento.
5. **Decidir por evidencia:** fijar `peso_doomer_por_mercado.oro` y `.petroleo`
   en `engine/config/agentes.json` según lo medido.
6. **Actualizar** `ESTADO_CALIBRACION.md` + informe; confirmar botones de reversa
   (`ENJAMBRE_PESO_DOOMER=0` apaga todo).

- **Costo IA:** ~$10 (con el truco de caché). **Hecho cuando:** oro y petróleo
  medidos, config actualizada, informe al día.

---

## FASE 2 — Dev gratis: features de MiroFish baratas

**Objetivo:** sumar valor de producto sin gastar tu saldo. Se construyen con mi
tiempo; el runtime consume muy poca IA y bajo demanda. Orden según lo que más te
ilusione mostrar/vender.

1. **⭐ Entrevistar a un líder** — clic en un líder → conversas con él ("¿por qué
   reaccionaste así?"). Efecto-wow alto; extiende el hover que ya existe.
2. **Semilla en PDF** — el cliente sube un informe/noticia y se simula, en vez de
   teclear el titular. Usa librerías de terceros con licencia limpia (PyMuPDF).
3. **Reportes plan-y-llena** en La Redacción — planear el índice y llenar por
   trozos: menos fallas, más control.

- **Costo:** ~$0 para construir; runtime bajo. **Hecho cuando:** cada feature
  probada en vivo. **Legal:** todo con código propio; nada del código AGPL de MiroFish.

---

## FASE 3 — Capital con tope estricto: experimento de memoria

**Objetivo:** medir de verdad si darle memoria a los agentes mejora algo. Va al
final porque es lo más grande y lo más incierto.

1. **Armar RAG local ligero** (sin Zep, para no romper el costo): del titular
   sacar entidades de mercado (ticker, sector, macro) y traer del banco de **652
   casos** los más parecidos, como contexto para los líderes.
2. **Precomputar embeddings** una sola vez (costo mínimo).
3. **Medir con la vara honesta:** base (sin memoria) vs. con-memoria, muestra
   completa, 100% con IA, empezando por **índice**.
4. **Separar dos métricas:** *acierto* (¿mejora la dirección?) y *realismo*
   (¿opiniones más ricas?). No confundirlas.
5. **Decidir por evidencia:** si mejora el acierto, productizar; si solo suma
   realismo, evaluar si vale el costo extra por simulación.

- **Tope de presupuesto:** fijar un máximo de dólares ANTES de empezar; si se
  alcanza, **parar y evaluar** (nada de cheque en blanco, como sí hace MiroFish).
- **Costo:** medio, con freno. **Hecho cuando:** informe de memoria con veredicto
  **medido**, no supuesto.

---

## Reglas que no cambian (recordatorio)

- **Medir, no adivinar.** Si una corazonada mía choca con los números, ganan los números.
- **Disciplina de costo.** Todo con tope; el respaldo léxico nunca contamina una medición.
- **CMF.** Todo el contenido sigue siendo "educativo, no asesoría financiera".
- **Una sesión, una misión.** No saltamos de fase sin cerrar la anterior.

---

*Fin del plan. Es una hoja de ruta viva: se ajusta según lo que la data y Giorgio
decidan en cada fase.*
