"""MercadoEnjambre — el modelo central de la simulación.

Carga la mezcla de 5.000 agentes desde config/agentes.json, corre el
mercado tick a tick y expone las series (precio, retornos, flujo) que
consumen la validación y, más adelante, el WebSocket hacia el frontend.
"""

import json
from pathlib import Path

import mesa

from agents.base import AgenteBase
from agents.lider import LiderOpinion
from agents.reglas import (
    Arbitrajista,
    BuyAndHold,
    Contrarian,
    EjecutorTWAP,
    FomoRetail,
    FondoPasivo,
    Fundamentalista,
    Manada,
    MarketMaker,
    Miedoso,
    NoiseTrader,
    QuantMomentum,
)
from market.order_book import LibroOrdenes

RUTA_CONFIG = Path(__file__).parent / "config" / "agentes.json"

CLASES_POR_TIPO = {
    "fundamentalista": Fundamentalista,
    "quant_momentum": QuantMomentum,
    "fondo_pasivo": FondoPasivo,
    "market_maker": MarketMaker,
    "ejecutor_twap": EjecutorTWAP,
    "arbitrajista": Arbitrajista,
    "noise_trader": NoiseTrader,
    "manada": Manada,
    "fomo": FomoRetail,
    "miedoso": Miedoso,
    "contrarian": Contrarian,
    "buy_and_hold": BuyAndHold,
}

CAPITAL_BASE = 10_000.0  # capital de un agente retail 1x


class MercadoEnjambre(mesa.Model):
    def __init__(
        self,
        seed: int | None = None,
        precio_inicial: float = 100.0,
        ticks_horizonte: int = 400,
        ruta_config: Path = RUTA_CONFIG,
    ):
        super().__init__(seed=seed)
        self.ticks_horizonte = ticks_horizonte
        self.libro = LibroOrdenes(precio_inicial)
        self.libro.notificar_ejecucion = self._notificar_ejecucion

        self.tick = 0
        self.sentimiento = 0.0  # sentimiento global de la noticia, decae solo
        self.historial_precios: list[float] = [precio_inicial]
        self.retornos: list[float] = []
        self.flujo_compras: list[float] = []  # volumen agresor comprador por tick
        self.flujo_ventas: list[float] = []

        self._crear_agentes(ruta_config)
        self._agentes_por_id = {a.unique_id: a for a in self.agents}

    # ---------- construcción ----------

    def _crear_agentes(self, ruta_config: Path) -> None:
        with open(ruta_config, encoding="utf-8") as f:
            config = json.load(f)
        for tipo in config["tipos"]:
            capital = tipo["capital_relativo"] * CAPITAL_BASE
            if tipo["id"] == "lider_opinion":
                for arquetipo in tipo["arquetipos"]:
                    for _ in range(arquetipo["cantidad"]):
                        LiderOpinion(self, capital, arquetipo["id"])
            else:
                clase = CLASES_POR_TIPO[tipo["id"]]
                for _ in range(tipo["cantidad"]):
                    clase(self, capital)

    # ---------- noticia ----------

    def aplicar_noticia(self, sentimiento: float) -> None:
        """Inyecta una noticia. En la Etapa 2, el sentimiento por líder
        vendrá del LLM; aquí usamos la señal precomputada de cada líder."""
        self.sentimiento = max(-1.0, min(1.0, self.sentimiento + sentimiento))
        for agente in self.agents:
            if isinstance(agente, LiderOpinion):
                agente.recibir_noticia(sentimiento)

    # ---------- ciclo ----------

    def step(self) -> None:
        self.libro.reiniciar_tick(self.tick)
        self.agents.shuffle_do("step")
        self.tick += 1
        # el cierre del tick es la última transacción real: una foto
        # puntual de dónde se cruzó de verdad la oferta con la demanda
        precio = self.libro.ultimo_precio if self.libro.volumen_tick > 0 else self.historial_precios[-1]
        anterior = self.historial_precios[-1]
        self.historial_precios.append(precio)
        self.retornos.append((precio - anterior) / anterior)
        self.flujo_compras.append(self.libro.volumen_compras_tick)
        self.flujo_ventas.append(self.libro.volumen_ventas_tick)
        self.sentimiento *= 0.95  # la noticia pierde fuerza cada tick

    def correr(self, ticks: int) -> None:
        for _ in range(ticks):
            self.step()

    # ---------- series que consultan los agentes ----------

    def retorno_acumulado(self, n: int) -> float | None:
        """Retorno del precio en los últimos n ticks."""
        if len(self.historial_precios) <= n:
            return None
        return self.historial_precios[-1] / self.historial_precios[-1 - n] - 1

    def volatilidad_reciente(self, n: int) -> float:
        """Desviación estándar de los últimos n retornos."""
        if len(self.retornos) < 2:
            return 0.0
        ventana = self.retornos[-n:]
        media = sum(ventana) / len(ventana)
        return (sum((r - media) ** 2 for r in ventana) / len(ventana)) ** 0.5

    def fraccion_compras(self, n: int) -> float | None:
        """Fracción del volumen reciente que fue comprador agresor."""
        if not self.flujo_compras:
            return None
        compras = sum(self.flujo_compras[-n:])
        ventas = sum(self.flujo_ventas[-n:])
        total = compras + ventas
        # con volumen insignificante no hay señal de manada que leer
        if total < 100:
            return None
        return compras / total

    # ---------- interno ----------

    def _notificar_ejecucion(self, agente_id: int, lado: str, cantidad: float, precio: float) -> None:
        agente: AgenteBase = self._agentes_por_id[agente_id]
        agente.aplicar_ejecucion(lado, cantidad, precio)
