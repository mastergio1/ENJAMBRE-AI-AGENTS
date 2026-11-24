"""THE LAST EXPERIMENT — experimento prospectivo confirmatorio P0–P5 (SPY).

Módulo AISLADO (`engine/research/last_experiment/`). No toca producción, no gasta
dinero, no arriesga capital. Implementa el protocolo congelado de
`docs/last-experiment/PROTOCOL.md` según las Partes I–III del documento maestro
`EL_ENJAMBRE_ULTIMO_EXPERIMENTO_Y_AUDITORIA.md`.

Pregunta científica (I.1): (1) ¿datos financieros + análisis contextual contienen
señal útil? (2) ¿el ABM MEJORA esa combinación con la MISMA información? La (2) decide
la continuidad de El Enjambre. Gate: P5 supera a P4 en Brier por >0.005 Y supera a B*
(mejor no-ABM preseleccionado) Y mejora económica neta. Si no, se archiva el producto.

NADA se activa (seal/resolve/finalize) sin aprobación explícita del fundador.
"""

VERSION = "le-1"  # versión del protocolo/código del experimento
