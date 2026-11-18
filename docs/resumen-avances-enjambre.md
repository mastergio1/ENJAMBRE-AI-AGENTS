# Resumen de avances — El Enjambre

*Rubicón Lab · Giorgio · actualizado 2026-11-18. Qué se ha hecho, qué se ha
encontrado y dónde estamos. Compañero del plan completo en
`docs/plan-evolucion-enjambre.md`.*

---

## 1. En una frase

El Enjambre es el "focus group sintético del mercado": 10.150 inversionistas
simulados reaccionan en 3D a una noticia. El motor está **desplegado y funcionando
en producción**; el trabajo actual es **demostrar, con rigor, cuánto de su señal
es predicción real.**

---

## 2. El camino hasta aquí

Recibimos **cuatro auditorías externas** y de cada una extrajimos lo salvageable,
verificándolo siempre contra el código real:

- **Propuesta 1 (gating + tono):** convergía en "señal > precio + convicción". Se
  implementó la Ventana A.
- **Propuesta 2 (seguridad/ingeniería):** encontró un P0 de credencial real
  (cerrado en vivo) + mejoras legítimas de ingeniería y ciencia (implementadas).
- **Propuesta 3 (ventanas de acierto):** reforzó la dirección del gating.
- **Propuesta 4 (predictiva):** la mejor. Sus 5 afirmaciones de código eran
  correctas y sus fuentes reales. Originó el plan de evolución y la Fase 0.

De ahí nació `plan-evolucion-enjambre.md`: dos vías (CIENCIA y INGENIERÍA) con una
estrella polar — *demostrar con datos fuera de muestra que acierta más que un
modelo simple, no que lo parezca.*

---

## 3. Mejoras YA implementadas, verificadas y desplegadas

### Seguridad (Fase 0 de seguridad)
- 🔒 **P0 cerrado en vivo:** se eliminó una credencial escrita en el código; el
  endpoint ahora valida token de admin. Verificado en producción (la vieja da 404).
- 🔒 **Reserva atómica de presupuesto:** el tope de gasto diario ya no se puede
  pasar por carreras entre pedidos simultáneos (probado con 20 pedidos a la vez).
- 🔒 **Límite de cuerpo HTTP** también para envíos troceados (anti-DoS).

### Ciencia y calibración
- 📊 **Re-medición SIN FUGA:** se detectó y corrigió la fuga de selección del
  cosechador; medición honesta establecida.
- 📊 **Rigor de calibración:** Brier, Platt/Isotonic, log-loss, ECE/MCE,
  walk-forward con baseline solo-train, promoción anidada con holdout congelado,
  partición temporal con embargo.
- 📊 **Ventana A (convicción):** el reporte expone dirección de la señal y nivel
  de convicción; marca cuándo la lectura es fiable (índice + señal fuerte).
- 📊 **doomer_selectivo** segmentado por mercado (ayuda en índice, inerte en
  cripto).

### Motor e ingeniería
- ⚙️ **Benchmark reproducible** del motor (10.150 agentes, ~7.8 ticks/seg).
- ⚙️ **Caché de IA versionada** por modelo+prompt (editar un prompt ya no reutiliza
  respuestas viejas en silencio).
- ⚙️ Arreglo del bug de acciones negativas (reservas en el libro de órdenes) +
  perillas de configuración realmente conectadas + instrumentación de ejecuciones.

### Frontend y presentación
- 🎯 **Badge de convicción** en el reporte, **desplegado en producción** (dorado
  "fiable" / gris "visualización").
- 📱 **Código QR** para el sábado (cartel imprimible, verificado).
- 📄 **Volcado completo del código** (152 archivos) para auditoría externa.

---

## 4. Hallazgos científicos (Fase 0 + Fase 2) — la parte importante

Todo medido con los **617 casos históricos reales**, sin gastar IA.

