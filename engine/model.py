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

# Escala del consenso de la IA cuando se usa como "tono de la prensa" (ver
# _tono_de_titular). Es una perilla de MAGNITUD, no de dirección: subirla
# agranda el golpe del ambiente sin cambiar si el mercado sube o baja. Se
# calibra con los exámenes (el corrector), igual que los diales de mercado.
# 1ª ronda de exámenes (163 casos, índice+cripto): con 1.5 la DIRECCIÓN mejoró
# fuerte (índice 47%→62%) pero el enjambre se pasó ~2x en MAGNITUD (ratio
# real/sim ~0.5). Como el cambio de magnitud vino entero de este ambiente,
# bajamos la perilla ~×0.54 para volver a la escala calibrada (real/sim ~0.9).
# La dirección NO se toca (es el signo del consenso, no su tamaño).
# El valor por defecto vive también en config/perillas_calibracion.json
# (ganancia_consenso) para poder experimentarlo sin tocar código.
GANANCIA_CONSENSO = 0.8

# Fracción mínima de líderes que deben haber hablado con la IA real para
# confiar en su consenso como tono. Si la mayoría cayó al respaldo léxico
# (sin saldo de API), se usa el diccionario directo, que es justo para eso.
MINIMO_IA_CONSENSO = 0.5


