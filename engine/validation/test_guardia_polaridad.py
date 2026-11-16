"""La guardia de polaridad defensiva (Propuesta gating, punto 5): ante un titular
donde la IA y el léxico discrepan en signo con fuerza, atenúa el consenso hacia
neutro en vez de moverse con convicción hacia un lado dudoso. Desactivada por
defecto (umbral 0.0). Nunca invierte el signo."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

from model import guardia_polaridad  # noqa: E402


def test_desactivada_no_toca_nada():
    assert guardia_polaridad(0.8, -0.9, umbral=0.0) == 0.8


def test_discrepancia_fuerte_atenua():
    # IA dice +0.8, léxico dice -0.9: discrepan y ambas fuertes → atenúa ×0.5
    assert guardia_polaridad(0.8, -0.9, umbral=0.3) == 0.4


def test_discrepancia_pero_lexico_debil_no_atenua():
    # el léxico discrepa pero es débil (0.1 < 0.3) → no es ambigüedad real
    assert guardia_polaridad(0.8, -0.1, umbral=0.3) == 0.8


def test_acuerdo_no_atenua():
    # mismo signo → no toca
    assert guardia_polaridad(0.8, 0.9, umbral=0.3) == 0.8


def test_nunca_invierte_el_signo():
    r = guardia_polaridad(-0.8, 0.9, umbral=0.3)
    assert r < 0 and r == -0.4  # sigue bajista, solo atenuado


def test_consenso_cero_se_devuelve_igual():
    assert guardia_polaridad(0.0, -0.9, umbral=0.3) == 0.0
