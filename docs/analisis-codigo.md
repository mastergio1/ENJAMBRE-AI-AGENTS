# Análisis de código — El Enjambre (seguridad, bugs y carga)

> Revisión a nivel de código: bugs, inyecciones y qué pasa bajo carga masiva.
> Fecha: 3 de agosto de 2026. Alcance: `engine/server.py`, `seguridad.py`,
> `limites.py`, `brains/cerebro.py`, `persistencia.py`, frontend `web/src`.

---

## Veredicto general: **sólido, con posturas de seguridad maduras**

Esto no es código de aficionado. Tiene defensas pensadas a conciencia:
consultas SQL parametrizadas, validación de identificadores, escape de XSS en
el frontend, comparación de tokens en tiempo constante, rate-limiting por IP,
semáforos de concurrencia y tope de presupuesto. La mayoría de proyectos en su
etapa **no** tienen esto. Lo que sigue son afinaciones, no incendios.

---

## 1. La pregunta grande: ¿y si 5.000–10.000 personas piden una simulación a la vez?

**Respuesta corta: el motor NO se derrite ni gasta una fortuna.** Está diseñado
para servir de a poco y rechazar el resto con cortesía. Hay **4 murallas en fila**:

| Muralla | Dónde | Qué hace ante la avalancha |
|---|---|---|
| Rate-limit por IP | `seguridad.permitir_http` | 120 req/min por IP en `/api/*`; el exceso recibe 429 |
| **Semáforo de simulaciones** | `server.py` `MAX_SIM_CONCURRENTES=2` | **Solo 2 simulaciones corren a la vez; las otras 9.998 reciben "El enjambre está ocupado" al instante** |
| Tope de presupuesto | `limites.permitir` | Tope por IP (3/hora) y **tope global diario** (`ENJAMBRE_MAX_SIM_DIA`). Al agotarse, invita a suscribirse |
| Concurrencia LLM interna | `cerebro.MAX_CONCURRENTES=45` | Dentro de una simulación, las ~108 llamadas van de a 45 |

**Qué pasa concretamente con 10.000 golpes simultáneos:**
- Solo **2** simulaciones se ejecutan; el resto ve "ocupado" en milisegundos.
- El gasto está **acotado por el tope diario** — no hay forma de que 10.000
  personas gasten 10.000 simulaciones.
- La IA nunca tumba nada: si Anthropic responde 429 (límite de tasa), cada líder
  **cae al respaldo léxico** y la simulación sigue (`cerebro._consultar_lider`).

**En una frase:** aunque llegue una turba, el enjambre atiende a dos, le dice
"ya vuelvo" al resto, y la billetera está tapada. Buen diseño.

### Pero — los límites reales (honestidad)

1. 🔴 **Una sola instancia es el techo.** Correr 2 simulaciones de 10.000
   agentes en 0,5 CPU / 512 MB está **al borde** — ya vimos reinicios por
   memoria con UNA sola. Bajo carga real, `MAX_SIM_CONCURRENTES=2` podría
   desbordar. En el plan actual, **1 sería más seguro** que 2.
2. 🔴 **10.000 WebSockets no caben.** El instante no sostiene 10.000 conexiones
   vivas; más allá de unos cientos, las conexiones fallan (no es un crash, pero
   es mala experiencia a escala masiva).
3. 🟠 **El tope de gasto vive en memoria** (`limites._consumidas_hoy`) → **se
   reinicia en cada deploy o reinicio.** Como Render reinicia (memoria, deploys),
   el contador diario vuelve a 0, y el tope "500/día" podría superarse a lo largo
   de varios reinicios. *La billetera está protegida, pero con una fuga.*
4. 🟠 **No escala horizontal sin romper el tope.** Si algún día se ponen 2
   instancias, cada una lleva su propio contador en memoria → el tope global se
   duplicaría. Para escalar de verdad, el rate-limit/presupuesto tendría que
   vivir en un lugar compartido (Redis o la propia base).

---

## 2. Inyecciones de datos