### ✅ La señal de índice es REAL (no memoria)
Probamos si el acierto venía de que el modelo "recuerda" noticias viejas. **No:**
el acierto en índice es **63% en noticias viejas y 62% en recientes** — no se cae.
La afirmación central del proyecto ("en índices, el texto lleva dirección")
sobrevive la prueba.

### ✅ Los números, con barras de error (bootstrap agrupado por activo)
| | Acierto | Intervalo 95% | Lectura |
|---|---:|:---:|---|
| Todos los mercados | 50.6 % | [45–56] | **azar** (sin señal fuera de índice) |
| Índice (base) | 63.1 % | [52.5–71.4] | **señal real** |
| Índice + convicción fuerte | 80.0 % | [69.6–85.7] | **real y sólido** (excluye azar) |

*(Corrección honesta: el "80%" NO era de 3 casos como temí al inicio; es n=30 con
intervalo que excluye el azar.)*

### ⚠️ La salvedad honesta
Todo descansa en **~4 instrumentos de índice** (SPY, QQQ, DIA, IWM), muy
correlacionados. Es real pero **estrecho**. Confirmarlo con muestra ancha es el
próximo paso.

### 🔍 Qué voces predicen (y cuáles no)
- 🟢 Mejores: **macro_trader (64%), optimista (64.5%), fomo (63%), institucional
  (61%, y 78.6% con convicción fuerte).** Que el macro brille en índice = lógica.
- 🔴 **El doomer perpetuo HACE DAÑO: 35.5%** (siempre dice "baja").
- 🟡 Contrarians flojos en dirección → **confirma con datos** que ya les bajábamos
  el peso.

### ❌ Resultado negativo valioso: reponderar NO mejora la dirección
Probamos la idea estrella de la Fase 2 (ponderar por acierto histórico en vez de
por confianza declarada). Resultado fuera de muestra: **idéntico acierto (64.9%)**
con cualquier esquema. La mayoría de voces fija el signo; bajar el peso del doomer
no lo voltea (0 de 37 casos). **Conclusión que redirige el plan: el lastre está en
los INSUMOS (Fase 1 evidencia), no en los pesos.** Nos ahorró invertir donde no
servía.

---

## 5. Herramientas nuevas (reproducibles, con tests)

| Herramienta | Qué hace |
|---|---|
| `remedir_sin_fuga.py` | Re-mide el acierto sin la fuga de selección |
| `contaminacion_temporal.py` | ¿El acierto decae en noticias recientes? (memoria) |
| `intervalos.py` | Intervalos de confianza (bootstrap agrupado por activo) |
| `acierto_por_arquetipo.py` | Acierto direccional de cada voz |
| `confianza_efectiva.py` | ¿Reponderar por acierto histórico mejora? (no, p/dirección) |
| `benchmark_motor.py` | Rendimiento reproducible del motor |

**20 tests nuevos**, suite completa en verde (386 pasan), todo commiteado y
desplegado.

---

## 6. Dónde estamos y qué sigue

**Estado:** Fase 0 (la verdad) esencialmente completa en todo lo medible sin gastar
IA; Fase 2 probada y **redirigida** por los datos. Llegamos al límite de lo que se
puede medir sin datos nuevos.

**Próximo paso (acción tuya, por botón):** ampliar los datos de índice
(`docs/runbook-ampliar-datos-indice.md`) — cosechar + backtest + exportar en
GitHub Actions, y pasarme el resultado. Con eso confirmo el 62%/80% con muestra
ancha.

**Después (la palanca real):** Fase 1 — **la capa de evidencia** (darle a los
agentes contexto, fecha, expectativa previa, qué ya estaba descontado). Es ahí
donde está la mejora de verdad, no en reordenar los pesos.

**Veredicto provisional honesto:** entre "predictor" y "simulador", nos inclinamos
a **predictor para índice** (ventaja real ~60%, modesta), con el 80% de alta
convicción prometedor y por confirmar con más datos. Esa honestidad —"esto
medimos, esto confirmamos todavía"— es la mejor carta frente a un inversionista
técnico.
