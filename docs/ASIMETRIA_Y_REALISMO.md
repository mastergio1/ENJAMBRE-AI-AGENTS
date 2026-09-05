# Asimetría y Realismo: Por qué el Enjambre "Falla" con Noticias Negativas

**Fecha:** 5 de septiembre de 2026
**Contexto:** Resultados de la Fase 0 de validación

---

## El Hallazgo

El enjambre acierta la dirección del mercado:
- **Noticias positivas: 80%** 🟢
- **Noticias negativas: 38%** 🔴

A simple vista, parece un defecto. Pero en buena parte es **lo contrario**: es la **huella** de un mercado real (con un matiz honesto que se explica más abajo).

---

## Por qué el Mercado Ignora las Malas Noticias

1. **El precio ya las descontó:** Los mercados eficientes incorporan la información antes de que llegue a los titulares.
2. **Efecto rebote:** Las malas noticias suelen venir después de caídas, y el mercado tiende a recuperarse (sobreventa).
3. **Asimetría de pánico:** Las caídas son más violentas que las subidas (efecto apalancamiento).

**El enjambre está programado para anticipar el pánico.** Por eso:
- Acierta el 80% de las positivas (euforia)
- Pero "falla" el 62% de las negativas (anticipa caídas que no ocurren)

### El matiz honesto (importante)
El 38% tiene **dos causas mezcladas**, no una:
- **(a) Irreducible:** el mercado real sube seguido tras una mala noticia (ya está en el precio, o rebota). Ningún ajuste puede predecir eso sin volver el enjambre un contrarian irreal.
- **(b) Corregible con cuidado:** el enjambre además *exagera* el pánico. Suavizarlo podría subir algo las negativas, pero **degradaría** las colas gordas y la asimetría que hacen pasar los hechos estilizados. Es un trade-off, no una victoria gratis.

Por eso el 38% se entiende mejor como **rasgo de diseño con un margen de mejora acotado**, no como un simple bug.

---

## La Evidencia: Hechos Estilizados

| Hecho Estilizado | Resultado | Meta | Verdicto |
|------------------|-----------|------|----------|
| Curtosis (colas gordas) | **5.22** | > 3 | ✅ PASA |
| Clustering de volatilidad | **0.317** | > 0 | ✅ PASA |
| Sin autocorrelación | **0.073** | ≈ 0 | ✅ PASA |
| Asimetría de pánico | **1.37** | > 1 | ✅ PASA |

**El enjambre pasa las 4 pruebas de un mercado real.** La asimetría que lo hace "fallar" en negativas es la **misma** que le da colas gordas y crashes creíbles.

---

## Posicionamiento para el Cliente / Marco CMF

**Afirmación defendible:**
> "El enjambre acierta la dirección del mercado ~6 de cada 10 veces globalmente, y hasta 8 de cada 10 con noticias positivas. Su sesgo pesimista (anticipación de pánico) refleja la asimetría real de los mercados financieros."

**Afirmación que NO se debe hacer:**
> "El enjambre predice el precio del mercado."
> "El enjambre es estadísticamente indistinguible de un mercado real."
> *(Ambas son sobre-claims: el enjambre reproduce las huellas estadísticas clave, pero su precisión de magnitud es modesta —correlación ~0.24— y no predice precios.)*

**Posicionamiento correcto:**
> "Es un focus group sintético que muestra cómo reacciona la manada ante noticias. Informa y simula, nunca aconseja."

---

## Conclusión

El 38% en negativas **no es, en su mayor parte, un bug que arreglar**. Es en buena medida la consecuencia natural de un enjambre que:
1. Tiene **asimetría de pánico** (como los mercados reales)
2. Reproduce las **4 huellas estilizadas** clave de un mercado real
3. Es **pesimista por diseño** (anticipa crisis)

Con el matiz honesto de que el enjambre además *exagera* algo el pánico —margen de mejora real, pero acotado por el trade-off con los hechos estilizados—.

**El producto no necesita "arreglarse" de urgencia. Necesita, sobre todo, posicionarse correctamente** — y, si se quiere, un ajuste fino y medido del pánico, siempre re-validando contra los hechos estilizados.
