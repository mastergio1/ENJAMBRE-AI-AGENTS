# Calibración por arquetipo — ¿quién descalibra el consenso?

> Fase 3 de la calibración. Mide, con datos reales de IA, el **contenido
> direccional** de cada una de las 8 voces (arquetipos) del enjambre. Es un
> **diagnóstico**, no un cambio de config: dice dónde conviene intervenir, con
> medición antes de desplegar.

## De dónde salen los datos

- **678 casos** con resultado real (617 del backtest histórico + 61 destacadas
  en vivo), cada uno con el resumen de señales por arquetipo (`senales_arquetipo`).
- Extraídos por el **canal propio** `GET /api/calibracion/export` (protegido con
  `X-Pipeline-Token`) + el workflow `Export calibración (artefacto)`. Es
  independiente del respaldo a la rama `respaldo-datos` (cuyo token pudo
  expirar), así que no dependemos de la madrugada para medir.
- Partición **temporal** (2/3 entrena por fecha, 1/3 prueba) — nunca se calibra
  con el futuro.
- Herramienta reproducible: `engine/calibration/ablacion_arquetipos.py`.

Rango: 2026-08-03 a 2026-11-16. Tasa base de "subió": 0.55.

## Qué mide

Para cada arquetipo, su **señal media** se convierte en probabilidad de "subió"
y se mide:
- **acierto direccional**: ¿el signo de la señal coincidió con el movimiento real?
- **Brier calibrado** (Platt, fuera de muestra): qué tan buenas son las
  probabilidades. Más bajo = mejor. Línea base trivial ≈ 0.248.

## Resultado 1 — cada voz por separado

| Arquetipo | Acierto | Brier cal. |
|---|---:|---:|
| institucional_frio | 63.5% | 0.219 |
| **fomo_evangelista** | **64.1%** | 0.223 |
| influencer_optimista | 56.2% | 0.219 |
| macro_trader | 56.1% | 0.244 |
| value_paciente | 51.2% | 0.246 |
| contrarian_sabio | 47.3% | 0.238 |
| quant_esceptico | 46.8% | 0.231 |
| doomer | 45.3% | 0.228 |

Los dos **contrarians** (quant_escéptico, contrarian_sabio) y el **doomer**
aciertan por DEBAJO del 50% a nivel global: su señal, sola, apunta al lado
equivocado más de la mitad de las veces.

## Resultado 2 — leave-one-out: quitar una voz del consenso

Consenso = promedio simple de las 8 voces. Brier del consenso completo: **0.2247**
(acierto 64.2%). Al quitar una voz:

| Quito | Δ Brier | Lectura |
|---|---:|---|
| **quant_esceptico** | **−0.0045** | quitarlo MEJORA: desorientaba |
| **contrarian_sabio** | **−0.0035** | quitarlo MEJORA: desorientaba |
| macro_trader | −0.0003 | neutro |
| value_paciente | −0.0003 | neutro |
| doomer | +0.0021 | ayuda un poco |
| institucional_frio | +0.0024 | ayuda |
| influencer_optimista | +0.0046 | ayuda |
| **fomo_evangelista** | **+0.0135** | ayuda MUCHO (el que más) |

**Y apila:** un consenso sin los 2 contrarians baja el Brier a **0.2185**
(Δ −0.0062); con solo las 4 voces direccionales (institucional, fomo, doomer,
optimista) baja a **0.2167** (Δ −0.0080) manteniendo el acierto (64.6%).

## Resultado 3 — el hallazgo estructural (por tipo de titular)

El acierto global esconde lo más importante. Separando por la clase del titular:

**Titulares NEGATIVOS** (n=265, en la vida real bajaron el 96%):

| Arquetipo | Acierto |
|---|---:|
| **doomer** | **93.6%** |
| value_paciente | 51.7% |
| macro_trader | 48.3% |
| institucional_frio | 46.0% |
| fomo_evangelista | 44.3% |
| quant_esceptico | 34.3% |
| contrarian_sabio | 24.9% |
| influencer_optimista | 4.9% |
| *consenso* | *44.9%* |

**Titulares POSITIVOS** (n=335, subieron el 98%):

