# El Enjambre — Estado del proyecto

> Documento de contexto para Giorgio (Rubicón Lab).
> Escrito en lenguaje simple, sin tecnicismos. Fecha: **3 de agosto de 2026** (tarde).
> Este archivo es una foto de "cómo va todo" — no toca el código, solo lo explica.

---

## 1. Qué es El Enjambre (en una frase)

Un **simulador del mercado**: escribes una noticia (ej. *"la Fed sube las tasas"*) y ves,
en una escena 3D, cómo **10.000 inversionistas de mentira —hechos con inteligencia
artificial— reaccionan en vivo**: el pánico se contagia, se forman manadas, el precio
emerge solo. Al final entrega un reporte de qué pasó.

Es **"el focus group sintético del mercado"**: una herramienta de simulación y educación.
**Nunca da consejos de inversión** (regla legal de la CMF en Chile, respetada en todo el producto).

**Cliente:** empresas (fintechs, educación financiera, medios económicos, gestores).
**Diferenciador:** la visualización 3D del enjambre en tiempo real. Nadie más la tiene.

---

## 2. En qué punto estamos hoy

**El producto está vivo y funcionando en internet.** No es una maqueta: es un sistema real,
publicado, que cualquiera puede usar desde un link.

- 🌐 **La web (lo que ve el público):** https://enjambre-ai-agents.vercel.app
- ⚙️ **El motor (el cerebro que simula):** corriendo en un servidor 24/7.

Las etapas grandes del plan (0 a 10) **están completas**. Resumen de lo que ya existe y funciona:

| Pieza | Qué hace | Estado |
|---|---|---|
| **El motor** | Simula los 10.000 inversionistas y arma el precio | ✅ Funcionando |
| **El enjambre 3D** | La escena hipnótica que reacciona en vivo | ✅ Funcionando |
| **El muro** | La portada: las 3 noticias del día ya simuladas | ✅ Funcionando |
| **El Pulso** | La newsletter diaria por correo (ritual de madrugada) | ✅ Funcionando (Resend conectado y probado) |
| **El archivo** | La hemeroteca: todas las noticias pasadas, buscables | ✅ Funcionando |
| **La Redacción** | Análisis de mercado investigado y verificado para el Pulso | ✅ Funcionando |
| **El duelo** | Enfrenta dos escenarios lado a lado (+ export a video vertical) | ✅ Funcionando |
| **El widget** | Un recuadro embebible para que un medio lo ponga en sus notas | ✅ Funcionando |
| **Blindaje** | Protecciones contra abuso y ataques | ✅ Puesto |

---

## 3. La gran mejora en la que estamos ahora: la calibración

**El problema que fuimos a resolver.** El enjambre acertaba bastante bien la *dirección*
(si el precio sube o baja tras una noticia), pero se quedaba **corto en la fuerza**: cuando
el mercado real caía 10%, él apenas simulaba una caída de 3-4%. Reaccionaba, pero tímido.

**Qué hicimos.** Le ajustamos las "perillas" de cada mercado, porque no todos se mueven
igual: la **cripto** salta como resorte, las **acciones sueltas** se mueven fuerte, el **oro**
es más tranquilo (y hasta sube cuando hay miedo, porque es refugio), y los **índices tipo SPY**
son los más calmados. Antes el enjambre trataba a todos por igual; ahora distingue.

**Cómo lo comprobamos (el "examen general").** Le ponemos enfrente noticias reales del pasado
—de las que ya sabemos qué pasó de verdad con el precio— y comparamos su reacción contra la
realidad. Es como tomarle una prueba con las respuestas ya en la mano.

**Resultado de la re-validación (tanda de 110 exámenes, terminada el 3 de agosto):**
El problema de la fuerza quedó **en gran parte resuelto**. Comparación pareada (mismos 110
eventos, diales viejos vs. nuevos):

| | Antes | Ahora | Ideal |
|---|---|---|---|
| Fuerza del movimiento (mediana) | 2,4% | **8,2%** | ~real (8,0%) |
| Ratio de fuerza | 0,32 | **0,89** | 0,7–1,3 |
| Dirección (acierto) | 58% | 56% | ≥55% |

Por mercado: **Acciones** el mejor (dirección 56%→70%, fuerza 0,20→0,90); **Cripto** arreglado
(fuerza 0,20→0,80, dirección 59%→62%); **Oro** fuerza bien pero dirección floja (~50%, es el
más difícil por la lógica de refugio); **Petróleo** fuerza perfecta pero dirección bajó (muestra
chica); **Índices/SPY** ahora se pasa de fuerte (ratio 1,68, hay que bajarlo un toque).

