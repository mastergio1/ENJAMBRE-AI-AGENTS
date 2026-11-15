"""Calibración de la señal del enjambre a probabilidad honesta.

El enjambre produce una señal agregada (el sentimiento de los líderes, la
dirección del precio simulado). Este módulo la convierte en una **probabilidad**
P(sí) ∈ [0, 1] y la **calibra** para que ese número sea honesto: cuando el
enjambre dice "80% seguro", que de verdad acierte ~80% de las veces.

Por qué importa (para Giorgio, en simple): un "% de dirección" no dice qué tan
confiado está el enjambre. Una probabilidad calibrada sí — y es lo que se puede
comparar de igual a igual contra un mercado de predicción (vía el Brier score).

Diseño:
- **Python puro** (sin numpy/sklearn): el motor corre en Render con RAM ajustada,
  así que no sumamos dependencias pesadas. Solo biblioteca estándar.
- El **mapeo** señal→probabilidad cruda es una función **reemplazable** (registro
  MAPEOS), para poder cambiarlo sin tocar el resto.
- Dos calibradores clásicos: **Platt** (logístico, suave) e **isotónico**
  (escalonado, no asume forma). Se ajustan SOLO con datos de entrenamiento.
- El calibrador, al predecir, **nunca** recibe el resultado real (sin fuga).

Este módulo NO llama a la IA ni toca la red: es pura matemática sobre resultados
ya medidos. Se puede ajustar gratis en cuanto tengamos la libreta histórica
(señal del enjambre + resultado real) exportada desde producción.
"""

from __future__ import annotations

import math

EPS = 1e-12


# ---------------------------------------------------------------------------
# 1. Mapeo señal del enjambre → probabilidad cruda P(sí) ∈ [0, 1] (reemplazable)
# ---------------------------------------------------------------------------

def _clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _sigmoid(z: float) -> float:
    """Logística estable numéricamente."""
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def mapeo_senal_media(reporte: dict) -> float:
    """Desde el sentimiento medio de los líderes ∈ [-1, 1] → P(sube) ∈ [0, 1].
    Lineal y simple: venta total (−1) → 0, compra total (+1) → 1."""
    s = _clip(float(reporte.get("senal_media_lideres", 0.0)), -1.0, 1.0)
    return (s + 1.0) / 2.0


def mapeo_direccion(reporte: dict, escala: float = 2.0) -> float:
    """Desde la dirección simulada (en %) → P(sube), aplastando con una logística.
    `escala` controla cuán rápido satura (2% ≈ bastante confianza)."""
    d = float(reporte.get("direccion_pct", 0.0))
    return _sigmoid(d / escala)


# registro de mapeos reemplazables: se elige por nombre
MAPEOS = {
    "senal_media": mapeo_senal_media,
    "direccion": mapeo_direccion,
}


def senal_a_prob_cruda(reporte: dict, modo: str = "senal_media") -> float:
    """Convierte el reporte del enjambre en una probabilidad CRUDA (sin calibrar).
    `modo` elige el mapeo del registro MAPEOS."""
    if modo not in MAPEOS:
        raise ValueError(f"mapeo desconocido: {modo!r}. Opciones: {sorted(MAPEOS)}")
    return _clip(MAPEOS[modo](reporte), 0.0, 1.0)


# ---------------------------------------------------------------------------
# 2. Métricas de calibración
# ---------------------------------------------------------------------------

def brier(probs, resultados) -> float:
    """Brier score = media de (prob − resultado)². Menor es mejor (0 = perfecto)."""
    pares = list(zip(probs, resultados))
    if not pares:
        raise ValueError("brier necesita al menos un caso")
    return sum((p - y) ** 2 for p, y in pares) / len(pares)


def log_loss(probs, resultados) -> float:
    """Log loss (entropía cruzada). Menor es mejor. Recorta para no explotar."""
    pares = list(zip(probs, resultados))
    if not pares:
        raise ValueError("log_loss necesita al menos un caso")
    total = 0.0
    for p, y in pares:
        p = _clip(p, EPS, 1.0 - EPS)
        total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return total / len(pares)


def tasa_base(resultados) -> float:
    """La proporción de 'sí' en los datos — la línea base trivial #2."""
    res = list(resultados)
    if not res:
        raise ValueError("tasa_base necesita al menos un caso")
    return sum(res) / len(res)


def curva_confiabilidad(probs, resultados, n_tramos: int = 10):
    """Agrupa en tramos de probabilidad y compara lo predicho vs lo observado.
    Devuelve lista de dicts: {tramo, pred_media, obs_frac, n}. Un calibrador
    bueno tiene pred_media ≈ obs_frac en cada tramo."""
    tramos = [[] for _ in range(n_tramos)]
    for p, y in zip(probs, resultados):
        idx = min(int(_clip(p, 0.0, 1.0 - EPS) * n_tramos), n_tramos - 1)
        tramos[idx].append((p, y))
    salida = []
    for i, t in enumerate(tramos):
        if not t:
            continue
        salida.append({
            "tramo": f"[{i / n_tramos:.1f}, {(i + 1) / n_tramos:.1f})",
            "pred_media": sum(p for p, _ in t) / len(t),
            "obs_frac": sum(y for _, y in t) / len(t),
            "n": len(t),
        })
    return salida


def skill_score(brier_modelo: float, brier_base: float) -> float:
    """1 − (Brier modelo / Brier base). >0 = mejor que la línea base."""
    if brier_base <= 0:
        return 0.0
    return 1.0 - (brier_modelo / brier_base)


