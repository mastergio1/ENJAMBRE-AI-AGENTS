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
        # cola del rumor: (tick_entrega, agente, valor, salto)
        self.cola_senales: list[tuple[int, AgenteBase, float, int]] = []

        self._crear_agentes(ruta_config)
        self._agentes_por_id = {a.unique_id: a for a in self.agents}
        self._lideres = [a for a in self.agents if isinstance(a, LiderOpinion)]

        from network.red import construir_red

        construir_red(self)

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
        """Inyecta una noticia como número (para tests y calibración).
        Cada líder forma su señal y la propaga por la red de influencia."""
        self.sentimiento = max(-1.0, min(1.0, self.sentimiento + sentimiento))
        for lider in self._lideres:
            lider.recibir_noticia(sentimiento)
        self._propagar_desde_lideres()

    def aplicar_titular(self, titular: str) -> list[dict]:
        """Inyecta una noticia REAL: los 100 líderes la leen (LLM con
        fallback léxico), forman su señal y la propagan por la red."""
        from brains.cerebro import analizar_titular

        consultas = [(lider.unique_id, lider.arquetipo) for lider in self._lideres]
        respuestas = analizar_titular(titular, consultas)
        for lider, respuesta in zip(self._lideres, respuestas):
            lider.senal = respuesta["senal"]
            lider.confianza = respuesta["confianza"]
            lider.frase = respuesta["frase"]
        # el "tono de la prensa": el titular crudo marca el ambiente del
        # mercado (todos leen la misma noticia); las opiniones expertas
        # de los líderes viajan aparte, por la red de influencia
        from brains.fallback import sentimiento_lexico

        tono = sentimiento_lexico(titular)
        self.sentimiento = max(-1.0, min(1.0, self.sentimiento + tono))
        self._propagar_desde_lideres()
        return respuestas

    def _propagar_desde_lideres(self) -> None:
        """La señal de cada líder viaja a sus seguidores con retardo de
        1-4 ticks y atenuación 0.7 por salto — esto crea la ola visual."""
        for lider in self._lideres:
            if abs(lider.senal) < 0.05:
                continue
            valor = lider.senal * lider.confianza * 0.7
            for seguidor in lider.seguidores:
                retardo = self.random.randint(1, 4)
                self.cola_senales.append((self.tick + retardo, seguidor, valor, 1))

    def _entregar_senales(self) -> None:
        """Entrega el rumor que vence este tick y lo reenvía a los pares
        (segundo salto, atenuado otra vez; ahí muere la cadena)."""
        pendientes = []
        for tick_entrega, agente, valor, salto in self.cola_senales:
            if tick_entrega > self.tick:
                pendientes.append((tick_entrega, agente, valor, salto))
                continue
            agente.senal_social = max(-1.0, min(1.0, agente.senal_social + valor))
            if salto == 1:
                for par in agente.pares:
                    retardo = self.random.randint(1, 4)
                    pendientes.append((self.tick + retardo, par, valor * 0.7, 2))
        self.cola_senales = pendientes

    # ---------- ciclo ----------

    def step(self) -> None:
        self.tick += 1
        self.libro.reiniciar_tick(self.tick)
        self._entregar_senales()  # el rumor de hoy llega antes de operar
        self.agents.shuffle_do("step")
        # el rumor recibido se desvanece rápido (lo fresco es lo que arrastra)
        for agente in self.agents:
            if agente.senal_social != 0.0:
                agente.senal_social *= 0.75
                if abs(agente.senal_social) < 0.01:
                    agente.senal_social = 0.0
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