| Vector | Estado | Detalle |
|---|---|---|
| **SQL injection** | ✅ Protegido | Todo con consultas parametrizadas (`?`). Los f-strings solo arman fragmentos internos (nombres de columna, cláusulas), nunca valores del usuario. |
| **XSS (script en un titular)** | ✅ Protegido | El frontend escapa titulares y frases del LLM antes de `innerHTML` (`muro.js:85`, `panel.js:6/112`, `widget.js`). Comentarios en el código muestran que lo pensaron a propósito. |
| **Path traversal** (`/replay`, `/imagen`) | ✅ Protegido | El `sim_id` se valida como hex de 16 (`seguridad.sim_id_valido`) ANTES de tocar disco o base. |
| **Endpoints de admin** | ✅ Protegido | Token comparado en tiempo constante (`hmac.compare_digest`), y **falla cerrado**: sin token configurado, nadie pasa. |
| **Prompt injection** (titular → prompt del LLM) | 🟠 Bajo riesgo | El titular entra al prompt (`cerebro.py:100`). Un usuario podría intentar "jailbreak" para forzar una señal o frase. **Impacto acotado:** la salida se valida y recorta (señal a [-1,1], frase a 160 chars), y solo afecta LA simulación de ese usuario. |

**Único matiz del prompt injection:** una `frase` "jailbreakeada" podría colar
lenguaje que el filtro CMF prohíbe (ej. "compra esto ya"). El filtro
`es_publicable` se aplica al epílogo y al brief, **pero no a las frases del
LLM**. Probabilidad baja, pero es un borde de cumplimiento CMF a cerrar antes
de abrir al público (pasar las frases por el mismo filtro).

---

## 3. Bugs y fallas reales encontradas (priorizadas)

| # | Severidad | Qué | Dónde | Arreglo |
|---|---|---|---|---|
| 1 | 🔴 Media-alta | Tope de gasto en memoria se reinicia con cada deploy → se puede exceder el tope diario a lo largo de reinicios | `limites.py` | Persistir el contador (una fila en SQLite con la fecha) |
| 2 | 🔴 Media | `MAX_SIM_CONCURRENTES=2` puede desbordar 512 MB (evidencia: OOM con 1 sim + calibración) | `server.py:44` | Bajar a **1** en el plan actual, o subir la RAM |
| 3 | 🟠 Media-baja | Carrera al escribir el caché: 2 simulaciones leen-modifican-escriben el mismo JSON → se pierden entradas (auto-sana, pero real) | `cerebro.py:117-151` | Escritura atómica (archivo temporal + rename) o candado |
| 4 | 🟠 Baja | Frases del LLM no pasan por el filtro CMF | `cerebro.py` + `vocabulario.es_publicable` | Filtrar la `frase` antes de mostrarla/guardarla |
| 5 | 🟡 Baja | Bajo carga sostenida, muchos líderes caen al respaldo léxico (429 de Anthropic) sin avisar → calidad degrada en silencio | `cerebro.py` | Ya hay log de la primera falla; bastaría exponerlo en `/api/estado` |
| 6 | 🟡 Info | Escalar a 2+ instancias rompería el tope global (estado en memoria) | `limites.py`, `seguridad.py` | Mover estado a Redis/DB si algún día se escala |

**Nada de esto es un incendio hoy** (en pruebas privadas, con el candado
`ENJAMBRE_ACCESO` puesto, casi nadie llega a gastar IA). Son la lista de
"antes de abrir al público de verdad".

---

## 4. Recomendación priorizada para el lanzamiento público

1. **Persistir el tope de gasto** (bug #1) — es la única fuga de billetera real.
2. **`MAX_SIM_CONCURRENTES=1`** mientras siga en 512 MB (bug #2) — mata los OOM.
3. **Filtrar las frases del LLM por CMF** (bug #4) — cierre de cumplimiento.
4. Escritura atómica del caché (bug #3) — pulido.
5. Si algún día hay tráfico serio: subir RAM/CPU y mover el rate-limit a un
   almacén compartido (bugs #2 y #6).

---

*Rubicón Lab · El Enjambre · Análisis de código · 3 de agosto de 2026*
