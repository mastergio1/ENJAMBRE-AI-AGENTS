"""L1/L9 — Manifiesto del experimento, validación e identidad de eventos.

El manifiesto CONGELA todos los parámetros del protocolo ANTES de T0 (Parte I). Una
vez congelado, su hash sella la configuración; cambiarlo invalida el experimento. Aquí
viven también la identidad determinista de eventos (`event_id`) y el hashing canónico.

Nada en este módulo contacta la red ni gasta dinero. Es pura definición y validación.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from . import VERSION

# Los 9 arquetipos EXACTOS del vector estructurado P3 (I.4.1). Orden congelado.
ARQUETIPOS = (
    "institucional_frio", "quant_esceptico", "fomo_evangelista", "doomer",
    "contrarian_sabio", "macro_trader", "influencer_optimista", "value_paciente",
    "doomer_selectivo",
)

# Categorías macro congeladas para el universo de titulares (I.4).
CATEGORIAS_MACRO = ("CPI", "PCE", "empleo", "FOMC", "PIB", "ventas", "PMI")
TOKEN_SIN_EVENTO = "NO_MACRO_EVENT"

MODELOS = ("P0", "P1", "P2", "P3", "P4", "P5")


def hash_canonico(obj) -> str:
    """SHA-256 de la serialización JSON canónica (claves ordenadas, sin espacios)."""
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                   default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def event_id(symbol: str, emision: str, horizonte_sesiones: int, version: str = "v1") -> str:
    """Identidad determinista de evento (I.8): `SPY:YYYY-MM-DD:2D:v1`.

    `emision` = fecha de la sesión de emisión (identificador de sesión, no día natural).
    """
    return f"{symbol}:{emision}:{horizonte_sesiones}D:{version}"


@dataclass(frozen=True)
class Bootstrap:
    block_sessions: int = 5
    resamples: int = 10000
    seed: int = 20261124
    block_sensitivity: int = 10  # bloque alternativo para sensibilidad


@dataclass(frozen=True)
class Economia:
    capital: float = 10000.0        # cartera ficticia; parámetro de test, NO del usuario
    umbral_largo: float = 0.55
    umbral_corto: float = 0.45
    coste_base_bps: float = 5.0     # por lado sobre notional
    coste_estres_bps: float = 10.0
    max_tramo_frac: float = 0.5     # tamaño máximo por tramo = 1/2 equity
    max_bruto: float = 1.0          # exposición bruta agregada <= 100%
    variante: str = "long_short"    # o "long_flat" si no se modela el corto
    tolerancia_drawdown_pp: float = 2.0


@dataclass(frozen=True)
class ModelosCfg:
    l2_grid: tuple = (0.01, 0.1, 1.0)   # C de regularización (I.6)
    desempate_C: str = "menor"          # desempate por C menor
    prob_empate: float = 0.5            # p=0.5 -> no operar / dir 0


@dataclass(frozen=True)
class ABMCfg:
    seeds: tuple = (1701, 1702, 1703)
    config_agentes: str = "config/agentes.json"
    # Features candidatas congeladas (I.5): retorno final mediano, dispersión, vol
    # simulada mediana, desequilibrio de volumen agresor, max drawdown sim, rango.
    features: tuple = (
        "ret_final_mediano", "dispersion_ret_final", "vol_sim_mediana",
        "desequilibrio_agresor", "max_drawdown_sim", "rango_sim",
    )
    confianza_lider: float = 0.5        # confianza común congelada (I.4.1)


@dataclass(frozen=True)
class Noticias:
    max_titulares: int = 5
    categorias: tuple = CATEGORIAS_MACRO
    token_sin_evento: str = TOKEN_SIN_EVENTO


@dataclass
class Manifiesto:
    """Manifiesto congelable del experimento. Todos los parámetros del protocolo."""
    experiment_id: str
    symbol: str = "SPY"
    protocolo_version: str = VERSION
    horizonte_sesiones: int = 2
    cutoff_min_antes_cierre: int = 30
    deadline_min_despues_cutoff: int = 10
    ventana_meses: int = 6
    t0: str | None = None               # ISO date; se fija al freeze
    t1: str | None = None               # T0 + 6 meses; derivado
    min_sesiones: int = 100
    min_cobertura: float = 0.90
    delta_min: float = 0.005
    presupuesto_usd: float = 300.0
    capital_real_usd: float = 0.0       # SIEMPRE 0: solo paper trading
    b_star: str | None = None           # mejor no-ABM preseleccionado en desarrollo
    bootstrap: Bootstrap = field(default_factory=Bootstrap)
    economia: Economia = field(default_factory=Economia)
    modelos: ModelosCfg = field(default_factory=ModelosCfg)
    abm: ABMCfg = field(default_factory=ABMCfg)
    noticias: Noticias = field(default_factory=Noticias)
    # Hashes de congelación (se rellenan en freeze; None hasta entonces).
    hash_datos: str | None = None
    hash_codigo: str | None = None
    hash_prompts: str | None = None
    hash_artefactos: str | None = None
    hash_calendario: str | None = None
    code_commit: str | None = None

    # ------------------------------------------------------------------ carga
    @classmethod
    def desde_dict(cls, d: dict) -> "Manifiesto":
        d = dict(d)
        if "bootstrap" in d and isinstance(d["bootstrap"], dict):
            d["bootstrap"] = Bootstrap(**d["bootstrap"])
        if "economia" in d and isinstance(d["economia"], dict):
            d["economia"] = Economia(**d["economia"])
        if "modelos" in d and isinstance(d["modelos"], dict):
            m = dict(d["modelos"])
            for k in ("l2_grid",):
                if k in m and isinstance(m[k], list):
                    m[k] = tuple(m[k])
            d["modelos"] = ModelosCfg(**m)
        if "abm" in d and isinstance(d["abm"], dict):
            a = dict(d["abm"])
            for k in ("seeds", "features"):
                if k in a and isinstance(a[k], list):
                    a[k] = tuple(a[k])
            d["abm"] = ABMCfg(**a)
        if "noticias" in d and isinstance(d["noticias"], dict):
            n = dict(d["noticias"])
            if "categorias" in n and isinstance(n["categorias"], list):
                n["categorias"] = tuple(n["categorias"])
            d["noticias"] = Noticias(**n)
        validos = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in validos})

    @classmethod
    def cargar(cls, ruta: str | Path) -> "Manifiesto":
        return cls.desde_dict(json.loads(Path(ruta).read_text(encoding="utf-8")))

    def a_dict(self) -> dict:
        return asdict(self)

    def guardar(self, ruta: str | Path) -> None:
        Path(ruta).write_text(
            json.dumps(self.a_dict(), indent=2, ensure_ascii=False, default=str),
            encoding="utf-8")

    # ------------------------------------------------------------- validación
    def validar(self, *, exigir_freeze: bool = False) -> list[str]:
        """Devuelve lista de problemas (vacía = válido). `exigir_freeze` pide los
        campos que solo existen tras congelar (T0, B*, hashes)."""
        p: list[str] = []
        if not self.experiment_id:
            p.append("experiment_id vacío")
        if self.symbol != "SPY":
            p.append("symbol debe ser SPY (instrumento confirmatorio único)")
        if self.horizonte_sesiones != 2:
            p.append("horizonte debe ser 2 sesiones (contrato congelado)")
        if self.capital_real_usd != 0.0:
            p.append("capital_real_usd DEBE ser 0 (solo paper trading)")
        if not (0 < self.min_cobertura <= 1):
            p.append("min_cobertura fuera de (0,1]")
        if self.delta_min != 0.005:
            p.append("delta_min debe ser 0.005 (congelado)")
        if self.economia.umbral_corto >= self.economia.umbral_largo:
            p.append("umbral_corto debe ser < umbral_largo")
        if self.bootstrap.seed != 20261124:
            p.append("seed de bootstrap debe ser 20261124 (congelado)")
        if self.bootstrap.block_sessions != 5:
            p.append("bloque de bootstrap debe ser 5 sesiones (congelado)")
        if tuple(self.modelos.l2_grid) != (0.01, 0.1, 1.0):
            p.append("grid L2 debe ser {0.01,0.1,1} (congelado)")
        if self.economia.variante not in ("long_short", "long_flat"):
            p.append("variante económica inválida")
        if exigir_freeze:
            if not self.t0:
                p.append("T0 sin fijar (freeze)")
            if not self.t1:
                p.append("T1 sin derivar (freeze)")
            if not self.b_star or self.b_star not in MODELOS:
                p.append("B* sin preseleccionar o inválido (freeze)")
            for h in ("hash_datos", "hash_codigo", "hash_prompts",
                      "hash_calendario", "code_commit"):
                if not getattr(self, h):
                    p.append(f"{h} sin fijar (freeze)")
            # coherencia T1 = T0 + ventana_meses
            if self.t0 and self.t1:
                t0 = dt.date.fromisoformat(self.t0)
                t1_esp = _sumar_meses(t0, self.ventana_meses)
                if dt.date.fromisoformat(self.t1) != t1_esp:
                    p.append(f"T1 incoherente: esperado {t1_esp.isoformat()}")
        return p

    def derivar_t1(self) -> str:
        if not self.t0:
            raise ValueError("T0 sin fijar")
        return _sumar_meses(dt.date.fromisoformat(self.t0), self.ventana_meses).isoformat()

    def hash_config(self) -> str:
        """Hash de la configuración SIN los hashes de congelación ni el commit
        (para evitar dependencia circular)."""
        d = self.a_dict()
        for k in ("hash_datos", "hash_codigo", "hash_prompts", "hash_artefactos",
                  "hash_calendario", "code_commit"):
            d.pop(k, None)
        return hash_canonico(d)


def _sumar_meses(d: dt.date, meses: int) -> dt.date:
    """Suma `meses` meses naturales (ancla fin de mes al día válido más cercano)."""
    m = d.month - 1 + meses
    anio = d.year + m // 12
    mes = m % 12 + 1
    # último día del mes destino
    if mes == 12:
        ult = 31
    else:
        ult = (dt.date(anio, mes + 1, 1) - dt.timedelta(days=1)).day
    return dt.date(anio, mes, min(d.day, ult))
