# Aprendizajes de MiroFish — qué nos podemos quedar

*Rubicón Lab · El Enjambre · Análisis del repo `666ghj/MiroFish` (75k★) · 2026-09-27*

> **Para Giorgio, en simple.** Miré el código de MiroFish con mente abierta,
> buscando problemas que ellos ya resolvieron y que a nosotros nos sirven. Esto
> NO es copiar su idea ni su código: es ver qué **herramientas de terceros** y qué
> **patrones** podemos adoptar por nuestra cuenta. Abajo está el filtro honesto:
> qué sí, qué no, y con cuánto esfuerzo.

---

## 0. La línea legal (leer primero)

MiroFish está bajo licencia **AGPL-3.0** (copyleft fuerte). Eso significa:

- ❌ **NO** copiamos sus archivos de código a El Enjambre. Si lo hiciéramos, nos
  obligaría a **abrir todo nuestro producto** y regalar el código a cualquiera que
  lo use por internet. Veneno para un producto B2B que queremos vender.
- ✅ **SÍ** podemos: (a) usar las **mismas herramientas de terceros** que ellos usan
  —cada una tiene su propia licencia, independiente de la de MiroFish—, y (b)
  aprender **ideas y patrones** conocidos (reintentos, "planificar y luego llenar",
  RAG, entrevistar a un agente). Las ideas no son de nadie; el código sí.

**Regla de oro:** herramientas de terceros y patrones, sí. Sus archivos, no.

---

## 1. Qué es MiroFish vs. qué somos nosotros (recordatorio)

| | MiroFish 🐟 | El Enjambre 🐝 |
|---|---|---|
| Qué simula | Opinión / redes sociales | **Mercado con precio real (libro de órdenes)** |
| Motor | OASIS (CAMEL-AI) | Mesa + libro de órdenes propio |
| Memoria | Zep Cloud (pago) | (pendiente — experimento con tope) |
| Visual | Dashboard 2D | **Enjambre 3D en vivo** |
| Validación | Ninguna publicada | **Hechos estilizados con tests** |
| Costo IA | "Alto consumo", sin revelar | **~$0,12/sim, 110 cerebros compartidos** |
| Licencia | AGPL-3.0 | Nuestra |

**Conclusión:** no competimos en tamaño; ganamos en foco (mercados reales + 3D +
honestidad + costo). Ellos igual resolvieron problemas de "plomería" que a
nosotros nos sirven.

---

## 2. Lo que SÍ nos quedamos (candidatos, ordenados por valor)

### 🥇 A. "Entrevistar a un agente" después de la simulación
- **Dónde lo vi:** `report_agent.py` tiene una herramienta `InterviewResult` — el
  reporte puede *entrevistar a un agente individual* y también conversar con el
  usuario llamando herramientas de búsqueda (patrón ReAct).
- **Cómo lo usamos:** hoy ya mostramos la `frase` de un líder al pasar el mouse.
  El siguiente paso natural: **clic en un líder → conversa con él**, pregúntale
  "¿por qué reaccionaste así?". Efecto-wow alto, encaja con lo que ya tenemos.
- **Esfuerzo:** medio. **Costo IA:** bajo (una charla corta, bajo demanda).
- **Veredicto:** ⭐ el mejor candidato. Reimplementable con nuestro propio código.

### 🥈 B. Semilla = subir un PDF / noticia (no solo escribir el titular)
- **Dónde lo vi:** `utils/file_parser.py` usa **PyMuPDF** (PDF) + **charset-normalizer/chardet**
  (detección de codificación con varios niveles de respaldo) para leer archivos
  desordenados sin romperse.
- **Cómo lo usamos:** dejar que el usuario **suelte un informe/noticia en PDF** como
  semilla de la simulación, en vez de teclear el titular a mano. Más pro, más B2B.
- **Legal:** PyMuPDF y charset-normalizer son librerías de terceros con su propia
  licencia — las usamos directo, nada que ver con la AGPL de MiroFish.
