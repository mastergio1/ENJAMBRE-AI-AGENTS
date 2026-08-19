# Revisión de código — el freemium (PR #22 + #23)

> Revisión del 19 de agosto de 2026 sobre los dos últimos cambios fusionados: el
> paso a **1 simulación gratis al día** y **40 al mes para Premium**.
> Archivos mirados: `engine/contenido/limites.py`, `engine/contenido/persistencia.py`,
> `engine/server.py`, `web/src/ui/premium.js`, `web/pulso/*`, `render.yaml`.
>
> **Nada de esto está arreglado todavía** — este documento es el diagnóstico.
> Cada punto trae *qué encontré*, *por qué importa* y *cómo se arregla*.

---

## Resumen en una frase

El freemium funciona bien en el laboratorio —probé `limites.permitir` a mano y
respeta 1/día gratis, 40/mes Premium y guarda el gasto en disco— pero **tiene tres
agujeros que solo aparecen en producción**: un freno viejo que contradice al nuevo,
un "carnet Premium" que nadie revisa, y una puerta que dice en voz alta quién pagó.

Los seis hallazgos, de más grave a menos:

| # | Dónde | Qué pasa | Gravedad |
|---|-------|----------|:---:|
| 1 | `render.yaml:28` | El servidor real corta a las 5 simulaciones diarias, no a las 30 | 🔴 Alta |
| 2 | `engine/server.py:91` | Cualquiera puede decir "soy Premium" con el correo ajeno | 🔴 Alta |
| 3 | `engine/server.py:980` | Una URL pública revela quién es suscriptor de pago | 🟠 Media-alta |
| 4 | `engine/contenido/limites.py:96` | Una oficina entera comparte 1 simulación al día | 🟠 Media |
| 5 | `web/src/ui/premium.js:11` | El chip Premium tapa el aviso legal CMF | 🟠 Media |
| 6 | `web/src/ui/premium.js:118` | El panel se cierra solo en el momento equivocado | 🟡 Baja |

*(Nota: la suite completa de `pytest` no pudo correr en este entorno porque
faltan `mesa` y `numpy` instalados. Lo que sí probé directamente fue el módulo
`limites`, que no depende de ellos.)*

---

## 1. 🔴 El freno de producción quedó desincronizado

**Archivo:** `render.yaml:28`

### Qué encontré

El blueprint que configura el servidor en Render todavía dice:

```yaml
- key: ENJAMBRE_MAX_SIM_DIA
  value: "5"
- key: ENJAMBRE_MAX_SIM_IP_HORA
  value: "3"
```

Pero el código nuevo (`limites.py:41`) espera **30** como tope global diario, y
le promete a Premium **40 simulaciones al mes**. Además `ENJAMBRE_MAX_SIM_IP_HORA`
ya no lo lee nadie: busqué en todo el código y solo aparece en `render.yaml` y en
dos documentos. Es una variable muerta.

Y las dos variables nuevas —`ENJAMBRE_SIM_DIA_GRATIS` y `ENJAMBRE_SIM_MES_PREMIUM`—
**no están declaradas** en el blueprint.

### Por qué importa

En Render mandan las variables de entorno, no los valores por defecto del código.
Como `ENJAMBRE_MAX_SIM_DIA=5` está puesta a mano, el tope global real del sitio es
**5, no 30**. Y ese tope global manda sobre todos (`limites.py:80`), incluido Premium.

Traducido: **la sexta simulación nueva del día falla para todo el mundo**. Un
suscriptor que pagó $6,99 por sus 40 mensuales entra a las 3 de la tarde, escribe
un titular, y recibe:

> *"El enjambre agotó sus simulaciones públicas de hoy. Suscríbete al Pulso para
> no perderte la reacción de mañana."*

Le estamos pidiendo que se suscriba a lo que ya pagó. Es la peor cara posible del
producto y no se ve en desarrollo local, porque local no lee `render.yaml`.

*Analogía:* pusiste un cartel nuevo en la puerta que dice "abierto hasta las 10",
pero el reloj del cerrojo automático sigue programado a las 6.

### Cómo se arregla

Sincronizar el blueprint con el código: subir el tope global, borrar la variable
muerta y declarar las dos nuevas para que se puedan ajustar sin tocar código.

```yaml
# 🔒 TOPES DE PRODUCCIÓN — la muralla de la billetera.
# Global: manda sobre gratis y Premium por igual.
- key: ENJAMBRE_MAX_SIM_DIA
  value: "30"
- key: ENJAMBRE_SIM_DIA_GRATIS
  value: "1"
- key: ENJAMBRE_SIM_MES_PREMIUM
  value: "40"
# (ENJAMBRE_MAX_SIM_IP_HORA se elimina: ya no la lee nadie.)
```