# ---------------------------------------------------------------------------
# 3. Calibradores (se ajustan SOLO con entrenamiento; nunca ven el resultado al predecir)
# ---------------------------------------------------------------------------

class CalibradorPlatt:
    """Escalado de Platt: ajusta una logística P = sigmoid(a·x + b) sobre la señal.
    Suave; asume una relación monótona en forma de S. Ajuste por descenso de
    gradiente sobre la log-loss, con la entrada estandarizada para estabilidad."""

    def __init__(self):
        self.a = 0.0
        self.b = 0.0
        self._mu = 0.0
        self._sd = 1.0
        self.ajustado = False

    def fit(self, scores, resultados, iteraciones: int = 3000, lr: float = 0.3):
        xs = [float(s) for s in scores]
        ys = [float(y) for y in resultados]
        n = len(xs)
        if n == 0:
            raise ValueError("fit necesita al menos un caso")
        self._mu = sum(xs) / n
        var = sum((x - self._mu) ** 2 for x in xs) / n
        self._sd = math.sqrt(var) if var > 1e-18 else 1.0
        zs = [(x - self._mu) / self._sd for x in xs]
        a, b = 0.0, 0.0
        for _ in range(iteraciones):
            ga = gb = 0.0
            for z, y in zip(zs, ys):
                d = _sigmoid(a * z + b) - y
                ga += d * z
                gb += d
            a -= lr * ga / n
            b -= lr * gb / n
        self.a, self.b, self.ajustado = a, b, True
        return self

    def predict_uno(self, score: float) -> float:
        z = (float(score) - self._mu) / self._sd
        return _sigmoid(self.a * z + self.b)

    def predict(self, scores):
        return [self.predict_uno(s) for s in scores]


class CalibradorIsotonic:
    """Regresión isotónica (algoritmo Pool-Adjacent-Violators). No asume forma:
    solo que a mayor señal, no menor probabilidad. Más flexible que Platt pero
    necesita más datos para no sobreajustar. Predice por interpolación lineal
    entre los puntos ajustados."""

    def __init__(self):
        self._xs = []   # señales ordenadas (puntos de anclaje)
        self._ys = []   # probabilidad calibrada en cada punto (monótona ↑)
        self.ajustado = False

    def fit(self, scores, resultados):
        pares = sorted(zip((float(s) for s in scores), (float(y) for y in resultados)))
        if not pares:
            raise ValueError("fit necesita al menos un caso")
        # bloques PAV: cada bloque guarda (suma, peso, x_representativa)
        bloques = []
        for x, y in pares:
            bloques.append([y, 1.0, x])
            # fusiona hacia atrás mientras se viole la monotonía
            while len(bloques) > 1 and (bloques[-2][0] / bloques[-2][1]) >= (bloques[-1][0] / bloques[-1][1]):
                s2, w2, x2 = bloques.pop()
                s1, w1, x1 = bloques.pop()
                bloques.append([s1 + s2, w1 + w2, x2])  # x del extremo derecho del bloque
        # expande los bloques a puntos (x, valor_calibrado)
        xs, ys = [], []
        idx = 0
        for suma, peso, _ in bloques:
            valor = suma / peso
            # cada bloque cubre `peso` puntos consecutivos de `pares`
            for _ in range(int(round(peso))):
                xs.append(pares[idx][0])
                ys.append(valor)
                idx += 1
        self._xs, self._ys, self.ajustado = xs, ys, True
        return self

    def predict_uno(self, score: float) -> float:
        xs, ys = self._xs, self._ys
        x = float(score)
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        # búsqueda e interpolación lineal
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        if xs[hi] == xs[lo]:
            return ys[lo]
        t = (x - xs[lo]) / (xs[hi] - xs[lo])
        return ys[lo] + t * (ys[hi] - ys[lo])

    def predict(self, scores):
        return [self.predict_uno(s) for s in scores]


CALIBRADORES = {
    "platt": CalibradorPlatt,
    "isotonic": CalibradorIsotonic,
}


# ---------------------------------------------------------------------------
# 4. Conveniencia: ajustar y evaluar de una
# ---------------------------------------------------------------------------

def ajustar_calibrador(scores, resultados, metodo: str = "platt"):
    """Ajusta un calibrador del registro sobre (señal, resultado) de entrenamiento."""
    if metodo not in CALIBRADORES:
        raise ValueError(f"método desconocido: {metodo!r}. Opciones: {sorted(CALIBRADORES)}")
    return CALIBRADORES[metodo]().fit(scores, resultados)


def evaluar_calibracion(scores_test, resultados_test, calibrador=None) -> dict:
    """Compara el Brier de: (1) 0.5 constante, (2) tasa base, (3) señal cruda,
    (4) señal calibrada (si se pasa un calibrador ya ajustado). Más líneas base,
    más honesto el veredicto."""
    n = len(resultados_test)
    base_rate = tasa_base(resultados_test)
    crudas = [_clip(s, 0.0, 1.0) for s in scores_test]
    salida = {
        "n": n,
        "tasa_base": round(base_rate, 4),
        "brier_constante_050": round(brier([0.5] * n, resultados_test), 4),
        "brier_tasa_base": round(brier([base_rate] * n, resultados_test), 4),
        "brier_cruda": round(brier(crudas, resultados_test), 4),
    }
    if calibrador is not None and getattr(calibrador, "ajustado", False):
        cal = calibrador.predict(scores_test)
        salida["brier_calibrada"] = round(brier(cal, resultados_test), 4)
        salida["skill_vs_base"] = round(
            skill_score(brier(cal, resultados_test), salida["brier_tasa_base"]), 4)
    return salida
