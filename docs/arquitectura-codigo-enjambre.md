# El Enjambre — Arquitectura a nivel de código

*Rubicón Lab · documento técnico factual · referencia del motor de simulación.*
*Solo describe cómo está construido el código actual. Sin recomendaciones.*

---

## 1. Stack y dependencias

- **Lenguaje:** Python 3.11+.
- **Simulación basada en agentes:** `mesa==3.3.1`.
- **Servidor:** `fastapi==0.139.0` + `uvicorn[standard]==0.51.0` + `websockets==16.0`.
- **LLM:** `anthropic==0.116.0` (modelos `claude-sonnet-5` y `claude-haiku-4-5-20251001`).
- **Numérico/estadística:** `numpy==2.4.6`, `scipy==1.17.1`.
- **Red de influencia:** `networkx==3.6.1`.
- **Imagen:** `Pillow==12.3.0`.
- **Persistencia:** SQLite (biblioteca estándar `sqlite3`, modo WAL).

## 2. Estructura del directorio `engine/`

```
engine/
├── model.py                 # MercadoEnjambre: modelo central, ciclo de ticks
├── market/order_book.py     # LibroOrdenes: formación de precio (VWAP)
├── agents/
│   ├── base.py              # AgenteBase: cartera, órdenes, memoria
│   ├── reglas.py            # 12 tipos de agentes de reglas
│   └── lider.py             # LiderOpinion (tipo 13, LLM)
├── brains/
│   ├── arquetipos.py        # 9 arquetipos LLM (prompts, cantidades, seguidores)
│   ├── cerebro.py           # llamadas a la API, caché, concurrencia
│   ├── reparto.py           # reparto de ~110 cerebros entre 1150 líderes
│   ├── fallback.py          # respaldo léxico (sin API)
│   └── mercado.py           # clasificador de mercado + perfiles de personalidad
├── network/red.py           # construcción de la red de influencia (scale-free)
├── config/agentes.json      # la mezcla de 10.150 agentes + perillas globales
├── validation/
│   ├── hechos_estilizados.py# curtosis, autocorrelación, asimetría de pánico
│   └── test_*.py            # ~45 archivos de tests
├── calibration/             # laboratorio de calibración offline (no lo usa el motor en vivo)
├── contenido/               # capa de contenido (backtest, libreta, persistencia, pulso…)
├── server.py                # FastAPI + WebSocket; orquesta una simulación
├── simular.py               # runner CLI de hechos estilizados
└── demo_titular.py          # runner CLI de un titular
```

## 3. El modelo central — `model.py` → `MercadoEnjambre(mesa.Model)`

### 3.1 Constantes de módulo
- `CAPITAL_BASE = 10_000.0` (capital de un retail 1x; cada tipo lo multiplica por `capital_relativo`).
- `FACTORES_LIQUIDEZ = {"cripto": 30.0, "accion": 40.0}` — tope de `|direccion_pct|` reportado por mercado (función `acotar_magnitud`, P3: recorta magnitud, conserva el signo).
- `GANANCIA_CONSENSO = 0.8` — factor de magnitud aplicado al consenso de la IA al usarlo como tono.
- `MINIMO_IA_CONSENSO = 0.5` — fracción mínima de líderes con respuesta real de IA para usar el consenso como tono (si no, se usa el léxico).
- `ARQUETIPOS_INVERSORES = {quant_esceptico, contrarian_sabio, influencer_optimista}`.
- `ARQUETIPOS_DOOMER = {doomer_selectivo}`.

### 3.2 Estado (`__init__`)
`seed`, `precio_inicial=100.0`, `ticks_horizonte=400`, `ruta_config=config/agentes.json`.
- `self.libro = LibroOrdenes(precio_inicial)` con callback `notificar_ejecucion`.
- `self.sentimiento = 0.0` (sentimiento global, decae `*0.95`/tick).
- `self._ultimo_consenso = 0.0` (P4, fuerza de la señal → "confianza" del reporte).
- `self.perfil = perfil_de("indice")` (perfil de mercado por defecto).
- Series: `historial_precios` (empieza `[100.0]`), `retornos`, `flujo_compras`, `flujo_ventas`.
- `cola_senales`: cola del rumor `(tick_entrega, agente, valor, salto)`.
- `MAX_HISTORIAL = 600` (recorte de colas en sesiones largas).
- Crea agentes (`_crear_agentes`), indexa por id, aísla líderes (`_lideres`), y llama `construir_red(self)`.

