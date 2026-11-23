# El Enjambre — Bitácora de la sesión del 23-nov-2026

*Rubicón Lab · Para Giorgio. Todo lo que hicimos hoy: el plan, las fases, cómo lo
hice, los hallazgos y lo que quedó en producción. En simple, sin jerga.*

---

## 0. Resumen en 30 segundos

Hoy dejé de "mejorar el enjambre a ciegas" y lo puse a prueba de verdad: construí
las herramientas honestas para medir **si el enjambre predice o solo parece que
predice**. El resultado es incómodo pero valiosísimo:

> **La simulación de 10.150 agentes NO mejora la predicción de dirección; la
> empeora. El poco acierto que existe vive en el consenso de los líderes LLM, solo
> en índices, y es apenas mejor que decir "los índices suelen subir".**

Con eso corregí el producto (que ya está en vivo) para no vender el enjambre como un
predictor, y dejé lista la última prueba (A2), que necesita que cargues una clave.

---

## 1. El plan que estamos siguiendo

Veníamos de 6 auditorías externas. La más rigurosa (la "v3") decía, en el fondo:
*"estás afinando perillas sin haber probado que el enjambre aporta algo sobre un
modelo tonto."* Le di la razón. El plan (en `docs/plan-evolucion-enjambre.md`) es una
escalera de fases para **demostrar valor predictivo real, no aparente**:

| Fase | Qué | Para qué |
|---|---|---|
| **0** | Cimientos estadísticos honestos | medir la incertidumbre sin engañarnos |
| **1** | Capa de evidencia *point-in-time* | darle a cada líder datos reales del momento, sin fugas del futuro |
| **3** | **Ablación A0–A5** | apagar cada capa y ver cuánto aporta de verdad |
| **4** | A/B/C/D pre-registrado | el veredicto final |
| **7** | Registro prospectivo | anotar predicciones ANTES del resultado (la prueba limpia) |

**Analogía:** antes estábamos tuneando el motor de un auto sin haberlo subido nunca a
una pista con cronómetro. Hoy construí el cronómetro y lo subí a la pista.

---

## 2. Lo que hice hoy, fase por fase

Orden cronológico real (cada línea es un punto de guardado en el repositorio):

### Mañana — cerrar la Fase 1 y arreglar deudas

1. **Analicé en frío la auditoría v3** (la más dura) contra el código real. Confirmé
   sus críticas donde tenía razón y descarté donde no.
2. **Arreglé 4 bugs del registro prospectivo** que la auditoría encontró: una
   predicción que se guardaba en silencio y solo con el primer ticker; otra que nunca
   se resolvía si la noticia caía un fin de semana; un conteo truncado; y una
   actualización no atómica. *(Cómo: reescribí cada función y le puse un test que
   impide que el bug vuelva.)*
3. **Adopté el plan v3** y repartí los carriles: yo hago ciencia/ablación/registro;
   Codex hace la parte de identidad macro (sus PRs #34/#35, que revisé: buenos y
   complementarios).
4. **Fase 1 — capa de evidencia** (dos puntos de guardado): cada líder puede recibir
   contexto **real** del precio en el momento de la noticia (retorno previo,
   volatilidad, distancia al máximo), **sin ver nada publicado después** de la fecha
   de la noticia (la regla sagrada anti-fuga). Va en "modo sombra": se calcula y se
   guarda, sin cambiar aún las predicciones. **Verificado en producción.**

### Tarde/noche — Fase 0 (cimientos) y Fase 3 (la autopsia)

5. **Fase 0.4 — Holdout congelado.** Un "juez" protegido: separo los casos más nuevos
   como examen final, le saco una huella digital (hash) y la congelo. Si alguien
   cambia una etiqueta o se pierde un caso, el hash deja de cuadrar y salta la alarma.
   *Sirve para que nunca nos hagamos trampa midiendo sobre datos que tocamos.*
6. **Fase 0.5 — Bootstrap multiway.** La "prueba de honestidad" del margen de error
   (ver §3).
7. **Fase 3 — Ablación A0–A5.** La autopsia: apagar cada capa y medir (ver §3). **El
   hallazgo central del día.**
8. **A2 — un solo LLM.** Dejé listo el runner (ver §4).
9. **Corrección de producto.** Separé en el sitio "lo que simuló el enjambre" de "la
   lectura" honesta (ver §5).

### Cómo trabajo (para que sepas qué garantías tienes)

- **Nada se declara "listo" sin evidencia:** cada herramienta trae sus tests y los
  corrí. Hoy terminamos con **468 tests en verde, 0 fallos**.
- **Cada avance es un punto de guardado** en el repositorio, con mensaje en español.
- **No toco producción sin la suite completa en verde.** Hoy esperé los 24 minutos
  que tarda y recién entonces desplegué.
- **No invento resultados.** Donde faltaba la clave de IA (A2), lo dejé pendiente en
  vez de rellenar con números falsos.

---

## 3. Los hallazgos (los números honestos)

### Hallazgo central: el enjambre no predice mejor que el consenso

La ablación apaga capas y mide el acierto de **dirección** (¿sube o baja?) sobre datos
limpios, sin fuga. De lo más tonto a lo más complejo:

| Capa | Qué es | Acierto en ÍNDICE (fuera de muestra) |
|---|---|---:|
| **A0** | piso tonto: "los índices suelen subir" | 62.8 % |
| **A1** | léxico: contar palabras del titular (sin IA) | ~59 % |
| **A3** | **consenso de los ~110 cerebros LLM** (sin simular) | **65.1 %** |
| **A4** | **el enjambre completo de 10.150 agentes** | **53.5 %** |