**Decisión de foco del producto (3 de agosto):** concentrar El Enjambre en la **bolsa USA —
acciones individuales** (donde es más creíble y tiene mejores datos), con el **índice (SPY)**
como "ánimo general" y la **cripto** como extra opcional/viral. **Oro y petróleo** quedan a la
banca (experimentales) hasta que el núcleo esté sólido. La próxima tanda (con saldo nuevo, fin
de mes) irá **profunda solo en acciones USA**, mezclando días normales con días extremos —
vale más 500 exámenes sobre lo que importa que 100 sobre cinco mercados a medias.

**Nota de la prueba anterior (perillas viejas)** — para comparar:

| Mercado | Acertó la dirección | Fuerza |
|---|---|---|
| Metales (oro) | 51% | corta (~3-5% vs. 7-17% real) |
| Cripto | 59% | corta |
| Petróleo | 61% | corta |
| Índices (SPY) | 55% | corta |
| Acciones sueltas | 55% | corta |

Lo que esperamos ver con las perillas nuevas: que el acierto de dirección se mantenga o suba,
y sobre todo que **la fuerza deje de quedarse corta**.

---

## 4. Cómo está armado (para entender las piezas)

Piensa en el enjambre como una multitud de 10.000 personas, de dos clases:

- **1.000 "líderes de opinión"** — son los únicos que **leen la noticia de verdad**. Cada uno
  tiene una personalidad (el pesimista, el eufórico, el que va contra la corriente, el
  institucional frío…). Hay **8 personalidades** en total. Ellos opinan, y su opinión se
  **contagia** al resto. Son los puntos **dorados** de la escena; si pasas el cursor por uno,
  lees su frase (el momento mágico del demo).
- **9.000 "seguidores"** — no leen la noticia; **reaccionan al ambiente**: al precio, al miedo,
  a lo que hacen sus vecinos. Son la textura de la multitud.

**El truco de costo:** los 1.000 líderes no llaman uno a uno a la inteligencia artificial
(sería carísimo). Comparten ~110 "cerebros" repartidos por personalidad. Así el costo por
simulación se mantiene bajito (~$0,12 por simulación) pase lo que pase.

**De dónde salen las noticias reales para los exámenes:** un "cosechador" busca días de
movimientos grandes en el mercado real y sus titulares de esa fecha. **Nunca inventa
noticias** — solo usa hechos que de verdad ocurrieron.

---

## 5. Lo que resolvimos esta semana

- ✅ **Crecimos de 5.000 a 10.000 inversionistas** — un enjambre más impresionante y más
  estable, sin subir el costo.
- ✅ **El enjambre ahora distingue mercados** (cripto ≠ oro ≠ acciones ≠ índices).
- ✅ **Amenaza de Obsidian eliminada.** Un "ayudante" (plugin) de la app de notas Obsidian
  estaba, sin avisar, pisando el código del enjambre. Giorgio lo **eliminó del terminal**:
  problema resuelto de raíz, para siempre. Las notas que se alcanzaron a rescatar quedaron
  guardadas dentro del proyecto, en `docs/`. (Si algún día se quiere volver a usar Obsidian,
  se configura para que guarde en un cuaderno aparte, nunca encima del enjambre.)
- ✅ **Servidor mejorado** al plan pago con disco propio, para que las simulaciones queden
  guardadas y el motor aguante más.
- ✅ **El Pulso ya envía correos de verdad (Resend conectado).** Se creó la cuenta de Resend,
  se cargó la llave en el servidor y se blindó el remitente para que un deploy no lo rompa.
  Prueba completa exitosa: suscripción → correo de confirmación → llegó al Gmail → confirmado
  (el "double opt-in" completo). *Único pendiente cosmético: sin dominio propio el correo cae
  a la carpeta de spam; se cura al verificar un dominio (ver §6).*
- ✅ **Dirección web corregida.** `enjambre.vercel.app` quedó tomada por un proyecto ajeno;
  la web oficial y estable es ahora **enjambre-ai-agents.vercel.app** (todo el proyecto ya
  apunta ahí).

---

## 6. Lo que falta (pendientes)

**El Pulso — correos:** ✅ **Resuelto.** Resend está conectado y probado de punta a punta.
Faltan dos cosas menores para dejarlo "de producción":
- **Dominio propio** (ej. `rubiconlab.cl`): hoy el correo sale desde `onboarding@resend.dev`
  (remitente de prueba) y por eso cae a spam. Con un dominio verificado llega a la bandeja y
  además arregla la dirección web bonita — dos pájaros de un tiro (~US$10/año en nic.cl).
