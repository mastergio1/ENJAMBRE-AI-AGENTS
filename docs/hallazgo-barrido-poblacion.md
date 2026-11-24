# Hallazgo — Más agentes NO mejoran la predicción (la empeoran). Fase 2.

*Rubicón Lab · El Enjambre · 2026-11-24. Fase 2 del plan maestro v5 (barrido de
población). Herramienta: `engine/calibration/barrido_poblacion.py` (con tests). Mide
el acierto direccional del ABM a distintos tamaños, con **capital agregado
constante** (control de la auditoría) y **señales de líder congeladas** (sin IA), en
índice (142 casos). Exploratorio (banco histórico). Sin IA.*

## Resultado (semilla 1)

| Enjambre | Agentes | Acierto direccional | Velocidad |
|---|---:|---:|---:|
| Completo | 10.150 | **58.5 %** | 6.6 s/caso |
| 1/4 | 2.540 | 58.5 % | 1.07 s |
| 1/10 | 1.016 | 61.3 % | 0.37 s |
| 1/20 | 510 | **62.7 %** | 0.16 s |

**Monótono:** a menor población, mayor (o igual) acierto. El enjambre GRANDE es el
PEOR; el chico (510) es el mejor y **empata exactamente al consenso de líderes
(A3 = 62.7 %)**.

## Qué significa

1. **Hacer el enjambre más grande no crea señal; añade ruido.** La masa de agentes
   (manada, FOMO, pánico, noise) distorsiona el precio ALEJÁNDOLO del consenso. Mientras
   menos agentes, menos distorsión, y el precio simulado se acerca al consenso (que es
   el techo de acierto ~62.7 %).
2. Refuerza las 4 evidencias previas: el valor predictivo vive en el **consenso LLM**;
   el motor de agentes, cuanto más grande, más resta. "Más agentes = más impresionante"
   es cierto para el PRODUCTO/visual, **falso para la predicción**.
3. **Costo:** 510 agentes corren ~40× más rápido que 10.150 y aciertan igual o mejor.
   Un predictor mínimo no necesita el enjambre grande.

## Caveats (honestidad)

- **Semilla única** (pendiente de confirmación multi-semilla, en curso): el N chico es
  más ruidoso corrida a corrida. La tendencia monótona en 4 tamaños es sugerente, pero
  hay que ver que replica. *(Se actualizará esta sección con el promedio de semillas.)*
- Exploratorio: banco histórico de shocks, n=142. Veredicto definitivo = prospectivo.
- Esto mide DIRECCIÓN. No prueba nada sobre si el ABM predice **riesgo/volatilidad**
  (Fase 4/H14), que es la pista que podría rescatar al motor.

## Implicación para el producto

El enjambre de 10.150 agentes es una **decisión de producto y visualización** (más
espectacular), **no** de predicción. Si algún día se arma un "producto predictor",
usaría el consenso (o 1 LLM) y, a lo sumo, un enjambre pequeño — barato y más fiel.
