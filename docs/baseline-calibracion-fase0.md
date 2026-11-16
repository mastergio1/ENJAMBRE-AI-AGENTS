# Línea base de calibración — Fase 0 (instrumentación)

*Rubicón Lab · El Enjambre · 2026-11-16. Reporte por segmento sobre 678 casos
reales (export de calibración). Generado por `engine/calibration/evaluar_por_segmento.py`.
Diagnóstico, NO criterio de despliegue (la categoría es circular; decide el walk-forward).*

## Lo que confirma este baseline
- **Asimetría pos/neg real y por mercado:** el enjambre acierta mucho en subidas
  y poco en bajadas (acción 84.7% sube vs 27.5% baja; cripto 81.5% vs 46.5%;
  índice 64.6% vs 46.2%). (Ojo: "sube/baja" aquí es la categoría circular.)
- **La confianza auto-reportada del LLM NO informa del acierto:** corr(confianza,
  hit) ≈ 0 para todos los arquetipos (−0.08 a +0.09). → justifica calibrarla (Fase 2).
- **IA real > respaldo léxico:** 60.7% vs 51.9% (solo 27 casos léxicos).
- **Voces flojas en dirección:** value_paciente 8.8% y macro_trader 32.0%
  (value es neutral por diseño, así que su "acierto direccional" es bajo por
  construcción; macro aporta poca dirección).

## Reporte completo

```
casos usables: 678   hit global: 60.3%

=== MERCADO × SIGNO REAL × |consenso| → hit% (n) ===
  indice (n=170)
    real_sube: hit 64.6% (n=79)  por |consenso|: 0.00-0.15:50.0%(2)  0.15-0.35:57.1%(49)  0.35-0.60:78.6%(28)  0.60-1.01:None%(0)
    real_baja: hit 46.2% (n=91)  por |consenso|: 0.00-0.15:0.0%(6)  0.15-0.35:51.7%(58)  0.35-0.60:44.4%(27)  0.60-1.01:None%(0)
  accion (n=239)
    real_sube: hit 84.7% (n=137)  por |consenso|: 0.00-0.15:50.0%(4)  0.15-0.35:80.6%(72)  0.35-0.60:91.8%(61)  0.60-1.01:None%(0)
    real_baja: hit 27.5% (n=102)  por |consenso|: 0.00-0.15:16.7%(12)  0.15-0.35:27.1%(59)  0.35-0.60:32.3%(31)  0.60-1.01:None%(0)
  cripto (n=221)
    real_sube: hit 81.5% (n=135)  por |consenso|: 0.00-0.15:90.0%(10)  0.15-0.35:86.6%(97)  0.35-0.60:63.0%(27)  0.60-1.01:0.0%(1)
    real_baja: hit 46.5% (n=86)  por |consenso|: 0.00-0.15:0.0%(6)  0.15-0.35:45.2%(62)  0.35-0.60:66.7%(18)  0.60-1.01:None%(0)
  oro (n=22)
    real_sube: hit 57.1% (n=7)  por |consenso|: 0.00-0.15:None%(0)  0.15-0.35:60.0%(5)  0.35-0.60:50.0%(2)  0.60-1.01:None%(0)
    real_baja: hit 40.0% (n=15)  por |consenso|: 0.00-0.15:25.0%(4)  0.15-0.35:42.9%(7)  0.35-0.60:50.0%(4)  0.60-1.01:None%(0)
  petroleo (n=26)
    real_sube: hit 53.3% (n=15)  por |consenso|: 0.00-0.15:33.3%(3)  0.15-0.35:37.5%(8)  0.35-0.60:100.0%(4)  0.60-1.01:None%(0)
    real_baja: hit 36.4% (n=11)  por |consenso|: 0.00-0.15:None%(0)  0.15-0.35:44.4%(9)  0.35-0.60:0.0%(2)  0.60-1.01:None%(0)

=== ARQUETIPO → acierto direccional · corr(confianza,hit) ===
  institucional_frio     61.5% (n=678)  corr=0.006
  quant_esceptico        45.1% (n=678)  corr=0.067
  fomo_evangelista       63.9% (n=678)  corr=0.012
  doomer                 45.3% (n=678)  corr=-0.036
  contrarian_sabio       43.8% (n=678)  corr=-0.012
  macro_trader           32.0% (n=678)  corr=-0.082
  influencer_optimista   56.2% (n=678)  corr=0.091
  value_paciente         8.8% (n=678)  corr=-0.052

=== FUENTE → hit% (n) ===
  ia_real            60.7% (n=651)
  respaldo_lexico    51.9% (n=27)
```

---

## Fase 2 — medición offline de consenso (antes de cablear)

Medido con walk-forward (Platt, fuera de muestra) sobre los 678 casos:

| Esquema | Brier OOS | Skill |
|---|---:|---:|
| **ponderada 0.3 (actual, prioridad 1)** | **0.2227** | **10.1%** |
| fiabilidad (re-pesar por acierto histórico, H5) | 0.2236 | 9.7% |
| simple | 0.2258 | 8.8% |
| recortada ~12% (H4) | 0.2328 | 6.0% |
| mediana (H4) | 0.2384 | 3.8% |

**Verdicto:** H4 (consenso robusto: mediana/recortada) **empeora**; H5 (re-pesar por
fiabilidad) **empata/no supera** a la señal ponderada que ya está en producción.
→ **No se cablean.** La señal ponderada 0.3 sigue siendo el mejor estimador OOS.
Medir antes de implementar evitó dos cambios inútiles.

Lo que queda de Fase 2 (Plan A suave, MINIMO_IA gradual, hash de prompt en caché)
toca el motor en vivo → requiere despliegue (reinicia Render) → se decide con
Giorgio respecto al evento del 21.