**Cuenta de la billetera:** 30 simulaciones × ~$0,12 = **$3,60 al día ≈ $108 al mes**
en el peor caso. Vale la pena decidir ese número a conciencia, no heredarlo. Si el
techo debe ser más bajo, hay que bajarlo aquí *y* revisar que 40/mes de Premium
siga siendo alcanzable.

**Ojo con un efecto de segundo orden:** aunque se suba el global a 30, un Premium
que llegue tarde un día muy activo puede seguir chocando con el tope global. Vale
la pena, más adelante, **reservar cupo** para los que pagan (ej. el global corta a
los gratis en 25, pero deja pasar a Premium hasta 30). Hoy no existe esa distinción.

---

## 2. 🔴 El "carnet Premium" no lo revisa nadie

**Archivo:** `engine/server.py:91` (`_correo_premium`)

### Qué encontré

Cuando el visitante suelta un titular, el navegador manda por WebSocket un campo
`premium_email`. El servidor lo toma así:

```python
def _correo_premium(mensaje: dict) -> str | None:
    email = str(mensaje.get("premium_email", "")).strip().lower()
    return email if seguridad.correo_valido(email) else None
```

`correo_valido` solo verifica que *tenga forma* de correo (que lleve arroba y punto).
No hay ninguna prueba de que quien lo escribe sea el dueño de ese buzón.

### Por qué importa

Son dos daños, y el segundo es el que no tiene vuelta atrás:

1. **Cupo regalado.** Cualquiera que adivine o conozca el correo de un suscriptor
   escribe esa dirección en el chip y obtiene el nivel de 40/mes gratis.
2. **Cupo robado, sin forma de devolverlo.** El gasto Premium se guarda **en disco**,
   por correo y por mes (`limites.py:92` → tabla `gasto_premium`). El impostor no
   solo simula gratis: **le está gastando el mes al suscriptor real**. Cuando el que
   pagó llega el día 20 y descubre que ya "usó" sus 40, no hay ningún mecanismo
   para restituírselas. Hay que entrar a la base a mano.

Y el ataque no requiere adivinar nada: el hallazgo #3 regala una lista de correos
Premium válidos.

*Analogía:* es un club donde entras diciendo el nombre de un socio, y además te
descuentan las consumiciones de la cuenta de ese socio.

### Cómo se arregla

La solución correcta es un **token firmado**, no el correo desnudo. La buena
noticia es que el proyecto **ya tiene toda la maquinaria** — es la misma idea del
double opt-in de El Pulso (`/api/confirmar/{token}`):

1. El visitante escribe su correo en el chip.
2. El servidor **no responde si es Premium o no**. Le manda un correo con un
   enlace mágico (token firmado, con fecha de expiración de ~30 días).
3. Al hacer clic, el navegador guarda **el token**, no el correo.
4. Cada simulación manda el token; el servidor verifica la firma antes de conceder
   el nivel Premium.

Así el cupo solo lo puede gastar quien tiene acceso real al buzón — que es
exactamente la persona que pagó. De paso, esto **cierra el hallazgo #3 por
construcción**: el endpoint deja de responder sí/no y pasa a responder siempre
"te mandamos un correo si corresponde".

**Parche intermedio, si el enlace mágico no cabe ahora:** al menos evitar el daño
irreversible — llevar el gasto Premium por **correo + huella del dispositivo**, de
modo que un impostor consuma su propio contador y no el del suscriptor. No cierra
el robo de cupo, pero deja de castigar a quien pagó.

---

## 3. 🟠 Una URL pública dice quién es suscriptor de pago

**Archivo:** `engine/server.py:980` (`GET /api/pulso/premium?email=`)

### Qué encontré

```python
@app.get("/api/pulso/premium")
def estado_premium(email: str = "") -> dict:
    ...
    if es_prem:
        return {"premium": True,  "limite": ..., "periodo": "mes"}
    return {"premium": False, "limite": ..., "periodo": "día"}
```

Sin autenticación de ningún tipo. Le preguntas por cualquier dirección y te dice
si es suscriptor activo de pago. El comentario del código dice *"Respuesta neutra
si el correo es inválido (no revela nada)"* — pero eso solo cubre las direcciones
mal escritas. Para un correo bien formado, la respuesta es un sí o un no directo.

La única protección es el rate-limit genérico de `/api/*`: **120 solicitudes por
minuto por IP** (`engine/contenido/seguridad.py:74`).

### Por qué importa

Dos problemas encadenados:

- **Fuga de datos personales.** Estás publicando, para quien pregunte, el hecho de
  que una persona concreta le paga a El Pulso. Es información comercial de tus
  clientes que nadie autorizó a difundir.