### 3.3 Creación de agentes (`_crear_agentes`)
- Lee `config/agentes.json`.
- Perillas globales leídas con override por entorno:
  - `_peso_tono_invertidores` ← `peso_tono_invertidores` (config, def 1.0) / `ENJAMBRE_PESO_TONO_INVERSORES`.
  - `_umbral_correccion` ← `umbral_correccion_sesgo` (config) / `ENJAMBRE_UMBRAL_CORRECCION_SESGO`.
  - `_peso_doomer` ← `ENJAMBRE_PESO_DOOMER` (override global, o `None`).
  - `_peso_doomer_por_mercado` ← config `peso_doomer_por_mercado`.
  - `_peso_doomer_defecto` ← config `peso_doomer`.
  - `_sigma_ruido` ← `ruido_parametros_sigma` (def 0.15).
- Por cada tipo: `capital = capital_relativo * CAPITAL_BASE`; expone `parametros` del tipo en `_cfg_agentes_actual` (lo lee `AgenteBase.cfg`); instancia `cantidad` agentes. Para `lider_opinion`, instancia por arquetipo.
- `CLASES_POR_TIPO` mapea id→clase (fundamentalista, quant_momentum, fondo_pasivo, market_maker, ejecutor_twap, arbitrajista, noise_trader, manada, fomo, miedoso, contrarian, buy_and_hold).

### 3.4 Ciclo de un tick (`step`)
1. `self.tick += 1`.
2. `self.libro.reiniciar_tick(tick)` (expira órdenes viejas, reinicia flujo).
3. `self._entregar_senales()` (entrega el rumor que vence este tick).
4. `self.agents.shuffle_do("step")` (cada agente opera, en orden aleatorio).
5. Decaimiento de `senal_social` de cada agente `*0.75` (se anula bajo 0.01).
6. Precio del tick = `libro.ultimo_precio` si hubo volumen, si no el último precio.
7. Append a `historial_precios`, `retornos`, `flujo_compras`, `flujo_ventas`.
8. `self.sentimiento *= 0.95`.
9. Recorte de colas a `MAX_HISTORIAL`.

### 3.5 Series consultadas por los agentes
- `retorno_acumulado(n)`, `volatilidad_reciente(n)` (desv. est. de los últimos n retornos), `fraccion_compras(n)` (fracción compradora del volumen; `None` si volumen < 100).

## 4. Formación de precio — `market/order_book.py` → `LibroOrdenes`

- **Todas las órdenes son límite.** `VIDA_ORDEN = 4` ticks (luego expiran en `reiniciar_tick`).
- `orden_limite(agente_id, lado, precio, cantidad)`: cruza contra el lado contrario mientras el precio cruce; lo no ejecutado queda reposando (compras ordenadas desc por precio, ventas asc). Devuelve `(ejecutado, dinero)`.
- Cuando se ejecuta una orden en reposo, se llama `notificar_ejecucion(agente_id, lado_dueño, cantidad, precio)` → `MercadoEnjambre._notificar_ejecucion` → `agente.aplicar_ejecucion`.
- Precio del tick = **VWAP** (`valor_tick / volumen_tick`); `ultimo_precio` = último precio transado.
- Contadores por tick: `volumen_tick`, `valor_tick`, `volumen_compras_tick`, `volumen_ventas_tick`.

## 5. Clase base — `agents/base.py` → `AgenteBase(mesa.Agent)`

- Arranca `efectivo = capital*0.5`, `acciones = (capital*0.5)/precio`.
- `cfg` = parámetros del tipo (del config); `ruido(valor, sigma=0.15)` = `valor * gauss(1, sigma)`.
- `colocar_orden(lado, precio_limite, cantidad)`: compra limitada por efectivo y por `tope_sano = 2*capital_inicial/precio`; venta limitada a `acciones` (sin ventas en corto). Ejecuta vía `libro.orden_limite`.
- `comprar_mercado/vender_mercado(cantidad, urgencia)`: urgencia por defecto `min(expovariate(125), 0.06)`; coloca orden a `precio*(1±urgencia)`.
- `aplicar_ejecucion(lado, cantidad, precio)`: actualiza efectivo/acciones, `ultima_accion`, `tick_ultima_accion`.
- **Memoria (Nivel 1):** `actualizar_memoria(sentimiento)` guarda las últimas 5 noticias; `modo_cautela = (nº noticias con sentimiento < -0.3) >= 3`. Lo usa el freno de la manada.
- Atributos de red: `pares`, `lideres_seguidos`, `vecinos`, `senal_social`.

