# RUNBOOK — THE LAST EXPERIMENT (activación, operación, apagado)

> **Todo comando `seal`/`resolve`/`finalize` está BLOQUEADO** salvo que exista un
> manifiesto congelado y se pase `--aprobado-por-fundador`. No actives nada sin la
> autorización por escrito de Giorgio, el presupuesto congelado y un proveedor de precios
> point-in-time (PIT) aprobado. Capital real = USD 0 siempre.

Todos los comandos se ejecutan desde `engine/` con `python3.13` (o `python`), en la rama
`research/last-experiment`.

## 0. Desarrollo (sin red, sin dinero, sin riesgo)

```bash
cd engine
python -m pytest validation/test_last_experiment_*.py -q      # 61 tests
python -m research.last_experiment.cli dry-run --fixture synthetic   # end-to-end sintético
python -m research.last_experiment.cli validate-data --config ../docs/last-experiment/manifest.example.json
python -m research.last_experiment.cli train --fixture synthetic --out artifacts/bundle.json
```

El `dry-run` entrena, sella 6 probabilidades por evento, resuelve con precios ficticios,
evalúa (Brier pareado + bootstrap) y corre paper trading. Es CAÑERÍA, **no** evidencia.

## 1. Antes de T0 (preparación, máx. 4 semanas) — lo que falta

1. **Proveedor de precios PIT de SPY** (bloqueo real): adaptador Alpaca/Yahoo que
   cumpla el contrato (barra final certificada, calendario NYSE, ajustes corporativos).
   Implementar la clase que cumpla `resolver.ProveedorPrecios`. Validar licencia/calidad.
   Las claves van por variable de entorno/secreto, NUNCA en config/logs/artefactos.
2. **Panel histórico de desarrollo** (no el banco de shocks): panel diario de SPY con las
   mismas reglas de cutoff/horizonte para entrenar P0–P5 y preseleccionar B*. Guardar en
   `docs/last-experiment/dev_panel.json`. Las señales LLM sobre noticias antiguas son
   solo para desarrollo (riesgo de memorización), NUNCA evidencia confirmatoria.
3. **Fuentes macro** (FRED/ALFRED, BLS, BEA) con vintage real para sorpresas; opcionales,
   omitir si no se certifica el timestamp.
4. **Clave Anthropic** para P2/P3 en vivo (variable de entorno; ver estado de la clave en
   el proyecto). Presupuesto de API dentro de los USD 300 propuestos.
5. `train` real sobre el panel; revisar el **reporte de potencia** (σ de d_t, n para
   Δ=0.01 y 0.02). Si la potencia es baja, informar a Giorgio ANTES de activar.
6. `freeze`:

```bash
# fijar T0 en el manifiesto, luego:
python -m research.last_experiment.cli freeze \
  --config ../docs/last-experiment/manifest.json \
  --artifact artifacts/bundle.json --commit "$(git rev-parse HEAD)" \
  --hash-datos <hash_del_panel_PIT> --out ../docs/last-experiment/manifest.json
```

`freeze` deriva T1 = T0 + 6 meses, fija B*, y sella los hashes de código/calendario/
prompts/artefactos. A partir de aquí nada se toca.

## 2. Operación en vivo (solo tras aprobación)

- Scheduler durable (ver `.github/workflows/last-experiment.yml`, **desactivado** por
  defecto): disparo frecuente con guardia de calendario/horario NYSE. Un workflow
  atrasado NO genera un pronóstico pasado.
- `seal`: en cada sesión válida, antes del deadline, construye el snapshot PIT, corre
  P0–P5 y sella en el ledger (idempotente). Si el ABM pasa el deadline → fallo registrado.
- `resolve`: tras madurar cada evento (cierre de salida + barra final), inserta el outcome
  inmutable.
- **Observabilidad SOLO operativa** durante la ventana: heartbeat, última emisión,
  latencia, coste, nº de faltantes. NUNCA mostrar aciertos/Brier/PnL antes de T1.

```bash
python -m research.last_experiment.cli seal     --manifest ../docs/last-experiment/manifest.json --aprobado-por-fundador
python -m research.last_experiment.cli resolve  --manifest ../docs/last-experiment/manifest.json --aprobado-por-fundador
```

## 3. Cierre (en T1, con la última etiqueta madura)

```bash
python -m research.last_experiment.cli finalize --manifest ../docs/last-experiment/manifest.json --aprobado-por-fundador
```

Genera `FINAL_REPORT.md`, JSON de métricas y export de pronósticos/resultados con hashes.
Aplica la regla de decisión. Archiva con tag de cierre; secretos fuera de Git; recursos
facturables se apagan solo con autorización explícita.

## 4. Apagado de emergencia

Si hay fallo de seguridad o presupuesto: terminar y archivar como fallo operativo/
inconcluso (NO reiniciar selectivamente). Una reparación de infraestructura sin cambio de
semántica puede hacerse si queda auditada y no recalcula pronósticos anteriores.

## 5. Amenazas y límites honestos

- El hash-chain del ledger protege del uso normal, **no** de un administrador con acceso
  directo a SQLite. Exportar a destino de solo escritura para endurecerlo.
- Señales LLM sobre noticias antiguas ≠ evidencia (memorización). Solo lo prospectivo
  cuenta.
- 100 pares no garantizan potencia; un IC ancho = inconcluso = cierre empresarial.
