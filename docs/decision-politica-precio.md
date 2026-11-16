# Decisión: política de precio de la serie — último-trade, no VWAP

*Rubicón Lab · El Enjambre · Fase 0 (correctitud) · 2026-11-16*

## Contexto

Una auditoría externa (Propuesta 2) señaló una inconsistencia real: la
documentación/comentarios decían que el precio del tick era el **VWAP**, pero el
código construye la serie (`model.historial_precios`) con el **último precio
transado** (`libro.ultimo_precio`). El VWAP (`vwap_tick()`) existía pero no se
usaba para la serie. También advirtió que una orden minúscula puede fijar el
último-trade lejos de donde se operó la mayoría del volumen.

## Qué medimos (3 semillas, 600 ticks, sin IA)

| Métrica | Último-trade (actual) | VWAP |
|---|---|---|
| Divergencia media último-vs-VWAP | — | ~0.5% (máx ~5%) |
| Curtosis (real si >3) | 4.5–5.3 | 7.3–9.4 |
| AC \|retornos\| rezago 1 | 0.19–0.35 | 0.38–0.49 |
| **AC retornos rezago 1 (arrastre, real si <0.10)** | **0.05 promedio** | **~0.40** ❌ |
| Asimetría de pánico (real si >1) | 1.15–1.33 | 1.07–1.35 |

## Decisión

**La serie del mercado usa el ÚLTIMO PRECIO TRANSADO (último-trade).** No se
cambia a VWAP.

**Razón (con datos):** el VWAP es un promedio → suaviza → mete **autocorrelación
artificial** en los retornos. El arrastre salta de ~0.05 (último-trade) a **~0.40
con VWAP**, muy por encima del límite de realismo (<0.10), rompiendo el hecho
estilizado de "sin arrastre / no free lunch". El último-trade es más ruidoso tick
a tick, pero es el que produce un mercado realista.

**Resolución de la inconsistencia:** el **código estaba bien** y la
**documentación estaba mal**. Se corrigieron los comentarios de
`market/order_book.py` y `agents/base.py` para que digan la verdad (último-trade),
y se dejó esta decisión registrada. Cero cambio de comportamiento.

**El VWAP** (`vwap_tick()`) se conserva como **métrica separada** de
ejecución/liquidez (para análisis), no como el precio de la serie.

## Pendiente relacionado (Fase 1)

Para instrumentación de microestructura se puede exponer además el **precio medio
cotizado (mid)** `(mejor_bid + mejor_ask)/2` como tercera métrica — no como serie.
