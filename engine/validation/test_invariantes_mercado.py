"""Invariantes de contabilidad del motor (Fase 0 — correctitud).

Garantizan que el mercado no "inventa" ni "destruye" dinero/acciones y que
ningún agente opera más de lo que tiene:
  - ningún agente termina con efectivo o acciones negativas (sin ventas cortas);
  - lo reservado por órdenes en reposo nunca supera lo que el agente posee;
  - el efectivo total y las acciones totales se conservan durante la sesión.

Antes de la Fase 0, decenas de agentes terminaban con acciones negativas tras
un crash (ventas en corto no deseadas por falta de reserva de inventario). Este
test impide que esa regresión vuelva a entrar.
"""

from model import MercadoEnjambre

TOL = 1e-6


def _correr(seed=42, calienta=80, shocks=(-0.7, -0.9), post=40):
    m = MercadoEnjambre(seed=seed, ticks_horizonte=400)
    ef0 = sum(a.efectivo for a in m.agents)
    ac0 = sum(a.acciones for a in m.agents)
    for _ in range(calienta):
        m.step()
    for s in shocks:
        m.aplicar_noticia(s)
        for _ in range(post):
            m.step()
    return m, ef0, ac0


def test_sin_efectivo_ni_acciones_negativas():
    m, _, _ = _correr()
    for a in m.agents:
        assert a.efectivo >= -TOL, f"efectivo negativo: {a.efectivo}"
        assert a.acciones >= -TOL, f"acciones negativas: {a.acciones}"


def test_reservas_no_superan_lo_disponible():
    m, _, _ = _correr()
    for a in m.agents:
        assert m.libro.reserva_venta(a.unique_id) <= a.acciones + TOL
        assert m.libro.reserva_compra(a.unique_id) <= a.efectivo + TOL


def test_conservacion_de_efectivo_y_acciones():
    m, ef0, ac0 = _correr()
    ef1 = sum(a.efectivo for a in m.agents)
    ac1 = sum(a.acciones for a in m.agents)
    # tolerancia relativa al tamaño del total (sumas de millones)
    assert abs(ef1 - ef0) <= max(1e-3, 1e-6 * abs(ef0)), f"drift efectivo {ef1 - ef0}"
    assert abs(ac1 - ac0) <= max(1e-3, 1e-6 * abs(ac0)), f"drift acciones {ac1 - ac0}"