**Las dos verdades duras:**

1. **El enjambre completo (A4) es el PEOR.** Cuando la simulación se atreve a
   contradecir al consenso de los líderes (21 veces en índice), **acierta 6 y falla
   15**. La simulación agrega ruido, no señal. El valor predictivo vive en lo que
   dicen los líderes (A3), no en el enjambre de partículas.
2. **Ese valor es frágil.** El consenso (65 %) apenas le gana al piso tonto (63 %).
   Con pocos casos, **todavía no podemos afirmar que de verdad le gane.** Fuera de
   índices (cripto, oro, petróleo, acciones) **todo es moneda al aire (~50 %).**

**Analogía:** montamos una orquesta de 10.000 músicos (el enjambre), pero quien afina
es el director leyendo la partitura (los líderes); la orquesta entera, al tocar,
**desafina el resultado del director.** El espectáculo es real. La predicción no sale
de la orquesta. → `docs/hallazgo-ablacion.md`

### Hallazgo de apoyo: el "80 % con convicción" era menos seguro de lo que parecía

Antes decíamos "~80 % con convicción fuerte en índices". El bootstrap multiway mostró
que ese número, bien medido (contando que 4 ETFs el mismo día no son 4 experimentos
independientes), tiene un margen de error **enorme**: el intervalo pasa de [69.6–81.0]
a **[54.5–92.3]**. O sea, el 80 % **no está probado**; podría estar apenas sobre el
azar. La señal base (~62 %) sí aguanta. → `docs/hallazgo-bootstrap-multiway.md`

### Adelanto gratis de A2 (con datos ya recolectados)

En índice, **una sola voz** (el influencer optimista) ya acierta 64.1 %, **igual que
el consenso de las 110 (62.7 %)**. Señal de que la diversidad de 110 cerebros quizá
**no compra acierto** — lo confirma el A2 definitivo (pendiente de la clave).

---

## 4. A2 — listo para correr, bloqueado por una clave

Construí `un_llm.py`: hace **una** lectura LLM neutral por titular (sin personalidad,
sin enjambre) y la compara contra el consenso. Si empatan, el reparto de 110 cerebros
es **gasto evitable** para la dirección. Está testeado y corre en un comando.

**Por qué no lo corrí hoy:** esta sesión no puede recibir la clave de Anthropic (es un
host propio de Anthropic; no se puede inyectar por el proxy). **Necesito que la cargues
tú** (ver §7).

---

## 5. La corrección de producto (ya en vivo)

**Problema:** el sitio mostraba como "dirección esperada" el **precio simulado del
enjambre (A4)** — justo el peor predictor.

**Lo que hice (la opción más honesta):** separé dos cosas que antes se mezclaban:
- **"+3 % simulado"** → el movimiento que simuló el enjambre (la animación). Es verdad
  y se queda, pero **ya no se presenta como la predicción**.
- **"lectura ▲ alza"** → una insignia aparte con la dirección del **consenso de
  líderes (A3)**, que aparece **solo cuando es fiable** (índice + convicción fuerte).

Así no vendemos el enjambre como predictor ni sobre-afirmamos ante la CMF.

---

## 6. Qué quedó en producción (verificado)

| | Estado |
|---|---|
| Motor (Render) | versión `fe3415992eb4` · campo `lectura` sirviéndose en la API |
| Frontend (Vercel) | HTTP 200 · el bundle en vivo ya trae "lectura" y "simulado" |
| Suite de tests | **468 passed, 0 fallos** |
| Evidencia Fase 1 | activa en modo sombra, verificada antes |

---

## 7. Lo que necesito de ti (2 cosas; ninguna la puedo hacer yo)

1. 🔑 **Cargar `ANTHROPIC_API_KEY`** como variable de entorno del entorno de nube
   (barra de título → entorno de nube → *Edit* → variable de entorno) y **abrir una
   sesión nueva**. Esta sesión no la verá; la toma una nueva. Con eso corro el **A2
   definitivo** en un comando.
2. 🔑 **Rotar `ENJAMBRE_PIPELINE_TOKEN`** (lo pegaste por error en el chat): Render →
   Environment → regenerar, y actualizar el mismo secreto en GitHub.

---

## 8. Próximos pasos (cuando quieras)

- **A2 definitivo** (apenas cargues la clave): ¿un LLM empata al consenso de 110?
- **A5**: ¿la capa de evidencia mueve la aguja?
- **Más casos prospectivos** (Fase 7): la única forma de angostar los márgenes y pasar
  de "indicio" a "prueba".
- **Confiabilidad del ritual**: el cron de la mañana no siempre dispara (Fase 5).

---

## 9. Mapa: dónde está cada cosa

| Archivo | Qué |
|---|---|
| `docs/plan-evolucion-enjambre.md` | el plan completo con todas las fases |
| `docs/hallazgo-ablacion.md` | **el hallazgo central**: el ABM no predice mejor |
| `docs/hallazgo-bootstrap-multiway.md` | el 80 % es menos seguro de lo que parecía |
| `docs/hallazgo-baselines.md` | ¿el enjambre le gana a un modelo tonto? (preview) |
| `engine/calibration/ablacion.py` | la ablación A0–A5 (con tests) |
| `engine/calibration/un_llm.py` | A2: un LLM neutral, listo para correr |
| `engine/calibration/intervalos_multiway.py` | el bootstrap honesto |
| `engine/calibration/holdout.py` | el "juez" congelado |
| `engine/server.py` (`_lectura_tarjeta`) | la corrección de producto |

*Commits de hoy: `f2e8ee8` → `fe34159` (13 puntos de guardado).*
