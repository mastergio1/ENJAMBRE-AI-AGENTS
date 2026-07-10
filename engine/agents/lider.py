"""Tipo 13 — Líder de opinión (LLM).

En la Etapa 1 es un esqueleto: guarda una señal y opera según ella.
En la Etapa 2 la señal vendrá de una llamada real a la API de Anthropic
(engine/brains/) y se propagará por la red de influencia (engine/network/).
"""

from .base import AgenteBase


class LiderOpinion(AgenteBase):
    """Lee la noticia; su señal se propaga a sus seguidores."""

    def __init__(self, model, capital, arquetipo: str):
        super().__init__(model, capital)
        self.arquetipo = arquetipo
        self.senal = 0.0       # ∈ [-1, +1], la fija aplicar_noticia()
        self.confianza = 0.7   # ∈ [0, 1], modula cuánto arrastra
        self.frase = ""        # la escribirá el LLM en la Etapa 2
        self.desfase = self.model.random.randint(0, 2)

    def recibir_noticia(self, sentimiento: float) -> None:
        """Etapa 1: señal precomputada = sentimiento ± ruido personal.
        En la Etapa 2 esto se reemplaza por la respuesta del LLM por arquetipo."""
        cruda = sentimiento * self.model.random.gauss(1.0, 0.3)
        # sesgo de negatividad: las malas noticias pesan más que las buenas
        # (en la Etapa 2 esto emerge de los arquetipos Doomer/Miedoso reales)
        if cruda < 0:
            cruda *= 1.4
        self.senal = max(-1.0, min(1.0, cruda))

    def step(self):
        if abs(self.senal) < 0.05:
            return
        cantidad = abs(self.senal) * self.confianza * 0.25 * self.capital_inicial / self.precio
        if self.senal > 0:
            self.comprar_mercado(cantidad)
        else:
            self.vender_mercado(cantidad)
        self.senal *= 0.6  # actúa fuerte y rápido; la opinión se agota pronto