## 6. Los 12 tipos de agentes de reglas — `agents/reglas.py`

Cada uno lee sus parámetros de `config/agentes.json → tipos[].parametros` con `± ruido 15%`.

| # | Clase | Cant. | Cap. rel. | Lógica resumida (código) |
|---|---|---:|---:|---|
| 1 | `Fundamentalista` | 370 | 50 | Valor justo `V` con ruido; opera cada `ticks_entre_operaciones`[10,20]; compra si `precio < V*(1-banda)`, vende si `> V*(1+banda)`; banda ±5% × `volatilidad` del perfil; `V` se actualiza con la noticia (`ponderacion 0.3`). |
| 2 | `QuantMomentum` | 220 | 40 | Media móvil `corta(8)` vs `larga(20)`; entra si corta > larga*1.002 (50% prob/tick); sale por `stop_loss -3%` o cruce a la baja; enfriamiento 5-15 ticks. |
| 3 | `FondoPasivo` | 150 | 60 | Compra fija cada `ticks_entre_compras`[10]; `sensibilidad_noticias = 0` (constante por diseño). |
| 4 | `MarketMaker` | 9 | 100 | Cotiza bid/ask; spread = max(base, 3×vol); si `vol > umbral_volatilidad_panico`[0.008] ×`multiplicador_spread_panico`[3] (tope 0.08); sesga el centro por inventario. |
| 5 | `EjecutorTWAP` | 28 | 30 | Orden grande (40% capital) comprar/vender; la reparte en rebanadas iguales en `ticks_horizonte`. |
| 6 | `Arbitrajista` | 55 | 20 | Opera 10% de las veces; si `|desviación vs media de 3 ticks| > umbral_desviacion`[0.004], opera en contra (anti-inercia). |
| 7 | `NoiseTrader` | 3670 | 1 | Con prob `probabilidad_operar`[0.12] compra/vende al azar; una fracción `fraccion_sensible_noticias`[0.2] inclina su prob con `sentimiento + senal_social` × `desplazamiento`[0.1]. |
| 8 | `Manada` | 1650 | 1 | Observa `vecinos`; umbral de activación aleatorio en `[0.4,0.8]`; si > umbral de vecinos compró/vendió en `ventana_observacion_ticks`[3], copia; el rumor (`senal_social`) baja el umbral; en `modo_cautela` vende ×`factor_freno_cautela`[0.5]. |
| 9 | `FomoRetail` | 1100 | 1 | Si `retorno(ventana 5) > umbral_subida`[0.03] Y la red habla (≥`vecinos_minimos`[2] compraron, o `senal_social>0.25`), compra `fraccion_capital_maxima`[0.15]; vende todo si cae `stop_panico`[4%] desde su entrada. |
| 10 | `Miedoso` | 920 | 1 | Aversión `asimetria_kahneman`[2.5]; pánico si `retorno5 < -0.03/asimetria` o `sentimiento+senal_social < -umbral_miedo`[0.15-0.45]; vende `fraccion_venta_rango`[0.7-1.0]; recompra tras `ticks_calma_para_recomprar`[10] en calma. |
| 11 | `Contrarian` | 460 | 1.5 | Cada `ticks_entre_operaciones`[5,10]; si `(1-fraccion_compras) ≥ umbral_consenso`[0.7] compra; si `fraccion_compras ≥ umbral` vende. |
| 12 | `BuyAndHold` | 368 | 2 | Compra si cae `umbral_caida_oportunidad`[-15%] desde su máximo; con prob `probabilidad_liquidez`[0.001] vende por liquidez. |

## 7. Líderes de opinión (tipo 13) — `agents/lider.py` → `LiderOpinion`

