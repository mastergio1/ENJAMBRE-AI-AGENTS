"""El símbolo del HECHO, no el primero de la sopa.

El portero a veces pega 9 tickers a un titular de Eli Lilly y el
corrector puntuaba APP. Eso no calibra: compara el enjambre contra
otra empresa. Acá se elige el ticker del evento, se marca el ruido
(Benzinga whales, top-N, WSB) y se decide si el caso entra a la nota.
"""

from __future__ import annotations

import re

# más largo primero: "eli lilly" antes que "lilly"
_NOMBRES: tuple[tuple[str, str], ...] = (
    ("eli lilly", "LLY"),
    ("lilly", "LLY"),
    ("nvidia", "NVDA"),
    ("apple", "AAPL"),
    ("amazon", "AMZN"),
    ("tesla", "TSLA"),
    ("microsoft", "MSFT"),
    ("alphabet", "GOOGL"),
    ("google", "GOOGL"),
    ("netflix", "NFLX"),
    ("meta platforms", "META"),
    ("facebook", "META"),
    ("meta shares", "META"),
    ("jpmorgan", "JPM"),
    ("jp morgan", "JPM"),
    ("goldman sachs", "GS"),
    ("morgan stanley", "MS"),
    ("bank of america", "BAC"),
    ("wells fargo", "WFC"),
    ("occidental petroleum", "OXY"),
    ("boeing", "BA"),
    ("intel", "INTC"),
    ("micron", "MU"),
    ("broadcom", "AVGO"),
    ("qualcomm", "QCOM"),
    ("palantir", "PLTR"),
    ("coinbase", "COIN"),
    ("microstrategy", "MSTR"),
    ("walmart", "WMT"),
    ("costco", "COST"),
    ("starbucks", "SBUX"),
    ("mcdonald", "MCD"),
    ("coca-cola", "KO"),
    ("pepsico", "PEP"),
    ("pfizer", "PFE"),
    ("moderna", "MRNA"),
    ("unitedhealth", "UNH"),
    ("salesforce", "CRM"),
    ("adobe", "ADBE"),
    ("oracle", "ORCL"),
    ("cisco", "CSCO"),
    ("shopify", "SHOP"),
    ("snowflake", "SNOW"),
    ("crowdstrike", "CRWD"),
    ("exxon", "XOM"),
    ("chevron", "CVX"),
    ("occidental", "OXY"),
    ("advanced micro devices", "AMD"),
    (" target ", "TGT"),  # espacios: no "price target"
)

_RUIDO = (
    r"whale activit",
    r"whale alert",
    r"what whales are doing",
    r"stocks whale",
    r"most[- ]searched",
    r"searched tickers",
    r"searched on benzinga",
    r"crypto update",
    r"stocks to watch",
    r"what to watch",
    r"beginner's guide",
    r"how to invest",
    r"\bsponsored\b",
    r"webinar",
    r"weekly market preview",
    r"top \d+\s+(mid-cap|large-cap|gainers|stocks|trending)",
    r"trending stocks on wallstreetbets",
    r"why these \d+ stocks",
    r"are among top",
    r"mid-cap gainers last week",
    r"large-cap gainers last week",
)

_MACRO = (
    "federal reserve", "the fed ", "fed holds", "fed pauses", "fed cuts",
    "fed raises", "fed keeps", "fomc", "s&p 500", "s&p500", "nasdaq 100",
    "dow jones", "wall street", "consumer prices", "cpi ", "inflation",
    "nonfarm", "rate hike", "rate cut", "treasury yield",
)


def lista_simbolos(simbolos: str | None) -> list[str]:
    return [s.strip().upper() for s in (simbolos or "").split(",") if s.strip()]


def es_sopa(simbolos: str | None) -> bool:
    return len(lista_simbolos(simbolos)) >= 4


def es_ruido(titular: str | None) -> bool:
    t = (titular or "").lower()
    if not t.strip():
        return False
    return any(re.search(p, t) for p in _RUIDO)


def _es_macro(titular: str) -> bool:
    t = f" {(titular or '').lower()} "
    return any(k in t for k in _MACRO)


def _ticker_en_titular(titular: str, tickers: list[str]) -> str | None:
    for tk in sorted(tickers, key=len, reverse=True):
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(tk) + r"(?![A-Za-z0-9])",
                     titular or "", re.I):
            return tk.upper()
    return None


def _nombre_en_titular(titular: str) -> str | None:
    t = f" {(titular or '').lower()} "
    if "price target" in t and "target raises" not in t and "target cuts" not in t:
        t = t.replace("price target", " ")
    for name, tk in _NOMBRES:
        if name in t:
            return tk
    if re.search(r"\bmeta\b", t) and "metaverse" not in t:
        return "META"
    if re.search(r"\btarget\b", t) and "price target" not in f" {(titular or '').lower()} ":
        return "TGT"
    return None


def simbolo_del_hecho(titular: str, simbolos: str | None = "") -> str:
    """Ticker del evento. Vacío si es sopa sin ancla: no adivinar."""
    lista = lista_simbolos(simbolos)
    nom = _nombre_en_titular(titular or "")
    if nom:
        return nom
    if lista:
        tk = _ticker_en_titular(titular or "", lista)
        if tk:
            return tk
    if _es_macro(titular or ""):
        for pref in ("SPY", "QQQ", "DIA", "IWM"):
            if pref in lista:
                return pref
        if not lista:
            return "SPY"
    if len(lista) == 1:
        return lista[0]
    if len(lista) >= 4:
        return ""
    return lista[0] if lista else ""


def apto_calibracion(titular: str, simbolos: str | None = "",
                     simbolo_real: str | None = "") -> bool:
    """¿Entra a la nota del producto? Ruido y sopa mal puntuada, afuera."""
    if es_ruido(titular):
        return False
    hecho = simbolo_del_hecho(titular, simbolos)
    scored = (simbolo_real or "").upper().split(",")[0].strip()
    if es_sopa(simbolos) and (not hecho or (scored and scored != hecho.upper())):
        return False
    if hecho and scored and scored != hecho.upper():
        return False
    return True