- **Es la munición del hallazgo #2.** 120 consultas por minuto son **172.800 al
  día por IP** — y basta con rotar IPs para multiplicarlo. Alguien puede pasar una
  lista de correos filtrados de cualquier otro sitio, quedarse con los que
  responden `premium: true`, y usar esos correos para quemarles el cupo.

*Analogía:* es un portero que, si le preguntas por cualquier nombre, te confirma
en voz alta si esa persona es socio del club. Y no se cansa de responder.

### Cómo se arregla

En orden de preferencia:

1. **Lo ideal:** eliminar el endpoint como oráculo. Con el enlace mágico del
   hallazgo #2, la respuesta pasa a ser siempre la misma —*"Si ese correo es
   Premium, le enviamos un enlace"*— sin importar si existe o no. Un atacante no
   aprende nada.
2. **Mínimo si se mantiene el endpoint:** ponerle su propia clase de rate-limit
   mucho más estricta (`seguridad._clase` ya soporta clases distintas: hoy
   distingue `replay` de `api`). Algo como **5 por minuto y 20 por hora por IP**
   basta para el uso legítimo —una persona verifica su correo una vez— y hace la
   enumeración masiva impracticable. Añadir un retardo artificial de ~1 segundo
   refuerza lo mismo.

---

## 4. 🟠 Una oficina entera comparte una simulación al día

**Archivo:** `engine/contenido/limites.py:96`

### Qué encontré

El nivel gratis cuenta el uso por dirección IP cruda:

```python
clave = f"ip:{ip}"
fecha, cuenta = _uso.get(clave, (hoy, 0))
```

El cambio de PR #23 pasó el free de **3 por hora** a **1 por día**.

### Por qué importa

Una dirección IP no identifica a una persona: identifica a una *salida a internet*.
Muchísimos visitantes comparten una:

- Una oficina, un colegio o una universidad: cientos de personas, una IP.
- **CGNAT**, la técnica que usan casi todos los operadores móviles: miles de
  clientes de Entel o Movistar compartiendo la misma IP pública.
- Cualquier VPN o red corporativa.

Con 3/hora el daño era tolerable: quien chocaba con el muro esperaba un rato y
volvía a entrar. **Con 1/día el bloqueo dura hasta medianoche.** Si una sola
persona de una oficina prueba El Enjambre a las 9 de la mañana, todos los demás
—que nunca lo usaron— ven durante el resto del día:

> *"Usaste tu simulación gratis de hoy."*

Es un mensaje que además **miente**, y en el peor momento posible: la primera
visita de alguien que llega desde El Pulso o desde un medio. En un lanzamiento
donde el tráfico llega en oleadas desde pocas redes, esto puede significar que la
mayoría de los visitantes nuevos jamás vea al enjambre moverse.

*Analogía:* le pusiste el límite de entradas al edificio, no a cada persona.

### Cómo se arregla

Tres opciones, combinables:

1. **Cambiar la clave, no el número.** En vez de contar por IP sola, contar por
   IP + una huella suave del navegador (el `User-Agent`, o un identificador
   aleatorio guardado en `localStorage`). No es inviolable —quien quiera saltárselo
   abre una ventana privada— pero *ese no es el ataque que importa*: el objetivo es
   no castigar al inocente. La muralla de la billetera sigue siendo el tope global,
   que es el que de verdad protege la plata.
2. **Suavizar la ventana.** 1 cada 8 horas en vez de 1 por día calendario: el
   visitante bloqueado a las 9 AM se libera a las 5 PM en vez de a medianoche.
3. **Arreglar el mensaje.** Aunque el límite se mantenga, no afirmar algo que puede
   ser falso. Mejor: *"El enjambre ya corrió una simulación desde tu red hoy.
   Mira las 3 destacadas del día, o desbloquea 40 al mes con El Pulso Premium."*
   Dice la verdad, no acusa a nadie, y ofrece salida.

Mi recomendación: **(1) + (3)**. Mantiene la economía intacta y deja de castigar
a visitantes que no hicieron nada.

---

## 5. 🟠 El chip Premium tapa el aviso legal de la CMF

**Archivos:** `web/src/ui/premium.js:11` y `web/src/style.css:557`

### Qué encontré

Los dos elementos viven exactamente en el mismo rincón de la pantalla:

| | `.beta-badge` (el disclaimer) | `.pz-chip` (Premium) |
|---|---|---|
| posición | `fixed` | `fixed` |
| izquierda | `16px` | `16px` |
| abajo | `14px` | `16px` |
| **z-index** | **25** | **40** |

Mayor `z-index` gana: **el chip Premium queda encima del badge**. Y como el chip
es más alto que el badge, no solo lo tapa visualmente — **le roba los clics**. El
botón que abre el disclaimer completo de la CMF deja de ser accesible.

