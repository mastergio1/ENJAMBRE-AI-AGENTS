# La Redacción — propuesta de diseño

> **ESTADO: Fase 1 implementada** (commit de La Redacción). El análisis de
> mercado ya aparece en El Pulso, con datos que degradan a un snapshot de
> demostración hasta que se enchufe la clave de Barchart. El resto del
> documento es la especificación original.
>
> **Documento de propuesta.** Especifica cómo El Pulso
> (la newsletter) pasa de "así reaccionó el enjambre" a un **análisis de
> mercado con contexto real, investigado por agentes desde fuentes
> verificadas**. Para revisión de Giorgio antes de codificar. Si se
> aprueba, se resume como nueva sección de `CONTENIDO.md`.
>
> Decisiones ya tomadas: **mercado global** · capa de datos tipo
> **Barchart** (cifras) + **fuentes de economía** (relato).

---

## 1. La idea en una frase

Cada mañana, una pequeña redacción de agentes investiga qué pasó ayer en
el mercado global —desde fuentes verificables, con cita—, deja que el
enjambre reaccione a los titulares del día, y arma un correo editorial.
**La IA pone la voz; los datos ponen los números; nada se publica sin
fuente.**

## 2. La línea que NO se cruza (CMF Chile)

Investigar hace sólido el **pasado**; no habilita predecir el **futuro**.

- ✅ Permitido: *"El petróleo cerró +2%; la prensa lo atribuye a las
  tensiones en Ormuz."* (hecho pasado, con fuente)
- ✅ Permitido: *"Ante ese titular, en esta simulación educativa el
  enjambre se inclinó a la baja."* (nuestra simulación, etiquetada)
- ✅ Permitido: *"Hoy el enjambre está leyendo: la decisión de la Fed, los
  resultados de Nvidia."* (atención, no predicción)
- ❌ Prohibido: *"se espera que el petróleo suba hoy"*, *"el precio
  bajará"*, *"predicción"*, *"oportunidad de compra"*.

Cada frase generada pasa por el **filtro de vocabulario** (`vocabulario.py`,
ya existe como código con test). Una frase que no pasa, no sale.

## 3. La redacción — tres roles, una regla de oro cada uno

Encaja con la metáfora editorial de Rubicón Lab. Son agentes LLM con
herramientas (no "un modelo que escribe de memoria").

**1. El Reportero** — sale a las fuentes de la lista blanca, trae el
contenido **real** y extrae los hechos *con su cita (link + fecha)*.
> Regla: nada entra sin fuente.

**2. El Verificador (fact-checker)** — cruza cada número contra la capa de
**datos de mercado** (el % del petróleo lo saca de la API de precios, no
de un texto). Lo que no se puede verificar, se cae.
> Regla: el número manda sobre la narrativa.

**3. El Editor** — recién ahí redacta la prosa con la voz de El Enjambre y
pasa cada frase por el filtro CMF.
> Regla: la IA pone la voz; los datos ya pusieron los hechos.

Resultado: cada correo es **auditable**. Si alguien pregunta "¿de dónde
sacaron que el oro bajó?", hay un link.

## 4. Las fuentes — dos capas separadas a propósito

| Capa | Qué aporta | Candidatos | Uso |
|---|---|---|---|
| **Datos** (cifras) | precios, % de variación, históricos | **Barchart** (API de cotizaciones), Alpaca Market Data | El Verificador. **Los números salen SOLO de aquí.** |
| **Relato** (por qué) | titulares y contexto económico | Benzinga (vía Alpaca News), agencias/medios de economía de la lista blanca | El Reportero. Aporta la narrativa y la cita. |

**Lista blanca explícita**, no "internet abierto". Se define contigo como
director editorial y vive en configuración (se amplía sin tocar código).
Los endpoints y planes exactos de Barchart se confirman al integrar (tiene
tier gratuito y de pago; el gratuito puede bastar para el arranque).

**Selección dinámica (cada día es distinto).** El brief NO es una lista
fija. El universo del día se arma solo:
- **Telón de fondo** (siempre): índices y materias primas (S&P, Nasdaq,
  petróleo, oro) — el estado general del mercado.
- **Lo del día** (dinámico): los tickers que traen las noticias relevantes
  del día, según el **portero** (que ya evalúa ~100 titulares e identifica
  qué importa). Hoy puede ser Nvidia y el oro; mañana una adquisición, un
  banco, un sector — lo que el día traiga.

Y "lo que pasó" mezcla **dos tipos de hecho**:
- **Movimientos de precio** (con número verificado de la capa de datos).
- **Eventos** (adquisiciones, resultados, regulación): el hecho es la
  noticia con su fuente, sin número inventado.

## 5. La anatomía del correo (evolución de la sección 6.2 de CONTENIDO.md)

```
[Cabecera: El Enjambre · fecha]

LO QUE PASÓ AYER            ← investigado, con datos reales y citas
· Petróleo +2% · tensiones en Ormuz [fuente]
· Oro −1% · [contexto] [fuente]
· Nvidia +X% · anuncio de asociación con Y [fuente]

ASÍ REACCIONÓ EL ENJAMBRE   ← nuestra simulación, etiquetada
[imagen del momento dramático]
Ante [titular estrella], el enjambre simulado se inclinó a [▲▼◆].
«[voz del Doomer]» · «[voz del Institucional]»

QUÉ OBSERVA EL ENJAMBRE HOY ← atención, NO predicción
· [titular en el radar] · [titular] · [titular]

[CTA: ver el enjambre en vivo →]
[Disclaimer CMF · baja de un clic]
```

## 6. Dónde se enchufa (arquitectura)

- Nuevo paquete `engine/contenido/redaccion/` (reportero, verificador,
  editor) + `fuentes/barchart.py` (capa de datos).
- Se llama dentro del **ritual de la madrugada** (`pipeline.py`), justo
  antes de redactar el correo. Corre una vez al día.
- El resultado (el "brief del día": hechos + citas verificadas) se guarda
  en la base — se vuelve otro activo del archivo, auditable.

## 7. Presupuesto y red de seguridad

- **Costo LLM**: acotado. Una corrida de madrugada = unas pocas llamadas
  (reportero por instrumento en lote + editor). Mismo espíritu que el
  portero: si un diseño pide cientos de llamadas, se rediseña.
- **Humano en el lazo (al inicio)**: el correo queda como **borrador para
  tu visto bueno** con un clic antes de salir. Cuando confíes en la
  redacción, se pasa a automático. Ningún error llega a un suscriptor sin
  que un humano lo haya visto.
- **Degradación elegante**: si una fuente no responde, ese ítem se cae
  (nunca se inventa). Si se caen todas, el correo vuelve a la versión
  actual ("así reaccionó el enjambre"), sin bloque de mercado.

## 8. Qué necesito de Giorgio

1. **Cuenta de Barchart** (o la API de datos que prefieras) → claves.
2. La **lista blanca de fuentes de economía** que autorizas a citar.
3. Las de Alpaca (noticias + market data), pendientes desde antes.
4. Aprobar esta propuesta (o ajustarla) para plegarla a `CONTENIDO.md`.

## 9. Fases sugeridas

- **Fase 1** — El Verificador + Barchart: el bloque "Lo que pasó ayer" con
  cifras reales de índices/commodities/mega-caps. Sin relato aún.
- **Fase 2** — El Reportero: el "por qué" con citas de la lista blanca.
- **Fase 3** — Integración al correo + borrador para tu visto bueno.
- **Fase 4** — Automático, cuando la calidad esté probada.

---
*Rubicón Lab · El Enjambre · propuesta "La Redacción" · borrador para revisión*
