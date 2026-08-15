# La edición de fin de semana de El Pulso

> La lectura pausada del sábado. Entre semana El Pulso cuenta las noticias del
> día; el fin de semana cambia de marcha y hace **un análisis a fondo de un solo
> protagonista**.

## Qué es

Dos formatos que se **turnan solos** semana a semana (par/impar de la semana del
calendario, así es reproducible):

1. **Acción seleccionada** — una empresa de **mediana capitalización, franja ~1 a
   20 mil millones de dólares** (foco de Giorgio). Se elige la que **más llamó la
   atención** esa semana (mayor movida de precio) que además esté **en banda**: la
   capitalización se verifica con el dato REAL de Yahoo; si el mayor movedor es más
   grande que ~20B, se baja al siguiente candidato en banda.
2. **Sector en rotación** — un sector que se está moviendo en bloque (energía,
   semiconductores, bancos regionales, biotecnología, utilities, oro). También se
   elige por atención.

## El formato del correo (en este orden)

1. **Qué es** — el CONTEXTO primero: a qué se dedica la empresa/sector, cómo gana
   dinero, qué lo hace particular. Se apoya en una descripción **factual y curada**
   (no la inventa la IA).
2. **Por qué está en la mira** — la movida de la semana y la narrativa alrededor.
3. **Gráfico real** — la curva de precio del mes del protagonista (desde Yahoo).
4. **Los números** — la ficha de **fundamentales VERIFICADOS** (capitalización,
   ingresos y su crecimiento, márgenes, EBITDA, deuda, caja), traída de Yahoo. La
   **tabla se dibuja desde los datos** (no desde el texto de la IA), atribuida a su
   fuente; debajo, la IA la explica en simple ("EBITDA = ganancias antes de
   intereses e impuestos", etc.). Si Yahoo no da la ficha (p. ej. un ETF), este
   bloque se omite entero. Aplica a la **acción seleccionada**, no a los sectores.
5. **Lo que ven nuestros inversionistas IA** — el **debate de arquetipos**: 4 a 6
   perfiles de inversionista con miradas que se **contradicen** entre sí. Ese
   choque es el corazón del análisis.
6. **Qué observar** — qué está en juego de aquí en adelante. Atención, no predicción.

## La regla de oro (marco CMF)

El encuadre que manda, en cada edición: **no es asesoría de inversión, es lo que
nuestros inversionistas IA están viendo y analizando.** Nunca se recomienda
comprar, vender ni mantener; nunca se predice el futuro; nunca se dice "le vemos
potencial". El "potencial" no lo pone el medio: lo ponen en tensión los
arquetipos, como miradas. Todo el texto pasa por el filtro `es_publicable` y el
correo lleva el disclaimer oficial.

## Cómo funciona por dentro

- `engine/contenido/config/universo_semanal.json` — el universo curado
  (acciones + sectores, cada uno con su contexto factual). **Aquí se crece la
  lista** sin tocar código.
- `engine/contenido/analisis_semanal.py` — selecciona el protagonista por atención
  (el número manda: la variación viene de Yahoo, gratis), lo filtra a la franja
  ~1-20B con la capitalización real, y adjunta sus fundamentales.
- `engine/contenido/fuentes/yahoo.py::fundamentales` — trae la ficha financiera
  verificada (usa el flujo cookie+crumb de Yahoo; degrada a None si falla).
- `engine/contenido/redaccion_ia.py::redactar_analisis` — le pone voz al deep-dive
  (contexto + lectura + debate + qué observar), con el `PROMPT_ANALISIS`. Un solo
  llamado LLM (respeta el presupuesto: el fin de semana **no** simula el enjambre).
- `engine/contenido/boletin.py::_bloque_analisis` — dibuja la edición en el correo.
- `engine/contenido/pipeline.py::ritual_matutino` — detecta que es fin de semana
  (hora local del lector) y arma el deep-dive en vez de la edición diaria.

## Cuándo se envía

El cron (`.github/workflows/ritual-diario.yml`) corre **de lunes a sábado** a las
6:00 de Chile. De lunes a viernes arma la edición diaria; el **sábado** arma la
edición de fin de semana. Como todas las ediciones, queda **pendiente de la
revisión de Giorgio** (correo de revisión + panel) antes de salir a los
suscriptores.

## En el panel

La edición de fin de semana aparece como cualquier otra, con su vista previa y los
botones **Aprobar / Descartar**. No trae el editor por campos (es otro formato):
se revisa en la vista previa y se aprueba o descarta.

## Degradación elegante

Si Yahoo no responde para ningún candidato, o si la IA no está disponible, el fin
de semana simplemente no arma edición (no se cae nada). En producción, con la
clave de Anthropic puesta, el sábado produce el deep-dive normalmente.

## Cómo crecer el universo

Editar `engine/contenido/config/universo_semanal.json`:
- **Acciones:** `{ "ticker", "nombre", "banda" ("1-15B" | "15-30B"), "sector", "contexto" }`.
  El `contexto` es la descripción factual (qué hace la empresa). La `banda` es solo
  un criterio interno de curaduría; **no se publica** como cifra exacta.
- **Sectores:** `{ "nombre", "etf", "en_rotacion_por", "contexto", "ejemplos" }`.

La única cifra que sale al correo es la **variación de precio real** (Yahoo) y los
puntos del gráfico. Nada de market cap, ingresos ni múltiplos inventados.