- **El "cron" del envío diario:** el reloj que dispara El Pulso cada madrugada. Se agrega
  cuando el dominio esté listo (bloque de referencia en `docs/despliegue.md`).

**Cuentas de datos con las llaves de Giorgio (para dejar todo "en producción real"):**
- **Alpaca** (titulares históricos) y **Barchart** (datos de mercado): hoy funcionan en modo
  demostración; con tus cuentas quedan con datos reales.

**Antes del lanzamiento público (blindaje final):**
- Bajar los topes de uso a lo normal (hoy están altos para poder calibrar).
- Regenerar llaves de seguridad y afinar la lista de dominios permitidos para el widget.

**Terminar la calibración:**
- Completar los exámenes de los 5 mercados. La meta de largo plazo es **100 exámenes por
  mercado**. El límite hoy es el saldo de inteligencia artificial (~US$21, alcanza para una
  buena tanda; recargando se completa).

---

## 7. Glosario rápido (para leer sin tropezar)

- **Agente / inversionista simulado** — una de las 10.000 personas de mentira del enjambre.
- **Líder de opinión** — de los 1.000 que sí leen la noticia y contagian al resto.
- **Señal** — la opinión de un líder convertida en número (de "vender fuerte" a "comprar fuerte").
- **Tick** — un "latido" del mercado: una ronda de decisiones.
- **Precio** — no se fija a mano; **emerge** de todas las compras y ventas juntas.
- **Perillas (diales)** — los ajustes que le dan a cada mercado su carácter propio.
- **Examen / calibración** — ponerle al enjambre noticias reales del pasado y comparar su
  reacción con lo que pasó de verdad.
- **Caja fuerte** — el respaldo en la nube donde se guarda cada examen a medida que avanza.
- **El motor** — el programa que hace la simulación (vive en el servidor).
- **La web** — lo que ve el público (vive en internet, se actualiza sola).

---

## 8. En una línea, para contarlo

> *El Enjambre está vivo en internet y funcionando de punta a punta. Esta semana lo hicimos
> más grande (10.000 inversionistas), le enseñamos a distinguir tipos de mercado, lo estamos
> afinando con exámenes contra la realidad, conectamos el correo de la newsletter (El Pulso ya
> envía de verdad) y eliminamos la única amenaza real que tenía. Falta el dominio propio, las
> cuentas de datos de Giorgio y terminar de afinarlo, para el lanzamiento público.*

---

## 9. Marca y dominio (decisión en curso)

**El nombre "El Enjambre" se mantiene.** Es un acierto: apuesta por el diferenciador (la
visualización del enjambre), es memorable y visual, y describe con precisión lo que hace
(comportamiento de manada). Su única limitación: por sí solo no dice "mercado", así que
**siempre debe ir con su bajada de línea** ("el focus group sintético del mercado"). Para
público internacional, la versión en inglés sería *The Swarm*.

**Se decidió comprar un dominio propio para El Enjambre como producto** (no el corporativo de
Rubicón). Rubicón queda como la firma ("by Rubicón Lab"). Un dominio propio le da cara pública
memorable, correos con identidad (`pulso@…`) e independencia como marca. Cuesta poco y de paso
resuelve dos cosas a la vez: el correo deja de caer a spam **y** la web tiene dirección corta.

**Lista corta de dominios a revisar** (verificar disponibilidad y precio en el registrador —
nic.cl para `.cl`; Namecheap o Cloudflare para el resto):

| Dominio | Terminación | Precio aprox./año | Para qué / pros |
|---|---|---|---|
| **elenjambre.cl** / **enjambre.cl** | `.cl` (Chile) | ~US$10 | Ancla local; confianza para clientes chilenos y contexto CMF. Barato. |
| **elenjambre.ai** / **enjambre.ai** | `.ai` | ~US$60–100 | Ángulo de inteligencia artificial (encaja: son agentes de IA). Moderno, caro. |
| **enjambre.market** | `.market` | ~US$25–35 | Se lee como frase ("enjambre · market"); temático y claro. |
| **elenjambre.com** | `.com` | ~US$12 | El estándar universal (`enjambre.com` casi seguro tomado; probar la variante). |
| **elenjambre.app** | `.app` | ~US$14 | Sensación de producto/herramienta; requiere HTTPS (ya lo tenemos). |

**Recomendación:** un dominio "de marca" como cara principal (**enjambre.market** o
**elenjambre.ai**, según si se quiere resaltar el mercado o la IA) **+** el **`.cl` barato** como
ancla local. Con ese dominio se verifica en Resend (correo a la bandeja, no a spam) y se apunta
la web para tener dirección corta.

---
*Rubicón Lab · El Enjambre · Estado del proyecto · 3 de agosto de 2026 (tarde)*
