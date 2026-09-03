# Hoja de ruta — calibración de El Enjambre

Para: Giorgio, Rubicón Lab  
Fecha: 3 de septiembre de 2026  
Rama de trabajo: `calibracion/impacto-no-lineal`  
Producción (`main`): **no se toca hasta evidencia**

Esto es el mapa de lo que **falta implementar y medir**, en orden.
Una hipótesis por sesión. Si una no gana, se tira y no se arrastra.

---

## Dónde estamos hoy

El enjambre **funciona**. No está **calibrado**.

| Meta | Hoy (632 exámenes IA) | ¿Listo? |
|---|---|---|
| Dirección ≥ 70 % | 60 % (entre 56 y 64 %) | No |
| En el S&P | 54 % — una moneda | No |
| Fuerza (ni corto ni 3×) | 0.46 (grita ~3×) | No |
| En vivo | 26 % simulado vs 5 % real | No |

El parlante (10.000 agentes) ya grita ~11 % en un crash. El cuello es el
**micrófono**: los ~110 cerebros que leen el titular.

### Ya construido (no repetir)

| Pieza | Estado |
|---|---|
| Medición honesta (Wilson, Loss que penaliza pasarse, n≥80) | Hecho |
| Libreta partida por mercado (índice/acción/cripto) | Hecho |
| v1a subir volumen | Medida. **No pasa.** |
| v1b paquete de perillas | Código. **No usar.** |
| v1c zona muerta (tapar susurros) | Medida. No va a producción sola. |
| v1d prompt “¿sorpresa o ya estaba en el precio?” | **Código listo. No medido** (falta clave Claude). |
| v1e = v1c + v1d | Código. **No medir** hasta tener v1d solo. |

---

## Cómo seguir (reglas)

1. **Una palanca por sesión.** Si se mueven tres a la vez, no se sabe cuál curó.
2. **Producción = baseline** hasta que una hipótesis gane en hold-out.
3. **No fusionar a `main`** con un 8/12 ni con un prompt nuevo sin nota.
4. **70 % de normales + 30 % de extremas** en cada tanda de noticias.
5. Solo cuentan cerebros **IA**. Si no hay saldo, el examen no vale.
6. El producto se califica en **índice + acción**. Cripto no declara victoria.

---

## Lo que falta — fases

### Fase A — Destrabar (vos, 10 minutos)

**Falta:** la clave de Claude en el entorno donde se rinden los exámenes.

Sin eso, v1d está escrita y no se puede poner a prueba. El saldo puede
estar recargado en Anthropic; esta máquina no la ve.

**Hecho cuando:** un titular de prueba sale con `fuente: api` (no `fallback`).

---

### Fase B — Medir v1d (~US$1.50, una sesión)

**Qué es:** los cerebros leen con 3 reglas nuevas:
- si ya estaba en el precio → señal casi 0
- si es earnings → beat/miss de *esa* empresa
- si hay sopa de tickers → el hecho, no el primer nombre

**Cómo:** tanda de 12 titulares ya armada (4 Fed “as expected”, 3 crashes,
3 resultados, 2 ruido), baseline vs v1d.

```text
python -m contenido.tanda_microfono --dry          # ver la lista, US$0
ENJAMBRE_PERILLAS=baseline python -m contenido.tanda_microfono --n 12
ENJAMBRE_PERILLAS=hipotesis_v1d python -m contenido.tanda_microfono --n 12
```

**Pasa si:**
- Fed-en-pausa ya no se desploma (el grito baja, el signo no se inventa)
- Lehman / aranceles **siguen** siendo fuertes
- Target/Medline ya no salen +50 % contra +4 % real

**Si no pasa:** se descarta v1d. No se enciende v1e. Se va a la Fase D
(limpiar datos) y se piensa el siguiente golpe al prompt, no al volumen.

---

### Fase C — Limpiar la libreta (US$0, se puede en paralelo a A)

Esto **sí falta implementar**. No mueve el mercado; evita que la nota mienta.

| Trabajo | Por qué |
|---|---|
| Puntuar el símbolo del **hecho**, no el primer ticker de la lista | Hoy “Eli Lilly…” se compara con APP |
| Sacar de la nota “whale activity / most-searched / crypto update” | No son exámenes, son ruido |
| Banco de hold-out **solo SPY/QQQ + acciones líquidas** | 233/632 son cripto; ensucian el 70 % |
| Etiquetar a mano 30–40 titulares priced-in vs sorpresa | El léxico deja ~450 en “otro/ambiguo” |

