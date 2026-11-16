"""La re-medición SIN FUGA (`calibration.remedir_sin_fuga`): la ventana parte del
cierre DEL DÍA del titular (no del anterior), la media ponderada baja a los 2
contrarians, y el acierto se cuenta solo sobre casos direccionables. Con un
`fetch` simulado no se llama a Yahoo."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from calibration import remedir_sin_fuga as R  # noqa: E402


def test_signo():
    assert R._sg(1.2) == 1 and R._sg(-0.1) == -1 and R._sg(0) == 0


def test_pond_castiga_contrarians():
    # dos arquetipos: uno base (+1) y un contrarian (-1); el contrarian pesa 0.3
    sa = {"institucional_frio": {"senal_media": 1.0, "n": 10},
          "quant_esceptico": {"senal_media": -1.0, "n": 10}}
    # num = 1*10*1 + (-1)*10*0.3 = 7 ; den = 10 + 3 = 13 -> 0.538
    assert round(R._pond(sa), 3) == 0.538


def test_pct_sin_fuga_parte_del_dia_del_titular():
    barras = [("2026-01-01", 100.0), ("2026-01-02", 110.0),
              ("2026-01-03", 120.0), ("2026-01-04", 132.0)]
    # fecha_base = cierre ANTERIOR (01-01); base = día del titular (01-02 = 110)
    # final = 2 ruedas después (01-04 = 132) -> (132-110)/110 = +20%
    assert round(R.pct_sin_fuga(barras, "2026-01-01", 2), 2) == 20.0


def test_pct_sin_fuga_sin_barras_suficientes():
    barras = [("2026-01-01", 100.0), ("2026-01-02", 110.0)]
    assert R.pct_sin_fuga(barras, "2026-01-01", 2) is None   # no alcanza
    assert R.pct_sin_fuga(barras, "2099-01-01", 1) is None   # fecha ausente
    assert R.pct_sin_fuga(None, "2026-01-01", 1) is None     # sin barras


def test_acc_solo_cuenta_direccionables():
    filas = [
        {"senal": 0.5, "direccion_pct": 1.0, "pct_corr": 2.0, "pct_orig": 2.0},   # señal+ real+ ok
        {"senal": -0.5, "direccion_pct": 1.0, "pct_corr": 3.0, "pct_orig": 3.0},  # señal- real+ falla
        {"senal": 0.5, "direccion_pct": 1.0, "pct_corr": 0.1, "pct_orig": 0.1},   # plano: fuera (|.1|<0.3)
    ]
    acc, n = R._acc(filas, por_senal=True, usar_corr=True)
    assert n == 2 and acc == 50.0  # 1 de 2 direccionables


def test_recolectar_desde_archivo(tmp_path):
    import json
    casos = {"casos": [{
        "origen": "historico",
        "simbolos": "BTC-USD",
        "direccion_pct": -1.0,
        "senales_arquetipo": {"institucional_frio": {"senal_media": -0.8, "n": 5}},
        "reaccion_real": {"simbolo": "BTC-USD", "fecha_base": "2026-01-01",
                          "ruedas": 2, "pct_real": 9.0},
    }]}
    ruta = tmp_path / "cal.json"
    ruta.write_text(json.dumps(casos))
    barras = [("2026-01-01", 100.0), ("2026-01-02", 100.0),
              ("2026-01-03", 100.0), ("2026-01-04", 95.0)]  # sin fuga: -5%
    filas = R.recolectar(str(ruta), fetch=lambda s, f: barras, pausa=0)
    assert len(filas) == 1
    f = filas[0]
    assert f["mercado"] == "cripto"
    assert round(f["pct_corr"], 1) == -5.0   # sin fuga
    assert f["pct_orig"] == 9.0              # con fuga (lo que trae el export)
    assert round(f["senal"], 2) == -0.8
    # resumen: la señal (-0.8) acierta contra el real sin fuga (-5%)
    res = R.resumen(filas)
    assert res["cripto"]["sin_fuga"]["senal"] == 100.0


def test_gating_por_senal_cobertura_y_acierto():
    # 4 casos direccionables: señales fuertes aciertan, señales débiles fallan
    filas = [
        {"senal": 0.8, "pct_corr": 5.0},    # fuerte, acierta
        {"senal": 0.6, "pct_corr": 4.0},    # fuerte, acierta
        {"senal": 0.05, "pct_corr": -3.0},  # débil, falla (señal+ real-)
        {"senal": -0.05, "pct_corr": 2.0},  # débil, falla (señal- real+)
    ]
    g = R.gating_por_senal(filas, cortes=(0.0, 0.5))
    base = g[0]       # |señal|>=0: los 4
    fuerte = g[1]     # |señal|>=0.5: los 2 fuertes
    assert base["n"] == 4 and base["acierto"] == 50.0 and base["cobertura"] == 100.0
    assert fuerte["n"] == 2 and fuerte["acierto"] == 100.0 and fuerte["cobertura"] == 50.0