- Atributos: `arquetipo`, `senal ∈ [-1,1]`, `confianza ∈ [0,1]` (def 0.7), `frase`, `seguidores`.
- `recibir_noticia(sentimiento)` (ruta numérica): `senal = sentimiento * gauss(1,0.3)`, y si `< 0` se multiplica ×1.4 (sesgo de negatividad).
- `step()`: si `|senal| ≥ 0.05`, opera `cantidad = |senal|*confianza*0.4*capital/precio` con `urgencia = 0.005 + 0.04*|senal|`; luego `senal *= 0.6`.
- Config: 1150 líderes, `capital_relativo 5`, repartidos en 9 arquetipos.

## 8. Los 9 arquetipos LLM — `brains/arquetipos.py`

Cada arquetipo define `id`, `nombre`, `cantidad`, `seguidores` (rango), `sigue` (tipos a los que arrastra), `prompt`, y opcionalmente `contextual: True`.

| id | nombre | cant. | seguidores | contextual | sigue |
|---|---|---:|---|:---:|---|
| `institucional_frio` | El Institucional Frío | 150 | 12–40 | sí | buy_and_hold, contrarian |
| `quant_esceptico` | El Quant Escéptico | 100 | 12–35 | sí | contrarian, noise_trader |
| `fomo_evangelista` | El FOMO Evangelista | 150 | 40–90 | no | fomo, manada |
| `doomer` | El Doomer | 150 | 25–60 | no | miedoso |
| `contrarian_sabio` | El Contrarian Sabio | 100 | 12–40 | sí | contrarian |
| `macro_trader` | El Macro Trader | 100 | 20–50 | sí | manada, noise_trader |
| `influencer_optimista` | El Influencer Retail Optimista | 150 | 40–90 | no | manada, noise_trader |
| `value_paciente` | El Value Paciente | 100 | 12–35 | sí | buy_and_hold |
| `doomer_selectivo` | El Analista de Riesgo Selectivo | 150 | 20–55 | no | miedoso |

- `INSTRUCCION_JSON`: obliga a responder solo `{"senal", "confianza", "frase"}`.
- `RAZONAMIENTO_CONTEXTUAL`: texto extra que se añade al prompt de los arquetipos `contextual: True` (descontar el futuro / contexto). Los no-contextual reaccionan en frío.

## 9. Cerebros LLM — `brains/cerebro.py` y `brains/reparto.py`

### 9.1 Reparto de cerebros (`reparto.py`)
- `CEREBROS_OBJETIVO = 110`. Los 1150 líderes comparten ~110 "cerebros" (una llamada LLM por cerebro).
- `planificar(lideres, semilla_fn)` reparte cerebros por arquetipo proporcional a su tamaño (mín 1, máx = nº líderes); devuelve `(consultas, asignacion)`. Los líderes de un arquetipo rotan sus cerebros en ronda.
- `expandir(respuestas_cerebros, asignacion)` expande ~110 respuestas a una por líder.

### 9.2 Llamadas a la API (`cerebro.py`)
- `MODELO = "claude-sonnet-5"`, `max_tokens=200`, `MAX_CONCURRENTES=45`, `TIMEOUT_SEGUNDOS=12.0`.
- **No se envía `temperature`** (sonnet-5 devuelve 400). La variabilidad viene del modelo + semilla de caché.
- Orden de resolución por cerebro: **caché → API → fallback léxico**. La simulación nunca se cae por la API.
- Caché por clave `sha256(titular|arquetipo|semilla)[:16]`, en `ENJAMBRE_DB/cache_cerebros/respuestas.json` (persistente) o `brains/cache/respuestas.json` (local). Solo se cachea la fuente `api`.
- `ENJAMBRE_IGNORAR_CACHE` fuerza respuestas frescas (para medir cambios de prompt) y sobrescribe la caché.
- `_validar_respuesta`: extrae JSON, recorta `senal∈[-1,1]`, `confianza∈[0,1]`, `frase` a 160 chars.
- Prompt enviado = `prompt del arquetipo` (+ `RAZONAMIENTO_CONTEXTUAL` si contextual) + `INSTRUCCION_JSON` como `system`; `user` = "Titular de hoy: {titular}".

### 9.3 Fallback léxico (`brains/fallback.py`)
- `respuesta_fallback(titular, arquetipo_id, semilla)` → `{senal, confianza, frase, fuente:"fallback"}` con una función por arquetipo (frases precargadas + `sentimiento_lexico`).
- `sentimiento_lexico(titular)` → float a partir de un diccionario de palabras.