- **Esfuerzo:** bajo-medio. **Veredicto:** ✅ práctico y limpio.

### 🥉 C. "Planificar y luego llenar" + generación por pasos (para La Redacción)
- **Dónde lo vi:** `report_agent.py` **planifica primero el índice** y luego genera
  sección por sección; `simulation_config_generator.py` genera **por pasos** para
  "evitar que una salida muy larga falle".
- **Cómo lo usamos:** hacer los reportes de **La Redacción** más robustos: planear
  la estructura y llenarla en trozos, en vez de pedir todo de una (menos fallas,
  más control).
- **Esfuerzo:** bajo (es cambiar cómo pedimos, no el motor). **Veredicto:** ✅ mejora de calidad.

### D. Noticia → mini-mapa de entidades (la versión estructurada de "memoria")
- **Dónde lo vi:** `ontology_generator.py` saca **tipos de entidades y relaciones**
  del texto; `graph_builder.py` arma un grafo de conocimiento; luego se usa para
  dar contexto a los agentes.
- **Cómo lo usamos:** es la versión "con esteroides" de la **memoria** que te
  interesa. Para nosotros, LIGERO: sacar del titular las **entidades de mercado**
  (tickers, sector, variable macro) y metérselas como contexto a los líderes.
  **SIN Zep** (hacemos RAG local barato) para no romper la disciplina de costo.
- **Esfuerzo:** medio-alto. **Veredicto:** 🔬 alimenta directamente el experimento
  de memoria que ya teníamos en fila. Medir con tope, no cheque en blanco.

### E. Patrones sueltos, baratos
- **Reintentos con retroceso exponencial + jitter** (`utils/retry.py`): patrón
  idiomático para llamadas a la IA. Nosotros ya tenemos *fallback*; esto lo
  complementa. Lo escribimos nosotros en 20 líneas.
- **Instrucción de idioma inyectada en cada prompt** (`utils/locale.py`): truco
  limpio para forzar que la IA responda en español consistente.
- **Perfil de actividad por hora del día** (madrugada/mañana/trabajo/peak/noche
  en `simulation_config_generator.py`): da realismo a *cuándo* actúan los agentes.
  Menor para nosotros (somos por "ticks", no por reloj), pero anotado.

---

## 3. Lo que NO nos sirve (y por qué)

- **Zep Cloud** (memoria administrada de pago): rompe nuestra disciplina de costo.
  Hacemos memoria local/barata en su lugar.
- **Capa de compatibilidad OpenAI** (`openai_chat_compat.py`): somos nativos de
  Anthropic (Claude) y queremos seguir así. No metemos atajos de OpenAI.
- **Motor OASIS** (CAMEL-AI): simula redes sociales, **no forma precio**. Nuestro
  motor (Mesa + libro de órdenes) es más correcto para mercados. Bueno saber que
  existe; no lo adoptamos.
- **"Predecir cualquier cosa":** su posicionamiento es humo sin accuracy. Nosotros
  somos honestos y medimos. No lo copiamos.

---

## 4. Resumen ejecutivo

MiroFish **valida que el concepto vende** (75k estrellas) y nos deja 3-4 piezas de
plomería útiles, todas reimplementables con código propio o con librerías de
terceros de licencia limpia:

1. **Entrevistar a un líder** (wow barato). ⭐
2. **Subir PDF/noticia como semilla** (más B2B).
3. **Reportes plan-y-llena** (más robustos).
4. **Memoria estructurada ligera** (alimenta el experimento ya planeado).

Nada de esto toca su código AGPL. Nuestra ventaja de fondo —mercado real con
precio, 3D, validación y costo bajo— sigue intacta y es lo que nos diferencia.

---

*Fin. Este documento es de referencia; ninguna de estas ideas está implementada
todavía — son candidatas para cuando Giorgio las priorice.*
