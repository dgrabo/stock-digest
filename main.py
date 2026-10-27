"""Daily stock news email digest.

Fetches yesterday's company news (Finnhub) and daily % price change (yfinance)
for a list of tickers, builds a simple HTML email, and sends it via Gmail SMTP.
Runs on weekdays via GitHub Actions.
"""

import logging
import os
import sys
import warnings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import yfinance as yf
from dotenv import load_dotenv

# --- Config ---
TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]
MAX_HEADLINES = 5
TZ = ZoneInfo("Europe/Zagreb")
FINNHUB_URL = "https://finnhub.io/api/v1/company-news"
REQUEST_TIMEOUT = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# yfinance triggers pandas deprecation warnings internally; not our code, so mute them.
warnings.filterwarnings("ignore", message="The inplace keyword", module="yfinance")

load_dotenv()
FINNHUB_KEY = os.getenv("FINNHUB_KEY")
if not FINNHUB_KEY:
    sys.exit("Error: FINNHUB_KEY is not set. Add it to .env (or the environment).")


def news_window(now=None):
    """Return (start, end) datetimes in Zagreb time covering the previous weekday(s).

    Monday -> Fri 00:00 to Mon 00:00 (includes the weekend); other days -> yesterday.
    """
    now = now or datetime.now(TZ)
    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    days_back = 3 if end.weekday() == 0 else 1
    start = end - timedelta(days=days_back)
    return start, end


def fetch_news(ticker):
    start, end = news_window()
    params = {
        "symbol": ticker,
        # Finnhub filters by date only, so query a slightly wider range
        # and filter precisely on each article's timestamp below.
        "from": (start - timedelta(days=1)).date().isoformat(),
        "to": end.date().isoformat(),
        "token": FINNHUB_KEY,
    }
    resp = requests.get(FINNHUB_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    start_ts, end_ts = start.timestamp(), end.timestamp()
    seen = set()
    articles = []
    for item in resp.json():
        ts = item.get("datetime", 0)
        headline = (item.get("headline") or "").strip()
        if not (start_ts <= ts < end_ts) or not headline:
            continue
        key = headline.lower()
        if key in seen:
            continue
        seen.add(key)
        articles.append({
            "headline": headline,
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "datetime": ts,
            "summary": item.get("summary", ""),
        })

    articles.sort(key=lambda a: a["datetime"], reverse=True)
    return articles[:MAX_HEADLINES]


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


def build_report(tickers):
    report = {}
    for ticker in tickers:
        log.info("Fetching %s", ticker)
        result = {"price": None, "news": [], "error": None}
        errors = []
        # Separate try blocks so a price failure doesn't also lose the news.
        try:
            result["price"] = fetch_price(ticker)
        except Exception as e:
            log.warning("%s price failed: %s", ticker, e)
            errors.append(f"price: {e}")
        try:
            result["news"] = fetch_news(ticker)
        except Exception as e:
            log.warning("%s news failed: %s", ticker, e)
            errors.append(f"news: {e}")
        result["error"] = "; ".join(errors) or None
        report[ticker] = result
    return report


def print_report(report):
    start, end = news_window()
    print(f"\nNews window: {start:%a %d.%m. %H:%M} - {end:%a %d.%m. %H:%M} (Europe/Zagreb)")
    for ticker, data in report.items():
        print(f"\n=== {ticker} ===")
        price = data["price"]
        if price:
            print(f"{price['last_close']:.2f} ({price['change_pct']:+.2f}%), prev close {price['prev_close']:.2f}")
        if data["error"]:
            print(f"ERROR: {data['error']}")
        if not data["news"] and not data["error"]:
            print("No news in window.")
        for a in data["news"]:
            when = datetime.fromtimestamp(a["datetime"], TZ)
            print(f"- [{when:%d.%m. %H:%M}] {a['headline']} ({a['source']})")


def main():
    # Windows consoles default to a legacy codepage; curly quotes etc. would print as garbage.
    sys.stdout.reconfigure(encoding="utf-8")
    report = build_report(TICKERS)
    print_report(report)


if __name__ == "__main__":
    main()