**Hecho cuando:** la libreta de índice+acción no mezcla sopas de tickers
ni cables de Benzinga que no son un evento.

---

### Fase D — Si v1d gana: v1e (barato)

Juntar zona muerta (v1c) + prompt (v1d). **Solo si B pasó.**

Si se juntan antes, no se sabe qué curó. Una sesión, mismo banco de 12,
después una tanda un poco más grande (20–30).

---

### Fase E — El 70 % de verdad (~US$10)

**Falta implementar el protocolo**, no solo “correr más”:

- ~40 noticias para ajustar (no se cuentan en la nota final)
- **~80 hold-out** que el enjambre no vio, 70 % normales / 30 % extremas
- Solo índice + acción, solo IA
- Misma hipótesis que ganó en B/D, congelada

**Se declara listo solo si, en esos 80:**

| Meta | Número |
|---|---|
| Dirección | ≥ 70 % **y** el piso de Wilson ≥ ~60 % |
| Fuerza simétrica | ≥ 0.70 (ni la mitad ni el triple) |
| Dentro de ±30 % del real | ≥ 40 % |
| Hechos estilizados | siguen pasando |
| En vivo (muro) | ya no sale 26 % vs 5 % |

Hasta no tener esto, **nadie dice 70 %**. Un 8/12 es teatro.

---

### Fase F — Solo si E se estanca

Estas **no están implementadas**. No se tocan antes del hold-out.

| Mejora | Qué haría | Cuándo |
|---|---|---|
| Campo `sorpresa` en el JSON del cerebro (número 0–1) | Medir priced-in de verdad, no solo con el prompt | Si v1d ayuda pero no basta |
| GEPA / DSPy sobre los 8 prompts | Ajustar el oído de cada arquetipo | Caro; después de E |
| Más peso a Quant en earnings, Doomer en crashes (MoE suave) | Menos cancelación FOMO vs Quant (caso Nvidia) | Cuando haya n≥30 por casilla |
| Retorno anormal (CAR) en vez del close-to-close | Quitar el ruido del día | Cuando la libreta esté limpia |
| Bajar `ganancia_consenso` 0.8 → 0.5 | Si v1d no corta el 3× | Último recurso de volumen; v1a enseñó |

---

## Lo que no se implementa (lista cerrada)

| Idea | Por qué no |
|---|---|
| v1b / más FOMO / más influencers | El enjambre ya grita 3× |
| Subir `impacto_base` otra vez | v1a: infla días chicos, no mueve extremos |
| Fijar el precio (Kyle-λ, k × señal) | Se rompen los 5 hechos estilizados |
| PyABC / SBI / 100.000 simulaciones | Impagable con 10.000 agentes |
| Entrenar XGBoost con 12 filas | Teatro con más decimales |
| Fusionar a `main` “para probar en vivo” | El vivo ya grita 26 % vs 5 % |

---

## Calendario práctico (si hay clave)

| Sesión | Qué | Plata |
|---|---|---|
| 0 | Poner la clave de Claude donde se rinde | US$0 |
| 1 | Fase C (limpiar libreta) — se puede el mismo día que 0 | US$0 |
| 2 | Fase B: 12 vs 12, baseline contra v1d | ~US$3 |
| 3 | Si B pasa: Fase D, v1e, 12–30 titulares | ~US$2–4 |
| 4 | Fase E: 40 ajuste + 80 hold-out | ~US$10–15 |
| 5 | Recién ahí: ¿se fusiona o se tira? | — |

Si en la sesión 2 v1d pierde: no hay sesión 3 de paquete. Se limpia
dato (C) y se diseña **otra** palanca de micrófono (campo sorpresa, no
volumen).

---

## Cómo se ve el éxito

Un usuario en el muro lee “Fed mantiene tasas, como se esperaba” y el
enjambre se mueve **poco**. Lee “Lehman quiebra” y se mueve **mucho**.
Lee “Nvidia earnings” y el signo coincide con el beat/miss. La libreta
de índice+acción, con 80 casos que no se usaron para ajustar, dice
≥ 70 % de dirección sin gritar 3×.

Eso es calibrado. Hoy no estamos ahí. El camino de arriba es cómo llegar
sin romper el producto.

*Rubicón Lab · hoja de ruta · 3 sep 2026*