## 10. Clasificación de mercado y perfiles — `brains/mercado.py`

- `MODELO_CLASIFICADOR = "claude-haiku-4-5-20251001"` (1 llamada barata por titular, `max_tokens=30`); fallback léxico `clasificar_lexico` (palabras clave bilingües).
- `MERCADOS_ACTIVOS = ("indice", "accion", "cripto")`. Oro y petróleo **en pausa**: sus perfiles existen pero el clasificador no los elige (caen a `indice`).
- Perfiles `PERFILES[tipo]` con campos `sensibilidad`, `volatilidad`, `refugio`, `etiqueta`:

| tipo | sensibilidad | volatilidad | refugio | estado |
|---|---:|---:|---:|---|
| indice | 1.0 | 1.0 | 0.0 | activo (base) |
| accion | 1.4 | 4.0 | 0.0 | activo |
| cripto | 1.7 | 3.6 | 0.0 | activo |
| petroleo | 1.2 | 2.6 | 0.0 | en pausa |
| oro | 0.9 | 2.2 | 0.25 | en pausa |

- Uso de los campos: `sensibilidad` escala el tono y el arrastre de los líderes; `volatilidad` ensancha bandas (fundamentalista); `refugio` convierte parte del miedo (tono<0) en compra (`_aplicar_perfil`).

## 11. Red de influencia — `network/red.py`

- Grafo dirigido scale-free (conexión preferencial / Efraimidis-Spirakis).
- Líderes → seguidores: cada líder toma `randint(seguidores_rango)` seguidores de los tipos que `sigue`, con peso `1 + popularidad`.
- `manada` y `fomo` reciben 1-2 líderes garantizados.
- Pares horizontales entre `(Manada, FomoRetail, Miedoso)`: 3-8 vecinos, conexión preferencial.
- Institucionales (fundamentalista, quant, fondo pasivo, market maker, TWAP, arbitrajista) **no** están en la red social.
- Deja en cada agente: `pares`, `lideres_seguidos`, `vecinos`; y en cada líder `seguidores`.

## 12. Cómo una noticia se convierte en movimiento

### 12.1 Ruta numérica (tests/calibración) — `model.aplicar_noticia(sentimiento)`
1. `sentimiento` global acumulado (recortado [-1,1]).
2. Cada agente `actualizar_memoria`.
3. Cada líder `recibir_noticia` (señal precomputada).
4. `_propagar_desde_lideres`.

### 12.2 Ruta de titular real — `model.aplicar_titular(titular, respuestas, perfil)`
1. Los 1150 líderes reciben `senal/confianza/frase` de `respuestas` (de `cerebro.analizar_titular` vía reparto).
2. `perfil` ← clasificación de mercado.
3. **Tono de fondo** (`_tono_de_titular`):
   - Solo cuentan los líderes con `fuente ∈ {api, cache}`. Si son menos de `MINIMO_IA_CONSENSO`(0.5) del total → se usa `sentimiento_lexico`.
   - `consenso = Σ(senal*w) / Σ(w)` con `w = confianza`; `w *= peso_tono_invertidores` para `ARQUETIPOS_INVERSORES`; `w *= peso_doomer` para `ARQUETIPOS_DOOMER`.
   - `peso_doomer`: si hay override global (`_peso_doomer`), ese; si no, `peso_doomer_por_mercado[mercado]` (índice 1.0, resto 0.0).
   - **Plan A (corrección de sesgo):** si `_umbral_correccion > 0` y `consenso < -umbral`, devuelve `min(consenso, sentimiento_lexico)` (a plena magnitud, sin invertir el signo).
   - Si no, devuelve `consenso * GANANCIA_CONSENSO`(0.8).
   - Guarda `_ultimo_consenso` (→ "confianza" del reporte, P4).
4. `_aplicar_perfil(tono)`: `tono *= sensibilidad`; si `refugio` y `tono<0`, `tono *= (1 - 2*refugio)`.
5. `sentimiento` global += tono; `_propagar_desde_lideres`.

### 12.3 Propagación del rumor (la "ola")
- `_propagar_desde_lideres`: por cada líder con `|senal|≥0.05`, `valor = senal*confianza*0.7*sensibilidad`; a cada seguidor con retardo `randint(1,4)` ticks (salto 1).
- `_entregar_senales` (en cada `step`): aplica el valor a `senal_social` del agente; si es salto 1, reenvía a sus `pares` con `*0.7` y retardo `randint(1,4)` (salto 2; ahí termina).

