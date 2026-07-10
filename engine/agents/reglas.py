"""Los 12 tipos de agentes de reglas de El Enjambre (CLAUDE.md sección 4).

Cada agente se instancia con sus parámetros base ± ruido gaussiano
(σ = 15%) para que no haya dos idénticos.
"""

from .base import AgenteBase


class Fundamentalista(AgenteBase):
    """Tipo 1 — Ancla el precio al valor "justo". El freno del sistema."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # valor fundamental con ruido idiosincrático
        self.valor = model.libro.ultimo_precio * self.model.random.gauss(1.0, 0.04)
        self.periodo = self.model.random.randint(10, 20)
        self.proximo_tick = self.model.random.randint(0, self.periodo)

    def step(self):
        # la noticia actualiza el valor fundamental lentamente (ponderación 0.3)
        if abs(self.model.sentimiento) > 0.01:
            self.valor *= 1 + 0.3 * self.model.sentimiento * 0.01
        if self.model.tick < self.proximo_tick:
            return
        self.proximo_tick = self.model.tick + self.periodo
        # opera solo cuando el precio se aleja de su valor: es el freno del sistema
        self.model.libro.cancelar_ordenes(self.unique_id)
        if self.precio < self.valor * 0.95:
            self.colocar_orden("compra", self.precio * 1.002, 0.25 * self.efectivo / self.precio)
        elif self.precio > self.valor * 1.05:
            self.colocar_orden("venta", self.precio * 0.998, 0.25 * self.acciones)


class QuantMomentum(AgenteBase):
    """Tipo 2 — Sigue tendencias con disciplina mecánica. Sin emociones."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.ventana_corta = 5
        self.ventana_larga = 20
        self.stop_loss = self.ruido(0.03)
        self.precio_entrada = None
        self.enfriamiento_hasta = 0

    def step(self):
        precios = self.model.historial_precios
        if len(precios) < self.ventana_larga or self.model.tick < self.enfriamiento_hasta:
            return
        corta = sum(precios[-self.ventana_corta:]) / self.ventana_corta
        larga = sum(precios[-self.ventana_larga:]) / self.ventana_larga
        if self.precio_entrada is None and corta > larga * 1.002:
            # entrada escalonada: no todos los fondos disparan el mismo tick
            if self.model.random.random() > 0.5:
                return
            cantidad = 0.1 * self.efectivo / self.precio
            self.comprar_mercado(cantidad)
            self.precio_entrada = self.precio
        elif self.precio_entrada is not None:
            stop = self.precio < self.precio_entrada * (1 - self.stop_loss)
            tendencia_rota = corta < larga * 0.998
            if stop or tendencia_rota:
                self.vender_mercado(self.acciones * 0.8)
                self.precio_entrada = None
                # tras salir, espera antes de buscar la próxima tendencia
                self.enfriamiento_hasta = self.model.tick + self.model.random.randint(5, 15)


class FondoPasivo(AgenteBase):
    """Tipo 3 — Compra constante pase lo que pase. El flujo 401k/AFP."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.periodo = max(2, round(self.ruido(10)))
        self.desfase = self.model.random.randint(0, self.periodo - 1)

    def step(self):
        if (self.model.tick + self.desfase) % self.periodo == 0:
            self.comprar_mercado(0.004 * self.capital_inicial / self.precio)


class MarketMaker(AgenteBase):
    """Tipo 4 — Cotiza compra y venta siempre. En pánico amplía el spread ×3."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.spread_base = self.ruido(0.002)
        self.umbral_panico = self.ruido(0.008)  # volatilidad por tick
        self.acciones_objetivo = self.acciones

    def step(self):
        self.model.libro.cancelar_ordenes(self.unique_id)
        vol = self.model.volatilidad_reciente(10)
        spread = max(self.spread_base, 3 * vol)
        if vol > self.umbral_panico:
            spread *= 3  # evaporación de liquidez en crashes
        spread = min(spread, 0.08)  # ni en pánico cotiza precios absurdos
        # sesgo por inventario FUERTE: si el flujo lo desequilibra, mueve el
        # precio de inmediato al nivel donde aparece la contraparte. Un ajuste
        # lento crearía tendencias predecibles (y un mercado predecible es falso).
        desbalance = (self.acciones - self.acciones_objetivo) / max(self.acciones_objetivo, 1)
        centro = self.precio * (1 - 0.12 * max(-1.5, min(1.5, desbalance)))
        tamano = 0.15 * self.capital_inicial / self.precio
        self.colocar_orden("compra", centro * (1 - spread / 2), tamano)
        self.colocar_orden("venta", centro * (1 + spread / 2), tamano)


class EjecutorTWAP(AgenteBase):
    """Tipo 5 — Ejecuta una orden grande en rebanadas iguales toda la sesión."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.lado = self.model.random.choice(["compra", "venta"])
        total = 0.4 * self.capital_inicial / model.libro.ultimo_precio
        self.rebanada = total / model.ticks_horizonte

    def step(self):
        if self.lado == "compra":
            self.comprar_mercado(self.rebanada)
        else:
            self.vender_mercado(self.rebanada)


class Arbitrajista(AgenteBase):
    """Tipo 6 — Corrige desviaciones rápidas del precio. Opera cada tick."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.umbral = self.ruido(0.006)

    def step(self):
        precios = self.model.historial_precios
        if len(precios) < 4:
            return
        # no todos los arbitrajistas ven la misma oportunidad al mismo tiempo
        if self.model.random.random() > 0.8:
            return
        # referencia de MUY corto plazo: desvanece los empujones del flujo
        # que no tienen información detrás (borra la predictibilidad)
        referencia = sum(precios[-4:-1]) / 3
        desviacion = (self.precio - referencia) / referencia
        if abs(desviacion) < self.umbral:
            return
        cantidad = min(abs(desviacion) * 5, 0.2) * self.capital_inicial / self.precio
        if desviacion > 0:
            self.vender_mercado(cantidad)
        else:
            self.comprar_mercado(cantidad)


