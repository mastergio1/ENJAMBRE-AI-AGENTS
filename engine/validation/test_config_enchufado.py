"""Guardián anti "perilla muerta": toda perilla del config debe leerla el código.

Contexto: en agentes.json hay perillas de calibración. Si una existe en el
config pero NINGÚN archivo de código la lee, es una "perilla muerta" — girarla
no hace nada, y calibrar con ella es tirar plata (y tiempo de medición) a la
basura. Este test recorre el config, junta cada perilla, y falla si alguna no
aparece leída por el código (`config.get("clave")` / `cfg.get("clave")`).

Todo local, sin IA. Si agregas una perilla nueva al config, enchúfala al código
(léela con .get) o, si es una constante intencional sin ruta de código, añádela
a PERILLAS_INTENCIONALMENTE_CONSTANTES con su justificación.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_CONFIG = os.path.join(ENGINE, "config", "agentes.json")

# Claves estructurales / metadatos: NO son perillas de comportamiento, no se
# "leen" con .get sino que dan forma al config. Se excluyen del chequeo.
CLAVES_ESTRUCTURALES = {
    "descripcion", "total_agentes", "tipos", "ruido_parametros_sigma",
    # dentro de cada tipo:
    "id", "nombre", "cantidad", "capital_relativo", "en_red_social", "rol",
    "parametros", "arquetipos", "seguidores_rango",
}

# Perillas que a propósito son constantes sin ruta de código (documentar por qué).
PERILLAS_INTENCIONALMENTE_CONSTANTES = {
    # el fondo pasivo (flujo 401k/AFP) no reacciona a titulares por diseño:
    # su sensibilidad es 0 y no hay código de noticia al que enchufarla.
    "sensibilidad_noticias",
}


def _claves_leidas_por_el_codigo() -> set:
    """Todas las claves que el código lee vía .get("clave") / .get('clave')."""
    patron = re.compile(r"\.get\(\s*[\"']([a-zA-Z_]+)[\"']")
    leidas = set()
    for raiz, _, ficheros in os.walk(ENGINE):
        if "__pycache__" in raiz:
            continue
        for f in ficheros:
            if not f.endswith(".py") or f.startswith("test_"):
                continue
            ruta = os.path.join(raiz, f)
            with open(ruta, encoding="utf-8") as fh:
                leidas |= set(patron.findall(fh.read()))
    return leidas


def _perillas_del_config() -> set:
    with open(RUTA_CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    perillas = set()
    # top-level (peso_doomer, peso_doomer_por_mercado, umbral_correccion_sesgo…)
    for k in cfg:
        if k not in CLAVES_ESTRUCTURALES:
            perillas.add(k)
    # parametros de cada tipo de agente
    for tipo in cfg["tipos"]:
        perillas |= set(tipo.get("parametros", {}))
    return perillas - CLAVES_ESTRUCTURALES


def test_ninguna_perilla_del_config_esta_muerta():
    """Cada perilla del config la lee el código (o es constante intencional)."""
    leidas = _claves_leidas_por_el_codigo()
    perillas = _perillas_del_config()
    muertas = perillas - leidas - PERILLAS_INTENCIONALMENTE_CONSTANTES
    assert not muertas, (
        "Perillas MUERTAS (existen en agentes.json pero el código no las lee): "
        f"{sorted(muertas)}. Enchúfalas con .get(\"clave\") en el agente/modelo, "
        "o si son constantes intencionales añádelas a "
        "PERILLAS_INTENCIONALMENTE_CONSTANTES con su justificación."
    )
