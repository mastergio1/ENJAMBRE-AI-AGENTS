"""Libro de órdenes de El Enjambre.

Todas las órdenes son órdenes límite. Un agente con urgencia cruza el
libro poniendo un precio agresivo (dispuesto a pagar más / recibir menos);
lo que no encuentra contraparte queda reposando y da liquidez al resto.
Las órdenes viejas expiran. Así el precio emerge del cruce de oferta y
demanda, sin mecanismos artificiales.

POLÍTICA DE PRECIO DE LA SERIE (explícita): la serie del mercado
(`model.historial_precios`) usa el ÚLTIMO PRECIO TRANSADO del tick
(`ultimo_precio`), no el VWAP. Se midió que usar el VWAP para la serie mete
autocorrelación artificial en los retornos (arrastre ~0.40 vs ~0.05 con
último-trade) y rompe el hecho estilizado de "sin arrastre". El VWAP
(`vwap_tick()`) queda disponible como métrica SEPARADA de ejecución/liquidez,
no como el precio de la serie. Ver docs/decision-politica-precio.md.
"""

from dataclasses import dataclass

EPSILON = 1e-9


@dataclass
class OrdenLimite:
    agente_id: int
    lado: str  # "compra" o "venta"
    precio: float
    cantidad: float
    tick: int  # tick en que se creó (para expirar)


