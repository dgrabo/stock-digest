"""Daily price change from Yahoo Finance (yfinance)."""

import warnings

import yfinance as yf

# yfinance triggers pandas deprecation warnings internally; not our code, so mute them.
warnings.filterwarnings("ignore", message="The inplace keyword", module="yfinance")


def fetch_price(ticker):
    # 5d instead of 2d so weekends/holidays still give two trading days.
    closes = yf.Ticker(ticker).history(period="5d")["Close"].dropna()
    if len(closes) < 2:
        raise ValueError(f"not enough price data ({len(closes)} closes)")
    last_close, prev_close = float(closes.iloc[-1]), float(closes.iloc[-2])
    return {
        "last_close": round(last_close, 2),
        "prev_close": round(prev_close, 2),
        "change_pct": round((last_close - prev_close) / prev_close * 100, 2),
    }