class NoiseTrader(AgenteBase):
    """Tipo 7 — Ruido browniano de fondo. La textura del mercado."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.prob_operar = self.ruido(0.12)
        # solo el 20% es sensible al sentimiento global
        self.sensible = self.model.random.random() < 0.2

    def step(self):
        if self.model.random.random() > self.prob_operar:
            return
        prob_compra = 0.5
        if self.sensible:
            prob_compra += 0.1 * self.model.sentimiento
        cantidad = 0.04 * self.capital_inicial / self.precio
        if self.model.random.random() < prob_compra:
            self.comprar_mercado(cantidad)
        else:
            self.vender_mercado(cantidad)


class Manada(AgenteBase):
    """Tipo 8 — Copia a su red. Umbrales heterogéneos crean cascadas tipo ola."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        # umbral variado (40%-80%): crucial para cascadas graduales
        self.umbral = self.model.random.uniform(0.4, 0.8)
        self.espera_hasta = 0

    def step(self):
        if self.model.tick < self.espera_hasta:
            return
        # Etapa 1: observa el flujo agregado reciente como proxy de su red.
        # En la Etapa 2 esto se reemplaza por sus vecinos reales del grafo.
        frac_compras = self.model.fraccion_compras(3)
        if frac_compras is None:
            return
        if frac_compras > self.umbral:
            self.comprar_mercado(0.05 * self.efectivo / self.precio)
        elif (1 - frac_compras) > self.umbral:
            # vende más pesado de lo que compra: el miedo corre más que la codicia
            self.vender_mercado(0.15 * self.acciones)
        else:
            return
        # espera corta y variada: la cascada es rápida pero no un solo bloque
        self.espera_hasta = self.model.tick + self.model.random.randint(1, 3)


class FomoRetail(AgenteBase):
    """Tipo 9 — Persigue subidas, entra tarde y agresivo, vende en pánico."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.umbral_subida = self.ruido(0.02)
        self.precio_entrada = None

    def step(self):
        if self.precio_entrada is not None:
            # pánico: cae > 4% desde su entrada → vende TODO con máxima urgencia
            if self.precio < self.precio_entrada * (1 - self.ruido(0.04, 0.1)):
                self.vender_mercado(self.acciones, urgencia=0.05)
                self.precio_entrada = None
            return
        retorno_5 = self.model.retorno_acumulado(5)
        frac_compras = self.model.fraccion_compras(3)
        if retorno_5 is None or frac_compras is None:
            return
        # sube > 2% en 5 ticks Y su red habla de ello
        if retorno_5 > self.umbral_subida and frac_compras > 0.55:
            self.comprar_mercado(0.2 * self.efectivo / self.precio)
            self.precio_entrada = self.precio


class Miedoso(AgenteBase):
    """Tipo 10 — Aversión a pérdida 2.5:1. Motor del sobreajuste a la baja."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.umbral_miedo = self.model.random.uniform(0.15, 0.45)
        self.tick_venta = None

    def step(self):
        retorno_5 = self.model.retorno_acumulado(5)
        # el dolor de perder pesa 2.5x: reacciona a caídas 2.5 veces menores
        panico_precio = retorno_5 is not None and retorno_5 < -0.03 / 2.5
        panico_noticia = self.model.sentimiento < -self.umbral_miedo
        if self.acciones > 1e-9 and (panico_precio or panico_noticia):
            fraccion = self.model.random.uniform(0.7, 1.0)
            # vende ya, al precio que sea: el dolor de perder manda
            self.vender_mercado(self.acciones * fraccion, urgencia=0.05)
            self.tick_venta = self.model.tick
            return
        # recompra lenta y tarde: necesita 10+ ticks de calma
        if self.tick_venta is not None and self.model.tick - self.tick_venta > 10:
            calma = self.model.volatilidad_reciente(10) < 0.004
            if calma and self.model.sentimiento > -0.05:
                self.comprar_mercado(0.05 * self.efectivo / self.precio)
                if self.efectivo < 0.3 * self.capital_inicial:
                    self.tick_venta = None


class Contrarian(AgenteBase):
    """Tipo 11 — Compra con "sangre en las calles", vende en euforia."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.umbral = self.ruido(0.7, 0.1)
        self.periodo = self.model.random.randint(5, 10)
        self.desfase = self.model.random.randint(0, self.periodo - 1)

    def step(self):
        if (self.model.tick + self.desfase) % self.periodo != 0:
            return
        frac_compras = self.model.fraccion_compras(5)
        if frac_compras is None:
            return
        if (1 - frac_compras) >= self.umbral:  # el mercado vendió masivamente
            self.comprar_mercado(0.15 * self.efectivo / self.precio)
        elif frac_compras >= self.umbral:  # euforia compradora
            self.vender_mercado(0.3 * self.acciones)


class BuyAndHold(AgenteBase):
    """Tipo 12 — El capital dormido. Casi nunca opera."""

    def __init__(self, model, capital):
        super().__init__(model, capital)
        self.precio_referencia = model.libro.ultimo_precio
        self.prob_liquidez = 0.001

    def step(self):
        self.precio_referencia = max(self.precio_referencia, self.precio)
        # "la oportunidad de la década": caída > 15% desde el máximo
        if self.precio < self.precio_referencia * 0.85 and self.efectivo > 0.1 * self.capital_inicial:
            self.comprar_mercado(0.5 * self.efectivo / self.precio)
        elif self.model.random.random() < self.prob_liquidez:
            self.vender_mercado(0.2 * self.acciones)
