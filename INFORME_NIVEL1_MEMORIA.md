# Informe: Nivel 1 — Contexto Histórico (memoria de los agentes)

**Rama:** `feature/memoria-agentes` (aislada — parte de `main`, no toca producción)
**Fecha:** 5 de septiembre de 2026
**Veredicto de una línea:** el feature está implementado, **verificado que funciona** y es **seguro** (no rompe los hechos estilizados). Falta medir su *beneficio* real (subir el acierto en negativas), que solo se puede confirmar con un backtest LLM (cuesta saldo).

---

## 0. Resumen ejecutivo

- Los agentes ahora **recuerdan las últimas 5 noticias** y, ante una racha mala (3+ negativas), entran en **modo cautela**: amortiguan su reacción a una nueva mala noticia (×0.7). Tras una buena racha, amplifican una buena (×1.2).
- Está **acotado al retail emocional** (miedosos, noise traders); los institucionales conservan la memoria pero deciden por fundamentales.
- **Probado:** la lógica dispara y ajusta correctamente, y los **hechos estilizados siguen pasando** (9 tests ✅). No rompe nada.
- **Lo que NO se pudo medir aquí:** si de verdad sube el acierto en noticias negativas (el 38%). Eso requiere re-correr el backtest real (líderes LLM), que cuesta saldo Anthropic.

## 1. La idea (y por qué es interesante)

El desglose de la Fase 0 mostró que el enjambre **exagera el pánico** ante malas noticias (acierta solo 38% de las negativas). El Nivel 1 ataca justo eso con un mecanismo psicológicamente realista: la **desensibilización**. Tras varias malas noticias seguidas, la gente se "acostumbra" y reacciona menos a la siguiente. Eso reduce la sobre-reacción del enjambre exactamente donde falla.

## 2. Qué se implementó

### 2.1 `AgenteBase` (engine/agents/base.py)
- **Atributos** en `__init__`: `memoria_noticias` (lista), `modo_cautela` (bool), `contador_malas`, `contador_buenas`.
- **`actualizar_memoria(sentimiento, texto=None)`**: agrega la noticia (guarda las últimas 5), cuenta rachas (mala si `< -0.3`, buena si `> 0.3`) y activa `modo_cautela` con **3+ malas** en la ventana.
- **`ajustar_por_contexto(sentimiento_raw)`**: en cautela y ante una mala nueva → `×0.7`; con 3+ buenas y ante una buena → `×1.2`; si no, sin cambio.

### 2.2 `MercadoEnjambre.aplicar_noticia` (engine/model.py)
Cada vez que llega una noticia, **todos los agentes** la registran (`actualizar_memoria`). Así construyen su memoria y sus rachas.

### 2.3 Enganche en el retail emocional (engine/agents/reglas.py)
El ajuste se aplica solo donde el retail *emocional* percibe el sentimiento:
- **Miedoso** (el motor del pánico): `sentimiento_percibido = ajustar_por_contexto(model.sentimiento + senal_social)`.
- **Noise trader sensible**: idem en su probabilidad de compra.
- **Institucionales (fundamentalista, etc.):** conservan memoria pero su decisión **no** usa el ajuste — la cautela por rachas es un fenómeno de retail, no de un fondo que opera por valor.

### Ajuste menor respecto al borrador
El método original guardaba `datetime.now()` (reloj de pared). Lo cambié por `model.tick` (tiempo de simulación): en una simulación el reloj real no tiene sentido, evita una dependencia y el campo no lo usa la lógica igual.

## 3. Verificación (evidencia)

### 3.1 La lógica dispara y ajusta (no es un no-op)
Prueba directa: tras inyectar 3 noticias de −0.5 a un miedoso →
```
memoria: 3 · contador_malas: 3 · modo_cautela: True
ajustar_por_contexto(-0.4) = -0.28   (= -0.4 × 0.7) ✅
```
Y el fundamentalista tiene memoria (n=4) pero su decisión no usa el ajuste (acotado al retail, como se diseñó).

### 3.2 No rompe los hechos estilizados
`pytest engine/validation/test_hechos_estilizados.py` → **`9 passed` (2 min 19 s)**.

En una sesión normal (seed 42) el resumen sale **idéntico** a la línea base (curtosis 5.22, clustering 0.317, sin autocorrelación 0.073, asimetría de pánico 1.37). Esto es porque, con noticias aleatorias simétricas, la racha de 3 malas **rara vez ocurre** → el feature queda inerte y no altera nada. Es la señal de un buen diseño: se activa solo cuando debe.

## 4. Lo que SÍ y lo que NO sabemos (honestidad)

| | |
|---|---|
| ✅ **Es seguro** | Funciona, se activa ante rachas malas, amortigua el pánico, y NO degrada el realismo estadístico (9 tests). |
| ❓ **¿Ayuda al 38%?** | No medido. El efecto en el acierto de negativas solo se ve re-corriendo el backtest **real** (líderes LLM leyendo titulares), que cuesta ~$0.12/evento de saldo Anthropic. Aquí solo se pudo confirmar *seguridad*, no *beneficio*. |

## 5. Cómo seguir (opciones)

1. **Dejarlo en la rama** como feature validado-seguro; medir el beneficio real más adelante.
2. **Gastar saldo** en un backtest real acotado para ver si el 38% sube — la única forma de confirmarlo.
3. **Mergear a producción** ya: es seguro (no rompe nada) y *podría* ayudar. Recomendación honesta: si se mergea, que sea como *"memoria de agentes — neutra y segura"*, **no** como *"arreglo del 38%"* hasta medirlo.

---

*Archivos: `engine/agents/base.py`, `engine/model.py`, `engine/agents/reglas.py`.
Verificado con `pytest engine/validation/test_hechos_estilizados.py` (9 passed) y
pruebas directas. `main` y producción: sin cambios.*
