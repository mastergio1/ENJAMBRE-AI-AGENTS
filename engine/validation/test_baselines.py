"""Tests de los baselines (Fase 3/4). Sin red."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # engine/
from calibration import baselines as bl


def _f(pct, senal=0.0, mom=0.0, precio=0.0, fecha="2020-01-01"):
    return {"fecha": fecha, "pct_corr": pct, "senal": senal, "mom_prev": mom,
            "direccion_pct": precio}


def test_acc_regla_cuenta_y_filtra_zona():
    filas = [_f(2.0, senal=0.5), _f(-2.0, senal=-0.5), _f(0.1, senal=0.5)]  # el 3º no es direccionable
    a, nop, ndir = bl.acc_regla(filas, bl.regla_senal)
    assert ndir == 2 and nop == 2 and a == 100.0


def test_regla_se_abstiene_cuando_pred_cero():
    filas = [_f(2.0, senal=0.0), _f(2.0, senal=0.5)]  # la 1ª: la señal no opina
    a, nop, ndir = bl.acc_regla(filas, bl.regla_senal)
    assert ndir == 2 and nop == 1 and a == 100.0


def test_regla_mayoria_toma_el_signo_dominante_del_train():
    train = [_f(2.0), _f(2.0), _f(-2.0)]  # mayoría sube
    regla = bl.regla_mayoria(train)
    assert regla(_f(0)) == 1
    train2 = [_f(-2.0), _f(-2.0), _f(2.0)]  # mayoría baja
    assert bl.regla_mayoria(train2)(_f(0)) == -1


def test_momentum_predice_continuacion():
    # mom_prev positivo → predice subida; el caso subió → acierta
    filas = [_f(2.0, mom=1.5), _f(-2.0, mom=-1.5)]
    a, nop, _ = bl.acc_regla(filas, bl.regla_momentum)
    assert nop == 2 and a == 100.0


def test_comparar_devuelve_las_cuatro_reglas():
    train = [_f(2.0, senal=0.5, mom=1.0, precio=1.0)] * 3
    test = [_f(2.0, senal=0.5, mom=1.0, precio=1.0)]
    res = bl.comparar(train, test)
    assert set(res) == {"mayoria", "momentum", "senal_enjambre", "precio_simulado"}
    assert res["senal_enjambre"][0] == 100.0  # señal positiva, subió
