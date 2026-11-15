# Criterios de inclusión — set de preguntas (Fase 1)

*Rubicón Lab · El Enjambre · 2026-11-15*
*Congelados ANTES de seleccionar preguntas (regla del plan). No se mueven después
de ver resultados.*

> **Para Giorgio, en simple.** Para medir si el enjambre "acierta" de verdad,
> necesitamos un banco de preguntas honestas: eventos binarios (pasó / no pasó),
> ya resueltos, donde la noticia sea la entrada natural del enjambre. Esto define
> cuáles entran y cuáles no, para no hacer trampa eligiendo las fáciles.

## Qué pregunta entra

1. **Binaria y resuelta sin ambigüedad** (sí/no, pasó/no pasó).
2. **Foco macro/índice** (Fed, tasas, inflación/IPC, empleo, recesión, umbrales de
   índices). Es el único terreno donde **la dirección está en el titular** — y
   por tanto donde el enjambre puede aportar. Cripto/acción entran solo como
   control para confirmar el techo, no como objetivo.
3. **Historial de precio suficiente** para reconstruir la probabilidad del mercado
   en el instante de corte T (cuando haya fuente con licencia; ver `fuentes_datos.md`).
4. **Titulares fechados disponibles** para el período previo a T.
5. **Se excluye** toda pregunta de resolución subjetiva o disputada.

## Anti-contaminación (regla dura)

El modelo de IA puede "saber" el resultado de eventos pasados. Por eso cada
pregunta se marca con `post_corte_conocimiento`:

- **Preferir eventos posteriores al corte de conocimiento del modelo** — son los
  verdaderamente no vistos y dan la medición más limpia. Se recolectan **en vivo**
  desde ahora hacia adelante.
- Los eventos anteriores al corte se reportan **por separado** y se contrastan con
  la variante **solo-reglas** (sin líderes LLM).

## Esquema de cada pregunta (`data/preguntas.jsonl`, una por línea)

| Campo | Qué es |
|---|---|
| `id` | identificador único |
| `texto` | la pregunta binaria (ej. "¿La Fed sube tasas en su reunión de dic-2026?") |
| `categoria` | fed · inflacion · empleo · indice · recesion · cripto · accion |
| `fecha_apertura` | cuándo abrió el mercado/evento |
| `T` | instante de corte: el enjambre solo ve datos < T |
| `titulares_hasta_T` | lista de titulares fechados antes de T (entrada del enjambre) |
| `precio_mercado_T` | probabilidad implícita del mercado en T (null hasta tener fuente con licencia) |
| `resultado` | 1 = sí ocurrió, 0 = no (hecho público) |
| `fuente` | de dónde salió la resolución y el precio |
| `fecha_descarga` | cuándo se obtuvo |
| `post_corte_conocimiento` | true si el evento es posterior al corte del modelo |
| `split` | train · val · test (la prueba sellada no se toca hasta el final) |

## Nota honesta sobre el dato con licencia

Por `docs/fuentes_datos.md`: el **resultado** y la **pregunta** son hechos públicos
(gratis, sin licencia). Solo el `precio_mercado_T` depende de Polymarket/Kalshi, que
están en ámbar. Por eso el banco puede empezar a llenarse **ya** con todo menos ese
campo, y el precio se agrega cuando se resuelva la licencia — sin frenar el resto.

## Regla "nada inventado"

Si un campo no se puede obtener, queda `null` y se reporta el hueco. **Nunca** se
rellena con un número estimado. (La única fila de ejemplo en `preguntas.jsonl` lleva
`ejemplo: true` y sus campos de resultado/precio en `null` a propósito.)
