"""L4/L5 — Modelos P0–P5: fit/predict, calibración y selección de hiperparámetros.

Todos producen una PROBABILIDAD de subida finita en [0,1] para el MISMO objetivo
(`y=1` si retorno futuro estrictamente positivo). Preprocesamiento ajustado SOLO en
train (mediana + indicadores de ausencia + estandarización). Grid L2 común
C∈{0.01,0.1,1}; selección por Brier medio en folds de desarrollo, desempate por C menor
(I.6).

Control de información (I.2): P4 recibe TODAS las variables de mercado y TODAS las
señales del LLM que alimentan al ABM (score contextual + vector de 9 arquetipos + su
media y dispersión). P5 = exactamente P4 + el resumen de features del ABM. Así la
diferencia P5−P4 aísla el aporte de la SIMULACIÓN, no de información adicional.

Logística L2 por optimización determinista (scipy L-BFGS-B, gradiente analítico). Sin
sklearn. `model_hash` sella coeficientes + lista de features + config.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import optimize

from .config import ARQUETIPOS, hash_canonico
from .features import FEATURES_MACRO, FEATURES_MERCADO


# ----------------------------------------------------------------- utilidades
def brier(p: list[float], y: list[float]) -> float:
    return float(np.mean([(pi - yi) ** 2 for pi, yi in zip(p, y)]))


def _sigmoide(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -35, 35)))


# ------------------------------------------------- preprocesador (train-only)
@dataclass
class Preprocesador:
    """Imputa (mediana de train), añade indicadores de ausencia y estandariza.
    Se AJUSTA solo con train; `transform` aplica los parámetros congelados."""
    nombres: list[str]
    medianas: list[float]
    mu: list[float]
    sigma: list[float]

    @classmethod
    def ajustar(cls, filas: list[dict], nombres: list[str]) -> "Preprocesador":
        medianas = []
        for k in nombres:
            vals = [f[k] for f in filas if f.get(k) is not None]
            medianas.append(float(np.median(vals)) if vals else 0.0)
        # matriz imputada + indicadores
        X = cls._crudo(filas, nombres, medianas)
        mu = X.mean(axis=0).tolist()
        sigma = [s if s > 1e-12 else 1.0 for s in X.std(axis=0).tolist()]
        return cls(nombres=list(nombres), medianas=medianas, mu=mu, sigma=sigma)

    @staticmethod
    def _crudo(filas, nombres, medianas):
        filas_m = []
        for f in filas:
            fila = []
            for k, med in zip(nombres, medianas):
                v = f.get(k)
                falta = 1.0 if v is None else 0.0
                fila.append(med if v is None else float(v))
                fila.append(falta)  # indicador de ausencia por feature
            filas_m.append(fila)
        return np.array(filas_m, dtype=float)

    def transform(self, filas: list[dict]) -> np.ndarray:
        X = self._crudo(filas, self.nombres, self.medianas)
        mu = np.array(self.mu); sigma = np.array(self.sigma)
        return (X - mu) / sigma

    @property
    def dim(self) -> int:
        return len(self.nombres) * 2


# ------------------------------------------------------- logística L2 (scipy)
@dataclass
class LogisticaL2:
    w: list[float]        # pesos (sin intercepto)
    b: float              # intercepto
    C: float

    @staticmethod
    def _perdida_grad(theta, X, y, C):
        n, d = X.shape
        w = theta[:d]; b = theta[d]
        z = X @ w + b
        p = _sigmoide(z)
        eps = 1e-12
        ll = -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))
        reg = (1.0 / (2.0 * C * n)) * np.dot(w, w)   # L2 sin penalizar intercepto
        perdida = ll + reg
        g = p - y
        gw = X.T @ g / n + (1.0 / (C * n)) * w
        gb = np.mean(g)
        return perdida, np.concatenate([gw, [gb]])

    @classmethod
    def ajustar(cls, X: np.ndarray, y: np.ndarray, C: float) -> "LogisticaL2":
        n, d = X.shape
        theta0 = np.zeros(d + 1)
        res = optimize.minimize(
            cls._perdida_grad, theta0, args=(X, y, C), jac=True,
            method="L-BFGS-B", options={"maxiter": 500})
        theta = res.x
        return cls(w=theta[:d].tolist(), b=float(theta[d]), C=C)

    def proba(self, X: np.ndarray) -> np.ndarray:
        return _sigmoide(X @ np.array(self.w) + self.b)


# --------------------------------------------------------------- Platt (1-D)
@dataclass
class Platt:
    a: float
    b: float

    @classmethod
    def ajustar(cls, scores: list[float], y: list[float]) -> "Platt":
        X = np.array(scores, dtype=float).reshape(-1, 1)
        yy = np.array(y, dtype=float)
        lg = LogisticaL2.ajustar(X, yy, C=1e6)  # casi sin regularización (Platt clásico)
        return cls(a=lg.w[0], b=lg.b)

    def proba(self, scores: list[float]) -> np.ndarray:
        s = np.array(scores, dtype=float)
        return _sigmoide(self.a * s + self.b)


# ----------------------------------------------------- selección de C (folds)
def _folds_temporales(n: int, k: int = 4) -> list[tuple[list[int], list[int]]]:
    """Validación expanding-window purgada por orden temporal (filas ya ordenadas).
    Cada fold entrena con el pasado y valida con el bloque siguiente."""
    if n < k + 1:
        return [([i for i in range(n - 1)], [n - 1])] if n >= 2 else []
    tam = n // (k + 1)
    folds = []
    for j in range(1, k + 1):
        corte = tam * j
        tr = list(range(corte))
        va = list(range(corte, min(corte + tam, n)))
        if va:
            folds.append((tr, va))
    return folds


def seleccionar_C(filas: list[dict], nombres: list[str], y: list[float],
                  grid=(0.01, 0.1, 1.0)) -> float:
    """Elige C por Brier medio en folds de desarrollo; desempate por C menor."""
    n = len(filas)
    folds = _folds_temporales(n)
    if not folds:
        return min(grid)
    mejor_C, mejor_brier = min(grid), math.inf
    for C in sorted(grid):  # orden ascendente → desempate natural por C menor
        briers = []
        for tr, va in folds:
            pre = Preprocesador.ajustar([filas[i] for i in tr], nombres)
            Xtr = pre.transform([filas[i] for i in tr])
            Xva = pre.transform([filas[i] for i in va])
            ytr = np.array([y[i] for i in tr])
            lg = LogisticaL2.ajustar(Xtr, ytr, C)
            pva = lg.proba(Xva)
            briers.append(brier(pva.tolist(), [y[i] for i in va]))
        bm = float(np.mean(briers))
        if bm < mejor_brier - 1e-9:
            mejor_brier, mejor_C = bm, C
    return mejor_C


# --------------------------------------------------- ensamblado de features
def nombres_P1() -> list[str]:
    return list(FEATURES_MERCADO) + list(FEATURES_MACRO)


def nombres_P4() -> list[str]:
    """P4: mercado + macro + score contextual + 9 arquetipos + media y dispersión."""
    return (list(FEATURES_MERCADO) + list(FEATURES_MACRO)
            + ["llm_score_ctx"]
            + [f"arq_{a}" for a in ARQUETIPOS]
            + ["arq_media", "arq_desv"])


def nombres_P5() -> list[str]:
    from .config import ABMCfg
    return nombres_P4() + [f"abm_{k}" for k in ABMCfg().features]


def fila_features(reg: dict, cuales: str) -> dict:
    """Aplana un registro de desarrollo a un dict plano de features según el modelo.
    `cuales` ∈ {'P1','P4','P5'}. Valores ausentes quedan como None (los imputa el
    preprocesador). Controla que P4 y P5 compartan EXACTAMENTE las señales LLM."""
    m = reg.get("features_mercado", {}) or {}
    mac = reg.get("features_macro", {}) or {}
    out: dict = {}
    for k in FEATURES_MERCADO:
        out[k] = m.get(k)
    for k in FEATURES_MACRO:
        out[k] = mac.get(k)
    if cuales == "P1":
        return out
    llm = reg.get("llm", {}) or {}
    out["llm_score_ctx"] = llm.get("score_contextual")
    arqs = (llm.get("archetypes") or {})
    vals = []
    for a in ARQUETIPOS:
        v = arqs.get(a)
        out[f"arq_{a}"] = v
        if v is not None:
            vals.append(float(v))
    out["arq_media"] = float(np.mean(vals)) if vals else None
    out["arq_desv"] = float(np.std(vals)) if len(vals) >= 2 else 0.0
    if cuales == "P4":
        return out
    abm = reg.get("abm", {}) or {}
    from .config import ABMCfg
    for k in ABMCfg().features:
        out[f"abm_{k}"] = abm.get(k)
    return out


# ---------------------------------------------------------------- modelos
@dataclass
class ModeloBase:
    model_id: str

    def model_hash(self) -> str:
        raise NotImplementedError

    def proba_una(self, reg: dict) -> float:
        raise NotImplementedError


@dataclass
class ModeloP0(ModeloBase):
    p: float = 0.5

    @classmethod
    def entrenar(cls, y: list[float]) -> "ModeloP0":
        n = len(y); s = sum(y)
        return cls(model_id="P0", p=(s + 1.0) / (n + 2.0))  # beta-binomial(1,1)

    def model_hash(self) -> str:
        return hash_canonico({"id": "P0", "p": round(self.p, 10)})

    def proba_una(self, reg: dict) -> float:
        return self.p

    def a_dict(self) -> dict:
        return {"tipo": "P0", "model_id": self.model_id, "p": self.p}

    @classmethod
    def desde_dict(cls, d: dict) -> "ModeloP0":
        return cls(model_id=d["model_id"], p=d["p"])


@dataclass
class ModeloLogistico(ModeloBase):
    nombres: list[str] = None
    pre: Preprocesador = None
    lg: LogisticaL2 = None
    cuales: str = "P1"

    @classmethod
    def entrenar(cls, model_id: str, regs: list[dict], y: list[float],
                 cuales: str, grid=(0.01, 0.1, 1.0)) -> "ModeloLogistico":
        nombres = {"P1": nombres_P1, "P4": nombres_P4, "P5": nombres_P5}[cuales]()
        filas = [fila_features(r, cuales) for r in regs]
        C = seleccionar_C(filas, nombres, y, grid)
        pre = Preprocesador.ajustar(filas, nombres)
        X = pre.transform(filas)
        lg = LogisticaL2.ajustar(X, np.array(y), C)
        return cls(model_id=model_id, nombres=nombres, pre=pre, lg=lg, cuales=cuales)

    def model_hash(self) -> str:
        return hash_canonico({
            "id": self.model_id, "nombres": self.nombres, "C": self.lg.C,
            "w": [round(x, 8) for x in self.lg.w], "b": round(self.lg.b, 8)})

    def proba_una(self, reg: dict) -> float:
        fila = fila_features(reg, self.cuales)
        X = self.pre.transform([fila])
        return float(self.lg.proba(X)[0])

    def a_dict(self) -> dict:
        return {"tipo": "logistica", "model_id": self.model_id, "cuales": self.cuales,
                "nombres": self.nombres,
                "pre": {"nombres": self.pre.nombres, "medianas": self.pre.medianas,
                        "mu": self.pre.mu, "sigma": self.pre.sigma},
                "lg": {"w": self.lg.w, "b": self.lg.b, "C": self.lg.C}}

    @classmethod
    def desde_dict(cls, d: dict) -> "ModeloLogistico":
        pre = Preprocesador(**d["pre"])
        lg = LogisticaL2(w=d["lg"]["w"], b=d["lg"]["b"], C=d["lg"]["C"])
        return cls(model_id=d["model_id"], nombres=d["nombres"], pre=pre, lg=lg,
                   cuales=d["cuales"])


@dataclass
class ModeloPlatt(ModeloBase):
    campo: str = "score_titular"   # 'score_titular' (P2) o 'score_contextual' (P3)
    platt: Platt = None

    @classmethod
    def entrenar(cls, model_id: str, scores: list[float], y: list[float],
                 campo: str) -> "ModeloPlatt":
        return cls(model_id=model_id, campo=campo, platt=Platt.ajustar(scores, y))

    def model_hash(self) -> str:
        return hash_canonico({"id": self.model_id, "campo": self.campo,
                              "a": round(self.platt.a, 8), "b": round(self.platt.b, 8)})

    def proba_una(self, reg: dict) -> float:
        s = (reg.get("llm", {}) or {}).get(self.campo)
        if s is None:
            s = 0.0  # sin score → neutral; abstención la decide la economía, no el Brier
        return float(self.platt.proba([float(s)])[0])

    def a_dict(self) -> dict:
        return {"tipo": "platt", "model_id": self.model_id, "campo": self.campo,
                "platt": {"a": self.platt.a, "b": self.platt.b}}

    @classmethod
    def desde_dict(cls, d: dict) -> "ModeloPlatt":
        return cls(model_id=d["model_id"], campo=d["campo"],
                   platt=Platt(a=d["platt"]["a"], b=d["platt"]["b"]))


def cargar_modelo(d: dict):
    """Reconstruye cualquier modelo desde su dict serializado."""
    tipo = d["tipo"]
    if tipo == "P0":
        return ModeloP0.desde_dict(d)
    if tipo == "logistica":
        return ModeloLogistico.desde_dict(d)
    if tipo == "platt":
        return ModeloPlatt.desde_dict(d)
    raise ValueError(f"tipo de modelo desconocido: {tipo}")