| Arquetipo | Acierto |
|---|---:|
| **influencer_optimista** | **98.2%** |
| fomo_evangelista | 80.3% |
| institucional_frio | 77.3% |
| contrarian_sabio | 64.2% |
| macro_trader | 62.2% |
| quant_esceptico | 57.2% |
| value_paciente | 50.0% |
| doomer | 4.8% |

El **doomer** es el ÚNICO que lee bien las malas noticias (93.6%), pero es
catastrófico en las buenas (4.8%). El **influencer_optimista** es su espejo:
98.2% en buenas, 4.9% en malas. Son **especialistas complementarios**: por eso
el doomer "pierde" a nivel global (su acierto en malas se cancela con su fracaso
en buenas), pero su señal es ORO cuando la noticia es genuinamente mala.

Esto es exactamente lo que motivó el `doomer_selectivo` ya activado en índice
(ver CLAUDE.md §5): un doomer que lee la mala noticia a plena magnitud **solo
cuando corresponde**. Este dato le pone número al porqué.

## Advertencia honesta (para no sobrevender)

- Es un diagnóstico con **promedio simple**. El motor real pondera por
  seguidores y confianza, y el consenso mueve el **enjambre 3D**, no solo una
  probabilidad. Así que esto mide *contenido direccional*, no es un cambio de
  config listo para pegar.
- Que un "permaoso" acierte el 93.6% en un grupo que casi todo bajó es en parte
  mecánico (siempre dice "baja" y el grupo bajó). El leave-one-out global, en
  cambio, mezcla buenas y malas y es más limpio: ahí los contrarians salen
  perdedores de verdad.
- Las mejoras de Brier son modestas (−0.006 a −0.008). Reales y repetibles, pero
  no mágicas. El techo direccional del enjambre sigue acotado por lo que el texto
  del titular NO dice (cripto/acción).

## Recomendación concreta (a medir antes de desplegar)

1. **Capa de calibración del reporte** (seguro, no toca el enjambre): construir
   la *probabilidad reportada* ("confianza") a partir de las voces con contenido
   direccional probado, bajando el peso de los dos contrarians. Mejora esperada:
   Brier −0.006 a −0.008 fuera de muestra.
2. **Ruteo del doomer por sentimiento**: el dato respalda **ampliar
   `doomer_selectivo`** a más mercados *con medición por mercado* (como se hizo
   en índice), porque su señal bajista es fiable justo en las malas noticias.
3. **No borrar voces del enjambre**: los contrarians y el doomer aportan a la
   dinámica visual (olas, pánico, reversión). La intervención es de *peso en la
   calibración*, no de *existencia en la simulación*.

## ✅ Implementado (Intervención A — señal de predicción ponderada)

La recomendación 1 ya está en el código, de la forma **más segura posible**:

- Nuevo campo del reporte `senal_media_ponderada` (`engine/contenido/senal_prediccion.py`):
  promedio de las señales de los líderes **bajando a 0.3 el peso de las 2 voces
  contrarian** (quant escéptico, contrarian sabio). El optimista NO se baja.
- **No toca nada del enjambre**: ni la simulación, ni el tono de mercado, ni las
  frases mostradas, ni la `senal_media_lideres` histórica (promedio simple, que
  queda intacta para comparar). Solo agrega el número que alimentará la
  probabilidad calibrada cuando se publique.
- Mapeo de calibración `senal_ponderada` (`contenido/calibracion.py`): usa el
  campo nuevo y cae al viejo si un caso histórico no lo trae.
- Reversible al instante con el env `ENJAMBRE_PESO_CONTRARIANS` (1.0 = vuelve al
  promedio simple; vacío = 0.3).

**Medición definitiva (678 casos reales, partición temporal, promedio como el del
motor):**

| Señal de predicción | Brier calibrado |
|---|---:|
| Actual (promedio simple) | 0.2212 |
| **Ponderada, contrarians 0.3 (producción)** | **0.2185** (Δ −0.0027) |
| Ponderada, contrarians 0.0 | 0.2179 (Δ −0.0033) |

Se eligió 0.3 (no 0.0) para capturar la mayor parte de la mejora dejando un
colchón contra el sobreajuste a 678 casos. Tests: `test_senal_ponderada.py`.
