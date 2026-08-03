"""Libro de órdenes de El Enjambre.

Todas las órdenes son órdenes límite. Un agente con urgencia cruza el
libro poniendo un precio agresivo (dispuesto a pagar más / recibir menos);
lo que no encuentra contraparte queda reposando y da liquidez al resto.
Las órdenes viejas expiran. El precio del tick es el VWAP: el promedio
de donde realmente se operó. Así el precio emerge del cruce de oferta y
demanda, sin mecanismos artificiales.
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
        self.reiniciar_tick(0)

    def reiniciar_tick(self, tick: int) -> None:
        """Nuevo tick: expira órdenes viejas y reinicia contadores de flujo."""
        self.tick_actual = tick
        limite = tick - self.VIDA_ORDEN
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
        """Retira todas las órdenes reposando de un agente."""
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
            self._ejecutar(lado, tope, ejecutado)
            restante -= ejecutado
            if tope.cantidad <= EPSILON:
                contra.pop(0)
        if restante > EPSILON:
            orden = OrdenLimite(agente_id, lado, precio, restante, self.tick_actual)
            if lado == "compra":
                self.compras.append(orden)
                self.compras.sort(key=lambda o: -o.precio)
            else:
                self.ventas.append(orden)
                self.ventas.sort(key=lambda o: o.precio)
        return cantidad - restante, dinero

    # ---------- interno ----------

    def _ejecutar(self, lado_agresor: str, orden_reposo: OrdenLimite, cantidad: float) -> None:
        """Cruza una cantidad contra una orden que reposaba en el libro."""
        orden_reposo.cantidad -= cantidad
        self._registrar(lado_agresor, cantidad, orden_reposo.precio)
        if self.notificar_ejecucion is not None:
            # el dueño de la orden en reposo operó en el lado contrario al agresor
            lado_dueno = "venta" if lado_agresor == "compra" else "compra"
            self.notificar_ejecucion(orden_reposo.agente_id, lado_dueno, cantidad, orden_reposo.precio)

    def _registrar(self, lado_agresor: str, cantidad: float, precio: float) -> None:
        self.ultimo_precio = precio
        self.volumen_tick += cantidad
        self.valor_tick += cantidad * precio
        if lado_agresor == "compra":
            self.volumen_compras_tick += cantidad
        else:
            self.volumen_ventas_tick += cantidad