## 13. Configuración — `config/agentes.json`

- **Perillas globales (top-level):** `total_agentes: 10150`, `ruido_parametros_sigma: 0.15`, `umbral_correccion_sesgo: 0.35`, `peso_doomer: 0.0`, `peso_doomer_por_mercado: {indice:1.0, accion:0.0, cripto:0.0, oro:0.0, petroleo:0.0}`.
- **Mezcla (10.150 agentes):** 9.000 de reglas + 1.150 líderes.

| tipo | cantidad | capital_relativo | en_red_social |
|---|---:|---:|:---:|
| fundamentalista | 370 | 50 | no |
| quant_momentum | 220 | 40 | no |
| fondo_pasivo | 150 | 60 | no |
| market_maker | 9 | 100 | no |
| ejecutor_twap | 28 | 30 | no |
| arbitrajista | 55 | 20 | no |
| noise_trader | 3670 | 1 | sí |
| manada | 1650 | 1 | sí |
| fomo | 1100 | 1 | sí |
| miedoso | 920 | 1 | sí |
| contrarian | 460 | 1.5 | sí |
| buy_and_hold | 368 | 2 | no |
| lider_opinion | 1150 | 5 | sí |

- `test_config_enchufado.py` verifica que cada parámetro del config sea leído por su agente (excepto `sensibilidad_noticias` del fondo pasivo, constante por diseño).

## 14. Reporte final — `server.py` → `_generar_reporte`

Devuelve un dict con:
- `direccion_pct`, `minimo_pct`, `maximo_pct` (recortados por `acotar_magnitud` según mercado).
- `volatilidad_pct` (desv. est. de los retornos posteriores).
- `confianza` = `abs(_ultimo_consenso)` (P4).
- `senal_media_lideres` = promedio de `senal` de todas las respuestas.
- `desglose` = `{nombre_tipo: {compras, ventas}}` (conteo de operaciones por tipo).
- `frases` = 3 frases (la más bajista, la mediana, la más alcista).
- `descargo` = disclaimer CMF (`contenido/vocabulario.py → DISCLAIMER`).

## 15. Servidor y flujo de simulación — `server.py`

- Constantes: `TICKS_CALENTAMIENTO = 60` (no se transmite), `TICKS_PREVIOS = 10`, `TICKS_POSTERIORES = 140`, `RITMO_DEFECTO = 0.08` s/tick.
- Flujo de una simulación (WebSocket):
  1. `_crear_mercado(semilla)` (horizonte = 60+140).
  2. En paralelo: `analizar_titular_async` (líderes leen el titular, compartiendo cerebros) + `clasificar_async` (tipo de mercado).
  3. `vocabulario.sanear_frases` (filtro CMF a las voces) + `perfil_de(tipo)`.
  4. `TICKS_PREVIOS` de calma transmitidos.
  5. `modelo.aplicar_titular(...)` inyecta la noticia.
  6. `TICKS_POSTERIORES` transmitidos (`modelo.step` + `_contar_acciones` + paquete binario por WS).
  7. `_generar_reporte(...)`; persistencia en SQLite.
- Endpoints principales (prefijo `/api` salvo indicado): `/salud`, `/api/estado`, `/api/muro`, `/api/simulacion/{id}`, `/api/simulacion/{id}/replay`, `/api/duelo/{a}/{b}`, `/api/simular-titular` (POST), `/api/backtest` (POST, protegido), `/api/libreta` (GET, protegido con `x_pipeline_token`), `/api/corrector` (POST), `/api/pipeline` (POST), endpoints de El Pulso/panel/pagos.

## 16. Validación de realismo — `validation/hechos_estilizados.py`

- `curtosis(retornos)` = curtosis de Pearson (una normal = 3).
- `autocorrelacion(serie, rezago)` = autocorrelación en un rezago.
- `asimetria_panico(retornos)` = media del |2.5% peor| / media del 2.5% mejor.
- `simular.py` corre una sesión de 600 ticks con noticias aleatorias e imprime: curtosis, AC de |retornos| (rezagos 1/5/10), AC de retornos (rezago 1), asimetría de pánico, volumen.
- Tests en `validation/test_hechos_estilizados.py` y otros.

