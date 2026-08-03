# El Enjambre — Estado del proyecto

> Documento de contexto para Giorgio (Rubicón Lab).
> Escrito en lenguaje simple, sin tecnicismos. Fecha: **3 de agosto de 2026**.
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

- 🌐 **La web (lo que ve el público):** https://enjambre.vercel.app
- ⚙️ **El motor (el cerebro que simula):** corriendo en un servidor 24/7.

Las etapas grandes del plan (0 a 10) **están completas**. Resumen de lo que ya existe y funciona:

| Pieza | Qué hace | Estado |
|---|---|---|
| **El motor** | Simula los 10.000 inversionistas y arma el precio | ✅ Funcionando |
| **El enjambre 3D** | La escena hipnótica que reacciona en vivo | ✅ Funcionando |
| **El muro** | La portada: las 3 noticias del día ya simuladas | ✅ Funcionando |
| **El Pulso** | La newsletter diaria por correo (ritual de madrugada) | ✅ Lista (falta cuenta de correo, ver §6) |
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

**Estado ahora mismo:** re-validación en curso. Estamos rindiendo ~25 exámenes por mercado
sobre las perillas nuevas, para comparar antes vs. después. Cada examen queda guardado a
medida que avanza, así que aunque se corte, no se pierde nada.

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

---

## 6. Lo que falta (pendientes)

**Para que El Pulso (la newsletter) mande correos de verdad:**
- Giorgio debe crear una cuenta en **Resend** (el servicio que envía los correos) y pegar su
  clave en el servidor. Es un trámite de 10 minutos; te acompaño cuando quieras.

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
> afinando con exámenes contra la realidad, y eliminamos la única amenaza real que tenía.
> Falta conectar las cuentas de correo y datos de Giorgio, y terminar de afinarlo, para el
> lanzamiento público.*

---
*Rubicón Lab · El Enjambre · Estado del proyecto · 3 de agosto de 2026*
