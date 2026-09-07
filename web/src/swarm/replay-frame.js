// Medidas del replay 3D, robustas al tamaño de la mezcla.
//
// El motor guarda SIEMPRE `TICKS_REPLAY` frames por simulación
// (engine/server.py: TICKS_PREVIOS 10 + TICKS_POSTERIORES 140). Ese número es
// una constante del producto: NO cambia aunque la mezcla de agentes crezca.
// El tamaño de cada frame, en cambio, es 8 + N_agentes, y N sí puede cambiar
// (p. ej. la mezcla pasó de 10.000 a 10.150 al sumar un arquetipo).
//
// Por eso derivamos N por-buffer desde el conteo fijo de frames en vez de
// hardcodearlo: así el replay lee bien tanto los replays HISTÓRICOS ya guardados
// (10.000 agentes, que sobreviven en el disco persistente de Render) como los
// nuevos (10.150) — sin romperse cuando la mezcla vuelve a cambiar.
export const TICKS_REPLAY = 150            // TICKS_PREVIOS + TICKS_POSTERIORES
export const N_AGENTES_VIGENTE = 10150     // tamaño de la mezcla actual (fallback)

/**
 * Dado el buffer crudo de un replay, deduce cuántos agentes trae cada frame.
 * Devuelve { nAgentes, tamanoFrame, total }.
 */
export function medidasReplay(byteLength) {
  const tamanoFrame = Math.round(byteLength / TICKS_REPLAY)
  const nAgentes = tamanoFrame - 8
  // el buffer debe ser un múltiplo EXACTO de (8 + N) × TICKS_REPLAY
  if (nAgentes > 0 && tamanoFrame * TICKS_REPLAY === byteLength) {
    return { nAgentes, tamanoFrame, total: TICKS_REPLAY }
  }
  // buffer con forma inesperada: degradamos al tamaño vigente sin reventar
  const tamanoVigente = 8 + N_AGENTES_VIGENTE
  return {
    nAgentes: N_AGENTES_VIGENTE,
    tamanoFrame: tamanoVigente,
    total: Math.floor(byteLength / tamanoVigente),
  }
}