## 17. Backtest, libreta y calibración

### 17.1 Backtest — `contenido/backtest.py`
- `evaluar(tamano, mercado, …)`: pasa titulares históricos (`backtest_eventos.json` + cosecha) al enjambre, compara `signo(direccion_pct)` vs `signo(movimiento_real)` (Alpaca), acumula acierto por categoría (`negativa/positiva/neutra`) en un progreso por clave `{mercado|peso|umbral|doomer}`.
- Reporta `con_ia`/`sin_ia` por tanda. `RUEDAS = 2` ticks de medición; `TANDA_MAXIMA = 40`.

### 17.2 Libreta — `contenido/corrector.py → libreta()`
- Lee `simulaciones` con `reaccion_real` (destacadas o backtest), excluye `cerebros == "respaldo"`, arma pares `(sim = direccion_pct, real = pct_real)` separando en vivo vs histórico; devuelve resúmenes.

### 17.3 Persistencia — `contenido/persistencia.py`
- SQLite (WAL). Tabla `simulaciones(id, titular, fuente, fecha, seed, resumen_json, lideres_json, serie_precios, reaccion_real, destacada)`. Ruta `ENJAMBRE_DB` o `engine/datos/enjambre.db`.

### 17.4 Laboratorio de calibración offline — `calibration/`
- `real_optimizer.py`: optimiza (Optuna) contra hechos estilizados usando el motor real `MercadoEnjambre` (headless).
- `optimizer.py`: modelo de agente reducido (NO el motor real).
- `optimizar_freno.py`: optimiza `factor_freno_cautela` de la manada.
- `validacion_base.py`, `verificador.py`: arnés que congela baseline y separa casos visibles/held-out (local, sin IA).
- `data_loader.py`, `recopilar_datos.py`: descargan benchmark real (SPY/Yahoo) para laboratorio.

### 17.5 Capa de probabilidad calibrada — `contenido/calibracion.py`, `calibrar_libreta.py`, `exportar_libreta.py`
- `calibracion.py`: mapeo `senal_a_prob_cruda` (reemplazable), calibradores `CalibradorPlatt` y `CalibradorIsotonic` (Python puro), métricas `brier`, `log_loss`, `curva_confiabilidad`, `tasa_base`, `skill_score`.
- `exportar_libreta.py`: vuelca pares crudos `(direccion_pct, senal_media_lideres, confianza, pct_real, categoria, fuente)` de la base.
- `calibrar_libreta.py`: parte entrena/prueba, ajusta y reporta Brier crudo vs calibrado vs líneas base.

## 18. Variables de entorno

| Variable | Efecto |
|---|---|
| `ANTHROPIC_API_KEY` | sin ella, todos los líderes usan fallback léxico |
| `ENJAMBRE_DB` | ruta de la base SQLite (y de la caché de cerebros) |
| `ENJAMBRE_PESO_TONO_INVERSORES` | override de `peso_tono_invertidores` [0,1] |
| `ENJAMBRE_UMBRAL_CORRECCION_SESGO` | override de `umbral_correccion_sesgo` [0,1] |
| `ENJAMBRE_PESO_DOOMER` | override GLOBAL del peso doomer (manda sobre la segmentación) |
| `ENJAMBRE_IGNORAR_CACHE` | fuerza respuestas frescas de la IA y sobrescribe la caché |

## 19. Resumen numérico de referencia

- Agentes: **10.150** = 9.000 reglas + 1.150 líderes (9 arquetipos).
- Llamadas LLM por simulación: **~110 cerebros** (`claude-sonnet-5`) + **1 clasificación** (`claude-haiku-4-5`).
- Ticks por simulación en vivo: 60 calentamiento (oculto) + 10 previos + 140 posteriores.
- Precio inicial: 100.0; VWAP por tick; órdenes viven 4 ticks.
- Propagación: atenuación 0.7/salto, retardo 1-4 ticks, 2 saltos máximo.
- Mercados activos: índice, acción, cripto (oro/petróleo en pausa).
- Perillas globales actuales: `ruido 0.15`, `umbral_correccion_sesgo 0.35`, `peso_doomer` segmentado (índice 1.0, resto 0.0), `GANANCIA_CONSENSO 0.8`.

---

*Fin del documento. Describe el estado del código a la fecha de generación.*
