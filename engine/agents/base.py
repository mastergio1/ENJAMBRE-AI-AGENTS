"""Clase base de todos los inversionistas simulados de El Enjambre."""

import mesa


class AgenteBase(mesa.Agent):
    """Inversionista con efectivo y acciones. Arranca 50/50."""

    def __init__(self, model, capital: float):
        super().__init__(model)
        self.capital_inicial = capital
        self.efectivo = capital * 0.5
        self.acciones = (capital * 0.5) / model.libro.ultimo_precio
        self.ultima_accion = None  # "compra" | "venta" | None (para la visual)

    # ---------- utilidades ----------

    def ruido(self, valor: float, sigma_relativo: float = 0.15) -> float:
        """Valor base ± ruido gaussiano (σ = 15% por defecto, CLAUDE.md sección 4)."""
        return valor * self.model.random.gauss(1.0, sigma_relativo)

    @property
    def precio(self) -> float:
        """Precio de referencia: el cierre VWAP del último tick.
        (El último precio transado rebota demasiado entre bid y ask.)"""
        return self.model.historial_precios[-1]

    def valor_cartera(self) -> float:
        return self.efectivo + self.acciones * self.precio

    # ---------- operaciones ----------

    def colocar_orden(self, lado: str, precio_limite: float, cantidad: float) -> None:
        """Coloca una orden límite y contabiliza lo que se ejecute al instante."""
        if lado == "compra":
            # limitada por el efectivo disponible y por un tope de cordura
            maximo = self.efectivo / max(precio_limite, 0.01)
            tope_sano = 2 * self.capital_inicial / max(self.precio, 0.01)
            cantidad = min(cantidad, maximo, tope_sano)
        else:
            cantidad = min(cantidad, self.acciones)  # sin ventas cortas
        if cantidad <= 1e-9:
            return
        ejecutado, dinero = self.model.libro.orden_limite(
            self.unique_id, lado, precio_limite, cantidad
        )
        if ejecutado > 1e-9:
            self.aplicar_ejecucion(lado, ejecutado, dinero / ejecutado)
        else:
            self.ultima_accion = lado

    def _urgencia_aleatoria(self) -> float:
        """Urgencia con cola larga: la mayoría es paciente, unos pocos cruzan
        el libro profundo. Así el precio se ajusta rápido y no deja tendencias
        predecibles de varios ticks."""
        return min(self.model.random.expovariate(125), 0.06)

    def comprar_mercado(self, cantidad: float, urgencia: float | None = None) -> None:
        """Compra con urgencia: dispuesto a pagar hasta `urgencia` sobre el precio."""
        if urgencia is None:
            urgencia = self._urgencia_aleatoria()
        self.colocar_orden("compra", self.precio * (1 + urgencia), cantidad)

    def vender_mercado(self, cantidad: float, urgencia: float | None = None) -> None:
        """Vende con urgencia: dispuesto a recibir hasta `urgencia` bajo el precio."""
        if urgencia is None:
            urgencia = self._urgencia_aleatoria()
        self.colocar_orden("venta", self.precio * (1 - urgencia), cantidad)

    def aplicar_ejecucion(self, lado: str, cantidad: float, precio: float) -> None:
        """Se ejecutó (total o parcialmente) una orden propia."""
        if lado == "compra":
            self.efectivo -= cantidad * precio
            self.acciones += cantidad
        else:
            self.efectivo += cantidad * precio
            self.acciones -= cantidad
        self.ultima_accion = lado