En móvil es peor: el badge se corre a `left:12px; bottom:10px` (`style.css:586`),
así que se mete aún más debajo del chip.

### Por qué importa

Esto no es un detalle estético. El `.beta-badge` es la pieza que abre el aviso
legal completo — el que deja claro que El Enjambre es un **simulador educativo y
no asesoría financiera**. Es la restricción regulatoria número uno del proyecto
(CMF Chile, sección 1 del CLAUDE.md). Un elemento comercial que tapa el aviso
legal es exactamente el orden de prioridades invertido: le estamos vendiendo una
suscripción al usuario encima del texto que lo protege.

*Analogía:* pegaste el cartel de "oferta" justo encima de la señal de "no es una
recomendación de compra".

### Cómo se arregla

Separarlos físicamente. El disclaimer se queda donde está —abajo a la izquierda,
es su lugar de siempre— y el chip Premium se muda a la **derecha**:

```css
.pz-chip{position:fixed; right:16px; bottom:16px; z-index:40; ...}
.pz-pop {position:fixed; right:16px; bottom:60px; z-index:41; ...}
```

Y verificar que en esa esquina no haya otro elemento (hay que revisar el HUD del
enjambre antes de dar el cambio por bueno).

**Además, como regla del proyecto:** el `.beta-badge` debería llevar el `z-index`
más alto de la interfaz normal, no uno de los más bajos. Ningún elemento comercial
debería poder taparlo nunca — hoy es una coincidencia de números lo que decide
quién gana, y esa coincidencia ya salió mal una vez.

---

## 6. 🟡 El panel se cierra solo en el momento equivocado

**Archivo:** `web/src/ui/premium.js:118`

### Qué encontré

Al desbloquear con éxito, el panel se cierra solo tras 1,4 segundos:

```js
guardarPremium(correo); pintarChip()
msg.textContent = '¡Listo! Ya tienes 40 simulaciones al mes. 🐝'
setTimeout(cerrar, 1400)
```

El problema: `cerrar()` no cierra *ese* panel, cierra **el que esté abierto cuando
el reloj llegue a cero**. Si el usuario cierra el panel y vuelve a abrirlo dentro
de esos 1,4 segundos, el temporizador viejo mata al panel nuevo.

### Por qué importa

Es el bug menos grave de la lista, pero ocurre justo después de un pago y en el
gesto natural de "a ver, déjame confirmar que quedó bien": el usuario toca el chip,
el panel aparece y desaparece de golpe. Parece que la app se rompió en el momento
exacto en que debía inspirar confianza.

*Analogía:* dejaste programado "apagar la luz en 1,4 segundos" en vez de "apagar
*esta* luz". Si alguien enciende otra mientras tanto, se apaga la que no era.

### Cómo se arregla

Guardar el temporizador y cancelarlo al cerrar, y verificar que el panel sea el
mismo antes de actuar:

```js
let temporizador = null

function cerrar() {
  clearTimeout(temporizador)   // ← cancela cualquier cierre pendiente
  temporizador = null
  pop?.remove()
  pop = null
}

// ...y en desbloquear(), recordando cuál panel es:
const mio = pop
temporizador = setTimeout(() => { if (pop === mio) cerrar() }, 1400)
```

---

## Comentarios desactualizados (de paso)

No son errores, pero dicen algo falso al próximo que lea el código:

- `engine/server.py:980` — el docstring dice *"desbloquear el cupo de 10/día"*.
  Son **40/mes**.
- `web/src/ui/premium.js:2-3` — el encabezado dice *"elevar su cupo de 3 a 10
  simulaciones al día"*. Son **de 1/día a 40/mes**. (Lo que se muestra en pantalla
  sí está bien: las cadenas de texto de la interfaz ya dicen 40/mes.)

---

## Qué haría primero

Si hay que elegir un orden:

1. **Hallazgo #1** (`render.yaml`) — es una línea de configuración y hoy le está
   rompiendo el producto a los clientes que pagan. Cinco minutos de trabajo.
2. **Hallazgo #5** (el chip sobre el disclaimer) — es CSS, riesgo cero, y es la
   pieza regulatoria. Cinco minutos.
3. **Hallazgo #4** (mensaje + clave del límite gratis) — barato y protege el
   lanzamiento del embudo de entrada.
4. **Hallazgos #2 y #3 juntos** (enlace mágico) — es el trabajo de verdad, medio
   día bien hecho, pero cierra los dos de una sola vez porque son el mismo problema
   visto por sus dos extremos.
5. **Hallazgo #6** — cuando toque tocar ese archivo por otra razón.

---

*Rubicón Lab · El Enjambre · Revisión de código del freemium · 19 de agosto de 2026*