class MercadoEnjambre(mesa.Model):
    MAX_HISTORIAL = 600  # cola de precios/retornos en sesiones largas

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
        # perfil de personalidad del mercado (índice por defecto); una noticia
        # de petróleo/oro/cripto lo cambia y con él la reacción del enjambre
        from brains.mercado import perfil_de
        self.perfil = perfil_de("indice")
        self.intensidad_shock = 1.0  # >1 solo si el impacto no lineal se recortó
        self.historial_precios: list[float] = [precio_inicial]
        self.retornos: list[float] = []
        self.flujo_compras: list[float] = []  # volumen agresor comprador por tick
        self.flujo_ventas: list[float] = []
        # cola del rumor: (tick_entrega, agente, valor, salto)
        self.cola_senales: list[tuple[int, AgenteBase, float, int]] = []

        self._crear_agentes(ruta_config)
        self._agentes_por_id = {a.unique_id: a for a in self.agents}
        self._lideres = [a for a in self.agents if isinstance(a, LiderOpinion)]
        # orden estable de creación (tipos 1-12 y al final los 100 líderes):
        # es el contrato con el frontend para el streaming por WebSocket
        self.agentes_ordenados = sorted(self.agents, key=lambda a: a.unique_id)

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
        Cada líder forma su señal y la propaga por la red de influencia.

        El tono AMBIENTE (lo que sienten todos) pasa por zona_muerta:
        en baseline no hace nada; en v1c silencia titulares tibios.
        Los líderes oyen el shock completo — no se les tapa la boca.
        """
        from brains.impacto import factor_residual, transformar_senal, zona_muerta

        self.intensidad_shock = factor_residual(sentimiento, self.perfil)
        shock = transformar_senal(sentimiento, self.perfil)
        ambiente = zona_muerta(shock, self.perfil)
        self.sentimiento = max(-1.0, min(1.0, self.sentimiento + ambiente))
        for lider in self._lideres:
            lider.recibir_noticia(shock)
        self._propagar_desde_lideres()

    def aplicar_titular(self, titular: str, respuestas: list[dict] | None = None,
                        perfil: dict | None = None) -> list[dict]:
        """Inyecta una noticia REAL: los 100 líderes la leen (LLM con
        fallback léxico), forman su señal y la propagan por la red.
        El servidor puede pasar `respuestas` ya calculadas (vía async) y el
        `perfil` de mercado (índice/petróleo/oro/cripto/acción) ya clasificado."""
        if respuestas is None:
            from brains.cerebro import analizar_titular
            from brains import reparto

            # 1000 líderes comparten ~110 cerebros (presupuesto de la biblia)
            consultas, asignacion = reparto.planificar(self._lideres, lambda uid: uid)
            respuestas_cerebros = analizar_titular(titular, consultas)
            respuestas = reparto.expandir(respuestas_cerebros, asignacion)
        if perfil is not None:
            self.perfil = perfil
        from brains.impacto import ruido_lider_sigma
        sigma = ruido_lider_sigma()
        for lider, respuesta in zip(self._lideres, respuestas):
            senal = respuesta["senal"]
            if sigma:
                senal = max(-1.0, min(1.0, senal + self.random.gauss(0.0, sigma)))
            lider.senal = senal
            lider.confianza = respuesta["confianza"]
            lider.frase = respuesta["frase"]
        # el "tono de la prensa": el ambiente de fondo que sienten todos los
        # agentes (todos leen la misma noticia). Antes lo ponía un diccionario
        # de palabras; ahora lo pone la LECTURA REAL de la IA (el consenso de
        # los líderes que hablaron con Claude), que entiende el SIGNIFICADO del
        # titular donde el diccionario se equivocaba ("recortan aranceles" es
        # bueno, "wipes out $2 trillion" es malo). Las opiniones expertas de
        # cada líder siguen viajando aparte, por la red de influencia.
        tono = self._aplicar_perfil(self._tono_de_titular(titular, respuestas))
        self.sentimiento = max(-1.0, min(1.0, self.sentimiento + tono))
        self._propagar_desde_lideres()
        return respuestas

    def _tono_de_titular(self, titular: str, respuestas: list[dict]) -> float:
        """El tono de fondo del mercado a partir de la noticia ∈ [-1, +1].

        Prioridad a la LECTURA de la IA: el promedio de las señales de los
        líderes, ponderado por su confianza. La IA entiende el sentido del
        titular; el diccionario léxico solo cuenta palabras y fallaba en
        noticias compuestas (leía "slash tariffs" como pánico cuando es alza).

        Solo pesan los líderes que hablaron con la IA de verdad (fuente
        api/cache). Si la mayoría usó el respaldo léxico (sin saldo de API),
        se vuelve al diccionario — que es exactamente para lo que existe.
        """
        from brains.fallback import sentimiento_lexico
        from brains.impacto import ganancia_consenso, zona_muerta

        ia = [r for r in respuestas if r.get("fuente") in ("api", "cache")]
        peso = sum(r["confianza"] for r in ia)
        if len(ia) < len(respuestas) * MINIMO_IA_CONSENSO or peso <= 0:
            crudo = sentimiento_lexico(titular)  # la IA no opinó lo suficiente
        else:
            consenso = sum(r["senal"] * r["confianza"] for r in ia) / peso
            crudo = max(-1.0, min(1.0, consenso * ganancia_consenso()))
        return zona_muerta(crudo, self.perfil)

    def _aplicar_perfil(self, tono: float) -> float:
        """La personalidad del mercado transforma el tono de la noticia.

        - sensibilidad: cuánto mueve el sentimiento a este mercado.
        - refugio (oro): el miedo (tono<0) se refleja parcialmente a compra;
          con refugio=0.5 el miedo se neutraliza, >0.5 lo hace SUBIR.
        - impacto no lineal: umbral de pánico + asimetría (brains/impacto.py).
        """
        from brains.impacto import calcular_impacto, factor_residual

        tono *= self.perfil.get("sensibilidad", 1.0)
        refugio = self.perfil.get("refugio", 0.0)
        if refugio and tono < 0:
            tono *= (1.0 - 2.0 * refugio)
        self.intensidad_shock = factor_residual(tono, self.perfil)
        return max(-1.0, min(1.0, calcular_impacto(tono, self.perfil)))

    def _propagar_desde_lideres(self) -> None:
        """La señal de cada líder viaja a sus seguidores con retardo de
        1-4 ticks y atenuación (ganancia_contagio) por salto — esto crea la ola visual."""
        from brains.impacto import ganancia_contagio

        sensibilidad = self.perfil.get("sensibilidad", 1.0)
        contagio = ganancia_contagio(self.perfil)
        factor = getattr(self, "intensidad_shock", 1.0)
        for lider in self._lideres:
            if abs(lider.senal) < 0.05:
                continue
            # la personalidad del mercado escala cuánto arrastra cada líder
            valor = lider.senal * lider.confianza * contagio * sensibilidad * factor
            for seguidor in lider.seguidores:
                retardo = self.random.randint(1, 4)
                self.cola_senales.append((self.tick + retardo, seguidor, valor, 1))

    def _entregar_senales(self) -> None:
        """Entrega el rumor que vence este tick y lo reenvía a los pares
        (segundo salto, atenuado otra vez; ahí muere la cadena)."""
        from brains.impacto import ganancia_contagio

        contagio = ganancia_contagio(self.perfil)
        pendientes = []
        for tick_entrega, agente, valor, salto in self.cola_senales:
            if tick_entrega > self.tick:
                pendientes.append((tick_entrega, agente, valor, salto))
                continue
            agente.senal_social = max(-1.0, min(1.0, agente.senal_social + valor))
            if salto == 1:
                for par in agente.pares:
                    retardo = self.random.randint(1, 4)
                    pendientes.append((self.tick + retardo, par, valor * contagio, 2))
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
        # en sesiones largas (modo observatorio) las listas no crecen sin fin:
        # los agentes solo miran ventanas cortas, así que basta la cola reciente
        if len(self.historial_precios) > self.MAX_HISTORIAL:
            recorte = len(self.historial_precios) - self.MAX_HISTORIAL
            del self.historial_precios[:recorte]
            del self.retornos[:recorte]
            del self.flujo_compras[:recorte]
            del self.flujo_ventas[:recorte]

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