class LibroOrdenes:
    VIDA_ORDEN = 4  # ticks que vive una orden antes de expirar

    def __init__(self, precio_inicial: float = 100.0):
        self.ultimo_precio = precio_inicial
        self.compras: list[OrdenLimite] = []  # ordenadas de mayor a menor precio
        self.ventas: list[OrdenLimite] = []   # ordenadas de menor a mayor precio
        self.tick_actual = 0
        # callback: se llama cuando la orden en reposo de un agente se ejecuta
        self.notificar_ejecucion = None
        # callback opcional de instrumentación (laboratorio): (agresor_id,
        # proveedor_id, cantidad, precio) por ejecución. None en producción.
        self.registrar_ejecucion_instr = None
        # Reservas por agente para las órdenes EN REPOSO (no ejecutadas aún):
        # inventario comprometido en ventas y efectivo comprometido en compras.
        # Así un agente nunca vende más acciones de las que tiene ni compromete
        # más efectivo del que posee, aunque tenga varias órdenes reposando.
        self._reserva_venta: dict[int, float] = {}   # acciones comprometidas
        self._reserva_compra: dict[int, float] = {}  # efectivo comprometido
        self.reiniciar_tick(0)

    # ---------- reservas (lo comprometido por órdenes en reposo) ----------

    def reserva_venta(self, agente_id: int) -> float:
        """Acciones del agente ya comprometidas en órdenes de venta en reposo."""
        return self._reserva_venta.get(agente_id, 0.0)

    def reserva_compra(self, agente_id: int) -> float:
        """Efectivo del agente ya comprometido en órdenes de compra en reposo."""
        return self._reserva_compra.get(agente_id, 0.0)

    def _reservar(self, orden: OrdenLimite) -> None:
        if orden.lado == "venta":
            self._reserva_venta[orden.agente_id] = (
                self._reserva_venta.get(orden.agente_id, 0.0) + orden.cantidad)
        else:
            self._reserva_compra[orden.agente_id] = (
                self._reserva_compra.get(orden.agente_id, 0.0)
                + orden.cantidad * orden.precio)

    def _liberar(self, orden: OrdenLimite, cantidad: float) -> None:
        """Libera la reserva de `cantidad` de una orden (al ejecutarse,
        cancelarse o expirar). Se recorta a 0 para no arrastrar ruido numérico."""
        if orden.lado == "venta":
            nuevo = self._reserva_venta.get(orden.agente_id, 0.0) - cantidad
            self._reserva_venta[orden.agente_id] = nuevo if nuevo > EPSILON else 0.0
        else:
            nuevo = (self._reserva_compra.get(orden.agente_id, 0.0)
                     - cantidad * orden.precio)
            self._reserva_compra[orden.agente_id] = nuevo if nuevo > EPSILON else 0.0

    def reiniciar_tick(self, tick: int) -> None:
        """Nuevo tick: expira órdenes viejas y reinicia contadores de flujo."""
        self.tick_actual = tick
        limite = tick - self.VIDA_ORDEN
        # al expirar una orden se libera su reserva (ya no compromete nada)
        for o in self.compras:
            if o.tick <= limite:
                self._liberar(o, o.cantidad)
        for o in self.ventas:
            if o.tick <= limite:
                self._liberar(o, o.cantidad)
        self.compras = [o for o in self.compras if o.tick > limite]
        self.ventas = [o for o in self.ventas if o.tick > limite]
        self.volumen_tick = 0.0
        self.valor_tick = 0.0            # Σ cantidad × precio (para el VWAP)
        self.volumen_compras_tick = 0.0  # volumen donde el agresor compró
        self.volumen_ventas_tick = 0.0   # volumen donde el agresor vendió

    # ---------- consultas ----------

    def mejor_compra(self) -> float | None:
        return self.compras[0].precio if self.compras else None

    def mejor_venta(self) -> float | None:
        return self.ventas[0].precio if self.ventas else None

    def vwap_tick(self) -> float | None:
        """Precio promedio ponderado por volumen del tick (el 'cierre' limpio)."""
        if self.volumen_tick <= EPSILON:
            return None
        return self.valor_tick / self.volumen_tick

    def cancelar_ordenes(self, agente_id: int) -> None:
        """Retira todas las órdenes reposando de un agente y libera sus reservas."""
        for o in self.compras:
            if o.agente_id == agente_id:
                self._liberar(o, o.cantidad)
        for o in self.ventas:
            if o.agente_id == agente_id:
                self._liberar(o, o.cantidad)
        self.compras = [o for o in self.compras if o.agente_id != agente_id]
        self.ventas = [o for o in self.ventas if o.agente_id != agente_id]

    # ---------- ejecución ----------

    def orden_limite(
        self, agente_id: int, lado: str, precio: float, cantidad: float
    ) -> tuple[float, float]:
        """Coloca una orden límite. Cruza lo que pueda; el resto reposa.

        Devuelve (cantidad_ejecutada, dinero_movido) para que el agresor
        actualice su cartera. Los dueños de órdenes en reposo se enteran
        vía el callback notificar_ejecucion.
        """
        precio = max(precio, 0.01)
        contra = self.ventas if lado == "compra" else self.compras
        restante = cantidad
        dinero = 0.0
        while restante > EPSILON and contra:
            tope = contra[0]
            cruza = tope.precio <= precio if lado == "compra" else tope.precio >= precio
            if not cruza:
                break
            ejecutado = min(restante, tope.cantidad)
            dinero += ejecutado * tope.precio
            self._ejecutar(agente_id, lado, tope, ejecutado)
            restante -= ejecutado
            if tope.cantidad <= EPSILON:
                contra.pop(0)
        if restante > EPSILON:
            orden = OrdenLimite(agente_id, lado, precio, restante, self.tick_actual)
            self._reservar(orden)  # el remanente reposa → compromete inventario/efectivo
            if lado == "compra":
                self.compras.append(orden)
                self.compras.sort(key=lambda o: -o.precio)
            else:
                self.ventas.append(orden)
                self.ventas.sort(key=lambda o: o.precio)
        return cantidad - restante, dinero

    # ---------- interno ----------

    def _ejecutar(self, agresor_id: int, lado_agresor: str,
                  orden_reposo: OrdenLimite, cantidad: float) -> None:
        """Cruza una cantidad contra una orden que reposaba en el libro."""
        orden_reposo.cantidad -= cantidad
        self._liberar(orden_reposo, cantidad)  # lo ejecutado deja de estar reservado
        self._registrar(lado_agresor, cantidad, orden_reposo.precio)
        if self.notificar_ejecucion is not None:
            # el dueño de la orden en reposo operó en el lado contrario al agresor
            lado_dueno = "venta" if lado_agresor == "compra" else "compra"
            self.notificar_ejecucion(orden_reposo.agente_id, lado_dueno, cantidad, orden_reposo.precio)
        # instrumentación opcional (laboratorio): quién fue agresor y quién proveyó
        # liquidez en esta ejecución. None en producción → sin costo.
        if self.registrar_ejecucion_instr is not None:
            self.registrar_ejecucion_instr(agresor_id, orden_reposo.agente_id,
                                           cantidad, orden_reposo.precio)

    def _registrar(self, lado_agresor: str, cantidad: float, precio: float) -> None:
        self.ultimo_precio = precio
        self.volumen_tick += cantidad
        self.valor_tick += cantidad * precio
        if lado_agresor == "compra":
            self.volumen_compras_tick += cantidad
        else:
            self.volumen_ventas_tick += cantidad
