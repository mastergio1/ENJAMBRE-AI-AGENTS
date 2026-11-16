# Resultado: calibración agregada sobre datos reales

*Rubicón Lab · El Enjambre · Fase 2–3 · 2026-11-16*

## Qué se midió

Sobre **643 casos reales** (reacción del enjambre vs movimiento real, todos con
`cerebros: "ia"` — IA real, no respaldo), tomados de la libreta pública
(`datos/calibracion.json`, rama respaldo-datos). Se convierte la dirección
simulada del enjambre en una probabilidad P(sube) y se calibra (Platt /
Isotónica). **Split temporal** (entrena con los casos antiguos, prueba con los
recientes) para no filtrar futuro. Métrica: **Brier score** (menor = mejor).
`calibration/calibrar_respaldo.py` lo reproduce.

## Resultados (Brier en prueba, held-out temporal)

| Mercado | casos | Brier línea base | Brier CRUDO | Brier CALIBRADO | Skill vs base |
|---|---:|---:|---:|---:|---:|
| **Agregado** | 643 | 0.244 | 0.330 | **0.227** | +6.9% |
| Índice | 345 | 0.232 | 0.325 | **0.217** | +6.4% |
| Cripto | 192 | 0.247 | 0.282 | **0.213** | +14% |
| Acción | 106 | 0.246 | 0.360 | **0.238** | +3.4% |

## Interpretación honesta

1. **La probabilidad CRUDA del enjambre está mal calibrada** (Brier 0.33, peor que
   adivinar la tasa base 0.24). Confirma lo que señalaron las tres auditorías: la
   "confianza" cruda es sobre-confiada.
2. **Calibrada, mejora y supera a las líneas base triviales** en los tres mercados.
   La calibración **funciona**.
3. **La ventaja sobre la base es MODESTA** (skill 3–14%). Es un edge **real y
   medido**, no un oráculo.
4. **Ojo con la lectura de "cripto gana más" (skill 14%):** gran parte de esa
   mejora de Brier es el calibrador **aprendiendo a decir "incierto"** (regresa
   hacia la tasa base donde no hay señal) — eso **baja el Brier sin aportar
   dirección**. Es honestidad, no predicción. Coincide con que en cripto la
   dirección no está en el texto.
5. **Acción es el más débil** (skill 3.4%, y la isotónica sobreajusta con solo 74
   casos de entrenamiento) — consistente con el patrón "el hype precede la caída".
6. **Muestras de prueba chicas** en cripto (58) y acción (32) → esos números son
   **ruidosos/anecdóticos**; el agregado (prueba 193) es el más confiable.

## Conclusión

**La calibración hace la probabilidad del enjambre honesta y le da un edge pequeño
pero real sobre las líneas base triviales; no inventa capacidad predictiva.** Es
exactamente la tesis que veníamos sosteniendo, ahora **medida sobre datos reales**.

## Pendiente (necesita el SQLite de Render)

Esto es la calibración **agregada** (dirección→probabilidad). La calibración **por
arquetipo** (¿quién descalibra el consenso?) necesita las señales por líder
(`lideres_json`), que solo están en el SQLite de producción, no en la libreta
pública. Ese es el siguiente paso de la Fase 3.
