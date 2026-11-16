"""Señal de PREDICCIÓN ponderada del reporte (sin dependencias de web).

La ablación por arquetipo sobre 678 casos reales (docs/calibracion-por-arquetipo.md)
mostró que las voces CONTRARIAN (quant escéptico, contrarian sabio) aciertan
<50% y DESORIENTAN el consenso. Esta señal baja su peso SOLO para el número que
alimenta la calibración (`senal_media_ponderada`). NO toca el enjambre, ni el
tono de mercado, ni las frases, ni la `senal_media_lideres` histórica (promedio
simple). El optimista NO se baja: la medición lo halló útil.

Reversible con el env ENJAMBRE_PESO_CONTRARIANS (vacío = 0.3; 1.0 = promedio
simple, sin cambio).
"""
import os

ARQUETIPOS_CONTRARIAN_SENAL = frozenset({"quant_esceptico", "contrarian_sabio"})
PESO_DEFECTO = 0.3


def peso_contrarians() -> float:
    try:
        v = os.environ.get("ENJAMBRE_PESO_CONTRARIANS", "")
        return float(v) if v != "" else PESO_DEFECTO
    except ValueError:
        return PESO_DEFECTO


def senal_media_ponderada(lideres, respuestas) -> float:
    """Media de las señales de los líderes bajando el peso de las voces
    contrarian. `lideres[i].arquetipo` empareja con `respuestas[i]["senal"]`."""
    peso = peso_contrarians()
    num = den = 0.0
    for lider, r in zip(lideres, respuestas):
        w = peso if lider.arquetipo in ARQUETIPOS_CONTRARIAN_SENAL else 1.0
        num += r["senal"] * w
        den += w
    return round(num / den, 2) if den else 0.0


# ---------- GATING por fuerza de señal (Propuesta "gating", punto 1) ----------
# La re-medición SIN FUGA (remedir_sin_fuga.py, 616 casos) mostró que la DIRECCIÓN
# solo es fiable cuando se cumplen DOS condiciones a la vez:
#   1. el mercado tiene señal real en el texto → solo ÍNDICE (cripto/acción/oro/
#      petróleo quedan en ~azar: su dirección NO está en la noticia), y
#   2. el enjambre está muy convencido → |senal_media_ponderada| ≥ 0.3.
# En esa banda el acierto histórico (sin fuga) fue ~80% en índice. Fuera de ella
# NO afirmamos dirección: la mostramos como "lectura ambigua / visualización".
# Esto SUBE el acierto condicional a cambio de cobertura (trade-off correcto) y es
# MÁS honesto ante la CMF (no sobre-afirma). Umbrales y mercados fiables son
# overridables por entorno para medir/rollback sin re-desplegar.
UMBRAL_FUERTE = 0.30
UMBRAL_MODERADA = 0.20
MERCADOS_FIABLES_DEFECTO = frozenset({"indice"})


def _umbral(nombre: str, por_defecto: float) -> float:
    try:
        v = os.environ.get(nombre, "")
        return float(v) if v != "" else por_defecto
    except ValueError:
        return por_defecto


def mercados_fiables() -> frozenset:
    """Mercados donde la dirección se considera fiable (env
    ENJAMBRE_MERCADOS_FIABLES = lista separada por comas; vacío = solo índice)."""
    crudo = os.environ.get("ENJAMBRE_MERCADOS_FIABLES", "").strip()
    if not crudo:
        return MERCADOS_FIABLES_DEFECTO
    return frozenset(m.strip() for m in crudo.split(",") if m.strip())


def clasificar_conviccion(senal_ponderada: float, mercado: str | None) -> dict:
    """Clasifica la convicción del enjambre y si la DIRECCIÓN es fiable.

    Devuelve: nivel ('fuerte'|'moderada'|'debil'), fiable_direccion (bool) y una
    nota honesta para la UI. NO cambia el motor ni el precio: solo etiqueta el
    reporte para que el producto afirme dirección solo cuando el historial
    (sin fuga) la respalda."""
    a = abs(senal_ponderada or 0.0)
    fuerte = _umbral("ENJAMBRE_UMBRAL_FUERTE", UMBRAL_FUERTE)
    moderada = _umbral("ENJAMBRE_UMBRAL_MODERADA", UMBRAL_MODERADA)
    if a >= fuerte:
        nivel = "fuerte"
    elif a >= moderada:
        nivel = "moderada"
    else:
        nivel = "debil"
    fiable = nivel == "fuerte" and (mercado in mercados_fiables())
    if fiable:
        nota = "El enjambre está muy convencido y en este tipo de mercado su lectura ha sido confiable."
    elif nivel == "debil":
        nota = "Lectura ambigua: el enjambre no se decide. Tómalo como visualización, no como dirección."
    else:
        nota = "Convicción parcial, o un mercado donde la dirección no suele leerse en la noticia. Visualización."
    return {"nivel": nivel, "fiable_direccion": fiable, "nota": nota}
