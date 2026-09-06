# Cómo medir P2 (el impacto real en el 38%)

> P2 saca a los arquetipos "invertidores" (contrarian/quant/optimista) del
> **tono de mercado** — sin tocar su apuesta ni su frase. La perilla es
> `peso_tono_invertidores`: 1.0 = comportamiento actual · 0.0 = fuera del tono.

## El obstáculo que resolvimos

El backtest normal **salta los exámenes ya respaldados** (no re-rinde), y la
caché de cerebros **se borraba en cada deploy**. Por eso no se podía re-medir.
Lo arreglamos con:

1. **Caché de cerebros en el disco persistente** → se calienta una vez y
   sobrevive a los deploys.
2. **Endpoint de evaluación** (`/api/evaluar`) → re-simula los exámenes ya
   rendidos bajo el código/entorno actual y mide el acierto **sin re-respaldar**.
3. **Workflow "Evaluar acierto (P2)"** → un clic, ves el resultado en Actions.

Resultado: la **primera** medición (caché fría) gasta ~$0.12/examen y calienta
la caché; **las siguientes con otro `peso` son casi gratis**.

## Los pasos

### 1. Desplegar P2
Mergear la rama `p2-tono-vs-apuesta` a `main`. Se despliega solo en Render con
`peso = 1.0` por defecto: **cero cambio de comportamiento** hasta que midamos.

### 2. Medir la línea base (peso 1.0) — calienta la caché
GitHub → Actions → **"Evaluar acierto (P2)"** → Run workflow:
- `peso` = `1.0`
- `mercado` = vacío (o `cripto` para empezar chico y barato)
- `tamano` = `0` (todos) o un número chico para probar

Esta corrida **gasta** (~$12 para 100 exámenes) y deja la caché caliente.
Debería reproducir ~**38%** en negativas (la línea base conocida). El resultado
sale en el log de Actions:
```
"negativa": {"aciertos": ..., "total": ..., "acierto": 0.38}
```

### 3. Medir P2 (peso 0.0) — ya casi gratis
Otra vez Run workflow con `peso` = `0.0`. La caché está caliente → los cerebros
responden gratis, solo se re-agrega el tono. Compara el acierto en negativas.

### 4. Barrer valores (gratis)
Repite con `peso` = `0.3`, `0.5`, `0.7`. Busca el punto donde:
- **negativas > 45%** (sube desde 38%),
- **positivas se mantiene > 75%**,
- global no empeora.

### 5. Fijar el ganador
Cuando encuentres el mejor valor, se activa en producción de dos formas:
- **Rápida (sin re-desplegar):** en Render → Environment →
  `ENJAMBRE_PESO_TONO_INVERSORES` = el valor ganador. Toma efecto al reiniciar.
- **Permanente:** poner `"peso_tono_invertidores": <valor>` en
  `engine/config/agentes.json` y mergear.

## Criterio de decisión (honesto)

| Resultado en negativas | Veredicto |
|---|---|
| > 45% y positivas ≥ 75% | ✅ P2 funciona — fijar el valor |
| 42–45% | 🟡 mejora parcial — evaluar si vale |
| < 42% o positivas caen | ❌ descartar P2, ir a P3 (magnitudes) |

## Notas

- La evaluación **no toca el respaldo histórico** — es una medición pura, se
  puede repetir sin ensuciar nada.
- Si el workflow dice "aún corriendo" al agotar el tiempo, vuelve a correrlo:
  con la caché ya caliente termina rápido. O usa `tamano` chico / por `mercado`.
- `GET /api/evaluar` (con el token) devuelve el último resultado y un pequeño
  historial para comparar valores.
