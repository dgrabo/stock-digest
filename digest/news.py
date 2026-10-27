"""Company news from Finnhub."""

from datetime import datetime, timedelta

import requests

from . import config

FINNHUB_URL = "https://finnhub.io/api/v1/company-news"


def news_window(now=None):
    """Return (start, end) datetimes in Zagreb time covering the previous weekday(s).

    Monday -> Fri 00:00 to Mon 00:00 (includes the weekend); other days -> yesterday.
    """
    now = now or datetime.now(config.TZ)
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
        "token": config.FINNHUB_KEY,
    }
    resp = requests.get(FINNHUB_URL, params=params, timeout=config.REQUEST_TIMEOUT)
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
    return articles[:config.MAX_HEADLINES]
