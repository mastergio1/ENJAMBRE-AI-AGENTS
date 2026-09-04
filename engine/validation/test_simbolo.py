"""El símbolo del hecho, no el primero de la sopa."""

from contenido.simbolo import (
    apto_calibracion,
    es_ruido,
    es_sopa,
    simbolo_del_hecho,
)


def test_lilly_no_es_app():
    tit = "Eli Lilly Could Swing Over $76 Billion In Value After Earnings"
    sims = "APP,GILD,HWM,LLY,NET,SHOP,SNDK,UBER,WDC"
    assert simbolo_del_hecho(tit, sims) == "LLY"
    assert not apto_calibracion(tit, sims, "APP")
    assert apto_calibracion(tit, sims, "LLY")


def test_nvidia_cobre_no_es_copx():
    tit = "NVIDIA CEO Says AI's Future Isn't Just Copper"
    assert simbolo_del_hecho(tit, "COPX") == "NVDA"
    assert not apto_calibracion(tit, "COPX", "COPX")


def test_fed_elige_spy_en_la_sopa():
    tit = "Stock Market Today: S&P 500, Dow, Nasdaq 100 Futures Gain as Trump Halts Tariffs"
    sims = "AMD,AMZN,ATKR,BA,QQQ,SPY"
    assert simbolo_del_hecho(tit, sims) == "SPY"


def test_sopa_sin_ancla_no_adivina():
    tit = "A mixed bag of names in today's session"
    sims = "ASND,BMRN,CLGN,EIX,FNGR,PCG,TITN"
    assert simbolo_del_hecho(tit, sims) == ""
    assert not apto_calibracion(tit, sims, "ASND")


def test_un_solo_ticker_se_queda():
    assert simbolo_del_hecho("Something happened overnight", "AAPL") == "AAPL"
    assert apto_calibracion("Something happened overnight", "AAPL", "AAPL")


def test_ruido_whale_y_top_n():
    assert es_ruido("Check Out What Whales Are Doing With SLB")
    assert es_ruido("10 Information Technology Stocks Whale Activity In Today's Session")
    assert es_ruido("EXCLUSIVE: Top 20 Most-Searched Tickers On Benzinga Pro")
    assert es_ruido("Top 15 Trending Stocks On WallStreetBets As Of Tuesday")
    assert not es_ruido("Fed holds rates steady as widely expected")
    assert not apto_calibracion("Check Out What Whales Are Doing With SLB", "SLB", "SLB")


def test_sopa_cuenta_cuatro():
    assert es_sopa("A,B,C,D")
    assert not es_sopa("AAPL,MSFT")


def test_price_target_no_es_tgt():
    tit = "TD Cowen Downgrades Occidental Petroleum to Hold, Lowers Price Target"
    assert simbolo_del_hecho(tit, "OXY") == "OXY"


def test_target_earnings_si_es_tgt():
    tit = "Target Raises FY2026 GAAP EPS Guidance from $8.50 to $9.90"
    assert simbolo_del_hecho(tit, "TGT") == "TGT"
